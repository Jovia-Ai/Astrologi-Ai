"""Helper for deriving strain/resilience scores from pressure/support signals."""
from __future__ import annotations

from typing import Any, Dict, Mapping


def build_strain_resilience(
    *,
    pressure_support: Mapping[str, Any] | None,
    meaning_weighting: Mapping[str, Any] | None,
    aspect_mechanics: Mapping[str, Mapping[str, Any]] | None = None,
) -> Dict[str, Dict[str, Any]]:
    pressure_support = pressure_support or {}
    meaning_weighting = meaning_weighting or {}
    aspect_mechanics = aspect_mechanics or {}

    pressure = _safe_float(
        pressure_support.get("pressure_index", meaning_weighting.get("pressure_index"))
    )
    support = _safe_float(
        pressure_support.get("support_index", meaning_weighting.get("support_index"))
    )

    strain_score = _min_max_normalize(pressure, 0.0, 1.0)
    resilience_score = _min_max_normalize(support, 0.0, 1.0)

    strain_drivers = _collect_drivers(
        aspect_mechanics,
        allowed_modes={"friction", "polarity", "blind_spot"},
    )
    resilience_drivers = _collect_drivers(
        aspect_mechanics,
        allowed_modes={"flow"},
    )

    return {
        "strain": {"score": strain_score, "drivers": strain_drivers},
        "resilience": {"score": resilience_score, "drivers": resilience_drivers},
    }


def _collect_drivers(
    aspect_mechanics: Mapping[str, Mapping[str, Any]],
    *,
    allowed_modes: set[str],
) -> list[str]:
    drivers = [
        aspect_id
        for aspect_id, meta in aspect_mechanics.items()
        if str(meta.get("energy_mode") or "") in allowed_modes
    ]
    return sorted(drivers)


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _min_max_normalize(value: float, minimum: float, maximum: float) -> float:
    if maximum <= minimum:
        return 0.0
    if value <= minimum:
        return 0.0
    if value >= maximum:
        return 1.0
    return (value - minimum) / (maximum - minimum)
