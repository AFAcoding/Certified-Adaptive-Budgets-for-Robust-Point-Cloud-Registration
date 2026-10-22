"""Protocol v3 (PROTOCOL.md), indoor splits: fresh blind scenes from the v2 fitting scenes, and v3 fitting pairs.

The 53 v2 fitting scenes are permuted with seed 20261021 and assigned to the v3 blind test until it holds at least
3,500 pairs with overlap > 0.1; the blind test is a random sample of 3,000 of them (seed 1), split at 30 % overlap.
v3 fitting pairs: the v2 fitting pairs outside the v3 blind scenes, topped up to 1,000 with random pairs (seed 3) of
the remaining fitting scenes. Calibration stays v2_cal. Uses only the metadata (scene names, overlaps), never a
registration outcome. The logs of the kept v2 fitting pairs are copied (same pair, same computation) into the v3_fit
logs, so build_budget_logs.py computes only the new pairs. Re-running reproduces the same files.

Writes data/3DMatch/metadata/{v3_fit, v3_blind_hi, v3_blind_lo}.json and results/protocol_v3/indoor_splits.json.
Usage: python -I scripts/make_splits_v3.py
"""

import json

import numpy as np

from acpr import LOG_ROOT, RESULTS_ROOT
from acpr.data import THREEDMATCH_ROOT

SEED = 20261021
TARGET = 3500


def main():
    meta = THREEDMATCH_ROOT / "metadata"
    v2 = json.loads((RESULTS_ROOT / "protocol_v2" / "indoor_splits.json").read_text())
    fit_scenes = sorted(v2["fitting_scenes"])
    train = [x for x in json.loads((meta / "train.json").read_text()) if x["overlap"] > 0.1]
    count = {s: sum(x["scene"] == s for x in train) for s in fit_scenes}
    order = [fit_scenes[i] for i in np.random.default_rng(SEED).permutation(len(fit_scenes))]
    blind_sc = []
    for s in order:
        if sum(count[x] for x in blind_sc) >= TARGET:
            break
        blind_sc.append(s)
    rest_sc = [s for s in fit_scenes if s not in blind_sc]
    pool = [x for x in train if x["scene"] in blind_sc]
    idx = np.sort(np.random.default_rng(1).choice(len(pool), min(3000, len(pool)), replace=False))
    blind = [pool[i] for i in idx]

    key = lambda x: (x["scene"], x["frag0"], x["frag1"])  # noqa: E731
    # deviation 1 (no leakage): drop every sampled pair that appears in any earlier log, whatever its role
    # (fitting, training, calibration); the v3 blind test holds only pairs nothing has ever processed
    seen = set()
    for f in LOG_ROOT.glob("*.jsonl"):
        if "v3_" in f.name:
            continue
        for line in open(f):
            try:
                parts = json.loads(line)["pair_id"].split("/")
            except (ValueError, KeyError):
                continue
            if len(parts) == 3 and parts[1] in blind_sc:
                a, b = parts[2].split("_")[:2]
                seen.add((parts[1], int(a), int(b)))
    n_sampled = len(blind)
    blind = [x for x in blind if key(x) not in seen]
    v2_fit = json.loads((meta / "v2_fit.json").read_text())
    fit = [x for x in v2_fit if x["scene"] in rest_sc]
    have = {key(x) for x in fit}
    rest = [x for x in train if x["scene"] in rest_sc and key(x) not in have]
    extra = np.sort(np.random.default_rng(3).choice(len(rest), 1000 - len(fit), replace=False))
    fit += [rest[i] for i in extra]
    fit.sort(key=key)

    out = {"v3_fit": fit, "v3_blind_hi": [x for x in blind if x["overlap"] > 0.3],
           "v3_blind_lo": [x for x in blind if x["overlap"] <= 0.3]}
    for name, items in out.items():
        (meta / f"{name}.json").write_text(json.dumps(items))

    # copy the logged v2 fitting records of the kept pairs (pair ids follow the subset name)
    kept = {key(x) for x in v2_fit if x["scene"] in rest_sc}
    copied = {}
    for prefix in ("budget", "budgetc"):
        dst = LOG_ROOT / f"{prefix}_v3_fit.jsonl"
        if dst.exists():
            copied[prefix] = "exists"
            continue
        n = 0
        with open(LOG_ROOT / f"{prefix}_v2_fit.jsonl") as f, open(dst, "w") as g:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                _, scene, frags = r["pair_id"].split("/")
                a, b = map(int, frags.split("_"))
                if (scene, a, b) in kept:
                    r["pair_id"], r["subset"] = f"v3_fit/{scene}/{frags}", "v3_fit"
                    g.write(json.dumps(r) + "\n")
                    n += 1
        copied[prefix] = n
    summary = {"seed": SEED, "blind_scenes": blind_sc, "fitting_scenes": rest_sc,
               "pairs": {k: len(v) for k, v in out.items()},
               "pairs_available_blind": sum(count[s] for s in blind_sc), "blind_sampled": n_sampled,
               "blind_dropped_seen_before": n_sampled - len(blind),
               "fit_kept_from_v2": len(kept), "fit_new": 1000 - len(kept), "log_records_copied": copied}
    d = RESULTS_ROOT / "protocol_v3"
    d.mkdir(parents=True, exist_ok=True)
    (d / "indoor_splits.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
