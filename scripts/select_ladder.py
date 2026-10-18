"""Choose ladder + stopping policy on validation; evaluate on test against single full-budget runs.

Policy families (all certified on validation with Learn-then-Test, eps = 1 pp,
delta = 0.1, reference = the full-budget estimator):
  threshold   stop when P(current answer correct) >= lambda
  giveup      ... or when P(final answer correct) < gamma (one LTT sequence per gamma)
  mdp         Markov controller (stage x 5 x 3 confidence bins)
  mondrian    group-conditional certification: pairs are grouped by an observable
              after the first (cheap) budget (terciles of explained-correspondence count);
              each group gets its own threshold, certified on that group alone
              (Bonferroni over groups). Per-group risk <= eps implies overall
              risk <= eps for ANY mixture of groups, i.e. robustness to scene shift.

Usage: python -I scripts/select_ladder.py [--prefix budget|budgetc] [--ladders base|extended]
  (budgetc = compatibility-ordered budgets; outputs get the suffix _compat)
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_budget as B  # noqa: E402

from acpr import RESULTS_ROOT  # noqa: E402
from acpr import analysis as A  # noqa: E402

GAMMAS = [0.0, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3]
N_GROUPS = 3
BUDGETS = [250, 500, 1000, 2000, 4000]


def build(logs, est, ladder):
    tr = {s: [B.trajectory_ladder(r, est, ladder) for r in logs[s]] for s in logs}
    X, y = A.rows(tr["train"], B.FEATURES, "ok")
    clf_now = A.fit_classifier(X, y)
    clf_fin = A.fit_classifier(X, A.final_labels(tr["train"]))
    for s in tr:
        A.attach_scores(tr[s], B.FEATURES, clf_now, clf_fin)
    return tr, ({"mdp": A.MDPController(tr["train"])} if len(ladder) > 1 else {})


def full_ok(recs, est):
    """Outcome of the standard full-budget run (the reference for every ladder)."""
    return np.array([bool(r[est][4]["ok15"]) for r in recs])


def group_edges(tr_val):
    g = np.array([t[0]["log_inl_all"] for t in tr_val])
    return np.quantile(g, np.linspace(0, 1, N_GROUPS + 1)[1:-1])


def groups_of(trs, edges):
    return np.searchsorted(edges, np.array([t[0]["log_inl_all"] for t in trs]), side="right")


def mondrian_policy(trs, edges, lams):
    g = groups_of(trs, edges)
    stops = []
    for t, gi in zip(trs, g):
        lam = lams[gi]
        stops.append(next((st["stage"] for st in t if st["p_now"] >= lam), len(t) - 1))
    return A._from_stops(trs, stops)


def certify(tr, mdps, ref_ok, truncated=False):
    """Certify each family on validation against the FULL-budget run (ref_ok).

    For a ladder that ends below the full budget, stopping at its last stage is itself
    a risk, so the always-continue fallback must pass the test too (it is the first
    element of every fixed sequence); an uncertifiable group then voids the ladder.
    """
    ref = A.Outcome(ref_ok, ref_ok, None, None, None)
    res = {}

    def record(name, p, o):
        res[name] = {"param": p, "val_s": float(o.s.mean()), "val_rr": float(o.ok.mean()),
                     "val_risk": float(np.mean(ref.ok & ~o.ok))}

    items = [(l, A.threshold_policy(tr["val"], "p_now", l)) for l in B.LAMBDAS_P]
    idx, _ = A.ltt_select([p for p, _ in items], [o for _, o in items], ref.ok, B.EPS, B.DELTA)
    if idx is not None:
        record("threshold", *items[idx])
    for mname, m in mdps.items():
        items = [(l, m.policy(tr["val"], l)) for l in B.LAMBDAS_MDP]
        idx, _ = A.ltt_select([p for p, _ in items], [o for _, o in items], ref.ok, B.EPS, B.DELTA)
        if idx is not None:
            record(mname, *items[idx])
    best = None
    for g in GAMMAS:
        items = [((l, g), A.accept_or_giveup_policy(tr["val"], l, g)) for l in B.LAMBDAS_P]
        idx, _ = A.ltt_select([p for p, _ in items], [o for _, o in items], ref.ok, B.EPS, B.DELTA / len(GAMMAS))
        if idx is not None and (best is None or items[idx][1].s.mean() < best[1].s.mean()):
            best = items[idx]
    if best is not None:
        record("giveup", *best)
    # Mondrian: per-group certification (each group's risk measured on that group alone)
    edges = group_edges(tr["val"])
    gv = groups_of(tr["val"], edges)
    lams = []
    for gi in range(N_GROUPS):
        sub = [t for t, g in zip(tr["val"], gv) if g == gi]
        ref_g = ref.ok[gv == gi]
        items = [(l, A.threshold_policy(sub, "p_now", l)) for l in B.LAMBDAS_P]
        idx, _ = A.ltt_select([p for p, _ in items], [o for _, o in items], ref_g, B.EPS, B.DELTA / N_GROUPS)
        if idx is None and truncated:
            return res
        lams.append(items[idx][0] if idx is not None else 1.01)
    o = mondrian_policy(tr["val"], edges, lams)
    record("mondrian", {"edges": edges.tolist(), "lambdas": lams}, o)
    return res


def policy_outcome(tr_s, mdps, name, param):
    if name in mdps:
        return mdps[name].policy(tr_s, param)
    if name == "giveup":
        return A.accept_or_giveup_policy(tr_s, param[0], param[1])
    if name == "mondrian":
        return mondrian_policy(tr_s, np.array(param["edges"]), param["lambdas"])
    return A.threshold_policy(tr_s, "p_now", param)


def fmt(p):
    if isinstance(p, dict):
        return "λ per group = " + "/".join(f"{x:.3g}" for x in p["lambdas"])
    if isinstance(p, (tuple, list)):
        return ", ".join(f"{x:.3g}" for x in p)
    return f"{p:.4g}"


SUFFIX = {"budget": "", "budgetc": "_compat"}
# log names of the fitting / certification / test splits per dataset
DATASETS = {"3dmatch": {"train": "train", "val": "val", "tests": ["3DMatch", "3DLoMatch"]},
            "kitti": {"train": "kitti_train", "val": "kitti_val+kitti_calib", "tests": ["kitti_test"]},
            # FCGF re-certification: controller still fitted on FPFH training logs; thresholds certified on the
            # held-out (odd-indexed) FCGF test pairs; evaluated on the even-indexed ones
            "fcgf3dmatch": {"train": "train", "val": "fcgf_3DMatch_cal+fcgf_3DLoMatch_cal",
                            "tests": ["fcgf_3DMatch", "fcgf_3DLoMatch"]},
            "fcgfkitti": {"train": "kitti_train", "val": "fcgf_kitti_test_cal", "tests": ["fcgf_kitti_test"]},
            # FCGF re-fit + re-certification: controller fitted on a quarter of the held-out FCGF pool, certified on
            # the other three quarters (split_fcgf_cal.py); same even-indexed test pairs
            "fcgf3dmatch_refit": {"train": "fcgf_3DMatch_fit+fcgf_3DLoMatch_fit",
                                  "val": "fcgf_3DMatch_cert+fcgf_3DLoMatch_cert",
                                  "tests": ["fcgf_3DMatch", "fcgf_3DLoMatch"]}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="budget", choices=list(SUFFIX))
    ap.add_argument("--ladders", default="base", choices=["base", "extended"])
    ap.add_argument("--dataset", default="3dmatch", choices=list(DATASETS))
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    D = DATASETS[args.dataset]
    logs = {"train": B.load(D["train"], args.prefix), "val": B.load(D["val"], args.prefix),
            **{s: B.load(s, args.prefix) for s in D["tests"]}}
    ladders = B.LADDERS if args.ladders == "base" else B.LADDERS_EXT
    suffix = SUFFIX[args.prefix] + ("" if args.ladders == "base" else "_ext") + \
        ("" if args.dataset == "3dmatch" else f"_{args.dataset}")
    out = {}
    lines = ["# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation\n",
             "Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. "
             "Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).\n"]
    if args.prefix == "budgetc":
        lines.append("Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by "
                     "second-order compatibility with the 100 most distinctive ones; the reordering time is "
                     "charged to every configuration that truncates (adaptive and fixed), never to the full run.\n")
    for est, ename in [("sc2", "SC²-PCR"), ("turbo", "TurboReg")]:
        rows, built = [], {}
        for lname, ladder in ladders.items():
            tr, mdps = build(logs, est, ladder)
            built[lname] = (tr, mdps)
            for pname, c in certify(tr, mdps, full_ok(logs["val"], est), truncated=ladder[-1] != 4).items():
                rows.append({"ladder": lname, "policy": pname, **c})
        rows.sort(key=lambda x: x["val_s"])
        lines.append(f"\n## {ename}\n\nValidation, certified operating points (cheapest first):\n")
        lines.append("| ladder | policy | parameters | val RR % | val risk % | val mean time (ms) |")
        lines.append("|---|---|---|---|---|---|")
        for x in rows:
            lines.append(f"| {x['ladder']} | {x['policy']} | {fmt(x['param'])} | {100 * x['val_rr']:.1f} | "
                         f"{100 * x['val_risk']:.2f} | {1e3 * x['val_s']:.0f} |")
        # the full-budget-only ladder is always certified (zero risk), so both families have an operating point
        marg = [x for x in rows if x["policy"] != "mondrian"][0]
        mond = [x for x in rows if x["policy"] == "mondrian"][0]
        lines.append(f"\nSelected on validation: marginal = `{marg['ladder']}` / {marg['policy']}; "
                     f"group-conditional = `{mond['ladder']}` / mondrian.\n")
        out[est] = {"candidates": rows, "selected": {"marginal": marg, "mondrian": mond}, "test": {}}
        for s in D["tests"]:
            lines.append(f"\n### {ename}, {s} test ({len(logs[s])} pairs)\n")
            lines.append("| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | "
                         "speed-up vs full [95% CI] | McNemar p | risk % |")
            lines.append("|---|---|---|---|---|---|---|---|")
            full = A.fixed_stage([B.trajectory_ladder(r, est, (4,)) for r in logs[s]], 0)
            for tag, x in [("marginal", marg), ("mondrian", mond)]:
                tr, mdps = built[x["ladder"]]
                o = policy_outcome(tr[s], mdps, x["policy"], x["param"])
                cmp = B.paired(o, full, logs[s], B.MARGIN[s])
                risk = float(np.mean(full.ok & ~o.ok))
                lines.append(f"| {tag}: {x['ladder']} / {x['policy']} | {100 * o.ok.mean():.2f} | {1e3 * o.s.mean():.0f} | "
                             f"{100 * cmp['delta_rr']:+.2f} [{100 * cmp['ub95']:+.2f}] | {cmp['non_inferior']} | "
                             f"{cmp['speedup']:.2f}× [{cmp['speedup_ci'][0]:.2f}, {cmp['speedup_ci'][1]:.2f}] | "
                             f"{cmp['mcnemar_p']:.3g} | {100 * risk:.2f} |")
                stops = np.bincount(np.clip(o.stop, 0, None), minlength=len(ladders[x["ladder"]]))
                out[est]["test"].setdefault(s, {})[tag] = {"rr": float(o.ok.mean()), "s": float(o.s.mean()),
                                                           "risk": risk, **cmp,
                                                           "stop_hist": stops.tolist()}
            for k in range(5):
                fk = A.fixed_stage([B.trajectory_ladder(r, est, (k,)) for r in logs[s]], 0)
                lines.append(f"| fixed budget N={BUDGETS[k]} (single run) | {100 * fk.ok.mean():.2f} | "
                             f"{1e3 * fk.s.mean():.0f} | | | | | |")
            out[est]["test"][s]["full"] = {"rr": float(full.ok.mean()), "s": float(full.s.mean())}
    d = RESULTS_ROOT / "budget"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"ladder_selection{suffix}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    with open(d / f"ladder_selection{suffix}.json", "w") as f:
        json.dump(out, f, indent=1, default=float)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
