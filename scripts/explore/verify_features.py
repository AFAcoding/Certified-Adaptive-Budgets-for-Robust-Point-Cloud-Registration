"""Exploration (fitting, calibration and development splits only): geometric verification of each stage's pose.

For every logged stage estimate T (logs/budgetc_<split>.jsonl), the source fragment's downsampled points (the 5 cm
FPFH points, cached) are transformed by T and matched to the target's points with a k-d tree:
  vfit   share of source points within tau = 0.10 m of the target (the inlier threshold), i.e. the overlap a
         correct pose explains;
  vfit2  the same at 2 tau;
  vrmse  RMS distance of the points within tau (m).
No ground truth is used. The k-d tree of the target is built once per pair; its time and every query's time are
recorded (single thread) so that a controller using these signals can be charged for them.

Usage: python -I -u scripts/explore/verify_features.py <split> [--workers 4]
Writes results/explore/verify_<split>.jsonl
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(var, "1")

import numpy as np  # noqa: E402
from scipy.spatial import cKDTree  # noqa: E402

from acpr import LOG_ROOT, RESULTS_ROOT  # noqa: E402

BLIND = ("v2_blind_hi", "v2_blind_lo", "v3_blind_hi", "v3_blind_lo", "kitti_raw_blind")
TAU = 0.10
_PAIRS = {}


def work(split, rec):
    from acpr.data import load_pairs
    from acpr.features import get_fpfh
    pairs = _PAIRS.setdefault(split, {p.pair_id: p for p in load_pairs(split)})
    p = pairs[rec["pair_id"]]
    ref, _, _ = get_fpfh(p.pcd0)
    src, _, _ = get_fpfh(p.pcd1)
    t0 = time.perf_counter()
    tree = cKDTree(ref)
    t_tree = time.perf_counter() - t0
    out = {"pair_id": rec["pair_id"], "t_tree": t_tree}
    for est in ("sc2", "turbo"):  # same fragments for both estimators; their poses differ
        f1, f2, rm, tq = [], [], [], []
        for st in rec[est]:
            if st is None:
                f1.append(None), f2.append(None), rm.append(None), tq.append(None)
                continue
            T = np.asarray(st["T"], dtype=float).reshape(4, 4)
            t0 = time.perf_counter()
            d, _ = tree.query(src @ T[:3, :3].T + T[:3, 3], k=1, distance_upper_bound=2 * TAU)
            tq.append(time.perf_counter() - t0)
            inl = d < TAU
            f1.append(float(inl.mean()))
            f2.append(float(np.isfinite(d).mean()))
            rm.append(float(np.sqrt(np.mean(d[inl] ** 2))) if inl.any() else TAU)
        out[est] = {"vfit": f1, "vfit2": f2, "vrmse": rm, "t_query": tq}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("split")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    if a.split in BLIND:
        sys.exit("blind test sets are not used for exploration")
    with open(LOG_ROOT / f"budgetc_{a.split}.jsonl") as f:
        recs = [json.loads(x) for x in f if x.strip()]
    out = RESULTS_ROOT / "explore" / f"verify_{a.split}.jsonl"
    with open(out, "w") as g, ProcessPoolExecutor(max_workers=a.workers) as ex:
        for k, r in enumerate(ex.map(work, [a.split] * len(recs), recs, chunksize=8)):
            g.write(json.dumps(r) + "\n")
            if k % 500 == 0:
                print(f"  {a.split} {k}/{len(recs)}", flush=True)


if __name__ == "__main__":
    main()
