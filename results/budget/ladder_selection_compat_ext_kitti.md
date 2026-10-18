# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## SC²-PCR

Validation, certified operating points (cheapest first):

| ladder | policy | parameters | val RR % | val risk % | val mean time (ms) |
|---|---|---|---|---|---|
| 500-2000-4000 | giveup | 0.5, 0.05 | 79.2 | 0.24 | 3208 |
| 500-2000-4000 | threshold | 0.5 | 79.2 | 0.24 | 3341 |
| 250-2000-4000 | threshold | 0.6 | 78.9 | 0.48 | 3414 |
| 250-2000-4000 | giveup | 0.7, 0.1 | 79.0 | 0.32 | 3469 |
| 250-1000-2000-4000 | threshold | 0.6 | 78.8 | 0.57 | 3481 |
| 250-1000-2000-4000 | giveup | 0.7, 0.1 | 79.2 | 0.32 | 3530 |
| 250-2000-4000 | mdp | 0 | 78.9 | 0.40 | 3549 |
| 250-2000-4000 | mondrian | λ per group = 0.75/0.6/0.6 | 79.2 | 0.00 | 3585 |
| 250-1000-2000-4000 | mdp | 0 | 78.8 | 0.57 | 3624 |
| 500-2000-4000 | mondrian | λ per group = 0.7/0.5/0.6 | 79.2 | 0.00 | 3670 |
| x4 | giveup | 0.6, 0.1 | 79.2 | 0.32 | 3675 |
| 250-1000-4000 | giveup | 0.6, 0.1 | 79.2 | 0.32 | 3675 |
| x4 | threshold | 0.5 | 78.8 | 0.57 | 3701 |
| 250-1000-4000 | threshold | 0.5 | 78.8 | 0.57 | 3701 |
| doubling | giveup | 0.7, 0.02 | 79.2 | 0.24 | 3715 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.7/0.7/0.7 | 79.3 | 0.00 | 3767 |
| doubling | threshold | 0.7 | 79.2 | 0.24 | 3824 |
| x4 | mondrian | λ per group = 0.75/0.75/0.5 | 79.3 | 0.00 | 3884 |
| 250-1000-4000 | mondrian | λ per group = 0.75/0.75/0.5 | 79.3 | 0.00 | 3884 |
| 250-500-4000 | giveup | 0.5, 0.02 | 79.0 | 0.32 | 3938 |
| 500-4000 | giveup | 0.5, 0.2 | 79.1 | 0.32 | 3951 |
| 250-500-4000 | threshold | 0.5 | 79.0 | 0.32 | 4001 |
| doubling | mondrian | λ per group = 0.75/0.75/0.75 | 79.3 | 0.00 | 4027 |
| 250-4000 | giveup | 0.5, 0.1 | 79.2 | 0.16 | 4083 |
| 250-500-4000 | mondrian | λ per group = 0.8/0.5/0.5 | 79.2 | 0.00 | 4100 |
| 500-4000 | threshold | 0.5 | 79.2 | 0.08 | 4140 |
| 500-4000 | mondrian | λ per group = 0.5/0.6/0.5 | 79.2 | 0.00 | 4144 |
| 500-2000-4000 | mdp | 0 | 78.9 | 0.32 | 4179 |
| 250-4000 | threshold | 0.5 | 79.2 | 0.00 | 4215 |
| 250-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 79.2 | 0.00 | 4215 |
| doubling | mdp | 0 | 79.1 | 0.16 | 4226 |
| 250-4000 | mdp | 0 | 79.2 | 0.00 | 4312 |
| 500-4000 | mdp | 0 | 79.2 | 0.00 | 4339 |
| full | threshold | 0.5 | 79.2 | 0.00 | 4450 |
| full | giveup | 0.5, 0 | 79.2 | 0.00 | 4450 |
| full | mondrian | λ per group = 0.5/0.5/0.5 | 79.2 | 0.00 | 4450 |
| 250-500-4000 | mdp | -1 | 79.2 | 0.00 | 4684 |
| x4 | mdp | -1 | 79.2 | 0.00 | 4925 |
| 250-1000-4000 | mdp | -1 | 79.2 | 0.00 | 4925 |

Selected on validation: marginal = `500-2000-4000` / giveup; group-conditional = `250-2000-4000` / mondrian.


### SC²-PCR, kitti_test test (555 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-2000-4000 / giveup | 91.17 | 2936 | +1.08 [+1.80] | False | 1.46× [1.37, 1.57] | 0.0312 | 1.08 |
| mondrian: 250-2000-4000 / mondrian | 92.25 | 3312 | +0.00 [+0.36] | True | 1.30× [1.23, 1.38] | 1 | 0.18 |
| fixed budget N=250 (single run) | 12.79 | 92 | | | | | |
| fixed budget N=500 (single run) | 20.72 | 173 | | | | | |
| fixed budget N=1000 (single run) | 39.28 | 407 | | | | | |
| fixed budget N=2000 (single run) | 72.43 | 1210 | | | | | |
| fixed budget N=4000 (single run) | 92.25 | 4294 | | | | | |

## TurboReg

Validation, certified operating points (cheapest first):

| ladder | policy | parameters | val RR % | val risk % | val mean time (ms) |
|---|---|---|---|---|---|
| 250-2000-4000 | threshold | 0.6 | 78.8 | 0.48 | 4226 |
| 500-2000-4000 | giveup | 0.6, 0.05 | 79.2 | 0.24 | 4239 |
| 250-2000-4000 | giveup | 0.7, 0.05 | 79.1 | 0.24 | 4360 |
| 250-2000-4000 | mondrian | λ per group = 0.8/0.6/0.5 | 79.2 | 0.00 | 4369 |
| 500-2000-4000 | threshold | 0.6 | 79.1 | 0.24 | 4394 |
| 250-1000-2000-4000 | giveup | 0.7, 0.1 | 79.3 | 0.24 | 4429 |
| x4 | threshold | 0.5 | 78.9 | 0.48 | 4523 |
| 250-1000-4000 | threshold | 0.5 | 78.9 | 0.48 | 4523 |
| x4 | giveup | 0.6, 0.05 | 79.2 | 0.16 | 4582 |
| 250-1000-4000 | giveup | 0.6, 0.05 | 79.2 | 0.16 | 4582 |
| doubling | giveup | 0.7, 0.02 | 79.2 | 0.24 | 4607 |
| x4 | mdp | 0 | 78.9 | 0.48 | 4619 |
| 250-1000-4000 | mdp | 0 | 78.9 | 0.48 | 4619 |
| 250-1000-2000-4000 | mdp | 0 | 78.9 | 0.40 | 4645 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.7/0.6/0.7 | 79.4 | 0.00 | 4667 |
| 500-2000-4000 | mondrian | λ per group = 0.75/0.7/0.6 | 79.2 | 0.00 | 4686 |
| 250-1000-2000-4000 | threshold | 0.7 | 79.4 | 0.00 | 4708 |
| x4 | mondrian | λ per group = 0.7/0.7/0.5 | 79.2 | 0.00 | 4724 |
| 250-1000-4000 | mondrian | λ per group = 0.7/0.7/0.5 | 79.2 | 0.00 | 4724 |
| doubling | threshold | 0.7 | 79.2 | 0.24 | 4734 |
| doubling | mdp | 0 | 79.0 | 0.32 | 4775 |
| 250-500-4000 | giveup | 0.5, 0.02 | 78.8 | 0.32 | 4849 |
| 250-500-4000 | threshold | 0.5 | 78.8 | 0.32 | 4916 |
| 500-4000 | giveup | 0.5, 0.1 | 78.9 | 0.24 | 4945 |
| doubling | mondrian | λ per group = 0.8/0.7/0.75 | 79.4 | 0.00 | 5034 |
| 250-4000 | giveup | 0.5, 0.1 | 78.9 | 0.24 | 5049 |
| 250-500-4000 | mondrian | λ per group = 0.88/0.5/0.5 | 79.2 | 0.00 | 5056 |
| 500-4000 | threshold | 0.5 | 79.1 | 0.08 | 5076 |
| 500-4000 | mondrian | λ per group = 0.5/0.75/0.5 | 79.2 | 0.00 | 5095 |
| 250-4000 | threshold | 0.5 | 79.2 | 0.00 | 5208 |
| 250-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 79.2 | 0.00 | 5208 |
| 500-2000-4000 | mdp | 0 | 78.8 | 0.32 | 5220 |
| 250-4000 | mdp | 0 | 79.2 | 0.00 | 5366 |
| full | threshold | 0.5 | 79.2 | 0.00 | 5552 |
| full | giveup | 0.5, 0 | 79.2 | 0.00 | 5552 |
| full | mondrian | λ per group = 0.5/0.5/0.5 | 79.2 | 0.00 | 5552 |
| 500-4000 | mdp | -1 | 79.2 | 0.00 | 5793 |
| 250-500-4000 | mdp | -1 | 79.2 | 0.00 | 5856 |
| 250-2000-4000 | mdp | -1 | 79.2 | 0.00 | 7280 |

Selected on validation: marginal = `250-2000-4000` / threshold; group-conditional = `250-2000-4000` / mondrian.


### TurboReg, kitti_test test (555 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-2000-4000 / threshold | 90.81 | 4044 | +1.44 [+2.34] | False | 1.41× [1.33, 1.50] | 0.0215 | 1.62 |
| mondrian: 250-2000-4000 / mondrian | 91.71 | 4201 | +0.54 [+1.26] | False | 1.36× [1.28, 1.44] | 0.375 | 0.72 |
| fixed budget N=250 (single run) | 14.23 | 103 | | | | | |
| fixed budget N=500 (single run) | 22.34 | 226 | | | | | |
| fixed budget N=1000 (single run) | 42.34 | 574 | | | | | |
| fixed budget N=2000 (single run) | 71.53 | 1631 | | | | | |
| fixed budget N=4000 (single run) | 92.25 | 5697 | | | | | |
