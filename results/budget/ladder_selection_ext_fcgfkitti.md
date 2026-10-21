# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## SC²-PCR

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 276 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-1000-2000-4000 | giveup | 0.6, 0.1 | 0.00 | 2476 |
| 250-2000-4000 | giveup | 0.6, 0.2 | 0.00 | 2489 |
| 250-1000-2000-4000 | threshold | 0.6 | 0.00 | 2542 |
| 250-2000-4000 | threshold | 0.6 | 0.00 | 2594 |
| 500-2000-4000 | giveup | 0.7, 0.1 | 0.00 | 2611 |
| 500-2000-4000 | threshold | 0.7 | 0.00 | 2626 |
| doubling | giveup | 0.8, 0.05 | 0.00 | 2798 |
| doubling | threshold | 0.8 | 0.00 | 2830 |
| 250-2000-4000 | mdp | 0 | 0.00 | 2990 |
| x4 | giveup | 0.5, 0.1 | 0.00 | 3017 |
| 250-1000-4000 | giveup | 0.5, 0.1 | 0.00 | 3017 |
| x4 | threshold | 0.5 | 0.00 | 3048 |
| 250-1000-4000 | threshold | 0.5 | 0.00 | 3048 |
| x4 | mdp | 0 | 0.00 | 3102 |
| 250-1000-4000 | mdp | 0 | 0.00 | 3102 |
| 500-4000 | threshold | 0.5 | 0.00 | 3908 |
| 500-4000 | giveup | 0.5, 0 | 0.00 | 3908 |
| 250-500-4000 | threshold | 0.6 | 0.00 | 3963 |
| 250-500-4000 | giveup | 0.6, 0 | 0.00 | 3963 |
| 500-4000 | mdp | 0 | 0.00 | 3994 |
| 250-500-4000 | mdp | 0 | 0.00 | 4079 |
| full | threshold | 1.01 | 0.00 | 4219 |
| full | mondrian | never stop early | 0.00 | 4219 |
| 250-4000 | giveup | 0.5, 0.1 | 0.00 | 4260 |
| 250-4000 | threshold | 0.5 | 0.00 | 4275 |
| 250-4000 | mdp | 0 | 0.00 | 4275 |
| 250-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 4275 |
| 500-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 4368 |
| 250-500-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 4423 |
| x4 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 4666 |
| 250-1000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 4666 |
| 250-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 5469 |
| 500-2000-4000 | mdp | -1 | 0.00 | 5562 |
| 500-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 5562 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 5860 |
| 250-1000-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 5860 |
| doubling | mdp | -1 | 0.00 | 6008 |
| doubling | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 6008 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-1000-2000-4000 / giveup | full / threshold (fallback) | 1.01 | 92.8 | 0.00 | 3906 |
| mondrian | full / mondrian | full / mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 3906 |

### SC²-PCR, fcgf_kitti_test test (278 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 94.96 | 4035 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 94.96 | 4035 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 91.73 | 64 | | | | | |
| fixed budget N=500 (single run) | 92.45 | 153 | | | | | |
| fixed budget N=1000 (single run) | 93.53 | 390 | | | | | |
| fixed budget N=2000 (single run) | 93.88 | 1158 | | | | | |
| fixed budget N=4000 (single run) | 94.96 | 4035 | | | | | |

## TurboReg

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 276 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-1000-2000-4000 | threshold | 0.75 | 0.00 | 3012 |
| 250-1000-2000-4000 | giveup | 0.75, 0 | 0.00 | 3012 |
| doubling | threshold | 0.85 | 0.00 | 3199 |
| doubling | giveup | 0.85, 0 | 0.00 | 3199 |
| 250-1000-2000-4000 | mdp | 0 | 0.00 | 3273 |
| 500-2000-4000 | giveup | 0.8, 0.05 | 0.00 | 3363 |
| 500-2000-4000 | threshold | 0.8 | 0.00 | 3399 |
| x4 | giveup | 0.6, 0.05 | 0.00 | 3442 |
| 250-1000-4000 | giveup | 0.6, 0.05 | 0.00 | 3442 |
| 500-2000-4000 | mdp | 0 | 0.00 | 3455 |
| x4 | threshold | 0.6 | 0.00 | 3515 |
| 250-1000-4000 | threshold | 0.6 | 0.00 | 3515 |
| 250-2000-4000 | giveup | 0.85, 0.05 | 0.00 | 3564 |
| x4 | mdp | 0 | 0.00 | 3568 |
| 250-1000-4000 | mdp | 0 | 0.00 | 3568 |
| 250-2000-4000 | threshold | 0.85 | 0.00 | 3599 |
| 250-500-4000 | giveup | 0.6, 0.2 | 0.00 | 4715 |
| 500-4000 | giveup | 0.75, 0.2 | 0.00 | 4848 |
| 250-500-4000 | threshold | 0.6 | 0.00 | 4877 |
| 500-4000 | mdp | 0 | 0.00 | 4902 |
| 500-4000 | threshold | 0.75 | 0.00 | 4920 |
| 250-4000 | giveup | 0.5, 0.2 | 0.00 | 5170 |
| full | threshold | 1.01 | 0.00 | 5253 |
| full | mondrian | never stop early | 0.00 | 5253 |
| 250-4000 | threshold | 0.5 | 0.00 | 5260 |
| 250-4000 | mdp | 0 | 0.00 | 5260 |
| 250-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 5260 |
| 500-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 5300 |
| 250-500-4000 | mdp | -1 | 0.00 | 5307 |
| 250-500-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 5307 |
| x4 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 5516 |
| 250-1000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 5516 |
| 250-2000-4000 | mdp | -1 | 0.00 | 6694 |
| 250-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 6694 |
| 500-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 6734 |
| 250-1000-2000-4000 | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 6950 |
| doubling | mdp | -1 | 0.00 | 6998 |
| doubling | mondrian | λ per group = 1.01/1.01/1.01 | 0.00 | 6998 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-1000-2000-4000 / threshold | 250-1000-2000-4000 / threshold | 0.98 | 92.8 | 0.00 | 7704 |
| mondrian | full / mondrian | full / mondrian | λ per group = 1.01/1.01/1.01 | 92.8 | 0.00 | 5521 |

### TurboReg, fcgf_kitti_test test (278 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-1000-2000-4000 / threshold | 94.96 | 8653 | +0.00 [+0.00] | True | 0.76× [0.75, 0.79] | 1 | 0.00 |
| mondrian: full / mondrian | 94.96 | 6617 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 91.37 | 164 | | | | | |
| fixed budget N=500 (single run) | 92.09 | 273 | | | | | |
| fixed budget N=1000 (single run) | 93.53 | 606 | | | | | |
| fixed budget N=2000 (single run) | 93.88 | 1661 | | | | | |
| fixed budget N=4000 (single run) | 94.96 | 6617 | | | | | |
