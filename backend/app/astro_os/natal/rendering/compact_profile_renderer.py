from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ..contracts import CanonicalNatalStateV1, ChartSpineLine, ContradictionNode, NatalEvidence, NatalPromiseNode


CompactSlotKey = Literal[
    "opening",
    "core_pattern",
    "relationship_pattern",
    "work_visibility_pattern",
    "shadow_growth",
    "integration",
]


class CompactRenderSlot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slot: CompactSlotKey
    node_id: str
    title: str
    body: str
    evidence_refs: list[str] = Field(default_factory=list)
    linked_node_ids: list[str] = Field(default_factory=list)


class CompactProfileRender(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chart_id: str
    opening: CompactRenderSlot | None = None
    core_pattern: CompactRenderSlot | None = None
    relationship_pattern: CompactRenderSlot | None = None
    work_visibility_pattern: CompactRenderSlot | None = None
    shadow_growth: CompactRenderSlot | None = None
    integration: CompactRenderSlot | None = None
    filled_slots: list[CompactSlotKey] = Field(default_factory=list)


def _evidence_refs(evidence: list[NatalEvidence], *, limit: int = 2) -> list[str]:
    refs: list[str] = []
    for item in evidence:
        technical = str(item.technical).strip()
        if technical:
            refs.append(technical)
        if len(refs) >= limit:
            break
    return refs


def _promise_rank_value(centrality: str) -> int:
    return {"core": 0, "major": 1, "supporting": 2, "minor": 3}.get(str(centrality), 9)


def _contradiction_rank_value(centrality: str) -> int:
    return {"primary": 0, "secondary": 1, "minor": 2}.get(str(centrality), 9)


def _promise_body(node: NatalPromiseNode) -> str:
    return f"{node.psychological_pattern} {node.growth_path}"


def _contradiction_body(node: ContradictionNode) -> str:
    return f"{node.title.capitalize()}. {node.integration_path}"


def _slot_from_promise(slot: CompactSlotKey, node: NatalPromiseNode) -> CompactRenderSlot | None:
    if not node.id or not node.evidence:
        return None
    return CompactRenderSlot(
        slot=slot,
        node_id=node.id,
        title=node.theme,
        body=_promise_body(node),
        evidence_refs=_evidence_refs(node.evidence),
        linked_node_ids=[node.id, *node.linked_contradictions, *node.linked_character_patterns],
    )


def _slot_from_contradiction(
    slot: CompactSlotKey,
    node: ContradictionNode,
) -> CompactRenderSlot | None:
    if not node.id or not node.evidence:
        return None
    return CompactRenderSlot(
        slot=slot,
        node_id=node.id,
        title=node.title,
        body=_contradiction_body(node),
        evidence_refs=_evidence_refs(node.evidence),
        linked_node_ids=[node.id, *node.linked_promises],
    )


def _line_claimable(line: ChartSpineLine) -> bool:
    return bool(line.node_id and line.evidence)


def _choose_from_line(
    state: CanonicalNatalStateV1,
    line: ChartSpineLine,
    slot: CompactSlotKey,
) -> CompactRenderSlot | None:
    if not _line_claimable(line):
        return None
    if line.node_id.startswith("promise_"):
        for promise in state.core_promises:
            if promise.id == line.node_id:
                return _slot_from_promise(slot, promise)
    if line.node_id.startswith("contradiction_"):
        for contradiction in state.contradictions:
            if contradiction.id == line.node_id:
                return _slot_from_contradiction(slot, contradiction)
    return None


def _top_promise(
    state: CanonicalNatalStateV1,
    *,
    preferred_domains: set[str] | None = None,
    exclude_ids: set[str] | None = None,
) -> NatalPromiseNode | None:
    blocked = exclude_ids or set()
    candidates = [node for node in state.core_promises if node.evidence and node.id not in blocked]
    if preferred_domains:
        preferred = [node for node in candidates if node.domain in preferred_domains]
        if preferred:
            candidates = preferred
    if not candidates:
        return None
    return sorted(candidates, key=lambda node: (_promise_rank_value(node.centrality), node.id))[0]


def _top_contradiction(
    state: CanonicalNatalStateV1,
    *,
    exclude_ids: set[str] | None = None,
) -> ContradictionNode | None:
    blocked = exclude_ids or set()
    candidates = [node for node in state.contradictions if node.evidence and node.id not in blocked]
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda node: (_contradiction_rank_value(node.centrality), node.id),
    )[0]


def render_compact_profile(state: CanonicalNatalStateV1) -> CompactProfileRender:
    used_node_ids: set[str] = set()

    opening = _choose_from_line(state, state.chart_spine.primary_identity_line, "opening")
    if opening is None:
        opening_promise = _top_promise(
            state,
            preferred_domains={"identity", "emotional_security", "communication_learning"},
        )
        opening = _slot_from_promise("opening", opening_promise) if opening_promise is not None else None
    if opening is not None:
        used_node_ids.add(opening.node_id)

    core_pattern_promise = _top_promise(state, exclude_ids=used_node_ids)
    core_pattern = (
        _slot_from_promise("core_pattern", core_pattern_promise)
        if core_pattern_promise is not None
        else None
    )
    if core_pattern is not None:
        used_node_ids.add(core_pattern.node_id)

    relationship_pattern = _choose_from_line(state, state.chart_spine.relational_line, "relationship_pattern")
    if relationship_pattern is None:
        relationship_promise = _top_promise(
            state,
            preferred_domains={"relationship"},
            exclude_ids=used_node_ids,
        )
        relationship_pattern = (
            _slot_from_promise("relationship_pattern", relationship_promise)
            if relationship_promise is not None
            else None
        )
    if relationship_pattern is not None:
        used_node_ids.add(relationship_pattern.node_id)

    work_visibility_pattern = _choose_from_line(
        state,
        state.chart_spine.work_visibility_line,
        "work_visibility_pattern",
    )
    if work_visibility_pattern is None:
        work_promise = _top_promise(
            state,
            preferred_domains={"career_visibility"},
            exclude_ids=used_node_ids,
        )
        work_visibility_pattern = (
            _slot_from_promise("work_visibility_pattern", work_promise)
            if work_promise is not None
            else None
        )
    if work_visibility_pattern is not None:
        used_node_ids.add(work_visibility_pattern.node_id)

    shadow_growth = _choose_from_line(state, state.chart_spine.shadow_protection_line, "shadow_growth")
    if shadow_growth is None:
        contradiction = _top_contradiction(state, exclude_ids=used_node_ids)
        shadow_growth = (
            _slot_from_contradiction("shadow_growth", contradiction)
            if contradiction is not None
            else None
        )
    if shadow_growth is not None:
        used_node_ids.add(shadow_growth.node_id)

    integration = _choose_from_line(state, state.chart_spine.growth_integration_line, "integration")
    if integration is None:
        growth_promise = _top_promise(
            state,
            preferred_domains={"growth_shadow", "emotional_security", "spiritual_meaning"},
            exclude_ids=used_node_ids,
        )
        integration = (
            _slot_from_promise("integration", growth_promise)
            if growth_promise is not None
            else None
        )

    filled_slots: list[CompactSlotKey] = []
    for key, value in (
        ("opening", opening),
        ("core_pattern", core_pattern),
        ("relationship_pattern", relationship_pattern),
        ("work_visibility_pattern", work_visibility_pattern),
        ("shadow_growth", shadow_growth),
        ("integration", integration),
    ):
        if value is not None:
            filled_slots.append(key)

    return CompactProfileRender(
        chart_id=state.chart_id,
        opening=opening,
        core_pattern=core_pattern,
        relationship_pattern=relationship_pattern,
        work_visibility_pattern=work_visibility_pattern,
        shadow_growth=shadow_growth,
        integration=integration,
        filled_slots=filled_slots,
    )
