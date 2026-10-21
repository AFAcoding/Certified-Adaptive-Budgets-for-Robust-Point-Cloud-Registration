# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## SC²-PCR

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1331 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-4000 | threshold | 0.75 | 0.60 | 778 |
| 250-4000 | giveup | 0.75, 0 | 0.60 | 778 |
| 250-4000 | mondrian | λ per group = 0.9/1.01/0.5 | 0.00 | 1803 |
| full | threshold | 1.01 | 0.00 | 2719 |
| full | mondrian | never stop early | 0.00 | 2719 |
| 250-4000 | mdp | -1 | 0.00 | 2760 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-4000 / threshold | 250-4000 / threshold | 0.75 | 74.2 | 0.53 | 703 |
| mondrian | 250-4000 / mondrian | 250-4000 / mondrian | λ per group = 0.88/1.01/1.01 | 74.5 | 0.15 | 1750 |

### SC²-PCR, fcgfown_3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / threshold | 92.17 | 555 | +0.37 [+0.80] | True | 4.87× [4.43, 5.37] | 0.238 | 0.74 |
| mondrian: 250-4000 / mondrian | 92.48 | 2704 | +0.06 [+0.18] | True | 1.00× [0.99, 1.00] | 1 | 0.06 |
| fixed budget N=250 (single run) | 85.09 | 40 | | | | | |
| fixed budget N=500 (single run) | 88.60 | 118 | | | | | |
| fixed budget N=1000 (single run) | 90.82 | 329 | | | | | |
| fixed budget N=2000 (single run) | 92.11 | 887 | | | | | |
| fixed budget N=4000 (single run) | 92.54 | 2701 | | | | | |

### SC²-PCR, fcgfown_3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / threshold | 57.27 | 1989 | +0.73 [+1.18] | True | 1.30× [1.27, 1.33] | 0.0106 | 1.01 |
| mondrian: 250-4000 / mondrian | 57.94 | 2547 | +0.06 [+0.17] | True | 1.02× [1.01, 1.02] | 1 | 0.06 |
| fixed budget N=250 (single run) | 39.75 | 51 | | | | | |
| fixed budget N=500 (single run) | 46.72 | 136 | | | | | |
| fixed budget N=1000 (single run) | 53.06 | 348 | | | | | |
| fixed budget N=2000 (single run) | 57.05 | 905 | | | | | |
| fixed budget N=4000 (single run) | 58.00 | 2585 | | | | | |

## TurboReg

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1331 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-4000 | threshold | 0.8 | 0.60 | 1505 |
| 250-4000 | giveup | 0.8, 0 | 0.60 | 1505 |
| 250-4000 | mondrian | λ per group = 0.94/1.01/0.5 | 0.00 | 3249 |
| full | threshold | 1.01 | 0.00 | 4866 |
| full | mondrian | never stop early | 0.00 | 4866 |
| 250-4000 | mdp | -1 | 0.00 | 4988 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-4000 / threshold | 250-4000 / threshold | 0.6 | 74.3 | 0.60 | 1113 |
| mondrian | 250-4000 / mondrian | 250-4000 / mondrian | λ per group = 0.75/1.01/1.01 | 74.6 | 0.15 | 3135 |

### TurboReg, fcgfown_3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / threshold | 91.74 | 1006 | +0.86 [+1.42] | False | 5.84× [5.28, 6.49] | 0.0161 | 1.36 |
| mondrian: 250-4000 / mondrian | 92.36 | 5633 | +0.25 [+0.55] | True | 1.04× [1.03, 1.06] | 0.289 | 0.37 |
| fixed budget N=250 (single run) | 84.66 | 117 | | | | | |
| fixed budget N=500 (single run) | 88.05 | 273 | | | | | |
| fixed budget N=1000 (single run) | 90.94 | 630 | | | | | |
| fixed budget N=2000 (single run) | 91.87 | 1711 | | | | | |
| fixed budget N=4000 (single run) | 92.61 | 5877 | | | | | |

### TurboReg, fcgfown_3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / threshold | 57.38 | 3150 | +1.01 [+1.52] | True | 1.43× [1.39, 1.48] | 0.00143 | 1.35 |
| mondrian: 250-4000 / mondrian | 58.11 | 4115 | +0.28 [+0.56] | True | 1.10× [1.08, 1.11] | 0.18 | 0.39 |
| fixed budget N=250 (single run) | 38.29 | 46 | | | | | |
| fixed budget N=500 (single run) | 44.92 | 213 | | | | | |
| fixed budget N=1000 (single run) | 53.06 | 628 | | | | | |
| fixed budget N=2000 (single run) | 55.98 | 1586 | | | | | |
| fixed budget N=4000 (single run) | 58.39 | 4509 | | | | | |
