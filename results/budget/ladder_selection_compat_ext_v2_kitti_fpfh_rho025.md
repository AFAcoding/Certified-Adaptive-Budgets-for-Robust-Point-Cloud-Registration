# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## SC²-PCR

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1238 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| x4 | giveup | 0.6, 0.05 | 0.33 | 3547 |
| 250-1000-4000 | giveup | 0.6, 0.05 | 0.33 | 3547 |
| x4 | mondrian | λ per group = 0.6/0.6/0.5 | 0.00 | 3565 |
| 250-1000-4000 | mondrian | λ per group = 0.6/0.6/0.5 | 0.00 | 3565 |
| x4 | threshold | 0.6 | 0.00 | 3642 |
| 250-1000-4000 | threshold | 0.6 | 0.00 | 3642 |
| 250-500-4000 | mdp | 0 | 0.00 | 3650 |
| 500-4000 | giveup | 0.5, 0.2 | 0.33 | 3663 |
| 250-500-4000 | giveup | 0.5, 0.05 | 0.33 | 3671 |
| 250-500-4000 | threshold | 0.5 | 0.00 | 3792 |
| 250-500-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 3792 |
| 250-4000 | giveup | 0.5, 0.1 | 0.33 | 3834 |
| 500-4000 | threshold | 0.5 | 0.00 | 3855 |
| 500-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 3855 |
| 250-4000 | threshold | 0.5 | 0.00 | 3968 |
| 250-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 3968 |
| 500-4000 | mdp | 0 | 0.00 | 4119 |
| 250-4000 | mdp | 0 | 0.00 | 4134 |
| full | threshold | 1.01 | 0.00 | 4219 |
| full | mondrian | never stop early | 0.00 | 4219 |
| x4 | mdp | -1 | 0.00 | 4670 |
| 250-1000-4000 | mdp | -1 | 0.00 | 4670 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | x4 / giveup | x4 / giveup | 0.6, 0.05 | 79.1 | 0.32 | 3719 |
| mondrian | x4 / mondrian | x4 / mondrian | λ per group = 0.75/0.75/1.01 | 79.3 | 0.00 | 4284 |

### SC²-PCR, kitti_raw_blind test (1310 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / giveup | 61.37 | 3935 | +0.38 [+0.76] | True | 1.12× [1.10, 1.15] | 0.227 | 0.61 |
| mondrian: x4 / mondrian | 61.68 | 4408 | +0.08 [+0.31] | True | 1.00× [0.99, 1.02] | 1 | 0.15 |
| fixed budget N=250 (single run) | 6.34 | 97 | | | | | |
| fixed budget N=500 (single run) | 12.75 | 182 | | | | | |
| fixed budget N=1000 (single run) | 24.35 | 425 | | | | | |
| fixed budget N=2000 (single run) | 42.98 | 1256 | | | | | |
| fixed budget N=4000 (single run) | 61.76 | 4411 | | | | | |

### SC²-PCR, kitti_test test (555 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / giveup | 91.89 | 3600 | +0.36 [+0.90] | True | 1.19× [1.14, 1.25] | 0.5 | 0.36 |
| mondrian: x4 / mondrian | 92.25 | 4101 | +0.00 [+0.00] | True | 1.05× [1.02, 1.08] | 1 | 0.00 |
| fixed budget N=250 (single run) | 12.79 | 92 | | | | | |
| fixed budget N=500 (single run) | 20.72 | 173 | | | | | |
| fixed budget N=1000 (single run) | 39.28 | 407 | | | | | |
| fixed budget N=2000 (single run) | 72.43 | 1210 | | | | | |
| fixed budget N=4000 (single run) | 92.25 | 4294 | | | | | |

## TurboReg

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1238 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| x4 | threshold | 0.5 | 0.33 | 4365 |
| x4 | giveup | 0.5, 0 | 0.33 | 4365 |
| 250-1000-4000 | threshold | 0.5 | 0.33 | 4365 |
| 250-1000-4000 | giveup | 0.5, 0 | 0.33 | 4365 |
| x4 | mdp | 0 | 0.33 | 4520 |
| 250-1000-4000 | mdp | 0 | 0.33 | 4520 |
| x4 | mondrian | λ per group = 0.7/0.5/0.5 | 0.00 | 4524 |
| 250-1000-4000 | mondrian | λ per group = 0.7/0.5/0.5 | 0.00 | 4524 |
| 500-4000 | giveup | 0.5, 0.15 | 0.33 | 4537 |
| 250-500-4000 | giveup | 0.6, 0.1 | 0.33 | 4613 |
| 250-500-4000 | threshold | 0.5 | 0.33 | 4624 |
| 250-500-4000 | mondrian | λ per group = 0.5/0.6/0.5 | 0.00 | 4676 |
| 250-4000 | giveup | 0.5, 0.1 | 0.33 | 4721 |
| 500-4000 | threshold | 0.5 | 0.00 | 4747 |
| 500-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 4747 |
| 250-4000 | threshold | 0.5 | 0.00 | 4860 |
| 250-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 4860 |
| 250-4000 | mdp | 0 | 0.00 | 5074 |
| full | threshold | 1.01 | 0.00 | 5253 |
| full | mondrian | never stop early | 0.00 | 5253 |
| 500-4000 | mdp | -1 | 0.00 | 5504 |
| 250-500-4000 | mdp | -1 | 0.00 | 5578 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | x4 / threshold | x4 / threshold | 0.5 | 78.9 | 0.48 | 4523 |
| mondrian | x4 / mondrian | x4 / mondrian | λ per group = 0.7/0.7/1.01 | 79.2 | 0.00 | 5294 |

### TurboReg, kitti_raw_blind test (1310 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / threshold | 62.29 | 4779 | +0.31 [+0.76] | True | 1.13× [1.11, 1.16] | 0.454 | 0.76 |
| mondrian: x4 / mondrian | 62.75 | 5336 | -0.15 [+0.08] | True | 1.01× [1.00, 1.03] | 0.625 | 0.08 |
| fixed budget N=250 (single run) | 7.18 | 99 | | | | | |
| fixed budget N=500 (single run) | 14.12 | 212 | | | | | |
| fixed budget N=1000 (single run) | 25.50 | 555 | | | | | |
| fixed budget N=2000 (single run) | 44.05 | 1618 | | | | | |
| fixed budget N=4000 (single run) | 62.60 | 5414 | | | | | |

### TurboReg, kitti_test test (555 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / threshold | 90.81 | 4521 | +1.44 [+2.52] | False | 1.26× [1.20, 1.33] | 0.0215 | 1.62 |
| mondrian: x4 / mondrian | 91.53 | 5209 | +0.72 [+1.44] | False | 1.09× [1.06, 1.13] | 0.125 | 0.72 |
| fixed budget N=250 (single run) | 14.23 | 103 | | | | | |
| fixed budget N=500 (single run) | 22.34 | 226 | | | | | |
| fixed budget N=1000 (single run) | 42.34 | 574 | | | | | |
| fixed budget N=2000 (single run) | 71.53 | 1631 | | | | | |
| fixed budget N=4000 (single run) | 92.25 | 5697 | | | | | |
