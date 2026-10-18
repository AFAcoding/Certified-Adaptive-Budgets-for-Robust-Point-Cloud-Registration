"""Design study 2 (validation only): cheap compatibility orderings + registrability signals.

No estimator runs: reports, per ordering, true matches in the top-k, reordering time (single
thread) and AUROC of compatibility statistics for predicting that the full-budget estimator
fails (labels from logs/budget_val.jsonl).

Usage: python -I -u scripts/ordering_study_fast.py [every=3] [workers=6]
"""

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")

import numpy as np  # noqa: E402

from acpr import LOG_ROOT, RESULTS_ROOT  # noqa: E402
from acpr.data import load_pairs  # noqa: E402

N_ALL, KS, THR = 4000, (250, 500), 0.10


def _dist(X, Y):
    d2 = (X * X).sum(1)[:, None] + (Y * Y).sum(1)[None] - 2.0 * (X @ Y.T)
    return np.sqrt(np.maximum(d2, 0, out=d2), out=d2)


def compat(P, Q, a):
    """(N, |a|) float32 first-order compatibility against anchor indices a."""
    return (np.abs(_dist(P, P[a]) - _dist(Q, Q[a])) < THR).astype(np.float32)


def orderings(P, Q):
    P = (P - P.mean(0)).astype(np.float32)
    Q = (Q - Q.mean(0)).astype(np.float32)
    n = P.shape[0]
    out, stats = {}, {}
    for m in (100, 250, 500):
        a = np.arange(min(m, n))
        t0 = time.perf_counter()
        C = compat(P, Q, a)
        s1 = C.sum(1)
        o1 = np.argsort(-s1, kind="stable")
        t1 = time.perf_counter() - t0
        out[f"deg1_m{m}"] = (o1, t1)
        if m <= 250:
            t0 = time.perf_counter()
            C = compat(P, Q, a)
            s2 = (C * (C @ C[a])).sum(1)
            out[f"deg2_m{m}"] = (np.argsort(-s2, kind="stable"), time.perf_counter() - t0)
        if m == 250:
            # two passes: anchors re-chosen as the top-m by first-order degree
            t0 = time.perf_counter()
            C = compat(P, Q, a)
            a2 = np.argsort(-C.sum(1), kind="stable")[: len(a)]
            C2 = compat(P, Q, a2)
            s3 = C2.sum(1)
            out["iter_m250"] = (np.argsort(-s3, kind="stable"), time.perf_counter() - t0)
            t0 = time.perf_counter()
            s4 = (C2 * (C2 @ C2[a2])).sum(1)
            out["iter2_m250"] = (np.argsort(-s4, kind="stable"), time.perf_counter() - t0 + out["iter_m250"][1])
            # registrability statistics (from the two-pass pass, essentially free)
            stats = {"deg1_max": float(s1.max()), "deg1_top50": float(np.sort(s1)[-50:].mean()),
                     "iter_max": float(s3.max()), "iter_top50": float(np.sort(s3)[-50:].mean()),
                     "iter_n_hi": float((s3 >= 0.5 * s3.max()).sum()),
                     "sc_top50": float(np.sort(s4)[-50:].mean())}
    return out, stats


def run(index):
    from acpr.estimators import nn_correspondences
    from acpr.features import get_fpfh

    p = load_pairs("val")[index]
    rp, rf, _ = get_fpfh(p.pcd0)
    sp, sf, _ = get_fpfh(p.pcd1)
    P, Q, _ = nn_correspondences(sp, sf, rp, rf)
    P, Q = P[:N_ALL], Q[:N_ALL]
    gt = np.linalg.norm(P @ p.transform[:3, :3].T + p.transform[:3, 3] - Q, axis=1) < 0.1
    o, stats = orderings(P, Q)
    o["ratio"] = (np.arange(P.shape[0]), 0.0)
    res = {"pair_id": p.pair_id, "overlap": p.overlap, "gt_total": int(gt.sum()), "stats": stats}
    for name, (od, t) in o.items():
        res[name] = {"t": t, **{f"inl{k}": int(gt[od[:k]].sum()) for k in KS}}
    return res


def auroc(score, y):
    """P(score of a positive > score of a negative), ties 1/2."""
    from scipy.stats import rankdata
    r = rankdata(score)
    n1 = y.sum()
    n0 = len(y) - n1
    return (r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    every = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    idx = list(range(0, len(load_pairs("val")), every))
    with ProcessPoolExecutor(workers) as ex:
        rows = list(ex.map(run, idx, chunksize=4))
    with open(RESULTS_ROOT / "budget" / "ordering_study_fast_val.json", "w") as f:
        json.dump(rows, f)
    names = [k for k in rows[0] if isinstance(rows[0][k], dict) and "t" in rows[0][k]]
    print(f"validation pairs: {len(rows)}")
    for nm in names:
        print(f"  {nm:11s} reorder {1e3 * np.median([r[nm]['t'] for r in rows]):6.1f} ms (median) "
              f"| inliers top250 {np.mean([r[nm]['inl250'] for r in rows]):6.1f} top500 {np.mean([r[nm]['inl500'] for r in rows]):6.1f}")
    logs = {json.loads(x)["pair_id"]: json.loads(x) for x in open(LOG_ROOT / "budget_val.jsonl")}
    rows = [r for r in rows if r["pair_id"] in logs]
    for est in ("sc2", "turbo"):
        fail = np.array([not logs[r["pair_id"]][est][-1]["ok15"] for r in rows])
        print(f"\n  AUROC for predicting full-budget {est} failure (n={len(rows)}, fail rate {fail.mean():.2f}):")
        base = {"stage0 inliers_all (current)": [logs[r["pair_id"]][est][0]["inliers_all"] for r in rows],
                "stage0 inliers (current)": [logs[r["pair_id"]][est][0]["inliers"] for r in rows]}
        for k in rows[0]["stats"]:
            base[k] = [r["stats"][k] for r in rows]
        for k, v in base.items():
            print(f"    {k:30s} {auroc(-np.asarray(v, float), fail):.3f}")


if __name__ == "__main__":
    main()
