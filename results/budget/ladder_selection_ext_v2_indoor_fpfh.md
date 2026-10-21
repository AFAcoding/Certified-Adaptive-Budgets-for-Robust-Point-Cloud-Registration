# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## SC²-PCR

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| x4 | threshold | 0.75 | 0.70 | 1329 |
| x4 | giveup | 0.75, 0 | 0.70 | 1329 |
| 250-1000-4000 | threshold | 0.75 | 0.70 | 1329 |
| 250-1000-4000 | giveup | 0.75, 0 | 0.70 | 1329 |
| 500-4000 | threshold | 0.6 | 0.70 | 1335 |
| 500-4000 | giveup | 0.6, 0 | 0.70 | 1335 |
| 250-2000-4000 | giveup | 0.6, 0.2 | 0.60 | 1360 |
| 250-2000-4000 | threshold | 0.6 | 0.60 | 1368 |
| 250-500-4000 | threshold | 0.75 | 0.60 | 1392 |
| 250-500-4000 | giveup | 0.75, 0 | 0.60 | 1392 |
| 500-4000 | mdp | 0 | 0.40 | 1459 |
| 250-500-4000 | mondrian | λ per group = 0.8/0.88/0.5 | 0.20 | 1481 |
| 500-2000-4000 | giveup | 0.7, 0.15 | 0.70 | 1486 |
| 500-4000 | mondrian | λ per group = 0.5/0.85/0.5 | 0.10 | 1486 |
| 500-2000-4000 | threshold | 0.7 | 0.70 | 1487 |
| 250-4000 | giveup | 0.6, 0.3 | 0.70 | 1516 |
| 250-4000 | threshold | 0.6 | 0.50 | 1526 |
| 250-2000-4000 | mondrian | λ per group = 0.5/0.88/0.5 | 0.20 | 1553 |
| 250-2000-4000 | mdp | 0 | 0.30 | 1570 |
| x4 | mondrian | λ per group = 0.88/0.92/0.5 | 0.10 | 1593 |
| 250-1000-4000 | mondrian | λ per group = 0.88/0.92/0.5 | 0.10 | 1593 |
| 250-1000-2000-4000 | mdp | 0 | 0.30 | 1620 |
| 250-4000 | mondrian | λ per group = 0.5/0.85/0.5 | 0.10 | 1622 |
| 250-1000-2000-4000 | giveup | 0.8, 0.15 | 0.60 | 1631 |
| x4 | mdp | 0 | 0.20 | 1636 |
| 250-1000-4000 | mdp | 0 | 0.20 | 1636 |
| 250-1000-2000-4000 | threshold | 0.8 | 0.60 | 1643 |
| 500-2000-4000 | mondrian | λ per group = 0.6/0.88/0.5 | 0.10 | 1649 |
| doubling | mdp | 0 | 0.70 | 1664 |
| 500-2000-4000 | mdp | 0 | 0.40 | 1720 |
| 250-4000 | mdp | 0 | 0.00 | 1755 |
| doubling | giveup | 0.85, 0.15 | 0.60 | 1811 |
| doubling | threshold | 0.85 | 0.60 | 1818 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.88/0.9/0.5 | 0.20 | 1909 |
| doubling | mondrian | λ per group = 0.88/0.93/0.5 | 0.10 | 2055 |
| full | threshold | 1.01 | 0.00 | 2579 |
| full | mondrian | never stop early | 0.00 | 2579 |
| 250-500-4000 | mdp | -1 | 0.00 | 2791 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | x4 / threshold | x4 / threshold | 0.96 | 76.7 | 0.63 | 1845 |
| mondrian | 250-500-4000 / mondrian | 250-500-4000 / mondrian | λ per group = 0.85/0.97/1.01 | 77.0 | 0.20 | 2573 |

### SC²-PCR, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / threshold | 84.94 | 1660 | +0.24 [+0.43] | True | 1.59× [1.53, 1.66] | 0.125 | 0.29 |
| mondrian: 250-500-4000 / mondrian | 85.04 | 2666 | +0.14 [+0.33] | True | 0.99× [0.98, 1.00] | 0.375 | 0.19 |
| fixed budget N=250 (single run) | 55.93 | 51 | | | | | |
| fixed budget N=500 (single run) | 66.44 | 140 | | | | | |
| fixed budget N=1000 (single run) | 75.67 | 379 | | | | | |
| fixed budget N=2000 (single run) | 81.88 | 964 | | | | | |
| fixed budget N=4000 (single run) | 85.18 | 2645 | | | | | |

### SC²-PCR, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / threshold | 40.42 | 2731 | +0.11 [+0.33] | True | 0.88× [0.87, 0.89] | 1 | 0.11 |
| mondrian: 250-500-4000 / mondrian | 40.31 | 2558 | +0.22 [+0.45] | True | 0.94× [0.93, 0.95] | 0.5 | 0.22 |
| fixed budget N=250 (single run) | 14.87 | 55 | | | | | |
| fixed budget N=500 (single run) | 22.69 | 150 | | | | | |
| fixed budget N=1000 (single run) | 30.62 | 383 | | | | | |
| fixed budget N=2000 (single run) | 36.34 | 936 | | | | | |
| fixed budget N=4000 (single run) | 40.53 | 2410 | | | | | |

### SC²-PCR, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / threshold | 81.02 | 1818 | +0.49 [+0.80] | True | 1.52× [1.46, 1.58] | 0.00781 | 0.49 |
| mondrian: 250-500-4000 / mondrian | 81.45 | 2783 | +0.06 [+0.18] | True | 0.99× [0.98, 1.00] | 1 | 0.06 |
| fixed budget N=250 (single run) | 50.83 | 55 | | | | | |
| fixed budget N=500 (single run) | 61.31 | 143 | | | | | |
| fixed budget N=1000 (single run) | 70.18 | 375 | | | | | |
| fixed budget N=2000 (single run) | 77.08 | 965 | | | | | |
| fixed budget N=4000 (single run) | 81.52 | 2762 | | | | | |

### SC²-PCR, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / threshold | 36.61 | 2804 | +0.00 [+0.00] | True | 0.88× [0.87, 0.89] | 1 | 0.00 |
| mondrian: 250-500-4000 / mondrian | 36.55 | 2641 | +0.06 [+0.17] | True | 0.94× [0.93, 0.94] | 1 | 0.06 |
| fixed budget N=250 (single run) | 13.31 | 60 | | | | | |
| fixed budget N=500 (single run) | 19.03 | 152 | | | | | |
| fixed budget N=1000 (single run) | 25.44 | 378 | | | | | |
| fixed budget N=2000 (single run) | 32.00 | 933 | | | | | |
| fixed budget N=4000 (single run) | 36.61 | 2470 | | | | | |

## TurboReg

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| x4 | giveup | 0.6, 0.2 | 0.70 | 1883 |
| 250-1000-4000 | giveup | 0.6, 0.2 | 0.70 | 1883 |
| x4 | threshold | 0.6 | 0.70 | 1890 |
| 250-1000-4000 | threshold | 0.6 | 0.70 | 1890 |
| 250-500-4000 | threshold | 0.6 | 0.60 | 2040 |
| 250-500-4000 | giveup | 0.6, 0 | 0.60 | 2040 |
| 250-2000-4000 | giveup | 0.6, 0.3 | 0.50 | 2063 |
| 500-2000-4000 | threshold | 0.6 | 0.70 | 2096 |
| 500-2000-4000 | giveup | 0.6, 0 | 0.70 | 2096 |
| 500-4000 | threshold | 0.6 | 0.40 | 2148 |
| 500-4000 | giveup | 0.6, 0 | 0.40 | 2148 |
| x4 | mdp | 0 | 0.60 | 2158 |
| 250-1000-4000 | mdp | 0 | 0.60 | 2158 |
| 250-2000-4000 | threshold | 0.6 | 0.30 | 2181 |
| 250-500-4000 | mondrian | λ per group = 0.75/0.75/0.5 | 0.10 | 2186 |
| 500-4000 | mondrian | λ per group = 0.5/0.7/0.5 | 0.10 | 2203 |
| 500-4000 | mdp | 0 | 0.10 | 2209 |
| x4 | mondrian | λ per group = 0.7/0.85/0.5 | 0.20 | 2210 |
| 250-1000-4000 | mondrian | λ per group = 0.7/0.85/0.5 | 0.20 | 2210 |
| 500-2000-4000 | mondrian | λ per group = 0.6/0.75/0.5 | 0.10 | 2237 |
| 250-1000-2000-4000 | mdp | 0 | 0.60 | 2240 |
| 250-1000-2000-4000 | giveup | 0.7, 0.2 | 0.60 | 2263 |
| 250-1000-2000-4000 | threshold | 0.7 | 0.60 | 2302 |
| 500-2000-4000 | mdp | 0 | 0.20 | 2307 |
| doubling | mdp | 0 | 0.50 | 2344 |
| doubling | giveup | 0.75, 0.15 | 0.70 | 2375 |
| doubling | threshold | 0.75 | 0.70 | 2385 |
| 250-2000-4000 | mdp | 0 | 0.10 | 2435 |
| 250-4000 | giveup | 0.5, 0.3 | 0.60 | 2482 |
| 250-4000 | threshold | 0.5 | 0.60 | 2489 |
| 250-2000-4000 | mondrian | λ per group = 0.6/0.85/0.5 | 0.10 | 2539 |
| 250-4000 | mondrian | λ per group = 0.5/0.7/0.5 | 0.10 | 2581 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.7/0.85/0.5 | 0.20 | 2623 |
| 250-500-4000 | mdp | 0 | 0.00 | 2636 |
| doubling | mondrian | λ per group = 0.8/0.85/0.5 | 0.10 | 2719 |
| 250-4000 | mdp | 0 | 0.10 | 2829 |
| full | threshold | 1.01 | 0.00 | 4384 |
| full | mondrian | never stop early | 0.00 | 4384 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | x4 / giveup | x4 / giveup | 0.95, 0.2 | 76.1 | 0.70 | 3249 |
| mondrian | 250-500-4000 / mondrian | 250-500-4000 / mondrian | λ per group = 0.8/0.97/0.99 | 76.3 | 0.37 | 3380 |

### TurboReg, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / giveup | 85.33 | 2504 | +0.33 [+0.57] | True | 1.77× [1.70, 1.84] | 0.0391 | 0.38 |
| mondrian: 250-500-4000 / mondrian | 85.56 | 2727 | +0.10 [+0.29] | True | 1.62× [1.57, 1.69] | 0.688 | 0.19 |
| fixed budget N=250 (single run) | 53.97 | 27 | | | | | |
| fixed budget N=500 (single run) | 66.44 | 144 | | | | | |
| fixed budget N=1000 (single run) | 75.05 | 540 | | | | | |
| fixed budget N=2000 (single run) | 81.84 | 1534 | | | | | |
| fixed budget N=4000 (single run) | 85.66 | 4431 | | | | | |

### TurboReg, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / giveup | 39.98 | 4304 | +0.22 [+0.55] | True | 0.94× [0.93, 0.95] | 0.5 | 0.22 |
| mondrian: 250-500-4000 / mondrian | 40.09 | 3985 | +0.11 [+0.33] | True | 1.01× [1.00, 1.03] | 1 | 0.11 |
| fixed budget N=250 (single run) | 16.30 | 12 | | | | | |
| fixed budget N=500 (single run) | 22.36 | 89 | | | | | |
| fixed budget N=1000 (single run) | 30.29 | 484 | | | | | |
| fixed budget N=2000 (single run) | 36.56 | 1519 | | | | | |
| fixed budget N=4000 (single run) | 40.20 | 4038 | | | | | |

### TurboReg, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / giveup | 81.27 | 2804 | +0.62 [+0.99] | True | 1.64× [1.57, 1.71] | 0.00195 | 0.62 |
| mondrian: 250-500-4000 / mondrian | 81.58 | 3057 | +0.31 [+0.62] | True | 1.50× [1.45, 1.56] | 0.125 | 0.37 |
| fixed budget N=250 (single run) | 49.04 | 26 | | | | | |
| fixed budget N=500 (single run) | 60.01 | 140 | | | | | |
| fixed budget N=1000 (single run) | 69.25 | 548 | | | | | |
| fixed budget N=2000 (single run) | 76.59 | 1582 | | | | | |
| fixed budget N=4000 (single run) | 81.89 | 4590 | | | | | |

### TurboReg, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / giveup | 36.44 | 4369 | +0.11 [+0.28] | True | 0.94× [0.93, 0.95] | 0.5 | 0.11 |
| mondrian: 250-500-4000 / mondrian | 36.50 | 4062 | +0.06 [+0.22] | True | 1.01× [1.00, 1.02] | 1 | 0.11 |
| fixed budget N=250 (single run) | 13.87 | 11 | | | | | |
| fixed budget N=500 (single run) | 19.03 | 81 | | | | | |
| fixed budget N=1000 (single run) | 25.21 | 469 | | | | | |
| fixed budget N=2000 (single run) | 31.44 | 1517 | | | | | |
| fixed budget N=4000 (single run) | 36.55 | 4100 | | | | | |
