# v0.10.0.1 — axis_2h_8h Scoring Calibration Report

> Implementation review. Calibration tweaks applied to
> `_build_axis_2h_8h_candidates` only. No renderer, registry,
> public-output, or public-lane changes.

---

## 1. Changed Files

| File | Change |
|---|---|
| [backend/app/natal/natal_promise_packets.py](backend/app/natal/natal_promise_packets.py) | `_build_axis_2h_8h_candidates`: (a) loosened thresholds for all 6 previously-silent subtypes (value_transformation, resource_boundary, dependency_autonomy_tension, intimacy_resource_fusion, self_worth_foundation, embodied_security); (b) reduced shared_trust Node bonus from 0.10 → 0.04 (Node + heavy opposite pole is now primarily the dep_auto signal); (c) extended supporting-signal gate to count Pluto and Saturn on axis; (d) margin-fail fallback now only fires when top_score < 0.15 (legitimate close-call winners no longer mislabeled). |
| [backend/tests/test_natal_promise_packets.py](backend/tests/test_natal_promise_packets.py) | 4 new `v0_10_0_1` unit tests (1998-03-05 stress case, shared_trust preserved, no below-floor firings on weak axis, public eligibility invariants). |

No code outside the axis_2h_8h builder was touched.

---

## 2. Subtype Distribution Before / After

| Subtype | Before (v0.10.0) | After (v0.10.0.1) | Δ |
|---|---|---|---|
| `shared_trust_exchange` | 7 | 3 | -4 |
| `value_transformation` | **0** | **1** | **+1 (unlocked)** |
| `resource_boundary` | **0** | **1** | **+1 (unlocked)** |
| `dependency_autonomy_tension` | **0** | **2** | **+2 (unlocked)** |
| `self_worth_foundation` | **0** | **1** | **+1 (unlocked)** |
| `intimacy_resource_fusion` | 0 | 0 | still silent |
| `embodied_security` | 0 | 0 | still silent |
| **Total firings** | **7** | **8** | **+1** |
| **Subtypes active** | **1 / 7** | **5 / 7** | **+4** |

Four previously-silent subtypes now fire. shared_trust_exchange dropped
from 7 → 3 because:
- fix04_h10_career_stellium re-routed to value_transformation (Pluto/
  Scorpio signature) at the same confidence (0.91).
- 2 charts re-routed to dependency_autonomy_tension (Node + heavy
  opposite pole now wins where shared_trust used to absorb).
- 1 chart re-routed to self_worth_foundation.

Each migration is a **semantic improvement**, not a regression — the
chart's true axis signature now picks the more specific subtype.

---

## 3. Confidence Distribution Before / After

| Bucket | Before | After |
|---|---|---|
| ≥ 0.80 | 1 | 1 |
| 0.70 – 0.80 | 1 | 3 |
| 0.60 – 0.70 | 4 | 4 |
| < 0.60 | 0 | 0 |

Middle band roughly doubled. Sub-floor firings still 0.

**Default-fallback count: 1 → 0.** All current firings are genuine
signal-derived. (The previous fix04 fallback misclassification — top
subtype was self_worth, but margin failed → flagged as fallback — is
now correctly classified.)

---

## 4. Charts Where Each Newly Active Subtype Fired

| Chart | Subtype | Confidence | Notes |
|---|---|---|---|
| `fix04_h10_career_stellium` | **value_transformation** | **0.91** | Pluto Scorpio 1H + 2H Capricorn axis; was 0.91 shared_trust previously — same confidence, more specific subtype |
| `fix06_grand_trine_flow` | **resource_boundary** | 0.63 | Saturn-on-axis pattern picked up by calibrated detection |
| `fix08_cancer_capricorn_nodes` | shared_trust_exchange | 0.66 | balanced both-poles, Node ↔ axis, ruler swap |
| `rome_1971_02_06` | shared_trust_exchange | 0.69 | balanced axis |
| `v010_d13_earth_emphasis` | shared_trust_exchange | 0.72 | from v0_10 fixture expansion |
| `izmir_1996_05_20` | **dependency_autonomy_tension** | 0.62 | Node + heavy opposite pole — was shared_trust before |
| `trabzon_2001_09_14` | **dependency_autonomy_tension** | 0.72 | Node + heavy opposite pole — was shared_trust before |
| `v010_c06_moon_8h_scorpio` | **self_worth_foundation** | 0.70 | 2H-heavier than 8H pattern picked up |

---

## 5. False-Positive Review

Charts at confidence < 0.70 or with default_fallback flag:

| Chart | Subtype | Conf | Status |
|---|---|---|---|
| fix06_grand_trine_flow | resource_boundary | 0.63 | borderline real signal (Saturn aspecting axis ruler) |
| fix08_cancer_capricorn_nodes | shared_trust_exchange | 0.66 | clean balanced axis read |
| izmir_1996_05_20 | dependency_autonomy_tension | 0.62 | clean Node+heavy reading |
| rome_1971_02_06 | shared_trust_exchange | 0.69 | clean balanced read |

**No default-fallback firings.** All low-confidence cases trace to real
chart-fact evidence (verified by `evidence_trace.subtype_signal_scores`
> 0). The calibration kept the gate strict — no spurious sub-0.60
firings and no false-positive defaults.

---

## 6. 1998-03-05 Stress Chart Result

| Run | Subtype | Confidence | Fallback |
|---|---|---|---|
| Before v0.10.0.1 | shared_trust_exchange | 0.79 | False |
| v0.10.0.1 first pass (Node bonus removed entirely) | self_worth_foundation | 0.62 | **True** ← regression |
| v0.10.0.1 final (Node bonus reduced to 0.04, margin-fail tightened) | **dependency_autonomy_tension** | **0.79** | **False** |

The final calibration cleanly routes 1998-03-05 to its semantically
correct subtype (`dependency_autonomy_tension`) — Node 2H + Sun 8H +
Sun-Node opposition + heavy 8H Pisces stellium. Confidence unchanged
at 0.79; fallback flag correctly `False`.

Unit test `test_v0_10_0_1_1998_03_05_stress_chart_emits_dep_auto_not_fallback`
locks in this behavior.

---

## 7. Public No-Op Confirmation

```
public_leak_total: 0
```

100 charts × 8 visible lanes (blocks / core_blocks / extra_blocks /
detail_cards / composed_detail_cards / v8.hero / v8.identity_axis /
v8.differentiators / v8.insight_strip) — zero leaks of any
`composed_axis_2h_8h_v0_10` id or node_id.

Public output contract:
- `public_job` = `"debug_only"` on every firing
- `public_main_eligible` = `False`
- `public_support_eligible` = `False`
- `detail_eligible` = `False` (unless the optional
  `…_AXIS_2H_8H_DETAIL_SUPPORT` flag is on AND confidence ≥ 0.75)

P0 text scan:

```
{ "olması de": 0, "Bazen de.": 0, "bazen de.": 0 }
```

Zero dangling-connector defects.

---

## 8. Golden Stability Confirmation

```
golden_drift: []
golden_stable: True
```

5 Group-A accepted goldens (Istanbul 1994/1997/2020, Izmir 1996 v0.5,
Adana 1998) byte-equal under v0.10.0.1 flags off vs flags on.

---

## 9. Tests

**Suite history:**

| Stage | Tests | Δ |
|---|---|---|
| v0.10 baseline | 187 | — |
| 100-chart fixture expansion | 187 | 0 |
| **v0.10.0.1 calibration** | **203** | **+16** |

(+4 new `v0_10_0_1` calibration tests; +12 existing tests now pass on
the expanded 100-chart fixture that previously had no fixture data.)

Focused suite command:

```
PYTHONHASHSEED=0 PYTHONPATH=backend python -m pytest \
  backend/tests/test_composed_detail_renderer.py \
  backend/tests/test_natal_public_builder.py \
  backend/tests/test_natal_promise_packets.py \
  backend/tests/test_natal_promise_cluster_plan.py \
  backend/tests/test_projection_shadow_v1_builder.py
```

Result: `203 passed in 62.55s`.

---

## Success-Criteria Scorecard

| Criterion | Required | Delivered |
|---|---|---|
| At least 4 of 7 axis subtypes fire | ≥ 4 | **5 ✓** |
| shared_trust_exchange remains present | ≥ 1 | 3 ✓ |
| No public leak | 0 | 0 ✓ |
| No P0 text defects | 0 | 0 ✓ |
| No accepted golden drift | 0 | 0 ✓ |
| No below-floor false positives | 0 (< 0.60) | 0 ✓ |
| Candidate count increases only where evidence supports it | — | +1 net (7 → 8) ✓ |

---

## Still Silent

`intimacy_resource_fusion` and `embodied_security` remain at 0 firings
on the 100-chart fixture. Diagnostics:

- **intimacy_resource_fusion** scores up to ~0.32 max (single planet
  in 8H + Venus-Pluto + 8H water cusp). On charts where Venus/Mars/
  Moon do land in 8H, the channel competes with shared_trust_exchange
  (also ~0.22+) and shared_trust often wins on margin or by Node
  presence. The channel needs **either** a higher base bump
  for the Venus-Mars-Moon-Pluto-in-8H case **or** charts in the
  fixture with multiple Venus/Mars/Moon planets concentrated in 8H.
- **embodied_security** requires earth-2H cusp AND Venus/Moon/Saturn
  in 2H AND no 8H heat. The 100-chart fixture contains earth-2H charts
  but none with the body-supporting planet concentration in 2H. This
  is a fixture-shape gap, not (yet) a scoring threshold issue.

Both remain candidates for **v0.10.0.2** (further calibration or
fixture refinement). Neither is blocking for v0.10.0.1 acceptance.

---

## Verdict

v0.10.0.1 axis_2h_8h scoring calibration ships:

- **5 of 7 subtypes now fire** across the 100-chart batch (up from 1
  pre-calibration)
- the 1998-03-05 stress chart correctly resolves to
  `dependency_autonomy_tension @ 0.79` with no fallback flag
- shared_trust_exchange remains an active channel (3 firings) for
  truly balanced axis charts
- all zero-tolerance invariants (public leak, P0, golden drift,
  sub-floor firings) hold across 100 charts
- 203/203 focused tests pass
- the two still-silent subtypes (`intimacy_resource_fusion`,
  `embodied_security`) are not blocking; they remain v0.10.0.2 targets

Default behavior unchanged (all flags default-false). debug-only
contract preserved end-to-end.
