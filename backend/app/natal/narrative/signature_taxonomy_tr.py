from __future__ import annotations

from typing import Any, Dict, List


BLOCK_ALIAS_TO_TAXONOMY = {
    "identity_aura": "identity_aura",
    "mind_voice": "inner_system",
    "drive_rhythm": "talent_gifts",
    "love_depth": "love_depth",
    "career_visibility": "career_visibility",
    "home_roots": "home_roots",
    "luck_creation": "luck_flow",
}


TAXONOMY_V1_TR: List[Dict[str, Any]] = [
    {
        "block_id": "identity_aura",
        "goal": "Bu kişi nasıl biri?",
        "primitive_clusters": ["inner_structure", "self_definition", "originality_drive", "big_picture_vision", "visible_presence"],
        "priority_order": {
            "spine": ["inner_structure", "self_definition"],
            "spark": ["originality_drive", "big_picture_vision"],
            "tone": ["visible_presence"],
        },
        "astro_sources": {
            "spine": ["asc_sign", "chart_ruler", "first_house_emphasis"],
            "spark": ["angular_uranus", "jupiter_neptune_first", "sun_angular", "pluto_angular"],
            "tone": ["element_dominance", "modality_dominance", "saturnian_tone", "uranian_tone", "neptunian_tone"],
        },
        "signature_bundles": [
            "identity_structured_self",
            "identity_structured_but_original",
            "identity_visionary_but_grounded",
        ],
    },
    {
        "block_id": "inner_system",
        "goal": "Bu kişi içeride nasıl çalışıyor?",
        "primitive_clusters": ["tone_sensitivity", "inner_critic", "decision_rhythm", "mental_structuring", "push_pull_drive", "self_regulation"],
        "priority_order": {
            "spine": ["tone_sensitivity", "mental_structuring"],
            "spark": ["inner_critic", "push_pull_drive"],
            "tone": ["self_regulation"],
        },
        "astro_sources": {
            "spine": ["mercury", "third_house", "saturn"],
            "spark": ["mercury_saturn", "sun_saturn", "mars_saturn"],
            "tone": ["mercury_retro", "mutable_tone", "cardinal_tone"],
        },
        "signature_bundles": ["mind_structured_voice", "mind_refining_before_speaking", "drive_push_pull_refine"],
    },
    {
        "block_id": "talent_gifts",
        "goal": "Bu kişi nasıl üretir?",
        "primitive_clusters": ["systems_thinking", "meaning_making", "creative_synthesis", "refinement_drive", "implementation_power", "pattern_recognition"],
        "priority_order": {
            "spine": ["systems_thinking", "meaning_making"],
            "spark": ["creative_synthesis", "implementation_power"],
            "tone": ["refinement_drive"],
        },
        "astro_sources": {
            "spine": ["fifth_ninth_eleventh", "mercury", "mars", "jupiter"],
            "spark": ["mars_neptune", "mars_jupiter", "uranus_patterns"],
            "tone": ["virgo", "saturnian_tone", "uranian_tone"],
        },
        "signature_bundles": ["talent_meaning_into_system", "talent_vision_into_structure", "talent_refine_and_ship"],
    },
    {
        "block_id": "love_depth",
        "goal": "Bu kişi ilişkide nasıl bağ kuruyor?",
        "primitive_clusters": ["relational_security", "intimacy_depth", "emotional_threshold", "trust_testing", "attachment_style", "transformative_bonding"],
        "priority_order": {
            "spine": ["relational_security", "intimacy_depth"],
            "spark": ["emotional_threshold", "transformative_bonding"],
            "tone": ["attachment_style"],
        },
        "astro_sources": {
            "spine": ["seventh_house", "seventh_ruler", "moon", "venus"],
            "spark": ["eighth_house", "moon_pluto", "venus_saturn", "lilith"],
            "tone": ["water_tone", "saturnian_tone", "venusian_tone"],
        },
        "signature_bundles": ["love_depth_security", "love_intense_but_selective", "love_soft_but_guarded"],
    },
    {
        "block_id": "career_visibility",
        "goal": "Bu kişi toplumda nasıl görünür olur?",
        "primitive_clusters": ["public_refinement", "visibility_sensitivity", "role_awareness", "aesthetic_social_intelligence", "backstage_creation", "mastery_through_exposure"],
        "priority_order": {
            "spine": ["public_refinement", "role_awareness"],
            "spark": ["visibility_sensitivity", "backstage_creation"],
            "tone": ["mastery_through_exposure"],
        },
        "astro_sources": {
            "spine": ["mc", "tenth_house", "mc_ruler", "saturn"],
            "spark": ["chiron_tenth", "neptune_mc", "jupiter_mc", "venus_twelve"],
            "tone": ["venusian_tone", "saturnian_tone", "neptunian_tone"],
        },
        "signature_bundles": ["career_refined_visibility", "career_private_incubation", "career_visible_but_sensitive"],
    },
    {
        "block_id": "home_roots",
        "goal": "Bu kişi güveni ve köklenmeyi nasıl kuruyor?",
        "primitive_clusters": ["family_self_reliance", "recharge_through_home", "inner_safety_structure", "emotional_base", "protective_reflex"],
        "priority_order": {
            "spine": ["inner_safety_structure", "recharge_through_home"],
            "spark": ["family_self_reliance", "protective_reflex"],
            "tone": ["emotional_base"],
        },
        "astro_sources": {
            "spine": ["ic", "fourth_house", "moon", "saturn"],
            "spark": ["ic_mars", "moon_saturn", "moon_eighth", "pluto_fourth"],
            "tone": ["moon_tone", "mars_tone", "saturnian_tone"],
        },
        "signature_bundles": ["home_self_reliant_roots", "home_emotional_recharge", "home_private_intensity"],
    },
    {
        "block_id": "luck_flow",
        "goal": "Bu kişide fırsat nerede açılıyor?",
        "primitive_clusters": ["creation_luck", "network_luck", "visibility_luck", "steady_growth", "meaningful_expansion"],
        "priority_order": {
            "spine": ["meaningful_expansion", "creation_luck"],
            "spark": ["network_luck", "visibility_luck"],
            "tone": ["steady_growth"],
        },
        "astro_sources": {
            "spine": ["fortune", "jupiter", "fifth", "eleventh"],
            "spark": ["jupiter_neptune", "benefic_support", "fortune_ruler"],
            "tone": ["jupiterian_tone", "venusian_tone", "saturnian_tone"],
        },
        "signature_bundles": ["luck_creation_flow", "luck_network_lift", "luck_slow_but_stable"],
    },
]


TAXONOMY_BY_BLOCK_ID_TR: Dict[str, Dict[str, Any]] = {item["block_id"]: item for item in TAXONOMY_V1_TR}
