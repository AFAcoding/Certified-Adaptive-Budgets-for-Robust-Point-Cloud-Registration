# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## MAC

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1107 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-1000-2000 | threshold | 0.5 | 0.33 | 154 |
| 250-1000-2000 | giveup | 0.5, 0 | 0.33 | 154 |
| 250-2000 | threshold | 0.5 | 0.33 | 163 |
| 250-2000 | giveup | 0.5, 0 | 0.33 | 163 |
| doubling | threshold | 0.5 | 0.33 | 171 |
| doubling | giveup | 0.5, 0 | 0.33 | 171 |
| 250-1000-2000-4000 | threshold | 0.5 | 0.00 | 172 |
| 250-1000-2000-4000 | giveup | 0.5, 0 | 0.00 | 172 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 172 |
| 250-2000-4000 | threshold | 0.5 | 0.00 | 180 |
| 250-2000-4000 | giveup | 0.5, 0 | 0.00 | 180 |
| 250-2000-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 180 |
| 250-500-4000 | threshold | 0.5 | 0.33 | 186 |
| 250-500-4000 | giveup | 0.5, 0 | 0.33 | 186 |
| x4 | threshold | 0.5 | 0.00 | 189 |
| x4 | giveup | 0.5, 0 | 0.00 | 189 |
| x4 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 189 |
| 250-1000-4000 | threshold | 0.5 | 0.00 | 189 |
| 250-1000-4000 | giveup | 0.5, 0 | 0.00 | 189 |
| 250-1000-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 189 |
| 250-500-1000-2000 | threshold | 0.99 | 0.33 | 201 |
| 250-500-1000-2000 | giveup | 0.99, 0 | 0.33 | 201 |
| 250-4000 | threshold | 0.5 | 0.00 | 254 |
| 250-4000 | giveup | 0.5, 0 | 0.00 | 254 |
| 250-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 254 |
| 500-2000-4000 | giveup | 0.5, 0.02 | 0.33 | 292 |
| 500-4000 | giveup | 0.5, 0.02 | 0.33 | 309 |
| 500-2000 | threshold | 0.97 | 0.33 | 321 |
| 500-2000 | giveup | 0.97, 0 | 0.33 | 321 |
| 500-2000-4000 | threshold | 0.5 | 0.33 | 345 |
| 500-4000 | threshold | 0.5 | 0.33 | 354 |
| 250-500-1000-2000 | mdp | 0 | 0.33 | 549 |
| 250-2000 | mdp | 0 | 0.33 | 557 |
| 500-4000 | mondrian | λ per group = 0.98/0.5/0.5 | 0.00 | 566 |
| 250-500-4000 | mondrian | λ per group = 0.995/0.5/0.5 | 0.00 | 606 |
| 500-2000-4000 | mondrian | λ per group = 0.99/0.5/0.5 | 0.00 | 632 |
| 250-1000-2000 | mdp | 0 | 0.33 | 647 |
| doubling | mdp | 0 | 0.33 | 686 |
| 250-1000-2000-4000 | mdp | 0 | 0.33 | 781 |
| 500-2000 | mdp | 0 | 0.33 | 847 |
| 250-2000-4000 | mdp | 0 | 0.33 | 1242 |
| 250-500-4000 | mdp | 0 | 0.00 | 1379 |
| 250-4000 | mdp | 0 | 0.00 | 1691 |
| 500-2000-4000 | mdp | 0 | 0.33 | 1733 |
| fixed-2000 | threshold | 0.5 | 0.33 | 2703 |
| fixed-2000 | giveup | 0.5, 0 | 0.33 | 2703 |
| 500-4000 | mdp | 0 | 0.00 | 3048 |
| doubling | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 6360 |
| full | threshold | 1.01 | 0.00 | 10726 |
| full | mondrian | never stop early | 0.00 | 10726 |
| x4 | mdp | -1 | 0.00 | 11912 |
| 250-1000-4000 | mdp | -1 | 0.00 | 11912 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-1000-2000 / threshold | full / threshold (fallback) | 1.01 | 82.2 | 0.00 | 16896 |
| mondrian | 250-1000-2000-4000 / mondrian | full / mondrian (fallback) | λ per group = 1.01/1.01/1.01 | 82.2 | 0.00 | 16896 |
