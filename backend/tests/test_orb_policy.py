"""Unit tests for backend/app/astro/orb_policy.py.

Natal ve synastry default davranışları hem parametrize boundary test'iyle
hem de semantik ayrımı vurgulayan dedicated test'lerle doğrulanır.
"""
from __future__ import annotations

import pytest

from app.astro.orb_policy import (
    CURVE_TYPE,
    FALLBACK_MAX_ORB,
    MAX_ORB_BY_ASPECT,
    max_orb_for,
    tightness,
)


def test_max_orb_table_values() -> None:
    assert MAX_ORB_BY_ASPECT == {
        "conjunction": 8.0,
        "opposition": 8.0,
        "square": 7.0,
        "trine": 7.0,
        "sextile": 5.0,
    }
    assert FALLBACK_MAX_ORB == 6.0
    assert CURVE_TYPE == "linear"


def test_max_orb_for_case_insensitive() -> None:
    assert max_orb_for("Conjunction") == 8.0
    assert max_orb_for("SQUARE") == 7.0


def test_max_orb_for_unknown_uses_fallback() -> None:
    assert max_orb_for("semisextile") == FALLBACK_MAX_ORB
    assert max_orb_for("quincunx") == FALLBACK_MAX_ORB


# --------------------------------------------------------------------------
# Default (natal) mode: zero_orb_as_missing=False
# --------------------------------------------------------------------------

_NATAL_CASES = [
    ("conjunction", 0.0, 1.0),
    ("conjunction", 4.0, 0.5),
    ("conjunction", 7.99, pytest.approx(1.0 - 7.99 / 8.0, abs=1e-6)),
    ("conjunction", 8.0, 0.0),
    ("conjunction", 10.0, 0.0),
    ("opposition", 0.0, 1.0),
    ("opposition", 8.0, 0.0),
    ("square", 0.0, 1.0),
    ("square", 3.5, 0.5),
    ("square", 7.0, 0.0),
    ("trine", 0.0, 1.0),
    ("trine", 7.0, 0.0),
    ("sextile", 0.0, 1.0),
    ("sextile", 2.5, 0.5),
    ("sextile", 5.0, 0.0),
    ("quincunx", 3.0, 0.5),   # fallback 6.0
    ("quincunx", 6.0, 0.0),
]


@pytest.mark.parametrize("aspect,orb,expected", _NATAL_CASES)
def test_tightness_natal_default_mode(aspect: str, orb: float, expected: float) -> None:
    assert tightness(aspect, orb) == expected


# --------------------------------------------------------------------------
# Synastry mode: zero_orb_as_missing=True
# --------------------------------------------------------------------------

_SYNASTRY_CASES = [
    ("conjunction", 0.0, 0.0),        # sentinel — natal'la zıt
    ("conjunction", -1.0, 0.0),
    ("conjunction", 4.0, 0.5),
    ("conjunction", 8.0, 0.0),
    ("square", 0.0, 0.0),
    ("square", 3.5, 0.5),
    ("trine", 0.0, 0.0),
    ("sextile", 0.0, 0.0),
    ("quincunx", 0.0, 0.0),           # fallback path da sentinel'a uyar
    ("quincunx", 3.0, 0.5),
]


@pytest.mark.parametrize("aspect,orb,expected", _SYNASTRY_CASES)
def test_tightness_synastry_mode(aspect: str, orb: float, expected: float) -> None:
    assert tightness(aspect, orb, zero_orb_as_missing=True) == expected


def test_zero_orb_flag_creates_semantic_divergence() -> None:
    """Bu test natal vs synastry'nin en kritik ayrımını vurgular."""
    assert tightness("conjunction", 0.0) == 1.0                          # natal
    assert tightness("conjunction", 0.0, zero_orb_as_missing=True) == 0.0  # synastry


def test_non_numeric_orb_returns_zero_in_both_modes() -> None:
    assert tightness("conjunction", "nope") == 0.0  # type: ignore[arg-type]
    assert tightness("conjunction", None) == 0.0   # type: ignore[arg-type]
    assert tightness("conjunction", "bad", zero_orb_as_missing=True) == 0.0  # type: ignore[arg-type]


def test_natal_mode_allows_negative_orb_to_exceed_one() -> None:
    """Negatif orb (zero_orb_as_missing=False): matematiksel olarak 1'i geçebilir,
    ama clamp ile 1.0'da durur. Pozitif tightness invariant'ı korunur."""
    value = tightness("conjunction", -2.0)
    assert value == 1.0
