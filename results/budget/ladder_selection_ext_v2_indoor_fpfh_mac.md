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

### MAC, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / giveup | 85.52 | 3281 | +0.19 [+0.43] | True | 2.44× [2.31, 2.59] | 0.289 | 0.29 |
| mondrian: x4 / mondrian | 85.61 | 4056 | +0.10 [+0.24] | True | 1.98× [1.88, 2.08] | 0.625 | 0.14 |
| fixed budget N=250 (single run) | 54.11 | 50 | | | | | |
| fixed budget N=500 (single run) | 66.35 | 84 | | | | | |
| fixed budget N=1000 (single run) | 74.67 | 365 | | | | | |
| fixed budget N=2000 (single run) | 81.50 | 1863 | | | | | |
| fixed budget N=4000 (single run) | 85.71 | 8017 | | | | | |

### MAC, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / giveup | 43.50 | 5989 | +0.00 [+0.00] | True | 1.01× [0.99, 1.02] | 1 | 0.00 |
| mondrian: x4 / mondrian | 43.17 | 6088 | +0.33 [+0.66] | True | 0.99× [0.98, 1.00] | 0.25 | 0.33 |
| fixed budget N=250 (single run) | 16.19 | 49 | | | | | |
| fixed budget N=500 (single run) | 24.45 | 73 | | | | | |
| fixed budget N=1000 (single run) | 31.72 | 325 | | | | | |
| fixed budget N=2000 (single run) | 38.22 | 1651 | | | | | |
| fixed budget N=4000 (single run) | 43.50 | 6023 | | | | | |

### MAC, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / giveup | 80.53 | 3632 | +0.74 [+1.11] | False | 2.06× [1.95, 2.18] | 0.000488 | 0.74 |
| mondrian: x4 / mondrian | 80.90 | 4415 | +0.37 [+0.62] | True | 1.70× [1.62, 1.79] | 0.0312 | 0.37 |
| fixed budget N=250 (single run) | 49.66 | 49 | | | | | |
| fixed budget N=500 (single run) | 60.44 | 83 | | | | | |
| fixed budget N=1000 (single run) | 69.01 | 356 | | | | | |
| fixed budget N=2000 (single run) | 76.16 | 1763 | | | | | |
| fixed budget N=4000 (single run) | 81.27 | 7492 | | | | | |

### MAC, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / giveup | 37.23 | 5924 | +0.06 [+0.17] | True | 1.00× [0.99, 1.01] | 1 | 0.06 |
| mondrian: x4 / mondrian | 37.23 | 6017 | +0.06 [+0.17] | True | 0.98× [0.97, 0.99] | 1 | 0.06 |
| fixed budget N=250 (single run) | 14.04 | 46 | | | | | |
| fixed budget N=500 (single run) | 19.31 | 70 | | | | | |
| fixed budget N=1000 (single run) | 26.61 | 307 | | | | | |
| fixed budget N=2000 (single run) | 32.51 | 1538 | | | | | |
| fixed budget N=4000 (single run) | 37.28 | 5910 | | | | | |
