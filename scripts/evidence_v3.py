"""Additional evidence for the final method (protocol v3; compatibility order, group-conditional certificate).

1. Per scene, fresh blind test: pairs, offline speed-up of the final method and of CAB without the gate, risk, share of
   pairs gated. (The same single evaluation, broken down; no configuration is chosen.)
2. Per difficulty group, every test set: the realized risk of the final method in each certified group, i.e. the
   risk of the worst mixture of easy and hard pairs.
3. Bootstrap re-fits (development benchmarks only): the final method's controller and gate re-fitted on 10 bootstrap
   resamples of the fitting pairs (classifier kind as chosen), re-certified on the calibration pairs and evaluated on
   3DMatch / 3DLoMatch: speed-up range and largest risk.

Usage: python -I scripts/evidence_v3.py
Writes results/budget/evidence_v3.json
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

RB = RESULTS_ROOT / "budget"
FAMS = {"v3_indoor_fpfh": ["v3_blind_hi", "v3_blind_lo"],
        "v2_indoor_fpfh": ["v2_blind_hi", "v2_blind_lo", "3DMatch", "3DLoMatch"],
        "v2_kitti_fpfh": ["kitti_raw_blind", "kitti_test"],
        "v2_indoor_fcgf": ["fcgfown_3DMatch", "fcgfown_3DLoMatch"]}


def outcomes(fam, est, cfg, logs, tests):
    """Per-pair outcome of the final method (and of its ungated policy) on every test set, with the groups."""
    D = S.DATASETS[fam]
    A.CLASSIFIER = cfg["classifier"]
    ladder = B.LADDERS_EXT[cfg["ladder"]]
    tr, mdps = S.build(logs, est, ladder)
    gate = S.fit_gate_for(logs, D, est, cfg, (tr, mdps), "budgetc")
    A.CLASSIFIER = "logit"
    edges = np.array(cfg["param"]["edges"])
    out = {}
    for t in tests:
        o = S.policy_outcome(tr[t], mdps, cfg["policy"], cfg["param"])
        full = A.fixed_stage([B.trajectory_ladder(r, est, (4,)) for r in logs[t]], 0)
        gated = np.zeros(len(logs[t]), bool)
        if gate.clf is not None:
            gated = gate.predict(S.load_gate_features(t, logs[t])[0])
            o = S.gated_outcome(o, full, gated, S.gate_eval_charges(logs[t], "budgetc", gate.kind))
        out[t] = {"o": o, "full": full, "gated": gated, "groups": S.groups_of(tr[t], edges),
                  "scene": np.array([r["scene"] for r in logs[t]])}
    return out


def main():
    res = {"per_scene": {}, "groups": {}, "refit": {}}
    for fam, tests in FAMS.items():
        D = S.DATASETS[fam]
        logs = {"train": B.load(D["train"], "budgetc"), "val": B.load(D["val"], "budgetc"),
                **{t: B.load(t, "budgetc") for t in tests}}
        v3 = json.loads((RB / f"ladder_selection_compat_ext_{fam}_ctlauto_gate.json").read_text())
        v2 = json.loads((RB / f"ladder_selection_compat_ext_{fam}.json").read_text())
        for est in ("sc2", "turbo"):
            cfg = v3[est]["selected"]["mondrian"]
            if cfg["ladder"] == "full":
                continue
            out = outcomes(fam, est, cfg, logs, tests)
            for t, x in out.items():  # 2. group-wise risks
                rs = []
                for g in np.unique(x["groups"]):
                    m = x["groups"] == g
                    rs.append({"group": int(g), "n": int(m.sum()),
                               "risk": float(np.mean(x["full"].ok[m] & ~x["o"].ok[m])),
                               "lost": int((x["full"].ok[m] & ~x["o"].ok[m]).sum())})
                res["groups"].setdefault(t, {})[est] = rs
            if fam == "v3_indoor_fpfh":  # 1. per scene, fresh blind test (with the ungated configuration of v2)
                cfg2 = v2[est]["selected"]["mondrian"]
                tr2, mdps2 = S.build(logs, est, B.LADDERS_EXT[cfg2["ladder"]])
                for t, x in out.items():
                    o2 = S.policy_outcome(tr2[t], mdps2, cfg2["policy"], cfg2["param"])
                    rows = []
                    for sc in np.unique(x["scene"]):
                        m = x["scene"] == sc
                        rows.append({"scene": str(sc), "n": int(m.sum()),
                                     "speed_v3": float(x["full"].s[m].mean() / x["o"].s[m].mean()),
                                     "speed_v2": float(x["full"].s[m].mean() / o2.s[m].mean()),
                                     "risk_v3": float(np.mean(x["full"].ok[m] & ~x["o"].ok[m])),
                                     "risk_v2": float(np.mean(x["full"].ok[m] & ~o2.ok[m])),
                                     "gated": float(x["gated"][m].mean())})
                    res["per_scene"].setdefault(t, {})[est] = rows
            if fam == "v2_indoor_fpfh":  # 3. bootstrap re-fits, development benchmarks only
                rng = np.random.default_rng(0)
                runs = []
                for b in range(10):
                    idx = rng.integers(0, len(logs["train"]), len(logs["train"]))
                    lb = {**logs, "train": [logs["train"][i] for i in idx]}
                    sel, _, built = S.select_and_certify(lb, est, B.LADDERS_EXT, families=("mondrian",),
                                                         controller=cfg["classifier"])
                    c = sel["mondrian"]
                    c["classifier"] = cfg["classifier"]
                    tr, mdps = built["mondrian"]
                    A.CLASSIFIER = cfg["classifier"]
                    gate = S.fit_gate_for(lb, D, est, c, (tr, mdps), "budgetc")
                    A.CLASSIFIER = "logit"
                    r = {"ladder": c["ladder"]}
                    for t in ("3DMatch", "3DLoMatch"):
                        o = S.policy_outcome(tr[t], mdps, c["policy"], c["param"])
                        full = A.fixed_stage([B.trajectory_ladder(q, est, (4,)) for q in logs[t]], 0)
                        if gate.clf is not None:
                            g = gate.predict(S.load_gate_features(t, logs[t])[0])
                            o = S.gated_outcome(o, full, g, S.gate_eval_charges(logs[t], "budgetc", gate.kind))
                        r[t] = {"speed": float(full.s.mean() / o.s.mean()), "risk": float(np.mean(full.ok & ~o.ok))}
                    runs.append(r)
                    print(est, "refit", b, r, flush=True)
                res["refit"][est] = runs
        print(fam, "done", flush=True)
    (RB / "evidence_v3.json").write_text(json.dumps(res, indent=1))
    print("written")


if __name__ == "__main__":
    main()
