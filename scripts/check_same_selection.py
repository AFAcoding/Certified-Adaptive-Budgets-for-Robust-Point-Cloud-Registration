"""Check that a selection re-run with its test sets chose and certified exactly what was written to disk before any
test pair was processed (select_ladder.py --no-tests): ladder, policy, parameters, classifier and gate, for every
estimator and certificate. Exits with status 1 on any difference.

Usage: python -I scripts/check_same_selection.py <selection_only.json> <evaluated.json> [...pairs]
"""

import json
import sys


def main():
    args = sys.argv[1:]
    bad = 0
    for a, b in zip(args[::2], args[1::2]):
        x, y = json.load(open(a)), json.load(open(b))
        for est in x:
            for tag in x[est]["selected"]:
                for k in ("ladder", "policy", "param", "classifier", "gate", "fallback"):
                    if x[est]["selected"][tag].get(k) != y[est]["selected"][tag].get(k):
                        print(f"DIFFERENT {b} {est} {tag} {k}")
                        bad += 1
        print(f"{b}: {'identical' if not bad else 'DIFFERENT'} to {a}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
