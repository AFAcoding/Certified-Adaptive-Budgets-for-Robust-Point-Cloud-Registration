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

1. **No leakage (2026-10-21, after the v3 split was generated and before any v3 test pair was logged or processed).**
   A leakage check found that 377 of the 3,000 sampled v3 blind pairs had appeared in earlier logs as fitting or
   training pairs (never as test pairs): 237 v2 fitting pairs (also fitting data of the exploration), and pairs of
   the first protocol's training sample and of the pose-search training logs. They are removed from the blind test,
   which therefore holds only pairs that nothing has ever processed: 2,623 pairs (1,976 above and 647 below 30 %
   overlap; `scripts/make_splits_v3.py`, `results/protocol_v3/indoor_splits.json`). The blind scenes are disjoint
   from every set that fits, calibrates, chooses or gates method v3; other pairs of these scenes were v2 fitting
   pairs, which method v3 does not use. No 3DMatch training scene is free of earlier logs, so scene-level freshness
   with respect to protocol v2 is not attainable within 3DMatch; this is stated in the paper.

# Evaluation protocol v4 (pre-registered 2026-10-22, before the v4 split was generated)

Reason: after protocol v3, analyses on fitting, calibration and development data only found that (a) the speed-up is
limited by the calibration set's size (with ~1,000 calibration pairs per difficulty group no loss can be accepted, and
the 3DMatch speed-up still rose from 1.37x to 1.55x between 2,400 and 3,000 calibration pairs), (b) the choice among
controller configurations is limited by the fitting set's size (with 1,000 fitting pairs the best configurations
differ by about one standard error), and (c) part of the gate's live cost is the per-call overhead of scikit-learn
predictions. v4 enlarges both sets, widens the choice and evaluates the fitted models natively.

## Method v4 (frozen candidate space and choice rule)
- Candidates, for each estimator, with the compatibility order: controller signals {base (v3), base + geometric
  verification of each stage's pose (`scripts/explore/verify_features.py`), base + correspondence-geometry
  uncertainty (`scripts/explore/geom_features.py`), base + both} x classifier {logit, poly2, hgb} x number of
  difficulty groups G in {2, 3} x gate {off, on}. Ladders, families, eps = 1 %, delta = 0.1, the dominance rule and
  choose-then-certify as in v3; the extra signals' measured cost is charged to every visited stage.
- Choice: the configuration with the lowest out-of-fold mean cost on the v4 fitting pairs (gate on: times one minus
  the gate's out-of-fold saving, the gate trained on fitting + calibration pairs as in v3). Configurations within one
  standard error of the best are tied; among ties the simplest wins: fewest extra signals, then logit < poly2 < hgb,
  then G = 3 (the v3 default) before G = 2, then no gate. The ratio order is reported for the chosen configuration.
- Implementation: the fitted classifiers and the gate are evaluated natively (NumPy); their decisions must equal
  scikit-learn's on every fitting and calibration pair before any blind pair is processed.

## Data v4 (indoor, FPFH)
- Pool: the 56 3DMatch training scenes that were not a blind scene of protocol v2 or v3 (13 v2 calibration scenes,
  43 v2 fitting scenes); pairs with overlap > 0.1.
- Blind test: pool scenes permuted with `numpy.random.default_rng(20261022)` and assigned until they hold at least
  3,500 eligible pairs; a random sample of 3,000 of their pairs (seed 1), minus every pair that appears in any earlier
  log under any role; reported above and below 30 % overlap.
- Calibration: the eligible pairs of the other pool scenes that appear in no earlier log, at most 6,000 (random,
  seed 2).
- Fitting: the eligible pairs of the other pool scenes that already have compatibility- and ratio-order budget logs
  (earlier fitting and calibration pairs); no new fitting logs.
- The blind scenes are disjoint from the fitting and calibration pairs; blind and calibration pairs were never
  processed before. No fresh outdoor or FCGF data exist: v4 is indoor FPFH only, and is also reported on the earlier
  test sets as not blind.

## Evaluation v4
- Order: calibration logs and signals; every selection (methods v2, v3 and v4, all fitted and certified on the v4
  fitting and calibration pairs) written to disk; only then are the blind pairs logged and evaluated, once.
- Live timing: 300 random blind pairs per overlap part, the full budget and the v2, v3 and v4 configurations on the
  same pairs, rotating order, on an otherwise idle machine.
- Adoption rule: v4 replaces v3 as the paper's method only if, on the v4 blind test, it is non-inferior and within the
  risk level for both estimators at both overlap levels, and its live mean time is lower than v3's on the same pairs
  above 30 % overlap for both estimators (paired scene-stratified bootstrap ratio of mean times above 1), with the 95 %
  interval above 1 for at least one of them. Otherwise v3 stays and v4 is reported as a negative or partial result.

## Status of protocol v4 (2026-10-22, 14:20)
**Not executed.** The v4 split was generated (`scripts/make_splits_v4.py`: metadata only; the fitting pairs' existing
logs were copied), but no v4 calibration or blind pair was logged, processed or looked at. The authors decided to
strengthen the evaluation of the final method (v3) instead: component ablations on earlier test sets, per-scene and
group-wise checks of the fresh blind result, and a third estimator (pre-registered separately before it is run).

# Protocol v3, addendum A: a third estimator, MAC (pre-registered 2026-10-22, before any MAC run on a blind pair)

Purpose: test whether the final method (v3), frozen, carries over to another graph-based estimator.
- Estimator: MAC (Zhang et al., CVPR 2023), re-implemented on CPU after the authors' implementation (`src/acpr/mac.py`):
  first-order compatibility max(0, 1 - d^2/tau^2) pruned below 0.99, second-order graph, maximal cliques of at least
  three nodes (igraph), node-guided clique selection, instance-equal SVD hypotheses, MAE scoring, 20-iteration
  refinement (always applied; the authors' demo keeps it only if it is closer to the ground truth, which uses the
  ground truth); tau = 0.10 m. Same FPFH correspondences, budgets, orderings and success criterion as the other
  estimators. Fidelity is reported against the published FPFH recall (3DMatch 84.10 %, 3DLoMatch 40.88 %).
- Methods: the final method (classifier chosen on the fitting pairs among the four v3 kinds, hardness gate) and CAB
  without the gate (logistic controller), unchanged, with the v3 choice and certification rules.
- Data (indoor FPFH only; no outdoor or FCGF runs): the v3 split (fitting v3_fit, calibration v2_cal, fresh blind test
  v3_blind_hi / v3_blind_lo, evaluated once for MAC), and the protocol-v2 indoor family (fitting v2_fit, calibration
  v2_cal; held-out scenes and 3DMatch / 3DLoMatch, reported as earlier test sets).
- Order: MAC logs of the fitting and calibration pairs and every MAC selection are written to disk before MAC runs on
  any blind pair; then the blind pairs are logged and evaluated once, and timed live (300 pairs per overlap part,
  full budget and both configurations on the same pairs). All results are reported, favourable or not.

# Protocol v3, addendum B: MAC on every family, with the authors' graph reduction (pre-registered 2026-10-22, 22:30, before any MAC run on a test pair)

Amends addendum A before MAC ran on any test pair: only 520 fitting pairs (v3_fit) had been logged, with addendum A's
implementation; those logs are archived (logs/mac_python_impl/) and not used.
- Scope: MAC is evaluated on every family of test sets of SC2-PCR and TurboReg, with the same fitting, calibration and
  test splits and the same methods as in addendum A (CAB without the gate with the logistic controller; the final
  method, with the classifier kind chosen on the fitting pairs and the hardness gate), both orderings, the v3 choice and
  certification rules: indoor FPFH (addendum A: families v3_indoor_fpfh and v2_indoor_fpfh), KITTI with FPFH
  (v2_kitti_fpfh: fitting kitti_train, calibration kitti_val + kitti_calib, tests kitti_raw_blind and kitti_test),
  indoor FCGF (v2_indoor_fcgf: fcgfown_v2_fit, fcgfown_val; tests fcgfown_3DMatch, fcgfown_3DLoMatch) and KITTI with
  FCGF (v2_kitti_fcgf: fcgfown_kitti_fit, fcgfown_kitti_raw_cal; tests fcgfown_kitti_raw_blind, fcgfown_kitti_test).
- Implementation (`src/acpr/mac.py`): addendum A's MAC plus two parts of the authors' C++ implementation, which
  produced their published results. (1) Graph reduction before the clique search, on every graph: weighted clustering
  coefficient of every node on the second-order graph, threshold min(Otsu, mean, total coefficient); if it exceeds 3
  and there are more than 50 correspondences, only the edges among the most clustered nodes (at least about 50) are
  kept. (2) The C++ KITTI setting outdoors: tau = 0.6 m, edge cut-off 0.9 with FPFH and 0.999 with FCGF, cliques of at
  least 4 nodes. Indoors, for both descriptors, the compatibility graph stays that of the Python implementation
  (tau = 0.10 m, cut-off 0.99, cliques of at least 3; the C++ indoor graph depends on the resolution of the authors'
  point-cloud files). Success is judged after the refinement, as for the other estimators.
  Reason: without the reduction, the clique search on dense graphs (pairs with many inliers: easy indoor pairs, most
  FCGF pairs) explodes (16.5 million maximal cliques and ~6 min per run on an indoor FPFH fitting pair; with the
  reduction 2,768 cliques, 2 s, still registered), so addendum A's MAC was far slower than the authors' published MAC
  on exactly the easy pairs, which would inflate the savings of any adaptive wrapper, and the FCGF families could not be
  run. Checks (fitting pairs and synthetic graphs only): the reduction reproduces a literal transcription of the C++
  loops on random and planted-cluster graphs; graphs it does not reduce give results identical to addendum A's
  implementation (3 fitting pairs); full-budget runs on 6 fitting pairs of each family take 1-35 s and agree with
  SC2-PCR's success on every one.
- Fidelity is reported against MAC's published recall (FPFH: 3DMatch 84.10 %, 3DLoMatch 40.88 %, KITTI 99.46 %;
  FCGF: 3DMatch 93.72 %, 3DLoMatch 59.85 %, KITTI 97.84 %).
- Order, family by family (indoor FPFH, KITTI FPFH, indoor FCGF, KITTI FCGF): MAC logs of the fitting and calibration
  pairs and every MAC selection are written to disk before MAC runs on any test pair of that family; then its test
  logs, a single evaluation (which must reproduce the selections), and live timing on an otherwise idle machine
  (300 random pairs per test set, full budget and both configurations on the same pairs, compatibility order; a family
  whose configurations are all certified as the full budget is not timed). All results are reported, favourable or not.

## Addendum B, amendment 1 (2026-10-23, 12:05, before any MAC run on a KITTI calibration or test pair)
MAC with FPFH on KITTI uses the compatibility cut-off 0.99 (the authors' Python implementation's rule, an edge needs
d < 0.1 tau, as indoors) instead of the C++ KITTI value 0.9. With 0.9 the clique search found up to 25 million maximal
cliques per run on KITTI fitting pairs (mean 143 s per full-budget run, up to 1,310 s; the graph reduction does not
trigger on these graphs), which puts the pre-registered KITTI evaluation (3,403 pairs and live timing) out of reach
on our machine (estimated two days of logs and live timing). On the 47 KITTI fitting pairs logged with 0.9, cut-off
0.99 registers exactly the same pairs (95.7 %, as SC2-PCR and TurboReg; no pair differs), with a mean of 7.5 s per
run and 80x fewer cliques. Only fitting pairs (kitti_train) had been processed; those logs are archived
(logs/mac_kitti_cut09/) and the KITTI family is restarted with the amended setting. FCGF on KITTI keeps 0.999.
