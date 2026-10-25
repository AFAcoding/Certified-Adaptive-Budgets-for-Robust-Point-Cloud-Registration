# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## MAC

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-2000-4000 | threshold | 0.6 | 0.70 | 2754 |
| 250-2000-4000 | giveup | 0.6, 0 | 0.70 | 2754 |
| x4 | giveup | 0.8, 0.15 | 0.70 | 2965 |
| 250-1000-4000 | giveup | 0.8, 0.15 | 0.70 | 2965 |
| x4 | threshold | 0.8 | 0.70 | 2982 |
| 250-1000-4000 | threshold | 0.8 | 0.70 | 2982 |
| 250-500-4000 | giveup | 0.75, 0.15 | 0.70 | 3135 |
| 500-4000 | giveup | 0.75, 0.2 | 0.60 | 3138 |
| 250-500-4000 | threshold | 0.75 | 0.70 | 3144 |
| 500-4000 | threshold | 0.75 | 0.60 | 3173 |
| 500-2000-4000 | giveup | 0.8, 0.15 | 0.70 | 3217 |
| 500-2000-4000 | mdp | 0 | 0.40 | 3309 |
| 500-2000-4000 | threshold | 0.8 | 0.50 | 3334 |
| 250-2000-4000 | mdp | 0 | 0.30 | 3400 |
| 250-1000-2000-4000 | giveup | 0.85, 0.1 | 0.60 | 3525 |
| doubling | giveup | 0.85, 0.1 | 0.60 | 3547 |
| 250-1000-2000-4000 | threshold | 0.85 | 0.60 | 3568 |
| doubling | threshold | 0.85 | 0.60 | 3574 |
| 500-4000 | mondrian | λ per group = 0.5/0.9/0.5 | 0.20 | 3671 |
| 250-4000 | giveup | 0.6, 0.2 | 0.60 | 3771 |
| 250-4000 | threshold | 0.6 | 0.60 | 3779 |
| 250-500-4000 | mondrian | λ per group = 0.9/0.92/0.5 | 0.20 | 3912 |
| 250-500-4000 | mdp | 0 | 0.20 | 4032 |
| x4 | mondrian | λ per group = 0.93/0.94/0.5 | 0.20 | 4048 |
| 250-1000-4000 | mondrian | λ per group = 0.93/0.94/0.5 | 0.20 | 4048 |
| 250-4000 | mdp | 0 | 0.40 | 4107 |
| 250-2000-4000 | mondrian | λ per group = 0.6/0.94/0.5 | 0.20 | 4124 |
| 500-4000 | mdp | 0 | 0.30 | 4201 |
| 500-2000-4000 | mondrian | λ per group = 0.6/0.96/0.5 | 0.20 | 4245 |
| 250-4000 | mondrian | λ per group = 0.5/0.9/0.5 | 0.10 | 4263 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.94/0.95/0.5 | 0.20 | 4778 |
| doubling | mondrian | λ per group = 0.95/0.95/0.5 | 0.20 | 4841 |
| full | threshold | 1.01 | 0.00 | 7489 |
| full | mondrian | never stop early | 0.00 | 7489 |
| x4 | mdp | -1 | 0.00 | 7905 |
| 250-1000-4000 | mdp | -1 | 0.00 | 7905 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 9694 |
| doubling | mdp | -1 | 0.00 | 9773 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-2000-4000 / threshold | 250-2000-4000 / threshold | 0.9 | 77.0 | 0.57 | 4391 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.5/0.93/0.98 | 77.3 | 0.20 | 4600 |
