#!/usr/bin/env bash
# Protocol v3, addendum D: MAC in the equal-time comparison. Offline variant logs (held-out scenes above 30 % overlap,
# 3DLoMatch), then live timing of the same 300 held-out pairs as for SC2-PCR and TurboReg, on an otherwise idle machine.
set -uo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-./.venv/Scripts/python.exe}
for subset in v2_blind_hi 3DLoMatch; do
  echo "[$(date +%H:%M)] offline MAC variants, $subset"
  $PY -I -u scripts/build_equal_time_logs.py --subset $subset --workers 6 --estimator mac || { echo "exit 1"; exit 1; }
done
echo "[$(date +%H:%M)] live equal-time, MAC, method v3, v2 blind indoor"
$PY -I -u scripts/live_equal_time.py --per-set 300 --subset v2_blind_hi --dataset v2_indoor_fpfh --method v3 --estimators mac || { echo "exit 1"; exit 1; }
echo "[$(date +%H:%M)] done"
echo "exit 0"
