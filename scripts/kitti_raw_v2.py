"""Protocol v2 (PROTOCOL.md), outdoor data: KITTI raw drives that are not part of odometry sequences 0-10.

Steps (each resumable; outputs under data/KITTI_raw/ and results/protocol_v2/):
  enumerate  probe the official raw archives, read every drive's OXTS (GPS/IMU) poses, form pairs by FCGF's rule
  split      permute the eligible drives (seed 20261019): blind test until >= 800 pairs, calibration until >= 1,600
  fetch      download the velodyne scans of the selected pairs (HTTP range requests), raw xyz as float32
  refine     ICP refinement of the GPS/IMU relative poses exactly as in FCGF (0.05 m voxels, 0.2 m, 200 iterations);
             pairs whose refinement moves the pose by more than 1 m or 5 degrees are dropped
  metadata   write data/KITTI_raw/metadata/{v2_kitti_blind, v2_kitti_cal}.json (KITTI metadata format)

Poses follow the KITTI raw devkit (Mercator projection of latitude/longitude, R = Rz(yaw) Ry(pitch) Rx(roll)); the
velodyne pose is T_w_imu * inv(T_velo_imu) with T_velo_imu from calib_imu_to_velo.txt.

Usage: python -I -u scripts/kitti_raw_v2.py {enumerate|split|fetch|fetch-odometry|refine|metadata} [--threads 8]
"""

import argparse
import json
import sys
import threading
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kitti_fetch as KF  # noqa: E402

from acpr import DATA_ROOT, RESULTS_ROOT  # noqa: E402

BASE = "https://s3.eu-central-1.amazonaws.com/avg-kitti/raw_data"
ROOT = DATA_ROOT / "KITTI_raw"
OUT = RESULTS_ROOT / "protocol_v2"
SEED = 20261019
ODOMETRY = {"2011_10_03_drive_0027", "2011_10_03_drive_0042", "2011_10_03_drive_0034", "2011_09_26_drive_0067",
            "2011_09_30_drive_0016", "2011_09_30_drive_0018", "2011_09_30_drive_0020", "2011_09_30_drive_0027",
            "2011_09_30_drive_0028", "2011_09_30_drive_0033", "2011_09_30_drive_0034"}  # sequences 00-10
CANDIDATES = ([f"2011_09_26_drive_{i:04d}" for i in range(1, 120)] + [f"2011_09_28_drive_{i:04d}" for i in range(1, 226)]
              + [f"2011_09_29_drive_{i:04d}" for i in range(1, 110)] + [f"2011_09_30_drive_{i:04d}" for i in range(1, 73)]
              + [f"2011_10_03_drive_{i:04d}" for i in range(1, 59)])


def zip_url(drive):
    return f"{BASE}/{drive}/{drive}_sync.zip"


def head(url):
    try:
        return KF.remote_size(url)
    except Exception:  # noqa: BLE001  (missing drive id)
        return None


def oxts_pose(fields, scale):
    """KITTI raw devkit: convertOxtsToPose for one OXTS record (lat, lon, alt, roll, pitch, yaw, ...)."""
    lat, lon, alt, roll, pitch, yaw = fields[:6]
    er = 6378137.0
    t = np.array([scale * lon * np.pi * er / 180.0, scale * er * np.log(np.tan((90.0 + lat) * np.pi / 360.0)), alt])
    cx, sx, cy, sy, cz, sz = np.cos(roll), np.sin(roll), np.cos(pitch), np.sin(pitch), np.cos(yaw), np.sin(yaw)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    T = np.eye(4)
    T[:3, :3], T[:3, 3] = Rz @ Ry @ Rx, t
    return T


def fcgf_pairs(pos):
    """FCGF's KITTI pairing rule (datasets KITTIPairDataset): partner = the frame before the first one more than
    10 m away (within 100 frames); next start = partner + 1."""
    n = len(pos)
    pairs, curr = [], 0
    while curr < n:
        d = np.linalg.norm(pos[curr:curr + 100] - pos[curr], axis=1)
        far = np.flatnonzero(d > 10)
        if len(far) == 0:
            curr += 1
            continue
        nxt = curr + far[0] - 1
        if nxt < n:
            pairs.append((curr, nxt))
        curr = nxt + 1
    return pairs


def read_calib(date):
    url = f"{BASE}/{date}_calib.zip"
    z = zipfile.ZipFile(KF.HttpRangeFile(url, KF.remote_size(url)))
    txt = z.read(f"{date}/calib_imu_to_velo.txt").decode()
    vals = {}
    for line in txt.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            try:
                vals[k.strip()] = np.array([float(x) for x in v.split()])
            except ValueError:
                pass
    T = np.eye(4)
    T[:3, :3], T[:3, 3] = vals["R"].reshape(3, 3), vals["T"]
    return T  # p_velo = T @ p_imu


def enumerate_drives(threads):
    OUT.mkdir(parents=True, exist_ok=True)
    cand = [d for d in CANDIDATES if d not in ODOMETRY]
    with ThreadPoolExecutor(threads) as ex:
        sizes = dict(zip(cand, ex.map(lambda d: head(zip_url(d)), cand)))
    drives = sorted(d for d, s in sizes.items() if s)
    print(f"{len(drives)} raw drives outside odometry 00-10", flush=True)
    calib = {date: read_calib(date) for date in sorted({d[:10] for d in drives})}
    res = {}

    def one(drive):
        z = zipfile.ZipFile(KF.HttpRangeFile(zip_url(drive), sizes[drive], block=1 << 20))
        date = drive[:10]
        names = z.namelist()
        velo = sorted(n for n in names if "/velodyne_points/data/" in n and n.endswith(".bin"))
        oxts = sorted(n for n in names if "/oxts/data/" in n and n.endswith(".txt"))
        frames = sorted({int(Path(n).stem) for n in velo} & {int(Path(n).stem) for n in oxts})
        if len(frames) < 50:
            return drive, {"frames": len(frames), "pairs": []}
        recs = {int(Path(n).stem): np.array([float(x) for x in z.read(n).split()]) for n in oxts}
        scale = np.cos(recs[frames[0]][0] * np.pi / 180.0)
        T_imu = [oxts_pose(recs[f], scale) for f in frames]
        T_velo = [T @ np.linalg.inv(calib[date]) for T in T_imu]
        pos = np.array([T[:3, 3] for T in T_imu])
        out = []
        for a, b in fcgf_pairs(pos):
            fa, fb = frames[a], frames[b]
            if fb - fa != b - a:  # gap in the frame numbering: skip
                continue
            T = np.linalg.inv(T_velo[b]) @ T_velo[a]  # maps the earlier scan (fa) into the later one (fb)
            out.append({"frame0": fb, "frame1": fa, "oxts_transform": T.tolist()})
        return drive, {"frames": len(frames), "pairs": out}

    with ThreadPoolExecutor(threads) as ex:
        futs = [ex.submit(one, d) for d in drives]
        for f in as_completed(futs):
            drive, r = f.result()
            res[drive] = r
            print(f"  {drive}: {r['frames']} frames, {len(r['pairs'])} pairs", flush=True)
    (OUT / "kitti_raw_drives.json").write_text(json.dumps(dict(sorted(res.items())), indent=1))


def split():
    """Amended split (PROTOCOL.md, deviation 1): every raw-drive pair is an FPFH blind-test pair; for FCGF, drives in
    permuted order go to calibration until it holds >= 1,100 pairs, the rest form the FCGF blind test."""
    drives = json.loads((OUT / "kitti_raw_drives.json").read_text())
    eligible = sorted(d for d, r in drives.items() if r["pairs"])
    order = [eligible[i] for i in np.random.default_rng(SEED).permutation(len(eligible))]
    count = lambda ds: sum(len(drives[d]["pairs"]) for d in ds)  # noqa: E731
    cal = []
    for d in order:
        if count(cal) < 1100:
            cal.append(d)
    blind = [d for d in order if d not in cal]
    out = {"seed": SEED, "all_drives": eligible, "fcgf_calibration_drives": cal, "fcgf_blind_drives": blind,
           "pairs": {"all": count(eligible), "fcgf_calibration": count(cal), "fcgf_blind": count(blind)}}
    (OUT / "kitti_raw_split.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out["pairs"]), len(cal), "FCGF calibration drives,", len(blind), "FCGF blind drives")


def selected_pairs():
    """(role, drive, pair) for every raw-drive pair; role is the drive's FCGF role (all pairs are FPFH blind)."""
    drives = json.loads((OUT / "kitti_raw_drives.json").read_text())
    sp = json.loads((OUT / "kitti_raw_split.json").read_text())
    for role, key in (("fcgf_blind", "fcgf_blind_drives"), ("fcgf_cal", "fcgf_calibration_drives")):
        for d in sp[key]:
            for p in drives[d]["pairs"]:
                yield role, d, p


def scan_file(drive, frame):
    return ROOT / "scans" / drive / f"{frame:010d}.npy"


_local = threading.local()


def fetch(threads):
    need = sorted({(d, f) for _, d, p in selected_pairs() for f in (p["frame0"], p["frame1"])
                   if not scan_file(d, f).exists()})
    print(f"{len(need)} scans to fetch", flush=True)
    sizes = {}

    def one(drive, frame):
        if drive not in sizes:
            sizes[drive] = KF.remote_size(zip_url(drive))
        zs = getattr(_local, "zips", {})
        if drive not in zs:
            zs[drive] = zipfile.ZipFile(KF.HttpRangeFile(zip_url(drive), sizes[drive]))
            _local.zips = zs
        raw = zs[drive].read(f"{drive[:10]}/{drive}_sync/velodyne_points/data/{frame:010d}.bin")
        xyz = np.frombuffer(raw, np.float32).reshape(-1, 4)[:, :3]
        out = scan_file(drive, frame)
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_name(out.stem + ".tmp.npy")
        np.save(tmp, xyz)
        tmp.replace(out)

    with ThreadPoolExecutor(threads) as ex:
        futs = [ex.submit(one, d, f) for d, f in need]
        for i, f in enumerate(as_completed(futs), 1):
            f.result()
            if i % 200 == 0 or i == len(futs):
                print(f"  {i}/{len(futs)}", flush=True)


def fetch_odometry(threads):
    """Raw velodyne scans of the odometry frames used with FCGF: the 300 fitting pairs and the 555 test pairs
    (FCGF quantises the raw scan; the stored 0.3 m scans use another grid)."""
    from acpr import kitti as K
    from acpr.v2data import odometry_raw_path
    pairs = [K.load_kitti_pairs("train")[i] for i in K.train_fit()] + K.load_kitti_pairs("test")
    need = sorted({(int(p.scene), f) for p in pairs for f in (p.frag0, p.frag1)
                   if not odometry_raw_path(int(p.scene), f).exists()})
    print(f"{len(need)} odometry scans to fetch", flush=True)
    size = KF.remote_size(KF.URL)

    def one(seq, frame):
        if not hasattr(_local, "odo"):
            _local.odo = zipfile.ZipFile(KF.HttpRangeFile(KF.URL, size))
        raw = _local.odo.read(f"dataset/sequences/{seq:02d}/velodyne/{frame:06d}.bin")
        out = odometry_raw_path(seq, frame)
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_name(out.stem + ".tmp.npy")
        np.save(tmp, np.frombuffer(raw, np.float32).reshape(-1, 4)[:, :3])
        tmp.replace(out)

    with ThreadPoolExecutor(threads) as ex:
        futs = [ex.submit(one, s, f) for s, f in need]
        for i, f in enumerate(as_completed(futs), 1):
            f.result()
            if i % 200 == 0 or i == len(futs):
                print(f"  {i}/{len(futs)}", flush=True)


def icp_refine(args):
    """FCGF's refinement: point-to-point ICP between the 0.05 m-quantised scans, starting from the OXTS pose."""
    import open3d as o3d
    drive, p = args
    src = np.load(scan_file(drive, p["frame1"]))
    ref = np.load(scan_file(drive, p["frame0"]))

    def q(x):
        _, idx = np.unique(np.floor(x.astype(np.float64) / 0.05).astype(np.int64), axis=0, return_index=True)
        return o3d.geometry.PointCloud(o3d.utility.Vector3dVector(x[np.sort(idx)].astype(np.float64)))
    T0 = np.asarray(p["oxts_transform"])
    reg = o3d.pipelines.registration.registration_icp(
        q(src), q(ref), 0.2, T0, o3d.pipelines.registration.TransformationEstimationPointToPoint(),
        o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=200))
    T = np.asarray(reg.transformation)
    dR = T0[:3, :3].T @ T[:3, :3]
    ddeg = float(np.degrees(np.arccos(np.clip((np.trace(dR) - 1) / 2, -1, 1))))
    dm = float(np.linalg.norm(T0[:3, 3] - T[:3, 3]))
    return drive, p["frame0"], {"transform": T.tolist(), "icp_fitness": float(reg.fitness), "dpose_deg": ddeg, "dpose_m": dm}


def refine(threads):
    from concurrent.futures import ProcessPoolExecutor
    path = OUT / "kitti_raw_icp.json"
    done = json.loads(path.read_text()) if path.exists() else {}
    todo = [(d, p) for _, d, p in selected_pairs() if f"{d}/{p['frame0']}" not in done]
    print(f"{len(todo)} pairs to refine", flush=True)
    with ProcessPoolExecutor(threads) as ex:
        for i, (d, f0, r) in enumerate(ex.map(icp_refine, todo, chunksize=4), 1):
            done[f"{d}/{f0}"] = r
            if i % 100 == 0 or i == len(todo):
                path.write_text(json.dumps(done))
                print(f"  {i}/{len(todo)}", flush=True)
    path.write_text(json.dumps(done))


def metadata():
    icp = json.loads((OUT / "kitti_raw_icp.json").read_text())
    (ROOT / "metadata").mkdir(parents=True, exist_ok=True)
    report = {}
    for role in ("all", "fcgf_blind", "fcgf_cal"):
        items, dropped = [], 0
        for r, d, p in selected_pairs():
            if role != "all" and r != role:
                continue
            g = icp[f"{d}/{p['frame0']}"]
            if g["dpose_m"] > 1.0 or g["dpose_deg"] > 5.0:
                dropped += 1
                continue
            items.append({"seq": d, "frame0": p["frame0"], "frame1": p["frame1"], "transform": g["transform"]})
        (ROOT / "metadata" / f"v2_kitti_{role}.json").write_text(json.dumps(items))
        report[role] = {"pairs": len(items), "dropped_icp": dropped}
    (OUT / "kitti_raw_metadata.json").write_text(json.dumps(report, indent=1))
    print(report)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["enumerate", "split", "fetch", "fetch-odometry", "refine", "metadata"])
    ap.add_argument("--threads", type=int, default=8)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    {"enumerate": lambda: enumerate_drives(a.threads), "split": split, "fetch": lambda: fetch(a.threads),
     "fetch-odometry": lambda: fetch_odometry(a.threads), "refine": lambda: refine(a.threads),
     "metadata": metadata}[a.step]()


if __name__ == "__main__":
    main()
