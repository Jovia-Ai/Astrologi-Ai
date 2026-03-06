from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.models.chart_models import ChartBody, ChartMeta, NormalizedChart
from app.models.chart_request import ChartInputRef
from app.astro_core.aspects import compute_aspects
from app.astro_core.formatting import format_lon
from app.astro_core.math import midpoint_longitude
from app.charts.natal import build_natal


COMPOSITE_BODIES = [
    "sun",
    "moon",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
    "node",
    "chiron",
    "vertex",
    "fortune",
    "lilith",
]


def build_composite(
    a: ChartInputRef, b: ChartInputRef, tz: str, options: Optional[Dict[str, Any]] = None
) -> NormalizedChart:
    na = build_natal(a, tz=tz, options=options)
    nb = build_natal(b, tz=tz, options=options)

    a_map = {x.body: x for x in na.bodies}
    b_map = {x.body: x for x in nb.bodies}

    bodies: List[ChartBody] = []
    for body in COMPOSITE_BODIES:
        if body not in a_map or body not in b_map:
            continue
        lon = midpoint_longitude(a_map[body].longitude, b_map[body].longitude)
        sign, deg_in_sign, formatted = format_lon(lon)
        bodies.append(
            ChartBody(
                body=body,
                longitude=lon,
                sign=sign,
                deg_in_sign=deg_in_sign,
                formatted=formatted,
                house=None,
            )
        )

    aspects = compute_aspects(bodies=bodies, options=options)
    meta = ChartMeta(kind="composite", tz=tz, notes={"a": a.name, "b": b.name})
    return NormalizedChart(meta=meta, bodies=bodies, angles=[], houses=[], aspects=aspects, overlays=None)
