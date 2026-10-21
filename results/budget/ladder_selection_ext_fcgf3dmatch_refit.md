# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## SC²-PCR

Step 1, fitting pairs (426, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1275 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-4000 | threshold | 0.92 | 0.47 | 1859 |
| 500-4000 | giveup | 0.92, 0 | 0.47 | 1859 |
| 250-4000 | giveup | 0.94, 0.15 | 0.47 | 1923 |
| 250-4000 | threshold | 0.94 | 0.47 | 1923 |
| 250-500-4000 | giveup | 0.96, 0.1 | 0.47 | 2031 |
| 250-500-4000 | threshold | 0.96 | 0.23 | 2039 |
| 250-500-4000 | mondrian | λ per group = 0.5/0.93/0.98 | 0.00 | 2042 |
| 250-4000 | mondrian | λ per group = 0.5/0.9/0.98 | 0.00 | 2103 |
| 250-2000-4000 | mondrian | λ per group = 0.5/0.9/0.98 | 0.00 | 2127 |
| 500-2000-4000 | threshold | 0.92 | 0.47 | 2144 |
| 500-2000-4000 | giveup | 0.92, 0 | 0.47 | 2144 |
| x4 | mondrian | λ per group = 0.7/0.93/0.98 | 0.00 | 2146 |
| 250-1000-4000 | mondrian | λ per group = 0.7/0.93/0.98 | 0.00 | 2146 |
| x4 | giveup | 0.96, 0.1 | 0.47 | 2158 |
| 250-1000-4000 | giveup | 0.96, 0.1 | 0.47 | 2158 |
| x4 | threshold | 0.96 | 0.47 | 2160 |
| 250-1000-4000 | threshold | 0.96 | 0.47 | 2160 |
| 500-4000 | mondrian | λ per group = 0.6/0.92/0.99 | 0.00 | 2223 |
| 250-2000-4000 | threshold | 0.94 | 0.47 | 2266 |
| 250-2000-4000 | giveup | 0.94, 0 | 0.47 | 2266 |
| 500-2000-4000 | mondrian | λ per group = 0.6/0.92/0.99 | 0.00 | 2464 |
| 250-1000-2000-4000 | threshold | 0.97 | 0.23 | 2800 |
| 250-1000-2000-4000 | giveup | 0.97, 0 | 0.23 | 2800 |
| full | threshold | 1.01 | 0.00 | 2832 |
| full | mondrian | never stop early | 0.00 | 2832 |
| 250-4000 | mdp | -1 | 0.00 | 2880 |
| doubling | threshold | 0.97 | 0.23 | 2907 |
| doubling | giveup | 0.97, 0 | 0.23 | 2907 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.6/0.95/0.99 | 0.00 | 2915 |
| doubling | mondrian | λ per group = 0.7/0.94/0.99 | 0.00 | 2940 |
| 500-4000 | mdp | -1 | 0.00 | 2968 |
| 250-500-4000 | mdp | -1 | 0.00 | 3016 |
| x4 | mdp | -1 | 0.00 | 3243 |
| 250-1000-4000 | mdp | -1 | 0.00 | 3243 |
| 250-2000-4000 | mdp | -1 | 0.00 | 3821 |
| 500-2000-4000 | mdp | -1 | 0.00 | 3909 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 4184 |
| doubling | mdp | -1 | 0.00 | 4319 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-4000 / threshold | 500-4000 / threshold | 0.75 | 75.8 | 0.55 | 1357 |
| mondrian | 250-500-4000 / mondrian | 250-500-4000 / mondrian | λ per group = 0.7/0.96/0.97 | 76.1 | 0.00 | 2084 |

### SC²-PCR, fcgf_3DMatch test (812 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 91.87 | 543 | +0.49 [+1.11] | False | 4.87× [4.35, 5.56] | 0.344 | 0.86 |
| mondrian: 250-500-4000 / mondrian | 92.24 | 1340 | +0.12 [+0.37] | True | 1.98× [1.84, 2.14] | 1 | 0.12 |
| fixed budget N=250 (single run) | 85.71 | 59 | | | | | |
| fixed budget N=500 (single run) | 88.92 | 152 | | | | | |
| fixed budget N=1000 (single run) | 90.52 | 369 | | | | | |
| fixed budget N=2000 (single run) | 91.63 | 917 | | | | | |
| fixed budget N=4000 (single run) | 92.36 | 2647 | | | | | |

### SC²-PCR, fcgf_3DLoMatch test (891 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 56.79 | 1836 | +0.56 [+1.01] | True | 1.25× [1.20, 1.30] | 0.125 | 0.67 |
| mondrian: 250-500-4000 / mondrian | 57.13 | 2386 | +0.22 [+0.56] | True | 0.96× [0.94, 0.98] | 0.5 | 0.22 |
| fixed budget N=250 (single run) | 39.84 | 84 | | | | | |
| fixed budget N=500 (single run) | 46.46 | 184 | | | | | |
| fixed budget N=1000 (single run) | 52.53 | 406 | | | | | |
| fixed budget N=2000 (single run) | 56.68 | 884 | | | | | |
| fixed budget N=4000 (single run) | 57.35 | 2289 | | | | | |

## TurboReg

Step 1, fitting pairs (426, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1275 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-4000 | giveup | 0.94, 0.15 | 0.47 | 3368 |
| 250-4000 | threshold | 0.94 | 0.47 | 3373 |
| 500-4000 | threshold | 0.94 | 0.47 | 3448 |
| 500-4000 | giveup | 0.94, 0 | 0.47 | 3448 |
| 250-500-4000 | mondrian | λ per group = 0.88/0.92/0.97 | 0.00 | 3513 |
| 250-500-4000 | giveup | 0.96, 0.1 | 0.47 | 3606 |
| 250-500-4000 | threshold | 0.96 | 0.23 | 3619 |
| 500-4000 | mondrian | λ per group = 0.7/0.9/0.98 | 0.00 | 3707 |
| 250-4000 | mondrian | λ per group = 0.5/0.92/0.98 | 0.00 | 3723 |
| x4 | giveup | 0.96, 0.1 | 0.47 | 3741 |
| 250-1000-4000 | giveup | 0.96, 0.1 | 0.47 | 3741 |
| 250-2000-4000 | mondrian | λ per group = 0.5/0.92/0.98 | 0.00 | 3743 |
| x4 | threshold | 0.96 | 0.47 | 3753 |
| 250-1000-4000 | threshold | 0.96 | 0.47 | 3753 |
| x4 | mondrian | λ per group = 0.85/0.95/0.98 | 0.00 | 3946 |
| 250-1000-4000 | mondrian | λ per group = 0.85/0.95/0.98 | 0.00 | 3946 |
| 500-2000-4000 | threshold | 0.94 | 0.47 | 3961 |
| 500-2000-4000 | giveup | 0.94, 0 | 0.47 | 3961 |
| 250-2000-4000 | threshold | 0.95 | 0.47 | 4006 |
| 250-2000-4000 | giveup | 0.95, 0 | 0.47 | 4006 |
| 500-2000-4000 | mondrian | λ per group = 0.7/0.92/0.98 | 0.00 | 4051 |
| doubling | mondrian | λ per group = 0.94/0.95/0.97 | 0.00 | 4806 |
| doubling | threshold | 0.96 | 0.47 | 4841 |
| doubling | giveup | 0.96, 0 | 0.47 | 4841 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.88/0.95/0.98 | 0.00 | 4847 |
| 250-1000-2000-4000 | threshold | 0.97 | 0.47 | 4859 |
| 250-1000-2000-4000 | giveup | 0.97, 0 | 0.47 | 4859 |
| full | threshold | 1.01 | 0.00 | 4964 |
| full | mondrian | never stop early | 0.00 | 4964 |
| 250-4000 | mdp | -1 | 0.00 | 5051 |
| 500-4000 | mdp | -1 | 0.00 | 5224 |
| 250-500-4000 | mdp | -1 | 0.00 | 5310 |
| x4 | mdp | -1 | 0.00 | 5705 |
| 250-1000-4000 | mdp | -1 | 0.00 | 5705 |
| 250-2000-4000 | mdp | -1 | 0.00 | 6668 |
| 500-2000-4000 | mdp | -1 | 0.00 | 6842 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 7322 |
| doubling | mdp | -1 | 0.00 | 7582 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-4000 / giveup | 250-4000 / giveup | 0.7, 0.15 | 75.9 | 0.47 | 2280 |
| mondrian | 250-500-4000 / mondrian | 250-500-4000 / mondrian | λ per group = 0.75/0.95/0.92 | 76.0 | 0.00 | 3163 |

### TurboReg, fcgf_3DMatch test (812 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / giveup | 91.63 | 1032 | +0.49 [+0.99] | True | 5.00× [4.44, 5.76] | 0.219 | 0.62 |
| mondrian: 250-500-4000 / mondrian | 91.87 | 1788 | +0.25 [+0.62] | True | 2.88× [2.63, 3.21] | 0.5 | 0.25 |
| fixed budget N=250 (single run) | 84.98 | 124 | | | | | |
| fixed budget N=500 (single run) | 88.30 | 284 | | | | | |
| fixed budget N=1000 (single run) | 90.64 | 629 | | | | | |
| fixed budget N=2000 (single run) | 91.26 | 1620 | | | | | |
| fixed budget N=4000 (single run) | 92.12 | 5155 | | | | | |

### TurboReg, fcgf_3DLoMatch test (891 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / giveup | 57.69 | 3542 | +0.34 [+0.79] | True | 1.33× [1.28, 1.38] | 0.453 | 0.56 |
| mondrian: 250-500-4000 / mondrian | 57.80 | 4367 | +0.22 [+0.45] | True | 1.08× [1.05, 1.10] | 0.5 | 0.22 |
| fixed budget N=250 (single run) | 38.61 | 49 | | | | | |
| fixed budget N=500 (single run) | 45.34 | 202 | | | | | |
| fixed budget N=1000 (single run) | 52.86 | 593 | | | | | |
| fixed budget N=2000 (single run) | 55.67 | 1536 | | | | | |
| fixed budget N=4000 (single run) | 58.02 | 4695 | | | | | |
