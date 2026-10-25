"""Exploration (development data only): pre-estimation hardness signals for a gate that sends predicted-hard pairs
straight to the full budget.

Every signal is computed before any estimator runs, from the putative correspondences (sorted by Lowe ratio, capped at
4,000) and the first pass of the compatibility ordering that CAB computes anyway: no ground truth is used.

Usage: python -I -u scripts/explore/gate_features.py <subset> [--workers 4]
  subset: v2_fit | v2_cal | 3DMatch | 3DLoMatch   (the blind v2 subsets are refused)
Writes results/explore/gate_features_<subset>.jsonl (one record per pair, keyed by pair_id).
"""

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from acpr import RESULTS_ROOT
from acpr.data import load_pairs

BLIND = {"v2_blind_hi", "v2_blind_lo", "v2_blind", "v3_blind_hi", "v3_blind_lo", "v4_blind_hi", "v4_blind_lo", "kitti_raw_blind"}
_PAIRS = {}


def signals(P, Q, ratio, m=100, pool=500, thr=0.10):
    """Cheap hardness signals (same compatibility test and anchors as acpr.estimators.compat_order)."""
    from acpr.estimators import _compat
    n = P.shape[0]
    c = slice(0, min(pool, n))
    W = _compat(P, Q, c, c, thr)
    deg = W.sum(axis=1)
    a = np.argsort(-deg, kind="stable")[:m]
    C = _compat(P, Q, slice(None), a, thr)
    score = (C * (C @ C[a])).sum(axis=1) / (m * m)
    s = np.sort(score)[::-1]
    deg_a = np.sort(deg[a])[::-1] / max(W.shape[0], 1)
    support = C.mean(axis=1)  # share of anchors each correspondence agrees with
    return {
        "log_N": float(np.log(max(n, 1))),
        "ratio_q10": float(np.quantile(ratio, 0.1)), "ratio_q50": float(np.median(ratio)),
        "ratio_top250": float(np.mean(ratio[:250])),
        "deg_max": float(deg_a[0]), "deg_q10": float(deg_a[min(9, len(deg_a) - 1)]),
        "deg_mean": float(deg_a.mean()),
        "score_top1": float(s[0]), "score_top10": float(s[min(9, n - 1)]), "score_top50": float(s[min(49, n - 1)]),
        "score_top250": float(s[min(249, n - 1)]),
        "n_support50": float(np.log1p((support >= 0.5).sum())), "n_support25": float(np.log1p((support >= 0.25).sum())),
        "anchor_cohesion": float(C[a].mean()),
    }


def work(subset, i):
    from acpr.estimators import nn_correspondences
    from acpr.features import get_fpfh
    pair = _PAIRS.setdefault(subset, load_pairs(subset))[i]
    rp, rf, _ = get_fpfh(pair.pcd0)
    sp, sf, _ = get_fpfh(pair.pcd1)
    P, Q, ratio = nn_correspondences(sp, sf, rp, rf)
    n = min(P.shape[0], 4000)
    return {"pair_id": pair.pair_id, **signals(P[:n], Q[:n], ratio[:n])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("subset")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    if a.subset in BLIND or "blind" in a.subset:
        sys.exit("blind test sets are not used for exploration")
    pairs = load_pairs(a.subset)
    out = RESULTS_ROOT / "explore" / f"gate_features_{a.subset}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {json.loads(x)["pair_id"] for x in open(out)} if out.exists() else set()
    todo = [i for i, p in enumerate(pairs) if p.pair_id not in done]
    print(f"{a.subset}: {len(todo)} of {len(pairs)} pairs to do", flush=True)
    with open(out, "a") as f, ProcessPoolExecutor(max_workers=a.workers) as ex:
        for k, rec in enumerate(ex.map(work, [a.subset] * len(todo), todo, chunksize=8)):
            f.write(json.dumps(rec) + "\n")
            if k % 500 == 0:
                f.flush()
                print(f"  {k}/{len(todo)}", flush=True)


if __name__ == "__main__":
    main()
