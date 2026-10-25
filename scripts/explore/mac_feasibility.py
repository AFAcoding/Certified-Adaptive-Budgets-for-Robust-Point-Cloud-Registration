"""Feasibility of MAC as a third estimator (development pairs only): runtime and success at every budget of the
compatibility-ordered ladder, next to SC2-PCR on the same correspondences.

Usage: python -I scripts/explore/mac_feasibility.py [n_pairs] [subset]
Writes results/explore/mac_feasibility_<subset>.json
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from acpr import RESULTS_ROOT  # noqa: E402
from acpr.data import load_pairs  # noqa: E402
from acpr.estimators import compat_order, nn_correspondences, sc2_pcr  # noqa: E402
from acpr.features import get_fpfh  # noqa: E402
from acpr.mac import mac  # noqa: E402
from acpr.metrics import rre_rte  # noqa: E402

BUDGETS = (250, 500, 1000, 2000, 4000)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    subset = sys.argv[2] if len(sys.argv) > 2 else "3DMatch"
    assert "blind" not in subset
    pairs = load_pairs(subset)
    idx = sorted(np.random.default_rng(21).choice(len(pairs), n, replace=False).tolist())
    rows = []
    for i in idx:
        p = pairs[i]
        rp, rf, _ = get_fpfh(p.pcd0)
        sp, sf, _ = get_fpfh(p.pcd1)
        P, Q, ratio = nn_correspondences(sp, sf, rp, rf)
        P, Q = P[:4000], Q[:4000]
        perm, _ = compat_order(P, Q, thr=0.10)
        row = {"pair_id": p.pair_id, "N": int(P.shape[0])}
        for b in BUDGETS:
            m = min(b, P.shape[0])
            Pi, Qi = (P[perm[:m]], Q[perm[:m]]) if m < P.shape[0] else (P, Q)
            for name, fn in (("mac", mac), ("sc2", sc2_pcr)):
                t0 = time.perf_counter()
                T, inf = fn(Pi, Qi)
                s = time.perf_counter() - t0
                rre, rte = rre_rte(p.transform, T)
                row[f"{name}@{b}"] = {"s": s, "ok": bool(rre <= 15 and rte <= 0.3),
                                     "cliques": inf.get("cliques"), "selected": inf.get("selected")}
        rows.append(row)
        print(p.pair_id, " ".join(f"{b}:mac {row[f'mac@{b}']['s']:.2f}s/{int(row[f'mac@{b}']['ok'])} "
                                  f"sc2 {row[f'sc2@{b}']['s']:.2f}s/{int(row[f'sc2@{b}']['ok'])}" for b in BUDGETS),
              flush=True)
    summ = {b: {"mac_s": float(np.mean([r[f"mac@{b}"]["s"] for r in rows])),
                "sc2_s": float(np.mean([r[f"sc2@{b}"]["s"] for r in rows])),
                "mac_ok": float(np.mean([r[f"mac@{b}"]["ok"] for r in rows])),
                "sc2_ok": float(np.mean([r[f"sc2@{b}"]["ok"] for r in rows])),
                "mac_cliques_max": int(max(r[f"mac@{b}"]["cliques"] or 0 for r in rows))} for b in BUDGETS}
    print(json.dumps(summ, indent=1))
    (RESULTS_ROOT / "explore" / f"mac_feasibility_{subset}.json").write_text(json.dumps({"rows": rows, "summary": summ},
                                                                                      indent=1, default=float))


if __name__ == "__main__":
    main()
