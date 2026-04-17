# Transit Sistemi — Audit + Revize Edilmiş Plan

**Tarih:** 2026-04-17
**Bağlam:** Home v2 (Figma) bağlantısı öncesi, transit backend'inin durumu + tonu + pipeline'ı için kapsamlı inceleme. Önceki chat'lerde tartışılan monetizasyon + LLM planı da burada kayıt altına alınır.

---

## BÖLÜM A — AUDIT (Mevcut Durum)

### A.1 Mimari özet

```
[Natal Chart]
      ↓
[Natal Promise Builder] → { themes, claims }
      ↓
[Period Layer] → Calendar (30-120 gün) + Coverage + Deep Archetype
      ↓
[Daily Selection Engine] → Weighted scoring (strength, exactness, speed, phase)
      ↓
[Narrative Assembly] → Templates + LLM (Groq) + Voice Engine
      ↓
[Public Response] → JSON (event_engine_v2, calendar, narrative)
```

**Modül sorumlulukları:**
- `backend/app/transit/` — astro compute (astro_event_v2.py: 95KB), calendar builder (43KB), narrative pipeline (14.8KB)
- `backend/app/engine/transit_engine.py` (67KB) — low-level aspect/body/angle
- `backend/app/transit/interpret/` — interpretation_engine_v1, template resolution, ContentStore
- `backend/app/transit/narrative/` — generator, daily_humanizer_tr, daily_selection, voice shaping
- `backend/app/ai/narrative/` — Groq entegrasyonu (groq_client.py, interpreter.py)
- `backend/app/services/performance/home_orchestrator.py` — Fast (30 min) + Deep (2 hour) cache

**Cache katmanları:**
- Fast: 30 min TTL (home/fast)
- Deep: 2 hour TTL (home/deep)
- Client-side (Dart): 6-30 min + inflight deduplication

**LLM çağrısı:** `call_groq_ai()` — daily narrative, temperature 0.4, max 400 tokens, confidence > 0.35 şartı.

---

### A.2 Yavaş yükleme analizi

**Mobile SLA:** fast 3s / interactive 8s / background 18s

**Home/fast (cache miss) toplam: 1.2–1.8s** — 3s SLA içinde.
**Home/deep (cache miss) toplam: 2–5s** — 8-18s SLA'da ama Groq latency spike'larına açık.

| İşlem | Dosya | Süre |
|---|---|---|
| Swiss Ephemeris | transit_engine.py:85-99 | 100-300ms |
| Rule engine | engine/rule_engine.py | 50-150ms |
| Composite 6 engine | engine/* | 50-100ms (serial) |
| Groq narrative | ai/narrative/groq_client.py:52 | 1-2s (timeout 20s, **senkron blocking**) |
| Template resolution | transits.py:1192-1200 | 50-100ms (6-key fallback cascade) |
| Calendar builder | transit/calendar_builder.py | 800-1200ms |
| Text quality normalization | transit/narrative/text_quality_tr.py | 50-200ms |

**Ana darboğaz:** Groq senkron + template resolution cascade + calendar builder.

---

### A.3 Gereksiz / çift compute

| Hesaplama | Yerler | Kayıp |
|---|---|---|
| Aspect strength scoring | transit_engine + astro_event_v2 + hybrid_context | 3 uygulama, ~50-100ms |
| Aspect orb ↔ strength | transit_engine + daily_selection + ASPECT_ORB_MAX (4 yer) | 20-30ms |
| House overlay | transit_engine:107 + daily_humanizer + assembler | 2-3 traversal |
| Day context extraction | home_orchestrator + assembler:546-596 + calendar_hub_page.dart | 40-80ms |
| Score mixing | daily_selection:97-101 + voice_engine_tr | Overlapping weights |
| Lunar phase detection | astro_event_v2 + calendar/marker_tagger | 2 bağımsız detector |

**Konsolidasyon kazancı:** ~110ms/chart + ~40ms/home-deep.

---

### A.4 Skorlama sistemleri envanteri — 8 sistem

| # | Sistem | Dosya | Risk |
|---|---|---|---|
| 1 | Orb → strength | transit_engine.py:100-130 | Sağlam |
| 2 | Phase (exact/exactish/applying) | daily_selection.py:54-60 | Sağlam |
| 3 | Planet speed weight | daily_selection.py:33-44 | **Moon 0.18 outer Pluto 0.04 — 4.5× fark; Pluto bastırılıyor** |
| 4 | Component mix (str/today/salience) | daily_selection.py:97-101 | **Dilution riski — 3-way ortalama güçlü sinyali körleştiriyor** |
| 5 | Lunation boost | daily_selection.py:79-84 | Sağlam |
| 6 | Event family weight | astro_event_v2.py:59-68 | **aspect_event 0.46 vs cycle 0.92 — daily aspect bastırılıyor** |
| 7 | Planet class weight | astro_event_v2.py:48-57 | Makul |
| 8 | Period narrative score | voice_engine_tr + renderer | **Implicit — dokümante değil** |

**Kalite bozucu vektörler:**
1. Orb saturation → tie-breaker Moon; Saturn/Pluto bastırılıyor
2. Phase × speed çarpımı: exact Moon 0.032 vs exact Pluto 0.007 (25× fark!)
3. Component dilution: 3-way ortalama strong signal'ı nötr hale getiriyor
4. Event family: iki exact aspect bir cycle event'ten düşük kalabiliyor

**Öneri:** 3-way → 2-way (strength 0.60 + temporal 0.40), event family range daralt (0.60-0.85).

---

### A.5 Promise → Period → Daily bağlantısı (silent drop zinciri)

**Promise layer:** promise_builder_v1.py (70 satır). Deterministic, LLM yok, **period/daily seçimine HİÇ girmez.**

**Period layer:** calendar_builder.py. Aspects bağımsız skorlanır — **promise themes görmez.** Coverage modülü period önemini atar ama promise kontrolü yok.

**Daily layer:** daily_selection.py. Selection threshold 0.42. **Period context tamamen kayıp** — daily yalnızca aspect score + lunar phase miras alır. narrative_binding → HOUSE_PACKS_TR (12 pack) — promise claim injection yok.

**Zayıf halkalar:**
1. Promise → period: feedback yok. "Career high" (0.8) → period career aspect'leri boost olmuyor.
2. Period → daily: period title üretilse de daily bağımsız skorlama yapıyor.
3. Promise-aware threshold yok: 0.40 skorlu ama yüksek-promise-theme aspect reddediliyor.
4. Fallback period_story'yi kullanıyor ama promise ile eşleşmeyi doğrulamıyor.

---

### A.6 SHOU editorial tone uyumu

**Mevcut tone defaults:** warmth_bias 0.6, uncertainty 0.35, shadow_safety always_soften.

**Brand V2 spec (shou_brand_v2.html):**
- Inter 400/500, editorial hafiflik
- 50-80 char headline, 2-3 cümle body
- NO klasik astroloji dili ("Jupiter expands your 9th house" yasak)
- Highlight-ready metin (lime/lav/stone inline vurgu için)

**Mevcut çıktı örneği (klasik):**
```
"Güneş Terazi'de Satürn'ün karşısında — doğru tarafta durmak, net sınırlar koyma.
Tavır, sorumlu bir yapı kurmaya, kabul gören yöne gitmeye çağırıyor."
```

**Hedef (SHOU V2):**
```
"Dürüstlüğün tanınan yapıdır bugün. Kalbini korumaya dikkat et."
```

**Generator değerlendirmesi:**
- `daily_humanizer_tr.py` HOUSE_PACKS_TR: kabul edilebilir, punchy değil
- `generator.py` PHRASE_LIBRARY: **çok klasik**
- `voice_engine_tr.py` ASPECT_ESSENCE_TR: **verbose**
- `ai/narrative/interpreter.py` Groq fallback: V2'ye en yakın

**Birleşik tone lint pass** yok — her generator kendi tonunda üretiyor.

---

### A.7 Home v2 için field mapping

| Bölüm | Endpoint | Field | Status | Eksik |
|---|---|---|---|---|
| **Günlük Transit kartı** | /home/deep | daily_cards[0] | 70% | 5-gün strip struct, lime highlight styling |
| ↳ headline | daily_cards[0].headline | | ✓ | — |
| ↳ felt_line | .felt_line_tr | | ✓ | — |
| ↳ why | .why_it_feels_this_way_tr | | ✓ | — |
| ↳ guidance | .guidance_micro_tr | | ✓ | — |
| ↳ signal label | .signal_label_tr | | ✓ | — |
| ↳ 5-gün strip | calendar_public.days[1:5] | | ❌ | `summary_strip` per-day struct |
| **Gökyüzünde Şu An** (3 aspect) | /home/fast → sky_now_feed | sky_events[0:3] | 70% | phase_label_tr, hours_to_exact, signal_icon |
| **Dönem Transiti** (progress ring) | /home/deep → period_core | period_core | 60% | duration_days, themes (promise), progress % |

**Backend'e eklenmesi gereken:**
```python
# /home/fast:
{
  "period_core": { ..., "duration_days": 120, "themes": {...} },
  "promise": { "version": "promise.v1", "themes": {...} }
}
# calendar_public.days[i]:
{ ..., "summary_strip": { "date": "...", "signal_label_tr": "...", "heat": 2, "is_critical": false } }
# sky_event:
{ ..., "phase": "applying", "phase_label_tr": "Yaklaşan", "hours_to_exact": 4.5, "signal_icon": "⚡" }
```

**Tahmini süre:** Period duration 10 min · Promise themes 30 min · Calendar strip 40 min · Sky event enrichment 20 min = **~100 min backend work**.

---

## BÖLÜM B — REVİZE EDİLMİŞ PLAN (Önceki chat'lerden)

### B.1 Monetizasyon Modeli: HYBRID TEASER + LOCK

```
FREE KULLANICI                    PREMIUM KULLANICI
─────────────────                 ──────────────────
✅ Daily kartlar (tam)            ✅ Daily kartlar (tam)
✅ Period teaser (1-2 cümle)      ✅ Period hikayesi (tam, LLM)
🔒 Period devamı → reklam izle   ✅ İleri zaman görünümü
🔒 İleri zaman → premium         ✅ Reklam yok
```

**Reklam mantığı:** Kullanıcı reklamı period kartı güncellendiğinde BİR KEZ izler. Cache'te aynı `period_version` için kilit açık kalır. Haftalık (veya büyük transit değişiminde) yeniden kapanır.

**Maliyet dengesi:**
- 1 period hesap = 1 LLM çağrısı (cache ile tekrarlanmaz)
- 1 reklam = ~$0.01–0.03 gelir
- 1 LLM (GPT-4o-mini) = ~$0.001–0.002 maliyet
- **Her reklamda 10-15× karşılanır**

### B.2 LLM Seçimi: GPT-4o-mini

| Kriter | Groq 70b | Haiku 4.5 | **GPT-4o-mini** |
|---|---|---|---|
| Türkçe nuans | Zayıf | Mükemmel | Çok iyi |
| Editorial tone | Tutarsız | İyi | **Stabil** |
| Hallucination | Orta | Düşük | **Çok düşük** |
| Output predictability | Düşük | İyi | **Yüksek** |
| Fiyat ($/MTok in/out) | 0.59/0.79 | 0.80/4.00 | **0.15/0.60** |

**Karar:** GPT-4o-mini (Haiku'ya göre 5× ucuz, Groq'a göre Türkçe stabil).

**Aylık maliyet (max, cache ile):**
| Kullanıcı | Toplam/ay |
|---|---|
| 1.000 | $0.33 |
| 5.000 | $1.65 |
| 20.000 | $6.60 |

### B.3 Sprint 0 — Hızlı Kazanımlar (Hafta 1-2)

Sıfır yeni paket. Sadece içerik + template.

- **S0-1** SIGN_STYLES_TR → 12 burca tamamla (kalan 7: taurus/gemini/cancer/leo/libra/scorpio/sagittarius). Her biri: style + pitfall + superpower.
- **S0-2** PLANET_ARCHETYPES_TR → 10 gezegen (kalan 6: sun/moon/mercury/venus/jupiter/pluto). Her biri: verbs×3 + shadow×3 + gift×3.
- **S0-3** Period track 4 → 9 (ekle: resource_axis_2_8, healing_axis_6_12, creativity_5, root_4, dissolution_12). Track = 7 alan × 2 varyant.
- **S0-4** Natal vaat → period_opening'e bağlam cümlesi olarak taşı.
- **S0-5** Legacy event_cards → null/boş; mobile fallback sadeleşsin.

### B.4 Sprint 1 — Teaser + Lock Altyapısı (Hafta 3-4)

- **S1-1** Period payload'a `period_teaser` + `period_full` + `period_locked` ayrımı.
- **S1-2** Mobile lock UI (blur + kilit ikonu, rewarded ad → unlock).
- **S1-3** `period_version` hash (natal_fingerprint + ay + transit set hash) — mobile bunu cache'ler, değişmezse tekrar reklam sormaz.

### B.5 Sprint 2 — GPT-4o-mini Entegrasyonu (Hafta 5-7)

- **S2-1** `backend/app/ai/narrative/openai_client.py` — groq_client pattern mirror. Fallback: OpenAI → Groq → template.
- **S2-2** `TRANSIT_PERIOD_PROMPT` — natal-aware, editorial ton, JSON output (period_opening, big_picture, growth_edge, upper_meaning).
- **S2-3** Cache key `sha1(natal_fingerprint + period_month + transit_set_hash)`. Premium = GPT-4o-mini; free (reklam sonrası) = Groq 70b.
- **S2-4** Background job — senkron değil. "Dönem yorumun hazır 🔮" push notification.

### B.6 Sprint 3 — Golden Window + İleri Zaman (Hafta 8-10)

- **S3-1** Golden window: `promise_verdict == strong` + `strength > 0.70` → `golden_window: true`. Free: "Bu ay 2 pencere var" (tarih yok). Premium: "14 Mayıs 15:30 — Satürn-MC."
- **S3-2** İleri zaman: free = mevcut ay. Premium = +3 ay. Backend zaten 120 gün scan'liyor, payload shaping.
- **S3-3** Transit değişince push notification ("Dönem koşulların değişti").

### B.7 Kritik kararlar (onay bekliyor)

| Karar | Öneri |
|---|---|
| Period refresh | **Haftalık** (dinamik) |
| Free'de reklam sonrası | **Groq 70b** (template değil) |
| Push notification | **Otomatik** |
| Golden window tarihi free'de | **"Bu ay var" göster, tarih kilitle** |

---

## BÖLÜM C — RİSKSİZ UYGULAMA GUARDRAIL'LERİ

Sprint 0 içerik ağırlıklı ama yine de tone regression / production crash riski taşıyor. Aşağıdakileri her sprint öncesi uygulayacağız.

### C.1 Commit hijyeni

- **Her S0-X madde ayrı commit.** 5 maddede 5 commit. Tek git revert ile geri alınır.
- Her commit sonrası: `cd backend && pytest` + `flutter analyze` (mobile etkileniyorsa).
- `pubspec.yaml`, `backend/app/core/config.py`, `backend/app/main.py`, `mobile/lib/design/theme/`, `mobile/lib/main.dart`, `mobile/lib/app/app_router.dart`, migration/schema → **onay gerektirir.**

### C.2 İçerik regression koruması

- `backend/tests/test_phrase_lib_golden.py` (yeni) — mevcut 5 burç + 4 gezegen çıktılarının **bire bir aynı kaldığını** doğrular. Yeni eklenenler ayrı test bloğunda.
- Yeni içerik için lint:
  - Headline char ≤ 80
  - Body cümle sayısı ≤ 3
  - Blocklist: "enerji", "evren sana", "çakra", "frekans", "titreşim", "etkisi altında"
  - Required: Türkçe only (no English code-switching)
- `backend/tests/test_tone_editorial_v2.py` (yeni) — regex pass ile klasik marker kontrolü.

### C.3 Feature flag

- Yeni 5 track başlangıçta `settings.transit_new_tracks_enabled = False` ile kapalı.
- Runtime env var ile açılır; kapanır. Rollback = flag flip, deploy beklemez.
- Mobile tarafında aynı paradigma: `period_locked` backend'den True dönerse lock UI, False dönerse mevcut davranış. Feature deploy edilmeden mobile guard çalışır.

### C.4 Performance baseline

Sprint 0 öncesi → `ops-tools/transit_latency_baseline.sh` ile ölçüm:
- `/home/fast` cache hit + miss
- `/home/deep` cache hit + miss
- `/transits/narrative` standalone

Her sprint sonu aynı ölçüm tekrarlanır. %20+ regression = rollback tetikleyici.

### C.5 LLM maliyet kontrolü (Sprint 2 için)

- Daily rate limit per user: **1 LLM period narrative / ay** (hard cap).
- Cost dashboard: daily OpenAI cost metric (günlük $1 threshold → alarm).
- Cache-miss rate monitor (%50'yi geçerse cache key strategy gözden geçir).
- Canary: ilk 48 saat sadece %5 user'a açık. Hata/maliyet kontrol edilip genişletilir.

### C.6 Rollback matrisi

| Problem | Rollback |
|---|---|
| Yeni track'te tone regression | Feature flag kapat |
| GPT-4o-mini Türkçe kalite düşük | Fallback zincirinde GPT-4o-mini'yi atla, Groq 70b kullan |
| LLM maliyeti threshold aşımı | Rate limit haftada 1'e indir |
| Home/deep latency > 8s | Groq call paralelleştirmesini devre dışı bırak |
| Reklam flow user complaint | `period_teaser` alanını kaldır, tam payload dön |

---

## BÖLÜM D — ÖZET EYLEM LİSTESİ

### Yapısal (hemen, Sprint 0 ile paralel)

- [ ] Aspect strength scoring tek yerde (engine/transit_engine.py)
- [ ] House overlay helper — 3 yerden 1 yere
- [ ] Day context extraction — 2 yerden 1 yere
- [ ] `event_cards` legacy null'a çekilsin

### İçerik (Sprint 0)

- [ ] SIGN_STYLES_TR — 7 burç
- [ ] PLANET_ARCHETYPES_TR — 6 gezegen
- [ ] 5 yeni period track
- [ ] Natal vaat → period_opening bağlam cümlesi
- [ ] Golden regression test

### Home V2 backend hazırlığı (Home UI yapmadan önce)

- [ ] `/home/fast` → `promise.themes` ekle
- [ ] `/home/fast` → `period_core.duration_days` + `.themes`
- [ ] `calendar_public.days[i].summary_strip` ekle
- [ ] Sky event enrichment (phase_label_tr, hours_to_exact)

### Home V2 mobile

- [ ] Günlük Transit kartı widget (stone bg + lime highlight + 5-gün strip + event satırı)
- [ ] Gökyüzünde Şu An (3 aspect kartı)
- [ ] Dönem Transiti (progress ring + headline + theme tags)

### Teaser + Lock (Sprint 1)

- [ ] Backend `period_teaser` / `period_full` / `period_locked`
- [ ] Mobile lock widget
- [ ] `period_version` hash

### LLM (Sprint 2)

- [ ] `openai_client.py`
- [ ] `TRANSIT_PERIOD_PROMPT`
- [ ] Cache + fallback zinciri
- [ ] Background job + push notification

### Premium (Sprint 3)

- [ ] Golden window boost + payload flag
- [ ] İleri zaman (+3 ay) gating
- [ ] Transit değişimi push notification

---

**Başlama noktası:** Sprint 0 / S0-1 — SIGN_STYLES_TR içerik yazımı. Kod değişikliği minimal, onay sonrası taslak metinleri önce doküman olarak çıkarıp değerlendirir, sonra `phrase_lib_tr.py`'a işleriz.
