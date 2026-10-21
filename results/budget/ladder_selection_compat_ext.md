# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## SC²-PCR

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1331 calibration pairs (cheapest first):

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
| marginal | 250-4000 / threshold | 250-4000 / threshold | 0.6 | 71.0 | 0.60 | 832 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.7/0.9/0.5 | 71.5 | 0.00 | 1029 |

### SC²-PCR, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / threshold | 80.90 | 1268 | +0.62 [+1.05] | False | 2.23× [2.11, 2.35] | 0.0213 | 0.80 |
| mondrian: 500-4000 / mondrian | 81.39 | 1630 | +0.12 [+0.31] | True | 1.73× [1.66, 1.81] | 0.625 | 0.18 |
| fixed budget N=250 (single run) | 65.13 | 81 | | | | | |
| fixed budget N=500 (single run) | 69.32 | 155 | | | | | |
| fixed budget N=1000 (single run) | 74.25 | 350 | | | | | |
| fixed budget N=2000 (single run) | 78.00 | 961 | | | | | |
| fixed budget N=4000 (single run) | 81.52 | 2825 | | | | | |

### SC²-PCR, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / threshold | 36.61 | 2324 | +0.00 [+0.17] | True | 1.09× [1.07, 1.11] | 1 | 0.11 |
| mondrian: 500-4000 / mondrian | 36.61 | 2581 | +0.00 [+0.00] | True | 0.98× [0.97, 0.99] | 1 | 0.00 |
| fixed budget N=250 (single run) | 21.45 | 84 | | | | | |
| fixed budget N=500 (single run) | 24.71 | 164 | | | | | |
| fixed budget N=1000 (single run) | 28.19 | 367 | | | | | |
| fixed budget N=2000 (single run) | 32.17 | 938 | | | | | |
| fixed budget N=4000 (single run) | 36.61 | 2538 | | | | | |

## TurboReg

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1331 calibration pairs (cheapest first):

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
| marginal | 500-4000 / giveup | 500-4000 / giveup | 0.75, 0.15 | 71.8 | 0.60 | 1636 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.6/0.92/0.5 | 72.2 | 0.00 | 1943 |

### TurboReg, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 81.21 | 2333 | +0.68 [+1.05] | False | 2.01× [1.91, 2.11] | 0.000977 | 0.68 |
| mondrian: 500-4000 / mondrian | 81.70 | 2842 | +0.18 [+0.37] | True | 1.65× [1.58, 1.72] | 0.25 | 0.18 |
| fixed budget N=250 (single run) | 65.00 | 195 | | | | | |
| fixed budget N=500 (single run) | 69.32 | 341 | | | | | |
| fixed budget N=1000 (single run) | 74.00 | 685 | | | | | |
| fixed budget N=2000 (single run) | 78.31 | 1645 | | | | | |
| fixed budget N=4000 (single run) | 81.89 | 4686 | | | | | |

### TurboReg, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 36.38 | 4127 | +0.17 [+0.34] | True | 1.02× [1.01, 1.04] | 0.25 | 0.17 |
| mondrian: 500-4000 / mondrian | 36.55 | 4353 | +0.00 [+0.00] | True | 0.97× [0.96, 0.98] | 1 | 0.00 |
| fixed budget N=250 (single run) | 21.56 | 146 | | | | | |
| fixed budget N=500 (single run) | 24.93 | 321 | | | | | |
| fixed budget N=1000 (single run) | 28.13 | 679 | | | | | |
| fixed budget N=2000 (single run) | 32.06 | 1592 | | | | | |
| fixed budget N=4000 (single run) | 36.55 | 4224 | | | | | |
