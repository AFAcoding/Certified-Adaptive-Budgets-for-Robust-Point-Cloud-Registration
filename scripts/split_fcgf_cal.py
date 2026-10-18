"""Split the held-out FCGF pool (odd-indexed test pairs, logs/*_fcgf_<set>_cal.jsonl) into a fitting part and a
disjoint certification part, for re-fitting the controller on FCGF (the FPFH-fitted controller is overconfident
on FCGF, so re-certifying its thresholds alone finds no operating point cheaper than the full budget).

  fit   pair index % 8 == 1   (a quarter of the pool: fits p_now / p_fin / Markov controller)
  cert  pair index % 8 != 1   (three quarters: Learn-then-Test certification)

The test pairs (even indices, logs/*_fcgf_<set>.jsonl) are untouched.
Writes logs/budget{,c}_fcgf_<set>_{fit,cert}.jsonl for <set> in {3DMatch, 3DLoMatch}.

Usage: python -I scripts/split_fcgf_cal.py
"""

import json

from acpr import LOG_ROOT
from acpr import fcgf as F


def main():
    for s in ("3DMatch", "3DLoMatch"):
        index = {p.pair_id: p.index for p in F.load_fcgf_3dmatch_pairs(s)}
        for pf in ("budget", "budgetc"):
            recs = [x for x in open(LOG_ROOT / f"{pf}_fcgf_{s}_cal.jsonl") if x.strip()]
            parts = {"fit": [], "cert": []}
            for x in recs:
                i = index[json.loads(x)["pair_id"]]
                assert i % 2 == 1, "calibration pool must hold odd-indexed pairs only"
                parts["fit" if i % 8 == 1 else "cert"].append(x if x.endswith("\n") else x + "\n")
            for k, v in parts.items():
                with open(LOG_ROOT / f"{pf}_fcgf_{s}_{k}.jsonl", "w") as f:
                    f.writelines(v)
            print(f"{pf} {s}: fit {len(parts['fit'])}, cert {len(parts['cert'])}")


if __name__ == "__main__":
    main()
