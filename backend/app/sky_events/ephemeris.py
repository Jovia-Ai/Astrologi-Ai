from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from typing import Dict

import swisseph as swe

from app.core.config import settings


BODY_CODES = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
    "North Node": swe.TRUE_NODE,
}

SIGN_NAMES = (
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
)


@dataclass(frozen=True)
class BodyState:
    body: str
    longitude: float
    speed: float
    sign: str
    sign_index: int
    degree_in_sign: float
    retrograde: bool


def _ensure_ephe_path() -> None:
    try:
        swe.set_ephe_path(settings.swisseph_path)
    except Exception:
        return


def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def julian_day(value: datetime) -> float:
    dt = ensure_utc(value)
    ut = dt.hour + dt.minute / 60 + dt.second / 3600 + dt.microsecond / 3_600_000_000
    return swe.julday(dt.year, dt.month, dt.day, ut, swe.GREG_CAL)


def _normalize_degrees(value: float) -> float:
    return value % 360.0


def sign_name(longitude: float) -> str:
    index = int(_normalize_degrees(longitude) / 30.0)
    return SIGN_NAMES[index % 12]


def sign_index(longitude: float) -> int:
    return int(_normalize_degrees(longitude) / 30.0) % 12


def degree_in_sign(longitude: float) -> float:
    return _normalize_degrees(longitude) % 30.0


def angle_distance(lon_a: float, lon_b: float) -> float:
    diff = abs(_normalize_degrees(lon_a) - _normalize_degrees(lon_b)) % 360.0
    return diff if diff <= 180.0 else 360.0 - diff


@lru_cache(maxsize=32768)
def _calc_body_cached(body: str, minute_key: str) -> BodyState:
    _ensure_ephe_path()
    code = BODY_CODES[body]
    dt = datetime.fromisoformat(minute_key).replace(tzinfo=timezone.utc)
    values = swe.calc_ut(julian_day(dt), code)[0]
    longitude = float(values[0]) % 360.0
    speed = float(values[3]) if len(values) > 3 else 0.0
    return BodyState(
        body=body,
        longitude=longitude,
        speed=speed,
        sign=sign_name(longitude),
        sign_index=sign_index(longitude),
        degree_in_sign=degree_in_sign(longitude),
        retrograde=speed < 0,
    )


def body_state(body: str, value: datetime) -> BodyState:
    dt = ensure_utc(value).replace(second=0, microsecond=0)
    return _calc_body_cached(body, dt.isoformat())


def aspect_error(lon_a: float, lon_b: float, target_angle: int) -> float:
    return abs(angle_distance(lon_a, lon_b) - float(target_angle))
