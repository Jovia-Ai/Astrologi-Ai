"""Synastry aspect utilities."""
from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence

from app.astro.chart_engine.aspects import ASPECT_DEFINITIONS, diff_angle


def calculate_synastry_aspects(
    planets_a: Mapping[str, Dict[str, Any]],
    planets_b: Mapping[str, Dict[str, Any]],
) -> list[Dict[str, Any]]:
    aspects: list[Dict[str, Any]] = []
    for name_a, data_a in planets_a.items():
        lon_a = data_a.get("longitude")
        if not isinstance(lon_a, (int, float)):
            continue
        for name_b, data_b in planets_b.items():
            lon_b = data_b.get("longitude")
            if not isinstance(lon_b, (int, float)):
                continue
            difference = diff_angle(float(lon_a), float(lon_b))
            for aspect_name, angle, orb in ASPECT_DEFINITIONS:
                if abs(difference - angle) <= orb:
                    aspects.append(
                        {
                            "planet1": name_a,
                            "planet2": name_b,
                            "aspect": aspect_name,
                            "orb": round(abs(difference - angle), 2),
                        }
                    )
                    break
    return aspects
