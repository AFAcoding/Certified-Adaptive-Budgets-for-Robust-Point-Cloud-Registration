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
