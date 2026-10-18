# Results (psh_jump1024)

Operating points certified on validation with Learn-then-Test (eps = 1 pp, delta = 0.1): `{'learned_threshold': 0.7, 'mdp': np.float64(1.51177507061566e-07), 'accept_or_giveup': [0.75, 0.05], 'ransac_learned': 0.86, 'ransac_hybrid': 0.075}`


## val (1331 pairs)

| Method | RR % (scene avg) | RR % (RE<15°, TE<30cm) | mean cost (k CE) | median cost (k CE) | mean time (ms) | vs exhaustive: ΔRR pp [95% UB] | cost reduction |
|---|---|---|---|---|---|---|---|
| Exhaustive pose search (7 stages) | 62.1 | 68.1 | 577.0 | 569.7 | 134 |  |  |
| Cheapest stage only (256 rotations, 1 basin) | 53.5 | 60.7 | 68.0 | 68.6 | 16 |  |  |
| Best static config (M=256, b=16) | 61.6 | 67.9 | 122.4 | 123.7 | 37 |  |  |
| Adaptive: learned stop (LTT) param=0.7 | 61.4 | 67.5 | 236.3 | 120.4 | 55 | +0.7 [+1.4] | 2.4× [2.3, 2.6] |
| Adaptive: stop or give up (LTT) param=[0.75, 0.05] | 61.8 | 67.8 | 246.4 | 122.6 | 57 | +0.3 [+0.9] | 2.3× [2.2, 2.5] |
| Adaptive: Markov controller (LTT) param=1.51177507061566e-07 | 61.9 | 67.8 | 188.4 | 115.2 | 45 | +0.2 [+0.7] | 3.1× [2.9, 3.2] |
| Oracle stopping (upper bound) | 63.9 | 68.8 | 77.6 | 70.8 | 19 |  |  |
| RANSAC 100k | 61.4 | 66.6 | 987.6 | 503.7 | 446 |  |  |
| RANSAC, classical adaptive stopping (p=0.999) | 61.1 | 65.4 | 148.3 | 40.3 | 72 |  |  |
| RANSAC + learned stop (LTT) param=0.86 | 60.9 | 66.1 | 232.1 | 280.4 | 109 | +0.4 [+0.8] | 4.3× [3.8, 4.8] |
| RANSAC classical + certified give-up (ours) γ=0.075 | 61.0 | 65.3 | 147.4 | 38.1 | 72 | +0.1 [+0.2] | 1.0× [1.0, 1.0] |
| SC² (same correspondences) | 62.0 | 66.8 | — | — | 80 | | |

Paired statistics against the exhaustive search (ΔRR = exhaustive − policy; non-inferiority margin per set; McNemar exact test):

| Policy | ΔRR pp | 95% upper bound | non-inferior | McNemar p | gains / losses | risk % | static frontier RR % at same cost |
|---|---|---|---|---|---|---|---|
| learned_threshold | +0.66 | +1.38 | False | 0.581 | 5 / 8 | 0.60 | 61.6 |
| mdp | +0.20 | +0.68 | True | 1.000 | 5 / 5 | 0.38 | 61.6 |
| accept_or_giveup | +0.28 | +0.90 | True | 1.000 | 5 / 4 | 0.30 | 61.6 |
| ransac_hybrid | +0.08 | +0.16 | True | 0.250 | 0 / 3 | 0.23 |  |
| ransac_learned | +0.14 | +0.49 | True | 0.442 | 16 / 11 | 0.83 |  |

Head-to-head against standard implementations on the same correspondences (dRR = reference - ours, negative = ours better; cost ratio = reference cost / our cost):

| Our policy | vs | ΔRR pp [95% UB] | McNemar p | cost ratio [95% CI] |
|---|---|---|---|---|
| learned_threshold | RANSAC, classical stopping | -0.4 [+1.2] | 0.0594 | 0.63× [0.61, 0.65] |
| learned_threshold | RANSAC 100k | -0.1 [+1.6] | 0.47 | 4.18× [3.74, 4.69] |
| learned_threshold | exhaustive search (same voting) | +0.7 [+1.4] | 0.581 | 2.44× [2.32, 2.58] |
| learned_threshold | exhaustive search, full voting | +2.2 [+3.5] | 0.0137 | 7.31× [6.96, 7.72] |
| mdp | RANSAC, classical stopping | -0.8 [+0.7] | 0.0265 | 0.79× [0.75, 0.82] |
| mdp | RANSAC 100k | -0.5 [+1.1] | 0.3 | 5.24× [4.71, 5.86] |
| mdp | exhaustive search (same voting) | +0.2 [+0.7] | 1 | 3.06× [2.92, 3.22] |
| mdp | exhaustive search, full voting | +1.7 [+3.0] | 0.0385 | 9.17× [8.73, 9.64] |
| accept_or_giveup | RANSAC, classical stopping | -0.8 [+0.9] | 0.0197 | 0.60× [0.58, 0.62] |
| accept_or_giveup | RANSAC 100k | -0.5 [+1.2] | 0.251 | 4.01× [3.59, 4.48] |
| accept_or_giveup | exhaustive search (same voting) | +0.3 [+0.9] | 1 | 2.34× [2.23, 2.47] |
| accept_or_giveup | exhaustive search, full voting | +1.8 [+3.1] | 0.0533 | 7.01× [6.67, 7.39] |

Compute allocation by difficulty (ground-truth inliers among the putative correspondences):

| GT inliers | pairs | exhaustive cost (k CE) | adaptive cost (k CE) | exhaustive RR % | adaptive RR % |
|---|---|---|---|---|---|
| [0,5) | 142 | 484.9 | 366.5 | 0.0 | 0.0 |
| [5,10) | 130 | 458.6 | 316.2 | 6.2 | 6.2 |
| [10,20) | 183 | 505.7 | 299.7 | 43.7 | 43.7 |
| [20,40) | 272 | 527.9 | 177.0 | 81.2 | 81.2 |
| [40,80) | 263 | 532.6 | 76.3 | 97.0 | 97.0 |
| [80,inf) | 341 | 772.2 | 101.2 | 100.0 | 100.0 |

RANSAC budget by difficulty: classical stopping rule vs. classical + certified give-up:

| GT inliers | pairs | share of classical budget | classical cost (k CE) | ours (k CE) | classical RR % | ours RR % |
|---|---|---|---|---|---|---|
| [0,5) | 142 | 20 % | 277.4 | 272.9 | 0.7 | 0.7 |
| [5,10) | 130 | 17 % | 260.4 | 257.9 | 6.9 | 6.9 |
| [10,20) | 183 | 24 % | 263.9 | 262.9 | 33.3 | 31.7 |
| [20,40) | 272 | 26 % | 192.1 | 192.1 | 79.0 | 79.0 |
| [40,80) | 263 | 8 % | 59.0 | 59.0 | 97.0 | 97.0 |
| [80,inf) | 341 | 4 % | 23.6 | 23.6 | 100.0 | 100.0 |

## 3DMatch (1279 pairs)

| Method | RR % (scene avg) | RR % (RE<15°, TE<30cm) | mean cost (k CE) | median cost (k CE) | mean time (ms) | vs exhaustive: ΔRR pp [95% UB] | cost reduction |
|---|---|---|---|---|---|---|---|
| Exhaustive pose search (7 stages) | 69.7 | 71.1 | 840.3 | 890.7 | 216 |  |  |
| Cheapest stage only (256 rotations, 1 basin) | 61.5 | 61.8 | 101.1 | 107.5 | 28 |  |  |
| Best static config (M=256, b=16) | 68.9 | 70.0 | 187.0 | 196.9 | 56 |  |  |
| Adaptive: learned stop (LTT) param=0.7 | 68.6 | 70.5 | 357.0 | 135.0 | 91 | +1.1 [+2.1] | 2.4× [2.2, 2.5] |
| Adaptive: stop or give up (LTT) param=[0.75, 0.05] | 68.6 | 70.4 | 359.1 | 135.0 | 92 | +1.1 [+2.1] | 2.3× [2.2, 2.5] |
| Adaptive: Markov controller (LTT) param=1.51177507061566e-07 | 69.3 | 70.6 | 292.2 | 156.6 | 77 | +0.3 [+0.9] | 2.9× [2.7, 3.0] |
| Oracle stopping (upper bound) | 71.2 | 70.8 | 117.6 | 110.9 | 33 |  |  |
| RANSAC 100k | 69.5 | 70.6 | 1017.6 | 584.2 | 409 |  |  |
| RANSAC, classical adaptive stopping (p=0.999) | 69.5 | 70.5 | 245.2 | 179.7 | 101 |  |  |
| RANSAC + learned stop (LTT) param=0.86 | 68.1 | 69.3 | 266.1 | 310.9 | 108 | +1.4 [+2.2] | 3.8× [3.4, 4.3] |
| RANSAC classical + certified give-up (ours) γ=0.075 | 69.4 | 70.4 | 243.9 | 176.0 | 101 | +0.1 [+0.2] | 1.0× [1.0, 1.0] |
| SC² (same correspondences) | 71.8 | 73.3 | — | — | 140 | | |

Paired statistics against the exhaustive search (ΔRR = exhaustive − policy; non-inferiority margin per set; McNemar exact test):

| Policy | ΔRR pp | 95% upper bound | non-inferior | McNemar p | gains / losses | risk % | static frontier RR % at same cost |
|---|---|---|---|---|---|---|---|
| learned_threshold | +1.05 | +2.08 | False | 0.065 | 2 / 9 | 0.70 | 68.9 |
| mdp | +0.35 | +0.94 | True | 0.774 | 5 / 7 | 0.55 | 68.9 |
| accept_or_giveup | +1.08 | +2.13 | False | 0.039 | 2 / 10 | 0.78 | 68.9 |
| ransac_hybrid | +0.08 | +0.24 | True | 1.000 | 0 / 1 | 0.08 |  |
| ransac_learned | +1.39 | +2.08 | False | 0.001 | 2 / 16 | 1.25 |  |

Head-to-head against standard implementations on the same correspondences (dRR = reference - ours, negative = ours better; cost ratio = reference cost / our cost):

| Our policy | vs | ΔRR pp [95% UB] | McNemar p | cost ratio [95% CI] |
|---|---|---|---|---|
| learned_threshold | RANSAC, classical stopping | +0.8 [+3.0] | 0.509 | 0.69× [0.67, 0.71] |
| learned_threshold | RANSAC 100k | +0.9 [+3.1] | 0.566 | 2.85× [2.54, 3.20] |
| learned_threshold | exhaustive search (same voting) | +1.1 [+2.1] | 0.0654 | 2.35× [2.23, 2.49] |
| learned_threshold | exhaustive search, full voting | +2.8 [+4.5] | 0.000156 | 7.30× [6.92, 7.71] |
| mdp | RANSAC, classical stopping | +0.1 [+2.0] | 0.845 | 0.84× [0.81, 0.87] |
| mdp | RANSAC 100k | +0.2 [+2.2] | 0.923 | 3.48× [3.11, 3.91] |
| mdp | exhaustive search (same voting) | +0.3 [+0.9] | 0.774 | 2.88× [2.73, 3.03] |
| mdp | exhaustive search, full voting | +2.1 [+3.5] | 0.00309 | 8.91× [8.47, 9.39] |
| accept_or_giveup | RANSAC, classical stopping | +0.9 [+3.0] | 0.448 | 0.68× [0.66, 0.71] |
| accept_or_giveup | RANSAC 100k | +0.9 [+3.1] | 0.501 | 2.83× [2.53, 3.19] |
| accept_or_giveup | exhaustive search (same voting) | +1.1 [+2.1] | 0.0386 | 2.34× [2.22, 2.47] |
| accept_or_giveup | exhaustive search, full voting | +2.8 [+4.5] | 9.85e-05 | 7.26× [6.87, 7.66] |

Compute allocation by difficulty (ground-truth inliers among the putative correspondences):

| GT inliers | pairs | exhaustive cost (k CE) | adaptive cost (k CE) | exhaustive RR % | adaptive RR % |
|---|---|---|---|---|---|
| [0,5) | 80 | 580.1 | 475.7 | 0.0 | 0.0 |
| [5,10) | 104 | 675.2 | 587.3 | 6.7 | 6.7 |
| [10,20) | 188 | 797.4 | 590.4 | 31.4 | 31.9 |
| [20,40) | 250 | 837.7 | 309.2 | 76.0 | 76.0 |
| [40,80) | 298 | 874.7 | 139.9 | 98.3 | 97.3 |
| [80,inf) | 359 | 942.0 | 124.3 | 99.7 | 99.7 |

RANSAC budget by difficulty: classical stopping rule vs. classical + certified give-up:

| GT inliers | pairs | share of classical budget | classical cost (k CE) | ours (k CE) | classical RR % | ours RR % |
|---|---|---|---|---|---|---|
| [0,5) | 80 | 10 % | 376.9 | 367.6 | 0.0 | 0.0 |
| [5,10) | 104 | 13 % | 384.0 | 375.8 | 2.9 | 2.9 |
| [10,20) | 188 | 26 % | 438.9 | 438.7 | 31.9 | 31.4 |
| [20,40) | 250 | 32 % | 401.4 | 401.4 | 78.4 | 78.4 |
| [40,80) | 298 | 15 % | 159.1 | 159.1 | 97.7 | 97.7 |
| [80,inf) | 359 | 4 % | 36.8 | 36.8 | 99.7 | 99.7 |

## 3DLoMatch (1726 pairs)

| Method | RR % (scene avg) | RR % (RE<15°, TE<30cm) | mean cost (k CE) | median cost (k CE) | mean time (ms) | vs exhaustive: ΔRR pp [95% UB] | cost reduction |
|---|---|---|---|---|---|---|---|
| Exhaustive pose search (7 stages) | 29.3 | 30.6 | 733.4 | 735.5 | 170 |  |  |
| Cheapest stage only (256 rotations, 1 basin) | 19.7 | 20.1 | 88.7 | 88.9 | 23 |  |  |
| Best static config (M=256, b=16) | 27.9 | 29.2 | 162.7 | 163.2 | 47 |  |  |
| Adaptive: learned stop (LTT) param=0.7 | 29.5 | 30.7 | 607.3 | 630.1 | 140 | -0.2 [+0.0] | 1.2× [1.2, 1.2] |
| Adaptive: stop or give up (LTT) param=[0.75, 0.05] | 29.4 | 30.6 | 584.6 | 613.1 | 135 | -0.0 [+0.2] | 1.3× [1.2, 1.3] |
| Adaptive: Markov controller (LTT) param=1.51177507061566e-07 | 29.2 | 30.4 | 505.1 | 451.8 | 117 | +0.2 [+0.8] | 1.5× [1.4, 1.5] |
| Oracle stopping (upper bound) | 31.8 | 31.0 | 113.0 | 92.3 | 29 |  |  |
| RANSAC 100k | 26.5 | 27.0 | 457.8 | 442.1 | 153 |  |  |
| RANSAC, classical adaptive stopping (p=0.999) | 26.3 | 26.7 | 385.9 | 412.9 | 128 |  |  |
| RANSAC + learned stop (LTT) param=0.86 | 26.2 | 26.9 | 418.8 | 427.2 | 138 | +0.4 [+0.9] | 1.1× [1.1, 1.1] |
| RANSAC classical + certified give-up (ours) γ=0.075 | 26.3 | 26.7 | 385.7 | 412.9 | 128 | +0.1 [+0.2] | 1.0× [1.0, 1.0] |
| SC² (same correspondences) | 27.6 | 29.4 | — | — | 92 | | |

Paired statistics against the exhaustive search (ΔRR = exhaustive − policy; non-inferiority margin per set; McNemar exact test):

| Policy | ΔRR pp | 95% upper bound | non-inferior | McNemar p | gains / losses | risk % | static frontier RR % at same cost |
|---|---|---|---|---|---|---|---|
| learned_threshold | -0.18 | +0.00 | True | 0.375 | 4 / 1 | 0.06 | 27.9 |
| mdp | +0.16 | +0.76 | True | 0.774 | 7 / 5 | 0.29 | 27.9 |
| accept_or_giveup | -0.04 | +0.21 | True | 1.000 | 5 / 5 | 0.29 | 27.9 |
| ransac_hybrid | +0.06 | +0.17 | True | 1.000 | 0 / 1 | 0.06 |  |
| ransac_learned | +0.15 | +0.89 | True | 1.000 | 6 / 7 | 0.41 |  |

Head-to-head against standard implementations on the same correspondences (dRR = reference - ours, negative = ours better; cost ratio = reference cost / our cost):

| Our policy | vs | ΔRR pp [95% UB] | McNemar p | cost ratio [95% CI] |
|---|---|---|---|---|
| learned_threshold | RANSAC, classical stopping | -3.2 [-1.4] | 6.41e-06 | 0.64× [0.63, 0.65] |
| learned_threshold | RANSAC 100k | -3.0 [-1.2] | 7.66e-06 | 0.75× [0.74, 0.77] |
| learned_threshold | exhaustive search (same voting) | -0.2 [+0.0] | 0.375 | 1.21× [1.18, 1.23] |
| learned_threshold | exhaustive search, full voting | +1.5 [+2.5] | 0.000636 | 3.75× [3.68, 3.83] |
| mdp | RANSAC, classical stopping | -2.8 [-1.0] | 1.34e-05 | 0.76× [0.75, 0.78] |
| mdp | RANSAC 100k | -2.6 [-0.8] | 1.6e-05 | 0.91× [0.88, 0.94] |
| mdp | exhaustive search (same voting) | +0.2 [+0.8] | 0.774 | 1.45× [1.42, 1.49] |
| mdp | exhaustive search, full voting | +1.8 [+3.0] | 0.000535 | 4.51× [4.40, 4.63] |
| accept_or_giveup | RANSAC, classical stopping | -3.0 [-1.3] | 1.72e-05 | 0.66× [0.65, 0.67] |
| accept_or_giveup | RANSAC 100k | -2.8 [-1.1] | 2.05e-05 | 0.78× [0.76, 0.80] |
| accept_or_giveup | exhaustive search (same voting) | -0.0 [+0.2] | 1 | 1.25× [1.23, 1.28] |
| accept_or_giveup | exhaustive search, full voting | +1.6 [+2.7] | 0.000256 | 3.90× [3.82, 3.99] |

Compute allocation by difficulty (ground-truth inliers among the putative correspondences):

| GT inliers | pairs | exhaustive cost (k CE) | adaptive cost (k CE) | exhaustive RR % | adaptive RR % |
|---|---|---|---|---|---|
| [0,5) | 569 | 667.8 | 582.5 | 0.4 | 0.4 |
| [5,10) | 370 | 731.6 | 636.2 | 7.8 | 7.8 |
| [10,20) | 384 | 751.4 | 551.8 | 37.8 | 37.8 |
| [20,40) | 266 | 779.0 | 276.5 | 83.1 | 83.1 |
| [40,80) | 107 | 861.5 | 146.9 | 97.2 | 99.1 |
| [80,inf) | 30 | 906.6 | 123.3 | 100.0 | 100.0 |

RANSAC budget by difficulty: classical stopping rule vs. classical + certified give-up:

| GT inliers | pairs | share of classical budget | classical cost (k CE) | ours (k CE) | classical RR % | ours RR % |
|---|---|---|---|---|---|---|
| [0,5) | 569 | 34 % | 403.7 | 403.3 | 0.4 | 0.4 |
| [5,10) | 370 | 24 % | 426.0 | 425.5 | 4.1 | 3.8 |
| [10,20) | 384 | 24 % | 419.2 | 419.2 | 32.6 | 32.6 |
| [20,40) | 266 | 15 % | 369.8 | 369.8 | 73.3 | 73.3 |
| [40,80) | 107 | 3 % | 172.7 | 172.7 | 98.1 | 98.1 |
| [80,inf) | 30 | 0 % | 32.1 | 32.1 | 100.0 | 100.0 |
