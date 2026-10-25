# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## MAC

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-4000 | giveup | 0.5, 0.2 | 0.70 | 2415 |
| 500-4000 | threshold | 0.5 | 0.50 | 2477 |
| 250-2000-4000 | threshold | 0.5 | 0.70 | 2525 |
| 250-2000-4000 | giveup | 0.5, 0 | 0.70 | 2525 |
| x4 | threshold | 0.6 | 0.70 | 2551 |
| x4 | giveup | 0.6, 0 | 0.70 | 2551 |
| 250-1000-4000 | threshold | 0.6 | 0.70 | 2551 |
| 250-1000-4000 | giveup | 0.6, 0 | 0.70 | 2551 |
| 250-500-4000 | giveup | 0.6, 0.2 | 0.70 | 2585 |
| 250-500-4000 | threshold | 0.6 | 0.60 | 2617 |
| 500-2000-4000 | giveup | 0.6, 0.15 | 0.50 | 2693 |
| 250-4000 | giveup | 0.5, 0.2 | 0.70 | 2719 |
| 250-4000 | threshold | 0.5 | 0.50 | 2735 |
| 500-2000-4000 | threshold | 0.6 | 0.30 | 2748 |
| x4 | mdp | 0 | 0.10 | 2896 |
| 250-1000-4000 | mdp | 0 | 0.10 | 2896 |
| 250-500-4000 | mdp | 0 | 0.40 | 2910 |
| 500-4000 | mdp | 0 | 0.20 | 3047 |
| doubling | mdp | 0 | 0.40 | 3139 |
| 500-2000-4000 | mdp | 0 | 0.20 | 3139 |
| 250-1000-2000-4000 | giveup | 0.7, 0.15 | 0.70 | 3145 |
| 250-1000-2000-4000 | threshold | 0.7 | 0.50 | 3166 |
| 250-2000-4000 | mdp | 0 | 0.10 | 3217 |
| doubling | threshold | 0.7 | 0.60 | 3244 |
| doubling | giveup | 0.7, 0 | 0.60 | 3244 |
| 250-4000 | mondrian | λ per group = 0.5/0.88/0.5 | 0.10 | 3436 |
| x4 | mondrian | λ per group = 0.5/0.92/0.5 | 0.20 | 3446 |
| 250-1000-4000 | mondrian | λ per group = 0.5/0.92/0.5 | 0.20 | 3446 |
| 250-500-4000 | mondrian | λ per group = 0.6/0.94/0.5 | 0.10 | 3634 |
| 500-4000 | mondrian | λ per group = 0.5/0.92/0.5 | 0.10 | 3672 |
| 250-4000 | mdp | 0 | 0.10 | 3705 |
| 250-2000-4000 | mondrian | λ per group = 0.5/0.9/0.5 | 0.20 | 3706 |
| 500-2000-4000 | mondrian | λ per group = 0.6/0.93/0.5 | 0.10 | 4152 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.7/0.93/0.5 | 0.10 | 4259 |
| doubling | mondrian | λ per group = 0.7/0.97/0.5 | 0.10 | 4873 |
| full | threshold | 1.01 | 0.00 | 7656 |
| full | mondrian | never stop early | 0.00 | 7656 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 10310 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-4000 / giveup | 500-4000 / giveup | 0.75, 0.2 | 76.9 | 0.73 | 3013 |
| mondrian | 250-4000 / mondrian | 250-4000 / mondrian | λ per group = 0.5/0.96/0.92 | 77.3 | 0.27 | 4060 |

### MAC, v3_blind_hi test (1976 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 92.16 | 1972 | +0.46 [+0.71] | True | 3.62× [3.37, 3.91] | 0.0117 | 0.51 |
| mondrian: 250-4000 / mondrian | 92.51 | 2997 | +0.10 [+0.20] | True | 2.38× [2.26, 2.53] | 0.5 | 0.10 |
| fixed budget N=250 (single run) | 77.99 | 90 | | | | | |
| fixed budget N=500 (single run) | 81.68 | 176 | | | | | |
| fixed budget N=1000 (single run) | 85.73 | 571 | | | | | |
| fixed budget N=2000 (single run) | 90.44 | 2200 | | | | | |
| fixed budget N=4000 (single run) | 92.61 | 7138 | | | | | |

### MAC, v3_blind_lo test (647 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 51.78 | 5510 | +2.47 [+3.40] | False | 1.25× [1.20, 1.30] | 3.05e-05 | 2.47 |
| mondrian: 250-4000 / mondrian | 54.25 | 6528 | +0.00 [+0.00] | True | 1.05× [1.03, 1.08] | 1 | 0.00 |
| fixed budget N=250 (single run) | 26.74 | 89 | | | | | |
| fixed budget N=500 (single run) | 33.08 | 171 | | | | | |
| fixed budget N=1000 (single run) | 38.95 | 501 | | | | | |
| fixed budget N=2000 (single run) | 46.68 | 1862 | | | | | |
| fixed budget N=4000 (single run) | 54.25 | 6878 | | | | | |

### MAC, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 84.42 | 2439 | +1.29 [+1.72] | False | 3.29× [3.07, 3.52] | 4.63e-07 | 1.39 |
| mondrian: 250-4000 / mondrian | 85.61 | 3598 | +0.10 [+0.24] | True | 2.23× [2.11, 2.35] | 0.625 | 0.14 |
| fixed budget N=250 (single run) | 69.93 | 92 | | | | | |
| fixed budget N=500 (single run) | 74.71 | 174 | | | | | |
| fixed budget N=1000 (single run) | 78.92 | 534 | | | | | |
| fixed budget N=2000 (single run) | 82.46 | 2159 | | | | | |
| fixed budget N=4000 (single run) | 85.71 | 8017 | | | | | |

### MAC, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 42.84 | 5254 | +0.66 [+1.10] | True | 1.15× [1.12, 1.18] | 0.0312 | 0.66 |
| mondrian: 250-4000 / mondrian | 43.50 | 5847 | +0.00 [+0.00] | True | 1.03× [1.02, 1.05] | 1 | 0.00 |
| fixed budget N=250 (single run) | 25.33 | 87 | | | | | |
| fixed budget N=500 (single run) | 29.63 | 172 | | | | | |
| fixed budget N=1000 (single run) | 33.37 | 507 | | | | | |
| fixed budget N=2000 (single run) | 38.22 | 1846 | | | | | |
| fixed budget N=4000 (single run) | 43.50 | 6023 | | | | | |

### MAC, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 80.41 | 2985 | +0.86 [+1.23] | False | 2.51× [2.36, 2.67] | 0.000122 | 0.86 |
| mondrian: 250-4000 / mondrian | 81.08 | 3969 | +0.18 [+0.37] | True | 1.89× [1.79, 1.99] | 0.25 | 0.18 |
| fixed budget N=250 (single run) | 66.11 | 97 | | | | | |
| fixed budget N=500 (single run) | 70.18 | 182 | | | | | |
| fixed budget N=1000 (single run) | 74.12 | 555 | | | | | |
| fixed budget N=2000 (single run) | 77.94 | 2088 | | | | | |
| fixed budget N=4000 (single run) | 81.27 | 7492 | | | | | |

### MAC, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 36.61 | 5339 | +0.67 [+1.01] | True | 1.11× [1.09, 1.13] | 0.000488 | 0.67 |
| mondrian: 250-4000 / mondrian | 37.28 | 5795 | +0.00 [+0.00] | True | 1.02× [1.01, 1.03] | 1 | 0.00 |
| fixed budget N=250 (single run) | 22.91 | 91 | | | | | |
| fixed budget N=500 (single run) | 25.66 | 171 | | | | | |
| fixed budget N=1000 (single run) | 29.14 | 496 | | | | | |
| fixed budget N=2000 (single run) | 33.30 | 1742 | | | | | |
| fixed budget N=4000 (single run) | 37.28 | 5910 | | | | | |
