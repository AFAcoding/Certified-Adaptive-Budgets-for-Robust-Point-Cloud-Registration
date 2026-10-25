"""Assemble gpu_bundle_part3.zip for addendum C, amendment 1 (MAC on the eight further timed test sets): the MAC
entries of gpu_bundle/ (held-out scenes, 3DMatch, 3DLoMatch, KITTI odometry) and of gpu_bundle_mac3/ (KITTI raw
drives, FCGF 3DMatch, FCGF 3DLoMatch, exported after their MAC configurations were certified). The MAC entries of
gpu_bundle_mac3/ are also merged into gpu_bundle/, whose config.json holds the CPU references of every published GPU
run (scripts/paper_assets.py). Also writes gpu/CAB_GPU_timing_part3.ipynb."""
import json
import shutil
import zipfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MAIN, NEW, OUT = ROOT / "gpu_bundle", ROOT / "gpu_bundle_mac3", ROOT / "gpu_bundle_part3"
SETS = ("bh", "bl", "kr", "m", "lo", "ki", "fm", "flo")


def main():
    cfg, cfg3 = (json.loads((d / "config.json").read_text()) for d in (MAIN, NEW))
    models, models3 = dict(np.load(MAIN / "models.npz")), dict(np.load(NEW / "models.npz"))
    for code in cfg3["sets"]:  # same pairs and correspondences as the main bundle (same sample, single-threaded)
        a, b = np.load(MAIN / f"data_{code}.npz"), np.load(NEW / f"data_{code}.npz")
        for k in a.files:
            assert np.array_equal(a[k], b[k]), (code, k)
        cfg["sets"][code]["estimators"]["mac"] = cfg3["sets"][code]["estimators"]["mac"]
        models.update({k: v for k, v in models3.items() if k.startswith(f"{code}/mac/")})
    (MAIN / "config.json").write_text(json.dumps(cfg, indent=1))
    np.savez_compressed(MAIN / "models.npz", **models)
    missing = [c for c in SETS if "mac" not in cfg["sets"][c]["estimators"]]
    assert not missing, missing

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    sub = {"per_set": cfg["per_set"], "sets": {}}
    for code in SETS:
        e = dict(cfg["sets"][code])
        e["estimators"] = {"mac": cfg["sets"][code]["estimators"]["mac"]}
        sub["sets"][code] = e
        shutil.copy(MAIN / f"data_{code}.npz", OUT)
    (OUT / "config.json").write_text(json.dumps(sub, indent=1))
    np.savez_compressed(OUT / "models.npz", **{k: v for k, v in models.items()
                                               if k.split("/")[0] in SETS and k.split("/")[1] == "mac"})
    for f in ("cab_gpu.py", "run_gpu_timing.py"):
        shutil.copy(ROOT / "gpu" / f, OUT)
    zp = ROOT / "gpu_bundle_part3.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(OUT.iterdir()):
            z.write(f, f"gpu_bundle_part3/{f.name}")
    print(f"{zp.name}: {zp.stat().st_size / 1e6:.0f} MB, MAC on {', '.join(SETS)}")

    # notebook: the part-2 notebook with the part-3 bundle and MAC
    nb = json.loads((ROOT / "gpu" / "CAB_GPU_timing_part2.ipynb").read_text(encoding="utf-8"))
    for c in nb["cells"]:
        s = "".join(c["source"])
        s = s.replace("gpu_bundle_part2", "gpu_bundle_part3")
        if c["cell_type"] == "markdown" and s.startswith("# CAB"):
            s = ("# CAB: live timing on a GPU, part 3 (PROTOCOL.md, protocol v3, addendum C, amendment 1)\n\n"
                 "Times MAC (full budget and the two certified CAB configurations; graphs on the GPU, maximal-clique "
                 "search on the CPU, as in the authors' code) on the eight further test sets: held-out scenes (both "
                 "overlap parts), KITTI raw drives, 3DMatch, 3DLoMatch, KITTI odometry, FCGF 3DMatch and FCGF "
                 "3DLoMatch, on the same 300 test pairs per set as the CPU live timing. Nothing is trained here.\n\n"
                 "**Steps**\n1. Upload `gpu_bundle_part3.zip` to the top level of your Google Drive (\"My Drive\").\n"
                 "2. Choose a GPU runtime (Colab: *Runtime > Change runtime type > T4 GPU*; VS Code with the Colab "
                 "extension: a Colab **GPU** server as the kernel).\n"
                 "3. *Run all*; give the GitHub token when the second cell asks. About 5-6 hours on a T4; the results "
                 "of every two sets are published as they finish, so a disconnection loses at most one batch "
                 "(re-running skips nothing, it simply times the batch again).\n")
        if c["cell_type"] == "markdown" and s.startswith("## "):
            s = "## MAC on the eight further test sets, two sets per batch\n"
        if c["cell_type"] == "code" and "run_gpu_timing.py" in s:
            s = ("for batch in ['bh,bl', 'kr,m', 'lo,ki', 'fm,flo']:\n"
                 "    out = f\"/content/cab_gpu_results_mac_part3_{batch.replace(',', '_')}.json\"\n"
                 "    !cd /content/gpu_bundle_part3 && python -u run_gpu_timing.py --bundle . --estimators mac "
                 "--sets {batch} --out {out}\n"
                 "    publish(out)\n")
        c["source"] = s.splitlines(keepends=True)
    (ROOT / "gpu" / "CAB_GPU_timing_part3.ipynb").write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n",
                                                             encoding="utf-8")
    print("wrote gpu/CAB_GPU_timing_part3.ipynb")


if __name__ == "__main__":
    main()
