# Profile V8 — Baseline Metrikleri (Sprint 0 Çıktısı)

> Sprint 0 (2026-04-17 → 2026-05-01) çıktısı. Bu döküman, Faz 1 ve sonrası için referans noktası.
> Sprint backlog'u: [docs/profile_v8_implementation_plan.md](profile_v8_implementation_plan.md) Bölüm 2.

---

## 1. Telemetri Altyapısı (S0.1, S0.2, S0.3)

### Backend stage breakdown
[`_prepare_payload_from_chart()`](../backend/app/api/routes/natal_interpretation.py:1481) artık şu seviyede ölçülüyor:

**Ana stage'ler** (`prepare_stage_breakdown_ms`):
- `normalize_chart_inputs` — planet/aspect serialize + V1 graph build
- `selection_runtime` (V3 omurgası) — alt-stage'leri:
  - `selection_runtime.graph_v2`
  - `selection_runtime.feature_graph`
  - `selection_runtime.primitives_v2`
  - `selection_runtime.contradiction`
  - `selection_runtime.master_selector`
- `rule_engine` + alt-stage'leri (rule_engine.* — meta_eval, signature_select, vb.)
- `core_feature_layers` + 4 alt-stage (`feature_extract`, `weighting`, `pattern_context`, `aggregation`)
- `narrative_layers` + alt-stage:
  - `narrative_layers.semantic_build` (JoviaSemanticNarrativeBuilder.build())
- `surface_layers` + 4 alt-stage
- `prepare_debug_layers`

**Finalize stage'leri** (`finalize_stage_breakdown_ms`):
- `dynamic_insights`, `pattern_context`, `composite_meanings`, `upper_meaning_refresh`, `core_story_layers`, `finalize_debug_layers`, `finalize_payload`

### Debug payload (S0.2)
`/interpret/ui?debug=true` ve `/profile/fast?debug=true` artık response'a `_debug_timing` block'u ekler:
```json
{
  "_debug_timing": {
    "endpoint": "/interpret/ui",
    "cache_status": "miss",
    "cache_write": "stored",
    "total_ms": 1234.5,
    "stage_breakdown_ms": {...},
    "payload_bytes": 32456
  }
}
```

### Mobile telemetry (S0.3)
[`api_client.dart`](../mobile/lib/app/api/api_client.dart) artık her API request telemetri'sine **backend timing'i** lift eder:
- `backend_total_ms` — backend'in self-reported süresi
- `backend_cache_status`
- `backend_slowest_stage` + `backend_slowest_stage_ms` (en yavaş alt-stage otomatik)

**Network + parse delta** = `client_duration_ms` − `backend_total_ms`. Bu sayede mobile/network gecikmesi backend gecikmesinden ayrılabilir.

`payload_bytes` ve `payload_kb` zaten mevcuttu — değişmedi.

### Engine rollout log (S0.6)
[`profile_narrative_engine.py:147`](../backend/app/natal/narrative/profile_narrative_engine.py:147) artık her çağrıda log atıyor:
```
profile_narrative_engine_selection
  profile_narrative_engine: signature
  profile_narrative_engine_pre_force: legacy
  profile_narrative_legacy_force_promoted: true
  profile_narrative_engine_override_present: false
  profile_narrative_seed_key_hash: a3f1c8b9d4e5
  profile_narrative_migration_mode: legacy
  profile_narrative_include_debug: false
```

`debug=true` çağrıldığında ayrıca `profile_internal.engine_telemetry` payload'a girer.

---

## 2. Ölü Kod Tespiti (S0.4)

| Dosya | Durum | Audit'in dediği | Gerçek |
|---|---|---|---|
| `backend/app/builders/composite_fragments.py` | 🔴 **GERÇEKTEN ÖLÜ** | Ölü dedi | ✅ Doğru — sadece import + class def, hiç instantiate edilmiyor |
| `backend/app/builders/composite_fragments_legacy.py` | 🔴 **GERÇEKTEN ÖLÜ** | Ölü dedi | ✅ Doğru — hiç import yok |
| `backend/app/natal/narrative/primitive_engine.py` (V1) | 🟢 **CANLI** | Ölü dedi | ❌ **AUDIT YANLIŞ** — `build_primitives` 3 yerden çağrılıyor: `primitive_engine_v2.py:268`, `profile_narrative_engine_signature.py:1792`, `signature_engine.py` |
| `backend/app/natal/narrative/profile_narrative_engine_legacy.py` | 🟡 **ROLLOUT-AKTIF** | Wrapper'da kullanılıyor dedi | ✅ Doğru — `profile_narrative_engine.py:157` çağırıyor |

**Faz 1'de güvenle silinebilecekler**: `composite_fragments.py` + `composite_fragments_legacy.py` (2 dosya, ~?? satır).
**Faz 1'de silinemez**: `primitive_engine.py` (V1) — V2 ve signature engine bağımlılığı var; önce 3 callsite refactor edilmeli, sonra silinebilir.
**Faz 1 sonu Selection V3 %100 rollout sonrası silinebilir**: `profile_narrative_engine_legacy.py`.

---

## 3. Spec-Implementation Gap Raporu (S0.7)

### Narrative V2 spec'in 8 alanı vs production payload

| Spec alanı | Public payload'da var mı | Hangi alana map oluyor (mevcut) |
|---|---|---|
| `hook` | ❌ slot olarak yok | `core_story_ui.headline`, `profile_narrative.blocks[].headline` |
| `lived_experience` | ❌ slot olarak yok | `core_story_ui.text`, `personality_imprint.entries[].trait` |
| `mechanism` | 🟡 **domain olarak var, slot olarak yok** | `composite_layer["mechanism"]`, `profile_v8_payload_builder` `EditorialSectionPayload.body` (kısmi) |
| `reflex` | ❌ slot olarak yok | `personality_imprint.entries[].drive`, narrative bundle `reflex_tags` (mobile model'inde kısmi) |
| `gift` | 🟡 **kısmi** | `personality_imprint.entries[].gift`, `narrative_v2_aspect_bundle.gift_tags` (mobile model'de var) |
| `growth_edge` | ❌ slot olarak yok | `upper_meaning`, `latent_potential` ile karışmış |
| `what_it_builds` | ❌ slot olarak yok | `upper_meaning_selected.text` ile karışmış |
| `technical_anchor` | 🟡 **kısmi** | `narrative_v2_aspect_bundle.bundle_id`, `chips` |

**Coverage**: 8/8 hedefinden şu an **0/8 tam, 3/8 kısmi**.

### `profile_v8_payload_builder.py` — gizli zenginlik

[Bu dosya](../backend/app/natal/profile_v8_payload_builder.py) audit'te "import edilmiş ama çağrılmıyor" diye işaretlenmişti. **İçerik incelendiğinde aslında çok daha hazır**:

**Tanımlı dataclass'lar** (zaten yazılmış, kullanılmıyor):
- `ProfileV8Payload` — tasarımın **tüm section'ları** alanları olarak: `hero`, `identity_axis`, `insight_strip`, `differentiators`, `past_teaser`, `first_impression`, `talents`, `conversation_hooks`, `affects_you`, `defense`, `first_felt`, **`intimacy`**, **`mind`**, `mission_preview`, `archetype_portal`
- `FullMapV8Payload` + `FullMapTabPayload` — **4-tab modal** (kimlik, iliski, kariyer, golge) tam yapı: `pull_quote`, `past_fragments`, `mechanism`, `opening_point`, `mission`, `shadow_fragments`, `potentials`
- `MissionPayload` + `MissionStepPayload` — Lunar nodes 3-aşama timeline yapısı

**Hazır içerik motorları** (statik trigger tabloları):
- `PAST_LAYER_TRIGGERS` (4 örnek): `saturn_in_house_3`, `venus_in_house_12`, `moon_in_house_8`, `south_node_aries`
- `TALENT_RULES` (örn. `mercury_jupiter_signature`)
- Section scoring fonksiyonları (`score_fragment_for_section`, `_section_match_score`, `_placement_score`, vb.)

**Bağlama eksikliği**:
- Hiçbir route bu builder'ı çağırmıyor.
- Mobile `profile_v8_adapter.dart` bunun yerine `/interpret/ui` ham payload'ından parse etmeye çalışıyor.

### Etki — Faz 2 yeniden boyutlandırma

Audit'te Faz 2'de **5 yeni motor** yazılacak demiştik (`past_layer_engine`, `opening_point_engine`, `shadow_door_pairing`, `life_mission_timeline`, `axis_section_builder`). **`profile_v8_payload_builder.py` bunların ~%50-60'ını zaten içeriyor.**

Faz 2 işi yeniden:
- ✅ `past_layer_engine` → mevcut `PAST_LAYER_TRIGGERS`'ı genişlet (4 → 30+ trigger)
- ✅ `axis_section_builder` (intimacy/mind) → `FullMapTabPayload.mechanism` zaten var, daha fazla content rule eklenecek
- ✅ `life_mission_timeline` → `MissionPayload` + `MissionStepPayload` yapısı hazır, content kuralı yazılacak
- ⏳ `opening_point_engine` → `FullMapTabPayload.opening_point` slot'u var, motor yok
- ⏳ `shadow_door_pairing` → `shadow_fragments` + `potentials` slot'ları var, eşleştirme motoru yok

**Sonuç**: Faz 2 kapsamı **%30-40 daha küçük**. Çoğunlukla content kuralı + bağlama işi.

---

## 4. Performans Baseline (S0.9)

⚠️ **Henüz toplanmadı**. Mobile uygulamayı çalıştırıp 100+ profile açılışı telemetrisini Supabase'den çekmek gerekli. Sprint 0 sonuna kadar bunu sahaden topla.

**Topla**:
- `/interpret/ui` p50 / p95 (cache hit / miss ayrı)
- `/profile/fast` p50 / p95
- Mobile `profile_natal_load` span p50 / p95
- `payload_bytes` ortalama
- En yavaş 5 alt-stage (yeni `_debug_timing` ile)

**Tahmin (audit dayanağı)** — gerçek ölçüm beklenirken referans:
| Metrik | Tahmini baseline | Hedef (Faz 1 sonu) |
|---|---|---|
| `/interpret/ui` p50 (miss) | ~1200-1800 ms | ≤ 800 ms |
| `/interpret/ui` p95 (miss) | ~2500-4000 ms | ≤ 1500 ms |
| `/profile/fast` p50 | ~300-500 ms | ≤ 250 ms |
| `payload_bytes` | ~45-60 KB | ≤ 35 KB |
| Mobile profile FCP | ~4-6 sn | ≤ 2 sn |

---

## 5. Referans Natal Fixture'ları (S0.8)

Mevcut fixture'lar:
- `backend/tests/_fixtures/golden_days.json` (transit testleri için)
- `backend/tests/_fixtures/selection_benchmark_cases.json`

⚠️ **Natal-specific fixture yok**. Sprint 1'de oluşturulacak: `backend/tests/_fixtures/natal_v8_baseline.json` — 10 referans natal:
- 3× sun-rising kombinasyonu (Aslan/Aslan, Oğlak/Oğlak, Balık/Yengeç)
- 2× stellium ağırlıklı (1. ev 4+, 10. ev 3+)
- 2× kuvvetli açı paterni (T-square, Grand Trine)
- 2× nodal düğüm vurgusu (Koç-Terazi, Yengeç-Oğlak)
- 1× edge case (uçlarda gezegen, ev cusp'ında)

Her fixture için **before/after JSON snapshot** alınacak — Faz 1 refactor'larında diff kontrolü için.

---

## 6. Kod Sağlığı Baseline

| Metrik | Mevcut | Hedef (Faz 1 sonu) |
|---|---|---|
| `backend/app/natal/` toplam dosya | 16 | -2 (composite_fragments yok) |
| `backend/app/builders/` toplam dosya | 18 | -2 |
| `backend/app/api/routes/natal_interpretation.py` satır | 3151 + ~40 (S0.1) ≈ 3190 | İdeal: ≤ 2400 (Faz 1) |
| `profile_narrative_engine` sayısı | 3 (wrapper + legacy + signature) | 1 (Faz 1 sonu) |
| `natal_graph` sayısı | 2 (V1 + V2) | 1 (V2 only) |
| Atık import (composite_fragments) | 1 | 0 |
| `profile_v8_payload_builder.py` çağrı sayısı | 0 | ≥ 1 (production route'tan) |

---

## 7. Sprint 0 Sonuç & Sprint 1'e Hazırlık

### Tamamlananlar
- ✅ S0.1 Backend ince stage breakdown (selection_runtime alt-stage'leri + narrative_layers.semantic_build)
- ✅ S0.2 Debug timing block (`/interpret/ui`, `/profile/fast`)
- ✅ S0.3 Mobile telemetry backend timing extract
- ✅ S0.4 Ölü kod doğrulama (audit revize edildi: 2 dosya gerçek ölü, 1 audit yanlışı)
- ✅ S0.5 Dual-call telemetry (S0.1 ile birlikte)
- ✅ S0.6 Engine rollout dağılım log
- ✅ S0.7 Spec-implementation gap raporu

### Bekleyen
- ⏳ S0.8 — 10 referans natal fixture (Sprint 1 başında)
- ⏳ S0.9 — Mobile load timing distribution (sahadan toplama)
- ✅ S0.10 — Bu döküman

### Sprint 1'e taşınacak güncellemeler

1. **Plan revizyonu** ([profile_v8_implementation_plan.md](profile_v8_implementation_plan.md) Bölüm 4):
   - **S2.2** (`profile_v8_payload_builder.py` aktive et) → öncelik artırıldı, çünkü dosya zaten zengin.
   - **Faz 2 kapsamı küçültüldü** (5 yeni motor → ~3 yeni motor + 2 mevcut genişletme).
   - **Primitive engine V1'i silme** Faz 1'den çıkar, Faz 2'ye taşı (refactor gerek).

2. **Yeni risk**: `profile_v8_payload_builder.py` test coverage'ı bilinmiyor; Sprint 1'de mevcut test'leri (`test_profile_v8_payload_builder.py`) gözden geçir.

3. **Hedef revizyonu** (KPI tablosu, Bölüm 1.2):
   - "atık dosya sayısı: 4 → 0" hedefi → "2 → 0" (composite_fragments tamamı için).
   - "tek narrative engine" hedefi Faz 1 sonu yerine Faz 2 sonu.

---

## 8. Bu Dökümanı Güncelleme

- S0.8 ve S0.9 tamamlandığında **Bölüm 4 ve 5**'i revize et.
- Faz 1 sonu KPI ölçümü → **Bölüm 4 "Hedef" kolonunun yanına "Gerçekleşen"** ekle.
- Tahmin tablo değerleri yerine gerçek p50/p95 girildiğinde "Tahmin" kolonu silinir.
