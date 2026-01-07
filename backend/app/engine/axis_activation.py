from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Sequence

from app.helpers.normalize import normalize_node_alias, normalize_planet_key
from app.helpers.placement_utils import extract_planet_signs


class AxisActivationEngine:
    """Detects activated axes through placements and hard aspect signals."""

    AXES: Dict[str, Dict[str, Any]] = {
        "1-7": {
            "signs": {"aries", "libra"},
            "rulers": {"mars", "venus"},
            "points": {"ascendant", "descendant"},
        },
        "4-10": {
            "signs": {"cancer", "capricorn"},
            "rulers": {"moon", "saturn"},
            "points": {"midheaven", "imum_coeli"},
        },
        "2-8": {
            "signs": {"taurus", "scorpio"},
            "rulers": {"venus", "mars"},
            "points": set(),
        },
        "3-9": {
            "signs": {"gemini", "sagittarius"},
            "rulers": {"mercury", "jupiter"},
            "points": set(),
        },
    }

    def build(
        self,
        placements: Sequence[str],
        *,
        core_aspects: Iterable[Mapping[str, Any]],
    ) -> Dict[str, Any]:
        planet_signs = extract_planet_signs(placements)
        sign_map: Dict[str, List[str]] = {}
        for planet, sign in planet_signs.items():
            normalized_planet = normalize_node_alias(planet)
            if not normalized_planet:
                continue
            sign_map.setdefault(sign, []).append(normalized_planet)
        active_axes = []
        axis_aspect_count = 0

        normalized_aspects = self._normalize_aspects(core_aspects)
        for axis, info in self.AXES.items():
            if self._has_axis_activation(axis, info, sign_map):
                active_axes.append(axis)
            elif self._aspect_activates_axis(axis, info, normalized_aspects):
                active_axes.append(axis)
                axis_aspect_count += 1
            elif self._aspect_activates_axis(
                axis, info, normalized_aspects, require_existing_planet=True
            ):
                active_axes.append(axis)
                axis_aspect_count += 1

        tension = self._derive_tension(active_axes, axis_aspect_count)
        return {"active_axes": sorted(active_axes), "axis_tension": tension}

    @staticmethod
    def _normalize_aspects(aspects: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        for entry in aspects:
            planet1 = normalize_node_alias(normalize_planet_key(entry.get("planet1") or entry.get("planet")))
            planet2 = normalize_node_alias(normalize_planet_key(entry.get("planet2") or entry.get("target")))
            aspect_type = str(entry.get("type") or entry.get("aspect") or "").strip().lower()
            if not (planet1 and planet2 and aspect_type):
                continue
            normalized.append({"planet1": planet1, "planet2": planet2, "type": aspect_type})
        return normalized

    def _has_axis_activation(
        self,
        axis: str,
        info: Dict[str, Any],
        sign_map: Dict[str, List[str]],
    ) -> bool:
        sides = info["signs"]
        planets_on_axis = sum(len(sign_map.get(sign, [])) for sign in sides)
        return planets_on_axis >= 2 and any(sign_map.get(sign) for sign in sides)

    def _aspect_activates_axis(
        self,
        axis: str,
        info: Dict[str, Any],
        aspects: List[Dict[str, Any]],
        require_existing_planet: bool = False,
    ) -> bool:
        rulers = info["rulers"]
        points = info["points"]
        for aspect in aspects:
            if aspect["type"] not in {"square", "opposition"}:
                continue
            planets = {aspect["planet1"], aspect["planet2"]}
            intersects = planets & rulers or planets & points
            if not intersects:
                continue
            if require_existing_planet and not planets & rulers:
                continue
            return True
        return False

    @staticmethod
    def _derive_tension(active_axes: List[str], axis_aspect_count: int) -> str:
        score = len(active_axes) + axis_aspect_count
        if score >= 3:
            return "high"
        if score == 2:
            return "medium"
        return "low"
