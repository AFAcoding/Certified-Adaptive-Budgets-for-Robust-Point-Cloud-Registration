"""Download the per-pair logs of all experiments (GitHub Release asset) into logs/.

With the logs, every number, table and figure can be regenerated in minutes (scripts/paper_assets.py and the
selection scripts) without re-running the experiments, which take days on a CPU.

Usage: python -I scripts/download_logs.py
"""

import hashlib
import sys
import urllib.request
import zipfile
from pathlib import Path

URL = ("https://github.com/AFAcoding/Certified-Adaptive-Budgets-for-Robust-Point-Cloud-Registration/"
       "releases/download/v1.0/logs-v1.0.zip")
SHA256 = "25ed91dd102b3033c17a7640dffab7f3e040b37878440d01cead2337b945e184"
ROOT = Path(__file__).resolve().parents[1]


def main():
    logs = ROOT / "logs"
    logs.mkdir(exist_ok=True)
    archive = logs / "logs-v1.0.zip"
    if not archive.exists():
        print(f"downloading {URL}", flush=True)
        urllib.request.urlretrieve(URL, archive)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != SHA256:
        sys.exit(f"checksum mismatch for {archive}: {digest}")
    with zipfile.ZipFile(archive) as z:
        names = [n for n in z.namelist() if n.endswith(".jsonl") and "/" not in n and "\\" not in n]
        for n in names:  # flat archive of .jsonl files only
            (logs / n).write_bytes(z.read(n))
    archive.unlink()
    print(f"{len(names)} log files in {logs}")


if __name__ == "__main__":
    main()
