from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .contracts import ContradictionNode, NatalEvidence
from .legacy_adapter import LegacyNatalReasoningBundle


@dataclass(frozen=True)
class ContradictionHierarchyResult:
    active: list[ContradictionNode]
    suppressed: list[dict[str, Any]]
    evidence_count: int


def _centrality_for(score: float) -> str:
    if score >= 0.70:
        return "primary"
    if score >= 0.52:
        return "secondary"
    return "minor"


def _humanized_summary(contradiction_id: str) -> str:
    mapping = {
        "visibility_vs_private_preparation": "Visibility and private readiness are both active, so being seen may require a preparation buffer.",
        "closeness_vs_threshold": "Closeness is wanted, but trust and emotional threshold regulate access to it.",
        "structure_vs_originality": "Originality and structure are both central, so expression may need form rather than collapse into spontaneity or control.",
        "composure_vs_internal_pressure": "External composure may coexist with significant inner pressure or self-regulation demands.",
        "speed_vs_control": "Action and control may compete, creating stop-start motion between urgency and restraint.",
    }
    return mapping.get(contradiction_id, contradiction_id.replace("_", " "))


def build_contradiction_hierarchy(
    bundle: LegacyNatalReasoningBundle,
) -> ContradictionHierarchyResult:
    payload = bundle.contradiction_signatures or {}
    signatures = payload.get("signatures") if isinstance(payload.get("signatures"), list) else []
    active: list[ContradictionNode] = []
    suppressed: list[dict[str, Any]] = []
    evidence_count = 0

    for signature in signatures:
        if not isinstance(signature, dict):
            continue
        contradiction_id = str(signature.get("id") or "").strip()
        score = float(signature.get("score") or 0.0)
        evidence_items = [str(item).strip() for item in (signature.get("evidence") or []) if str(item).strip()]
        if score < 0.38 or not contradiction_id or not evidence_items:
            suppressed.append(
                {
                    "candidate_id": f"contradiction_{contradiction_id or 'unknown'}",
                    "score": round(score, 4),
                    "reason": "insufficient_signal_or_missing_evidence",
                    "source": "contradiction_signatures",
                }
            )
            continue
        node_evidence = [
            NatalEvidence(
                id=f"{contradiction_id}_ev_{index + 1}",
                factor=item,
                technical=item,
                humanized=_humanized_summary(contradiction_id),
                layer="contradiction" if "vs" in contradiction_id else "motif",
                role="contradiction",
                source="contradiction_signatures.signatures",
                source_ref=f"contradiction_signatures.{contradiction_id}",
            )
            for index, item in enumerate(evidence_items)
        ]
        evidence_count += len(node_evidence)
        active.append(
            ContradictionNode(
                id=f"contradiction_{contradiction_id}",
                title=str(signature.get("editorial_label") or contradiction_id.replace("_", " ")),
                polarity_a=str(signature.get("left") or ""),
                polarity_b=str(signature.get("right") or ""),
                centrality=_centrality_for(score),
                evidence=node_evidence,
                integration_path=_humanized_summary(contradiction_id),
            )
        )

    return ContradictionHierarchyResult(
        active=active,
        suppressed=suppressed,
        evidence_count=evidence_count,
    )
