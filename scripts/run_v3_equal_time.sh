#!/usr/bin/env bash
# Protocol v3: equal-time comparison re-timed with the final method (CAB with its classifier chosen on the fitting
# pairs and the hardness gate), same pairs and variants as the v2 run; after run_v3_reeval.sh, on an idle machine.
set -uo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-./.venv/Scripts/python.exe}
until grep -q "^exit" logs/v3_reeval.log 2>/dev/null; do sleep 60; done
echo "[$(date +%H:%M)] live equal-time, method v3, v2 blind indoor"
$PY -I -u scripts/live_equal_time.py --per-set 300 --subset v2_blind_hi --dataset v2_indoor_fpfh --method v3
echo "[$(date +%H:%M)] done"
echo "exit 0"
