"""Add the MAC stages (logs/mac_<subset>.jsonl, scripts/build_mac_logs.py) to the budget logs of a subset: every record
of logs/budget_<subset>.jsonl gets "mac" = the ratio-order stages, every record of logs/budgetc_<subset>.jsonl the
compatibility-order stages. Nothing else in the records changes; the originals are kept in logs/premac_backup/.
Every logged pair must have its MAC stages.

Usage: python -I scripts/merge_mac_logs.py <subset> [<subset> ...]
"""

import json
import shutil
import sys

from acpr import LOG_ROOT


def main():
    bak = LOG_ROOT / "premac_backup"
    bak.mkdir(exist_ok=True)
    for subset in sys.argv[1:]:
        mac = {}
        for line in open(LOG_ROOT / f"mac_{subset}.jsonl"):
            if line.strip():
                r = json.loads(line)
                mac[r["pair_id"]] = r
        for prefix, order in (("budget", "ratio"), ("budgetc", "compat")):
            path = LOG_ROOT / f"{prefix}_{subset}.jsonl"
            if not (bak / path.name).exists():
                shutil.copy2(path, bak / path.name)
            recs = [json.loads(x) for x in open(bak / path.name) if x.strip()]
            missing = [r["pair_id"] for r in recs if r["pair_id"] not in mac]
            assert not missing, f"{path.name}: {len(missing)} pairs without MAC stages"
            tmp = path.with_suffix(".tmp")
            with open(tmp, "w") as g:
                for r in recs:
                    r["mac"] = mac[r["pair_id"]][order]
                    g.write(json.dumps(r) + "\n")
            tmp.replace(path)
            print(f"{path.name}: {len(recs)} records with MAC stages")


if __name__ == "__main__":
    main()
