"""Reproduction check: SC^2-PCR and TurboReg re-implementations vs. their published recall.

Published (3DMatch, FPFH, success = RE <= 15 deg and TE <= 30 cm, all 1,623 pairs):
SC^2-PCR 83.73 %, TurboReg 84.10 % (TurboReg paper, Table 1).

Usage: python -I -u scripts/validate_estimators.py [every=10] [n_max=5000]
"""

import sys
import time

import numpy as np

from acpr.data import load_pairs
from acpr.estimators import nn_correspondences, sc2_pcr, turboreg
from acpr.features import get_fpfh
from acpr.metrics import rre_rte


def main():
    every = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    n_max = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    pairs = load_pairs("3DMatch")[::every]
    res = {"sc2": [], "turbo": []}
    t = {"sc2": 0.0, "turbo": 0.0}
    for k, p in enumerate(pairs):
        rp, rf, _ = get_fpfh(p.pcd0)
        sp, sf, _ = get_fpfh(p.pcd1)
        P, Q, _ = nn_correspondences(sp, sf, rp, rf)
        P, Q = P[:n_max], Q[:n_max]
        for name, fn in [("sc2", sc2_pcr), ("turbo", turboreg)]:
            t0 = time.perf_counter()
            T, info = fn(P, Q)
            t[name] += time.perf_counter() - t0
            rre, rte = rre_rte(p.transform, T)
            res[name].append(rre <= 15 and rte <= 0.30)
        if (k + 1) % 25 == 0:
            print(f"  {k + 1}/{len(pairs)}  SC2 {100 * np.mean(res['sc2']):.1f}%  TurboReg {100 * np.mean(res['turbo']):.1f}%", flush=True)
    n = len(pairs)
    print(f"pairs {n}: SC2 RR {100 * np.mean(res['sc2']):.2f}% ({1e3 * t['sc2'] / n:.0f} ms/pair), "
          f"TurboReg RR {100 * np.mean(res['turbo']):.2f}% ({1e3 * t['turbo'] / n:.0f} ms/pair); published 83.73 / 84.10")


if __name__ == "__main__":
    main()
