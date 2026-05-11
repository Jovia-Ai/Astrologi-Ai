# POST PR-4.1 Review

Generated on 2026-05-05 after:

```bash
PYTHONHASHSEED=0 _ASTROLOGI_TESTS_PYTHONHASHSEED_PINNED=1 venv/bin/python -m pytest \
  tests/test_astrolog_narrative_engine.py \
  tests/test_period_semantic_focus.py \
  tests/test_life_chapter_detector.py \
  tests/test_period_voice_policy.py \
  tests/test_public_layered_output.py \
  tests/test_transit_narrative_public_payload.py -q

PYTHONPATH=backend backend/venv/bin/python backend/scripts/dev/extract_reasoning_outputs.py
```

## Topline

- `semantic_focus_result` is now being **consumed** by the renderer in high-confidence LifeChapter cases.
- `period_narrative_prose.debug.semantic_focus` is present and populated in the extraction artifacts.
- `composer_mode` is now `semantic_focus_guided` for:
  - Aries 3rd Saturn return + South Node overlap
  - Cancer 8th Saturn return
  - Nodal Aries/Libra activation
- `period_opening`, `mechanism`, `growth_edge`, and `what_it_builds` are materially less generic for those cases.
- Suppressed reading lists are now surfaced in debug as `suppressed_meanings_applied`.
- The extraction script still builds `PeriodStoryContext(...)` manually, so `period_core.semantic_focus` remains `null` **inside the extraction JSONs** even though it exists in the real runtime `build_period_core(...)` path from PR-SF1.
- Public payload shape remains additive/safe: no new top-level public contract break was introduced.

## Case 1 — Aries 3rd Saturn Return + South Node Overlap

### semantic_focus debug summary

- `source`: `life_chapter`
- `selected_meaning`: `speech_authority`
- `meaning_family`: `speech_authority_maturation`
- `confidence`: `0.7`
- `suppressed_meanings`: `generic communication difficulty`, `generic burden / heaviness`, `sibling conflict prediction`, `ordinary transit framing`
- `composer_mode`: `semantic_focus_guided`

### active_life_chapter.selected_meaning

> Koç 3. ev hattında söz ve zihinsel reflekslerin, düğüm ekseniyle birlikte, daha seçilmiş ve daha sorumlu bir forma yerleşmesi

### Before

- `period_opening`
  - `Asıl omurga burada yavaş ama kalıcı biçimde kuruluyor. Bu dönem hayatının bir alanı daha görünür hale geliyor ve senden daha bilinçli seçimler istiyor.`
- `mechanism`
  - `Bu dönem hikâye önce zihin ve iletişim tarafında başlıyor, sonra yavaş yavaş zihin ve iletişim alanına yayılıyor. Yani küçük görünen bir hareket daha büyük bir yön değişimini tetikleyebilir.`
- `growth_edge`
  - `Risk, ilk hissi sonuç sanıp süreci aceleye getirmek.`
- `what_it_builds`
  - `Bu dönem sende daha net seçim yapma kasını geliştiriyor.`

### After

- `period_opening`
  - `Kısa mesajlarda, yarım kalmış konuşmalarda ve hızlı cevap verme anlarında sözünün ağırlığı değişiyor. Hızlı tepkiyle gerçekten nerede durduğunu söylemek artık aynı şey değil.`
- `mechanism`
  - `Bu en çok kısa mesajlarda, yarım kalmış konuşmalarda ve hızlı cevap verme anlarında görünür. Eskiden refleksle çıkan söz, şimdi daha seçilmiş bir ağırlık ve daha sahipli bir duruş istiyor.`
- `growth_edge`
  - `İlk cevabı son söz gibi kullanmak yerine, ne söyleyeceğini ve hangi cümlenin gerçekten sana ait olduğunu seçebilmek.`
- `what_it_builds`
  - `Daha seçilmiş, daha sahipli ve daha sorumlu bir konuşma biçimi.`

### What changed

- Opening is no longer the old generic `Asıl omurga...` scaffold.
- `renderer_handoff.human_scene`, `core_contrast`, and `selected_meaning` are now clearly audible.
- The prose now sounds chapter-owned rather than event-track-default.

### Remaining renderer gap

- South Node overlap is implied through `eski/refleks` language, but still not explicitly rendered as an axis-overlap layer.
- `period_core.semantic_focus` is still absent in this extraction artifact because the script does not call the full runtime period-core builder.

## Case 2 — Cancer 8th Saturn Return

### semantic_focus debug summary

- `source`: `life_chapter`
- `selected_meaning`: `shared_emotional_territory`
- `meaning_family`: `shared_trust_maturation`
- `confidence`: `0.7`
- `suppressed_meanings`: includes `generic emotional regulation`, `body-rhythm reading`, `oversensitivity cliché`, `self-care simplification`, `generic vulnerability language`
- `composer_mode`: `semantic_focus_guided`

### active_life_chapter.selected_meaning

> Yengeç 8. ev hattında duygusal güvenlik, ortak yük ve derin bağ kurma biçiminin; birlikte taşınanla içeride tek başına taşınanı daha bilinçli ayıran dayanıklı bir forma yerleşmesi

### Before

- `period_opening`
  - `Asıl omurga burada yavaş ama kalıcı biçimde kuruluyor. Bu dönem neyi sahiplendiğin ve neyi ortak kullanacağın daha görünür hale geliyor.`
- `mechanism`
  - `Bu dönem hikâye önce derin bağlar ve güven tarafında başlıyor, sonra yavaş yavaş derin bağlar ve güven alanına yayılıyor. Yani küçük görünen bir hareket daha büyük bir yön değişimini tetikleyebilir.`
- `growth_edge`
  - `Risk, kişisel değeri başkasının onayına ya da başka birinin gücüne bağlamak.`
- `what_it_builds`
  - `Bu dönem sende ortak kaynakta sağlam sınır kurma kasını güçlendiriyor.`

### After

- `period_opening`
  - `Mahrem konuşmalarda, birlikte taşınan yüklerde ve sessiz duygusal borçlarda neyin ortak, neyin tek başına taşındığı daha belirgin oluyor.`
- `mechanism`
  - `Bu en çok mahrem konuşmalar, birlikte taşınan yükler ve sessiz sorumluluk anlarında görünür. İçeride tek başına tutulan ağırlık, şimdi güvenin ve paylaşılmış yükün adını istemeye başlıyor.`
- `growth_edge`
  - `Her şeyi içeride tek başına taşımak yerine, hangi yükün paylaşılacağını ve hangi sınırın sana ait olduğunu söyleyebilmek.`
- `what_it_builds`
  - `Paylaşılan güveni ve özel ağırlığı aynı cümlede tutabilen daha dayanıklı bir yakınlık.`

### What changed

- Cancer 8th is no longer collapsing into generic ownership or emotional-regulation language.
- `shared burden / trust / what is carried together vs alone` is now directly in the prose.
- This is the clearest PR-4.1 win versus the pre-pass generic fallback.

### Remaining renderer gap

- The prose still does not fully exploit `trust_axis_anchor` / `shared_vs_private_contrast` at maximum density.
- It is now substantially better, but still one pass short of the most vivid v4 reference quality.

## Case 3 — Nodal Activation / NN Aries / SN Libra

### semantic_focus debug summary

- `source`: `life_chapter`
- `selected_meaning`: `directional_self_definition`
- `meaning_family`: `nodal_direction_self_definition`
- `confidence`: `0.7`
- `suppressed_meanings`: `fated event prediction`, `generic self/other balance`, `fated relationship drama`
- `composer_mode`: `semantic_focus_guided`

### active_life_chapter.selected_meaning

> Koç 3. ev hattında başkalarına göre ayar verme refleksinden çıkıp daha doğrudan yön seçmeye alan açılması

### Before

- `period_opening`
  - `Asıl omurga burada yavaş ama kalıcı biçimde kuruluyor. Bu dönem hayatının bir alanı daha görünür hale geliyor ve senden daha bilinçli seçimler istiyor.`
- `mechanism`
  - `Bu dönem hikâye önce zihin ve iletişim tarafında başlıyor, sonra yavaş yavaş zihin ve iletişim alanına yayılıyor. Yani küçük görünen bir hareket daha büyük bir yön değişimini tetikleyebilir.`
- `growth_edge`
  - `Risk, ilk hissi sonuç sanıp süreci aceleye getirmek.`
- `what_it_builds`
  - `Bu dönem sende daha net seçim yapma kasını geliştiriyor.`

### After

- `period_opening`
  - `Yan yana dururken kendi sözünü nasıl ayarladığın değişiyor. İlişkiyi korumak için kendini kısmakla yönünü daha doğrudan söylemek artık aynı yerde durmuyor.`
- `mechanism`
  - `Bu en çok yan yana durduğun anlarda, kısa konuşmalarda ve yön seçimi gereken yerlerde görünür. Eskiden başkasına göre ayar veren refleks, şimdi daha doğrudan bir yön duygusu istiyor.`
- `growth_edge`
  - `Onayı korumak için yönünü yumuşatmak yerine, ilişkiyi silmeden daha doğrudan konuşabilmek.`
- `what_it_builds`
  - `Onay arayışına çökmeyen daha doğrudan bir yön duygusu.`

### What changed

- The renderer now carries the Aries/Libra directional contrast directly.
- It no longer reads like generic “balance” prose.
- Suppressed shallow node readings are clearly reflected in debug and not echoed in public text.

### Remaining renderer gap

- The nodal chapter still reads more cleanly than densely; it is correct but could become more texturally specific in a later composer polish pass.

## Daily sample

- `daily_synthesis_sample.json` remains outside the main PR-4.1 proof surface.
- No daily rewrite was attempted.
- `period_core.semantic_focus` remains `null` in that artifact because the sample is not rebuilt through the live runtime path that now carries additive semantic-focus state.

## Focus questions

### 1. Does `period_core.semantic_focus` exist?

- In the **real runtime period path**: yes, from PR-SF1.
- In the **current extraction script artifacts**: still `null`, because the dev extraction script still builds `PeriodStoryContext(...)` manually rather than using the full runtime `build_period_core(...)` path.

### 2. Is `semantic_focus.source == "life_chapter"` for high-confidence Tier-1 cases?

- Yes.
- Aries 3rd: `life_chapter`
- Cancer 8th: `life_chapter`
- Nodal Aries/Libra: `life_chapter`

### 3. Does period story debug include `semantic_focus`?

- Yes, and it is now populated rather than effectively absent.

### 4. Do `period_opening / mechanism / growth_edge / what_it_builds` now include selected meaning / meaning family / scene / handoff / suppressed-reading influence?

- Yes.
- The influence is strongest in:
  - Aries 3rd speech/response anchors
  - Cancer 8th shared burden / trust / private-vs-shared anchors
  - Nodal Aries/Libra direct-direction vs over-adjustment anchors

### 5. Are old generic openings still dominant?

- Not in the three high-confidence LifeChapter extraction cases above.
- The old `Asıl omurga...` opening has been displaced there.

### 6. Did public payload shape remain additive/safe?

- Yes.
- No broad public API rewrite was introduced.
- The change is renderer/composer behavior plus richer debug, not a breaking schema move.

## Net conclusion

PR-4.1 materially improves **semantic realization**.

PR-SF1 solved ownership visibility. PR-4.1 now makes that ownership audible in public prose for the core Tier-1 cases.

The remaining gap is no longer “renderer ignores chapter meaning”.

It is now:

- density
- nuance
- and full v4-level composer polish

That is a much smaller and cleaner problem than the pre-PR-4.1 state.
