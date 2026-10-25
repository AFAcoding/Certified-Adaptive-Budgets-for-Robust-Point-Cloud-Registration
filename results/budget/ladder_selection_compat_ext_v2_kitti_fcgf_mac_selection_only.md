# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## MAC

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1107 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| doubling | mdp | 30 | 0.33 | 133 |
| x4 | mdp | 30 | 0.33 | 133 |
| 250-2000-4000 | mdp | 30 | 0.33 | 133 |
| 250-500-4000 | mdp | 30 | 0.33 | 133 |
| 250-1000-2000-4000 | mdp | 30 | 0.33 | 133 |
| 250-4000 | mdp | 30 | 0.33 | 133 |
| 250-1000-4000 | mdp | 30 | 0.33 | 133 |
| 250-2000 | threshold | 0.5 | 0.33 | 133 |
| 250-2000 | mdp | 30 | 0.33 | 133 |
| 250-2000 | giveup | 0.5, 0 | 0.33 | 133 |
| 250-1000-2000 | threshold | 0.5 | 0.33 | 133 |
| 250-1000-2000 | mdp | 30 | 0.33 | 133 |
| 250-1000-2000 | giveup | 0.5, 0 | 0.33 | 133 |
| 250-500-1000-2000 | threshold | 0.5 | 0.33 | 133 |
| 250-500-1000-2000 | mdp | 30 | 0.33 | 133 |
| 250-500-1000-2000 | giveup | 0.5, 0 | 0.33 | 133 |
| doubling | threshold | 0.5 | 0.33 | 133 |
| doubling | giveup | 0.5, 0 | 0.33 | 133 |
| 250-4000 | threshold | 0.5 | 0.00 | 150 |
| 250-4000 | giveup | 0.5, 0 | 0.00 | 150 |
| 250-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 150 |
| 250-500-4000 | threshold | 0.5 | 0.00 | 151 |
| 250-500-4000 | giveup | 0.5, 0 | 0.00 | 151 |
| 250-500-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 151 |
| x4 | threshold | 0.5 | 0.00 | 151 |
| x4 | giveup | 0.5, 0 | 0.00 | 151 |
| x4 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 151 |
| 250-1000-4000 | threshold | 0.5 | 0.00 | 151 |
| 250-1000-4000 | giveup | 0.5, 0 | 0.00 | 151 |
| 250-1000-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 151 |
| 250-2000-4000 | threshold | 0.5 | 0.00 | 154 |
| 250-2000-4000 | giveup | 0.5, 0 | 0.00 | 154 |
| 250-2000-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 154 |
| 250-1000-2000-4000 | threshold | 0.5 | 0.00 | 155 |
| 250-1000-2000-4000 | giveup | 0.5, 0 | 0.00 | 155 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 155 |
| doubling | mondrian | λ per group = 0.6/0.5/0.5 | 0.00 | 156 |
| 500-2000-4000 | mdp | 30 | 0.33 | 321 |
| 500-4000 | mdp | 30 | 0.33 | 321 |
| 500-2000 | threshold | 0.5 | 0.33 | 321 |
| 500-2000 | mdp | 30 | 0.33 | 321 |
| 500-2000 | giveup | 0.5, 0 | 0.33 | 321 |
| 500-4000 | threshold | 0.5 | 0.00 | 338 |
| 500-4000 | giveup | 0.5, 0 | 0.00 | 338 |
| 500-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 338 |
| 500-2000-4000 | threshold | 0.5 | 0.00 | 343 |
| 500-2000-4000 | giveup | 0.5, 0 | 0.00 | 343 |
| 500-2000-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 343 |
| fixed-1000 | threshold | 0.5 | 0.33 | 1083 |
| fixed-1000 | giveup | 0.5, 0 | 0.33 | 1083 |
| 250-2000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 1406 |
| 500-2000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 1595 |
| 250-1000-2000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 1739 |
| 250-500-1000-2000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 1820 |
| fixed-2000 | threshold | 0.5 | 0.00 | 2733 |
| fixed-2000 | giveup | 0.5, 0 | 0.00 | 2733 |
| fixed-2000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 2733 |
| full | threshold | 1.01 | 0.00 | 10726 |
| full | mondrian | never stop early | 0.00 | 10726 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | doubling / mdp | full / threshold (fallback) | 1.01 | 82.2 | 0.00 | 16896 |
| mondrian | 250-4000 / mondrian | full / mondrian (fallback) | λ per group = 1.01/1.01/1.01 | 82.2 | 0.00 | 16896 |
