"""Exploration (development pairs only; idle machine): is part of the gate's live overhead an artifact of the timing
harness?

live_budget.time_pair computes, between timed runs, an untimed "offline stop" for each adaptive job; for the final
method that includes a prediction of the gate's boosted-tree classifier. Here the exact five-job protocol of the
fresh blind test (full, budget, budgetc, budget+v3, budgetc+v3, rotating order) is run on 3DMatch development pairs
twice per pair:
  interleaved  as in live_budget.time_pair (offline stops between timed runs)
  deferred     the same timed runs, with every offline stop computed after all of them
Reports the median paired overhead of budgetc+v3 over budgetc on pairs with identical stops, and the speed-ups.

Usage: python -I scripts/explore/harness_check.py [n_pairs] [estimator]
Writes results/explore/harness_check_<estimator>.json
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import analyze_budget as B  # noqa: E402
import live_budget as L  # noqa: E402
from acpr import RESULTS_ROOT  # noqa: E402

JOBS = ["full", "budget", "budgetc", "budget+v3", "budgetc+v3"]


def run_pair(ds, est, ctrls, p, jobs, offline, deferred):
    fn, kw = L.FNS[est], ds.kwargs(est)
    rp, rf, sp, sf = ds.features_pair(p)
    P, Q, ratio = ds.corr(sp, sf, rp, rf)
    P, Q, ratio = P[:4000], Q[:4000], ratio[:4000]
    out, pending = {}, []
    for job in jobs:
        t0 = time.perf_counter()
        if job == "full":
            fn(P, Q, **kw)
            stop = None
        else:
            _, stop = ctrls[job].run(fn, P, Q, ratio, None, p)
        out[job] = {"s": time.perf_counter() - t0, "stop": stop}
        if job != "full":
            if deferred:
                pending.append(job)
            else:
                out[job]["offline_stop"] = ctrls[job].offline_stop(offline[job][p.pair_id], "3DMatch")
    for job in pending:
        out[job]["offline_stop"] = ctrls[job].offline_stop(offline[job][p.pair_id], "3DMatch")
    return out


def summarise(rows):
    tf = np.mean([r["full"]["s"] for r in rows])
    same = [r for r in rows if r["budgetc"]["stop"] == r["budgetc+v3"]["stop"] and r["budgetc+v3"]["stop"] != -1]
    return {"speed": {j: float(tf / np.mean([r[j]["s"] for r in rows])) for j in JOBS[1:]},
            "same_stop_n": len(same),
            "overhead_ms_median": float(1e3 * np.median([r["budgetc+v3"]["s"] - r["budgetc"]["s"] for r in same]))}


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    est = sys.argv[2] if len(sys.argv) > 2 else "sc2"
    ds = L.make_dataset("v3_indoor_fpfh")
    ctrls = {j: L.Controller(j, est, "extended", ds) for j in JOBS[1:]}
    offline = {j: {r["pair_id"]: r for r in B.load("3DMatch", j.split("+")[0])} for j in JOBS[1:]}
    pairs = [p for p in ds.pairs("3DMatch") if p.pair_id in offline["budgetc"]]
    idx = sorted(np.random.default_rng(13).choice(len(pairs), n, replace=False).tolist())
    rows = {"interleaved": [], "deferred": []}
    for j, i in enumerate(idx):
        jobs = JOBS[j % 5:] + JOBS[: j % 5]  # the rotation of live_budget.main
        for mode in (("interleaved", "deferred") if j % 2 == 0 else ("deferred", "interleaved")):
            rows[mode].append(run_pair(ds, est, ctrls, pairs[i], jobs, offline, mode == "deferred"))
    res = {mode: summarise(r) for mode, r in rows.items()}
    print(json.dumps(res, indent=1))
    (RESULTS_ROOT / "explore" / f"harness_check_{est}.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
