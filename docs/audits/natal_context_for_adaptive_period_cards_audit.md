# Natal Context For Adaptive Period Cards Audit

## TL;DR

- Future `period_signal_lines_v1` / adaptive expandable period cards should not become a second meaning engine. They should sit **after** `semantic_focus_result` and `period_reading_v1`, and only personalize already-selected period meaning through natal context.
- The safest current runtime inputs are already in the transit stack: `period_core.semantic_focus`, `period_core.canonical_period_spine`, `period_core.natal_activation_context`, `period_core.featured_events[].derived_context`, and, for Tier-1 cases, `active_life_chapter.renderer_handoff`.
- The strongest deeper upstream source is `CanonicalNatalStateV1`, especially `core_promises`, `contradictions`, `chart_spine`, `meaning_graph.activation_hooks`, `structural_state.dispositor_routes`, and `structural_state.house_ruler_routes`.
- `personality_imprint`, `profile_v8`, `full_map_v8`, `meaning_graph_v1_1`, and projection outputs are useful only as downstream display/color references, if used at all. They should not become semantic authority for period cards.
- The safest architecture is not direct card rendering from many raw sources. It is a narrow projection layer: `period_core + canonical_natal_state -> NatalContextForPeriodCards`, then card rendering from that contract.
- Phase 1 should stay canonical and evidence-first: event-linked natal hooks, chart spine, promise/contradiction context, and translated structural routes. Avoid profile-style identity claims unless they are period-triggered and traceable.

## 1. Current Runtime Field Map

The current period runtime chain is:

`active_life_chapter`
→ `semantic_focus_result`
→ `chapter_priority`
→ `composer_plan`
→ `period_reading_v1`

Adaptive cards should come **after** this chain, not beside or above it.

### Runtime fields already in the period stack

| Path | Producer | What it contains | Safe for public copy? | Role |
|---|---|---|---|---|
| `period_core.semantic_focus` | `resolve_period_semantic_focus(...)` in `backend/app/transit/narrative/period_semantic_focus.py` | Selected meaning, meaning family, primary/secondary domains, suppression list, scene translation request, voice hints, confidence, source | Yes, indirectly. Safe as an internal semantic contract; public copy should translate it, not dump labels verbatim | Semantic owner |
| `period_core.chapter_priority` | `build_period_core(...)` in `backend/app/transit/narrative/deep_archetype_engine.py` | PR-D gate status, owner, chapter type, chapter id, semantic focus source, event card role | Yes for debug/breadcrumbs, not as prose | Semantic routing / debug |
| `period_core.canonical_period_spine` | `build_canonical_period_spine(...)` in `backend/app/transit/narrative/canonical_natal_activation.py` via public builder path | Canonical matched hook, target node, domains, spine evidence, meaning seed, natal activation tie | Yes, but translated. It is an evidence carrier, not user-facing raw copy | Evidence |
| `period_core.natal_activation_context` | `build_transit_natal_activation_context(...)` in `backend/app/transit/narrative/canonical_natal_activation.py` | Top matched hooks, matched event ids, target node ids, period/daily activation summaries | Yes, but only after translation; raw hook ids should stay internal | Evidence |
| `period_core.featured_events[]` | `build_period_core(...)` in `backend/app/transit/narrative/deep_archetype_engine.py` | Selected period event cards used as current period evidence | Yes, selectively. Already public-facing event layer | Evidence |
| `period_core.featured_events[].derived_context` | `build_hybrid_event_context(...)` in `backend/app/transit/narrative/hybrid_context.py` | `natal_target`, `connected_points`, `links`, `motifs`, `derived_domains` | Yes, after translation. Raw labels are internal support | Evidence / render support |
| Event-card-level `natal_promise` | `build_natal_promise(...)` in `backend/app/transit/narrative/natal_promise.py` and event assembly in `deep_archetype_engine.py` | Promise match score, connected points, drivers/themes, claim linkage | Yes, selectively. Good evidence input; not all compact/public period payloads surface it as a guaranteed `featured_events[]` field | Evidence |
| `period_core.period_reading_v1` | `build_period_story(...)` in `backend/app/transit/narrative/astrolog_narrative_engine.py` | Organic public prose: `blocks[]` and `full_text` | Yes. This is the current public period surface | Rendered public surface |
| `period_core._period_story_debug.composer_plan` | `build_period_story(...)` in `backend/app/transit/narrative/astrolog_narrative_engine.py` | Internal hook / scene / contrast / mechanism / growth / closer plan | No, not for direct public copy | Render support |
| `period_core._period_story_debug.semantic_focus` and related markers | `build_period_story(...)` + semantic focus resolver | Semantic ownership markers, consumed fields, suppressed readings applied, mode | No, debug only | Debug / trace |
| `active_life_chapter` (runtime internal input, not stable public surface) | `detect_active_life_chapter(...)` in `backend/app/transit/narrative/life_chapter_detector.py` | Chapter type, selected meaning, semantic focus, domain ownership, natal architecture anchor, scene priority, renderer handoff, suppressed readings | Only partially, after translation. It is upstream authority, not a public copy source | Semantic owner |
| `active_life_chapter.renderer_handoff` | `life_chapter_detector.py` | Human scene, core contrast, chapter weight, chart-specific anchor, voice register, avoid readings | Yes, after translation. Strong render support for Tier-1 cases | Render support with semantic authority upstream |
| `active_life_chapter.natal_architecture_anchor.human` | `life_chapter_detector.py` | Humanized natal architecture phrase anchored to chapter claim | Yes, selectively | Evidence / render support |

### Important nuance on `natal_promise`

`natal_promise` already exists in the event interpretation / selection / narrative stack, but it is not as stable a public `period_core.featured_events[]` contract as `derived_context` and `canonical_period_spine`. For adaptive cards, it is safe to use as an internal evidence input, but the card contract should not depend on it being present in every compact/public period payload.

## 2. Deeper Natal Sources That Exist But Do Not Fully Reach Period Runtime

These sources already exist in the backend, but most are not yet shaped for period-card consumption.

| Source | Where it lives | What it contains | Can it safely feed period cards? | Notes |
|---|---|---|---|---|
| `CanonicalNatalStateV1` | `backend/app/astro_os/natal/contracts.py` + `state_builder.py` | Canonical structural state, promises, contradictions, chart spine, meaning graph | Yes | Best upstream natal authority |
| `core_promises` | `CanonicalNatalStateV1.core_promises` | Canonical natal promises with evidence and linked contradictions/patterns | Yes | Strong candidate for card personalization when activation is explicit |
| `contradictions` | `CanonicalNatalStateV1.contradictions` | Canonical tension/integration nodes with evidence | Yes | Useful only when activated by current period evidence |
| `chart_spine` | `CanonicalNatalStateV1.chart_spine` | Primary identity, emotional regulation, relational, work visibility, shadow protection, growth integration lines | Yes | Strong translator between natal structure and public language |
| `meaning_graph.activation_hooks` | `backend/app/astro_os/natal/meaning_graph.py` | Hook ids that connect period triggers to canonical natal nodes | Yes | Already used by `canonical_natal_activation`; ideal bridge layer |
| `structural_state.dispositor_routes` | `CanonicalNatalStateV1.structural_state` | Canonical routing from sign dispositor structures to promises | Yes, carefully translated | Strong internal support; must not leak jargon |
| `structural_state.house_ruler_routes` | `CanonicalNatalStateV1.structural_state` | Canonical manifestation routes through houses/rulers | Yes, carefully translated | Good for “where this lands” in cards |
| `structural_state.planet_conditions` / `aspect_patterns` | `CanonicalNatalStateV1.structural_state` | Canonical planet condition / aspect structure | Yes, secondarily | Use only when it clearly supports the already-selected period theme |
| `canonical_natal_activation` outputs | `backend/app/transit/narrative/canonical_natal_activation.py` | Period-to-natal hook matching summaries | Yes | Already partially in runtime; should remain Tier A |
| `personality_imprint` | `backend/app/natal/personality_imprint/` | Public-facing headline, entries, bundles, support entries | Only as optional color reference | Too rendered/editorial to act as semantic source |
| `profile_v8` / `full_map_v8` | `backend/app/natal/profile_v8_payload_builder.py` | Editorial profile sections and fragments | No for authority; maybe limited tone inspiration | Too downstream and identity-heavy |
| `meaning_graph_v1_1` | `backend/app/meaning/meaning_graph_v1_1_builder.py` | Projection-oriented meaning graph built partly from public imprint surfaces | No for authority | Downstream / display-oriented |
| Projection outputs (`profile_narrative_projection_v1`, `profile_v8_projection_v1`) | `backend/app/meaning/projection_shadow_v1_builder.py` | Rendered projection surfaces | No as source | Legacy/display outputs, not canonical semantics |

## 3. Safe Natal Source Hierarchy For Adaptive Period Cards

### Tier A — canonical and evidence-safe

These are safe as actual card context inputs:

- `CanonicalNatalStateV1`
- `core_promises`
- `contradictions`
- `chart_spine`
- `meaning_graph.activation_hooks`
- `structural_state.dispositor_routes`
- `structural_state.house_ruler_routes`
- `period_core.semantic_focus`
- `period_core.canonical_period_spine`
- `period_core.natal_activation_context`
- `period_core.featured_events[].derived_context.natal_target`
- `period_core.featured_events[].derived_context.connected_points`
- `period_core.featured_events[].derived_context.motifs`
- Event-level `natal_promise` when available
- `active_life_chapter.renderer_handoff`
- `active_life_chapter.natal_architecture_anchor`

Why Tier A is safe:

- It is either canonical natal structure, or period-linked evidence that already flows through the transit runtime.
- It is traceable to period triggers.
- It can personalize meaning without inventing a second semantic owner.

### Tier B — projection / display surfaces

These are not safe as authority:

- `personality_imprint`
- `profile_v8`
- `full_map_v8`
- `meaning_graph_v1_1`
- `profile_narrative_projection_v1`
- `profile_v8_projection_v1`

Rule for Tier B:

- At most, treat them as optional language-color references in a later editorial phase.
- Do not use them to decide what the period means.
- Do not let them introduce a new identity claim or “this is who you are” line.

For Phase 1 adaptive period cards, the safest choice is to avoid Tier B entirely.

## 4. How Cards Should Reference Natal Personality

Adaptive cards should personalize the already-selected period meaning, not open a separate natal reading.

### Good rule

Use natal context only when it is explicitly connected to the current period trigger.

### Good example

“Sen zaten sözünü kolay harcamayan birisin; bu dönem o ölçülü tarafın daha seçilmiş bir cümleye dönüşüyor.”

Why this works:

- The personality note is short.
- It is tied to the current period meaning.
- It does not become the main story.

### Bad example

“Sen böyle bir insansın...”

Why this fails:

- It becomes a second profile reading.
- It makes a broad identity claim without current period evidence.
- It risks contradicting `semantic_focus_result`.

### Practical rule set

- Lead with the period.
- Use natal personality only as a supporting sentence or sub-line.
- Keep the personalization narrow and triggered.
- Prefer “this period activates a familiar way of moving” over “you are fundamentally X.”

## 5. How Dispositor Chains Should Be Used

Dispositor and ruler routes are valuable, but they are internal structure, not public prose.

### When to use them

Use dispositor / ruler routes when:

- the current period trigger clearly routes through a natal planet or house pattern,
- that route helps explain *how* the selected period meaning shows up,
- the route strengthens an already-supported semantic focus.

### How to translate them

Technical:

“Saturn in Aries disposited by Mars.”

Public:

“Harekete geçme tarafın sözünü de hızlandırıyor; bu dönem o ilk tepkiyi daha seçilmiş bir cümleye çevirmeyi öğreniyorsun.”

### Rules

- Never surface raw “dispositor” or “house ruler route” terminology.
- Translate structure into behavior, timing, or lived scene.
- Use routes to explain pressure flow, not to show technical astrology competence.

## 6. How `personality_imprint` / `profile_v8` Should Be Used

### Are they canonical enough?

No. They are too rendered and downstream to act as semantic authority for period cards.

### Are they legacy/rendered enough that they should not feed meaning?

Yes. They are display-oriented enough that using them as upstream meaning sources would create semantic drift.

### Can they still help?

Possibly, but only in a weak role:

- voice-color inspiration
- optional editorial softening
- fallback phrasing review

### Phase 1 recommendation

Do not use `personality_imprint` or `profile_v8` as source inputs for adaptive period cards.

If they are used later, they should be behind a one-way rule:

`canonical card meaning -> optional language color`

never:

`profile text -> card meaning`

## 7. No-Contradiction Guardrails

Adaptive period cards need strict guardrails so they do not become a hidden second profile system.

### Required rules

- A card cannot contradict `period_core.semantic_focus.suppressed_meanings`.
- A card cannot contradict `active_life_chapter.suppressed_surface_readings` when a life chapter is active.
- A card cannot introduce a personality claim unsupported by canonical natal evidence.
- A card cannot become a second natal profile reading.
- A card cannot use `profile_v8`, `personality_imprint`, `meaning_graph_v1_1`, or projection outputs as upstream authority.
- A card must trace to:
  - selected period meaning
  - period evidence (`featured_events`, `canonical_period_spine`, `natal_activation_context`)
  - canonical natal context

### Safe trace rule

Every adaptive card should be explainable as:

“This period means **X** because the current semantic owner selected **X**, and that lands in the natal architecture through **Y**.”

If the sentence cannot be completed with real period evidence and real natal evidence, the card should not render.

## 8. Recommended Architecture

### Options

- **A) only `period_core` runtime fields**
- **B) `period_core` + `canonical_natal_state`**
- **C) `period_core` + a new `NatalContextForPeriodCards` projection**
- **D) something else**

### Recommendation

The safest path is **C**.

Why not A:

- `period_core` already has strong evidence, but not enough shaped natal context for stable adaptive cards across all cases.

Why not direct B:

- `period_core + canonical_natal_state` is semantically correct, but too raw and too easy to misuse across many rendering points.

Why C is better:

- It keeps authority canonical.
- It avoids direct coupling to many deep natal structures.
- It creates a narrow, testable, non-authoritative projection specifically for card personalization.

### Recommended contract

`NatalContextForPeriodCards` should be a *projection*, not a meaning engine.

Suggested content:

- `semantic_owner_ref`
  - selected meaning id / meaning family / source
- `period_anchor`
  - primary domain
  - secondary domains
  - semantic suppression list
- `event_evidence`
  - event ids
  - derived context summaries
  - connected points
  - motifs
- `natal_hook_context`
  - canonical period spine target node
  - matched hook ids
  - top hook ids
- `natal_structure_context`
  - chart spine line refs
  - promise refs
  - contradiction refs when activated
  - translated route hints from dispositor / ruler chains
- `life_chapter_context`
  - renderer handoff
  - natal architecture anchor
  - scene priority
  - only when life chapter exists

This contract should only **project** already-selected meaning into natal context. It should not perform fresh semantic arbitration.

## 9. Good / Bad Natal Personalization Examples

### Good

- “Normalde içerde tuttuğun şeyi hemen açmayan bir tarafın var; bu dönem güveni korurken neyi paylaşacağını daha seçili söylemen gerekiyor.”
- “Sen zaten ritmini kolay bozmayan birisin; bu dönem o tarafın daha net sınır çizmek için çalışıyor.”
- “Kendi yönünü önce içeride netleştirmen gereken bir yapı var; bu dönem o iç netlik dışarıdaki duruşunu daha fazla etkiliyor.”

### Bad

- “Sen derin, kontrollü, mesafeli bir insansın.”
- “Aslında kişiliğinin özü bu.”
- “Hayatın boyunca böyle çalışıyorsun.”
- “Haritanda Mars Satürn’ü disposit ediyor, bu yüzden...”

## 10. Implementation Phases

### Phase 0 — contract discipline

- Freeze the authority chain:
  - `semantic_focus_result` remains owner
  - cards only project it
- Decide the exact `NatalContextForPeriodCards` schema

### Phase 1 — canonical card context projection

- Build `NatalContextForPeriodCards` from:
  - `period_core`
  - `CanonicalNatalStateV1`
  - `canonical_natal_activation`
  - event `derived_context`
  - event `natal_promise` when available
- No Tier B profile/projection inputs

### Phase 2 — adaptive card rendering

- Render `period_signal_lines_v1` / expandable cards from:
  - `period_reading_v1`
  - `NatalContextForPeriodCards`
- Keep card copy subordinate to the period semantic owner

### Phase 3 — optional editorial softening

- If needed, test whether tiny amounts of Tier B voice color help readability
- Keep this one-way and strictly non-authoritative

## Final Recommendation

Adaptive period cards should not read directly from `profile_v8`, `personality_imprint`, or projection surfaces. They should be powered by a narrow canonical/evidence projection that starts from the already-resolved period meaning and personalizes it through real natal structure.

The safest path is:

`active_life_chapter`
→ `semantic_focus_result`
→ `chapter_priority`
→ `composer_plan`
→ `period_reading_v1`
→ `NatalContextForPeriodCards`
→ `period_signal_lines_v1 / adaptive cards`

That keeps the period owner singular, the natal context traceable, and the future card layer adaptive without becoming a second interpretation engine.
