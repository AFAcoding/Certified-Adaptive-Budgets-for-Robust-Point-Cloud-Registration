"""Registration error metrics and success criteria (Section 8.1 of the proposal)."""

from __future__ import annotations

import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation

RMSE_THRESHOLD = 0.2  # metres, 3DMatch official protocol
RRE_THRESHOLD = 15.0  # degrees, robust-estimator protocol
RTE_THRESHOLD = 0.3  # metres, robust-estimator protocol


def rre_rte(T_gt: np.ndarray, T_est: np.ndarray) -> tuple[float, float]:
    """Relative rotation error (degrees) and translation error (metres)."""
    R_gt, t_gt = T_gt[:3, :3], T_gt[:3, 3]
    R_est, t_est = T_est[:3, :3], T_est[:3, 3]
    cos = (np.trace(R_est.T @ R_gt) - 1.0) / 2.0
    rre = float(np.degrees(np.arccos(np.clip(cos, -1.0, 1.0))))
    rte = float(np.linalg.norm(t_gt - t_est))
    return rre, rte


def info_rmse2(T_gt: np.ndarray, info: np.ndarray, T_est: np.ndarray) -> float:
    """Squared RMSE over ground-truth correspondences, as in the official 3DMatch script.

    error = [t, q_xyz] of inv(T_gt) @ T_est; rmse^2 = e^T * info * e / info[0, 0].
    """
    rel = np.linalg.inv(T_gt) @ T_est
    q = Rotation.from_matrix(rel[:3, :3]).as_quat()  # (x, y, z, w)
    if q[3] < 0:  # nibabel's mat2quat returns w >= 0; keep the same sign convention
        q = -q
    e = np.concatenate([rel[:3, 3], q[:3]])
    return float(e @ info @ e / info[0, 0])


def info_matrix(ref_points: np.ndarray, src_points: np.ndarray, T_gt: np.ndarray, radius: float = 0.0375,
                max_corr: int = 5000, seed: int = 0) -> np.ndarray:
    """Information matrix from ground-truth correspondences (same construction as 3DMatch's gt.info).

    Used for validation pairs, which have no published gt.info.
    """
    src_t = src_points @ T_gt[:3, :3].T + T_gt[:3, 3]
    d, _ = cKDTree(ref_points).query(src_t, k=1, distance_upper_bound=radius)
    p = src_t[np.isfinite(d)]
    if p.shape[0] > max_corr:
        p = p[np.random.default_rng(seed).choice(p.shape[0], max_corr, replace=False)]
    if p.shape[0] == 0:
        return np.zeros((6, 6))
    g = np.zeros((p.shape[0], 3, 6))
    g[:, :3, :3] = np.eye(3)
    g[:, 0, 4] = p[:, 2]
    g[:, 0, 5] = -p[:, 1]
    g[:, 1, 3] = -p[:, 2]
    g[:, 1, 5] = p[:, 0]
    g[:, 2, 3] = p[:, 1]
    g[:, 2, 4] = -p[:, 0]
    return np.einsum("nij,nik->jk", g, g)


def evaluate_transform(T_gt: np.ndarray, T_est: np.ndarray, info: np.ndarray | None) -> dict:
    """All per-pair accuracy quantities used by the analysis."""
    rre, rte = rre_rte(T_gt, T_est)
    out = {
        "rre": rre,
        "rte": rte,
        "ok_rre_rte": bool(rre <= RRE_THRESHOLD and rte <= RTE_THRESHOLD),
    }
    if info is not None and info[0, 0] > 0:
        rmse2 = info_rmse2(T_gt, info, T_est)
        out["rmse"] = float(np.sqrt(max(rmse2, 0.0)))
        out["ok_rmse"] = bool(rmse2 < RMSE_THRESHOLD**2)
    else:
        out["rmse"] = float("nan")
        out["ok_rmse"] = False
    return out
