"""Additional evidence for CAB's guarantee and its stability (compatibility order, selected configurations).

1. Group-wise test risk: the certificate holds per difficulty group, so the test risk of every group should stay
   within 1 %. The worst-case risk over all mixtures of the groups is the largest group risk (Proposition 1); it is
   reported for the group-conditional and for the marginal certificate (groups: those of the group-conditional
   selection, an observable after the first stage).
2. Per-scene test risk and offline speed-up (3DMatch/3DLoMatch scenes, KITTI sequences).
3. Stability: the controller re-fitted on 10 bootstrap resamples of the training pairs, the group-conditional
   thresholds re-certified on the unchanged calibration pool, each evaluated on test (selected ladder).

Settings: FPFH 3DMatch/3DLoMatch, FPFH KITTI, and FCGF 3DMatch/3DLoMatch (controller fitted and certified on the
held-out FCGF pool). Writes results/budget/evidence_extra.{json,md}.
Usage: python -I scripts/evidence_extra.py
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

# protocol v2 (PROTOCOL.md): (fitting, calibration, test sets, selection file, development sets). The worst-case
# mixture and per-scene checks concern the selected configuration itself and cover every test set; the re-fitted
# controllers are other configurations, evaluated on the development benchmarks only.
DATA = {"fpfh_indoor": ("v2_fit", "v2_cal", ["v2_blind_hi", "v2_blind_lo", "3DMatch", "3DLoMatch"],
                        "ladder_selection_compat_ext_v2_indoor_fpfh.json", ["3DMatch", "3DLoMatch"]),
        "fpfh_kitti": ("kitti_train", "kitti_val+kitti_calib", ["kitti_raw_blind", "kitti_test"],
                       "ladder_selection_compat_ext_v2_kitti_fpfh.json", ["kitti_test"]),
        "fcgf_indoor": ("fcgfown_v2_fit", "fcgfown_val", ["fcgfown_3DMatch", "fcgfown_3DLoMatch"],
                        "ladder_selection_compat_ext_v2_indoor_fcgf.json", ["fcgfown_3DMatch", "fcgfown_3DLoMatch"]),
        "fcgf_kitti": ("fcgfown_kitti_fit", "fcgfown_kitti_raw_cal", ["fcgfown_kitti_raw_blind", "fcgfown_kitti_test"],
                       "ladder_selection_compat_ext_v2_kitti_fcgf.json", ["fcgfown_kitti_test"])}
N_BOOT = 10


def outcome(tr_t, mdps, x):
    return S.policy_outcome(tr_t, mdps, x["policy"], x["param"])


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out = {}
    lines = ["# Additional evidence (compatibility order)\n"]
    for dname, (train, val, tests, selfile, dev) in DATA.items():
        sel = json.loads((RESULTS_ROOT / "budget" / selfile).read_text())
        logs = {"train": B.load(train, "budgetc"), "val": B.load(val, "budgetc"), **{t: B.load(t, "budgetc") for t in tests}}
        for est in ("sc2", "turbo"):
            g_sel, m_sel = sel[est]["selected"]["mondrian"], sel[est]["selected"]["marginal"]
            tr_g, mdps_g = S.build(logs, est, B.LADDERS_EXT[g_sel["ladder"]])
            tr_m, mdps_m = S.build(logs, est, B.LADDERS_EXT[m_sel["ladder"]])
            edges = np.array(g_sel["param"]["edges"])
            for t in tests:
                full = A.fixed_stage([B.trajectory_ladder(r, est, (4,)) for r in logs[t]], 0)
                og, om = outcome(tr_g[t], mdps_g, g_sel), outcome(tr_m[t], mdps_m, m_sel)
                groups = S.groups_of(tr_g[t], edges)
                res = {"groups": [], "scenes": {}}
                for gi in range(S.N_GROUPS):
                    m = groups == gi
                    res["groups"].append({"n": int(m.sum()),
                                          "risk_group": float(np.mean(full.ok[m] & ~og.ok[m])) if m.any() else 0.0,
                                          "risk_marginal": float(np.mean(full.ok[m] & ~om.ok[m])) if m.any() else 0.0})
                res["worst_group"] = max(g["risk_group"] for g in res["groups"])
                res["worst_marginal"] = max(g["risk_marginal"] for g in res["groups"])
                scenes = np.array([r["scene"] for r in logs[t]])
                for sc in np.unique(scenes):
                    m = scenes == sc
                    res["scenes"][str(sc)] = {"n": int(m.sum()), "risk": float(np.mean(full.ok[m] & ~og.ok[m])),
                                             "speedup": float(full.s[m].sum() / og.s[m].sum())}
                out.setdefault(dname, {}).setdefault(est, {})[t] = res
                lines.append(f"- {dname} {est} {t}: group risks (CAB) "
                             + ", ".join(f"{100 * g['risk_group']:.2f}% (n={g['n']})" for g in res["groups"])
                             + f"; worst-case mixture CAB {100 * res['worst_group']:.2f}%, marginal "
                             f"{100 * res['worst_marginal']:.2f}%; scenes: max risk "
                             f"{100 * max(v['risk'] for v in res['scenes'].values()):.2f}%, speed-up "
                             f"{min(v['speedup'] for v in res['scenes'].values()):.2f}-"
                             f"{max(v['speedup'] for v in res['scenes'].values()):.2f}x")
            # stability: controller re-fitted on bootstrap resamples of the training pairs
            rng = np.random.default_rng(0)
            boots = {t: [] for t in dev}
            for b in range(N_BOOT):
                idx = rng.integers(0, len(logs["train"]), len(logs["train"]))
                lb = dict(logs, train=[logs["train"][i] for i in idx])
                # same ladder, controller re-fitted, thresholds re-certified (edges from the resampled fitting pairs)
                cfg, (tr, mdps) = S.certify_choice(lb, est, {"ladder": g_sel["chosen"]["ladder"], "policy": "mondrian"})
                for t in dev:
                    full = A.fixed_stage([B.trajectory_ladder(r, est, (4,)) for r in lb[t]], 0)
                    o = S.policy_outcome(tr[t], mdps, cfg["policy"], cfg["param"])
                    boots[t].append({"speedup": float(full.s.sum() / o.s.sum()), "risk": float(np.mean(full.ok & ~o.ok))})
            for t in dev:
                sp = np.array([x["speedup"] for x in boots[t]])
                rk = np.array([x["risk"] for x in boots[t]])
                out[dname][est][t]["bootstrap"] = boots[t]
                lines.append(f"- {dname} {est} {t}: re-fitted controller ({N_BOOT} resamples): speed-up {sp.mean():.2f} "
                             f"[{sp.min():.2f}, {sp.max():.2f}], risk max {100 * rk.max():.2f}%")
            print(f"  {dname} {est} done", flush=True)
    (RESULTS_ROOT / "budget" / "evidence_extra.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    (RESULTS_ROOT / "budget" / "evidence_extra.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
