"""House calculations."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Dict, List, Tuple

import swisseph as swe

from app.astro.chart_engine.positions import get_zodiac_sign
from app.core.config import settings

logger = logging.getLogger(__name__)

HOUSE_SYSTEM_VALUE = str(getattr(settings, "house_system", "P") or "P").strip().upper()
HOUSE_FLAG = HOUSE_SYSTEM_VALUE[:1].encode("ascii")


def calc_houses(
    jd_ut: float,
    latitude: float,
    longitude: float,
    *,
    local_dt: datetime | None = None,
    utc_dt: datetime | None = None,
) -> Tuple[List[float], Dict[str, float]]:
    """Calculate houses using the configured system."""

    if local_dt is not None or utc_dt is not None:
        if local_dt is not None:
            logger.warning(f"LOCAL DT (before conversion) = {local_dt} tzinfo={local_dt.tzinfo}")
        if utc_dt is not None:
            logger.warning(f"UTC DT (after conversion) = {utc_dt} tzinfo={utc_dt.tzinfo}")
        logger.warning(f"JD UT USED = {jd_ut}")
    else:
        logger.warning(f"JD UT = {jd_ut}")
    raw_cusps, ascmc = swe.houses(jd_ut, latitude, longitude, HOUSE_FLAG)
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
