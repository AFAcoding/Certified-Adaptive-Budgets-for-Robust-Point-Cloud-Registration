#!/usr/bin/env bash
# Component ablation of the final method on the earlier (non-blind) test sets: CAB without the gate (v2, existing
# selections), + classifier chosen on the fitting pairs (--controller auto), + gate with the logistic controller
# (--gate), and the final method (both, existing selections). Compatibility order. No timing involved.
# Usage: bash scripts/run_ablation_v3.sh > logs/ablation_v3.log 2>&1
set -uo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-./.venv/Scripts/python.exe}
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
for ds in v2_indoor_fpfh v2_kitti_fpfh v2_indoor_fcgf v2_kitti_fcgf; do
  for opt in "--controller auto" "--gate"; do
    tag=$([ "$opt" = "--gate" ] && echo _gate || echo _ctlauto)
    [ -f results/budget/ladder_selection_compat_ext_${ds}${tag}.json ] && continue
    while [ "$(jobs -rp | wc -l)" -ge 5 ]; do sleep 20; done
    echo "[$(date +%H:%M)] $ds $opt"
    $PY -I scripts/select_ladder.py --prefix budgetc --ladders extended --dataset $ds $opt > logs/sel_${ds}_budgetc${tag}.txt 2>&1 &
  done
done
wait
echo "[$(date +%H:%M)] done"
echo "exit 0"
