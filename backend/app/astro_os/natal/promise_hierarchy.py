from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .contracts import NatalEvidence, NatalPromiseNode
from .legacy_adapter import LegacyNatalReasoningBundle


@dataclass(frozen=True)
class _PromiseDefinition:
    domain: str
    theme: str
    psychological_pattern: str
    potential: str
    shadow: str
    growth_path: str


@dataclass(frozen=True)
class PromiseHierarchyResult:
    active: list[NatalPromiseNode]
    suppressed: list[dict[str, Any]]
    evidence_count: int


_PROMISE_DEFINITIONS: dict[str, _PromiseDefinition] = {
    "learn_clear_expression": _PromiseDefinition(
        domain="communication_learning",
        theme="clear expression under inner pressure",
        psychological_pattern="Thoughts may be filtered, refined, or delayed before they are expressed.",
        potential="Build a voice that is precise, credible, and emotionally intelligent.",
        shadow="Over-editing the self until real expression gets delayed.",
        growth_path="Move from protected thinking into iterative, visible expression.",
    ),
    "build_safe_intimacy": _PromiseDefinition(
        domain="relationship",
        theme="safe intimacy through trust and depth",
        psychological_pattern="Closeness may be approached through selective trust, testing, and emotional depth.",
        potential="Create relationships that can hold both vulnerability and loyalty.",
        shadow="Confusing emotional safety with permanent caution or withholding.",
        growth_path="Let trust build gradually without requiring perfect certainty first.",
    ),
    "integrate_vision_with_structure": _PromiseDefinition(
        domain="spiritual_meaning",
        theme="integrating vision with structure",
        psychological_pattern="Big insight or imagination may need disciplined scaffolding before it can become usable.",
        potential="Translate intuition, scale, and future-thinking into durable systems.",
        shadow="Swinging between over-idealism and over-control.",
        growth_path="Give large vision a repeatable structure instead of forcing one side to cancel the other.",
    ),
    "mature_visibility": _PromiseDefinition(
        domain="career_visibility",
        theme="maturing visibility and public presence",
        psychological_pattern="Being seen can carry both ambition and sensitivity, especially around readiness or legitimacy.",
        potential="Develop a public role that feels earned, embodied, and resilient.",
        shadow="Making visibility conditional on feeling fully prepared.",
        growth_path="Practice measured visibility before certainty feels complete.",
    ),
    "embody_originality": _PromiseDefinition(
        domain="identity",
        theme="embodying originality without fragmentation",
        psychological_pattern="Difference, independence, or unconventional instinct wants to become lived identity rather than scattered reaction.",
        potential="Live distinctiveness in a stable and self-owned way.",
        shadow="Performing difference without grounding it in identity.",
        growth_path="Let originality become embodied character instead of episodic disruption.",
    ),
    "turn_depth_into_wisdom": _PromiseDefinition(
        domain="growth_shadow",
        theme="turning depth into wisdom",
        psychological_pattern="Intense inner material asks to become meaning, perspective, and lived understanding.",
        potential="Convert emotional or existential intensity into wisdom that can guide life direction.",
        shadow="Staying inside depth without metabolizing it into perspective.",
        growth_path="Move from raw intensity toward insight, interpretation, and orientation.",
    ),
}


def _promise_scores(bundle: LegacyNatalReasoningBundle) -> dict[str, float]:
    if bundle.promise_vectors:
        return {
            str(key): float(value)
            for key, value in bundle.promise_vectors.items()
            if key in _PROMISE_DEFINITIONS
        }
    graph = bundle.natal_graph_v2 if isinstance(bundle.natal_graph_v2, Mapping) else {}
    promise_vectors = graph.get("promise_vectors") if isinstance(graph.get("promise_vectors"), Mapping) else {}
    return {
        str(key): float(value)
        for key, value in promise_vectors.items()
        if key in _PROMISE_DEFINITIONS
    }


def _vector_evidence(bundle: LegacyNatalReasoningBundle) -> dict[str, list[str]]:
    graph = bundle.natal_graph_v2 if isinstance(bundle.natal_graph_v2, Mapping) else {}
    debug = graph.get("debug") if isinstance(graph.get("debug"), Mapping) else {}
    evidence = debug.get("vector_evidence") if isinstance(debug.get("vector_evidence"), Mapping) else {}
    out: dict[str, list[str]] = {}
    for key, items in evidence.items():
        if key not in _PROMISE_DEFINITIONS or not isinstance(items, list):
            continue
        normalized = [str(item).strip() for item in items if str(item).strip()]
        out[str(key)] = normalized
    return out


def _infer_layer(technical: str) -> str:
    lowered = technical.lower()
    if "motif" in lowered:
        return "motif"
    if "ruler" in lowered:
        return "house_ruler"
    if "bridge" in lowered or "-" in technical:
        return "aspect"
    if " in " in lowered or "house" in lowered:
        return "placement"
    return "promise"


def _infer_role(technical: str) -> str:
    lowered = technical.lower()
    if "ruler" in lowered:
        return "governing_filter"
    if "motif" in lowered:
        return "support"
    if "bridge" in lowered:
        return "driver"
    if " in " in lowered or "house" in lowered:
        return "manifestation_channel"
    return "support"


def _humanize_evidence(technical: str, promise_key: str) -> str:
    mapping = {
        "learn_clear_expression": "This supports a life task around structured, visible, and emotionally filtered expression.",
        "build_safe_intimacy": "This supports a relationship path built through trust, depth, and emotional thresholds.",
        "integrate_vision_with_structure": "This supports joining large vision with durable form and discipline.",
        "mature_visibility": "This supports a growth path around being seen, recognized, and publicly embodied.",
        "embody_originality": "This supports living difference as stable identity rather than scattered reaction.",
        "turn_depth_into_wisdom": "This supports translating intensity into meaning, perspective, and guidance.",
    }
    return mapping.get(promise_key, technical)


def _centrality_for(score: float, evidence_count: int) -> str:
    if score >= 0.72 and evidence_count >= 2:
        return "core"
    if score >= 0.55:
        return "major"
    if score >= 0.35:
        return "supporting"
    return "minor"


def build_promise_hierarchy(
    bundle: LegacyNatalReasoningBundle,
) -> PromiseHierarchyResult:
    scores = _promise_scores(bundle)
    evidence_map = _vector_evidence(bundle)
    active: list[NatalPromiseNode] = []
    suppressed: list[dict[str, Any]] = []
    evidence_count = 0

    ranked = sorted(scores.items(), key=lambda item: (-float(item[1]), item[0]))
    for promise_key, score in ranked:
        definition = _PROMISE_DEFINITIONS.get(promise_key)
        if definition is None:
            continue
        technical_items = evidence_map.get(promise_key, [])
        filtered_items = [item for item in technical_items if not item.endswith("_fallback")]
        if score < 0.25 or not filtered_items:
            suppressed.append(
                {
                    "candidate_id": f"promise_{promise_key}",
                    "score": round(float(score), 4),
                    "reason": "insufficient_signal_or_missing_evidence",
                    "source": "natal_graph_v2.promise_vectors",
                }
            )
            continue
        node_evidence = [
            NatalEvidence(
                id=f"{promise_key}_ev_{index + 1}",
                factor=item,
                technical=item,
                humanized=_humanize_evidence(item, promise_key),
                layer=_infer_layer(item),
                role=_infer_role(item),
                source="natal_graph_v2.debug.vector_evidence",
                source_ref=f"promise_vectors.{promise_key}",
            )
            for index, item in enumerate(filtered_items)
        ]
        evidence_count += len(node_evidence)
        centrality = _centrality_for(float(score), len(node_evidence))
        active.append(
            NatalPromiseNode(
                id=f"promise_{promise_key}",
                domain=definition.domain,
                theme=definition.theme,
                centrality=centrality,
                stability="lifelong",
                evidence=node_evidence,
                psychological_pattern=definition.psychological_pattern,
                potential=definition.potential,
                shadow=definition.shadow,
                growth_path=definition.growth_path,
            )
        )

    return PromiseHierarchyResult(
        active=active,
        suppressed=suppressed,
        evidence_count=evidence_count,
    )
