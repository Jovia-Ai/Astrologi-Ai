from __future__ import annotations

from app.models.chart_models import NormalizedChart
from app.models.chart_request import ChartRequest

from app.charts.natal import build_natal
from app.charts.composite import build_composite


def build_chart(req: ChartRequest) -> NormalizedChart:
    kind = req.kind

    if kind == "natal":
        assert req.a is not None
        return build_natal(req.a, tz=req.tz, options=req.options)

    if kind == "composite":
        assert req.a is not None and req.b is not None
        return build_composite(req.a, req.b, tz=req.tz, options=req.options)

    # stubs for next steps (synastry/transit/progressions)
    raise ValueError(f"Unsupported chart kind (in this patch): {kind}")
