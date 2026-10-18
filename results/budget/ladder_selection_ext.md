# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## SC²-PCR

Validation, certified operating points (cheapest first):

| ladder | policy | parameters | val RR % | val risk % | val mean time (ms) |
|---|---|---|---|---|---|
| x4 | threshold | 0.7 | 71.1 | 0.53 | 851 |
| 250-1000-4000 | threshold | 0.7 | 71.1 | 0.53 | 851 |
| 500-4000 | giveup | 0.7, 0.2 | 71.4 | 0.38 | 887 |
| x4 | giveup | 0.75, 0 | 71.2 | 0.38 | 899 |
| 250-1000-4000 | giveup | 0.75, 0 | 71.2 | 0.38 | 899 |
| 500-4000 | mdp | 0 | 71.3 | 0.45 | 900 |
| 500-4000 | threshold | 0.7 | 71.4 | 0.38 | 905 |
| 250-500-4000 | threshold | 0.7 | 71.1 | 0.60 | 906 |
| 250-500-4000 | giveup | 0.75, 0.2 | 71.3 | 0.30 | 919 |
| 500-2000-4000 | threshold | 0.7 | 71.4 | 0.53 | 961 |
| 250-4000 | giveup | 0.7, 0.3 | 71.1 | 0.38 | 986 |
| 250-4000 | threshold | 0.6 | 71.0 | 0.45 | 1018 |
| 250-2000-4000 | mdp | 0 | 71.4 | 0.30 | 1022 |
| 500-2000-4000 | mdp | 0 | 71.5 | 0.45 | 1023 |
| 250-2000-4000 | threshold | 0.75 | 71.1 | 0.53 | 1026 |
| 250-1000-2000-4000 | threshold | 0.75 | 71.1 | 0.60 | 1035 |
| 250-2000-4000 | giveup | 0.8, 0.15 | 71.3 | 0.38 | 1066 |
| 250-4000 | mondrian | λ per group = 0.5/0.85/0.5 | 71.4 | 0.00 | 1070 |
| 500-2000-4000 | giveup | 0.85, 0.2 | 71.5 | 0.30 | 1072 |
| x4 | mondrian | λ per group = 0.92/0.92/0.5 | 71.5 | 0.00 | 1094 |
| 250-1000-4000 | mondrian | λ per group = 0.92/0.92/0.5 | 71.5 | 0.00 | 1094 |
| 250-1000-2000-4000 | giveup | 0.85, 0.2 | 71.1 | 0.38 | 1099 |
| 250-500-4000 | mdp | 0 | 71.3 | 0.15 | 1099 |
| 250-500-4000 | mondrian | λ per group = 0.75/0.9/0.97 | 71.5 | 0.00 | 1139 |
| 250-2000-4000 | mondrian | λ per group = 0.8/0.9/0.5 | 71.7 | 0.00 | 1139 |
| 250-4000 | mdp | 0 | 71.3 | 0.08 | 1143 |
| doubling | threshold | 0.8 | 71.2 | 0.53 | 1148 |
| x4 | mdp | 0 | 71.3 | 0.15 | 1149 |
| 250-1000-4000 | mdp | 0 | 71.3 | 0.15 | 1149 |
| doubling | giveup | 0.85, 0.2 | 71.3 | 0.38 | 1162 |
| 500-4000 | mondrian | λ per group = 0.7/0.92/0.97 | 71.5 | 0.00 | 1178 |
| doubling | mdp | 0 | 71.4 | 0.38 | 1179 |
| 500-2000-4000 | mondrian | λ per group = 0.75/0.94/0.97 | 71.6 | 0.00 | 1345 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.9/0.94/0.5 | 71.5 | 0.00 | 1346 |
| doubling | mondrian | λ per group = 0.9/0.94/0.98 | 71.5 | 0.00 | 1595 |
| full | threshold | 0.5 | 71.4 | 0.00 | 1672 |
| full | giveup | 0.5, 0 | 71.4 | 0.00 | 1672 |
| full | mondrian | λ per group = 0.5/0.5/0.5 | 71.4 | 0.00 | 1672 |
| 250-1000-2000-4000 | mdp | -1 | 71.4 | 0.00 | 2600 |

Selected on validation: marginal = `x4` / threshold; group-conditional = `250-4000` / mondrian.


### SC²-PCR, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / threshold | 80.04 | 1281 | +1.48 [+2.03] | False | 2.16× [2.04, 2.28] | 8.43e-06 | 1.66 |
| mondrian: 250-4000 / mondrian | 80.71 | 1670 | +0.80 [+1.17] | False | 1.65× [1.59, 1.72] | 0.000244 | 0.80 |
| fixed budget N=250 (single run) | 50.83 | 55 | | | | | |
| fixed budget N=500 (single run) | 61.31 | 143 | | | | | |
| fixed budget N=1000 (single run) | 70.18 | 375 | | | | | |
| fixed budget N=2000 (single run) | 77.08 | 965 | | | | | |
| fixed budget N=4000 (single run) | 81.52 | 2762 | | | | | |

### SC²-PCR, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / threshold | 36.22 | 2511 | +0.39 [+0.73] | True | 0.98× [0.97, 1.00] | 0.0654 | 0.51 |
| mondrian: 250-4000 / mondrian | 36.50 | 2408 | +0.11 [+0.22] | True | 1.03× [1.02, 1.04] | 0.5 | 0.11 |
| fixed budget N=250 (single run) | 13.31 | 60 | | | | | |
| fixed budget N=500 (single run) | 19.03 | 152 | | | | | |
| fixed budget N=1000 (single run) | 25.44 | 378 | | | | | |
| fixed budget N=2000 (single run) | 32.00 | 933 | | | | | |
| fixed budget N=4000 (single run) | 36.61 | 2470 | | | | | |

## TurboReg

Validation, certified operating points (cheapest first):

| ladder | policy | parameters | val RR % | val risk % | val mean time (ms) |
|---|---|---|---|---|---|
| x4 | threshold | 0.7 | 71.8 | 0.60 | 1417 |
| 250-1000-4000 | threshold | 0.7 | 71.8 | 0.60 | 1417 |
| x4 | giveup | 0.75, 0.2 | 72.1 | 0.38 | 1469 |
| 250-1000-4000 | giveup | 0.75, 0.2 | 72.1 | 0.38 | 1469 |
| 500-4000 | giveup | 0.8, 0.3 | 72.1 | 0.38 | 1506 |
| 250-500-4000 | threshold | 0.8 | 72.0 | 0.45 | 1512 |
| 500-4000 | threshold | 0.75 | 72.0 | 0.45 | 1540 |
| 250-500-4000 | giveup | 0.85, 0.2 | 72.1 | 0.38 | 1560 |
| x4 | mondrian | λ per group = 0.5/0.93/0.88 | 72.4 | 0.00 | 1585 |
| 250-1000-4000 | mondrian | λ per group = 0.5/0.93/0.88 | 72.4 | 0.00 | 1585 |
| 250-2000-4000 | threshold | 0.75 | 71.9 | 0.53 | 1686 |
| 250-1000-2000-4000 | threshold | 0.75 | 71.8 | 0.60 | 1702 |
| 250-4000 | threshold | 0.7 | 71.8 | 0.53 | 1723 |
| 250-500-4000 | mdp | 0 | 72.2 | 0.15 | 1728 |
| 250-4000 | giveup | 0.75, 0.3 | 72.0 | 0.30 | 1739 |
| 250-500-4000 | mondrian | λ per group = 0.88/0.97/0.88 | 72.4 | 0.00 | 1760 |
| 500-2000-4000 | threshold | 0.8 | 71.9 | 0.53 | 1761 |
| 250-2000-4000 | giveup | 0.8, 0.15 | 72.0 | 0.38 | 1782 |
| doubling | mdp | 0 | 71.9 | 0.60 | 1822 |
| 250-1000-2000-4000 | giveup | 0.8, 0.15 | 72.1 | 0.30 | 1826 |
| doubling | threshold | 0.8 | 71.8 | 0.60 | 1843 |
| 500-2000-4000 | giveup | 0.85, 0.15 | 72.1 | 0.38 | 1860 |
| 250-4000 | mondrian | λ per group = 0.5/0.92/0.85 | 72.2 | 0.00 | 1880 |
| x4 | mdp | 0 | 72.3 | 0.08 | 1891 |
| 250-1000-4000 | mdp | 0 | 72.3 | 0.08 | 1891 |
| 500-4000 | mondrian | λ per group = 0.6/0.88/0.98 | 72.4 | 0.00 | 1936 |
| 250-4000 | mdp | 0 | 72.2 | 0.08 | 1941 |
| doubling | giveup | 0.85, 0.15 | 72.1 | 0.38 | 1980 |
| 250-2000-4000 | mondrian | λ per group = 0.8/0.92/0.92 | 72.4 | 0.00 | 2029 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.8/0.92/0.9 | 72.4 | 0.00 | 2063 |
| 500-2000-4000 | mdp | 0 | 72.1 | 0.30 | 2087 |
| 500-2000-4000 | mondrian | λ per group = 0.85/0.9/0.98 | 72.4 | 0.00 | 2298 |
| doubling | mondrian | λ per group = 0.9/0.98/0.9 | 72.4 | 0.00 | 2449 |
| full | threshold | 0.5 | 72.2 | 0.00 | 2917 |
| full | giveup | 0.5, 0 | 72.2 | 0.00 | 2917 |
| full | mondrian | λ per group = 0.5/0.5/0.5 | 72.2 | 0.00 | 2917 |
| 500-4000 | mdp | -1 | 72.2 | 0.00 | 3082 |
| 250-2000-4000 | mdp | -1 | 72.2 | 0.00 | 3925 |
| 250-1000-2000-4000 | mdp | -1 | 72.2 | 0.00 | 4430 |

Selected on validation: marginal = `x4` / threshold; group-conditional = `x4` / mondrian.


### TurboReg, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / threshold | 79.91 | 1974 | +1.97 [+2.59] | False | 2.33× [2.19, 2.47] | 4.07e-09 | 2.03 |
| mondrian: x4 / mondrian | 80.65 | 2235 | +1.23 [+1.73] | False | 2.05× [1.95, 2.17] | 1.1e-05 | 1.29 |
| fixed budget N=250 (single run) | 49.04 | 26 | | | | | |
| fixed budget N=500 (single run) | 60.01 | 140 | | | | | |
| fixed budget N=1000 (single run) | 69.25 | 548 | | | | | |
| fixed budget N=2000 (single run) | 76.59 | 1582 | | | | | |
| fixed budget N=4000 (single run) | 81.89 | 4590 | | | | | |

### TurboReg, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / threshold | 36.22 | 3918 | +0.34 [+0.62] | True | 1.05× [1.03, 1.07] | 0.0703 | 0.39 |
| mondrian: x4 / mondrian | 36.05 | 4051 | +0.51 [+0.84] | True | 1.01× [1.00, 1.03] | 0.0225 | 0.62 |
| fixed budget N=250 (single run) | 13.87 | 11 | | | | | |
| fixed budget N=500 (single run) | 19.03 | 81 | | | | | |
| fixed budget N=1000 (single run) | 25.21 | 469 | | | | | |
| fixed budget N=2000 (single run) | 31.44 | 1517 | | | | | |
| fixed budget N=4000 (single run) | 36.55 | 4100 | | | | | |
