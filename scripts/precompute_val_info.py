"""Compute ground-truth information matrices for validation pairs.

The test benchmarks ship gt.info files; the validation pairs do not. To label
validation pairs with exactly the same RMSE criterion as the test protocol, we
build the 6x6 information matrix from ground-truth correspondences (same
construction as 3DMatch's gt.info) once and store it.

Usage: python -I scripts/precompute_val_info.py [subset=val]
"""

import json
import sys

import numpy as np

from acpr.data import THREEDMATCH_ROOT, load_fragment, load_pairs
from acpr.metrics import info_matrix


def main():
    subset = sys.argv[1] if len(sys.argv) > 1 else "val"
    pairs = load_pairs(subset)
    out = {}
    for p in pairs:
        ref, src = load_fragment(p.pcd0), load_fragment(p.pcd1)
        out[p.pair_id] = info_matrix(ref, src, p.transform).tolist()
    path = THREEDMATCH_ROOT / "metadata" / f"{subset}_info.json"
    with open(path, "w") as f:
        json.dump(out, f)
    n0 = np.array([v[0][0] for v in out.values()])
    print(f"{subset}: {len(out)} info matrices -> {path}; correspondences min/median {n0.min():.0f}/{np.median(n0):.0f}")


if __name__ == "__main__":
    main()
