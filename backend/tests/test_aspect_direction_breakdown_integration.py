"""Faz 2 PR 8a integration: aspect_direction_breakdown wire through
build_archetype_profile. Explainability-only — scoring davranışını
değiştirmez.
"""
from __future__ import annotations

from typing import Any, Dict

import pytest

from app.natal.archetype_profile import build_archetype_profile


# --------------------------------------------------------------------------
# Shared builders
# --------------------------------------------------------------------------


def _primitive_scores() -> Dict[str, Any]:
    return {
        "primitive_scores": [
            {"primitive_id": "self_definition", "score": 0.82},
            {"primitive_id": "inner_structure", "score": 0.80},
            {"primitive_id": "methodical_drive", "score": 0.74},
            {"primitive_id": "public_refinement", "score": 0.68},
            {"primitive_id": "mental_structuring", "score": 0.78},
            {"primitive_id": "intimacy_depth", "score": 0.65},
        ]
    }


def _master_selector() -> Dict[str, Any]:
    return {
        "identity_spine": {
            "primary_identity_spine": {
                "source_primitives": ["self_definition", "inner_structure"],
                "confidence": 0.84,
            },
            "secondary_balancing_line": {
                "source_primitives": ["originality_drive"],
                "confidence": 0.76,
            },
            "relational_line": {
                "source_primitives": ["intimacy_depth"],
                "confidence": 0.67,
            },
            "work_visibility_line": {
                "source_primitives": ["public_refinement"],
                "confidence": 0.74,
            },
            "shadow_protection_line": {
                "source_primitives": ["emotional_threshold"],
                "confidence": 0.63,
            },
        }
    }


def _inputs(**overrides) -> Dict[str, Any]:
    defaults: Dict[str, Any] = dict(
        primitive_scores=_primitive_scores(),
        master_selector=_master_selector(),
        contradiction_signatures={"top_signatures": []},
        natal_feature_graph={"public_private_split": {"public_score": 0.6, "private_score": 0.5}},
        test_scores={"builder": 0.88, "visionary": 0.55},
        question_family_scores={},
        birth_time_confidence="exact",
        answer_consistency=0.83,
    )
    defaults.update(overrides)
    return defaults


def _a(p1: str, p2: str, direction: str | None) -> Dict[str, Any]:
    return {"planet1": p1, "planet2": p2, "aspect": "conjunction", "orb": 2.0, "direction": direction}


# --------------------------------------------------------------------------
# Every archetype gets aspect_direction_breakdown field
# --------------------------------------------------------------------------


def test_every_top_archetype_has_breakdown_field() -> None:
    payload = build_archetype_profile(**_inputs(
        chart_aspects=[_a("Saturn", "Moon", "applying")],
    ))
    for item in payload["top_archetypes"]:
        assert "aspect_direction_breakdown" in item
        breakdown = item["aspect_direction_breakdown"]
        assert set(breakdown.keys()) == {"applying", "separating", "exact", "unknown"}


def test_legacy_call_without_chart_aspects_all_zero() -> None:
    """chart_aspects geçilmezse tüm breakdown all-zero (zero-diff fallback)."""
    payload = build_archetype_profile(**_inputs())
    for item in payload["top_archetypes"]:
        assert item["aspect_direction_breakdown"] == {
            "applying": 0, "separating": 0, "exact": 0, "unknown": 0,
        }


def test_empty_chart_aspects_all_zero() -> None:
    payload = build_archetype_profile(**_inputs(chart_aspects=[]))
    for item in payload["top_archetypes"]:
        assert item["aspect_direction_breakdown"] == {
            "applying": 0, "separating": 0, "exact": 0, "unknown": 0,
        }


# --------------------------------------------------------------------------
# Hero chart: Saturn-heavy aspects → builder breakdown reflects it
# --------------------------------------------------------------------------


def test_saturn_heavy_chart_reflects_in_builder_breakdown() -> None:
    """Builder signature=Saturn. Chart'ta 4 Saturn aspect: 2 applying,
    1 separating, 1 exact → breakdown (2, 1, 1, 0)."""
    chart_aspects = [
        _a("Saturn", "Moon", "applying"),
        _a("Saturn", "Venus", "applying"),
        _a("Saturn", "Sun", "separating"),
        _a("Saturn", "Mars", "exact"),
        _a("Venus", "Mercury", "applying"),   # Saturn yok → builder'a sayılmaz
        _a("Jupiter", "Mars", "separating"),
    ]
    payload = build_archetype_profile(**_inputs(chart_aspects=chart_aspects))
    builder = next(
        (item for item in payload["top_archetypes"] if item["id"] == "builder"),
        None,
    )
    assert builder is not None
    assert builder["aspect_direction_breakdown"] == {
        "applying": 2, "separating": 1, "exact": 1, "unknown": 0,
    }


def test_different_archetypes_have_different_breakdowns() -> None:
    """Her arketip kendi signature planetinin aspect'lerini sayar —
    farklı arketipler farklı count'lar görür."""
    chart_aspects = [
        _a("Saturn", "Moon", "applying"),           # builder, guardian
        _a("Jupiter", "Sun", "applying"),           # visionary
        _a("Venus", "Mars", "separating"),          # connector, depthkeeper, catalyst
        _a("Mercury", "Saturn", "exact"),           # analyst, builder, guardian
    ]
    payload = build_archetype_profile(**_inputs(chart_aspects=chart_aspects))
    by_id = {item["id"]: item["aspect_direction_breakdown"] for item in payload["top_archetypes"]}

    # Top 3 bu setup'ta büyük olasılıkla: builder, visionary, depthkeeper
    if "builder" in by_id:
        # Saturn → Saturn-Moon (applying), Mercury-Saturn (exact)
        assert by_id["builder"]["applying"] == 1
        assert by_id["builder"]["exact"] == 1
    if "visionary" in by_id:
        # Jupiter → Jupiter-Sun (applying)
        assert by_id["visionary"]["applying"] == 1


# --------------------------------------------------------------------------
# Unknown direction bucket works through pipeline
# --------------------------------------------------------------------------


def test_none_direction_lands_in_unknown() -> None:
    chart_aspects = [
        _a("Saturn", "Moon", None),
        _a("Saturn", "Venus", "applying"),
    ]
    payload = build_archetype_profile(**_inputs(chart_aspects=chart_aspects))
    builder = next(item for item in payload["top_archetypes"] if item["id"] == "builder")
    assert builder["aspect_direction_breakdown"]["unknown"] == 1
    assert builder["aspect_direction_breakdown"]["applying"] == 1


# --------------------------------------------------------------------------
# GUARDRAIL: breakdown does NOT change scoring behavior
# --------------------------------------------------------------------------


def test_breakdown_does_not_affect_primary_archetypes() -> None:
    """Iki farklı chart_aspects input, top_archetypes sıra/score aynı."""
    heavy_applying = [_a("Saturn", "Moon", "applying")] * 5
    heavy_separating = [_a("Saturn", "Moon", "separating")] * 5

    payload_a = build_archetype_profile(**_inputs(chart_aspects=heavy_applying))
    payload_b = build_archetype_profile(**_inputs(chart_aspects=heavy_separating))

    ids_a = [item["id"] for item in payload_a["top_archetypes"]]
    ids_b = [item["id"] for item in payload_b["top_archetypes"]]
    scores_a = [round(item["score"], 6) for item in payload_a["top_archetypes"]]
    scores_b = [round(item["score"], 6) for item in payload_b["top_archetypes"]]

    assert ids_a == ids_b
    assert scores_a == scores_b


def test_breakdown_does_not_affect_confidence() -> None:
    payload_with = build_archetype_profile(**_inputs(
        chart_aspects=[_a("Saturn", "Moon", "applying")],
    ))
    payload_without = build_archetype_profile(**_inputs())
    assert payload_with["confidence"] == payload_without["confidence"]


def test_breakdown_does_not_affect_shadow() -> None:
    payload_with = build_archetype_profile(**_inputs(
        chart_aspects=[_a("Saturn", "Moon", "applying")],
    ))
    payload_without = build_archetype_profile(**_inputs())
    assert payload_with["shadow_archetype"] == payload_without["shadow_archetype"]


def test_breakdown_does_not_affect_scoring_profile_version() -> None:
    payload = build_archetype_profile(**_inputs(
        chart_aspects=[_a("Saturn", "Moon", "applying")],
    ))
    assert payload["scoring_profile_version"] == "v2"


def test_breakdown_does_not_affect_lunar_phase_or_birth_time_mode() -> None:
    """PR 7 ve PR 4a field'ları dokunulmuyor."""
    payload = build_archetype_profile(**_inputs(
        chart_aspects=[_a("Saturn", "Moon", "applying")],
        chart_planets={
            "Sun": {"sign": "Aries", "longitude": 0.0},
            "Moon": {"sign": "Cancer", "longitude": 90.0},
        },
        birth_time_confidence="unknown",
    ))
    assert payload["lunar_phase"] == "first_quarter"
    assert payload["birth_time_mode"] == "unknown"


def test_breakdown_does_not_leak_into_chart_prior() -> None:
    """GUARDRAIL: breakdown sadece final_items/top_archetypes seviyesinde;
    chart_prior components'a sızmaz."""
    payload = build_archetype_profile(**_inputs(
        chart_aspects=[_a("Saturn", "Moon", "applying")],
    ))
    chart_prior = payload.get("chart_prior") or {}
    for item in chart_prior.get("items") or []:
        components = item.get("components") or {}
        assert "aspect_direction_breakdown" not in components
        assert "aspect_direction_breakdown" not in item


# --------------------------------------------------------------------------
# Coexistence with PR 6 dignity and PR 7 lunar_phase
# --------------------------------------------------------------------------


def test_breakdown_dignity_and_lunar_phase_coexist() -> None:
    """Tüm Faz 2 explainability surface'ları aynı payload'da görünür ve
    birbirinden bağımsız."""
    chart_planets = {
        "Sun": {"sign": "Aries", "longitude": 0.0},
        "Moon": {"sign": "Cancer", "longitude": 180.0},    # full moon
        "Saturn": {"sign": "Capricorn", "longitude": 280.0},   # domicile
    }
    chart_aspects = [
        _a("Saturn", "Moon", "applying"),
        _a("Saturn", "Sun", "separating"),
    ]
    payload = build_archetype_profile(**_inputs(
        chart_planets=chart_planets,
        chart_aspects=chart_aspects,
    ))

    # Lunar phase (PR 7)
    assert payload["lunar_phase"] == "full"

    # Dignity (PR 6) on builder
    builder_prior = next(
        item for item in payload["chart_prior"]["items"] if item["id"] == "builder"
    )
    assert builder_prior["components"]["dignity_bonus"] == pytest.approx(0.15, abs=1e-9)

    # Breakdown (PR 8a) on builder
    builder_top = next(item for item in payload["top_archetypes"] if item["id"] == "builder")
    assert builder_top["aspect_direction_breakdown"] == {
        "applying": 1, "separating": 1, "exact": 0, "unknown": 0,
    }
