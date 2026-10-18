"""Build the per-pair experiment logs (search lattice, RANSAC, SC^2) in parallel.

FPFH features are computed first in the main process (cached per fragment), then
pairs are distributed over worker processes, each limited to one BLAS thread.
The output is append-only JSONL and resumable.

Usage:
    python -I -u scripts/build_search_logs.py --subset val --workers 6
    python -I -u scripts/build_search_logs.py --subset train --sample 2000 --workers 6
"""

from __future__ import annotations

import argparse
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(var, "1")

import numpy as np  # noqa: E402

from acpr import LOG_ROOT  # noqa: E402
from acpr.data import load_pairs  # noqa: E402
from acpr.features import get_fpfh  # noqa: E402


def _work(subset: str, index: int, variant: str = "full") -> str:
    from acpr.data import load_pairs as lp
    from acpr.experiment import run_pair

    pair = _PAIRS_CACHE.setdefault(subset, lp(subset))[index]
    return json.dumps(run_pair(pair, variant=variant))


_PAIRS_CACHE: dict = {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subset", required=True, choices=["train", "val", "3DMatch", "3DLoMatch"])
    ap.add_argument("--sample", type=int, default=None, help="random subset size (train)")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out", default=None)
    ap.add_argument("--variant", default="full", choices=["full", "psh"])
    args = ap.parse_args()
    prefix = "search" if args.variant == "full" else "psh"

    pairs = load_pairs(args.subset)
    indices = list(range(len(pairs)))
    if args.sample and args.sample < len(pairs):
        indices = sorted(np.random.default_rng(0).choice(len(pairs), args.sample, replace=False).tolist())

    out = Path(args.out) if args.out else LOG_ROOT / f"{prefix}_{args.subset}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        with open(out) as f:
            done = {json.loads(line)["pair_id"] for line in f if line.strip()}
    todo = [i for i in indices if pairs[i].pair_id not in done]

    # features first, sequentially (clean timing, no cache races)
    t0 = time.time()
    frags = sorted({pairs[i].pcd0 for i in todo} | {pairs[i].pcd1 for i in todo})
    for k, pcd in enumerate(frags):
        get_fpfh(pcd)
    print(f"{args.subset}: features for {len(frags)} fragments ready ({time.time() - t0:.0f}s); "
          f"{len(todo)} pairs to run ({len(done)} already logged)", flush=True)

    t0 = time.time()
    with open(out, "a") as f, ProcessPoolExecutor(max_workers=args.workers) as ex:
        futures = [ex.submit(_work, args.subset, i, args.variant) for i in todo]
        for n, fut in enumerate(as_completed(futures), 1):
            f.write(fut.result() + "\n")
            f.flush()
            if n % 100 == 0 or n == len(futures):
                el = time.time() - t0
                print(f"  {n}/{len(futures)} pairs, {el:.0f}s elapsed, ETA {el / n * (len(futures) - n):.0f}s",
                      flush=True)


if __name__ == "__main__":
    main()
