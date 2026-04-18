"""Unit tests for app.astro.aspect_direction.

User'ın PR 5 test gereksinimleri:
- retrograde case
- exact case
- applying → separating transition
- missing speed data fallback
- unknown aspect fallback
"""
from __future__ import annotations

import pytest

from app.astro.aspect_direction import (
    ASPECT_ANGLES,
    DIRECTION_TIGHTNESS_BONUS,
    EXACT_ORB_EPSILON,
    SPEED_EPSILON,
    compute_direction,
    direction_multiplier,
)


# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

def test_constants_are_frozen() -> None:
    """Eşik değerlerinin kasıtsız değişmesini engelle (behavior-lock)."""
    assert EXACT_ORB_EPSILON == 0.1
    assert SPEED_EPSILON == 0.01
    assert ASPECT_ANGLES == {
        "conjunction": 0.0,
        "sextile": 60.0,
        "square": 90.0,
        "trine": 120.0,
        "opposition": 180.0,
    }


def test_direction_multiplier_table_is_conservative() -> None:
    """Konservatif başlangıç: applying/exact %10 bonus, separating penaltısız."""
    assert DIRECTION_TIGHTNESS_BONUS == {
        "applying": 1.10,
        "exact": 1.10,
        "separating": 1.00,
    }


# --------------------------------------------------------------------------
# Exact cases
# --------------------------------------------------------------------------

def test_exact_conjunction_at_zero_orb() -> None:
    """İki body aynı longitude'da → conjunction exact."""
    assert compute_direction("conjunction", 15.0, 15.0, 1.0, 0.5) == "exact"


def test_exact_within_epsilon_tolerance() -> None:
    """Orb < 0.1° → exact (epsilon içinde)."""
    assert compute_direction("conjunction", 15.0, 15.05, 1.0, 0.5) == "exact"


def test_exact_square_ninety_degrees() -> None:
    """90° ± epsilon → square exact."""
    assert compute_direction("square", 100.05, 10.0, 1.0, 0.5) == "exact"


def test_exact_opposition_one_eighty() -> None:
    assert compute_direction("opposition", 10.0, 190.0, 1.0, 0.5) == "exact"


def test_beyond_epsilon_not_exact() -> None:
    """Orb = 0.15° > epsilon → exact DEĞİL."""
    result = compute_direction("conjunction", 15.0, 15.15, 1.0, 0.5)
    assert result != "exact"


# --------------------------------------------------------------------------
# Applying / separating geometric rule
# --------------------------------------------------------------------------

def test_applying_conjunction_fast_body_approaching() -> None:
    """A body B'ye yaklaşıyor → applying."""
    # A at 10°, B at 15°. A faster (speed 2 > speed 1) → A catches up → applying
    assert compute_direction("conjunction", 10.0, 15.0, 2.0, 1.0) == "applying"


def test_separating_conjunction_past_exact() -> None:
    """A body B'den ayrılıyor → separating."""
    # A at 20°, B at 15°. A faster → A pulling away → separating
    assert compute_direction("conjunction", 20.0, 15.0, 2.0, 1.0) == "separating"


def test_applying_square() -> None:
    """Square: A'nın B'ye olan 90° açısına yaklaşma durumu."""
    # A at 105° (15° past square), B at 10°, A slower → orb shrinks → applying
    assert compute_direction("square", 105.0, 10.0, 0.5, 1.0) == "applying"


def test_separating_trine() -> None:
    """Trine 120°: orb genişliyorsa separating."""
    # A at 132° (12° past trine from B=10°), A faster → orb grows → separating
    assert compute_direction("trine", 132.0, 10.0, 2.0, 1.0) == "separating"


# --------------------------------------------------------------------------
# Retrograde cases (negatif speed)
# --------------------------------------------------------------------------

def test_retrograde_body_applying_from_behind() -> None:
    """A retrograde, B direct. A at 20°, B at 15°. A negative speed.
    A retrograde movement takes it toward B → applying conjunction.
    """
    # A speed -0.5 (retrograde), B speed +1.0
    # rel_speed = -0.5 - 1.0 = -1.5 (negative)
    # sep = 20 - 15 = 5, target 0 (conj). current orb = 5
    # future_sep = 5 + (-1.5) = 3.5, future orb = 3.5 < 5 → applying
    assert compute_direction("conjunction", 20.0, 15.0, -0.5, 1.0) == "applying"


def test_retrograde_body_separating_when_moving_away() -> None:
    """Retrograde body aspect'ten geriye doğru uzaklaşırsa separating."""
    # A at 10°, B at 15°, A retrograde (-0.5), B direct (+1.0)
    # rel_speed = -1.5. sep = -5, orb = 5.
    # future_sep = -5 + (-1.5) = -6.5, future orb = 6.5 > 5 → separating
    assert compute_direction("conjunction", 10.0, 15.0, -0.5, 1.0) == "separating"


def test_both_retrograde_uses_standard_rule() -> None:
    """İki body de retrograde. Geometric rule aynı şekilde işler."""
    # A at 15°, B at 10°. A speed -2, B speed -1. rel = -1.
    # sep = 5, orb = 5. future_sep = 4, future_orb = 4 < 5 → applying
    assert compute_direction("conjunction", 15.0, 10.0, -2.0, -1.0) == "applying"


# --------------------------------------------------------------------------
# Transition: same pair at different moments
# --------------------------------------------------------------------------

def test_applying_then_separating_transition() -> None:
    """Aynı iki body çifti — sep değişimini zaman boyunca test et.

    Scenario: A faster catches up to B at exact, then moves past.
    Before exact: A=25, B=30, A faster(+1)/B slower(+0.5) → approaching conj → applying
    At exact: A=30.05, B=30, A fast/B slow → at exact point, tightness peaks
    After exact: A=35, B=30, same speeds → orb growing → separating
    """
    before = compute_direction("conjunction", 25.0, 30.0, 1.0, 0.5)
    at_exact = compute_direction("conjunction", 30.05, 30.0, 1.0, 0.5)
    after = compute_direction("conjunction", 35.0, 30.0, 1.0, 0.5)

    assert before == "applying"
    assert at_exact == "exact"
    assert after == "separating"


# --------------------------------------------------------------------------
# Indeterminate: None fallback paths (zero-diff guarantee)
# --------------------------------------------------------------------------

def test_missing_a_speed_returns_none() -> None:
    assert compute_direction("conjunction", 10.0, 15.0, None, 1.0) is None


def test_missing_b_speed_returns_none() -> None:
    assert compute_direction("conjunction", 10.0, 15.0, 1.0, None) is None


def test_missing_both_speeds_returns_none() -> None:
    assert compute_direction("conjunction", 10.0, 15.0, None, None) is None


def test_missing_longitude_returns_none() -> None:
    assert compute_direction("conjunction", None, 15.0, 1.0, 0.5) is None
    assert compute_direction("conjunction", 10.0, None, 1.0, 0.5) is None


def test_unknown_aspect_returns_none() -> None:
    assert compute_direction("quincunx", 10.0, 15.0, 1.0, 0.5) is None
    assert compute_direction("", 10.0, 15.0, 1.0, 0.5) is None


def test_stationary_below_speed_epsilon_returns_none() -> None:
    """Kritik user revizyonu: low relative speed → None, NOT exact.

    Orb 5° (geniş) ama iki body eş hızla ilerliyorsa yön belirsiz.
    Geniş orb yanlışlıkla 'exact' etiketlenmemeli.
    """
    # sep = 5, well beyond EXACT_ORB_EPSILON. Both speeds nearly equal.
    result = compute_direction("conjunction", 15.0, 10.0, 1.005, 1.000)
    assert result is None, (
        f"Low rel speed + wide orb beklenen None, alındı {result!r}. "
        f"Geniş orb (5°) 'exact' etiketlenmemeli."
    )


def test_stationary_at_exact_is_still_exact() -> None:
    """Stasyoner ama orb exact ise 'exact' geri döner (sırayla: exact önce,
    sonra speed check)."""
    # Orb 0.05° < epsilon, speeds eşit. "exact" döner çünkü speed check'inden
    # önce exact kontrolü yapılır.
    result = compute_direction("conjunction", 15.0, 15.05, 1.0, 1.0)
    assert result == "exact"


def test_non_numeric_speed_returns_none() -> None:
    assert compute_direction("conjunction", 10.0, 15.0, "bad", 1.0) is None  # type: ignore[arg-type]


# --------------------------------------------------------------------------
# Multiplier helper
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "direction,expected",
    [
        ("applying", 1.10),
        ("exact", 1.10),
        ("separating", 1.00),
        (None, 1.00),
        ("unknown_label", 1.00),
        ("", 1.00),
    ],
)
def test_direction_multiplier_map(direction, expected: float) -> None:
    assert direction_multiplier(direction) == expected
