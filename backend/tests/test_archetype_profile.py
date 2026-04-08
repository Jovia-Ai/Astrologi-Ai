from app.natal.archetype_profile import build_archetype_profile, build_chart_prior


def _primitive_scores(overrides: dict[str, float] | None = None) -> dict:
    base = {
        "self_definition": 0.82,
        "inner_structure": 0.80,
        "methodical_drive": 0.74,
        "public_refinement": 0.68,
        "visible_presence": 0.54,
        "originality_drive": 0.63,
        "big_picture_vision": 0.56,
        "meaningful_expansion": 0.51,
        "mental_structuring": 0.78,
        "systems_thinking": 0.70,
        "network_luck": 0.34,
        "intimacy_depth": 0.65,
        "transformative_bonding": 0.58,
        "emotional_threshold": 0.61,
        "recharge_through_home": 0.46,
        "family_self_reliance": 0.42,
        "backstage_creation": 0.31,
        "push_pull_drive": 0.37,
    }
    if overrides:
        base.update(overrides)
    return {
        "primitive_scores": [
            {"primitive_id": primitive_id, "score": score}
            for primitive_id, score in base.items()
        ]
    }


def _master_selector() -> dict:
    return {
        "identity_spine": {
            "primary_identity_spine": {
                "source_primitives": ["self_definition", "inner_structure"],
                "confidence": 0.84,
            },
            "secondary_balancing_line": {
                "source_primitives": ["originality_drive", "big_picture_vision"],
                "confidence": 0.76,
            },
            "relational_line": {
                "source_primitives": ["intimacy_depth", "emotional_threshold"],
                "confidence": 0.67,
            },
            "work_visibility_line": {
                "source_primitives": ["public_refinement", "methodical_drive"],
                "confidence": 0.74,
            },
            "shadow_protection_line": {
                "source_primitives": ["emotional_threshold", "recharge_through_home"],
                "confidence": 0.63,
            },
        }
    }


def _contradictions(
    contradiction_id: str = "structure_vs_originality",
    score: float = 0.72,
) -> dict:
    return {
        "top_signatures": [
            {
                "id": contradiction_id,
                "score": score,
            }
        ]
    }


def _feature_graph(
    *,
    public_score: float = 0.69,
    private_score: float = 0.44,
) -> dict:
    return {
        "public_private_split": {
            "public_score": public_score,
            "private_score": private_score,
        }
    }


def test_chart_prior_prefers_builder_with_structured_identity_inputs() -> None:
    payload = build_chart_prior(
        primitive_scores=_primitive_scores(),
        master_selector=_master_selector(),
        contradiction_signatures=_contradictions(),
        natal_feature_graph=_feature_graph(),
    )

    assert payload["engine_version"] == "archetype_chart_prior_v2"
    assert payload["items"][0]["id"] == "builder"
    assert payload["items"][0]["components"]["slot_bonus"] > 0
    assert payload["items"][0]["matched_contradiction"] == "structure_vs_originality"


def test_archetype_profile_fuses_test_scores_and_keeps_legacy_fields() -> None:
    payload = build_archetype_profile(
        primitive_scores=_primitive_scores(),
        master_selector=_master_selector(),
        contradiction_signatures=_contradictions(),
        natal_feature_graph=_feature_graph(),
        test_scores={
            "builder": 0.88,
            "visionary": 0.62,
            "depthkeeper": 0.49,
            "guardian": 0.38,
        },
        question_family_scores={
            "structure_preference": 0.91,
            "mental_precision": 0.82,
            "execution_style": 0.78,
            "novelty_vs_structure": 0.64,
        },
        birth_time_confidence="exact",
        answer_consistency=0.83,
    )

    top = payload["top_archetypes"][0]

    assert payload["engine_version"] == "archetype_profile_v2"
    assert payload["chart_prior"]["weight_profile"] == "default"
    assert len(payload["top_archetypes"]) == 3
    assert top["id"] == "builder"
    assert top["subprofile_id"] == "systems_architect"
    assert top["subprofile_label_tr"] == "Sistem Mimari"
    assert top["mixins"]
    assert top["differentiators"]
    assert top["copy_variant"]
    assert top["why_this_not_that"]
    assert top["plain_summary_tr"]
    assert top["reasoning_tr"]
    assert top["portrait_tr"]
    assert top["gift_tr"]
    assert top["growth_tr"]
    assert top["copy_blocks"]["portrait_tr"] == top["portrait_tr"]
    assert top["copy_blocks"]["plain_summary_tr"] == top["plain_summary_tr"]
    assert payload["primary_contradiction"]["id"] == "structure_vs_originality"
    assert payload["slots"]["primary_identity_spine"] == "builder"
    assert payload["top_archetypes"][1]["mixins"] == []


def test_archetype_profile_uses_chart_only_when_test_absent() -> None:
    payload = build_archetype_profile(
        primitive_scores=_primitive_scores(),
        master_selector=_master_selector(),
        contradiction_signatures=_contradictions(),
        natal_feature_graph=_feature_graph(),
        birth_time_confidence="unknown",
        question_family_scores={
            "structure_preference": 0.88,
            "mental_precision": 0.84,
        },
    )

    assert payload["chart_prior"]["weight_profile"] == "chart_only"
    assert payload["test_scores"] == []
    assert payload["confidence"]["test"] == 0.0
    assert payload["top_archetypes"][0]["id"] == "builder"
    assert payload["top_archetypes"][0]["subprofile_is_softened"] is True
    assert payload["top_archetypes"][0]["subprofile_display_label_tr"] == ""
    assert "simdilik daha cok" in payload["top_archetypes"][0]["portrait_tr"]


def test_same_core_can_split_into_different_subprofiles() -> None:
    duty_payload = build_archetype_profile(
        primitive_scores=_primitive_scores(
            {
                "recharge_through_home": 0.74,
                "family_self_reliance": 0.70,
                "visible_presence": 0.28,
            }
        ),
        master_selector=_master_selector(),
        contradiction_signatures=_contradictions(
            "composure_vs_internal_pressure",
            score=0.79,
        ),
        natal_feature_graph=_feature_graph(public_score=0.34, private_score=0.82),
        test_scores={"builder": 0.93, "visionary": 0.44},
        question_family_scores={
            "responsibility_style": 0.96,
            "safety_needs": 0.88,
            "stress_regulation": 0.84,
            "execution_style": 0.79,
        },
        answer_consistency=0.88,
    )
    refinement_payload = build_archetype_profile(
        primitive_scores=_primitive_scores(
            {
                "public_refinement": 0.86,
                "visible_presence": 0.82,
                "recharge_through_home": 0.26,
            }
        ),
        master_selector=_master_selector(),
        contradiction_signatures=_contradictions(
            "visibility_vs_private_preparation",
            score=0.77,
        ),
        natal_feature_graph=_feature_graph(public_score=0.86, private_score=0.24),
        test_scores={"builder": 0.93, "visionary": 0.44},
        question_family_scores={
            "visibility_preference": 0.95,
            "expression_style": 0.92,
            "audience_energy": 0.86,
            "structure_preference": 0.72,
        },
        answer_consistency=0.88,
    )

    first = duty_payload["top_archetypes"][0]
    second = refinement_payload["top_archetypes"][0]

    assert first["id"] == "builder"
    assert second["id"] == "builder"
    assert first["subprofile_id"] == "duty_anchor"
    assert second["subprofile_id"] == "refinement_foreman"
    assert first["copy_variant"] != second["copy_variant"]


def test_mixins_shift_without_changing_core_or_subprofile() -> None:
    shared_scores = {
        "structure_preference": 0.93,
        "mental_precision": 0.88,
        "execution_style": 0.81,
        "novelty_vs_structure": 0.67,
    }
    backstage_payload = build_archetype_profile(
        primitive_scores=_primitive_scores(
            {
                "visible_presence": 0.26,
                "backstage_creation": 0.62,
                "recharge_through_home": 0.74,
            }
        ),
        master_selector=_master_selector(),
        contradiction_signatures=_contradictions(),
        natal_feature_graph=_feature_graph(public_score=0.18, private_score=0.86),
        test_scores={"builder": 0.91, "visionary": 0.48},
        question_family_scores=shared_scores,
        answer_consistency=0.86,
    )
    broadcast_payload = build_archetype_profile(
        primitive_scores=_primitive_scores(
            {
                "visible_presence": 0.88,
                "public_refinement": 0.82,
                "backstage_creation": 0.12,
                "recharge_through_home": 0.22,
            }
        ),
        master_selector=_master_selector(),
        contradiction_signatures=_contradictions(),
        natal_feature_graph=_feature_graph(public_score=0.88, private_score=0.18),
        test_scores={"builder": 0.91, "visionary": 0.48},
        question_family_scores=shared_scores,
        answer_consistency=0.86,
    )

    backstage_top = backstage_payload["top_archetypes"][0]
    broadcast_top = broadcast_payload["top_archetypes"][0]
    backstage_mixins = {
        mixin["id"]: mixin["value_id"] for mixin in backstage_top["mixins"]
    }
    broadcast_mixins = {
        mixin["id"]: mixin["value_id"] for mixin in broadcast_top["mixins"]
    }

    assert backstage_top["id"] == "builder"
    assert broadcast_top["id"] == "builder"
    assert backstage_top["subprofile_id"] == "systems_architect"
    assert broadcast_top["subprofile_id"] == "systems_architect"
    assert backstage_mixins["visibility_mode"] == "backstage"
    assert broadcast_mixins["visibility_mode"] == "broadcast"
    assert backstage_top["copy_variant"] != broadcast_top["copy_variant"]


def test_adaptive_questions_trigger_on_close_core_scores_and_stay_quiet_when_clear() -> None:
    ambiguous = build_archetype_profile(
        primitive_scores=_primitive_scores(
            {
                "originality_drive": 0.77,
                "big_picture_vision": 0.74,
                "meaningful_expansion": 0.70,
            }
        ),
        master_selector=_master_selector(),
        contradiction_signatures=_contradictions(),
        natal_feature_graph=_feature_graph(),
        test_scores={
            "builder": 0.73,
            "visionary": 0.88,
            "analyst": 0.45,
        },
        question_family_scores={
            "structure_preference": 0.81,
            "future_pull": 0.84,
            "meaning_orientation": 0.82,
            "novelty_vs_structure": 0.79,
        },
        answer_consistency=0.79,
    )
    clear = build_archetype_profile(
        primitive_scores=_primitive_scores(),
        master_selector=_master_selector(),
        contradiction_signatures=_contradictions(),
        natal_feature_graph=_feature_graph(),
        test_scores={
            "builder": 0.94,
            "visionary": 0.39,
            "analyst": 0.34,
        },
        question_family_scores={
            "structure_preference": 0.92,
            "mental_precision": 0.84,
        },
        answer_consistency=0.91,
    )

    assert ambiguous["adaptive"]["trigger_reason"] == "core_ambiguity"
    assert ambiguous["adaptive"]["families"]
    assert clear["adaptive"] == {"trigger_reason": "", "families": []}


def test_fixed_builder_cases_produce_distinct_identity_signatures() -> None:
    cases = [
        build_archetype_profile(
            primitive_scores=_primitive_scores(
                {
                    "recharge_through_home": 0.74,
                    "family_self_reliance": 0.72,
                    "visible_presence": 0.26,
                }
            ),
            master_selector=_master_selector(),
            contradiction_signatures=_contradictions(
                "composure_vs_internal_pressure",
                0.79,
            ),
            natal_feature_graph=_feature_graph(public_score=0.32, private_score=0.84),
            test_scores={"builder": 0.92},
            question_family_scores={
                "responsibility_style": 0.95,
                "stress_regulation": 0.86,
                "safety_needs": 0.84,
            },
            answer_consistency=0.87,
        ),
        build_archetype_profile(
            primitive_scores=_primitive_scores(
                {
                    "public_refinement": 0.88,
                    "visible_presence": 0.83,
                }
            ),
            master_selector=_master_selector(),
            contradiction_signatures=_contradictions(
                "visibility_vs_private_preparation",
                0.78,
            ),
            natal_feature_graph=_feature_graph(public_score=0.88, private_score=0.22),
            test_scores={"builder": 0.92},
            question_family_scores={
                "visibility_preference": 0.95,
                "expression_style": 0.90,
                "audience_energy": 0.86,
            },
            answer_consistency=0.87,
        ),
        build_archetype_profile(
            primitive_scores=_primitive_scores(
                {
                    "mental_structuring": 0.89,
                    "systems_thinking": 0.84,
                }
            ),
            master_selector=_master_selector(),
            contradiction_signatures=_contradictions(),
            natal_feature_graph=_feature_graph(public_score=0.54, private_score=0.54),
            test_scores={"builder": 0.92},
            question_family_scores={
                "structure_preference": 0.92,
                "mental_precision": 0.89,
                "execution_style": 0.83,
            },
            answer_consistency=0.87,
        ),
    ]

    signatures = {
        (
            payload["top_archetypes"][0]["id"],
            payload["top_archetypes"][0]["subprofile_id"],
            payload["top_archetypes"][0]["copy_variant"],
        )
        for payload in cases
    }

    assert all(payload["top_archetypes"][0]["id"] == "builder" for payload in cases)
    assert len(signatures) == len(cases)
