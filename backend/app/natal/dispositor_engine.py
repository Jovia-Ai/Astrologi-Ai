from __future__ import annotations

from typing import Any, Dict, Mapping


SIGN_RULERS: Dict[str, Dict[str, str | None]] = {
    "aries": {"primary": "Mars", "secondary": None},
    "taurus": {"primary": "Venus", "secondary": None},
    "gemini": {"primary": "Mercury", "secondary": None},
    "cancer": {"primary": "Moon", "secondary": None},
    "leo": {"primary": "Sun", "secondary": None},
    "virgo": {"primary": "Mercury", "secondary": None},
    "libra": {"primary": "Venus", "secondary": None},
    "scorpio": {"primary": "Mars", "secondary": "Pluto"},
    "sagittarius": {"primary": "Jupiter", "secondary": None},
    "capricorn": {"primary": "Saturn", "secondary": None},
    "aquarius": {"primary": "Saturn", "secondary": "Uranus"},
    "pisces": {"primary": "Jupiter", "secondary": "Neptune"},
}

SIGN_ORDER = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]

BODY_ALIASES = {
    "north node": "Node",
    "south node": "South Node",
    "node": "Node",
    "true node": "Node",
    "mean node": "Node",
    "fortune": "Fortune",
    "part of fortune": "Fortune",
    "asc": "Ascendant",
    "ascendant": "Ascendant",
    "mc": "Midheaven",
    "midheaven": "Midheaven",
    "dsc": "Descendant",
    "descendant": "Descendant",
    "ic": "IC",
    "imum coeli": "IC",
}


def _norm_sign(sign: Any) -> str:
    return str(sign or "").strip().lower()


def _title_sign(sign: Any) -> str | None:
    normalized = _norm_sign(sign)
    for item in SIGN_ORDER:
        if item.lower() == normalized:
            return item
    return None


def _safe_house(value: Any) -> int | None:
    try:
        ivalue = int(value)
    except (TypeError, ValueError):
        return None
    return ivalue if 1 <= ivalue <= 12 else None


def _canonical_body(name: Any) -> str:
    raw = str(name or "").strip()
    if not raw:
        return ""
    return BODY_ALIASES.get(raw.lower(), raw)


def _sign_from_longitude(value: Any) -> str | None:
    try:
        longitude = float(value)
    except (TypeError, ValueError):
        return None
    index = int(longitude % 360 // 30)
    return SIGN_ORDER[index]


def extract_planet_positions(
    chart: Mapping[str, Any],
    natal_graph: Mapping[str, Any] | None = None,
) -> Dict[str, Dict[str, Any]]:
    raw = chart.get("planets")
    out: Dict[str, Dict[str, Any]] = {}
    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, Mapping):
        items = [{**payload, "planet": key} for key, payload in raw.items() if isinstance(payload, Mapping)]
    else:
        items = []
    for item in items:
        if not isinstance(item, Mapping):
            continue
        planet = _canonical_body(item.get("planet") or item.get("body") or item.get("name"))
        if not planet:
            continue
        sign = _title_sign(item.get("sign")) or _sign_from_longitude(item.get("longitude")) or _sign_from_longitude(item.get("degree"))
        out[planet] = {
            "planet": planet,
            "sign": sign,
            "house": _safe_house(item.get("house")),
            "longitude": item.get("longitude"),
            "degree": item.get("degree"),
            "retrograde": bool(item.get("retrograde", False)),
        }
    if out:
        return out
    graph_planets = natal_graph.get("chart_planets") if isinstance(natal_graph, Mapping) else {}
    if isinstance(graph_planets, Mapping):
        for key, payload in graph_planets.items():
            if not isinstance(payload, Mapping):
                continue
            planet = _canonical_body(key)
            out[planet] = {
                "planet": planet,
                "sign": _title_sign(payload.get("sign")),
                "house": _safe_house(payload.get("house")),
                "longitude": payload.get("longitude"),
                "degree": payload.get("degree"),
                "retrograde": bool(payload.get("retrograde", False)),
            }
    return out


def extract_aspects(
    chart: Mapping[str, Any],
    natal_graph: Mapping[str, Any] | None = None,
) -> list[Dict[str, Any]]:
    raw = chart.get("aspects")
    if not isinstance(raw, list) and isinstance(natal_graph, Mapping):
        raw = natal_graph.get("chart_aspects")
    if not isinstance(raw, list):
        raw = []
    out: list[Dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, Mapping):
            continue
        planet1 = _canonical_body(item.get("planet1") or item.get("a_body") or item.get("a"))
        planet2 = _canonical_body(item.get("planet2") or item.get("b_body") or item.get("b"))
        aspect = str(item.get("aspect") or item.get("type") or "").strip().lower()
        try:
            orb = float(item.get("orb") if item.get("orb") is not None else item.get("orb_deg"))
        except (TypeError, ValueError):
            orb = None
        if not planet1 or not planet2 or not aspect:
            continue
        out.append({"planet1": planet1, "planet2": planet2, "aspect": aspect, "orb": orb})
    return out


def ruler_of_sign(sign: str) -> dict:
    payload = SIGN_RULERS.get(_norm_sign(sign), {"primary": None, "secondary": None})
    return {"primary": payload.get("primary"), "secondary": payload.get("secondary")}


def get_house_sign(chart: Mapping[str, Any], house_num: int) -> str | None:
    house_positions = chart.get("house_positions")
    if isinstance(house_positions, Mapping):
        payload = house_positions.get(str(house_num))
        if isinstance(payload, Mapping):
            sign = _title_sign(payload.get("sign"))
            if sign:
                return sign
    houses = chart.get("houses")
    if isinstance(houses, list):
        for item in houses:
            if not isinstance(item, Mapping):
                continue
            if _safe_house(item.get("house")) != house_num:
                continue
            sign = _title_sign(item.get("sign")) or _sign_from_longitude(item.get("longitude"))
            if sign:
                return sign
    return None


def build_house_ruler_map(
    chart: Mapping[str, Any],
    natal_graph: Mapping[str, Any] | None = None,
) -> dict:
    planets = extract_planet_positions(chart, natal_graph)
    out: Dict[str, Dict[str, Any]] = {}
    for house_num in range(1, 13):
        sign = get_house_sign(chart, house_num)
        rulers = ruler_of_sign(sign or "")
        primary = rulers.get("primary")
        secondary = rulers.get("secondary")
        out[str(house_num)] = {
            "sign": sign,
            "primary": primary,
            "secondary": secondary,
            "placement": dict(planets.get(str(primary) or "") or {}) if primary else None,
            "secondary_placement": dict(planets.get(str(secondary) or "") or {}) if secondary else None,
        }
    return out


def build_angle_ruler_map(
    chart: Mapping[str, Any],
    natal_graph: Mapping[str, Any] | None = None,
) -> dict:
    planets = extract_planet_positions(chart, natal_graph)
    angles = chart.get("angles") if isinstance(chart.get("angles"), Mapping) else {}
    asc_sign = _title_sign(angles.get("ascendant_sign") or angles.get("asc_sign")) or get_house_sign(chart, 1)
    mc_sign = _title_sign(angles.get("midheaven_sign") or angles.get("mc_sign")) or get_house_sign(chart, 10)
    asc_rulers = ruler_of_sign(asc_sign or "")
    mc_rulers = ruler_of_sign(mc_sign or "")
    return {
        "asc_sign": asc_sign,
        "asc_ruler_primary": asc_rulers.get("primary"),
        "asc_ruler_secondary": asc_rulers.get("secondary"),
        "asc_ruler_placement": dict(planets.get(str(asc_rulers.get("primary")) or "") or {})
        if asc_rulers.get("primary")
        else None,
        "mc_sign": mc_sign,
        "mc_ruler_primary": mc_rulers.get("primary"),
        "mc_ruler_secondary": mc_rulers.get("secondary"),
        "mc_ruler_placement": dict(planets.get(str(mc_rulers.get("primary")) or "") or {})
        if mc_rulers.get("primary")
        else None,
        "house_rulers": build_house_ruler_map(chart, natal_graph),
    }


def classical_dispositor(
    body: str,
    chart: Mapping[str, Any],
    natal_graph: Mapping[str, Any] | None = None,
) -> str | None:
    planets = extract_planet_positions(chart, natal_graph)
    payload = planets.get(_canonical_body(body))
    if not payload:
        return None
    return ruler_of_sign(str(payload.get("sign") or "")).get("primary")


def build_dispositor_chain(
    body: str,
    chart: Mapping[str, Any],
    max_hops: int = 6,
    natal_graph: Mapping[str, Any] | None = None,
) -> dict:
    planets = extract_planet_positions(chart, natal_graph)
    current = _canonical_body(body)
    payload = planets.get(current)
    if not payload:
        return {
            "start_sign": None,
            "primary_chain": [],
            "secondary_echoes": [],
            "terminated": True,
            "termination_reason": "missing_data",
        }

    start_sign = payload.get("sign")
    chain: list[str] = []
    secondary_echoes: list[str] = []
    visited: set[str] = set()
    reason = "max_hops"

    for _ in range(max_hops):
        current_payload = planets.get(current)
        if not current_payload or not current_payload.get("sign"):
            reason = "missing_data"
            break
        rulers = ruler_of_sign(str(current_payload.get("sign") or ""))
        next_body = str(rulers.get("primary") or "")
        secondary = str(rulers.get("secondary") or "")
        if secondary and secondary not in secondary_echoes:
            secondary_echoes.append(secondary)
        if not next_body:
            reason = "missing_data"
            break
        chain.append(next_body)
        if next_body in visited:
            reason = "loop_detected"
            break
        visited.add(next_body)
        next_payload = planets.get(next_body)
        if not next_payload or not next_payload.get("sign"):
            reason = "missing_data"
            break
        next_rulers = ruler_of_sign(str(next_payload.get("sign") or ""))
        if str(next_rulers.get("primary") or "") == next_body:
            reason = "domicile"
            break
        current = next_body
    else:
        reason = "max_hops"

    return {
        "start_sign": start_sign,
        "primary_chain": chain,
        "secondary_echoes": secondary_echoes,
        "terminated": True,
        "termination_reason": reason,
    }
