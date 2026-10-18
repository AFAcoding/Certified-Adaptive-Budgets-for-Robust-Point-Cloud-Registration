"""Light registration path: FPFH features + mutual matching + SC^2-style robust estimation.

Everything runs on the CPU. Besides the pose, the estimator returns cheap
by-product signals that the controller uses to predict whether this pose is
correct (Section 5.4 of the proposal). None of them uses ground truth.

SC^2 estimator follows Chen et al., "SC^2-PCR", CVPR 2022 (second-order spatial
compatibility, seed selection with non-maximum suppression, local consensus
expansion, hypothesis verification by inlier counting).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np
import open3d as o3d
from scipy.spatial import cKDTree
from scipy.spatial.distance import cdist


@dataclass
class LightConfig:
    voxel_size: float = 0.05  # FPFH resolution (3DMatch convention)
    normal_radius_mult: float = 2.0
    feature_radius_mult: float = 5.0
    normal_max_nn: int = 30
    feature_max_nn: int = 100
    max_correspondences: int = 2000  # cap before building the N x N compatibility graph
    compat_threshold: float = 0.10  # metres, |d_src - d_ref| for spatial compatibility
    inlier_threshold: float = 0.10  # metres, residual for hypothesis verification
    num_seeds_ratio: float = 0.10
    max_seeds: int = 200
    k1: int = 30  # local consensus set size (stage 1)
    k2: int = 20  # refined consensus set size (stage 2)
    nms_radius: float = 0.10  # metres, seed non-maximum suppression radius (source space)
    overlap_radius: float = 0.075  # metres, alignment-overlap signal
    refine_iters: int = 3
    num_threads: int = 8


@dataclass
class LightResult:
    transform: np.ndarray
    signals: dict = field(default_factory=dict)
    times: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Features and correspondences
# ---------------------------------------------------------------------------


def preprocess(points: np.ndarray, cfg: LightConfig):
    """Voxel-downsample, estimate normals, compute FPFH. Returns (points (N,3), fpfh (N,33))."""
    pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(points.astype(np.float64)))
    pcd = pcd.voxel_down_sample(cfg.voxel_size)
    pcd.estimate_normals(
        o3d.geometry.KDTreeSearchParamHybrid(radius=cfg.voxel_size * cfg.normal_radius_mult, max_nn=cfg.normal_max_nn)
    )
    fpfh = o3d.pipelines.registration.compute_fpfh_feature(
        pcd,
        o3d.geometry.KDTreeSearchParamHybrid(radius=cfg.voxel_size * cfg.feature_radius_mult, max_nn=cfg.feature_max_nn),
    )
    return np.asarray(pcd.points, dtype=np.float32), np.asarray(fpfh.data, dtype=np.float32).T


def mutual_matches(src_feat: np.ndarray, ref_feat: np.ndarray, workers: int = -1):
    """Mutual nearest neighbours in feature space. Returns (src_idx, ref_idx, ratio)."""
    ref_tree = cKDTree(ref_feat)
    d_sr, i_sr = ref_tree.query(src_feat, k=2, workers=workers)
    src_tree = cKDTree(src_feat)
    _, i_rs = src_tree.query(ref_feat, k=1, workers=workers)
    src_idx = np.arange(src_feat.shape[0])
    nn = i_sr[:, 0]
    mutual = i_rs[nn] == src_idx
    ratio = d_sr[:, 0] / np.maximum(d_sr[:, 1], 1e-12)  # Lowe ratio (lower = more distinctive)
    return src_idx[mutual], nn[mutual], ratio[mutual]


# ---------------------------------------------------------------------------
# Rigid estimation helpers
# ---------------------------------------------------------------------------


def kabsch(src: np.ndarray, ref: np.ndarray, w: np.ndarray | None = None) -> np.ndarray:
    """Weighted least-squares rigid transform mapping src -> ref. Batched over leading dims."""
    if w is None:
        w = np.ones(src.shape[:-1], dtype=src.dtype)
    w = w / np.maximum(w.sum(axis=-1, keepdims=True), 1e-12)
    cs = (w[..., None] * src).sum(axis=-2, keepdims=True)
    cr = (w[..., None] * ref).sum(axis=-2, keepdims=True)
    H = np.einsum("...ni,...nj->...ij", w[..., None] * (src - cs), ref - cr)
    U, _, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(np.einsum("...ji,...kj->...ik", Vt, U)))
    D = np.zeros(H.shape)
    D[..., 0, 0] = 1.0
    D[..., 1, 1] = 1.0
    D[..., 2, 2] = d
    R = np.einsum("...ji,...jk,...lk->...il", Vt, D, U)
    t = cr[..., 0, :] - np.einsum("...ij,...j->...i", R, cs[..., 0, :])
    T = np.zeros(H.shape[:-2] + (4, 4))
    T[..., :3, :3] = R
    T[..., :3, 3] = t
    T[..., 3, 3] = 1.0
    return T


def transform_points(T: np.ndarray, p: np.ndarray) -> np.ndarray:
    return p @ T[:3, :3].T + T[:3, 3]


def pose_distance(Ta: np.ndarray, Tb: np.ndarray) -> tuple[float, float]:
    """Rotation angle (deg) and translation distance between two poses."""
    R = Ta[:3, :3].T @ Tb[:3, :3]
    ang = np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1)))
    return float(ang), float(np.linalg.norm(Ta[:3, 3] - Tb[:3, 3]))


# ---------------------------------------------------------------------------
# SC^2 robust estimator
# ---------------------------------------------------------------------------


def sc2_estimate(src_c: np.ndarray, ref_c: np.ndarray, cfg: LightConfig) -> tuple[np.ndarray, dict]:
    """Estimate src->ref from putative correspondences with second-order spatial compatibility."""
    n = src_c.shape[0]
    sig: dict = {"n_corr": int(n)}
    if n < 3:
        sig.update(best_inliers=0, second_inliers=0, inlier_ratio=0.0, sc2_seed_max=0.0, n_hyp_near_best=0,
                   top_pose_spread_deg=180.0)
        return np.eye(4), sig

    src64 = src_c.astype(np.float64)
    ref64 = ref_c.astype(np.float64)
    ds = cdist(src64, src64)
    dr = cdist(ref64, ref64)
    C = (np.abs(ds - dr) < cfg.compat_threshold).astype(np.float32)
    np.fill_diagonal(C, 0.0)
    SC2 = C * (C @ C)  # second-order compatibility
    degree = SC2.sum(axis=1)

    # seed selection: top-scoring correspondences with spatial non-maximum suppression
    num_seeds = int(min(cfg.max_seeds, max(3, round(n * cfg.num_seeds_ratio))))
    order = np.argsort(-degree)
    src_tree = cKDTree(src_c)
    suppressed = np.zeros(n, dtype=bool)
    seeds = []
    for i in order:
        if suppressed[i]:
            continue
        seeds.append(i)
        if len(seeds) >= num_seeds:
            break
        suppressed[src_tree.query_ball_point(src_c[i], cfg.nms_radius)] = True
    seeds = np.asarray(seeds)

    # local consensus: k1 most SC2-compatible correspondences around each seed (incl. the seed)
    k1 = min(cfg.k1, n - 1)
    nbr = np.argsort(-SC2[seeds], axis=1)[:, :k1]
    cons = np.concatenate([seeds[:, None], nbr], axis=1)  # (S, k1+1)
    # weights: SC2 compatibility with the seed (seed itself gets max weight)
    w = SC2[seeds[:, None], cons]
    w[:, 0] = w.max(axis=1) + 1e-6
    hyp = kabsch(src64[cons], ref64[cons], w + 1e-9)  # (S, 4, 4)

    # stage 2: re-select k2 correspondences with the smallest residuals under each hypothesis
    res_all = np.linalg.norm(
        np.einsum("sij,nj->sni", hyp[:, :3, :3], src64) + hyp[:, None, :3, 3] - ref64[None], axis=-1
    )  # (S, N)
    k2 = min(cfg.k2, n)
    sel = np.argsort(res_all, axis=1)[:, :k2]
    hyp = kabsch(src64[sel], ref64[sel])

    # verification: inlier count under each hypothesis (all correspondences)
    res_all = np.linalg.norm(
        np.einsum("sij,nj->sni", hyp[:, :3, :3], src64) + hyp[:, None, :3, 3] - ref64[None], axis=-1
    )
    inl = res_all < cfg.inlier_threshold
    counts = inl.sum(axis=1)
    best = int(np.argmax(counts))
    T = hyp[best]

    # refinement on the inlier set
    for _ in range(cfg.refine_iters):
        r = np.linalg.norm(transform_points(T, src64) - ref64, axis=1)
        m = r < cfg.inlier_threshold
        if m.sum() < 3:
            break
        T = kabsch(src64[m], ref64[m])
    r = np.linalg.norm(transform_points(T, src64) - ref64, axis=1)
    final_inl = r < cfg.inlier_threshold

    # ambiguity signals: best hypothesis with a clearly different pose
    rot_best = hyp[best, :3, :3]
    rel = np.einsum("ji,sjk->sik", rot_best, hyp[:, :3, :3])
    ang = np.degrees(np.arccos(np.clip((np.trace(rel, axis1=1, axis2=2) - 1) / 2, -1, 1)))
    trans = np.linalg.norm(hyp[:, :3, 3] - hyp[best, :3, 3], axis=1)
    different = (ang > 10.0) | (trans > 0.3)
    second = int(counts[different].max()) if different.any() else 0
    near_best = counts >= 0.9 * counts[best]
    top = np.argsort(-counts)[: min(10, len(counts))]
    spread = float(np.max(ang[top])) if len(top) else 0.0

    sig.update(
        best_inliers=int(final_inl.sum()),
        hyp_best_inliers=int(counts[best]),
        second_inliers=second,
        inlier_ratio=float(final_inl.mean()),
        inlier_margin=float((counts[best] - second) / max(counts[best], 1)),
        n_hyp_near_best=int(near_best.sum()),
        n_hyp_near_best_diff=int((near_best & different).sum()),
        top_pose_spread_deg=spread,
        sc2_seed_max=float(degree[seeds].max()),
        sc2_seed_mean=float(degree[seeds].mean()),
        compat_density=float(C.mean()),
        inlier_residual_mean=float(r[final_inl].mean()) if final_inl.any() else float(cfg.inlier_threshold),
        num_seeds=int(len(seeds)),
    )
    return T, sig


# ---------------------------------------------------------------------------
# Full light path
# ---------------------------------------------------------------------------


def alignment_overlap(src_pts: np.ndarray, ref_tree: cKDTree, T: np.ndarray, radius: float) -> float:
    d, _ = ref_tree.query(transform_points(T, src_pts), k=1, distance_upper_bound=radius, workers=-1)
    return float(np.isfinite(d).mean())


def register(ref: np.ndarray, src: np.ndarray, cfg: LightConfig | None = None) -> LightResult:
    """FPFH + SC^2 registration of src -> ref with per-stage timings and signals."""
    cfg = cfg or LightConfig()
    times: dict[str, float] = {}
    t0 = time.perf_counter()
    ref_pts, ref_f = preprocess(ref, cfg)
    src_pts, src_f = preprocess(src, cfg)
    times["features"] = time.perf_counter() - t0

    t1 = time.perf_counter()
    si, ri, ratio = mutual_matches(src_f, ref_f)
    if si.shape[0] > cfg.max_correspondences:
        keep = np.argsort(ratio)[: cfg.max_correspondences]
        si, ri, ratio = si[keep], ri[keep], ratio[keep]
    times["matching"] = time.perf_counter() - t1

    t2 = time.perf_counter()
    T, sig = sc2_estimate(src_pts[si], ref_pts[ri], cfg)
    times["estimation"] = time.perf_counter() - t2

    t3 = time.perf_counter()
    ref_tree = cKDTree(ref_pts)
    sig["align_overlap"] = alignment_overlap(src_pts, ref_tree, T, cfg.overlap_radius)
    sig["n_src"] = int(src_pts.shape[0])
    sig["n_ref"] = int(ref_pts.shape[0])
    sig["ratio_median"] = float(np.median(ratio)) if ratio.size else 1.0
    sig["mutual_frac"] = float(si.shape[0] / max(min(src_pts.shape[0], ref_pts.shape[0]), 1))
    ext_s = np.ptp(src_pts, axis=0)
    ext_r = np.ptp(ref_pts, axis=0)
    sig["extent_min"] = float(min(ext_s.min(), ext_r.min()))
    times["signals"] = time.perf_counter() - t3
    times["total"] = time.perf_counter() - t0
    return LightResult(transform=T, signals=sig, times=times)
