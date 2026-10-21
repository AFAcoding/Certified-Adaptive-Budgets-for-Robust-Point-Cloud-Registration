# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).

Compatibility-ordered budgets: a truncated budget takes the top-N correspondences by second-order compatibility with the 100 most distinctive ones; the reordering time is charged to every configuration that truncates (adaptive and fixed), never to the full run.


## SC²-PCR

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 276 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| x4 | giveup | 0.6, 0.02 | 0.00 | 3609 |
| 250-1000-4000 | giveup | 0.6, 0.02 | 0.00 | 3609 |
| 250-2000-4000 | giveup | 0.85, 0.02 | 0.00 | 3631 |
| x4 | threshold | 0.6 | 0.00 | 3642 |
| 250-1000-4000 | threshold | 0.6 | 0.00 | 3642 |
| 250-500-4000 | mdp | 0 | 0.00 | 3650 |
| 250-2000-4000 | threshold | 0.85 | 0.00 | 3709 |
| 500-2000-4000 | threshold | 0.8 | 0.00 | 3751 |
| 500-2000-4000 | giveup | 0.8, 0 | 0.00 | 3751 |
| 250-500-4000 | threshold | 0.5 | 0.00 | 3792 |
| 250-500-4000 | giveup | 0.5, 0 | 0.00 | 3792 |
| 500-4000 | threshold | 0.5 | 0.00 | 3855 |
| 500-4000 | giveup | 0.5, 0 | 0.00 | 3855 |
| 250-1000-2000-4000 | giveup | 0.88, 0.02 | 0.00 | 3953 |
| 250-4000 | giveup | 0.5, 0.02 | 0.00 | 3953 |
| 250-4000 | threshold | 0.5 | 0.00 | 3968 |
| 250-1000-2000-4000 | threshold | 0.88 | 0.00 | 4024 |
| 500-4000 | mdp | 0 | 0.00 | 4119 |
| 250-4000 | mdp | 0 | 0.00 | 4134 |
| doubling | threshold | 0.88 | 0.00 | 4146 |
| doubling | giveup | 0.88, 0 | 0.00 | 4146 |
| full | threshold | 1.01 | 0.00 | 4219 |
| full | mondrian | never stop early | 0.00 | 4219 |
| 250-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 4314 |
| 500-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 4391 |
| 250-500-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 4441 |
| x4 | mdp | -1 | 0.00 | 4670 |
| x4 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 4670 |
| 250-1000-4000 | mdp | -1 | 0.00 | 4670 |
| 250-1000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 4670 |
| 250-2000-4000 | mdp | -1 | 0.00 | 5454 |
| 250-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 5454 |
| 500-2000-4000 | mdp | -1 | 0.00 | 5531 |
| 500-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 5531 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 5810 |
| 250-1000-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 5810 |
| doubling | mdp | -1 | 0.00 | 5937 |
| doubling | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 5937 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | x4 / giveup | full / threshold (fallback) | 1.01 | 92.8 | 0.00 | 3906 |
| mondrian | full / mondrian | full / mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 3906 |

### SC²-PCR, fcgf_kitti_test test (278 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 94.96 | 4035 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 94.96 | 4035 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 93.88 | 116 | | | | | |
| fixed budget N=500 (single run) | 93.53 | 194 | | | | | |
| fixed budget N=1000 (single run) | 94.60 | 422 | | | | | |
| fixed budget N=2000 (single run) | 94.24 | 1183 | | | | | |
| fixed budget N=4000 (single run) | 94.96 | 4035 | | | | | |

## TurboReg

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 276 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-2000-4000 | giveup | 0.8, 0.02 | 0.00 | 4590 |
| 250-2000-4000 | threshold | 0.8 | 0.00 | 4663 |
| 500-4000 | giveup | 0.5, 0.02 | 0.00 | 4731 |
| 500-2000-4000 | giveup | 0.8, 0.02 | 0.00 | 4744 |
| 500-4000 | threshold | 0.5 | 0.00 | 4747 |
| 250-500-4000 | threshold | 0.6 | 0.00 | 4787 |
| 250-500-4000 | giveup | 0.6, 0 | 0.00 | 4787 |
| 500-2000-4000 | threshold | 0.8 | 0.00 | 4818 |
| 250-4000 | giveup | 0.5, 0.02 | 0.00 | 4827 |
| 250-4000 | threshold | 0.5 | 0.00 | 4860 |
| x4 | threshold | 0.7 | 0.00 | 4941 |
| x4 | giveup | 0.7, 0 | 0.00 | 4941 |
| 250-1000-4000 | threshold | 0.7 | 0.00 | 4941 |
| 250-1000-4000 | giveup | 0.7, 0 | 0.00 | 4941 |
| 250-4000 | mdp | 0 | 0.00 | 5074 |
| full | threshold | 1.01 | 0.00 | 5253 |
| full | mondrian | never stop early | 0.00 | 5253 |
| 250-1000-2000-4000 | threshold | 0.88 | 0.00 | 5357 |
| 250-1000-2000-4000 | giveup | 0.88, 0 | 0.00 | 5357 |
| 250-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 5371 |
| 500-4000 | mdp | -1 | 0.00 | 5504 |
| 500-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 5504 |
| doubling | threshold | 0.88 | 0.00 | 5520 |
| doubling | giveup | 0.88, 0 | 0.00 | 5520 |
| 250-500-4000 | mdp | -1 | 0.00 | 5578 |
| 250-500-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 5578 |
| x4 | mdp | -1 | 0.00 | 5941 |
| x4 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 5941 |
| 250-1000-4000 | mdp | -1 | 0.00 | 5941 |
| 250-1000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 5941 |
| 250-2000-4000 | mdp | -1 | 0.00 | 6977 |
| 250-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 6977 |
| 500-2000-4000 | mdp | -1 | 0.00 | 7110 |
| 500-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 7110 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 7547 |
| 250-1000-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 7547 |
| doubling | mdp | -1 | 0.00 | 7754 |
| doubling | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 7754 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-2000-4000 / giveup | full / threshold (fallback) | 1.01 | 92.8 | 0.00 | 5521 |
| mondrian | full / mondrian | full / mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 5521 |

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
