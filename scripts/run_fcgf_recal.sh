#!/usr/bin/env bash
# FCGF protocols after the FCGF test logs (even-indexed pairs) exist. The FPFH-certified configurations do not
# transfer to FCGF (results/budget/transfer_fcgf.md), so:
#   1. logs of the odd-indexed FCGF test pairs (held-out pool)
#   2. thresholds re-certified on the pool, FPFH controller unchanged (finds nothing cheaper than the full budget)
#   3. controller re-fitted on a quarter of the pool and certified on the rest (3DMatch/3DLoMatch; Table 1)
#   4. live benchmark of the re-fitted configurations
# Usage: bash scripts/run_fcgf_recal.sh
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-python}  # set PYTHON to use another interpreter
for s in 3DMatch 3DLoMatch kitti_test; do
  echo "[$(date +%H:%M)] fcgf held-out logs $s"
  $PY -I -u scripts/build_budget_logs_fcgf.py --set $s --workers 6 --every 2 --offset 1
done
for ds in fcgf3dmatch fcgfkitti; do
  echo "[$(date +%H:%M)] thresholds re-certified: $ds"
  $PY -I scripts/select_ladder.py --prefix budget --ladders extended --dataset $ds
  $PY -I scripts/select_ladder.py --prefix budgetc --ladders extended --dataset $ds
done
echo "[$(date +%H:%M)] controller re-fitted and re-certified"
$PY -I scripts/split_fcgf_cal.py
$PY -I scripts/select_ladder.py --prefix budget --ladders extended --dataset fcgf3dmatch_refit
$PY -I scripts/select_ladder.py --prefix budgetc --ladders extended --dataset fcgf3dmatch_refit
echo "[$(date +%H:%M)] live timing (re-fitted)"
$PY -I -u scripts/live_budget.py --per-set 100 --prefixes budget,budgetc --ladders extended --dataset fcgf3dmatch --refit
echo "[$(date +%H:%M)] done"
