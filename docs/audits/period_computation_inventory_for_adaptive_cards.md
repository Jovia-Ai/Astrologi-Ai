# Period Computation Inventory For Adaptive Cards

## TL;DR

- The current period stack already computes enough meaning and evidence to support adaptive cards without inventing a new semantic authority.
- The safest period-side inputs are not old `blocks[]` or score-only surfaces. They are `semantic_focus`, `chapter_priority`, `canonical_period_spine`, `natal_activation_context`, `featured_events` plus event-linked context, and the current renderer’s internal `composer_plan`.
- `period_reading_v1` is the current public period surface and should remain the main proof surface. Future adaptive cards should sit under/alongside it, not replace it.
- `period_voice_policy` and `manifestation_context` are useful framing layers, but they are not sufficient alone for strong cards in non-LifeChapter cases.
- The old route-level `blocks[]` surface (`core_theme`, `daily_energy`, `event_list_preview`) is legacy UI assembly. It should not power `period_signal_lines_v1`.
- The safest next step is not “implement cards now from whatever exists.” It is first shaping a narrow `PeriodCardContext / PeriodEvidenceContext` that consumes the current semantic period pipeline and the recommended natal context projection.

## 1. Current Period Runtime Pipeline Map

The current transit period pipeline is already layered. Adaptive cards need to plug into the right layer, not shortcut across it.

### Runtime chain

Raw transit events  
→ route builds core response and detector inputs in `backend/app/api/routes/transits.py`  
→ event scoring / selection in `backend/app/transit/narrative/selection.py`  
→ selected event cards enriched with `derived_context`, `chapter_role`, `story_score`, and related metadata  
→ `build_period_core(...)` in `backend/app/transit/narrative/deep_archetype_engine.py`  
→ `resolve_period_semantic_focus(...)` in `backend/app/transit/narrative/period_semantic_focus.py`  
→ `chapter_priority` gate in `deep_archetype_engine.py`  
→ `build_period_story(...)` in `backend/app/transit/narrative/astrolog_narrative_engine.py`  
→ `composer_plan`  
→ `period_reading_v1`  
→ legacy shadow fields  
→ daily/calendar/best-times side surfaces

### Key runtime handoff points

| Stage | Main file/function | What happens |
|---|---|---|
| Route wiring | `backend/app/api/routes/transits.py` | Builds core transit response, attaches canonical natal state, detects active life chapter, builds public payload, then derives daily/period side payloads |
| Active chapter detection | `detect_active_life_chapter(...)` in `backend/app/transit/narrative/life_chapter_detector.py` | Emits Tier-1 `active_life_chapter` when policy gates pass |
| Canonical period/natal bridge | `build_transit_natal_activation_context(...)` and `build_canonical_period_spine(...)` in `backend/app/transit/narrative/canonical_natal_activation.py` | Connects period events to canonical natal activation hooks |
| Period event selection | `select_event_ids(...)` in `backend/app/transit/narrative/selection.py` | Chooses public-allowed period events, computes hybrid/natal evidence, chapter role, story score |
| Daily selection | `select_daily_and_period_event_cards(...)` and `build_daily_trigger_selection(...)` in `backend/app/transit/narrative/daily_selection.py` | Selects daily cards, support cards, and daily trigger structure |
| Public period-core assembly | `build_period_core(...)` in `backend/app/transit/narrative/deep_archetype_engine.py` | Builds `period_core`, semantic focus, chapter priority, story tracks, and renderer input |
| Semantic focus resolution | `resolve_period_semantic_focus(...)` in `backend/app/transit/narrative/period_semantic_focus.py` | Resolves owner meaning from life chapter, canonical spine, policy, then events |
| Policy framing | `build_period_voice_policy(...)` in `backend/app/transit/narrative/period_voice_policy.py` | Computes meaning intent, rhetorical frame, valence/intensity, manifestation context |
| Lived-scene mapping | `build_manifestation_context(...)` in `backend/app/transit/narrative/manifestation_context_policy.py` | Maps house/domain signal into lived scene strings |
| Final period prose | `build_period_story(...)` in `backend/app/transit/narrative/astrolog_narrative_engine.py` | Produces `composer_plan`, `period_reading_v1`, and legacy shadows |
| Public normalization | `build_public_response(...)` in `backend/app/transit/present/public_builder.py` | Preserves/normalizes `period_core`, teaser/version/lock flags, and canonical period spine |
| Calendar side | `backend/app/transit/calendar_builder.py` | Computes day markers, heat, `label_pack`, `active_theme_ids` |
| Timing side | `best_times_from_calendar_payload(...)` in `backend/app/transit/lens/best_times.py` | Builds intent-scored windows from calendar marker scores |

### Where daily / calendar / best-times branch away

- `daily_synthesis`, `daily_event_cards`, `daily_selection`, and `today_story_candidate` are derived after `period_core` exists, but they are a different surface with different authority rules.
- `calendar_builder.py` and `best_times.py` consume marker/timing computations, not the final period semantic owner.
- This means adaptive period cards should treat daily/calendar/best-times as side evidence or timing hints, not as their primary meaning authority.

## 2. Period Field Inventory

## 2.1 `period_core` fields

| Field | Producer | Contains | Public/internal/debug/legacy | Semantic role | Safe for adaptive cards? | Notes / risks |
|---|---|---|---|---|---|---|
| `period_core.title` | `build_period_core(...)` | Short theme title | Public | UI summary | Yes, weakly | Useful as display label only |
| `period_core.core_story` | `build_period_core(...)` then renderer | Canonical public long-form period text shadow, now usually `period_reading_v1.full_text` | Public | UI summary | Yes, weakly | Treat as summary output, not source authority |
| `period_core.upper_meaning` | `build_period_core(...)` then renderer | High-level meaning shadow | Public | UI summary / legacy | Yes, weakly | Useful as fallback summary only |
| `period_core.period_reading_v1` | `build_period_story(...)` | Organic reading contract | Public | Rendered public surface | Yes | Good framing surface, but not primary evidence |
| `period_core.period_reading_v1.blocks[]` | `build_period_story(...)` | Hook / unfolding / growth / closer blocks | Public | Render support / UI surface | Yes | Useful for card rhythm and editorial paragraph splitting |
| `period_core.period_reading_v1.full_text` | `build_period_story(...)` | Canonical public organic full text | Public | UI summary / public proof surface | Yes | Strong proof surface; should not be re-parsed as main authority if structured fields already exist |
| `period_core.semantic_focus` | `resolve_period_semantic_focus(...)` | Selected meaning, domains, source, suppressed meanings, scene request, hints | Public additive | Semantic owner | Yes, primary | Strongest period-side authority input |
| `period_core.chapter_priority` | `deep_archetype_engine.py` | PR-D gate status and owner/evidence role | Public additive | Semantic routing / debug | Yes | Important for “cards orbit chapter owner or not” |
| `period_core.canonical_period_spine` | `canonical_natal_activation.py` via public builder | Canonical hook match and spine meaning seed | Public additive | Evidence | Yes, primary | Strong period→natal bridge |
| `period_core.natal_activation_context` | `canonical_natal_activation.py` | Top hook ids / matched event ids for period | Public additive | Evidence | Yes | Useful for trace/debug and card grounding |
| `period_core.featured_events[]` | `build_period_core(...)` | Selected period evidence cards | Public | Evidence | Yes, primary | Main period evidence pool |
| `period_core.story_tracks` | `build_period_core(...)` | Per-track legacy story copy grouped by inferred track id | Public additive | Legacy render support | Risky | May help dedupe clusters, but not authority |
| `period_core._event_story_map` | `build_period_core(...)` | Event id → track id map | Public additive/internal-ish | Legacy render support | Risky | Useful only for grouping, not meaning |
| `period_core._debug_root_causes` | `build_period_core(...)` transient | Old root-cause keys/evidence ids | Internal transient | Debug only | No | Popped out of final `period_core` by route before final payload |
| `period_core._period_story_debug` | `build_period_story(...)` | Renderer debug surface | Public additive debug | Debug only | Selectively | Good for traceability; not user-facing meaning |
| `period_core._period_story_debug.composer_plan` | `build_period_story(...)` | Internal hook / scene / contrast / mechanism / growth / closer plan | Debug | Render support | Yes, carefully | Good for card framing, not authority |
| `period_core._period_story_debug.semantic_focus` | `build_period_story(...)` | Semantic focus debug mirror | Debug | Debug / owner trace | Yes, for debug only | Helpful for trace fields |
| `period_core.period_teaser` | `public_builder.py` | Short teaser for summaries | Public | UI summary | Weakly | Teaser only; not enough for adaptive cards |
| `period_core.period_locked` | `public_builder.py` | Current lock state | Public | UI gating | No | Product gating, not meaning |
| `period_core.period_version` | `public_builder.py` | Hash/version of current period core | Public | Debug / caching | Yes, for trace only | Useful as cache/debug ref |
| `period_core.canonical_promise_prefix` | `canonical_natal_activation.py` injection | Canonical period prefix from natal activation | Public additive | Evidence / render support | Yes | Useful for chapter-aware framing, but secondary to semantic focus |

### Note on `_debug_root_causes`

`_debug_root_causes` is computed in `deep_archetype_engine.py`, but `transits.py` pops it out of `period_core` and exposes it instead as `_period_root_causes` on the larger narrative payload. This makes it useful for audit/debug, but too unstable as a direct adaptive-card contract input.

## 2.2 `featured_events[]` fields

| Field | Producer | Contains | Semantic role | Safe for adaptive cards? | Notes / risks |
|---|---|---|---|---|---|
| `event_id` | selection / public builder | Stable event id | Evidence ref | Yes | Required trace ref |
| `label` | event/public layer | Human-readable event label | Evidence display | Yes | Good debug/display only |
| `transit_body` | raw event / public | Transit planet/body | Evidence | Yes | Internal translation source |
| `natal_point` | raw event / public | Natal target point | Evidence | Yes | Internal translation source |
| `aspect` | raw event / public | Aspect type | Evidence | Yes | Internal translation source |
| `orb_deg` | raw event / public | Orb | Timing/evidence | Yes | Strong for support ranking, not meaning alone |
| `phase` / `current_phase` | raw event / public | Applying/exact/separating phase | Timing signal | Yes | Good for card timing hints |
| `bucket` / `time_scale` | raw event / public | Duration bucket | Timing signal | Yes | Good secondary timing hint |
| `houses` | raw event / public | Transit house / natal point house | Evidence | Yes | Strong scene/location hint |
| `tags` | raw event / public | Domain tags | Evidence/support | Yes | Useful but often generic |
| `chapter_role` | selection / role engine | Role scores like opener/builder/peak/release/integrator | Render support / evidence ranking | Yes | Useful as candidate role, not authority by itself |
| `story_score` | selection | Event-level story salience | Evidence ranking | Yes | Useful as ranking hint only |
| `selection_index` | selection | Position in chosen list | Debug / ranking | Yes, weakly | Trace only |
| `selection_mode` | selection | Why/how selected | Debug | Yes, weakly | Trace only |
| `derived_context` | hybrid context | Natal target, connected points, links, motifs, domains | Evidence / render support | Yes, primary | Strongest event-level card support input |
| `natal_promise` if present | natal promise builder | Promise match score/drivers/themes | Evidence | Yes, selectively | Useful but not guaranteed stable in every public compact path |
| `timing` | raw event / public | Entry/peak/exit dates, time hints | Timing signal | Yes | Good for collapsible timing chips |
| `semantic_role` / `semantic_owner` if present | PR-D chapter priority apply path | Evidence support vs owner marker | Semantic routing | Yes | Not present in every case; useful when chapter priority applies |

## 2.3 Semantic / policy layer fields

| Field | Producer | Contains | Semantic role | Safe for adaptive cards? | Notes / risks |
|---|---|---|---|---|---|
| `PeriodSemanticFocusResult` | `period_semantic_focus.py` | Selected meaning, family, domains, source, suppression, scene request, hints | Semantic owner | Yes, primary | Cards should start here |
| `period_voice_policy` output | `period_voice_policy.py` | Mechanism lens, psychological process, higher meaning, growth edge, what it builds, meaning intent, rhetorical frame, valence/intensity, manifestation context | Render support / framing | Yes, secondary | Strong framing, but too generic alone in some non-LifeChapter cases |
| `manifestation_context` | `manifestation_context_policy.py` | Primary house, life scene, context seed, angle/ruled houses, release strengthened | Evidence / lived-scene support | Yes, primary | Strong for “where this shows up” |
| `valence_mode` | policy layer | Emotional stance mode | Render support | Yes | Good for tone selection, not meaning |
| `intensity_mode` | policy layer | Density/intensity guidance | Render support | Yes | Good for card density / expansion behavior |
| `rhetorical_frame` | policy layer | Framing family | Render support | Yes | Good for display strategy, not authority |
| `meaning_intent` | policy layer | Policy-level meaning intent | Secondary semantic framing | Yes | Useful fallback meaning hint only |
| `suppressed_meanings` | semantic focus / life chapter | Meanings that must not surface | Guardrail | Yes, mandatory | Hard filter for card candidates |

## 2.4 LifeChapter fields

| Field | Producer | Contains | Semantic role | Safe for adaptive cards? | Notes / risks |
|---|---|---|---|---|---|
| `active_life_chapter` | `life_chapter_detector.py` | Tier-1 chapter contract | Semantic owner upstream | Yes | Strongest context when present |
| `renderer_handoff` | `active_life_chapter` | Human scene, contrast, chapter weight, chart anchor, avoid readings | Render support with authority backing | Yes | Strong card framing source for Tier-1 |
| `natal_architecture_anchor` | `active_life_chapter` | Human natal anchor | Evidence / render support | Yes | Strong personalization bridge |
| `domain_ownership` | `active_life_chapter` | Primary/secondary domain ownership | Semantic routing | Yes | Useful for chapter-first cards |
| `scene_priority` | `active_life_chapter` | Ordered scenes to prioritize | Render support | Yes | Good candidate ordering hint |
| `suppressed_readings` / `suppressed_surface_readings` | `active_life_chapter` | Meaning and surface bans | Guardrail | Yes, mandatory | Must hard-block contradicting cards |

## 2.5 Calendar / timing fields

| Field | Producer | Contains | Semantic role | Safe for adaptive cards? | Notes / risks |
|---|---|---|---|---|---|
| `calendar.days[].label_pack` | `calendar_builder.py` | Phase/top labels for a day | Timing signal / UI summary | Yes, secondary | Timing hint only |
| `calendar.days[].active_theme_ids` | `calendar_builder.py` | Active theme ids for day | Timing signal | Yes, secondary | Useful for linkage, not meaning |
| `calendar.days[].heat` / `score` / `rating` | `calendar_builder.py` | Day intensity summaries | Timing/UI only | Risky | Do not treat as meaning |
| Marker `score_by_intent` | interpretation / calendar path | Intent-specific timing score | Timing-only | Risky | Good for best-times, bad as card meaning source |
| `best_times` | `best_times.py` | Intent-ranked day candidates from marker scores | Timing-only | Risky | Not a semantic owner |
| Phase/inress/retro/station markers | calendar/event engine | Structural timing events | Timing evidence | Yes, secondary | Good for “when this peaks/releases” |

## 2.6 Daily-side fields

| Field | Producer | Contains | Semantic role | Safe for adaptive cards? | Notes / risks |
|---|---|---|---|---|---|
| `daily_synthesis` | `build_daily_synthesis(...)` | Daily narrative body, guidance, support signal, period spine, sources | Daily owner/surface | Risky | Do not let daily body become period-card authority |
| `daily_event_cards` | daily selector | Daily trigger/support events | Timing/support evidence | Yes, secondary | Useful only as same-period support |
| `today_story_candidate` | `today_story_candidate.py` | Daily story type, trigger, support ids, voice-policy snapshot | Daily routing | Yes, secondary | Useful to connect a period card to “today this is active” |
| `support_signal` | daily synthesis | Support/pressure synthesis for day | Secondary support | Yes, carefully | Good as support badge, not meaning |
| `period_spine` inside daily surfaces | daily synthesis / trigger selection | Daily relation to period spine | Support trace | Yes, secondary | Useful for cross-surface continuity |

## 3. Useful vs Risky Period Sources For Adaptive Cards

## Tier A — safe primary card inputs

- `semantic_focus_result`
- `chapter_priority`
- `canonical_period_spine`
- `natal_activation_context`
- `featured_events[].derived_context`
- `featured_events[].chapter_role`
- `featured_events[].story_score`
- `manifestation_context`
- `suppressed_meanings`
- `active_life_chapter.renderer_handoff`
- `active_life_chapter.natal_architecture_anchor`
- `composer_plan`
- `period_reading_v1` as framing/proof surface

Why Tier A is safe:

- It is already inside the current semantic period chain.
- It is either owner, evidence, or render support directly tied to current period evidence.
- It can personalize and expand without inventing a second owner.

Important nuance:

- `period_reading_v1` and `composer_plan` are safe as **framing** inputs, not as primary evidence.
- `semantic_focus`, `chapter_priority`, `canonical_period_spine`, `featured_events`, and `manifestation_context` should stay structurally above them.

## Tier B — useful supporting inputs

- `featured_events[].timing`
- `featured_events[].phase`
- `featured_events[].bucket`
- event tags/domains
- calendar markers
- `active_theme_ids`
- `label_pack`
- daily `support_signal`
- `today_story_candidate`

Why Tier B is useful:

- These fields help decide “when does this peak,” “what scene is hottest now,” or “which card deserves an expandable timing drawer.”

Why Tier B is not enough alone:

- They are timing/support enrichments, not stable semantic owners.
- They should decorate or prioritize cards, not decide what the period means.

## Tier C — risky or not safe as authority

- raw `story_score` alone
- raw `heat` / `rating` alone
- `best_times.score_by_intent`
- `daily_synthesis.body`
- daily narrative copy as source for period cards
- old `blocks[]`
- `story_tracks` as meaning owner
- `_event_story_map` as meaning owner
- legacy/profile-rendered text branches

Why Tier C is risky:

- It is score-heavy, UI-heavy, or legacy/rendered.
- It can easily create cards that sound plausible but are no longer anchored to the selected period meaning.
- It raises the risk that adaptive cards quietly become a second interpretation system.

## 4. What Period Cards Actually Need

Each strong adaptive card needs:

- one selected period meaning link
- one evidence source
- one domain / life scene
- one user-facing tension or movement
- one trace/debug ref

### Minimal card shape

- `meaning_ref`
  - from `semantic_focus_result`
- `evidence_ref`
  - event id, canonical hook, or chapter handoff
- `scene_ref`
  - manifestation context or derived context
- `movement_ref`
  - tension / growth / release / integration
- `debug_ref`
  - card id, source ids, suppression checks

### Example

Communication card:

- `semantic_focus`: `speech_authority` or `reorientation`
- `evidence`: Saturn return 3rd or a strong 3rd/1st transit stack
- `manifestation_context`: messages, conversations, near environment
- `natal context`: activated 3rd-house / Saturn promise
- `copy`: lived recognition, not analysis

## 5. How Period Signals Should Become Cards

A conservative backend algorithm should look like this:

1. Start from `semantic_focus_result`.
2. Read `chapter_priority`.
   - If applied, cards orbit chapter owner.
   - If not, cards stay evidence-guided and must not imitate a pseudo-chapter.
3. Use `period_reading_v1` and `composer_plan` for main framing.
4. Build card candidates from:
   - primary owner / chapter line
   - top `featured_events`
   - strong secondary domains
   - manifestation context
   - timing peaks / releases
5. Enrich with `NatalContextForPeriodCards`.
6. Drop unsupported candidates.
7. Dedupe.
8. Apply no-contradiction checks.
9. Emit `0–8` cards, usually `3–6`.

### Key discipline

Do not generate a card just because a role exists.

Generate a card only if:

- there is a real semantic anchor,
- there is a real event/natal trace,
- and the card adds a distinct scene/tension/value beyond the main reading.

## 6. What Period Computations Should Be Improved Later

| Weak spot | Blocker or later polish? | Recommended PR | Risk if ignored |
|---|---|---|---|
| `period_voice_policy` can still be generic in non-LifeChapter cases | Later polish, not blocker | Fallback density / domain-anchoring pass | Cards may sound flatter in non-chapter periods |
| `story_score` and `chapter_role` are useful but not yet an explicit card-selection contract | Medium blocker | `PeriodCardContext` shaping PR | Card ranking may feel arbitrary |
| `featured_events` are rich, but they lack a compact human-facing evidence summary | Later polish | Event evidence summarizer PR | Cards may overuse raw technical clues or under-explain evidence |
| `period_reading_v1` fallback is still less vivid than Tier-1 chapter outputs | Later polish | Non-LifeChapter fallback vividness PR | Non-chapter cards inherit weaker tone |
| Event-derived domains are sometimes too generic or house-biased | Medium blocker | Domain normalization PR | Cards may over-repeat broad labels |
| Calendar labels / heat / rating are not SHOU voice | Later polish | Calendar public polish PR | Timing chips may feel disconnected from premium voice |
| Daily can sound more specific than period in some paths | Later polish | Daily/period alignment PR | Cross-surface mismatch can confuse users |
| Best-times is not meaning-aware | Later polish | Timing/opportunity engine PR | Cards must not rely on best-times for meaning |

## 7. Relation To The Old `blocks[]` Surface

The old top-level `blocks[]` surface is still built in `backend/app/api/routes/transits.py` from `backend/app/transit/narrative/assembler.py`.

Observed block types in current artifacts:

- `core_theme`
- `support`
- `daily_energy`
- `event_list_preview`
- related screen builders and `screens.*`

### What it is

- A legacy UI assembly layer
- horizon/intensity/domain grouped blocks
- mostly ASCII-normalized generic copy bundles

### What it is not

- It is not the current semantic period owner
- It is not `period_reading_v1`
- It is not the right basis for adaptive period cards

### Recommendation

- Ignore old `blocks[]` as an authority source.
- Do not base `period_signal_lines_v1` on `core_theme`, `daily_energy`, or `event_list_preview`.
- At most, reuse:
  - block horizon conventions
  - CTA grouping logic
  - UI grouping semantics

Do not reuse:

- block meaning logic
- generic copy
- score/intensity heuristics as semantic meaning

### Future removal stance

- `core_theme`, `daily_energy`, and `event_list_preview` are strong deprecation candidates later.
- They should not block adaptive cards.
- They should be removed only after mobile/frontend consumers migrate away from them.

## 8. Output Recommendation

### Recommended answer

**B) first create `PeriodCardContext / PeriodEvidenceContext`**

Implementing cards directly from the current raw field set would work, but it would couple a new UI surface to too many mixed-purpose fields.

### Recommended PR order

1. Period computation inventory + card context contract
2. `PeriodCardContext / PeriodEvidenceContext` + `NatalContextForPeriodCards` integration plan
3. Adaptive period cards backend additive
4. Mobile expandable cards
5. Old `blocks[]` deprecation

### Why not “implement cards now”

- The semantic owner chain is ready.
- The raw material is ready.
- The missing piece is a narrow projection contract that says which period fields are authoritative, which are just support, and which are forbidden.

## 9. Real Examples From Current Artifacts

## 9.1 2026-03-04 real route case

Current available period data:

- `semantic_focus.source = period_voice_policy`
- `semantic_focus.selected_meaning = reorientation`
- `semantic_focus.primary_domain = küçük cümlelerin ağırlığı`
- `manifestation_context.primary_house = 3`
- `manifestation_context.life_scene = küçük cümlelerin ağırlığı`
- `chapter_priority.applied = false`
- top featured events include:
  - `Neptune square Sun`
  - `Neptune square DSC`
  - `Saturn sextile Uranus`

What cards could be generated:

- “Konuşma / small-signal ambiguity” card
- “Identity under diffuse pressure” card
- “Relationship boundary tone” support card

Which fields support them:

- `semantic_focus`
- `featured_events[].derived_context`
- `manifestation_context`
- `chapter_role`
- `story_score`
- `natal_activation_context` when present

Which fields should not be used:

- raw `story_score` alone
- old `daily_energy`
- `best_times`

Important note:

This artifact is a non-LifeChapter `period_voice_policy` case. Separately, the later PR-D wiring work proved that the real Istanbul chart can emit a Saturn-return life chapter in the flagged Tier-1 path. For adaptive cards, this means the backend already supports both a non-chapter evidence-guided card mode and a chapter-first card mode.

## 9.2 2026-04-22 real route case

Current available period data:

- `semantic_focus.source = period_voice_policy`
- `semantic_focus.selected_meaning = reorientation`
- `semantic_focus.primary_domain = yakın çevrendeki ses`
- `semantic_focus.secondary_domains` includes house-2 / house-4 / house-5 traces
- top events include:
  - `Neptune square Sun`
  - `North Node sextile Sun`
  - `Sun trine ASC`
  - `Uranus sextile South Node`
  - `Venus trine Mars`
- one featured event runs through transit house `4`

What cards could be generated:

- “Belirsizliği doldurmadan yönünü ayırma” main card
- “İç güvenlik ile kimlik/duruş ilişkisi” support card
- “Yakın çevre / cümle tonu” secondary card

Which fields support them:

- `semantic_focus`
- `featured_events[].houses`
- `featured_events[].derived_context.connected_points`
- `manifestation_context`
- `chapter_role` / `story_score`

Which fields should not be used:

- raw heat/rating
- daily body copy
- legacy `core_theme`

Key weak spot:

This case shows why a future `PeriodCardContext` is necessary. The selected semantic focus remains communication-leaning, while the wider event stack also contains identity / 4th-house / interior-security support. Cards need a controlled way to surface that support without overriding the selected meaning.

## 9.3 Cancer 8th Saturn return fixture

Current available period data:

- `semantic_focus.source = life_chapter`
- `selected_meaning = shared_emotional_territory`
- `primary_domain = trust_transformation`
- `chapter_priority.applied = true`
- chapter handoff fields are present
- suppressed meanings are present

What cards could be generated:

- “Shared vs private burden” main card
- “Naming trust boundaries” support card
- “What gets shared and what stays yours” tension/growth card

Which fields support them:

- `active_life_chapter.renderer_handoff`
- `active_life_chapter.natal_architecture_anchor`
- `semantic_focus`
- `suppressed_meanings`
- `period_reading_v1`
- `composer_plan`

Which fields should not be used:

- generic vulnerability templates
- old `blocks[]`
- best-times

## 9.4 Nodal Aries/Libra fixture

Current available period data:

- `semantic_focus.source = life_chapter`
- `selected_meaning = directional_self_definition`
- `primary_domain = identity_presence`
- `chapter_priority.applied = true`
- suppressed meanings include generic self/other balance

What cards could be generated:

- “Choosing direction without collapsing into approval” main card
- “Speaking your line in relationship” support card
- “Adjustment vs self-erasure” tension card

Which fields support them:

- `semantic_focus`
- `chapter_priority`
- `renderer_handoff`
- `suppressed_meanings`
- `period_reading_v1`

Which fields should not be used:

- generic relationship-drama language
- profile-style identity claims

## 10. Recommended Card Context Contract

### Period-side contract should likely expose:

- `owner_ref`
  - semantic focus id/source/family
- `chapter_ref`
  - chapter priority applied?
  - chapter type/id if any
- `framing_ref`
  - composer plan slots
  - period reading block roles
- `evidence_refs`
  - selected featured event ids
  - chapter role
  - story score
  - derived context
  - timing phase
- `scene_refs`
  - manifestation context
  - primary and secondary domains
- `guardrails`
  - suppressed meanings
  - chapter suppressed surface readings when applicable
- `debug_refs`
  - period version
  - semantic source
  - source event ids

This is the period-side equivalent of the natal audit’s recommendation:

`period_core + canonical_natal_state`
→ `NatalContextForPeriodCards`

The period side should become:

`period_core`
→ `PeriodCardContext / PeriodEvidenceContext`

Then:

`PeriodCardContext + NatalContextForPeriodCards`
→ `period_signal_lines_v1`

## 11. Open Questions

- Should `PeriodCardContext` expose `composer_plan` raw, or a reduced framing contract only?
- Should event timing be normalized into a single card-timing field instead of reusing raw `timing`, `phase`, and `bucket` fields separately?
- Should `story_tracks` be kept only as an internal clustering helper, or ignored entirely for card generation?
- Do we want a strict maximum number of chapter-owned cards when `chapter_priority.applied=true`, to prevent secondary evidence from over-expanding the UI?
- Should the first adaptive-card PR ship only backend context emission, before copy rendering?

## Final Recommendation

The backend already computes enough period meaning, evidence, scene context, and timing support to power adaptive cards. What it does not yet have is a narrow, card-specific contract that protects the current semantic authority chain from becoming diffuse.

The safest next move is:

1. define `PeriodCardContext / PeriodEvidenceContext`
2. connect it to `NatalContextForPeriodCards`
3. build backend additive adaptive cards
4. let mobile consume them
5. deprecate the old `blocks[]` layer later

Adaptive cards should be built from the current semantic period pipeline, not from the old assembler surface.
