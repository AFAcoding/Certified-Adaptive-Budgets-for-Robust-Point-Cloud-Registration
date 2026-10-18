# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## SC²-PCR

Validation, certified operating points (cheapest first):

| ladder | policy | parameters | val RR % | val risk % | val mean time (ms) |
|---|---|---|---|---|---|
| full | threshold | 0.5 | 75.1 | 0.00 | 2806 |
| full | giveup | 0.5, 0 | 75.1 | 0.00 | 2806 |
| full | mondrian | λ per group = 0.5/0.5/0.5 | 75.1 | 0.00 | 2806 |
| 250-4000 | mondrian | λ per group = 0.99/1.01/1.01 | 75.1 | 0.00 | 2885 |
| 250-4000 | threshold | 1.01 | 75.1 | 0.00 | 2887 |
| 250-4000 | mdp | -1 | 75.1 | 0.00 | 2887 |
| 250-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 2887 |
| 500-4000 | mondrian | λ per group = 0.99/1.01/1.01 | 75.1 | 0.00 | 2943 |
| 500-4000 | threshold | 1.01 | 75.1 | 0.00 | 2948 |
| 500-4000 | mdp | -1 | 75.1 | 0.00 | 2948 |
| 500-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 2948 |
| 250-500-4000 | threshold | 1.01 | 75.1 | 0.00 | 2989 |
| 250-500-4000 | mdp | -1 | 75.1 | 0.00 | 2989 |
| 250-500-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 2989 |
| 250-500-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 2989 |
| x4 | threshold | 1.01 | 75.1 | 0.00 | 3143 |
| x4 | mdp | -1 | 75.1 | 0.00 | 3143 |
| x4 | giveup | 1.01, 0 | 75.1 | 0.00 | 3143 |
| x4 | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 3143 |
| 250-1000-4000 | threshold | 1.01 | 75.1 | 0.00 | 3143 |
| 250-1000-4000 | mdp | -1 | 75.1 | 0.00 | 3143 |
| 250-1000-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 3143 |
| 250-1000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 3143 |
| 500-2000-4000 | mondrian | λ per group = 0.995/1.01/1.01 | 75.1 | 0.06 | 3689 |
| 250-2000-4000 | threshold | 1.01 | 75.1 | 0.00 | 3699 |
| 250-2000-4000 | mdp | -1 | 75.1 | 0.00 | 3699 |
| 250-2000-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 3699 |
| 250-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 3699 |
| 500-2000-4000 | threshold | 1.01 | 75.1 | 0.00 | 3761 |
| 500-2000-4000 | mdp | -1 | 75.1 | 0.00 | 3761 |
| 500-2000-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 3761 |
| 250-1000-2000-4000 | threshold | 1.01 | 75.1 | 0.00 | 3956 |
| 250-1000-2000-4000 | mdp | -1 | 75.1 | 0.00 | 3956 |
| 250-1000-2000-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 3956 |
| 250-1000-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 3956 |
| doubling | threshold | 1.01 | 75.1 | 0.00 | 4058 |
| doubling | mdp | -1 | 75.1 | 0.00 | 4058 |
| doubling | giveup | 1.01, 0 | 75.1 | 0.00 | 4058 |
| doubling | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 4058 |

Selected on validation: marginal = `full` / threshold; group-conditional = `full` / mondrian.


### SC²-PCR, fcgf_3DMatch test (812 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 92.36 | 2647 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 92.36 | 2647 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 87.07 | 98 | | | | | |
| fixed budget N=500 (single run) | 88.30 | 155 | | | | | |
| fixed budget N=1000 (single run) | 90.15 | 303 | | | | | |
| fixed budget N=2000 (single run) | 91.50 | 828 | | | | | |
| fixed budget N=4000 (single run) | 92.36 | 2647 | | | | | |

### SC²-PCR, fcgf_3DLoMatch test (891 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 57.35 | 2289 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 57.35 | 2289 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 44.56 | 89 | | | | | |
| fixed budget N=500 (single run) | 46.24 | 140 | | | | | |
| fixed budget N=1000 (single run) | 51.29 | 292 | | | | | |
| fixed budget N=2000 (single run) | 54.43 | 796 | | | | | |
| fixed budget N=4000 (single run) | 57.35 | 2289 | | | | | |

## TurboReg

Validation, certified operating points (cheapest first):

| ladder | policy | parameters | val RR % | val risk % | val mean time (ms) |
|---|---|---|---|---|---|
| full | threshold | 0.5 | 75.1 | 0.00 | 4902 |
| full | giveup | 0.5, 0 | 75.1 | 0.00 | 4902 |
| full | mondrian | λ per group = 0.5/0.5/0.5 | 75.1 | 0.00 | 4902 |
| 250-4000 | mondrian | λ per group = 0.98/1.01/1.01 | 75.1 | 0.06 | 5090 |
| 250-4000 | threshold | 1.01 | 75.1 | 0.00 | 5110 |
| 250-4000 | mdp | -1 | 75.1 | 0.00 | 5110 |
| 250-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 5110 |
| 500-4000 | mondrian | λ per group = 0.99/1.01/1.01 | 75.1 | 0.06 | 5244 |
| 500-4000 | threshold | 1.01 | 75.1 | 0.00 | 5253 |
| 500-4000 | mdp | -1 | 75.1 | 0.00 | 5253 |
| 500-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 5253 |
| 250-500-4000 | mondrian | λ per group = 0.995/1.01/1.01 | 75.1 | 0.06 | 5415 |
| 250-500-4000 | threshold | 1.01 | 75.1 | 0.00 | 5421 |
| 250-500-4000 | mdp | -1 | 75.1 | 0.00 | 5421 |
| 250-500-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 5421 |
| x4 | threshold | 1.01 | 75.1 | 0.00 | 5779 |
| x4 | mdp | -1 | 75.1 | 0.00 | 5779 |
| x4 | giveup | 1.01, 0 | 75.1 | 0.00 | 5779 |
| x4 | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 5779 |
| 250-1000-4000 | threshold | 1.01 | 75.1 | 0.00 | 5779 |
| 250-1000-4000 | mdp | -1 | 75.1 | 0.00 | 5779 |
| 250-1000-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 5779 |
| 250-1000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 5779 |
| 250-2000-4000 | mondrian | λ per group = 0.995/1.01/1.01 | 75.1 | 0.06 | 6613 |
| 250-2000-4000 | threshold | 1.01 | 75.1 | 0.00 | 6725 |
| 250-2000-4000 | mdp | -1 | 75.1 | 0.00 | 6725 |
| 250-2000-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 6725 |
| 500-2000-4000 | mondrian | λ per group = 0.995/1.01/1.01 | 75.1 | 0.06 | 6745 |
| 500-2000-4000 | threshold | 1.01 | 75.1 | 0.00 | 6869 |
| 500-2000-4000 | mdp | -1 | 75.1 | 0.00 | 6869 |
| 500-2000-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 6869 |
| 250-1000-2000-4000 | threshold | 1.01 | 75.1 | 0.00 | 7395 |
| 250-1000-2000-4000 | mdp | -1 | 75.1 | 0.00 | 7395 |
| 250-1000-2000-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 7395 |
| 250-1000-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 7395 |
| doubling | threshold | 1.01 | 75.1 | 0.00 | 7706 |
| doubling | mdp | -1 | 75.1 | 0.00 | 7706 |
| doubling | giveup | 1.01, 0 | 75.1 | 0.00 | 7706 |
| doubling | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 7706 |

Selected on validation: marginal = `full` / threshold; group-conditional = `full` / mondrian.


### TurboReg, fcgf_3DMatch test (812 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 92.12 | 5155 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 92.12 | 5155 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 86.70 | 209 | | | | | |
| fixed budget N=500 (single run) | 88.67 | 338 | | | | | |
| fixed budget N=1000 (single run) | 90.02 | 673 | | | | | |
| fixed budget N=2000 (single run) | 91.26 | 1657 | | | | | |
| fixed budget N=4000 (single run) | 92.12 | 5155 | | | | | |

### TurboReg, fcgf_3DLoMatch test (891 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 58.02 | 4695 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 58.02 | 4695 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 44.22 | 202 | | | | | |
| fixed budget N=500 (single run) | 46.58 | 329 | | | | | |
| fixed budget N=1000 (single run) | 51.40 | 647 | | | | | |
| fixed budget N=2000 (single run) | 53.98 | 1599 | | | | | |
| fixed budget N=4000 (single run) | 58.02 | 4695 | | | | | |
