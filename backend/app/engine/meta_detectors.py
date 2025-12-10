"""Meta pattern detectors for natal charts."""
from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable, Mapping

ELEMENT_MAP = {
    "Aries": "Fire",
    "Taurus": "Earth",
    "Gemini": "Air",
    "Cancer": "Water",
    "Leo": "Fire",
    "Virgo": "Earth",
    "Libra": "Air",
    "Scorpio": "Water",
    "Sagittarius": "Fire",
    "Capricorn": "Earth",
    "Aquarius": "Air",
    "Pisces": "Water",
}

MODALITY_MAP = {
    "Aries": "Cardinal",
    "Taurus": "Fixed",
    "Gemini": "Mutable",
    "Cancer": "Cardinal",
    "Leo": "Fixed",
    "Virgo": "Mutable",
    "Libra": "Cardinal",
    "Scorpio": "Fixed",
    "Sagittarius": "Mutable",
    "Capricorn": "Cardinal",
    "Aquarius": "Fixed",
    "Pisces": "Mutable",
}


def analyze_planets(planets: Iterable[Mapping[str, object]]) -> Dict[str, object]:
    """Return normalized planet metadata, element/modality counts, and house aggregates."""

    planet_signs: Dict[str, str] = {}
    planet_houses: Dict[str, int] = {}
    element_counts: Counter[str] = Counter()
    modality_counts: Counter[str] = Counter()
    house_counts: Counter[int] = Counter()
    normalized_planets: Dict[str, Dict[str, object | None]] = {}

    for entry in planets:
        planet = entry.get("planet")
        normalized_planet = normalize_node_alias(normalize_planet_key(planet))
        if not normalized_planet:
            continue

        sign = entry.get("sign")
        house = entry.get("house")
        degree = entry.get("degree")
        sign_value: str | None = None
        sign_normalized: str | None = None
        if isinstance(sign, str):
            sign_value = sign.strip()
            sign_normalized = sign_value.lower()
            planet_signs[normalized_planet] = sign_normalized
            formatted_sign = sign_value.title()
            element = ELEMENT_MAP.get(formatted_sign)
            modality = MODALITY_MAP.get(formatted_sign)
            if element:
                element_counts[element] += 1
            if modality:
                modality_counts[modality] += 1

        house_value: int | None = None
        if house is not None:
            try:
                house_value = int(house)
            except (TypeError, ValueError):
                house_value = None
        if house_value is not None:
            planet_houses[normalized_planet] = house_value
            house_counts[house_value] += 1

        normalized_planets[normalized_planet] = {
            "sign": sign_normalized if isinstance(sign_value, str) else None,
            "house": house_value,
            "degree": degree,
        }

    stelliums = detect_stelliums(house_counts)
    dominant_elements = detect_dominance(element_counts, minimum=4)
    dominant_modalities = detect_dominance(modality_counts, minimum=4)
    house_clusters = detect_house_clusters(house_counts)

    return {
        "planet_signs": planet_signs,
        "planet_houses": planet_houses,
        "element_counts": element_counts,
        "modality_counts": modality_counts,
        "house_counts": house_counts,
        "stelliums": stelliums,
        "dominant_elements": dominant_elements,
        "dominant_modalities": dominant_modalities,
        "house_clusters": house_clusters,
        "normalized_planets": normalized_planets,
    }


def detect_stelliums(house_counts: Counter[int], minimum: int = 3) -> Dict[int, int]:
    """Return houses exceeding the stellium threshold."""

    return {house: count for house, count in house_counts.items() if count >= minimum}


def detect_dominance(counter: Counter[str], minimum: int = 4) -> Dict[str, int]:
    """Return element/modality types meeting dominance threshold."""

    return {key: count for key, count in counter.items() if count >= minimum}


def detect_house_clusters(house_counts: Counter[int], minimum: int = 3) -> Dict[int, int]:
    """Return houses that host repeated experiential focus."""

    return {house: count for house, count in house_counts.items() if count >= minimum}


def normalize_planet_key(value: object | None) -> str:
    if not value:
        return ""
    return str(value).strip().lower().replace(" ", "_")


def normalize_node_alias(value: str) -> str:
    normalized = value.strip().lower()
    if normalized in {"north_node", "true_node", "mean_node", "node"}:
        return "node"
    if normalized in {"lilith", "black_moon_lilith"}:
        return "lilith"
    return normalized
