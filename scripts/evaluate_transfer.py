"""Transfer to learned descriptors: apply the configurations selected and certified on FPFH validation,
unchanged, to the FCGF test logs (only FCGF test sets are released).

For every estimator, ordering and certificate: the ladder and parameters of
results/budget/ladder_selection{_compat}_ext{,_kitti}.json, the controller fitted on the FPFH training
logs, evaluated once on logs/budget{c}_fcgf_<set>.jsonl against the FCGF full budget.
Writes results/budget/transfer_fcgf.{json,md}.

Usage: python -I scripts/evaluate_transfer.py
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

TARGETS = [("fcgf_3DMatch", "3dmatch", 0.01), ("fcgf_3DLoMatch", "3dmatch", 0.02), ("fcgf_kitti_test", "kitti", 0.01)]
FIT = {"3dmatch": ("train", "val", ""), "kitti": ("kitti_train", "kitti_val+kitti_calib", "_kitti")}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out, lines = {}, ["# Transfer to FCGF descriptors (configurations certified on FPFH validation)\n",
                      "| set | estimator | order | certificate | ladder | RR % | full RR % | loss [UB] pp | non-inferior | "
                      "speed-up [95% CI] | risk % |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for subset, fam, margin in TARGETS:
        train, val, suffix = FIT[fam]
        for order, prefix in (("ratio", "budget"), ("compat", "budgetc")):
            recs = B.load(subset, prefix)
            if not recs:
                continue
            sel = json.loads((RESULTS_ROOT / "budget" / f"ladder_selection{S.SUFFIX[prefix]}_ext{suffix}.json").read_text())
            logs = {"train": B.load(train, prefix), "val": B.load(val, prefix), subset: recs}
            for est in ("sc2", "turbo"):
                full = A.fixed_stage([B.trajectory_ladder(r, est, (4,)) for r in recs], 0)
                for tag in ("mondrian", "marginal"):
                    x = sel[est]["selected"][tag]
                    tr, mdps = S.build(logs, est, B.LADDERS_EXT[x["ladder"]])
                    o = S.policy_outcome(tr[subset], mdps, x["policy"], x["param"])
                    cmp = B.paired(o, full, recs, margin)
                    risk = float(np.mean(full.ok & ~o.ok))
                    res = {"ladder": x["ladder"], "policy": x["policy"], "rr": float(o.ok.mean()), "full_rr": float(full.ok.mean()),
                           "s": float(o.s.mean()), "full_s": float(full.s.mean()), "risk": risk, "n": len(recs), **cmp}
                    out.setdefault(subset, {}).setdefault(est, {}).setdefault(order, {})[tag] = res
                    lines.append(f"| {subset} | {est} | {order} | {tag} | {x['ladder']} | {100 * res['rr']:.2f} | "
                                 f"{100 * res['full_rr']:.2f} | {100 * cmp['delta_rr']:.2f} [{100 * cmp['ub95']:.2f}] | "
                                 f"{cmp['non_inferior']} | {cmp['speedup']:.2f}× [{cmp['speedup_ci'][0]:.2f}, "
                                 f"{cmp['speedup_ci'][1]:.2f}] | {100 * risk:.2f} |")
    with open(RESULTS_ROOT / "budget" / "transfer_fcgf.json", "w") as f:
        json.dump(out, f, indent=1, default=float)
    (RESULTS_ROOT / "budget" / "transfer_fcgf.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
