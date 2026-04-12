# Daily Transit Disappearing Bug Report

## A. Bug özeti
Home ekranındaki "Günlük transit" kartı aynı gün içinde bazen dolu geliyor, sonra daha zayıf bir kopyaya ya da `"Bugün için kısa yorum henüz hazır değil."` fallback'ine düşüyordu. Sorun UI placeholder değil, state precedence ve source drift kaynaklıydı.

## B. Root cause
Ana kök neden iki katmandı:

1. Home, günlük kartı iki ayrı kaynaktan kuruyordu.
   - İlk olarak `/home/fast` preview kartı state'e yazılıyor.
   - Ardından `/transit/narrative` `payload_profile=home` + `response_mode=public_only` çağrısı gelince bu state tekrar merge ediliyordu.

2. Bu ikinci merge, "daha iyi mi?" diye bakmadan gelen non-empty daily kartı mevcut kartın üstüne yazabiliyordu.
   - Kaynak: `buildHomeTransitSnapshot(...)` ve `mergeHomeTransitSnapshot(...)`.

3. Home ile detail ekranı aynı günlük seçim mantığını kullanmıyordu.
   - Home daha basit bir seçim/fallback zinciriyle çalışıyordu.
   - Detail ekranı ise daha zengin scoring + dedupe + period fallback mantığı kullanıyordu.

4. Home narrative çağrısı `public_only` olduğu için root `calendar.days` gelmiyordu.
   - Backend `public_only` modunda yalnız `range` + `public` dönüyor.
   - `NarrativeResponse.fromMap(...)` ise `calendarDays`'i root `calendar` alanından okuyor.
   - Sonuç: Home narrative response'u geldikten sonra day meta çoğu zaman boş kalıyordu; bu da zayıf bir overwrite sonrası empty/fallback görünürlüğünü artırıyordu.

5. `public_only/home` yolu bazı günlerde günlük kartı hiç çözemiyordu ama detail ekranı `calendar_day/full` kaynağından yorum üretebiliyordu.
   - Yani kalan bug'in ikinci parçası gerçek bir source-of-truth drift'ti.
   - Home boş kalırken detail aynı gün dolu olabiliyordu.

## C. Bu neden intermittently oluyordu
- `/home/fast` ve `/transit/narrative` farklı zamanlarda dönüyordu.
- Hızlı preview önce dolu bir kart gösterebiliyordu.
- Birkaç saniye sonra gelen home narrative response'u daha zayıf/period-derived bir kart üretirse bunu ezebiliyordu.
- `NarrativeRepository` client cache'i bu daha zayıf sonucu aynı session içinde tekrar dolaşıma sokabildiği için bug "bazen geliyor, bazen gidiyor" gibi görünüyordu.
- Detail ekranı farklı selection logic kullandığı için aynı tarih detail'de dolu, Home'da zayıf/boş görünebiliyordu.

## D. Hangi dosyalara dokundun
- `mobile/lib/app/tabs/home_page.dart`
- `mobile/lib/app/tabs/calendar_hub_page.dart`
- `mobile/lib/app/timing/daily_transit_selection.dart`
- `mobile/test/home_page_logic_test.dart`

## E. Uygulanan fix
1. Home ile detail'in günlük kart seçimini aynı scoring/dedupe mantığına hizalamak için ortak helper eklendi.
   - `selectDailyTransitCardsForDate(...)`

2. Home merge precedence güçlendirildi.
   - Güçlü valid daily kart, daha zayıf period-derived/fallback kartla overwrite edilmiyor.
   - Daha zengin gerçek daily kart gelirse preview yükseltilebiliyor.

3. Today metadata fallback'i sertleştirildi.
   - Bugün seçiliyken week item meta yoksa `_todayDayMeta` kullanılabiliyor.

4. Home `public_only/home` sonucu günlük copy çözemiyorsa, yalnız o durumda detail'in kullandığı `calendar_day/full` kaynağından tek-gün hydrate fallback'i eklendi.
   - Ana performans yolu korunuyor.
   - Ek çağrı sadece boş kalan günlerde yapılıyor.

5. Bug'e özel küçük telemetry eklendi.
   - `home_daily_transit_merge`
   - `home_daily_transit_detail_fallback_start/end`
   - source / strength / overwrite_prevented / resolution_reason loglanıyor.

## F. Önceki davranış neden yanlıştı
- Source-of-truth tek değildi.
- Merge kuralı "non-empty incoming kazanır" seviyesinde çok zayıftı.
- Home response'u `public_only` olduğu halde Home, detail kadar güvenilir daily seçim yapmıyordu.
- Mevcut valid daily summary, daha geç gelen ama daha düşük kaliteli response ile ezilebiliyordu.

## G. Hangi senaryolarda artık düzelmiş olmalı
- Fast preview dolu geldikten sonra geç gelen daha zayıf response o kartı silememeli.
- Tab değiştirip geri gelince aynı session içinde valid günlük kart korunmalı.
- App resume sonrası weaker cached response gelirse mevcut iyi kart ezilmemeli.
- Home ve detail aynı tarih için daha uyumlu günlük kart seçmeli.
- `public_only/home` boş dönerse Home, detail source'tan tek günlük hydrate alıp boş state'ten çıkmalı.
- Gerçek daily kart yoksa ancak o zaman period fallback veya empty state görünmeli.

## H. Eklenen testler
- `mergeHomeTransitSnapshot keeps stronger existing daily card over period-derived fallback`
- `mergeHomeTransitSnapshot upgrades fast preview when richer true daily card arrives`
- `buildHomeTransitSnapshot scores legacy event cards so stronger daily stays on home`

Ek doğrulama:
- `flutter test test/home_page_logic_test.dart`
- `flutter test test/calendar_hub_page_test.dart`
- `flutter analyze lib/app/timing/daily_transit_selection.dart lib/app/tabs/home_page.dart lib/app/tabs/calendar_hub_page.dart test/home_page_logic_test.dart`

## I. Hala risk kalan alanlar
- `public_only` response bugün için root `calendar.days` taşımadığı için Home hala tam day-meta zenginliğini ayrı hydrate/fallback çağrısından alıyor.
- Midnight/day-boundary senaryolarında device local time ile profile timezone farkı ayrı bir sertleştirme konusu olabilir.
- Eğer backend gerçekten o gün için daily ve period ikisini de boş dönerse empty state halen doğru olarak görünecek.

## J. Sonraki önerilen cleanup / hardening adımları
1. Home için selected day key ve profile timezone bazlı küçük bir state object çıkarıp request/merge/render kararını tek yerde toplamak.
2. `public_only` için selected-day micro summary'nin response contract'ı içinde net bir alan olarak taşınmasını değerlendirmek.
3. Home ve detail selection helper'ı için ayrı saf unit test dosyası eklemek.
4. `home_daily_transit_merge` event'lerini dashboard'a bağlayıp `overwrite_prevented` ve `resolution_reason=empty` oranlarını izlemek.
5. Gece yarısı/timezone boundary için hedefli regression testi eklemek.
