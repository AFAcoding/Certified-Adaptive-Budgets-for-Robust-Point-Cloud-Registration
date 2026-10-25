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
