# Improving CAB v3: registrability-aware and direct-budget policies — research memo

2026-10-22. Scope: the user's prompt (`registrability_aware_adaptive_registration_research_prompt.md`) and the idea of a
model that predicts the needed budget in {250, 500, 1000, 2000, 4000} directly. All numbers below come from fitting,
calibration and development data only (no blind set was loaded). Labels: **[fact]** source- or data-supported,
**[inference]** my reasoning, **[open]** needs an experiment.

## 1. Executive verdict

- **Direct budget prediction, as a stand-alone one-shot policy: abandon.** Without a correctness check it cannot be
  certified relative to the full estimator, and with a check it becomes "choose the first rung + CAB monitoring",
  i.e. a generalisation of the v3 gate. The data limit its value (section 4).
- **Pursue, narrowed:** (A) a *start-rung selector* {250, 500, full} trained on fitting pairs and **certified jointly**
  with the stopping thresholds by Learn-then-Test; (B) a **group-conditional give-up rule** for predicted-unsolvable
  pairs, reported as abstention, not as success; (C) the **engineering overhead** of the gate (~40 ms live,
  thread contention), which alone explains why v3 is 5 % slower than v2 for SC²-PCR at high overlap.
- Novelty: modest but real for (A)+(B) as a *certified* pre-estimation allocation policy for robust registration;
  closest work is risk-controlled early stopping for LLM reasoning (sequential, not pre-estimation) and overlap /
  pose-quality prediction in registration (no budgets, no guarantees). Not a standalone paper; a strong section of
  the CAB paper or a follow-up.

## 2. What CAB (v3) actually does [fact]

Ladder of nested budgets of compatibility-ordered correspondences; after each stage a controller (classifier chosen
on fitting pairs: logistic / quadratic logistic / boosted trees) gives p_now; per difficulty group (terciles of
first-stage explained correspondences) a threshold certified by Learn-then-Test (eps = 1 %, delta = 0.1, fixed
sequence, delta/G per group) bounds the share of full-budget successes lost. v3 adds a hardness gate: pre-estimation
signals; predicted-hard pairs run the full budget directly (can only remove losses). It controls **risk relative to
the full estimator**, not absolute accuracy, and only under within-group exchangeability; it does not rescue pairs the
full estimator fails.

## 3. Closest prior art

| Work | Predicts | Before estimation? | Budget / compute decision | Guarantee | Difference to (A)+(B) |
|---|---|---|---|---|---|
| Conformal Thinking (arXiv 2602.03814) | stop / give up during LLM reasoning | no (sequential) | yes, token budget | distribution-free risk control | domain; sequential only; no pre-estimation start choice |
| When does learning to stop help? (arXiv 2606.30852) | stop during reasoning | no | yes | risk-matched comparison | same; shows learned stopping helps only when evidence is spread over signals |
| Fast yet Safe (NeurIPS 2024), CALM | early exit in networks | no | exit layer | LTT / risk control | networks, not estimators |
| PREDATOR, UTOPIC, BEV overlap (2011.13005, 2208.02712, 2302.14511) | per-point overlap | yes | no | no | learned, GPU; no budget, no risk bound |
| Deep-PE (2405.16085) | pose quality after registration | no | hypothesis selection | no | post-hoc evaluator |
| Nobili et al. ICRA 2018 | alignment risk (localisation) | yes | no | no | ICP / geometry degeneracy |
| Context-based ICP selection (Souza Neto 2021) | which ICP variant | yes | algorithm choice | no | per context, not per pair |
| CAB v2/v3 (this work) | stop, gate | partly (gate) | yes | group-conditional LTT | baseline |

I found no work that certifies a pre-estimation budget or start-rung choice for robust registration [inference,
from the searches; not exhaustive].

## 4. Evidence from the logs (development data, compatibility order) [fact]

Target k* = smallest correct budget; class 5 = the full budget fails.

| Split | 250 | 500 | 1000 | 2000 | 4000 | full fails |
|---|---|---|---|---|---|---|
| 3DMatch (SC²-PCR) | 1,045 | 67 | 74 | 69 | 68 | 300 |
| 3DLoMatch (SC²-PCR) | 368 | 57 | 59 | 72 | 96 | 1,129 |

- The distribution is **bimodal**: easy-at-250 or unsolvable; each middle class holds ~4 % (3DMatch).
- **Perfect one-shot budget** (run only k*, unsolvable pairs run the full budget): 3.59x on 3DMatch, **1.33x on
  3DLoMatch**. Only *skipping* unsolvable pairs moves 3DLoMatch (10.8x) — i.e. the low-overlap lever is giving up,
  not budget choice.
- **Predictability from cheap pre-estimation signals** (boosted trees on fit+cal, 14 signals of `acpr.gate`):
  accuracy 0.71 / 0.62; one-vs-rest AUC: "solved at 250" 0.93 / 0.83, middle classes 0.73–0.82 / 0.45–0.67,
  "full fails" 0.84 / 0.64 (3DMatch / 3DLoMatch).
- **Predict-then-verify upper bound** (choose the first budget by expected cost, verify with *ground truth*, else full):
  2.70x / 1.14x (SC²-PCR) and 2.63x / 1.12x (TurboReg). v3 offline is ~1.7–1.9x on 3DMatch, so a realistic policy
  (verification by the controller, not ground truth) has perhaps +10–25 % to gain there, and little at low overlap.

## 5. Formal problem (for A and B)

Pair x with pre-estimation signals g(x); budgets b_1 < ... < b_K; full-budget success s_K. A policy pi = (start rung
r(g), stop thresholds lambda_{g,k}, give-up threshold gamma_g) returns a pose or *abstains*.
Risk R(pi) = P(s_K = 1 and pi does not return a correct pose) — abstention on a full-budget success counts as a loss.
Certify R <= eps per difficulty group with LTT over a **fixed sequence** of joint parameters (e.g. ordered by fitting
cost: one path through the (start, lambda, gamma) grid), calibrated on pairs **not** used to train r(.) or the
controllers. Unlike the v3 gate, a start rung below full and a give-up rule **can add losses**, so they must be inside
the certified family; the gate's "can only remove losses" argument does not apply.

## 6. Proposed policy

1. r(g) in {250, 500, full}: three classes are learnable (AUC 0.83–0.93 for the extremes); finer classes are not.
2. CAB monitoring from the start rung (same features; the pose-change feature is undefined at the first visited rung,
   as today).
3. Give-up (abstain) at the first rung when p_fin < gamma_g, certified with the stop thresholds; report abstention
   rate and returned-pose accuracy separately (never count abstentions as fast successes).
4. Fallback to the full budget when g(x) is out of distribution (e.g. Mahalanobis distance on fitting signals above
   its 99th percentile) — cheap and conservative.
5. Overhead: compile the gate tree ensemble to NumPy (or limit sklearn's OpenMP pool with threadpoolctl) so that the
   live gate costs its microbenchmarked ~3 ms instead of ~40 ms.

## 7. Minimum viable experiment (CPU, from existing logs; < 2 h)

- Data: v3_fit (train r, controllers), v2_cal (certify), development benchmarks 3DMatch / 3DLoMatch / KITTI for
  reporting. No blind set.
- Baselines: full budget; CAB v2; CAB v3 (gate); oracle bounds of section 4.
- Report: recall, loss with UB, risk (overall and per group), abstention rate, mean / median / p95 / p99 time,
  predictor and gate overhead (live, after the overhead fix), operation counts.
- Evaluate offline from logs, then live on 300 development pairs.

## 8. Ablations and failure analysis

Start rung alone / give-up alone / both; 2 vs 3 start classes; signal ablations (ratio only, anchor degrees only,
second-order support only); per-overlap and per-scene breakdown; pairs sent to 250 that needed full (cost of misses);
recoverable pairs abandoned (must stay within eps by construction — verify); calibration of p_fin; FCGF vs FPFH.

## 9. Go / no-go (decided before running)

- **Go** if, on development benchmarks, the combined policy is non-inferior with certified risk and improves CAB v3's
  live mean time by >= 10 % on 3DMatch *or* >= 5 % on 3DLoMatch / KITTI (the noise floor of the paired live
  bootstrap at 300 pairs is ~2–3 %), without raising p99 latency by more than 10 %.
- **No-go** if gains fall within the live bootstrap interval of zero, or if give-up is certified only at abstention
  rates below 5 % of unsolvable pairs (then it is not worth its complexity).
- A positive result needs a fresh pre-registered blind test (protocol v4), as v3 did.

## 10. Paper framing

Possible: "certified pre-estimation allocation: when to start small, when to start big, and when to abstain".
Claims to avoid: "predicts registrability" (it predicts success *of this estimator on these correspondences*);
"certified gate" for any component that can add losses unless it is inside the LTT family; speed-ups without the
predictor's live cost; gains measured on data used to design the policy.

## 11. Implementation plan

1. Overhead fix for the gate (threadpoolctl / NumPy trees); re-time on development pairs only.
2. Start-rung selector + give-up in `select_ladder.py` as a new family ("mondrian-start"), certified jointly.
3. Offline evaluation on development data; go/no-go.
4. If go: pre-register protocol v4 (fresh blind pairs: none remain in 3DMatch training scenes after v3 — would need a
   new dataset, e.g. ScanNet or ETH for indoor / outdoor generalisation, with their own calibration splits).
   Bottleneck: fresh blind data, not compute.

## 12. References

- Conformal Thinking: https://arxiv.org/abs/2602.03814
- When Does Learning to Stop Help?: https://arxiv.org/abs/2606.30852
- Fast yet Safe (NeurIPS 2024): https://proceedings.neurips.cc/paper_files/paper/2024/file/ea5a63f7ddb82e58623693fd1f4933f7-Paper-Conference.pdf
- PREDATOR: https://arxiv.org/abs/2011.13005 · UTOPIC: https://arxiv.org/abs/2208.02712 · BEV overlap: https://arxiv.org/abs/2302.14511
- Deep-PE: https://arxiv.org/abs/2405.16085
- Predicting Alignment Risk (Nobili et al., ICRA 2018): https://robots.ox.ac.uk/~mfallon/publications/2018ICRA_nobili.pdf
- Context-based registration algorithm selection: https://scitepress.org/PublishedPapers/2021/107124
- Data: `results/explore/budget_prediction.json` (script `scripts/explore/budget_prediction.py`)

## 13. Update 2026-10-22 (09:35): what is established, and the systematic v4 study

### Evidence ledger (development data unless stated)
| Component | Result | Status |
|---|---|---|
| Controller classifier chosen on fitting pairs | +22 % TurboReg on 3DMatch; live +28 % on the fresh v3 blind test | established (blind) |
| Hardness gate | offline +1–2 % (3DMatch), +3–4 % (3DLoMatch); live overhead ~40 ms/pair (SC²-PCR high overlap 5 % slower) | established, with an engineering defect |
| Ordering chosen on fitting pairs | KITTI +, FCGF TurboReg − | mixed |
| Certified give-up (E-B, union-bound split 0.5 % + 0.5 %) | gives up on 0–0.45 % of pairs, costs speed (1.71 → 1.44) | refuted |
| Certified start-rung routing (E-C) | 1.64/1.68 vs 1.71/1.77 | refuted |
| Direct budget prediction | bimodal targets; ceiling 2.7x on 3DMatch with ground-truth verification | bounded, subsumed by gate + monitoring |
| Cost anatomy (E-A) | ~26 % of v3's time on 3DMatch are **missed stops** (correct at 500, controller not confident), ~26 % gated pairs that were cheaply solvable, ~14 % unsolvable | the bottleneck is verification, not allocation |
| Geometric verification signals (fitness, residual) | features computed (cost ~5 ms tree + ~3 ms per stage) | in the factorial |
| Correspondence-geometry uncertainty (support covariance, Gauss-Newton Hessian) | features computed (< 1 ms per stage) | in the factorial |

### Factorial study (queued after the paper's timing runs: `scripts/explore/run_v4_factorial.sh`)
signals {base, verify, geom, both} x classifier {logit, poly2, hgb} x gate {off, on} x estimator {SC²-PCR, TurboReg}
= 48 configurations, each through the full choose-then-certify pipeline (fitting v2_fit, calibration v2_cal,
development 3DMatch / 3DLoMatch); the extra signals' measured cost is charged to every visited stage.

**Selection rule fixed before any result** (`scripts/explore/v4_select.py`): lowest out-of-fold cost on the fitting
pairs (gate-on: times one minus the gate's out-of-fold saving on fitting + calibration pairs); candidates within one
standard error are tied; among ties the simplest wins (fewest extra signals, then logit < poly2 < hgb, then no gate).
Development benchmarks only check non-inferiority, risk and overhead; they never choose. Every configuration is
reported. The winner is a v4 *candidate*: it needs the overhead fix (`scripts/explore/gate_overhead.py`, idle machine),
live timing on development pairs, and a fresh pre-registered blind test before any claim.

## 14. Result of the factorial study (2026-10-22, 12:28; `results/explore/v4_selection.md`)
The pre-specified rule (fitting-pair cost, 1-SE ties, simplest wins) selects signals that the development benchmarks
do not support: SC²-PCR winner verify / boosted trees / gate on: 3DMatch 1.68x, 3DLoMatch 0.98x, against 1.71x /
1.03x for the final method (base signals, chosen classifier, gate); TurboReg winner both / boosted trees / no gate:
1.69x / 0.87x against 1.77x / 1.04x. Fitting-cost gaps between the top configurations are about one standard error
(SE 51 and 80 ms), so 1,000 fitting pairs cannot rank them. **Conclusion: no evidence that geometric verification or
correspondence-geometry uncertainty improve the controller; no v4 candidate is named; the final method stays.**
Remaining levers, by evidence: the gate's live implementation overhead (engineering, `scripts/explore/gate_overhead.py`)
and larger fitting sets (the ranking noise is the binding constraint).
