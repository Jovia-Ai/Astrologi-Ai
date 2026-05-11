# SHOU Reasoning Ownership Audit

## 1. Executive Summary

**Overall status:** `yellow` leaning `red` on semantic ownership.

- Canonical building blocks now exist in the repo: `CanonicalNatalStateV1`, `promise_hierarchy`, `contradiction_hierarchy`, `chart_spine`, `canonical_period_spine`, `LifeChapter`, `PeriodVoicePolicy`.
- But runtime meaning ownership is still fragmented across **event selection**, **voice policy**, **renderer fallbacks**, **daily humanizer**, and **public adapters**.
- Period is still materially **event-first**: `selection.py` chooses narrative ownership from ranked events, then `public_builder.py` reconstructs period meaning from selected event cards.
- `canonical_period_spine` is a useful canonical bridge, but today it is mostly an **event-to-hook matcher**, not the primary owner of period reasoning.
- `active_life_chapter` is real in detector output, but in period rendering it is still **debug/no-op only**.
- `PeriodVoicePolicy` is not voice-only; it already selects meaning-like fields such as `meaning_intent`, `growth_edge`, `what_it_builds`, and `reason_line_seed`.
- `astrolog_narrative_engine.py` is still a major semantic owner. It does not only render; it chooses and extends meaning when upstream payloads are thin.
- Natal public/profile/projection surfaces still rely on **rendered-copy-derived meaning graphs** (`meaning_graph_v1`, `meaning_graph_v1_1`) rather than a fully canonical astro structure.
- Daily is still closer to **best event/card condensation** than to a true “what changed today?” engine.
- Broad PR-D is still early. A scoped Tier-1 PR-D can be planned, but a small `PeriodSemanticFocusResolver` facade should come first.

**Most important blocker:** there is no single runtime layer that owns **selected meaning** between `LifeChapter / canonical period signals` and the renderer. That missing owner is why period copy is improved but still often policy-led or renderer-invented.

**Recommended next PR:** a minimal `PeriodSemanticFocusResolver` facade, introduced before PR-D and used as the semantic owner for Tier-1 chapter + period meaning.

## 2. Current Semantic Authority Map

| Surface | Current owner | Canonical? | Legacy? | Risk | Notes |
|---|---|---:|---:|---|---|
| natal public payload | `backend/app/natal/public_builder.py::build_public_natal_view` | partial | yes | risky | Aggregates `core_story`, `upper_meaning_selected`, `user_compact`, `personality_imprint`, `supporting_threads`, `profile_narrative`, `sections_v2`, `profile_v8`, `full_map_v8`; not a single canonical owner. |
| profile_narrative | `backend/app/natal/narrative/profile_narrative_engine.py::build_profile_narrative` + signature/legacy engines | partial | yes | risky | Engine rollout/migration wrapper still supports legacy; meaning comes from profile engines, not canonical natal state directly. |
| sections_v2 | `backend/app/natal/supporting_threads_builder.py::build_sections_v2` | partial | yes | risky | Uses `natal_graph`, rulers, loops, section families, and migration mode; still an independent authored semantic pack. |
| profile_v8 / full_map_v8 | `backend/app/natal/profile_v8_payload_builder.py::build_profile_and_full_map_v8_payload` | no | yes | risky | Selects and reshapes fragments from rendered/profile artifacts into new surfaces; acts as a projection engine. |
| meaning_graph / meaning_graph_v1 | `backend/app/meaning/meaning_graph_builder.py::build_meaning_graph_v1` | no | yes | risky | Nodes are extracted from `core_story_ui`, `user_compact`, `personality_imprint`, `supporting_threads`; graph is built from rendered text families. |
| meaning_graph_v1_1 | `backend/app/meaning/meaning_graph_v1_1_builder.py::build_meaning_graph_v1_1` | no | yes | risky | Same pattern, even more explicit: it classifies layers from already-rendered copy and source-family cues. |
| projection outputs | `backend/app/meaning/projection_shadow_v1_builder.py::{build_profile_narrative_projection_v1,build_profile_v8_projection_v1}` | no | yes | risky | Shadow projections derive from `meaning_graph_v1_1`, which is already downstream from rendered copy. |
| period narrative | `backend/app/transit/narrative/astrolog_narrative_engine.py::build_period_story` | partial | yes | risky | Combines selected events, story track, voice policy, canonical spine prefix, and local render fallbacks. |
| period_core | `backend/app/transit/narrative/deep_archetype_engine.py::build_period_core` | partial | yes | risky | Takes selected event cards, computes period copy, root causes, story tracks, then asks renderer to rewrite ownership again. |
| event cards | `backend/app/transit/narrative/deep_archetype_engine.py::build_event_card` | no | yes | risky | Event card already blends combined meaning, natal promise, hybrid context, section injections, insight pack, copy quality, rewrite layer. |
| daily_synthesis | `backend/app/transit/narrative/daily_synthesis.py::build_daily_synthesis` | partial | yes | risky | Synthesizes daily prose from dominant domain/mode + signal candidates + bridge logic; not a pure renderer. |
| daily humanizer | `backend/app/transit/narrative/daily_humanizer_tr.py::{generate_daily_from_event,humanize_event_card_tr}` | no | yes | risky | Independent daily meaning engine built from house packs, aspect modes, narrative signature, scene activation, natal resonance, period bridge. |
| daily event cards | `backend/app/transit/narrative/daily_selection.py::select_daily_and_period_event_cards` | no | yes | risky | Score-heavy selector that also humanizes cards and uses previews in scoring context. |
| transit calendar / markers | `backend/app/transit/calendar_builder.py` + `backend/app/transit/interpret/interpretation_engine_v1.py::enrich_markers_with_lens` | partial | yes | partial | Marker generation is structural, but `score_by_intent` and lens enrichment give markers semantic weight beyond raw timing. |
| best-times / opportunity-like outputs | `backend/app/transit/lens/best_times.py::best_times_from_calendar_payload` | no | yes | partial | Purely marker-score ranking by intent; no life chapter or semantic focus owner. |

## 3. Event-First Leftovers

| File | Function | Behavior | Risk | Keep/Migrate | Recommendation |
|---|---|---|---|---|---|
| `backend/app/transit/narrative/selection.py` | `select_event_ids` | Story ownership is chosen from ranked events using salience, story score, chapter role, coverage anchors, fill score. | high | migrate | This is the clearest old-system leftover. Period ownership should move upstream to `LifeChapter` + semantic focus; event ranking should become evidence selection. |
| `backend/app/transit/present/public_builder.py` | `build_public_response` | Builds `event_cards`, then builds `canonical_period_spine` from those cards, then calls `build_period_core` with selected cards. | high | migrate | `canonical_period_spine` should not be downstream of event cards long-term. Public builder should become adapter-only. |
| `backend/app/transit/narrative/deep_archetype_engine.py` | `build_period_core` | Rebuilds period meaning from selected events, domains, dominant house, period copy, root causes, story tracks. | high | migrate | Keep temporarily as assembly layer, but period owner should be semantic-focus payload, not selected event pack. |
| `backend/app/transit/narrative/deep_archetype_engine.py` | `build_event_card` | Each event card gets its own hybrid/natal/copy stack and then becomes period input. | medium | keep for now | Event cards can survive as evidence surfaces, but they should stop feeding back as period semantic owners. |
| `backend/app/transit/narrative/daily_selection.py` | `select_daily_and_period_event_cards` | Daily and period cards are selected through score weights, readability, memorability, confidence, delta salience, surfaceability. | high | migrate | Daily should stop choosing meaning from scores. Keep ranking only for evidence choice once `TodayStoryCandidate` has a stable owner. |
| `backend/app/transit/narrative/daily_selection.py` | `compute_today_score` / `compute_delta_salience_score` | Today-ness is approximated by score features around events. | medium | partial | Acceptable as proto `today_delta_signal`, but it is still event-first and not yet chapter-aware. |
| `backend/app/transit/narrative/today_story_candidate.py` | `build_today_story_candidate` | Chooses `exceptional_event`, `period_triggered_today`, `period_continuation`, `daily_flavor`, `quiet_day`. | medium | migrate | Still candidate-first. Needs to become “today delta under active period/life chapter,” not “which event/card wins today.” |
| `backend/app/transit/lens/best_times.py` | `best_times_from_calendar_payload` | Picks best day from `markers[].score_by_intent`. | medium | keep for now | Fine as timing/ranking utility, but should not be treated as semantic owner. |
| `backend/app/transit/calendar_builder.py` | marker pipeline + `enrich_markers_with_lens` | Calendar meaning is marker-first, then lens-enriched, then intent-scored. | medium | partial | Acceptable for calendar UX, but should remain proof/timing infrastructure, not narrative authority. |

## 4. Meaning Ownership Leaks

| File | Function | Leak | Why it matters | Recommendation |
|---|---|---|---|---|
| `backend/app/api/routes/transits.py` | `_inject_canonical_natal_activation_context` | Mutates already-built `period_core`, `daily_selection`, `daily_synthesis` by prefixing canonical promise/context after the fact. | Canonical meaning is being patched in after downstream meaning already exists. | Move canonical promise/chapter ownership earlier; route should orchestrate, not reinterpret. |
| `backend/app/transit/narrative/period_voice_policy.py` | `build_period_voice_policy` | Selects `meaning_intent`, `psychological_process`, `higher_meaning`, `growth_edge`, `what_it_builds`, `reason_line_seed`. | Voice policy is acting like a partial semantic resolver. | Split semantic selection into explicit resolver output; keep policy as register/voice policy. |
| `backend/app/transit/narrative/manifestation_context_policy.py` | context builders | House/life-scene selection can become meaning selection when upstream focus is thin. | Scene translation starts owning interpretation. | Keep scene translation, but require explicit `selected_meaning` / `primary_domain` upstream. |
| `backend/app/transit/narrative/astrolog_narrative_engine.py` | `build_period_story` + `_render_policy_*` helpers | Renderer generates new semantic material from sparse policy/track inputs. | Violates “render slots must not create new meaning.” | Reduce renderer to composition from canonical slots after resolver lands. |
| `backend/app/transit/narrative/daily_humanizer_tr.py` | `generate_daily_from_event` / `humanize_event_card_tr` | Humanizer adds scene activation, natal resonance, period bridge, story editorialization. | Daily humanizer is a standalone interpretation layer. | Long-term replace with canonical daily renderer over `TodayStoryCandidate`. |
| `backend/app/natal/public_builder.py` | `build_public_natal_view` | Public builder emits multiple narrative branches and meaning graphs from them. | Public adapter is acting like multi-author semantic merger. | Gradually demote to adapter-only after canonical natal authority path is explicit. |
| `backend/app/meaning/meaning_graph_builder.py` | `build_meaning_graph_v1` | Meaning graph is extracted from rendered public text families. | The graph cannot be a canonical reasoning substrate if it is text-derived. | Freeze as projection/support artifact; do not promote as upstream authority. |
| `backend/app/meaning/meaning_graph_v1_1_builder.py` | `build_meaning_graph_v1_1` | Layer/node inference is built from text cues and public source families. | This converts rendered copy into a supposed semantic backbone. | Keep for projection/explainability only, not reasoning ownership. |
| `backend/app/meaning/projection_shadow_v1_builder.py` | projection builders | Projection builder performs independent semantic selection from graph nodes. | Projection becomes its own meaning engine. | Accept as shadow/projection surface only; do not let it back-propagate into canonical owners. |
| `backend/app/natal/profile_v8_payload_builder.py` | fragment pool and selectors | Merges profile fragments into hero/identity/mission/etc. and changes emphasis/ordering. | UI payload builder becomes a semantic editor. | Keep as surface-specific projection only; do not treat as canonical. |

## 5. Natal Downstream Readiness

| Area | Rating | Notes |
|---|---|---|
| `CanonicalNatalStateV1` | partial | `backend/app/astro_os/natal/state_builder.py::build_canonical_natal_state_v1` exists and is structured, but it is still fed by `LegacyNatalReasoningBundle`. |
| promise hierarchy | ready | `backend/app/astro_os/natal/promise_hierarchy.py` distinguishes `core`, `major`, `supporting`, `minor`. This is one of the stronger canonical pieces. |
| contradiction hierarchy | partial | `backend/app/astro_os/natal/contradiction_hierarchy.py` is structured, but still legacy-fed and threshold-driven. |
| chart spine | partial | `backend/app/astro_os/natal/chart_spine_reducer.py` produces useful slots, but it reduces legacy selector candidates rather than starting from raw chart logic. |
| activation hooks | partial | `backend/app/transit/narrative/canonical_natal_activation.py` exposes hook matching, but via event-to-hook overlap rather than deep promise consumption. |
| meaning graph builder | risky | `meaning_graph_v1` / `v1_1` are not canonical natal meaning graphs; they are downstream rendered-copy graphs. |
| legacy adapter | risky | Canonical natal state still absorbs legacy narrative bundle structures. |
| public builder usage | risky | `build_public_natal_view` still treats many legacy/rendered branches as co-owners. |
| profile renderers | partial | Good surface engines exist, but they are still semantic owners rather than pure renderers. |
| dispositor / ruler / house logic usage | partial | Present in natal/profile builders and daily humanizer, but not yet consistently centralized as canonical reasoning inputs for period/daily. |

**Answers**

- **Is natal meaning selected once and reused?** No. It is selected multiple times across canonical natal, public builder, profile engines, meaning graph builders, projection builders, and period adapters.
- **Are core promises distinguishable from secondary promises?** Yes, in `promise_hierarchy.py`.
- **Are contradictions used to influence selection, or only rendered?** Mostly rendered/downstream; there is no strong evidence they are central runtime selectors for period/daily reasoning.
- **Are activation hooks available to period/daily?** Yes, through `canonical_natal_activation.py`, but as shallow hook matching rather than full semantic ownership.
- **Does period consume natal promise deeply or only theme labels?** Mostly theme labels / matched hooks / promise prefixing; not deep canonical promise reasoning.
- **Does public/mobile natal still rely on legacy semantic authorities?** Yes.
- **What should be cleaned now vs later?**
  - **Now:** stop promoting `meaning_graph_v1_1` or public/profile projections as upstream authority.
  - **Later:** replace legacy-fed canonical natal sources and reduce public/profile builders to adapters.

## 6. Period Proof Surface Readiness

**Current pipeline in code**

`transits.py`
-> `selection.py::select_event_ids`
-> `public_builder.py::build_public_response`
-> `deep_archetype_engine.py::build_period_core`
-> `astrolog_narrative_engine.py::build_period_story`
-> route-level canonical prefix injection / daily synthesis / today story candidate

**Assessment**

- **Does period narrative start from selected events or from canonical reasoning?**  
  It still starts from **selected events**. `canonical_period_spine` is helpful, but it is built from selected cards in `public_builder.py`.

- **Does `active_life_chapter` actually influence meaning, or only appear in debug?**  
  Only debug/no-op in `PeriodStoryContext` and renderer debug payload.

- **Does `PeriodVoicePolicy` determine voice only, or also select meaning?**  
  It also selects meaning. `meaning_intent`, `growth_edge`, `what_it_builds`, `reason_line_seed`, and `higher_meaning` are semantic ownership fields.

- **Is `ManifestationContext` used as scene translation only, or does it become selected meaning?**  
  Intended as scene translation, but it can become quasi-meaning when upstream semantic focus is thin.

- **Does valence/intensity affect phrasing without becoming simplistic good/bad?**  
  Mostly yes in the newer layer, but older artifacts still show classifier-like simplification. The bigger problem is not polarity; it is missing ownership.

- **Does renderer invent meaning when semantic focus is thin?**  
  Yes. `astrolog_narrative_engine.py` still composes meaning-bearing copy when upstream inputs are incomplete.

- **What is missing before PR-D can safely enable LifeChapter priority?**
  - one explicit semantic owner between `LifeChapter` / `canonical_period_spine` and renderer
  - `active_life_chapter` consumption in period meaning, not just debug
  - renderer reduction from semantic owner to composition layer
  - clean contract for `selected_meaning`, `meaning_family`, `primary_domain`, `suppressed_meanings`, `evidence`

**Component ratings**

| Component | Rating | Notes |
|---|---|---|
| `canonical_period_spine` | partial | Good canonical bridge, but currently derived from selected event cards. |
| `period_voice_policy` | partial | Strong and useful, but semantically overloaded. |
| `manifestation_context_policy` | partial | Useful scene layer, but must stop filling meaning gaps. |
| `aspect_valence_mapper` / valence-intensity usage | partial | Better than old good/bad tone, but still downstream of event-first ownership. |
| `astrolog_narrative_engine` | risky | Closest renderer to v4 target, but still invents meaning. |
| `active_life_chapter` handoff | partial | Contract exists, quality improved, runtime consumption absent. |
| `renderer_handoff` / `suppressed_surface_readings` | partial | Good prep work in detector output, not yet period owner at runtime. |

## 7. LifeChapter PR-D Readiness

**Current implementation status**

- **Can become active now:** `saturn_return`, `nodal_return`, `nodal_activation`
- **Candidate-only:** `jupiter_return`, `eclipse_activation`, `major_transit_chapter`, `solar_return_theme`, `structural_natal_chapter`, others
- **Signal registry:** `docs/system/life_chapter_signal_registry.md`
- **Contract:** `backend/app/transit/narrative/life_chapter_contract.py`
- **Detector:** `backend/app/transit/narrative/life_chapter_detector.py`

**Case assessment**

- **Aries 3rd + South Node overlap:** `ready_or_nearly_ready`  
  The handoff is dense enough that a renderer would not need to invent the core chapter meaning.

- **Cancer 8th Saturn return:** `ready_or_nearly_ready`, but thinner than Aries 3rd  
  Shared burden / trust / intimacy boundary / shared-vs-private contrast is now present, but still less structurally anchored than the Aries case.

- **Nodal activation / nodal return:** `partial but acceptable for Tier-1 scope`  
  Good enough for a conservative flag-gated rollout, assuming meaning selection is stabilized upstream.

- **Structural T-square:** correctly **excluded from PR-D v1**  
  Candidate semantics exist, but it is not first-class owner-ready. Keeping it out of PR-D v1 is correct.

- **Feature flag readiness:** missing  
  The codebase has planning/docs for `LIFE_CHAPTER_PRIORITY_ENABLED = false`, but no live integration path yet.

**Exact gaps blocking PR-D**

1. `active_life_chapter` is not period owner yet; renderer only sees it in debug.
2. No explicit `PeriodSemanticFocusResolver` owns “why this meaning, not that one.”
3. `period_voice_policy` and renderer still jointly invent meaning when period inputs are thin.
4. `canonical_period_spine` is still event-downstream.
5. Daily stack is not ready to follow chapter priority safely.

**PR-D readiness:** `no-go` for current broad runtime, but **go-behind-flag-only after a minimal resolver facade** for scoped Tier-1 v1 (`saturn_return`, `nodal_return`, `nodal_activation` only).

## 8. PeriodSemanticFocusResolver Gap

**Is any existing function already acting like a resolver?** Yes, but scattered.

| Existing location | Resolver-like responsibility |
|---|---|
| `backend/app/transit/narrative/canonical_natal_activation.py::build_canonical_period_spine` | picks matched hook / theme / prefix from events + canonical natal hook graph |
| `backend/app/transit/narrative/life_chapter_detector.py` enrichment functions | chapter-specific `selected_meaning`, `semantic_focus`, `renderer_handoff`, suppressed readings |
| `backend/app/transit/narrative/period_voice_policy.py::build_period_voice_policy` | meaning intent, rhetorical frame, growth edge, what it builds |
| `backend/app/transit/narrative/manifestation_context_policy.py` | chooses primary house / life scene / contextual surface |
| `backend/app/transit/narrative/astrolog_narrative_engine.py` | backfills missing meaning in final prose |

**Current problem:** there is no single place that says:

- this is the selected meaning
- this is why it won
- these are the suppressed alternatives
- these are the scene anchors
- renderer should not reinterpret beyond this

**Minimum safe facade for v1**

Inputs:

- `canonical_natal_state`
- `active_life_chapter | None`
- `canonical_period_spine`
- selected event evidence ids / event pack
- period signal families from current `period_voice_policy`
- manifestation context candidates

Outputs:

- `selected_meaning`
- `meaning_family`
- `primary_domain`
- `secondary_domains`
- `why_this_meaning[]`
- `evidence[]`
- `suppressed_meanings[]`
- `confidence`
- `scene_translation_request`
- `voice_register_hints`

**Migration path**

1. Extract semantic ownership from `period_voice_policy` into resolver output.
2. Feed resolver output into `astrolog_narrative_engine` as required input.
3. Keep `manifestation_context_policy` as scene translator only.
4. Keep renderer as composer over fixed semantic slots.
5. After that, wire `active_life_chapter` into PR-D behind flag.

## 9. Daily Readiness

**Current state**

- `daily_selection.py` still selects the best event/card.
- `today_story_candidate.py` still chooses between event-based candidate modes.
- `daily_synthesis.py` is a planner/composer over daily card signals.
- `daily_humanizer_tr.py` is still a meaning engine.

**Answers**

- **Is daily still selecting the best event/card?** Yes.
- **Is daily reading the active period/life chapter?** Not as a semantic owner.
- **Does daily answer “what is different today?”** Only partially, through score-based today/delta heuristics.
- **Is there a `today_delta_signal` or equivalent?** Not as a clean owner. `compute_delta_salience_score(...)` is only a scoring approximation.
- **Does `daily_humanizer` invent meaning?** Yes.
- **Does daily duplicate period mechanism?** Yes, especially in bridge/editorial lines.
- **What must wait until period/life chapter/semantic focus are stable?**
  - daily semantic owner
  - real today-delta reasoning
  - chapter-aware daily renderer
  - daily render slot cleanup

**Clean now**

- stop using humanized preview copy inside selection scoring as narrative authority
- keep daily as evidence + delta scoring only where possible

**Wait until later**

- full daily semantic rewrite
- `TodayStoryCandidate` redesign
- today-delta engine

## 10. Voice / Renderer Risks

**Files generating risky or legacy phrasing**

- `backend/app/transit/narrative/astrolog_narrative_engine.py`
  - generates patterns close to the banned family: `Buradaki eşik`, `Asıl ayrım`, `sende X kuruyor`, `tarafında`, `aynı anda söz istiyor`, `asıl omurga`
- `backend/app/transit/narrative/daily_synthesis.py`
  - template-heavy lines like `Bu tema bugün...`, `Bugünün ağırlığı...`, `Bu tema bugün iki ayrı ihtiyacı...`
- `backend/app/transit/narrative/daily_humanizer_tr.py`
  - heavy editorial/interpreting lines around scene activation, natal resonance, and period bridge
- `backend/app/engine/composite_engine.py`
  - still emits older `Bu yapı...` copy
- `backend/app/narrative/style_packs/tr_v26.py`
  - still contains direct `Bu yapı...` style templates

**Observed old-system smells in artifacts**

- From `backend/tests/_artifacts/transit_narrative_1996-12-28_07-10_istanbul_2026-03-04.json`:
  - `Bu süreç yükselen hattında daha sakin bir ayar kuruyor.`  
    Owner is renderer/policy stack, not explicit semantic focus. This is generic and still v3-ish.
  - `Bu süreç 5. Ev temasını daha olgun bir çizgiye taşıyor.`  
    Better than old score labels, but still house-label generic rather than chart-owned.

- From `docs/voice/handcrafted_period_validation_v4_final.md` target reference:
  - `Sen uzun yıllardır kendini inşa eden birisin...`
  - `Bu yapı bitmeyen bir proje, ama bu ara bir faz tamamlanıyor.`
  - `T-square ... üç parçalı bir basınç sistemi var.`
  These are chart-architecture-led and are still denser than current runtime period prose.

**Which renderer functions are closest to v4 target?**

- `backend/app/transit/narrative/astrolog_narrative_engine.py::build_period_story`
- its policy-aware sections around `period_opening`, `big_picture`, `mechanism`, `growth_edge`, `what_it_builds`

These are the closest, but still not safe as pure renderers because they compensate for missing upstream meaning.

**Which outputs likely need PR-4.1 composer pass?**

- period opening rotation and anti-scaffold cleanup in `astrolog_narrative_engine.py`
- daily synthesis phrasing discipline in `daily_synthesis.py`
- daily humanizer de-editorialization in `daily_humanizer_tr.py`

## 11. Recommended PR Order

1. **Minimal `PeriodSemanticFocusResolver` facade**
   - smallest missing owner
   - should gather current scattered logic instead of adding another semantic branch
2. **PR-4.1 period output review / composer pass**
   - remove remaining v3 scaffolds from `astrolog_narrative_engine.py`
   - keep renderer chapter-ready, not chapter-owning
3. **PR-D v1 feature-flagged Tier-1 integration**
   - `saturn_return`
   - `nodal_return`
   - `nodal_activation`
   - `LIFE_CHAPTER_PRIORITY_ENABLED = false` by default
4. **Daily today-delta owner pass**
   - separate “today difference” from “best event”
5. **Structural chapter track (`structural_natal_chapter`)**
   - explicit PR-C.4 style work
   - keep excluded from PR-D v1
6. **Natal public authority cleanup**
   - stop treating `meaning_graph_v1_1` and projection packs as canonical authority
7. **Projection and profile renderer cleanup**
   - reduce fragment/projection builders to surface renderers
8. **Timing/Opportunity engine**
   - after period/daily owners stabilize

## 12. Appendix: File Map

| File | Current ownership / role |
|---|---|
| `backend/app/api/routes/transits.py` | orchestration layer that still mutates semantic output via canonical-prefix injection and wires daily/period/today story surfaces |
| `backend/app/transit/narrative/selection.py` | event-first narrative ownership selector |
| `backend/app/transit/present/public_builder.py` | public adapter that still rebuilds period meaning from event cards |
| `backend/app/transit/narrative/deep_archetype_engine.py` | event card builder + period core builder + story track assembler |
| `backend/app/transit/narrative/canonical_natal_activation.py` | canonical natal activation hook matcher and current `canonical_period_spine` owner |
| `backend/app/transit/narrative/period_voice_policy.py` | voice plus partial meaning selector |
| `backend/app/transit/narrative/manifestation_context_policy.py` | scene / house / manifestation translator |
| `backend/app/transit/narrative/astrolog_narrative_engine.py` | current period renderer and major semantic backfill owner |
| `backend/app/transit/narrative/life_chapter_contract.py` | current LifeChapter contract |
| `backend/app/transit/narrative/life_chapter_detector.py` | current LifeChapter detector, candidate extractor, Tier-1 emitter, semantic handoff prep |
| `backend/app/transit/narrative/daily_selection.py` | score-heavy daily/period event card selector |
| `backend/app/transit/narrative/today_story_candidate.py` | today candidate chooser, still event/trigger oriented |
| `backend/app/transit/narrative/daily_synthesis.py` | daily planner/composer over domain/mode/signal pack |
| `backend/app/transit/narrative/daily_humanizer_tr.py` | daily interpretation/humanization layer |
| `backend/app/transit/calendar_builder.py` | calendar/marker builder with lens enrichment and intent score wiring |
| `backend/app/transit/lens/best_times.py` | marker-score ranking utility |
| `backend/app/astro_os/natal/state_builder.py` | canonical natal state builder, legacy-fed |
| `backend/app/astro_os/natal/promise_hierarchy.py` | strongest current canonical natal meaning hierarchy |
| `backend/app/astro_os/natal/contradiction_hierarchy.py` | contradiction structure, still legacy-fed |
| `backend/app/astro_os/natal/chart_spine_reducer.py` | chart spine slot reducer from legacy selector output |
| `backend/app/natal/public_builder.py` | natal public semantic merger |
| `backend/app/natal/narrative/profile_narrative_engine.py` | profile narrative engine wrapper and migration selector |
| `backend/app/natal/supporting_threads_builder.py` | `sections_v2` and supporting threads authored semantic surfaces |
| `backend/app/natal/profile_v8_payload_builder.py` | fragment selector / surface-specific semantic projection |
| `backend/app/meaning/meaning_graph_builder.py` | text-derived meaning graph v1 |
| `backend/app/meaning/meaning_graph_v1_1_builder.py` | text-derived meaning graph v1.1 |
| `backend/app/meaning/projection_shadow_v1_builder.py` | projection builders over meaning graph nodes |
