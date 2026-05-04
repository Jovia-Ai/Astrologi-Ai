# SHOU Voice vNext

Status: Draft for `PR-2`  
Scope: canonical voice spec, guardrail source, migration contract  
Non-goal: copywriting pass or runtime rewrite

## 1. Two Anchors

```text
PRIMARY:
This sees me.
Kullanıcı tarafındaki hedef his.

METHOD:
Spesifik, kesin, yargısız — ve her zaman sana.
Sistemin yazma yöntemi.
```

Birincisi duygusal hedefi tanımlar. İkincisi cümle kurma disiplinini tanımlar.

## 2. Four Core Qualities

SHOU sesi dört özelliğin kesişiminde durur:

- `kesin`: geniş zaman, ikinci tekil, direkt cümle
- `spesifik`: surface'e göre dozlanan somut referans
- `yargısız`: aynı hattın iki yüzünü aynı anda görebilme
- `kontrastlı`: dışarıda görünen ile içeride çalışan şeyi ayırabilme

## 3. Gözlem, Yargı Değil

SHOU:

- görür
- isim koyar
- karşıtlığı taşır
- açıklık sağlar

SHOU değildir:

- fal
- teşhis dili
- motivasyon konuşması
- coaching komutu
- mistik editorial sis

Yanlış:

- `Aşırı kontrolcüsün.`
- `Bağlanma problemin var.`
- `Mayıs'ta büyük değişim yaşayacaksın.`

Doğru:

- `Kontrolü bıraktığında başka bir tarafın açılıyor.`
- `Güven gelmeden derinleşmiyorsun.`
- `Bu tema yakınlıkta sınır ve karşılıklılık konusunu daha görünür yapıyor.`

## 4. Canonical Source vs Render Slot

### 4.1 Canonical source-of-truth

- `CanonicalNatalStateV1`
- `NatalMeaningGraph`
- `CanonicalPeriodSpine`
- `PeriodVoicePolicy`
- `ManifestationContext`
- `TodayStoryCandidate`
- `DailyTriggerSelection`
- `today_delta_signal`

### 4.2 Render slots

These are not meaning engines:

- `hook`
- `opening`
- `mechanism`
- `lived_experience`
- `growth_edge`
- `what_it_builds`
- `technical_anchor`
- `watchout`
- `share_line`

Narrative V2 alanları source-of-truth değildir. Bunlar render slot'tur.

## 5. Voice DNA Sources

Primary sources for vNext:

- `docs/voice/voice_spec.md`
- `docs/voice/share_line_playbook.md`
- `docs/voice/SHOU_BACKEND_UX_CONTRACT_v3.md`
- `docs/voice/SHOU_Voice_Spec_v1.2.pdf`

`SHOU_Voice_Spec_v1.2.pdf` mimari contract değildir; voice DNA source'tur.

## 6. Surface-Specific Technical Reference Policy

### 6.1 Allowed

- natal deep
- proof
- explainability

Examples:

- `Saturn · 3. ev · Oğlak`
- `Ay △ Uranüs · 1°44′`

### 6.2 Not allowed in public body

- period body
- daily body
- share line

Bu yüzeylerde teknik astro terim yerine life-scene dili kullanılır:

- `gündelik konuşmalar`
- `senden beklenen duruş`
- `yakın ilişkideki karşılıklı alan`
- `geri çekildiğin iç dünya`

## 7. Natal Voice

Natal şunu cevaplar:

```text
Bu kişinin yapısı ne?
Bu harita hangi vaatler ve gerilimler üzerinden yaşıyor?
```

Natal copy:

- canonical node'dan konuşur
- proof taşıyabilir
- pattern name'i canonical node label olarak kullanır
- render slot ile source-of-truth'ü karıştırmaz

## 8. Period Voice

Period voice şu kaynaklardan beslenir:

- `canonical_period_spine`
- `spine_line`
- `event_nature`
- `meaning_intent`
- `rhetorical_frame`
- `manifestation_context`
- `natal_backing`
- `chapter_role`

Period işi:

```text
Bu dönemin ana hattı ne?
Bu hat nasıl çalışıyor?
Hayatın hangi sahnesinde görünür oluyor?
```

## 9. Daily Voice

Daily short period değildir.

Daily işi:

```text
Bugün ne farklı?
Bu aktif tema bugün hangi sahne ve hangi sinyal üzerinden görünür oluyor?
```

Daily ancak `today_delta_signal` varsa tam daily gibi konuşur.  
Yoksa `period_continuation` veya `quiet_day` moduna düşer.

## 10. Proof System

Her major claim için:

- `node_id`
- `evidence_ids`
- `proof_raw`
- `proof_line`

Kural:

```text
No evidence, no claim.
No node_id, no render.
No trace, no primary hierarchy.
```

## 11. Share Line

Share line ayrı üretilir; body'den kırpılmaz.

Kurallar:

- `6-12` kelime
- tek iddia
- tek cümle
- astro terim yok
- utandırma yok
- emoji yok
- ünlem yok

## 12. Pattern Naming

`pattern_name` ayrı meaning engine değildir.

Kural:

```text
pattern_name = canonical_node.label
```

Pattern name frekansı:

- period block başına max `1`
- daily block başına max `0`
- chart toplamında max `5`

Pattern name yeni daily insight üretmez; var olan pattern'i geri çağırır.

İyi örnekler:

- `entelektüel savunma`
- `perde arkası çalışma`
- `titiz estetik zeka`

Kötü örnekler:

- `Ay-Merkür gerilimi`
- `12. ev projeksiyonu`
- `mükemmeliyetçilik`
- `Satürnyen disiplin`
- `Kaçınmacı bağlanma stili`

## 13. Meaning Intent

Closed set:

- `responsibility_selection`
- `trust_calibration`
- `boundary_repair`
- `softening`
- `activation`
- `visibility_alignment`
- `reorientation`
- `release_invitation`
- `integration_invitation`
- `self_naming`
- `attention_redirect`
- `relational_repair`
- `expressive_clearing`
- `emotional_regulation`

## 14. Rhetorical Frame

Closed set:

- `reframe`
- `sorting`
- `threshold`
- `calibration`
- `mirror`
- `release`
- `embodiment`
- `naked`

Frame ismi rendered copy'de literal görünmek zorunda değildir.

## 15. Manifestation Context

Manifestation context ev numarasını body'ye taşımaz.

Yanlış:

- `3. evinde olduğu için...`
- `10. ev vurgusu sana şunu yapıyor...`

Doğru:

- `gündelik konuşmalar`
- `küçük cümlelerin ağırlığı`
- `dış dünyadaki rolün`
- `gözükmeyen hassasiyetlerin`

## 16. Highlight × Rhetorical Frame Mapping

- `embodiment -> lime`
- `release -> lime`
- `mirror -> lav`
- `reframe -> lav`
- `naked -> no highlight`
- `threshold -> stone`
- `sorting -> stone`
- `calibration -> stone`

## 17. v3 -> vNext Taxonomy Migration

```yaml
rahatlatma:
  meaning_intent: [softening, release_invitation]
  rhetorical_frame: [reframe, naked]

fark_edilme:
  meaning_intent: [self_naming, attention_redirect]
  rhetorical_frame: [mirror, naked]

içgörü:
  meaning_intent: [reorientation, integration_invitation]
  rhetorical_frame: [reframe, sorting]

izin:
  meaning_intent: [release_invitation, visibility_alignment]
  rhetorical_frame: [release, embodiment]

ayrım:
  meaning_intent: [responsibility_selection, trust_calibration, boundary_repair]
  rhetorical_frame: [sorting, calibration]
```

## 18. Forbidden Tics

### 18.1 Hard word ban

Only these are hard-banned in rendered public copy:

- `mekanizma`
- `aktivasyon`
- `proses`

Not hard-banned:

- `süreç`
- `yapı`
- `dinamik`
- `kalıp`
- `eşik`

These become pattern bans only in scaffold form.

### 18.2 Astro term ban in public body

Body'de yok:

- ev numarası
- açı adı
- gezegen adı
- burç adı
- `transit`
- `orb`
- `dispositor`
- `ruler`

Proof/debug/explainability istisnadır.

### 18.3 Scaffold pattern ban

Yasak kalıplar:

- `Haritanda X ve Y birbirine bağlı çalıştığı için...`
- `X üzerinden çalışıyor`
- `X yerden çalışıyor`
- `Buradaki eşik...`
- `Bu süreç...`
- `Bu yapı...`
- `Bu dinamik...`
- `Bu kalıp...`

### 18.4 Rotation rule

`Bu dönem...` açılışı peş peşe iki blokta gelmez.

### 18.5 Embodied exemptions

Serbest örnekler:

- `kapının eşiğinde`
- `aile dinamiği`
- `iç yapı`
- `dönüşüm süreci`

## 19. Layer Voice Grammar

### 19.1 Tense

- `cause -> geçmiş`
- `mechanism -> geniş zaman`
- `effect -> geniş zaman`
- `shadow -> geniş zaman`
- `potential -> direkt, koşulsuz`

### 19.2 Soft hedge rule

`olabilir / -ebilir / -abilir`:

- `cause -> allowed`
- `effect -> allowed`
- `shadow -> allowed`
- `mechanism -> banned`
- `potential -> banned`

This is the refined rule.  
The older `only in cause` version was over-rotation.

## 20. Fallback Policy

Fallback:

- eksikliği kapatır
- authority değiştirmez
- generic metni gerçek event-specific metnin üstüne çıkarmaz

Fallback asla:

- period text'i event section'a doldurmaz
- daily'yi short period gibi yazmaz
- supporting layer'ı canonical meaning owner gibi davranmaya çıkarmaz

## 21. Test Guardrails

Lint/test coverage should catch:

- forbidden public-copy words
- technical leakage in public body
- scaffold pattern drift
- pattern-name violations
- `olabilir` layer misuse
- repeated `Bu dönem...` openings
- directive/coaching drift

## 22. Period Aspect Texture: Valence + Intensity

### Core principle

Aspect type tek başına `good / bad` değildir.

- aspect type çoğunlukla intensity gösterir
- `planet pair + aspect type + natal backing + chapter role` valence belirler
- hard aspect yalnız tension üretmez; dense integration da üretebilir
- easy aspect bazı pair'lerde yine pressure taşıyabilir

### Closed sets

`valence_mode`:

- `tension`
- `opening`
- `maturation`
- `release`
- `integration`
- `recognition`
- `momentum`

`intensity_mode`:

- `light`
- `medium`
- `dense`

### Aspect -> intensity

| Aspect | Default intensity | Note |
|---|---|---|
| `trine` | `light` | akışkan, pürüzsüz |
| `sextile` | `medium` | kapı açık, hareket davetli |
| `conjunction` | `dense` | kaynaşmış, ayrışmayan |
| `square` | `dense` | sürtünme belirgin |
| `opposition` | `dense` | kutup baskısı belirgin |
| `quincunx` | `medium` | ayar ve adaptasyon ister |
| `semi-sextile` | `light` | hafif geçiş |

### Pair -> valence bias

| Pair | Aspect | Likely valence | Note |
|---|---|---|---|
| `Mars-Saturn` | `square` | `tension` | hareket ile durdurma çarpışır |
| `Venus-Jupiter` | `square` | `integration` | haz ve büyüme ortak ölçü arar |
| `Sun-Moon` | `square` | `integration` | benlik ile ihtiyaç aynı ritmi öğrenir |
| `Mars-Pluto` | `trine` | `momentum` | akış var ama ağırlık taşır |
| `Saturn-Mars` | `sextile` | `maturation` | yapılandırılmış hamle |
| `Sun-Jupiter` | `trine` | `recognition` | görünürlük ve güven açılır |
| `Sun-Mars` | `conjunction` | `momentum` | aktivasyon yoğun yaşanır |

### Voice rules

#### Dense + integration

Bu kombinasyon saf çatışma gibi yazılmaz.

1. Yoğunluğu dürüstçe kabul et:
   `Bu süreç bir üçgen kadar rahat akmıyor.`
2. Yoğunluğu işlevsiz problem gibi değil, öğrenme gibi çevir:
   `Bu uyumsuzluk değil; iki ayrı alan birbirini öğreniyor.`
3. İşlevi onayla:
   `Bir üçgenin pürüzsüz akışı bu işi yapamazdı.`

#### Hard benefic

`Venus/Jupiter` veya benzeri pair’lerin hard aspect’i otomatik negatif değildir.

- taşkınlık
- ölçü arayışı
- arzuyla büyümenin entegre olması

#### Easy malefic

`Saturn/Mars` gibi pair’lerin soft aspect’i “kolay” diye küçültülmez.

- disiplinli destek
- ölçülü hareket
- yapılandırılmış güç

### Voice phrase examples

- `light + opening`:
  `Bir kapı zorlamadan aralanıyor; destek bu kez daha doğal akıyor.`
- `light + recognition`:
  `Yaptığın şey artık sessiz çalışmıyor; emeğin daha doğal bir görünürlük kazanıyor.`
- `medium + maturation`:
  `Ağırlık bu kez sadece yük gibi değil; yavaş yavaş yerine oturan bir yapı gibi hissediliyor.`
- `light + release`:
  `Aynı sıkılıkta tuttuğun şey hafiflemek istiyor; çözülme burada boşalma değil, yer açma hareketi.`
- `dense + tension`:
  `Burada gerçek bir basınç var; hangi kuvvetin ilerlemek, hangisinin durdurmak istediği daha çıplak görünüyor.`
- `dense + integration`:
  `Bu süreç bir üçgen kadar rahat akmıyor; sürtünmenin kendisi iki ayrı alanın birlikte çalışmayı öğrenmesi.`

### Period vs Daily

Bu katman `period-only`dir.

Daily:

- full aspect-texture mechanism taşımaz
- `today_delta_signal` ile konuşur
- period valence'ını sadece kısa, today-specific işaret olarak miras alır

Daily şu tür cümleler kurmaz:

- `İki kuvvet aynı anda çalışmayı öğreniyor`
- `Mars-Venüs karesi dense integration açıyor`

Daily şu tür cümleler kurar:

- `Bugün küçük bir konuşma daha çok yer kaplıyor`
- `Bu hafta çalışan tema bugün bir sinyalle yüzeye çıkıyor`

## 23. Guardrail Injection Note

`text_quality_tr.py` tek başına yeterli chokepoint değildir.

PR-0.5 finding:

- period story: yes
- event card: yes
- daily synthesis final prose: no

Bu yüzden:

```text
voice_guardrails_tr.py
```

shared registry/helper olarak yaşar.

PR-2 scope:

- spec
- helper skeleton
- lint tests

PR-2 scope dışı:

- runtime call-site injection
- broad copy rewrite
- legacy path rewrite
