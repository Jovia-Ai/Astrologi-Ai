"""Faz 2 PR 6 integration: dignity bonus wire through build_chart_prior /
build_archetype_profile. Saturn domicile vs detriment hero scenarios,
zero-diff fallback, sect-compound önleme guard.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping

import pytest

from app.astro.dignity import archetype_dignity_bonus, dignity_weight
from app.natal.archetype_profile import (
    build_archetype_profile,
    build_chart_prior,
)


# --------------------------------------------------------------------------
# Shared builders (mirror test_archetype_profile.py shape)
# --------------------------------------------------------------------------


def _primitive_scores() -> Dict[str, Any]:
    return {
        "primitive_scores": [
            {"primitive_id": "self_definition", "score": 0.82},
            {"primitive_id": "inner_structure", "score": 0.80},
            {"primitive_id": "methodical_drive", "score": 0.74},
            {"primitive_id": "public_refinement", "score": 0.68},
            {"primitive_id": "mental_structuring", "score": 0.78},
            {"primitive_id": "systems_thinking", "score": 0.70},
            {"primitive_id": "intimacy_depth", "score": 0.65},
            {"primitive_id": "emotional_threshold", "score": 0.61},
            {"primitive_id": "recharge_through_home", "score": 0.46},
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
        contradiction_signatures={"top_signatures": [{"id": "structure_vs_originality", "score": 0.7}]},
        natal_feature_graph={"public_private_split": {"public_score": 0.6, "private_score": 0.5}},
        test_scores={"builder": 0.88, "visionary": 0.55, "depthkeeper": 0.50},
        question_family_scores={"structure_preference": 0.9, "mental_precision": 0.82},
        birth_time_confidence="exact",
        answer_consistency=0.83,
    )
    defaults.update(overrides)
    return defaults


def _chart(saturn_sign: str, moon_sign: str = "Cancer", **extra) -> Dict[str, str]:
    """Minimal chart for dignity tests."""
    base = {
        "Saturn": saturn_sign,
        "Moon": moon_sign,
        "Mercury": "Gemini",   # domicile
        "Venus": "Libra",       # domicile
        "Mars": "Aries",        # domicile
        "Jupiter": "Sagittarius",  # domicile
        "Sun": "Leo",           # domicile
    }
    base.update(extra)
    return base


# --------------------------------------------------------------------------
# Hero: Saturn domicile vs detriment → builder score shift
# --------------------------------------------------------------------------


def test_saturn_domicile_boosts_builder_score() -> None:
    """Saturn in Capricorn (domicile) vs Saturn in Cancer (detriment) →
    builder chart_score farkı ≥ 0.20 (domicile bonus - detriment penalty = 0.25)."""
    domicile_prior = build_chart_prior(
        primitive_scores=_primitive_scores(),
        master_selector=_master_selector(),
        contradiction_signatures={"top_signatures": [{"id": "structure_vs_originality", "score": 0.7}]},
        natal_feature_graph={"public_private_split": {"public_score": 0.6, "private_score": 0.5}},
        chart_planets=_chart(saturn_sign="Capricorn"),
    )
    detriment_prior = build_chart_prior(
        primitive_scores=_primitive_scores(),
        master_selector=_master_selector(),
        contradiction_signatures={"top_signatures": [{"id": "structure_vs_originality", "score": 0.7}]},
        natal_feature_graph={"public_private_split": {"public_score": 0.6, "private_score": 0.5}},
        chart_planets=_chart(saturn_sign="Cancer", moon_sign="Scorpio"),  # Cancer Saturn = detriment
    )

    dom_builder = domicile_prior["by_id"]["builder"]
    det_builder = detriment_prior["by_id"]["builder"]

    assert dom_builder["components"]["dignity_bonus"] == pytest.approx(0.15, abs=1e-9)
    assert det_builder["components"]["dignity_bonus"] == pytest.approx(-0.10, abs=1e-9)
    assert dom_builder["score"] > det_builder["score"]


def test_moon_fall_penalizes_depthkeeper() -> None:
    """Depthkeeper → (Pluto, Mars). Moon fall (Scorpio) shouldn't affect depthkeeper
    since Moon not in its signature. Kontrol testi — signature-specific etki."""
    moon_fall_prior = build_chart_prior(
        primitive_scores=_primitive_scores(),
        master_selector=_master_selector(),
        contradiction_signatures={"top_signatures": []},
        natal_feature_graph={"public_private_split": {"public_score": 0.5, "private_score": 0.5}},
        chart_planets={"Moon": "Scorpio", "Mars": "Aries", "Pluto": "Scorpio"},
    )
    depthkeeper = moon_fall_prior["by_id"]["depthkeeper"]
    # Pluto domicile (+0.15) + Mars domicile (+0.15) = +0.30, Moon fall alakasız
    assert depthkeeper["components"]["dignity_bonus"] == pytest.approx(0.30, abs=1e-9)


def test_dignity_components_surface_in_payload() -> None:
    """`components.dignity_bonus` her arketipin audit/debug payload'ında görünür."""
    prior = build_chart_prior(
        primitive_scores=_primitive_scores(),
        master_selector=_master_selector(),
        contradiction_signatures={"top_signatures": []},
        natal_feature_graph=None,
        chart_planets=_chart(saturn_sign="Capricorn"),
    )
    for item in prior["items"]:
        assert "dignity_bonus" in item["components"]


# --------------------------------------------------------------------------
# Zero-diff fallback — no chart_planets
# --------------------------------------------------------------------------


def test_legacy_call_without_chart_planets_produces_zero_dignity() -> None:
    """Eski call site chart_planets geçmezse tüm archetype dignity_bonus=0."""
    prior = build_chart_prior(
        primitive_scores=_primitive_scores(),
        master_selector=_master_selector(),
        contradiction_signatures={"top_signatures": []},
        natal_feature_graph=None,
    )
    for item in prior["items"]:
        assert item["components"]["dignity_bonus"] == 0.0


def test_empty_chart_planets_produces_zero_dignity() -> None:
    prior = build_chart_prior(
        primitive_scores=_primitive_scores(),
        master_selector=_master_selector(),
        contradiction_signatures={"top_signatures": []},
        natal_feature_graph=None,
        chart_planets={},
    )
    for item in prior["items"]:
        assert item["components"]["dignity_bonus"] == 0.0


def test_chart_planets_nested_shape_handled() -> None:
    """chart_planets `{planet: {sign: "...", ...}}` şeklinde de kabul edilir
    (dispositor_engine çıktısı format'ı)."""
    prior = build_chart_prior(
        primitive_scores=_primitive_scores(),
        master_selector=_master_selector(),
        contradiction_signatures={"top_signatures": []},
        natal_feature_graph=None,
        chart_planets={
            "Saturn": {"sign": "Capricorn", "house": 10, "longitude": 275.0},
        },
    )
    assert prior["by_id"]["builder"]["components"]["dignity_bonus"] == pytest.approx(0.15, abs=1e-9)


# --------------------------------------------------------------------------
# Additive guard — dignity must sum, not multiply
# --------------------------------------------------------------------------


def test_dignity_bonus_is_strictly_additive() -> None:
    """Dignity bonus score'a TOPLANIR, asla çarpılmaz.

    Builder score formula:
      total = clamp01(base + slot_bonus + contradiction_bonus + split_bonus + dignity_bonus)

    PR 7 sect geldiğinde aynı layer'da ayrı term olarak eklenecek. Bu test
    compound/multiplicative davranışı tripwire olarak engeller.
    """
    # Saturn in Capricorn (+0.15) + base components
    prior = build_chart_prior(
        primitive_scores=_primitive_scores(),
        master_selector=_master_selector(),
        contradiction_signatures={"top_signatures": []},
        natal_feature_graph=None,
        chart_planets=_chart(saturn_sign="Capricorn"),
    )
    builder = prior["by_id"]["builder"]
    components = builder["components"]

    # Score should equal sum of components (clamped to 1.0)
    expected = min(1.0,
        components["base"]
        + components["slot_bonus"]
        + components["contradiction_bonus"]
        + components["public_private_bonus"]
        + components["dignity_bonus"]
    )
    # Round to 4 decimals to match build_chart_prior's rounding
    assert builder["score"] == pytest.approx(round(expected, 4), abs=1e-3)


# --------------------------------------------------------------------------
# End-to-end: build_archetype_profile forwards chart_planets
# --------------------------------------------------------------------------


def test_build_archetype_profile_forwards_chart_planets() -> None:
    """build_archetype_profile yeni chart_planets param'ını chart_prior'a iletmeli."""
    with_dignity = build_archetype_profile(
        **_inputs(chart_planets=_chart(saturn_sign="Capricorn"))
    )
    without_dignity = build_archetype_profile(**_inputs())

    builder_with = next(
        (item for item in with_dignity["chart_prior"]["items"] if item["id"] == "builder"),
        None,
    )
    builder_without = next(
        (item for item in without_dignity["chart_prior"]["items"] if item["id"] == "builder"),
        None,
    )
    assert builder_with is not None
    assert builder_without is not None
    assert builder_with["components"]["dignity_bonus"] == pytest.approx(0.15, abs=1e-9)
    assert builder_without["components"]["dignity_bonus"] == 0.0


def test_dignity_does_not_affect_scoring_profile_version() -> None:
    """PR 6 scoring_profile_version'ı re-bump etmiyor — v2 Phase 2 boyunca accumulative."""
    with_dignity = build_archetype_profile(
        **_inputs(chart_planets=_chart(saturn_sign="Capricorn"))
    )
    assert with_dignity["scoring_profile_version"] == "v2"


def test_dignity_does_not_affect_birth_time_mode() -> None:
    """birth_time_mode dignity'den bağımsız — user guardrail."""
    payload = build_archetype_profile(
        **_inputs(
            birth_time_confidence="unknown",
            chart_planets=_chart(saturn_sign="Capricorn"),
        )
    )
    assert payload["birth_time_mode"] == "unknown"


def test_dignity_does_not_affect_confidence() -> None:
    """confidence formülü dignity'e duyarlı değil."""
    with_dignity = build_archetype_profile(
        **_inputs(chart_planets=_chart(saturn_sign="Capricorn"))
    )
    without_dignity = build_archetype_profile(**_inputs())
    assert with_dignity["confidence"] == without_dignity["confidence"]
