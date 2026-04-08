"""Service helpers for chart calculation and serialization."""
from __future__ import annotations

from typing import Any, Dict, List, Mapping

from app.astro.chart_engine.builder import calculate_chart_from_birth_details


def compute_natal_chart(
    birth_date: str,
    birth_time: str,
    birth_place: str,
    *,
    birth_latitude: Any = None,
    birth_longitude: Any = None,
    birth_timezone: str | None = None,
) -> Dict[str, Any]:
    """Wrapper around chart builder for dependency inversion."""

    return calculate_chart_from_birth_details(
        birth_date,
        birth_time,
        birth_place,
        latitude=birth_latitude,
        longitude=birth_longitude,
        timezone=birth_timezone,
    )


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
        orb_value = aspect.get("orb")
        if orb_value is None:
            expected = aspect.get("aspect_angle")
            exact = aspect.get("exact_angle") or aspect.get("angle")
            if isinstance(expected, (int, float)) and isinstance(exact, (int, float)):
                orb_value = abs(float(exact) - float(expected))
        serialized.append(
            {
                "planet1": str(planet_one),
                "planet2": str(planet_two),
                "type": str(aspect_type),
                "angle": aspect.get("angle"),
                "aspect_angle": aspect.get("aspect_angle"),
                "orb": orb_value,
                "exact_angle": aspect.get("exact_angle"),
            }
        )
    return serialized
