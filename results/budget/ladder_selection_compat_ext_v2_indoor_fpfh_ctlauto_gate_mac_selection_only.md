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
