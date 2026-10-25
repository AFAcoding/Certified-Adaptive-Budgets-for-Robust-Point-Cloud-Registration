# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## SC²-PCR

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-4000 | threshold | 0.5 | 0.70 | 1052 |
| 500-4000 | giveup | 0.5, 0 | 0.70 | 1052 |
| x4 | threshold | 0.7 | 0.70 | 1112 |
| x4 | giveup | 0.7, 0 | 0.70 | 1112 |
| 250-1000-4000 | threshold | 0.7 | 0.70 | 1112 |
| 250-1000-4000 | giveup | 0.7, 0 | 0.70 | 1112 |
| 500-2000-4000 | giveup | 0.6, 0.05 | 0.70 | 1126 |
| 500-2000-4000 | threshold | 0.6 | 0.70 | 1130 |
| 250-500-4000 | giveup | 0.75, 0.1 | 0.70 | 1175 |
| 250-500-4000 | threshold | 0.75 | 0.60 | 1177 |
| 250-500-4000 | mdp | 0 | 0.60 | 1212 |
| 250-4000 | giveup | 0.7, 0.1 | 0.70 | 1233 |
| 250-4000 | threshold | 0.7 | 0.60 | 1235 |
| 500-4000 | mondrian | λ per group = 0.5/0.75/0.5 | 0.20 | 1235 |
| x4 | mdp | 0 | 0.50 | 1247 |
| 250-1000-4000 | mdp | 0 | 0.50 | 1247 |
| 250-2000-4000 | mdp | 0 | 0.70 | 1312 |
| 250-4000 | mdp | 0 | 0.50 | 1318 |
| 250-1000-2000-4000 | threshold | 0.75 | 0.70 | 1322 |
| 250-1000-2000-4000 | giveup | 0.75, 0 | 0.70 | 1322 |
| 250-2000-4000 | giveup | 0.8, 0.1 | 0.70 | 1331 |
| 500-2000-4000 | mondrian | λ per group = 0.8/0.75/0.5 | 0.20 | 1332 |
| doubling | threshold | 0.75 | 0.60 | 1343 |
| doubling | giveup | 0.75, 0 | 0.60 | 1343 |
| 500-4000 | mdp | 0 | 0.00 | 1351 |
| 250-1000-2000-4000 | mdp | 0 | 0.50 | 1361 |
| 250-2000-4000 | threshold | 0.8 | 0.50 | 1364 |
| 500-2000-4000 | mdp | 0 | 0.20 | 1366 |
| 250-500-4000 | mondrian | λ per group = 0.7/0.95/0.5 | 0.20 | 1476 |
| x4 | mondrian | λ per group = 0.7/0.95/0.5 | 0.20 | 1487 |
| 250-1000-4000 | mondrian | λ per group = 0.7/0.95/0.5 | 0.20 | 1487 |
| 250-4000 | mondrian | λ per group = 0.5/0.94/0.5 | 0.10 | 1554 |
| 250-2000-4000 | mondrian | λ per group = 0.75/0.92/0.5 | 0.20 | 1568 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.7/0.94/0.5 | 0.20 | 1626 |
| doubling | mondrian | λ per group = 0.75/0.93/0.5 | 0.20 | 1631 |
| full | threshold | 1.01 | 0.00 | 2600 |
| full | mondrian | never stop early | 0.00 | 2600 |
| doubling | mdp | -1 | 0.00 | 3902 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-4000 / threshold | 500-4000 / threshold | 0.75 | 76.7 | 0.70 | 1316 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.6/0.93/0.5 | 77.0 | 0.30 | 1722 |

### SC²-PCR, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 84.51 | 1077 | +0.67 [+1.00] | False | 2.50× [2.37, 2.64] | 0.000519 | 0.72 |
| mondrian: 500-4000 / mondrian | 84.94 | 1485 | +0.24 [+0.48] | True | 1.81× [1.74, 1.89] | 0.125 | 0.29 |
| fixed budget N=250 (single run) | 68.83 | 72 | | | | | |
| fixed budget N=500 (single run) | 73.71 | 142 | | | | | |
| fixed budget N=1000 (single run) | 77.82 | 339 | | | | | |
| fixed budget N=2000 (single run) | 81.88 | 943 | | | | | |
| fixed budget N=4000 (single run) | 85.18 | 2690 | | | | | |

### SC²-PCR, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 40.42 | 2238 | +0.11 [+0.44] | True | 1.10× [1.07, 1.13] | 1 | 0.22 |
| mondrian: 500-4000 / mondrian | 40.42 | 2434 | +0.11 [+0.33] | True | 1.01× [0.99, 1.03] | 1 | 0.11 |
| fixed budget N=250 (single run) | 23.46 | 75 | | | | | |
| fixed budget N=500 (single run) | 27.86 | 150 | | | | | |
| fixed budget N=1000 (single run) | 32.16 | 350 | | | | | |
| fixed budget N=2000 (single run) | 36.12 | 935 | | | | | |
| fixed budget N=4000 (single run) | 40.53 | 2457 | | | | | |

### SC²-PCR, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 80.59 | 1262 | +0.92 [+1.42] | False | 2.24× [2.12, 2.37] | 0.0026 | 1.17 |
| mondrian: 500-4000 / mondrian | 81.21 | 1675 | +0.31 [+0.55] | True | 1.69× [1.62, 1.76] | 0.125 | 0.37 |
| fixed budget N=250 (single run) | 65.13 | 81 | | | | | |
| fixed budget N=500 (single run) | 69.32 | 155 | | | | | |
| fixed budget N=1000 (single run) | 74.25 | 350 | | | | | |
| fixed budget N=2000 (single run) | 78.00 | 961 | | | | | |
| fixed budget N=4000 (single run) | 81.52 | 2825 | | | | | |

### SC²-PCR, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 36.66 | 2381 | -0.06 [+0.17] | True | 1.07× [1.05, 1.08] | 1 | 0.11 |
| mondrian: 500-4000 / mondrian | 36.50 | 2549 | +0.11 [+0.28] | True | 1.00× [0.98, 1.01] | 0.625 | 0.17 |
| fixed budget N=250 (single run) | 21.45 | 84 | | | | | |
| fixed budget N=500 (single run) | 24.71 | 164 | | | | | |
| fixed budget N=1000 (single run) | 28.19 | 367 | | | | | |
| fixed budget N=2000 (single run) | 32.17 | 938 | | | | | |
| fixed budget N=4000 (single run) | 36.61 | 2538 | | | | | |

## TurboReg

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-4000 | threshold | 0.5 | 0.70 | 1853 |
| 500-4000 | giveup | 0.5, 0 | 0.70 | 1853 |
| 250-500-4000 | giveup | 0.7, 0.1 | 0.70 | 1999 |
| 250-500-4000 | threshold | 0.7 | 0.60 | 2000 |
| x4 | giveup | 0.75, 0.1 | 0.70 | 2043 |
| 250-1000-4000 | giveup | 0.75, 0.1 | 0.70 | 2043 |
| x4 | threshold | 0.75 | 0.70 | 2045 |
| 250-1000-4000 | threshold | 0.75 | 0.70 | 2045 |
| 250-4000 | giveup | 0.7, 0.2 | 0.70 | 2076 |
| 500-4000 | mondrian | λ per group = 0.6/0.75/0.5 | 0.10 | 2079 |
| 500-2000-4000 | giveup | 0.7, 0.05 | 0.60 | 2090 |
| 500-2000-4000 | threshold | 0.7 | 0.60 | 2093 |
| 250-4000 | threshold | 0.7 | 0.40 | 2096 |
| 250-500-4000 | mdp | 0 | 0.40 | 2167 |
| 250-2000-4000 | giveup | 0.75, 0.02 | 0.70 | 2198 |
| 250-2000-4000 | threshold | 0.75 | 0.70 | 2200 |
| 500-4000 | mdp | 0 | 0.10 | 2211 |
| 500-2000-4000 | mondrian | λ per group = 0.8/0.75/0.5 | 0.20 | 2236 |
| x4 | mdp | 0 | 0.30 | 2245 |
| 250-1000-4000 | mdp | 0 | 0.30 | 2245 |
| 250-4000 | mdp | 0 | 0.40 | 2263 |
| 250-1000-2000-4000 | mdp | 0 | 0.70 | 2275 |
| 500-2000-4000 | mdp | 0 | 0.20 | 2311 |
| 250-1000-2000-4000 | giveup | 0.8, 0.1 | 0.60 | 2469 |
| 250-1000-2000-4000 | threshold | 0.8 | 0.60 | 2485 |
| 250-4000 | mondrian | λ per group = 0.5/0.93/0.5 | 0.20 | 2551 |
| doubling | giveup | 0.8, 0.05 | 0.70 | 2562 |
| doubling | threshold | 0.8 | 0.70 | 2566 |
| 250-500-4000 | mondrian | λ per group = 0.75/0.96/0.5 | 0.10 | 2703 |
| 250-2000-4000 | mondrian | λ per group = 0.75/0.93/0.5 | 0.20 | 2751 |
| x4 | mondrian | λ per group = 0.85/0.96/0.5 | 0.20 | 2808 |
| 250-1000-4000 | mondrian | λ per group = 0.85/0.96/0.5 | 0.20 | 2808 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.85/0.94/0.5 | 0.10 | 3168 |
| doubling | mondrian | λ per group = 0.85/0.95/0.5 | 0.10 | 3389 |
| full | threshold | 1.01 | 0.00 | 4414 |
| full | mondrian | never stop early | 0.00 | 4414 |
| 250-2000-4000 | mdp | -1 | 0.00 | 6015 |
| doubling | mdp | -1 | 0.00 | 6883 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-4000 / threshold | 500-4000 / threshold | 0.8 | 76.1 | 0.70 | 2348 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.7/0.92/0.95 | 76.4 | 0.30 | 2792 |

### TurboReg, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 85.09 | 1920 | +0.57 [+0.91] | True | 2.33× [2.22, 2.45] | 0.00418 | 0.67 |
| mondrian: 500-4000 / mondrian | 85.23 | 2360 | +0.43 [+0.67] | True | 1.89× [1.81, 1.98] | 0.00391 | 0.43 |
| fixed budget N=250 (single run) | 68.50 | 185 | | | | | |
| fixed budget N=500 (single run) | 73.66 | 319 | | | | | |
| fixed budget N=1000 (single run) | 78.20 | 654 | | | | | |
| fixed budget N=2000 (single run) | 81.98 | 1595 | | | | | |
| fixed budget N=4000 (single run) | 85.66 | 4468 | | | | | |

### TurboReg, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 39.98 | 3755 | +0.22 [+0.55] | True | 1.09× [1.06, 1.12] | 0.625 | 0.33 |
| mondrian: 500-4000 / mondrian | 40.09 | 3991 | +0.11 [+0.33] | True | 1.02× [1.01, 1.05] | 1 | 0.11 |
| fixed budget N=250 (single run) | 23.57 | 146 | | | | | |
| fixed budget N=500 (single run) | 27.64 | 305 | | | | | |
| fixed budget N=1000 (single run) | 32.38 | 650 | | | | | |
| fixed budget N=2000 (single run) | 35.79 | 1591 | | | | | |
| fixed budget N=4000 (single run) | 40.20 | 4089 | | | | | |

### TurboReg, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 81.15 | 2227 | +0.74 [+1.17] | False | 2.10× [2.01, 2.21] | 0.00183 | 0.80 |
| mondrian: 500-4000 / mondrian | 81.27 | 2648 | +0.62 [+0.99] | True | 1.77× [1.70, 1.85] | 0.00635 | 0.68 |
| fixed budget N=250 (single run) | 65.00 | 195 | | | | | |
| fixed budget N=500 (single run) | 69.32 | 341 | | | | | |
| fixed budget N=1000 (single run) | 74.00 | 685 | | | | | |
| fixed budget N=2000 (single run) | 78.31 | 1645 | | | | | |
| fixed budget N=4000 (single run) | 81.89 | 4686 | | | | | |

### TurboReg, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 36.44 | 4034 | +0.11 [+0.34] | True | 1.05× [1.03, 1.06] | 0.688 | 0.22 |
| mondrian: 500-4000 / mondrian | 36.50 | 4167 | +0.06 [+0.28] | True | 1.01× [1.00, 1.03] | 1 | 0.22 |
| fixed budget N=250 (single run) | 21.56 | 146 | | | | | |
| fixed budget N=500 (single run) | 24.93 | 321 | | | | | |
| fixed budget N=1000 (single run) | 28.13 | 679 | | | | | |
| fixed budget N=2000 (single run) | 32.06 | 1592 | | | | | |
| fixed budget N=4000 (single run) | 36.55 | 4224 | | | | | |
