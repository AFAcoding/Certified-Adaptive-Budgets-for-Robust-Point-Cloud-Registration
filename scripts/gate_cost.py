"""Measured per-pair cost of the hardness gate (protocol v3), on development pairs, in the live setting (one process,
default multi-threaded BLAS): the compatibility ordering alone, the gate signals (which also return the ordering), and
one prediction of each gate classifier on a single pair. The extra cost of the gate over CAB's own ordering is
signals + prediction - ordering for the compatibility order, and signals + prediction for the ratio order.

Usage: python -I scripts/gate_cost.py [n_pairs]   (on an otherwise idle machine)
Writes results/protocol_v3/gate_cost.json.
"""

import json
import sys
import time

import numpy as np

from acpr import RESULTS_ROOT
from acpr.data import load_pairs
from acpr.estimators import compat_order, nn_correspondences
from acpr.features import get_fpfh
from acpr.gate import FEATURES, model, signals


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    pairs = load_pairs("3DMatch")
    idx = sorted(np.random.default_rng(0).choice(len(pairs), n, replace=False).tolist())
    rng = np.random.default_rng(1)
    X = rng.normal(size=(2000, len(FEATURES)))
    y = (X[:, 0] + rng.normal(size=2000) > 0).astype(int)
    clfs = {k: model(k).fit(X, y) for k in ("logit", "hgb")}
    t_ord, t_sig, t_pred = [], [], {k: [] for k in clfs}
    for i in idx:
        p = pairs[i]
        rp, rf, _ = get_fpfh(p.pcd0)
        sp, sf, _ = get_fpfh(p.pcd1)
        P, Q, ratio = nn_correspondences(sp, sf, rp, rf)
        P, Q, ratio = P[:4000], Q[:4000], ratio[:4000]
        t0 = time.perf_counter()
        compat_order(P, Q, thr=0.10)
        t_ord.append(time.perf_counter() - t0)
        t0 = time.perf_counter()
        sig, _ = signals(P, Q, ratio, 0.10, return_order=True)
        t_sig.append(time.perf_counter() - t0)
        x = [[sig[f] for f in FEATURES]]
        for k, c in clfs.items():
            t0 = time.perf_counter()
            c.predict_proba(x)
            t_pred[k].append(time.perf_counter() - t0)
    ms = lambda v: 1e3 * float(np.mean(v))  # noqa: E731
    out = {"n_pairs": n, "order_ms": ms(t_ord), "signals_ms": ms(t_sig),
           "predict_ms": {k: ms(v) for k, v in t_pred.items()},
           "extra_compat_ms": {k: ms(t_sig) + ms(v) - ms(t_ord) for k, v in t_pred.items()},
           "extra_ratio_ms": {k: ms(t_sig) + ms(v) for k, v in t_pred.items()}}
    (RESULTS_ROOT / "protocol_v3" / "gate_cost.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
