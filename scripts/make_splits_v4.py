"""Protocol v4 (PROTOCOL.md), indoor splits: fresh blind scenes, a larger calibration set of never-processed pairs and
a larger fitting set of already-logged pairs.

Pool: the 3DMatch training scenes that were not a blind scene of protocol v2 or v3 (overlap > 0.1). Blind: pool scenes
permuted with seed 20261022 until they hold at least 3,500 eligible pairs; a random 3,000 of their pairs (seed 1),
minus every pair that appears in any earlier log. Calibration: the eligible pairs of the other pool scenes that appear
in no earlier log, at most 6,000 (seed 2). Fitting: the eligible pairs of the other pool scenes that already have
ratio- and compatibility-order FPFH budget logs; their records are copied into logs/budget{,c}_v4_fit.jsonl (same pair,
same computation), so no fitting pair is recomputed. Uses only metadata and log identities, never an outcome.
Re-running reproduces the same files.

Writes data/3DMatch/metadata/{v4_fit, v4_cal, v4_blind_hi, v4_blind_lo}.json and results/protocol_v4/indoor_splits.json.
Usage: python -I scripts/make_splits_v4.py
"""

import json

import numpy as np

from acpr import LOG_ROOT, RESULTS_ROOT
from acpr.data import THREEDMATCH_ROOT

SEED = 20261022
TARGET = 3500
FPFH_LOGS = ("train", "v2_fit", "v2_cal", "v3_fit")  # indoor FPFH budget logs of training-scene pairs


def key(x):
    return (x["scene"], x["frag0"], x["frag1"])


def pair_key(pid):
    parts = pid.split("/")
    if len(parts) != 3:
        return None
    a, b = parts[2].split("_")[:2]
    return (parts[1], int(a), int(b))


def main():
    meta = THREEDMATCH_ROOT / "metadata"
    v2 = json.loads((RESULTS_ROOT / "protocol_v2" / "indoor_splits.json").read_text())
    v3 = json.loads((RESULTS_ROOT / "protocol_v3" / "indoor_splits.json").read_text())
    used_blind = set(v2["blind_scenes"]) | set(v3["blind_scenes"])
    train = [x for x in json.loads((meta / "train.json").read_text()) if x["overlap"] > 0.1]
    pool = sorted({x["scene"] for x in train} - used_blind)
    count = {s: sum(x["scene"] == s for x in train) for s in pool}

    seen = set()  # every pair in any earlier log, under any role
    for f in LOG_ROOT.glob("*.jsonl"):
        if "v4_" in f.name:
            continue
        for line in open(f):
            try:
                k = pair_key(json.loads(line)["pair_id"])
            except (ValueError, KeyError):
                continue
            if k:
                seen.add(k)

    order = [pool[i] for i in np.random.default_rng(SEED).permutation(len(pool))]
    blind_sc = []
    for s in order:
        if sum(count[x] for x in blind_sc) >= TARGET:
            break
        blind_sc.append(s)
    rest_sc = [s for s in pool if s not in blind_sc]

    cand = [x for x in train if x["scene"] in blind_sc]
    idx = np.sort(np.random.default_rng(1).choice(len(cand), min(3000, len(cand)), replace=False))
    sampled = [cand[i] for i in idx]
    blind = [x for x in sampled if key(x) not in seen]

    fresh_rest = [x for x in train if x["scene"] in rest_sc and key(x) not in seen]
    if len(fresh_rest) > 6000:
        idx = np.sort(np.random.default_rng(2).choice(len(fresh_rest), 6000, replace=False))
        cal = [fresh_rest[i] for i in idx]
    else:
        cal = fresh_rest

    # fitting: pairs of the other pool scenes logged in both orders by an earlier FPFH budget log
    logged = {"budget": {}, "budgetc": {}}
    for prefix in logged:
        for sub in FPFH_LOGS:
            path = LOG_ROOT / f"{prefix}_{sub}.jsonl"
            if not path.exists():
                continue
            for line in open(path):
                if not line.strip():
                    continue
                r = json.loads(line)
                k = pair_key(r["pair_id"])
                if k and k[0] in rest_sc and k not in logged[prefix]:
                    logged[prefix][k] = r
    rest_keys = {key(x): x for x in train if x["scene"] in rest_sc}
    fit_keys = sorted(set(logged["budget"]) & set(logged["budgetc"]) & set(rest_keys))
    fit = [rest_keys[k] for k in fit_keys]
    assert not ({key(x) for x in fit} & {key(x) for x in cal}), "fitting and calibration pairs overlap"

    out = {"v4_fit": fit, "v4_cal": cal, "v4_blind_hi": [x for x in blind if x["overlap"] > 0.3],
           "v4_blind_lo": [x for x in blind if x["overlap"] <= 0.3]}
    for name, items in out.items():
        (meta / f"{name}.json").write_text(json.dumps(items))
    copied = {}
    for prefix in logged:
        dst = LOG_ROOT / f"{prefix}_v4_fit.jsonl"
        if dst.exists():
            copied[prefix] = "exists"
            continue
        with open(dst, "w") as g:
            for k in fit_keys:
                r = dict(logged[prefix][k])
                r["pair_id"], r["subset"] = f"v4_fit/{k[0]}/{k[1]}_{k[2]}", "v4_fit"
                g.write(json.dumps(r) + "\n")
        copied[prefix] = len(fit_keys)
    summary = {"seed": SEED, "pool_scenes": len(pool), "blind_scenes": blind_sc, "other_scenes": rest_sc,
               "pairs": {k: len(v) for k, v in out.items()}, "blind_sampled": len(sampled),
               "blind_dropped_seen_before": len(sampled) - len(blind), "cal_never_processed_available": len(fresh_rest),
               "fit_log_records_copied": copied}
    d = RESULTS_ROOT / "protocol_v4"
    d.mkdir(parents=True, exist_ok=True)
    (d / "indoor_splits.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps({k: v for k, v in summary.items() if k not in ("blind_scenes", "other_scenes")}, indent=1))


if __name__ == "__main__":
    main()
