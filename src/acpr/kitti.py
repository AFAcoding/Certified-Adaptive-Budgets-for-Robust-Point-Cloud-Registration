"""KITTI odometry registration benchmark (FCGF / Predator / GeoTransformer protocol).

Pairs, frames and ICP-refined ground-truth transforms come from GeoTransformer's metadata
(train: sequences 0-5, val: 6-7, test: 8-10; 1,358 / 180 / 555 pairs). Scans are the official
velodyne scans, voxel-downsampled at 0.3 m (data/KITTI/downsampled/SS/FFFFFF.npy).
Success criterion (SC^2-PCR / MAC / TurboReg convention): RE <= 5 deg and TE <= 0.6 m.
"""

from __future__ import annotations

import json
import pickle
import time
from pathlib import Path

import numpy as np

from acpr import DATA_ROOT
from acpr import light
from acpr.data import Pair

KITTI_ROOT = DATA_ROOT / "KITTI"
VOXEL = 0.30
RE_MAX, TE_MAX = 5.0, 0.60
# distance thresholds of the estimators scale with the inlier threshold (0.6 m vs 0.1 m on 3DMatch)
SCALE = 6.0
SPLITS = {"train": "kitti_train", "val": "kitti_val", "test": "kitti_test"}


class _NumpyOnlyUnpickler(pickle.Unpickler):
    """The metadata are third-party pickles: allow numpy arrays/scalars only, nothing executable."""

    ALLOWED = {("numpy.core.multiarray", "_reconstruct"), ("numpy._core.multiarray", "_reconstruct"),
               ("numpy", "ndarray"), ("numpy", "dtype"), ("numpy.core.multiarray", "scalar"),
               ("numpy._core.multiarray", "scalar")}

    def find_class(self, module, name):
        if (module, name) not in self.ALLOWED:
            raise pickle.UnpicklingError(f"blocked {module}.{name}")
        return super().find_class(module, name)


def convert_metadata(root: Path = KITTI_ROOT):
    """metadata_raw/{split}.pkl (GeoTransformer) -> metadata/{split}.json."""
    (root / "metadata").mkdir(parents=True, exist_ok=True)
    for split in SPLITS:
        with open(root / "metadata_raw" / f"{split}.pkl", "rb") as f:
            items = _NumpyOnlyUnpickler(f).load()
        out = [{"seq": int(x["seq_id"]), "frame0": int(x["frame0"]), "frame1": int(x["frame1"]),
                "transform": np.asarray(x["transform"], dtype=np.float64).tolist()} for x in items]
        with open(root / "metadata" / f"{split}.json", "w") as f:
            json.dump(out, f)


def scan_path(seq: int, frame: int) -> str:
    return f"KITTI/downsampled/{seq:02d}/{frame:06d}.npy"


def load_kitti_pairs(split: str, root: Path = KITTI_ROOT) -> list[Pair]:
    with open(root / "metadata" / f"{split}.json") as f:
        items = json.load(f)
    return [Pair(subset=SPLITS[split], index=i, scene=f"{x['seq']:02d}", frag0=x["frame0"], frag1=x["frame1"],
                 pcd0=scan_path(x["seq"], x["frame0"]), pcd1=scan_path(x["seq"], x["frame1"]), overlap=float("nan"),
                 transform=np.asarray(x["transform"], dtype=np.float64)) for i, x in enumerate(items)]


def train_sample(n: int = 500, seed: int = 0) -> list[int]:
    """Indices of the training pairs whose scans were fetched (fixed random sample)."""
    total = len(load_kitti_pairs("train"))
    return sorted(np.random.default_rng(seed).choice(total, min(n, total), replace=False).tolist())


def calib_indices() -> list[int]:
    """Training pairs NOT used for fitting: added to validation for certification (180 pairs alone are too
    few to certify a 1 % risk at delta = 0.1: even zero observed losses give p = 0.99^180 = 0.16)."""
    fit = set(train_fit())
    return [i for i in range(len(load_kitti_pairs("train"))) if i not in fit]


def train_fit(n: int = 300, seed: int = 1) -> list[int]:
    """Training pairs used to fit the controllers: a random subset of the fetched sample (compute budget)."""
    sample = train_sample()
    return sorted(np.random.default_rng(seed).choice(sample, min(n, len(sample)), replace=False).tolist())


def get_fpfh_kitti(pcd: str):
    """FPFH on the 0.3 m voxel grid (normals 0.6 m, features 1.5 m: the 3DMatch multipliers). Cached."""
    path = DATA_ROOT / "cache" / "kitti_fpfh_300mm" / Path(pcd).relative_to("KITTI/downsampled").with_suffix(".npz")
    if path.exists():
        z = np.load(path, allow_pickle=False)
        return z["points"], z["feats"], float(z["seconds"])
    pts = np.load(DATA_ROOT / pcd, allow_pickle=False)
    t0 = time.perf_counter()
    p, f = light.preprocess(pts, light.LightConfig(voxel_size=VOXEL))
    dt = time.perf_counter() - t0
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, points=p, feats=f, seconds=np.float64(dt))
    return p, f, dt


def success(T_gt: np.ndarray, T: np.ndarray) -> tuple[bool, float, float]:
    from acpr.metrics import rre_rte
    rre, rte = rre_rte(T_gt, T)
    return bool(rre <= RE_MAX and rte <= TE_MAX), rre, rte
