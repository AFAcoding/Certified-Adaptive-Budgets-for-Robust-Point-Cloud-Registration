"""Exploration (development data only): does a stronger stopping controller make CAB faster at the same guarantee?

Swaps the controller's classifier (p_now and p_fin) and re-runs the whole choose-then-certify pipeline of
select_ladder.py: choice on the fitting pairs, certification on the calibration pairs, evaluation on the development
benchmarks. The blind test sets of protocol v2 are never loaded. One variant per process, because the out-of-fold
controller scores are cached per process.

Usage: python -I scripts/explore/controller_variants.py <variant> <dataset> [prefix]
  variant: logit (the paper's), logit_c01, poly2, hgb
  dataset: v2_indoor_fpfh | v2_kitti_fpfh | v2_indoor_fcgf
Writes results/explore/controller_<variant>_<dataset>_<prefix>.json
"""

import json
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import analyze_budget as B  # noqa: E402
import select_ladder as S  # noqa: E402
from acpr import RESULTS_ROOT  # noqa: E402
from acpr import analysis as A  # noqa: E402

DEV_TESTS = {"v2_indoor_fpfh": ["3DMatch", "3DLoMatch"], "v2_kitti_fpfh": ["kitti_test"],
             "v2_indoor_fcgf": ["fcgfown_3DMatch", "fcgfown_3DLoMatch"]}


def make(variant):
    def fit(X, y, C=1.0):
        if len(np.unique(y)) < 2:
            return A._Constant(np.mean(y))
        if variant == "logit":
            clf = make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=2000))
        elif variant == "logit_c01":
            clf = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=2000))
        elif variant == "poly2":
            clf = make_pipeline(StandardScaler(), PolynomialFeatures(2, include_bias=False), StandardScaler(),
                                LogisticRegression(C=0.1, max_iter=5000))
        elif variant == "hgb":
            clf = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=300,
                                                 l2_regularization=1.0, random_state=0)
        else:
            raise ValueError(variant)
        clf.fit(X, y)
        return clf
    return fit


def main():
    variant, dataset = sys.argv[1], sys.argv[2]
    prefix = sys.argv[3] if len(sys.argv) > 3 else "budgetc"
    A.fit_classifier = make(variant)  # select_ladder and analyze_budget call A.fit_classifier at run time
    D = S.DATASETS[dataset]
    tests = DEV_TESTS[dataset]
    logs = {"train": B.load(D["train"], prefix), "val": B.load(D["val"], prefix),
            **{s: B.load(s, prefix) for s in tests}}
    out = {}
    for est in ("sc2", "turbo"):
        selected, rows, built = S.select_and_certify(logs, est, B.LADDERS_EXT)
        x = selected["mondrian"]
        res = {"ladder": x["ladder"], "policy": x["policy"], "fallback": x["fallback"],
               "fit_s": x["fit_s"], "chosen": x["chosen"]["ladder"], "test": {}}
        tr, mdps = built["mondrian"]
        for s in tests:
            full = A.fixed_stage([B.trajectory_ladder(r, est, (4,)) for r in logs[s]], 0)
            o = S.policy_outcome(tr[s], mdps, x["policy"], x["param"])
            cmp = B.paired(o, full, logs[s], B.MARGIN[s])
            res["test"][s] = {"speedup": cmp["speedup"], "risk": float(np.mean(full.ok & ~o.ok)),
                              "ub95": cmp["ub95"], "non_inferior": cmp["non_inferior"]}
        out[est] = res
        print(variant, dataset, prefix, est, res["ladder"], f"fit {1e3 * res['fit_s']:.0f} ms",
              {s: (round(v["speedup"], 2), round(100 * v["risk"], 2)) for s, v in res["test"].items()}, flush=True)
    d = RESULTS_ROOT / "explore"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"controller_{variant}_{dataset}_{prefix}.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
