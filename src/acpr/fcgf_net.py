"""FCGF features (Choy, Park and Koltun, ICCV 2019) in plain PyTorch on the CPU.

The ResUNetBN2C sparse U-Net of the official code (model/resunet.py), with MinkowskiEngine's sparse convolutions
re-implemented by coordinate hashing, run with the official weights (loaded by acpr.safe_torch_load, no code from the
checkpoint is executed). Conventions follow MinkowskiEngine:
  * a sparse tensor at tensor stride s has integer coordinates that are multiples of s;
  * a stride-1 convolution keeps the coordinates; output o sums W[k] applied to the input at o + offset_k * s;
  * a stride-2 convolution outputs floor(c / 2s) * 2s and sums the inputs at o + offset_k * s;
  * a stride-2 transposed convolution writes into the existing coordinates of stride s (those of the encoder):
    input c (stride 2s) contributes W[k] to the output at c + offset_k * s.
Kernel offsets are enumerated with the first axis varying fastest (scripts/verify_fcgf.py checks every convention
against the features released with SC2-PCR).
"""

from __future__ import annotations

import numpy as np
import torch

from acpr.safe_torch_load import load as safe_load

_M, _OFF = 1 << 20, 1 << 19


def _key(c: np.ndarray) -> np.ndarray:
    c = c.astype(np.int64) + _OFF
    return c[:, 0] + c[:, 1] * _M + c[:, 2] * _M * _M


def kernel_offsets(k: int, first_axis_fastest: bool = True) -> np.ndarray:
    r = np.arange(k) - (k - 1) // 2
    g = np.stack(np.meshgrid(r, r, r, indexing="ij"), -1).reshape(-1, 3)  # last axis fastest
    return g[:, ::-1].copy() if first_axis_fastest else g


class Level:
    """Coordinates at one tensor stride, with a hash index."""

    def __init__(self, coords: np.ndarray, stride: int):
        self.coords, self.stride = coords, stride
        keys = _key(coords)
        self.order = np.argsort(keys)
        self.keys = keys[self.order]

    def find(self, q: np.ndarray) -> np.ndarray:
        """Row of each query coordinate, or -1."""
        kq = _key(q)
        pos = np.clip(np.searchsorted(self.keys, kq), 0, len(self.keys) - 1)
        hit = self.keys[pos] == kq
        return np.where(hit, self.order[pos], -1)


def kernel_map(src: Level, dst: Level, offsets: np.ndarray, transpose=False):
    """Per kernel offset, the (input rows, output rows) it connects."""
    step = min(src.stride, dst.stride)
    maps = []
    for off in offsets:
        if transpose:  # input c contributes to c + off * step
            rows_out = dst.find(src.coords + off * step)
            m = rows_out >= 0
            maps.append((torch.from_numpy(np.flatnonzero(m)), torch.from_numpy(rows_out[m])))
        else:  # output o reads o + off * step
            rows_in = src.find(dst.coords + off * step)
            m = rows_in >= 0
            maps.append((torch.from_numpy(rows_in[m]), torch.from_numpy(np.flatnonzero(m))))
    return maps


def _conv(x: torch.Tensor, n_out: int, w: np.ndarray, maps):
    """Sparse convolution with a precomputed kernel map. w: (K, C_in, C_out)."""
    out = torch.zeros(n_out, w.shape[2], dtype=torch.float32)
    w = torch.from_numpy(np.ascontiguousarray(w)).float()
    for k, (rin, rout) in enumerate(maps):
        if len(rin):
            out.index_add_(0, rout, x[rin] @ w[k])
    return out


class FCGF:
    CHANNELS = [None, 32, 64, 128, 256]
    TR_CHANNELS = [None, 64, 64, 64, 128]  # ResUNetBN2C

    def __init__(self, path: str, normalize: bool | None = None, first_axis_fastest: bool = True):
        ck = safe_load(path)
        self.sd = {k: np.asarray(v) for k, v in ck["state_dict"].items()}
        cfg = dict(ck.get("config", {}))
        self.normalize = cfg.get("normalize_feature", True) if normalize is None else normalize
        self.k1 = round(self.sd["conv1.kernel"].shape[0] ** (1 / 3))
        self.fast = first_axis_fastest
        self.voxel = cfg.get("voxel_size")

    def _bn(self, name, x):
        g = lambda s: torch.from_numpy(self.sd[f"{name}.bn.{s}"]).float()  # noqa: E731
        return (x - g("running_mean")) / torch.sqrt(g("running_var") + 1e-5) * g("weight") + g("bias")

    def _block(self, name, x, maps):
        out = _conv(x, len(x), self.sd[f"{name}.conv1.kernel"], maps)
        out = torch.relu(self._bn(f"{name}.norm1", out))
        out = _conv(out, len(x), self.sd[f"{name}.conv2.kernel"], maps)
        out = self._bn(f"{name}.norm2", out)
        return torch.relu(out + x)

    @torch.no_grad()
    def features(self, coords: np.ndarray) -> np.ndarray:
        """coords: unique integer voxel coordinates (N, 3) at the model's voxel size; returns (N, 32) features."""
        off3, off1 = kernel_offsets(3, self.fast), kernel_offsets(self.k1, self.fast)
        L1 = Level(coords, 1)
        levels = [L1]
        for s in (2, 4, 8):
            c = np.unique(np.floor_divide(levels[-1].coords, s) * s, axis=0)
            levels.append(Level(c, s))
        L1, L2, L4, L8 = levels
        same = {L: kernel_map(L, L, off3) for L in levels}  # every 3x3x3 convolution at one stride
        n = {L: len(L.coords) for L in levels}
        sd = self.sd
        x = torch.ones(len(coords), 1)
        s1 = self._block("block1", self._bn("norm1", _conv(x, n[L1], sd["conv1.kernel"], kernel_map(L1, L1, off1))),
                         same[L1])
        s2 = self._block("block2", self._bn("norm2", _conv(torch.relu(s1), n[L2], sd["conv2.kernel"],
                                                          kernel_map(L1, L2, off3))), same[L2])
        s4 = self._block("block3", self._bn("norm3", _conv(torch.relu(s2), n[L4], sd["conv3.kernel"],
                                                          kernel_map(L2, L4, off3))), same[L4])
        s8 = self._block("block4", self._bn("norm4", _conv(torch.relu(s4), n[L8], sd["conv4.kernel"],
                                                          kernel_map(L4, L8, off3))), same[L8])
        t = _conv(torch.relu(s8), n[L4], sd["conv4_tr.kernel"], kernel_map(L8, L4, off3, transpose=True))
        t4 = torch.relu(self._block("block4_tr", self._bn("norm4_tr", t), same[L4]))
        t = _conv(torch.cat([t4, s4], 1), n[L2], sd["conv3_tr.kernel"], kernel_map(L4, L2, off3, transpose=True))
        t2 = torch.relu(self._block("block3_tr", self._bn("norm3_tr", t), same[L2]))
        t = _conv(torch.cat([t2, s2], 1), n[L1], sd["conv2_tr.kernel"], kernel_map(L2, L1, off3, transpose=True))
        t1 = torch.relu(self._block("block2_tr", self._bn("norm2_tr", t), same[L1]))
        out = torch.relu(torch.cat([t1, s1], 1) @ torch.from_numpy(self.sd["conv1_tr.kernel"]).float())
        out = out @ torch.from_numpy(self.sd["final.kernel"]).float() + torch.from_numpy(self.sd["final.bias"]).float()
        if self.normalize:
            out = out / torch.linalg.norm(out, dim=1, keepdim=True)
        return out.numpy()


def voxelize(points: np.ndarray, voxel: float):
    """FCGF's quantisation: integer voxel coordinates floor(p / voxel), one point per voxel (the first)."""
    c = np.floor(np.asarray(points, np.float64) / voxel).astype(np.int64)  # float64, as the official pipeline
    coords, idx = np.unique(c, axis=0, return_index=True)
    return coords, points[idx]
