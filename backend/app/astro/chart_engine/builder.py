"""Natal chart builder orchestrating location, houses, planets, and aspects."""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
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

_CITY_TOKEN_ALIASES = {
    "turkey": "tr",
    "turkiye": "tr",
    "türkiye": "tr",
}


@dataclass(slots=True)
class LocationData:
    latitude: float
    longitude: float
    timezone: str
    label: str


_LOCAL_LOCATION_FALLBACKS: Dict[str, LocationData] = {
    "istanbul": LocationData(41.0082, 28.9784, "Europe/Istanbul", "Istanbul, TR"),
    "istanbul tr": LocationData(41.0082, 28.9784, "Europe/Istanbul", "Istanbul, TR"),
    "ankara": LocationData(39.9334, 32.8597, "Europe/Istanbul", "Ankara, TR"),
    "ankara tr": LocationData(39.9334, 32.8597, "Europe/Istanbul", "Ankara, TR"),
    "izmir": LocationData(38.4237, 27.1428, "Europe/Istanbul", "Izmir, TR"),
    "izmir tr": LocationData(38.4237, 27.1428, "Europe/Istanbul", "Izmir, TR"),
    "sanliurfa": LocationData(37.1674, 38.7955, "Europe/Istanbul", "Sanliurfa, TR"),
    "sanliurfa tr": LocationData(37.1674, 38.7955, "Europe/Istanbul", "Sanliurfa, TR"),
    "sanliurfa turkey": LocationData(37.1674, 38.7955, "Europe/Istanbul", "Sanliurfa, TR"),
    "şanlıurfa": LocationData(37.1674, 38.7955, "Europe/Istanbul", "Sanliurfa, TR"),
    "şanlıurfa tr": LocationData(37.1674, 38.7955, "Europe/Istanbul", "Sanliurfa, TR"),
    "şanlıurfa turkey": LocationData(37.1674, 38.7955, "Europe/Istanbul", "Sanliurfa, TR"),
    "urfa": LocationData(37.1674, 38.7955, "Europe/Istanbul", "Sanliurfa, TR"),
    "urfa tr": LocationData(37.1674, 38.7955, "Europe/Istanbul", "Sanliurfa, TR"),
}


def _normalize_city_key(city: str) -> str:
    normalized = city.lower()
    for separator in (",", ";", "/", "|"):
        normalized = normalized.replace(separator, " ")
    tokens = [
        _CITY_TOKEN_ALIASES.get(token, token)
        for token in normalized.split()
    ]
    return " ".join(tokens)


def _fallback_location(city: str) -> LocationData | None:
    key = _normalize_city_key(city)
    return _LOCAL_LOCATION_FALLBACKS.get(key)


def _coerce_coordinate(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", ".")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _first_present(*values: Any) -> Any:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None


def _explicit_location(
    *,
    label: str,
    latitude: Any = None,
    longitude: Any = None,
    timezone: Any = None,
) -> LocationData | None:
    lat = _coerce_coordinate(latitude)
    lon = _coerce_coordinate(longitude)
    tz = str(timezone or "").strip()
    if lat is None or lon is None or not tz:
        return None
    resolved_label = label.strip() or "Known location"
    return LocationData(
        latitude=lat,
        longitude=lon,
        timezone=tz,
        label=resolved_label,
    )


def julian_day(utc_dt: datetime) -> float:
    ut = utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, ut, swe.GREG_CAL)


@lru_cache(maxsize=256)
def fetch_location(city: str) -> LocationData:
    if not city:
        raise ApiError("City is required for location lookup.")
    fallback = _fallback_location(city)
    if fallback:
        return fallback
    if not settings.opencage_api_key:
        raise ApiError("OPENCAGE_API_KEY not configured. Check your .env file.")
    params = {
        "q": city,
        "key": settings.opencage_api_key,
        "language": "tr",
        "limit": 1,
        "no_annotations": 0,
    }
    last_exc: Exception | None = None
    for attempt in range(3):
        try:
            response = requests.get(
                "https://api.opencagedata.com/geocode/v1/json",
                params=params,
                timeout=10,
            )
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
        except requests.RequestException as exc:
            last_exc = exc
            time.sleep(0.5 * (attempt + 1))

    raise ApiError("OpenCage request failed.") from last_exc


def resolve_location(
    city: str,
    *,
    latitude: Any = None,
    longitude: Any = None,
    timezone: Any = None,
) -> LocationData:
    explicit = _explicit_location(
        label=city,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
    )
    if explicit is not None:
        return explicit
    fallback = _fallback_location(city)
    if fallback is not None:
        return fallback
    return fetch_location(city)


def extract_birth_inputs(payload: Mapping[str, Any]) -> tuple[str, str, str] | tuple[str, str, None]:
    """Extract city and birth date/time components from request payload."""

    city_candidate = (
        payload.get("city")
        or payload.get("birth_place")
        or payload.get("birthPlace")
        or payload.get("place")
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
    location = resolve_location(
        city,
        latitude=_first_present(
            payload.get("birth_latitude"),
            payload.get("latitude"),
            payload.get("lat"),
        ),
        longitude=_first_present(
            payload.get("birth_longitude"),
            payload.get("longitude"),
            payload.get("lng"),
            payload.get("lon"),
        ),
        timezone=_first_present(
            payload.get("birth_timezone"),
            payload.get("timezone"),
            payload.get("tz"),
        ),
    )
    local_dt, utc_dt = parse_birth_datetime_components(date_value, time_value, location.timezone)
    jd_ut = julian_day(utc_dt)

    logger.warning(f"LOCAL DT (before conversion) = {local_dt} tzinfo={local_dt.tzinfo}")
    logger.warning(f"UTC DT (after conversion) = {utc_dt} tzinfo={utc_dt.tzinfo}")
    logger.warning(f"JD UT USED = {jd_ut}")

    try:
        swe.set_topo(location.longitude, location.latitude, 0.0)
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("Failed to set topocentric coordinates: %s", exc)

    house_list, angles = calc_houses(
        jd_ut,
        location.latitude,
        location.longitude,
        local_dt=local_dt,
        utc_dt=utc_dt,
    )
    cusp_sequence = [0.0, *house_list]

    planets: Dict[str, Dict[str, Any]] = calc_planets(
        jd_ut,
        cusp_sequence,
        angles=angles,
        local_dt=local_dt,
        utc_dt=utc_dt,
    )

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


def calculate_chart_from_birth_details(
    date_value: str,
    time_value: str,
    city_value: str,
    *,
    latitude: Any = None,
    longitude: Any = None,
    timezone: Any = None,
) -> Dict[str, Any]:
    """Utility used by interpretation endpoint when only birth inputs are provided."""

    payload = {
        "date": (date_value or "").strip(),
        "time": (time_value or "").strip(),
        "city": (city_value or "").strip(),
        "birth_latitude": latitude,
        "birth_longitude": longitude,
        "birth_timezone": timezone,
    }
    return build_natal_chart(payload)
