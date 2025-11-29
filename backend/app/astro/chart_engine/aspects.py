"""Aspect detection helpers."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

ASPECT_DEFINITIONS: Sequence[Tuple[str, int, int]] = (
    ("Conjunction", 0, 8),
    ("Sextile", 60, 6),
    ("Square", 90, 6),
    ("Trine", 120, 6),
    ("Opposition", 180, 8),
)


def diff_angle(lon1: float, lon2: float) -> float:
    diff = abs(lon1 - lon2) % 360
    return diff if diff <= 180 else 360 - diff


def build_angle_points(angles: Mapping[str, Any]) -> List[Tuple[str, float]]:
    points: List[Tuple[str, float]] = []
    asc = angles.get("ascendant")
    mc = angles.get("midheaven")
    if isinstance(asc, (int, float)):
        points.append(("Ascendant", float(asc)))
        points.append(("Descendant", (float(asc) + 180) % 360))
    if isinstance(mc, (int, float)):
        points.append(("Midheaven", float(mc)))
        points.append(("Imum Coeli", (float(mc) + 180) % 360))
    return points


def calculate_chart_aspects(
    planets: Mapping[str, Mapping[str, Any]],
    *,
    angles: Mapping[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    """Detect aspects within a single chart among planets and key angles."""

    planet_items: List[Tuple[str, float]] = [
        (name, data["longitude"])
        for name, data in planets.items()
        if isinstance(data, Mapping) and isinstance(data.get("longitude"), (int, float))
    ]
    if angles:
        planet_items.extend(build_angle_points(angles))

    aspects: List[Dict[str, Any]] = []
    for i in range(len(planet_items)):
        for j in range(i + 1, len(planet_items)):
            name_a, lon_a = planet_items[i]
            name_b, lon_b = planet_items[j]
            diff = diff_angle(lon_a, lon_b)
            for aspect_name, aspect_angle, orb in ASPECT_DEFINITIONS:
                if abs(diff - aspect_angle) <= orb:
                    aspects.append(
                        {
                            "planet1": name_a,
                            "planet2": name_b,
                            "aspect": aspect_name,
                            "exact_angle": round(diff, 2),
                        }
                    )
                    break
    return aspects
