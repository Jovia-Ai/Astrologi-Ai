from __future__ import annotations

from typing import Any, Mapping

PLANET_POINTS = {
    "sun",
    "moon",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
}

ANGLE_POINTS = {"asc", "dsc", "mc", "ic"}
NODE_POINTS = {"north_node", "south_node"}
SPECIAL_POINTS = {"lilith", "chiron", "vertex", "fortune"}

ALLOWED_PUBLIC_POINTS = PLANET_POINTS | ANGLE_POINTS | NODE_POINTS | SPECIAL_POINTS

POINT_WEIGHTS = {
    "planet": 1.0,
    "angle": 1.0,
    "node": 0.9,
    "lilith": 0.8,
    "chiron": 0.75,
    "vertex": 0.6,
    "fortune": 0.6,
    "other": 0.4,
}


def normalize_point_token(value: Any) -> str:
    token = str(value or "").strip().lower().replace("-", " ").replace("_", " ")
    token = " ".join(token.split())
    aliases = {
        "north node": "north_node",
        "south node": "south_node",
        "ascending": "asc",
        "ascendant": "asc",
        "descendant": "dsc",
        "medium coeli": "mc",
        "midheaven": "mc",
        "imum coeli": "ic",
    }
    return aliases.get(token, token.replace(" ", "_"))


def point_kind(value: Any) -> str:
    token = normalize_point_token(value)
    if token in PLANET_POINTS:
        return "planet"
    if token in ANGLE_POINTS:
        return "angle"
    if token in NODE_POINTS:
        return "node"
    if token in {"lilith", "chiron", "vertex", "fortune"}:
        return token
    return "other"


def point_weight(value: Any) -> float:
    kind = point_kind(value)
    return float(POINT_WEIGHTS.get(kind, POINT_WEIGHTS["other"]))


def is_public_point(value: Any) -> bool:
    return normalize_point_token(value) in ALLOWED_PUBLIC_POINTS


def is_public_event(item: Mapping[str, Any]) -> bool:
    transit = item.get("transit_body")
    target = item.get("natal_point")
    return is_public_point(transit) and is_public_point(target)
