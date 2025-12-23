"""Shared style data for CompositeEngine-derived signals."""
from __future__ import annotations

from typing import Dict

SIGN_STYLE: Dict[str, Dict[str, str]] = {
    "aries": {"cognitive": "direct", "emotional": "impulsive", "expression": "assertive"},
    "taurus": {"cognitive": "practical", "emotional": "steady", "expression": "grounded"},
    "gemini": {"cognitive": "quick", "emotional": "processed_through_thought", "expression": "verbal"},
    "cancer": {"cognitive": "protective", "emotional": "sensitive", "expression": "nurturing"},
    "leo": {"cognitive": "creative", "emotional": "proud", "expression": "radiant"},
    "virgo": {"cognitive": "analytical", "emotional": "self_regulating", "expression": "refined"},
    "libra": {"cognitive": "balancing", "emotional": "considerate", "expression": "harmonizing"},
    "scorpio": {"cognitive": "probing", "emotional": "intense", "expression": "controlled"},
    "sagittarius": {"cognitive": "big_picture", "emotional": "optimistic", "expression": "candid"},
    "capricorn": {"cognitive": "strategic", "emotional": "contained", "expression": "measured"},
    "aquarius": {"cognitive": "innovative", "emotional": "detached", "expression": "unconventional"},
    "pisces": {"cognitive": "imaginative", "emotional": "porous", "expression": "poetic"},
}

ELEMENT_FALLBACK: Dict[str, Dict[str, str]] = {
    "fire": {"cognitive": "fast", "emotional": "bold", "expression": "direct"},
    "earth": {"cognitive": "practical", "emotional": "contained", "expression": "calm"},
    "air": {"cognitive": "quick", "emotional": "light", "expression": "verbal"},
    "water": {"cognitive": "intuitive", "emotional": "sensitive", "expression": "feeling_led"},
}

PROTECTED_STYLE_KEYS: set[str] = {"cognitive", "emotional", "expression"}


def apply_style_modifiers(base: Dict[str, str], modifiers: Dict[str, str] | None) -> Dict[str, str]:
    """Apply modifiers without overwriting protected core style keys."""

    result = dict(base)
    if not modifiers:
        return result
    for key, value in modifiers.items():
        if key in PROTECTED_STYLE_KEYS:
            continue
        result[key] = value
    return result


DEFAULT_STYLE: Dict[str, str] = {"cognitive": "clear", "emotional": "balanced", "expression": "direct"}
