# Performance Instrumentation Report

## Kısa Özet

Bu değişiklik seti davranışı değiştirmeden startup, auth, profile ve natal hot path etrafına düşük riskli structured performance telemetry ekler.
Ana amaç şunları görünür hale getirmektir:

- app açılış milestone süreleri
- profile first-open akışındaki provider, request ve fallback kararları
- mobile API client tarafında süre, payload boyutu, cache ve inflight dedupe
- backend `/interpret/ui` ve `/interpret` stage breakdown
- `/profile/fast` timing loglarında PII içermeyen request summary

## Değişen Dosyalar

- `mobile/lib/app/telemetry/perf_telemetry.dart`
- `mobile/lib/main.dart`
- `mobile/lib/app/splash/splash_screen.dart`
- `mobile/lib/app/auth/auth_gate.dart`
- `mobile/lib/app/tabs/tabs_shell.dart`
- `mobile/lib/app/tabs/home_page.dart`
- `mobile/lib/app/api/api_client.dart`
- `mobile/lib/app/profile/profile_providers.dart`
- `mobile/lib/app/people/people_providers.dart`
- `mobile/lib/app/profile/profile_repository.dart`
- `mobile/lib/app/tabs/profile_page.dart`
- `backend/app/api/routes/natal_interpretation.py`

## Eklenen Event Listesi

### Mobile Startup

- `app_launch_start`
- `splash_visible`
- `auth_gate_start`
- `auth_gate_resolved`
- `tabs_shell_visible`
- `first_home_visible`

### Mobile API Client

- `api_request_start`
- `api_request_end`
- `api_request_deduped`

Her request logunda şu alanlar bulunur:

- `endpoint`
- `method`
- `request_sla`
- `status_code`
- `start_ms`
- `end_ms`
- `duration_ms`
- `payload_bytes`
- `payload_kb`
- `cache_status`
- `cache_store`
- `inflight_dedupe`

### Profile Surface

- `profile_first_open`
- `profile_reopen_same_session`
- `profile_tab_first_build`
- `profile_natal_load_start`
- `profile_natal_load_end`
- `interpret_ui_request_start`
- `interpret_ui_request_end`
- `profile_fast_request_start`
- `profile_fast_request_end`
- `interpret_legacy_request_start`
- `interpret_legacy_request_end`
- `fallback_used`
- `fallback_skipped`
- `profile_payload_shape`
- `archetype_summary_load_start`
- `archetype_summary_load_end`
- `first_meaningful_profile_content_visible`

### Provider / Repository

- `userProfileProvider_resolve_start`
- `userProfileProvider_resolve_end`
- `peopleListProvider_resolve_start`
- `peopleListProvider_resolve_end`
- `profile_loaded_from_cache`
- `profile_loaded_from_network`
- `profile_repository_inflight_dedupe`
- `birth_gate_profile_loaded_from_cache`
- `birth_gate_profile_inflight_dedupe`
- `profile_repository_fetch_start`
- `profile_repository_fetch_end`
- `birth_gate_profile_fetch_start`
- `birth_gate_profile_fetch_end`

### Backend Natal Routes

Event name değişmedi, ama JSON payload genişletildi:

- `natal_timing`
- `profile_fast_timing`

Yeni alanlar:

- `request_summary`
- `payload_shape`
- `stage_breakdown_ms`
- `status`
- `error_type`

## Ölçülebilir Hale Gelen Metrikler

- App launch ile splash, auth, tabs shell ve first home arasındaki sıra ve süreler
- Auth gate’in tabs, onboarding, login veya retry’a kaç ms’de çözüldüğü
- `userProfileProvider` ve `peopleListProvider` resolve süreleri
- Profile first-open’da natal load’ın toplam süresi
- `/interpret/ui`, `/profile/fast`, `/interpret` çağrılarının mobile tarafındaki gerçek request süreleri
- Mobile client cache hit/miss ve inflight dedupe oranı
- Legacy fallback’in ne zaman ve hangi reason code ile tetiklendiği
- Natal payload’ın kritik üst alanlarının var/yok bilgisi
- Backend `/interpret/ui` içinde input normalize, chart/payload preparation, public build ve response finalize stage süreleri
- Backend `/interpret` legacy yolunun stage süreleri
- `/profile/fast` cache hit/miss ve timing breakdown

## Risk Notları

- Mobile telemetry `developer.log` kullanır; payload içeriği yerine shape ve metadata loglanır.
- Backend natal loglarında raw `birth_place` kaldırıldı; yerine hash/masked request summary geldi.
- Instrumentation minimal tutuldu, fakat payload boyutu hesabı request başına küçük ek CPU maliyeti ekler.
- Riverpod provider resolve logları provider her yeniden çalıştığında tekrar üretilebilir; bu bilinçli bırakıldı çünkü amaç tekrar hesapları görmek.
- `profile_reopen_same_session` ana tab revisits için `TabsShell`, yeni page instance açılışları için `ProfilePage` init üzerinden gelebilir.

## Nasıl Test Edilir

1. Uygulamayı cold start ile aç.
2. Console’da `mobile.perf` loglarını izle.
3. Login sonrası auth gate, tabs shell ve home milestone sırasını doğrula.
4. Profile tab’ını ilk kez aç; `profile_first_open`, `profile_tab_first_build`, provider resolve ve natal request eventlerini izle.
5. `/interpret/ui` boş veya zayıf payload dönerse `fallback_used` ve ardından `/interpret` request loglarını doğrula.
6. Aynı profile tekrar dön; `profile_reopen_same_session` eventini kontrol et.
7. Backend loglarında `natal_timing` ve `profile_fast_timing` JSON payload’larını izle.

## Örnek Beklenen Log Akışları

### Startup

```json
{"event":"app_launch_start","uptime_ms":0}
{"event":"splash_visible","uptime_ms":18}
{"event":"auth_gate_start","has_session":true}
{"event":"auth_gate_resolved","target":"tabs","duration_ms":143}
{"event":"tabs_shell_visible","initial_index":0}
{"event":"first_home_visible","uptime_ms":812}
```

### Profile First Open

```json
{"event":"profile_first_open","source":"profile_page_init"}
{"event":"profile_tab_first_build","source":"profile_page"}
{"event":"userProfileProvider_resolve_end","duration_ms":42,"has_profile":true}
{"event":"peopleListProvider_resolve_end","duration_ms":85,"count":3}
{"event":"profile_natal_load_start","surface":"profile_page"}
{"event":"interpret_ui_request_end","endpoint":"/interpret/ui","duration_ms":1280,"payload_bytes":18452,"cache_status":"miss"}
{"event":"profile_fast_request_end","endpoint":"/profile/fast","duration_ms":220,"payload_bytes":1180,"cache_status":"hit"}
{"event":"fallback_skipped","reason_code":"not_needed","elapsed_ms":1292}
{"event":"first_meaningful_profile_content_visible","fallback_used":false,"summary_present":true}
{"event":"profile_natal_load_end","duration_ms":1355,"fallback_used":false}
```

### Fallback Triggered

```json
{"event":"interpret_ui_request_end","endpoint":"/interpret/ui","result_empty":true,"failure_reason":"schema_mismatch"}
{"event":"fallback_used","reason_code":"schema_mismatch","elapsed_ms":910}
{"event":"interpret_legacy_request_end","endpoint":"/interpret","duration_ms":1640}
{"event":"profile_natal_load_end","fallback_used":true,"fallback_reason":"schema_mismatch"}
```

### Backend `/interpret/ui`

```json
{
  "endpoint": "/interpret/ui",
  "status": "ok",
  "request_summary": {
    "request_key": "8b1d2f43c1a2",
    "birth_date_masked": "1996-12-xx",
    "birth_place_hash": "a1b2c3d4e5",
    "has_coordinates": true,
    "summary_only": false
  },
  "stage_breakdown_ms": {
    "request_received": 0.0,
    "input_normalize": 0.1,
    "chart_payload_preparation": 1240.3,
    "public_natal_build": 211.4,
    "response_finalize": 3.2
  },
  "payload_bytes": 28491,
  "payload_shape": {
    "has_sections_v2": true,
    "has_supporting_threads": true,
    "has_core_story_ui": true
  }
}
```

## Bu Instrumentation ile Artık Cevaplanabilir Sorular

- Cold start’ın en pahalı aşaması splash sonrası auth gate mi yoksa first home render mı?
- Profile first-open yavaşlığı provider resolve’dan mı, `/interpret/ui`’dan mı, yoksa legacy fallback’ten mi geliyor?
- `/profile/fast` çoğu zaman cache hit mi oluyor?
- `/interpret/ui` boş veya zayıf shape ile dönüyorsa hangi reason code fallback’i tetikliyor?
- Mobile client cache ve inflight dedupe tekrar request maliyetini ne kadar azaltıyor?
- Backend `/interpret/ui` maliyeti en çok chart/payload preparation’da mı birikiyor?

## Runtime veya Infra Desteği Gerektiren Kalan Noktalar

- Log aggregation, dashboard ve percentile analizi için merkezi log pipeline gerekli.
- Session bazlı funnel/trace correlation için server-client ortak trace id standardı henüz eklenmedi.
- Release build’de sampling veya remote toggle yok; şimdilik log hacmi kod seviyesinde sınırlı tutuldu.
- Supabase query-level telemetry bu task kapsamında eklenmedi; profile row ve people list için repository/provider seviyesinde ölçüm var.

## Sonraki İlk 5 Analiz Önerisi

1. `profile_natal_load_end` eventlerini `fallback_used=true/false` diye ayırıp p50/p95 karşılaştır.
2. `/interpret/ui` backend `stage_breakdown_ms.chart_payload_preparation` dağılımını çıkar.
3. `profile_fast_timing.cache_status` hit oranını kullanıcı başına ve session başına incele.
4. `api_request_deduped` ve `cache_status=hit` oranlarını `endpoint` bazında grupla.
5. `first_home_visible` ile `tabs_shell_visible` arasındaki farkı cold start ve warm resume olarak ayrı incele.
