"""Service helpers for chart calculation and serialization."""
from __future__ import annotations

from typing import Any, Dict, List, Mapping

from app.astro.chart_engine.builder import calculate_chart_from_birth_details


def compute_natal_chart(birth_date: str, birth_time: str, birth_place: str) -> Dict[str, Any]:
    """Wrapper around chart builder for dependency inversion."""

    return calculate_chart_from_birth_details(birth_date, birth_time, birth_place)


def serialize_planets(planets_data: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Normalize planet payload for rule engine consumption."""

    serialized: List[Dict[str, Any]] = []
    if not isinstance(planets_data, Mapping):
        return serialized
    for name, payload in planets_data.items():
        if not isinstance(payload, Mapping):
            continue
        serialized.append(
            {
                "planet": str(name),
                "sign": payload.get("sign"),
                "house": payload.get("house"),
                "degree": payload.get("longitude"),
            }
        )
    return serialized


def serialize_aspects(aspects_data: Any) -> List[Dict[str, Any]]:
    """Normalize aspect payload for rule engine consumption."""

    serialized: List[Dict[str, Any]] = []
    if not isinstance(aspects_data, list):
        return serialized
    for aspect in aspects_data:
        if not isinstance(aspect, Mapping):
            continue
        planet_one = aspect.get("planet1")
        planet_two = aspect.get("planet2")
        aspect_type = aspect.get("type") or aspect.get("aspect")
        if not (planet_one and planet_two and aspect_type):
            continue
        serialized.append(
            {
                "planet1": str(planet_one),
                "planet2": str(planet_two),
                "type": str(aspect_type),
                "orb": aspect.get("orb") or aspect.get("exact_angle"),
            }
        )
    return serialized
