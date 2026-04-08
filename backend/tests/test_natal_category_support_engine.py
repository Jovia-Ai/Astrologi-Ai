from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_module():
    module_path = Path(__file__).resolve().parents[1] / "app" / "natal" / "category_support_engine.py"
    spec = importlib.util.spec_from_file_location("category_support_engine", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _rich_chart_data() -> dict:
    return {
        "birth_datetime": "1996-12-28T07:10:00+02:00",
        "angles": {
            "ascendant_sign": "Capricorn",
            "midheaven_sign": "Libra",
            "ic_sign": "Aries",
            "descendant_sign": "Cancer",
        },
    }


def _rich_planets() -> list[dict]:
    return [
        {"planet": "Sun", "sign": "Capricorn", "house": 1},
        {"planet": "Moon", "sign": "Leo", "house": 8},
        {"planet": "Mercury", "sign": "Capricorn", "house": 1},
        {"planet": "Venus", "sign": "Sagittarius", "house": 12},
        {"planet": "Mars", "sign": "Virgo", "house": 9},
        {"planet": "Jupiter", "sign": "Capricorn", "house": 1},
        {"planet": "Saturn", "sign": "Aries", "house": 3},
        {"planet": "Uranus", "sign": "Aquarius", "house": 1},
        {"planet": "Neptune", "sign": "Capricorn", "house": 1},
        {"planet": "Fortune", "sign": "Taurus", "house": 5},
    ]


def _rich_aspects() -> list[dict]:
    return [
        {"planet1": "Sun", "planet2": "Saturn", "type": "Square", "orb": 0.2},
        {"planet1": "Mars", "planet2": "Saturn", "type": "Opposition", "orb": 0.4},
        {"planet1": "Mercury", "planet2": "Jupiter", "type": "Conjunction", "orb": 0.6},
        {"planet1": "Moon", "planet2": "Venus", "type": "Trine", "orb": 0.2},
        {"planet1": "Jupiter", "planet2": "Fortune", "type": "Trine", "orb": 0.1},
        {"planet1": "Neptune", "planet2": "Midheaven", "type": "Square", "orb": 1.0},
    ]


def _rich_natal_graph() -> dict:
    return {
        "importance": {
            "Sun": 0.84,
            "Moon": 0.79,
            "Mercury": 0.73,
            "Venus": 0.7,
            "Mars": 0.71,
            "Jupiter": 0.76,
            "Saturn": 0.91,
            "Uranus": 0.68,
            "Neptune": 0.72,
            "Fortune": 0.63,
        },
        "house_rulers": {
            "1": {"cusp_sign": "Capricorn", "primary_ruler": "Saturn", "primary_ruler_pos": {"house": 3, "sign": "Aries"}},
            "3": {"cusp_sign": "Aquarius", "primary_ruler": "Saturn", "primary_ruler_pos": {"house": 1, "sign": "Capricorn"}},
            "4": {"cusp_sign": "Aries", "primary_ruler": "Mars", "primary_ruler_pos": {"house": 9, "sign": "Virgo"}},
            "5": {"cusp_sign": "Taurus", "primary_ruler": "Venus", "primary_ruler_pos": {"house": 12, "sign": "Sagittarius"}},
            "7": {"cusp_sign": "Cancer", "primary_ruler": "Moon", "primary_ruler_pos": {"house": 8, "sign": "Leo"}},
            "8": {"cusp_sign": "Leo", "primary_ruler": "Sun", "primary_ruler_pos": {"house": 1, "sign": "Capricorn"}},
            "10": {"cusp_sign": "Libra", "primary_ruler": "Venus", "primary_ruler_pos": {"house": 12, "sign": "Sagittarius"}},
        },
    }


def _rich_feature_graph() -> dict:
    return {
        "planet_salience": {
            "Sun": {"score": 0.84, "house": 1},
            "Moon": {"score": 0.78, "house": 8},
            "Mercury": {"score": 0.72, "house": 1},
            "Venus": {"score": 0.69, "house": 12},
            "Mars": {"score": 0.71, "house": 9},
            "Jupiter": {"score": 0.75, "house": 1},
            "Saturn": {"score": 0.92, "house": 3},
            "Neptune": {"score": 0.72, "house": 1},
            "Fortune": {"score": 0.64, "house": 5},
        },
        "repeated_motif_count": {
            "dominant_motifs": [
                {"id": "identity_structure", "score": 0.77},
                {"id": "language_boundary", "score": 0.73},
                {"id": "depth_intimacy", "score": 0.74},
                {"id": "thresholded_intimacy", "score": 0.71},
                {"id": "creative_flow", "score": 0.66},
                {"id": "visibility_sensitivity", "score": 0.68},
            ]
        },
    }


def _rich_contradictions() -> dict:
    return {
        "signatures": [
            {"id": "speed_vs_control", "score": 0.72, "slot_biases": ["secondary_balancing_line"]},
            {"id": "closeness_vs_threshold", "score": 0.69, "slot_biases": ["relational_line"]},
            {"id": "composure_vs_internal_pressure", "score": 0.67, "slot_biases": ["shadow_protection_line"]},
            {"id": "structure_vs_originality", "score": 0.64, "slot_biases": ["primary_identity_spine"]},
            {"id": "visibility_vs_private_preparation", "score": 0.63, "slot_biases": ["work_visibility_line"]},
        ]
    }


def _master_selector() -> dict:
    return {
        "identity_spine": {
            "primary_identity_spine": {"confidence": 0.8},
            "secondary_balancing_line": {"confidence": 0.76},
            "relational_line": {"confidence": 0.73},
            "work_visibility_line": {"confidence": 0.7},
            "shadow_protection_line": {"confidence": 0.62},
        }
    }


def _weak_chart_data() -> dict:
    return {
        "birth_datetime": "2000-01-01T12:00:00+03:00",
        "angles": {
            "ascendant_sign": "Gemini",
            "midheaven_sign": "Pisces",
            "ic_sign": "Virgo",
            "descendant_sign": "Sagittarius",
        },
    }


def _weak_planets() -> list[dict]:
    return [
        {"planet": "Mercury", "sign": "Aquarius", "house": 3},
        {"planet": "Mars", "sign": "Aquarius", "house": 6},
        {"planet": "Jupiter", "sign": "Gemini", "house": 1},
    ]


def _weak_natal_graph() -> dict:
    return {
        "importance": {"Mercury": 0.18, "Mars": 0.16, "Jupiter": 0.14},
        "house_rulers": {
            "3": {"cusp_sign": "Leo", "primary_ruler": "Sun", "primary_ruler_pos": {"house": 9, "sign": "Aquarius"}},
            "4": {"cusp_sign": "Virgo", "primary_ruler": "Mars", "primary_ruler_pos": {"house": 6, "sign": "Aquarius"}},
            "5": {"cusp_sign": "Libra", "primary_ruler": "Venus", "primary_ruler_pos": {"house": 11, "sign": "Aries"}},
            "7": {"cusp_sign": "Sagittarius", "primary_ruler": "Jupiter", "primary_ruler_pos": {"house": 1, "sign": "Gemini"}},
            "10": {"cusp_sign": "Pisces", "primary_ruler": "Jupiter", "primary_ruler_pos": {"house": 1, "sign": "Gemini"}},
        },
    }


def test_locked_category_inventory_remains_stable() -> None:
    module = _load_module()

    assert module.CATEGORY_FAMILY_BY_ID == {
        "identity_aura": "identity",
        "identity_mechanics": "identity",
        "mind_voice": "mind",
        "mind_system": "mind",
        "drive_rhythm": "drive",
        "love_depth": "intimacy",
        "relationships": "intimacy",
        "relationships_depth": "intimacy",
        "career_visibility": "visibility",
        "home_roots": "home",
        "luck_creation": "opportunity",
    }


def test_support_bundle_prefers_ruler_route_anchor_for_mind_and_is_deterministic() -> None:
    module = _load_module()

    first = module.build_natal_category_support_bundle(
        chart_data=_rich_chart_data(),
        planets=_rich_planets(),
        aspects=_rich_aspects(),
        natal_graph=_rich_natal_graph(),
        natal_feature_graph=_rich_feature_graph(),
        contradiction_signatures=_rich_contradictions(),
        master_selector=_master_selector(),
    )
    second = module.build_natal_category_support_bundle(
        chart_data=_rich_chart_data(),
        planets=_rich_planets(),
        aspects=_rich_aspects(),
        natal_graph=_rich_natal_graph(),
        natal_feature_graph=_rich_feature_graph(),
        contradiction_signatures=_rich_contradictions(),
        master_selector=_master_selector(),
    )

    assert first == second
    mind = first["by_id"]["mind_voice"]
    assert mind["primary_anchor"]["source_type"] == "ruler_route"
    assert mind["primary_anchor"]["source_ref"] == "house:3->ruler:Saturn->house:1"


def test_support_bundle_caps_evidence_and_uses_machine_readable_shape() -> None:
    module = _load_module()

    bundle = module.build_natal_category_support_bundle(
        chart_data=_rich_chart_data(),
        planets=_rich_planets(),
        aspects=_rich_aspects(),
        natal_graph=_rich_natal_graph(),
        natal_feature_graph=_rich_feature_graph(),
        contradiction_signatures=_rich_contradictions(),
        master_selector=_master_selector(),
    )

    for support in bundle["by_id"].values():
        assert support["primary_anchor"] is None or set(support["primary_anchor"]) == {
            "kind",
            "label",
            "source_type",
            "source_ref",
            "score",
        }
        assert len(support["supporting_combo"]) <= 3
        assert len(support["hidden_support"]) <= 2
        assert len(support["repeated_motifs"]) <= 3
        if support["contradiction_signature"] is not None:
            assert set(support["contradiction_signature"]) == {
                "kind",
                "label",
                "source_type",
                "source_ref",
                "score",
            }
        for field in ("supporting_combo", "hidden_support", "repeated_motifs"):
            for item in support[field]:
                assert set(item) == {
                    "kind",
                    "label",
                    "source_type",
                    "source_ref",
                    "score",
                }


def test_weak_category_support_is_sparse_and_apply_helpers_preserve_ids() -> None:
    module = _load_module()

    weak_bundle = module.build_natal_category_support_bundle(
        chart_data=_weak_chart_data(),
        planets=_weak_planets(),
        aspects=[],
        natal_graph=_weak_natal_graph(),
        natal_feature_graph={"planet_salience": {"Mars": {"score": 0.16, "house": 6}}},
        contradiction_signatures={"signatures": []},
        master_selector={"identity_spine": {}},
    )

    assert "home_roots" not in weak_bundle["by_id"]

    rich_bundle = module.build_natal_category_support_bundle(
        chart_data=_rich_chart_data(),
        planets=_rich_planets(),
        aspects=_rich_aspects(),
        natal_graph=_rich_natal_graph(),
        natal_feature_graph=_rich_feature_graph(),
        contradiction_signatures=_rich_contradictions(),
        master_selector=_master_selector(),
    )

    profile = {
        "profile_public": {
            "blocks": [
                {"id": "mind_voice", "headline": "Mind"},
                {"id": "career_visibility", "headline": "Career"},
            ]
        }
    }
    sections = [
        {"id": "mind_system", "title": "Mind"},
        {"id": "relationships", "title": "Relationships"},
    ]
    threads = [
        {"id": "identity_mechanics", "title": "Identity"},
        {"id": "relationships_depth", "title": "Relationships"},
    ]
    imprint = {
        "entries": [{"key": "saturn_house_3", "kind": "house_placement"}],
        "extra_entries": [{"key": "venus_house_12", "kind": "house_placement"}],
    }

    patched_profile = module.apply_category_support_to_profile_narrative(profile, rich_bundle)
    patched_sections = module.apply_category_support_to_sections(sections, rich_bundle)
    patched_threads = module.apply_category_support_to_threads(threads, rich_bundle)
    patched_imprint = module.apply_category_support_to_personality_imprint(imprint, rich_bundle)

    assert [block["id"] for block in patched_profile["profile_public"]["blocks"]] == ["mind_voice", "career_visibility"]
    assert patched_profile["profile_public"]["blocks"][0]["category_support"]["category_id"] == "mind_voice"
    assert patched_sections[0]["id"] == "mind_system"
    assert patched_sections[0]["category_support"]["category_id"] == "mind_system"
    assert patched_sections[0]["evidence"]
    assert patched_threads[0]["id"] == "identity_mechanics"
    assert patched_threads[0]["category_support"]["category_id"] == "identity_mechanics"
    assert patched_threads[0]["evidence"]
    assert patched_imprint["entries"][0]["category_support"]["category_id"] == "mind_voice"
    assert patched_imprint["extra_entries"][0]["category_support"]["category_id"] == "love_depth"
