#!/usr/bin/env bash
# Protocol v2 (PROTOCOL.md), data stage after the indoor FPFH logs (run_v2_indoor_fpfh.sh) and the scan downloads
# (kitti_raw_v2.py fetch, fetch-odometry): ICP ground truth of the KITTI raw pairs, every new budget log (FPFH on the
# raw drives, FCGF everywhere), and the equal-time logs on the blind indoor test. One heavy job at a time.
# Usage: bash scripts/run_v2_data.sh > logs/v2_data.log 2>&1
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-./.venv/Scripts/python.exe}
until grep -q "^exit" logs/v2_indoor_fpfh.log 2>/dev/null; do sleep 60; done
grep -q "^exit 0" logs/v2_indoor_fpfh.log
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 ACPR_KD_WORKERS=1
echo "[$(date +%H:%M)] KITTI raw: ICP ground truth"
$PY -I -u scripts/kitti_raw_v2.py refine --threads 6
$PY -I -u scripts/kitti_raw_v2.py metadata
for n in kitti_raw_blind fcgfown_kitti_fit fcgfown_kitti_test fcgfown_kitti_raw_cal fcgfown_kitti_raw_blind \
         fcgfown_v2_fit fcgfown_val fcgfown_3DMatch fcgfown_3DLoMatch; do
  echo "[$(date +%H:%M)] logs $n"
  $PY -I -u scripts/build_logs_v2.py --name $n --workers 6
done
echo "[$(date +%H:%M)] equal-time logs, blind indoor (every second pair)"
$PY -I -u scripts/build_equal_time_logs.py --subset v2_blind_hi --workers 6 --every 2
echo "[$(date +%H:%M)] done"
