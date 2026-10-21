# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## SC²-PCR

Validation, certified operating points (cheapest first):

| ladder | policy | parameters | val RR % | val risk % | val mean time (ms) |
|---|---|---|---|---|---|
| 500-4000 | threshold | 0.75 | 75.8 | 0.55 | 1357 |
| 500-4000 | giveup | 0.8, 0 | 75.9 | 0.39 | 1427 |
| 250-500-4000 | threshold | 0.85 | 75.8 | 0.55 | 1455 |
| 250-4000 | threshold | 0.8 | 75.8 | 0.47 | 1456 |
| x4 | threshold | 0.85 | 75.8 | 0.47 | 1504 |
| 250-1000-4000 | threshold | 0.85 | 75.8 | 0.47 | 1504 |
| 250-4000 | giveup | 0.85, 0.15 | 75.8 | 0.39 | 1568 |
| 250-1000-2000-4000 | mdp | 0 | 75.9 | 0.47 | 1607 |
| 250-2000-4000 | threshold | 0.8 | 75.9 | 0.55 | 1628 |
| 500-2000-4000 | threshold | 0.8 | 76.1 | 0.39 | 1642 |
| 500-2000-4000 | giveup | 0.8, 0 | 76.1 | 0.39 | 1642 |
| x4 | giveup | 0.9, 0.1 | 75.8 | 0.39 | 1651 |
| 250-1000-4000 | giveup | 0.9, 0.1 | 75.8 | 0.39 | 1651 |
| 500-2000-4000 | mdp | 0 | 76.2 | 0.55 | 1698 |
| 250-500-4000 | giveup | 0.92, 0.1 | 75.8 | 0.39 | 1709 |
| 500-4000 | mondrian | λ per group = 0.6/0.9/0.97 | 76.2 | 0.00 | 1816 |
| 500-4000 | mdp | 0 | 76.1 | 0.16 | 1822 |
| 250-4000 | mdp | 0 | 75.9 | 0.16 | 1833 |
| 250-1000-2000-4000 | threshold | 0.85 | 75.8 | 0.47 | 1849 |
| doubling | threshold | 0.85 | 76.0 | 0.47 | 1913 |
| 250-4000 | mondrian | λ per group = 0.6/0.95/0.96 | 76.1 | 0.00 | 2014 |
| 250-1000-2000-4000 | giveup | 0.9, 0.1 | 75.8 | 0.39 | 2021 |
| 250-2000-4000 | giveup | 0.93, 0.15 | 75.8 | 0.39 | 2030 |
| 250-500-4000 | mondrian | λ per group = 0.7/0.96/0.97 | 76.1 | 0.00 | 2081 |
| x4 | mondrian | λ per group = 0.8/0.96/0.97 | 76.1 | 0.00 | 2169 |
| 250-1000-4000 | mondrian | λ per group = 0.8/0.96/0.97 | 76.1 | 0.00 | 2169 |
| 250-2000-4000 | mondrian | λ per group = 0.6/0.96/0.97 | 76.2 | 0.00 | 2278 |
| 500-2000-4000 | mondrian | λ per group = 0.7/0.95/0.97 | 76.2 | 0.00 | 2292 |
| doubling | giveup | 0.92, 0 | 75.8 | 0.39 | 2292 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.75/0.96/0.97 | 76.2 | 0.00 | 2556 |
| full | threshold | 0.5 | 76.0 | 0.00 | 2798 |
| full | giveup | 0.5, 0 | 76.0 | 0.00 | 2798 |
| full | mondrian | λ per group = 0.5/0.5/0.5 | 76.0 | 0.00 | 2798 |
| doubling | mondrian | λ per group = 0.75/0.97/0.98 | 76.0 | 0.00 | 2928 |
| 250-500-4000 | mdp | -1 | 76.0 | 0.00 | 2984 |
| x4 | mdp | -1 | 76.0 | 0.00 | 3205 |
| 250-1000-4000 | mdp | -1 | 76.0 | 0.00 | 3205 |
| 250-2000-4000 | mdp | -1 | 76.0 | 0.00 | 3767 |
| doubling | mdp | -1 | 76.0 | 0.00 | 4262 |

Selected on validation: marginal = `500-4000` / threshold; group-conditional = `500-4000` / mondrian.


### SC²-PCR, fcgf_3DMatch test (812 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 91.87 | 543 | +0.49 [+1.11] | False | 4.87× [4.35, 5.56] | 0.344 | 0.86 |
| mondrian: 500-4000 / mondrian | 92.36 | 1005 | +0.00 [+0.00] | True | 2.63× [2.42, 2.91] | 1 | 0.00 |
| fixed budget N=250 (single run) | 85.71 | 59 | | | | | |
| fixed budget N=500 (single run) | 88.92 | 152 | | | | | |
| fixed budget N=1000 (single run) | 90.52 | 369 | | | | | |
| fixed budget N=2000 (single run) | 91.63 | 917 | | | | | |
| fixed budget N=4000 (single run) | 92.36 | 2647 | | | | | |

### SC²-PCR, fcgf_3DLoMatch test (891 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 56.79 | 1836 | +0.56 [+1.01] | True | 1.25× [1.20, 1.30] | 0.125 | 0.67 |
| mondrian: 500-4000 / mondrian | 57.13 | 2143 | +0.22 [+0.56] | True | 1.07× [1.04, 1.10] | 0.5 | 0.22 |
| fixed budget N=250 (single run) | 39.84 | 84 | | | | | |
| fixed budget N=500 (single run) | 46.46 | 184 | | | | | |
| fixed budget N=1000 (single run) | 52.53 | 406 | | | | | |
| fixed budget N=2000 (single run) | 56.68 | 884 | | | | | |
| fixed budget N=4000 (single run) | 57.35 | 2289 | | | | | |

## TurboReg

Validation, certified operating points (cheapest first):

| ladder | policy | parameters | val RR % | val risk % | val mean time (ms) |
|---|---|---|---|---|---|
| 250-500-4000 | threshold | 0.75 | 75.8 | 0.55 | 2185 |
| 250-4000 | threshold | 0.7 | 75.9 | 0.47 | 2280 |
| x4 | threshold | 0.75 | 75.8 | 0.47 | 2325 |
| 250-1000-4000 | threshold | 0.75 | 75.8 | 0.47 | 2325 |
| 250-500-4000 | mdp | 0 | 75.7 | 0.55 | 2325 |
| 500-4000 | threshold | 0.75 | 75.7 | 0.55 | 2375 |
| 250-4000 | giveup | 0.75, 0 | 75.8 | 0.39 | 2395 |
| x4 | giveup | 0.8, 0.1 | 75.8 | 0.39 | 2473 |
| 250-1000-4000 | giveup | 0.8, 0.1 | 75.8 | 0.39 | 2473 |
| 250-500-4000 | giveup | 0.85, 0.1 | 75.8 | 0.31 | 2525 |
| 500-4000 | giveup | 0.8, 0.1 | 75.8 | 0.39 | 2561 |
| 250-2000-4000 | threshold | 0.75 | 75.8 | 0.47 | 2645 |
| 250-2000-4000 | mdp | 0 | 76.1 | 0.24 | 2697 |
| 250-2000-4000 | giveup | 0.8, 0 | 76.0 | 0.31 | 2810 |
| 250-1000-2000-4000 | mdp | 0 | 76.0 | 0.39 | 2814 |
| 500-2000-4000 | threshold | 0.8 | 75.8 | 0.39 | 2842 |
| 500-2000-4000 | giveup | 0.8, 0 | 75.8 | 0.39 | 2842 |
| 250-1000-2000-4000 | giveup | 0.8, 0.05 | 75.9 | 0.39 | 2982 |
| 250-1000-2000-4000 | threshold | 0.8 | 75.9 | 0.39 | 2987 |
| 500-2000-4000 | mdp | 0 | 76.2 | 0.24 | 3012 |
| doubling | giveup | 0.8, 0.05 | 75.9 | 0.39 | 3018 |
| doubling | threshold | 0.8 | 75.9 | 0.39 | 3022 |
| 250-4000 | mondrian | λ per group = 0.6/0.94/0.5 | 76.0 | 0.00 | 3123 |
| x4 | mondrian | λ per group = 0.7/0.94/0.5 | 76.0 | 0.00 | 3178 |
| 250-1000-4000 | mondrian | λ per group = 0.7/0.94/0.5 | 76.0 | 0.00 | 3178 |
| 250-500-4000 | mondrian | λ per group = 0.75/0.95/0.5 | 76.0 | 0.00 | 3192 |
| 250-4000 | mdp | 0 | 75.9 | 0.08 | 3193 |
| 250-2000-4000 | mondrian | λ per group = 0.7/0.94/0.5 | 76.1 | 0.00 | 3566 |
| 500-4000 | mondrian | λ per group = 0.6/0.94/0.97 | 76.0 | 0.00 | 3653 |
| 500-2000-4000 | mondrian | λ per group = 0.6/0.94/0.97 | 76.0 | 0.00 | 3802 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.8/0.95/0.5 | 76.0 | 0.00 | 4108 |
| doubling | mondrian | λ per group = 0.8/0.95/0.5 | 76.1 | 0.00 | 4237 |
| full | threshold | 0.5 | 75.9 | 0.00 | 4881 |
| full | giveup | 0.5, 0 | 75.9 | 0.00 | 4881 |
| full | mondrian | λ per group = 0.5/0.5/0.5 | 75.9 | 0.00 | 4881 |
| 500-4000 | mdp | -1 | 75.9 | 0.00 | 5144 |
| x4 | mdp | -1 | 75.9 | 0.00 | 5629 |
| 250-1000-4000 | mdp | -1 | 75.9 | 0.00 | 5629 |
| doubling | mdp | -1 | 75.9 | 0.00 | 7490 |

Selected on validation: marginal = `250-500-4000` / threshold; group-conditional = `250-4000` / mondrian.


### TurboReg, fcgf_3DMatch test (812 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / threshold | 91.38 | 899 | +0.74 [+1.35] | False | 5.74× [5.01, 6.72] | 0.0703 | 0.86 |
| mondrian: 250-4000 / mondrian | 91.87 | 1870 | +0.25 [+0.62] | True | 2.76× [2.52, 3.03] | 0.5 | 0.25 |
| fixed budget N=250 (single run) | 84.98 | 124 | | | | | |
| fixed budget N=500 (single run) | 88.30 | 284 | | | | | |
| fixed budget N=1000 (single run) | 90.64 | 629 | | | | | |
| fixed budget N=2000 (single run) | 91.26 | 1620 | | | | | |
| fixed budget N=4000 (single run) | 92.12 | 5155 | | | | | |

### TurboReg, fcgf_3DLoMatch test (891 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / threshold | 57.80 | 3496 | +0.22 [+0.67] | True | 1.34× [1.29, 1.40] | 0.688 | 0.45 |
| mondrian: 250-4000 / mondrian | 58.02 | 4287 | +0.00 [+0.22] | True | 1.10× [1.07, 1.12] | 1 | 0.11 |
| fixed budget N=250 (single run) | 38.61 | 49 | | | | | |
| fixed budget N=500 (single run) | 45.34 | 202 | | | | | |
| fixed budget N=1000 (single run) | 52.86 | 593 | | | | | |
| fixed budget N=2000 (single run) | 55.67 | 1536 | | | | | |
| fixed budget N=4000 (single run) | 58.02 | 4695 | | | | | |
