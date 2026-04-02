from app.natal.archetype_profile import build_archetype_profile, build_chart_prior


def _primitive_scores() -> dict:
    return {
        "primitive_scores": [
            {"primitive_id": "self_definition", "score": 0.82},
            {"primitive_id": "inner_structure", "score": 0.80},
            {"primitive_id": "methodical_drive", "score": 0.74},
            {"primitive_id": "public_refinement", "score": 0.68},
            {"primitive_id": "originality_drive", "score": 0.63},
            {"primitive_id": "big_picture_vision", "score": 0.56},
            {"primitive_id": "meaningful_expansion", "score": 0.51},
            {"primitive_id": "intimacy_depth", "score": 0.65},
            {"primitive_id": "transformative_bonding", "score": 0.58},
            {"primitive_id": "emotional_threshold", "score": 0.61},
            {"primitive_id": "recharge_through_home", "score": 0.46},
            {"primitive_id": "family_self_reliance", "score": 0.42},
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


def _contradictions() -> dict:
    return {
        "top_signatures": [
            {
                "id": "structure_vs_originality",
                "score": 0.72,
            }
        ]
    }


def _feature_graph() -> dict:
    return {
        "public_private_split": {
            "public_score": 0.69,
            "private_score": 0.44,
        }
    }


def test_chart_prior_prefers_builder_with_structured_identity_inputs() -> None:
    payload = build_chart_prior(
        primitive_scores=_primitive_scores(),
        master_selector=_master_selector(),
        contradiction_signatures=_contradictions(),
        natal_feature_graph=_feature_graph(),
    )

    assert payload["engine_version"] == "archetype_chart_prior_v1"
    assert payload["items"][0]["id"] == "builder"
    assert payload["items"][0]["components"]["slot_bonus"] > 0
    assert payload["items"][0]["matched_contradiction"] == "structure_vs_originality"


def test_archetype_profile_fuses_test_scores_and_returns_top_three() -> None:
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
        birth_time_confidence="exact",
        answer_consistency=0.83,
    )

    assert payload["engine_version"] == "archetype_profile_v1"
    assert payload["chart_prior"]["weight_profile"] == "default"
    assert len(payload["top_archetypes"]) == 3
    assert payload["top_archetypes"][0]["id"] == "builder"
    assert payload["primary_contradiction"]["id"] == "structure_vs_originality"
    assert payload["slots"]["primary_identity_spine"] == "builder"


def test_archetype_profile_uses_chart_only_when_test_absent() -> None:
    payload = build_archetype_profile(
        primitive_scores=_primitive_scores(),
        master_selector=_master_selector(),
        contradiction_signatures=_contradictions(),
        natal_feature_graph=_feature_graph(),
        birth_time_confidence="unknown",
    )

    assert payload["chart_prior"]["weight_profile"] == "chart_only"
    assert payload["test_scores"] == []
    assert payload["confidence"]["test"] == 0.0
    assert payload["top_archetypes"][0]["id"] == "builder"
