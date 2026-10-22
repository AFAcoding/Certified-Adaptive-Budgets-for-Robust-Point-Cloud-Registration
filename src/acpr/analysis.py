"""Offline evaluation of adaptive computation policies from per-pair logs.

Two anytime estimators are analysed with the same machinery:

* the pose search, run along a fixed schedule of (rotation density, number of
  refined basins) stages whose cumulative cost roughly doubles at each stage;
* RANSAC, observed at hypothesis-count checkpoints.

A stopping policy sees, at every stage, signals computed from the search state
(never ground truth) and decides whether to stop and return the incumbent. Because
the estimators are deterministic given the logs, every policy is evaluated exactly.

Cost unit: correspondence evaluations (CE) = transforming one correspondence under
one pose. Logged wall-clock seconds are reported alongside.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np
from scipy.stats import binom
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from acpr import LOG_ROOT

SCHEDULE = [(0, 1), (0, 4), (1, 4), (2, 4), (3, 8), (4, 8), (5, 16)]
# Candidate schedules (chosen on validation only). Indices are (density level, basins);
# density levels 0..5 = 256, 512, 1024, 2048, 4096, 8192 rotations.
SCHEDULES = {
    "full": SCHEDULE,
    "to2048": [(0, 1), (0, 4), (1, 4), (2, 8), (3, 16)],
    "jump1024": [(0, 1), (0, 4), (2, 4), (3, 16)],
    "jump2048": [(0, 1), (0, 4), (3, 16)],
}
STATIC_GRID = [(d, b) for d in range(6) for b in (1, 2, 4, 8, 16)]
RANSAC_FEATURES = ["c1", "w", "log_c1", "stable", "streak", "stage", "need_ratio", "log_N"]
SEARCH_FEATURES = ["log_c1", "w", "margin", "log_c2", "stable", "streak", "stage", "vote_z", "vote_ratio",
                   "level_gain", "log_N", "from_current"]
SEARCH_FEATURES_VERIFIED = SEARCH_FEATURES + ["ov1", "ov_margin", "score_margin"]
PRE_STATE_FEATURES = ["pre_avail", "pre_deg_max", "pre_deg_p95", "pre_sc2"]
TOP_T = 96


def load_logs(subset: str) -> list[dict]:
    with open(LOG_ROOT / f"search_{subset}.jsonl") as f:
        recs = [json.loads(line) for line in f if line.strip()]
    return [r for r in recs if r.get("search")]


def pose_close(Ta, Tb, deg=5.0, m=0.2) -> bool:
    Ra, Rb = Ta[:3, :3], Tb[:3, :3]
    c = (np.trace(Ra.T @ Rb) - 1) / 2
    ang = np.degrees(np.arccos(np.clip(c, -1, 1)))
    return bool(ang < deg and np.linalg.norm(Ta[:3, 3] - Tb[:3, 3]) < m)


def _basin_T(b) -> np.ndarray:
    return np.asarray(b["T"], dtype=np.float64).reshape(4, 4)


def _extraction_ce(level: dict, n_basins: int, N: int) -> int:
    basins = level["basins"]
    if n_basins <= 0 or not basins:
        return 0
    if n_basins <= len(basins):
        examined = basins[n_basins - 1]["rank"] + 1
    else:
        examined = TOP_T
    return examined * N


# ---------------------------------------------------------------------------
# Static configurations and the search schedule
# ---------------------------------------------------------------------------


def static_outcome(r: dict, d: int, b: int, ov=None, score=None, ce_query: float = 0.0, ce_tree: float = 0.0,
                   n_sub: int = 0) -> dict:
    """Single-shot configuration: score M_d rotations once, refine the top-b basins."""
    lvl = r["search"][d]
    N = r["N"]
    bs = lvl["basins"][:b]
    if not bs:
        return {"ok": False, "ok15": False, "ce": lvl["vote_cost"], "s": lvl["s_vote"]}
    if score is None:
        inc = max(bs, key=lambda x: x["consensus"])
        ver = 0.0
    else:
        k = int(np.argmax([score(r, d, i, ov) for i in range(len(bs))]))
        inc = bs[k]
        ver = ce_tree + len(bs) * n_sub * ce_query
    ce = lvl["vote_cost"] + _extraction_ce(lvl, len(bs), N) + sum(x["cost"] for x in bs) + ver
    frac = (bs[-1]["rank"] + 1) / TOP_T
    s = lvl["s_vote"] + lvl["s_extract"] * min(1.0, frac) + sum(x["s"] for x in bs)
    return {"ok": inc["ok"], "ok15": inc["ok15"], "ce": ce, "s": s}


def basin_score_fn(select: str, ranker=None):
    """Score used to pick the incumbent among refined basins.

    consensus: inlier count (classical); overlap: whole-cloud overlap check;
    product: overlap * log(1 + consensus); learned: ranker probability (see fit_basin_ranker).
    """
    def score(r, d, i, ov):
        b = r["search"][d]["basins"][i]
        c = b["consensus"]
        if select == "consensus":
            return float(c)
        o = ov[d][i]
        if select == "overlap":
            return o + 1e-6 * c
        if select == "product":
            return o * np.log1p(c)
        if select == "learned":
            return float(ranker.predict_proba(np.array([basin_features(r, d, i, ov)]))[0, 1])
        raise ValueError(select)

    return score


def basin_features(r, d, i, ov):
    b = r["search"][d]["basins"][i]
    N = max(r["N"], 1)
    return [np.log1p(b["consensus"]), b["consensus"] / N, ov[d][i], np.log1p(b["vote"]), b["vote"] / N,
            float(i), float(d)]


def precompute_basin_scores(recs, verify, select: str, ranker=None) -> dict:
    """{pair_id: [[score of basin i at level d]]}, vectorised (one model call per pair)."""
    out = {}
    for r in recs:
        ov = verify.get(r["pair_id"]) if verify else None
        if select == "consensus" or ov is None:
            out[r["pair_id"]] = [[float(b["consensus"]) for b in lvl["basins"]] for lvl in r["search"]]
            continue
        if select == "learned":
            feats = [basin_features(r, d, i, ov) for d, lvl in enumerate(r["search"]) for i in range(len(lvl["basins"]))]
            p = ranker.predict_proba(np.array(feats))[:, 1] if feats else np.array([])
            it = iter(p.tolist())
            out[r["pair_id"]] = [[next(it) for _ in lvl["basins"]] for lvl in r["search"]]
            continue
        fn = basin_score_fn(select)
        out[r["pair_id"]] = [[fn(r, d, i, ov) for i in range(len(lvl["basins"]))] for d, lvl in enumerate(r["search"])]
    return out


def lookup_score(table: dict):
    return lambda r, d, i, ov: table[r["pair_id"]][d][i]


def fit_basin_ranker(recs, verify):
    """Logistic model P(basin pose correct | basin features), trained on training-scene basins."""
    X, y = [], []
    for r in recs:
        ov = verify.get(r["pair_id"])
        if ov is None:
            continue
        for d, lvl in enumerate(r["search"]):
            for i, b in enumerate(lvl["basins"]):
                X.append(basin_features(r, d, i, ov))
                y.append(int(b["ok"]))
    return fit_classifier(np.array(X), np.array(y))


def search_trajectory(r: dict, schedule=SCHEDULE, ov=None, score=None, ce_query: float = 0.0,
                      ce_tree: float = 0.0, n_sub: int = 0, pre: dict | None = None) -> list[dict]:
    """State after each stage of the schedule: incumbent outcome, cumulative cost, signals.

    By default the incumbent is the refined basin with the largest consensus. With `ov`
    (per-basin overlap from verify_basins.py) and a `score` function, the incumbent is the
    basin with the best score, and each verification adds n_sub * ce_query CE (plus the
    one-off KD-tree build, ce_tree).
    """
    N = max(r["N"], 1)
    levels = r["search"]
    if score is None:
        score = basin_score_fn("consensus")
    use_ov = ov is not None
    refined: list[tuple[int, int]] = []
    refined_per_level: dict[int, int] = {}
    ext_per_level: dict[int, int] = {}
    visited: set[int] = set()
    ce, secs = 0.0, 0.0
    prev_T, streak, prev_level_best = None, 0, 0
    tree_built = False
    scores: list[float] = []
    out = []
    for s, (d, b) in enumerate(schedule):
        lvl = levels[d]
        if d not in visited:
            visited.add(d)
            ce += lvl["vote_cost"]
            secs += lvl["s_vote"]
        nb = min(b, len(lvl["basins"]))
        have = refined_per_level.get(d, 0)
        for i in range(have, nb):
            ce += lvl["basins"][i]["cost"]
            secs += lvl["basins"][i]["s"]
            refined.append((d, i))
            if use_ov:
                if not tree_built:
                    ce += ce_tree
                    tree_built = True
                ce += n_sub * ce_query
            scores.append(score(r, d, i, ov))
        refined_per_level[d] = max(have, nb)
        ext = _extraction_ce(lvl, nb, N)
        if ext > ext_per_level.get(d, 0):
            ce += ext - ext_per_level.get(d, 0)
            secs += lvl["s_extract"] * (ext - ext_per_level.get(d, 0)) / (TOP_T * N)
            ext_per_level[d] = ext

        if pre is not None and s == 1:  # pre-check runs only for pairs that continue past stage 0
            ce += pre["ce"]
            secs += pre["seconds"]
        if refined:
            sc = np.array(scores)
            k = int(np.argmax(sc))  # earliest maximum
            dd, ii = refined[k]
            inc = levels[dd]["basins"][ii]
            T_inc = _basin_T(inc)
            c1 = int(inc["consensus"])
            c2, s2, ov2 = 0, -np.inf, 0.0
            for (d2, i2), sv in zip(refined, sc):
                if (d2, i2) == (dd, ii):
                    continue
                if pose_close(_basin_T(levels[d2]["basins"][i2]), T_inc, 10.0, 0.3):
                    continue
                c2 = max(c2, int(levels[d2]["basins"][i2]["consensus"]))
                if sv > s2:
                    s2 = sv
                    ov2 = ov[d2][i2] if use_ov else 0.0
            stable = prev_T is not None and pose_close(prev_T, T_inc)
            streak = streak + 1 if stable else 0
            prev_T = T_inc
            ok, ok15 = inc["ok"], inc["ok15"]
            from_current = dd == d
            ov1 = ov[dd][ii] if use_ov else 0.0
            s1 = float(sc[k])
            s_margin = (s1 - s2) / max(abs(s1), 1e-9) if np.isfinite(s2) else 1.0
        else:
            c1 = c2 = 0
            stable, streak, ok, ok15, from_current = False, 0, False, False, False
            ov1 = ov2 = 0.0
            s_margin = 0.0
        lvl_best = max((x["consensus"] for x in lvl["basins"][:nb]), default=0)
        # coarse votes are known after extraction, before refinement (live runs store them separately)
        votes = (lvl.get("coarse_votes") or [x["vote"] for x in lvl["basins"]])[:2]
        out.append(
            {
                "stage": s,
                "ok": bool(ok),
                "ok15": bool(ok15),
                "ce": float(ce),
                "s": float(secs),
                "c1": c1,
                "log_c1": float(np.log1p(c1)),
                "w": c1 / N,
                "margin": (c1 - c2) / max(c1, 1),
                "log_c2": float(np.log1p(c2)),
                "stable": float(stable),
                "streak": float(streak),
                "vote_z": float((lvl["vote_top"][0] - lvl["vote_mean"]) / (lvl["vote_std"] + 1e-9)),
                "vote_ratio": float(votes[0] / max(votes[1], 1)) if len(votes) == 2 else 1.0,
                "level_gain": float(lvl_best - prev_level_best) / max(c1, 1),
                "log_N": float(np.log(N)),
                "from_current": float(from_current),
                "ov1": float(ov1),
                "ov_margin": float(ov1 - ov2),
                "score_margin": float(s_margin),
                "pre_avail": float(pre is not None and s >= 1),
                "pre_deg_max": float(pre["deg_max"]) if pre is not None and s >= 1 else 0.0,
                "pre_deg_p95": float(pre["deg_p95"]) if pre is not None and s >= 1 else 0.0,
                "pre_sc2": float(pre["sc2_max"]) if pre is not None and s >= 1 else 0.0,
            }
        )
        prev_level_best = max(prev_level_best, lvl_best)
    return out


def ransac_trajectory_states(r: dict, confidence: float = 0.999) -> list[dict]:
    N = max(r["N"], 1)
    out, prev_c, streak = [], None, 0
    for s, c in enumerate(r["ransac"]):
        stable = prev_c is not None and c["consensus"] == prev_c
        streak = streak + 1 if stable else 0
        prev_c = c["consensus"]
        w = c["consensus"] / N
        need = np.log(1 - confidence) / np.log(max(1 - w**3, 1e-12)) if w > 0 else 1e9
        out.append(
            {
                "stage": s,
                "k": int(c["k"]),
                "ok": bool(c["ok"]),
                "ok15": bool(c["ok15"]),
                "ce": int(3 * c["k"] + c["scored"] * N),
                "s": float(c["s"]),
                "c1": c["consensus"],
                "log_c1": float(np.log1p(c["consensus"])),
                "w": w,
                "stable": float(stable),
                "streak": float(streak),
                "need_ratio": float(np.log10(max(need, 1) / c["k"])),
                "log_N": float(np.log(N)),
            }
        )
    return out


# ---------------------------------------------------------------------------
# Policies
# ---------------------------------------------------------------------------


@dataclass
class Outcome:
    ok: np.ndarray  # bool per pair
    ok15: np.ndarray
    ce: np.ndarray  # cost per pair (CE)
    s: np.ndarray  # seconds per pair
    stop: np.ndarray  # stage index per pair


def run_policy(trajs: list[list[dict]], stop_fn) -> Outcome:
    ok, ok15, ce, s, stop = [], [], [], [], []
    for tr in trajs:
        k = len(tr) - 1
        for st in tr:
            if stop_fn(st):
                k = st["stage"]
                break
        st = tr[k]
        ok.append(st["ok"])
        ok15.append(st["ok15"])
        ce.append(st["ce"])
        s.append(st["s"])
        stop.append(k)
    return Outcome(np.array(ok), np.array(ok15), np.array(ce, dtype=float), np.array(s), np.array(stop))


def fixed_stage(trajs, k) -> Outcome:
    return run_policy(trajs, lambda st: st["stage"] >= k)


def oracle(trajs) -> Outcome:
    """Stop at the first correct stage; if none is ever correct, stop immediately."""
    out = []
    for tr in trajs:
        k = next((st["stage"] for st in tr if st["ok"]), 0)
        out.append(k)
    return _from_stops(trajs, out)


def _from_stops(trajs, stops) -> Outcome:
    sel = [tr[k] for tr, k in zip(trajs, stops)]
    return Outcome(np.array([x["ok"] for x in sel]), np.array([x["ok15"] for x in sel]),
                   np.array([x["ce"] for x in sel], dtype=float), np.array([x["s"] for x in sel]),
                   np.array(stops))


def rows(trajs, features, label="ok"):
    X = np.array([[st[f] for f in features] for tr in trajs for st in tr], dtype=float)
    y = np.array([st[label] for tr in trajs for st in tr], dtype=int)
    return X, y


def final_labels(trajs) -> np.ndarray:
    """For every stage row: is the incumbent at the *last* stage correct? (value of continuing)"""
    return np.array([tr[-1]["ok"] for tr in trajs for _ in tr], dtype=int)


class _Constant:
    """Fitted on labels of a single class (e.g. every training stage correct): predicts that class."""

    def __init__(self, p):
        self.p = float(p)

    def predict_proba(self, X):
        n = len(X)
        return np.column_stack([np.full(n, 1 - self.p), np.full(n, self.p)])


CLASSIFIERS = ("logit", "logit_c01", "poly2", "hgb")  # controller kinds (protocol v3); "logit" is protocol v2's
CLASSIFIER = "logit"  # kind used by fit_classifier when none is given (set by select_ladder --controller)


def fit_classifier(X, y, C=1.0, kind=None):
    if len(np.unique(y)) < 2:
        return _Constant(np.mean(y))
    kind = kind or CLASSIFIER
    if kind == "logit":
        clf = make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=2000))
    elif kind == "logit_c01":
        clf = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=2000))
    elif kind == "poly2":
        from sklearn.preprocessing import PolynomialFeatures
        clf = make_pipeline(StandardScaler(), PolynomialFeatures(2, include_bias=False), StandardScaler(),
                            LogisticRegression(C=0.1, max_iter=5000))
    elif kind == "hgb":
        from sklearn.ensemble import HistGradientBoostingClassifier
        clf = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=300, l2_regularization=1.0,
                                             random_state=0)
    else:
        raise ValueError(f"unknown classifier {kind}")
    clf.fit(X, y)
    return clf


def attach_scores(trajs, features, clf_now, clf_final=None):
    for tr in trajs:
        X = np.array([[st[f] for f in features] for st in tr], dtype=float)
        p = clf_now.predict_proba(X)[:, 1]
        q = clf_final.predict_proba(X)[:, 1] if clf_final is not None else np.full(len(tr), np.nan)
        for st, pi, qi in zip(tr, p, q):
            st["p_now"] = float(pi)
            st["p_final"] = float(qi)


def threshold_policy(trajs, key, thr) -> Outcome:
    return run_policy(trajs, lambda st: st[key] >= thr)


def ransac_hybrid_policy(recs, rtrajs, gam) -> Outcome:
    """Drop-in improvement of RANSAC: classical stopping rule OR certified give-up.

    The classical rule (hypotheses >= log(1-p)/log(1-w^3)) is kept unchanged; in
    addition, at each checkpoint before the classical stop, RANSAC gives up if the
    predicted probability that the final result will be correct is below gam.
    """
    ok, ok15, ce, s, stop = [], [], [], [], []
    for r, tr in zip(recs, rtrajs):
        a = r["ransac_adaptive"]
        k_cls = a["k"]
        give = next((st for st in tr if st["k"] < k_cls and st["p_final"] < gam), None)
        if give is not None:
            ok.append(give["ok"]); ok15.append(give["ok15"]); ce.append(give["ce"]); s.append(give["s"])
            stop.append(give["stage"])
        else:
            ok.append(a["ok"]); ok15.append(a["ok15"]); ce.append(3 * a["k"] + a["scored"] * r["N"]); s.append(a["s"])
            stop.append(-1)
    return Outcome(np.array(ok), np.array(ok15), np.array(ce, float), np.array(s), np.array(stop))


PRE_FEATURES = ["pre_deg_max", "pre_deg_p95", "pre_deg_mean", "pre_sc2", "log_N"]


def load_precheck(subset: str) -> dict:
    path = LOG_ROOT / f"precheck_{subset}.jsonl"
    if not path.exists():
        return {}
    with open(path) as f:
        return {v["pair_id"]: v for v in (json.loads(x) for x in f if x.strip())}


def pre_vector(r, pre) -> list:
    v = pre[r["pair_id"]]
    return [v["deg_max"], v["deg_p95"], v["deg_mean"], v["sc2_max"], float(np.log(max(r["N"], 1)))]


def gate_rows(recs, rtrajs, pre, k0):
    """Features at the gate point: pre-check statistics + RANSAC state at checkpoint k0."""
    X = []
    for r, tr in zip(recs, rtrajs):
        st = next(s for s in tr if s["k"] >= k0)
        X.append(pre_vector(r, pre) + [st["log_c1"], st["w"]])
    return np.array(X, dtype=float)


def ransac_gate_policy(recs, rtrajs, gate_p, gam, k0) -> Outcome:
    """Classical RANSAC with a registrability gate at k0 hypotheses.

    Pairs that the classical rule stops before k0 are untouched (no overhead). Otherwise
    the pre-check is run (its cost is added) and RANSAC gives up if P(success) < gam,
    returning its incumbent at k0.
    """
    ok, ok15, ce, s, stop = [], [], [], [], []
    for r, tr, p in zip(recs, rtrajs, gate_p):
        a = r["ransac_adaptive"]
        cls_ce = 3 * a["k"] + a["scored"] * r["N"]
        if a["k"] <= k0:
            ok.append(a["ok"]); ok15.append(a["ok15"]); ce.append(cls_ce); s.append(a["s"]); stop.append(-1)
            continue
        st = next(x for x in tr if x["k"] >= k0)
        pre_ce = r["_pre_ce"]
        if p < gam:
            ok.append(st["ok"]); ok15.append(st["ok15"]); ce.append(st["ce"] + pre_ce); s.append(st["s"]); stop.append(st["stage"])
        else:
            ok.append(a["ok"]); ok15.append(a["ok15"]); ce.append(cls_ce + pre_ce); s.append(a["s"]); stop.append(-1)
    return Outcome(np.array(ok), np.array(ok15), np.array(ce, float), np.array(s), np.array(stop))


def accept_or_giveup_policy(trajs, lam, gam) -> Outcome:
    """Stop when confident the incumbent is right (p_now >= lam) or when continuing looks hopeless."""
    return run_policy(trajs, lambda st: st["p_now"] >= lam or st["p_final"] < gam)


# ---------------------------------------------------------------------------
# Markov decision process controller
# ---------------------------------------------------------------------------


class MDPController:
    """Finite-horizon MDP over (stage, bin(p_now), bin(p_final)) states.

    Transition probabilities, immediate success probabilities and stage costs are
    estimated from training trajectories (Dirichlet-smoothed counts); the policy is
    solved by backward induction for a cost weight lambda (reward = success - lambda * CE).
    """

    def __init__(self, train_trajs, n_now=5, n_final=3, alpha=0.5):
        self.n_now, self.n_final = n_now, n_final
        p = np.array([st["p_now"] for tr in train_trajs for st in tr])
        q = np.array([st["p_final"] for tr in train_trajs for st in tr])
        self.edges_now = np.unique(np.quantile(p, np.linspace(0, 1, n_now + 1)[1:-1]))
        self.edges_final = np.unique(np.quantile(q, np.linspace(0, 1, n_final + 1)[1:-1]))
        self.n_now = len(self.edges_now) + 1
        self.n_final = len(self.edges_final) + 1
        H = len(train_trajs[0])
        S = self.n_now * self.n_final
        self.H, self.S = H, S
        succ = np.zeros((H, S))
        cnt = np.zeros((H, S))
        trans = np.full((H, S, S), alpha)
        dcost = np.zeros((H, S))
        for tr in train_trajs:
            z = [self.state(st) for st in tr]
            for h in range(H):
                succ[h, z[h]] += tr[h]["ok"]
                cnt[h, z[h]] += 1
                if h + 1 < H:
                    trans[h, z[h], z[h + 1]] += 1
                    dcost[h, z[h]] += tr[h + 1]["ce"] - tr[h]["ce"]
        prior = (succ.sum() + 1) / (cnt.sum() + 2)
        self.r = (succ + prior) / (cnt + 1)  # smoothed P(success | stop now)
        self.P = trans / trans.sum(axis=2, keepdims=True)
        mean_dc = np.array([dcost[h].sum() / max(cnt[h].sum(), 1) for h in range(H)])
        self.dc = np.where(cnt > 0, dcost / np.maximum(cnt, 1), mean_dc[:, None])

    def state(self, st) -> int:
        i = int(np.searchsorted(self.edges_now, st["p_now"], side="right"))
        j = int(np.searchsorted(self.edges_final, st["p_final"], side="right"))
        return i * self.n_final + j

    def solve(self, lam: float) -> np.ndarray:
        stop = np.zeros((self.H, self.S), dtype=bool)
        V = self.r[-1].copy()
        stop[-1] = True
        for h in range(self.H - 2, -1, -1):
            cont = -lam * self.dc[h] + self.P[h] @ V
            stop[h] = self.r[h] >= cont
            V = np.where(stop[h], self.r[h], cont)
        return stop

    def policy(self, trajs, lam) -> Outcome:
        table = self.solve(lam)
        return run_policy(trajs, lambda st: bool(table[st["stage"], self.state(st)]))


# ---------------------------------------------------------------------------
# Risk control (Learn-then-Test with an exact binomial test)
# ---------------------------------------------------------------------------


def ltt_select(params, outcomes_cal: list[Outcome], ref_ok: np.ndarray, eps: float, delta: float):
    """Fixed-sequence testing over `params` (ordered conservative -> aggressive).

    Loss per pair: the reference solves it and the policy does not. H0: risk > eps.
    Returns the index of the most aggressive parameter certified before the first failure.
    """
    chosen = None
    pvals = []
    for i, out in enumerate(outcomes_cal):
        n = len(ref_ok)
        k = int(np.sum(ref_ok & ~out.ok))
        p = float(binom.cdf(k, n, eps))
        pvals.append(p)
        if p <= delta:
            chosen = i
        else:
            break
    return chosen, pvals


# ---------------------------------------------------------------------------
# Metrics and statistics
# ---------------------------------------------------------------------------


def scene_rr(ok: np.ndarray, scenes: np.ndarray) -> float:
    """Registration recall averaged over scenes (official 3DMatch convention)."""
    return float(np.mean([ok[scenes == sc].mean() for sc in np.unique(scenes)]))


def stratified_bootstrap(stat_fn, scenes: np.ndarray, B: int = 2000, seed: int = 0) -> np.ndarray:
    """Bootstrap distribution of stat_fn(idx), resampling pairs within each scene."""
    rng = np.random.default_rng(seed)
    groups = [np.flatnonzero(scenes == sc) for sc in np.unique(scenes)]
    vals = np.empty(B)
    for i in range(B):
        idx = np.concatenate([g[rng.integers(0, len(g), len(g))] for g in groups])
        vals[i] = stat_fn(idx)
    return vals


def mcnemar_exact(a: np.ndarray, b: np.ndarray) -> float:
    """Two-sided exact McNemar p-value for paired binary outcomes."""
    n01 = int(np.sum(a & ~b))
    n10 = int(np.sum(~a & b))
    n = n01 + n10
    if n == 0:
        return 1.0
    return float(min(1.0, 2 * binom.cdf(min(n01, n10), n, 0.5)))


def upper_hull(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Upper-left frontier (cost, rr): best rr reachable at each cost by mixing configurations."""
    pts = sorted(set(points))
    hull: list[tuple[float, float]] = []
    for p in pts:
        if hull and p[1] <= hull[-1][1]:
            continue
        while len(hull) >= 2:
            (x1, y1), (x2, y2) = hull[-2], hull[-1]
            if (y2 - y1) * (p[0] - x1) <= (p[1] - y1) * (x2 - x1):
                hull.pop()
            else:
                break
        hull.append(p)
    return hull


def hull_value(hull, cost: float) -> float:
    """RR of the static frontier at a given mean cost (linear interpolation = random mixing)."""
    if cost <= hull[0][0]:
        return hull[0][1]
    for (x1, y1), (x2, y2) in zip(hull[:-1], hull[1:]):
        if x1 <= cost <= x2:
            return y1 + (y2 - y1) * (cost - x1) / (x2 - x1)
    return hull[-1][1]
