# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## SC²-PCR

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1238 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-1000-2000-4000 | giveup | 0.6, 0.2 | 0.33 | 2257 |
| 250-2000-4000 | giveup | 0.5, 0.2 | 0.33 | 2333 |
| 250-2000-4000 | threshold | 0.5 | 0.33 | 2438 |
| 250-2000-4000 | mondrian | λ per group = 0.5/0.6/0.5 | 0.00 | 2507 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.6/0.5/0.6 | 0.00 | 2528 |
| 250-1000-2000-4000 | threshold | 0.6 | 0.00 | 2542 |
| 500-2000-4000 | giveup | 0.7, 0.15 | 0.33 | 2577 |
| 500-2000-4000 | mondrian | λ per group = 0.7/0.7/0.6 | 0.00 | 2584 |
| 500-2000-4000 | threshold | 0.7 | 0.00 | 2626 |
| doubling | giveup | 0.75, 0.05 | 0.33 | 2723 |
| doubling | threshold | 0.75 | 0.33 | 2755 |
| doubling | mondrian | λ per group = 0.8/0.75/0.75 | 0.00 | 2770 |
| x4 | giveup | 0.5, 0.15 | 0.33 | 2919 |
| 250-1000-4000 | giveup | 0.5, 0.15 | 0.33 | 2919 |
| 500-2000-4000 | mdp | 0 | 0.33 | 2970 |
| 250-2000-4000 | mdp | 0 | 0.00 | 2990 |
| x4 | threshold | 0.5 | 0.00 | 3048 |
| x4 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 3048 |
| 250-1000-4000 | threshold | 0.5 | 0.00 | 3048 |
| 250-1000-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 3048 |
| x4 | mdp | 0 | 0.00 | 3102 |
| 250-1000-4000 | mdp | 0 | 0.00 | 3102 |
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
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 5860 |
| doubling | mdp | -1 | 0.00 | 6008 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-1000-2000-4000 / giveup | full / threshold (fallback) | 1.01 | 79.2 | 0.00 | 4450 |
| mondrian | 250-2000-4000 / mondrian | 250-2000-4000 / mondrian | λ per group = 1.01/0.8/0.7 | 79.2 | 0.08 | 3512 |

### SC²-PCR, kitti_test test (555 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 92.25 | 4294 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: 250-2000-4000 / mondrian | 92.25 | 3352 | +0.00 [+0.00] | True | 1.28× [1.22, 1.36] | 1 | 0.00 |
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

### TurboReg, kitti_test test (555 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-1000-2000-4000 / giveup | 91.71 | 3194 | +0.54 [+1.08] | False | 1.78× [1.65, 1.95] | 0.25 | 0.54 |
| mondrian: 250-1000-2000-4000 / mondrian | 92.07 | 3762 | +0.18 [+0.54] | True | 1.51× [1.42, 1.63] | 1 | 0.18 |
| fixed budget N=250 (single run) | 1.08 | 8 | | | | | |
| fixed budget N=500 (single run) | 8.65 | 50 | | | | | |
| fixed budget N=1000 (single run) | 40.54 | 242 | | | | | |
| fixed budget N=2000 (single run) | 75.32 | 1399 | | | | | |
| fixed budget N=4000 (single run) | 92.25 | 5697 | | | | | |
