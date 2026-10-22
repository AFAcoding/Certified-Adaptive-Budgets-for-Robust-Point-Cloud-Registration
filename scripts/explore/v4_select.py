"""Exploration: apply the pre-specified selection rule to the factorial study (scripts/explore/run_v4_factorial.sh).

Rule (written before any factorial result existed, 2026-10-22):
  score = out-of-fold mean cost of the chosen candidate on the fitting pairs (fit_s), times (1 - gate saving) for the
  gate-on variant, where the gate saving is its out-of-fold saving on the fitting + calibration pairs;
  candidates within one standard error (fit_s_se) of the best score are tied, and among them the simplest wins:
  fewest extra signals (base 0 < verify 4 < geom 5 < both 9), then classifier logit < poly2 < hgb, then gate off.
Development benchmarks are reported for every configuration but never used to choose.

Usage: python -I scripts/explore/v4_select.py
Writes results/explore/v4_selection.md
"""

import json

from acpr import RESULTS_ROOT

FSETS = {"base": 0, "verify": 4, "geom": 5, "both": 9}
CLFS = {"logit": 0, "poly2": 1, "hgb": 2}


def main():
    ex = RESULTS_ROOT / "explore"
    L = ["# v4 factorial: pre-specified selection (fitting-pair cost, 1-SE rule, simplest wins)\n"]
    for est in ("sc2", "turbo"):
        rows = []
        for f in FSETS:
            for c in CLFS:
                p = ex / f"controller_features_{f}_{est}_{c}.json"
                if not p.exists():
                    continue
                r = json.loads(p.read_text())
                for gate in (False, True):
                    sav = r["gate"]["fitcal_saving"] if gate and r["gate"]["kind"] else 0.0
                    rows.append({"f": f, "c": c, "gate": gate, "score": r["fit_s"] * (1 - sav),
                                 "se": r.get("fit_s_se") or 0.0, "ladder": r["ladder"],
                                 "dev": r["test_gate" if gate else "test"]})
        if not rows:
            continue
        best = min(rows, key=lambda x: x["score"])
        tied = [x for x in rows if x["score"] <= best["score"] + best["se"]]
        win = min(tied, key=lambda x: (FSETS[x["f"]], CLFS[x["c"]], x["gate"]))
        L.append(f"\n## {est}: winner {win['f']} / {win['c']} / gate {'on' if win['gate'] else 'off'} "
                 f"(best score {1e3 * best['score']:.0f} ms ± {1e3 * best['se']:.0f}; {len(tied)} tied)\n")
        L.append("| signals | classifier | gate | fit score (ms) | ladder | 3DMatch speed (risk %) | 3DLoMatch speed (risk %) | NI |")
        L.append("|---|---|---|---|---|---|---|---|")
        for x in sorted(rows, key=lambda x: x["score"]):
            d = x["dev"]
            ni = all(v["non_inferior"] for v in d.values())
            mark = " **(winner)**" if x is win else (" (tied)" if x in tied else "")
            L.append(f"| {x['f']}{mark} | {x['c']} | {'on' if x['gate'] else 'off'} | {1e3 * x['score']:.0f} | "
                     f"{x['ladder']} | {d['3DMatch']['speedup']:.2f} ({100 * d['3DMatch']['risk']:.2f}) | "
                     f"{d['3DLoMatch']['speedup']:.2f} ({100 * d['3DLoMatch']['risk']:.2f}) | {ni} |")
    (ex / "v4_selection.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
