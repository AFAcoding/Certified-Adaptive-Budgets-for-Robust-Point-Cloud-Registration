"""Exploration (fitting, calibration and development splits only): uncertainty of each stage's pose from the
geometry of its correspondences.

For every logged stage estimate T of the compatibility-ordered budget (logs/budgetc_<split>.jsonl), the correspondences
are recomputed exactly as the log builder computes them (FPFH, nearest neighbours, Lowe-ratio order, cap 4,000, then
acpr.estimators.compat_order), and the stage's support set is taken as the correspondences of its budget that T
aligns within tau = 0.10 m. Signals (no ground truth):
  g_lmin         log of the smallest eigenvalue of the support's spatial covariance (source side; m^2)
  g_lratio       smallest / largest eigenvalue (planar or linear support -> near 0: a degenerate pose)
  g_inl_spread   sqrt of the covariance trace (m)
  g_hess_logdet  log det of the Gauss-Newton Hessian sum_i J_i^T J_i / n of the point-to-point residuals at T,
                 J_i = [-[R p_i]_x, I] (pose = small rotation + translation)
  g_hess_lmin    log of its smallest eigenvalue (the least constrained pose direction)
Their single-thread cost per stage is recorded.

Usage: python -I -u scripts/explore/geom_features.py <split> [--workers 4]
Writes results/explore/geom_<split>.jsonl
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "ACPR_KD_WORKERS"):
    os.environ.setdefault(var, "1")

import numpy as np  # noqa: E402

from acpr import LOG_ROOT, RESULTS_ROOT  # noqa: E402

BLIND = ("v2_blind_hi", "v2_blind_lo", "v3_blind_hi", "v3_blind_lo", "v4_blind_hi", "v4_blind_lo", "kitti_raw_blind")
TAU = 0.10
BUDGETS = (250, 500, 1000, 2000, 4000)
_PAIRS = {}
NAMES = ("g_lmin", "g_lratio", "g_inl_spread", "g_hess_logdet", "g_hess_lmin")


def skew(v):
    z = np.zeros((len(v), 3, 3))
    z[:, 0, 1], z[:, 0, 2], z[:, 1, 2] = -v[:, 2], v[:, 1], -v[:, 0]
    z[:, 1, 0], z[:, 2, 0], z[:, 2, 1] = v[:, 2], -v[:, 1], v[:, 0]
    return z


def signals(P, Q, T):
    R, t = T[:3, :3], T[:3, 3]
    RP = P @ R.T
    res = np.linalg.norm(RP + t - Q, axis=1)
    inl = res < TAU
    if inl.sum() < 4:
        return {"g_lmin": -12.0, "g_lratio": 0.0, "g_inl_spread": 0.0, "g_hess_logdet": -40.0, "g_hess_lmin": -12.0}
    X = P[inl]
    ev = np.sort(np.linalg.eigvalsh(np.cov(X.T)))
    J = np.concatenate([-skew(RP[inl]), np.broadcast_to(np.eye(3), (int(inl.sum()), 3, 3))], axis=2)  # n x 3 x 6
    H = np.einsum("nij,nik->jk", J, J) / inl.sum()
    hv = np.linalg.eigvalsh(H)
    return {"g_lmin": float(np.log(max(ev[0], 1e-12))), "g_lratio": float(ev[0] / max(ev[-1], 1e-12)),
            "g_inl_spread": float(np.sqrt(max(ev.sum(), 0.0))),
            "g_hess_logdet": float(np.sum(np.log(np.maximum(hv, 1e-12)))), "g_hess_lmin": float(np.log(max(hv[0], 1e-12)))}


def work(split, rec):
    from acpr.data import load_pairs
    from acpr.estimators import compat_order, nn_correspondences
    from acpr.features import get_fpfh
    pairs = _PAIRS.setdefault(split, {p.pair_id: p for p in load_pairs(split)})
    p = pairs[rec["pair_id"]]
    rp, rf, _ = get_fpfh(p.pcd0)
    sp, sf, _ = get_fpfh(p.pcd1)
    P, Q, ratio = nn_correspondences(sp, sf, rp, rf)
    n = min(P.shape[0], 4000)
    P, Q = P[:n], Q[:n]
    perm, _ = compat_order(P, Q, thr=0.10)
    out = {"pair_id": rec["pair_id"]}
    for est in ("sc2", "turbo"):
        cols = {k: [] for k in NAMES + ("t",)}
        for b, st in enumerate(rec[est]):
            if st is None:
                for k in cols:
                    cols[k].append(None)
                continue
            m = min(BUDGETS[b], n)
            Pi, Qi = (P[perm[:m]], Q[perm[:m]]) if m < n else (P, Q)
            t0 = time.perf_counter()
            sg = signals(Pi, Qi, np.asarray(st["T"], dtype=float).reshape(4, 4))
            cols["t"].append(time.perf_counter() - t0)
            for k in NAMES:
                cols[k].append(sg[k])
        out[est] = cols
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("split")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    if a.split in BLIND:
        sys.exit("blind test sets are not used for exploration")
    with open(LOG_ROOT / f"budgetc_{a.split}.jsonl") as f:
        recs = [json.loads(x) for x in f if x.strip()]
    out = RESULTS_ROOT / "explore" / f"geom_{a.split}.jsonl"
    with open(out, "w") as g, ProcessPoolExecutor(max_workers=a.workers) as ex:
        for k, r in enumerate(ex.map(work, [a.split] * len(recs), recs, chunksize=8)):
            g.write(json.dumps(r) + "\n")
            if k % 500 == 0:
                print(f"  {a.split} {k}/{len(recs)}", flush=True)


if __name__ == "__main__":
    main()
