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
