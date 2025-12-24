from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Sequence

from app.helpers.meta_detectors import normalize_node_alias, normalize_planet_key


def _normalize_planet(value: object | None) -> str:
    if not value:
        return ""
    return normalize_node_alias(normalize_planet_key(value))


class AspectMechanicsEngine:
    """Classifies core aspects according to their mechanical energy."""

    ENERGY_MAP: Mapping[str, str] = {
        "square": "friction",
        "opposition": "polarity",
        "trine": "flow",
        "sextile": "flow",
        "quincunx": "blind_spot",
        "semi_sextile": "blind_spot",
    }
    HEAVY_PLANETS = {"saturn", "pluto", "mars", "jupiter"}
    ASPECT_ANGLES: Mapping[str, float] = {
        "conjunction": 0.0,
        "sextile": 60.0,
        "square": 90.0,
        "trine": 120.0,
        "opposition": 180.0,
    }

    def build(self, aspects: Iterable[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
        result: Dict[str, Dict[str, Any]] = {}
        for aspect in aspects:
            aspect_type = str(aspect.get("type") or "").strip().lower()
            if not aspect_type:
                continue
            planet1 = _normalize_planet(aspect.get("planet1") or aspect.get("planet"))
            planet2 = _normalize_planet(aspect.get("planet2") or aspect.get("target"))
            if not planet1 or not planet2:
                continue

            exact_angle = self._fetch_exact_angle(aspect)
            aspect_id = f"{planet1}_{aspect_type}_{planet2}"
            energy_mode = self._determine_energy_mode(aspect_type, planet1, planet2)
            regulation_required = energy_mode in {"friction", "polarity", "blind_spot"}
            awareness_gap = energy_mode == "blind_spot"
            orb_strength = self._classify_orb_strength(aspect_type, exact_angle)
            phase = self._determine_phase(aspect_type, exact_angle)

            result[aspect_id] = {
                "aspect_type": aspect_type,
                "energy_mode": energy_mode,
                "regulation_required": regulation_required,
                "awareness_gap": awareness_gap,
                "regulation_possible": regulation_required,
                "orb_strength": orb_strength,
                "phase": phase,
            }
        return result

    def _determine_energy_mode(self, aspect_type: str, planet1: str, planet2: str) -> str:
        if aspect_type == "conjunction":
            if planet1 in self.HEAVY_PLANETS or planet2 in self.HEAVY_PLANETS:
                return "friction"
            return "flow"
        return self.ENERGY_MAP.get(aspect_type, "flow")

    def _fetch_exact_angle(self, aspect: Mapping[str, Any]) -> float:
        angle = aspect.get("exact_angle")
        if isinstance(angle, (int, float)):
            return float(angle)
        orb = aspect.get("orb")
        if isinstance(orb, (int, float)):
            return float(orb)
        return 0.0

    def _classify_orb_strength(self, aspect_type: str, exact_angle: float) -> str:
        target = self.ASPECT_ANGLES.get(aspect_type, exact_angle)
        deviation = abs(exact_angle - target)
        if deviation <= 1.5:
            return "tight"
        if deviation <= 4.0:
            return "medium"
        return "wide"

    def _determine_phase(self, aspect_type: str, exact_angle: float) -> str:
        target = self.ASPECT_ANGLES.get(aspect_type)
        if target is None:
            return "applying"
        return "applying" if exact_angle <= target else "separating"
