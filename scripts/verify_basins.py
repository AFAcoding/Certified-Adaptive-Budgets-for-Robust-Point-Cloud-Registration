"""Whole-cloud verification of every logged basin (overlap under the basin pose).

For each pair, a KD-tree is built once on the target cloud (5 cm points); for every
basin, a fixed subsample of source points is transformed and the fraction with a
target neighbour within `radius` is recorded. This is a cheap check that does not
depend on the putative correspondences, used to re-rank basins (gap G3).

Output: logs/verify_<prefix>_<subset>.jsonl with, per pair, the overlap of every basin
(same nesting as the search log) and the measured seconds for the tree and queries.

Usage: python -I -u scripts/verify_basins.py --subset val [--prefix search] [--workers 6]
"""

from __future__ import annotations

import argparse
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(var, "1")

import numpy as np  # noqa: E402
from scipy.spatial import cKDTree  # noqa: E402

from acpr import LOG_ROOT  # noqa: E402

N_SUB = 1000
RADIUS = 0.075


def _verify(line: str) -> str:
    from acpr.data import load_pairs
    from acpr.features import get_fpfh

    r = json.loads(line)
    subset = r["subset"]
    pairs = _PAIRS.setdefault(subset, {p.pair_id: p for p in load_pairs(subset)})
    p = pairs[r["pair_id"]]
    ref_pts, _, _ = get_fpfh(p.pcd0)
    src_pts, _, _ = get_fpfh(p.pcd1)
    rng = np.random.default_rng(0)
    sub = src_pts if src_pts.shape[0] <= N_SUB else src_pts[rng.choice(src_pts.shape[0], N_SUB, replace=False)]
    sub = sub.astype(np.float64)
    t0 = time.perf_counter()
    tree = cKDTree(ref_pts)
    t_tree = time.perf_counter() - t0
    out, n_q, t_q = [], 0, 0.0
    for lvl in r.get("search", []):
        row = []
        for b in lvl["basins"]:
            T = np.asarray(b["T"]).reshape(4, 4)
            t1 = time.perf_counter()
            d, _ = tree.query(sub @ T[:3, :3].T + T[:3, 3], k=1, distance_upper_bound=RADIUS)
            t_q += time.perf_counter() - t1
            n_q += sub.shape[0]
            row.append(round(float(np.isfinite(d).mean()), 5))
        out.append(row)
    return json.dumps({"pair_id": r["pair_id"], "overlap": out, "n_sub": int(sub.shape[0]), "n_ref": int(ref_pts.shape[0]),
                       "t_tree": t_tree, "t_query_per_point": t_q / max(n_q, 1)})


_PAIRS: dict = {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subset", required=True)
    ap.add_argument("--prefix", default="search")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()
    src = LOG_ROOT / f"{args.prefix}_{args.subset}.jsonl"
    dst = LOG_ROOT / f"verify_{args.prefix}_{args.subset}.jsonl"
    done = set()
    if dst.exists():
        done = {json.loads(x)["pair_id"] for x in open(dst) if x.strip()}
    lines = [x for x in open(src) if x.strip() and json.loads(x)["pair_id"] not in done]
    t0 = time.time()
    with open(dst, "a") as f, ProcessPoolExecutor(max_workers=args.workers) as ex:
        for i, res in enumerate(ex.map(_verify, lines, chunksize=8), 1):
            f.write(res + "\n")
            if i % 500 == 0 or i == len(lines):
                print(f"  {args.subset}: {i}/{len(lines)} verified, {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
