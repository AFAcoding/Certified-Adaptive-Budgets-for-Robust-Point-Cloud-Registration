"""Verify the PyTorch FCGF on KITTI: fetch the raw scans of released FCGF KITTI test pairs, quantise them at 0.3 m as
the official code does, and compare the features of both KITTI checkpoints with the released ones (per voxel).

Usage: python -I scripts/verify_fcgf_kitti.py [n_pairs]
"""

import sys
import zipfile

import numpy as np

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import kitti_fetch as KF  # noqa: E402

from acpr import DATA_ROOT, PROJECT_ROOT  # noqa: E402
from acpr import kitti as K  # noqa: E402
from acpr.fcgf_net import FCGF, voxelize  # noqa: E402

W = PROJECT_ROOT / "third_party" / "fcgf_weights"


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    geo = K.load_kitti_pairs("test")
    G = np.array([p.transform for p in geo])
    zf = zipfile.ZipFile(KF.HttpRangeFile(KF.URL, KF.remote_size(KF.URL)))
    nets = {name: FCGF(str(W / name)) for name in ("KITTI-v0.3-ResUNetBN2C-conv1-5-nout32.pth", "2019-07-31_19-37-00.pth")}
    done = 0
    for i in range(555):
        z = np.load(DATA_ROOT / "FCGF" / "KITTI" / f"pair_{i}.npz", allow_pickle=False)
        d = np.linalg.norm(G[:, :3, 3] - z["gt_trans"][None, :3, 3], axis=1)
        j = int(d.argmin())
        if d[j] > 1e-3:
            continue
        p = geo[j]
        seq = int(p.scene)
        for tag, frame in (("0", p.frag1), ("1", p.frag0)):  # released xyz0 is the later frame
            raw = np.frombuffer(zf.read(f"dataset/sequences/{seq:02d}/velodyne/{frame:06d}.bin"), np.float32)
            pts = raw.reshape(-1, 4)[:, :3]
            coords, _ = voxelize(pts, 0.3)
            kq = np.floor(z["xyz" + tag].astype(np.float64) / 0.3).astype(np.int64)
            idx = {tuple(c): r for r, c in enumerate(coords)}
            rows = np.array([idx.get(tuple(c), -1) for c in kq])
            ok = rows >= 0
            print(f"pair {i} ({seq:02d} {frame}) xyz{tag}: {len(coords)} voxels vs {len(kq)} keypoints, "
                  f"{ok.mean():.4f} found; released feature norm {np.linalg.norm(z['features' + tag], axis=1).mean():.3f}")
            for name, net in nets.items():
                f = net.features(coords)[rows[ok]]
                r = z["features" + tag][ok]
                cos = np.sum(f * r, 1) / np.linalg.norm(f, axis=1) / np.linalg.norm(r, axis=1)
                print(f"   {name}: cosine mean {cos.mean():.6f}, min {cos.min():.5f}; "
                      f"max abs diff {np.abs(f - r).max():.2e}")
        done += 1
        if done >= n:
            break


if __name__ == "__main__":
    main()
