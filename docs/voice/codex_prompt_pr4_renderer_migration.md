# Codex Prompt — PR-4 Period Renderer Migration (Voice-Lead Approved Target)

**For:** Codex  
**From:** Sahra (voice lead)  
**Date:** 2026-05-04  
**Status:** Greenlit — human blind validation skipped per voice lead decision

---

## TL;DR

[handcrafted_period_validation_v4_final.md](/Users/sahradenizozdogan/Astrologi-Ai/docs/voice/handcrafted_period_validation_v4_final.md) artık **target voice reference**. Reviewer'a gitmeyecek, sonuç doc'u dolmayacak, decode edilmeyecek. Bu prose renderer'ın yaklaşması gereken kalite çizgisi.

PR-4 Period Renderer Migration bu reference üzerinden başlatılmalı. Renderer canonical chain'i (`valence_mode + intensity_mode + manifestation_context + rhetorical_frame + spine_line`) bu prose kalitesinde Türkçe metne çevirmeli.

## Karar Bağlamı

Voice lead validation cycle'ını skipping etti çünkü:

1. v4 prose yeterince specific: her chart kendi astrolojik mimarisinden konuşuyor.
2. Voice register stabilize oldu: friend-warm, grounded, mobile-paragraphed.
3. Reviewer cycle bu kalitenin altında signal verirdi: generic-feedback noise, specific-improvement signal'dan daha yüksek.

Sonuç: validation pack, target voice reference'a promote edildi.

## PR-4 Scope

### 1. Renderer migration target

[astrolog_narrative_engine.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/astrolog_narrative_engine.py) renderer'ı v4 reference'taki prose kalitesine yaklaşmalı.

Target mapping:

| Chart | Canonical chain | Target prose quality |
|---|---|---|
| 1 | Capricorn 1st stellium, Saturn maturation, `maturation/medium` | identity-as-construction tone |
| 2 | Pisces sun, Cancer rising, water-heavy, `release/light` | perception-as-gift tone |
| 3 | 10th house stellium, `recognition/light` | kimlik sahnesi tone |
| 4 | T-square, `integration/dense` | üç-parçalı basınç + apex release tone |
| 5 | Aries/Libra nodes, `momentum+integration` | directional NN/SN explicit tone |

### 2. Astrolog-lens guardrails

Renderer prose üretiminde şu yüzey-cliche astroloji banları uygulanmalı:

```python
ASTROLOGER_LENS_BANS = {
    "water_heavy": [
        "her şeyi taşıyor",
        "yükünü çekiyor",
        "duygusal olarak boğuluyor",
    ],
    "10th_house": [
        "kariyerinde başarı",
        "iş hayatında ilerleme",
        "profesyonel başarı",
    ],
    "t_square": [
        "iki ihtiyaç çatışıyor",
        "stres yaratan gezegenler",
        "zorluk çıkartan açı",
    ],
    "nodes": [
        "ben ve biz dengesi",
        "iki tarafı da kabul etmek",
        "denge bulmak",
    ],
}
```

### 3. Chart 5 nodal direction handling

Chart 5 için düğüm yönü fixture data'dan okunmalı.

- `NN Aries / SN Libra` ve `NN Libra / SN Aries` iki ayrı reading'dir.
- Generic `"ben/biz dengesi"` reading üretmek yasaktır.
- Direction yoksa renderer generic balance output'a düşmemeli.

### 4. Existing guardrails stay active

[voice_guardrails_tr.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/narrative/voice_guardrails_tr.py) registry v4 için de aktif kalır:

- hard ban: `mekanizma`, `aktivasyon`, `proses`
- pattern ban: `ritm`, `akış`, `tutmak`, `ardındaki`, `inşa edilen`, `yerleşen`
- construction ban: `"X yapmakla Y aynı şey değil"` ve hyper-formal interrogatives
- modality ban: `"olabilir"` mechanism/potential layer'da
- coaching ban: `yap`, `uygula`, `olmalı`, `lazım`

### 5. UX paragraph format

Output mobile-readable olmalı: `1-2 cümle paragraf`, single-block dump değil.

## Deprecated For This Cycle

Bu cycle'da dependency sayılmayacak ama silinmeyecek dosyalar:

- `handcrafted_period_blind_reviewer_pack_v3.md`
- `02_facilitator_brief.md`
- `handcrafted_validation_answer_key_v3.json`
- `validation_results_2026_05_xx.md`

Bunlar arşiv/template olarak kalır.

## Suggested Deliverables

1. renderer update
2. astrolog-lens guardrail extension
3. chart 5 nodal-direction routing
4. renderer snapshot tests
5. render-time lint pass

---

*PR-4 handoff prompt — v4 target reference active, validation cycle skipped.*
