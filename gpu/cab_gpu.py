"""CAB on a GPU (PROTOCOL.md, addendum C): PyTorch ports of the estimators SC2-PCR and TurboReg, of MAC's graph stages
(its maximal-clique search stays on the CPU, as in the authors' implementations), of the compatibility ordering and
the hardness gate's signals, and the CAB controller as in scripts/live_budget.py, for live timing on a GPU.

The ports follow src/acpr/estimators.py, src/acpr/mac.py and src/acpr/gate.py operation by operation. Distances are
computed in double precision and every graph product in single precision, as on the CPU; ties in a few sorts can be
broken differently, so a GPU run can differ from the CPU logs on rare pairs, which run_gpu_timing.py reports. The
controller's classifiers and the gate are exported as plain arrays (export_bundle.py) and evaluated with NumPy here.

Self-contained: needs only numpy and torch (and igraph for MAC).
"""

from __future__ import annotations

import os
import tempfile

import numpy as np
import torch

BUDGETS = (250, 500, 1000, 2000, 4000)
FEATURES = ["log_inl", "inl_frac", "inl_all_frac", "top250_frac", "log_dpose_deg", "log_dpose_m", "agree",
            "stage", "log_N_all", "ratio_med", "inl_gain", "log_inl_all"]
GATE_FEATURES = ["log_N", "ratio_q10", "ratio_q50", "ratio_top250", "deg_max", "deg_q10", "deg_mean", "score_top1",
                 "score_top10", "score_top50", "score_top250", "n_support50", "n_support25", "anchor_cohesion"]


def sync(device):
    if device.type == "cuda":
        torch.cuda.synchronize(device)


def cross_dist(P, Q, rows=None, cols=None):
    """| ||p_i - p_j|| - ||q_i - q_j|| | in double precision (P, Q: float64 tensors)."""
    Pr = P if rows is None else P[rows]
    Qr = Q if rows is None else Q[rows]
    Pc = P if cols is None else P[cols]
    Qc = Q if cols is None else Q[cols]
    return (torch.cdist(Pr, Pc, compute_mode="donot_use_mm_for_euclid_dist")
            - torch.cdist(Qr, Qc, compute_mode="donot_use_mm_for_euclid_dist")).abs_()


# ------------------------------------------------------------------------------------------------- rigid estimation
def kabsch(src, ref, w=None):
    """Weighted least-squares rigid transforms src -> ref, batched over leading dims (float64)."""
    if w is None:
        w = torch.ones(src.shape[:-1], dtype=src.dtype, device=src.device)
    w = w / w.sum(-1, keepdim=True).clamp_min(1e-12)
    cs = (w[..., None] * src).sum(-2, keepdim=True)
    cr = (w[..., None] * ref).sum(-2, keepdim=True)
    H = torch.einsum("...ni,...nj->...ij", w[..., None] * (src - cs), ref - cr)
    U, _, Vt = torch.linalg.svd(H)
    d = torch.sign(torch.linalg.det(torch.einsum("...ji,...kj->...ik", Vt, U)))
    D = torch.zeros_like(H)
    D[..., 0, 0] = 1.0
    D[..., 1, 1] = 1.0
    D[..., 2, 2] = d
    R = torch.einsum("...ji,...jk,...lk->...il", Vt, D, U)
    t = cr[..., 0, :] - torch.einsum("...ij,...j->...i", R, cs[..., 0, :])
    T = torch.zeros(H.shape[:-2] + (4, 4), dtype=H.dtype, device=H.device)
    T[..., :3, :3] = R
    T[..., :3, 3] = t
    T[..., 3, 3] = 1.0
    return T


def residuals(T, P, Q):
    return torch.linalg.norm(P @ T[:3, :3].T + T[:3, 3] - Q, dim=1)


def post_refinement(T, P, Q, thr=0.10, iters=20):
    prev = -1
    for _ in range(iters):
        d = residuals(T, P, Q)
        inl = d < thr
        n = int(inl.sum())
        if n < 3 or abs(n - prev) < 1:
            break
        prev = n
        w = 1.0 / (1.0 + (d[inl] / thr) ** 2)
        T = kabsch(P[inl], Q[inl], w.clamp_min(1e-12))
    return T


def verify(Ts, P, Q, thr, chunk=512):
    """Inlier count of every hypothesis (single precision)."""
    PT, QT = P.T.float(), Q.T.float()
    thr2 = float(thr * thr)
    out = []
    for s in range(0, Ts.shape[0], chunk):
        T = Ts[s:s + chunk].float()
        D = torch.matmul(T[:, :3, :3], PT) + T[:, :3, 3:4] - QT[None]
        out.append(((D * D).sum(1) < thr2).sum(1))
    return torch.cat(out)


def leading_eigenvector(M, iters=10):
    """Power iteration with the CPU code's early stop; M: (..., n, n)."""
    v = torch.ones(M.shape[:-1], dtype=M.dtype, device=M.device)
    for _ in range(iters):
        nv = torch.einsum("...ij,...j->...i", M, v)
        nv = nv / (torch.linalg.norm(nv, dim=-1, keepdim=True) + 1e-12)
        if torch.allclose(nv, v, rtol=1e-5, atol=1e-6):
            v = nv
            break
        v = nv
    return v


# ------------------------------------------------------------------------------------------------- estimators
def sc2_pcr(P, Q, d_thre=0.10, inlier_thr=0.10, ratio=0.2, nms_radius=0.10, k1=30, k2=20, refine=True):
    N = P.shape[0]
    dev = P.device
    if N < 3:
        return torch.eye(4, dtype=P.dtype, device=dev), 0
    src_dist = torch.cdist(P, P, compute_mode="donot_use_mm_for_euclid_dist")
    cross = (src_dist - torch.cdist(Q, Q, compute_mode="donot_use_mm_for_euclid_dist")).abs_()
    soft = (1.0 - cross ** 2 / d_thre ** 2).clamp_min_(0)  # double precision, as on the CPU
    hard = (cross < d_thre).float()
    tight = (cross < d_thre / 2).float()
    del cross
    conf = leading_eigenvector(soft)
    del soft
    nbr = src_dist < nms_radius
    local_max = conf >= torch.where(nbr, conf[None, :], torch.full_like(conf[None, :], -float("inf"))).amax(1)
    del nbr
    cand = torch.nonzero(local_max).flatten()
    max_num = max(1, int(N * ratio))
    seeds = cand[torch.argsort(-conf[cand], stable=True)][:max_num]
    sc2 = (tight[seeds] @ tight) * hard[seeds]
    k1e = min(k1, N)
    k2e = min(k2, k1e)
    knn = torch.topk(sc2, k1e, dim=1).indices  # (S, k1)
    lt = tight[knn[:, :, None], knn[:, None, :]]
    lsc2 = (lt @ lt) * hard[knn[:, :, None], knn[:, None, :]]
    fine = torch.gather(knn, 1, torch.topk(lsc2.sum(-1), k2e, dim=1).indices)  # (S, k2)
    sd = src_dist[fine[:, :, None], fine[:, None, :]]
    Qf = Q[fine]
    loc = (1.0 - (sd - torch.cdist(Qf, Qf, compute_mode="donot_use_mm_for_euclid_dist")).abs() ** 2 / d_thre ** 2)
    loc = loc.clamp_min(0)
    lt2 = tight[fine[:, :, None], fine[:, None, :]]
    w = leading_eigenvector((lt2 @ lt2).double() * loc)
    hyps = kabsch(P[fine], Q[fine], w.abs().clamp_min(1e-12))
    fit = verify(hyps, P, Q, inlier_thr)
    T = hyps[int(torch.argmax(fit))]
    if refine:
        T = post_refinement(T, P, Q, inlier_thr)
    return T, int((residuals(T, P, Q) < inlier_thr).sum())


def turboreg(P, Q, tau=0.012, k1=2000, k2=2, inlier_thr=0.10, refine=True):
    N = P.shape[0]
    dev = P.device
    eye = torch.eye(4, dtype=P.dtype, device=dev)
    if N < 3:
        return eye, 0
    G = (cross_dist(P, Q) < tau).float()
    G.fill_diagonal_(0)
    Gs = G * (G @ G)
    del G
    iu = torch.triu_indices(N, N, 1, device=dev)
    wts = Gs[iu[0], iu[1]]
    nz = torch.nonzero(wts > 0).flatten()
    if nz.numel() == 0:
        return eye, 0
    top = nz[torch.argsort(-wts[nz], stable=True)[:min(k1, nz.numel())]]
    I, J = iu[0][top], iu[1][top]
    cand = (Gs[I] > 0) & (Gs[J] > 0)
    score = torch.where(cand, Gs[I] + Gs[J], torch.full_like(Gs[I], -1.0))
    ar = torch.arange(I.numel(), device=dev)
    score[ar, I] = -1.0
    score[ar, J] = -1.0
    kk = min(k2, N)
    top_s = torch.topk(score, kk, dim=1)
    valid = (top_s.values > 0).reshape(-1)
    tri = torch.stack([I.repeat_interleave(kk), J.repeat_interleave(kk), top_s.indices.reshape(-1)], 1)[valid]
    if tri.shape[0] == 0:
        return eye, 0
    hyps = kabsch(P[tri], Q[tri])
    fit = verify(hyps, P, Q, inlier_thr)
    T = hyps[int(torch.argmax(fit))]
    if refine:
        T = post_refinement(T, P, Q, inlier_thr)
    return T, int((residuals(T, P, Q) < inlier_thr).sum())


def _otsu(values):
    """The MAC C++ implementation's OTSU_thresh (as acpr.mac._otsu)."""
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


def mac(P, Q, inlier_thr=0.10, t_cmp=0.99, min_clique=3, refine=True):
    """MAC as acpr.mac.mac: graphs, graph reduction, hypotheses, scoring and refinement on the device; maximal cliques
    and the node-guided selection on the CPU (igraph), as in the authors' implementations."""
    import igraph
    N = P.shape[0]
    dev = P.device
    eye = torch.eye(4, dtype=P.dtype, device=dev)
    if N < 3:
        return eye, 0
    cross = cross_dist(P, Q)
    FCG = (1.0 - cross ** 2 / inlier_thr ** 2).clamp_min_(0).float()
    del cross
    FCG.fill_diagonal_(0)
    FCG[FCG < t_cmp] = 0
    SCG = (FCG @ FCG) * FCG
    del FCG
    A = SCG > 0
    if not bool(A.any()):
        return eye, 0
    deg = A.sum(1).double()
    H = torch.pow(SCG, 1.0 / 3)
    num = 0.5 * (H * (H @ H)).double().sum(1)
    del H
    has = deg > 1
    den = deg * (deg - 1) / 2.0
    factor = torch.zeros(N, dtype=torch.float64, device=dev)
    factor[has] = num[has] / den[has]
    f_np = factor.cpu().numpy()
    average = float(f_np.mean())
    total = float(num[has].sum() / den[has].sum()) if bool(has.any()) else 0.0
    otsu = _otsu(f_np) if f_np.max() != 0 else 0.0
    if min(otsu, average, total) > 3 and N > 50:
        s50 = float(np.sort(f_np)[::-1][49])
        m = max(otsu, total)
        f = np.float32(10.0)
        while float(f) * m > s50:
            f = np.float32(float(f) - 0.05)
        keep = factor > float(f) * m
        A = A & keep[:, None] & keep[None, :]
    iu, ju = torch.nonzero(torch.triu(A, 1), as_tuple=True)
    del A
    g = igraph.Graph(n=N, edges=zip(iu.cpu().numpy(), ju.cpu().numpy()))
    scg = SCG.cpu().numpy()
    del SCG
    fd, path = tempfile.mkstemp(suffix=".cliques")
    os.close(fd)
    try:
        g.maximal_cliques(min=min_clique, file=path)
        members = _node_guided(scg, path, N)
    finally:
        os.remove(path)
    if not members:
        return eye, 0
    k = max(len(m) for m in members)
    Ps = torch.zeros((len(members), k, 3), dtype=P.dtype, device=dev)
    Qs = torch.zeros_like(Ps)
    ws = torch.zeros((len(members), k), dtype=P.dtype, device=dev)
    for r, idx in enumerate(members):
        it = torch.as_tensor(idx, device=dev)
        Ps[r, :len(idx)], Qs[r, :len(idx)], ws[r, :len(idx)] = P[it], Q[it], 1.0
    Ts = kabsch(Ps, Qs, ws)
    best_s, best_T = -1.0, eye
    for start in range(0, Ts.shape[0], 256):
        T = Ts[start:start + 256]
        res = torch.linalg.norm(torch.einsum("hij,nj->hni", T[:, :3, :3], P) + T[:, None, :3, 3] - Q[None], dim=2)
        score = ((inlier_thr - res) / inlier_thr).clamp_min(0).sum(1)
        j = int(torch.argmax(score))
        if float(score[j]) > best_s:
            best_s, best_T = float(score[j]), T[j]
    T = post_refinement(best_T, P, Q, inlier_thr) if refine else best_T
    return T, int((residuals(T, P, Q) < inlier_thr).sum())


def _node_guided(scg, path, N, chunk_lines=200_000, chunk_entries=2_000_000, gather=4_000_000):
    """Node-guided clique selection over igraph's clique file, as acpr.mac (heaviest clique per node, ties to the
    first found); returns the member lists of the selected cliques in clique order."""
    best_w = np.full(N, -1.0)
    best_c = np.full(N, -1, dtype=np.int64)
    kept, n_cliques = {}, 0
    with open(path) as fh:
        while True:
            lines, sizes, n = [], [], 0
            for ln in fh:
                lines.append(ln)
                sizes.append(ln.count(" ") + 1)
                n += sizes[-1]
                if len(lines) >= chunk_lines or n >= chunk_entries:
                    break
            if not lines:
                break
            flat = np.array("".join(lines).split(), dtype=np.int64)
            sizes = np.array(sizes, dtype=np.int64)
            w = np.empty(len(sizes))
            offs = np.concatenate([[0], np.cumsum(sizes)[:-1]])
            for k in np.unique(sizes):
                rows = np.nonzero(sizes == k)[0]
                step = max(1, gather // int(k * k))
                for a in range(0, len(rows), step):
                    r = rows[a:a + step]
                    arr = flat[offs[r][:, None] + np.arange(k)]
                    w[r] = scg[arr[:, :, None], arr[:, None, :]].astype(np.float64).sum(axis=(1, 2)) / 2.0
            cid = np.repeat(np.arange(n_cliques, n_cliques + len(sizes)), sizes)
            ww = np.repeat(w, sizes)
            order = np.lexsort((cid, -ww, flat))
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
    return [kept[int(c)] for c in np.unique(best_c[best_c >= 0])]


ESTIMATORS = {"sc2": sc2_pcr, "turbo": turboreg, "mac": mac}


# ------------------------------------------------------------------------------------------------- ordering, gate
def _compat(P, Q, rows, cols, thr):
    return (cross_dist(P, Q, rows, cols) < thr).float()


def compat_order(P, Q, m=100, pool=500, thr=0.10):
    n = P.shape[0]
    c = torch.arange(min(pool, n), device=P.device)
    W = _compat(P, Q, c, c, thr)
    a = torch.argsort(-W.sum(1), stable=True)[:m]
    C = _compat(P, Q, None, a, thr)
    score = (C * (C @ C[a])).sum(1)
    return torch.argsort(-score, stable=True)


def signals(P, Q, ratio, thr, m=100, pool=500):
    """The gate's 14 pre-estimation signals and the compatibility order (as acpr.gate.signals, return_order=True)."""
    n = P.shape[0]
    c = torch.arange(min(pool, n), device=P.device)
    W = _compat(P, Q, c, c, thr)
    deg = W.sum(1)
    a = torch.argsort(-deg, stable=True)[:m]
    k = a.numel()
    C = _compat(P, Q, None, a, thr)
    raw = (C * (C @ C[a])).sum(1)
    score = raw / (k * k)
    s = torch.sort(score, descending=True).values.double().cpu().numpy()
    deg_a = (torch.sort(deg[a], descending=True).values / max(W.shape[0], 1)).double().cpu().numpy()
    support = C.mean(1)
    r = ratio
    top = lambda j: float(s[min(j, n - 1)])  # noqa: E731
    out = {"log_N": float(np.log(n)), "ratio_q10": float(np.quantile(r, 0.1)), "ratio_q50": float(np.median(r)),
           "ratio_top250": float(np.mean(r[:250])), "deg_max": float(deg_a[0]), "deg_q10": float(deg_a[min(9, k - 1)]),
           "deg_mean": float(deg_a.mean()), "score_top1": top(0), "score_top10": top(9), "score_top50": top(49),
           "score_top250": top(249), "n_support50": float(np.log1p(int((support >= 0.5).sum()))),
           "n_support25": float(np.log1p(int((support >= 0.25).sum()))),
           "anchor_cohesion": float(C[a].double().mean())}
    return out, torch.argsort(-raw, stable=True)


# ------------------------------------------------------------------------------------------------- classifiers
def _expit(x):
    return 1.0 / (1.0 + np.exp(-x))


class Classifier:
    """predict_proba of a classifier exported by export_bundle.py (logistic, quadratic logistic, boosted trees or a
    constant), evaluated with NumPy."""

    def __init__(self, spec, arrays):
        self.kind = spec["kind"]
        self.spec = spec
        self.a = arrays

    def proba(self, X):
        X = np.asarray(X, dtype=np.float64)
        if self.kind == "constant":
            return np.full(len(X), self.spec["p"])
        if self.kind == "logistic":
            Z = (X - self.a["mean"]) / self.a["scale"]
            if "powers" in self.a:  # quadratic features, then a second scaler
                Z = np.prod(Z[:, None, :] ** self.a["powers"][None], axis=2)
                Z = (Z - self.a["mean2"]) / self.a["scale2"]
            return _expit(Z @ self.a["coef"] + self.a["intercept"])
        if self.kind == "trees":  # HistGradientBoostingClassifier: baseline + sum of tree leaves
            raw = np.full(len(X), float(self.a["baseline"]))
            for t in range(int(self.spec["n_trees"])):
                lo, hi = self.a["tree_offsets"][t], self.a["tree_offsets"][t + 1]
                feat, thr = self.a["feature"][lo:hi], self.a["threshold"][lo:hi]
                left, right, leaf = self.a["left"][lo:hi], self.a["right"][lo:hi], self.a["is_leaf"][lo:hi]
                value = self.a["value"][lo:hi]
                for i in range(len(X)):
                    node = 0
                    while not leaf[node]:
                        node = left[node] if X[i, feat[node]] <= thr[node] else right[node]
                    raw[i] += value[node]
            return _expit(raw)
        raise ValueError(self.kind)


# ------------------------------------------------------------------------------------------------- CAB controller
def _pose_change(prev_T, T):
    if prev_T is None:
        return 180.0, 10.0
    R = prev_T[:3, :3].T @ T[:3, :3]
    return (float(np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1)))),
            float(np.linalg.norm(prev_T[:3, 3] - T[:3, 3])))


def _features(stages, ladder, k, N_all):
    """Features of the k-th visited stage, as scripts/analyze_budget.trajectory_ladder."""
    prev_T, prev_inl, out = None, 0, None
    Nn = max(N_all, 1)
    for j, b in enumerate(ladder[:k + 1]):
        st = stages[b]
        ddeg, dm = _pose_change(prev_T, st["T"])
        prev_T = st["T"]
        n = max(st["n"], 1)
        out = {"log_inl": float(np.log1p(st["inliers"])), "inl_frac": st["inliers"] / n,
               "inl_all_frac": st["inliers_all"] / Nn, "top250_frac": st["inliers_top250"] / min(250, Nn),
               "log_dpose_deg": float(np.log1p(ddeg)), "log_dpose_m": float(np.log1p(dm)),
               "agree": float(ddeg < 5 and dm < 0.2), "stage": j, "log_N_all": float(np.log(Nn)),
               "ratio_med": st["ratio_med"], "inl_gain": float(st["inliers_all"] - prev_inl) / Nn,
               "log_inl_all": float(np.log1p(st["inliers_all"]))}
        if j == 0:
            first_log_inl_all = out["log_inl_all"]
        prev_inl = st["inliers_all"]
    return out, first_log_inl_all


class Controller:
    """One certified configuration (CAB without the gate, or the final method with its gate)."""

    def __init__(self, cfg, arrays, compat_thr):
        self.ladder = tuple(cfg["ladder_idx"])
        self.edges = np.asarray(cfg["edges"], dtype=float)
        self.lams = list(cfg["lambdas"])
        self.compat = cfg["prefix"] == "budgetc"
        self.compat_thr = compat_thr
        self.clf = Classifier(cfg["clf"], arrays["clf"])
        self.gate = Classifier(cfg["gate"], arrays["gate"]) if cfg.get("gate") else None
        self.gate_threshold = cfg.get("gate_threshold")

    def run(self, fn, kw, P, Q, ratio, inlier):
        """Adaptive run (timed by the caller). P, Q: device tensors (float64); ratio: NumPy array. Returns
        (T, stop stage); stop -1: gated to the full budget."""
        N_all = P.shape[0]
        perm = None
        if self.gate is not None:
            sig, perm = signals(P, Q, ratio, self.compat_thr)
            if self.gate.proba([[sig[f] for f in GATE_FEATURES]])[0] >= self.gate_threshold:
                T, _ = fn(P, Q, **kw)
                return T, -1
        if self.compat and BUDGETS[self.ladder[0]] < N_all:
            if perm is None:
                perm = compat_order(P, Q, thr=self.compat_thr)
            Po, Qo, ro = P[perm], Q[perm], ratio[perm.cpu().numpy()]
        else:
            Po, Qo, ro = P, Q, ratio
        stages = [None] * 5
        prev_st, prev_T, group = None, None, None
        for k, b in enumerate(self.ladder):
            n = min(BUDGETS[b], N_all)
            if prev_st is not None and n == prev_st["n"]:
                st = dict(prev_st, repeat=True)  # same input as the previous budget: nothing to recompute
            else:
                if n >= N_all:  # full set: the standard input order
                    Po, Qo, ro = P, Q, ratio
                T, inl = fn(Po[:n], Qo[:n], **kw)
                res_all = residuals(T, P, Q)
                st = {"n": n, "inliers": inl, "inliers_all": int((res_all < inlier).sum()),
                      "inliers_top250": int((res_all[:250] < inlier).sum()),
                      "ratio_med": float(np.median(ro[:n])) if n else 1.0, "T": T.cpu().numpy()}
                prev_T = T
            prev_st = st
            stages[b] = st
            x, first = _features(stages, self.ladder, k, N_all)
            p_now = float(self.clf.proba([[x[f] for f in FEATURES]])[0])
            if group is None:
                group = int(np.searchsorted(self.edges, first, side="right"))
            if p_now >= self.lams[group] or k == len(self.ladder) - 1:
                return prev_T, k
        return prev_T, len(self.ladder) - 1


def success(T, T_gt, rot_deg, trans_m):
    """Registration success: rotation and translation error within the dataset's thresholds."""
    T = np.asarray(T, dtype=np.float64)
    R = T_gt[:3, :3].T @ T[:3, :3]
    re = float(np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1))))
    te = float(np.linalg.norm(T_gt[:3, 3] - T[:3, 3]))
    return bool(re <= rot_deg and te <= trans_m)
