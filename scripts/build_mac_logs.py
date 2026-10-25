"""MAC budget logs (PROTOCOL.md, protocol v3, addenda A and B): the same pairs, correspondences, budgets and record format
as the budget logs of SC2-PCR and TurboReg, for the estimator MAC (acpr.mac), on every family of test sets.

For every pair of logs/budgetc_<subset>.jsonl, the correspondences are recomputed exactly as that subset's builder
computes them (indoor FPFH: build_budget_logs.py, k-d tree; KITTI odometry FPFH: build_budget_logs_kitti.py; FCGF and
KITTI raw drives: build_logs_v2.py; exact nearest neighbours by brute force), and their number must equal the logged
N_all. MAC runs with the settings of its dataset and descriptor (acpr.mac.SETTINGS) on every budget of both orderings
(ratio order and compatibility order, acpr.estimators.compat_order with the logs' threshold); the full-budget run is
computed once and shared by both orderings, as in the builders. Pairs already computed under another subset name
(same scene and fragments, same features) are copied. Writes logs/mac_<subset>.jsonl with
{"pair_id": ..., "ratio": [stages], "compat": [stages]}; scripts/merge_mac_logs.py adds them to the budget logs.

Usage: python -I -u scripts/build_mac_logs.py --subset 3DMatch --workers 6
"""

from __future__ import annotations

import argparse
import json
import os
import time
from functools import lru_cache
from multiprocessing import Pool

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "ACPR_KD_WORKERS"):
    os.environ.setdefault(var, "1")

import numpy as np  # noqa: E402

from acpr import LOG_ROOT, RESULTS_ROOT  # noqa: E402

BUDGETS = (250, 500, 1000, 2000, 4000)
KITTI_ODOMETRY = {"kitti_train": "train", "kitti_calib": "train", "kitti_val": "val", "kitti_test": "test"}


def _pose_change(prev_T, T):
    if prev_T is None:
        return 180.0, 10.0
    R = prev_T[:3, :3].T @ T[:3, :3]
    return (float(np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1)))),
            float(np.linalg.norm(prev_T[:3, 3] - T[:3, 3])))


def _key(subset, pair_id):
    """Identity of a computation: the pair and its features (FCGF subsets share no computation with FPFH ones)."""
    _, scene, frags = pair_id.split("/")
    return ("fcgf" if subset.startswith("fcgfown_") else "fpfh") + "/" + scene + "/" + frags


@lru_cache(maxsize=None)
def _source(subset):
    """Pairs by id, correspondence function, success function, inlier threshold, ordering threshold, MAC settings."""
    from acpr.estimators import nn_correspondences, nn_correspondences_bf
    from acpr.mac import SETTINGS
    if subset.startswith("fcgfown_") or subset == "kitti_raw_blind":  # protocol-v2 configurations
        from acpr.v2data import config
        cfg = config(subset)
        feats = cfg["features"]

        def corr(p):
            rp, rf = feats(p.pcd0)
            sp, sf = feats(p.pcd1)
            return nn_correspondences_bf(sp, sf, rp, rf)

        outdoor = cfg["inlier"] > 0.1
        mac_kw = SETTINGS[("kitti_fcgf" if subset.startswith("fcgfown_") else "kitti_fpfh") if outdoor else "indoor"]
        succ = cfg["success"]
        return ({p.pair_id: p for p in cfg["pairs"]()}, corr, lambda p, T: tuple(succ(p.transform, T)),
                cfg["inlier"], cfg["compat_thr"], mac_kw)
    if subset in KITTI_ODOMETRY:  # odometry pairs with FPFH (build_budget_logs_kitti.py)
        from acpr import kitti as K
        thr = json.loads((RESULTS_ROOT / "kitti" / "thresholds.json").read_text())

        def corr(p):
            rp, rf, _ = K.get_fpfh_kitti(p.pcd0)
            sp, sf, _ = K.get_fpfh_kitti(p.pcd1)
            return nn_correspondences_bf(sp, sf, rp, rf)

        return ({p.pair_id: p for p in K.load_kitti_pairs(KITTI_ODOMETRY[subset])}, corr,
                lambda p, T: tuple(K.success(p.transform, T)), 0.6, thr["sc2_d_thre"], SETTINGS["kitti_fpfh"])
    # indoor FPFH (build_budget_logs.py)
    from acpr.data import load_pairs
    from acpr.experiment import info_and_eligibility
    from acpr.features import get_fpfh
    from acpr.metrics import evaluate_transform

    def corr(p):
        rp, rf, _ = get_fpfh(p.pcd0)
        sp, sf, _ = get_fpfh(p.pcd1)
        return nn_correspondences(sp, sf, rp, rf)

    def success(p, T):
        ev = evaluate_transform(p.transform, T, info_and_eligibility(p)[0])
        return ev["ok_rmse"], ev["ok_rre_rte"], ev["rre"], ev["rte"]

    return {p.pair_id: p for p in load_pairs(subset)}, corr, success, 0.10, 0.10, SETTINGS["indoor"]


def _run(subset: str, pair_id: str, n_all_logged: int) -> str:
    from acpr.estimators import compat_order
    from acpr.mac import mac

    pairs, corr, success, inl, compat_thr, mac_kw = _source(subset)
    pair = pairs[pair_id]
    P, Q, ratio = corr(pair)
    Nall = min(P.shape[0], BUDGETS[-1])
    assert Nall == n_all_logged, f"{pair_id}: {Nall} correspondences, the log has {n_all_logged}"
    P, Q, ratio = P[:Nall], Q[:Nall], ratio[:Nall]
    perm, _ = compat_order(P, Q, thr=compat_thr)
    full = None
    out = {"pair_id": pair_id}
    for order in ("ratio", "compat"):
        Po, Qo, ratio_o = (P[perm], Q[perm], ratio[perm]) if order == "compat" else (P, Q, ratio)
        stages, prev_T = [], None
        for b in BUDGETS:
            n = min(b, Nall)
            if n >= Nall and full is not None:
                st = {**full, "budget": b}  # the standard full-budget run, shared by both orderings
                T = np.asarray(st["T"], dtype=float).reshape(4, 4)
            else:
                Pi, Qi = (P, Q) if n >= Nall else (Po[:n], Qo[:n])  # full set: standard input order
                ts = time.perf_counter()
                T, inf = mac(Pi, Qi, **mac_kw)
                secs = time.perf_counter() - ts
                res = success(pair, T)  # (ok, rre, rte), or indoor FPFH (ok_rmse, ok_rre_rte, rre, rte)
                ok, ok15, rre, rte = (res[0], res[0], res[1], res[2]) if len(res) == 3 else res
                res_all = np.linalg.norm(P @ T[:3, :3].T + T[:3, 3] - Q, axis=1)  # ratio order
                st = {"budget": b, "n": n, "s": secs, "ops": inf.get("ops", 0), "inliers": inf.get("inliers", 0),
                      "inliers_all": int((res_all < inl).sum()), "inliers_top250": int((res_all[:250] < inl).sum()),
                      "ratio_med": float(np.median(ratio_o[:n])) if n else 1.0,
                      "ok": bool(ok), "ok15": bool(ok15), "rre": round(float(rre), 4), "rte": round(float(rte), 5),
                      "T": [round(float(x), 6) for x in T.reshape(-1)],
                      "cliques": inf.get("cliques", 0), "kept": inf.get("kept", -1)}
                if n >= Nall:
                    full = dict(st)
            st["dpose_deg"], st["dpose_m"] = _pose_change(prev_T, T)
            prev_T = T
            stages.append(st)
            if n >= Nall:  # larger budgets would repeat the same computation
                for b2 in BUDGETS[len(stages):]:
                    stages.append({**st, "budget": b2, "s": 0.0, "ops": 0, "dpose_deg": 0.0, "dpose_m": 0.0,
                                   "repeat": True})
                break
        out[order] = stages
    return json.dumps(out)


def _run_task(task):
    return _run(*task)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subset", required=True)
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()
    with open(LOG_ROOT / f"budgetc_{args.subset}.jsonl") as f:
        want = {r["pair_id"]: r["N_all"] for r in map(json.loads, f) if r}
    out = LOG_ROOT / f"mac_{args.subset}.jsonl"
    done = {json.loads(x)["pair_id"] for x in open(out) if x.strip()} if out.exists() else set()
    # pairs already computed under another subset name with the same features: copy (same computation)
    other = {}
    for f in LOG_ROOT.glob("mac_*.jsonl"):
        if f != out:
            sub = f.stem[len("mac_"):]
            for line in open(f):
                if line.strip():
                    r = json.loads(line)
                    other.setdefault(_key(sub, r["pair_id"]), r)
    todo = [pid for pid in want if pid not in done]
    copied = 0
    with open(out, "a") as g:
        for pid in list(todo):
            r = other.get(_key(args.subset, pid))
            if r is not None:
                g.write(json.dumps({**r, "pair_id": pid}) + "\n")
                todo.remove(pid)
                copied += 1
    print(f"{args.subset}: {len(want)} pairs, {len(done)} done, {copied} copied, {len(todo)} to run", flush=True)
    t0 = time.time()
    # workers are replaced every 100 pairs, as igraph leaks one C-runtime stream per clique enumeration (acpr.mac);
    # multiprocessing.Pool, because ProcessPoolExecutor(max_tasks_per_child=...) hangs on Python 3.13.3 (measured)
    tasks = [(args.subset, pid, want[pid]) for pid in todo]
    with open(out, "a") as g, Pool(args.workers, maxtasksperchild=100) as pool:
        for k, res in enumerate(pool.imap_unordered(_run_task, tasks, chunksize=1)):
            g.write(res + "\n")
            if k % 50 == 0:
                g.flush()
                print(f"  {k + 1}/{len(todo)}  {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
