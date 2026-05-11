from __future__ import annotations

from typing import Any

from .contracts import CanonicalDebugTrace, CanonicalNatalStateV1
from .chart_spine_reducer import reduce_chart_spine
from .contradiction_hierarchy import build_contradiction_hierarchy
from .legacy_adapter import LegacyNatalReasoningBundle
from .meaning_graph import build_natal_meaning_graph
from .promise_hierarchy import build_promise_hierarchy


def _source_trace_lists(source_trace: dict[str, str]) -> dict[str, list[str]]:
    normalized: dict[str, list[str]] = {}
    for key, value in source_trace.items():
        if not key or not value:
            continue
        normalized[str(key)] = [str(value)]
    return normalized


def build_canonical_natal_state_v1(
    bundle: LegacyNatalReasoningBundle,
    *,
    include_debug: bool = True,
    debug_overrides: dict[str, Any] | None = None,
) -> CanonicalNatalStateV1:
    promise_result = build_promise_hierarchy(bundle)
    contradiction_result = build_contradiction_hierarchy(bundle)
    spine_result = reduce_chart_spine(
        bundle.master_selector,
        promises=promise_result.active,
        contradictions=contradiction_result.active,
    )
    debug = None
    if include_debug:
        overrides = dict(debug_overrides or {})
        debug = CanonicalDebugTrace(
            legacy_sources_used=bundle.legacy_sources_used,
            source_trace=_source_trace_lists(bundle.source_trace),
            evidence_count=int(
                overrides.pop(
                    "evidence_count",
                    promise_result.evidence_count + contradiction_result.evidence_count,
                )
            ),
            suppressed_candidates=list(
                overrides.pop(
                    "suppressed_candidates",
                    [
                        *promise_result.suppressed,
                        *contradiction_result.suppressed,
                        *spine_result.suppressed,
                    ],
                )
            ),
            conflicting_evidence=list(
                overrides.pop(
                    "conflicting_evidence",
                    [
                        {
                            "node_id": contradiction.id,
                            "conflict": contradiction.title,
                            "resolution": "kept_as_contradiction",
                        }
                        for contradiction in contradiction_result.active
                        if contradiction.centrality in {"primary", "secondary"}
                    ],
                )
            ),
            fallback_used=bool(overrides.pop("fallback_used", False)),
            legacy_branch_overlap=list(overrides.pop("legacy_branch_overlap", [])),
            golden_expectation_misses=list(overrides.pop("golden_expectation_misses", [])),
        )
    state = CanonicalNatalStateV1(
        chart_id=bundle.chart_id,
        core_promises=promise_result.active,
        contradictions=contradiction_result.active,
        chart_spine=spine_result.chart_spine,
        debug=debug,
    )
    state.meaning_graph = build_natal_meaning_graph(state)
    return state
