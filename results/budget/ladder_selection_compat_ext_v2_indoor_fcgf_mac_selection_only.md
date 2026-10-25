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
