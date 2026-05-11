from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .contracts import ChartSpine, ChartSpineLine, ContradictionNode, NatalPromiseNode


@dataclass(frozen=True)
class ChartSpineReductionResult:
    chart_spine: ChartSpine
    suppressed: list[dict[str, Any]]


_SLOT_TO_CONTRACT_KEY = {
    "primary_identity_spine": "primary_identity_line",
    "secondary_balancing_line": "emotional_regulation_line",
    "relational_line": "relational_line",
    "work_visibility_line": "work_visibility_line",
    "shadow_protection_line": "shadow_protection_line",
}

_SLOT_TO_DOMAINS = {
    "primary_identity_spine": {"identity"},
    "secondary_balancing_line": {"emotional_security", "growth_shadow"},
    "relational_line": {"relationship"},
    "work_visibility_line": {"career_visibility"},
    "shadow_protection_line": {"growth_shadow", "emotional_security"},
}


def _promise_rank_value(centrality: str) -> int:
    return {"core": 0, "major": 1, "supporting": 2, "minor": 3}.get(str(centrality), 9)


def _find_backing_promise(slot: str, promises: list[NatalPromiseNode]) -> NatalPromiseNode | None:
    preferred_domains = _SLOT_TO_DOMAINS.get(slot, set())
    candidates = [promise for promise in promises if promise.domain in preferred_domains]
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda promise: (_promise_rank_value(promise.centrality), promise.id),
    )[0]


def _find_backing_contradiction(
    candidate: Mapping[str, Any],
    contradictions: list[ContradictionNode],
) -> ContradictionNode | None:
    wanted = {str(item).strip() for item in (candidate.get("contradiction_ids") or []) if str(item).strip()}
    if not wanted:
        return None
    by_suffix = {
        contradiction.id.removeprefix("contradiction_"): contradiction
        for contradiction in contradictions
    }
    for contradiction_id in wanted:
        contradiction = by_suffix.get(contradiction_id)
        if contradiction is not None:
            return contradiction
    return None


def reduce_chart_spine(
    master_selector: Mapping[str, Any] | None,
    *,
    promises: list[NatalPromiseNode],
    contradictions: list[ContradictionNode],
) -> ChartSpineReductionResult:
    payload = master_selector if isinstance(master_selector, Mapping) else {}
    spine = ChartSpine()
    suppressed: list[dict[str, Any]] = []

    for selector_slot, contract_key in _SLOT_TO_CONTRACT_KEY.items():
        candidate = payload.get(selector_slot)
        if not isinstance(candidate, Mapping):
            continue
        line: ChartSpineLine = getattr(spine, contract_key)
        line.source_candidates = [str(candidate.get("line_id") or "")] if str(candidate.get("line_id") or "").strip() else []

        backing_contradiction = _find_backing_contradiction(candidate, contradictions)
        if backing_contradiction is not None:
            line.node_id = backing_contradiction.id
            line.title = backing_contradiction.title
            line.summary = backing_contradiction.integration_path
            line.evidence = list(backing_contradiction.evidence)
            line.linked_node_ids = [backing_contradiction.id]
            continue

        backing_promise = _find_backing_promise(selector_slot, promises)
        if backing_promise is not None:
            line.node_id = backing_promise.id
            line.title = backing_promise.theme
            line.summary = backing_promise.growth_path
            line.evidence = list(backing_promise.evidence)
            line.linked_node_ids = [backing_promise.id]
            continue

        suppressed.append(
            {
                "candidate_id": str(candidate.get("line_id") or contract_key),
                "slot": selector_slot,
                "reason": "no_backing_promise_or_contradiction",
                "source": "master_selector",
            }
        )

    if not spine.growth_integration_line.node_id:
        growth_promise = _find_backing_promise("shadow_protection_line", promises) or _find_backing_promise(
            "secondary_balancing_line",
            promises,
        )
        if growth_promise is not None:
            spine.growth_integration_line.node_id = growth_promise.id
            spine.growth_integration_line.title = growth_promise.theme
            spine.growth_integration_line.summary = growth_promise.growth_path
            spine.growth_integration_line.evidence = list(growth_promise.evidence)
            spine.growth_integration_line.linked_node_ids = [growth_promise.id]

    return ChartSpineReductionResult(chart_spine=spine, suppressed=suppressed)
