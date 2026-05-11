# Live Route period_reading_v1 Compression Trace

## Scope

- Case A: live route/component-equivalent output already captured in:
  - `backend/tests/_artifacts/transit_output_review_after_period_reading_v1/raw_transit_narrative_istanbul_2026-03-04.json`
  - `backend/tests/_artifacts/transit_output_review_after_period_reading_v1/raw_transit_narrative_istanbul_2026-04-22.json`
- Case B: plain composer rerender from the same public `period_core` artifact via `build_period_story(...)`
- Goal: locate the exact point where rich available evidence collapses into the generic 157-char `period_reading_v1`

## Route Order

Confirmed current runtime order in [transits.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/transits.py):

1. `_build_transits_engine_response(...)`
2. `_attach_internal_period_reasoning_state(...)`
3. `build_public_response(...)`
4. `build_period_core(...)`
5. `build_period_story(...)`

`_attach_internal_period_reasoning_state(...)` runs **before** `build_public_response(...)`.

## What `_attach_internal_period_reasoning_state(...)` Actually Does

Confirmed in [transits.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/transits.py):

- injects `_canonical_natal_state`
- attempts to detect `_active_life_chapter`
- does **not** directly mutate `period_core`
- does **not** directly overwrite `period_reading_v1`

Conclusion:

- compression is **not** caused by `_attach_internal_period_reasoning_state(...)` mutating existing prose
- compression happens downstream when `build_public_response(...) -> build_period_core(...) -> build_period_story(...)` recomposes period prose

## Before / After `period_reading_v1.full_text`

### 2026-03-04

Route/component-equivalent output:

```text
Bu dönem dikkatini tek bir hatta topluyor.

Küçük görünen anlar alttaki daha büyük meseleyi görünür kılıyor.

Bunu daha sahipli bir çizgiye yerleştiriyorsun.
```

- length: `157`

Plain rerender from the same `period_core` artifact:

```text
Burada görünür olan şey tek bir hatta toplanıyor. Küçük cümlelerin ağırlığı tarafında birkaç ayrı ihtiyaç aynı anda söz istiyor.

İlk bakışta görünen şey tek mesele değil; altında daha kişisel bir yön ayarı var. Küçük cümlelerin ağırlığı tarafında bu çizgi pürüzsüz bir akış kadar rahat akmıyor; ayrı duran iki taraf aynı anda yer arıyor. Sürtünmenin kendisi çelişki değil; iki alan birbirini öğreniyor.

Asıl ayrım, küçük cümlelerin ağırlığı tarafındaki sürtünmeyi uyumsuzluk sanmamak. Ayrı duran ihtiyaçlar burada birbirini öğreniyor. Sende sürtünmeyi taşıyabilen daha keskin bir iç koordinasyon kuruyor.

sende olgunlaşma zaten parça parça değil, bütün bir düzen olarak çalışıyor.
```

- length: `683`

### 2026-04-22

Route/component-equivalent output:

```text
Bu dönem dikkatini tek bir hatta topluyor.

Küçük görünen anlar alttaki daha büyük meseleyi görünür kılıyor.

Bunu daha sahipli bir çizgiye yerleştiriyorsun.
```

- length: `157`

Plain rerender from the same `period_core` artifact:

```text
Aynı sıkılıkta taşınmayan şey önce burada belli oluyor. Bu dönem önce kendini nasıl anlattığın değişiyor, sonra bunun etkisi dışarıda nasıl göründüğüne yansıyor.

İlk bakışta görünen şey tek mesele değil; altında daha kişisel bir yön ayarı var. Sende zaten çalışan birkaç ayrı taraf var. Bu dönem onlar birbirine daha yakın duruyor. Bu tema daha çok sana ait hissettiren alan içinden görünür oluyor.

Asıl ayrım, sana ait hissettiren alan tarafında büyüyen tepkiyi bütün hikayenin yerine koymamak. Sende daha bütünlüklü bir yön kuruyor; içeride ayrı konuşan parçalar aynı cümlede toplanıyor.

sende büyüme zaten farklı taraflarını aynı hayata yerleştirme ihtiyacıyla çalışıyor.
```

- length: `677`

## Featured Events Availability

Both live route payloads already carry rich evidence:

- `featured_events` count on `2026-03-04`: `5`
- `featured_events` count on `2026-04-22`: `5`

Examples already present in the compressed payload debug:

- `2026-03-04`
  - `Chiron square Jupiter`
  - `Saturn square DSC`
  - `Pluto sextile South Node`
  - `Uranus trine Mars`
  - `Neptune square DSC`
- `2026-04-22`
  - `Chiron square Neptune`
  - `Saturn trine Fortune`
  - `Sun trine ASC`
  - `Pluto sextile South Node`
  - `Neptune sextile Uranus`

Conclusion:

- rich event evidence is already available at the time prose is built
- the problem is not missing event cards

## Semantic Focus Diff

### 2026-03-04

- `semantic_focus.source = period_voice_policy`
- `semantic_focus.selected_meaning = reorientation`
- `semantic_focus.primary_domain = gündelik konuşmalar`
- `semantic_focus.confidence = 0.7`
- `scene_translation_request.context_seed = "Bu tema daha çok gündelik konuşmalar içinden görünür oluyor."`

### 2026-04-22

- `semantic_focus.source = period_voice_policy`
- `semantic_focus.selected_meaning = integration_invitation`
- `semantic_focus.primary_domain = sana ait hissettiren alan`
- `semantic_focus.confidence = 0.7`
- `scene_translation_request.context_seed = "Bu tema daha çok sana ait hissettiren alan içinden görünür oluyor."`

Conclusion:

- semantic focus is **not identical**
- available semantic focus differs by date
- visible prose collapses anyway

## Composer Plan Diff

### Route/component-equivalent composer plan on both dates

The live payload stores the same generic plan for both dates:

```json
{
  "hook": "Bu dönem dikkatini tek bir hatta topluyor.",
  "scene_anchor": "",
  "core_contrast": "",
  "mechanism": "Küçük görünen anlar alttaki daha büyük meseleyi görünür kılıyor.",
  "growth_edge": "Otomatik tepkiyle seçilmiş cevap arasındaki farkı daha net görmek.",
  "what_it_builds": "Bunu daha sahipli bir çizgiye yerleştiriyorsun.",
  "closer": "Bunu daha sahipli bir çizgiye yerleştiriyorsun.",
  "legacy_prefix": "Bu dönem doğum haritandaki anlam ve yön hattını özellikle çalıştırıyor.",
  "semantic_mode": "guided"
}
```

### Plain rerender composer plan from same artifact

The same `period_core` can still yield differentiated, longer fallback plans:

- `2026-03-04`
  - hook: `Burada görünür olan şey tek bir hatta toplanıyor...`
  - mechanism: `Küçük cümlelerin ağırlığı tarafında bu çizgi pürüzsüz bir akış kadar rahat akmıyor...`
  - `semantic_mode = fallback`
- `2026-04-22`
  - hook: `Aynı sıkılıkta taşınmayan şey önce burada belli oluyor...`
  - mechanism: `Sende zaten çalışan birkaç ayrı taraf var...`
  - `semantic_mode = fallback`

Conclusion:

- the compression is happening **inside the guided composer path**
- the same artifact can still support richer prose if the fallback plan is allowed to work

## Exact Genericization Point

The rich text becomes generic in [astrolog_narrative_engine.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/astrolog_narrative_engine.py):

1. `build_period_story(...)` computes `semantic_focus_result`
2. `_compose_semantic_focus_guidance(...)` treats the non-LifeChapter `period_voice_policy` meanings as consumable semantic guidance because:
   - source is not `unknown`
   - confidence is `0.7`
3. `_compose_guided_fields(...)` generates generic override fields for:
   - `reorientation`
   - `integration_invitation`
4. `build_period_story(...)` then overrides:
   - `opening_raw`
   - `mechanism`
   - `growth_edge`
   - `what_it_builds`
   with those generic guidance fields
5. `_compose_period_plan(...)` enters `_guided_composer_plan(...)`
6. because the meaning key is not one of the hand-authored LifeChapter branches, the flow falls to `_semantic_enriched_fallback_plan(...)`
7. by that point the seeds are already generic, so the resulting `composer_plan` is generic too

This is the compression point.

## Does Public Builder Normalization Drop Richer Text?

No evidence of that in the current trace.

`build_public_response(...)` normalizes `period_core`, but:

- `_normalize_period_core_copy(...)` preserves nested `period_reading_v1`
- `_derive_period_reading_v1_from_legacy(...)` only runs if `period_reading_v1` is missing

In the captured live payload, `period_reading_v1` is already generic **before** any fallback derivation would matter.

## Suspected Root Cause

Primary root cause:

- non-LifeChapter `semantic_focus_result` from `period_voice_policy` is triggering the semantic-focus-guided path too aggressively
- that path currently replaces richer event-aware fallback seeds with generic semantic abstractions

Secondary contributing condition:

- `active_life_chapter` is absent in these live cases, so the renderer is not using chapter handoff anchors
- the remaining semantic guidance source is `period_voice_policy`, which is strong enough to switch the renderer into guided mode but not rich enough to carry public prose by itself

## Minimal Fix Proposal

Do not restore old segmented prose.

Minimal safe fix boundary:

1. keep `period_reading_v1` as the public surface
2. keep semantic focus ownership intact
3. change non-LifeChapter fallback behavior so that when:
   - `semantic_focus.source == period_voice_policy`
   - `active_life_chapter` is absent
   - rich `featured_events` / `derived_context` / manifestation context exist
   then the composer must preserve the richer fallback/event-aware plan instead of replacing it with generic semantic-focus scaffolding
4. `_attach_internal_period_reasoning_state(...)` should continue to enrich context only, not trigger a thinner recomposition path

## Suggested Regression Tests After Fix

- `test_live_route_preserves_rich_period_reading_2026_03_04`
- `test_live_route_period_readings_differ_by_date`
- assert `period_reading_v1.full_text` length `>= 350` when rich `featured_events` and semantic evidence exist
- assert concrete anchors from top events/domains are present
- assert `2026-03-04` and `2026-04-22` do not share a `4+` word verbatim fragment in `period_reading_v1.full_text`
- Tier-1 fixture outputs do not regress
