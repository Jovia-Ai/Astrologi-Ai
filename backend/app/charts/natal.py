from __future__ import annotations

from typing import Any, Dict, Optional

from app.models.chart_models import NormalizedChart
from app.models.chart_request import ChartInputRef
from app.charts._adapters.natal_adapter import compute_raw_natal, normalize_raw_natal
from app.astro_core.aspects import compute_aspects


def build_natal(a: ChartInputRef, tz: str, options: Optional[Dict[str, Any]] = None) -> NormalizedChart:
    raw = compute_raw_natal(a.data, tz=tz, options=options)
    chart = normalize_raw_natal(raw, tz=tz, name=a.name)
    aspects = compute_aspects(chart.bodies, options=options)
    return NormalizedChart(
        meta=chart.meta,
        bodies=chart.bodies,
        angles=chart.angles,
        houses=chart.houses,
        aspects=aspects,
        overlays=None,
    )
