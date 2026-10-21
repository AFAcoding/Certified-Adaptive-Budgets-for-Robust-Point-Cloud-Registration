# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## SC²-PCR

Validation, certified operating points (cheapest first):

| ladder | policy | parameters | val RR % | val risk % | val mean time (ms) |
|---|---|---|---|---|---|
| 250-500-4000 | threshold | 0.88 | 76.0 | 0.47 | 1412 |
| 500-4000 | threshold | 0.85 | 75.9 | 0.47 | 1434 |
| 250-4000 | threshold | 0.9 | 75.9 | 0.47 | 1469 |
| 500-4000 | giveup | 0.88, 0.1 | 75.9 | 0.39 | 1489 |
| x4 | threshold | 0.88 | 75.9 | 0.47 | 1500 |
| 250-1000-4000 | threshold | 0.88 | 75.9 | 0.47 | 1500 |
| 250-500-4000 | giveup | 0.92, 0 | 75.9 | 0.39 | 1518 |
| 250-4000 | giveup | 0.93, 0.1 | 76.0 | 0.39 | 1555 |
| x4 | giveup | 0.92, 0 | 76.0 | 0.39 | 1618 |
| 250-1000-4000 | giveup | 0.92, 0 | 76.0 | 0.39 | 1618 |
| x4 | mdp | 0 | 76.1 | 0.16 | 1746 |
| 250-1000-4000 | mdp | 0 | 76.1 | 0.16 | 1746 |
| x4 | mondrian | λ per group = 0.8/0.95/0.98 | 76.2 | 0.00 | 1750 |
| 250-1000-4000 | mondrian | λ per group = 0.8/0.95/0.98 | 76.2 | 0.00 | 1750 |
| 500-2000-4000 | threshold | 0.85 | 75.8 | 0.55 | 1771 |
| 250-2000-4000 | threshold | 0.88 | 75.9 | 0.47 | 1775 |
| 500-2000-4000 | giveup | 0.88, 0.05 | 75.9 | 0.39 | 1872 |
| 250-1000-2000-4000 | threshold | 0.88 | 75.9 | 0.47 | 1877 |
| 500-4000 | mondrian | λ per group = 0.5/0.96/0.98 | 76.2 | 0.00 | 1903 |
| 250-2000-4000 | giveup | 0.92, 0 | 76.0 | 0.31 | 1935 |
| doubling | threshold | 0.9 | 75.8 | 0.55 | 1960 |
| doubling | giveup | 0.92, 0 | 75.9 | 0.39 | 2023 |
| 250-500-4000 | mondrian | λ per group = 0.6/0.97/0.99 | 76.1 | 0.00 | 2025 |
| 250-1000-2000-4000 | giveup | 0.92, 0.05 | 76.0 | 0.31 | 2037 |
| 250-4000 | mondrian | λ per group = 0.7/0.95/0.99 | 76.1 | 0.00 | 2049 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.88/0.95/0.98 | 76.2 | 0.00 | 2206 |
| 250-2000-4000 | mondrian | λ per group = 0.85/0.95/0.99 | 76.0 | 0.00 | 2376 |
| doubling | mondrian | λ per group = 0.88/0.96/0.99 | 76.2 | 0.00 | 2504 |
| 500-2000-4000 | mondrian | λ per group = 0.7/0.96/0.99 | 76.0 | 0.00 | 2639 |
| full | threshold | 0.5 | 76.0 | 0.00 | 2798 |
| full | giveup | 0.5, 0 | 76.0 | 0.00 | 2798 |
| full | mondrian | λ per group = 0.5/0.5/0.5 | 76.0 | 0.00 | 2798 |
| 250-4000 | mdp | -1 | 76.0 | 0.00 | 2879 |
| 500-4000 | mdp | -1 | 76.0 | 0.00 | 2940 |
| 250-500-4000 | mdp | -1 | 76.0 | 0.00 | 2981 |
| 250-2000-4000 | mdp | -1 | 76.0 | 0.00 | 3689 |
| 500-2000-4000 | mdp | -1 | 76.0 | 0.00 | 3751 |
| 250-1000-2000-4000 | mdp | -1 | 76.0 | 0.00 | 3945 |
| doubling | mdp | -1 | 76.0 | 0.00 | 4048 |

Selected on validation: marginal = `250-500-4000` / threshold; group-conditional = `x4` / mondrian.


### SC²-PCR, fcgf_3DMatch test (812 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / threshold | 91.50 | 561 | +0.86 [+1.48] | False | 4.72× [4.20, 5.43] | 0.0391 | 0.99 |
| mondrian: x4 / mondrian | 92.00 | 791 | +0.37 [+0.74] | True | 3.35× [3.01, 3.78] | 0.25 | 0.37 |
| fixed budget N=250 (single run) | 87.07 | 98 | | | | | |
| fixed budget N=500 (single run) | 88.30 | 155 | | | | | |
| fixed budget N=1000 (single run) | 90.15 | 303 | | | | | |
| fixed budget N=2000 (single run) | 91.50 | 828 | | | | | |
| fixed budget N=4000 (single run) | 92.36 | 2647 | | | | | |

### SC²-PCR, fcgf_3DLoMatch test (891 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-500-4000 / threshold | 57.01 | 1839 | +0.34 [+0.79] | True | 1.24× [1.20, 1.30] | 0.375 | 0.45 |
| mondrian: x4 / mondrian | 57.35 | 2202 | +0.00 [+0.00] | True | 1.04× [1.01, 1.07] | 1 | 0.00 |
| fixed budget N=250 (single run) | 44.56 | 89 | | | | | |
| fixed budget N=500 (single run) | 46.24 | 140 | | | | | |
| fixed budget N=1000 (single run) | 51.29 | 292 | | | | | |
| fixed budget N=2000 (single run) | 54.43 | 796 | | | | | |
| fixed budget N=4000 (single run) | 57.35 | 2289 | | | | | |

## TurboReg

Validation, certified operating points (cheapest first):

| ladder | policy | parameters | val RR % | val risk % | val mean time (ms) |
|---|---|---|---|---|---|
| 500-4000 | giveup | 0.85, 0.1 | 75.8 | 0.39 | 2551 |
| 500-4000 | threshold | 0.85 | 75.9 | 0.31 | 2592 |
| 250-4000 | threshold | 0.88 | 75.8 | 0.47 | 2601 |
| 250-500-4000 | threshold | 0.9 | 75.8 | 0.55 | 2696 |
| 250-4000 | giveup | 0.92, 0.1 | 76.0 | 0.24 | 2759 |
| x4 | threshold | 0.88 | 75.8 | 0.55 | 2792 |
| 250-1000-4000 | threshold | 0.88 | 75.8 | 0.55 | 2792 |
| 250-500-4000 | giveup | 0.92, 0 | 76.0 | 0.24 | 2810 |
| x4 | giveup | 0.93, 0.1 | 75.8 | 0.39 | 2981 |
| 250-1000-4000 | giveup | 0.93, 0.1 | 75.8 | 0.39 | 2981 |
| 500-2000-4000 | threshold | 0.85 | 75.8 | 0.47 | 3217 |
| 250-2000-4000 | threshold | 0.88 | 75.8 | 0.47 | 3255 |
| 500-2000-4000 | giveup | 0.88, 0 | 75.8 | 0.39 | 3391 |
| 500-4000 | mondrian | λ per group = 0.6/0.95/0.98 | 76.0 | 0.00 | 3461 |
| 250-2000-4000 | giveup | 0.92, 0.1 | 75.8 | 0.39 | 3463 |
| 250-1000-2000-4000 | threshold | 0.9 | 75.7 | 0.55 | 3587 |
| 250-4000 | mondrian | λ per group = 0.6/0.98/0.98 | 76.0 | 0.00 | 3608 |
| x4 | mondrian | λ per group = 0.6/0.98/0.98 | 76.0 | 0.00 | 3611 |
| 250-1000-4000 | mondrian | λ per group = 0.6/0.98/0.98 | 76.0 | 0.00 | 3611 |
| 250-1000-2000-4000 | giveup | 0.93, 0.1 | 75.8 | 0.39 | 3728 |
| doubling | threshold | 0.92 | 76.0 | 0.24 | 3886 |
| doubling | giveup | 0.92, 0 | 76.0 | 0.24 | 3886 |
| 250-2000-4000 | mondrian | λ per group = 0.75/0.97/0.97 | 76.0 | 0.00 | 4145 |
| 250-500-4000 | mondrian | λ per group = 0.6/0.99/0.99 | 76.0 | 0.00 | 4220 |
| 500-2000-4000 | mondrian | λ per group = 0.75/0.97/0.98 | 76.0 | 0.00 | 4502 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.75/0.98/0.98 | 76.0 | 0.00 | 4555 |
| doubling | mondrian | λ per group = 0.8/0.98/0.98 | 76.0 | 0.00 | 4860 |
| full | threshold | 0.5 | 75.9 | 0.00 | 4881 |
| full | giveup | 0.5, 0 | 75.9 | 0.00 | 4881 |
| full | mondrian | λ per group = 0.5/0.5/0.5 | 75.9 | 0.00 | 4881 |
| 250-4000 | mdp | -1 | 75.9 | 0.00 | 5089 |
| 500-4000 | mdp | -1 | 75.9 | 0.00 | 5233 |
| 250-500-4000 | mdp | -1 | 75.9 | 0.00 | 5400 |
| x4 | mdp | -1 | 75.9 | 0.00 | 5758 |
| 250-1000-4000 | mdp | -1 | 75.9 | 0.00 | 5758 |
| 250-2000-4000 | mdp | -1 | 75.9 | 0.00 | 6701 |
| 500-2000-4000 | mdp | -1 | 75.9 | 0.00 | 6845 |
| 250-1000-2000-4000 | mdp | -1 | 75.9 | 0.00 | 7371 |
| doubling | mdp | -1 | 75.9 | 0.00 | 7682 |

Selected on validation: marginal = `500-4000` / giveup; group-conditional = `500-4000` / mondrian.


### TurboReg, fcgf_3DMatch test (812 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 91.75 | 1224 | +0.37 [+0.74] | True | 4.21× [3.81, 4.77] | 0.25 | 0.37 |
| mondrian: 500-4000 / mondrian | 92.00 | 2236 | +0.12 [+0.37] | True | 2.31× [2.14, 2.51] | 1 | 0.12 |
| fixed budget N=250 (single run) | 86.70 | 209 | | | | | |
| fixed budget N=500 (single run) | 88.67 | 338 | | | | | |
| fixed budget N=1000 (single run) | 90.02 | 673 | | | | | |
| fixed budget N=2000 (single run) | 91.26 | 1657 | | | | | |
| fixed budget N=4000 (single run) | 92.12 | 5155 | | | | | |

### TurboReg, fcgf_3DLoMatch test (891 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / giveup | 57.58 | 3749 | +0.45 [+0.90] | True | 1.25× [1.21, 1.30] | 0.125 | 0.45 |
| mondrian: 500-4000 / mondrian | 58.02 | 4498 | +0.00 [+0.00] | True | 1.04× [1.02, 1.07] | 1 | 0.00 |
| fixed budget N=250 (single run) | 44.22 | 202 | | | | | |
| fixed budget N=500 (single run) | 46.58 | 329 | | | | | |
| fixed budget N=1000 (single run) | 51.40 | 647 | | | | | |
| fixed budget N=2000 (single run) | 53.98 | 1599 | | | | | |
| fixed budget N=4000 (single run) | 58.02 | 4695 | | | | | |
