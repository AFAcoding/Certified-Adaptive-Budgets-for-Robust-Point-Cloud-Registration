# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## SC²-PCR

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-4000 | giveup | 0.5, 0.15 | 0.40 | 1144 |
| 500-4000 | threshold | 0.5 | 0.30 | 1148 |
| 250-4000 | threshold | 0.5 | 0.70 | 1180 |
| 250-4000 | giveup | 0.5, 0 | 0.70 | 1180 |
| 250-500-4000 | giveup | 0.7, 0.2 | 0.60 | 1258 |
| 250-500-4000 | threshold | 0.7 | 0.50 | 1267 |
| 500-4000 | mondrian | λ per group = 0.5/0.7/0.5 | 0.10 | 1285 |
| 250-500-4000 | mdp | 0 | 0.20 | 1298 |
| 500-4000 | mdp | 0 | 0.10 | 1356 |
| 250-4000 | mondrian | λ per group = 0.5/0.9/0.5 | 0.10 | 1500 |
| 250-500-4000 | mondrian | λ per group = 0.5/0.92/0.5 | 0.20 | 1508 |
| 250-4000 | mdp | 0 | 0.10 | 1577 |
| full | threshold | 1.01 | 0.00 | 2600 |
| full | mondrian | never stop early | 0.00 | 2600 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-4000 / giveup | 500-4000 / giveup | 0.75, 0.15 | 76.7 | 0.73 | 1368 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.5/0.96/0.5 | 76.9 | 0.30 | 1812 |

### SC²-PCR, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 84.89 | 1166 | +0.29 [+0.53] | True | 2.31× [2.20, 2.42] | 0.0703 | 0.33 |
| mondrian: 500-4000 / mondrian | 85.13 | 1612 | +0.05 [+0.19] | True | 1.67× [1.61, 1.73] | 1 | 0.10 |
| fixed budget N=250 (single run) | 68.83 | 72 | | | | | |
| fixed budget N=500 (single run) | 73.71 | 142 | | | | | |
| fixed budget N=1000 (single run) | 77.82 | 339 | | | | | |
| fixed budget N=2000 (single run) | 81.88 | 943 | | | | | |
| fixed budget N=4000 (single run) | 85.18 | 2690 | | | | | |

### SC²-PCR, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 40.20 | 2283 | +0.33 [+0.66] | True | 1.08× [1.05, 1.10] | 0.25 | 0.33 |
| mondrian: 500-4000 / mondrian | 40.53 | 2501 | +0.00 [+0.00] | True | 0.98× [0.97, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 23.46 | 75 | | | | | |
| fixed budget N=500 (single run) | 27.86 | 150 | | | | | |
| fixed budget N=1000 (single run) | 32.16 | 350 | | | | | |
| fixed budget N=2000 (single run) | 36.12 | 935 | | | | | |
| fixed budget N=4000 (single run) | 40.53 | 2457 | | | | | |

### SC²-PCR, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 81.02 | 1385 | +0.49 [+0.86] | True | 2.04× [1.94, 2.15] | 0.0574 | 0.68 |
| mondrian: 500-4000 / mondrian | 81.52 | 1820 | +0.00 [+0.18] | True | 1.55× [1.50, 1.61] | 1 | 0.12 |
| fixed budget N=250 (single run) | 65.13 | 81 | | | | | |
| fixed budget N=500 (single run) | 69.32 | 155 | | | | | |
| fixed budget N=1000 (single run) | 74.25 | 350 | | | | | |
| fixed budget N=2000 (single run) | 78.00 | 961 | | | | | |
| fixed budget N=4000 (single run) | 81.52 | 2825 | | | | | |

### SC²-PCR, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 36.55 | 2463 | +0.06 [+0.17] | True | 1.03× [1.02, 1.05] | 1 | 0.06 |
| mondrian: 500-4000 / mondrian | 36.55 | 2614 | +0.06 [+0.17] | True | 0.97× [0.96, 0.98] | 1 | 0.06 |
| fixed budget N=250 (single run) | 21.45 | 84 | | | | | |
| fixed budget N=500 (single run) | 24.71 | 164 | | | | | |
| fixed budget N=1000 (single run) | 28.19 | 367 | | | | | |
| fixed budget N=2000 (single run) | 32.17 | 938 | | | | | |
| fixed budget N=4000 (single run) | 36.61 | 2538 | | | | | |

## TurboReg

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-4000 | giveup | 0.5, 0.2 | 0.50 | 1910 |
| 500-4000 | threshold | 0.5 | 0.30 | 1923 |
| 250-4000 | threshold | 0.5 | 0.50 | 1990 |
| 250-4000 | giveup | 0.5, 0 | 0.50 | 1990 |
| 500-4000 | mondrian | λ per group = 0.5/0.7/0.5 | 0.10 | 2175 |
| 250-4000 | mondrian | λ per group = 0.5/0.8/0.5 | 0.10 | 2320 |
| 500-4000 | mdp | 0 | 0.10 | 2524 |
| 250-4000 | mdp | 0 | 0.10 | 2554 |
| full | threshold | 1.01 | 0.00 | 4414 |
| full | mondrian | never stop early | 0.00 | 4414 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-4000 / giveup | 500-4000 / giveup | 0.7, 0.2 | 76.1 | 0.73 | 2245 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.5/0.88/0.995 | 76.5 | 0.30 | 3150 |

### TurboReg, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 84.99 | 1873 | +0.67 [+1.00] | False | 2.39× [2.28, 2.51] | 0.000519 | 0.72 |
| mondrian: 500-4000 / mondrian | 85.66 | 2841 | +0.00 [+0.10] | True | 1.57× [1.52, 1.63] | 1 | 0.05 |
| fixed budget N=250 (single run) | 68.50 | 185 | | | | | |
| fixed budget N=500 (single run) | 73.66 | 319 | | | | | |
| fixed budget N=1000 (single run) | 78.20 | 654 | | | | | |
| fixed budget N=2000 (single run) | 81.98 | 1595 | | | | | |
| fixed budget N=4000 (single run) | 85.66 | 4468 | | | | | |

### TurboReg, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 39.98 | 3748 | +0.22 [+0.55] | True | 1.09× [1.06, 1.12] | 0.625 | 0.33 |
| mondrian: 500-4000 / mondrian | 40.20 | 4154 | +0.00 [+0.00] | True | 0.98× [0.97, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 23.57 | 146 | | | | | |
| fixed budget N=500 (single run) | 27.64 | 305 | | | | | |
| fixed budget N=1000 (single run) | 32.38 | 650 | | | | | |
| fixed budget N=2000 (single run) | 35.79 | 1591 | | | | | |
| fixed budget N=4000 (single run) | 40.20 | 4089 | | | | | |

### TurboReg, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 81.27 | 2242 | +0.62 [+0.99] | True | 2.09× [1.99, 2.20] | 0.00635 | 0.68 |
| mondrian: 500-4000 / mondrian | 81.70 | 3233 | +0.18 [+0.37] | True | 1.45× [1.40, 1.50] | 0.25 | 0.18 |
| fixed budget N=250 (single run) | 65.00 | 195 | | | | | |
| fixed budget N=500 (single run) | 69.32 | 341 | | | | | |
| fixed budget N=1000 (single run) | 74.00 | 685 | | | | | |
| fixed budget N=2000 (single run) | 78.31 | 1645 | | | | | |
| fixed budget N=4000 (single run) | 81.89 | 4686 | | | | | |

### TurboReg, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 36.16 | 4055 | +0.39 [+0.67] | True | 1.04× [1.03, 1.06] | 0.0391 | 0.45 |
| mondrian: 500-4000 / mondrian | 36.50 | 4358 | +0.06 [+0.17] | True | 0.97× [0.96, 0.98] | 1 | 0.06 |
| fixed budget N=250 (single run) | 21.56 | 146 | | | | | |
| fixed budget N=500 (single run) | 24.93 | 321 | | | | | |
| fixed budget N=1000 (single run) | 28.13 | 679 | | | | | |
| fixed budget N=2000 (single run) | 32.06 | 1592 | | | | | |
| fixed budget N=4000 (single run) | 36.55 | 4224 | | | | | |
