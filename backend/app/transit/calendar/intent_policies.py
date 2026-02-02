from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class IntentPolicy:
    include_any: List[str]
    exclude_any: List[str]
    weights: Dict[str, float]
    penalties: Dict[str, float]
    require_include_match: bool = True


INTENT_POLICIES: Dict[str, IntentPolicy] = {
    "beauty_care": IntentPolicy(
        include_any=[
            "venus",
            "moon_venus_soft",
            "moon_neptune_soft",
            "venus_neptune_soft",
        ],
        exclude_any=[
            "north_node",
            "south_node",
            "node",
            "fortune",
            "vertex",
            "chiron",
        ],
        weights={
            "venus": 1.0,
            "moon_venus_soft": 0.9,
            "moon_neptune_soft": 0.6,
            "venus_neptune_soft": 0.6,
            "moon_ingress": 0.10,
            "venus_ingress": 0.20,
            "moon_taurus": 0.15,
            "moon_libra": 0.15,
        },
        penalties={
            "moon_voc": -1.2,
            "moon_mars_hard": -0.9,
            "moon_saturn_hard": -0.8,
            "mars_venus_hard": -0.7,
            "venus_saturn_hard": -0.5,
            "moon_square": -0.2,
            "moon_opposition": -0.2,
        },
        require_include_match=True,
    ),
    "business": IntentPolicy(
        include_any=[
            "mercury",
            "jupiter",
            "mc",
            "career",
            "contract_support",
        ],
        exclude_any=[
            "moon_voc",
        ],
        weights={
            "mercury": 0.8,
            "jupiter": 0.6,
            "mc": 0.7,
            "career": 0.6,
            "contract_support": 1.0,
            "sun_mc_soft": 0.4,
            "mercury_jupiter_soft": 0.5,
            "mercury_saturn_soft": 0.6,
        },
        penalties={
            "mercury_retro": -1.0,
            "mercury_station": -0.6,
            "mercury_mars_hard": -0.7,
            "mercury_neptune_hard": -0.8,
            "mars_saturn_hard": -0.5,
        },
        require_include_match=True,
    ),
}


def get_intent_policy(intent: str) -> IntentPolicy:
    if intent not in INTENT_POLICIES:
        return IntentPolicy(
            include_any=[],
            exclude_any=[],
            weights={},
            penalties={},
            require_include_match=False,
        )
    return INTENT_POLICIES[intent]
