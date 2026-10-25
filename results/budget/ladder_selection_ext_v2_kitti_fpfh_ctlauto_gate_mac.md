# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## MAC

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1238 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 500-2000-4000 | giveup | 0.5, 0.15 | 0.33 | 3007 |
| 250-1000-2000-4000 | giveup | 0.6, 0.02 | 0.00 | 3671 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.5/0.6/0.6 | 0.00 | 3753 |
| doubling | giveup | 0.6, 0.02 | 0.33 | 3783 |
| 250-1000-2000-4000 | threshold | 0.6 | 0.00 | 3796 |
| doubling | threshold | 0.6 | 0.33 | 3965 |
| 250-2000-4000 | giveup | 0.5, 0.02 | 0.33 | 3982 |
| 500-2000-4000 | threshold | 0.5 | 0.00 | 3995 |
| 500-2000-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 3995 |
| 250-2000-4000 | threshold | 0.5 | 0.00 | 4320 |
| 250-2000-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 4320 |
| doubling | mondrian | λ per group = 0.88/0.6/0.6 | 0.00 | 4336 |
| x4 | giveup | 0.5, 0.05 | 0.33 | 5135 |
| 250-1000-4000 | giveup | 0.5, 0.05 | 0.33 | 5135 |
| x4 | threshold | 0.5 | 0.00 | 5705 |
| x4 | mdp | 0 | 0.00 | 5705 |
| x4 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 5705 |
| 250-1000-4000 | threshold | 0.5 | 0.00 | 5705 |
| 250-1000-4000 | mdp | 0 | 0.00 | 5705 |
| 250-1000-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 5705 |
| 500-4000 | giveup | 0.6, 0.15 | 0.33 | 6987 |
| 250-500-4000 | giveup | 0.8, 0.05 | 0.33 | 7239 |
| 500-4000 | threshold | 0.5 | 0.33 | 7444 |
| 500-4000 | mondrian | λ per group = 0.5/0.5/0.6 | 0.00 | 7488 |
| 250-4000 | giveup | 0.5, 0.2 | 0.33 | 7552 |
| 250-500-4000 | threshold | 0.5 | 0.33 | 7568 |
| 250-500-4000 | mondrian | λ per group = 0.8/0.5/0.5 | 0.00 | 7610 |
| 500-4000 | mdp | 0 | 0.00 | 7784 |
| full | threshold | 1.01 | 0.00 | 8188 |
| full | mondrian | never stop early | 0.00 | 8188 |
| 250-4000 | threshold | 0.5 | 0.00 | 8250 |
| 250-4000 | mdp | 0 | 0.00 | 8250 |
| 250-4000 | mondrian | λ per group = 0.5/0.5/0.5 | 0.00 | 8250 |
| 250-500-4000 | mdp | -1 | 0.00 | 8332 |
| 250-2000-4000 | mdp | -1 | 0.00 | 9716 |
| 500-2000-4000 | mdp | -1 | 0.00 | 9736 |
| 250-1000-2000-4000 | mdp | -1 | 0.00 | 10045 |
| doubling | mdp | -1 | 0.00 | 10127 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 500-2000-4000 / giveup | full / threshold (fallback) | 1.01 | 79.6 | 0.00 | 8061 |
| mondrian | 250-1000-2000-4000 / mondrian | 250-1000-2000-4000 / mondrian | λ per group = 0.92/0.99/0.8 | 79.6 | 0.00 | 6406 |

### MAC, kitti_raw_blind test (1310 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 64.50 | 11404 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: 250-1000-2000-4000 / mondrian | 64.50 | 9832 | +0.00 [+0.00] | True | 1.16× [1.13, 1.20] | 1 | 0.00 |
| fixed budget N=250 (single run) | 0.31 | 64 | | | | | |
| fixed budget N=500 (single run) | 4.12 | 108 | | | | | |
| fixed budget N=1000 (single run) | 16.95 | 472 | | | | | |
| fixed budget N=2000 (single run) | 40.53 | 2072 | | | | | |
| fixed budget N=4000 (single run) | 64.50 | 11404 | | | | | |

### MAC, kitti_test test (555 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 92.79 | 14616 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: 250-1000-2000-4000 / mondrian | 92.79 | 10799 | +0.00 [+0.00] | True | 1.35× [1.28, 1.44] | 1 | 0.00 |
| fixed budget N=250 (single run) | 0.54 | 108 | | | | | |
| fixed budget N=500 (single run) | 6.85 | 155 | | | | | |
| fixed budget N=1000 (single run) | 36.22 | 612 | | | | | |
| fixed budget N=2000 (single run) | 73.69 | 2690 | | | | | |
| fixed budget N=4000 (single run) | 92.79 | 14616 | | | | | |
