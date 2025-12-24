from __future__ import annotations

from typing import Iterable, List, Mapping, Sequence

from app.helpers.meta_detectors import normalize_node_alias, normalize_planet_key


HOUSE_ORDINALS = {
    1: "1st",
    2: "2nd",
    3: "3rd",
    4: "4th",
    5: "5th",
    6: "6th",
    7: "7th",
    8: "8th",
    9: "9th",
    10: "10th",
    11: "11th",
    12: "12th",
}


def derive_placements(planets: Sequence[Mapping[str, object]]) -> List[str]:
    """Normalize placements for composite engine input."""

    placements: List[str] = []
    for entry in planets:
        planet = entry.get("planet")
        normalized = normalize_node_alias(normalize_planet_key(planet))
        if not normalized:
            continue
        sign = entry.get("sign")
        if isinstance(sign, str) and sign.strip():
            slug = sign.strip().lower().replace(" ", "_")
            placements.append(f"{normalized}_in_{slug}")
        house = entry.get("house")
        if isinstance(house, (int, float, str)):
            try:
                house_value = int(house)
            except (TypeError, ValueError):
                continue
            ordinal = HOUSE_ORDINALS.get(house_value, f"{house_value}th")
            placements.append(f"{normalized}_in_{ordinal}_house")
    return placements


def derive_core_aspects(aspects: Sequence[Mapping[str, object]]) -> List[str]:
    """Produce normalized core aspect identifiers."""

    ids: List[str] = []
    for aspect in aspects:
        planet1 = normalize_node_alias(normalize_planet_key(aspect.get("planet1") or aspect.get("planet") or ""))
        planet2 = normalize_node_alias(normalize_planet_key(aspect.get("planet2") or aspect.get("target") or ""))
        aspect_type = str(aspect.get("type") or aspect.get("aspect") or "").strip().lower()
        if not (planet1 and planet2 and aspect_type):
            continue
        ids.append(f"{planet1}_{aspect_type}_{planet2}")
        ids.append(f"{planet2}_{aspect_type}_{planet1}")
    return ids
