# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## MAC

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| x4 | threshold | 0.8 | 0.70 | 2987 |
| x4 | giveup | 0.8, 0 | 0.70 | 2987 |
| 250-1000-4000 | threshold | 0.8 | 0.70 | 2987 |
| 250-1000-4000 | giveup | 0.8, 0 | 0.70 | 2987 |
| 500-2000-4000 | giveup | 0.7, 0.15 | 0.70 | 3024 |
| 500-2000-4000 | threshold | 0.7 | 0.70 | 3032 |
| 500-2000-4000 | mdp | 0 | 0.40 | 3096 |
| 500-4000 | giveup | 0.7, 0.2 | 0.50 | 3131 |
| 500-4000 | threshold | 0.7 | 0.50 | 3138 |
| 250-500-4000 | threshold | 0.75 | 0.70 | 3185 |
| 250-500-4000 | giveup | 0.75, 0 | 0.70 | 3185 |
| 250-2000-4000 | giveup | 0.7, 0.2 | 0.60 | 3214 |
| 250-2000-4000 | threshold | 0.7 | 0.50 | 3240 |
| 250-2000-4000 | mdp | 0 | 0.30 | 3301 |
| 250-1000-2000-4000 | threshold | 0.8 | 0.70 | 3413 |
| 250-1000-2000-4000 | giveup | 0.8, 0 | 0.70 | 3413 |
| doubling | threshold | 0.8 | 0.70 | 3417 |
| doubling | giveup | 0.8, 0 | 0.70 | 3417 |
| 250-500-4000 | mdp | 0 | 0.50 | 3494 |
| 250-4000 | giveup | 0.6, 0.3 | 0.70 | 3696 |
| 250-4000 | threshold | 0.6 | 0.50 | 3729 |
| 500-4000 | mdp | 0 | 0.30 | 3826 |
| 500-4000 | mondrian | λ per group = 0.5/0.92/0.5 | 0.20 | 3835 |
| 250-2000-4000 | mondrian | λ per group = 0.6/0.94/0.5 | 0.20 | 3941 |
| 250-500-4000 | mondrian | λ per group = 0.93/0.96/0.5 | 0.20 | 4002 |
| x4 | mondrian | λ per group = 0.94/0.97/0.5 | 0.20 | 4003 |
| 250-1000-4000 | mondrian | λ per group = 0.94/0.97/0.5 | 0.20 | 4003 |
| 500-2000-4000 | mondrian | λ per group = 0.7/0.93/0.5 | 0.30 | 4034 |
| 250-4000 | mondrian | λ per group = 0.5/0.88/0.5 | 0.10 | 4126 |
| 250-4000 | mdp | 0 | 0.30 | 4288 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.94/0.98/0.5 | 0.20 | 4971 |
| doubling | mondrian | λ per group = 0.95/0.98/0.5 | 0.20 | 5011 |
| full | threshold | 1.01 | 0.00 | 7656 |
| full | mondrian | never stop early | 0.00 | 7656 |
| x4 | mdp | -1 | 0.00 | 8069 |
| 250-1000-4000 | mdp | -1 | 0.00 | 8069 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 9844 |
| doubling | mdp | -1 | 0.00 | 9924 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | x4 / threshold | x4 / threshold | 0.92 | 76.8 | 0.73 | 3788 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.5/0.94/0.98 | 77.2 | 0.23 | 4343 |
