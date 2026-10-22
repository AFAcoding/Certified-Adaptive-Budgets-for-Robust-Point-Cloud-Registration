# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## SC²-PCR

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-4000 | threshold | 0.5 | 0.70 | 1259 |
| 500-4000 | giveup | 0.5, 0 | 0.70 | 1259 |
| 500-4000 | mdp | 0 | 0.30 | 1342 |
| 250-500-4000 | threshold | 0.75 | 0.70 | 1371 |
| 250-500-4000 | giveup | 0.75, 0 | 0.70 | 1371 |
| 500-4000 | mondrian | λ per group = 0.5/0.8/0.5 | 0.00 | 1397 |
| x4 | giveup | 0.8, 0.2 | 0.60 | 1416 |
| 250-1000-4000 | giveup | 0.8, 0.2 | 0.60 | 1416 |
| x4 | threshold | 0.8 | 0.60 | 1429 |
| 250-1000-4000 | threshold | 0.8 | 0.60 | 1429 |
| x4 | mdp | 0 | 0.50 | 1443 |
| 250-1000-4000 | mdp | 0 | 0.50 | 1443 |
| 500-2000-4000 | giveup | 0.7, 0.15 | 0.60 | 1504 |
| 500-2000-4000 | threshold | 0.7 | 0.50 | 1518 |
| 250-4000 | threshold | 0.7 | 0.60 | 1543 |
| 250-4000 | giveup | 0.7, 0 | 0.60 | 1543 |
| 250-500-4000 | mondrian | λ per group = 0.75/0.92/0.5 | 0.20 | 1548 |
| 500-2000-4000 | mondrian | λ per group = 0.5/0.85/0.5 | 0.10 | 1568 |
| 250-2000-4000 | mdp | 0 | 0.30 | 1571 |
| x4 | mondrian | λ per group = 0.7/0.94/0.5 | 0.20 | 1592 |
| 250-1000-4000 | mondrian | λ per group = 0.7/0.94/0.5 | 0.20 | 1592 |
| 250-2000-4000 | giveup | 0.75, 0.2 | 0.70 | 1602 |
| 250-1000-2000-4000 | mdp | 0 | 0.60 | 1611 |
| 250-2000-4000 | threshold | 0.75 | 0.70 | 1623 |
| 500-2000-4000 | mdp | 0 | 0.50 | 1690 |
| 250-4000 | mondrian | λ per group = 0.5/0.92/0.5 | 0.10 | 1696 |
| 250-1000-2000-4000 | giveup | 0.8, 0.15 | 0.70 | 1710 |
| 250-2000-4000 | mondrian | λ per group = 0.5/0.93/0.5 | 0.20 | 1726 |
| 250-1000-2000-4000 | threshold | 0.8 | 0.70 | 1736 |
| 250-4000 | mdp | 0 | 0.10 | 1748 |
| doubling | giveup | 0.85, 0.15 | 0.60 | 1892 |
| doubling | threshold | 0.85 | 0.50 | 1904 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.7/0.95/0.5 | 0.20 | 1974 |
| doubling | mondrian | λ per group = 0.85/0.94/0.5 | 0.20 | 2115 |
| full | threshold | 1.01 | 0.00 | 2551 |
| full | mondrian | never stop early | 0.00 | 2551 |
| 250-500-4000 | mdp | -1 | 0.00 | 2761 |
| doubling | mdp | -1 | 0.00 | 4070 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-4000 / threshold | 500-4000 / threshold | 0.85 | 76.6 | 0.73 | 1544 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.5/0.95/0.98 | 77.1 | 0.23 | 1796 |

### SC²-PCR, v3_blind_hi test (1976 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 92.71 | 1126 | +0.35 [+0.61] | True | 2.18× [2.07, 2.29] | 0.0156 | 0.35 |
| mondrian: 500-4000 / mondrian | 93.07 | 1380 | +0.00 [+0.00] | True | 1.77× [1.71, 1.85] | 1 | 0.00 |
| fixed budget N=250 (single run) | 58.65 | 54 | | | | | |
| fixed budget N=500 (single run) | 72.12 | 144 | | | | | |
| fixed budget N=1000 (single run) | 83.00 | 373 | | | | | |
| fixed budget N=2000 (single run) | 90.28 | 948 | | | | | |
| fixed budget N=4000 (single run) | 93.07 | 2449 | | | | | |

### SC²-PCR, v3_blind_lo test (647 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 53.01 | 2637 | -0.15 [+0.00] | True | 1.04× [1.02, 1.07] | 1 | 0.00 |
| mondrian: 500-4000 / mondrian | 52.86 | 2750 | +0.00 [+0.00] | True | 1.00× [0.99, 1.02] | 1 | 0.00 |
| fixed budget N=250 (single run) | 14.37 | 60 | | | | | |
| fixed budget N=500 (single run) | 22.87 | 157 | | | | | |
| fixed budget N=1000 (single run) | 34.47 | 399 | | | | | |
| fixed budget N=2000 (single run) | 46.37 | 994 | | | | | |
| fixed budget N=4000 (single run) | 52.86 | 2755 | | | | | |

### SC²-PCR, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 84.51 | 1362 | +0.67 [+0.96] | True | 1.94× [1.86, 2.03] | 0.000519 | 0.72 |
| mondrian: 500-4000 / mondrian | 84.99 | 1661 | +0.19 [+0.38] | True | 1.59× [1.54, 1.65] | 0.219 | 0.24 |
| fixed budget N=250 (single run) | 55.93 | 51 | | | | | |
| fixed budget N=500 (single run) | 66.44 | 140 | | | | | |
| fixed budget N=1000 (single run) | 75.67 | 379 | | | | | |
| fixed budget N=2000 (single run) | 81.88 | 964 | | | | | |
| fixed budget N=4000 (single run) | 85.18 | 2645 | | | | | |

### SC²-PCR, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 40.42 | 2356 | +0.11 [+0.44] | True | 1.02× [1.01, 1.04] | 1 | 0.22 |
| mondrian: 500-4000 / mondrian | 40.53 | 2481 | +0.00 [+0.00] | True | 0.97× [0.96, 0.98] | 1 | 0.00 |
| fixed budget N=250 (single run) | 14.87 | 55 | | | | | |
| fixed budget N=500 (single run) | 22.69 | 150 | | | | | |
| fixed budget N=1000 (single run) | 30.62 | 383 | | | | | |
| fixed budget N=2000 (single run) | 36.34 | 936 | | | | | |
| fixed budget N=4000 (single run) | 40.53 | 2410 | | | | | |

### SC²-PCR, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 80.90 | 1563 | +0.62 [+0.99] | True | 1.77× [1.69, 1.85] | 0.00195 | 0.62 |
| mondrian: 500-4000 / mondrian | 81.33 | 1862 | +0.18 [+0.37] | True | 1.48× [1.43, 1.54] | 0.25 | 0.18 |
| fixed budget N=250 (single run) | 50.83 | 55 | | | | | |
| fixed budget N=500 (single run) | 61.31 | 143 | | | | | |
| fixed budget N=1000 (single run) | 70.18 | 375 | | | | | |
| fixed budget N=2000 (single run) | 77.08 | 965 | | | | | |
| fixed budget N=4000 (single run) | 81.52 | 2762 | | | | | |

### SC²-PCR, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 36.50 | 2472 | +0.11 [+0.28] | True | 1.00× [0.99, 1.01] | 0.5 | 0.11 |
| mondrian: 500-4000 / mondrian | 36.61 | 2554 | +0.00 [+0.11] | True | 0.97× [0.96, 0.97] | 1 | 0.06 |
| fixed budget N=250 (single run) | 13.31 | 60 | | | | | |
| fixed budget N=500 (single run) | 19.03 | 152 | | | | | |
| fixed budget N=1000 (single run) | 25.44 | 378 | | | | | |
| fixed budget N=2000 (single run) | 32.00 | 933 | | | | | |
| fixed budget N=4000 (single run) | 36.61 | 2470 | | | | | |

## TurboReg

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| x4 | threshold | 0.6 | 0.50 | 1893 |
| x4 | giveup | 0.6, 0 | 0.50 | 1893 |
| 250-1000-4000 | threshold | 0.6 | 0.50 | 1893 |
| 250-1000-4000 | giveup | 0.6, 0 | 0.50 | 1893 |
| 250-500-4000 | mdp | 0 | 0.40 | 1977 |
| x4 | mdp | 0 | 0.20 | 2009 |
| 250-1000-4000 | mdp | 0 | 0.20 | 2009 |
| 500-2000-4000 | threshold | 0.5 | 0.70 | 2012 |
| 500-2000-4000 | giveup | 0.5, 0 | 0.70 | 2012 |
| 250-500-4000 | threshold | 0.6 | 0.50 | 2035 |
| 250-500-4000 | giveup | 0.6, 0 | 0.50 | 2035 |
| 500-4000 | threshold | 0.5 | 0.40 | 2036 |
| 500-4000 | giveup | 0.5, 0 | 0.40 | 2036 |
| x4 | mondrian | λ per group = 0.5/0.8/0.5 | 0.20 | 2041 |
| 250-1000-4000 | mondrian | λ per group = 0.5/0.8/0.5 | 0.20 | 2041 |
| 250-2000-4000 | threshold | 0.5 | 0.70 | 2107 |
| 250-2000-4000 | giveup | 0.5, 0 | 0.70 | 2107 |
| 250-500-4000 | mondrian | λ per group = 0.7/0.7/0.5 | 0.20 | 2130 |
| 250-1000-2000-4000 | giveup | 0.6, 0.15 | 0.70 | 2183 |
| 250-1000-2000-4000 | threshold | 0.6 | 0.70 | 2186 |
| 500-4000 | mondrian | λ per group = 0.5/0.7/0.5 | 0.10 | 2187 |
| doubling | mdp | 0 | 0.40 | 2205 |
| 500-2000-4000 | mdp | 0 | 0.50 | 2265 |
| 500-2000-4000 | mondrian | λ per group = 0.5/0.75/0.5 | 0.20 | 2287 |
| doubling | giveup | 0.7, 0.2 | 0.40 | 2355 |
| 500-4000 | mdp | 0 | 0.10 | 2364 |
| doubling | threshold | 0.7 | 0.30 | 2384 |
| 250-2000-4000 | mondrian | λ per group = 0.5/0.8/0.5 | 0.10 | 2426 |
| 250-2000-4000 | mdp | 0 | 0.20 | 2430 |
| 250-4000 | giveup | 0.5, 0.3 | 0.60 | 2435 |
| 250-4000 | threshold | 0.5 | 0.60 | 2442 |
| 250-4000 | mondrian | λ per group = 0.5/0.7/0.5 | 0.10 | 2535 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.6/0.85/0.5 | 0.10 | 2591 |
| doubling | mondrian | λ per group = 0.7/0.85/0.5 | 0.00 | 2645 |
| 250-4000 | mdp | 0 | 0.00 | 2855 |
| full | threshold | 1.01 | 0.00 | 4345 |
| full | mondrian | never stop early | 0.00 | 4345 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 6390 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | x4 / threshold | x4 / threshold | 0.93 | 76.1 | 0.73 | 3139 |
| mondrian | x4 / mondrian | x4 / mondrian | λ per group = 0.93/0.96/0.99 | 76.5 | 0.30 | 3646 |

### TurboReg, v3_blind_hi test (1976 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / threshold | 92.61 | 1997 | +0.30 [+0.51] | True | 2.07× [1.97, 2.18] | 0.0312 | 0.30 |
| mondrian: x4 / mondrian | 92.86 | 2440 | +0.05 [+0.15] | True | 1.69× [1.63, 1.77] | 1 | 0.05 |
| fixed budget N=250 (single run) | 57.34 | 24 | | | | | |
| fixed budget N=500 (single run) | 70.85 | 151 | | | | | |
| fixed budget N=1000 (single run) | 82.14 | 568 | | | | | |
| fixed budget N=2000 (single run) | 89.78 | 1541 | | | | | |
| fixed budget N=4000 (single run) | 92.91 | 4132 | | | | | |

### TurboReg, v3_blind_lo test (647 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / threshold | 51.78 | 4569 | +0.00 [+0.00] | True | 0.99× [0.97, 1.02] | 1 | 0.00 |
| mondrian: x4 / mondrian | 51.78 | 4700 | +0.00 [+0.00] | True | 0.97× [0.95, 0.99] | 1 | 0.00 |
| fixed budget N=250 (single run) | 13.45 | 11 | | | | | |
| fixed budget N=500 (single run) | 23.18 | 83 | | | | | |
| fixed budget N=1000 (single run) | 34.00 | 463 | | | | | |
| fixed budget N=2000 (single run) | 46.83 | 1518 | | | | | |
| fixed budget N=4000 (single run) | 51.78 | 4545 | | | | | |

### TurboReg, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / threshold | 85.37 | 2390 | +0.29 [+0.53] | True | 1.85× [1.78, 1.93] | 0.0703 | 0.33 |
| mondrian: x4 / mondrian | 85.66 | 2966 | +0.00 [+0.10] | True | 1.49× [1.45, 1.55] | 1 | 0.05 |
| fixed budget N=250 (single run) | 53.97 | 27 | | | | | |
| fixed budget N=500 (single run) | 66.44 | 144 | | | | | |
| fixed budget N=1000 (single run) | 75.05 | 540 | | | | | |
| fixed budget N=2000 (single run) | 81.84 | 1534 | | | | | |
| fixed budget N=4000 (single run) | 85.66 | 4431 | | | | | |

### TurboReg, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / threshold | 40.09 | 4285 | +0.11 [+0.33] | True | 0.94× [0.93, 0.96] | 1 | 0.11 |
| mondrian: x4 / mondrian | 40.09 | 4410 | +0.11 [+0.33] | True | 0.92× [0.91, 0.93] | 1 | 0.11 |
| fixed budget N=250 (single run) | 16.30 | 12 | | | | | |
| fixed budget N=500 (single run) | 22.36 | 89 | | | | | |
| fixed budget N=1000 (single run) | 30.29 | 484 | | | | | |
| fixed budget N=2000 (single run) | 36.56 | 1519 | | | | | |
| fixed budget N=4000 (single run) | 40.20 | 4038 | | | | | |

### TurboReg, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / threshold | 81.33 | 2713 | +0.55 [+0.86] | True | 1.69× [1.62, 1.77] | 0.00391 | 0.55 |
| mondrian: x4 / mondrian | 81.76 | 3283 | +0.12 [+0.31] | True | 1.40× [1.35, 1.45] | 0.5 | 0.12 |
| fixed budget N=250 (single run) | 49.04 | 26 | | | | | |
| fixed budget N=500 (single run) | 60.01 | 140 | | | | | |
| fixed budget N=1000 (single run) | 69.25 | 548 | | | | | |
| fixed budget N=2000 (single run) | 76.59 | 1582 | | | | | |
| fixed budget N=4000 (single run) | 81.89 | 4590 | | | | | |

### TurboReg, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / threshold | 36.50 | 4352 | +0.06 [+0.17] | True | 0.94× [0.93, 0.95] | 1 | 0.06 |
| mondrian: x4 / mondrian | 36.50 | 4456 | +0.06 [+0.17] | True | 0.92× [0.91, 0.93] | 1 | 0.06 |
| fixed budget N=250 (single run) | 13.87 | 11 | | | | | |
| fixed budget N=500 (single run) | 19.03 | 81 | | | | | |
| fixed budget N=1000 (single run) | 25.21 | 469 | | | | | |
| fixed budget N=2000 (single run) | 31.44 | 1517 | | | | | |
| fixed budget N=4000 (single run) | 36.55 | 4100 | | | | | |
