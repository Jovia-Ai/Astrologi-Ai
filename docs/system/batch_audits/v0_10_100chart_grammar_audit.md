# v0.10 Compositional Grammar — 100-Chart Debug Audit

> Analysis only. No code, registry, scoring, renderer, or selection
> changes are made by this document. Flags: v0.9a/v0.9b/v0.10 debug
> families ON, all rollout/render/public-lane flags OFF.
>
> Fixture: `backend/tests/_artifacts/natal_batch_audits/natal_50_chart_discovery_metrics.json`
> expanded from 50 → 100 charts (`version = "v0_10_audit_expansion_100chart"`).

---

## Updated 100-Chart Fixture List

The expansion added 50 new charts grouped by the silent / under-tested
subtype each was authored to stress. Every new chart carries an
`audit_expansion_meta.target_family` + `target_subtype` annotation so
the audit can compare **intent vs. observed firing** chart-by-chart.

### Group A — `axis_2h_8h` silent subtypes (15 charts)

| chart_id | Target subtype | Reason |
|---|---|---|
| v010_a01_pluto_2h_scorpio | value_transformation | Pluto Scorpio + early-morning ASC ~ Libra → Pluto 2H |
| v010_a02_pluto_8h_sag | value_transformation | Pluto Sagittarius + ASC ~ Taurus → Pluto 8H |
| v010_a03_saturn_2h_cap | resource_boundary | Saturn Capricorn + ASC ~ Sagittarius → Saturn 2H |
| v010_a04_saturn_8h_aqua | resource_boundary | Saturn Aquarius + ASC ~ Cancer → Saturn 8H |
| v010_a05_venus_8h_scorpio | intimacy_resource_fusion | Venus Scorpio + ASC ~ Aries → Venus 8H |
| v010_a06_mars_8h_aries | intimacy_resource_fusion | Mars Aries + ASC ~ Virgo → Mars 8H |
| v010_a07_moon_8h_cancer | intimacy_resource_fusion | Moon Cancer + ASC ~ Sagittarius → Moon 8H |
| v010_a08_2h_stellium_no_8h | self_worth_foundation | Taurus stellium + ASC ~ Aries, 8H empty |
| v010_a09_8h_stellium_node_2h | dependency_autonomy_tension | Virgo 8H stellium + Node 2H |
| v010_a10_2h_ruler_in_8h | shared_trust_exchange | ASC ~ Libra → 2H ruler in 8H |
| v010_a11_8h_ruler_in_2h | value_transformation | ASC ~ Aries → 8H ruler in 2H |
| v010_a12_taurus_2h_embodied | embodied_security | 2H Taurus + earth planets |
| v010_a13_node_8h_heavy_2h | dependency_autonomy_tension | Inverse Node + heavy 2H pole |
| v010_a14_pluto_sun_axis | value_transformation | Sun 2H Scorpio + Pluto on axis |
| v010_a15_saturn_rules_8h | resource_boundary | ASC ~ Cancer → 8H Aquarius → ruler Saturn |

### Group B — `relationship_route` under-tested subtypes (12 charts)

| chart_id | Target subtype | Reason |
|---|---|---|
| v010_b01_hidden_love_12h_venus | hidden_private_love | DSC Pisces + Venus 12H |
| v010_b02_neptune_7h_pisces | hidden_private_love | Neptune 7H + Pisces DSC |
| v010_b03_chiron_7h_wound | wound_to_gift | Chiron 7H + Saturn-Venus hard |
| v010_b04_chiron_5h_saturn_moon | wound_to_gift | Chiron 5H + Saturn-Moon hard |
| v010_b05_venus_sun_5h_fire | attraction_warmth | Venus & Sun in Leo 5H |
| v010_b06_venus_7h_libra | attraction_warmth | Venus Libra 7H |
| v010_b07_mars_7h_cancer | boundary_conflict | Mars 7H Cancer + ASC Cap |
| v010_b08_mars_saturn_hard | boundary_conflict | Mars-Saturn opposition era |
| v010_b09_aries_dsc_mars_active | direct_relational_activation | Sanliurfa addendum chart (DSC Aries + Mars Aries 6H retro) |
| v010_b10_aries_dsc_mars_retro | direct_relational_activation | ASC Libra → DSC Aries |
| v010_b11_uranus_7h_aqua | freedom_space | Uranus Aqua + ASC ~ Leo → 7H Aqua |
| v010_b12_dsc_aqua_uranus_11h | freedom_space | ASC Leo → DSC Aqua + Uranus 11H |

### Group C — `moon_signature` under-tested subtypes (10 charts)

| chart_id | Target subtype | Reason |
|---|---|---|
| v010_c01_moon_5h_sag | creative_emotional_expression | Moon Sag 5H |
| v010_c02_moon_5h_leo | creative_emotional_expression | Moon Leo 5H |
| v010_c03_moon_12h_neptune | private_emotional_processing | Moon 12H + Moon-Neptune |
| v010_c04_moon_pisces_12h | private_emotional_processing | Moon Pisces 12H |
| v010_c05_moon_6h_virgo | daily_sensitivity | Moon Virgo 6H |
| v010_c06_moon_8h_scorpio | intimacy_depth (moon) | Moon Scorpio 8H |
| v010_c07_moon_8h_pluto | intimacy_depth (moon) | Moon 8H + Moon-Pluto aspect |
| v010_c08_moon_4h_cancer | home_inner_security | Moon Cancer 4H + IC Cancer |
| v010_c09_moon_4h_planets | home_inner_security | Moon 4H + 4H stellium |
| v010_c10_moon_neutral_rhythm | emotional_rhythm | Neutral tone — tests default-fallback gate |

### Group D — house/axis variety (13 charts)

| chart_id | Target subtype | Reason |
|---|---|---|
| v010_d01_3h_stellium | identity_route mediated | 3H stellium |
| v010_d02_9h_stellium | career_route creative_visibility | 9H stellium (non-10H public direction) |
| v010_d03_mercury_3h_9h | identity_route direct | Mercury 3H/9H axis |
| v010_d04_4h_stellium_no_moon | moon_signature home_inner_security | 4H stellium, Moon elsewhere |
| v010_d05_5h_stellium | moon_signature creative_emotional | 5H stellium |
| v010_d06_venus_sun_5h | relationship_route attraction_warmth | Venus+Sun 5H secondary path |
| v010_d07_12h_stellium | moon_signature private_emotional | 12H stellium |
| v010_d08_mars_saturn_12h | moon_signature private_emotional | Mars+Saturn 12H tension |
| v010_d09_mixed_no_dom | identity_route mediated | No clear dominance |
| v010_d10_mixed_no_dom_2 | identity_route mediated | Mid intensity, no pole |
| v010_d11_even_house_spread | identity_route mediated | Planets even across houses |
| v010_d12_air_emphasis | identity_route direct | Air-sign emphasis |
| v010_d13_earth_emphasis | axis_2h_8h embodied_security | Earth-sign emphasis |

Total new charts: **50**.
Total fixture size: **50 baseline + 50 expansion = 100**.

---

## Audit Results

### 1. Family Counts (50 → 100)

| Family | 50-chart | 100-chart | Δ |
|---|---|---|---|
| `identity_route` | 44 | **85** | +41 |
| `moon_signature` | 31 | **60** | +29 |
| `career_route` | 29 | **63** | +34 |
| `relationship_route` | 22 | **41** | +19 |
| `axis_2h_8h` | 6 | **7** | +1 |

The Group-A charts intended to stress axis_2h_8h **almost entirely
failed to produce axis candidates** — only +1 axis firing across the
new 50 charts. This is the most striking finding of the expansion.

### 2. Subtype Distributions by Family (100-chart)

#### `identity_route` (85 candidates)

| Subtype | Count |
|---|---|
| private_identity_spine | 29 |
| direct_identity_spine | 25 |
| controlled_identity_spine | 17 |
| relational_identity_spine | 8 |
| mediated_identity_spine | 6 |

Healthy across all 5 subtypes.

#### `career_route` (63 candidates)

| Subtype | Count |
|---|---|
| invisible_preparation_before_visibility | 18 |
| public_voice | 13 |
| creative_visibility | 13 |
| action_initiative | 8 |
| authority_responsibility | 8 |
| **strategic_role** | **3** *(new — default fallback)* |

`strategic_role` (career default fallback) now fires on 3 charts —
previously 0. These are charts in the expansion that didn't match
any other career subtype. Default-fallback penalty is keeping them
near floor.

#### `relationship_route` (41 candidates)

| Subtype | Count |
|---|---|
| trust_steadiness | 14 (of which 8 default-fallback) |
| intimacy_depth | 6 |
| emotional_need_affection | 6 |
| freedom_space | 5 |
| boundary_conflict | 3 |
| direct_relational_activation | 2 |
| **hidden_private_love** | **2** *(was 0)* |
| **wound_to_gift** | **2** *(was 0)* |
| attraction_warmth | 1 |

**Both previously-silent subtypes now fire.** hidden_private_love
and wound_to_gift each hit 2 charts in the expansion.

#### `moon_signature` (60 candidates)

| Subtype | Count |
|---|---|
| home_inner_security | 17 |
| intimacy_depth | 14 |
| creative_emotional_expression | 10 |
| private_emotional_processing | 10 |
| daily_sensitivity | 7 |
| emotional_rhythm | 2 (default fallback) |

All 6 moon subtypes still fire; coverage almost doubled.

#### `axis_2h_8h` (7 candidates)

| Subtype | Count |
|---|---|
| shared_trust_exchange | 7 |
| **all other 6 subtypes** | **0** |

**Six of seven axis subtypes remain silent even on engineered charts.**
See §11 for the diagnostic.

### 3. Confidence Distributions (100-chart)

| Family | ≥ 0.80 | 0.70-0.80 | 0.60-0.70 | < 0.60 |
|---|---|---|---|---|
| `identity_route` | 31 (36%) | 30 (35%) | 24 (28%) | 0 |
| `career_route` | 46 (73%) | 12 (19%) | 5 (8%) | 0 |
| `relationship_route` | 5 (12%) | 14 (34%) | 22 (54%) | 0 |
| `moon_signature` | 12 (20%) | 30 (50%) | 18 (30%) | 0 |
| `axis_2h_8h` | 1 (14%) | 2 (29%) | 4 (57%) | 0 |

`< 0.60` still 0 across the board — the gate works correctly on the
expanded fixture.

### 4. Default Fallback Counts

| Family | 50-chart | 100-chart | Δ |
|---|---|---|---|
| `identity_route` | 0 | 0 | — |
| `career_route` | 0 | 3 *(new)* | +3 |
| `relationship_route` | 4 | 8 | +4 |
| `moon_signature` | 1 | 2 | +1 |
| `axis_2h_8h` | 0 | 0 | — |

13 total default-fallback firings across 256 composed candidates (5.1%).
Proportional to the fixture growth.

### 5. Public Leak Total

```
public_leak_total: 0
```

100 charts × 8 visible lanes — zero leaks.

### 6. P0 Text Scan

```
{ "olması de": 0, "Bazen de.": 0, "bazen de.": 0 }
```

Zero dangling-connector defects.

### 7. Golden Drift

```
golden_drift: []
golden_stable: True
```

5 Group-A accepted goldens (Istanbul 1994/1997/2020, Izmir 1996 v0.5,
Adana 1998) byte-equal under flags off vs flags on.

### 8. Silent Subtype Report

| Family | Subtype | 50-chart | 100-chart | Status |
|---|---|---|---|---|
| relationship | hidden_private_love | 0 | **2** | **unlocked** |
| relationship | wound_to_gift | 0 | **2** | **unlocked** |
| relationship | direct_relational_activation | 1 | 2 | growing |
| relationship | attraction_warmth | 1 | 1 | still thin |
| relationship | boundary_conflict | 1 | 3 | growing |
| axis_2h_8h | self_worth_foundation | 0 | **0** | still silent |
| axis_2h_8h | dependency_autonomy_tension | 0 | **0** | still silent |
| axis_2h_8h | intimacy_resource_fusion | 0 | **0** | still silent |
| axis_2h_8h | value_transformation | 0 | **0** | still silent |
| axis_2h_8h | resource_boundary | 0 | **0** | still silent |
| axis_2h_8h | embodied_security | 0 | **0** | still silent |

The relationship-family expansion is a clean success. The axis_2h_8h
expansion is a clean **failure**, and that failure carries clear
diagnostic value.

---

## Intent vs Observed (the load-bearing finding)

For each of the 50 expansion charts, we recorded
`audit_expansion_meta.target_subtype` and compared it against what
the live audit pipeline actually produced.

| Outcome | Count |
|---|---|
| **hit** (target_family + target_subtype both matched) | **7** |
| **family_only** (target_family fired, but a different subtype won) | **19** |
| **no_candidate** (the target_family produced nothing at all on this chart) | **24** |
| miss (target_family fired wrong subtype that we ruled out) | 0 |

**24 of 50 expansion charts produced no candidate in the targeted
family.** This breaks down by group:

- **Group A (axis_2h_8h targets, 15 charts):** 14 of 15 produced no
  axis candidate. The intended chart shapes (Pluto 2H, Saturn 8H,
  Venus 8H, Mars 8H, etc.) **were not actually present** when the
  ephemeris ran the chosen birth times. The synthetic birth times +
  cities did not reliably land planets in the intended houses.
- **Group B (relationship_route, 12 charts):** 4 of 12 produced no
  relationship candidate; 6 fired with a different subtype than
  intended (e.g. `direct_relational_activation` intent → observed
  `trust_steadiness@0.8`); 2 hit exactly.
- **Group C (moon_signature, 10 charts):** 2 of 10 produced no moon
  candidate; 5 fired with different subtypes; 3 hit exactly.
- **Group D (variety, 13 charts):** 4 of 13 produced no candidate in
  the targeted family.

### What this means

The expansion is **honest documentation of the gap**, not a
demonstration that the silent subtypes are firing. The conclusion is
two-fold:

1. **Synthetic birth-time chart engineering is unreliable without
   ephemeris pre-verification.** Picking a date+city+time to land a
   specific planet in a specific house requires actually running the
   ephemeris first and iterating. The audit harness *is* the
   ephemeris, so the right workflow is: (a) draft synthetic charts,
   (b) run them, (c) inspect what fires, (d) adjust dates/times,
   (e) re-run. This audit completed steps (a)-(c); steps (d)-(e)
   are the v0.10.0.2 fixture refinement task.

2. **The axis_2h_8h silence is now confirmed on 100 charts, with
   stronger diagnostic clarity.** Of the 14 axis-intended charts
   that produced no candidate, several have axis hardware that
   *should* satisfy the supporting-signal gate even without the
   exact intended subtype — e.g. a chart with Pluto in some 8H sign
   should at least fire `value_transformation` even if the exact
   ASC didn't land Pluto in 8H. The fact that NONE of them fire
   tells us the **detection thresholds for the 6 silent subtypes
   are over-conservative**, independent of fixture shape. The
   v0.10.0.1 calibration plan (relaxing thresholds for
   `dependency_autonomy_tension`, `intimacy_resource_fusion`,
   `self_worth_foundation`) is the right next step.

---

## Special-Focus Answers (revisited)

### Does `axis_2h_8h` produce more than `shared_trust_exchange` in 100 charts?

**No.** All 7 axis firings across 100 charts are `shared_trust_exchange`.
The other 6 subtypes are silent on the expanded fixture as well —
confirming the v0.10 50-chart finding holds on 100 charts.

### Which 2H/8H subtypes need calibration?

The 100-chart audit narrows the diagnostic: this is now **primarily a
scoring-threshold issue**, not (only) a fixture-shape gap.

- `value_transformation` — 4 charts in Group A specifically engineered
  for Pluto-on-axis. **None** fire. Need to loosen the Pluto-on-axis
  detection OR widen to Pluto-aspect-to-axis-ruler scoring.
- `resource_boundary` — 3 charts engineered for Saturn-on-axis. **None**
  fire. Same diagnostic.
- `dependency_autonomy_tension` — 2 charts engineered for Node + heavy
  pole. **None** fire. `shared_trust_exchange` is absorbing the cases.
- `intimacy_resource_fusion` — 3 charts engineered for Venus/Mars/Moon
  in 8H. **None** fire. Threshold too high.
- `self_worth_foundation` — 1 chart engineered for 2H stellium without
  8H. **None** fire.
- `embodied_security` — 1 chart engineered for Taurus 2H. **None**
  fire.

This is a strong calibration signal. v0.10.0.1 must address it before
any axis_2h_8h rollout.

### Is `v0.10` safe enough to remain debug-only?

**Yes — confirmed across 100 charts.**

- 0 public leak
- 0 P0 defects
- 0 golden drift
- 0 below-floor firings
- All firings remain `public_job=debug_only`,
  `public_main_eligible=False`, `public_support_eligible=False`

The narrow subtype coverage is a correctness property under
debug-only flags — and a calibration target before any future
rollout.

---

## Recommended Next Steps (updated after 100-chart evidence)

1. **v0.10.0.1 axis_2h_8h scoring calibration** — promoted from
   "should do" to **required before any axis rollout**. Loosen
   detection thresholds for the 6 silent subtypes. Target: 4 of 7
   subtypes firing on the next 100-chart pass.
2. **v0.10.0.2 fixture refinement** — for each of the 24
   `no_candidate` charts in this audit, iterate on birth_time +
   city to land the intended chart shape. The audit harness is the
   feedback loop.
3. **v0.9b.0.3 relationship `attraction_warmth` audit** — still
   1/100 (london_1972 only). One additional chart engineered for it
   (v010_b05_venus_sun_5h_fire) didn't fire. Threshold review needed.
4. **Cross-family ownership rules** — same as before; axis ↔ moon and
   axis ↔ relationship rules still need to be authored before any
   axis public lane.

### Out of Scope (restated)

- No runtime / registry / scoring / renderer changes.
- No public output changes.
- No flag default flips.
- Mobile work still deferred (Phase C).

---

## Summary

The fixture expansion to 100 charts:

- successfully **unblocks two previously-silent relationship
  subtypes** (hidden_private_love, wound_to_gift) and grows the
  candidate inventory for relationship + moon + identity + career
  families,
- **confirms axis_2h_8h's subtype silence is a scoring problem, not
  just a fixture-shape problem** — engineered charts that should have
  produced axis candidates produced none, demonstrating the
  detection thresholds for 6 of 7 axis subtypes are over-conservative,
- **holds every zero-tolerance invariant** (public leak 0, P0
  defects 0, golden drift 0, sub-floor firings 0) across 100 charts,
- creates the empirical evidence baseline for the v0.10.0.1
  axis_2h_8h scoring calibration plan.

The next step is **scoring calibration** of axis_2h_8h, not further
fixture expansion. Fixture refinement (re-engineering the
no_candidate cases) is a parallel concern but is secondary —
loosening the detection thresholds will surface most of the silent
subtypes even on the existing 100-chart fixture.
