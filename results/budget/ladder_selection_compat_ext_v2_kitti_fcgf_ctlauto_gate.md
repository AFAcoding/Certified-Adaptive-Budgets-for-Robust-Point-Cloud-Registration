# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## SC²-PCR

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1107 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| doubling | threshold | 0.5 | 0.33 | 85 |
| doubling | mdp | 30 | 0.33 | 85 |
| doubling | giveup | 0.5, 0 | 0.33 | 85 |
| x4 | threshold | 0.5 | 0.33 | 85 |
| x4 | mdp | 30 | 0.33 | 85 |
| x4 | giveup | 0.5, 0 | 0.33 | 85 |
| 250-2000-4000 | threshold | 0.5 | 0.33 | 85 |
| 250-2000-4000 | mdp | 30 | 0.33 | 85 |
| 250-2000-4000 | giveup | 0.5, 0 | 0.33 | 85 |
| 250-500-4000 | threshold | 0.5 | 0.33 | 85 |
| 250-500-4000 | mdp | 30 | 0.33 | 85 |
| 250-500-4000 | giveup | 0.5, 0 | 0.33 | 85 |
| 250-1000-2000-4000 | threshold | 0.5 | 0.33 | 85 |
| 250-1000-2000-4000 | mdp | 30 | 0.33 | 85 |
| 250-1000-2000-4000 | giveup | 0.5, 0 | 0.33 | 85 |
| 250-4000 | threshold | 0.5 | 0.33 | 85 |
| 250-4000 | mdp | 30 | 0.33 | 85 |
| 250-4000 | giveup | 0.5, 0 | 0.33 | 85 |
| 250-1000-4000 | threshold | 0.5 | 0.33 | 85 |
| 250-1000-4000 | mdp | 30 | 0.33 | 85 |
| 250-1000-4000 | giveup | 0.5, 0 | 0.33 | 85 |
| 250-2000 | threshold | 0.5 | 0.33 | 85 |
| 250-2000 | mdp | 30 | 0.33 | 85 |
| 250-2000 | giveup | 0.5, 0 | 0.33 | 85 |
| 250-1000-2000 | threshold | 0.5 | 0.33 | 85 |
| 250-1000-2000 | mdp | 30 | 0.33 | 85 |
| 250-1000-2000 | giveup | 0.5, 0 | 0.33 | 85 |
| 250-500-1000-2000 | threshold | 0.5 | 0.33 | 85 |
| 250-500-1000-2000 | mdp | 30 | 0.33 | 85 |
| 250-500-1000-2000 | giveup | 0.5, 0 | 0.33 | 85 |
| 500-2000-4000 | threshold | 0.5 | 0.33 | 147 |
| 500-2000-4000 | mdp | 30 | 0.33 | 147 |
| 500-2000-4000 | giveup | 0.5, 0 | 0.33 | 147 |
| 500-4000 | threshold | 0.5 | 0.33 | 147 |
| 500-4000 | mdp | 30 | 0.33 | 147 |
| 500-4000 | giveup | 0.5, 0 | 0.33 | 147 |
| 500-2000 | threshold | 0.5 | 0.33 | 147 |
| 500-2000 | mdp | 30 | 0.33 | 147 |
| 500-2000 | giveup | 0.5, 0 | 0.33 | 147 |
| fixed-1000 | threshold | 0.5 | 0.33 | 336 |
| fixed-1000 | giveup | 0.5, 0 | 0.33 | 336 |
| 250-2000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 415 |
| 500-2000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 477 |
| 250-1000-2000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 516 |
| 250-500-1000-2000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 551 |
| fixed-2000 | threshold | 0.5 | 0.00 | 1023 |
| fixed-2000 | giveup | 0.5, 0 | 0.00 | 1023 |
| fixed-2000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 1023 |
| 250-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 1342 |
| 250-500-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 1377 |
| 500-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 1402 |
| x4 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 1443 |
| 250-1000-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 1443 |
| 250-2000-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 1672 |
| 500-2000-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 1732 |
| 250-1000-2000-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 1773 |
| doubling | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 1807 |
| full | threshold | 1.01 | 0.00 | 3721 |
| full | mondrian | never stop early | 0.00 | 3721 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | doubling / threshold | full / threshold (fallback) | 1.01 | 86.4 | 0.00 | 3926 |
| mondrian | 250-2000 / mondrian | full / mondrian (fallback) | λ per group = 1.01/1.01/1.01 | 86.4 | 0.00 | 3926 |

### SC²-PCR, fcgfown_kitti_raw_blind test (203 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 92.61 | 3997 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 92.61 | 3997 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 92.12 | 93 | | | | | |
| fixed budget N=500 (single run) | 92.12 | 164 | | | | | |
| fixed budget N=1000 (single run) | 92.61 | 367 | | | | | |
| fixed budget N=2000 (single run) | 91.63 | 1085 | | | | | |
| fixed budget N=4000 (single run) | 92.61 | 3997 | | | | | |

### SC²-PCR, fcgfown_kitti_test test (555 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 93.51 | 3930 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 93.51 | 3930 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 92.43 | 88 | | | | | |
| fixed budget N=500 (single run) | 92.61 | 156 | | | | | |
| fixed budget N=1000 (single run) | 93.15 | 353 | | | | | |
| fixed budget N=2000 (single run) | 92.79 | 1070 | | | | | |
| fixed budget N=4000 (single run) | 93.51 | 3930 | | | | | |

## TurboReg

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1107 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| doubling | threshold | 0.5 | 0.33 | 203 |
| doubling | mdp | 30 | 0.33 | 203 |
| doubling | giveup | 0.5, 0 | 0.33 | 203 |
| x4 | threshold | 0.5 | 0.33 | 203 |
| x4 | mdp | 30 | 0.33 | 203 |
| x4 | giveup | 0.5, 0 | 0.33 | 203 |
| 250-2000-4000 | threshold | 0.5 | 0.33 | 203 |
| 250-2000-4000 | mdp | 30 | 0.33 | 203 |
| 250-2000-4000 | giveup | 0.5, 0 | 0.33 | 203 |
| 250-500-4000 | threshold | 0.5 | 0.33 | 203 |
| 250-500-4000 | mdp | 30 | 0.33 | 203 |
| 250-500-4000 | giveup | 0.5, 0 | 0.33 | 203 |
| 250-1000-2000-4000 | threshold | 0.5 | 0.33 | 203 |
| 250-1000-2000-4000 | mdp | 30 | 0.33 | 203 |
| 250-1000-2000-4000 | giveup | 0.5, 0 | 0.33 | 203 |
| 250-4000 | threshold | 0.5 | 0.33 | 203 |
| 250-4000 | mdp | 30 | 0.33 | 203 |
| 250-4000 | giveup | 0.5, 0 | 0.33 | 203 |
| 250-1000-4000 | threshold | 0.5 | 0.33 | 203 |
| 250-1000-4000 | mdp | 30 | 0.33 | 203 |
| 250-1000-4000 | giveup | 0.5, 0 | 0.33 | 203 |
| 250-2000 | threshold | 0.5 | 0.33 | 203 |
| 250-2000 | mdp | 30 | 0.33 | 203 |
| 250-2000 | giveup | 0.5, 0 | 0.33 | 203 |
| 250-1000-2000 | threshold | 0.5 | 0.33 | 203 |
| 250-1000-2000 | mdp | 30 | 0.33 | 203 |
| 250-1000-2000 | giveup | 0.5, 0 | 0.33 | 203 |
| 250-500-1000-2000 | threshold | 0.5 | 0.33 | 203 |
| 250-500-1000-2000 | mdp | 30 | 0.33 | 203 |
| 250-500-1000-2000 | giveup | 0.5, 0 | 0.33 | 203 |
| 500-2000-4000 | threshold | 0.5 | 0.33 | 334 |
| 500-2000-4000 | mdp | 30 | 0.33 | 334 |
| 500-2000-4000 | giveup | 0.5, 0 | 0.33 | 334 |
| 500-4000 | threshold | 0.5 | 0.33 | 334 |
| 500-4000 | mdp | 30 | 0.33 | 334 |
| 500-4000 | giveup | 0.5, 0 | 0.33 | 334 |
| 500-2000 | threshold | 0.5 | 0.33 | 334 |
| 500-2000 | mdp | 30 | 0.33 | 334 |
| 500-2000 | giveup | 0.5, 0 | 0.33 | 334 |
| fixed-1000 | threshold | 0.5 | 0.33 | 681 |
| fixed-1000 | giveup | 0.5, 0 | 0.33 | 681 |
| 250-2000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 745 |
| 500-2000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 874 |
| 250-1000-2000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 958 |
| 250-500-1000-2000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 1055 |
| fixed-2000 | threshold | 0.5 | 0.00 | 1674 |
| fixed-2000 | giveup | 0.5, 0 | 0.00 | 1674 |
| fixed-2000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 1674 |
| 250-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 2022 |
| 250-500-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 2119 |
| 500-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 2154 |
| x4 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 2234 |
| 250-1000-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 2234 |
| 250-2000-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 2563 |
| 500-2000-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 2694 |
| 250-1000-2000-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 2776 |
| doubling | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 2873 |
| full | threshold | 1.01 | 0.00 | 5578 |
| full | mondrian | never stop early | 0.00 | 5578 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | doubling / threshold | full / threshold (fallback) | 1.01 | 85.6 | 0.00 | 5455 |
| mondrian | 250-2000 / mondrian | full / mondrian (fallback) | λ per group = 1.01/1.01/1.01 | 85.6 | 0.00 | 5455 |

### TurboReg, fcgfown_kitti_raw_blind test (203 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 92.12 | 5496 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 92.12 | 5496 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 92.12 | 208 | | | | | |
| fixed budget N=500 (single run) | 92.61 | 336 | | | | | |
| fixed budget N=1000 (single run) | 92.61 | 694 | | | | | |
| fixed budget N=2000 (single run) | 91.63 | 1687 | | | | | |
| fixed budget N=4000 (single run) | 92.12 | 5496 | | | | | |

### TurboReg, fcgfown_kitti_test test (555 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 93.51 | 5870 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 93.51 | 5870 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 92.43 | 199 | | | | | |
| fixed budget N=500 (single run) | 92.43 | 324 | | | | | |
| fixed budget N=1000 (single run) | 92.97 | 670 | | | | | |
| fixed budget N=2000 (single run) | 92.79 | 1704 | | | | | |
| fixed budget N=4000 (single run) | 93.51 | 5870 | | | | | |
