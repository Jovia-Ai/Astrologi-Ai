from __future__ import annotations

from typing import Dict, Any, List

# Psychology-first taxonomy for natal profile narrative.
# Purpose:
# astro facts -> primitive hits -> signature bundles -> selected blocks -> rendered narrative
#
# Each block defines:
# - goal: what user-facing question this block answers
# - primitive_clusters: all relevant psychological primitives
# - priority_order:
#     spine = primary identity of the block
#     spark = non-generic "main crater" primitives
#     tone  = style/texture modifiers
# - astro_sources:
#     which raw astro sources should mostly feed this block
# - signature_bundles:
#     preferred signature ids for this block
#
# Engine usage suggestion:
# 1) build primitive hits from chart + natal_graph
# 2) for each block:
#    - choose 1 spine signature
#    - choose 1 spark signature
#    - choose 0-1 tone modifier
# 3) rank with:
#    raw_signature_score
#    + taxonomy_slot_bonus
#    + primitive_cluster_match_bonus
#    + spark_bonus_if_missing
#    - duplication_penalty


BLOCK_ORDER_V1_TR: List[str] = [
    "identity_aura",
    "inner_system",
    "talent_gifts",
    "love_depth",
    "career_visibility",
    "home_roots",
    "luck_flow",
]

PRIMARY_BLOCKS_V1_TR: List[str] = [
    "identity_aura",
    "inner_system",
    "love_depth",
    "career_visibility",
]

SECONDARY_BLOCKS_V1_TR: List[str] = [
    "talent_gifts",
    "home_roots",
    "luck_flow",
]

TAXONOMY_V1_TR: Dict[str, Dict[str, Any]] = {
    "identity_aura": {
        "block_id": "identity_aura",
        "goal": "Bu kişi dışarıdan ve içeriden nasıl biri?",
        "primitive_clusters": [
            "inner_structure",
            "self_definition",
            "originality_drive",
            "big_picture_vision",
            "visible_presence",
            "personal_myth",
            "identity_tension",
        ],
        "priority_order": {
            "spine": [
                "inner_structure",
                "self_definition",
                "visible_presence",
            ],
            "spark": [
                "originality_drive",
                "big_picture_vision",
                "identity_tension",
                "personal_myth",
            ],
            "tone": [
                "saturnian_tone",
                "uranian_tone",
                "neptunian_tone",
                "plutonian_tone",
                "elemental_style",
                "modal_style",
            ],
        },
        "astro_sources": {
            "spine": [
                "asc_sign",
                "chart_ruler",
                "first_house_emphasis",
                "sun_house",
                "sun_aspect_pattern",
            ],
            "spark": [
                "angular_uranus",
                "uranus_first_house",
                "jupiter_neptune_first",
                "sun_angular",
                "pluto_angular",
                "first_house_stellium",
                "chart_ruler_loop",
            ],
            "tone": [
                "element_dominance",
                "modality_dominance",
                "saturn_signature",
                "uranus_signature",
                "neptune_signature",
                "pluto_signature",
            ],
        },
        "signature_bundles": [
            "identity_structured_self",
            "identity_structured_but_original",
            "identity_visionary_but_grounded",
            "identity_intense_presence",
            "identity_soft_but_strong",
            "identity_1st_stellium",
            "identity_uranus_angular",
            "identity_jupiter_neptune_vision",
            "identity_sun_angular",
            "spark_pluto_angular",
        ],
    },

    "inner_system": {
        "block_id": "inner_system",
        "goal": "Bu kişi içeride nasıl çalışıyor; zihni, kararı ve ritmi nasıl ilerliyor?",
        "primitive_clusters": [
            "tone_sensitivity",
            "inner_critic",
            "decision_rhythm",
            "mental_structuring",
            "push_pull_drive",
            "self_regulation",
            "cognitive_pressure",
            "precision_need",
        ],
        "priority_order": {
            "spine": [
                "mental_structuring",
                "decision_rhythm",
                "self_regulation",
            ],
            "spark": [
                "inner_critic",
                "push_pull_drive",
                "tone_sensitivity",
                "cognitive_pressure",
            ],
            "tone": [
                "mercurial_tone",
                "saturnian_tone",
                "mars_tone",
                "mutable_processing_style",
                "cardinal_processing_style",
            ],
        },
        "astro_sources": {
            "spine": [
                "mercury_condition",
                "third_house",
                "chart_ruler_to_third",
                "saturn_house",
                "mercury_house",
            ],
            "spark": [
                "sun_saturn_hard",
                "mercury_saturn_hard",
                "mars_saturn_hard",
                "mercury_retrograde",
                "saturn_to_asc",
                "third_house_ruler_patterns",
            ],
            "tone": [
                "mercury_signature",
                "saturn_signature",
                "mars_signature",
                "element_dominance",
                "modality_dominance",
            ],
        },
        "signature_bundles": [
            "mind_structured_voice",
            "mind_refining_before_speaking",
            "mind_precise_but_pressured",
            "mind_sensitive_to_tone",
            "mind_saturn_3rd_boundary",
            "mind_mercury_1st",
            "mind_mercury_rx_refine",
            "mind_sun_square_saturn_standard",
            "drive_mars_opp_saturn_push_pull",
        ],
    },

    "talent_gifts": {
        "block_id": "talent_gifts",
        "goal": "Bu kişi ne konuda doğal yetenekli; nasıl üretir, nasıl değer yaratır?",
        "primitive_clusters": [
            "systems_thinking",
            "meaning_making",
            "creative_synthesis",
            "refinement_drive",
            "implementation_power",
            "pattern_recognition",
            "translational_intelligence",
            "vision_to_structure",
        ],
        "priority_order": {
            "spine": [
                "systems_thinking",
                "meaning_making",
                "implementation_power",
            ],
            "spark": [
                "creative_synthesis",
                "vision_to_structure",
                "pattern_recognition",
                "translational_intelligence",
            ],
            "tone": [
                "technical_tone",
                "visionary_tone",
                "strategic_tone",
                "expressive_tone",
            ],
        },
        "astro_sources": {
            "spine": [
                "fifth_house",
                "ninth_house",
                "eleventh_house",
                "mercury_condition",
                "mars_condition",
                "jupiter_condition",
            ],
            "spark": [
                "mars_neptune_flow",
                "mars_jupiter_flow",
                "saturn_uranus_flow",
                "uranus_eleventh",
                "neptune_ninth",
                "dispositor_repetition_mercury_mars_jupiter",
            ],
            "tone": [
                "element_dominance",
                "modality_dominance",
                "uranus_signature",
                "neptune_signature",
                "mercury_signature",
            ],
        },
        "signature_bundles": [
            "talent_meaning_into_system",
            "talent_vision_into_structure",
            "talent_teach_and_build",
            "talent_refine_and_ship",
            "talent_innovative_frameworks",
            "drive_mars_9th_method",
            "drive_mars_trine_neptune_inspired_action",
            "drive_saturn_sextile_uranus_structured_change",
            "luck_fortune_5_creation",
        ],
    },

    "love_depth": {
        "block_id": "love_depth",
        "goal": "Bu kişi ilişkide nasıl bağ kuruyor; yakınlık, güven ve çekim nasıl çalışıyor?",
        "primitive_clusters": [
            "relational_security",
            "intimacy_depth",
            "emotional_threshold",
            "trust_testing",
            "attachment_style",
            "transformative_bonding",
            "devotional_love",
            "relational_intensity",
        ],
        "priority_order": {
            "spine": [
                "relational_security",
                "attachment_style",
                "intimacy_depth",
            ],
            "spark": [
                "emotional_threshold",
                "transformative_bonding",
                "relational_intensity",
                "trust_testing",
            ],
            "tone": [
                "moon_tone",
                "venusian_tone",
                "saturnian_tone",
                "plutonian_tone",
                "lilith_tone",
                "water_relational_style",
                "fire_relational_style",
            ],
        },
        "astro_sources": {
            "spine": [
                "seventh_house_sign",
                "seventh_ruler",
                "moon_condition",
                "venus_condition",
                "mars_condition",
            ],
            "spark": [
                "seventh_ruler_chain",
                "eighth_house",
                "moon_8th_or_12th",
                "moon_venus",
                "moon_pluto",
                "venus_saturn",
                "lilith_relational",
                "sun_to_dsc",
            ],
            "tone": [
                "moon_signature",
                "venus_signature",
                "saturn_signature",
                "pluto_signature",
                "lilith_signature",
            ],
        },
        "signature_bundles": [
            "love_depth_security",
            "love_intense_but_selective",
            "love_soft_but_guarded",
            "love_devotional_private",
            "love_friendship_to_bond",
            "love_7th_ruler_in_8th",
            "love_7th_ruler_in_11th_friends_to_love",
            "love_moon_in_8_intimacy_threshold",
            "love_moon_trine_venus_soft_bond",
            "love_venus_in_12_private_affection",
            "spark_venus_saturn_hard",
            "spark_moon_saturn_hard",
            "spark_moon_pluto_hard",
            "spark_venus_neptune_hard",
        ],
    },

    "career_visibility": {
        "block_id": "career_visibility",
        "goal": "Bu kişi toplumda nasıl parlıyor; kariyer ritmi ve görünürlük eşiği nasıl çalışıyor?",
        "primitive_clusters": [
            "public_refinement",
            "visibility_sensitivity",
            "role_awareness",
            "aesthetic_social_intelligence",
            "backstage_creation",
            "mastery_through_exposure",
            "public_authority",
            "career_threshold",
        ],
        "priority_order": {
            "spine": [
                "role_awareness",
                "public_refinement",
                "backstage_creation",
            ],
            "spark": [
                "visibility_sensitivity",
                "career_threshold",
                "mastery_through_exposure",
                "public_authority",
            ],
            "tone": [
                "venusian_tone",
                "saturnian_tone",
                "neptunian_tone",
                "jupiterian_tone",
                "chironic_tone",
            ],
        },
        "astro_sources": {
            "spine": [
                "mc_sign",
                "mc_ruler",
                "tenth_house",
                "saturn_condition",
                "venus_condition",
            ],
            "spark": [
                "mc_ruler_bucket",
                "jupiter_hard_mc",
                "neptune_hard_mc",
                "chiron_tenth",
                "pluto_mc",
                "uranus_mc",
            ],
            "tone": [
                "venus_signature",
                "saturn_signature",
                "neptune_signature",
                "jupiter_signature",
                "chiron_signature",
            ],
        },
        "signature_bundles": [
            "career_refined_visibility",
            "career_private_incubation",
            "career_visible_but_sensitive",
            "career_relational_authority",
            "career_builder_with_high_standard",
            "career_mc_ruler_12_backstage",
            "career_mc_square_neptune_or_jupiter_visibility_sensitivity",
            "career_chiron_10_heal_visibility",
            "career_mc_ruler_in_1_personal_brand",
            "career_mc_ruler_in_9_teach_expand",
            "career_mc_ruler_in_11_network_lift",
        ],
    },

    "home_roots": {
        "block_id": "home_roots",
        "goal": "Bu kişi güveni, köklenmeyi ve iç toparlanmayı nasıl kuruyor?",
        "primitive_clusters": [
            "family_self_reliance",
            "recharge_through_home",
            "inner_safety_structure",
            "emotional_base",
            "protective_reflex",
            "private_intensity",
            "home_as_reset",
        ],
        "priority_order": {
            "spine": [
                "inner_safety_structure",
                "recharge_through_home",
                "emotional_base",
            ],
            "spark": [
                "family_self_reliance",
                "protective_reflex",
                "private_intensity",
            ],
            "tone": [
                "mars_tone",
                "moon_tone",
                "saturnian_tone",
                "plutonian_tone",
                "venusian_tone",
            ],
        },
        "astro_sources": {
            "spine": [
                "ic_sign",
                "ic_ruler",
                "fourth_house",
                "moon_condition",
            ],
            "spark": [
                "moon_4th_8th_12th",
                "moon_saturn",
                "mars_on_ic",
                "aries_ic",
                "pluto_ic",
            ],
            "tone": [
                "moon_signature",
                "saturn_signature",
                "mars_signature",
                "pluto_signature",
                "venus_signature",
            ],
        },
        "signature_bundles": [
            "home_self_reliant_roots",
            "home_emotional_recharge",
            "home_control_as_safety",
            "home_private_intensity",
            "home_family_duty",
            "home_ic_aries_independence",
            "home_moon_recharge_deep",
        ],
    },

    "luck_flow": {
        "block_id": "luck_flow",
        "goal": "Bu kişide fırsat nerede açılıyor; şans hangi sahnede daha kolay akıyor?",
        "primitive_clusters": [
            "creation_luck",
            "network_luck",
            "visibility_luck",
            "steady_growth",
            "meaningful_expansion",
            "earned_opportunity",
            "flow_through_expression",
        ],
        "priority_order": {
            "spine": [
                "steady_growth",
                "meaningful_expansion",
                "creation_luck",
            ],
            "spark": [
                "network_luck",
                "visibility_luck",
                "flow_through_expression",
            ],
            "tone": [
                "jupiterian_tone",
                "venusian_tone",
                "saturnian_tone",
                "uranian_tone",
                "neptunian_tone",
            ],
        },
        "astro_sources": {
            "spine": [
                "fortune_sign_house",
                "fortune_ruler",
                "jupiter_condition",
                "second_house",
                "fifth_house",
                "eleventh_house",
            ],
            "spark": [
                "fortune_benefic_aspects",
                "jupiter_neptune",
                "jupiter_eleventh",
                "venus_jupiter",
                "uranian_breakthrough",
            ],
            "tone": [
                "jupiter_signature",
                "venus_signature",
                "saturn_signature",
                "uranus_signature",
                "neptune_signature",
            ],
        },
        "signature_bundles": [
            "luck_creation_flow",
            "luck_network_lift",
            "luck_visibility_through_output",
            "luck_slow_but_stable",
            "luck_expands_when_shared",
            "luck_fortune_5_creation",
        ],
    },
}


PRIMITIVE_REGISTRY_V1_TR: Dict[str, Dict[str, Any]] = {
    "inner_structure": {
        "label": "İç omurga",
        "theme_bias": ["identity_aura", "inner_system"],
        "description_debug": "Kişi güveni çerçeve, yapı ve iç düzen üzerinden kurar.",
        "possible_chips": ["Omurga", "Netlik", "Çerçeve"],
        "tone_tags": ["saturnian_tone", "earth_style"],
    },
    "self_definition": {
        "label": "Kendini tanımlama",
        "theme_bias": ["identity_aura"],
        "description_debug": "Benlik sınırları ve kendini ortaya koyma biçimi güçlüdür.",
        "possible_chips": ["Duruş", "Kimlik", "Kendi Çizgin"],
        "tone_tags": ["visible_presence"],
    },
    "originality_drive": {
        "label": "Özgünlük dürtüsü",
        "theme_bias": ["identity_aura", "talent_gifts"],
        "description_debug": "Kişi sıradan kalmak istemez; kendi yolunu icat etme ihtiyacı taşır.",
        "possible_chips": ["Özgün Yol", "Elektrik", "Farklı Frekans"],
        "tone_tags": ["uranian_tone"],
    },
    "big_picture_vision": {
        "label": "Büyük resim vizyonu",
        "theme_bias": ["identity_aura", "talent_gifts", "luck_flow"],
        "description_debug": "Kişi yalnızca ayrıntıyı değil anlamı ve bütün resmi de duyar.",
        "possible_chips": ["Büyük Resim", "Vizyon", "Sezgi"],
        "tone_tags": ["neptunian_tone", "jupiterian_tone"],
    },
    "visible_presence": {
        "label": "Görünür etki",
        "theme_bias": ["identity_aura", "career_visibility"],
        "description_debug": "Kişi girdiği ortamda hissedilir bir varlık/ağırlık bırakır.",
        "possible_chips": ["Etki", "Duruş", "Varlık"],
        "tone_tags": ["solar_tone", "plutonian_tone"],
    },
    "tone_sensitivity": {
        "label": "Ton hassasiyeti",
        "theme_bias": ["inner_system"],
        "description_debug": "Kişi yalnızca ne dediğine değil, nasıl duyulduğuna da dikkat eder.",
        "possible_chips": ["Ton", "İfade", "İncelik"],
        "tone_tags": ["mercurial_tone", "saturnian_tone"],
    },
    "inner_critic": {
        "label": "İç eleştirmen",
        "theme_bias": ["inner_system", "career_visibility"],
        "description_debug": "Standart yüksektir; kişi kendini ciddi biçimde tartar.",
        "possible_chips": ["Standart", "Sorumluluk", "Ustalık"],
        "tone_tags": ["saturnian_tone"],
    },
    "decision_rhythm": {
        "label": "Karar ritmi",
        "theme_bias": ["inner_system"],
        "description_debug": "Karar verme biçimi hız–kontrol dengesiyle çalışır.",
        "possible_chips": ["Ritim", "Karar", "Tempo"],
        "tone_tags": ["cardinal_processing_style", "mutable_processing_style"],
    },
    "mental_structuring": {
        "label": "Zihinsel yapı kurma",
        "theme_bias": ["inner_system", "talent_gifts"],
        "description_debug": "Kişi düşünceyi yapılandırır, ayıklar, organize eder.",
        "possible_chips": ["Zihin Gücü", "Yapı", "Netleştir"],
        "tone_tags": ["mercurial_tone", "saturnian_tone"],
    },
    "push_pull_drive": {
        "label": "İtki–fren dinamiği",
        "theme_bias": ["inner_system", "talent_gifts"],
        "description_debug": "Kişi aynı anda başlamak ve durup düzeltmek arasında çekilebilir.",
        "possible_chips": ["İtki–Fren", "Başlat–Rafine", "Süreklilik"],
        "tone_tags": ["mars_tone", "saturnian_tone"],
    },
    "self_regulation": {
        "label": "Kendini düzenleme",
        "theme_bias": ["inner_system", "home_roots"],
        "description_debug": "Kişi ritim, düzen ve çerçeve ile kendini toparlar.",
        "possible_chips": ["Denge", "Ritim", "Toparlanma"],
        "tone_tags": ["saturnian_tone"],
    },
    "systems_thinking": {
        "label": "Sistem düşüncesi",
        "theme_bias": ["talent_gifts"],
        "description_debug": "Kişi dağınık şeyler arasında bağlantı kurup yapı üretir.",
        "possible_chips": ["Sistem", "Çerçeve", "Yapı Kur"],
        "tone_tags": ["technical_tone", "strategic_tone"],
    },
    "meaning_making": {
        "label": "Anlam kurma",
        "theme_bias": ["talent_gifts", "identity_aura"],
        "description_debug": "Kişi deneyimi daha büyük bir anlam ağına bağlama eğilimindedir.",
        "possible_chips": ["Anlam", "Derinlik", "Vizyon"],
        "tone_tags": ["visionary_tone", "neptunian_tone"],
    },
    "creative_synthesis": {
        "label": "Yaratıcı sentez",
        "theme_bias": ["talent_gifts"],
        "description_debug": "Kişi farklı parçaları birleştirip yeni form çıkarabilir.",
        "possible_chips": ["Yaratıcı Zeka", "Sentez", "Birleştir"],
        "tone_tags": ["visionary_tone", "expressive_tone"],
    },
    "refinement_drive": {
        "label": "Rafine etme dürtüsü",
        "theme_bias": ["talent_gifts", "career_visibility"],
        "description_debug": "Kişi bir şeyi daha iyi, daha temiz, daha etkili hale getirmek ister.",
        "possible_chips": ["Rafine Et", "İyileştir", "Ustalık"],
        "tone_tags": ["technical_tone", "saturnian_tone"],
    },
    "implementation_power": {
        "label": "Uygulamaya indirme gücü",
        "theme_bias": ["talent_gifts", "career_visibility"],
        "description_debug": "Kişi fikri sonuç ve çıktı düzeyine indirebilir.",
        "possible_chips": ["Çıktı", "Uygula", "Gerçekleştir"],
        "tone_tags": ["strategic_tone", "mars_tone"],
    },
    "pattern_recognition": {
        "label": "Pattern görme",
        "theme_bias": ["talent_gifts", "inner_system"],
        "description_debug": "Kişi tekrar eden desenleri ve sistem mantığını fark eder.",
        "possible_chips": ["Pattern", "Görü", "Bağlantı"],
        "tone_tags": ["visionary_tone", "technical_tone"],
    },
    "relational_security": {
        "label": "İlişkisel güven",
        "theme_bias": ["love_depth"],
        "description_debug": "İlişkide güven ve zeminin öncelikli olması.",
        "possible_chips": ["Güven", "Zemin", "Tutarlılık"],
        "tone_tags": ["moon_tone", "water_relational_style"],
    },
    "intimacy_depth": {
        "label": "Yakınlık derinliği",
        "theme_bias": ["love_depth"],
        "description_debug": "Bağların yüzeyde kalmaması, derinleşme ihtiyacı.",
        "possible_chips": ["Derinlik", "Yakınlık", "Gerçek Temas"],
        "tone_tags": ["plutonian_tone", "water_relational_style"],
    },
    "emotional_threshold": {
        "label": "Duygusal eşik",
        "theme_bias": ["love_depth"],
        "description_debug": "Yakınlık arttığında içerde test/eşik çalışması.",
        "possible_chips": ["Eşik", "Savunma", "Açılma"],
        "tone_tags": ["moon_tone", "saturnian_tone"],
    },
    "trust_testing": {
        "label": "Güven testi",
        "theme_bias": ["love_depth"],
        "description_debug": "Kişi bağda söz–davranış uyumunu ve istikrarı test eder.",
        "possible_chips": ["Test", "Tutarlılık", "Gerçeklik"],
        "tone_tags": ["saturnian_tone"],
    },
    "attachment_style": {
        "label": "Bağlanma tarzı",
        "theme_bias": ["love_depth"],
        "description_debug": "Kişinin duygusal bağ kurma ritmi ve açılma biçimi.",
        "possible_chips": ["Bağ", "Açılma", "Yakınlık Ritmi"],
        "tone_tags": ["moon_tone", "venusian_tone"],
    },
    "transformative_bonding": {
        "label": "Dönüştürücü bağ",
        "theme_bias": ["love_depth"],
        "description_debug": "İlişkiler kişinin iç dünyasında derin değişim yaratır.",
        "possible_chips": ["Dönüşüm", "Mahremiyet", "Derin Bağ"],
        "tone_tags": ["plutonian_tone", "lilith_tone"],
    },
    "public_refinement": {
        "label": "Kamusal rafinelik",
        "theme_bias": ["career_visibility"],
        "description_debug": "Kişi toplum önünde estetik, denge ve doğru bağlamla parlamak ister.",
        "possible_chips": ["Zarif Etki", "Sunum", "Bağlam"],
        "tone_tags": ["venusian_tone"],
    },
    "visibility_sensitivity": {
        "label": "Görünürlük hassasiyeti",
        "theme_bias": ["career_visibility"],
        "description_debug": "Kişi görünür olduğunda ekstra hassasiyet ve standart hissedebilir.",
        "possible_chips": ["Vitrin Eşiği", "Hazır mıyım?", "İz Bırak"],
        "tone_tags": ["neptunian_tone", "chironic_tone"],
    },
    "role_awareness": {
        "label": "Rol farkındalığı",
        "theme_bias": ["career_visibility", "identity_aura"],
        "description_debug": "Kişi toplum içindeki rolünü ciddiye alır; yön verme isteği vardır.",
        "possible_chips": ["Rol", "Yön", "Toplumsal Etki"],
        "tone_tags": ["saturnian_tone", "venusian_tone"],
    },
    "aesthetic_social_intelligence": {
        "label": "Sosyal estetik zeka",
        "theme_bias": ["career_visibility", "love_depth"],
        "description_debug": "Kişi insan ilişkileri, denge ve sunumda doğal sezgi taşır.",
        "possible_chips": ["Sosyal Zeka", "Denge", "İnsan İlişkisi"],
        "tone_tags": ["venusian_tone"],
    },
    "backstage_creation": {
        "label": "Perde arkası üretim",
        "theme_bias": ["career_visibility", "talent_gifts"],
        "description_debug": "Kişi işini önce içeride olgunlaştırıp sonra paylaşmayı sever.",
        "possible_chips": ["Pişirip Çık", "İnkübasyon", "Perde Arkası"],
        "tone_tags": ["neptunian_tone", "venusian_tone"],
    },
    "mastery_through_exposure": {
        "label": "Görünerek ustalaşma",
        "theme_bias": ["career_visibility"],
        "description_debug": "Kişi görünürlükten çekinse bile görünerek büyür ve ustalaşır.",
        "possible_chips": ["Ustalık", "Vitrin", "Gelişim"],
        "tone_tags": ["saturnian_tone", "solar_tone"],
    },
    "family_self_reliance": {
        "label": "Ailede öz yeterlilik",
        "theme_bias": ["home_roots"],
        "description_debug": "Köklerde ‘ben hallederim’ refleksi gelişmiş olabilir.",
        "possible_chips": ["Bağımsızlık", "Kendin Hallet", "İnisiyatif"],
        "tone_tags": ["mars_tone", "saturnian_tone"],
    },
    "recharge_through_home": {
        "label": "Evde şarj olma",
        "theme_bias": ["home_roots"],
        "description_debug": "Ev, kişi için sinir sistemi regülasyonu ve toparlanma alanıdır.",
        "possible_chips": ["Şarj", "Ev Ritmi", "Toparlanma"],
        "tone_tags": ["moon_tone"],
    },
    "inner_safety_structure": {
        "label": "İç güven zemini",
        "theme_bias": ["home_roots", "inner_system"],
        "description_debug": "Kişi içerde güveni düzen ve zemin üzerinden kurar.",
        "possible_chips": ["Güven Zemini", "İç Alan", "Ritim"],
        "tone_tags": ["saturnian_tone", "moon_tone"],
    },
    "emotional_base": {
        "label": "Duygusal taban",
        "theme_bias": ["home_roots", "love_depth"],
        "description_debug": "İç dünyadaki duygusal temel ve korunma ihtiyacı.",
        "possible_chips": ["Kök Duygu", "İç Güven", "Korunma"],
        "tone_tags": ["moon_tone"],
    },
    "protective_reflex": {
        "label": "Koruma refleksi",
        "theme_bias": ["home_roots", "love_depth"],
        "description_debug": "Güven sarsıldığında kendini ya da alanını hızlıca korumaya alma.",
        "possible_chips": ["Koruma", "Savunma", "Alan"],
        "tone_tags": ["mars_tone", "saturnian_tone"],
    },
    "creation_luck": {
        "label": "Yaratım şansı",
        "theme_bias": ["luck_flow", "talent_gifts"],
        "description_debug": "Fırsat üretim, yaratım ve kendini ifade ettiğinde açılır.",
        "possible_chips": ["Yaratım", "Akış", "Somutlaştır"],
        "tone_tags": ["venusian_tone", "jupiterian_tone"],
    },
    "network_luck": {
        "label": "Network şansı",
        "theme_bias": ["luck_flow", "career_visibility"],
        "description_debug": "Fırsat doğru insan, bağlam ve ekiplerle hızlanır.",
        "possible_chips": ["Network", "Bağlantı", "Kaldıraç"],
        "tone_tags": ["jupiterian_tone", "uranian_tone"],
    },
    "visibility_luck": {
        "label": "Görünürlük şansı",
        "theme_bias": ["luck_flow", "career_visibility"],
        "description_debug": "Fırsat görünür çıktılar ve kamusal iz bırakma ile açılır.",
        "possible_chips": ["Vitrin", "İz Bırak", "Paylaş"],
        "tone_tags": ["solar_tone", "jupiterian_tone"],
    },
    "steady_growth": {
        "label": "İstikrarlı büyüme",
        "theme_bias": ["luck_flow", "career_visibility"],
        "description_debug": "Şans ani patlamadan çok düzenli büyüme şeklinde çalışır.",
        "possible_chips": ["İstikrar", "Adım Adım", "Büyüme"],
        "tone_tags": ["saturnian_tone", "earth_style"],
    },
    "meaningful_expansion": {
        "label": "Anlamlı genişleme",
        "theme_bias": ["luck_flow", "identity_aura"],
        "description_debug": "Fırsat yalnızca büyütmez; aynı zamanda kişiye anlam hissi verir.",
        "possible_chips": ["Anlam", "Genişleme", "Doğru Yön"],
        "tone_tags": ["jupiterian_tone", "neptunian_tone"],
    },
}


def get_taxonomy_block(block_id: str) -> Dict[str, Any]:
    return TAXONOMY_V1_TR[block_id]


def get_block_order() -> List[str]:
    return list(BLOCK_ORDER_V1_TR)
