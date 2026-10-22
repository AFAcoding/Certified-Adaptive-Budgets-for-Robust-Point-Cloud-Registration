"""Exploration (development pairs only; idle machine): where does the live time of CAB go, component by component?

Runs the live code path (live_budget.Controller.run) of CAB without the gate ("budgetc") and of the final method
("budgetc+v3") on the same 3DMatch development pairs, in alternating order, with every component wrapped in a timer:
the compatibility ordering, the gate's signals, the gate's prediction, each estimator stage, the trajectory /
feature construction and the controller's prediction per stage. Reports the mean time per pair of each component,
and the paired difference between the two methods on pairs with identical stopping decisions.

Usage: python -I scripts/explore/live_breakdown.py <dataset> <estimator> [n_pairs]
  dataset: v2_indoor_fpfh | v3_indoor_fpfh   (selection files of both methods must exist)
Writes results/explore/live_breakdown_<dataset>_<estimator>.json
"""

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import analyze_budget as B  # noqa: E402
import live_budget as L  # noqa: E402
from acpr import RESULTS_ROOT  # noqa: E402
from acpr import gate as G  # noqa: E402

T = defaultdict(float)  # component -> seconds, for the current run


def timed(name, fn):
    def w(*a, **k):
        t0 = time.perf_counter()
        try:
            return fn(*a, **k)
        finally:
            T[name] += time.perf_counter() - t0
    return w


class TimedModel:
    def __init__(self, m, name):
        self.m, self.name = m, name

    def predict_proba(self, X):
        t0 = time.perf_counter()
        try:
            return self.m.predict_proba(X)
        finally:
            T[self.name] += time.perf_counter() - t0


def main():
    ds_name, est = sys.argv[1], sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 80
    ds = L.make_dataset(ds_name)
    ctrls = {j: L.Controller(j, est, "extended", ds) for j in ("budgetc", "budgetc+v3")}
    for c in ctrls.values():
        c.clf_now = TimedModel(c.clf_now, "controller predict")
        if c.gate is not None and c.gate.clf is not None:
            c.gate.clf = TimedModel(c.gate.clf, "gate predict")
    # wrap the components used inside Controller.run
    L.compat_order = timed("ordering", L.compat_order)
    G.signals = timed("gate signals", G.signals)
    B.trajectory_ladder = timed("trajectory + features", B.trajectory_ladder)
    L.stage_record = timed("estimator stages (incl. stage record)", L.stage_record)
    fn, kw = L.FNS[est], ds.kwargs(est)
    pairs = ds.pairs("3DMatch")
    idx = sorted(np.random.default_rng(11).choice(len(pairs), n, replace=False).tolist())
    rows = []
    for j, i in enumerate(idx):
        p = pairs[i]
        rp, rf, sp, sf = ds.features_pair(p)
        P, Q, ratio = ds.corr(sp, sf, rp, rf)
        P, Q, ratio = P[:4000], Q[:4000], ratio[:4000]
        row = {}
        for job in (["budgetc", "budgetc+v3"] if j % 2 == 0 else ["budgetc+v3", "budgetc"]):
            T.clear()
            t0 = time.perf_counter()
            _, k = ctrls[job].run(fn, P, Q, ratio, None, p)
            total = time.perf_counter() - t0
            row[job] = {"total": total, "stop": k, **dict(T)}
        rows.append(row)
    out = {}
    for job in ("budgetc", "budgetc+v3"):
        comps = sorted({c for r in rows for c in r[job] if c not in ("stop",)})
        out[job] = {c: 1e3 * float(np.mean([r[job].get(c, 0.0) for r in rows])) for c in comps}
    same = [r for r in rows if r["budgetc"]["stop"] == r["budgetc+v3"]["stop"] and r["budgetc+v3"]["stop"] != -1]
    comps = sorted({c for r in same for j in r for c in r[j] if c != "stop"})
    out["same_stop_pairs"] = len(same)
    out["same_stop_median_diff_ms"] = {c: 1e3 * float(np.median([r["budgetc+v3"].get(c, 0.0) - r["budgetc"].get(c, 0.0)
                                                                  for r in same])) for c in comps}
    print(json.dumps(out, indent=1))
    (RESULTS_ROOT / "explore" / f"live_breakdown_{ds_name}_{est}.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
