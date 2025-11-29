"""Formatting helpers for chart outputs."""
from __future__ import annotations

from typing import Any, Dict, List

from app.astro.chart_engine.aspects import ASPECT_DEFINITIONS

PLANET_DISPLAY_ORDER = [
    "Sun",
    "Moon",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
    "North Node",
    "Lilith",
    "Chiron",
    "Fortune",
    "Vertex",
]

ASPECT_ANGLE_LOOKUP = {name: angle for name, angle, _ in ASPECT_DEFINITIONS}


def _ordinal(value: int) -> str:
    suffixes = {1: "st", 2: "nd", 3: "rd"}
    if 10 <= value % 100 <= 20:
        suffix = "th"
    else:
        suffix = suffixes.get(value % 10, "th")
    return f"{value}{suffix}"


def _format_degree(degree: int | float | None, minute: int | float | None) -> str:
    deg = int(degree or 0)
    minutes_total = int(round(minute or 0))
    if minutes_total >= 60:
        deg += minutes_total // 60
        minutes_total %= 60
    return f"{deg}°{str(minutes_total).zfill(2)}'"


def build_formatted_planet_positions(chart: Dict[str, Any]) -> List[str]:
    planets = chart.get("planets") or {}
    ordered_names = [name for name in PLANET_DISPLAY_ORDER if name in planets]
    ordered_names.extend(name for name in planets.keys() if name not in ordered_names)

    formatted: List[str] = []
    for name in ordered_names:
        details = planets.get(name) or {}
        sign = details.get("sign") or "Unknown"
        degree = details.get("degree")
        minute = details.get("minute")
        house = details.get("house")
        retrograde = details.get("retrograde")
        retro_suffix = ", Retrograde" if retrograde else ""
        house_label = f"{_ordinal(int(house))} House" if isinstance(house, int) and house > 0 else "Unknown House"
        formatted.append(
            f"{name} in {sign} {_format_degree(degree, minute)}, in {house_label}{retro_suffix}"
        )
    return formatted


def build_formatted_house_positions(chart: Dict[str, Any]) -> List[str]:
    houses = chart.get("house_positions") or {}
    formatted: List[str] = []
    for index in sorted(houses, key=lambda x: int(x)):
        details = houses[index] or {}
        sign = details.get("sign") or "Unknown"
        degree = details.get("degree")
        minute = details.get("minute")
        formatted.append(
            f"{_ordinal(int(index))} House in {sign} {_format_degree(degree, minute)}"
        )
    return formatted


def build_formatted_aspects(chart: Dict[str, Any]) -> List[str]:
    aspects = chart.get("aspects") or []
    formatted: List[str] = []
    for item in aspects:
        planet1 = item.get("planet1") or "Unknown"
        planet2 = item.get("planet2") or "Unknown"
        aspect_name = item.get("aspect") or "Aspect"
        exact_angle = item.get("exact_angle")

        expected_angle = ASPECT_ANGLE_LOOKUP.get(aspect_name)
        orb_value: float | None = None
        if expected_angle is not None and isinstance(exact_angle, (int, float)):
            orb_value = abs(exact_angle - expected_angle)

        if orb_value is not None:
            orb_degrees = int(orb_value)
            orb_minutes = int(round((orb_value - orb_degrees) * 60))
            if orb_minutes >= 60:
                orb_degrees += orb_minutes // 60
                orb_minutes %= 60
            orb_text = f"{orb_degrees}°{str(orb_minutes).zfill(2)}'"
            formatted.append(f"{planet1} {aspect_name} {planet2} (Orb: {orb_text})")
        else:
            formatted.append(f"{planet1} {aspect_name} {planet2}")
    return formatted
