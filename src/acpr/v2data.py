"""Protocol v2 datasets (PROTOCOL.md): pairs and descriptors for the new fitting, calibration and blind-test splits.

FCGF features are computed here with the official weights (acpr.fcgf_net, verified identical to the released ones):
indoors on our 3DMatch fragments at 0.05 m (they give exactly the released features' voxels), outdoors on raw velodyne
scans at 0.3 m. FPFH on the KITTI raw drives uses the odometry preprocessing (Open3D voxel grid at 0.3 m, then
FPFH as acpr.kitti.get_fpfh_kitti). Features are cached under data/cache/.
"""

from __future__ import annotations

import json
import time
from functools import lru_cache
from pathlib import Path

import numpy as np

from acpr import DATA_ROOT, PROJECT_ROOT
from acpr import kitti as K
from acpr import light
from acpr.data import Pair, load_fragment, load_pairs

RAW_ROOT = DATA_ROOT / "KITTI_raw"
W = PROJECT_ROOT / "third_party" / "fcgf_weights"
FCGF_INDOOR, FCGF_KITTI = "2019-08-16_19-21-47.pth", "KITTI-v0.3-ResUNetBN2C-conv1-5-nout32.pth"


@lru_cache(maxsize=2)
def _net(name):
    from acpr.fcgf_net import FCGF
    return FCGF(str(W / name))


def _cached(path: Path, compute):
    if path.exists():
        z = np.load(path, allow_pickle=False)
        return z["points"], z["feats"]
    p, f = compute()
    path.parent.mkdir(parents=True, exist_ok=True)
    import os
    tmp = path.with_name(f"{path.stem}.{os.getpid()}.tmp.npz")  # per process: parallel workers may share a scan
    np.savez(tmp, points=p.astype(np.float32), feats=f.astype(np.float32))
    try:
        tmp.replace(path)
    except PermissionError:  # another worker is writing the same (identical) features
        tmp.unlink(missing_ok=True)
    return p, f


def fcgf_from_points(points: np.ndarray, voxel: float, net: str):
    from acpr.fcgf_net import voxelize
    coords, reps = voxelize(points, voxel)
    return reps, _net(net).features(coords)


# ---------------------------------------------------------------- scans
def odometry_raw_path(seq: int, frame: int) -> Path:
    return DATA_ROOT / "KITTI" / "raw" / f"{seq:02d}" / f"{frame:06d}.npy"


def raw_drive_path(drive: str, frame: int) -> Path:
    return RAW_ROOT / "scans" / drive / f"{frame:010d}.npy"


def _raw_scan(pcd: str) -> np.ndarray:
    """pcd: 'odo/SS/FFFFFF' (KITTI odometry) or 'raw/<drive>/<frame>' (KITTI raw drive)."""
    kind, a, b = pcd.split("/")
    path = odometry_raw_path(int(a), int(b)) if kind == "odo" else raw_drive_path(a, int(b))
    return np.load(path, allow_pickle=False)


# ---------------------------------------------------------------- features
def fcgf_indoor(pcd: str):
    path = DATA_ROOT / "cache" / "fcgf_own_50mm" / Path(pcd).with_suffix(".npz")
    return _cached(path, lambda: fcgf_from_points(np.asarray(load_fragment(pcd), np.float64), 0.05, FCGF_INDOOR))


def fcgf_kitti(pcd: str):
    path = DATA_ROOT / "cache" / "fcgf_own_kitti_300mm" / f"{pcd}.npz"
    return _cached(path, lambda: fcgf_from_points(_raw_scan(pcd), 0.3, FCGF_KITTI))


def fpfh_kitti_raw(pcd: str):
    """FPFH exactly as for the odometry scans: Open3D voxel grid at 0.3 m, then acpr.kitti's FPFH settings."""
    import open3d as o3d

    def compute():
        pts = _raw_scan(pcd).astype(np.float64)
        pc = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(pts)).voxel_down_sample(K.VOXEL)
        return light.preprocess(np.asarray(pc.points, dtype=np.float32), light.LightConfig(voxel_size=K.VOXEL))
    return _cached(DATA_ROOT / "cache" / "fpfh_kitti_raw_300mm" / f"{pcd}.npz", compute)


# ---------------------------------------------------------------- pairs
def kitti_odometry_pairs(split: str, indices=None) -> list[Pair]:
    pairs = K.load_kitti_pairs(split)
    if indices is not None:
        pairs = [pairs[i] for i in indices]
    return [Pair(subset=p.subset, index=p.index, scene=p.scene, frag0=p.frag0, frag1=p.frag1,
                 pcd0=f"odo/{p.scene}/{p.frag0:06d}", pcd1=f"odo/{p.scene}/{p.frag1:06d}", overlap=float("nan"),
                 transform=p.transform) for p in pairs]


def kitti_raw_pairs(role: str) -> list[Pair]:
    items = json.loads((RAW_ROOT / "metadata" / f"v2_kitti_{role}.json").read_text())
    return [Pair(subset=f"kitti_raw_{role}", index=i, scene=x["seq"], frag0=x["frame0"], frag1=x["frame1"],
                 pcd0=f"raw/{x['seq']}/{x['frame0']}", pcd1=f"raw/{x['seq']}/{x['frame1']}", overlap=float("nan"),
                 transform=np.asarray(x["transform"], dtype=np.float64)) for i, x in enumerate(items)]


def _success_indoor(Tg, T):
    from acpr.metrics import rre_rte
    rre, rte = rre_rte(Tg, T)
    return bool(rre <= 15 and rte <= 0.3), rre, rte


def config(name: str) -> dict:
    """Log configurations of protocol v2. Thresholds: indoors those of the FPFH experiments, outdoors the KITTI ones
    (results/kitti/thresholds.json, chosen on odometry validation); both are geometric, not descriptor-dependent."""
    from acpr import RESULTS_ROOT
    indoor = {"inlier": 0.1, "compat_thr": 0.10, "sc2": {}, "turbo": {}, "success": _success_indoor}
    thr = json.loads((RESULTS_ROOT / "kitti" / "thresholds.json").read_text())
    outdoor = {"inlier": 0.6, "compat_thr": thr["sc2_d_thre"],
               "sc2": {"d_thre": thr["sc2_d_thre"], "inlier_thr": 0.6, "nms_radius": 0.6},
               "turbo": {"tau": thr["turbo_tau"], "inlier_thr": 0.6}, "success": lambda Tg, T: K.success(Tg, T)}
    table = {
        # FCGF indoors: fitting on training-scene pairs, calibration on the validation scenes, development tests
        "fcgfown_v2_fit": (lambda: load_pairs("v2_fit"), fcgf_indoor, indoor),
        "fcgfown_val": (lambda: load_pairs("val"), fcgf_indoor, indoor),
        "fcgfown_3DMatch": (lambda: load_pairs("3DMatch"), fcgf_indoor, indoor),
        "fcgfown_3DLoMatch": (lambda: load_pairs("3DLoMatch"), fcgf_indoor, indoor),
        # outdoors: fitting on odometry training pairs, calibration and blind test on KITTI raw drives,
        # development test on odometry sequences 8-10
        "fcgfown_kitti_fit": (lambda: kitti_odometry_pairs("train", K.train_fit()), fcgf_kitti, outdoor),
        "fcgfown_kitti_test": (lambda: kitti_odometry_pairs("test"), fcgf_kitti, outdoor),
        # FCGF: calibration and blind test on disjoint raw drives (PROTOCOL.md, deviation 1)
        "fcgfown_kitti_raw_cal": (lambda: kitti_raw_pairs("fcgf_cal"), fcgf_kitti, outdoor),
        "fcgfown_kitti_raw_blind": (lambda: kitti_raw_pairs("fcgf_blind"), fcgf_kitti, outdoor),
        # FPFH: every raw-drive pair is a blind-test pair (calibration on the odometry validation/held-out pairs)
        "kitti_raw_blind": (lambda: kitti_raw_pairs("all"), fpfh_kitti_raw, outdoor),
    }
    pairs, feats, cfg = table[name]
    return {"pairs": pairs, "features": feats, **cfg}
