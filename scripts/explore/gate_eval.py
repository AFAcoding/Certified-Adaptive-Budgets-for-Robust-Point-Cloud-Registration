"""Exploration (development data only): a hardness gate in front of CAB.

The gate sees only pre-estimation signals (scripts/explore/gate_features.py). Pairs it predicts hard run the full
budget directly, so their result is the reference itself; every other pair runs the certified CAB policy unchanged.
Losses can only disappear, never appear, so the gated policy keeps CAB's certificate (overall and in every group).

Gate training: label = "CAB costs more than the full budget on this pair" (it visits the full budget after cheaper
stages), on the fitting and calibration pairs (5-fold out-of-fold predictions); the threshold minimises the total cost
on those predictions. Evaluation: the development benchmarks 3DMatch and 3DLoMatch.

Usage: python -I scripts/explore/gate_eval.py [budgetc|budget] [logit|hgb]
"""

import json
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import analyze_budget as B  # noqa: E402
import select_ladder as S  # noqa: E402
from acpr import RESULTS_ROOT  # noqa: E402
from acpr import analysis as A  # noqa: E402

FEATS = ["log_N", "ratio_q10", "ratio_q50", "ratio_top250", "deg_max", "deg_q10", "deg_mean", "score_top1",
         "score_top10", "score_top50", "score_top250", "n_support50", "n_support25", "anchor_cohesion"]
DEV = ["3DMatch", "3DLoMatch"]


def gate_model(kind):
    if kind == "hgb":
        return HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=300, l2_regularization=1.0,
                                              random_state=0)
    return make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000))


def features(subset, recs):
    path = RESULTS_ROOT / "explore" / f"gate_features_{subset}.jsonl"
    F = {}
    for line in open(path):
        r = json.loads(line)
        F[r["pair_id"]] = [r[k] for k in FEATS]
    return np.array([F[r["pair_id"]] for r in recs], dtype=float)


def main():
    prefix = sys.argv[1] if len(sys.argv) > 1 else "budgetc"
    kind = sys.argv[2] if len(sys.argv) > 2 else "logit"
    D = S.DATASETS["v2_indoor_fpfh"]
    logs = {"train": B.load(D["train"], prefix), "val": B.load(D["val"], prefix), **{s: B.load(s, prefix) for s in DEV}}
    X = {"train": features("v2_fit", logs["train"]), "val": features("v2_cal", logs["val"]),
         **{s: features(s, logs[s]) for s in DEV}}
    out = {}
    for est in ("sc2", "turbo"):
        selected, _, built = S.select_and_certify(logs, est, B.LADDERS_EXT)  # the paper's configuration
        x = selected["mondrian"]
        tr, mdps = built["mondrian"]
        res = {"ladder": x["ladder"]}
        cost, full, ok, fok = {}, {}, {}, {}
        for s in ["train", "val"] + DEV:
            o = S.policy_outcome(tr[s], mdps, x["policy"], x["param"])
            f = A.fixed_stage([B.trajectory_ladder(r, est, (4,)) for r in logs[s]], 0)
            cost[s], full[s], ok[s], fok[s] = o.s, f.s, o.ok, f.ok
        # gate cost: the first ordering pass is computed anyway; charge the whole ordering time to gated pairs
        t_gate = {s: np.array([r.get("t_order", 0.0) for r in logs[s]]) for s in cost}
        Xg = np.vstack([X["train"], X["val"]])
        yg = np.concatenate([cost["train"] > full["train"] + 1e-9, cost["val"] > full["val"] + 1e-9]).astype(int)
        cg = np.concatenate([cost["train"], cost["val"]])
        fg = np.concatenate([full["train"], full["val"]]) + np.concatenate([t_gate["train"], t_gate["val"]])
        oof = np.zeros(len(yg))
        for a, b in StratifiedKFold(5, shuffle=True, random_state=0).split(Xg, yg):
            oof[b] = gate_model(kind).fit(Xg[a], yg[a]).predict_proba(Xg[b])[:, 1]
        grid = np.linspace(0.05, 1.0, 96)
        totals = [np.where(oof >= t, fg, cg).sum() for t in grid]
        thr = float(grid[int(np.argmin(totals))])
        res.update(threshold=thr, hard_share_fitcal=float(yg.mean()),
                   fitcal_speed_cab=float(fg.sum() / cg.sum()), fitcal_speed_gate=float(fg.sum() / min(totals)))
        g = gate_model(kind).fit(Xg, yg)
        for s in DEV:
            p = g.predict_proba(X[s])[:, 1]
            gated = p >= thr
            cs = np.where(gated, full[s] + t_gate[s], cost[s])
            oks = np.where(gated, fok[s], ok[s])
            res[s] = {"gated_share": float(gated.mean()),
                      "speed_cab": float(full[s].mean() / cost[s].mean()),
                      "speed_gate": float(full[s].mean() / cs.mean()),
                      "risk_cab": float(np.mean(fok[s] & ~ok[s])), "risk_gate": float(np.mean(fok[s] & ~oks)),
                      "auc_like": float(np.mean(p[cost[s] > full[s]]) - np.mean(p[cost[s] <= full[s]]))}
        out[est] = res
        print(est, json.dumps(res, default=float), flush=True)
    (RESULTS_ROOT / "explore" / f"gate_eval_{prefix}_{kind}.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
