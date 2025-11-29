"""House calculations."""
from __future__ import annotations

import logging
from typing import Dict, List, Tuple

import swisseph as swe

from app.astro.chart_engine.positions import get_zodiac_sign

logger = logging.getLogger(__name__)


def calc_houses(jd_ut: float, latitude: float, longitude: float) -> Tuple[List[float], Dict[str, float]]:
    """Calculate Placidus houses and ensure ASC–House 1 alignment."""

    raw_cusps, ascmc = swe.houses(jd_ut, latitude, longitude, b"P")
    houses = [float(raw_cusps[i]) % 360 for i in range(12)]
    angles = {
        "ascendant": round(ascmc[0] % 360, 4),
        "midheaven": round(ascmc[1] % 360, 4),
    }
    angles["ascendant_sign"] = get_zodiac_sign(angles["ascendant"])
    angles["midheaven_sign"] = get_zodiac_sign(angles["midheaven"])
    angles["descendant"] = round((angles["ascendant"] + 180) % 360, 4)
    angles["imum_coeli"] = round((angles["midheaven"] + 180) % 360, 4)
    angles["descendant_sign"] = get_zodiac_sign(angles["descendant"])
    angles["imum_coeli_sign"] = get_zodiac_sign(angles["imum_coeli"])

    delta = (angles["ascendant"] - houses[0]) % 360
    if delta:
        logger.debug("Aligning house cusps with ASC. Shift=%.4f°", delta)
        houses = [(h + delta) % 360 for h in houses]
    logger.info("ASC=%.4f°, House1=%.4f°", angles["ascendant"], houses[0])

    return houses, angles
