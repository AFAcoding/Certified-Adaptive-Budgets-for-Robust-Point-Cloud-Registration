"""Scene-disjoint FCGF evaluation by cross-fitting over scenes.

The main FCGF protocol fits and certifies on held-out pairs of the *same* scenes as the test pairs (only test features
are released). Here every scene is held out in turn: for each fold, the controller is fitted and certified on pairs of
the other scenes only (fitting: every third pair, certification: the rest) and evaluated on the held-out scenes, so
calibration and test never share a scene. Every pair is tested exactly once; outcomes are pooled over the folds.

Pools (all FCGF pairs: the even-indexed test logs plus the odd-indexed held-out logs):
  3DMatch + 3DLoMatch: 8 scenes, 4 folds of 2 scenes; results reported per test set
  KITTI: sequences 08, 09, 10, 3 folds (one sequence each)

Writes results/budget/fcgf_scene_disjoint.{json,md}.
Usage: python -I scripts/fcgf_scene_disjoint.py
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

PREFIXES = {"ratio": "budget", "compat": "budgetc"}
POOLS = {"indoor": (["fcgf_3DMatch", "fcgf_3DLoMatch"], 4), "kitti": (["fcgf_kitti_test"], 3)}


def load_pool(sets, prefix):
    recs = []
    for s in sets:
        recs += B.load(s, prefix) + B.load(f"{s}_cal", prefix)
    return recs


def select(logs, est):
    """Certified selection on logs['val'] as in select_ladder.py: cheapest certified point per family."""
    rows, built = [], {}
    for lname, ladder in B.LADDERS_EXT.items():
        tr, mdps = S.build(logs, est, ladder)
        built[lname] = (tr, mdps)
        for pname, c in S.certify(tr, mdps, S.full_ok(logs["val"], est), truncated=ladder[-1] != 4).items():
            rows.append({"ladder": lname, "policy": pname, **c})
    rows.sort(key=lambda x: x["val_s"])
    # the full budget is the reference itself (zero risk by definition): with too few calibration pairs to certify
    # anything, not even the never-stop rule, it is the fallback
    marg = next((x for x in rows if x["policy"] != "mondrian"),
                {"ladder": "full", "policy": "threshold", "param": 1.01, "fallback": True})
    mond = next((x for x in rows if x["policy"] == "mondrian"),
                {"ladder": "full", "policy": "mondrian", "fallback": True,
                 "param": {"edges": [0.0] * (S.N_GROUPS - 1), "lambdas": [1.01] * S.N_GROUPS}})
    return {"marginal": marg, "mondrian": mond}, built


def concat(outs):
    return A.Outcome(*[np.concatenate([getattr(o, f) for o in outs]) for f in ("ok", "ok15", "ce", "s", "stop")])


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out, lines = {}, ["# Scene-disjoint FCGF evaluation (cross-fitting over scenes)\n",
                      "Controller fitted and certified on the other scenes only; every pair tested once; pooled over folds.\n",
                      "| test set | estimator | order | certificate | folds: ladder | RR % | full RR % | loss [UB] pp | "
                      "non-inferior | offline speed-up [95% CI] | risk % |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for pool, (sets, n_folds) in POOLS.items():
        for order, prefix in PREFIXES.items():
            recs = load_pool(sets, prefix)
            scenes = sorted({r["scene"] for r in recs})
            folds = [scenes[i::n_folds] for i in range(n_folds)]
            for est in ("sc2", "turbo"):
                per = {tag: {"o": [], "full": [], "recs": [], "ladders": []} for tag in ("marginal", "mondrian")}
                for k, test_scenes in enumerate(folds):
                    test = [r for r in recs if r["scene"] in test_scenes]
                    rest = [r for r in recs if r["scene"] not in test_scenes]
                    logs = {"train": rest[0::3], "val": [r for i, r in enumerate(rest) if i % 3], "test": test}
                    sel, built = select(logs, est)
                    full = A.fixed_stage([B.trajectory_ladder(r, est, (4,)) for r in test], 0)
                    for tag, x in sel.items():
                        tr, mdps = built[x["ladder"]]
                        per[tag]["o"].append(S.policy_outcome(tr["test"], mdps, x["policy"], x["param"]))
                        per[tag]["full"].append(full)
                        per[tag]["recs"].append(test)
                        per[tag]["ladders"].append(x["ladder"])
                    print(f"  {pool} {order} {est} fold {k}: {[sel[t]['ladder'] for t in sel]}", flush=True)
                for tag, p in per.items():
                    o, full = concat(p["o"]), concat(p["full"])
                    trecs = [r for rs in p["recs"] for r in rs]
                    for s in sets:  # report per test set (3DMatch and 3DLoMatch share the indoor folds)
                        m = np.array([r["subset"] == s for r in trecs])
                        if not m.any():
                            continue
                        sub = lambda oc: A.Outcome(*[getattr(oc, f)[m] for f in ("ok", "ok15", "ce", "s", "stop")])  # noqa: E731
                        rs = [r for r, keep in zip(trecs, m) if keep]
                        cmp = B.paired(sub(o), sub(full), rs, B.MARGIN.get(s, 0.01))
                        risk = float(np.mean(sub(full).ok & ~sub(o).ok))
                        res = {"rr": float(sub(o).ok.mean()), "full_rr": float(sub(full).ok.mean()), "risk": risk,
                               "n": int(m.sum()), "ladders": p["ladders"], **cmp}
                        out.setdefault(s, {}).setdefault(est, {}).setdefault(order, {})[tag] = res
                        lines.append(f"| {s} | {est} | {order} | {tag} | {'/'.join(p['ladders'])} | {100 * res['rr']:.2f} | "
                                     f"{100 * res['full_rr']:.2f} | {100 * cmp['delta_rr']:.2f} [{100 * cmp['ub95']:.2f}] | "
                                     f"{cmp['non_inferior']} | {cmp['speedup']:.2f}× [{cmp['speedup_ci'][0]:.2f}, "
                                     f"{cmp['speedup_ci'][1]:.2f}] | {100 * risk:.2f} |")
    (RESULTS_ROOT / "budget" / "fcgf_scene_disjoint.json").write_text(json.dumps(out, indent=1, default=float))
    (RESULTS_ROOT / "budget" / "fcgf_scene_disjoint.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
