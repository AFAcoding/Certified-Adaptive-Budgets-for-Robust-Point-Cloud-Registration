# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## SC²-PCR

Validation, certified operating points (cheapest first):

| ladder | policy | parameters | val RR % | val risk % | val mean time (ms) |
|---|---|---|---|---|---|
| x4 | threshold | 0.7 | 92.8 | 0.00 | 2026 |
| 250-1000-4000 | threshold | 0.7 | 92.8 | 0.00 | 2026 |
| 250-500-4000 | threshold | 0.5 | 92.8 | 0.00 | 2635 |
| 500-4000 | threshold | 0.5 | 92.8 | 0.00 | 3162 |
| 250-2000-4000 | threshold | 0.5 | 92.8 | 0.00 | 3183 |
| 500-2000-4000 | threshold | 0.5 | 92.8 | 0.00 | 3512 |
| 250-4000 | threshold | 0.5 | 92.8 | 0.00 | 3699 |
| 250-1000-2000-4000 | threshold | 0.7 | 92.8 | 0.00 | 3809 |
| full | threshold | 0.5 | 92.8 | 0.00 | 3906 |
| full | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 3906 |
| 500-4000 | mdp | 0 | 92.8 | 0.00 | 3934 |
| 250-4000 | mdp | 0 | 92.8 | 0.00 | 3939 |
| 250-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 3939 |
| 250-500-4000 | mdp | 0 | 92.8 | 0.00 | 3953 |
| 500-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 4011 |
| 250-500-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 4044 |
| x4 | mdp | 0 | 92.8 | 0.00 | 4055 |
| 250-1000-4000 | mdp | 0 | 92.8 | 0.00 | 4055 |
| x4 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 4256 |
| 250-1000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 4256 |
| doubling | threshold | 0.85 | 92.8 | 0.00 | 4616 |
| 250-2000-4000 | mdp | 0 | 92.8 | 0.00 | 4731 |
| 500-2000-4000 | mdp | 0 | 92.8 | 0.00 | 4756 |
| 250-1000-2000-4000 | mdp | 0 | 92.8 | 0.00 | 4922 |
| 250-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 4990 |
| 500-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 5061 |
| 250-1000-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 5307 |
| doubling | mdp | -1 | 92.8 | 0.00 | 5412 |
| doubling | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 5412 |

Selected on validation: marginal = `x4` / threshold; group-conditional = `full` / mondrian.


### SC²-PCR, fcgf_kitti_test test (278 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: x4 / threshold | 93.53 | 2156 | +1.44 [+2.52] | False | 1.87× [1.68, 2.14] | 0.125 | 1.44 |
| mondrian: full / mondrian | 94.96 | 4035 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 91.73 | 64 | | | | | |
| fixed budget N=500 (single run) | 92.45 | 153 | | | | | |
| fixed budget N=1000 (single run) | 93.53 | 390 | | | | | |
| fixed budget N=2000 (single run) | 93.88 | 1158 | | | | | |
| fixed budget N=4000 (single run) | 94.96 | 4035 | | | | | |

## TurboReg

Validation, certified operating points (cheapest first):

| ladder | policy | parameters | val RR % | val risk % | val mean time (ms) |
|---|---|---|---|---|---|
| full | threshold | 0.5 | 92.8 | 0.00 | 5521 |
| full | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 5521 |
| 250-4000 | threshold | 0.5 | 92.8 | 0.00 | 5630 |
| 250-4000 | mdp | 0 | 92.8 | 0.00 | 5687 |
| 250-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 5687 |
| 500-4000 | mdp | 0 | 93.1 | 0.00 | 5712 |
| 500-4000 | threshold | 1.01 | 92.8 | 0.00 | 5809 |
| 500-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 5809 |
| 250-500-4000 | threshold | 1.01 | 92.8 | 0.00 | 5976 |
| 250-500-4000 | mdp | -1 | 92.8 | 0.00 | 5976 |
| 250-500-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 5976 |
| x4 | threshold | 1.01 | 92.8 | 0.00 | 6317 |
| x4 | mdp | -1 | 92.8 | 0.00 | 6317 |
| x4 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 6317 |
| 250-1000-4000 | threshold | 1.01 | 92.8 | 0.00 | 6317 |
| 250-1000-4000 | mdp | -1 | 92.8 | 0.00 | 6317 |
| 250-1000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 6317 |
| 250-2000-4000 | threshold | 0.5 | 93.1 | 0.00 | 7025 |
| 500-2000-4000 | mdp | 0 | 93.1 | 0.00 | 7105 |
| 250-2000-4000 | mdp | 0 | 92.8 | 0.00 | 7167 |
| 250-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 7330 |
| 500-2000-4000 | threshold | 1.01 | 92.8 | 0.00 | 7452 |
| 500-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 7452 |
| 250-1000-2000-4000 | threshold | 0.98 | 92.8 | 0.00 | 7704 |
| 250-1000-2000-4000 | mdp | -1 | 92.8 | 0.00 | 7959 |
| 250-1000-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 7959 |
| doubling | threshold | 1.01 | 92.8 | 0.00 | 8248 |
| doubling | mdp | -1 | 92.8 | 0.00 | 8248 |
| doubling | mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 8248 |

Selected on validation: marginal = `full` / threshold; group-conditional = `full` / mondrian.


### TurboReg, fcgf_kitti_test test (278 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 94.96 | 6617 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 94.96 | 6617 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 91.37 | 164 | | | | | |
| fixed budget N=500 (single run) | 92.09 | 273 | | | | | |
| fixed budget N=1000 (single run) | 93.53 | 606 | | | | | |
| fixed budget N=2000 (single run) | 93.88 | 1661 | | | | | |
| fixed budget N=4000 (single run) | 94.96 | 6617 | | | | | |
