from __future__ import annotations

BODY_ALIASES = {
    "sun": "Sun",
    "moon": "Moon",
    "mercury": "Mercury",
    "venus": "Venus",
    "mars": "Mars",
    "jupiter": "Jupiter",
    "saturn": "Saturn",
    "uranus": "Uranus",
    "neptune": "Neptune",
    "pluto": "Pluto",
    "north node": "North Node",
    "true node": "North Node",
    "mean node": "North Node",
    "node": "North Node",
    "chiron": "Chiron",
}

POINT_ALIASES = {
    "asc": "ASC",
    "ascendant": "ASC",
    "dsc": "DSC",
    "descendant": "DSC",
    "mc": "MC",
    "midheaven": "MC",
    "ic": "IC",
    "imum coeli": "IC",
    "any": "ANY",
}

ASPECT_ALIASES = {
    "conj": "conjunction",
    "conjunction": "conjunction",
    "opp": "opposition",
    "opposition": "opposition",
    "square": "square",
    "trine": "trine",
    "sextile": "sextile",
}


def canon_body(value: str) -> str:
    key = (value or "").strip().lower()
    return BODY_ALIASES.get(key, (value or "").strip())


def canon_point(value: str) -> str:
    key = (value or "").strip().lower()
    return POINT_ALIASES.get(key, (value or "").strip())


def canon_aspect(value: str) -> str:
    key = (value or "").strip().lower()
    return ASPECT_ALIASES.get(key, key)


def canonical_key(body: str, aspect: str, point: str) -> str:
    body_key = canon_body(body).replace(" ", "_")
    point_key = canon_point(point).replace(" ", "_")
    return f"{body_key}.{canon_aspect(aspect)}.{point_key}"
