# POST_FALLBACK_DENSITY_REVIEW

## Scope

This review covers the non-LifeChapter fallback density fix for `period_reading_v1`.

Source of truth for the root cause:

- `backend/tests/_artifacts/p0_diagnostics/live_route_compression_trace.md`

Fix intent:

- keep `semantic_focus_result`
- keep Tier-1 LifeChapter guided outputs unchanged
- stop non-LifeChapter `period_voice_policy` semantic focus from fully overriding richer event-aware fallback seeds

## Root Cause Recap

Before this fix, non-LifeChapter semantic focus from `period_voice_policy` entered the semantic-focus-guided path too aggressively.

That caused rich fallback seeds to be replaced by generic abstraction lines:

```text
Bu dönem dikkatini tek bir hatta topluyor.

Küçük görünen anlar alttaki daha büyük meseleyi görünür kılıyor.

Bunu daha sahipli bir çizgiye yerleştiriyorsun.
```

The result was:

- generic
- date-insensitive
- under 200 chars
- weaker than the available featured event and manifestation context evidence

## What Changed

Renderer routing now distinguishes two cases:

1. `life_chapter` semantic focus
- still allowed to fully guide / override prose
- Tier-1 Aries / Cancer / Nodal outputs remain chapter-owned

2. `period_voice_policy` semantic focus with no active life chapter
- semantic focus is still consumed
- composer stays `semantic_focus_guided`
- but semantic focus now acts as framing only
- richer event-aware fallback seeds remain the main prose source
- manifestation context and featured event evidence are appended into fallback, not replaced by generic scaffolding

## Before / After

### 2026-03-04

Before:

- source: live route artifact
- length: `157`

```text
Bu dönem dikkatini tek bir hatta topluyor.

Küçük görünen anlar alttaki daha büyük meseleyi görünür kılıyor.

Bunu daha sahipli bir çizgiye yerleştiriyorsun.
```

After:

- source: current runtime after the later real-chart LifeChapter wiring fix
- length: `353`
- mode: `semantic_focus_guided`
- composer semantic mode: `guided`
- semantic owner: `life_chapter`

```text
Kısa mesajlarda, yarım kalmış konuşmalarda ve hızlı cevap verme anlarında sözünün ağırlığı değişiyor.

Eskiden refleksle çıkan cümle seni hemen konumlandırıyor gibi gelebilirdi. Şimdi ilk tepkiyi son söz yapmak yerine, hangi cümlenin gerçekten sana ait olduğunu seçiyorsun.

Bu dönem sana daha çok konuşmayı değil, sözünü daha sahipli kurmayı öğretiyor.
```

Note:

- this date no longer exercises the non-LifeChapter fallback path
- it is still relevant as a regression control because the fallback density patch must not weaken the now-correct LifeChapter output

### 2026-04-22

Stage 1 — pre-fix (compression bug):

- source: live route artifact
- length: `157`

```text
Bu dönem dikkatini tek bir hatta topluyor.

Küçük görünen anlar alttaki daha büyük meseleyi görünür kılıyor.

Bunu daha sahipli bir çizgiye yerleştiriyorsun.
```

Stage 2 — post density-fix, pre quality-fix (still abstract + broken Turkish):

- source: live route artifact after the renderer-routing density fix
- length: `987`
- mode: `semantic_focus_guided`
- composer semantic mode: `guided_fallback`

```text
Yakın çevrendeki ses bu dönem daha görünür hale geliyor. Burada daha yavaş ama daha kalıcı bir çizgi oluşuyor. Bu dönem hayatının bir alanı daha görünür hale geliyor ve burada seçimini daha netleştirmen gerekiyor.

İlk bakışta görünen şey tek mesele değil; altında daha kişisel bir yön ayarı var. Sende zaten çalışan birkaç ayrı taraf var. Bu dönem onlar birbirini daha çok duyuyor. Bu tema küçük cümlelerin ağırlığı içinden büyüyor; küçük cümleler bile alttaki daha büyük meseleyi görünür kılabilir. Duruşun ve yönün test edilebilir. Netlik azalırken zihin boşlukları doldurmak isteyebilir; varsayım yerine somut veri toplamak iyi gelir. Bunu en çok kimlik ve durus alanında hissedebilirsin; etkisi para ve özdeğer tarafina da tasabilir.

Burada dikkat etmen gereken yer, küçük cümlelerin ağırlığı tarafında büyüyen tepkiyi bütün hikayenin yerine koymamak. Daha esnek ama dağılmayan bir yön duygusu kuruyorsun.

Farklı parçalarını aynı ritme almayı öğreniyorsun.
```

Stage 3 — first P0 fallback prose patch:

- source: live composer (`_semantic_enriched_fallback_plan` →
  `_build_period_reading_v1`) against the live `period_voice_policy`
  semantic focus for 2026-04-22 (h3 primary, h4 / h2 / h5 secondaries,
  target_planet_house = 1)
- length: `484` (>= 450 floor)
- block count: `4`
- mode: `semantic_focus_guided`
- composer semantic mode: `guided_fallback`
- semantic owner: `period_voice_policy` (life_chapter absent)

```text
Sana ait hissettiren alan bu dönem daha fazla görünür oluyor. Ev, iç güvenlik ya da yalnız kaldığında kurduğun düzen sadece arka plan gibi kalmıyor; kimliğini ve sınırını da etkiliyor.

Bu dönem onlar birbirini daha çok duyuyor. Yakın çevrendeki ses bu dönem daha görünür hale geliyor. Duruşun ve yönün test edilebilir.

Dikkat etmen gereken yer, ilk hissi sonuç sanıp süreci aceleye getirmek. Daha bütünlüklü bir yön kuruyorsun.

Daha esnek ama dağılmayan bir yön duygusu kuruyorsun.
```

Stage 4 — wave-2 fallback prose patch (current):

- source: live composer with the wave-2 changes (extra scaffold strips,
  chart-specific closer for h4+visible-axis combo, evidence-first
  mechanism).
- length: `481` (>= 450 floor)
- block count: `4`
- mode: `semantic_focus_guided`
- composer semantic mode: `guided_fallback`
- semantic owner: `period_voice_policy` (life_chapter absent)

```text
Sana ait hissettiren alan bu dönem daha fazla görünür oluyor. Ev, iç güvenlik ya da yalnız kaldığında kurduğun düzen sadece arka plan gibi kalmıyor; kimliğini ve sınırını da etkiliyor.

Duruşun ve yönün test edilebilir. Yakın çevrendeki ses bu dönem daha görünür hale geliyor.

Dikkat etmen gereken yer, ilk hissi sonuç sanıp süreci aceleye getirmek. Daha bütünlüklü bir yön kuruyorsun.

Bu sana içeride hissettiğin şeyle dışarıda gösterdiğin duruşu aynı hatta toplamayı öğretiyor.
```

Wave-2 deltas:

- **Mechanism evidence-first.** The second block now opens with the
  featured event's `interpretation.summary` ("Duruşun ve yönün test
  edilebilir.") and the transit-side scene supports it. The seed-derived
  "Sende zaten çalışan birkaç ayrı taraf var" / "Bu dönem onlar birbirini
  daha çok duyuyor" pair no longer leads.
- **Two more scaffold sentences stripped** in
  `_FALLBACK_SCAFFOLD_PHRASES`:
  - "Bu dönem onlar birbirini daha çok duyuyor" — orphan "onlar" reference
    when the anchor changes from the integration seed
  - "Daha esnek ama dağılmayan bir yön duygusu kuruyorsun" — interchangeable
    closer that recurred across cases
- **Chart-specific closer.** When the h4 inner-foundation anchor pairs
  with a visible-axis natal point (h1/7/10), `_fallback_chart_specific_closer`
  emits "Bu sana içeride hissettiğin şeyle dışarıda gösterdiğin duruşu
  aynı hatta toplamayı öğretiyor." instead of the generic seed closer.
  Falls back to "Bu sana neyin gerçekten sana ait olduğunu daha sakin
  ayırmayı öğretiyor." when no visible-axis is present.

What changed in stage 3:

- **Primary-domain anchor leads.** When `secondary_domains` includes
  `house_4`, the fallback now opens with the inner-foundation
  ("sana ait hissettiren alan / iç güvenlik / yalnız kaldığında / kimliğini
  ve sınırını") composite anchor instead of the transit-side scene
  ("yakın çevrendeki ses").
- **Transit scene demoted to support.** The h3 phrase now appears later
  in the second block as evidence, not as the lead.
- **Scaffold sentences stripped** in `_semantic_enriched_fallback_plan`
  before any anchor / focus / chart-hint is layered in. Forbidden phrases
  centralised in `_FALLBACK_SCAFFOLD_PHRASES`:
  - "Burada daha yavaş ama daha kalıcı bir çizgi oluşuyor"
  - "Bu dönem hayatının bir alanı daha görünür hale geliyor"
  - "Hayatının bir alanı daha görünür hale geliyor" (softened variant)
  - "İlk bakışta görünen şey tek mesele değil"
  - "Sende zaten çalışan birkaç ayrı taraf var"
  - "Bu tema küçük cümlelerin ağırlığı içinden büyüyor"
  - "Bu konu boşuna buradan açılmıyor"
  - "küçük cümleler bile alttaki daha büyük meseleyi görünür kılabilir"
- **Turkish diacritics fixed at source + safety net.**
  - `app/transit/interpret/where.py` ASCII-only `HOUSE_LABELS_TR` /
    `ANGLE_LABELS_TR` / sentence templates rewritten with proper Turkish
    diacritics ("kimlik ve duruş", "para ve özdeğer", "ev ve iç güven",
    "kariyer ve görünürlük", …, "Bunu en çok …", "tarafına da taşabilir").
  - `app/transit/narrative/text_quality_tr._TR_WORD_FIXES` extended with
    the missing word fixes so any pass-through prose normalises:
    `durus`, `tarafina`, `tasabilir`, `tasimana`, `netlestirme`, `cabasini`,
    `yumusatip`, `yumusak`, `yumusatmak`, plus the few neighbouring
    inflections.
- **Tier-1 LifeChapter outputs unaffected.** All three Tier-1 hardcoded
  guided plans (`speech_authority`, `shared_emotional_territory`,
  `directional_self_definition`) bypass the fallback path, so chapter
  prose remains identical.

## Concrete Improvements

- `2026-03-04` and `2026-04-22` are no longer identical
- `2026-04-22` is `484` chars (>= `450` density floor), `4` blocks
- the old fallback scaffold is now actively stripped (not just softened):
  - no "Burada daha yavaş ama daha kalıcı bir çizgi"
  - no "Bu dönem hayatının bir alanı / Hayatının bir alanı"
  - no "İlk bakışta görünen şey tek mesele değil"
  - no "Sende zaten çalışan birkaç ayrı taraf var"
  - no "Bu tema küçük cümlelerin ağırlığı içinden büyüyor"
  - no "küçük cümleler bile alttaki daha büyük meseleyi görünür kılabilir"
- `period_voice_policy` semantic focus still contributes framing
- primary natal-side domain anchor leads the opening; transit-side scene
  becomes support
- `where.py` and any pass-through prose now normalise Turkish diacritics
  consistently — no `durus`, `tarafina`, `tasabilir`, `netlestirme`,
  `cabasini`, `yumusatip` in fallback prose

## Guardrail / Contract Status

- `period_reading_v1` remains the public surface
- block count remains `3-4`
- `full_text` still joins blocks with `\n\n`
- no event selection rewrite
- no daily rewrite
- no natal rewrite
- no PR-D scope change
- no Home wrapper change
- no architecture change — patch is contained to:
  - `app/transit/interpret/where.py` (diacritics at source)
  - `app/transit/narrative/text_quality_tr.py` (`_TR_WORD_FIXES` safety net)
  - `app/transit/narrative/astrolog_narrative_engine.py`
    (`_FALLBACK_SCAFFOLD_PHRASES`, `_FALLBACK_HOUSE_OPENINGS`,
    `_resolve_primary_anchor_house`, `_fallback_primary_anchor_sentence`,
    `_strip_fallback_scaffold_sentences`, rewired
    `_semantic_enriched_fallback_plan`)

## Validation Snapshot

Tests run after the wave-2 patch:

- `backend/tests/test_fallback_prose_quality.py`
  - `13 passed` (10 wave-1 + 3 wave-2)
- `backend/tests/test_astrolog_narrative_engine.py`
  - `34 passed`
- `backend/tests/test_period_reading_v1_contract.py`
  - `5 passed`
- `backend/tests/test_period_voice_policy.py`,
  `test_period_voice_policy_matrix_coverage.py`
  - `37 passed`
- `backend/tests/test_life_chapter_detector.py`,
  `test_life_chapter_contract.py`
  - `72 passed`
- `backend/tests/test_text_quality_tr.py`,
  `test_phrase_lib_tr.py`
  - `39 passed`
- combined fast suite:
  - `200 passed`
- transit narrative integration suite (slower):
  - `backend/tests/test_transit_narrative_assembler.py` `5 passed`
  - `backend/tests/test_transit_narrative_public_payload.py` `28 passed`
  - total `33 passed`

Assertions now covered (via `test_fallback_prose_quality.py`):

- `tr_normalize` fixes the `where.py` house-label sentence
- `tr_normalize` fixes the `upper_meaning` neptune.square line
- scaffold-strip helper drops every entry in `_FALLBACK_SCAFFOLD_PHRASES`
- 2026-04-22-shaped fallback opens with a primary-domain anchor
  (`sana ait`, `iç güven`, `ev,`, `yalnız kaldığında`, `kimliğini`, `sınır`)
- 2026-04-22-shaped fallback `full_text` does not contain
  `Bu dönem hayatının bir alanı`, `İlk bakışta görünen şey tek mesele değil`,
  `Sende zaten çalışan birkaç ayrı taraf var`, or
  `Burada daha yavaş ama daha kalıcı bir çizgi`
- 2026-04-22-shaped fallback `full_text` carries no forbidden ASCII
  Turkish (`durus`, `tarafina`, `tasabilir`, `netlestirme`, `cabasini`,
  `yumusatip`)
- 2026-04-22-shaped fallback `full_text` length `>= 450`
- 2026-04-22-shaped fallback retains `3-4` blocks and
  `semantic_mode = guided_fallback`
- transit-side h3 scene does not lead the opening sentence
- **wave-2:** `Bu dönem onlar birbirini daha çok duyuyor` and
  `Daha esnek ama dağılmayan bir yön duygusu kuruyorsun` are no longer
  in fallback prose
- **wave-2:** h4 + visible-axis combo emits the chart-specific
  "içeride hissettiğin şeyle dışarıda gösterdiğin duruşu aynı hatta
  toplamayı öğretiyor" closer
- **wave-2:** mechanism (second block) leads with the featured-event
  evidence sentence (`Duruşun ve yönün test edilebilir.`) rather than
  the seed-derived "Sende zaten çalışan…" scaffold

## Remaining Gaps

- Fallback prose is now denser, anchor-led and chart-specific in the closer,
  but still not as fully chart-specific as Tier-1 LifeChapter prose. That
  remains a downstream concern handled when a Tier-1 chapter is detected
  and a renderer-mode upgrade is in scope.
- `period_voice_policy_version` is still empty in `_period_story_debug` for
  fallback cases — the LifeChapter→renderer voice handoff stamp is not
  wired in this PR (out of scope; would touch wiring boundary the patch
  brief explicitly excluded).

## Net Result

The compression bug is fixed at the renderer routing level:

- non-LifeChapter semantic focus no longer erases richer fallback seeds
- semantic focus remains part of the chain
- `period_reading_v1` stays organic and additive
- Tier-1 guided outputs do not regress
