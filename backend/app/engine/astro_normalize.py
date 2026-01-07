from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


RULER_TRAD = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

ASPECT_TYPE_WEIGHTS = {
    "conjunction": 1.0,
    "opposition": 0.9,
    "square": 0.85,
    "trine": 0.7,
    "sextile": 0.55,
}

AXIS_POINTS = {
    "ascendant",
    "asc",
    "midheaven",
    "mc",
}

PERSONAL_BODIES = {"sun", "moon", "mercury", "venus", "mars"}
NODE_ALIASES = {"node", "true node", "mean node", "north node"}


def normalize_chart(
    chart_data: Mapping[str, Any],
    meta_info: Mapping[str, Any] | None = None,
) -> tuple[Dict[str, Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], Optional[str]]:
    meta_info = meta_info or {}
    placements_by_body: Dict[str, Dict[str, Any]] = {}
    aspects: List[Dict[str, Any]] = []
    house_cusps: List[Dict[str, Any]] = []

    raw_planets = chart_data.get("planets")
    if isinstance(raw_planets, list) and raw_planets:
        for entry in raw_planets:
            placement = _placement_from_structured(entry)
            if placement and placement["body"] not in placements_by_body:
                placements_by_body[placement["body"]] = placement
    elif chart_data.get("formatted_positions"):
        for line in chart_data.get("formatted_positions") or []:
            placement = _placement_from_formatted(line)
            if placement and placement["body"] not in placements_by_body:
                placements_by_body[placement["body"]] = placement

    raw_aspects = chart_data.get("aspects")
    if isinstance(raw_aspects, list) and raw_aspects:
        for entry in raw_aspects:
            aspect = _aspect_from_structured(entry)
            if aspect:
                aspects.append(aspect)
    elif chart_data.get("formatted_aspects"):
        for line in chart_data.get("formatted_aspects") or []:
            aspect = _aspect_from_formatted(line)
            if aspect:
                aspects.append(aspect)

    raw_houses = chart_data.get("houses")
    if isinstance(raw_houses, list) and raw_houses:
        for entry in raw_houses:
            cusp = _house_from_structured(entry)
            if cusp:
                house_cusps.append(cusp)
    elif chart_data.get("formatted_houses"):
        for line in chart_data.get("formatted_houses") or []:
            cusp = _house_from_formatted(line)
            if cusp:
                house_cusps.append(cusp)

    asc_sign = meta_info.get("ascendant_sign") or meta_info.get("asc_sign")
    if not house_cusps and asc_sign:
        house_cusps.append({"house": 1, "sign": str(asc_sign), "degree": 0.0})

    if not asc_sign:
        for cusp in house_cusps:
            if cusp.get("house") == 1:
                asc_sign = cusp.get("sign")
                break

    return placements_by_body, aspects, house_cusps, asc_sign


def canonical_body(raw: Any) -> Optional[str]:
    if not raw:
        return None
    name = str(raw).strip()
    lowered = name.lower()
    if lowered in NODE_ALIASES:
        return "North Node"
    aliases = {
        "asc": "Ascendant",
        "ascendant": "Ascendant",
        "mc": "Midheaven",
        "midheaven": "Midheaven",
        "ic": "Imum Coeli",
        "imum coeli": "Imum Coeli",
        "desc": "Descendant",
        "descendant": "Descendant",
    }
    if lowered in aliases:
        return aliases[lowered]
    return name


def normalize_aspect_type(value: Any) -> str:
    name = str(value or "").lower()
    aliases = {
        "conjunction": "conjunction",
        "conj": "conjunction",
        "opposition": "opposition",
        "opp": "opposition",
        "square": "square",
        "trine": "trine",
        "sextile": "sextile",
    }
    return aliases.get(name, name)


def orb_strength(orb: float, orb_max: float = 6.0) -> float:
    return clamp01(1.0 - min(orb / orb_max, 1.0))


def aspect_strength(aspect: Mapping[str, Any]) -> float:
    orb = aspect.get("orb")
    orb_value = float(orb) if isinstance(orb, (int, float)) else 6.0
    strength = orb_strength(orb_value) * ASPECT_TYPE_WEIGHTS.get(aspect.get("type"), 0.0)
    return clamp01(strength)


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _placement_from_structured(entry: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    body = canonical_body(entry.get("planet") or entry.get("body"))
    if not body:
        return None
    sign = entry.get("sign")
    house = entry.get("house")
    degree = entry.get("degree") or entry.get("longitude")
    retrograde = bool(entry.get("retrograde"))
    return {
        "body": body,
        "sign": str(sign) if sign else None,
        "house": int(house) if isinstance(house, (int, float)) else None,
        "degree": float(degree) if isinstance(degree, (int, float)) else None,
        "retrograde": retrograde,
    }


def _placement_from_formatted(line: str) -> Optional[Dict[str, Any]]:
    if not line:
        return None
    body_match = re.match(r"^(\w+(?:\s\w+)*)\s+in\s+", line, flags=re.IGNORECASE)
    sign_match = re.search(r"in\s+(\w+)\s+", line, flags=re.IGNORECASE)
    deg_match = re.search(r"(\d+)°(\d+)'", line)
    house_match = re.search(r"in\s+(\d+)(?:st|nd|rd|th)\s+House", line, flags=re.IGNORECASE)
    if not body_match or not sign_match:
        return None
    body = canonical_body(body_match.group(1).strip())
    sign = sign_match.group(1).strip()
    degree = _deg_from_match(deg_match)
    house = int(house_match.group(1)) if house_match else None
    retrograde = "retrograde" in line.lower()
    return {
        "body": body,
        "sign": sign,
        "house": house,
        "degree": degree,
        "retrograde": retrograde,
    }


def _aspect_from_structured(entry: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    a = canonical_body(entry.get("planet1") or entry.get("a"))
    b = canonical_body(entry.get("planet2") or entry.get("b"))
    aspect_type = normalize_aspect_type(entry.get("type") or entry.get("aspect"))
    if not a or not b or aspect_type not in ASPECT_TYPE_WEIGHTS:
        return None
    orb = entry.get("orb")
    if orb is None:
        orb = _orb_from_angles(entry)
    orb_value = float(orb) if isinstance(orb, (int, float)) else None
    return {"a": a, "b": b, "type": aspect_type, "orb": orb_value}


def _aspect_from_formatted(line: str) -> Optional[Dict[str, Any]]:
    if not line:
        return None
    pattern = re.compile(
        r"^(.+?)\s+(Conjunction|Opposition|Square|Trine|Sextile)\s+(.+?)\s+\(Orb:\s+(\d+)°(\d+)'\)$",
        flags=re.IGNORECASE,
    )
    match = pattern.match(line.strip())
    if not match:
        return None
    a = canonical_body(match.group(1).strip())
    b = canonical_body(match.group(3).strip())
    aspect_type = normalize_aspect_type(match.group(2))
    orb = _deg_from_match(match)
    if not a or not b or aspect_type not in ASPECT_TYPE_WEIGHTS:
        return None
    return {"a": a, "b": b, "type": aspect_type, "orb": orb}


def _house_from_structured(entry: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    house = entry.get("house") or entry.get("number")
    sign = entry.get("sign")
    degree = entry.get("degree")
    if not house or not sign:
        return None
    return {
        "house": int(house),
        "sign": str(sign),
        "degree": float(degree) if isinstance(degree, (int, float)) else None,
    }


def _house_from_formatted(line: str) -> Optional[Dict[str, Any]]:
    pattern = re.compile(r"^(\d+)(?:st|nd|rd|th)\s+House\s+in\s+(\w+)\s+(\d+)°(\d+)'$")
    match = pattern.match(line.strip())
    if not match:
        return None
    house = int(match.group(1))
    sign = match.group(2)
    degree = _deg_from_match(match)
    return {"house": house, "sign": sign, "degree": degree}


def _deg_from_match(match: Optional[re.Match]) -> Optional[float]:
    if not match:
        return None
    deg = int(match.group(match.lastindex - 1))
    minute = int(match.group(match.lastindex))
    return deg + minute / 60.0


def _orb_from_angles(entry: Mapping[str, Any]) -> Optional[float]:
    expected = entry.get("aspect_angle")
    exact = entry.get("exact_angle") or entry.get("angle")
    if isinstance(expected, (int, float)) and isinstance(exact, (int, float)):
        return abs(float(exact) - float(expected))
    return None
