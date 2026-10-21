#!/usr/bin/env bash
# Protocol v2 (PROTOCOL.md), analysis stage after run_v2_data.sh: every certified selection (written to disk before
# anything is timed), the supplementary studies (development benchmarks only), then the live timing of every dataset
# on an otherwise idle machine (300 random test pairs per set) and the re-timing of stalled measurements.
# Usage: bash scripts/run_v2_analysis.sh > logs/v2_analysis.log 2>&1
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-./.venv/Scripts/python.exe}
until grep -q "^exit" logs/v2_data.log 2>/dev/null; do sleep 60; done
grep -q "^exit 0" logs/v2_data.log
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
echo "[$(date +%H:%M)] certified selections"
for ds in v2_indoor_fpfh v2_kitti_fpfh v2_indoor_fcgf v2_kitti_fcgf; do
  for pf in budget budgetc; do
    sfx=$([ $pf = budgetc ] && echo _compat || echo "")
    [ -f results/budget/ladder_selection${sfx}_ext_${ds}.json ] ||       $PY -I scripts/select_ladder.py --prefix $pf --ladders extended --dataset $ds > logs/sel_${ds}_${pf}.txt
    for rho in 0.10 0.25; do
      r=$([ $rho = 0.10 ] && echo 010 || echo 025)
      [ -f results/budget/ladder_selection${sfx}_ext_${ds}_rho${r}.json ] ||         $PY -I scripts/select_ladder.py --prefix $pf --ladders extended --dataset $ds --rho $rho > logs/sel_${ds}_${pf}_rho${rho}.txt
    done
  done
done
echo "[$(date +%H:%M)] supplementary studies"
$PY -I -u scripts/calibration_size.py > logs/v2_calibration_size.txt
$PY -I -u scripts/sensitivity.py > logs/v2_sensitivity.txt
$PY -I -u scripts/evidence_extra.py > logs/v2_evidence_extra.txt
unset OPENBLAS_NUM_THREADS OMP_NUM_THREADS
for ds in v2_indoor_fpfh v2_kitti_fpfh v2_indoor_fcgf v2_kitti_fcgf; do
  echo "[$(date +%H:%M)] live $ds"
  $PY -I -u scripts/live_budget.py --per-set 300 --prefixes budget,budgetc --ladders extended --dataset $ds
done
echo "[$(date +%H:%M)] live equal-time, blind indoor"
$PY -I -u scripts/live_equal_time.py --per-set 300 --subset v2_blind_hi --dataset v2_indoor_fpfh
echo "[$(date +%H:%M)] re-time stalled pairs"
$PY -I -u scripts/retime_stalls.py
echo "[$(date +%H:%M)] done"
