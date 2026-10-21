#!/usr/bin/env bash
# Protocol v2, indoor FPFH logs: fitting (top-up), calibration and blind-test pairs, ratio then compatibility order.
# Usage: bash scripts/run_v2_indoor_fpfh.sh > logs/v2_indoor_fpfh.log 2>&1
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-./.venv/Scripts/python.exe}
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 ACPR_KD_WORKERS=1
for s in v2_fit v2_cal v2_blind_hi v2_blind_lo; do
  for o in ratio compat; do
    echo "[$(date +%H:%M)] $s $o"
    $PY -I -u scripts/build_budget_logs.py --subset $s --workers 6 --order $o
  done
done
echo "[$(date +%H:%M)] done"
