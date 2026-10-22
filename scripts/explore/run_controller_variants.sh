#!/usr/bin/env bash
# Exploration sweep (development data only): controller classifiers x datasets, compatibility order.
set -uo pipefail
cd "$(dirname "$0")/../.."
PY=${PYTHON:-./.venv/Scripts/python.exe}
export OPENBLAS_NUM_THREADS=4 OMP_NUM_THREADS=4
for v in logit hgb poly2 logit_c01; do
  for ds in v2_indoor_fpfh v2_kitti_fpfh v2_indoor_fcgf; do
    $PY -I -u scripts/explore/controller_variants.py $v $ds budgetc || echo "FAILED $v $ds"
  done
done
echo exit
