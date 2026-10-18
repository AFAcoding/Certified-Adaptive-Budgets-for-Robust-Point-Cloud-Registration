"""FPFH features (cached per fragment) and putative correspondences."""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np

from acpr import DATA_ROOT
from acpr import light
from acpr.data import Pair, load_fragment

CACHE_ROOT = DATA_ROOT / "cache"


def fpfh_cache_path(pcd: str, voxel: float) -> Path:
    return CACHE_ROOT / f"fpfh_{int(round(voxel * 1000))}mm" / Path(pcd).with_suffix(".npz")


def get_fpfh(pcd: str, voxel: float = 0.05):
    """Return (points (n,3), fpfh (n,33), seconds spent computing them)."""
    path = fpfh_cache_path(pcd, voxel)
    if path.exists():
        z = np.load(path, allow_pickle=False)
        return z["points"], z["feats"], float(z["seconds"])
    cfg = light.LightConfig(voxel_size=voxel)
    t0 = time.perf_counter()
    pts, feats = light.preprocess(load_fragment(pcd), cfg)
    dt = time.perf_counter() - t0
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, points=pts, feats=feats, seconds=np.float64(dt))
    return pts, feats, dt


def correspondences(pair: Pair, voxel: float = 0.05, n_max: int = 1000) -> dict:
    """Mutual-NN FPFH correspondences, keeping the n_max most distinctive (Lowe ratio)."""
    ref_pts, ref_f, t_ref = get_fpfh(pair.pcd0, voxel)
    src_pts, src_f, t_src = get_fpfh(pair.pcd1, voxel)
    t0 = time.perf_counter()
    si, ri, ratio = light.mutual_matches(src_f, ref_f)
    if si.shape[0] > n_max:
        keep = np.argsort(ratio)[:n_max]
        si, ri, ratio = si[keep], ri[keep], ratio[keep]
    t_match = time.perf_counter() - t0
    return {
        "P": src_pts[si].astype(np.float32),  # source side
        "Q": ref_pts[ri].astype(np.float32),  # reference side
        "ratio": ratio,
        "src_pts": src_pts,
        "ref_pts": ref_pts,
        "t_features": t_ref + t_src,
        "t_matching": t_match,
        "n_mutual": int(si.shape[0]),
    }


def inlier_mask(P: np.ndarray, Q: np.ndarray, T: np.ndarray, thr: float = 0.1) -> np.ndarray:
    return np.linalg.norm(P @ T[:3, :3].T + T[:3, 3] - Q, axis=1) < thr
