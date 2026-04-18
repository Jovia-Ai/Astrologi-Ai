"""Unit tests for app.astro.lunar_phase — Faz 2 PR 7.

8 kanonik phase detection doğruluğu + boundary + wrap-around +
fail-safe fallback.
"""
from __future__ import annotations

import pytest

from app.astro.lunar_phase import PHASE_BOUNDARIES, compute_lunar_phase


# --------------------------------------------------------------------------
# 8 phase center elongations
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "elongation,expected",
    [
        (0.0, "new"),
        (45.0, "waxing_crescent"),
        (90.0, "first_quarter"),
        (135.0, "waxing_gibbous"),
        (180.0, "full"),
        (225.0, "waning_gibbous"),
        (270.0, "last_quarter"),
        (315.0, "balsamic"),
    ],
)
def test_phase_center_points(elongation: float, expected: str) -> None:
    """Her phase'in merkezinde (elongation = cardinal angle)."""
    assert compute_lunar_phase(0.0, elongation) == expected


# --------------------------------------------------------------------------
# Boundary tests — inclusive-exclusive [start, end)
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "elongation,expected",
    [
        # new upper boundary: 22.5 exclusive → waxing_crescent
        (22.4, "new"),
        (22.5, "waxing_crescent"),
        # waxing_crescent upper: 67.5
        (67.4, "waxing_crescent"),
        (67.5, "first_quarter"),
        # first_quarter upper: 112.5
        (112.4, "first_quarter"),
        (112.5, "waxing_gibbous"),
        # waxing_gibbous upper: 157.5
        (157.4, "waxing_gibbous"),
        (157.5, "full"),
        # full upper: 202.5
        (202.4, "full"),
        (202.5, "waning_gibbous"),
        # waning_gibbous upper: 247.5
        (247.4, "waning_gibbous"),
        (247.5, "last_quarter"),
        # last_quarter upper: 292.5
        (292.4, "last_quarter"),
        (292.5, "balsamic"),
        # balsamic upper: 337.5 → new
        (337.4, "balsamic"),
        (337.5, "new"),
    ],
)
def test_phase_boundaries_are_inclusive_exclusive(
    elongation: float, expected: str
) -> None:
    assert compute_lunar_phase(0.0, elongation) == expected


# --------------------------------------------------------------------------
# Wrap-around — new phase spans 0°
# --------------------------------------------------------------------------


def test_new_phase_wraps_around_zero() -> None:
    """Sun at 350°, Moon at 10° → elongation 20° (mod 360) → new."""
    assert compute_lunar_phase(350.0, 10.0) == "new"


def test_new_phase_wraps_around_from_above() -> None:
    """Sun at 10°, Moon at 355° → elongation 345° (mod 360) → new."""
    assert compute_lunar_phase(10.0, 355.0) == "new"


def test_elongation_computed_via_mod_360() -> None:
    """Input longitude'ları 360'tan büyük olsa bile mod 360 ile normalize edilir."""
    # Sun 720°, Moon 810° → elongation 90 → first_quarter
    assert compute_lunar_phase(720.0, 810.0) == "first_quarter"


def test_negative_elongation_handled() -> None:
    """Sun ahead of Moon — (Moon-Sun) negative, mod 360 ile pozitife döner.
    Sun 90, Moon 0 → elongation -90 mod 360 = 270 → last_quarter.
    """
    assert compute_lunar_phase(90.0, 0.0) == "last_quarter"


# --------------------------------------------------------------------------
# Fail-safe: missing input
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "sun,moon",
    [
        (None, 90.0),
        (0.0, None),
        (None, None),
    ],
)
def test_missing_longitude_returns_none(sun, moon) -> None:
    assert compute_lunar_phase(sun, moon) is None


# --------------------------------------------------------------------------
# Legacy fail-safe: non-numeric input
# --------------------------------------------------------------------------
# Production caller'lar numeric göndermeli. Bu test'ler runtime robustness'i
# lock'lar ama beklenen call pattern'i değil.


@pytest.mark.parametrize(
    "sun,moon",
    [
        ("bad", 90.0),
        (0.0, "bad"),
        ("", ""),
    ],
)
def test_non_numeric_input_returns_none_fail_safe(sun, moon) -> None:
    """Legacy/robust fail-safe — docstring'de işaretli."""
    assert compute_lunar_phase(sun, moon) is None  # type: ignore[arg-type]


# --------------------------------------------------------------------------
# Table constants — behavior lock
# --------------------------------------------------------------------------


def test_phase_boundaries_table_frozen() -> None:
    """PHASE_BOUNDARIES bağımsız bir kaynak olarak behavior-lock.
    Değişim kasıtlı olmalı ve bu test'i güncellemek gerektirmeli."""
    expected = (
        ("new", 337.5, 22.5),
        ("waxing_crescent", 22.5, 67.5),
        ("first_quarter", 67.5, 112.5),
        ("waxing_gibbous", 112.5, 157.5),
        ("full", 157.5, 202.5),
        ("waning_gibbous", 202.5, 247.5),
        ("last_quarter", 247.5, 292.5),
        ("balsamic", 292.5, 337.5),
    )
    assert PHASE_BOUNDARIES == expected


def test_phase_names_are_eight_canonical() -> None:
    phases = {entry[0] for entry in PHASE_BOUNDARIES}
    assert phases == {
        "new", "waxing_crescent", "first_quarter", "waxing_gibbous",
        "full", "waning_gibbous", "last_quarter", "balsamic",
    }
