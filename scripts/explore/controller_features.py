"""Exploration (fitting, calibration and development data only): do extra per-stage signals let the certified
controller stop earlier at the same risk?

Feature sets (added to analyze_budget.FEATURES for every visited stage of a multi-stage ladder):
  base     the paper's features
  verify   + geometric verification of the stage's pose (scripts/explore/verify_features.py): vfit, vfit2,
           vrmse / tau and the change of vfit since the previous visited stage
  geom     + correspondence-geometry uncertainty of the stage's pose (scripts/explore/geom_features.py)
  both     verify + geom
The measured single-thread cost of the extra signals is added to every visited stage (never to the full budget run
alone). The whole choose-then-certify pipeline of select_ladder.py runs unchanged (classifier fixed, default: boosted
trees, the kind v3 chose for this dataset), without the gate, so that only the controller's signals differ.

Usage: python -I scripts/explore/controller_features.py <feature set> <estimator> [classifier]
Writes results/explore/controller_features_<set>_<estimator>.json
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
SPLITS = {"v2_fit", "v2_cal", "3DMatch", "3DLoMatch"}
TAU = 0.10


def load(kind):
    out = {}
    for s in SPLITS:
        path = RESULTS_ROOT / "explore" / f"{kind}_{s}.jsonl"
        for line in open(path):
            r = json.loads(line)
            out[r["pair_id"]] = r
    return out


def main():
    fset, est = sys.argv[1], sys.argv[2]
    A.CLASSIFIER = sys.argv[3] if len(sys.argv) > 3 else "hgb"
    V = load("verify") if fset in ("verify", "both") else {}
    Gm = load("geom") if fset in ("geom", "both") else {}
    extra = (["vfit", "vfit2", "vrmse", "dvfit"] if V else []) + \
            (["g_lmin", "g_lratio", "g_hess_logdet", "g_hess_lmin", "g_inl_spread"] if Gm else [])
    B.FEATURES = B.FEATURES + extra
    orig = B.trajectory_ladder

    def traj(r, e, ladder, label="ok15"):
        out = orig(r, e, ladder, label)
        if not extra:
            return out
        charge = len(ladder) > 1  # a single run (e.g. the full budget, the reference) never needs the signals
        v, g = V[r["pair_id"]] if V else None, Gm[r["pair_id"]] if Gm else None
        add, prev = 0.0, None
        for k, b in enumerate(ladder):
            st = out[k]
            if v is not None:
                add += (v["t_tree"] if k == 0 else 0.0) + v[e]["t_query"][b]
                st["vfit"], st["vfit2"] = v[e]["vfit"][b], v[e]["vfit2"][b]
                st["vrmse"] = v[e]["vrmse"][b] / TAU
                st["dvfit"] = 0.0 if prev is None else st["vfit"] - prev
                prev = st["vfit"]
            if g is not None:
                add += g[e]["t"][b]
                for f in ("g_lmin", "g_lratio", "g_hess_logdet", "g_hess_lmin", "g_inl_spread"):
                    st[f] = g[e][f][b]
            if charge:
                st["s"] += add
        return out

    B.trajectory_ladder = traj
    D = S.DATASETS[FAM]
    logs = {"train": B.load(D["train"], "budgetc"), "val": B.load(D["val"], "budgetc"),
            **{s: B.load(s, "budgetc") for s in DEV}}
    selected, rows, built = S.select_and_certify(logs, est, B.LADDERS_EXT, families=("mondrian",),
                                                 controller=A.CLASSIFIER)
    x = selected["mondrian"]
    tr, mdps = built["mondrian"]
    # fitting-pair cost of the chosen candidate, out-of-fold, with its spread over pairs (for the 1-SE rule)
    chosen = S.choose(rows, "mondrian")
    res = {"features": B.FEATURES, "classifier": A.CLASSIFIER, "ladder": x["ladder"], "param": x["param"],
           "fit_s": x["fit_s"], "fit_s_se": chosen.get("fit_s_se"), "test": {}, "test_gate": {}}
    gate = S.fit_gate_for(logs, {"train": D["train"], "val": D["val"]}, est, x, (tr, mdps), "budgetc")
    res["gate"] = {"kind": gate.kind, "threshold": gate.threshold,
                   "fitcal_saving": 1 - gate.oof_total / gate.cab_total}  # out-of-fold, fitting + calibration pairs
    for s in DEV:
        full = A.fixed_stage([orig(r, est, (4,)) for r in logs[s]], 0)
        o = S.policy_outcome(tr[s], mdps, x["policy"], x["param"])
        for key, oo in (("test", o), ("test_gate", None)):
            if key == "test_gate":
                if gate.clf is None:
                    oo = o
                else:
                    gated = gate.predict(S.load_gate_features(s, logs[s])[0])
                    oo = S.gated_outcome(o, full, gated, S.gate_eval_charges(logs[s], "budgetc", gate.kind))
            cmp = B.paired(oo, full, logs[s], B.MARGIN[s])
            res[key][s] = {"speedup": cmp["speedup"], "speedup_ci": cmp["speedup_ci"], "ops": cmp["ops_ratio"],
                           "risk": float(np.mean(full.ok & ~oo.ok)), "ub95": cmp["ub95"],
                           "non_inferior": cmp["non_inferior"],
                           "stop_hist": np.bincount(np.clip(oo.stop, 0, None),
                                                    minlength=len(B.LADDERS_EXT[x["ladder"]])).tolist()}
    print(fset, est, A.CLASSIFIER, x["ladder"], f"fit {1e3 * x['fit_s']:.0f} ms",
          {s: (round(v["speedup"], 2), round(100 * v["risk"], 2), v["stop_hist"]) for s, v in res["test"].items()},
          flush=True)
    (RESULTS_ROOT / "explore" / f"controller_features_{fset}_{est}_{A.CLASSIFIER}.json").write_text(
        json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
