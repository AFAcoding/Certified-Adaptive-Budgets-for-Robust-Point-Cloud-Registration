# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## MAC

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| x4 | giveup | 0.75, 0.15 | 0.70 | 2768 |
| 250-1000-4000 | giveup | 0.75, 0.15 | 0.70 | 2768 |
| x4 | threshold | 0.75 | 0.70 | 2776 |
| 250-1000-4000 | threshold | 0.75 | 0.70 | 2776 |
| 500-2000-4000 | giveup | 0.7, 0.15 | 0.70 | 2897 |
| 500-2000-4000 | threshold | 0.7 | 0.70 | 2907 |
| 250-2000-4000 | giveup | 0.7, 0.2 | 0.50 | 3099 |
| 500-4000 | threshold | 0.7 | 0.50 | 3114 |
| 500-4000 | giveup | 0.7, 0 | 0.50 | 3114 |
| 250-2000-4000 | threshold | 0.7 | 0.40 | 3126 |
| 250-500-4000 | threshold | 0.75 | 0.60 | 3155 |
| 250-500-4000 | giveup | 0.75, 0 | 0.60 | 3155 |
| 500-2000-4000 | mdp | 0 | 0.30 | 3193 |
| 250-1000-2000-4000 | giveup | 0.8, 0.15 | 0.60 | 3276 |
| 250-1000-2000-4000 | threshold | 0.8 | 0.60 | 3301 |
| doubling | giveup | 0.85, 0.15 | 0.60 | 3514 |
| doubling | threshold | 0.85 | 0.60 | 3531 |
| 250-2000-4000 | mdp | 0 | 0.20 | 3688 |
| 250-4000 | giveup | 0.6, 0.3 | 0.70 | 3774 |
| x4 | mondrian | λ per group = 0.94/0.95/0.5 | 0.20 | 3792 |
| 250-1000-4000 | mondrian | λ per group = 0.94/0.95/0.5 | 0.20 | 3792 |
| 250-4000 | threshold | 0.6 | 0.60 | 3798 |
| 250-500-4000 | mondrian | λ per group = 0.92/0.93/0.5 | 0.20 | 3804 |
| 500-4000 | mondrian | λ per group = 0.5/0.92/0.5 | 0.20 | 3821 |
| 250-500-4000 | mdp | 0 | 0.30 | 3971 |
| 250-2000-4000 | mondrian | λ per group = 0.6/0.96/0.5 | 0.20 | 4047 |
| 500-2000-4000 | mondrian | λ per group = 0.6/0.96/0.5 | 0.30 | 4083 |
| 500-4000 | mdp | 0 | 0.20 | 4109 |
| 250-4000 | mondrian | λ per group = 0.5/0.92/0.5 | 0.10 | 4260 |
| 250-4000 | mdp | 0 | 0.10 | 4454 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.94/0.96/0.5 | 0.20 | 4563 |
| doubling | mondrian | λ per group = 0.96/0.95/0.5 | 0.20 | 4646 |
| full | threshold | 1.01 | 0.00 | 7489 |
| full | mondrian | never stop early | 0.00 | 7489 |
| x4 | mdp | -1 | 0.00 | 7905 |
| 250-1000-4000 | mdp | -1 | 0.00 | 7905 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 9694 |
| doubling | mdp | -1 | 0.00 | 9770 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | x4 / giveup | x4 / giveup | 0.93, 0.15 | 76.8 | 0.73 | 3803 |
| mondrian | x4 / mondrian | x4 / mondrian | λ per group = 0.85/0.96/0.99 | 77.1 | 0.33 | 4430 |
