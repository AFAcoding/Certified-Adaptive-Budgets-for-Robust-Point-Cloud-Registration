# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## SC²-PCR

Validation, certified operating points (cheapest first):

| ladder | policy | parameters | val RR % | val risk % | val mean time (ms) |
|---|---|---|---|---|---|
| 500-4000 | threshold | 0.98 | 93.1 | 0.00 | 610 |
| 250-500-4000 | threshold | 0.99 | 92.8 | 0.00 | 901 |
| full | threshold | 0.5 | 92.8 | 0.00 | 3906 |
| full | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 3906 |
| 250-4000 | threshold | 1.01 | 92.8 | 0.00 | 3992 |
| 250-4000 | mdp | -1 | 92.8 | 0.00 | 3992 |
| 250-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 3992 |
| 500-4000 | mdp | -1 | 92.8 | 0.00 | 4062 |
| 500-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 4062 |
| 250-500-4000 | mdp | -1 | 92.8 | 0.00 | 4106 |
| 250-500-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 4106 |
| x4 | threshold | 1.01 | 92.8 | 0.00 | 4304 |
| x4 | mdp | -1 | 92.8 | 0.00 | 4304 |
| x4 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 4304 |
| 250-1000-4000 | threshold | 1.01 | 92.8 | 0.00 | 4304 |
| 250-1000-4000 | mdp | -1 | 92.8 | 0.00 | 4304 |
| 250-1000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 4304 |
| 250-2000-4000 | threshold | 1.01 | 92.8 | 0.00 | 5013 |
| 250-2000-4000 | mdp | -1 | 92.8 | 0.00 | 5013 |
| 250-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 5013 |
| 500-2000-4000 | threshold | 1.01 | 92.8 | 0.00 | 5083 |
| 500-2000-4000 | mdp | -1 | 92.8 | 0.00 | 5083 |
| 500-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 5083 |
| 250-1000-2000-4000 | threshold | 1.01 | 92.8 | 0.00 | 5325 |
| 250-1000-2000-4000 | mdp | -1 | 92.8 | 0.00 | 5325 |
| 250-1000-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 5325 |
| doubling | threshold | 1.01 | 92.8 | 0.00 | 5439 |
| doubling | mdp | -1 | 92.8 | 0.00 | 5439 |
| doubling | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 5439 |

Selected on validation: marginal = `500-4000` / threshold; group-conditional = `full` / mondrian.


### SC²-PCR, fcgf_kitti_test test (278 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 500-4000 / threshold | 93.88 | 645 | +1.08 [+2.16] | False | 6.25× [5.02, 8.02] | 0.25 | 1.08 |
| mondrian: full / mondrian | 94.96 | 4035 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 93.88 | 116 | | | | | |
| fixed budget N=500 (single run) | 93.53 | 194 | | | | | |
| fixed budget N=1000 (single run) | 94.60 | 422 | | | | | |
| fixed budget N=2000 (single run) | 94.24 | 1183 | | | | | |
| fixed budget N=4000 (single run) | 94.96 | 4035 | | | | | |

## TurboReg

Validation, certified operating points (cheapest first):

| ladder | policy | parameters | val RR % | val risk % | val mean time (ms) |
|---|---|---|---|---|---|
| full | threshold | 0.5 | 92.8 | 0.00 | 5521 |
| full | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 5521 |
| 250-4000 | threshold | 1.01 | 92.8 | 0.00 | 5724 |
| 250-4000 | mdp | -1 | 92.8 | 0.00 | 5724 |
| 250-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 5724 |
| 500-4000 | threshold | 1.01 | 92.8 | 0.00 | 5858 |
| 500-4000 | mdp | -1 | 92.8 | 0.00 | 5858 |
| 500-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 5858 |
| 250-500-4000 | threshold | 1.01 | 92.8 | 0.00 | 6019 |
| 250-500-4000 | mdp | -1 | 92.8 | 0.00 | 6019 |
| 250-500-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 6019 |
| x4 | threshold | 1.01 | 92.8 | 0.00 | 6373 |
| x4 | mdp | -1 | 92.8 | 0.00 | 6373 |
| x4 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 6373 |
| 250-1000-4000 | threshold | 1.01 | 92.8 | 0.00 | 6373 |
| 250-1000-4000 | mdp | -1 | 92.8 | 0.00 | 6373 |
| 250-1000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 6373 |
| 500-2000-4000 | mdp | 0 | 92.8 | 0.00 | 7332 |
| 250-2000-4000 | threshold | 1.01 | 92.8 | 0.00 | 7401 |
| 250-2000-4000 | mdp | -1 | 92.8 | 0.00 | 7401 |
| 250-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 7401 |
| 500-2000-4000 | threshold | 1.01 | 92.8 | 0.00 | 7534 |
| 500-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 7534 |
| 250-1000-2000-4000 | threshold | 1.01 | 92.8 | 0.00 | 8050 |
| 250-1000-2000-4000 | mdp | -1 | 92.8 | 0.00 | 8050 |
| 250-1000-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 8050 |
| doubling | threshold | 1.01 | 92.8 | 0.00 | 8344 |
| doubling | mdp | -1 | 92.8 | 0.00 | 8344 |
| doubling | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 8344 |

Selected on validation: marginal = `full` / threshold; group-conditional = `full` / mondrian.


### TurboReg, fcgf_kitti_test test (278 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 94.96 | 6617 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 94.96 | 6617 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 93.53 | 203 | | | | | |
| fixed budget N=500 (single run) | 93.17 | 324 | | | | | |
| fixed budget N=1000 (single run) | 94.24 | 666 | | | | | |
| fixed budget N=2000 (single run) | 94.24 | 1766 | | | | | |
| fixed budget N=4000 (single run) | 94.96 | 6617 | | | | | |
