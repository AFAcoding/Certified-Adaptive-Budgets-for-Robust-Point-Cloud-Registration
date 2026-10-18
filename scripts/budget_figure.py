"""Insight figure for adaptive correspondence budgets.

(a) Speed-up over the standard full-budget estimator: ours (validation-selected,
    certified) vs. the accept-only oracle (perfect early acceptance, no failure
    detection) vs. the full oracle.
(b) Share of pairs that are unsolvable at any budget vs. their share of full-budget time.

Usage: python -I scripts/budget_figure.py
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_budget as B  # noqa: E402

from acpr import RESULTS_ROOT  # noqa: E402

INK, INK2, MUTED, GRID, BASE, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"


def main():
    sel = json.loads((RESULTS_ROOT / "budget" / "ladder_selection.json").read_text())
    cases, ours, acc, orc, unsolv_pairs, unsolv_time = [], [], [], [], [], []
    for est, en in [("sc2", "SC²"), ("turbo", "TurboReg")]:
        for s in ["3DMatch", "3DLoMatch"]:
            recs = B.load(s)
            tr = [B.trajectory_ladder(r, est, B.LADDERS["x4"]) for r in recs]
            # true full-budget time (the N=4,000 entry is a free repeat when N_all <= 2,000)
            full = np.array([B.trajectory_ladder(r, est, (4,))[-1]["s"] for r in recs])
            first_ok = [next((st["stage"] for st in t if st["ok"]), None) for t in tr]
            solved = np.array([k is not None for k in first_ok])
            o = np.array([t[k]["s"] if k is not None else t[0]["s"] for t, k in zip(tr, first_ok)])
            a = np.array([t[k]["s"] if k is not None else t[-1]["s"] for t, k in zip(tr, first_ok)])
            m = sel[est]["test"][s]["mondrian"]
            cases.append(f"{en}\n{s}")
            ours.append(full.mean() / m["s"])
            acc.append(full.mean() / a.mean())
            orc.append(full.mean() / o.mean())
            unsolv_pairs.append(100 * (1 - solved.mean()))
            unsolv_time.append(100 * full[~solved].sum() / full.sum())
            print(f"{en:8s} {s:9s}: speed-up ours (Mondrian) {ours[-1]:.2f}x | accept-only oracle {acc[-1]:.2f}x | "
                  f"full oracle {orc[-1]:.2f}x | ours / accept-only {ours[-1] / acc[-1]:.0%} | "
                  f"unsolvable: {unsolv_pairs[-1]:.0f}% of pairs, {unsolv_time[-1]:.0f}% of full-budget time")
    plt.rcParams.update({"font.family": "sans-serif", "font.size": 9, "axes.edgecolor": BASE, "axes.labelcolor": INK2,
                         "xtick.color": MUTED, "ytick.color": MUTED, "figure.facecolor": SURF, "axes.facecolor": SURF,
                         "savefig.facecolor": SURF})
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.6), dpi=160, gridspec_kw={"width_ratios": [1.4, 1]})
    x = np.arange(len(cases))
    ax = axes[0]
    for xi, (vals, col, lab) in enumerate([(ours, BLUE, "Ours (certified, Mondrian)"),
                                           (acc, AQUA, "Accept-only oracle (no failure detection)"),
                                           (orc, ORANGE, "Full oracle")]):
        bars = ax.bar(x + (xi - 1) * 0.26, vals, width=0.24, color=col, label=lab)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.08, f"{v:.1f}×", ha="center", fontsize=7, color=INK2)
    ax.axhline(1, color=MUTED, lw=1, ls="--")
    ax.set_xticks(x, cases, fontsize=8)
    ax.set_ylabel("Speed-up over full-budget estimator")
    ax.set_title("(a) Where the speed-up comes from", loc="left", color=INK, fontsize=9.5)
    ax.legend(frameon=False, fontsize=7.5, labelcolor=INK2, loc="upper left")
    ax2 = axes[1]
    ax2.bar(x - 0.18, unsolv_pairs, width=0.34, color=BASE, label="share of pairs")
    ax2.bar(x + 0.18, unsolv_time, width=0.34, color=BLUE, label="share of full-budget time")
    ax2.set_xticks(x, cases, fontsize=8)
    ax2.set_ylabel("Unsolvable pairs: % of pairs, % of time")
    ax2.set_xlabel("")
    ax2.set_title("(b) Unsolvable pairs and their cost", loc="left", color=INK, fontsize=9.5)
    ax2.legend(frameon=False, fontsize=7.5, labelcolor=INK2, loc="upper left")
    ax2.set_ylim(0, 80)
    for a_ in axes:
        a_.grid(True, axis="y", color=GRID, lw=0.6)
        a_.set_axisbelow(True)
        for sp in ("top", "right"):
            a_.spines[sp].set_visible(False)
    fig.tight_layout()
    out = RESULTS_ROOT / "budget" / "fig_budget_insight.png"
    fig.savefig(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
