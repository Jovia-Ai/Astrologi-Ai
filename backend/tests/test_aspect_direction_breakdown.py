"""Faz 2 PR 8a unit tests: aspect_direction_breakdown helper.

Signature-based filtering, direction count aggregation, fail-safe fallback.
Explainability surface — scoring'e sıfır etki.
"""
from __future__ import annotations

from typing import Any, Mapping

import pytest

from app.astro.aspect_direction import aspect_direction_breakdown


def _a(p1: str, p2: str, direction: str | None, aspect: str = "conjunction", orb: float = 2.0) -> dict[str, Any]:
    return {"planet1": p1, "planet2": p2, "aspect": aspect, "orb": orb, "direction": direction}


# --------------------------------------------------------------------------
# Fail-safe fallback → all-zero
# --------------------------------------------------------------------------


def test_none_aspects_returns_zero_breakdown() -> None:
    result = aspect_direction_breakdown("builder", None)
    assert result == {"applying": 0, "separating": 0, "exact": 0, "unknown": 0}


def test_empty_aspects_returns_zero_breakdown() -> None:
    assert aspect_direction_breakdown("builder", []) == {
        "applying": 0, "separating": 0, "exact": 0, "unknown": 0,
    }


def test_missing_archetype_id_returns_zero_breakdown() -> None:
    aspects = [_a("Saturn", "Moon", "applying")]
    assert aspect_direction_breakdown(None, aspects) == {
        "applying": 0, "separating": 0, "exact": 0, "unknown": 0,
    }
    assert aspect_direction_breakdown("", aspects) == {
        "applying": 0, "separating": 0, "exact": 0, "unknown": 0,
    }


def test_unknown_archetype_returns_zero_breakdown() -> None:
    """Signature tablosunda olmayan arketip → all-zero, graceful fallback."""
    aspects = [_a("Saturn", "Moon", "applying")]
    assert aspect_direction_breakdown("mystery_archetype", aspects) == {
        "applying": 0, "separating": 0, "exact": 0, "unknown": 0,
    }


# --------------------------------------------------------------------------
# Signature-based filtering (builder → Saturn)
# --------------------------------------------------------------------------


def test_builder_counts_only_saturn_aspects() -> None:
    """Builder signature = Saturn. Sadece Saturn'u içeren aspect'ler sayılır."""
    aspects = [
        _a("Saturn", "Moon", "applying"),         # Saturn var → sayılır
        _a("Venus", "Mars", "applying"),          # Saturn yok → sayılmaz
        _a("Sun", "Saturn", "separating"),        # Saturn var → sayılır
        _a("Mercury", "Jupiter", "exact"),        # Saturn yok → sayılmaz
    ]
    result = aspect_direction_breakdown("builder", aspects)
    assert result == {"applying": 1, "separating": 1, "exact": 0, "unknown": 0}


def test_visionary_counts_only_jupiter_aspects() -> None:
    aspects = [
        _a("Jupiter", "Sun", "applying"),
        _a("Saturn", "Moon", "applying"),
        _a("Venus", "Jupiter", "exact"),
    ]
    result = aspect_direction_breakdown("visionary", aspects)
    assert result == {"applying": 1, "separating": 0, "exact": 1, "unknown": 0}


def test_guardian_counts_saturn_and_moon_aspects() -> None:
    """Guardian signature = (Saturn, Moon) — iki planet'ten biri yeterli."""
    aspects = [
        _a("Saturn", "Mercury", "applying"),    # Saturn → sayılır
        _a("Moon", "Venus", "separating"),       # Moon → sayılır
        _a("Mars", "Pluto", "applying"),         # ikisi de yok → sayılmaz
        _a("Saturn", "Moon", "exact"),           # ikisi de var → 1 sayılır
    ]
    result = aspect_direction_breakdown("guardian", aspects)
    assert result == {"applying": 1, "separating": 1, "exact": 1, "unknown": 0}


# --------------------------------------------------------------------------
# Direction label handling
# --------------------------------------------------------------------------


def test_none_direction_counted_as_unknown() -> None:
    """direction=None (eksik speed/stasyoner) → `unknown` bucket."""
    aspects = [_a("Saturn", "Moon", None)]
    result = aspect_direction_breakdown("builder", aspects)
    assert result == {"applying": 0, "separating": 0, "exact": 0, "unknown": 1}


def test_unrecognized_direction_label_counted_as_unknown() -> None:
    """Gelecek refactor'da yeni label eklenirse old UI crash etmez."""
    aspects = [_a("Saturn", "Moon", "approaching")]    # not in canonical set
    result = aspect_direction_breakdown("builder", aspects)
    assert result == {"applying": 0, "separating": 0, "exact": 0, "unknown": 1}


def test_mixed_directions_sum_correctly() -> None:
    aspects = [
        _a("Saturn", "Moon", "applying"),
        _a("Saturn", "Venus", "applying"),
        _a("Saturn", "Sun", "separating"),
        _a("Saturn", "Mars", "exact"),
        _a("Saturn", "Mercury", None),
        _a("Saturn", "Jupiter", "approaching"),   # unknown label
    ]
    result = aspect_direction_breakdown("builder", aspects)
    assert result == {"applying": 2, "separating": 1, "exact": 1, "unknown": 2}


# --------------------------------------------------------------------------
# Case insensitivity + malformed aspect dict
# --------------------------------------------------------------------------


def test_case_insensitive_planet_matching() -> None:
    """ARCHETYPE_SIGNATURE_PLANETS lowercase, aspect dict'te planet case
    karışık gelebilir — case-insensitive match."""
    aspects = [
        _a("saturn", "moon", "applying"),
        _a("SATURN", "VENUS", "separating"),
        _a("Saturn", "Mars", "exact"),
    ]
    result = aspect_direction_breakdown("builder", aspects)
    assert result == {"applying": 1, "separating": 1, "exact": 1, "unknown": 0}


def test_case_insensitive_archetype_id() -> None:
    aspects = [_a("Saturn", "Moon", "applying")]
    assert aspect_direction_breakdown("BUILDER", aspects) == {
        "applying": 1, "separating": 0, "exact": 0, "unknown": 0,
    }
    assert aspect_direction_breakdown(" Builder ", aspects) == {
        "applying": 1, "separating": 0, "exact": 0, "unknown": 0,
    }


def test_malformed_aspect_entries_skipped() -> None:
    """Non-Mapping aspect entries gracefully skipped."""
    aspects = [
        _a("Saturn", "Moon", "applying"),
        "not a dict",                            # type: ignore[list-item]
        None,                                     # type: ignore[list-item]
        {"planet1": "Saturn"},                    # missing planet2 → still matches Saturn
        _a("Saturn", "Mars", "exact"),
    ]
    result = aspect_direction_breakdown("builder", aspects)   # type: ignore[arg-type]
    # 3 valid Saturn aspects (malformed dict without planet2 → planet1 still Saturn, direction None → unknown)
    assert result == {"applying": 1, "separating": 0, "exact": 1, "unknown": 1}


def test_missing_planet_field_skipped() -> None:
    """Her iki planet field'ı eksikse sayılmaz."""
    aspects = [
        {"aspect": "conjunction", "orb": 0.0, "direction": "exact"},
    ]
    result = aspect_direction_breakdown("builder", aspects)
    assert result == {"applying": 0, "separating": 0, "exact": 0, "unknown": 0}


# --------------------------------------------------------------------------
# Custom signature_planets override (testability)
# --------------------------------------------------------------------------


def test_custom_signature_planets_override() -> None:
    """Dışarıdan `signature_planets` geçirerek davranışı test et — unit
    test'lerde izolasyon için yararlı."""
    aspects = [
        _a("Chiron", "Moon", "applying"),
        _a("Saturn", "Mars", "separating"),
    ]
    custom_sig: Mapping[str, list] = {"healer": ("chiron",)}
    result = aspect_direction_breakdown(
        "healer", aspects, signature_planets=custom_sig
    )
    assert result == {"applying": 1, "separating": 0, "exact": 0, "unknown": 0}


def test_default_uses_dignity_signature_planets() -> None:
    """Default signature_planets=None → dignity.ARCHETYPE_SIGNATURE_PLANETS."""
    from app.astro.dignity import ARCHETYPE_SIGNATURE_PLANETS
    # Builder'ın dignity tablosundaki signature — Saturn
    assert "saturn" in {p.lower() for p in ARCHETYPE_SIGNATURE_PLANETS["builder"]}

    aspects = [_a("Saturn", "Moon", "applying")]
    assert aspect_direction_breakdown("builder", aspects) == {
        "applying": 1, "separating": 0, "exact": 0, "unknown": 0,
    }
