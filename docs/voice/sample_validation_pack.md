# SHOU Voice vNext — Sample Validation Pack

Bu dosya `backend/scripts/generate_validation_samples.py` tarafından doldurulur.
Blind test insan moderasyonuyla yürür; event card bu pack'in dışında tutulur.

## Validation Readiness

- `validation_ready`: `True`
- `period_only_validation_ready`: `True`
- `usable_period_charts`: `5`
- `usable_daily_charts`: `5`
- `usable_natal_sanity_charts`: `3`
- `daily_validation_deferred`: `True`

Daily blind test bu turda reviewer pack'e dahil değildir; daily renderer guardrail injection ayrı cycle'da kapanacaktır.

Bu pack reviewer'a period-only validation için gönderilebilir. Daily diagnosis JSON artefaktında tutulur.

## Runbook

```bash
PYTHONPATH=backend backend/venv/bin/python backend/scripts/generate_validation_samples.py
```

Not: Script canlı transit generation yapabiliyorsa pack'i doldurur. Swiss ephemeris veya runtime bağımlılıkları yoksa ilgili chart satırı `unavailable` olarak işaretlenir.

Validation sonuçlarını tamamlandıktan sonra `docs/voice/validation_results_2026_05_xx.md` dosyasına kaydedin.

## Variant Contract

Bu mapping facilitator içindir; reviewer'a gösterilmez.

- Period: `A legacy`, `B canonical spine + voice policy`, `C canonical + manifestation context`
- Daily: `A legacy`, `B TodayStoryCandidate + current daily_synthesis`, `C mock today_delta_signal + scene-aware daily`
- Natal: `sanity review only`
- Natal sanity surface `legacy_compat` olarak değerlendirilir; vNext lint gate'inden muaf, ama quality flag taşır.

## Blind Protocol

- Reviewer A/B/C semantic mapping'i görmez.
- Chart başına A/B/C sırası deterministic seed ile karıştırılır.
- Answer key yalnız `docs/voice/sample_validation_samples.json` içinde tutulur.

## Rating Scale

Per-variant `1–5` numeric rating fields:

- `seen_score`
- `generic_score`
- `too_technical_score`
- `coaching_motivation_score`
- `reread_score`
- `repetition_score`

Chart-level choice fields:

- `best_overall`: `A | B | C`
- `worst_overall`: `A | B | C`

Skor yönü:

- `seen_score`, `reread_score`: yüksek daha iyi
- `generic_score`, `too_technical_score`, `coaching_motivation_score`, `repetition_score`: düşük daha iyi

Not: `best_overall` ve `worst_overall` numeric skor değil; chart-level seçim alanıdır.

## Minimum Sample / Reviewer Count

- Minimum reviewer: `5`
- Minimum usable period charts: `4`
- Minimum usable daily charts: `4` (`full validation` için; bu tur reviewer pack'ine dahil değil)
- Minimum usable natal sanity charts: `3`

## Decision Thresholds

- Period `B/C wins` if average `seen_score` beats `A` by at least `0.7` and `generic_score` is lower.
- Secondary win rule: `B/C` wins `best_overall` in at least `60%` of reviews.
- If Daily `B/C` does not beat `A`, mark this as evidence for `PR-5 Daily Today-ness Signal`.
- Bu reviewer pack şu an yalnız period + natal sanity için kullanılacaktır.

Reviewer-facing `A/B/C` label chart başına randomize edilebilir. Source variant çözümü için `docs/voice/sample_validation_samples.json` kullanılır.

## PR-2v.1 Period Blind Test

### Oğlak/Oğlak — 1. ev stellium (4+ gezegen)

- `fixture_id`: `fix02_capricorn_stellium`
- `window`: `2026-05-01 -> 2026-05-31`
- `selected_date`: `2026-05-03`
#### Variant A

**Başlık:** Zihinsel Otoriteni İnşa Ediyorsun

Anlam ve yön hattı bu dönemde özellikle belirginleşiyor. Bu dönem asıl omurga yavaş ama kalıcı biçimde kuruluyor. Hayatının bir alanı daha görünür hale geliyor; senden daha bilinçli seçimler istiyor.

Bu, kendini zorlamak değil. Özellikle yakın çevrendeki ses tarafında büyüyen şeyi hemen sonuca çevirmek de değil.

Sende zaten çalışan birkaç ayrı taraf var. Şu sıralar onlar birbirine daha yakın duruyor. Bu tema yakın çevrendeki ses içinden büyüyor; küçük cümleler bile alttaki daha büyük meseleyi görünür kılabilir.

Asıl ayrım, yakın çevrendeki ses içinden yükselen şeyi hemen sonuca çevirmemek.

Score sheet:

| seen_score | generic_score | too_technical_score | coaching_motivation_score | reread_score | repetition_score |
|---|---|---|---|---|---|
|   |   |   |   |   |   |

#### Variant B

**Başlık:** Zihinsel Otoriteni İnşa Ediyorsun

Hayatının bir alanı daha görünür hale geliyor; senden daha bilinçli seçimler istiyor.

Mesele sadece bir konunun açılması değil; ona nasıl yaklaştığının değişmesi.

Etki önce gündelik hayatta görünür oluyor, sonra bunun sonucu daha kalıcı bir davranış değişimine dönüşüyor.

Risk, ilk hissi sonuç sanıp süreci aceleye getirmek.

Score sheet:

| seen_score | generic_score | too_technical_score | coaching_motivation_score | reread_score | repetition_score |
|---|---|---|---|---|---|
|   |   |   |   |   |   |

#### Variant C

**Başlık:** Zihinsel Otoriteni İnşa Ediyorsun

Anlam ve yön hattı bu dönemde özellikle belirginleşiyor. Bu dönem asıl omurga yavaş ama kalıcı biçimde kuruluyor. Hayatının bir alanı daha görünür hale geliyor; senden daha bilinçli seçimler istiyor.

Bu, kendini zorlamak değil.

Sende zaten çalışan birkaç ayrı taraf var. Şu sıralar onlar birbirine daha yakın duruyor.

Bu, savunmayı çözmek değil.

Score sheet:

| seen_score | generic_score | too_technical_score | coaching_motivation_score | reread_score | repetition_score |
|---|---|---|---|---|---|
|   |   |   |   |   |   |

**Sorular**

1. Hangisi daha "beni görüyor" hissi veriyor?
2. Hangisi generic horoscope gibi?
3. Hangisi fazla teknik?
4. Hangisi fazla koçluk/motivasyon gibi?
5. Hangisini tekrar okumak isterdin?
6. Hangisinde cümleler birbirine benziyor?

- `best_overall`: 
- `worst_overall`: 

### Balık güneş + Yengeç yükselen — su ağırlık

- `fixture_id`: `fix03_pisces_cancer_water`
- `window`: `2026-05-01 -> 2026-05-31`
- `selected_date`: `2026-05-03`
#### Variant A

**Başlık:** Denge ve Yapı Teması Derinleşiyor

Yakınlık ve güven hattı bu dönemde özellikle belirginleşiyor. Bu dönem asıl omurga yavaş ama kalıcı biçimde kuruluyor. Mesele çok insan değil; doğru çevre, doğru hedef ve doğru ortaklık.

Konu daha sert olmak değil; yakınlıkla mesafeyi aynı cümlede tutacak ayarı bulmak.

İlişkilerde sınır daha belirgin hale geliyor. Açılmak istediğin yerle kendini koruduğun yer aynı anda görünür oluyor.

İki uçtan birine gitmek gerekmiyor; küçük ayar bu temayı daha doğru taşır.

Score sheet:

| seen_score | generic_score | too_technical_score | coaching_motivation_score | reread_score | repetition_score |
|---|---|---|---|---|---|
|   |   |   |   |   |   |

#### Variant B

**Başlık:** Denge ve Yapı Teması Derinleşiyor

Mesele çok insan değil; doğru çevre, doğru hedef ve doğru ortaklık.

İçeride değişen güç algın, dışarıda hangi çevrede yer almak istediğini de yeniden tanımlıyor.

Önce içeride eleme oluyor, sonra dışarıda çevre ve hedef kendini yeniden sıralıyor.

Risk, seçiciliği soğukluk ya da kontrol etme ihtiyacına çevirmek.

Score sheet:

| seen_score | generic_score | too_technical_score | coaching_motivation_score | reread_score | repetition_score |
|---|---|---|---|---|---|
|   |   |   |   |   |   |

#### Variant C

**Başlık:** Denge ve Yapı Teması Derinleşiyor

Yakınlık ve güven hattı bu dönemde özellikle belirginleşiyor. Bu dönem asıl omurga yavaş ama kalıcı biçimde kuruluyor. Mesele çok insan değil; doğru çevre, doğru hedef ve doğru ortaklık.

Konu daha sert olmak değil; özellikle kendini başlatma biçimin tarafında yakınlıkla mesafeyi aynı cümlede tutacak ayarı bulmak.

İlişkilerde sınır daha belirgin hale geliyor. Açılmak istediğin yerle kendini koruduğun yer aynı anda görünür oluyor. Bu tema daha çok kendini başlatma biçimin içinden görünür oluyor.

Asıl ayar, kendini başlatma biçimin tarafında neyi açıp neyi biraz geride tuttuğunu daha bilinçli seçmek.

Score sheet:

| seen_score | generic_score | too_technical_score | coaching_motivation_score | reread_score | repetition_score |
|---|---|---|---|---|---|
|   |   |   |   |   |   |

**Sorular**

1. Hangisi daha "beni görüyor" hissi veriyor?
2. Hangisi generic horoscope gibi?
3. Hangisi fazla teknik?
4. Hangisi fazla koçluk/motivasyon gibi?
5. Hangisini tekrar okumak isterdin?
6. Hangisinde cümleler birbirine benziyor?

- `best_overall`: 
- `worst_overall`: 

### 10. ev stellium — kariyer/visibility ağırlığı

- `fixture_id`: `fix04_h10_career_stellium`
- `window`: `2026-05-01 -> 2026-05-31`
- `selected_date`: `2026-05-03`
#### Variant A

**Başlık:** İlişki Dengesini Yeniden Kuruyorsun

Yakınlık ve güven hattı bu dönemde özellikle belirginleşiyor. Görünürlük kazanan çizgi bu kez tam bu hatta toplanıyor. Hayatının bir alanı daha görünür hale geliyor; senden daha bilinçli seçimler istiyor.

Bu, kendini zorlamak değil.

Yakın olduğun yerlerde daha çok kendin oluyorsun. Birinin yanında durmak ya da durmamak eskisi kadar yarım his bırakmıyor.

Bu, savunmayı çözmek değil.

Score sheet:

| seen_score | generic_score | too_technical_score | coaching_motivation_score | reread_score | repetition_score |
|---|---|---|---|---|---|
|   |   |   |   |   |   |

#### Variant B

**Başlık:** İlişki Dengesini Yeniden Kuruyorsun

Yakınlık ve güven hattı bu dönemde özellikle belirginleşiyor. Görünürlük kazanan çizgi bu kez tam bu hatta toplanıyor. Hayatının bir alanı daha görünür hale geliyor; senden daha bilinçli seçimler istiyor.

Bu, kendini zorlamak değil. Özellikle anlaşma yapma biçimin tarafında büyüyen şeyi hemen sonuca çevirmek de değil.

Yakın olduğun yerlerde daha çok kendin oluyorsun. Birinin yanında durmak ya da durmamak eskisi kadar yarım his bırakmıyor. Bu tema daha çok anlaşma yapma biçimin içinden görünür oluyor.

Bu, savunmayı çözmek değil.

Score sheet:

| seen_score | generic_score | too_technical_score | coaching_motivation_score | reread_score | repetition_score |
|---|---|---|---|---|---|
|   |   |   |   |   |   |

#### Variant C

**Başlık:** İlişki Dengesini Yeniden Kuruyorsun

Hayatının bir alanı daha görünür hale geliyor; senden daha bilinçli seçimler istiyor.

Mesele sadece bir konunun açılması değil; ona nasıl yaklaştığının değişmesi.

Etki önce gündelik hayatta görünür oluyor, sonra bunun sonucu daha kalıcı bir davranış değişimine dönüşüyor.

Risk, ilk hissi sonuç sanıp süreci aceleye getirmek.

Score sheet:

| seen_score | generic_score | too_technical_score | coaching_motivation_score | reread_score | repetition_score |
|---|---|---|---|---|---|
|   |   |   |   |   |   |

**Sorular**

1. Hangisi daha "beni görüyor" hissi veriyor?
2. Hangisi generic horoscope gibi?
3. Hangisi fazla teknik?
4. Hangisi fazla koçluk/motivasyon gibi?
5. Hangisini tekrar okumak isterdin?
6. Hangisinde cümleler birbirine benziyor?

- `best_overall`: 
- `worst_overall`: 

### T-square paterni — gerilim odaklı

- `fixture_id`: `fix05_t_square_tense`
- `window`: `2026-05-01 -> 2026-05-31`
- `selected_date`: `2026-05-03`
#### Variant A

**Başlık:** Denge ve Yapı Teması Derinleşiyor

Bu dönem ilişkilerde yakınlık kadar tanım ve çerçeve ihtiyacı da büyüyor.

İlişki tarafında mesele sadece bağ kurmak değil; bağı taşıyacak dili ve sınırı kurmak.

Önce konuşma biçimi değişir, ardından ilişkinin ritmi ve güven duygusu buna cevap verir.

Risk, ima ile anlaşılmayı beklemek ya da karşı tarafın tepkisini bütün niyetin yerine koymak.

Score sheet:

| seen_score | generic_score | too_technical_score | coaching_motivation_score | reread_score | repetition_score |
|---|---|---|---|---|---|
|   |   |   |   |   |   |

#### Variant B

**Başlık:** Denge ve Yapı Teması Derinleşiyor

Yakınlık ve güven hattı bu dönemde özellikle belirginleşiyor. Bu dönem asıl omurga yavaş ama kalıcı biçimde kuruluyor. Şu sıralar ilişkilerde yakınlık kadar tanım ve çerçeve ihtiyacı da büyüyor.

İlk bakışta bu bir "kim haklı" meselesi gibi görünebilir; ama altında, kendini ifade ederken nasıl korunduğun var.

Yakın olduğun yerlerde daha çok kendin oluyorsun. Birinin yanında durmak ya da durmamak eskisi kadar yarım his bırakmıyor.

Asıl ayrım burada: yakınlığı kendinden uzaklaşmak sanmamak.

Score sheet:

| seen_score | generic_score | too_technical_score | coaching_motivation_score | reread_score | repetition_score |
|---|---|---|---|---|---|
|   |   |   |   |   |   |

#### Variant C

**Başlık:** Denge ve Yapı Teması Derinleşiyor

Yakınlık ve güven hattı bu dönemde özellikle belirginleşiyor. Bu dönem asıl omurga yavaş ama kalıcı biçimde kuruluyor. Şu sıralar ilişkilerde yakınlık kadar tanım ve çerçeve ihtiyacı da büyüyor.

İlk bakışta bu bir "kim haklı" meselesi gibi görünebilir; ama özellikle sana ait hissettiren alan tarafında, altında kendini ifade ederken nasıl korunduğun var.

Yakın olduğun yerlerde daha çok kendin oluyorsun. Birinin yanında durmak ya da durmamak eskisi kadar yarım his bırakmıyor. Bu tema daha çok sana ait hissettiren alan içinden görünür oluyor.

Asıl ayrım, sana ait hissettiren alan tarafında büyüyen tepkiyi bütün hikayenin yerine koymamak.

Score sheet:

| seen_score | generic_score | too_technical_score | coaching_motivation_score | reread_score | repetition_score |
|---|---|---|---|---|---|
|   |   |   |   |   |   |

**Sorular**

1. Hangisi daha "beni görüyor" hissi veriyor?
2. Hangisi generic horoscope gibi?
3. Hangisi fazla teknik?
4. Hangisi fazla koçluk/motivasyon gibi?
5. Hangisini tekrar okumak isterdin?
6. Hangisinde cümleler birbirine benziyor?

- `best_overall`: 
- `worst_overall`: 

### GAD Koç / KAD Terazi — yalnız → birlik ekseni

- `fixture_id`: `fix07_aries_libra_nodes`
- `window`: `2026-05-01 -> 2026-05-31`
- `selected_date`: `2026-05-03`
#### Variant A

**Başlık:** Denge ve Yapı Teması Derinleşiyor

Hayatının bir alanı daha görünür hale geliyor; senden daha bilinçli seçimler istiyor.

Mesele sadece bir konunun açılması değil; ona nasıl yaklaştığının değişmesi.

Etki önce gündelik hayatta görünür oluyor, sonra bunun sonucu daha kalıcı bir davranış değişimine dönüşüyor.

Risk, ilk hissi sonuç sanıp süreci aceleye getirmek.

Score sheet:

| seen_score | generic_score | too_technical_score | coaching_motivation_score | reread_score | repetition_score |
|---|---|---|---|---|---|
|   |   |   |   |   |   |

#### Variant B

**Başlık:** Denge ve Yapı Teması Derinleşiyor

Yön ve görünürlük hattı bu dönemde özellikle belirginleşiyor. Bu dönem asıl omurga yavaş ama kalıcı biçimde kuruluyor. Hayatının bir alanı daha görünür hale geliyor; senden daha bilinçli seçimler istiyor.

Karar şurada: hazır hissetmekle harekete geçmek aynı şey değil.

İş, yön ya da görünürlük tarafında kontrol etmek istediğin yerler belirginleşiyor. Bir şeyi sıkı tutman sadece hırs değil; orada kaybetmek istemediğin bir güç alanı var.

Karar şurada: hazır hissetmekle kendini ortaya koymak aynı şey değil.

Score sheet:

| seen_score | generic_score | too_technical_score | coaching_motivation_score | reread_score | repetition_score |
|---|---|---|---|---|---|
|   |   |   |   |   |   |

#### Variant C

**Başlık:** Denge ve Yapı Teması Derinleşiyor

Yön ve görünürlük hattı bu dönemde özellikle belirginleşiyor. Bu dönem asıl omurga yavaş ama kalıcı biçimde kuruluyor. Hayatının bir alanı daha görünür hale geliyor; senden daha bilinçli seçimler istiyor.

Karar şurada: uzak hedeflerin ve inançların tarafında hazır hissetmekle harekete geçmek aynı şey değil.

İş, yön ya da görünürlük tarafında kontrol etmek istediğin yerler belirginleşiyor. Bir şeyi sıkı tutman sadece hırs değil; orada kaybetmek istemediğin bir güç alanı var. Bu tema daha çok uzak hedeflerin ve inançların içinden görünür oluyor.

Asıl ayrım, uzak hedeflerin ve inançların tarafında görünür olan şeyi hemen son kararın gibi taşımamak.

Score sheet:

| seen_score | generic_score | too_technical_score | coaching_motivation_score | reread_score | repetition_score |
|---|---|---|---|---|---|
|   |   |   |   |   |   |

**Sorular**

1. Hangisi daha "beni görüyor" hissi veriyor?
2. Hangisi generic horoscope gibi?
3. Hangisi fazla teknik?
4. Hangisi fazla koçluk/motivasyon gibi?
5. Hangisini tekrar okumak isterdin?
6. Hangisinde cümleler birbirine benziyor?

- `best_overall`: 
- `worst_overall`: 

## PR-2v.3 Natal Sanity Check

Bu bölüm blind ranking değil; 3 chart üzerinde beklenmedik ton/akış bozulması var mı diye manuel sanity pass.
Buradaki surface `legacy_compat`; soru seti astro-terim var/yok yerine beklenmedik regressions ve tone mismatch üstüne kurulu.

### Oğlak/Oğlak — 1. ev stellium (4+ gezegen)

- `fixture_id`: `fix02_capricorn_stellium`
- `source`: `backend/tests/_artifacts/natal_v8_baseline/fix02_capricorn_stellium.json`
- `quality_flags`: `morphology_issue`

#### Ritmini koruduğunda yön duygun güçleniyor

Netlik sende kontrol değil güven meselesi; Yükselen Oğlak belirsizliği uzatmayı sevmez ve yöneticin Satürn'ün 3. ev vurgusu bunu en çok söz, karar ve ton üzerinden görünür kılar, bu yüzden bazen bir cümleyi kurmadan önce içinden ölçüp biçmen ya da konuşma bittikten sonra ne demek istediğini zihninde yeniden toplaman aslında fazla düşünmekten çok netlik aradığını gösterir. İyi çalıştığında bu ton sana cesaret ve direktlik verir; gölgesinde sabırsızlık ya da ani tepki doğurabilir.

#### Karar verirken içinde ne oluyor

Bir ortama girdiğinde bir şey sana çarptığında zihnin boşta kalmıyor, içeride hemen pozisyon alan bir tarafın çalışıyor. Perde arkasında ise bu hat en çok söz, ton ve karar dili t…

#### Sevginin derinleşme biçimi

Kalbin yakınlığı hafif yaşamıyor; güven gördüğünde hızla derinleşiyor. Bağ sende en çok güven, mahremiyet ve derinlik tarafında açılıyor; bu yüzden gerçek açıklık arıyor ve sevildiğini hissedilir biçimde duymak istiyorsun. Açıldığında sevgiyi sıcak, görünür ve cömert biçimde hissettirebilme tarafın da belirginleşiyor. Kırıldığında güvensizlikte fazla alınmak ya da kabuğa çekilmek daha kolay tetiklenebiliyor.

**Sanity soruları**

1. Akışta beklenmedik kırılma veya dağınıklık var mı?
2. Yeni vNext renderer'a geçmesi gerekirken hâlâ legacy şablonda duran bir cümle var mı?
3. SHOU vNext tonu ile açık çelişen bir bölüm var mı?
4. Bu chart için bariz bir içerik regresyonu hissediliyor mu?

### 10. ev stellium — kariyer/visibility ağırlığı

- `fixture_id`: `fix04_h10_career_stellium`
- `source`: `backend/tests/_artifacts/natal_v8_baseline/fix04_h10_career_stellium.json`
- `quality_flags`: `morphology_issue`

#### Netlik kurduğunda gücün daha görünür oluyor

Netlik sende kontrol değil güven meselesi; Yükselen Başak belirsizliği uzatmayı sevmez ve yöneticin Merkür'ün 10. ev vurgusu bunu en çok günlük kararların ve duruşun üzerinden görünür kılar, bu yüzden bir şeyi içinden tartıp sağlam bir cümleye dönüştürdüğünde hem ritmin hem yön duygun birlikte güçlenir. İyi çalıştığında bu ton sana sezgi ve koruyucu bir hassasiyet verir; gölgesinde fazla alınma ya da geri çekilme yaratabilir.

#### Zihin–eylem–kontrol

Yükselen Başak sana dışarıda daha ölçülü ve düzenli bir duruş veriyor; insanlar çoğu zaman sende önce kontrollü tarafı görüyor. Ama zihnin çoğu zaman o kadar sakin çalışmıyor; içe…

#### Sevginin derinleşme biçimi

Bir ortama girdiğinde kalbin yakınlığı hafif yaşamıyor, güven gördüğünde hızla derinleşiyor. Perde arkasında ise bağ sende en çok yaratıcılık ve ifade tarafında açılıyor, bu yüzden gerçek açıklık arıyor ve sevildiğini hissedilir biçimde duymak istiyorsun. Açıldığında sevgiyi özgürlük bırakarak ama yine de gerçek kalarak yaşayabilme tarafın da belirginleşiyor. Kırıldığında sınırların bulanıklaşması ya da hayal kırıklığında dağılmak daha kolay tetiklenebiliyor.

**Sanity soruları**

1. Akışta beklenmedik kırılma veya dağınıklık var mı?
2. Yeni vNext renderer'a geçmesi gerekirken hâlâ legacy şablonda duran bir cümle var mı?
3. SHOU vNext tonu ile açık çelişen bir bölüm var mı?
4. Bu chart için bariz bir içerik regresyonu hissediliyor mu?

### T-square paterni — gerilim odaklı

- `fixture_id`: `fix05_t_square_tense`
- `source`: `backend/tests/_artifacts/natal_v8_baseline/fix05_t_square_tense.json`
- `quality_flags`: `morphology_issue`

#### Netlik kurduğunda gücün daha görünür oluyor

Netlik sende kontrol değil güven meselesi; Yükselen Akrep belirsizliği uzatmayı sevmez ve yöneticin Mars'ün 5. ev vurgusu bunu en çok günlük kararların ve duruşun üzerinden görünür kılar, bu yüzden bir şeyi içinden tartıp sağlam bir cümleye dönüştürdüğünde hem ritmin hem yön duygun birlikte güçlenir. İyi çalıştığında bu ton sana sezgisel akış ve hayal gücü verir; gölgesinde dağılma ya da sınır kaybı yaratabilir.

#### Karar verirken içinde ne oluyor

Bir şey sana çarptığında zihnin boşta kalmıyor; içeride hemen pozisyon alan bir tarafın çalışıyor. Bu hat en çok yaratıcılık ve ifade tarafında belirginleşiyor; bazen söylemeden ö…

#### Kalbinin eşiği

Kalbin yakınlığı hafif yaşamıyor; güven gördüğünde hızla derinleşiyor. İç hattında bağ sende en çok günlük ritim ve düzen tarafında açılıyor, bu yüzden gerçek açıklık arıyor ve sevildiğini hissedilir biçimde duymak istiyorsun. Açıldığında sevgiyi direkt, cesur ve bekletmeden gösterebilme tarafın da belirginleşiyor. Kırılgan yerde zemin sarsıldığında inatla kapanmak ya da değişime direnmek daha kolay tetiklenebiliyor.

**Sanity soruları**

1. Akışta beklenmedik kırılma veya dağınıklık var mı?
2. Yeni vNext renderer'a geçmesi gerekirken hâlâ legacy şablonda duran bir cümle var mı?
3. SHOU vNext tonu ile açık çelişen bir bölüm var mı?
4. Bu chart için bariz bir içerik regresyonu hissediliyor mu?

## Decision Criteria

- `A`: Period B/C clearly wins → runtime alignment ve daily migration devam eder.
- `B`: Period no difference → canonical policy renderer görünürlüğü tekrar kontrol edilir.
- `C`: Period better but Daily weak → PR-5 Daily Today-ness Signal ve PR-7 Daily Canonical Renderer önceliklenir.
- `D`: Legacy wins → legacy insight rescue yapılır; cleanup durur.
- `E`: Mixed → frame / scene / proof / daily trigger / natal backing bazında parçalanır.

Decision authority: **Sahra**
