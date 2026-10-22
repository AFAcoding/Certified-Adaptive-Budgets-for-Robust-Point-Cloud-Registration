"""Exploration (development pairs only; run on an otherwise idle machine): where does the live overhead of the v3
gate come from (~40 ms per pair on the v3 blind test, against ~3 ms in an isolated microbenchmark)?

Times on the same 3DMatch development pairs, in rotating order, with the live code path (live_budget.Controller):
  v2       CAB without the gate (compatibility order)
  v3       CAB v3 as timed in the paper (gate + classifier chosen on the fitting pairs)
  v3_1thr  CAB v3 with scikit-learn's OpenMP pool limited to one thread around every prediction
           (threadpoolctl); identical decisions, only the threading of the predictions changes
and reports the mean time per pair of each, and the paired difference on pairs with identical stops.

Usage: python -I scripts/explore/gate_overhead.py [n_pairs] [estimator]
Writes results/explore/gate_overhead_<estimator>.json
"""

import json
import sys
import time
from pathlib import Path

import numpy as np
from threadpoolctl import threadpool_limits

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import live_budget as L  # noqa: E402
from acpr import RESULTS_ROOT  # noqa: E402


class OneThread:
    """Wraps a fitted model: predictions run with the OpenMP pool limited to one thread."""

    def __init__(self, m):
        self.m = m

    def predict_proba(self, X):
        with threadpool_limits(limits=1, user_api="openmp"):
            return self.m.predict_proba(X)

    def predict(self, X):
        with threadpool_limits(limits=1, user_api="openmp"):
            return self.m.predict(X)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    est = sys.argv[2] if len(sys.argv) > 2 else "sc2"
    ds = L.make_dataset("v2_indoor_fpfh")
    ctrls = {"v2": L.Controller("budgetc", est, "extended", ds), "v3": L.Controller("budgetc+v3", est, "extended", ds),
             "v3_1thr": L.Controller("budgetc+v3", est, "extended", ds)}
    c = ctrls["v3_1thr"]
    c.clf_now = OneThread(c.clf_now)
    if c.gate is not None and c.gate.clf is not None:
        c.gate.clf = OneThread(c.gate.clf)
    pairs = ds.pairs("3DMatch")
    idx = sorted(np.random.default_rng(7).choice(len(pairs), n, replace=False).tolist())
    fn, kw = L.FNS[est], ds.kwargs(est)
    jobs = list(ctrls)
    rows = []
    for j, i in enumerate(idx):
        p = pairs[i]
        rp, rf, sp, sf = ds.features_pair(p)
        P, Q, ratio = ds.corr(sp, sf, rp, rf)
        P, Q, ratio = P[:4000], Q[:4000], ratio[:4000]
        order = jobs[j % 3:] + jobs[: j % 3]
        row = {}
        for job in order:
            t0 = time.perf_counter()
            _, k = ctrls[job].run(fn, P, Q, ratio, None, p)
            row[job] = (time.perf_counter() - t0, k)
        rows.append(row)
    res = {job: 1e3 * float(np.mean([r[job][0] for r in rows])) for job in jobs}
    for a, b in (("v2", "v3"), ("v2", "v3_1thr"), ("v3", "v3_1thr")):
        same = [r for r in rows if r[a][1] == r[b][1] and r[b][1] != -1]
        d = np.array([1e3 * (r[b][0] - r[a][0]) for r in same])
        res[f"{b}-{a} same-stop median ms"] = float(np.median(d)) if len(d) else None
        res[f"{b}-{a} same-stop n"] = len(d)
    print(json.dumps(res, indent=1))
    (RESULTS_ROOT / "explore" / f"gate_overhead_{est}.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
