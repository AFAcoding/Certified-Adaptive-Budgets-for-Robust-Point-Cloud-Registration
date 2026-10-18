"""Combined accuracy-vs-cost figure for the README (test sets).

Usage: python -I scripts/combined_figure.py results/search_jump1024 results/psh_jump1024 results/fig_tradeoff.png
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from acpr import analysis as A  # noqa: E402

INK, INK2, MUTED, GRID, BASE, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"


def front(items):
    pts = sorted({(x["ce"] / 1e3, 100 * x["rr"]) for x in items})
    return A.upper_hull(pts)


def main():
    full = json.loads((Path(sys.argv[1]) / "summary.json").read_text())
    psh = json.loads((Path(sys.argv[2]) / "summary.json").read_text())
    out = Path(sys.argv[3])
    plt.rcParams.update({"font.family": "sans-serif", "font.size": 9, "axes.edgecolor": BASE, "axes.labelcolor": INK2,
                         "xtick.color": MUTED, "ytick.color": MUTED, "figure.facecolor": SURF, "axes.facecolor": SURF,
                         "savefig.facecolor": SURF})
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), dpi=160)
    for ax, s in zip(axes, ["3DMatch", "3DLoMatch"]):
        ax.grid(True, color=GRID, linewidth=0.6)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        F, Pz = full["sets"][s], psh["sets"][s]
        h = A.upper_hull([(x["ce"] / 1e3, 100 * x["rr"]) for x in F["static"]])
        ax.plot([p[0] for p in h], [p[1] for p in h], color=MUTED, lw=1.2, ls="--", label="Static search configs, full voting (frontier)")
        for st, col, lab, mk in [(F, BLUE, "Adaptive search, full voting", "o"),
                                 (Pz, AQUA, "Adaptive search, progressive voting", "^")]:
            fr = front(st["families"]["mdp"])
            ax.plot([p[0] for p in fr], [p[1] for p in fr], color=col, lw=2, marker=mk, ms=4, label=lab)
            if "mdp" in st["operating_points"]:
                op = st["operating_points"]["mdp"]
                ax.scatter([op["ce"] / 1e3], [100 * op["rr"]], s=110, marker="*", color=col, edgecolor=SURF, zorder=5)
        fr = front(F["families"]["ransac_fixed"])
        ax.plot([p[0] for p in fr], [p[1] for p in fr], color=ORANGE, lw=2, marker="s", ms=4, label="RANSAC, fixed budgets")
        cr = F["classical_ransac"]
        ax.scatter([cr["ce"] / 1e3], [100 * cr["rr"]], s=46, facecolor=SURF, edgecolor=ORANGE, linewidth=2, zorder=4,
                   label="RANSAC, classical stopping")
        ex = F["exhaustive"]
        ax.scatter([ex["ce"] / 1e3], [100 * ex["rr"]], s=46, marker="D", color=INK2, zorder=4, label="Exhaustive search")
        ax.axhline(100 * F["sc2"]["rr"], color=MUTED, lw=1, ls=":")
        ax.text(ax.get_xlim()[0] if False else 25, 100 * F["sc2"]["rr"] + 0.3, "SC² recall", color=INK2, fontsize=7.5)
        ax.set_xscale("log")
        ax.set_xlabel("Mean search cost per pair (thousand correspondence evaluations, log)")
        ax.set_ylabel("Registration recall (%)")
        ax.set_title(f"{s} test set  (★ = certified operating point)", color=INK, fontsize=9.5,
                     loc="left")
    axes[0].legend(frameon=False, fontsize=7.2, loc="lower right", labelcolor=INK2)
    fig.tight_layout()
    fig.savefig(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
