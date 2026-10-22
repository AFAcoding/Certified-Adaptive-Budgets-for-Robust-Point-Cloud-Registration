"""Exploration (fitting, calibration and development data only; no blind test set is loaded): can the budget a pair
needs be predicted before the estimator runs?

Target k*: the smallest logged budget (250, 500, 1000, 2000, 4000) whose estimate is correct, for pairs the full
budget registers; class 5 = the full budget fails ("unsolvable" for this estimator and correspondences).
Reports (compatibility order, offline single-thread cost from the logs, ordering included when a budget truncates):
  - the distribution of k* per split;
  - cost bounds relative to the full budget: perfect one-shot budget (run only k*; unsolvable pairs run the full
    budget, or are skipped entirely), the protocol-v2 ladder with a perfect stopping oracle;
  - predictability of k* from the pre-estimation gate signals (acpr.gate): a boosted-tree classifier trained on the
    fitting + calibration pairs, evaluated on 3DMatch / 3DLoMatch (development benchmarks): accuracy, per-class
    one-vs-rest AUC, and a "predict, run, verify-by-oracle, else full" policy (an optimistic upper bound, since a real
    policy must verify without ground truth).

Usage: python -I scripts/explore/budget_prediction.py
Writes results/explore/budget_prediction.json
"""

import json
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import analyze_budget as B  # noqa: E402
import select_ladder as S  # noqa: E402
from acpr import RESULTS_ROOT  # noqa: E402

SPLITS = {"fit": "v2_fit", "cal": "v2_cal", "3DMatch": "3DMatch", "3DLoMatch": "3DLoMatch"}


def stage_cost(r, est, k):
    return B.trajectory_ladder(r, est, (k,))[-1]["s"]


def target(r, est):
    if not r[est][4]["ok15"]:
        return 5
    return next(k for k in range(5) if r[est][k]["ok15"])


def main():
    out = {}
    for est in ("sc2", "turbo"):
        D = {}
        for name, log in SPLITS.items():
            recs = B.load(log, "budgetc")
            X, _ = S.load_gate_features(log, recs)
            y = np.array([target(r, est) for r in recs])
            C = np.array([[stage_cost(r, est, k) for k in range(5)] for r in recs])
            D[name] = (X, y, C)
        res = {}
        for name, (X, y, C) in D.items():
            full = C[:, 4].sum()
            one = np.where(y < 5, C[np.arange(len(y)), np.minimum(y, 4)], C[:, 4]).sum()
            one_skip = np.where(y < 5, C[np.arange(len(y)), np.minimum(y, 4)], 0.0).sum()
            res[name] = {"dist": np.bincount(y, minlength=6).tolist(), "oracle_oneshot_speed": float(full / one),
                         "oracle_oneshot_skip_unsolvable_speed": float(full / one_skip)}
        Xtr = np.vstack([D["fit"][0], D["cal"][0]])
        ytr = np.concatenate([D["fit"][1], D["cal"][1]])
        clf = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=300, l2_regularization=1.0,
                                             random_state=0).fit(Xtr, ytr)
        for name in ("3DMatch", "3DLoMatch"):
            X, y, C = D[name]
            P = clf.predict_proba(X)
            cls = clf.classes_
            aucs = {int(c): float(roc_auc_score(y == c, P[:, i])) for i, c in enumerate(cls) if 0 < (y == c).sum() < len(y)}
            # expected-cost choice of the first budget, then (oracle) verification, else the full budget
            exp_cost = []
            for k in range(5):
                p_ok = P[:, [i for i, c in enumerate(cls) if c <= k]].sum(axis=1)
                exp_cost.append(C[:, k] + (1 - p_ok) * C[:, 4] * (k < 4))
            kh = np.argmin(np.array(exp_cost), axis=0)
            ok_at = np.array([y[i] <= kh[i] for i in range(len(y))])
            cost = np.where(ok_at | (kh == 4), C[np.arange(len(y)), kh], C[np.arange(len(y)), kh] + C[:, 4])
            res[name].update({"acc": float(np.mean(cls[P.argmax(1)] == y)), "auc_by_class": aucs,
                              "pred_then_verify_oracle_speed": float(C[:, 4].sum() / cost.sum()),
                              "first_budget_hist": np.bincount(kh, minlength=5).tolist()})
        out[est] = res
        print(est, json.dumps(res, indent=1), flush=True)
    (RESULTS_ROOT / "explore" / "budget_prediction.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
