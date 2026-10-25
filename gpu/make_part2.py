"""Assemble gpu_bundle_part2.zip from the exports of the remaining test sets (KITTI raw drives, 3DMatch, 3DLoMatch from
gpu_bundle/; KITTI odometry, FCGF 3DMatch and FCGF 3DLoMatch from their parallel exports gpu_bundle_<set>/), once all
are written. Stops the main export after 3DLoMatch, so that it does not repeat the sets exported in parallel."""

import json
import shutil
import subprocess
import time
import zipfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {"kr": "gpu_bundle", "m": "gpu_bundle", "lo": "gpu_bundle",
           "ki": "gpu_bundle_ki", "fm": "gpu_bundle_fm", "flo": "gpu_bundle_flo"}


def done(code, folder):
    cfg = ROOT / folder / "config.json"
    return cfg.exists() and code in json.loads(cfg.read_text())["sets"] and (ROOT / folder / f"data_{code}.npz").exists()


def main():
    stopped = False
    while True:  # the stop check comes first: the parallel exports can finish before the main one reaches 3DLoMatch
        if not stopped and all(done(c, "gpu_bundle") for c in ("kr", "m", "lo")):
            subprocess.run(["powershell.exe", "-NoProfile", "-Command",
                            "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and "
                            "$_.CommandLine -like '*th,tl,bh,bl,kr,m,lo,ki,fm,flo*' } | "
                            "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -Confirm:$false }"], check=False)
            stopped = True
            print(time.strftime("%H:%M"), "main export stopped after 3DLoMatch", flush=True)
        if stopped and all(done(c, f) for c, f in SOURCES.items()):
            break
        time.sleep(30)
    part = ROOT / "gpu_bundle_part2"
    if part.exists():
        shutil.rmtree(part)
    part.mkdir()
    cfg, models = None, {}
    for code, folder in SOURCES.items():
        c = json.loads((ROOT / folder / "config.json").read_text())
        if cfg is None:
            cfg = {**c, "sets": {}}
        cfg["sets"][code] = c["sets"][code]
        m = np.load(ROOT / folder / "models.npz")
        models.update({k: m[k] for k in m.files if k.split("/")[0] == code})
        shutil.copy(ROOT / folder / f"data_{code}.npz", part / f"data_{code}.npz")
        z = np.load(part / f"data_{code}.npz")
        assert len(z["pair_id"]) == 300, code
    np.savez_compressed(part / "models.npz", **models)
    (part / "config.json").write_text(json.dumps(cfg, indent=1))
    for f in ("cab_gpu.py", "run_gpu_timing.py", "README.md"):
        shutil.copy(ROOT / "gpu" / f, part / f)
    with zipfile.ZipFile(ROOT / "gpu_bundle_part2.zip", "w", zipfile.ZIP_STORED) as zf:
        for f in sorted(part.iterdir()):
            zf.write(f, f"gpu_bundle_part2/{f.name}")
    # the full local bundle (references for the paper's analysis): every set in one config
    full = json.loads((ROOT / "gpu_bundle" / "config.json").read_text())
    full["sets"].update(cfg["sets"])
    (ROOT / "gpu_bundle" / "config.json").write_text(json.dumps(full, indent=1))
    print(time.strftime("%H:%M"), "gpu_bundle_part2.zip:", {c: list(e["estimators"]) for c, e in cfg["sets"].items()},
          f"{(ROOT / 'gpu_bundle_part2.zip').stat().st_size / 2**20:.0f} MB", flush=True)


if __name__ == "__main__":
    main()
