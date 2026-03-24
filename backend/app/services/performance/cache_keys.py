"""Centralized cache key generation for performance wrappers."""
from __future__ import annotations

import hashlib
from datetime import date as date_type

from .payload_versions import (
    GLOBAL_TRANSITS_VERSION,
    HOME_CONFIG_VERSION,
    HOME_DEEP_PAYLOAD_VERSION,
    HOME_FAST_PAYLOAD_VERSION,
)


def build_home_cache_config_hash() -> str:
    raw = "|".join(
        (
            f"home_config={HOME_CONFIG_VERSION}",
            f"home_fast={HOME_FAST_PAYLOAD_VERSION}",
            f"home_deep={HOME_DEEP_PAYLOAD_VERSION}",
            f"global_transits={GLOBAL_TRANSITS_VERSION}",
        )
    )
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]


def build_global_transits_key(*, day: date_type, tz: str) -> str:
    normalized_tz = (tz or "UTC").strip().replace("/", "_")
    return f"global_transits:{GLOBAL_TRANSITS_VERSION}:{normalized_tz}:{day.isoformat()}"


def build_home_fast_key(*, subject_key: str, day: date_type, config_hash: str | None = None) -> str:
    return f"home_fast:{HOME_FAST_PAYLOAD_VERSION}:{config_hash or build_home_cache_config_hash()}:{subject_key}:{day.isoformat()}"


def build_home_deep_key(*, subject_key: str, day: date_type, config_hash: str | None = None) -> str:
    return f"home_deep:{HOME_DEEP_PAYLOAD_VERSION}:{config_hash or build_home_cache_config_hash()}:{subject_key}:{day.isoformat()}"
