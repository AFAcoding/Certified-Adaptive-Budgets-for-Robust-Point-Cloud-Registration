#!/usr/bin/env bash
# Protocol v3 (PROTOCOL.md): logs of the fresh blind scenes and the new fitting pairs, gate signals, every selection
# (method v2 and method v3 on the v3 split; method v3 on every v2 dataset), then live timing on an otherwise idle
# machine and the re-timing of stalled measurements. Every step resumes or is skipped if its output exists.
# Usage: bash scripts/run_v3.sh > logs/v3.log 2>&1   (after run_gate_features_v2.sh)
set -uo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-./.venv/Scripts/python.exe}
until grep -q "^exit" logs/gate_features_v2.log 2>/dev/null; do sleep 60; done
# the logs record per-stage times: start only when no other experiment process is running
others() {
  powershell.exe -NoProfile -Command "(Get-CimInstance Win32_Process | Where-Object { \$_.Name -eq 'python.exe' -and \$_.CommandLine -match 'select_ladder|controller_variants|gate_eval|live_budget' }).Count" | tr -d '\r'
}
until [ "$(others)" = "0" ]; do sleep 60; done
echo "[$(date +%H:%M)] machine idle, starting"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 ACPR_KD_WORKERS=1
for s in v3_fit v3_blind_hi v3_blind_lo; do
  for o in ratio compat; do
    echo "[$(date +%H:%M)] logs $s $o"
    $PY -I -u scripts/build_budget_logs.py --subset $s --workers 6 --order $o || { echo "exit 1"; exit 1; }
  done
done
for s in v3_fit v3_blind_hi v3_blind_lo; do
  echo "[$(date +%H:%M)] gate signals $s"
  $PY -I -u scripts/gate_features.py --name $s --workers 6 || { echo "exit 1"; exit 1; }
done
sel() {  # dataset prefix [extra args]
  local ds=$1 pf=$2; shift 2
  local sfx; sfx=$([ $pf = budgetc ] && echo _compat || echo "")
  local tag; tag=$([ $# -gt 0 ] && echo "_ctlauto_gate" || echo "")
  if [ ! -f results/budget/ladder_selection${sfx}_ext_${ds}${tag}.json ]; then
    echo "[$(date +%H:%M)] selection $ds $pf $*"
    $PY -I scripts/select_ladder.py --prefix $pf --ladders extended --dataset $ds "$@" > logs/sel_${ds}_${pf}${tag}.txt \
      || { echo "exit 1"; exit 1; }
  fi
}
# selections only read the logs (no timing), so they run in parallel, five at a time
jobs_=()
for pf in budget budgetc; do
  jobs_+=("v3_indoor_fpfh $pf" "v3_indoor_fpfh $pf --controller auto --gate")
  for ds in v2_indoor_fpfh v2_kitti_fpfh v2_indoor_fcgf v2_kitti_fcgf; do
    jobs_+=("$ds $pf --controller auto --gate")
  done
done
for j in "${jobs_[@]}"; do
  while [ "$(jobs -rp | wc -l)" -ge 5 ]; do sleep 20; done
  sel $j &
done
wait
for j in "${jobs_[@]}"; do  # every selection must exist before anything is timed
  set -- $j
  sfx=$([ $2 = budgetc ] && echo _compat || echo ""); tag=$([ $# -gt 2 ] && echo _ctlauto_gate || echo "")
  [ -f results/budget/ladder_selection${sfx}_ext_$1${tag}.json ] || { echo "missing selection: $j"; echo "exit 1"; exit 1; }
done
unset OPENBLAS_NUM_THREADS OMP_NUM_THREADS ACPR_KD_WORKERS
echo "[$(date +%H:%M)] live v3 blind"
$PY -I -u scripts/live_budget.py --per-set 300 --prefixes budget,budgetc,budget+v3,budgetc+v3 --ladders extended \
  --dataset v3_indoor_fpfh --subsets v3_blind_hi,v3_blind_lo || { echo "exit 1"; exit 1; }
for ds in v2_indoor_fpfh v2_kitti_fpfh v2_indoor_fcgf v2_kitti_fcgf; do
  echo "[$(date +%H:%M)] live method v3 on $ds"
  $PY -I -u scripts/live_budget.py --per-set 300 --prefixes budget+v3,budgetc+v3 --ladders extended --dataset $ds \
    || { echo "exit 1"; exit 1; }
done
echo "[$(date +%H:%M)] re-time stalled pairs"
$PY -I -u scripts/retime_stalls.py
echo "[$(date +%H:%M)] done"
echo "exit 0"
