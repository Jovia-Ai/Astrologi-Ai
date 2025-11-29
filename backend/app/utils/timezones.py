"""Timezone parsing helpers for birth data."""
from __future__ import annotations

from datetime import datetime

import pytz


def parse_birth_datetime_components(date_value: str, time_value: str | None, timezone_name: str) -> tuple[datetime, datetime]:
    """Build a datetime from separate date/time fields and convert to UTC."""

    if not isinstance(date_value, str) or not date_value.strip():
        raise ValueError("birth date must be provided as string.")

    date_str = date_value.strip()
    try:
        year, month, day = [int(part) for part in date_str.split("-")]
    except ValueError as exc:
        raise ValueError("birth date must be in YYYY-MM-DD format.") from exc

    hour = 12
    minute = 0
    if time_value:
        try:
            hour_str, minute_str = time_value.strip().split(":", 1)
            hour = int(hour_str)
            minute = int(minute_str)
        except ValueError as exc:
            raise ValueError("birth time must be in HH:MM format.") from exc

    try:
        tz = pytz.timezone(timezone_name)
    except pytz.UnknownTimeZoneError as exc:
        raise ValueError(f"Unknown timezone '{timezone_name}'.") from exc

    local_naive = datetime(year, month, day, hour, minute)
    local_dt = tz.localize(local_naive)
    utc_dt = local_dt.astimezone(pytz.utc)
    return local_dt, utc_dt


def parse_birth_datetime(birth_str: str, timezone_name: str) -> tuple[datetime, datetime]:
    """Parse the provided datetime string and convert it using the location timezone."""

    if not isinstance(birth_str, str):
        raise ValueError("birth_date must be provided as string.")

    raw = birth_str.strip()
    if not raw:
        raise ValueError("birth_date is required.")

    parsed: datetime | None = None

    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        pass

    if parsed is None:
        normalized = raw.replace('T', ' ').rstrip('Z').strip()
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
            if _can_parse(normalized, fmt):
                parsed = datetime.strptime(normalized, fmt)
                break

    if parsed is None:
        raise ValueError("birth_date must match ISO format (YYYY-MM-DDTHH:MM) or 'YYYY-MM-DD HH:MM'.")

    try:
        tz = pytz.timezone(timezone_name)
    except pytz.UnknownTimeZoneError as exc:
        raise ValueError(f"Unknown timezone '{timezone_name}'.") from exc

    if parsed.tzinfo is not None:
        local_dt = parsed.astimezone(tz)
    else:
        local_dt = tz.localize(parsed)

    utc_dt = local_dt.astimezone(pytz.utc)
    return local_dt, utc_dt


def _can_parse(value: str, fmt: str) -> bool:
    try:
        datetime.strptime(value, fmt)
        return True
    except ValueError:
        return False
