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

1. **Outdoor split (2026-10-19, before any scan of these drives was downloaded or processed).** The 145 KITTI raw
   drives outside odometry sequences 0-10 yield 1,332 pairs under FCGF's rule (49 drives move far enough), not the
   2,400 the split above assumed. Denser pairings would create near-duplicate pairs, which a binomial certificate
   must not see. Amended split:
   - FPFH: calibration on the odometry validation pairs (180) and the held-out odometry training pairs (1,058),
     which were never used for design (FPFH is not learned, so FCGF's training does not matter); blind test: all
     1,332 raw-drive pairs.
   - FCGF: the raw drives, permuted with `numpy.random.default_rng(20261019)`, go to FCGF calibration until it holds
     at least 1,100 pairs (FCGF needs calibration data it was not trained on); the remaining drives form the FCGF
     blind test. The odometry test pairs remain the development benchmark.

# Evaluation protocol v3 (pre-registered 2026-10-21)

Frozen before any v3 split was generated and before any v3 test pair was processed. Reason: after the v2 blind
evaluation, exploration on development data only (`results/explore/SUMMARY.md`) found two improvements. Because they
were found after the v2 blind sets had been seen, their claim needs a fresh blind test.

## Method v3 (frozen, `scripts/select_ladder.py --controller auto --gate`)
CAB exactly as in v2, plus two choices made without test data:
1. **Controller classifier.** For each dataset, estimator and ordering, the stopping controller (p_now, p_fin) uses
   one of: logistic regression C=1 (v2), logistic regression C=0.1, quadratic logistic regression (degree-2
   features, C=0.1), gradient-boosted trees (`acpr.analysis.fit_classifier` kinds `logit`, `logit_c01`, `poly2`,
   `hgb`). The kind is the one whose chosen candidate (step 1 of choose-then-certify, out-of-fold) has the lowest
   mean cost on the fitting pairs. Only the chosen candidate is certified, as in v2.
2. **Hardness gate** (`acpr.gate`). Pre-estimation signals of the correspondences predict whether CAB would cost
   more than the full budget; predicted-hard pairs run the full budget directly. Classifier (logistic or boosted
   trees) and threshold minimise the 5-fold out-of-fold total cost on the fitting and calibration pairs. The gate
   can only remove losses, so the certificate is unchanged.
Everything else (ladders, families, eps, delta, G, dominance rule, both orderings, marginal certificate) as in v2.

## Data v3 (indoor, FPFH)
- The 53 v2 fitting scenes are permuted with `numpy.random.default_rng(20261021)` and assigned to the v3 blind test
  until it holds at least 3,500 pairs with overlap > 0.1. Blind test: a random sample of 3,000 of them (seed 1),
  reported above and below 30 % overlap.
- v3 fitting pairs: the v2 fitting pairs outside the v3 blind scenes, topped up to 1,000 with random pairs (seed 3)
  of the remaining fitting scenes. Calibration: the v2 calibration pairs, unchanged.
- No pair of the v3 blind scenes has ever been evaluated as a test pair; pairs of these scenes that served as v2
  fitting pairs (and in the exploration as fitting data) are removed from fitting.
- Outdoor and FCGF: no fresh data exist. Method v3 is also evaluated on every v2 test set; those results are
  reported as non-blind for v3.

## Evaluation v3
- The v3 blind test is evaluated once, for method v2 and method v3 (both re-fitted on the v3 fitting pairs), after
  all selections are written to disk. Live timing: 300 random v3 blind pairs, every configuration on the same pairs.
- The paper reports method v3 as the main method only if it is non-inferior to the full budget and within the risk
  level on the v3 blind test; otherwise v2 remains the main method and v3 is reported as a negative result.

## Deviations v3

1. **Strictly unseen subset (2026-10-21, after the v3 split was generated and before any v3 test pair was logged or
   processed).** A leakage check found that 377 of the 3,000 v3 blind pairs had appeared in earlier logs as
   fitting or training pairs (never as test pairs): 237 v2 fitting pairs (also fitting data of the exploration), and
   pairs of the first protocol's training sample and of the pose-search training logs. The v3 controllers are
   re-fitted without them. The pre-registered analysis on all 3,000 pairs stays primary; in addition, every v3 blind
   result is reported on the 2,623 pairs that appear in no earlier log (1,976 above and 647 below 30 % overlap),
   and any difference in conclusions is stated.
