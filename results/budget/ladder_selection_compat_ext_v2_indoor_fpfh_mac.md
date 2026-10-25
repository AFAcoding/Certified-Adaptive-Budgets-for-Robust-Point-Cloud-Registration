# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## MAC

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-4000 | giveup | 0.5, 0.15 | 0.70 | 2455 |
| 500-4000 | threshold | 0.5 | 0.60 | 2462 |
| 250-500-4000 | threshold | 0.6 | 0.70 | 2584 |
| 250-500-4000 | giveup | 0.6, 0 | 0.70 | 2584 |
| 500-2000-4000 | threshold | 0.6 | 0.70 | 2718 |
| 500-2000-4000 | giveup | 0.6, 0 | 0.70 | 2718 |
| 250-4000 | giveup | 0.6, 0.2 | 0.70 | 2787 |
| x4 | threshold | 0.7 | 0.60 | 2798 |
| x4 | giveup | 0.7, 0 | 0.60 | 2798 |
| 250-1000-4000 | threshold | 0.7 | 0.60 | 2798 |
| 250-1000-4000 | giveup | 0.7, 0 | 0.60 | 2798 |
| 250-4000 | threshold | 0.6 | 0.50 | 2802 |
| 250-500-4000 | mdp | 0 | 0.30 | 2944 |
| 250-2000-4000 | giveup | 0.7, 0.15 | 0.70 | 3044 |
| 250-2000-4000 | threshold | 0.7 | 0.60 | 3052 |
| x4 | mdp | 0 | 0.30 | 3063 |
| 250-1000-4000 | mdp | 0 | 0.30 | 3063 |
| 250-1000-2000-4000 | threshold | 0.7 | 0.70 | 3110 |
| 250-1000-2000-4000 | giveup | 0.7, 0 | 0.70 | 3110 |
| doubling | giveup | 0.75, 0.15 | 0.60 | 3300 |
| doubling | threshold | 0.75 | 0.50 | 3308 |
| doubling | mdp | 0 | 0.40 | 3344 |
| 500-4000 | mdp | 0 | 0.20 | 3451 |
| 250-2000-4000 | mdp | 0 | 0.20 | 3502 |
| 500-2000-4000 | mdp | 0 | 0.20 | 3579 |
| 250-1000-2000-4000 | mdp | 0 | 0.20 | 3604 |
| 250-4000 | mondrian | λ per group = 0.5/0.92/0.5 | 0.20 | 3652 |
| 500-4000 | mondrian | λ per group = 0.5/0.92/0.5 | 0.20 | 3660 |
| 250-4000 | mdp | 0 | 0.10 | 3970 |
| 250-2000-4000 | mondrian | λ per group = 0.6/0.93/0.5 | 0.20 | 4065 |
| 250-500-4000 | mondrian | λ per group = 0.5/0.99/0.5 | 0.10 | 4234 |
| 500-2000-4000 | mondrian | λ per group = 0.7/0.93/0.5 | 0.20 | 4259 |
| x4 | mondrian | λ per group = 0.6/0.99/0.5 | 0.10 | 4334 |
| 250-1000-4000 | mondrian | λ per group = 0.6/0.99/0.5 | 0.10 | 4334 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.7/0.99/0.5 | 0.10 | 5316 |
| doubling | mondrian | λ per group = 0.75/0.99/0.5 | 0.00 | 5418 |
| full | threshold | 1.01 | 0.00 | 7489 |
| full | mondrian | never stop early | 0.00 | 7489 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-4000 / giveup | 500-4000 / giveup | 0.7, 0.15 | 77.0 | 0.67 | 2862 |
| mondrian | 250-4000 / mondrian | 250-4000 / mondrian | λ per group = 0.5/0.96/0.995 | 77.3 | 0.23 | 4694 |

### MAC, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 85.09 | 2390 | +0.62 [+0.96] | True | 3.35× [3.14, 3.59] | 0.00235 | 0.72 |
| mondrian: 250-4000 / mondrian | 85.71 | 4373 | +0.00 [+0.10] | True | 1.83× [1.75, 1.92] | 1 | 0.05 |
| fixed budget N=250 (single run) | 69.93 | 92 | | | | | |
| fixed budget N=500 (single run) | 74.71 | 174 | | | | | |
| fixed budget N=1000 (single run) | 78.92 | 534 | | | | | |
| fixed budget N=2000 (single run) | 82.46 | 2159 | | | | | |
| fixed budget N=4000 (single run) | 85.71 | 8017 | | | | | |

### MAC, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 43.50 | 5193 | +0.00 [+0.00] | True | 1.16× [1.13, 1.19] | 1 | 0.00 |
| mondrian: 250-4000 / mondrian | 43.50 | 5970 | +0.00 [+0.00] | True | 1.01× [1.00, 1.02] | 1 | 0.00 |
| fixed budget N=250 (single run) | 25.33 | 87 | | | | | |
| fixed budget N=500 (single run) | 29.63 | 172 | | | | | |
| fixed budget N=1000 (single run) | 33.37 | 507 | | | | | |
| fixed budget N=2000 (single run) | 38.22 | 1846 | | | | | |
| fixed budget N=4000 (single run) | 43.50 | 6023 | | | | | |

### MAC, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 80.78 | 2801 | +0.49 [+0.80] | True | 2.68× [2.51, 2.86] | 0.00781 | 0.49 |
| mondrian: 250-4000 / mondrian | 81.08 | 4728 | +0.18 [+0.37] | True | 1.58× [1.51, 1.66] | 0.25 | 0.18 |
| fixed budget N=250 (single run) | 66.11 | 97 | | | | | |
| fixed budget N=500 (single run) | 70.18 | 182 | | | | | |
| fixed budget N=1000 (single run) | 74.12 | 555 | | | | | |
| fixed budget N=2000 (single run) | 77.94 | 2088 | | | | | |
| fixed budget N=4000 (single run) | 81.27 | 7492 | | | | | |

### MAC, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 37.28 | 5351 | +0.00 [+0.11] | True | 1.10× [1.09, 1.12] | 1 | 0.06 |
| mondrian: 250-4000 / mondrian | 37.23 | 5917 | +0.06 [+0.17] | True | 1.00× [0.99, 1.00] | 1 | 0.06 |
| fixed budget N=250 (single run) | 22.91 | 91 | | | | | |
| fixed budget N=500 (single run) | 25.66 | 171 | | | | | |
| fixed budget N=1000 (single run) | 29.14 | 496 | | | | | |
| fixed budget N=2000 (single run) | 33.30 | 1742 | | | | | |
| fixed budget N=4000 (single run) | 37.28 | 5910 | | | | | |
