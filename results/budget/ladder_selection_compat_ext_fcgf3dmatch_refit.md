# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## SC²-PCR

Step 1, fitting pairs (426, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1275 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-2000-4000 | mdp | 0 | 0.47 | 1388 |
| 250-500-4000 | threshold | 0.85 | 0.47 | 1389 |
| 250-500-4000 | giveup | 0.85, 0 | 0.47 | 1389 |
| 250-4000 | threshold | 0.85 | 0.47 | 1395 |
| 250-4000 | giveup | 0.85, 0 | 0.47 | 1395 |
| x4 | threshold | 0.85 | 0.47 | 1467 |
| x4 | giveup | 0.85, 0 | 0.47 | 1467 |
| 250-1000-4000 | threshold | 0.85 | 0.47 | 1467 |
| 250-1000-4000 | giveup | 0.85, 0 | 0.47 | 1467 |
| 500-4000 | threshold | 0.85 | 0.47 | 1493 |
| 500-4000 | giveup | 0.85, 0 | 0.47 | 1493 |
| 250-2000-4000 | threshold | 0.85 | 0.47 | 1739 |
| 250-2000-4000 | giveup | 0.85, 0 | 0.47 | 1739 |
| 250-500-4000 | mondrian | λ per group = 0.7/0.97/0.5 | 0.00 | 1811 |
| 250-4000 | mondrian | λ per group = 0.5/0.97/0.5 | 0.00 | 1826 |
| 500-2000-4000 | threshold | 0.85 | 0.47 | 1832 |
| 500-2000-4000 | giveup | 0.85, 0 | 0.47 | 1832 |
| 500-4000 | mondrian | λ per group = 0.5/0.96/0.5 | 0.00 | 1832 |
| 250-1000-2000-4000 | threshold | 0.85 | 0.47 | 1847 |
| 250-1000-2000-4000 | giveup | 0.85, 0 | 0.47 | 1847 |
| doubling | threshold | 0.85 | 0.47 | 1848 |
| doubling | giveup | 0.85, 0 | 0.47 | 1848 |
| x4 | mondrian | λ per group = 0.6/0.97/0.5 | 0.00 | 1895 |
| 250-1000-4000 | mondrian | λ per group = 0.6/0.97/0.5 | 0.00 | 1895 |
| 500-2000-4000 | mondrian | λ per group = 0.6/0.96/0.5 | 0.00 | 2274 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.75/0.96/0.5 | 0.00 | 2294 |
| 250-2000-4000 | mondrian | λ per group = 0.5/0.96/0.99 | 0.00 | 2423 |
| doubling | mondrian | λ per group = 0.7/0.97/0.5 | 0.00 | 2433 |
| full | threshold | 1.01 | 0.00 | 2832 |
| full | mondrian | never stop early | 0.00 | 2832 |
| 250-4000 | mdp | -1 | 0.00 | 2911 |
| 500-4000 | mdp | -1 | 0.00 | 2972 |
| 250-500-4000 | mdp | -1 | 0.00 | 3012 |
| x4 | mdp | -1 | 0.00 | 3170 |
| 250-1000-4000 | mdp | -1 | 0.00 | 3170 |
| 500-2000-4000 | mdp | -1 | 0.00 | 3790 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 3988 |
| doubling | mdp | -1 | 0.00 | 4088 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-2000-4000 / mdp | full / threshold (fallback) | 1.01 | 76.0 | 0.00 | 2798 |
| mondrian | 250-500-4000 / mondrian | 250-500-4000 / mondrian | λ per group = 0.6/0.97/0.99 | 76.1 | 0.00 | 2075 |

### SC²-PCR, fcgf_3DMatch test (812 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 92.36 | 2647 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: 250-500-4000 / mondrian | 92.24 | 1429 | +0.12 [+0.49] | True | 1.85× [1.73, 1.99] | 1 | 0.25 |
| fixed budget N=250 (single run) | 87.07 | 98 | | | | | |
| fixed budget N=500 (single run) | 88.30 | 155 | | | | | |
| fixed budget N=1000 (single run) | 90.15 | 303 | | | | | |
| fixed budget N=2000 (single run) | 91.50 | 828 | | | | | |
| fixed budget N=4000 (single run) | 92.36 | 2647 | | | | | |

### SC²-PCR, fcgf_3DLoMatch test (891 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 57.35 | 2289 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: 250-500-4000 / mondrian | 57.35 | 2258 | +0.00 [+0.00] | True | 1.01× [0.99, 1.03] | 1 | 0.00 |
| fixed budget N=250 (single run) | 44.56 | 89 | | | | | |
| fixed budget N=500 (single run) | 46.24 | 140 | | | | | |
| fixed budget N=1000 (single run) | 51.29 | 292 | | | | | |
| fixed budget N=2000 (single run) | 54.43 | 796 | | | | | |
| fixed budget N=4000 (single run) | 57.35 | 2289 | | | | | |

## TurboReg

Step 1, fitting pairs (426, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1275 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-2000-4000 | mdp | 0 | 0.47 | 2637 |
| 250-500-4000 | threshold | 0.94 | 0.47 | 2970 |
| 250-500-4000 | giveup | 0.94, 0 | 0.47 | 2970 |
| 500-4000 | threshold | 0.93 | 0.47 | 3020 |
| 500-4000 | giveup | 0.93, 0 | 0.47 | 3020 |
| 250-4000 | threshold | 0.93 | 0.47 | 3023 |
| 250-4000 | giveup | 0.93, 0 | 0.47 | 3023 |
| x4 | threshold | 0.93 | 0.47 | 3104 |
| x4 | giveup | 0.93, 0 | 0.47 | 3104 |
| 250-1000-4000 | threshold | 0.93 | 0.47 | 3104 |
| 250-1000-4000 | giveup | 0.93, 0 | 0.47 | 3104 |
| 250-4000 | mondrian | λ per group = 0.6/0.96/0.5 | 0.00 | 3272 |
| 500-4000 | mondrian | λ per group = 0.5/0.96/0.5 | 0.00 | 3335 |
| x4 | mondrian | λ per group = 0.6/0.96/0.5 | 0.00 | 3408 |
| 250-1000-4000 | mondrian | λ per group = 0.6/0.96/0.5 | 0.00 | 3408 |
| 250-500-4000 | mondrian | λ per group = 0.6/0.98/0.5 | 0.00 | 3544 |
| 250-2000-4000 | threshold | 0.93 | 0.47 | 3740 |
| 250-2000-4000 | giveup | 0.93, 0 | 0.47 | 3740 |
| 500-2000-4000 | threshold | 0.93 | 0.47 | 3821 |
| 500-2000-4000 | giveup | 0.93, 0 | 0.47 | 3821 |
| 250-1000-2000-4000 | threshold | 0.93 | 0.47 | 3913 |
| 250-1000-2000-4000 | giveup | 0.93, 0 | 0.47 | 3913 |
| 250-2000-4000 | mondrian | λ per group = 0.6/0.96/0.5 | 0.00 | 4044 |
| 500-2000-4000 | mondrian | λ per group = 0.6/0.96/0.5 | 0.00 | 4170 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.6/0.96/0.5 | 0.00 | 4185 |
| doubling | threshold | 0.94 | 0.47 | 4208 |
| doubling | giveup | 0.94, 0 | 0.47 | 4208 |
| doubling | mondrian | λ per group = 0.6/0.97/0.5 | 0.00 | 4631 |
| full | threshold | 1.01 | 0.00 | 4964 |
| full | mondrian | never stop early | 0.00 | 4964 |
| 250-4000 | mdp | -1 | 0.00 | 5172 |
| 500-4000 | mdp | -1 | 0.00 | 5315 |
| 250-500-4000 | mdp | -1 | 0.00 | 5483 |
| x4 | mdp | -1 | 0.00 | 5842 |
| 250-1000-4000 | mdp | -1 | 0.00 | 5842 |
| 500-2000-4000 | mdp | -1 | 0.00 | 6939 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 7467 |
| doubling | mdp | -1 | 0.00 | 7777 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-2000-4000 / mdp | full / threshold (fallback) | 1.01 | 75.9 | 0.00 | 4881 |
| mondrian | 250-4000 / mondrian | 250-4000 / mondrian | λ per group = 0.6/0.94/0.98 | 76.0 | 0.00 | 3328 |

### TurboReg, fcgf_3DMatch test (812 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 92.12 | 5155 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: 250-4000 / mondrian | 91.75 | 2185 | +0.37 [+0.74] | True | 2.36× [2.18, 2.58] | 0.25 | 0.37 |
| fixed budget N=250 (single run) | 86.70 | 209 | | | | | |
| fixed budget N=500 (single run) | 88.67 | 338 | | | | | |
| fixed budget N=1000 (single run) | 90.02 | 673 | | | | | |
| fixed budget N=2000 (single run) | 91.26 | 1657 | | | | | |
| fixed budget N=4000 (single run) | 92.12 | 5155 | | | | | |

### TurboReg, fcgf_3DLoMatch test (891 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 58.02 | 4695 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: 250-4000 / mondrian | 57.91 | 4365 | +0.11 [+0.34] | True | 1.08× [1.05, 1.10] | 1 | 0.11 |
| fixed budget N=250 (single run) | 44.22 | 202 | | | | | |
| fixed budget N=500 (single run) | 46.58 | 329 | | | | | |
| fixed budget N=1000 (single run) | 51.40 | 647 | | | | | |
| fixed budget N=2000 (single run) | 53.98 | 1599 | | | | | |
| fixed budget N=4000 (single run) | 58.02 | 4695 | | | | | |
