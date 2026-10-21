#!/usr/bin/env bash
# Live timing on 300 test pairs per set (instead of 100), on an otherwise idle machine.
# The 100-pair results are kept in results/budget/live_100pairs/. Pairs whose timing was interrupted by a
# system stall are timed again at the end (scripts/retime_stalls.py).
# Usage: bash scripts/run_live_300.sh > logs/live_300.log 2>&1
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-./.venv/Scripts/python.exe}
R=results/budget
mkdir -p $R/live_100pairs
for f in live_budget_compare_ext.json live_budget_compare_ext_kitti.json live_budget_compare_ext_fcgf3dmatch_refit.json \
         live_equal_time_3DMatch.json; do
  [ -f $R/live_100pairs/$f ] || cp $R/$f $R/live_100pairs/$f
done
echo "[$(date +%H:%M)] live 3DMatch/3DLoMatch"
$PY -I -u scripts/live_budget.py --per-set 300 --prefixes budget,budgetc --ladders extended
echo "[$(date +%H:%M)] live KITTI"
$PY -I -u scripts/live_budget.py --per-set 300 --prefixes budget,budgetc --ladders extended --dataset kitti
echo "[$(date +%H:%M)] live FCGF (re-fitted)"
$PY -I -u scripts/live_budget.py --per-set 300 --prefixes budget,budgetc --ladders extended --dataset fcgf3dmatch --refit
echo "[$(date +%H:%M)] live equal-time"
$PY -I -u scripts/live_equal_time.py --per-set 300
echo "[$(date +%H:%M)] re-time stalled pairs"
$PY -I -u scripts/retime_stalls.py
echo "[$(date +%H:%M)] done"
