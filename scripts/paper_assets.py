"""Generate every number, table and figure of the paper from the result files.

Writes paper/numbers.tex (\\defval{key}{value}), paper/tables/*.tex and paper/figures/*.pdf.
Nothing in the paper is typed by hand: rerun after any re-analysis. Inputs that do not exist yet
(e.g. KITTI before its logs are built) are skipped, so drafts compile at any time.

Usage: python -I scripts/paper_assets.py
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

from acpr import LOG_ROOT, PROJECT_ROOT, RESULTS_ROOT  # noqa: E402
from acpr import analysis as A  # noqa: E402

PAPER = PROJECT_ROOT / "paper"
TAB, FIG = PAPER / "tables", PAPER / "figures"
RB = RESULTS_ROOT / "budget"
SETS = {"m": "3DMatch", "lo": "3DLoMatch"}                       # Part A (pose search)
DS = {"m": ("3DMatch", "3dmatch"), "lo": ("3DLoMatch", "3dmatch"), "ki": ("kitti_test", "kitti"),
      # FCGF: configurations certified on FPFH validation, applied unchanged (transfer); see evaluate_transfer.py
      "fm": ("fcgf_3DMatch", "fcgf3dmatch"), "flo": ("fcgf_3DLoMatch", "fcgf3dmatch"), "fki": ("fcgf_kitti_test", "fcgfkitti")}
DNAME = {"m": "3DMatch", "lo": "3DLoMatch", "ki": "KITTI", "fm": "3DMatch", "flo": "3DLoMatch", "fki": "KITTI"}
FCGF = {"fm", "flo", "fki"}
DATASETS_CAL = {"fm": ["fcgf_3DMatch_cal", "fcgf_3DLoMatch_cal"], "flo": ["fcgf_3DMatch_cal", "fcgf_3DLoMatch_cal"],
                "fki": ["fcgf_kitti_test_cal"]}
DATASETS_FIT = {"fm": ["fcgf_3DMatch_fit", "fcgf_3DLoMatch_fit"], "flo": ["fcgf_3DMatch_fit", "fcgf_3DLoMatch_fit"]}


def dlabel(d):
    return DNAME[d] + (" (FCGF)" if d in FCGF else "")
SEL = {("3dmatch", "ratio"): "ladder_selection_ext.json", ("3dmatch", "compat"): "ladder_selection_compat_ext.json",
       ("kitti", "ratio"): "ladder_selection_ext_kitti.json", ("kitti", "compat"): "ladder_selection_compat_ext_kitti.json",
       # FCGF 3DMatch/3DLoMatch: controller re-fitted on a quarter of the held-out (odd-indexed) FCGF pairs and
       # certified on the rest; FCGF KITTI: thresholds re-certified on its 276 held-out pairs (too few to split)
       ("fcgf3dmatch", "ratio"): "ladder_selection_ext_fcgf3dmatch_refit.json",
       ("fcgf3dmatch", "compat"): "ladder_selection_compat_ext_fcgf3dmatch_refit.json",
       ("fcgfkitti", "ratio"): "ladder_selection_ext_fcgfkitti.json",
       ("fcgfkitti", "compat"): "ladder_selection_compat_ext_fcgfkitti.json"}
# FCGF 3DMatch/3DLoMatch with the FPFH controller and only its thresholds re-certified on FCGF (finds nothing
# cheaper than the full budget: the FPFH controller's confidence saturates on FCGF)
SEL_RCERT = {("fcgf3dmatch", "ratio"): "ladder_selection_ext_fcgf3dmatch.json",
             ("fcgf3dmatch", "compat"): "ladder_selection_compat_ext_fcgf3dmatch.json"}
LIVE = {"3dmatch": "live_budget_compare_ext.json", "kitti": "live_budget_compare_ext_kitti.json",
        "fcgf3dmatch": "live_budget_compare_ext_fcgf3dmatch_refit.json",
        "fcgfkitti": "live_budget_compare_ext_fcgfkitti_recal.json"}
# FCGF with the FPFH-certified configurations applied unchanged (the transfer test, which fails)
LIVE_XFER = {"fcgf3dmatch": "live_budget_compare_ext_fcgf3dmatch.json", "fcgfkitti": "live_budget_compare_ext_fcgfkitti.json"}
PREFIX = {"ratio": "budget", "compat": "budgetc"}
ESTS = {"sc": "sc2", "tr": "turbo"}
ENAME = {"sc": "SC$^2$-PCR", "tr": "TurboReg"}
BUDGETS = [250, 500, 1000, 2000, 4000]
VALS: dict[str, str] = {}

INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
GRAY, BLUE, ORANGE, AQUA, PURPLE, OCHRE = "#9a9890", "#2a78d6", "#eb6834", "#1baf7a", "#8a5cc8", "#c79a2e"
# main-paper figures (validated reference palette): blue = ours (CAB, its ordering), light blue = our ordering with a
# fixed budget, grey = the standard baselines, other slots = alternatives; red only for transferred certificates
BLUE_L, VIOLET, MAGENTA, RED, LIGHT = "#86b6ef", "#6250d6", "#e87ba4", "#e34948", "#d4d2cb"
DARK, AXIS = "#6f6d66", "#8f8d86"  # dark grey fill; spines and tick marks
# figures are drawn at their printed width (7.0 in for full-width, 3.35 in for one column), so these are point sizes
FS_TICK, FS_LABEL, FS_TITLE, FS_LEGEND = 7.5, 8.0, 8.5, 7.5


def setup_style():
    plt.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "mathtext.fontset": "custom", "mathtext.rm": "Arial", "mathtext.it": "Arial:italic", "mathtext.bf": "Arial:bold",
        "pdf.fonttype": 42, "savefig.dpi": 400,
        "axes.edgecolor": AXIS, "axes.linewidth": 0.7, "axes.labelcolor": INK, "axes.titlecolor": INK,
        "axes.titleweight": "bold", "axes.titlesize": FS_TITLE, "axes.labelsize": FS_LABEL,
        "xtick.color": AXIS, "ytick.color": AXIS, "xtick.labelcolor": INK2, "ytick.labelcolor": INK2,
        "xtick.labelsize": FS_TICK, "ytick.labelsize": FS_TICK,
        "xtick.major.width": 0.7, "ytick.major.width": 0.7, "xtick.major.size": 2.5, "ytick.major.size": 2.5,
        "legend.frameon": False, "legend.fontsize": FS_LEGEND, "legend.handletextpad": 0.45,
        "legend.columnspacing": 1.2, "legend.labelcolor": INK,
        "lines.solid_capstyle": "round", "lines.solid_joinstyle": "round"})


def val(key, x, fmt="{:.2f}"):
    s = x if isinstance(x, str) else fmt.format(x)
    if s.startswith("-"):  # typographic minus that works in text and math mode
        s = "\\ensuremath{-}" + s[1:]
    VALS[key] = s
    return s


def num(key):
    return float(VALS[key].replace("\\ensuremath{-}", "-").replace(",", "").replace("+", ""))


def pfmt(p):
    if p >= 0.01:
        return f"{p:.2f}"
    if p >= 1e-3:
        return f"{p:.3f}"
    m, e = f"{p:.1e}".split("e")
    return f"{m}\\times10^{{{int(e)}}}"


def boot_ratio(numr, den, scenes, seed):
    b = A.stratified_bootstrap(lambda i: numr[i].mean() / den[i].mean(), scenes, B=2000, seed=seed)
    return float(numr.mean() / den.mean()), float(np.quantile(b, 0.025)), float(np.quantile(b, 0.975))


def style(ax, fs=FS_TICK):
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=fs, labelcolor=INK2, color=AXIS, length=2.5, width=0.7)
    for sp_ in ("top", "right"):
        ax.spines[sp_].set_visible(False)


def fixed_points(recs, est):
    out = []
    for k in range(5):
        o = A.fixed_stage([B.trajectory_ladder(r, est, (k,)) for r in recs], 0)
        out.append((float(o.s.mean()), float(o.ok.mean())))
    return out


def hull_value(points, t):
    pts = sorted([(0.0, 0.0)] + points)
    h = []
    for p in pts:
        while len(h) >= 2 and (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0]) <= (p[1] - h[-2][1]) * (h[-1][0] - h[-2][0]):
            h.pop()
        h.append(p)
    xs, ys = zip(*h)
    return float(np.interp(t, xs, ys))


TRANSFER = RB / "transfer_fcgf.json"


def available(d):
    log, fam = DS[d]
    if not (LOG_ROOT / f"budgetc_{log}.jsonl").exists():
        return False
    if d in FCGF:
        return TRANSFER.exists() and log in json.loads(TRANSFER.read_text())
    return all((RB / SEL[(fam, o)]).exists() for o in ("ratio", "compat"))


# ============================================================================ CAB results
def cab_results():
    ds = [d for d in DS if available(d)]
    logs = {(d, o): B.load(DS[d][0], PREFIX[o]) for d in ds for o in PREFIX}
    sel = {(fam, o): json.loads((RB / SEL[(fam, o)]).read_text()) for (fam, o) in SEL if (RB / SEL[(fam, o)]).exists()}
    fixed = {(d, o, e): fixed_points(logs[(d, o)], E) for d in ds for o in PREFIX for e, E in ESTS.items()}
    transfer = json.loads(TRANSFER.read_text()) if TRANSFER.exists() else {}

    def entry(d, o, E, tag):
        log, fam = DS[d]
        if d in FCGF and (fam, o) not in sel:  # not yet re-certified: the transfer result
            t = transfer[log][E][o][tag]
            return t, {"rr": t["full_rr"], "s": t["full_s"]}, t["ladder"]
        s_ = sel[(fam, o)][E]
        return s_["test"][log][tag], s_["test"][log]["full"], s_["selected"][tag]["ladder"]

    marg_risks, xfer_risks = {}, {}
    for d in [d for d in ds if d in FCGF]:  # FCGF split sizes: even-indexed test pairs, odd-indexed calibration pool
        val(f"{d}.n.test", f"{len(logs[(d, 'compat')]):,}")
        n_cal = sum(len(B.load(c, "budgetc")) for c in DATASETS_CAL[d])
        val(f"{d}.n.cal", f"{n_cal:,}")
        if d in DATASETS_FIT:
            n_fit = sum(len(B.load(c, "budgetc")) for c in DATASETS_FIT[d])
            val(f"{d}.n.fit", f"{n_fit:,}")
            val(f"{d}.n.cert", f"{n_cal - n_fit:,}")
    for d in ds:
        log, fam = DS[d]
        for o in PREFIX:
            for e, E in ESTS.items():
                for cert, tag in (("group", "mondrian"), ("marg", "marginal")):
                    t, full, ladder = entry(d, o, E, tag)
                    k = f"{e}.{d}.{o}.{cert}"
                    val(k + ".rr", 100 * t["rr"], "{:.1f}")
                    val(k + ".full", 100 * full["rr"], "{:.1f}")
                    val(k + ".loss", 100 * t["delta_rr"], "{:.2f}")
                    val(k + ".ub", 100 * t["ub95"], "{:.2f}")
                    val(k + ".p", pfmt(t["mcnemar_p"]))
                    val(k + ".speed", t["speedup"])
                    val(k + ".speedlo", t["speedup_ci"][0])
                    val(k + ".speedhi", t["speedup_ci"][1])
                    # hardware-independent cost: analytic operation count of every stage run, ordering included
                    val(k + ".ops", t["ops_ratio"])
                    val(k + ".opslo", t["ops_ratio_ci"][0])
                    val(k + ".opshi", t["ops_ratio_ci"][1])
                    val(k + ".risk", 100 * t["risk"], "{:.2f}")
                    val(k + ".nlost", str(int(round(t["risk"] * len(logs[(d, o)])))))
                    if cert == "marg":
                        marg_risks.setdefault(d, []).append(100 * t["risk"])
                    val(k + ".ms", 1e3 * t["s"], "{:,.0f}")
                    val(k + ".fullms", 1e3 * full["s"], "{:,.0f}")
                    val(k + ".ni", "yes" if t["non_inferior"] else "no")
                    val(k + ".ladder", ladder)
                    val(k + ".frontier", 100 * (t["rr"] - hull_value(fixed[(d, o, e)], t["s"])), "{:+.1f}")
                    if d in FCGF and log in transfer:  # transfer test: FPFH-certified configuration applied unchanged
                        x = transfer[log][E][o][tag]
                        kx = f"{e}.{d}.{o}.{cert}.xfer"
                        val(kx + ".risk", 100 * x["risk"], "{:.2f}")
                        val(kx + ".loss", 100 * x["delta_rr"], "{:.2f}")
                        val(kx + ".ub", 100 * x["ub95"], "{:.2f}")
                        val(kx + ".speed", x["speedup"])
                        if cert == "group":
                            xfer_risks.setdefault(d, []).append(100 * x["risk"])
                for i in range(5):
                    val(f"{e}.{d}.{o}.fix{i}.rr", 100 * fixed[(d, o, e)][i][1], "{:.1f}")
                    val(f"{e}.{d}.{o}.fix{i}.ms", 1e3 * fixed[(d, o, e)][i][0], "{:,.0f}")
    for d, rs in xfer_risks.items():  # FCGF transfer, group-conditional, both estimators and orders
        val(f"{d}.xfer.risk.min", min(rs), "{:.1f}")
        val(f"{d}.xfer.risk.max", max(rs), "{:.1f}")
    for d, rs in marg_risks.items():  # marginal certificates, both estimators and orders
        val(f"{d}.marg.risk.min", min(rs), "{:.2f}")
        val(f"{d}.marg.risk.max", max(rs), "{:.2f}")
    # live (group-conditional configurations; full budget and both orderings on the same pairs)
    agrees, stalls = [], []
    for fam, fname, lk in [(f, n, "live") for f, n in LIVE.items()] + [(f, n, "xlive") for f, n in LIVE_XFER.items()]:
        path = RB / fname
        if not path.exists():
            continue
        rows = json.loads(path.read_text())
        if lk == "live":  # pairs re-timed after a system stall (scripts/retime_stalls.py)
            stalls += [max(r["stalled"].values()) for r in rows if "stalled" in r]
        for d in [d for d in ds if DS[d][1] == fam]:
            log = DS[d][0]
            for e, E in ESTS.items():
                rs = [r for r in rows if r["est"] == E and r["subset"] == log]
                if not rs:
                    continue
                sc = np.array([r["scene"] for r in rs])
                tf = np.array([r["full"]["s"] for r in rs])
                val(f"{e}.{d}.{lk}.n", str(len(rs)))
                val(f"{e}.{d}.{lk}.fullms", 1e3 * tf.mean(), "{:,.0f}")
                val(f"{e}.{d}.{lk}.fullrr", 100 * np.mean([r["full"]["ok"] for r in rs]), "{:.0f}")
                for o, pf in PREFIX.items():
                    ta = np.array([r[pf]["s"] for r in rs])
                    sp, lo, hi = boot_ratio(tf, ta, sc, 1)
                    k = f"{e}.{d}.{o}.{lk}"
                    val(k + ".speed", sp)
                    val(k + ".speedlo", lo)
                    val(k + ".speedhi", hi)
                    val(k + ".ms", 1e3 * ta.mean(), "{:,.0f}")
                    val(k + ".rr", 100 * np.mean([r[pf]["ok"] for r in rs]), "{:.0f}")
                    val(k + ".lost", str(sum(r["full"]["ok"] and not r[pf]["ok"] for r in rs)))
                    agrees.append(np.mean([r[pf]["stop"] == r[pf]["offline_stop"] for r in rs]))
                tr_, tc_ = np.array([r["budget"]["s"] for r in rs]), np.array([r["budgetc"]["s"] for r in rs])
                sp, lo, hi = boot_ratio(tr_, tc_, sc, 2)
                val(f"{e}.{d}.{lk}.compatvsratio", sp)
                val(f"{e}.{d}.{lk}.compatvsratiolo", lo)
                val(f"{e}.{d}.{lk}.compatvsratiohi", hi)
    if agrees:
        val("live.agree.min", 100 * min(agrees), "{:.0f}")
    eq_path = RB / "live_equal_time_3DMatch.json"
    if eq_path.exists():
        stalls += [max(r["stalled"].values()) for r in json.loads(eq_path.read_text()) if "stalled" in r]
    val("live.retimed", str(len(stalls)))
    val("live.stall.s", max(stalls, default=0.0), "{:,.0f}")
    # worst live speed-up of CAB (compat order, group-conditional): its overhead where there is nothing to save
    worst = min(((num(f"{e}.{d}.compat.live.speed"), e, d) for d in ds for e in ESTS
                 if f"{e}.{d}.compat.live.speed" in VALS), default=None)
    if worst is not None:
        val("cab.live.min", worst[0])
        val("cab.live.min.where", f"{ENAME[worst[1]]} on {'FCGF ' if worst[2] in FCGF else ''}{DNAME[worst[2]]}")

    for (fam, o), fname in SEL_RCERT.items():  # FCGF, thresholds-only re-certification (supp)
        if not (RB / fname).exists():
            continue
        rc = json.loads((RB / fname).read_text())
        for d in [d for d in ds if DS[d][1] == fam]:
            for e, E in ESTS.items():
                t = rc[E]["test"][DS[d][0]]["mondrian"]
                k = f"{e}.{d}.{o}.group.rcert"
                val(k + ".speed", t["speedup"])
                val(k + ".risk", 100 * t["risk"], "{:.2f}")
                val(k + ".ladder", rc[E]["selected"]["mondrian"]["ladder"])

    # supp: FCGF under three protocols (compat order, group-conditional): FPFH controller and thresholds applied
    # unchanged (transfer); FPFH controller with thresholds re-certified on FCGF; controller re-fitted on FCGF and
    # certified on a disjoint part of the pool (3DMatch/3DLoMatch only; the KITTI pool is too small to split)
    L = []
    for d in [d for d in ("fm", "flo", "fki") if d in ds]:
        for e in ESTS:
            k, kx = f"{e}.{d}.compat.group", f"{e}.{d}.compat.group.xfer"
            if kx + ".risk" not in VALS:
                continue
            refit = d in DATASETS_FIT
            thr = (f"{VALS[k + '.rcert.speed']}\\X" if refit and k + ".rcert.speed" in VALS
                   else (f"{VALS[k + '.speed']}\\X" if not refit else "--"))
            cells = [f"{ENAME[e]}, {DNAME[d]}", VALS[kx + ".risk"], VALS[kx + ".speed"] + "\\X", thr]
            cells += ([VALS[k + ".risk"], f"{VALS[k + '.loss']} [{VALS[k + '.ub']}]", VALS[k + ".speed"] + "\\X"]
                      if refit else ["--", "--", "--"])
            L.append(" & ".join(cells) + " \\\\")
    (TAB / "supp_fcgf.tex").write_text("\n".join(L) + "\n", encoding="utf-8")

    # ---- Table 1: main results (group-conditional certificates)
    L = []
    blocks = [("FPFH correspondences", ["m", "lo", "ki"]),
              ("FCGF correspondences (controller fitted and certified on held-out FCGF pairs)", ["fm", "flo", "fki"])]
    for title, cols in blocks:
      if not any(d in ds for d in cols):
        continue
      L.append(f"\\multicolumn{{16}}{{@{{}}l}}{{\\textbf{{{title}}}}} \\\\")
      for e in ESTS:
        L.append(f"\\multicolumn{{16}}{{@{{}}l}}{{\\textit{{{ENAME[e]}}}}} \\\\")
        for lab, o in (("Full budget (standard)", None), ("\\method, ratio order", "ratio"), ("\\textbf{\\method (ours)}", "compat")):
            cells = [lab]
            for d in cols:
                if d not in ds:
                    cells += ["--"] * 5
                    continue
                if o is None:
                    cells += [VALS[f"{e}.{d}.ratio.group.full"], "--", "1.00\\X", "1.00\\X", "--"]
                    continue
                k = f"{e}.{d}.{o}.group"
                ni = "\\cmark" if VALS[k + ".ni"] == "yes" else "\\xmark"
                if VALS[k + ".ladder"] == "full":  # nothing cheaper certifiable: CAB is the full budget itself
                    lv = "1.00$\\times^\\dagger$"
                elif f"{e}.{d}.{o}.live.speed" in VALS:
                    lv = f"{VALS[f'{e}.{d}.{o}.live.speed']}\\X"
                else:
                    lv = f"{VALS[k + '.speed']}$\\times^*$"
                rr =f"\\textbf{{{VALS[k + '.rr']}}}" if o == "compat" else VALS[k + ".rr"]
                lvb = f"\\textbf{{{lv}}}" if o == "compat" else lv
                ops = f"{VALS[k + '.ops']}\\X"
                cells += [rr, f"{VALS[k + '.loss']} [{VALS[k + '.ub']}] {ni}", lvb,
                          f"\\textbf{{{ops}}}" if o == "compat" else ops, VALS[k + ".risk"]]
            L.append(" & ".join(cells) + " \\\\")
      L.append("\\midrule")
    L[-1] = "\\bottomrule"
    (TAB / "main_results.tex").write_text("\n".join(L) + "\n", encoding="utf-8")

    # ---- supplementary: all certified configurations
    L = []
    for d in ds:
        for e in ESTS:
            for o, oname in (("ratio", "ratio"), ("compat", "compat.")):
                for cert, cname in (("marg", "marginal"), ("group", "group")):
                    k = f"{e}.{d}.{o}.{cert}"
                    ni = "\\cmark" if VALS[k + ".ni"] == "yes" else "\\xmark"
                    lv = f"{VALS[f'{e}.{d}.{o}.live.speed']}\\X" if cert == "group" and f"{e}.{d}.{o}.live.speed" in VALS else "--"
                    L.append(f"{dlabel(d)} & {ENAME[e]} & {oname} & {cname} & \\texttt{{{VALS[k + '.ladder']}}} & "
                             f"{VALS[k + '.rr']} & {VALS[k + '.loss']} [{VALS[k + '.ub']}] {ni} & {VALS[k + '.speed']}\\X & "
                             f"{lv} & {VALS[k + '.risk']} & {VALS[k + '.frontier']} \\\\")
        L.append("\\midrule")
    L[-1] = ""
    (TAB / "supp_full_results.tex").write_text("\n".join(L) + "\n", encoding="utf-8")

    # ---- supplementary: fixed budgets
    L = []
    for e in ESTS:
        for o, oname in (("ratio", "ratio"), ("compat", "compat.")):
            cells = [ENAME[e], oname]
            for d in ("m", "lo", "ki"):
                cells += [VALS.get(f"{e}.{d}.{o}.fix{i}.rr", "--") for i in range(5)]
            L.append(" & ".join(cells) + " \\\\")
    (TAB / "supp_fixed_budgets.tex").write_text("\n".join(L) + "\n", encoding="utf-8")

    fig_tradeoff_all(ds, fixed)
    return ds, logs, fixed


def fig_tradeoff_all(ds, fixed):
    """Supplementary figure: recall vs relative time of every fixed budget, with CAB's certified operating points
    (colour: ordering; filled diamond: group-conditional certificate; open square: marginal certificate)."""
    dsf = [d for d in ds if d not in FCGF]
    fig, axes = plt.subplots(len(ESTS), len(dsf), figsize=(7.0, 2.05 * len(ESTS) + 0.45), squeeze=False)
    for r, e in enumerate(ESTS):
        for c, d in enumerate(dsf):
            ax = axes[r, c]
            for o, col, name in (("ratio", GRAY, "ratio order"), ("compat", BLUE, "our ordering")):
                pts = fixed[(d, o, e)]
                ax.plot([p[0] / pts[-1][0] for p in pts], [100 * p[1] for p in pts], "-o", color=col, lw=1.5, ms=3.6,
                        mec="white", mew=0.6, label=f"fixed budgets, {name}", zorder=2)
            for cert, mk, cname in (("group", "D", "group-conditional"), ("marg", "s", "marginal")):
                for o, col, name in (("ratio", DARK, "ratio order"), ("compat", BLUE, "our ordering")):
                    k = f"{e}.{d}.{o}.{cert}"
                    ax.plot([1.0 / num(k + ".speed")], [num(k + ".rr")], mk, ls="none", ms=6.0 if mk == "D" else 5.6,
                            color=col, mfc=col if cert == "group" else "white", mec="white" if cert == "group" else col,
                            mew=0.6 if cert == "group" else 1.3, zorder=5 if cert == "group" else 4,
                            label=f"CAB, {name}, {cname}")
            ax.set_xlim(0, 1.04)
            ax.set_title(f"{ENAME[e].replace('$^2$', '²')}, {DNAME[d]}", loc="left")
            style(ax)
            if r == len(ESTS) - 1:
                ax.set_xlabel("time / full-budget time")
            if c == 0:
                ax.set_ylabel("recall (%)")
    fig.tight_layout(rect=(0, 0.085, 1, 1), w_pad=1.0, h_pad=0.8)
    # legend columns: fixed budgets | CAB, group-conditional | CAB, marginal
    fig.legend(*axes[0, 0].get_legend_handles_labels(), loc="lower center", ncol=3, bbox_to_anchor=(0.5, 0.0),
               handlelength=1.8)
    fig.savefig(FIG / "tradeoff_all.pdf", facecolor="white")
    plt.close(fig)


# ============================================================================ which pairs / headroom
def anchors_and_headroom(ds, logs):
    edges = [(0, 1, "0"), (1, 5, "1--4"), (5, 20, "5--19"), (20, 50, "20--49"), (50, 10 ** 6, "$\\geq$50")]

    def pairs(d):
        ratio = {r["pair_id"]: r for r in logs[(d, "ratio")]}
        return [(r["anchors_true"], bool(ratio[r["pair_id"]]["sc2"][4]["ok15"]), bool(ratio[r["pair_id"]]["sc2"][0]["ok15"]),
                 bool(r["sc2"][0]["ok15"])) for r in logs[(d, "compat")]]

    groups = {"indoor": [p for d in ("m", "lo") if d in ds for p in pairs(d)]}
    if "ki" in ds:
        groups["KITTI"] = pairs("ki")
    L, bins = [], {}
    for name, P in groups.items():
        rows = []
        for lo, hi, lab in edges:
            m = [x for x in P if lo <= x[0] < hi]
            if not m:
                continue
            arr = np.array([[f, r0, c0] for _, f, r0, c0 in m], float)
            rows.append((lab, len(m), 100 * arr[:, 0].mean(), 100 * arr[:, 1].mean(), 100 * arr[:, 2].mean()))
        bins[name] = rows
        dname = "3DM+3DLoM" if name == "indoor" else "KITTI"
        for i, (lab, n, f, r0, c0) in enumerate(rows):
            L.append(f"{dname if i == 0 else ''} & {lab} & {n:,} & {f:.1f} & {r0:.1f} & \\textbf{{{c0:.1f}}} & {c0 - r0:+.1f} \\\\")
        L.append("\\midrule")
    L[-1] = ""
    (TAB / "supp_anchors.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
    mid = [x for x in bins["indoor"] if x[0] in ("5--19", "20--49")]
    val("anch.test.mid.gain.lo", min(c - r for _, _, _, r, c in mid), "{:.1f}")
    val("anch.test.mid.gain.hi", max(c - r for _, _, _, r, c in mid), "{:.1f}")
    val("anch.test.n", f"{len(groups['indoor']):,}")
    for d in ds:
        a = np.array([r["anchors_true"] for r in logs[(d, "compat")]])
        val(f"anch.{d}.zero", 100 * np.mean(a == 0), "{:.0f}")
        val(f"anch.{d}.lt5", 100 * np.mean(a < 5), "{:.0f}")
        val(f"anch.{d}.ge50", 100 * np.mean(a >= 50), "{:.0f}")
        val(f"anch.{d}.mean", a.mean(), "{:.1f}")

    # figure: (a) success at N=250 by true anchors (indoor test sets pooled); (b) difficulty mix of every test set
    labels = [b[2].replace("--", "–").replace("$\\geq$", "≥") for b in edges]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(3.35, 3.05), gridspec_kw={"height_ratios": [1.75, 1]})
    x = np.arange(len(edges))
    rows = bins["indoor"]
    w = 0.27
    # 5-49 true anchors: where the ordering rescues the cheap budget (blue band, the blue segment of (b))
    mid = [i for i, b in enumerate(edges) if 5 <= b[0] < 50]
    ax1.axvspan(min(mid) - 0.5, max(mid) + 0.5, color=BLUE, alpha=0.08, lw=0, zorder=0)
    ax1.text((min(mid) + max(mid)) / 2, 104, "the ordering helps", ha="center", va="bottom", fontsize=FS_LEGEND,
             color=INK, style="italic")
    for i, (col, key, lab) in enumerate(((GRAY, 3, "ratio order, $N$ = 250"), (BLUE, 4, "our ordering, $N$ = 250"),
                                         (INK, 2, "full budget"))):
        ax1.bar(x + (i - 1) * w, [r[key] for r in rows], width=w * 0.92, color=col, label=lab, edgecolor="white",
                linewidth=0.6, zorder=2)
    ax1.set_xticks(x, labels)
    ax1.set_xlim(-0.55, len(edges) - 0.45)
    ax1.set_ylim(0, 115)
    ax1.set_yticks([0, 25, 50, 75, 100])
    ax1.set_ylabel("SC²-PCR success (%)")
    ax1.set_xlabel("true correspondences among the 100 anchors")
    ax1.set_title("(a) Success by true anchors", loc="left", fontsize=FS_LABEL)
    ax1.legend(loc="upper left", bbox_to_anchor=(0.0, 0.93), handlelength=1.0, labelspacing=0.3, borderaxespad=0.2)
    # (b) composition of every test set: fewer than 5 true anchors (a cheap budget cannot be rescued),
    # 5-49 (the ordering helps; blue, as the band in (a)) and 50 or more (already easy)
    groups = [("< 5 true anchors", 0, 5, DARK), ("5–49", 5, 50, BLUE), ("≥ 50", 50, 10 ** 6, LIGHT)]
    sets_ = [d for d in ("m", "lo", "ki") if d in ds]
    for j, d in enumerate(sets_):
        a = np.array([r["anchors_true"] for r in logs[(d, "compat")]])
        left = 0.0
        for gname, lo, hi, col in groups:
            share = 100 * np.mean((a >= lo) & (a < hi))
            ax2.barh(j, share, left=left, height=0.66, color=col, edgecolor="white", linewidth=1.0,
                     label=gname if j == 0 else None)
            if share >= 8:
                ax2.text(left + share / 2, j, f"{share:.0f}", ha="center", va="center", fontsize=FS_TICK,
                         color="white" if col != LIGHT else INK, weight="bold")
            left += share
    ax2.set_yticks(range(len(sets_)), [DNAME[d] for d in sets_])
    ax2.set_ylim(len(sets_) - 0.5, -0.5)
    ax2.set_xlim(0, 100)
    ax2.set_xticks([0, 25, 50, 75, 100])
    ax2.set_title("(b) Share of test pairs (%)", loc="left", fontsize=FS_LABEL, pad=13)
    ax2.legend(loc="lower left", bbox_to_anchor=(0.0, 0.98), ncol=3, handlelength=1.0, borderaxespad=0,
               columnspacing=1.0)
    for ax in (ax1, ax2):
        style(ax)
    ax1.grid(False, axis="x")
    ax2.grid(False, axis="y")
    ax2.tick_params(axis="y", length=0)
    fig.tight_layout(pad=0.3, h_pad=0.9)
    fig.savefig(FIG / "anchors.pdf", facecolor="white")
    plt.close(fig)

    # headroom: CAB (group-cond.) vs two oracles on CAB's own (selected) ladder, both orders:
    # accept-only (stops at the first correct stage, runs failures to the end) and full (also stops
    # unsolvable pairs after the first stage). Table: FPFH sets; FCGF keys only.
    L = []
    for d in ds:
        for e, E in ESTS.items():
            cells = [f"{ENAME[e]}, {dlabel(d)}"]
            for o in PREFIX:
                recs = logs[(d, o)]
                ladder = B.LADDERS_EXT[VALS[f"{e}.{d}.{o}.group.ladder"]]
                tr = [B.trajectory_ladder(r, E, ladder) for r in recs]
                full = np.array([B.trajectory_ladder(r, E, (4,))[-1]["s"] for r in recs])
                first_ok = [next((st["stage"] for st in t if st["ok"]), None) for t in tr]
                solved = np.array([k is not None for k in first_ok])
                orc = np.array([t[k]["s"] if k is not None else t[0]["s"] for t, k in zip(tr, first_ok)])
                acc = np.array([t[k]["s"] if k is not None else t[-1]["s"] for t, k in zip(tr, first_ok)])
                acc_sp, orc_sp = full.mean() / acc.mean(), full.mean() / orc.mean()
                val(f"{e}.{d}.{o}.acc", acc_sp)
                val(f"{e}.{d}.{o}.orc", orc_sp)
                val(f"{e}.{d}.{o}.margfrac", 100 * num(f"{e}.{d}.{o}.marg.speed") / acc_sp, "{:.0f}")
                val(f"{e}.{d}.{o}.groupfrac", 100 * num(f"{e}.{d}.{o}.group.speed") / acc_sp, "{:.0f}")
                cells += [VALS[f"{e}.{d}.{o}.group.speed"], f"{acc_sp:.2f}", f"{orc_sp:.2f}"]
                if o == "ratio":
                    val(f"{e}.{d}.unsolv.pairs", 100 * (1 - solved.mean()), "{:.0f}")
                    val(f"{e}.{d}.unsolv.time", 100 * full[~solved].sum() / full.sum(), "{:.0f}")
            cells += [VALS[f"{e}.{d}.unsolv.pairs"], VALS[f"{e}.{d}.unsolv.time"]]
            if d not in FCGF:
                L.append(" & ".join(cells) + " \\\\")
    # when does CAB pay off: per test set, success of the cheapest budget, unsolvable pairs, speed-up and risk
    # (each cell: SC2-PCR / TurboReg; CAB = compat order, group-conditional; live speed-up where measured)
    P = []
    for d in [d for d in ("m", "lo", "ki", "fm", "flo", "fki") if d in ds]:
        def both(fmt):
            return " / ".join(fmt(e) for e in ESTS)

        def speed(e):
            k = f"{e}.{d}.compat"
            if VALS[k + ".group.ladder"] == "full":
                return "1.00$^\\dagger$"
            return VALS.get(k + ".live.speed", VALS[k + ".group.speed"] + "$^*$")
        P.append(" & ".join([dlabel(d), both(lambda e: VALS[f"{e}.{d}.compat.fix0.rr"]),
                             both(lambda e: VALS[f"{e}.{d}.unsolv.pairs"]), both(speed),
                             both(lambda e: VALS[f"{e}.{d}.compat.group.risk"])]) + " \\\\")
    (TAB / "payoff.tex").write_text("\n".join(P) + "\n", encoding="utf-8")
    for d in ds:  # range over the two estimators, collapsed when equal
        a, b = sorted(int(VALS[f"{e}.{d}.unsolv.time"]) for e in ESTS)
        val(f"{d}.unsolv.time.range", f"{a}" if a == b else f"{a}--{b}")
    (TAB / "headroom.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


# ============================================================================ equal-time comparison
def equal_time(logs):
    """Cheaper variants of the estimators vs CAB at equal time (3DMatch: live time; 3DLoMatch: offline, supp)."""
    variants = [("rand", "Uniform sampling"), ("fm1", "FastMAC-style, 1st-order graph"),
                ("fm2", "FastMAC-style, 2nd-order graph"), ("ratio", "Fixed budget, ratio order"),
                ("compat", "Fixed budget, compat.\\ order")]
    lo_rows = {}
    for subset, d in (("3DMatch", "m"), ("3DLoMatch", "lo")):
        path = LOG_ROOT / f"eqtime_{subset}.jsonl"
        if not path.exists() or (d, "compat") not in logs:
            continue
        eq = {r["pair_id"]: r for r in map(json.loads, open(path))}
        index = {r["pair_id"]: i for i, r in enumerate(logs[(d, "ratio")])}
        # keep the schedule: every 2nd pair (rand, fm1), every 4th (fm2), every 8th (seeds, k1)
        from acpr.data import load_pairs
        idx_of = {p.pair_id: p.index for p in load_pairs(subset)}
        ids = [pid for pid in eq if idx_of[pid] % 2 == 0]
        val(f"eq.n.{d}", f"{len(ids):,}")
        ratio_logs = {r["pair_id"]: r for r in logs[(d, "ratio")]}
        compat_logs = {r["pair_id"]: r for r in logs[(d, "compat")]}
        for e, E in ESTS.items():
            # CAB outcome per pair (compat order, group-conditional, selected on validation)
            import select_ladder as S
            sel = json.loads((RB / SEL[("3dmatch", "compat")]).read_text())[E]["selected"]["mondrian"]
            ladder = B.LADDERS_EXT[sel["ladder"]]
            tr, mdps = S.build({"train": B.load("train", "budgetc"), "val": B.load("val", "budgetc"),
                                subset: logs[(d, "compat")]}, E, ladder)
            o = S.policy_outcome(tr[subset], mdps, "mondrian", sel["param"])
            cab_ok = {r["pair_id"]: bool(ok) for r, ok in zip(logs[(d, "compat")], o.ok)}
            cab_rel = {r["pair_id"]: s / B.trajectory_ladder(r, E, (4,))[-1]["s"] for r, s in zip(logs[(d, "compat")], o.s)}
            full_ok = {pid: bool(ratio_logs[pid][E][4]["ok15"]) for pid in ids}
            res = {}
            for v, _ in variants:
                curve = []
                for i, b in enumerate(BUDGETS[:4]):
                    if v in ("ratio", "compat"):
                        src = ratio_logs if v == "ratio" else compat_logs
                        sub = ids
                        oks = [bool(src[pid][E][i]["ok15"]) for pid in sub]
                    else:
                        sub = [pid for pid in ids if v in eq[pid] and (v != "fm2" or idx_of[pid] % 4 == 0)]
                        oks = [eq[pid][v][str(b)][E]["ok15"] for pid in sub]
                    curve.append((b, 100 * np.mean(oks), sub))
                res[v] = curve
            res["cheap"] = []
            key, params = ("seeds", ("0.025", "0.01")) if e == "sc" else ("k1", ("500", "250"))
            sub8 = [pid for pid in ids if key in eq[pid] and idx_of[pid] % 8 == 0]
            for prm in params:
                res["cheap"].append((prm, 100 * np.mean([eq[pid][key][prm]["ok15"] for pid in sub8]), sub8))
            for v, curve in res.items():
                for b, rr, sub in curve:
                    val(f"eq.{e}.{d}.{v}.{b}.rr", rr, "{:.1f}")
                    val(f"eq.{e}.{d}.{v}.{b}.cab", 100 * np.mean([cab_ok[pid] for pid in sub]), "{:.1f}")
                    val(f"eq.{e}.{d}.{v}.{b}.fullrr", 100 * np.mean([full_ok[pid] if pid in full_ok else ratio_logs[pid][E][4]["ok15"] for pid in sub]), "{:.1f}")
            val(f"eq.{e}.{d}.cab.rr", 100 * np.mean([cab_ok[pid] for pid in ids]), "{:.1f}")
            val(f"eq.{e}.{d}.full.rr", 100 * np.mean([full_ok[pid] for pid in ids]), "{:.1f}")
            val(f"eq.{e}.{d}.cab.rel", np.mean([cab_rel[pid] for pid in ids]), "{:.2f}")
            # the strongest cheap baseline: uniform sampling of 2,000 correspondences, paired with CAB (McNemar)
            from scipy.stats import binomtest
            a = np.array([cab_ok[p] for p in ids])
            u = np.array([bool(eq[p]["rand"]["2000"][E]["ok15"]) for p in ids])
            n10, n01 = int((a & ~u).sum()), int((~a & u).sum())
            val(f"eq.{e}.{d}.rand2000.rr", 100 * u.mean(), "{:.1f}")
            val(f"eq.{e}.{d}.rand2000.p", pfmt(binomtest(n10, n10 + n01, 0.5).pvalue if n10 + n01 else 1.0))
            val(f"eq.{e}.{d}.rand2000.gap", 100 * (a.mean() - u.mean()), "{:+.1f}")
            val(f"eq.{e}.{d}.rand2000.loss", 100 * (np.mean([full_ok[p] for p in ids]) - u.mean()), "{:.1f}")
            fo = np.array([full_ok[p] for p in ids])
            val(f"eq.{e}.{d}.rand2000.risk", 100 * np.mean(fo & ~u), "{:.2f}")
            if d == "lo":  # offline table (supp): relative time = ratio of summed times on the variant's own pairs
                full_s = {pid: B.trajectory_ladder(ratio_logs[pid], E, (4,))[-1]["s"] for pid in ids}
                cab_s = {r["pair_id"]: s for r, s in zip(logs[(d, "compat")], o.s)}
                # rows: (group, label, relative time, recall minus the full budget's on the same pairs, pp)
                rows = lo_rows.setdefault(e, [])
                fr = lambda sub: 100 * np.mean([full_ok[p] for p in sub])  # noqa: E731
                rows.append((None, "\\method (ours)", sum(cab_s[p] for p in ids) / sum(full_s.values()),
                             100 * np.mean([cab_ok[p] for p in ids]) - fr(ids)))
                for v, name in variants:
                    for i, b in enumerate(BUDGETS[:4]):
                        sub = res[v][i][2]
                        if v in ("ratio", "compat"):
                            src = ratio_logs if v == "ratio" else compat_logs
                            t = sum(B.trajectory_ladder(src[p], E, (i,))[-1]["s"] for p in sub)
                        else:
                            sig = {"rand": None, "fm1": "t_fm1", "fm2": "t_fm2"}[v]
                            t = sum(eq[p][v][str(b)][E]["s"] + (eq[p][sig] if sig else 0.0) for p in sub)
                        rows.append((name, f"$N{{=}}{b:,}$".replace(",", "{,}"), t / sum(full_s[p] for p in sub),
                                     res[v][i][1] - fr(sub)))
                for prm, rr, sub in res["cheap"]:
                    t = sum(eq[p][key][prm]["s"] for p in sub)
                    rows.append(("Fewer seeds (\\SCP) / cliques (TurboReg)", "(a)" if prm == params[0] else "(b)",
                                 t / sum(full_s[p] for p in sub), rr - fr(sub)))
                val(f"eq.{e}.lo.fullrr", fr(ids), "{:.1f}")
    for e, rows in lo_rows.items():  # smallest recall loss of any cheaper variant that saves >= 5 % of the time
        cheaper = [r for r in rows if r[0] is not None and r[2] <= 0.95]
        val(f"eq.{e}.lo.minloss", -max(r[3] for r in cheaper), "{:.1f}")
        val(f"eq.{e}.lo.cab.trel", rows[0][2], "{:.2f}")
    if len(lo_rows) == 2:
        L, group = [], None
        for (g, name, ts, ds_), (_, _, tt, dt) in zip(lo_rows["sc"], lo_rows["tr"]):
            if g is not None and g != group:
                L.append(f"\\multicolumn{{5}}{{@{{}}l}}{{\\textit{{{g}}}}} \\\\")
            group = g
            cells = [f"{ts:.2f}", f"{ds_:+.1f}", f"{tt:.2f}", f"{dt:+.1f}"]
            cells = [c.replace("-", "\\ensuremath{-}") for c in cells]
            L.append(("\\quad " if g else "") + " & ".join([name] + cells) + " \\\\")
            if g is None:
                L.append("\\midrule")
        (TAB / "supp_equal_time_lo.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
    _equal_time_live(variants)


def controller_calibration():
    """Why FPFH certificates fail on FCGF: the FPFH-fitted controller is overconfident on FCGF. Share of
    first-stage answers with p_now >= 0.9 and how many of them are correct (compat order, CAB's ladder)."""
    import select_ladder as S
    sel = json.loads((RB / SEL[("3dmatch", "compat")]).read_text())
    sets_ = {"val": "val", "m": "3DMatch", "fm": "fcgf_3DMatch", "flo": "fcgf_3DLoMatch"}
    for e, E in ESTS.items():
        ladder = B.LADDERS_EXT[sel[E]["selected"]["mondrian"]["ladder"]]
        logs = {"train": B.load("train", "budgetc"), **{k: B.load(v, "budgetc") for k, v in sets_.items() if k != "val"},
                "val": B.load("val", "budgetc")}
        if not all(logs.values()):
            return
        tr, _ = S.build(logs, E, ladder)
        for k in sets_:
            p = np.array([t[0]["p_now"] for t in tr[k]])
            ok = np.array([t[0]["ok"] for t in tr[k]])
            hi = p >= 0.9
            val(f"conf.{e}.{k}.share", 100 * hi.mean(), "{:.0f}")
            val(f"conf.{e}.{k}.correct", 100 * ok[hi].mean(), "{:.0f}")
    for k in sets_:  # range over the two estimators, collapsed when equal
        a, b = sorted(int(VALS[f"conf.{e}.{k}.correct"]) for e in ESTS)
        val(f"conf.{k}.correct", f"{a}" if a == b else f"{a}--{b}")


def risk_ledger(ax):
    """Realized test risk (pairs the full budget registers but the configuration loses) on every test set, for
    CAB with group-conditional certificates against the alternatives that carry no valid guarantee there."""
    sets_ = [d for d in ("m", "lo", "ki", "fm", "flo", "fki") if f"sc.{d}.compat.group.risk" in VALS]
    series = [  # (label, key pattern, color, marker, filled)
        ("CAB, group-cond. (ours)", "{e}.{d}.compat.group.risk", BLUE, "o", True),
        ("CAB, marginal cert.", "{e}.{d}.compat.marg.risk", BLUE, "o", False),
        ("uniform sampling", "eq.{e}.{d}.rand2000.risk", ORANGE, "^", True),
        ("FPFH cert. on FCGF", "{e}.{d}.compat.group.xfer.risk", RED, "X", True),
    ]
    cab = [num(f"{e}.{d}.compat.group.risk") for d in sets_ for e in ESTS]
    val("cab.risk.max", max(cab), "{:.2f}")
    val("cab.risk.n", str(len(cab)))
    # horizontal dot plot: one row per test set (upper dot SC2-PCR, lower TurboReg), risk on a symlog axis
    off = {"sc": -0.18, "tr": 0.18}
    XMAX = 14
    ax.axvspan(1.0, XMAX, color=RED, alpha=0.08, lw=0, zorder=0)
    ax.axvline(1.0, color=INK, lw=0.9, ls=(0, (3, 2)), zorder=2)
    for si, (label, pat, col, mk, filled) in enumerate(series):
        xs, ys = [], []
        for i, d in enumerate(sets_):
            for e in ESTS:
                k = pat.format(e=e, d=d)
                if k in VALS:
                    xs.append(num(k))
                    ys.append(i + off[e])
        if xs:
            ax.plot(xs, ys, mk, ls="none", ms={"^": 6.2, "X": 6.0}.get(mk, 6.6 if filled else 5.8), color=col,
                    mfc=col if filled else "white", mec=col if mk == "X" or not filled else "white",
                    mew={"X": 0.3}.get(mk, 0.6 if filled else 1.3), label=label,
                    zorder=6 if si == 0 else 4, clip_on=False)
    for i in range(len(sets_) - 1):
        ax.axhline(i + 0.5, color=GRID, lw=0.6, zorder=1)
    for name, rows_ in (("FPFH", [i for i, d in enumerate(sets_) if d not in FCGF]),
                        ("FCGF", [i for i, d in enumerate(sets_) if d in FCGF])):
        if rows_:  # descriptor of each block of rows, left of the row labels
            ax.annotate(name, xy=(0, np.mean(rows_)), xycoords=("axes fraction", "data"), xytext=(-49, 0),
                        textcoords="offset points", rotation=90, ha="center", va="center", fontsize=FS_LABEL,
                        weight="bold", color=INK)
            if name == "FCGF":
                ax.axhline(min(rows_) - 0.5, color=AXIS, lw=0.8, zorder=1)
    ax.text(0.93, -0.8, "level ε = 1 %", fontsize=FS_LEGEND, color=INK, ha="right", va="center")
    ax.text(1.12, -0.8, "exceeds ε", fontsize=FS_LEGEND, color=INK, ha="left", va="center", style="italic")
    ax.set_xscale("symlog", linthresh=1.0, linscale=1.0)
    ax.set_xlim(-0.05, XMAX)
    ax.set_xticks([0, 0.5, 1, 2, 5, 10])
    ax.set_xticklabels(["0", "0.5", "1", "2", "5", "10"])
    ax.set_yticks(range(len(sets_)), [DNAME[d] for d in sets_])
    ax.set_ylim(len(sets_) - 0.5, -1.15)  # band above the rows for the level labels
    ax.set_xlabel("pairs lost vs. the full budget (%)")
    ax.set_title("(c) Risk on every test set", loc="left")
    style(ax)
    ax.grid(False, axis="y")
    ax.tick_params(axis="y", length=0)
    return ax.get_legend_handles_labels()


def _equal_time_live(variants):
    path = RB / "live_equal_time_3DMatch.json"
    if not path.exists():
        return
    rows = json.loads(path.read_text())
    L = []
    # layout in inches: (a), (b) share the recall axis; (c) leaves room for its row and descriptor labels;
    # the band below the panels holds the two legends
    W, H, BOT, HGT = 7.0, 2.94, 1.12, 1.58
    fig = plt.figure(figsize=(W, H))
    axes = [fig.add_axes((l / W, BOT / H, w / W, HGT / H)) for l, w in ((0.44, 1.93), (2.47, 1.93), (5.2, 1.76))]
    colors = {"rand": ORANGE, "fm1": VIOLET, "fm2": MAGENTA, "ratio": GRAY, "compat": BLUE_L, "cheap": INK2}
    legend_name = {"rand": "uniform sampling", "fm1": "FastMAC-style, 1st order",
                   "fm2": "FastMAC-style, 2nd order", "ratio": "fixed budget, ratio order",
                   "compat": "fixed budget, our ordering", "cheap": "fewer seeds / cliques"}
    for ax, (e, E), letter in zip(axes[:2], ESTS.items(), "ab"):
        rs = [r for r in rows if r["est"] == E]
        t = {k: 1e3 * np.mean([r[k] for r in rs]) for k in rs[0] if isinstance(rs[0][k], float)}
        val(f"eq.{e}.live.n", str(len(rs)))
        val(f"eq.{e}.full.ms", t["full"], "{:,.0f}")
        val(f"eq.{e}.cab.ms", t["cab"], "{:,.0f}")
        val(f"eq.{e}.cab.speed", t["full"] / t["cab"])
        val(f"eq.{e}.fm2.signal.ms", t["fm2_signal"], "{:,.0f}")
        val(f"eq.{e}.fm1.signal.ms", t["fm1_signal"], "{:,.0f}")
        val(f"eq.{e}.rand2000.ms", t["rand@2000"], "{:,.0f}")
        cab_t, cab_rr, full_rr = t["cab"], num(f"eq.{e}.m.cab.rr"), num(f"eq.{e}.m.full.rr")
        L.append(f"\\multicolumn{{5}}{{@{{}}l}}{{\\textit{{{ENAME[e]}: full budget {t['full']:,.0f}\\,ms, {full_rr:.1f}\\,\\%; "
                 f"\\method {cab_t:,.0f}\\,ms, {cab_rr:.1f}\\,\\%}}}} \\\\")
        key, params = ("seeds", ("0.025", "0.01")) if e == "sc" else ("k1", ("500", "250"))
        cheap_name = "Fewer seeds (ratio 0.025, 0.01)" if e == "sc" else "Fewer cliques ($K_1{=}500, 250$)"
        for v, name in [("cheap", cheap_name)] + variants:
            if v == "cheap":
                pts = [(t[f"{key}@{prm}"], num(f"eq.{e}.m.cheap.{prm}.rr")) for prm in params]
                ref_full = num(f"eq.{e}.m.cheap.{params[0]}.fullrr")
                cab_same = num(f"eq.{e}.m.cheap.{params[0]}.cab")
            else:
                pts = [(t[f"{v}@{b}"], num(f"eq.{e}.m.{v}.{b}.rr")) for b in BUDGETS[:4]]
                ref_full = num(f"eq.{e}.m.{v}.250.fullrr")
                cab_same = num(f"eq.{e}.m.{v}.250.cab")  # CAB on the same pairs as this variant
            curve = sorted(pts + [(t["full"], ref_full)])  # the full budget closes every curve (same pairs)
            hull = A.upper_hull(curve)
            hx, hy = [p[0] for p in hull], [p[1] for p in hull]
            at_cab = float(np.interp(cab_t, hx, hy)) if cab_t >= hx[0] else None
            reach = next((x0 + (cab_same - y0) / (y1 - y0) * (x1 - x0)
                          for (x0, y0), (x1, y1) in zip(hull, hull[1:]) if y0 < cab_same <= y1), None)
            if reach is None and hy[0] >= cab_same:
                reach = hx[0]
            tmin = min(p[0] for p in pts)
            val(f"eq.{e}.{v}.min.ms", tmin, "{:,.0f}")
            if at_cab is not None:
                val(f"eq.{e}.{v}.atcab", at_cab, "{:.1f}")
                val(f"eq.{e}.{v}.gap", cab_same - at_cab, "{:+.1f}")
                val(f"eq.{e}.{v}.gapu", cab_same - at_cab, "{:.1f}")  # unsigned form for running text
            if reach is not None:
                val(f"eq.{e}.{v}.reach.ms", reach, "{:,.0f}")
                val(f"eq.{e}.{v}.reach.x", reach / cab_t, "{:.1f}")
            gap = f"{cab_same - at_cab:+.1f}" if at_cab is not None else None
            cells = [name, f"{tmin:,.0f}", f"{at_cab:.1f}" if at_cab is not None else "--",
                     (gap.replace("-", "\\ensuremath{-}") if gap else "--"),
                     f"{reach:,.0f} ({reach / cab_t:.1f}\\X)" if reach is not None else "never"]
            L.append(" & ".join(cells) + " \\\\")
            xs, ys = [p[0] for p in curve], [p[1] for p in curve]
            if v == "cheap":
                ax.plot([p[0] for p in pts], [p[1] for p in pts], "v", color=colors[v], ms=6.0, mec="white", mew=0.6,
                        label=legend_name[v], zorder=4)
            else:
                ax.plot(xs, ys, "-o", color=colors[v], lw=1.5, ms=3.8, mec="white", mew=0.6, label=legend_name[v],
                        zorder=3)
        # equal time: the guide marks CAB's time; every curve is read where it crosses the guide. The arrow above
        # the curves goes from the full budget's time to CAB's time at (nearly) the same recall.
        y_ar = 83.3
        ax.plot([cab_t, cab_t], [70, y_ar], color=BLUE, lw=0.9, ls=(0, (3, 2)), zorder=2)
        ax.plot([t["full"], t["full"]], [full_rr + 0.5, y_ar], color=INK, lw=0.7, ls=(0, (1, 1.5)), zorder=2)
        ax.annotate("", xy=(cab_t, y_ar), xytext=(t["full"], y_ar), zorder=6,
                    arrowprops=dict(arrowstyle="-|>,head_length=0.45,head_width=0.22", fc=INK, ec=INK, lw=1.0,
                                    shrinkA=0, shrinkB=0))
        ax.text(np.sqrt(cab_t * t["full"]), y_ar + 0.3, f"{t['full'] / cab_t:.2f}× faster", ha="center", va="bottom",
                fontsize=FS_LEGEND, color=INK, weight="bold")
        ax.plot([t["full"]], [full_rr], "D", color=INK, ms=5.6, mec="white", mew=0.6, label="full budget", zorder=5)
        ax.plot([cab_t], [cab_rr], "*", color=BLUE, ms=13, mec=INK, mew=0.6, label="CAB (ours)", zorder=7)
        ax.set_xscale("log")
        ax.set_xlim(100, 1300)
        ax.set_ylim(70, 85.2)
        ax.set_yticks([70, 74, 78, 82])
        ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator([100, 200, 500, 1000]))
        ax.xaxis.set_major_formatter(matplotlib.ticker.FixedFormatter(["100", "200", "500", "1000"]))
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.set_xlabel("live time per pair (ms, log scale)")
        if e == "sc":
            ax.set_ylabel("recall (%)")
        else:
            ax.tick_params(labelleft=False)
        ax.set_title(f"({letter}) {ENAME[e].replace('$^2$', '²')} on 3DMatch", loc="left")
        style(ax)
        L.append("\\midrule" if e == "sc" else "\\bottomrule")
    handles = {}
    for ax in axes[:2]:
        for hh, ll in zip(*ax.get_legend_handles_labels()):
            handles.setdefault(ll, hh)
    order = ["CAB (ours)", "full budget", legend_name["compat"], legend_name["ratio"], legend_name["rand"],
             legend_name["cheap"], legend_name["fm1"], legend_name["fm2"]]  # two columns of four
    order = [o for o in order if o in handles]
    rh, rl = risk_ledger(axes[2])
    # legends in the band below the panels: equal time under (a)-(b), risk under (c)
    y_leg = 0.37 / H
    fig.legend([handles[o] for o in order], order, loc="center", ncol=2, bbox_to_anchor=(2.42 / W, y_leg),
               handlelength=1.9, columnspacing=2.0, labelspacing=0.25)
    fig.legend(rh, rl, loc="center", ncol=1, bbox_to_anchor=(6.0 / W, y_leg), handlelength=1.0, labelspacing=0.25)
    fig.savefig(FIG / "teaser.pdf", facecolor="white")
    plt.close(fig)
    (TAB / "equal_time.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


# ============================================================================ qualitative figure
def render_points(X, eye, target):
    """Perspective projection of points X seen from `eye` towards `target` (camera frame: y down, z forward), with
    a grey shade from a headlight on PCA normals and a little depth fog. Returns (uv, shade, depth, project)."""
    from scipy.spatial import cKDTree
    f = (target - eye) / np.linalg.norm(target - eye)
    r = np.cross(f, (0.0, -1.0, 0.0))
    r /= np.linalg.norm(r)
    R = np.stack([r, np.cross(r, f), f])  # rows: image right, image up, viewing direction

    def project(Y):
        c = (Y - eye) @ R.T
        return c[:, :2] / c[:, 2:], c[:, 2]

    _, nn = cKDTree(X).query(X, k=16)
    nb = X[nn] - X[nn].mean(1, keepdims=True)
    normals = np.linalg.eigh(np.einsum("nki,nkj->nij", nb, nb))[1][:, :, 0]
    light = R.T @ np.array([-0.3, 0.5, -1.0])
    uv, depth = project(X)
    fog = (depth - depth.min()) / np.ptp(depth)
    shade = np.clip(0.60 + 0.34 * np.abs(normals @ (light / np.linalg.norm(light))) - 0.14 * fog, 0, 1)
    return uv, shade, depth, project


def qualitative():
    from acpr.data import load_fragment, load_pairs
    from acpr.estimators import compat_order, nn_correspondences
    from acpr.features import get_fpfh

    ratio = {r["pair_id"]: r for r in B.load("3DMatch", "budget")}
    compat = {r["pair_id"]: r for r in B.load("3DMatch", "budgetc")}
    # a pair where the cheap budget fails with ratio order and succeeds with compatibility order,
    # with a typical number of true matches in the compat budget (first such pair in test order)
    pairs = [p for p in load_pairs("3DMatch") if p.pair_id in compat]
    cand = [p for p in pairs if not ratio[p.pair_id]["sc2"][0]["ok15"] and compat[p.pair_id]["sc2"][0]["ok15"]
            and 60 <= compat[p.pair_id]["gt_inliers_by_budget"][0] <= 150]
    p = cand[len(cand) // 2]
    rp, rf, _ = get_fpfh(p.pcd0)
    sp, sf, _ = get_fpfh(p.pcd1)
    P, Q, _ = nn_correspondences(sp, sf, rp, rf)
    P, Q = P[:4000], Q[:4000]
    perm, _ = compat_order(P, Q)
    gt = np.linalg.norm(P @ p.transform[:3, :3].T + p.transform[:3, 3] - Q, axis=1) < 0.1
    # the full-resolution reference fragment, seen from slightly above and right of its sensor
    X = np.asarray(load_fragment(p.pcd0), float)
    uv, shade, depth, project = render_points(X, np.array([0.35, -0.7, -0.3]), X.mean(0))
    back = np.argsort(-depth)  # far to near
    size = 3.2 * np.clip(np.median(depth) / depth[back], 0.7, 1.6) ** 2  # perspective splats fill the surfaces
    lo, hi = np.percentile(uv, 0.5, 0), np.percentile(uv, 99.5, 0)
    pad = 0.03 * (hi - lo)
    pw = 1.62  # panel width (in); the height follows the rendering's aspect ratio
    ph = pw * (hi - lo + 2 * pad)[1] / (hi - lo + 2 * pad)[0]
    W, H = 3.35, ph + 0.62
    fig = plt.figure(figsize=(W, H))
    axes = [fig.add_axes((x0 / W, 0.24 / H, pw / W, ph / H)) for x0 in (0.03, W - 0.03 - pw)]
    for ax, (title, idx) in zip(axes, (("250 most distinctive", np.arange(250)), ("250 most consistent (ours)", perm[:250]))):
        ax.scatter(uv[back, 0], uv[back, 1], s=size, c=np.repeat(shade[back, None], 3, 1), lw=0, rasterized=True)
        q, _ = project(Q[idx])
        ok = gt[idx]
        # outliers first, true correspondences on top, each with a white ring
        ax.scatter(q[~ok, 0], q[~ok, 1], s=10, c=ORANGE, edgecolors="white", linewidths=0.4, label="outlier")
        ax.scatter(q[ok, 0], q[ok, 1], s=13, c=BLUE, edgecolors="white", linewidths=0.4, label="true correspondence",
                   zorder=3)
        ax.set_title(title, fontsize=FS_LABEL, weight="normal", pad=12)
        ax.text(0.5, 1.0, f"{ok.sum()} true correspondences", transform=ax.transAxes, ha="center", va="bottom",
                fontsize=FS_LABEL, weight="bold", color=INK)
        ax.set_xlim(lo[0] - pad[0], hi[0] + pad[0])
        ax.set_ylim(lo[1] - pad[1], hi[1] + pad[1])
        ax.set_aspect("equal")
        ax.axis("off")
    h, lab = axes[1].get_legend_handles_labels()
    fig.legend(h[::-1], lab[::-1], loc="lower center", ncol=2, markerscale=1.3, columnspacing=1.5,
               bbox_to_anchor=(0.5, 0.0), borderaxespad=0.1)
    fig.savefig(FIG / "qualitative.pdf", facecolor="white")
    plt.close(fig)
    val("qual.pair", p.pair_id.replace("_", "\\_"))
    val("qual.ratio", str(int(gt[:250].sum())))
    val("qual.compat", str(int(gt[perm[:250]].sum())))


# ============================================================================ Part A (CAPS, supplementary)
def part_a():
    for variant, tag in (("psh_jump1024", "psh"), ("search_jump1024", "full")):
        summ = json.loads((RESULTS_ROOT / variant / "summary.json").read_text())
        live = json.loads((RESULTS_ROOT / f"live_{variant}.json").read_text())
        for s, S in SETS.items():
            st = summ["sets"][S]
            op = st["operating_points"]["mdp"]
            d_last, b_last = A.SCHEDULES["jump1024"][-1]  # largest configuration of the schedule, run once
            direct = next(x for x in st["static"] if x["d"] == d_last and x["b"] == b_last)
            k = f"A.{tag}.{s}"
            val(k + ".rr", 100 * op["rr"], "{:.1f}")
            val(k + ".ce", op["ce"] / 1e3, "{:,.0f}")
            refs = {"ransac": st["classical_ransac"], "r100k": st["ransac100k"], "sc2": st["sc2"],
                    "direct": direct, "anytime": st["exhaustive"]}
            for rk, rv in refs.items():
                val(f"{k}.{rk}.rr", 100 * rv["rr"], "{:.1f}")
                if "ce" in rv:
                    val(f"{k}.{rk}.ce", rv["ce"] / 1e3, "{:,.0f}")
                    val(f"{k}.{rk}.ceratio", rv["ce"] / op["ce"])
                val(f"{k}.{rk}.drr", 100 * (op["rr"] - rv["rr"]), "{:+.1f}")
            for rk, key in (("ransac", "vs_ransac_classical"), ("r100k", "vs_ransac100k"), ("anytime", "vs_exhaustive")):
                if key in op:
                    val(f"{k}.{rk}.p", pfmt(op[key]["mcnemar_p"]))
                    val(f"{k}.{rk}.pdrr", -100 * op[key]["delta_rr"], "{:+.1f}")
            rs = [r for r in live if r["subset"] == S and r["eligible"]]
            sc = np.array([r["scene"] for r in rs])
            ta = np.array([r["adaptive_s"] for r in rs])
            val(k + ".live.n", str(len(rs)))
            val(k + ".live.ms", 1e3 * ta.mean(), "{:.1f}")
            for rk, fk in (("ransac", "ransac_classical_s"), ("r100k", "ransac_100k_s"), ("sc2", "sc2_s"),
                           ("direct", "static_last_s")):
                tb = np.array([r[fk] for r in rs])
                sp, lo, hi = boot_ratio(tb, ta, sc, 1)
                val(f"{k}.{rk}.live", sp)
                val(f"{k}.{rk}.livelo", lo)
                val(f"{k}.{rk}.livehi", hi)
    L = []
    bench = [("RANSAC, classical stopping ($p{=}0.999$)", "ransac"), ("RANSAC, 100k hypotheses", "r100k"),
             ("SC$^2$ (simplified, same harness)", "sc2"), ("Largest search config., run once", "direct"),
             ("Anytime schedule run to completion", "anytime")]
    for tag, name in (("psh", "CAPS-fast (progressive voting)"), ("full", "CAPS-accurate (full voting)")):
        L.append(f"\\multicolumn{{9}}{{l}}{{\\textit{{Ours: {name}; recall {VALS[f'A.{tag}.m.rr']} / {VALS[f'A.{tag}.lo.rr']}\\,\\%, "
                 f"{VALS[f'A.{tag}.m.ce']} / {VALS[f'A.{tag}.lo.ce']}\\,k CE}}}} \\\\")
        for lab, rk in bench:
            cells = [lab]
            for s in SETS:
                k = f"A.{tag}.{s}.{rk}"
                cells.append(VALS[k + ".rr"])
                dd = VALS.get(k + ".pdrr", VALS[k + ".drr"])
                p = VALS.get(k + ".p")
                cells.append(f"{dd}" + (f" ($p{{=}}{p}$)" if p else ""))
                cells.append(f"{VALS[k + '.ceratio']}$\\times$" if k + ".ceratio" in VALS else "--")
                cells.append(f"{VALS[k + '.live']}$\\times$" if k + ".live" in VALS else "--")
            L.append(" & ".join(cells) + " \\\\")
        L.append("\\midrule" if tag == "psh" else "\\bottomrule")
    (TAB / "caps.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


def caps_extras():
    summ = {tag: json.loads((RESULTS_ROOT / v / "summary.json").read_text())
            for tag, v in (("full", "search_jump1024"), ("psh", "psh_jump1024"))}
    fams = (("learned_threshold", "threshold"), ("accept_or_giveup", "give-up"), ("mdp", "Markov"))
    L = []
    for tag, vname in (("full", "full"), ("psh", "progr.")):
        for fk, fname in fams:
            cells = [f"{vname}, {fname}"]
            for s, S in SETS.items():
                st = summ[tag]["sets"][S]
                op = st["operating_points"][fk]
                ve = op["vs_exhaustive"]
                hull = sorted((p[0], p[1]) for p in st["static_hull"])
                fr = float(np.interp(op["ce"], [p[0] for p in hull], [p[1] for p in hull]))
                ni = "\\cmark" if ve["non_inferior"] else "\\xmark"
                k = f"A.{tag}.{s}.{fk}"
                val(k + ".ce", op["ce"] / 1e3, "{:,.0f}")
                val(k + ".ub", 100 * ve["delta_rr_ub95"], "{:.1f}")
                val(k + ".frontier", 100 * (op["rr"] - fr), "{:+.1f}")
                ce = f"\\textbf{{{VALS[k + '.ce']}}}" if fk == "mdp" else VALS[k + ".ce"]
                cells += [ce, f"{100 * op['rr']:.1f}", f"{VALS[k + '.ub']} {ni}", VALS[k + ".frontier"]]
            L.append(" & ".join(cells) + " \\\\")
        L.append("\\midrule" if tag == "full" else "\\bottomrule")
    (TAB / "caps_controllers.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
    L = []
    rows = {S: summ["psh"]["sets"][S]["ransac_allocation"] for S in SETS.values()}
    for i, b in enumerate(rows["3DMatch"]):
        cells = ["{" + b["gt_inliers"].replace("inf", "$\\infty$") + "}"]  # braces: "[" would start an optional argument
        for S in SETS.values():
            x = rows[S][i]
            cells += [str(x["pairs"]), f"{100 * x['classical_cost_share']:.0f}", f"{100 * x['classical_rr']:.1f}"]
        L.append(" & ".join(cells) + " \\\\")
    (TAB / "ransac_waste.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
    for variant in ("psh_jump1024",):
        st = summ["psh"]["sets"]
        for s, S in SETS.items():
            rr = [x for x in st[S]["ransac_allocation"] if x["gt_inliers"] in ("[0,5)", "[5,10)")]
            val(f"A.waste.psh.{s}.share", 100 * sum(x["classical_cost_share"] for x in rr), "{:.0f}")
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.75))
    for ax, (s, S) in zip(axes, SETS.items()):
        F, P = summ["full"]["sets"][S], summ["psh"]["sets"][S]
        h = A.upper_hull([(x["ce"] / 1e3, 100 * x["rr"]) for x in F["static"]])
        ax.plot([p[0] for p in h], [p[1] for p in h], color=MUTED, lw=1.2, ls=(0, (4, 2)),
                label="static search configurations (frontier)")
        for st, col, lab, mk in ((F, BLUE, "CAPS-accurate, all thresholds", "o"), (P, AQUA, "CAPS-fast, all thresholds", "^")):
            fr = A.upper_hull(sorted({(x["ce"] / 1e3, 100 * x["rr"]) for x in st["families"]["mdp"]}))
            ax.plot([p[0] for p in fr], [p[1] for p in fr], color=col, lw=1.5, marker=mk, ms=4.0, mec="white", mew=0.5,
                    label=lab)
            op = st["operating_points"]["mdp"]
            ax.plot([op["ce"] / 1e3], [100 * op["rr"]], "*", ms=12, color=col, mec=INK, mew=0.6, zorder=6)
        fr = A.upper_hull(sorted({(x["ce"] / 1e3, 100 * x["rr"]) for x in F["families"]["ransac_fixed"]}))
        ax.plot([p[0] for p in fr], [p[1] for p in fr], color=ORANGE, lw=1.5, marker="s", ms=3.6, mec="white", mew=0.5,
                label="RANSAC, fixed budgets")
        cr = F["classical_ransac"]
        ax.plot([cr["ce"] / 1e3], [100 * cr["rr"]], "o", ms=6, mfc="white", mec=ORANGE, mew=1.5, zorder=5,
                label="RANSAC, classical stopping")
        ex = F["exhaustive"]
        ax.plot([ex["ce"] / 1e3], [100 * ex["rr"]], "D", ms=5.5, color=INK2, mec="white", mew=0.6, zorder=5,
                label="schedule run to completion")
        ax.axhline(100 * F["sc2"]["rr"], color=MUTED, lw=0.9, ls=":")
        ax.text(0.02, 100 * F["sc2"]["rr"], "SC²-PCR recall", transform=ax.get_yaxis_transform(), ha="left",
                va="bottom", color=INK2, fontsize=FS_LEGEND)
        ax.set_xscale("log")
        ax.set_xlabel("mean cost per pair (thousand CE, log scale)")
        ax.set_ylabel("recall (%)")
        ax.set_title(S, loc="left")
        style(ax)
    axes[0].plot([], [], "*", ms=12, color="white", mec=INK, mew=0.6, label="certified operating point")
    fig.tight_layout(rect=(0, 0.16, 1, 1), pad=0.4, w_pad=1.5)
    fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=4, bbox_to_anchor=(0.5, 0.0),
               handlelength=1.9, columnspacing=1.2)
    fig.savefig(FIG / "caps_tradeoff.pdf", facecolor="white")
    plt.close(fig)


# ============================================================================ design studies and misc
def registrability():
    import select_ladder as S
    from sklearn.metrics import roc_auc_score

    logs = {s: B.load(s) for s in ["train", "val", "3DMatch", "3DLoMatch"]}
    for est, e in (("sc2", "sc"), ("turbo", "tr")):
        tr, _ = S.build(logs, est, B.LADDERS["x4"])
        for s, key in (("val", "val"), ("3DMatch", "m"), ("3DLoMatch", "lo")):
            y = np.array([t[-1]["ok"] for t in tr[s]], dtype=int)
            p = np.array([t[0]["p_final"] for t in tr[s]])
            val(f"reg.{e}.{key}.auc", roc_auc_score(y, p))


def ablations():
    rs = [json.loads(x) for x in open(LOG_ROOT / "budgetc_val.jsonl")]
    old = {r["pair_id"]: r for r in map(json.loads, open(LOG_ROOT / "budget_val.jsonl"))}
    one = {r["pair_id"]: r for r in map(json.loads, open(LOG_ROOT / "budgetc100_val.jsonl"))}
    rows = []
    for tag, name, src in (("ratio", "Lowe ratio", None), ("one", "One pass", one), ("two", "\\textbf{Two passes (ours)}", "self")):
        def pick(r, src=src):
            return old[r["pair_id"]] if src is None else (r if src == "self" else src[r["pair_id"]])
        cells = [name, val(f"abl.top250.{tag}", np.mean([pick(r)["gt_inliers_by_budget"][0] for r in rs]), "{:.1f}")]
        for e in ("sc2", "turbo"):
            for k in (0, 1, 2):
                cells.append(val(f"abl.{e}.k{k}.{tag}", 100 * np.mean([pick(r)[e][k]["ok15"] for r in rs]), "{:.1f}"))
        rows.append(" & ".join(cells) + " \\\\")
    for tag in ("one", "two"):
        for k in (0, 1, 2):
            val(f"abl.sc2.k{k}.gain.{tag}", num(f"abl.sc2.k{k}.{tag}") - num(f"abl.sc2.k{k}.ratio"), "{:+.1f}")
    (TAB / "ordering_ablation.tex").write_text("\n".join(rows) + "\n", encoding="utf-8")
    val("abl.full.sc", 100 * np.mean([old[r["pair_id"]]["sc2"][4]["ok15"] for r in rs]), "{:.1f}")
    val("abl.full.tr", 100 * np.mean([old[r["pair_id"]]["turbo"][4]["ok15"] for r in rs]), "{:.1f}")
    val("abl.anchors.true", np.mean([r["anchors_true"] for r in rs]), "{:.1f}")
    val("abl.torder.log", 1e3 * np.mean([r["t_order"] for r in rs]), "{:.0f}")
    st = json.loads((RB / "ordering_study_anchors_val.json").read_text())
    val("abl.torder.micro", st["timing_ms"]["tp_s500"], "{:.1f}")
    val("abl.ratio.top100.true", np.mean([r["gt_top100"] for r in st["rows"]]), "{:.1f}")
    val("abl.ratio.top100.zero", 100 * np.mean([r["gt_top100"] == 0 for r in st["rows"]]), "{:.0f}")
    for e in ("sc2", "turbo"):
        val(f"abl.stage0.{e}.ratio", 1e3 * np.mean([old[r["pair_id"]][e][0]["s"] for r in rs]), "{:.0f}")
        val(f"abl.stage0.{e}.compat", 1e3 * np.mean([r[e][0]["s"] for r in rs]), "{:.0f}")
    val("abl.stage0.turbo.factor", num("abl.stage0.turbo.compat") / num("abl.stage0.turbo.ratio"), "{:.1f}")
    # pitfall 2: full-budget SC^2 time, validation vs 3DMatch test (ratio-order logs)
    for s, key in (("val", "val"), ("3DMatch", "m")):
        recs = B.load(s)
        val(f"pit.full.{key}", 1e3 * np.mean([B.trajectory_ladder(r, "sc2", (4,))[-1]["s"] for r in recs]), "{:,.0f}")


def kitti_meta():
    from acpr import kitti as K
    val("ki.n.test", f"{len(K.load_kitti_pairs('test')):,}")
    val("ki.n.val", f"{len(K.load_kitti_pairs('val')):,}")
    val("ki.n.train", f"{len(K.train_fit()):,}")
    val("ki.n.calib", f"{len(K.calib_indices()):,}")
    val("ki.n.cert", f"{len(K.load_kitti_pairs('val')) + len(K.calib_indices()):,}")
    thr_path = RESULTS_ROOT / "kitti" / "thresholds.json"
    if not thr_path.exists():
        return
    thr = json.loads(thr_path.read_text())
    val("ki.thr.sc2", thr["sc2_d_thre"], "{:.2f}")
    val("ki.thr.turbo", thr["turbo_tau"], "{:.3f}")
    L = []
    for est, name, chosen in (("sc2", "\\SCP ($d$)", thr["sc2_d_thre"]), ("turbo", "TurboReg ($\\tau$)", thr["turbo_tau"])):
        items = sorted((float(k.split("@")[1]), v) for k, v in thr["validation"].items() if k.startswith(est + "@"))
        for i, (v, r) in enumerate(items):
            mark = " (chosen)" if abs(v - chosen) < 1e-9 else ""
            L.append(f"{name if i == 0 else ''} & {v:.3f}{mark} & {100 * r['rr']:.1f} & {1e3 * r['s']:,.0f} \\\\")
    (TAB / "supp_kitti_thresholds.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


def latency():
    """Supp table: per-pair live latency percentiles (ms) of the full budget and CAB (compatibility order), and the
    share of pairs on which CAB is slower than the full budget (the first-stage overhead on hard pairs)."""
    L, worst = [], []
    for fam, sets_ in (("3dmatch", [("m", "3DMatch"), ("lo", "3DLoMatch")]), ("kitti", [("ki", "kitti_test")]),
                       ("fcgf3dmatch", [("fm", "fcgf_3DMatch"), ("flo", "fcgf_3DLoMatch")])):
        path = RB / LIVE[fam]
        if not path.exists():
            continue
        rows = json.loads(path.read_text())
        for d, s in sets_:
            for e, E in ESTS.items():
                rs = [r for r in rows if r["est"] == E and r["subset"] == s]
                if not rs:
                    continue
                f = 1e3 * np.array([r["full"]["s"] for r in rs])
                c = 1e3 * np.array([r["budgetc"]["s"] for r in rs])
                q = lambda x, p: float(np.percentile(x, p))  # noqa: E731
                slower = 100 * np.mean(c > f)
                k = f"lat.{e}.{d}"
                for p in (50, 90, 99):
                    val(f"{k}.full.p{p}", q(f, p), "{:,.0f}")
                    val(f"{k}.cab.p{p}", q(c, p), "{:,.0f}")
                val(k + ".slower", slower, "{:.0f}")
                val(k + ".overhead.p99", 100 * (q(c, 99) / q(f, 99) - 1), "{:+.0f}")
                worst.append((100 * (q(c, 99) / q(f, 99) - 1), f"{ENAME[e]} on {dlabel(d)}"))
                L.append(f"{ENAME[e]}, {dlabel(d)} & {len(rs)} & {q(f, 50):,.0f} / {q(c, 50):,.0f} & "
                         f"{q(f, 90):,.0f} / {q(c, 90):,.0f} & {q(f, 99):,.0f} / {q(c, 99):,.0f} & {slower:.0f} \\\\")
    (TAB / "supp_latency.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
    if all(f"lat.{e}.lo.slower" in VALS for e in ESTS):  # 3DLoMatch: share of pairs slower than the full budget
        a, b = sorted(int(VALS[f"lat.{e}.lo.slower"]) for e in ESTS)
        val("lat.lo.slower", f"{a}" if a == b else f"{a}--{b}")
    if worst:  # largest increase of the 99th-percentile latency over the full budget
        val("lat.overhead.p99.max", max(worst)[0], "{:.0f}")
        val("lat.overhead.p99.where", max(worst)[1])


def evidence_extra():
    """Supp table from results/budget/evidence_extra.json: worst-case mixture risk (largest group risk) for CAB and
    the marginal certificate, largest per-scene risk, and the controller re-fitted on bootstrap resamples."""
    path = RB / "evidence_extra.json"
    if not path.exists():
        return
    data = json.loads(path.read_text())
    names = {"3DMatch": "3DMatch", "3DLoMatch": "3DLoMatch", "kitti_test": "KITTI", "fcgf_3DMatch": "3DMatch (FCGF)",
             "fcgf_3DLoMatch": "3DLoMatch (FCGF)"}
    L, wg, wm, groups, over = [], [], [], 0, []
    for dname in ("fpfh_indoor", "fpfh_kitti", "fcgf_indoor"):
        for e, E in ESTS.items():
            for t, r in data[dname][E].items():
                sp = np.array([b["speedup"] for b in r["bootstrap"]])
                rk = np.array([b["risk"] for b in r["bootstrap"]])
                scene_risk = max(v["risk"] for v in r["scenes"].values())
                wg.append(100 * r["worst_group"])
                wm.append(100 * r["worst_marginal"])
                for g in r["groups"]:
                    groups += 1
                    if g["risk_group"] > 0.01:
                        over.append((g["risk_group"], g["n"]))
                L.append(f"{ENAME[e]}, {names[t]} & {100 * r['worst_group']:.2f} & {100 * r['worst_marginal']:.2f} & "
                         f"{100 * scene_risk:.2f} & {sp.mean():.2f}\\X\\,[{sp.min():.2f}, {sp.max():.2f}] & {100 * rk.max():.2f} \\\\")
    val("ev.worst.group.max", max(wg), "{:.2f}")
    val("ev.worst.marg.max", max(wm), "{:.2f}")
    val("ev.worst.marg.min", min(wm), "{:.2f}")
    val("ev.groups.n", str(groups))
    val("ev.groups.over", str(len(over)))
    if over:
        r, n = max(over)
        val("ev.groups.over.risk", 100 * r, "{:.2f}")
        val("ev.groups.over.lost", str(int(round(r * n))))
        val("ev.groups.over.n", str(n))
    (TAB / "supp_evidence.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


def sensitivity():
    """Supp table from results/budget/sensitivity.json: offline speed-up (risk) per (epsilon, G) setting."""
    path = RB / "sensitivity.json"
    if not path.exists():
        return
    data = json.loads(path.read_text())
    settings = [("0.005", "3"), ("0.01", "3"), ("0.02", "3"), ("0.05", "3"), ("0.01", "1"), ("0.01", "2"),
                ("0.01", "4"), ("0.01", "5")]
    cols = [("3dmatch", "3DMatch"), ("kitti", "kitti_test")]
    L, viol = [], 0
    for eps, g in settings:
        key = f"{float(eps)}_{g}"
        cells = [f"{100 * float(eps):g}", g]
        for dname, test in cols:
            for e, E in ESTS.items():
                r = data[dname][E][test][key]
                over = r["risk"] > float(eps)
                viol += over
                risk = f"{100 * r['risk']:.2f}"
                cells.append(f"{r['speedup']:.2f}\\X\\,({'\\textbf{' + risk + '}' if over else risk})")
                val(f"sens.{e}.{dname}.{eps}.{g}.speed", r["speedup"])
                val(f"sens.{e}.{dname}.{eps}.{g}.risk", 100 * r["risk"], "{:.2f}")
        L.append(" & ".join(cells) + " \\\\")
        if (eps, g) == ("0.05", "3"):
            L.append("\\midrule")
    val("sens.violations", str(viol))
    (TAB / "supp_sensitivity.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


def fcgf_scene_disjoint():
    """Supp table from results/budget/fcgf_scene_disjoint.json (cross-fitting over scenes, compatibility order)."""
    path = RB / "fcgf_scene_disjoint.json"
    if not path.exists():
        return
    data = json.loads(path.read_text())
    L, risks_g, risks_m = [], [], []
    names = {"fcgf_3DMatch": ("fm", "3DMatch"), "fcgf_3DLoMatch": ("flo", "3DLoMatch"), "fcgf_kitti_test": ("fki", "KITTI")}
    for s, (d, nm) in names.items():
        if s not in data:
            continue
        for e, E in ESTS.items():
            g, m = data[s][E]["compat"]["mondrian"], data[s][E]["compat"]["marginal"]
            k = f"fsd.{e}.{d}"
            val(k + ".speed", g["speedup"])
            val(k + ".risk", 100 * g["risk"], "{:.2f}")
            val(k + ".loss", 100 * g["delta_rr"], "{:.2f}")
            val(k + ".ub", 100 * g["ub95"], "{:.2f}")
            val(k + ".marg.risk", 100 * m["risk"], "{:.2f}")
            risks_g.append(100 * g["risk"])
            risks_m.append(100 * m["risk"])
            ni = "\\cmark" if g["non_inferior"] else "\\xmark"
            L.append(f"{ENAME[e]}, {nm} & {100 * g['delta_rr']:.2f} [{100 * g['ub95']:.2f}] {ni} & {g['speedup']:.2f}\\X & "
                     f"{100 * g['risk']:.2f} & {100 * m['risk']:.2f} \\\\")
    if risks_g:
        val("fsd.group.risk.max", max(risks_g), "{:.2f}")
        val("fsd.marg.risk.max", max(risks_m), "{:.2f}")
    (TAB / "supp_fcgf_scene.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


def calibration_size():
    """Supp table from results/budget/calibration_size.json: smallest calibration pool that certifies, and how often
    the certificates exceed the 1 % level on test (over all subset sizes)."""
    path = RB / "calibration_size.json"
    if not path.exists():
        return
    data = json.loads(path.read_text())
    L = []
    names = {"3DMatch": "3DMatch", "3DLoMatch": "3DLoMatch", "kitti_test": "KITTI"}
    for dname, ests in data.items():
        for e, E in ESTS.items():
            for test, tags in ests[E].items():
                cells = [f"{ENAME[e]}, {names[test]}"]
                for tag in ("mondrian", "marginal"):
                    by_n = {int(n): recs for n, recs in tags[tag].items()}
                    nmin = min((n for n, recs in by_n.items() if np.mean([r["certified"] for r in recs]) >= 0.5),
                               default=None)
                    cert = [r for recs in by_n.values() for r in recs if r["certified"]]
                    over = 100 * np.mean([r["risk"] > 0.01 for r in cert]) if cert else float("nan")
                    worst = 100 * max(r["risk"] for r in cert) if cert else float("nan")
                    k = f"cal.{e}.{test}.{tag}"
                    if nmin is not None:
                        val(k + ".nmin", f"{nmin:,}")
                    val(k + ".over", over, "{:.0f}")
                    val(k + ".worst", worst, "{:.2f}")
                    cells += [f"{nmin:,}" if nmin else "--", f"{over:.0f}", f"{worst:.2f}"]
                L.append(" & ".join(cells) + " \\\\")
    # summary keys for the text: the share of marginal certificates above 1 % on KITTI, and the group-conditional maximum
    over_k = [num(f"cal.{e}.kitti_test.marginal.over") for e in ESTS if f"cal.{e}.kitti_test.marginal.over" in VALS]
    if over_k:
        val("cal.kitti.marg.over.max", max(over_k), "{:.0f}")
    worst_g = [num(k) for k in VALS if k.startswith("cal.") and k.endswith(".mondrian.worst")]
    if worst_g:
        val("cal.group.worst.max", max(worst_g), "{:.2f}")
    (TAB / "supp_calibration_size.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


# published full-budget recall (%) under the same success criteria, from TurboReg (Yan et al., ICCV 2025), Tables 1, 2
# and 4: SC2-PCR, and TurboReg with K1 = 2,000 indoors and 500 pivots on KITTI
PUBLISHED_RR = {("sc", "fpfh"): (83.73, 38.57, 96.40), ("tr", "fpfh"): (84.10, 40.99, 97.84),
                ("sc", "fcgf"): (93.16, 58.73, 97.12), ("tr", "fcgf"): (93.59, 59.74, 98.20)}


def fidelity():
    """Supp table: full-budget recall of our re-implementations vs published, with FPFH (test sets) and with the
    released FCGF features (all test pairs: even-indexed and held-out)."""
    L = []
    for desc in ("fpfh", "fcgf"):
        for e, E in ESTS.items():
            ours = []
            for d, s in (("m", "3DMatch"), ("lo", "3DLoMatch"), ("ki", "kitti_test")):
                if desc == "fpfh":
                    ours.append(num(f"{e}.{d}.ratio.group.full"))
                else:
                    recs = B.load(f"fcgf_{s}", "budgetc") + B.load(f"fcgf_{s}_cal", "budgetc")
                    ours.append(100 * np.mean([r[E][4]["ok15"] for r in recs]) if recs else float("nan"))
            pub = PUBLISHED_RR[(e, desc)]
            for (d, o, p) in zip(("m", "lo", "ki"), ours, pub):
                val(f"fid.{e}.{desc}.{d}.ours", o, "{:.1f}")
                val(f"fid.{e}.{desc}.{d}.gap", p - o, "{:.1f}")
            cells = [f"{ENAME[e]}, {desc.upper()}"] + [x for o, p in zip(ours, pub) for x in (f"{o:.1f}", f"{p:.1f}")]
            L.append(" & ".join(cells) + " \\\\")
    for desc in ("fpfh", "fcgf"):  # gap ranges for the text (indoor sets, both estimators)
        g = [num(f"fid.{e}.{desc}.{d}.gap") for e in ESTS for d in ("m", "lo")]
        val(f"fid.{desc}.indoor.gap.min", min(g), "{:.1f}")
        val(f"fid.{desc}.indoor.gap.max", max(g), "{:.1f}")
        gk = [num(f"fid.{e}.{desc}.ki.gap") for e in ESTS]
        val(f"fid.{desc}.kitti.gap.min", min(gk), "{:.1f}")
        val(f"fid.{desc}.kitti.gap.max", max(gk), "{:.1f}")
    (TAB / "supp_reimpl.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    TAB.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    setup_style()
    ds, logs, _ = cab_results()
    anchors_and_headroom(ds, logs)
    controller_calibration()
    equal_time(logs)
    qualitative()
    part_a()
    caps_extras()
    registrability()
    ablations()
    kitti_meta()
    calibration_size()
    fidelity()
    fcgf_scene_disjoint()
    sensitivity()
    evidence_extra()
    latency()
    lines = ["% generated by scripts/paper_assets.py -- do not edit"]
    lines += [f"\\defval{{{k}}}{{{v}}}" for k, v in sorted(VALS.items())]
    (PAPER / "numbers.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"datasets with CAB results: {ds}; wrote {len(VALS)} values, tables and figures to {PAPER}")


if __name__ == "__main__":
    main()
