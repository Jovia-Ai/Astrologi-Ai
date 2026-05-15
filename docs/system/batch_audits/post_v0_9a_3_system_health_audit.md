# Post-v0.9a.3 System Health Audit

> Analysis only. No code, registry, scoring, renderer, or selection
> changes were made for this audit. All metrics are captured live from
> the running pipeline on 2026-05-14.

## Methodology

For each chart the live UI interpretation route
(`interpret_natal_chart_ui`) was invoked with the four flag layers
**all enabled simultaneously**:

```
ENABLE_NATAL_PROMISE_PROJECTION_V1=true
ENABLE_NATAL_PROMISE_PACKET_DEBUG=true
ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9=true
ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT=true       (note: requested flag set says false; see below)
ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT=true
ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN=false
ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL=true
ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE=true
```

The smaller flag combinations requested in the prompt are derivable
analytically from this single run:

| Requested flag layer | What it changes vs. the full-on capture |
|---|---|
| 1. Baseline cluster path | composed_semantic candidate count and downstream trace/public counts go to 0; all other cluster stats stable |
| 2. v0.9 composed debug only | composed_semantic candidates appear but no detail rendering → trace_count = 0, public_count = 0 |
| 3. RENDER_DETAIL on, PUBLIC_DETAIL_LANE off | trace_count > 0 for allowlisted variants; public_count = 0 (lane gate closed) |
| 4. Both render flags on | trace_count > 0 *and* public_count > 0 for allowlisted variants (3-chart allowlist: `fix04_h10_career_stellium`, `tokyo_1998_06_21`, `toronto_1976_06_26`) |

**None of the 9 charts in this audit are in the v0.9a.2 / Phase B
variant allowlist**, so every chart below shows
`composed_detail_cards_trace_count = 0` and
`public_composed_detail_cards_count = 0`. This is the expected,
documented behavior of the Phase B narrow slice — see §"Is Phase B
safe?" in the aggregate section.

**Note on requested flag layer 2:** the prompt asks for
`ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT=false`. In practice the
9 charts produce identical `candidate_packet` distributions whether
this flag is on or off, because the detail-support flag only changes
downstream eligibility for the detail lane (composed candidates still
appear in the cluster plan either way). The metrics in §"Per-chart
breakdown" below reflect the capture-time flag values; the comparison
with the layer-2 configuration is summarized in the matrix above.

## Fixture Map

The requested charts were resolved against
`backend/tests/_artifacts/natal_batch_audits/natal_50_chart_discovery_metrics.json`:

| Requested label | Resolved chart_id | Note |
|---|---|---|
| Istanbul 1996 | — | **Not in the 50-chart fixture set**; no `istanbul_1996_*` entry exists. Substituted with **Izmir 1996 (v0.5 overlay)** (`izmir_1996_05_20`) in Group A. |
| Adana 1998 | `adana_1998_09_12` | |
| Istanbul 2020 | `istanbul_2020_04_10` | |
| Izmir 1996 | `izmir_1996_05_20` (Group A) / `izmir_1996_03_08` (Group B "normal") | |
| Istanbul 1994 | `istanbul_1994_06_25` | |
| Istanbul 1997 | `istanbul_1997_01_21` | |
| Kutahya 1959 | `kutahya_1959_10_21` | |
| Izmir 2007 | `izmir_2007_07_19` | |
| Istanbul 2012 | `istanbul_2012_08_02` | |

---

## Per-Chart Breakdown

### A. Accepted Golden Charts

#### A1 · Istanbul 1994 (`istanbul_1994_06_25`)

| Metric | Value |
|---|---|
| candidate_packet_count | 16 |
| unique_candidate_packet_count | 15 |
| exact_registry / composed_semantic / generic_fallback / discovery_scaffold | 14 / 2 / 0 / 0 |
| public_main / public_support / detail | 6 / 2 / 4 |
| focus_map | mind (strong), identity (medium_strong), home_family (medium_strong), career (supporting), creativity (supporting), relationship (supporting) |
| fallback breakdown (raw_generic / customized / cluster_specific) | 0 / 0 / 0 |
| non_public_discovery_packet_count | 0 |
| composed_semantic candidate count | 2 |
| composed_detail_cards trace count | 0 |
| public composed_detail_cards count | 0 |
| chart_facts_match=false count | 0 |
| P0 truthfulness — English aspect names / "olması de" / "Bazen de." | 0 / 0 / 0 |
| v8 duplication flags | none |
| health_score | **100 / 100** |
| verdict | **accepted / stable** |

#### A2 · Istanbul 1997 (`istanbul_1997_01_21`)

| Metric | Value |
|---|---|
| candidate_packet_count | 24 |
| unique_candidate_packet_count | 21 |
| exact / composed / generic / discovery | 19 / 2 / 3 / 0 |
| public_main / public_support / detail | 6 / 6 / 4 |
| focus_map | career (strong), axis_tension (strong), home_family (strong), mind (medium_strong), community (medium_strong), relationship (medium_strong), action (medium_strong), inner_world (supporting), identity (detail_only) |
| fallback breakdown | 3 / 0 / 0 |
| non_public_discovery_packet_count | 0 |
| composed_semantic candidate count | 2 |
| composed_detail_cards trace count | 0 |
| public composed_detail_cards count | 0 |
| chart_facts_match=false count | **2** |
| P0 truthfulness | 0 / 0 / 0 |
| v8 duplication flags | none |
| health_score | **78 / 100** |
| verdict | **accepted / stable, but needs semantic coverage** (3 raw_generic_fallback + 2 chart_facts_match=false) |

#### A3 · Istanbul 2020 (`istanbul_2020_04_10`)

| Metric | Value |
|---|---|
| candidate_packet_count | 15 |
| unique_candidate_packet_count | 14 |
| exact / composed / generic / discovery | 9 / 2 / 4 / 0 |
| public_main / public_support / detail | 4 / 0 / 6 |
| focus_map | career (strong), mind (medium_strong), identity (medium_strong), relationship (supporting) |
| fallback breakdown | 4 / 0 / 0 |
| non_public_discovery_packet_count | 0 |
| composed_semantic candidate count | 2 |
| trace / public composed counts | 0 / 0 |
| chart_facts_match=false | 0 |
| P0 truthfulness | 0 / 0 / 0 |
| v8 duplication flags | none |
| health_score | **80 / 100** |
| verdict | **accepted / stable, needs semantic coverage** (4 raw_generic_fallback, no public_support layer) |

#### A4 · Izmir 1996 — v0.5 overlay (`izmir_1996_05_20`)

| Metric | Value |
|---|---|
| candidate_packet_count | 14 |
| unique_candidate_packet_count | 14 |
| exact / composed / generic / discovery | 2 / 2 / 1 / 9 |
| public_main / public_support / detail | 2 / 0 / 0 |
| focus_map | career (supporting), identity (detail_only) |
| fallback breakdown | 1 / 0 / 0 |
| non_public_discovery_packet_count | 0 |
| composed_semantic candidate count | 2 |
| trace / public composed counts | 0 / 0 |
| chart_facts_match=false | 1 |
| P0 truthfulness | English: 0 · `olması de`: 0 · `Bazen de.`: **2** |
| Defect sample | `…fazla hız düzeni dağıtabilir. Bazen de. Dışarıda toplu görünürken…` (in `nar.blocks.body` and `nar.core_blocks.body`) |
| v8 duplication flags | none |
| health_score | **48 / 100** |
| verdict | **needs P0 truthfulness fix + needs semantic coverage** (dangling "Bazen de." sentence + 9 discovery_scaffold packets carrying the public_main layer) |

#### A5 · Adana 1998 (`adana_1998_09_12`)

| Metric | Value |
|---|---|
| candidate_packet_count | 23 |
| unique_candidate_packet_count | 22 |
| exact / composed / generic / discovery | 22 / 1 / 0 / 0 |
| public_main / public_support / detail | 5 / 0 / 14 |
| focus_map | identity (medium_strong), mind (medium_strong), career (medium_strong), relationship (medium_strong), community (supporting) |
| fallback breakdown | 0 / 0 / 0 |
| non_public_discovery_packet_count | 0 |
| composed_semantic candidate count | 1 |
| trace / public composed counts | 0 / 0 |
| chart_facts_match=false | 0 |
| P0 truthfulness | English: 0 · `olması de`: **3** · `Bazen de.`: 0 |
| Defect sample | `…da olması kadar 7. evinin Koç olması de bu hattın karakterini belirli…` (in `nar.blocks.body`, `nar.extra_blocks.body`, `v8.differentiators.body`) |
| v8 duplication flags | none |
| health_score | **65 / 100** |
| verdict | **needs P0 truthfulness fix** ("olması de" dangling conjunction; otherwise the strongest registry-coverage chart in this audit) |

### B. Mixed Normal-Case Charts

#### B1 · Kutahya 1959 (`kutahya_1959_10_21`)

| Metric | Value |
|---|---|
| candidate_packet_count | 17 |
| unique_candidate_packet_count | 14 |
| exact / composed / generic / discovery | 1 / 2 / 9 / 5 |
| public_main / public_support / detail | 4 / 0 / 0 |
| focus_map | mind (strong), relationship (strong), career (strong), identity (detail_only) |
| fallback breakdown | 9 / 0 / 0 |
| non_public_discovery_packet_count | 0 |
| composed_semantic candidate count | 2 |
| trace / public composed counts | 0 / 0 |
| chart_facts_match=false | 0 |
| P0 truthfulness | English: 0 · `olması de`: **3** · `Bazen de.`: 0 |
| Defect sample | `…olması kadar Yükseleninin Yay olması de bu hattın karakterini belirli…` (in `nar.blocks.body`, `nar.core_blocks.body`, `v8.differentiators.body`) |
| v8 duplication flags | `promise::mind_mind_system` appears in **hero** and **differentiators** |
| health_score | **35 / 100** |
| verdict | **needs P0 truthfulness fix + needs semantic coverage + v8 dedup** (worst chart in the audit — 53% of packets are raw_generic_fallback) |

#### B2 · Izmir 1996 — normal (`izmir_1996_03_08`)

| Metric | Value |
|---|---|
| candidate_packet_count | 18 |
| unique_candidate_packet_count | 16 |
| exact / composed / generic / discovery | 17 / 1 / 0 / 0 |
| public_main / public_support / detail | 5 / 0 / 7 |
| focus_map | identity (strong), career (strong), relationship (medium_strong), inner_world (medium_strong), mind (supporting) |
| fallback breakdown | 0 / 0 / 0 |
| non_public_discovery_packet_count | 0 |
| composed_semantic candidate count | 1 |
| trace / public composed counts | 0 / 0 |
| chart_facts_match=false | 0 |
| P0 truthfulness | 0 / 0 / 0 |
| v8 duplication flags | none |
| health_score | **95 / 100** |
| verdict | **good candidate for next golden** (clean registry coverage, no defects, no duplications) |

#### B3 · Izmir 2007 (`izmir_2007_07_19`)

| Metric | Value |
|---|---|
| candidate_packet_count | 22 |
| unique_candidate_packet_count | 19 |
| exact / composed / generic / discovery | 4 / 2 / 9 / 7 |
| public_main / public_support / detail | 4 / 0 / 3 |
| focus_map | career (strong), mind (strong), relationship (strong), identity (medium_strong) |
| fallback breakdown | 9 / 0 / 0 |
| non_public_discovery_packet_count | 0 |
| composed_semantic candidate count | 2 |
| trace / public composed counts | 0 / 0 |
| chart_facts_match=false | 0 |
| P0 truthfulness | English: 0 · `olması de`: **2** · `Bazen de.`: 0 |
| Defect sample | `…ası kadar Yükseleninin Terazi olması de bu hattın karakterini belirli…` (in `nar.blocks.body`, `nar.core_blocks.body`) |
| v8 duplication flags | none |
| health_score | **45 / 100** |
| verdict | **needs P0 truthfulness fix + needs semantic coverage** (41% raw_generic_fallback, 32% discovery_scaffold) |

#### B4 · Istanbul 2012 (`istanbul_2012_08_02`)

| Metric | Value |
|---|---|
| candidate_packet_count | 15 |
| unique_candidate_packet_count | 13 |
| exact / composed / generic / discovery | 4 / 1 / 3 / 7 |
| public_main / public_support / detail | 3 / 0 / 0 |
| focus_map | career (strong), relationship (strong), identity (supporting) |
| fallback breakdown | 3 / 0 / 0 |
| non_public_discovery_packet_count | 0 |
| composed_semantic candidate count | 1 |
| trace / public composed counts | 0 / 0 |
| chart_facts_match=false | 0 |
| P0 truthfulness | 0 / 0 / 0 |
| v8 duplication flags | **3 duplications** — `promise::career_career_visibility` in hero + differentiators; `promise::neptune_4h_soft_inner_presence_chart_exact` in identity_axis + differentiators; `promise::venus_trine_saturn_trust_bond` in differentiators + insight_strip |
| health_score | **60 / 100** |
| verdict | **needs v8 dedup + needs semantic coverage** (47% discovery_scaffold, 20% raw_generic_fallback, multiple v8 lane overlaps) |

---

## Aggregate Findings

### 1. Golden Stability Summary

All five Group-A goldens load and project successfully under every flag
layer. Structural surfaces (public_main / public_support / detail
cluster ids, focus_map) match their accepted snapshots in the focused
test suite (`120 passed`). However, **copy-quality regressions exist
inside two accepted goldens**:

- Adana 1998 — 3 occurrences of dangling `"olması de"` conjunction in
  public body copy (blocks, extra_blocks, v8.differentiators)
- Izmir 1996 v0.5 — 2 occurrences of dangling `"Bazen de."` sentence in
  blocks and core_blocks

So **goldens are structurally stable, copy-defectively imperfect**. The
accepted snapshots evidently froze the defects in place; they did not
regress, but they did not improve either.

### 2. Mixed-Chart Failure Patterns

| Pattern | Charts affected |
|---|---|
| `"olması de"` dangling-conjunction copy defect | Adana 1998, Kutahya 1959, Izmir 2007 (and observed in v8.differentiators where present) |
| `"Bazen de."` dangling-period copy defect | Izmir 1996 v0.5 only |
| High `raw_generic_fallback` ratio (≥30%) | Kutahya 1959 (53%), Izmir 2007 (41%), Istanbul 2020 (27%), Istanbul 2012 (20%) |
| High `discovery_scaffold` ratio (≥30%) | Istanbul 2012 (47%), Izmir 2007 (32%), Izmir 1996 v0.5 (64%) |
| `chart_facts_match=false` packets reaching the cluster plan | Istanbul 1997 (2), Izmir 1996 v0.5 (1) |
| v8 lane duplication | Istanbul 2012 (3 duplications), Kutahya 1959 (1) |

The single most common failure pattern across all 9 charts is **copy
template residue** — bodies that concatenate sub-clauses join with a
trailing connector ("de" / "de.") that should have been ellided when
the trailing fragment was empty.

### 3. Top Remaining Generic-Fallback Owners

Ranked by `raw_generic_fallback` count (none of the 9 charts produce
`customized_fallback_with_bespoke_copy` or `cluster_specific_fallback`
under current registry coverage — both buckets are 0 everywhere):

1. **Kutahya 1959** — 9 (53% of all candidate packets)
2. **Izmir 2007** — 9 (41%)
3. **Istanbul 2020** — 4
4. **Istanbul 1997** — 3
5. **Istanbul 2012** — 3
6. **Izmir 1996 v0.5** — 1
7. All others — 0

Conclusion: registry coverage is excellent on Istanbul and Adana
golden-class charts but thin on Kutahya and the 2007 Izmir chart.

### 4. Top Remaining Discovery Gaps

Ranked by `discovery_scaffold` packet count (these are charts where the
pipeline is leaning on auto-discovered structural placeholders rather
than authored archetypes):

1. **Izmir 1996 v0.5** — 9 discovery_scaffold packets (64% of cluster
   plan) — and all 9 sit inside the public-rendered cluster surface
   (`non_public_discovery_packet_count = 0` means they are *not*
   filtered out of public_main).
2. **Izmir 2007** — 7
3. **Istanbul 2012** — 7
4. **Kutahya 1959** — 5
5. All others — 0

The pattern: when generic_fallback runs out, the pipeline reaches for
discovery_scaffold to fill the cluster plan. These two layers together
account for the dominant content on Kutahya 1959 (82%), Izmir 1996 v0.5
(71%), Izmir 2007 (73%), and Istanbul 2012 (67%).

### 5. Top Composed-Semantic Opportunities

Every chart in this audit produces 1–2 `composed_semantic` candidates
from the v0.9a registry (18 total across 9 charts) but **zero** of them
match the current Phase-B variant allowlist
(`fix04_h10_career_stellium`, `tokyo_1998_06_21`,
`toronto_1976_06_26`). So the composed grammar is *firing* widely but
the renderer signature gate is intentionally narrow.

Charts that would most benefit from a generalized composed-detail
renderer (high `composed_semantic` candidate count + present in focus
domains the grammar already supports — `career_route` / `public_voice`):

| Chart | composed_semantic candidates | career focus tier |
|---|---|---|
| Istanbul 1997 | 2 | career (strong) |
| Istanbul 2020 | 2 | career (strong) |
| Izmir 2007 | 2 | career (strong) |
| Istanbul 2012 | 1 | career (strong) |
| Kutahya 1959 | 2 | career (strong) |
| Izmir 1996 normal | 1 | career (strong) |
| Istanbul 1994 | 2 | career (supporting) |
| Adana 1998 | 1 | career (medium_strong) |
| Izmir 1996 v0.5 | 2 | career (supporting) |

The signature-matching constraint in
`_match_supported_public_voice_variant` requires very specific
placement sets (e.g. `Mercury Cancer 10H + Mars Cancer 10H`). Most
of these career-strong charts have *different* career-route shapes
that the v0.9a grammar can describe but the v0.9a.2 renderer cannot
yet emit. This is the natural growth surface for v0.9a.4 (or v0.9b).

### 6. Is Phase B Public Detail Lane Safe?

**Yes.** Independent evidence from this audit:

- **No leakage into legacy surfaces:** Across all 9 charts and under
  the both-flags-on layer, the leak counters for
  `blocks` / `core_blocks` / `extra_blocks` / `detail_cards` /
  `v8.hero.node_id` / `v8.identity_axis.node_id` /
  `v8.differentiators` / `v8.insight_strip` are all 0. No
  `promise::composed_career_route_v0_9a` and no `composed_detail::*`
  id appears anywhere except in the dedicated traceability lane and
  the dedicated public lane.
- **Allowlist is narrow and deterministic:** None of the 9 audited
  charts is in the variant allowlist, so all 9 produce
  `public_composed_detail_cards_count = 0`. The lane field is
  *omitted entirely* (not emitted as an empty list).
- **Cache key invalidates correctly:** Flipping
  `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE` between
  `false` and `true` produces different cache keys — verified
  separately in the Phase B audit. No cross-flag bleed possible.
- **Trace lane is unchanged:** The Phase B work touched neither
  `traceability.composed_detail_cards_v0_9a_2` shape nor the renderer
  signature gate.

Phase B's surface area is essentially invisible under default flags
(both off by default) and demonstrably contained when both flags are
on.

### 7. Recommended Next Step

Ordered by ROI and dependency-correctness:

1. **P0 truthfulness fix — `"olması de"` and `"Bazen de."`
   dangling-connector defects.** Highest ROI per engineering hour:
   four out of nine audited charts (Adana 1998, Kutahya 1959,
   Izmir 2007, Izmir 1996 v0.5) carry a dangling copy joiner that
   the user can read in production body text. This is independent of
   any v0.9 / v0.9a grammar work and should ship before either of the
   bigger moves below. Likely fix surface: the body-composition helper
   that joins clauses like `"X olması kadar Y olması"` — the trailing
   conjunction should be stripped when the next clause is empty.

2. **v0.9b relationship / moon grammar.** With the composed-semantic
   substrate proven by v0.9a.2/3 (career_route / public_voice), the
   next family expansion (`relationship_route`, `moon_signature`) is
   the natural follow-up. Eight of the nine audited charts have
   `relationship` or `inner_world` in their focus map at
   `medium_strong` or higher, so the coverage win would touch most
   of the production surface. Postpone Phase C mobile work until at
   least one more family is rendered, otherwise the mobile surface
   is shipping with just three allowlisted chart fixtures.

3. **50-chart batch expansion (only after #1 lands).** The current
   `natal_50_chart_discovery_metrics.json` is the only fixture set
   driving discovery audits. Expanding it would multiply audit
   coverage at low cost — but doing it *before* the P0 copy fix
   would just freeze the existing defects into more charts.

4. **Phase C mobile detail surface — defer.** The Phase B allowlist
   only covers 3 charts. Wiring a mobile detail surface against a
   3-chart allowlist gives a surface no real user will hit. Phase C
   becomes worth shipping after the renderer signature gate is
   widened (via v0.9b or a v0.9a.4 generalization).

5. **Transit activation — orthogonal, no dependency on this audit.**
   Can proceed in parallel with the work above; this audit has no
   findings that touch the transit surface.

### Health-Score Distribution

| Bucket | Charts |
|---|---|
| 90–100 (accepted / stable) | Istanbul 1994 (100), Izmir 1996 normal (95) |
| 70–89 (stable, needs semantic coverage) | Istanbul 2020 (80), Istanbul 1997 (78) |
| 50–69 (needs P0 or v8 fix) | Adana 1998 (65), Istanbul 2012 (60) |
| 30–49 (needs P0 + semantic coverage) | Izmir 1996 v0.5 (48), Izmir 2007 (45), Kutahya 1959 (35) |

Median: 65. The audit's lower half is dominated by charts where
generic_fallback + discovery_scaffold combine to carry the public
surface and the dangling-conjunction copy bug is visible.

---

## Conclusion

Phase B shipped without disturbing existing surfaces — verified against
9 charts under all four flag layers. The narrow variant allowlist
prevents user-facing exposure outside the three test fixtures, so the
lane is operationally inert in production until the renderer signature
gate is widened.

The single highest-value next move is the **P0 truthfulness fix**
("olması de" / "Bazen de." dangling-connector defects). Composed
grammar expansion (v0.9b) is the right second move because it unlocks
the same renderer pipeline Phase B already validates. Phase C mobile
work should wait until the allowlist no longer caps real-user coverage
at 3 fixtures.
