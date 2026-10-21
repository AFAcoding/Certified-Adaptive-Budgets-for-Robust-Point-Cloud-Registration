#!/usr/bin/env bash
# Everything downstream of the certified selections (select_ladder.py), after the selection was changed to
# "choose on the fitting pairs, certify only the choice": offline analyses first, then the live timing of the new
# configurations on an otherwise idle machine (300 pairs per set), then the paper's assets.
# The previous results stay in results/budget/legacy_calibration_selection/.
# Usage: bash scripts/run_after_selection_fix.sh > logs/after_selection_fix.log 2>&1
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-./.venv/Scripts/python.exe}
R=results/budget
L=$R/legacy_calibration_selection
mkdir -p $L
for f in live_budget_compare_ext.json live_budget_compare_ext_kitti.json live_budget_compare_ext_fcgf3dmatch_refit.json \
         live_equal_time_3DMatch.json; do
  [ -f $L/$f ] || cp $R/$f $L/$f
done
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
echo "[$(date +%H:%M)] certified selections"
for ds in 3dmatch kitti fcgf3dmatch fcgfkitti fcgf3dmatch_refit; do
  for pf in budget budgetc; do
    $PY -I scripts/select_ladder.py --prefix $pf --ladders extended --dataset $ds > logs/sel_${ds}_${pf}.txt
  done
done
echo "[$(date +%H:%M)] offline analyses"
$PY -I -u scripts/evaluate_transfer.py
$PY -I -u scripts/summarize_budget_final.py || echo "summarize_budget_final.py failed (docs only)"
$PY -I -u scripts/fcgf_scene_disjoint.py
$PY -I -u scripts/calibration_size.py
$PY -I -u scripts/sensitivity.py
$PY -I -u scripts/evidence_extra.py
unset OPENBLAS_NUM_THREADS OMP_NUM_THREADS
echo "[$(date +%H:%M)] live timing"
PYTHON=$PY bash scripts/run_live_300.sh
echo "[$(date +%H:%M)] paper assets"
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 $PY -I scripts/paper_assets.py
echo "[$(date +%H:%M)] all done"
