# Profile V8 — Uygulama Planı ve Hedefler

> Bu, [docs/profile_v8_audit_and_roadmap.md](profile_v8_audit_and_roadmap.md) yol haritasının **çalışan plana** dönüşmüş hali.
> Sprint bazlı, ölçülebilir, sahiplik atamalı.
>
> Başlangıç: 2026-04-17 · Hedef ilk milestone (Faz 1 tamamı): 2026-06-15

---

## 0. Plan Özeti

| Faz | Süre | Sprint | Çıktı | Tamamlanma hedefi |
|---|---|---|---|---|
| **Faz 0** Temizlik & ölçüm | 2 hafta | S0 | Baseline metrikleri, ölü kod listesi, telemetri | 2026-05-01 |
| **Faz 1** Konsolidasyon | 4 hafta | S1, S2 | Tek omurga, Selection V3 prod, V8 contract | 2026-06-15 |
| **Faz 2** Yeni section motorları | 4 hafta | S3, S4 | 5 yeni motor + Tam Harita payload | 2026-07-15 |
| **Faz 3** Dil katmanı (LLM rewrite) | 4 hafta | S5, S6 | Empatik rewrite, voice profile | 2026-08-15 |
| **Faz 4** Mobile yeni tasarım | 4 hafta | S7, S8 | HTML mockup → Flutter production | 2026-09-15 |

**Toplam**: ~5 ay. Her faz **bağımsız ship edilir**, sonraki fazı bloke etmez.

---

## 1. Hedefler — Net KPI'lar

Her hedef için **(baseline / target)**. Baseline değerleri Faz 0 sonunda kesinleşir; aşağıdaki "?" değerler Sprint 0'da doldurulacak.

### 1.1 Performans hedefleri (Faz 1 sonu için)

| Metrik | Baseline | Hedef | Ölçüm noktası |
|---|---|---|---|
| `/interpret/ui` p50 (cache miss) | ? ms | **≤ 800 ms** | backend timing log |
| `/interpret/ui` p95 (cache miss) | ? ms | **≤ 1500 ms** | backend timing log |
| `/profile/fast` p50 | ? ms | **≤ 250 ms** | backend timing log |
| Mobile `profile_natal_load` p50 | ? ms | **≤ 2000 ms** | PerfTelemetry |
| `/interpret/ui` payload boyutu | ? KB | **≤ 35 KB** | response size |
| Cache hit oranı (`profile_natal`) | ? % | **≥ 75%** | cache_store metrics |

### 1.2 Kod sağlığı hedefleri (Faz 1 sonu)

| Metrik | Baseline | Hedef |
|---|---|---|
| `backend/app/natal/` + `builders/` toplam satır | ? | **−25%** |
| Atık dosya sayısı (import edilmiş ama çağrılmamış) | ≥ 4 | **0** |
| Aynı entity için tekrar parse sayısı (graph/primitive/aspect) | 6+ | **1** |
| `profile_narrative_engine` sayısı | 3 (wrapper + legacy + signature) | **1** |
| `natal_graph` sayısı | 2 (V1 + V2) | **1** (V2 only) |

### 1.3 İçerik kalitesi hedefleri (Faz 2 sonu)

| Metrik | Baseline | Hedef |
|---|---|---|
| Narrative V2 spec coverage (8 alan) | 0/8 | **8/8** |
| HTML mockup section coverage (18 section) | ~10/18 | **18/18** |
| Astrolog review skoru (10 referans natal, 1-5) | ? | **≥ 4.0 ortalama** |
| Generic cümle oranı (LLM judge) | ? % | **≤ %10** |

### 1.4 Mobile UI hedefleri (Faz 4 sonu)

| Metrik | Baseline | Hedef |
|---|---|---|
| `profile_page.dart` satır sayısı | ~11.4k | **≤ 5k** |
| Tasarım fidelity (HTML mockup vs prod) | – | **%95+ pixel match** |
| Dark mode + light mode rendering path sayısı | 2 | **1** |

### 1.5 İş etkisi hedefleri (Faz 4 sonu)

| Metrik | Baseline | Hedef |
|---|---|---|
| Profile sayfa ortalama scroll derinliği | ? | **+%30** |
| "Tam Harita" CTA tıklama oranı | – | **≥ %40** (yeni özellik) |
| Premium upgrade conversion (profile → upgrade) | ? | **+%15** |

---

## 2. Sprint 0 — Baseline & Telemetri (2 hafta)

**Tarih**: 2026-04-17 → 2026-05-01
**Faz**: 0
**Risk**: Düşük (sadece okuma + log eklemek)

### Backlog

| # | İş | Tahmin | Dosya | Tamamlandı |
|---|---|---|---|---|
| S0.1 | Backend `_prepare_payload_from_chart()` her stage'i `TimingRecorder.stage()` ile sar | 0.5 gün | `backend/app/api/routes/natal_interpretation.py` | ☐ |
| S0.2 | `/interpret/ui` ve `/profile/fast` response'una `_debug_timing` block ekle (debug mode only) | 0.5 gün | aynı | ☐ |
| S0.3 | Mobile `PerfTelemetry`'ye `payload_bytes` ve `parse_duration_ms` ekle | 0.5 gün | `mobile/lib/app/api/api_client.dart` | ☐ |
| S0.4 | Ölü kod doğrulama: `composite_fragments.py`, `composite_fragments_legacy.py`, `primitive_engine.py` (V1) — `grep -r` + test çalıştır, **çağrı yoksa listele** | 1 gün | — | ☐ |
| S0.5 | `natal_graph` V1 + V2 dual-call telemetrisi: hangi flag açıkken hangisi çalışıyor, kaç ms | 1 gün | `natal_interpretation.py:1543-1584` | ☐ |
| S0.6 | `profile_narrative_engine` rollout dağılımı: hangi user yüzdesi legacy/signature alıyor | 0.5 gün | `profile_narrative_engine.py:42-55` | ☐ |
| S0.7 | Spec-impl gap raporu: Narrative V2 8 alanından hangileri payload'da var/yok | 0.5 gün | `narrative_v2_product_spec.md` vs `_build_public_natal_view()` | ☐ |
| S0.8 | 10 referans natal seç (farklı sun/moon/asc kombinasyonları) — JSON snapshot al | 1 gün | `tests/approval/fixtures/` | ☐ |
| S0.9 | Mobile profile load timing distribution: 100+ açılıştan p50/p95 al | 0.5 gün | telemetry pipeline | ☐ |
| S0.10 | `docs/profile_v8_baseline_metrics.md` yaz: tüm baseline değerler tek dökümanda | 0.5 gün | `docs/` | ☐ |

**Toplam**: ~6.5 gün iş, 2 hafta süre.

> **🌍 Yeni backlog item**: BL-01 — Offline geocoding (OpenCage bağımlılığını kaldır). Detay: [audit doc Bölüm 7.5](profile_v8_audit_and_roadmap.md#75-ek-backlog-faz-d%C4%B1%C5%9F%C4%B1-ama-%C3%B6nemli). Faz dışı, herhangi bir sprint yanında paralel ele alınabilir. Tahmini 1 hafta.

### Sprint 0 başarı kriteri

- 🟡 KPI tablosundaki "?" değerler — telemetri hazır, sahadan toplama bekleniyor (S0.9).
- ☑ Ölü kod listesi onaylandı (Sprint 1'de silinecek): `composite_fragments.py`, `composite_fragments_legacy.py` (audit revize edildi — `primitive_engine.py` V1 canlı çıktı).
- ⏳ 10 referans natal snapshot — Sprint 1 başına taşındı (S0.8 deferred).
- ☑ `docs/profile_v8_baseline_metrics.md` yazıldı, review bekliyor.

> **Önemli bulgu (Sprint 0)**: [`profile_v8_payload_builder.py`](../backend/app/natal/profile_v8_payload_builder.py) audit'te düşünülenden çok daha hazır — `ProfileV8Payload`, `FullMapV8Payload` (4 tab modal), `PAST_LAYER_TRIGGERS`, `TALENT_RULES` zaten yazılmış. Faz 2 kapsamı **%30-40 küçüldü**. Detay: baseline doc Bölüm 3.

### Sprint 0 riskleri

| Risk | Azaltma |
|---|---|
| Telemetri PII sızdırır | Birth data hashlenir, request body loglanmaz |
| Snapshot fixture'larda gerçek user data | Sentetik test profilleri kullan |

---

## 3. Sprint 1 — Konsolidasyon Başlangıç (2 hafta)

**Tarih**: 2026-05-01 → 2026-05-15
**Faz**: 1
**Risk**: Orta

### Backlog

| # | İş | Tahmin | Onay gerek? |
|---|---|---|---|
| S1.1 | Ölü kod silme: `composite_fragments.py`, `composite_fragments_legacy.py`, `primitive_engine.py` V1, `profile_narrative_engine_legacy.py` | 0.5 gün | ✓ — silmeden önce sor |
| S1.2 | `profile_narrative_engine.py` wrapper'ı kaldır, doğrudan signature engine'e geçiş | 1 gün | ✓ |
| S1.3 | `NatalContext` katmanı: aspect/house/ruler/dispositor parse'ı tek yerde | 2 gün | ✓ — yeni servis |
| S1.4 | Mevcut engine'leri (`natal_graph_v2`, `natal_feature_graph`, `primitive_engine_v2`, `aspect_bundle_selector`) `NatalContext`'i tüketmeye geçir | 2 gün | ✗ |
| S1.5 | Selection V3 feature flag'lerini production'da %10 canary aç | 1 gün | ✓ — canary kararı |
| S1.6 | Golden snapshot test seti: Sprint 0'daki 10 fixture için before/after JSON diff | 1 gün | ✗ |
| S1.7 | Regression watchlist'teki 6 senaryoyu manuel test et | 1 gün | ✗ |

### Sprint 1 başarı kriteri

- ☐ 4 atık dosya silindi, test'ler geçiyor.
- ☐ Tek `NatalContext` aktif, en az 4 engine onu tüketiyor.
- ☐ Selection V3 %10 canary'de stabil (24 saat error rate < %0.1).
- ☐ Golden snapshot diff'leri kabul edildi (varyasyon kasıtlı).

---

## 4. Sprint 2 — Konsolidasyon Tamamlama (2 hafta)

**Tarih**: 2026-05-15 → 2026-05-29
**Faz**: 1

### Backlog

| # | İş | Tahmin |
|---|---|---|
| S2.1 | `natal_graph.py` V1'i emekliye ayır — sadece V2 (Selection V3 omurgası) | 1 gün |
| S2.2 | `profile_v8_payload_builder.py` aktive et — `_build_profile_fast_payload` ile birleştir | 2 gün |
| S2.3 | Profile V8 payload contract sabit: `backend/app/natal/profile_v8_contracts.py` (Pydantic) | 1 gün |
| S2.4 | Mobile `profile_v8_models.dart` contract karşılığı + adapter güncelle | 1 gün |
| S2.5 | Narrative V2 8 alanı (`hook`, `lived_experience`, `mechanism`, `reflex`, `gift`, `growth_edge`, `what_it_builds`, `technical_anchor`) production payload'a girecek şekilde mapping | 2 gün |
| S2.6 | Selection V3 canary %10 → %50 → %100 rollout | 1 gün (3 gün canary süresi dahil değil) |
| S2.7 | Payload version bump (`payload_versions.py`) — eski cache invalidate | 0.5 gün |
| S2.8 | Faz 1 sonu KPI ölçümü, hedef vs gerçekleşen tablosu | 0.5 gün |

### Sprint 2 başarı kriteri (= Faz 1 milestone)

- ☐ KPI 1.1 hedefleri sağlandı (`/interpret/ui` p50 ≤ 800ms, payload ≤ 35KB).
- ☐ KPI 1.2 hedefleri sağlandı (kod %25 küçüldü, atık 0, tek narrative engine).
- ☐ Profile V8 contract her iki tarafta da yaşıyor.
- ☐ Selection V3 production'da %100.

---

## 5. Faz 2-4 İskeleti (Sonraki Sprint'ler)

Detaylı backlog Faz 1 bittiğinde yazılır. İskelet:

### Sprint 3-4 (Faz 2): Yeni section motorları
- `past_layer_engine.py` (geçmiş katmanları)
- `opening_point_engine.py` (açılma noktası)
- `shadow_door_pairing.py` (gölge ↔ açılan kapı eşleri)
- `life_mission_timeline.py` (lunar nodes 3-aşama)
- `axis_section_builder.py` (yakınlık + zihinsel işleyiş)
- Tam Harita 4-tab payload (`?view=full_chart`)

### Sprint 5-6 (Faz 3): Dil katmanı
- `JoviaEmpathicRewriter` (Groq → OpenAI fallback)
- Voice profile prompt entegrasyonu
- Specificity guard (LLM judge)
- Free için offline batch cache

### Sprint 7-8 (Faz 4): Mobile yeni tasarım
- `JoviaAccentCard` paylaşılan widget (lime/lavender/green/amber left border)
- 7 yeni section widget
- Dark mode legacy → V8 sections geçiş
- Tam Harita 4-tab modal (`full_chart_page.dart`)
- Hero redesign + animation pass

---

## 6. Karara Bağlanması Gerekenler

Plana başlamadan önce **netleşmesi gereken** kararlar (✅ = 2026-04-17 onaylandı).

| # | Karar | Sonuç |
|---|---|---|
| K1 | **Çalışan kapasitesi & astrolog reviewer** | ✅ **Sen + Claude Code çift.** Faz 0-1'de astrolog reviewer = **sen (Sahra)**. Faz 2'de dış astrolog danışmanı devreye alınacak. |
| K2 | **Faz öncelik sırası** | ✅ **Sıralı** (0 → 1 → 2 → 3 → 4). Faz 4 (mobile yeni tasarım) öne alınmaz; backend sözleşmesi önce oturur. |
| K3 | **Selection V3 canary stratejisi** | ✅ **Kademeli rollout**: %10 → %50 → %100. S1.5'te %10 başla, 24 saat error rate < %0.1 ise S2.6'da %50, 48 saat sağlam ise %100. **Render env var**: `SELECTION_V3_ROLLOUT_PCT=10` (default 0). Hash bazlı per-user (SHA256(seed_key) % 100 < pct), deterministik. Boolean phase flag'ler hâlâ override (herhangi biri true → herkese açık). Telemetri: `selection_v3_rollout_decision` log event'i her request'te basılır. |
| K4 | **LLM provider önceliği (Faz 3)** | ✅ **Default: Groq → OpenAI fallback** (mevcut zincir). Premium akış için OpenAI birincil. |
| K5 | **Astrolog review bütçesi (Faz 2)** | ✅ Faz 2 başlamadan önce dış astrolog danışmanı seçilir. Sahra Faz 0-1 review'larını kendi yapar. |
| K6 | **Mobile rollout (Faz 4)** | ✅ TestFlight beta 1 hafta → store release. |
| K7 | **Dark mode geçişi (Faz 4)** | ✅ Legacy dark mode silinir; `profile_page_v2_experiment.dart` ve `experimental_profile_page.dart` da bu fazda temizlenir. |
| K8 | **Backward compatibility** | ✅ `?contract_version=v8` query param ile her iki contract serve edilir. 1 release sonra eski contract kaldırılır (deprecation header ile). |

---

## 7. Risk ve Blocker Takibi

| Risk | Olasılık | Şiddet | Sahip | Azaltma |
|---|---|---|---|---|
| Selection V3 prod'da regression | Orta | Yüksek | TBD | Golden snapshot, kademeli canary |
| Cache invalidation yangını | Orta | Orta | TBD | Payload version bump disiplini |
| LLM maliyet patlaması | Düşük | Orta | TBD | Voice × signature cache, rate limit |
| Astrolog reviewer bulunamaması | Orta | Yüksek | TBD | Faz 2 içerik kalite gate'i kayar |
| Mobile build kırılma (Faz 4) | Orta | Yüksek | TBD | 2 alt-faz: önce paralel, sonra cleanup |
| Backend payload contract değişikliği eski mobile'ı kırar | Yüksek | Yüksek | TBD | `contract_version` query param |

---

## 8. Haftalık Ritim

- **Pazartesi**: Sprint backlog review, blocker tarama.
- **Çarşamba**: Mid-sprint check, KPI dashboard güncelleme.
- **Cuma**: Demo + sprint snapshot. Bu dökümandaki "Tamamlandı" kutucuğu işaretle.
- **Sprint sonu**: KPI hedef vs gerçekleşen, sonraki sprint backlog yazımı.

---

## 9. Bu Dökümanı Güncelleme

- Her sprint sonunda **"Tamamlandı"** kutucuklarını işaretle (☐ → ☑).
- Hedef değerler değişirse **Bölüm 1** revize, gerekçesi commit message'da.
- Yeni risk → **Bölüm 7**'ye ekle.
- Karara bağlanan K# → **Bölüm 6** üzerine "✅ karar: ..." satırı.
- Faz tamamlanınca **Bölüm 0**'daki tabloda durum güncelle ve [docs/ASTROLOGI_AI_MASTER.md](ASTROLOGI_AI_MASTER.md) bölüm 12'deki roadmap'i de güncelle.

---

## 10. Sonraki Aksiyon

**Bu plan onaylandığında**:
1. Bölüm 6'daki K1-K8 kararları netleşir → her birinin yanına "✅ karar: ..." yazılır.
2. Sprint 0 backlog'u (S0.1-S0.10) tek tek issue/task olarak ele alınır.
3. İlk iş: **S0.1 — `_prepare_payload_from_chart()` timing instrumentation**.

Onay vermeden önce K1-K8 kararlarını gözden geçir.
