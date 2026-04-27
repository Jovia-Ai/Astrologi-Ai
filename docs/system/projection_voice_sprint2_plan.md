# Projection Voice — Sprint 2 Plan

**Tarih:** 2026-04-27
**Kapsam:** Pattern-level + surface-mode + semantic-enrichment maddeler — `profile_narrative_projection_v1` ve `profile_v8_projection_v1` yüzeyleri.
**Kaynak:**
- [`projection_voice_tuning_gap_audit.md`](projection_voice_tuning_gap_audit.md) — 32 bulgu (orijinal denetim)
- [`projection_voice_sprint1_post_audit.md`](projection_voice_sprint1_post_audit.md) — Sprint 1 doğrulaması, 21 madde açık
- [`shou_surface_orchestration.md`](shou_surface_orchestration.md) — voice mode × length constraint × repetition rules
- `docs/voice/voice_spec.md` v2.1 — SHOU voice doktrini

> **Bu doküman implementation içermez** — sadece sırayla atılacak işleri, riskleri, test stratejilerini ve karar noktalarını sıralar.

---

## 0. Sprint 2 hedefi

Sprint 1 phrase-level (11 madde) ve lint guard'ı kapattı; voice "biraz daha az coaching" hissini verdi ama "şablon hissi" duruyor. Sprint 2'nin amacı **yapısal repetition + flat-declarative + paralel-sözdizimi** sorunlarını çözüp:

1. Profile body 7 blok (identity_aura, mind_voice, drive_rhythm, love_depth, career_visibility, home_roots, luck_creation) için **blok-spesifik semantic çatı** (1.1)
2. v8 bundle headline'ları için **signature-aware contrastive reducer** (1.6 + 3.3 + 6.3)
3. SOFT_ASTRO_HINTS için **kontrast yapısı + uzunluk hiyerarşisi** (1.5 + 4.1)
4. _BLOCK_COPY_FALLBACKS için **slot ritmi varyasyonu** (4.3)
5. Self-help kalıbının kapanışı (5.5 + 6.2)
6. Mode-conditional template pattern (2.3)
7. PAST_LAYER_TRIGGERS / TALENT_RULES / MISSION_RULES kapsam genişletmesi → **Sprint 3'e bırakıldı**

**Sprint 2 success criteria:**
- Phrase lint testi yeşil kalmaya devam ediyor (regression yok)
- Voice spec §3 (kontrastlı), §4.4 (gölge yumuşatılır), §6 (kontrast yapısı), §10 (cümle uzunluk hiyerarşisi), §11 (spesifik referans) ihlal sayısı azalıyor
- Per-fixture render frequency aynı (fix01: 3 surface → 3 surface; pre-Sprint-2 baseline ile karşılaştır)
- Schema / selection / surface orchestration **dokunulmadı**

---

## 1. P0 — Body template havuzu blok-spesifik refactor

### 1.1 Audit referansı: madde **1.1** (pattern-level fix)

### Mevcut sorun
`backend/app/natal/narrative/phrase_lib_tr_profile.py:99-101`:

```python
BODY_TEMPLATES_TR: Dict[str, Dict[str, str]] = {
    block_id: dict(_BODY_TEMPLATE_BY_MODE) for block_id in TITLE_FAMILIES_TR
}
```

7 blok aynı 4 mode template'ini paylaşıyor (`_BODY_TEMPLATE_BY_MODE`). Her renderda 4 cümlelik aynı iskelet:
- A: `{core} → {mechanism} → "Baskı yükseldiğinde {shadow}" → "Yerini bulduğunda {gift}"`
- B: `"İnsanlar sende önce şu çizgiyi okur: {core}" → ...`
- C: `"Bir ortama girdiğinde {core}" → "Perde arkasında ise {mechanism}" → ...`
- D: `{core} → "İç hattında {mechanism}" → "Kırılgan yerde {shadow}" → "Güven oluştuğunda {gift}"`

`identity_aura` body'si ile `home_roots` body'si tamamen aynı yapıdan üretiliyor — kullanıcı 2-3 blok aşağı kaydırdığında "Bir ortama girdiğinde / Perde arkasında / Gerilim yükseldiğinde / Denge geldiğinde" tekrarını fark ediyor.

### Kullanıcı-görünür semptom
- Profile sayfasında 7 ayrı blok kart aynı 4-cümle iskeletinde geliyor
- Kart-arası geçişlerde "şablon hissi" — özellikle aynı mode iki kartta düştüğünde (her renderda %25 ihtimal × 7 blok = en az 1-2 collision tipik)
- Voice spec §10 (cümle uzunluk hiyerarşisi: kısa-orta-uzun) hiç işlemiyor — body hep 4 ~eşit cümle

### Risk düzeyi: **MEDIUM-HIGH**
- `BODY_TEMPLATES_TR` çıktısı 14 baseline fixture'a etki ediyor → regen gerekecek
- Block-spesifik template aile ekleyip mevcut 4-mode mantığını kırarsam: render mode rotation güvenliği bozulabilir
- Approval test (`test_profile_narrative_engine.py:325-328`) marker phrase'lere bel bağlıyor — marker listesini güncellemek gerekecek

### Implementation yaklaşımı

Üç katmanlı refactor:

**Adım 1 — Block-family taxonomy oluştur** (no code change yet, design only):

Her blok için 2-3 farklı semantic çatı tanımla. Örnek:

| Block | Çatı tipleri |
|---|---|
| `identity_aura` | "outer-vs-inner contrast" / "structure-vs-flow contrast" / "presence-vs-direction contrast" |
| `mind_voice` | "tempo-vs-precision" / "clarity-vs-discernment" / "voice-vs-listening" |
| `drive_rhythm` | "momentum-vs-method" / "vision-vs-build" |
| `love_depth` | "threshold-vs-depth" / "trust-vs-openness" |
| `career_visibility` | "quality-vs-visibility" / "private-vs-public" |
| `home_roots` | "self-reliance-vs-receiving" / "rhythm-vs-recharge" |
| `luck_creation` | "creation-vs-flow" / "patience-vs-leap" |

Toplam ~17-20 farklı çatı pattern'ı; her biri kendi 4-cümle iskeletine sahip ama yapısal olarak farklı opening + closing.

**Adım 2 — `BODY_TEMPLATES_TR` dictionary'sini block-explicit hale getir:**

```python
# Kavramsal — kod örneği değil, plan
BODY_TEMPLATES_TR: Dict[str, Dict[str, str]] = {
    "identity_aura": {
        "A": "<outer-inner contrast template>",
        "B": "<structure-flow contrast template>",
        "C": "<presence-direction contrast template>",
        "D": "<inner-resilience template>",
    },
    "mind_voice": {
        "A": "<tempo-precision template>",
        ...
    },
    # ... 7 blok her biri özel 4 mode
}
```

**Adım 3 — Mode rotation seed mantığını koru:**

`_select_mode` (line 254-256) ve `_candidate_modes` aynı kalır — sadece template havuzunun blok-bağımsız olması yerine blok-spesifik olması değişir. Quality issues kontrolü (`quality_issues` line 352) korunur.

### Tests needed

| Test | Amaç |
|---|---|
| `test_profile_narrative_engine.py::test_profile_narrative_uses_multiple_render_modes_when_possible` | Block-spesifik template'lerle de mode rotation çalışıyor mu |
| `test_profile_narrative_engine.py:325-328` (marker assertion) | Yeni opening/closing marker setine güncelle (her blok için) |
| Yeni: `test_profile_narrative_engine.py::test_profile_narrative_blocks_use_distinct_body_templates` | İki farklı blokta üretilen body'ler şablonsal-eşdeğer olmamalı (hash veya opening-key bazlı diff > 0) |
| `test_natal_v8_baseline_snapshot.py` — REGEN | 11 baseline regenerate edilecek |
| `test_projection_phrase_lint.py` | 20 case yeşil kalmalı |

### Sprint 2 mi deferred mi?
**Sprint 2 — P0**. En yüksek user-visible impact, "şablon hissi"nin %50'sini taşıyor.

### Effort tahmini
**1.5–2 sprint günü** (taxonomy design 0.5 + 7 blok × ~4 template yazımı 1 + test/regen 0.5)

---

## 2. P0 — `_BUNDLE_HEADLINES` signature-aware contrastive reducer

### Audit referansı: maddeler **1.6 + 3.3 + 6.3** (pattern-level + needs semantic enrichment)

### Mevcut sorun
`backend/app/natal/profile_v8_payload_builder.py:405-413`:

```python
_BUNDLE_HEADLINES: dict[str, str] = {
    "relational_pattern_bundle": "İlişki hattında tekrar eden bir desen var.",
    "angle_identity_bundle": "Dışarı verdiğin kimlik tonu güçlü.",
    "soft_capacity_bundle": "Yumuşak kapasitelerin hızlı açılıyor.",
    "mental_style_bundle": "Zihinsel ritminde ayırt edici bir hat var.",
    "emotional_regulation_bundle": "Duyguyu yönetme biçimin, savunma hattının da rengini veriyor.",
    "pressure_growth_bundle": "Baskı altında büyüme refleksin belirgin.",
    "contradiction_bundle": "İçeride iki yönü aynı anda taşıyorsun.",
    "personal_core_bundle": "Merkezinde net bir kişisel omurga var.",
}
```

8 başlığın 5'i `var` ile bitiyor; **hiçbiri kontrast yapısı** (voice spec §6) içermiyor; bundle selection'ın getirdiği signature spesifikasyonu (örn. `7th-cusp ruler + Saturn-Venus square`) headline'a inmiyor — string lookup ile düzleşiyor.

### Kullanıcı-görünür semptom
- v8 profil sayfasında bundle başlıkları flat-declarative — "şu var" / "şu güçlü"
- Aynı bundle iki ay sonra ikinci kullanıcıya açıldığında **birebir aynı başlık** çıkıyor
- Spec §1.4 "Co-Star ile fark"ın temel iddiası ("uncanny validation") burada zayıflıyor

### Risk düzeyi: **MEDIUM**
- v8 builder'ın `_BUNDLE_HEADLINES` lookup'ını signature-aware reducer'a çevirmek runtime path'ı genişletiyor
- Ama selection logic'e dokunmuyor — sadece label katmanı
- Schema değişmiyor: headline string aynı yere yazılır

### Implementation yaklaşımı

**Adım 1 — Bundle × signature → headline matrix tanımla:**

Her bundle için 2-3 farklı signature alternatif headline'ı tanımla:

```python
# Plan
_BUNDLE_HEADLINE_VARIANTS: dict[str, dict[str, str]] = {
    "relational_pattern_bundle": {
        "default": "İlişki hattında tekrar eden bir desen var.",
        "saturn_venus_dominant": "Bağlarında yakınlık ve ölçü aynı anda var.",
        "h7_ruler_h12": "Yakınlık görünmeden önce sende olgunlaşıyor.",
        "node_axis_relational": "Bağlanma yönün hayatın boyunca yön değiştiriyor.",
    },
    # ...
}
```

**Adım 2 — Signature detector helper:**

`_detect_bundle_subsignature(bundle_id, fragments, facts) -> str` — bundle'a bağlı signature'lara bakıp en iyi matching variant key'ini döner. Hiçbiri match etmezse `"default"` kullanır.

**Adım 3 — Contrast pattern enforce:**

8 default + ~16-24 variant headline'ın her birinde voice spec §6 kontrast (dış-iç / şimdi-sonra / akış-tutuculuk) uygula. Örnek:

| Bundle | Default (mevcut) | Spec'e uygun (önerilen) |
|---|---|---|
| `personal_core_bundle` | "Merkezinde net bir kişisel omurga var." | "Dışarıda yumuşak duruyor; merkezinde net bir omurga var." |
| `pressure_growth_bundle` | "Baskı altında büyüme refleksin belirgin." | "Sıkıştığında dağılmıyor; baskı altında pozisyon alan bir tarafın var." |

### Tests needed

| Test | Amaç |
|---|---|
| Yeni: `test_profile_v8_payload_builder.py::test_bundle_headline_variant_distribution` | Aynı bundle 2 farklı signature ile 2 farklı headline üretmeli |
| Yeni: `test_profile_v8_payload_builder.py::test_bundle_headline_default_when_no_signature_match` | Match yok → default headline |
| `test_natal_v8_baseline_snapshot.py` — REGEN | bundle_headline'ı görünen 8 fixture (fix01-fix08) update edilecek |
| `test_projection_phrase_lint.py` — yeni eklemeler | "var." kapanışlarında forbidden pattern eklemek (gevşek lint, sadece bundle headline'da) |

### Sprint 2 mi deferred mi?
**Sprint 2 — P0**. v8 yüzeyinde en görünür flat-declarative kaynağı.

### Effort tahmini
**1 sprint günü** (matrix yazımı 0.5 + detector 0.25 + test/regen 0.25)

---

## 3. P1 — `SOFT_ASTRO_HINTS_TR` rhythm ve kontrast iyileştirmesi

### Audit referansı: maddeler **1.5 + 4.1** (pattern-level + surface mismatch)

### Mevcut sorun
`backend/app/natal/narrative/phrase_lib_tr_profile.py:104-140`:

21 hint'in 17'si "X ile Y aynı anda/birlikte çalışıyor/hissediliyor" formülünden türemiş. Hepsi 12-16 kelime aralığında.

```python
"identity_aura": [
    "Sende sağlam bir omurga ile özgünlük aynı anda hissediliyor.",
    "Sağlam duruşun ile farklı kalan tarafın aynı çizgide ilerliyor.",
    "Yön duygun ile büyük resmi birlikte taşıyan bir yanın var.",
],
```

Voice spec §6 **kontrast yapısı** istiyor (dış-iç, görünen-gerçek, hız-yavaş). Burada **eşitleme yapısı** var (X ile Y birlikte). Spec §10 cümle uzunluk hiyerarşisi (kısa-orta-uzun) bekliyor.

### Kullanıcı-görünür semptom
- Hint katmanı (paragraph-altı küçük cümle) blok geçişlerinde monoton ritmde
- Kart 1'de "X ile Y birlikte çalışıyor", kart 2'de "X ile Y aynı anda hissediliyor", kart 3'te "X ile Y aynı çizgide ilerliyor" — kullanıcı 3-4 kart sonra "robotik kalem" hissine geliyor

### Risk düzeyi: **LOW**
- Hint cümleleri tek başına bağımsız — block boundary'sine sıkı bağlı değil
- Selection logic'i değişmeden sadece template havuzu genişler
- Per-block 3 hint zaten randomize seçiliyor; uzunluk hiyerarşisi varyasyonu eklemek yan etki yapmaz

### Implementation yaklaşımı

**Adım 1 — Her bloğa 5-7 hint** (3'ten 5-7'ye genişlet):

| Block | Hint sayısı (yeni) | Çatı tipleri |
|---|---|---|
| identity_aura | 6 | 2 kontrast (dış-iç) + 2 kısa beyan + 2 uzun gözlem |
| mind_voice | 6 | aynı kalıpta |
| ... | ... | ... |

**Adım 2 — Yapısal varyasyon enforce:**

3 yapı tipi, her bloğun hint havuzunda balanced:
- **Kısa kontrast** (8-10 kelime): "Dışarıda toplu, içeride özgün."
- **Orta gözlem** (12-15 kelime): "Sağlam bir çerçeve kuruyorsun ama o çerçevenin içinde kendi yönünü de istiyorsun."
- **Uzun nüans** (16-22 kelime): "Bir tarafın yapı kurmak isterken diğer tarafın kalıba sığmamak istiyor; bu ikisi senin gücünün doğal kaynağı."

Selection seed mevcut `_stable_int(seed) % len(hints)` ile rasgele seçer; balanced havuzda hangi struct çıkarsa block-cross-rhythm sağlanır.

**Adım 3 — Eşitleme formülünü blokla:**

Yeni hint lint testi: "X ile Y aynı anda/birlikte (çalışıyor|hissediliyor|ilerliyor)" pattern'ı havuzun %50'sinden fazla olmasın.

### Tests needed

| Test | Amaç |
|---|---|
| Yeni: `test_phrase_lib_tr_profile.py::test_soft_astro_hints_have_length_diversity` | Her bloğun hint havuzunda en az 1 kısa (≤10 kelime), 1 orta (12-15), 1 uzun (16-22) olsun |
| Yeni: `test_phrase_lib_tr_profile.py::test_soft_astro_hints_avoid_equalization_overdensity` | Her bloğun hint havuzunda "X ile Y aynı anda/birlikte" pattern'ı %50'yi geçmesin |
| `test_natal_v8_baseline_snapshot.py` — REGEN | hint katmanı seed'e bağlı seçim yapıyor, bazı baselines'da hint cümlesi değişebilir |
| `test_projection_phrase_lint.py` | 20 case yeşil kalmalı |

### Sprint 2 mi deferred mi?
**Sprint 2 — P1**. Görünürlüğü P0'lara göre düşük ama effort de düşük; aynı sprint'te halletmek mantıklı.

### Effort tahmini
**0.75 sprint günü** (7 blok × 3-4 yeni hint yazımı 0.5 + test/regen 0.25)

---

## 4. P1 — `_BLOCK_COPY_FALLBACKS` slot ritmi varyasyonu

### Audit referansı: madde **4.3** (pattern-level fix)

### Mevcut sorun
`backend/app/natal/narrative/profile_narrative_engine_signature.py:238-274`:

7 blok × 3 slot (mechanism / shadow / gift) = 21 fragment, hepsi tek cümle. Body 4 cümleye dönüştürüldüğünde (template'ten gelen connector'larla):
- core (1 cümle) → mechanism (1 cümle) → shadow (1 cümle) → gift (1 cümle)
- 4 ~eşit uzunlukta cümle → ritm yok

### Kullanıcı-görünür semptom
- Fallback path'e düşen body'ler "robotic kalem" hissi veriyor
- 4 cümle eşit uzunlukta + connector tekrarları
- Voice spec §10 (kısa-orta-uzun ritm) hiç işlemiyor

### Risk düzeyi: **LOW**
- Fallback path zaten "emergency text" — selection güçlüyse hiç fire etmiyor
- Mevcut sample'lara göre fix01-fix08'de fallback path neredeyse hiç düşmüyor (post-audit dormant analizi gösterdi)
- Schema değişmez

### Implementation yaklaşımı

**Adım 1 — Her slot için 2-3 farklı uzunluk varyantı:**

```python
# Plan
_BLOCK_COPY_FALLBACKS = {
    "identity_aura": {
        "mechanism": [
            "yapın hem sağlam hem özgün",                     # kısa
            "içeride hem sağlam kalmak hem kendi yolunu korumak istiyorsun",  # orta
            "sağlam bir çerçeve kuruyorsun ama o çerçevenin içinde kalıba sığmamak da istiyorsun, ikisi aynı anda işliyor",  # uzun
        ],
        "shadow": [...],  # 3 varyant
        "gift": [...],    # 3 varyant
    },
    # ... 7 blok her biri 3×3 = 9 fragment
}
```

**Adım 2 — Seed-based rotation:**

`_clean_copy_sentence` etrafında bir wrapper helper: aynı seed family'den slot uzunluk varyantı seçer. Body 4 cümle ile dolduğunda kısa-orta-uzun-orta gibi rhythm kurulur.

### Tests needed

| Test | Amaç |
|---|---|
| Yeni: `test_profile_narrative_engine.py::test_block_copy_fallbacks_have_length_variants` | Her slot 2+ uzunluk varyantına sahip |
| Yeni: `test_profile_narrative_engine.py::test_fallback_body_has_rhythm_variation` | Forced fallback path body'sinde 4 cümle uzunluğu en az 2 farklı bucket'a girmeli |
| Mevcut testler | Yeşil kalmalı |

### Sprint 2 mi deferred mi?
**Sprint 2 — P1**. Düşük risk, düşük effort; "şablon hissi"ne katkısı sınırlı ama Sprint 1 chip değişiklikleri gibi safety-net olarak duruyor.

### Effort tahmini
**0.5 sprint günü** (7 blok × 6 ek varyant yazımı 0.4 + test 0.1)

---

## 5. P2 — Self-help kalıbının kapanışı

### Audit referansı: maddeler **5.5 + 6.2** (pattern-level)

### Mevcut sorun

**5.5** — `MISSION_RULES.saturn_third_house_teacher.headline` tipindeki mission rule headline'ları yapısal olarak "X yaptığında Y olabilirsin" şartına çekiyor. Sprint 1 phrase swap (`dönüm noktası olabilirsin → düşüncesi net kayma yaşıyor`) düzeltti ama **kalıp duruyor**: yeni mission rule eklendiğinde aynı yapıyı tekrar üreteceğiz.

**6.2** — `_BALANCE_GIFT_LEADS` strip + rebuild: `_strip_balance_lead` baş kısmı kesip "İyi çalıştığında {clause}; gölgesinde {clause}" sabit yapısına gömüyor. Selection güçlü gift cümlesi sağlasa bile homojenize ediliyor.

### Kullanıcı-görünür semptom
- Mission card'ları "X yaptığında Y olabilirsin" hissi vermeye devam edebilir (yeni trigger eklendiğinde)
- Balance sentence'larında "İyi çalıştığında ... ; gölgesinde ..." sabit connector

### Risk düzeyi: **MEDIUM**
- 5.5 — yeni mission rules için sadece **kural** koymak yeterli (data shape değişmez)
- 6.2 — `_balance_sentence` (line 942) connector pattern'ı değiştirirsek baseline'lar etkilenir; balance sentence quality test'ini güncellemek gerekecek

### Implementation yaklaşımı

**5.5 — Mission headline kalıbı için lint:**

Yeni lint case'leri `test_projection_phrase_lint.py`:
- `r"\bolabilirsin\."` — mission/talent rule headline'larında 0 hit
- `r"\bdönüm noktası\b"` — 0 hit
- `r"\baltın kapı\b"` — 0 hit (TED-pep antipattern)

**6.2 — Balance sentence connector varyasyonu:**

Mevcut tek connector ("İyi çalıştığında / gölgesinde") yerine 3 alternatif:

```python
# Plan
_BALANCE_CONNECTORS = (
    ("İyi çalıştığında", "gölgesinde"),
    ("Yerini bulduğunda", "kırılganken"),
    ("Olgun halinde", "yorulduğunda"),
)
```

Seed-based rotation ile farklı blokta farklı connector seç. Stripped clause'lar aynı ama framing değişir.

### Tests needed

| Test | Amaç |
|---|---|
| Yeni lint case'ler | "olabilirsin." mission/talent path'lerinde 0 hit |
| Yeni: `test_profile_narrative_engine.py::test_balance_connectors_rotate` | 3 connector pair'i seed bazlı rotate ediyor |

### Sprint 2 mi deferred mi?
**Sprint 2 — P2**. Düşük effort, düşük risk; Sprint 1'in koruyucu lint'ini güçlendirir.

### Effort tahmini
**0.5 sprint günü**

---

## 6. P2 — Mode-conditional template (Mode C "Perde arkasında ise" izolasyonu)

### Audit referansı: madde **2.3** (surface-specific voice mode mismatch)

### Mevcut sorun
`phrase_lib_tr_profile.py:87` — Mode C body'sinde `"Perde arkasında ise {mechanism}"` connector'u "cinematic" ton istiyor (spec uygun) ama mode B veya D'ye yanlışlıkla taşınırsa spec §1.2 "ne mistik ne klinisyen" ihlali olur.

### Kullanıcı-görünür semptom
- Şu an semptom yok — Mode C'de doğru kullanılıyor
- Gelecekte refactor edilirken (P0 madde 1.1 block-spesifik template) mode-tone bağı kayabilir; bu madde **defansif lint**

### Risk düzeyi: **LOW**

### Implementation yaklaşımı

P0 madde 1.1 ile birleştir: block-spesifik template tasarlarken her mode'un kendi tone family'sine sadık kalmasını enforce eden lint case'i ekle:

```python
# Plan: test_projection_phrase_lint.py
("perde_arkasinda_only_in_cinematic_C", r"Perde arkasında ise", # in non-mode-C context: 0)
```

Bu test source-level değil runtime-level olur (mode-aware).

### Sprint 2 mi deferred mi?
**Sprint 2'ye P0 (madde 1.1) ile birleştir** — bağımsız iş yok.

### Effort tahmini
**0.1 sprint günü** (P0 ile içiçe)

---

## 7. P3 — `astro_hint` teknik filter Pro paragraph body için gevşetme

### Audit referansı: madde **6.1** (selected node iyi, rendering zayıf)

### Mevcut sorun
`phrase_lib_tr_profile.py:283-296` — `soft_public_astro_hint` zorla teknik referansları filter'lıyor (84 char + tech regex). Voice spec §4.3 **body katmanında spesifik referans gerekli** diyor; filter spec'ten ayrışıyor.

### Kullanıcı-görünür semptom
- Free yüzeyde: hint cümlesi spesifik astrolojik referans içermiyor (örn. "Saturn 3rd ev" yerine "İlişkide güven ile derinlik aynı anda önem kazanıyor")
- Pro yüzeyde: aynı thing — hâlbuki spec Pro paragraph body'de proof katmanı bekliyor
- Paywall sonrası "premium" hissi zayıflıyor

### Risk düzeyi: **HIGH**
- Filter mantığını değiştirmek **selection-adjacent** karar — filter çıktısı renderer'a giriyor
- Free vs Pro yüzey ayrımı surface orchestration spec'i ile çakışıyor — `shou_surface_orchestration.md` "Profile Cards" rules'a göre proof_card optional, ama içerik spec §4.3'e göre body'de specific olmalı
- Net karar paywall infra'sıyla bağlantılı

### Implementation yaklaşımı

**Adım 1 — Sprint 2'de yapma**, ama Sprint 3 hazırlığı için **karar matrisi** çıkar:

| Yüzey | Astro hint katmanı specificity |
|---|---|
| Home > insight_card | Soft (mevcut filter doğru) |
| Profile Top > insight_card | Medium (hint orta seviye, proof opsiyonel) |
| Profile Cards > mechanism_card body | **Specific** — filter gevşemeli |
| Profile Deep > narrative_card body | **Specific + proof_card eşliğinde** |
| Story slide | Soft |
| Share Card | Soft (asla teknik) |

**Adım 2 — Sprint 3'te:** filter'ı yüzey-aware yap (`soft_public_astro_hint(block_id, raw_hint, surface_mode="medium")`). Surface mode parameter'ı surface orchestrator tarafından inject edilir.

### Tests needed (Sprint 3 için)

| Test | Amaç |
|---|---|
| Yeni: `test_phrase_lib_tr_profile.py::test_astro_hint_specific_in_profile_cards` | Profile Cards yüzeyinde technical reference geçiyor |
| Yeni: `test_phrase_lib_tr_profile.py::test_astro_hint_soft_in_home` | Home yüzeyinde technical regex tetiklenmiyor |

### Sprint 2 mi deferred mi?
**Sprint 3'e bırak**. Surface orchestration entegrasyonu Sprint 2 kapsamına çok büyük.

### Effort tahmini (Sprint 3)
**2-3 sprint günü** (surface mode threading + 6 surface için param + test + paywall logic alignment)

---

## 8. Deferred — Semantic enrichment paketi (Sprint 3 ana iş)

Bu maddeler Sprint 2'de **dokunulmaz**, Sprint 3+ kapsamında ele alınır:

### 8.1 `PAST_LAYER_TRIGGERS` kapsam genişletme (madde 6.4)
- Mevcut: 4 trigger handler (`saturn_in_house_3`, `venus_in_house_12`, `moon_in_house_8`, `south_node_aries`)
- Eksik: Pluto-Sun, Chiron-house, Saturn-Moon, Lilith-house, Vertex aspects, MC oppositions
- Hedef: 12-15 trigger
- Effort: 1.5-2 sprint günü

### 8.2 `TALENT_RULES` kapsam genişletme (madde 4.4)
- Mevcut: 3 trigger (`mercury_jupiter_signature`, `moon_venus_harmony`, `neptune_first_house`)
- Eksik: Mars-Saturn (kurma gücü), Sun-Uranus (özgünlük), Mercury-Pluto (analiz derinliği), Venus-Neptune (estetik), Jupiter-MC (görünürlük)
- Hedef: 10-12 trigger
- Effort: 1.5 sprint günü

### 8.3 `MISSION_RULES` kapsam genişletme (madde örtük)
- Mevcut: 2 trigger (north_node_libra, saturn_third_house_teacher)
- Hedef: tüm node sign × house kombinasyonları + Saturn return + Chiron mission
- Effort: 2 sprint günü

### 8.4 Renderer-level proof injection (madde 3.2)
- "kuruluyor" + abstract noun yerine astrolojik anchor (`Saturn 3rd ev`, `Venus Cancer`) sızdırma
- Renderer level değişiklik — selection değil
- Effort: 1.5 sprint günü

### 8.5 `ARCHETYPE_LABELS` signature-aware formatting (madde 3.7)
- Mevcut: `"İlişki akışı"`, `"Kimlik ekseni"`, `"Yumuşak kapasite"` flat label
- Hedef: bundle id + signature → "{adjective} {label}" pattern (örn. "Su-yapılı ilişki ritmi", "Toprak-omurgalı kimlik ekseni")
- Effort: 1 sprint günü

### 8.6 `_BUNDLE_HEADLINES` reducer (madde 6.3)
- **Sprint 2 P0 ile çakışıyor** — orada hallediliyor

---

## 9. Sprint 2 ordering ve bağımlılıklar

```
   ┌──────────────────────────┐
   │ P0-1.1 Body template     │
   │ block-spesifik refactor  │ ◄──── 1.5-2 gün
   └──────────────┬───────────┘
                  │
   ┌──────────────┴───────────┐
   │ P0-1.6/3.3/6.3 Bundle    │
   │ headline reducer         │ ◄──── 1 gün (paralel)
   └──────────────┬───────────┘
                  │
   ┌──────────────┴───────────┐
   │ P1-1.5/4.1 SOFT_ASTRO    │
   │ hints kontrast/ritim     │ ◄──── 0.75 gün
   └──────────────┬───────────┘
                  │
   ┌──────────────┴───────────┐
   │ P1-4.3 Block fallback    │
   │ slot ritim varyasyonu    │ ◄──── 0.5 gün
   └──────────────┬───────────┘
                  │
   ┌──────────────┴───────────┐
   │ P2-5.5/6.2 Self-help     │
   │ kalıp + balance connector│ ◄──── 0.5 gün
   └──────────────┬───────────┘
                  │
   ┌──────────────┴───────────┐
   │ P2-2.3 Mode-conditional  │
   │ (P0-1.1 ile birleşir)    │ ◄──── 0.1 gün (örtük)
   └──────────────────────────┘

   Toplam: 4.75-5.25 sprint günü
```

**Bağımlılıklar:**
- P0-1.1 ve P0-1.6 paralel yapılabilir (iki ayrı dosya, çakışma yok)
- P1-1.5 P0'lardan sonra (P0'lar template iskeletini kurarsa SOFT_ASTRO_HINTS'e nasıl bağlanacağı netleşir)
- P2'ler P1'lerden sonra
- Her aşama sonunda baseline regen + lint test

---

## 10. Out of scope — Sprint 2

**Açıkça dokunulmayacak:**

- ❌ Selection logic (`select_phase2_fragments`, `_apply_semantic_normalization`, `_resolve_best_fragment`, `select_for_profile_v8`)
- ❌ Schema (dataclass field'ları, payload yapıları, surface contracts)
- ❌ Surface orchestration (`shou_surface_orchestration.md`'in tanımladığı surface→card→voice mapping)
- ❌ Cache layer (default_cache_store, surface caches)
- ❌ Voice spec'in kendisi (`docs/voice/voice_spec.md`)
- ❌ EN paritesi (Sprint 4'e bırakıldı)
- ❌ fix11 unknown_birthtime softened narrative (ayrı denetim turu)
- ❌ Semantic enrichment data dictionaries (PAST_LAYER_TRIGGERS / TALENT_RULES / MISSION_RULES kapsam genişletme — Sprint 3)
- ❌ astro_hint surface-aware filter (Sprint 3, paywall infra ile birlikte)
- ❌ Renderer-level proof injection (Sprint 3)
- ❌ ARCHETYPE_LABELS signature-aware formatting (Sprint 3)

---

## 11. Validation strategy

Her commit sonrası:

1. **Phrase lint** (`test_projection_phrase_lint.py`) yeşil — Sprint 1 forbidden phrases geri sızmadı.
2. **Profile narrative engine** (`test_profile_narrative_engine.py`) yeşil — body marker assertion'ı yeni marker setiyle güncel.
3. **Profile v8 builder** (`test_profile_v8_payload_builder.py`) yeşil — bundle headline distribution test'leri eklenmiş.
4. **Baseline snapshot suite** REGEN edildi (`REGENERATE_NATAL_V8_SNAPSHOTS=1 pytest test_natal_v8_baseline_snapshot.py`).
5. **Voice engine TR** (`test_voice_engine_tr.py`) yeşil — tone profile değişmediğinden bozulmamalı.
6. **Selection v3** (`test_natal_selection_v3.py`) yeşil — selection katmanı dokunulmadı.
7. **Spot check 8 fixture** — fix01-fix08'in yeni baseline'ları okunup voice spec §1-6 ihlali aranır.

Sprint 2 sonunda:

- **Yeni post-Sprint-2 audit** (`projection_voice_sprint2_post_audit.md`) yazılır
- Pattern-level 9 madde + surface mismatch 1 madde (5.5/6.2 dahil) statüsü güncellenir
- Sprint 3 readiness raporlanır

---

## 12. Karar checkpoint'leri

Sprint 2 başlamadan önce ürün/PM kararı bekleyen 3 nokta:

### 12.1 Block-spesifik template tasarım yetkisi
P0-1.1 madde için 7 blok × ~4 yeni template = ~28 yeni narrative iskelet yazılacak. Bunlar **voice tasarım kararları**, sadece engineering değil. PM/voice editor onayı:
- Önce 1-2 blok için draft template yazıp PM ile review
- Onaylandıktan sonra kalan 5-6 blok aynı kalıpta hızla tamamlanır
- Effort tahmini bu PM-loop'u içerir

### 12.2 Bundle headline'larında ne kadar spesifiklik?
P0-1.6 için bundle × signature variant matrix kuruyoruz. Spec §4.3 body'de specific istiyor ama bundle headline daha **share-line benzeri** — Story / Share Card yüzeylerine de gidiyor olabilir. Specificity bandını PM'le belirle.

### 12.3 Lint genişletmesi
Sprint 1 lint 20 case ile başladı; Sprint 2 sonunda muhtemelen 30+ case olacak. Her sprintte lint sadece phrase-level değil **structural patterns** (eşitleme formülü, var. kapanışı, X yaptığında Y kalıbı) içerecek. Bu düşey kayma kabul ediliyor mu? Önerim: evet, ama lint commit message'larında pattern'ı açıkla.

---

## 13. Sonuç

Sprint 2 = **4.75-5.25 sprint günü** + 1 PM review döngüsü (block template draft).

Beklenen impact:
- Profile body kart-arası "şablon hissi" %50-70 azalır (P0-1.1)
- v8 bundle başlıkları flat-declarative'den kontrastive-recognition'a kayar (P0-1.6)
- Hint katmanı eşitleme→kontrast yapısına geçer (P1-1.5)
- Lint coverage: 20 → ~30 case
- Sprint 1 phrase lint guard'ı korunur, regression riski düşük

Sprint 2 sonrasında geriye kalan iş:
- Sprint 3: semantic enrichment + surface-aware filter + proof injection (5-7 sprint günü)
- Sprint 4: EN paritesi (3-4 sprint günü)
- Ayrı tur: fix11 unknown_birthtime softened narrative
