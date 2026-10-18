# Results (search_jump1024)

Operating points certified on validation with Learn-then-Test (eps = 1 pp, delta = 0.1): `{'learned_threshold': 0.75, 'mdp': np.float64(4.641588833612773e-08), 'accept_or_giveup': [0.8, 0.1], 'ransac_learned': 0.86, 'ransac_hybrid': 0.075}`


## val (1331 pairs)

| Method | RR % (scene avg) | RR % (RE<15°, TE<30cm) | mean cost (k CE) | median cost (k CE) | mean time (ms) | vs exhaustive: ΔRR pp [95% UB] | cost reduction |
|---|---|---|---|---|---|---|---|
| Exhaustive pose search (7 stages) | 63.6 | 69.3 | 1727.7 | 1772.4 | 902 |  |  |
| Cheapest stage only (256 rotations, 1 basin) | 55.1 | 62.3 | 130.2 | 133.9 | 70 |  |  |
| Best static config (M=2048, b=16) | 64.3 | 69.7 | 1066.0 | 1094.3 | 556 |  |  |
| Adaptive: learned stop (LTT) param=0.75 | 63.0 | 68.9 | 676.9 | 238.0 | 350 | +0.7 [+1.4] | 2.6× [2.4, 2.7] |
| Adaptive: stop or give up (LTT) param=[0.8, 0.1] | 63.2 | 69.0 | 701.6 | 244.6 | 364 | +0.4 [+1.1] | 2.5× [2.3, 2.6] |
| Adaptive: Markov controller (LTT) param=4.641588833612773e-08 | 63.3 | 69.3 | 445.6 | 206.0 | 229 | +0.4 [+1.1] | 3.9× [3.6, 4.1] |
| Oracle stopping (upper bound) | 65.7 | 69.9 | 162.7 | 135.7 | 86 |  |  |
| RANSAC 100k | 61.4 | 66.6 | 987.6 | 503.7 | 446 |  |  |
| RANSAC, classical adaptive stopping (p=0.999) | 61.1 | 65.4 | 148.3 | 40.3 | 72 |  |  |
| RANSAC + learned stop (LTT) param=0.86 | 60.9 | 66.1 | 232.1 | 280.4 | 109 | +0.4 [+0.8] | 4.3× [3.8, 4.7] |
| RANSAC classical + certified give-up (ours) γ=0.075 | 61.0 | 65.3 | 147.4 | 38.1 | 72 | +0.1 [+0.2] | 1.0× [1.0, 1.0] |
| SC² (same correspondences) | 62.0 | 66.8 | — | — | 80 | | |

Paired statistics against the exhaustive search (ΔRR = exhaustive − policy; non-inferiority margin per set; McNemar exact test):

| Policy | ΔRR pp | 95% upper bound | non-inferior | McNemar p | gains / losses | risk % | static frontier RR % at same cost |
|---|---|---|---|---|---|---|---|
| learned_threshold | +0.67 | +1.38 | False | 0.791 | 6 / 8 | 0.60 | 63.5 |
| mdp | +0.39 | +1.06 | False | 1.000 | 7 / 6 | 0.45 | 63.0 |
| accept_or_giveup | +0.43 | +1.06 | False | 1.000 | 4 / 4 | 0.30 | 63.6 |
| ransac_hybrid | +0.08 | +0.16 | True | 0.250 | 0 / 3 | 0.23 |  |
| ransac_learned | +0.14 | +0.47 | True | 0.442 | 16 / 11 | 0.83 |  |

Head-to-head against standard implementations on the same correspondences (dRR = reference - ours, negative = ours better; cost ratio = reference cost / our cost):

| Our policy | vs | ΔRR pp [95% UB] | McNemar p | cost ratio [95% CI] |
|---|---|---|---|---|
| learned_threshold | RANSAC, classical stopping | -1.9 [-0.5] | 0.000728 | 0.22× [0.21, 0.23] |
| learned_threshold | RANSAC 100k | -1.6 [-0.2] | 0.0206 | 1.46× [1.30, 1.63] |
| learned_threshold | exhaustive search (same voting) | +0.7 [+1.4] | 0.791 | 2.55× [2.41, 2.71] |
| mdp | RANSAC, classical stopping | -2.2 [-0.8] | 0.000111 | 0.33× [0.31, 0.35] |
| mdp | RANSAC 100k | -1.9 [-0.5] | 0.00667 | 2.22× [1.98, 2.48] |
| mdp | exhaustive search (same voting) | +0.4 [+1.1] | 1 | 3.88× [3.64, 4.15] |
| accept_or_giveup | RANSAC, classical stopping | -2.2 [-0.8] | 0.000219 | 0.21× [0.20, 0.22] |
| accept_or_giveup | RANSAC 100k | -1.9 [-0.5] | 0.0105 | 1.41× [1.25, 1.58] |
| accept_or_giveup | exhaustive search (same voting) | +0.4 [+1.1] | 1 | 2.46× [2.32, 2.63] |

Compute allocation by difficulty (ground-truth inliers among the putative correspondences):

| GT inliers | pairs | exhaustive cost (k CE) | adaptive cost (k CE) | exhaustive RR % | adaptive RR % |
|---|---|---|---|---|---|
| [0,5) | 142 | 1399.4 | 1021.4 | 0.0 | 0.0 |
| [5,10) | 130 | 1312.5 | 877.3 | 9.2 | 9.2 |
| [10,20) | 183 | 1485.4 | 806.4 | 46.4 | 46.4 |
| [20,40) | 272 | 1566.7 | 322.7 | 82.7 | 83.1 |
| [40,80) | 263 | 1590.4 | 138.4 | 97.3 | 97.3 |
| [80,inf) | 341 | 2386.9 | 182.5 | 100.0 | 100.0 |

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
| Exhaustive pose search (7 stages) | 71.4 | 72.6 | 2605.0 | 2770.9 | 1309 |  |  |
| Cheapest stage only (256 rotations, 1 basin) | 61.3 | 62.4 | 196.5 | 208.8 | 100 |  |  |
| Best static config (M=8192, b=16) | 71.4 | 72.9 | 6198.4 | 6598.1 | 3168 |  |  |
| Adaptive: learned stop (LTT) param=0.75 | 70.6 | 72.1 | 1051.3 | 263.0 | 526 | +0.8 [+1.9] | 2.5× [2.3, 2.6] |
| Adaptive: stop or give up (LTT) param=[0.8, 0.1] | 69.9 | 71.1 | 1033.4 | 263.0 | 517 | +1.4 [+2.5] | 2.5× [2.4, 2.7] |
| Adaptive: Markov controller (LTT) param=4.641588833612773e-08 | 71.2 | 72.2 | 749.0 | 264.0 | 374 | +0.2 [+0.8] | 3.5× [3.2, 3.7] |
| Oracle stopping (upper bound) | 73.5 | 72.5 | 263.6 | 215.4 | 134 |  |  |
| RANSAC 100k | 69.5 | 70.6 | 1017.6 | 584.2 | 409 |  |  |
| RANSAC, classical adaptive stopping (p=0.999) | 69.5 | 70.5 | 245.2 | 179.7 | 101 |  |  |
| RANSAC + learned stop (LTT) param=0.86 | 68.1 | 69.3 | 266.1 | 310.9 | 108 | +1.4 [+2.3] | 3.8× [3.4, 4.3] |
| RANSAC classical + certified give-up (ours) γ=0.075 | 69.4 | 70.4 | 243.9 | 176.0 | 101 | +0.1 [+0.2] | 1.0× [1.0, 1.0] |
| SC² (same correspondences) | 71.8 | 73.3 | — | — | 140 | | |

Paired statistics against the exhaustive search (ΔRR = exhaustive − policy; non-inferiority margin per set; McNemar exact test):

| Policy | ΔRR pp | 95% upper bound | non-inferior | McNemar p | gains / losses | risk % | static frontier RR % at same cost |
|---|---|---|---|---|---|---|---|
| learned_threshold | +0.84 | +1.88 | False | 0.344 | 3 / 7 | 0.55 | 70.6 |
| mdp | +0.21 | +0.82 | True | 1.000 | 8 / 8 | 0.63 | 70.6 |
| accept_or_giveup | +1.45 | +2.51 | False | 0.000 | 3 / 20 | 1.56 | 70.6 |
| ransac_hybrid | +0.08 | +0.24 | True | 1.000 | 0 / 1 | 0.08 |  |
| ransac_learned | +1.39 | +2.10 | False | 0.001 | 2 / 16 | 1.25 |  |

Head-to-head against standard implementations on the same correspondences (dRR = reference - ours, negative = ours better; cost ratio = reference cost / our cost):

| Our policy | vs | ΔRR pp [95% UB] | McNemar p | cost ratio [95% CI] |
|---|---|---|---|---|
| learned_threshold | RANSAC, classical stopping | -1.1 [+0.6] | 0.193 | 0.23× [0.23, 0.24] |
| learned_threshold | RANSAC 100k | -1.0 [+0.7] | 0.155 | 0.97× [0.85, 1.09] |
| learned_threshold | exhaustive search (same voting) | +0.8 [+1.9] | 0.344 | 2.48× [2.33, 2.64] |
| mdp | RANSAC, classical stopping | -1.7 [-0.3] | 0.0822 | 0.33× [0.31, 0.34] |
| mdp | RANSAC 100k | -1.7 [-0.2] | 0.0642 | 1.36× [1.20, 1.53] |
| mdp | exhaustive search (same voting) | +0.2 [+0.8] | 1 | 3.48× [3.24, 3.72] |
| accept_or_giveup | RANSAC, classical stopping | -0.5 [+1.2] | 1 | 0.24× [0.23, 0.25] |
| accept_or_giveup | RANSAC 100k | -0.4 [+1.3] | 0.917 | 0.98× [0.87, 1.11] |
| accept_or_giveup | exhaustive search (same voting) | +1.4 [+2.5] | 0.000488 | 2.52× [2.37, 2.69] |

Compute allocation by difficulty (ground-truth inliers among the putative correspondences):

| GT inliers | pairs | exhaustive cost (k CE) | adaptive cost (k CE) | exhaustive RR % | adaptive RR % |
|---|---|---|---|---|---|
| [0,5) | 80 | 1783.9 | 1512.4 | 0.0 | 0.0 |
| [5,10) | 104 | 2080.3 | 1773.5 | 6.7 | 6.7 |
| [10,20) | 188 | 2479.1 | 1743.4 | 37.2 | 37.8 |
| [20,40) | 250 | 2602.1 | 687.1 | 79.2 | 79.6 |
| [40,80) | 298 | 2713.6 | 242.5 | 98.3 | 97.7 |
| [80,inf) | 359 | 2917.7 | 224.9 | 99.7 | 99.7 |

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
| Exhaustive pose search (7 stages) | 31.0 | 32.3 | 2280.1 | 2287.6 | 900 |  |  |
| Cheapest stage only (256 rotations, 1 basin) | 19.9 | 20.9 | 172.3 | 172.8 | 68 |  |  |
| Best static config (M=2048, b=8) | 31.0 | 31.4 | 1372.4 | 1377.4 | 547 |  |  |
| Adaptive: learned stop (LTT) param=0.75 | 31.0 | 32.2 | 1906.5 | 1984.2 | 750 | +0.0 [+0.2] | 1.2× [1.2, 1.2] |
| Adaptive: stop or give up (LTT) param=[0.8, 0.1] | 30.0 | 31.1 | 1668.2 | 1777.0 | 658 | +1.1 [+1.5] | 1.4× [1.3, 1.4] |
| Adaptive: Markov controller (LTT) param=4.641588833612773e-08 | 31.2 | 32.2 | 1511.2 | 1341.0 | 593 | -0.2 [+0.1] | 1.5× [1.5, 1.6] |
| Oracle stopping (upper bound) | 33.1 | 33.2 | 271.3 | 179.8 | 108 |  |  |
| RANSAC 100k | 26.5 | 27.0 | 457.8 | 442.1 | 153 |  |  |
| RANSAC, classical adaptive stopping (p=0.999) | 26.3 | 26.7 | 385.9 | 412.9 | 128 |  |  |
| RANSAC + learned stop (LTT) param=0.86 | 26.2 | 26.9 | 418.8 | 427.2 | 138 | +0.4 [+0.9] | 1.1× [1.1, 1.1] |
| RANSAC classical + certified give-up (ours) γ=0.075 | 26.3 | 26.7 | 385.7 | 412.9 | 128 | +0.1 [+0.2] | 1.0× [1.0, 1.0] |
| SC² (same correspondences) | 27.6 | 29.4 | — | — | 92 | | |

Paired statistics against the exhaustive search (ΔRR = exhaustive − policy; non-inferiority margin per set; McNemar exact test):

| Policy | ΔRR pp | 95% upper bound | non-inferior | McNemar p | gains / losses | risk % | static frontier RR % at same cost |
|---|---|---|---|---|---|---|---|
| learned_threshold | +0.01 | +0.19 | True | 1.000 | 2 / 3 | 0.17 | 31.0 |
| mdp | -0.16 | +0.06 | True | 0.549 | 7 / 4 | 0.23 | 31.0 |
| accept_or_giveup | +1.06 | +1.47 | True | 0.000 | 3 / 28 | 1.62 | 31.0 |
| ransac_hybrid | +0.06 | +0.17 | True | 1.000 | 0 / 1 | 0.06 |  |
| ransac_learned | +0.15 | +0.90 | True | 1.000 | 6 / 7 | 0.41 |  |

Head-to-head against standard implementations on the same correspondences (dRR = reference - ours, negative = ours better; cost ratio = reference cost / our cost):

| Our policy | vs | ΔRR pp [95% UB] | McNemar p | cost ratio [95% CI] |
|---|---|---|---|---|
| learned_threshold | RANSAC, classical stopping | -4.7 [-2.9] | 5.95e-11 | 0.20× [0.20, 0.21] |
| learned_threshold | RANSAC 100k | -4.5 [-2.9] | 5.32e-11 | 0.24× [0.23, 0.25] |
| learned_threshold | exhaustive search (same voting) | +0.0 [+0.2] | 1 | 1.20× [1.17, 1.22] |
| mdp | RANSAC, classical stopping | -4.8 [-3.1] | 9.51e-12 | 0.26× [0.25, 0.26] |
| mdp | RANSAC 100k | -4.6 [-3.0] | 6.26e-12 | 0.30× [0.29, 0.31] |
| mdp | exhaustive search (same voting) | -0.2 [+0.1] | 0.549 | 1.51× [1.47, 1.55] |
| accept_or_giveup | RANSAC, classical stopping | -3.6 [-1.9] | 1.69e-06 | 0.23× [0.23, 0.24] |
| accept_or_giveup | RANSAC 100k | -3.4 [-1.8] | 1.76e-06 | 0.27× [0.27, 0.28] |
| accept_or_giveup | exhaustive search (same voting) | +1.1 [+1.5] | 4.65e-06 | 1.37× [1.33, 1.40] |

Compute allocation by difficulty (ground-truth inliers among the putative correspondences):

| GT inliers | pairs | exhaustive cost (k CE) | adaptive cost (k CE) | exhaustive RR % | adaptive RR % |
|---|---|---|---|---|---|
| [0,5) | 569 | 2073.3 | 1808.8 | 0.7 | 0.7 |
| [5,10) | 370 | 2277.6 | 2003.3 | 8.6 | 8.9 |
| [10,20) | 384 | 2338.9 | 1677.7 | 42.7 | 41.9 |
| [20,40) | 266 | 2423.6 | 604.5 | 86.1 | 87.2 |
| [40,80) | 107 | 2673.0 | 245.0 | 97.2 | 99.1 |
| [80,inf) | 30 | 2809.1 | 220.4 | 100.0 | 100.0 |

RANSAC budget by difficulty: classical stopping rule vs. classical + certified give-up:

| GT inliers | pairs | share of classical budget | classical cost (k CE) | ours (k CE) | classical RR % | ours RR % |
|---|---|---|---|---|---|---|
| [0,5) | 569 | 34 % | 403.7 | 403.3 | 0.4 | 0.4 |
| [5,10) | 370 | 24 % | 426.0 | 425.5 | 4.1 | 3.8 |
| [10,20) | 384 | 24 % | 419.2 | 419.2 | 32.6 | 32.6 |
| [20,40) | 266 | 15 % | 369.8 | 369.8 | 73.3 | 73.3 |
| [40,80) | 107 | 3 % | 172.7 | 172.7 | 98.1 | 98.1 |
| [80,inf) | 30 | 0 % | 32.1 | 32.1 | 100.0 | 100.0 |
