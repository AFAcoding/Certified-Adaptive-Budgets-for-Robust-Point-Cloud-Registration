"""Fetch only the KITTI odometry scans used by the registration benchmark.

The official velodyne archive is an 85 GB zip on S3 that supports HTTP range requests.
We read its central directory remotely and download just the members (scans) referenced by
the benchmark pairs: all test (sequences 8-10) and validation (6-7) pairs, and a fixed
500-pair sample of the training pairs (0-5). Each scan is voxel-downsampled at 0.3 m
(as in GeoTransformer's preprocessing) and saved as float32 xyz.

Usage: python -I -u scripts/kitti_fetch.py [--list] [--threads 8]
"""

import argparse
import sys
import threading
import time
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np

from acpr import DATA_ROOT
from acpr import kitti as K

URL = "https://s3.eu-central-1.amazonaws.com/avg-kitti/data_odometry_velodyne.zip"


class HttpRangeFile:
    """Minimal read-only, seekable file over HTTP range requests (enough for zipfile)."""

    def __init__(self, url, size, block=1 << 16):
        self.url, self.size, self.pos, self.block = url, size, 0, block
        self.buf_start, self.buf = None, b""
        self.bytes_fetched = 0

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        self.pos = off if whence == 0 else (self.pos + off if whence == 1 else self.size + off)
        return self.pos

    def _fetch(self, start, end):
        req = urllib.request.Request(self.url, headers={"Range": f"bytes={start}-{end}"})
        for attempt in range(6):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    data = r.read()
                if len(data) == end - start + 1:
                    self.bytes_fetched += len(data)
                    return data
            except Exception:  # transient network error: back off and retry
                pass
            time.sleep(2 * (attempt + 1))
        raise IOError(f"range {start}-{end} failed")

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.size - self.pos
        if n == 0 or self.pos >= self.size:
            return b""
        n = min(n, self.size - self.pos)
        if self.buf_start is not None and self.buf_start <= self.pos and self.pos + n <= self.buf_start + len(self.buf):
            out = self.buf[self.pos - self.buf_start: self.pos - self.buf_start + n]
        else:
            end = min(self.pos + max(n, self.block), self.size) - 1
            self.buf_start, self.buf = self.pos, self._fetch(self.pos, end)
            out = self.buf[:n]
        self.pos += len(out)
        return out


def remote_size(url):
    with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=60) as r:
        return int(r.headers["Content-Length"])


ALL_TRAIN = False  # --all-train: every training pair (fitting subset + calibration pool)


def needed_frames():
    frames = set()
    for split in ("test", "val"):
        for p in K.load_kitti_pairs(split):
            frames |= {(int(p.scene), p.frag0), (int(p.scene), p.frag1)}
    train = K.load_kitti_pairs("train")
    for i in (range(len(train)) if ALL_TRAIN else K.train_sample()):
        p = train[i]
        frames |= {(int(p.scene), p.frag0), (int(p.scene), p.frag1)}
    return sorted(frames)


_local = threading.local()


def _zip(size):
    if not hasattr(_local, "zf"):
        _local.f = HttpRangeFile(URL, size)
        _local.zf = zipfile.ZipFile(_local.f)
    return _local.zf


def fetch_one(seq, frame, size):
    import open3d as o3d

    out = DATA_ROOT / K.scan_path(seq, frame)
    if out.exists():
        return 0
    raw = _zip(size).read(f"dataset/sequences/{seq:02d}/velodyne/{frame:06d}.bin")
    pts = np.frombuffer(raw, dtype=np.float32).reshape(-1, 4)[:, :3]
    pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(pts.astype(np.float64)))
    pcd = pcd.voxel_down_sample(K.VOXEL)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp.npy")
    np.save(tmp, np.asarray(pcd.points, dtype=np.float32))
    tmp.replace(out)
    return len(raw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--all-train", action="store_true")
    args = ap.parse_args()
    global ALL_TRAIN
    ALL_TRAIN = args.all_train
    sys.stdout.reconfigure(encoding="utf-8")
    K.convert_metadata()
    size = remote_size(URL)
    if args.list:
        f = HttpRangeFile(URL, size)
        zf = zipfile.ZipFile(f)
        names = zf.namelist()
        print(f"{len(names)} members, central directory fetched with {f.bytes_fetched / 1e6:.1f} MB; first: {names[:3]}")
        return
    frames = needed_frames()
    todo = [fr for fr in frames if not (DATA_ROOT / K.scan_path(*fr)).exists()]
    print(f"{len(frames)} scans needed, {len(todo)} to fetch", flush=True)
    t0, got = time.time(), 0
    with ThreadPoolExecutor(args.threads) as ex:
        futs = [ex.submit(fetch_one, s, f, size) for s, f in todo]
        for i, fu in enumerate(as_completed(futs), 1):
            got += fu.result()
            if i % 100 == 0 or i == len(futs):
                el = time.time() - t0
                print(f"  {i}/{len(futs)}  {got / 1e6:.0f} MB  {got / 1e6 / max(el, 1e-6):.1f} MB/s  "
                      f"ETA {el / i * (len(futs) - i):.0f}s", flush=True)


if __name__ == "__main__":
    main()
