from __future__ import annotations

from typing import Any, Mapping

from app.natal.natal_context import NatalContext
from app.natal.natal_graph import build_natal_graph
from app.natal.natal_graph_v2 import build_natal_graph_v2
from app.natal.narrative.contradiction_engine import build_contradiction_signatures
from app.natal.narrative.master_selector import build_master_natal_selector
from app.natal.narrative.natal_feature_graph import build_natal_feature_graph
from app.natal.narrative.primitive_engine_v2 import build_primitives_v2

from .legacy_adapter import build_legacy_natal_bundle_from_chart
from .state_builder import build_canonical_natal_state_v1


def build_canonical_natal_state_from_chart_data(
    chart_data: Mapping[str, Any],
    *,
    metadata: Mapping[str, Any] | None = None,
    include_debug: bool = True,
) -> Any:
    natal_context = NatalContext.from_chart(dict(chart_data or {}))
    planets = natal_context.planets
    aspects = natal_context.aspects
    natal_graph = build_natal_graph(chart_data=chart_data, planets=planets, aspects=aspects)
    chart_for_selection = natal_context.chart_for_selection
    natal_graph_v2 = build_natal_graph_v2(chart_for_selection, natal_graph=natal_graph)
    natal_feature_graph = build_natal_feature_graph(
        chart_data=chart_for_selection,
        planets=planets,
        aspects=aspects,
        natal_graph=natal_graph,
        natal_graph_v2=natal_graph_v2,
    )
    primitive_scores = build_primitives_v2(
        chart_for_selection,
        natal_graph=natal_graph,
        natal_feature_graph=natal_feature_graph,
        natal_graph_v2=natal_graph_v2,
    )
    contradiction_signatures = build_contradiction_signatures(
        natal_feature_graph=natal_feature_graph,
        primitive_scores=primitive_scores,
    )
    master_selector = build_master_natal_selector(
        primitive_scores=primitive_scores,
        natal_feature_graph=natal_feature_graph,
        contradiction_signatures=contradiction_signatures,
    )
    legacy_bundle = build_legacy_natal_bundle_from_chart(
        chart_for_selection,
        metadata=metadata,
        natal_graph=natal_graph,
        natal_graph_v2=natal_graph_v2,
        feature_graph=natal_feature_graph,
        promise_vectors=(natal_graph_v2.get("promise_vectors") or {})
        if isinstance(natal_graph_v2, Mapping)
        else {},
        contradiction_signatures=contradiction_signatures,
        master_selector=master_selector,
    )
    return build_canonical_natal_state_v1(legacy_bundle, include_debug=include_debug)
