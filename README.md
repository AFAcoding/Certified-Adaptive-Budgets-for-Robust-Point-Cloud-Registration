# Certified Adaptive Budgets for Robust Point Cloud Registration

Code, results and paper of *Not All Pairs Need All Correspondences: Certified Adaptive Budgets for Robust Point Cloud Registration*.

**Certified adaptive budgets (CAB)** wrap an unchanged robust estimator (re-implemented SC²-PCR and TurboReg) in three steps:
- They run it on growing budgets of correspondences, ordered by mutual consistency.
- A learned controller stops as soon as it is confident.
- The stopping rule, chosen on the fitting pairs, is certified per difficulty group with Learn-then-Test on separate calibration pairs. With high probability, at most 1 % of the pairs the full estimator registers are lost.

The paper's claims rest on a **pre-registered protocol** ([PROTOCOL.md](PROTOCOL.md)) with blind test sets that were evaluated once:
- held-out 3DMatch training scenes (high and low overlap);
- KITTI raw drives outside the odometry benchmark.

The official 3DMatch, 3DLoMatch and KITTI odometry test sets are reported as development benchmarks. Correspondences come from FPFH and from FCGF, computed by a PyTorch re-implementation of the network that reproduces the released features.

## Results (live speed-up over the full budget; realized risk ≤ 1 % everywhere)

| Test set | SC²-PCR | TurboReg |
|---|---|---|
| Blind: held-out scenes, overlap > 30 % (2,092 pairs) | 1.56× | 1.49× |
| Blind: held-out scenes, overlap 10–30 % (908) | 0.94× | 0.95× |
| Blind: KITTI raw drives, FPFH (1,310) | 0.93× | 0.91× |
| Blind: KITTI raw drives, FCGF (203) | full budget | full budget |
| Development: 3DMatch / 3DLoMatch / KITTI odometry, FPFH | 1.58× / 0.96× / 1.08× | 1.42× / 0.97× / 1.07× |
| Development: 3DMatch / 3DLoMatch, FCGF | 1.04× / 1.08× | 1.01× / 1.03× |

All results are statistically non-inferior in recall. Where nearly every pair needs the full budget, CAB declines to cut instead of losing pairs. Details are in the paper (`paper/main.pdf`, `paper/supp.pdf`).

## Contents

| Path | What it is |
|---|---|
| `paper/` | paper and supplementary material: LaTeX sources, PDFs, and the generated `numbers.tex`, `tables/` and `figures/` |
| `PROTOCOL.md` | the pre-registered evaluation protocol v2 and its single deviation |
| `src/acpr/` | the library: data loading, FPFH correspondences, the FCGF re-implementation (`fcgf_net.py`, `safe_torch_load.py`), SC²-PCR and TurboReg re-implementations, compatibility ordering, FastMAC-style sampling, pose search, controllers and Learn-then-Test certification |
| `scripts/` | every experiment, analysis and figure script (see the pipeline below) |
| `results/` | the selection reports (`*.md`/`*.json`), live timings and summaries that the paper's numbers come from; `results/protocol_v2/` holds the splits, the KITTI raw pairs with their ICP ground truth, and the FCGF verification |
| `scripts/download_logs.py` | downloads the per-pair logs of all experiments (122 MB zip from the v2.0 release) into `logs/` |

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
python -I scripts/download_logs.py                                       # -> logs/*.jsonl (79 files)
# protocol v2: choice on the fitting pairs, certification on the calibration pairs, single test evaluation
python -I scripts/select_ladder.py --prefix {budget|budgetc} --ladders extended --dataset {v2_indoor_fpfh|v2_kitti_fpfh|v2_indoor_fcgf|v2_kitti_fcgf}
python -I scripts/select_ladder.py --prefix {budget|budgetc} --ladders extended --dataset ... --rho {0.10|0.25}   # worst-case variant
# further checks on the development benchmarks (all from the logs)
python -I scripts/calibration_size.py      # certification on random calibration subsets of growing size
python -I scripts/sensitivity.py           # risk level epsilon and number of difficulty groups
python -I scripts/evidence_extra.py        # group-wise and worst-case risk, per-scene results, re-fitted controllers
# every number, table and figure of the paper, then an independent re-computation of the headline numbers
python -I scripts/paper_assets.py          # -> paper/numbers.tex, paper/tables/, paper/figures/
python -I scripts/validate_numbers.py      # prints MISMATCH lines, or "no mismatches"
```

`{a|b}` means "run once with each value". The outputs should match the files in `results/`. `scripts/run_v2_analysis.sh` runs this whole stage, followed by the live timing.

Cost is reported in two ways:
- **Operation counts** are hardware-independent and come from the logs: the dominant arithmetic of every estimator stage (compatibility tests, graph products, consensus and hypothesis scoring) plus the ordering. The fast path reproduces them exactly (`ops_ratio` in the selection reports, column "Ops" of the paper's Tables 1 and 2).
- **Live speed-ups** are wall-clock measurements on our machine (AMD Ryzen 7 5700U, 8 cores; `results/budget/live_*_v2_*.json`, 300 random test pairs per set). On other hardware, re-measure them on an otherwise idle machine with the live steps of `scripts/run_v2_analysis.sh`. Its last step, `scripts/retime_stalls.py`, times again any pair interrupted by a system stall (a run longer than ten times the median full-budget time); no pair of the v2 runs needed it.

## Full rerun from the data

Expect several days on a laptop CPU. The log builders run 6 worker processes with single-threaded BLAS; run one builder at a time.

**1. Data**
- **3DMatch / 3DLoMatch:**
  - Predator's preprocessed archive (`data.zip`, linked in the [OverlapPredator](https://github.com/prs-eth/OverlapPredator) README);
  - the pair lists of a [GeoTransformer](https://github.com/qinzheng93/GeoTransformer) clone (commit `e7a135a`).
  ```bash
  python -I scripts/prepare_3dmatch.py <data.zip> <GeoTransformer clone> data/3DMatch   # needs torch
  python -I scripts/precompute_val_info.py val
  python -I scripts/make_splits_v2.py                                                    # protocol v2 indoor splits
  ```
- **KITTI odometry:**
  - Copy GeoTransformer's `data/Kitti/metadata/{train,val,test}.pkl` to `data/KITTI/metadata_raw/`.
  - The fetch script then downloads only the scans used by the benchmark pairs, via HTTP range requests on the official velodyne archive, and voxelises them at 0.3 m.
  ```bash
  python -I -u scripts/kitti_fetch.py --all-train --threads 8
  python -I -u scripts/kitti_features.py --workers 4
  ```
- **KITTI raw drives (protocol v2):** enumerate the raw drives outside odometry sequences 0–10, split them, fetch only the scans of the pairs (HTTP range requests on the official archives), then refine the GPS/IMU poses by ICP.
  ```bash
  python -I -u scripts/kitti_raw_v2.py enumerate
  python -I -u scripts/kitti_raw_v2.py split
  python -I -u scripts/kitti_raw_v2.py fetch --threads 8
  python -I -u scripts/kitti_raw_v2.py fetch-odometry --threads 8   # odometry scans for the FCGF features
  ```
- **FCGF weights:** the official checkpoints linked in the [FCGF](https://github.com/chrischoy/FCGF) README, placed in `third_party/fcgf_weights/`: `2019-08-16_19-21-47.pth` (3DMatch, 5 cm) and `KITTI-v0.3-ResUNetBN2C-conv1-5-nout32.pth`. They are loaded with a restricted unpickler (`acpr.safe_torch_load`), so no code inside a checkpoint is run.
- **FCGF verification (optional):** with the test features released with [SC²-PCR](https://github.com/ZhiChen902/SC2-PCR) (Google Drive files `1kRwuTHlNPr9siENcEMddCO23Oaq0cz-X` for 3DMatch and `1mT4stteKF2IVjUe-YWht67WtgaB5lMTN` for KITTI, extracted to `data/FCGF/3DMatch/<scene>/cloud_bin_<i>_fcgf.npz` and `data/FCGF/KITTI/pair_<i>.npz`), `scripts/verify_fcgf.py 8` and `scripts/verify_fcgf_kitti.py` check that the re-implementation reproduces them (`results/protocol_v2/fcgf_verification.txt`).

**2. Logs, selections and timing (protocol v2)**
```bash
python -I scripts/reuse_fit_logs_v2.py                        # fitting pairs already logged in the old training sample
bash scripts/run_v2_indoor_fpfh.sh > logs/v2_indoor_fpfh.log 2>&1   # FPFH logs: fitting top-up, calibration, blind test
bash scripts/run_v2_data.sh > logs/v2_data.log 2>&1           # ICP ground truth, FPFH raw-drive logs, FCGF logs, equal-time logs
bash scripts/run_v2_analysis.sh > logs/v2_analysis.log 2>&1   # selections, studies, live timing (idle machine), re-timing
python -I scripts/paper_assets.py && python -I scripts/validate_numbers.py
```
The development benchmarks also need the logs of the official test sets:
```bash
python -I -u scripts/validate_estimators.py 10 4000             # re-implementations vs published recall
python -I -u scripts/build_budget_logs.py --subset {3DMatch|3DLoMatch} --workers 6 [--order compat]
python -I -u scripts/build_budget_logs_kitti.py --select-thresholds --workers 6
python -I -u scripts/build_budget_logs_kitti.py --split {train|val|calib|test} --workers 6
python -I -u scripts/build_equal_time_logs.py --subset 3DLoMatch --workers 6 --every 2
```
The ordering design studies (`scripts/ordering_study*.py`) run on the 3DMatch validation scenes.

**3. Supplementary: certified adaptive pose search (CAPS)**
```bash
python -I -u scripts/build_search_logs.py --subset {val|3DMatch|3DLoMatch} --workers 6 [--variant psh]
python -I -u scripts/build_search_logs.py --subset train --sample 2000 --workers 6 [--variant psh]
python -I scripts/analyze.py --prefix search --schedule jump1024 --tag search_jump1024
python -I scripts/analyze.py --prefix psh --baselines-from search --schedule jump1024 --reference-prefix search --tag psh_jump1024
python -I scripts/combined_figure.py results/search_jump1024 results/psh_jump1024 results/fig_tradeoff.png
python -I -u scripts/live_benchmark.py --summary results/psh_jump1024/summary.json --prefix psh --schedule jump1024 --per-set 200
```

**4. Paper**
```bash
cd paper && latexmk -pdf supp.tex && latexmk -pdf main.tex
```

## Protocol notes

- **Pre-registration.** PROTOCOL.md was committed before any of the new data was downloaded; its one amendment (the outdoor split) was committed before any raw-drive scan was downloaded. Each blind test set was evaluated once, after every selection had been written to disk.
- **Choose, then certify.** The ladder, the policy family and the difficulty groups are chosen on the fitting pairs only (5-fold out-of-fold controller scores); only the chosen candidate is certified on the calibration pairs. Certifying several candidates on the same calibration pairs and keeping the cheapest would void the guarantee (an earlier version of this code did that; its results are kept in `results/budget/legacy_calibration_selection/`).
- **Development history.** The first protocol (selections without the `v2_` suffix in `results/budget/`) used the 3DMatch validation scenes for both design and certification, and fitted FCGF on held-out test pairs. Its results are kept for transparency; the paper reports protocol v2.
- **Statistics.** Speed-up intervals use a scene-stratified bootstrap; recall losses are tested for non-inferiority (1 pp margin, 2 pp at low overlap); paired comparisons use McNemar's exact test.
- **Cost accounting.** Every distinct computation is charged once, including the ordering and the FastMAC sampling signal.

## License

No license is granted. The code is published for transparency and reproducibility; all rights are reserved. The datasets keep their own terms of use.
