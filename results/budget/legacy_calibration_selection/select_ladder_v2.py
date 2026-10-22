"""Choose ladder + stopping policy on the fitting pairs, certify it on the calibration pairs, evaluate on test.

Policy families (reference = the full-budget estimator; risk = share of pairs it registers but the policy does not):
  threshold   stop when P(current answer correct) >= lambda
  giveup      ... or when P(final answer correct) < gamma
  mdp         Markov controller (stage x 5 x 3 confidence bins)
  mondrian    group-conditional certification: pairs are grouped by an observable
              after the first (cheap) budget (terciles of explained-correspondence count on the fitting pairs);
              each group gets its own threshold, certified on that group alone
              (Bonferroni over groups). Per-group risk <= eps implies overall
              risk <= eps for ANY mixture of groups, i.e. robustness to scene shift.

Selection and certification are separated so that the guarantee holds for the configuration actually used:
  1. choose: every candidate (ladder, family) is scored on the fitting pairs only, with out-of-fold controller
     scores (K-fold cross-fitting); its operating point is the most aggressive parameter of its fixed sequence whose
     loss share stays within what the certificate can accept for the calibration set's size. The cheapest
     candidate is kept (the full budget alone is always a candidate).
  2. certify: only the chosen candidate is certified on the calibration pairs with Learn-then-Test (exact binomial
     test, fixed-sequence testing, eps = 1 %, delta = 0.1; delta / G per group). Choosing among several candidates
     certified on the same calibration pairs would void the guarantee (the cheapest of them is the most likely
     to have been certified by luck).

Usage: python -I scripts/select_ladder.py [--prefix budget|budgetc] [--ladders base|extended]
  (budgetc = compatibility-ordered budgets; outputs get the suffix _compat)
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import binom

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_budget as B  # noqa: E402

from acpr import RESULTS_ROOT  # noqa: E402
from acpr import analysis as A  # noqa: E402

GAMMAS = [0.0, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3]
N_GROUPS = 3
K_FOLDS = 5
BUDGETS = [250, 500, 1000, 2000, 4000]
FAMILIES = ("threshold", "mdp", "giveup")  # marginal certificate; "mondrian" is the group-conditional one


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


def group_edges(trs, n_groups=N_GROUPS):
    """Quantile edges of the first-stage observable; computed on the fitting pairs, never on calibration pairs."""
    g = np.array([t[0]["log_inl_all"] for t in trs])
    return np.quantile(g, np.linspace(0, 1, n_groups + 1)[1:-1])


def groups_of(trs, edges):
    return np.searchsorted(edges, np.array([t[0]["log_inl_all"] for t in trs]), side="right")


def mondrian_policy(trs, edges, lams):
    g = groups_of(trs, edges)
    stops = []
    for t, gi in zip(trs, g):
        lam = lams[gi]
        stops.append(next((st["stage"] for st in t if st["p_now"] >= lam), len(t) - 1))
    return A._from_stops(trs, stops)


def tolerance(n, eps, delta):
    """Largest loss share that the exact binomial test certifies on n calibration pairs at level delta, or None when
    even zero losses are not enough (n < log(delta) / log(1 - eps))."""
    k = -1
    while n > 0 and binom.cdf(k + 1, n, eps) <= delta:
        k += 1
    return None if k < 0 else k / n


def full_choice(family, n_groups=N_GROUPS):
    """The standard estimator itself (zero risk by definition): the fallback when nothing cheaper is certifiable."""
    if family == "mondrian":
        return {"ladder": "full", "policy": "mondrian",
                "param": {"edges": [0.0] * (n_groups - 1), "lambdas": [1.01] * n_groups}}
    return {"ladder": "full", "policy": "threshold", "param": 1.01}


_CROSSFIT = {}


def crossfit(recs, est, ladder, k=K_FOLDS, seed=0):
    """Out-of-fold trajectories of the fitting pairs: fold f is scored by a controller (classifiers and, for ladders
    with several stages, the Markov model) fitted on the other folds, as the calibration pairs are later scored.
    Cached per fitting set (the policies only read the trajectories)."""
    key = (id(recs), est, tuple(ladder), k, seed)
    if key not in _CROSSFIT or _CROSSFIT[key][0] is not recs:  # the entry keeps recs alive, so its id is not reused
        _CROSSFIT[key] = (recs, _crossfit(recs, est, ladder, k, seed))
    return _CROSSFIT[key][1]


def _crossfit(recs, est, ladder, k, seed):
    fold = np.random.default_rng(seed).permutation(len(recs)) % k
    held, mdp_of = [None] * len(recs), []
    for f in range(k):
        idx = np.flatnonzero(fold == f)
        tr, mdps = build({"train": [r for r, g in zip(recs, fold) if g != f], "held": [recs[i] for i in idx]},
                         est, ladder)
        for i, t in zip(idx, tr["held"]):
            held[i] = t
        mdp_of.append((idx, mdps.get("mdp")))
    return held, mdp_of


def _mdp_outcome(held, mdp_of, lam):
    stops = np.zeros(len(held), dtype=int)
    for idx, m in mdp_of:
        stops[idx] = m.policy([held[i] for i in idx], lam).stop
    return A._from_stops(held, stops)


def _within(outcomes, ref_ok, tol):
    """Fixed sequence on the fitting pairs: index of the last parameter before the first loss share above tol."""
    idx = None
    for i, o in enumerate(outcomes):
        if np.mean(ref_ok & ~o.ok) > tol + 1e-12:
            break
        idx = i
    return idx


def fit_candidates(recs, est, ladders, n_cal, eps=B.EPS, n_groups=N_GROUPS, families=FAMILIES + ("mondrian",)):
    """Step 1 (choose): the operating point and cost of every candidate on the fitting pairs alone.

    The loss tolerance matches what the certificate can accept for the calibration set's size (zero losses for
    the group-conditional certificate with our pool sizes); only that size, never a calibration pair, is used."""
    tol_m = tolerance(n_cal, eps, B.DELTA)
    tol_g = tolerance(n_cal // n_groups, eps, B.DELTA / n_groups)
    ref = full_ok(recs, est)
    rows = []
    for lname, ladder in ladders.items():
        truncated = ladder[-1] != 4
        held, mdp_of = crossfit(recs, est, ladder)

        def add(policy, param, o):
            rows.append({"ladder": lname, "policy": policy, "fit_param": param, "fit_s": float(o.s.mean()),
                         "fit_risk": float(np.mean(ref & ~o.ok))})

        if lname == "full":  # the standard estimator: zero risk, needs no certificate
            o = A.fixed_stage(held, 0)
            if set(families) - {"mondrian"}:
                add("threshold", 1.01, o)
            if "mondrian" in families:
                add("mondrian", None, o)
            continue
        if tol_m is not None:
            if "threshold" in families:
                outs = [A.threshold_policy(held, "p_now", l) for l in B.LAMBDAS_P]
                i = _within(outs, ref, tol_m)
                if i is not None:
                    add("threshold", B.LAMBDAS_P[i], outs[i])
            if "mdp" in families and mdp_of[0][1] is not None:
                outs = [_mdp_outcome(held, mdp_of, l) for l in B.LAMBDAS_MDP]
                i = _within(outs, ref, tol_m)
                if i is not None:
                    add("mdp", float(B.LAMBDAS_MDP[i]), outs[i])
            if "giveup" in families:
                best = None
                for g in GAMMAS:
                    outs = [A.accept_or_giveup_policy(held, l, g) for l in B.LAMBDAS_P]
                    i = _within(outs, ref, tol_m)
                    if i is not None and (best is None or outs[i].s.mean() < best[1].s.mean()):
                        best = ((B.LAMBDAS_P[i], g), outs[i])
                if best is not None:
                    add("giveup", *best)
        if "mondrian" in families:
            edges = group_edges(held, n_groups)
            gv = groups_of(held, edges)
            lams = []
            for gi in range(n_groups):
                sub = [t for t, g in zip(held, gv) if g == gi]
                outs = [A.threshold_policy(sub, "p_now", l) for l in B.LAMBDAS_P]
                i = _within(outs, ref[gv == gi], tol_g) if tol_g is not None and sub else None
                lams.append(B.LAMBDAS_P[i] if i is not None else None)
            if truncated and None in lams:
                continue
            lams = [1.01 if x is None else x for x in lams]
            add("mondrian", {"edges": edges.tolist(), "lambdas": lams}, mondrian_policy(held, edges, lams))
    return rows


def choose(rows, family):
    """The cheapest candidate on the fitting pairs: group-conditional (family='mondrian') or marginal (any other)."""
    pool = [x for x in rows if (x["policy"] == "mondrian") == (family == "mondrian")]
    return min(pool, key=lambda x: x["fit_s"])


def certify_choice(logs, est, choice, eps=B.EPS, n_groups=N_GROUPS):
    """Step 2 (certify): Learn-then-Test of the chosen candidate alone on logs['val'] against the full budget.

    A ladder ending below the full budget is risky even when it never stops early, so its always-continue
    parameter is the first element of every fixed sequence; if it is not certified (in some group), the
    candidate falls back to the full budget. Returns the certified configuration and the built controller."""
    lname, policy = choice["ladder"], choice["policy"]
    ladder = B.LADDERS_EXT[lname]
    tr, mdps = build(logs, est, ladder)
    ref = full_ok(logs["val"], est)
    truncated = ladder[-1] != 4
    fallback = {**full_choice("mondrian" if policy == "mondrian" else "threshold", n_groups),
                "fit_s": choice.get("fit_s"), "chosen": choice.get("chosen", choice), "fallback": True}
    if lname == "full":
        param, policy = fallback["param"], fallback["policy"]
    elif policy == "mondrian":
        edges = group_edges(tr["train"], n_groups)
        gv = groups_of(tr["val"], edges)
        lams = []
        for gi in range(n_groups):
            sub = [t for t, g in zip(tr["val"], gv) if g == gi]
            items = [(l, A.threshold_policy(sub, "p_now", l)) for l in B.LAMBDAS_P]
            idx, _ = A.ltt_select([p for p, _ in items], [o for _, o in items], ref[gv == gi], eps, B.DELTA / n_groups)
            if idx is None and truncated:
                return certify_choice(logs, est, fallback, eps, n_groups)
            lams.append(items[idx][0] if idx is not None else 1.01)
        param = {"edges": edges.tolist(), "lambdas": lams}
    else:
        if policy == "threshold":
            items = [(l, A.threshold_policy(tr["val"], "p_now", l)) for l in B.LAMBDAS_P]
        elif policy == "mdp":
            items = [(float(l), mdps["mdp"].policy(tr["val"], l)) for l in B.LAMBDAS_MDP]
        else:  # giveup, with the gamma chosen on the fitting pairs
            gam = choice["fit_param"][1]
            items = [((l, gam), A.accept_or_giveup_policy(tr["val"], l, gam)) for l in B.LAMBDAS_P]
        idx, _ = A.ltt_select([p for p, _ in items], [o for _, o in items], ref, eps, B.DELTA)
        if idx is None:  # not even the first (most conservative) parameter: the full budget
            return certify_choice(logs, est, fallback, eps, n_groups)
        param = items[idx][0]
    # a certified policy that can never stop before the last stage has the outcomes of the full budget at a higher
    # cost (it also runs the cheaper stages), so the full budget replaces it; this changes cost, never risk
    never_stops = (lname != "full" and not truncated and
                   ((policy == "mondrian" and min(param["lambdas"]) > 1.0) or
                    (policy == "threshold" and param > 1.0) or
                    (policy == "mdp" and not mdps["mdp"].solve(param)[:-1].any())))
    if never_stops:
        return certify_choice(logs, est, fallback, eps, n_groups)
    cfg = {"ladder": lname, "policy": policy, "param": param}
    o = policy_outcome(tr["val"], mdps, policy, param)
    chosen = choice.get("chosen", choice)
    cfg.update({"val_s": float(o.s.mean()), "val_rr": float(o.ok.mean()), "val_risk": float(np.mean(ref & ~o.ok)),
                "fit_s": choice.get("fit_s"), "chosen": {"ladder": chosen["ladder"], "policy": chosen["policy"]},
                "fallback": bool(choice.get("fallback", False))})
    return cfg, (tr, mdps)


def worst_case_ratio(recs, est, ladder, q=0.95):
    """q-quantile over pairs of (cost of running every stage of the ladder) / (cost of the full budget alone)."""
    r = [B.trajectory_ladder(x, est, ladder)[-1]["s"] / B.trajectory_ladder(x, est, (4,))[0]["s"] for x in recs]
    return float(np.quantile(r, q))


def select_and_certify(logs, est, ladders=None, eps=B.EPS, n_groups=N_GROUPS, families=FAMILIES + ("mondrian",),
                       rho=None):
    """Choose on logs['train'] (out-of-fold), certify the choice on logs['val']. Returns (selected, candidates, built)
    with selected = {"marginal": cfg, "mondrian": cfg} (only the requested families) and built[tag] = (tr, mdps).
    rho: optional worst-case bound; only ladders whose full run costs at most (1 + rho) times the full budget on 95 %
    of the fitting pairs are candidates (the full budget alone always is)."""
    ladders = B.LADDERS_EXT if ladders is None else ladders
    if rho is not None:
        ladders = {n: l for n, l in ladders.items() if n == "full" or worst_case_ratio(logs["train"], est, l) <= 1 + rho}
    rows = fit_candidates(logs["train"], est, ladders, len(logs["val"]), eps, n_groups, families)
    selected, built = {}, {}
    tags = (["marginal"] if set(families) - {"mondrian"} else []) + (["mondrian"] if "mondrian" in families else [])
    for tag in tags:
        cfg, b = certify_choice(logs, est, choose(rows, tag), eps, n_groups)
        selected[tag], built[tag] = cfg, b
    return selected, rows, built


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
                                  "tests": ["fcgf_3DMatch", "fcgf_3DLoMatch"]},
            # protocol v2 (PROTOCOL.md): blind tests first, development benchmarks after
            "v2_indoor_fpfh": {"train": "v2_fit", "val": "v2_cal",
                               "tests": ["v2_blind_hi", "v2_blind_lo", "3DMatch", "3DLoMatch"]},
            "v2_kitti_fpfh": {"train": "kitti_train", "val": "kitti_val+kitti_calib",
                              "tests": ["kitti_raw_blind", "kitti_test"]},
            "v2_indoor_fcgf": {"train": "fcgfown_v2_fit", "val": "fcgfown_val",
                               "tests": ["fcgfown_3DMatch", "fcgfown_3DLoMatch"]},
            "v2_kitti_fcgf": {"train": "fcgfown_kitti_fit", "val": "fcgfown_kitti_raw_cal",
                              "tests": ["fcgfown_kitti_raw_blind", "fcgfown_kitti_test"]}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="budget", choices=list(SUFFIX))
    ap.add_argument("--ladders", default="base", choices=["base", "extended"])
    ap.add_argument("--dataset", default="3dmatch", choices=list(DATASETS))
    ap.add_argument("--rho", type=float, default=None, help="worst-case bound (PROTOCOL.md variant)")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    D = DATASETS[args.dataset]
    logs = {"train": B.load(D["train"], args.prefix), "val": B.load(D["val"], args.prefix),
            **{s: B.load(s, args.prefix) for s in D["tests"]}}
    ladders = B.LADDERS if args.ladders == "base" else B.LADDERS_EXT
    suffix = SUFFIX[args.prefix] + ("" if args.ladders == "base" else "_ext") + \
        ("" if args.dataset == "3dmatch" else f"_{args.dataset}") + \
        ("" if args.rho is None else f"_rho{round(100 * args.rho):03d}")
    out = {}
    lines = ["# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation\n",
             "Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. "
             "Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).\n"]
    if args.prefix == "budgetc":
        lines.append("Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by "
                     "second-order compatibility with the 100 most distinctive ones; the reordering time is "
                     "charged to every configuration that truncates (adaptive and fixed), never to the full run.\n")
    for est, ename in [("sc2", "SC²-PCR"), ("turbo", "TurboReg")]:
        selected, rows, built = select_and_certify(logs, est, ladders, rho=args.rho)
        rows.sort(key=lambda x: x["fit_s"])
        lines.append(f"\n## {ename}\n\nStep 1, fitting pairs ({len(logs['train'])}, out-of-fold controller): operating "
                     f"point of every candidate at the loss share the certificate can accept for "
                     f"{len(logs['val'])} calibration pairs (cheapest first):\n")
        lines.append("| ladder | policy | parameters | fit risk % | fit mean time (ms) |")
        lines.append("|---|---|---|---|---|")
        for x in rows:
            p = "never stop early" if x["fit_param"] is None else fmt(x["fit_param"])
            lines.append(f"| {x['ladder']} | {x['policy']} | {p} | {100 * x['fit_risk']:.2f} | {1e3 * x['fit_s']:.0f} |")
        lines.append("\nStep 2, calibration pairs: Learn-then-Test of the chosen candidates only:\n")
        lines.append("| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |")
        lines.append("|---|---|---|---|---|---|---|")
        for tag, x in selected.items():
            lines.append(f"| {tag} | {x['chosen']['ladder']} / {x['chosen']['policy']} | {x['ladder']} / {x['policy']}"
                         f"{' (fallback)' if x['fallback'] else ''} | {fmt(x['param'])} | {100 * x['val_rr']:.1f} | "
                         f"{100 * x['val_risk']:.2f} | {1e3 * x['val_s']:.0f} |")
        marg, mond = selected["marginal"], selected["mondrian"]
        out[est] = {"candidates": rows, "selected": selected, "test": {}}
        for s in D["tests"]:
            lines.append(f"\n### {ename}, {s} test ({len(logs[s])} pairs)\n")
            lines.append("| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | "
                         "speed-up vs full [95% CI] | McNemar p | risk % |")
            lines.append("|---|---|---|---|---|---|---|---|")
            full = A.fixed_stage([B.trajectory_ladder(r, est, (4,)) for r in logs[s]], 0)
            for tag, x in [("marginal", marg), ("mondrian", mond)]:
                tr, mdps = built[tag]
                o = policy_outcome(tr[s], mdps, x["policy"], x["param"])
                cmp = B.paired(o, full, logs[s], B.MARGIN[s])
                risk = float(np.mean(full.ok & ~o.ok))
                lines.append(f"| {tag}: {x['ladder']} / {x['policy']} | {100 * o.ok.mean():.2f} | {1e3 * o.s.mean():.0f} | "
                             f"{100 * cmp['delta_rr']:+.2f} [{100 * cmp['ub95']:+.2f}] | {cmp['non_inferior']} | "
                             f"{cmp['speedup']:.2f}× [{cmp['speedup_ci'][0]:.2f}, {cmp['speedup_ci'][1]:.2f}] | "
                             f"{cmp['mcnemar_p']:.3g} | {100 * risk:.2f} |")
                stops = np.bincount(np.clip(o.stop, 0, None), minlength=len(B.LADDERS_EXT[x["ladder"]]))
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
