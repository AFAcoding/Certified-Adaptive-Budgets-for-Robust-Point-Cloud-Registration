"""Per-pair logs of cheaper variants of SC^2-PCR and TurboReg, for the equal-time comparison.

Same correspondences as the budget logs (nearest FPFH neighbour per source point, Lowe-ratio
sorted, capped at 4,000). Variants:
  rand   uniform random subset of N in {250, 500, 1000, 2000}                    (every 2nd pair)
  fm1    FastMAC-style sampling on the first-order graph (O(N^2) signal)          (every 2nd pair)
  fm2    FastMAC-style sampling on the second-order graph (O(N^3), as published)  (every 4th pair)
  seeds  SC^2-PCR on all correspondences with fewer seeds (ratio 0.025, 0.01)     (every 8th pair)
  k1     TurboReg on all correspondences with fewer cliques (K1 = 500, 250)       (every 8th pair)
(pairs taken by test-set index, so every scene is represented; the 101 pairs logged before this
schedule was reduced keep their extra variants and are filtered to the schedule in the analysis)
Sampling-signal times are logged separately (t_fm1, t_fm2) and charged per configuration.
Primary timing for the paper comes from the live single-process benchmark; offline times here
are recorded under 6-worker load.

Usage: python -I -u scripts/build_equal_time_logs.py --subset 3DMatch --workers 6
"""

from __future__ import annotations

import argparse
import json
import os
import time
import zlib
from concurrent.futures import ProcessPoolExecutor, as_completed

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "ACPR_KD_WORKERS"):
    os.environ.setdefault(var, "1")

import numpy as np  # noqa: E402

from acpr import LOG_ROOT  # noqa: E402
from acpr.data import load_pairs  # noqa: E402

BUDGETS = (250, 500, 1000, 2000)
SEED_RATIOS = (0.025, 0.01)
K1S = (500, 250)
_PAIRS: dict = {}


def _run(subset: str, index: int) -> str:
    from acpr.estimators import fastmac_draw, fastmac_probs, nn_correspondences, sc2_pcr, turboreg
    from acpr.features import get_fpfh
    from acpr.metrics import rre_rte

    pair = _PAIRS.setdefault(subset, load_pairs(subset))[index]
    rp, rf, _ = get_fpfh(pair.pcd0)
    sp, sf, _ = get_fpfh(pair.pcd1)
    P, Q, _ = nn_correspondences(sp, sf, rp, rf)
    Nall = min(P.shape[0], 4000)
    P, Q = P[:Nall], Q[:Nall]
    rec = {"pair_id": pair.pair_id, "subset": subset, "scene": pair.scene, "N_all": int(Nall)}

    def run(fn, idx, **kw):
        ts = time.perf_counter()
        T, inf = fn(P[idx], Q[idx], **kw) if idx is not None else fn(P, Q, **kw)
        secs = time.perf_counter() - ts
        rre, rte = rre_rte(pair.transform, T)
        return {"s": secs, "ok15": bool(rre <= 15 and rte <= 0.3), "rre": round(rre, 4), "rte": round(rte, 5),
                "inliers": int(inf.get("inliers", 0))}

    seed = zlib.crc32(pair.pair_id.encode())
    samplers = {"rand": lambda m, rng: np.sort(rng.choice(Nall, size=min(m, Nall), replace=False))}
    # FastMAC-style signal: computed (and timed) once per pair, shared by all budgets
    t0 = time.perf_counter()
    probs1 = fastmac_probs(P, Q, second_order=False)
    rec["t_fm1"] = time.perf_counter() - t0
    samplers["fm1"] = lambda m, rng: fastmac_draw(probs1, m, rng)
    if index % 4 == 0:
        t0 = time.perf_counter()
        probs2 = fastmac_probs(P, Q, second_order=True)
        rec["t_fm2"] = time.perf_counter() - t0
        samplers["fm2"] = lambda m, rng: fastmac_draw(probs2, m, rng)
    for name, sampler in samplers.items():
        rec[name] = {}
        for b in BUDGETS:
            idx = sampler(b, np.random.default_rng(seed + b)) if b < Nall else None
            rec[name][str(b)] = {"sc2": run(sc2_pcr, idx), "turbo": run(turboreg, idx)}
    if index % 8 == 0:
        rec["seeds"] = {str(r): run(sc2_pcr, None, ratio=r) for r in SEED_RATIOS}
        rec["k1"] = {str(k): run(turboreg, None, k1=k) for k in K1S}
    return json.dumps(rec)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subset", required=True)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--every", type=int, default=2, help="use every k-th test pair (by index)")
    args = ap.parse_args()
    pairs = load_pairs(args.subset)
    out = LOG_ROOT / f"eqtime_{args.subset}.jsonl"
    done = {json.loads(x)["pair_id"] for x in open(out) if x.strip()} if out.exists() else set()
    todo = [i for i in range(0, len(pairs), args.every) if pairs[i].pair_id not in done]
    print(f"{args.subset}: {len(todo)} pairs to run", flush=True)
    t0 = time.time()
    with open(out, "a") as f, ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(_run, args.subset, i) for i in todo]
        for n, fu in enumerate(as_completed(futs), 1):
            f.write(fu.result() + "\n")
            f.flush()
            if n % 100 == 0 or n == len(futs):
                el = time.time() - t0
                print(f"  {n}/{len(futs)}  {el:.0f}s  ETA {el / n * (len(futs) - n):.0f}s", flush=True)


if __name__ == "__main__":
    main()
