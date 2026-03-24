# Jovia Visual System Field Mapping Spec

Updated: 2026-03-20

This document maps current backend-visible payload fields into the normalized interpretation schema defined in [normalized_interpretation_schema.ts](./normalized_interpretation_schema.ts).

## Mapping Principles

- Mapping is deterministic.
- Structural fields win over free text.
- Text is used only as fallback or supporting evidence.
- Visual decisions must be based on normalized tags and visual tokens, not on raw backend fields directly.
- Internal scores and provenance fields can influence visual adaptation but should not be shown directly in primary UI.

## 1. Profile Mapping

### Raw -> Normalized semantic layer

| Raw field | Normalized target | Rule |
| --- | --- | --- |
| `core_story_ui.text` | `identity_core.summary` | Highest-priority identity summary source. |
| `core_story` | `identity_core.summary` | Use if `core_story_ui.text` is empty. |
| `narrative_text`, `summary` | `identity_core.summary` | Final fallback. |
| `planets[].sign`, `planet_signs{}`, `formatted_positions[]` | `energyType` | Convert signs to elements; use dominant element, return `mixed` if top two counts are close. |
| `angles.ascendant_sign`, `angles.asc_sign` | `chart_context.rising_sign` | Extract rising sign; derive chart ruler from sign if needed. |
| `profile_narrative.profile_public.blocks[]` | `reading_layers.profileNarrative[]` | Map block-by-block without rewriting text. |
| `profile_narrative.profile_public.blocks[].id` | `meaning_layer` | `overview` is primary identity overview; other ids become secondary reading chapters. |
| `profile_narrative.profile_public.blocks[].headline` | `reading_title` | Use directly for reading panel titles. |
| `profile_narrative.profile_public.blocks[].teaser`, `subtitle` | `preview_copy` | Short preview layer for Profile surfaces. |
| `profile_narrative.profile_public.blocks[].body` | `detail_copy` | Deep reading layer for Haritam. |
| `profile_narrative.profile_public.blocks[].micro` | `micro_copy` | Meta caption / supporting line. |
| `profile_narrative.profile_public.blocks[].astro_hint` | `astro_context` | Safe secondary metadata. |
| `profile_narrative.profile_public.blocks[].astro_sources[]` | `source_signals` | Internal trace or optional tech detail. |
| `profile_narrative.profile_public.blocks[].chips[]` | `activeDomains` or section metadata | Normalize only if chip matches known domain vocabulary; otherwise keep as display metadata. |
| `narrative_v2.aspect_bundle_selector.selected_bundles[]` | `bundleTypes`, `dominantDomains`, semantic patterns | Use bundle type first; domains and tags shape patterns. |
| `selected_bundles[].bundle_type` | pattern family | Map to emotional / mental / relational / identity / contradiction / pressure / capacity / core. |
| `selected_bundles[].domains[]` | `dominantDomains`, `activeDomains` | Count frequencies; sort descending. |
| `selected_bundles[].recognition_tags[]` | pattern evidence | Safe for secondary explanation, not direct visual rule input unless used as debug trace. |
| `selected_bundles[].gift_tags[]` | strengths | Can influence share-card emphasis or positive CTA framing. |
| `selected_bundles[].reflex_tags[]` | tension evidence | Contributes to `tensionPattern`. |
| `personality_imprint.headline` | `identity_signature.headline` | Primary identity signature string for Profile/Studio. |
| `personality_imprint.render_shape` | illustration/debug hint | Safe for internal visual experimentation; do not depend on it as sole renderer input. |
| `personality_imprint.entries[]` | dominant identity objects | Source for `aura`, `trait`, `drive`, `shadow`, `gift`. |
| `entries[].kind` | `entry_kind` | Maps to `aspect`, `house_placement`, `sign_placement`. |
| `entries[].tags[]` | display chips / semantic evidence | Use as metadata unless tag matches controlled vocab. |
| `entries[].aura` | `emotionalPattern`, surface mood support | Strong signal for hero tone / mood family. |
| `entries[].trait` | `behavioralPattern`, `expressionPattern` support | Identity / expression evidence. |
| `entries[].drive` | `behavioralPattern` / `speed` support | Motivation and force direction. |
| `entries[].shadow` | `tensionPattern`, `contrastLevel` support | Never primary hero copy. |
| `entries[].background_hint` | support layer | Keep in deep-reading only. |
| `entries[].gift` | strength layer | Safe for Studio/share emphasis. |
| `entries[].support_keys[]` | internal connection graph | Use to group related modules; do not show raw. |
| `personality_imprint.support_entries[]` | support identity modules | Secondary content family. |
| `personality_imprint.bundles[].dominant_key` | entry grouping | Connect dominant entry to related support entries. |
| `personality_imprint.bundles[].related_planets[]` | symbolic accent seed | Safe for illustration accent or glyph selection. |
| `supporting_threads[]` | social resonance layer | Secondary social proof, not identity core. |

### Derived profile rules

- `energyType`: count elements from placements; fallback to rising sign if placements are sparse.
- `moodType`: Saturn/earth -> `structured`; Neptune/water contradiction -> `diffuse` or `ambiguous`; fire + high activation -> `intense`.
- `behavioralPattern`: `pressure_growth_bundle` + earth -> `distiller`; earth default -> `stabilizer`; fire default -> `initiator`; water default -> `container`.
- `mentalPattern`: `mental_style_bundle` + Saturn/air -> `analytical` or `synthetic`.
- `expressionPattern`: `angle_identity_bundle` + earth/Saturn -> `measured`; fire -> `performative`; water -> `quiet`.
- `tensionPattern`: `contradiction_bundle` -> `inner_split`; shadow-heavy + Saturn -> `overcontrol`.

## 2. Timing Mapping

| Raw field | Normalized target | Rule |
| --- | --- | --- |
| `public.period_core.title` | `timing_core.title` | Main period frame. |
| `public.period_core.core_story` | `timing_core.summary` | Period summary layer. |
| `public.period_core.upper_meaning` | `timing_core.upper_meaning` | Hero / feature subtitle candidate. |
| `public.period_core.big_picture` | `timing_core.big_picture` | Secondary reading panel. |
| `public.period_core.mechanism` | `timing_core.mechanism` | Best source for explanatory body. |
| `public.period_core.tags[]` | period metadata | Secondary chips only. |
| `public.event_cards[]` | `timing_events[]` | Primary current-state narrative units. |
| `event_cards[].headline`, `title` | `timing_events[].title` | Prefer `headline`. |
| `event_cards[].opening` | `timing_events[].summary` | Primary preview sentence. |
| `event_cards[].essence` | `timing_events[].essence` | Best deep-reading short core. |
| `event_cards[].mechanism` | `timing_events[].mechanism` | Explanatory logic layer. |
| `event_cards[].asks` | `timing_events[].directive` | Action/response layer. |
| `event_cards[].watchout`, `shadow` | `timing_events[].risk` | Contributes to contrast/tension. |
| `event_cards[].what_it_builds` | `timing_events[].growth` | Positive developmental layer. |
| `event_cards[].technical_note` | internal detail | Safe in advanced detail only. |
| `event_cards[].why_now` | `timing_events[].timing_reason` | Context cue. |
| `event_cards[].tone` | `moodType` support | Low-confidence support only. |
| `event_cards[].guidance[]` | `timing_events[].guidance` | Action/support bullets. |
| `event_cards[].watch_out[]` | `timing_events[].risk_list` | Secondary caution bullets. |
| `event_cards[].hook_tags[]` | `timing_events[].hook_tags` | Metadata only. |
| `event_cards[].tags.domain` | `activeDomains` | Count toward domain focus. |
| `event_cards[].tags.phase` | `timingPhase` | Normalize into `applying`, `peak`, `exact`, `exit`, `waning`, `receding`, `unknown`. |
| `event_cards[].tags.duration` | utility metadata | Safe for timing rows, not hero. |
| `event_cards[].tags.intensity` | `intensityBand`, `densityLevel`, `contrastLevel` | Numeric timing force. |
| `event_cards[].timing.timing_note` | timing meta | Timing note line. |
| `event_cards[].period_story.title`, `lead`, `big_picture` | umbrella layer | Use for broad period context, not main event body. |
| `public.period_peak_timeline[]` | `timing_peak_rows[]` | Utility row family. |
| `public.timeline.summary`, `lines[]`, `dot_intensity` | daily timeline | Utility + density cue. |
| `calendar.days[].heat`, `rating` | utility severity | Can affect accent intensity. |
| `calendar.days[].signals_count`, `event_count` | density | Calendar cell density only. |
| `calendar.days[].is_critical` | contrast/attention | Use sparingly; not for global archetype. |
| `public.markers[]` | support timing rows | Secondary timing support only. |
| `public.themes[]` | fallback timing topics | Use when event cards are absent. |
| `public.intent_summary{}` | intent-based utility cards | Safe for utility rows, not narrative hero. |
| `screens.personal_transit.blocks[]` | screen-specific narrative | Can provide UI copy but should not override `public.event_cards` as primary meaning source. |
| `screens.feed_snippet`, `space_hub`, `calendar_day` | screen-specific variants | Useful for screen-specific layouts; lower precedence than event/period contracts. |

### Derived timing rules

- `intensityBand` comes from highest visible event-card intensity.
- `speed` derives from `phase`: `peak/exact` -> `fast`, `applying` -> `steady`, `waning/receding` -> `slow`.
- `densityLevel` increases with more active domains, higher event intensity, and more simultaneous timing rows.
- `heroMode` for Home should come from `period_core` + first event, not from utility rows.

## 3. Collective Mapping

| Raw field | Normalized target | Rule |
| --- | --- | --- |
| `/sky/now.summary_tr` | `collective.summary` | Primary collective summary line. |
| `/sky/now.items[]` | `collective.items[]` | Topic list. |
| `items[].short_title_tr`, `items[].title_tr` | `topic.title` | Prefer short title. |
| `items[].summary_tr` | `topic.summary` | Main collective topic body. |
| `items[].badge_tr` | `topic.badge` | Timing / status badge. |
| `items[].relative_timing_tr` | `topic.relative_timing` | Time state for social metadata. |
| `items[].tags[]` | `activeDomains`, topic metadata | Normalize only if tag matches controlled domain vocab; otherwise keep as metadata. |

### Derived collective rules

- `collectiveActivation`: `active` if there are items with chart-relevant tags; `possible` if items exist but no chart-relevant tags; `none` if empty.
- `socialDensity`: based on item count and rising-signal count.
- `shapeFamily`: collective topics prefer `paired_axis`, `orbit`, or `burst` depending activation and contrast.
- Do not use collective text to overwrite identity archetype. Collective is a contextual overlay.

## 4. Bond Mapping

| Raw field | Normalized target | Rule |
| --- | --- | --- |
| `public.synastry_imprint.summary` | `bond.summary` | Primary relationship summary. |
| `public.synastry_imprint.theme` | `bond.theme` | Secondary bond framing line. |
| `public.synastry_imprint.lesson` | `bond.lesson` | Growth/teaching layer. |
| `public.synastry_imprint.emotional_dynamic` | `bond.emotional_dynamic` | Emotional layer. |
| `public.synastry_imprint.headline` | `bond.headline` | Optional bond signature title. |
| `public.narrative.blocks[]` | `bond.reading_blocks[]` | Narrative-first bond reading. |
| `public.drivers` | `bond.drivers` | Driver categories and line items. |
| `public.display.touchpoints_lines[]` | `bond.flow_lines` | What flows. |
| `public.display.aspects_lines.top[]` | `bond.aspect_lines` | Advanced detail only. |
| `public.derived_context.partner_a_activated[]` | relational activation evidence | Domain activations and reasons. |
| `public.derived_context.partner_b_activated[]` | relational activation evidence | Domain activations and reasons. |
| `public.derived_context.asymmetry_notes[]` | `tensionPattern`, `contrastLevel` support | Strong asymmetry cue. |
| `public.narrative_ready.partner_a_story.lived_as` | `bond.partner_a_lived_as` | Readable partner resonance layer. |
| `public.narrative_ready.partner_b_story.lived_as` | `bond.partner_b_lived_as` | Readable partner resonance layer. |
| `partner_*_story.primary_domain` | `activeDomains` | Count domain focus. |
| `partner_*_story.secondary_domain` | `activeDomains` | Count domain focus. |
| `partner_*_story.surface_domain` | `activeDomains` | Count domain focus. |
| `partner_*_story.background_domain` | `activeDomains` | Count domain focus. |
| `public.scores.*` | internal resonance metrics | May affect contrast / density / sustainability but should not be shown raw on primary UI. |
| `public.raw_scores.*` | internal scoring only | Never primary UI copy. |
| `public.contextual_scores.*` | internal scoring only | Never primary UI copy. |
| `public.resonance_scores.*` | internal scoring only | Never primary UI copy. |

### Derived bond rules

- `relationalPattern`: `bonding` when relational bundle/summary aligns with sustainable connection; `testing` when trigger load is high; `negotiating` when asymmetry notes are present.
- `tensionPattern`: `asymmetry` if asymmetry notes exist; otherwise use contradiction/trigger cues.
- `contrastLevel`: increased by `trigger_load`, `magnetic_intensity`, `growth_tension`, and asymmetry notes.

## 5. Safe vs Unsafe Display Rules

### Safe for illustration mapping

- dominant element / `energyType`
- mood / structure / clarity / speed
- normalized archetype
- dominant domains
- timing phase
- collective activation level
- chart-ruler-derived heaviness only as internal signal
- personality imprint `kind` and `related_planets`

### Safe for spacing rhythm

- `densityLevel`
- `clarity`
- `socialDensity`
- `timingPhase`
- `cohesion`
- content length of each surface

### Safe for typography hierarchy

- `heroMode`
- `narrativeMode`
- `intensityBand`
- `contrastLevel`
- `weight`
- `archetype`

### Should NOT be shown directly in user-facing primary surfaces

- `raw_scores`
- `contextual_scores`
- `resonance_scores`
- raw `drivers` key names when untranslated
- `narrative_provenance`
- `contract_version`
- `engine_version`
- `library_version`
- `support_keys`
- raw `derived_context`
- raw `render_shape`
- internal calendar `heat` / `signals_count` unless translated into UI copy
- `technical_note` outside advanced detail

## 6. Surface Priority by Screen

- Profile: identity core, signature, dominant imprint, core bundles, natal trinity.
- Home: period core, first event, collective summary, upcoming timing rows.
- Haritam: profile narrative blocks, imprint entries, bundle-driven chapters, support threads.
- Bond: synastry imprint, narrative blocks, flow/tension/lesson/emotional dynamic.
- Studio: imprint headline, one dominant entry, one supporting gift/shadow pair.
