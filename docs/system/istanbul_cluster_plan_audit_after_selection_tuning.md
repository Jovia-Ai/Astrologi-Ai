# Istanbul ClusterPlan Audit After Selection Tuning

- Generated: 2026-05-11
- Source artifact: `backend/tests/_artifacts/natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json`
- Flags: `ENABLE_NATAL_PROMISE_PROJECTION_V1=true`, `ENABLE_NATAL_PROMISE_PACKET_DEBUG=true`
- Scope: source richness unchanged; only public-main selection and suppression were tuned.

## 1. candidate_inventory summary

- Total candidate packet count: `11`
- Selected packet count: `3`
- Top candidate packets:

1. `capricorn_asc_sun_1h_composed_self_construction_chart_exact`
   - domain: `identity`
   - promise_type: `behavior_reflex`
   - strength: `1.0`
   - technical_anchors: `["Yükselen · Oğlak · Güneş 1. ev", "Yükselen Oğlak", "Güneş 1. ev", "Satürn 3. ev", "1th house ruler route", "Sun conjunction Ascendant"]`
   - direct_meaning: `Dışarıda toparlanmış ve kontrollü görünmek senin için önemli olabilir.`
2. `chiron_conjunct_mc_visibility_wound_to_voice_chart_exact`
   - domain: `career`
   - promise_type: `wound_to_gift`
   - strength: `1.0`
   - technical_anchors: `["Chiron conjunct MC", "Chiron 10. ev", "MC Terazi", "Jupiter square Midheaven", "Neptune square Midheaven", "Chiron conjunct Midheaven"]`
   - direct_meaning: `Görünür olma hassasiyetini zamanla başkalarına dokunan bir sese çevirmek.`
3. `moon_leo_8h_deep_proud_heart_chart_exact`
   - domain: `relationship`
   - promise_type: `love_style`
   - strength: `1.0`
   - technical_anchors: `["Ay · 8. ev · Aslan", "7. ev Yengeç", "Ay 8. ev", "Aslan", "7th house ruler route", "Moon trine Venus"]`
   - direct_meaning: `Derin, gururlu, kolay açılmayan ama açıldığında güçlü bağlanan kalp.`
4. `moon_trine_venus_emotional_warmth_chart_exact`
   - domain: `relationship`
   - promise_type: `gift`
   - strength: `1.0`
   - technical_anchors: `["Moon trine Venus", "Ay 8. ev", "Venüs 12. ev", "7th house ruler route", "Venus conjunction Vertex"]`
   - direct_meaning: `Sevdiği şeyi yumuşatan, güzelleştiren ve korumak isteyen bir kalp.`
5. `saturn_3h_aries_speech_decision_language_chart_exact`
   - domain: `mind`
   - promise_type: `mind_style`
   - strength: `1.0`
   - technical_anchors: `["Satürn · 3. ev · Koç", "Satürn 3. ev", "Koç", "Merkür 1. ev", "Saturn in house 3 Aries", "Mercury conjunction Jupiter"]`
   - direct_meaning: `Söz, ton ve karar dili sende kimliğe yakın bir yerden çalışıyor olabilir.`
6. `saturn_sextile_uranus_structured_originality_chart_exact`
   - domain: `mind`
   - promise_type: `gift`
   - strength: `1.0`
   - technical_anchors: `["Saturn sextile Uranus", "Satürn 3. ev", "Uranüs 1. ev", "1th house ruler route", "Mercury conjunction Jupiter"]`
   - direct_meaning: `Farklı fikri sadece bulmak değil, ona çalışır bir form verebilmek.`
7. `saturn_sextile_uranus_structured_originality_identity_chart_exact`
   - domain: `identity`
   - promise_type: `gift`
   - strength: `1.0`
   - technical_anchors: `["Saturn sextile Uranus", "Yükselen Oğlak", "Uranüs 1. ev", "Ascendant Capricorn"]`
   - direct_meaning: `Farklı fikri sadece bulmak değil, ona çalışır bir form verebilmek.`
8. `saturn_trine_pluto_deep_resilience_chart_exact`
   - domain: `identity`
   - promise_type: `gift`
   - strength: `1.0`
   - technical_anchors: `["Saturn trine Pluto", "Sun square Saturn", "Mars opposite Saturn", "Mars opposition Saturn"]`
   - direct_meaning: `Baskı geldiğinde bile yapıyı koruyup içerden dönüşebilmek.`
9. `venus_sagittarius_12h_hidden_expansive_love_chart_exact`
   - domain: `career`
   - promise_type: `career_signature`
   - strength: `1.0`
   - technical_anchors: `["Venüs · 12. ev · Yay", "MC Terazi", "Venüs 12. ev", "Yay", "10th house ruler route", "Jupiter square Midheaven"]`
   - direct_meaning: `Üretim ve görünürlük sende önce içeride olgunlaşmak isteyebilir.`
10. `venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact`
    - domain: `relationship`
    - promise_type: `career_signature`
    - strength: `1.0`
    - technical_anchors: `["Venüs · 12. ev · Yay", "Venüs 12. ev", "Yay", "Moon trine Venus", "Venus in house 12", "Venus conjunction Vertex"]`
    - direct_meaning: `Üretim ve görünürlük sende önce içeride olgunlaşmak isteyebilir.`
11. `mercury_conjunct_jupiter_big_mind_chart_exact`
    - domain: `mind`
    - promise_type: `gift`
    - strength: `0.9279`
    - technical_anchors: `["Mercury conjunction Jupiter", "Merkür 1. ev", "Jüpiter 1. ev", "3th house ruler route", "Mercury conjunct Jupiter"]`
    - direct_meaning: `Parçaları tek tek görmekten çok, aralarındaki anlamı kuran bir zihin.`

## 2. focus_map

### `career`
- score: `1.0`
- tier: `strong`
- packet_ids: `["chiron_conjunct_mc_visibility_wound_to_voice_chart_exact", "venus_sagittarius_12h_hidden_expansive_love_chart_exact"]`
- evidence_summary: `["chart ruler support", "angular support", "luminary support", "house-chain support"]`
- scoring_breakdown: `{"packet_strength_sum": 0.8511, "chart_ruler": 1.0, "angularity": 1.0, "luminary": 0.5, "house_chain": 0.5, "repeated_support": 0.8, "contradiction": 0.0, "archetype_confidence": 0.8595}`

### `identity`
- score: `0.8762`
- tier: `strong`
- packet_ids: `["capricorn_asc_sun_1h_composed_self_construction_chart_exact", "saturn_sextile_uranus_structured_originality_identity_chart_exact", "saturn_trine_pluto_deep_resilience_chart_exact"]`
- evidence_summary: `["chart ruler support", "angular support", "luminary support", "house-chain support"]`
- scoring_breakdown: `{"packet_strength_sum": 1.0, "chart_ruler": 0.6667, "angularity": 0.6667, "luminary": 0.6667, "house_chain": 0.3333, "repeated_support": 1.0, "contradiction": 0.2767, "archetype_confidence": 0.895}`

### `mind`
- score: `0.7737`
- tier: `medium_strong`
- packet_ids: `["saturn_3h_aries_speech_decision_language_chart_exact", "saturn_sextile_uranus_structured_originality_chart_exact", "mercury_conjunct_jupiter_big_mind_chart_exact"]`
- evidence_summary: `["angular support", "house-chain support", "repeated packet support"]`
- scoring_breakdown: `{"packet_strength_sum": 1.0, "chart_ruler": 0.0, "angularity": 1.0, "luminary": 0.0, "house_chain": 0.6667, "repeated_support": 1.0, "contradiction": 0.0, "archetype_confidence": 0.8503}`

### `relationship`
- score: `0.7218`
- tier: `medium_strong`
- packet_ids: `["moon_leo_8h_deep_proud_heart_chart_exact", "moon_trine_venus_emotional_warmth_chart_exact", "venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact"]`
- evidence_summary: `["angular support", "luminary support", "house-chain support", "repeated packet support"]`
- scoring_breakdown: `{"packet_strength_sum": 1.0, "chart_ruler": 0.0, "angularity": 0.3333, "luminary": 1.0, "house_chain": 0.6667, "repeated_support": 1.0, "contradiction": 0.0, "archetype_confidence": 0.9239}`

## 3. clusters

### `identity_self_construction`
- domain: `identity`
- domain_family: `identity`
- cluster_label: `self_construction`
- cluster_strength: `0.9041`
- public_card_priority: `1.0`
- target_surface_role: `public_main`
- main_packet_id: `capricorn_asc_sun_1h_composed_self_construction_chart_exact`
- packet_members:
  - `capricorn_asc_sun_1h_composed_self_construction_chart_exact` | `primary_anchor` | `main_promise` | explicit_anchor_allowed=`True` | `main packet of cluster`
  - `saturn_3h_aries_speech_decision_language_chart_exact` | `secondary_anchor` | `speech_decision_language` | explicit_anchor_allowed=`True` | `distinct subtype enriches cluster without duplicating main card`
  - `saturn_sextile_uranus_structured_originality_chart_exact` | `secondary_anchor` | `structured_originality` | explicit_anchor_allowed=`True` | `distinct subtype enriches cluster without duplicating main card`
- shared_themes: `["bazen", "bile", "calisma", "capricorn_asc_sun_1h_composed_self_construction_chart_exact", "cizgini", "disarida"]`
- distinct_lived_scene: `Dışarıda güçlü, toparlı ve kendi çizgisini koruyan görünmek istemek.`
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: `["strong focus-map domain", "hero-capable cluster", "identity support should survive even if not hero", "has reusable sub-angles for detail"]`

### `career_healing_voice`
- domain: `career`
- domain_family: `career`
- cluster_label: `healing_voice`
- cluster_strength: `0.9153`
- public_card_priority: `0.9753`
- target_surface_role: `public_main`
- main_packet_id: `chiron_conjunct_mc_visibility_wound_to_voice_chart_exact`
- packet_members:
  - `chiron_conjunct_mc_visibility_wound_to_voice_chart_exact` | `primary_anchor` | `main_promise` | explicit_anchor_allowed=`True` | `main packet of cluster`
  - `capricorn_asc_sun_1h_composed_self_construction_chart_exact` | `secondary_anchor` | `self_construction` | explicit_anchor_allowed=`True` | `distinct subtype enriches cluster without duplicating main card`
  - `venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact` | `secondary_anchor` | `hidden_private_love_pattern` | explicit_anchor_allowed=`True` | `distinct subtype enriches cluster without duplicating main card`
- shared_themes: `["acan", "alan", "baskalarina", "baskasina", "cevirmek", "chiron_conjunct_mc_visibility_wound_to_voice_chart_exact"]`
- distinct_lived_scene: `Görünmeden önce fazladan hazırlanmak ama zamanla bunu sese çevirmek.`
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: `["strong focus-map domain", "has reusable sub-angles for detail"]`

### `relationship_attachment_architecture`
- domain: `relationship`
- domain_family: `relationship`
- cluster_label: `attachment_architecture`
- cluster_strength: `0.7341`
- public_card_priority: `0.8441`
- target_surface_role: `public_main`
- main_packet_id: `moon_leo_8h_deep_proud_heart_chart_exact`
- packet_members:
  - `moon_leo_8h_deep_proud_heart_chart_exact` | `primary_anchor` | `main_promise` | explicit_anchor_allowed=`True` | `main packet of cluster`
  - `venus_sagittarius_12h_hidden_expansive_love_chart_exact` | `secondary_anchor` | `internal_visibility_maturation` | explicit_anchor_allowed=`True` | `distinct subtype enriches cluster without duplicating main card`
- shared_themes: `["acildiginda", "acilmayan", "baglanan", "baglandiginda", "baglardan", "birakmamak"]`
- distinct_lived_scene: `Bir bağ içeri gerçekten oturana kadar duyguyu tam açmamak.`
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: `["has reusable sub-angles for detail"]`

### `relationship_affection_gift`
- domain: `relationship`
- domain_family: `relationship`
- cluster_label: `affection_gift`
- cluster_strength: `0.7501`
- public_card_priority: `0.8101`
- target_surface_role: `public_support`
- main_packet_id: `moon_trine_venus_emotional_warmth_chart_exact`
- packet_members:
  - `moon_trine_venus_emotional_warmth_chart_exact` | `primary_anchor` | `main_promise` | explicit_anchor_allowed=`True` | `main packet of cluster`
  - `venus_sagittarius_12h_hidden_expansive_love_chart_exact` | `secondary_anchor` | `internal_visibility_maturation` | explicit_anchor_allowed=`True` | `distinct subtype enriches cluster without duplicating main card`
- shared_themes: `["atmak", "duyguyu", "etmek", "fazla", "gelmek", "gorunur"]`
- distinct_lived_scene: `Gergin bir anda bile sevdiğin kişiye daha yumuşak ve iyi gelen bir yerden dönmek.`
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: `["has reusable sub-angles for detail"]`

### `mind_speech_decision_language`
- domain: `mind`
- domain_family: `mind`
- cluster_label: `speech_decision_language`
- cluster_strength: `0.8655`
- public_card_priority: `0.9755`
- target_surface_role: `detail`
- main_packet_id: `saturn_3h_aries_speech_decision_language_chart_exact`
- packet_members:
  - `saturn_3h_aries_speech_decision_language_chart_exact` | `primary_anchor` | `main_promise` | explicit_anchor_allowed=`True` | `main packet of cluster`
  - `capricorn_asc_sun_1h_composed_self_construction_chart_exact` | `secondary_anchor` | `self_construction` | explicit_anchor_allowed=`True` | `distinct subtype enriches cluster without duplicating main card`
  - `saturn_sextile_uranus_structured_originality_identity_chart_exact` | `secondary_anchor` | `gift` | explicit_anchor_allowed=`True` | `distinct lived scene keeps a separate support angle`
- shared_themes: `["agirlik", "bastirmadan", "calisiyor", "cikmak", "cumleye", "dili"]`
- distinct_lived_scene: `Cümleyi hem tartıp hem hızlı netleştirmek.`
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: `["hero-capable cluster", "has reusable sub-angles for detail"]`

### `mind_structured_originality`
- domain: `mind`
- domain_family: `mind`
- cluster_label: `structured_originality`
- cluster_strength: `0.8815`
- public_card_priority: `0.9415`
- target_surface_role: `public_main`
- main_packet_id: `saturn_sextile_uranus_structured_originality_chart_exact`
- packet_members:
  - `saturn_sextile_uranus_structured_originality_chart_exact` | `primary_anchor` | `main_promise` | explicit_anchor_allowed=`True` | `main packet of cluster`
  - `capricorn_asc_sun_1h_composed_self_construction_chart_exact` | `secondary_anchor` | `self_construction` | explicit_anchor_allowed=`True` | `distinct subtype enriches cluster without duplicating main card`
  - `saturn_sextile_uranus_structured_originality_identity_chart_exact` | `secondary_anchor` | `gift` | explicit_anchor_allowed=`True` | `distinct lived scene keeps a separate support angle`
- shared_themes: `["ayni", "bogabilir", "bulmak", "calisir", "cevirmek", "dagitabilir"]`
- distinct_lived_scene: `Yeni bir fikri hızla çalışır bir sisteme çevirebilmek.`
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: `["hero-capable cluster", "has reusable sub-angles for detail"]`

### `identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact`
- domain: `identity`
- domain_family: `identity`
- cluster_label: `gift_like`
- cluster_strength: `0.8881`
- public_card_priority: `0.9481`
- target_surface_role: `detail`
- main_packet_id: `saturn_sextile_uranus_structured_originality_identity_chart_exact`
- packet_members:
  - `saturn_sextile_uranus_structured_originality_identity_chart_exact` | `primary_anchor` | `main_promise` | explicit_anchor_allowed=`True` | `main packet of cluster`
  - `saturn_3h_aries_speech_decision_language_chart_exact` | `secondary_anchor` | `speech_decision_language` | explicit_anchor_allowed=`True` | `distinct subtype enriches cluster without duplicating main card`
  - `saturn_sextile_uranus_structured_originality_chart_exact` | `secondary_anchor` | `structured_originality` | explicit_anchor_allowed=`True` | `distinct subtype enriches cluster without duplicating main card`
- shared_themes: `["ayni", "bogabilir", "bulmak", "calisir", "cevirmek", "dagitabilir"]`
- distinct_lived_scene: `Dışarıda kontrollü kalırken içeride daha özgün bir çizgiyi taşımak.`
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: `["strong focus-map domain", "hero-capable cluster", "has reusable sub-angles for detail"]`

### `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact`
- domain: `identity`
- domain_family: `identity`
- cluster_label: `gift_like`
- cluster_strength: `0.8881`
- public_card_priority: `0.9481`
- target_surface_role: `public_main`
- main_packet_id: `saturn_trine_pluto_deep_resilience_chart_exact`
- packet_members:
  - `saturn_trine_pluto_deep_resilience_chart_exact` | `primary_anchor` | `main_promise` | explicit_anchor_allowed=`True` | `main packet of cluster`
  - `saturn_3h_aries_speech_decision_language_chart_exact` | `secondary_anchor` | `speech_decision_language` | explicit_anchor_allowed=`True` | `distinct subtype enriches cluster without duplicating main card`
  - `saturn_sextile_uranus_structured_originality_chart_exact` | `secondary_anchor` | `structured_originality` | explicit_anchor_allowed=`True` | `distinct subtype enriches cluster without duplicating main card`
- shared_themes: `["basina", "baski", "bazen", "bile", "calisma", "cozulmek"]`
- distinct_lived_scene: `Baskı arttığında dağılmak yerine daha kontrollü ve dayanıklı kalmak.`
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: `["strong focus-map domain", "hero-capable cluster", "has reusable sub-angles for detail"]`

### `career_internal_visibility_maturation`
- domain: `career`
- domain_family: `career`
- cluster_label: `internal_visibility_maturation`
- cluster_strength: `0.9313`
- public_card_priority: `1.0`
- target_surface_role: `public_main`
- main_packet_id: `venus_sagittarius_12h_hidden_expansive_love_chart_exact`
- packet_members:
  - `venus_sagittarius_12h_hidden_expansive_love_chart_exact` | `primary_anchor` | `main_promise` | explicit_anchor_allowed=`True` | `main packet of cluster`
  - `capricorn_asc_sun_1h_composed_self_construction_chart_exact` | `secondary_anchor` | `self_construction` | explicit_anchor_allowed=`True` | `distinct subtype enriches cluster without duplicating main card`
  - `venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact` | `secondary_anchor` | `hidden_private_love_pattern` | explicit_anchor_allowed=`True` | `distinct subtype enriches cluster without duplicating main card`
- shared_themes: `["acabilmek", "bicimde", "buyuttugun", "ceride", "daha", "dealize"]`
- distinct_lived_scene: `Bir üretimi paylaşmadan önce içeride rafine etmek istemek.`
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: `["strong focus-map domain", "has reusable sub-angles for detail"]`

### `relationship_hidden_private_love_pattern`
- domain: `relationship`
- domain_family: `relationship`
- cluster_label: `hidden_private_love_pattern`
- cluster_strength: `0.7341`
- public_card_priority: `0.8441`
- target_surface_role: `detail`
- main_packet_id: `venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact`
- packet_members:
  - `venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact` | `primary_anchor` | `main_promise` | explicit_anchor_allowed=`True` | `main packet of cluster`
  - `venus_sagittarius_12h_hidden_expansive_love_chart_exact` | `secondary_anchor` | `internal_visibility_maturation` | explicit_anchor_allowed=`True` | `distinct subtype enriches cluster without duplicating main card`
- shared_themes: `["acabilmek", "bicimde", "buyuttugun", "ceride", "daha", "dealize"]`
- distinct_lived_scene: `Sevginin önce kendi içinde uzun süre büyümesi ve kolay açılmaması.`
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: `["has reusable sub-angles for detail"]`

### `mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact`
- domain: `mind`
- domain_family: `mind`
- cluster_label: `gift_like`
- cluster_strength: `0.8655`
- public_card_priority: `0.9255`
- target_surface_role: `public_support`
- main_packet_id: `mercury_conjunct_jupiter_big_mind_chart_exact`
- packet_members:
  - `mercury_conjunct_jupiter_big_mind_chart_exact` | `primary_anchor` | `main_promise` | explicit_anchor_allowed=`True` | `main packet of cluster`
  - `capricorn_asc_sun_1h_composed_self_construction_chart_exact` | `secondary_anchor` | `self_construction` | explicit_anchor_allowed=`True` | `distinct subtype enriches cluster without duplicating main card`
  - `saturn_sextile_uranus_structured_originality_identity_chart_exact` | `secondary_anchor` | `gift` | explicit_anchor_allowed=`True` | `distinct lived scene keeps a separate support angle`
- shared_themes: `["anlami", "anlatilabilir", "aralarindaki", "ayrinti", "baglama", "baskasina"]`
- distinct_lived_scene: `Parçaları bir araya getirip daha büyük resmi kurmak.`
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: `["hero-capable cluster", "has reusable sub-angles for detail"]`

## 4. surface_plan

- public_main_cluster_ids:
  - `career_internal_visibility_maturation`
  - `identity_self_construction`
  - `mind_structured_originality`
  - `relationship_attachment_architecture`
  - `career_healing_voice`
  - `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact`
- public_support_cluster_ids:
  - `mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact`
  - `relationship_affection_gift`
- detail_cluster_ids:
  - `mind_speech_decision_language`
  - `identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact`
  - `relationship_hidden_private_love_pattern`
- debug_packet_ids count: `11`

## 5. suppressed_packets

- `saturn_sextile_uranus_structured_originality_identity_chart_exact`
  - suppressed_from_public_main: `True`
  - keep_for: `["detail", "debug", "transit_activation"]`
  - reason: `same signal family already has a stronger public-main cluster`
  - superseded_by_cluster_id: `mind_structured_originality`
  - superseded_by_packet_id: `None`

## 6. anchor_usage

- `saturn 3 ev`
  - public_main_explicit_uses: `2`
  - explicit_use_budget: `2`
  - cluster_ids: `["identity_self_construction", "career_healing_voice", "mind_speech_decision_language", "mind_structured_originality", "identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact", "identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact", "career_internal_visibility_maturation", "mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact"]`
  - chart_defining_override: `False`
- `1th house ruler route`
  - public_main_explicit_uses: `2`
  - explicit_use_budget: `2`
  - cluster_ids: `["identity_self_construction", "career_healing_voice", "mind_speech_decision_language", "mind_structured_originality", "identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact", "identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact", "career_internal_visibility_maturation", "mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact"]`
  - chart_defining_override: `False`
- `saturn sextile uranus`
  - public_main_explicit_uses: `1`
  - explicit_use_budget: `2`
  - cluster_ids: `["identity_self_construction", "mind_speech_decision_language", "mind_structured_originality", "identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact", "identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact", "mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact"]`
  - chart_defining_override: `False`
- `mc terazi`
  - public_main_explicit_uses: `2`
  - explicit_use_budget: `2`
  - cluster_ids: `["career_healing_voice", "relationship_attachment_architecture", "relationship_affection_gift", "career_internal_visibility_maturation", "relationship_hidden_private_love_pattern"]`
  - chart_defining_override: `True`
- `venus 12 ev yay`
  - public_main_explicit_uses: `1`
  - explicit_use_budget: `2`
  - cluster_ids: `["career_healing_voice", "relationship_attachment_architecture", "relationship_affection_gift", "career_internal_visibility_maturation", "relationship_hidden_private_love_pattern"]`
  - chart_defining_override: `False`

Note: full anchor_usage is larger; these are the most relevant anchors with non-zero public-main explicit use.

## 7. projection outputs after cluster integration

### `profile_narrative_projection_v1`
- source_graph: `natal_promise_cluster_plan_v1`
- core_blocks:
  - `promise::venus_sagittarius_12h_hidden_expansive_love_chart_exact`
  - `promise::capricorn_asc_sun_1h_composed_self_construction_chart_exact`
  - `promise::saturn_sextile_uranus_structured_originality_chart_exact`
  - `promise::moon_leo_8h_deep_proud_heart_chart_exact`
- additional blocks:
  - `promise::moon_trine_venus_emotional_warmth_chart_exact`
  - `promise::saturn_sextile_uranus_structured_originality_identity_chart_exact`
  - `promise::saturn_3h_aries_speech_decision_language_chart_exact`
  - `promise::venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact`
  - `promise::mercury_conjunct_jupiter_big_mind_chart_exact`

### `profile_v8_projection_v1`
- source_graph: `natal_promise_cluster_plan_v1`
- hero: `promise::capricorn_asc_sun_1h_composed_self_construction_chart_exact`
- identity_axis: `promise::saturn_3h_aries_speech_decision_language_chart_exact`
- insight_strip:
  - `promise::moon_leo_8h_deep_proud_heart_chart_exact`
  - `promise::venus_sagittarius_12h_hidden_expansive_love_chart_exact`
  - `promise::saturn_trine_pluto_deep_resilience_chart_exact`
- differentiators:
  - `promise::moon_trine_venus_emotional_warmth_chart_exact`
  - `promise::saturn_sextile_uranus_structured_originality_chart_exact`
  - `promise::chiron_conjunct_mc_visibility_wound_to_voice_chart_exact`

### source_graph/source layer markers
- `profile_narrative_projection_v1.source_graph = natal_promise_cluster_plan_v1`
- `profile_v8_projection_v1.source_graph = natal_promise_cluster_plan_v1`
- `profile_v8_projection_v1.traceability.cluster_public_main_count = 6`
- with `include_debug=False`, cluster plan is still not exposed as a normal top-level public field and the full cluster object is absent from traceability

## 8. checks

### Required confirmations
- PASS: public main card count is `6`, so `<= 7`
- PASS: identity/self-construction is `strong` in focus_map and remains `public_main`
- PASS: `Venus 12H` appears in both career and relationship clusters with different roles
  - career: `career_internal_visibility_maturation` main packet
  - relationship: `relationship_attachment_architecture` and `relationship_affection_gift` as secondary support angle, plus `relationship_hidden_private_love_pattern` detail cluster
- PASS: suppressed packets are not removed from debug/detail/transit_activation
- PASS: v8 hero remains identity/mind, not relationship
- PASS: public schema does not expose cluster plan as a normal top-level field; full cluster payload appears only in debug traceability

### Rubric pass/fail notes
- PASS: mind / communication / structured originality is now clearly represented in public main through `mind_structured_originality`
- PASS: identity / self-construction remains visible and chart-defining; it did not disappear into modifier-only status
- PASS: relationship is no longer flattened out of main feed; `attachment_architecture` is public_main and `affection_gift` survives in public_support
- PASS: career / visibility / creative channel remains strong with two distinct public_main jobs
- PASS: action / pressure / resilience is visible via `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact`
- PASS: money/self-worth is not forced into the feed
- PASS: same technical family no longer crowds public_main
  - `mind_structured_originality` is public_main
  - `identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact` is detail-only and explicitly suppressed from public_main
- PASS: detail allocation is no longer empty
- PASS: public main target settled at `6`, not the hard max `7`

### Remaining weirdness to keep visible
- `mind_speech_decision_language` still has very high raw priority (`0.9755`) but is held in detail by diversity rules rather than by low score
- `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact` still surfaces as a generic `gift_like` identity cluster id; semantically it reads correctly, but the cluster label is not yet subtype-specific
