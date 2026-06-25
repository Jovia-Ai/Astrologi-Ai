"""Deterministic Free V1 placement-key plan builder (R4).

Consumes real normalized natal chart facts (structured planet/sign/house), not
text scanning. Emits an exact ordered plan: Sun, Moon, Mercury, Venus, Mars;
sign first, house second. No ranking, no fallback, no aspect replacement.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from .free_profile_plan_contracts import (
    DOMAIN_BY_PLANET,
    PLAN_VERSION,
    PLANET_ORDER,
    FreePlacementCard,
    FreePlacementPlan,
    PlanOmission,
)


def _index_planet_facts(planets: Sequence[Any]) -> dict[str, Mapping[str, Any]]:
    facts: dict[str, Mapping[str, Any]] = {}
    for item in planets or []:
        if not isinstance(item, Mapping):
            continue
        name = str(item.get("planet") or item.get("name") or "").strip().lower()
        if name in PLANET_ORDER and name not in facts:
            facts[name] = item  # first occurrence wins; deterministic
    return facts


def _sign_token(fact: Mapping[str, Any]) -> str | None:
    sign = str(fact.get("sign") or fact.get("zodiac_sign") or "").strip().lower()
    return sign or None


def _house_number(fact: Mapping[str, Any]) -> int | None:
    raw = fact.get("house")
    try:
        n = int(raw)
    except (TypeError, ValueError):
        return None
    return n if 1 <= n <= 12 else None


def build_free_placement_plan(planets: Sequence[Any]) -> FreePlacementPlan:
    facts = _index_planet_facts(planets)
    cards: list[FreePlacementCard] = []
    omissions: list[PlanOmission] = []
    seen_keys: set[str] = set()
    ordinal = 0
    for planet in PLANET_ORDER:
        domain = DOMAIN_BY_PLANET[planet]
        fact = facts.get(planet)
        if fact is None:
            omissions.append(PlanOmission(planet, "planet_sign", "PLANET_FACT_MISSING"))
            omissions.append(PlanOmission(planet, "planet_house", "PLANET_FACT_MISSING"))
            continue
        sign = _sign_token(fact)
        if sign is not None:
            key = f"{planet}_{sign}"
            if key in seen_keys:
                raise ValueError(f"duplicate primary key in plan: {key}")
            seen_keys.add(key)
            cards.append(FreePlacementCard(ordinal, planet, "planet_sign", key, domain))
            ordinal += 1
        else:
            omissions.append(PlanOmission(planet, "planet_sign", "SIGN_MISSING"))
        house = _house_number(fact)
        if house is not None:
            key = f"{planet}_house_{house}"
            if key in seen_keys:
                raise ValueError(f"duplicate primary key in plan: {key}")
            seen_keys.add(key)
            cards.append(FreePlacementCard(ordinal, planet, "planet_house", key, domain))
            ordinal += 1
        else:
            omissions.append(PlanOmission(planet, "planet_house", "HOUSE_MISSING"))
    return FreePlacementPlan(version=PLAN_VERSION, cards=tuple(cards), omissions=tuple(omissions))
