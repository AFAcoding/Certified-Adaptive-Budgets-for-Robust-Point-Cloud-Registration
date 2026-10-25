# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## MAC

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1331 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-4000 | giveup | 0.6, 0.1 | 0.60 | 3108 |
| 500-4000 | threshold | 0.6 | 0.60 | 3138 |
| 500-4000 | mdp | 0 | 0.50 | 3466 |
| 500-2000-4000 | giveup | 0.7, 0.05 | 0.60 | 3574 |
| 500-2000-4000 | threshold | 0.7 | 0.60 | 3609 |
| 250-500-4000 | threshold | 0.8 | 0.60 | 3813 |
| 250-500-4000 | giveup | 0.8, 0 | 0.60 | 3813 |
| 250-4000 | threshold | 0.7 | 0.60 | 3864 |
| 250-4000 | giveup | 0.7, 0 | 0.60 | 3864 |
| x4 | giveup | 0.85, 0.1 | 0.60 | 4075 |
| 250-1000-4000 | giveup | 0.85, 0.1 | 0.60 | 4075 |
| x4 | threshold | 0.85 | 0.50 | 4124 |
| 250-1000-4000 | threshold | 0.85 | 0.50 | 4124 |
| 500-2000-4000 | mdp | 0 | 0.60 | 4203 |
| 250-2000-4000 | threshold | 0.8 | 0.60 | 4298 |
| 250-2000-4000 | giveup | 0.8, 0 | 0.60 | 4298 |
| 250-1000-2000-4000 | threshold | 0.85 | 0.60 | 4794 |
| 250-1000-2000-4000 | giveup | 0.85, 0 | 0.60 | 4794 |
| doubling | threshold | 0.85 | 0.60 | 4834 |
| doubling | giveup | 0.85, 0 | 0.60 | 4834 |
| 250-2000-4000 | mdp | 0 | 0.60 | 5943 |
| 500-4000 | mondrian | λ per group = 0.75/0.99/0.5 | 0.00 | 7242 |
| 500-2000-4000 | mondrian | λ per group = 0.8/0.99/0.5 | 0.00 | 7803 |
| 250-4000 | mondrian | λ per group = 0.93/1.01/0.5 | 0.00 | 13207 |
| 250-500-4000 | mondrian | λ per group = 0.94/1.01/0.5 | 0.00 | 13257 |
| x4 | mondrian | λ per group = 0.95/1.01/0.5 | 0.00 | 13763 |
| 250-1000-4000 | mondrian | λ per group = 0.95/1.01/0.5 | 0.00 | 13763 |
| 250-2000-4000 | mondrian | λ per group = 0.94/1.01/0.5 | 0.00 | 15836 |
| full | threshold | 1.01 | 0.00 | 16478 |
| full | mondrian | never stop early | 0.00 | 16478 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.96/1.01/0.5 | 0.00 | 16598 |
| 250-4000 | mdp | -1 | 0.00 | 16610 |
| doubling | mondrian | λ per group = 0.96/1.01/0.5 | 0.00 | 16701 |
| 250-500-4000 | mdp | -1 | 0.00 | 16847 |
| x4 | mdp | -1 | 0.00 | 17448 |
| 250-1000-4000 | mdp | -1 | 0.00 | 17448 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 21046 |
| doubling | mdp | -1 | 0.00 | 21284 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-4000 / giveup | 500-4000 / giveup | 0.75, 0.1 | 75.5 | 0.45 | 3027 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.85/1.01/1.01 | 75.7 | 0.08 | 7920 |

### MAC, fcgfown_3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 92.24 | 2006 | +0.12 [+0.62] | True | 6.39× [5.75, 7.17] | 0.832 | 0.74 |
| mondrian: 500-4000 / mondrian | 92.48 | 12431 | -0.12 [+0.06] | True | 1.03× [1.02, 1.04] | 0.625 | 0.06 |
| fixed budget N=250 (single run) | 84.84 | 90 | | | | | |
| fixed budget N=500 (single run) | 88.05 | 178 | | | | | |
| fixed budget N=1000 (single run) | 90.39 | 660 | | | | | |
| fixed budget N=2000 (single run) | 92.24 | 2849 | | | | | |
| fixed budget N=4000 (single run) | 92.36 | 12819 | | | | | |

### MAC, fcgfown_3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 58.51 | 7308 | +0.90 [+1.35] | True | 1.49× [1.44, 1.56] | 0.00154 | 1.12 |
| mondrian: 500-4000 / mondrian | 59.12 | 10164 | +0.28 [+0.51] | True | 1.07× [1.06, 1.09] | 0.0625 | 0.28 |
| fixed budget N=250 (single run) | 37.84 | 76 | | | | | |
| fixed budget N=500 (single run) | 45.93 | 145 | | | | | |
| fixed budget N=1000 (single run) | 53.68 | 593 | | | | | |
| fixed budget N=2000 (single run) | 58.00 | 2680 | | | | | |
| fixed budget N=4000 (single run) | 59.40 | 10920 | | | | | |
