#!/usr/bin/env bash
# FCGF re-certification. The FPFH-certified configurations do not transfer to FCGF (risk 4-12 % on
# 3DMatch/3DLoMatch, transfer_fcgf.md), so the stopping thresholds are re-certified on held-out FCGF pairs:
#   1. logs of the odd-indexed FCGF test pairs (the even-indexed ones are the test logs)
#   2. selection: controller fitted on FPFH training logs, certified on the odd pairs, tested on the even pairs
#   3. live benchmark of the re-certified configurations
# Usage: bash scripts/run_fcgf_recal.sh > logs/pipeline_recal.log 2>&1   (waits for run_paper_final.sh)
set -uo pipefail
cd "$(dirname "$0")/.."
PY=./.venv/Scripts/python.exe
R=results/budget
until grep -q -E "\] exit|Traceback" logs/pipeline_resume.log; do sleep 30; done
for s in 3DMatch 3DLoMatch kitti_test; do
  echo "[$(date +%H:%M)] fcgf calibration logs $s"
  $PY -I -u scripts/build_budget_logs_fcgf.py --set $s --workers 6 --every 2 --offset 1 2>&1 | grep -E --line-buffered "pairs to run|ETA 0s|Error|error|Traceback" || exit 1
done
for ds in fcgf3dmatch fcgfkitti; do
  echo "[$(date +%H:%M)] selection $ds"
  $PY -I scripts/select_ladder.py --prefix budget --ladders extended --dataset $ds > $R/ladder_selection_ext_${ds}_stdout.txt 2>&1 || exit 1
  $PY -I scripts/select_ladder.py --prefix budgetc --ladders extended --dataset $ds > $R/ladder_selection_compat_ext_${ds}_stdout.txt 2>&1 || exit 1
done
for ds in fcgf3dmatch fcgfkitti; do
  echo "[$(date +%H:%M)] live $ds (re-certified)"
  $PY -I -u scripts/live_budget.py --per-set 100 --prefixes budget,budgetc --ladders extended --dataset $ds --recal > $R/live_compare_ext_${ds}_recal_stdout.txt 2>&1 || exit 1
done
echo "[$(date +%H:%M)] recal done"
