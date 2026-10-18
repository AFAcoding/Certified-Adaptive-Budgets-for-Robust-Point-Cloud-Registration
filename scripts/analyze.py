"""Evaluate adaptive computation policies offline and write results/ (tables, figures, summary).

Protocol (fixed before looking at test data):
  * controllers are fitted on the training-scene subset (no learned base model is
    involved, so training scenes are clean for this purpose);
  * operating points are certified on the validation scenes with Learn-then-Test
    (risk: pairs the exhaustive search solves but the policy does not; eps = 1 pp,
    delta = 0.1);
  * test sets (3DMatch, 3DLoMatch) are evaluated once with the official protocol:
    RMSE < 0.2 m, non-adjacent pairs, recall averaged over scenes.

Usage: python -I scripts/analyze.py [--prefix search] [--tag main]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from acpr import RESULTS_ROOT
from acpr import analysis as A

EPS, DELTA = 0.01, 0.10
MARGIN = {"3DMatch": 0.01, "3DLoMatch": 0.02, "val": 0.01}
TEST_SETS = ["3DMatch", "3DLoMatch"]
LAMBDAS_P = [1.01, 0.99, 0.98, 0.97, 0.96, 0.95, 0.94, 0.93, 0.92, 0.91, 0.9, 0.88, 0.86, 0.84, 0.82, 0.8, 0.75,
             0.7, 0.65, 0.6, 0.5, 0.4, 0.3, 0.2]
GAMMAS = [0.0, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3]
LAMBDAS_MDP = [-1.0, 0.0] + list(np.geomspace(1e-9, 1e-4, 40))  # -1: always continue (certification anchor)
GAMMAS_R = [0.0, 0.005, 0.01, 0.02, 0.03, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.4]
C1_THRESHOLDS = [8, 10, 12, 15, 18, 20, 25, 30, 40, 50, 60, 80, 100, 150, 200]


def eval_mask(recs, subset):
    if subset in TEST_SETS:
        return np.array([r["rr_eligible"] for r in recs])
    return np.ones(len(recs), dtype=bool)


def summarize(out: A.Outcome, recs, mask) -> dict:
    scenes = np.array([r["scene"] for r in recs])[mask]
    ok = out.ok[mask]
    return {
        "rr": A.scene_rr(ok, scenes),
        "rr_pooled": float(ok.mean()),
        "rr15": float(out.ok15[mask].mean()),
        "ce": float(out.ce[mask].mean()),
        "ce_median": float(np.median(out.ce[mask])),
        "s": float(out.s[mask].mean()),
        "n": int(mask.sum()),
    }


def compare(out: A.Outcome, ref: A.Outcome, recs, mask, margin, B=2000) -> dict:
    """Paired comparison against a reference: non-inferiority, McNemar, cost ratio, risk."""
    scenes = np.array([r["scene"] for r in recs])[mask]
    a, b = out.ok[mask], ref.ok[mask]
    ca, cb = out.ce[mask], ref.ce[mask]

    def diff(idx):
        return A.scene_rr(b[idx], scenes[idx]) - A.scene_rr(a[idx], scenes[idx])

    boot = A.stratified_bootstrap(diff, scenes, B=B)
    ratio_boot = A.stratified_bootstrap(lambda idx: cb[idx].mean() / ca[idx].mean(), scenes, B=B, seed=1)
    d = A.scene_rr(b, scenes) - A.scene_rr(a, scenes)
    ub = float(np.quantile(boot, 0.95))
    return {
        "delta_rr": float(d),  # reference minus policy (positive = policy worse)
        "delta_rr_ub95": ub,
        "non_inferior": bool(ub < margin),
        "mcnemar_p": A.mcnemar_exact(a, b),
        "cost_ratio": float(cb.mean() / ca.mean()),
        "cost_ratio_ci": [float(np.quantile(ratio_boot, 0.025)), float(np.quantile(ratio_boot, 0.975))],
        "risk": float(np.mean(b & ~a)),
        "gains": int(np.sum(a & ~b)),
        "losses": int(np.sum(~a & b)),
    }


NL = chr(10)


def fmt_pct(x):
    return f"{100 * x:.1f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="search")
    ap.add_argument("--tag", default="main")
    ap.add_argument("--select", default="consensus", choices=["consensus", "overlap", "product", "learned"],
                    help="how the incumbent basin is chosen (verification-based options need verify logs)")
    ap.add_argument("--baselines-from", default="search", help="log prefix that holds the RANSAC / SC2 fields")
    ap.add_argument("--schedule", default="full", choices=list(A.SCHEDULES))
    ap.add_argument("--precheck", action="store_true", help="use the registrability pre-check (gate + features)")
    ap.add_argument("--gate-k0", type=int, default=1000)
    ap.add_argument("--reference-prefix", default=None,
                    help="also compare against the exhaustive search of another log variant (e.g. full voting)")
    args = ap.parse_args()
    out_dir = RESULTS_ROOT / args.tag
    out_dir.mkdir(parents=True, exist_ok=True)

    from acpr import LOG_ROOT

    subsets = [s for s in ["train", "val", *TEST_SETS] if (LOG_ROOT / f"{args.prefix}_{s}.jsonl").exists()]
    logs = {}
    for s in subsets:
        with open(LOG_ROOT / f"{args.prefix}_{s}.jsonl") as f:
            logs[s] = [r for r in (json.loads(x) for x in f if x.strip()) if r.get("search")]
        if args.prefix != args.baselines_from:  # attach RANSAC / SC2 results logged with the full variant
            base = {}
            with open(LOG_ROOT / f"{args.baselines_from}_{s}.jsonl") as f:
                for x in f:
                    if x.strip():
                        b = json.loads(x)
                        base[b["pair_id"]] = b
            logs[s] = [{**r, **{k: base[r["pair_id"]][k] for k in ("ransac", "ransac_adaptive", "sc2")}}
                       for r in logs[s] if r["pair_id"] in base]
    print({s: len(v) for s, v in logs.items()}, flush=True)

    # ---- incumbent selection (consensus, or verification-based re-ranking)
    verify, vkw = {s: None for s in logs}, {}
    feats = A.SEARCH_FEATURES
    if args.select != "consensus":
        stats = []
        for s in logs:
            path = LOG_ROOT / f"verify_{args.prefix}_{s}.jsonl"
            verify[s] = {}
            with open(path) as f:
                for x in f:
                    if x.strip():
                        v = json.loads(x)
                        verify[s][v["pair_id"]] = v["overlap"]
                        stats.append((v["t_query_per_point"], v["t_tree"], v["n_sub"]))
        s_per_ce = float(np.median([lvl["s_vote"] / lvl["vote_cost"] for r in logs["val"] for lvl in r["search"]
                                    if lvl["vote_cost"] > 0]))
        vkw = {"ce_query": float(np.median([x[0] for x in stats])) / s_per_ce,
               "ce_tree": float(np.median([x[1] for x in stats])) / s_per_ce,
               "n_sub": int(np.median([x[2] for x in stats]))}
        print(f"verification cost model: {vkw} (seconds per CE {s_per_ce:.2e})", flush=True)
        feats = A.SEARCH_FEATURES_VERIFIED
    ranker = None
    if args.select == "learned":
        ranker = A.fit_basin_ranker(logs["train"], verify["train"])
    score_tables = {s: A.precompute_basin_scores(logs[s], verify[s], args.select, ranker) for s in logs}
    sched = A.SCHEDULES[args.schedule]
    pres = {s: (A.load_precheck(s) if args.precheck else {}) for s in logs}
    if args.precheck:
        for s in logs:
            logs[s] = [r for r in logs[s] if r["pair_id"] in pres[s]]
            for r in logs[s]:
                r["_pre_ce"] = pres[s][r["pair_id"]]["ce"]
        for s in [s for s in logs if not logs[s]]:
            del logs[s]
        feats = feats + A.PRE_STATE_FEATURES
    trajs = {s: [A.search_trajectory(r, schedule=sched, ov=(verify[s] or {}).get(r["pair_id"]) if verify[s] else None,
                                     score=A.lookup_score(score_tables[s]), pre=pres[s].get(r["pair_id"]) if args.precheck else None,
                                     **vkw) for r in logs[s]] for s in logs}
    rtrajs = {s: [A.ransac_trajectory_states(r) for r in logs[s]] for s in logs}

    # ---- controllers (fit on train scenes)
    fit_set = "train" if "train" in logs else "val"
    Xn, yn = A.rows(trajs[fit_set], feats, "ok")
    yf = A.final_labels(trajs[fit_set])
    clf_now = A.fit_classifier(Xn, yn)
    clf_final = A.fit_classifier(Xn, yf)
    for s in logs:
        A.attach_scores(trajs[s], feats, clf_now, clf_final)
    mdp = A.MDPController(trajs[fit_set])

    Xr, yr = A.rows(rtrajs[fit_set], A.RANSAC_FEATURES, "ok")
    yrf = A.final_labels(rtrajs[fit_set])
    rclf_now = A.fit_classifier(Xr, yr)
    rclf_final = A.fit_classifier(Xr, yrf)
    for s in logs:
        A.attach_scores(rtrajs[s], A.RANSAC_FEATURES, rclf_now, rclf_final)
    rmdp = A.MDPController(rtrajs[fit_set])

    # ---- policy families
    def families(tr, rtr):
        fam = {}
        fam["fixed_stage"] = [(k, A.fixed_stage(tr, k)) for k in range(len(tr[0]))]
        fam["c1_threshold"] = [(t, A.threshold_policy(tr, "c1", t)) for t in C1_THRESHOLDS]
        fam["learned_threshold"] = [(l, A.threshold_policy(tr, "p_now", l)) for l in LAMBDAS_P]
        fam["accept_or_giveup"] = [((l, g), A.accept_or_giveup_policy(tr, l, g)) for g in GAMMAS for l in LAMBDAS_P]
        fam["mdp"] = [(l, mdp.policy(tr, l)) for l in LAMBDAS_MDP]
        fam["oracle"] = [(None, A.oracle(tr))]
        fam["ransac_fixed"] = [(rtr[0][k]["k"], A.fixed_stage(rtr, k)) for k in range(len(rtr[0]))]
        fam["ransac_learned"] = [(l, A.threshold_policy(rtr, "p_now", l)) for l in LAMBDAS_P]
        fam["ransac_mdp"] = [(l, rmdp.policy(rtr, l)) for l in LAMBDAS_MDP]
        return fam

    fams = {s: families(trajs[s], rtrajs[s]) for s in logs if s != "train"}
    ref_full = None
    if args.reference_prefix:
        ref_full = {}
        for s in fams:
            with open(LOG_ROOT / f"{args.reference_prefix}_{s}.jsonl") as f:
                full = {r["pair_id"]: r for r in (json.loads(x) for x in f if x.strip())}
            tr_full = [A.search_trajectory(full[r["pair_id"]], schedule=sched) for r in logs[s]]
            ref_full[s] = A.fixed_stage(tr_full, len(tr_full[0]) - 1)
            summary_ref = summarize(ref_full[s], logs[s], eval_mask(logs[s], s))
            print(f"{s}: reference ({args.reference_prefix}) exhaustive RR {summary_ref['rr']:.4f} CE {summary_ref['ce']:.0f}", flush=True)
    if args.precheck:  # registrability gate in front of classical RANSAC (fit on train)
        Xg = A.gate_rows(logs[fit_set], rtrajs[fit_set], pres[fit_set], args.gate_k0)
        yg = np.array([r["ransac_adaptive"]["ok"] for r in logs[fit_set]], int)
        gate = A.fit_classifier(Xg, yg)
        for s in fams:
            gp = gate.predict_proba(A.gate_rows(logs[s], rtrajs[s], pres[s], args.gate_k0))[:, 1]
            fams[s]["ransac_gate"] = [(g, A.ransac_gate_policy(logs[s], rtrajs[s], gp, g, args.gate_k0)) for g in GAMMAS_R]
    for s in fams:
        fams[s]["ransac_hybrid"] = [(g, A.ransac_hybrid_policy(logs[s], rtrajs[s], g)) for g in GAMMAS_R]

    # classical adaptive RANSAC and SC^2 (from logs)
    def classical_ransac(recs):
        ok = np.array([r["ransac_adaptive"]["ok"] for r in recs])
        ok15 = np.array([r["ransac_adaptive"]["ok15"] for r in recs])
        ce = np.array([3 * r["ransac_adaptive"]["k"] + r["ransac_adaptive"]["scored"] * r["N"] for r in recs], float)
        s = np.array([r["ransac_adaptive"]["s"] for r in recs])
        return A.Outcome(ok, ok15, ce, s, np.zeros(len(recs), int))

    def sc2(recs):
        ok = np.array([r["sc2"]["ok"] for r in recs])
        ok15 = np.array([r["sc2"]["ok15"] for r in recs])
        s = np.array([r["sc2"]["s"] for r in recs])
        return A.Outcome(ok, ok15, np.full(len(recs), np.nan), s, np.zeros(len(recs), int))

    # ---- static configurations (single-shot (density, basins))
    statics = {}
    for s in fams:
        res = []
        sfn = A.lookup_score(score_tables[s]) if args.select != "consensus" else None
        n_lv = min(len(r["search"]) for r in logs[s])
        for d, b in [(d, b) for d, b in A.STATIC_GRID if d < n_lv]:
            outs = [A.static_outcome(r, d, b, ov=(verify[s] or {}).get(r["pair_id"]) if verify[s] else None,
                                     score=sfn, **vkw) for r in logs[s]]
            o = A.Outcome(np.array([x["ok"] for x in outs]), np.array([x["ok15"] for x in outs]),
                          np.array([x["ce"] for x in outs], float), np.array([x["s"] for x in outs]),
                          np.zeros(len(outs), int))
            res.append(((d, b), o))
        statics[s] = res

    # ---- certify operating points on validation (Learn-then-Test)
    val_recs, vmask = logs["val"], eval_mask(logs["val"], "val")
    ref_val = fams["val"]["fixed_stage"][-1][1]  # exhaustive = full schedule
    ref_ok_val = ref_val.ok[vmask]
    certified = {}

    def certify(name, items, ref_ok, mask):
        idx, pvals = A.ltt_select([p for p, _ in items], [_mask(o, mask) for _, o in items], ref_ok, EPS, DELTA)
        return idx

    def _mask(o, mask):
        return A.Outcome(o.ok[mask], o.ok15[mask], o.ce[mask], o.s[mask], o.stop[mask])

    for name in ["learned_threshold", "mdp"]:
        items = fams["val"][name]
        idx = certify(name, items, ref_ok_val, vmask)
        certified[name] = None if idx is None else items[idx][0]
    # accept-or-giveup: one LTT sequence per gamma (Bonferroni over gammas), keep the cheapest certified
    best = None
    for g in GAMMAS:
        items = [(p, o) for p, o in fams["val"]["accept_or_giveup"] if p[1] == g]
        idx, _ = A.ltt_select([p for p, _ in items], [_mask(o, vmask) for _, o in items], ref_ok_val, EPS,
                              DELTA / len(GAMMAS))
        if idx is not None:
            cost = items[idx][1].ce[vmask].mean()
            if best is None or cost < best[1]:
                best = (items[idx][0], cost)
    certified["accept_or_giveup"] = None if best is None else best[0]
    # RANSAC with learned stopping, certified against RANSAC-100k
    ref_r_val = fams["val"]["ransac_fixed"][-1][1]
    items = fams["val"]["ransac_learned"]
    idx, _ = A.ltt_select([p for p, _ in items], [_mask(o, vmask) for _, o in items], ref_r_val.ok[vmask], EPS, DELTA)
    certified["ransac_learned"] = None if idx is None else items[idx][0]
    # drop-in RANSAC improvement: classical rule + certified give-up, certified against classical RANSAC
    ref_cls_val = classical_ransac(logs["val"])
    items = fams["val"]["ransac_hybrid"]
    idx, _ = A.ltt_select([p for p, _ in items], [_mask(o, vmask) for _, o in items], ref_cls_val.ok[vmask], EPS, DELTA)
    certified["ransac_hybrid"] = None if idx is None else items[idx][0]
    if "ransac_gate" in fams["val"]:
        items = fams["val"]["ransac_gate"]
        idx, _ = A.ltt_select([p for p, _ in items], [_mask(o, vmask) for _, o in items], ref_cls_val.ok[vmask], EPS, DELTA)
        certified["ransac_gate"] = None if idx is None else items[idx][0]
    print("certified on val:", certified, flush=True)

    def pick(fam_items, param):
        for p, o in fam_items:
            if p == param:
                return o
        return None

    # ---- evaluate on every set
    summary = {"certified": {k: (list(v) if isinstance(v, tuple) else v) for k, v in certified.items()},
               "eps": EPS, "delta": DELTA, "sets": {}}
    for s in fams:
        recs, mask = logs[s], eval_mask(logs[s], s)
        fam = fams[s]
        exhaustive = fam["fixed_stage"][-1][1]
        ransac100k = fam["ransac_fixed"][-1][1]
        st = {"n_pairs": int(mask.sum()), "families": {}, "static": [], "operating_points": {}}
        for name, items in fam.items():
            st["families"][name] = [{"param": (list(p) if isinstance(p, tuple) else p), **summarize(o, recs, mask)}
                                    for p, o in items]
        for (d, b), o in statics[s]:
            st["static"].append({"d": d, "b": b, **summarize(o, recs, mask)})
        st["classical_ransac"] = summarize(classical_ransac(recs), recs, mask)
        sc = sc2(recs)
        st["sc2"] = {"rr": A.scene_rr(sc.ok[mask], np.array([r["scene"] for r in recs])[mask]),
                     "rr15": float(sc.ok15[mask].mean()), "s": float(sc.s[mask].mean())}
        st["exhaustive"] = summarize(exhaustive, recs, mask)
        st["ransac100k"] = summarize(ransac100k, recs, mask)
        st["oracle"] = summarize(fam["oracle"][0][1], recs, mask)
        margin = MARGIN.get(s, 0.02)
        for name in ["learned_threshold", "mdp", "accept_or_giveup"]:
            p = certified.get(name)
            if p is None:
                continue
            o = pick(fam[name], p)
            st["operating_points"][name] = {"param": (list(p) if isinstance(p, tuple) else p),
                                            **summarize(o, recs, mask),
                                            "vs_exhaustive": compare(o, exhaustive, recs, mask, margin),
                                            "vs_ransac_classical": compare(o, classical_ransac(recs), recs, mask, margin),
                                            "vs_ransac100k": compare(o, ransac100k, recs, mask, margin)}
            if ref_full is not None and s in ref_full:
                st["operating_points"][name]["vs_full_voting_exhaustive"] = compare(o, ref_full[s], recs, mask, margin)
        gate_name = "ransac_gate" if certified.get("ransac_gate") is not None else "ransac_hybrid"
        p = certified.get(gate_name)
        if p is not None:
            o = pick(fam[gate_name], p)
            cls = classical_ransac(recs)
            st["operating_points"][gate_name] = {"param": p, **summarize(o, recs, mask),
                                                       "vs_classical": compare(o, cls, recs, mask, margin)}
            gt_ = np.array([r["gt_inliers"] for r in recs])[mask]
            ra = []
            for lo, hi in zip([0, 5, 10, 20, 40, 80], [5, 10, 20, 40, 80, 10**9]):
                m = (gt_ >= lo) & (gt_ < hi)
                if m.sum():
                    ra.append({"gt_inliers": f"[{lo},{hi if hi < 10**9 else 'inf'})", "pairs": int(m.sum()),
                               "classical_ce": float(cls.ce[mask][m].mean()), "hybrid_ce": float(o.ce[mask][m].mean()),
                               "classical_rr": float(cls.ok[mask][m].mean()), "hybrid_rr": float(o.ok[mask][m].mean()),
                               "classical_cost_share": float(cls.ce[mask][m].sum() / cls.ce[mask].sum())})
            st["ransac_allocation"] = ra
        p = certified.get("ransac_learned")
        if p is not None:
            o = pick(fam["ransac_learned"], p)
            st["operating_points"]["ransac_learned"] = {"param": p, **summarize(o, recs, mask),
                                                        "vs_ransac100k": compare(o, ransac100k, recs, mask, margin),
                                                        "vs_classical": compare(o, classical_ransac(recs), recs, mask,
                                                                                margin)}
        # static frontier (upper convex hull) and how far each operating point sits above it
        hull = A.upper_hull([(x["ce"], x["rr"]) for x in st["static"]])
        st["static_hull"] = hull
        for name, op in st["operating_points"].items():
            if name.startswith("ransac"):
                continue
            op["static_hull_rr_at_cost"] = A.hull_value(hull, op["ce"])
        # cost allocation by difficulty (ground-truth inliers among the correspondences)
        gt = np.array([r["gt_inliers"] for r in recs])[mask]
        bins = [0, 5, 10, 20, 40, 80, 10**9]
        alloc = []
        best_name = "mdp" if "mdp" in st["operating_points"] else next(iter(st["operating_points"]), None)
        o_best = pick(fam[best_name], certified[best_name]) if best_name else None
        for lo, hi in zip(bins[:-1], bins[1:]):
            m = (gt >= lo) & (gt < hi)
            if m.sum() == 0:
                continue
            row = {"gt_inliers": f"[{lo},{hi if hi < 10**9 else 'inf'})", "pairs": int(m.sum()),
                   "exhaustive_ce": float(exhaustive.ce[mask][m].mean()),
                   "exhaustive_rr": float(exhaustive.ok[mask][m].mean())}
            if o_best is not None:
                row.update({"adaptive": best_name, "adaptive_ce": float(o_best.ce[mask][m].mean()),
                            "adaptive_rr": float(o_best.ok[mask][m].mean())})
            alloc.append(row)
        st["allocation_by_difficulty"] = alloc
        summary["sets"][s] = st

    with open(out_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=1, default=float)
    write_report(summary, out_dir)
    make_figures(summary, out_dir)
    print(f"wrote {out_dir}", flush=True)


def write_report(summary, out_dir: Path):
    L = []
    L.append(f"# Results ({out_dir.name})\n")
    L.append(f"Operating points certified on validation with Learn-then-Test (eps = {100 * summary['eps']:.0f} pp, "
             f"delta = {summary['delta']}): `{summary['certified']}`\n")
    for s, st in summary["sets"].items():
        L.append(f"\n## {s} ({st['n_pairs']} pairs)\n")
        L.append("| Method | RR % (scene avg) | RR % (RE<15°, TE<30cm) | mean cost (k CE) | median cost (k CE) | "
                 "mean time (ms) | vs exhaustive: ΔRR pp [95% UB] | cost reduction |")
        L.append("|---|---|---|---|---|---|---|---|")

        def row(name, x, cmp=None):
            ce = "—" if not np.isfinite(x.get("ce", np.nan)) else f"{x['ce'] / 1e3:.1f}"
            ced = "—" if not np.isfinite(x.get("ce_median", np.nan)) else f"{x['ce_median'] / 1e3:.1f}"
            c = "" if cmp is None else f"{100 * cmp['delta_rr']:+.1f} [{100 * cmp['delta_rr_ub95']:+.1f}]"
            red = "" if cmp is None else f"{cmp['cost_ratio']:.1f}× [{cmp['cost_ratio_ci'][0]:.1f}, {cmp['cost_ratio_ci'][1]:.1f}]"
            L.append(f"| {name} | {fmt_pct(x['rr'])} | {fmt_pct(x.get('rr15', np.nan))} | {ce} | {ced} | "
                     f"{1e3 * x['s']:.0f} | {c} | {red} |")

        row("Exhaustive pose search (7 stages)", st["exhaustive"])
        stage0 = st["families"]["fixed_stage"][0]
        row("Cheapest stage only (256 rotations, 1 basin)", stage0)
        best_static = max(st["static"], key=lambda x: (round(x["rr"], 4), -x["ce"]))
        row(f"Best static config (M={256 * 2 ** best_static['d']}, b={best_static['b']})", best_static)
        for name, label in [("learned_threshold", "Adaptive: learned stop (LTT)"),
                            ("accept_or_giveup", "Adaptive: stop or give up (LTT)"),
                            ("mdp", "Adaptive: Markov controller (LTT)")]:
            if name in st["operating_points"]:
                op = st["operating_points"][name]
                row(label + f" param={op['param']}", op, op["vs_exhaustive"])
        row("Oracle stopping (upper bound)", st["oracle"])
        row("RANSAC 100k", st["ransac100k"])
        row("RANSAC, classical adaptive stopping (p=0.999)", st["classical_ransac"])
        if "ransac_learned" in st["operating_points"]:
            op = st["operating_points"]["ransac_learned"]
            row(f"RANSAC + learned stop (LTT) param={op['param']}", op, op["vs_ransac100k"])
        for gname, glabel in [("ransac_hybrid", "RANSAC classical + certified give-up (ours)"),
                              ("ransac_gate", "RANSAC classical + certified registrability gate (ours)")]:
            if gname in st["operating_points"]:
                op = st["operating_points"][gname]
                row(f"{glabel} γ={op['param']}", op, op["vs_classical"])
        L.append(f"| SC² (same correspondences) | {fmt_pct(st['sc2']['rr'])} | {fmt_pct(st['sc2']['rr15'])} | — | — | "
                 f"{1e3 * st['sc2']['s']:.0f} | | |")
        if st["operating_points"]:
            L.append("\nPaired statistics against the exhaustive search (ΔRR = exhaustive − policy; non-inferiority "
                     "margin per set; McNemar exact test):\n")
            L.append("| Policy | ΔRR pp | 95% upper bound | non-inferior | McNemar p | gains / losses | risk % | "
                     "static frontier RR % at same cost |")
            L.append("|---|---|---|---|---|---|---|---|")
            for name, op in st["operating_points"].items():
                cmp = op.get("vs_exhaustive") or op.get("vs_classical") or op.get("vs_ransac100k")
                hull = op.get("static_hull_rr_at_cost")
                L.append(f"| {name} | {100 * cmp['delta_rr']:+.2f} | {100 * cmp['delta_rr_ub95']:+.2f} | "
                         f"{cmp['non_inferior']} | {cmp['mcnemar_p']:.3f} | {cmp['gains']} / {cmp['losses']} | "
                         f"{100 * cmp['risk']:.2f} | {'' if hull is None else fmt_pct(hull)} |")
        heads = [(n, op) for n, op in st["operating_points"].items() if "vs_ransac_classical" in op]
        if heads:
            L.append(NL + "Head-to-head against standard implementations on the same correspondences "
                     "(dRR = reference - ours, negative = ours better; cost ratio = reference cost / our cost):" + NL)
            L.append("| Our policy | vs | ΔRR pp [95% UB] | McNemar p | cost ratio [95% CI] |")
            L.append("|---|---|---|---|---|")
            for n, op in heads:
                for key, lab in [("vs_ransac_classical", "RANSAC, classical stopping"), ("vs_ransac100k", "RANSAC 100k"),
                                 ("vs_exhaustive", "exhaustive search (same voting)"),
                                 ("vs_full_voting_exhaustive", "exhaustive search, full voting")]:
                    if key in op:
                        c = op[key]
                        L.append(f"| {n} | {lab} | {100 * c['delta_rr']:+.1f} [{100 * c['delta_rr_ub95']:+.1f}] | "
                                 f"{c['mcnemar_p']:.3g} | {c['cost_ratio']:.2f}× [{c['cost_ratio_ci'][0]:.2f}, {c['cost_ratio_ci'][1]:.2f}] |")
        if st.get("allocation_by_difficulty"):
            L.append("\nCompute allocation by difficulty (ground-truth inliers among the putative correspondences):\n")
            L.append("| GT inliers | pairs | exhaustive cost (k CE) | adaptive cost (k CE) | exhaustive RR % | adaptive RR % |")
            L.append("|---|---|---|---|---|---|")
            for a in st["allocation_by_difficulty"]:
                L.append(f"| {a['gt_inliers']} | {a['pairs']} | {a['exhaustive_ce'] / 1e3:.1f} | "
                         f"{a.get('adaptive_ce', np.nan) / 1e3:.1f} | {fmt_pct(a['exhaustive_rr'])} | "
                         f"{fmt_pct(a.get('adaptive_rr', np.nan))} |")
        if st.get("ransac_allocation"):
            L.append("\nRANSAC budget by difficulty: classical stopping rule vs. classical + certified give-up:\n")
            L.append("| GT inliers | pairs | share of classical budget | classical cost (k CE) | ours (k CE) | classical RR % | ours RR % |")
            L.append("|---|---|---|---|---|---|---|")
            for a in st["ransac_allocation"]:
                L.append(f"| {a['gt_inliers']} | {a['pairs']} | {100 * a['classical_cost_share']:.0f} % | "
                         f"{a['classical_ce'] / 1e3:.1f} | {a['hybrid_ce'] / 1e3:.1f} | {fmt_pct(a['classical_rr'])} | "
                         f"{fmt_pct(a['hybrid_rr'])} |")
    (out_dir / "report.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def make_figures(summary, out_dir: Path):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    INK, INK2, MUTED, GRID, BASE, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
    BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
    plt.rcParams.update({"font.family": "sans-serif", "font.size": 9, "axes.edgecolor": BASE,
                         "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED,
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF})
    for s, st in summary["sets"].items():
        fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=160)
        ax.grid(True, color=GRID, linewidth=0.6)
        ax.set_axisbelow(True)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        sx = [x["ce"] / 1e3 for x in st["static"]]
        sy = [100 * x["rr"] for x in st["static"]]
        ax.scatter(sx, sy, s=14, color=BASE, zorder=2, label="Static search configs")
        hull = st["static_hull"]
        ax.plot([h[0] / 1e3 for h in hull], [100 * h[1] for h in hull], color=MUTED, lw=1.2, ls="--", zorder=2,
                label="Static frontier")

        def curve(items, color, label, marker="o"):
            pts = sorted({(x["ce"] / 1e3, 100 * x["rr"]) for x in items})
            front = A.upper_hull([(p[0], p[1]) for p in pts])
            ax.plot([p[0] for p in front], [p[1] for p in front], color=color, lw=2, marker=marker, ms=4,
                    zorder=3, label=label)

        curve(st["families"]["mdp"], BLUE, "Adaptive search (Markov controller)")
        curve(st["families"]["ransac_fixed"], ORANGE, "RANSAC, fixed budgets", marker="s")
        cr = st["classical_ransac"]
        ax.scatter([cr["ce"] / 1e3], [100 * cr["rr"]], s=46, facecolor=SURF, edgecolor=ORANGE, linewidth=2, zorder=4,
                   label="RANSAC, classical adaptive stop")
        ex = st["exhaustive"]
        ax.scatter([ex["ce"] / 1e3], [100 * ex["rr"]], s=46, color=INK2, marker="D", zorder=4,
                   label="Exhaustive search")
        if "mdp" in st["operating_points"]:
            op = st["operating_points"]["mdp"]
            ax.scatter([op["ce"] / 1e3], [100 * op["rr"]], s=90, color=BLUE, marker="*", zorder=5,
                       edgecolor=SURF, linewidth=1)
            ax.annotate(f"certified point\n{op['vs_exhaustive']['cost_ratio']:.1f}× cheaper",
                        (op["ce"] / 1e3, 100 * op["rr"]), xytext=(10, -26), textcoords="offset points",
                        color=INK, fontsize=8)
        ax.set_xscale("log")
        ax.set_xlabel("Mean search cost per pair (thousand correspondence evaluations, log scale)")
        ax.set_ylabel("Registration recall (%)")
        ax.set_title(f"{s}: accuracy vs. search cost", color=INK, fontsize=10, loc="left")
        ax.legend(frameon=False, fontsize=7.5, loc="lower right", labelcolor=INK2)
        fig.tight_layout()
        fig.savefig(out_dir / f"pareto_{s}.png")
        plt.close(fig)

        alloc = st.get("allocation_by_difficulty")
        if alloc and "adaptive_ce" in alloc[0]:
            fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.0), dpi=160)
            labels = [a["gt_inliers"] for a in alloc]
            xi = np.arange(len(labels))
            for ax, key, title in [(axes[0], "ce", "Mean search cost (k CE)"), (axes[1], "rr", "Registration recall (%)")]:
                ax.grid(True, axis="y", color=GRID, linewidth=0.6)
                ax.set_axisbelow(True)
                for spine in ("top", "right"):
                    ax.spines[spine].set_visible(False)
                scale = 1e-3 if key == "ce" else 100
                ax.bar(xi - 0.2, [a[f"exhaustive_{key}"] * scale for a in alloc], width=0.38, color=BASE,
                       label="Exhaustive")
                ax.bar(xi + 0.2, [a[f"adaptive_{key}"] * scale for a in alloc], width=0.38, color=BLUE,
                       label="Adaptive (Markov)")
                ax.set_xticks(xi, labels, fontsize=7)
                ax.set_xlabel("Ground-truth inliers among correspondences")
                ax.set_title(title, color=INK, fontsize=9, loc="left")
            axes[0].legend(frameon=False, fontsize=7.5, labelcolor=INK2)
            fig.tight_layout()
            fig.savefig(out_dir / f"allocation_{s}.png")
            plt.close(fig)


if __name__ == "__main__":
    main()
