# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## SC²-PCR

Validation, certified operating points (cheapest first):

| ladder | policy | parameters | val RR % | val risk % | val mean time (ms) |
|---|---|---|---|---|---|
| 250-4000 | threshold | 0.6 | 71.0 | 0.60 | 832 |
| 250-500-4000 | mdp | 0 | 71.2 | 0.38 | 862 |
| 500-4000 | threshold | 0.7 | 71.1 | 0.45 | 868 |
| x4 | threshold | 0.7 | 71.1 | 0.60 | 875 |
| 250-1000-4000 | threshold | 0.7 | 71.1 | 0.60 | 875 |
| 250-4000 | giveup | 0.7, 0.15 | 71.2 | 0.38 | 877 |
| 500-4000 | giveup | 0.75, 0.15 | 71.2 | 0.38 | 888 |
| 250-500-4000 | threshold | 0.75 | 71.1 | 0.45 | 897 |
| 250-500-4000 | giveup | 0.8, 0.1 | 71.3 | 0.30 | 927 |
| 250-4000 | mondrian | λ per group = 0.6/0.8/0.5 | 71.6 | 0.00 | 933 |
| 500-2000-4000 | mdp | 0 | 71.2 | 0.60 | 935 |
| 250-2000-4000 | threshold | 0.7 | 71.2 | 0.53 | 939 |
| x4 | mdp | 0 | 71.2 | 0.30 | 947 |
| 250-1000-4000 | mdp | 0 | 71.2 | 0.30 | 947 |
| x4 | giveup | 0.8, 0 | 71.3 | 0.38 | 953 |
| 250-1000-4000 | giveup | 0.8, 0 | 71.3 | 0.38 | 953 |
| 500-2000-4000 | threshold | 0.7 | 71.3 | 0.53 | 960 |
| 250-500-4000 | mondrian | λ per group = 0.93/0.85/0.5 | 71.6 | 0.00 | 981 |
| 250-2000-4000 | giveup | 0.8, 0.15 | 71.3 | 0.38 | 1015 |
| 500-2000-4000 | giveup | 0.75, 0 | 71.5 | 0.38 | 1018 |
| 500-4000 | mondrian | λ per group = 0.7/0.9/0.5 | 71.5 | 0.00 | 1025 |
| x4 | mondrian | λ per group = 0.7/0.88/0.5 | 71.6 | 0.00 | 1028 |
| 250-1000-4000 | mondrian | λ per group = 0.7/0.88/0.5 | 71.6 | 0.00 | 1028 |
| 250-1000-2000-4000 | threshold | 0.75 | 71.3 | 0.53 | 1064 |
| 250-4000 | mdp | 0 | 71.4 | 0.00 | 1086 |
| doubling | threshold | 0.75 | 71.3 | 0.53 | 1101 |
| 250-2000-4000 | mdp | 0 | 71.6 | 0.08 | 1101 |
| 250-2000-4000 | mondrian | λ per group = 0.7/0.88/0.5 | 71.7 | 0.00 | 1104 |
| 250-1000-2000-4000 | giveup | 0.8, 0 | 71.3 | 0.38 | 1130 |
| 500-4000 | mdp | 0 | 71.4 | 0.00 | 1142 |
| doubling | giveup | 0.85, 0 | 71.2 | 0.38 | 1246 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.8/0.93/0.5 | 71.5 | 0.00 | 1340 |
| 500-2000-4000 | mondrian | λ per group = 0.7/0.97/0.5 | 71.5 | 0.00 | 1361 |
| doubling | mondrian | λ per group = 0.98/0.93/0.5 | 71.5 | 0.00 | 1456 |
| full | threshold | 0.5 | 71.4 | 0.00 | 1672 |
| full | giveup | 0.5, 0 | 71.4 | 0.00 | 1672 |
| full | mondrian | λ per group = 0.5/0.5/0.5 | 71.4 | 0.00 | 1672 |
| 250-1000-2000-4000 | mdp | -1 | 71.4 | 0.00 | 2526 |
| doubling | mdp | -1 | 71.4 | 0.00 | 2621 |

Selected on validation: marginal = `250-4000` / threshold; group-conditional = `250-4000` / mondrian.


### SC²-PCR, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / threshold | 80.90 | 1268 | +0.62 [+1.05] | False | 2.23× [2.11, 2.35] | 0.0213 | 0.80 |
| mondrian: 250-4000 / mondrian | 81.27 | 1439 | +0.25 [+0.49] | True | 1.96× [1.88, 2.07] | 0.219 | 0.31 |
| fixed budget N=250 (single run) | 65.13 | 81 | | | | | |
| fixed budget N=500 (single run) | 69.32 | 155 | | | | | |
| fixed budget N=1000 (single run) | 74.25 | 350 | | | | | |
| fixed budget N=2000 (single run) | 78.00 | 961 | | | | | |
| fixed budget N=4000 (single run) | 81.52 | 2825 | | | | | |

### SC²-PCR, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / threshold | 36.61 | 2324 | +0.00 [+0.17] | True | 1.09× [1.07, 1.11] | 1 | 0.11 |
| mondrian: 250-4000 / mondrian | 36.61 | 2438 | +0.00 [+0.00] | True | 1.04× [1.03, 1.05] | 1 | 0.00 |
| fixed budget N=250 (single run) | 21.45 | 84 | | | | | |
| fixed budget N=500 (single run) | 24.71 | 164 | | | | | |
| fixed budget N=1000 (single run) | 28.19 | 367 | | | | | |
| fixed budget N=2000 (single run) | 32.17 | 938 | | | | | |
| fixed budget N=4000 (single run) | 36.61 | 2538 | | | | | |

## TurboReg

Validation, certified operating points (cheapest first):

| ladder | policy | parameters | val RR % | val risk % | val mean time (ms) |
|---|---|---|---|---|---|
| 250-4000 | threshold | 0.6 | 71.9 | 0.53 | 1500 |
| 250-4000 | mdp | 0 | 72.1 | 0.38 | 1573 |
| 250-4000 | giveup | 0.7, 0.2 | 72.1 | 0.38 | 1585 |
| 500-4000 | mdp | 0 | 71.8 | 0.60 | 1620 |
| 250-500-4000 | mdp | 0 | 71.8 | 0.60 | 1625 |
| 500-4000 | threshold | 0.75 | 71.8 | 0.60 | 1638 |
| x4 | threshold | 0.75 | 72.1 | 0.45 | 1698 |
| 250-1000-4000 | threshold | 0.75 | 72.1 | 0.45 | 1698 |
| 250-2000-4000 | threshold | 0.7 | 71.8 | 0.60 | 1708 |
| 250-500-4000 | threshold | 0.8 | 71.9 | 0.53 | 1722 |
| 250-4000 | mondrian | λ per group = 0.75/0.85/0.5 | 72.4 | 0.00 | 1736 |
| x4 | mdp | 0 | 71.8 | 0.53 | 1762 |
| 250-1000-4000 | mdp | 0 | 71.8 | 0.53 | 1762 |
| x4 | giveup | 0.8, 0.15 | 72.1 | 0.38 | 1779 |
| 250-1000-4000 | giveup | 0.8, 0.15 | 72.1 | 0.38 | 1779 |
| 500-4000 | giveup | 0.85, 0.15 | 72.1 | 0.30 | 1788 |
| 250-2000-4000 | giveup | 0.75, 0.15 | 72.1 | 0.38 | 1797 |
| 250-500-4000 | giveup | 0.85, 0.15 | 72.1 | 0.30 | 1815 |
| 250-2000-4000 | mdp | 0 | 72.1 | 0.23 | 1851 |
| 250-500-4000 | mondrian | λ per group = 0.92/0.9/0.5 | 72.3 | 0.00 | 1913 |
| 500-4000 | mondrian | λ per group = 0.6/0.92/0.5 | 72.2 | 0.00 | 1930 |
| 250-1000-2000-4000 | threshold | 0.75 | 72.0 | 0.53 | 1949 |
| 500-2000-4000 | threshold | 0.8 | 71.8 | 0.60 | 1980 |
| 250-2000-4000 | mondrian | λ per group = 0.8/0.85/0.5 | 72.4 | 0.00 | 1991 |
| x4 | mondrian | λ per group = 0.75/0.93/0.5 | 72.3 | 0.00 | 2073 |
| 250-1000-4000 | mondrian | λ per group = 0.75/0.93/0.5 | 72.3 | 0.00 | 2073 |
| 500-2000-4000 | mdp | 0 | 72.1 | 0.15 | 2076 |
| 250-1000-2000-4000 | giveup | 0.8, 0.1 | 72.1 | 0.38 | 2085 |
| 500-2000-4000 | giveup | 0.88, 0.1 | 72.1 | 0.38 | 2192 |
| doubling | threshold | 0.85 | 71.9 | 0.60 | 2384 |
| 500-2000-4000 | mondrian | λ per group = 0.7/0.96/0.5 | 72.2 | 0.00 | 2432 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.75/0.93/0.5 | 72.3 | 0.00 | 2435 |
| doubling | giveup | 0.88, 0.15 | 72.2 | 0.30 | 2487 |
| doubling | mondrian | λ per group = 0.96/0.93/0.5 | 72.3 | 0.00 | 2733 |
| full | threshold | 0.5 | 72.2 | 0.00 | 2917 |
| full | giveup | 0.5, 0 | 72.2 | 0.00 | 2917 |
| full | mondrian | λ per group = 0.5/0.5/0.5 | 72.2 | 0.00 | 2917 |
| 250-1000-2000-4000 | mdp | -1 | 72.2 | 0.00 | 4605 |
| doubling | mdp | -1 | 72.2 | 0.00 | 4883 |

Selected on validation: marginal = `250-4000` / threshold; group-conditional = `250-4000` / mondrian.


### TurboReg, 3DMatch test (1623 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / threshold | 81.15 | 2171 | +0.74 [+1.11] | False | 2.16× [2.05, 2.27] | 0.00183 | 0.80 |
| mondrian: 250-4000 / mondrian | 81.52 | 2553 | +0.37 [+0.62] | True | 1.84× [1.76, 1.92] | 0.0312 | 0.37 |
| fixed budget N=250 (single run) | 65.00 | 195 | | | | | |
| fixed budget N=500 (single run) | 69.32 | 341 | | | | | |
| fixed budget N=1000 (single run) | 74.00 | 685 | | | | | |
| fixed budget N=2000 (single run) | 78.31 | 1645 | | | | | |
| fixed budget N=4000 (single run) | 81.89 | 4686 | | | | | |

### TurboReg, 3DLoMatch test (1781 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / threshold | 36.55 | 3888 | +0.00 [+0.11] | True | 1.09× [1.07, 1.10] | 1 | 0.06 |
| mondrian: 250-4000 / mondrian | 36.55 | 4109 | +0.00 [+0.00] | True | 1.03× [1.02, 1.04] | 1 | 0.00 |
| fixed budget N=250 (single run) | 21.56 | 146 | | | | | |
| fixed budget N=500 (single run) | 24.93 | 321 | | | | | |
| fixed budget N=1000 (single run) | 28.13 | 679 | | | | | |
| fixed budget N=2000 (single run) | 32.06 | 1592 | | | | | |
| fixed budget N=4000 (single run) | 36.55 | 4224 | | | | | |
