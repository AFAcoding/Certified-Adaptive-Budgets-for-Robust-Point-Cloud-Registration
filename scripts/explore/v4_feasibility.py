"""Exploration for a possible method v4 (fitting, calibration and development data only; no blind set is loaded).

Dataset family v2_indoor_fpfh (fit v2_fit, calibration v2_cal, development 3DMatch / 3DLoMatch), compatibility order,
the method-v3 configuration (classifier chosen on the fitting pairs, hardness gate). Offline costs from the logs.

E-A  Anatomy of CAB v3's cost on the development sets: share of pairs and of time by outcome (gated, stopped at
     stage k, unsolvable), and the excess over an oracle that stops at the first correct stage (and stops
     unsolvable pairs after the first stage).
E-B  Certified give-up, valid by a union bound: stop thresholds re-certified at eps1 = 0.5 % and a group-wise give-up
     threshold gamma_g on p_final at the first stage certified at eps2 = 0.5 %, each per group at delta / (2 G).
     A pair that gives up returns its first-stage estimate (as CAB's accept-or-give-up family does).
E-C  Certified start-rung routing: pairs predicted easy (by a classifier on the gate signals, trained on the fitting
     pairs only) run the ladder 250-4000, the others the selected ladder; the composite policy is certified directly,
     per (route x difficulty group) cell, at eps = 1 %, delta / (#cells).

Usage: python -I scripts/explore/v4_feasibility.py
Writes results/explore/v4_feasibility.json
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import analyze_budget as B  # noqa: E402
import select_ladder as S  # noqa: E402
from acpr import RESULTS_ROOT  # noqa: E402
from acpr import analysis as A  # noqa: E402

FAM, DEV = "v2_indoor_fpfh", ["3DMatch", "3DLoMatch"]
CFG = RESULTS_ROOT / "budget" / "v3_uncorrected_gate_accounting" / f"ladder_selection_compat_ext_{FAM}_ctlauto_gate.json"
GAMMAS = [0.0, 0.01, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4]
EPS, DELTA, G = 0.01, 0.10, 3


def outcome_with_giveup(trs, edges, lams, gams):
    g = S.groups_of(trs, edges)
    stops = []
    for t, gi in zip(trs, g):
        if t[0]["p_final"] < gams[gi]:
            stops.append(0)
            continue
        stops.append(next((st["stage"] for st in t if st["p_now"] >= lams[gi]), len(t) - 1))
    return A._from_stops(trs, stops)


def certify_lams(tr_val, ref, edges, eps, delta):
    gv = S.groups_of(tr_val, edges)
    lams = []
    for gi in range(G):
        sub = [t for t, g in zip(tr_val, gv) if g == gi]
        items = [(l, A.threshold_policy(sub, "p_now", l)) for l in B.LAMBDAS_P]
        idx, _ = A.ltt_select([p for p, _ in items], [o for _, o in items], ref[gv == gi], eps, delta)
        lams.append(items[idx][0] if idx is not None else 1.01)
    return lams


def main():
    out = {}
    for est in ("sc2", "turbo"):
        cfg = json.loads(CFG.read_text())[est]["selected"]["mondrian"]
        A.CLASSIFIER = cfg["classifier"]
        logs = {"train": B.load("v2_fit", "budgetc"), "val": B.load("v2_cal", "budgetc"),
                **{s: B.load(s, "budgetc") for s in DEV}}
        ladder = B.LADDERS_EXT[cfg["ladder"]]
        tr, mdps = S.build(logs, est, ladder)
        edges, lams = np.array(cfg["param"]["edges"]), cfg["param"]["lambdas"]
        gate = S.fit_gate_for(logs, {"train": "v2_fit", "val": "v2_cal"}, est, cfg, (tr, mdps), "budgetc")
        full = {s: A.fixed_stage([B.trajectory_ladder(r, est, (4,)) for r in logs[s]], 0) for s in logs}
        res = {"ladder": cfg["ladder"], "classifier": cfg["classifier"]}

        def v3(s, o):  # apply the gate (evaluation accounting as in select_ladder)
            if gate.clf is None:
                return o, np.zeros(len(o.ok), bool)
            gated = gate.predict(S.load_gate_features(s, logs[s])[0])
            return S.gated_outcome(o, full[s], gated, S.gate_eval_charges(logs[s], "budgetc", gate.kind)), gated

        # ---- E-A: anatomy
        for s in DEV:
            o0 = S.mondrian_policy(tr[s], edges, lams)
            o, gated = v3(s, o0)
            fok = full[s].ok
            orc = A.oracle(tr[s])
            first = np.array([t[0]["s"] for t in tr[s]])
            orc_s = np.where(fok, orc.s, first)  # oracle stops unsolvable pairs after the first stage
            cats = {"gated": gated, "unsolvable(not gated)": ~gated & ~fok}
            for k in range(len(ladder)):
                cats[f"stop{k}(solvable)"] = ~gated & fok & (o.stop == k)
            tot = o.s.sum()
            res[f"A.{s}"] = {
                "speed_v3": float(full[s].s.mean() / o.s.mean()), "speed_oracle": float(full[s].s.mean() / orc_s.mean()),
                "cats": {c: {"pairs%": round(100 * m.mean(), 1), "time%": round(100 * o.s[m].sum() / tot, 1),
                             "excess_over_oracle%": round(100 * (o.s[m] - orc_s[m]).sum() / tot, 1)}
                         for c, m in cats.items()}}

        # ---- E-B: give-up with a split risk budget (union bound)
        ref = full["val"].ok
        lams_b = certify_lams(tr["val"], ref, edges, EPS / 2, DELTA / 2 / G)
        gv = S.groups_of(tr["val"], edges)
        gams = []
        for gi in range(G):
            sub = [t for t, g in zip(tr["val"], gv) if g == gi]
            # risk of giving up alone: pairs the full budget registers whose first-stage estimate is wrong
            outs = [A._from_stops(sub, [0 if t[0]["p_final"] < gm else len(t) - 1 for t in sub]) for gm in GAMMAS]
            idx, _ = A.ltt_select(GAMMAS, outs, ref[gv == gi], EPS / 2, DELTA / 2 / G)
            gams.append(GAMMAS[idx] if idx is not None else 0.0)
        res["B.params"] = {"lams_eps0.5": lams_b, "gammas": gams}
        for s in DEV:
            o, _ = v3(s, outcome_with_giveup(tr[s], edges, lams_b, gams))
            fok = full[s].ok
            gave = np.array([t[0]["p_final"] < gams[g] for t, g in zip(tr[s], S.groups_of(tr[s], edges))])
            res[f"B.{s}"] = {"speed": float(full[s].s.mean() / o.s.mean()), "risk%": float(100 * np.mean(fok & ~o.ok)),
                             "gave_up%": float(100 * gave.mean()),
                             "gave_up_of_unsolvable%": float(100 * (gave & ~fok).sum() / max((~fok).sum(), 1))}

        # ---- E-C: start-rung routing, composite certified per (route x group) cell
        from acpr.gate import model
        lad_lo = B.LADDERS_EXT["250-4000"]
        tr_lo, _ = S.build(logs, est, lad_lo)
        y = np.array([bool(r[est][0]["ok15"]) for r in logs["train"]])  # solved at 250 (fitting pairs only)
        Xtr = S.load_gate_features("v2_fit", logs["train"])[0]
        clf = model("hgb").fit(Xtr, y.astype(int))
        edges_lo = S.group_edges(tr_lo["train"], G)
        res["C"] = {}
        for thr in (0.5, 0.7, 0.85):
            route = {s: clf.predict_proba(S.load_gate_features({"val": "v2_cal"}.get(s, s), logs[s])[0])[:, 1] >= thr
                     for s in ["val"] + DEV}

            def cell(s):
                g_hi = S.groups_of(tr[s], edges)
                g_lo = S.groups_of(tr_lo[s], edges_lo)
                return np.where(route[s], G + g_lo, g_hi)

            cv = cell("val")
            lam_c = []
            for c in range(2 * G):
                m = cv == c
                if not m.any():
                    lam_c.append(1.01)
                    continue
                src = tr_lo["val"] if c >= G else tr["val"]
                sub = [t for t, mm in zip(src, m) if mm]
                items = [(l, A.threshold_policy(sub, "p_now", l)) for l in B.LAMBDAS_P]
                idx, _ = A.ltt_select([p for p, _ in items], [o for _, o in items], ref[m], EPS, DELTA / (2 * G))
                lam_c.append(items[idx][0] if idx is not None else 1.01)
            r_thr = {"lams": lam_c}
            for s in DEV:
                cs = cell(s)
                stops_hi = [next((st["stage"] for st in t if st["p_now"] >= lam_c[c]), len(t) - 1)
                            for t, c in zip(tr[s], cs)]
                stops_lo = [next((st["stage"] for st in t if st["p_now"] >= lam_c[c]), len(t) - 1)
                            for t, c in zip(tr_lo[s], cs)]
                o_hi, o_lo = A._from_stops(tr[s], stops_hi), A._from_stops(tr_lo[s], stops_lo)
                rt = route[s]
                o = A.Outcome(np.where(rt, o_lo.ok, o_hi.ok), np.where(rt, o_lo.ok15, o_hi.ok15),
                              np.where(rt, o_lo.ce, o_hi.ce), np.where(rt, o_lo.s, o_hi.s), np.where(rt, o_lo.stop, o_hi.stop))
                o, _ = v3(s, o)
                fok = full[s].ok
                r_thr[s] = {"routed_low%": float(100 * rt.mean()), "speed": float(full[s].s.mean() / o.s.mean()),
                            "risk%": float(100 * np.mean(fok & ~o.ok))}
            res["C"][str(thr)] = r_thr
        A.CLASSIFIER = "logit"
        out[est] = res
        print(est, json.dumps(res, indent=1), flush=True)
    (RESULTS_ROOT / "explore" / "v4_feasibility.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
