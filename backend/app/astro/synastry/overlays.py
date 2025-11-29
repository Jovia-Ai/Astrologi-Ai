"""Placeholder for synastry overlay computations."""
from __future__ import annotations

from typing import Dict, Mapping


def build_overlay_summary(chart_a: Mapping[str, Mapping[str, float]], chart_b: Mapping[str, Mapping[str, float]]) -> Dict[str, float]:
    """Return a basic overlay metric placeholder."""
    score = 0.0
    planets = {"Sun", "Moon", "Venus", "Mars"}
    for name in planets:
        lon_a = chart_a.get(name, {}).get("longitude")
        lon_b = chart_b.get(name, {}).get("longitude")
        if isinstance(lon_a, (int, float)) and isinstance(lon_b, (int, float)):
            score += 1 - min(abs(lon_a - lon_b), 360 - abs(lon_a - lon_b)) / 180
    return {"compatibility_score": round(score / max(len(planets), 1), 3)}
