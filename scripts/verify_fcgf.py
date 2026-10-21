"""Verify the PyTorch re-implementation of FCGF (acpr.fcgf_net) against the features released with SC2-PCR.

The released 3DMatch files contain each fragment's input points ('points'), the keypoints ('xyz', one input point
per occupied voxel) and their features. Running the official weights on the same points must give the same feature
for every keypoint's voxel. Reports, per checkpoint and kernel-ordering convention, the cosine similarity between
released and recomputed features.

Usage: python -I scripts/verify_fcgf.py [n_fragments]
"""

import glob
import sys

import numpy as np

from acpr import DATA_ROOT, PROJECT_ROOT
from acpr.fcgf_net import FCGF, voxelize

W = PROJECT_ROOT / "third_party" / "fcgf_weights"


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    files = sorted(glob.glob(str(DATA_ROOT / "FCGF" / "3DMatch" / "*" / "cloud_bin_*_fcgf.npz")))[::97][:n]
    for ckpt, voxel in (("2019-08-16_19-21-47.pth", 0.05), ("2019-08-19_06-17-41.pth", 0.025)):
        for fast in (True, False):
            net = FCGF(str(W / ckpt), first_axis_fastest=fast)
            cos = []
            for f in files:
                z = np.load(f, allow_pickle=False)
                coords, _ = voxelize(z["points"], voxel)
                feat = net.features(coords)
                kq = np.floor(z["xyz"].astype(np.float64) / voxel).astype(np.int64)
                idx = {tuple(c): i for i, c in enumerate(coords)}
                rows = np.array([idx.get(tuple(c), -1) for c in kq])
                ok = rows >= 0
                a, b = feat[rows[ok]], z["feature"][ok]
                cos.append(np.sum(a * b, 1) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)))
                print(f"  {ckpt} voxel {voxel} first-axis-fastest={fast}: {f.split('FCGF')[-1]}: "
                      f"{ok.mean():.3f} of keypoints found, {len(coords)} voxels vs {len(z['xyz'])} keypoints", flush=True)
            c = np.concatenate(cos)
            print(f"{ckpt} voxel {voxel} first-axis-fastest={fast}: cosine mean {c.mean():.5f}, min {c.min():.5f}, "
                  f">0.999: {np.mean(c > 0.999):.4f}", flush=True)


if __name__ == "__main__":
    main()
