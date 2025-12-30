from __future__ import annotations

from typing import Any, Dict, List


class CompositeEngine:
    """
    CompositeEngine builds lived-experience composites.
    GOLDEN PATH v1: base identity composites only.
    """

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
