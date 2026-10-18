"""Per-pair logs for adaptive correspondence budgets in front of SC^2-PCR and TurboReg.

For each pair, correspondences (nearest target feature per source point) are sorted by
Lowe ratio. Each estimator is run on the top-N correspondences for every budget in
BUDGETS; the last budget is the standard full-budget configuration. Each stage records
accuracy, wall-clock time (single-threaded BLAS), operation count and signals.

--order compat: truncated budgets take the top-N by second-order compatibility with 100
anchors chosen by first-order degree within the 500 most distinctive correspondences
(acpr.estimators.compat_order, two-pass) instead of the top-N by ratio.
The reordering time is logged as t_order. A budget that covers all correspondences is
the standard full-budget run itself (ratio order, same input set). For train and val it
is copied from the ratio-order log; for the test sets it is re-run, so that the
reference and the truncated budgets are timed in the same run. (A precaution: the
re-run reproduced the old test timings within 2-3 %. The val/test gap in full-budget
time comes from val pairs having fewer correspondences, not from machine load.)

Usage: python -I -u scripts/build_budget_logs.py --subset 3DMatch --workers 6 [--sample K] [--order compat]
"""

from __future__ import annotations

import argparse
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(var, "1")

import numpy as np  # noqa: E402

from acpr import LOG_ROOT  # noqa: E402
from acpr.data import load_pairs  # noqa: E402

BUDGETS = (250, 500, 1000, 2000, 4000)
COPY_FULL_SUBSETS = ("train", "val")  # val: timing conditions verified to match (SC^2 N=2000: 699 vs 692 ms)
_PAIRS: dict = {}


def _pose_change(prev_T, T):
    if prev_T is None:
        return 180.0, 10.0
    R = prev_T[:3, :3].T @ T[:3, :3]
    return (float(np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1)))),
            float(np.linalg.norm(prev_T[:3, 3] - T[:3, 3])))


def _run(subset: str, index: int, order: str = "ratio", full_rec: dict | None = None) -> str:
    from acpr.estimators import compat_order, nn_correspondences, sc2_pcr, turboreg
    from acpr.experiment import info_and_eligibility
    from acpr.features import get_fpfh
    from acpr.metrics import evaluate_transform

    pair = _PAIRS.setdefault(subset, load_pairs(subset))[index]
    info, eligible = info_and_eligibility(pair)
    rp, rf, _ = get_fpfh(pair.pcd0)
    sp, sf, _ = get_fpfh(pair.pcd1)
    t0 = time.perf_counter()
    P, Q, ratio = nn_correspondences(sp, sf, rp, rf)
    t_corr = time.perf_counter() - t0
    Nall = min(P.shape[0], BUDGETS[-1])
    P, Q, ratio = P[:Nall], Q[:Nall], ratio[:Nall]
    rec = {"pair_id": pair.pair_id, "subset": subset, "scene": pair.scene, "overlap": pair.overlap,
           "rr_eligible": bool(eligible and info is not None), "N_all": int(Nall), "t_corr": t_corr,
           "order": order, "t_order": 0.0, "ops_order": 0}
    if order == "compat":
        t0 = time.perf_counter()
        perm, ops_order, anchors = compat_order(P, Q, return_anchors=True)
        rec["t_order"], rec["ops_order"] = time.perf_counter() - t0, ops_order
        Po, Qo, ratio_o = P[perm], Q[perm], ratio[perm]
        res_gt = np.linalg.norm(P @ pair.transform[:3, :3].T + pair.transform[:3, 3] - Q, axis=1)
        rec["anchors_true"] = int((res_gt[anchors] < 0.1).sum())
    else:
        Po, Qo, ratio_o = P, Q, ratio
    gt_res = np.linalg.norm(Po @ pair.transform[:3, :3].T + pair.transform[:3, 3] - Qo, axis=1)
    rec["gt_inliers"] = int((gt_res < 0.1).sum())
    rec["gt_inliers_by_budget"] = [int((gt_res[:b] < 0.1).sum()) for b in BUDGETS]
    for name, fn in [("sc2", sc2_pcr), ("turbo", turboreg)]:
        stages, prev_T = [], None
        for b in BUDGETS:
            n = min(b, Nall)
            if full_rec is not None and n >= Nall:
                # all correspondences: the standard full-budget run (copied, identical input set)
                st = dict(next(s for s in full_rec[name] if s["n"] >= Nall and not s.get("repeat")))
                st["budget"] = b
                T = np.asarray(st["T"], dtype=float).reshape(4, 4)
            else:
                Pi, Qi = (P, Q) if n >= Nall else (Po[:n], Qo[:n])  # full set: standard input order
                ts = time.perf_counter()
                T, inf = fn(Pi, Qi)
                secs = time.perf_counter() - ts
                ev = evaluate_transform(pair.transform, T, info)
                res_all = np.linalg.norm(P @ T[:3, :3].T + T[:3, 3] - Q, axis=1)  # ratio order
                st = {"budget": b, "n": n, "s": secs, "ops": inf.get("ops", 0), "inliers": inf.get("inliers", 0),
                      "inliers_all": int((res_all < 0.1).sum()), "inliers_top250": int((res_all[:250] < 0.1).sum()),
                      "ratio_med": float(np.median(ratio_o[:n])) if n else 1.0,
                      "ok": bool(ev["ok_rmse"]), "ok15": bool(ev["ok_rre_rte"]), "rre": round(ev["rre"], 4),
                      "rte": round(ev["rte"], 5), "T": [round(float(x), 6) for x in T.reshape(-1)]}
            st["dpose_deg"], st["dpose_m"] = _pose_change(prev_T, T)
            prev_T = T
            stages.append(st)
            if n >= Nall:  # larger budgets would repeat the same computation
                for b2 in BUDGETS[len(stages):]:
                    stages.append({**st, "budget": b2, "s": 0.0, "ops": 0, "dpose_deg": 0.0, "dpose_m": 0.0,
                                   "repeat": True})
                break
        rec[name] = stages
    return json.dumps(rec)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subset", required=True)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--sample", type=int, default=None)
    ap.add_argument("--order", choices=["ratio", "compat"], default="ratio")
    args = ap.parse_args()
    pairs = load_pairs(args.subset)
    idx = list(range(len(pairs)))
    if args.sample and args.sample < len(pairs):
        idx = sorted(np.random.default_rng(0).choice(len(pairs), args.sample, replace=False).tolist())
    full = {}
    if args.order == "compat":
        with open(LOG_ROOT / f"budget_{args.subset}.jsonl") as f:
            full = {r["pair_id"]: r for r in map(json.loads, f) if r}
        idx = [i for i in idx if pairs[i].pair_id in full]
    out = LOG_ROOT / f"{'budget' if args.order == 'ratio' else 'budgetc'}_{args.subset}.jsonl"
    done = {json.loads(x)["pair_id"] for x in open(out) if x.strip()} if out.exists() else set()
    todo = [i for i in idx if pairs[i].pair_id not in done]
    print(f"{args.subset} ({args.order}): {len(todo)} pairs to run", flush=True)
    t0 = time.time()
    with open(out, "a") as f, ProcessPoolExecutor(max_workers=args.workers) as ex:
        copy = args.subset in COPY_FULL_SUBSETS
        futs = [ex.submit(_run, args.subset, i, args.order, full.get(pairs[i].pair_id) if copy else None)
                for i in todo]
        for n, fu in enumerate(as_completed(futs), 1):
            f.write(fu.result() + "\n")
            f.flush()
            if n % 50 == 0 or n == len(futs):
                el = time.time() - t0
                print(f"  {n}/{len(futs)}  {el:.0f}s  ETA {el / n * (len(futs) - n):.0f}s", flush=True)


if __name__ == "__main__":
    main()
