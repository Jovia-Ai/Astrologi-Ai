from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Mapping, Optional, Tuple


TRADITIONAL_RULERS: Dict[str, str] = {
    "aries": "Mars",
    "taurus": "Venus",
    "gemini": "Mercury",
    "cancer": "Moon",
    "leo": "Sun",
    "virgo": "Mercury",
    "libra": "Venus",
    "scorpio": "Mars",
    "sagittarius": "Jupiter",
    "capricorn": "Saturn",
    "aquarius": "Saturn",
    "pisces": "Jupiter",
}

MODERN_CO_RULERS: Dict[str, str] = {
    "aquarius": "Uranus",
    "pisces": "Neptune",
    "scorpio": "Pluto",
}

MAJOR_ASPECTS = {"conjunction", "opposition", "square", "trine", "sextile"}


def _norm_sign(sign: Any) -> str:
    return str(sign or "").strip().lower()


def _safe_house(value: Any) -> Optional[int]:
    try:
        ivalue = int(value)
        return ivalue if 1 <= ivalue <= 12 else None
    except (TypeError, ValueError):
        return None


def _planet_positions(planets: List[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for p in planets:
        if not isinstance(p, Mapping):
            continue
        name = str(p.get("planet") or "").strip()
        if not name:
            continue
        out[name] = {
            "planet": name,
            "sign": p.get("sign"),
            "house": _safe_house(p.get("house")),
            "degree": p.get("degree"),
            "retrograde": bool(p.get("retrograde", False)),
        }
    return out


def _rulers_for_sign(sign: Any) -> Tuple[Optional[str], Optional[str]]:
    sign_key = _norm_sign(sign)
    primary = TRADITIONAL_RULERS.get(sign_key)
    co = MODERN_CO_RULERS.get(sign_key)
    return primary, co


def build_house_rulers(
    house_positions: Mapping[str, Any],
    planets_map: Mapping[str, Mapping[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for i in range(1, 13):
        house_key = str(i)
        raw = house_positions.get(house_key)
        if not isinstance(raw, Mapping):
            continue
        cusp_sign = raw.get("sign")
        primary, co = _rulers_for_sign(cusp_sign)
        out[house_key] = {
            "house": i,
            "cusp_sign": cusp_sign,
            "primary_ruler": primary,
            "co_ruler": co,
            "primary_ruler_pos": planets_map.get(primary) if primary else None,
            "co_ruler_pos": planets_map.get(co) if co else None,
        }
    return out


def build_dispositor_map(planets_map: Mapping[str, Mapping[str, Any]]) -> Dict[str, Dict[str, Optional[str]]]:
    out: Dict[str, Dict[str, Optional[str]]] = {}
    for planet, pos in planets_map.items():
        primary, secondary = _rulers_for_sign(pos.get("sign"))
        out[planet] = {"primary": primary, "secondary": secondary}
    return out


def _trace_chain(
    start: str,
    planets_map: Mapping[str, Mapping[str, Any]],
    dispositor_map: Mapping[str, Mapping[str, Optional[str]]],
    max_steps: int = 12,
) -> Dict[str, Any]:
    chain: List[Dict[str, Any]] = []
    visited_index: Dict[str, int] = {}
    current = start

    for idx in range(max_steps):
        if current in visited_index:
            loop_start = visited_index[current]
            loop = [entry["planet"] for entry in chain[loop_start:]]
            return {
                "start": start,
                "chain": chain,
                "loop": loop,
                "loop_start_index": loop_start,
            }

        pos = planets_map.get(current)
        disp = dispositor_map.get(current) or {}
        if not pos:
            break
        visited_index[current] = idx
        chain.append(
            {
                "planet": current,
                "sign": pos.get("sign"),
                "house": pos.get("house"),
                "primary_dispositor": disp.get("primary"),
                "secondary_dispositor": disp.get("secondary"),
            }
        )

        nxt = disp.get("primary")
        if not nxt or nxt not in planets_map:
            break
        current = nxt

    return {"start": start, "chain": chain, "loop": [], "loop_start_index": None}


def build_dispositor_chains(
    planets_map: Mapping[str, Mapping[str, Any]],
    dispositor_map: Mapping[str, Mapping[str, Optional[str]]],
) -> Tuple[Dict[str, Dict[str, Any]], List[Dict[str, Any]]]:
    chains = {planet: _trace_chain(planet, planets_map, dispositor_map) for planet in planets_map}
    loop_counts: Counter[str] = Counter()
    for payload in chains.values():
        loop = payload.get("loop") or []
        if loop:
            loop_counts["→".join(loop)] += 1

    dominant_loops = [
        {"signature": sig, "count": count, "planets": sig.split("→")}
        for sig, count in loop_counts.most_common()
    ]
    return chains, dominant_loops


def build_aspect_index(aspects: List[Mapping[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    index: Dict[str, List[Dict[str, Any]]] = {}
    for raw in aspects:
        if not isinstance(raw, Mapping):
            continue
        p1 = str(raw.get("planet1") or "").strip()
        p2 = str(raw.get("planet2") or "").strip()
        aspect = str(raw.get("aspect") or raw.get("type") or "").strip()
        orb = raw.get("orb")
        if not p1 or not p2 or not aspect:
            continue
        entry = {
            "planet1": p1,
            "planet2": p2,
            "aspect": aspect,
            "orb": orb,
            "major": aspect.strip().lower() in MAJOR_ASPECTS,
        }
        index.setdefault(p1, []).append(entry)
        index.setdefault(p2, []).append(entry)
    return index


def build_importance(
    planets_map: Mapping[str, Mapping[str, Any]],
    aspect_index: Mapping[str, List[Mapping[str, Any]]],
    house_rulers: Mapping[str, Mapping[str, Any]],
) -> Dict[str, float]:
    angle_rulers = {
        (house_rulers.get("1") or {}).get("primary_ruler"),
        (house_rulers.get("10") or {}).get("primary_ruler"),
    }
    angle_rulers.discard(None)
    scores: Dict[str, float] = {}
    for planet, pos in planets_map.items():
        house = _safe_house(pos.get("house"))
        angular_bonus = 0.2 if house in {1, 4, 7, 10} else 0.0
        ruler_bonus = 0.2 if planet in angle_rulers else 0.0
        aspect_count = len(aspect_index.get(planet) or [])
        aspect_bonus = min(0.2, aspect_count * 0.02)
        scores[planet] = round(min(1.0, 0.35 + angular_bonus + ruler_bonus + aspect_bonus), 4)
    return scores


def _compact_house_rulers(house_rulers: Mapping[str, Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
    compact: Dict[str, Dict[str, Any]] = {}
    for house_key, payload in house_rulers.items():
        if not isinstance(payload, Mapping):
            continue
        primary_pos = payload.get("primary_ruler_pos") if isinstance(payload.get("primary_ruler_pos"), Mapping) else {}
        co_pos = payload.get("co_ruler_pos") if isinstance(payload.get("co_ruler_pos"), Mapping) else {}
        compact[house_key] = {
            "cusp_sign": payload.get("cusp_sign"),
            "primary_ruler": payload.get("primary_ruler"),
            "primary_house": primary_pos.get("house"),
            "co_ruler": payload.get("co_ruler"),
            "co_house": co_pos.get("house"),
        }
    return compact


def build_natal_graph(
    *,
    chart_data: Mapping[str, Any],
    planets: List[Mapping[str, Any]],
    aspects: List[Mapping[str, Any]],
) -> Dict[str, Any]:
    house_positions = chart_data.get("house_positions")
    house_map = house_positions if isinstance(house_positions, Mapping) else {}

    planets_map = _planet_positions(planets)
    house_rulers = build_house_rulers(house_map, planets_map)
    dispositor_map = build_dispositor_map(planets_map)
    dispositor_chains, dominant_loops = build_dispositor_chains(planets_map, dispositor_map)
    aspect_index = build_aspect_index(aspects)
    importance = build_importance(planets_map, aspect_index, house_rulers)

    compact = {
        "house_rulers": _compact_house_rulers(house_rulers),
        "dominant_loops": dominant_loops[:3],
        "importance": importance,
    }
    return {
        "chart_planets": planets_map,
        "chart_aspects": aspects,
        "house_rulers": house_rulers,
        "dispositor_map": dispositor_map,
        "dispositor_chains": dispositor_chains,
        "dominant_loops": dominant_loops,
        "aspect_index": aspect_index,
        "importance": importance,
        "compact": compact,
    }
