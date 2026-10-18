# Results (search_to2048)

Operating points certified on validation with Learn-then-Test (eps = 1 pp, delta = 0.1): `{'learned_threshold': 0.75, 'mdp': np.float64(3.4551072945922184e-08), 'accept_or_giveup': [0.8, 0.1], 'ransac_learned': 0.86, 'ransac_hybrid': 0.075}`


## val (1331 pairs)

| Method | RR % (scene avg) | RR % (RE<15°, TE<30cm) | mean cost (k CE) | median cost (k CE) | mean time (ms) | vs exhaustive: ΔRR pp [95% UB] | cost reduction |
|---|---|---|---|---|---|---|---|
| Exhaustive pose search (7 stages) | 63.6 | 69.3 | 2009.0 | 2062.5 | 1048 |  |  |
| Cheapest stage only (256 rotations, 1 basin) | 55.1 | 62.3 | 130.2 | 133.9 | 70 |  |  |
| Best static config (M=2048, b=16) | 64.3 | 69.7 | 1066.0 | 1094.3 | 556 |  |  |
| Adaptive: learned stop (LTT) param=0.75 | 62.9 | 68.8 | 756.2 | 240.6 | 389 | +0.7 [+1.4] | 2.7× [2.5, 2.8] |
| Adaptive: stop or give up (LTT) param=[0.8, 0.1] | 63.3 | 69.0 | 777.4 | 244.0 | 402 | +0.3 [+0.8] | 2.6× [2.4, 2.8] |
| Adaptive: Markov controller (LTT) param=3.4551072945922184e-08 | 62.8 | 69.1 | 446.0 | 199.3 | 228 | +0.7 [+1.6] | 4.5× [4.2, 4.9] |
| Oracle stopping (upper bound) | 65.4 | 69.5 | 155.8 | 135.4 | 83 |  |  |
| RANSAC 100k | 61.4 | 66.6 | 987.6 | 503.7 | 446 |  |  |
| RANSAC, classical adaptive stopping (p=0.999) | 61.1 | 65.4 | 148.3 | 40.3 | 72 |  |  |
| RANSAC + learned stop (LTT) param=0.86 | 60.9 | 66.1 | 232.1 | 280.4 | 109 | +0.4 [+0.8] | 4.3× [3.8, 4.7] |
| RANSAC classical + certified give-up (ours) γ=0.075 | 61.0 | 65.3 | 147.4 | 38.1 | 72 | +0.1 [+0.2] | 1.0× [1.0, 1.0] |
| SC² (same correspondences) | 62.0 | 66.8 | — | — | 80 | | |

Paired statistics against the exhaustive search (ΔRR = exhaustive − policy; non-inferiority margin per set; McNemar exact test):

| Policy | ΔRR pp | 95% upper bound | non-inferior | McNemar p | gains / losses | risk % | static frontier RR % at same cost |
|---|---|---|---|---|---|---|---|
| learned_threshold | +0.70 | +1.40 | False | 0.581 | 5 / 8 | 0.60 | 63.7 |
| mdp | +0.74 | +1.60 | False | 1.000 | 7 / 8 | 0.60 | 63.1 |
| accept_or_giveup | +0.26 | +0.81 | True | 1.000 | 4 / 4 | 0.30 | 63.7 |
| ransac_hybrid | +0.08 | +0.16 | True | 0.250 | 0 / 3 | 0.23 |  |
| ransac_learned | +0.14 | +0.47 | True | 0.442 | 16 / 11 | 0.83 |  |

Head-to-head against standard implementations on the same correspondences (dRR = reference - ours, negative = ours better; cost ratio = reference cost / our cost):

| Our policy | vs | ΔRR pp [95% UB] | McNemar p | cost ratio [95% CI] |
|---|---|---|---|---|
| learned_threshold | RANSAC, classical stopping | -1.8 [-0.3] | 0.00111 | 0.20× [0.19, 0.20] |
| learned_threshold | RANSAC 100k | -1.5 [-0.1] | 0.028 | 1.31× [1.16, 1.47] |
| learned_threshold | exhaustive search (same voting) | +0.7 [+1.4] | 0.581 | 2.66× [2.50, 2.82] |
| mdp | RANSAC, classical stopping | -1.8 [-0.2] | 0.000409 | 0.33× [0.31, 0.36] |
| mdp | RANSAC 100k | -1.5 [+0.1] | 0.016 | 2.21× [1.95, 2.49] |
| mdp | exhaustive search (same voting) | +0.7 [+1.6] | 1 | 4.50× [4.19, 4.86] |
| accept_or_giveup | RANSAC, classical stopping | -2.3 [-0.8] | 0.000219 | 0.19× [0.18, 0.20] |
| accept_or_giveup | RANSAC 100k | -2.0 [-0.5] | 0.00967 | 1.27× [1.13, 1.42] |
| accept_or_giveup | exhaustive search (same voting) | +0.3 [+0.8] | 1 | 2.58× [2.44, 2.76] |

Compute allocation by difficulty (ground-truth inliers among the putative correspondences):

| GT inliers | pairs | exhaustive cost (k CE) | adaptive cost (k CE) | exhaustive RR % | adaptive RR % |
|---|---|---|---|---|---|
| [0,5) | 142 | 1627.0 | 1101.2 | 0.0 | 0.0 |
| [5,10) | 130 | 1525.8 | 924.6 | 9.2 | 9.2 |
| [10,20) | 183 | 1727.0 | 795.4 | 45.9 | 45.9 |
| [20,40) | 272 | 1821.6 | 260.8 | 83.1 | 82.7 |
| [40,80) | 263 | 1849.5 | 144.8 | 97.3 | 97.3 |
| [80,inf) | 341 | 2775.9 | 183.4 | 100.0 | 100.0 |

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
| Exhaustive pose search (7 stages) | 71.3 | 72.9 | 3030.6 | 3220.7 | 1516 |  |  |
| Cheapest stage only (256 rotations, 1 basin) | 61.3 | 62.4 | 196.5 | 208.8 | 100 |  |  |
| Best static config (M=8192, b=16) | 71.4 | 72.9 | 6198.4 | 6598.1 | 3168 |  |  |
| Adaptive: learned stop (LTT) param=0.75 | 70.5 | 72.3 | 1172.4 | 263.0 | 583 | +0.8 [+1.9] | 2.6× [2.4, 2.8] |
| Adaptive: stop or give up (LTT) param=[0.8, 0.1] | 70.1 | 71.9 | 1154.9 | 263.0 | 574 | +1.2 [+2.3] | 2.6× [2.5, 2.8] |
| Adaptive: Markov controller (LTT) param=3.4551072945922184e-08 | 71.0 | 72.6 | 741.0 | 264.0 | 369 | +0.3 [+1.0] | 4.1× [3.8, 4.4] |
| Oracle stopping (upper bound) | 73.7 | 72.9 | 264.2 | 215.4 | 135 |  |  |
| RANSAC 100k | 69.5 | 70.6 | 1017.6 | 584.2 | 409 |  |  |
| RANSAC, classical adaptive stopping (p=0.999) | 69.5 | 70.5 | 245.2 | 179.7 | 101 |  |  |
| RANSAC + learned stop (LTT) param=0.86 | 68.1 | 69.3 | 266.1 | 310.9 | 108 | +1.4 [+2.3] | 3.8× [3.4, 4.3] |
| RANSAC classical + certified give-up (ours) γ=0.075 | 69.4 | 70.4 | 243.9 | 176.0 | 101 | +0.1 [+0.2] | 1.0× [1.0, 1.0] |
| SC² (same correspondences) | 71.8 | 73.3 | — | — | 140 | | |

Paired statistics against the exhaustive search (ΔRR = exhaustive − policy; non-inferiority margin per set; McNemar exact test):

| Policy | ΔRR pp | 95% upper bound | non-inferior | McNemar p | gains / losses | risk % | static frontier RR % at same cost |
|---|---|---|---|---|---|---|---|
| learned_threshold | +0.84 | +1.88 | False | 0.344 | 3 / 7 | 0.55 | 70.7 |
| mdp | +0.32 | +1.05 | False | 1.000 | 11 / 11 | 0.86 | 70.6 |
| accept_or_giveup | +1.21 | +2.28 | False | 0.012 | 4 / 16 | 1.25 | 70.7 |
| ransac_hybrid | +0.08 | +0.24 | True | 1.000 | 0 / 1 | 0.08 |  |
| ransac_learned | +1.39 | +2.10 | False | 0.001 | 2 / 16 | 1.25 |  |

Head-to-head against standard implementations on the same correspondences (dRR = reference - ours, negative = ours better; cost ratio = reference cost / our cost):

| Our policy | vs | ΔRR pp [95% UB] | McNemar p | cost ratio [95% CI] |
|---|---|---|---|---|
| learned_threshold | RANSAC, classical stopping | -1.0 [+0.6] | 0.193 | 0.21× [0.20, 0.22] |
| learned_threshold | RANSAC 100k | -1.0 [+0.7] | 0.155 | 0.87× [0.76, 0.98] |
| learned_threshold | exhaustive search (same voting) | +0.8 [+1.9] | 0.344 | 2.58× [2.42, 2.75] |
| mdp | RANSAC, classical stopping | -1.6 [-0.1] | 0.079 | 0.33× [0.31, 0.35] |
| mdp | RANSAC 100k | -1.5 [+0.0] | 0.0614 | 1.37× [1.21, 1.56] |
| mdp | exhaustive search (same voting) | +0.3 [+1.0] | 1 | 4.09× [3.79, 4.42] |
| accept_or_giveup | RANSAC, classical stopping | -0.7 [+1.0] | 0.617 | 0.21× [0.20, 0.22] |
| accept_or_giveup | RANSAC 100k | -0.6 [+1.1] | 0.538 | 0.88× [0.78, 0.99] |
| accept_or_giveup | exhaustive search (same voting) | +1.2 [+2.3] | 0.0118 | 2.62× [2.46, 2.80] |

Compute allocation by difficulty (ground-truth inliers among the putative correspondences):

| GT inliers | pairs | exhaustive cost (k CE) | adaptive cost (k CE) | exhaustive RR % | adaptive RR % |
|---|---|---|---|---|---|
| [0,5) | 80 | 2074.5 | 1647.0 | 0.0 | 0.0 |
| [5,10) | 104 | 2419.4 | 1948.3 | 7.7 | 7.7 |
| [10,20) | 188 | 2883.4 | 1771.0 | 36.7 | 36.2 |
| [20,40) | 250 | 3027.2 | 518.1 | 79.2 | 80.0 |
| [40,80) | 298 | 3157.2 | 233.4 | 98.3 | 98.0 |
| [80,inf) | 359 | 3395.1 | 226.4 | 99.7 | 99.7 |

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
| Exhaustive pose search (7 stages) | 31.0 | 32.7 | 2651.8 | 2659.9 | 1044 |  |  |
| Cheapest stage only (256 rotations, 1 basin) | 19.9 | 20.9 | 172.3 | 172.8 | 68 |  |  |
| Best static config (M=2048, b=8) | 31.0 | 31.4 | 1372.4 | 1377.4 | 547 |  |  |
| Adaptive: learned stop (LTT) param=0.75 | 30.9 | 32.5 | 2189.8 | 2293.8 | 859 | +0.1 [+0.3] | 1.2× [1.2, 1.2] |
| Adaptive: stop or give up (LTT) param=[0.8, 0.1] | 29.7 | 31.2 | 1865.7 | 1945.5 | 734 | +1.3 [+1.7] | 1.4× [1.4, 1.5] |
| Adaptive: Markov controller (LTT) param=3.4551072945922184e-08 | 30.5 | 32.0 | 1575.0 | 1356.9 | 615 | +0.6 [+1.0] | 1.7× [1.6, 1.7] |
| Oracle stopping (upper bound) | 33.2 | 33.1 | 254.1 | 179.6 | 101 |  |  |
| RANSAC 100k | 26.5 | 27.0 | 457.8 | 442.1 | 153 |  |  |
| RANSAC, classical adaptive stopping (p=0.999) | 26.3 | 26.7 | 385.9 | 412.9 | 128 |  |  |
| RANSAC + learned stop (LTT) param=0.86 | 26.2 | 26.9 | 418.8 | 427.2 | 138 | +0.4 [+0.9] | 1.1× [1.1, 1.1] |
| RANSAC classical + certified give-up (ours) γ=0.075 | 26.3 | 26.7 | 385.7 | 412.9 | 128 | +0.1 [+0.2] | 1.0× [1.0, 1.0] |
| SC² (same correspondences) | 27.6 | 29.4 | — | — | 92 | | |

Paired statistics against the exhaustive search (ΔRR = exhaustive − policy; non-inferiority margin per set; McNemar exact test):

| Policy | ΔRR pp | 95% upper bound | non-inferior | McNemar p | gains / losses | risk % | static frontier RR % at same cost |
|---|---|---|---|---|---|---|---|
| learned_threshold | +0.12 | +0.26 | True | 0.250 | 0 / 3 | 0.17 | 31.0 |
| mdp | +0.57 | +1.01 | True | 0.027 | 5 / 16 | 0.93 | 31.0 |
| accept_or_giveup | +1.28 | +1.70 | True | 0.000 | 0 / 30 | 1.74 | 31.0 |
| ransac_hybrid | +0.06 | +0.17 | True | 1.000 | 0 / 1 | 0.06 |  |
| ransac_learned | +0.15 | +0.90 | True | 1.000 | 6 / 7 | 0.41 |  |

Head-to-head against standard implementations on the same correspondences (dRR = reference - ours, negative = ours better; cost ratio = reference cost / our cost):

| Our policy | vs | ΔRR pp [95% UB] | McNemar p | cost ratio [95% CI] |
|---|---|---|---|---|
| learned_threshold | RANSAC, classical stopping | -4.6 [-2.9] | 1.24e-11 | 0.18× [0.17, 0.18] |
| learned_threshold | RANSAC 100k | -4.4 [-2.8] | 1.07e-11 | 0.21× [0.20, 0.21] |
| learned_threshold | exhaustive search (same voting) | +0.1 [+0.3] | 0.25 | 1.21× [1.19, 1.24] |
| mdp | RANSAC, classical stopping | -4.1 [-2.4] | 9.26e-10 | 0.25× [0.24, 0.25] |
| mdp | RANSAC 100k | -3.9 [-2.3] | 6.9e-10 | 0.29× [0.28, 0.30] |
| mdp | exhaustive search (same voting) | +0.6 [+1.0] | 0.0266 | 1.68× [1.62, 1.74] |
| accept_or_giveup | RANSAC, classical stopping | -3.4 [-1.7] | 1.76e-06 | 0.21× [0.20, 0.21] |
| accept_or_giveup | RANSAC 100k | -3.2 [-1.6] | 1.83e-06 | 0.25× [0.24, 0.25] |
| accept_or_giveup | exhaustive search (same voting) | +1.3 [+1.7] | 1.86e-09 | 1.42× [1.38, 1.46] |

Compute allocation by difficulty (ground-truth inliers among the putative correspondences):

| GT inliers | pairs | exhaustive cost (k CE) | adaptive cost (k CE) | exhaustive RR % | adaptive RR % |
|---|---|---|---|---|---|
| [0,5) | 569 | 2411.0 | 1996.9 | 0.7 | 0.7 |
| [5,10) | 370 | 2648.5 | 2153.1 | 8.4 | 8.4 |
| [10,20) | 384 | 2720.0 | 1640.8 | 43.8 | 41.9 |
| [20,40) | 266 | 2818.9 | 465.8 | 85.7 | 84.2 |
| [40,80) | 107 | 3110.0 | 232.6 | 99.1 | 99.1 |
| [80,inf) | 30 | 3269.1 | 224.0 | 100.0 | 100.0 |

RANSAC budget by difficulty: classical stopping rule vs. classical + certified give-up:

| GT inliers | pairs | share of classical budget | classical cost (k CE) | ours (k CE) | classical RR % | ours RR % |
|---|---|---|---|---|---|---|
| [0,5) | 569 | 34 % | 403.7 | 403.3 | 0.4 | 0.4 |
| [5,10) | 370 | 24 % | 426.0 | 425.5 | 4.1 | 3.8 |
| [10,20) | 384 | 24 % | 419.2 | 419.2 | 32.6 | 32.6 |
| [20,40) | 266 | 15 % | 369.8 | 369.8 | 73.3 | 73.3 |
| [40,80) | 107 | 3 % | 172.7 | 172.7 | 98.1 | 98.1 |
| [80,inf) | 30 | 0 % | 32.1 | 32.1 | 100.0 | 100.0 |
