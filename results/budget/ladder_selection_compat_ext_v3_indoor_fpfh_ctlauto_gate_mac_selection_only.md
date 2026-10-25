# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## MAC

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-2000-4000 | giveup | 0.6, 0.02 | 0.70 | 2490 |
| 500-2000-4000 | threshold | 0.6 | 0.60 | 2496 |
| 500-4000 | threshold | 0.6 | 0.70 | 2506 |
| 500-4000 | giveup | 0.6, 0 | 0.70 | 2506 |
| x4 | threshold | 0.7 | 0.60 | 2522 |
| x4 | giveup | 0.7, 0 | 0.60 | 2522 |
| 250-1000-4000 | threshold | 0.7 | 0.60 | 2522 |
| 250-1000-4000 | giveup | 0.7, 0 | 0.60 | 2522 |
| 250-500-4000 | threshold | 0.7 | 0.60 | 2646 |
| 250-500-4000 | giveup | 0.7, 0 | 0.60 | 2646 |
| 500-2000-4000 | mondrian | λ per group = 0.7/0.7/0.5 | 0.20 | 2692 |
| x4 | mdp | 0 | 0.50 | 2694 |
| 250-1000-4000 | mdp | 0 | 0.50 | 2694 |
| 500-4000 | mondrian | λ per group = 0.7/0.7/0.5 | 0.20 | 2712 |
| 250-2000-4000 | giveup | 0.7, 0.05 | 0.40 | 2730 |
| doubling | giveup | 0.7, 0.05 | 0.70 | 2758 |
| 250-2000-4000 | threshold | 0.7 | 0.40 | 2769 |
| doubling | threshold | 0.7 | 0.70 | 2771 |
| x4 | mondrian | λ per group = 0.7/0.8/0.5 | 0.20 | 2811 |
| 250-1000-4000 | mondrian | λ per group = 0.7/0.8/0.5 | 0.20 | 2811 |
| 250-500-4000 | mdp | 0 | 0.40 | 2831 |
| 250-2000-4000 | mdp | 0 | 0.10 | 2856 |
| 250-4000 | giveup | 0.7, 0.1 | 0.60 | 2859 |
| doubling | mdp | 0 | 0.50 | 2864 |
| 250-4000 | threshold | 0.7 | 0.30 | 2883 |
| 250-1000-2000-4000 | mdp | 0 | 0.60 | 2918 |
| 250-500-4000 | mondrian | λ per group = 0.6/0.85/0.5 | 0.20 | 2931 |
| 250-1000-2000-4000 | giveup | 0.75, 0.05 | 0.50 | 2962 |
| 250-1000-2000-4000 | threshold | 0.75 | 0.40 | 2981 |
| 500-2000-4000 | mdp | 0 | 0.10 | 3000 |
| 500-4000 | mdp | 0 | 0.10 | 3044 |
| 250-4000 | mdp | 0 | 0.20 | 3084 |
| 250-4000 | mondrian | λ per group = 0.7/0.85/0.5 | 0.10 | 3133 |
| 250-2000-4000 | mondrian | λ per group = 0.7/0.85/0.5 | 0.10 | 3171 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.7/0.88/0.5 | 0.20 | 3307 |
| doubling | mondrian | λ per group = 0.8/0.88/0.5 | 0.10 | 3541 |
| full | threshold | 1.01 | 0.00 | 7656 |
| full | mondrian | never stop early | 0.00 | 7656 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-2000-4000 / giveup | 500-2000-4000 / giveup | 0.8, 0.02 | 76.8 | 0.73 | 3177 |
| mondrian | 500-2000-4000 / mondrian | 500-2000-4000 / mondrian | λ per group = 0.85/0.94/0.5 | 77.2 | 0.30 | 4330 |
