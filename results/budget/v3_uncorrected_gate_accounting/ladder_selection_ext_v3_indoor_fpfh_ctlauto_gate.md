# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## SC²-PCR

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| x4 | mdp | 0 | 0.50 | 1256 |
| 250-1000-4000 | mdp | 0 | 0.50 | 1256 |
| 500-4000 | giveup | 0.6, 0.15 | 0.60 | 1258 |
| 500-4000 | threshold | 0.6 | 0.60 | 1273 |
| 500-4000 | mdp | 0 | 0.20 | 1336 |
| 500-4000 | mondrian | λ per group = 0.5/0.8/0.5 | 0.10 | 1384 |
| 250-500-4000 | giveup | 0.8, 0.1 | 0.70 | 1398 |
| 250-500-4000 | threshold | 0.8 | 0.70 | 1405 |
| 250-1000-2000-4000 | mdp | 0 | 0.60 | 1481 |
| x4 | giveup | 0.85, 0.1 | 0.50 | 1516 |
| 250-1000-4000 | giveup | 0.85, 0.1 | 0.50 | 1516 |
| x4 | threshold | 0.85 | 0.50 | 1519 |
| 250-1000-4000 | threshold | 0.85 | 0.50 | 1519 |
| 500-2000-4000 | giveup | 0.75, 0.1 | 0.40 | 1523 |
| 500-2000-4000 | threshold | 0.75 | 0.40 | 1545 |
| 250-2000-4000 | mdp | 0 | 0.50 | 1545 |
| 250-500-4000 | mdp | 0 | 0.60 | 1552 |
| 250-4000 | giveup | 0.75, 0.15 | 0.70 | 1552 |
| 250-4000 | threshold | 0.75 | 0.70 | 1556 |
| 500-2000-4000 | mdp | 0 | 0.40 | 1567 |
| 500-2000-4000 | mondrian | λ per group = 0.5/0.88/0.5 | 0.20 | 1579 |
| 250-500-4000 | mondrian | λ per group = 0.8/0.93/0.5 | 0.20 | 1612 |
| x4 | mondrian | λ per group = 0.7/0.96/0.5 | 0.20 | 1718 |
| 250-1000-4000 | mondrian | λ per group = 0.7/0.96/0.5 | 0.20 | 1718 |
| 250-4000 | mondrian | λ per group = 0.5/0.94/0.5 | 0.10 | 1726 |
| 250-4000 | mdp | 0 | 0.20 | 1736 |
| 250-2000-4000 | giveup | 0.85, 0.15 | 0.70 | 1768 |
| 250-1000-2000-4000 | giveup | 0.85, 0.1 | 0.60 | 1799 |
| 250-2000-4000 | threshold | 0.85 | 0.50 | 1812 |
| 250-1000-2000-4000 | threshold | 0.85 | 0.60 | 1829 |
| doubling | giveup | 0.85, 0.1 | 0.70 | 1842 |
| doubling | threshold | 0.85 | 0.50 | 1876 |
| 250-2000-4000 | mondrian | λ per group = 0.7/0.95/0.5 | 0.10 | 1972 |
| doubling | mondrian | λ per group = 0.85/0.94/0.5 | 0.10 | 2175 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.75/0.97/0.5 | 0.20 | 2205 |
| full | threshold | 1.01 | 0.00 | 2551 |
| full | mondrian | never stop early | 0.00 | 2551 |
| doubling | mdp | -1 | 0.00 | 4070 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | x4 / mdp | full / threshold (fallback) | 1.01 | 77.2 | 0.00 | 2554 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.5/0.93/0.96 | 77.1 | 0.23 | 1733 |

### SC²-PCR, v3_blind_hi test (1976 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 93.07 | 2465 | +0.00 [+0.00] | True | 0.99× [0.99, 0.99] | 1 | 0.00 |
| mondrian: 500-4000 / mondrian | 93.02 | 1327 | +0.05 [+0.15] | True | 1.85× [1.78, 1.92] | 1 | 0.05 |
| fixed budget N=250 (single run) | 58.65 | 54 | | | | | |
| fixed budget N=500 (single run) | 72.12 | 144 | | | | | |
| fixed budget N=1000 (single run) | 83.00 | 373 | | | | | |
| fixed budget N=2000 (single run) | 90.28 | 948 | | | | | |
| fixed budget N=4000 (single run) | 93.07 | 2449 | | | | | |

### SC²-PCR, v3_blind_lo test (647 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 52.86 | 2771 | +0.00 [+0.00] | True | 0.99× [0.99, 0.99] | 1 | 0.00 |
| mondrian: 500-4000 / mondrian | 52.86 | 2638 | +0.00 [+0.00] | True | 1.04× [1.03, 1.07] | 1 | 0.00 |
| fixed budget N=250 (single run) | 14.37 | 60 | | | | | |
| fixed budget N=500 (single run) | 22.87 | 157 | | | | | |
| fixed budget N=1000 (single run) | 34.47 | 399 | | | | | |
| fixed budget N=2000 (single run) | 46.37 | 994 | | | | | |
| fixed budget N=4000 (single run) | 52.86 | 2755 | | | | | |

### SC²-PCR, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 85.18 | 2661 | +0.00 [+0.00] | True | 0.99× [0.99, 0.99] | 1 | 0.00 |
| mondrian: 500-4000 / mondrian | 85.04 | 1577 | +0.14 [+0.33] | True | 1.68× [1.62, 1.74] | 0.375 | 0.19 |
| fixed budget N=250 (single run) | 55.93 | 51 | | | | | |
| fixed budget N=500 (single run) | 66.44 | 140 | | | | | |
| fixed budget N=1000 (single run) | 75.67 | 379 | | | | | |
| fixed budget N=2000 (single run) | 81.88 | 964 | | | | | |
| fixed budget N=4000 (single run) | 85.18 | 2645 | | | | | |

### SC²-PCR, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 40.53 | 2425 | +0.00 [+0.00] | True | 0.99× [0.99, 0.99] | 1 | 0.00 |
| mondrian: 500-4000 / mondrian | 40.42 | 2375 | +0.11 [+0.33] | True | 1.01× [1.00, 1.03] | 1 | 0.11 |
| fixed budget N=250 (single run) | 14.87 | 55 | | | | | |
| fixed budget N=500 (single run) | 22.69 | 150 | | | | | |
| fixed budget N=1000 (single run) | 30.62 | 383 | | | | | |
| fixed budget N=2000 (single run) | 36.34 | 936 | | | | | |
| fixed budget N=4000 (single run) | 40.53 | 2410 | | | | | |

### SC²-PCR, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 81.52 | 2778 | +0.00 [+0.00] | True | 0.99× [0.99, 0.99] | 1 | 0.00 |
| mondrian: 500-4000 / mondrian | 81.27 | 1748 | +0.25 [+0.43] | True | 1.58× [1.52, 1.64] | 0.125 | 0.25 |
| fixed budget N=250 (single run) | 50.83 | 55 | | | | | |
| fixed budget N=500 (single run) | 61.31 | 143 | | | | | |
| fixed budget N=1000 (single run) | 70.18 | 375 | | | | | |
| fixed budget N=2000 (single run) | 77.08 | 965 | | | | | |
| fixed budget N=4000 (single run) | 81.52 | 2762 | | | | | |

### SC²-PCR, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 36.61 | 2485 | +0.00 [+0.00] | True | 0.99× [0.99, 0.99] | 1 | 0.00 |
| mondrian: 500-4000 / mondrian | 36.50 | 2427 | +0.11 [+0.22] | True | 1.02× [1.01, 1.03] | 0.5 | 0.11 |
| fixed budget N=250 (single run) | 13.31 | 60 | | | | | |
| fixed budget N=500 (single run) | 19.03 | 152 | | | | | |
| fixed budget N=1000 (single run) | 25.44 | 378 | | | | | |
| fixed budget N=2000 (single run) | 32.00 | 933 | | | | | |
| fixed budget N=4000 (single run) | 36.61 | 2470 | | | | | |

## TurboReg

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| x4 | giveup | 0.6, 0.05 | 0.30 | 1956 |
| 250-1000-4000 | giveup | 0.6, 0.05 | 0.30 | 1956 |
| x4 | threshold | 0.6 | 0.30 | 1962 |
| 250-1000-4000 | threshold | 0.6 | 0.30 | 1962 |
| x4 | mondrian | λ per group = 0.5/0.7/0.5 | 0.10 | 2007 |
| 250-1000-4000 | mondrian | λ per group = 0.5/0.7/0.5 | 0.10 | 2007 |
| 250-500-4000 | mondrian | λ per group = 0.5/0.6/0.5 | 0.20 | 2055 |
| 500-4000 | giveup | 0.5, 0.2 | 0.50 | 2058 |
| 500-4000 | threshold | 0.5 | 0.40 | 2060 |
| 500-2000-4000 | threshold | 0.5 | 0.60 | 2063 |
| 500-2000-4000 | giveup | 0.5, 0 | 0.60 | 2063 |
| x4 | mdp | 0 | 0.30 | 2084 |
| 250-1000-4000 | mdp | 0 | 0.30 | 2084 |
| 250-500-4000 | giveup | 0.6, 0.1 | 0.10 | 2091 |
| 250-500-4000 | threshold | 0.6 | 0.10 | 2096 |
| 250-2000-4000 | giveup | 0.5, 0.05 | 0.70 | 2114 |
| 250-2000-4000 | threshold | 0.5 | 0.70 | 2120 |
| 250-500-4000 | mdp | 0 | 0.30 | 2134 |
| doubling | mdp | 0 | 0.70 | 2164 |
| 500-4000 | mondrian | λ per group = 0.5/0.6/0.5 | 0.10 | 2174 |
| doubling | giveup | 0.6, 0.2 | 0.60 | 2208 |
| doubling | threshold | 0.6 | 0.60 | 2223 |
| 500-4000 | mdp | 0 | 0.10 | 2227 |
| 250-1000-2000-4000 | giveup | 0.6, 0.2 | 0.60 | 2231 |
| 250-1000-2000-4000 | threshold | 0.6 | 0.50 | 2255 |
| 500-2000-4000 | mondrian | λ per group = 0.5/0.7/0.5 | 0.20 | 2325 |
| 250-2000-4000 | mdp | 0 | 0.40 | 2422 |
| 500-2000-4000 | mdp | 0 | 0.30 | 2430 |
| doubling | mondrian | λ per group = 0.6/0.75/0.5 | 0.20 | 2431 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.6/0.75/0.5 | 0.10 | 2464 |
| 250-4000 | giveup | 0.5, 0.3 | 0.40 | 2476 |
| 250-4000 | threshold | 0.5 | 0.40 | 2487 |
| 250-2000-4000 | mondrian | λ per group = 0.5/0.8/0.5 | 0.20 | 2524 |
| 250-4000 | mondrian | λ per group = 0.5/0.6/0.5 | 0.10 | 2544 |
| 250-4000 | mdp | 0 | 0.10 | 2760 |
| full | threshold | 1.01 | 0.00 | 4345 |
| full | mondrian | never stop early | 0.00 | 4345 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 6393 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | x4 / giveup | x4 / giveup | 0.9, 0.05 | 76.1 | 0.67 | 3219 |
| mondrian | x4 / mondrian | x4 / mondrian | λ per group = 0.85/0.93/0.98 | 76.4 | 0.37 | 3680 |

### TurboReg, v3_blind_hi test (1976 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / giveup | 92.66 | 2015 | +0.25 [+0.46] | True | 2.05× [1.96, 2.15] | 0.0625 | 0.25 |
| mondrian: x4 / mondrian | 92.86 | 2484 | +0.05 [+0.15] | True | 1.66× [1.60, 1.73] | 1 | 0.05 |
| fixed budget N=250 (single run) | 57.34 | 24 | | | | | |
| fixed budget N=500 (single run) | 70.85 | 151 | | | | | |
| fixed budget N=1000 (single run) | 82.14 | 568 | | | | | |
| fixed budget N=2000 (single run) | 89.78 | 1541 | | | | | |
| fixed budget N=4000 (single run) | 92.91 | 4132 | | | | | |

### TurboReg, v3_blind_lo test (647 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / giveup | 51.78 | 4349 | +0.00 [+0.00] | True | 1.05× [1.02, 1.07] | 1 | 0.00 |
| mondrian: x4 / mondrian | 51.78 | 4494 | +0.00 [+0.00] | True | 1.01× [1.00, 1.03] | 1 | 0.00 |
| fixed budget N=250 (single run) | 13.45 | 11 | | | | | |
| fixed budget N=500 (single run) | 23.18 | 83 | | | | | |
| fixed budget N=1000 (single run) | 34.00 | 463 | | | | | |
| fixed budget N=2000 (single run) | 46.83 | 1518 | | | | | |
| fixed budget N=4000 (single run) | 51.78 | 4545 | | | | | |

### TurboReg, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / giveup | 85.33 | 2378 | +0.33 [+0.57] | True | 1.86× [1.79, 1.94] | 0.0391 | 0.38 |
| mondrian: x4 / mondrian | 85.61 | 2920 | +0.05 [+0.19] | True | 1.52× [1.47, 1.57] | 1 | 0.10 |
| fixed budget N=250 (single run) | 53.97 | 27 | | | | | |
| fixed budget N=500 (single run) | 66.44 | 144 | | | | | |
| fixed budget N=1000 (single run) | 75.05 | 540 | | | | | |
| fixed budget N=2000 (single run) | 81.84 | 1534 | | | | | |
| fixed budget N=4000 (single run) | 85.66 | 4431 | | | | | |

### TurboReg, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / giveup | 40.20 | 3955 | +0.00 [+0.00] | True | 1.02× [1.01, 1.04] | 1 | 0.00 |
| mondrian: x4 / mondrian | 40.20 | 4058 | +0.00 [+0.00] | True | 1.00× [0.99, 1.01] | 1 | 0.00 |
| fixed budget N=250 (single run) | 16.30 | 12 | | | | | |
| fixed budget N=500 (single run) | 22.36 | 89 | | | | | |
| fixed budget N=1000 (single run) | 30.29 | 484 | | | | | |
| fixed budget N=2000 (single run) | 36.56 | 1519 | | | | | |
| fixed budget N=4000 (single run) | 40.20 | 4038 | | | | | |

### TurboReg, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / giveup | 81.39 | 2696 | +0.49 [+0.80] | True | 1.70× [1.63, 1.77] | 0.00781 | 0.49 |
| mondrian: x4 / mondrian | 81.70 | 3221 | +0.18 [+0.37] | True | 1.42× [1.38, 1.48] | 0.25 | 0.18 |
| fixed budget N=250 (single run) | 49.04 | 26 | | | | | |
| fixed budget N=500 (single run) | 60.01 | 140 | | | | | |
| fixed budget N=1000 (single run) | 69.25 | 548 | | | | | |
| fixed budget N=2000 (single run) | 76.59 | 1582 | | | | | |
| fixed budget N=4000 (single run) | 81.89 | 4590 | | | | | |

### TurboReg, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / giveup | 36.50 | 4016 | +0.06 [+0.17] | True | 1.02× [1.01, 1.03] | 1 | 0.06 |
| mondrian: x4 / mondrian | 36.50 | 4116 | +0.06 [+0.17] | True | 1.00× [0.99, 1.00] | 1 | 0.06 |
| fixed budget N=250 (single run) | 13.87 | 11 | | | | | |
| fixed budget N=500 (single run) | 19.03 | 81 | | | | | |
| fixed budget N=1000 (single run) | 25.21 | 469 | | | | | |
| fixed budget N=2000 (single run) | 31.44 | 1517 | | | | | |
| fixed budget N=4000 (single run) | 36.55 | 4100 | | | | | |
