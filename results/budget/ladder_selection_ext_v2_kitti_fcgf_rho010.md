# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## SC²-PCR

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1107 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-500-4000 | threshold | 0.97 | 0.33 | 60 |
| 250-500-4000 | giveup | 0.97, 0 | 0.33 | 60 |
| 250-4000 | threshold | 0.88 | 0.33 | 70 |
| 250-4000 | giveup | 0.88, 0 | 0.33 | 70 |
| 500-4000 | threshold | 0.5 | 0.33 | 96 |
| 500-4000 | mdp | 30 | 0.33 | 96 |
| 500-4000 | giveup | 0.5, 0 | 0.33 | 96 |
| 500-2000 | threshold | 0.5 | 0.33 | 96 |
| 500-2000 | mdp | 30 | 0.33 | 96 |
| 500-2000 | giveup | 0.5, 0 | 0.33 | 96 |
| 250-500-1000-2000 | mdp | 0 | 0.33 | 170 |
| 250-1000-2000 | mdp | 0 | 0.33 | 227 |
| fixed-1000 | threshold | 0.5 | 0.33 | 303 |
| fixed-1000 | giveup | 0.5, 0 | 0.33 | 303 |
| 250-2000 | mdp | 0 | 0.33 | 339 |
| 250-500-4000 | mdp | 0 | 0.33 | 377 |
| fixed-2000 | threshold | 0.5 | 0.33 | 1020 |
| fixed-2000 | giveup | 0.5, 0 | 0.33 | 1020 |
| 250-2000 | threshold | 1.01 | 0.33 | 1052 |
| 250-2000 | giveup | 1.01, 0 | 0.33 | 1052 |
| 250-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 1289 |
| 250-4000 | mdp | 0 | 0.00 | 1306 |
| 250-500-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 1323 |
| 500-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 1351 |
| 250-1000-2000 | threshold | 1.01 | 0.33 | 1356 |
| 250-1000-2000 | giveup | 1.01, 0 | 0.33 | 1356 |
| 250-500-1000-2000 | threshold | 1.01 | 0.33 | 1452 |
| 250-500-1000-2000 | giveup | 1.01, 0 | 0.33 | 1452 |
| full | threshold | 1.01 | 0.00 | 3721 |
| full | mondrian | never stop early | 0.00 | 3721 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-500-4000 / threshold | full / threshold (fallback) | 1.01 | 86.4 | 0.00 | 3926 |
| mondrian | 250-4000 / mondrian | full / mondrian (fallback) | λ per group = 1.01/1.01/1.01 | 86.4 | 0.00 | 3926 |

### SC²-PCR, fcgfown_kitti_raw_blind test (203 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 92.61 | 3997 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 92.61 | 3997 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 90.15 | 37 | | | | | |
| fixed budget N=500 (single run) | 90.64 | 115 | | | | | |
| fixed budget N=1000 (single run) | 90.64 | 335 | | | | | |
| fixed budget N=2000 (single run) | 91.63 | 1087 | | | | | |
| fixed budget N=4000 (single run) | 92.61 | 3997 | | | | | |

### SC²-PCR, fcgfown_kitti_test test (555 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 93.51 | 3930 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 93.51 | 3930 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 90.45 | 35 | | | | | |
| fixed budget N=500 (single run) | 91.53 | 105 | | | | | |
| fixed budget N=1000 (single run) | 92.43 | 319 | | | | | |
| fixed budget N=2000 (single run) | 93.15 | 1062 | | | | | |
| fixed budget N=4000 (single run) | 93.51 | 3930 | | | | | |

## TurboReg

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1107 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-4000 | threshold | 0.96 | 0.33 | 262 |
| 250-4000 | giveup | 0.96, 0 | 0.33 | 262 |
| 500-4000 | threshold | 0.5 | 0.33 | 293 |
| 500-4000 | mdp | 30 | 0.33 | 293 |
| 500-4000 | giveup | 0.5, 0 | 0.33 | 293 |
| 500-2000 | threshold | 0.5 | 0.33 | 293 |
| 500-2000 | mdp | 30 | 0.33 | 293 |
| 500-2000 | giveup | 0.5, 0 | 0.33 | 293 |
| 250-500-1000-2000 | mdp | 0 | 0.33 | 464 |
| 250-1000-2000 | mdp | 0 | 0.33 | 532 |
| 250-2000 | mdp | 0 | 0.33 | 594 |
| fixed-1000 | threshold | 0.5 | 0.33 | 637 |
| fixed-1000 | giveup | 0.5, 0 | 0.33 | 637 |
| fixed-2000 | threshold | 0.5 | 0.33 | 1648 |
| fixed-2000 | giveup | 0.5, 0 | 0.33 | 1648 |
| 250-2000 | threshold | 1.01 | 0.33 | 1823 |
| 250-2000 | giveup | 1.01, 0 | 0.33 | 1823 |
| 250-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 1993 |
| 250-4000 | mdp | 0 | 0.00 | 2033 |
| 500-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 2113 |
| 250-1000-2000 | threshold | 1.01 | 0.33 | 2460 |
| 250-1000-2000 | giveup | 1.01, 0 | 0.33 | 2460 |
| 250-500-1000-2000 | threshold | 1.01 | 0.33 | 2753 |
| 250-500-1000-2000 | giveup | 1.01, 0 | 0.33 | 2753 |
| full | threshold | 1.01 | 0.00 | 5578 |
| full | mondrian | never stop early | 0.00 | 5578 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-4000 / threshold | full / threshold (fallback) | 1.01 | 85.6 | 0.00 | 5455 |
| mondrian | 250-4000 / mondrian | full / mondrian (fallback) | λ per group = 1.01/1.01/1.01 | 85.6 | 0.00 | 5455 |

### TurboReg, fcgfown_kitti_raw_blind test (203 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 92.12 | 5496 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 92.12 | 5496 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 90.15 | 180 | | | | | |
| fixed budget N=500 (single run) | 90.64 | 308 | | | | | |
| fixed budget N=1000 (single run) | 90.64 | 652 | | | | | |
| fixed budget N=2000 (single run) | 91.13 | 1664 | | | | | |
| fixed budget N=4000 (single run) | 92.12 | 5496 | | | | | |

### TurboReg, fcgfown_kitti_test test (555 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 93.51 | 5870 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 93.51 | 5870 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 90.09 | 163 | | | | | |
| fixed budget N=500 (single run) | 91.53 | 278 | | | | | |
| fixed budget N=1000 (single run) | 92.25 | 630 | | | | | |
| fixed budget N=2000 (single run) | 92.97 | 1679 | | | | | |
| fixed budget N=4000 (single run) | 93.51 | 5870 | | | | | |
