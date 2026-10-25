# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## MAC

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1331 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-4000 | giveup | 0.7, 0.1 | 0.50 | 3311 |
| 500-4000 | threshold | 0.7 | 0.50 | 3370 |
| 500-2000-4000 | giveup | 0.75, 0.15 | 0.60 | 3720 |
| 250-500-4000 | threshold | 0.8 | 0.60 | 3780 |
| 250-500-4000 | giveup | 0.8, 0 | 0.60 | 3780 |
| 500-2000-4000 | threshold | 0.75 | 0.40 | 3937 |
| 500-4000 | mdp | 0 | 0.40 | 4078 |
| 250-4000 | threshold | 0.8 | 0.60 | 4125 |
| 250-4000 | giveup | 0.8, 0 | 0.60 | 4125 |
| x4 | threshold | 0.85 | 0.60 | 4218 |
| x4 | giveup | 0.85, 0 | 0.60 | 4218 |
| 250-1000-4000 | threshold | 0.85 | 0.60 | 4218 |
| 250-1000-4000 | giveup | 0.85, 0 | 0.60 | 4218 |
| 250-2000-4000 | threshold | 0.8 | 0.60 | 4405 |
| 250-2000-4000 | giveup | 0.8, 0 | 0.60 | 4405 |
| 500-2000-4000 | mdp | 0 | 0.60 | 4475 |
| doubling | threshold | 0.85 | 0.60 | 4710 |
| doubling | giveup | 0.85, 0 | 0.60 | 4710 |
| 250-1000-2000-4000 | threshold | 0.88 | 0.60 | 5156 |
| 250-1000-2000-4000 | giveup | 0.88, 0 | 0.60 | 5156 |
| 500-4000 | mondrian | λ per group = 0.85/0.97/0.5 | 0.00 | 6161 |
| 500-2000-4000 | mondrian | λ per group = 0.85/0.98/0.5 | 0.00 | 8000 |
| 250-500-4000 | mondrian | λ per group = 0.92/0.995/0.5 | 0.00 | 12481 |
| x4 | mondrian | λ per group = 0.92/0.995/0.5 | 0.00 | 12935 |
| 250-1000-4000 | mondrian | λ per group = 0.92/0.995/0.5 | 0.00 | 12935 |
| 250-4000 | mondrian | λ per group = 0.92/0.995/0.5 | 0.00 | 13009 |
| doubling | mondrian | λ per group = 0.92/0.995/0.5 | 0.00 | 14997 |
| 250-2000-4000 | mondrian | λ per group = 0.92/0.995/0.5 | 0.00 | 15205 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.92/0.995/0.5 | 0.00 | 15244 |
| full | threshold | 1.01 | 0.00 | 16478 |
| full | mondrian | never stop early | 0.00 | 16478 |
| 250-4000 | mdp | -1 | 0.00 | 16610 |
| 250-500-4000 | mdp | -1 | 0.00 | 16847 |
| x4 | mdp | -1 | 0.00 | 17448 |
| 250-1000-4000 | mdp | -1 | 0.00 | 17448 |
| 250-2000-4000 | mdp | -1 | 0.00 | 20208 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 21046 |
| doubling | mdp | -1 | 0.00 | 21284 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-4000 / giveup | 500-4000 / giveup | 0.88, 0.1 | 75.3 | 0.53 | 3565 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.92/1.01/1.01 | 75.6 | 0.15 | 8155 |
