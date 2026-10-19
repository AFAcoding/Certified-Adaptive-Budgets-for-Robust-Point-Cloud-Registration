"""Sensitivity of CAB to its two certification parameters: the risk level epsilon and the number of difficulty groups G.

For 3DMatch (tests: 3DMatch, 3DLoMatch) and KITTI (test: KITTI), compatibility order, group-conditional certificate:
for each setting, every candidate ladder is certified on the calibration pool (thresholds per group at delta/G; a
truncated ladder needs every group certified) and the cheapest certified ladder on the calibration pool is evaluated
once on test (offline speed-up, risk, recall loss).
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

DATA = {"3dmatch": ("train", "val", ["3DMatch", "3DLoMatch"]),
        "kitti": ("kitti_train", "kitti_val+kitti_calib", ["kitti_test"])}
SETTINGS = [(0.005, 3), (0.01, 3), (0.02, 3), (0.05, 3), (0.01, 1), (0.01, 2), (0.01, 4), (0.01, 5)]


def certify(trv, ref_ok, eps, n_groups, truncated):
    """Group-conditional thresholds; None if a truncated ladder leaves a group uncertified."""
    g = np.array([t[0]["log_inl_all"] for t in trv])
    edges = np.quantile(g, np.linspace(0, 1, n_groups + 1)[1:-1]) if n_groups > 1 else np.array([])
    gv = np.searchsorted(edges, g, side="right")
    lams = []
    for gi in range(n_groups):
        sub = [t for t, k in zip(trv, gv) if k == gi]
        items = [(lam, A.threshold_policy(sub, "p_now", lam)) for lam in B.LAMBDAS_P]
        idx, _ = A.ltt_select([p for p, _ in items], [o for _, o in items], ref_ok[gv == gi], eps, B.DELTA / n_groups)
        if idx is None and truncated:
            return None
        lams.append(items[idx][0] if idx is not None else 1.01)
    return {"edges": edges.tolist(), "lambdas": lams}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out = {}
    lines = ["# Sensitivity to the risk level epsilon and the number of difficulty groups G (compatibility order)\n",
             "| data | estimator | epsilon % | G | ladder | test | offline speed-up | risk % | loss [UB] pp |",
             "|---|---|---|---|---|---|---|---|---|"]
    for dname, (train, val, tests) in DATA.items():
        logs = {"train": B.load(train, "budgetc"), "val": B.load(val, "budgetc"), **{t: B.load(t, "budgetc") for t in tests}}
        for est in ("sc2", "turbo"):
            ref = S.full_ok(logs["val"], est)
            full = {t: A.fixed_stage([B.trajectory_ladder(r, est, (4,)) for r in logs[t]], 0) for t in tests}
            built = {ln: S.build(logs, est, lad) for ln, lad in B.LADDERS_EXT.items()}
            for eps, n_groups in SETTINGS:
                best = None
                for ln, (tr, _) in built.items():
                    param = certify(tr["val"], ref, eps, n_groups, truncated=B.LADDERS_EXT[ln][-1] != 4)
                    if param is None:
                        continue
                    o = S.mondrian_policy(tr["val"], np.array(param["edges"]), param["lambdas"]) if n_groups > 1 else \
                        A.threshold_policy(tr["val"], "p_now", param["lambdas"][0])
                    if best is None or o.s.mean() < best[2]:
                        best = (ln, param, o.s.mean())
                ln, param, _ = best
                tr = built[ln][0]
                for t in tests:
                    o = S.mondrian_policy(tr[t], np.array(param["edges"]), param["lambdas"]) if n_groups > 1 else \
                        A.threshold_policy(tr[t], "p_now", param["lambdas"][0])
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
