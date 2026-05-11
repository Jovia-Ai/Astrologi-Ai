# Istanbul ClusterPlan Audit After Source Fix

- Generated: 2026-05-11
- Source artifact: `backend/tests/_artifacts/natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json`
- Flags: `ENABLE_NATAL_PROMISE_PROJECTION_V1=true`, `ENABLE_NATAL_PROMISE_PACKET_DEBUG=true`
- Source fix status: ClusterPlan candidate inventory is now built from raw response sections/threads plus chart-signature fallback seeds from planets/aspects/house-ruler context before public humanization loss.

## 1. candidate_inventory summary

- Total candidate packet count: `11`
- Selected packet count: `3`
- Top candidate packets (current inventory has 11):

### 1. `capricorn_asc_sun_1h_composed_self_construction_chart_exact`
- domain: `identity`
- promise_type: `behavior_reflex`
- strength: `1.0`
- technical_anchors: ["Yükselen · Oğlak · Güneş 1. ev", "Yükselen Oğlak", "Güneş 1. ev", "Satürn 3. ev", "1th house ruler route", "Sun conjunction Ascendant"]
- direct_meaning: Dışarıda toparlanmış ve kontrollü görünmek senin için önemli olabilir.

### 2. `chiron_conjunct_mc_visibility_wound_to_voice_chart_exact`
- domain: `career`
- promise_type: `wound_to_gift`
- strength: `1.0`
- technical_anchors: ["Chiron conjunct MC", "Chiron 10. ev", "MC Terazi", "Jupiter square Midheaven", "Neptune square Midheaven", "Chiron conjunct Midheaven"]
- direct_meaning: Görünür olma hassasiyetini zamanla başkalarına dokunan bir sese çevirmek.

### 3. `moon_leo_8h_deep_proud_heart_chart_exact`
- domain: `relationship`
- promise_type: `love_style`
- strength: `1.0`
- technical_anchors: ["Ay · 8. ev · Aslan", "7. ev Yengeç", "Ay 8. ev", "Aslan", "7th house ruler route", "Moon trine Venus"]
- direct_meaning: Derin, gururlu, kolay açılmayan ama açıldığında güçlü bağlanan kalp.

### 4. `moon_trine_venus_emotional_warmth_chart_exact`
- domain: `relationship`
- promise_type: `gift`
- strength: `1.0`
- technical_anchors: ["Moon trine Venus", "Ay 8. ev", "Venüs 12. ev", "7th house ruler route", "Venus conjunction Vertex"]
- direct_meaning: Sevdiği şeyi yumuşatan, güzelleştiren ve korumak isteyen bir kalp.

### 5. `saturn_3h_aries_speech_decision_language_chart_exact`
- domain: `mind`
- promise_type: `mind_style`
- strength: `1.0`
- technical_anchors: ["Satürn · 3. ev · Koç", "Satürn 3. ev", "Koç", "Merkür 1. ev", "Saturn in house 3 Aries", "Mercury conjunction Jupiter"]
- direct_meaning: Söz, ton ve karar dili sende kimliğe yakın bir yerden çalışıyor olabilir.

### 6. `saturn_sextile_uranus_structured_originality_chart_exact`
- domain: `mind`
- promise_type: `gift`
- strength: `1.0`
- technical_anchors: ["Saturn sextile Uranus", "Satürn 3. ev", "Uranüs 1. ev", "1th house ruler route", "Mercury conjunction Jupiter"]
- direct_meaning: Farklı fikri sadece bulmak değil, ona çalışır bir form verebilmek.

### 7. `saturn_sextile_uranus_structured_originality_identity_chart_exact`
- domain: `identity`
- promise_type: `gift`
- strength: `1.0`
- technical_anchors: ["Saturn sextile Uranus", "Yükselen Oğlak", "Uranüs 1. ev", "Ascendant Capricorn"]
- direct_meaning: Farklı fikri sadece bulmak değil, ona çalışır bir form verebilmek.

### 8. `saturn_trine_pluto_deep_resilience_chart_exact`
- domain: `identity`
- promise_type: `gift`
- strength: `1.0`
- technical_anchors: ["Saturn trine Pluto", "Sun square Saturn", "Mars opposite Saturn", "Mars opposition Saturn"]
- direct_meaning: Baskı geldiğinde bile yapıyı koruyup içerden dönüşebilmek.

### 9. `venus_sagittarius_12h_hidden_expansive_love_chart_exact`
- domain: `career`
- promise_type: `career_signature`
- strength: `1.0`
- technical_anchors: ["Venüs · 12. ev · Yay", "MC Terazi", "Venüs 12. ev", "Yay", "10th house ruler route", "Jupiter square Midheaven"]
- direct_meaning: Üretim ve görünürlük sende önce içeride olgunlaşmak isteyebilir.

### 10. `venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact`
- domain: `relationship`
- promise_type: `career_signature`
- strength: `1.0`
- technical_anchors: ["Venüs · 12. ev · Yay", "Venüs 12. ev", "Yay", "Moon trine Venus", "Venus in house 12", "Venus conjunction Vertex"]
- direct_meaning: Üretim ve görünürlük sende önce içeride olgunlaşmak isteyebilir.

### 11. `mercury_conjunct_jupiter_big_mind_chart_exact`
- domain: `mind`
- promise_type: `gift`
- strength: `0.9279`
- technical_anchors: ["Mercury conjunction Jupiter", "Merkür 1. ev", "Jüpiter 1. ev", "3th house ruler route", "Mercury conjunct Jupiter"]
- direct_meaning: Parçaları tek tek görmekten çok, aralarındaki anlamı kuran bir zihin.

## 2. focus_map

### `career`
- score: `1.0`
- tier: `strong`
- packet_ids: ["chiron_conjunct_mc_visibility_wound_to_voice_chart_exact", "venus_sagittarius_12h_hidden_expansive_love_chart_exact"]
- evidence_summary: ["chart ruler support", "angular support", "luminary support", "house-chain support"]
- scoring_breakdown:
  - `packet_strength_sum`: `0.8511`
  - `chart_ruler`: `1.0`
  - `angularity`: `1.0`
  - `luminary`: `0.5`
  - `house_chain`: `0.5`
  - `repeated_support`: `0.8`
  - `contradiction`: `0.0`
  - `archetype_confidence`: `0.8595`

### `identity`
- score: `0.8762`
- tier: `strong`
- packet_ids: ["capricorn_asc_sun_1h_composed_self_construction_chart_exact", "saturn_sextile_uranus_structured_originality_identity_chart_exact", "saturn_trine_pluto_deep_resilience_chart_exact"]
- evidence_summary: ["chart ruler support", "angular support", "luminary support", "house-chain support"]
- scoring_breakdown:
  - `packet_strength_sum`: `1.0`
  - `chart_ruler`: `0.6667`
  - `angularity`: `0.6667`
  - `luminary`: `0.6667`
  - `house_chain`: `0.3333`
  - `repeated_support`: `1.0`
  - `contradiction`: `0.2767`
  - `archetype_confidence`: `0.895`

### `mind`
- score: `0.7737`
- tier: `medium_strong`
- packet_ids: ["saturn_3h_aries_speech_decision_language_chart_exact", "saturn_sextile_uranus_structured_originality_chart_exact", "mercury_conjunct_jupiter_big_mind_chart_exact"]
- evidence_summary: ["angular support", "house-chain support", "repeated packet support"]
- scoring_breakdown:
  - `packet_strength_sum`: `1.0`
  - `chart_ruler`: `0.0`
  - `angularity`: `1.0`
  - `luminary`: `0.0`
  - `house_chain`: `0.6667`
  - `repeated_support`: `1.0`
  - `contradiction`: `0.0`
  - `archetype_confidence`: `0.8503`

### `relationship`
- score: `0.7218`
- tier: `medium_strong`
- packet_ids: ["moon_leo_8h_deep_proud_heart_chart_exact", "moon_trine_venus_emotional_warmth_chart_exact", "venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact"]
- evidence_summary: ["angular support", "luminary support", "house-chain support", "repeated packet support"]
- scoring_breakdown:
  - `packet_strength_sum`: `1.0`
  - `chart_ruler`: `0.0`
  - `angularity`: `0.3333`
  - `luminary`: `1.0`
  - `house_chain`: `0.6667`
  - `repeated_support`: `1.0`
  - `contradiction`: `0.0`
  - `archetype_confidence`: `0.9239`

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
  - packet_id: `capricorn_asc_sun_1h_composed_self_construction_chart_exact`
    - cluster_role: `primary_anchor`
    - contribution_type: `main_promise`
    - explicit_anchor_allowed: `True`
    - reason: main packet of cluster
  - packet_id: `saturn_3h_aries_speech_decision_language_chart_exact`
    - cluster_role: `secondary_anchor`
    - contribution_type: `speech_decision_language`
    - explicit_anchor_allowed: `True`
    - reason: distinct subtype enriches cluster without duplicating main card
  - packet_id: `saturn_sextile_uranus_structured_originality_chart_exact`
    - cluster_role: `secondary_anchor`
    - contribution_type: `structured_originality`
    - explicit_anchor_allowed: `True`
    - reason: distinct subtype enriches cluster without duplicating main card
- shared_themes: ["bazen", "bile", "calisma", "capricorn_asc_sun_1h_composed_self_construction_chart_exact", "cizgini", "disarida"]
- distinct_lived_scene: Dışarıda güçlü, toparlı ve kendi çizgisini koruyan görünmek istemek.
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: ["strong focus-map domain", "hero-capable cluster", "identity support should survive even if not hero", "has reusable sub-angles for detail"]

### `career_healing_voice`
- domain: `career`
- domain_family: `career`
- cluster_label: `healing_voice`
- cluster_strength: `0.9153`
- public_card_priority: `0.9753`
- target_surface_role: `public_main`
- main_packet_id: `chiron_conjunct_mc_visibility_wound_to_voice_chart_exact`
- packet_members:
  - packet_id: `chiron_conjunct_mc_visibility_wound_to_voice_chart_exact`
    - cluster_role: `primary_anchor`
    - contribution_type: `main_promise`
    - explicit_anchor_allowed: `True`
    - reason: main packet of cluster
  - packet_id: `capricorn_asc_sun_1h_composed_self_construction_chart_exact`
    - cluster_role: `secondary_anchor`
    - contribution_type: `self_construction`
    - explicit_anchor_allowed: `True`
    - reason: distinct subtype enriches cluster without duplicating main card
  - packet_id: `venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact`
    - cluster_role: `secondary_anchor`
    - contribution_type: `hidden_private_love_pattern`
    - explicit_anchor_allowed: `True`
    - reason: distinct subtype enriches cluster without duplicating main card
- shared_themes: ["acan", "alan", "baskalarina", "baskasina", "cevirmek", "chiron_conjunct_mc_visibility_wound_to_voice_chart_exact"]
- distinct_lived_scene: Görünmeden önce fazladan hazırlanmak ama zamanla bunu sese çevirmek.
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: ["strong focus-map domain", "has reusable sub-angles for detail"]

### `relationship_attachment_architecture`
- domain: `relationship`
- domain_family: `relationship`
- cluster_label: `attachment_architecture`
- cluster_strength: `0.7341`
- public_card_priority: `0.8441`
- target_surface_role: `public_support`
- main_packet_id: `moon_leo_8h_deep_proud_heart_chart_exact`
- packet_members:
  - packet_id: `moon_leo_8h_deep_proud_heart_chart_exact`
    - cluster_role: `primary_anchor`
    - contribution_type: `main_promise`
    - explicit_anchor_allowed: `True`
    - reason: main packet of cluster
  - packet_id: `venus_sagittarius_12h_hidden_expansive_love_chart_exact`
    - cluster_role: `secondary_anchor`
    - contribution_type: `internal_visibility_maturation`
    - explicit_anchor_allowed: `True`
    - reason: distinct subtype enriches cluster without duplicating main card
- shared_themes: ["acildiginda", "acilmayan", "baglanan", "baglandiginda", "baglardan", "birakmamak"]
- distinct_lived_scene: Bir bağ içeri gerçekten oturana kadar duyguyu tam açmamak.
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: ["has reusable sub-angles for detail"]

### `relationship_affection_gift`
- domain: `relationship`
- domain_family: `relationship`
- cluster_label: `affection_gift`
- cluster_strength: `0.7501`
- public_card_priority: `0.8101`
- target_surface_role: `public_support`
- main_packet_id: `moon_trine_venus_emotional_warmth_chart_exact`
- packet_members:
  - packet_id: `moon_trine_venus_emotional_warmth_chart_exact`
    - cluster_role: `primary_anchor`
    - contribution_type: `main_promise`
    - explicit_anchor_allowed: `True`
    - reason: main packet of cluster
  - packet_id: `venus_sagittarius_12h_hidden_expansive_love_chart_exact`
    - cluster_role: `secondary_anchor`
    - contribution_type: `internal_visibility_maturation`
    - explicit_anchor_allowed: `True`
    - reason: distinct subtype enriches cluster without duplicating main card
- shared_themes: ["atmak", "duyguyu", "etmek", "fazla", "gelmek", "gorunur"]
- distinct_lived_scene: Gergin bir anda bile sevdiğin kişiye daha yumuşak ve iyi gelen bir yerden dönmek.
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: ["has reusable sub-angles for detail"]

### `mind_speech_decision_language`
- domain: `mind`
- domain_family: `mind`
- cluster_label: `speech_decision_language`
- cluster_strength: `0.8655`
- public_card_priority: `0.9755`
- target_surface_role: `public_main`
- main_packet_id: `saturn_3h_aries_speech_decision_language_chart_exact`
- packet_members:
  - packet_id: `saturn_3h_aries_speech_decision_language_chart_exact`
    - cluster_role: `primary_anchor`
    - contribution_type: `main_promise`
    - explicit_anchor_allowed: `True`
    - reason: main packet of cluster
  - packet_id: `capricorn_asc_sun_1h_composed_self_construction_chart_exact`
    - cluster_role: `secondary_anchor`
    - contribution_type: `self_construction`
    - explicit_anchor_allowed: `True`
    - reason: distinct subtype enriches cluster without duplicating main card
  - packet_id: `saturn_sextile_uranus_structured_originality_identity_chart_exact`
    - cluster_role: `secondary_anchor`
    - contribution_type: `gift`
    - explicit_anchor_allowed: `True`
    - reason: distinct lived scene keeps a separate support angle
- shared_themes: ["agirlik", "bastirmadan", "calisiyor", "cikmak", "cumleye", "dili"]
- distinct_lived_scene: Cümleyi hem tartıp hem hızlı netleştirmek.
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: ["hero-capable cluster", "has reusable sub-angles for detail"]

### `mind_structured_originality`
- domain: `mind`
- domain_family: `mind`
- cluster_label: `structured_originality`
- cluster_strength: `0.8815`
- public_card_priority: `0.9415`
- target_surface_role: `public_main`
- main_packet_id: `saturn_sextile_uranus_structured_originality_chart_exact`
- packet_members:
  - packet_id: `saturn_sextile_uranus_structured_originality_chart_exact`
    - cluster_role: `primary_anchor`
    - contribution_type: `main_promise`
    - explicit_anchor_allowed: `False`
    - reason: main packet of cluster
  - packet_id: `capricorn_asc_sun_1h_composed_self_construction_chart_exact`
    - cluster_role: `secondary_anchor`
    - contribution_type: `self_construction`
    - explicit_anchor_allowed: `True`
    - reason: distinct subtype enriches cluster without duplicating main card
  - packet_id: `saturn_sextile_uranus_structured_originality_identity_chart_exact`
    - cluster_role: `secondary_anchor`
    - contribution_type: `gift`
    - explicit_anchor_allowed: `True`
    - reason: distinct lived scene keeps a separate support angle
- shared_themes: ["ayni", "bogabilir", "bulmak", "calisir", "cevirmek", "dagitabilir"]
- distinct_lived_scene: Yeni bir fikri hızla çalışır bir sisteme çevirebilmek.
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: ["hero-capable cluster", "has reusable sub-angles for detail"]

### `identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact`
- domain: `identity`
- domain_family: `identity`
- cluster_label: `gift_like`
- cluster_strength: `0.8881`
- public_card_priority: `0.9481`
- target_surface_role: `public_main`
- main_packet_id: `saturn_sextile_uranus_structured_originality_identity_chart_exact`
- packet_members:
  - packet_id: `saturn_sextile_uranus_structured_originality_identity_chart_exact`
    - cluster_role: `primary_anchor`
    - contribution_type: `main_promise`
    - explicit_anchor_allowed: `True`
    - reason: main packet of cluster
  - packet_id: `saturn_3h_aries_speech_decision_language_chart_exact`
    - cluster_role: `secondary_anchor`
    - contribution_type: `speech_decision_language`
    - explicit_anchor_allowed: `True`
    - reason: distinct subtype enriches cluster without duplicating main card
  - packet_id: `saturn_sextile_uranus_structured_originality_chart_exact`
    - cluster_role: `secondary_anchor`
    - contribution_type: `structured_originality`
    - explicit_anchor_allowed: `True`
    - reason: distinct subtype enriches cluster without duplicating main card
- shared_themes: ["ayni", "bogabilir", "bulmak", "calisir", "cevirmek", "dagitabilir"]
- distinct_lived_scene: Dışarıda kontrollü kalırken içeride daha özgün bir çizgiyi taşımak.
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: ["strong focus-map domain", "hero-capable cluster", "has reusable sub-angles for detail"]

### `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact`
- domain: `identity`
- domain_family: `identity`
- cluster_label: `gift_like`
- cluster_strength: `0.8881`
- public_card_priority: `0.9481`
- target_surface_role: `public_main`
- main_packet_id: `saturn_trine_pluto_deep_resilience_chart_exact`
- packet_members:
  - packet_id: `saturn_trine_pluto_deep_resilience_chart_exact`
    - cluster_role: `primary_anchor`
    - contribution_type: `main_promise`
    - explicit_anchor_allowed: `True`
    - reason: main packet of cluster
  - packet_id: `saturn_3h_aries_speech_decision_language_chart_exact`
    - cluster_role: `secondary_anchor`
    - contribution_type: `speech_decision_language`
    - explicit_anchor_allowed: `True`
    - reason: distinct subtype enriches cluster without duplicating main card
  - packet_id: `saturn_sextile_uranus_structured_originality_chart_exact`
    - cluster_role: `secondary_anchor`
    - contribution_type: `structured_originality`
    - explicit_anchor_allowed: `True`
    - reason: distinct subtype enriches cluster without duplicating main card
- shared_themes: ["basina", "baski", "bazen", "bile", "calisma", "cozulmek"]
- distinct_lived_scene: Baskı arttığında dağılmak yerine daha kontrollü ve dayanıklı kalmak.
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: ["strong focus-map domain", "hero-capable cluster", "has reusable sub-angles for detail"]

### `career_internal_visibility_maturation`
- domain: `career`
- domain_family: `career`
- cluster_label: `internal_visibility_maturation`
- cluster_strength: `0.9313`
- public_card_priority: `1.0`
- target_surface_role: `public_main`
- main_packet_id: `venus_sagittarius_12h_hidden_expansive_love_chart_exact`
- packet_members:
  - packet_id: `venus_sagittarius_12h_hidden_expansive_love_chart_exact`
    - cluster_role: `primary_anchor`
    - contribution_type: `main_promise`
    - explicit_anchor_allowed: `True`
    - reason: main packet of cluster
  - packet_id: `capricorn_asc_sun_1h_composed_self_construction_chart_exact`
    - cluster_role: `secondary_anchor`
    - contribution_type: `self_construction`
    - explicit_anchor_allowed: `True`
    - reason: distinct subtype enriches cluster without duplicating main card
  - packet_id: `venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact`
    - cluster_role: `secondary_anchor`
    - contribution_type: `hidden_private_love_pattern`
    - explicit_anchor_allowed: `True`
    - reason: distinct subtype enriches cluster without duplicating main card
- shared_themes: ["acabilmek", "bicimde", "buyuttugun", "ceride", "daha", "dealize"]
- distinct_lived_scene: Bir üretimi paylaşmadan önce içeride rafine etmek istemek.
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: ["strong focus-map domain", "has reusable sub-angles for detail"]

### `relationship_hidden_private_love_pattern`
- domain: `relationship`
- domain_family: `relationship`
- cluster_label: `hidden_private_love_pattern`
- cluster_strength: `0.7341`
- public_card_priority: `0.8441`
- target_surface_role: `public_support`
- main_packet_id: `venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact`
- packet_members:
  - packet_id: `venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact`
    - cluster_role: `primary_anchor`
    - contribution_type: `main_promise`
    - explicit_anchor_allowed: `True`
    - reason: main packet of cluster
  - packet_id: `venus_sagittarius_12h_hidden_expansive_love_chart_exact`
    - cluster_role: `secondary_anchor`
    - contribution_type: `internal_visibility_maturation`
    - explicit_anchor_allowed: `True`
    - reason: distinct subtype enriches cluster without duplicating main card
- shared_themes: ["acabilmek", "bicimde", "buyuttugun", "ceride", "daha", "dealize"]
- distinct_lived_scene: Sevginin önce kendi içinde uzun süre büyümesi ve kolay açılmaması.
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: ["has reusable sub-angles for detail"]

### `mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact`
- domain: `mind`
- domain_family: `mind`
- cluster_label: `gift_like`
- cluster_strength: `0.8655`
- public_card_priority: `0.9255`
- target_surface_role: `public_support`
- main_packet_id: `mercury_conjunct_jupiter_big_mind_chart_exact`
- packet_members:
  - packet_id: `mercury_conjunct_jupiter_big_mind_chart_exact`
    - cluster_role: `primary_anchor`
    - contribution_type: `main_promise`
    - explicit_anchor_allowed: `True`
    - reason: main packet of cluster
  - packet_id: `capricorn_asc_sun_1h_composed_self_construction_chart_exact`
    - cluster_role: `secondary_anchor`
    - contribution_type: `self_construction`
    - explicit_anchor_allowed: `True`
    - reason: distinct subtype enriches cluster without duplicating main card
  - packet_id: `saturn_sextile_uranus_structured_originality_identity_chart_exact`
    - cluster_role: `secondary_anchor`
    - contribution_type: `gift`
    - explicit_anchor_allowed: `True`
    - reason: distinct lived scene keeps a separate support angle
- shared_themes: ["anlami", "anlatilabilir", "aralarindaki", "ayrinti", "baglama", "baskasina"]
- distinct_lived_scene: Parçaları bir araya getirip daha büyük resmi kurmak.
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: ["hero-capable cluster", "has reusable sub-angles for detail"]

## 4. surface_plan

- public_main_cluster_ids: ["career_internal_visibility_maturation", "identity_self_construction", "mind_speech_decision_language", "career_healing_voice", "identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact", "identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact", "mind_structured_originality"]
- public_support_cluster_ids: ["mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact", "relationship_attachment_architecture", "relationship_hidden_private_love_pattern", "relationship_affection_gift"]
- detail_cluster_ids: []
- debug_packet_ids count: `11`

## 5. suppressed_packets

- No suppressed packets emitted in this run.

## 6. anchor_usage

### `yukselen oglak gunes 1 ev`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["identity_self_construction", "career_healing_voice", "mind_speech_decision_language", "mind_structured_originality", "career_internal_visibility_maturation", "mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact"]
- chart_defining_override: `True`

### `yukselen oglak`
- public_main_explicit_uses: `2`
- explicit_use_budget: `2`
- cluster_ids: ["identity_self_construction", "career_healing_voice", "mind_speech_decision_language", "mind_structured_originality", "identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact", "career_internal_visibility_maturation", "mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact"]
- chart_defining_override: `True`

### `gunes 1 ev`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["identity_self_construction", "career_healing_voice", "mind_speech_decision_language", "mind_structured_originality", "career_internal_visibility_maturation", "mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact"]
- chart_defining_override: `False`

### `saturn 3 ev`
- public_main_explicit_uses: `2`
- explicit_use_budget: `2`
- cluster_ids: ["identity_self_construction", "career_healing_voice", "mind_speech_decision_language", "mind_structured_originality", "identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact", "identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact", "career_internal_visibility_maturation", "mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact"]
- chart_defining_override: `False`

### `1th house ruler route`
- public_main_explicit_uses: `2`
- explicit_use_budget: `2`
- cluster_ids: ["identity_self_construction", "career_healing_voice", "mind_speech_decision_language", "mind_structured_originality", "identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact", "identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact", "career_internal_visibility_maturation", "mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact"]
- chart_defining_override: `False`

### `sun conjunction ascendant`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["identity_self_construction", "career_healing_voice", "mind_speech_decision_language", "mind_structured_originality", "career_internal_visibility_maturation", "mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact"]
- chart_defining_override: `True`

### `section:chart_seed::capricorn_asc_sun_1h_composed_self_construction::identity`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["identity_self_construction", "career_healing_voice", "mind_speech_decision_language", "mind_structured_originality", "career_internal_visibility_maturation", "mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact"]
- chart_defining_override: `False`

### `section:mind_system`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["identity_self_construction", "career_healing_voice", "mind_speech_decision_language", "mind_structured_originality", "career_internal_visibility_maturation", "mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact"]
- chart_defining_override: `False`

### `thread:identity_mechanics`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["identity_self_construction", "career_healing_voice", "mind_speech_decision_language", "mind_structured_originality", "career_internal_visibility_maturation", "mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact"]
- chart_defining_override: `False`

### `saturn 3 ev koc`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["identity_self_construction", "mind_speech_decision_language", "identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact", "identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact"]
- chart_defining_override: `False`

### `koc`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["identity_self_construction", "mind_speech_decision_language", "identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact", "identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact"]
- chart_defining_override: `False`

### `merkur 1 ev`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["identity_self_construction", "mind_speech_decision_language", "identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact", "identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact", "mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact"]
- chart_defining_override: `False`

### `saturn in house 3 aries`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["identity_self_construction", "mind_speech_decision_language", "identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact", "identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact"]
- chart_defining_override: `False`

### `mercury conjunction jupiter`
- public_main_explicit_uses: `2`
- explicit_use_budget: `2`
- cluster_ids: ["identity_self_construction", "mind_speech_decision_language", "mind_structured_originality", "identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact", "identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact", "mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact"]
- chart_defining_override: `False`

### `section:chart_seed::saturn_3h_aries_speech_decision_language::mind`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["identity_self_construction", "mind_speech_decision_language", "identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact", "identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact"]
- chart_defining_override: `False`

### `saturn sextile uranus`
- public_main_explicit_uses: `2`
- explicit_use_budget: `2`
- cluster_ids: ["identity_self_construction", "mind_speech_decision_language", "mind_structured_originality", "identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact", "identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact", "mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact"]
- chart_defining_override: `False`

### `uranus 1 ev`
- public_main_explicit_uses: `2`
- explicit_use_budget: `2`
- cluster_ids: ["identity_self_construction", "mind_speech_decision_language", "mind_structured_originality", "identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact", "identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact", "mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact"]
- chart_defining_override: `False`

### `section:chart_seed::saturn_sextile_uranus_structured_originality::mind`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["identity_self_construction", "mind_structured_originality", "identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact", "identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact"]
- chart_defining_override: `False`

### `chiron conjunct mc`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["career_healing_voice"]
- chart_defining_override: `True`

### `chiron 10 ev`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["career_healing_voice"]
- chart_defining_override: `False`

### `mc terazi`
- public_main_explicit_uses: `2`
- explicit_use_budget: `2`
- cluster_ids: ["career_healing_voice", "relationship_attachment_architecture", "relationship_affection_gift", "career_internal_visibility_maturation", "relationship_hidden_private_love_pattern"]
- chart_defining_override: `True`

### `jupiter square midheaven`
- public_main_explicit_uses: `2`
- explicit_use_budget: `2`
- cluster_ids: ["career_healing_voice", "relationship_attachment_architecture", "relationship_affection_gift", "career_internal_visibility_maturation", "relationship_hidden_private_love_pattern"]
- chart_defining_override: `True`

### `neptune square midheaven`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["career_healing_voice"]
- chart_defining_override: `True`

### `chiron conjunct midheaven`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["career_healing_voice"]
- chart_defining_override: `True`

### `section:chart_seed::chiron_conjunct_mc_visibility_wound_to_voice::career`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["career_healing_voice"]
- chart_defining_override: `True`

### `venus 12 ev yay`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["career_healing_voice", "relationship_attachment_architecture", "relationship_affection_gift", "career_internal_visibility_maturation", "relationship_hidden_private_love_pattern"]
- chart_defining_override: `False`

### `venus 12 ev`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["career_healing_voice", "relationship_attachment_architecture", "relationship_affection_gift", "career_internal_visibility_maturation", "relationship_hidden_private_love_pattern"]
- chart_defining_override: `False`

### `yay`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["career_healing_voice", "relationship_attachment_architecture", "relationship_affection_gift", "career_internal_visibility_maturation", "relationship_hidden_private_love_pattern"]
- chart_defining_override: `False`

### `moon trine venus`
- public_main_explicit_uses: `0`
- explicit_use_budget: `2`
- cluster_ids: ["career_healing_voice", "relationship_attachment_architecture", "relationship_affection_gift", "career_internal_visibility_maturation", "relationship_hidden_private_love_pattern"]
- chart_defining_override: `False`

### `venus in house 12`
- public_main_explicit_uses: `0`
- explicit_use_budget: `2`
- cluster_ids: ["career_healing_voice", "career_internal_visibility_maturation", "relationship_hidden_private_love_pattern"]
- chart_defining_override: `False`

### `venus conjunction vertex`
- public_main_explicit_uses: `0`
- explicit_use_budget: `2`
- cluster_ids: ["career_healing_voice", "relationship_affection_gift", "career_internal_visibility_maturation", "relationship_hidden_private_love_pattern"]
- chart_defining_override: `False`

### `section:chart_seed::venus_sagittarius_12h_hidden_expansive_love::relationship`
- public_main_explicit_uses: `0`
- explicit_use_budget: `2`
- cluster_ids: ["career_healing_voice", "career_internal_visibility_maturation", "relationship_hidden_private_love_pattern"]
- chart_defining_override: `False`

### `ay 8 ev aslan`
- public_main_explicit_uses: `0`
- explicit_use_budget: `2`
- cluster_ids: ["relationship_attachment_architecture"]
- chart_defining_override: `False`

### `7 ev yengec`
- public_main_explicit_uses: `0`
- explicit_use_budget: `2`
- cluster_ids: ["relationship_attachment_architecture"]
- chart_defining_override: `False`

### `ay 8 ev`
- public_main_explicit_uses: `0`
- explicit_use_budget: `2`
- cluster_ids: ["relationship_attachment_architecture", "relationship_affection_gift"]
- chart_defining_override: `False`

### `aslan`
- public_main_explicit_uses: `0`
- explicit_use_budget: `2`
- cluster_ids: ["relationship_attachment_architecture"]
- chart_defining_override: `False`

### `7th house ruler route`
- public_main_explicit_uses: `0`
- explicit_use_budget: `2`
- cluster_ids: ["relationship_attachment_architecture", "relationship_affection_gift"]
- chart_defining_override: `False`

### `section:chart_seed::moon_leo_8h_deep_proud_heart::relationship`
- public_main_explicit_uses: `0`
- explicit_use_budget: `2`
- cluster_ids: ["relationship_attachment_architecture"]
- chart_defining_override: `False`

### `section:relationships`
- public_main_explicit_uses: `0`
- explicit_use_budget: `2`
- cluster_ids: ["relationship_attachment_architecture"]
- chart_defining_override: `False`

### `thread:relationships_depth`
- public_main_explicit_uses: `0`
- explicit_use_budget: `2`
- cluster_ids: ["relationship_attachment_architecture"]
- chart_defining_override: `False`

### `10th house ruler route`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["relationship_attachment_architecture", "relationship_affection_gift", "career_internal_visibility_maturation", "relationship_hidden_private_love_pattern"]
- chart_defining_override: `False`

### `section:chart_seed::venus_sagittarius_12h_hidden_expansive_love::career`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["relationship_attachment_architecture", "relationship_affection_gift", "career_internal_visibility_maturation", "relationship_hidden_private_love_pattern"]
- chart_defining_override: `False`

### `section:career_visibility`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["relationship_attachment_architecture", "relationship_affection_gift", "career_internal_visibility_maturation", "relationship_hidden_private_love_pattern"]
- chart_defining_override: `False`

### `thread:career_visibility`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["relationship_attachment_architecture", "relationship_affection_gift", "career_internal_visibility_maturation", "relationship_hidden_private_love_pattern"]
- chart_defining_override: `False`

### `section:chart_seed::moon_trine_venus_emotional_warmth::relationship`
- public_main_explicit_uses: `0`
- explicit_use_budget: `2`
- cluster_ids: ["relationship_affection_gift"]
- chart_defining_override: `False`

### `ascendant capricorn`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["mind_speech_decision_language", "mind_structured_originality", "identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact", "mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact"]
- chart_defining_override: `True`

### `section:chart_seed::saturn_sextile_uranus_structured_originality::identity`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["mind_speech_decision_language", "mind_structured_originality", "identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact", "mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact"]
- chart_defining_override: `False`

### `saturn trine pluto`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact"]
- chart_defining_override: `False`

### `sun square saturn`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact"]
- chart_defining_override: `False`

### `mars opposite saturn`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact"]
- chart_defining_override: `False`

### `mars opposition saturn`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact"]
- chart_defining_override: `False`

### `section:chart_seed::saturn_trine_pluto_deep_resilience::identity`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact"]
- chart_defining_override: `False`

### `jupiter 1 ev`
- public_main_explicit_uses: `0`
- explicit_use_budget: `2`
- cluster_ids: ["mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact"]
- chart_defining_override: `False`

### `3th house ruler route`
- public_main_explicit_uses: `0`
- explicit_use_budget: `2`
- cluster_ids: ["mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact"]
- chart_defining_override: `False`

### `mercury conjunct jupiter`
- public_main_explicit_uses: `0`
- explicit_use_budget: `2`
- cluster_ids: ["mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact"]
- chart_defining_override: `False`

### `section:chart_seed::mercury_conjunct_jupiter_big_mind::mind`
- public_main_explicit_uses: `0`
- explicit_use_budget: `2`
- cluster_ids: ["mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact"]
- chart_defining_override: `False`

## 7. projection outputs after cluster integration

### profile_narrative_projection_v1
- source_graph: `natal_promise_cluster_plan_v1`
- source_graph_version: `natal_promise_cluster_plan_v1`
- blocks:
  - node_id: `promise::venus_sagittarius_12h_hidden_expansive_love_chart_exact`
    - headline: Bir şeyi hemen göstermekten çok, içine sindirip olgunlaştırmak senin ritmine daha yakın olabilir.
    - origin: `meaning_graph_v1_1_projection`
    - family: `visible_power`
    - chips: ["Kariyer", "Venüs · 12. ev · Yay", "MC Terazi"]
  - node_id: `promise::capricorn_asc_sun_1h_composed_self_construction_chart_exact`
    - headline: Az cümleyle sınır koyduğunda hem zihnin hem ritmin rahatlıyor; sende hız çoğu zaman bu sadeleşmeden geliyor.
    - origin: `meaning_graph_v1_1_projection`
    - family: `mind_mechanics`
    - chips: ["Kimlik", "Yükselen · Oğlak · Güneş 1. ev", "Yükselen Oğlak"]
  - node_id: `promise::saturn_3h_aries_speech_decision_language_chart_exact`
    - headline: Söz, ton ve karar dili sende kimliğe yakın bir yerden çalışıyor olabilir.
    - origin: `meaning_graph_v1_1_projection`
    - family: `mind_mechanics`
    - chips: ["Zihin", "Satürn · 3. ev · Koç", "Satürn 3. ev"]
  - node_id: `promise::chiron_conjunct_mc_visibility_wound_to_voice_chart_exact`
    - headline: Görünür olma hassasiyetini zamanla başkalarına dokunan bir sese çevirmek.
    - origin: `meaning_graph_v1_1_projection`
    - family: `contradiction_core`
    - chips: ["Kariyer", "Chiron conjunct MC", "Chiron 10. ev"]
  - node_id: `promise::moon_leo_8h_deep_proud_heart_chart_exact`
    - headline: Kalbin güven olmadan tam açılmıyor olabilir.
    - origin: `meaning_graph_v1_1_projection`
    - family: `intimacy_guard`
    - chips: ["İlişki", "Ay · 8. ev · Aslan", "7. ev Yengeç"]
  - node_id: `promise::mercury_conjunct_jupiter_big_mind_chart_exact`
    - headline: Senin zihnin tek tek parçalardan çok, aralarındaki anlamı kurmak ister.
    - origin: `meaning_graph_v1_1_projection`
    - family: `mind_mechanics`
    - chips: ["Zihin", "Mercury conjunction Jupiter", "Merkür 1. ev"]
  - node_id: `promise::moon_trine_venus_emotional_warmth_chart_exact`
    - headline: Kalbin birini sevdiğinde onu yalnızca sevmek değil, ona iyi gelmek de isteyebilir.
    - origin: `meaning_graph_v1_1_projection`
    - family: `intimacy_guard`
    - chips: ["İlişki", "Moon trine Venus", "Ay 8. ev"]
  - node_id: `promise::venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact`
    - headline: Bir şeyi hemen göstermekten çok, içine sindirip olgunlaştırmak senin ritmine daha yakın olabilir.
    - origin: `meaning_graph_v1_1_projection`
    - family: `visible_power`
    - chips: ["İlişki", "Venüs · 12. ev · Yay", "Venüs 12. ev"]

### profile_v8_projection_v1
- source_graph: `natal_promise_cluster_plan_v1`
- source_graph_version: `natal_promise_cluster_plan_v1`
- hero:
  - node_id: `promise::capricorn_asc_sun_1h_composed_self_construction_chart_exact`
  - headline: Az cümleyle sınır koyduğunda hem zihnin hem ritmin rahatlıyor; sende hız çoğu zaman bu sadeleşmeden geliyor.
- identity_axis:
  - node_id: `promise::saturn_3h_aries_speech_decision_language_chart_exact`
  - headline: Söz, ton ve karar dili sende kimliğe yakın bir yerden çalışıyor olabilir.
- insight_strip:
  - node_id: `promise::venus_sagittarius_12h_hidden_expansive_love_chart_exact`
    - label: Kariyer
    - title: Bir şeyi hemen göstermekten çok, içine sindirip olgunlaştırmak senin ritmine daha y…
  - node_id: `promise::moon_leo_8h_deep_proud_heart_chart_exact`
    - label: İlişki
    - title: Kalbin güven olmadan tam açılmıyor olabilir.
  - node_id: `promise::saturn_trine_pluto_deep_resilience_chart_exact`
    - label: Kimlik
    - title: Baskı arttığında sende panik değil, daha derin bir omurga devreye girebilir.
- differentiators:
  - node_id: `promise::moon_trine_venus_emotional_warmth_chart_exact`
    - headline: Kalbin birini sevdiğinde onu yalnızca sevmek değil, ona iyi gelmek de isteyebilir.
    - stat_label: hediye
  - node_id: `promise::saturn_sextile_uranus_structured_originality_chart_exact`
    - headline: Yeni fikri yalnızca bulmak değil, ona çalışır bir omurga vermek senin güçlü tarafın olabilir.
    - stat_label: hediye
  - node_id: `promise::chiron_conjunct_mc_visibility_wound_to_voice_chart_exact`
    - headline: Görünür olma hassasiyetini zamanla başkalarına dokunan bir sese çevirmek.
    - stat_label: dönüşüm

## 8. explicit pass/fail notes against rubric

- PASS: public main card count <= 7. Actual: `7`.
- PASS: identity/self-construction is at least surfaced and focus tier is `strong`.
- PASS: Venus 12H now appears in career and relationship cluster lines. Roles: `[('career', 'secondary_anchor'), ('relationship', 'secondary_anchor'), ('relationship', 'secondary_anchor'), ('career', 'primary_anchor'), ('career', 'secondary_anchor'), ('relationship', 'primary_anchor'), ('relationship', 'secondary_anchor')]`.
- MIXED: no suppressed packets emitted in this run, so suppression retention is still not exercised.
- PASS: v8 hero remains mind/identity, not relationship. Actual hero: `promise::capricorn_asc_sun_1h_composed_self_construction_chart_exact`.
- PASS: public schema does not expose cluster plan at top level. Actual: `False`.

### Rubric verdict
- PASS: candidate inventory is materially larger than 5. Current count is 11.
- PASS: key Sprint 1 packets are present again: `moon_trine_venus_emotional_warmth`, `saturn_sextile_uranus_structured_originality`, `venus_sagittarius_12h_hidden_expansive_love`, `capricorn_asc_sun_1h_composed_self_construction`, `saturn_3h_aries_speech_decision_language`, `moon_leo_8h_deep_proud_heart`, `chiron_conjunct_mc_visibility_wound_to_voice`, `saturn_trine_pluto_deep_resilience`, `mercury_conjunct_jupiter_big_mind`.
- PASS: mind is now `medium_strong` and relationship is `medium_strong` instead of collapsing to `detail_only`.
- PASS: career is now `strong`.
- PASS: action/pressure/resilience re-enters inventory via `saturn_trine_pluto_deep_resilience_chart_exact`.
- PASS: relationship subtype separation exists structurally across `attachment_architecture`, `affection_gift`, and `hidden_private_love_pattern` clusters/support clusters.
- MIXED: mind/identity duplication is improved because the main mind public-main packet is now `saturn_3h_aries_speech_decision_language_chart_exact`, not the Capricorn ASC packet. But the plan still surfaces additional identity-side public-main clusters (`identity_gift_like_*`) and may still be over-allocating self/pressure clusters into public main before suppression is doing enough work.
- MIXED: public-main count is valid at 7, but the feed still looks crowded. The source fix succeeded; the next remaining issue is cluster selection/suppression tuning, not source richness.
- MIXED: relationship is only `public_support`, not public main, despite a medium_strong focus map and three preserved subtype clusters. That is now a cluster selection policy question rather than a source-loss question.
- PASS: source-loss diagnosis from the previous audit is resolved. Candidate inventory is no longer constrained to lossy humanized surface text only.
