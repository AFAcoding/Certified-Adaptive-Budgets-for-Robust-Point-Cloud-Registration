#!/usr/bin/env bash
# Final evaluation for the paper, after all logs exist:
#   1. KITTI: certified selection on validation (ratio and compatibility order), single test evaluation
#   2. FCGF: transfer of the FPFH-certified configurations (evaluate_transfer.py)
#   3. live single-process benchmarks, one at a time on a quiet machine:
#        KITTI (FPFH), FCGF 3DMatch/3DLoMatch, FCGF KITTI, equal-time variants on 3DMatch
#   4. every number, table and figure of the paper (paper_assets.py)
# Usage: bash scripts/run_paper_final.sh [--skip-kitti-selection]
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-python}  # set PYTHON to use another interpreter
R=results/budget
if [ "${1:-}" != "--skip-kitti-selection" ]; then
  echo "[$(date +%H:%M)] KITTI selection"
  $PY -I scripts/select_ladder.py --prefix budget --ladders extended --dataset kitti > $R/ladder_selection_ext_kitti_stdout.txt
  $PY -I scripts/select_ladder.py --prefix budgetc --ladders extended --dataset kitti > $R/ladder_selection_compat_ext_kitti_stdout.txt
fi
echo "[$(date +%H:%M)] FCGF transfer"
$PY -I scripts/evaluate_transfer.py > $R/transfer_fcgf_stdout.txt
for ds in kitti fcgf3dmatch fcgfkitti; do
  echo "[$(date +%H:%M)] live $ds"
  $PY -I -u scripts/live_budget.py --per-set 100 --prefixes budget,budgetc --ladders extended --dataset $ds > $R/live_compare_ext_${ds}_stdout.txt
done
echo "[$(date +%H:%M)] live equal-time"
$PY -I -u scripts/live_equal_time.py --per-set 100 > $R/live_equal_time_stdout.txt
echo "[$(date +%H:%M)] paper assets"
$PY -I scripts/paper_assets.py > $R/paper_assets_stdout.txt
echo "[$(date +%H:%M)] done"
