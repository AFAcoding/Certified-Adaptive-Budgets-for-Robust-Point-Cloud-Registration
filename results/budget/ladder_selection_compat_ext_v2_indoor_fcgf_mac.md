# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## MAC

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1331 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-500-4000 | threshold | 0.6 | 0.60 | 2847 |
| 250-500-4000 | giveup | 0.6, 0 | 0.60 | 2847 |
| 500-4000 | giveup | 0.6, 0.15 | 0.60 | 2952 |
| 500-4000 | threshold | 0.6 | 0.50 | 3006 |
| 250-500-4000 | mdp | 0 | 0.50 | 3049 |
| 250-4000 | giveup | 0.6, 0.15 | 0.50 | 3057 |
| 250-4000 | threshold | 0.6 | 0.50 | 3084 |
| x4 | mdp | 0 | 0.60 | 3231 |
| 250-1000-4000 | mdp | 0 | 0.60 | 3231 |
| 250-2000-4000 | giveup | 0.6, 0.15 | 0.60 | 3261 |
| 500-2000-4000 | giveup | 0.6, 0.1 | 0.60 | 3263 |
| x4 | giveup | 0.7, 0.15 | 0.60 | 3275 |
| 250-1000-4000 | giveup | 0.7, 0.15 | 0.60 | 3275 |
| 500-2000-4000 | threshold | 0.6 | 0.60 | 3280 |
| 250-4000 | mdp | 0 | 0.50 | 3291 |
| 250-2000-4000 | threshold | 0.6 | 0.60 | 3330 |
| x4 | threshold | 0.7 | 0.50 | 3372 |
| 250-1000-4000 | threshold | 0.7 | 0.50 | 3372 |
| 500-4000 | mdp | 0 | 0.40 | 3381 |
| doubling | mdp | 0 | 0.60 | 3785 |
| 250-1000-2000-4000 | giveup | 0.7, 0.1 | 0.60 | 3879 |
| doubling | giveup | 0.7, 0.1 | 0.60 | 3909 |
| 250-1000-2000-4000 | threshold | 0.7 | 0.60 | 3911 |
| 250-1000-2000-4000 | mdp | 0 | 0.60 | 3913 |
| doubling | threshold | 0.7 | 0.50 | 3941 |
| 500-2000-4000 | mdp | 0 | 0.30 | 3986 |
| 250-2000-4000 | mdp | 0 | 0.50 | 4058 |
| 500-4000 | mondrian | λ per group = 0.8/0.99/0.5 | 0.00 | 7171 |
| x4 | mondrian | λ per group = 0.85/0.995/0.5 | 0.00 | 7965 |
| 250-1000-4000 | mondrian | λ per group = 0.85/0.995/0.5 | 0.00 | 7965 |
| 500-2000-4000 | mondrian | λ per group = 0.8/0.99/0.5 | 0.00 | 8732 |
| 250-2000-4000 | mondrian | λ per group = 0.8/0.99/0.5 | 0.00 | 8875 |
| 250-500-4000 | mondrian | λ per group = 0.88/0.995/0.5 | 0.00 | 9288 |
| doubling | mondrian | λ per group = 0.85/0.995/0.5 | 0.00 | 9889 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.85/0.995/0.5 | 0.00 | 10197 |
| 250-4000 | mondrian | λ per group = 0.85/0.995/0.5 | 0.00 | 11854 |
| full | threshold | 1.01 | 0.00 | 16478 |
| full | mondrian | never stop early | 0.00 | 16478 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-500-4000 / threshold | 250-500-4000 / threshold | 0.75 | 75.2 | 0.53 | 2839 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.7/1.01/1.01 | 75.7 | 0.15 | 7214 |

### MAC, fcgfown_3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / threshold | 92.11 | 1798 | +0.25 [+0.74] | True | 7.13× [6.34, 8.11] | 0.523 | 0.80 |
| mondrian: 500-4000 / mondrian | 92.36 | 11714 | +0.00 [+0.31] | True | 1.09× [1.08, 1.11] | 1 | 0.25 |
| fixed budget N=250 (single run) | 87.31 | 107 | | | | | |
| fixed budget N=500 (single run) | 88.60 | 186 | | | | | |
| fixed budget N=1000 (single run) | 89.83 | 561 | | | | | |
| fixed budget N=2000 (single run) | 91.07 | 2664 | | | | | |
| fixed budget N=4000 (single run) | 92.36 | 12819 | | | | | |

### MAC, fcgfown_3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / threshold | 58.90 | 7140 | +0.51 [+0.84] | True | 1.53× [1.47, 1.59] | 0.0352 | 0.67 |
| mondrian: 500-4000 / mondrian | 59.18 | 9257 | +0.22 [+0.51] | True | 1.18× [1.15, 1.21] | 0.289 | 0.34 |
| fixed budget N=250 (single run) | 44.47 | 120 | | | | | |
| fixed budget N=500 (single run) | 47.45 | 252 | | | | | |
| fixed budget N=1000 (single run) | 51.54 | 852 | | | | | |
| fixed budget N=2000 (single run) | 56.09 | 3170 | | | | | |
| fixed budget N=4000 (single run) | 59.40 | 10920 | | | | | |
