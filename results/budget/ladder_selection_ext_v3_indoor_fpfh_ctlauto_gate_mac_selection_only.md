# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## MAC

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-4000 | giveup | 0.75, 0.2 | 0.70 | 3100 |
| 500-2000-4000 | mdp | 0 | 0.30 | 3123 |
| 250-2000-4000 | giveup | 0.7, 0.1 | 0.60 | 3140 |
| 250-2000-4000 | threshold | 0.7 | 0.60 | 3146 |
| 500-4000 | threshold | 0.75 | 0.70 | 3157 |
| 250-2000-4000 | mdp | 0 | 0.30 | 3159 |
| 500-2000-4000 | giveup | 0.75, 0.1 | 0.70 | 3169 |
| 500-2000-4000 | threshold | 0.75 | 0.70 | 3180 |
| x4 | threshold | 0.88 | 0.70 | 3491 |
| x4 | giveup | 0.88, 0 | 0.70 | 3491 |
| 250-1000-4000 | threshold | 0.88 | 0.70 | 3491 |
| 250-1000-4000 | giveup | 0.88, 0 | 0.70 | 3491 |
| 250-500-4000 | giveup | 0.88, 0.15 | 0.50 | 3680 |
| 500-4000 | mondrian | λ per group = 0.5/0.9/0.5 | 0.20 | 3702 |
| 250-4000 | giveup | 0.6, 0.2 | 0.50 | 3712 |
| 250-500-4000 | threshold | 0.88 | 0.50 | 3713 |
| 250-4000 | threshold | 0.6 | 0.50 | 3730 |
| 500-4000 | mdp | 0 | 0.40 | 3776 |
| 250-1000-2000-4000 | giveup | 0.88, 0.1 | 0.70 | 3894 |
| 250-1000-2000-4000 | threshold | 0.88 | 0.70 | 3898 |
| doubling | giveup | 0.9, 0.1 | 0.70 | 3991 |
| 250-500-4000 | mondrian | λ per group = 0.9/0.92/0.5 | 0.20 | 4008 |
| doubling | threshold | 0.9 | 0.70 | 4038 |
| 250-2000-4000 | mondrian | λ per group = 0.6/0.93/0.5 | 0.20 | 4058 |
| 500-2000-4000 | mondrian | λ per group = 0.6/0.94/0.5 | 0.30 | 4078 |
| 250-500-4000 | mdp | 0 | 0.20 | 4091 |
| 250-4000 | mondrian | λ per group = 0.5/0.85/0.5 | 0.10 | 4109 |
| x4 | mondrian | λ per group = 0.92/0.96/0.5 | 0.20 | 4145 |
| 250-1000-4000 | mondrian | λ per group = 0.92/0.96/0.5 | 0.20 | 4145 |
| 250-4000 | mdp | 0 | 0.30 | 4376 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.93/0.94/0.5 | 0.20 | 4660 |
| doubling | mondrian | λ per group = 0.94/0.97/0.5 | 0.10 | 5215 |
| full | threshold | 1.01 | 0.00 | 7656 |
| full | mondrian | never stop early | 0.00 | 7656 |
| x4 | mdp | -1 | 0.00 | 8069 |
| 250-1000-4000 | mdp | -1 | 0.00 | 8069 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 9844 |
| doubling | mdp | -1 | 0.00 | 9924 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-4000 / giveup | 500-4000 / giveup | 0.99, 0.2 | 76.7 | 0.70 | 5622 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.5/0.92/0.98 | 77.3 | 0.20 | 4612 |
