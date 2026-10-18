"""Design study 3 (validation only): anchor selection for compatibility-guided budgets.

Lesson of study 2 / the 100-anchor logs: mean top-k inlier yield is a misleading design
metric. With the 100 most distinctive correspondences as anchors, hard pairs have almost
no true anchors and the score promotes mutually consistent outliers. Candidates:
  deg1_m500      first-order degree against the top-500 (ratio) anchors
  deg2_m500      second-order degree against the top-500 anchors (outcomes from study 1)
  tp_s500        two-pass: anchors = top-100 by first-order degree WITHIN the top-500,
                 then second-order degree of all correspondences against those anchors
  tp2_s500       same, second-order degree within the top-500 to choose the anchors
  tp_s1000       same as tp_s500 with the top-1,000
Reports SC^2 / TurboReg success on the top-250 / top-500 (ratio from logs/budget_val.jsonl),
true anchors, and single-process ordering time.

Usage: python -I -u scripts/ordering_study_anchors.py [every=3] [workers=6]
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

from acpr import LOG_ROOT, RESULTS_ROOT  # noqa: E402
from acpr.data import load_pairs  # noqa: E402

N_ALL, KS, THR, N_ANCH = 4000, (250, 500), 0.10, 100


def compat(P, Q, rows, cols):
    D = cdist(P[rows], P[cols])
    D -= cdist(Q[rows], Q[cols])
    np.abs(D, out=D)
    return (D < THR).astype(np.float32)


def score_vs(P, Q, a, second):
    C = compat(P, Q, slice(None), a)
    if not second:
        return C.sum(1)
    return (C * (C @ C[a])).sum(1)


def order_variant(P, Q, name):
    n = P.shape[0]
    if name == "deg1_m500":
        a = np.arange(min(500, n))
        return np.argsort(-score_vs(P, Q, a, False), kind="stable"), a
    if name == "deg2_m500":
        a = np.arange(min(500, n))
        return np.argsort(-score_vs(P, Q, a, True), kind="stable"), a
    pool = np.arange(min(1000 if name == "tp_s1000" else 500, n))
    W = compat(P, Q, pool, pool)
    s = (W * (W @ W)).sum(1) if name == "tp2_s500" else W.sum(1)
    a = pool[np.argsort(-s, kind="stable")[:N_ANCH]]
    return np.argsort(-score_vs(P, Q, a, True), kind="stable"), a


VARIANTS = ["deg1_m500", "tp_s500", "tp2_s500", "tp_s1000"]


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
    out = {"pair_id": p.pair_id, "overlap": p.overlap, "gt_total": int(gt.sum()), "gt_top100": int(gt[:100].sum()),
           "gt_top500": int(gt[:500].sum())}
    for name in VARIANTS:
        o, a = order_variant(P, Q, name)
        res = {"anchors_true": int(gt[a].sum()), "anchors_n": int(len(a))}
        for k in KS:
            idx = o[:k]
            res[f"inl{k}"] = int(gt[idx].sum())
            for en, fn in [("sc2", sc2_pcr), ("turbo", turboreg)]:
                T, _ = fn(P[idx], Q[idx])
                rre, rte = rre_rte(p.transform, T)
                res[f"{en}{k}_ok"] = bool(rre <= 15 and rte <= 0.3)
        out[name] = res
    return out


def timing(n_pairs=20):
    """Single-process ordering time (ms), median over pairs."""
    from acpr.estimators import nn_correspondences
    from acpr.features import get_fpfh

    pairs = load_pairs("val")[::67][:n_pairs]
    t = {v: [] for v in VARIANTS + ["deg2_m500", "deg2_m100"]}
    for p in pairs:
        rp, rf, _ = get_fpfh(p.pcd0)
        sp, sf, _ = get_fpfh(p.pcd1)
        P, Q, _ = nn_correspondences(sp, sf, rp, rf)
        P, Q = P[:N_ALL], Q[:N_ALL]
        for v in t:
            reps = []
            for _ in range(3):
                t0 = time.perf_counter()
                if v == "deg2_m100":
                    score_vs(P, Q, np.arange(100), True)
                else:
                    order_variant(P, Q, v)
                reps.append(time.perf_counter() - t0)
            t[v].append(min(reps))
    return {v: 1e3 * float(np.median(x)) for v, x in t.items()}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    every = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    tm = timing()
    idx = list(range(0, len(load_pairs("val")), every))
    with ProcessPoolExecutor(workers) as ex:
        rows = list(ex.map(run, idx, chunksize=4))
    s1 = {r["pair_id"]: r for r in json.load(open(RESULTS_ROOT / "budget" / "ordering_study_val.json"))}
    logs = {r["pair_id"]: r for r in map(json.loads, open(LOG_ROOT / "budget_val.jsonl"))}
    c100 = {r["pair_id"]: r for r in map(json.loads, open(LOG_ROOT / "budgetc100_val.jsonl"))}
    for r in rows:
        r["deg2_m500"] = {k: v for k, v in s1[r["pair_id"]]["deg2"].items() if not k.endswith("_s")}
        r["ratio"] = {f"{e}{b}_ok": logs[r["pair_id"]][e][k]["ok15"] for e in ("sc2", "turbo") for k, b in enumerate(KS)}
        r["deg2_m100"] = {f"{e}{b}_ok": c100[r["pair_id"]][e][k]["ok15"] for e in ("sc2", "turbo") for k, b in enumerate(KS)}
        r["full"] = {e: logs[r["pair_id"]][e][4]["ok15"] for e in ("sc2", "turbo")}
    with open(RESULTS_ROOT / "budget" / "ordering_study_anchors_val.json", "w") as f:
        json.dump({"timing_ms": tm, "rows": rows}, f)
    print(f"validation pairs: {len(rows)} (every {every}th); true matches among the top-100 by ratio: "
          f"mean {np.mean([r['gt_top100'] for r in rows]):.1f}, zero for {100 * np.mean([r['gt_top100'] == 0 for r in rows]):.0f}% of pairs")
    full = {e: 100 * np.mean([r["full"][e] for r in rows]) for e in ("sc2", "turbo")}
    print(f"full budget (N=4000): SC2 {full['sc2']:.1f}%  TurboReg {full['turbo']:.1f}%")
    print("ordering     time(ms)  true anchors | SC2@250 SC2@500 | Turbo@250 Turbo@500")
    for v in ["ratio", "deg2_m100", "deg2_m500"] + VARIANTS:
        if v == "deg2_m500" and v in VARIANTS:
            continue
        ta = f"{np.mean([r[v]['anchors_true'] for r in rows]):5.1f}/{rows[0][v]['anchors_n']}" if "anchors_true" in rows[0][v] else "   -   "
        tt = tm.get(v, 0.0)
        acc = [100 * np.mean([r[v][f"{e}{b}_ok"] for r in rows]) for e in ("sc2", "turbo") for b in KS]
        print(f"  {v:10s} {tt:7.1f}   {ta:>10s}  | {acc[0]:6.1f}  {acc[1]:6.1f}  | {acc[2]:7.1f}  {acc[3]:7.1f}")


if __name__ == "__main__":
    main()
