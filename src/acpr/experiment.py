"""Per-pair experiment record: full search lattice + RANSAC trajectory + SC^2, all evaluated.

One call of `run_pair` produces everything needed to evaluate any adaptive policy
offline: every (rotation density, basin) state of the pose search, every RANSAC
checkpoint, the adaptive-RANSAC stopping point and the SC^2 estimate, each with its
cost and its success under both protocols.
"""

from __future__ import annotations

import json
import time

import numpy as np

from acpr.data import THREEDMATCH_ROOT, Pair, load_benchmark_gt, load_fragment
from acpr.features import correspondences, inlier_mask
from acpr.light import LightConfig, sc2_estimate
from acpr.metrics import evaluate_transform, info_matrix
from acpr.pose_search import SearchConfig, ransac_trajectory, search_lattice

_VAL_INFO: dict | None = None


def _val_info() -> dict:
    global _VAL_INFO
    if _VAL_INFO is None:
        with open(THREEDMATCH_ROOT / "metadata" / "val_info.json") as f:
            _VAL_INFO = json.load(f)
    return _VAL_INFO


def info_and_eligibility(pair: Pair):
    """Information matrix for the RMSE criterion and whether the pair counts for RR."""
    if pair.subset in ("3DMatch", "3DLoMatch"):
        gt = load_benchmark_gt(pair.subset, pair.scene).get((pair.frag0, pair.frag1))
        if gt is None:
            return None, False
        return gt[1], pair.frag1 > pair.frag0 + 1  # official protocol: non-adjacent pairs only
    if pair.subset == "val":
        return np.asarray(_val_info()[pair.pair_id]), True
    return info_matrix(load_fragment(pair.pcd0), load_fragment(pair.pcd1), pair.transform), True


def _ev(pair: Pair, T: np.ndarray, info) -> dict:
    e = evaluate_transform(pair.transform, T, info)
    return {
        "ok": bool(e["ok_rmse"]),
        "ok15": bool(e["ok_rre_rte"]),
        "rre": round(e["rre"], 4),
        "rte": round(e["rte"], 5),
        "rmse": round(e["rmse"], 5) if np.isfinite(e["rmse"]) else None,
    }


def _round_T(T: np.ndarray) -> list:
    return [round(float(x), 6) for x in np.asarray(T).reshape(-1)]


def run_pair(pair: Pair, search_cfg: SearchConfig | None = None, n_max: int = 1000, variant: str = "full") -> dict:
    """variant: "full" = full voting + baselines; "psh" = progressive successive-halving voting only."""
    search_cfg = search_cfg or SearchConfig()
    if variant == "psh":
        search_cfg = SearchConfig(**{**search_cfg.__dict__, "progressive": True})
    info, eligible = info_and_eligibility(pair)
    c = correspondences(pair, n_max=n_max)
    P, Q = c["P"], c["Q"]
    if variant == "psh":  # most distinctive correspondences first
        o = np.argsort(c["ratio"], kind="stable")
        P, Q = P[o], Q[o]
    N = int(P.shape[0])
    rec = {
        "pair_id": pair.pair_id,
        "subset": pair.subset,
        "scene": pair.scene,
        "frag0": pair.frag0,
        "frag1": pair.frag1,
        "overlap": pair.overlap,
        "rr_eligible": bool(eligible and info is not None),
        "N": N,
        "n_mutual": c["n_mutual"],
        "n_src": int(c["src_pts"].shape[0]),
        "n_ref": int(c["ref_pts"].shape[0]),
        "gt_inliers": int(inlier_mask(P, Q, pair.transform).sum()) if N else 0,
        "t_features": round(c["t_features"], 5),
        "t_matching": round(c["t_matching"], 5),
    }

    # --- pose search lattice
    center = c["src_pts"].mean(axis=0) if c["src_pts"].shape[0] else np.zeros(3)
    levels = search_lattice(P, Q, center, search_cfg) if N >= 3 else []
    rec["search"] = []
    for lvl in levels:
        rec["search"].append(
            {
                "M": lvl.M,
                "h": round(lvl.h, 4),
                "sigma": round(lvl.sigma, 5),
                "vote_cost": lvl.vote_cost,
                "s_vote": round(lvl.seconds_vote, 5),
                "s_extract": round(lvl.seconds_extract, 5),
                "vote_top": lvl.vote_top,
                "vote_mean": round(lvl.vote_mean, 3),
                "vote_std": round(lvl.vote_std, 3),
                "basins": [
                    {
                        "rank": b["rank"],
                        "vote": b["vote"],
                        "consensus": b["consensus"],
                        "iters": b["iters"],
                        "cost": b["cost"],
                        "s": round(b["seconds"], 6),
                        "T": _round_T(b["T"]),
                        **_ev(pair, b["T"], info),
                    }
                    for b in lvl.basins
                ],
            }
        )

    # --- RANSAC trajectory (fixed budgets) and its adaptive stopping point
    if variant == "psh":
        rec["variant"] = "psh"
        return rec
    if N >= 3:
        rs = ransac_trajectory(P, Q, eps=search_cfg.eps)
        rec["ransac"] = [
            {"k": t["sampled"], "scored": t["scored"], "consensus": t["consensus"], "s": round(t["seconds"], 5),
             **_ev(pair, t["T"], info)}
            for t in rs["trajectory"]
        ]
        a = rs["adaptive"]
        rec["ransac_adaptive"] = {"k": a["sampled"], "scored": a["scored"], "consensus": a["consensus"],
                                  "s": round(a["seconds"], 5), "capped": bool(a.get("capped", False)),
                                  **_ev(pair, a["T"], info)}
        # --- SC^2 on the same correspondences
        t0 = time.perf_counter()
        T_sc2, sig = sc2_estimate(P, Q, LightConfig())
        rec["sc2"] = {"s": round(time.perf_counter() - t0, 5), "consensus": sig.get("best_inliers", 0),
                      **_ev(pair, T_sc2, info)}
    else:
        rec["ransac"], rec["ransac_adaptive"], rec["sc2"] = [], None, None
    return rec
