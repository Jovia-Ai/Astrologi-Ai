"""Faz 2 PR 5: aspect_direction integration — dispositor_engine + natal
promise_vector_engine._aspect_tightness zincirinin birleşik davranışı.

Supabase env gerektirmeden, synthetic chart dict üzerinden tüm pipeline'ı
koşar. Hero fixture olarak T-square konfigürasyonu (audit fix05_t_square_tense
muadili) kullanılır: 3 sıkı aspect, 2 applying 1 separating.
"""
from __future__ import annotations

from typing import Any, Dict

import pytest

from app.natal.dispositor_engine import extract_aspects, extract_planet_positions
from app.natal.promise_vector_engine import _aspect_tightness


def _chart_tsquare_applying_heavy() -> Dict[str, Any]:
    """Hero: 3 body mix, applying + separating + exact.

    Setup:
      Sun       0° Aries     (speed  1.0)
      Mercury  58° Gemini    (speed  1.5) — sextile Sun, 2° before exact, faster → applying
      Venus    92° Cancer    (speed  1.2) — square Sun, 2° past exact, faster  → separating
      Mars    120° Leo       (speed  0.6) — trine Sun, exact (orb 0)            → exact
    """
    return {
        "planets": [
            {"planet": "Sun", "longitude": 0.0, "speed": 1.0, "retrograde": False,
             "sign": "Aries", "house": 1},
            {"planet": "Mercury", "longitude": 58.0, "speed": 1.5, "retrograde": False,
             "sign": "Gemini", "house": 3},
            {"planet": "Venus", "longitude": 92.0, "speed": 1.2, "retrograde": False,
             "sign": "Cancer", "house": 4},
            {"planet": "Mars", "longitude": 120.0, "speed": 0.6, "retrograde": False,
             "sign": "Leo", "house": 5},
        ],
        "aspects": [
            # Mercury sx Sun: sep=58, target=60, signed_dev=-2, rel=+0.5,
            # derivative=sign(-2)*0.5=-1.0 → applying
            {"planet1": "Mercury", "planet2": "Sun", "aspect": "sextile", "orb": 2.0},
            # Venus sq Sun: sep=92, target=90, signed_dev=+2, rel=+0.2,
            # derivative=sign(+2)*0.2=+0.4 → separating
            {"planet1": "Venus", "planet2": "Sun", "aspect": "square", "orb": 2.0},
            # Mars tr Sun: sep=120, target=120, signed_dev=0 → exact
            {"planet1": "Mars", "planet2": "Sun", "aspect": "trine", "orb": 0.0},
        ],
    }


def _chart_missing_speed() -> Dict[str, Any]:
    """Legacy chart formatı — speed field yok (fail-safe path)."""
    return {
        "planets": [
            {"planet": "Mars", "longitude": 15.0, "sign": "Aries", "house": 1},
            {"planet": "Moon", "longitude": 107.0, "sign": "Cancer", "house": 4},
        ],
        "aspects": [
            {"planet1": "Moon", "planet2": "Mars", "aspect": "square", "orb": 2.0},
        ],
    }


# --------------------------------------------------------------------------
# Speed pass-through
# --------------------------------------------------------------------------


def test_extract_planet_positions_preserves_speed() -> None:
    """Speed field dispositor_engine'den geçerken kaybolmamalı."""
    chart = _chart_tsquare_applying_heavy()
    positions = extract_planet_positions(chart)
    assert positions["Mercury"]["speed"] == 1.5
    assert positions["Mars"]["speed"] == 0.6
    assert positions["Sun"]["speed"] == 1.0


def test_extract_planet_positions_legacy_chart_speed_none() -> None:
    """Speed yoksa None pass-through, hata değil."""
    chart = _chart_missing_speed()
    positions = extract_planet_positions(chart)
    assert positions["Mars"]["speed"] is None
    assert positions["Moon"]["speed"] is None


# --------------------------------------------------------------------------
# Direction computation on real aspects
# --------------------------------------------------------------------------


def test_extract_aspects_computes_direction_from_chart_pipeline() -> None:
    """Hero chart'ta 3 aspect, beklenen direction'lar doğru hesaplanmalı."""
    chart = _chart_tsquare_applying_heavy()
    aspects = extract_aspects(chart)

    by_pair = {(a["planet1"], a["planet2"], a["aspect"]): a for a in aspects}

    assert by_pair[("Mercury", "Sun", "sextile")]["direction"] == "applying"
    assert by_pair[("Venus", "Sun", "square")]["direction"] == "separating"
    assert by_pair[("Mars", "Sun", "trine")]["direction"] == "exact"


def test_extract_aspects_missing_speed_yields_none_direction() -> None:
    """Fail-safe: speed yoksa direction=None (wrapper multiplier=1.0)."""
    chart = _chart_missing_speed()
    aspects = extract_aspects(chart)
    assert len(aspects) == 1
    assert aspects[0]["direction"] is None


def test_extract_aspects_preserves_upstream_direction_if_present() -> None:
    """Upstream pipeline direction'ı zaten set etmişse override etme."""
    chart = {
        "planets": [
            {"planet": "Mars", "longitude": 15.0, "speed": 0.6, "sign": "Aries"},
            {"planet": "Moon", "longitude": 107.0, "speed": 12.5, "sign": "Cancer"},
        ],
        "aspects": [
            {
                "planet1": "Moon",
                "planet2": "Mars",
                "aspect": "square",
                "orb": 2.0,
                # Upstream preset override
                "direction": "separating",
            },
        ],
    }
    aspects = extract_aspects(chart)
    assert aspects[0]["direction"] == "separating"


# --------------------------------------------------------------------------
# Ranking impact — _aspect_tightness direction multiplier
# --------------------------------------------------------------------------


def test_aspect_tightness_applies_applying_bonus() -> None:
    """Aynı orb, applying direction → tightness %10 yüksek."""
    applying = _aspect_tightness({"aspect": "square", "orb": 2.0, "direction": "applying"})
    separating = _aspect_tightness({"aspect": "square", "orb": 2.0, "direction": "separating"})
    # 7° max_orb, orb=2 → base tightness = 5/7 ≈ 0.714
    # Applying: 0.714 * 1.10 ≈ 0.786
    # Separating: 0.714 * 1.00 = 0.714
    assert applying > separating
    assert applying == pytest.approx(separating * 1.10, abs=1e-4)


def test_aspect_tightness_exact_gets_applying_level_bonus() -> None:
    """Exact direction da %10 bonus (applying ile aynı)."""
    exact = _aspect_tightness({"aspect": "square", "orb": 2.0, "direction": "exact"})
    separating = _aspect_tightness({"aspect": "square", "orb": 2.0, "direction": "separating"})
    assert exact > separating


def test_aspect_tightness_none_direction_zero_diff_fallback() -> None:
    """direction=None → multiplier=1.0 → base tightness aynen döner.

    Bu fail-safe guarantee: eski chart data (speed yok) davranışı kırmaz.
    """
    no_dir = _aspect_tightness({"aspect": "square", "orb": 2.0, "direction": None})
    no_key = _aspect_tightness({"aspect": "square", "orb": 2.0})   # direction key yok
    # Her ikisi de base tightness döner
    assert no_dir == no_key


def test_aspect_tightness_clamps_at_one() -> None:
    """Çok tight aspect + applying bonus → 1.0'ı geçmemeli."""
    # orb=0 → base 1.0, * 1.10 = 1.10 → clamp 1.0
    tight_applying = _aspect_tightness({"aspect": "conjunction", "orb": 0.0, "direction": "applying"})
    assert tight_applying == 1.0


# --------------------------------------------------------------------------
# Hero integration: T-square chart applying/separating breakdown
# --------------------------------------------------------------------------


def test_hero_chart_applying_separating_exact_mix() -> None:
    """Hero chart: 3 aspect, beklenen dağılım 1 applying + 1 separating + 1 exact.
    Direction multiplier applying/exact aspect'lerde tightness artırmalı.
    """
    chart = _chart_tsquare_applying_heavy()
    aspects = extract_aspects(chart)

    directions = [a["direction"] for a in aspects]
    assert directions.count("exact") == 1
    assert directions.count("applying") == 1
    assert directions.count("separating") == 1

    # Tightness total'i applying/exact bonus'uyla gözle görülür şekilde artmış olmalı.
    total_tightness = sum(_aspect_tightness(a) for a in aspects)
    no_dir_aspects = [{**a, "direction": None} for a in aspects]
    total_tightness_neutral = sum(_aspect_tightness(a) for a in no_dir_aspects)
    assert total_tightness > total_tightness_neutral
