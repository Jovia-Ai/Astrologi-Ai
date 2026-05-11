from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ..contracts import CanonicalNatalStateV1
from .compact_profile_renderer import CompactRenderSlot, render_compact_profile


SectionKey = Literal[
    "core_architecture",
    "relationship_dynamics",
    "work_and_visibility",
    "shadow_and_growth",
]


class SectionRenderBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: SectionKey
    title: str
    body: str
    node_ids: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)


class SectionProfileRender(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chart_id: str
    sections: list[SectionRenderBlock] = Field(default_factory=list)


def _merge_evidence_refs(*slots: CompactRenderSlot | None) -> list[str]:
    seen: set[str] = set()
    merged: list[str] = []
    for slot in slots:
        if slot is None:
            continue
        for ref in slot.evidence_refs:
            item = str(ref).strip()
            if not item or item in seen:
                continue
            seen.add(item)
            merged.append(item)
    return merged


def _merge_node_ids(*slots: CompactRenderSlot | None) -> list[str]:
    seen: set[str] = set()
    merged: list[str] = []
    for slot in slots:
        if slot is None:
            continue
        for node_id in [slot.node_id, *slot.linked_node_ids]:
            item = str(node_id).strip()
            if not item or item in seen:
                continue
            seen.add(item)
            merged.append(item)
    return merged


def _build_body(*slots: CompactRenderSlot | None) -> str:
    parts: list[str] = []
    for slot in slots:
        if slot is None:
            continue
        parts.append(slot.body)
    return " ".join(parts).strip()


def render_section_profile(state: CanonicalNatalStateV1) -> SectionProfileRender:
    compact = render_compact_profile(state)
    sections: list[SectionRenderBlock] = []

    if compact.opening is not None or compact.core_pattern is not None:
        sections.append(
            SectionRenderBlock(
                key="core_architecture",
                title="Core architecture",
                body=_build_body(compact.opening, compact.core_pattern),
                node_ids=_merge_node_ids(compact.opening, compact.core_pattern),
                evidence_refs=_merge_evidence_refs(compact.opening, compact.core_pattern),
            )
        )

    if compact.relationship_pattern is not None:
        sections.append(
            SectionRenderBlock(
                key="relationship_dynamics",
                title="Relationship dynamics",
                body=_build_body(compact.relationship_pattern),
                node_ids=_merge_node_ids(compact.relationship_pattern),
                evidence_refs=_merge_evidence_refs(compact.relationship_pattern),
            )
        )

    if compact.work_visibility_pattern is not None:
        sections.append(
            SectionRenderBlock(
                key="work_and_visibility",
                title="Work and visibility",
                body=_build_body(compact.work_visibility_pattern),
                node_ids=_merge_node_ids(compact.work_visibility_pattern),
                evidence_refs=_merge_evidence_refs(compact.work_visibility_pattern),
            )
        )

    if compact.shadow_growth is not None or compact.integration is not None:
        sections.append(
            SectionRenderBlock(
                key="shadow_and_growth",
                title="Shadow and growth",
                body=_build_body(compact.shadow_growth, compact.integration),
                node_ids=_merge_node_ids(compact.shadow_growth, compact.integration),
                evidence_refs=_merge_evidence_refs(compact.shadow_growth, compact.integration),
            )
        )

    return SectionProfileRender(chart_id=state.chart_id, sections=sections)
