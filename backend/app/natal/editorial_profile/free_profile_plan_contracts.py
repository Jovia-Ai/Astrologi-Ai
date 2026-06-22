"""Deterministic Free V1 placement-key plan contracts (R4).

The natal placement fact itself is the semantic owner. No SHOU selection, no
salience, no ranking, no fallback. Fixed planet order and fixed domain map.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

PLAN_VERSION = "free_editorial_placement_plan_v1"

# Fixed order and fixed domain assignment (task section A/B).
PLANET_ORDER: Tuple[str, ...] = ("sun", "moon", "mercury", "venus", "mars")
DOMAIN_BY_PLANET = {
    "sun": "identity",
    "moon": "emotion",
    "mercury": "mind",
    "venus": "relationship",
    "mars": "action",
}
PLACEMENT_TYPES: Tuple[str, ...] = ("planet_sign", "planet_house")


@dataclass(frozen=True)
class FreePlacementCard:
    ordinal: int
    planet: str
    placement_type: str  # planet_sign | planet_house
    primary_key: str
    domain: str


@dataclass(frozen=True)
class PlanOmission:
    planet: str
    placement_type: str
    reason: str  # PLANET_FACT_MISSING | SIGN_MISSING | HOUSE_MISSING


@dataclass(frozen=True)
class FreePlacementPlan:
    version: str
    cards: Tuple[FreePlacementCard, ...]
    omissions: Tuple[PlanOmission, ...]
