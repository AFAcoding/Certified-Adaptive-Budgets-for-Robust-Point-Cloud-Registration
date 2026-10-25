"""Download the per-pair logs of all experiments (GitHub Release asset) into logs/.

With the logs, every number, table and figure can be regenerated in minutes (scripts/paper_assets.py and the
selection scripts) without re-running the experiments, which take days on a CPU.

logs-v4.0.zip adds the MAC logs (addenda A and B) and the exploration logs to logs-v3.0.zip. If release v4.0 is not
available, the script falls back to v3.0, which has every log except MAC's.

Usage: python -I scripts/download_logs.py
"""

import hashlib
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

BASE = "https://github.com/AFAcoding/Certified-Adaptive-Budgets-for-Robust-Point-Cloud-Registration/releases/download"
ARCHIVES = [  # (tag, sha256), newest first
    ("v4.0", "b63360f182cbe3834cef84b958f9d01deb25e96b12be0055c4570df45d38d4ae"),
    ("v3.0", "71fdba2e6c662e94ae9b6dcd4a619c3a42b18bd5f1cde5f96b222d1bb84ccbd1"),
]
ROOT = Path(__file__).resolve().parents[1]


def fetch(tag, sha, logs):
    archive = logs / f"logs-{tag}.zip"
    if not archive.exists():
        url = f"{BASE}/{tag}/logs-{tag}.zip"
        print(f"downloading {url}", flush=True)
        try:
            urllib.request.urlretrieve(url, archive)
        except urllib.error.HTTPError as e:
            print(f"  not available ({e.code})")
            archive.unlink(missing_ok=True)
            return None
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != sha:
        sys.exit(f"checksum mismatch for {archive}: {digest}")
    return archive


def main():
    logs = ROOT / "logs"
    logs.mkdir(exist_ok=True)
    for tag, sha in ARCHIVES:
        archive = fetch(tag, sha, logs)
        if archive:
            break
    else:
        sys.exit("no log archive could be downloaded")
    with zipfile.ZipFile(archive) as z:
        names = [n for n in z.namelist() if n.endswith(".jsonl") and "/" not in n and "\\" not in n]
        for n in names:  # flat archive of .jsonl files only
            (logs / n).write_bytes(z.read(n))
    archive.unlink()
    print(f"{len(names)} log files from logs-{tag}.zip in {logs}")
    if tag != ARCHIVES[0][0]:
        print("note: the MAC logs are only in logs-v4.0.zip")


if __name__ == "__main__":
    main()
