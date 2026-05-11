# Voice Runtime Clarification Report

Date: 2026-05-03  
Scope: `PR-0.5 Micro Runtime Clarification Tasks` before full voice migration/spec work.

## Goal

Bu rapor üç küçük ama kritik belirsizliği kapatır:

1. `text_quality_tr.py` gerçekten ne kadar chokepoint?
2. İki farklı style pack dosyasının rolü aynı mı, farklı mı?
3. Daily output'ta canonical reasoning ile legacy phrasing şu an nasıl karışıyor?

## A. `text_quality_tr.py` Chokepoint Analysis

### Finding

`text_quality_tr.py` canlı ve derin gömülü bir compatibility katmanı. Ama **tek başına bütün public transit/daily/period çıktılarının geçtiği evrensel chokepoint değil.**

### Observed public-path coverage

| Output family | `text_quality_tr.py` path | Coverage | Notes |
|---|---|---|---|
| Period story | `astrolog_narrative_engine -> text_quality_tr.tr_normalize(...)` | `yes` | Canonical period prose normalize ediliyor. |
| Event card | `deep_archetype_engine -> voice_engine_tr / text_quality_tr` | `yes` | Legacy event-card copy quality katmanı burada canlı. |
| Transit route normalize helpers | `transits.py -> tr_normalize_tree` | `partial` | Route-level cleanup var ama tüm prose üretimi burada yapılmıyor. |
| Interpret content/public builder | `content_loader.py`, `present/public_builder.py`, `archetype_engine.py` | `partial` | Support normalization. |
| Daily synthesis final prose | no direct import | `no` | `daily_synthesis.py` final headline/body/guidance metnini `text_quality_tr` olmadan kuruyor. |
| Calendar signal/micro summaries | no direct import | `no` | `signal_label_tr`, `summarize_daily_micro_copy`, route helper akışı ayrı. |

### Decision

```text
text_quality_tr.py = live compatibility chokepoint
ama universal public voice chokepoint değil
```

Bu yüzden vNext forbidden phrase / guardrail mantığını yalnız `text_quality_tr.py` içine koymak yeterli olmaz.

### Recommended guardrail architecture

Recommended shared file:

```text
backend/app/narrative/voice_guardrails_tr.py
```

Recommended role:

- shared forbidden phrase registry
- public-copy lint helpers
- optional runtime cleanup helpers
- canonical ve legacy layer tarafından ortak import edilebilir

### Injection recommendation

Karar:

```text
lint-only yetmez
runtime guardrail da gerekli
ama call-site adoption aşamalı olmalı
```

Önerilen sıra:

1. `PR-2`: ortak guardrail registry + lint tests
2. `PR-3`: runtime alignment plan decides exact call sites
3. `PR-4`: `text_quality_tr.py` ve canonical renderer path'lerine kontrollü injection

Sebep:

- `text_quality_tr.py` period/event tarafında güçlü chokepoint
- daily tarafı bunu hiç kullanmıyor
- erken, kör bir injection mixed path'i bozabilir

## B. Style Pack Double-Location Diff

Compared files:

- `backend/app/narrative/style_packs/tr_v26.py`
- `backend/app/style/style_pack_v26_tr.py`

### Finding

Bunlar aynı dosyanın kopyası değil.

### Role split

| File | Current shape | Imported by | Real role |
|---|---|---|---|
| `backend/app/narrative/style_packs/tr_v26.py` | büyük dict/token bank + helper | `backend/app/builders/narrative_binding.py` | legacy planner token pack |
| `backend/app/style/style_pack_v26_tr.py` | `StylePackV26TR` class renderer | `backend/app/builders/narrative_binding.py`, `backend/app/builders/narrative_renderer_v26.py` | runtime style renderer class |

### Decision

```text
Duplicate değiller.
Ama naming overlap var.
```

Bu yüzden şu sınıflama doğru:

- `backend/app/narrative/style_packs/tr_v26.py` -> `legacy_compat`
- `backend/app/style/style_pack_v26_tr.py` -> `renderer`

Şimdilik delete/deprecate kararı erken. Önce import ownership daha temiz hale getirilmeli.

## C. One Real Daily Output Trace

### Sample setup

Sample event:

- `Saturn opposition Venus`
- relationship domain
- house context `7`
- daily event id `evt_daily`
- canonical period spine line `relational_line`
- canonical hook `hook:relationship`

Built objects:

- `build_daily_synthesis(...)`
- `build_today_story_candidate(...)`
- `generate_daily_from_event(...)`

### Sample outputs

#### 1. Final daily prose now

`daily_synthesis.headline`

```text
Bugün özellikle iki tarafın ihtiyacını aynı anda taşımak seni arada bırakabilir.
```

`daily_synthesis.body`

```text
Bugün karşı tarafın tonu seni daha hızlı gerebilir. Bu en çok karşı tarafla arandaki çizgi tarafında; beklenti, sınır ve konuşulmamış başlıklarda görünür olur. Çünkü bu doğrudan yakınlık ve beğeni ölçün çizgine değiyor. O yüzden 7. ev, 8. ev başlığı da bu etkiye kolayca eşlik edebilir. Buradaki karşıt bir yandan seni, bir yandan karşı tarafı aynı anda konuşturabilir Bugün etkisi daha güçlü. Bu yeni bir başlık değil; içinde olduğun "Yakınlıkta Yeni Denge" dönemi bugün en çok karşı tarafla arandaki çizgi tarafına vuruyor.
```

`daily_synthesis.guidance`

```text
Yanıt vermeden önce neyi koruduğunu ayırt et.
```

#### 2. Canonical reasoning object now

`today_story_candidate`

- `story_type`: `period_triggered_today`
- `primary_spine_line`: `relational_line`
- `event_nature`: `boundary`
- `meaning_intent`: `trust_calibration`
- `rhetorical_frame`: `calibration`
- `manifestation_context.life_scene`: `anlaşma yapma biçimin`
- `reason_line_allowed`: `true`

#### 3. Legacy humanizer preview now

`daily_humanizer_tr.generate_daily_from_event(...)`

- `guidance_micro_tr`: `İlk tarafı final sanma.`
- `signal_label_tr`: `Bugün iki taraf konuşuyor.`

### Trace reading

```json
{
  "daily_output_sample_id": "saturn_opposition_venus_relational_daily",
  "final_text": {
    "headline": "Bugün özellikle iki tarafın ihtiyacını aynı anda taşımak seni arada bırakabilir.",
    "body": "Bugün karşı tarafın tonu seni daha hızlı gerebilir. Bu en çok karşı tarafla arandaki çizgi tarafında ...",
    "guidance": "Yanıt vermeden önce neyi koruduğunu ayırt et."
  },
  "source_trace": [
    {
      "span": "story_type=period_triggered_today, primary_spine_line=relational_line, event_nature=boundary, meaning_intent=trust_calibration, manifestation_context=anlaşma yapma biçimin",
      "source": "today_story_candidate",
      "role": "canonical_reasoning"
    },
    {
      "span": "headline/body/guidance main prose",
      "source": "daily_synthesis",
      "role": "renderer_assembler_and_meaning_writer"
    },
    {
      "span": "guidance_micro_tr='İlk tarafı final sanma.', signal_label_tr='Bugün iki taraf konuşuyor.'",
      "source": "daily_humanizer_tr",
      "role": "legacy_humanizer"
    }
  ],
  "canonical_share": "medium in reasoning, low in final prose ownership",
  "legacy_share": "high in visible daily phrasing"
}
```

### Interpretation

Bugünkü route'ta `today_story_candidate` **payload içinde canonical reasoning authority** ama final daily prose'u yazan ana katman henüz o değil.

Şu anki durum:

```text
canonical decides what kind of day this is
legacy/mixed layers still decide much of how the visible daily prose sounds
```

### Decision

Bu trace'e göre:

- `daily_synthesis.py` yalnız renderer değil; bugün hâlâ kısmen meaning owner davranıyor
- `daily_humanizer_tr.py` tamamen ölü değil; preview/signal/micro phrasing taşıyor
- `PR-2v` daily blind test beklentisi period kadar yüksek tutulmamalı
- `PR-5 Daily Today-ness Signal` ve sonrası gerçekten gerekli

## PR-0.5 Acceptance Check

- `text_quality_tr.py` hangi public path'lerden geçtiği raporlandı: `done`
- `voice_guardrails_tr.py` gerekliliği karara bağlandı: `yes, recommended`
- style pack double-location rol farkı raporlandı: `done`
- en az 1 daily sample trace çıkarıldı: `done`
- `daily_synthesis` renderer mı yoksa mixed meaning owner mı sorusu netleşti: `mixed, renderer-plus-meaning`

## Immediate Follow-Through

Bu raporun çıktıları doğrudan şu dosyalara yansıtılmalı:

- `docs/voice/voice_runtime_registry.yml`
- `docs/voice/SHOU_VOICE_VNEXT.md`
- `docs/system/voice_runtime_alignment_plan.md`
