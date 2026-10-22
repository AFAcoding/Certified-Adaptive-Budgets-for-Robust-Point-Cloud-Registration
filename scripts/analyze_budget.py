"""Certified adaptive correspondence budgets for SC^2-PCR and TurboReg.

Each estimator runs on the top-N (Lowe-ratio ordered) correspondences, N = 250 ... 4000.
A controller fitted on training scenes decides after each budget whether to stop.
Operating points are certified on validation (Learn-then-Test, eps = 1 pp,
delta = 0.1, reference = the full-budget estimator) and evaluated once on the
3DMatch / 3DLoMatch test sets.

Primary protocol (as in the SC^2 / MAC / TurboReg papers): success = RE <= 15 deg and
TE <= 30 cm, pooled over all pairs. Secondary: official RMSE < 0.2 m recall,
scene-averaged over non-adjacent pairs. Cost: cumulative wall-clock seconds
(single-threaded BLAS) and cumulative operation counts.

Usage: python -I scripts/analyze_budget.py
"""

from __future__ import annotations

import json

import numpy as np

from acpr import LOG_ROOT, RESULTS_ROOT
from acpr import analysis as A

FEATURES = ["log_inl", "inl_frac", "inl_all_frac", "top250_frac", "log_dpose_deg", "log_dpose_m", "agree",
            "stage", "log_N_all", "ratio_med", "inl_gain", "log_inl_all"]
LAMBDAS_P = [1.01, 0.995, 0.99, 0.98, 0.97, 0.96, 0.95, 0.94, 0.93, 0.92, 0.9, 0.88, 0.85, 0.8, 0.75, 0.7, 0.6, 0.5]
LAMBDAS_MDP = [-1.0, 0.0] + list(np.geomspace(1e-3, 30, 40))  # cost unit: seconds
EPS, DELTA = 0.01, 0.10
MARGIN = {"3DMatch": 0.01, "3DLoMatch": 0.02, "val": 0.01, "kitti_test": 0.01, "kitti_val": 0.01,
          "fcgf_3DMatch": 0.01, "fcgf_3DLoMatch": 0.02, "fcgf_kitti_test": 0.01,
          # protocol v2: 2 pp at low overlap (10-30 %), 1 pp elsewhere, as above
          "v2_blind_hi": 0.01, "v2_blind_lo": 0.02, "kitti_raw_blind": 0.01, "fcgfown_3DMatch": 0.01,
          "fcgfown_3DLoMatch": 0.02, "fcgfown_kitti_raw_blind": 0.01, "fcgfown_kitti_test": 0.01,
          "v3_blind_hi": 0.01, "v3_blind_lo": 0.02,
          "v3_blind_hi@unseen": 0.01, "v3_blind_lo@unseen": 0.02}


def load(subset, prefix="budget"):
    if "+" in subset:  # union of splits, e.g. "kitti_val+kitti_calib"
        return [r for s in subset.split("+") for r in load(s, prefix)]
    if subset.endswith("@unseen"):  # protocol v3, deviation 1: blind pairs that appear in no earlier log
        base = subset[: -len("@unseen")]
        ids = set(json.loads((RESULTS_ROOT / "protocol_v3" / "strictly_unseen.json").read_text())[base])
        return [r for r in load(base, prefix) if r["pair_id"] in ids]
    path = LOG_ROOT / f"{prefix}_{subset}.jsonl"
    if not path.exists():
        return []
    with open(path) as f:
        return [json.loads(x) for x in f if x.strip()]


def trajectory(r, est: str, label: str = "ok15"):
    out, ce, secs, prev_inl = [], 0.0, 0.0, 0
    N_all = max(r["N_all"], 1)
    for k, st in enumerate(r[est]):
        if k == 0 and st["n"] < r["N_all"]:  # truncation needs the ordering (zero for ratio order)
            ce += r.get("ops_order", 0)
            secs += r.get("t_order", 0.0)
        ce += st["ops"]
        secs += st["s"]
        n = max(st["n"], 1)
        agree = float(st["dpose_deg"] < 5 and st["dpose_m"] < 0.2)
        out.append({
            "stage": k, "ok": bool(st[label]), "ok15": bool(st["ok15"]), "ok_rmse": bool(st["ok"]),
            "ce": float(ce), "s": float(secs),
            "log_inl": float(np.log1p(st["inliers"])), "inl_frac": st["inliers"] / n,
            "inl_all_frac": st["inliers_all"] / N_all, "top250_frac": st["inliers_top250"] / min(250, N_all),
            "log_dpose_deg": float(np.log1p(st["dpose_deg"])), "log_dpose_m": float(np.log1p(st["dpose_m"])),
            "agree": agree, "log_N_all": float(np.log(N_all)), "ratio_med": st["ratio_med"],
            "inl_gain": float(st["inliers_all"] - prev_inl) / N_all,
            "log_inl_all": float(np.log1p(st["inliers_all"])),
        })
        prev_inl = st["inliers_all"]
    return out


def _T(st):
    return np.asarray(st["T"], dtype=float).reshape(4, 4)


def trajectory_ladder(r, est: str, ladder: tuple, label: str = "ok15"):
    """Trajectory over a subset of budgets (indices into the logged budgets).

    Only visited budgets are charged; the pose-change signal is computed against the
    previously *visited* budget, exactly as an online system would see it. The ordering
    cost (compatibility order only) is charged once, when a truncated budget is visited;
    a run that only visits the full budget never pays it.

    A budget at or above N_all is the same computation as the first logged full-set
    stage (later entries are logged as free "repeats"). That computation is charged
    exactly once: when it is first visited, whichever entry the ladder visits.
    (Bug fixed 2026-10-17: a repeat entry used to be free even when the ladder had
    skipped the stage holding the real run, so pairs with N_all <= 2,000 got a free
    full budget.)
    """
    out, ce, secs, prev_inl, prev_T = [], 0.0, 0.0, 0, None
    N_all = max(r["N_all"], 1)
    stages = r[est]
    charged = set()
    for k, b in enumerate(ladder):
        st = stages[b]
        if k == 0 and st["n"] < r["N_all"]:
            ce += r.get("ops_order", 0)
            secs += r.get("t_order", 0.0)
        j = b
        if st.get("repeat"):
            j = next(i for i, s in enumerate(stages)
                     if s is not None and s["n"] >= r["N_all"] and not s.get("repeat"))
        if j not in charged:
            charged.add(j)
            ce += stages[j]["ops"]
            secs += stages[j]["s"]
        T = _T(st)
        if prev_T is None:
            ddeg, dm = 180.0, 10.0
        else:
            R = prev_T[:3, :3].T @ T[:3, :3]
            ddeg = float(np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1))))
            dm = float(np.linalg.norm(prev_T[:3, 3] - T[:3, 3]))
        prev_T = T
        n = max(st["n"], 1)
        out.append({
            "stage": k, "ok": bool(st[label]), "ok15": bool(st["ok15"]), "ok_rmse": bool(st["ok"]),
            "ce": float(ce), "s": float(secs),
            "log_inl": float(np.log1p(st["inliers"])), "inl_frac": st["inliers"] / n,
            "inl_all_frac": st["inliers_all"] / N_all, "top250_frac": st["inliers_top250"] / min(250, N_all),
            "log_dpose_deg": float(np.log1p(ddeg)), "log_dpose_m": float(np.log1p(dm)),
            "agree": float(ddeg < 5 and dm < 0.2), "log_N_all": float(np.log(N_all)), "ratio_med": st["ratio_med"],
            "inl_gain": float(st["inliers_all"] - prev_inl) / N_all,
            "log_inl_all": float(np.log1p(st["inliers_all"])),
        })
        prev_inl = st["inliers_all"]
    return out


LADDERS = {
    "doubling": (0, 1, 2, 3, 4),
    "x4": (0, 2, 4),
    "250-2000-4000": (0, 3, 4),
    "250-500-4000": (0, 1, 4),
    "500-2000-4000": (1, 3, 4),
    "250-1000-2000-4000": (0, 2, 3, 4),
    "250-4000": (0, 4),
    "500-4000": (1, 4),
    "250-1000-4000": (0, 2, 4),
}
# Extended candidate set: also ladders that end below the full budget (their last stage is
# a forced stop, so certification has to cover the truncation risk too) and single budgets.
LADDERS_EXT = {
    **LADDERS,
    "250-2000": (0, 3),
    "250-1000-2000": (0, 2, 3),
    "250-500-1000-2000": (0, 1, 2, 3),
    "500-2000": (1, 3),
    "fixed-1000": (2,),
    "fixed-2000": (3,),
    # the standard estimator itself (never stops early): always certifiable, so a selection never comes back
    # empty when the calibration pool is too small to certify anything cheaper (FCGF KITTI); never selected
    # while a cheaper point is certified, so the 3DMatch and KITTI selections are unchanged by it
    "full": (4,),
}


def outcome_summary(o: A.Outcome, recs, eligible_only=False, rmse=False):
    m = np.array([r["rr_eligible"] for r in recs]) if eligible_only else np.ones(len(recs), bool)
    ok = o.ok[m]
    sc = np.array([r["scene"] for r in recs])[m]
    return {"rr": float(ok.mean()), "rr_scene": A.scene_rr(ok, sc), "s": float(o.s[m].mean()),
            "ops": float(o.ce[m].mean()), "n": int(m.sum())}


def paired(o, ref, recs, margin, B=2000):
    sc = np.array([r["scene"] for r in recs])
    a, b = o.ok, ref.ok
    boot = A.stratified_bootstrap(lambda i: b[i].mean() - a[i].mean(), sc, B=B)
    sp = A.stratified_bootstrap(lambda i: ref.s[i].mean() / o.s[i].mean(), sc, B=B, seed=1)
    opr = A.stratified_bootstrap(lambda i: ref.ce[i].mean() / o.ce[i].mean(), sc, B=B, seed=2)
    ub = float(np.quantile(boot, 0.95))
    return {"delta_rr": float(b.mean() - a.mean()), "ub95": ub, "non_inferior": bool(ub < margin),
            "mcnemar_p": A.mcnemar_exact(a, b), "speedup": float(ref.s.mean() / o.s.mean()),
            "speedup_ci": [float(np.quantile(sp, 0.025)), float(np.quantile(sp, 0.975))],
            "ops_ratio": float(ref.ce.mean() / o.ce.mean()),
            "ops_ratio_ci": [float(np.quantile(opr, 0.025)), float(np.quantile(opr, 0.975))],
            "gains": int((a & ~b).sum()), "losses": int((~a & b).sum())}


def main():
    logs = {s: load(s) for s in ["train", "val", "3DMatch", "3DLoMatch"]}
    logs = {s: v for s, v in logs.items() if v}
    print({s: len(v) for s, v in logs.items()})
    out_dir = RESULTS_ROOT / "budget"
    out_dir.mkdir(parents=True, exist_ok=True)
    report = ["# Certified adaptive correspondence budgets (SC²-PCR, TurboReg)\n",
              "Primary metric: RR = RE ≤ 15° and TE ≤ 30 cm, pooled over all pairs (SC²/MAC/TurboReg protocol). "
              "Time: cumulative single-thread wall-clock of the estimator (correspondence construction excluded; "
              "identical for all). Certified on validation with Learn-then-Test (ε = 1 pp, δ = 0.1) against the "
              "full-budget estimator, then evaluated once on test.\n"]
    summary = {}
    for est, name in [("sc2", "SC²-PCR"), ("turbo", "TurboReg")]:
        tr = {s: [trajectory(r, est) for r in logs[s]] for s in logs}
        fit = "train" if "train" in tr else "val"
        X, y = A.rows(tr[fit], FEATURES, "ok")
        clf_now = A.fit_classifier(X, y)
        clf_fin = A.fit_classifier(X, A.final_labels(tr[fit]))
        for s in tr:
            A.attach_scores(tr[s], FEATURES, clf_now, clf_fin)
        mdp = A.MDPController(tr[fit])
        H = len(tr[fit][0])
        # certify on validation against the full budget
        ref_val = A.fixed_stage(tr["val"], H - 1)
        fam_val = {"threshold": [(l, A.threshold_policy(tr["val"], "p_now", l)) for l in LAMBDAS_P],
                   "mdp": [(l, mdp.policy(tr["val"], l)) for l in LAMBDAS_MDP]}
        cert = {}
        for fname, items in fam_val.items():
            idx, _ = A.ltt_select([p for p, _ in items], [o for _, o in items], ref_val.ok, EPS, DELTA)
            cert[fname] = None if idx is None else items[idx][0]
        print(name, "certified:", cert, flush=True)
        summary[est] = {"certified": cert, "sets": {}}
        report.append(f"\n## {name}  (certified: threshold λ = {cert['threshold']}, Markov λ = {cert['mdp']})\n")
        for s in [x for x in ["val", "3DMatch", "3DLoMatch"] if x in tr]:
            recs = logs[s]
            full = A.fixed_stage([trajectory_ladder(r, est, (H - 1,)) for r in recs], 0)  # single full-budget run
            rows = []
            budgets = [st["budget"] for st in recs[0][est]]
            statics = [(f"fixed N={budgets[k]}", A.fixed_stage([trajectory_ladder(r, est, (k,)) for r in recs], 0))
                       for k in range(H)]  # single run at one budget (what fixed-budget methods pay)
            pol = {}
            if cert["threshold"] is not None:
                pol["Adaptive budget, threshold (certified)"] = A.threshold_policy(tr[s], "p_now", cert["threshold"])
            if cert["mdp"] is not None:
                pol["Adaptive budget, Markov (certified)"] = mdp.policy(tr[s], cert["mdp"])
            pol["Oracle budget (upper bound)"] = A.oracle(tr[s])
            margin = MARGIN.get(s, 0.02)
            st_sum = {"static": {}, "policies": {}}
            report.append(f"\n### {s} ({len(recs)} pairs)\n")
            report.append("| Configuration | RR % (15°/30 cm) | official RR % (RMSE) | mean time (ms) | mean ops (M) | "
                          "vs full: ΔRR pp [95% UB] | non-inferior | speed-up [95% CI] | ops reduction |")
            report.append("|---|---|---|---|---|---|---|---|---|")
            for lab, o in statics + list(pol.items()):
                sm = outcome_summary(o, recs)
                o_rmse = A.Outcome(np.array([t[o.stop[i]]["ok_rmse"] for i, t in enumerate(tr[s])]), o.ok15, o.ce, o.s, o.stop)
                rm = outcome_summary(o_rmse, recs, eligible_only=True)
                is_full = lab == f"fixed N={budgets[-1]}"
                cmp = None if is_full else paired(o, full, recs, margin)
                st_sum["static" if lab.startswith("fixed") else "policies"][lab] = {**sm, "rr_rmse_scene": rm["rr_scene"],
                                                                                    "vs_full": cmp}
                c = "" if cmp is None else (f"{100 * cmp['delta_rr']:+.1f} [{100 * cmp['ub95']:+.1f}] | {cmp['non_inferior']} | "
                                            f"{cmp['speedup']:.1f}× [{cmp['speedup_ci'][0]:.1f}, {cmp['speedup_ci'][1]:.1f}] | "
                                            f"{cmp['ops_ratio']:.1f}×")
                if cmp is None:
                    c = "reference | | | "
                report.append(f"| {lab} | {100 * sm['rr']:.2f} | {100 * rm['rr_scene']:.2f} | {1e3 * sm['s']:.0f} | "
                              f"{sm['ops'] / 1e6:.1f} | {c} |")
            summary[est]["sets"][s] = st_sum
        summary[est]["published_reference"] = {"SC²-PCR": {"3DMatch": 83.73, "3DLoMatch": 38.57},
                                               "TurboReg": {"3DMatch": 84.10, "3DLoMatch": 40.99}}
    report.append("\nPublished full-budget results with FPFH (TurboReg paper, Table 1–2): SC²-PCR 83.73 / 38.57, "
                  "TurboReg 84.10 / 40.99 (3DMatch / 3DLoMatch). Our correspondences are recomputed (5 cm FPFH, "
                  "nearest neighbour, top 4,000 by Lowe ratio), so small differences are expected.\n")
    (out_dir / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    with open(out_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=1, default=float)
    print("wrote", out_dir)


if __name__ == "__main__":
    main()
