# Protocol v3: evaluation notes (written as results arrived)

## 2026-10-22 03:12, offline selections on the v3 blind test (2,623 never-processed pairs)
Main configuration (compatibility order, group-conditional). Offline speed-up over the full budget, method v2 -> v3:
- held-out high overlap (1,976): SC2 1.85 -> 1.90, TurboReg 1.61 -> 2.19; low overlap (647): 1.00 -> 1.04, 1.01 -> 1.08.
- every v3 configuration non-inferior, risk <= 0.15 % (v3 marginal <= 0.46 %); pre-registered rule for making v3 the
  main method (non-inferior and within the risk level on the v3 blind test) is met.
- ratio order, TurboReg: v3 slightly slower (1.69 -> 1.66); ratio order, SC2 marginal: v3 falls back to the full budget.

## 04:25, live timing on the v3 blind test (300 pairs per set, same pairs and clock for every configuration)
Live speed-up: SC2 high 1.78 (v2) vs 1.68 (v3); TurboReg high 1.64 vs 2.10; low: 0.98 vs 1.01 and 1.00 vs 1.05.
Paired bootstrap (scene-stratified) of the time ratio v2/v3 on the same pairs, compatibility order:
SC2 high 0.946 [0.921, 0.972] (v3 slower), SC2 low 1.024 [1.007, 1.040], TurboReg high 1.280 [1.185, 1.392],
TurboReg low 1.055 [1.032, 1.082]. Live and offline stopping decisions agree on 100 % of pairs.

**Finding:** on pairs the gate lets through, SC2 stops at the same stage under v2 and v3 (218 of 222 pairs) but v3 takes
~44 ms longer per pair: the gate's signals and its classifier prediction cost more live than the offline accounting
charged (it charged non-gated compatibility-order pairs only max(0, t_gate - t_order) and no prediction time).
The offline v3 speed-ups are therefore optimistic; live time remains the primary measure.

**Handling (decided before any further look at blind data):** the blind live numbers stand as measured (no
re-timing or re-implementation on blind pairs). The offline accounting is made consistent by charging every pair
the measured gate cost (signals + prediction, microbenchmarked on development pairs on an idle machine), and the
paper states the correction.

## Correction (2026-10-22 12:40)
The re-run accounting is *consistent*, not uniformly *conservative*: it adds the prediction cost but takes the
signals' cost from the microbenchmark (same conditions as the ordering), whereas the first run took it from the
feature runs, timed under parallel load (inflated). Printed offline speed-ups changed by at most ~0.02
(group-conditional) and ~0.11 (marginal), in either direction; every choice and per-pair outcome is identical.
The 04:25 hypothesis that the offline v3 speed-ups were optimistic *because of the accounting* is refuted: the
gate's computation costs ~3 ms per pair (signals replace the ordering; one prediction), so the offline numbers barely
move; the ~40-48 ms live overhead is a runtime effect (likely thread-pool contention), reported as measured.

## Overhead diagnosis on development pairs (2026-10-22, 13:10-13:40; blind pairs not re-timed)
Median extra time of the final method over CAB without the gate on pairs with identical decisions: 10-20 ms
(gate_overhead.py 19.9, live_breakdown.py 9.6, harness_check.py 15.7 interleaved / 16.4 deferred). Of it, ~4 ms is
the boosted-tree gate's prediction (sklearn per-call overhead) and ~6 ms the estimator stages running slower on
identical work. Limiting the classifier's OpenMP pool to one thread: -1 ms (thread-contention hypothesis refuted).
Moving the harness's untimed offline checks after all timed runs: no change (harness-artifact hypothesis refuted).
The 40-48 ms of the blind run is not reproduced on development pairs; its cause is not established. Paper corrected.

## Addendum A (MAC): engineering notes (2026-10-22, 19:00-21:30; no blind pair processed)
- Run 3 of the MAC logs stopped at 218 fitting pairs: igraph's `maximal_cliques(file=...)` leaves one C-runtime
  stream open per call (the 509th call of a process fails, "fdopen() failed unexpectedly"). Fix: `acpr.mac` raises
  the stream limit to 8,192 (`_setmaxstdio`) and the log builder replaces its workers every 100 pairs
  (`multiprocessing.Pool(maxtasksperchild=100)`; `ProcessPoolExecutor(max_tasks_per_child=...)` hangs on Python
  3.13.3). Re-running 4 logged pairs in recycled workers reproduced every logged field except the timings.
  The run resumed at 20:33 with the 218 logged pairs kept.
- Workers started after 21:00 (each is replaced after 100 pairs) use a lower-memory but bit-identical `acpr.mac` (edges streamed into igraph,
  clique file read in chunks of at most 2 million members): identical transform and info on 8 inputs of 4 fitting
  pairs (9k-239k cliques), also with a tiny chunk bound that forces many chunk boundaries; same run time; peak memory
  on a 5.6M-clique pair 971 MB (a worker of the old version reached 3.8 GB on such pairs, with 0.8 GB of RAM free).
- MAC's cost varies by orders of magnitude between pairs (a fitting pair with 16.5 million maximal cliques takes
  ~6 min per stage, single-threaded), so the stall rule of the live timing (a run longer than 10x the median
  full-budget time of its set) would flag legitimately heavy pairs. For MAC rows only, the reference is the pair's own
  logged full-budget time (`retime_stalls.PAIR_RELATIVE`); the rule and every result for SC2-PCR and TurboReg are
  unchanged (dry run: 0 stalled pairs in every existing live file, as before).
- `live_budget.py` lacked the estimator keyword entry for MAC indoors (`{"mac": {}}`); added before the live run.

## Addendum B (2026-10-22, 21:20-21:55; no MAC run on any test pair before it)
- The authors asked for MAC on every family (KITTI, FCGF). The inlier counts of those fitting sets (FCGF indoors:
  median 861, 44 % above 1,000; FCGF on KITTI: median ~3,700 of 4,000) made addendum A's MAC infeasible there.
- Reading the authors' C++ implementation (the one behind their published numbers; Linux/registration.cpp, PCR.cpp,
  funcs.cpp of zhangxy0517/3D-Registration-with-Maximal-Cliques, downloaded for reading only) showed two differences
  from their Python implementation: a graph reduction before the clique search (clustering coefficients, Otsu
  threshold; dense graphs are cut to their most clustered ~50+ nodes) and dataset-specific settings (KITTI: tau 0.6 m,
  cut-off 0.9 FPFH / 0.999 FCGF, cliques of at least 4; recommended build igraph 0.10.6, whose code path uses 4).
- Checks before pre-registering: the Python transcription of the reduction equals a literal transcription of the C++
  loops on 10 synthetic graphs (sparse and dense paths, reduction triggered and not); on indoor FPFH fitting pairs it
  leaves sparse graphs and their results unchanged (3 pairs identical to the earlier logs) and cuts the 3 heaviest
  pairs from 5.6-16.5 million cliques and 120-392 s to 1.6-2.8 thousand cliques and 1.5-2.3 s, all still registered;
  6 fitting pairs per family run in 1-35 s and agree with SC2-PCR's success on every pair.
- The running addendum-A log build (520 v3_fit pairs, no test pair) was stopped at 21:20 and archived
  (logs/mac_python_impl/, logs/mac_attempt4_python_impl_stopped.log). Addendum B was committed and pushed (139a861)
  before the new run started at 21:53 (scripts/run_mac_all.sh, logs/mac_all.log).

## Addendum B, amendment 1 (2026-10-23, 11:07-12:05)
- Indoor FPFH family complete at 11:07 (all 8 selections reproduced at evaluation; live/offline agreement 100 %).
  The remaining families were switched from 6 to 8 log workers (all physical cores) at that family boundary, before
  any KITTI record was written; each family is built with one setting.
- KITTI FPFH with the C++ cut-off 0.9: up to 25 million maximal cliques per full-budget run (1,310 s), mean 143 s;
  47 kitti_train pairs logged in ~1 h. Cut-off 0.99 on the same 47 pairs: identical success on every pair, 7.5 s per
  run. Amendment 1 (pushed, e318bff) before any KITTI calibration or test pair; the 0.9 logs are archived in
  logs/mac_kitti_cut09/; KITTI family restarted at 12:03 with 8 workers.

## Addendum C: GPU timing (2026-10-23)
- Bundles exported single-threaded (as the logs; with several BLAS threads the brute-force nearest neighbours of KITTI
  pairs change, verified: recomputed gate signals equal the logged ones exactly only single-threaded).
- Part 1 (fresh blind and held-out scenes; SC2-PCR and TurboReg, MAC on the fresh blind test) ran on a Tesla T4
  (Google Colab) 12:32-14:21 UTC and was published to results/gpu/ by the notebook. GPU stopping decisions equal the
  CPU's offline decisions on 98-100 % of the pairs per set.
- Part 2 (six further sets) was exported and uploaded as a private draft release, but not run before the paper was
  finalised (the notebook's 6-hour wait for it in Drive expired); it can be added later without changing anything else.

## Addendum B: the remaining families (2026-10-23 12:03 to 2026-10-24 03:11)
- KITTI FPFH (12:03-17:35), indoor FCGF (17:35-00:06) and KITTI FCGF (00:06-03:11), 8 log workers
  (`WORKERS=8 FROM=2 bash scripts/run_mac_families.sh`, logs/mac_rest.log). In every family the selections were
  written before its first test log, and the single evaluation reproduced every one of them
  (scripts/check_same_selection.py).
- Live, final method (300 pairs per set): KITTI raw drives 1.13x [1.08, 1.19], KITTI odometry 1.40x [1.31, 1.51],
  FCGF 3DMatch 1.07x [1.04, 1.12], FCGF 3DLoMatch 1.06x [1.03, 1.09]; live and offline decisions agree on 94-100 %
  of the pairs (on KITTI, multi-threaded arithmetic also changes a few brute-force nearest neighbours).
- KITTI FCGF: on FCGF's own training pairs the first stage already registers 295 (ratio order) and 299
  (compatibility order) of the 300 fitting pairs. As for SC2-PCR and TurboReg, every MAC configuration was certified
  as the full budget (both orderings, with and without the gate, marginal and group-conditional), so by the
  addendum's rule this family was not timed.
- scripts/retime_stalls.py at the end: no stalled pair in any live file.

## Addendum C: GPU timing, parts 2 and 3 (2026-10-25)
- Part 2 (SC2-PCR and TurboReg on KITTI raw drives, 3DMatch, 3DLoMatch, KITTI odometry, FCGF 3DMatch and FCGF
  3DLoMatch) ran on a Tesla T4 15:12-17:22 and was published by the notebook.
- Amendment 1 (pushed 8ac340b before any MAC GPU run beyond the fresh blind test): MAC on the eight further timed test
  sets. Its bundle reuses the exported correspondences (checked identical to a new single-threaded export of KITTI raw,
  FCGF 3DMatch and FCGF 3DLoMatch); part 3 ran on a Tesla T4 in four batches, published 19:21-21:24.
- All 30 conditions: GPU stopping decisions equal the CPU's offline decisions on at least
  98 % of the pairs; SC2-PCR and TurboReg speed-ups within 0.14 of the CPU's; largest
  realized risk on the 300-pair samples 1.00 % (3 of
  300, in 2 conditions); the final method faster than CAB without the gate in
  23 of 30 conditions, SC2-PCR above 30 % overlap included (unlike the CPU live run).

## Addendum D: MAC in the equal-time comparison (2026-10-26)
- Pre-registered and pushed (4acca12) before any MAC equal-time run on a test pair. Smoke tests on fitting pairs only
  (v2_fit; their outputs deleted). The smoke test showed that a fresh worker's first MAC call pays for importing igraph
  (about 0.8 s); every worker process of the offline logs now starts with an untimed run (in the addendum as pushed).
- Offline variant logs: held-out scenes above 30 % overlap 10:11-10:50 (1,046 pairs), 3DLoMatch 10:50-11:18
  (891 pairs), 6 worker processes.
- Live timing: a first start at 11:18 was stopped within its first 25 pairs, because a validation run
  (scripts/validate_numbers.py) was still using about five cores; it wrote nothing. Restarted from the first pair at
  11:19 with the machine otherwise idle.
- Live timing finished 12:54 (300 pairs; MAC full budget 4,195 ms, final method 1,645 ms per pair). Every variant that
  runs as fast as CAB registers fewer pairs at its time (MAC: FastMAC-style second order 0.7 pp, uniform 1.1 pp, fixed
  budgets 2.5-3.5 pp); Top-K cliques takes 1,695-1,773 ms and needs 1.1x CAB's time to match its recall. On 3DLoMatch
  FastMAC-style second-order sampling of 2,000 correspondences keeps MAC's net recall (+0.0 pp at 0.79x the offline
  time) but loses 1.79 % of the pairs the full budget registers; every cheaper variant saving at least 5 % of the time
  loses at least 1.35 % (MAC), 2.69 % (TurboReg), 4.04 % (SC2-PCR) of them. scripts/validate_numbers.py (now also
  recomputing the equal-time recalls, risks and live times from the raw logs): no mismatches.
