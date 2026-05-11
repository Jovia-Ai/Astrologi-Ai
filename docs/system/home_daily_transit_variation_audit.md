# Home Daily Transit Variation Audit

**Tarih:** 2026-05-01  
**Kapsam:** Home V2 `daily_synthesis` neden günler arasında aynı görünüyor, tek bir fix yeterli mi, daha sağlıklı günlük transit öngörüleri için başka hangi katmanlar gerekiyor?

---

## 1. Kısa cevap

**Hayır, tek başına tek bir fix yeterli değil.**

Şu anki en kritik bug:

- Home fast path günlük aday havuzunu daraltırken `selected_day_context.top_event_ids` ile raw transit `event_id`’leri **aynı id uzayında değilmiş gibi** kullanıyor.
- Sonuçta günlük context her gün değişse bile scorer’a pratikte tek aynı long-period event giriyor.

Bu fix yapılmadan günlük varyasyon beklenmemeli.

Ama bu fix **tek başına da yeterli değil**, çünkü:

1. Home `daily_synthesis` tek `primary_signal` üzerinden yazıyor.
2. Home payload shaping günlük kartları `1` adede kesiyor.
3. Headline üretimi support/mix farkını yeterince yansıtmıyor.
4. Home fast path aday seed’i period odaklı başladığı için “gerçek günlük tetik” yüzeye yeterince erken çıkmıyor.

---

## 2. Gözlenen mevcut davranış

Aynı chart için art arda 4 gün test edildi:

- `2026-04-29`
- `2026-04-30`
- `2026-05-01`
- `2026-05-02`

Takvim context’i her gün değişiyor:

- `2026-04-29`: `tr.moon.sextile.venus`, `tr.moon.sextile.moon`, `tr.fortune.conjunction.sun`
- `2026-04-30`: `tr.moon.square.jupiter`, `tr.moon.opposition.ic`, `tr.moon.square.neptune`
- `2026-05-01`: `tr.moon.square.uranus`, `tr.moon.sextile.sun`, `tr.fortune.conjunction.uranus`
- `2026-05-02`: `tr.moon.square.lilith`, `tr.fortune.opposition.moon`, `tr.moon.sextile.mercury`

Ama Home public payload’da seçilen günlük event hep aynı kaldı:

- `daily_event_ids = ["88bc98188b2f7931360493237881969004d50662"]`

Ve headline da aynı kaldı:

- `Bugün ilk tepkinin tonunu ayarlamak kolay olmayabilir.`

Kaynaklar:

- [backend/app/api/routes/transits.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/transits.py:550)
- [backend/app/api/routes/transits.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/transits.py:2283)
- [backend/app/transit/narrative/daily_selection.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/daily_selection.py:1190)
- [backend/app/transit/narrative/daily_synthesis.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/daily_synthesis.py:1148)

---

## 3. Asıl root cause

### 3.1 Calendar `top_event_ids` ile raw transit `event_id`’leri eşleşmiyor

Takvimden gelen `top_event_ids` şu formatta:

- `tr.moon.square.uranus`
- `tr.moon.sextile.venus`
- `tr.fortune.conjunction.sun`

Raw transit item `event_id`’leri ise şu formatta:

- `88bc98188b2f7931360493237881969004d50662`

Yani Home fast path şu anda iki farklı id uzayını aynıymış gibi filtreliyor.

İlgili kod:

- takvim context çıkarımı:
  - [transits.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/transits.py:563)
- Home candidate daraltma:
  - [transits.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/transits.py:2283)

### Sonuç

Home candidate listesi pratikte sadece `event_cards` seed’inden kalan event’lerle sınırlanıyor.

Bu seed ise Home fast path’te önce `select_event_ids(...)` ile period/structural eksende seçiliyor:

- [transits.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/transits.py:2216)

Dolayısıyla “günün tepe tetikleri” Home daily selection’a fiilen taşınamıyor.

---

## 4. Tek fix neden yetmez

### 4.1 Home payload shaping günlük kartları 1 adede kesiyor

Home shaping:

- `daily_event_cards = daily_cards[:1]`

Kaynak:

- [transits.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/transits.py:286)

Bu şu anlama geliyor:

- scorer doğru çalışsa bile Home sonunda yalnızca tek daily card görüyor
- `daily_synthesis` de bu tek karttan yazıyor

Bu, “varyasyon”u sadece event seçimine indirger. İkinci bir günlük karşı-akış veya soft modifier Home’da prose düzeyinde daralır.

### 4.2 `daily_synthesis` headline tek `primary_signal` üzerinden kuruluyor

`build_daily_synthesis(...)` şu akışla çalışıyor:

- `primary_signal = cards[0]`
- support signal ayrıca çözülebiliyor
- ama headline yine `_build_headline(primary_signal, seed)` ile kuruluyor

Kaynak:

- [daily_synthesis.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/daily_synthesis.py:1148)

Bu yüzden:

- support değişse bile
- `narrative_mode` değişse bile
- aynı primary signal seçildiyse headline sabit kalabiliyor

Nitekim testte bu oldu:

- `2026-05-01` için `mode = support_dominant`
- ama headline yine aynı kaldı

### 4.3 Home candidate seed period-first başlıyor

Home fast path seed’i önce:

- `select_event_ids(...)`

ile seçiliyor; bu selection daha çok yapısal/periodik ağırlık taşıyor.

Kaynak:

- [transits.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/transits.py:2216)

Bu tek başına bug değil, ama Home günlük ürün mantığı için şu riski yaratıyor:

- “bugünü en çok hissettiren event” ile
- “uzun dönemde en anlamlı event”

aynı şey olmayabilir.

Eğer top-day signal mapping düzgün bağlanmazsa Home her zaman period omurgasına geri düşer.

### 4.4 Günlük variation için prose katmanı da yeterince date-sensitive değil

Şu an günlük metnin bazı parçaları farklılaşabiliyor:

- `what_now`
- `support_line`
- `narrative_mode`

Ama headline kalıbı daha dar:

- domain
- aspect_mode
- primary signal

Support veya selected-day shift’i headline’da yeterince görünür olmayabilir.

Kaynak:

- [daily_synthesis.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/daily_synthesis.py:1183)

---

## 5. Mevcut sistemde iyi olan şeyler

Bunlar hazır ve doğru temel:

1. `selected_date` gerçekten backend’e gidiyor.
   - [mobile/lib/app/timing/transit_repositories.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/timing/transit_repositories.dart:209)

2. `selected_day_context` gerçekten takvimden gün gün üretiliyor.
   - [transits.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/transits.py:602)

3. Daily selection scorer `selected_day_context` kullanıyor.
   - [daily_selection.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/daily_selection.py:1204)

4. `daily_synthesis` artık multi-signal planner taşıyor.
   - `period_spine`
   - `support_signal`
   - `narrative_mode`
   - `planner_debug`
   - [daily_synthesis.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/daily_synthesis.py:1210)

Yani sistemin problemi “günlük katman yok” değil.  
Problem, **günlük sinyalin Home aday havuzuna doğru bağlanamaması** ve sonrasında **tek-sinyal headline kısıtı**.

---

## 6. Değerlendirme: hangi fix ne kadar etkili olur

### A. `top_event_ids` -> raw event mapping fix
**Durum:** Zorunlu  
**Etkisi:** Çok yüksek  
**Yeter mi?:** Hayır

Bu fix olmadan Home günlük varyasyon beklenmemeli.

Ama bu fix tek başına sadece şunu çözer:

- günlük tepe sinyaller gerçekten candidate pool’a girebilir

Şunu çözmez:

- support/headline varyasyonu
- Home’un 1-card kısıtı
- prose tonundaki tekrar hissi

### B. Home candidate seed’i day-first hale getirmek
**Durum:** Kuvvetle önerilir  
**Etkisi:** Çok yüksek  
**Yeter mi?:** Tek başına hayır, ama A ile birlikte büyük fark yaratır

Bugünkü aday havuzu:

- Home `event_cards` seed’i
- plus `top_event_ids`

Daha doğru Home mantığı:

- selected day top events öncelikli
- sonra period spine / support

### C. Headline’ı `narrative_mode` ve support’a duyarlı hale getirmek
**Durum:** Gerekli kalite adımı  
**Etkisi:** Orta-yüksek  
**Yeter mi?:** Hayır

Bu, aynı primary signal etrafında bile “gün açılıyor mu, sıkışıyor mu, karışık mı” farkını daha görünür kılar.

### D. Home `daily_event_cards[:1]` kısıtını gözden geçirmek
**Durum:** Ürün kararı  
**Etkisi:** Orta  
**Yeter mi?:** Hayır

Eğer Home’da tek card kalacaksa prose’ın mixed/support farkını çok iyi taşıması gerekir.  
Yok eğer 1 card korunacaksa, ikinci sinyal en azından text içinde görünür hale gelmeli.

### E. Günlük metinde “selected-day wording” katmanı
**Durum:** Kalite iyileştirmesi  
**Etkisi:** Orta  
**Yeter mi?:** Hayır

Şu an prose astro-grounded, ama date-facing variety için:

- `today trigger`
- `today support`
- `today tone shift`

daha görünür olmalı.

---

## 7. En sağlıklı çözüm sırası

### P0 — Gerekli teknik düzeltme

1. Calendar `top_event_ids` ile raw transit item’lar arasında güvenilir mapping kur.
2. Home candidate set’ini bu mapped günlük event’leri gerçekten içerecek şekilde güncelle.

Bu olmadan günler arası varyasyon yapay kalır.

### P1 — Günlük selection mantığını Home için düzelt

3. Home daily selection candidate set’inde **day-top triggers first** mantığı kur.
4. Period spine yalnızca day-top candidate zayıfsa baskın hale gelsin.

### P2 — Synthesis görünürlüğünü düzelt

5. Headline’ı `primary_signal` + `narrative_mode` + support presence ile varyasyonlu kur.
6. `support_dominant` ve `mixed` günlerde headline/body ayrımı daha net olsun.

### P3 — Yüzey kalitesi

7. Home shaping’in `daily_event_cards[:1]` yaklaşımı yeterli mi karar ver.
8. Tek kart kalacaksa text içinde ikinci sinyal görünürlüğü zorunlu hale gelsin.

---

## 8. Sonuç

**Sadece tek bir mapping fix’i yeterli değil.**  
Ama o fix **zorunlu ilk adım**.

En doğru değerlendirme:

- `top_event_ids` / raw `event_id` mismatch = **root cause**
- Home day-first candidate selection = **esas ürün düzeltmesi**
- headline/synthesis variation = **kalite katmanı**
- 1-card Home shaping = **sunum kısıtı**

Bugünkü sistemde günlük transitler “hep aynı” görünüyorsa, bu:

1. selected day gitmediği için değil,
2. astro hesap aynı olduğu için değil,
3. Home günlük trigger’ı period spine’dan ayıramadığı için.

Dolayısıyla öneri:

- önce candidate mapping + day-first selection
- sonra headline/support variation
- en son Home surface tuning

Bu sıra en düşük riskli ve en yüksek etkili sıradır.
