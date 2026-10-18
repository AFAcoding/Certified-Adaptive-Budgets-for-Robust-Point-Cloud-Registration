"""Compute (and cache) FPFH for every fetched KITTI scan.

Usage: python -I -u scripts/kitti_features.py [--workers 6]
"""

import argparse
import os
import time
from concurrent.futures import ProcessPoolExecutor

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(var, "1")

from acpr import DATA_ROOT  # noqa: E402
from acpr import kitti as K  # noqa: E402


def _one(pcd):
    _, f, dt = K.get_fpfh_kitti(pcd)
    return f.shape[0], dt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()
    scans = sorted("KITTI/" + p.relative_to(DATA_ROOT / "KITTI").as_posix()
                   for p in (DATA_ROOT / "KITTI" / "downsampled").rglob("*.npy"))
    t0 = time.time()
    with ProcessPoolExecutor(args.workers) as ex:
        res = list(ex.map(_one, scans, chunksize=8))
    pts = [n for n, _ in res]
    print(f"{len(scans)} scans in {time.time() - t0:.0f}s; points per scan: mean {sum(pts) / len(pts):.0f}, "
          f"min {min(pts)}, max {max(pts)}; mean FPFH time {sum(d for _, d in res) / len(res):.2f}s")


if __name__ == "__main__":
    main()
