# Projection Merge Plan (Post Lazy/Full Measurement)

Date: 2026-04-24  
Scope: Natal output branches only. No code changes in this document.

## Goal
Turn heavy duplicate natal branches into **projection packs** over time, with `meaning_graph_v1_1` as canonical semantic backbone, while preserving editorial quality (profile/story depth, pacing, tone, card quality).

## Baseline (confirmed from lazy/full measurement)
Same `/interpret/ui` natal request, two variants:

- `include_full_profile=false` (lazy)
- `include_full_profile=true` (full)

Observed:

- Total latency: `1163.884 ms` (lazy) vs `1452.380 ms` (full)  
  Delta: `+288.496 ms` in full
- `public_natal_build`: `232.945 ms` (lazy) vs `469.457 ms` (full)  
  Delta: `+236.512 ms` in full
- Public payload size: `206,237 B` (lazy) vs `313,729 B` (full)  
  Delta: `+107,492 B`
- `meaning_graph_v1_1` parity: `51` nodes / `189` evidence in both modes
- Cache keys differ between lazy/full variants (no collision)
- Semantic roots for graph remain intact in lazy mode:
  - `core_story`, `core_story_ui`, `user_compact`, `personality_imprint`, `supporting_threads`, `meaning_graph_v1_1`

Conclusion from baseline: lazy/full split is working and gives a safe runway for projection migration.

---

## Branch-by-branch projection analysis

| Branch | 1) Current role | 2) Type | 3) Unique editorial/UI value | 4) Derivable from `meaning_graph_v1_1` | 5) Not yet derivable from `meaning_graph_v1_1` | 6) Migration risk | 7) Proposed future state |
|---|---|---|---|---|---|---|---|
| `profile_narrative` | Rich narrative card system (`blocks`, `core_blocks`, `extra_blocks`, `detail_cards`, `insight_modules`) assembled in public builder v3; merges profile blocks + bundles + threads + imprint detail cards. | **Hybrid** (render projection + semantic reconstruction) | High editorial depth: card family logic, core/extra emphasis, detail-block writing cadence, dedupe, narrative pacing. | Card picking by `domain/layers/node_type/projection_hints`, summary/micro from node text, chips/proof from evidence payloads. | Family-specific editorial composition, bundle narrative synthesis, v3-specific ranking/boosting behavior, nuanced TR copy shaping quality. | **High** (major profile UX regression risk if degraded). | **Convert to projection** from graph in stages; keep full editor path as fallback until parity. **Lazy-only by default** for non-profile consumers. |
| `sections_v2` | Three deterministic section cards (mind/relationship/career), currently generated as separate branch and also used to seed threads. | **Hybrid leaning projection/fallback** | Strong scaffold for deep-home/profile sections; includes `detail_blocks`, `chips`, `proof_raw`, `category_support`. | Domain-grouped top sections can be projected from graph nodes + evidence (`chips`, `proof_raw`). | Current section personalization/rhythm family selection, spine migration section remap, explicit category-support shaping in section schema. | **Medium** (home deep payload currently uses it directly). | **Merge into projection path** (derived from graph + support metadata). Keep lazy by default. **Removal candidate later** after telemetry parity. |
| `profile_v8` | Primary profile render contract (`hero`, `identity_axis`, `insight_strip`, differentiators, curated sections). Built via fragment pool across multiple branches. | **Render projection** | Stable UI contract and layout semantics; strong “top of profile” experience and visual hierarchy. | Most narrative texts/insights can come from graph node selections and evidence snippets. | Hero/social/fact synthesis (chart + social context), some differentiator/stat constructs, section choreography rules. | **High** (current primary profile entry surface). | **Keep as projection output**, but re-source progressively from graph. Keep lazy outside profile surfaces. |
| `full_map_v8` | Deep tabbed profile map (`kimlik/iliski/kariyer/golge`) for exploration of past/mechanism/shadow/potential flows. | **Render projection** | Deep exploration structure, tab semantics, mission/opening/pull-quote narrative pacing. | Layer/domain grouping in graph can seed each tab’s core meaning blocks. | Mission-step composition, tab-specific editorial transition logic, rule-driven anchors not yet represented in graph schema. | **Medium-high** | **Convert to projection** from graph + fact adapters; keep lazy by default. Potential merge with a unified deep-profile projection pack later. |
| `supporting_threads` | Thread-format meaning (`one_liner`, `paragraph`, `proof_raw`, `chips`) and currently a **direct source family** for `meaning_graph_v1_1`. | **Core semantic source (current)** + transport | Concise readable thread framing + proof line continuity used by UI and graph evidence. | Future: thread cards can be projected from graph nodes and typed evidence. | Today graph still depends on this branch as source input; removing/converting now risks semantic coverage loss. | **Very high** (semantic root break risk). | **Keep as source now**. Later: once graph source families expand and parity is proven, convert to projection and merge with sections transport.

---

## Recommended target classification (near-term)

- `supporting_threads`: **keep as source** (temporary canonical source family)
- `profile_narrative`: **convert to projection** (graph-backed), keep current builder as fallback
- `profile_v8`: **convert to projection** (graph-backed) while preserving current contract
- `full_map_v8`: **convert to projection** (graph-backed deep pack)
- `sections_v2`: **merge into projection** and make lazy; potential removal after telemetry

This keeps editorial richness while reducing semantic authority fragmentation.

---

## Migration plan (projection-first, quality-safe)

## Phase 1 — Projection contracts over graph (no consumer switch yet)
- Define projection contracts for:
  - `profile_narrative_projection_v1`
  - `profile_v8_projection_v1`
  - `full_map_v8_projection_v1`
  - `sections_v2_projection_v1`
- Add traceability fields in projection output (internal/debug): `node_id`, `evidence_id` provenance per rendered block.
- Keep current branches as primary output; generate projection shadow outputs for parity comparison only.

Exit criteria:
- Projection shadow outputs generated for >=95% of charts without runtime errors.

## Phase 2 — Parity instrumentation + editorial QA gates
- Add per-surface parity checks:
  - Coverage parity (required card/section slots filled)
  - Semantic parity (same dominant themes/layers)
  - Editorial quality checks (length, repetition, astro-jargon leakage)
- Add telemetry for branch reads/fallbacks:
  - how often mobile/profile consumes each branch
  - how often it falls back from `profile_v8` to legacy reconstruction
  - how often `sections_v2` vs `supporting_threads` are actually used

Exit criteria:
- Projection parity pass rate acceptable across profile surfaces.
- No significant editorial quality regression in QA review set.

## Phase 3 — Consumer migration by surface
- Migrate consumers in order:
  1. Profile top (lowest risk, highest structure)
  2. Profile deep (`full_map_v8`/detail surfaces)
  3. Story/slide style surfaces
  4. Home deep hooks using section/thread projection
- Keep legacy branch fallback toggles behind flags during migration window.

Exit criteria:
- Production telemetry shows projection path stable and fallback usage low.

## Phase 4 — Compute pruning (only after proven parity)
- Keep outputs but make heavy branches lazy/default-off where possible.
- Remove duplicated compute paths first, not editorial outputs.
- Candidate sequence:
  1. Stop dual semantic reconstruction in `sections_v2` + `supporting_threads`
  2. Collapse `profile_narrative` synthesis duplication (retain projection output)
  3. Reduce fragment-pool duplication once graph-backed projections are stable

Exit criteria:
- Same editorial surface quality with lower latency/payload.
- Semantic root integrity unchanged.

---

## Editorial quality guardrails (non-negotiable)

- Do not reduce to terse “signal-only” cards for profile/story surfaces.
- Preserve:
  - narrative pacing (teaser -> body -> detail)
  - contrast/shadow nuance
  - proof-grounding (`proof_raw`, `chips`, typed evidence)
  - TR copy naturalness and de-duplication quality
- Every projection migration step needs before/after editorial sample review.

---

## Risks to watch

1. **Silent flattening risk**
- Converting rich cards to generic summaries can pass schema checks but fail product quality.

2. **Source/projection inversion risk**
- Removing `supporting_threads` too early breaks current graph source coverage.

3. **Adapter drift risk**
- Mobile adapters currently reconstruct from multiple branches; projection migration must reduce, not increase, fallback complexity.

4. **False dedupe risk**
- Repeated meaning in different rhetorical forms can be useful variation, not waste.

---

## Final recommendation

Adopt a **graph-first, projection-rich** architecture:

- One semantic source of truth: `meaning_graph_v1_1` (and its successors).
- Multiple high-quality render projections for profile/deep/story surfaces.
- Keep editorial richness, prune duplicated compute, and retire legacy paths only after telemetry-backed parity.

