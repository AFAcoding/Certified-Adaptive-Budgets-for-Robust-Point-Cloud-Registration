"""MAC, 3D registration with maximal cliques (Zhang et al., CVPR 2023), re-implemented on CPU (NumPy + igraph).

Follows the authors' implementations (repository zhangxy0517/3D-Registration-with-Maximal-Cliques):
- compatibility graph: FCG = max(0, 1 - d^2 / tau^2) with d = | ||p_i - p_j|| - ||q_i - q_j|| | and tau the inlier
  threshold, pruned below t_cmp. Indoors as in the Python implementation (tau = 0.10 m, t_cmp = 0.99: an edge needs
  d < 0.1 tau); on KITTI tau = 0.6 m, with t_cmp = 0.999 for FCGF as in the C++ implementation's KITTI branch and
  t_cmp = 0.99 for FPFH as indoors (the C++ value 0.9 gave the same success on 47 KITTI fitting pairs but up to
  25 million maximal cliques per run). Second-order graph SCG = (FCG FCG) (.) FCG.
- graph reduction (C++ implementation, every dataset): the weighted clustering coefficient of every node, c_i = sum over
  neighbour pairs a < b adjacent to each other of (G_ia G_ib G_ab)^(1/3), divided by deg_i (deg_i - 1) / 2 (G = SCG);
  the threshold min(OTSU, mean coefficient, total coefficient), with OTSU the 100-bin Otsu threshold of the
  coefficients and total = sum of numerators / sum of denominators. If it exceeds 3 (a dense, clustered graph) and there
  are more than 50 correspondences, only the edges among nodes whose coefficient exceeds f max(OTSU, total) are kept,
  f = 10 lowered in steps of 0.05 until at least the 50 most clustered nodes qualify.
- maximal cliques of at least min_clique nodes (3; 4 on KITTI in the C++ implementation) on the (reduced) graph
  (igraph); node-guided clique selection (each node keeps the maximal clique of largest weight, the sum of its SCG edge
  weights; ties to the clique found first; duplicates removed); one instance-equal SVD hypothesis per selected clique;
  the hypothesis with the largest MAE score sum_i max(0, (tau - e_i) / tau) wins and is refined
  (acpr.estimators.post_refinement, 20 iterations). The authors' Python demo keeps the refined pose only if it is closer
  to the ground truth, and their C++ code judges success before refining; both use the ground truth and are not
  reproduced: the refinement is always applied and success is judged on the refined pose, as for the other estimators.
"""

from __future__ import annotations

import os
import tempfile

import numpy as np
from scipy.spatial.distance import cdist

from acpr.light import kabsch

CHUNK_LINES = 200_000  # cliques read at a time, at most
CHUNK_ENTRIES = 2_000_000  # and at most this many clique members (bounded memory however large the cliques)
GATHER = 4_000_000  # SCG entries gathered at a time when weighting cliques
SPARSE = 0.05  # clustering coefficients by sparse products below this edge density, dense BLAS above

# settings per dataset and descriptor (see the module docstring)
SETTINGS = {"indoor": {"inlier_thr": 0.10, "t_cmp": 0.99, "min_clique": 3},
            # KITTI with FPFH: the Python implementation's cut-off (as indoors), not the C++ value 0.9, which gave the same
            # success on 47 KITTI fitting pairs but up to 25 million maximal cliques per run (PROTOCOL.md, addendum B,
            # amendment 1)
            "kitti_fpfh": {"inlier_thr": 0.6, "t_cmp": 0.99, "min_clique": 4},
            "kitti_fcgf": {"inlier_thr": 0.6, "t_cmp": 0.999, "min_clique": 4}}

# igraph's maximal_cliques(file=...) leaves one C-runtime stream open per call (measured: the 509th call of a process
# fails with "fdopen() failed unexpectedly" under the default limit of 512 streams). On Windows the limit is raised to
# the C runtime's maximum, 8,192 streams; long-running callers should also recycle their worker processes.
if os.name == "nt":
    try:
        import ctypes
        ctypes.cdll.ucrtbase._setmaxstdio(8192)
    except (OSError, AttributeError):
        pass


def _clique_chunks(path):
    """Yield (sizes, flat node ids) for consecutive chunks of the clique file (one clique per line, in igraph order)."""
    with open(path) as f:
        while True:
            lines, sizes, n = [], [], 0
            for ln in f:
                lines.append(ln)
                sizes.append(ln.count(" ") + 1)
                n += sizes[-1]
                if len(lines) >= CHUNK_LINES or n >= CHUNK_ENTRIES:
                    break
            if not lines:
                return
            flat = np.array("".join(lines).split(), dtype=np.int64)
            yield np.array(sizes, dtype=np.int64), flat


def _clique_weights(SCG, sizes, flat):
    """Sum of the SCG weights of every clique's edges (the diagonal of SCG is zero), in float64."""
    w = np.empty(len(sizes))
    offsets = np.concatenate([[0], np.cumsum(sizes)[:-1]])
    for k in np.unique(sizes):
        rows = np.nonzero(sizes == k)[0]
        step = max(1, GATHER // int(k * k))
        for a in range(0, len(rows), step):
            r = rows[a:a + step]
            arr = flat[offsets[r][:, None] + np.arange(k)]
            w[r] = SCG[arr[:, :, None], arr[:, None, :]].astype(np.float64).sum(axis=(1, 2)) / 2.0
    return w


def _otsu(values):
    """The C++ implementation's OTSU_thresh: 100-bin histogram of values / step (step = range / 100), the bin edge
    i * range / 100 that maximises the between-class variance; default range / 2."""
    vmax, vmin = float(values.max()), float(values.min())
    thresh = (vmax - vmin) / 2
    step = (vmax - vmin) / 100
    if step <= 0:
        return thresh
    ids = np.minimum((values / step).astype(np.int64), 99)
    hist = np.bincount(ids, minlength=100)
    sums = np.bincount(ids, weights=values, minlength=100)
    n, total = len(values), float(values.sum())
    fmax, n1, fore = -1000.0, 0, 0.0
    for i in range(100):
        n1 += int(hist[i])
        if n1 == 0:
            continue
        n2 = n - n1
        if n2 == 0:
            break
        fore += float(sums[i])
        sb = float(n1) * float(n2) * (fore / n1 - (total - fore) / n2) ** 2
        if sb > fmax:
            fmax, thresh = sb, i * (vmax - vmin) / 100.0
    return thresh


def _reduce(SCG, A):
    """The C++ implementation's graph reduction. Returns (adjacency to search, kept nodes or -1, ops)."""
    N = A.shape[0]
    deg = A.sum(1).astype(np.int64)
    H = np.cbrt(SCG)  # (G_ia G_ib G_ab)^(1/3) = H_ia H_ib H_ab; numerators are diag(H^3) / 2 (zero diagonal)
    if deg.sum() <= SPARSE * N * N:
        from scipy import sparse
        Hs = sparse.csr_matrix(H, dtype=np.float64)
        num = 0.5 * np.asarray(Hs.multiply(Hs @ Hs).sum(axis=1)).ravel()
    else:
        num = 0.5 * np.einsum("ij,ij->i", H, H @ H, dtype=np.float64)
    del H
    ops = int((deg * deg).sum() // 2)  # the C++ loop over each node's neighbour pairs
    has = deg > 1
    den = deg * (deg - 1) / 2.0
    factor = np.zeros(N)
    factor[has] = num[has] / den[has]
    average = float(factor.mean())
    total = float(num[has].sum() / den[has].sum()) if has.any() else 0.0
    otsu = _otsu(factor) if factor.max() != 0 else 0.0
    if min(otsu, average, total) > 3 and N > 50:
        s50 = float(np.sort(factor)[::-1][49])
        m = max(otsu, total)
        f = np.float32(10.0)  # float arithmetic as in the C++ code
        while float(f) * m > s50:
            f = np.float32(float(f) - 0.05)
        keep = factor > float(f) * m
        return A & keep[:, None] & keep[None, :], int(keep.sum()), ops
    return A, -1, ops


def mac(P, Q, inlier_thr=0.10, t_cmp=0.99, min_clique=3, refine=True, top_k=None):
    """Returns (4x4 transform mapping P to Q, info) with info = {N, ops, inliers, cliques, selected, kept}; kept is the
    number of nodes left by the graph reduction, -1 if the graph was not reduced. top_k: keep only the top_k heaviest
    of the node-guided cliques as hypotheses (the authors' Top-K ablation, MAC paper, Table 5; ties to the clique found
    first); None keeps them all (MAC as published, used everywhere except the equal-time comparison)."""
    import igraph
    from acpr.estimators import post_refinement
    P = np.asarray(P, np.float64)
    Q = np.asarray(Q, np.float64)
    N = P.shape[0]
    info = {"N": N, "kept": -1}
    if N < 3:
        info.update(ops=0, inliers=0, cliques=0, selected=0)
        return np.eye(4), info
    # first-order graph, computed in row blocks straight into float32 (bounded memory; same values)
    FCG = np.empty((N, N), dtype=np.float32)
    for a in range(0, N, 512):
        cross = np.abs(cdist(P[a:a + 512], P) - cdist(Q[a:a + 512], Q))
        FCG[a:a + 512] = np.clip(1.0 - cross ** 2 / inlier_thr ** 2, 0.0, None)
    del cross
    np.fill_diagonal(FCG, 0.0)
    FCG[FCG < t_cmp] = 0.0
    SCG = FCG @ FCG
    SCG *= FCG
    del FCG
    ops = N * N + N * N * N
    A = SCG > 0
    if not A.any():
        info.update(ops=int(ops), inliers=0, cliques=0, selected=0)
        return np.eye(4), info
    A, info["kept"], o = _reduce(SCG, A)
    ops += o
    iu, ju = np.nonzero(np.triu(A, 1))  # edges i < j in row-major order
    del A
    g = igraph.Graph(n=N, edges=zip(iu, ju))  # streamed: no Python list of millions of edges
    del iu, ju
    # maximal cliques are written by igraph (C) to a temporary file and processed in bounded chunks: a pair can have
    # millions of them, too many to hold as Python objects
    fd, path = tempfile.mkstemp(suffix=".cliques")
    os.close(fd)
    try:
        g.maximal_cliques(min=min_clique, file=path)
        # node-guided selection: per node, the maximal clique of largest weight (sum of its SCG edge weights); ties go
        # to the clique found first, as in a sequential pass over igraph's output
        best_w = np.full(N, -1.0)
        best_c = np.full(N, -1, dtype=np.int64)
        kept = {}  # node lists of the cliques that are currently some node's best
        n_cliques = 0
        for sizes, flat in _clique_chunks(path):
            w = _clique_weights(SCG, sizes, flat)
            ops += int((sizes ** 2).sum())
            cid = np.repeat(np.arange(n_cliques, n_cliques + len(sizes)), sizes)
            ww = np.repeat(w, sizes)
            order = np.lexsort((cid, -ww, flat))  # by node, then heaviest, then earliest
            first = np.ones(len(order), dtype=bool)
            first[1:] = flat[order][1:] != flat[order][:-1]
            nodes, wn, cn = flat[order][first], ww[order][first], cid[order][first]
            better = wn > best_w[nodes]
            best_w[nodes[better]], best_c[nodes[better]] = wn[better], cn[better]
            offsets = np.concatenate([[0], np.cumsum(sizes)])
            for c in np.unique(cn[better]):
                i = int(c) - n_cliques
                kept[int(c)] = flat[offsets[i]:offsets[i + 1]]
            live = set(np.unique(best_c[best_c >= 0]).tolist())
            kept = {c: m for c, m in kept.items() if c in live}
            n_cliques += len(sizes)
    finally:
        os.remove(path)
    info["cliques"] = n_cliques
    if n_cliques == 0:
        info.update(ops=int(ops), inliers=0, selected=0)
        return np.eye(4), info
    selected = np.unique(best_c[best_c >= 0])
    if top_k is not None and len(selected) > top_k:
        weight = np.zeros(len(selected))
        np.maximum.at(weight, np.searchsorted(selected, best_c[best_c >= 0]), best_w[best_c >= 0])
        selected = selected[np.sort(np.argsort(-weight, kind="stable")[:top_k])]
    members = [kept[int(c)] for c in selected]
    info["selected"] = int(len(selected))
    # instance-equal SVD per selected clique (batched by padding with zero weights)
    k = max(len(m) for m in members)
    Ps = np.zeros((len(selected), k, 3))
    Qs = np.zeros((len(selected), k, 3))
    ws = np.zeros((len(selected), k))
    for r, idx in enumerate(members):
        Ps[r, : len(idx)], Qs[r, : len(idx)], ws[r, : len(idx)] = P[idx], Q[idx], 1.0
    Ts = kabsch(Ps, Qs, ws)
    # MAE score over all correspondences
    best_s, best_T = -1.0, np.eye(4)
    for start in range(0, len(Ts), 256):
        T = Ts[start:start + 256]
        res = np.linalg.norm(np.einsum("hij,nj->hni", T[:, :3, :3], P) + T[:, None, :3, 3] - Q[None], axis=2)
        score = np.clip((inlier_thr - res) / inlier_thr, 0.0, None).sum(axis=1)
        j = int(np.argmax(score))
        if score[j] > best_s:
            best_s, best_T = float(score[j]), T[j]
    ops += len(Ts) * N
    if refine:
        best_T, o = post_refinement(best_T, P, Q, thr=inlier_thr, iters=20)
        ops += o
    inliers = int((np.linalg.norm(P @ best_T[:3, :3].T + best_T[:3, 3] - Q, axis=1) < inlier_thr).sum())
    info.update(ops=int(ops), inliers=inliers)
    return best_T, info
