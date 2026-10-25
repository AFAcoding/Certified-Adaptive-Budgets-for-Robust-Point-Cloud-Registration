# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## MAC

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-4000 | giveup | 0.5, 0.1 | 0.70 | 2323 |
| 500-4000 | threshold | 0.5 | 0.60 | 2328 |
| 500-2000-4000 | threshold | 0.6 | 0.60 | 2415 |
| 500-2000-4000 | giveup | 0.6, 0 | 0.60 | 2415 |
| x4 | threshold | 0.75 | 0.70 | 2550 |
| x4 | giveup | 0.75, 0 | 0.70 | 2550 |
| 250-1000-4000 | threshold | 0.75 | 0.70 | 2550 |
| 250-1000-4000 | giveup | 0.75, 0 | 0.70 | 2550 |
| x4 | mdp | 0 | 0.70 | 2606 |
| 250-1000-4000 | mdp | 0 | 0.70 | 2606 |
| 500-4000 | mondrian | λ per group = 0.5/0.75/0.5 | 0.20 | 2633 |
| 250-500-4000 | giveup | 0.75, 0.15 | 0.70 | 2654 |
| 250-500-4000 | threshold | 0.75 | 0.50 | 2667 |
| 250-4000 | threshold | 0.7 | 0.70 | 2792 |
| 250-4000 | giveup | 0.7, 0 | 0.70 | 2792 |
| 500-4000 | mdp | 0 | 0.50 | 2856 |
| 500-2000-4000 | mondrian | λ per group = 0.8/0.75/0.5 | 0.20 | 2898 |
| 250-2000-4000 | mdp | 0 | 0.50 | 2952 |
| 500-2000-4000 | mdp | 0 | 0.40 | 3030 |
| 250-4000 | mdp | 0 | 0.50 | 3093 |
| 250-2000-4000 | giveup | 0.8, 0.05 | 0.60 | 3106 |
| 250-2000-4000 | threshold | 0.8 | 0.60 | 3111 |
| doubling | giveup | 0.8, 0.1 | 0.60 | 3172 |
| doubling | threshold | 0.8 | 0.40 | 3181 |
| 250-1000-2000-4000 | giveup | 0.85, 0.1 | 0.60 | 3424 |
| 250-1000-2000-4000 | threshold | 0.85 | 0.40 | 3449 |
| 250-4000 | mondrian | λ per group = 0.5/0.95/0.5 | 0.20 | 3644 |
| 250-500-4000 | mondrian | λ per group = 0.6/0.98/0.5 | 0.20 | 3948 |
| x4 | mondrian | λ per group = 0.75/0.98/0.5 | 0.00 | 4067 |
| 250-1000-4000 | mondrian | λ per group = 0.75/0.98/0.5 | 0.00 | 4067 |
| 250-2000-4000 | mondrian | λ per group = 0.8/0.97/0.5 | 0.10 | 4455 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.85/0.98/0.5 | 0.10 | 5053 |
| doubling | mondrian | λ per group = 0.8/0.98/0.5 | 0.10 | 5061 |
| full | threshold | 1.01 | 0.00 | 7489 |
| full | mondrian | never stop early | 0.00 | 7489 |
| 250-500-4000 | mdp | -1 | 0.00 | 7723 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 10167 |
| doubling | mdp | -1 | 0.00 | 10311 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-4000 / giveup | 500-4000 / giveup | 0.8, 0.1 | 76.9 | 0.57 | 2960 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.7/0.94/0.5 | 77.2 | 0.23 | 3786 |

### MAC, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 85.18 | 2442 | +0.53 [+0.81] | True | 3.28× [3.08, 3.51] | 0.00739 | 0.62 |
| mondrian: 500-4000 / mondrian | 85.33 | 3098 | +0.38 [+0.67] | True | 2.59× [2.44, 2.75] | 0.0386 | 0.48 |
| fixed budget N=250 (single run) | 69.93 | 92 | | | | | |
| fixed budget N=500 (single run) | 74.71 | 174 | | | | | |
| fixed budget N=1000 (single run) | 78.92 | 534 | | | | | |
| fixed budget N=2000 (single run) | 82.46 | 2159 | | | | | |
| fixed budget N=4000 (single run) | 85.71 | 8017 | | | | | |

### MAC, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 43.17 | 5167 | +0.33 [+0.77] | True | 1.17× [1.13, 1.20] | 0.375 | 0.44 |
| mondrian: 500-4000 / mondrian | 43.39 | 5663 | +0.11 [+0.33] | True | 1.06× [1.04, 1.09] | 1 | 0.11 |
| fixed budget N=250 (single run) | 25.33 | 87 | | | | | |
| fixed budget N=500 (single run) | 29.63 | 172 | | | | | |
| fixed budget N=1000 (single run) | 33.37 | 507 | | | | | |
| fixed budget N=2000 (single run) | 38.22 | 1846 | | | | | |
| fixed budget N=4000 (single run) | 43.50 | 6023 | | | | | |

### MAC, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 80.90 | 2797 | +0.37 [+0.68] | True | 2.68× [2.51, 2.86] | 0.109 | 0.49 |
| mondrian: 500-4000 / mondrian | 80.71 | 3501 | +0.55 [+0.92] | True | 2.14× [2.02, 2.27] | 0.0117 | 0.62 |
| fixed budget N=250 (single run) | 66.11 | 97 | | | | | |
| fixed budget N=500 (single run) | 70.18 | 182 | | | | | |
| fixed budget N=1000 (single run) | 74.12 | 555 | | | | | |
| fixed budget N=2000 (single run) | 77.94 | 2088 | | | | | |
| fixed budget N=4000 (single run) | 81.27 | 7492 | | | | | |

### MAC, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 37.06 | 5304 | +0.22 [+0.45] | True | 1.11× [1.09, 1.14] | 0.219 | 0.28 |
| mondrian: 500-4000 / mondrian | 37.11 | 5604 | +0.17 [+0.34] | True | 1.05× [1.04, 1.07] | 0.25 | 0.17 |
| fixed budget N=250 (single run) | 22.91 | 91 | | | | | |
| fixed budget N=500 (single run) | 25.66 | 171 | | | | | |
| fixed budget N=1000 (single run) | 29.14 | 496 | | | | | |
| fixed budget N=2000 (single run) | 33.30 | 1742 | | | | | |
| fixed budget N=4000 (single run) | 37.28 | 5910 | | | | | |
