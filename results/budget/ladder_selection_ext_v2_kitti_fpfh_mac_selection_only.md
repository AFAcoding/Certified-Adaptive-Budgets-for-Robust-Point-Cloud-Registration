# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## MAC

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1238 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-2000-4000 | giveup | 0.5, 0.2 | 0.33 | 3538 |
| 250-1000-2000-4000 | giveup | 0.5, 0.05 | 0.33 | 3599 |
| 250-1000-2000-4000 | threshold | 0.5 | 0.00 | 3813 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 3813 |
| 250-2000-4000 | giveup | 0.5, 0.15 | 0.00 | 3972 |
| doubling | threshold | 0.6 | 0.33 | 4104 |
| doubling | giveup | 0.6, 0 | 0.33 | 4104 |
| 500-2000-4000 | threshold | 0.5 | 0.33 | 4129 |
| 500-2000-4000 | mondrian | λ per group = 0.5/0.5/0.6 | 0.00 | 4160 |
| 250-2000-4000 | threshold | 0.5 | 0.00 | 4400 |
| 250-2000-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 4400 |
| 250-1000-2000-4000 | mdp | 0 | 0.00 | 4417 |
| doubling | mondrian | λ per group = 0.93/0.5/0.6 | 0.00 | 4526 |
| x4 | giveup | 0.7, 0.15 | 0.33 | 5174 |
| 250-1000-4000 | giveup | 0.7, 0.15 | 0.33 | 5174 |
| x4 | threshold | 0.5 | 0.33 | 5683 |
| 250-1000-4000 | threshold | 0.5 | 0.33 | 5683 |
| x4 | mondrian | λ per group = 0.7/0.5/0.5 | 0.00 | 5744 |
| 250-1000-4000 | mondrian | λ per group = 0.7/0.5/0.5 | 0.00 | 5744 |
| 250-500-4000 | giveup | 0.8, 0.2 | 0.33 | 6984 |
| 500-4000 | giveup | 0.5, 0.2 | 0.33 | 7151 |
| 500-4000 | threshold | 0.5 | 0.33 | 7396 |
| 500-4000 | mondrian | λ per group = 0.5/0.5/0.6 | 0.00 | 7510 |
| 250-500-4000 | threshold | 0.5 | 0.33 | 7524 |
| 250-500-4000 | mondrian | λ per group = 0.8/0.5/0.5 | 0.00 | 7565 |
| 500-4000 | mdp | 0 | 0.00 | 7711 |
| 250-4000 | giveup | 0.5, 0.2 | 0.33 | 7833 |
| full | threshold | 1.01 | 0.00 | 8188 |
| full | mondrian | never stop early | 0.00 | 8188 |
| 250-500-4000 | mdp | 0 | 0.00 | 8190 |
| 250-4000 | threshold | 0.5 | 0.00 | 8250 |
| 250-4000 | mdp | 0 | 0.00 | 8250 |
| 250-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 8250 |
| x4 | mdp | -1 | 0.00 | 8579 |
| 250-1000-4000 | mdp | -1 | 0.00 | 8579 |
| 250-2000-4000 | mdp | -1 | 0.00 | 9716 |
| 500-2000-4000 | mdp | -1 | 0.00 | 9736 |
| doubling | mdp | -1 | 0.00 | 10127 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-2000-4000 / giveup | full / threshold (fallback) | 1.01 | 79.6 | 0.00 | 8061 |
| mondrian | 250-1000-2000-4000 / mondrian | 250-1000-2000-4000 / mondrian | λ per group = 0.95/0.995/0.75 | 79.6 | 0.00 | 6621 |
