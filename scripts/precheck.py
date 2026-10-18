"""Registrability pre-check: compatibility statistics of the top correspondences.

For the K most distinctive correspondences (Lowe ratio), two correspondences are
compatible if they preserve distance (| |p_i - p_j| - |q_i - q_j| | < 10 cm). True
inliers are mutually compatible, so the degree distribution of this graph estimates
how many inliers exist *before* any search. Cost: K(K-1)/2 pair checks, counted as
one correspondence evaluation each.

Output: logs/precheck_<subset>.jsonl
Usage: python -I -u scripts/precheck.py --subset val
"""

from __future__ import annotations

import argparse
import json
import time

import numpy as np
from scipy.spatial.distance import cdist

from acpr import LOG_ROOT
from acpr.data import load_pairs
from acpr.features import correspondences

K = 200
THR = 0.10


def stats(P, Q):
    o = np.arange(min(K, P.shape[0]))
    p, q = P[o].astype(np.float64), Q[o].astype(np.float64)
    if p.shape[0] < 3:
        return {"deg_max": 0, "deg_p95": 0.0, "deg_mean": 0.0, "sc2_max": 0.0, "k": int(p.shape[0])}
    C = (np.abs(cdist(p, p) - cdist(q, q)) < THR).astype(np.float32)
    np.fill_diagonal(C, 0)
    deg = C.sum(1)
    sc2 = (C * (C @ C)).sum(1)
    return {"deg_max": int(deg.max()), "deg_p95": float(np.quantile(deg, 0.95)), "deg_mean": float(deg.mean()),
            "sc2_max": float(np.log1p(sc2.max())), "k": int(p.shape[0])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subset", required=True)
    args = ap.parse_args()
    ids = {json.loads(x)["pair_id"] for x in open(LOG_ROOT / f"search_{args.subset}.jsonl") if x.strip()}
    out = LOG_ROOT / f"precheck_{args.subset}.jsonl"
    done = {json.loads(x)["pair_id"] for x in open(out)} if out.exists() else set()
    with open(out, "a") as f:
        for p in load_pairs(args.subset):
            if p.pair_id not in ids or p.pair_id in done:
                continue
            c = correspondences(p)
            order = np.argsort(c["ratio"], kind="stable")
            t0 = time.perf_counter()
            s = stats(c["P"][order], c["Q"][order])
            s["seconds"] = time.perf_counter() - t0
            s["ce"] = s["k"] * (s["k"] - 1) // 2
            f.write(json.dumps({"pair_id": p.pair_id, **s}) + "\n")
    print(f"{args.subset}: precheck done")


if __name__ == "__main__":
    main()
