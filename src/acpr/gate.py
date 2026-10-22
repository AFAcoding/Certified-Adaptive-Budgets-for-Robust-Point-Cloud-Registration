"""Hardness gate in front of CAB.

Before any estimator runs, cheap signals of the putative correspondences (sorted by Lowe ratio) predict whether CAB
would end up paying more than the full budget on the pair (it visits the full budget after cheaper stages). Pairs
predicted hard run the full budget directly, so their result is the reference itself; every other pair runs the
certified CAB policy unchanged. Losses can only disappear, so the gated policy keeps CAB's certificate, overall and
within every difficulty group, and the gate needs no certificate of its own.

The gate is trained on the fitting and calibration pairs (its labels need CAB's outcome, not ground truth beyond what
the certificate already used) and its threshold minimises the total cost of 5-fold out-of-fold predictions.
"""

from __future__ import annotations

import numpy as np

FEATURES = ["log_N", "ratio_q10", "ratio_q50", "ratio_top250", "deg_max", "deg_q10", "deg_mean", "score_top1",
            "score_top10", "score_top50", "score_top250", "n_support50", "n_support25", "anchor_cohesion"]
KINDS = ("logit", "hgb")


def signals(P, Q, ratio, thr: float, m: int = 100, pool: int = 500, return_order: bool = False):
    """Pre-estimation hardness signals: the first pass of acpr.estimators.compat_order (anchor degrees within the
    `pool` most distinctive correspondences), second-order support of every correspondence by the anchors, and Lowe
    ratio statistics. No ground truth. return_order: also return the compatibility order, identical to
    compat_order(P, Q, m, pool, thr)[0], so that a pair that is not gated reuses the work."""
    from acpr.estimators import _compat
    n = P.shape[0]
    if n == 0:
        out = {f: 0.0 for f in FEATURES}
        return (out, np.arange(0)) if return_order else out
    c = slice(0, min(pool, n))
    W = _compat(P, Q, c, c, thr)
    deg = W.sum(axis=1)
    a = np.argsort(-deg, kind="stable")[:m]
    k = len(a)
    C = _compat(P, Q, slice(None), a, thr)
    raw = (C * (C @ C[a])).sum(axis=1)
    score = raw / (k * k)
    s = np.sort(score)[::-1]
    deg_a = np.sort(deg[a])[::-1] / max(W.shape[0], 1)
    support = C.mean(axis=1)
    top = lambda j: float(s[min(j, n - 1)])  # noqa: E731
    out = {"log_N": float(np.log(n)), "ratio_q10": float(np.quantile(ratio, 0.1)),
           "ratio_q50": float(np.median(ratio)), "ratio_top250": float(np.mean(ratio[:250])),
           "deg_max": float(deg_a[0]), "deg_q10": float(deg_a[min(9, k - 1)]), "deg_mean": float(deg_a.mean()),
           "score_top1": top(0), "score_top10": top(9), "score_top50": top(49), "score_top250": top(249),
           "n_support50": float(np.log1p((support >= 0.5).sum())),
           "n_support25": float(np.log1p((support >= 0.25).sum())), "anchor_cohesion": float(C[a].mean())}
    return (out, np.argsort(-raw, kind="stable")) if return_order else out


def model(kind: str):
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    if kind == "hgb":
        return HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=300, l2_regularization=1.0,
                                              random_state=0)
    return make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000))


class Gate:
    """Fitted gate: predict(X) -> True where the pair should run the full budget directly."""

    def __init__(self, kind, clf, threshold, oof_total, cab_total):
        self.kind, self.clf, self.threshold = kind, clf, threshold
        self.oof_total, self.cab_total = oof_total, cab_total

    def predict(self, X):
        if self.clf is None:
            return np.zeros(len(X), dtype=bool)
        return self.clf.predict_proba(np.asarray(X, dtype=float))[:, 1] >= self.threshold


def fit_gate(X, cab_cost, full_cost, gate_cost, kinds=KINDS, seed=0) -> Gate:
    """Choose the classifier and threshold minimising the out-of-fold total cost; X: signals of the training pairs,
    cab_cost: CAB's cost on them, full_cost: the full budget's, gate_cost: the signals' own cost (charged to gated
    pairs, which skip the ordering). Falls back to no gate when gating never pays."""
    from sklearn.model_selection import StratifiedKFold
    X = np.asarray(X, dtype=float)
    y = (cab_cost > full_cost + 1e-12).astype(int)
    gated_cost = full_cost + gate_cost
    best = Gate(None, None, np.inf, float(cab_cost.sum()), float(cab_cost.sum()))
    if y.min() == y.max():
        return best
    grid = np.linspace(0.05, 1.0, 96)
    for kind in kinds:
        oof = np.zeros(len(y))
        for a, b in StratifiedKFold(5, shuffle=True, random_state=seed).split(X, y):
            oof[b] = model(kind).fit(X[a], y[a]).predict_proba(X[b])[:, 1]
        totals = np.array([np.where(oof >= t, gated_cost, cab_cost).sum() for t in grid])
        i = int(np.argmin(totals))
        if totals[i] < best.oof_total:
            best = Gate(kind, model(kind).fit(X, y), float(grid[i]), float(totals[i]), float(cab_cost.sum()))
    return best
