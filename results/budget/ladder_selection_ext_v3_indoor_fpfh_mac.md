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

### MAC, v3_blind_hi test (1976 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / threshold | 92.46 | 2618 | +0.15 [+0.30] | True | 2.73× [2.56, 2.92] | 0.25 | 0.15 |
| mondrian: 500-4000 / mondrian | 92.56 | 3280 | +0.05 [+0.15] | True | 2.18× [2.06, 2.31] | 1 | 0.05 |
| fixed budget N=250 (single run) | 56.28 | 50 | | | | | |
| fixed budget N=500 (single run) | 71.46 | 86 | | | | | |
| fixed budget N=1000 (single run) | 81.93 | 381 | | | | | |
| fixed budget N=2000 (single run) | 89.52 | 1847 | | | | | |
| fixed budget N=4000 (single run) | 92.61 | 7138 | | | | | |

### MAC, v3_blind_lo test (647 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / threshold | 54.10 | 6530 | +0.15 [+0.46] | True | 1.05× [1.03, 1.08] | 1 | 0.15 |
| mondrian: 500-4000 / mondrian | 54.25 | 6538 | +0.00 [+0.00] | True | 1.05× [1.03, 1.08] | 1 | 0.00 |
| fixed budget N=250 (single run) | 13.45 | 55 | | | | | |
| fixed budget N=500 (single run) | 23.96 | 70 | | | | | |
| fixed budget N=1000 (single run) | 35.24 | 309 | | | | | |
| fixed budget N=2000 (single run) | 48.53 | 1625 | | | | | |
| fixed budget N=4000 (single run) | 54.25 | 6878 | | | | | |

### MAC, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / threshold | 85.47 | 3269 | +0.24 [+0.48] | True | 2.45× [2.32, 2.60] | 0.18 | 0.33 |
| mondrian: 500-4000 / mondrian | 85.71 | 4024 | +0.00 [+0.10] | True | 1.99× [1.89, 2.10] | 1 | 0.05 |
| fixed budget N=250 (single run) | 54.11 | 50 | | | | | |
| fixed budget N=500 (single run) | 66.35 | 84 | | | | | |
| fixed budget N=1000 (single run) | 74.67 | 365 | | | | | |
| fixed budget N=2000 (single run) | 81.50 | 1863 | | | | | |
| fixed budget N=4000 (single run) | 85.71 | 8017 | | | | | |

### MAC, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / threshold | 43.50 | 5994 | +0.00 [+0.00] | True | 1.00× [0.99, 1.02] | 1 | 0.00 |
| mondrian: 500-4000 / mondrian | 43.50 | 5911 | +0.00 [+0.00] | True | 1.02× [1.01, 1.03] | 1 | 0.00 |
| fixed budget N=250 (single run) | 16.19 | 49 | | | | | |
| fixed budget N=500 (single run) | 24.45 | 73 | | | | | |
| fixed budget N=1000 (single run) | 31.72 | 325 | | | | | |
| fixed budget N=2000 (single run) | 38.22 | 1651 | | | | | |
| fixed budget N=4000 (single run) | 43.50 | 6023 | | | | | |

### MAC, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / threshold | 80.78 | 3634 | +0.49 [+0.80] | True | 2.06× [1.95, 2.18] | 0.00781 | 0.49 |
| mondrian: 500-4000 / mondrian | 81.15 | 4347 | +0.12 [+0.31] | True | 1.72× [1.64, 1.81] | 0.5 | 0.12 |
| fixed budget N=250 (single run) | 49.66 | 49 | | | | | |
| fixed budget N=500 (single run) | 60.44 | 83 | | | | | |
| fixed budget N=1000 (single run) | 69.01 | 356 | | | | | |
| fixed budget N=2000 (single run) | 76.16 | 1763 | | | | | |
| fixed budget N=4000 (single run) | 81.27 | 7492 | | | | | |

### MAC, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / threshold | 37.23 | 5949 | +0.06 [+0.17] | True | 0.99× [0.98, 1.00] | 1 | 0.06 |
| mondrian: 500-4000 / mondrian | 37.28 | 5824 | +0.00 [+0.00] | True | 1.01× [1.01, 1.02] | 1 | 0.00 |
| fixed budget N=250 (single run) | 14.04 | 46 | | | | | |
| fixed budget N=500 (single run) | 19.31 | 70 | | | | | |
| fixed budget N=1000 (single run) | 26.61 | 307 | | | | | |
| fixed budget N=2000 (single run) | 32.51 | 1538 | | | | | |
| fixed budget N=4000 (single run) | 37.28 | 5910 | | | | | |
