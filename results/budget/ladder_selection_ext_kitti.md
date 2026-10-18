# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## SC²-PCR

Validation, certified operating points (cheapest first):

| ladder | policy | parameters | val RR % | val risk % | val mean time (ms) |
|---|---|---|---|---|---|
| 500-2000-4000 | threshold | 0.6 | 78.7 | 0.57 | 2787 |
| 250-1000-2000-4000 | giveup | 0.75, 0.1 | 78.9 | 0.32 | 2899 |
| 500-2000-4000 | giveup | 0.7, 0.05 | 78.9 | 0.32 | 2927 |
| 250-1000-2000-4000 | threshold | 0.7 | 79.0 | 0.24 | 2968 |
| 500-2000-4000 | mondrian | λ per group = 0.75/0.75/0.75 | 79.2 | 0.00 | 3001 |
| 250-2000-4000 | threshold | 0.7 | 78.8 | 0.40 | 3023 |
| doubling | giveup | 0.75, 0.02 | 78.9 | 0.32 | 3042 |
| doubling | threshold | 0.75 | 78.9 | 0.32 | 3049 |
| 250-2000-4000 | giveup | 0.75, 0.05 | 78.9 | 0.32 | 3148 |
| 250-1000-2000-4000 | mdp | 0 | 79.1 | 0.16 | 3179 |
| 500-2000-4000 | mdp | 0 | 79.2 | 0.00 | 3296 |
| 250-1000-2000-4000 | mondrian | λ per group = 1.01/0.7/0.6 | 79.2 | 0.08 | 3331 |
| 250-2000-4000 | mdp | 0 | 79.1 | 0.16 | 3361 |
| x4 | giveup | 0.6, 0.05 | 79.0 | 0.24 | 3384 |
| 250-1000-4000 | giveup | 0.6, 0.05 | 79.0 | 0.24 | 3384 |
| x4 | threshold | 0.6 | 79.0 | 0.24 | 3402 |
| 250-1000-4000 | threshold | 0.6 | 79.0 | 0.24 | 3402 |
| doubling | mondrian | λ per group = 1.01/0.8/0.6 | 79.2 | 0.08 | 3434 |
| x4 | mdp | 0 | 79.1 | 0.16 | 3439 |
| 250-1000-4000 | mdp | 0 | 79.1 | 0.16 | 3439 |
| 250-2000-4000 | mondrian | λ per group = 1.01/0.8/0.7 | 79.2 | 0.08 | 3495 |
| x4 | mondrian | λ per group = 1.01/0.6/0.5 | 79.2 | 0.08 | 3543 |
| 250-1000-4000 | mondrian | λ per group = 1.01/0.6/0.5 | 79.2 | 0.08 | 3543 |
| 500-4000 | giveup | 0.5, 0.3 | 79.1 | 0.16 | 4197 |
| 500-4000 | threshold | 0.5 | 79.2 | 0.08 | 4208 |
| 500-4000 | mondrian | λ per group = 0.5/0.5/0.6 | 79.2 | 0.00 | 4232 |
| 250-500-4000 | giveup | 0.5, 0.3 | 79.2 | 0.08 | 4272 |
| 250-500-4000 | threshold | 0.5 | 79.2 | 0.08 | 4280 |
| 500-4000 | mdp | 0 | 79.2 | 0.00 | 4304 |
| 250-500-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 79.2 | 0.08 | 4305 |
| 250-500-4000 | mdp | 0 | 79.2 | 0.00 | 4378 |
| full | threshold | 0.5 | 79.2 | 0.00 | 4450 |
| full | giveup | 0.5, 0 | 79.2 | 0.00 | 4450 |
| full | mondrian | λ per group = 0.5/0.5/0.5 | 79.2 | 0.00 | 4450 |
| 250-4000 | giveup | 0.5, 0.3 | 79.2 | 0.08 | 4476 |
| 250-4000 | threshold | 0.5 | 79.2 | 0.00 | 4506 |
| 250-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 79.2 | 0.00 | 4506 |
| 250-4000 | mdp | 0 | 79.2 | 0.00 | 4510 |
| doubling | mdp | -1 | 79.2 | 0.00 | 6328 |

Selected on validation: marginal = `500-2000-4000` / threshold; group-conditional = `500-2000-4000` / mondrian.


### SC²-PCR, kitti_test test (555 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-2000-4000 / threshold | 90.81 | 2410 | +1.44 [+2.34] | False | 1.78× [1.66, 1.92] | 0.00781 | 1.44 |
| mondrian: 500-2000-4000 / mondrian | 91.71 | 2671 | +0.54 [+1.08] | False | 1.61× [1.51, 1.72] | 0.25 | 0.54 |
| fixed budget N=250 (single run) | 1.62 | 55 | | | | | |
| fixed budget N=500 (single run) | 12.25 | 145 | | | | | |
| fixed budget N=1000 (single run) | 41.44 | 390 | | | | | |
| fixed budget N=2000 (single run) | 75.50 | 1200 | | | | | |
| fixed budget N=4000 (single run) | 92.25 | 4294 | | | | | |

## TurboReg

Validation, certified operating points (cheapest first):

| ladder | policy | parameters | val RR % | val risk % | val mean time (ms) |
|---|---|---|---|---|---|
| doubling | threshold | 0.7 | 78.7 | 0.57 | 3262 |
| doubling | giveup | 0.8, 0.05 | 79.0 | 0.24 | 3344 |
| 250-1000-2000-4000 | threshold | 0.75 | 78.8 | 0.48 | 3349 |
| 250-2000-4000 | threshold | 0.6 | 78.8 | 0.48 | 3403 |
| 500-2000-4000 | threshold | 0.7 | 78.8 | 0.40 | 3443 |
| 250-1000-2000-4000 | giveup | 0.8, 0.02 | 78.9 | 0.32 | 3462 |
| 250-2000-4000 | giveup | 0.7, 0.02 | 78.9 | 0.32 | 3513 |
| 500-2000-4000 | giveup | 0.75, 0.02 | 79.0 | 0.24 | 3530 |
| 500-2000-4000 | mondrian | λ per group = 0.75/0.8/0.7 | 79.2 | 0.00 | 3584 |
| 250-1000-2000-4000 | mdp | 0 | 79.0 | 0.24 | 3665 |
| 500-2000-4000 | mdp | 0 | 79.2 | 0.00 | 3711 |
| x4 | threshold | 0.5 | 78.7 | 0.48 | 3810 |
| 250-1000-4000 | threshold | 0.5 | 78.7 | 0.48 | 3810 |
| 250-2000-4000 | mdp | 0 | 78.9 | 0.32 | 3824 |
| x4 | giveup | 0.6, 0 | 78.8 | 0.32 | 3897 |
| 250-1000-4000 | giveup | 0.6, 0 | 78.8 | 0.32 | 3897 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.98/0.85/0.7 | 79.2 | 0.00 | 4068 |
| x4 | mdp | 0 | 78.8 | 0.32 | 4071 |
| 250-1000-4000 | mdp | 0 | 78.8 | 0.32 | 4071 |
| x4 | mondrian | λ per group = 0.94/0.75/0.5 | 79.2 | 0.00 | 4179 |
| 250-1000-4000 | mondrian | λ per group = 0.94/0.75/0.5 | 79.2 | 0.00 | 4179 |
| doubling | mondrian | λ per group = 0.995/0.88/0.8 | 79.2 | 0.00 | 4465 |
| 250-2000-4000 | mondrian | λ per group = 0.88/0.97/0.5 | 79.2 | 0.00 | 4669 |
| 500-4000 | giveup | 0.5, 0.3 | 78.9 | 0.24 | 4864 |
| 250-500-4000 | giveup | 0.5, 0.2 | 79.1 | 0.08 | 4910 |
| 500-4000 | threshold | 0.5 | 79.2 | 0.00 | 5101 |
| 500-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 79.2 | 0.00 | 5101 |
| 250-500-4000 | threshold | 0.5 | 79.2 | 0.00 | 5134 |
| 250-500-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 79.2 | 0.00 | 5134 |
| 250-500-4000 | mdp | 0 | 79.1 | 0.08 | 5186 |
| 500-4000 | mdp | 0 | 79.2 | 0.00 | 5229 |
| 250-4000 | giveup | 0.5, 0.2 | 78.9 | 0.24 | 5374 |
| full | threshold | 0.5 | 79.2 | 0.00 | 5552 |
| full | giveup | 0.5, 0 | 79.2 | 0.00 | 5552 |
| full | mondrian | λ per group = 0.5/0.5/0.5 | 79.2 | 0.00 | 5552 |
| 250-4000 | threshold | 0.5 | 79.2 | 0.00 | 5559 |
| 250-4000 | mdp | 0 | 79.2 | 0.00 | 5559 |
| 250-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 79.2 | 0.00 | 5559 |
| doubling | mdp | -1 | 79.2 | 0.00 | 7295 |

Selected on validation: marginal = `doubling` / threshold; group-conditional = `500-2000-4000` / mondrian.


### TurboReg, kitti_test test (555 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: doubling / threshold | 91.17 | 2881 | +1.08 [+1.80] | False | 1.98× [1.81, 2.16] | 0.0312 | 1.08 |
| mondrian: 500-2000-4000 / mondrian | 91.71 | 3196 | +0.54 [+1.08] | False | 1.78× [1.67, 1.92] | 0.25 | 0.54 |
| fixed budget N=250 (single run) | 1.08 | 8 | | | | | |
| fixed budget N=500 (single run) | 8.65 | 50 | | | | | |
| fixed budget N=1000 (single run) | 40.54 | 242 | | | | | |
| fixed budget N=2000 (single run) | 75.32 | 1399 | | | | | |
| fixed budget N=4000 (single run) | 92.25 | 5697 | | | | | |
