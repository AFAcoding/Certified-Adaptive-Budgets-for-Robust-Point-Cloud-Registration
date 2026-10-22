# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## SC²-PCR

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1238 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-2000-4000 | giveup | 0.6, 0.3 | 0.00 | 2478 |
| 500-2000-4000 | threshold | 0.6 | 0.00 | 2492 |
| 500-2000-4000 | mondrian | λ per group = 0.6/0.6/0.6 | 0.00 | 2492 |
| 250-1000-2000-4000 | giveup | 0.6, 0.3 | 0.00 | 2502 |
| 250-2000-4000 | threshold | 0.6 | 0.33 | 2511 |
| 250-2000-4000 | giveup | 0.6, 0 | 0.33 | 2511 |
| 250-2000-4000 | mondrian | λ per group = 0.5/0.7/0.6 | 0.00 | 2590 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.5/0.6/0.6 | 0.00 | 2602 |
| doubling | giveup | 0.6, 0.2 | 0.00 | 2603 |
| doubling | mondrian | λ per group = 0.6/0.5/0.6 | 0.00 | 2605 |
| 250-1000-2000-4000 | threshold | 0.6 | 0.00 | 2616 |
| 500-2000-4000 | mdp | 0 | 0.33 | 2649 |
| doubling | threshold | 0.6 | 0.00 | 2652 |
| doubling | mdp | 0 | 0.00 | 2734 |
| x4 | giveup | 0.5, 0.3 | 0.00 | 3060 |
| 250-1000-4000 | giveup | 0.5, 0.3 | 0.00 | 3060 |
| x4 | threshold | 0.5 | 0.00 | 3075 |
| x4 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 3075 |
| 250-1000-4000 | threshold | 0.5 | 0.00 | 3075 |
| 250-1000-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 3075 |
| x4 | mdp | 0 | 0.00 | 3191 |
| 250-1000-4000 | mdp | 0 | 0.00 | 3191 |
| 250-2000-4000 | mdp | 0 | 0.00 | 3258 |
| 500-4000 | threshold | 0.5 | 0.00 | 3939 |
| 500-4000 | giveup | 0.5, 0 | 0.00 | 3939 |
| 500-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 3939 |
| 250-500-4000 | threshold | 0.5 | 0.00 | 3994 |
| 250-500-4000 | giveup | 0.5, 0 | 0.00 | 3994 |
| 250-500-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 3994 |
| 500-4000 | mdp | 0 | 0.00 | 4121 |
| 250-500-4000 | mdp | 0 | 0.33 | 4219 |
| full | threshold | 1.01 | 0.00 | 4219 |
| full | mondrian | never stop early | 0.00 | 4219 |
| 250-4000 | threshold | 0.5 | 0.00 | 4275 |
| 250-4000 | mdp | 0 | 0.00 | 4275 |
| 250-4000 | giveup | 0.5, 0 | 0.00 | 4275 |
| 250-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 4275 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 5860 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-2000-4000 / giveup | 500-2000-4000 / giveup | 0.7, 0.3 | 78.9 | 0.32 | 3086 |
| mondrian | 500-2000-4000 / mondrian | 500-2000-4000 / mondrian | λ per group = 0.7/0.75/1.01 | 79.2 | 0.00 | 4050 |

### SC²-PCR, kitti_raw_blind test (1310 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-2000-4000 / giveup | 61.83 | 3877 | -0.08 [+0.00] | True | 1.14× [1.12, 1.16] | 1 | 0.00 |
| mondrian: 500-2000-4000 / mondrian | 61.83 | 4301 | -0.08 [+0.00] | True | 1.03× [1.01, 1.04] | 1 | 0.00 |
| fixed budget N=250 (single run) | 0.76 | 58 | | | | | |
| fixed budget N=500 (single run) | 5.27 | 155 | | | | | |
| fixed budget N=1000 (single run) | 19.16 | 418 | | | | | |
| fixed budget N=2000 (single run) | 39.08 | 1257 | | | | | |
| fixed budget N=4000 (single run) | 61.76 | 4411 | | | | | |

### SC²-PCR, kitti_test test (555 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-2000-4000 / giveup | 91.89 | 2902 | +0.36 [+0.90] | True | 1.48× [1.40, 1.57] | 0.5 | 0.36 |
| mondrian: 500-2000-4000 / mondrian | 92.25 | 3634 | +0.00 [+0.00] | True | 1.18× [1.14, 1.23] | 1 | 0.00 |
| fixed budget N=250 (single run) | 1.62 | 55 | | | | | |
| fixed budget N=500 (single run) | 12.25 | 145 | | | | | |
| fixed budget N=1000 (single run) | 41.44 | 390 | | | | | |
| fixed budget N=2000 (single run) | 75.50 | 1200 | | | | | |
| fixed budget N=4000 (single run) | 92.25 | 4294 | | | | | |

## TurboReg

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1238 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-1000-2000-4000 | giveup | 0.75, 0.05 | 0.33 | 2792 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.7/0.75/0.5 | 0.00 | 2856 |
| 250-1000-2000-4000 | threshold | 0.7 | 0.33 | 2932 |
| doubling | mondrian | λ per group = 0.8/0.85/0.5 | 0.00 | 2978 |
| doubling | threshold | 0.8 | 0.33 | 3061 |
| doubling | giveup | 0.8, 0 | 0.33 | 3061 |
| 500-2000-4000 | mondrian | λ per group = 0.8/0.6/0.75 | 0.00 | 3174 |
| 500-2000-4000 | giveup | 0.75, 0.05 | 0.33 | 3185 |
| 500-2000-4000 | threshold | 0.75 | 0.33 | 3221 |
| x4 | giveup | 0.6, 0.1 | 0.33 | 3266 |
| 250-1000-4000 | giveup | 0.6, 0.1 | 0.33 | 3266 |
| 250-1000-2000-4000 | mdp | 0 | 0.00 | 3273 |
| 250-2000-4000 | mondrian | λ per group = 0.85/0.7/0.5 | 0.00 | 3335 |
| 250-2000-4000 | giveup | 0.8, 0.05 | 0.33 | 3357 |
| 250-2000-4000 | threshold | 0.8 | 0.33 | 3391 |
| 250-2000-4000 | mdp | 0 | 0.33 | 3428 |
| 500-2000-4000 | mdp | 0 | 0.00 | 3455 |
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
| doubling | mdp | -1 | 0.00 | 6998 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-1000-2000-4000 / giveup | 250-1000-2000-4000 / giveup | 0.85, 0.05 | 78.8 | 0.48 | 3351 |
| mondrian | 250-1000-2000-4000 / mondrian | 250-1000-2000-4000 / mondrian | λ per group = 0.98/0.85/0.7 | 79.2 | 0.00 | 4046 |

### TurboReg, kitti_raw_blind test (1310 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-1000-2000-4000 / giveup | 62.06 | 4420 | +0.53 [+0.92] | True | 1.22× [1.19, 1.26] | 0.0391 | 0.61 |
| mondrian: 250-1000-2000-4000 / mondrian | 62.44 | 4746 | +0.15 [+0.38] | True | 1.14× [1.12, 1.16] | 0.5 | 0.15 |
| fixed budget N=250 (single run) | 0.92 | 7 | | | | | |
| fixed budget N=500 (single run) | 4.58 | 48 | | | | | |
| fixed budget N=1000 (single run) | 17.94 | 230 | | | | | |
| fixed budget N=2000 (single run) | 39.08 | 1316 | | | | | |
| fixed budget N=4000 (single run) | 62.60 | 5414 | | | | | |

### TurboReg, kitti_test test (555 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-1000-2000-4000 / giveup | 91.71 | 3189 | +0.54 [+1.08] | False | 1.79× [1.66, 1.95] | 0.25 | 0.54 |
| mondrian: 250-1000-2000-4000 / mondrian | 92.07 | 3818 | +0.18 [+0.54] | True | 1.49× [1.41, 1.60] | 1 | 0.18 |
| fixed budget N=250 (single run) | 1.08 | 8 | | | | | |
| fixed budget N=500 (single run) | 8.65 | 50 | | | | | |
| fixed budget N=1000 (single run) | 40.54 | 242 | | | | | |
| fixed budget N=2000 (single run) | 75.32 | 1399 | | | | | |
| fixed budget N=4000 (single run) | 92.25 | 5697 | | | | | |
