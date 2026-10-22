# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## SC²-PCR

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-500-4000 | giveup | 0.5, 0.15 | 0.50 | 1121 |
| 250-500-4000 | threshold | 0.5 | 0.50 | 1127 |
| 250-4000 | giveup | 0.5, 0.2 | 0.70 | 1137 |
| 500-4000 | giveup | 0.5, 0.15 | 0.40 | 1159 |
| 500-4000 | threshold | 0.5 | 0.40 | 1162 |
| 250-4000 | threshold | 0.5 | 0.40 | 1166 |
| x4 | giveup | 0.6, 0.15 | 0.30 | 1181 |
| 250-1000-4000 | giveup | 0.6, 0.15 | 0.30 | 1181 |
| x4 | threshold | 0.6 | 0.30 | 1189 |
| 250-1000-4000 | threshold | 0.6 | 0.30 | 1189 |
| 250-2000-4000 | threshold | 0.5 | 0.70 | 1195 |
| 250-2000-4000 | giveup | 0.5, 0 | 0.70 | 1195 |
| 500-2000-4000 | giveup | 0.5, 0.15 | 0.60 | 1215 |
| 500-2000-4000 | threshold | 0.5 | 0.40 | 1236 |
| 500-4000 | mondrian | λ per group = 0.5/0.6/0.5 | 0.10 | 1237 |
| 250-500-4000 | mdp | 0 | 0.10 | 1259 |
| 500-4000 | mdp | 0 | 0.10 | 1303 |
| x4 | mdp | 0 | 0.00 | 1310 |
| 250-1000-4000 | mdp | 0 | 0.00 | 1310 |
| 250-1000-2000-4000 | giveup | 0.6, 0.15 | 0.50 | 1335 |
| 250-4000 | mondrian | λ per group = 0.5/0.75/0.5 | 0.10 | 1350 |
| x4 | mondrian | λ per group = 0.5/0.8/0.5 | 0.10 | 1350 |
| 250-1000-4000 | mondrian | λ per group = 0.5/0.8/0.5 | 0.10 | 1350 |
| 500-2000-4000 | mdp | 0 | 0.70 | 1360 |
| 250-1000-2000-4000 | threshold | 0.6 | 0.30 | 1373 |
| doubling | giveup | 0.6, 0.15 | 0.50 | 1392 |
| 250-500-4000 | mondrian | λ per group = 0.5/0.85/0.5 | 0.00 | 1403 |
| doubling | threshold | 0.6 | 0.40 | 1409 |
| 500-2000-4000 | mondrian | λ per group = 0.5/0.7/0.5 | 0.10 | 1433 |
| 250-4000 | mdp | 0 | 0.20 | 1449 |
| 250-1000-2000-4000 | mdp | 0 | 0.10 | 1487 |
| 250-2000-4000 | mondrian | λ per group = 0.5/0.8/0.5 | 0.10 | 1509 |
| 250-2000-4000 | mdp | 0 | 0.10 | 1531 |
| doubling | mdp | 0 | 0.20 | 1559 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.5/0.85/0.5 | 0.00 | 1630 |
| doubling | mondrian | λ per group = 0.6/0.85/0.5 | 0.10 | 1746 |
| full | threshold | 1.01 | 0.00 | 2570 |
| full | mondrian | never stop early | 0.00 | 2570 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-500-4000 / giveup | 250-500-4000 / giveup | 0.85, 0.15 | 76.8 | 0.67 | 1532 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.5/0.93/0.5 | 76.9 | 0.30 | 1787 |

### SC²-PCR, v3_blind_hi test (1976 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 92.91 | 1062 | +0.15 [+0.35] | True | 2.35× [2.23, 2.48] | 0.375 | 0.20 |
| mondrian: 500-4000 / mondrian | 93.07 | 1309 | +0.00 [+0.00] | True | 1.90× [1.83, 1.98] | 1 | 0.00 |
| fixed budget N=250 (single run) | 76.52 | 72 | | | | | |
| fixed budget N=500 (single run) | 80.87 | 140 | | | | | |
| fixed budget N=1000 (single run) | 85.43 | 331 | | | | | |
| fixed budget N=2000 (single run) | 90.74 | 930 | | | | | |
| fixed budget N=4000 (single run) | 93.07 | 2491 | | | | | |

### SC²-PCR, v3_blind_lo test (647 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 52.86 | 2573 | +0.00 [+0.31] | True | 1.09× [1.06, 1.12] | 1 | 0.15 |
| mondrian: 500-4000 / mondrian | 52.86 | 2692 | +0.00 [+0.00] | True | 1.04× [1.02, 1.06] | 1 | 0.00 |
| fixed budget N=250 (single run) | 25.19 | 79 | | | | | |
| fixed budget N=500 (single run) | 30.60 | 162 | | | | | |
| fixed budget N=1000 (single run) | 35.86 | 371 | | | | | |
| fixed budget N=2000 (single run) | 44.05 | 969 | | | | | |
| fixed budget N=4000 (single run) | 52.86 | 2802 | | | | | |

### SC²-PCR, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 85.13 | 1274 | +0.05 [+0.19] | True | 2.11× [2.02, 2.21] | 1 | 0.10 |
| mondrian: 500-4000 / mondrian | 85.13 | 1544 | +0.05 [+0.19] | True | 1.74× [1.68, 1.81] | 1 | 0.10 |
| fixed budget N=250 (single run) | 68.83 | 72 | | | | | |
| fixed budget N=500 (single run) | 73.71 | 142 | | | | | |
| fixed budget N=1000 (single run) | 77.82 | 339 | | | | | |
| fixed budget N=2000 (single run) | 81.88 | 943 | | | | | |
| fixed budget N=4000 (single run) | 85.18 | 2690 | | | | | |

### SC²-PCR, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 40.53 | 2332 | +0.00 [+0.00] | True | 1.05× [1.04, 1.07] | 1 | 0.00 |
| mondrian: 500-4000 / mondrian | 40.53 | 2398 | +0.00 [+0.00] | True | 1.02× [1.01, 1.04] | 1 | 0.00 |
| fixed budget N=250 (single run) | 23.46 | 75 | | | | | |
| fixed budget N=500 (single run) | 27.86 | 150 | | | | | |
| fixed budget N=1000 (single run) | 32.16 | 350 | | | | | |
| fixed budget N=2000 (single run) | 36.12 | 935 | | | | | |
| fixed budget N=4000 (single run) | 40.53 | 2457 | | | | | |

### SC²-PCR, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 81.27 | 1480 | +0.25 [+0.49] | True | 1.91× [1.82, 2.01] | 0.219 | 0.31 |
| mondrian: 500-4000 / mondrian | 81.52 | 1738 | +0.00 [+0.12] | True | 1.63× [1.57, 1.69] | 1 | 0.06 |
| fixed budget N=250 (single run) | 65.13 | 81 | | | | | |
| fixed budget N=500 (single run) | 69.32 | 155 | | | | | |
| fixed budget N=1000 (single run) | 74.25 | 350 | | | | | |
| fixed budget N=2000 (single run) | 78.00 | 961 | | | | | |
| fixed budget N=4000 (single run) | 81.52 | 2825 | | | | | |

### SC²-PCR, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 36.55 | 2436 | +0.06 [+0.17] | True | 1.04× [1.03, 1.06] | 1 | 0.06 |
| mondrian: 500-4000 / mondrian | 36.55 | 2493 | +0.06 [+0.17] | True | 1.02× [1.01, 1.03] | 1 | 0.06 |
| fixed budget N=250 (single run) | 21.45 | 84 | | | | | |
| fixed budget N=500 (single run) | 24.71 | 164 | | | | | |
| fixed budget N=1000 (single run) | 28.19 | 367 | | | | | |
| fixed budget N=2000 (single run) | 32.17 | 938 | | | | | |
| fixed budget N=4000 (single run) | 36.61 | 2538 | | | | | |

## TurboReg

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-4000 | giveup | 0.5, 0.15 | 0.60 | 1960 |
| 500-2000-4000 | giveup | 0.5, 0.05 | 0.60 | 1974 |
| 500-4000 | threshold | 0.5 | 0.50 | 1983 |
| 500-2000-4000 | threshold | 0.5 | 0.60 | 1984 |
| 250-4000 | giveup | 0.5, 0.1 | 0.70 | 2021 |
| 250-4000 | threshold | 0.5 | 0.60 | 2026 |
| 250-500-4000 | giveup | 0.6, 0.05 | 0.60 | 2041 |
| 250-500-4000 | threshold | 0.6 | 0.60 | 2047 |
| 500-4000 | mondrian | λ per group = 0.5/0.6/0.5 | 0.10 | 2080 |
| 500-2000-4000 | mondrian | λ per group = 0.5/0.6/0.5 | 0.20 | 2118 |
| 250-2000-4000 | giveup | 0.6, 0.1 | 0.60 | 2124 |
| 250-2000-4000 | threshold | 0.6 | 0.50 | 2140 |
| x4 | giveup | 0.7, 0.1 | 0.60 | 2167 |
| 250-1000-4000 | giveup | 0.7, 0.1 | 0.60 | 2167 |
| x4 | threshold | 0.7 | 0.50 | 2175 |
| 250-1000-4000 | threshold | 0.7 | 0.50 | 2175 |
| 250-4000 | mdp | 0 | 0.40 | 2220 |
| 250-500-4000 | mdp | 0 | 0.20 | 2239 |
| x4 | mdp | 0 | 0.30 | 2301 |
| 250-1000-4000 | mdp | 0 | 0.30 | 2301 |
| 250-4000 | mondrian | λ per group = 0.5/0.8/0.5 | 0.20 | 2303 |
| 250-500-4000 | mondrian | λ per group = 0.7/0.8/0.5 | 0.20 | 2313 |
| 500-4000 | mdp | 0 | 0.10 | 2423 |
| 250-1000-2000-4000 | giveup | 0.7, 0.1 | 0.70 | 2425 |
| x4 | mondrian | λ per group = 0.92/0.8/0.5 | 0.20 | 2433 |
| 250-1000-4000 | mondrian | λ per group = 0.92/0.8/0.5 | 0.20 | 2433 |
| 250-1000-2000-4000 | threshold | 0.7 | 0.50 | 2452 |
| 250-2000-4000 | mondrian | λ per group = 0.6/0.8/0.5 | 0.20 | 2492 |
| doubling | mdp | 0 | 0.40 | 2512 |
| doubling | giveup | 0.7, 0.05 | 0.60 | 2561 |
| doubling | threshold | 0.7 | 0.60 | 2573 |
| 250-1000-2000-4000 | mdp | 0 | 0.40 | 2622 |
| 250-2000-4000 | mdp | 0 | 0.20 | 2673 |
| 500-2000-4000 | mdp | 0 | 0.10 | 2897 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.93/0.8/0.5 | 0.10 | 2953 |
| doubling | mondrian | λ per group = 0.95/0.8/0.5 | 0.10 | 3069 |
| full | threshold | 1.01 | 0.00 | 4493 |
| full | mondrian | never stop early | 0.00 | 4493 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-4000 / giveup | 500-4000 / giveup | 0.75, 0.15 | 76.1 | 0.73 | 2315 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.5/0.85/0.96 | 76.4 | 0.30 | 2636 |

### TurboReg, v3_blind_hi test (1976 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 92.66 | 1640 | +0.25 [+0.46] | True | 2.55× [2.43, 2.69] | 0.0625 | 0.25 |
| mondrian: 500-4000 / mondrian | 92.91 | 1913 | +0.00 [+0.00] | True | 2.19× [2.09, 2.30] | 1 | 0.00 |
| fixed budget N=250 (single run) | 76.62 | 194 | | | | | |
| fixed budget N=500 (single run) | 81.07 | 327 | | | | | |
| fixed budget N=1000 (single run) | 85.37 | 662 | | | | | |
| fixed budget N=2000 (single run) | 90.38 | 1598 | | | | | |
| fixed budget N=4000 (single run) | 92.91 | 4187 | | | | | |

### TurboReg, v3_blind_lo test (647 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 51.31 | 4048 | +0.46 [+0.93] | True | 1.14× [1.10, 1.18] | 0.25 | 0.46 |
| mondrian: 500-4000 / mondrian | 51.62 | 4280 | +0.15 [+0.46] | True | 1.08× [1.05, 1.11] | 1 | 0.15 |
| fixed budget N=250 (single run) | 25.04 | 154 | | | | | |
| fixed budget N=500 (single run) | 30.60 | 311 | | | | | |
| fixed budget N=1000 (single run) | 36.48 | 648 | | | | | |
| fixed budget N=2000 (single run) | 44.36 | 1587 | | | | | |
| fixed budget N=4000 (single run) | 51.78 | 4613 | | | | | |

### TurboReg, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 84.85 | 1905 | +0.81 [+1.15] | False | 2.35× [2.24, 2.46] | 7.63e-05 | 0.86 |
| mondrian: 500-4000 / mondrian | 85.61 | 2251 | +0.05 [+0.19] | True | 1.99× [1.91, 2.07] | 1 | 0.10 |
| fixed budget N=250 (single run) | 68.50 | 185 | | | | | |
| fixed budget N=500 (single run) | 73.66 | 319 | | | | | |
| fixed budget N=1000 (single run) | 78.20 | 654 | | | | | |
| fixed budget N=2000 (single run) | 81.98 | 1595 | | | | | |
| fixed budget N=4000 (single run) | 85.66 | 4468 | | | | | |

### TurboReg, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 39.65 | 3747 | +0.55 [+1.10] | True | 1.09× [1.07, 1.12] | 0.18 | 0.77 |
| mondrian: 500-4000 / mondrian | 40.20 | 3883 | +0.00 [+0.00] | True | 1.05× [1.04, 1.07] | 1 | 0.00 |
| fixed budget N=250 (single run) | 23.57 | 146 | | | | | |
| fixed budget N=500 (single run) | 27.64 | 305 | | | | | |
| fixed budget N=1000 (single run) | 32.38 | 650 | | | | | |
| fixed budget N=2000 (single run) | 35.79 | 1591 | | | | | |
| fixed budget N=4000 (single run) | 40.20 | 4089 | | | | | |

### TurboReg, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 81.21 | 2259 | +0.68 [+1.05] | False | 2.07× [1.97, 2.18] | 0.00342 | 0.74 |
| mondrian: 500-4000 / mondrian | 81.58 | 2562 | +0.31 [+0.55] | True | 1.83× [1.76, 1.91] | 0.0625 | 0.31 |
| fixed budget N=250 (single run) | 65.00 | 195 | | | | | |
| fixed budget N=500 (single run) | 69.32 | 341 | | | | | |
| fixed budget N=1000 (single run) | 74.00 | 685 | | | | | |
| fixed budget N=2000 (single run) | 78.31 | 1645 | | | | | |
| fixed budget N=4000 (single run) | 81.89 | 4686 | | | | | |

### TurboReg, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 35.93 | 4002 | +0.62 [+0.95] | True | 1.06× [1.04, 1.07] | 0.00342 | 0.67 |
| mondrian: 500-4000 / mondrian | 36.50 | 4040 | +0.06 [+0.17] | True | 1.05× [1.03, 1.06] | 1 | 0.06 |
| fixed budget N=250 (single run) | 21.56 | 146 | | | | | |
| fixed budget N=500 (single run) | 24.93 | 321 | | | | | |
| fixed budget N=1000 (single run) | 28.13 | 679 | | | | | |
| fixed budget N=2000 (single run) | 32.06 | 1592 | | | | | |
| fixed budget N=4000 (single run) | 36.55 | 4224 | | | | | |
