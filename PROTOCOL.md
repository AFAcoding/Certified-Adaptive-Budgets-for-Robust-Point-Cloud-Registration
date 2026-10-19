# Evaluation protocol v2 (pre-registered)

Frozen on 2026-10-19, before any of the new data below was downloaded, generated or looked at. Every rule here is
fixed; deviations, if any, are listed at the end with their reason. The paper's blind claims rest only on the blind
test sets, each evaluated exactly once under this protocol.

## Why a second protocol

The first protocol had three problems that no re-analysis can fix:
1. the 3DMatch validation scenes served both the design of the method and its certification;
2. the 3DMatch/3DLoMatch and KITTI odometry test sets were evaluated under several versions of the method;
3. FCGF features exist only for the test sets, so FCGF fitting and calibration used held-out test pairs.

Protocol v2 adds fresh data for calibration and testing, computes FCGF features for every split, and keeps the
previously seen test sets only as development benchmarks for comparability.

## Method (unchanged, frozen)

CAB exactly as implemented in `scripts/select_ladder.py` at this commit: two-pass compatibility ordering
(P = 500, m = 100), budgets {250, 500, 1000, 2000, 4000}, the 15 candidate ladders and the full budget, the
controller features and the three policy families, risk level eps = 1 %, delta = 0.1, G = 3 difficulty groups
(terciles of the first-stage observable on the fitting pairs), choose-then-certify (5-fold out-of-fold controller
scores on the fitting pairs, loss tolerance matched to the calibration set's size), the dominance rule (a certified
policy that never stops early runs the full budget). Both orderings (ratio, compatibility) and the marginal
certificate are evaluated, as before.

Pre-registered variant, reported in the supplementary: a worst-case bound rho in {0.10, 0.25}. A ladder is a
candidate only if running all its stages costs at most (1 + rho) times the full budget on 95 % of the fitting pairs.

## Data

### Indoor, FPFH (3DMatch training scenes; FPFH is not learned, so any scene is fair)
- The 75 training scenes are permuted with `numpy.random.default_rng(20261019)`. Scenes are assigned in this order to
  the blind test until it holds at least 3,500 pairs with overlap > 0.1, then to calibration until it holds at least
  3,500 such pairs; the remaining scenes are the fitting scenes.
- Pairs with overlap <= 0.1 are excluded everywhere. Blind test: a random subsample of 3,000 pairs (seed 1); it is
  reported in two parts, overlap > 0.3 (3DMatch-like) and 0.1-0.3 (3DLoMatch-like). Calibration: a random subsample
  of 3,000 pairs (seed 2). Fitting: the existing 1,000-pair training sample restricted to fitting scenes, topped up to
  1,000 with a random sample (seed 3) of the other fitting-scene pairs.
- Development benchmarks: the official 3DMatch (1,623) and 3DLoMatch (1,781) test pairs, with the same calibration.
- The validation scenes (design data) are not used.

### Indoor, FCGF (official 3DMatch 5 cm weights; FCGF was trained on all 3DMatch training scenes)
- Features computed with `acpr.fcgf_net` (verified identical to the released features, `scripts/verify_fcgf.py`).
- Fitting: the indoor FPFH fitting pairs. Calibration: the 1,331 validation-scene pairs (not seen by FCGF's training;
  their FCGF outcomes were never looked at). Development benchmarks: official 3DMatch and 3DLoMatch test pairs.
- No blind indoor FCGF test exists: FCGF has seen every training scene, and the test scenes were seen by us.

### Outdoor, FPFH and FCGF (KITTI)
- Fitting: the existing 300 KITTI odometry training pairs (sequences 0-5).
- New data: the KITTI raw drives that are not part of odometry sequences 0-10 (neither FCGF nor this project has
  used them). Scans are fetched by HTTP range requests from the official archives. Pairs follow FCGF's rule (start
  at the first frame, partner = the frame before the first one more than 10 m away, next start = partner + 1), with
  poses from the drive's OXTS (GPS/IMU) data refined by point-to-point ICP exactly as in FCGF (0.05 m voxels, 0.2 m
  correspondence distance, 200 iterations). A pair is dropped if ICP moves the GPS/IMU pose by more than 1 m or 5
  degrees (failed refinement); the number dropped is reported.
- The eligible drives are permuted with `numpy.random.default_rng(20261019)`; drives are assigned to the blind test
  until it holds at least 800 pairs, then to calibration until it holds at least 1,600 pairs.
- Development benchmark: the 555 KITTI odometry test pairs (sequences 8-10).
- FPFH: 0.3 m voxel grid as before. FCGF: official KITTI v0.3 32-dim weights on raw scans quantised at 0.3 m.

## Evaluation
- Success: RE <= 15 deg and TE <= 30 cm indoors, RE <= 5 deg and TE <= 60 cm outdoors.
- Each blind test set is evaluated once, for every configuration listed above, after all selections are written to
  disk; nothing is changed afterwards. Live timing: 300 random test pairs per set, as before.
- Cost: live wall-clock time and the analytic operation count.

## Deviations
(none yet)
