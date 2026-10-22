# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## SC²-PCR

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| x4 | giveup | 0.75, 0.15 | 0.70 | 1310 |
| 250-1000-4000 | giveup | 0.75, 0.15 | 0.70 | 1310 |
| x4 | threshold | 0.75 | 0.60 | 1322 |
| 250-1000-4000 | threshold | 0.75 | 0.60 | 1322 |
| 500-4000 | giveup | 0.7, 0.2 | 0.70 | 1337 |
| 250-500-4000 | giveup | 0.7, 0.1 | 0.70 | 1341 |
| 250-500-4000 | threshold | 0.7 | 0.70 | 1344 |
| 500-4000 | threshold | 0.7 | 0.50 | 1360 |
| x4 | mdp | 0 | 0.70 | 1376 |
| 250-1000-4000 | mdp | 0 | 0.70 | 1376 |
| 500-4000 | mondrian | λ per group = 0.5/0.8/0.5 | 0.10 | 1420 |
| 250-2000-4000 | giveup | 0.7, 0.15 | 0.50 | 1442 |
| 500-4000 | mdp | 0 | 0.20 | 1444 |
| 250-2000-4000 | threshold | 0.7 | 0.50 | 1455 |
| 250-500-4000 | mondrian | λ per group = 0.75/0.85/0.5 | 0.20 | 1469 |
| 250-2000-4000 | mdp | 0 | 0.20 | 1489 |
| 250-4000 | giveup | 0.6, 0.2 | 0.70 | 1500 |
| 250-1000-2000-4000 | mdp | 0 | 0.60 | 1503 |
| x4 | mondrian | λ per group = 0.85/0.85/0.5 | 0.20 | 1505 |
| 250-1000-4000 | mondrian | λ per group = 0.85/0.85/0.5 | 0.20 | 1505 |
| 250-4000 | threshold | 0.6 | 0.60 | 1507 |
| 500-2000-4000 | giveup | 0.75, 0.1 | 0.70 | 1531 |
| 500-2000-4000 | threshold | 0.75 | 0.70 | 1540 |
| 500-2000-4000 | mdp | 0 | 0.40 | 1594 |
| 250-2000-4000 | mondrian | λ per group = 0.5/0.9/0.5 | 0.20 | 1600 |
| 250-1000-2000-4000 | giveup | 0.8, 0.1 | 0.70 | 1629 |
| 250-4000 | mondrian | λ per group = 0.5/0.85/0.5 | 0.10 | 1635 |
| 250-1000-2000-4000 | threshold | 0.8 | 0.70 | 1650 |
| 250-4000 | mdp | 0 | 0.20 | 1653 |
| doubling | giveup | 0.8, 0.1 | 0.60 | 1683 |
| doubling | threshold | 0.8 | 0.60 | 1691 |
| 500-2000-4000 | mondrian | λ per group = 0.6/0.92/0.5 | 0.20 | 1706 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.85/0.85/0.5 | 0.20 | 1795 |
| doubling | mondrian | λ per group = 0.88/0.85/0.5 | 0.10 | 1870 |
| full | threshold | 1.01 | 0.00 | 2579 |
| full | mondrian | never stop early | 0.00 | 2579 |
| 250-500-4000 | mdp | -1 | 0.00 | 2791 |
| doubling | mdp | -1 | 0.00 | 4128 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | x4 / giveup | x4 / giveup | 0.97, 0.15 | 76.6 | 0.63 | 2083 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.5/0.93/0.96 | 77.1 | 0.20 | 1709 |

### SC²-PCR, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / giveup | 84.89 | 1810 | +0.29 [+0.53] | True | 1.46× [1.42, 1.51] | 0.0703 | 0.33 |
| mondrian: 500-4000 / mondrian | 85.04 | 1578 | +0.14 [+0.33] | True | 1.68× [1.62, 1.74] | 0.375 | 0.19 |
| fixed budget N=250 (single run) | 55.93 | 51 | | | | | |
| fixed budget N=500 (single run) | 66.44 | 140 | | | | | |
| fixed budget N=1000 (single run) | 75.67 | 379 | | | | | |
| fixed budget N=2000 (single run) | 81.88 | 964 | | | | | |
| fixed budget N=4000 (single run) | 85.18 | 2645 | | | | | |

### SC²-PCR, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / giveup | 40.42 | 2385 | +0.11 [+0.33] | True | 1.01× [1.00, 1.02] | 1 | 0.11 |
| mondrian: 500-4000 / mondrian | 40.53 | 2365 | +0.00 [+0.00] | True | 1.02× [1.01, 1.03] | 1 | 0.00 |
| fixed budget N=250 (single run) | 14.87 | 55 | | | | | |
| fixed budget N=500 (single run) | 22.69 | 150 | | | | | |
| fixed budget N=1000 (single run) | 30.62 | 383 | | | | | |
| fixed budget N=2000 (single run) | 36.34 | 936 | | | | | |
| fixed budget N=4000 (single run) | 40.53 | 2410 | | | | | |

### SC²-PCR, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / giveup | 81.08 | 1951 | +0.43 [+0.74] | True | 1.42× [1.37, 1.46] | 0.0156 | 0.43 |
| mondrian: 500-4000 / mondrian | 81.27 | 1735 | +0.25 [+0.49] | True | 1.59× [1.53, 1.65] | 0.125 | 0.25 |
| fixed budget N=250 (single run) | 50.83 | 55 | | | | | |
| fixed budget N=500 (single run) | 61.31 | 143 | | | | | |
| fixed budget N=1000 (single run) | 70.18 | 375 | | | | | |
| fixed budget N=2000 (single run) | 77.08 | 965 | | | | | |
| fixed budget N=4000 (single run) | 81.52 | 2762 | | | | | |

### SC²-PCR, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / giveup | 36.50 | 2438 | +0.11 [+0.22] | True | 1.01× [1.01, 1.02] | 0.5 | 0.11 |
| mondrian: 500-4000 / mondrian | 36.50 | 2419 | +0.11 [+0.22] | True | 1.02× [1.01, 1.03] | 0.5 | 0.11 |
| fixed budget N=250 (single run) | 13.31 | 60 | | | | | |
| fixed budget N=500 (single run) | 19.03 | 152 | | | | | |
| fixed budget N=1000 (single run) | 25.44 | 378 | | | | | |
| fixed budget N=2000 (single run) | 32.00 | 933 | | | | | |
| fixed budget N=4000 (single run) | 36.61 | 2470 | | | | | |

## TurboReg

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-2000-4000 | giveup | 0.6, 0.2 | 0.60 | 1985 |
| x4 | giveup | 0.7, 0.15 | 0.70 | 1987 |
| 250-1000-4000 | giveup | 0.7, 0.15 | 0.70 | 1987 |
| x4 | threshold | 0.7 | 0.60 | 2005 |
| 250-1000-4000 | threshold | 0.7 | 0.60 | 2005 |
| 250-500-4000 | giveup | 0.6, 0.15 | 0.70 | 2024 |
| 250-500-4000 | threshold | 0.6 | 0.70 | 2031 |
| 500-4000 | giveup | 0.6, 0.2 | 0.50 | 2072 |
| 500-4000 | threshold | 0.6 | 0.50 | 2093 |
| 250-2000-4000 | threshold | 0.6 | 0.50 | 2097 |
| 500-2000-4000 | giveup | 0.7, 0.2 | 0.70 | 2111 |
| x4 | mdp | 0 | 0.50 | 2171 |
| 250-1000-4000 | mdp | 0 | 0.50 | 2171 |
| x4 | mondrian | λ per group = 0.7/0.8/0.5 | 0.20 | 2181 |
| 250-1000-4000 | mondrian | λ per group = 0.7/0.8/0.5 | 0.20 | 2181 |
| 500-4000 | mdp | 0 | 0.10 | 2215 |
| 250-500-4000 | mondrian | λ per group = 0.7/0.8/0.5 | 0.10 | 2220 |
| 500-2000-4000 | threshold | 0.7 | 0.40 | 2260 |
| 500-4000 | mondrian | λ per group = 0.5/0.8/0.5 | 0.00 | 2293 |
| 250-500-4000 | mdp | 0 | 0.40 | 2297 |
| 250-2000-4000 | mdp | 0 | 0.10 | 2327 |
| 500-2000-4000 | mdp | 0 | 0.30 | 2342 |
| doubling | giveup | 0.75, 0.1 | 0.60 | 2365 |
| doubling | threshold | 0.75 | 0.60 | 2373 |
| 250-1000-2000-4000 | giveup | 0.75, 0.15 | 0.70 | 2384 |
| 250-2000-4000 | mondrian | λ per group = 0.6/0.8/0.5 | 0.20 | 2386 |
| 250-1000-2000-4000 | mdp | 0 | 0.60 | 2430 |
| 250-1000-2000-4000 | threshold | 0.75 | 0.40 | 2431 |
| 500-2000-4000 | mondrian | λ per group = 0.6/0.85/0.5 | 0.10 | 2433 |
| 250-4000 | giveup | 0.6, 0.3 | 0.40 | 2499 |
| 250-4000 | threshold | 0.6 | 0.30 | 2529 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.75/0.8/0.5 | 0.20 | 2555 |
| 250-4000 | mondrian | λ per group = 0.5/0.7/0.5 | 0.10 | 2579 |
| 250-4000 | mdp | 0 | 0.30 | 2644 |
| doubling | mondrian | λ per group = 0.85/0.85/0.5 | 0.20 | 2842 |
| full | threshold | 1.01 | 0.00 | 4384 |
| full | mondrian | never stop early | 0.00 | 4384 |
| doubling | mdp | -1 | 0.00 | 6600 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-2000-4000 / giveup | 250-2000-4000 / giveup | 1.01, 0.2 | 76.0 | 0.73 | 6319 |
| mondrian | x4 / mondrian | x4 / mondrian | λ per group = 0.88/0.94/0.98 | 76.4 | 0.37 | 3579 |

### TurboReg, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-2000-4000 / giveup | 85.56 | 4445 | +0.10 [+0.24] | True | 1.00× [1.00, 1.00] | 0.5 | 0.10 |
| mondrian: x4 / mondrian | 85.66 | 2854 | +0.00 [+0.10] | True | 1.55× [1.50, 1.61] | 1 | 0.05 |
| fixed budget N=250 (single run) | 53.97 | 27 | | | | | |
| fixed budget N=500 (single run) | 66.44 | 144 | | | | | |
| fixed budget N=1000 (single run) | 75.05 | 540 | | | | | |
| fixed budget N=2000 (single run) | 81.84 | 1534 | | | | | |
| fixed budget N=4000 (single run) | 85.66 | 4431 | | | | | |

### TurboReg, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-2000-4000 / giveup | 40.20 | 4056 | +0.00 [+0.00] | True | 1.00× [0.99, 1.00] | 1 | 0.00 |
| mondrian: x4 / mondrian | 40.20 | 4032 | +0.00 [+0.00] | True | 1.00× [0.99, 1.01] | 1 | 0.00 |
| fixed budget N=250 (single run) | 16.30 | 12 | | | | | |
| fixed budget N=500 (single run) | 22.36 | 89 | | | | | |
| fixed budget N=1000 (single run) | 30.29 | 484 | | | | | |
| fixed budget N=2000 (single run) | 36.56 | 1519 | | | | | |
| fixed budget N=4000 (single run) | 40.20 | 4038 | | | | | |

### TurboReg, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-2000-4000 / giveup | 81.89 | 4608 | +0.00 [+0.00] | True | 1.00× [0.99, 1.00] | 1 | 0.00 |
| mondrian: x4 / mondrian | 81.64 | 3095 | +0.25 [+0.49] | True | 1.48× [1.43, 1.54] | 0.125 | 0.25 |
| fixed budget N=250 (single run) | 49.04 | 26 | | | | | |
| fixed budget N=500 (single run) | 60.01 | 140 | | | | | |
| fixed budget N=1000 (single run) | 69.25 | 548 | | | | | |
| fixed budget N=2000 (single run) | 76.59 | 1582 | | | | | |
| fixed budget N=4000 (single run) | 81.89 | 4590 | | | | | |

### TurboReg, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-2000-4000 / giveup | 36.50 | 4117 | +0.06 [+0.17] | True | 1.00× [0.99, 1.00] | 1 | 0.06 |
| mondrian: x4 / mondrian | 36.50 | 4078 | +0.06 [+0.17] | True | 1.01× [1.00, 1.01] | 1 | 0.06 |
| fixed budget N=250 (single run) | 13.87 | 11 | | | | | |
| fixed budget N=500 (single run) | 19.03 | 81 | | | | | |
| fixed budget N=1000 (single run) | 25.21 | 469 | | | | | |
| fixed budget N=2000 (single run) | 31.44 | 1517 | | | | | |
| fixed budget N=4000 (single run) | 36.55 | 4100 | | | | | |
