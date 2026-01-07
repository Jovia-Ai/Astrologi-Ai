from __future__ import annotations

from typing import Any, Dict, List

from app.engine.context_maps import DEFAULT_CONTEXT, HOUSE_CONTEXT
from app.engine.style_maps import DEFAULT_STYLE, ELEMENT_FALLBACK, SIGN_STYLE


class CompositeEngine:
    """
    CompositeEngine builds lived-experience composites.
    GOLDEN PATH v1: base identity composites only.
    """

    DEFAULT_COMPOSITE_PRIORITY = 0.5

    def __init__(self) -> None:
        pass

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_composites(self, chart_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        GOLDEN PATH v1
        - Only base composites
        - No rule-based composites
        - Identity domain only
        """

        return self._build_base_identity_composites(chart_data)

    # ------------------------------------------------------------------
    # Base identity composite
    # ------------------------------------------------------------------

    def _build_base_identity_composites(self, chart_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        composites: List[Dict[str, Any]] = []

        sun = chart_data.get("sun")
        moon = chart_data.get("moon")
        if not sun or not moon:
            planets = chart_data.get("planets") if isinstance(chart_data.get("planets"), dict) else {}
            sun = sun or planets.get("sun")
            moon = moon or planets.get("moon")

        if not sun or not moon:
            return composites

        composite = {
            "composite_id": "identity_core_tension",
            "domain": "identity",
            "priority_score": self.DEFAULT_COMPOSITE_PRIORITY,
            "base_interpretation": (
                "Bu yapı, kimliğini kontrollü ve yapılandırılmış bir duruş "
                "üzerinden kurmaya çalışan bir yönelimle, daha içgüdüsel ve "
                "duygusal tepkiler üreten bir tarafın aynı anda aktif olmasını ifade eder."
            ),
            "sources": [
                "sun_identity_axis",
                "moon_emotional_axis",
            ],
        }

        composites.append(composite)
        return composites

    def _sign_style(self, sign: str) -> Dict[str, str]:
        """Legacy helper for sign-based style lookups."""
        normalized = str(sign or "").strip().lower()
        style = SIGN_STYLE.get(normalized)
        if style:
            return dict(style)
        element = None
        if normalized:
            element = {
                "aries": "fire",
                "taurus": "earth",
                "gemini": "air",
                "cancer": "water",
                "leo": "fire",
                "virgo": "earth",
                "libra": "air",
                "scorpio": "water",
                "sagittarius": "fire",
                "capricorn": "earth",
                "aquarius": "air",
                "pisces": "water",
            }.get(normalized)
        if element and element in ELEMENT_FALLBACK:
            return dict(ELEMENT_FALLBACK[element])
        return dict(DEFAULT_STYLE)

    def _house_context(self, house: int) -> Dict[str, str]:
        """Legacy helper for house-based context lookups."""
        try:
            house_value = int(house)
        except (TypeError, ValueError):
            house_value = None
        if house_value in HOUSE_CONTEXT:
            return dict(HOUSE_CONTEXT[house_value])
        return dict(DEFAULT_CONTEXT)
