#!/usr/bin/env bash
# Gate signals (scripts/gate_features.py) for every logged split of protocol v2.
# Usage: bash scripts/run_gate_features_v2.sh > logs/gate_features_v2.log 2>&1
set -uo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-./.venv/Scripts/python.exe}
for n in v2_fit v2_cal v2_blind_hi v2_blind_lo 3DMatch 3DLoMatch kitti_train kitti_val kitti_calib kitti_test \
         kitti_raw_blind fcgfown_v2_fit fcgfown_val fcgfown_3DMatch fcgfown_3DLoMatch fcgfown_kitti_fit \
         fcgfown_kitti_raw_cal fcgfown_kitti_raw_blind fcgfown_kitti_test; do
  echo "[$(date +%H:%M)] $n"
  $PY -I -u scripts/gate_features.py --name $n --workers 6 || echo "FAILED $n"
done
echo "[$(date +%H:%M)] done"
echo exit
