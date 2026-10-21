# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## SC²-PCR

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1701 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-4000 | threshold | 0.6 | 0.60 | 1164 |
| 250-4000 | giveup | 0.6, 0 | 0.60 | 1164 |
| x4 | threshold | 0.7 | 0.60 | 1205 |
| x4 | giveup | 0.7, 0 | 0.60 | 1205 |
| 250-1000-4000 | threshold | 0.7 | 0.60 | 1205 |
| 250-1000-4000 | giveup | 0.7, 0 | 0.60 | 1205 |
| 500-4000 | threshold | 0.7 | 0.40 | 1222 |
| 500-4000 | giveup | 0.7, 0 | 0.40 | 1222 |
| 250-500-4000 | threshold | 0.75 | 0.60 | 1241 |
| 250-500-4000 | giveup | 0.75, 0 | 0.60 | 1241 |
| x4 | mdp | 0 | 0.20 | 1271 |
| 250-1000-4000 | mdp | 0 | 0.20 | 1271 |
| 250-500-4000 | mdp | 0 | 0.50 | 1299 |
| 500-2000-4000 | threshold | 0.7 | 0.60 | 1349 |
| 500-2000-4000 | giveup | 0.7, 0 | 0.60 | 1349 |
| 500-2000-4000 | mdp | 0 | 0.40 | 1370 |
| 250-2000-4000 | mdp | 0 | 0.40 | 1385 |
| 250-2000-4000 | threshold | 0.75 | 0.60 | 1394 |
| 250-2000-4000 | giveup | 0.75, 0 | 0.60 | 1394 |
| 250-1000-2000-4000 | mdp | 0 | 0.50 | 1406 |
| 250-4000 | mdp | 0 | 0.50 | 1421 |
| 250-1000-2000-4000 | threshold | 0.75 | 0.60 | 1436 |
| 250-1000-2000-4000 | giveup | 0.75, 0 | 0.60 | 1436 |
| 500-4000 | mdp | 0 | 0.30 | 1511 |
| 500-4000 | mondrian | λ per group = 0.5/0.94/0.5 | 0.00 | 1578 |
| doubling | giveup | 0.8, 0.1 | 0.60 | 1585 |
| doubling | threshold | 0.8 | 0.50 | 1592 |
| 250-4000 | mondrian | λ per group = 0.5/0.98/0.5 | 0.00 | 1666 |
| 250-500-4000 | mondrian | λ per group = 0.7/0.98/0.5 | 0.00 | 1699 |
| x4 | mondrian | λ per group = 0.5/0.98/0.5 | 0.00 | 1740 |
| 250-1000-4000 | mondrian | λ per group = 0.5/0.98/0.5 | 0.00 | 1740 |
| 500-2000-4000 | mondrian | λ per group = 0.85/0.94/0.5 | 0.00 | 1939 |
| 250-2000-4000 | mondrian | λ per group = 0.8/0.98/0.5 | 0.00 | 2046 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.85/0.98/0.5 | 0.00 | 2223 |
| doubling | mondrian | λ per group = 0.8/0.98/0.5 | 0.00 | 2262 |
| full | threshold | 1.01 | 0.00 | 2463 |
| full | mondrian | never stop early | 0.00 | 2463 |
| doubling | mdp | -1 | 0.00 | 3621 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-4000 / threshold | full / threshold (fallback) | 1.01 | 75.1 | 0.00 | 2806 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 1.01/0.99/1.01 | 75.1 | 0.00 | 2943 |

### SC²-PCR, fcgf_3DMatch test (812 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 92.36 | 2647 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: 500-4000 / mondrian | 92.36 | 2800 | +0.00 [+0.00] | True | 0.95× [0.94, 0.95] | 1 | 0.00 |
| fixed budget N=250 (single run) | 87.07 | 98 | | | | | |
| fixed budget N=500 (single run) | 88.30 | 155 | | | | | |
| fixed budget N=1000 (single run) | 90.15 | 303 | | | | | |
| fixed budget N=2000 (single run) | 91.50 | 828 | | | | | |
| fixed budget N=4000 (single run) | 92.36 | 2647 | | | | | |

### SC²-PCR, fcgf_3DLoMatch test (891 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 57.35 | 2289 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: 500-4000 / mondrian | 57.35 | 2424 | +0.00 [+0.00] | True | 0.94× [0.94, 0.95] | 1 | 0.00 |
| fixed budget N=250 (single run) | 44.56 | 89 | | | | | |
| fixed budget N=500 (single run) | 46.24 | 140 | | | | | |
| fixed budget N=1000 (single run) | 51.29 | 292 | | | | | |
| fixed budget N=2000 (single run) | 54.43 | 796 | | | | | |
| fixed budget N=4000 (single run) | 57.35 | 2289 | | | | | |

## TurboReg

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1701 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-4000 | giveup | 0.5, 0.15 | 0.60 | 1866 |
| 500-4000 | threshold | 0.5 | 0.60 | 1867 |
| 250-4000 | threshold | 0.7 | 0.50 | 2158 |
| 250-4000 | giveup | 0.7, 0 | 0.50 | 2158 |
| 250-500-4000 | mdp | 0 | 0.40 | 2161 |
| 500-2000-4000 | giveup | 0.6, 0.1 | 0.50 | 2161 |
| 500-2000-4000 | threshold | 0.6 | 0.50 | 2163 |
| x4 | giveup | 0.75, 0.15 | 0.60 | 2174 |
| 250-1000-4000 | giveup | 0.75, 0.15 | 0.60 | 2174 |
| x4 | threshold | 0.75 | 0.60 | 2178 |
| 250-1000-4000 | threshold | 0.75 | 0.60 | 2178 |
| 250-2000-4000 | mdp | 0 | 0.60 | 2247 |
| 250-500-4000 | giveup | 0.8, 0.15 | 0.50 | 2270 |
| 250-500-4000 | threshold | 0.8 | 0.50 | 2271 |
| 250-4000 | mdp | 0 | 0.50 | 2284 |
| 250-2000-4000 | giveup | 0.75, 0.15 | 0.60 | 2408 |
| 250-2000-4000 | threshold | 0.75 | 0.50 | 2422 |
| 500-4000 | mdp | 0 | 0.20 | 2492 |
| 500-4000 | mondrian | λ per group = 0.5/0.92/0.5 | 0.00 | 2638 |
| 500-2000-4000 | mdp | 0 | 0.10 | 2643 |
| 250-1000-2000-4000 | giveup | 0.8, 0.15 | 0.60 | 2678 |
| 250-1000-2000-4000 | threshold | 0.8 | 0.50 | 2702 |
| 250-4000 | mondrian | λ per group = 0.5/0.98/0.5 | 0.00 | 2876 |
| 250-500-4000 | mondrian | λ per group = 0.5/0.98/0.5 | 0.00 | 2924 |
| doubling | giveup | 0.85, 0.15 | 0.60 | 2990 |
| doubling | threshold | 0.85 | 0.50 | 3002 |
| x4 | mondrian | λ per group = 0.75/0.98/0.5 | 0.00 | 3089 |
| 250-1000-4000 | mondrian | λ per group = 0.75/0.98/0.5 | 0.00 | 3089 |
| 500-2000-4000 | mondrian | λ per group = 0.85/0.93/0.5 | 0.00 | 3269 |
| 250-2000-4000 | mondrian | λ per group = 0.8/0.98/0.5 | 0.00 | 3545 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.85/0.98/0.5 | 0.00 | 3893 |
| doubling | mondrian | λ per group = 0.85/0.98/0.5 | 0.00 | 4032 |
| full | threshold | 1.01 | 0.00 | 4195 |
| full | mondrian | never stop early | 0.00 | 4195 |
| x4 | mdp | -1 | 0.00 | 4876 |
| 250-1000-4000 | mdp | -1 | 0.00 | 4876 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 6163 |
| doubling | mdp | -1 | 0.00 | 6410 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-4000 / giveup | 500-4000 / giveup | 1.01, 0.15 | 75.1 | 0.00 | 5253 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 1.01/0.99/1.01 | 75.1 | 0.00 | 5247 |

### TurboReg, fcgf_3DMatch test (812 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 92.12 | 5494 | +0.00 [+0.00] | True | 0.94× [0.94, 0.94] | 1 | 0.00 |
| mondrian: 500-4000 / mondrian | 92.12 | 5489 | +0.00 [+0.00] | True | 0.94× [0.94, 0.94] | 1 | 0.00 |
| fixed budget N=250 (single run) | 86.70 | 209 | | | | | |
| fixed budget N=500 (single run) | 88.67 | 338 | | | | | |
| fixed budget N=1000 (single run) | 90.02 | 673 | | | | | |
| fixed budget N=2000 (single run) | 91.26 | 1657 | | | | | |
| fixed budget N=4000 (single run) | 92.12 | 5155 | | | | | |

### TurboReg, fcgf_3DLoMatch test (891 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 58.02 | 5024 | +0.00 [+0.00] | True | 0.93× [0.93, 0.94] | 1 | 0.00 |
| mondrian: 500-4000 / mondrian | 57.91 | 5010 | +0.11 [+0.34] | True | 0.94× [0.93, 0.94] | 1 | 0.11 |
| fixed budget N=250 (single run) | 44.22 | 202 | | | | | |
| fixed budget N=500 (single run) | 46.58 | 329 | | | | | |
| fixed budget N=1000 (single run) | 51.40 | 647 | | | | | |
| fixed budget N=2000 (single run) | 53.98 | 1599 | | | | | |
| fixed budget N=4000 (single run) | 58.02 | 4695 | | | | | |
