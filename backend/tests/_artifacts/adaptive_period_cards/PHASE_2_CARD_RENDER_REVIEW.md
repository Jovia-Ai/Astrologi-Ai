# Phase 2 Card Render Review

- `period_signal_lines_v1` is additive under `period_core`.
- Card copy is theme-clustered, not one-card-per-aspect.
- `_adaptive_cards_context` remains artifact/test-only.

## 2026-03-04 Istanbul real route

### Semantic owner

- `source`: `life_chapter`
- `selected_meaning`: `speech_authority`
- `chapter_priority.applied`: `False`

### period_reading_v1.full_text

```text
Kısa mesajlarda, yarım kalmış konuşmalarda ve hızlı cevap verme anlarında sözünün ağırlığı değişiyor.

Eskiden refleksle çıkan cümle seni hemen konumlandırıyor gibi gelebilirdi. Şimdi ilk tepkiyi son söz yapmak yerine, hangi cümlenin gerçekten sana ait olduğunu seçiyorsun.

Bu dönem sana daha çok konuşmayı değil, sözünü daha sahipli kurmayı öğretiyor.
```

### period_signal_lines_v1 cards

#### 1. Sözün yerini buluyor

- `preview`: Kelimelerin artık daha seçilmiş bir yere oturuyor. Hızlıca verilen cevaplar eskisi kadar rahat taşınmıyor.
- `body`: Bir mesajı göndermeden önce kelimeleri tarttığın o küçük duraksama var ya; tam orada bir şey değişiyor. Eskiden hızlı cevap vermek seni koruyor gibi görünmüş olabilir. Şimdi cümle hızlı çıktığında değil, gerçekten sana ait olduğunda ağırlık kazanıyor. Sadece konuşmuyor, sözünle oraya bir imza bırakıyorsun.
- `theme_palette`: `saturn_maturation`
- `domain_palette`: `mind_communication_learning`
- `narrative_move`: `communication_reflex`
- `evidence_refs`: `[{'event_id': '88bc98188b2f7931360493237881969004d50662', 'role': 'builder', 'domain': 'identity', 'house_scene': 'house_1'}, {'event_id': '4f022aff91a1e6ad15cdb8962a6fd660338d94bc', 'role': 'peak', 'domain': 'relationships', 'house_scene': 'house_7'}, {'event_id': '161ec34605e090dffcc4ebf8f610d818058e3ab8', 'role': 'integrator', 'domain': 'identity', 'house_scene': 'house_1'}]`
- `source_event_ids`: `['88bc98188b2f7931360493237881969004d50662', '4f022aff91a1e6ad15cdb8962a6fd660338d94bc', '161ec34605e090dffcc4ebf8f610d818058e3ab8']`
- `context_used.summary`: semantic=`speech_authority`, manifestation=`kısa mesajlar, yarım kalmış konuşmalar, hızlı cevap verme anları`

#### 2. İlk cümle yetmiyor

- `preview`: Boşluğu hemen dolduran cevap, içerideki gerçek yerini tam taşımıyor. Biraz durduğunda ne söylemek istediğin daha net çıkıyor.
- `body`: Yarım kalmış konuşmalar ya da kısa mesajlar bu ara sandığından fazla iz bırakıyor. İlk tepkinle son sözünün aynı olmadığını daha çabuk fark ediyorsun. Özellikle küçük cümlelerin ağırlığı artarken, aceleyle kurduğun ton bütün hikâyenin yerine geçebiliyor. Bir nefeslik duraksama burada zayıflık değil; cümleni gerçekten seçtiğin yer.
- `theme_palette`: `pluto_depth`
- `domain_palette`: `mind_communication_learning`
- `narrative_move`: `integration`
- `evidence_refs`: `[{'event_id': 'b66e8f9d1fe74f30df6447f63e57b0b2e99e1f19', 'role': 'builder', 'domain': 'mind', 'house_scene': 'house_3'}]`
- `source_event_ids`: `['b66e8f9d1fe74f30df6447f63e57b0b2e99e1f19']`
- `context_used.summary`: semantic=`speech_authority`, manifestation=`kısa mesajlar, yarım kalmış konuşmalar, hızlı cevap verme anları`

#### 3. Yakınlıkta çizgin beliriyor

- `preview`: Yan yana dururken kendi cümleni fazla kısmadan da kalabildiğin anlar çoğalıyor. İlişki burada sadece uyumla yürümüyor.
- `body`: Karşı tarafı kollarken kendi yerini sessizce geri çektiğin anlar daha görünür. Burada mesele sertleşmek değil; ne hissettiğini fazla dolandırmadan söyleyebilmek. Sıcak kalırken çizgini de koruduğunda, yakınlık savunmaya değil açıklığa yaslanıyor. Bu da ilişkide seni silmeden kalmanın başka bir yolunu açıyor.
- `theme_palette`: `neptune_blur_or_sensitivity`
- `domain_palette`: `relationship_intimacy_agreements`
- `narrative_move`: `relationship_mirror`
- `evidence_refs`: `[{'event_id': '4f022aff91a1e6ad15cdb8962a6fd660338d94bc', 'role': 'peak', 'domain': 'relationships', 'house_scene': 'house_7'}]`
- `source_event_ids`: `['4f022aff91a1e6ad15cdb8962a6fd660338d94bc']`
- `context_used.summary`: semantic=`speech_authority`, manifestation=`yan yana dururken nerede durduğunu söylemek`

### Checks

- `blocked_source_check`: `{'used_old_blocks': False, 'used_daily_body': False, 'used_best_times_score': False, 'used_story_tracks_as_owner': False, 'used_event_story_map_as_owner': False, 'used_profile_v8_as_authority': False, 'used_personality_imprint_as_authority': False, 'used_meaning_graph_v1_1_as_authority': False}`
- `voice_quality`: `['Sözün yerini buluyor', 'İlk cümle yetmiyor', 'Yakınlıkta çizgin beliriyor']`
- `ui_readiness`: `compact + expanded fields present`

## 2026-04-22 Istanbul real route

### Semantic owner

- `source`: `period_voice_policy`
- `selected_meaning`: `reorientation`
- `chapter_priority.applied`: `False`

### period_reading_v1.full_text

```text
Sana ait hissettiren alan bu dönem daha fazla görünür oluyor. Ev, iç güvenlik ya da yalnız kaldığında kurduğun düzen sadece arka plan gibi kalmıyor; kimliğini ve sınırını da etkiliyor.

Evde ya da yalnız kaldığında taşıdığın duygu, dışarıdaki duruşuna daha kolay yansıyor. Duruşun ve yönün test edilebilir. Netlik azalırken zihin boşlukları doldurmak isteyebilir; varsayım yerine somut veri toplamak iyi gelir. Bunu en çok kimlik ve duruş alanında hissedebilirsin; etkisi para ve özdeğer tarafına da taşabilir. Yakın çevrendeki ses bu dönem daha görünür hale geliyor.

Burada dikkat etmen gereken yer, küçük cümlelerin ağırlığı tarafında büyüyen tepkiyi bütün hikayenin yerine koymamak.

Bu sana içeride hissettiğin şeyle dışarıda gösterdiğin duruşu aynı hatta toplamayı öğretiyor.
```

### period_signal_lines_v1 cards

#### 1. İçeride olan dışarıya taşıyor

- `preview`: Sana ait hissettiren alan, dışarıda nasıl durduğunu daha doğrudan etkiliyor. Evde ya da yalnız kaldığında tuttuğun ritim gizli kalmıyor.
- `body`: İç güvenlik ya da yalnız kaldığında kurduğun düzen şu ara arka plan gibi durmuyor. İçeride taşıdığın duygu, dışarıdaki yüzüne ve sınırına daha çabuk yansıyor. Bu yüzden meseleyi sadece dışarıdaki duruşta çözmeye çalışmak yetmiyor. Ne kadarını gerçekten kendin için tuttuğunu ayırdığında, kimliğin de daha sakin bir yerden yerleşiyor.
- `theme_palette`: `neptune_blur_or_sensitivity`
- `domain_palette`: `home_family_inner_security`
- `narrative_move`: `home_inner_safety`
- `evidence_refs`: `[{'event_id': '88bc98188b2f7931360493237881969004d50662', 'role': 'builder', 'domain': 'identity', 'house_scene': 'house_1'}, {'event_id': 'f20ef9eb9742c7eb0940794301fee6ab2a171965', 'role': 'peak', 'domain': 'identity', 'house_scene': 'house_1'}, {'event_id': '5c094e3bd122d16ecf5d3fe427057c9ed74a73f5', 'role': 'peak', 'domain': 'identity', 'house_scene': 'house_1'}]`
- `source_event_ids`: `['88bc98188b2f7931360493237881969004d50662', 'f20ef9eb9742c7eb0940794301fee6ab2a171965', '5c094e3bd122d16ecf5d3fe427057c9ed74a73f5']`
- `context_used.summary`: semantic=`reorientation`, manifestation=`yakın çevrendeki ses`

#### 2. Netlik aceleye gelmiyor

- `preview`: Her boşluğu hemen cevapla kapatma isteği artıyor. Ama bu kez hızlı netlik değil, doğru ayıklama daha çok şey söylüyor.
- `body`: Bazı anlarda neye net cevap vereceğini seçmek zorlaşıyor. Zihin boşluğu hızla doldurmak istese de, ilk cümle bazen sadece tedirginliği taşıyor. Burada bulanıklığı düşman gibi görmek yerine, hangi parçanın gerçekten sana ait olduğunu ayırmak önemli. Netliğin geç gelmesi, yanlış bir cevaba erkenden tutunmaktan daha dürüst olabiliyor.
- `theme_palette`: `neptune_blur_or_sensitivity`
- `domain_palette`: `home_family_inner_security`
- `narrative_move`: `clarification`
- `evidence_refs`: `[{'event_id': '88bc98188b2f7931360493237881969004d50662', 'role': 'builder', 'domain': 'identity', 'house_scene': 'house_1'}]`
- `source_event_ids`: `['88bc98188b2f7931360493237881969004d50662']`
- `context_used.summary`: semantic=`reorientation`, manifestation=`yakın çevrendeki ses`

#### 3. İlk cümle yetmiyor

- `preview`: Boşluğu hemen dolduran cevap, içerideki gerçek yerini tam taşımıyor. Biraz durduğunda ne söylemek istediğin daha net çıkıyor.
- `body`: Yarım kalmış konuşmalar ya da kısa mesajlar bu ara sandığından fazla iz bırakıyor. İlk tepkinle son sözünün aynı olmadığını daha çabuk fark ediyorsun. Özellikle küçük cümlelerin ağırlığı artarken, aceleyle kurduğun ton bütün hikâyenin yerine geçebiliyor. Bir nefeslik duraksama burada zayıflık değil; cümleni gerçekten seçtiğin yer.
- `theme_palette`: `uranus_change`
- `domain_palette`: `mind_communication_learning`
- `narrative_move`: `integration`
- `evidence_refs`: `[{'event_id': 'f8f11ffebcfda30f4a64126627cee7aba340aae4', 'role': 'builder', 'domain': 'mind', 'house_scene': 'house_3'}]`
- `source_event_ids`: `['f8f11ffebcfda30f4a64126627cee7aba340aae4']`
- `context_used.summary`: semantic=`reorientation`, manifestation=`yakın çevrendeki ses`

#### 4. Bir cümle daha sade çıkıyor

- `preview`: Söylemek istediğin şey bazen fazla uzamadan yerini buluyor. Mesajı taşımak için artık o kadar çok cümle gerekmiyor.
- `body`: Bazı konuşmalarda doğru kelime beklediğinden daha çabuk beliriyor. Boşluğu uzun açıklamalarla kapatmak yerine, tek bir cümle daha sade çıkıyor. Bu sadeleşme seni eksiltmiyor; ne demek istediğini daha net duyuruyor. Yakın çevrende ya da mesajlarda, az zorlanan söz bazen en güçlü duruşu taşıyor.
- `theme_palette`: `node_direction`
- `domain_palette`: `mind_communication_learning`
- `narrative_move`: `support`
- `evidence_refs`: `[{'event_id': 'f20ef9eb9742c7eb0940794301fee6ab2a171965', 'role': 'peak', 'domain': 'identity', 'house_scene': 'house_1'}, {'event_id': '5c094e3bd122d16ecf5d3fe427057c9ed74a73f5', 'role': 'peak', 'domain': 'identity', 'house_scene': 'house_1'}, {'event_id': 'f8f11ffebcfda30f4a64126627cee7aba340aae4', 'role': 'builder', 'domain': 'mind', 'house_scene': 'house_3'}]`
- `source_event_ids`: `['f20ef9eb9742c7eb0940794301fee6ab2a171965', '5c094e3bd122d16ecf5d3fe427057c9ed74a73f5', 'f8f11ffebcfda30f4a64126627cee7aba340aae4']`
- `context_used.summary`: semantic=`reorientation`, manifestation=`yakın çevrendeki ses`

### Checks

- `blocked_source_check`: `{'used_old_blocks': False, 'used_daily_body': False, 'used_best_times_score': False, 'used_story_tracks_as_owner': False, 'used_event_story_map_as_owner': False, 'used_profile_v8_as_authority': False, 'used_personality_imprint_as_authority': False, 'used_meaning_graph_v1_1_as_authority': False}`
- `voice_quality`: `['İçeride olan dışarıya taşıyor', 'Netlik aceleye gelmiyor', 'İlk cümle yetmiyor', 'Bir cümle daha sade çıkıyor']`
- `ui_readiness`: `compact + expanded fields present`

## Cancer 8th Saturn return fixture

### Semantic owner

- `source`: `life_chapter`
- `selected_meaning`: `shared_emotional_territory`
- `chapter_priority.applied`: `False`

### period_reading_v1.full_text

```text
Mahrem konuşmalarda ve birlikte taşınan yüklerde neyin ortak, neyin tek başına kaldığı daha görünür oluyor.

Bazı şeyleri içeride tutmak seni güvende hissettirmiş olabilir. Ama güvenin sadece susarak değil, neyi paylaşacağını ve hangi sınırın sana ait olduğunu söyleyerek de kurulabileceğini görüyorsun.

Bu sana hem paylaşılanı taşıyan hem özel alanı koruyan daha dayanıklı bir yakınlık kurduruyor.
```

### period_signal_lines_v1 cards

#### 1. Neyin sana ait olduğu

- `preview`: Paylaşılan yük ile tek başına taşıdığın şey aynı yerde durmuyor. Bunu ayırdıkça yakınlık daha sağlam bir zemine oturuyor.
- `body`: Mahrem konuşmaların ya da birlikte taşınan yüklerin içinde, sessizce üstlendiğin şey daha görünür. Güveni sadece susarak değil, neyi taşıyacağını ve neyi geri vereceğini söyleyerek de kurabiliyorsun. Burada fazlalığı atmak değil, paylaşılanı daha doğru ölçüyle taşımak var. Sınırın netleştikçe yakınlık da daha dayanıklı bir forma yerleşiyor.
- `theme_palette`: `saturn_maturation`
- `domain_palette`: `relationship_intimacy_agreements`
- `narrative_move`: `boundary`
- `evidence_refs`: `[{'event_id': 'evt-saturn-return-cancer-8', 'role': 'builder', 'domain': None, 'house_scene': None}]`
- `source_event_ids`: `['evt-saturn-return-cancer-8']`
- `context_used.summary`: semantic=`shared_emotional_territory`, manifestation=`mahrem konuşmalar, birlikte taşınan yükler, duygusal borç ve sorumluluğun sessizce paylaşıldığı anlar`

#### 2. Yakınlıkta çizgin beliriyor

- `preview`: Yan yana dururken kendi cümleni fazla kısmadan da kalabildiğin anlar çoğalıyor. İlişki burada sadece uyumla yürümüyor.
- `body`: Karşı tarafı kollarken kendi yerini sessizce geri çektiğin anlar daha görünür. Burada mesele sertleşmek değil; ne hissettiğini fazla dolandırmadan söyleyebilmek. Sıcak kalırken çizgini de koruduğunda, yakınlık savunmaya değil açıklığa yaslanıyor. Bu da ilişkide seni silmeden kalmanın başka bir yolunu açıyor.
- `theme_palette`: `saturn_maturation`
- `domain_palette`: `relationship_intimacy_agreements`
- `narrative_move`: `relationship_mirror`
- `evidence_refs`: `[{'event_id': 'evt-saturn-return-cancer-8', 'role': 'builder', 'domain': None, 'house_scene': None}]`
- `source_event_ids`: `['evt-saturn-return-cancer-8']`
- `context_used.summary`: semantic=`shared_emotional_territory`, manifestation=`ne kadarını taşıyacağını ayırdığın anlar`

#### 3. Güven daha açık kuruluyor

- `preview`: Mahrem olanı korurken her şeyi sessizce taşımak gerekmiyor. Paylaşılan yük adını buldukça yakınlık daha sakin akıyor.
- `body`: Bazı şeyleri tek başına sırtlanmak seni güvende tutmuş olabilir. Şimdi paylaşılan yükü, mahrem olanı dağıtmadan da konuşabildiğin bir yer açılıyor. Kısa bir açıklık, neyin sana ait neyin ortak olduğunu daha rahat ayırıyor. Yakınlık burada büyük bir itirafla değil, güveni daha açık kurabildiğin küçük anlarla güçleniyor.
- `theme_palette`: `saturn_maturation`
- `domain_palette`: `mind_communication_learning`
- `narrative_move`: `support`
- `evidence_refs`: `[{'event_id': 'evt-saturn-return-cancer-8', 'role': 'builder', 'domain': None, 'house_scene': None}]`
- `source_event_ids`: `['evt-saturn-return-cancer-8']`
- `context_used.summary`: semantic=`shared_emotional_territory`, manifestation=`güvenin daha açık ama dağılmadan kurulduğu anlar`

### Checks

- `blocked_source_check`: `{'used_old_blocks': False, 'used_daily_body': False, 'used_best_times_score': False, 'used_story_tracks_as_owner': False, 'used_event_story_map_as_owner': False, 'used_profile_v8_as_authority': False, 'used_personality_imprint_as_authority': False, 'used_meaning_graph_v1_1_as_authority': False}`
- `voice_quality`: `['Neyin sana ait olduğu', 'Yakınlıkta çizgin beliriyor', 'Güven daha açık kuruluyor']`
- `ui_readiness`: `compact + expanded fields present`

## Nodal Aries/Libra fixture

### Semantic owner

- `source`: `life_chapter`
- `selected_meaning`: `directional_self_definition`
- `chapter_priority.applied`: `False`

### period_reading_v1.full_text

```text
Yan yana dururken kendi sözünü ne kadar ayarladığını daha net fark ediyorsun.

İlişkiyi korumak için kendini kısmana gerek kalmadan, yönünü daha açık söylemeyi öğreniyorsun. Bu kopmak değil; onayın içinde erimeden kendi çizgini de masada tutmak.

Bu dönem sende onay arayışına çökmeyen daha doğrudan bir yön duygusu kuruyor.
```

### period_signal_lines_v1 cards

#### 1. Yönünü daha açık söylüyorsun

- `preview`: İlişkiyi korumak için kendi yönünü kısmak eskisi kadar kolay gelmiyor. Sözün biraz daha doğrudanlaşıyor.
- `body`: Yan yana dururken kendini ne kadar çabuk ayarladığını daha net görüyorsun. Burada kopmak ya da sertleşmek değil, kendi çizgini saklamadan söylemek öne çıkıyor. Onayın içinde erimeden de masada kalabildiğinde, yönün sadece içeride değil dışarıda da belirginleşiyor. Bu da seni ilişkiyi korurken kendini silmeyen bir çizgiye taşıyor.
- `theme_palette`: `node_direction`
- `domain_palette`: `relationship_intimacy_agreements`
- `narrative_move`: `choice`
- `evidence_refs`: `[{'event_id': 'evt-nodal-return-aries', 'role': 'builder', 'domain': None, 'house_scene': None}]`
- `source_event_ids`: `['evt-nodal-return-aries']`
- `context_used.summary`: semantic=`directional_self_definition`, manifestation=`yan yana dururken kendi sözünü ayarladığın anlar, yön seçimi, görünür pozisyon alma`

#### 2. Yakınlıkta çizgin beliriyor

- `preview`: Yan yana dururken kendi cümleni fazla kısmadan da kalabildiğin anlar çoğalıyor. İlişki burada sadece uyumla yürümüyor.
- `body`: Karşı tarafı kollarken kendi yerini sessizce geri çektiğin anlar daha görünür. Burada mesele sertleşmek değil; ne hissettiğini fazla dolandırmadan söyleyebilmek. Sıcak kalırken çizgini de koruduğunda, yakınlık savunmaya değil açıklığa yaslanıyor. Bu da ilişkide seni silmeden kalmanın başka bir yolunu açıyor.
- `theme_palette`: `node_direction`
- `domain_palette`: `relationship_intimacy_agreements`
- `narrative_move`: `relationship_mirror`
- `evidence_refs`: `[{'event_id': 'evt-nodal-return-aries', 'role': 'builder', 'domain': None, 'house_scene': None}]`
- `source_event_ids`: `['evt-nodal-return-aries']`
- `context_used.summary`: semantic=`directional_self_definition`, manifestation=`uyumu korurken kendini kısmadığın anlar`

#### 3. Kendini kısmadan kalıyorsun

- `preview`: Onay aramadan da sıcak kalabildiğin anlar çoğalıyor. Aynı masada dururken yönün daha az geri çekiliyor.
- `body`: Bazen ilişkiyi korumak için cümleni hemen yumuşatmak kolay geliyor. Şimdi aynı masada kalırken kendi çizgini de bırakmıyorsun. Küçük bir netlik, onay beklemeden de sıcaklığın bozulmadığını gösteriyor. Yönünü saklamadığında ilişki sertleşmiyor; sadece seni daha doğru yerden görüyor.
- `theme_palette`: `node_direction`
- `domain_palette`: `mind_communication_learning`
- `narrative_move`: `support`
- `evidence_refs`: `[{'event_id': 'evt-nodal-return-aries', 'role': 'builder', 'domain': None, 'house_scene': None}]`
- `source_event_ids`: `['evt-nodal-return-aries']`
- `context_used.summary`: semantic=`directional_self_definition`, manifestation=`kendi çizginle masada kaldığın anlar`

### Checks

- `blocked_source_check`: `{'used_old_blocks': False, 'used_daily_body': False, 'used_best_times_score': False, 'used_story_tracks_as_owner': False, 'used_event_story_map_as_owner': False, 'used_profile_v8_as_authority': False, 'used_personality_imprint_as_authority': False, 'used_meaning_graph_v1_1_as_authority': False}`
- `voice_quality`: `['Yönünü daha açık söylüyorsun', 'Yakınlıkta çizgin beliriyor', 'Kendini kısmadan kalıyorsun']`
- `ui_readiness`: `compact + expanded fields present`

## 2026-05-08 supportive/opening route

### Semantic owner

- `source`: `period_voice_policy`
- `selected_meaning`: `reorientation`
- `chapter_priority.applied`: `False`

### period_reading_v1.full_text

```text
Sana ait hissettiren alan bu dönem daha fazla görünür oluyor. Ev, iç güvenlik ya da yalnız kaldığında kurduğun düzen sadece arka plan gibi kalmıyor; kimliğini ve sınırını da etkiliyor.

Bu, kendini zorlamak değil. Özellikle yakın çevrendeki ses tarafında büyüyen şeyi hemen sonuca çevirmek de değil. Evde ya da yalnız kaldığında taşıdığın duygu, dışarıdaki duruşuna daha kolay yansıyor. Duruşun ve yönün test edilebilir. Netlik azalırken zihin boşlukları doldurmak isteyebilir; varsayım yerine somut veri toplamak iyi gelir. Bunu en çok kimlik ve duruş alanında hissedebilirsin; etkisi para ve özdeğer tarafına da taşabilir. Küçük cümlelerin ağırlığı bu dönem daha görünür hale geliyor. Bu dönem onlar birbirine daha yakın duruyor.

Burada dikkat etmen gereken yer, yakın çevrendeki ses içinden yükselen şeyi hemen sonuca çevirmemek. Daha bütünlüklü bir yön kuruyorsun; içeride ayrı konuşan parçaları aynı cümlede topluyorsun.

Bu sana içeride hissettiğin şeyle dışarıda gösterdiğin duruşu aynı hatta toplamayı öğretiyor.
```

### period_signal_lines_v1 cards

#### 1. İçeride olan dışarıya taşıyor

- `preview`: Sana ait hissettiren alan, dışarıda nasıl durduğunu daha doğrudan etkiliyor. Evde ya da yalnız kaldığında tuttuğun ritim gizli kalmıyor.
- `body`: İç güvenlik ya da yalnız kaldığında kurduğun düzen şu ara arka plan gibi durmuyor. İçeride taşıdığın duygu, dışarıdaki yüzüne ve sınırına daha çabuk yansıyor. Bu yüzden meseleyi sadece dışarıdaki duruşta çözmeye çalışmak yetmiyor. Ne kadarını gerçekten kendin için tuttuğunu ayırdığında, kimliğin de daha sakin bir yerden yerleşiyor.
- `theme_palette`: `neptune_blur_or_sensitivity`
- `domain_palette`: `home_family_inner_security`
- `narrative_move`: `home_inner_safety`
- `evidence_refs`: `[{'event_id': '88bc98188b2f7931360493237881969004d50662', 'role': 'builder', 'domain': 'identity', 'house_scene': 'house_1'}, {'event_id': 'f20ef9eb9742c7eb0940794301fee6ab2a171965', 'role': 'peak', 'domain': 'identity', 'house_scene': 'house_1'}]`
- `source_event_ids`: `['88bc98188b2f7931360493237881969004d50662', 'f20ef9eb9742c7eb0940794301fee6ab2a171965']`
- `context_used.summary`: semantic=`reorientation`, manifestation=`küçük cümlelerin ağırlığı`

#### 2. Netlik aceleye gelmiyor

- `preview`: Her boşluğu hemen cevapla kapatma isteği artıyor. Ama bu kez hızlı netlik değil, doğru ayıklama daha çok şey söylüyor.
- `body`: Bazı anlarda neye net cevap vereceğini seçmek zorlaşıyor. Zihin boşluğu hızla doldurmak istese de, ilk cümle bazen sadece tedirginliği taşıyor. Burada bulanıklığı düşman gibi görmek yerine, hangi parçanın gerçekten sana ait olduğunu ayırmak önemli. Netliğin geç gelmesi, yanlış bir cevaba erkenden tutunmaktan daha dürüst olabiliyor.
- `theme_palette`: `neptune_blur_or_sensitivity`
- `domain_palette`: `home_family_inner_security`
- `narrative_move`: `clarification`
- `evidence_refs`: `[{'event_id': '88bc98188b2f7931360493237881969004d50662', 'role': 'builder', 'domain': 'identity', 'house_scene': 'house_1'}]`
- `source_event_ids`: `['88bc98188b2f7931360493237881969004d50662']`
- `context_used.summary`: semantic=`reorientation`, manifestation=`küçük cümlelerin ağırlığı`

#### 3. İlk cümle yetmiyor

- `preview`: Boşluğu hemen dolduran cevap, içerideki gerçek yerini tam taşımıyor. Biraz durduğunda ne söylemek istediğin daha net çıkıyor.
- `body`: Yarım kalmış konuşmalar ya da kısa mesajlar bu ara sandığından fazla iz bırakıyor. İlk tepkinle son sözünün aynı olmadığını daha çabuk fark ediyorsun. Özellikle küçük cümlelerin ağırlığı artarken, aceleyle kurduğun ton bütün hikâyenin yerine geçebiliyor. Bir nefeslik duraksama burada zayıflık değil; cümleni gerçekten seçtiğin yer.
- `theme_palette`: `pluto_depth`
- `domain_palette`: `mind_communication_learning`
- `narrative_move`: `integration`
- `evidence_refs`: `[{'event_id': 'b66e8f9d1fe74f30df6447f63e57b0b2e99e1f19', 'role': 'builder', 'domain': 'mind', 'house_scene': 'house_3'}, {'event_id': '2413a54cce08948db730f9bbdecab1038ba8e6e8', 'role': 'peak', 'domain': 'mind', 'house_scene': 'house_3'}]`
- `source_event_ids`: `['b66e8f9d1fe74f30df6447f63e57b0b2e99e1f19', '2413a54cce08948db730f9bbdecab1038ba8e6e8']`
- `context_used.summary`: semantic=`reorientation`, manifestation=`küçük cümlelerin ağırlığı`

#### 4. Sözün daha az zorlanıyor

- `preview`: Küçük cümlelerin yükü biraz hafifliyor. Aynı şeyi söylemek için artık o kadar sert bir ton gerekmiyor.
- `body`: Bazen kısa bir mesaj ya da tek bir cevap, düşündüğünden daha temiz bir yere oturuyor. Kelimeleri fazla sıkıştırmadığında, ne demek istediğin daha rahat anlaşılıyor. Bu yumuşama seni belirsiz bırakmıyor; tam tersine sözünü daha net taşıyor. Yakın çevrende, az zorlanan cümle bu kez daha uzun bir yankı bırakıyor.
- `theme_palette`: `node_direction`
- `domain_palette`: `mind_communication_learning`
- `narrative_move`: `support`
- `evidence_refs`: `[{'event_id': 'f20ef9eb9742c7eb0940794301fee6ab2a171965', 'role': 'peak', 'domain': 'identity', 'house_scene': 'house_1'}, {'event_id': '2413a54cce08948db730f9bbdecab1038ba8e6e8', 'role': 'peak', 'domain': 'mind', 'house_scene': 'house_3'}]`
- `source_event_ids`: `['f20ef9eb9742c7eb0940794301fee6ab2a171965', '2413a54cce08948db730f9bbdecab1038ba8e6e8']`
- `context_used.summary`: semantic=`reorientation`, manifestation=`küçük cümlelerin ağırlığı`

### Checks

- `blocked_source_check`: `{'used_old_blocks': False, 'used_daily_body': False, 'used_best_times_score': False, 'used_story_tracks_as_owner': False, 'used_event_story_map_as_owner': False, 'used_profile_v8_as_authority': False, 'used_personality_imprint_as_authority': False, 'used_meaning_graph_v1_1_as_authority': False}`
- `voice_quality`: `['İçeride olan dışarıya taşıyor', 'Netlik aceleye gelmiyor', 'İlk cümle yetmiyor', 'Sözün daha az zorlanıyor']`
- `ui_readiness`: `compact + expanded fields present`
