"""Canonical natal core foundations."""

from .contracts import (
    AspectPatternNode,
    CanonicalNatalStateV1,
    CharacterPatternNode,
    ChartSpine,
    ChartSpineLine,
    ContradictionNode,
    DispositorRouteNode,
    HouseRulerRouteNode,
    NatalEvidence,
    NatalPromiseNode,
    PlanetConditionNode,
)
from .legacy_adapter import (
    LegacyNatalReasoningBundle,
    build_legacy_natal_bundle_from_base_payload,
    build_legacy_natal_bundle_from_chart,
)
from .chart_spine_reducer import ChartSpineReductionResult, reduce_chart_spine
from .contradiction_hierarchy import ContradictionHierarchyResult, build_contradiction_hierarchy
from .legacy_compare import compare_legacy_branches_to_canonical_state
from .meaning_graph import build_natal_meaning_graph
from .promise_hierarchy import PromiseHierarchyResult, build_promise_hierarchy
from .rendering import (
    CompactProfileRender,
    CompactRenderSlot,
    SectionProfileRender,
    SectionRenderBlock,
    render_compact_profile,
    render_section_profile,
)
from .runtime import build_canonical_natal_state_from_chart_data
from .state_builder import build_canonical_natal_state_v1

__all__ = [
    "AspectPatternNode",
    "CanonicalNatalStateV1",
    "CompactProfileRender",
    "CompactRenderSlot",
    "CharacterPatternNode",
    "ChartSpine",
    "ChartSpineLine",
    "ChartSpineReductionResult",
    "ContradictionNode",
    "ContradictionHierarchyResult",
    "DispositorRouteNode",
    "HouseRulerRouteNode",
    "LegacyNatalReasoningBundle",
    "NatalEvidence",
    "NatalPromiseNode",
    "PlanetConditionNode",
    "PromiseHierarchyResult",
    "SectionProfileRender",
    "SectionRenderBlock",
    "build_natal_meaning_graph",
    "build_canonical_natal_state_from_chart_data",
    "build_contradiction_hierarchy",
    "build_canonical_natal_state_v1",
    "build_legacy_natal_bundle_from_base_payload",
    "build_legacy_natal_bundle_from_chart",
    "build_promise_hierarchy",
    "compare_legacy_branches_to_canonical_state",
    "reduce_chart_spine",
    "render_compact_profile",
    "render_section_profile",
]
