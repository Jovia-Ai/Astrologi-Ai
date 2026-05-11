# Meaning Graph v1

## Purpose

`meaning_graph_v1` is the first canonical semantic abstraction layer for natal meaning output.

It sits:

- above existing backend meaning producers (`core_story_ui`, `user_compact`, `personality_imprint`, `supporting_threads`)
- below UI-specific render packs (`profile_v8`, `full_map_v8`, page-level adapters)

This layer is additive only in v1. Legacy payload branches are preserved.

## Canonical Layer Taxonomy

Each `MeaningNode` must use exactly one primary layer:

- `recognition`: "this is what is true/visible about you"
- `cause`: "what has historically shaped this pattern"
- `mechanism`: "how the pattern operates"
- `effect`: "how this pattern is experienced/expressed"
- `shadow`: "risk/blind-spot expression"
- `potential`: "constructive growth expression"

## Canonical Domain Taxonomy

v1 standard domains:

- `identity`
- `relationships`
- `career`
- `mind`
- `emotional`
- `inner_world`
- `life_direction`
- `general`

Domain normalization rule:

- known aliases are normalized into one of the canonical domains
- unknown domain labels map to `general`

## MeaningNode Schema

`MeaningNode` (v1):

- `node_id: str` deterministic ID (`mgv1_node_*`)
- `layer: str` one of layer taxonomy
- `domain: str` one of domain taxonomy
- `source_family: str` (`core_story_ui`, `user_compact`, `personality_imprint`, `supporting_threads`)
- `source_path: str` public-path style origin (example: `public.user_compact.domains[0]`)
- `title: str` short semantic label
- `summary: str` user-readable meaning line
- `confidence: float` 0..1 normalized confidence proxy
- `rank: int` deterministic order index
- `tags: list[str]` optional semantic tags
- `evidence_ids: list[str]` references to evidence rows
- `mapping_status: str` (`mapped` or `partial`)

## MeaningEvidence Schema

`MeaningEvidence` (v1):

- `evidence_id: str` deterministic ID (`mgv1_evd_*`)
- `node_id: str` parent node reference
- `source_family: str`
- `source_path: str`
- `kind: str` (`text` | `tag`)
- `snippet: str` compact source snippet
- `weight: float` 0..1 contribution weight
- `mapping_status: str` (`mapped` | `partial`)

## Mapping Rules (Natal v1)

v1 supports these source families.

### 1) `core_story_ui` -> recognition node

- source: `public.core_story_ui`
- preferred text: `text`, fallback `headline`
- output:
  - 1 `recognition` node
  - optional tag evidence from `drivers[]`

### 2) `user_compact` -> mechanism/effect nodes

- source:
  - `public.user_compact.domains[]`
  - `public.user_compact.micro_insights[]`
- output:
  - per domain entry: 1 `mechanism` node
  - per micro insight: 1 `effect` node
- domain:
  - `domain` field normalized via canonical domain mapping

### 3) `personality_imprint` -> effect/shadow/potential nodes

- source:
  - `public.personality_imprint.entries[]`
  - `public.personality_imprint.support_entries[]`
  - `public.personality_imprint.extra_entries[]`
- output:
  - from `trait`/`aura`: `effect`
  - from `shadow`: `shadow`
  - from `gift`: `potential`
- each mapped text adds evidence with explicit source path

### 4) `supporting_threads` -> cause nodes

- source: `public.supporting_threads[]`
- preferred text: `paragraph`, fallback `body`, fallback `one_liner`
- output:
  - per thread: 1 `cause` node

### Incomplete Mapping Policy

When a source family is present but only partial mapping is possible:

- emit node/evidence with `mapping_status: partial`
- do not infer missing meaning via opaque heuristics

## UI Surface Rules

`meaning_graph_v1` is semantic-first. Surface packs remain render-first.

### Home

- consume top-ranked `effect` + `potential` nodes
- prefer concise summaries

### Profile Top

- consume `recognition` + `effect` + selected `mechanism`
- keep to low card count, high confidence

### Profile Deep

- consume full node set grouped by domain/layer
- use `shadow` and `cause` explicitly

### Story Studio

- sequence by layer arc:
  `recognition -> cause -> mechanism -> effect -> shadow -> potential`

### Explainability

- use `evidence_ids` to show source trace (`source_family`, `source_path`, `snippet`)

## Source-of-Truth Rules

- Target state: `meaning_graph` is the canonical semantic source.
- Current state (v1 rollout): canonical intent exists, but coverage is partial and some artifacts still do not include `public.meaning_graph`.
- `profile_v8`, `full_map_v8`, `profile_narrative`, `sections_v2`, and `supporting_threads` remain render-oriented or mixed semantic/render packs.
- UI semantic reconstruction from multiple branches is still active in mobile and should migrate toward `meaning_graph`.

v1 compatibility rule:

- existing output branches remain unchanged
- `public.meaning_graph` is additive

### Runtime Precedence (explicit, migration-safe)

When reading semantic meaning in clients/services:

1. If `public.meaning_graph.version == "meaning_graph_v1"` and `nodes` is non-empty: read this first.
2. If absent/empty: fallback to legacy semantic branches in this order:
   - `public.core_story_ui`
   - `public.user_compact`
   - `public.supporting_threads`
   - `public.sections_v2`
   - `public.profile_narrative.profile_public`
3. Treat `profile_v8` and `full_map_v8` as render projections, not primary semantic authority.

## Migration Phases

### Phase 0 (this change)

- add `public.meaning_graph` scaffold
- map 4 natal source families deterministically

### Phase 1

- add ranking policy per surface (`home`, `profile_top`, `profile_deep`)
- align mobile adapters to read `meaning_graph` first

### Phase 2

- migrate render packs to become thin projections from `meaning_graph`
- reduce semantic duplication across `profile_v8`/`profile_narrative`/thread adapters

### Phase 3

- extend graph builder coverage to transit contracts
- add canonical cross-natal/transit linking

## Post-Implementation Gap Review (Critical)

This section patches missed items from the initial draft.

### 1) Outputs Not Yet Classified (artifact-grounded)

From `docs/system/_generated_outputs/fresh_natal_interpret_ui_1996-12-28_07-10_istanbul.json`, these public outputs exist but were not fully classified/mapped in v1:

- `core_story` (semantic long-form, unmapped)
- `upper_meaning` (semantic guidance, unmapped)
- `sections_v2` (semantic cards, unmapped in graph)
- `profile_narrative.profile_public` (`blocks/core_blocks/detail_cards/extra_blocks`, unmapped)
- `profile_v8` (UI-facing semantic projection, unmapped by graph rules)
- `full_map_v8` (UI-facing semantic projection, unmapped by graph rules)
- `narrative_v2` (contract/explainability policy, unmapped)
- `data_quality_summary` (quality/meta, unmapped)
- `meta_summary` (meta, unmapped)
- `meaning_weighting` (score/meta, unmapped)
- `narrative_anchor` (meta semantic anchor, unmapped)
- `natal_graph_compact` (raw structural evidence, unmapped)
- `flags` (runtime mode/meta, unmapped)
- `theme_scores` (currently nullable, unmapped)

### 2) Meaning Layers Implied But Not Formalized

The first draft defined 6 layers, but artifacts imply additional semantic classes that are not formalized in v1 schema:

- `guidance`: actionable "what to do/how to hold this" language (`upper_meaning`, CTA-like lines)
- `proof`: editorial trace/proof snippets (`proof_raw`, evidence-heavy blocks)
- `quality`: uncertainty/confidence/coverage semantics (`data_quality_summary`, `meta_summary`)
- `arbitration`: selection/ranking rationale (`narrative_v2.section_priority_matrix`, `fallback_rules`)

These are explicitly deferred and must be formalized in v1.1+ instead of being silently mixed into existing layers.

### 3) Places With Structure But No Mapping Definition

Initial draft described structure but did not define deterministic mapping rules for:

- `core_story` when `core_story_ui` is missing
- `upper_meaning` dictionary shape (`enabled/mode/reasons/text/content`)
- `sections_v2` vs `supporting_threads` overlap handling
- `profile_narrative.profile_public` block families and dedupe behavior
- `profile_v8` and `full_map_v8` projection-to-node traceability
- `narrative_v2` explainability fields to evidence linkage

Resolution: these remain unmapped in v1 and should be tracked as explicit mapping backlog, not implicit behavior.

### 4) Artifact vs Conclusion Inconsistencies

- Generated output artifact currently does not include `public.meaning_graph`:
  - `docs/system/_generated_outputs/fresh_natal_interpret_ui_1996-12-28_07-10_istanbul.json`
- Runtime builder does produce `meaning_graph` in current code path (`backend/app/natal/public_builder.py`), so generated artifacts are stale relative to code.
- Initial draft claimed `MeaningEvidence.kind` could be `text|tag`; current builder emits only `text`.
- Initial draft claimed partial mapping rows should be emitted; current builder mostly marks mapped nodes and reports gaps via `meta.missing_source_families`.
- `personality_imprint` may be absent in valid natal payloads; source-family coverage is therefore conditional, not guaranteed.

### 5) Source-of-Truth Ambiguities (explicitly unresolved)

- Ambiguity: whether semantic authority is payload branch (`core_story_ui` etc.) or graph branch (`meaning_graph`) during rollout.
- Ambiguity: whether `profile_v8` is canonical meaning or presentation projection.
- Ambiguity: whether arbitration policy (`narrative_v2`) is semantic truth or render policy.

Current decision:

- semantic authority target = `meaning_graph`
- rollout fallback authority = legacy branches (ordered precedence above)
- render packs are non-canonical for semantics

### 6) Duplicate Meaning Producers (same idea, multiple systems)

Observed duplication patterns:

- identity thesis:
  - `core_story_ui.text`
  - `core_story`
  - `profile_v8.identity_axis`
  - `profile_narrative.profile_public.blocks`
- trait/shadow/potential semantics:
  - `personality_imprint.entries/support_entries/extra_entries`
  - `profile_narrative.detail_cards`
  - `sections_v2`/`supporting_threads` detail blocks
- micro insights / short cards:
  - `user_compact.micro_insights`
  - `profile_v8.insight_strip`
  - `profile_narrative.core_blocks/extra_blocks`

This duplication is intentional legacy coexistence today, but it is a correctness risk if mappings drift.

### 7) UI Reconstruction Hotspots (not direct graph consumption yet)

Mobile currently reconstructs meaning from multiple payload branches instead of consuming a single semantic layer:

- `mobile/lib/app/profile/profile_v8_adapter.dart`
  - merges `profile_v8`, `profile_narrative.profile_public`, `sections_v2`, `supporting_threads`, `user_compact`, `core_story_ui`
  - performs local dedupe, fallback text selection, and heuristic assembly
- `mobile/lib/app/tabs/profile_page.dart`
  - payload-shape checks and conditional branching on multiple sources
- `mobile/lib/app/timing/narrative_dtos.dart`
  - transit DTO parsing uses multiple key-path fallbacks and conditional omission behavior

Conclusion: migration to `meaning_graph` should reduce adapter-side reconstruction logic and semantic drift.

### 8) Mapping Patch Set (next incremental, deterministic)

These rules close the weakest mapping gaps without broad rewrites.

- `M1 core_story fallback`
- when `public.core_story_ui.text` is empty and `public.core_story` is non-empty:
- create one `recognition` node from `core_story` with `source_family="core_story"` and `source_path="public.core_story"`.

- `M2 upper_meaning guidance mapping`
- when `public.upper_meaning.enabled == true`:
- map `public.upper_meaning.text` (fallback `content`) into one `potential` node.
- map `reasons[]` into evidence rows.
- when disabled: do not emit semantic node, keep only meta.

- `M3 sections_v2 structural mapping`
- per `public.sections_v2[i]`:
- `body` -> `mechanism` node.
- `micro` -> `effect` node (if non-empty).
- `detail_blocks[]` and `proof_raw` -> evidence rows only.

- `M4 profile_narrative block mapping`
- from `public.profile_narrative.profile_public`:
- `core_blocks[]` -> `mechanism` nodes.
- `detail_cards[]` -> `effect` nodes.
- `extra_blocks[]` -> `potential` nodes.
- keep original block IDs in `source_path` for stable traceability.

- `M5 v8 projection trace links`
- do not map `profile_v8` / `full_map_v8` as source semantic nodes.
- add optional `projection_refs` in `meaning_graph.meta` linking v8 card IDs to node IDs once upstream mappings exist.

- `M6 narrative_v2 explainability bridge`
- include `narrative_v2.contract_version` in `meaning_graph.meta.contract_version`.
- map `fallback_rules` and `section_priority_matrix` as explainability metadata (not semantic nodes).

### 9) Confidence Labels For Conclusions

- Proven:
- mobile reconstructs meaning from multi-branch payloads (`profile_v8_adapter.dart`, `profile_page.dart`).
- generated natal artifact under `docs/system/_generated_outputs` is stale and lacks `public.meaning_graph`.
- duplication exists across `core_story_ui` / `profile_narrative` / `profile_v8` / `sections_v2`.

- Medium-confidence (needs targeted verification snapshots):
- exact one-to-one projection from `profile_narrative` block types to layers for all charts.
- stability of `personality_imprint` availability across all production modes.

- Unknown:
- transit empty-card behavior root cause is not resolved in this natal-first v1 doc and remains out of scope here.
