# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## MAC

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1238 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-2000-4000 | giveup | 0.5, 0.05 | 0.33 | 4632 |
| 250-2000-4000 | giveup | 0.5, 0.05 | 0.33 | 4797 |
| 500-2000-4000 | threshold | 0.5 | 0.00 | 4842 |
| 500-2000-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 4842 |
| 250-2000-4000 | threshold | 0.5 | 0.00 | 4949 |
| 250-2000-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 4949 |
| doubling | giveup | 0.6, 0.02 | 0.33 | 4958 |
| 250-1000-2000-4000 | giveup | 0.6, 0.02 | 0.33 | 5059 |
| doubling | threshold | 0.6 | 0.33 | 5106 |
| doubling | mondrian | λ per group = 0.5/0.6/0.7 | 0.00 | 5193 |
| 250-1000-2000-4000 | threshold | 0.6 | 0.33 | 5213 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.7/0.5/0.6 | 0.00 | 5232 |
| 250-2000-4000 | mdp | 0 | 0.33 | 5845 |
| x4 | giveup | 0.5, 0.02 | 0.33 | 6244 |
| 250-1000-4000 | giveup | 0.5, 0.02 | 0.33 | 6244 |
| x4 | threshold | 0.5 | 0.33 | 6355 |
| 250-1000-4000 | threshold | 0.5 | 0.33 | 6355 |
| x4 | mdp | 0 | 0.33 | 6406 |
| 250-1000-4000 | mdp | 0 | 0.33 | 6406 |
| x4 | mondrian | λ per group = 0.75/0.5/0.5 | 0.00 | 6640 |
| 250-1000-4000 | mondrian | λ per group = 0.75/0.5/0.5 | 0.00 | 6640 |
| 250-500-4000 | threshold | 0.5 | 0.33 | 6998 |
| 250-500-4000 | giveup | 0.5, 0 | 0.33 | 6998 |
| 500-4000 | giveup | 0.5, 0.02 | 0.33 | 6998 |
| 500-4000 | threshold | 0.5 | 0.33 | 7058 |
| 250-500-4000 | mdp | 0 | 0.33 | 7073 |
| 250-500-4000 | mondrian | λ per group = 0.6/0.5/0.5 | 0.00 | 7076 |
| 500-4000 | mondrian | λ per group = 0.8/0.5/0.5 | 0.00 | 7128 |
| 250-4000 | giveup | 0.5, 0.05 | 0.33 | 7463 |
| 250-4000 | threshold | 0.5 | 0.00 | 7548 |
| 250-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 7548 |
| 250-4000 | mdp | 0 | 0.33 | 7772 |
| full | threshold | 1.01 | 0.00 | 8188 |
| full | mondrian | never stop early | 0.00 | 8188 |
| 500-4000 | mdp | -1 | 0.00 | 8379 |
| 500-2000-4000 | mdp | -1 | 0.00 | 10121 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 10487 |
| doubling | mdp | -1 | 0.00 | 10633 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-2000-4000 / giveup | 500-2000-4000 / giveup | 0.6, 0.05 | 79.2 | 0.57 | 5477 |
| mondrian | 500-2000-4000 / mondrian | 500-2000-4000 / mondrian | λ per group = 0.8/0.7/0.6 | 79.6 | 0.00 | 6127 |
