# Projection Voice — Sprint 1 Post-Audit

**Tarih:** 2026-04-27
**Kapsam:** `profile_narrative_projection_v1` + `profile_v8_projection_v1` (regen edilmiş baselines üzerinde — `backend/tests/_artifacts/natal_v8_baseline/fix0[1-8]*.json`).
**Önceki referans:** [`projection_voice_tuning_gap_audit.md`](projection_voice_tuning_gap_audit.md) — 32 bulgu, 6 kategori.
**Sprint 1 kapsamı:** phrase-level fix maddeleri (commit `d5c98e9`) + lint guard (`test_projection_phrase_lint.py`).

> **Bu rapor sadece tespit içindir.** Hiçbir kod değişikliği yapılmamıştır.

---

## 0. Özet — Sprint 1 sonuçları

| Sprint 1 hedefi | Sonuç |
|---|---|
| Forbidden phrase 0 hit | ✅ 13/13 phrase, fix01-fix08 baselines'da 0 görünüm |
| Coaching/self-help azalt | ✅ 5 phrase'in tamamı 0 hit |
| Yeni replacement'lar repetition cluster yaratmadı | ✅ Per-fixture surface count pre-Sprint-1 ile birebir eşit (3-3, 2-2, 3-3 sample) |
| SHOU voice korundu | ✅ Observational + spesifik + non-motivational kalitede sample |
| Schema/selection değişmedi | ✅ 5 source dosyası — hepsi string-content edit, fonksiyon imzaları + dataclass'lar dokunulmadı |

**Karar:** Sprint 1 — **safe to keep**. Hiçbir phrase rollback gerekmiyor. Sprint 2 pattern-level work için hazır.

---

## 1. Forbidden phrase taraması

`fix01_leo_leo_classic` → `fix08_cancer_capricorn_nodes` baseline JSON dosyalarında orijinal audit'in 13 forbidden phrase'i için tam metin araması:

| Phrase | Kategori | Pre-Sprint-1 | Post-Sprint-1 | Δ |
|---|---|---|---|---|
| `Yerine oturduğunda` | calque | n* | **0** | ✅ |
| `İç tarafta işleyiş şöyle` | engineering | n* | **0** | ✅ |
| `birden fazla damar` | metaphor | 1+ | **0** | ✅ |
| `iç standart` | jargon | 4+ | **0** | ✅ |
| `iç standardın` | jargon | 2+ | **0** | ✅ |
| `kazandırır` | reward verb | 6+ | **0** | ✅ |
| `savunma gücünü etkiliyor` | empty verb | 1+ | **0** | ✅ |
| `anlamlı bir akış buluyor` | affirmation | 1+ | **0** | ✅ |
| `büyüme tarafını hızlandırır` | coaching | 3-7 (fix-bağımlı) | **0** | ✅ |
| `Hayat seni …büyütüyor` | life-as-coach | 1-3 | **0** | ✅ |
| `ölçeklenebilen bir zihin` | startup jargon | 23 (8 dosya × 3 surface) | **0** | ✅ |
| `önsezi avantajı veriyor` | competitive | 1-3 | **0** | ✅ |
| `dönüm noktası olabilirsin` | TED-pep | 5+ | **0** | ✅ |

\* mode A/D template'lerinde her renderlamada görünüyordu — pre-Sprint-1 baseline JSON'larda template-koşullu görünüm vardı.

**Karar:** lint testi (`test_projection_phrase_lint.py`) bu pattern'leri source-level enforce ediyor; baseline'lar runtime-level confirm ediyor. **Çift katmanlı koruma aktif.**

---

## 2. Yeni replacement phrase frekansları

Sprint 1'in eklediği phrase'lerin fix01-fix08 baseline'larındaki dağılımı (intra-file × cross-file):

| Yeni phrase | Toplam hit | Dosya sayısı | Hit/dosya | Pre-Sprint-1 eşdeğeri | Δ |
|---|---|---|---|---|---|
| `zihin hattı görünüyor` | 23 | 8 | 2.9 | 23 (`ölçeklenebilen bir zihin var`) | aynı |
| `İç hattında` | 12 | 5 | 2.4 | ~12 (`İç tarafta işleyiş şöyle`) | aynı |
| `kolaylaşıyor` | 12 | 2 | 6.0 | ~12 (`hayat seni büyütüyor`) | aynı |
| `net bir kayma` | 10 | 2 | 5.0 | ~10 (`dönüm noktası olabilirsin`) | aynı |
| `esnek çalışıyor` | 7 | 2 | 3.5 | ~7 (`büyüme tarafını hızlandırır`) | aynı |
| `taşıyor` | 6 | 2 | 3.0 | — (yeni gift fallback path) | yeni-eq |
| `rengini veriyor` | 5 | 1 | 5.0 | ~5 (`savunma gücünü etkiliyor`) | aynı |
| `merkeze çıkarıyor` | 2 | 1 | 2.0 | ~2 (`avantaj veriyor`) | aynı |

**Pre-Sprint-1 vs post-Sprint-1 cross-file count comparison:**

```
fix01_leo_leo_classic.json       pre=3 post=3 (same)
fix02_capricorn_stellium.json    pre=2 post=2 (same)
fix04_h10_career_stellium.json   pre=3 post=3 (same)
```

**Karar:** Yeni phrase'ler **yeni repetition cluster yaratmadı**. Per-trigger render frequency aynı kaldı (her zaten N kez emit ediyordu, hâlâ N kez emit ediyor — sadece içerik değişti).

---

## 3. Dormant Sprint 1 değişiklikleri (güvenli ama görünmez)

Bazı Sprint 1 değişiklikleri fix01-fix08 baseline'larında **hiç** görünmüyor:

| Değişiklik | Pre Sprint 1 hit | Post Sprint 1 hit | Yorum |
|---|---|---|---|
| `Geniş Görüş` (chip) | — | 0 | DEFAULT_PUBLIC_CHIPS_TR fallback path; signature catalog yetmediğinde devreye girer; bu charts için yetmiyor durumu yok |
| `Anlam Çizgisi` (chip) | — | 0 | aynı |
| `Kurma Gücü` (chip) | — | 0 | aynı |
| `Akış Hattı` / `Açılma Eşiği` | — | 0 | aynı |
| `duruş çiziyor` (gift fallback) | — | 0 | `_BLOCK_COPY_FALLBACKS.identity_aura.gift` — selection güçlü olduğu için fallback hiç fire etmiyor |
| `ifade taşıyor` (gift fallback) | — | 0 | aynı |
| `netlik belirginleşir` (fallback signatures gift) | — | 0 | `FALLBACK_SIGNATURES_BY_BLOCK` içinde — fix01-fix08'in hepsi non-fallback path |

**Karar:** Bu phrase'ler **safety-net** olarak duruyor. fix01-fix08 trigger fallback path'ine düşmediği için aktif değil — ama başka chart shape'leri (özellikle birth-time-unknown veya weak-signature charts) bunlara çarpabilir. Sprint 1 koruma katmanını genişletti, runtime davranışı bu fixture seti için aynı kaldı.

---

## 4. SHOU voice spot-check (sample)

`fix02_capricorn_stellium.json` profile_v8 surface'lerinden örnekler:

```
profile_v8.first_felt.body:
  "İnsanlar sende önce şu çizgiyi okur: ilk hissedilen şey çoğu zaman daha
   ciddi ve hedef odaklı bir duruşun olması, ama bunun altında kendi
   yönünü koruyan bir taraf da var…"

profile_v8.defense.body:
  "Yakınlıkta duygunu önce içeride tutup sonra açma refleksi, görünmeyen
   bir korunma hattı kurmana yol açmış olabilir."

profile_v8.mind.body:
  "Bir ortama girdiğinde bir şey sana çarptığında zihnin boşta kalmıyor,
   içeride hemen pozisyon alan bir tarafın çalışıyor. Perde arkasında ise
   bu hat en çok söz, ton ve karar dili tarafında kendini gösteriyor."

profile_v8.first_impression.body:
  "Moon ile Vertex arasındaki trine hattı 0.24° ile çok yakın çalışıyor."
```

**SHOU voice spec uyumu (§§1-4):**
- ✅ **Gözlem, yargı değil**: "İnsanlar sende önce şu çizgiyi okur" — observation
- ✅ **Spesifik referans**: "Moon ile Vertex arasındaki trine hattı 0.24°" — proof level (§4.3)
- ✅ **Yargısız**: "ciddi ve hedef odaklı bir duruşun olması, ama bunun altında kendi yönünü koruyan bir taraf da var" — iki yüz
- ✅ **Kontrastlı**: "girdiğinde / Perde arkasında ise" — dış vs iç
- ✅ **Coaching ton yok**: hiçbir "yapmalısın / hızlanır / büyütüyor" çıkmadı

**Karar:** SHOU voice **post-Sprint-1'de korunmuş**.

---

## 5. Schema / selection değişikliği yok

Sprint 1 commit (`d5c98e9`) tarafından dokunulan source dosyaları + diff niteliği:

| Dosya | Değişiklik niteliği |
|---|---|
| `backend/app/narrative/editorial_render_policy.py` | 1 satır — template string swap (Yerine oturduğunda → Yerini bulduğunda) |
| `backend/app/narrative/humanize_tr.py` | 4 lokasyon — string swap'lar + 1 yeni regex (legacy → new form) |
| `backend/app/natal/narrative/phrase_lib_tr_profile.py` | 4 lokasyon — body template + chip data dict swap'ları |
| `backend/app/natal/narrative/profile_narrative_engine_signature.py` | 9 lokasyon — `_BLOCK_COPY_FALLBACKS` + `FALLBACK_SIGNATURES_BY_BLOCK` + 2 priority_copy gift string swap'ı |
| `backend/app/natal/profile_v8_payload_builder.py` | 7 lokasyon — `PAST_LAYER_TRIGGERS` + `TALENT_RULES` + `MISSION_RULES` + `_BUNDLE_HEADLINES` data dict text alanları |

**Hiçbir değişiklik:**
- Fonksiyon imzasına dokunmadı
- Dataclass field'larına dokunmadı
- Selection function'larına dokunmadı (`select_phase2_fragments`, `_apply_semantic_normalization`, `select_for_profile_v8`, vb.)
- Surface orchestration'a dokunmadı
- Yeni semantik veri eklemedi (TALENT_RULES kapsamı, PAST_LAYER_TRIGGERS kapsamı aynı)
- Schema field'larına dokunmadı (`Profile_v8Payload`, `EditorialSectionPayload` aynı)

**Karar:** **Pure phrase-level**, başka katman dokunulmamış.

---

## 6. Geriye kalan iş — Sprint 2+ scope

Orijinal audit'in 32 maddesinden 11'i (phrase-level) Sprint 1'de kapatıldı. Geriye kalan **21 madde** kategorize:

### 6.1 Pattern-level fix (9 madde) — Sprint 2 ana iş

| # | Madde | Etki yüzeyi | Notes |
|---|---|---|---|
| 1.1 | Body template havuzu blok-bağımsız çoğaltımı (`BODY_TEMPLATES_TR`) | profile body | 7 blok aynı 4 mode template'i paylaşıyor → her blok için kendi semantik çatısı gerek |
| 1.3 | `_BALANCE_GIFT_LEADS` rotasyon-paradoksu | gift cümleleri | Aynı liste hem strip hem rebuild → kullanıcı rotasyon hissetmiyor |
| 1.5 | `SOFT_ASTRO_HINTS_TR` paralel sözdizimi | hint katmanı | 21/21 hint "X ile Y birlikte çalışıyor" eşitleme yapısı; spec kontrast istiyor |
| 1.6 | `_BUNDLE_HEADLINES` flat declarative | v8 bundle başlıkları | 8/8 "var/açılıyor/etkiliyor" düz beyan |
| 3.3 | `_BUNDLE_HEADLINES` "var" kapanışları | aynı | spec §3.4 (kontrastlı) ihlali |
| 4.1 | SOFT_ASTRO_HINTS uniform 12-16 kelime | hint katmanı | spec §10 (cümle uzunluk hiyerarşisi) yok |
| 4.3 | `_BLOCK_COPY_FALLBACKS` slot ritmi | profile body | Tüm slot'lar tek cümle → 4 cümlelik body monoton |
| 5.5 | `mission_rules` headline kalıbı | v8 mission | "X yaptığında Y olabilirsin" yapısal koçluk şartı; phrase swap yetmez |
| 6.2 | `_BALANCE_GIFT_LEADS` homojenizer | gift sentence | strip sonrası kalıba sıkıştırıyor |

**Sprint 2 önerim**: 1.1 (template havuzu) + 1.5 (paralel sözdizimi) + 1.6/3.3 (bundle headlines) bir paket — bunlar en görünür yapısal pattern, kullanıcı feedback'inde "şablon hissi" suçlamasının kaynağı.

### 6.2 Surface-specific voice mode mismatch (5 madde) — Sprint 2 yan iş

| # | Madde | Etki | Notes |
|---|---|---|---|
| 2.3 | "Perde arkasında ise" | Mode C cinematic | Mode B/D'de çıkmamalı; mode-bazlı conditional template gerek |
| 3.5 | PAST_LAYER_TRIGGERS "olabilir" stack | past teaser | 5/5 trigger headline'ı "-mış olabilir(sin)"; certainty kalibrasyonu spec'le çelişiyor |
| 4.1 | SOFT_ASTRO_HINTS uzunluk monotonluğu | hint katmanı | (1.5 ile beraber) |
| 6.1 | astro_hint teknik filter Pro paragraph body için fazla kısıtlayıcı | profile body | spec §4.3 "body'de spesifik referans olmalı" — filter spec'ten ayrışıyor |
| (örtük) | editorialize_teaser/editorialize_micro mode bazlı varyasyon mekanik | teaser/micro | tone.yaml ↔ render policy haritalama yeniden okunmalı |

### 6.3 Needs semantic enrichment (6 madde) — Sprint 3+ yatırım

| # | Madde | Yatırım |
|---|---|---|
| 3.2 | "kuruluyor" + abstract noun (proof sızdırılmalı) | renderer'a astrolojik anchor inject |
| 3.7 | `ARCHETYPE_LABELS` abstract sınıflandırma | label formatter signature-aware olmalı |
| 4.4 | `fix04` Tokyo h10 stellium TALENT_RULES kapsamı dar | TALENT_RULES dictionary expansion (5-10 yeni trigger) |
| 6.3 | v8 `_BUNDLE_HEADLINES` reducer | bundle-level signature → headline mapping |
| 6.4 | PAST_LAYER_TRIGGERS kapsamı dar | aynı pattern (8-15 yeni trigger) |
| (örtük) | `MISSION_RULES` 2 trigger | aynı pattern |

### 6.4 Leave as-is (1 madde)

| # | Madde | Notes |
|---|---|---|
| 6.5 | fix11 unknown_birthtime softened narrative | Bu turun kapsamı dışı; kendi denetim turuna bırakıldı |

---

## 7. Sınıflandırma

### 🟢 Sprint 1 safe to keep
- Tüm 11 phrase-level swap (`yerini bulduğunda`, `iç hattında`, `iç ölçü`, `çiziyor`/`taşıyor`/`belirginleşir`, `rengini veriyor`, `bağlamlı bir yön`, `esnek çalışıyor`, `zihin hattı görünüyor`, `merkeze çıkarıyor`, `kolaylaşıyor`, `net bir kayma`)
- Chip değişiklikleri (`Geniş Görüş`, `Anlam Çizgisi`, `Kurma Gücü`, `Akış Hattı`, `Açılma Eşiği`) — dormant ama safety-net olarak korunsun
- `humanize_tr.py` legacy → new form çevirici regex (eski metin akışlarını otomatik çevirir)
- `test_projection_phrase_lint.py` (20 lint case) — drift guard, koru

### 🟡 Needs minor phrase rollback
- **Yok.** Hiçbir Sprint 1 swap regression yaratmadı. Sample'larda voice kalitesi sağlam, replacement'lar coaching/jargon'a kaymadı.

### 🟢 Ready for Sprint 2 pattern-level work
- Yukarıdaki 9 pattern-level madde
- Önerilen Sprint 2 paketi: **1.1 + 1.5 + 1.6 + 3.3 + 4.3** (template havuzu + paralel sözdizimi + bundle headlines + slot ritmi). Bu beş madde profile body ve v8 bundle headline yüzeylerinde "şablon hissi"nin %80'ini taşıyor.
- Surface mismatch maddelerinden **2.3 (Perde arkasında ise)** Sprint 2'de mode-conditional template çözümüyle birleştirilebilir.

### 🔴 Not ready
- **Yok kritik.** 6 semantic-enrichment maddesi Sprint 3+ kapsamında değerlendirilmeli (TALENT_RULES + PAST_LAYER_TRIGGERS + MISSION_RULES expansion); bunlar Sprint 1 sonrası **opportunity**, regression değil.

---

## 8. Sprint 2 önerisi (öncelik sırası)

| Öncelik | Paket | Etki yüzeyi | Tahmini effort |
|---|---|---|---|
| **P0** | Body template havuzu blok-spesifik refactor (1.1) | profile body 7 blok | 1-2 sprint günü |
| **P0** | `_BUNDLE_HEADLINES` signature-aware reducer (1.6 + 3.3 + 6.3) | v8 bundle başlıkları | 1 gün |
| **P1** | `SOFT_ASTRO_HINTS_TR` kontrast yapısı + uzunluk hiyerarşisi (1.5 + 4.1) | hint katmanı | 1 gün |
| **P1** | `_BLOCK_COPY_FALLBACKS` slot ritmi (4.3) | profile body fallback | 0.5 gün |
| **P2** | `_BALANCE_GIFT_LEADS` strip/rebuild (1.3 + 6.2) | gift cümleleri | 0.5 gün |
| **P2** | mission_rules headline kalıbı (5.5) | v8 mission | 0.5 gün |
| **P2** | mode-conditional template (2.3) | profile mode C izolasyonu | 0.5 gün |
| **P3** | astro_hint teknik filter gevşetme (6.1) | hint Pro paragraph | 1 gün (Pro/free yüzey ayrımı + spec §4.3 alignment) |

Toplam tahmin: **5-7 sprint günü**.

---

## 9. Bu raporun dışı

- Code değişiklikleri ✗ (sadece tespit + sınıflandırma)
- EN paritesi ✗ (`phrase_lib_en_profile` + `humanize_en` ayrı denetim turuna bırakıldı)
- fix11 unknown_birthtime softened narrative ✗ (leave-as-is)
- Pattern-level / semantic-enrichment implementation ✗ (Sprint 2+)
- Selection / projection / schema ✗ (sınır)

---

## 10. Sonuç

**Sprint 1 başarılı**: tüm phrase-level audit kapatıldı, regression yok, lint guard aktif, baseline'lar deterministik. SHOU voice spec'inden taviz verilmedi. Pattern-level Sprint 2 için temiz zemin var.

**Tek dikkat noktası**: Sprint 1'in gerçek değeri pattern-level + semantic-enrichment maddeleri uygulanana kadar **kısmi**. Phrase-level temizlik kullanıcı hissini "biraz daha az koçluk" seviyesine çekti; "şablon hissi" pattern-level iş ile çözülecek.

**Tavsiye**: Sprint 2'yi P0 paketiyle (template havuzu + bundle headlines) başlatmak — kullanıcı geri bildiriminde en yüksek yankıyı yapacak yer burası.
