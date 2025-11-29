"""Transit scoring placeholder utilities."""
from __future__ import annotations

from typing import Dict, Mapping


def score_transits(natal_chart: Mapping[str, Dict[str, float]], transits: Mapping[str, float]) -> Dict[str, float]:
    """Return a placeholder response describing transit intensity."""
    if not natal_chart or not transits:
        return {"intensity": 0.0}
    return {"intensity": 0.5, "message": "Transit scoring is under construction."}
