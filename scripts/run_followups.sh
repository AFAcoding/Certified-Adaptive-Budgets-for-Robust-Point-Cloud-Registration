#!/usr/bin/env bash
# Follow-up jobs after the main search logs: registrability pre-check and progressive-voting logs.
# Usage: bash scripts/run_followups.sh <main-chain output file to wait for>
set -e
cd "$(dirname "$0")/.."
PY=./.venv/Scripts/python.exe
if [ -n "$1" ]; then
  while ! grep -q ALL_DONE "$1" 2>/dev/null; do sleep 60; done
fi
for s in 3DMatch 3DLoMatch train; do
  OMP_NUM_THREADS=1 $PY -I scripts/precheck.py --subset $s
done
for s in val 3DMatch 3DLoMatch; do
  $PY -I -u scripts/build_search_logs.py --subset $s --variant psh --workers 6
done
$PY -I -u scripts/build_search_logs.py --subset train --sample 2000 --variant psh --workers 6
echo FOLLOWUPS_DONE
