# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## SC²-PCR

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-4000 | giveup | 0.5, 0.15 | 0.40 | 1144 |
| 500-4000 | threshold | 0.5 | 0.30 | 1148 |
| x4 | threshold | 0.6 | 0.70 | 1165 |
| x4 | giveup | 0.6, 0 | 0.70 | 1165 |
| 250-1000-4000 | threshold | 0.6 | 0.70 | 1165 |
| 250-1000-4000 | giveup | 0.6, 0 | 0.70 | 1165 |
| 500-2000-4000 | giveup | 0.5, 0.15 | 0.70 | 1172 |
| 250-4000 | threshold | 0.5 | 0.70 | 1180 |
| 250-4000 | giveup | 0.5, 0 | 0.70 | 1180 |
| 500-2000-4000 | threshold | 0.5 | 0.50 | 1188 |
| 250-500-4000 | giveup | 0.7, 0.2 | 0.60 | 1258 |
| 250-500-4000 | threshold | 0.7 | 0.50 | 1267 |
| 500-4000 | mondrian | λ per group = 0.5/0.7/0.5 | 0.10 | 1285 |
| 250-500-4000 | mdp | 0 | 0.20 | 1298 |
| 500-4000 | mdp | 0 | 0.10 | 1356 |
| x4 | mdp | 0 | 0.10 | 1363 |
| 250-1000-4000 | mdp | 0 | 0.10 | 1363 |
| 250-2000-4000 | giveup | 0.7, 0.15 | 0.70 | 1368 |
| 250-2000-4000 | threshold | 0.7 | 0.60 | 1376 |
| 250-1000-2000-4000 | giveup | 0.7, 0.15 | 0.70 | 1435 |
| 250-1000-2000-4000 | threshold | 0.7 | 0.60 | 1443 |
| 500-2000-4000 | mdp | 0 | 0.20 | 1446 |
| 250-1000-2000-4000 | mdp | 0 | 0.20 | 1485 |
| doubling | mdp | 0 | 0.30 | 1488 |
| doubling | giveup | 0.7, 0.15 | 0.70 | 1491 |
| doubling | threshold | 0.7 | 0.70 | 1495 |
| 500-2000-4000 | mondrian | λ per group = 0.5/0.8/0.5 | 0.10 | 1496 |
| 250-4000 | mondrian | λ per group = 0.5/0.9/0.5 | 0.10 | 1500 |
| 250-500-4000 | mondrian | λ per group = 0.5/0.92/0.5 | 0.20 | 1508 |
| 250-2000-4000 | mdp | 0 | 0.40 | 1531 |
| x4 | mondrian | λ per group = 0.5/0.93/0.5 | 0.20 | 1551 |
| 250-1000-4000 | mondrian | λ per group = 0.5/0.93/0.5 | 0.20 | 1551 |
| 250-4000 | mdp | 0 | 0.10 | 1577 |
| 250-2000-4000 | mondrian | λ per group = 0.5/0.93/0.5 | 0.10 | 1726 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.5/0.95/0.5 | 0.20 | 1872 |
| doubling | mondrian | λ per group = 0.7/0.96/0.5 | 0.20 | 2113 |
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
| marginal: 500-4000 / giveup | 84.94 | 1167 | +0.24 [+0.48] | True | 2.30× [2.20, 2.42] | 0.125 | 0.29 |
| mondrian: 500-4000 / mondrian | 85.13 | 1589 | +0.05 [+0.19] | True | 1.69× [1.63, 1.76] | 1 | 0.10 |
| fixed budget N=250 (single run) | 68.83 | 72 | | | | | |
| fixed budget N=500 (single run) | 73.71 | 142 | | | | | |
| fixed budget N=1000 (single run) | 77.82 | 339 | | | | | |
| fixed budget N=2000 (single run) | 81.88 | 943 | | | | | |
| fixed budget N=4000 (single run) | 85.18 | 2690 | | | | | |

### SC²-PCR, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 40.31 | 2255 | +0.22 [+0.55] | True | 1.09× [1.07, 1.12] | 0.5 | 0.22 |
| mondrian: 500-4000 / mondrian | 40.53 | 2393 | +0.00 [+0.00] | True | 1.03× [1.02, 1.04] | 1 | 0.00 |
| fixed budget N=250 (single run) | 23.46 | 75 | | | | | |
| fixed budget N=500 (single run) | 27.86 | 150 | | | | | |
| fixed budget N=1000 (single run) | 32.16 | 350 | | | | | |
| fixed budget N=2000 (single run) | 36.12 | 935 | | | | | |
| fixed budget N=4000 (single run) | 40.53 | 2457 | | | | | |

### SC²-PCR, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 81.02 | 1378 | +0.49 [+0.86] | True | 2.05× [1.95, 2.15] | 0.0574 | 0.68 |
| mondrian: 500-4000 / mondrian | 81.45 | 1779 | +0.06 [+0.25] | True | 1.59× [1.53, 1.65] | 1 | 0.12 |
| fixed budget N=250 (single run) | 65.13 | 81 | | | | | |
| fixed budget N=500 (single run) | 69.32 | 155 | | | | | |
| fixed budget N=1000 (single run) | 74.25 | 350 | | | | | |
| fixed budget N=2000 (single run) | 78.00 | 961 | | | | | |
| fixed budget N=4000 (single run) | 81.52 | 2825 | | | | | |

### SC²-PCR, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 36.55 | 2410 | +0.06 [+0.17] | True | 1.05× [1.04, 1.07] | 1 | 0.06 |
| mondrian: 500-4000 / mondrian | 36.55 | 2496 | +0.06 [+0.17] | True | 1.02× [1.01, 1.03] | 1 | 0.06 |
| fixed budget N=250 (single run) | 21.45 | 84 | | | | | |
| fixed budget N=500 (single run) | 24.71 | 164 | | | | | |
| fixed budget N=1000 (single run) | 28.19 | 367 | | | | | |
| fixed budget N=2000 (single run) | 32.17 | 938 | | | | | |
| fixed budget N=4000 (single run) | 36.61 | 2538 | | | | | |

## TurboReg

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-500-4000 | giveup | 0.5, 0.2 | 0.70 | 1893 |
| 250-500-4000 | threshold | 0.5 | 0.60 | 1901 |
| 500-4000 | giveup | 0.5, 0.2 | 0.50 | 1910 |
| 500-4000 | threshold | 0.5 | 0.30 | 1923 |
| 500-2000-4000 | giveup | 0.5, 0.15 | 0.70 | 1964 |
| 500-2000-4000 | threshold | 0.5 | 0.50 | 1977 |
| 250-4000 | threshold | 0.5 | 0.50 | 1990 |
| 250-4000 | giveup | 0.5, 0 | 0.50 | 1990 |
| 250-2000-4000 | giveup | 0.6, 0.15 | 0.60 | 2110 |
| 250-2000-4000 | threshold | 0.6 | 0.60 | 2111 |
| x4 | giveup | 0.7, 0.2 | 0.70 | 2137 |
| 250-1000-4000 | giveup | 0.7, 0.2 | 0.70 | 2137 |
| x4 | threshold | 0.7 | 0.50 | 2146 |
| 250-1000-4000 | threshold | 0.7 | 0.50 | 2146 |
| 500-4000 | mondrian | λ per group = 0.5/0.7/0.5 | 0.10 | 2175 |
| 250-500-4000 | mdp | 0 | 0.20 | 2212 |
| 500-2000-4000 | mondrian | λ per group = 0.5/0.7/0.5 | 0.20 | 2293 |
| x4 | mdp | 0 | 0.10 | 2299 |
| 250-1000-4000 | mdp | 0 | 0.10 | 2299 |
| x4 | mondrian | λ per group = 0.7/0.8/0.5 | 0.20 | 2309 |
| 250-1000-4000 | mondrian | λ per group = 0.7/0.8/0.5 | 0.20 | 2309 |
| 250-4000 | mondrian | λ per group = 0.5/0.8/0.5 | 0.10 | 2320 |
| 250-2000-4000 | mondrian | λ per group = 0.5/0.8/0.5 | 0.10 | 2425 |
| 250-1000-2000-4000 | threshold | 0.7 | 0.50 | 2488 |
| 250-1000-2000-4000 | giveup | 0.7, 0 | 0.50 | 2488 |
| 500-4000 | mdp | 0 | 0.10 | 2524 |
| doubling | giveup | 0.7, 0.2 | 0.70 | 2549 |
| 250-4000 | mdp | 0 | 0.10 | 2554 |
| 250-1000-2000-4000 | mdp | 0 | 0.30 | 2556 |
| doubling | threshold | 0.7 | 0.50 | 2574 |
| 250-500-4000 | mondrian | λ per group = 0.5/0.92/0.5 | 0.20 | 2583 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.7/0.8/0.5 | 0.20 | 2727 |
| doubling | mdp | 0 | 0.60 | 2751 |
| 250-2000-4000 | mdp | 0 | 0.20 | 2754 |
| 500-2000-4000 | mdp | 0 | 0.10 | 2903 |
| doubling | mondrian | λ per group = 0.7/0.93/0.5 | 0.20 | 3355 |
| full | threshold | 1.01 | 0.00 | 4414 |
| full | mondrian | never stop early | 0.00 | 4414 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-500-4000 / giveup | 250-500-4000 / giveup | 0.88, 0.2 | 76.3 | 0.63 | 2634 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.5/0.88/0.995 | 76.5 | 0.30 | 3150 |

### TurboReg, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 85.37 | 2159 | +0.29 [+0.53] | True | 2.07× [1.98, 2.17] | 0.0703 | 0.33 |
| mondrian: 500-4000 / mondrian | 85.66 | 2807 | +0.00 [+0.10] | True | 1.59× [1.54, 1.65] | 1 | 0.05 |
| fixed budget N=250 (single run) | 68.50 | 185 | | | | | |
| fixed budget N=500 (single run) | 73.66 | 319 | | | | | |
| fixed budget N=1000 (single run) | 78.20 | 654 | | | | | |
| fixed budget N=2000 (single run) | 81.98 | 1595 | | | | | |
| fixed budget N=4000 (single run) | 85.66 | 4468 | | | | | |

### TurboReg, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 40.20 | 3921 | +0.00 [+0.22] | True | 1.04× [1.03, 1.06] | 1 | 0.11 |
| mondrian: 500-4000 / mondrian | 40.20 | 4058 | +0.00 [+0.00] | True | 1.01× [1.00, 1.02] | 1 | 0.00 |
| fixed budget N=250 (single run) | 23.57 | 146 | | | | | |
| fixed budget N=500 (single run) | 27.64 | 305 | | | | | |
| fixed budget N=1000 (single run) | 32.38 | 650 | | | | | |
| fixed budget N=2000 (single run) | 35.79 | 1591 | | | | | |
| fixed budget N=4000 (single run) | 40.20 | 4089 | | | | | |

### TurboReg, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 81.45 | 2524 | +0.43 [+0.68] | True | 1.86× [1.78, 1.94] | 0.0156 | 0.43 |
| mondrian: 500-4000 / mondrian | 81.70 | 3187 | +0.18 [+0.37] | True | 1.47× [1.42, 1.52] | 0.25 | 0.18 |
| fixed budget N=250 (single run) | 65.00 | 195 | | | | | |
| fixed budget N=500 (single run) | 69.32 | 341 | | | | | |
| fixed budget N=1000 (single run) | 74.00 | 685 | | | | | |
| fixed budget N=2000 (single run) | 78.31 | 1645 | | | | | |
| fixed budget N=4000 (single run) | 81.89 | 4686 | | | | | |

### TurboReg, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 36.55 | 4080 | +0.00 [+0.00] | True | 1.04× [1.02, 1.05] | 1 | 0.00 |
| mondrian: 500-4000 / mondrian | 36.50 | 4208 | +0.06 [+0.17] | True | 1.00× [1.00, 1.01] | 1 | 0.06 |
| fixed budget N=250 (single run) | 21.56 | 146 | | | | | |
| fixed budget N=500 (single run) | 24.93 | 321 | | | | | |
| fixed budget N=1000 (single run) | 28.13 | 679 | | | | | |
| fixed budget N=2000 (single run) | 32.06 | 1592 | | | | | |
| fixed budget N=4000 (single run) | 36.55 | 4224 | | | | | |
