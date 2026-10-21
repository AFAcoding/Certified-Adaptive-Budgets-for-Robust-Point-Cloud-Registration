"""Independent re-computation of the paper's headline numbers from the raw per-pair logs.

For every test set, estimator and ordering: the certified configuration (results/budget/ladder_selection*.json) is
applied to the test logs (stop stages from the shared controller code), and recall, loss, risk, offline speed-up and
operation reduction are recomputed with separately written cost accounting. Live speed-ups are recomputed from the
live JSONs. Everything is compared with what the paper prints (paper/numbers.tex). Prints MISMATCH lines.

Usage: python -I scripts/validate_numbers.py [project_root]   (after scripts/paper_assets.py)
"""
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import analyze_budget as B  # noqa: E402
import select_ladder as S  # noqa: E402

RB = ROOT / "results" / "budget"
VALS = {}
for line in (ROOT / "paper" / "numbers.tex").read_text(encoding="utf-8").splitlines():
    m = re.match(r"\\defval\{(.+?)\}\{(.*)\}$", line)
    if m:
        VALS[m[1]] = m[2]


def num(k):
    return float(VALS[k].replace("\\ensuremath{-}", "-").replace(",", "").replace("+", ""))


bad = 0


def check(key, value, fmt, tol=0.0):
    global bad
    if key not in VALS:
        print(f"MISSING {key}")
        bad += 1
        return
    printed = num(key)
    if abs(printed - float(fmt.format(value))) > tol + 1e-9:
        print(f"MISMATCH {key}: paper {VALS[key]} vs recomputed {fmt.format(value)}")
        bad += 1


def cost(r, est, ladder, k, field):
    """Independent accounting: ordering once if the first visited budget truncates; each distinct computation once
    (every budget >= N_all is the same run as the first logged full-set stage)."""
    stages = r[est]
    total = 0.0
    if stages[ladder[0]]["n"] < r["N_all"]:
        total += r.get("ops_order" if field == "ops" else "t_order", 0.0)
    seen = set()
    for b in ladder[:k + 1]:
        j = b
        if stages[b].get("repeat"):
            j = min(i for i, s in enumerate(stages) if s is not None and s["n"] >= r["N_all"] and not s.get("repeat"))
        if j not in seen:
            seen.add(j)
            total += stages[j][field]
    return total


SETS = {"bh": ("v2_blind_hi", "v2_indoor_fpfh"), "bl": ("v2_blind_lo", "v2_indoor_fpfh"),
        "m": ("3DMatch", "v2_indoor_fpfh"), "lo": ("3DLoMatch", "v2_indoor_fpfh"),
        "kr": ("kitti_raw_blind", "v2_kitti_fpfh"), "ki": ("kitti_test", "v2_kitti_fpfh"),
        "fm": ("fcgfown_3DMatch", "v2_indoor_fcgf"), "flo": ("fcgfown_3DLoMatch", "v2_indoor_fcgf"),
        "fkr": ("fcgfown_kitti_raw_blind", "v2_kitti_fcgf"), "fki": ("fcgfown_kitti_test", "v2_kitti_fcgf")}
ESTS = {"sc": "sc2", "tr": "turbo"}
risks = []
for d, (log, fam) in SETS.items():
    D = S.DATASETS[fam]
    for o, prefix in (("ratio", "budget"), ("compat", "budgetc")):
        sel = json.loads((RB / f"ladder_selection{S.SUFFIX[prefix]}_ext_{fam}.json").read_text())
        logs = {"train": B.load(D["train"], prefix), "val": B.load(D["val"], prefix), log: B.load(log, prefix)}
        recs = logs[log]
        for e, E in ESTS.items():
            for cert, tag in (("group", "mondrian"), ("marg", "marginal")):
                x = sel[E]["selected"][tag]
                ladder = B.LADDERS_EXT[x["ladder"]]
                tr, mdps = S.build(logs, E, ladder)
                stops = S.policy_outcome(tr[log], mdps, x["policy"], x["param"]).stop
                ok = np.array([bool(r[E][ladder[k]]["ok15"]) for r, k in zip(recs, stops)])
                full_ok = np.array([bool(r[E][4]["ok15"]) for r in recs])
                s = np.array([cost(r, E, ladder, k, "s") for r, k in zip(recs, stops)])
                ops = np.array([cost(r, E, ladder, k, "ops") for r, k in zip(recs, stops)])
                fs = np.array([cost(r, E, (4,), 0, "s") for r in recs])
                fops = np.array([cost(r, E, (4,), 0, "ops") for r in recs])
                k = f"{e}.{d}.{o}.{cert}"
                rr, loss, risk = 100 * ok.mean(), 100 * (full_ok.mean() - ok.mean()), 100 * np.mean(full_ok & ~ok)
                check(k + ".rr", rr, "{:.1f}", 0.05)
                check(k + ".loss", loss, "{:.2f}", 0.005)
                check(k + ".risk", risk, "{:.2f}", 0.005)
                check(k + ".speed", fs.mean() / s.mean(), "{:.2f}", 0.005)
                if cert == "group":
                    check(k + ".ops", fops.mean() / ops.mean(), "{:.2f}", 0.005)
                    if o == "compat":
                        risks.append((risk, k))
                t = sel[E]["test"][log][tag]
                for name, mine, theirs in (("rr", rr, 100 * t["rr"]), ("risk", risk, 100 * t["risk"]),
                                           ("speed", fs.mean() / s.mean(), t["speedup"])):
                    if abs(mine - theirs) > 1e-6:
                        print(f"MISMATCH json {k}.{name}: json {theirs:.4f} vs recomputed {mine:.4f}")
                        bad += 1
print(f"group-conditional (compat) test risks: max {max(risks)[0]:.2f} % ({max(risks)[1]}), "
      f"all <= 1 %: {all(r <= 1.0 for r, _ in risks)}")

# live speed-ups
for d, (sub, fam) in SETS.items():
    rows = json.loads((RB / f"live_budget_compare_ext_{fam}.json").read_text())
    fn = fam
    for e, E in ESTS.items():
        rs = [r for r in rows if r["est"] == E and r["subset"] == sub]
        if not rs:
            print(f"no live rows for {sub}")
            continue
        f = np.mean([r["full"]["s"] for r in rs])
        for o, pf in (("ratio", "budget"), ("compat", "budgetc")):
            check(f"{e}.{d}.{o}.live.speed", f / np.mean([r[pf]["s"] for r in rs]), "{:.2f}", 0.005)
        stall = max(max(r[j]["s"] for j in r["run_order"]) / np.median([q["full"]["s"] for q in rs]) for r in rs)
        if stall > 10:
            print(f"STALL left in {fn} {E} {sub}: {stall:.0f}x the median")
            bad += 1
print("checks done;", "no mismatches" if bad == 0 else f"{bad} problems")
