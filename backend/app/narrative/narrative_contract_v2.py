from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


CONTRACT_VERSION = "narrative_v2_draft_2026_03"

NATAL_SECTION_PRIORITY_MATRIX: Dict[str, Dict[str, list[str]]] = {
    "hook": {
        "primary": ["aspect"],
        "secondary": ["house"],
        "contextual": ["ruler"],
    },
    "lived_experience": {
        "primary": ["aspect", "house"],
        "secondary": ["ruler"],
        "contextual": ["motif"],
    },
    "mechanism": {
        "primary": ["house", "ruler"],
        "secondary": ["aspect"],
        "contextual": ["dispositor"],
    },
    "reflex": {
        "primary": ["aspect"],
        "secondary": ["ruler"],
        "contextual": ["house"],
    },
    "gift": {
        "primary": ["aspect"],
        "secondary": ["house"],
        "contextual": ["ruler"],
    },
    "growth_edge": {
        "primary": ["ruler", "aspect"],
        "secondary": ["house"],
        "contextual": ["motif"],
    },
    "what_it_builds": {
        "primary": ["ruler"],
        "secondary": ["aspect"],
        "contextual": ["house"],
    },
    "technical_anchor": {
        "primary": ["house", "ruler", "aspect"],
        "secondary": ["graph"],
        "contextual": ["derived"],
    },
}

FIELD_SETS: Dict[str, list[str]] = {
    "natal": [
        "hook",
        "lived_experience",
        "mechanism",
        "reflex",
        "gift",
        "growth_edge",
        "what_it_builds",
        "technical_anchor",
    ],
    "transit_event": [
        "headline",
        "opening",
        "essence",
        "mechanism",
        "asks",
        "watchout",
        "what_it_builds",
        "technical_note",
    ],
    "period": [
        "period_opening",
        "big_picture",
        "mechanism",
        "growth_edge",
        "relational_or_life_expression",
        "what_it_builds",
        "technical_note",
    ],
}

HOOK_FAMILY_SPEC: Dict[str, Dict[str, Any]] = {
    "sharp": {
        "tone": "direct_recognition",
        "best_for": ["high_recognition", "clear_internal_contradiction", "pressure"],
        "guardrails": ["not_judgmental", "not_fatalistic", "not_labeling"],
    },
    "magnetic": {
        "tone": "deep_weighted_pull",
        "best_for": ["depth", "power", "pluto", "venus", "belonging", "angles"],
        "guardrails": ["not_theatrical", "not_mystical_overreach", "not_dark_romanticizing"],
    },
    "soft_striking": {
        "tone": "gentle_but_penetrating",
        "best_for": ["moon", "neptune", "sensitivity", "subtle_defense"],
        "guardrails": ["not_vague", "not_poetic_fog", "still_concrete"],
    },
    "builder": {
        "tone": "stable_developmental",
        "best_for": ["saturn", "mercury", "6th_house", "10th_house", "craft", "structure"],
        "guardrails": ["not_mechanical", "not_generic_coaching", "must_feel_human"],
    },
}

FALLBACK_RULES: Dict[str, Any] = {
    "activation_conditions": [
        "source_field_empty",
        "dedupe_removed_field",
        "specificity_filter_failed",
        "low_confidence_generation",
    ],
    "order": [
        "same_object_source_of_truth",
        "same_object_secondary_enrichment",
        "safe_local_rewrite",
        "minimal_generic_fallback",
    ],
    "never": [
        "period_into_event",
        "generic_risk_overrides_real_watchout",
        "supporting_thread_overrides_primary_natal_copy",
        "fallback_for_style_variety_only",
    ],
    "watchout_policy": {
        "preserve_event_specific": True,
        "allow_empty_if_no_real_risk": True,
        "append_generic_only_if_empty": True,
    },
}

MIGRATION_MAP: Dict[str, Dict[str, str]] = {
    "natal": {
        "core_story": "lived_experience + mechanism",
        "core_story_ui.headline": "hook",
        "upper_meaning": "growth_edge or what_it_builds",
        "supporting_threads": "secondary_contexts",
        "signature_motifs": "primary_aspect_bundles or secondary_contexts",
    },
    "transit_event": {
        "title": "headline",
        "teaser": "opening",
        "big_picture": "essence",
        "why_now": "mechanism or technical_note",
        "upper": "asks",
        "guidance": "what_it_builds or support",
        "conflict": "watchout",
        "shadow": "watchout_support",
    },
    "period": {
        "lead": "period_opening",
        "core_story": "big_picture",
        "contribution": "growth_edge",
        "upper_meaning": "what_it_builds",
    },
}


def build_contract_descriptor_v2() -> Dict[str, Any]:
    return deepcopy(
        {
            "contract_version": CONTRACT_VERSION,
            "section_priority_matrix": NATAL_SECTION_PRIORITY_MATRIX,
            "field_sets": FIELD_SETS,
            "hook_families": HOOK_FAMILY_SPEC,
            "fallback_rules": FALLBACK_RULES,
            "migration_map": MIGRATION_MAP,
        }
    )

