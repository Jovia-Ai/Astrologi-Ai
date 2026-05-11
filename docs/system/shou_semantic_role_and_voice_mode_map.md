# SHOU Semantic Role & Voice Mode Map

Date: 2026-04-24  
Scope: current backend natal outputs + SHOU Voice Spec alignment (no code changes)

## 1) Extraction First: What Already Exists In Backend Outputs

This map starts from live payload structures, not target architecture.

### 1.1 Confirmed output branches in `/interpret/ui` public payload
- `core_story_ui`
- `user_compact`
- `personality_imprint`
- `supporting_threads`
- `profile_narrative`
- `sections_v2`
- `profile_v8`
- `full_map_v8`
- `meaning_graph`
- `meaning_graph_v1_1`
- `profile_narrative_projection_v1`
- `profile_v8_projection_v1`
- `upper_meaning`
- `meaning_weighting`
- `meta_summary`
- `narrative_anchor`
- `data_quality_summary`
- `natal_graph_compact`

### 1.2 Backend-derived semantic category seeds (existing categories)
- `core_story_ui`: `headline`, `text`, `drivers[]`
- `user_compact`: `domains[].summary`, `domains[].highlights[]`, `micro_insights[]`, `tone_profile.voice_profile_v2`
- `personality_imprint`: `trait`, `drive`, `shadow`, `gift`, `support_keys`, `tags`
- `supporting_threads`: `title`, `one_liner`, `paragraph`, `body`, `detail_blocks`, `proof_raw`, `evidence`, `category_support`
- `sections_v2`: `title`, `subtitle`, `body`, `detail_blocks`, `proof_raw`, `evidence`
- `profile_narrative.profile_public.blocks`: `headline`, `teaser`, `subtitle`, `body`, `micro`, `chips`, `astro_sources`
- `profile_v8`: sectioned render packs (`identity_axis`, `first_impression`, `defense`, `mind`, `intimacy`, `mission_preview`, etc.)
- `full_map_v8` domain packs: `opening_point`, `mechanism`, `past_fragments`, `shadow_fragments`, `potentials`, `mission`, `pull_quote`
- `meaning_graph_v1_1`: `nodes[]` + `evidence[]` with `layers`, `node_type`, `source_family`, `projection_hints`

### 1.3 Cross-fixture evidence (8 natal fixtures)
- `core_story_ui` present: `8/8`
- `supporting_threads` present: `8/8`
- `profile_narrative` present: `8/8`
- `meaning_graph_v1_1` source families observed: `core_story_ui`, `user_compact`, `personality_imprint`, `supporting_threads`
- `full_map_v8` role fields present in all domains/fixtures: `opening_point`, `mechanism`, `past_fragments`, `shadow_fragments`, `potentials`, `mission`, `pull_quote`
- `proof_raw` coverage:
  - `supporting_threads`: `24/24`
  - `sections_v2`: `24/24`
  - `profile_v8` dict sections: `0/96` (missing projection continuity)

## 2) Semantic Role + Voice Mode Classification Map

| status | semantic role name | what it means | current backend sources | related meaning_graph layers | intended voice mode | intended UI surfaces | should be | examples (backend / spec) |
|---|---|---|---|---|---|---|---|---|
| confirmed_existing | Core Hook | First high-salience recognition line | `public.core_story_ui.headline`, `profile_v8.identity_axis.headline`, `profile_narrative.blocks[].headline` | mostly `recognition`, `effect` | `effect_hook` | Home teaser, Profile top, Story entry | source + projection | Backend: `Ritmini koruduğunda yön duygun güçleniyor.` / Spec: contrast opening |
| confirmed_existing | Mechanism Narrative | “How it works” process description | `core_story_ui.text`, `supporting_threads.body`, `full_map_v8.*.mechanism`, `profile_v8.mind.body` | `mechanism` | `mechanism_voice` | Profile deep, Story slides | source + projection | Backend: “Söylemeden önce…” style flow in thread bodies |
| confirmed_existing | Shadow Narrative | Tension/risk side without pathology | `personality_imprint.entries[].shadow`, `supporting_threads.body`, `full_map_v8.*.shadow_fragments`, `profile_v8.defense` | `shadow` | `shadow_safe` | Profile deep, Explainability, Story | source + projection | Backend: shadow fragments and defense copy |
| confirmed_existing | Potential Narrative | Growth/opening side | `full_map_v8.*.potentials`, `profile_v8.mission_preview.growth`, some `user_compact.highlights` | `potential` | `potential_voice` | Profile deep, Story close, Home deep | source + projection | Backend: “potentials” blocks in full_map_v8 |
| emerging_existing | Cause / Past Layer | Origin/past conditioning context | `full_map_v8.*.past_fragments`, `profile_v8.past_teasers`, thread past hints | sparse `cause` | `cause_voice` | Profile deep, Story mid-slides | source + projection | Backend has `past_fragments`; `meaning_graph_v1_1` cause exists but low share |
| emerging_existing | Effect / First Impression | Outside perception layer | `profile_v8.first_impression`, `first_felt`, `profile_narrative` first cards | mostly `effect` | `effect_voice` | Profile top + deep | source + projection | Backend first-impression sections exist, but not canonicalized as explicit effect object |
| confirmed_existing | Raw Proof Anchor | Astro reference chip-level proof | `supporting_threads[].proof_raw`, `sections_v2[].proof_raw`, `meaning_graph_v1_1.evidence[].structured_payload.proof_raw` | evidence across all layers | `proof_raw_voice` | Profile deep, Detail flow, Explainability | source | Backend: `Satürn · 3. ev · Koç` |
| emerging_existing | Evidence Graph / Trace | Traceable reasoning from text to evidence | `meaning_graph_v1_1.nodes/evidence`, projection `trace.node_id/evidence_ids`, `category_support` | all | `explainability_voice` | Explainability, internal QA, projection audit | source | Node/evidence links are deterministic and present |
| confirmed_existing | Voice Axes Profile | Persona-level tone calibration knobs | `user_compact.tone_profile.voice_profile_v2` | N/A (meta) | `voice_profile_mode` | Profile deep personalization, render policy | source | `direct_vs_reflective`, `warm_vs_restrained`, etc. |
| emerging_existing | Pattern Label Surrogate | Human-rememberable theme naming | `supporting_threads[].title`, `profile_narrative.headline`, `full_map_v8.pull_quote.headline` | mixed (`effect/mechanism/shadow`) | `pattern_naming_mode` | Profile top/deep, Story | projection | Role exists implicitly as titles, not formal `pattern_name` |
| emerging_existing | Share Line Surrogate | Quotable short line for social/share | `teaser`, `micro`, `insight_modules[].share_text` | usually `recognition/effect/potential` | `share_line_mode` | Home teaser, share card, push | projection | No canonical `share_line` key; distributed surrogates |
| emerging_existing | Rationale Surrogate | “Why this, not that” comparative explanation | `category_support.contradiction_signature`, internal narrative debug fields | weakly linked | `rationale_mode` | Explainability panel | source | Present in internal/debug channels; not stable public role |
| emerging_existing | Context Surrogate | Scene/time/frame cues around meaning | chips, domain labels, `narrative_anchor.domain`, range/date in home/transit | cross-layer | `context_mode` | Home, calendar, explainability | source + projection | Exists as fragments, not explicit context object in natal public |
| emerging_existing | Caution Surrogate | Action-warning layer separate from shadow | partially implicit in shadow lines and defense text | mostly shadow-adjacent | `caution_mode` | Home alerts, story final caution, calendar | source | No dedicated caution field in natal public |
| confirmed_existing | Canonical Semantic Node | Shared semantic backbone abstraction | `public.meaning_graph_v1_1.nodes[]` | explicit layer vectors | `layered_semantic_mode` | Home/Profile projection inputs, Explainability | source | Nodes carry `layers`, `primary_layer`, `source_family` |
| confirmed_existing | Render Narrative Pack | Editorial long-form card composition | `profile_narrative.profile_public`, `sections_v2`, `profile_v8`, `full_map_v8` | mixed multi-layer | `editorial_pack_mode` | Profile top/deep, detail flow | projection | Strongly used by current UI adapters |
| missing_needed | Explicit `pattern_name` | Stable named pattern token (not just headline) | none in natal public | should attach to dominant layer set | `pattern_name_mode` | Profile top, Story retention, share | source | Voice spec defines `pattern_name` as primary role |
| missing_needed | Canonical `share_line` | Single canonical quotable line field | none in natal public | typically `effect/potential/recognition` | `share_line_mode` | Home teaser, share, push | source | Spec standardizes `share_line` naming |
| missing_needed | `proof_line` (human bridge) | Humanized explanation line tied to proof | none | layer-linked support | `proof_line_mode` | Profile deep, explainability card | source | Voice spec: `proof_raw` + `proof_line` pair |
| missing_needed | `proof_orb` | Orb precision for proof chip confidence | none in natal public | evidence meta | `proof_precision_mode` | Detail flow, explainability | source | SHOU contract v3 includes `proof_orb` |
| missing_needed | `emotional_intent` | Single intent label driving tone + UI accent | none | cross-layer selector | `intent_driver_mode` | Home/profile card chrome, story end-state | source | Contract v3 defines 5-label intent driver |
| missing_needed | `tone_accent` | Intent-to-visual/accent binding | none | N/A | `accent_driver_mode` | UI accent/chip/render emphasis | source + UI | Contract v3 uses intent → accent mapping |
| missing_needed | `why_now` + `why_now_active` | Temporal activation sentence + visibility flag | none in natal public | context + current horizon | `temporal_activation_mode` | Home, calendar, event detail | source | Contract v3 requires human-first `why_now` |
| missing_needed | Typed `detail_blocks.kind` | Layer-explicit block typing (`mechanism/cause/shadow/potential`) | current `detail_blocks` are string arrays | all narrative layers | `slide_projection_mode` | Story/detail flow projection | source + projection | Contract v3 slide projection expects typed detail kinds |
| later | Synastry role harmonization | Align pair-signature roles with same role map | present in synastry domain, not natal public | separate graph branch | `pair_voice_mode` | Relationship/synastry surfaces | source | Voice spec maps `PAIR_SIGNATURE` to pattern/share roles |
| later | Transit role harmonization | Apply same role map to transit event/period outputs | transit has separate contracts | temporal layers | `transit_role_mode` | Home calendar/event surfaces | source | Needed for full-stack role parity, not blocking natal now |

## 3) Surface-Level Strength / Gap Summary

### Home
- Strong now: hook-like summaries, short highlights, domain-level compact meaning.
- Weak now: no canonical `share_line`, no `why_now`, no explicit caution role.

### Profile Top
- Strong now: identity axis + first impression + concise insights.
- Weak now: pattern naming and proof formatting are implicit/inconsistent.

### Profile Deep
- Strong now: rich long-form narrative + thread proof anchors + deep packs.
- Weak now: role typing is distributed (same meaning expressed with different field conventions).

### Story / Detail Flow
- Strong now: abundant `detail_blocks`.
- Weak now: blocks are not layer-typed, so projection must infer structure heuristically.

### Explainability
- Strong now: graph evidence + trace IDs.
- Weak now: rationale/context/caution roles are not explicit public contracts.

## 4) Ownership Rule (Current Truth vs Target)

- **Source (canonical semantic truth)**: `meaning_graph_v1_1` + structured evidence + tone profile.
- **Projection (rendered editorial packs)**: `profile_narrative`, `sections_v2`, `profile_v8`, `full_map_v8`, projection shadow outputs.
- **UI-only**: visual treatment details (accent rendering, card choreography, slide layout choreography).

Current drift is mainly from roles that are present as prose conventions but missing as explicit contract fields (`pattern_name`, `share_line`, `proof_line`, `why_now`, `emotional_intent`, `tone_accent`, typed `detail_blocks.kind`).
