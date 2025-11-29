"""Natal chart builder orchestrating location, houses, planets, and aspects."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Mapping

import requests
import swisseph as swe

from app.astro.chart_engine.aspects import calculate_chart_aspects
from app.astro.chart_engine.houses import calc_houses
from app.astro.chart_engine.positions import calc_planets, get_zodiac_sign, normalize_degrees
from app.core.config import settings
from app.core.errors import ApiError
from app.utils.timezones import parse_birth_datetime_components

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class LocationData:
    latitude: float
    longitude: float
    timezone: str
    label: str


def julian_day(utc_dt: datetime) -> float:
    ut = utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, ut, swe.GREG_CAL)


def fetch_location(city: str) -> LocationData:
    if not settings.opencage_api_key:
        raise ApiError("OPENCAGE_API_KEY not configured. Check your .env file.")
    params = {
        "q": city,
        "key": settings.opencage_api_key,
        "language": "tr",
        "limit": 1,
        "no_annotations": 0,
    }
    try:
        response = requests.get("https://api.opencagedata.com/geocode/v1/json", params=params, timeout=10)
    except requests.RequestException as exc:
        raise ApiError("OpenCage request failed.") from exc
    if response.status_code >= 400:
        raise ApiError(f"OpenCage request failed ({response.status_code}).")
    data = response.json()
    results = data.get("results", [])
    if not results:
        raise ApiError("City not found via OpenCage.")
    first = results[0]
    geometry = first.get("geometry", {})
    timezone_info = first.get("annotations", {}).get("timezone", {})
    timezone = timezone_info.get("name")
    if not timezone:
        raise ApiError("Timezone information missing from OpenCage response.")
    return LocationData(
        latitude=float(geometry.get("lat")),
        longitude=float(geometry.get("lng")),
        timezone=str(timezone),
        label=first.get("formatted") or city,
    )


def extract_birth_inputs(payload: Mapping[str, Any]) -> tuple[str, str, str] | tuple[str, str, None]:
    """Extract city and birth date/time components from request payload."""

    city_candidate = (
        payload.get("city")
        or payload.get("birthCity")
        or payload.get("birth_location")
        or payload.get("birthLocation")
        or payload.get("location")
    )
    if isinstance(city_candidate, Mapping):
        city_candidate = (
            city_candidate.get("name")
            or city_candidate.get("label")
            or city_candidate.get("city")
            or city_candidate.get("value")
        )
    city = str(city_candidate).strip() if city_candidate else ""

    date_value = (
        payload.get("birthDate")
        or payload.get("birth_date")
        or payload.get("date")
        or payload.get("dob")
    )
    if isinstance(date_value, Mapping):
        date_value = date_value.get("value") or date_value.get("date")

    time_value = payload.get("time") or payload.get("birthTime") or payload.get("birth_time")
    if isinstance(time_value, Mapping):
        time_value = time_value.get("value") or time_value.get("time")

    if not city:
        raise ValueError("city is required.")

    datetime_candidate = payload.get("birthDateTime") or payload.get("birth_datetime")
    if isinstance(datetime_candidate, Mapping):
        datetime_candidate = datetime_candidate.get("value") or datetime_candidate.get("datetime")

    if datetime_candidate:
        return city, str(datetime_candidate).strip(), None

    if not date_value:
        raise ValueError("birth date is required.")

    return city, str(date_value).strip(), str(time_value).strip() if time_value else None


def build_natal_chart(payload: Mapping[str, Any]) -> Dict[str, Any]:
    city, date_value, time_value = extract_birth_inputs(payload)

    location = fetch_location(city)
    local_dt, utc_dt = parse_birth_datetime_components(date_value, time_value, location.timezone)
    jd_ut = julian_day(utc_dt)

    try:
        swe.set_topo(location.longitude, location.latitude, 0.0)
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("Failed to set topocentric coordinates: %s", exc)

    house_list, angles = calc_houses(jd_ut, location.latitude, location.longitude)
    cusp_sequence = [0.0, *house_list]

    planets: Dict[str, Dict[str, Any]] = calc_planets(jd_ut, cusp_sequence, angles=angles)

    houses: Dict[str, Any] = {
        str(index + 1): round((value % 360), 4) for index, value in enumerate(house_list)
    }
    houses_detailed = {}
    for index, value in enumerate(house_list):
        lon = normalize_degrees(value) or 0.0
        degree_in_sign = lon % 30
        houses_detailed[str(index + 1)] = {
            "longitude": round(lon, 4),
            "sign": get_zodiac_sign(lon),
            "degree": int(degree_in_sign),
            "minute": int(round((degree_in_sign - int(degree_in_sign)) * 60)),
        }

    aspects = calculate_chart_aspects(planets, angles=angles)

    return {
        "location": {
            "city": location.label,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "timezone": location.timezone,
        },
        "birth_datetime": local_dt.isoformat(),
        "timezone": location.timezone,
        "planets": planets,
        "houses": houses,
        "house_positions": houses_detailed,
        "angles": angles,
        "aspects": aspects,
    }


def calculate_chart_from_birth_details(date_value: str, time_value: str, city_value: str) -> Dict[str, Any]:
    """Utility used by interpretation endpoint when only birth inputs are provided."""

    payload = {
        "date": (date_value or "").strip(),
        "time": (time_value or "").strip(),
        "city": (city_value or "").strip(),
    }
    return build_natal_chart(payload)
