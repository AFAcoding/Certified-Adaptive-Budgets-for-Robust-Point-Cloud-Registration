# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## SC²-PCR

Validation, certified operating points (cheapest first):

| ladder | policy | parameters | val RR % | val risk % | val mean time (ms) |
|---|---|---|---|---|---|
| full | threshold | 0.5 | 75.1 | 0.00 | 2806 |
| full | giveup | 0.5, 0 | 75.1 | 0.00 | 2806 |
| full | mondrian | λ per group = 0.5/0.5/0.5 | 75.1 | 0.00 | 2806 |
| 250-4000 | mondrian | λ per group = 0.98/1.01/1.01 | 75.1 | 0.06 | 2841 |
| 250-4000 | threshold | 1.01 | 75.1 | 0.00 | 2855 |
| 250-4000 | mdp | -1 | 75.1 | 0.00 | 2855 |
| 250-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 2855 |
| 500-4000 | threshold | 1.01 | 75.1 | 0.00 | 2943 |
| 500-4000 | mdp | -1 | 75.1 | 0.00 | 2943 |
| 500-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 2943 |
| 500-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 2943 |
| 250-500-4000 | threshold | 1.01 | 75.1 | 0.00 | 2992 |
| 250-500-4000 | mdp | -1 | 75.1 | 0.00 | 2992 |
| 250-500-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 2992 |
| 250-500-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 2992 |
| x4 | threshold | 1.01 | 75.1 | 0.00 | 3214 |
| x4 | mdp | -1 | 75.1 | 0.00 | 3214 |
| x4 | giveup | 1.01, 0 | 75.1 | 0.00 | 3214 |
| x4 | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 3214 |
| 250-1000-4000 | threshold | 1.01 | 75.1 | 0.00 | 3214 |
| 250-1000-4000 | mdp | -1 | 75.1 | 0.00 | 3214 |
| 250-1000-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 3214 |
| 250-1000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 3214 |
| 250-2000-4000 | mondrian | λ per group = 0.995/1.01/1.01 | 75.2 | 0.06 | 3607 |
| 250-2000-4000 | threshold | 1.01 | 75.1 | 0.00 | 3781 |
| 250-2000-4000 | mdp | -1 | 75.1 | 0.00 | 3781 |
| 250-2000-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 3781 |
| 500-2000-4000 | threshold | 1.01 | 75.1 | 0.00 | 3869 |
| 500-2000-4000 | mdp | -1 | 75.1 | 0.00 | 3869 |
| 500-2000-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 3869 |
| 500-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 3869 |
| 250-1000-2000-4000 | giveup | 1.01, 0.3 | 75.1 | 0.00 | 4137 |
| 250-1000-2000-4000 | threshold | 1.01 | 75.1 | 0.00 | 4140 |
| 250-1000-2000-4000 | mdp | -1 | 75.1 | 0.00 | 4140 |
| 250-1000-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 4140 |
| doubling | threshold | 1.01 | 75.1 | 0.00 | 4276 |
| doubling | mdp | -1 | 75.1 | 0.00 | 4276 |
| doubling | giveup | 1.01, 0 | 75.1 | 0.00 | 4276 |
| doubling | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 4276 |

Selected on validation: marginal = `full` / threshold; group-conditional = `full` / mondrian.


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

Validation, certified operating points (cheapest first):

| ladder | policy | parameters | val RR % | val risk % | val mean time (ms) |
|---|---|---|---|---|---|
| full | threshold | 0.5 | 75.1 | 0.00 | 4902 |
| full | giveup | 0.5, 0 | 75.1 | 0.00 | 4902 |
| full | mondrian | λ per group = 0.5/0.5/0.5 | 75.1 | 0.00 | 4902 |
| 250-4000 | mondrian | λ per group = 0.99/1.01/1.01 | 75.1 | 0.00 | 4989 |
| 250-4000 | threshold | 1.01 | 75.1 | 0.00 | 4990 |
| 250-4000 | mdp | -1 | 75.1 | 0.00 | 4990 |
| 250-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 4990 |
| 500-4000 | threshold | 1.01 | 75.1 | 0.00 | 5164 |
| 500-4000 | mdp | -1 | 75.1 | 0.00 | 5164 |
| 500-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 5164 |
| 500-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 5164 |
| 250-500-4000 | threshold | 1.01 | 75.1 | 0.00 | 5252 |
| 250-500-4000 | mdp | -1 | 75.1 | 0.00 | 5252 |
| 250-500-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 5252 |
| 250-500-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 5252 |
| x4 | threshold | 1.01 | 75.1 | 0.00 | 5648 |
| x4 | mdp | -1 | 75.1 | 0.00 | 5648 |
| x4 | giveup | 1.01, 0 | 75.1 | 0.00 | 5648 |
| x4 | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 5648 |
| 250-1000-4000 | threshold | 1.01 | 75.1 | 0.00 | 5648 |
| 250-1000-4000 | mdp | -1 | 75.1 | 0.00 | 5648 |
| 250-1000-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 5648 |
| 250-1000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 5648 |
| 250-2000-4000 | giveup | 1.01, 0.3 | 75.1 | 0.06 | 6586 |
| 250-2000-4000 | threshold | 1.01 | 75.1 | 0.00 | 6593 |
| 250-2000-4000 | mdp | -1 | 75.1 | 0.00 | 6593 |
| 250-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 6593 |
| 500-2000-4000 | threshold | 1.01 | 75.1 | 0.00 | 6767 |
| 500-2000-4000 | mdp | -1 | 75.1 | 0.00 | 6767 |
| 500-2000-4000 | giveup | 1.01, 0 | 75.1 | 0.00 | 6767 |
| 500-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 6767 |
| 250-1000-2000-4000 | giveup | 1.01, 0.3 | 75.1 | 0.00 | 7247 |
| 250-1000-2000-4000 | threshold | 1.01 | 75.1 | 0.00 | 7251 |
| 250-1000-2000-4000 | mdp | -1 | 75.1 | 0.00 | 7251 |
| 250-1000-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 7251 |
| doubling | threshold | 1.01 | 75.1 | 0.00 | 7513 |
| doubling | mdp | -1 | 75.1 | 0.00 | 7513 |
| doubling | giveup | 1.01, 0 | 75.1 | 0.00 | 7513 |
| doubling | mondrian | λ per group = 1.01/1.01/1.01 | 75.1 | 0.00 | 7513 |

Selected on validation: marginal = `full` / threshold; group-conditional = `full` / mondrian.


### TurboReg, fcgf_3DMatch test (812 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 92.12 | 5155 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 92.12 | 5155 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 84.98 | 124 | | | | | |
| fixed budget N=500 (single run) | 88.30 | 284 | | | | | |
| fixed budget N=1000 (single run) | 90.64 | 629 | | | | | |
| fixed budget N=2000 (single run) | 91.26 | 1620 | | | | | |
| fixed budget N=4000 (single run) | 92.12 | 5155 | | | | | |

### TurboReg, fcgf_3DLoMatch test (891 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 58.02 | 4695 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 58.02 | 4695 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 38.61 | 49 | | | | | |
| fixed budget N=500 (single run) | 45.34 | 202 | | | | | |
| fixed budget N=1000 (single run) | 52.86 | 593 | | | | | |
| fixed budget N=2000 (single run) | 55.67 | 1536 | | | | | |
| fixed budget N=4000 (single run) | 58.02 | 4695 | | | | | |
