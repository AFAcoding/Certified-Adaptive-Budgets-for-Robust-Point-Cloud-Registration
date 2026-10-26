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
# protocol v2 (PROTOCOL.md): test set -> (log name, dataset of select_ladder.DATASETS). Blind tests: bh, bl (held-out
# 3DMatch training scenes, overlap > 30 % / 10-30 %), kr (KITTI raw drives, FPFH), fkr (KITTI raw drives, FCGF).
# Development benchmarks (seen during development): m, lo, ki (FPFH), fm, flo, fki (FCGF, own features).
DS = {"bh": ("v2_blind_hi", "v2_indoor_fpfh"), "bl": ("v2_blind_lo", "v2_indoor_fpfh"),
      "kr": ("kitti_raw_blind", "v2_kitti_fpfh"), "fkr": ("fcgfown_kitti_raw_blind", "v2_kitti_fcgf"),
      "m": ("3DMatch", "v2_indoor_fpfh"), "lo": ("3DLoMatch", "v2_indoor_fpfh"), "ki": ("kitti_test", "v2_kitti_fpfh"),
      "fm": ("fcgfown_3DMatch", "v2_indoor_fcgf"), "flo": ("fcgfown_3DLoMatch", "v2_indoor_fcgf"),
      "fki": ("fcgfown_kitti_test", "v2_kitti_fcgf"),
      # protocol v3: fresh blind test (pairs never processed before), overlap > 30 % / 10-30 %
      "th": ("v3_blind_hi", "v3_indoor_fpfh"), "tl": ("v3_blind_lo", "v3_indoor_fpfh")}
BLIND = ("bh", "bl", "kr", "fkr")
BLIND3 = ("th", "tl")
DNAME = {"bh": "Held-out scenes", "bl": "Held-out scenes, low overlap", "kr": "KITTI raw", "fkr": "KITTI raw",
         "m": "3DMatch", "lo": "3DLoMatch", "ki": "KITTI", "fm": "3DMatch", "flo": "3DLoMatch", "fki": "KITTI",
         "th": "Fresh scenes", "tl": "Fresh scenes, low overlap"}
FCGF = {"fkr", "fm", "flo", "fki"}


def dlabel(d):
    return DNAME[d] + (" (FCGF)" if d in FCGF else "")


DSENT = {"bh": "the held-out scenes", "bl": "the held-out scenes at low overlap", "kr": "the KITTI raw drives",
         "fkr": "the KITTI raw drives", "m": "3DMatch", "lo": "3DLoMatch", "ki": "KITTI odometry", "fm": "3DMatch",
         "flo": "3DLoMatch", "fki": "KITTI odometry", "th": "the fresh scenes", "tl": "the fresh scenes at low overlap"}


def dsent(d):
    """A test set named in running text."""
    return DSENT[d] + (" with FCGF" if d in FCGF else "")


FAMS = ("v2_indoor_fpfh", "v2_kitti_fpfh", "v2_indoor_fcgf", "v2_kitti_fcgf", "v3_indoor_fpfh")
SEL = {(f, o): f"ladder_selection{'_compat' if o == 'compat' else ''}_ext_{f}.json" for f in FAMS for o in ("ratio", "compat")}
SEL_RCERT = {}
LIVE = {f: f"live_budget_compare_ext_{f}.json" for f in FAMS}
LIVE["v3_indoor_fpfh"] = "live_budget_compare_ext_v3_indoor_fpfh_v3.json"  # also times CAB without the gate
LIVE_XFER = {}
PREFIX = {"ratio": "budget", "compat": "budgetc"}
ESTS = {"sc": "sc2", "tr": "turbo"}
ENAME = {"sc": "SC$^2$-PCR", "tr": "TurboReg", "mc": "MAC"}
# MAC (protocol v3, addendum A): third estimator, indoor FPFH only; selection files carry the suffix _mac
ESTS_ALL = {**ESTS, "mc": "mac"}
MAC_SETS = ("th", "tl", "bh", "bl", "kr", "fkr", "m", "lo", "ki", "fm", "flo", "fki")  # addenda A and B
# published recall of MAC (Zhang et al., CVPR 2023, Tables 1, 2 and 4)
MAC_PUBLISHED = {("fpfh", "m"): 84.10, ("fpfh", "lo"): 40.88, ("fpfh", "ki"): 99.46,
                 ("fcgf", "m"): 93.72, ("fcgf", "lo"): 59.85, ("fcgf", "ki"): 97.84}
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
FS_CELL = 6.2  # values inside the cells of a grid


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


TRANSFER = RB / "transfer_fcgf_v2.json"  # not used in protocol v2


def available(d):
    log, fam = DS[d]
    if not (LOG_ROOT / f"budgetc_{log}.jsonl").exists():
        return False
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
    import select_ladder as S  # split sizes of every dataset (fitting, calibration, test)
    for fam in FAMS:
        D = S.DATASETS[fam]
        val(f"{fam}.n.fit", f"{len(B.load(D['train'], 'budgetc')):,}")
        val(f"{fam}.n.cal", f"{len(B.load(D['val'], 'budgetc')):,}")
    for d in ds:
        val(f"{d}.n.test", f"{len(logs[(d, 'compat')]):,}")
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
    eq_path = RB / "live_equal_time_v2_blind_hi.json"
    if eq_path.exists():
        stalls += [max(r["stalled"].values()) for r in json.loads(eq_path.read_text()) if "stalled" in r]
    val("live.retimed", str(len(stalls)))
    val("live.stall.s", max(stalls, default=0.0), "{:,.0f}")
    # worst live speed-up of CAB (compat order, group-conditional): its overhead where there is nothing to save
    worst = min(((num(f"{e}.{d}.compat.live.speed"), e, d) for d in ds for e in ESTS
                 if f"{e}.{d}.compat.live.speed" in VALS), default=None)
    if worst is not None:
        val("cab.live.min", worst[0])
        val("cab.live.min.pct", 100 * (1 / worst[0] - 1), "{:.0f}")  # extra time where CAB is slowest
        val("cab.live.min.where", f"{ENAME[worst[1]]} on {dsent(worst[2])}")

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

    # ---- main tables: blind tests (FPFH; FCGF on the raw drives runs the full budget) and development benchmarks
    def table(blocks, ncols, path):
        L = []
        for title, cols in blocks:
            if not any(d in ds for d in cols):
                continue
            L.append(f"\\multicolumn{{{ncols}}}{{@{{}}l}}{{\\textbf{{{title}}}}} \\\\")
            for e in ESTS:
                L.append(f"\\multicolumn{{{ncols}}}{{@{{}}l}}{{\\textit{{{ENAME[e]}}}}} \\\\")
                for lab, o in (("Full budget (standard)", None), ("\\method, ratio order", "ratio"),
                               ("\\textbf{\\method (ours)}", "compat")):
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
                        bold = (lambda x: f"\\textbf{{{x}}}") if o == "compat" else (lambda x: x)
                        cells += [bold(VALS[k + ".rr"]), f"{VALS[k + '.loss']} [{VALS[k + '.ub']}] {ni}", bold(lv),
                                  bold(f"{VALS[k + '.ops']}\\X"), VALS[k + ".risk"]]
                    L.append(" & ".join(cells) + " \\\\")
            L.append("\\midrule")
        L[-1] = "\\bottomrule"
        (TAB / path).write_text("\n".join(L) + "\n", encoding="utf-8")

    table([("FPFH correspondences", ["bh", "bl", "kr"])], 16, "blind_results.tex")
    table([("FPFH correspondences", ["m", "lo", "ki"]), ("FCGF correspondences", ["fm", "flo", "fki"])], 16,
          "main_results.tex")

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
    # too long for one page: blind test sets (fresh scenes first) and development benchmarks in two tables
    rows = {d: [r for r in L if r.startswith(dlabel(d) + " & ")] for d in ds}
    for name, sets in (("blind", [d for d in BLIND3 + BLIND if d in ds]),
                       ("dev", [d for d in ds if d not in BLIND3 + BLIND])):
        P = [x for d in sets for x in rows[d] + ["\\midrule"]]
        (TAB / f"supp_full_results_{name}.tex").write_text("\n".join(P[:-1]) + "\n", encoding="utf-8")

    # ---- supplementary: fixed budgets
    L = []
    for e in ESTS:
        for o, oname in (("ratio", "ratio"), ("compat", "compat.")):
            cells = [ENAME[e], oname]
            for d in ("m", "lo", "ki"):
                cells += [VALS.get(f"{e}.{d}.{o}.fix{i}.rr", "--") for i in range(5)]
            L.append(" & ".join(cells) + " \\\\")
    (TAB / "supp_fixed_budgets.tex").write_text("\n".join(L) + "\n", encoding="utf-8")

    fig_tradeoff_all(ds, fixed, logs)
    return ds, logs, fixed


def fig_tradeoff_all(ds, fixed, logs=None):
    """Supplementary figure: recall vs relative time of every fixed budget, with the certified operating points of CAB
    without the gate (colour: ordering; filled diamond: group-conditional certificate; open square: marginal
    certificate). One row per estimator (MAC from the merged MAC logs, where they exist), one column per FPFH test set;
    time relative to the full budget of the same run, log scale."""
    import matplotlib.ticker as mticker
    dsf = [d for d in ds if d not in FCGF and d not in BLIND3]
    short = {"bh": "Held-out scenes", "bl": "Held-out, low overlap", "kr": "KITTI raw drives", "m": "3DMatch",
             "lo": "3DLoMatch", "ki": "KITTI odometry"}
    rows = dict(ESTS)
    if logs is not None and all(f"mc.{d}.compat.group.speed" in VALS for d in dsf) and \
            all(all(isinstance(r.get("mac"), list) for r in logs[(d, o)]) for d in dsf for o in PREFIX):
        rows["mc"] = "mac"
        for d in dsf:
            for o in PREFIX:
                fixed[(d, o, "mc")] = fixed_points(logs[(d, o)], "mac")
    W, ROW, TOP, BOT = 7.0, 1.42, 0.22, 0.95
    fig, axes = plt.subplots(len(rows), len(dsf), figsize=(W, TOP + ROW * len(rows) + BOT), squeeze=False,
                             sharey="col")
    xmin = min(p[0] / fixed[(d, o, e)][-1][0] for e in rows for d in dsf for o in PREFIX for p in fixed[(d, o, e)])
    for r, e in enumerate(rows):
        for c, d in enumerate(dsf):
            ax = axes[r, c]
            for o, col, name in (("ratio", GRAY, "ratio order"), ("compat", BLUE, "our ordering")):
                pts = fixed[(d, o, e)]
                ax.plot([p[0] / pts[-1][0] for p in pts], [100 * p[1] for p in pts], "-o", color=col, lw=1.4, ms=3.2,
                        mec="white", mew=0.5, label=f"fixed budgets, {name}", zorder=2)
            for cert, mk, cname in (("group", "D", "group-conditional"), ("marg", "s", "marginal")):
                for o, col, name in (("ratio", DARK, "ratio order"), ("compat", BLUE, "our ordering")):
                    k = f"{e}.{d}.{o}.{cert}"
                    ax.plot([1.0 / num(k + ".speed")], [num(k + ".rr")], mk, ls="none", ms=5.6 if mk == "D" else 5.2,
                            color=col, mfc=col if cert == "group" else "white", mec="white" if cert == "group" else col,
                            mew=0.6 if cert == "group" else 1.2, zorder=5 if cert == "group" else 4,
                            label=f"CAB, {name}, {cname}")
            ax.set_xscale("log")
            ax.set_xlim(0.8 * xmin, 1.3)
            ax.xaxis.set_major_locator(mticker.FixedLocator([0.01, 0.1, 1]))
            ax.xaxis.set_major_formatter(mticker.FixedFormatter(["0.01", "0.1", "1"]))
            ax.xaxis.set_minor_formatter(mticker.NullFormatter())
            ax.yaxis.set_major_locator(mticker.MaxNLocator(4))
            style(ax)
            if r == 0:
                ax.set_title(short[d], loc="center", fontsize=FS_LABEL)
            if r < len(rows) - 1:
                ax.tick_params(labelbottom=False)
            if c == 0:
                ax.set_ylabel(f"{ENAME[e].replace('$^2$', '²')}\nrecall (%)", fontsize=FS_LABEL)
    fig.subplots_adjust(left=0.085, right=0.99, top=1 - TOP / fig.get_figheight(), wspace=0.42, hspace=0.18,
                        bottom=BOT / fig.get_figheight())
    fig.text(0.535, (BOT - 0.33) / fig.get_figheight(), "time relative to the full budget of the same run (log scale)",
             ha="center", va="center", fontsize=FS_LABEL)
    fig.legend(*axes[0, 0].get_legend_handles_labels(), loc="lower center", ncol=3, bbox_to_anchor=(0.535, 0.0),
               handlelength=1.8, columnspacing=1.6, fontsize=FS_LEGEND)
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
    for d in [d for d in BLIND3 + BLIND + ("m", "lo", "ki", "fm", "flo", "fki") if d in ds]:
        if d in ("bh", "m") and P:  # blind test sets first, then the development benchmarks
            P.append("\\midrule")
        def both(fmt):
            return " / ".join(fmt(e) for e in ESTS)

        def speed(e):
            k = f"v3.{e}.{d}.compat"  # the final method
            if VALS.get(k + ".group.ladder") == "full":
                return "1.00$^\\dagger$"
            return VALS.get(k + ".live.speed", VALS.get(k + ".group.speed", "--") + "$^*$")
        P.append(" & ".join([dlabel(d), both(lambda e: VALS[f"{e}.{d}.compat.fix0.rr"]),
                             both(lambda e: VALS[f"{e}.{d}.unsolv.pairs"]), both(speed),
                             both(lambda e: VALS.get(f"v3.{e}.{d}.compat.group.risk", "--"))]) + " \\\\")
    (TAB / "payoff.tex").write_text("\n".join(P) + "\n", encoding="utf-8")
    for d in ds:  # range over the two estimators, collapsed when equal
        a, b = sorted(int(VALS[f"{e}.{d}.unsolv.time"]) for e in ESTS)
        val(f"{d}.unsolv.time.range", f"{a}" if a == b else f"{a}--{b}")
    (TAB / "headroom.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


# ============================================================================ equal-time comparison
# cheaper setting of each estimator on all correspondences: SC2-PCR fewer seeds (seed ratio), TurboReg fewer cliques
# (K1), MAC its Top-K clique selection (addendum D); (log key, values (a) and (b))
CHEAP = {"sc": ("seeds", ("0.025", "0.01")), "tr": ("k1", ("500", "250")), "mc": ("topk", ("200", "100"))}
def equal_time(logs):
    """Cheaper variants of the estimators vs CAB at equal time (blind held-out scenes: live time; 3DLoMatch: offline, supp)."""
    variants = [("rand", "Uniform sampling"), ("fm1", "FastMAC-style, 1st-order graph"),
                ("fm2", "FastMAC-style, 2nd-order graph"), ("ratio", "Fixed budget, ratio order"),
                ("compat", "Fixed budget, compat.\\ order")]
    lo_rows = {}
    for subset, d in (("v2_blind_hi", "bh"), ("3DLoMatch", "lo")):
        path = LOG_ROOT / f"eqtime_{subset}.jsonl"
        if not path.exists() or (d, "compat") not in logs:
            continue
        eq = {r["pair_id"]: r for r in map(json.loads, open(path))}
        mac_path = LOG_ROOT / f"eqtime_mac_{subset}.jsonl"  # addendum D: MAC's variants, logged separately
        eq_mac = {r["pair_id"]: r for r in map(json.loads, open(mac_path))} if mac_path.exists() else {}
        index = {r["pair_id"]: i for i, r in enumerate(logs[(d, "ratio")])}
        # keep the schedule: every 2nd pair (rand, fm1), every 4th (fm2), every 8th (seeds, k1)
        from acpr.data import load_pairs
        idx_of = {p.pair_id: p.index for p in load_pairs(subset)}
        ids = [pid for pid in eq if idx_of[pid] % 2 == 0]
        val(f"eq.n.{d}", f"{len(ids):,}")
        ratio_logs = {r["pair_id"]: r for r in logs[(d, "ratio")]}
        compat_logs = {r["pair_id"]: r for r in logs[(d, "compat")]}
        for e, E in ESTS_ALL.items():
            if E == "mac" and not all(pid in eq_mac for pid in ids):
                continue  # MAC's variant logs not complete yet
            eqe = eq_mac if E == "mac" else eq
            # CAB outcome per pair: the final method (protocol v3: classifier chosen on the fitting pairs and the
            # hardness gate; compat order, group-conditional), as timed live in live_equal_time_v2_blind_hi_v3.json
            import select_ladder as S
            from acpr import analysis as AN
            sel = json.loads((RB / f"ladder_selection_compat_ext_v2_indoor_fpfh_ctlauto_gate{'_mac' if E == 'mac' else ''}"
                                   ".json").read_text())
            sel = sel[E]["selected"]["mondrian"]
            ladder = B.LADDERS_EXT[sel["ladder"]]
            AN.CLASSIFIER = sel["classifier"]
            lg = {"train": B.load("v2_fit", "budgetc"), "val": B.load("v2_cal", "budgetc"), subset: logs[(d, "compat")]}
            tr, mdps = S.build(lg, E, ladder)
            o = S.policy_outcome(tr[subset], mdps, "mondrian", sel["param"])
            gate = S.fit_gate_for(lg, {"train": "v2_fit", "val": "v2_cal"}, E, sel, (tr, mdps), "budgetc")
            AN.CLASSIFIER = "logit"
            if gate.clf is not None:
                full_o = AN.fixed_stage([B.trajectory_ladder(r, E, (4,)) for r in logs[(d, "compat")]], 0)
                gated = gate.predict(S.load_gate_features(subset, logs[(d, "compat")])[0])
                o = S.gated_outcome(o, full_o, gated, S.gate_eval_charges(logs[(d, "compat")], "budgetc", gate.kind))
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
                        sub = [pid for pid in ids if v in eqe[pid] and (v != "fm2" or idx_of[pid] % 4 == 0)]
                        oks = [eqe[pid][v][str(b)][E]["ok15"] for pid in sub]
                    curve.append((b, 100 * np.mean(oks), sub))
                res[v] = curve
            res["cheap"] = []
            key, params = CHEAP[e]
            sub8 = [pid for pid in ids if key in eqe[pid] and idx_of[pid] % 8 == 0]
            for prm in params:
                res["cheap"].append((prm, 100 * np.mean([eqe[pid][key][prm]["ok15"] for pid in sub8]), sub8))
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
            u = np.array([bool(eqe[p]["rand"]["2000"][E]["ok15"]) for p in ids])
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
                # rows: (group, label, relative time, recall minus the full budget's on the same pairs (pp), risk:
                # share of the pairs the full budget registers that the row loses (%))
                rows = lo_rows.setdefault(e, [])
                fr = lambda sub: 100 * np.mean([full_ok[p] for p in sub])  # noqa: E731
                risk = lambda sub, ok: 100 * np.mean([full_ok[p] and not ok(p) for p in sub])  # noqa: E731
                rows.append((None, "\\method (ours)", sum(cab_s[p] for p in ids) / sum(full_s.values()),
                             100 * np.mean([cab_ok[p] for p in ids]) - fr(ids), risk(ids, lambda p: cab_ok[p])))
                for v, name in variants:
                    for i, b in enumerate(BUDGETS[:4]):
                        sub = res[v][i][2]
                        if v in ("ratio", "compat"):
                            src = ratio_logs if v == "ratio" else compat_logs
                            t = sum(B.trajectory_ladder(src[p], E, (i,))[-1]["s"] for p in sub)
                            ok = lambda p, src=src, i=i: bool(src[p][E][i]["ok15"])  # noqa: E731
                        else:
                            sig = {"rand": None, "fm1": "t_fm1", "fm2": "t_fm2"}[v]
                            t = sum(eqe[p][v][str(b)][E]["s"] + (eqe[p][sig] if sig else 0.0) for p in sub)
                            ok = lambda p, v=v, b=b: bool(eqe[p][v][str(b)][E]["ok15"])  # noqa: E731
                        rows.append((name, f"$N{{=}}{b:,}$".replace(",", "{,}"), t / sum(full_s[p] for p in sub),
                                     res[v][i][1] - fr(sub), risk(sub, ok)))
                for prm, rr, sub in res["cheap"]:
                    t = sum(eqe[p][key][prm]["s"] for p in sub)
                    rows.append(("Fewer seeds (\\SCP) / cliques (TurboReg, MAC)", "(a)" if prm == params[0] else "(b)",
                                 t / sum(full_s[p] for p in sub), rr - fr(sub),
                                 risk(sub, lambda p, prm=prm: bool(eqe[p][key][prm]["ok15"]))))
                val(f"eq.{e}.lo.fullrr", fr(ids), "{:.1f}")
    for e, rows in lo_rows.items():  # cheaper variants that save >= 5 % of the time: smallest loss, smallest risk
        cheaper = [r for r in rows if r[0] is not None and r[2] <= 0.95]
        val(f"eq.{e}.lo.minloss", -max(r[3] for r in cheaper), "{:.1f}")
        val(f"eq.{e}.lo.minrisk", min(r[4] for r in cheaper), "{:.2f}")
        best = max(cheaper, key=lambda r: (r[3], -r[2]))  # the best recall, then the cheapest
        val(f"eq.{e}.lo.best.trel", best[2], "{:.2f}")
        val(f"eq.{e}.lo.best.d", best[3], "{:+.1f}")
        val(f"eq.{e}.lo.best.risk", best[4], "{:.2f}")
        val(f"eq.{e}.lo.cab.trel", rows[0][2], "{:.2f}")
        val(f"eq.{e}.lo.cab.risk", rows[0][4], "{:.2f}")
    if {"sc", "tr"} <= set(lo_rows):  # one column pair per estimator (MAC once its logs are complete)
        L, group = [], None
        ests_lo = [e for e in ("sc", "tr", "mc") if e in lo_rows]
        for parts in zip(*(lo_rows[e] for e in ests_lo)):
            g, name = parts[0][0], parts[0][1]
            if g is not None and g != group:
                L.append(f"\\multicolumn{{{1 + 3 * len(ests_lo)}}}{{@{{}}l}}{{\\textit{{{g}}}}} \\\\")
            group = g
            cells = [c for _, _, t_, d_, r_ in parts for c in (f"{t_:.2f}", f"{d_:+.1f}", f"{r_:.1f}")]
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


SHORT = {"th": "Fresh scenes", "tl": "Fresh, low", "bh": "Held-out", "bl": "Held-out low", "kr": "KITTI raw",
         "fkr": "KITTI raw F", "m": "3DMatch", "lo": "3DLoMatch", "ki": "KITTI", "fm": "3DMatch F", "flo": "3DLoMatch F",
         "fki": "KITTI F"}  # row labels of the teaser's panels (b) and (c)


def teaser_sets():
    """Rows of the teaser's panels (b) and (c): the blind sets of protocol v3, then every earlier test set."""
    return [d for d in BLIND3 + BLIND + ("m", "lo", "ki", "fm", "flo", "fki") if f"v3.sc.{d}.compat.group.risk" in VALS]


def set_rows(ax, sets_, descriptors=False):
    """Row labels of the teaser's panels (b) and (c) (bold: the blind test of the final method), the rules between rows
    and, optionally, a rotated descriptor of each block left of the labels."""
    for i in range(len(sets_) - 1):
        ax.axhline(i + 0.5, color=GRID, lw=0.6, zorder=1)
    for name, rows_ in (("Blind", [i for i, d in enumerate(sets_) if d in BLIND3]),
                        ("Earlier test sets", [i for i, d in enumerate(sets_) if d not in BLIND3])):
        if rows_ and descriptors:  # descriptor of each block of rows, left of the row labels
            ax.annotate(name, xy=(0, np.mean(rows_)), xycoords=("axes fraction", "data"), xytext=(-58, 0),
                        textcoords="offset points", rotation=90, ha="center", va="center", fontsize=FS_LABEL,
                        weight="bold", color=INK)
        if rows_ and name == "Earlier test sets":
            ax.axhline(min(rows_) - 0.5, color=AXIS, lw=0.8, zorder=4)
    ax.set_yticks(range(len(sets_)), [SHORT[d] for d in sets_])
    for lab, d in zip(ax.get_yticklabels(), sets_):
        lab.set_fontweight("bold" if d in BLIND3 else "normal")
    ax.set_ylim(len(sets_) - 0.5, -1.15)  # band above the rows for the column and level labels
    ax.tick_params(axis="y", length=0)


def risk_ledger(ax, sets_):
    """Realized test risk (pairs the full budget registers but the configuration loses) on every test set, for
    CAB with group-conditional certificates against the alternatives that carry no valid guarantee there."""
    if not sets_:
        return [], []
    series = [  # (label, key pattern over estimator e and ordering o, color, marker, filled)
        ("CAB, group-cond. (ours)", "v3.{e}.{d}.{o}.group.risk", BLUE, "o", True),
        ("CAB, marginal cert.", "v3.{e}.{d}.{o}.marg.risk", BLUE, "o", False),
        ("uniform sampling", "eq.{e}.{d}.rand2000.risk", ORANGE, "^", True),
        ("FPFH cert. on FCGF", "{e}.{d}.{o}.group.xfer.risk", RED, "X", True),
    ]
    # every estimator run on a test set: SC2-PCR and TurboReg everywhere, MAC on the indoor FPFH sets (addendum A)
    cab = [num(f"v3.{e}.{d}.{o}.group.risk") for d in sets_ for e in ESTS_ALL for o in PREFIX
           if f"v3.{e}.{d}.{o}.group.risk" in VALS]
    val("cab.risk.max", max(cab), "{:.2f}")
    val("cab.risk.n", str(len(cab)))
    marg = [(num(f"v3.{e}.{d}.{o}.marg.risk"), e, d, o) for d in sets_ for e in ESTS_ALL for o in PREFIX
            if f"v3.{e}.{d}.{o}.marg.risk" in VALS]
    val("marg.risk.max", max(marg)[0], "{:.2f}")
    val("marg.risk.over", str(sum(m[0] > 1.0 for m in marg)))
    val("marg.compat.risk.max", max(m[0] for m in marg if m[3] == "compat"), "{:.2f}")
    # horizontal dot plot: one row per test set; every method at its worst over the estimators and orderings
    XMAX = 14
    ax.axvspan(1.0, XMAX, color=RED, alpha=0.08, lw=0, zorder=0)
    ax.axvline(1.0, color=INK, lw=0.9, ls=(0, (3, 2)), zorder=2)
    for si, (label, pat, col, mk, filled) in enumerate(series):
        xs, ys = [], []
        for i, d in enumerate(sets_):
            vals = [num(k) for k in {pat.format(e=e, d=d, o=o) for e in ESTS_ALL for o in PREFIX} if k in VALS]
            if vals:
                xs.append(max(vals))
                ys.append(i + (-0.14, 0.14, 0.0, 0.0)[si])  # CAB above, its marginal variant below
        if xs:
            ax.plot(xs, ys, mk, ls="none", ms={"^": 6.2, "X": 6.0}.get(mk, 6.6 if filled else 5.8), color=col,
                    mfc=col if filled else "white", mec=col if mk == "X" or not filled else "white",
                    mew={"X": 0.3}.get(mk, 0.6 if filled else 1.3), label=label,
                    zorder=6 if si == 0 else 4, clip_on=False)
    set_rows(ax, sets_)
    ax.tick_params(labelleft=False)  # the row labels are those of panel (b), on its left
    ax.text(0.93, -0.8, "level ε = 1 %", fontsize=FS_LEGEND, color=INK, ha="right", va="center")
    ax.text(1.12, -0.8, "exceeds ε", fontsize=FS_LEGEND, color=INK, ha="left", va="center", style="italic")
    ax.set_xscale("symlog", linthresh=1.0, linscale=1.0)
    ax.set_xlim(-0.05, XMAX)
    ax.set_xticks([0, 0.5, 1, 2, 5, 10])
    ax.set_xticklabels(["0", "0.5", "1", "2", "5", "10"])
    ax.set_xlabel("pairs lost (%)")
    ax.set_title("(c) Risk", loc="left")
    style(ax)
    ax.grid(False, axis="y")
    ax.tick_params(axis="y", length=0)  # style() restores tick marks; the rows carry no ticks
    return ax.get_legend_handles_labels()


def speedup_dots(ax, sets_):
    """Teaser (b): live speed-up of CAB over the full budget on every test set (rows, as in panel (c)), one marker per
    estimator (shape and shade), filled on the CPU and open on the GPU. With FCGF on KITTI the certified method is the
    full budget itself and was not timed. Returns the legend handles and labels."""
    NAVY = "#173f73"
    marks = {"sc": ("o", BLUE_L), "tr": ("s", BLUE), "mc": ("^", NAVY)}
    key = {"CPU": "v3.{e}.{d}.compat.live.speed", "GPU": "gpu.{e}.{d}.v3.speed"}
    XLIM = (0.85, 3.9)
    ax.axvline(1.0, color=INK, lw=0.9, ls=(0, (3, 2)), zorder=2)
    ax.text(1.06, -0.8, "faster →", fontsize=FS_LEGEND, color=INK, ha="left", va="center", style="italic")
    handles = []
    for e, (mk, col) in marks.items():
        for dev in ("GPU", "CPU"):  # CPU drawn on top
            pts = [(num(key[dev].format(e=e, d=d)), i) for i, d in enumerate(sets_) if key[dev].format(e=e, d=d) in VALS]
            if not pts:
                continue
            filled = dev == "CPU"
            h, = ax.plot(*zip(*pts), mk, ls="none", ms={"o": 5.6, "s": 5.0, "^": 5.8}[mk], color=col,
                         mfc=col if filled else "white", mec="white" if filled else col, mew=0.5 if filled else 1.1,
                         zorder=5 if filled else 4, clip_on=False)
            if filled:
                handles.append((h, ENAME[e].replace("$^2$", "²")))
    for i, d in enumerate(sets_):
        sp = [num(key[dev].format(e=e, d=d)) for e in marks for dev in key if key[dev].format(e=e, d=d) in VALS]
        if sp:  # the row's bar: from the full budget to its fastest configuration, so the gain reads as a length
            ax.plot([1.0, max(sp)], [i, i], color=BLUE_L, lw=4.0, alpha=0.45, solid_capstyle="butt", zorder=3)
        else:
            ax.text(1.06, i, "full budget itself", fontsize=FS_CELL, color=MUTED, ha="left", va="center",
                    style="italic")
    set_rows(ax, sets_)
    ax.set_xscale("log")
    ax.set_xlim(*XLIM)
    ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator([1, 1.5, 2, 3]))
    ax.xaxis.set_major_formatter(matplotlib.ticker.FixedFormatter(["1×", "1.5×", "2×", "3×"]))
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlabel("live speed-up")
    ax.set_title("(b) Speed-up of CAB", loc="left")
    style(ax)
    ax.grid(False, axis="y")
    ax.tick_params(axis="y", length=0)
    dev = [matplotlib.lines.Line2D([], [], marker="o", ls="none", ms=5.2, color=INK2, mec="white", mew=0.5),
           matplotlib.lines.Line2D([], [], marker="o", ls="none", ms=5.2, mfc="white", mec=INK2, mew=1.1)]
    return [h for h, _ in handles] + dev, [l for _, l in handles] + ["CPU", "GPU"]


def speedup_grid(ax, sets_):
    """Teaser (b): live speed-up of CAB over the full budget on every test set (rows, as in panel (c)), for each
    estimator on the CPU and on the GPU (columns); the shade darkens with the speed-up (log scale, from 1x). With FCGF
    on KITTI the certified method is the full budget itself and was not timed ("full")."""
    NAVY = "#173f73"
    key = {"CPU": "v3.{e}.{d}.compat.live.speed", "GPU": "gpu.{e}.{d}.v3.speed"}
    cols = [(e, dev) for e in ("sc", "tr", "mc") for dev in ("CPU", "GPU")]
    x0 = [j + 0.3 * (j // 2) for j in range(len(cols))]  # a narrow gap between estimators
    cells = {(i, j): num(key[dev].format(e=e, d=d)) for i, d in enumerate(sets_) for j, (e, dev) in enumerate(cols)
             if key[dev].format(e=e, d=d) in VALS}
    if not cells:
        return
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("cab", ["#f3f7fc", BLUE_L, BLUE, NAVY])
    norm = matplotlib.colors.LogNorm(1.0, max(cells.values()))
    for i, d in enumerate(sets_):
        for j in range(len(cols)):
            sp = cells.get((i, j))
            shade = float(norm(min(max(sp, 1.0), norm.vmax))) if sp is not None else 0.0
            ax.add_patch(matplotlib.patches.Rectangle((x0[j], i - 0.5), 1, 1, fc=cmap(shade), ec="white", lw=1.0,
                                                      zorder=2))
            ax.text(x0[j] + 0.5, i, f"{sp:.2f}" if sp is not None else "full", ha="center", va="center", zorder=3,
                    fontsize=FS_CELL, color="white" if shade > 0.6 else (INK if sp is not None else MUTED),
                    style="normal" if sp is not None else "italic")
    for k, e in enumerate(("sc", "tr", "mc")):
        ax.text(x0[2 * k] + 1.0, -0.8, ENAME[e].replace("$^2$", "²"), ha="center", va="center", fontsize=FS_CELL + 0.6,
                color=INK)
    set_rows(ax, sets_)
    ax.set_xlim(x0[0], x0[-1] + 1)
    ax.set_xticks([x + 0.5 for x in x0], [dev for _, dev in cols])
    ax.tick_params(axis="x", length=0, pad=2, labelsize=FS_CELL)
    for sp_ in ax.spines.values():
        sp_.set_visible(False)
    ax.set_xlabel("live speed-up (×)")
    ax.set_title("(b) Speed-up of CAB", loc="left")


def _equal_time_live(variants):
    paths = [RB / "live_equal_time_v2_blind_hi_v3.json",  # timed with the final method (protocol v3)
             RB / "live_equal_time_v2_blind_hi_v3_mac.json"]  # MAC (addendum D)
    if not paths[0].exists():
        return
    rows = [r for path in paths if path.exists() for r in json.loads(path.read_text())]
    ests = [e for e, E in ESTS_ALL.items() if any(r["est"] == E for r in rows) and f"eq.{e}.bh.cab.rr" in VALS]
    cheap_name = {"sc": "Fewer seeds (ratio 0.025, 0.01)", "tr": "Fewer cliques ($K_1{=}500, 250$)",
                  "mc": "Top-$K$ cliques ($K{=}200, 100$)"}
    L, panels = [], []
    for e in ests:
        E = ESTS_ALL[e]
        rs = [r for r in rows if r["est"] == E]
        t = {k: 1e3 * np.mean([r[k] for r in rs]) for k in rs[0] if isinstance(rs[0][k], float)}
        val(f"eq.{e}.live.n", str(len(rs)))
        val(f"eq.{e}.full.ms", t["full"], "{:,.0f}")
        val(f"eq.{e}.cab.ms", t["cab"], "{:,.0f}")
        val(f"eq.{e}.cab.speed", t["full"] / t["cab"])
        val(f"eq.{e}.fm2.signal.ms", t["fm2_signal"], "{:,.0f}")
        val(f"eq.{e}.fm1.signal.ms", t["fm1_signal"], "{:,.0f}")
        val(f"eq.{e}.rand2000.ms", t["rand@2000"], "{:,.0f}")
        for k in t:  # live time of every fixed budget of every variant, e.g. eq.sc.compat.250.ms
            if "@" in k and k.split("@")[1].isdigit():
                val(f"eq.{e}.{k.split('@')[0]}.{k.split('@')[1]}.ms", t[k], "{:,.0f}")
        cab_t, cab_rr, full_rr = t["cab"], num(f"eq.{e}.bh.cab.rr"), num(f"eq.{e}.bh.full.rr")
        L.append(f"\\multicolumn{{5}}{{@{{}}l}}{{\\textit{{{ENAME[e]}: full budget {t['full']:,.0f}\\,ms, {full_rr:.1f}\\,\\%; "
                 f"\\method {cab_t:,.0f}\\,ms, {cab_rr:.1f}\\,\\%}}}} \\\\")
        key, params = CHEAP[e]
        curves = {}  # variant -> points (time relative to the full budget, recall minus the full budget's, pp)
        cross = {}  # variant -> (its recall at CAB's time minus the full budget's, CAB's lead on the same pairs), pp
        for v, name in [("cheap", cheap_name[e])] + variants:
            if v == "cheap":
                pts = [(t[f"{key}@{prm}"], num(f"eq.{e}.bh.cheap.{prm}.rr")) for prm in params]
                ref_full = num(f"eq.{e}.bh.cheap.{params[0]}.fullrr")
                cab_same = num(f"eq.{e}.bh.cheap.{params[0]}.cab")
            else:
                pts = [(t[f"{v}@{b}"], num(f"eq.{e}.bh.{v}.{b}.rr")) for b in BUDGETS[:4]]
                ref_full = num(f"eq.{e}.bh.{v}.250.fullrr")
                cab_same = num(f"eq.{e}.bh.{v}.250.cab")  # CAB on the same pairs as this variant
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
            curves[v] = [(x / t["full"], y - ref_full) for x, y in (pts if v == "cheap" else curve)]
            if at_cab is not None and v != "cheap":
                cross[v] = (at_cab - ref_full, round(cab_same - at_cab, 1))
        L.append("\\bottomrule" if e == ests[-1] else "\\midrule")
        panels.append((e, curves, cab_t / t["full"], cab_rr - full_rr, cross))
    reach = [num(k) for k in list(VALS) if k.startswith("eq.") and k.endswith(".reach.x")]
    if reach:  # "Match" column: time to reach CAB's recall relative to CAB's time, over every estimator
        val("eq.reach.x.min", min(reach), "{:.1f}")
        val("eq.reach.x.max", max(reach), "{:.1f}")
    (TAB / "equal_time.tex").write_text("\n".join(L) + "\n", encoding="utf-8")

    # ---- the teaser. Layout in inches: (a) one panel per estimator, the same axes in each; (b) and (c) share the
    # rows, labelled left of (b); the band below the panels holds the legends
    W, H, BOT, HGT = 7.0, 2.86, 1.02, 1.62
    AL, AW, AG = 0.42, 0.94, 0.07
    fig = plt.figure(figsize=(W, H))
    ax_eq = [fig.add_axes(((AL + k * (AW + AG)) / W, BOT / H, AW / W, HGT / H)) for k in range(3)]
    ax_b = fig.add_axes((4.14 / W, BOT / H, 1.42 / W, HGT / H))
    ax_c = fig.add_axes((5.66 / W, BOT / H, 1.28 / W, HGT / H))
    colors = {"rand": ORANGE, "fm1": VIOLET, "fm2": MAGENTA, "ratio": GRAY, "compat": BLUE_L, "cheap": INK2}
    legend_name = {"rand": "uniform sampling", "fm1": "FastMAC-style, 1st order",
                   "fm2": "FastMAC-style, 2nd order", "ratio": "fixed budget, ratio order",
                   "compat": "fixed budget, our ordering", "cheap": "fewer seeds / cliques"}
    XLIM = (0.1, 1.5)  # cheaper configurations below a tenth of the full budget's time lie off the panel (Table 3)
    # the recall axis is zoomed on what the comparison reads: every curve where it crosses CAB's time, with room below;
    # the cheapest configurations leave the panel at the bottom (Table 3 lists them all)
    y_lo = 2 * np.floor((min(y for *_, cross in panels for y, _ in cross.values()) - 3) / 2)
    # the speed-up arrow runs above every curve between CAB's time and the full budget's, with its label above it
    y_ar = max([y for _, curves, xc, *_ in panels for c in curves.values() for x, y in c if xc <= x <= XLIM[1]]
               + [0.0]) + 0.9
    y_hi = y_ar + 2.0
    for ax, (e, curves, x_cab, y_cab, cross) in zip(ax_eq, panels):
        for v, c in curves.items():
            if v == "cheap":
                ax.plot(*zip(*c), "v", color=colors[v], ms=5.2, mec="white", mew=0.6, label=legend_name[v], zorder=4)
            else:  # the alternatives slightly recede, so that CAB's star reads first
                ax.plot(*zip(*c), "-o", color=colors[v], lw=1.2, ms=3.0, mec="white", mew=0.4, alpha=0.9,
                        label=legend_name[v], zorder=3)
        # equal time: the guide marks CAB's time; every alternative is marked where it stands there (Table 3, "At
        # CAB"), and the solid segment from CAB's star down to the best of them is CAB's lead at equal time
        ax.axhline(0.0, color=MUTED, lw=0.6, ls=(0, (1, 1.5)), zorder=1)
        ax.plot([x_cab, x_cab], [y_lo, y_ar], color=BLUE, lw=0.8, ls=(0, (3, 2)), zorder=2)  # up to the arrow
        for v, (y, _) in cross.items():
            ax.plot([x_cab], [y], "o", ms=4.4, mfc="white", mec=colors[v], mew=1.3, zorder=6)
        if cross:
            best = max(cross, key=lambda v: cross[v][0])
            ax.plot([x_cab, x_cab], [cross[best][0], y_cab], color=BLUE, lw=2.0, solid_capstyle="butt", zorder=5)
            ax.text(x_cab / 1.22, (cross[best][0] + y_cab) / 2 - 0.15, f"+{cross[best][1]:.1f} pp", ha="right",
                    va="center", fontsize=FS_LEGEND, color=BLUE, weight="bold", zorder=9)
        if ax is ax_eq[0]:
            ax.text(x_cab * 1.07, y_lo + 0.35, "CAB's time", rotation=90, ha="left", va="bottom", fontsize=FS_CELL,
                    color=BLUE, style="italic")
        # the speed-up: an arrow from the full budget's time to CAB's, labelled with the ratio (this timing run)
        ax.plot([1.0, 1.0], [0.0, y_ar], color=INK, lw=0.7, ls=(0, (1, 1.5)), zorder=2)
        ax.annotate("", xy=(x_cab, y_ar), xytext=(1.0, y_ar), zorder=6,
                    arrowprops=dict(arrowstyle="-|>,head_length=0.45,head_width=0.24", fc=BLUE, ec=BLUE, lw=1.6,
                                    shrinkA=0, shrinkB=0))
        ax.text(np.sqrt(x_cab), y_ar + 0.3, f"{1 / x_cab:.2f}×", ha="center", va="bottom", fontsize=FS_LABEL + 0.5,
                color=BLUE, weight="bold", zorder=9)
        ax.plot([1.0], [0.0], "D", color=INK, ms=5.2, mec="white", mew=0.6, label="full budget", zorder=5)
        ax.plot([x_cab], [y_cab], "*", color="white", ms=16, mec="white", mew=0, zorder=7)  # halo over the curves
        ax.plot([x_cab], [y_cab], "*", color=BLUE, ms=12.5, mec=INK, mew=0.6, label="CAB (ours)", zorder=8)
        ax.text(0.05, 0.96, ENAME[e].replace("$^2$", "²"), transform=ax.transAxes, ha="left", va="top",
                fontsize=FS_LABEL, weight="bold", color=INK, zorder=9)  # top left: clear of every curve
        ax.set_xscale("log")
        ax.set_xlim(*XLIM)
        ax.set_ylim(y_lo, y_hi)
        ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(2))
        ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator([0.1, 0.2, 0.5, 1]))
        ax.xaxis.set_major_formatter(matplotlib.ticker.FixedFormatter(["0.1", "0.2", "0.5", "1"]))
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        if ax is ax_eq[0]:
            ax.set_ylabel("recall vs. full budget (pp)")
            ax.set_title("(a) Recall at equal live time", loc="left")
        else:
            ax.tick_params(labelleft=False)
        style(ax)
    for ax in ax_eq[len(panels):]:
        ax.set_visible(False)
    fig.text((AL + 1.5 * AW + AG) / W, (BOT - 0.33) / H, "live time per pair, relative to the full budget (← faster)",
             ha="center", va="center", fontsize=FS_LABEL, color=INK)
    handles = {}
    for ax in ax_eq[:len(panels)]:
        for hh, ll in zip(*ax.get_legend_handles_labels()):
            handles.setdefault(ll, hh)
    sets_ = teaser_sets()
    bh, bl = speedup_dots(ax_b, sets_)
    order = ["CAB (ours)", "full budget", legend_name["compat"], legend_name["ratio"], legend_name["rand"],
             legend_name["cheap"], legend_name["fm1"], legend_name["fm2"]]  # two columns of four
    order = [o for o in order if o in handles]
    rh, rl = risk_ledger(ax_c, sets_)
    # legends in the band below the panels: equal time under (a), risk under (b) and (c)
    y_leg = 0.33 / H
    fig.legend([handles[o] for o in order], order, loc="center", ncol=2, bbox_to_anchor=((AL + 1.5 * AW + AG) / W, y_leg),
               handlelength=1.5, columnspacing=0.9, labelspacing=0.25)
    fig.legend(bh, bl, loc="center", ncol=2, bbox_to_anchor=(4.62 / W, y_leg), handlelength=1.0, labelspacing=0.25,
               columnspacing=0.8)
    fig.legend(rh, rl, loc="center", ncol=1, bbox_to_anchor=(6.18 / W, y_leg), handlelength=1.0, labelspacing=0.25)
    fig.savefig(FIG / "teaser.pdf", facecolor="white")
    plt.close(fig)


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
    for fam, sets_ in (("v2_indoor_fpfh", [("bh", "v2_blind_hi"), ("bl", "v2_blind_lo"), ("m", "3DMatch"),
                                           ("lo", "3DLoMatch")]),
                       ("v2_kitti_fpfh", [("kr", "kitti_raw_blind"), ("ki", "kitti_test")]),
                       ("v2_indoor_fcgf", [("fm", "fcgfown_3DMatch"), ("flo", "fcgfown_3DLoMatch")])):
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
                worst.append((100 * (q(c, 99) / q(f, 99) - 1), f"{ENAME[e]} on {dsent(d)}"))
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
    names = {"v2_blind_hi": "Held-out scenes", "v2_blind_lo": "Held-out, low overlap", "3DMatch": "3DMatch",
             "3DLoMatch": "3DLoMatch", "kitti_raw_blind": "KITTI raw", "kitti_test": "KITTI",
             "fcgfown_3DMatch": "3DMatch (FCGF)", "fcgfown_3DLoMatch": "3DLoMatch (FCGF)",
             "fcgfown_kitti_raw_blind": "KITTI raw (FCGF)", "fcgfown_kitti_test": "KITTI (FCGF)"}
    L, wg, wm, groups, over = [], [], [], 0, []
    wg_f, wm_f, refit = [], [], []
    for dname in ("fpfh_indoor", "fpfh_kitti", "fcgf_indoor", "fcgf_kitti"):
        for e, E in ESTS.items():
            for t, r in data[dname][E].items():
                boot = r.get("bootstrap", [])  # re-fitted controllers: development benchmarks only
                sp = np.array([b["speedup"] for b in boot])
                rk = np.array([b["risk"] for b in boot])
                scene_risk = max(v["risk"] for v in r["scenes"].values())
                wg.append(100 * r["worst_group"])
                wm.append(100 * r["worst_marginal"])
                if dname.startswith("fpfh"):
                    wg_f.append(100 * r["worst_group"])
                    wm_f.append(100 * r["worst_marginal"])
                refit += list(100 * rk)
                for g in r["groups"]:
                    groups += 1
                    if g["risk_group"] > 0.01:
                        over.append((g["risk_group"], g["n"]))
                refit_cells = (f"{sp.mean():.2f}\\X\\,[{sp.min():.2f}, {sp.max():.2f}] & {100 * rk.max():.2f}" if len(sp)
                               else "-- & --")
                L.append(f"{ENAME[e]}, {names[t]} & {100 * r['worst_group']:.2f} & {100 * r['worst_marginal']:.2f} & "
                         f"{100 * scene_risk:.2f} & {refit_cells} \\\\")
    val("ev.worst.group.max", max(wg), "{:.2f}")
    val("ev.worst.marg.max", max(wm), "{:.2f}")
    val("ev.worst.marg.min", min(wm), "{:.2f}")
    val("ev.worst.group.fpfh.max", max(wg_f), "{:.2f}")
    val("ev.worst.marg.fpfh.max", max(wm_f), "{:.2f}")
    val("ev.refit.risk.max", max(refit), "{:.2f}")
    val("ev.refit.n", str(len(refit)))
    val("ev.refit.over", str(sum(x > 1.0 for x in refit)))
    val("ev.groups.n", str(groups))
    val("ev.groups.over", str(len(over)))
    if over:
        r, n = max(over)
        val("ev.groups.over.risk", 100 * r, "{:.2f}")
        val("ev.groups.over.lost", str(int(round(r * n))))
        val("ev.groups.over.n", str(n))
        val("ev.groups.over.step", 100 / n, "{:.1f}")
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
    few = [100 * data[d][E][t][f"0.01_{g}"]["risk"] for d, t in cols for E in ESTS.values() for g in ("1", "2")]
    val("sens.g12.risk.max", max(few), "{:.2f}")  # one or two groups at epsilon = 1 %
    (TAB / "supp_sensitivity.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


def live_agreement():
    """Smallest share of pairs whose live stopping decision equals the offline one, over every live run (every
    estimator, configuration and test set), and over the runs outside KITTI: keys live.agree.minall / .indoor.min."""
    allr, indoor = [], []
    for path in sorted(RB.glob("live_budget_compare_ext*.json")):
        rows = json.loads(path.read_text())
        for est in {r["est"] for r in rows}:
            for sub in {r["subset"] for r in rows if r["est"] == est}:
                rs = [r for r in rows if r["est"] == est and r["subset"] == sub]
                for job in [j for j in rs[0]["run_order"] if j != "full"]:
                    a = float(np.mean([r[job]["stop"] == r[job]["offline_stop"] for r in rs]))
                    allr.append(a)
                    if "kitti" not in sub:
                        indoor.append(a)
    if allr:
        val("live.agree.minall", 100 * min(allr), "{:.0f}")
        val("live.agree.indoor.min", 100 * min(indoor), "{:.1f}")


def mac_results():
    """Protocol v3, addenda A and B (PROTOCOL.md): MAC on every family whose evaluation exists. Offline keys
    mc.{d}.{o}.{cert}.* (CAB without the gate, selection files *_mac.json) and v3.mc.{d}.{o}.{cert}.* (the final method,
    *_ctlauto_gate_mac.json), live keys (live_budget_compare_ext_<family>_v3_mac.json), all in the namespaces of the other
    estimators, and the full-budget recall against the published one. Returns False while no family is complete."""
    sel = {}
    for fam in FAMS:
        paths = {(o, kind): RB / f"ladder_selection{'_compat' if o == 'compat' else ''}_ext_{fam}{sfx}.json"
                 for o in PREFIX for kind, sfx in (("v2", "_mac"), ("v3", "_ctlauto_gate_mac"))}
        if all(q.exists() for q in paths.values()):
            for (o, kind), q in paths.items():
                sel[(fam, o, kind)] = json.loads(q.read_text())["mac"]
    if not sel:
        return False
    names = {"logit": "logistic", "logit_c01": "logistic ($C{=}0.1$)", "poly2": "quadratic logistic",
             "hgb": "boosted trees", None: "none"}
    for fam in {f for f, _, _ in sel}:
        for o in PREFIX:
            cfg = sel[(fam, o, "v3")]["selected"]["mondrian"]
            val(f"v3.mc.{fam}.{o}.clf", names[cfg["classifier"]])
            val(f"v3.mc.{fam}.{o}.gate", names[cfg["gate"]["kind"]])
    for d in MAC_SETS:
        log, fam = DS[d]
        if (fam, "compat", "v3") not in sel:
            continue
        for o in PREFIX:
            n = len(B.load(log, PREFIX[o]))
            for kind, pre in (("v2", ""), ("v3", "v3.")):
                s_ = sel[(fam, o, kind)]
                full = s_["test"][log]["full"]
                for cert, tag in (("group", "mondrian"), ("marg", "marginal")):
                    t = s_["test"][log][tag]
                    k = f"{pre}mc.{d}.{o}.{cert}"
                    val(k + ".rr", 100 * t["rr"], "{:.1f}")
                    val(k + ".full", 100 * full["rr"], "{:.1f}")
                    val(k + ".loss", 100 * t["delta_rr"], "{:.2f}")
                    val(k + ".ub", 100 * t["ub95"], "{:.2f}")
                    val(k + ".p", pfmt(t["mcnemar_p"]))
                    val(k + ".ni", "yes" if t["non_inferior"] else "no")
                    val(k + ".speed", t["speedup"])
                    val(k + ".ops", t["ops_ratio"])
                    val(k + ".risk", 100 * t["risk"], "{:.2f}")
                    val(k + ".nlost", str(int(round(t["risk"] * n))))
                    val(k + ".ms", 1e3 * t["s"], "{:,.0f}")
                    val(k + ".fullms", 1e3 * full["s"], "{:,.0f}")
                    val(k + ".ladder", s_["selected"][tag]["ladder"])
                    if kind == "v3":
                        val(k + ".gated", 100 * t.get("gated", 0) / max(n, 1), "{:.0f}")
    # fidelity of the re-implementation: full-budget recall (the same in both orderings) on the development test sets
    # (FCGF: features of our re-implementation of the network) against the published one
    for (desc, d), pub in MAC_PUBLISHED.items():
        key = f"mc.{'f' if desc == 'fcgf' else ''}{d}.ratio.group.full"
        if key in VALS:
            val(f"fid.mc.{desc}.{d}.ours", num(key), "{:.1f}")
            val(f"fid.mc.{desc}.{d}.gap", pub - num(key), "{:.1f}")
    # live: full budget, CAB without the gate ("budgetc") and the final method ("budgetc+v3") on the same pairs
    agrees, p99, ovh, retimed = [], [], [], 0
    for fam in FAMS:
        path = RB / f"live_budget_compare_ext_{fam}_v3_mac.json"
        if not path.exists():
            continue
        rows = [r for r in json.loads(path.read_text()) if r["est"] == "mac"]
        retimed += sum("stalled" in r for r in rows)
        for d in [d for d in MAC_SETS if DS[d][1] == fam]:
            rs = [r for r in rows if r["subset"] == DS[d][0]]
            if not rs:
                continue
            sc = np.array([r["scene"] for r in rs])
            tf = np.array([r["full"]["s"] for r in rs])
            val(f"mc.{d}.live.n", str(len(rs)))
            val(f"mc.{d}.live.fullms", 1e3 * tf.mean(), "{:,.0f}")
            val(f"mc.{d}.live.fullrr", 100 * np.mean([r["full"]["ok"] for r in rs]), "{:.0f}")
            for pf, k in (("budgetc", f"mc.{d}.compat.live"), ("budgetc+v3", f"v3.mc.{d}.compat.live")):
                ta = np.array([r[pf]["s"] for r in rs])
                sp, lo, hi = boot_ratio(tf, ta, sc, 1)
                val(k + ".speed", sp)
                val(k + ".speedlo", lo)
                val(k + ".speedhi", hi)
                val(k + ".ms", 1e3 * ta.mean(), "{:,.0f}")
                val(k + ".lost", str(sum(r["full"]["ok"] and not r[pf]["ok"] for r in rs)))
                agree = np.mean([r[pf]["stop"] == r[pf]["offline_stop"] for r in rs])
                val(k + ".agree", 100 * agree, "{:.0f}")
                agrees.append(agree)
            tb = np.array([r["budgetc"]["s"] for r in rs])
            ta = np.array([r["budgetc+v3"]["s"] for r in rs])
            sp, lo, hi = boot_ratio(tb, ta, sc, 3)
            val(f"v3.mc.{d}.compat.live.vs2", sp)
            val(f"v3.mc.{d}.compat.live.vs2lo", lo)
            val(f"v3.mc.{d}.compat.live.vs2hi", hi)
            p99.append((100 * (np.quantile(ta, 0.99) / np.quantile(tf, 0.99) - 1), d))
            same = [r for r in rs if r["budgetc+v3"]["stop"] != -1 and r["budgetc+v3"]["stop"] == r["budgetc"]["stop"]]
            if same:
                ovh.append(1e3 * np.median([r["budgetc+v3"]["s"] - r["budgetc"]["s"] for r in same]))
    val("mc.live.retimed", str(retimed))
    if agrees:
        val("mc.live.agree.min", 100 * min(agrees), "{:.0f}")
    if p99:
        w = max(p99)
        val("v3.mc.lat.p99.max", w[0], "{:.0f}")
        val("v3.mc.lat.p99.where", dlabel(w[1]))
    if ovh:
        val("v3.mc.gate.live.overhead.min", min(ovh), "{:.0f}")
        val("v3.mc.gate.live.overhead.max", max(ovh), "{:.0f}")
    return True


def gpu_results(gpu_dir=None, bundle=None):
    """GPU timing (PROTOCOL.md, addendum C) from results/gpu/*.json.gz (the latest file of each phase): per test set and
    estimator, the full budget's mean time, the live speed-ups of CAB without the gate (v2) and of the final method
    with scene-stratified bootstrap intervals, recall and risk on the GPU runs, and the agreement of the GPU stopping
    decisions and full-budget outcomes with the CPU logs (references in gpu_bundle/config.json). Keys gpu.*."""
    import gzip
    gpu_dir = Path(gpu_dir) if gpu_dir else RESULTS_ROOT / "gpu"
    files = sorted(gpu_dir.glob("cab_gpu_results_*.json.gz")) if gpu_dir.exists() else []
    if not files:
        return False
    latest = {}
    for f in files:  # one file per phase (sc2_turbo, mac); the latest of each
        latest[f.name.split("_20")[0]] = f
    cfg = json.loads((Path(bundle) if bundle else PROJECT_ROOT / "gpu_bundle" / "config.json").read_text())
    rows, devices = [], set()
    for f in latest.values():
        d = json.loads(gzip.decompress(f.read_bytes()))
        devices.add(d["device"])
        rows += d["rows"]
    val("gpu.device", " / ".join(sorted(devices)).replace("NVIDIA ", ""))
    agree_all, full_all, L = [], [], []
    for code in [c for c in BLIND3 + BLIND + ("m", "lo", "ki", "fm", "flo") if c in cfg["sets"]]:
        cells, any_e = [dlabel(code)], False
        for e, E in ESTS_ALL.items():
            rs = [r for r in rows if r["set"] == code and r["est"] == E]
            if not rs:
                cells += ["--"] * 3
                continue
            any_e = True
            ref = cfg["sets"][code]["estimators"][E]["reference"]
            idx = {pid: i for i, pid in enumerate(json.loads(json.dumps([r["pair_id"] for r in rs])))}
            sc = np.array([r["scene"] for r in rs])
            tf = np.array([r["full"]["s"] for r in rs])
            k = f"gpu.{e}.{code}"
            val(k + ".n", str(len(rs)))
            val(k + ".fullms", 1e3 * tf.mean(), "{:,.0f}")
            val(k + ".fullrr", 100 * np.mean([r["full"]["ok"] for r in rs]), "{:.1f}")
            for v in ("v2", "v3"):
                ta = np.array([r[v]["s"] for r in rs])
                sp, lo, hi = boot_ratio(tf, ta, sc, 1)
                val(f"{k}.{v}.speed", sp)
                val(f"{k}.{v}.speedlo", lo)
                val(f"{k}.{v}.speedhi", hi)
                val(f"{k}.{v}.rr", 100 * np.mean([r[v]["ok"] for r in rs]), "{:.1f}")
                val(f"{k}.{v}.risk", 100 * np.mean([r["full"]["ok"] and not r[v]["ok"] for r in rs]), "{:.2f}")
                stops = ref[v]["offline_stop"]
                ag = np.mean([r[v]["stop"] == stops[i] for i, r in enumerate(rs)])
                val(f"{k}.{v}.agree", 100 * ag, "{:.0f}")
                agree_all.append(ag)
            fa = np.mean([r["full"]["ok"] == ref["full_ok"][i] for i, r in enumerate(rs)])
            full_all.append(fa)
            cells += [f"{1e3 * tf.mean():,.0f}", f"{num(k + '.v2.speed'):.2f}\\X",
                      f"\\textbf{{{num(k + '.v3.speed'):.2f}\\X}}"]
        if any_e:
            L.append(" & ".join(cells) + " \\\\")
            if code in ("tl", "kr"):  # fresh blind test | blind sets of protocol v2 | development benchmarks
                L.append("\\midrule")
    # final method on the GPU: largest realized risk on the timed samples, and the largest gap between the GPU and the
    # CPU live speed-up (SC2-PCR and TurboReg; MAC's GPU runs are a hybrid with its clique search on the host CPU)
    risks = [(num(f"gpu.{e}.{c}.v3.risk"), e, c) for e in ESTS_ALL for c in cfg["sets"] if f"gpu.{e}.{c}.v3.risk" in VALS]
    if risks:
        w = max(risks)
        val("gpu.v3.risk.max", w[0], "{:.2f}")
        val("gpu.v3.risk.max.where", f"{ENAME[w[1]]} on {dsent(w[2])}")
        val("gpu.v3.risk.max.lost", str(int(round(w[0] / 100 * int(VALS[f"gpu.{w[1]}.{w[2]}.n"])))))
        val("gpu.v3.risk.max.n", VALS[f"gpu.{w[1]}.{w[2]}.n"])
        val("gpu.v3.risk.max.count", str(sum(r[0] == w[0] for r in risks)))
        val("gpu.conds.n", str(len(risks)))
        # the gate on the GPU: conditions where the final method is faster than CAB without the gate
        val("gpu.gate.faster", str(sum(num(f"gpu.{e}.{c}.v3.speed") > num(f"gpu.{e}.{c}.v2.speed") for _, e, c in risks)))
    gaps = [abs(num(f"gpu.{e}.{c}.v3.speed") - num(f"v3.{e}.{c}.compat.live.speed")) for e in ESTS for c in cfg["sets"]
            if f"gpu.{e}.{c}.v3.speed" in VALS and f"v3.{e}.{c}.compat.live.speed" in VALS]
    if gaps:
        val("gpu.cpugap.max", max(gaps), "{:.2f}")
        val("gpu.sets.n", str(len({c for e in ESTS for c in cfg["sets"] if f"gpu.{e}.{c}.v3.speed" in VALS})))
        val("gpu.mc.sets.n", str(len([c for c in cfg["sets"] if f"gpu.mc.{c}.v3.speed" in VALS])))
    if agree_all:
        val("gpu.agree.min", 100 * min(agree_all), "{:.0f}")
        val("gpu.agree.mean", 100 * float(np.mean(agree_all)), "{:.0f}")
        val("gpu.fullagree.min", 100 * min(full_all), "{:.0f}")
    L.append("\\bottomrule")
    (TAB / "supp_gpu.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
    fig_gpu_vs_cpu([c for c in cfg["sets"]])
    return True


def fig_gpu_vs_cpu(codes):
    """Supplementary figure: live speed-up of the final method on the GPU against the CPU, per test set and estimator,
    with the bootstrap intervals of both; the diagonal marks equal speed-ups."""
    marks = {"sc": ("o", BLUE), "tr": ("s", ORANGE), "mc": ("^", PURPLE)}
    fig, ax = plt.subplots(figsize=(3.35, 2.75))
    lo_all, hi_all = [], []
    for e, (mk, col) in marks.items():
        pts = [c for c in codes if f"gpu.{e}.{c}.v3.speed" in VALS and f"v3.{e}.{c}.compat.live.speed" in VALS]
        if not pts:
            continue
        x = np.array([num(f"v3.{e}.{c}.compat.live.speed") for c in pts])
        y = np.array([num(f"gpu.{e}.{c}.v3.speed") for c in pts])
        xe = np.array([[num(f"v3.{e}.{c}.compat.live.speedlo") for c in pts], [num(f"v3.{e}.{c}.compat.live.speedhi") for c in pts]])
        ye = np.array([[num(f"gpu.{e}.{c}.v3.speedlo") for c in pts], [num(f"gpu.{e}.{c}.v3.speedhi") for c in pts]])
        ax.errorbar(x, y, xerr=np.abs(xe - x), yerr=np.abs(ye - y), fmt="none", ecolor=col, elinewidth=0.7, alpha=0.55,
                    zorder=2)
        ax.plot(x, y, mk, ls="none", ms=5.2, color=col, mec="white", mew=0.6, zorder=3,
                label=f"{ENAME[e].replace('$^2$', '²')} ({len(pts)} test sets)")
        lo_all += list(xe[0]) + list(ye[0])
        hi_all += list(xe[1]) + list(ye[1])
    lim = (0.9 * min(lo_all), 1.08 * max(hi_all))
    ax.plot(lim, lim, color=MUTED, lw=0.9, ls=(0, (3, 2)), zorder=1)
    ax.text(lim[1] / 1.04, lim[1] / 1.04, "equal", rotation=45, ha="right", va="bottom", color=INK2,
            fontsize=FS_LEGEND, rotation_mode="anchor")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(*lim)
    ax.set_ylim(*lim)
    ticks = [t for t in (1, 1.5, 2, 3, 4) if lim[0] <= t <= lim[1]]
    for axis in (ax.xaxis, ax.yaxis):
        axis.set_major_locator(matplotlib.ticker.FixedLocator(ticks))
        axis.set_major_formatter(matplotlib.ticker.FixedFormatter([f"{t:g}×" for t in ticks]))
        axis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlabel("speed-up on the CPU (live)")
    ax.set_ylabel("speed-up on the GPU (live)")
    ax.set_aspect("equal")
    style(ax)
    ax.legend(loc="upper left", frameon=False, handletextpad=0.3, borderaxespad=0.2)
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "gpu_vs_cpu.pdf", facecolor="white")
    plt.close(fig)


def v3_results(ds):
    """Protocol v3 (PROTOCOL.md): the final method (CAB with the classifier chosen on the fitting pairs and the
    hardness gate; selection files *_ctlauto_gate) on every test set, the fresh blind test th/tl included.
    Keys v3.{e}.{d}.{o}.{cert}.* (offline, full test set) and v3.{e}.{d}.{o}.live.* (live), the paired live
    comparison with CAB without the gate on the fresh blind test, and the main tables v3_blind.tex / v3_all.tex."""
    sel = {}
    for fam in {DS[d][1] for d in ds}:
        for o in PREFIX:
            path = RB / f"ladder_selection{'_compat' if o == 'compat' else ''}_ext_{fam}_ctlauto_gate.json"
            if path.exists():
                sel[(fam, o)] = json.loads(path.read_text())
    if not sel:
        return []
    names = {"logit": "logistic", "logit_c01": "logistic ($C{=}0.1$)", "poly2": "quadratic logistic",
             "hgb": "boosted trees", None: "none"}
    done = []
    for d in ds:
        log, fam = DS[d]
        if (fam, "compat") not in sel:
            continue
        done.append(d)
        for o in PREFIX:
            for e, E in ESTS.items():
                s_ = sel[(fam, o)][E]
                cfg = s_["selected"]["mondrian"]
                val(f"v3.{e}.{fam}.{o}.clf", names[cfg["classifier"]])
                val(f"v3.{e}.{fam}.{o}.gate", names[cfg["gate"]["kind"]])
                for cert, tag in (("group", "mondrian"), ("marg", "marginal")):
                    t = s_["test"][log][tag]
                    k = f"v3.{e}.{d}.{o}.{cert}"
                    val(k + ".rr", 100 * t["rr"], "{:.1f}")
                    val(k + ".loss", 100 * t["delta_rr"], "{:.2f}")
                    val(k + ".ub", 100 * t["ub95"], "{:.2f}")
                    val(k + ".ni", "yes" if t["non_inferior"] else "no")
                    val(k + ".speed", t["speedup"])
                    val(k + ".ops", t["ops_ratio"])
                    val(k + ".risk", 100 * t["risk"], "{:.2f}")
                    val(k + ".gated", 100 * t.get("gated", 0) / max(len(B.load(log, PREFIX[o])), 1), "{:.0f}")
                    val(k + ".ladder", s_["selected"][tag]["ladder"])
    # live: the final method on every set (jobs "<prefix>+v3"); on the fresh blind test also CAB without the gate
    for fam in {DS[d][1] for d in done}:
        path = RB / f"live_budget_compare_ext_{fam}_v3.json"
        if not path.exists():
            continue
        rows = json.loads(path.read_text())
        for d in [d for d in done if DS[d][1] == fam]:
            for e, E in ESTS.items():
                rs = [r for r in rows if r["est"] == E and r["subset"] == DS[d][0]]
                if not rs:
                    continue
                sc = np.array([r["scene"] for r in rs])
                tf = np.array([r["full"]["s"] for r in rs])
                val(f"v3.{e}.{d}.live.n", str(len(rs)))
                for o, pf in PREFIX.items():
                    ta = np.array([r[pf + "+v3"]["s"] for r in rs])
                    sp, lo, hi = boot_ratio(tf, ta, sc, 1)
                    k = f"v3.{e}.{d}.{o}.live"
                    val(k + ".speed", sp)
                    val(k + ".speedlo", lo)
                    val(k + ".speedhi", hi)
                    val(k + ".agree", 100 * np.mean([r[pf + "+v3"]["stop"] == r[pf + "+v3"]["offline_stop"] for r in rs]),
                        "{:.0f}")
                    if pf in rs[0]:  # CAB without the gate timed on the same pairs: paired ratio of mean times
                        tb = np.array([r[pf]["s"] for r in rs])
                        sp, lo, hi = boot_ratio(tb, ta, sc, 3)
                        val(k + ".vs2", sp)
                        val(k + ".vs2lo", lo)
                        val(k + ".vs2hi", hi)
    # latency of the final method (compat order): 99th-percentile overhead over the full budget, worst over sets; and
    # the gate's live overhead on the fresh blind test: median extra time of CAB over CAB without the gate on pairs
    # that are not gated and stop at the same stage (identical estimator work)
    p99, ovh = [], []
    for fam in {DS[d][1] for d in done}:
        path = RB / f"live_budget_compare_ext_{fam}_v3.json"
        if not path.exists():
            continue
        rows = json.loads(path.read_text())
        for d in [d for d in done if DS[d][1] == fam]:
            for e, E in ESTS.items():
                rs = [r for r in rows if r["est"] == E and r["subset"] == DS[d][0]]
                if not rs:
                    continue
                tf = np.array([r["full"]["s"] for r in rs])
                tc = np.array([r["budgetc+v3"]["s"] for r in rs])
                p99.append((100 * (np.quantile(tc, 0.99) / np.quantile(tf, 0.99) - 1), e, d))
                if "budgetc" in rs[0] and d in BLIND3:
                    same = [r for r in rs if r["budgetc+v3"]["stop"] != -1
                            and r["budgetc+v3"]["stop"] == r["budgetc"]["stop"]]
                    if same:
                        ovh.append(1e3 * np.median([r["budgetc+v3"]["s"] - r["budgetc"]["s"] for r in same]))
    if p99:
        w = max(p99)
        val("v3.lat.p99.max", w[0], "{:.0f}")
        val("v3.lat.p99.where", f"{ENAME[w[1]]} on {dsent(w[2])}")
    if ovh:
        val("v3.gate.live.overhead.min", min(ovh), "{:.0f}")
        val("v3.gate.live.overhead.max", max(ovh), "{:.0f}")
    risks = [num(f"v3.{e}.{d}.{o}.group.risk") for d in done for e in ESTS for o in PREFIX]
    val("v3.risk.max", max(risks), "{:.2f}")
    val("v3.risk.n", str(len(risks)))
    margs = [num(f"v3.{e}.{d}.{o}.marg.risk") for d in done for e in ESTS for o in PREFIX]
    val("v3.marg.risk.max", max(margs), "{:.2f}")
    mc = [num(f"v3.mc.{d}.{o}.group.risk") for d in done for o in PREFIX if f"v3.mc.{d}.{o}.group.risk" in VALS]
    if mc:  # MAC (addendum A): its own ledger, and the ledger over all three estimators
        val("v3.mc.risk.max", max(mc), "{:.2f}")
        val("v3.mc.risk.n", str(len(mc)))
        val("v3.riskall.max", max(risks + mc), "{:.2f}")
        val("v3.riskall.n", str(len(risks) + len(mc)))
        mm = [num(f"v3.mc.{d}.{o}.marg.risk") for d in done for o in PREFIX if f"v3.mc.{d}.{o}.marg.risk" in VALS]
        val("v3.mc.marg.risk.max", max(mm), "{:.2f}")
    lives = [(num(f"v3.{e}.{d}.compat.live.speed"), e, d) for d in done for e in ESTS
             if f"v3.{e}.{d}.compat.live.speed" in VALS]
    if all(d in done for d in BLIND3):
        val("v3.n.blind", f"{sum(len(B.load(DS[d][0], 'budgetc')) for d in BLIND3):,}")
    if lives:
        w = min(lives)
        val("v3.live.min", w[0])
        val("v3.live.min.pct", 100 * (1 / w[0] - 1), "{:.0f}")
        val("v3.live.min.where", f"{ENAME[w[1]]} on {dsent(w[2])}")
        lives += [(num(f"v3.mc.{d}.compat.live.speed"), "mc", d) for d in done if f"v3.mc.{d}.compat.live.speed" in VALS]
        w = min(lives)
        val("v3.liveall.min", w[0])
        val("v3.liveall.min.pct", 100 * (1 / w[0] - 1), "{:.0f}")
        val("v3.liveall.min.where", f"{ENAME[w[1]]} on {dsent(w[2])}")
    # the evaluation was re-run with the gate-cost accounting of select_ladder.gate_eval_charges; the first run (archived)
    # used the signals' times of the feature runs and no prediction cost: largest change of an offline speed-up
    arch = RB / "v3_uncorrected_gate_accounting"
    if arch.exists():
        for cert, tag in (("group", "mondrian"), ("marg", "marginal")):
            diffs = []
            for (fam, o), cur in sel.items():
                old_p = arch / f"ladder_selection{'_compat' if o == 'compat' else ''}_ext_{fam}_ctlauto_gate.json"
                if old_p.exists():
                    old = json.loads(old_p.read_text())
                    diffs += [abs(cur[E]["test"][t][tag]["speedup"] - old[E]["test"][t][tag]["speedup"])
                              for E in cur for t in cur[E]["test"]]
            if diffs:
                val(f"v3.acct.maxdiff.{cert}", max(diffs), "{:.2f}")
    # diagnosis of the gate's live overhead on development pairs (scripts/explore/gate_overhead.py, live_breakdown.py,
    # harness_check.py): median extra time on pairs with identical decisions, the prediction's share, and the effect of
    # limiting the classifier's thread pool to one thread
    ex = RESULTS_ROOT / "explore"
    dev = []
    if (ex / "gate_overhead_sc2.json").exists():
        go = json.loads((ex / "gate_overhead_sc2.json").read_text())
        dev.append(go["v3-v2 same-stop median ms"])
        val("gate.dev.thread.diff", go["v3_1thr-v3 same-stop median ms"], "{:+.0f}")
    if (ex / "harness_check_sc2.json").exists():
        hc = json.loads((ex / "harness_check_sc2.json").read_text())
        dev += [hc["interleaved"]["overhead_ms_median"], hc["deferred"]["overhead_ms_median"]]
    if (ex / "live_breakdown_v3_indoor_fpfh_sc2.json").exists():
        lb = json.loads((ex / "live_breakdown_v3_indoor_fpfh_sc2.json").read_text())
        dev.append(lb["same_stop_median_diff_ms"]["total"])
        val("gate.dev.pred.ms", lb["same_stop_median_diff_ms"]["gate predict"], "{:.0f}")
    if dev:
        val("gate.dev.overhead.min", min(dev), "{:.0f}")
        val("gate.dev.overhead.max", max(dev), "{:.0f}")
    gc = RESULTS_ROOT / "protocol_v3" / "gate_cost.json"
    if gc.exists():
        c = json.loads(gc.read_text())
        val("gate.signals.ms", c["signals_ms"], "{:.1f}")
        val("gate.order.ms", c["order_ms"], "{:.1f}")
        val("gate.pred.logit.ms", c["predict_ms"]["logit"], "{:.1f}")
        val("gate.pred.hgb.ms", c["predict_ms"]["hgb"], "{:.1f}")
    sp = json.loads((RESULTS_ROOT / "protocol_v3" / "indoor_splits.json").read_text())
    val("v3.n.scenes", str(len(sp["blind_scenes"])))
    val("v3.n.dropped", f"{sp['blind_dropped_seen_before']:,}")
    val("v3.n.sampled", f"{sp['blind_sampled']:,}")
    val("v3.n.fitkept", f"{sp['fit_kept_from_v2']:,}")
    val("v3.n.fitnew", f"{sp['fit_new']:,}")

    def cell_live(key_off, key_live):
        return f"{VALS[key_live]}\\X" if key_live in VALS else f"{VALS[key_off]}$\\times^*$"

    # Table 1: the fresh blind test (full budget, CAB without the gate = protocol v2 method, CAB); MAC once its results
    # exist (addendum A)
    ests = [e for e in ESTS_ALL if e in ESTS or f"v3.{e}.th.compat.group.rr" in VALS]
    L = []
    for e in ests:
        L.append(f"\\multicolumn{{11}}{{@{{}}l}}{{\\textit{{{ENAME[e]}}}}} \\\\")
        for lab, kind in (("Full budget (standard)", None), ("\\method without gate (v2)", "v2"),
                          ("\\textbf{\\method (ours)}", "v3")):
            cells = [lab]
            for d in ("th", "tl"):
                if d not in done:
                    cells += ["--"] * 5
                    continue
                if kind is None:
                    cells += [VALS[f"{e}.{d}.compat.group.full"], "--", "1.00\\X", "1.00\\X", "--"]
                    continue
                p = "" if kind == "v2" else "v3."
                k = f"{p}{e}.{d}.compat.group"
                ni = "\\cmark" if VALS[k + ".ni"] == "yes" else "\\xmark"
                lv = cell_live(k + ".speed", f"{p}{e}.{d}.compat.live.speed")
                bold = (lambda x: f"\\textbf{{{x}}}") if kind == "v3" else (lambda x: x)
                cells += [bold(VALS[k + ".rr"]), f"{VALS[k + '.loss']} [{VALS[k + '.ub']}] {ni}", bold(lv),
                          bold(f"{VALS[k + '.ops']}\\X"), VALS[k + ".risk"]]
            L.append(" & ".join(cells) + " \\\\")
        L.append("\\midrule")
    L[-1] = "\\bottomrule"
    (TAB / "v3_blind.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
    # Table 2: every other test set, CAB without the gate vs CAB (live speed-up; CAB's ops, risk and NI)
    L = []
    blocks = [("Blind test sets of protocol v2", [d for d in ("bh", "bl", "kr", "fkr") if d in done]),
              ("Development benchmarks", [d for d in ("m", "lo", "ki", "fm", "flo", "fki") if d in done])]
    for title, sets_ in blocks:
        L.append(f"\\multicolumn{{{1 + 4 * len(ests)}}}{{@{{}}l}}{{\\textit{{{title}}}}} \\\\")
        for d in sets_:
            cells = [dlabel(d)]
            for e in ests:
                k2, k3 = f"{e}.{d}.compat", f"v3.{e}.{d}.compat"
                if k3 + ".group.rr" not in VALS:  # MAC: indoor FPFH only
                    cells += ["--"] * 4
                    continue
                ni = "" if VALS[k3 + ".group.ni"] == "yes" else "$^\\ddagger$"  # not non-inferior
                full_only = VALS[k3 + ".group.ladder"] == "full"
                v2c = "1.00$\\times^\\dagger$" if VALS[k2 + ".group.ladder"] == "full" else \
                    cell_live(k2 + ".group.speed", k2 + ".live.speed")
                v3c = "1.00$\\times^\\dagger$" if full_only else cell_live(k3 + ".group.speed", k3 + ".live.speed")
                cells += [v2c, f"\\textbf{{{v3c}}}{ni}", f"{VALS[k3 + '.group.ops']}\\X", VALS[k3 + ".group.risk"]]
            L.append(" & ".join(cells) + " \\\\")
        L.append("\\midrule")
    L[-1] = "\\bottomrule"
    (TAB / "v3_all.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
    # Supp: every configuration of the final method (group-conditional), both orderings, every test set
    short_clf = {"logistic": "log.", "logistic ($C{=}0.1$)": "log.\\,0.1", "quadratic logistic": "quad.",
                 "boosted trees": "trees", "none": "--"}
    L = []
    for d in [d for d in BLIND3 + BLIND + ("m", "lo", "ki", "fm", "flo", "fki") if d in done]:
        fam = DS[d][1]
        for e in [e for e in ests if f"v3.{e}.{d}.compat.group.rr" in VALS]:
            for o in PREFIX:
                k = f"v3.{e}.{d}.{o}.group"
                lv = VALS.get(f"v3.{e}.{d}.{o}.live.speed")
                lv = "1.00$^\\dagger$" if VALS[k + ".ladder"] == "full" else (f"{lv}\\X" if lv else "--")
                ni = "\\cmark" if VALS[k + ".ni"] == "yes" else "\\xmark"
                L.append(" & ".join([dlabel(d) if (e == "sc" and o == "ratio") else "", ENAME[e] if o == "ratio" else "",
                                     "ratio" if o == "ratio" else "compat.", VALS[k + ".ladder"],
                                     short_clf[VALS[f"v3.{e}.{fam}.{o}.clf"]], short_clf[VALS[f"v3.{e}.{fam}.{o}.gate"]],
                                     VALS[k + ".rr"], f"{VALS[k + '.loss']} [{VALS[k + '.ub']}] {ni}",
                                     f"{VALS[k + '.speed']}\\X", lv, f"{VALS[k + '.ops']}\\X", VALS[k + ".risk"],
                                     VALS[k + ".gated"]]) + " \\\\")
        L.append("\\midrule")
    L[-1] = "\\bottomrule"
    (TAB / "supp_v3_full.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
    # too long for one page: the blind test sets come first in L, then the development benchmarks
    cut = [i for i, r in enumerate(L) if r in ("\\midrule", "\\bottomrule")]
    nb = len([d for d in BLIND3 + BLIND if d in done])
    (TAB / "supp_v3_full_blind.tex").write_text("\n".join(L[:cut[nb - 1]] + ["\\bottomrule"]) + "\n", encoding="utf-8")
    (TAB / "supp_v3_full_dev.tex").write_text("\n".join(L[cut[nb - 1] + 1:]) + "\n", encoding="utf-8")
    return done


def scene_label(s):
    for a, b in (("sun3d-", "SUN3D "), ("bundlefusion-", "BundleFusion "), ("7-scenes-", "7-Scenes "),
                 ("analysis-by-synthesis-", "AbS "), ("-sc_athena_oct_29_2012_scan1_", " ")):
        s = s.replace(a, b)
    return s.replace("_", "\\_")


def v3_evidence():
    """Supp tables of further evidence for the final method (compatibility order, group-conditional certificates):
    the component ablation on the earlier test sets (selection files *_ctlauto: classifier chosen on the fitting pairs;
    *_gate: hardness gate with the logistic controller), and, from results/budget/evidence_v3.json, the fresh blind test
    per scene, the realized risk per difficulty group on every test set, and controllers re-fitted on bootstrap
    resamples of the fitting pairs (development benchmarks). All speed-ups here are offline (full test sets)."""
    variants = (("", "v2"), ("_ctlauto", "clf"), ("_gate", "gate"), ("_ctlauto_gate", "v3"))
    sel = {}
    for fam in ("v2_indoor_fpfh", "v2_kitti_fpfh", "v2_indoor_fcgf", "v2_kitti_fcgf"):
        for sfx, tag in variants:
            path = RB / f"ladder_selection_compat_ext_{fam}{sfx}.json"
            if not path.exists():
                return
            sel[(fam, tag)] = json.loads(path.read_text())
    L, cmp_ = [], {"gate": [], "clf": [], "v3": []}
    for d in ("bh", "bl", "kr", "fkr", "m", "lo", "ki", "fm", "flo", "fki"):
        log, fam = DS[d]
        cells = [dlabel(d)]
        for e, E in ESTS.items():
            r = {}
            for _, tag in variants:
                s_ = sel[(fam, tag)][E]
                t = s_["test"][log]["mondrian"]
                full = s_["selected"]["mondrian"]["ladder"] == "full"
                r[tag] = (1.0 if full else t["speedup"], 100 * t["risk"], full)
                val(f"abl3.{e}.{d}.{tag}.speed", r[tag][0])
                val(f"abl3.{e}.{d}.{tag}.risk", r[tag][1], "{:.2f}")
                sp = "1.00$^\\dagger$" if full else f"{t['speedup']:.2f}\\X"
                cell = f"{sp}\\,({100 * t['risk']:.2f})"
                cells.append(f"\\textbf{{{cell}}}" if tag == "v3" else cell)
            if not all(x[2] for x in r.values()):  # some variant cuts: compare each with CAB without the gate
                for tag in cmp_:
                    cmp_[tag].append((r[tag][0] / r["v2"][0], r[tag][1] - r["v2"][1]))
        L.append(" & ".join(cells) + " \\\\")
        if d == "fkr":
            L.append("\\midrule")
    L.append("\\bottomrule")
    (TAB / "supp_v3_ablation.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
    for tag, xs in cmp_.items():
        val(f"abl3.{tag}.n", str(len(xs)))
        val(f"abl3.{tag}.faster", str(sum(a > 1.005 for a, _ in xs)))
        val(f"abl3.{tag}.slower", str(sum(a < 0.995 for a, _ in xs)))
        val(f"abl3.{tag}.riskier", str(sum(b > 1e-9 for _, b in xs)))
        val(f"abl3.{tag}.gain.max", 100 * (max(a for a, _ in xs) - 1), "{:.0f}")
        val(f"abl3.{tag}.dr.max", max(b for _, b in xs), "{:.2f}")
    path = RB / "evidence_v3.json"
    if not path.exists():
        return
    ev = json.loads(path.read_text())
    # per scene, fresh blind test
    L = []
    for part, log in (("hi", "v3_blind_hi"), ("lo", "v3_blind_lo")):
        title = "Overlap above 30\\,\\%" if part == "hi" else "Overlap 10--30\\,\\%"
        L.append(f"\\multicolumn{{10}}{{@{{}}l}}{{\\textit{{{title}}}}} \\\\")
        rows = ev["per_scene"][log]
        for i in range(len(rows["sc2"])):
            cells = [scene_label(rows["sc2"][i]["scene"]), str(rows["sc2"][i]["n"])]
            for e, E in ESTS.items():
                r = rows[E][i]
                assert r["scene"] == rows["sc2"][i]["scene"]
                cells += [f"{r['speed_v2']:.2f}\\X", f"\\textbf{{{r['speed_v3']:.2f}\\X}}", f"{100 * r['risk_v3']:.2f}",
                          f"{100 * r['gated']:.0f}"]
            L.append(" & ".join(cells) + " \\\\")
        L.append("\\midrule")
        val(f"ev3.scene.{part}.n", str(len(rows["sc2"])))
        for e, E in ESTS.items():
            sv3 = [r["speed_v3"] for r in rows[E]]
            val(f"ev3.scene.{part}.{e}.min", min(sv3))
            val(f"ev3.scene.{part}.{e}.max", max(sv3))
            val(f"ev3.scene.{part}.{e}.faster", str(sum(x > 1.0 for x in sv3)))
            val(f"ev3.scene.{part}.{e}.vs2", str(sum(r["speed_v3"] > r["speed_v2"] for r in rows[E])))
            val(f"ev3.scene.{part}.{e}.risk.max", 100 * max(r["risk_v3"] for r in rows[E]), "{:.2f}")
            val(f"ev3.scene.{part}.{e}.risk.n", str(sum(r["risk_v3"] > 0 for r in rows[E])))
    L[-1] = "\\bottomrule"
    (TAB / "supp_v3_scenes.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
    # per difficulty group (hard, middle, easy: terciles of the explained correspondences after the first stage)
    order = ("v3_blind_hi", "v3_blind_lo", "v2_blind_hi", "v2_blind_lo", "kitti_raw_blind", "3DMatch", "3DLoMatch",
             "kitti_test", "fcgfown_3DMatch", "fcgfown_3DLoMatch")
    code = {DS[d][0]: d for d in DS}
    L, n_groups, over = [], 0, []
    for log in order:
        d = code[log]
        cells = [dlabel(d)]
        for e, E in ESTS.items():
            for g in ev["groups"][log][E]:
                n_groups += 1
                risk = 100 * g["lost"] / g["n"]
                if risk > 1.0:
                    over.append((risk, g["lost"], g["n"], e, d, g["group"]))
                txt = f"{risk:.2f}\\,({g['lost']}/{g['n']})"
                cells.append(f"\\textbf{{{txt}}}" if risk > 1.0 else txt)
        L.append(" & ".join(cells) + " \\\\")
        if log == "v3_blind_lo":
            L.append("\\midrule")
    L.append("\\bottomrule")
    (TAB / "supp_v3_groups.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
    val("ev3.groups.n", str(n_groups))
    val("ev3.groups.over", str(len(over)))
    if over:
        risk, lost, n, e, d, g = max(over)
        val("ev3.groups.over.risk", risk, "{:.2f}")
        val("ev3.groups.over.lost", str(lost))
        val("ev3.groups.over.n", str(n))
        val("ev3.groups.over.where", f"{ENAME[e]} on {dlabel(d)}, {('hard', 'middle', 'easy')[g]} group")
    # re-fitted controllers and gates (10 bootstrap resamples of the fitting pairs), development benchmarks
    rk = []
    for e, E in ESTS.items():
        for d, log in (("m", "3DMatch"), ("lo", "3DLoMatch")):
            sp = [r[log]["speed"] for r in ev["refit"][E]]
            rk += [100 * r[log]["risk"] for r in ev["refit"][E]]
            val(f"ev3.refit.{e}.{d}.min", min(sp))
            val(f"ev3.refit.{e}.{d}.max", max(sp))
            val(f"ev3.refit.{e}.{d}.med", float(np.median(sp)))
        val("ev3.refit.n", str(len(ev["refit"][E])))
    val("ev3.refit.risk.max", max(rk), "{:.2f}")
    val("ev3.refit.over", str(sum(x > 1.0 for x in rk)))


def worst_case():
    """Supp table of the pre-registered worst-case variant (PROTOCOL.md): ladders allowed only if running all their
    stages costs at most (1 + rho) times the full budget on 95 % of the fitting pairs. Compatibility order,
    group-conditional certificate; FPFH test sets; offline speed-up (risk)."""
    cols = [("v2_indoor_fpfh", "v2_blind_hi"), ("v2_indoor_fpfh", "v2_blind_lo"), ("v2_kitti_fpfh", "kitti_raw_blind"),
            ("v2_indoor_fpfh", "3DMatch"), ("v2_indoor_fpfh", "3DLoMatch"), ("v2_kitti_fpfh", "kitti_test")]
    L = []
    for e, E in ESTS.items():
        for rho, sfx, name in ((None, "", "none"), (0.25, "_rho025", "0.25"), (0.10, "_rho010", "0.10")):
            cells = [ENAME[e] if rho is None else "", name]
            ladders = []
            for ds, test in cols:
                path = RB / f"ladder_selection_compat_ext_{ds}{sfx}.json"
                if not path.exists():
                    return
                d = json.loads(path.read_text())[E]
                if test == cols[0][1] or (ds, test) == ("v2_kitti_fpfh", "kitti_raw_blind"):
                    ladders.append(d["selected"]["mondrian"]["ladder"])
                r = d["test"][test]["mondrian"]
                cells.append(f"{r['speedup']:.2f}\\X\\,({100 * r['risk']:.2f})")
                val(f"wc.{e}.{name}.{test}.speed", r["speedup"])
                val(f"wc.{e}.{name}.{test}.risk", 100 * r["risk"], "{:.2f}")
            cells.insert(2, " / ".join(ladders))
            L.append(" & ".join(cells) + " \\\\")
        if e == "sc":
            L.append("\\midrule")
    (TAB / "supp_worst_case.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


def exploration():
    """Supp table of the post-hoc exploration (results/explore; development benchmarks only, blind sets never loaded):
    the controller classifier and the hardness gate, each chosen by cost on the fitting (and, for the gate, the
    calibration) pairs, against the paper's configuration. Offline speed-up (risk %)."""
    ex = RESULTS_ROOT / "explore"
    variants = {"logit": "logistic", "logit_c01": "logistic, $C{=}0.1$", "poly2": "quadratic logistic",
                "hgb": "boosted trees"}
    rows = [("v2_indoor_fpfh", "FPFH indoor", ["3DMatch", "3DLoMatch"]), ("v2_kitti_fpfh", "FPFH KITTI", ["kitti_test"]),
            ("v2_indoor_fcgf", "FCGF indoor", ["fcgfown_3DMatch", "fcgfown_3DLoMatch"])]
    if not all((ex / f"controller_{v}_{ds}_budgetc.json").exists() for v in variants for ds, _, _ in rows):
        return
    L, gains = [], []
    for ds, name, tests in rows:
        R = {v: json.loads((ex / f"controller_{v}_{ds}_budgetc.json").read_text()) for v in variants}
        for e, E in ESTS.items():
            best = min(variants, key=lambda v: R[v][E]["fit_s"])  # chosen on the fitting pairs only
            cell = lambda v, t: f"{R[v][E]['test'][t]['speedup']:.2f}\\X\\,({100 * R[v][E]['test'][t]['risk']:.2f})"
            for t in tests:
                gains.append(R[best][E]["test"][t]["speedup"] / R["logit"][E]["test"][t]["speedup"])
                val(f"ex.{e}.{t}.base", R["logit"][E]["test"][t]["speedup"])
                val(f"ex.{e}.{t}.best", R[best][E]["test"][t]["speedup"])
            risks = [100 * R[best][E]["test"][t]["risk"] for t in tests]
            val(f"ex.{e}.{ds}.chosen", variants[best])
            L.append(" & ".join([f"{name}, {ENAME[e]}", variants[best]] + [cell("logit", t) for t in tests] +
                                ["--"] * (2 - len(tests)) + [cell(best, t) for t in tests] + ["--"] * (2 - len(tests)))
                     + " \\\\")
    allr = [100 * json.loads((ex / f"controller_{v}_{ds}_budgetc.json").read_text())[E]["test"][t]["risk"]
            for v in variants for ds, _, tests in rows for E in ESTS.values() for t in tests]
    val("ex.risk.max", max(allr), "{:.2f}")
    val("ex.gain.min", 100 * (min(gains) - 1), "{:+.0f}")
    val("ex.gain.max", 100 * (max(gains) - 1), "{:+.0f}")
    (TAB / "supp_explore_controller.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
    # hardness gate: classifier chosen by out-of-fold cost on the fitting and calibration pairs
    G = {k: json.loads((ex / f"gate_eval_budgetc_{k}.json").read_text()) for k in ("logit", "hgb")
         if (ex / f"gate_eval_budgetc_{k}.json").exists()}
    if not G:
        return
    L = []
    for e, E in ESTS.items():
        k = max(G, key=lambda k: G[k][E]["fitcal_speed_gate"])
        g = G[k][E]
        cells = [ENAME[e]]
        for t in ("3DMatch", "3DLoMatch"):
            r = g[t]
            cells += [f"{r['speed_cab']:.2f}\\X\\,({100 * r['risk_cab']:.2f})",
                      f"{r['speed_gate']:.2f}\\X\\,({100 * r['risk_gate']:.2f})", f"{100 * r['gated_share']:.0f}"]
            val(f"gate.{e}.{t}.cab", r["speed_cab"])
            val(f"gate.{e}.{t}.gate", r["speed_gate"])
        L.append(" & ".join(cells) + " \\\\")
    (TAB / "supp_explore_gate.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


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
                    pool = by_n[max(by_n)]  # the whole calibration pool (a single certificate)
                    val(k + ".pool", 100 * pool[0]["risk"], "{:.2f}")
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
    for desc in ("fpfh", "fcgf"):  # MAC (addenda A and B), where its results exist
        if any(f"fid.mc.{desc}.{d}.ours" in VALS for d in ("m", "lo", "ki")):
            cells = [f"MAC, {desc.upper()}"]
            for d in ("m", "lo", "ki"):
                k = f"fid.mc.{desc}.{d}.ours"
                cells += [VALS[k], f"{MAC_PUBLISHED[(desc, d)]:.1f}"] if k in VALS else ["--", "--"]
            L.append(" & ".join(cells) + " \\\\")
    for desc in ("fpfh", "fcgf"):  # gap ranges for the text (indoor sets, every estimator with results)
        g = [num(f"fid.{e}.{desc}.{d}.gap") for e in ESTS_ALL for d in ("m", "lo") if f"fid.{e}.{desc}.{d}.gap" in VALS]
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
    mac_results()
    live_agreement()
    v3_results(ds)
    v3_evidence()
    gpu_results()
    anchors_and_headroom(ds, logs)
    equal_time(logs)
    qualitative()
    part_a()
    caps_extras()
    registrability()
    ablations()
    kitti_meta()
    calibration_size()
    fidelity()
    sensitivity()
    worst_case()
    exploration()
    evidence_extra()
    latency()
    lines = ["% generated by scripts/paper_assets.py -- do not edit"]
    lines += [f"\\defval{{{k}}}{{{v}}}" for k, v in sorted(VALS.items())]
    (PAPER / "numbers.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"datasets with CAB results: {ds}; wrote {len(VALS)} values, tables and figures to {PAPER}")


if __name__ == "__main__":
    main()
