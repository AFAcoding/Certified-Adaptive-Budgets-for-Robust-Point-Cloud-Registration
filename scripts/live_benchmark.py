"""Live, single-process benchmark of the adaptive pose search against standard estimators.

The offline analysis evaluates stopping policies exactly from logs. This script runs
the *online* system end to end on a sample of test pairs and times every method in
one process, sequentially, on the same correspondences:

  * adaptive search: stages run lazily; after each stage the trained controller
    (logistic success models + Markov stop table, certified lambda from the analysis
    summary) decides whether to stop;
  * exhaustive search (the last stage of the same schedule);
  * RANSAC with the classical adaptive stopping rule (p = 0.999, cap 100k);
  * RANSAC with a fixed budget of 100k hypotheses;
  * SC^2.

It also checks that the live adaptive decisions reproduce the offline evaluation.

Usage:
  python -I -u scripts/live_benchmark.py --summary results/<tag>/summary.json --prefix psh
         --schedule to2048 --per-set 150
"""

from __future__ import annotations

import argparse
import json
import time

import numpy as np

from acpr import LOG_ROOT, RESULTS_ROOT
from acpr import analysis as A
from acpr.data import load_pairs
from acpr.experiment import info_and_eligibility
from acpr.features import correspondences
from acpr.light import LightConfig, kabsch, sc2_estimate
from acpr.metrics import evaluate_transform
from acpr.pose_search import (SearchConfig, best_translation, get_grid, refine, rot_angle, vote_scores,
                              vote_scores_progressive)


class LiveLevel:
    """One density level: votes and extracts candidates once, refines basins on demand."""

    def __init__(self, P, Q, center, cfg: SearchConfig, M: int, max_basins: int):
        self.P, self.Q, self.center, self.cfg = P, Q, center, cfg
        lv = search_level(P, Q, center, cfg, M, max_basins, refine_n=0)
        self.rec, self.coarse, self.h, self.Pc = lv["rec"], lv["coarse"], lv["h"], lv["Pc"]
        self.rec["coarse_votes"] = [c[2] for c in self.coarse]

    def ensure(self, b: int):
        N = self.Pc.shape[0]
        while len(self.rec["basins"]) < min(b, len(self.coarse)):
            R0, t0_, vote, rank = self.coarse[len(self.rec["basins"])]
            ts = time.perf_counter()
            R, t, cons, iters = refine(R0, t0_, self.Pc, self.Q, tau0=self.h, eps=self.cfg.eps)
            T = np.eye(4)
            T[:3, :3] = R
            T[:3, 3] = t - R @ self.center
            self.rec["basins"].append({"T": T.reshape(-1).tolist(), "consensus": cons, "vote": vote, "rank": rank,
                                       "iters": iters, "cost": iters * N, "s": time.perf_counter() - ts,
                                       "ok": False, "ok15": False})


def search_level(P, Q, center, cfg: SearchConfig, M: int, n_basins: int, refine_n: int | None = None) -> dict:
    """One density level (identical to search_lattice). Refines refine_n basins (default: all found)."""
    grid = get_grid(max(cfg.densities), cfg.seed)
    Pc = (P - center).astype(np.float32)
    N = Pc.shape[0]
    r_p = float(np.percentile(np.linalg.norm(Pc, axis=1), cfg.radius_pct)) if N else 1.0
    sigma = grid.coverage(M)[cfg.coverage_stat]
    h = max(cfg.h_min, cfg.kappa * sigma * r_p)
    t0 = time.perf_counter()
    if cfg.progressive:
        scores, vote_cost, first = vote_scores_progressive(grid.R[:M], Pc, Q, h, keep_min=cfg.top_t,
                                                           first_frac=cfg.first_frac, keep_frac=cfg.keep_frac)
        stats = first[np.isfinite(first)]
    else:
        scores = vote_scores(grid.R[:M], Pc, Q, h)
        vote_cost, stats = M * N, scores
    t_vote = time.perf_counter() - t0
    order = np.argsort(-scores, kind="stable")[: cfg.top_t]
    coarse = []
    t0 = time.perf_counter()
    for rank, i in enumerate(order):
        t, _ = best_translation(grid.R[i].astype(np.float64), Pc, Q, h)
        if not any(rot_angle(grid.R[i], c[0]) < cfg.nms_factor * sigma and np.linalg.norm(t - c[1]) < h for c in coarse):
            coarse.append((grid.R[i].astype(np.float64), t, int(scores[i]), rank))
        if len(coarse) >= n_basins:
            break
    t_ext = time.perf_counter() - t0
    basins = []
    for R0, t0_, vote, rank in coarse[: (len(coarse) if refine_n is None else refine_n)]:
        ts = time.perf_counter()
        R, t, cons, iters = refine(R0, t0_, Pc, Q, tau0=h, eps=cfg.eps)
        T = np.eye(4)
        T[:3, :3] = R
        T[:3, 3] = t - R @ center
        basins.append({"T": T.reshape(-1).tolist(), "consensus": cons, "vote": vote, "rank": rank, "iters": iters,
                       "cost": iters * N, "s": time.perf_counter() - ts, "ok": False, "ok15": False})
    rec = {"M": M, "vote_cost": int(vote_cost), "s_vote": t_vote, "s_extract": t_ext,
           "vote_top": np.sort(scores)[::-1][:8].tolist(), "vote_mean": float(stats.mean()),
           "vote_std": float(stats.std()), "basins": basins}
    return {"rec": rec, "coarse": coarse, "h": h, "Pc": Pc}


def adaptive_search(P, Q, center, cfg, schedule, controller):
    """Run stages lazily; stop when the controller says so. Returns (T, stage, CE)."""
    clf_now, clf_final, mdp, table, feats = controller
    rec = {"N": int(P.shape[0]), "search": {}}
    n_needed = {}
    for d, b in schedule:
        n_needed[d] = max(n_needed.get(d, 0), b)
    live: dict[int, LiveLevel] = {}
    levels = {}
    for s, (d, b) in enumerate(schedule):
        if d not in live:  # vote and extract once, for the most basins this level will ever need
            live[d] = LiveLevel(P, Q, center, cfg, cfg.densities[d], n_needed[d])
        live[d].ensure(b)
        levels[d] = live[d].rec
        rec_partial = {"N": rec["N"], "search": [levels.get(i, {"basins": [], "vote_cost": 0, "s_vote": 0.0,
                                                                  "s_extract": 0.0, "vote_top": [0], "vote_mean": 0.0,
                                                                  "vote_std": 1.0})
                                                  for i in range(len(cfg.densities))]}
        tr = A.search_trajectory(rec_partial, schedule=schedule[: s + 1])
        st = tr[-1]
        x = np.array([[st[f] for f in feats]])
        st["p_now"] = float(clf_now.predict_proba(x)[0, 1])
        st["p_final"] = float(clf_final.predict_proba(x)[0, 1])
        if s == len(schedule) - 1 or table[s, mdp.state(st)]:
            # incumbent = basin with max consensus among refined ones (same rule as offline)
            refined = []
            seen = {}
            for dd, bb in schedule[: s + 1]:
                for i in range(seen.get(dd, 0), min(bb, len(levels[dd]["basins"]))):
                    refined.append(levels[dd]["basins"][i])
                seen[dd] = max(seen.get(dd, 0), min(bb, len(levels[dd]["basins"])))
            inc = max(refined, key=lambda x_: x_["consensus"]) if refined else None
            T = np.asarray(inc["T"]).reshape(4, 4) if inc else np.eye(4)
            return T, s, st["ce"]
    return np.eye(4), len(schedule) - 1, 0.0


def ransac_live(P, Q, eps=0.10, confidence=0.999, k_max=100000, adaptive=True, batch=500, edge_ratio=0.9, seed=0):
    rng = np.random.default_rng(seed)
    N = P.shape[0]
    P64, Q64 = P.astype(np.float64), Q.astype(np.float64)
    best_cnt, best_T, sampled = -1, np.eye(4), 0
    while sampled < k_max:
        idx = rng.integers(0, N, size=(batch, 3))
        sp, sq = P64[idx], Q64[idx]
        dp = np.linalg.norm(sp[:, [0, 0, 1]] - sp[:, [1, 2, 2]], axis=2)
        dq = np.linalg.norm(sq[:, [0, 0, 1]] - sq[:, [1, 2, 2]], axis=2)
        ok = (np.minimum(dp, dq) > edge_ratio * np.maximum(dp, dq)).all(axis=1) & (dp.min(axis=1) > 1e-3)
        sampled += batch
        if ok.any():
            Ts = kabsch(sp[ok], sq[ok])
            res = np.linalg.norm(np.einsum("bij,nj->bni", Ts[:, :3, :3], P64) + Ts[:, None, :3, 3] - Q64[None], axis=2)
            cnt = (res < eps).sum(axis=1)
            j = int(cnt.argmax())
            if cnt[j] > best_cnt:
                best_cnt, best_T = int(cnt[j]), Ts[j]
        if adaptive and best_cnt > 0:
            w = best_cnt / N
            if sampled >= np.log(1 - confidence) / np.log(max(1 - w**3, 1e-12)):
                break
    m = np.linalg.norm(P64 @ best_T[:3, :3].T + best_T[:3, 3] - Q64, axis=1) < eps
    return kabsch(P64[m], Q64[m]) if m.sum() >= 3 else best_T


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True)
    ap.add_argument("--prefix", default="psh")
    ap.add_argument("--schedule", default="to2048")
    ap.add_argument("--per-set", type=int, default=150)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    summary = json.loads(open(args.summary).read())
    lam = summary["certified"]["mdp"]
    schedule = A.SCHEDULES[args.schedule]
    cfg = SearchConfig(progressive=(args.prefix == "psh"))

    # controller fitted exactly as in analyze.py (training-scene logs)
    with open(LOG_ROOT / f"{args.prefix}_train.jsonl") as f:
        train = [r for r in (json.loads(x) for x in f if x.strip()) if r.get("search")]
    trajs = [A.search_trajectory(r, schedule=schedule) for r in train]
    feats = A.SEARCH_FEATURES
    X, y = A.rows(trajs, feats, "ok")
    clf_now, clf_final = A.fit_classifier(X, y), A.fit_classifier(X, A.final_labels(trajs))
    A.attach_scores(trajs, feats, clf_now, clf_final)
    mdp = A.MDPController(trajs)
    table = mdp.solve(lam)
    controller = (clf_now, clf_final, mdp, table, feats)

    offline = {}
    for subset in ["3DMatch", "3DLoMatch"]:
        with open(LOG_ROOT / f"{args.prefix}_{subset}.jsonl") as f:
            for x in f:
                if x.strip():
                    r = json.loads(x)
                    offline[r["pair_id"]] = r

    rows = []
    for subset in ["3DMatch", "3DLoMatch"]:
        pairs = [p for p in load_pairs(subset) if p.pair_id in offline]
        rng = np.random.default_rng(0)
        pairs = [pairs[i] for i in sorted(rng.choice(len(pairs), min(args.per_set, len(pairs)), replace=False))]
        for p in pairs:
            info, elig = info_and_eligibility(p)
            c = correspondences(p)
            P, Q = c["P"], c["Q"]
            if cfg.progressive:
                o = np.argsort(c["ratio"], kind="stable")
                P, Q = P[o], Q[o]
            center = c["src_pts"].mean(axis=0)
            res = {"pair_id": p.pair_id, "subset": subset, "scene": p.scene, "eligible": bool(elig and info is not None)}

            t0 = time.perf_counter()
            T, stage, ce = adaptive_search(P, Q, center, cfg, schedule, controller)
            res["adaptive_s"] = time.perf_counter() - t0
            res["adaptive_ok"] = evaluate_transform(p.transform, T, info)["ok_rmse"]
            res["adaptive_stage"], res["adaptive_ce"] = stage, ce
            # offline replay of the same policy, for consistency
            tr_off = A.search_trajectory(offline[p.pair_id], schedule=schedule)
            A.attach_scores([tr_off], feats, clf_now, clf_final)
            k_off = next((st["stage"] for st in tr_off if table[st["stage"], mdp.state(st)]), len(tr_off) - 1)
            res["offline_stage"], res["offline_ok"] = k_off, tr_off[k_off]["ok"]

            t0 = time.perf_counter()
            lv = search_level(P, Q, center, cfg, cfg.densities[schedule[-1][0]], schedule[-1][1])["rec"]
            inc = max(lv["basins"], key=lambda b: b["consensus"])
            res["static_last_s"] = time.perf_counter() - t0
            res["static_last_ok"] = evaluate_transform(p.transform, np.asarray(inc["T"]).reshape(4, 4), info)["ok_rmse"]

            for name, kw in [("ransac_classical", {"adaptive": True}), ("ransac_100k", {"adaptive": False})]:
                t0 = time.perf_counter()
                T = ransac_live(P, Q, **kw)
                res[f"{name}_s"] = time.perf_counter() - t0
                res[f"{name}_ok"] = evaluate_transform(p.transform, T, info)["ok_rmse"]
            t0 = time.perf_counter()
            T, _ = sc2_estimate(P, Q, LightConfig())
            res["sc2_s"] = time.perf_counter() - t0
            res["sc2_ok"] = evaluate_transform(p.transform, T, info)["ok_rmse"]
            res["features_s"] = c["t_features"] + c["t_matching"]
            rows.append(res)
            if len(rows) % 25 == 0:
                print(f"  {len(rows)} pairs", flush=True)

    out = args.out or str(RESULTS_ROOT / f"live_{args.prefix}_{args.schedule}.json")
    with open(out, "w") as f:
        json.dump(rows, f, indent=1, default=float)
    # summary
    print(f"\nlive benchmark ({len(rows)} pairs, single process):")
    for subset in ["3DMatch", "3DLoMatch"]:
        rs = [r for r in rows if r["subset"] == subset and r["eligible"]]
        if not rs:
            continue
        sc = np.array([r["scene"] for r in rs])
        print(f"  {subset} ({len(rs)} pairs)")
        for m in ["adaptive", "static_last", "ransac_classical", "ransac_100k", "sc2"]:
            ok = np.array([r[f"{m}_ok"] for r in rs])
            t = np.array([r[f"{m}_s"] for r in rs])
            print(f"    {m:18s} RR {100 * A.scene_rr(ok, sc):5.1f}%  mean {1e3 * t.mean():7.1f} ms  median {1e3 * np.median(t):7.1f} ms")
        agree = np.mean([r["adaptive_stage"] == r["offline_stage"] for r in rs])
        print(f"    live/offline stop-stage agreement: {100 * agree:.1f}%")


if __name__ == "__main__":
    main()
