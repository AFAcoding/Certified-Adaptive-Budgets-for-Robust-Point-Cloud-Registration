# Adaptive correspondence budgets: ladder/policy selection (validation) and test evaluation

Reference on test = a single full-budget run (N = 4,000), i.e. the standard estimator. Risk = fraction of pairs the full-budget estimator registers but the policy does not (target ≤ 1 %).


## SC²-PCR

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1107 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-4000 | threshold | 0.5 | 0.33 | 45 |
| 250-4000 | giveup | 0.5, 0 | 0.33 | 45 |
| 250-500-4000 | threshold | 0.7 | 0.33 | 46 |
| 250-500-4000 | giveup | 0.7, 0 | 0.33 | 46 |
| x4 | threshold | 0.7 | 0.33 | 47 |
| x4 | giveup | 0.7, 0 | 0.33 | 47 |
| 250-1000-4000 | threshold | 0.7 | 0.33 | 47 |
| 250-1000-4000 | giveup | 0.7, 0 | 0.33 | 47 |
| 250-1000-2000 | threshold | 0.98 | 0.33 | 47 |
| 250-1000-2000 | giveup | 0.98, 0 | 0.33 | 47 |
| 250-2000-4000 | threshold | 0.6 | 0.33 | 49 |
| 250-2000-4000 | giveup | 0.6, 0 | 0.33 | 49 |
| doubling | threshold | 0.75 | 0.33 | 51 |
| doubling | giveup | 0.75, 0 | 0.33 | 51 |
| 250-1000-2000-4000 | threshold | 0.7 | 0.33 | 51 |
| 250-1000-2000-4000 | giveup | 0.7, 0 | 0.33 | 51 |
| 250-500-1000-2000 | threshold | 0.99 | 0.33 | 59 |
| 250-500-1000-2000 | giveup | 0.99, 0 | 0.33 | 59 |
| 250-2000 | threshold | 0.98 | 0.33 | 65 |
| 250-2000 | giveup | 0.98, 0 | 0.33 | 65 |
| doubling | mondrian | λ per group = 0.99/0.5/0.5 | 0.00 | 73 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.99/0.5/0.5 | 0.00 | 88 |
| 500-2000-4000 | threshold | 0.5 | 0.33 | 96 |
| 500-2000-4000 | mdp | 30 | 0.33 | 96 |
| 500-2000-4000 | giveup | 0.5, 0 | 0.33 | 96 |
| 500-4000 | threshold | 0.5 | 0.33 | 96 |
| 500-4000 | mdp | 30 | 0.33 | 96 |
| 500-4000 | giveup | 0.5, 0 | 0.33 | 96 |
| 500-2000 | threshold | 0.5 | 0.33 | 96 |
| 500-2000 | mdp | 30 | 0.33 | 96 |
| 500-2000 | giveup | 0.5, 0 | 0.33 | 96 |
| 250-500-4000 | mondrian | λ per group = 0.99/0.5/0.5 | 0.00 | 102 |
| x4 | mondrian | λ per group = 0.99/0.5/0.5 | 0.00 | 109 |
| 250-1000-4000 | mondrian | λ per group = 0.99/0.5/0.5 | 0.00 | 109 |
| 250-2000-4000 | mondrian | λ per group = 0.99/0.5/0.5 | 0.00 | 150 |
| 250-4000 | mondrian | λ per group = 0.99/0.5/0.5 | 0.00 | 177 |
| 250-500-1000-2000 | mdp | 0 | 0.33 | 180 |
| 250-1000-2000 | mdp | 0 | 0.33 | 246 |
| fixed-1000 | threshold | 0.5 | 0.33 | 303 |
| fixed-1000 | giveup | 0.5, 0 | 0.33 | 303 |
| 250-2000 | mdp | 0 | 0.33 | 312 |
| 250-500-4000 | mdp | 0 | 0.33 | 440 |
| doubling | mdp | 0 | 0.33 | 486 |
| x4 | mdp | 0 | 0.33 | 510 |
| 250-1000-4000 | mdp | 0 | 0.33 | 510 |
| 250-1000-2000-4000 | mdp | 0 | 0.33 | 584 |
| 250-2000-4000 | mdp | 0 | 0.33 | 766 |
| fixed-2000 | threshold | 0.5 | 0.33 | 1020 |
| fixed-2000 | giveup | 0.5, 0 | 0.33 | 1020 |
| 250-4000 | mdp | 0 | 0.00 | 1179 |
| 500-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 1351 |
| 500-2000-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 1694 |
| full | threshold | 1.01 | 0.00 | 3721 |
| full | mondrian | never stop early | 0.00 | 3721 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-4000 / threshold | 250-4000 / threshold | 0.995 | 86.3 | 0.54 | 1514 |
| mondrian | doubling / mondrian | full / mondrian (fallback) | λ per group = 1.01/1.01/1.01 | 86.4 | 0.00 | 3926 |

### SC²-PCR, fcgfown_kitti_raw_blind test (203 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / threshold | 92.12 | 1236 | +0.49 [+1.48] | False | 3.23× [2.76, 3.90] | 1 | 0.49 |
| mondrian: full / mondrian | 92.61 | 3997 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 90.15 | 37 | | | | | |
| fixed budget N=500 (single run) | 90.64 | 115 | | | | | |
| fixed budget N=1000 (single run) | 90.64 | 335 | | | | | |
| fixed budget N=2000 (single run) | 91.63 | 1087 | | | | | |
| fixed budget N=4000 (single run) | 92.61 | 3997 | | | | | |

### SC²-PCR, fcgfown_kitti_test test (555 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: 250-4000 / threshold | 92.79 | 1164 | +0.72 [+1.26] | False | 3.38× [3.00, 3.91] | 0.125 | 0.72 |
| mondrian: full / mondrian | 93.51 | 3930 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 90.45 | 35 | | | | | |
| fixed budget N=500 (single run) | 91.53 | 105 | | | | | |
| fixed budget N=1000 (single run) | 92.43 | 319 | | | | | |
| fixed budget N=2000 (single run) | 93.15 | 1062 | | | | | |
| fixed budget N=4000 (single run) | 93.51 | 3930 | | | | | |

## TurboReg

Step 1, fitting pairs (300, out-of-fold controller): operating point of every candidate at the loss share the certificate can accept for 1107 calibration pairs (cheapest first):

| ladder | policy | parameters | fit risk % | fit mean time (ms) |
|---|---|---|---|---|
| 250-4000 | threshold | 0.6 | 0.33 | 193 |
| 250-4000 | giveup | 0.6, 0 | 0.33 | 193 |
| 250-500-4000 | threshold | 0.7 | 0.33 | 193 |
| 250-500-4000 | giveup | 0.7, 0 | 0.33 | 193 |
| x4 | threshold | 0.7 | 0.33 | 196 |
| x4 | giveup | 0.7, 0 | 0.33 | 196 |
| 250-1000-4000 | threshold | 0.7 | 0.33 | 196 |
| 250-1000-4000 | giveup | 0.7, 0 | 0.33 | 196 |
| 250-1000-2000 | threshold | 0.98 | 0.33 | 196 |
| 250-1000-2000 | giveup | 0.98, 0 | 0.33 | 196 |
| doubling | threshold | 0.8 | 0.33 | 201 |
| doubling | giveup | 0.8, 0 | 0.33 | 201 |
| 250-2000-4000 | threshold | 0.7 | 0.33 | 202 |
| 250-2000-4000 | giveup | 0.7, 0 | 0.33 | 202 |
| 250-1000-2000-4000 | threshold | 0.8 | 0.33 | 206 |
| 250-1000-2000-4000 | giveup | 0.8, 0 | 0.33 | 206 |
| 250-2000 | threshold | 0.98 | 0.33 | 209 |
| 250-2000 | giveup | 0.98, 0 | 0.33 | 209 |
| 250-500-1000-2000 | threshold | 0.99 | 0.33 | 223 |
| 250-500-1000-2000 | giveup | 0.99, 0 | 0.33 | 223 |
| doubling | mondrian | λ per group = 0.99/0.5/0.5 | 0.00 | 232 |
| 250-1000-2000-4000 | mondrian | λ per group = 0.99/0.5/0.5 | 0.00 | 249 |
| 250-500-4000 | mondrian | λ per group = 0.99/0.5/0.5 | 0.00 | 271 |
| x4 | mondrian | λ per group = 0.99/0.5/0.5 | 0.00 | 285 |
| 250-1000-4000 | mondrian | λ per group = 0.99/0.5/0.5 | 0.00 | 285 |
| 500-2000-4000 | threshold | 0.5 | 0.33 | 293 |
| 500-2000-4000 | mdp | 30 | 0.33 | 293 |
| 500-2000-4000 | giveup | 0.5, 0 | 0.33 | 293 |
| 500-4000 | threshold | 0.5 | 0.33 | 293 |
| 500-4000 | mdp | 30 | 0.33 | 293 |
| 500-4000 | giveup | 0.5, 0 | 0.33 | 293 |
| 500-2000 | threshold | 0.5 | 0.33 | 293 |
| 500-2000 | mdp | 30 | 0.33 | 293 |
| 500-2000 | giveup | 0.5, 0 | 0.33 | 293 |
| 250-2000-4000 | mondrian | λ per group = 0.99/0.5/0.5 | 0.00 | 335 |
| 250-4000 | mondrian | λ per group = 0.99/0.5/0.5 | 0.00 | 383 |
| 250-500-1000-2000 | mdp | 0 | 0.33 | 479 |
| 250-1000-2000 | mdp | 0 | 0.33 | 556 |
| 250-2000 | mdp | 0 | 0.33 | 600 |
| fixed-1000 | threshold | 0.5 | 0.33 | 637 |
| fixed-1000 | giveup | 0.5, 0 | 0.33 | 637 |
| 250-500-4000 | mdp | 0 | 0.33 | 777 |
| doubling | mdp | 0 | 0.33 | 891 |
| x4 | mdp | 0 | 0.33 | 908 |
| 250-1000-4000 | mdp | 0 | 0.33 | 908 |
| 250-1000-2000-4000 | mdp | 0 | 0.33 | 1057 |
| 250-2000-4000 | mdp | 0 | 0.33 | 1306 |
| fixed-2000 | threshold | 0.5 | 0.33 | 1648 |
| fixed-2000 | giveup | 0.5, 0 | 0.33 | 1648 |
| 250-4000 | mdp | 0 | 0.00 | 1793 |
| 500-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 2113 |
| 500-2000-4000 | mondrian | λ per group = 1.01/0.5/0.5 | 0.00 | 2654 |
| full | threshold | 1.01 | 0.00 | 5578 |
| full | mondrian | never stop early | 0.00 | 5578 |

Step 2, calibration pairs: Learn-then-Test of the chosen candidates only:

| certificate | chosen | certified | parameters | cal RR % | cal risk % | cal mean time (ms) |
|---|---|---|---|---|---|---|
| marginal | 250-4000 / threshold | full / threshold (fallback) | 1.01 | 85.6 | 0.00 | 5455 |
| mondrian | doubling / mondrian | full / mondrian (fallback) | λ per group = 1.01/1.01/1.01 | 85.6 | 0.00 | 5455 |

### TurboReg, fcgfown_kitti_raw_blind test (203 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 92.12 | 5496 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 92.12 | 5496 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 90.15 | 180 | | | | | |
| fixed budget N=500 (single run) | 90.64 | 308 | | | | | |
| fixed budget N=1000 (single run) | 90.64 | 652 | | | | | |
| fixed budget N=2000 (single run) | 91.13 | 1664 | | | | | |
| fixed budget N=4000 (single run) | 92.12 | 5496 | | | | | |

### TurboReg, fcgfown_kitti_test test (555 pairs)

| configuration | RR % | mean time (ms) | ΔRR vs full, pp [95% UB] | non-inferior | speed-up vs full [95% CI] | McNemar p | risk % |
|---|---|---|---|---|---|---|---|
| marginal: full / threshold | 93.51 | 5870 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| mondrian: full / mondrian | 93.51 | 5870 | +0.00 [+0.00] | True | 1.00× [1.00, 1.00] | 1 | 0.00 |
| fixed budget N=250 (single run) | 90.09 | 163 | | | | | |
| fixed budget N=500 (single run) | 91.53 | 278 | | | | | |
| fixed budget N=1000 (single run) | 92.25 | 630 | | | | | |
| fixed budget N=2000 (single run) | 92.97 | 1679 | | | | | |
| fixed budget N=4000 (single run) | 93.51 | 5870 | | | | | |
