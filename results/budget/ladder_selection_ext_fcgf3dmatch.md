# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## SC²-PCR

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1701 calibration pairs (cheapest first):

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
| marginal | 500-4000 / mdp | full / threshold (fallback) | 1.01 | 75.1 | 0.00 | 2806 |
| mondrian | 500-4000 / mondrian | full / mondrian (fallback) | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 2806 |

### SC²-PCR, fcgf_3DMatch test (812 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 92.36 | 2647 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 92.36 | 2647 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 85.71 | 59 | | | | | |
| fixed budget N=500 (single run) | 88.92 | 152 | | | | | |
| fixed budget N=1000 (single run) | 90.52 | 369 | | | | | |
| fixed budget N=2000 (single run) | 91.63 | 917 | | | | | |
| fixed budget N=4000 (single run) | 92.36 | 2647 | | | | | |

### SC²-PCR, fcgf_3DLoMatch test (891 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 57.35 | 2289 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 57.35 | 2289 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 39.84 | 84 | | | | | |
| fixed budget N=500 (single run) | 46.46 | 184 | | | | | |
| fixed budget N=1000 (single run) | 52.53 | 406 | | | | | |
| fixed budget N=2000 (single run) | 56.68 | 884 | | | | | |
| fixed budget N=4000 (single run) | 57.35 | 2289 | | | | | |

## TurboReg

Step 1, fitting pairs (1000, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1701 calibration pairs (cheapest first):

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
| marginal | 250-500-4000 / giveup | 250-500-4000 / giveup | 1.01, 0.2 | 75.1 | 0.00 | 5252 |
| mondrian | 500-4000 / mondrian | full / mondrian (fallback) | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 4902 |

### TurboReg, fcgf_3DMatch test (812 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 92.12 | 5562 | +0.00 [+0.00] | True | 0.93× [0.93, 0.93] | 1 | 0.00 |
| mondrian: full / mondrian | 92.12 | 5155 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 84.98 | 124 | | | | | |
| fixed budget N=500 (single run) | 88.30 | 284 | | | | | |
| fixed budget N=1000 (single run) | 90.64 | 629 | | | | | |
| fixed budget N=2000 (single run) | 91.26 | 1620 | | | | | |
| fixed budget N=4000 (single run) | 92.12 | 5155 | | | | | |

### TurboReg, fcgf_3DLoMatch test (891 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / giveup | 58.02 | 4946 | +0.00 [+0.00] | True | 0.95× [0.95, 0.95] | 1 | 0.00 |
| mondrian: full / mondrian | 58.02 | 4695 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 38.61 | 49 | | | | | |
| fixed budget N=500 (single run) | 45.34 | 202 | | | | | |
| fixed budget N=1000 (single run) | 52.86 | 593 | | | | | |
| fixed budget N=2000 (single run) | 55.67 | 1536 | | | | | |
| fixed budget N=4000 (single run) | 58.02 | 4695 | | | | | |
