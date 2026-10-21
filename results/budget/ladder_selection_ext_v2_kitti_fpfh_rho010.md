# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## SC²-PCR

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1238 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-4000 | threshold | 0.5 | 0.00 | 3908 |
| 500-4000 | giveup | 0.5, 0 | 0.00 | 3908 |
| 500-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 3908 |
| 250-500-4000 | giveup | 0.6, 0.3 | 0.33 | 3948 |
| 250-500-4000 | threshold | 0.5 | 0.33 | 3949 |
| 250-500-4000 | mondrian | λ per group = 0.5/0.5/0.6 | 0.00 | 3963 |
| 500-4000 | mdp | 0 | 0.00 | 3994 |
| 250-500-4000 | mdp | 0 | 0.00 | 4079 |
| full | threshold | 1.01 | 0.00 | 4219 |
| full | mondrian | never stop early | 0.00 | 4219 |
| 250-4000 | giveup | 0.5, 0.1 | 0.00 | 4260 |
| 250-4000 | threshold | 0.5 | 0.00 | 4275 |
| 250-4000 | mdp | 0 | 0.00 | 4275 |
| 250-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 4275 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-4000 / threshold | 500-4000 / threshold | 0.5 | 79.2 | 0.08 | 4208 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.5/0.5/1.01 | 79.2 | 0.00 | 4606 |

### SC²-PCR, kitti_raw_blind test (1310 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 61.68 | 4316 | +0.08 [+0.23] | True | 1.02× [1.01, 1.03] | 1 | 0.08 |
| mondrian: 500-4000 / mondrian | 61.76 | 4566 | +0.00 [+0.00] | True | 0.97× [0.97, 0.97] | 1 | 0.00 |
| fixed budget N=250 (single run) | 0.76 | 58 | | | | | |
| fixed budget N=500 (single run) | 5.27 | 155 | | | | | |
| fixed budget N=1000 (single run) | 19.16 | 418 | | | | | |
| fixed budget N=2000 (single run) | 39.08 | 1257 | | | | | |
| fixed budget N=4000 (single run) | 61.76 | 4411 | | | | | |

### SC²-PCR, kitti_test test (555 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 91.71 | 4023 | +0.54 [+1.08] | False | 1.07× [1.04, 1.10] | 0.25 | 0.54 |
| mondrian: 500-4000 / mondrian | 92.25 | 4439 | +0.00 [+0.00] | True | 0.97× [0.97, 0.97] | 1 | 0.00 |
| fixed budget N=250 (single run) | 1.62 | 55 | | | | | |
| fixed budget N=500 (single run) | 12.25 | 145 | | | | | |
| fixed budget N=1000 (single run) | 41.44 | 390 | | | | | |
| fixed budget N=2000 (single run) | 75.50 | 1200 | | | | | |
| fixed budget N=4000 (single run) | 92.25 | 4294 | | | | | |

## TurboReg

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1238 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| x4 | giveup | 0.6, 0.1 | 0.33 | 3266 |
| 250-1000-4000 | giveup | 0.6, 0.1 | 0.33 | 3266 |
| x4 | mondrian | λ per group = 0.6/0.6/0.5 | 0.00 | 3498 |
| 250-1000-4000 | mondrian | λ per group = 0.6/0.6/0.5 | 0.00 | 3498 |
| x4 | threshold | 0.6 | 0.00 | 3515 |
| 250-1000-4000 | threshold | 0.6 | 0.00 | 3515 |
| x4 | mdp | 0 | 0.00 | 3568 |
| 250-1000-4000 | mdp | 0 | 0.00 | 3568 |
| 250-500-4000 | giveup | 0.5, 0.2 | 0.33 | 4682 |
| 500-4000 | giveup | 0.6, 0.2 | 0.33 | 4764 |
| 500-4000 | threshold | 0.6 | 0.33 | 4836 |
| 250-500-4000 | threshold | 0.5 | 0.33 | 4844 |
| 250-500-4000 | mondrian | λ per group = 0.6/0.5/0.5 | 0.00 | 4860 |
| 500-4000 | mdp | 0 | 0.00 | 4902 |
| 500-4000 | mondrian | λ per group = 0.5/0.5/0.75 | 0.00 | 4920 |
| 250-4000 | giveup | 0.5, 0.2 | 0.00 | 5170 |
| full | threshold | 1.01 | 0.00 | 5253 |
| full | mondrian | never stop early | 0.00 | 5253 |
| 250-4000 | threshold | 0.5 | 0.00 | 5260 |
| 250-4000 | mdp | 0 | 0.00 | 5260 |
| 250-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 5260 |
| 250-500-4000 | mdp | -1 | 0.00 | 5307 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | x4 / giveup | full / threshold (fallback) | 1.01 | 79.2 | 0.00 | 5552 |
| mondrian | x4 / mondrian | x4 / mondrian | λ per group = 0.94/0.75/0.5 | 79.2 | 0.00 | 4167 |

### TurboReg, kitti_raw_blind test (1310 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 62.60 | 5414 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: x4 / mondrian | 62.52 | 4827 | +0.08 [+0.23] | True | 1.12× [1.11, 1.14] | 1 | 0.08 |
| fixed budget N=250 (single run) | 0.92 | 7 | | | | | |
| fixed budget N=500 (single run) | 4.58 | 48 | | | | | |
| fixed budget N=1000 (single run) | 17.94 | 230 | | | | | |
| fixed budget N=2000 (single run) | 39.08 | 1316 | | | | | |
| fixed budget N=4000 (single run) | 62.60 | 5414 | | | | | |

### TurboReg, kitti_test test (555 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 92.25 | 5697 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: x4 / mondrian | 91.89 | 4238 | +0.36 [+0.90] | True | 1.34× [1.28, 1.42] | 0.5 | 0.36 |
| fixed budget N=250 (single run) | 1.08 | 8 | | | | | |
| fixed budget N=500 (single run) | 8.65 | 50 | | | | | |
| fixed budget N=1000 (single run) | 40.54 | 242 | | | | | |
| fixed budget N=2000 (single run) | 75.32 | 1399 | | | | | |
| fixed budget N=4000 (single run) | 92.25 | 5697 | | | | | |
