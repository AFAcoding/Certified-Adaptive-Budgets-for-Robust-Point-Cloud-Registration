"""Re-implementations of graph-based robust estimators (CPU, NumPy).

* SC^2-PCR (Chen et al., CVPR 2022), following the official code
  (github.com/ZhiChen902/SC2-PCR): soft/hard spatial compatibility, leading-eigenvector
  confidence, NMS seed selection, second-order compatibility restricted to seed rows,
  two-stage local spectral matching (k1, k2), inlier-count verification and weighted
  post-refinement.
* TurboReg (Yan et al., ICCV 2025), following the paper: stringent compatibility
  graph (tau), second-order weights, pivot-guided search of 3-cliques (top-K1 edges,
  top-K2 third nodes), Kabsch per clique, inlier-count selection, same post-refinement.

Both functions return the estimate and an operation count used as a hardware-
independent cost (pairwise compatibility checks + multiply-adds of the second-order
products + correspondence evaluations for hypothesis verification).
"""

from __future__ import annotations

import numpy as np
import os

from scipy.spatial.distance import cdist

from acpr.light import kabsch


def _leading_eigenvector(M: np.ndarray, iters: int = 10) -> np.ndarray:
    v = np.ones(M.shape[0], dtype=M.dtype)
    for _ in range(iters):
        nv = M @ v
        nv /= np.linalg.norm(nv) + 1e-12
        if np.allclose(nv, v, atol=1e-6):
            v = nv
            break
        v = nv
    return v


def _weighted_kabsch(P, Q, w):
    return kabsch(P, Q, np.maximum(w, 1e-12))


def post_refinement(T, P, Q, thr: float = 0.10, iters: int = 20):
    """SC^2-PCR's weighted refinement on the current inlier set."""
    prev = -1
    ops = 0
    for _ in range(iters):
        d = np.linalg.norm(P @ T[:3, :3].T + T[:3, 3] - Q, axis=1)
        ops += P.shape[0]
        inl = d < thr
        n = int(inl.sum())
        if n < 3 or abs(n - prev) < 1:
            break
        prev = n
        w = 1.0 / (1.0 + (d[inl] / thr) ** 2)
        T = _weighted_kabsch(P[inl], Q[inl], w)
    return T, ops


def _verify(Ts, P, Q, thr, chunk=512):
    """Inlier count of every hypothesis (BLAS matmul, float32, chunked)."""
    PT = np.ascontiguousarray(P.T, dtype=np.float32)  # (3, N)
    QT = np.ascontiguousarray(Q.T, dtype=np.float32)
    thr2 = np.float32(thr * thr)
    out = np.empty(Ts.shape[0], dtype=np.int64)
    for s in range(0, Ts.shape[0], chunk):
        T = Ts[s : s + chunk].astype(np.float32)
        D = np.matmul(T[:, :3, :3], PT) + T[:, :3, 3:4] - QT[None]  # (b, 3, N)
        out[s : s + chunk] = ((D * D).sum(axis=1) < thr2).sum(axis=1)
    return out


def sc2_pcr(P, Q, d_thre=0.10, inlier_thr=0.10, ratio=0.2, nms_radius=0.10, k1=30, k2=20, refine=True):
    P = np.asarray(P, np.float64)
    Q = np.asarray(Q, np.float64)
    N = P.shape[0]
    info = {"N": N}
    if N < 3:
        info.update(ops=0, inliers=0)
        return np.eye(4), info
    src_dist = cdist(P, P)
    cross = np.abs(src_dist - cdist(Q, Q))
    soft = np.clip(1.0 - cross**2 / d_thre**2, 0, None)
    hard = (cross < d_thre).astype(np.float32)
    tight = (cross < d_thre / 2).astype(np.float32)
    ops = N * N  # compatibility checks
    conf = _leading_eigenvector(soft)
    ops += 10 * N * N
    # NMS seeds: highest confidence within radius, then top ratio*N
    nbr = src_dist < nms_radius
    local_max = conf >= np.max(np.where(nbr, conf[None, :], -np.inf), axis=1)
    cand = np.flatnonzero(local_max)
    max_num = max(1, int(N * ratio))
    seeds = cand[np.argsort(-conf[cand])][:max_num]
    S = seeds.shape[0]
    # second-order compatibility for seed rows only
    sc2 = (tight[seeds] @ tight) * hard[seeds]  # (S, N)
    ops += S * N * N
    k1e = min(k1, N)
    k2e = min(k2, k1e)
    knn = np.argsort(-sc2, axis=1)[:, :k1e]  # (S, k1)
    # local stage: SC2 within each seed's k1 set, keep top-k2 by local degree, eigenvector weights
    hyps = np.empty((S, 4, 4))
    for s in range(S):
        idx = knn[s]
        lt = tight[np.ix_(idx, idx)]
        lsc2 = (lt @ lt) * hard[np.ix_(idx, idx)]
        fine = idx[np.argsort(-lsc2.sum(axis=1))[:k2e]]
        loc = np.clip(1.0 - np.abs(src_dist[np.ix_(fine, fine)] - cdist(Q[fine], Q[fine])) ** 2 / d_thre**2, 0, None)
        lt2 = tight[np.ix_(fine, fine)]
        w = _leading_eigenvector(((lt2 @ lt2) * loc).astype(np.float64))
        hyps[s] = _weighted_kabsch(P[fine], Q[fine], np.abs(w))
        ops += k1e**3 + k2e**3
    fit = _verify(hyps, P, Q, inlier_thr)
    ops += S * N
    T = hyps[int(fit.argmax())]
    if refine:
        T, o = post_refinement(T, P, Q, inlier_thr)
        ops += o
    inliers = int((np.linalg.norm(P @ T[:3, :3].T + T[:3, 3] - Q, axis=1) < inlier_thr).sum())
    info.update(ops=int(ops), inliers=inliers, seeds=int(S), best_fit=int(fit.max()))
    return T, info


def turboreg(P, Q, tau=0.012, k1=2000, k2=2, inlier_thr=0.10, refine=True):
    P = np.asarray(P, np.float64)
    Q = np.asarray(Q, np.float64)
    N = P.shape[0]
    info = {"N": N}
    if N < 3:
        info.update(ops=0, inliers=0)
        return np.eye(4), info
    cross = np.abs(cdist(P, P) - cdist(Q, Q))
    G = (cross < tau).astype(np.float32)
    np.fill_diagonal(G, 0)
    Gs = G * (G @ G)  # second-order weights (SC^2 graph)
    ops = N * N + N * N * N
    iu = np.triu_indices(N, 1)
    wts = Gs[iu]
    nz = np.flatnonzero(wts > 0)
    if nz.size == 0:
        info.update(ops=int(ops), inliers=0, cliques=0)
        return np.eye(4), info
    top = nz[np.argsort(-wts[nz], kind="stable")[: min(k1, nz.size)]]
    I, J = iu[0][top], iu[1][top]
    # third node: candidates adjacent to both ends; score = G_ij + G_iz + G_jz, keep top-k2
    cand = (Gs[I] > 0) & (Gs[J] > 0)  # (K1, N)
    score = np.where(cand, Gs[I] + Gs[J], -1.0)
    score[np.arange(I.size), I] = -1.0
    score[np.arange(I.size), J] = -1.0
    ops += I.size * N
    kk = min(k2, N)
    Z = np.argpartition(-score, kk - 1, axis=1)[:, :kk]
    valid = np.take_along_axis(score, Z, axis=1) > 0
    tri = np.stack([np.repeat(I, kk), np.repeat(J, kk), Z.reshape(-1)], axis=1)[valid.reshape(-1)]
    if tri.shape[0] == 0:
        info.update(ops=int(ops), inliers=0, cliques=0)
        return np.eye(4), info
    hyps = kabsch(P[tri], Q[tri])
    fit = _verify(hyps, P, Q, inlier_thr)
    ops += tri.shape[0] * N
    T = hyps[int(fit.argmax())]
    if refine:
        T, o = post_refinement(T, P, Q, inlier_thr)
        ops += o
    inliers = int((np.linalg.norm(P @ T[:3, :3].T + T[:3, 3] - Q, axis=1) < inlier_thr).sum())
    info.update(ops=int(ops), inliers=inliers, cliques=int(tri.shape[0]), best_fit=int(fit.max()))
    return T, info


def _compat(P, Q, rows, cols, thr):
    D = cdist(P[rows], P[cols])
    D -= cdist(Q[rows], Q[cols])
    np.abs(D, out=D)
    return (D < thr).astype(np.float32)


def compat_order(P, Q, m: int = 100, pool: int | None = 500, thr: float = 0.10, return_anchors: bool = False):
    """Compatibility-guided ordering for truncated budgets (input sorted by Lowe ratio).

    Two passes. (1) Anchors: the m correspondences with the highest first-order
    compatibility degree within the `pool` most distinctive ones. (2) Every correspondence
    is scored by its second-order compatibility with the anchors,
    s_i = sum_a C_ia (C C_AA)_ia, C_ia = [| ||p_i - p_a|| - ||q_i - q_a|| | < thr].
    Cost O(pool^2 + N m + N m^2) instead of the O(N^2) / O(N^3) of the full graph.
    pool=None: one pass with the first m correspondences as anchors (weaker: for hard
    pairs those anchors are almost all outliers and mutually consistent outliers rise).
    Ties keep the ratio order. Returns (permutation, op count[, anchors]).
    """
    n = P.shape[0]
    ops = 0
    if pool:
        c = slice(0, min(pool, n))
        W = _compat(P, Q, c, c, thr)
        a = np.argsort(-W.sum(axis=1), kind="stable")[:m]
        ops += W.size
    else:
        a = np.arange(min(m, n))
    C = _compat(P, Q, slice(None), a, thr)
    k = C.shape[1]
    score = (C * (C @ C[a])).sum(axis=1)
    ops += n * k + n * k * k
    out = (np.argsort(-score, kind="stable"), int(ops))
    return out + (a,) if return_anchors else out


def fastmac_sample(P, Q, m, rng, second_order=True, d_cmp=0.10, t=0.999):
    """FastMAC-style stochastic spectral sampling (Zhang et al., CVPR 2024), re-implemented.

    Builds the compatibility graph over ALL correspondences, W_ij = 1 - S_ij^2 / (2 d_cmp^2) if that
    exceeds t (else 0), S_ij = | ||p_i - p_j|| - ||q_i - q_j|| |; with second_order, W <- W * (W @ W)
    (the second-order graph, O(N^3)). The generalized degree s = W 1 is high-pass filtered with the
    graph Laplacian, f = (Diag(s) - W) s, and m correspondences are drawn without replacement with
    probability proportional to f^2. Returns sorted indices (ratio order kept among them).
    """
    if m >= P.shape[0]:
        return np.arange(P.shape[0])
    return fastmac_draw(fastmac_probs(P, Q, second_order, d_cmp, t), m, rng)


def fastmac_draw(probs, m, rng):
    """Draw m correspondences without replacement from FastMAC sampling probabilities (sorted indices)."""
    n = probs.shape[0]
    if m >= n:
        return np.arange(n)
    return np.sort(rng.choice(n, size=m, replace=False, p=probs))


def fastmac_probs(P, Q, second_order=True, d_cmp=0.10, t=0.999):
    """FastMAC sampling probabilities (the graph signal; computed once per pair, shared by all budgets)."""
    S = cdist(P, P)
    S -= cdist(Q, Q)
    np.square(S, out=S)
    W = 1.0 - S / (2.0 * d_cmp * d_cmp)
    W[W <= t] = 0.0
    np.fill_diagonal(W, 0.0)
    W = W.astype(np.float32)
    if second_order:
        W = W * (W @ W)
    s = W.sum(axis=1)
    f = s * s - W @ s
    w = f.astype(np.float64) ** 2
    w += 1e-12 * max(w.max(), 1e-12)  # every correspondence keeps a tiny probability
    return w / w.sum()


def nn_correspondences_bf(src_pts, src_feat, ref_pts, ref_feat, normalize=True, chunk=2048):
    """Same correspondences as nn_correspondences (exact nearest neighbour + Lowe ratio), by brute force.

    k-d trees degrade in 33 dimensions when many descriptors are near-identical (e.g. ground points in
    KITTI: 167 s per pair); a chunked BLAS distance computation takes a few seconds. Used for KITTI.
    """
    sf = np.asarray(src_feat, np.float32)
    rf = np.asarray(ref_feat, np.float32)
    if normalize:
        sf = sf / (np.linalg.norm(sf, axis=1, keepdims=True) + 1e-6)
        rf = rf / (np.linalg.norm(rf, axis=1, keepdims=True) + 1e-6)
    r2 = (rf * rf).sum(axis=1)
    n = sf.shape[0]
    j = np.empty(n, dtype=np.int64)
    d1 = np.empty(n, dtype=np.float64)
    d2 = np.empty(n, dtype=np.float64)
    for s in range(0, n, chunk):
        a = sf[s:s + chunk]
        D = r2[None, :] - 2.0 * (a @ rf.T)  # squared distance minus |a|^2 (constant per row)
        rows = np.arange(a.shape[0])
        i1 = D.argmin(axis=1)
        b1 = D[rows, i1].copy()
        D[rows, i1] = np.inf
        b2 = D.min(axis=1)
        a2 = (a * a).sum(axis=1)
        j[s:s + chunk] = i1
        d1[s:s + chunk] = np.sqrt(np.maximum(b1 + a2, 0.0))
        d2[s:s + chunk] = np.sqrt(np.maximum(b2 + a2, 0.0))
    ratio = d1 / np.maximum(d2, 1e-12)
    order = np.argsort(ratio, kind="stable")
    return src_pts[order], ref_pts[j[order]], ratio[order]


def nn_correspondences(src_pts, src_feat, ref_pts, ref_feat, normalize=True):
    """SC^2-PCR-style correspondences: nearest target feature for every source point.

    Returns correspondences sorted by quality (Lowe ratio, most distinctive first).
    """
    from scipy.spatial import cKDTree

    sf, rf = src_feat, ref_feat
    if normalize:
        sf = sf / (np.linalg.norm(sf, axis=1, keepdims=True) + 1e-6)
        rf = rf / (np.linalg.norm(rf, axis=1, keepdims=True) + 1e-6)
    # all cores by default; parallel log builders set ACPR_KD_WORKERS=1 to avoid oversubscription
    d, j = cKDTree(rf).query(sf, k=2, workers=int(os.environ.get("ACPR_KD_WORKERS", "-1")))
    ratio = d[:, 0] / np.maximum(d[:, 1], 1e-12)
    order = np.argsort(ratio, kind="stable")
    return src_pts[order], ref_pts[j[order, 0]], ratio[order]
