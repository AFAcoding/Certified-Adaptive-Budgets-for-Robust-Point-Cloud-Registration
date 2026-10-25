# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## MAC

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1331 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-4000 | threshold | 0.5 | 0.60 | 2694 |
| 500-4000 | giveup | 0.5, 0 | 0.60 | 2694 |
| 250-4000 | threshold | 0.5 | 0.60 | 2796 |
| 250-4000 | giveup | 0.5, 0 | 0.60 | 2796 |
| 500-2000-4000 | threshold | 0.6 | 0.40 | 3236 |
| 500-2000-4000 | giveup | 0.6, 0 | 0.40 | 3236 |
| 250-500-4000 | threshold | 0.7 | 0.60 | 3268 |
| 250-500-4000 | giveup | 0.7, 0 | 0.60 | 3268 |
| 250-4000 | mdp | 0 | 0.50 | 3281 |
| x4 | threshold | 0.7 | 0.60 | 3337 |
| x4 | giveup | 0.7, 0 | 0.60 | 3337 |
| 250-1000-4000 | threshold | 0.7 | 0.60 | 3337 |
| 250-1000-4000 | giveup | 0.7, 0 | 0.60 | 3337 |
| 500-4000 | mdp | 0 | 0.40 | 3429 |
| 250-2000-4000 | mdp | 0 | 0.50 | 3613 |
| 250-2000-4000 | giveup | 0.7, 0.05 | 0.60 | 3671 |
| 250-2000-4000 | threshold | 0.7 | 0.50 | 3686 |
| 250-1000-2000-4000 | mdp | 0 | 0.60 | 3728 |
| doubling | giveup | 0.7, 0.05 | 0.60 | 3739 |
| doubling | threshold | 0.7 | 0.50 | 3749 |
| 250-1000-2000-4000 | threshold | 0.7 | 0.60 | 3835 |
| 250-1000-2000-4000 | giveup | 0.7, 0 | 0.60 | 3835 |
| 500-2000-4000 | mdp | 0 | 0.30 | 3865 |
| 500-4000 | mondrian | λ per group = 0.85/0.995/0.5 | 0.00 | 6473 |
| 500-2000-4000 | mondrian | λ per group = 0.85/0.995/0.5 | 0.00 | 7541 |
| 250-500-4000 | mondrian | λ per group = 0.92/1.01/0.5 | 0.00 | 12596 |
| 250-4000 | mondrian | λ per group = 0.95/1.01/0.5 | 0.00 | 12654 |
| x4 | mondrian | λ per group = 0.94/1.01/0.5 | 0.00 | 12934 |
| 250-1000-4000 | mondrian | λ per group = 0.94/1.01/0.5 | 0.00 | 12934 |
| 250-2000-4000 | mondrian | λ per group = 0.95/1.01/0.5 | 0.00 | 14848 |
| doubling | mondrian | λ per group = 0.9/1.01/0.5 | 0.00 | 15059 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.92/1.01/0.5 | 0.00 | 15064 |
| full | threshold | 1.01 | 0.00 | 16478 |
| full | mondrian | never stop early | 0.00 | 16478 |
| 250-500-4000 | mdp | -1 | 0.00 | 16834 |
| x4 | mdp | -1 | 0.00 | 17394 |
| 250-1000-4000 | mdp | -1 | 0.00 | 17394 |
| doubling | mdp | -1 | 0.00 | 20881 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-4000 / threshold | 500-4000 / threshold | 0.6 | 75.2 | 0.60 | 2519 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.85/1.01/1.01 | 75.6 | 0.15 | 7833 |

### MAC, fcgfown_3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 92.24 | 1656 | +0.12 [+0.55] | True | 7.74× [6.87, 8.87] | 0.815 | 0.62 |
| mondrian: 500-4000 / mondrian | 92.24 | 12059 | +0.12 [+0.31] | True | 1.06× [1.05, 1.08] | 0.625 | 0.18 |
| fixed budget N=250 (single run) | 87.31 | 107 | | | | | |
| fixed budget N=500 (single run) | 88.60 | 186 | | | | | |
| fixed budget N=1000 (single run) | 89.83 | 561 | | | | | |
| fixed budget N=2000 (single run) | 91.07 | 2664 | | | | | |
| fixed budget N=4000 (single run) | 92.36 | 12819 | | | | | |

### MAC, fcgfown_3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 58.90 | 6532 | +0.51 [+0.90] | True | 1.67× [1.60, 1.74] | 0.0784 | 0.84 |
| mondrian: 500-4000 / mondrian | 59.35 | 10003 | +0.06 [+0.22] | True | 1.09× [1.08, 1.11] | 1 | 0.11 |
| fixed budget N=250 (single run) | 44.47 | 120 | | | | | |
| fixed budget N=500 (single run) | 47.45 | 252 | | | | | |
| fixed budget N=1000 (single run) | 51.54 | 852 | | | | | |
| fixed budget N=2000 (single run) | 56.09 | 3170 | | | | | |
| fixed budget N=4000 (single run) | 59.40 | 10920 | | | | | |
