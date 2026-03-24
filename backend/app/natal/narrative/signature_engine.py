from __future__ import annotations

import hashlib
from collections import Counter
from typing import Any, Dict, List, Mapping, Sequence

from app.narrative.editorial_render_policy import semantic_overlap
from app.natal.narrative.primitive_engine import build_primitives
from app.natal.narrative.primitive_taxonomy_tr import TAXONOMY_V1_TR
from app.natal.narrative.signature_taxonomy_tr import BLOCK_ALIAS_TO_TAXONOMY


BLOCK_ORDER = [
    "identity_aura",
    "mind_voice",
    "drive_rhythm",
    "love_depth",
    "career_visibility",
    "home_roots",
    "luck_creation",
]

TAXONOMY_BY_BLOCK_ID_TR: Dict[str, Dict[str, Any]] = {
    str(block_id): dict(payload)
    for block_id, payload in TAXONOMY_V1_TR.items()
}

ANGLE_ALIASES = {
    "ASC": {"ASC", "Ascendant"},
    "MC": {"MC", "Midheaven"},
    "DSC": {"DSC", "Descendant"},
    "IC": {"IC", "Imum Coeli"},
}

BENEFICS = {"Jupiter", "Venus"}
PERSONAL_PLANETS = {"Sun", "Moon", "Mercury", "Venus", "Mars"}
POINTS = {"Ascendant", "Midheaven", "Descendant", "Imum Coeli", "Fortune", "Lilith", "Chiron", "Vertex"}

_SIGNATURE_PRIMITIVE_HINTS = {
    "identity_1st_stellium": ["self_definition", "visible_presence", "inner_structure"],
    "identity_uranus_angular": ["originality_drive", "self_definition"],
    "identity_jupiter_neptune_vision": ["big_picture_vision", "meaningful_expansion"],
    "identity_sun_angular": ["visible_presence", "self_definition"],
    "mind_saturn_3rd_boundary": ["tone_sensitivity", "inner_structure"],
    "mind_mercury_1st": ["mental_structuring", "systems_thinking"],
    "mind_mercury_rx_refine": ["mental_structuring", "systems_thinking"],
    "mind_sun_square_saturn_standard": ["inner_critic", "inner_structure"],
    "drive_mars_9th_method": ["methodical_drive", "meaningful_expansion"],
    "drive_mars_opp_saturn_push_pull": ["push_pull_drive", "inner_critic"],
    "drive_mars_trine_neptune_inspired_action": ["creative_synthesis", "meaningful_expansion"],
    "drive_saturn_sextile_uranus_structured_change": ["systems_thinking", "originality_drive"],
    "love_7th_ruler_in_8th": ["relational_security", "intimacy_depth"],
    "love_7th_ruler_in_11th_friends_to_love": ["relational_security", "network_luck"],
    "love_moon_in_8_intimacy_threshold": ["intimacy_depth", "emotional_threshold"],
}


def _safe_house(value: Any) -> int | None:
    try:
        ivalue = int(value)
    except (TypeError, ValueError):
        return None
    return ivalue if 1 <= ivalue <= 12 else None


def _norm_aspect(value: Any) -> str:
    return str(value or "").strip().lower()


def _planet_positions(chart: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    raw = chart.get("planets")
    out: Dict[str, Dict[str, Any]] = {}
    if isinstance(raw, Mapping):
        items = raw.items()
    elif isinstance(raw, list):
        items = ((item.get("planet"), item) for item in raw if isinstance(item, Mapping))
    else:
        items = ()
    for name, payload in items:
        if not isinstance(payload, Mapping):
            continue
        planet = str(name or payload.get("planet") or "").strip()
        if not planet:
            continue
        out[planet] = {
            "planet": planet,
            "sign": payload.get("sign"),
            "house": _safe_house(payload.get("house")),
            "degree": payload.get("longitude") if payload.get("longitude") is not None else payload.get("degree"),
            "retrograde": bool(payload.get("retrograde", False)),
        }
    return out


def _planet_positions_from_graph(natal_graph: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    raw = natal_graph.get("chart_planets")
    if not isinstance(raw, Mapping):
        raw = natal_graph.get("planets")
    out: Dict[str, Dict[str, Any]] = {}
    if not isinstance(raw, Mapping):
        return out
    for planet, payload in raw.items():
        if not isinstance(payload, Mapping):
            continue
        out[str(planet)] = {
            "planet": str(planet),
            "sign": payload.get("sign"),
            "house": _safe_house(payload.get("house")),
            "degree": payload.get("degree"),
            "retrograde": bool(payload.get("retrograde", False)),
        }
    return out


def _normalized_aspects(chart: Mapping[str, Any], natal_graph: Mapping[str, Any] | None = None) -> List[Dict[str, Any]]:
    raw = chart.get("aspects")
    if not isinstance(raw, list) and isinstance(natal_graph, Mapping):
        raw = natal_graph.get("chart_aspects")
    if not isinstance(raw, list) and isinstance(natal_graph, Mapping):
        raw = natal_graph.get("aspects")
    if not isinstance(raw, list):
        return []
    out: List[Dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, Mapping):
            continue
        p1 = str(item.get("planet1") or "").strip()
        p2 = str(item.get("planet2") or "").strip()
        aspect = str(item.get("aspect") or item.get("type") or "").strip()
        if not p1 or not p2 or not aspect:
            continue
        orb = item.get("orb")
        try:
            orb_value = float(orb) if orb is not None else None
        except (TypeError, ValueError):
            orb_value = None
        out.append({"planet1": p1, "planet2": p2, "type": aspect, "orb": orb_value})
    return out


def _angle_signs(chart: Mapping[str, Any], house_rulers: Mapping[str, Any]) -> Dict[str, str]:
    angles = chart.get("angles") if isinstance(chart.get("angles"), Mapping) else {}
    return {
        "ASC": str(angles.get("ascendant_sign") or (house_rulers.get("1") or {}).get("cusp_sign") or "").strip(),
        "MC": str(angles.get("midheaven_sign") or (house_rulers.get("10") or {}).get("cusp_sign") or "").strip(),
        "DSC": str((house_rulers.get("7") or {}).get("cusp_sign") or "").strip(),
        "IC": str((house_rulers.get("4") or {}).get("cusp_sign") or "").strip(),
    }


def _house_counts(planets: Mapping[str, Mapping[str, Any]]) -> Dict[int, int]:
    counts: Counter[int] = Counter()
    for planet, payload in planets.items():
        if planet in POINTS:
            continue
        house = _safe_house(payload.get("house"))
        if house is not None:
            counts[house] += 1
    return dict(counts)


def normalize_facts(chart: Mapping[str, Any], natal_graph: Mapping[str, Any]) -> Dict[str, Any]:
    planets = _planet_positions(chart) or _planet_positions_from_graph(natal_graph)
    house_rulers = natal_graph.get("house_rulers") if isinstance(natal_graph.get("house_rulers"), Mapping) else {}
    angle_signs = _angle_signs(chart, house_rulers)
    location = chart.get("location") if isinstance(chart.get("location"), Mapping) else {}
    seed = "|".join(
        [
            str(chart.get("birth_datetime") or "").strip(),
            str(location.get("city") or chart.get("birth_place") or "").strip(),
            angle_signs.get("ASC", ""),
            angle_signs.get("MC", ""),
        ]
    )
    return {
        "seed": seed,
        "chart": chart,
        "planets": planets,
        "aspects": _normalized_aspects(chart, natal_graph),
        "house_rulers": house_rulers,
        "house_counts": _house_counts(planets),
        "dominant_loops": natal_graph.get("dominant_loops") if isinstance(natal_graph.get("dominant_loops"), list) else [],
        "importance": natal_graph.get("importance") if isinstance(natal_graph.get("importance"), Mapping) else {},
        "angle_signs": angle_signs,
    }


def _is_angular_house(house: Any) -> bool:
    return _safe_house(house) in {1, 4, 7, 10}


def _planet_is_strong(planet: str, facts: Mapping[str, Any], max_orb: float = 6.0) -> bool:
    payload = (facts.get("planets") or {}).get(planet) or {}
    if _is_angular_house(payload.get("house")):
        return True
    for angle in ("ASC", "MC", "DSC", "IC"):
        if eval_rule("planet_near_angle", {"planet": planet, "angle": angle, "max_orb": max_orb}, facts):
            return True
    return False


def _placement_evidence(planet: str, facts: Mapping[str, Any]) -> Dict[str, Any]:
    payload = (facts.get("planets") or {}).get(planet, {})
    return {
        "type": "placement",
        "planet": planet,
        "sign": payload.get("sign"),
        "house": payload.get("house"),
        "degree": payload.get("degree"),
    }


def _house_ruler_evidence(house: int, facts: Mapping[str, Any]) -> Dict[str, Any]:
    payload = (facts.get("house_rulers") or {}).get(str(house), {})
    ruler_pos = payload.get("primary_ruler_pos") if isinstance(payload.get("primary_ruler_pos"), Mapping) else {}
    return {
        "type": "house_ruler",
        "house": house,
        "cusp_sign": payload.get("cusp_sign"),
        "ruler": payload.get("primary_ruler"),
        "ruler_sign": ruler_pos.get("sign"),
        "ruler_house": ruler_pos.get("house"),
    }


def _aspect_evidence(aspect: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "type": "aspect",
        "planet1": aspect.get("planet1"),
        "planet2": aspect.get("planet2"),
        "aspect": aspect.get("type"),
        "orb": aspect.get("orb"),
    }


def _angle_evidence(angle: str, facts: Mapping[str, Any]) -> Dict[str, Any]:
    return {"type": "angle", "angle": angle, "sign": (facts.get("angle_signs") or {}).get(angle)}


def _iter_aspects_for_pair(a: str, b: str, facts: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    out: List[Mapping[str, Any]] = []
    for aspect in facts.get("aspects") or []:
        pair = {aspect.get("planet1"), aspect.get("planet2")}
        if pair == {a, b}:
            out.append(aspect)
    return out


def _iter_angle_aspects(planet: str, angle: str, facts: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    angle_aliases = ANGLE_ALIASES.get(angle, {angle})
    out: List[Mapping[str, Any]] = []
    for aspect in facts.get("aspects") or []:
        pair = {aspect.get("planet1"), aspect.get("planet2")}
        if planet in pair and pair.intersection(angle_aliases):
            out.append(aspect)
    return out


def _find_aspect(a: str, b: str, types: Sequence[str] | None, max_orb: float | None, facts: Mapping[str, Any]) -> Mapping[str, Any] | None:
    allowed = {_norm_aspect(item) for item in (types or [])}
    for aspect in _iter_aspects_for_pair(a, b, facts):
        if allowed and _norm_aspect(aspect.get("type")) not in allowed:
            continue
        orb = aspect.get("orb")
        if max_orb is not None and orb is not None and float(orb) > max_orb:
            continue
        return aspect
    return None


def eval_rule(fn: str, args: Mapping[str, Any], facts: Mapping[str, Any]) -> Dict[str, Any] | None:
    planets = facts.get("planets") or {}
    house_rulers = facts.get("house_rulers") or {}

    if fn == "always":
        return {"matched": True, "evidence": [_angle_evidence("ASC", facts), _house_ruler_evidence(1, facts)]}

    if fn == "planet_in_house":
        planet = str(args.get("planet") or "").strip()
        house = _safe_house(args.get("house"))
        if (planets.get(planet) or {}).get("house") == house:
            return {"matched": True, "evidence": [_placement_evidence(planet, facts)]}
        return None

    if fn == "sun_in_house":
        return eval_rule("planet_in_house", {"planet": "Sun", **dict(args)}, facts)

    if fn == "moon_in_house":
        return eval_rule("planet_in_house", {"planet": "Moon", **dict(args)}, facts)

    if fn == "mars_in_house":
        return eval_rule("planet_in_house", {"planet": "Mars", **dict(args)}, facts)

    if fn == "saturn_in_house":
        return eval_rule("planet_in_house", {"planet": "Saturn", **dict(args)}, facts)

    if fn == "planet_retrograde":
        planet = str(args.get("planet") or "").strip()
        if (planets.get(planet) or {}).get("retrograde"):
            return {"matched": True, "evidence": [{"type": "retrograde", "planet": planet}]}
        return None

    if fn == "stellium_in_house":
        house = _safe_house(args.get("house"))
        min_count = int(args.get("min_count") or 3)
        count = int((facts.get("house_counts") or {}).get(house, 0))
        if house and count >= min_count:
            return {"matched": True, "evidence": [{"type": "stellium", "house": house, "count": count}]}
        return None

    if fn == "planet_near_angle":
        planet = str(args.get("planet") or "").strip()
        angle = str(args.get("angle") or "").strip()
        max_orb = float(args.get("max_orb") or 99.0)
        for aspect in _iter_angle_aspects(planet, angle, facts):
            if _norm_aspect(aspect.get("type")) != "conjunction":
                continue
            orb = aspect.get("orb")
            if orb is None or float(orb) <= max_orb:
                return {"matched": True, "evidence": [_aspect_evidence(aspect), _angle_evidence(angle, facts)]}
        if angle == "ASC" and (planets.get(planet) or {}).get("house") == 1 and max_orb >= 6.0:
            return {"matched": True, "evidence": [_placement_evidence(planet, facts), _angle_evidence(angle, facts)]}
        return None

    if fn == "either_near_angle":
        for planet in args.get("planets") or []:
            result = eval_rule("planet_near_angle", {"planet": planet, "angle": args.get("angle"), "max_orb": args.get("max_orb")}, facts)
            if result:
                return result
        return None

    if fn == "angle_ruler_in_house":
        angle = str(args.get("angle") or "").strip()
        target_house = _safe_house(args.get("target_house"))
        house = {"ASC": 1, "DSC": 7, "MC": 10, "IC": 4}.get(angle)
        payload = house_rulers.get(str(house)) if house else None
        if not isinstance(payload, Mapping):
            return None
        ruler_pos = payload.get("primary_ruler_pos") if isinstance(payload.get("primary_ruler_pos"), Mapping) else {}
        if ruler_pos.get("house") == target_house:
            return {"matched": True, "evidence": [_house_ruler_evidence(house or 0, facts)]}
        return None

    if fn == "house_ruler_in_house":
        house = _safe_house(args.get("house"))
        target_house = _safe_house(args.get("target_house"))
        payload = house_rulers.get(str(house)) if house else None
        if not isinstance(payload, Mapping):
            return None
        ruler_pos = payload.get("primary_ruler_pos") if isinstance(payload.get("primary_ruler_pos"), Mapping) else {}
        if ruler_pos.get("house") == target_house:
            return {"matched": True, "evidence": [_house_ruler_evidence(house or 0, facts)]}
        return None

    if fn == "aspect_between":
        a = str(args.get("a") or "").strip()
        b = str(args.get("b") or "").strip()
        max_orb = float(args.get("max_orb") or 99.0)
        aspect = _find_aspect(a, b, args.get("types") or [], max_orb, facts)
        if aspect:
            return {"matched": True, "evidence": [_aspect_evidence(aspect)]}
        return None

    if fn == "angle_aspected_by" or fn == "planet_aspect_angle":
        angle = str(args.get("angle") or "").strip()
        planet = str(args.get("planet") or "").strip()
        max_orb = float(args.get("max_orb") or 99.0)
        allowed = {_norm_aspect(item) for item in (args.get("types") or [])}
        for aspect in _iter_angle_aspects(planet, angle, facts):
            if allowed and _norm_aspect(aspect.get("type")) not in allowed:
                continue
            orb = aspect.get("orb")
            if orb is not None and float(orb) > max_orb:
                continue
            return {"matched": True, "evidence": [_aspect_evidence(aspect), _angle_evidence(angle, facts)]}
        return None

    if fn == "fortune_aspected_by_benefic":
        max_orb = float(args.get("max_orb") or 99.0)
        for benefic in BENEFICS:
            aspect = _find_aspect("Fortune", benefic, ["Trine", "Sextile", "Conjunction"], max_orb, facts)
            if aspect:
                return {"matched": True, "evidence": [_placement_evidence("Fortune", facts), _aspect_evidence(aspect)]}
        return None

    if fn == "dominance_house":
        house = _safe_house(args.get("house"))
        min_count = int(args.get("min_count") or 2)
        count = int((facts.get("house_counts") or {}).get(house, 0))
        if house and count >= min_count:
            return {"matched": True, "evidence": [{"type": "house_emphasis", "house": house, "count": count}]}
        return None

    if fn == "tight_orb_bonus":
        return eval_rule("planet_near_angle", args, facts)

    if fn == "tight_orb_aspect_bonus":
        return eval_rule("aspect_between", {"types": ["Trine", "Sextile", "Conjunction", "Square", "Opposition"], **dict(args)}, facts)

    if fn == "either_in_house":
        house = _safe_house(args.get("house"))
        for planet in args.get("planets") or []:
            if (planets.get(planet) or {}).get("house") == house:
                return {"matched": True, "evidence": [_placement_evidence(str(planet), facts)]}
        return None

    if fn == "either_angular":
        for planet in args.get("planets") or []:
            result = eval_rule("planet_near_angle", {"planet": planet, "angle": "ASC", "max_orb": args.get("max_orb", 6.0)}, facts)
            if result:
                return result
            house = (planets.get(str(planet)) or {}).get("house")
            if house in {1, 4, 7, 10}:
                return {"matched": True, "evidence": [_placement_evidence(str(planet), facts)]}
        return None

    if fn == "mercury_angular":
        result = eval_rule("planet_near_angle", {"planet": "Mercury", "angle": "ASC", "max_orb": args.get("max_orb", 6.0)}, facts)
        if result:
            return result
        if (planets.get("Mercury") or {}).get("house") in {1, 4, 7, 10}:
            return {"matched": True, "evidence": [_placement_evidence("Mercury", facts)]}
        return None

    if fn == "sun_aspect_dsc":
        for aspect_type in ("Conjunction", "Opposition", "Square", "Trine", "Sextile"):
            result = eval_rule(
                "planet_aspect_angle",
                {"planet": "Sun", "angle": "DSC", "types": [aspect_type], "max_orb": args.get("max_orb", 6.0)},
                facts,
            )
            if result:
                return result
        return None

    if fn == "mercury_aspects_personal":
        max_orb = float(args.get("max_orb") or 99.0)
        for planet in ("Sun", "Moon", "Venus", "Mars"):
            aspect = _find_aspect("Mercury", planet, ["Conjunction", "Trine", "Sextile", "Square", "Opposition"], max_orb, facts)
            if aspect:
                return {"matched": True, "evidence": [_aspect_evidence(aspect)]}
        return None

    if fn == "venus_strong":
        if _planet_is_strong("Venus", facts, float(args.get("max_orb") or 6.0)):
            return {"matched": True, "evidence": [_placement_evidence("Venus", facts)]}
        return None

    if fn == "moon_strong":
        if _planet_is_strong("Moon", facts, float(args.get("max_orb") or 6.0)):
            return {"matched": True, "evidence": [_placement_evidence("Moon", facts)]}
        return None

    if fn == "jupiter_strong":
        if _planet_is_strong("Jupiter", facts, float(args.get("max_orb") or 6.0)):
            return {"matched": True, "evidence": [_placement_evidence("Jupiter", facts)]}
        return None

    if fn == "saturn_strong":
        if _planet_is_strong("Saturn", facts, float(args.get("max_orb") or 6.0)):
            return {"matched": True, "evidence": [_placement_evidence("Saturn", facts)]}
        return None

    if fn == "pluto_strong":
        if _planet_is_strong("Pluto", facts, float(args.get("max_orb") or 6.0)):
            return {"matched": True, "evidence": [_placement_evidence("Pluto", facts)]}
        return None

    if fn == "mercury_strong":
        if _planet_is_strong("Mercury", facts, float(args.get("max_orb") or 6.0)):
            return {"matched": True, "evidence": [_placement_evidence("Mercury", facts)]}
        return None

    if fn == "angle_strong":
        angle = str(args.get("angle") or "").strip()
        if (facts.get("angle_signs") or {}).get(angle):
            return {"matched": True, "evidence": [_angle_evidence(angle, facts)]}
        return None

    if fn == "venus_or_sun_strong":
        for planet in ("Venus", "Sun"):
            if _planet_is_strong(planet, facts, float(args.get("max_orb") or 6.0)):
                return {"matched": True, "evidence": [_placement_evidence(planet, facts)]}
        return None

    if fn == "sun_or_venus_strong":
        return eval_rule("venus_or_sun_strong", args, facts)

    if fn == "saturn_or_moon_strong":
        for planet in ("Saturn", "Moon"):
            if _planet_is_strong(planet, facts, float(args.get("max_orb") or 6.0)):
                return {"matched": True, "evidence": [_placement_evidence(planet, facts)]}
        return None

    if fn == "neptune_or_venus_strong":
        for planet in ("Neptune", "Venus"):
            if _planet_is_strong(planet, facts, float(args.get("max_orb") or 6.0)):
                return {"matched": True, "evidence": [_placement_evidence(planet, facts)]}
        return None

    if fn == "saturn_hard_to_angle":
        for angle in ("ASC", "MC"):
            result = eval_rule(
                "planet_aspect_angle",
                {"planet": "Saturn", "angle": angle, "types": ["Square", "Opposition", "Conjunction"], "max_orb": args.get("max_orb", 2.0)},
                facts,
            )
            if result:
                return result
        return None

    if fn == "mars_strong_aspects":
        for target in ("Sun", "Moon", "Mercury", "Jupiter", "Neptune", "Uranus"):
            result = eval_rule("aspect_between", {"a": "Mars", "b": target, "types": args.get("types"), "max_orb": args.get("max_orb")}, facts)
            if result:
                return result
        return None

    if fn == "neptune_or_mars_angular":
        return eval_rule("either_angular", {"planets": ["Neptune", "Mars"], "max_orb": args.get("max_orb", 6.0)}, facts)

    if fn == "moon_aspects_personal":
        max_orb = float(args.get("max_orb") or 99.0)
        for planet in ("Sun", "Mercury", "Venus", "Mars"):
            aspect = _find_aspect("Moon", planet, ["Conjunction", "Trine", "Sextile", "Square", "Opposition"], max_orb, facts)
            if aspect:
                return {"matched": True, "evidence": [_aspect_evidence(aspect)]}
        return None

    if fn == "venus_aspects_neptune_or_moon":
        max_orb = float(args.get("max_orb") or 99.0)
        for planet in ("Neptune", "Moon"):
            aspect = _find_aspect("Venus", planet, ["Conjunction", "Trine", "Sextile", "Square", "Opposition"], max_orb, facts)
            if aspect:
                return {"matched": True, "evidence": [_aspect_evidence(aspect)]}
        return None

    if fn == "mc_sign_known":
        if (facts.get("angle_signs") or {}).get("MC"):
            return {"matched": True, "evidence": [_angle_evidence("MC", facts)]}
        return None

    if fn == "both_hits":
        angle = str(args.get("a") or "").strip()
        planets_list = list(args.get("b") or [])
        hits: List[Dict[str, Any]] = []
        for planet in planets_list:
            result = eval_rule(
                "angle_aspected_by",
                {"angle": angle, "planet": planet, "types": ["Square", "Opposition", "Conjunction"], "max_orb": 3.5},
                facts,
            )
            if result:
                hits.extend(result.get("evidence") or [])
        if len(hits) >= 2:
            return {"matched": True, "evidence": hits[:2]}
        return None

    if fn == "ic_sign_is":
        sign = str(args.get("sign") or "").strip().lower()
        if str((facts.get("angle_signs") or {}).get("IC") or "").strip().lower() == sign:
            return {"matched": True, "evidence": [_angle_evidence("IC", facts)]}
        return None

    if fn == "ic_ruler_is_mars":
        payload = house_rulers.get("4") if isinstance(house_rulers.get("4"), Mapping) else {}
        if payload.get("primary_ruler") == "Mars":
            return {"matched": True, "evidence": [_house_ruler_evidence(4, facts)]}
        return None

    if fn == "moon_aspect_ic":
        return eval_rule("planet_aspect_angle", {"planet": "Moon", "angle": "IC", "types": ["Conjunction"], "max_orb": args.get("max_orb", 5.0)}, facts)

    return None


def _score_candidate(signature: Mapping[str, Any], evidence: Sequence[Mapping[str, Any]], facts: Mapping[str, Any]) -> float:
    scoring = signature.get("scoring") if isinstance(signature.get("scoring"), Mapping) else {}
    score = float(scoring.get("base") or 0.0)
    for boost in scoring.get("boosts") or []:
        if not isinstance(boost, Mapping):
            continue
        if eval_rule(str(boost.get("fn") or ""), boost.get("args") if isinstance(boost.get("args"), Mapping) else {}, facts):
            score += float(boost.get("add") or 0.0)
    cap = float(scoring.get("cap") or 1.0)
    if evidence and len(evidence) >= 2:
        score += 0.01
    return round(min(score, cap), 4)


def eval_signature(signature: Mapping[str, Any], facts: Mapping[str, Any]) -> Dict[str, Any] | None:
    evidence: List[Dict[str, Any]] = []
    for rule in signature.get("rules") or []:
        if not isinstance(rule, Mapping):
            continue
        result = eval_rule(str(rule.get("fn") or ""), rule.get("args") if isinstance(rule.get("args"), Mapping) else {}, facts)
        if not result or not result.get("matched"):
            return None
        for item in result.get("evidence") or []:
            if isinstance(item, Mapping) and item not in evidence:
                evidence.append(dict(item))
    score = _score_candidate(signature, evidence, facts)
    return {
        "id": signature.get("id"),
        "signature_id": signature.get("id"),
        "spark": bool(signature.get("spark")),
        "block_affinity": list(signature.get("block_affinity") or []),
        "score": score,
        "evidence": evidence,
        "copy_tr": dict(signature.get("copy_tr") or {}),
        "chips": list(signature.get("chips") or []),
        "astro_tokens": list(signature.get("astro_tokens") or []),
        "primitive_ids": list(_SIGNATURE_PRIMITIVE_HINTS.get(str(signature.get("id") or ""), [])),
    }


def extract_candidates(facts: Mapping[str, Any], catalog: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for signature in catalog:
        candidate = eval_signature(signature, facts)
        if candidate:
            out.append(candidate)
    return out


def _tie_break(seed: str, block_id: str, signature_id: str) -> str:
    return hashlib.sha256(f"{seed}|{block_id}|{signature_id}".encode("utf-8")).hexdigest()


def _candidate_primitive_ids(candidate: Mapping[str, Any], taxonomy_block_id: str) -> list[str]:
    primitive_ids = [str(item) for item in candidate.get("primitive_ids") or [] if str(item).strip()]
    if primitive_ids:
        return primitive_ids
    fallback_by_taxonomy = {
        "identity_aura": ["self_definition", "inner_structure"],
        "inner_system": ["tone_sensitivity", "systems_thinking"],
        "talent_gifts": ["methodical_drive", "systems_thinking"],
        "love_depth": ["relational_security", "intimacy_depth"],
        "career_visibility": ["public_refinement", "visibility_sensitivity"],
        "home_roots": ["recharge_through_home", "family_self_reliance"],
        "luck_flow": ["creation_luck", "meaningful_expansion"],
    }
    return fallback_by_taxonomy.get(taxonomy_block_id, [])


def _slot_bonus(
    candidate: Mapping[str, Any],
    primitive_scores: Mapping[str, float],
    taxonomy: Mapping[str, Any],
    slot: str,
) -> float:
    priority = taxonomy.get("priority_order") if isinstance(taxonomy.get("priority_order"), Mapping) else {}
    wanted = [str(item) for item in priority.get(slot) or []]
    candidate_primitive_ids = _candidate_primitive_ids(candidate, str(taxonomy.get("block_id") or ""))
    score = 0.0
    for primitive_id in candidate_primitive_ids:
        if primitive_id in wanted:
            score += 0.16 + float(primitive_scores.get(primitive_id) or 0.0) * 0.18
        elif primitive_id in (taxonomy.get("primitive_clusters") or []):
            score += 0.08 + float(primitive_scores.get(primitive_id) or 0.0) * 0.12
    if slot == "spark" and candidate.get("spark"):
        score += 0.12
    if slot == "tone" and not candidate.get("spark"):
        score += 0.05
    return score


def _candidate_source_keys(candidate: Mapping[str, Any]) -> set[str]:
    keys: set[str] = set()
    for item in list(candidate.get("evidence") or []) + list(candidate.get("astro_tokens") or []):
        if not isinstance(item, Mapping):
            continue
        for name in ("planet", "planet1", "planet2", "ruler", "a", "b"):
            value = str(item.get(name) or "").strip()
            if value:
                keys.add(f"planet:{value}")
        for name in ("house", "ruler_house", "target_house"):
            value = item.get(name)
            if value is not None:
                keys.add(f"house:{value}")
        angle = str(item.get("angle") or "").strip()
        if angle:
            keys.add(f"angle:{angle}")
    return keys


def _candidate_surface_text(candidate: Mapping[str, Any]) -> str:
    copy_tr = candidate.get("copy_tr") if isinstance(candidate.get("copy_tr"), Mapping) else {}
    parts = [
        str(copy_tr.get("teaser") or "").strip(),
        str(copy_tr.get("core") or "").strip(),
        str(copy_tr.get("spark") or "").strip(),
    ]
    return " ".join(part for part in parts if part).strip()


def _diversity_penalty(
    candidate: Mapping[str, Any],
    *,
    selected_source_counts: Counter[str],
    selected_surfaces: Sequence[str],
    block: str,
) -> float:
    penalty = 0.0
    candidate_keys = _candidate_source_keys(candidate)
    if candidate_keys:
        for key in candidate_keys:
            reuse = selected_source_counts.get(key, 0)
            if reuse <= 0:
                continue
            if key.startswith("planet:"):
                penalty += 0.04 * min(reuse, 2)
            elif key.startswith("house:"):
                penalty += 0.03 * min(reuse, 2)
            else:
                penalty += 0.02 * min(reuse, 2)
    surface = _candidate_surface_text(candidate)
    if block != "identity_aura" and surface:
        for prior in selected_surfaces:
            overlap = semantic_overlap(surface, prior)
            if overlap >= 0.52:
                penalty += min(0.12, overlap * 0.14)
    return min(0.18, penalty)


def select_by_block(
    candidates: Sequence[Mapping[str, Any]],
    facts: Mapping[str, Any],
    primitive_hits: Sequence[Mapping[str, Any]] | None = None,
) -> Dict[str, Dict[str, Any]]:
    by_block: Dict[str, List[Mapping[str, Any]]] = {block: [] for block in BLOCK_ORDER}
    for candidate in candidates:
        for block in candidate.get("block_affinity") or []:
            if block in by_block:
                by_block[block].append(candidate)

    selected: Dict[str, Dict[str, Any]] = {}
    used_ids: set[str] = set()
    chip_counts: Counter[str] = Counter()
    selected_source_counts: Counter[str] = Counter()
    selected_surfaces: list[str] = []
    seed = str(facts.get("seed") or "")
    primitive_scores = {str(hit.get("primitive_id") or ""): float(hit.get("score") or 0.0) for hit in (primitive_hits or []) if isinstance(hit, Mapping)}

    for block in BLOCK_ORDER:
        taxonomy_block_id = BLOCK_ALIAS_TO_TAXONOMY.get(block, block)
        taxonomy = TAXONOMY_BY_BLOCK_ID_TR.get(taxonomy_block_id, {})
        ranked = sorted(
            by_block.get(block) or [],
            key=lambda item: (
                -float(item.get("score") or 0.0),
                -_slot_bonus(item, primitive_scores, taxonomy, "spine"),
                _tie_break(seed, block, str(item.get("signature_id") or "")),
            ),
        )

        def choose(slot: str, *, min_score: float = 0.0) -> Dict[str, Any] | None:
            best: Dict[str, Any] | None = None
            best_score = -999.0
            for candidate in ranked:
                signature_id = str(candidate.get("signature_id") or "")
                if signature_id in used_ids:
                    continue
                if float(candidate.get("score") or 0.0) < min_score:
                    continue
                if any(chip_counts.get(str(chip), 0) >= 2 for chip in candidate.get("chips") or []):
                    continue
                slot_score = float(candidate.get("score") or 0.0) + _slot_bonus(candidate, primitive_scores, taxonomy, slot)
                if slot == "spine" and "identity_" in signature_id and block != "identity_aura":
                    slot_score -= 0.05
                slot_score -= _diversity_penalty(
                    candidate,
                    selected_source_counts=selected_source_counts,
                    selected_surfaces=selected_surfaces,
                    block=block,
                )
                if slot_score > best_score:
                    best = dict(candidate)
                    best_score = slot_score
            if best is not None:
                used_ids.add(str(best.get("signature_id") or ""))
                for chip in best.get("chips") or []:
                    chip_counts[str(chip)] += 1
                for key in _candidate_source_keys(best):
                    selected_source_counts[key] += 1
                surface = _candidate_surface_text(best)
                if surface:
                    selected_surfaces.append(surface)
            return best

        spine = choose("spine")
        spark = choose("spark", min_score=0.45) if ranked else None
        area = choose("spine", min_score=0.35) if ranked else None
        tone = choose("tone", min_score=0.3) if ranked else None

        primary = spine or spark or area
        color = spark or area or tone
        if primary:
            selected[block] = {
                "primary": primary,
                "color": color,
                "spine_signature": spine,
                "spark_signature": spark,
                "area_signature": area,
                "tone_modifier": tone,
                "taxonomy_block_id": taxonomy_block_id,
            }

    return selected
