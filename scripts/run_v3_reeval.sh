#!/usr/bin/env bash
# Protocol v3: re-run the method-v3 selections with the corrected (conservative) reporting of the gate's cost
# (select_ladder.gate_eval_charges; the method itself is unchanged), then the remaining live timing and re-timing.
# Usage: bash scripts/run_v3_reeval.sh > logs/v3_reeval.log 2>&1
set -uo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-./.venv/Scripts/python.exe}
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
for pf in budget budgetc; do
  for ds in v3_indoor_fpfh v2_indoor_fpfh v2_kitti_fpfh v2_indoor_fcgf v2_kitti_fcgf; do
    while [ "$(jobs -rp | wc -l)" -ge 5 ]; do sleep 20; done
    echo "[$(date +%H:%M)] selection $ds $pf"
    $PY -I scripts/select_ladder.py --prefix $pf --ladders extended --dataset $ds --controller auto --gate \
      > logs/sel_${ds}_${pf}_ctlauto_gate.txt 2>&1 &
  done
done
wait
unset OPENBLAS_NUM_THREADS OMP_NUM_THREADS
echo "[$(date +%H:%M)] live method v3 on v2_kitti_fcgf"
$PY -I -u scripts/live_budget.py --per-set 300 --prefixes budget+v3,budgetc+v3 --ladders extended --dataset v2_kitti_fcgf
echo "[$(date +%H:%M)] re-time stalled pairs"
$PY -I -u scripts/retime_stalls.py
echo "[$(date +%H:%M)] done"
echo "exit 0"
