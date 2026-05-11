# Semantic Deduplication & Compute Pruning Audit (Post-calibration)

Date: 2026-04-24

## Scope & method
- Fresh natal public payload generated from `POST /interpret/ui` equivalent route call with:
  - `birth_date=1996-12-28`
  - `birth_time=07:10`
  - `birth_place=Istanbul, TR`
  - `locale=tr`
  - `summary_only=false`
- No code changes in this audit.
- Ground truth artifacts used:
  - `/tmp/semantic_pruning_fresh_payload.json`
  - `/tmp/semantic_pruning_stats.json`
  - `/tmp/semantic_pruning_debug_timing.json`
- Overlap metric is **exact normalized text overlap** against `public.meaning_graph_v1_1` node summaries + text evidence; this undercounts paraphrased semantic overlap.

## Snapshot
- `meaning_graph_v1_1`: `51` nodes, `189` evidence, source families:
  - `core_story_ui: 1`
  - `user_compact: 5`
  - `personality_imprint: 42`
  - `supporting_threads: 3`
- Endpoint timing (debug sample):
  - `total_ms: 444.63`
  - `chart_payload_preparation: 230.529 ms`
  - `public_natal_build: 201.377 ms`
- Payload size concentration (selected branches):
  - `profile_narrative`: 65,530 bytes (40.1%)
  - `supporting_threads`: 23,905 bytes (14.6%)
  - `sections_v2`: 22,048 bytes (13.5%)
  - `full_map_v8`: 16,680 bytes (10.2%)

---

## Branch classification matrix

| Branch | Classification tags | 1) Semantic role | 2) UI consumers | 3) Overlap with `meaning_graph_v1_1` | 4) Unique value not captured by graph | 5) Compute/cost risk (inferable) | 6) Safe action |
|---|---|---|---|---|---|---|---|
| `core_story` | duplicate semantic channel, fallback-only | Single long-form synthesis from core-story plan + upper-meaning gate. | Mobile Home/Profile/Chart Lab summary fallback chain. | Exact overlap `0.0%` (`1` text item). | Dynamic prose shaped by `core_story_plan`, `expression_profile`, upper-meaning gating. | Low-medium compute; tiny payload (`811 B`). | **keep**; merge into graph projection later (do not remove now). |
| `core_story_ui` | core semantic source, duplicate semantic channel | Short profile-facing story (`headline/text/drivers`) used as stable semantic anchor. | Mobile Home, Profile adapter, backend Home orchestrator. | Exact overlap `7.7%` (`1/13`); plus direct graph source family. | Driver list + concise headline contract not fully represented as projection pack yet. | Low payload (`849 B`), high dependency. | **keep** (canonical input for graph and UI). |
| `user_compact` | core semantic source, possible lazy candidate | Domain summaries + micro insights compact semantic digest. | Profile adapter talents fallback; backend home source snapshot; graph builder. | Exact overlap `23.1%` (`15/65`); graph source family. | Domain grouping, compact shape, tone-profile/meta hints. | Medium (built in finalize stage), payload `8,384 B`. | **keep**; later merge into graph projections; optional lazy for consumers that do not read compact. |
| `personality_imprint` | core semantic source, duplicate semantic channel | Trait/shadow/gift + support entry library for identity semantics. | Profile page, Story Studio, People Aura, graph builder. | Exact overlap `35.4%` (`62/175`); graph source family dominant (`42` nodes). | Bundle/support-entry structure (`support_keys`, bundles, render shape) still not first-class in graph projections. | Medium-high compute and payload (`13,542 B`). | **keep** (critical semantic source). |
| `profile_v8` | render projection, duplicate semantic channel, possible lazy candidate | UI-ready profile pack (hero, insight strip, editorial sections). | Profile page via `ProfileV8Adapter` preferred path. | Exact overlap `1.1%` (`1/93`). | Layout-ready contract and section-level UX composition. | Medium compute, payload `7,096 B`. | **keep but make lazy** for non-profile surfaces. |
| `full_map_v8` | render projection, duplicate semantic channel, possible lazy candidate | Deep tabbed map (`kimlik/iliski/kariyer/golge`) for deep profile exploration. | Profile adapter fallback thread synthesis path. | Exact overlap `0.9%` (`1/109`). | Tab/mission/past/shadow/potential editorial organization. | High payload (`16,680 B`). | **keep but make lazy**; merge into graph projections later. |
| `profile_narrative` | duplicate semantic channel, render projection, possible lazy candidate | Rich card system (`blocks/core/extra/detail/insight_modules`) combining multiple sources. | Profile page + adapter, backend Home deep story hooks. | Exact overlap `2.6%` (`8/305`) but high semantic reconstruction from same roots. | Card-level editoriality, detail blocks, UX-ready modules. | **Very high** payload (`65,530 B`, largest) + synthesis complexity. | **keep but make lazy**; target graph-projection convergence later. |
| `sections_v2` | duplicate semantic channel, fallback-only, possible lazy candidate, possible removal candidate later | Section cards (mind/relations/career) with subtitle/body/detail/proof. | Profile adapter currently checks `sections_v2` first; backend Home deep sections. | Exact overlap `0.0%` (`0/106`), not graph source. | Section-oriented structural packaging + proof fields + category support. | High payload (`22,048 B`) + separate builder pass. | **keep but make lazy**; candidate for merge/removal only after telemetry proves redundancy. |
| `supporting_threads` | core semantic source, duplicate semantic channel | Thread-form narrative derived from sections and used as graph semantic source. | Profile adapter fallback, Profile page, graph builder, Home deep contexts. | Exact overlap `2.6%` (`3/114`); graph source family (`3` nodes). | `one_liner/paragraph/proof_raw` thread contract used directly in UI and graph. | High payload (`23,905 B`) but key source. | **keep**; consolidate with `sections_v2` via single projection path before any removal. |
| `narrative_v2` | debug/support metadata, render projection helper, possible lazy candidate | Selector metadata (`selected_bundles`, policy, candidate_count) used for card/bundle projection. | Profile adapter bundle teasers; profile public v3 extra-card synthesis. | Exact overlap `0.0%` (`0/46`). | Bundle-selection rationale and IDs for editorial packs. | Low payload (`1,685 B`), low-medium compute. | **keep but make lazy** where bundle UI not needed. |
| `upper_meaning` | fallback-only, debug/support metadata | Gated contribution message + gate diagnostics (`mode/reasons/thresholds`). | Profile adapter fallback quote input, Home summary fallback, core-story gate path. | Exact overlap `0.0%` (`0/3`). | Gate diagnostics and threshold context absent in graph nodes. | Low payload (`441 B`), low compute. | **keep**; later expose as graph projection/meta, not removal. |
| `meta_summary` | debug/support metadata | Pressure/support/uncertainty compact meta. | Profile adapter fallback text/theme hints; backend gating/quality paths. | `0.0%` text overlap (numeric/meta). | Scalar health/uncertainty signals. | Very low payload (`96 B`). | **keep**. |
| `meaning_weighting` | debug/support metadata | Theme arbitration (`primary_theme`, `secondary_theme`, `upper_meaning_allowed`). | Profile adapter fallback talents/insights; backend narrative gate logic. | Exact overlap `0.0%`. | Theme weights and gating flags not modeled as graph projection today. | Very low payload (`198 B`). | **keep**. |
| `data_quality_summary` | debug/support metadata, possible lazy candidate, possible removal candidate later | Summary of fallback/missing-signal/uncertainty state. | No direct mobile/runtime consumer found in current scan. | Exact overlap `0.0%`. | Operational quality signal only. | Very low payload (`261 B`). | **debug-only candidate**; potential removal after telemetry confirms zero external reads. |
| `natal_graph_compact` | debug/support metadata, possible lazy candidate | Compact raw astro scaffolding (`house_rulers/dominant_loops/importance`). | Profile adapter chart-ruler fallback path + profile experiments. | Exact overlap `0.0%`. | Raw astro-reference scaffolding not represented in graph layer. | Low payload (`1,948 B`), compute already amortized upstream. | **keep but make lazy** once profile contracts stop fallbacking to it. |

---

## Deduplication findings (post-calibration)

### Useful variants (keep)
- `core_story_ui`, `user_compact`, `personality_imprint`, `supporting_threads`.
- Reason: these are current semantic inputs to `meaning_graph_v1_1` and also power active UI experiences.

### True duplicate semantic channels (convergence targets)
- `profile_narrative` vs (`personality_imprint` + `supporting_threads` + `narrative_v2`) in profile detail composition.
- `sections_v2` vs `supporting_threads` (same origin family; two parallel transport shapes).
- `core_story` vs `core_story_ui` for summary surfaces.

### Render packs with high value (do not remove)
- `profile_v8`, `full_map_v8`, `profile_narrative` carry UX structure and editorial pacing that the graph does not yet project.

---

## Compute pruning opportunities (safe order)

1. **Lazy-first candidates (highest ROI)**
- `profile_narrative`
- `sections_v2`
- `supporting_threads` (only after unifying with section transport)
- `full_map_v8`
- `profile_v8`

2. **Metadata lazy/debug gating**
- `data_quality_summary`
- `natal_graph_compact`
- `narrative_v2` on surfaces not using bundle teasers.

3. **Do not prune yet**
- `core_story_ui`, `user_compact`, `personality_imprint`, `supporting_threads` (current graph roots)

---

## Telemetry/tests required before any pruning

### Telemetry
- Field-read telemetry by client version and surface:
  - profile: `profile_v8`, `full_map_v8`, `profile_narrative`, `sections_v2`, `supporting_threads`
  - home: `core_story_ui`, `core_story`, `upper_meaning`
- Fallback-hit counters in mobile adapters:
  - how often adapter falls from `profile_v8` to legacy reconstruction
  - how often `sections_v2` path is used vs `supporting_threads`
- Payload + render telemetry:
  - per-branch bytes
  - decode time
  - first-render time by screen

### Tests/guards
- Contract tests for each surface with branch toggles (lazy on/off):
  - Profile renders unchanged if `profile_narrative` is omitted but `profile_v8` exists
  - Thread rendering unchanged when `sections_v2` is omitted but `supporting_threads` exists (and vice versa)
- Golden output tests for identity summary chain:
  - `core_story_ui.text -> core_story -> fallback`
- Graph parity tests:
  - semantic source families still produce required node/evidence counts when projection branches are lazy.

---

## Evidence index (code paths)

### Backend producers and shaping
- `backend/app/api/routes/natal_interpretation.py:2044-2230` (`sections_v2`, `supporting_threads`, `profile_narrative`, `personality_imprint`, `meaning_weighting`, `meta_summary`, `upper_meaning`)
- `backend/app/api/routes/natal_interpretation.py:2456-2550` (`core_story`, `core_story_ui`, `user_compact`, `data_quality`)
- `backend/app/natal/public_builder.py:49-142` (public emission including `profile_v8`, `full_map_v8`, `meaning_graph`, `meaning_graph_v1_1`)
- `backend/app/natal/profile_v8_payload_builder.py:416-443` (v8/full-map projection built from existing branches)
- `backend/app/natal/supporting_threads_builder.py:2012-2154` (`sections_v2` and `supporting_threads` shared origin)

### Graph source coverage
- `backend/app/meaning/meaning_graph_v1_1_builder.py:192-206` and extraction functions for:
  - `core_story_ui`
  - `user_compact`
  - `personality_imprint`
  - `supporting_threads`

### Mobile/backend consumers
- `mobile/lib/app/profile/profile_v8_adapter.dart:223-267, 248-263, 277-287, 728-733, 1931-1937, 2891-2929, 2956-2964`
- `mobile/lib/app/tabs/profile_page.dart:2500-2535, 2537-2566, 2598-2606, 2891-2929, 3145-3177`
- `mobile/lib/app/tabs/home_page.dart:2788-2809`
- `mobile/lib/app/tabs/story_studio_page.dart:1404-1419`
- `mobile/lib/app/people/people_aura_repository.dart:127-143`
- `backend/app/services/performance/home_orchestrator.py:341-359, 407-459`

