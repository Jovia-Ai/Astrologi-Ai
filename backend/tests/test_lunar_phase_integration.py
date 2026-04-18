"""Faz 2 PR 7 integration: lunar_phase top-level metadata wire through
build_archetype_profile. User'ın özellikle istediği 4 phase (new,
first_quarter, full, balsamic) integration coverage'ında doğrulanır.

Guardrail: lunar_phase KESİNLİKLE chart_prior veya per-archetype
components'a sızmaz. Sadece top-level payload metadata.
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


def _chart_with_luminaries(sun_lon: float, moon_lon: float) -> Dict[str, Any]:
    """Minimal chart — sadece Sun ve Moon longitude'u phase detection için."""
    return {
        "Sun": {"sign": "Aries", "longitude": sun_lon},
        "Moon": {"sign": "Cancer", "longitude": moon_lon},
    }


# --------------------------------------------------------------------------
# User-requested 4 phases: new, first_quarter, full, balsamic
# --------------------------------------------------------------------------


def test_integration_new_phase_surfaces_in_payload() -> None:
    """Sun at 0°, Moon at 5° → elongation 5° → new."""
    payload = build_archetype_profile(**_inputs(
        chart_planets=_chart_with_luminaries(sun_lon=0.0, moon_lon=5.0),
    ))
    assert payload["lunar_phase"] == "new"


def test_integration_first_quarter_phase() -> None:
    """Sun at 0°, Moon at 90° → first_quarter."""
    payload = build_archetype_profile(**_inputs(
        chart_planets=_chart_with_luminaries(sun_lon=0.0, moon_lon=90.0),
    ))
    assert payload["lunar_phase"] == "first_quarter"


def test_integration_full_phase() -> None:
    """Sun at 0°, Moon at 180° → full."""
    payload = build_archetype_profile(**_inputs(
        chart_planets=_chart_with_luminaries(sun_lon=0.0, moon_lon=180.0),
    ))
    assert payload["lunar_phase"] == "full"


def test_integration_balsamic_phase() -> None:
    """Sun at 0°, Moon at 320° → elongation 320° → balsamic (292.5-337.5)."""
    payload = build_archetype_profile(**_inputs(
        chart_planets=_chart_with_luminaries(sun_lon=0.0, moon_lon=320.0),
    ))
    assert payload["lunar_phase"] == "balsamic"


# --------------------------------------------------------------------------
# Fail-safe fallback paths
# --------------------------------------------------------------------------


def test_no_chart_planets_lunar_phase_none() -> None:
    """Legacy caller chart_planets geçmezse lunar_phase None."""
    payload = build_archetype_profile(**_inputs())
    assert payload["lunar_phase"] is None


def test_missing_sun_lunar_phase_none() -> None:
    """Moon var ama Sun yoksa None."""
    payload = build_archetype_profile(**_inputs(
        chart_planets={"Moon": {"sign": "Cancer", "longitude": 90.0}},
    ))
    assert payload["lunar_phase"] is None


def test_missing_moon_lunar_phase_none() -> None:
    payload = build_archetype_profile(**_inputs(
        chart_planets={"Sun": {"sign": "Aries", "longitude": 0.0}},
    ))
    assert payload["lunar_phase"] is None


def test_sun_moon_without_longitude_lunar_phase_none() -> None:
    """chart_planets nested ama longitude field'ı yok → None."""
    payload = build_archetype_profile(**_inputs(
        chart_planets={
            "Sun": {"sign": "Aries"},
            "Moon": {"sign": "Cancer"},
        },
    ))
    assert payload["lunar_phase"] is None


def test_string_shape_chart_planets_lunar_phase_none() -> None:
    """PR 6'da `{planet: sign_string}` shape destekleniyor (dignity için).
    Ama longitude olmadığı için lunar_phase None — dignity ile bağımsız çalışma."""
    payload = build_archetype_profile(**_inputs(
        chart_planets={"Sun": "Aries", "Moon": "Cancer"},
    ))
    assert payload["lunar_phase"] is None


# --------------------------------------------------------------------------
# GUARDRAIL: lunar_phase MUST stay top-level only
# --------------------------------------------------------------------------


def test_lunar_phase_does_not_leak_into_chart_prior() -> None:
    """User guardrail #2: lunar_phase chart_prior'a veya per-archetype
    components'a sızmamalı. Sadece top-level metadata."""
    payload = build_archetype_profile(**_inputs(
        chart_planets=_chart_with_luminaries(sun_lon=0.0, moon_lon=180.0),
    ))
    # Top-level contains it
    assert "lunar_phase" in payload
    # chart_prior does NOT contain it
    chart_prior = payload.get("chart_prior") or {}
    assert "lunar_phase" not in chart_prior
    # Per-archetype items don't contain it either
    for item in chart_prior.get("items") or []:
        assert "lunar_phase" not in item
        components = item.get("components") or {}
        assert "lunar_phase" not in components


def test_lunar_phase_does_not_affect_primary_archetypes() -> None:
    """Phase değişimi ranking'e sıfır etki — 2 farklı phase, aynı primary."""
    payload_new = build_archetype_profile(**_inputs(
        chart_planets=_chart_with_luminaries(sun_lon=0.0, moon_lon=5.0),
    ))
    payload_full = build_archetype_profile(**_inputs(
        chart_planets=_chart_with_luminaries(sun_lon=0.0, moon_lon=180.0),
    ))
    ids_new = [item["id"] for item in payload_new["top_archetypes"]]
    ids_full = [item["id"] for item in payload_full["top_archetypes"]]
    assert ids_new == ids_full


def test_lunar_phase_does_not_affect_confidence() -> None:
    """Phase değişimi confidence'a sıfır etki."""
    payload_new = build_archetype_profile(**_inputs(
        chart_planets=_chart_with_luminaries(sun_lon=0.0, moon_lon=5.0),
    ))
    payload_full = build_archetype_profile(**_inputs(
        chart_planets=_chart_with_luminaries(sun_lon=0.0, moon_lon=180.0),
    ))
    assert payload_new["confidence"] == payload_full["confidence"]


def test_lunar_phase_does_not_affect_shadow() -> None:
    """Phase değişimi shadow'a sıfır etki."""
    payload_new = build_archetype_profile(**_inputs(
        chart_planets=_chart_with_luminaries(sun_lon=0.0, moon_lon=5.0),
    ))
    payload_full = build_archetype_profile(**_inputs(
        chart_planets=_chart_with_luminaries(sun_lon=0.0, moon_lon=180.0),
    ))
    assert payload_new["shadow_archetype"] == payload_full["shadow_archetype"]


def test_lunar_phase_does_not_affect_birth_time_mode() -> None:
    """Phase değişimi birth_time_mode'a sıfır etki."""
    payload = build_archetype_profile(**_inputs(
        chart_planets=_chart_with_luminaries(sun_lon=0.0, moon_lon=180.0),
        birth_time_confidence="unknown",
    ))
    assert payload["birth_time_mode"] == "unknown"
    assert payload["lunar_phase"] == "full"


def test_lunar_phase_does_not_bump_scoring_profile_version() -> None:
    """Scoring profile version v2'de kalmalı — PR 7 user-facing ranking
    değişimi getirmiyor."""
    payload = build_archetype_profile(**_inputs(
        chart_planets=_chart_with_luminaries(sun_lon=0.0, moon_lon=180.0),
    ))
    assert payload["scoring_profile_version"] == "v2"


# --------------------------------------------------------------------------
# Coexistence with PR 6 dignity
# --------------------------------------------------------------------------


def test_dignity_and_lunar_phase_work_together() -> None:
    """Dignity (PR 6) ve lunar_phase (PR 7) aynı chart_planets'ten çıkar
    ama birbirinden bağımsız. Ikisi de aynı payload'da doğru surface eder."""
    chart_planets = {
        "Sun": {"sign": "Aries", "longitude": 0.0},
        "Moon": {"sign": "Cancer", "longitude": 180.0},
        "Saturn": {"sign": "Capricorn", "longitude": 280.0},   # domicile
    }
    payload = build_archetype_profile(**_inputs(chart_planets=chart_planets))

    # Lunar phase correct
    assert payload["lunar_phase"] == "full"

    # Dignity (PR 6) still works in chart_prior — builder gets domicile bonus
    builder = next(
        (item for item in payload["chart_prior"]["items"] if item["id"] == "builder"),
        None,
    )
    assert builder is not None
    assert builder["components"]["dignity_bonus"] == pytest.approx(0.15, abs=1e-9)
