"""Design study (validation only): which ordering puts the most true matches into a small budget?

Orderings of the same top-4,000 (Lowe ratio) correspondences:
  ratio   Lowe ratio (baseline used so far)
  deg1    first-order compatibility degree against anchors A = top-M by ratio
  deg2    second-order (SC^2-style) degree against the anchors
For each, report inliers in the top-k and the success of SC^2 / TurboReg run on the top-k,
with the reordering cost included.

Usage: python -I -u scripts/ordering_study.py [every=3] [workers=6]
"""

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")

import numpy as np  # noqa: E402
from scipy.spatial.distance import cdist  # noqa: E402

from acpr import RESULTS_ROOT  # noqa: E402
from acpr.data import load_pairs  # noqa: E402

N_ALL, KS, M_ANCHOR, THR = 4000, (250, 500), 500, 0.10


def compat_order(P, Q, m, second_order):
    """Return (order, seconds). Degree of every correspondence w.r.t. the first m (ratio-ordered) anchors."""
    t0 = time.perf_counter()
    A = slice(0, m)
    C = (np.abs(cdist(P, P[A]) - cdist(Q, Q[A])) < THR).astype(np.float32)  # (N, m)
    if second_order:
        CAA = C[A]  # (m, m)
        score = (C * (C @ CAA)).sum(axis=1)
    else:
        score = C.sum(axis=1)
    # stable: ties keep ratio order
    order = np.argsort(-score, kind="stable")
    return order, time.perf_counter() - t0


def run(index):
    from acpr.estimators import nn_correspondences, sc2_pcr, turboreg
    from acpr.features import get_fpfh
    from acpr.metrics import rre_rte

    p = load_pairs("val")[index]
    rp, rf, _ = get_fpfh(p.pcd0)
    sp, sf, _ = get_fpfh(p.pcd1)
    P, Q, _ = nn_correspondences(sp, sf, rp, rf)
    P, Q = P[:N_ALL], Q[:N_ALL]
    gt = np.linalg.norm(P @ p.transform[:3, :3].T + p.transform[:3, 3] - Q, axis=1) < 0.1
    out = {"pair_id": p.pair_id, "n": int(P.shape[0]), "gt_total": int(gt.sum())}
    orders = {"ratio": (np.arange(P.shape[0]), 0.0)}
    orders["deg1"] = compat_order(P, Q, min(M_ANCHOR, P.shape[0]), False)
    orders["deg2"] = compat_order(P, Q, min(M_ANCHOR, P.shape[0]), True)
    for name, (o, t_ord) in orders.items():
        res = {"t_order": t_ord}
        for k in KS:
            idx = o[:k]
            res[f"inl{k}"] = int(gt[idx].sum())
            for en, fn in [("sc2", sc2_pcr), ("turbo", turboreg)]:
                t0 = time.perf_counter()
                T, _ = fn(P[idx], Q[idx])
                res[f"{en}{k}_s"] = time.perf_counter() - t0
                rre, rte = rre_rte(p.transform, T)
                res[f"{en}{k}_ok"] = bool(rre <= 15 and rte <= 0.3)
        out[name] = res
    return out


def main():
    every = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    idx = list(range(0, len(load_pairs("val")), every))
    rows = []
    with ProcessPoolExecutor(workers) as ex:
        for i, r in enumerate(ex.map(run, idx, chunksize=4), 1):
            rows.append(r)
            if i % 100 == 0:
                print(f"  {i}/{len(idx)}", flush=True)
    (RESULTS_ROOT / "budget").mkdir(parents=True, exist_ok=True)
    with open(RESULTS_ROOT / "budget" / "ordering_study_val.json", "w") as f:
        json.dump(rows, f)
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"\nvalidation pairs: {len(rows)}; mean true matches among all 4,000: {np.mean([r['gt_total'] for r in rows]):.1f}")
    for name in ["ratio", "deg1", "deg2"]:
        line = f"  {name:5s}: reorder {1e3 * np.mean([r[name]['t_order'] for r in rows]):5.1f} ms"
        for k in KS:
            line += (f" | top{k}: inliers {np.mean([r[name][f'inl{k}'] for r in rows]):5.1f}, "
                     f"SC2 RR {100 * np.mean([r[name][f'sc2{k}_ok'] for r in rows]):5.1f}% "
                     f"TurboReg RR {100 * np.mean([r[name][f'turbo{k}_ok'] for r in rows]):5.1f}%")
        print(line)


if __name__ == "__main__":
    main()
