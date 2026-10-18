# Certified adaptive correspondence budgets (SC²-PCR, TurboReg)

Primary metric: RR = RE ≤ 15° and TE ≤ 30 cm, pooled over all pairs (SC²/MAC/TurboReg protocol). Time: cumulative single-thread wall-clock of the estimator (correspondence construction excluded; identical for all). Certified on validation with Learn-then-Test (ε = 1 pp, δ = 0.1) against the full-budget estimator, then evaluated once on test.


## SC²-PCR  (certified: threshold λ = 0.8, Markov λ = 0.0)


### val (1331 pairs)

| Configuration | RR % (15°/30 cm) | official RR % (RMSE) | mean time (ms) | mean ops (M) | vs full: ΔRR pp [95% UB] | non-inferior | speed-up [95% CI] | ops reduction |
|---|---|---|---|---|---|---|---|---|
| fixed N=250 | 51.31 | 44.65 | 52 | 5.3 | +20.1 [+21.9] | False | 32.4× [31.5, 33.3] | 304.2× |
| fixed N=500 | 61.16 | 44.65 | 127 | 26.7 | +10.2 [+11.6] | False | 13.2× [12.9, 13.5] | 61.1× |
| fixed N=1000 | 67.54 | 44.65 | 307 | 142.3 | +3.8 [+5.0] | False | 5.4× [5.3, 5.5] | 11.4× |
| fixed N=2000 | 70.02 | 44.65 | 705 | 550.6 | +1.4 [+2.0] | False | 2.4× [2.3, 2.4] | 3.0× |
| fixed N=4000 | 71.37 | 44.65 | 1672 | 1627.6 | reference | | |  |
| Adaptive budget, threshold (certified) | 71.22 | 64.96 | 1149 | 930.4 | +0.2 [+0.6] | True | 1.5× [1.4, 1.6] | 1.7× |
| Adaptive budget, Markov (certified) | 71.37 | 65.21 | 1180 | 910.8 | +0.0 [+0.4] | True | 1.4× [1.3, 1.5] | 1.8× |
| Oracle budget (upper bound) | 73.48 | 66.67 | 231 | 137.5 | -2.1 [-1.5] | True | 7.2× [6.3, 8.5] | 11.8× |

### 3DMatch (1623 pairs)

| Configuration | RR % (15°/30 cm) | official RR % (RMSE) | mean time (ms) | mean ops (M) | vs full: ΔRR pp [95% UB] | non-inferior | speed-up [95% CI] | ops reduction |
|---|---|---|---|---|---|---|---|---|
| fixed N=250 | 50.83 | 42.83 | 55 | 5.6 | +30.7 [+32.5] | False | 50.1× [49.1, 51.2] | 579.4× |
| fixed N=500 | 61.31 | 42.83 | 143 | 30.9 | +20.2 [+21.8] | False | 19.3× [19.0, 19.6] | 104.2× |
| fixed N=1000 | 70.18 | 42.83 | 375 | 198.1 | +11.3 [+12.8] | False | 7.4× [7.3, 7.5] | 16.2× |
| fixed N=2000 | 77.08 | 42.83 | 965 | 929.2 | +4.4 [+5.4] | False | 2.9× [2.8, 2.9] | 3.5× |
| fixed N=4000 | 81.52 | 42.83 | 2762 | 3216.8 | reference | | |  |
| Adaptive budget, threshold (certified) | 79.42 | 73.89 | 1687 | 1677.9 | +2.1 [+2.7] | False | 1.6× [1.5, 1.7] | 1.9× |
| Adaptive budget, Markov (certified) | 80.59 | 74.98 | 1711 | 1637.0 | +0.9 [+1.4] | False | 1.6× [1.5, 1.7] | 2.0× |
| Oracle budget (upper bound) | 83.30 | 75.73 | 484 | 394.2 | -1.8 [-1.2] | True | 5.7× [5.1, 6.4] | 8.2× |

### 3DLoMatch (1781 pairs)

| Configuration | RR % (15°/30 cm) | official RR % (RMSE) | mean time (ms) | mean ops (M) | vs full: ΔRR pp [95% UB] | non-inferior | speed-up [95% CI] | ops reduction |
|---|---|---|---|---|---|---|---|---|
| fixed N=250 | 13.31 | 11.25 | 60 | 5.6 | +23.3 [+25.0] | False | 41.4× [40.5, 42.3] | 494.6× |
| fixed N=500 | 19.03 | 11.25 | 152 | 30.5 | +17.6 [+19.1] | False | 16.3× [15.9, 16.6] | 90.0× |
| fixed N=1000 | 25.44 | 11.25 | 378 | 186.3 | +11.2 [+12.5] | False | 6.5× [6.4, 6.6] | 14.8× |
| fixed N=2000 | 32.00 | 11.25 | 933 | 831.7 | +4.6 [+5.7] | False | 2.6× [2.6, 2.7] | 3.3× |
| fixed N=4000 | 36.61 | 11.25 | 2470 | 2748.6 | reference | | |  |
| Adaptive budget, threshold (certified) | 36.16 | 34.57 | 3408 | 3264.1 | +0.4 [+0.8] | True | 0.7× [0.7, 0.7] | 0.8× |
| Adaptive budget, Markov (certified) | 36.27 | 34.51 | 3346 | 3166.1 | +0.3 [+0.7] | True | 0.7× [0.7, 0.8] | 0.9× |
| Oracle budget (upper bound) | 39.47 | 35.96 | 469 | 372.8 | -2.9 [-2.2] | True | 5.3× [4.8, 5.9] | 7.4× |

## TurboReg  (certified: threshold λ = 0.8, Markov λ = 0.0)


### val (1331 pairs)

| Configuration | RR % (15°/30 cm) | official RR % (RMSE) | mean time (ms) | mean ops (M) | vs full: ΔRR pp [95% UB] | non-inferior | speed-up [95% CI] | ops reduction |
|---|---|---|---|---|---|---|---|---|
| fixed N=250 | 51.69 | 45.05 | 31 | 15.9 | +20.5 [+22.4] | False | 94.5× [89.1, 100.2] | 1860.2× |
| fixed N=500 | 61.16 | 45.05 | 166 | 125.1 | +11.0 [+12.5] | False | 17.5× [17.0, 18.1] | 236.9× |
| fixed N=1000 | 67.17 | 45.05 | 556 | 905.8 | +5.0 [+6.1] | False | 5.2× [5.1, 5.4] | 32.7× |
| fixed N=2000 | 70.47 | 45.05 | 1265 | 5698.7 | +1.7 [+2.4] | False | 2.3× [2.3, 2.3] | 5.2× |
| fixed N=4000 | 72.20 | 45.05 | 2917 | 29641.3 | reference | | |  |
| Adaptive budget, threshold (certified) | 71.83 | 65.32 | 1841 | 14018.6 | +0.4 [+0.8] | True | 1.6× [1.5, 1.7] | 2.1× |
| Adaptive budget, Markov (certified) | 71.90 | 65.32 | 1822 | 12328.1 | +0.3 [+0.8] | True | 1.6× [1.5, 1.7] | 2.4× |
| Oracle budget (upper bound) | 74.00 | 66.12 | 289 | 1539.5 | -1.8 [-1.3] | True | 10.1× [8.5, 12.3] | 19.3× |

### 3DMatch (1623 pairs)

| Configuration | RR % (15°/30 cm) | official RR % (RMSE) | mean time (ms) | mean ops (M) | vs full: ΔRR pp [95% UB] | non-inferior | speed-up [95% CI] | ops reduction |
|---|---|---|---|---|---|---|---|---|
| fixed N=250 | 49.04 | 40.12 | 26 | 15.9 | +32.8 [+34.8] | False | 177.8× [167.0, 189.5] | 3293.4× |
| fixed N=500 | 60.01 | 40.12 | 140 | 126.3 | +21.9 [+23.6] | False | 32.9× [31.8, 34.1] | 413.6× |
| fixed N=1000 | 69.25 | 40.12 | 548 | 997.2 | +12.6 [+14.0] | False | 8.4× [8.2, 8.5] | 52.4× |
| fixed N=2000 | 76.59 | 40.12 | 1582 | 7804.9 | +5.3 [+6.3] | False | 2.9× [2.9, 2.9] | 6.7× |
| fixed N=4000 | 81.89 | 40.12 | 4590 | 52239.6 | reference | | |  |
| Adaptive budget, threshold (certified) | 79.73 | 73.67 | 2526 | 22542.8 | +2.2 [+2.8] | False | 1.8× [1.7, 1.9] | 2.3× |
| Adaptive budget, Markov (certified) | 80.84 | 74.40 | 2454 | 20006.3 | +1.0 [+1.5] | False | 1.9× [1.8, 2.0] | 2.6× |
| Oracle budget (upper bound) | 83.18 | 75.73 | 665 | 4804.4 | -1.3 [-0.9] | True | 6.9× [6.1, 7.9] | 10.9× |

### 3DLoMatch (1781 pairs)

| Configuration | RR % (15°/30 cm) | official RR % (RMSE) | mean time (ms) | mean ops (M) | vs full: ΔRR pp [95% UB] | non-inferior | speed-up [95% CI] | ops reduction |
|---|---|---|---|---|---|---|---|---|
| fixed N=250 | 13.87 | 11.91 | 11 | 15.7 | +22.7 [+24.3] | False | 357.0× [345.0, 368.8] | 2911.6× |
| fixed N=500 | 19.03 | 11.91 | 81 | 125.7 | +17.5 [+19.0] | False | 50.7× [49.3, 52.2] | 364.5× |
| fixed N=1000 | 25.21 | 11.91 | 469 | 996.0 | +11.3 [+12.7] | False | 8.7× [8.6, 8.9] | 46.0× |
| fixed N=2000 | 31.44 | 11.91 | 1517 | 7451.8 | +5.1 [+6.1] | False | 2.7× [2.7, 2.7] | 6.1× |
| fixed N=4000 | 36.55 | 11.91 | 4100 | 45810.8 | reference | | |  |
| Adaptive budget, threshold (certified) | 36.16 | 34.50 | 5226 | 46567.0 | +0.4 [+0.7] | True | 0.8× [0.8, 0.8] | 1.0× |
| Adaptive budget, Markov (certified) | 36.22 | 34.15 | 5024 | 43272.1 | +0.3 [+0.7] | True | 0.8× [0.8, 0.8] | 1.1× |
| Oracle budget (upper bound) | 38.85 | 34.95 | 585 | 4458.6 | -2.3 [-1.7] | True | 7.0× [6.2, 8.1] | 10.3× |

Published full-budget results with FPFH (TurboReg paper, Table 1–2): SC²-PCR 83.73 / 38.57, TurboReg 84.10 / 40.99 (3DMatch / 3DLoMatch). Our correspondences are recomputed (5 cm FPFH, nearest neighbour, top 4,000 by Lowe ratio), so small differences are expected.

