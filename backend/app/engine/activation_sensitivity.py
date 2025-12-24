from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Sequence


class ActivationSensitivityEngine:
    """Rates composites by structural sensitivity without interpretation."""

    ANGULAR_HOUSES = {"1st_house", "4th_house", "7th_house", "10th_house"}
    ORB_WEIGHTS = {"tight": 3, "medium": 2, "wide": 1}

    def build(
        self,
        composites: Sequence[Mapping[str, Any]],
        aspect_mechanics: Mapping[str, Mapping[str, Any]] | None = None,
    ) -> Dict[str, str]:
        mechanics = aspect_mechanics or {}
        scores: Dict[str, str] = {}
        for composite in composites:
            comp_id = composite.get("composite_id")
            if not comp_id:
                continue
            sources = composite.get("sources", []) or []

            orb_score = 0
            aspect_hits = 0
            angular_hits = 0
            for source in sources:
                normalized = str(source).lower()
                if "_house" in normalized:
                    if any(h in normalized for h in self.ANGULAR_HOUSES):
                        angular_hits += 1
                if normalized in mechanics:
                    aspect_hits += 1
                    strength = mechanics[normalized].get("orb_strength")
                    orb_score += self._orb_weight(strength)

            total = orb_score + angular_hits * 2
            sensitivity = self._classify_sensitivity(total, aspect_hits)
            scores[comp_id] = sensitivity
        return scores

    @classmethod
    def _orb_weight(cls, strength: object | None) -> int:
        return cls.ORB_WEIGHTS.get(str(strength).lower(), 1)

    @staticmethod
    def _classify_sensitivity(total_score: float, aspect_hits: int) -> str:
        if total_score >= 6 or aspect_hits >= 4:
            return "high"
        if total_score >= 3 or aspect_hits >= 2:
            return "medium"
        return "low"
