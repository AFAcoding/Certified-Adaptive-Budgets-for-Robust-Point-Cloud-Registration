"""Extract the 3DMatch fragments from Predator's archive and convert them to .npy.

Layout produced (inside the project folder):
    data/3DMatch/fragments/{train,test}/<scene>/cloud_bin_<i>.npy   float32 (N, 3)
    data/3DMatch/metadata/{train,val,3DMatch,3DLoMatch}.json        pair lists
    data/3DMatch/metadata/benchmarks/{3DMatch,3DLoMatch}/<scene>/gt.log, gt.info

The fragments are torch-pickled numpy arrays. They are loaded with
torch.load(weights_only=True) plus an allow-list of numpy reconstruction
helpers, so no arbitrary pickle code from the download can run.
The GeoTransformer metadata pickles are read with a restricted unpickler that
only allows numpy array reconstruction.

Usage:
    python -I scripts/prepare_3dmatch.py <data.zip> <GeoTransformer repo> <output dir>
"""

import io
import json
import pickle
import shutil
import sys
import zipfile
from pathlib import Path

import numpy as np
import torch

ALLOWED_PICKLE_GLOBALS = {
    ("numpy.core.multiarray", "_reconstruct"),
    ("numpy._core.multiarray", "_reconstruct"),
    ("numpy", "ndarray"),
    ("numpy", "dtype"),
    ("numpy.core.multiarray", "scalar"),
    ("numpy._core.multiarray", "scalar"),
}


class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if (module, name) in ALLOWED_PICKLE_GLOBALS or module.startswith("numpy.dtypes"):
            return super().find_class(module, name)
        raise pickle.UnpicklingError(f"blocked global {module}.{name}")


def safe_torch_load_numpy(raw: bytes) -> np.ndarray:
    import numpy.dtypes as npd
    from numpy._core import multiarray as ma

    # The archive was pickled with NumPy 1.x, which names these helpers under
    # "numpy.core.multiarray"; allow-list them under both module paths.
    allowed = [
        ma._reconstruct,
        (ma._reconstruct, "numpy.core.multiarray._reconstruct"),
        ma.scalar,
        (ma.scalar, "numpy.core.multiarray.scalar"),
        np.ndarray,
        np.dtype,
    ]
    allowed += [getattr(npd, n) for n in dir(npd) if n.endswith("DType")]
    with torch.serialization.safe_globals(allowed):
        obj = torch.load(io.BytesIO(raw), weights_only=True)
    if isinstance(obj, torch.Tensor):
        obj = obj.numpy()
    arr = np.asarray(obj, dtype=np.float32)
    if arr.ndim != 2 or arr.shape[1] != 3:
        raise ValueError(f"unexpected fragment shape {arr.shape}")
    return arr


def extract_fragments(zip_path: Path, out_root: Path) -> int:
    count = 0
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            name = info.filename
            if not name.startswith("data/indoor/") or not name.endswith(".pth"):
                continue
            rel = Path(name[len("data/indoor/"):])  # {train,test}/<scene>/cloud_bin_i.pth
            if rel.is_absolute() or ".." in rel.parts:
                raise ValueError(f"unsafe path in archive: {name}")
            dest = (out_root / "fragments" / rel).with_suffix(".npy")
            if dest.exists():
                count += 1
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            arr = safe_torch_load_numpy(zf.read(info))
            np.save(dest, arr, allow_pickle=False)
            count += 1
            if count % 500 == 0:
                print(f"  converted {count} fragments", flush=True)
    return count


def convert_metadata(repo: Path, out_root: Path) -> None:
    src_meta = repo / "data" / "3DMatch" / "metadata"
    dst_meta = out_root / "metadata"
    dst_meta.mkdir(parents=True, exist_ok=True)
    for subset in ["train", "val", "3DMatch", "3DLoMatch"]:
        with open(src_meta / f"{subset}.pkl", "rb") as f:
            items = RestrictedUnpickler(f).load()
        pairs = []
        for x in items:
            pairs.append(
                {
                    "scene": x["scene_name"],
                    "frag0": int(x["frag_id0"]),
                    "frag1": int(x["frag_id1"]),
                    "pcd0": x["pcd0"],
                    "pcd1": x["pcd1"],
                    "overlap": float(x["overlap"]),
                    "rotation": np.asarray(x["rotation"], dtype=np.float64).tolist(),
                    "translation": np.asarray(x["translation"], dtype=np.float64).reshape(3).tolist(),
                }
            )
        with open(dst_meta / f"{subset}.json", "w") as f:
            json.dump(pairs, f)
        print(f"  {subset}: {len(pairs)} pairs")
    # benchmark ground-truth logs (plain text)
    shutil.copytree(src_meta / "benchmarks", dst_meta / "benchmarks", dirs_exist_ok=True)


def main():
    zip_path, repo, out_root = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    out_root.mkdir(parents=True, exist_ok=True)
    print("converting metadata ...")
    convert_metadata(repo, out_root)
    print("extracting fragments ...")
    n = extract_fragments(zip_path, out_root)
    print(f"done: {n} fragments")


if __name__ == "__main__":
    main()
