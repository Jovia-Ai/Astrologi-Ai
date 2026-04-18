"""Unit tests for app.astro.dignity — Faz 2 PR 6.

Planet × sign dignity tablosu + weight + per-archetype bonus lookup.
"""
from __future__ import annotations

import pytest

from app.astro.dignity import (
    ARCHETYPE_SIGNATURE_PLANETS,
    DIGNITY_WEIGHTS,
    EXALTATIONS,
    RULERSHIPS,
    archetype_dignity_bonus,
    dignity_weight,
    essential_dignity,
)


# --------------------------------------------------------------------------
# Weight table (behavior-lock — konservatif başlangıç değerleri)
# --------------------------------------------------------------------------


def test_dignity_weights_are_conservative() -> None:
    assert DIGNITY_WEIGHTS == {
        "domicile": 0.15,
        "exaltation": 0.10,
        "peregrine": 0.0,
        "detriment": -0.10,
        "fall": -0.15,
    }


# --------------------------------------------------------------------------
# Traditional 7 planets — full dignity matrix
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "planet,sign,expected",
    [
        # Sun: rules Leo, exalts Aries, detriment Aquarius, fall Libra
        ("Sun", "Leo", "domicile"),
        ("Sun", "Aries", "exaltation"),
        ("Sun", "Aquarius", "detriment"),
        ("Sun", "Libra", "fall"),
        ("Sun", "Gemini", "peregrine"),
        # Moon: Cancer/Taurus/Capricorn/Scorpio
        ("Moon", "Cancer", "domicile"),
        ("Moon", "Taurus", "exaltation"),
        ("Moon", "Capricorn", "detriment"),
        ("Moon", "Scorpio", "fall"),
        ("Moon", "Libra", "peregrine"),
        # Mercury: Gemini+Virgo / Virgo exalt / Sag+Pisces detriment / Pisces fall
        ("Mercury", "Gemini", "domicile"),
        ("Mercury", "Virgo", "domicile"),  # domicile > exaltation precedence
        ("Mercury", "Sagittarius", "detriment"),
        ("Mercury", "Pisces", "detriment"),  # detriment > fall precedence on tie
        # Venus: Taurus+Libra / Pisces exalt / Aries+Scorpio detriment / Virgo fall
        ("Venus", "Taurus", "domicile"),
        ("Venus", "Libra", "domicile"),
        ("Venus", "Pisces", "exaltation"),
        ("Venus", "Aries", "detriment"),
        ("Venus", "Scorpio", "detriment"),
        ("Venus", "Virgo", "fall"),
        # Mars: Aries+Scorpio / Capricorn exalt / Taurus+Libra detriment / Cancer fall
        ("Mars", "Aries", "domicile"),
        ("Mars", "Scorpio", "domicile"),
        ("Mars", "Capricorn", "exaltation"),
        ("Mars", "Taurus", "detriment"),
        ("Mars", "Libra", "detriment"),
        ("Mars", "Cancer", "fall"),
        # Jupiter: Sag+Pisces / Cancer exalt / Gem+Virgo detriment / Capricorn fall
        ("Jupiter", "Sagittarius", "domicile"),
        ("Jupiter", "Pisces", "domicile"),
        ("Jupiter", "Cancer", "exaltation"),
        ("Jupiter", "Gemini", "detriment"),
        ("Jupiter", "Virgo", "detriment"),
        ("Jupiter", "Capricorn", "fall"),
        # Saturn: Capricorn+Aquarius / Libra exalt / Cancer+Leo detriment / Aries fall
        ("Saturn", "Capricorn", "domicile"),
        ("Saturn", "Aquarius", "domicile"),
        ("Saturn", "Libra", "exaltation"),
        ("Saturn", "Cancer", "detriment"),
        ("Saturn", "Leo", "detriment"),
        ("Saturn", "Aries", "fall"),
    ],
)
def test_traditional_planet_dignities(planet: str, sign: str, expected: str) -> None:
    assert essential_dignity(planet, sign) == expected


# --------------------------------------------------------------------------
# Modern planets — only domicile, else peregrine (opinionated decision)
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "planet,sign,expected",
    [
        ("Uranus", "Aquarius", "domicile"),
        ("Uranus", "Leo", "peregrine"),       # NO detriment for modern
        ("Uranus", "Aries", "peregrine"),     # no exaltation for modern
        ("Neptune", "Pisces", "domicile"),
        ("Neptune", "Virgo", "peregrine"),
        ("Neptune", "Leo", "peregrine"),
        ("Pluto", "Scorpio", "domicile"),
        ("Pluto", "Taurus", "peregrine"),
        ("Pluto", "Capricorn", "peregrine"),
    ],
)
def test_modern_planet_dignities_only_domicile(planet: str, sign: str, expected: str) -> None:
    """Modern planetler için sadece domicile; exaltation/det/fall yok."""
    assert essential_dignity(planet, sign) == expected


# --------------------------------------------------------------------------
# Input normalization — case-insensitive, whitespace, None fallback
# --------------------------------------------------------------------------


def test_case_insensitive_lookups() -> None:
    assert essential_dignity("SUN", "LEO") == "domicile"
    assert essential_dignity("saturn", "capricorn") == "domicile"
    assert essential_dignity("  Mars  ", "  Aries  ") == "domicile"


@pytest.mark.parametrize(
    "planet,sign",
    [
        (None, "Leo"),
        ("Sun", None),
        ("", "Leo"),
        ("Sun", ""),
        (None, None),
    ],
)
def test_missing_input_falls_back_to_peregrine(planet, sign) -> None:
    assert essential_dignity(planet, sign) == "peregrine"


def test_unknown_planet_or_sign_falls_back_to_peregrine() -> None:
    assert essential_dignity("Chiron", "Leo") == "peregrine"
    assert essential_dignity("Sun", "Ophiuchus") == "peregrine"
    assert essential_dignity("xyz", "abc") == "peregrine"


# --------------------------------------------------------------------------
# dignity_weight wrapper
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "planet,sign,expected",
    [
        ("Sun", "Leo", 0.15),
        ("Sun", "Aries", 0.10),
        ("Sun", "Aquarius", -0.10),
        ("Sun", "Libra", -0.15),
        ("Sun", "Gemini", 0.0),
        ("Uranus", "Aquarius", 0.15),
        ("Uranus", "Leo", 0.0),   # modern no-detriment
        (None, "Leo", 0.0),
    ],
)
def test_dignity_weight_returns_correct_values(
    planet, sign, expected: float
) -> None:
    assert dignity_weight(planet, sign) == expected


# --------------------------------------------------------------------------
# archetype_dignity_bonus — summation + graceful fallback
# --------------------------------------------------------------------------


def test_archetype_dignity_bonus_single_signature_planet() -> None:
    """Builder → Saturn. Saturn in Capricorn (domicile) → +0.15."""
    bonus = archetype_dignity_bonus("builder", {"Saturn": "Capricorn"})
    assert bonus == 0.15


def test_archetype_dignity_bonus_dual_signature_sums_additively() -> None:
    """Guardian → (Saturn, Moon). Saturn domicile + Moon domicile = +0.30."""
    bonus = archetype_dignity_bonus(
        "guardian",
        {"Saturn": "Capricorn", "Moon": "Cancer"},
    )
    assert bonus == pytest.approx(0.30, abs=1e-9)


def test_archetype_dignity_bonus_mixed_dignities() -> None:
    """Guardian: Saturn in Aries (fall, -0.15) + Moon in Cancer (domicile, +0.15) = 0."""
    bonus = archetype_dignity_bonus(
        "guardian",
        {"Saturn": "Aries", "Moon": "Cancer"},
    )
    assert bonus == pytest.approx(0.0, abs=1e-9)


def test_archetype_dignity_bonus_planet_not_in_chart_treated_as_peregrine() -> None:
    """Signature planet chart'ta yoksa o planet için 0 (peregrine)."""
    # Depthkeeper → (Pluto, Mars). Sadece Pluto var, Mars eksik.
    bonus = archetype_dignity_bonus(
        "depthkeeper",
        {"Pluto": "Scorpio"},  # domicile, Mars missing → 0
    )
    assert bonus == pytest.approx(0.15, abs=1e-9)


def test_archetype_dignity_bonus_empty_chart_returns_zero() -> None:
    assert archetype_dignity_bonus("builder", {}) == 0.0


def test_archetype_dignity_bonus_unknown_archetype_returns_zero() -> None:
    """Tablo dışı archetype → 0 (graceful fallback, scoring kırılmaz)."""
    assert archetype_dignity_bonus("mystery_archetype", {"Saturn": "Capricorn"}) == 0.0


def test_archetype_dignity_bonus_empty_id_returns_zero() -> None:
    assert archetype_dignity_bonus("", {"Saturn": "Capricorn"}) == 0.0
    assert archetype_dignity_bonus(None, {"Saturn": "Capricorn"}) == 0.0


def test_archetype_dignity_bonus_case_insensitive_planet_names() -> None:
    """Chart dict key'leri 'saturn' veya 'Saturn' olabilir — ikisi de tanınır."""
    bonus_capitalized = archetype_dignity_bonus("builder", {"Saturn": "Capricorn"})
    bonus_lower = archetype_dignity_bonus("builder", {"saturn": "Capricorn"})
    assert bonus_capitalized == bonus_lower == 0.15


# --------------------------------------------------------------------------
# Table completeness — behavior-lock for signature planet map
# --------------------------------------------------------------------------


def test_archetype_signature_planets_covers_known_archetypes() -> None:
    """Taxonomy'de bilinen tüm archetype'ler için signature planet mapping olmalı.
    Yeni archetype eklenirse bu test kırmızı olur — mapping eklemeyi zorlar.
    """
    known = {
        "builder", "visionary", "analyst", "connector",
        "guardian", "depthkeeper", "catalyst",
    }
    mapping_keys = set(ARCHETYPE_SIGNATURE_PLANETS.keys())
    missing = known - mapping_keys
    assert not missing, f"Signature mapping'den eksik archetype'ler: {missing}"


def test_rulerships_cover_all_planets() -> None:
    """Tüm 10 planet'in en az bir rulership'i olmalı."""
    expected = {"sun", "moon", "mercury", "venus", "mars",
                "jupiter", "saturn", "uranus", "neptune", "pluto"}
    assert set(RULERSHIPS.keys()) == expected


def test_exaltations_only_traditional_seven() -> None:
    """Exaltation sadece traditional 7 planet için tanımlı."""
    assert set(EXALTATIONS.keys()) == {
        "sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn",
    }
