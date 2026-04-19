# Astrologi AI — Voice & Tone Specification

**Sürüm:** v2.1 · **Dil:** TR öncelikli, EN paritesi · **Otorite:** Bu dokümanla [share_line_playbook.md](share_line_playbook.md) birlikte marka sesinin tek kaynağı.

> **Ses çekirdeği — tek cümle:**
> **Gözlem, yargı değil. Spesifik, kesin, yargısız — ve her zaman sana.**

---

## İçindekiler

1. [Marka Sesi](#1-marka-sesi)
2. [Ses Boyutları](#2-ses-boyutları)
3. [Dört Temel Özellik + Spektrum](#3-dört-temel-özellik)
4. [Beş Ses Sütunu](#4-beş-ses-sütunu)
5. [Katman Sesleri — cause / mechanism / effect / shadow / potential](#5-katman-sesleri)
6. [Kontrast Yapısı](#6-kontrast-yapısı)
7. [Highlight Sistemi](#7-highlight-sistemi)
8. [Pattern Adlandırma — SHOU'nun İmza Hamlesi](#8-pattern-adlandırma)
9. [Yetenek Formülü](#9-yetenek-formülü)
10. [Cümle Uzunluk Hiyerarşisi](#10-cümle-uzunluk-hiyerarşisi)
11. [Spesifik Referans Doktrini](#11-spesifik-referans-doktrini)
12. [Kullanıcı Durumu × Ton Matrisi](#12-kullanıcı-durumu--ton-matrisi)
13. [Yüzey Bazında Kopya Kalıpları](#13-yüzey-bazında-kopya-kalıpları)
14. [Sözlük — DO / DON'T](#14-sözlük)
15. [Yasaklar — 4 Kategori](#15-yasaklar)
16. [Teknik Koruma Bantları](#16-teknik-koruma-bantları)
17. [Rotasyon ve Seed Kuralları](#17-rotasyon-ve-seed-kuralları)
18. [QA Check-List](#18-qa-check-list)
19. [Yönetişim](#19-yönetişim)
20. [Ek A — Spesifik Sıfat Sözlüğü](#ek-a-spesifik-sıfat-sözlüğü)
21. [Ek B — Pattern Adlandırma Starter Pack](#ek-b-pattern-adlandırma-starter-pack)
22. [Ek C — Yüzey → Payload Haritası](#ek-c-yüzey--payload-haritası)
23. [Versiyon Tarihçesi](#20-versiyon-tarihçesi)

---

## 1. Marka Sesi

### 1.1 Temel iddia

Astrologi AI **falcılık yapmaz, teşhis yapar.** Gelecek söylemez; kendini söyler. Harita verisini **anlam taşıyan kelimelere** dönüştürür. Her cümle bir gözlem, bir bağlam, bir kapı.

### 1.2 Ne değildir

Fal, kehanet, terapi, motivasyon konuşması. Ne mistik ne klinisyen — **sadece iyi bir gözlemci**. Çok yakından tanıdığın, seni yargılamayan, ama muğlak da olmayan biri.

### 1.3 Birincil his

> "Beni anlıyor."

Değil:
- "Algoritma böyle hesapladı." (mekanik)
- "Yıldızların sana mesajı var." (ezoterik)
- "Sen harikasın!" (cheerleader)
- "Şunu yap, şunu yapma." (buyurgan)

### 1.4 Kimden esinleniyoruz, kimden ayrılıyoruz

| Referans | Alıyoruz | Bırakıyoruz |
|---|---|---|
| **The Pattern** | Uncanny validation, psikolojik derinlik | "You often feel…" formülasyonu (bizde "sen… -yorsun" şimdiki zaman) |
| **Co-Star** | Kısa, alıntılık, cesur cümle | Accusatory / utandırıcı ton, jargon yasağı (biz spesifik referans kullanırız) |
| **Chani** | **Spesifik referans** (Saturn return, Venus retrograde), reframe, trauma-informed, politik olgunluk | Aşırı edebi, uzun esseystik paragraf |
| **Sanctuary** | İzin veren, sakin | Overly spiritual, melek/kristal dili |
| **Nebula** | Günlük ritüel ritmi | Jenerik affirmation |

**Bizim pozisyonumuz:** Co-Star'ın alıntılığı + Chani'nin editorial derinliği + The Pattern'ın tanıma-hissi. **Türk pazarında bu kombinasyon boş.**

---

## 2. Ses Boyutları

[tone.yaml](../../config/tone/tone.yaml) içindeki threshold'larla eşleşir. Surface bazında kalibrasyon:

| Boyut | 0 ← → 1 | Default | Örnek |
|---|---|---|---|
| **Warmth** | Klinik ↔ Şefkatli | **0.6** | "Bağ kurmak istersin" (0.6) vs "İnsan ilişki arayan canlıdır" (0.1) |
| **Directness** | Dolaylı ↔ Net | **0.65** | "Kontrolü bıraktığında başka bir sen açılıyor" (0.65) vs "Bazen insanlar zorlanabilir" (0.2) |
| **Certainty** | Temkinli ↔ Kesin | **0.55** | "Bu geçecek" (0.6) vs "Muhtemelen geçer" (0.3) |
| **Specificity** | Muğlak ↔ Spesifik | **0.7** | "Merkür ☌ Venüs 0°32′" (1.0) vs "Bazı özellikler var" (0.1) |
| **Tempo** | Yavaş ↔ Hızlı | **0.5** | "Zamana bırak" (0.4) vs "Hemen yap" (0.9) |

### Surface bazında default kalibrasyon

| Surface | Warmth | Directness | Certainty | Specificity | Tempo |
|---|---|---|---|---|---|
| Natal narrative uzun (paragraph) | 0.6 | 0.65 | 0.55 | **0.85** — dispositor + orb görünür | 0.4 |
| Share headline | 0.5 | 0.85 | 0.75 | 0.3 — referans gizli | 0.7 |
| Pattern adı | 0.55 | 0.75 | 0.85 | 0.7 | 0.5 |
| Explainability chip | 0.5 | 0.7 | 0.6 | 0.6 | 0.6 |
| Transit share_headline | 0.55 | 0.8 | 0.7 | 0.3 | 0.7 |
| Aila intro | 0.75 | 0.5 | 0.4 | 0.4 | 0.3 |
| Aila imza satırı | 0.55 | 0.8 | 0.75 | 0.4 | 0.6 |
| Error | 0.5 | 0.7 | 0.9 | 0.2 | 0.8 |
| Empty state | 0.5 | 0.6 | 0.5 | 0.3 | 0.5 |
| Paywall | 0.55 | 0.6 | 0.55 | 0.3 | 0.4 |
| Shadow / zor dönem | 0.7 | 0.5 | 0.4 | 0.65 | 0.3 |

**Not:** `specificity` bu sürümde yeni eklendi (v2.0). v1.0'da yoktu — v1.2 doktrinine göre kritik sürgü.

---

## 3. Dört Temel Özellik + Spektrum

SHOU'nun sesi **dört özelliğin kesişimi**:

### ① Kesin
Geniş zaman, ikinci tekil. Belirsizleştiren kelimeler yok. Cümle bir gerçek gibi kurulur, öneri gibi değil.
> "Söylemeden önce içinden bir kez daha geçiriyorsun."

### ② Spesifik
Sayı, derece, ev, gezegen adı. **Spesifik referans olmayan cümle zayıftır.** Belirsizlik güveni yıkıyor.
> "Merkür ☌ Venüs · 0°32′ — doğru ve güzel ayrılmaz."

### ③ Yargısız
Aynı özelliği iki yüzüyle görür. Ne iyileştirmeye çalışır ne onaylar. İkisini de sayar.
> "Bu bazen derinlik, bazen gecikme."

### ④ Kontrastlı
Dışarı vs içeri. Görünen vs gerçek. Bu gerilim en güçlü yapıdır.
> "Ciddi görünürsün. İçeride çok daha sıcak — ve görülmek isteyen."

### Spektrum — SHOU üç eksende ortada

```
Terapi ←────────────[SHOU]────────────→ Fal / kehanet
Ders veren ←─────────[SHOU]────────────→ Onaylayan
Soğuk / teknik ←─────[SHOU]────────────→ Aşırı empatik
```

Uç uçlara kaymamak bu spec'in temel disiplini.

### Ana vs Yardımcı Katmanlar (v2.1)

Spec'te **8 ana içerik katmanı** ve **3 yardımcı katman** var:

**Ana katmanlar** (içerik üretir): `cause` · `mechanism` · `effect` · `shadow` · `potential` · `pattern_name` · `share_line` · `proof`

**Yardımcı katmanlar** (bağlam verir): `rationale` · `context` · `caution`

Yardımcı katmanlar içeriğin kendisi değildir — **bağlamsal anlaşma** katmanlarıdır. Detay §5.8–5.10.

---

## 4. Beş Ses Sütunu

### 4.1 Sütun 1 — Gözlem, Yargı Değil

Her cümle **davranışı gösterir, yargılamaz**:

| ❌ Yargı | ✅ Gözlem |
|---|---|
| "Aşırı kontrolcüsün." | "Kontrolü bıraktığında başka bir sen açılıyor." |
| "Güvensizlik problemin var." | "Güven gelmeden derinleşmiyorsun." |
| "Mükemmeliyetçisin." | "Her şeyi ciddiye almak bir süre sonra yorar." |

[tone.yaml:13-14](../../config/tone/tone.yaml) `shadow_safety.always_soften: true` bu sütunu kilitler.

### 4.2 Sütun 2 — Sen + Şimdiki Zaman

Tüm user-facing metin **ikinci tekil şahıs** + **şimdiki/geniş zaman**.

- ✅ "Güven gelmeden derinleşmiyorsun."
- ❌ "İnsanlar güven ararken derinleşmez."
- ❌ "Güven geldiğinde derinleşeceksin." (gelecek)
- ❌ "Size güven önemlidir." (çoğul, mesafeli)

**Tek istisna:** Aila'nın birinci tekil şahsı ("Merhaba, ben Aila…") — marka karakteri.

### 4.3 Sütun 3 — Spesifik Referans, Kanıt Katmanında

**DEĞİŞİKLİK — v1.0'dan v2.0'a revize:**

v1.0'da: "Teknik astrolojik terimler user-facing metinde kullanılmaz."
**v2.0'da:** "Spesifik referans **kanıt katmanında zorunlu**, başlık katmanında gizli."

Astroloji sözlüğü artık **iki katmanlı** kullanılır:

| Katman | Terim kullanımı | Örnek |
|---|---|---|
| **Headline / share** | ❌ Hayır | "Önce düşünüyorsun, sonra var oluyorsun." |
| **Body / paragraph** | ✅ Evet (spesifik) | "Saturn 3. ev · Oğlak. Söz disiplini iletişim alanında." |
| **Proof chip** | ✅ Evet (yarı-teknik) | "Merkür ☌ Venüs · 0°32′" |
| **Alt metin / bağlam** | ✅ Ev + gezegen + orb | "Ay △ Uranüs · 1°44′" |

**Neden değiştirdik:** Co-Star modeli (terim yasak) bir niş başarı; Chani modeli (spesifik referans + editorial) **retention** açısından daha güçlü. Türk pazarında sofistike konum boş. Ayrıca **kullanıcı kendi haritasının sözlüğünü biriktiriyor** — "bendeki o Saturn 3" demek başlıyor. Bu uzun vadeli bağ kuruyor.

### 4.4 Sütun 4 — Gölge Yumuşatılır, Patolojize Edilmez

Her zor gözlem için bir reframe:

| ❌ Patologize | ✅ Reframe |
|---|---|
| "Aşırı hassas." | "Aşırı hassas değilsin — yüksek çözünürlüklüsün." |
| "İçine kapanık." | "İçeri dönmek kaçmak değil — toparlanmak." |
| "Takıntılı." | "Bir şeyi sonuna kadar götürmek istiyorsun." |

### 4.5 Sütun 5 — İki Taraf Her Zaman Duruyor

**Shadow katmanı da bir taraf, gift katmanı da bir taraf.** Aynı özelliğin iki yüzü.

> "Her şeyi ciddiye almak bir süre sonra yorar. **Ama** aynı zamanda bu bir derinlik."

"Ama" bağlacı iki gerçeği birleştirir, ilkini geçersiz kılmaz.

---

## 5. Katman Sesleri

**v1.2 doktrini:** Her içerik katmanının farklı gramer + ton'u var. Aynı kişi için farklı katmanlar farklı nefeslerde konuşur.

### 5.1 `cause` — geçmiş / neden

**Ton:** İhtimalli. Geçmişi kesin bilemeyiz.
**Gramer:** "Olabilir" meşru.
**Highlight:** `hi-lav`
**Formül:** `[Çocukluk / erken dönem] + [gözlemlenen kalıp] + olabilir`

```
"Küçükken konuşmanın bir bedeli olduğunu öğrenmiş olabilirsin."
```

### 5.2 `mechanism` — nasıl çalışır

**Ton:** Kesin, geniş zaman.
**Gramer:** "Olabilir" yok. İşleyişi tarif eder, neden değil.
**Highlight:** `hi-stone` veya `hi-lav`
**Formül:** `[Geniş zaman] + [spesifik eylem] — [sonuç]`

```
"Söylemeden önce içinden bir kez daha geçiriyorsun."
```

### 5.3 `effect` — dışarıdan görünen

**Ton:** Kontrast yapısı zorunlu.
**Gramer:** İki cümle. Birinci dışarıdan, ikinci gerçek.
**Highlight:** `hi-stone` (ilk cümle), highlight ikinci cümlede olabilir
**Formül:** `[Dışarıdan / ilk izlenim] + nokta + [İçeride / gerçek]`

```
"Ciddi görünürsün. İçeride çok daha sıcak — ve görülmek isteyen."
```

### 5.4 `shadow` — gölge / iç gerilim

**Ton:** İki tarafı aynı anda görür. Yargılamaz.
**Gramer:** "Bu bazen X, bazen Y" kalıbı sık.
**Highlight:** `hi-lav`
**Formül:** `[Kalıp gözlemi] + [iki tarafı]`

```
"Bu bazen derinlik, bazen gecikme. İkisinin farkını hissedebilirsin."
```

### 5.5 `potential` — açılma / gelecek

**Ton:** Doğrudan, koşulsuz.
**Gramer:** "Olabilirsin" **yasak**. "Artık", "zaten", "bu sefer" kullanılır.
**Highlight:** `hi-lime` (en güçlü kelime)
**Formül:** `Artık [direkt fiil] / [olumlu geniş zaman] — koşulsuz`

```
"Seni görmelerini beklemeyi bıraktığında, zaten görülüyorsun."
```

### 5.6 `past_teaser` — kilitli içerik

**Ton:** Meraklandırır ama açmaz.
**Highlight:** `hi-lav`
**Formül:** `Bir dönem + [derin referans] + bir şey oldu`

```
"Bir dönem derinlemesine sarsılan bir şeyler oldu."
```

Tam haritaya yönlendirir.

### 5.7 Katman sırası — narrative akışı

Standart zincir: **effect → mechanism → cause → shadow → potential**

Kullanıcı önce dışarıdan gördüğü tanımla girer, sonra mekanizmasını öğrenir, sonra nereden geldiğini düşünür, sonra iki yüzünü görür, sonra açılmayı keşfeder.

### 5.8 `rationale` — karşılaştırmalı gerekçe (yardımcı)

**Ton:** Gözlem cümlesi, yargısız.
**Gramer:** "X de mümkündü; ama Y daha net ayrışıyor."
**Uzunluk:** 10–18 kelime.
**Mevcut karşılık:** `why_this_not_that` alanı (arketip output).

```
"Aynı çekirdekte rebel_designer tonu da mümkündü; ama systems_architect sende daha net ayrışıyor."
```

**Kural:** Rakip arketipi **yargılamaz** — "daha iyi" demez, "daha net ayrışıyor" der.

### 5.9 `context` — bağlam / sahne (yardımcı)

**Ton:** Şiirsel kısa — bağlamı ima eder.
**Gramer:** Noun phrase veya prepozisyon — cümle değil.
**Uzunluk:** 2–5 kelime.
**Mevcut karşılık:** `lunar_phase` chip, dönem adı.

```
"Dolunay altında"
"Balsamic an"
```

**Kural:** Astronomik isim yerine **şiirsel karşılığı**. "Full moon" değil "Dolunay altında".

### 5.10 `caution` — imperatif uyarı (yardımcı)

**Ton:** Kısa, imperatif, yargısız.
**Gramer:** Fiil-sonlu, 3–6 kelime.
**Uzunluk:** 3–6 kelime.
**Mevcut karşılık:** transit `watch_variants`.

```
"Aşırı idealizasyona dikkat."
"Her şeyi kontrol etmeye çalışma."
```

**Kural:** Uyarı şadow **değildir** — shadow gözlem, caution eylem uyarısı. İkisi ayrı rol.

---

## 6. Kontrast Yapısı

SHOU'nun **en sık kullanılan yapısı**. "Dışarıdan X. İçeride Y."

### Kalıp
```
[Dışarıdan / görünen / ilk izlenim] + nokta + [İçeride / gerçek / sürpriz]
```

### Örnekler
- "Ciddi görünür. İçeride çok daha sıcak — ve görülmek isteyen."
- "Dışarıdan sakin. İçeride bir kez daha geçiriyorsun."
- "Fikir alışverişi. Asıl neden, nasıl?"
- "Taşıyabilirim, dersin. Çoğu zaman haklısın."

### Kural
- İkinci cümle **ilkini yıkmaz — tamamlar**.
- İki cümle de ayakta durur (kes-yapıştır testi).
- Screenshot kültüründe en güçlü yapı.

### Uygulama yerleri
- Profile "İlk izlenim" section
- Share headline alt-havuzu (`shareContrast*` key'leri önerilir)
- Story Studio kart başlığı

---

## 7. Highlight Sistemi

Metin içinde üç renk işaretleme. En spesifik, en sürpriz, en ezberlenebilir kelimeye gider.

### 7.1 Üç renk, üç anlam

| Renk | Anlam | Nerede | Örnek |
|---|---|---|---|
| `hi-lime` 🟢 | Aksiyon / potansiyel / sürpriz | Potential katmanı, kontrastın ikinci yarısı | "**zaten görülüyorsun**" |
| `hi-lav` 🟣 | Derinlik / geçmiş / bilinçdışı | Cause, mechanism, savunma | "**konuşmanın bir bedeli**" |
| `hi-stone` ⚪ | Nötr / gözlem / ilk izlenim | Effect, shadow, beklenmedik onay | "**Ciddi görünür.**" |

### 7.2 Kurallar

- ✅ **Max 1 highlight / cümle.**
- ✅ **En spesifik öbek** highlight alır — "çok düşünüyorsun" değil "bir kez daha geçiriyorsun".
- ✅ **Genel fiiller** highlight almaz: "söylemeden önce", "geliyor".
- ✅ **Sıfat yığını** highlight almaz: "çok güçlü", "çok derin".
- ✅ **Alt metin** (gri, 10.5px) **renk almaz**. Highlight sadece ana cümlede.

### 7.3 Uygulama

Bu patch Flutter tarafında şu an **yok** — sadece chip'lerde accent var. İleride `InlineSpan` ile narrative paragraf render'ında `hi-lime` / `hi-lav` / `hi-stone` class'ları eklenir.

**Backend tarafında:** Phrase bank template'lerine `<hi-lime>...</hi-lime>` veya MD benzeri `==lime==` işaretleme eklenir. Render sırasında parse edilir.

---

## 8. Pattern Adlandırma

**SHOU'nun en güçlü hamlesi.** İki gezegeni tarif eder, etkileşimlerini gösterir, sonra o duruma **iki kelimelik bir ad** verir.

### 8.1 Neden çalışır

- **Somutlaştırır:** "Ay kare Merkür" bir teknik ifade — kimse yaşamaz. "Entelektüel savunma" bir deneyim — herkes bilir.
- **Ezberlenebilir:** Ad bir kanca gibi takılır. Kullanıcı günler sonra "bendeki o entelektüel savunma" diye geri döner.
- **Otorite kurar:** Adı olmayan şey bulanıktır; adı olan şey netleşir.

### 8.2 Dört adımlı formül

```
① iki öğe     → "[Gezegen A] + [Gezegen B] / [Ev] + [Açı + orb]"
               "Ay kare Merkür · 0°23′. Biri duygu, biri düşünce."

② etkileşim   → "Bu ikisi [ne yapıyor] — pratikte ne hissedilir?"
               "Bir şey hissettiğinde hemen 'bu neden, bu doğru mu?' başlıyor."

③ isim        → "Bu kalıbın bir adı var: [iki kelimelik ad]."
               "Bu kalıbın bir adı var: entelektüel savunma."

④ açma        → "[Günlük davranış] + [iki tarafı: koruyor / kısıtlıyor]"
               "Hissetmek yerine anlamak — seni koruyor ama gerçekten hissetmeni de engelliyor."
```

### 8.3 İsim seçme kuralları

- ✅ **İki kelime.** "Titiz estetik", "sessiz değerlendirme", "görünmeme korkusu".
- ✅ **Sıfat + isim.** Sıfat niteliği (titiz, sessiz), isim davranışı (estetik, savunma).
- ✅ **Kullanıcının tanıdığı kavram.** "Entelektüel savunma" psikoloji terimi — tanıdık, bağlantı yeni.
- ✅ **Nötr.** "Kontrol kaynağı" ✓ · "kontrol takıntısı" ✗.
- ❌ **Mistik jargon:** "Satürnyen disiplin" ✗ → "erken sorumluluk" ✓
- ❌ **Klinik jargon:** "Kaçınmacı bağlanma stili" ✗ → "mesafeli yakınlık" ✓

### 8.4 Sıklık

| Nerede | Ne kadar |
|---|---|
| Slide serisi (6 slayt) | 1–2× |
| Profil kartı | 0–1× |
| Aynı ad tekrarı | Haritada 1 kez konur, sonraki slaytlarda "o kalıp" ile geri çağrılır |
| Tam harita toplamı | 3–5 ana adlandırma — kullanıcı sözlüğünü biriktirir |

### 8.5 Uygulama

Backend'te yeni content module: [`pattern_names_tr.py`](../../backend/app/natal/narrative/pattern_names_tr.py) (henüz yok — **Patch 2** önerisi).

Starter pack için [Ek B](#ek-b-pattern-adlandırma-starter-pack).

---

## 9. Yetenek Formülü

**Yetenek her zaman kanıtla gelir.** "Güzel yazarsın" tek başına boş. Kanıt = açı + orb veya gezegen + ev.

### 9.1 Üç parça

```
① ad          → "[Spesifik eylem / beceri — 3-6 kelime]"
               "Söylenmeyeni duymak."

② kanıt       → "[Açı + orb veya gezegen + ev]"
               "Ay △ Uranüs · 1°44′. Algı hızı normalin üstünde."

③ uygulama    → "[Hayatta nerede işe yarıyor — 1 cümle]"
               "Bir konuşmada asıl meseleyi, söylenmeyen şeyi erken fark edersin."
```

### 9.2 Kurallar

- ✅ **Spesifik eylem.** "Doğru kelimeyi doğru zamanda bulmak" ✓ · "iyi konuşmak" ✗
- ✅ **Nadirlik istatistikle.** "Bu açı haritalarda sık görülmez" ✓ · "Çok özel birisin" ✗
- ✅ **"Güçlü yan" ≠ "yetenek".** Güçlü yan karakter (dürüstsün). Yetenek uygulanabilir beceri (dürüstlüğü iletişime dönüştürüyorsun).
- ❌ "Çok yeteneklisin!" — ünlem + genel sıfat = motivasyon sesi.
- ❌ "Steve Jobs'ta da bu vardı" — ünlü karşılaştırma = ucuz.

### 9.3 Uygulama

**Yeni profile section önerisi:** "Ne iyi yapıyorsun" — 3–5 yetenek, her biri 3 parça halinde. Backend'te [`talent_patterns_tr.py`](../../backend/app/natal/narrative/talent_patterns_tr.py) modülü (henüz yok — **Patch 6**).

---

## 10. Cümle Uzunluk Hiyerarşisi

### 10.1 Üç kademe

| Kademe | Kelime sayısı | Örnek |
|---|---|---|
| ✅ **Başlık** | 2–5 | "Ciddi görünür." |
| ✅ **Ana cümle** | 8–14 | "Söylemeden önce içinden bir kez daha geçiriyorsun." |
| ✅ **Alt metin** | max 28 | "Bu bazen derinlik, bazen gecikme. İkisinin farkını hissedebilirsin." |
| ⚠️ Sınırda | ~30 | "Artık söylemeden önce çok düşünüyorsun — bu oradan geliyor olabilir, en azından bir kısmı." |
| ❌ Çok uzun | 35+ | "Küçüklüğünde yaşanan deneyimler seni şekillendirmiş ve bu da şimdi ilişkilerde ve iletişimde kendini gösteriyor." |

### 10.2 Share headline özel — 6–12 kelime

[share_line_playbook.md](share_line_playbook.md) kural 1.

---

## 11. Spesifik Referans Doktrini

### 11.1 Referans hiyerarşisi

| Referans | Ne zaman | Güven derecesi |
|---|---|---|
| **Orb derecesi** (0°14′) | "Neredeyse tam açı" — en güçlü | ⭐⭐⭐⭐⭐ |
| **Ev numarası** (3. ev) | Gezegen + ev her zaman birlikte | ⭐⭐⭐⭐ |
| **Stellium sayısı** (5×) | "5 gezegen, tek ev" — nadir, vurgulanır | ⭐⭐⭐⭐ |
| **Retrograd** (Rx) | İçe dönme, yeniden işleme — ses değişir | ⭐⭐⭐ |
| **Sadece gezegen adı** (Saturn) | Bağlam yok — zayıf | ⭐⭐ |
| **Sadece burç** (Oğlak) | Bağlam yok — en zayıf | ⭐ |

### 11.2 Sayı + metin entegrasyonu

```
✅ "Ay △ Venüs. Estetik zeka doğuştan."           — referans önce
✅ "0°14′ — neredeyse tam açı."                    — orb vurgu
✅ "Merkür ☌ Venüs · 0°32′. Ayrılmaz halde."     — kanıt katmanı

❌ "Senin haritanda bazı özellikler var."          — referans yok
❌ "Güneş, Ay, Merkür, Venüs, Mars ilginç."       — spesifik değil
```

### 11.3 Katman bazında referans yoğunluğu

| Katman | Referans yoğunluğu |
|---|---|
| Share line | ❌ yok |
| Effect (ilk izlenim) | Minimum — "Terazi yükselen bu" civarı |
| Mechanism | Orta — gezegen + ev |
| Cause | Orta — gezegen + ev |
| Shadow | Düşük — iki tarafı gösterirken referans dağıtır |
| Potential | Düşük — koşulsuzluk ön planda |
| **Proof — raw** | **Maksimum** — açı + orb, telgraf |
| **Proof — soft** | Orta — insan cümlesi, veriye köprü |
| Fun fact | Yüksek — nadirlik istatistiği ile |

### 11.4 Proof — İki Seviyeli (v2.1)

Proof tek alan değil, iki seviye. Payload'a **ayrı iki field**:

| Alan | Rol | Format | Örnek |
|---|---|---|---|
| `proof_raw` | Astrolojik künye — telgraf | "Yönetici · Ev · İşaret" | `"Satürn · 3. ev · Oğlak"` |
| `proof_line` | İnsan cümlesi — veri/his köprüsü | Tek cümle, 10–18 kelime | _(Şimdilik boş — içerik ileride; **altyapı hazır**)_ |

**Amaç:** `proof_raw` otorite kurar, `proof_line` "bu yüzden böyle hissediyorsun" köprüsü kurar. İkisi birbirinin yerine geçmez — birlikte çalışırlar.

### 11.5 Proof yazım kuralları

- **Title Case.** `"Satürn · 3. ev · Oğlak"` — lowercase transform **yok**. Python `.lower()` Türkçe locale-aware değil (`İ` → `i̇` bug'ı). Template zaten Title Case render edilir.
- **Tek ayraç: `·` (middle dot).** Virgül değil, tire değil. Görsel telgraf.
- **3 parça standardı:** yönetici · ev · işaret. Redundancy yok (`"7. ev · 7. ev {dsc_sign}"` yasak).
- **Dignity sembol yok** (zaten chip'te var).
- **Proof_line TR'den soyut cümle değil** — kullanıcının "aaa" diyeceği, `proof_raw`'u insanlaştıran cümle.

### 11.6 Accessibility (WCAG AA minimum)

UI tarafında proof render edilirken:

- Alpha ≥ **0.60** (text on bg kontrastı 4.5:1 minimum)
- Font size ≥ **11px**
- Widget test'e contrast invariant — alpha 0.60'ın altına düşmez
- "Sessizleştirelim" isteği açısı (%45) **yetersiz** — okunabilirlik şart

### 11.7 Template kapsamı — her core thread için zorunlu

Her core natal thread için `proof_raw` template **tanımlı olmalıdır**. Yeni thread eklendiğinde `_PROOF_LINE_TEMPLATES` (backend) içinde karşılığı yoksa CI / code review engeli. Bazı thread'lerde proof var, bazılarında yok — **ritim kırılır, yasak**.

Mevcut 4 core thread:
- `identity_mechanics`
- `relationships_depth`
- `career_visibility`
- `direction_learning`

h-variant'lar (`:h11`, `:h8`, `:h3`, `:h12`) base thread'den inherit eder.

### 11.8 i18n — locale-gated render

Şu an template string'leri Türkçe hard-coded (`"3. ev"`, `"MC"`). İngilizce locale'de render **edilmez**:

```dart
if (locale == 'tr' && proofRaw.isNotEmpty) {
  renderProofChip(proofRaw);
} else {
  SizedBox.shrink();
}
```

EN template havuzu ayrı PR'da gelir (S1b veya sonrası). **Ön koşul:** Template rigor TR + EN paritesine — her TR template için EN karşılığı.

### 11.9 Render güvenliği

| Durum | Davranış |
|---|---|
| Context variable eksik | Template `""` döner |
| Thread ID `_PROOF_LINE_TEMPLATES`'de yok | `""` döner |
| h-variant → base thread fallback | Otomatik |
| Render exception | Try/except → `""` |
| Legacy caller (chart_planets yok) | `""` |
| Locale ≠ TR | UI render etmez |

**Invariant:** `proof_raw` daima payload'ta — empty string veya rendered. **Asla `null`.**

---

## 12. Kullanıcı Durumu × Ton Matrisi

| Kullanıcı durumu | Trigger | Ton kayması |
|---|---|---|
| Keşif modu (yeni) | Onboarding sonrası | Warmth ↑, certainty ↓ |
| Hüzünlü / kriz | (gelecek: mood check) | Warmth ↑↑, directness ↓, tempo ↓ |
| Kariyer arayışı | career thread aktif | Directness ↑, specificity ↑ |
| İlişki zorluğu | synastry friction | Warmth ↑, izin cümlesi zorunlu |
| Kutlama | soft.career.any | Tempo ↑, certainty ↑ |
| Gölge | saturn/pluto aktif | Warmth ↑↑, reframe zorunlu |
| Merak (explainability açık) | Panel tap | Directness ↑, specificity ↑ |
| Paylaşım anı | Share card üretiliyor | Certainty ↑↑, specificity ↓ |

---

## 13. Yüzey Bazında Kopya Kalıpları

### 13.1 Home Hero
- 4–8 kelime, ikinci tekil, rotasyonlu.
- Kaynak: [app_tr.arb](../../mobile/lib/l10n/app_tr.arb) `shareHomeHeroRotation1..4`

### 13.2 Archetype Card — 3 Katmanlı

| Katman | Örnek | Kural |
|---|---|---|
| `label` | "İnşaatçı" | Kelime, nötr |
| `one_liner` | "Kendini en çok düşünme biçimin üzerinden kuruyorsun." | 8–14 kelime |
| `share_headline` | "Önce düşünüyorsun, sonra var oluyorsun." | 6–12 kelime |

Kaynak: [phrase_lib_tr_natal.py](../../backend/app/natal/narrative/phrase_lib_tr_natal.py)

### 13.3 Profile Narrative — 5 Katman (YENİ)

Her thread variant şu yapıya geçmeli (v2.0 öneri — şu an mevcut yapıda yok):

```python
{
    "title": "Kimlik omurgan",
    "share_headline": "Önce düşünüyorsun, sonra var oluyorsun.",
    "layers": {
        "effect": "Ciddi görünürsün. İçeride çok daha hızlı.",
        "mechanism": "Söylemeden önce içinden bir kez daha geçiriyorsun.",
        "cause": "Küçükken konuşmanın bir bedeli olduğunu öğrenmiş olabilirsin.",
        "shadow": "Bu bazen derinlik, bazen gecikme.",
        "potential": "Artık tartmak ile susmak aynı şey değil — söz isabetli.",
    },
    "pattern_name": "sessiz değerlendirme",  # opsiyonel
}
```

### 13.4 Profile Detail Flow — Proof Chip (v2.1 S1)

Uzun okuma yüzeyi. Her thread paragraph'ının altına, sessiz bir künye:

- `proof_raw` — render edilir (§11.4)
- `proof_line` — şimdilik render **yok** (altyapı hazır, içerik yok)
- Sadece TR locale (§11.8)
- Accessibility minimum (§11.6)

Widget spec: sol border lime (2px, alpha 0.55), Inter 11px, alpha 0.60, Title Case metin, maxLines 1 + ellipsis, paragraph'tan 14px sonra. Boş string → `SizedBox.shrink`.

### 13.5 Explainability Panel — 4 Block

[explainability_panel.dart](../../mobile/lib/app/profile/explainability_panel.dart) birebir sync.

| Block | Source | Kural |
|---|---|---|
| 1. Neden bu, başka değil | `why_this_not_that` | Editorial cümle, karşılaştırma — yargısız |
| 2. Güç derecesi | `score_meets_primary_threshold` × `dignity_bonus` | Nitel: "güçlü oturmuş" / "net ama gerilimde" / "net ayrışıyor" / "arka planda" / "hafif" |
| 3. Gerilim ritmi | `aspect_direction_breakdown` | "N yaklaşan gerilim" / "N işlenmiş hareket" / "N tam aspect" — unknown gizli |
| 4. Bağlam | `lunar_phase` | 8 faz TR etiketi — şiirsel |

Dignity chip variant'ları:
- `bonus ≥ 0.12` → "[Planet] güçlü destekli"
- `bonus ≥ 0.05` → "[Planet] destekli"
- `bonus ≤ -0.12` → "[Planet] yabancı alanda"
- `bonus ≤ -0.05` → "[Planet] hafif gerilimde"
- peregrine — chip yok

### 13.6 Transit Card — 4 Katmanlı
| `headline_variants` | `share_headline_variants` | `summary` | `do_variants` + `watch_variants` |

Kaynak: [transit_templates.v1.json](../../backend/app/transit/content/tr/transit_templates.v1.json)

`watch_variants` = **caution** layer (§5.10). `do_variants` = potential (imperatif).

### 13.7 Synastry — 3 Katmanlı
| `label` | `share_line` | `one_liner` |

**"Siz" çoğul** (ikinci tekil tek istisnası). Pair signature yargılamaz — fark eder. Mevcut `label` = **pattern_name** rolünde.

Kaynak: [synastry_phrase_bank_tr.py](../../backend/app/synastry/narrative/synastry_phrase_bank_tr.py)

### 13.8 Story Studio Kart Kapanışı
4–8 kelime mühür satırı.

### 13.9 Aila

**Açılış** (revize öneri):
> "Merhaba, ben Aila — psikolojik astrolojiyle çalışıyorum. Sana falcılık yapmam; haritanda gördüğüm şeyi sana sen'in kelimelerinle geri veririm. Bugün ne var?"

**İmza satırı — her yanıt sonunda bir**:
- "Bıraktığın zaman değil, bırakamadığın zaman kayıp ediyorsun."
- "Eski kapıyı açmak, eskiye dönmek değildir."
- "Haritada gördüğüm şey: sen zaten biliyorsun."
- "Herkesi anlıyorsun. Bugün sadece kendini anla."

**Paywall** (revize):
> "Aila'yla sohbetin bir eşiğe geldi. Derinleşmeye devam etmek için Pro ya da kredi paketiyle bağa alan aç."

### 13.10 Empty / Loading / Error
Sabırlı, yargısız, backend jargonu sızmamalı.

### 13.11 Share Card
Kırık beyaz zemin + lime accent. Sessiz `astrologi` imzası. URL yok, CTA yok.

---

## 14. Sözlük

### 14.1 DO — tercih edilen kelimeler

**Astro kavram insani karşılığı (ama kanıt katmanında teknik kullanım da OK):**

| Kavram | Yarı-teknik (proof chip / paragraph) | Tam-insani (headline / share) |
|---|---|---|
| aspect / açı | "temas", "0°32′ açı" | "ayrılmaz halde" |
| transit | "geçiş", "dönem" | "etki", "rüzgâr" |
| applying | "yaklaşan" | "büyüyen gerilim" |
| separating | "işlenmiş" | "geride kalmış" |
| exact | "tam aspect", "0°14′" | "tam zamanlamada" |
| retrograde | "Rx", "geri bakış" | "geri izleme dönemi" |
| house / ev | "3. ev" (paragraph OK) | "iletişim alanı", "yakın çevre" |
| conjunction | "☌" (chip'te), "kavuşum" | "birleşim", "ayrılmaz" |
| square | "□", "kare" | "gerilim", "sürtüşme" |
| trine | "△" | "akış", "destek" |
| opposition | "☍" | "karşıtlık" |
| natal | "natal harita" (paragraph) | "harita" |

### 14.3 Naming Standardı (v2.1)

Aynı rolün farklı isimlerle gezinmesi ses yönetişimini zayıflatır. Yeni kod için standart:

| Rol | Standart isim | Tarihsel isimler (geriye uyumluluk) |
|---|---|---|
| Alıntılık tek satır | **`share_line`** | `share_headline` (natal), `share_headline_variants` (transit) — alias olarak çalışmaya devam |
| Astrolojik künye | **`proof_raw`** | — (yeni) |
| İnsan köprü cümlesi | **`proof_line`** | — (yeni, içerik ileride) |

**Kural:** Yeni eklenecek her alan standart ismi kullanır. Mevcut alanlar **silinmez** — rename migration ayrı PR (zamanı: S3 / share_line genişletme).

**Metaforlar (tüm katmanlar):**
- açılmak / kapanmak, akış, omurga, kas, eşik, kapı, ritim, sahne / perde arkası, taşımak, koymak

**Duygu nitelemeleri:**
- net / bulanık, yakın / uzak, dolu / boş, hafif / ağır, işlenmiş / ham

### 14.2 Katman-spesifik kelime haritası

| Katman | DO | DON'T |
|---|---|---|
| cause | "olabilir", "öğrenmiş", "küçükken" | "kesinlikle", "doğrudan" |
| mechanism | "-iyorsun" şimdiki zaman, "zaten", "her seferinde" | "-ebilirsin", "olabilir" |
| effect | "görünürsün", "izlenim", "ilk bakışta" | "-iyorsun" (içerik için), uzun açıklama |
| shadow | "bazen X, bazen Y", "ikisinin farkı" | "kötü", "yanlış", "problemli" |
| potential | "artık", "zaten", "bu sefer" | "olabilirsin", "yapabilirsin" |

---

## 15. Yasaklar

### 15.1 Mistik jargon — tamamen yasak

| Yasak | Alternatif |
|---|---|
| "Enerji akışı" | Hangi gezegen, hangi açı — "Güneş △ Jüpiter" |
| "Frekansın yükseldi" | — yazma |
| "Evren sinyali" | "Saturn dönüşümü başlıyor" |
| "Kozmik plan / misyon" | "Haritan bu yöne baskı yapıyor" |
| "Aura", "çakra", "kundalini" | — hiç kullanma |
| "Manifest", "affirmation" | — hiç kullanma |
| "Yüksek benlik" | "Sen" |

### 15.2 Motivasyon dili — yasak

| Yasak | Alternatif |
|---|---|
| "Çok güçlü çıkacaksın!" | "Saturn 8. ev geçişi. Bazı kimlikler düşüyor — bu plana dahil." |
| "Sen özelsin" | "5 gezegen, tek ev. Varlığın taşıdığı ağırlık nadir." |
| "Gerçek gücün içinde" | "Güneş 1. ev. Güç sende zaten var." |
| "İnanırsan olur" | — yazma |
| "Sen harikasın!" | — yazma |
| "Başaracaksın!" | — yazma |

### 15.3 Belirsiz sıfatlar — yasak

**Genel kural:** Sıfat tek başına boş. Spesifik eylem veya öbek seç.

| Yasak | Yerine |
|---|---|
| "akışkan" | Ay işaretine özgü — Aslan "sıcak ve görülmek isteyen", İkizler "aynı anda birkaç tarafını gören", Balık "sınır çekmekte zorlanan" |
| "çok daha fazlası" | "İçeride her şeyi sessizce tartan bir zihin var." |
| "derin" tek başına | Jüpiter 9. ev → anlam arayan; Plüton → dönüştürücü; Neptün → sınır eriten |
| "çok güçlü" sıfat | "söylenmeyeni erken duymak" — spesifik beceri |
| "ilginç bir yapı" | "Merkür ☌ Venüs · 0°32′ — nadir" |

**Ay işareti × iç tanım sözlüğü → [Ek A](#ek-a-spesifik-sıfat-sözlüğü)**

### 15.4 Dil / gramer yasakları

| Yasak | Sebep |
|---|---|
| **"Olabilirsin"** potential'da | Potential **koşulsuz** olmalı. Cause'da "olabilir" meşru. |
| **Siz, o, onlar** | Mesafe yaratır. Her cümle "sen". Tek istisna synastry "siz" (ikili). |
| **"Sanki", "gibi görünüyor", "bir şekilde"** aşırı yumuşatma | Cümle ya kesin ya ihtimalli (cause). Arası yok. |
| **Soru ile bitirme** | "Bu sana tanıdık geliyor mu?" — SHOU bildirir, sormaz. Tek istisna Aila. |
| **Ünlem** | Asla. |
| **Üç nokta (…)** | Viral değil. |

---

## 16. Teknik Koruma Bantları

### 16.1 AI prompt yerleşik yasakları
[prompts/__init__.py](../../backend/app/ai/prompts/__init__.py):
- İngilizce sözcük: YASAK
- Teknik terim **başlık / opening'de**: YASAK (kanıt katmanında OK — v2.0 revizyon!)
- Emoji/sembol: YASAK
- Soyut metafor ("bir anlatı seni çağırıyor"): YASAK

### 16.2 L10N geriye uyumluluk
- Mevcut key silme yok
- Yeni key additive — her zaman güvenli
- TR ↔ EN parite zorunlu

### 16.3 Chip phrase değişimi
Explainability panel chip'i değişiyorsa:
1. [explainability_panel.dart](../../mobile/lib/app/profile/explainability_panel.dart) helper güncellenir
2. Widget test güncellenir (28 test)
3. §13.4 tablosu güncellenir

### 16.4 Scoring ve voice ayrı
Voice değişikliği scoring'e dokunmaz. `scoring_profile_version` voice-only PR'da bump edilmez.

### 16.5 Share card görsel
CLAUDE.md `lib/design/theme/` kuralı geçerli. Amber / sıcak ton yasak. Kırık beyaz + lime.

---

## 17. Rotasyon ve Seed Kuralları

[phrase_lib_tr_natal.py](../../backend/app/natal/narrative/phrase_lib_tr_natal.py) `pick_variant(seed, n)` mekanizması kullanılır.

| Surface | Seed |
|---|---|
| Home hero | `user_id + date` |
| Transit share_headline | `user_id + transit_key + date` |
| Natal thread variant | `user_id + thread_id` |
| Synastry pair_signature | `user_id + partner_id + pair_category` |
| Aila imza | `user_id + session_id + message_index` |
| Story Studio | `user_id + card_id` |

---

## 18. QA Check-List

### 18.1 Share headline — 4 soru
[share_line_playbook.md §3](share_line_playbook.md):
- [ ] Ekran görüntüsünde okunabiliyor mu?
- [ ] Arkadaşına atmak ister misin?
- [ ] Bir şey açığa çıkarıyor mu?
- [ ] Astrolojik terim sızıyor mu? (share'de sızmamalı)

### 18.2 Narrative cümle — 9 soru (genişletildi)
- [ ] İkinci tekil şahıs mı? (§4.2)
- [ ] Şimdiki / geniş zaman mı? (katman kurallarına uygun)
- [ ] Hangi katmanda? Katmanın ses kuralına uyuyor mu? (§5)
- [ ] Yargısız mı? Reframe var mı? (§4.1, §4.4)
- [ ] Tek iddia, tek cümle mi? Kontrast kullanılıyorsa iki cümle de ayakta duruyor mu? (§6)
- [ ] Belirsiz sıfat ("derin", "akışkan", "çok güçlü") var mı? (§15.3)
- [ ] Kanıt katmanındaysa spesifik referans var mı? (§11)
- [ ] Yasaklı kelime (mistik / motivasyon) sızıyor mu? (§15)
- [ ] Uzunluk kademesine uyuyor mu? (§10)

### 18.3 Pattern adı — 5 soru
- [ ] İki kelime mi? (sıfat + isim)
- [ ] Kullanıcının tanıdığı kavram mı?
- [ ] Nötr mü? Hem güç hem hassasiyet barındırıyor mu?
- [ ] Mistik / klinik jargon mı?
- [ ] Davranışı anında çağırıyor mu?

### 18.4 Yetenek — 3 parça check
- [ ] Ad spesifik eylem mi?
- [ ] Kanıt (açı + orb veya gezegen + ev) var mı?
- [ ] Uygulama cümlesi hayatta nerede işe yaradığını gösteriyor mu?

---

## 19. Yönetişim

### 19.1 Sahipler
- **Voice lead:** Sahra (editorial authority)
- **Implementor:** engineering ekibi
- **Update cadence:** PR bazlı

### 19.2 Değişiklik süreci
1. Öneri `docs/voice/` içinde draft
2. Voice lead onayı
3. Merge + relevant `.arb` / phrase bank güncelleme
4. Widget / unit test güncelleme
5. Bu doküman **aynı commit'te** güncellenir

### 19.3 Onay zinciri
- Yeni `share_headline` → Voice lead
- Yeni thread variant → Voice lead + astroloji review
- Yeni pattern adı → Voice lead + astroloji review (adın doğru yerleşime bağlandığı)
- AI prompt değişikliği → Voice lead + technical
- Share card görsel → Voice + design

---

## Ek A. Spesifik Sıfat Sözlüğü

"Akışkan" gibi genel sıfatlar yerine **işaret-spesifik** kelimeler. v1.2'nin "her işareti kendisiyle tarif et" kuralı.

### Ay işareti × iç dünya betimlemesi

| Ay | İçeride |
|---|---|
| Koç | direkt, taşmaya meyilli, ilk tepki veren |
| Boğa | yavaş kök salan, istikrar arayan |
| İkizler | aynı anda birkaç tarafını gören, bağlantı kuran |
| Yengeç | saklayıp koruyan, dalga halinde hisseden |
| Aslan | sıcak ve görülmek isteyen |
| Başak | ayıklayan, dokusu önemseyen |
| Terazi | denge arayan, karar gerilen |
| Akrep | derine inmek isteyen, kolay göstermez |
| Yay | anlam arayan, genişleyen |
| Oğlak | dayanıklı, zamanla test eden |
| Kova | ayrı duran, bağlamı gören |
| Balık | sınır çekmekte zorlanan, geçirgen |

### Yükselen × dış dünya betimlemesi

| Yükselen | Dışarıdan |
|---|---|
| Koç | direkt, enerjik, açık |
| Boğa | sakin, kokulu, yerli |
| İkizler | çevik, meraklı, hızlı |
| Yengeç | yumuşak, koruyan, dokunulabilir |
| Aslan | gösterişli, varlıklı, sıcak |
| Başak | temiz, hassas, ölçülü |
| Terazi | zarif, dengeli, dingin |
| Akrep | mesafeli, yoğun, dikkatli |
| Yay | açık, arayan, geniş |
| Oğlak | mesafeli, kontrollü, değerlendirici |
| Kova | farklı, serin, düşüncede |
| Balık | yumuşak, sınırsız hisseden, dalga |

### MC × kariyer doğal akış yeri

| MC | Doğal akış |
|---|---|
| Koç | öne çıkan, başlatan — liderlik doğal |
| Boğa | sağlam üreten, uzun soluklu |
| İkizler | anlatan, bağlayan, çok parçalı |
| Yengeç | dokunan, koruyan, topluluğa bakan |
| Aslan | sahnede, yaratıcı, görünür |
| Başak | hizmet eden, ince çalışan, düzelten |
| Terazi | arabulucu, estetik kuran |
| Akrep | dönüştüren, derin inceleyen |
| Yay | öğreten, açan, geniş düşünen |
| Oğlak | inşa eden, otorite kuran |
| Kova | yenilikçi, kolektife bakan |
| Balık | şifalandıran, hayal kuran |

### Kullanım

Template context'e eklenebilir alanlar:
- `{moon_inner}` — MOON_INNER_TR[moon_sign]
- `{asc_outer}` — ASC_OUTER_TR[asc_sign]
- `{mc_flow}` — MC_FLOW_TR[mc_sign]

Phrase bank'ta kullanım:
```python
"paragraph": (
    "Dışarıdan {asc_outer}. İçeride {moon_inner}."
    # Örnek render: "Dışarıdan mesafeli, kontrollü, değerlendirici. İçeride sıcak ve görülmek isteyen."
),
```

---

## Ek B. Pattern Adlandırma Starter Pack

Backend'te yeni module: [`pattern_names_tr.py`](../../backend/app/natal/narrative/pattern_names_tr.py) (henüz yok — öneri).

### B.1 Aspect-bazlı kalıplar

| Kombinasyon | Ad | Çerçeve |
|---|---|---|
| Ay □ Merkür | **entelektüel savunma** | Duygu (Ay) ve düşünce (Merkür) birbirini zorluyor. Hissettiğinde "bu neden?" başlıyor. |
| Merkür ☌ Venüs | **titiz estetik zeka** | Düşünce ve estetik aynı noktada. Güzel bulmadığın fikri anlatamıyorsun. |
| Ay △ Uranüs | **erken algı** | Algı hızı normalin üstünde. Söylenmeyeni erken duyuyorsun. |
| Güneş □ Satürn | **erken sorumluluk** | Kimlik (Güneş) disiplin altında. Küçükken hızlı büyümek zorunda kalmış olabilirsin. |
| Venüs □ Satürn | **mesafeli yakınlık** | Sevgi (Venüs) sınır içinde (Satürn). Güven gelmeden açılmıyorsun. |
| Mars ☌ Plüton | **yoğun irade** | Hareket (Mars) derinlikle (Plüton) kavuşmuş. Küçük şeyleri bile sonuna götürüyorsun. |
| Merkür □ Neptün | **geçirgen zihin** | Düşünce (Merkür) sınır çekmekte zorlanıyor (Neptün). Başkasının düşüncesini kendinin sanmak kolay. |
| Jüpiter △ Satürn | **yapılı büyüme** | Genişleme (Jüpiter) disiplinle (Satürn) uyumlu. Yavaş ama kalıcı büyüyorsun. |

### B.2 Ev-bazlı kalıplar

| Kombinasyon | Ad | Çerçeve |
|---|---|---|
| Güneş 12. ev | **perde arkası çalışma** | Kimlik görünmez alanda. Emeğin genelde gizli. |
| Güneş 1. ev | **direkt varlık** | Sen olmak ve görünmek aynı şey. Savunma azaltılmış. |
| Ay 8. ev | **derin hisseden** | Duygu dönüşüm evinde. Yüzeyde kalamıyorsun. |
| Satürn 3. ev | **sessiz değerlendirme** | Söz disiplini iletişim alanında. Her cümleyi tartıyorsun. |
| Jüpiter 9. ev | **büyük çerçeve** | Anlam arayışı doğal alanda. Dağınık parçaları tek fikirde birleştiriyorsun. |
| Venüs 11. ev | **topluluk estetiği** | Güzellik ve değer kolektife açılıyor. Gruplarda zarif. |
| Mars 10. ev | **görünür irade** | Hareket kariyer evinde. Başarın hırslı ama doğrudan. |
| Neptün 7. ev | **sınırsız ortaklık** | Hayal ilişki evinde. Kolay idealize edip hayal kırıklığı yaşayabilirsin. |
| 5 gezegen 1. ev (stellium) | **yoğun kimlik** | Varlığın taşıdığı ağırlık nadir. Bir odaya girdiğinde fark ediliyor. |

### B.3 Yükselen + Ay kontrast kalıpları

| Kombinasyon | Ad | Çerçeve |
|---|---|---|
| Yükselen Oğlak + Ay Aslan | **ciddi görünüş / görülmek isteyen iç** | Dışarıda mesafeli, içeride yoğun ve görülmek isteyen. |
| Yükselen Terazi + Güneş 12. | **zarif görünüş / perde arkası çalışma** | İlk izlenim uyumlu, asıl çalışma gizli. |
| Yükselen Akrep + Ay Yengeç | **sert görünüş / şefkatli iç** | Dışarıdan dikkatli, içeride dalga halinde hisseden. |
| Yükselen İkizler + Ay Boğa | **çevik görünüş / kök isteyen iç** | Hızlı ve meraklı, ama istikrar arayan bir iç. |

Kullanım: natal narrative'in orta-son katmanında 1 kez, "Bu kalıbın adı: ..." cümlesiyle. Haritada 3–5 ad çıkar, kullanıcı kendi sözlüğünü biriktirir.

---

## Ek C. Yüzey → Payload Haritası

| Surface | Payload alanı | Voice kuralı |
|---|---|---|
| Archetype card `label` | `top_archetypes[].label` | §13.2 |
| Archetype card `one_liner` | `top_archetypes[].one_liner` | §13.2 |
| Archetype share_line | `top_archetypes[].share_headline` (alias `share_line`) | §13.2 + playbook |
| Archetype layered paragraph | `top_archetypes[].layers.*` (Patch önerisi) | §5, §13.3 |
| Proof chip (raw) | thread-level `proof_raw` (v2.1 S1) | §11.4–11.9, §13.4 |
| Proof cümle (soft) | thread-level `proof_line` (v2.1 altyapı, içerik sonra) | §11.4 |
| Pattern adı | `top_archetypes[].pattern_name` (yeni) | §8 |
| Talent | yeni `talents[].{name,proof,application}` (Patch 6) | §9 |
| Rationale | `why_this_not_that` | §5.8, §13.5 |
| Context — natal | top-level `lunar_phase` | §5.9, §13.5 |
| Caution — transit | `transit.watch_variants` | §5.10, §13.6 |
| Explainability — Block 1 | `why_this_not_that` (rationale) | §13.5 |
| Explainability — Block 2 strength | `score_meets_primary_threshold` × `dignity_bonus` (proof) | §13.5 |
| Explainability — Block 3 | `aspect_direction_breakdown` (proof) | §13.5 |
| Explainability — Block 4 | top-level `lunar_phase` (context) | §13.5 |
| Transit headline | `transit.headline_variants` | §13.6 |
| Transit share_line | `transit.share_headline_variants` (alias `share_line_variants`) | §13.6 + playbook |
| Transit summary | `transit.summary_variants` | §13.6 |
| Synastry pattern_name | `PAIR_SIGNATURE.label` | §13.7 |
| Synastry share_line | `PAIR_SIGNATURE.share_line` | §13.7 + playbook |
| Story Studio close | `shareStoryStudio*Close` (l10n) | §13.8 |
| Aila intro | `aiIntroMessage` (l10n) | §13.9 |
| Aila signature | `shareAilaSignature1..4` (l10n) | §13.9 |

---

## Ek D. Mevcut Field → Layer Haritası (v2.1)

Referans tablosu — hangi kod alanının hangi layer rolünü üstlendiği. Aynı rol için **farklı isimler** var — §14.3 standardı tarihsel isimleri tolere eder.

### Natal pipeline

| Mevcut field | Hangi layer? | Durum |
|---|---|---|
| `top_archetypes[].label` | — (rol adı, pattern_name değil) | OK |
| `components.dignity_bonus` | **proof** kaynağı (chip) | OK |
| `aspect_direction_breakdown` | **proof** kaynağı (chip) | OK |
| `why_this_not_that` | **rationale** | OK, adlandırıldı (v2.1) |
| `share_headline` (thread) | **share_line** | OK — alias |
| `proof_raw` (thread, v2.1 S1) | **proof (raw)** | Yeni |
| `proof_line` (thread, v2.1 S1) | **proof (soft)** | Yeni — altyapı, içerik yok |
| top-level `lunar_phase` | **context** | OK, adlandırıldı (v2.1) |
| Thread `title` | section_header | ⚠️ pattern_name ile karıştırılmasın |
| Thread `one_liner` | mechanism / effect | ⚠️ karışık |
| Thread `paragraph` | mechanism (çoğu) + effect + az cause | ⚠️ katmanlanmamış |

### Transit pipeline

| Mevcut field | Hangi layer? |
|---|---|
| `headline_variants[]` | section_header (etiket) |
| `share_headline_variants[]` | **share_line** |
| `summary_variants[]` | mechanism / effect |
| `do_variants[]` | **potential** (imperatif) |
| `watch_variants[]` | **caution** (v2.1) |
| `themes[]` | — (meta) |

### Synastry pipeline

| Mevcut field | Hangi layer? |
|---|---|
| PAIR_SIGNATURE `label` | **pattern_name** (✅ zaten pattern_name rolünde!) |
| PAIR_SIGNATURE `one_liner` | mechanism / effect |
| PAIR_SIGNATURE `share_line` | **share_line** |
| SWEET_SPOT_TEMPLATES | **potential** |
| FRICTION_POINT_TEMPLATES | **shadow** |
| A_TO_B_OPENERS / B_TO_A_OPENERS | directional_mechanism |
| TOGETHER_FIELD_TEMPLATES | composite_effect |

### Explainability Panel (mobile)

| Helper | Layer |
|---|---|
| `strengthLabel` | proof (özet) |
| `dignityChip` | proof (dignity) |
| `tensionChips` | proof (aspect count) |
| `lunarPhaseChip` | context |
| Block 1 (why_this_not_that) | rationale |

---

## 20. Versiyon Tarihçesi

| Sürüm | Tarih | Değişiklik |
|---|---|---|
| v1.0 | 2026-04-18 | İlk sürüm. Faz 1+2 canlı yapıyı, share_line playbook'u, explainability panel chip'lerini birleştirdi. |
| **v2.0** | **2026-04-18** | **Major revizyon.** SHOU voice spec v1.2 doktrinini özümsedi. Critical changes: |
| | | — **Sütun 3 revize:** "Teknik terim yasak" → "Spesifik referans kanıt katmanında zorunlu". Co-Star modelinden Chani modeline doğru hareket. |
| | | — **Yeni §5 Katman Sesleri:** cause/mechanism/effect/shadow/potential/past_teaser gramerleri. |
| | | — **Yeni §6 Kontrast Yapısı:** "Dışarıdan X. İçeride Y." codified. |
| | | — **Yeni §7 Highlight Sistemi:** lime/lav/stone anlam kodu. |
| | | — **Yeni §8 Pattern Adlandırma:** 4 adımlı formül — SHOU'nun imza hamlesi. |
| | | — **Yeni §9 Yetenek Formülü:** ad + kanıt + uygulama. |
| | | — **Yeni §10 Cümle Uzunluk Hiyerarşisi:** 3 kademe + uyarı kademeleri. |
| | | — **Yeni §11 Spesifik Referans Doktrini:** orb / ev / stellium / Rx hiyerarşisi. |
| | | — **Ses boyutları §2:** `specificity` dimensionı eklendi. |
| | | — **§15 Yasaklar:** 4 alt kategoriye bölündü (mistik / motivasyon / belirsiz sıfat / gramer). |
| | | — **Ek A:** Spesifik sıfat sözlüğü — Ay / Yükselen / MC × işaret betimlemesi. |
| | | — **Ek B:** Pattern adlandırma starter pack — 20+ ad. |
| | | — **QA checklist §18:** Narrative 9 soru + Pattern 5 soru + Yetenek 3 parça check'leri eklendi. |
| **v2.1** | **2026-04-19** | **Minor revizyon — sistem mimarisi için 6 karar.** Mevcut yapının explicit layer eşleşmesi yapıldı, kod tarafı için altyapı hazırlandı: |
| | | — **Yeni §3.x Ana vs Yardımcı Katmanlar:** 8 ana + 3 yardımcı katman ayrımı. |
| | | — **Yeni §5.8–5.10:** `rationale`, `context`, `caution` yardımcı katmanları tanımlandı (mevcut `why_this_not_that`, `lunar_phase`, `watch_variants` karşılıkları). |
| | | — **§11 Proof Doktrini genişletildi (§11.4–11.9):** İki seviye — `proof_raw` (telgraf) + `proof_line` (insan cümlesi, altyapı hazır, içerik sonra). Title Case kuralı, template redundancy kuralı, accessibility minimum (alpha ≥ 0.60, font ≥ 11px), template kapsamı zorunluluğu (her core thread), TR-only render kuralı. |
| | | — **Yeni §13.4 Profile Detail Flow — Proof Chip:** S1 widget spec'i. |
| | | — **Yeni §14.3 Naming Standardı:** `share_line`, `proof_raw`, `proof_line` standart isimleri; tarihsel isimler alias olarak korunur. |
| | | — **Ek C genişletildi:** Yardımcı layer'lar + proof alanları eklendi. |
| | | — **Yeni Ek D — Mevcut Field → Layer Haritası:** Natal / transit / synastry / explainability pipeline'larında kod alanlarının layer rolleri. |

---

## Son söz

Bu doküman bir **kural kitabı** değil; bir **ses eşiği**. Amacı, Astrologi AI'da her cümlenin aynı sesten çıktığı hissini vermek. Tonu koruyan kural değildir — tonu koruyan, kuralı bilen insandır.

Şüpheli kaldığında: **"Beni anlıyor" mu dedirtiyor?** O soru yanıt vermiyorsa, cümleyi tekrar yaz.

**Ve v2.0'ın ek sorusu:** **Spesifik mi, muğlak mı?** Muğlaksa, sayı veya referans ekleyerek spesifikleştir.
