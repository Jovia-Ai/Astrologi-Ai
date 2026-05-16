# v0.10 Compositional Grammar Debug Audit

> Analysis only. No code, registry, scoring, renderer, or selection
> changes are made by this document. Flags configured per the audit
> brief — all v0.9a / v0.9b / v0.10 debug-only flags ON, all
> rollout/render/public-lane flags OFF.

## Audit Configuration

```
ENABLE_NATAL_PROMISE_PROJECTION_V1                      = true
ENABLE_NATAL_PROMISE_PACKET_DEBUG                       = true
ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9                    = true
ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B = true
ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B    = true
ENABLE_NATAL_COMPOSED_SEMANTICS_AXIS_2H_8H_V0_10        = true

# all rollout flags off (default-false):
ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT
ENABLE_NATAL_COMPOSED_SEMANTICS_AXIS_2H_8H_DETAIL_SUPPORT
ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL
ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE
ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_HOME_INNER_SECURITY_PUBLIC_DETAIL_LANE
ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN
```

## Fixture Note

The requested 100-chart batch is **not yet provisioned**. The current
`natal_50_chart_discovery_metrics.json` fixture carries 50 charts;
this audit therefore runs against those 50. The user-supplied
1998-03-05 chart was used as a synthetic stress case in the v0.10
implementation tests but is not in the batch fixture.

A **fixture expansion to 100 charts** is the most pressing next step
for the audit harness — flagged in §15 below.

---

## 1. Composed Candidate Counts by Family

| Family | Charts firing | % of 50 |
|---|---|---|
| `identity_route` | 44 | 88% |
| `moon_signature` | 31 | 62% |
| `career_route` | 29 | 58% |
| `relationship_route` | 22 | 44% |
| `axis_2h_8h` | 6 | 12% |

Read: identity and career are saturating. Moon and relationship are
mid-tier. axis_2h_8h is the narrowest by design — its gate requires
multi-signal evidence and the default-fallback penalty + supporting
signal threshold filter out under-evidenced cases.

## 2. Subtype Distributions by Family

### `identity_route` (44 candidates, 5 subtypes)

| Subtype | Count |
|---|---|
| `private_identity_spine` | 17 |
| `direct_identity_spine` | 12 |
| `controlled_identity_spine` | 6 |
| `relational_identity_spine` | 6 |
| `mediated_identity_spine` | 3 |

Healthy distribution across all 5 authored subtypes.

### `career_route` (29 candidates, 5 subtypes)

| Subtype | Count |
|---|---|
| `invisible_preparation_before_visibility` | 11 |
| `public_voice` | 7 |
| `creative_visibility` | 5 |
| `action_initiative` | 4 |
| `authority_responsibility` | 2 |

Note: `strategic_role` (the default fallback) has 0 firings — the
calibrated scoring keeps it filtered below the floor.

### `relationship_route` (22 candidates, 7 subtypes)

| Subtype | Count |
|---|---|
| `trust_steadiness` | 8 (of which 4 are default-fallback) |
| `intimacy_depth` | 5 |
| `emotional_need_affection` | 4 |
| `freedom_space` | 2 |
| `boundary_conflict` | 1 |
| `attraction_warmth` | 1 |
| `direct_relational_activation` | 1 |
| `hidden_private_love` | 0 |
| `wound_to_gift` | 0 |

Two subtypes (`hidden_private_love`, `wound_to_gift`) still fire on
0 charts — confirmed gap, consistent with the v0.9b.0.1 audit.

### `moon_signature` (31 candidates, 6 subtypes)

| Subtype | Count |
|---|---|
| `home_inner_security` | 8 |
| `intimacy_depth` | 7 |
| `private_emotional_processing` | 6 |
| `daily_sensitivity` | 5 |
| `creative_emotional_expression` | 4 |
| `emotional_rhythm` | 1 (default-fallback) |

Healthiest distribution of the five families.

### `axis_2h_8h` (6 candidates, **1 subtype**)

| Subtype | Count |
|---|---|
| `shared_trust_exchange` | 6 |
| `self_worth_foundation` | 0 |
| `dependency_autonomy_tension` | 0 |
| `intimacy_resource_fusion` | 0 |
| `value_transformation` | 0 |
| `resource_boundary` | 0 |
| `embodied_security` | 0 |

**Six of seven subtypes never fire in the 50-chart batch.** See §15
for the calibration verdict.

## 3. Confidence Distributions

| Family | ≥ 0.80 | 0.70–0.80 | 0.60–0.70 | < 0.60 |
|---|---|---|---|---|
| `identity_route` | 13 (30%) | 16 (36%) | 15 (34%) | 0 |
| `career_route` | 22 (76%) | 4 (14%) | 3 (10%) | 0 |
| `relationship_route` | 4 (18%) | 8 (36%) | 10 (46%) | 0 |
| `moon_signature` | 6 (19%) | 16 (52%) | 9 (29%) | 0 |
| `axis_2h_8h` | 1 (17%) | 1 (17%) | 4 (66%) | 0 |

career_route is the strongest signal family by far — 76% of its
firings are high-confidence. relationship/moon/axis cluster around
medium-confidence; identity is bimodal.

`lt_0_60` is 0 across all families: the confidence floor gate works
correctly.

## 4. Default Fallback Counts

| Family | Default-fallback firings |
|---|---|
| `identity_route` | 0 |
| `career_route` | 0 |
| `relationship_route` | 4 |
| `moon_signature` | 1 |
| `axis_2h_8h` | 0 |

Total: **5 default-fallback firings across 132 composed candidates
(3.8%)**. The v0.9b.0.1 penalty bump is holding.

## 5. Cross-Family Overlaps

| Overlap | Count |
|---|---|
| Moon owns relationship Moon evidence (v0.9b.0.1 rule) | 4 |
| `axis_2h_8h` + `relationship_route` on same chart | 2 |
| `axis_2h_8h` + `moon_signature` on same chart | 6 (i.e. every axis chart also has a moon candidate) |

**Moon vs relationship**: 4 charts trigger the ownership rule. Cairo,
Antalya, Madrid, Diyarbakir — all relationship candidates marked
`future_renderer_eligibility_blocked=True` while their Moon family
takes ownership of the shared evidence.

**2H/8H vs relationship**: 2 charts. These cases need an additional
ownership rule before v0.10.1, otherwise an eventual axis_2h_8h public
lane would compete with relationship_route on the same emotional
signature.

**2H/8H vs Moon**: 6 charts (100% of axis firings). Every chart that
produces an axis candidate also produces a Moon candidate. This is
**not** a defect — the families read different aspects of the same
deep-evidence cluster — but a future detail lane for axis_2h_8h must
add a Moon-priority ownership rule analogous to the v0.9b.0.1 rule.

## 6. Top High-Confidence Candidates per Subtype

### `identity_route`

| Chart | Subtype | Conf |
|---|---|---|
| berlin_1999_11_24 | direct_identity_spine | 0.90 |
| fix11_unknown_birthtime | relational_identity_spine | 0.86 |
| new_york_1984_10_02 | direct_identity_spine | 0.86 |

### `career_route`

| Chart | Subtype | Conf |
|---|---|---|
| fix04_h10_career_stellium | public_voice | 0.94 |
| izmir_1996_03_08 | authority_responsibility | 0.94 |
| istanbul_1997_01_21 | public_voice | 0.94 |

### `relationship_route`

| Chart | Subtype | Conf |
|---|---|---|
| ankara_1993_06_10 | boundary_conflict | 0.94 |
| mumbai_1977_07_07 | intimacy_depth | 0.87 |
| fix02_capricorn_stellium | emotional_need_affection | 0.80 |

### `moon_signature`

| Chart | Subtype | Conf |
|---|---|---|
| antalya_1999_02_27 | private_emotional_processing | 0.93 |
| trabzon_2001_09_14 | home_inner_security | 0.88 |
| fix08_cancer_capricorn_nodes | home_inner_security | 0.85 |

### `axis_2h_8h`

| Chart | Subtype | Conf |
|---|---|---|
| fix04_h10_career_stellium | shared_trust_exchange | 0.91 |

Only one axis candidate hits ≥ 0.80 in the batch.

## 7. Subtypes with 0 or Low Firing

| Family | Subtype | Count |
|---|---|---|
| `relationship_route` | `hidden_private_love` | 0 |
| `relationship_route` | `wound_to_gift` | 0 |
| `relationship_route` | `boundary_conflict` | 1 (ankara_1993 outlier) |
| `relationship_route` | `attraction_warmth` | 1 (london_1972 only) |
| `relationship_route` | `direct_relational_activation` | 1 (Sanliurfa-derived signal in batch) |
| `axis_2h_8h` | `self_worth_foundation` | 0 |
| `axis_2h_8h` | `dependency_autonomy_tension` | 0 |
| `axis_2h_8h` | `intimacy_resource_fusion` | 0 |
| `axis_2h_8h` | `value_transformation` | 0 |
| `axis_2h_8h` | `resource_boundary` | 0 |
| `axis_2h_8h` | `embodied_security` | 0 |

The axis_2h_8h row is the most striking — six of seven subtypes
silent. Three explanations, in descending likelihood:

1. **Fixture-shape gap**: Pluto-in-2H/8H, Saturn-in-2H/8H, earth-
   2H-cusp charts are simply not in the 50-chart fixture. These
   subtypes will start firing once the fixture is expanded to 100.
2. **Threshold over-conservatism**: `dependency_autonomy_tension`,
   `self_worth_foundation`, and `intimacy_resource_fusion` should
   each have realistic candidates in a chart of 50, but the current
   scoring requires too-specific anchors. Likely needs threshold
   loosening for the next calibration pass.
3. **Subtype concept overlap**: `shared_trust_exchange` is broad
   enough to absorb most axis cases that the other subtypes would
   logically own. The scoring channels overlap.

## 8. Generic Fallback Public_main Owners Remaining

46 of 50 charts (92%) carry at least one `generic_fallback` packet in
their `public_main_cluster_ids`. Distribution by fallback count per
chart:

| Fallback count | Charts |
|---|---|
| 5 | adana_1998_09_12 |
| 4 | fix01, fix04, fix10, konya_1974, kutahya_1959, izmir_2007, new_york_1984, madrid_2004, mumbai_1977, cairo_1991, mexico_city_1988 |
| 3 | fix03, fix05, fix06, fix07, fix08, fix09, fix11, istanbul_2020, ankara_1993, trabzon_2001, gaziantep_1986, diyarbakir_1994, samsun_1970, kayseri_2003, eskisehir_1991, mersin_1981, london_1972, tokyo_1998, buenos_aires_1980, sydney_1993, paris_1986, rome_1971, sao_paulo_2002, toronto_1976, dubai_1995, singapore_1983 |
| 2 | izmir_1996_v0.5, istanbul_2012, bursa_1987, antalya_1999, berlin_1999, los_angeles_1994, johannesburg_1990, amsterdam_1985, fix02 |
| 0 | izmir_1996_03_08, istanbul_1994_06_25, istanbul_1997_01_21 |

The four charts in the `90-100` health bucket are the only ones with
≤ 1 generic fallback. The composed families are *eligible* to replace
many of these fallbacks under a future suppression rule (see §11) but
do not do so in this debug-only audit.

## 9. Health Score Distribution

| Bucket | Charts |
|---|---|
| 90-100 | 4 (izmir_1996_03_08, istanbul_1994_06_25, istanbul_1997_01_21, fix02_capricorn_stellium) |
| 70-89 | 23 |
| 50-69 | 23 |
| 30-49 | 0 |
| < 30 | 0 |

Median: **70**.

Distribution is healthier than the post-v0.9a.3 health audit (which
saw a median of 65 on the 9-chart slice): the composed families
visible in the candidate inventory pull the score up via the
`composed_candidate_count` metric, even though their public surface
is unchanged.

## 10. Top 10 Charts Needing Semantic Coverage

Sorted by health_score (ascending), with `generic_fallback /
discovery_scaffold` packet counts in trace:

| Chart | Health | generic_fallback | discovery_scaffold |
|---|---|---|---|
| fix06_grand_trine_flow | 60 | 9 | 6 |
| fix03_pisces_cancer_water | 64 | 9 | 6 |
| fix04_h10_career_stellium | 64 | 9 | 6 |
| fix07_aries_libra_nodes | 64 | 9 | 7 |
| fix11_unknown_birthtime | 64 | 0 | 8 |
| kutahya_1959_10_21 | 64 | 9 | 5 |
| ankara_1993_06_10 | 64 | 9 | 6 |
| konya_1974_05_19 | 64 | 9 | 6 |
| trabzon_2001_09_14 | 64 | 9 | 6 |
| gaziantep_1986_01_08 | 64 | 9 | 6 |

The pattern: fixture charts (`fix01`–`fix11`) dominate the coverage
gap because they were authored as edge-case stress tests. The
non-fixture cities at health 64 (kutahya, konya, ankara, trabzon,
gaziantep) are the real coverage opportunities for v0.9b/v0.10
extensions.

## 11. Top 10 Charts Where Composed Could Replace Generic Fallback

Charts with ≥ 1 composed candidate at confidence ≥ 0.70 AND ≥ 1
`generic_fallback` packet in trace (sorted by fallback count):

| Chart | Composed candidates (conf ≥ 0.70) | Generic fallback count |
|---|---|---|
| fix01_leo_leo_classic | identity/direct_identity_spine@0.81 | 9 |
| fix04_h10_career_stellium | career/public_voice@0.94 · axis/shared_trust_exchange@0.91 · identity/controlled_identity_spine@0.75 · moon/intimacy_depth@0.75 | 9 |
| fix05_t_square_tense | identity/direct_identity_spine@0.75 | 9 |
| fix06_grand_trine_flow | moon/intimacy_depth@0.745 · identity/private_identity_spine@0.71 | 9 |
| fix09_edge_cusp_planet | moon/intimacy_depth@0.765 · identity/direct_identity_spine@0.76 · relationship/emotional_need_affection@0.75 · career/action_initiative@0.70 | 9 |
| kutahya_1959_10_21 | career/creative_visibility@0.87 · identity/controlled_identity_spine@0.83 | 9 |
| izmir_2007_07_19 | career/authority_responsibility@0.94 · identity/controlled_identity_spine@0.75 | 9 |
| ankara_1993_06_10 | relationship/boundary_conflict@0.94 · identity/relational_identity_spine@0.80 | 9 |
| konya_1974_05_19 | career/invisible_preparation_before_visibility@0.82 | 9 |
| trabzon_2001_09_14 | career/creative_visibility@0.94 · moon/home_inner_security@0.88 · axis/shared_trust_exchange@0.72 · identity/private_identity_spine@0.70 | 9 |

These ten charts are the highest-ROI candidates for a future composed
→ generic-fallback suppression rule (v0.10.1+). Each carries a
strong composed reading **and** ≥ 9 generic fallback packets that
the composed candidate would semantically improve.

## 12. Accepted Golden Stability

```
golden_drift: []
golden_stable: True
```

5 Group-A audit charts (Istanbul 1994/1997/2020, Izmir 1996 v0.5,
Adana 1998) under v0.10 + v0.9b flags ON vs OFF — byte-equal
projection-surface snapshots.

## 13. Public Leak Total

```
public_leak_total: 0
```

Across 50 charts × 8 visible lanes
(`blocks` / `core_blocks` / `extra_blocks` / `detail_cards` /
`composed_detail_cards` / v8 hero / v8 identity_axis /
v8 differentiators / v8 insight_strip) × all flag combinations:

- 0 `composed_identity_route_v0_9a` leak
- 0 `composed_career_route_v0_9a` leak
- 0 `composed_relationship_route_v0_9b` leak
- 0 `composed_moon_signature_v0_9b` leak (only the 3-chart Phase-B-style
  v0.9b.1 lane is wired and it's off in this audit)
- 0 `composed_axis_2h_8h_v0_10` leak

## 14. P0 Text Scan

```
{ "olması de": 0, "Bazen de.": 0, "bazen de.": 0 }
```

Zero dangling-connector defects across all 50 charts' visible copy.
The v0.9a.3 P0 fix continues to hold under all v0.9b + v0.10 flag
combinations.

---

## 15. Special Focus

### Does `axis_2h_8h` produce more than `shared_trust_exchange` in 100 charts?

**Not in the current 50-chart batch.** All 6 axis firings produce
`shared_trust_exchange`. The other 6 subtypes
(`self_worth_foundation`, `dependency_autonomy_tension`,
`intimacy_resource_fusion`, `value_transformation`,
`resource_boundary`, `embodied_security`) are all silent.

Diagnostic:

- `value_transformation` requires Pluto in 2H or 8H — **no chart in
  the batch has it**. Pluto sits in 5H, 8H (no — checked, none have
  Pluto in 8H), 6H, etc. Pure fixture-shape gap.
- `resource_boundary` requires Saturn in 2H or 8H — likewise no chart
  has it.
- `embodied_security` requires earth-sign 2H cusp combined with no
  8H burden — no batch chart fits.
- `dependency_autonomy_tension` requires Node + heavy opposite pole.
  A few batch charts have Node in 2H or 8H but the opposite pole is
  not "heavy enough" by the current threshold; the
  `shared_trust_exchange` channel absorbs them first.
- `intimacy_resource_fusion` requires Venus/Mars/Moon/Pluto in 8H.
  The current threshold (`0.06 + 0.04 × len(intimacy_8h)`) starts at
  0.10 for a single planet; `shared_trust_exchange` outscores it on
  charts that also have Node on axis or ruler-route.
- `self_worth_foundation` requires 2H heavy WITHOUT 8H competition.
  The batch has no 2H stellium chart that lacks 8H content.

### Which 2H/8H subtypes need calibration?

Two distinct buckets:

**A. Need fixture expansion, not scoring change:**

- `value_transformation` (Pluto 2H/8H)
- `resource_boundary` (Saturn 2H/8H)
- `embodied_security` (earth 2H + no 8H heat)

These have unambiguous chart signatures. Expand the fixture to 100
and they will fire on their natural charts.

**B. Need threshold relaxation in v0.10.0.1 calibration:**

- `dependency_autonomy_tension` should not be drowned out by
  `shared_trust_exchange` when Node is on axis with weight on the
  opposite pole. Currently both fire on the same chart but
  shared_trust always wins on margin. Proposed: stronger weight for
  Node-on-axis when the heavy pole is the opposite of the Node house.
- `intimacy_resource_fusion` should be promoted when 8H has Venus or
  Mars AND there's a Venus-Pluto contact. Currently the channel is
  too conservative.

### Is v0.10 safe enough to remain debug-only?

**Yes, indefinitely if needed.**

- All v0.10 flags default to false.
- 0 public surface leak across 50 charts.
- 0 golden drift across the accepted golden set.
- 0 P0 defects introduced.
- Subtype coverage is narrow (1/7) but that is a *correctness*
  property in debug-only mode — only the strongest signal channel
  emits, and that channel is itself well-evidenced (5/6 firings have
  Node on axis + luminary + ruler route).

The narrow subtype coverage **is not** a blocker for the debug-only
slice. It would only become a blocker before a public detail lane
rollout, which v0.10 explicitly defers.

---

## Recommended Next Steps

1. **Expand fixture from 50 to 100 charts.** Highest ROI across the
   entire grammar. Will surface the silent axis_2h_8h subtypes,
   provide n>1 evidence for relationship `boundary_conflict` /
   `attraction_warmth` / `direct_relational_activation`, and create
   the empirical baseline for v0.10.0.1 / v0.9b.0.2 calibration.
2. **v0.10.0.1 axis_2h_8h scoring calibration.** Loosen thresholds
   for `dependency_autonomy_tension` and `intimacy_resource_fusion`
   (per §15). Re-run this audit. Goal: at least 4 of the 7 axis
   subtypes firing on the expanded fixture.
3. **v0.9b.0.2 relationship subtype gap audit.** Re-examine the
   `hidden_private_love` and `wound_to_gift` detection rules — still
   0/50 firing. Suspect the primary-signal thresholds are too
   restrictive.
4. **v0.10 cross-family ownership rules.** Establish the analog of
   the v0.9b.0.1 Moon-ownership rule for the axis ↔ relationship and
   axis ↔ moon overlaps (§5). Required before any axis public lane,
   not before v0.10.0.1.
5. **Composed → generic fallback suppression rule (v0.10.1).** §11
   identifies 10 high-ROI charts. Before suppression goes live, the
   rule needs its own audit (chart-by-chart copy QA + golden delta
   review).

### Out of Scope (restated)

- No code, registry, scoring, renderer, or selection changes in this
  audit.
- No public output changes.
- No flag default flips.
- No mobile work.

---

## Summary

The five-family compositional grammar is stable under the
debug-only audit configuration:

- 132 composed candidates across 50 charts, 0 public leak, 0 P0
  defects, 0 golden drift.
- identity, career, moon, relationship families distribute across
  their authored subtypes with healthy margins.
- `axis_2h_8h` fires narrowly (1/7 subtypes, 6/50 charts) — a
  correctness property in debug-only mode, but a calibration target
  before any future rollout.
- The dominant next step is **fixture expansion to 100 charts**;
  every other calibration / coverage / ownership-rule question is
  bottlenecked on more empirical evidence.
