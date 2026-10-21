"""Protocol v2 (PROTOCOL.md), indoor splits: fitting, calibration and blind-test pairs from the 3DMatch training scenes.

Writes data/3DMatch/metadata/{v2_fit, v2_cal, v2_blind_hi, v2_blind_lo}.json (same schema as train.json) and
results/protocol_v2/indoor_splits.json (scene lists and counts). Uses only the metadata (scene names, overlaps), never
a registration outcome. Re-running reproduces the same files.

Usage: python -I scripts/make_splits_v2.py
"""

import json

import numpy as np

from acpr import RESULTS_ROOT
from acpr.data import THREEDMATCH_ROOT

SEED = 20261019
TARGET = 3500


def main():
    meta = THREEDMATCH_ROOT / "metadata"
    train = [x for x in json.loads((meta / "train.json").read_text()) if x["overlap"] > 0.1]
    scenes = sorted({x["scene"] for x in train})
    count = {s: sum(x["scene"] == s for x in train) for s in scenes}
    order = [scenes[i] for i in np.random.default_rng(SEED).permutation(len(scenes))]
    test_sc, cal_sc, n = [], [], 0
    for s in order:  # blind test first, then calibration, the rest is fitting
        if sum(count[x] for x in test_sc) < TARGET:
            test_sc.append(s)
        elif sum(count[x] for x in cal_sc) < TARGET:
            cal_sc.append(s)
    fit_sc = [s for s in scenes if s not in test_sc and s not in cal_sc]

    def pick(sc, k, seed):
        pool = [x for x in train if x["scene"] in sc]
        idx = np.sort(np.random.default_rng(seed).choice(len(pool), min(k, len(pool)), replace=False))
        return [pool[i] for i in idx]

    blind = pick(test_sc, 3000, 1)
    cal = pick(cal_sc, 3000, 2)
    # fitting: the existing 1,000-pair training sample (build_budget_logs.py --sample 1000) inside fitting scenes,
    # topped up to 1,000 with other fitting-scene pairs
    full = json.loads((meta / "train.json").read_text())
    old = [full[i] for i in sorted(np.random.default_rng(0).choice(len(full), 1000, replace=False).tolist())]
    key = lambda x: (x["scene"], x["frag0"], x["frag1"])  # noqa: E731
    fit = [x for x in old if x["scene"] in fit_sc and x["overlap"] > 0.1]
    have = {key(x) for x in fit}
    rest = [x for x in train if x["scene"] in fit_sc and key(x) not in have]
    extra = np.sort(np.random.default_rng(3).choice(len(rest), 1000 - len(fit), replace=False))
    fit += [rest[i] for i in extra]
    fit.sort(key=key)

    out = {"v2_fit": fit, "v2_cal": cal,
           "v2_blind_hi": [x for x in blind if x["overlap"] > 0.3],
           "v2_blind_lo": [x for x in blind if x["overlap"] <= 0.3]}
    for name, items in out.items():
        (meta / f"{name}.json").write_text(json.dumps(items))
    summary = {"seed": SEED, "blind_scenes": test_sc, "calibration_scenes": cal_sc, "fitting_scenes": fit_sc,
               "pairs": {k: len(v) for k, v in out.items()},
               "pairs_available": {"blind": sum(count[s] for s in test_sc), "calibration": sum(count[s] for s in cal_sc),
                                   "fitting": sum(count[s] for s in fit_sc)},
               "fit_reused_from_old_sample": len(have)}
    d = RESULTS_ROOT / "protocol_v2"
    d.mkdir(parents=True, exist_ok=True)
    (d / "indoor_splits.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
