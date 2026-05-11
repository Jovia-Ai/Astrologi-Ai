# TRANSIT_OUTPUT_REVIEW

## Extraction Note

- Artifact bundle path: `backend/tests/_artifacts/transit_output_review_after_period_reading_v1/`
- Live Istanbul narrative payloads were built from the **current route components**: `build_transit_report -> _attach_internal_period_reasoning_state -> build_public_response -> build_transit_calendar -> _select_daily_and_period_event_cards -> build_daily_synthesis -> build_today_story_candidate`.
- This was used instead of a direct `/transit/narrative` full-path dump because the local checkout’s `payload_profile=home` wrapper currently degrades on the live route. Evidence file: `raw_transit_narrative_home_istanbul_2026-04-22.json`.
- Tier-1 cases are included separately as **fixture-based current runtime builder outputs** with `LIFE_CHAPTER_PRIORITY_ENABLED=true` so PR-D v1 ownership can be inspected clearly.

## Topline

- Current live Istanbul period outputs are **too compressed** after the route attaches internal period-reasoning state.
- The live `period_reading_v1.full_text` for both `2026-03-04` and `2026-04-22` collapses to the same 3 short paragraphs (`157` chars), even though the selected meaning/domain changes.
- Older March 4 public period prose was materially richer: old `core_story` length was `512`, old joined legacy period fields were `414`, current live `period_reading_v1` is `157`.
- The same current public builder **without** route-level internal reasoning attachment stays much richer: `712` chars on `2026-03-04`, `724` chars on `2026-04-22`. The compression happens on the live route-component path the app would use.
- Tier-1 fixture outputs remain strong. Aries/Cancer/Nodal cases still sound chapter-owned and keep their semantic anchors when `chapter_priority.applied=true`.
- Daily surfaces are much richer than the live period surface right now. The daily humanizer and `daily_synthesis.body` still carry more chart/event specificity than the current attached `period_reading_v1`.

## Case 1 / 2026-03-04

### Payload source

Route-component equivalent live Istanbul payload using current backend builders. Files:
- `raw_transit_narrative_istanbul_2026-03-04.json`
- `raw_transit_calendar_istanbul_2026-03-04.json`
- `compact_period_istanbul_2026-03-04.json`
- `compact_daily_istanbul_2026-03-04.json`

### period_reading_v1.full_text

Bu dönem dikkatini tek bir hatta topluyor.

Küçük görünen anlar alttaki daha büyük meseleyi görünür kılıyor.

Bunu daha sahipli bir çizgiye yerleştiriyorsun.

### period_reading_v1.blocks

- `hook`: Bu dönem dikkatini tek bir hatta topluyor.
- `unfolding`: Küçük görünen anlar alttaki daha büyük meseleyi görünür kılıyor.
- `growth`: Bunu daha sahipli bir çizgiye yerleştiriyorsun.

### Legacy fields

- `period_opening`: Bu dönem doğum haritandaki anlam ve yön hattını özellikle çalıştırıyor. Bu dönem dikkatini tek bir hatta topluyor.
- `mechanism`: Küçük görünen anlar alttaki daha büyük meseleyi görünür kılıyor.
- `growth_edge`: Otomatik tepkiyle seçilmiş cevap arasındaki farkı daha net görmek.
- `what_it_builds`: Bunu daha sahipli bir çizgiye yerleştiriyorsun.

### Debug ownership

- `semantic_focus.source`: `period_voice_policy`
- `semantic_focus.selected_meaning`: `reorientation`
- `semantic_focus.meaning_family`: `reorientation`
- `chapter_priority.enabled`: `False`
- `chapter_priority.applied`: `False`
- `chapter_priority.reason`: `flag_disabled`
- `composer_mode`: `semantic_focus_guided`
- `featured_events`: 5
- `b5a7004a12be4474d70579de2dbe14deef2dc3e6` | `None` | `None` | `Chiron` -> `Jupiter` | aspect `square` | houses `3`/`1`
- `f5e5e90860c7fb95136cc668eb62e45340bca24c` | `None` | `None` | `Saturn` -> `DSC` | aspect `square` | houses `3`/`None`
- `b66e8f9d1fe74f30df6447f63e57b0b2e99e1f19` | `None` | `None` | `Pluto` -> `South Node` | aspect `sextile` | houses `1`/`3`
- `0a40de18772071d6e2ca06709fe0e4437c0a0071` | `None` | `None` | `Uranus` -> `Mars` | aspect `trine` | houses `5`/`9`
- `4f022aff91a1e6ad15cdb8962a6fd660338d94bc` | `None` | `None` | `Neptune` -> `DSC` | aspect `square` | houses `3`/`None`

### Depth check

- Is the reading too short? **Yes. Severely.**
- Does it preserve the deeper period insight? **No.** The live attached surface drops the earlier March 4 identity/communication/Saturn-Neptune specificity.
- Does it feel more organic than the old 4-field version? **Flow-wise yes, content-wise no.** It reads as smoother but much thinner.
- Does it lose important astro/natal context? **Yes.** The specific 3rd/1st-house, Saturn/Neptune, Oğlak/Jüpiter bridge is gone from the visible period text.
- Is it generic or chart-specific? **Mostly generic.** The debug payload is chart-specific; the public reading is not.
- Does it feel SHOU v4-quality? **No.** It is below the old March artifact and below the current plain fallback builder output.
- Does it sound like a period reading, not a daily snippet? **Barely.** It is period-shaped, but so compressed that it risks reading like a teaser.

### UI readiness check

- If mobile consumed `period_reading_v1.full_text` today, would this be satisfying? **No.**
- Would `blocks[]` need visual treatment? **Yes, but visual treatment alone will not fix the depth loss.**
- Is `full_text` enough for the current period screen? **No.**
- Should we enrich `period_reading_v1` before mobile adoption? **Yes. Strongly.**

### Remaining issues

- too compressed
- too generic
- missing natal anchor
- legacy stronger than organic
- organic weaker than current plain fallback builder

## Case 2 / 2026-04-22

### Payload source

Route-component equivalent live Istanbul payload using current backend builders. Files:
- `raw_transit_narrative_istanbul_2026-04-22.json`
- `raw_transit_calendar_istanbul_2026-04-22.json`
- `compact_period_istanbul_2026-04-22.json`
- `compact_daily_istanbul_2026-04-22.json`

### period_reading_v1.full_text

Bu dönem dikkatini tek bir hatta topluyor.

Küçük görünen anlar alttaki daha büyük meseleyi görünür kılıyor.

Bunu daha sahipli bir çizgiye yerleştiriyorsun.

### period_reading_v1.blocks

- `hook`: Bu dönem dikkatini tek bir hatta topluyor.
- `unfolding`: Küçük görünen anlar alttaki daha büyük meseleyi görünür kılıyor.
- `growth`: Bunu daha sahipli bir çizgiye yerleştiriyorsun.

### Legacy fields

- `period_opening`: Bu dönem doğum haritandaki anlam ve yön hattını özellikle çalıştırıyor. Bu dönem dikkatini tek bir hatta topluyor.
- `mechanism`: Küçük görünen anlar alttaki daha büyük meseleyi görünür kılıyor.
- `growth_edge`: Otomatik tepkiyle seçilmiş cevap arasındaki farkı daha net görmek.
- `what_it_builds`: Bunu daha sahipli bir çizgiye yerleştiriyorsun.

### Debug ownership

- `semantic_focus.source`: `period_voice_policy`
- `semantic_focus.selected_meaning`: `integration_invitation`
- `semantic_focus.meaning_family`: `integration_invitation`
- `chapter_priority.enabled`: `False`
- `chapter_priority.applied`: `False`
- `chapter_priority.reason`: `flag_disabled`
- `composer_mode`: `semantic_focus_guided`
- `featured_events`: 5
- `254e183d13228b2952e4b5ee8a61abc7e721bef7` | `None` | `None` | `Chiron` -> `Neptune` | aspect `square` | houses `4`/`1`
- `c7e1654d0d711f1f6afcb5f762dda3b337e31e38` | `None` | `None` | `Saturn` -> `Fortune` | aspect `trine` | houses `3`/`7`
- `5c094e3bd122d16ecf5d3fe427057c9ed74a73f5` | `None` | `None` | `Sun` -> `ASC` | aspect `trine` | houses `4`/`None`
- `b66e8f9d1fe74f30df6447f63e57b0b2e99e1f19` | `None` | `None` | `Pluto` -> `South Node` | aspect `sextile` | houses `1`/`3`
- `4acb15849c62b153ce070571acef2f3a284a2f0b` | `None` | `None` | `Neptune` -> `Uranus` | aspect `sextile` | houses `3`/`1`

### Depth check

- Is the reading too short? **Yes.** Same compression pattern as March 4.
- Does it preserve the deeper period insight? **No.** The live text does not surface the stronger 4th/1st-house security/home/self-definition layer found in debug and in the plain fallback builder.
- Does it feel more organic than the old 4-field version? **Structurally yes, semantically no.**
- Does it lose important astro/natal context? **Yes.**
- Is it generic or chart-specific? **Mostly generic.**
- Does it feel SHOU v4-quality? **No.**
- Does it sound like a period reading, not a daily snippet? **Only minimally.**

### UI readiness check

- If mobile consumed `period_reading_v1.full_text` today, would this be satisfying? **No.**
- Would `blocks[]` need visual treatment? **Yes.**
- Is `full_text` enough for the current period screen? **No.**
- Should we enrich `period_reading_v1` before mobile adoption? **Yes.**

### Remaining issues

- too compressed
- too generic
- missing natal anchor
- legacy stronger than organic
- event-card mismatch

## Case 3 / Fixture Aries 3rd Saturn Return

### Payload source

Fixture-based current runtime builder output with `LIFE_CHAPTER_PRIORITY_ENABLED=true`. File:
- `fixture_period_aries_3rd_saturn_return.json`

### period_reading_v1.full_text

Kısa mesajlarda, yarım kalmış konuşmalarda ve hızlı cevap verme anlarında sözünün ağırlığı değişiyor.

Eskiden refleksle çıkan cümle seni hemen konumlandırıyor gibi gelebilirdi. Şimdi ilk tepkiyi son söz yapmak yerine, hangi cümlenin gerçekten sana ait olduğunu seçiyorsun.

Bu dönem sana daha çok konuşmayı değil, sözünü daha sahipli kurmayı öğretiyor.

### period_reading_v1.blocks

- `hook`: Kısa mesajlarda, yarım kalmış konuşmalarda ve hızlı cevap verme anlarında sözünün ağırlığı değişiyor.
- `unfolding`: Eskiden refleksle çıkan cümle seni hemen konumlandırıyor gibi gelebilirdi. Şimdi ilk tepkiyi son söz yapmak yerine, hangi cümlenin gerçekten sana ait olduğunu seçiyorsun.
- `growth`: Bu dönem sana daha çok konuşmayı değil, sözünü daha sahipli kurmayı öğretiyor.

### Legacy fields

- `period_opening`: Kısa mesajlarda, yarım kalmış konuşmalarda ve hızlı cevap verme anlarında sözünün ağırlığı değişiyor.
- `mechanism`: Şimdi ilk tepkiyi son söz yapmak yerine, hangi cümlenin gerçekten sana ait olduğunu seçiyorsun.
- `growth_edge`: İlk cevabı son söz gibi kullanmak yerine, ne söyleyeceğini ve hangi cümlenin gerçekten sana ait olduğunu seçebilmek.
- `what_it_builds`: Daha sahipli ve daha sorumlu bir konuşma biçimi.

### Debug ownership

- `semantic_focus.source`: `life_chapter`
- `semantic_focus.selected_meaning`: `speech_authority`
- `semantic_focus.meaning_family`: `speech_authority_maturation`
- `chapter_priority.enabled`: `True`
- `chapter_priority.applied`: `True`
- `chapter_priority.reason`: `eligible_tier1_life_chapter`
- `composer_mode`: `semantic_focus_guided`
- `featured_events`: 1
- `evt-saturn-return-aries-3` | `evidence_support` | `life_chapter` | `None` -> `None` | aspect `None` | houses `None`/`None`

### Depth check

- Is the reading too short? **No.**
- Does it preserve the deeper period insight? **Yes.** Speech authority / reflex-vs-owned-speech survives.
- Does it feel more organic than the old 4-field version? **Yes.**
- Does it lose important astro/natal context? **No major loss.**
- Is it generic or chart-specific? **Chart-specific.**
- Does it feel SHOU v4-quality? **Closer, though still not maximal density.**
- Does it sound like a period reading, not a daily snippet? **Yes.**

### UI readiness check

- If mobile consumed `period_reading_v1.full_text` today, would this be satisfying? **Mostly yes.**
- Would `blocks[]` need visual treatment? **Helpful but not required for basic satisfaction.**
- Is `full_text` enough for the current period screen? **Probably yes for a Tier-1 case.**
- Should we enrich `period_reading_v1` before mobile adoption? **Optional polish, not a blocker here.**

### Remaining issues

- organic stronger than legacy

## Case 4 / Fixture Cancer 8th Saturn Return

### Payload source

Fixture-based current runtime builder output with `LIFE_CHAPTER_PRIORITY_ENABLED=true`. File:
- `fixture_period_cancer_8th_saturn_return.json`

### period_reading_v1.full_text

Mahrem konuşmalarda ve birlikte taşınan yüklerde neyin ortak, neyin tek başına kaldığı daha görünür oluyor.

Bazı şeyleri içeride tutmak seni güvende hissettirmiş olabilir. Ama güvenin sadece susarak değil, neyi paylaşacağını ve hangi sınırın sana ait olduğunu söyleyerek de kurulabileceğini görüyorsun.

Bu sana hem paylaşılanı taşıyan hem özel alanı koruyan daha dayanıklı bir yakınlık kurduruyor.

### period_reading_v1.blocks

- `hook`: Mahrem konuşmalarda ve birlikte taşınan yüklerde neyin ortak, neyin tek başına kaldığı daha görünür oluyor.
- `unfolding`: Bazı şeyleri içeride tutmak seni güvende hissettirmiş olabilir. Ama güvenin sadece susarak değil, neyi paylaşacağını ve hangi sınırın sana ait olduğunu söyleyerek de kurulabileceğini görüyorsun.
- `growth`: Bu sana hem paylaşılanı taşıyan hem özel alanı koruyan daha dayanıklı bir yakınlık kurduruyor.

### Legacy fields

- `period_opening`: Mahrem konuşmalarda ve birlikte taşınan yüklerde neyin ortak, neyin tek başına kaldığı daha görünür oluyor.
- `mechanism`: Ama güvenin sadece susarak değil, neyi paylaşacağını ve hangi sınırın sana ait olduğunu söyleyerek de kurulabileceğini görüyorsun.
- `growth_edge`: Her şeyi içeride tek başına taşımak yerine, hangi yükün paylaşılacağını ve hangi sınırın sana ait olduğunu söyleyebilmek.
- `what_it_builds`: Paylaşılan güveni ve özel ağırlığı aynı cümlede tutabilen daha dayanıklı bir yakınlık.

### Debug ownership

- `semantic_focus.source`: `life_chapter`
- `semantic_focus.selected_meaning`: `shared_emotional_territory`
- `semantic_focus.meaning_family`: `shared_trust_maturation`
- `chapter_priority.enabled`: `True`
- `chapter_priority.applied`: `True`
- `chapter_priority.reason`: `eligible_tier1_life_chapter`
- `composer_mode`: `semantic_focus_guided`
- `featured_events`: 1
- `evt-saturn-return-cancer-8` | `evidence_support` | `life_chapter` | `None` -> `None` | aspect `None` | houses `None`/`None`

### Depth check

- Is the reading too short? **No.**
- Does it preserve the deeper period insight? **Yes.**
- Does it feel more organic than the old 4-field version? **Yes.**
- Does it lose important astro/natal context? **Not materially.**
- Is it generic or chart-specific? **Chart-specific.**
- Does it feel SHOU v4-quality? **Good, though still one layer short of the best handcrafted density.**
- Does it sound like a period reading, not a daily snippet? **Yes.**

### UI readiness check

- If mobile consumed `period_reading_v1.full_text` today, would this be satisfying? **Yes.**
- Would `blocks[]` need visual treatment? **Helpful.**
- Is `full_text` enough for the current period screen? **Yes.**
- Should we enrich `period_reading_v1` before mobile adoption? **Not for this case.**

### Remaining issues

- organic stronger than legacy

## Case 5 / Fixture Nodal Activation

### Payload source

Fixture-based current runtime builder output with `LIFE_CHAPTER_PRIORITY_ENABLED=true`. File:
- `fixture_period_nodal_activation.json`

### period_reading_v1.full_text

Yan yana dururken kendi sözünü ne kadar ayarladığını daha net fark ediyorsun.

İlişkiyi korumak için kendini kısmana gerek kalmadan, yönünü daha açık söylemeyi öğreniyorsun. Bu kopmak değil; onayın içinde erimeden kendi çizgini de masada tutmak.

Bu dönem sende onay arayışına çökmeyen daha doğrudan bir yön duygusu kuruyor.

### period_reading_v1.blocks

- `hook`: Yan yana dururken kendi sözünü ne kadar ayarladığını daha net fark ediyorsun.
- `unfolding`: İlişkiyi korumak için kendini kısmana gerek kalmadan, yönünü daha açık söylemeyi öğreniyorsun. Bu kopmak değil; onayın içinde erimeden kendi çizgini de masada tutmak.
- `growth`: Bu dönem sende onay arayışına çökmeyen daha doğrudan bir yön duygusu kuruyor.

### Legacy fields

- `period_opening`: Yan yana dururken kendi sözünü ne kadar ayarladığını daha net fark ediyorsun.
- `mechanism`: Bu kopmak değil; onayın içinde erimeden kendi çizgini de masada tutmak.
- `growth_edge`: Onayı korumak için yönünü yumuşatmak yerine, ilişkiyi silmeden daha doğrudan konuşabilmek.
- `what_it_builds`: Onay arayışına çökmeyen daha doğrudan bir yön duygusu.

### Debug ownership

- `semantic_focus.source`: `life_chapter`
- `semantic_focus.selected_meaning`: `directional_self_definition`
- `semantic_focus.meaning_family`: `nodal_direction_self_definition`
- `chapter_priority.enabled`: `True`
- `chapter_priority.applied`: `True`
- `chapter_priority.reason`: `eligible_tier1_life_chapter`
- `composer_mode`: `semantic_focus_guided`
- `featured_events`: 1
- `evt-nodal-activation` | `evidence_support` | `life_chapter` | `None` -> `None` | aspect `None` | houses `None`/`None`

### Depth check

- Is the reading too short? **No.**
- Does it preserve the deeper period insight? **Yes.**
- Does it feel more organic than the old 4-field version? **Yes.**
- Does it lose important astro/natal context? **Not materially.**
- Is it generic or chart-specific? **Chart-specific.**
- Does it feel SHOU v4-quality? **Good but still slightly cleaner than the densest target.**
- Does it sound like a period reading, not a daily snippet? **Yes.**

### UI readiness check

- If mobile consumed `period_reading_v1.full_text` today, would this be satisfying? **Yes.**
- Would `blocks[]` need visual treatment? **Helpful.**
- Is `full_text` enough for the current period screen? **Yes.**
- Should we enrich `period_reading_v1` before mobile adoption? **Optional polish only.**

### Remaining issues

- organic stronger than legacy

## Daily Surface Check

### 2026-03-04

- `daily_synthesis.headline`: Bugün özellikle kontrolü biraz gevşetmek kolay olmayabilir.
- `today_story_candidate.story_type`: `period_triggered_today`
- `daily_synthesis.body` length: `591`
- Read: the daily layer is much richer than the live period layer. It carries event-level natal anchors, house touchpoints, and a clear “period lands on today” bridge.

### 2026-04-22

- `daily_synthesis.headline`: Bugün ilk tepkinin tonunu ayarlamak gerilse de küçük fırsatı fark etmek tarafında kapı aralanabilir.
- `today_story_candidate.story_type`: `period_triggered_today`
- `daily_synthesis.body` length: `554`
- Read: same pattern. Daily still sounds like a real interpretation while the paired live period reading is reduced to a teaser.

## Current App-Facing Wrapper Risk

The direct live `/transit/narrative` `payload_profile=home` wrapper currently degrades to an empty public payload for the Istanbul sample used here.

- Evidence file: `raw_transit_narrative_home_istanbul_2026-04-22.json`
- Observed debug reason: `public_payload_exception`
- Raised error: `_home_daily_trigger_score` subtracts `datetime.date - str` through `_home_daily_candidate_ids(selected_date=transit_date)`.
- Resulting public payload: empty `period_core`, empty `daily_event_cards`, empty `period_event_cards`.

This does not block the builder-based inspection above, but it does matter for any claim about what the app would receive from the live home wrapper today.

## Old vs New

### Reference inputs used

- `backend/tests/_artifacts/transit_narrative_1996-12-28_07-10_istanbul_2026-03-04.json`
- `backend/tests/_artifacts/reasoning_output_review/POST_PR_4_1_REVIEW.md`
- `backend/tests/_artifacts/reasoning_output_review/POST_PR_ORGANIC_PERIOD_READING_REVIEW.md`
- `backend/tests/_artifacts/reasoning_output_review/POST_PR_D_V1_FLAG_REVIEW.md`

### Answers

- Did `period_reading_v1` become too short compared to older period prose?
  - **Yes.** Live Istanbul March 4 current attached output is `157` chars vs old March 4 `core_story=512` and old joined legacy period fields `414`.
- Did the new organic surface improve flow but reduce depth?
  - **Yes.** The live current attached output is cleaner structurally but materially worse semantically.
- Which fields still carry the richest interpretation?
  - For live current route-component cases: **not** `period_reading_v1`. The richest signal is spread across `daily_event_cards[].why_it_feels_this_way_tr`, `daily_synthesis.body`, `semantic_focus.debug.scene_translation_request`, and the older/plain fallback `core_story` shape.
  - For Tier-1 fixtures: `period_reading_v1` is already one of the richest fields.
- Should `period_reading_v1` use 3 blocks, 4 blocks, or allow expanded detail blocks?
  - **Allow expanded detail blocks.** A fixed 3-block surface is not enough for live fallback / period-voice-policy-owned cases. Keep 3 blocks for clean Tier-1 readings, but allow a 4th block or expanded unfolding/build detail when the selected meaning is route-derived rather than chapter-owned.

## Bottom Line

- Tier-1 chapter-owned organic readings look ready enough to inspect in UI.
- Current live Istanbul period outputs do **not** look ready for mobile adoption as the primary period surface.
- The regression is not “organic vs legacy” in the abstract. The problem is that the **live attached route path** currently compresses the organic surface into a generic 3-paragraph teaser, while the daily layer and Tier-1 fixtures remain much stronger.
