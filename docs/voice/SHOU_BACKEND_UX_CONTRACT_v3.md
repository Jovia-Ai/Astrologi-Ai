# SHOU Backend — UX Contract v3

**Versiyon:** v3.0 · **Tarih:** 2026-04-21 · **Yerini alır:** v2.0
**Anchor Principle:** *This sees me.* (Not "accurate astro explanation")

---

## 0. Neden v3?

v2 teknik olarak iyiydi ama üç ürün-seviyesi meseleyi kaçırmıştı:

1. **Why_now astro-first yazılmıştı** ("Moon in your 3rd house") — kullanıcıdan tercüme bekliyordu. Voice spec'in kendi kuralını ihlal.
2. **Emotional intent label olarak kalıyordu** — UI driver'a bağlı değildi.
3. **Pattern sistemi over-engineered** — activation_level, transit_ref, scoring → false precision.

v3'te üç düzeltme ve **%20 daha kısa scope**. Substrate korunur (mevcut 2155-line `supporting_threads_builder.py`, `voice_profile_v2`, synastry PAIR_SIGNATURE engine pattern). Üstüne minimal katman.

---

## 1. Anchor Principle — "This Sees Me"

Her karar bu testten geçer:

| Soru | Evet ise... |
|---|---|
| Bu cümleyi okuyan "bu benim" mi der, yoksa "bu doğru" mu? | "bu benim" → kalsın; "bu doğru" → tekrar yaz |
| Kart üstündeki satırda astro teknik terimi var mı? | Varsa: kes, proof_raw chip'e taşı |
| Payload field'ı UI'da render edilmiyor mu? | Edilmiyorsa: underscore prefix (_debug), public contract'a sızmasın |
| Float scoring user-facing mi? | Asla — int enum veya boolean yeter |
| Intent sadece label mı? | Evetse: 3 UI driver'a bağla veya kaldır |

Bu checklist `docs/voice/this_sees_me_test.md` olarak commit edilir. Her content/feature PR'ı buradan geçer.

---

## 2. Thread Payload Shape — Final

Tek gerçek kaynak. Tek root object. Ayrı `patterns[]` / `slides[]` collection yok.

```json
{
  "id": "identity_mechanics",
  "name": "Sessiz değerlendirme",
  "name_source": "pattern",

  "opening": "İnsanlar seni yavaş sanıyor — oysa her kelimeyi iki kez tartıyorsun.",

  "why_now": "Bugün söyleyeceğin her cümleyi içinden bir kez daha geçiriyorsun. Normalde de öyle — ama bugün daha sık.",
  "why_now_active": true,

  "emotional_intent": "fark_edilme",
  "tone_accent": "lav",

  "proof_raw": "Satürn · 3. ev · Koç",
  "proof_orb": "5°35′",

  "body": "...",
  "detail_blocks": [
    {"text": "...", "kind": "mechanism"},
    {"text": "...", "kind": "cause"},
    {"text": "...", "kind": "shadow"},
    {"text": "...", "kind": "potential"}
  ],

  "illust_hints": {
    "opening": "balance",
    "mechanism": "wheel_house",
    "cause": "timeline",
    "potential": "expanding_circle"
  }
}
```

### Çıkarılanlar (v2'den)

- `activation_level` (float) — int enum priority yeter
- `transit_ref` (public) — internal debug'a git
- `voice_overrides` (complex dict) — intent → accent mapping yeter
- `slide_posts[]` (ayrı collection) — frontend projection yapar
- `patterns[]` (ayrı root object) — thread'in kendisi pattern

---

## 3. Pattern System — Minimum Viable

### 3.1 Tanım

Pattern, bir thread'in **isim + tone + intent seçimidir**. Ayrı obje değil — thread üzerine yazılan metadata.

- Pattern tetiklenirse: `name` → pattern adı, `tone_accent` → pattern'ın tonu, `emotional_intent` → pattern'ın etiketi
- Tetiklenmezse: `name` → section title fallback, `name_source: "section"`

### 3.2 Pattern kütüphanesi — ilk 25

Backend dosyası: `app/natal/narrative/natal_pattern_library.py`

Her pattern şu alanları taşır:

```python
{
    "id": "saturn_h3_quiet_assessment",          # snake_case unique
    "name": "Sessiz değerlendirme",              # TR, 2 kelime
    "opening": {                                  # hook, yüzleşme tonu
        "tr": "İnsanlar seni yavaş sanıyor — oysa her kelimeyi iki kez tartıyorsun.",
        "en": "People think you're slow — but you weigh every word twice.",
    },
    "emotional_intent": "fark_edilme",            # 5 label'dan biri
    "tone_accent": "lav",                         # intent'ten türer
    "trigger": {                                  # chart match kuralı
        "kind": "placement",
        "planet": "Saturn",
        "house": 3,
    },
    "priority_kind": "placement",                 # selection sıralaması için
    "section_binding": "identity_mechanics",     # hangi section thread'ine iliştirilir
    "why_now_triggers": [ ... ],                  # §4'te detay
}
```

### 3.3 Detection

```python
def detect_patterns(chart_data) -> List[Pattern]:
    matched = [p for p in PATTERN_LIBRARY if p.trigger.matches(chart_data)]
    matched.sort(key=lambda p: priority_rank(p, chart_data))
    return matched[:5]  # en fazla 5 pattern/chart
```

**Priority rank — int enum, float yok:**

| Rank | Kural |
|---|---|
| 1 | Tight aspect (orb < 1°) |
| 2 | Stellium (3+ planet aynı evde) |
| 3 | Angular placement (ev 1/4/7/10) |
| 4 | Tight aspect (orb 1°–3°) |
| 5 | Standart placement |
| 6 | Loose aspect (orb 3°–6°) |

Stable sort. Deterministik. Reproducible.

### 3.4 Pattern seçim limiti

Voice spec §08 uyarınca: **haritada max 5 pattern**. Voice spec ayrıca "3-5 ad" önerir. Üst sınır 5 hard cap.

---

## 4. Why Now — Human-First, 2-3 Trigger

### 4.1 Core Principle

**Start from user feeling, not astro event.**

| ❌ ASTRO-FIRST (v2 hatalı) | ✅ HUMAN-FIRST (v3) |
|---|---|
| "Moon is in your 3rd house" | "Today your mind is more active, conversations feel heavier" |
| "Venüs 11. evden geçiyor" | "Bu hafta beğendiğin bir şey başkasına da dokunuyor" |
| "Mercury retrograde" | "Bu hafta bir şey hissetmene fırsat kalmadan zihnin 'dur, bir bakayım' diyor" |

Astrolojik açıklama **varsa** sadece proof_raw / slide-ref-tag / debug log'da yaşar. why_now kart üstünde **duygu cümlesi**.

### 4.2 Trigger Tipleri (3 — scoring yok, rule-based match)

| Tip | Nasıl tetiklenir | Örnek pattern |
|---|---|---|
| `transit_through_house` | Hızlı planet (Moon/Sun/Mercury/Venus/Mars), pattern'ın evinden geçiyor | Saturn 3rd — Moon transits 3rd |
| `transit_to_pattern_body` | Hızlı planet, pattern'ın ana gezegenine aspect yapıyor (orb < 6°) | Sun sq Saturn — today's Moon conjuncts Sun |
| `transit_state` | Retrograde / sign ingress / station | Moon sq Mercury — Mercury retrograde |

Slow planet trigger'ları (Jupiter, Saturn, Pluto transit'leri) v2'ye ertelendi.

### 4.3 Match → Render

```python
def render_why_now(pattern, today_transits, locale="tr"):
    for trigger in pattern.why_now_triggers:
        if trigger.matches(today_transits):
            template = pick_template(trigger.templates[locale])
            return render_template(template, today_transits)
    return ""  # not active, UI hides
```

**İlk match wins.** Tie-break yok. Scoring yok. Birden fazla trigger match ediyorsa ilkini kullan, diğerlerine bakma.

### 4.4 Boş kalma davranışı

Aktivasyon yoksa: `why_now_active: false`, `why_now: ""`. UI widget'ı `SizedBox.shrink` — zorlama yok. Voice spec invariant: asla `null`, daima empty string.

### 4.5 TR + EN Parity

Her pattern'ın why_now havuzunda **hem TR hem EN** template var. Locale gate frontend'de (voice spec v2.1 §11.8). EN render edilmezse TR default.

---

## 5. Emotional Intent — 5 Label × 3-Column UI Driver

### 5.1 5 Label

| Label | Hissettirir |
|---|---|
| `rahatlatma` | "Bu senin hatan değil" — trauma-informed yumuşatma |
| `fark_edilme` | "Ben seni görüyorum" — içsel gerçeğin dile gelmesi |
| `içgörü` | "Bunu böyle düşünmemiştim" — yeni açı |
| `izin` | "Böyle olabilirsin" — suçluluk dağıtma |
| `ayrım` | "X değil, Y" — paradox/reframe |

### 5.2 Her Label 3 UI Kararı Tetikler

| Intent | tone_accent | opening kalıp | potential closing |
|---|---|---|---|
| **rahatlatma** | `lime` | "Bu senin hatan değil..." | "zamanla gelir" |
| **fark_edilme** | `lav` | "İnsanlar X sanıyor — oysa Y..." | "görünürlük senin kararın" |
| **içgörü** | `stone` | "X değil, Y..." | "bu kavrayışın kendisi değişim" |
| **izin** | `blush` | "Bu senin hakkın..." | "olduğun gibi yeterli" |
| **ayrım** | `lime+lav` | "Bu bir X değil, Y..." | "iki tarafı birden tut" |

### 5.3 voice_profile_v2 override

Pattern'ın intent'i **sadece bu thread için** voice profile axis'lerini shift'ler:

```python
INTENT_VOICE_SHIFT = {
    "rahatlatma":   {"softening_level": 0.7, "warmth": 0.75},
    "fark_edilme":  {"texture": 0.8, "directness": 0.72},
    "içgörü":       {"holding_style": 0.7, "sentence_length": "long"},
    "izin":         {"warmth": 0.8, "softening_level": 0.65},
    "ayrım":        {"directness": 0.9, "playfulness": 0.55},
}
```

Profile-wide değil — sadece o thread'in render'ına uygulanır. Kullanıcının genel tone profile'ını bozmaz.

---

## 6. Opening Hook — Yüzleşme Tonu

### 6.1 Core Rule

Opening **compressed body değil**. Opening = **mini yüzleşme**.

| | ❌ Compression | ✅ Confrontation |
|---|---|---|
| Niyet | body'yi özetle | kullanıcıyı içeri çek |
| Cümle yapısı | tanım | paradoks/reframe |
| Test | "bu doğru mu?" | "bunu açmalı mıyım?" |
| Örnek | "Söylemeden önce içinden geçiriyorsun." | "İnsanlar seni yavaş sanıyor — oysa her kelimeyi iki kez tartıyorsun." |

### 6.2 4 Mikro-Kalıp

| Kalıp | Ne zaman | Örnek |
|---|---|---|
| "İnsanlar X sanıyor — oysa Y" | Dış algı ≠ iç gerçek | "Herkes seni sakin sanıyor — içerde ne döndüğünü kimseye söylemiyorsun." |
| "Bu bir X değil, Y" | Rasyonalizasyonun reframe'i | "Güzel olmayan bir cümleyi ağzına alamıyorsun — bu bir seçim değil, filtre." |
| "X öğrendin; şimdi Y tuhaf" | Zamanın kalıbı | "Çocukken büyük davranmayı öğrendin; şimdi küçük olmak tuhaf geliyor." |
| "Yüzde N — ve sen buna X yapıyorsun" | Sayı + suç ortaklığı | "Emeğinin yüzde doksanını kimse görmüyor — ve sen göstermeye de çalışmıyorsun." |

### 6.3 Voice Spec Check-List

Her yeni opening için:
- [ ] Sen + şimdiki zaman
- [ ] 6–14 kelime
- [ ] Yargısız ama rahatsız edici
- [ ] Tek iddia (ya da iki cümleli kontrast)
- [ ] Somut davranış
- [ ] Astro teknik terim YOK

---

## 7. Proof Layering — 3 Yerde Aynı Bilgi, 3 Farklı Yoğunluk

### 7.1 Üç Katman

| Katman | Pozisyon | Stil | Örnek |
|---|---|---|---|
| `icard-tag` | Kart header, sol | Mono 7.5–8px uppercase, color-dot prefix | `● SATURN · 3. EV` |
| `icard-orb` | Kart header, sağ | Fraunces italic 13px | `5°35′` |
| `slide-ref-tag` | Slide overlay alt | Mono 8px uppercase, outlined chip, color | `♄ · 3. EV · ARIES 1°09′` |

### 7.2 Tek Kaynak, Üç Format

Backend tek kaynaktan emit eder, UI hangisini kullanacaksa seçer:

```json
{
  "proof_raw": "Satürn · 3. ev · Koç",
  "proof_orb": "5°35′",
  "_debug": {
    "proof_slide_ref": "♄ · 3. EV · ARIES 1°09′"
  }
}
```

Frontend `proof_raw` + `proof_orb`'dan icard-tag + icard-orb türetir. Slide-ref için _debug kullanır ya da runtime format'lar.

### 7.3 ProfileProofChip (v2) Deprecated

Mevcut `mobile/lib/app/profile/proof_chip.dart` (paragraph altı, sol border, alpha 0.60, Title Case) **hedef tasarıma uymuyor.** S2 Commit 2b ile main'e girdi ama v3'te kaldırılacak — icard-tag konumu/stili ile değiştirilir. Migration: `claude/proof-redesign` branch'inde Sprint 5 içinde.

---

## 8. Experience Flow Contract

```
┌─────────────────────────────────────────────────────────────────┐
│ HOOK                    │  thread.opening                         │
│ "İnsanlar seni yavaş... │  (yüzleşme kalıbı, 6-14 kelime)        │
└─────────────────┬────────┴──────────────────────────────────────┘
                  │ user sees card
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ CURIOSITY               │  thread.proof_raw + thread.proof_orb   │
│ "hmm bu bende var mı?"  │  + thread.name (pattern adı)           │
│                         │  + thread.tone_accent (intent rengi)   │
└─────────────────┬────────┴──────────────────────────────────────┘
                  │ user taps
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ WHY NOW                 │  thread.why_now (human-first cümle)    │
│ "bu bugün canlı"        │  UI: opening'in altında, lime underline│
└─────────────────┬────────┴──────────────────────────────────────┘
                  │ user opens slide overlay
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ DEEPER — Slide sequence                                         │
│ Slide 1 (surface)    = opening + illust_hints.opening           │
│ Slide 2 (mechanism)  = detail[mechanism] + illust.wheel_house   │
│ Slide 3 (cause)      = detail[cause] + illust.timeline          │
│ Slide 4 (shadow)     = detail[shadow] + illust.two_cards_vs     │
│ Slide 5 (potential)  = detail[potential] + illust.expanding     │
│                        ← why_this_matters burada                │
│ Slide 6 (caption)    = pattern name + share CTA                 │
└─────────────────┬───────────────────────────────────────────────┘
                  │ user reads potential
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ "BENİ GÖRDÜ"            │  emotional_intent + potential closing  │
│                         │  (intent'e göre ton shifts)            │
└─────────────────┬────────┴──────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ RETENTION               │  pattern_name ("Sessiz değerlendirme") │
│ "bendeki o X pattern'i" │  ezberlenebilir, share target          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Bold Simplifications (Korunuyor)

### S1 — Pattern = thread metadata, not new root object

Payload'da `patterns[]` collection yok. Thread'in `name`'i pattern tetiklenirse pattern adını alır, tetiklenmezse section title'ı kalır.

### S2 — Slides = view, not data type

Backend slide üretmiyor. Thread → 6 slide projection **frontend'de**. Slide içeriği detail_blocks kind'larından türer. Tek content source, drift yok.

### S3 — Emotional intent = one primary label

Her pattern tek bir primary intent alır. Multi-dimensional taxonomy denemeyin — 5 label × pattern × sub-intent çarpımı içerik ekibini boğar. 5/pattern/primary.

---

## 10. Timeline — 5 Hafta

| Tier | Süre | İş |
|---|---|---|
| A | 1 hafta | Pattern detection engine (natal_pattern_library.py + matcher) |
| B | 1 hafta | Opening hook content (25 yüzleşme cümlesi) |
| C | 1.5 hafta | Detail taxonomy + potential content ("why_this_matters") |
| D | 0.75 hafta | Emotional intent + UI driver glue (tone_accent + voice_profile override) |
| E | 0.5 hafta | Experience flow doc + contract |
| F | 0.75 hafta | Why_now engine (2-3 trigger, human-first templates) |
| **Toplam** | **~5 hafta** | — |

**Paralel gidebilir:**
- A + F (ikisi de trigger structure'ı paylaşır)
- B + C (ikisi editorial work)
- D + E (ikisi glue/doc work)

3 kişilik ekip × 2 hafta = biter. Solo developer → 5 hafta.

---

## 11. Scope Dışı (v3'te yapılmaz)

- Slide overlay widget (Flutter) — Sprint 5'te ayrı
- 7 illustration component (Flutter) — Sprint 6'da ayrı
- Pattern library genişletme (25 → 60) — v3.1'de
- Slow planet why_now trigger'ları — v3.1'de
- Voice calibration UI yüzeyi — v4'te
- LLM fallback for rare patterns — v4'te

---

## 12. Şimdi Ne Yapılacak (Sprint 3 — bu hafta)

1. **B.1** `share_headline` emit bug fix (30 dk) — `supporting_threads_builder.py`
2. **B.2** Label translation (Recognition → İlk izlenim) — 1 saat
3. **B.5** `proof_orb` emit — 2 saat
4. **Pattern library v1 seed** (10 pattern, bu dokümanla birlikte) — 3 gün
5. **Why_now engine shell** (1 trigger type, ilk pass) — 2 gün

Sprint 3 sonunda: 10 pattern backend'de tanımlı, match ediyor, why_now üretiyor. Widget entegrasyonu Sprint 4.

---

## 13. Referanslar

- [voice_spec.md](voice_spec.md) — v2.1, 8+3 katman
- [share_line_playbook.md](share_line_playbook.md) — viral test + kurallar
- [s2_mobile_plan.md](s2_mobile_plan.md) — mobile çalışma scope
- `backend_briefing.md` — mevcut backend durumu (external)
- `natal_live_sample_1996-12-28_istanbul.json` — Sahra'nın canlı çıktı örneği (external)
- `SHOU_BACKEND_UX_CONTRACT_v2.md` — yerini alan versiyon
- `shou_profile_v9_sahra.html` — target profile mockup
- `shou_home_v12.html` — target home mockup
- `shou_slide_examples_3_patterns.html` — 3 pattern tam örneği

---

## 14. Değişiklik Tarihçesi

| Sürüm | Tarih | Ana değişiklik |
|---|---|---|
| v1.0 | (earlier) | İlk contract |
| v2.0 | 2026-04-18 | Dark overlay + illustration library + 15 pattern seed |
| **v3.0** | **2026-04-21** | **Human-first why_now, emotional intent UI driver, scoring yok, scope 5 hafta, ProfileProofChip deprecation** |

---

**Son söz:**

> Motor kurmuyoruz — var olan motora **duygu seslendirmesi** ekliyoruz. 
> Backend'deki 2155 satır elle yazılmış narrative zaten chart-specific.
> Eklediğimiz üç şey: **isim**, **hook**, **bağlam** (why_now).
> Kullanıcı 5 hafta sonra "bu beni gördü" diyecek çünkü:
> - Pattern adı ezberlenebilir (retention)
> - Opening yüzleşme (curiosity)
> - Why_now bugün aktive ediyor (immediate relevance)
> - Intent UI'da görünür (emotional aligned)
> - Depth slide payoff (meaning delivered)
