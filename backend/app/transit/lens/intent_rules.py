from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional


@dataclass(frozen=True)
class IntentWeights:
    w_venus: float = 0.0
    w_moon: float = 0.0
    w_jupiter: float = 0.0
    w_neptune: float = 0.0
    w_saturn: float = 0.0
    w_mercury: float = 0.0

    p_venus_retro: float = 0.0
    p_mars_retro: float = 0.0
    p_mercury_retro: float = 0.0
    p_eclipse: float = 0.0
    p_moon_voc: float = 0.0

    b_waxing: float = 0.0
    b_waning: float = 0.0

    density_cap: int = 3
    density_bonus: float = 0.02


INTENT_RULES: dict[str, IntentWeights] = {
    "beauty_care": IntentWeights(
        w_venus=0.20,
        w_moon=0.08,
        w_jupiter=0.06,
        w_neptune=0.03,
        p_venus_retro=0.35,
        p_mars_retro=0.25,
        p_mercury_retro=0.08,
        p_eclipse=0.20,
        p_moon_voc=0.18,
        b_waxing=0.06,
        b_waning=0.04,
        density_cap=2,
        density_bonus=0.015,
    ),
    "business_launch": IntentWeights(
        w_mercury=0.12,
        w_jupiter=0.10,
        w_saturn=0.06,
        p_mercury_retro=0.22,
        p_eclipse=0.25,
        p_moon_voc=0.18,
        density_cap=3,
        density_bonus=0.012,
    ),
    "contract_sign": IntentWeights(
        w_mercury=0.16,
        w_saturn=0.10,
        w_jupiter=0.06,
        p_mercury_retro=0.35,
        p_eclipse=0.30,
        p_moon_voc=0.20,
        density_cap=3,
        density_bonus=0.010,
    ),
}
