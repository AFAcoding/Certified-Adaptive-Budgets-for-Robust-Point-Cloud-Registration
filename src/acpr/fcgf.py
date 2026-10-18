"""Learned (FCGF) descriptors from the SC^2-PCR data release, for 3DMatch/3DLoMatch and KITTI test pairs.

3DMatch: data/FCGF/3DMatch/<scene>/cloud_bin_<i>_fcgf.npz with keys xyz (keypoints, fragment frame)
and feature (32-d). Pairs, ground truth and success criterion are those of the FPFH experiments.
KITTI: data/FCGF/KITTI/pair_<i>.npz with xyz0/xyz1, features0/features1 and gt_trans, which maps
xyz0 into the frame of xyz1; we use src = xyz0, ref = xyz1. 553 of the 555 pairs match a pair of the
GeoTransformer test list (used only for the sequence id); pair_0 and pair_1 are identical files,
kept as in the SC^2-PCR benchmark (555 pairs).
Only test sets are released, so controllers are trained and certified on FPFH data (transfer).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np

from acpr import DATA_ROOT
from acpr.data import Pair, load_pairs

FCGF_ROOT = DATA_ROOT / "FCGF"


def load_fcgf_3dmatch_pairs(subset: str) -> list[Pair]:
    """Same pairs and ground truth as the FPFH test sets, tagged fcgf_<subset>."""
    return [Pair(subset=f"fcgf_{subset}", index=p.index, scene=p.scene, frag0=p.frag0, frag1=p.frag1,
                 pcd0=p.pcd0, pcd1=p.pcd1, overlap=p.overlap, transform=p.transform) for p in load_pairs(subset)]


def features_3dmatch(pair: Pair):
    """(ref_xyz, ref_feat, src_xyz, src_feat) from the FCGF release."""
    def one(frag):
        z = np.load(FCGF_ROOT / "3DMatch" / pair.scene / f"cloud_bin_{frag}_fcgf.npz", allow_pickle=False)
        return z["xyz"].astype(np.float64), z["feature"].astype(np.float32)
    rp, rf = one(pair.frag0)
    sp, sf = one(pair.frag1)
    return rp, rf, sp, sf


@lru_cache(maxsize=1)
def _kitti_sequences() -> tuple:
    """Sequence id of every FCGF KITTI pair, from the closest GeoTransformer test pair (transform match)."""
    from acpr import kitti as K
    geo = K.load_kitti_pairs("test")
    G = np.array([p.transform for p in geo])
    seqs = []
    for i in range(len(list((FCGF_ROOT / "KITTI").glob("pair_*.npz")))):
        T = np.load(FCGF_ROOT / "KITTI" / f"pair_{i}.npz", allow_pickle=False)["gt_trans"].astype(np.float64)
        d = np.linalg.norm(G[:, :3, 3] - T[None, :3, 3], axis=1) + \
            np.linalg.norm((G[:, :3, :3] - T[None, :3, :3]).reshape(len(G), -1), axis=1)
        seqs.append(geo[int(d.argmin())].scene)
    return tuple(seqs)


def load_fcgf_kitti_pairs() -> list[Pair]:
    seqs = _kitti_sequences()
    pairs = []
    for i, seq in enumerate(seqs):
        T = np.load(FCGF_ROOT / "KITTI" / f"pair_{i}.npz", allow_pickle=False)["gt_trans"].astype(np.float64)
        pairs.append(Pair(subset="fcgf_kitti_test", index=i, scene=seq, frag0=i, frag1=i,
                          pcd0=f"FCGF/KITTI/pair_{i}.npz", pcd1=f"FCGF/KITTI/pair_{i}.npz",
                          overlap=float("nan"), transform=T))
    return pairs


def features_kitti(pair: Pair):
    z = np.load(DATA_ROOT / pair.pcd0, allow_pickle=False)
    return (z["xyz1"].astype(np.float64), z["features1"].astype(np.float32),
            z["xyz0"].astype(np.float64), z["features0"].astype(np.float32))
