# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## SC²-PCR

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1331 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-4000 | giveup | 0.5, 0.15 | 0.60 | 594 |
| 250-4000 | threshold | 0.5 | 0.60 | 601 |
| 250-500-4000 | threshold | 0.6 | 0.60 | 628 |
| 250-500-4000 | giveup | 0.6, 0 | 0.60 | 628 |
| x4 | giveup | 0.6, 0.1 | 0.60 | 634 |
| 250-1000-4000 | giveup | 0.6, 0.1 | 0.60 | 634 |
| x4 | threshold | 0.6 | 0.60 | 638 |
| 250-1000-4000 | threshold | 0.6 | 0.60 | 638 |
| 500-4000 | giveup | 0.6, 0.15 | 0.60 | 682 |
| 250-500-4000 | mdp | 0 | 0.50 | 687 |
| 250-2000-4000 | giveup | 0.6, 0.15 | 0.60 | 698 |
| 500-4000 | threshold | 0.6 | 0.40 | 701 |
| 250-2000-4000 | threshold | 0.6 | 0.50 | 725 |
| 250-1000-2000-4000 | giveup | 0.6, 0.1 | 0.60 | 728 |
| x4 | mdp | 0 | 0.50 | 733 |
| 250-1000-4000 | mdp | 0 | 0.50 | 733 |
| 250-1000-2000-4000 | threshold | 0.6 | 0.60 | 736 |
| 500-4000 | mdp | 0 | 0.40 | 742 |
| 500-2000-4000 | giveup | 0.6, 0.1 | 0.60 | 744 |
| doubling | threshold | 0.6 | 0.60 | 755 |
| doubling | giveup | 0.6, 0 | 0.60 | 755 |
| 500-2000-4000 | threshold | 0.6 | 0.60 | 756 |
| 250-2000-4000 | mdp | 0 | 0.50 | 825 |
| 250-4000 | mdp | 0 | 0.40 | 825 |
| doubling | mdp | 0 | 0.50 | 867 |
| 250-1000-2000-4000 | mdp | 0 | 0.50 | 895 |
| 500-2000-4000 | mdp | 0 | 0.20 | 904 |
| 500-4000 | mondrian | λ per group = 0.8/0.99/0.5 | 0.00 | 1229 |
| x4 | mondrian | λ per group = 0.9/0.99/0.5 | 0.00 | 1291 |
| 250-1000-4000 | mondrian | λ per group = 0.9/0.99/0.5 | 0.00 | 1291 |
| 250-4000 | mondrian | λ per group = 0.9/0.99/0.5 | 0.00 | 1480 |
| 500-2000-4000 | mondrian | λ per group = 0.8/0.99/0.5 | 0.00 | 1485 |
| 250-500-4000 | mondrian | λ per group = 0.9/0.995/0.5 | 0.00 | 1493 |
| 250-2000-4000 | mondrian | λ per group = 0.9/0.99/0.5 | 0.00 | 1669 |
| doubling | mondrian | λ per group = 0.9/0.995/0.5 | 0.00 | 1806 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.9/0.995/0.5 | 0.00 | 1867 |
| full | threshold | 1.01 | 0.00 | 2719 |
| full | mondrian | never stop early | 0.00 | 2719 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-4000 / giveup | 250-4000 / giveup | 0.7, 0.15 | 74.2 | 0.53 | 637 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.7/1.01/1.01 | 74.6 | 0.08 | 1640 |

### SC²-PCR, fcgfown_3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / giveup | 91.68 | 483 | +0.86 [+1.42] | False | 5.59× [5.08, 6.22] | 0.0125 | 1.29 |
| mondrian: 500-4000 / mondrian | 92.17 | 2558 | +0.37 [+0.68] | True | 1.06× [1.04, 1.07] | 0.0703 | 0.43 |
| fixed budget N=250 (single run) | 86.81 | 76 | | | | | |
| fixed budget N=500 (single run) | 88.11 | 133 | | | | | |
| fixed budget N=1000 (single run) | 89.90 | 275 | | | | | |
| fixed budget N=2000 (single run) | 91.44 | 815 | | | | | |
| fixed budget N=4000 (single run) | 92.54 | 2701 | | | | | |

### SC²-PCR, fcgfown_3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / giveup | 57.22 | 1803 | +0.79 [+1.24] | True | 1.43× [1.39, 1.48] | 0.00661 | 1.07 |
| mondrian: 500-4000 / mondrian | 57.72 | 2290 | +0.28 [+0.56] | True | 1.13× [1.11, 1.15] | 0.227 | 0.45 |
| fixed budget N=250 (single run) | 44.08 | 71 | | | | | |
| fixed budget N=500 (single run) | 46.77 | 129 | | | | | |
| fixed budget N=1000 (single run) | 51.09 | 281 | | | | | |
| fixed budget N=2000 (single run) | 55.03 | 850 | | | | | |
| fixed budget N=4000 (single run) | 58.00 | 2585 | | | | | |

## TurboReg

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1331 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-4000 | giveup | 0.5, 0.15 | 0.60 | 1118 |
| 250-4000 | threshold | 0.5 | 0.60 | 1129 |
| 250-500-4000 | giveup | 0.6, 0.15 | 0.60 | 1176 |
| 250-500-4000 | threshold | 0.6 | 0.60 | 1187 |
| 500-4000 | giveup | 0.5, 0.15 | 0.60 | 1197 |
| 500-4000 | threshold | 0.5 | 0.50 | 1223 |
| x4 | giveup | 0.6, 0.1 | 0.60 | 1238 |
| 250-1000-4000 | giveup | 0.6, 0.1 | 0.60 | 1238 |
| x4 | threshold | 0.6 | 0.60 | 1250 |
| 250-1000-4000 | threshold | 0.6 | 0.60 | 1250 |
| 250-500-4000 | mdp | 0 | 0.50 | 1258 |
| 250-2000-4000 | giveup | 0.6, 0.15 | 0.60 | 1353 |
| x4 | mdp | 0 | 0.60 | 1369 |
| 250-1000-4000 | mdp | 0 | 0.60 | 1369 |
| 250-2000-4000 | threshold | 0.6 | 0.60 | 1376 |
| 500-2000-4000 | giveup | 0.6, 0.15 | 0.50 | 1398 |
| 250-1000-2000-4000 | giveup | 0.6, 0.1 | 0.60 | 1431 |
| 250-1000-2000-4000 | threshold | 0.6 | 0.60 | 1447 |
| 250-4000 | mdp | 0 | 0.40 | 1453 |
| 500-4000 | mdp | 0 | 0.30 | 1467 |
| 500-2000-4000 | threshold | 0.6 | 0.50 | 1469 |
| doubling | giveup | 0.6, 0.1 | 0.60 | 1519 |
| doubling | threshold | 0.6 | 0.60 | 1536 |
| 250-2000-4000 | mdp | 0 | 0.50 | 1591 |
| 250-1000-2000-4000 | mdp | 0 | 0.60 | 1683 |
| doubling | mdp | 0 | 0.50 | 1699 |
| 500-2000-4000 | mdp | 0 | 0.10 | 1820 |
| 500-4000 | mondrian | λ per group = 0.75/0.99/0.5 | 0.00 | 2192 |
| x4 | mondrian | λ per group = 0.9/0.99/0.5 | 0.00 | 2396 |
| 250-1000-4000 | mondrian | λ per group = 0.9/0.99/0.5 | 0.00 | 2396 |
| 250-4000 | mondrian | λ per group = 0.88/0.99/0.5 | 0.00 | 2568 |
| 250-500-4000 | mondrian | λ per group = 0.88/0.995/0.5 | 0.00 | 2603 |
| 500-2000-4000 | mondrian | λ per group = 0.8/0.99/0.5 | 0.00 | 2862 |
| doubling | mondrian | λ per group = 0.9/0.99/0.5 | 0.00 | 3004 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.9/0.99/0.5 | 0.00 | 3065 |
| 250-2000-4000 | mondrian | λ per group = 0.9/0.99/0.5 | 0.00 | 3113 |
| full | threshold | 1.01 | 0.00 | 4866 |
| full | mondrian | never stop early | 0.00 | 4866 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-4000 / giveup | 250-4000 / giveup | 0.7, 0.15 | 74.0 | 0.53 | 1258 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.7/1.01/1.01 | 74.5 | 0.08 | 3187 |

### TurboReg, fcgfown_3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / giveup | 91.87 | 1066 | +0.74 [+1.23] | False | 5.51× [5.00, 6.12] | 0.0169 | 1.05 |
| mondrian: 500-4000 / mondrian | 92.11 | 5620 | +0.49 [+0.86] | True | 1.05× [1.03, 1.06] | 0.0215 | 0.55 |
| fixed budget N=250 (single run) | 87.00 | 195 | | | | | |
| fixed budget N=500 (single run) | 88.11 | 323 | | | | | |
| fixed budget N=1000 (single run) | 89.71 | 678 | | | | | |
| fixed budget N=2000 (single run) | 91.44 | 1770 | | | | | |
| fixed budget N=4000 (single run) | 92.61 | 5877 | | | | | |

### TurboReg, fcgfown_3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / giveup | 57.72 | 3216 | +0.67 [+1.12] | True | 1.40× [1.36, 1.45] | 0.029 | 1.07 |
| mondrian: 500-4000 / mondrian | 58.23 | 4081 | +0.17 [+0.51] | True | 1.10× [1.08, 1.13] | 0.549 | 0.39 |
| fixed budget N=250 (single run) | 43.57 | 197 | | | | | |
| fixed budget N=500 (single run) | 46.72 | 334 | | | | | |
| fixed budget N=1000 (single run) | 51.38 | 681 | | | | | |
| fixed budget N=2000 (single run) | 55.14 | 1631 | | | | | |
| fixed budget N=4000 (single run) | 58.39 | 4509 | | | | | |
