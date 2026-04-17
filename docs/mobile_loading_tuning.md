# Mobile Loading Tuning

## Single source of truth

Mobile tarafındaki home/profile yükleme süreleri ve cache TTL ayarları artık:

- `mobile/lib/app/performance/load_tuning.dart`

üzerinden yönetilmeli.

## Home critical path

Home ekranında dört bağımsız iş var:

- `home/fast` preview
- `/transit/narrative` home payload
- `/interpret/ui` natal summary
- `/sky/now` sky feed

Kural:

- `home/fast` hiçbir zaman gerçek narrative isteğini bloklamamalı.
- `home/fast` sadece erken fallback/prefill kaynağıdır.
- Günlük transit için source of truth önce `daily_event_cards`, sonra selected-day `calendar.days`, en sonda gerekiyorsa `calendar_day/full` fallback’idir.
- Home için `transit/narrative` isteklerinde client cache kullanılmamalı. Aksi halde ilk boş payload birkaç dakika boyunca UI'ı boş gösterebilir.
- Backend tarafında `payload_profile=home` veya `calendar_day` için boş public payload cache'e yazılmamalı.

## Profile critical path

Profile ekranında iki katman var:

- `/profile/fast`: hızlı snapshot, özellikle `sun/moon/rising`
- `/interpret/ui` ve gerekirse `/interpret`: ağır anlatı payload’ı

Kural:

- `profile/fast` sonucu gelince sign chip’leri hemen güncellenmeli.
- Ağır yorum payload’ı bununla paralel çalışmalı; hızlı snapshot tamamlanmadan tam profil render’ı beklenmemeli.
- Legacy `/interpret` fallback’i sadece `interpret/ui` gerçekten boş ya da yetersizse devreye girmeli.

## Değişiklik yaparken korunacak invariants

- Home’da `fast` preview daha güçlü bir günlük kartı ezmemeli.
- Home’da preview isteği yavaşsa narrative isteği yine hemen başlamalı.
- Profile’da hızlı snapshot başarısız olsa bile ağır payload akışı devam etmeli.
- Timeout ve TTL değerleri ekran dosyalarına dağılmamalı; yeni değerler önce `load_tuning.dart` içine taşınmalı.

## Ayarları nereden değiştirirsin

- Home fast timeout: `LoadTuning.homeFastTimeout`
- Home narrative timeout: `LoadTuning.homeNarrativeTimeout`
- Home week hydrate timeout: `LoadTuning.homeWeekNarrativeTimeout`
- Home retry delay/count: `LoadTuning.homeFastDeferredRetryDelay`, `LoadTuning.maxHomeFastDeferredRetries`
- Profile fast timeout: `LoadTuning.profileFastTimeout`
- Profile interpret timeout: `LoadTuning.profileInterpretUiTimeout`
- Profile legacy timeout: `LoadTuning.profileLegacyInterpretTimeout`
- Home/Profile cache TTL’leri: aynı dosyadaki ilgili `...CacheTtl` sabitleri

## Regression checks

UI yükleme akışına dokunduktan sonra en az şunlar çalıştırılmalı:

```bash
cd mobile
flutter test test/home_page_logic_test.dart test/profile_page_detail_blocks_test.dart
flutter analyze lib/app/tabs/home_page.dart lib/app/tabs/profile_page.dart lib/app/performance/load_tuning.dart
```
