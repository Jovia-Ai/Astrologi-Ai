# Engine Gercekte Sunu Uretiyor

Kaynak artifact'lar:

- `docs/system/_generated_outputs/live_profile_narrative_projection_v1_1996-12-28_07-10_istanbul.json`
- `docs/system/_generated_outputs/live_profile_narrative_projection_v1_1998-09-12_07-30_adana.json`
- `docs/system/_generated_outputs/live_profile_narrative_projection_v1_2019-11-03_23-40_istanbul.json`

Bu tablo `profile_narrative_projection_v1` uzerinden cikarildi.

Okuma kurali:

- `visible cards` = `core_blocks + extra_blocks`
- `candidate packets` = `traceability.natal_promise_cluster_plan_v1.candidate_packets`
- `hidden/private` sayimi yalnizca packet/cluster id, subtype ve teknik anchor uzerindeki acik `hidden/private/12h/home/roots` isaretlerinden yapildi
- `expandable` = evidence yogunlugu ve cluster derinligi slide acmak icin yeterli gorunen kart
- `compressed` = tek packet, dusuk evidence, dar anchor; ayrica aux tekrarlar compression adayi
- `borderline` = semantik olarak anlamli ama evidence derinligi slide acmak icin net degil

## Ozet Tablo

| Chart | Visible cards | Visible semantic clusters | Candidate packets | Visible domain family'ler | Theoretical-only promise_type | Hidden/private visible / candidate | Visible gift / friction / mechanism | Candidate gift / friction / mechanism | Expandable / Borderline / Compressed | Duplicate risk |
| --- | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Istanbul 1996-12-28 07:10 | 10 | 7 | 11 | `career`, `identity`, `mind`, `relationship` | `career_signature` | `0 / 1` | `6 / 1 / 3` | `7 / 1 / 3` | `6 / 4 / 0` | Yuksek |
| Adana 1998-09-12 07:30 | 10 | 10 | 22 | `career`, `community`, `identity`, `mind`, `relationship` | `mind_style` | `0 / 2` | `6 / 3 / 1` | `9 / 8 / 5` | `3 / 1 / 6` | Dusuk, ama id-collision var |
| Istanbul 2019-11-03 23:40 | 4 | 4 | 14 | `career`, `identity`, `mind`, `relationship` | `creative_signature`, `home_family_signature`, `mind_style`, `need`, `relationship_need` | `0 / 0` | `3 / 1 / 0` | `8 / 2 / 4` | `1 / 1 / 2` | Dusuk, ama duplicate aux id var |

Ana gozlem:

- Uc chart'in hicbirinde `domain_family` duzeyinde "teorik ama hic yok" bir bosluk yok; problem family yoklugu degil, ayni family icinde hangi packet'larin gercekten gorunur oldugu.
- Asil fark promise-type ve evidence yogunlugunda cikiyor.
- 1996 chart'i semantic cluster tekrarina en yakin chart.
- 1998 chart'i en zengin candidate inventory'ye sahip chart ama gorunur yuzeyin buyuk kismi compressed.
- 2019 chart'i en ince inventory'ye sahip chart; burada family coverage tamam ama depth dusuk.

## Chart 1: Istanbul 1996-12-28 07:10

### Engine ne uretiyor?

| Alan | Gercek durum |
| --- | --- |
| Visible cards | `10` |
| Semantic cluster sayisi | `7` |
| Candidate packet sayisi | `11` |
| Visible family'ler | `identity`, `relationship`, `mind`, `career` |
| Theoretical-only family | Yok |
| Theoretical-only promise_type | `career_signature` |
| Hidden/private | Visible `0`, candidate `1` |
| Hidden/private candidate | `venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact` |

### Visible kart dagilimi

| packet_id | Cluster | Surface role | promise_type | Evidence tier | Not |
| --- | --- | --- | --- | --- | --- |
| `capricorn_asc_sun_1h_composed_self_construction` | `identity_self_construction` | `public_main` | `behavior_reflex` | `expandable` | Yuksek evidence, cok anchor, acilabilir |
| `moon_leo_8h_deep_proud_heart` | `relationship_attachment_architecture` | `public_main` | `love_style` | `expandable` | Ana iliski cluster'i |
| `saturn_3h_aries_speech_decision_language` | `mind_speech_decision_language` | `public_main` | `mind_style` | `expandable` | Zihin hattinin ana karti |
| `chiron_conjunct_mc_visibility_wound_to_voice_chart_exact` | `career_healing_voice` | `public_main` | `wound_to_gift` | `borderline` | Public-main ama evidence sathi |
| `saturn_trine_pluto_deep_resilience_chart_exact` | `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact` | `public_main` | `gift` | `borderline` | Semantik iyi, evidence dar |
| `moon_trine_venus_emotional_warmth` | `relationship_attachment_architecture` | `public_main` | `love_style` | `expandable` | Ayni iliski cluster'inin ikinci guclu varyanti |
| `saturn_3h_aries_speech_decision_language_behavior_reflex_overlay` | `mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact` | `detail` | `mind_style` | `expandable` | Detail cluster'dan ekstra block'a siziyor |
| `saturn_sextile_uranus_structured_originality_identity_chart_exact` | `identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact` | `detail` | `gift` | `borderline` | Detail adayi, ama tek basin yeterince agir degil |
| `mercury_conjunct_jupiter_big_mind_chart_exact` | `mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact` | `detail` | `gift` | `borderline` | Ayrisiyor ama evidence daha kisa |
| `moon_trine_venus_emotional_warmth_aux` | `relationship_attachment_architecture` | `public_main` | `love_style` | `expandable` | Aux tekrar; semantic tekrar riski yuksek |

### Slide'a acilabilir vs compressed kalmali

- Expandable:
  `capricorn_asc_sun_1h_composed_self_construction`, `moon_leo_8h_deep_proud_heart`, `saturn_3h_aries_speech_decision_language`, `moon_trine_venus_emotional_warmth`, `saturn_3h_aries_speech_decision_language_behavior_reflex_overlay`, `moon_trine_venus_emotional_warmth_aux`
- Borderline:
  `chiron_conjunct_mc_visibility_wound_to_voice_chart_exact`, `saturn_trine_pluto_deep_resilience_chart_exact`, `saturn_sextile_uranus_structured_originality_identity_chart_exact`, `mercury_conjunct_jupiter_big_mind_chart_exact`
- Compressed:
  Net compressed kart cikmadi; sorun evidence yoklugundan cok semantic tekrar.

### Duplicate-semantic riski

En riskli eslesmeler:

- `moon_leo_8h_deep_proud_heart` vs `moon_trine_venus_emotional_warmth`
- `moon_leo_8h_deep_proud_heart` vs `moon_trine_venus_emotional_warmth_aux`
- `moon_trine_venus_emotional_warmth` vs `moon_trine_venus_emotional_warmth_aux`
- `saturn_3h_aries_speech_decision_language_behavior_reflex_overlay` vs `mercury_conjunct_jupiter_big_mind_chart_exact`

Net yorum:

- Engine 10 kart basiyor ama bunlar 7 semantic cluster'a denk dusuyor.
- Icerik tekrarinin ana kaynagi `relationship_attachment_architecture` cluster'inin uc ayri kart olarak yuzeye gelmesi.
- Mind tarafinda da `detail` cluster'in extra block lane'ine sizmasi var; bu coverage'yi artirmaktan cok ayni zihinsel hattin tekrarini buyutuyor.

## Chart 2: Adana 1998-09-12 07:30

### Engine ne uretiyor?

| Alan | Gercek durum |
| --- | --- |
| Visible cards | `10` |
| Semantic cluster sayisi | `10` |
| Candidate packet sayisi | `22` |
| Visible family'ler | `mind`, `identity`, `career`, `relationship`, `community` |
| Theoretical-only family | Yok |
| Theoretical-only promise_type | `mind_style` |
| Hidden/private | Visible `0`, candidate `2` |
| Hidden/private candidate | `mercury_virgo_12h_private_analytical_mind_chart_exact`, `sun_virgo_12h_quiet_inner_self_chart_exact` |

### Visible kart dagilimi

| packet_id | Cluster | Surface role | promise_type | Evidence tier | Not |
| --- | --- | --- | --- | --- | --- |
| `mercury_conjunct_venus_refined_relational_language` | `mind_gift_like_mercury_conjunct_venus_refined_relational_language` | `public_main` | `gift` | `expandable` | Gercekten acilabilir az sayidaki karttan biri |
| `mars_square_chiron_tender_courage` | `identity_wound_like_mars_square_chiron_tender_courage` | `public_main` | `wound_to_gift` | `expandable` | Kimlik/yaralanma hattinda guclu |
| `mc_cancer_moon_gemini_9h_teaching_voice_chart_exact` | `career_career_like_mc_cancer_moon_gemini_9h_teaching_voice_chart_exact` | `public_main` | `career_signature` | `compressed` | Public-main ama tek packet, zayif kanit |
| `venus_square_pluto_intense_love_chart_exact` | `relationship_love_like_venus_square_pluto_intense_love_chart_exact` | `public_main` | `love_style` | `compressed` | Yogunluk var ama kanit derinligi zayif |
| `mars_leo_11h_warm_visible_drive_community_chart_exact` | `community_identity_like_mars_leo_11h_warm_visible_drive_community_chart_exact` | `public_main` | `drive` | `compressed` | Community lane'i aciliyor ama ince |
| `moon_square_mercury_emotion_mind_friction_aux` | `mind_wound_like_moon_square_mercury_emotion_mind_friction_aux` | `detail` | `wound_to_gift` ya da `gift` collision | `borderline` | Ayni id ile iki farkli payload var |
| `moon_square_venus_need_affection_friction` | `relationship_wound_like_moon_square_venus_need_affection_friction` | `detail` | `wound_to_gift` | `expandable` | Detail lane icinde en guclu adaylardan |
| `libra_asc_venus_chart_ruler_chart_exact` | `identity_identity_like_libra_asc_venus_chart_ruler_chart_exact` | `detail` | `behavior_reflex` | `compressed` | Detay olarak kalmali |
| `saturn_taurus_8h_steady_public_maturity_chart_exact` | `career_career_like_saturn_taurus_8h_steady_public_maturity_chart_exact` | `detail` | `career_signature` | `compressed` | Kariyer ama ince evidence |
| `mars_leo_11h_warm_visible_drive_chart_exact` | `relationship_identity_like_mars_leo_11h_warm_visible_drive_chart_exact` | `detail` | `drive` | `compressed` | Community/relationship tonlari birbirine yaklasiyor |

### Slide'a acilabilir vs compressed kalmali

- Expandable:
  `mercury_conjunct_venus_refined_relational_language`, `mars_square_chiron_tender_courage`, `moon_square_venus_need_affection_friction`
- Borderline:
  `moon_square_mercury_emotion_mind_friction_aux`
- Compressed:
  `mc_cancer_moon_gemini_9h_teaching_voice_chart_exact`, `venus_square_pluto_intense_love_chart_exact`, `mars_leo_11h_warm_visible_drive_community_chart_exact`, `libra_asc_venus_chart_ruler_chart_exact`, `saturn_taurus_8h_steady_public_maturity_chart_exact`, `mars_leo_11h_warm_visible_drive_chart_exact`

### Duplicate-semantic riski

Kartlar arasi acik lexical overlap dusuk. Asil risk duplicate headline degil, inventory seviyesinde `id-collision`:

- `moon_square_mercury_emotion_mind_friction_aux` candidate inventory icinde iki farkli payload ile geliyor
  - bir versiyon `mind/gift` tonunda
  - diger versiyon `relationship/wound_to_gift` tonunda

Net yorum:

- Engine burada 22 candidate packet uretiyor; yani en zengin ham stok bu chart'ta.
- Ama visible 10 kartin sadece 3'u gercekten slide acmaya yeterli.
- Family coverage kuvvetli, fakat "deep enough public card" sayisi dusuk.

## Chart 3: Istanbul 2019-11-03 23:40

### Engine ne uretiyor?

| Alan | Gercek durum |
| --- | --- |
| Visible cards | `4` |
| Semantic cluster sayisi | `4` |
| Candidate packet sayisi | `14` |
| Visible family'ler | `relationship`, `identity`, `career`, `mind` |
| Theoretical-only family | Yok |
| Theoretical-only promise_type | `creative_signature`, `home_family_signature`, `mind_style`, `need`, `relationship_need` |
| Hidden/private | Visible `0`, candidate `0` |

### Visible kart dagilimi

| packet_id | Cluster | Surface role | promise_type | Evidence tier | Not |
| --- | --- | --- | --- | --- | --- |
| `relationship_relationships` | `relationship_love_like_relationship_relationships` | `public_main` | `love_style` | `borderline` | Temel iliski karti var ama generic |
| `uranus_square_asc_venus_unsettled_outer_signal` | `identity_unsettled_outer_signal` | `public_main` | `wound_to_gift` | `expandable` | En guclu kart bu |
| `career_career_visibility` | `career_career_like_career_career_visibility` | `public_main` | `career_signature` | `compressed` | Family coverage var, depth dusuk |
| `mercury_conjunct_venus_refined_relational_language_chart_exact` | `mind_gift_like_mercury_conjunct_venus_refined_relational_language_chart_exact` | `public_main` | `gift` | `compressed` | Zihin karti var ama ince |

### Slide'a acilabilir vs compressed kalmali

- Expandable:
  `uranus_square_asc_venus_unsettled_outer_signal`
- Borderline:
  `relationship_relationships`
- Compressed:
  `career_career_visibility`, `mercury_conjunct_venus_refined_relational_language_chart_exact`

### Duplicate-semantic riski

- Visible yuzeyde belirgin semantic cakis yok.
- Candidate inventory'de `relationship_relationships_aux` duplicate id olarak iki kez duruyor; burada payload ayni gorunuyor, yani collision degil ama gereksiz tekrar.

Net yorum:

- Bu chart coverage olarak temiz: 4 kart = 4 cluster.
- Ama semantic derinlik dengesiz; sadece identity hattinda guclu bir slide-acilabilir kart var.
- Home/creative/need ailesi candidate seviyesinde var ama visible yuzeye hic cikmiyor.

## Sonuc

Urun davranisi uc chart'ta da ayni degil:

- 1996: coverage var, ama cluster tekrarindan dolayi over-rendering riski yuksek
- 1998: candidate inventory zengin, ama public kartlarin buyuk kismi compression seviyesinde
- 2019: coverage sade, ama depth dar; sadece bir kart gercekten tasiyor

En onemli teknik gercek:

- Family coverage sorunu yok
- Sorunlar daha cok:
  - ayni semantic cluster'in birden fazla visible karta donusmesi
  - evidence yetersizligi yuzunden public-main kartin bile compressed kalmasi
  - bazi chart'larda duplicate `packet_id` collision/repetition gorulmesi
