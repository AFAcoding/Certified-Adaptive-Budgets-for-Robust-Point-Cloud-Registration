#!/usr/bin/env bash
# Exploration (fitting, calibration and development data only): factorial study of the controller's signals
# {base, verify, geom, both} x classifier {logit, poly2, hgb} x estimator {sc2, turbo}; every run also evaluates the
# hardness gate on top (gate off / on), so 48 configurations. Selection rule, fixed before any result: lowest
# out-of-fold cost on the fitting pairs, and among configurations within one standard error of it the simplest
# (fewest extra signals, then logit < poly2 < hgb, then no gate); development benchmarks only check
# non-inferiority, risk and overhead. Starts after the paper's timing runs (logs/v3_equal_time.log) so that no
# timed measurement is disturbed.
# Usage: bash scripts/explore/run_v4_factorial.sh > logs/explore/v4_factorial.log 2>&1
set -uo pipefail
cd "$(dirname "$0")/../.."
PY=${PYTHON:-./.venv/Scripts/python.exe}
until grep -q "^exit" logs/v3_equal_time.log 2>/dev/null; do sleep 60; done
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
for f in base verify geom both; do
  for c in logit poly2 hgb; do
    for e in sc2 turbo; do
      while [ "$(jobs -rp | wc -l)" -ge 6 ]; do sleep 20; done
      out=results/explore/controller_features_${f}_${e}_${c}.json
      [ -f "$out" ] && continue
      echo "[$(date +%H:%M)] $f $c $e"
      $PY -I scripts/explore/controller_features.py $f $e $c > logs/explore/cf_${f}_${e}_${c}.log 2>&1 &
    done
  done
done
wait
echo "[$(date +%H:%M)] done"
echo "exit 0"
