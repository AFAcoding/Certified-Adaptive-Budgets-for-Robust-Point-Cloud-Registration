#!/usr/bin/env bash
# Protocol v3, addenda A and B (PROTOCOL.md): MAC on every family of test sets, in the pre-registered order, family by
# family (indoor FPFH, KITTI FPFH, indoor FCGF, KITTI FCGF): logs of the fitting and calibration pairs, every selection
# written to disk, then the test logs, the single evaluation (which must reproduce the selections) and live timing of
# the test sets on an otherwise idle machine; finally the re-timing of stalled pairs.
# Usage: [WORKERS=6] [FROM=1] bash scripts/run_mac_families.sh > logs/mac_all.log 2>&1
# (the indoor FPFH family ran with WORKERS=6; the other families with WORKERS=8 FROM=2, logs/mac_rest.log)
set -uo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-./.venv/Scripts/python.exe}
WORKERS=${WORKERS:-6}  # parallel workers of the log builder (each family is built with one setting)
FROM=${FROM:-1}  # first family to run (1 indoor FPFH, 2 KITTI FPFH, 3 indoor FCGF, 4 KITTI FCGF)
ONE="env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 ACPR_KD_WORKERS=1"
fail() { echo "FAILED: $*"; echo "exit 1"; exit 1; }

logs() {  # MAC logs of the given subsets, then merged into their budget logs
  for s in "$@"; do
    echo "[$(date +%H:%M)] MAC logs $s"
    $ONE $PY -I -u scripts/build_mac_logs.py --subset "$s" --workers "$WORKERS" || fail "logs $s"
  done
  $PY -I scripts/merge_mac_logs.py "$@" || fail "merge $*"
}

select_all() {  # $1 dataset, $2 extra flag (--no-tests while no test log exists): CAB without the gate, final method
  local tag=""; [ "${2:-}" = "--no-tests" ] && tag="_sel"
  for pf in budget budgetc; do
    $ONE $PY -I scripts/select_ladder.py --prefix $pf --ladders extended --dataset "$1" --estimators mac ${2:-} \
      > "logs/sel_${1}_${pf}_mac${tag}.txt" 2>&1 &
    $ONE $PY -I scripts/select_ladder.py --prefix $pf --ladders extended --dataset "$1" --estimators mac ${2:-} \
      --controller auto --gate > "logs/sel_${1}_${pf}_ctlauto_gate_mac${tag}.txt" 2>&1 &
    wait
  done
  for c in "" "_compat"; do
    for v in "" "_ctlauto_gate"; do
      f=results/budget/ladder_selection${c}_ext_${1}${v}_mac
      if [ "${2:-}" = "--no-tests" ]; then
        [ -f "${f}_selection_only.json" ] || fail "selection missing: ${f}_selection_only.json"
      else
        $PY -I scripts/check_same_selection.py "${f}_selection_only.json" "${f}.json" || fail "selection changed: $f"
      fi
    done
  done
}

live() {  # $1 dataset, $2 comma-separated test subsets; not timed if every MAC configuration is the full budget
  if $PY -I -c "import json,sys; d='results/budget/ladder_selection_compat_ext_$1'; \
      sys.exit(0 if all(json.load(open(d + v + '_mac.json'))['mac']['selected']['mondrian']['ladder'] == 'full' \
      for v in ('', '_ctlauto_gate')) else 1)"; then
    echo "[$(date +%H:%M)] live $1: every configuration is the full budget, not timed"
    return
  fi
  echo "[$(date +%H:%M)] live MAC $1 ($2)"
  $PY -I -u scripts/live_budget.py --per-set 300 --prefixes budgetc,budgetc+v3 --ladders extended --dataset "$1" \
    --subsets "$2" --estimators mac || fail "live $1"
}

family() {  # $1 name, $2 fitting and calibration subsets, $3 datasets, $4 test subsets, $5 live specs dataset:subsets
  echo "[$(date +%H:%M)] === family $1"
  logs $2
  echo "[$(date +%H:%M)] selections, no test pair processed yet"
  for ds in $3; do select_all "$ds" --no-tests; done
  logs $4
  echo "[$(date +%H:%M)] evaluation"
  for ds in $3; do select_all "$ds"; done
  for spec in $5; do live "${spec%%:*}" "${spec#*:}"; done
}

echo "[$(date +%H:%M)] start (workers $WORKERS, from family $FROM)"
[ "$FROM" -le 1 ] && family "indoor FPFH" "v3_fit v2_fit v2_cal" "v3_indoor_fpfh v2_indoor_fpfh" \
  "v3_blind_hi v3_blind_lo v2_blind_hi v2_blind_lo 3DMatch 3DLoMatch" \
  "v3_indoor_fpfh:v3_blind_hi,v3_blind_lo v2_indoor_fpfh:v2_blind_hi,v2_blind_lo,3DMatch,3DLoMatch"
[ "$FROM" -le 2 ] && family "KITTI FPFH" "kitti_train kitti_val kitti_calib" "v2_kitti_fpfh" "kitti_raw_blind kitti_test" \
  "v2_kitti_fpfh:kitti_raw_blind,kitti_test"
[ "$FROM" -le 3 ] && family "indoor FCGF" "fcgfown_v2_fit fcgfown_val" "v2_indoor_fcgf" "fcgfown_3DMatch fcgfown_3DLoMatch" \
  "v2_indoor_fcgf:fcgfown_3DMatch,fcgfown_3DLoMatch"
[ "$FROM" -le 4 ] && family "KITTI FCGF" "fcgfown_kitti_fit fcgfown_kitti_raw_cal" "v2_kitti_fcgf" "fcgfown_kitti_raw_blind fcgfown_kitti_test" \
  "v2_kitti_fcgf:fcgfown_kitti_raw_blind,fcgfown_kitti_test"
echo "[$(date +%H:%M)] re-time stalled pairs"
$PY -I -u scripts/retime_stalls.py
echo "[$(date +%H:%M)] done"
echo "exit 0"
