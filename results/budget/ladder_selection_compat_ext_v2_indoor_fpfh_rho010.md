# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## SC²-PCR

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-4000 | threshold | 0.5 | 0.70 | 1180 |
| 250-4000 | giveup | 0.5, 0 | 0.70 | 1180 |
| 250-4000 | mondrian | λ per group = 0.5/0.9/0.5 | 0.10 | 1500 |
| 250-4000 | mdp | 0 | 0.10 | 1577 |
| full | threshold | 1.01 | 0.00 | 2600 |
| full | mondrian | never stop early | 0.00 | 2600 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-4000 / threshold | 250-4000 / threshold | 0.88 | 76.8 | 0.57 | 1531 |
| mondrian | 250-4000 / mondrian | 250-4000 / mondrian | λ per group = 0.5/0.97/0.995 | 77.2 | 0.17 | 2042 |

### SC²-PCR, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / threshold | 85.13 | 1333 | +0.05 [+0.19] | True | 2.02× [1.93, 2.11] | 1 | 0.10 |
| mondrian: 250-4000 / mondrian | 85.18 | 1906 | +0.00 [+0.10] | True | 1.41× [1.37, 1.45] | 1 | 0.05 |
| fixed budget N=250 (single run) | 68.83 | 72 | | | | | |
| fixed budget N=500 (single run) | 73.71 | 142 | | | | | |
| fixed budget N=1000 (single run) | 77.82 | 339 | | | | | |
| fixed budget N=2000 (single run) | 81.88 | 943 | | | | | |
| fixed budget N=4000 (single run) | 85.18 | 2690 | | | | | |

### SC²-PCR, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / threshold | 40.53 | 2358 | +0.00 [+0.00] | True | 1.04× [1.03, 1.06] | 1 | 0.00 |
| mondrian: 250-4000 / mondrian | 40.53 | 2493 | +0.00 [+0.00] | True | 0.99× [0.98, 0.99] | 1 | 0.00 |
| fixed budget N=250 (single run) | 23.46 | 75 | | | | | |
| fixed budget N=500 (single run) | 27.86 | 150 | | | | | |
| fixed budget N=1000 (single run) | 32.16 | 350 | | | | | |
| fixed budget N=2000 (single run) | 36.12 | 935 | | | | | |
| fixed budget N=4000 (single run) | 40.53 | 2457 | | | | | |

### SC²-PCR, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / threshold | 81.39 | 1527 | +0.12 [+0.31] | True | 1.85× [1.77, 1.94] | 0.625 | 0.18 |
| mondrian: 250-4000 / mondrian | 81.45 | 2116 | +0.06 [+0.25] | True | 1.34× [1.30, 1.38] | 1 | 0.12 |
| fixed budget N=250 (single run) | 65.13 | 81 | | | | | |
| fixed budget N=500 (single run) | 69.32 | 155 | | | | | |
| fixed budget N=1000 (single run) | 74.25 | 350 | | | | | |
| fixed budget N=2000 (single run) | 78.00 | 961 | | | | | |
| fixed budget N=4000 (single run) | 81.52 | 2825 | | | | | |

### SC²-PCR, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / threshold | 36.61 | 2483 | +0.00 [+0.00] | True | 1.02× [1.01, 1.03] | 1 | 0.00 |
| mondrian: 250-4000 / mondrian | 36.66 | 2592 | -0.06 [+0.00] | True | 0.98× [0.97, 0.98] | 1 | 0.00 |
| fixed budget N=250 (single run) | 21.45 | 84 | | | | | |
| fixed budget N=500 (single run) | 24.71 | 164 | | | | | |
| fixed budget N=1000 (single run) | 28.19 | 367 | | | | | |
| fixed budget N=2000 (single run) | 32.17 | 938 | | | | | |
| fixed budget N=4000 (single run) | 36.61 | 2538 | | | | | |

## TurboReg

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 3000 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| full | threshold | 1.01 | 0.00 | 4414 |
| full | mondrian | never stop early | 0.00 | 4414 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | full / threshold | full / threshold | 1.01 | 76.7 | 0.00 | 4390 |
| mondrian | full / mondrian | full / mondrian | λ per group = 1.01/1.01/1.01 | 76.7 | 0.00 | 4390 |

### TurboReg, v2_blind_hi test (2092 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 85.66 | 4468 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 85.66 | 4468 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 68.50 | 185 | | | | | |
| fixed budget N=500 (single run) | 73.66 | 319 | | | | | |
| fixed budget N=1000 (single run) | 78.20 | 654 | | | | | |
| fixed budget N=2000 (single run) | 81.98 | 1595 | | | | | |
| fixed budget N=4000 (single run) | 85.66 | 4468 | | | | | |

### TurboReg, v2_blind_lo test (908 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 40.20 | 4089 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 40.20 | 4089 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 23.57 | 146 | | | | | |
| fixed budget N=500 (single run) | 27.64 | 305 | | | | | |
| fixed budget N=1000 (single run) | 32.38 | 650 | | | | | |
| fixed budget N=2000 (single run) | 35.79 | 1591 | | | | | |
| fixed budget N=4000 (single run) | 40.20 | 4089 | | | | | |

### TurboReg, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 81.89 | 4686 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 81.89 | 4686 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 65.00 | 195 | | | | | |
| fixed budget N=500 (single run) | 69.32 | 341 | | | | | |
| fixed budget N=1000 (single run) | 74.00 | 685 | | | | | |
| fixed budget N=2000 (single run) | 78.31 | 1645 | | | | | |
| fixed budget N=4000 (single run) | 81.89 | 4686 | | | | | |

### TurboReg, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 36.55 | 4224 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 36.55 | 4224 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 21.56 | 146 | | | | | |
| fixed budget N=500 (single run) | 24.93 | 321 | | | | | |
| fixed budget N=1000 (single run) | 28.13 | 679 | | | | | |
| fixed budget N=2000 (single run) | 32.06 | 1592 | | | | | |
| fixed budget N=4000 (single run) | 36.55 | 4224 | | | | | |
