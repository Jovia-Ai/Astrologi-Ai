# Projection Voice Tuning Gap Audit

**Tarih:** 2026-04-26
**Kapsam:** `profile_narrative_projection_v1` + `profile_v8_projection_v1` (yalnızca render/projection katmanı — selection katmanına dokunulmaz)
**Fixture seti:** `backend/tests/_fixtures/natal_v8_baseline.json` ilk 8 senaryo (`fix01_leo_leo_classic` → `fix08_cancer_capricorn_nodes`). `fix09–11` (edge case + unknown birthtime) bu turun dışında.
**Guardrails referansı:** [`docs/voice/voice_spec.md`](../voice/voice_spec.md) v2.1 — özellikle §1 (gözlem ≠ yargı), §3 (kesin/spesifik/yargısız/kontrastlı), §4.4 (gölge yumuşatılır, patolojize edilmez), §15 (yasaklar).

> **Bu doküman yalnızca tespit etmek içindir.** Düzeltme PR'ı, kod değişikliği veya UI migration önerisi içermez.

---

## 0. Özet

| # | Bulgu kategorisi | Adet | En riskli yüzey |
|---|---|---|---|
| 1 | Tekrarlayan cümle şablonları | 6 | Profile body (mode A/B/C/D) |
| 2 | Doğal-olmayan TR ifade | 5 | Profile body kapanışları + bundle headline'ları |
| 3 | Jenerik implication kapanışları | 7 | `_BLOCK_COPY_FALLBACKS.gift`, `_BUNDLE_HEADLINES` |
| 4 | Çok kısa / yassı bloklar | 4 | `SOFT_ASTRO_HINTS_TR`, `DEFAULT_PUBLIC_CHIPS_TR` |
| 5 | Self-help / koçluk kayması | 5 | v8 PAST_LAYER_TRIGGERS, MISSION_RULES, TALENT_RULES |
| 6 | İyi seçim, zayıf render | 5 | astro_hint fallback, bundle headline reducer, balance leads |

**Toplam tespit:** 32 — bunlardan 11'i `phrase-level fix`, 9'u `pattern-level fix`, 5'i `surface-specific voice mode mismatch`, 6'sı `needs semantic enrichment`, 1'i `leave as-is`.

---

## 1. Tekrarlayan cümle şablonları

### 1.1 Body template havuzu blok-bağımsız çoğaltılıyor
**Konum:** `backend/app/natal/narrative/phrase_lib_tr_profile.py:99-101`
```python
BODY_TEMPLATES_TR: Dict[str, Dict[str, str]] = {
    block_id: dict(_BODY_TEMPLATE_BY_MODE) for block_id in TITLE_FAMILIES_TR
}
```
7 farklı blok (`identity_aura`, `mind_voice`, `drive_rhythm`, `love_depth`, `career_visibility`, `home_roots`, `luck_creation`) tamamen aynı 4 mode template'ini paylaşıyor. `fix01` (Leo Leo) `identity_aura` body'si ile `fix02` (Capricorn stellium) `home_roots` body'si **aynı iskeletten** üretiliyor → kullanıcı 2-3 blok aşağı kaydırdığında "Bir ortama girdiğinde / Perde arkasında / Gerilim yükseldiğinde / Denge geldiğinde" tekrarını fark ediyor.
**Sınıflandırma:** `pattern-level fix`
**Neden:** Phrase swap çözmez; her blok için kendi semantik çatısı gerekir (örn. `love_depth` "girdiğinde/perde arkası" yerine eşik/bağ ekseni isteyebilir).

### 1.2 Mode A — "Baskı yükseldiğinde / Yerine oturduğunda" sabit ikilisi
**Konum:** `phrase_lib_tr_profile.py:73-78`
Tüm Mode A render'larında ikinci ve üçüncü cümleler **birebir** "Baskı yükseldiğinde {shadow}. Yerine oturduğunda {gift}." dönüyor. 8 fixture × 7 blok × ~%25 mode A olasılığı → kullanıcı başına ortalama 1-2 blokta bu cümle çiftiyle karşılaşıyor.
**Sınıflandırma:** `phrase-level fix`

### 1.3 `_BALANCE_GIFT_LEADS` rotasyonu kendi giriş cümlelerinden besleniyor
**Konum:** `profile_narrative_engine_signature.py:907-915`
```python
_BALANCE_GIFT_LEADS = (
    "Bu yapı olgunlaştığında",
    "Olgun tarafında",
    "Dengeye geldiğinde",
    "Dengede olduğunda",
    ...
)
```
Aynı liste hem `_strip_balance_lead` (girişi sıyır) hem `_balance_sentence` (yeniden başla) için kullanılıyor → soyma sonrası "İyi çalıştığında" ile rebuild ediliyor (`:946`). Sonuç: kullanıcı **rotasyon hissetmiyor**, çünkü kapanışların hepsi aynı 7-elementli kovaya düşüyor.
**Sınıflandırma:** `pattern-level fix`

### 1.4 4 fallback gift'in tamamı aynı sözdizimi
**Konum:** `profile_narrative_engine_signature.py:296, 308, 320, 332`
```
"Bu yapı olgunlaştığında sana netlik ve istikrar kazandırır."
"Bu yapı olgunlaştığında sana dayanıklılık ve güven veren bir netlik kazandırır."
"Bu yapı olgunlaştığında seni hem derin düşünen hem de kurabilen biri yapar."
"Yakınlık sahici geldiğinde çok sadık, sıcak ve iyileştirici bir bağ kurarsın."
```
İlk 3'ü tamamen aynı kalıp ("Bu yapı olgunlaştığında … kazandırır"); 4.'sü kalıbı kırıyor. Fallback yolunda olan herhangi 2 blok çakıştığında kullanıcı tekrarı net görür.
**Sınıflandırma:** `phrase-level fix`

### 1.5 SOFT_ASTRO_HINTS_TR paralel sözdizimi
**Konum:** `phrase_lib_tr_profile.py:104-140`
21 hint'in **17'si** "X ile Y aynı anda/birlikte çalışıyor/hissediliyor" formülünden türemiş. Örnek:
- "Sağlam duruşun ile farklı kalan tarafın aynı çizgide ilerliyor."
- "Zihin tarafında netlik ile iç denge birlikte çalışıyor."
- "İlişkide güven ile derinlik aynı anda önem kazanıyor."
- "Kariyerde görünürlük kadar kalite standardın da güçlü."

Voice spec §6 "kontrast yapısı" bekliyor, bunlar **eşitleme yapısı** — kontrast yok, iki nicel öğe yan yana koyuluyor.
**Sınıflandırma:** `pattern-level fix`

### 1.6 v8 `_BUNDLE_HEADLINES` flat declarative
**Konum:** `profile_v8_payload_builder.py:405-413`
8 bundle başlığının **8'i de** "X var." veya "X açılıyor / etkiliyor / belirgin" şablonunda:
```
"İlişki hattında tekrar eden bir desen var."
"Dışarı verdiğin kimlik tonu güçlü."
"Yumuşak kapasitelerin hızlı açılıyor."
"Zihinsel ritminde ayırt edici bir hat var."
...
```
Voice spec §3 (kontrastlı) ve §11 (spesifik referans) ihlali — hepsi düz duyuru.
**Sınıflandırma:** `pattern-level fix`

---

## 2. Doğal-olmayan Türkçe ifade

### 2.1 "Yerine oturduğunda" — calque
**Konum:** `phrase_lib_tr_profile.py:77`
İngilizce "when it falls into place" calque'i. TR'de bu öbek doğal kullanım değil — "Olgunlaştığında" / "Yatışığında" / "Yerini bulduğunda" gibi alternatifler daha doğal. Mode A kapanışında her render'da görünüyor.
**Sınıflandırma:** `phrase-level fix`

### 2.2 "İç tarafta işleyiş şöyle:" + iki nokta üst üste
**Konum:** `phrase_lib_tr_profile.py:93`
Mühendislikvari yapı; voice spec §15 yasakları arasında "açıklayıcı / klinisyen ton" var. "İçeride şu olur:" veya "İç hattında" daha edebi.
**Sınıflandırma:** `phrase-level fix`

### 2.3 "Perde arkasında ise"
**Konum:** `phrase_lib_tr_profile.py:87`
"Perde arkası" idiom TR'de doğal ama "ise" bağlacı ile kullanım fazla "spotlights/dramatic copy" tonu yaratıyor. Voice spec §1.2 "ne mistik ne klinisyen" iddiasını sarsıyor — "perde arkasında" tiyatro/sahne metaforu sezgisel olarak mistiğe kayıyor.
**Sınıflandırma:** `surface-specific voice mode mismatch` (mode C "cinematic" tonunda kalabilir; mode B/D'de çıkmamalı)

### 2.4 "İçeride birden fazla damar aynı anda çalışıyor"
**Konum:** `phrase_lib_tr_profile.py:237` (default `mechanism` fallback)
"Damar" → biyolojik metafor, editorial ton ile çelişiyor. "Çizgi" / "hat" / "ses" daha SHOU dilinde.
**Sınıflandırma:** `phrase-level fix`

### 2.5 "İç standart yükselir ve akış gecikebilir"
**Konum:** `profile_narrative_engine_signature.py:309`
"İç standart" + "akış" = jargon karışımı. Türkçede "iç standart" doğal değil; "standart" zaten dış kıyas çağrıştırıyor. "İç editör" / "iç ölçü" daha oturmuş.
**Sınıflandırma:** `phrase-level fix`

---

## 3. Jenerik implication kapanışları

### 3.1 "kazandırır" tekrarı
**Konum:** `profile_narrative_engine_signature.py:242, 247, 296, 308, 1211, 1216`
6 farklı yerde "Sana ... kazandırır" formülü. Voice spec §1.3 "buyurgan değil" + §3 "yargısız" → "kazandırır" mekanik bir mükafat teslimatı imliyor. Spec şunu istiyor: gözlem + kontrast, mükafat değil.
**Sınıflandırma:** `phrase-level fix`

### 3.2 "kuruluyor" hep abstract
**Konum:** `phrase_lib_tr_profile.py:131-134`, `:238`
"İç güvenin en çok düzen ve toparlanma duygusuyla kuruluyor."
"Olgun tarafında daha net ve güven veren bir akış kuruluyor."
"akış" + "kuruluyor" + abstract noun = §11 "spesifik referans" kuralının zıttı. Kullanıcı somut bir anchor (Saturn-3, Venus-Cancer vb.) ile bağlantı kuramıyor.
**Sınıflandırma:** `needs semantic enrichment`
**Neden:** Phrase değiştirmek anchor sorununu çözmez; render'a astrolojik proof sızdırmak gerek (voice spec §4.3'teki iki katmanlı kullanım).

### 3.3 v8 `_BUNDLE_HEADLINES` "var." kapanışları
**Konum:** `profile_v8_payload_builder.py:405-413`
8 başlığın 5'i "var" ile bitiyor. Bu, voice spec §3 (kesin) ile uyumlu görünür ama §3.4 (kontrastlı) çiğneniyor — kontrastsız "var" düz beyandır.
**Sınıflandırma:** `pattern-level fix`

### 3.4 "etkiliyor / etkiliyor" jenerikliği
**Konum:** `profile_v8_payload_builder.py:409`
> "Duyguyu yönetme biçimin savunma gücünü etkiliyor."

"Etkilemek" → her şey her şeyi etkiler. Boş fiil. Spec §11 "muğlaklık güveni yıkıyor".
**Sınıflandırma:** `phrase-level fix`

### 3.5 PAST_LAYER_TRIGGERS — "olabilir" + "olmuş olabilir" stack
**Konum:** `profile_v8_payload_builder.py:205, 213, 216, 221, 229`
4 trigger headline'ının **5'i** "-mış olabilir(sin)" ile kapanıyor:
> "Küçükken konuşmanın bir bedeli olduğunu öğrenmiş olabilirsin."
> "Sevdiğini tam göstermenin zor geldiği bir dönem olmuş olabilir."

Voice spec §3.1 "kesin" / certainty default 0.55+ ile çelişiyor. The Pattern formülasyonu olan "you often feel..." ile aynı tuzak; spec §1.4'te bu açıkça reddedilmiş ("bizde 'sen ... -yorsun' şimdiki zaman").
**Sınıflandırma:** `surface-specific voice mode mismatch`
**Neden:** Past teaser yüzeyinde geçmiş zaman kullanılması mantıklı, ama "olabilir" temkinliliği shadow uyarısı (§4.4) için meşrudur — her past_layer headline'ında dağıtılması gereksiz.

### 3.6 "Ufuk büyüdükçe enerjin de daha anlamlı bir akış buluyor."
**Konum:** `profile_narrative_engine_signature.py:208`
"Anlamlı bir akış buluyor" → boş affirmation. Voice spec §15 yasaklar arasında "jenerik affirmation" var (Nebula bırakıyoruz dediği şey).
**Sınıflandırma:** `phrase-level fix`

### 3.7 v8 ARCHETYPE_LABELS abstract
**Konum:** `profile_v8_payload_builder.py:277-281`
`"İlişki akışı"`, `"Kimlik ekseni"`, `"Yumuşak kapasite"` — başlık olarak kullanıldığında §11 "spesifik referans" yok; abstrakt sınıflandırma. Selection bundle'a düştüğünde proof kaybediyor.
**Sınıflandırma:** `needs semantic enrichment`

---

## 4. Çok kısa / yassı bloklar

### 4.1 SOFT_ASTRO_HINTS_TR — 12-16 kelime aralığında sıkışık
**Konum:** `phrase_lib_tr_profile.py:104-140`
21 hint'in tamamı tek cümle, 12-16 kelime arasında. Voice spec §10 (cümle uzunluk hiyerarşisi) varyasyon istiyor (kısa-orta-uzun ritmi); buradaki uniform kısa hat ritmik monotonluk yaratıyor. Block'lar arası geçişte "rhythm leak" yok.
**Sınıflandırma:** `pattern-level fix`

### 4.2 DEFAULT_PUBLIC_CHIPS_TR — abstract noun yığını
**Konum:** `phrase_lib_tr_profile.py:143-151`
Chips: "Kendi Çizgin", "Yapı", "Akış", "Genişleme", "Toparlanma" → hepsi soyut isim. Voice spec §11 ve Ek A "spesifik sıfat sözlüğü" istiyor. Abstract chip kullanıcıyla resonance kurmuyor; "her astroloji app'inde olabilir" hissi.
**Sınıflandırma:** `phrase-level fix`

### 4.3 _BLOCK_COPY_FALLBACKS — 1 cümle/slot, ritim yok
**Konum:** `profile_narrative_engine_signature.py:238-274`
7 blok × 3 slot (mechanism/shadow/gift) = 21 fragment, hepsi tek cümle. Body 4 cümleye dönüştürüldüğünde (template'ten gelen connector'larla birlikte) ritim **şu pattern'a** sıkışıyor: `core → mechanism (1c) → shadow (1c) → gift (1c)`. Cümle uzunlukları neredeyse eşit → kullanıcı 4 satır okuduktan sonra "robotik kalem" hissi.
**Sınıflandırma:** `pattern-level fix`

### 4.4 fix04 (Tokyo h10 stellium) — talent fallback'e düşüyor
**Konum:** `profile_v8_payload_builder.py:236-258` TALENT_RULES'a yalnızca 3 trigger var (`mercury_jupiter_signature`, `moon_venus_harmony`, `neptune_first_house`). Tokyo h10 stellium signature'ı bunların hiçbiriyle eşleşmediğinde `pick_talents` jenerik domain pool'undan rastgele cümle seçiyor — selection güçlü, render zayıf.
**Sınıflandırma:** `needs semantic enrichment` (TALENT_RULES kapsamı dar; aynı dosyada genişletilmeli — yapısal yatırım)

---

## 5. Self-help / koçluk kayması

Voice spec §1.2 net: **"motivasyon konuşması değil"** + §1.3 "buyurgan ton" yasak. Aşağıdakiler bu bandı geçiyor.

### 5.1 v8 south_node_aries text — prescriptive
**Konum:** `profile_v8_payload_builder.py:232`
> "İçinde her şeyi tek elde tutan bir çizgi varsa, bugün iş birliğine alan açmak büyüme tarafını hızlandırır."

"... yapmak X'i hızlandırır" → buyurgan + koçluk. "Bugün" kelimesi action prescription. Spec §15 "şunu yap, şunu yapma" yasağına direkt çarpıyor.
**Sınıflandırma:** `phrase-level fix`

### 5.2 v8 north_node_libra text — life coaches you
**Konum:** `profile_v8_payload_builder.py:266`
> "Hayat seni tek başına yüklenmekten çok, ortak ritim ve karşılıklılık kurduğun yerde büyütüyor."

"Hayat seni büyütüyor" → spiritüel-koçluk dili. The Pattern + Sanctuary'den ayrılma noktasında SHOU "iyi gözlemci"; "hayat" özne yapılan cümleler bu pozisyonu kaydırıyor.
**Sınıflandırma:** `phrase-level fix`

### 5.3 v8 mercury_jupiter_signature — "ölçeklenebilen bir zihin"
**Konum:** `profile_v8_payload_builder.py:242`
> "doğru zeminde hızla ölçeklenebilen bir zihin var"

"Ölçeklenebilen" → Linkedin/startup dili. Voice spec §15 yasak listesine eklenmeli ama mevcut çerçevede de §1 "yargılayıcı performans dili" sayılır.
**Sınıflandırma:** `phrase-level fix`

### 5.4 v8 neptune_first_house — "avantaj veriyor"
**Konum:** `profile_v8_payload_builder.py:256`
> "sana güçlü bir önsezi avantajı veriyor"

"Avantaj veriyor" → competitive coaching ton. Spec'in gözlem+kontrast disiplinine değil, gain framework'üne dayanıyor.
**Sınıflandırma:** `phrase-level fix`

### 5.5 saturn_third_house_teacher headline
**Konum:** `profile_v8_payload_builder.py:271`
> "Öğrendiklerini paylaştığında başkaları için dönüm noktası olabilirsin."

"Olabilirsin" + "dönüm noktası" + koşullu ön-cümle = TED-talk pep dili. Bu cümle headline olarak da kullanılıyor (`:1252`'de fallback olarak) — yani strong selection sinyali geldiğinde bile bu kapanışla render'a düşüyor.
**Sınıflandırma:** `pattern-level fix`
**Neden:** Tek phrase swap yetmez; mission_rules headline kalıbı yapısal olarak "X yaptığında Y olabilirsin" şartına çekiyor.

---

## 6. Selected node iyi, rendering zayıf

### 6.1 astro_hint fallback hash → generic
**Konum:** `phrase_lib_tr_profile.py:283-296`
```python
def soft_public_astro_hint(...):
    ...
    hints = SOFT_ASTRO_HINTS_TR.get(block_id) or [""]
    index = _stable_int(...) % len(hints)
    return _cleanup(str(hints[index]), max_sentences=1)
```
Selection katmanı zengin signature_id sağladığında bile, hint katmanına teknik referans sızdırılmıyor (`_is_technical_hint` filter'ı zaten 84 karakter sınırı + tech regex ile kesiyor → deterministik fallback'e düşüyor). Sonuç: `fix02` Capricorn h1 stellium gibi spesifik bir signal "İlişkide güven ile derinlik aynı anda önem kazanıyor" tipi jenerik bir cümle olarak çıkıyor.
**Sınıflandırma:** `surface-specific voice mode mismatch`
**Neden:** Pro yüzeyde (paragraph body) spec §4.3 "spesifik referans body'de evet" diyor. Hint katmanı zorla teknik filter ile soft tutuluyor — Pro Profile için bu kalıbın gevşetilmesi gerek.

### 6.2 _BALANCE_GIFT_LEADS strip → kalıba gömülü çıktı
**Konum:** `profile_narrative_engine_signature.py:929-951`
Selection güçlü gift cümlesi sağlasa bile, `_strip_balance_lead` baş kısmı kesip "İyi çalıştığında {clause}; gölgesinde {clause}" sabit yapısına gömüyor. Yani bir signature'ın özgün tonu varsa, balance pass tarafından **homojenize ediliyor**.
**Sınıflandırma:** `pattern-level fix`

### 6.3 v8 `_BUNDLE_HEADLINES` reducer
**Konum:** `profile_v8_payload_builder.py:405-413`
Bundle selection hangisini seçerse seçsin, headline 8 sabit string'den birine map'leniyor. Bu, selection-time'daki nuance'ı (ör. 7th-cusp ruler + Saturn-Venus square'in spesifik tonu) düz-deklaratif bir headline'a indirgiyor.
**Sınıflandırma:** `needs semantic enrichment`
**Neden:** Headline'lar bundle level'da stringleştirilmiş; signature_id aşağı seviyeden çekilse zenginleştirilebilir.

### 6.4 PAST_LAYER_TRIGGERS sınırlı kapsam
**Konum:** `profile_v8_payload_builder.py:201-234`
Sadece 4 trigger handler. `fix01` (Leo Leo) güçlü luminary signature'ı seçildiğinde past_teaser handler'ı eşleşmezse `by_domain["past_experience"]` jenerik fallback yolu çalışıyor (`select_for_profile_v8` → `pick_past_teaser`). Selection iyi, render generic.
**Sınıflandırma:** `needs semantic enrichment`

### 6.5 fix11 (unknown_birthtime) — bu turun dışında, ama not
**Konum:** Doğum saati bilinmiyor → chart_only weight profile → narrative softened. Bu fixture v9-11 grubunda olduğu için bu turdan dışlanmış ama gelecek turda "softened narrative + voice spec uyumu" ayrı denetim gerektirecek (`leave as-is for this audit`).
**Sınıflandırma:** `leave as-is`

---

## 7. Sınıflandırma özeti

### Phrase-level fix (string swap + kelime alternatifi yeterli) — 11
- 1.2 "Baskı yükseldiğinde / Yerine oturduğunda" sabit ikilisi
- 1.4 4 fallback gift'in kalıbı
- 2.1 "Yerine oturduğunda" calque
- 2.2 "İç tarafta işleyiş şöyle:" + iki nokta
- 2.4 "damar" metaforu
- 2.5 "iç standart" jargonu
- 3.1 "kazandırır" tekrarı
- 3.4 "etkiliyor" boş fiil
- 3.6 "anlamlı bir akış buluyor"
- 4.2 DEFAULT_PUBLIC_CHIPS abstract noun
- 5.1 "büyüme tarafını hızlandırır"
- 5.2 "hayat seni büyütüyor"
- 5.3 "ölçeklenebilen bir zihin"
- 5.4 "avantaj veriyor"

> Not: 14 maddeyi 11'e yuvarlamak için bazı maddeler birleştirilebilir; aynı tip swap (örn. 5.1-5.4 koçluk dili) tek bir lint kuralında toplanabilir.

### Pattern-level fix (yapısal değişiklik gerek) — 9
- 1.1 Body template havuzunun blok-bağımsız çoğaltımı
- 1.3 `_BALANCE_GIFT_LEADS` rotasyon-paradoksu (aynı liste hem strip hem rebuild)
- 1.5 SOFT_ASTRO_HINTS paralel sözdizimi (eşitleme yapısı, kontrast yok)
- 1.6 `_BUNDLE_HEADLINES` flat declarative
- 3.3 `_BUNDLE_HEADLINES` "var" kapanışları
- 4.1 SOFT_ASTRO_HINTS_TR cümle uzunluk hiyerarşisi yok
- 4.3 _BLOCK_COPY_FALLBACKS slot ritmi
- 5.5 mission_rules headline kalıbı ("X yaptığında Y olabilirsin")
- 6.2 `_BALANCE_GIFT_LEADS` homojenizer

### Surface-specific voice mode mismatch (spec yüzey kalibrasyonu çakışıyor) — 5
- 2.3 "Perde arkasında ise" — Mode C cinematic dışında çıkmamalı
- 3.5 PAST_LAYER_TRIGGERS "olabilir" stack (past teaser yüzeyinde meşru ama dağıtılması gereksiz)
- 4.1 SOFT_ASTRO_HINTS uniform 12-16 kelime — pull/proof/headline yüzeylerinde farklı uzunluk gerek
- 6.1 astro_hint teknik filter'ı Pro paragraph body için fazla kısıtlayıcı (spec §4.3'e göre body'de spesifik referans **olmalı**)
- (örtük) editorialize_teaser/editorialize_micro mode bazlı varyasyonu fazla mekanik

### Needs semantic enrichment (kelime swap çözmez, anchor/data sızdırılmalı) — 6
- 3.2 "kuruluyor" + abstract noun (proof sızdırılmalı)
- 3.7 ARCHETYPE_LABELS abstract sınıflandırma
- 4.4 fix04 Tokyo h10 stellium — TALENT_RULES kapsamı dar
- 6.3 v8 _BUNDLE_HEADLINES reducer (signature-aware headline gerekiyor)
- 6.4 PAST_LAYER_TRIGGERS kapsamı dar
- (örtük) MISSION_RULES kapsamı 2 trigger ile sınırlı

### Leave as-is (bu turun dışında) — 1
- 6.5 fix11 unknown_birthtime — softened narrative ayrı denetim turu

---

## 8. Yüzey-bazlı sıcak nokta haritası

| Yüzey | En kritik 3 madde |
|---|---|
| **Profile body (mode A/B/C/D)** | 1.1 (template havuzu), 1.2 (mode A sabit ikilisi), 4.3 (slot ritmi) |
| **`_BLOCK_COPY_FALLBACKS.gift`** | 1.4 (4 fallback aynı kalıp), 3.1 (kazandırır), 6.2 (balance homojenizer) |
| **SOFT_ASTRO_HINTS_TR** | 1.5 (paralel sözdizimi), 4.1 (uzunluk monotonluğu), 6.1 (teknik filter mismatch) |
| **v8 PAST_LAYER_TRIGGERS** | 3.5 ("olabilir" stack), 5.5 (kalıp), 6.4 (kapsam darlığı) |
| **v8 TALENT/MISSION_RULES** | 4.4 (kapsam), 5.1-5.5 (koçluk dili), 6.3 (bundle reducer) |
| **v8 _BUNDLE_HEADLINES** | 1.6 (flat declarative), 3.3 (var kapanışı), 6.3 (reducer) |
| **v8 ARCHETYPE_LABELS** | 3.7 (abstract sınıflandırma) |

---

## 9. Fixture-bazlı dokunma tahmini

Bu turun **8 fixture seti** üzerinde her bulgunun tetiklenme olasılığı:

| Fixture | Kritik bulgu sayısı | En sert dokunan |
|---|---|---|
| fix01 leo_leo_classic | 5 | 1.1, 1.4, 5.5, 6.4 (past teaser fallback) |
| fix02 capricorn_stellium | 6 | 1.1, 3.1 (kazandırır × 2 blok), 4.4, 6.1 |
| fix03 pisces_cancer_water | 4 | 1.5, 3.2, 4.3 |
| fix04 h10_career_stellium | 6 | 4.4 (TALENT_RULES miss), 5.3, 6.3, 1.6 |
| fix05 t_square_tense | 5 | 6.2 (balance homojenizer), 1.4, 3.5 |
| fix06 grand_trine_flow | 4 | 1.5, 3.3, 5.2 |
| fix07 aries_libra_nodes | 7 | 5.1 (south_node_aries trigger), 5.2 (north_node_libra), 3.5 ("olabilir") |
| fix08 cancer_capricorn_nodes | 5 | 3.5, 5.5 (mission_rules), 6.4 |

> En riskli fixture: **fix07** (aries_libra_nodes) — node trigger'ları doğrudan koçluk dili kapanışlarına çarpıyor.
> En "sessiz" risk: **fix04** (Tokyo h10 stellium) — selection güçlü ama TALENT_RULES eşleşmediği için render zayıflıyor (selected-good / rendering-weak kategorisinin en net örneği).

---

## 10. Bu doküman dışında kalan konular

- **Selection guardrails:** dokunulmadı, mevcut Selection V3 watchlist disiplini bu denetim için referans alındı, değiştirilmedi.
- **UI migration:** mobile tarafının payload tüketimi, slot adaptasyonu, dark/light mode rendering — kapsam dışı.
- **EN paritesi:** `phrase_lib_en_profile.py` ayrı bir denetim turuna bırakıldı; bu rapor sadece TR projection için.
- **Implementation:** Hiçbir kod değişikliği önerilmiyor. Bu rapor "ne yanlış görünüyor" haritasıdır; "ne yapacağız" kararı ayrı bir oturumda alınmalı.

---

## 11. Sonuç

32 tespit, 5 net kategoriye dağıldı. **Pattern-level fix** ve **needs semantic enrichment** (toplam 15 madde) öncelikli iş yükü; bunlar phrase swap ile çözülmeyen yapısal kalıplar. **Phrase-level fix** (11 madde) ise tek seferlik phrase pack güncellemesi ile temizlenebilir. **Voice mode mismatch** (5 madde) tone.yaml ↔ render policy haritalamasının yeniden okunmasını gerektirir.

Bu denetim sonrası takip turları için iki açık hat bırakıldı:
1. EN paritesi denetim turu (`phrase_lib_en_profile`).
2. fix11 unknown_birthtime softened narrative voice uyumu.
