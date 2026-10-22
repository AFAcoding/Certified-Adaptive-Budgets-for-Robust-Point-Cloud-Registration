# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## SC²-PCR

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1238 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-2000-4000 | mondrian | λ per group = 0.5/0.9/0.5 | 0.00 | 3032 |
| 250-2000-4000 | mondrian | λ per group = 0.7/0.88/0.5 | 0.00 | 3154 |
| 500-2000-4000 | giveup | 0.75, 0.05 | 0.33 | 3305 |
| x4 | giveup | 0.5, 0.1 | 0.33 | 3311 |
| 250-1000-4000 | giveup | 0.5, 0.1 | 0.33 | 3311 |
| doubling | mondrian | λ per group = 0.5/0.95/0.6 | 0.00 | 3385 |
| 500-2000-4000 | threshold | 0.75 | 0.33 | 3408 |
| 250-2000-4000 | giveup | 0.85, 0.1 | 0.33 | 3439 |
| x4 | threshold | 0.5 | 0.33 | 3477 |
| 250-1000-4000 | threshold | 0.5 | 0.33 | 3477 |
| 250-1000-2000-4000 | giveup | 0.85, 0.05 | 0.33 | 3588 |
| 250-2000-4000 | threshold | 0.85 | 0.33 | 3601 |
| x4 | mondrian | λ per group = 0.8/0.5/0.5 | 0.00 | 3604 |
| 250-1000-4000 | mondrian | λ per group = 0.8/0.5/0.5 | 0.00 | 3604 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.85/0.95/0.6 | 0.00 | 3610 |
| doubling | giveup | 0.85, 0.05 | 0.33 | 3643 |
| 250-1000-2000-4000 | threshold | 0.85 | 0.33 | 3733 |
| 250-500-4000 | giveup | 0.5, 0.05 | 0.33 | 3748 |
| 500-4000 | giveup | 0.5, 0.1 | 0.33 | 3769 |
| doubling | threshold | 0.85 | 0.33 | 3811 |
| 250-500-4000 | threshold | 0.5 | 0.00 | 3836 |
| 250-500-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 3836 |
| 250-4000 | giveup | 0.5, 0.15 | 0.33 | 3838 |
| 500-4000 | threshold | 0.5 | 0.00 | 3855 |
| 500-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 3855 |
| 250-4000 | threshold | 0.5 | 0.00 | 3938 |
| 250-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 3938 |
| 500-4000 | mdp | 0 | 0.33 | 3982 |
| 250-4000 | mdp | 0 | 0.33 | 4026 |
| full | threshold | 1.01 | 0.00 | 4219 |
| full | mondrian | never stop early | 0.00 | 4219 |
| 250-500-4000 | mdp | -1 | 0.00 | 4441 |
| x4 | mdp | -1 | 0.00 | 4670 |
| 250-1000-4000 | mdp | -1 | 0.00 | 4670 |
| 250-2000-4000 | mdp | -1 | 0.00 | 5454 |
| 500-2000-4000 | mdp | -1 | 0.00 | 5531 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 5810 |
| doubling | mdp | -1 | 0.00 | 5937 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-2000-4000 / giveup | 500-2000-4000 / giveup | 0.6, 0.05 | 78.9 | 0.57 | 3356 |
| mondrian | 500-2000-4000 / mondrian | 500-2000-4000 / mondrian | λ per group = 0.85/0.6/0.7 | 79.2 | 0.00 | 3877 |

### SC²-PCR, kitti_raw_blind test (1310 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-2000-4000 / giveup | 61.07 | 3914 | +0.69 [+1.07] | False | 1.13× [1.10, 1.16] | 0.00391 | 0.69 |
| mondrian: 500-2000-4000 / mondrian | 61.60 | 4014 | +0.15 [+0.31] | True | 1.10× [1.08, 1.12] | 0.5 | 0.15 |
| fixed budget N=250 (single run) | 6.34 | 97 | | | | | |
| fixed budget N=500 (single run) | 12.75 | 182 | | | | | |
| fixed budget N=1000 (single run) | 24.35 | 425 | | | | | |
| fixed budget N=2000 (single run) | 42.98 | 1256 | | | | | |
| fixed budget N=4000 (single run) | 61.76 | 4411 | | | | | |

### SC²-PCR, kitti_test test (555 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-2000-4000 / giveup | 91.35 | 2966 | +0.90 [+1.62] | False | 1.45× [1.36, 1.55] | 0.0625 | 0.90 |
| mondrian: 500-2000-4000 / mondrian | 91.89 | 3302 | +0.36 [+0.90] | True | 1.30× [1.24, 1.37] | 0.5 | 0.36 |
| fixed budget N=250 (single run) | 12.79 | 92 | | | | | |
| fixed budget N=500 (single run) | 20.72 | 173 | | | | | |
| fixed budget N=1000 (single run) | 39.28 | 407 | | | | | |
| fixed budget N=2000 (single run) | 72.43 | 1210 | | | | | |
| fixed budget N=4000 (single run) | 92.25 | 4294 | | | | | |

## TurboReg

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1238 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-2000-4000 | giveup | 0.5, 0.05 | 0.33 | 3624 |
| 250-2000-4000 | threshold | 0.5 | 0.33 | 3682 |
| 500-2000-4000 | giveup | 0.5, 0.05 | 0.33 | 3747 |
| 500-2000-4000 | threshold | 0.5 | 0.33 | 3821 |
| 250-2000-4000 | mondrian | λ per group = 0.5/0.7/0.5 | 0.00 | 3845 |
| 500-2000-4000 | mondrian | λ per group = 0.5/0.7/0.5 | 0.00 | 3947 |
| 250-1000-2000-4000 | giveup | 0.6, 0.02 | 0.33 | 4167 |
| 250-1000-2000-4000 | threshold | 0.6 | 0.33 | 4211 |
| doubling | giveup | 0.6, 0.02 | 0.33 | 4228 |
| doubling | threshold | 0.6 | 0.33 | 4273 |
| 250-1000-2000-4000 | mdp | 0 | 0.33 | 4409 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.6/0.8/0.6 | 0.00 | 4442 |
| doubling | mondrian | λ per group = 0.6/0.8/0.6 | 0.00 | 4461 |
| x4 | giveup | 0.5, 0.05 | 0.33 | 4484 |
| 250-1000-4000 | giveup | 0.5, 0.05 | 0.33 | 4484 |
| x4 | mdp | 0 | 0.33 | 4494 |
| 250-1000-4000 | mdp | 0 | 0.33 | 4494 |
| x4 | threshold | 0.5 | 0.33 | 4520 |
| 250-1000-4000 | threshold | 0.5 | 0.33 | 4520 |
| x4 | mondrian | λ per group = 0.6/0.5/0.5 | 0.00 | 4681 |
| 250-1000-4000 | mondrian | λ per group = 0.6/0.5/0.5 | 0.00 | 4681 |
| 250-500-4000 | mdp | 0 | 0.33 | 4687 |
| 500-4000 | giveup | 0.5, 0.3 | 0.33 | 4695 |
| 250-500-4000 | giveup | 0.5, 0.15 | 0.33 | 4710 |
| 500-2000-4000 | mdp | 0 | 0.33 | 4719 |
| 250-500-4000 | threshold | 0.5 | 0.00 | 4851 |
| 250-500-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 4851 |
| 500-4000 | threshold | 0.5 | 0.00 | 4906 |
| 500-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 4906 |
| 250-4000 | giveup | 0.5, 0.2 | 0.33 | 4916 |
| 250-4000 | threshold | 0.5 | 0.00 | 5074 |
| 250-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 5074 |
| 500-4000 | mdp | 0 | 0.33 | 5184 |
| full | threshold | 1.01 | 0.00 | 5253 |
| full | mondrian | never stop early | 0.00 | 5253 |
| 250-4000 | mdp | -1 | 0.00 | 5371 |
| 250-2000-4000 | mdp | -1 | 0.00 | 6977 |
| doubling | mdp | -1 | 0.00 | 7754 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-2000-4000 / giveup | 250-2000-4000 / giveup | 0.6, 0.05 | 78.7 | 0.48 | 4201 |
| mondrian | 250-2000-4000 / mondrian | 250-2000-4000 / mondrian | λ per group = 0.85/0.7/1.01 | 79.2 | 0.00 | 5448 |

### TurboReg, kitti_raw_blind test (1310 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-2000-4000 / giveup | 61.91 | 4725 | +0.69 [+1.15] | False | 1.15× [1.12, 1.18] | 0.0352 | 0.92 |
| mondrian: 250-2000-4000 / mondrian | 62.67 | 5124 | -0.08 [+0.00] | True | 1.06× [1.04, 1.07] | 1 | 0.00 |
| fixed budget N=250 (single run) | 7.18 | 99 | | | | | |
| fixed budget N=500 (single run) | 14.12 | 212 | | | | | |
| fixed budget N=1000 (single run) | 25.50 | 555 | | | | | |
| fixed budget N=2000 (single run) | 44.05 | 1618 | | | | | |
| fixed budget N=4000 (single run) | 62.60 | 5414 | | | | | |

### TurboReg, kitti_test test (555 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-2000-4000 / giveup | 91.71 | 4028 | +0.54 [+1.26] | False | 1.41× [1.34, 1.50] | 0.375 | 0.72 |
| mondrian: 250-2000-4000 / mondrian | 92.07 | 4837 | +0.18 [+0.54] | True | 1.18× [1.13, 1.23] | 1 | 0.18 |
| fixed budget N=250 (single run) | 14.23 | 103 | | | | | |
| fixed budget N=500 (single run) | 22.34 | 226 | | | | | |
| fixed budget N=1000 (single run) | 42.34 | 574 | | | | | |
| fixed budget N=2000 (single run) | 71.53 | 1631 | | | | | |
| fixed budget N=4000 (single run) | 92.25 | 5697 | | | | | |
