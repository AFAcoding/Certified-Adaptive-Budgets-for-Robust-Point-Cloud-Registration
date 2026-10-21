# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## SC²-PCR

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-4000 | threshold | 0.6 | 0.70 | 1335 |
| 500-4000 | giveup | 0.6, 0 | 0.70 | 1335 |
| 500-4000 | mdp | 0 | 0.40 | 1459 |
| 500-4000 | mondrian | λ per group = 0.5/0.85/0.5 | 0.10 | 1486 |
| 250-4000 | giveup | 0.6, 0.3 | 0.70 | 1516 |
| 250-4000 | threshold | 0.6 | 0.50 | 1526 |
| 250-4000 | mondrian | λ per group = 0.5/0.85/0.5 | 0.10 | 1622 |
| 250-4000 | mdp | 0 | 0.00 | 1755 |
| full | threshold | 1.01 | 0.00 | 2579 |
| full | mondrian | never stop early | 0.00 | 2579 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-4000 / threshold | 500-4000 / threshold | 0.85 | 76.6 | 0.73 | 1534 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.5/0.96/0.98 | 77.1 | 0.20 | 1815 |

### SC²-PCR, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 84.51 | 1356 | +0.67 [+0.96] | True | 1.95× [1.87, 2.04] | 0.000519 | 0.72 |
| mondrian: 500-4000 / mondrian | 85.04 | 1696 | +0.14 [+0.33] | True | 1.56× [1.51, 1.62] | 0.375 | 0.19 |
| fixed budget N=250 (single run) | 55.93 | 51 | | | | | |
| fixed budget N=500 (single run) | 66.44 | 140 | | | | | |
| fixed budget N=1000 (single run) | 75.67 | 379 | | | | | |
| fixed budget N=2000 (single run) | 81.88 | 964 | | | | | |
| fixed budget N=4000 (single run) | 85.18 | 2645 | | | | | |

### SC²-PCR, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 40.42 | 2344 | +0.11 [+0.44] | True | 1.03× [1.01, 1.05] | 1 | 0.22 |
| mondrian: 500-4000 / mondrian | 40.53 | 2484 | +0.00 [+0.00] | True | 0.97× [0.96, 0.98] | 1 | 0.00 |
| fixed budget N=250 (single run) | 14.87 | 55 | | | | | |
| fixed budget N=500 (single run) | 22.69 | 150 | | | | | |
| fixed budget N=1000 (single run) | 30.62 | 383 | | | | | |
| fixed budget N=2000 (single run) | 36.34 | 936 | | | | | |
| fixed budget N=4000 (single run) | 40.53 | 2410 | | | | | |

### SC²-PCR, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 80.90 | 1550 | +0.62 [+0.99] | True | 1.78× [1.70, 1.86] | 0.00195 | 0.62 |
| mondrian: 500-4000 / mondrian | 81.39 | 1881 | +0.12 [+0.31] | True | 1.47× [1.42, 1.52] | 0.5 | 0.12 |
| fixed budget N=250 (single run) | 50.83 | 55 | | | | | |
| fixed budget N=500 (single run) | 61.31 | 143 | | | | | |
| fixed budget N=1000 (single run) | 70.18 | 375 | | | | | |
| fixed budget N=2000 (single run) | 77.08 | 965 | | | | | |
| fixed budget N=4000 (single run) | 81.52 | 2762 | | | | | |

### SC²-PCR, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 36.44 | 2460 | +0.17 [+0.34] | True | 1.00× [0.99, 1.02] | 0.25 | 0.17 |
| mondrian: 500-4000 / mondrian | 36.61 | 2555 | +0.00 [+0.11] | True | 0.97× [0.96, 0.97] | 1 | 0.06 |
| fixed budget N=250 (single run) | 13.31 | 60 | | | | | |
| fixed budget N=500 (single run) | 19.03 | 152 | | | | | |
| fixed budget N=1000 (single run) | 25.44 | 378 | | | | | |
| fixed budget N=2000 (single run) | 32.00 | 933 | | | | | |
| fixed budget N=4000 (single run) | 36.61 | 2470 | | | | | |

## TurboReg

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-500-4000 | threshold | 0.6 | 0.60 | 2040 |
| 250-500-4000 | giveup | 0.6, 0 | 0.60 | 2040 |
| 500-4000 | threshold | 0.6 | 0.40 | 2148 |
| 500-4000 | giveup | 0.6, 0 | 0.40 | 2148 |
| 250-500-4000 | mondrian | λ per group = 0.75/0.75/0.5 | 0.10 | 2186 |
| 500-4000 | mondrian | λ per group = 0.5/0.7/0.5 | 0.10 | 2203 |
| 500-4000 | mdp | 0 | 0.10 | 2209 |
| 250-4000 | giveup | 0.5, 0.3 | 0.60 | 2482 |
| 250-4000 | threshold | 0.5 | 0.60 | 2489 |
| 250-4000 | mondrian | λ per group = 0.5/0.7/0.5 | 0.10 | 2581 |
| 250-500-4000 | mdp | 0 | 0.00 | 2636 |
| 250-4000 | mdp | 0 | 0.10 | 2829 |
| full | threshold | 1.01 | 0.00 | 4384 |
| full | mondrian | never stop early | 0.00 | 4384 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-500-4000 / threshold | 250-500-4000 / threshold | 0.92 | 76.1 | 0.70 | 2926 |
| mondrian | 250-500-4000 / mondrian | 250-500-4000 / mondrian | λ per group = 0.8/0.97/0.99 | 76.3 | 0.37 | 3380 |

### TurboReg, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / threshold | 85.18 | 2234 | +0.48 [+0.76] | True | 1.98× [1.90, 2.07] | 0.00635 | 0.53 |
| mondrian: 250-500-4000 / mondrian | 85.56 | 2727 | +0.10 [+0.29] | True | 1.62× [1.57, 1.69] | 0.688 | 0.19 |
| fixed budget N=250 (single run) | 53.97 | 27 | | | | | |
| fixed budget N=500 (single run) | 66.44 | 144 | | | | | |
| fixed budget N=1000 (single run) | 75.05 | 540 | | | | | |
| fixed budget N=2000 (single run) | 81.84 | 1534 | | | | | |
| fixed budget N=4000 (single run) | 85.66 | 4431 | | | | | |

### TurboReg, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / threshold | 40.09 | 3865 | +0.11 [+0.33] | True | 1.04× [1.03, 1.06] | 1 | 0.11 |
| mondrian: 250-500-4000 / mondrian | 40.09 | 3985 | +0.11 [+0.33] | True | 1.01× [1.00, 1.03] | 1 | 0.11 |
| fixed budget N=250 (single run) | 16.30 | 12 | | | | | |
| fixed budget N=500 (single run) | 22.36 | 89 | | | | | |
| fixed budget N=1000 (single run) | 30.29 | 484 | | | | | |
| fixed budget N=2000 (single run) | 36.56 | 1519 | | | | | |
| fixed budget N=4000 (single run) | 40.20 | 4038 | | | | | |

### TurboReg, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / threshold | 81.02 | 2565 | +0.86 [+1.29] | False | 1.79× [1.71, 1.87] | 0.000122 | 0.86 |
| mondrian: 250-500-4000 / mondrian | 81.58 | 3057 | +0.31 [+0.62] | True | 1.50× [1.45, 1.56] | 0.125 | 0.37 |
| fixed budget N=250 (single run) | 49.04 | 26 | | | | | |
| fixed budget N=500 (single run) | 60.01 | 140 | | | | | |
| fixed budget N=1000 (single run) | 69.25 | 548 | | | | | |
| fixed budget N=2000 (single run) | 76.59 | 1582 | | | | | |
| fixed budget N=4000 (single run) | 81.89 | 4590 | | | | | |

### TurboReg, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / threshold | 36.38 | 3978 | +0.17 [+0.34] | True | 1.03× [1.02, 1.04] | 0.25 | 0.17 |
| mondrian: 250-500-4000 / mondrian | 36.50 | 4062 | +0.06 [+0.22] | True | 1.01× [1.00, 1.02] | 1 | 0.11 |
| fixed budget N=250 (single run) | 13.87 | 11 | | | | | |
| fixed budget N=500 (single run) | 19.03 | 81 | | | | | |
| fixed budget N=1000 (single run) | 25.21 | 469 | | | | | |
| fixed budget N=2000 (single run) | 31.44 | 1517 | | | | | |
| fixed budget N=4000 (single run) | 36.55 | 4100 | | | | | |
