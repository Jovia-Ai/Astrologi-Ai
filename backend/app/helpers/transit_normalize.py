"""Transit normalization helpers."""
from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping

from app.astro.chart_engine.positions import determine_house, get_zodiac_sign, normalize_degrees


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def sign_degree(longitude: float | None) -> float | None:
    if longitude is None:
        return None
    return round(longitude % 30, 4)


def build_body_position(
    body: str,
    longitude: float | None,
    speed: float | None,
    cusps: Iterable[float] | None,
) -> Dict[str, Any]:
    lon = normalize_degrees(longitude) if longitude is not None else None
    house = determine_house(lon, list(cusps)) if lon is not None and cusps is not None else None
    return {
        "body": body,
        "lon": round(lon, 4) if lon is not None else None,
        "sign": get_zodiac_sign(lon) if lon is not None else None,
        "sign_deg": sign_degree(lon),
        "retrograde": bool(speed is not None and speed < 0),
        "speed": round(speed, 4) if speed is not None else None,
        "house": house,
    }


def build_angle_position(point: str, longitude: float | None) -> Dict[str, Any]:
    lon = normalize_degrees(longitude) if longitude is not None else None
    return {
        "point": point,
        "lon": round(lon, 4) if lon is not None else None,
        "sign": get_zodiac_sign(lon) if lon is not None else None,
        "sign_deg": sign_degree(lon),
    }


def build_house_cusps(cusps: Iterable[float]) -> list[Dict[str, Any]]:
    out: list[Dict[str, Any]] = []
    for idx, value in enumerate(list(cusps)[:12], start=1):
        lon = normalize_degrees(float(value))
        out.append(
            {
                "house": idx,
                "lon": round(lon, 4) if lon is not None else None,
                "sign": get_zodiac_sign(lon) if lon is not None else None,
                "sign_deg": sign_degree(lon),
            }
        )
    return out
