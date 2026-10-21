"""Sensitivity of CAB to its two certification parameters: the risk level epsilon and the number of difficulty groups G.

For 3DMatch (tests: 3DMatch, 3DLoMatch) and KITTI (test: KITTI), compatibility order, group-conditional certificate:
for each setting, the ladder is chosen on the fitting pairs and only it is certified on the calibration pool
(thresholds per group at delta/G; select_ladder.select_and_certify), then evaluated once on test (offline speed-up,
risk, recall loss).
  epsilon in {0.5, 1, 2, 5} % with G = 3;  G in {1, 2, 3, 4, 5} with epsilon = 1 % (G = 1 is a marginal threshold).

Writes results/budget/sensitivity.{json,md}.
Usage: python -I scripts/sensitivity.py
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_budget as B  # noqa: E402
import select_ladder as S  # noqa: E402

from acpr import RESULTS_ROOT  # noqa: E402
from acpr import analysis as A  # noqa: E402

# protocol v2 (PROTOCOL.md); evaluated on the development benchmarks only, never on the blind tests
DATA = {"3dmatch": ("v2_fit", "v2_cal", ["3DMatch", "3DLoMatch"]),
        "kitti": ("kitti_train", "kitti_val+kitti_calib", ["kitti_test"])}
SETTINGS = [(0.005, 3), (0.01, 3), (0.02, 3), (0.05, 3), (0.01, 1), (0.01, 2), (0.01, 4), (0.01, 5)]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out = {}
    lines = ["# Sensitivity to the risk level epsilon and the number of difficulty groups G (compatibility order)\n",
             "| data | estimator | epsilon % | G | ladder | test | offline speed-up | risk % | loss [UB] pp |",
             "|---|---|---|---|---|---|---|---|---|"]
    for dname, (train, val, tests) in DATA.items():
        logs = {"train": B.load(train, "budgetc"), "val": B.load(val, "budgetc"), **{t: B.load(t, "budgetc") for t in tests}}
        for est in ("sc2", "turbo"):
            full = {t: A.fixed_stage([B.trajectory_ladder(r, est, (4,)) for r in logs[t]], 0) for t in tests}
            for eps, n_groups in SETTINGS:
                # chosen on the fitting pairs, certified on the calibration pool (as in select_ladder.py)
                sel, _, built = S.select_and_certify(logs, est, eps=eps, n_groups=n_groups, families=("mondrian",))
                x, (tr, mdps) = sel["mondrian"], built["mondrian"]
                ln, param = x["ladder"], x["param"]
                for t in tests:
                    o = S.policy_outcome(tr[t], mdps, x["policy"], param)
                    cmp = B.paired(o, full[t], logs[t], B.MARGIN[t])
                    res = {"ladder": ln, "lambdas": param["lambdas"], "risk": float(np.mean(full[t].ok & ~o.ok)), **cmp}
                    out.setdefault(dname, {}).setdefault(est, {}).setdefault(t, {})[f"{eps}_{n_groups}"] = res
                    lines.append(f"| {dname} | {est} | {100 * eps:g} | {n_groups} | {ln} | {t} | {cmp['speedup']:.2f}× | "
                                 f"{100 * res['risk']:.2f} | {100 * cmp['delta_rr']:.2f} [{100 * cmp['ub95']:.2f}] |")
                print(f"  {dname} {est} eps={eps} G={n_groups}: {ln}", flush=True)
    (RESULTS_ROOT / "budget" / "sensitivity.json").write_text(json.dumps(out, indent=1, default=float))
    (RESULTS_ROOT / "budget" / "sensitivity.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
