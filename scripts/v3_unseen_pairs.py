"""Protocol v3, deviation 1: the v3 blind pairs that appear in no earlier log (as fitting, training or any other
pair). Run before any v3 blind pair is logged; uses only pair identities, never an outcome.

Writes results/protocol_v3/strictly_unseen.json: {"v3_blind_hi": [pair ids], "v3_blind_lo": [...], "used": n}.
Usage: python -I scripts/v3_unseen_pairs.py
"""

import json

from acpr import LOG_ROOT, RESULTS_ROOT
from acpr.data import load_pairs


def main():
    blind = {s: load_pairs(s) for s in ("v3_blind_hi", "v3_blind_lo")}
    key = {(p.scene, p.frag0, p.frag1): p.pair_id for ps in blind.values() for p in ps}
    scenes = {k[0] for k in key}
    used = set()
    for f in LOG_ROOT.glob("*.jsonl"):
        if "v3_" in f.name:
            continue
        for line in open(f):
            try:
                parts = json.loads(line)["pair_id"].split("/")
            except (ValueError, KeyError):
                continue
            if len(parts) == 3 and parts[1] in scenes:
                a, b = parts[2].split("_")[:2]
                k = (parts[1], int(a), int(b))
                if k in key:
                    used.add(k)
    out = {s: [p.pair_id for p in ps if (p.scene, p.frag0, p.frag1) not in used] for s, ps in blind.items()}
    out["used"] = len(used)
    path = RESULTS_ROOT / "protocol_v3" / "strictly_unseen.json"
    path.write_text(json.dumps(out, indent=0))
    print({s: len(v) for s, v in out.items() if s != "used"}, "used:", len(used))


if __name__ == "__main__":
    main()
