"""Protocol v2 budget logs (PROTOCOL.md): every new split, with FCGF features computed by acpr.fcgf_net and FPFH on
the KITTI raw drives. Same record format, cost accounting and timing as the FCGF and KITTI builders: both orderings
in one pass per pair (shared correspondences and full-budget run), exact nearest neighbours by brute force.

Writes logs/budget_<name>.jsonl (ratio order) and logs/budgetc_<name>.jsonl (compatibility order); <name> is a key of
acpr.v2data.config. Resumable.

Usage: python -I -u scripts/build_logs_v2.py --name fcgfown_val --workers 6
"""

from __future__ import annotations

import argparse
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import lru_cache

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "ACPR_KD_WORKERS"):
    os.environ.setdefault(var, "1")

import numpy as np  # noqa: E402

from acpr import LOG_ROOT  # noqa: E402

BUDGETS = (250, 500, 1000, 2000, 4000)


@lru_cache(maxsize=None)
def _config(name):
    from acpr.v2data import config
    return config(name)


@lru_cache(maxsize=None)
def _pairs(name):
    return _config(name)["pairs"]()


def _pose_change(prev_T, T):
    if prev_T is None:
        return 180.0, 10.0
    R = prev_T[:3, :3].T @ T[:3, :3]
    return (float(np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1)))),
            float(np.linalg.norm(prev_T[:3, 3] - T[:3, 3])))


def _run(dset: str, index: int) -> tuple[str, str]:
    from acpr.estimators import compat_order, nn_correspondences_bf, sc2_pcr, turboreg

    cfg = _config(dset)
    pair = _pairs(dset)[index]
    rp, rf = cfg["features"](pair.pcd0)
    sp, sf = cfg["features"](pair.pcd1)
    t0 = time.perf_counter()
    P, Q, ratio = nn_correspondences_bf(sp, sf, rp, rf)
    t_corr = time.perf_counter() - t0
    n_all = min(P.shape[0], BUDGETS[-1])
    P, Q, ratio = P[:n_all], Q[:n_all], ratio[:n_all]
    t0 = time.perf_counter()
    perm, ops_order, anchors = compat_order(P, Q, thr=cfg["compat_thr"], return_anchors=True)
    t_order = time.perf_counter() - t0
    inl = cfg["inlier"]
    gt_res = np.linalg.norm(P @ pair.transform[:3, :3].T + pair.transform[:3, 3] - Q, axis=1)
    base = {"pair_id": pair.pair_id, "subset": pair.subset, "scene": pair.scene, "overlap": float(np.nan_to_num(pair.overlap)),
            "rr_eligible": True, "N_all": int(n_all), "t_corr": t_corr}

    def stage(fn, kw, Pi, Qi, ratio_i, b, n):
        ts = time.perf_counter()
        T, inf = fn(Pi, Qi, **kw)
        secs = time.perf_counter() - ts
        ok, rre, rte = cfg["success"](pair.transform, T)
        res_all = np.linalg.norm(P @ T[:3, :3].T + T[:3, 3] - Q, axis=1)
        return T, {"budget": b, "n": n, "s": secs, "ops": inf.get("ops", 0), "inliers": inf.get("inliers", 0),
                   "inliers_all": int((res_all < inl).sum()), "inliers_top250": int((res_all[:250] < inl).sum()),
                   "ratio_med": float(np.median(ratio_i)) if n else 1.0, "ok": ok, "ok15": ok,
                   "rre": round(rre, 4), "rte": round(rte, 5), "T": [round(float(x), 6) for x in T.reshape(-1)]}

    recs = {}
    full = {}
    for order in ("ratio", "compat"):
        Po, Qo, ratio_o, res_o = (P[perm], Q[perm], ratio[perm], gt_res[perm]) if order == "compat" else (P, Q, ratio, gt_res)
        rec = dict(base, order=order, t_order=t_order if order == "compat" else 0.0,
                   ops_order=ops_order if order == "compat" else 0, gt_inliers=int((gt_res < inl).sum()),
                   gt_inliers_by_budget=[int((res_o[:b] < inl).sum()) for b in BUDGETS])
        if order == "compat":
            rec["anchors_true"] = int((gt_res[anchors] < inl).sum())
        for name, fn in (("sc2", sc2_pcr), ("turbo", turboreg)):
            kw = cfg[name]
            stages, prev_T = [], None
            for b in BUDGETS:
                n = min(b, n_all)
                if n >= n_all:
                    if name not in full:  # the standard full-budget run, computed once per pair
                        full[name] = stage(fn, kw, P, Q, ratio, b, n)
                    T, st = full[name][0], dict(full[name][1], budget=b)
                else:
                    T, st = stage(fn, kw, Po[:n], Qo[:n], ratio_o[:n], b, n)
                st["dpose_deg"], st["dpose_m"] = _pose_change(prev_T, T)
                prev_T = T
                stages.append(st)
                if n >= n_all:
                    for b2 in BUDGETS[len(stages):]:
                        stages.append({**st, "budget": b2, "s": 0.0, "ops": 0, "dpose_deg": 0.0, "dpose_m": 0.0,
                                       "repeat": True})
                    break
            rec[name] = stages
        recs[order] = json.dumps(rec)
    return recs["ratio"], recs["compat"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()
    pairs = _pairs(args.name)
    outs = [LOG_ROOT / f"{pf}_{args.name}.jsonl" for pf in ("budget", "budgetc")]
    done = {json.loads(x)["pair_id"] for x in open(outs[1]) if x.strip()} if outs[1].exists() else set()
    todo = [i for i in range(len(pairs)) if pairs[i].pair_id not in done]
    print(f"{args.name}: {len(todo)} pairs to run", flush=True)
    t0 = time.time()
    with open(outs[0], "a") as f0, open(outs[1], "a") as f1, ProcessPoolExecutor(args.workers) as ex:
        futs = [ex.submit(_run, args.name, i) for i in todo]
        for n, fu in enumerate(as_completed(futs), 1):
            r0, r1 = fu.result()
            f0.write(r0 + "\n")
            f1.write(r1 + "\n")
            f0.flush()
            f1.flush()
            if n % 100 == 0 or n == len(futs):
                el = time.time() - t0
                print(f"  {n}/{len(futs)}  {el:.0f}s  ETA {el / n * (len(futs) - n):.0f}s", flush=True)


if __name__ == "__main__":
    main()
