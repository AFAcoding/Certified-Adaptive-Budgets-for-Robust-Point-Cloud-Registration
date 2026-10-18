"""Registration as an adaptive search over rotations and translations.

For a rotation R, every putative correspondence (p_i, q_i) votes for the translation
v_i = q_i - R p_i. Inliers of the true pose vote for (almost) the same translation,
so the size of the densest vote cluster scores R, and the cluster gives t.
The search is coarse-to-fine:

  1. Global stage: score a nested, quasi-uniform set of M rotations (Sobol sequence
     mapped to SO(3) with Shoemake's method). The vote tolerance h grows with the
     grid's covering angle so that a grid rotation near the true one still collects
     the inlier votes (the same inflation that branch-and-bound bounds use).
  2. Basin extraction: the best-scoring rotations, after non-maximum suppression in
     pose space, become candidate basins.
  3. Local refinement: annealed least squares (Kabsch) on the votes of each basin,
     shrinking the tolerance from h down to the inlier threshold eps.

Densifying the rotation set and refining more basins are the two ways to spend more
computation. `search_lattice` evaluates every (density, number of basins) state once
so that any adaptive policy can be evaluated offline exactly.

Cost is counted in "correspondence evaluations": transforming one correspondence
under one pose. Scoring one rotation costs N, one refinement iteration costs N, and
one RANSAC hypothesis costs N, which makes the methods directly comparable.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np
from scipy.spatial.transform import Rotation
from scipy.stats import qmc

from acpr.light import kabsch

# ---------------------------------------------------------------------------
# Nested quasi-uniform rotation set
# ---------------------------------------------------------------------------


class RotationGrid:
    """Prefixes of a scrambled Sobol sequence mapped to SO(3) (Shoemake's uniform map)."""

    def __init__(self, n_max: int = 8192, seed: int = 12345):
        m = int(np.ceil(np.log2(n_max)))
        u = qmc.Sobol(d=3, scramble=True, seed=seed).random_base2(m)[:n_max]
        u1, u2, u3 = u[:, 0], u[:, 1], u[:, 2]
        q = np.stack(
            [
                np.sqrt(1 - u1) * np.sin(2 * np.pi * u2),
                np.sqrt(1 - u1) * np.cos(2 * np.pi * u2),
                np.sqrt(u1) * np.sin(2 * np.pi * u3),
                np.sqrt(u1) * np.cos(2 * np.pi * u3),
            ],
            axis=1,
        )
        self.quat = q / np.linalg.norm(q, axis=1, keepdims=True)
        self.R = Rotation.from_quat(self.quat).as_matrix().astype(np.float32)
        self._stats: dict[int, dict] = {}

    def coverage(self, m: int, n_probe: int = 4000, seed: int = 0) -> dict:
        """Distribution of the angle (rad) from a random rotation to the nearest of the first m."""
        if m not in self._stats:
            probes = Rotation.random(n_probe, random_state=seed).as_quat()
            best = np.zeros(n_probe)
            for s in range(0, m, 2048):
                best = np.maximum(best, np.abs(probes @ self.quat[s : min(m, s + 2048)].T).max(axis=1))
            ang = 2 * np.arccos(np.clip(best, -1, 1))
            self._stats[m] = {"p50": float(np.median(ang)), "p90": float(np.quantile(ang, 0.9)),
                              "max": float(ang.max())}
        return self._stats[m]


@lru_cache(maxsize=4)
def get_grid(n_max: int = 8192, seed: int = 12345) -> RotationGrid:
    return RotationGrid(n_max, seed)


# ---------------------------------------------------------------------------
# Translation voting
# ---------------------------------------------------------------------------

_OFFSET = 1 << 20


def _pack(K: np.ndarray) -> np.ndarray:
    """Pack integer cell coordinates (..., 3 along axis -2 or last) into one int64 key."""
    K = K.astype(np.int64) + _OFFSET
    return (K[..., 0, :] << 42) | (K[..., 1, :] << 21) | K[..., 2, :]


def _max_run_length(key_sorted: np.ndarray) -> np.ndarray:
    b, n = key_sorted.shape
    idx = np.arange(n, dtype=np.int32)
    change = np.empty((b, n), dtype=bool)
    change[:, 0] = True
    np.not_equal(key_sorted[:, 1:], key_sorted[:, :-1], out=change[:, 1:])
    start = np.where(change, idx, 0).astype(np.int32)
    np.maximum.accumulate(start, axis=1, out=start)
    return (idx[None, :] - start + 1).max(axis=1)


def vote_scores(Rs: np.ndarray, Pc: np.ndarray, Q: np.ndarray, h: float, chunk: int = 256) -> np.ndarray:
    """Size of the densest translation-vote cell for every rotation (two staggered grids)."""
    PcT = np.ascontiguousarray(Pc.T, dtype=np.float32)  # (3, N)
    QT = np.ascontiguousarray(Q.T, dtype=np.float32)
    inv_h = np.float32(1.0 / h)
    out = np.empty(Rs.shape[0], dtype=np.int32)
    for s in range(0, Rs.shape[0], chunk):
        V = QT[None] - np.matmul(Rs[s : s + chunk], PcT)  # (b, 3, N)
        V *= inv_h
        best = np.zeros(V.shape[0], dtype=np.int32)
        for off in (0.0, 0.5):
            key = _pack(np.floor(V + np.float32(off)))
            key.sort(axis=1)
            np.maximum(best, _max_run_length(key), out=best)
        out[s : s + chunk] = best
    return out


def vote_scores_progressive(Rs: np.ndarray, Pc: np.ndarray, Q: np.ndarray, h: float, keep_min: int,
                            first_frac: float = 0.125, keep_frac: float = 0.25, min_n: int = 32):
    """Progressive successive halving over rotations.

    Correspondences must be sorted by quality (most distinctive first). All M rotations
    are scored on the first n0 = first_frac * N correspondences; the best keep_frac
    survive and the prefix doubles, until survivors are scored on all N. At least
    `keep_min` rotations reach the final round. Eliminated rotations get score -1.

    Returns (scores, cost_in_correspondence_evaluations, first_round_scores).
    """
    N = Pc.shape[0]
    M = Rs.shape[0]
    n = max(min(N, min_n), int(np.ceil(first_frac * N)))
    alive = np.arange(M)
    cost = 0
    first = None
    while True:
        if n >= N or alive.shape[0] <= keep_min:
            s = vote_scores(Rs[alive], Pc, Q, h)
            cost += alive.shape[0] * N
            scores = np.full(M, -1, dtype=np.int32)
            scores[alive] = s
            if first is None:
                first = scores.astype(float)
            return scores, cost, first
        s = vote_scores(Rs[alive], Pc[:n], Q[:n], h)
        cost += alive.shape[0] * n
        if first is None:
            first = np.full(M, np.nan)
            first[alive] = s * (N / n)
        n_keep = max(keep_min, int(np.ceil(alive.shape[0] * keep_frac)))
        if n_keep >= alive.shape[0]:
            n = N
            continue
        top = np.argpartition(-s, n_keep - 1)[:n_keep]
        alive = alive[top]
        n = min(N, 2 * n)


def best_translation(R: np.ndarray, Pc: np.ndarray, Q: np.ndarray, h: float) -> tuple[np.ndarray, int]:
    V = Q - Pc @ R.T
    best_cnt, best_t = -1, np.zeros(3)
    for off in (0.0, 0.5):
        key = _pack(np.floor(V.T / h + off))
        uniq, inv, cnt = np.unique(key, return_inverse=True, return_counts=True)
        j = int(cnt.argmax())
        if cnt[j] > best_cnt:
            best_cnt = int(cnt[j])
            best_t = V[inv.ravel() == j].mean(axis=0)
    return best_t.astype(np.float64), best_cnt


def rot_angle(Ra: np.ndarray, Rb: np.ndarray) -> float:
    c = (np.trace(Ra.T @ Rb) - 1.0) / 2.0
    return float(np.arccos(np.clip(c, -1.0, 1.0)))


# ---------------------------------------------------------------------------
# Local refinement
# ---------------------------------------------------------------------------


def refine(R: np.ndarray, t: np.ndarray, Pc: np.ndarray, Q: np.ndarray, tau0: float, eps: float,
           anneal: float = 0.6, final_iters: int = 2) -> tuple[np.ndarray, np.ndarray, int, int]:
    """Annealed least squares: inliers at a shrinking tolerance, Kabsch re-fit each step."""
    taus = []
    tau = tau0
    while tau > eps:
        taus.append(tau)
        tau *= anneal
    taus += [eps] * final_iters
    P64, Q64 = Pc.astype(np.float64), Q.astype(np.float64)
    R, t = R.astype(np.float64), t.astype(np.float64)
    iters = 0
    for tau in taus:
        res = np.linalg.norm(P64 @ R.T + t - Q64, axis=1)
        iters += 1
        m = res < tau
        if m.sum() < 3:
            break
        T = kabsch(P64[m], Q64[m])
        R, t = T[:3, :3], T[:3, 3]
    res = np.linalg.norm(P64 @ R.T + t - Q64, axis=1)
    return R, t, int((res < eps).sum()), iters + 1


# ---------------------------------------------------------------------------
# The search lattice
# ---------------------------------------------------------------------------


@dataclass
class SearchConfig:
    # 4096/8192 were dropped after validation showed no recall gain beyond 2048 (Section 11)
    densities: tuple = (256, 512, 1024, 2048)
    max_basins: int = 16
    top_t: int = 96  # best-scoring rotations examined for basin extraction
    eps: float = 0.10  # inlier threshold (m)
    h_min: float = 0.20  # minimum vote cell size (m)
    kappa: float = 1.0  # h = max(h_min, kappa * covering_angle * r_p)
    coverage_stat: str = "p50"
    radius_pct: float = 75.0  # percentile of |p - centre| used as r_p
    nms_factor: float = 2.0  # basins closer than nms_factor * covering angle (and < h) are merged
    seed: int = 12345
    progressive: bool = False  # progressive successive-halving voting (needs quality-sorted correspondences)
    first_frac: float = 0.125
    keep_frac: float = 0.25


@dataclass
class Level:
    M: int
    h: float
    sigma: float
    vote_cost: int
    extract_cost: int
    seconds_vote: float
    seconds_extract: float
    vote_top: list  # best vote scores (sorted)
    vote_mean: float
    vote_std: float
    basins: list = field(default_factory=list)  # dicts: T, consensus, vote, iters, cost, seconds


def search_lattice(P: np.ndarray, Q: np.ndarray, center: np.ndarray, cfg: SearchConfig) -> list[Level]:
    grid = get_grid(max(cfg.densities), cfg.seed)
    Pc = (P - center).astype(np.float32)
    N = Pc.shape[0]
    r_p = float(np.percentile(np.linalg.norm(Pc, axis=1), cfg.radius_pct)) if N else 1.0
    levels: list[Level] = []
    for M in cfg.densities:
        sigma = grid.coverage(M)[cfg.coverage_stat]
        h = max(cfg.h_min, cfg.kappa * sigma * r_p)
        t0 = time.perf_counter()
        if cfg.progressive:
            scores, vote_cost, first = vote_scores_progressive(
                grid.R[:M], Pc, Q, h, keep_min=cfg.top_t, first_frac=cfg.first_frac, keep_frac=cfg.keep_frac
            )
            stats_scores = first[np.isfinite(first)]
        else:
            scores = vote_scores(grid.R[:M], Pc, Q, h)
            vote_cost = M * N
            stats_scores = scores
        t_vote = time.perf_counter() - t0

        t0 = time.perf_counter()
        order = np.argsort(-scores, kind="stable")[: cfg.top_t]
        basins_coarse = []
        for rank, i in enumerate(order):
            t, _ = best_translation(grid.R[i].astype(np.float64), Pc, Q, h)
            dup = any(
                rot_angle(grid.R[i], b[0]) < cfg.nms_factor * sigma and np.linalg.norm(t - b[1]) < h
                for b in basins_coarse
            )
            if not dup:
                # rank = how many candidates had to be examined to find this basin
                basins_coarse.append((grid.R[i].astype(np.float64), t, int(scores[i]), rank))
            if len(basins_coarse) >= cfg.max_basins:
                break
        t_extract = time.perf_counter() - t0

        lvl = Level(
            M=M,
            h=h,
            sigma=sigma,
            vote_cost=int(vote_cost),
            extract_cost=len(order) * N,
            seconds_vote=t_vote,
            seconds_extract=t_extract,
            vote_top=np.sort(scores)[::-1][:8].tolist(),
            vote_mean=float(stats_scores.mean()),
            vote_std=float(stats_scores.std()),
        )
        for R0, t0_, vote, rank in basins_coarse:
            ts = time.perf_counter()
            R, t, cons, iters = refine(R0, t0_, Pc, Q, tau0=h, eps=cfg.eps)
            T = np.eye(4)
            T[:3, :3] = R
            T[:3, 3] = t - R @ center
            lvl.basins.append(
                {"T": T, "consensus": cons, "vote": vote, "rank": int(rank), "iters": iters,
                 "cost": iters * N, "seconds": time.perf_counter() - ts}
            )
        levels.append(lvl)
    return levels


# ---------------------------------------------------------------------------
# RANSAC baseline (anytime trajectory)
# ---------------------------------------------------------------------------


def ransac_trajectory(P: np.ndarray, Q: np.ndarray, eps: float = 0.10,
                      checkpoints=(100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000),
                      batch: int = 500, confidence: float = 0.999, edge_ratio: float = 0.9,
                      seed: int = 0) -> dict:
    """Textbook RANSAC on correspondences, logged at hypothesis-count checkpoints.

    Minimal samples are pre-checked for edge-length consistency (as Open3D does) and
    only consistent ones are scored on all N correspondences. The standard adaptive
    stopping point k >= log(1 - confidence) / log(1 - w^3), with w the best inlier
    ratio so far, is recorded too. Each checkpoint stores the pose re-fitted on the
    inliers of the best hypothesis.
    """
    rng = np.random.default_rng(seed)
    N = P.shape[0]
    P64, Q64 = P.astype(np.float64), Q.astype(np.float64)
    best_cnt, best_T = -1, np.eye(4)
    sampled = scored = 0
    traj, adaptive = [], None
    ck = list(checkpoints)
    t_start = time.perf_counter()

    def refit(T):
        m = np.linalg.norm(P64 @ T[:3, :3].T + T[:3, 3] - Q64, axis=1) < eps
        if m.sum() >= 3:
            T = kabsch(P64[m], Q64[m])
        cnt = int((np.linalg.norm(P64 @ T[:3, :3].T + T[:3, 3] - Q64, axis=1) < eps).sum())
        return T, cnt

    while ck and N >= 3:
        idx = rng.integers(0, N, size=(batch, 3))
        sp, sq = P64[idx], Q64[idx]
        dp = np.linalg.norm(sp[:, [0, 0, 1]] - sp[:, [1, 2, 2]], axis=2)
        dq = np.linalg.norm(sq[:, [0, 0, 1]] - sq[:, [1, 2, 2]], axis=2)
        ok = (np.minimum(dp, dq) > edge_ratio * np.maximum(dp, dq)).all(axis=1) & (dp.min(axis=1) > 1e-3)
        sampled += batch
        if ok.any():
            Ts = kabsch(sp[ok], sq[ok])
            res = np.linalg.norm(np.einsum("bij,nj->bni", Ts[:, :3, :3], P64) + Ts[:, None, :3, 3] - Q64[None], axis=2)
            cnt = (res < eps).sum(axis=1)
            scored += int(ok.sum())
            j = int(cnt.argmax())
            if cnt[j] > best_cnt:
                best_cnt, best_T = int(cnt[j]), Ts[j]
        if adaptive is None and best_cnt > 0:
            w = best_cnt / N
            need = np.log(1 - confidence) / np.log(max(1 - w**3, 1e-12))
            if sampled >= need:
                T, cnt_ = refit(best_T)
                adaptive = {"sampled": sampled, "scored": scored, "T": T, "consensus": cnt_,
                            "seconds": time.perf_counter() - t_start}
        while ck and sampled >= ck[0]:
            T, cnt_ = refit(best_T)
            traj.append({"sampled": ck.pop(0), "scored": scored, "T": T, "consensus": cnt_,
                         "seconds": time.perf_counter() - t_start})
    if adaptive is None and traj:
        last = traj[-1]
        adaptive = {**last, "capped": True}
    return {"trajectory": traj, "adaptive": adaptive, "N": N}
