# Certified Adaptive Budgets for Robust Point Cloud Registration

Code to reproduce the experiments of *Not All Pairs Need All Correspondences: Certified Adaptive Budgets for Robust Point Cloud Registration*.

**Certified adaptive budgets (CAB)** wrap an unchanged robust estimator (re-implemented SC²-PCR and TurboReg) in three steps:
- They run it on growing budgets of correspondences, ordered by mutual consistency.
- A learned controller stops as soon as it is confident.
- The stopping rule is certified per difficulty group with Learn-then-Test. With high probability, at most 1 % of the pairs the full estimator registers are lost.

Experiments cover 3DMatch, 3DLoMatch and KITTI, with FPFH and FCGF correspondences. They include live timing, an equal-time comparison against cheaper variants of the estimators, and a certified adaptive pose search (CAPS) in the supplementary material.

## Contents

| Path | What it is |
|---|---|
| `src/acpr/` | the library: data loading, FPFH/FCGF correspondences, SC²-PCR and TurboReg re-implementations, compatibility ordering, FastMAC-style sampling, pose search, controllers and Learn-then-Test certification |
| `scripts/` | every experiment, analysis and figure script (see the pipeline below) |
| `results/` | the selection reports (`*.md`/`*.json`), live timings and summaries that the paper's numbers come from |
| `scripts/download_logs.py` | downloads the per-pair logs of all experiments (88 MB zip from the v1.0 release) into `logs/` |

Datasets are not redistributed; the scripts below download or prepare them from their official sources.

## Setup

Tested with Python 3.13.3 on Windows 11, CPU only. The shell scripts use bash (Git Bash on Windows).

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .                   # the scripts run with python -I and import the installed acpr package
```

## Fast path: regenerate the numbers from the logs

The per-pair logs record every stage of every estimator on every pair. From them, all certified selections, test evaluations, tables and figures can be recomputed in minutes:

```bash
python -I scripts/download_logs.py                                       # -> logs/*.jsonl (52 files)
# certified selection on validation + single test evaluation (3DMatch/3DLoMatch, KITTI, FCGF)
python -I scripts/select_ladder.py --prefix {budget|budgetc} --ladders extended
python -I scripts/select_ladder.py --prefix {budget|budgetc} --ladders extended --dataset kitti
python -I scripts/evaluate_transfer.py                                   # FPFH certificates applied to FCGF
python -I scripts/select_ladder.py --prefix {budget|budgetc} --ladders extended --dataset {fcgf3dmatch|fcgfkitti}
python -I scripts/split_fcgf_cal.py
python -I scripts/select_ladder.py --prefix {budget|budgetc} --ladders extended --dataset fcgf3dmatch_refit
# further checks (all from the logs)
python -I scripts/fcgf_scene_disjoint.py   # FCGF calibrated on other scenes only (cross-fitting over scenes)
python -I scripts/calibration_size.py      # certification on random calibration subsets of growing size
python -I scripts/sensitivity.py           # risk level epsilon and number of difficulty groups
python -I scripts/evidence_extra.py        # group-wise and worst-case risk, per-scene results, re-fitted controllers
# every number, table and figure of the paper
python -I scripts/paper_assets.py                                        # -> paper/numbers.tex, paper/tables/, paper/figures/
```

`{a|b}` means "run once with each value". The outputs should match the files in `results/`.

Live speed-ups are wall-clock measurements on our machine (AMD Ryzen 7 5700U, 8 cores; `results/budget/live_*.json`, 300 test pairs per set). On other hardware, re-measure them with `bash scripts/run_live_300.sh` on an otherwise idle machine.

## Full rerun from the data

Expect several days on a laptop CPU. The log builders run 6 worker processes with single-threaded BLAS; run one builder at a time.

**1. Data**
- **3DMatch / 3DLoMatch:**
  - Predator's preprocessed archive (`data.zip`, linked in the [OverlapPredator](https://github.com/prs-eth/OverlapPredator) README);
  - the pair lists of a [GeoTransformer](https://github.com/qinzheng93/GeoTransformer) clone (commit `e7a135a`).
  ```bash
  python -I scripts/prepare_3dmatch.py <data.zip> <GeoTransformer clone> data/3DMatch   # needs torch
  python -I scripts/precompute_val_info.py val
  ```
- **KITTI odometry:**
  - Copy GeoTransformer's `data/Kitti/metadata/{train,val,test}.pkl` to `data/KITTI/metadata_raw/`.
  - The fetch script then downloads only the scans used by the benchmark pairs, via HTTP range requests on the official velodyne archive, and voxelises them at 0.3 m.
  ```bash
  python -I -u scripts/kitti_fetch.py --all-train --threads 8
  python -I -u scripts/kitti_features.py --workers 4
  ```
- **FCGF features:** use the test features released with [SC²-PCR](https://github.com/ZhiChen902/SC2-PCR) (Google Drive files `1kRwuTHlNPr9siENcEMddCO23Oaq0cz-X` for 3DMatch and `1mT4stteKF2IVjUe-YWht67WtgaB5lMTN` for KITTI).
  - `scripts/fetch_ranged.sh <id> <file> <bytes>` downloads them resumably.
  - Extract them so that the files are at `data/FCGF/3DMatch/<scene>/cloud_bin_<i>_fcgf.npz` and `data/FCGF/KITTI/pair_<i>.npz`.

**2. Logs and evaluation**
```bash
# re-implementations vs published recall
python -I -u scripts/validate_estimators.py 10 4000
# budget logs, FPFH, 3DMatch/3DLoMatch (ratio order and compatibility order)
python -I -u scripts/build_budget_logs.py --subset {val|3DMatch|3DLoMatch} --workers 6 [--order compat]
python -I -u scripts/build_budget_logs.py --subset train --sample 1000 --workers 6 [--order compat]
# ordering design studies (validation)
python -I -u scripts/ordering_study.py 3 6
python -I -u scripts/ordering_study_fast.py 3 6
python -I -u scripts/ordering_study_anchors.py 3 6
# KITTI: estimator thresholds on validation, then logs for every split
python -I -u scripts/build_budget_logs_kitti.py --select-thresholds --workers 6
python -I -u scripts/build_budget_logs_kitti.py --split {train|val|calib|test} --workers 6
# FCGF: test logs (even-indexed pairs), then the held-out pool and the three protocols
python -I -u scripts/build_budget_logs_fcgf.py --set {3DMatch|3DLoMatch|kitti_test} --workers 6 --every 2
bash scripts/run_fcgf_recal.sh
# equal-time comparison (fewer seeds/cliques, uniform and FastMAC-style sampling)
python -I -u scripts/build_equal_time_logs.py --subset {3DMatch|3DLoMatch} --workers 6 --every 2
# certified selection and test evaluation (as in the fast path), then live timing and the paper assets
bash scripts/run_budget_final.sh
bash scripts/run_paper_final.sh
```
`run_paper_final.sh` runs:
- the KITTI selection;
- the FCGF transfer evaluation;
- the live timing: `live_budget.py` for KITTI and FCGF, and `live_equal_time.py`;
- `paper_assets.py`.

Run the live timing on an otherwise idle machine.

**3. Supplementary: certified adaptive pose search (CAPS)**
```bash
python -I -u scripts/build_search_logs.py --subset {val|3DMatch|3DLoMatch} --workers 6 [--variant psh]
python -I -u scripts/build_search_logs.py --subset train --sample 2000 --workers 6 [--variant psh]
python -I scripts/analyze.py --prefix search --schedule jump1024 --tag search_jump1024
python -I scripts/analyze.py --prefix psh --baselines-from search --schedule jump1024 --reference-prefix search --tag psh_jump1024
python -I scripts/combined_figure.py results/search_jump1024 results/psh_jump1024 results/fig_tradeoff.png
python -I -u scripts/live_benchmark.py --summary results/psh_jump1024/summary.json --prefix psh --schedule jump1024 --per-set 200
```

## Protocol notes

- **Single test evaluation.** Controllers are fitted on training pairs and certified on held-out validation/calibration pairs; each test set is evaluated once.
  - KITTI certification uses the 180 validation pairs plus the 1,058 training pairs not used for fitting.
  - FCGF uses the even-indexed test pairs for testing and the odd-indexed ones as a held-out pool.
- **Statistics.** Speed-up intervals use a scene-stratified bootstrap; recall losses are tested for non-inferiority (1 pp margin, 2 pp on 3DLoMatch); paired comparisons use McNemar's exact test.
- **Cost accounting.** Every distinct computation is charged once, including the ordering and the FastMAC sampling signal.

## License

No license is granted. The code is published for transparency and reproducibility; all rights are reserved. The datasets keep their own terms of use.
