# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## SC²-PCR

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1238 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-2000-4000 | mondrian | λ per group = 0.5/0.85/0.5 | 0.00 | 3074 |
| 500-2000-4000 | mondrian | λ per group = 0.5/0.8/0.5 | 0.00 | 3104 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.5/0.88/0.6 | 0.00 | 3295 |
| doubling | mondrian | λ per group = 0.5/0.88/0.6 | 0.00 | 3329 |
| 250-1000-2000-4000 | giveup | 0.7, 0.02 | 0.33 | 3441 |
| 250-2000-4000 | giveup | 0.75, 0.02 | 0.33 | 3447 |
| 500-2000-4000 | threshold | 0.7 | 0.33 | 3497 |
| 500-2000-4000 | giveup | 0.7, 0 | 0.33 | 3497 |
| 250-1000-2000-4000 | threshold | 0.7 | 0.33 | 3512 |
| 250-2000-4000 | threshold | 0.75 | 0.33 | 3525 |
| x4 | giveup | 0.6, 0.05 | 0.33 | 3547 |
| 250-1000-4000 | giveup | 0.6, 0.05 | 0.33 | 3547 |
| doubling | mdp | 0 | 0.33 | 3556 |
| x4 | mondrian | λ per group = 0.6/0.6/0.5 | 0.00 | 3565 |
| 250-1000-4000 | mondrian | λ per group = 0.6/0.6/0.5 | 0.00 | 3565 |
| doubling | threshold | 0.75 | 0.33 | 3620 |
| doubling | giveup | 0.75, 0 | 0.33 | 3620 |
| x4 | threshold | 0.6 | 0.00 | 3642 |
| 250-1000-4000 | threshold | 0.6 | 0.00 | 3642 |
| 250-500-4000 | mdp | 0 | 0.00 | 3650 |
| 500-4000 | giveup | 0.5, 0.2 | 0.33 | 3663 |
| 250-500-4000 | giveup | 0.5, 0.05 | 0.33 | 3671 |
| 500-2000-4000 | mdp | 0 | 0.33 | 3745 |
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
| 250-2000-4000 | mdp | -1 | 0.00 | 5454 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 5810 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-1000-2000-4000 / giveup | 250-1000-2000-4000 / giveup | 0.6, 0.02 | 78.9 | 0.57 | 3384 |
| mondrian | 250-2000-4000 / mondrian | 250-2000-4000 / mondrian | λ per group = 0.75/0.6/1.01 | 79.2 | 0.00 | 4119 |

### SC²-PCR, kitti_raw_blind test (1310 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-1000-2000-4000 / giveup | 61.37 | 4084 | +0.38 [+0.69] | True | 1.08× [1.05, 1.11] | 0.125 | 0.46 |
| mondrian: 250-2000-4000 / mondrian | 61.68 | 4628 | +0.08 [+0.23] | True | 0.95× [0.94, 0.97] | 1 | 0.08 |
| fixed budget N=250 (single run) | 6.34 | 97 | | | | | |
| fixed budget N=500 (single run) | 12.75 | 182 | | | | | |
| fixed budget N=1000 (single run) | 24.35 | 425 | | | | | |
| fixed budget N=2000 (single run) | 42.98 | 1256 | | | | | |
| fixed budget N=4000 (single run) | 61.76 | 4411 | | | | | |

### SC²-PCR, kitti_test test (555 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-1000-2000-4000 / giveup | 91.89 | 3111 | +0.36 [+0.90] | True | 1.38× [1.29, 1.48] | 0.625 | 0.54 |
| mondrian: 250-2000-4000 / mondrian | 92.07 | 3721 | +0.18 [+0.54] | True | 1.15× [1.10, 1.21] | 1 | 0.18 |
| fixed budget N=250 (single run) | 12.79 | 92 | | | | | |
| fixed budget N=500 (single run) | 20.72 | 173 | | | | | |
| fixed budget N=1000 (single run) | 39.28 | 407 | | | | | |
| fixed budget N=2000 (single run) | 72.43 | 1210 | | | | | |
| fixed budget N=4000 (single run) | 92.25 | 4294 | | | | | |

## TurboReg

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1238 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-2000-4000 | giveup | 0.5, 0.02 | 0.33 | 3704 |
| 500-2000-4000 | threshold | 0.5 | 0.33 | 3777 |
| 250-2000-4000 | giveup | 0.6, 0.02 | 0.33 | 3857 |
| 250-2000-4000 | threshold | 0.6 | 0.33 | 3930 |
| 250-2000-4000 | mondrian | λ per group = 0.6/0.8/0.5 | 0.00 | 3964 |
| 500-2000-4000 | mondrian | λ per group = 0.5/0.8/0.5 | 0.00 | 3983 |
| 250-1000-2000-4000 | threshold | 0.6 | 0.33 | 4050 |
| 250-1000-2000-4000 | giveup | 0.6, 0 | 0.33 | 4050 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.6/0.88/0.6 | 0.00 | 4282 |
| x4 | threshold | 0.5 | 0.33 | 4365 |
| x4 | giveup | 0.5, 0 | 0.33 | 4365 |
| 250-1000-4000 | threshold | 0.5 | 0.33 | 4365 |
| 250-1000-4000 | giveup | 0.5, 0 | 0.33 | 4365 |
| 250-1000-2000-4000 | mdp | 0 | 0.33 | 4375 |
| doubling | mondrian | λ per group = 0.7/0.88/0.6 | 0.00 | 4499 |
| doubling | threshold | 0.7 | 0.33 | 4510 |
| doubling | giveup | 0.7, 0 | 0.33 | 4510 |
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
| 250-2000-4000 | mdp | -1 | 0.00 | 6977 |
| 500-2000-4000 | mdp | -1 | 0.00 | 7110 |
| doubling | mdp | -1 | 0.00 | 7754 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-2000-4000 / giveup | 500-2000-4000 / giveup | 0.6, 0.02 | 79.2 | 0.24 | 4314 |
| mondrian | 250-2000-4000 / mondrian | 250-2000-4000 / mondrian | λ per group = 0.8/0.6/1.01 | 79.2 | 0.00 | 5220 |

### TurboReg, kitti_raw_blind test (1310 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-2000-4000 / giveup | 62.37 | 5039 | +0.23 [+0.61] | True | 1.07× [1.05, 1.10] | 0.508 | 0.46 |
| mondrian: 250-2000-4000 / mondrian | 62.52 | 5693 | +0.08 [+0.38] | True | 0.95× [0.93, 0.97] | 1 | 0.31 |
| fixed budget N=250 (single run) | 7.18 | 99 | | | | | |
| fixed budget N=500 (single run) | 14.12 | 212 | | | | | |
| fixed budget N=1000 (single run) | 25.50 | 555 | | | | | |
| fixed budget N=2000 (single run) | 44.05 | 1618 | | | | | |
| fixed budget N=4000 (single run) | 62.60 | 5414 | | | | | |

### TurboReg, kitti_test test (555 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-2000-4000 / giveup | 91.35 | 4138 | +0.90 [+1.62] | False | 1.38× [1.30, 1.47] | 0.0625 | 0.90 |
| mondrian: 250-2000-4000 / mondrian | 92.07 | 4997 | +0.18 [+0.72] | True | 1.14× [1.09, 1.20] | 1 | 0.36 |
| fixed budget N=250 (single run) | 14.23 | 103 | | | | | |
| fixed budget N=500 (single run) | 22.34 | 226 | | | | | |
| fixed budget N=1000 (single run) | 42.34 | 574 | | | | | |
| fixed budget N=2000 (single run) | 71.53 | 1631 | | | | | |
| fixed budget N=4000 (single run) | 92.25 | 5697 | | | | | |
