# Profile V8 — Audit ve Yol Haritası

> Amaç: Natal hesaplama ve profil anlatımını **daha hızlı, daha tutarlı, daha empatik** hale getirmek.
> Tetik: Yeni `profile_v8_white_first` tasarımı (hero → kimlik → "bu nereden geliyor" → yakınlık → zihinsel işleyiş → arketip portali → 4-tab tam harita).
> Tarih: 2026-04-17 · İlgili spec'ler: [docs/narrative_v2_product_spec.md](narrative_v2_product_spec.md), [docs/natal_selection_v3.md](natal_selection_v3.md), [docs/archetype_test_system_v1.md](archetype_test_system_v1.md), [docs/mobile_loading_tuning.md](mobile_loading_tuning.md).

---

## 0. TL;DR

Mevcut natal hattı **çok katmanlı ve şişmiş**: aynı şey birden fazla yerde hesaplanıyor (graph V1+V2, primitive V1+V2, profile_narrative legacy/signature/wrapper), Selection V3 yazılı ama **feature-gated** olduğu için üretimde bypass ediliyor, dil katmanı %100 statik template (`{key}` replacement) — bu yüzden bazen mekanik kaçıyor. Profile V8 backend builder'ı **import edilmiş ama çağrılmıyor**. Mobile tarafında V8 adapter mevcut ama sadece light mode'da; dark mode hâlâ legacy narrative card sistemini kullanıyor. Tasarımdaki 7 yeni section'ın çoğu (yakınlık, zihinsel işleyiş, açılma, misyon timeline, gölge fragmentler, açılan kapılar, "bu nereden geliyor") henüz mobile'da render edilmiyor.

**Önerilen yol**: Önce **konsolidasyon** (ölü kod silinir, tek omurga aktive edilir, payload sözleşmesi sabitlenir), sonra **yeni section motorları** (geçmiş katmanları, açılma noktası, misyon, gölge, açılan kapılar), sonra **dil katmanı** (LLM rewrite + voice profile), en son **mobile yeni tasarım entegrasyonu** (left-border accent card sistemi + 4-tab Tam Harita modal'ı).

---

## 1. Mevcut Mimari (Ne Var)

### 1.1 Backend hesaplama hattı (sırayla)

`POST /interpret` ve `/interpret/ui` çağrıldığında [backend/app/api/routes/natal_interpretation.py](../backend/app/api/routes/natal_interpretation.py) içindeki `_prepare_payload_from_chart()` orchestrator olarak çalışır:

1. **Chart compute**: Swiss Ephemeris → `compute_natal_chart()` → planet/aspect/house pozisyonları
2. **Serialization**: `serialize_planets()`, `serialize_aspects()`
3. **Graph V1**: `build_natal_graph()` — basit angularity + aspect count + ruler ağırlığı (her zaman çalışır)
4. **Graph V2 + Selection runtime** (flag'e bağlı): `build_natal_graph_v2()` → `build_natal_feature_graph()` → `build_primitives_v2()` → `build_contradiction_signatures()` → `build_master_natal_selector()`
5. **Rule engine**: `rule_engine.interpret()` — JoviaWeighted kural değerlendirmesi
6. **Composite katmanları**: `CompositeEngine`, `DispositorFlowEngine`, `AxisActivationEngine`, `AspectMechanicsEngine`, `ActivationSensitivityEngine`, `PatternEmphasisEngine`, `LatentPotentialEngine`, `UpperMeaningEngine`
7. **Guidance & Narrative**: `build_guidance()`, `CompositeInterpretationBuilder`, `ExpressionResolver`, `build_profile_narrative()` (legacy/signature/wrapper seçimi)
8. **Section seri**: `build_sections_v2()`, `build_supporting_threads()`
9. **Public view**: `build_public_natal_view()` → cache

`POST /profile/fast` → `_build_profile_fast_payload()` (inline; sadece sun/moon/rising + ruler).

### 1.2 Mobile hattı

`profile_page.dart` (~11.4k satır) iki view modu:
- **Dark mode**: legacy narrative card sistemi — pull quote, insight strip, feature rail, lead section, placement strip, side themes
- **Light mode** (`_ProfileRecoveryReadingBody`): `ProfileV8SectionsView` ile V8 adapter çıktısını render eder

Paralel 3 istek atılır:
- `/profile/fast` → 4 sn timeout, `ApiRequestSla.fast`
- `/interpret/ui` → 18 sn, `background`
- `/interpret` (legacy) → 18 sn, fallback

3-tab switch (main + relationship preview + calendar) mevcut. **Tasarımdaki "Tam Harita 4-tab modal"ı (Kimlik / İlişki / Kariyer / Gölge) henüz yok.**

---

## 2. Bulunan Sorunlar

### 2.1 🔴 Kritik — Tekrar Eden Hesaplamalar

| # | Sorun | Dosyalar | Etki |
|---|---|---|---|
| 1 | İki graph engine | `natal_graph.py` + `natal_graph_v2.py` | V1 her zaman, V2 flag'e bağlı; aynı aspect/ruler hesabı iki kez |
| 2 | İki primitive engine | `primitive_engine.py` + `primitive_engine_v2.py` | V1 hayalet (sadece test'te), V2 aktif |
| 3 | Üç profile narrative engine | `profile_narrative_engine.py` (wrapper) + `_legacy.py` + `_signature.py` | Runtime rollout; debug'da shadow mode → iki engine paralel çalışıyor |
| 4 | Atık composite fragments | `composite_fragments.py` + `composite_fragments_legacy.py` | Import edilmiş, **hiç çağrılmıyor** |
| 5 | Aspect/house/ruler 6+ kaynaktan parse | `dispositor_engine.py`, `natal_graph.py`, `natal_graph_v2.py`, `natal_feature_graph.py`, `primitive_engine_v2.py`, `aspect_bundle_selector.py` | Her modül kendi parsing'ini yapıyor; tek normalizasyon katmanı yok |
| 6 | İki core_story üreticisi | `core_story_tr_natal.py` (deterministic) + `narrative_binding.py` + `narrative_renderer_v26.py` (rule-based) | İkisi de payload'a girebilir |

### 2.2 🟡 Yapısal — Yarım Kalmış Sistemler

- **Selection V3** ([docs/natal_selection_v3.md](natal_selection_v3.md)): `master_selector.py`, `layer_arbitrator.py`, `natal_feature_graph.py` aktif — **ama public output'a değil debug dump'ına gidiyor**. Production mode'da feature flag kapalı; eski rule_engine + composite engine path'i kullanılıyor. Yani **omurga yazılmış, beslemiyor**.
- **Profile V8 backend builder**: [backend/app/natal/profile_v8_payload_builder.py](../backend/app/natal/profile_v8_payload_builder.py) import edilmiş, **hiç çağrılmıyor**. Mobile `profile_v8_adapter.dart` bunun yerine `/interpret/ui` ham payload'ından V8 sözleşmesini parse etmeye çalışıyor.
- **Narrative V2 spec uyuşmazlığı**: Spec 8 yeni alan tanımlıyor (`hook`, `lived_experience`, `mechanism`, `reflex`, `gift`, `growth_edge`, `what_it_builds`, `technical_anchor`) — backend hâlâ `core_story_ui` + `sections_v2` + `supporting_threads` + `personality_imprint` üretiyor. Mobile model olarak sadece `gift_tags` + `reflex_tags` mapped.

### 2.3 🟡 Dil Katmanı — Mekanik Kaçıyor

- Tüm phrase library'ler **statik string + `{key}` replacement**: `phrase_lib_tr_natal.py` (754 satır), `phrase_lib_tr_profile.py`, `core_story_tr_natal.py`, `signature_catalog_tr.py`, `signature_catalog_tr_extra.py`.
- **Hiç AI rewrite yok**. `JoviaSemanticNarrativeBuilder` (premium) sadece composite fragment'lar için; profile/natal anlatısına dokunmuyor.
- `voice_profile_resolver.py` var ama çıktısı sadece tone label'a etki ediyor; gerçek dil dokunuşu yapmıyor.
- Sonuç: Kullanıcı "Yükselen Oğlak seni sağlam durmaya çağırıyor. Yöneticin Saturn 3. evde..." gibi şablon hissi alıyor.

### 2.4 🟢 Performans — Önceliklendirilmesi gereken hot path

Tahmini süreler (cache miss ile, tek istek):
1. **Swiss Ephemeris** `compute_natal_chart()` — ~100-300ms
2. **Profile narrative signature engine** — ~100-200ms
3. **rule_engine.interpret()** — ~50-150ms (1000+ kural)
4. `LatentPotentialEngine` + `UpperMeaningEngine` — ~50-100ms
5. Graph V1 + V2 paralel çalıştığında — ekstra ~30-80ms
6. Paralel olabilen şeyler (composite layer'lar, dispositor, axis activation) seri çalışıyor.

Cache stratejisi sağlam ([backend/app/services/performance/cache_store.py](../backend/app/services/performance/cache_store.py)) ama cache miss olduğu ilk istekte kullanıcı **2-4 saniye boş ekran görüyor** (mobile telemetry: `profile_natal_load` span).

### 2.5 🟢 Mobile — Tasarım vs Mevcut Section Açığı

HTML mockup'tan **eksik / yarım** olan section'lar:

| Section | Adapter'da var mı | Render var mı | Backend payload var mı |
|---|---|---|---|
| Hero (avatar + isim + chip + Haritam) | ❌ yeni | ❌ | ✓ kısmen (sun/moon/rising) |
| Kimlik ekseni (pull quote) | ✓ `centerQuote` | ✓ light mode | ✓ `core_story_ui.headline` |
| Insight strip (Aura/Yönetici/İç ritim) | ✓ | ✓ | ✓ kısmen |
| "Seni farklı kılan" (stellium, exact aspects) | ✓ `uniqueBlock` | ✓ | 🟡 kısmen — exact orb metric eksik |
| **"Bu nereden geliyor olabilir" (geçmiş fragmentler)** | ✓ `originSection` | 🟡 light mode'da var, dark'ta yok | ❌ **henüz net değil** |
| İlk izlenim | ✓ | ✓ | ✓ |
| Yetenekler (Merk+Jüp / Ay-Venüs / Neptün 1.ev) | ✓ `talents` | ✓ | ✓ |
| Bu kişiyle ne konuşulur | ✓ `conversationSection` | ✓ | 🟡 kısmen |
| Seni nasıl etkiler | ✓ `effectSection` | ✓ | 🟡 kısmen |
| Savunma mekanizman | ✓ `defenseSection` | ✓ | ✓ `moon_defense_mechanism.py` |
| İlk hissedilen şey | ✓ `firstFeltSection` | ✓ | 🟡 |
| Kolektiften (forum tie-in) | ✓ `collectiveSection` | ✓ | ❌ forum bağlantısı yok |
| **Yakınlık · Ay 8. ev** | ✓ `intimacySection` | ❌ | ❌ özel motor yok |
| **Zihinsel işleyiş · Saturn 3. ev** | ✓ `mindSection` | ❌ | ❌ özel motor yok |
| Arketip portali CTA | ✓ `ctaSection` | ✓ | ✓ archetype profile var |
| **Tam Harita / Kimlik tab** (4 fragment + mekanizma + açılma + misyon) | ❌ | ❌ | 🟡 kısmen |
| **Tam Harita / İlişki tab** | ❌ | ❌ | 🟡 (relationship preview ayrı) |
| **Tam Harita / Kariyer tab** | ❌ | ❌ | ❌ |
| **Tam Harita / Gölge tab** (gölge fragmentler + açılan kapılar) | ❌ | ❌ | 🟡 contradiction_engine var |

---

## 3. Tasarımın Getirdiği Yeni İçerik İhtiyaçları

Tasarım sadece UI değişikliği değil — **yeni içerik kategorileri** istiyor:

### 3.1 "Bu nereden geliyor olabilir" — geçmiş fragmentler
- Çocukluk/erken yaşam çıkarımları: "Küçükken konuşmanın bir bedeli olduğunu öğrenmiş olabilirsin" (Saturn 3. ev), "Bir dönem her şeyi yalnız çözmen gerekti" (South Node Koç), "Sevdiğini tam gösteremedin" (Venus 12. ev), "Açıldığın bir an vardı — o an seni daha seçici yaptı" (Ay 8. ev).
- **Kaynak signature'lar**: South Node house+sign, Saturn ev+aspect, Chiron, Pluto/Venus zorlu açıları, 12. ev gezegenleri.
- **Yeni motor gerekli**: `past_layer_engine.py` (signature → past hint mapping).

### 3.2 "Açılma noktası" / "Açılan kapı"
- Growth direction: "Seni görmelerini beklemeyi bıraktığında, zaten görülüyorsun" — kullanıcının gölge yapısından çıkış vektörü.
- Mekanik olarak North Node + progression hedefleri + Saturn return + uzun vadeli gelişim eksenleri.
- **Yeni motor**: `opening_point_engine.py`. Mevcut `LatentPotentialEngine` ve `UpperMeaningEngine` veriyor ama dil dokunuşu eksik.

### 3.3 "Hayattaki misyon" — Lunar Nodes timeline
- South Node → Şu an → North Node 3-aşamalı zaman çizgisi.
- **Mevcut**: `promise_vector_engine.py` benzer şey üretiyor olabilir; Lunar Nodes için özel render gerekli.

### 3.4 "Gölge fragmentler" + "Açılan kapılar"
- 4 gölge fragment (örn: Oğlak aşırı ciddiyet, Ay Aslan kapanma, Saturn 3. ifade çekingenliği, geç kalma korkusu) + her biri için bir "açılan kapı" eşi.
- **Mevcut**: `contradiction_engine.py` çelişki imzaları üretiyor; gölge → kapı eşleştirmesi yapan bir `shadow_door_pairing.py` gerekli.

### 3.5 Yakınlık / Zihinsel işleyiş eksenleri
- Belirli bir gezegen-ev kombinasyonunun kişinin yaşam alanına nasıl yansıdığını anlatan derin section'lar.
- Yakınlık: Ay'ın bulunduğu ev + Venüs/Pluto teması.
- Zihinsel işleyiş: Merkür ev/açı + Saturn-Merkür dinamiği.
- **Mevcut**: `composite_interpreter.py` domain başına yorum üretiyor ama bu eksenel section formatına uymuyor.

### 3.6 Dil tonu — empatik, hikâye anlatır gibi
- Tasarımdaki tüm metinler **2.tekil şahıs**, **yumuşak, "olabilir" çekingenliği**, **çocukluk/geçmiş bağlamı**.
- "Saturn 3. evde, sen mantıklı düşünürsün" → "Küçükken konuşmanın bir bedeli olduğunu öğrenmiş olabilirsin. Artık söylemeden önce çok düşünüyorsun — bu oradan geliyor olabilir."
- Bu **dil katmanı işi**: ya prompt-driven LLM rewrite, ya da çok daha zengin slot-filling.

---

## 4. Yol Haritası

Toplam 4 faz. Her faz **bağımsız ship edilebilir** olmalı; bir sonraki faz öncekinin üzerine inşa eder.

---

### 🟢 Faz 0 — Temizlik & Ölçüm (1-2 hafta)

**Amaç**: Refactor öncesi durumu sabitle, körü körüne kod silmeden önce gerçek tüketimi gör.

**İşler**:
1. **Telemetri zenginleştir**: `_prepare_payload_from_chart()` her stage'i için `TimingRecorder.stage()` ile timing breakdown logla. Mobile'a `payload_size_bytes` per endpoint ekle.
2. **Ölü kod tespiti**: `composite_fragments.py`, `composite_fragments_legacy.py`, `primitive_engine.py` (V1) — gerçekten hiç çağrılmadıklarını test suite'i çalıştırarak doğrula. Çağrı yoksa Faz 1'de sil.
3. **Dual-call telemetrisi**: `natal_graph` V1+V2 her ikisi de çalışırken kim ne süre alıyor — log.
4. **Profile fast vs interpret/ui delta**: Mobile fast snapshot → public payload arası geçen süre + kullanıcının ekrana ne kadar baktığı.
5. **Spec-impl gap raporu**: `narrative_v2_product_spec.md` 8 alanı + production payload diff'i tek bir sayfada.

**Çıktı**: `docs/profile_v8_baseline_metrics.md` — şimdiki performans, kullanım, payload boyutu.

**Riski**: Düşük (sadece okuma + log).

---

### 🟢 Faz 1 — Konsolidasyon (2-3 hafta)

**Amaç**: Tek omurga, tek hesaplama, tek payload sözleşmesi.

**İşler**:
1. **Tek "natal context" katmanı**: Aspect/house/ruler/dispositor parse'ını tek `NatalContext` sınıfında topla ([backend/app/natal/natal_context.py] yeni). Tüm engine'ler bu context'i tüketir, kendi parsing'ini yapmaz.
2. **Selection V3'ü production mode'a geçir**: Feature flag'leri kaldır. `master_selector` çıktısı production payload'a beslesin. `natal_graph.py` V1'i emekliye ayır (deprecation comment + 1 release sonra sil).
3. **Profile narrative engine birleştirme**: `profile_narrative_engine.py` wrapper'ı kaldır; tek `signature` engine'e karar ver. Legacy ve shadow mode'u sil. Rollout hash'lemesi gerekli değilse production hard-cut.
4. **Profile V8 backend builder'ı aktive et**: `profile_v8_payload_builder.py` çağrılır hale getir. `_build_profile_fast_payload()` ile birleşsin. Çıktısı: `narrative_v2_product_spec.md`'deki 8 slot (`hook`, `lived_experience`, `mechanism`, `reflex`, `gift`, `growth_edge`, `what_it_builds`, `technical_anchor`).
5. **Ölü kod sil**: composite_fragments_legacy, primitive_engine V1, profile_narrative_engine_legacy.
6. **Public payload sözleşmesi sabitle**: Mobile `profile_v8_adapter.dart` için **tek bir contract dosyası** oluştur (`backend/app/natal/profile_v8_contracts.py` Pydantic + mobile karşılığı `profile_v8_models.dart`). Diff testleri ekle.

**Çıktı**:
- Backend payload boyutu **%20-30 küçülür** (legacy alanlar silinir).
- Compute süresi **%30-40 azalır** (dual graph + dual primitive + shadow narrative kalktığı için).
- Spec-impl gap kapanır.

**Riski**: Orta. Selection V3'ü prod'a açmak — golden test kapsamı ([docs/regression_watchlist.md](regression_watchlist.md)) burada hayati.

**Test stratejisi**: `tests/approval/test_natal_snapshots.py` (yoksa eklenir) ile 5-10 referans natal için before/after JSON snapshot karşılaştırması.

---

### 🟡 Faz 2 — Yeni Section Motorları (3-4 hafta)

**Amaç**: Tasarımdaki yeni section'lar için backend içerik motorlarını kur.

**İşler**:
1. **`past_layer_engine.py`** (yeni): South Node, Saturn-ev/aspect, 12. ev gezegenleri, Chiron → "Bu nereden geliyor olabilir" fragmentleri. Slot çıktısı: `{eyebrow, body, footnote, signature_chip}`.
2. **`opening_point_engine.py`** (yeni): North Node + Saturn return + JoviaWeighted growth signal'leri → "Açılma noktası" / "Açılan kapı" slot'u.
3. **`shadow_door_pairing.py`** (yeni): `contradiction_engine` çıktısı + opening_point eşleştirmesi → "Gölge fragmentler" + "Açılan kapılar" eş çiftleri.
4. **`life_mission_timeline.py`** (yeni): Lunar Nodes 3 aşamalı timeline (`south_node_pattern`, `current_phase`, `north_node_aim`) — promise_vector ile birleşebilir.
5. **`axis_section_builder.py`** (yeni): "Yakınlık (Ay X. ev)" ve "Zihinsel işleyiş (Saturn 3. ev)" gibi eksenel section'lar için tek motor. Composite engine üzerinde çalışır ama section formatına dönüştürür.
6. **Profile V8 payload genişletme**: Yukarıdaki 5 motorun çıktısını V8 contract'a ekle (`origin_section`, `intimacy_section`, `mind_section`, `mission_section`, `shadow_section`, `opening_section`).
7. **Tam Harita 4-tab payload**: Tek bir `/interpret/ui?view=full_chart` query'si veya ayrı `/profile/full_chart` endpoint — Kimlik / İlişki / Kariyer / Gölge tab payload'larını döndürür. Mobile bunu modal'da render eder.

**Çıktı**: 7 yeni section motoru + 4-tab Tam Harita payload sözleşmesi.

**Riski**: Orta-yüksek. Yeni motorların **astrolojik kalitesi** kritik — sadece "Saturn 3. ev → şu cümle" yapmaz; aspect, dispositor, ev yöneticisi gibi katmanları da hesaba katar.

**Test stratejisi**: 5-10 referans natal için **insan elinden onaylanmış altın çıktı**. Astrolog gözünden review.

---

### 🟡 Faz 3 — Dil Katmanı (LLM Rewrite + Voice Profile) (3-4 hafta)

**Amaç**: Mekanik şablon hissini kır. Empatik, hikâye anlatır gibi dil.

**İşler**:
1. **Slot-driven prompt mimarisi**: Her section motorunun ürettiği `{signature_chip, eyebrow, raw_body, raw_footnote, source_facts}` payload'ı tek bir prompt'a beslensin. Çıktı: tasarımdaki tonda 2-3 cümle.
2. **`JoviaEmpathicRewriter`** (yeni — `backend/app/ai/narrative/empathic_rewriter.py`): Groq → OpenAI fallback. Her section için 1 LLM çağrısı (paralel). Cache anahtarı: `(section_id, signature_hash, voice_profile)`.
3. **Voice profile entegrasyonu**: `voice_profile_resolver.py` çıktısı (örn. "introspective_warm") prompt sistem mesajına gömülür. Dil tonu kullanıcının kendi haritasına göre değişir.
4. **Specificity guard**: Generic cümleleri engelleyen post-process (regex + LLM judge). "Sen biraz duygusalsın" gibi cümleler düşürülür.
5. **Free vs Premium ayrımı**: Free user için ön-rewrite edilmiş 50-100 voice profile × signature kombinasyonu cache'lenir (offline batch). Premium user her seferinde fresh rewrite.
6. **Hız hedefi**: 7 section paralel rewrite → ~800-1500ms eklemeli süre. Cache hit %85+ olduğu varsayımıyla p50 etki: +100ms.

**Çıktı**: Profile metni tasarımdaki tona ulaşır. A/B test ile karşılaştırılabilir (rewrite on/off).

**Riski**: Yüksek (LLM güvenilirliği, halüsinasyon, maliyet).

**Maliyet**: Kullanıcı başına ilk açılış için ~1.5K token output × 7 section = ~10K token. Groq 8B model ile $0.0001/1K → ~$0.001/profile. Cache ile çok daha düşük.

---

### 🟡 Faz 4 — Mobile Tasarım Entegrasyonu (3-4 hafta)

**Amaç**: HTML mockup'taki yapıyı production Flutter'a getir.

**İşler**:
1. **Left-border accent card sistemi**: `JoviaAccentCard(color: lime|lavender|green|amber, eyebrow, body, footnote)` paylaşılan widget. Mevcut `_V8SectionCard` parametreleştirilir.
2. **Yeni section widget'ları**: `_V8PastLayerCard` (4 fragment list), `_V8IntimacyCard`, `_V8MindCard`, `_V8OpeningPointCard`, `_V8MissionTimelineCard` (3-aşamalı node timeline), `_V8ShadowFragmentCard`, `_V8OpenedDoorCard`.
3. **Profile dark mode → V8 sections geçişi**: `profile_page.dart` dark mode legacy narrative card sistemini sil, tek render path olarak V8 sections kullan. ~5K satır küçülme beklentisi.
4. **Tam Harita 4-tab modal**: Yeni `full_chart_page.dart` — 4 tab (Kimlik / İlişki / Kariyer / Gölge), her tab pull quote + section'lar. Hero'daki "Haritam" butonu buraya navigate eder.
5. **Hero redesign**: Yeni avatar + isim + chip + "Haritam" inline button. `@username`, social row (X takip · Y arkadaş), forum aktif badge.
6. **Tasarım token'ları**: Lime `#caff4d`, lavender `#7f77dd`, dark `#111`, off-white `#f5f5f8`, highlight bg'leri (`hi-lime`, `hi-lav`, `hi-stone`). [mobile/lib/design/tokens/](../mobile/lib/design/tokens/) altında token dosyalarına ekle.
7. **Forum tie-in**: "Kolektiften" section'ı için `forum/` modülü ile bağlantı — kullanıcının sun sign'ında aktif post sayısı + öne çıkan post.
8. **Animation pass**: Tasarımdaki `pulse` animasyonu (lime dot) + scroll reveal + section stagger. Curves: `easeOutCubic`, stagger `index * 60ms`.
9. **`profile_page_v2_experiment.dart` ve `experimental_profile_page.dart` deneylerini sil** — Faz 1'deki konsolidasyona paralel.

**Çıktı**: Tasarım production'da. Profile page ~50% kod küçülmesi.

**Riski**: Düşük-orta (sadece UI; backend sözleşmesi Faz 2'de oturmuş olur).

---

## 5. Önerilen Ölçüm / KPI

Faz 0'da baseline al, her faz sonunda yeniden ölç:

### Performans
- **p50 / p95 `/interpret/ui` süresi** (cache miss + cache hit ayrı)
- **p50 `/profile/fast` → first contentful paint** (mobile)
- **Mobile `profile_natal_load` span** süresi
- **Backend payload boyutu** (`/interpret/ui` response bytes)

### Kalite
- **Spec-impl coverage**: Narrative V2 8 alanından kaçı production'da çıkıyor (target: 8/8 Faz 1 sonrası).
- **Section coverage**: Tasarımdaki 18 section'dan kaçı render ediliyor (target: 18/18 Faz 4 sonrası).
- **Specificity score**: LLM judge ile ürettiği metnin "generic" oranı (target: <%10).
- **Astrolog review**: 10 referans natal için 1-5 puan (target: ≥4.0).

### Kod sağlığı
- **Backend natal/ + builders/ toplam satır sayısı** (target: %25 azalma Faz 1 sonrası).
- **Profile_page.dart satır sayısı** (target: 11.4k → ~5k Faz 4 sonrası).
- **Dual-call telemetri**: Aynı entity için tekrar parsing oranı (target: 0).

### İş etkisi
- **Profile sayfa retention**: ortalama scroll derinliği, section CTR.
- **Premium conversion**: Empatik dil + Tam Harita 4-tab modal sonrası premium upgrade oranı.

---

## 6. Risk ve Dikkat Noktaları

| Risk | Olasılık | Şiddet | Azaltma |
|---|---|---|---|
| Selection V3 prod'a açılınca regression | Orta | Yüksek | Golden snapshot test seti, kademeli %10 → %50 → %100 rollout |
| LLM rewrite halüsinasyon | Yüksek | Orta | Kaynak fact'leri prompt'ta zorunlu; LLM judge specificity check; fallback statik metne |
| LLM maliyet patlaması | Düşük | Orta | Voice × signature cache, free için offline batch |
| Mobile profile page refactor breaking | Orta | Yüksek | Faz 4'ü 2 alt-fazda yap (önce dark mode silinmeden V8 paralel, sonra dark mode kaldır) |
| Astrolojik doğruluk kaybı (yeni motorlar) | Orta | Yüksek | Astrolog elinden onaylanmış altın çıktı; her motor için ayrı review |
| Cache invalidation karmaşası | Orta | Orta | Payload version bump'ı her faz başında; `payload_versions.py` disiplini |

---

## 7. Hızlı Başlangıç Önerisi

Eğer bir hafta içinde **somut bir ilerleme** istenirse, şu sırayla başla:

1. **Gün 1-2**: Faz 0 telemetri + ölü kod tespiti.
2. **Gün 3-5**: Faz 1 — `composite_fragments_legacy`, `primitive_engine` V1, `profile_narrative_engine_legacy` sil. Test çalıştır.
3. **Gün 6-7**: Profile V8 payload contract'ını sabit yaz (Pydantic + Dart model). Mobile adapter'ı bu contract'a bağla.

Bu, **Faz 1'in %30'u** ve hemen ölçülebilir bir kazanç (payload küçülme, kod sadeleşme).

---

## 7.5 Ek Backlog (Faz dışı ama önemli)

Bu işler ana fazlara dahil değil ama uzun vadede ürün sağlığı için kritik. Her biri **bağımsız sprint** olarak ele alınabilir, herhangi bir fazın yanında paralel ilerleyebilir.

### 🌑 BL-02 — SwissEph extended ephe files deployment audit

**Şu anki sorun**:
- `backend/ephe/seas_18.se1` ve diğer extended dosyalar repo'da var.
- Üretim ortamında `app.main.create_app()` `swe.set_ephe_path(settings.swisseph_path)` çağırarak path'i set ediyor → çalışıyor.
- **Test ortamında** `create_app()` çağrılmıyor → `swe.set_ephe_path` set edilmiyor → Swiss Ephemeris sistem default path'inde (`/usr/share/swisseph`) arıyor → **Chiron, Juno, Vesta, Pallas hesaplanamıyor** (warning + None döner).
- Kısmi düzeltildi: `backend/tests/conftest.py` ile session-level `swe.set_ephe_path(settings.swisseph_path)` çağrısı eklendi (Sprint 1, 2026-04-17).
- **Geriye kalan risk**: Render production'da gerçekten tüm extended dosyalar deploy edildi mi? Build dizininde mevcut mu? Bunu doğrulamak için Render shell'den `ls /opt/render/project/src/backend/ephe/` kontrolü gerek.

**Önerilen aksiyon**:
1. Render production shell üzerinde ephe dizini doğrula
2. Eksik dosya varsa `render.yaml` build script'ine ephe download adımı ekle veya `.gitattributes` ile LFS migration
3. Test fixture'larına Chiron/Juno içeren kontrol case ekle (regression korumalı)

**Kazanç**: Astrolojik içerik kalitesi (Chiron Wounded Healer, Juno relationship asteroid, Vesta sacred work — natal yorumlamada Faz 2 motorları için kritik).

**Tahmini iş**: 2-4 saat.

---

### 🌍 BL-01 — Offline geocoding (OpenCage bağımlılığını kaldır)

**Şu anki sorun**:
- `backend/app/astro/chart_engine/builder.py:112-158` her yabancı şehir için OpenCage API'ye gidiyor.
- Sadece TR şehirleri (`_LOCAL_LOCATION_FALLBACKS` 14 entry) offline çözülüyor.
- API key olmadan yabancı kullanıcı kayıt **çökiyor** (test snapshot çalıştırırken yaşandı, 2026-04-17).
- Network latency (~100-500ms) her ilk açılışta hot path'te.
- API key paylaşma riski yüksek (ortam değişkenleri terminal log'larda sızabilir).

**Önerilen çözüm**:
1. **Birincil**: `pgeocode` veya `geonamescache` Python paketi — embedded GeoNames data (1.5M+ şehir), 0 network call, ~10-50ms response, no API key.
2. `_fallback_location()` mekanizmasını koru, global cities ile genişlet.
3. OpenCage **son çare** olarak kalsın (paket bulamazsa).

**Önerilen dosyalar**:
- Yeni: `backend/app/astro/chart_engine/geocoding.py` — offline çözücü
- Refactor: `backend/app/astro/chart_engine/builder.py` — `fetch_location` çağrı sırası: `_explicit_location` → `_fallback_location` → `geocoding.lookup_offline` → `fetch_location_opencage` (rename)
- Yeni env: `GEOCODING_BACKEND=offline_first` (default) / `opencage_only` / `offline_only`

**Test stratejisi**: Mevcut `test_chart_location_resolution.py` korunur, yeni `test_geocoding_offline.py` 50+ global şehir için fixture.

**Kazanç**:
- API key bağımlılığı sıfırlanır (production env'de bile)
- p50 chart compute süresi -100/300ms (network kalkar)
- Maliyet sıfırlanır (OpenCage: aylık $50+ rate limit hit olunca)
- Test reproducibility tam (network yok)

**Tahmini iş**: 1 hafta. Faz 1 sonrasında istenen herhangi bir zamanda alınabilir.

**Risk**: Düşük — `pgeocode` zaten production-tested kütüphane. Tek dikkat: timezone resolution için `tzwhere` veya `timezonefinder` ek paketi gerekebilir (lat/lng → tz).

---

## 8. Bu Dökümanı Güncelleme

- Her faz tamamlandığında **"Çıktı" satırının altına** gerçekleşen sonucu yaz.
- Yeni risk ortaya çıkarsa bölüm 6'ya ekle.
- Bu döküman ana dökümanın ([docs/ASTROLOGI_AI_MASTER.md](ASTROLOGI_AI_MASTER.md)) bölüm 13 cheat sheet'inde linklenmeli.

> **Çalışan plan**: Bu yol haritasının sprint bazlı uygulama planı: [docs/profile_v8_implementation_plan.md](profile_v8_implementation_plan.md)
