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

### MAC, v3_blind_hi test (1976 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 92.16 | 4927 | +0.46 [+0.71] | True | 1.45× [1.39, 1.51] | 0.00391 | 0.46 |
| mondrian: 500-4000 / mondrian | 92.56 | 3615 | +0.05 [+0.15] | True | 1.97× [1.88, 2.08] | 1 | 0.05 |
| fixed budget N=250 (single run) | 56.28 | 50 | | | | | |
| fixed budget N=500 (single run) | 71.46 | 86 | | | | | |
| fixed budget N=1000 (single run) | 81.93 | 381 | | | | | |
| fixed budget N=2000 (single run) | 89.52 | 1847 | | | | | |
| fixed budget N=4000 (single run) | 92.61 | 7138 | | | | | |

### MAC, v3_blind_lo test (647 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 53.79 | 6794 | +0.46 [+0.93] | True | 1.01× [1.00, 1.02] | 0.25 | 0.46 |
| mondrian: 500-4000 / mondrian | 54.25 | 6555 | +0.00 [+0.00] | True | 1.05× [1.03, 1.07] | 1 | 0.00 |
| fixed budget N=250 (single run) | 13.45 | 55 | | | | | |
| fixed budget N=500 (single run) | 23.96 | 70 | | | | | |
| fixed budget N=1000 (single run) | 35.24 | 309 | | | | | |
| fixed budget N=2000 (single run) | 48.53 | 1625 | | | | | |
| fixed budget N=4000 (single run) | 54.25 | 6878 | | | | | |

### MAC, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 84.80 | 5426 | +0.91 [+1.24] | False | 1.48× [1.42, 1.54] | 3.81e-06 | 0.91 |
| mondrian: 500-4000 / mondrian | 85.71 | 4406 | +0.00 [+0.10] | True | 1.82× [1.74, 1.91] | 1 | 0.05 |
| fixed budget N=250 (single run) | 54.11 | 50 | | | | | |
| fixed budget N=500 (single run) | 66.35 | 84 | | | | | |
| fixed budget N=1000 (single run) | 74.67 | 365 | | | | | |
| fixed budget N=2000 (single run) | 81.50 | 1863 | | | | | |
| fixed budget N=4000 (single run) | 85.71 | 8017 | | | | | |

### MAC, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 43.28 | 5936 | +0.22 [+0.55] | True | 1.01× [1.01, 1.02] | 0.5 | 0.22 |
| mondrian: 500-4000 / mondrian | 43.50 | 5935 | +0.00 [+0.00] | True | 1.01× [1.01, 1.03] | 1 | 0.00 |
| fixed budget N=250 (single run) | 16.19 | 49 | | | | | |
| fixed budget N=500 (single run) | 24.45 | 73 | | | | | |
| fixed budget N=1000 (single run) | 31.72 | 325 | | | | | |
| fixed budget N=2000 (single run) | 38.22 | 1651 | | | | | |
| fixed budget N=4000 (single run) | 43.50 | 6023 | | | | | |

### MAC, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 80.90 | 5646 | +0.37 [+0.62] | True | 1.33× [1.28, 1.38] | 0.0312 | 0.37 |
| mondrian: 500-4000 / mondrian | 81.27 | 4672 | +0.00 [+0.00] | True | 1.60× [1.53, 1.68] | 1 | 0.00 |
| fixed budget N=250 (single run) | 49.66 | 49 | | | | | |
| fixed budget N=500 (single run) | 60.44 | 83 | | | | | |
| fixed budget N=1000 (single run) | 69.01 | 356 | | | | | |
| fixed budget N=2000 (single run) | 76.16 | 1763 | | | | | |
| fixed budget N=4000 (single run) | 81.27 | 7492 | | | | | |

### MAC, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 37.00 | 5887 | +0.28 [+0.51] | True | 1.00× [1.00, 1.01] | 0.0625 | 0.28 |
| mondrian: 500-4000 / mondrian | 37.34 | 5833 | -0.06 [+0.00] | True | 1.01× [1.01, 1.02] | 1 | 0.00 |
| fixed budget N=250 (single run) | 14.04 | 46 | | | | | |
| fixed budget N=500 (single run) | 19.31 | 70 | | | | | |
| fixed budget N=1000 (single run) | 26.61 | 307 | | | | | |
| fixed budget N=2000 (single run) | 32.51 | 1538 | | | | | |
| fixed budget N=4000 (single run) | 37.28 | 5910 | | | | | |
