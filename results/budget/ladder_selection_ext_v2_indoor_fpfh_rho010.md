# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## SC²-PCR

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-4000 | giveup | 0.6, 0.3 | 0.70 | 1516 |
| 250-4000 | threshold | 0.6 | 0.50 | 1526 |
| 250-4000 | mondrian | λ per group = 0.5/0.85/0.5 | 0.10 | 1622 |
| 250-4000 | mdp | 0 | 0.00 | 1755 |
| full | threshold | 1.01 | 0.00 | 2579 |
| full | mondrian | never stop early | 0.00 | 2579 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-4000 / giveup | 250-4000 / giveup | 0.9, 0.3 | 76.6 | 0.70 | 1678 |
| mondrian | 250-4000 / mondrian | 250-4000 / mondrian | λ per group = 0.5/0.93/0.995 | 77.0 | 0.23 | 2056 |

### SC²-PCR, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / giveup | 84.80 | 1525 | +0.38 [+0.62] | True | 1.73× [1.67, 1.80] | 0.0215 | 0.43 |
| mondrian: 250-4000 / mondrian | 85.23 | 2013 | -0.05 [+0.00] | True | 1.31× [1.28, 1.35] | 1 | 0.00 |
| fixed budget N=250 (single run) | 55.93 | 51 | | | | | |
| fixed budget N=500 (single run) | 66.44 | 140 | | | | | |
| fixed budget N=1000 (single run) | 75.67 | 379 | | | | | |
| fixed budget N=2000 (single run) | 81.88 | 964 | | | | | |
| fixed budget N=4000 (single run) | 85.18 | 2645 | | | | | |

### SC²-PCR, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / giveup | 40.20 | 2335 | +0.33 [+0.66] | True | 1.03× [1.02, 1.05] | 0.25 | 0.33 |
| mondrian: 250-4000 / mondrian | 40.31 | 2433 | +0.22 [+0.55] | True | 0.99× [0.98, 1.00] | 0.5 | 0.22 |
| fixed budget N=250 (single run) | 14.87 | 55 | | | | | |
| fixed budget N=500 (single run) | 22.69 | 150 | | | | | |
| fixed budget N=1000 (single run) | 30.62 | 383 | | | | | |
| fixed budget N=2000 (single run) | 36.34 | 936 | | | | | |
| fixed budget N=4000 (single run) | 40.53 | 2410 | | | | | |

### SC²-PCR, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / giveup | 80.71 | 1698 | +0.80 [+1.17] | False | 1.63× [1.56, 1.69] | 0.000244 | 0.80 |
| mondrian: 250-4000 / mondrian | 81.33 | 2170 | +0.18 [+0.37] | True | 1.27× [1.24, 1.31] | 0.25 | 0.18 |
| fixed budget N=250 (single run) | 50.83 | 55 | | | | | |
| fixed budget N=500 (single run) | 61.31 | 143 | | | | | |
| fixed budget N=1000 (single run) | 70.18 | 375 | | | | | |
| fixed budget N=2000 (single run) | 77.08 | 965 | | | | | |
| fixed budget N=4000 (single run) | 81.52 | 2762 | | | | | |

### SC²-PCR, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / giveup | 36.50 | 2415 | +0.11 [+0.28] | True | 1.02× [1.01, 1.03] | 0.5 | 0.11 |
| mondrian: 250-4000 / mondrian | 36.55 | 2497 | +0.06 [+0.17] | True | 0.99× [0.98, 0.99] | 1 | 0.06 |
| fixed budget N=250 (single run) | 13.31 | 60 | | | | | |
| fixed budget N=500 (single run) | 19.03 | 152 | | | | | |
| fixed budget N=1000 (single run) | 25.44 | 378 | | | | | |
| fixed budget N=2000 (single run) | 32.00 | 933 | | | | | |
| fixed budget N=4000 (single run) | 36.61 | 2470 | | | | | |

## TurboReg

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-4000 | giveup | 0.5, 0.3 | 0.60 | 2482 |
| 250-4000 | threshold | 0.5 | 0.60 | 2489 |
| 250-4000 | mondrian | λ per group = 0.5/0.7/0.5 | 0.10 | 2581 |
| 250-4000 | mdp | 0 | 0.10 | 2829 |
| full | threshold | 1.01 | 0.00 | 4384 |
| full | mondrian | never stop early | 0.00 | 4384 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-4000 / giveup | 250-4000 / giveup | 0.88, 0.3 | 76.1 | 0.67 | 3162 |
| mondrian | 250-4000 / mondrian | 250-4000 / mondrian | λ per group = 0.5/0.93/0.99 | 76.5 | 0.20 | 3732 |

### TurboReg, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / giveup | 85.13 | 2451 | +0.53 [+0.81] | True | 1.81× [1.74, 1.88] | 0.00342 | 0.57 |
| mondrian: 250-4000 / mondrian | 85.61 | 3095 | +0.05 [+0.19] | True | 1.43× [1.39, 1.47] | 1 | 0.10 |
| fixed budget N=250 (single run) | 53.97 | 27 | | | | | |
| fixed budget N=500 (single run) | 66.44 | 144 | | | | | |
| fixed budget N=1000 (single run) | 75.05 | 540 | | | | | |
| fixed budget N=2000 (single run) | 81.84 | 1534 | | | | | |
| fixed budget N=4000 (single run) | 85.66 | 4431 | | | | | |

### TurboReg, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / giveup | 40.31 | 3842 | -0.11 [+0.00] | True | 1.05× [1.04, 1.07] | 1 | 0.00 |
| mondrian: 250-4000 / mondrian | 40.20 | 3991 | +0.00 [+0.00] | True | 1.01× [1.01, 1.02] | 1 | 0.00 |
| fixed budget N=250 (single run) | 16.30 | 12 | | | | | |
| fixed budget N=500 (single run) | 22.36 | 89 | | | | | |
| fixed budget N=1000 (single run) | 30.29 | 484 | | | | | |
| fixed budget N=2000 (single run) | 36.56 | 1519 | | | | | |
| fixed budget N=4000 (single run) | 40.20 | 4038 | | | | | |

### TurboReg, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / giveup | 80.96 | 2778 | +0.92 [+1.36] | False | 1.65× [1.59, 1.72] | 6.1e-05 | 0.92 |
| mondrian: 250-4000 / mondrian | 81.76 | 3423 | +0.12 [+0.31] | True | 1.34× [1.30, 1.38] | 0.5 | 0.12 |
| fixed budget N=250 (single run) | 49.04 | 26 | | | | | |
| fixed budget N=500 (single run) | 60.01 | 140 | | | | | |
| fixed budget N=1000 (single run) | 69.25 | 548 | | | | | |
| fixed budget N=2000 (single run) | 76.59 | 1582 | | | | | |
| fixed budget N=4000 (single run) | 81.89 | 4590 | | | | | |

### TurboReg, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / giveup | 36.27 | 3921 | +0.28 [+0.51] | True | 1.05× [1.04, 1.06] | 0.0625 | 0.28 |
| mondrian: 250-4000 / mondrian | 36.50 | 4049 | +0.06 [+0.17] | True | 1.01× [1.01, 1.02] | 1 | 0.06 |
| fixed budget N=250 (single run) | 13.87 | 11 | | | | | |
| fixed budget N=500 (single run) | 19.03 | 81 | | | | | |
| fixed budget N=1000 (single run) | 25.21 | 469 | | | | | |
| fixed budget N=2000 (single run) | 31.44 | 1517 | | | | | |
| fixed budget N=4000 (single run) | 36.55 | 4100 | | | | | |
