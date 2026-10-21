"""Protocol v2: the fitting pairs that were already logged as part of the old 1,000-pair training sample get their
records copied (same pair, same computation) into the v2_fit logs; build_budget_logs.py then runs only the others.

Usage: python -I scripts/reuse_fit_logs_v2.py
"""

import json

from acpr import LOG_ROOT
from acpr.data import load_pairs


def main():
    want = {(p.scene, p.frag0, p.frag1): p.pair_id for p in load_pairs("v2_fit")}
    for prefix in ("budget", "budgetc"):
        out = LOG_ROOT / f"{prefix}_v2_fit.jsonl"
        if out.exists():
            print(f"{out.name} exists, skipped")
            continue
        n = 0
        with open(LOG_ROOT / f"{prefix}_train.jsonl") as f, open(out, "w") as g:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                _, scene, frags = r["pair_id"].split("/")
                a, b = map(int, frags.split("_"))
                if (scene, a, b) in want:
                    r["pair_id"], r["subset"] = want[(scene, a, b)], "v2_fit"
                    g.write(json.dumps(r) + "\n")
                    n += 1
        print(f"{out.name}: {n} records reused")


if __name__ == "__main__":
    main()
