# Exploration after protocol v2 (development data only, 2026-10-21)

Blind v2 test sets were never loaded. Offline speed-up (risk %) of CAB, compatibility order, group-conditional.

## E1 controller classifier (`scripts/explore/controller_variants.py`)
Choice rule that is legitimate without test data: lowest fitting-pair cost (`fit`, ms).

| dataset / est | logit (paper) | logit C=0.1 | poly2 | hgb |
|---|---|---|---|---|
| indoor FPFH SC² fit / 3DMatch / 3DLoMatch | 1285 / 1.55 (0.12) / 0.97 | 1304 / 1.54 / 0.97 | 1254 / 1.58 (0.06) / 0.98 | **1235 / 1.69 (0.37) / 1.00** |
| indoor FPFH Turbo | 2175 / 1.45 (0.18) / 0.97 | 2211 / 1.52 / 0.98 | 2137 / 1.75 (0.37) / 1.00 | **2079 / 1.77 (0.68) / 1.01** |
| KITTI FPFH SC² / kitti_test | 3074 / 1.15 (0.18) | 3050 / 1.12 | **3032 / 1.21 (0.54)** | 3553 / 1.03 |
| KITTI FPFH Turbo | 3964 / 1.14 (0.36) | **3845 / 1.08 (0.18)** | 3864 / 1.09 | 4295 / 1.16 |
| FCGF indoor SC² / 3DMatch / 3DLoMatch | 1229 / 1.06 / 1.13 | 1270 / 1.06 / 1.13 | **1175 / 1.02 / 1.06** | 1186 / 1.03 / 1.06 |
| FCGF indoor Turbo | 2192 / 1.05 / 1.10 | 2279 / 1.07 / 1.16 | 1984 / 1.07 / 1.17 (0.79) | **1691 / 1.04 / 1.10** |

Fit-chosen variant (bold): indoor FPFH gains +9 % (SC²) and +22 % (TurboReg) on 3DMatch; other sets mixed (±5 %).
All risks stay below 1 % (max 0.79 %).

## E2 hardness gate (`gate_features.py`, `gate_eval.py`)
Pre-estimation signals only; gated pairs run the full budget, so risk can only fall.
3DLoMatch 0.97 → 1.01 (SC²), 0.97 → 0.99–1.00 (Turbo); 3DMatch +1–2 %. Risk never increased.

## E3 ordering chosen on fitting pairs
KITTI picks the ratio order (dev 1.15/1.14 → 1.28/1.51 offline); FCGF TurboReg would pick ratio (1.05 → 0.99).

## Next
Combine fit-chosen controller + gate + rho = 0.25 + fit-chosen ordering into one pipeline, choose every option on
fitting pairs only, then pre-register protocol v3 with a fresh blind set (unused pairs of the held-out scenes and new
raw drives) before evaluating it.
