from __future__ import annotations

from typing import Any

from .models import (
    ProfileInsightAstroSource,
    ProfileInsightCard,
    ProfileInsightContent,
    ProfileInsightMeta,
)
from .moon_defense_mechanism_library import MOON_DEFENSE_MECHANISM_V1

_HEADLINE = "Senin savunma mekanizman"
_SUBHEADLINE = "Ay burcuna göre duygularını koruma biçimin"
_MODULE_ID = "moon_defense_mechanism"
_DEFAULT_PRIORITY = 32

_SIGN_ALIASES = {
    "aries": "Aries",
    "taurus": "Taurus",
    "gemini": "Gemini",
    "cancer": "Cancer",
    "leo": "Leo",
    "virgo": "Virgo",
    "libra": "Libra",
    "scorpio": "Scorpio",
    "sagittarius": "Sagittarius",
    "capricorn": "Capricorn",
    "aquarius": "Aquarius",
    "pisces": "Pisces",
    "koç": "Aries",
    "koc": "Aries",
    "boğa": "Taurus",
    "boga": "Taurus",
    "ikizler": "Gemini",
    "yengeç": "Cancer",
    "yengec": "Cancer",
    "aslan": "Leo",
    "başak": "Virgo",
    "basak": "Virgo",
    "terazi": "Libra",
    "akrep": "Scorpio",
    "yay": "Sagittarius",
    "oğlak": "Capricorn",
    "oglak": "Capricorn",
    "kova": "Aquarius",
    "balık": "Pisces",
    "balik": "Pisces",
}


def _normalize_sign(sign: str | None) -> str:
    if not sign:
        return ""
    key = str(sign).strip().lower()
    return _SIGN_ALIASES.get(key, "")


def build_moon_defense_mechanism(moon_sign: str | None) -> dict[str, Any] | None:
    normalized_sign = _normalize_sign(moon_sign)
    content = MOON_DEFENSE_MECHANISM_V1.get(normalized_sign)
    if not content:
        return None
    module = ProfileInsightCard(
        module_id=_MODULE_ID,
        headline=_HEADLINE,
        subheadline=_SUBHEADLINE,
        moon_sign=normalized_sign,
        title=content["title"],
        body=content["body"],
        tone="hard_truth_softened",
        share_text=content["share_text"],
        priority=_DEFAULT_PRIORITY,
        astro_source=ProfileInsightAstroSource(value=normalized_sign),
        content=ProfileInsightContent(
            title=content["title"],
            body=content["body"],
            share_text=content["share_text"],
            tone="hard_truth_softened",
        ),
        meta=ProfileInsightMeta(
            priority=_DEFAULT_PRIORITY,
            expandable=True,
            version="v1",
        ),
    )
    return module.model_dump()


def build_profile_insight_modules(*, moon_sign: str | None) -> list[dict[str, Any]]:
    module = build_moon_defense_mechanism(moon_sign)
    return [module] if module else []
