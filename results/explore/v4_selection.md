# v4 factorial: pre-specified selection (fitting-pair cost, 1-SE rule, simplest wins)


## sc2: winner verify / hgb / gate on (best score 1133 ms ± 51; 2 tied)

| signals | classifier | gate | fit score (ms) | ladder | 3DMatch speed (risk %) | 3DLoMatch speed (risk %) | NI |
|---|---|---|---|---|---|---|---|
| both (tied) | hgb | on | 1133 | 250-2000-4000 | 1.58 (0.18) | 1.00 (0.00) | True |
| verify **(winner)** | hgb | on | 1162 | 500-2000-4000 | 1.68 (0.25) | 0.98 (0.00) | True |
| both | hgb | off | 1194 | 250-2000-4000 | 1.49 (0.31) | 0.83 (0.22) | True |
| verify | poly2 | on | 1199 | 500-4000 | 1.72 (0.25) | 1.05 (0.11) | True |
| verify | poly2 | off | 1211 | 500-4000 | 1.70 (0.25) | 1.02 (0.11) | True |
| base | hgb | on | 1213 | 500-4000 | 1.71 (0.37) | 1.03 (0.11) | True |
| base | poly2 | on | 1215 | 500-4000 | 1.62 (0.06) | 1.03 (0.11) | True |
| verify | logit | on | 1220 | 500-4000 | 1.62 (0.25) | 1.02 (0.00) | True |
| both | logit | on | 1229 | x4 | 1.63 (0.12) | 1.01 (0.00) | True |
| base | hgb | off | 1235 | 500-4000 | 1.69 (0.37) | 1.00 (0.17) | True |
| verify | logit | off | 1244 | 500-4000 | 1.59 (0.25) | 0.98 (0.06) | True |
| geom | poly2 | on | 1245 | x4 | 1.58 (0.12) | 1.03 (0.11) | True |
| verify | hgb | off | 1246 | 500-2000-4000 | 1.60 (0.31) | 0.82 (0.11) | True |
| base | poly2 | off | 1254 | 500-4000 | 1.58 (0.06) | 0.98 (0.11) | True |
| base | logit | on | 1254 | 500-4000 | 1.59 (0.12) | 1.02 (0.06) | True |
| both | poly2 | on | 1260 | x4 | 1.86 (0.31) | 0.98 (0.00) | True |
| both | logit | off | 1263 | x4 | 1.58 (0.18) | 0.91 (0.00) | True |
| both | poly2 | off | 1266 | x4 | 1.85 (0.37) | 0.97 (0.06) | True |
| base | logit | off | 1285 | 500-4000 | 1.55 (0.12) | 0.97 (0.06) | True |
| geom | poly2 | off | 1308 | x4 | 1.53 (0.25) | 0.91 (0.45) | True |
| geom | hgb | on | 1346 | 500-4000 | 1.69 (0.31) | 1.02 (0.17) | True |
| geom | hgb | off | 1357 | 500-4000 | 1.68 (0.31) | 1.01 (0.22) | True |
| geom | logit | on | 1371 | 500-4000 | 1.65 (0.18) | 1.02 (0.11) | True |
| geom | logit | off | 1388 | 500-4000 | 1.61 (0.18) | 0.98 (0.11) | True |

## turbo: winner both / hgb / gate off (best score 1820 ms ± 80; 2 tied)

| signals | classifier | gate | fit score (ms) | ladder | 3DMatch speed (risk %) | 3DLoMatch speed (risk %) | NI |
|---|---|---|---|---|---|---|---|
| both (tied) | hgb | on | 1820 | 250-2000-4000 | 1.68 (0.68) | 0.89 (0.11) | True |
| both **(winner)** | hgb | off | 1834 | 250-2000-4000 | 1.69 (0.68) | 0.87 (0.11) | True |
| verify | logit | on | 1943 | 500-2000-4000 | 1.48 (0.31) | 0.97 (0.00) | True |
| verify | hgb | on | 1981 | 250-2000-4000 | 1.61 (0.49) | 0.97 (0.00) | True |
| both | poly2 | on | 2018 | 250-500-4000 | 1.86 (0.55) | 1.03 (0.11) | True |
| verify | poly2 | on | 2020 | 500-4000 | 1.94 (0.49) | 1.06 (0.17) | True |
| both | poly2 | off | 2023 | 250-500-4000 | 1.87 (0.55) | 1.02 (0.11) | True |
| verify | poly2 | off | 2027 | 500-4000 | 1.95 (0.49) | 1.06 (0.17) | True |
| both | logit | on | 2035 | x4 | 1.58 (0.12) | 0.99 (0.06) | True |
| verify | hgb | off | 2044 | 250-2000-4000 | 1.60 (0.68) | 0.84 (0.11) | True |
| both | logit | off | 2059 | x4 | 1.56 (0.18) | 0.92 (0.11) | True |
| base | hgb | on | 2063 | 500-4000 | 1.77 (0.55) | 1.04 (0.17) | True |
| base | hgb | off | 2079 | 500-4000 | 1.77 (0.68) | 1.01 (0.22) | True |
| verify | logit | off | 2091 | 500-2000-4000 | 1.37 (0.43) | 0.78 (0.00) | True |
| base | poly2 | on | 2109 | 500-4000 | 1.78 (0.37) | 1.05 (0.06) | True |
| base | poly2 | off | 2137 | 500-4000 | 1.75 (0.37) | 1.00 (0.06) | True |
| base | logit | on | 2149 | 500-4000 | 1.47 (0.18) | 1.00 (0.06) | True |
| base | logit | off | 2175 | 500-4000 | 1.45 (0.18) | 0.97 (0.06) | True |
| geom | hgb | on | 2177 | 500-4000 | 1.62 (0.18) | 1.02 (0.00) | True |
| geom | hgb | off | 2194 | 500-4000 | 1.61 (0.18) | 0.99 (0.00) | True |
| geom | poly2 | on | 2198 | 250-500-4000 | 1.60 (0.18) | 1.02 (0.00) | True |
| geom | poly2 | off | 2244 | 250-500-4000 | 1.57 (0.18) | 0.96 (0.00) | True |
| geom | logit | on | 2320 | 500-4000 | 1.50 (0.12) | 1.01 (0.00) | True |
| geom | logit | off | 2352 | 500-4000 | 1.47 (0.12) | 0.97 (0.00) | True |
