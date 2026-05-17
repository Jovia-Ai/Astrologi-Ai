# SHOU ARC v0.1 Batch-1 Score-Once Reveal

Sources:
- Scorer contract: [scripts/arc_corpus.py](/Users/sahradenizozdogan/Astrologi-Ai/scripts/arc_corpus.py#L430)
- Canonical reference set: [arc_v0_1_gold_authoring_guide.md](/Users/sahradenizozdogan/Astrologi-Ai/docs/system/arc_v0_1_gold_authoring_guide.md#L8)
- Reveal output: [score_report.json](/Users/sahradenizozdogan/Astrologi-Ai/docs/system/_corpus/score_report.json#L1)

## 1. Overall Metrics

Score run: `PYTHONPATH=backend backend/venv/bin/python scripts/arc_corpus.py score`

- `n_scored`: `8`
- Extraction coverage mean: `1.000`
- Extraction coverage worst: `1.000`
- Extraction provisional pass: `true`
- Salience alignment mean: `0.949`
- Salience alignment worst: `0.592`
- False emphasis total (`salience`-kind only): `3`
- Framing deferred count: `23`
- Unsupported anchor types seen: `["final_dispositor"]`

Interpretation of these metrics must follow the scorer invariant:
- extraction coverage is the stable gating metric
- salience alignment is separate, provisional, uncalibrated, and non-gating
- unsupported anchors are reported and never counted as engine failure

## 2. Chart-by-Chart Reveal

### 1985-06-20_15-50_istanbul
Pre-registered note: [1985 gold](/Users/sahradenizozdogan/Astrologi-Ai/docs/system/_corpus/gold/1985-06-20_15-50_istanbul.json#L1)

- Extraction coverage: `1.000`
- Salience alignment: `1.000`
- False emphasis: `1`
- Framing deferred: `3`
- Unsupported anchors: `0`
- Expected failure if bad occurred: `partially`

What the reveal says:
- The monopolization failure did not occur in measurable salience terms. Moon/Pluto/Venus ranks all aligned.
- The secondary probe did fire: `Neptune Capricorn 2 as a personal headline` was elevated through the `tight_aspect` anchor on `Neptune`.

Salience misses:
- none

False emphasis:
- `Neptune Capricorn 2 as a personal headline`
  - classification: `expected_uncalibrated_behavior`
  - reason: this is exactly the pre-registered generational-tightness probe, and the current scorer uses member-max behavior for tight aspects, which can promote an endpoint to `defining` in provisional salience.

Unsupported anchors:
- none

New calibration question:
- Does the current `tight_aspect` member-max rule over-promote a generational endpoint when the aspect is exact but the chart's actual defining structure is elsewhere?

### 2007-01-17_10-20_helsinki
Pre-registered note: [2007 gold](/Users/sahradenizozdogan/Astrologi-Ai/docs/system/_corpus/gold/2007-01-17_10-20_helsinki.json#L1)

- Extraction coverage: `1.000`
- Salience alignment: `1.000`
- False emphasis: `1`
- Framing deferred: `3`
- Unsupported anchors: `0`
- Expected failure if bad occurred: `partially`

What the reveal says:
- The main monopolization failure did not occur in measurable salience terms. Jupiter rank-1 and Mars rank-2 held.
- The secondary probe did fire: `Uranus Pisces 12 + Neptune Aquarius 12 as personal headlines` was hit via `Uranus`.

Salience misses:
- none

False emphasis:
- `Uranus Pisces 12 + Neptune Aquarius 12 as personal headlines`
  - classification: `expected_uncalibrated_behavior`
  - reason: the pre-registered risk was stellium membership inflating generational outers. The scorer's `house_concentration` salience uses member-max across stellium members, so this is a direct reveal of that pressure point rather than a regression.

Unsupported anchors:
- none

New calibration question:
- When a 12H concentration is real but not the spine, should generational members inside the stellium be prevented from inheriting `defining` unless they also carry an independent personal-planet or ruler route?

### 2009-06-15_11-40_nairobi
Pre-registered note: [2009 gold](/Users/sahradenizozdogan/Astrologi-Ai/docs/system/_corpus/gold/2009-06-15_11-40_nairobi.json#L1)

- Extraction coverage: `1.000`
- Salience alignment: `0.592`
- False emphasis: `0`
- Framing deferred: `3`
- Unsupported anchors: `0`
- Expected failure if bad occurred: `no`

What the reveal says:
- The feared failures did not occur. There is no false emphasis on Jupiter-Neptune, no false Mercury monopolization hit, and no dreamy-helper collapse.
- The only measurable issue is a rank-1 salience miss: `chart_ruler Mercury` resolved to `strong`, not `defining`.

Salience misses:
- `chart_ruler Mercury` at rank `1`, engine tier `strong`
  - classification: `calibration_candidate`
  - reason: extraction is perfect, supporting routes also resolve, and this is a dual-gift multi-centred chart. The miss is about whether a double-ruler domicile in this structure should be forced into `defining`, not about anchor failure.

False emphasis:
- none

Unsupported anchors:
- none

New calibration question:
- In a dual-gift chart, should a rank-1 double-ruler domicile be required to score `defining`, or is `strong` acceptable when another authentic defining centre remains close behind?

### 1982-07-07_21-30_nairobi
Pre-registered note: [1982 gold](/Users/sahradenizozdogan/Astrologi-Ai/docs/system/_corpus/gold/1982-07-07_21-30_nairobi.json#L1)

- Extraction coverage: `1.000`
- Salience alignment: `1.000`
- False emphasis: `1`
- Framing deferred: `3`
- Unsupported anchors: `0`
- Expected failure if bad occurred: `partially`

What the reveal says:
- The pressure spine itself held: Saturn-8 / Mars-Saturn / Sun-square structure stayed aligned.
- The secondary probe did fire: `Moon sextile Uranus as the chart's main headline` was elevated through the `tight_aspect` anchor on `Moon`.

Salience misses:
- none

False emphasis:
- `Moon sextile Uranus as the chart's main headline`
  - classification: `expected_uncalibrated_behavior`
  - reason: this is the exact Q2-style probe for tightness outrunning structural centrality. The scorer elevated the soft exact aspect without losing extraction coverage of the real pressure spine.

Unsupported anchors:
- none

New calibration question:
- Should exact soft aspects be prevented from becoming `defining` when a harder, denser chart-ruler pressure structure is already present and anchored at rank 1?

## 3. Regression Check

Canonical references are defined in the guide as:
- [1962-01-07_10-30_nairobi.json](/Users/sahradenizozdogan/Astrologi-Ai/docs/system/arc_v0_1_gold_authoring_guide.md#L12)
- [1993-03-09_08-50_helsinki.json](/Users/sahradenizozdogan/Astrologi-Ai/docs/system/arc_v0_1_gold_authoring_guide.md#L13)
- [1973-08-05_01-20_istanbul.json](/Users/sahradenizozdogan/Astrologi-Ai/docs/system/arc_v0_1_gold_authoring_guide.md#L14)
- [1972-10-12_15-20_istanbul.json](/Users/sahradenizozdogan/Astrologi-Ai/docs/system/arc_v0_1_gold_authoring_guide.md#L15)

Regression result:
- All 4 canonical references still pass with `rank_weighted_coverage = 1.000`.
- All 4 canonical references still have `salience_alignment_provisional = 1.000`.
- None of the 4 canonical references introduced new `false_emphasis` hits.
- Extraction coverage did not regress anywhere in the full scored set: mean `1.000`, worst `1.000`.

Notes:
- One unsupported anchor type remains visible in the full corpus: `final_dispositor`. This is reported-only and not a failure under the scorer invariant.
- The no-dominant canonical reference still behaves correctly: it preserves a supporting-route note without turning it into a hard salience miss.

## 4. Interpretation

Batch-1 does not challenge extraction. Extraction is fully stable across all eight scored charts.

Batch-1 does refine the salience hypotheses:
- It supports the current separation between extraction and salience. The corpus is now surfacing salience questions without confusing them for anchor failures.
- It supports the usefulness of the pre-registered probes. Three of the four new charts triggered exactly the kind of provisional false-emphasis pressure they were designed to test.
- It challenges any premature confidence in the current salience policy around exact aspects and member-max inheritance. The repeated false-emphasis hits are concentrated in the intended Q2/Q1-adjacent stress zones, not spread randomly.
- It surfaces one non-failure calibration candidate in the gift-heavy chart: whether a multi-centred double-ruler domicile should be allowed to remain `strong` at rank 1 without counting as a provisional miss.

Batch-1 verdict:
- `supports` the current extraction architecture
- `supports` the need for further salience calibration volume
- `refines` the live questions around generational tightness, stellium-member inheritance, and dual-gift rank-1 expectations
- does `not` justify coefficient changes yet

Future joint-calibration candidates surfaced by this reveal:
- exact generational aspect inflation
- stellium member-max inflation for generational outers
- rank-1 expectation for double-ruler dignified charts that are genuinely multi-centred
