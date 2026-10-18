"""Budget logs on KITTI (fresh test set; same format as build_budget_logs.py).

Both orderings in one pass per pair (shared correspondences and full-budget run, timed in the
same run): logs/budget_kitti_{split}.jsonl (ratio order) and logs/budgetc_kitti_{split}.jsonl
(compatibility order). Splits: train (fixed 500-pair sample, for fitting), val (certification and
estimator thresholds), test (evaluated once).

Distance thresholds scale with the dataset's inlier threshold (0.6 m vs 0.1 m on 3DMatch):
inlier threshold and NMS radius 0.6 m; the compatibility thresholds of SC^2-PCR (d_thre) and
TurboReg (tau) are chosen on KITTI validation (--select-thresholds), and the ordering uses SC^2's d_thre.
The success flag stored in "ok15"/"ok" is the KITTI criterion (RE <= 5 deg, TE <= 0.6 m).

Usage: python -I -u scripts/build_budget_logs_kitti.py --select-thresholds
       python -I -u scripts/build_budget_logs_kitti.py --split {train|val|test} --workers 6
"""

from __future__ import annotations

import argparse
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "ACPR_KD_WORKERS"):
    os.environ.setdefault(var, "1")

import numpy as np  # noqa: E402

from acpr import LOG_ROOT, RESULTS_ROOT  # noqa: E402
from acpr import kitti as K  # noqa: E402

BUDGETS = (250, 500, 1000, 2000, 4000)
THR_FILE = RESULTS_ROOT / "kitti" / "thresholds.json"
INLIER = 0.6


def thresholds():
    with open(THR_FILE) as f:
        return json.load(f)


def _corr(pair):
    from acpr.estimators import nn_correspondences_bf

    rp, rf, _ = K.get_fpfh_kitti(pair.pcd0)
    sp, sf, _ = K.get_fpfh_kitti(pair.pcd1)
    t0 = time.perf_counter()
    P, Q, ratio = nn_correspondences_bf(sp, sf, rp, rf)  # exact NN by brute force (k-d trees are slow here)
    t_corr = time.perf_counter() - t0
    n = min(P.shape[0], BUDGETS[-1])
    return P[:n], Q[:n], ratio[:n], t_corr


def _pose_change(prev_T, T):
    if prev_T is None:
        return 180.0, 10.0
    R = prev_T[:3, :3].T @ T[:3, :3]
    return (float(np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1)))),
            float(np.linalg.norm(prev_T[:3, 3] - T[:3, 3])))


def _stage(fn, kw, Pi, Qi, P, Q, ratio_i, b, n, pair):
    ts = time.perf_counter()
    T, inf = fn(Pi, Qi, **kw)
    secs = time.perf_counter() - ts
    ok, rre, rte = K.success(pair.transform, T)
    res_all = np.linalg.norm(P @ T[:3, :3].T + T[:3, 3] - Q, axis=1)
    return T, {"budget": b, "n": n, "s": secs, "ops": inf.get("ops", 0), "inliers": inf.get("inliers", 0),
               "inliers_all": int((res_all < INLIER).sum()), "inliers_top250": int((res_all[:250] < INLIER).sum()),
               "ratio_med": float(np.median(ratio_i)) if n else 1.0, "ok": ok, "ok15": ok,
               "rre": round(rre, 4), "rte": round(rte, 5), "T": [round(float(x), 6) for x in T.reshape(-1)]}


def _ladder(fn, kw, P, Q, ratio, Po, Qo, ratio_o, pair, full_cache):
    Nall = P.shape[0]
    stages, prev_T = [], None
    for b in BUDGETS:
        n = min(b, Nall)
        if n >= Nall:
            if "full" not in full_cache:  # the standard full-budget run: ratio order, computed once per pair
                full_cache["full"] = _stage(fn, kw, P, Q, P, Q, ratio, b, n, pair)
            T, st = full_cache["full"][0], dict(full_cache["full"][1], budget=b)
        else:
            T, st = _stage(fn, kw, Po[:n], Qo[:n], P, Q, ratio_o[:n], b, n, pair)
        st["dpose_deg"], st["dpose_m"] = _pose_change(prev_T, T)
        prev_T = T
        stages.append(st)
        if n >= Nall:
            for b2 in BUDGETS[len(stages):]:
                stages.append({**st, "budget": b2, "s": 0.0, "ops": 0, "dpose_deg": 0.0, "dpose_m": 0.0, "repeat": True})
            break
    return stages


def _run(split: str, index: int) -> tuple[str, str]:
    from acpr.estimators import compat_order, sc2_pcr, turboreg

    thr = thresholds()
    sc2_kw = {"d_thre": thr["sc2_d_thre"], "inlier_thr": INLIER, "nms_radius": INLIER}
    tr_kw = {"tau": thr["turbo_tau"], "inlier_thr": INLIER}
    pair = K.load_kitti_pairs("train" if split == "calib" else split)[index]
    P, Q, ratio, t_corr = _corr(pair)
    Nall = P.shape[0]
    t0 = time.perf_counter()
    perm, ops_order, anchors = compat_order(P, Q, thr=thr["sc2_d_thre"], return_anchors=True)
    t_order = time.perf_counter() - t0
    gt_res = np.linalg.norm(P @ pair.transform[:3, :3].T + pair.transform[:3, 3] - Q, axis=1)
    base = {"pair_id": pair.pair_id, "subset": pair.subset, "scene": pair.scene, "overlap": 0.0,
            "rr_eligible": True, "N_all": int(Nall), "t_corr": t_corr}
    recs = {}
    caches = {"sc2": {}, "turbo": {}}
    for order in ("ratio", "compat"):
        if order == "compat":
            Po, Qo, ratio_o, res_o = P[perm], Q[perm], ratio[perm], gt_res[perm]
        else:
            Po, Qo, ratio_o, res_o = P, Q, ratio, gt_res
        rec = dict(base, order=order, t_order=t_order if order == "compat" else 0.0,
                   ops_order=ops_order if order == "compat" else 0,
                   gt_inliers=int((gt_res < INLIER).sum()),
                   gt_inliers_by_budget=[int((res_o[:b] < INLIER).sum()) for b in BUDGETS])
        if order == "compat":
            rec["anchors_true"] = int((gt_res[anchors] < INLIER).sum())
        rec["sc2"] = _ladder(sc2_pcr, sc2_kw, P, Q, ratio, Po, Qo, ratio_o, pair, caches["sc2"])
        rec["turbo"] = _ladder(turboreg, tr_kw, P, Q, ratio, Po, Qo, ratio_o, pair, caches["turbo"])
        recs[order] = json.dumps(rec)
    return recs["ratio"], recs["compat"]


GRID = {"sc2": [0.6 * k for k in (0.5, 1.0, 2.0)], "turbo": [0.012 * K.SCALE * k for k in (1.0, 2.5, 5.0, 10.0)]}


def _val_full(index):
    """Full-budget success and time of every estimator configuration on one validation pair."""
    from acpr.estimators import sc2_pcr, turboreg

    pair = K.load_kitti_pairs("val")[index]
    P, Q, _, _ = _corr(pair)  # once per pair, shared by all configurations
    out = []
    for est, values in GRID.items():
        for value in values:
            ts = time.perf_counter()
            if est == "sc2":
                T, _ = sc2_pcr(P, Q, d_thre=value, inlier_thr=INLIER, nms_radius=INLIER)
            else:
                T, _ = turboreg(P, Q, tau=value, inlier_thr=INLIER)
            out.append((est, value, K.success(pair.transform, T)[0], time.perf_counter() - ts))
    return out


def select_thresholds(workers):
    """Choose each estimator's compatibility threshold by full-budget recall on KITTI validation."""
    grid = GRID
    n_val = len(K.load_kitti_pairs("val"))
    acc: dict = {}
    with ProcessPoolExecutor(workers) as ex:
        for res in ex.map(_val_full, range(n_val), chunksize=2):
            for est, v, ok, s in res:
                a = acc.setdefault((est, v), [0, 0, 0.0])
                a[0] += ok
                a[1] += 1
                a[2] += s
    table = {f"{e}@{v:.3f}": {"rr": a[0] / a[1], "s": a[2] / a[1]} for (e, v), a in acc.items()}
    best = {}
    for est in grid:
        cands = [(a[0] / a[1], -a[2] / a[1], v) for (e, v), a in acc.items() if e == est]
        best[est] = max(cands)[2]  # highest recall, then fastest
    THR_FILE.parent.mkdir(parents=True, exist_ok=True)
    out = {"sc2_d_thre": best["sc2"], "turbo_tau": best["turbo"], "validation": table}
    with open(THR_FILE, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["train", "val", "test", "calib"])
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--select-thresholds", action="store_true")
    args = ap.parse_args()
    if args.select_thresholds:
        select_thresholds(args.workers)
        return
    pairs = K.load_kitti_pairs("train" if args.split == "calib" else args.split)
    idx = {"train": K.train_fit, "calib": K.calib_indices}.get(args.split, lambda: list(range(len(pairs))))()
    outs = [LOG_ROOT / f"{pf}_kitti_{args.split}.jsonl" for pf in ("budget", "budgetc")]
    done = {json.loads(x)["pair_id"] for x in open(outs[1]) if x.strip()} if outs[1].exists() else set()
    todo = [i for i in idx if pairs[i].pair_id not in done]
    print(f"kitti {args.split}: {len(todo)} pairs to run", flush=True)
    t0 = time.time()
    with open(outs[0], "a") as f0, open(outs[1], "a") as f1, ProcessPoolExecutor(args.workers) as ex:
        futs = [ex.submit(_run, args.split, i) for i in todo]
        for n, fu in enumerate(as_completed(futs), 1):
            r0, r1 = fu.result()
            f0.write(r0 + "\n")
            f1.write(r1 + "\n")
            f0.flush()
            f1.flush()
            if n % 50 == 0 or n == len(futs):
                el = time.time() - t0
                print(f"  {n}/{len(futs)}  {el:.0f}s  ETA {el / n * (len(futs) - n):.0f}s", flush=True)


if __name__ == "__main__":
    main()
