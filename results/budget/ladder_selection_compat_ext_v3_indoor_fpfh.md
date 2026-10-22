# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## SC²-PCR

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-500-4000 | giveup | 0.5, 0.15 | 0.70 | 1124 |
| 250-500-4000 | threshold | 0.5 | 0.70 | 1129 |
| 500-4000 | giveup | 0.5, 0.15 | 0.40 | 1150 |
| x4 | giveup | 0.6, 0.15 | 0.70 | 1153 |
| 250-1000-4000 | giveup | 0.6, 0.15 | 0.70 | 1153 |
| 500-4000 | threshold | 0.5 | 0.40 | 1153 |
| x4 | threshold | 0.6 | 0.70 | 1165 |
| 250-1000-4000 | threshold | 0.6 | 0.70 | 1165 |
| 250-4000 | threshold | 0.5 | 0.60 | 1172 |
| 250-4000 | giveup | 0.5, 0 | 0.60 | 1172 |
| 500-2000-4000 | giveup | 0.5, 0.1 | 0.50 | 1202 |
| 500-2000-4000 | threshold | 0.5 | 0.50 | 1210 |
| 250-500-4000 | mdp | 0 | 0.10 | 1266 |
| 250-2000-4000 | giveup | 0.6, 0.15 | 0.70 | 1268 |
| 500-4000 | mondrian | λ per group = 0.5/0.7/0.5 | 0.10 | 1288 |
| 250-2000-4000 | threshold | 0.6 | 0.60 | 1294 |
| x4 | mdp | 0 | 0.10 | 1311 |
| 250-1000-4000 | mdp | 0 | 0.10 | 1311 |
| 500-4000 | mdp | 0 | 0.10 | 1313 |
| 250-4000 | mdp | 0 | 0.30 | 1343 |
| 250-1000-2000-4000 | giveup | 0.6, 0.1 | 0.70 | 1355 |
| 250-1000-2000-4000 | threshold | 0.6 | 0.70 | 1357 |
| x4 | mondrian | λ per group = 0.5/0.85/0.5 | 0.10 | 1368 |
| 250-1000-4000 | mondrian | λ per group = 0.5/0.85/0.5 | 0.10 | 1368 |
| 250-500-4000 | mondrian | λ per group = 0.5/0.85/0.5 | 0.20 | 1375 |
| 250-4000 | mondrian | λ per group = 0.5/0.85/0.5 | 0.10 | 1398 |
| 250-1000-2000-4000 | mdp | 0 | 0.20 | 1442 |
| 500-2000-4000 | mondrian | λ per group = 0.5/0.75/0.5 | 0.10 | 1456 |
| doubling | mdp | 0 | 0.30 | 1475 |
| 250-2000-4000 | mdp | 0 | 0.40 | 1500 |
| doubling | giveup | 0.7, 0.15 | 0.60 | 1539 |
| 250-2000-4000 | mondrian | λ per group = 0.5/0.85/0.5 | 0.10 | 1541 |
| doubling | threshold | 0.7 | 0.50 | 1559 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.5/0.85/0.5 | 0.20 | 1592 |
| doubling | mondrian | λ per group = 0.7/0.85/0.5 | 0.10 | 1777 |
| full | threshold | 1.01 | 0.00 | 2570 |
| full | mondrian | never stop early | 0.00 | 2570 |
| 500-2000-4000 | mdp | -1 | 0.00 | 3532 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-500-4000 / giveup | 250-500-4000 / giveup | 0.88, 0.15 | 76.8 | 0.63 | 1554 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.5/0.95/0.5 | 76.9 | 0.30 | 1800 |

### SC²-PCR, v3_blind_hi test (1976 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 92.81 | 1098 | +0.25 [+0.46] | True | 2.27× [2.15, 2.40] | 0.125 | 0.30 |
| mondrian: 500-4000 / mondrian | 93.07 | 1347 | +0.00 [+0.00] | True | 1.85× [1.78, 1.93] | 1 | 0.00 |
| fixed budget N=250 (single run) | 76.52 | 72 | | | | | |
| fixed budget N=500 (single run) | 80.87 | 140 | | | | | |
| fixed budget N=1000 (single run) | 85.43 | 331 | | | | | |
| fixed budget N=2000 (single run) | 90.74 | 930 | | | | | |
| fixed budget N=4000 (single run) | 93.07 | 2491 | | | | | |

### SC²-PCR, v3_blind_lo test (647 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 52.86 | 2680 | +0.00 [+0.31] | True | 1.05× [1.02, 1.08] | 1 | 0.15 |
| mondrian: 500-4000 / mondrian | 52.86 | 2797 | +0.00 [+0.00] | True | 1.00× [0.98, 1.02] | 1 | 0.00 |
| fixed budget N=250 (single run) | 25.19 | 79 | | | | | |
| fixed budget N=500 (single run) | 30.60 | 162 | | | | | |
| fixed budget N=1000 (single run) | 35.86 | 371 | | | | | |
| fixed budget N=2000 (single run) | 44.05 | 969 | | | | | |
| fixed budget N=4000 (single run) | 52.86 | 2802 | | | | | |

### SC²-PCR, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 85.09 | 1338 | +0.10 [+0.24] | True | 2.01× [1.92, 2.11] | 0.625 | 0.14 |
| mondrian: 500-4000 / mondrian | 85.13 | 1601 | +0.05 [+0.19] | True | 1.68× [1.62, 1.74] | 1 | 0.10 |
| fixed budget N=250 (single run) | 68.83 | 72 | | | | | |
| fixed budget N=500 (single run) | 73.71 | 142 | | | | | |
| fixed budget N=1000 (single run) | 77.82 | 339 | | | | | |
| fixed budget N=2000 (single run) | 81.88 | 943 | | | | | |
| fixed budget N=4000 (single run) | 85.18 | 2690 | | | | | |

### SC²-PCR, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 40.20 | 2436 | +0.33 [+0.66] | True | 1.01× [0.99, 1.03] | 0.25 | 0.33 |
| mondrian: 500-4000 / mondrian | 40.53 | 2503 | +0.00 [+0.00] | True | 0.98× [0.97, 0.99] | 1 | 0.00 |
| fixed budget N=250 (single run) | 23.46 | 75 | | | | | |
| fixed budget N=500 (single run) | 27.86 | 150 | | | | | |
| fixed budget N=1000 (single run) | 32.16 | 350 | | | | | |
| fixed budget N=2000 (single run) | 36.12 | 935 | | | | | |
| fixed budget N=4000 (single run) | 40.53 | 2457 | | | | | |

### SC²-PCR, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 81.08 | 1540 | +0.43 [+0.74] | True | 1.83× [1.75, 1.92] | 0.0391 | 0.49 |
| mondrian: 500-4000 / mondrian | 81.45 | 1811 | +0.06 [+0.25] | True | 1.56× [1.50, 1.62] | 1 | 0.12 |
| fixed budget N=250 (single run) | 65.13 | 81 | | | | | |
| fixed budget N=500 (single run) | 69.32 | 155 | | | | | |
| fixed budget N=1000 (single run) | 74.25 | 350 | | | | | |
| fixed budget N=2000 (single run) | 78.00 | 961 | | | | | |
| fixed budget N=4000 (single run) | 81.52 | 2825 | | | | | |

### SC²-PCR, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 36.16 | 2576 | +0.45 [+0.73] | True | 0.99× [0.97, 1.00] | 0.00781 | 0.45 |
| mondrian: 500-4000 / mondrian | 36.55 | 2616 | +0.06 [+0.17] | True | 0.97× [0.96, 0.98] | 1 | 0.06 |
| fixed budget N=250 (single run) | 21.45 | 84 | | | | | |
| fixed budget N=500 (single run) | 24.71 | 164 | | | | | |
| fixed budget N=1000 (single run) | 28.19 | 367 | | | | | |
| fixed budget N=2000 (single run) | 32.17 | 938 | | | | | |
| fixed budget N=4000 (single run) | 36.61 | 2538 | | | | | |

## TurboReg

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-500-4000 | giveup | 0.5, 0.2 | 0.70 | 1979 |
| 250-500-4000 | threshold | 0.5 | 0.60 | 1995 |
| 500-4000 | giveup | 0.5, 0.2 | 0.40 | 2004 |
| 500-4000 | threshold | 0.5 | 0.20 | 2023 |
| 250-4000 | giveup | 0.5, 0.15 | 0.70 | 2030 |
| 250-4000 | threshold | 0.5 | 0.60 | 2032 |
| x4 | giveup | 0.6, 0.15 | 0.60 | 2056 |
| 250-1000-4000 | giveup | 0.6, 0.15 | 0.60 | 2056 |
| x4 | threshold | 0.6 | 0.60 | 2057 |
| 250-1000-4000 | threshold | 0.6 | 0.60 | 2057 |
| 500-2000-4000 | giveup | 0.5, 0.15 | 0.40 | 2123 |
| 500-2000-4000 | threshold | 0.5 | 0.40 | 2135 |
| 250-4000 | mdp | 0 | 0.20 | 2218 |
| 250-2000-4000 | giveup | 0.6, 0.15 | 0.60 | 2257 |
| 250-2000-4000 | threshold | 0.6 | 0.50 | 2264 |
| 250-500-4000 | mdp | 0 | 0.10 | 2270 |
| 250-4000 | mondrian | λ per group = 0.5/0.75/0.5 | 0.10 | 2273 |
| 500-4000 | mondrian | λ per group = 0.5/0.7/0.5 | 0.10 | 2283 |
| 500-4000 | mdp | 0 | 0.10 | 2315 |
| 250-500-4000 | mondrian | λ per group = 0.5/0.8/0.5 | 0.10 | 2323 |
| x4 | mondrian | λ per group = 0.5/0.8/0.5 | 0.10 | 2339 |
| 250-1000-4000 | mondrian | λ per group = 0.5/0.8/0.5 | 0.10 | 2339 |
| 250-1000-2000-4000 | threshold | 0.6 | 0.70 | 2364 |
| 250-1000-2000-4000 | giveup | 0.6, 0 | 0.70 | 2364 |
| x4 | mdp | 0 | 0.20 | 2394 |
| 250-1000-4000 | mdp | 0 | 0.20 | 2394 |
| 250-2000-4000 | mondrian | λ per group = 0.5/0.75/0.5 | 0.10 | 2421 |
| 500-2000-4000 | mondrian | λ per group = 0.5/0.7/0.5 | 0.20 | 2465 |
| doubling | giveup | 0.6, 0.15 | 0.70 | 2469 |
| doubling | threshold | 0.6 | 0.70 | 2475 |
| 500-2000-4000 | mdp | 0 | 0.50 | 2484 |
| 250-2000-4000 | mdp | 0 | 0.30 | 2529 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.5/0.8/0.5 | 0.10 | 2691 |
| 250-1000-2000-4000 | mdp | 0 | 0.40 | 2703 |
| doubling | mdp | 0 | 0.40 | 2744 |
| doubling | mondrian | λ per group = 0.6/0.8/0.5 | 0.20 | 2913 |
| full | threshold | 1.01 | 0.00 | 4493 |
| full | mondrian | never stop early | 0.00 | 4493 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-500-4000 / giveup | 250-500-4000 / giveup | 0.88, 0.2 | 76.3 | 0.67 | 2656 |
| mondrian | 250-4000 / mondrian | 250-4000 / mondrian | λ per group = 0.5/0.96/0.995 | 76.5 | 0.27 | 3277 |

### TurboReg, v3_blind_hi test (1976 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 92.56 | 1933 | +0.35 [+0.56] | True | 2.17× [2.06, 2.28] | 0.0156 | 0.35 |
| mondrian: 250-4000 / mondrian | 92.81 | 2596 | +0.10 [+0.20] | True | 1.61× [1.56, 1.67] | 0.5 | 0.10 |
| fixed budget N=250 (single run) | 76.62 | 194 | | | | | |
| fixed budget N=500 (single run) | 81.07 | 327 | | | | | |
| fixed budget N=1000 (single run) | 85.37 | 662 | | | | | |
| fixed budget N=2000 (single run) | 90.38 | 1598 | | | | | |
| fixed budget N=4000 (single run) | 92.91 | 4187 | | | | | |

### TurboReg, v3_blind_lo test (647 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 51.00 | 4454 | +0.77 [+1.39] | True | 1.04× [1.01, 1.07] | 0.0625 | 0.77 |
| mondrian: 250-4000 / mondrian | 51.78 | 4568 | +0.00 [+0.00] | True | 1.01× [1.00, 1.03] | 1 | 0.00 |
| fixed budget N=250 (single run) | 25.04 | 154 | | | | | |
| fixed budget N=500 (single run) | 30.60 | 311 | | | | | |
| fixed budget N=1000 (single run) | 36.48 | 648 | | | | | |
| fixed budget N=2000 (single run) | 44.36 | 1587 | | | | | |
| fixed budget N=4000 (single run) | 51.78 | 4613 | | | | | |

### TurboReg, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 85.18 | 2251 | +0.48 [+0.76] | True | 1.98× [1.90, 2.08] | 0.00635 | 0.53 |
| mondrian: 250-4000 / mondrian | 85.56 | 2985 | +0.10 [+0.24] | True | 1.50× [1.45, 1.54] | 0.625 | 0.14 |
| fixed budget N=250 (single run) | 68.50 | 185 | | | | | |
| fixed budget N=500 (single run) | 73.66 | 319 | | | | | |
| fixed budget N=1000 (single run) | 78.20 | 654 | | | | | |
| fixed budget N=2000 (single run) | 81.98 | 1595 | | | | | |
| fixed budget N=4000 (single run) | 85.66 | 4468 | | | | | |

### TurboReg, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 39.98 | 4114 | +0.22 [+0.55] | True | 0.99× [0.98, 1.01] | 0.625 | 0.33 |
| mondrian: 250-4000 / mondrian | 40.20 | 4151 | +0.00 [+0.00] | True | 0.99× [0.98, 0.99] | 1 | 0.00 |
| fixed budget N=250 (single run) | 23.57 | 146 | | | | | |
| fixed budget N=500 (single run) | 27.64 | 305 | | | | | |
| fixed budget N=1000 (single run) | 32.38 | 650 | | | | | |
| fixed budget N=2000 (single run) | 35.79 | 1591 | | | | | |
| fixed budget N=4000 (single run) | 40.20 | 4089 | | | | | |

### TurboReg, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 81.27 | 2649 | +0.62 [+0.92] | True | 1.77× [1.69, 1.85] | 0.00195 | 0.62 |
| mondrian: 250-4000 / mondrian | 81.70 | 3358 | +0.18 [+0.37] | True | 1.40× [1.35, 1.44] | 0.25 | 0.18 |
| fixed budget N=250 (single run) | 65.00 | 195 | | | | | |
| fixed budget N=500 (single run) | 69.32 | 341 | | | | | |
| fixed budget N=1000 (single run) | 74.00 | 685 | | | | | |
| fixed budget N=2000 (single run) | 78.31 | 1645 | | | | | |
| fixed budget N=4000 (single run) | 81.89 | 4686 | | | | | |

### TurboReg, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 35.37 | 4303 | +1.18 [+1.63] | True | 0.98× [0.97, 0.99] | 9.54e-07 | 1.18 |
| mondrian: 250-4000 / mondrian | 36.55 | 4306 | +0.00 [+0.11] | True | 0.98× [0.98, 0.99] | 1 | 0.06 |
| fixed budget N=250 (single run) | 21.56 | 146 | | | | | |
| fixed budget N=500 (single run) | 24.93 | 321 | | | | | |
| fixed budget N=1000 (single run) | 28.13 | 679 | | | | | |
| fixed budget N=2000 (single run) | 32.06 | 1592 | | | | | |
| fixed budget N=4000 (single run) | 36.55 | 4224 | | | | | |
