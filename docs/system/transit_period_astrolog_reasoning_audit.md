# Transit / Period Astrologik Reasoning Audit

**Tarih:** 2026-05-02  
**Kapsam:** Transit, period ve daily anlatım zincirinin uçtan uca audit'i. Amaç mevcut sistemin nasıl düşündüğünü, hangi katmanlardan beslendiğini, nerede gerçekten astrologik bir akıl yürütmeye yaklaştığını ve nerede skor/filtre motoruna düştüğünü netleştirmek.

## 1. Ana hüküm

Sistemin bugünkü hali bir `tek astrologik reasoning motoru` değil. Daha doğru tanım:

1. Ham transit event üreticisi
2. Template tabanlı ilk anlamlandırma katmanı
3. Period spine seçici
4. Event card anlatı katmanı
5. Günlük seçim skorer'i
6. Günlük yeniden-yazım katmanı
7. En sonda küçük bir synthesis/planner

Yani sistem önce tekil event'leri anlamlandırıyor, sonra bunları seçiyor, sonra seçilmiş event'lerden tekrar hikâye kuruyor. Bu yüzden `neden bu bugün ana hikâye oldu?` sorusunun tek bir cevabı yok; cevap katmana göre değişiyor.

Bu mimari bazı iyi şeyler getiriyor:

- Public-safe, deterministic ve test edilebilir bir yapı
- Period ile daily arasında en azından kısmi bir bağ kurma çabası
- Natal bağlam, rulership ve dispositor zincirini tamamen yok saymama
- Tek event yerine küçük combo/suppport sinyali denemesi

Ama ana zayıflık şu:

- Astrolojik anlam grafiği merkezde değil
- Event seçimi hâlâ ağırlıklı olarak skor, okunabilirlik ve yüzeye çıkabilirlik üzerinden yapılıyor
- Derin astrolojik yapıların çoğu karar verdirici değil, copy zenginleştirici

## 2. Uçtan uca gerçek pipeline

### 2.1 Ham transit üretimi

Ana giriş:

- `backend/app/api/routes/transits.py`
- `backend/app/engine/transit_engine.py`

İlk aşamada sistem:

1. Natal snapshot çıkarıyor
2. Transit snapshot çıkarıyor
3. Transit-to-natal ve transit-to-angle aspect'lerini kuruyor
4. House overlay çıkarıyor
5. `display.items` havuzunu üretiyor

Buradaki düşünce modeli hesaplayıcı. Henüz “hangi hikâye önemli” diye düşünmüyor; “hangi event var” diye düşünüyor.

### 2.2 İlk yorum katmanı

Ana dosya:

- `backend/app/transit/interpret/interpretation_engine_v1.py`

Bu katman her raw event için:

1. `pick_primary_theme(...)` ile tema seçiyor
2. Content pack içinden template çözüyor
3. `headline`, `summary`, `do`, `watch`, `where`, `time_hint` üretiyor
4. Güçlü event ise promise injection yapmaya çalışıyor

Kaynaklar:

- `backend/app/transit/interpret/content/tr/events.json`
- `backend/app/transit/interpret/content/tr/rules.json`
- `backend/app/transit/interpret/content/tr/fallbacks.json`
- `backend/app/transit/interpret/mechanism.py`
- `backend/app/transit/interpret/themes.py`
- `backend/app/transit/interpret/where.py`

Burada temel mantık `event-first template interpretation`. Astrolojik akıl yürütme henüz global değil; event'in kendi polaritesi, aspect'i, house context'i ve seçilmiş teması üzerinden kısa anlam veriliyor.

### 2.3 Event meta / structural scoring katmanı

Ana dosya:

- `backend/app/transit/astro_event_v2.py`

Bu katman event'lere şunları ekliyor:

- `event_family`
- `importance_tier`
- `planet_class`
- `time_scale`
- `significance_score`
- `lasting_change_score`
- `chapter_opening`
- `is_structural`

Bu bölüm önemli çünkü sistem burada ilk kez “aynı event'ler eşit değil” demeye başlıyor. Ama bu da hâlâ event-centric.

### 2.4 Period selection

Ana dosya:

- `backend/app/transit/narrative/selection.py`

`select_event_ids(...)` period/event-card omurgasını seçiyor. Mod:

- `story_first_v2`

Buradaki mantık:

1. Bütün public event'ler içinden story score hesapla
2. Bir `spine` seç
3. Sonra role bazlı `support` seç
4. Sonra coverage anchor ekle:
   - angles
   - 3/9 mind axis
   - Uranus/Pluto transform hattı
5. Son olarak diversity + dedupe ile doldur

Bu katman period için sistemin en “hikâye arayan” bölümü. Ama hâlâ story, event'lerden sonradan çıkarılıyor; önce chart-graph kurulup sonra hikâye oradan türetilmiyor.

### 2.5 Event card üretimi

Ana dosyalar:

- `backend/app/transit/narrative/deep_archetype_engine.py`
- `backend/app/transit/narrative/natal_promise.py`
- `backend/app/transit/narrative/hybrid_context.py`
- `backend/app/transit/narrative/voice_engine_tr.py`
- `backend/app/transit/narrative/text_quality_tr.py`
- `backend/app/transit/narrative/chain_explainer_tr.py`

`build_event_card(...)` zinciri:

1. `build_combined_meaning(...)`
2. `build_natal_promise(...)`
3. `build_hybrid_event_context(...)`
4. `build_section_injections(...)`
5. `build_insight_pack(...)`
6. `build_card_copy(...)`
7. `apply_copy_quality_layer(...)`
8. `rewrite_event_card_tr(...)`

Bu zincirde event, artık düz aspect olmaktan çıkıp card'a dönüşüyor.

Burada sisteme eklenen şeyler:

- Natal target house/sign
- Dispositor
- Rulership houses
- Natal aspects focus
- Connected points
- House scene
- Copy motifs
- Phrase pack enjeksiyonu

Bu sistemin güçlü tarafı şu: `natal context pack` ve `hybrid context` gerçekten zengin. Yani mimaride astrolojik yapı düşünülmüş.

Ama zayıf tarafı şu: bu yapılar çoğu zaman `karar mekanizması` değil `copy enrichment` olarak kullanılıyor.

### 2.6 Period core ve period story

Ana dosyalar:

- `backend/app/transit/narrative/deep_archetype_engine.py`
- `backend/app/transit/narrative/astrolog_narrative_engine.py`
- `backend/app/transit/narrative/text_quality_tr.py`

`build_period_core(...)` ve `build_period_story(...)` period anlatısını kuruyor.

Zincir:

1. Seçilmiş event'lerden dominant house/domain çıkar
2. `build_period_copy(...)` ile ilk core story üret
3. `build_root_causes(...)` ile bazı kök sebep eksenleri çıkar
4. `infer_story_track_id(...)` ile track seç
5. `build_story_track_copy(...)`
6. `build_period_story(...)` ile opening, big_picture, mechanism, growth_edge, what_it_builds üret

Bu katman period tarafında sistemin en yetişkin bölümü. Çünkü düz headline üretmek yerine:

- spine event
- support events
- chapter role
- root cause
- track

mantığı var.

Ama burada da root cause gerçek anlamda tüm natal+transit ağından türemiyor. Daha çok seçilmiş event listesi üzerinde heuristik pattern çıkarımı yapılıyor.

### 2.7 Selected day context

Ana yer:

- `backend/app/api/routes/transits.py`

`selected_day_context` takvimden şunları alıyor:

- top event ids
- labels
- critical reasons
- signals count
- event count

Yani daily selection gökten bağımsız çalışmıyor; gün bağlamı takvimden geliyor. Bu doğru bir fikir.

### 2.8 Daily selection

Ana dosya:

- `backend/app/transit/narrative/daily_selection.py`

Bu dosya günlük adayları seçiyor. Kullandığı ana bileşenler:

- strength score
- today score
- narrative score
- delta salience score
- personalization score
- eligibility / qualifies / meaningful kapıları
- cluster / rerank / penalties

Bu bölüm pratikte bir `meaningful public daily card scorer`.

Yani sorusu şu:

- Hangisi bugün öne çıkar?
- Hangisi daha okunabilir?
- Hangisi günlük yüzeyde daha iyi çalışır?

Astrolojik sorusu şu değil:

- Bugünün gerçek astrologik ana hikâyesi ne?
- Bugün hangi sinyal period omurgasını aktive ediyor?
- Hangi olay diğerlerini organize etmeli?

### 2.9 Daily humanizer

Ana dosya:

- `backend/app/transit/narrative/daily_humanizer_tr.py`

Bu katman seçilmiş card'ı günlük kullanım diline çeviriyor:

- `felt_line_tr`
- `why_it_feels_this_way_tr`
- `guidance_micro_tr`
- `signal_label_tr`
- `house_touchpoint_tr`

Buradaki mantık açıkça surface-oriented. Daha okunur, daha kısa, daha app-uygun cümleler üretiyor.

### 2.10 Daily synthesis

Ana dosya:

- `backend/app/transit/narrative/daily_synthesis.py`

Bu son katman seçilmiş daily card'lar ve period core'dan tek metin kuruyor:

1. `primary_signal`
2. `period_spine`
3. `support_signal`
4. `narrative_mode`
5. headline/body/guidance

Bu katman gerçek combo reasoning'e en çok yaklaşan yer. Çünkü ilk kez:

- trigger
- spine
- support

üçlüsü üzerinden tek hikâye kurmaya çalışıyor.

Ama halen kısıtlı:

- primary signal merkezde
- support sinyal ikincil
- combo semantiği ev/house/domain benzerliği ağırlıklı
- dispositor, natal vow, sign ruler, natal temperament gibi derin bağlar combo mantığında merkezde değil

## 3. Sistemin aslında planladığı düşünce modeli ne

Kodun bugünkü hali, niyet olarak şunu planlamış görünüyor:

1. Natal promise kişinin temel yatkınlığını söylesin
2. Period layer bunun hangi chapter'ının aktive olduğunu söylesin
3. Daily layer bugün bunun nereden yüzeye çıktığını söylesin
4. Copy layer bunu insan diline indirsin

Yani teorik hedef zaten `yalnız event listesi` değil. Hedef:

- natal karakter
- dönem omurgası
- günlük trigger
- kısa yönlendirme

birleşimi.

Sorun niyetin zayıf olması değil. Sorun, bu katmanların karar gücünün eşit olmaması:

- Natal promise zengin ama çoğu yerde dekoratif
- Period story güçlü ama daily selection üzerinde sınırlı etkili
- Daily selection en sert karar verici olduğu için sistemin gerçek yöneticisi o oluyor

Bu yüzden sistemin düşünce merkezi period/natal değil, fiilen daily scorer oluyor.

## 4. Nerelerde doğru yapılmış

### 4.1 Natal bağlam tamamen unutulmamış

`build_natal_promise(...)` ve `build_hybrid_event_context(...)` içinde:

- dispositor
- rulership houses
- natal aspects focus
- connected points
- angle ruler

gibi yapılar var. Yani sistemin mimarisi astrologik derinliğe kapalı değil.

### 4.2 Period omurga düşüncesi var

`selection.py`, `chapter_role_engine.py`, `astrolog_narrative_engine.py` içinde:

- spine
- support
- opener/builder/peak/release/integrator
- story track

mantığı var. Bu ciddi bir artı.

### 4.3 Günlük tam boş kalmasın diye fallback düşünülmüş

`daily_selection.py` içinde `used_period_fallback` var. Bu önemli çünkü “bugün hiçbir şey yok” yerine “arkadaki dönem bugün yüzeyde” tonuna düşme çabası var.

### 4.4 Combo fikri tohum halinde var

`cluster_support_event_ids`, `support_signal`, `period_spine`, `narrative_mode` bölümleri gerçek combo reasoning'in embryosu.

### 4.5 Public narrative güvenliği düşünülmüş

Surfaceability, readability, guidance value gibi metrikler kötü ürün çıktısını azaltıyor. Bunlar astrologik derinlik değil ama ürün kalite katmanı olarak değerli.

## 5. Nerelerde yanlış yola düşülmüş

### 5.1 Tek reasoning merkezi yok

Şu an aynı event birden fazla yerde yeniden yorumlanıyor:

1. `interpretation_engine_v1`
2. `build_event_card`
3. `daily_humanizer_tr`
4. `daily_synthesis`

Bu şu probleme yol açıyor:

- Anlam katmanı parçalanıyor
- Katmanlar aynı astro veriyi farklı dillere ve önceliklere göre yeniden kuruyor
- Son metin bazen gerçek neden yerine son rewrite katmanının tercihlerini yansıtıyor

### 5.2 Derin astrolojik bilgi karar verici değil, süsleyici

Dispositor, rulership, natal aspect focus gibi bilgiler çoğunlukla:

- copy enrichment
- motif injection
- extra line
- promise score

seviyesinde kalıyor.

Yani sistem bunları `hangi hikâye kazanmalı` sorusunda tam kullanmıyor.

### 5.3 Daily selection astrologik önemden çok surfaceability optimize ediyor

`daily_selection.py` günlük event'i şunlara göre seçiyor:

- orb
- phase
- planet speed
- date proximity
- calendar salience
- humanizer confidence
- guidance specificity
- memorability

Bu ürün açısından mantıklı ama astrologik merkez açısından problemli. Çünkü:

- ağır ama belirleyici bir outer-planet activation
- günlük daha okunabilir bir Moon/Mercury olaya yenilebiliyor

### 5.4 Hızlı gezegen ve kısa pencere bias'ı çok yüksek

Config ve feature vector içinde:

- Moon/Sun/Mercury/Mars lehine yüksek ağırlık
- short / exact / peaking today lehine yüksek bias

var.

Bu, “bugün hissettirir” sorusu için faydalı ama “bugünün gerçek hikâyesi nedir” sorusunu saptırabilir.

### 5.5 `eligible/qualifies/meaningful` kapıları hâlâ filtre zihniyeti taşıyor

Fallback olsa bile ana mantık hâlâ:

- event yeterince güçlü mü
- yeterince bugünlük mü
- yeterince anlatılabilir mi

kapılarından geçiyor.

Bu, astrolog gibi `önce istisna var mı`, `yoksa period mu`, `yoksa combo mu` diye sormuyor. Önce puan soruyor.

### 5.6 Period root cause gerçek graph reasoning değil

`build_root_causes(...)` faydalı ama kısıtlı. Şu an daha çok:

- event'ler hangi evlere düşüyor
- angle hit var mı
- 3/9 veya 1/7 pattern'i var mı

seviyesinde.

Eksik olan:

- dispositorship chain dominance
- natal promise priority map
- exact aspect stack resolution
- house ruler activation chain
- transiting planet dignity / condition
- promise vs activation vs manifestation ayrımı

### 5.7 Combo mantığı semantik ama sığ

Şu an support çözümü çoğunlukla:

- same natal point
- same target house
- same domain
- supportive aspect mode

ile çalışıyor.

Gerçek astrologik combo için bu yetmez. Gerekli olan:

- aynı dispositor zinciri
- aynı ruler family
- aynı natal promise chapter'ı
- trigger vs container ayrımı
- cause vs expression ayrımı
- manifesting house vs source house ayrımı

### 5.8 Tema uzayı fazla sıkıştırılmış

Birçok yerde sistem house/domain map'e çöküyor:

- identity
- relationships
- mind
- career
- home
- inner

Bu güzel bir UI abstraction ama reasoning motorunun iç dili olmamalı. İç motor daha zengin olmalı; UI'ya inerken sıkıştırılmalı.

### 5.9 Metin katmanları üst üste binince ses ve mantık drift ediyor

Özellikle:

- `voice_engine_tr.py`
- `text_quality_tr.py`
- `daily_humanizer_tr.py`
- `daily_synthesis.py`

aynı anlamı farklı amaçlarla tekrar yazıyor.

Sonuç:

- bazen güçlü astrolojik bağ kayboluyor
- bazen metin daha düzgün ama daha yüzeysel oluyor
- bazen gerçek spine yerine copy-friendly sentence öne çıkıyor

## 6. “Gerçekten astrolog gibi düşünen” sisteme yaklaşmak için hedef model

Hedef “daha fazla template” değil. Hedef reasoning mimarisini merkezden değiştirmek.

### 6.1 Event-first yerine chart-state-first motor

Yeni merkez şu olmalı:

1. Natal meaning graph
2. Period activation graph
3. Day trigger graph
4. Story planner
5. Surface realizer

Yani önce event listesi değil, önce `bugünkü chart state` kurulmalı.

### 6.2 Ayrı ayrı olay değil, aktive olmuş yapı düşünülmeli

Önerilen canonical reasoning object:

1. `natal_promise_map`
2. `period_chapters`
3. `daily_triggers`
4. `activation_clusters`
5. `today_story_candidates`
6. `selected_story`

Burada `selected_story` bir event değil, bir reasoning paketi olmalı.

Örnek:

- chapter: `relationship_boundary_rebuild`
- spine: `Saturn square Venus`
- activator: `Moon conjunct DSC`
- support: `Venus sextile Mercury`
- cause_chain: `DSC ruler -> Venus -> Saturn pressure`
- manifested_in: `7th and 3rd house`
- tone: `combo_activation`

### 6.3 Öncelik ağacı skordan önce gelmeli

Önerilen sırayla soru:

1. İstisnai olay var mı?
2. İçinde bulunulan aktif chapter ne?
3. Bugün o chapter'ı aktive eden trigger var mı?
4. Aynı chapter içinde bir combo cluster oluşuyor mu?
5. Günlük flavor sadece bunun üstüne mi oturuyor?
6. Hiçbiri yoksa sessiz gün narrative'i chapter'dan mı geliyor?

Bu akışta score yardımcı olur; karar verici olmaz.

### 6.4 Combo cluster gerçekten astrolojik kurulmalı

Cluster kuralları yalnız ev/domain eşitliği olmamalı. Şunlar da dahil edilmeli:

- same dispositor chain
- same house ruler family
- same natal promise theme
- same chapter role
- source-house / target-house continuity
- transit planet as trigger vs container
- pressure + support dengesi
- manifestation vs root-cause ayrımı

### 6.5 Natal promise sürekli çalışan bias olmalı

Şu an promise score çoğu yerde yan veri. Bunun merkezileşmesi gerekiyor.

Her event veya cluster için sorulmalı:

1. Bu kişi için bu tema natal vaat içinde gerçekten merkezi mi?
2. Bu transit o vaadi büyütüyor mu, zorluyor mu, görünür kılıyor mu?
3. Günlük trigger bu vaadi bugün hangi sahnede somutlaştırıyor?

### 6.6 Sentence layer reasoning object'ten beslenmeli

Metin üretimi artık `single event`ten değil `selected_story`den yapılmalı.

Yani yazar şu veriyi almalı:

- story_type
- spine signal
- trigger signal
- support signals
- natal promise anchors
- manifested houses
- reasoning trace

Ve tek kez yazmalı.

Bugünkü gibi dört ayrı rewrite katmanı yerine:

1. Reasoning planner
2. Narrative realizer
3. Lightweight polish

yeterli olur.

## 7. Mevcut yapıyı çöpe atmadan dönüşüm yolu

### Faz 1. Canonical reasoning object çıkar

Yeni bir internal katman:

- `backend/app/transit/reasoning/today_story_engine.py`

Bu katman mevcut event'leri tüketip şunu üretmeli:

- `today_story_candidates`
- `selected_story`
- `reasoning_trace`

İlk aşamada mevcut dosyalardan beslenebilir:

- `build_natal_promise(...)`
- `build_hybrid_event_context(...)`
- `select_event_ids(...)`
- `selected_day_context`

### Faz 2. Daily selection scorer'i secondary yap

`daily_selection.py` tamamen silinmek zorunda değil. Ama rolü değişmeli:

- “hangi event daha okunur” değil
- “seçilmiş hikâyeyi hangi supporting event'lerle public yüzeye indirelim”

olmalı.

### Faz 3. Period ve daily'yi aynı planner altında birleştir

Şu an:

- period story ayrı motor
- daily synthesis ayrı motor

Bunun yerine:

- same chapter graph
- same story object
- farklı horizon render

mantığı daha doğru olur.

### Faz 4. Deep astro katmanlarını karar verici yap

Aşamalı olarak şu yapılar selection/planner içine taşınmalı:

- dispositors
- house rulers
- natal aspect bundles
- sign condition / modality bias
- chart temperament
- promise hierarchy
- transit as cause vs transit as surface trigger

### Faz 5. Voice katmanını sadeleştir

Uzun vadede ideal:

1. Template interpretation v1 ya emekliye ayrılır ya da sadece fallback olur
2. Event card copy ile daily humanizer tek omurgaya bağlanır
3. `daily_synthesis.py` sadece planner + realizer olur

## 8. Kısa net sonuç

Mevcut sistem kötü bir sistem değil. Hatta bugünkü repo içinde transit tarafındaki en değerli şey, period spine ve natal bağlam kurma niyetinin zaten var olması.

Ama sistemin gerçek kontrol merkezi hâlâ:

- score mix
- readability
- surfaceability
- event-first ranking

olduğu için ortaya çıkan şey “astrolog gibi düşünen motor” değil, “astro-event'leri iyi paketleyen anlatı sistemi”.

Gerçek dönüşüm için ana hareket şu olmalı:

- Event seçip hikâye yazmak yerine
- Önce bugünün chart-state hikâyesini seçip
- Sonra event'leri o hikâyenin kanıtları olarak bağlamak

Sistem buna uzak değil. Altyapının parçaları var. Ama bu parçaların karar hiyerarşisi ters kurulmuş durumda.
