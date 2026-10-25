# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## MAC

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-2000-4000 | threshold | 0.6 | 0.70 | 2754 |
| 250-2000-4000 | giveup | 0.6, 0 | 0.70 | 2754 |
| x4 | giveup | 0.8, 0.15 | 0.70 | 2965 |
| 250-1000-4000 | giveup | 0.8, 0.15 | 0.70 | 2965 |
| x4 | threshold | 0.8 | 0.70 | 2982 |
| 250-1000-4000 | threshold | 0.8 | 0.70 | 2982 |
| 250-500-4000 | giveup | 0.75, 0.15 | 0.70 | 3135 |
| 500-4000 | giveup | 0.75, 0.2 | 0.60 | 3138 |
| 250-500-4000 | threshold | 0.75 | 0.70 | 3144 |
| 500-4000 | threshold | 0.75 | 0.60 | 3173 |
| 500-2000-4000 | giveup | 0.8, 0.15 | 0.70 | 3217 |
| 500-2000-4000 | mdp | 0 | 0.40 | 3309 |
| 500-2000-4000 | threshold | 0.8 | 0.50 | 3334 |
| 250-2000-4000 | mdp | 0 | 0.30 | 3400 |
| 250-1000-2000-4000 | giveup | 0.85, 0.1 | 0.60 | 3525 |
| doubling | giveup | 0.85, 0.1 | 0.60 | 3547 |
| 250-1000-2000-4000 | threshold | 0.85 | 0.60 | 3568 |
| doubling | threshold | 0.85 | 0.60 | 3574 |
| 500-4000 | mondrian | λ per group = 0.5/0.9/0.5 | 0.20 | 3671 |
| 250-4000 | giveup | 0.6, 0.2 | 0.60 | 3771 |
| 250-4000 | threshold | 0.6 | 0.60 | 3779 |
| 250-500-4000 | mondrian | λ per group = 0.9/0.92/0.5 | 0.20 | 3912 |
| 250-500-4000 | mdp | 0 | 0.20 | 4032 |
| x4 | mondrian | λ per group = 0.93/0.94/0.5 | 0.20 | 4048 |
| 250-1000-4000 | mondrian | λ per group = 0.93/0.94/0.5 | 0.20 | 4048 |
| 250-4000 | mdp | 0 | 0.40 | 4107 |
| 250-2000-4000 | mondrian | λ per group = 0.6/0.94/0.5 | 0.20 | 4124 |
| 500-4000 | mdp | 0 | 0.30 | 4201 |
| 500-2000-4000 | mondrian | λ per group = 0.6/0.96/0.5 | 0.20 | 4245 |
| 250-4000 | mondrian | λ per group = 0.5/0.9/0.5 | 0.10 | 4263 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.94/0.95/0.5 | 0.20 | 4778 |
| doubling | mondrian | λ per group = 0.95/0.95/0.5 | 0.20 | 4841 |
| full | threshold | 1.01 | 0.00 | 7489 |
| full | mondrian | never stop early | 0.00 | 7489 |
| x4 | mdp | -1 | 0.00 | 7905 |
| 250-1000-4000 | mdp | -1 | 0.00 | 7905 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 9694 |
| doubling | mdp | -1 | 0.00 | 9773 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-2000-4000 / threshold | 250-2000-4000 / threshold | 0.9 | 77.0 | 0.57 | 4391 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.5/0.93/0.98 | 77.3 | 0.20 | 4600 |

### MAC, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-2000-4000 / threshold | 85.47 | 3553 | +0.24 [+0.48] | True | 2.26× [2.14, 2.40] | 0.18 | 0.33 |
| mondrian: 500-4000 / mondrian | 85.71 | 4391 | +0.00 [+0.10] | True | 1.83× [1.74, 1.91] | 1 | 0.05 |
| fixed budget N=250 (single run) | 54.11 | 50 | | | | | |
| fixed budget N=500 (single run) | 66.35 | 84 | | | | | |
| fixed budget N=1000 (single run) | 74.67 | 365 | | | | | |
| fixed budget N=2000 (single run) | 81.50 | 1863 | | | | | |
| fixed budget N=4000 (single run) | 85.71 | 8017 | | | | | |

### MAC, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-2000-4000 / threshold | 43.50 | 5844 | +0.00 [+0.00] | True | 1.03× [1.01, 1.05] | 1 | 0.00 |
| mondrian: 500-4000 / mondrian | 43.50 | 5929 | +0.00 [+0.00] | True | 1.02× [1.01, 1.03] | 1 | 0.00 |
| fixed budget N=250 (single run) | 16.19 | 49 | | | | | |
| fixed budget N=500 (single run) | 24.45 | 73 | | | | | |
| fixed budget N=1000 (single run) | 31.72 | 325 | | | | | |
| fixed budget N=2000 (single run) | 38.22 | 1651 | | | | | |
| fixed budget N=4000 (single run) | 43.50 | 6023 | | | | | |

### MAC, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-2000-4000 / threshold | 80.65 | 3848 | +0.62 [+0.99] | True | 1.95× [1.85, 2.05] | 0.00195 | 0.62 |
| mondrian: 500-4000 / mondrian | 81.21 | 4635 | +0.06 [+0.18] | True | 1.62× [1.55, 1.69] | 1 | 0.06 |
| fixed budget N=250 (single run) | 49.66 | 49 | | | | | |
| fixed budget N=500 (single run) | 60.44 | 83 | | | | | |
| fixed budget N=1000 (single run) | 69.01 | 356 | | | | | |
| fixed budget N=2000 (single run) | 76.16 | 1763 | | | | | |
| fixed budget N=4000 (single run) | 81.27 | 7492 | | | | | |

### MAC, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-2000-4000 / threshold | 37.17 | 5740 | +0.11 [+0.22] | True | 1.03× [1.02, 1.04] | 0.5 | 0.11 |
| mondrian: 500-4000 / mondrian | 37.28 | 5835 | +0.00 [+0.00] | True | 1.01× [1.01, 1.02] | 1 | 0.00 |
| fixed budget N=250 (single run) | 14.04 | 46 | | | | | |
| fixed budget N=500 (single run) | 19.31 | 70 | | | | | |
| fixed budget N=1000 (single run) | 26.61 | 307 | | | | | |
| fixed budget N=2000 (single run) | 32.51 | 1538 | | | | | |
| fixed budget N=4000 (single run) | 37.28 | 5910 | | | | | |
