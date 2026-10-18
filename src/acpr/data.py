"""3DMatch / 3DLoMatch pairs, fragments and benchmark ground truth."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

from acpr import DATA_ROOT

THREEDMATCH_ROOT = DATA_ROOT / "3DMatch"

# Number of fragments per test scene (needed to index gt.log / gt.info).
TEST_SCENE_NUM_FRAGMENTS = {
    "7-scenes-redkitchen": 60,
    "sun3d-home_at-home_at_scan1_2013_jan_1": 60,
    "sun3d-home_md-home_md_scan9_2012_sep_30": 60,
    "sun3d-hotel_uc-scan3": 55,
    "sun3d-hotel_umd-maryland_hotel1": 57,
    "sun3d-hotel_umd-maryland_hotel3": 37,
    "sun3d-mit_76_studyroom-76-1studyroom2": 66,
    "sun3d-mit_lab_hj-lab_hj_tea_nov_2_2012_scan1_erika": 38,
}

SCENE_ABBR = {
    "7-scenes-redkitchen": "Kitchen",
    "sun3d-home_at-home_at_scan1_2013_jan_1": "Home_1",
    "sun3d-home_md-home_md_scan9_2012_sep_30": "Home_2",
    "sun3d-hotel_uc-scan3": "Hotel_1",
    "sun3d-hotel_umd-maryland_hotel1": "Hotel_2",
    "sun3d-hotel_umd-maryland_hotel3": "Hotel_3",
    "sun3d-mit_76_studyroom-76-1studyroom2": "Study",
    "sun3d-mit_lab_hj-lab_hj_tea_nov_2_2012_scan1_erika": "MIT_Lab",
}


@dataclass(frozen=True)
class Pair:
    """A registration pair. `transform` maps src (frag1) points into the ref (frag0) frame."""

    subset: str
    index: int
    scene: str
    frag0: int  # reference fragment
    frag1: int  # source fragment
    pcd0: str
    pcd1: str
    overlap: float
    transform: np.ndarray  # (4, 4) float64

    @property
    def pair_id(self) -> str:
        return f"{self.subset}/{self.scene}/{self.frag0}_{self.frag1}"

    @property
    def adjacent(self) -> bool:
        return self.frag1 == self.frag0 + 1


def load_pairs(subset: str, root: Path = THREEDMATCH_ROOT) -> list[Pair]:
    with open(root / "metadata" / f"{subset}.json") as f:
        items = json.load(f)
    pairs = []
    for i, x in enumerate(items):
        T = np.eye(4)
        T[:3, :3] = np.asarray(x["rotation"], dtype=np.float64)
        T[:3, 3] = np.asarray(x["translation"], dtype=np.float64)
        pairs.append(
            Pair(
                subset=subset,
                index=i,
                scene=x["scene"],
                frag0=x["frag0"],
                frag1=x["frag1"],
                pcd0=x["pcd0"],
                pcd1=x["pcd1"],
                overlap=x["overlap"],
                transform=T,
            )
        )
    return pairs


def fragment_path(pcd: str, root: Path = THREEDMATCH_ROOT) -> Path:
    # metadata stores e.g. "test/7-scenes-redkitchen/cloud_bin_0.pth"
    return (root / "fragments" / pcd).with_suffix(".npy")


@lru_cache(maxsize=256)
def _load_fragment_cached(path: str) -> np.ndarray:
    arr = np.load(path, allow_pickle=False)
    arr.setflags(write=False)
    return arr


def load_fragment(pcd: str, root: Path = THREEDMATCH_ROOT) -> np.ndarray:
    """Load a fragment as a read-only float32 (N, 3) array."""
    return _load_fragment_cached(str(fragment_path(pcd, root)))


# ---------------------------------------------------------------------------
# Benchmark ground truth (gt.log / gt.info), used for the official RMSE recall
# ---------------------------------------------------------------------------


def _read_blocks(path: Path, rows: int) -> list[tuple[int, int, np.ndarray]]:
    with open(path) as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    blocks = []
    step = rows + 1
    for i in range(0, len(lines), step):
        head = lines[i].split()
        mat = np.array([ln.split() for ln in lines[i + 1 : i + step]], dtype=np.float64)
        blocks.append((int(head[0]), int(head[1]), mat))
    return blocks


@lru_cache(maxsize=32)
def load_benchmark_gt(benchmark: str, scene: str, root: Path = THREEDMATCH_ROOT):
    """Return {(frag0, frag1): (T_gt 4x4, info 6x6)} for one benchmark scene."""
    base = root / "metadata" / "benchmarks" / benchmark / scene
    logs = _read_blocks(base / "gt.log", 4)
    infos = _read_blocks(base / "gt.info", 6)
    out = {}
    for (a0, a1, T), (b0, b1, info) in zip(logs, infos):
        assert (a0, a1) == (b0, b1)
        out[(a0, a1)] = (T, info)
    return out
