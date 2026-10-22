"""Pre-estimation signals of the hardness gate (acpr.gate) for every pair of a logged split.

The correspondences are recomputed exactly as the log builders compute them (same descriptors, nearest-neighbour
search, Lowe-ratio order and cap), and acpr.gate.signals is evaluated with the dataset's compatibility threshold. The
pairs are those of logs/budgetc_<name>.jsonl, matched by pair_id. Single-threaded signal timing is recorded as the
gate's own cost.

Usage: python -I -u scripts/gate_features.py --name <log name> [--workers 6]
  <log name>: v2_fit, v2_cal, v2_blind_hi, 3DMatch, ... (FPFH indoors), kitti_train, kitti_val, kitti_calib,
  kitti_test (FPFH, KITTI odometry), or an acpr.v2data.config name (fcgfown_*, kitti_raw_blind).
Writes results/gate/features_<name>.jsonl. Resumable.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from pathlib import Path

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "ACPR_KD_WORKERS"):
    os.environ.setdefault(var, "1")

import numpy as np  # noqa: E402

from acpr import LOG_ROOT, RESULTS_ROOT  # noqa: E402

KITTI = {"kitti_train": "train", "kitti_val": "val", "kitti_calib": "train", "kitti_test": "test"}


def kind(name):
    if name in KITTI:
        return "kitti"
    from acpr.v2data import config
    try:
        config(name)
        return "v2"
    except KeyError:
        return "indoor"


@lru_cache(maxsize=None)
def pairs_by_id(name):
    k = kind(name)
    if k == "kitti":
        from acpr import kitti as K
        ps = K.load_kitti_pairs(KITTI[name])
    elif k == "v2":
        from acpr.v2data import config
        ps = config(name)["pairs"]()
    else:
        from acpr.data import load_pairs
        ps = load_pairs(name)
    return {p.pair_id: p for p in ps}


def correspondences(name, pair):
    k = kind(name)
    if k == "kitti":
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import build_budget_logs_kitti as BK
        P, Q, ratio, _ = BK._corr(pair)
        return P, Q, ratio, BK.thresholds()["sc2_d_thre"]
    if k == "v2":
        from acpr.estimators import nn_correspondences_bf
        from acpr.v2data import config
        cfg = config(name)
        rp, rf = cfg["features"](pair.pcd0)
        sp, sf = cfg["features"](pair.pcd1)
        P, Q, ratio = nn_correspondences_bf(sp, sf, rp, rf)
        thr = cfg["compat_thr"]
    else:
        from acpr.estimators import nn_correspondences
        from acpr.features import get_fpfh
        rp, rf, _ = get_fpfh(pair.pcd0)
        sp, sf, _ = get_fpfh(pair.pcd1)
        P, Q, ratio = nn_correspondences(sp, sf, rp, rf)
        thr = 0.10
    n = min(P.shape[0], 4000)
    return P[:n], Q[:n], ratio[:n], thr


def work(name, pid):
    from acpr.gate import signals
    P, Q, ratio, thr = correspondences(name, pairs_by_id(name)[pid])
    t0 = time.perf_counter()
    s = signals(P, Q, ratio, thr)
    return {"pair_id": pid, "t_gate": time.perf_counter() - t0, **s}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    with open(LOG_ROOT / f"budgetc_{a.name}.jsonl") as f:
        ids = [json.loads(x)["pair_id"] for x in f if x.strip()]
    out = RESULTS_ROOT / "gate" / f"features_{a.name}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {json.loads(x)["pair_id"] for x in open(out)} if out.exists() else set()
    todo = [i for i in ids if i not in done]
    print(f"{a.name}: {len(todo)} of {len(ids)} pairs to do", flush=True)
    with open(out, "a") as f, ProcessPoolExecutor(max_workers=a.workers) as ex:
        for k, rec in enumerate(ex.map(work, [a.name] * len(todo), todo, chunksize=4)):
            f.write(json.dumps(rec) + "\n")
            if k % 250 == 0:
                f.flush()
                print(f"  {k}/{len(todo)}", flush=True)


if __name__ == "__main__":
    main()
