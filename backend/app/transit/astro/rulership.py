from __future__ import annotations

from typing import Mapping

# P0 deterministic (traditional) sign rulers.
_TRADITIONAL_SIGN_RULERS: Mapping[str, str] = {
    "aries": "Mars",
    "taurus": "Venus",
    "gemini": "Mercury",
    "cancer": "Moon",
    "leo": "Sun",
    "virgo": "Mercury",
    "libra": "Venus",
    "scorpio": "Mars",
    "sagittarius": "Jupiter",
    "capricorn": "Saturn",
    "aquarius": "Saturn",
    "pisces": "Jupiter",
}


def ruler_of(sign: str) -> str:
    return _TRADITIONAL_SIGN_RULERS.get(str(sign or "").strip().lower(), "")


def ruler_of_lower(sign: str) -> str:
    return ruler_of(sign).lower()
