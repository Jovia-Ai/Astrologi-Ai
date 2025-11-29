"""Planetary position helpers built on Swiss Ephemeris."""
from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, Mapping, Sequence

import swisseph as swe

logger = logging.getLogger(__name__)

SIGNS_TR = (
    "Koç",
    "Boğa",
    "İkizler",
    "Yengeç",
    "Aslan",
    "Başak",
    "Terazi",
    "Akrep",
    "Yay",
    "Oğlak",
    "Kova",
    "Balık",
)

PLANET_CODES = {
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
    "Lilith": getattr(swe, "MEAN_APOG", getattr(swe, "OSCU_APOG", swe.MEAN_NODE)),
    "Chiron": swe.CHIRON,
    "Vertex": swe.VERTEX,
}


def normalize_degrees(value: float | None) -> float | None:
    if value is None:
        return None
    return value % 360


def get_zodiac_sign(longitude: float | None) -> str | None:
    if longitude is None:
        return None
    index = int((longitude % 360) / 30)
    names = [
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
    ]
    return names[index % 12]


def determine_house(longitude: float, cusps: list[float]) -> int:
    lon = longitude % 360
    for idx in range(12):
        start = cusps[idx] % 360
        end = cusps[(idx + 1) % 12] % 360
        if start <= end:
            if start <= lon < end:
                return idx + 1
        else:
            if lon >= start or lon < end:
                return idx + 1
    return 12


def assign_houses(planets: Mapping[str, Dict[str, Any]], cusps: Iterable[float]) -> None:
    cusp_list = list(cusps)[:12]
    for planet_data in planets.values():
        longitude = planet_data["longitude"]
        planet_data["house"] = determine_house(longitude, cusp_list)


def calc_planets(
    jd_ut: float,
    cusps: Sequence[float] | None = None,
    *,
    angles: Mapping[str, Any] | None = None,
) -> Dict[str, Dict[str, Any]]:
    """Calculate planetary longitudes with safe unpacking and metadata."""

    planets: Dict[str, Dict[str, Any]] = {}
    cusp_sequence = list(cusps) if cusps is not None else None
    cusp_list = [float(cusp_sequence[i]) % 360 for i in range(1, min(len(cusp_sequence), 13))] if cusp_sequence else None

    def resolve_house(longitude: float) -> int | None:
        if not cusp_sequence or len(cusp_sequence) < 2:
            return None
        lon_val = longitude % 360
        for idx in range(1, min(len(cusp_sequence), 13)):
            start = cusp_sequence[idx] % 360
            end = cusp_sequence[1] % 360 if idx == 12 else cusp_sequence[idx + 1] % 360
            if start <= end:
                if start <= lon_val < end:
                    return idx
            else:
                if lon_val >= start or lon_val < end:
                    return idx
        return None

    for planet_name, planet_id in PLANET_CODES.items():
        try:
            result = swe.calc_ut(jd_ut, planet_id)
            values = result[0] if isinstance(result[0], (list, tuple)) else result

            lon = values[0] if len(values) > 0 else None
            lat = values[1] if len(values) > 1 else None
            dist = values[2] if len(values) > 2 else None
            speed = values[3] if len(values) > 3 else None

            lon_float = float(lon) if lon is not None else None
            lat_float = float(lat) if lat is not None else None
            dist_float = float(dist) if dist is not None else None
            speed_float = float(speed) if speed is not None else None

            house = resolve_house(lon_float) if lon_float is not None else None

            lon_norm = normalize_degrees(lon_float)
            degree_value = None
            minute_value = None
            if lon_norm is not None:
                degree_in_sign = lon_norm % 30
                degree_value = int(degree_in_sign)
                minute_value = int(round((degree_in_sign - degree_value) * 60))
                if minute_value == 60:
                    minute_value = 0
                    degree_value = (degree_value + 1) % 30

            planets[planet_name] = {
                "longitude": round(lon_norm, 2) if lon_norm is not None else None,
                "latitude": round(lat_float, 2) if lat_float is not None else None,
                "distance": round(dist_float, 4) if dist_float is not None else None,
                "speed": round(speed_float, 4) if speed_float is not None else None,
                "sign": get_zodiac_sign(lon_norm) if lon_norm is not None else None,
                "house": house,
                "retrograde": bool(speed_float is not None and speed_float < 0),
                "degree": degree_value,
                "minute": minute_value,
            }

            if planet_name == "Sun" and lon_float is not None:
                logger.info(
                    "☀️ Sun calculated successfully → lon=%.4f, lat=%s, dist=%s, speed=%s",
                    lon_float,
                    f"{lat_float:.4f}" if lat_float is not None else "None",
                    f"{dist_float:.4f}" if dist_float is not None else "None",
                    speed_float,
                )

        except Exception as exc:
            logger.warning("Failed to calculate %s: %s", planet_name, exc)

    if angles and cusp_list:
        try:
            asc = normalize_degrees(angles.get("ascendant"))
            sun_lon = normalize_degrees(planets.get("Sun", {}).get("longitude"))
            moon_lon = normalize_degrees(planets.get("Moon", {}).get("longitude"))
            sun_house = planets.get("Sun", {}).get("house")
            is_day_chart = bool(sun_house and 7 <= sun_house <= 12)
            if asc is not None and sun_lon is not None and moon_lon is not None:
                if is_day_chart:
                    fortune_lon = normalize_degrees(asc + moon_lon - sun_lon)
                else:
                    fortune_lon = normalize_degrees(asc - moon_lon + sun_lon)
                fortune_house = determine_house(fortune_lon, cusp_list) if fortune_lon is not None else None
                fortune_degree = fortune_lon % 30 if fortune_lon is not None else 0.0
                fortune_degree_whole = int(fortune_degree)
                fortune_minute = int(round((fortune_degree - fortune_degree_whole) * 60))
                if fortune_minute == 60:
                    fortune_minute = 0
                    fortune_degree_whole = (fortune_degree_whole + 1) % 30
                planets["Fortune"] = {
                    "longitude": round(fortune_lon or 0.0, 2),
                    "latitude": None,
                    "distance": None,
                    "speed": None,
                    "sign": get_zodiac_sign(fortune_lon),
                    "house": fortune_house,
                    "retrograde": False,
                    "degree": fortune_degree_whole,
                    "minute": fortune_minute,
                }
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to calculate Part of Fortune: %s", exc)

    return planets
