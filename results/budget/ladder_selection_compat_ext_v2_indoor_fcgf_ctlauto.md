# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## SC²-PCR

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1331 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-4000 | threshold | 0.5 | 0.60 | 600 |
| 250-4000 | giveup | 0.5, 0 | 0.60 | 600 |
| x4 | giveup | 0.6, 0.15 | 0.60 | 612 |
| 250-1000-4000 | giveup | 0.6, 0.15 | 0.60 | 612 |
| x4 | threshold | 0.6 | 0.60 | 614 |
| 250-1000-4000 | threshold | 0.6 | 0.60 | 614 |
| 250-500-4000 | giveup | 0.6, 0.2 | 0.60 | 617 |
| 500-2000-4000 | giveup | 0.5, 0.15 | 0.60 | 629 |
| 250-500-4000 | threshold | 0.6 | 0.50 | 633 |
| 500-2000-4000 | threshold | 0.5 | 0.60 | 636 |
| 500-4000 | giveup | 0.5, 0.15 | 0.60 | 642 |
| 500-4000 | threshold | 0.5 | 0.60 | 643 |
| 250-500-4000 | mdp | 0 | 0.50 | 668 |
| 250-2000-4000 | giveup | 0.6, 0.15 | 0.40 | 693 |
| 250-2000-4000 | threshold | 0.6 | 0.40 | 699 |
| x4 | mdp | 0 | 0.50 | 709 |
| 250-1000-4000 | mdp | 0 | 0.50 | 709 |
| 250-1000-2000-4000 | giveup | 0.7, 0.15 | 0.60 | 766 |
| 250-1000-2000-4000 | threshold | 0.7 | 0.50 | 777 |
| 500-4000 | mdp | 0 | 0.30 | 807 |
| 250-1000-2000-4000 | mdp | 0 | 0.50 | 808 |
| doubling | mdp | 0 | 0.50 | 810 |
| doubling | giveup | 0.7, 0.15 | 0.50 | 814 |
| doubling | threshold | 0.7 | 0.50 | 819 |
| 250-2000-4000 | mdp | 0 | 0.40 | 832 |
| 250-4000 | mdp | 0 | 0.30 | 858 |
| 500-2000-4000 | mdp | 0 | 0.30 | 881 |
| 500-4000 | mondrian | λ per group = 0.85/0.98/0.5 | 0.00 | 1175 |
| 500-2000-4000 | mondrian | λ per group = 0.8/0.98/0.5 | 0.00 | 1324 |
| x4 | mondrian | λ per group = 0.88/0.995/0.5 | 0.00 | 1615 |
| 250-1000-4000 | mondrian | λ per group = 0.88/0.995/0.5 | 0.00 | 1615 |
| 250-4000 | mondrian | λ per group = 0.88/0.99/0.5 | 0.00 | 1629 |
| 250-500-4000 | mondrian | λ per group = 0.88/0.995/0.5 | 0.00 | 1725 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.88/0.995/0.5 | 0.00 | 1875 |
| doubling | mondrian | λ per group = 0.88/0.995/0.5 | 0.00 | 2002 |
| 250-2000-4000 | mondrian | λ per group = 0.88/0.995/0.5 | 0.00 | 2053 |
| full | threshold | 1.01 | 0.00 | 2719 |
| full | mondrian | never stop early | 0.00 | 2719 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-4000 / threshold | 250-4000 / threshold | 0.75 | 74.2 | 0.60 | 653 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.85/1.01/1.01 | 74.5 | 0.15 | 1732 |

### SC²-PCR, fcgfown_3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / threshold | 91.74 | 496 | +0.80 [+1.29] | False | 5.44× [4.95, 6.06] | 0.0192 | 1.23 |
| mondrian: 500-4000 / mondrian | 92.24 | 2646 | +0.31 [+0.55] | True | 1.02× [1.01, 1.03] | 0.0625 | 0.31 |
| fixed budget N=250 (single run) | 86.81 | 76 | | | | | |
| fixed budget N=500 (single run) | 88.11 | 133 | | | | | |
| fixed budget N=1000 (single run) | 89.90 | 275 | | | | | |
| fixed budget N=2000 (single run) | 91.44 | 815 | | | | | |
| fixed budget N=4000 (single run) | 92.54 | 2701 | | | | | |

### SC²-PCR, fcgfown_3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / threshold | 57.55 | 1836 | +0.45 [+0.84] | True | 1.41× [1.37, 1.45] | 0.115 | 0.79 |
| mondrian: 500-4000 / mondrian | 57.94 | 2447 | +0.06 [+0.28] | True | 1.06× [1.04, 1.07] | 1 | 0.17 |
| fixed budget N=250 (single run) | 44.08 | 71 | | | | | |
| fixed budget N=500 (single run) | 46.77 | 129 | | | | | |
| fixed budget N=1000 (single run) | 51.09 | 281 | | | | | |
| fixed budget N=2000 (single run) | 55.03 | 850 | | | | | |
| fixed budget N=4000 (single run) | 58.00 | 2585 | | | | | |

## TurboReg

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1331 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-4000 | giveup | 0.6, 0.15 | 0.60 | 1165 |
| 250-500-4000 | threshold | 0.6 | 0.50 | 1178 |
| 250-500-4000 | giveup | 0.6, 0 | 0.50 | 1178 |
| 250-500-4000 | mdp | 0 | 0.60 | 1184 |
| x4 | threshold | 0.6 | 0.60 | 1195 |
| x4 | giveup | 0.6, 0 | 0.60 | 1195 |
| 250-1000-4000 | threshold | 0.6 | 0.60 | 1195 |
| 250-1000-4000 | giveup | 0.6, 0 | 0.60 | 1195 |
| 250-4000 | threshold | 0.6 | 0.40 | 1217 |
| 250-4000 | mdp | 0 | 0.30 | 1247 |
| x4 | mdp | 0 | 0.60 | 1267 |
| 250-1000-4000 | mdp | 0 | 0.60 | 1267 |
| 500-4000 | giveup | 0.6, 0.15 | 0.60 | 1281 |
| 250-2000-4000 | giveup | 0.6, 0.05 | 0.60 | 1304 |
| 250-2000-4000 | threshold | 0.6 | 0.60 | 1309 |
| 500-4000 | threshold | 0.6 | 0.40 | 1310 |
| 500-4000 | mdp | 0 | 0.30 | 1356 |
| 250-2000-4000 | mdp | 0 | 0.50 | 1462 |
| 500-2000-4000 | mdp | 0 | 0.60 | 1529 |
| 250-1000-2000-4000 | threshold | 0.7 | 0.50 | 1566 |
| 250-1000-2000-4000 | giveup | 0.7, 0 | 0.50 | 1566 |
| 500-2000-4000 | giveup | 0.7, 0.1 | 0.50 | 1574 |
| 500-2000-4000 | threshold | 0.7 | 0.40 | 1600 |
| doubling | giveup | 0.7, 0.05 | 0.60 | 1621 |
| doubling | threshold | 0.7 | 0.50 | 1629 |
| 500-4000 | mondrian | λ per group = 0.7/0.98/0.5 | 0.00 | 1691 |
| 500-2000-4000 | mondrian | λ per group = 0.8/0.995/0.5 | 0.00 | 2358 |
| 250-4000 | mondrian | λ per group = 0.88/1.01/0.5 | 0.00 | 3045 |
| 250-500-4000 | mondrian | λ per group = 0.9/1.01/0.5 | 0.00 | 3183 |
| x4 | mondrian | λ per group = 0.94/1.01/0.5 | 0.00 | 3462 |
| 250-1000-4000 | mondrian | λ per group = 0.94/1.01/0.5 | 0.00 | 3462 |
| 250-2000-4000 | mondrian | λ per group = 0.8/1.01/0.5 | 0.00 | 3830 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.8/1.01/0.5 | 0.00 | 4154 |
| doubling | mondrian | λ per group = 0.93/1.01/0.5 | 0.00 | 4574 |
| full | threshold | 1.01 | 0.00 | 4866 |
| full | mondrian | never stop early | 0.00 | 4866 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 7340 |
| doubling | mdp | -1 | 0.00 | 7640 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-4000 / giveup | full / threshold (fallback) | 1.01 | 74.5 | 0.00 | 3369 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.75/1.01/1.01 | 74.4 | 0.15 | 3220 |

### TurboReg, fcgfown_3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 92.61 | 5877 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: 500-4000 / mondrian | 92.05 | 5635 | +0.55 [+0.99] | True | 1.04× [1.03, 1.06] | 0.0352 | 0.74 |
| fixed budget N=250 (single run) | 87.00 | 195 | | | | | |
| fixed budget N=500 (single run) | 88.11 | 323 | | | | | |
| fixed budget N=1000 (single run) | 89.71 | 678 | | | | | |
| fixed budget N=2000 (single run) | 91.44 | 1770 | | | | | |
| fixed budget N=4000 (single run) | 92.61 | 5877 | | | | | |

### TurboReg, fcgfown_3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 58.39 | 4509 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: 500-4000 / mondrian | 58.34 | 4105 | +0.06 [+0.39] | True | 1.10× [1.08, 1.12] | 1 | 0.34 |
| fixed budget N=250 (single run) | 43.57 | 197 | | | | | |
| fixed budget N=500 (single run) | 46.72 | 334 | | | | | |
| fixed budget N=1000 (single run) | 51.38 | 681 | | | | | |
| fixed budget N=2000 (single run) | 55.14 | 1631 | | | | | |
| fixed budget N=4000 (single run) | 58.39 | 4509 | | | | | |
