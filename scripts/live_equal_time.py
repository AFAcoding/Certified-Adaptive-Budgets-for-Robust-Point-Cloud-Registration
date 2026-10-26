"""Live single-process timing of every equal-time variant on the same test pairs.

For each sampled 3DMatch test pair (same sample as live_budget.py) and each estimator,
times in one process, with the run order rotated from pair to pair:
  full           the standard full-budget run
  cab            CAB (compatibility order, group-conditional certificate; ordering included)
  ratio@N        fixed budget, top-N by Lowe ratio
  compat@N       fixed budget, top-N by compatibility (ordering included)
  rand@N         uniform random subset
  fm1@N, fm2@N   FastMAC-style sampling, first-order / second-order graph (signal included)
  seeds@r / k1@K SC^2 with fewer seeds / TurboReg with fewer cliques, all correspondences
  topk@K         MAC keeping the Top-K node-guided cliques, all correspondences (--estimators mac; PROTOCOL.md,
                 protocol v3, addendum D)
Accuracy for the paper comes from the logs on the full test set; this run provides wall-clock time.

Usage: python -I -u scripts/live_equal_time.py [--per-set 100] [--subset 3DMatch] [--estimators sc2,turbo | mac]
"""

import argparse
import json
import sys
import time
import zlib
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_budget as B  # noqa: E402
import live_budget as L  # noqa: E402

from acpr import RESULTS_ROOT  # noqa: E402
from acpr.estimators import compat_order, fastmac_draw, fastmac_probs, nn_correspondences  # noqa: E402

BUDGETS = (250, 500, 1000, 2000)


def time_pair(ds, est, ctrl, p, j, subset, warm_up=False):
    """Time every variant on pair p; j, the pair's position in the sample, rotates the order of the runs. warm_up: one
    untimed full-budget run first (a fresh worker process)."""
    fn, kw = L.FNS[est], ds.kwargs(est)
    fn = (lambda f: lambda *a, **k: f(*a, **{**kw, **k}))(fn)  # the estimator's settings for this dataset
    info = ds.info(p)
    rp, rf, _ = ds.features(p.pcd0)
    sp, sf, _ = ds.features(p.pcd1)
    P, Q, ratio = nn_correspondences(sp, sf, rp, rf)
    n = min(P.shape[0], 4000)
    P, Q, ratio = P[:n], Q[:n], ratio[:n]
    seed = zlib.crc32(p.pair_id.encode())
    if warm_up:
        fn(P, Q)

    def timed(f):
        t0 = time.perf_counter()
        out = f()
        return out, time.perf_counter() - t0

    jobs = {"full": lambda: timed(lambda: fn(P, Q))[1],
            "cab": lambda: timed(lambda: ctrl.run(fn, P, Q, ratio, info, p))[1]}
    for b in BUDGETS:
        jobs[f"ratio@{b}"] = (lambda b=b: timed(lambda: fn(P[:b], Q[:b]))[1])
        jobs[f"compat@{b}"] = (lambda b=b: timed(lambda: fn(*(lambda o: (P[o[:b]], Q[o[:b]]))(compat_order(P, Q)[0])))[1])
        jobs[f"rand@{b}"] = (lambda b=b: timed(
            lambda: fn(*(lambda i: (P[i], Q[i]))(np.sort(np.random.default_rng(seed + b).choice(n, min(b, n), replace=False)))))[1])
    if est == "sc2":
        for r in (0.025, 0.01):
            jobs[f"seeds@{r}"] = (lambda r=r: timed(lambda: fn(P, Q, ratio=r))[1])
    elif est == "turbo":
        for k in (500, 250):
            jobs[f"k1@{k}"] = (lambda k=k: timed(lambda: fn(P, Q, k1=k))[1])
    else:  # MAC: the two smallest values of the authors' Top-K ablation
        for k in (200, 100):
            jobs[f"topk@{k}"] = (lambda k=k: timed(lambda: fn(P, Q, top_k=k))[1])
    names = list(jobs)
    names = names[j % len(names):] + names[: j % len(names)]
    row = {"est": est, "subset": subset, "pair_id": p.pair_id, "scene": p.scene, "N_all": int(n)}
    for name in names:
        row[name] = jobs[name]()
    # FastMAC-style samplers: signal once per pair and order (charged to every budget), then the estimator
    for tag, second in (("fm1", False), ("fm2", True)):
        probs, t_sig = timed(lambda second=second: fastmac_probs(P, Q, second_order=second))
        row[f"{tag}_signal"] = t_sig
        for b in BUDGETS:
            row[f"{tag}@{b}"] = t_sig + timed(
                lambda b=b: fn(*(lambda i: (P[i], Q[i]))(fastmac_draw(probs, b, np.random.default_rng(seed + b)))))[1]
    return row


def sample(ds, subset, per_set):
    offline = {r["pair_id"] for r in B.load(subset, "budgetc")}
    pairs = [p for p in ds.pairs(subset) if p.pair_id in offline]
    rng = np.random.default_rng(0)
    return [pairs[i] for i in sorted(rng.choice(len(pairs), min(per_set, len(pairs)), replace=False))]


_W = {}


def _worker_init(dataset, method, est):
    _W["ds"] = L.make_dataset(dataset)
    _W["ctrl"] = L.Controller("budgetc" + ("+v3" if method == "v3" else ""), est, "extended", _W["ds"])
    _W["est"], _W["warm"] = est, False


def _worker_pair(args):
    """One pair in a recycled worker process (MAC: igraph leaves one C-runtime stream open per clique search)."""
    j, p, subset = args
    row = time_pair(_W["ds"], _W["est"], _W["ctrl"], p, j, subset, warm_up=not _W["warm"])
    _W["warm"] = True
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-set", type=int, default=100)
    ap.add_argument("--subset", default="3DMatch")
    ap.add_argument("--dataset", default="3dmatch", help="whose certified CAB to time (e.g. v2_indoor_fpfh)")
    ap.add_argument("--method", default="v2", choices=["v2", "v3"], help="v3: classifier chosen on the fitting "
                    "pairs and hardness gate (protocol v3)")
    ap.add_argument("--estimators", default="sc2,turbo", help="sc2,turbo (one process) or mac (recycled worker)")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    ds = L.make_dataset(args.dataset)
    ests = args.estimators.split(",")
    rows = []
    for est in ests:
        pairs = sample(ds, args.subset, args.per_set)
        if est == "mac":  # one worker at a time, replaced every 25 pairs, with an untimed warm-up run
            with Pool(1, initializer=_worker_init, initargs=(args.dataset, args.method, est), maxtasksperchild=25) as pool:
                for j, row in enumerate(pool.imap(_worker_pair, [(j, p, args.subset) for j, p in enumerate(pairs)])):
                    rows.append(row)
                    if (j + 1) % 25 == 0:
                        print(f"  {est} {j + 1}/{len(pairs)}", flush=True)
            continue
        ctrl = L.Controller("budgetc" + ("+v3" if args.method == "v3" else ""), est, "extended", ds)
        for j, p in enumerate(pairs):
            rows.append(time_pair(ds, est, ctrl, p, j, args.subset))
            if (j + 1) % 25 == 0:
                print(f"  {est} {j + 1}/{len(pairs)}", flush=True)
    tag = "" if ests == ["sc2", "turbo"] else "_" + "_".join(ests)
    out = RESULTS_ROOT / "budget" / f"live_equal_time_{args.subset}{'_v3' if args.method == 'v3' else ''}{tag}.json"
    with open(out, "w") as f:
        json.dump(rows, f, indent=1)
    for est in ests:
        rs = [r for r in rows if r["est"] == est]
        keys = [k for k in rs[0] if k not in ("est", "subset", "pair_id", "scene", "N_all")]
        print(est, " ".join(f"{k}={1e3 * np.mean([r[k] for r in rs]):.0f}ms" for k in keys))


if __name__ == "__main__":
    main()
