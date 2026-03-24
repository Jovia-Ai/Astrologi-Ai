from __future__ import annotations

from typing import Any, Dict, Mapping


HOUSE_DOMAIN_WEIGHTS: Dict[int, Dict[str, float]] = {
    1: {"identity": 0.28},
    2: {"home_roots": 0.06, "relationships": 0.04},
    3: {"mind_communication": 0.22, "meaning_learning": 0.08},
    4: {"home_roots": 0.34, "identity": 0.04},
    5: {"creativity_talent": 0.24, "relationships": 0.08},
    6: {"career_visibility": 0.04, "mind_communication": 0.08},
    7: {"relationships": 0.26, "identity": 0.06},
    8: {"intimacy_depth": 0.38, "relationships": 0.08},
    9: {"meaning_learning": 0.24, "mind_communication": 0.08},
    10: {"career_visibility": 0.22, "identity": 0.06},
    11: {"social_future": 0.18, "relationships": 0.10, "creativity_talent": 0.06},
    12: {"private_inner_world": 0.22, "home_roots": 0.10, "relationships": 0.05},
}

BODY_DOMAIN_HINTS: Dict[str, Dict[str, float]] = {
    "sun": {"identity": 0.10, "private_inner_world": 0.03},
    "moon": {"home_roots": 0.10, "relationships": 0.08, "intimacy_depth": 0.06, "private_inner_world": 0.04},
    "mercury": {"mind_communication": 0.10, "meaning_learning": 0.04, "private_inner_world": 0.06},
    "venus": {"relationships": 0.10, "creativity_talent": 0.08, "social_future": 0.04, "private_inner_world": 0.03},
    "mars": {"intimacy_depth": 0.06, "creativity_talent": 0.05, "meaning_learning": 0.04, "social_future": 0.03},
    "jupiter": {"meaning_learning": 0.10},
    "saturn": {"home_roots": 0.04, "mind_communication": 0.04},
    "uranus": {"identity": 0.06, "meaning_learning": 0.05, "creativity_talent": 0.04, "social_future": 0.03},
    "neptune": {"intimacy_depth": 0.04, "home_roots": 0.04, "creativity_talent": 0.05, "private_inner_world": 0.08},
    "pluto": {"intimacy_depth": 0.10, "relationships": 0.04},
    "juno": {"relationships": 0.12, "home_roots": 0.04, "social_future": 0.04},
    "node": {"meaning_learning": 0.06, "relationships": 0.04, "private_inner_world": 0.03, "social_future": 0.03},
    "vertex": {"relationships": 0.05, "intimacy_depth": 0.04},
    "chiron": {"career_visibility": 0.05, "relationships": 0.04},
    "lilith": {"intimacy_depth": 0.06, "identity": 0.04},
    "fortune": {"creativity_talent": 0.08, "meaning_learning": 0.04},
    "asc": {"identity": 0.08},
    "mc": {"career_visibility": 0.08},
}

ASPECT_ACTIVATION_BASE = {
    "conjunction": 0.24,
    "square": 0.22,
    "opposition": 0.22,
    "trine": 0.18,
    "sextile": 0.14,
}

ASPECT_MAX_ORBS = {
    "conjunction": 8.0,
    "square": 7.0,
    "opposition": 8.0,
    "trine": 7.0,
    "sextile": 5.0,
}


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _safe_house(value: Any) -> int | None:
    try:
        house = int(value)
    except (TypeError, ValueError):
        return None
    return house if 1 <= house <= 12 else None


def _merge_weighted(target: Dict[str, float], values: Mapping[str, float], scale: float = 1.0) -> None:
    for key, value in values.items():
        target[key] = target.get(key, 0.0) + (float(value) * scale)


def _body_key(value: Any) -> str:
    return str(value or "").strip().lower()


def _ordinal(value: Any) -> str:
    try:
        num = int(value)
    except (TypeError, ValueError):
        return str(value or "")
    if 10 <= (num % 100) <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(num % 10, "th")
    return f"{num}{suffix}"


def _aspect_tightness(hit: Mapping[str, Any] | None) -> float:
    if not isinstance(hit, Mapping):
        return 0.0
    aspect = _body_key(hit.get("aspect"))
    max_orb = ASPECT_MAX_ORBS.get(aspect, 6.0)
    try:
        orb = float(hit.get("orb_deg") if hit.get("orb_deg") is not None else hit.get("orb"))
    except (TypeError, ValueError):
        return 0.0
    return clamp01(1.0 - (orb / max_orb))


def overlay_domain_activation(overlay_house: int) -> Dict[str, float]:
    return dict(HOUSE_DOMAIN_WEIGHTS.get(int(overlay_house), {}))


def house_ruler_carryover(person_natal_graph_v2: Mapping[str, Any], activated_house: int) -> list[dict]:
    chart_rulers = person_natal_graph_v2.get("chart_rulers") if isinstance(person_natal_graph_v2, Mapping) else {}
    house_rulers = chart_rulers.get("house_rulers") if isinstance(chart_rulers, Mapping) else {}
    if not isinstance(house_rulers, Mapping):
        return []

    payload = house_rulers.get(str(activated_house))
    if not isinstance(payload, Mapping):
        return []
    placement = payload.get("placement")
    if not isinstance(placement, Mapping):
        return []

    ruler = str(payload.get("primary") or "")
    placed_house = _safe_house(placement.get("house"))
    if not ruler or placed_house is None:
        return []

    carry_domains = overlay_domain_activation(placed_house)
    if not carry_domains:
        return []
    carry_domains = {key: round(value * 0.35, 4) for key, value in carry_domains.items()}
    return [
        {
            "house": int(activated_house),
            "ruler": ruler,
            "placed_house": placed_house,
            "domains": carry_domains,
            "because": [f"{_ordinal(activated_house)} ruler {ruler} in {_ordinal(placed_house)}"],
        }
    ]


def synastry_hit_to_partner_activation(
    hit: Mapping[str, Any] | None,
    overlay_info: Mapping[str, Any] | None,
    natal_graph_v2: Mapping[str, Any],
) -> dict | None:
    overlay_info = overlay_info or {}
    incoming_body = _body_key(
        overlay_info.get("incoming_body") or overlay_info.get("body") or (hit or {}).get("incoming_body")
    )
    native_body = _body_key(overlay_info.get("native_body") or (hit or {}).get("native_body"))
    activated_house = _safe_house(overlay_info.get("in_house") or overlay_info.get("activated_house"))

    if not incoming_body and hit:
        incoming_body = _body_key(hit.get("b_body") or hit.get("a_body"))

    domains: Dict[str, float] = {}
    because: list[str] = []

    if activated_house is not None:
        _merge_weighted(domains, overlay_domain_activation(activated_house))
        because.append(f"{incoming_body or 'partner'} in {_ordinal(activated_house)}")
        for carryover in house_ruler_carryover(natal_graph_v2, activated_house):
            _merge_weighted(domains, carryover.get("domains") or {})
            because.extend(list(carryover.get("because") or []))

    if incoming_body:
        _merge_weighted(domains, BODY_DOMAIN_HINTS.get(incoming_body, {}), scale=0.35)
    if native_body:
        _merge_weighted(domains, BODY_DOMAIN_HINTS.get(native_body, {}), scale=0.20)

    source = "overlay"
    aspect = None
    orb_deg = None
    if isinstance(hit, Mapping):
        aspect = _body_key(hit.get("aspect"))
        orb_deg = hit.get("orb_deg") if hit.get("orb_deg") is not None else hit.get("orb")
        tightness = _aspect_tightness(hit)
        aspect_boost = ASPECT_ACTIVATION_BASE.get(aspect or "", 0.0) * tightness
        if aspect_boost > 0.0:
            if domains:
                for key in list(domains.keys()):
                    domains[key] += aspect_boost * 0.25
            if incoming_body:
                _merge_weighted(domains, BODY_DOMAIN_HINTS.get(incoming_body, {}), scale=aspect_boost * 0.45)
            if native_body:
                _merge_weighted(domains, BODY_DOMAIN_HINTS.get(native_body, {}), scale=aspect_boost * 0.30)
            because.append(
                f"{_body_key(hit.get('a_body'))}-{_body_key(hit.get('b_body'))} {aspect}"
            )
        source = "touchpoint" if activated_house is not None else "aspect"

    ranked_domains = sorted(
        (
            (key, round(clamp01(value), 4))
            for key, value in domains.items()
            if float(value) > 0.0
        ),
        key=lambda item: (-item[1], item[0]),
    )
    cleaned_domains = dict(ranked_domains[:2])
    if not cleaned_domains:
        return None

    return {
        "source": source,
        "incoming_body": incoming_body,
        "native_body": native_body or None,
        "activated_house": activated_house,
        "aspect": aspect,
        "orb_deg": float(orb_deg) if orb_deg is not None else None,
        "domains": cleaned_domains,
        "because": list(dict.fromkeys([item for item in because if item])),
    }
