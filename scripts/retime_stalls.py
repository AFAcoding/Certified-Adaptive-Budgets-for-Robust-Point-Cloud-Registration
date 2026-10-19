"""Re-time the pairs whose live measurement was interrupted by a system stall.

An adaptive run executes at most its whole ladder, about twice a full-budget run, so a run that takes more than
STALL times the median full-budget time of its estimator and test set was interrupted (one KITTI pair took 321 s
instead of about 1 s). Such a pair is timed again with the code of live_budget.py (or live_equal_time.py for the
equal-time file): all of its runs, in their original order. The interrupted times stay in the row under "stalled".

Usage: python -I -u scripts/retime_stalls.py [--dry-run]   (on an otherwise idle machine, after live_budget.py)
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_budget as B  # noqa: E402
import live_budget as L  # noqa: E402
import live_equal_time as E  # noqa: E402

from acpr import RESULTS_ROOT  # noqa: E402

STALL = 10.0
# live file -> (dataset, recal, refit), as written by live_budget.py --ladders extended
FILES = {"live_budget_compare_ext.json": ("3dmatch", False, False),
         "live_budget_compare_ext_kitti.json": ("kitti", False, False),
         "live_budget_compare_ext_fcgf3dmatch_refit.json": ("fcgf3dmatch", False, True),
         "live_budget_compare_ext_fcgfkitti_recal.json": ("fcgfkitti", True, False)}


def stalled(rows):
    full = {}
    for r in rows:
        full.setdefault((r["est"], r["subset"]), []).append(r["full"]["s"])
    med = {k: float(np.median(v)) for k, v in full.items()}
    return [i for i, r in enumerate(rows) if max(r[j]["s"] for j in r["run_order"]) > STALL * med[(r["est"], r["subset"])]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    for fname, (name, recal, refit) in FILES.items():
        path = RESULTS_ROOT / "budget" / fname
        if not path.exists():
            continue
        rows = json.loads(path.read_text())
        bad = stalled(rows)
        print(f"{fname}: {len(bad)} stalled pair(s)", flush=True)
        if not bad or args.dry_run:
            continue
        ds = L.make_dataset(name, recal, refit)
        prefixes = [j for j in rows[0]["run_order"] if j != "full"]
        for est in sorted({rows[i]["est"] for i in bad}):
            ctrls = {pf: L.Controller(pf, est, "extended", ds) for pf in prefixes}
            for subset in sorted({rows[i]["subset"] for i in bad if rows[i]["est"] == est}):
                offline = {pf: {r["pair_id"]: r for r in B.load(subset, pf)} for pf in prefixes}
                pairs = {p.pair_id: p for p in ds.pairs(subset)}
                for i in [i for i in bad if rows[i]["est"] == est and rows[i]["subset"] == subset]:
                    r = rows[i]
                    before = {j: r[j]["s"] for j in r["run_order"]}
                    r.update(L.time_pair(ds, est, ctrls, pairs[r["pair_id"]], r["run_order"], offline))
                    r["stalled"] = before
                    print(f"  {est} {r['pair_id']}: "
                          + ", ".join(f"{j} {before[j]:.2f} -> {r[j]['s']:.2f} s" for j in r["run_order"]), flush=True)
        with open(path, "w") as f:
            json.dump(rows, f, indent=1)
        L.summary(rows, ds, prefixes)
    retime_equal_time(args.dry_run)


def retime_equal_time(dry_run, subset="3DMatch"):
    """The same rule for the equal-time file (live_equal_time.py), whose rows hold one time per variant."""
    path = RESULTS_ROOT / "budget" / f"live_equal_time_{subset}.json"
    if not path.exists():
        return
    rows = json.loads(path.read_text())
    times = lambda r: {k: v for k, v in r.items() if isinstance(v, float)}  # noqa: E731
    med = {est: float(np.median([r["full"] for r in rows if r["est"] == est])) for est in {r["est"] for r in rows}}
    bad = [i for i, r in enumerate(rows) if max(times(r).values()) > STALL * med[r["est"]]]
    print(f"{path.name}: {len(bad)} stalled pair(s)", flush=True)
    if not bad or dry_run:
        return
    ds = L.ThreeDMatch()
    for est in sorted({rows[i]["est"] for i in bad}):
        ctrl = L.Controller("budgetc", est, "extended", ds)
        pairs = {p.pair_id: p for p in ds.pairs(subset)}
        position = [i for i, r in enumerate(rows) if r["est"] == est]  # j: position in the sample (run order)
        for i in [i for i in bad if rows[i]["est"] == est]:
            before = times(rows[i])
            rows[i] = E.time_pair(ds, est, ctrl, pairs[rows[i]["pair_id"]], position.index(i), subset)
            rows[i]["stalled"] = before
            worst = max(before, key=before.get)
            print(f"  {est} {rows[i]['pair_id']}: {worst} {before[worst]:.2f} -> {rows[i][worst]:.2f} s", flush=True)
    with open(path, "w") as f:
        json.dump(rows, f, indent=1)


if __name__ == "__main__":
    main()
