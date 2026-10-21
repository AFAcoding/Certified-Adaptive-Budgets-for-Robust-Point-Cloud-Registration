# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## SC²-PCR

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1331 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-4000 | mdp | 0 | 0.50 | 1327 |
| 500-4000 | giveup | 0.7, 0.2 | 0.50 | 1327 |
| 500-4000 | threshold | 0.7 | 0.50 | 1330 |
| 250-500-4000 | giveup | 0.85, 0.15 | 0.60 | 1438 |
| 250-500-4000 | threshold | 0.85 | 0.60 | 1439 |
| x4 | threshold | 0.88 | 0.60 | 1502 |
| x4 | giveup | 0.88, 0 | 0.60 | 1502 |
| 250-1000-4000 | threshold | 0.88 | 0.60 | 1502 |
| 250-1000-4000 | giveup | 0.88, 0 | 0.60 | 1502 |
| 250-4000 | giveup | 0.8, 0.2 | 0.50 | 1538 |
| 250-4000 | threshold | 0.8 | 0.50 | 1538 |
| 250-500-4000 | mdp | 0 | 0.40 | 1608 |
| x4 | mdp | 0 | 0.30 | 1664 |
| 250-1000-4000 | mdp | 0 | 0.30 | 1664 |
| 500-2000-4000 | giveup | 0.85, 0.15 | 0.50 | 1672 |
| 500-2000-4000 | threshold | 0.85 | 0.40 | 1681 |
| 250-4000 | mdp | 0 | 0.20 | 1709 |
| 500-4000 | mondrian | λ per group = 0.5/0.92/0.98 | 0.00 | 1759 |
| 250-2000-4000 | giveup | 0.88, 0.15 | 0.50 | 1768 |
| 250-2000-4000 | threshold | 0.88 | 0.50 | 1775 |
| 250-1000-2000-4000 | giveup | 0.9, 0.15 | 0.60 | 1865 |
| 250-1000-2000-4000 | threshold | 0.9 | 0.50 | 1895 |
| doubling | giveup | 0.92, 0.1 | 0.60 | 2045 |
| doubling | threshold | 0.92 | 0.60 | 2050 |
| 500-2000-4000 | mondrian | λ per group = 0.85/0.96/0.99 | 0.00 | 2396 |
| 250-500-4000 | mondrian | λ per group = 0.8/0.94/1.01 | 0.00 | 2425 |
| full | threshold | 1.01 | 0.00 | 2463 |
| full | mondrian | never stop early | 0.00 | 2463 |
| 250-4000 | mondrian | λ per group = 0.5/0.93/1.01 | 0.00 | 2496 |
| x4 | mondrian | λ per group = 0.88/0.95/1.01 | 0.00 | 2601 |
| 250-1000-4000 | mondrian | λ per group = 0.88/0.95/1.01 | 0.00 | 2601 |
| 250-2000-4000 | mondrian | λ per group = 0.75/0.95/1.01 | 0.00 | 2984 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.9/0.97/1.01 | 0.00 | 3393 |
| 250-2000-4000 | mdp | -1 | 0.00 | 3401 |
| doubling | mondrian | λ per group = 0.92/0.96/1.01 | 0.00 | 3477 |
| 500-2000-4000 | mdp | -1 | 0.00 | 3484 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 3763 |
| doubling | mdp | -1 | 0.00 | 3899 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-4000 / mdp | 500-4000 / mdp | 0 | 71.3 | 0.45 | 900 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.5/0.9/0.97 | 71.5 | 0.08 | 1098 |

### SC²-PCR, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / mdp | 80.53 | 1411 | +0.99 [+1.42] | False | 1.96× [1.86, 2.06] | 0.000402 | 1.11 |
| mondrian: 500-4000 / mondrian | 81.27 | 1795 | +0.25 [+0.43] | True | 1.54× [1.48, 1.60] | 0.125 | 0.25 |
| fixed budget N=250 (single run) | 50.83 | 55 | | | | | |
| fixed budget N=500 (single run) | 61.31 | 143 | | | | | |
| fixed budget N=1000 (single run) | 70.18 | 375 | | | | | |
| fixed budget N=2000 (single run) | 77.08 | 965 | | | | | |
| fixed budget N=4000 (single run) | 81.52 | 2762 | | | | | |

### SC²-PCR, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / mdp | 36.27 | 2379 | +0.34 [+0.56] | True | 1.04× [1.02, 1.05] | 0.0312 | 0.34 |
| mondrian: 500-4000 / mondrian | 36.50 | 2524 | +0.11 [+0.28] | True | 0.98× [0.97, 0.99] | 0.5 | 0.11 |
| fixed budget N=250 (single run) | 13.31 | 60 | | | | | |
| fixed budget N=500 (single run) | 19.03 | 152 | | | | | |
| fixed budget N=1000 (single run) | 25.44 | 378 | | | | | |
| fixed budget N=2000 (single run) | 32.00 | 933 | | | | | |
| fixed budget N=4000 (single run) | 36.61 | 2470 | | | | | |

## TurboReg

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1331 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-500-4000 | giveup | 0.7, 0.2 | 0.60 | 2059 |
| 250-500-4000 | threshold | 0.7 | 0.50 | 2071 |
| 500-4000 | mdp | 0 | 0.60 | 2094 |
| 500-4000 | threshold | 0.7 | 0.50 | 2122 |
| 500-4000 | giveup | 0.7, 0 | 0.50 | 2122 |
| 250-2000-4000 | giveup | 0.7, 0.15 | 0.60 | 2323 |
| 250-2000-4000 | threshold | 0.7 | 0.60 | 2340 |
| x4 | giveup | 0.88, 0.2 | 0.50 | 2382 |
| 250-1000-4000 | giveup | 0.88, 0.2 | 0.50 | 2382 |
| x4 | threshold | 0.88 | 0.40 | 2399 |
| 250-1000-4000 | threshold | 0.88 | 0.40 | 2399 |
| 250-4000 | giveup | 0.6, 0.3 | 0.60 | 2405 |
| 500-2000-4000 | giveup | 0.8, 0.2 | 0.60 | 2414 |
| 250-4000 | threshold | 0.6 | 0.50 | 2421 |
| 500-2000-4000 | threshold | 0.8 | 0.40 | 2454 |
| 250-500-4000 | mdp | 0 | 0.10 | 2520 |
| 250-4000 | mdp | 0 | 0.20 | 2675 |
| doubling | giveup | 0.85, 0.15 | 0.50 | 2711 |
| doubling | threshold | 0.85 | 0.40 | 2735 |
| 250-1000-2000-4000 | giveup | 0.88, 0.15 | 0.50 | 2873 |
| 250-1000-2000-4000 | threshold | 0.88 | 0.40 | 2903 |
| 500-4000 | mondrian | λ per group = 0.5/0.94/0.99 | 0.00 | 3157 |
| 500-2000-4000 | mondrian | λ per group = 0.8/0.94/0.99 | 0.00 | 3627 |
| 250-500-4000 | mondrian | λ per group = 0.8/0.95/1.01 | 0.00 | 3976 |
| 250-4000 | mondrian | λ per group = 0.5/0.92/1.01 | 0.00 | 4151 |
| full | threshold | 1.01 | 0.00 | 4195 |
| full | mondrian | never stop early | 0.00 | 4195 |
| x4 | mondrian | λ per group = 0.88/0.98/1.01 | 0.00 | 4369 |
| 250-1000-4000 | mondrian | λ per group = 0.88/0.98/1.01 | 0.00 | 4369 |
| x4 | mdp | -1 | 0.00 | 4737 |
| 250-1000-4000 | mdp | -1 | 0.00 | 4737 |
| 250-2000-4000 | mondrian | λ per group = 0.8/0.94/1.01 | 0.00 | 4967 |
| doubling | mondrian | λ per group = 0.85/0.97/1.01 | 0.00 | 5534 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.88/0.98/1.01 | 0.00 | 5580 |
| 250-2000-4000 | mdp | -1 | 0.00 | 5661 |
| 500-2000-4000 | mdp | -1 | 0.00 | 5767 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 6181 |
| doubling | mdp | -1 | 0.00 | 6309 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-500-4000 / giveup | 250-500-4000 / giveup | 0.8, 0.2 | 72.0 | 0.45 | 1503 |
| mondrian | 500-4000 / mondrian | 500-4000 / mondrian | λ per group = 0.5/0.88/0.98 | 72.4 | 0.08 | 1809 |

### TurboReg, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 80.16 | 2270 | +1.73 [+2.28] | False | 2.02× [1.92, 2.13] | 5.77e-08 | 1.79 |
| mondrian: 500-4000 / mondrian | 81.58 | 2905 | +0.31 [+0.55] | True | 1.58× [1.52, 1.64] | 0.0625 | 0.31 |
| fixed budget N=250 (single run) | 49.04 | 26 | | | | | |
| fixed budget N=500 (single run) | 60.01 | 140 | | | | | |
| fixed budget N=1000 (single run) | 69.25 | 548 | | | | | |
| fixed budget N=2000 (single run) | 76.59 | 1582 | | | | | |
| fixed budget N=4000 (single run) | 81.89 | 4590 | | | | | |

### TurboReg, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 36.16 | 3819 | +0.39 [+0.67] | True | 1.07× [1.06, 1.09] | 0.0654 | 0.51 |
| mondrian: 500-4000 / mondrian | 36.38 | 4011 | +0.17 [+0.34] | True | 1.02× [1.01, 1.03] | 0.25 | 0.17 |
| fixed budget N=250 (single run) | 13.87 | 11 | | | | | |
| fixed budget N=500 (single run) | 19.03 | 81 | | | | | |
| fixed budget N=1000 (single run) | 25.21 | 469 | | | | | |
| fixed budget N=2000 (single run) | 31.44 | 1517 | | | | | |
| fixed budget N=4000 (single run) | 36.55 | 4100 | | | | | |
