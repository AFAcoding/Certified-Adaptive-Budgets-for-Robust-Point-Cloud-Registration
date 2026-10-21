#!/usr/bin/env bash
# Part B final analysis, after the cost-accounting fix of 2026-10-17 (trajectory_ladder):
#   1. archive the pre-fix outputs (results/budget/pre_fix/) for an old-vs-corrected comparison
#   2. certified selection on validation + one test evaluation:
#        ratio order, original candidate ladders (the published Part B configuration)
#        ratio order, extended ladders (control for the ordering study)
#        compatibility order, extended ladders (the new study, design frozen on validation)
#   3. report, oracle/unsolvable figure
#   4. live single-process benchmark: full budget vs ratio-order vs compatibility-order adaptive
#   5. if the corrected original selection differs from the pre-fix one, a live run of it too
# Usage: bash scripts/run_budget_final.sh [--wait]   (--wait: block until the compat logs are complete)
set -euo pipefail
cd "$(dirname "$0")/.."
PY=./.venv/Scripts/python.exe
R=results/budget
if [ "${1:-}" = "--wait" ]; then
  until [ -f logs/budgetc_3DLoMatch.jsonl ] && [ "$(wc -l < logs/budgetc_3DLoMatch.jsonl)" -ge 1781 ]; do sleep 30; done
  sleep 90  # let the worker pool exit
fi
mkdir -p $R/pre_fix
for f in ladder_selection.md ladder_selection.json ladder_selection_ext.md ladder_selection_ext.json report.md \
         summary.json fig_budget_insight.png live_budget.json; do
  [ -f $R/$f ] && [ ! -f $R/pre_fix/$f ] && cp $R/$f $R/pre_fix/$f
done
echo "[$(date +%H:%M:%S)] selection: ratio order, original ladders"
$PY -I scripts/select_ladder.py > $R/ladder_selection_stdout.txt
echo "[$(date +%H:%M:%S)] selection: ratio order, extended ladders"
$PY -I scripts/select_ladder.py --prefix budget --ladders extended > $R/ladder_selection_ext_stdout.txt
echo "[$(date +%H:%M:%S)] selection: compatibility order, extended ladders"
$PY -I scripts/select_ladder.py --prefix budgetc --ladders extended > $R/ladder_selection_compat_ext_stdout.txt
echo "[$(date +%H:%M:%S)] report + figure"
$PY -I scripts/analyze_budget.py > $R/report_stdout.txt
$PY -I scripts/budget_figure.py > $R/fig_budget_insight_stdout.txt
echo "[$(date +%H:%M:%S)] live benchmark: full vs ratio-order vs compatibility-order adaptive"
$PY -I -u scripts/live_budget.py --per-set 100 --prefixes budget,budgetc --ladders extended > $R/live_budget_compare_ext_stdout.txt
same=$($PY -I -c "
import json
a = json.load(open('$R/pre_fix/ladder_selection.json')); b = json.load(open('$R/ladder_selection.json'))
key = lambda d, e: (d[e]['selected']['mondrian']['ladder'], json.dumps(d[e]['selected']['mondrian']['param']))
print(int(all(key(a, e) == key(b, e) for e in ('sc2', 'turbo'))))")
if [ "$same" = "1" ]; then
  echo "[$(date +%H:%M:%S)] original selection unchanged by the fix: existing live_budget.json still applies"
else
  echo "[$(date +%H:%M:%S)] original selection changed by the fix: live benchmark of the corrected configuration"
  $PY -I -u scripts/live_budget.py --per-set 100 > $R/live_budget_stdout.txt
fi
echo "[$(date +%H:%M:%S)] done"
