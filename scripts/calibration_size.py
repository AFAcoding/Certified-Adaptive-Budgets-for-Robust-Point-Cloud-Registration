"""How many calibration pairs does a certificate need? Certification on random subsets of the calibration pool.

For FPFH 3DMatch (pool: the 1,331 validation pairs; tests: 3DMatch, 3DLoMatch) and KITTI (pool: 180 validation +
1,058 held-out training pairs; test: KITTI test), with CAB's selected configuration (compatibility order, the ladder
selected on the full pool), the stopping thresholds are re-certified on random subsets of n calibration pairs
(20 repetitions per n) with the group-conditional (Mondrian, 3 groups, delta/3 each) and the marginal certificate
(threshold family, delta). Each certificate is evaluated once on the test sets: certified or not (a group without a
certified threshold never stops early), offline speed-up over the full budget, and risk.

Writes results/budget/calibration_size.{json,md}.
Usage: python -I scripts/calibration_size.py
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

# protocol v2 (PROTOCOL.md); evaluated on the development benchmarks only, never on the blind tests
DATA = {"3dmatch": ("v2_fit", "v2_cal", ["3DMatch", "3DLoMatch"], "ladder_selection_compat_ext_v2_indoor_fpfh.json"),
        "kitti": ("kitti_train", "kitti_val+kitti_calib", ["kitti_test"], "ladder_selection_compat_ext_v2_kitti_fpfh.json")}
SIZES = [100, 200, 300, 450, 600, 900, 1200, 1800, 2400]
REPS = 20


def certify_mondrian(trv, ref_ok, edges):
    gv = S.groups_of(trv, edges)  # edges from the fitting pairs, fixed for every subset
    lams = []
    for gi in range(S.N_GROUPS):
        sub = [t for t, g in zip(trv, gv) if g == gi]
        items = [(lam, A.threshold_policy(sub, "p_now", lam)) for lam in B.LAMBDAS_P]
        idx, _ = A.ltt_select([p for p, _ in items], [o for _, o in items], ref_ok[gv == gi], B.EPS, B.DELTA / S.N_GROUPS)
        lams.append(items[idx][0] if idx is not None else 1.01)
    return {"edges": edges.tolist(), "lambdas": lams}


def certify_marginal(trv, ref_ok):
    items = [(lam, A.threshold_policy(trv, "p_now", lam)) for lam in B.LAMBDAS_P]
    idx, _ = A.ltt_select([p for p, _ in items], [o for _, o in items], ref_ok, B.EPS, B.DELTA)
    return items[idx][0] if idx is not None else 1.01


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out = {}
    lines = ["# Calibration size: certification on random subsets of the calibration pool\n",
             "Per n: share of the 20 subsets that certify any early stop, median offline speed-up [quartiles], mean and "
             "maximum test risk, share of subsets whose test risk exceeds 1 %.\n",
             "| data | estimator | test | certificate | n | certified | speed-up | risk mean / max % | risk > 1 % |",
             "|---|---|---|---|---|---|---|---|---|"]
    for dname, (train, val, tests, selfile) in DATA.items():
        sel = json.loads((RESULTS_ROOT / "budget" / selfile).read_text())
        for est in ("sc2", "turbo"):
            ladder = sel[est]["selected"]["mondrian"]["ladder"]
            logs = {"train": B.load(train, "budgetc"), "val": B.load(val, "budgetc"), **{t: B.load(t, "budgetc") for t in tests}}
            tr, mdps = S.build(logs, est, B.LADDERS_EXT[ladder])
            ref = S.full_ok(logs["val"], est)
            edges = S.group_edges(tr["train"])
            full = {t: A.fixed_stage([B.trajectory_ladder(r, est, (4,)) for r in logs[t]], 0) for t in tests}
            rng = np.random.default_rng(0)
            pool = len(tr["val"])
            for n in [s for s in SIZES if s < pool] + [pool]:
                reps = REPS if n < pool else 1
                for rep in range(reps):
                    idx = np.sort(rng.choice(pool, n, replace=False))
                    trv = [tr["val"][i] for i in idx]
                    certs = {"mondrian": certify_mondrian(trv, ref[idx], edges), "marginal": certify_marginal(trv, ref[idx])}
                    for tag, param in certs.items():
                        certified = (min(param["lambdas"]) < 1.01) if tag == "mondrian" else (param < 1.01)
                        for t in tests:
                            # nothing certified: the full budget (as in select_ladder.certify_choice)
                            o = (full[t] if not certified else
                                 S.mondrian_policy(tr[t], np.array(param["edges"]), param["lambdas"]) if tag == "mondrian"
                                 else A.threshold_policy(tr[t], "p_now", param))
                            f = full[t]
                            rec = {"certified": bool(certified), "speedup": float(f.s.sum() / o.s.sum()),
                                   "risk": float(np.mean(f.ok & ~o.ok)), "loss": float(f.ok.mean() - o.ok.mean())}
                            out.setdefault(dname, {}).setdefault(est, {}).setdefault(t, {}).setdefault(tag, {}) \
                                .setdefault(str(n), []).append(rec)
                print(f"  {dname} {est} n={n} done", flush=True)
            for t in tests:
                for tag in ("mondrian", "marginal"):
                    for n, recs in out[dname][est][t][tag].items():
                        sp = np.array([r["speedup"] for r in recs])
                        rk = 100 * np.array([r["risk"] for r in recs])
                        cert = np.mean([r["certified"] for r in recs])
                        lines.append(f"| {dname} | {est} | {t} | {tag} | {n} | {100 * cert:.0f} % | {np.median(sp):.2f} "
                                     f"[{np.quantile(sp, 0.25):.2f}, {np.quantile(sp, 0.75):.2f}] | {rk.mean():.2f} / "
                                     f"{rk.max():.2f} | {100 * np.mean(rk > 1):.0f} % |")
    (RESULTS_ROOT / "budget" / "calibration_size.json").write_text(json.dumps(out), encoding="utf-8")
    (RESULTS_ROOT / "budget" / "calibration_size.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
