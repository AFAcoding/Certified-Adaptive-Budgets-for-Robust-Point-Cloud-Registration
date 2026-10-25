# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## MAC

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-2000-4000 | giveup | 0.6, 0.02 | 0.70 | 2490 |
| 500-2000-4000 | threshold | 0.6 | 0.60 | 2496 |
| 500-4000 | threshold | 0.6 | 0.70 | 2506 |
| 500-4000 | giveup | 0.6, 0 | 0.70 | 2506 |
| x4 | threshold | 0.7 | 0.60 | 2522 |
| x4 | giveup | 0.7, 0 | 0.60 | 2522 |
| 250-1000-4000 | threshold | 0.7 | 0.60 | 2522 |
| 250-1000-4000 | giveup | 0.7, 0 | 0.60 | 2522 |
| 250-500-4000 | threshold | 0.7 | 0.60 | 2646 |
| 250-500-4000 | giveup | 0.7, 0 | 0.60 | 2646 |
| 500-2000-4000 | mondrian | λ per group = 0.7/0.7/0.5 | 0.20 | 2692 |
| x4 | mdp | 0 | 0.50 | 2694 |
| 250-1000-4000 | mdp | 0 | 0.50 | 2694 |
| 500-4000 | mondrian | λ per group = 0.7/0.7/0.5 | 0.20 | 2712 |
| 250-2000-4000 | giveup | 0.7, 0.05 | 0.40 | 2730 |
| doubling | giveup | 0.7, 0.05 | 0.70 | 2758 |
| 250-2000-4000 | threshold | 0.7 | 0.40 | 2769 |
| doubling | threshold | 0.7 | 0.70 | 2771 |
| x4 | mondrian | λ per group = 0.7/0.8/0.5 | 0.20 | 2811 |
| 250-1000-4000 | mondrian | λ per group = 0.7/0.8/0.5 | 0.20 | 2811 |
| 250-500-4000 | mdp | 0 | 0.40 | 2831 |
| 250-2000-4000 | mdp | 0 | 0.10 | 2856 |
| 250-4000 | giveup | 0.7, 0.1 | 0.60 | 2859 |
| doubling | mdp | 0 | 0.50 | 2864 |
| 250-4000 | threshold | 0.7 | 0.30 | 2883 |
| 250-1000-2000-4000 | mdp | 0 | 0.60 | 2918 |
| 250-500-4000 | mondrian | λ per group = 0.6/0.85/0.5 | 0.20 | 2931 |
| 250-1000-2000-4000 | giveup | 0.75, 0.05 | 0.50 | 2962 |
| 250-1000-2000-4000 | threshold | 0.75 | 0.40 | 2981 |
| 500-2000-4000 | mdp | 0 | 0.10 | 3000 |
| 500-4000 | mdp | 0 | 0.10 | 3044 |
| 250-4000 | mdp | 0 | 0.20 | 3084 |
| 250-4000 | mondrian | λ per group = 0.7/0.85/0.5 | 0.10 | 3133 |
| 250-2000-4000 | mondrian | λ per group = 0.7/0.85/0.5 | 0.10 | 3171 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.7/0.88/0.5 | 0.20 | 3307 |
| doubling | mondrian | λ per group = 0.8/0.88/0.5 | 0.10 | 3541 |
| full | threshold | 1.01 | 0.00 | 7656 |
| full | mondrian | never stop early | 0.00 | 7656 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-2000-4000 / giveup | 500-2000-4000 / giveup | 0.8, 0.02 | 76.8 | 0.73 | 3177 |
| mondrian | 500-2000-4000 / mondrian | 500-2000-4000 / mondrian | λ per group = 0.85/0.94/0.5 | 77.2 | 0.30 | 4330 |

### MAC, v3_blind_hi test (1976 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-2000-4000 / giveup | 92.31 | 1898 | +0.30 [+0.56] | True | 3.76× [3.50, 4.07] | 0.109 | 0.40 |
| mondrian: 500-2000-4000 / mondrian | 92.51 | 2680 | +0.10 [+0.25] | True | 2.66× [2.51, 2.84] | 0.5 | 0.10 |
| fixed budget N=250 (single run) | 77.99 | 90 | | | | | |
| fixed budget N=500 (single run) | 81.68 | 176 | | | | | |
| fixed budget N=1000 (single run) | 85.73 | 571 | | | | | |
| fixed budget N=2000 (single run) | 90.44 | 2200 | | | | | |
| fixed budget N=4000 (single run) | 92.61 | 7138 | | | | | |

### MAC, v3_blind_lo test (647 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-2000-4000 / giveup | 53.94 | 5876 | +0.31 [+0.63] | True | 1.17× [1.12, 1.22] | 0.5 | 0.31 |
| mondrian: 500-2000-4000 / mondrian | 54.25 | 6471 | +0.00 [+0.00] | True | 1.06× [1.04, 1.09] | 1 | 0.00 |
| fixed budget N=250 (single run) | 26.74 | 89 | | | | | |
| fixed budget N=500 (single run) | 33.08 | 171 | | | | | |
| fixed budget N=1000 (single run) | 38.95 | 501 | | | | | |
| fixed budget N=2000 (single run) | 46.68 | 1862 | | | | | |
| fixed budget N=4000 (single run) | 54.25 | 6878 | | | | | |

### MAC, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-2000-4000 / giveup | 84.99 | 2469 | +0.72 [+1.05] | False | 3.25× [3.03, 3.49] | 0.000729 | 0.81 |
| mondrian: 500-2000-4000 / mondrian | 85.52 | 3311 | +0.19 [+0.33] | True | 2.42× [2.28, 2.57] | 0.125 | 0.19 |
| fixed budget N=250 (single run) | 69.93 | 92 | | | | | |
| fixed budget N=500 (single run) | 74.71 | 174 | | | | | |
| fixed budget N=1000 (single run) | 78.92 | 534 | | | | | |
| fixed budget N=2000 (single run) | 82.46 | 2159 | | | | | |
| fixed budget N=4000 (single run) | 85.71 | 8017 | | | | | |

### MAC, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-2000-4000 / giveup | 43.06 | 5489 | +0.44 [+0.88] | True | 1.10× [1.06, 1.14] | 0.125 | 0.44 |
| mondrian: 500-2000-4000 / mondrian | 43.50 | 5834 | +0.00 [+0.00] | True | 1.03× [1.01, 1.06] | 1 | 0.00 |
| fixed budget N=250 (single run) | 25.33 | 87 | | | | | |
| fixed budget N=500 (single run) | 29.63 | 172 | | | | | |
| fixed budget N=1000 (single run) | 33.37 | 507 | | | | | |
| fixed budget N=2000 (single run) | 38.22 | 1846 | | | | | |
| fixed budget N=4000 (single run) | 43.50 | 6023 | | | | | |

### MAC, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-2000-4000 / giveup | 80.47 | 2865 | +0.80 [+1.23] | False | 2.62× [2.44, 2.80] | 0.000977 | 0.86 |
| mondrian: 500-2000-4000 / mondrian | 80.96 | 3635 | +0.31 [+0.55] | True | 2.06× [1.95, 2.18] | 0.0625 | 0.31 |
| fixed budget N=250 (single run) | 66.11 | 97 | | | | | |
| fixed budget N=500 (single run) | 70.18 | 182 | | | | | |
| fixed budget N=1000 (single run) | 74.12 | 555 | | | | | |
| fixed budget N=2000 (single run) | 77.94 | 2088 | | | | | |
| fixed budget N=4000 (single run) | 81.27 | 7492 | | | | | |

### MAC, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-2000-4000 / giveup | 37.17 | 5677 | +0.11 [+0.28] | True | 1.04× [1.02, 1.07] | 0.625 | 0.17 |
| mondrian: 500-2000-4000 / mondrian | 37.28 | 5741 | +0.00 [+0.00] | True | 1.03× [1.01, 1.04] | 1 | 0.00 |
| fixed budget N=250 (single run) | 22.91 | 91 | | | | | |
| fixed budget N=500 (single run) | 25.66 | 171 | | | | | |
| fixed budget N=1000 (single run) | 29.14 | 496 | | | | | |
| fixed budget N=2000 (single run) | 33.30 | 1742 | | | | | |
| fixed budget N=4000 (single run) | 37.28 | 5910 | | | | | |
