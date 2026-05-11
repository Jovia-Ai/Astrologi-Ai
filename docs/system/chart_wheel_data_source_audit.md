# Chart Wheel Data Source Audit

**Tarih:** 2026-04-28  
**Kapsam:** Profile Natal Chart Wheel veri kaynağı entegrasyonu  
**Kısıt:** Kod değiştirilmedi

## Sonuç

Genel durum:

1. `/api/calculate-natal-chart` backend’de mevcut.
2. Mobile repository mevcut default base URL ile doğru path’i çağırıyor.
3. Request payload **kısmen doğru**; önemli bir contract riski var:
   mobile hem `birth_place` hem `city` gönderiyor, backend ise `city` alanını
   `birth_place`’den önce okuyor.
4. Response, chart wheel için gereken alanları içeriyor, ama bunlar top-level
   `asc` / `mc` değil; nested alanlar.
5. Endpoint auth gerektirmiyor. Ayrıca doğum verisi bu route içinde persist
   edilmese de third-party servis yüzeyi var.
6. UI fallback davranışı crash-prevention açısından doğru, ama kullanıcıya
   gösterilen durum backend hata ile “veri yok” halini ayırmıyor.

---

## 1. `/api/calculate-natal-chart` backend’de var mı?

**Evet.**

Kanıt:

- [backend/app/routers/charts.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/routers/charts.py:31) router prefix’ini `/api` olarak tanımlıyor.
- Aynı dosyada [calculate_natal_chart route’u](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/routers/charts.py:98) `@router.post("/calculate-natal-chart")` ile tanımlı.
- Router, [backend/app/main.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/main.py:45) içinde uygulamaya include ediliyor.

Net path:

- `POST /api/calculate-natal-chart`

Ek not:

- Alias olarak `POST /api/natal-chart` da mevcut: [backend/app/routers/charts.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/routers/charts.py:99)

Durum: **PASS**

---

## 2. Mobile repository doğru API base path’i mi kullanıyor?

**Mevcut default konfigürasyonda evet.**

Kanıt:

- Mobile repository çağrısı: [mobile/lib/app/chart/chart_wheel_repository.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/chart/chart_wheel_repository.dart:17)
- Çağrılan path: `'/api/calculate-natal-chart'`
- Default base URL: [mobile/lib/app/api/api_environment.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/api/api_environment.dart:4) `http://127.0.0.1:5000`
- `ApiClient` bu base URL’yi doğrudan `Dio` base URL olarak kullanıyor: [mobile/lib/app/api/api_client.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/api/api_client.dart:36)

Bu durumda efektif URL:

- `http://127.0.0.1:5000/api/calculate-natal-chart`

Risk:

- Eğer `API_BASE_URL` build-time override’ı `/api` ile biterse, path
  `.../api/api/calculate-natal-chart` olur.
- `ApiEnvironment` trailing slash temizliyor ama path prefix normalize etmiyor:
  [mobile/lib/app/api/api_environment.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/api/api_environment.dart:28)

Karar:

- Default/dev setup için doğru.
- Config hygiene açısından kırılgan.

Durum: **PASS with caveat**

---

## 3. Request payload backend contract ile uyumlu mu?

**Kısmen.**

### Doğru taraflar

Mobile payload:

- `birth_date`
- `birth_time`
- `birth_place`
- `timezone`
- `latitude`
- `longitude`

Kaynak:

- [mobile/lib/app/chart/chart_wheel_repository.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/chart/chart_wheel_repository.dart:41)

Backend parser bunları kabul ediyor:

- `birth_date` / `birthDate` / `date`: [backend/app/astro/chart_engine/builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro/chart_engine/builder.py:204)
- `birth_time` / `birthTime` / `time`: [backend/app/astro/chart_engine/builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro/chart_engine/builder.py:213)
- `birth_timezone` veya `timezone`: [backend/app/astro/chart_engine/builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro/chart_engine/builder.py:248)
- `birth_latitude` veya `latitude`: [backend/app/astro/chart_engine/builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro/chart_engine/builder.py:237)
- `birth_longitude` veya `longitude`: [backend/app/astro/chart_engine/builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro/chart_engine/builder.py:242)

### Uyuşmazlık / risk

Backend `extract_birth_inputs` lokasyon seçerken şu sırayı kullanıyor:

1. `city`
2. `birth_place`
3. diğer alias’lar

Kanıt:

- [backend/app/astro/chart_engine/builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro/chart_engine/builder.py:185)

Mobile ise aynı payload’da hem `birth_place` hem `city` gönderiyor:

- [mobile/lib/app/chart/chart_wheel_repository.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/chart/chart_wheel_repository.dart:44)
- [mobile/lib/app/chart/chart_wheel_repository.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/chart/chart_wheel_repository.dart:45)

Pratik etki:

- `birth_place = "Istanbul, TR"` gönderilmiş olsa bile backend bunu çoğu durumda
  kullanmayıp `city = "Istanbul"` ile devam eder.
- Yani mobile daha spesifik bir yer etiketi hazırlıyor, fakat backend onu
  override ediyor.
- `country` alanı mobile tarafından gönderiliyor, fakat bu route’un parser’ı
  tarafından doğrudan kullanılmıyor.

Bu, özellikle explicit `latitude` / `longitude` / `timezone` yoksa geocoding
özgüllüğünü düşürür.

Karar:

- Sözleşme teknik olarak “çalışıyor”.
- Ama semantics tarafında **uyumsuz**.

Durum: **PARTIAL / contract risk**

---

## 4. Response şu alanları içeriyor mu?

İstenenler:

- asc
- mc
- house cusps
- planet longitudes
- retrograde flags

### Evet, ama nested olarak

#### ASC / MC

Backend `angles` içinde döndürüyor:

- `angles.ascendant`
- `angles.midheaven`

Kanıt:

- [backend/app/astro/chart_engine/houses.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro/chart_engine/houses.py:39)

Not:

- Top-level `asc` / `mc` kısa alias’ı yok.

#### House cusps

Backend `house_positions["1".."12"]` içinde döndürüyor:

- `longitude`
- `sign`
- `degree`
- `minute`

Kanıt:

- [backend/app/astro/chart_engine/builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro/chart_engine/builder.py:286)

Chart wheel için gereken cusp longitude burada mevcut.

#### Planet longitudes

Backend `planets` map’inde döndürüyor:

- `planets["Sun"].longitude`
- `planets["Moon"].longitude`
- vb.

Kanıt:

- [backend/app/astro/chart_engine/positions.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro/chart_engine/positions.py:161)

#### Retrograde flags

Her planet payload’ında:

- `retrograde: bool(speed < 0)`

Kanıt:

- [backend/app/astro/chart_engine/positions.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro/chart_engine/positions.py:168)

### Mobile parser uyumu

Mobile parser bu nested shape’i okuyabiliyor:

- `angles['ascendant']`
- `angles['midheaven']`
- `house_positions['1'..'12']['longitude']`
- `planets` map veya list

Kaynak:

- [mobile/lib/app/chart/chart_wheel_data.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/chart/chart_wheel_data.dart:54)

Karar:

- Response chart wheel için yeterli.
- Beklenen alan adları nested; top-level `asc` / `mc` bekleniyorsa yanlış olur.

Durum: **PASS**

---

## 5. Endpoint auth gerektiriyor mu, birth data’yı güvenli biçimde mi açıyor?

### Auth

**Hayır, bu endpoint auth gerektirmiyor.**

Kanıt:

- `calculate_natal_chart` route’u hiçbir auth dependency çağırmıyor:
  [backend/app/routers/charts.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/routers/charts.py:98)
- Aynı dosyada auth yalnızca `build_chart_route` için opsiyonel/flag-gated:
  [backend/app/routers/charts.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/routers/charts.py:146)

Mobile `Authorization` header ekleyebilir:

- [mobile/lib/app/api/api_client.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/api/api_client.dart:46)

Ama bu route onu kullanmıyor.

### Safety / privacy exposure

**Tam anlamıyla “safe/private by design” değil.**

Sebep:

1. Route doğum verisini persist etmiyor.
   Bu iyi taraf.

2. Ama `_calculate_chart` içinde chart summary oluşturulup AI yorumuna gönderiliyor:
   [backend/app/routers/charts.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/routers/charts.py:88)

3. `chart_to_summary` içinde şu bilgiler string’e çevriliyor:
   - location city
   - timezone
   - exact `birth_datetime`
   - planet positions

   Kanıt:
   [backend/app/ai/narrative/groq_client.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/ai/narrative/groq_client.py:137)

4. `generate_ai_interpretation`, bu summary’yi Groq endpoint’ine POST ediyor
   (`GROQ_API_KEY` varsa):
   [backend/app/ai/narrative/groq_client.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/ai/narrative/groq_client.py:95)

5. Explicit lat/lon/timezone yoksa backend geocoding yapabilir; bu da birth place’i
   external geocoder’a taşır:
   [backend/app/astro/chart_engine/builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro/chart_engine/builder.py:233)

6. Backend lokal/UTC datetime ve JD UT değerlerini log’luyor:
   [backend/app/astro/chart_engine/builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro/chart_engine/builder.py:257)

Karar:

- Auth: **No**
- Persist: **No**
- Third-party processing exposure: **Yes**
- Sensitive birth data açısından güvenlik seviyesi: **medium risk**

Durum: **FAIL for strict privacy, PASS for basic functionality**

---

## 6. Endpoint fail olduğunda fallback davranışı doğru mu?

### Mevcut davranış

Profile section önce embedded payload’dan parse etmeyi deniyor:

- [mobile/lib/app/profile/profile_natal_chart_section.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/profile/profile_natal_chart_section.dart:187)

Bu parse başarılıysa network’e gitmiyor.

Başarısızsa ve birth data varsa repository fetch başlatıyor:

- [mobile/lib/app/profile/profile_natal_chart_section.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/profile/profile_natal_chart_section.dart:193)

UI `FutureBuilder` ile çalışıyor:

- loading sırasında spinner + placeholder
- data varsa wheel
- data yoksa fallback placeholder

Kaynak:

- [mobile/lib/app/profile/profile_natal_chart_section.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/profile/profile_natal_chart_section.dart:61)

### Doğru olan taraf

- Endpoint fail ettiğinde widget crash olmuyor.
- Empty/missing data ile aynı şekilde güvenli placeholder gösteriliyor.
- Doğum bilgisi yoksa gereksiz request de atmıyor.

### Zayıf taraf

- `snapshot.hasError` için ayrı bir UI yok.
- Network failure, 400/502, parse failure ve gerçekten veri yok durumu aynı
  fallback görünümüne düşüyor.
- Kullanıcıya “backend hata verdi” ile “henüz veri yok” ayrımı yapılmıyor.
- Retry CTA yok.

Bu nedenle davranış:

- **stability açısından doğru**
- **diagnostics / UX açısından zayıf**

Durum: **PASS for graceful degradation, PARTIAL for user feedback**

---

## Kısa Cevaplar

### 1. Does `/api/calculate-natal-chart` exist in the backend?
Evet.

### 2. Is the mobile repository using the correct API base path?
Evet, default base URL ile doğru. Ama `API_BASE_URL` içine `/api` konursa çift prefix riski var.

### 3. Does the request payload match backend contract?
Kısmen. Gerekli alanlar var, coordinate/timezone alias’ları da uyuyor. Ama `city`
alanı backend’de `birth_place`’i override ediyor.

### 4. Does the response contain asc, mc, house cusps, planet longitudes, retrograde flags?
Evet. Bunlar nested alanlarda mevcut:

- `angles.ascendant`
- `angles.midheaven`
- `house_positions[*].longitude`
- `planets[*].longitude`
- `planets[*].retrograde`

### 5. Does this endpoint require auth or expose user birth data safely?
Auth gerektirmiyor. Persist etmiyor, ama strict privacy açısından güvenli sayılmaz;
geocoding ve AI interpretation üzerinden third-party exposure var.

### 6. Is the fallback behavior correct when endpoint fails?
Evet, crash etmiyor ve placeholder’a düşüyor. Ama hata ile “veri yok” durumu
ayırt edilmiyor.

---

## Önerilen Sonraki Aksiyonlar

Kod değiştirmeden audit sonucu olarak en kritik 3 nokta:

1. **Payload precedence riski**
   `city` vs `birth_place` önceliği netleştirilmeli. Şu an mobile daha spesifik
   place label üretse de backend bunu by-pass edebiliyor.

2. **Privacy değerlendirmesi**
   Bu endpoint chart wheel için geometri çekse de yanında AI interpretation da
   üretiyor. Bu, data minimization açısından ağır bir surface.

3. **Fallback UX ayrımı**
   “Endpoint başarısız oldu” ile “harita verisi yok” aynı state’e düşüyor.
   Teknik olarak güvenli, ürün olarak belirsiz.

---

## Audit Kararı

**Release-blocking değil, ama 2 önemli risk var:**

- **R1:** request payload semantics mismatch (`city` precedence)
- **R2:** strict privacy açısından endpoint over-broad ve third-party exposed

Chart wheel’in yalnızca render açısından çalışması beklenir. Ama veri sözleşmesi
ve privacy posture açısından “tam temiz” değil.
