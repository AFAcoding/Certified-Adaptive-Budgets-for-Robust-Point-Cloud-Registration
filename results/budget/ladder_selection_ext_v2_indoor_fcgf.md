# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## SC²-PCR

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1331 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-500-4000 | mdp | 0 | 0.60 | 649 |
| 500-4000 | giveup | 0.6, 0.1 | 0.60 | 654 |
| 500-4000 | threshold | 0.6 | 0.60 | 663 |
| 500-2000-4000 | giveup | 0.6, 0.1 | 0.60 | 681 |
| 500-2000-4000 | threshold | 0.6 | 0.50 | 705 |
| x4 | threshold | 0.75 | 0.60 | 720 |
| x4 | giveup | 0.75, 0 | 0.60 | 720 |
| 250-1000-4000 | threshold | 0.75 | 0.60 | 720 |
| 250-1000-4000 | giveup | 0.75, 0 | 0.60 | 720 |
| 500-4000 | mdp | 0 | 0.30 | 736 |
| 250-500-4000 | threshold | 0.8 | 0.60 | 765 |
| 250-500-4000 | giveup | 0.8, 0 | 0.60 | 765 |
| 250-4000 | threshold | 0.75 | 0.60 | 778 |
| 250-4000 | giveup | 0.75, 0 | 0.60 | 778 |
| 250-2000-4000 | threshold | 0.75 | 0.60 | 823 |
| 250-2000-4000 | giveup | 0.75, 0 | 0.60 | 823 |
| 250-1000-2000-4000 | threshold | 0.75 | 0.60 | 878 |
| 250-1000-2000-4000 | giveup | 0.75, 0 | 0.60 | 878 |
| x4 | mdp | 0 | 0.30 | 998 |
| 250-1000-4000 | mdp | 0 | 0.30 | 998 |
| 500-2000-4000 | mdp | 0 | 0.30 | 1058 |
| doubling | threshold | 0.85 | 0.60 | 1090 |
| doubling | giveup | 0.85, 0 | 0.60 | 1090 |
| 250-1000-2000-4000 | mdp | 0 | 0.40 | 1201 |
| 500-4000 | mondrian | λ per group = 0.8/0.99/0.5 | 0.00 | 1233 |
| 250-2000-4000 | mdp | 0 | 0.50 | 1318 |
| 500-2000-4000 | mondrian | λ per group = 0.85/0.99/0.5 | 0.00 | 1468 |
| 250-4000 | mondrian | λ per group = 0.9/1.01/0.5 | 0.00 | 1803 |
| 250-500-4000 | mondrian | λ per group = 0.93/1.01/0.5 | 0.00 | 1881 |
| x4 | mondrian | λ per group = 0.94/1.01/0.5 | 0.00 | 2024 |
| 250-1000-4000 | mondrian | λ per group = 0.94/1.01/0.5 | 0.00 | 2024 |
| 250-2000-4000 | mondrian | λ per group = 0.93/1.01/0.5 | 0.00 | 2358 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.95/1.01/0.5 | 0.00 | 2614 |
| doubling | mondrian | λ per group = 0.96/1.01/0.5 | 0.00 | 2696 |
| full | threshold | 1.01 | 0.00 | 2719 |
| full | mondrian | never stop early | 0.00 | 2719 |
| 250-4000 | mdp | -1 | 0.00 | 2760 |
| doubling | mdp | -1 | 0.00 | 4099 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-500-4000 / mdp | full / threshold (fallback) | 1.01 | 74.6 | 0.00 | 1793 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.8/1.01/1.01 | 74.6 | 0.15 | 1699 |

### SC²-PCR, fcgfown_3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 92.54 | 2701 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: 500-4000 / mondrian | 92.48 | 2615 | +0.06 [+0.37] | True | 1.03× [1.02, 1.05] | 1 | 0.31 |
| fixed budget N=250 (single run) | 85.09 | 40 | | | | | |
| fixed budget N=500 (single run) | 88.60 | 118 | | | | | |
| fixed budget N=1000 (single run) | 90.82 | 329 | | | | | |
| fixed budget N=2000 (single run) | 92.11 | 887 | | | | | |
| fixed budget N=4000 (single run) | 92.54 | 2701 | | | | | |

### SC²-PCR, fcgfown_3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 58.00 | 2585 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: 500-4000 / mondrian | 57.66 | 2408 | +0.34 [+0.62] | True | 1.07× [1.06, 1.09] | 0.109 | 0.45 |
| fixed budget N=250 (single run) | 39.75 | 51 | | | | | |
| fixed budget N=500 (single run) | 46.72 | 136 | | | | | |
| fixed budget N=1000 (single run) | 53.06 | 348 | | | | | |
| fixed budget N=2000 (single run) | 57.05 | 905 | | | | | |
| fixed budget N=4000 (single run) | 58.00 | 2585 | | | | | |

## TurboReg

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1331 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-4000 | giveup | 0.5, 0.15 | 0.60 | 1099 |
| 500-4000 | threshold | 0.5 | 0.40 | 1144 |
| 500-2000-4000 | giveup | 0.5, 0.05 | 0.60 | 1182 |
| 500-2000-4000 | threshold | 0.5 | 0.60 | 1189 |
| 500-4000 | mdp | 0 | 0.10 | 1317 |
| 250-500-4000 | threshold | 0.8 | 0.60 | 1368 |
| 250-500-4000 | giveup | 0.8, 0 | 0.60 | 1368 |
| x4 | threshold | 0.8 | 0.60 | 1445 |
| x4 | giveup | 0.8, 0 | 0.60 | 1445 |
| 250-1000-4000 | threshold | 0.8 | 0.60 | 1445 |
| 250-1000-4000 | giveup | 0.8, 0 | 0.60 | 1445 |
| 250-4000 | threshold | 0.8 | 0.60 | 1505 |
| 250-4000 | giveup | 0.8, 0 | 0.60 | 1505 |
| 500-2000-4000 | mdp | 0 | 0.20 | 1556 |
| doubling | mdp | 0 | 0.50 | 1641 |
| 500-4000 | mondrian | λ per group = 0.7/0.98/0.5 | 0.00 | 1689 |
| 250-2000-4000 | threshold | 0.8 | 0.60 | 1704 |
| 250-2000-4000 | giveup | 0.8, 0 | 0.60 | 1704 |
| 250-1000-2000-4000 | threshold | 0.8 | 0.60 | 1782 |
| 250-1000-2000-4000 | giveup | 0.8, 0 | 0.60 | 1782 |
| doubling | threshold | 0.8 | 0.60 | 1787 |
| doubling | giveup | 0.8, 0 | 0.60 | 1787 |
| 250-2000-4000 | mdp | 0 | 0.60 | 2139 |
| 500-2000-4000 | mondrian | λ per group = 0.8/0.99/0.5 | 0.00 | 2383 |
| 250-4000 | mondrian | λ per group = 0.94/1.01/0.5 | 0.00 | 3249 |
| 250-500-4000 | mondrian | λ per group = 0.96/1.01/0.5 | 0.00 | 3423 |
| x4 | mondrian | λ per group = 0.96/1.01/0.5 | 0.00 | 3673 |
| 250-1000-4000 | mondrian | λ per group = 0.96/1.01/0.5 | 0.00 | 3673 |
| 250-2000-4000 | mondrian | λ per group = 0.96/1.01/0.5 | 0.00 | 4288 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.97/1.01/0.5 | 0.00 | 4704 |
| doubling | mondrian | λ per group = 0.97/1.01/0.5 | 0.00 | 4851 |
| full | threshold | 1.01 | 0.00 | 4866 |
| full | mondrian | never stop early | 0.00 | 4866 |
| 250-4000 | mdp | -1 | 0.00 | 4988 |
| 250-500-4000 | mdp | -1 | 0.00 | 5266 |
| x4 | mdp | -1 | 0.00 | 5635 |
| 250-1000-4000 | mdp | -1 | 0.00 | 5635 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 7232 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-4000 / giveup | 500-4000 / giveup | 0.8, 0.15 | 74.2 | 0.53 | 1416 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.9/1.01/1.01 | 74.5 | 0.15 | 3383 |

### TurboReg, fcgfown_3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 91.81 | 1252 | +0.80 [+1.29] | False | 4.69× [4.31, 5.14] | 0.0072 | 1.05 |
| mondrian: 500-4000 / mondrian | 92.61 | 5941 | +0.00 [+0.12] | True | 0.99× [0.98, 1.00] | 1 | 0.06 |
| fixed budget N=250 (single run) | 84.66 | 117 | | | | | |
| fixed budget N=500 (single run) | 88.05 | 273 | | | | | |
| fixed budget N=1000 (single run) | 90.94 | 630 | | | | | |
| fixed budget N=2000 (single run) | 91.87 | 1711 | | | | | |
| fixed budget N=4000 (single run) | 92.61 | 5877 | | | | | |

### TurboReg, fcgfown_3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 57.33 | 3393 | +1.07 [+1.57] | True | 1.33× [1.29, 1.37] | 0.000546 | 1.35 |
| mondrian: 500-4000 / mondrian | 58.28 | 4434 | +0.11 [+0.28] | True | 1.02× [1.01, 1.03] | 0.5 | 0.11 |
| fixed budget N=250 (single run) | 38.29 | 46 | | | | | |
| fixed budget N=500 (single run) | 44.92 | 213 | | | | | |
| fixed budget N=1000 (single run) | 53.06 | 628 | | | | | |
| fixed budget N=2000 (single run) | 55.98 | 1586 | | | | | |
| fixed budget N=4000 (single run) | 58.39 | 4509 | | | | | |
