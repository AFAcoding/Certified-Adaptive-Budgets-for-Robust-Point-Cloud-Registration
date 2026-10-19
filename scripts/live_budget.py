"""Live single-process benchmark: adaptive correspondence budget vs. full-budget SC^2 / TurboReg.

Uses the validation-selected group-conditional (Mondrian) configuration from
results/budget/ladder_selection{,_compat}{,_ext}{,_kitti}.json. For each sampled test pair it
times, in one process: the standard estimator on the full budget (N = 4,000) and the adaptive
version of every requested configuration (budgets run lazily, controller decides after each
one; the compatibility ordering, if used, is timed as part of the adaptive run).
The order of the runs rotates from pair to pair so that cache warm-up favours none.
It also checks that the live stopping decision equals the offline one from the logs.

Usage: python -I -u scripts/live_budget.py [--per-set 100] [--prefixes budget,budgetc]
                                           [--ladders base|extended] [--dataset 3dmatch|kitti]
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_budget as B  # noqa: E402
import select_ladder as S  # noqa: E402

from acpr import RESULTS_ROOT  # noqa: E402
from acpr import analysis as A  # noqa: E402
from acpr import kitti as K  # noqa: E402
from acpr.data import load_pairs  # noqa: E402
from acpr.estimators import compat_order, nn_correspondences, nn_correspondences_bf, sc2_pcr, turboreg  # noqa: E402
from acpr.experiment import info_and_eligibility  # noqa: E402
from acpr.features import get_fpfh  # noqa: E402
from acpr.metrics import evaluate_transform  # noqa: E402

FNS = {"sc2": sc2_pcr, "turbo": turboreg}
BUDGETS = [250, 500, 1000, 2000, 4000]


class ThreeDMatch:
    name, tests, inlier, compat_thr, suffix = "3dmatch", ["3DMatch", "3DLoMatch"], 0.10, 0.10, ""
    train, val = "train", "val"

    def pairs(self, subset):
        return load_pairs(subset)

    def features(self, pcd):
        return get_fpfh(pcd)

    def kwargs(self, est):
        return {}

    def info(self, pair):
        return info_and_eligibility(pair)[0]

    def ok(self, pair, T, info):
        return bool(evaluate_transform(pair.transform, T, info)["ok_rre_rte"])

    def corr(self, sp, sf, rp, rf):
        return nn_correspondences(sp, sf, rp, rf)

    def features_pair(self, pair):
        rp, rf, _ = self.features(pair.pcd0)
        sp, sf, _ = self.features(pair.pcd1)
        return rp, rf, sp, sf

    outtag = ""


class Kitti(ThreeDMatch):
    name, tests, inlier, suffix = "kitti", ["kitti_test"], 0.60, "_kitti"
    train, val = "kitti_train", "kitti_val+kitti_calib"

    def __init__(self):
        thr = json.loads((RESULTS_ROOT / "kitti" / "thresholds.json").read_text())
        self.compat_thr = thr["sc2_d_thre"]
        self.kw = {"sc2": {"d_thre": thr["sc2_d_thre"], "inlier_thr": 0.6, "nms_radius": 0.6},
                   "turbo": {"tau": thr["turbo_tau"], "inlier_thr": 0.6}}

    def pairs(self, subset):
        return K.load_kitti_pairs("test")

    def features(self, pcd):
        return K.get_fpfh_kitti(pcd)

    def kwargs(self, est):
        return self.kw[est]

    def info(self, pair):
        return None

    def ok(self, pair, T, info):
        return K.success(pair.transform, T)[0]

    def corr(self, sp, sf, rp, rf):  # same as the KITTI logs (exact NN by brute force)
        return nn_correspondences_bf(sp, sf, rp, rf)

    outtag = "_kitti"


class FcgfThreeDMatch(ThreeDMatch):
    """FCGF test correspondences; controller fitted and certified on FPFH (transfer)."""
    name, tests, outtag = "fcgf3dmatch", ["fcgf_3DMatch", "fcgf_3DLoMatch"], "_fcgf3dmatch"

    def pairs(self, subset):
        from acpr import fcgf as F
        return F.load_fcgf_3dmatch_pairs(subset.replace("fcgf_", ""))

    def features_pair(self, pair):
        from acpr import fcgf as F
        return F.features_3dmatch(pair)

    def corr(self, sp, sf, rp, rf):  # same as the FCGF logs
        return nn_correspondences_bf(sp, sf, rp, rf)


class FcgfKitti(Kitti):
    name, tests, outtag = "fcgfkitti", ["fcgf_kitti_test"], "_fcgfkitti"

    def pairs(self, subset):
        from acpr import fcgf as F
        return F.load_fcgf_kitti_pairs()

    def features_pair(self, pair):
        from acpr import fcgf as F
        return F.features_kitti(pair)


def stage_record(fn, kw, P, Q, Po, Qo, ratio_o, n, prev_T, info, pair, ds):
    """Run the estimator on the first n of the ordered correspondences (Po, Qo)."""
    T, inf = fn(Po[:n], Qo[:n], **kw)
    res_all = np.linalg.norm(P @ T[:3, :3].T + T[:3, 3] - Q, axis=1)  # ratio order, as in the logs
    if prev_T is None:
        ddeg, dm = 180.0, 10.0
    else:
        R = prev_T[:3, :3].T @ T[:3, :3]
        ddeg = float(np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1))))
        dm = float(np.linalg.norm(prev_T[:3, 3] - T[:3, 3]))
    ok = ds.ok(pair, T, info)
    return T, {"n": n, "s": 0.0, "ops": inf.get("ops", 0), "inliers": inf.get("inliers", 0),
               "inliers_all": int((res_all < ds.inlier).sum()), "inliers_top250": int((res_all[:250] < ds.inlier).sum()),
               "ratio_med": float(np.median(ratio_o[:n])), "ok": ok, "ok15": ok,
               "dpose_deg": ddeg, "dpose_m": dm, "T": T.reshape(-1).tolist()}


class Controller:
    def __init__(self, prefix, est, ladders, ds):
        suffix = S.SUFFIX[prefix] + ("" if ladders == "base" else "_ext") + ds.suffix
        sel = json.loads((RESULTS_ROOT / "budget" / f"ladder_selection{suffix}.json").read_text())
        cfg = sel[est]["selected"]["mondrian"]
        self.prefix, self.est, self.ds, self.ladder_name = prefix, est, ds, cfg["ladder"]
        self.ladder = B.LADDERS_EXT[cfg["ladder"]]
        self.edges, self.lams = np.array(cfg["param"]["edges"]), cfg["param"]["lambdas"]
        logs = {"train": B.load(ds.train, prefix), "val": B.load(ds.val, prefix)}
        tr, _ = S.build(logs, est, self.ladder)
        X, y = A.rows(tr["train"], B.FEATURES, "ok")
        self.clf_now = A.fit_classifier(X, y)
        self.clf_fin = A.fit_classifier(X, A.final_labels(tr["train"]))

    def run(self, fn, P, Q, ratio, info, pair):
        """Adaptive run (timed by the caller). Returns (T, stop stage)."""
        kw = self.ds.kwargs(self.est)
        N_all = P.shape[0]
        if self.prefix == "budgetc" and BUDGETS[self.ladder[0]] < N_all:
            perm, _ = compat_order(P, Q, thr=self.ds.compat_thr)
            Po, Qo, ratio_o = P[perm], Q[perm], ratio[perm]
        else:
            Po, Qo, ratio_o = P, Q, ratio
        rec = {"N_all": N_all, self.est: [None] * 5}
        prev_T, group, prev_st = None, None, None
        for k, b in enumerate(self.ladder):
            n = min(BUDGETS[b], N_all)
            if prev_st is not None and n == prev_st["n"]:
                # same input as the previous budget (both cover all correspondences):
                # nothing to recompute, exactly like a logged repeat
                st = {**prev_st, "repeat": True, "ops": 0}
            else:
                if n >= N_all:  # full set: the standard input order
                    Po, Qo, ratio_o = P, Q, ratio
                prev_T, st = stage_record(fn, kw, P, Q, Po, Qo, ratio_o, n, prev_T, info, pair, self.ds)
            prev_st = st
            rec[self.est][b] = st
            traj = B.trajectory_ladder(rec, self.est, self.ladder[: k + 1])
            x = np.array([[traj[-1][f] for f in B.FEATURES]])
            pn = float(self.clf_now.predict_proba(x)[0, 1])
            if group is None:
                group = int(np.searchsorted(self.edges, traj[0]["log_inl_all"], side="right"))
            if pn >= self.lams[group] or k == len(self.ladder) - 1:
                return prev_T, k
        return prev_T, len(self.ladder) - 1

    def offline_stop(self, rec):
        tro = B.trajectory_ladder(rec, self.est, self.ladder)
        A.attach_scores([tro], B.FEATURES, self.clf_now, self.clf_fin)
        g = int(np.searchsorted(self.edges, tro[0]["log_inl_all"], side="right"))
        return next((st["stage"] for st in tro if st["p_now"] >= self.lams[g]), len(tro) - 1)


def make_dataset(name, recal=False, refit=False):
    ds = {"3dmatch": ThreeDMatch, "kitti": Kitti, "fcgf3dmatch": FcgfThreeDMatch, "fcgfkitti": FcgfKitti}[name]()
    if recal:  # FCGF: configuration re-certified on the held-out FCGF pairs instead of transferred from FPFH
        assert ds.name.startswith("fcgf"), "--recal applies to the FCGF datasets"
        ds.suffix, ds.val, ds.outtag = f"_{ds.name}", S.DATASETS[ds.name]["val"], ds.outtag + "_recal"
    if refit:  # FCGF: controller re-fitted and re-certified on disjoint parts of the held-out FCGF pool
        key = f"{ds.name}_refit"
        assert key in S.DATASETS, f"no re-fit protocol for {ds.name}"
        ds.suffix, ds.train, ds.val = f"_{key}", S.DATASETS[key]["train"], S.DATASETS[key]["val"]
        ds.outtag += "_refit"
    return ds


def time_pair(ds, est, ctrls, p, jobs, offline):
    """Time, on pair p and in the order `jobs`, the standard estimator ("full") and the adaptive configurations."""
    fn, kw = FNS[est], ds.kwargs(est)
    info = ds.info(p)
    rp, rf, sp, sf = ds.features_pair(p)
    P, Q, ratio = ds.corr(sp, sf, rp, rf)
    N_all = min(P.shape[0], 4000)
    P, Q, ratio = P[:N_all], Q[:N_all], ratio[:N_all]
    out = {}
    for job in jobs:
        t0 = time.perf_counter()
        if job == "full":  # standard estimator: one full-budget run
            T, _ = fn(P, Q, **kw)
            stop = None
        else:
            T, stop = ctrls[job].run(fn, P, Q, ratio, info, p)
        secs = time.perf_counter() - t0
        out[job] = {"s": secs, "ok": ds.ok(p, T, info), "stop": stop}
        if job != "full":
            out[job]["offline_stop"] = ctrls[job].offline_stop(offline[job][p.pair_id])
    return out


def summary(rows, ds, prefixes):
    print("\nlive single-process benchmark (adaptive budget vs. standard full-budget estimator):")
    for est in ["sc2", "turbo"]:
        for subset in ds.tests:
            rs = [r for r in rows if r["est"] == est and r["subset"] == subset]
            sc = np.array([r["scene"] for r in rs])
            b = np.array([r["full"]["ok"] for r in rs])
            tb = np.array([r["full"]["s"] for r in rs])
            line = f"  {est:5s} {subset:10s} n={len(rs)}: full {1e3 * tb.mean():6.0f} ms RR {100 * b.mean():5.1f}%"
            for pf in prefixes:
                a = np.array([r[pf]["ok"] for r in rs])
                ta = np.array([r[pf]["s"] for r in rs])
                sp = A.stratified_bootstrap(lambda i: tb[i].mean() / ta[i].mean(), sc, B=2000, seed=1)
                agree = np.mean([r[pf]["stop"] == r[pf]["offline_stop"] for r in rs])
                line += (f" | {pf}: {1e3 * ta.mean():6.0f} ms RR {100 * a.mean():5.1f}% speed-up "
                         f"{tb.mean() / ta.mean():.2f}x [{np.quantile(sp, .025):.2f}, {np.quantile(sp, .975):.2f}] "
                         f"agree {100 * agree:.0f}%")
            print(line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-set", type=int, default=100)
    ap.add_argument("--prefixes", default="budget")
    ap.add_argument("--ladders", default="base", choices=["base", "extended"])
    ap.add_argument("--dataset", default="3dmatch", choices=["3dmatch", "kitti", "fcgf3dmatch", "fcgfkitti"])
    ap.add_argument("--recal", action="store_true", help="FCGF: use the selection re-certified on FCGF")
    ap.add_argument("--refit", action="store_true", help="FCGF: controller re-fitted and re-certified on FCGF")
    args = ap.parse_args()
    prefixes = args.prefixes.split(",")
    ds = make_dataset(args.dataset, args.recal, args.refit)
    sys.stdout.reconfigure(encoding="utf-8")
    rows = []
    for est in ["sc2", "turbo"]:
        ctrls = {pf: Controller(pf, est, args.ladders, ds) for pf in prefixes}
        for subset in ds.tests:
            offline = {pf: {r["pair_id"]: r for r in B.load(subset, pf)} for pf in prefixes}
            ids = set.intersection(*[set(v) for v in offline.values()])
            pairs = [p for p in ds.pairs(subset) if p.pair_id in ids]
            rng = np.random.default_rng(0)
            pairs = [pairs[i] for i in sorted(rng.choice(len(pairs), min(args.per_set, len(pairs)), replace=False))]
            for j, p in enumerate(pairs):
                jobs = ["full"] + prefixes
                jobs = jobs[j % len(jobs):] + jobs[: j % len(jobs)]
                row = {"est": est, "subset": subset, "pair_id": p.pair_id, "scene": p.scene, "run_order": jobs}
                row.update(time_pair(ds, est, ctrls, p, jobs, offline))
                rows.append(row)
            print(f"  {est} {subset}: done", flush=True)
    if prefixes == ["budget"] and args.ladders == "base" and ds.name == "3dmatch":
        name = "live_budget.json"
    else:
        name = f"live_budget_compare{'' if args.ladders == 'base' else '_ext'}{ds.outtag}.json"
    with open(RESULTS_ROOT / "budget" / name, "w") as f:
        json.dump(rows, f, indent=1)
    summary(rows, ds, prefixes)


if __name__ == "__main__":
    main()
