"""Export the GPU timing bundle (PROTOCOL.md, addendum C): for every timed test set, the same 300 random pairs as the CPU
live timing (scripts/live_budget.py), their correspondences and ground truth, and for every estimator the two
certified configurations (CAB without the gate, the final method) with their controllers and gates as plain arrays.

Nothing is trained for the bundle: the controllers and gates are those of the certified configurations, refitted
deterministically from the same logs exactly as the CPU live timing does, and this script checks that the exported
arrays reproduce the fitted classifiers' probabilities and the logged stopping decisions on every exported pair.

Usage: python -I gpu/export_bundle.py [--out gpu_bundle] [--sets th,tl,m,lo,ki,fm] [--per-set 300]
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gpu"))
import analyze_budget as B  # noqa: E402
import live_budget as L  # noqa: E402
from acpr import analysis as A  # noqa: E402

import cab_gpu  # noqa: E402

# test set -> (log subset, dataset of select_ladder.DATASETS)
SETS = {"th": ("v3_blind_hi", "v3_indoor_fpfh"), "tl": ("v3_blind_lo", "v3_indoor_fpfh"),
        "bh": ("v2_blind_hi", "v2_indoor_fpfh"), "bl": ("v2_blind_lo", "v2_indoor_fpfh"),
        "m": ("3DMatch", "v2_indoor_fpfh"), "lo": ("3DLoMatch", "v2_indoor_fpfh"),
        "kr": ("kitti_raw_blind", "v2_kitti_fpfh"), "ki": ("kitti_test", "v2_kitti_fpfh"),
        "fm": ("fcgfown_3DMatch", "v2_indoor_fcgf"), "flo": ("fcgfown_3DLoMatch", "v2_indoor_fcgf"),
        # fitting pairs, for smoke tests of the GPU code only (never timed for the paper)
        "fit": ("v3_fit", "v3_indoor_fpfh"), "kfit": ("kitti_train", "v2_kitti_fpfh")}
JOBS = {"v2": "budgetc", "v3": "budgetc+v3"}


def wait_if_live():
    """Live timing needs an otherwise idle machine: wait while a live timing or re-timing process runs."""
    import psutil
    while any(any(k in " ".join(q.info["cmdline"] or []) for k in ("live_budget.py", "retime_stalls.py"))
              for q in psutil.process_iter(["cmdline"])):
        time.sleep(30)


def subset_pairs(ds, subset):
    if subset in ("kitti_train", "kitti_val"):  # odometry fitting / validation pairs (smoke tests)
        from acpr import kitti as K
        ds._current = subset  # features_pair dispatches on the subset being served
        return K.load_kitti_pairs(subset[len("kitti_"):])
    return ds.pairs(subset)


def export_clf(clf):
    """(spec, arrays) of a fitted controller or gate classifier."""
    from sklearn.pipeline import Pipeline
    if isinstance(clf, A._Constant):
        return {"kind": "constant", "p": float(clf.p)}, {}
    if isinstance(clf, Pipeline):
        steps = [s for _, s in clf.steps]
        lr = steps[-1]
        arrays = {"mean": steps[0].mean_, "scale": steps[0].scale_, "coef": lr.coef_[0],
                  "intercept": np.array(lr.intercept_[0])}
        if len(steps) == 4:  # quadratic logistic: scaler, polynomial features, scaler, logistic regression
            arrays.update(powers=steps[1].powers_.astype(np.float64), mean2=steps[2].mean_, scale2=steps[2].scale_)
        return {"kind": "logistic"}, arrays
    trees = [p[0].nodes for p in clf._predictors]  # HistGradientBoostingClassifier, binary
    for nd in trees:
        assert not nd["is_categorical"].any()
    offsets = np.concatenate([[0], np.cumsum([len(nd) for nd in trees])])
    cat = np.concatenate(trees)
    return ({"kind": "trees", "n_trees": len(trees)},
            {"baseline": np.array(float(np.ravel(clf._baseline_prediction)[0])), "feature": cat["feature_idx"].astype(np.int64),
             "threshold": cat["num_threshold"].astype(np.float64), "left": cat["left"].astype(np.int64),
             "right": cat["right"].astype(np.int64), "is_leaf": cat["is_leaf"].astype(bool),
             "value": cat["value"].astype(np.float64), "tree_offsets": offsets.astype(np.int64)})


def check_clf(clf, spec, arrays, X):
    ours = cab_gpu.Classifier(spec, arrays).proba(X)
    ref = clf.predict_proba(np.asarray(X, dtype=float))[:, 1]
    err = float(np.abs(ours - ref).max())
    assert err < 1e-9, f"exported classifier differs by {err}"
    return err


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "gpu_bundle"))
    ap.add_argument("--sets", default="th,tl,m,lo,ki,fm")
    ap.add_argument("--per-set", type=int, default=300)
    ap.add_argument("--estimators", default="sc2,turbo,mac")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    config, models, report = {"per_set": args.per_set, "sets": {}}, {}, []
    if (out / "config.json").exists():  # resume: keep the sets already exported
        config = json.loads((out / "config.json").read_text())
        models = dict(np.load(out / "models.npz"))
    for code in args.sets.split(","):
        if code in config["sets"] and (out / f"data_{code}.npz").exists():
            print(f"{code}: already exported", flush=True)
            continue
        subset, fam = SETS[code]
        ds = L.make_dataset(fam)
        # the same pairs as the CPU live timing: pairs logged under both prefixes, then 300 drawn with seed 0
        offline = {pf: {r["pair_id"]: r for r in B.load(subset, pf)} for pf in ("budgetc",)}
        ids = set(offline["budgetc"])
        pairs = [p for p in subset_pairs(ds, subset) if p.pair_id in ids]
        rng = np.random.default_rng(0)
        pairs = [pairs[i] for i in sorted(rng.choice(len(pairs), min(args.per_set, len(pairs)), replace=False))]
        n = len(pairs)
        Pp = np.zeros((n, 4000, 3), np.float32)
        Qp = np.zeros((n, 4000, 3), np.float32)
        Rp = np.ones((n, 4000), np.float32)
        n_all = np.zeros(n, np.int64)
        T_gt = np.zeros((n, 4, 4))
        t0 = time.time()
        for i, p in enumerate(pairs):
            wait_if_live()
            rp, rf, sp, sf = ds.features_pair(p)
            P, Q, ratio = ds.corr(sp, sf, rp, rf)
            k = min(P.shape[0], 4000)
            Pp[i, :k], Qp[i, :k], Rp[i, :k], n_all[i], T_gt[i] = P[:k], Q[:k], ratio[:k], k, p.transform
            assert k == offline["budgetc"][p.pair_id]["N_all"], p.pair_id
        np.savez_compressed(out / f"data_{code}.npz", P=Pp, Q=Qp, ratio=Rp, n_all=n_all, T_gt=T_gt,
                            pair_id=np.array([p.pair_id for p in pairs]), scene=np.array([p.scene for p in pairs]))
        print(f"{code} ({subset}): {n} pairs, correspondences {time.time() - t0:.0f}s", flush=True)
        entry = {"subset": subset, "family": fam, "inlier": ds.inlier, "compat_thr": ds.compat_thr,
                 "rot_deg": 5.0 if ds.outdoor else 15.0, "trans_m": 0.6 if ds.outdoor else 0.3, "estimators": {}}
        for est in args.estimators.split(","):
            try:
                ctrls = {v: L.Controller(job, est, "extended", ds) for v, job in JOBS.items()}
            except FileNotFoundError:
                print(f"  {est}: no certified configuration yet, skipped", flush=True)
                continue
            e = {"kw": ds.kwargs(est), "configs": {}, "reference": {}}
            for v, c in ctrls.items():
                key = f"{code}/{est}/{v}"
                spec, arr = export_clf(c.clf_now)
                cfg = {"prefix": c.prefix, "ladder": c.ladder_name, "ladder_idx": list(c.ladder),
                       "edges": c.edges.tolist(), "lambdas": list(c.lams), "clf": {**spec, "key": key + "/clf"}}
                models.update({f"{key}/clf/{k}": a for k, a in arr.items()})
                recs = [offline["budgetc"][p.pair_id] for p in pairs]
                X = np.array([[st[f] for f in B.FEATURES] for r in recs
                              for st in B.trajectory_ladder(r, est, c.ladder)], dtype=float)
                err = check_clf(c.clf_now, spec, arr, X)
                if c.gate is not None and c.gate.clf is not None:
                    gspec, garr = export_clf(c.gate.clf)
                    cfg.update(gate={**gspec, "key": key + "/gate"}, gate_threshold=float(c.gate.threshold))
                    models.update({f"{key}/gate/{k}": a for k, a in garr.items()})
                    Xg, _ = __import__("select_ladder").load_gate_features(subset, recs)
                    err = max(err, check_clf(c.gate.clf, gspec, garr, Xg))
                e["configs"][v] = cfg
                # the CPU decisions on these pairs (offline, from the logs) and the logged full-budget outcome
                e["reference"][v] = {"offline_stop": [int(c.offline_stop(r, subset)) for r in recs]}
                report.append(f"  {code} {est} {v}: ladder {c.ladder_name}, classifier {spec['kind']}, "
                              f"gate {cfg.get('gate', {}).get('kind', 'none')}, max probability error {err:.1e}")
            e["reference"]["full_ok"] = [bool(offline["budgetc"][p.pair_id][est][4]["ok15"]) for p in pairs]
            live = ROOT / "results" / "budget" / (f"live_budget_compare_ext_{fam}_v3"
                                                   + ("" if est in ("sc2", "turbo") else f"_{est}") + ".json")
            if live.exists():  # CPU live times of the same pairs, for the CPU/GPU comparison
                rows = {r["pair_id"]: r for r in json.loads(live.read_text()) if r["est"] == est and r["subset"] == subset}
                if all(p.pair_id in rows for p in pairs):
                    e["reference"]["cpu_live_s"] = {j: [rows[p.pair_id][j]["s"] for p in pairs]
                                                    for j in ("full", "budgetc", "budgetc+v3") if j in rows[pairs[0].pair_id]}
            entry["estimators"][est] = e
        config["sets"][code] = entry
        np.savez_compressed(out / "models.npz", **models)  # after every set, so that an interrupted export resumes
        (out / "config.json").write_text(json.dumps(config, indent=1))
    print("\n".join(report))
    print(f"bundle written to {out}")


if __name__ == "__main__":
    main()
