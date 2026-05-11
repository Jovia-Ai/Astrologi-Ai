# POST_PR_D_V1_FLAG_REVIEW

## Summary

- `LIFE_CHAPTER_PRIORITY_ENABLED=false` iken post-organic davranış korunuyor.
- `LIFE_CHAPTER_PRIORITY_ENABLED=true` iken Tier-1 allowed chapter types için `period_core.chapter_priority.applied=true` oluyor.
- Priority hedefi legacy alanlar değil; zincir hâlâ `active_life_chapter -> semantic_focus -> composer_plan -> period_reading_v1 -> legacy shadows`.
- `period_reading_v1` Tier-1 case’lerde aynı organic realization surface olarak kalıyor; flag bu PR’da selection veya prose family’yi değil, ownership priority marker’ını değiştiriyor.
- `featured_events` korunuyor; flag on durumunda semantic role `evidence_support` olarak işaretleniyor.
- `structural_natal_chapter` explicit olarak dışarıda; no-chapter fallback bozulmuyor.

## Extraction Note

- `backend/scripts/dev/extract_reasoning_outputs.py` rerun edildi.
- Extraction script period prose sample’larını hâlâ renderer-level context üzerinden üretiyor.
- `chapter_priority` delta değerlendirmesi ayrıca gerçek runtime `build_period_core(...)` path’i üzerinden doğrulandı.
- Bu review doc flag delta için runtime-core truth’u baz alır.

## Flag Off

### Expected

- `semantic_focus.source` Tier-1 chapter case’lerde zaten `life_chapter`.
- `period_reading_v1` ve legacy shadow fields mevcut.
- `chapter_priority.enabled=false`
- `chapter_priority.applied=false`
- event cards owner olmaya devam ediyor görünse de explicit chapter-priority owner marker yok.

### Observed

| Case | semantic_focus.source | chapter_priority.reason | period_reading_v1 |
|---|---|---|---|
| Aries 3rd Saturn return | `life_chapter` | `flag_disabled` | present |
| Cancer 8th Saturn return | `life_chapter` | `flag_disabled` | present |
| Nodal activation | `life_chapter` | `flag_disabled` | present |

## Flag On

### Expected

- Allowed Tier-1 cases:
  - `saturn_return`
  - `nodal_return`
  - `nodal_activation`
- `chapter_priority.applied=true`
- `event_cards_role=evidence_support`
- `period_reading_v1` same public realization surface
- legacy fields same composer chain’den türetilmiş shadow olarak kalır

### Observed

| Case | chapter_type | chapter_priority.applied | event_cards_role | featured_events semantic_role |
|---|---|---|---|---|
| Aries 3rd Saturn return | `saturn_return` | `true` | `evidence_support` | `evidence_support` |
| Cancer 8th Saturn return | `saturn_return` | `true` | `evidence_support` | `evidence_support` |
| Nodal activation | `nodal_activation` | `true` | `evidence_support` | `evidence_support` |

## Case Review

### Aries 3rd Saturn Return

#### Flag Off

`chapter_priority`
```json
{
  "enabled": false,
  "applied": false,
  "owner": "life_chapter",
  "chapter_type": "saturn_return",
  "chapter_id": "lc:saturn_return:evt-saturn-return-aries-3",
  "semantic_focus_source": "life_chapter",
  "scope": "pr_d_v1_tier_1",
  "event_cards_role": "selected_owner",
  "reason": "flag_disabled"
}
```

`period_reading_v1.full_text`
```text
Kısa mesajlarda, yarım kalmış konuşmalarda ve hızlı cevap verme anlarında sözünün ağırlığı değişiyor.

Eskiden refleksle çıkan cümle seni hemen konumlandırıyor gibi gelebilirdi. Şimdi ilk tepkiyi son söz yapmak yerine, hangi cümlenin gerçekten sana ait olduğunu seçiyorsun.

Bu dönem sana daha çok konuşmayı değil, sözünü daha sahipli kurmayı öğretiyor.
```

#### Flag On

`chapter_priority`
```json
{
  "enabled": true,
  "applied": true,
  "owner": "life_chapter",
  "chapter_type": "saturn_return",
  "chapter_id": "lc:saturn_return:evt-saturn-return-aries-3",
  "semantic_focus_source": "life_chapter",
  "scope": "pr_d_v1_tier_1",
  "event_cards_role": "evidence_support",
  "reason": "eligible_tier1_life_chapter"
}
```

`featured_events`
```json
[
  {
    "event_id": "evt-saturn-return-aries-3",
    "semantic_role": "evidence_support",
    "semantic_owner": "life_chapter"
  }
]
```

Delta:
- Prose meaning same kaldı.
- Explicit owner priority şimdi chapter-first.
- Event card owner değil, destek/evidence olarak işaretleniyor.

### Cancer 8th Saturn Return

#### Flag On

`chapter_priority`
```json
{
  "enabled": true,
  "applied": true,
  "owner": "life_chapter",
  "chapter_type": "saturn_return",
  "chapter_id": "lc:saturn_return:evt-saturn-return-cancer-8",
  "semantic_focus_source": "life_chapter",
  "scope": "pr_d_v1_tier_1",
  "event_cards_role": "evidence_support",
  "reason": "eligible_tier1_life_chapter"
}
```

`period_reading_v1.full_text`
```text
Mahrem konuşmalarda ve birlikte taşınan yüklerde neyin ortak, neyin tek başına kaldığı daha görünür oluyor.

Bazı şeyleri içeride tutmak seni güvende hissettirmiş olabilir. Ama güvenin sadece susarak değil, neyi paylaşacağını ve hangi sınırın sana ait olduğunu söyleyerek de kurulabileceğini görüyorsun.

Bu sana hem paylaşılanı taşıyan hem özel alanı koruyan daha dayanıklı bir yakınlık kurduruyor.
```

Observed:
- `semantic_focus.selected_meaning=shared_emotional_territory`
- `semantic_focus.primary_domain=trust_transformation`
- prose same organic flow üzerinden geliyor
- legacy fields dolu ve same composer chain shadow olarak kalıyor

### Nodal Activation

#### Flag On

`chapter_priority`
```json
{
  "enabled": true,
  "applied": true,
  "owner": "life_chapter",
  "chapter_type": "nodal_activation",
  "chapter_id": "lc:nodal_activation:evt-nodal-activation",
  "semantic_focus_source": "life_chapter",
  "scope": "pr_d_v1_tier_1",
  "event_cards_role": "evidence_support",
  "reason": "eligible_tier1_life_chapter"
}
```

`period_reading_v1.full_text`
```text
Yan yana dururken kendi sözünü ne kadar ayarladığını daha net fark ediyorsun.

İlişkiyi korumak için kendini kısmana gerek kalmadan, yönünü daha açık söylemeyi öğreniyorsun. Bu kopmak değil; onayın içinde erimeden kendi çizgini de masada tutmak.

Bu dönem sende onay arayışına çökmeyen daha doğrudan bir yön duygusu kuruyor.
```

Observed:
- `generic self/other balance` public prose’a geri dönmüyor
- chapter-first priority explicit hale geliyor
- realization surface hâlâ `period_reading_v1`

## Excluded Control

### Structural T-square

`chapter_priority`
```json
{
  "enabled": true,
  "applied": false,
  "owner": "life_chapter",
  "chapter_type": "structural_natal_chapter",
  "chapter_id": "lc:structural:t_square",
  "semantic_focus_source": "life_chapter",
  "scope": "pr_d_v1_tier_1",
  "event_cards_role": "selected_owner",
  "reason": "excluded_chapter_type"
}
```

Observed:
- even injected high-confidence structural chapter does not become owner
- exclusion guard works
- fallback period output still exists

Risk note:
- injected structural fake chapter still lets `semantic_focus.source=life_chapter` happen upstream if manually forced
- PR-D guard prevents ownership promotion, which is the required behavior for v1

## Fallback Control

### No Active Chapter

`chapter_priority`
```json
{
  "enabled": true,
  "applied": false,
  "owner": "life_chapter",
  "chapter_type": "",
  "chapter_id": "",
  "semantic_focus_source": "canonical_period_spine",
  "scope": "pr_d_v1_tier_1",
  "event_cards_role": "selected_owner",
  "reason": "no_active_life_chapter"
}
```

`period_reading_v1.full_text`
```text
Bu dönem dikkatini tek bir hatta topluyor.

Küçük görünen anlar alttaki daha büyük meseleyi görünür kılıyor.

Bunu daha sahipli bir çizgiye yerleştiriyorsun.
```

Observed:
- no crash
- fallback output valid
- non-LifeChapter prose hâlâ thinner than guided Tier-1 cases

## Public Surface Safety

- top-level public schema unchanged
- `period_core.period_reading_v1` remains additive
- legacy fields remain populated:
  - `period_opening`
  - `big_picture`
  - `mechanism`
  - `growth_edge`
  - `relational_or_life_expression`
  - `what_it_builds`
  - `core_story`
  - `upper_meaning`
- mobile için immediate change gerekmiyor; legacy teaser/fallback alanları duruyor

## Remaining Risks

- Event selection hâlâ event-first; PR-D v1 bu PR’da selection ranking’e dokunmuyor.
- Non-LifeChapter fallback prose still thinner; bu PR ownership/priority scope’unda bırakıldı.
- Extraction script hâlâ manual renderer path kullanıyor; chapter-priority truth için runtime `build_period_core(...)` path’i esas alınmalı.
- EN path preserve-safe; chapter priority semanticsi EN polish olarak zenginleştirmiyor.

## Decision Check

- flag default: safe
- flag off regression: safe
- flag on Tier-1 allowed cases: applied
- structural T-square: excluded
- public payload: additive-safe
- renderer surface: still `period_reading_v1`

Net sonuç:
- PR-D v1 behind-flag implementation behaves as intended.
