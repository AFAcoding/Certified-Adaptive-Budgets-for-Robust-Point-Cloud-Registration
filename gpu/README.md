# GPU timing of CAB (protocol v3, addendum C)

Live timing of the standard estimators and of the certified CAB configurations on a GPU, on the same 300 test pairs
per set as the CPU live timing. Nothing is trained or chosen here: the controllers, gates and certified thresholds come
from the CPU evaluation and are exported as plain arrays.

| File | Role |
|---|---|
| `cab_gpu.py` | PyTorch ports of SC2-PCR, TurboReg and MAC's graph stages (its clique search runs on the CPU, as in the authors' code), the compatibility ordering, the gate's signals and the CAB controller |
| `export_bundle.py` | writes `gpu_bundle/`: correspondences, ground truth and the certified controllers and gates, and checks that the exported arrays reproduce the fitted classifiers and the logged stopping decisions; run it locally after the CPU evaluation with single-threaded BLAS, since the brute-force nearest neighbours of KITTI and FCGF pairs depend on the thread count |
| `run_gpu_timing.py` | the timing itself; prints speed-ups and the agreement with the CPU decisions, writes one JSON |
| `CAB_GPU_timing_part1.ipynb` | the Colab notebook that was run: unpacks the bundle from Google Drive, times the fresh blind test (all three estimators) and the held-out scenes (SC2-PCR and TurboReg), and publishes the results to `results/gpu/` |
| `CAB_GPU_timing_part2.ipynb` | SC2-PCR and TurboReg on the six further test sets (`gpu_bundle_part2.zip`; written by `make_part2_notebook.py`) |
| `CAB_GPU_timing_part3.ipynb` | MAC on the eight further test sets (addendum C, amendment 1; `gpu_bundle_part3.zip`, assembled by `make_part3.py`) |
| `CAB_GPU_timing.ipynb` | the same for all ten test sets in one run |
| `make_part2.py` | helper used on our machine to assemble the bundle of the six further sets from parallel exports |

Steps:
1. `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -I gpu/export_bundle.py --sets th,tl,bh,bl` (needs the data and the logs), then zip `gpu_bundle/` and upload it to Google Drive.
2. Open the notebook with a GPU runtime (Colab, or VS Code with the Colab extension) and *Run all*. Give a fine-grained GitHub token (this repository, *Contents: read and write*) when asked, or store it as the Colab secret `GITHUB_TOKEN`. Never write the token into the notebook.
3. `python -I scripts/paper_assets.py` turns the published JSON into the paper's numbers (`gpu_results`, supplementary Sec. E).

The bundles are not published, since they hold correspondences and ground truth derived from the datasets. The published run (Tesla T4) covers the fresh blind test for all three estimators and the held-out scenes of protocol v2 for SC2-PCR and TurboReg. The six further sets of addendum C are exported; `CAB_GPU_timing_part2.ipynb` times them, and `scripts/paper_assets.py` adds every published result file to the paper's GPU table.
