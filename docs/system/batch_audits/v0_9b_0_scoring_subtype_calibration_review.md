# v0.9b.0 Scoring and Subtype Calibration Review

> Analysis only. No code, scoring weights, registry, renderer, or
> selection changes are made by this document. All numbers are
> captured live from the 50-chart batch
> (`natal_50_chart_discovery_metrics.json`) on 2026-05-14 with the
> v0.9b master flags on:
>
> ```
> ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B=true
> ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B=true
> ```

## 1. `relationship_route` Candidate Quality

### 1.1 Subtype Distribution (24 charts of 50)

| Subtype | Count | % of relationship charts | Notes |
|---|---|---|---|
| `trust_steadiness` | 11 | 46% | **8 of 11 are default-fallback** (signal-incoherent or below-margin) |
| `intimacy_depth` | 5 | 21% | strongest signal-derived bucket |
| `emotional_need_affection` | 4 | 17% | Moon-anchored, consistent |
| `freedom_space` | 2 | 8% | thin coverage |
| `boundary_conflict` | 1 | 4% | single-chart outlier (see §1.4) |
| `attraction_warmth` | 1 | 4% | thin coverage |
| `hidden_private_love` | 0 | 0% | no charts fired this subtype |
| `wound_to_gift` | 0 | 0% | no charts fired this subtype |

**Read:** the long tail of subtypes (hidden_private_love, wound_to_gift,
boundary_conflict, attraction_warmth) has insufficient batch data to
calibrate. The default-fallback `trust_steadiness` dominates and
inflates the headline coverage number.

### 1.2 Confidence Distribution

| Bucket | Count | % | Plan §3 target |
|---|---|---|---|
| ≥ 0.80 | 4 | 17% | ~25% |
| 0.70 – 0.80 | 10 | 42% | ~35% |
| 0.60 – 0.70 | 10 | 42% | ~35% |
| < 0.60 | 0 | 0% | ≤ 5% (gate working) |

Distribution is healthy at the lower buckets. The high-confidence
bucket is slightly under target (17% vs 25%) — driven by the dominance
of `trust_steadiness` default-fallback floor scores.

### 1.3 Top High-Confidence Examples per Subtype

| Subtype | Chart | Conf | Read |
|---|---|---|---|
| `boundary_conflict` | `ankara_1993_06_10` | **0.94** | **suspicious outlier** (only chart with this subtype; see §1.4) |
| `intimacy_depth` | `mumbai_1977_07_07` | 0.87 | clean — 8H pattern + DSC ruler in 8H |
| `intimacy_depth` | `antalya_1999_02_27` | 0.745 | clean |
| `intimacy_depth` | `cairo_1991_01_15` | 0.71 | clean |
| `intimacy_depth` | `madrid_2004_04_18` | 0.68 | clean |
| `intimacy_depth` | `istanbul_2012_08_02` | 0.65 | clean |
| `emotional_need_affection` | `fix02_capricorn_stellium` | 0.80 | clean (Moon route + 7H) |
| `emotional_need_affection` | `fix09_edge_cusp_planet` | 0.75 | clean |
| `emotional_need_affection` | `berlin_1999_11_24` | 0.64 | borderline |
| `emotional_need_affection` | `diyarbakir_1994_03_22` | 0.625 | borderline |
| `trust_steadiness` *(signal-derived)* | `fix08_cancer_capricorn_nodes` | 0.80 | clean (real DSC ruler in trust pattern) |
| `trust_steadiness` *(signal-derived)* | `singapore_1983_10_19` | 0.72 | clean |
| `trust_steadiness` *(signal-derived)* | `sydney_1993_02_01` | 0.70 | borderline |
| `attraction_warmth` | `london_1972_12_30` | 0.715 | clean (Venus 5H fire) |
| `freedom_space` | `fix10_y2k_complex` | 0.605 | borderline |
| `freedom_space` | `adana_1998_09_12` | 0.60 | borderline |

### 1.4 Likely False Positives

**Highest concern — `trust_steadiness` default-fallback at high confidence:**

| Chart | Conf | Real signal? |
|---|---|---|
| `samsun_1970_07_29` | 0.79 | default-fallback (penalty 0.06 applied; still well above floor) |
| `mersin_1981_08_17` | 0.73 | default-fallback |
| `gaziantep_1986_01_08` | 0.71 | default-fallback |
| `trabzon_2001_09_14` | 0.71 | default-fallback |
| `amsterdam_1985_04_16` | 0.69 | default-fallback |
| `istanbul_1997_01_21` | 0.65 | default-fallback |
| `johannesburg_1990_12_12` | 0.61 | default-fallback |
| `fix11_unknown_birthtime` | 0.60 | default-fallback (and chart has no birthtime — degenerate input) |

Eight of the eleven `trust_steadiness` candidates are default-fallback
firings, meaning no subtype channel beat the runner-up by the 0.04
margin. The current default-fallback penalty (0.06–0.08) is too weak
to push these below the 0.60 floor when `dsc_route_strength` (0.25) +
`dsc_ruler_strength` (0.14–0.20) already accumulate to ~0.40
unconditionally.

**Outlier — `boundary_conflict @ 0.94` on `ankara_1993_06_10`:**

Single chart with this subtype, hitting the score cap. Either:
(a) genuinely a very clear Mars-7H + Mars-Saturn hard aspect chart, or
(b) multiple weak signals stacking into the bonus path. **Recommend
manual chart-fact verification before promoting this subtype to any
non-debug surface.**

**`freedom_space @ 0.60`** for `adana_1998_09_12` is at the floor and
borderline — recommend treating as debug-only until more `freedom_space`
fixtures exist (currently only 2 charts).

### 1.5 Where Relationship Composed Would Improve Generic Fallback

Charts with **≥3 raw generic_fallback packets** *and* a v0.9b
relationship candidate present — i.e. composed could plausibly suppress
the generic per the plan's §6 rule (confidence ≥ 0.70 + non-default
subtype + lived_scene present):

| Chart | generic_fallback | v0.9b relationship | Improvement candidate? |
|---|---|---|---|
| `mumbai_1977_07_07` | 9 | intimacy_depth @ 0.87 | **yes — clear win** |
| `fix02_capricorn_stellium` | n/a (fix chart) | emotional_need_affection @ 0.80 | yes |
| `fix08_cancer_capricorn_nodes` | 7 | trust_steadiness @ 0.80 (real) | yes |
| `fix09_edge_cusp_planet` | 9 | emotional_need_affection @ 0.75 | yes |
| `cairo_1991_01_15` | 9 | intimacy_depth @ 0.71 | borderline (just above 0.70 floor) |
| `madrid_2004_04_18` | 9 | intimacy_depth @ 0.68 | no (below 0.70) |
| `antalya_1999_02_27` | 3 | intimacy_depth @ 0.745 | yes |
| `ankara_1993_06_10` | 9 | boundary_conflict @ 0.94 | yes *but verify chart facts first* |
| `singapore_1983_10_19` | 9 | trust_steadiness @ 0.72 | yes |
| `london_1972_12_30` | 9 | attraction_warmth @ 0.715 | yes |

**Eight clean improvement opportunities** (yes column). Note this is
analysis-only; the §6 suppression rule is not active in v0.9b.0.

### 1.6 Where Exact Registry Already Owns Relationship Well

Of the 50 charts, 22 have an exact-registry relationship packet in
their candidate inventory. Of the 24 charts that produce a v0.9b
relationship candidate, **16 collide with existing registry
ownership** — meaning the registry exact (score ~0.95–0.99) already
wins selection and the composed candidate stays at `keep_for=["debug"]`
via the existing dedup-by-anchor path.

This is correct behavior. No registry edits are needed; v0.9b's value
is in the **8 clean opportunity charts** where no exact-registry
relationship packet exists (listed in §1.5 with "yes" verdict).

---

## 2. `moon_signature` Candidate Quality

### 2.1 Subtype Distribution (35 charts of 50)

| Subtype | Count | % of moon charts | Notes |
|---|---|---|---|
| `home_inner_security` | 8 | 23% | strongest single subtype, clean signal |
| `intimacy_depth` | 7 | 20% | high overlap with relationship_route (see §3) |
| `private_emotional_processing` | 6 | 17% | clean signal, includes top confidence |
| `emotional_rhythm` *(default)* | 5 | 14% | all 5 are default-fallback |
| `daily_sensitivity` | 5 | 14% | clean signal |
| `creative_emotional_expression` | 4 | 11% | clean signal |

**Read:** the Moon family distribution is far healthier than
relationship — six subtypes with reasonable coverage and a much lower
default-fallback share (14% vs relationship's 33%). The
authored-subtype channels are clearly differentiated by Moon house +
ruler placement.

### 2.2 Confidence Distribution

| Bucket | Count | % | Plan §3 target |
|---|---|---|---|
| ≥ 0.80 | 6 | 17% | ~25% |
| 0.70 – 0.80 | 17 | 49% | ~35% |
| 0.60 – 0.70 | 12 | 34% | ~35% |
| < 0.60 | 0 | 0% | ≤ 5% |

Strong middle band (49% in 0.70–0.80). High bucket slightly under
target but the 0.70+ combined share is 66%, which is acceptable for a
debug-only first cut.

### 2.3 Top High-Confidence Examples per Subtype

| Subtype | Chart | Conf | Read |
|---|---|---|---|
| `private_emotional_processing` | `antalya_1999_02_27` | **0.93** | clean — Moon 12H or Moon-Neptune |
| `home_inner_security` | `trabzon_2001_09_14` | 0.88 | clean — Moon 4H + IC route |
| `home_inner_security` | `fix08_cancer_capricorn_nodes` | 0.85 | clean |
| `private_emotional_processing` | `rome_1971_02_06` | 0.84 | clean |
| `home_inner_security` | `cairo_1991_01_15` | 0.81 | clean |
| `daily_sensitivity` | `kayseri_2003_12_11` | 0.80 | clean — Moon 6H |
| `creative_emotional_expression` | `istanbul_1994_06_25` | 0.785 | clean — Moon 5H aspect pattern |
| `private_emotional_processing` | `mersin_1981_08_17` | 0.785 | clean |
| `daily_sensitivity` | `diyarbakir_1994_03_22` | 0.775 | clean |
| `intimacy_depth` | `amsterdam_1985_04_16` | 0.775 | clean |
| `daily_sensitivity` | `mumbai_1977_07_07` | 0.765 | clean |
| `intimacy_depth` | `fix09_edge_cusp_planet` | 0.765 | clean |
| `creative_emotional_expression` | `eskisehir_1991_04_05` | 0.755 | clean |
| `intimacy_depth` | `fix04_h10_career_stellium` | 0.75 | clean |

### 2.4 Likely False Positives

**`emotional_rhythm` default-fallback firings:**

| Chart | Conf | Read |
|---|---|---|
| `fix07_aries_libra_nodes` | 0.73 | default-fallback at 0.73 — too high |
| `mexico_city_1988_08_31` | 0.61 | default-fallback at floor — acceptable |
| `london_1972_12_30` | 0.64 | default-fallback — acceptable |
| `johannesburg_1990_12_12` | 0.62 | default-fallback — acceptable |
| `adana_1998_09_12` | 0.60 | default-fallback at floor — acceptable |

The single anomaly is `fix07_aries_libra_nodes` at 0.73 — the Moon
score components stack to a high baseline even without a clear
subtype winner. Same root cause as relationship's
`trust_steadiness` issue: base `moon_sign_strength + moon_house_scene
+ moon_ruler_route` floor is 0.32+ unconditionally, leaving too much
room above the 0.60 publishable threshold for the default-fallback
penalty (0.06–0.08) to push back.

**No other concerning patterns.** All non-fallback Moon candidates
trace cleanly back to Moon house / Moon ruler / Moon-significator
aspect evidence.

### 2.5 Cases Where Moon Should Remain Debug-Only

- Any candidate with `subtype = emotional_rhythm` AND
  `subtype_default_fallback = True` (the 5 charts above) — the signal
  is non-coherent.
- Any candidate at confidence < 0.70 — keep below the §6 suppression
  threshold.
- `intimacy_depth` candidates that **also** fire on the same chart's
  `relationship_route` (see §3 cross-family overlap) — pick one owner
  before promotion.

### 2.6 Cases Where Moon Could Become Detail/Support Later

Strongest candidates for the first detail-eligibility promotion (after
calibration of the default-fallback penalty):

| Subtype | Charts (conf ≥ 0.80) |
|---|---|
| `home_inner_security` | `trabzon_2001_09_14` (0.88), `fix08_cancer_capricorn_nodes` (0.85), `cairo_1991_01_15` (0.81) |
| `private_emotional_processing` | `antalya_1999_02_27` (0.93), `rome_1971_02_06` (0.84) |
| `daily_sensitivity` | `kayseri_2003_12_11` (0.80) |

These six chart-subtype pairs are the cleanest signal in the entire
50-chart batch. They are the natural first slice for a future
`v0.9b.1` detail-eligibility rollout — but **only behind the existing
Phase B-style renderer allowlist**, never via a blanket flag.

---

## 3. Cross-Family Overlap Review

### 3.1 The 14 Overlap Charts

Charts where the same chart produces both a `relationship_route` and a
`moon_signature` candidate that share Moon evidence (
`evidence_trace.cross_family_overlap` non-empty on either side):

| Chart | relationship_route | moon_signature |
|---|---|---|
| `fix02_capricorn_stellium` | emotional_need_affection @ 0.80 | intimacy_depth @ 0.665 |
| `fix04_h10_career_stellium` | — | intimacy_depth @ 0.75 |
| `fix06_grand_trine_flow` | — | intimacy_depth @ 0.745 |
| `fix09_edge_cusp_planet` | emotional_need_affection @ 0.75 | intimacy_depth @ 0.765 |
| `istanbul_2012_08_02` | intimacy_depth @ 0.65 | — |
| `antalya_1999_02_27` | intimacy_depth @ 0.745 | (private_emotional_processing @ 0.93 — distinct) |
| `gaziantep_1986_01_08` | — | intimacy_depth @ 0.645 |
| `diyarbakir_1994_03_22` | emotional_need_affection @ 0.625 | — |
| `sydney_1993_02_01` | — | intimacy_depth @ 0.63 |
| `madrid_2004_04_18` | intimacy_depth @ 0.68 | (private_emotional_processing @ 0.76 — distinct) |
| `mumbai_1977_07_07` | intimacy_depth @ 0.87 | — |
| `cairo_1991_01_15` | intimacy_depth @ 0.71 | (home_inner_security @ 0.81 — distinct) |
| `berlin_1999_11_24` | emotional_need_affection @ 0.64 | — |
| `amsterdam_1985_04_16` | — | intimacy_depth @ 0.775 |

### 3.2 Pattern

Three overlap cases:

1. **Same subtype label (`intimacy_depth`) on both families** — 1 chart
   (`fix09_edge_cusp_planet`). Both candidates carry the
   `intimacy_depth` subtype name but the family contracts differ.
2. **Moon-Anchored relationship subtype + distinct Moon subtype** — 4
   charts (e.g. `antalya_1999_02_27`: relationship.intimacy_depth +
   moon.private_emotional_processing). The two candidates use
   overlapping Moon evidence but emerge in different semantic
   registers.
3. **Single-family Moon-Anchored** — 9 charts where only one of the
   two families fires but its evidence trace still flags the
   cross-family overlap because it consumed Moon facts. These do not
   "collide" — they're solo emissions.

### 3.3 Should Overlap Be Deduped, Linked, or Left Visible?

Current behavior (v0.9b.0):

- both candidates emit independently
- both are debug-only (no public surface), so no user-visible
  duplication
- the cluster plan's `composed_cross_family_overlap_count` metric
  surfaces the overlap for audit (14 across 50 charts)

Recommended **future** ownership rule for any non-debug rollout
(v0.9b.1+):

> **Moon-anchored relationship subtypes** (`emotional_need_affection`,
> `intimacy_depth` when emitted by `relationship_route`) **cede**
> ownership of the Moon evidence to `moon_signature` when both
> families fire on the same chart **and** the Moon-signature confidence
> meets-or-exceeds the relationship confidence by 0.05 or more.
> Otherwise the relationship candidate keeps ownership.
>
> The relationship candidate is **not suppressed** — it stays in
> trace — but its renderer-eligibility (later v0.9b.1+) is gated by
> this ownership check.

This rule keeps the relationship reading intact when it's clearly
stronger (e.g. `mumbai_1977_07_07` relationship.intimacy_depth @ 0.87,
no Moon competitor) and routes Moon-flavored reads to the Moon family
when Moon's reading is the stronger one
(e.g. `antalya_1999_02_27`: moon @ 0.93 vs rel @ 0.745 — Moon wins).

The rule is **deferred for implementation** — v0.9b.0 ships with both
emissions visible in trace only.

---

## 4. Opportunity Severity Proposal

Applying the existing
`composed_opportunity_severity_distribution` taxonomy
(`high_priority_opportunity`, `medium_priority_opportunity`,
`debug_observation_only`) to the new families. **No code change** —
this is a proposal for how the ledger should classify v0.9b candidates
when the next opportunity-analyzer pass is run.

### 4.1 `relationship_route`

**high_priority_opportunity** — composed candidate clearly improves a
generic/discovery-dominated chart, signal is non-fallback, confidence
≥ 0.75:

- `mumbai_1977_07_07` · intimacy_depth @ 0.87
- `fix02_capricorn_stellium` · emotional_need_affection @ 0.80
- `fix08_cancer_capricorn_nodes` · trust_steadiness @ 0.80
- `fix09_edge_cusp_planet` · emotional_need_affection @ 0.75

**medium_priority_opportunity** — non-fallback signal, confidence
0.65–0.75:

- `antalya_1999_02_27` · intimacy_depth @ 0.745
- `singapore_1983_10_19` · trust_steadiness @ 0.72
- `london_1972_12_30` · attraction_warmth @ 0.715
- `cairo_1991_01_15` · intimacy_depth @ 0.71
- `sydney_1993_02_01` · trust_steadiness @ 0.70
- `madrid_2004_04_18` · intimacy_depth @ 0.68
- `istanbul_2012_08_02` · intimacy_depth @ 0.65

**debug_observation_only** — default-fallback firings, low confidence,
single-chart outliers needing manual verification:

- all 8 `trust_steadiness` default-fallback firings (samsun, mersin,
  gaziantep, trabzon, amsterdam, istanbul_1997, johannesburg, fix11)
- `ankara_1993_06_10` · boundary_conflict @ 0.94 *(single-chart
  outlier; flagged for chart-fact verification before promotion)*
- `freedom_space` candidates (only 2 charts, conf at floor)
- `emotional_need_affection` candidates at conf < 0.70
  (`diyarbakir_1994_03_22` @ 0.625, `berlin_1999_11_24` @ 0.64)

### 4.2 `moon_signature`

**high_priority_opportunity** — non-fallback, confidence ≥ 0.80:

- `antalya_1999_02_27` · private_emotional_processing @ 0.93
- `trabzon_2001_09_14` · home_inner_security @ 0.88
- `fix08_cancer_capricorn_nodes` · home_inner_security @ 0.85
- `rome_1971_02_06` · private_emotional_processing @ 0.84
- `cairo_1991_01_15` · home_inner_security @ 0.81
- `kayseri_2003_12_11` · daily_sensitivity @ 0.80

**medium_priority_opportunity** — non-fallback, confidence 0.70–0.80:

- `istanbul_1994_06_25` · creative_emotional_expression @ 0.785
- `mersin_1981_08_17` · private_emotional_processing @ 0.785
- `diyarbakir_1994_03_22` · daily_sensitivity @ 0.775
- `amsterdam_1985_04_16` · intimacy_depth @ 0.775
- `mumbai_1977_07_07` · daily_sensitivity @ 0.765
- `fix09_edge_cusp_planet` · intimacy_depth @ 0.765
- `eskisehir_1991_04_05` · creative_emotional_expression @ 0.755
- `fix04_h10_career_stellium` · intimacy_depth @ 0.75
- `fix06_grand_trine_flow` · intimacy_depth @ 0.745
- `paris_1986_05_12` · private_emotional_processing @ 0.73
- `bursa_1987_11_03` · home_inner_security @ 0.72
- `new_york_1984_10_02` · home_inner_security @ 0.72
- `buenos_aires_1980_09_09` · home_inner_security @ 0.71
- `los_angeles_1994_07_28` · home_inner_security @ 0.76

**debug_observation_only** — default-fallback emotional_rhythm firings
and low-confidence borderline cases:

- all 5 `emotional_rhythm` default-fallback firings
- all candidates at conf < 0.70

---

## 5. Detail/Support Readiness

### 5.1 Subtypes Safest for Future Detail Eligibility

| Subtype | Family | Reason |
|---|---|---|
| `home_inner_security` | moon_signature | Strong, clear signal across 8 charts; 3 at conf ≥ 0.80; no false positives observed; Moon-4H / IC route is unambiguous |
| `private_emotional_processing` | moon_signature | 6 charts, 2 at conf ≥ 0.80; Moon-12H / Moon-Neptune route is distinctive |
| `intimacy_depth` (moon family) | moon_signature | 7 charts, signal is consistent; **caveat**: shares label with relationship.intimacy_depth (see §3 ownership rule) |

### 5.2 Subtypes That Should Remain Debug-Only

| Subtype | Family | Reason |
|---|---|---|
| `trust_steadiness` | relationship_route | 73% default-fallback share; penalty doesn't push below 0.60 |
| `emotional_rhythm` | moon_signature | 100% default-fallback by construction (it IS the default); only fires when no other subtype wins |
| `boundary_conflict` | relationship_route | single-chart outlier needing manual verification |
| `attraction_warmth` | relationship_route | single chart (london); needs more batch data |
| `freedom_space` | relationship_route | 2 charts only, both at the 0.60 floor |
| `hidden_private_love` | relationship_route | 0 charts fired this — detection rules likely too strict |
| `wound_to_gift` | relationship_route | 0 charts fired this — detection rules likely too strict |

### 5.3 Recommended First Rollout Slice (v0.9b.1 narrowest)

If the next phase is detail-eligibility activation (not full
public_support), the narrowest defensible slice is:

```
family   = moon_signature
subtype  = home_inner_security
confidence threshold = 0.80
allowlist = trabzon_2001_09_14, fix08_cancer_capricorn_nodes, cairo_1991_01_15
flag     = ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT (already exists)
+ renderer signature gate widened to a moon_signature variant matcher
  (Phase B-style allowlist, fresh audit)
```

This gives **3 charts** as the live-audit surface — the same shape as
v0.9a.2's Phase A→B path, and small enough to manually verify every
rendered card before promotion.

The runner-up slice (next safest if home_inner_security ships clean):

```
family   = moon_signature
subtype  = private_emotional_processing
threshold = 0.80
allowlist = antalya_1999_02_27, rome_1971_02_06
```

---

## 6. Regression

### 6.1 Accepted Goldens No-Op

Captured live: 5 Group-A audit charts (Istanbul 1994 / 1997 / 2020,
Izmir 1996 v0.5, Adana 1998) under v0.9b flags ON vs OFF using the
`_projection_surface_snapshot` helper (which strips `traceability`):

```
golden_drift_charts: []
golden_stable: True
```

Byte-stable across all four flag combos.

### 6.2 Public Leak Total

Captured live across the full 50-chart batch with both family flags
+ detail-support flag + Phase B render/lane flags simultaneously ON:

```
public_leak_total: 0
```

Surfaces inspected: `profile_public.blocks`, `core_blocks`,
`extra_blocks`, `detail_cards`, `composed_detail_cards` and
`profile_v8.hero`, `identity_axis`, `insight_strip`, `differentiators`.
No v0.9b candidate `id` or `node_id` prefix appears anywhere.

### 6.3 P0 Truthfulness Scans

Captured live across all 50 charts:

```
{'olması de': 0, 'Bazen de.': 0, 'bazen de.': 0}
```

No new dangling-connector defects introduced by the v0.9b TR copy
seeds. The post-v0.9a.3 P0 fix continues to hold.

### 6.4 Focused Test Suite

```
========================= 142 passed in 36.24s =========================
```

(125 → 142, +17 new v0.9b tests). All v0.9a + v0.9a.1/2/3 tests
continue to pass unchanged.

---

## 7. Final Recommendation

**Keep v0.9b.0 debug-only. Calibrate scoring before any detail
rollout.**

### 7.1 Required Calibration Before v0.9b.1

1. **Stronger default-fallback penalty.** Current penalty
   (`subtype_penalty = 0.06–0.08`) is too weak. With base scoring
   producing ~0.40 unconditionally, default-fallback candidates land
   in the 0.65–0.80 range — masquerading as medium-confidence finds.
   Bump penalty to `0.10–0.15` to push default-fallback below 0.65
   in most cases.

2. **Single-chart subtype audit.** `boundary_conflict @ 0.94` on
   `ankara_1993_06_10` is the only chart hitting that subtype and
   sits at the score cap. Verify chart facts manually before
   classifying as `high_priority_opportunity`. Same applies to
   `attraction_warmth @ 0.715` on `london_1972_12_30` (single chart).

3. **Subtype gap audit.** `hidden_private_love` and `wound_to_gift`
   fired on 0/50 charts. Either the detection rules are too strict or
   the 50-chart batch underrepresents those signatures. Re-examine
   the rules in `_build_relationship_route_candidates` and consider
   relaxing the primary-signal thresholds.

4. **Cross-family ownership rule (§3.3) — implement before detail
   rollout.** Otherwise v0.9b.1 would emit duplicate Moon-flavored
   readings on the 14 overlap charts.

5. **Wait for 50→100 chart batch expansion** before promoting any
   subtype to detail eligibility. Single-chart subtypes
   (`attraction_warmth`, `boundary_conflict`) cannot be safely
   promoted on n=1 evidence.

### 7.2 Path Options

| Option | When |
|---|---|
| **Keep debug-only, calibrate scoring** (recommended) | Now. Implement §7.1.1, §7.1.4. Re-run this audit. Decide §7.2 on fresh metrics. |
| **Enable detail for `moon_signature.home_inner_security` (narrow slice)** | After §7.1.1 calibration ships clean. Use the 3-chart allowlist in §5.3 + the Phase B-style renderer signature gate. |
| **Enable detail for both `home_inner_security` and `private_emotional_processing`** | After narrow-slice rollout proves stable and `cross_family_overlap` ownership rule (§3.3) is implemented. |
| **Wait for more batch data** | If calibration §7.1.1 is non-trivial or if there's interest in expanding the fixture set first. The current single-chart subtypes (boundary_conflict, attraction_warmth) cannot graduate on n=1 evidence regardless of scoring tuning. |

### 7.3 Single-Sentence Verdict

> v0.9b.0 ships as designed; before any public-facing graduation,
> tighten the default-fallback penalty (relationship `trust_steadiness`
> overfires at 0.70+) and implement the cross-family Moon-ownership
> rule. The first defensible detail-eligibility slice is
> `moon_signature.home_inner_security` at confidence ≥ 0.80 — three
> charts, audit-sized, renderer-gated.
