from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence

from .natal_selection_config import get_natal_selection_v3_config


_CONTRADICTION_BLUEPRINTS: Dict[str, Dict[str, Any]] = {
    "visibility_vs_private_preparation": {
        "family": "visibility_tension",
        "left_ids": ["visible_presence", "public_refinement", "creation_luck", "network_luck"],
        "right_ids": ["backstage_creation", "recharge_through_home", "family_self_reliance"],
        "editorial_label": "visible but privately prepared",
        "slot_biases": ["secondary_balancing_line", "work_visibility_line", "shadow_protection_line"],
        "feature_keys": ["public_private_split", "compensation_patterns"],
        "motif_hints": ["hidden_creation", "hidden_devotion", "creative_flow", "visibility_sensitivity"],
    },
    "closeness_vs_threshold": {
        "family": "relational_tension",
        "left_ids": ["intimacy_depth", "relational_security", "graceful_affection", "transformative_bonding"],
        "right_ids": ["emotional_threshold", "family_self_reliance", "tone_sensitivity"],
        "editorial_label": "closeness with a high trust threshold",
        "slot_biases": ["relational_line", "shadow_protection_line"],
        "feature_keys": ["public_private_split", "contradiction_polarity"],
        "motif_hints": ["depth_intimacy", "thresholded_intimacy", "selective_bonding", "depth_guardedness"],
    },
    "structure_vs_originality": {
        "family": "identity_tension",
        "left_ids": ["inner_structure", "mental_structuring", "systems_thinking", "methodical_drive"],
        "right_ids": ["originality_drive", "big_picture_vision", "visible_presence"],
        "editorial_label": "structured originality",
        "slot_biases": ["primary_identity_spine", "secondary_balancing_line"],
        "feature_keys": ["house_ruler_recursion", "compensation_patterns"],
        "motif_hints": ["identity_structure", "visionary_originality", "system_builder"],
    },
    "composure_vs_internal_pressure": {
        "family": "regulation_tension",
        "left_ids": ["inner_structure", "public_refinement", "visible_presence", "mental_structuring"],
        "right_ids": ["inner_critic", "tone_sensitivity", "push_pull_drive", "emotional_threshold"],
        "editorial_label": "composed outside, pressured inside",
        "slot_biases": ["secondary_balancing_line", "shadow_protection_line"],
        "feature_keys": ["public_private_split", "dispositor_chain_pressure"],
        "motif_hints": ["language_boundary", "visibility_sensitivity", "private_intellect"],
    },
    "speed_vs_control": {
        "family": "action_tension",
        "left_ids": ["push_pull_drive", "visible_presence", "originality_drive"],
        "right_ids": ["methodical_drive", "inner_structure", "mental_structuring"],
        "editorial_label": "speed pulled back by control",
        "slot_biases": ["secondary_balancing_line", "shadow_protection_line"],
        "feature_keys": ["dispositor_chain_pressure", "compensation_patterns"],
        "motif_hints": ["push_pull_drive", "system_builder", "language_boundary"],
    },
}


def _clamp01(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, number))


def _primitive_entries(primitive_scores: Mapping[str, Any] | None) -> Dict[str, Dict[str, Any]]:
    payload = primitive_scores if isinstance(primitive_scores, Mapping) else {}
    entries = payload.get("primitive_scores") if isinstance(payload.get("primitive_scores"), Sequence) else []
    return {
        str(item.get("primitive_id") or ""): dict(item)
        for item in entries
        if isinstance(item, Mapping) and str(item.get("primitive_id") or "").strip()
    }


def _feature_contradiction_map(natal_feature_graph: Mapping[str, Any] | None) -> Dict[str, Dict[str, Any]]:
    payload = natal_feature_graph if isinstance(natal_feature_graph, Mapping) else {}
    items = payload.get("contradiction_polarity") if isinstance(payload.get("contradiction_polarity"), Sequence) else []
    return {
        str(item.get("id") or ""): dict(item)
        for item in items
        if isinstance(item, Mapping) and str(item.get("id") or "").strip()
    }


def _feature_motif_scores(natal_feature_graph: Mapping[str, Any] | None) -> Dict[str, float]:
    payload = natal_feature_graph if isinstance(natal_feature_graph, Mapping) else {}
    dominant = ((payload.get("repeated_motif_count") or {}).get("dominant_motifs")) if isinstance(payload.get("repeated_motif_count"), Mapping) else []
    return {
        str(item.get("id") or ""): float(item.get("score") or 0.0)
        for item in dominant or []
        if isinstance(item, Mapping) and str(item.get("id") or "").strip()
    }


def _feature_compensation_map(natal_feature_graph: Mapping[str, Any] | None) -> Dict[str, float]:
    payload = natal_feature_graph if isinstance(natal_feature_graph, Mapping) else {}
    items = payload.get("compensation_patterns") if isinstance(payload.get("compensation_patterns"), Sequence) else []
    return {
        str(item.get("id") or ""): float(item.get("score") or 0.0)
        for item in items
        if isinstance(item, Mapping) and str(item.get("id") or "").strip()
    }


def _best_primitive(entries: Mapping[str, Mapping[str, Any]], primitive_ids: Sequence[str]) -> tuple[Dict[str, Any], float]:
    best: Dict[str, Any] = {}
    best_score = 0.0
    for primitive_id in primitive_ids:
        entry = entries.get(str(primitive_id))
        if not isinstance(entry, Mapping):
            continue
        score = float(entry.get("score") or 0.0)
        if score > best_score:
            best = dict(entry)
            best_score = score
    return best, round(best_score, 4)


def _priority_for_score(score: float) -> str:
    if score >= 0.7:
        return "high"
    if score >= 0.52:
        return "medium"
    return "low"


def _feature_bonus(
    contradiction_id: str,
    *,
    natal_feature_graph: Mapping[str, Any],
    compensation_scores: Mapping[str, float],
) -> float:
    public_private = natal_feature_graph.get("public_private_split") if isinstance(natal_feature_graph.get("public_private_split"), Mapping) else {}
    public_score = float(public_private.get("public_score") or 0.0)
    private_score = float(public_private.get("private_score") or 0.0)
    if contradiction_id == "visibility_vs_private_preparation":
        return max(
            min(public_score, private_score),
            float(compensation_scores.get("private_preparation_before_visibility") or 0.0),
        )
    if contradiction_id == "closeness_vs_threshold":
        return max(
            private_score,
            float(compensation_scores.get("trust_threshold_regulates_closeness") or 0.0),
        )
    if contradiction_id == "structure_vs_originality":
        return float(compensation_scores.get("structure_scaffolds_originality") or 0.0)
    if contradiction_id == "composure_vs_internal_pressure":
        return _clamp01((private_score * 0.7) + (public_score * 0.3))
    if contradiction_id == "speed_vs_control":
        return float((natal_feature_graph.get("dispositor_chain_pressure") or {}).get("summary", {}).get("loop_count") or 0.0) * 0.2
    return 0.0


def build_contradiction_signatures(
    *,
    natal_feature_graph: Mapping[str, Any] | None = None,
    primitive_scores: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    config = get_natal_selection_v3_config()
    phase_flags = config.get("phase_flags") if isinstance(config.get("phase_flags"), Mapping) else {}
    enabled = bool(phase_flags.get("contradiction_engine_enabled"))
    debug_only = bool(phase_flags.get("contradiction_engine_debug_only", True))
    feature_graph = natal_feature_graph if isinstance(natal_feature_graph, Mapping) else {}
    primitive_lookup = _primitive_entries(primitive_scores)
    feature_contradictions = _feature_contradiction_map(feature_graph)
    motif_scores = _feature_motif_scores(feature_graph)
    compensation_scores = _feature_compensation_map(feature_graph)

    signatures: list[dict[str, Any]] = []
    for contradiction_id, blueprint in _CONTRADICTION_BLUEPRINTS.items():
        left_entry, left_score = _best_primitive(primitive_lookup, blueprint["left_ids"])
        right_entry, right_score = _best_primitive(primitive_lookup, blueprint["right_ids"])
        proto = feature_contradictions.get(contradiction_id) or {}
        proto_score = float(proto.get("score") or 0.0)
        if left_score < 0.2 or right_score < 0.2:
            continue
        feature_bonus = _feature_bonus(
            contradiction_id,
            natal_feature_graph=feature_graph,
            compensation_scores=compensation_scores,
        )
        score = _clamp01(max(proto_score, (min(left_score, right_score) * 0.82) + (feature_bonus * 0.18)))
        if score < 0.26:
            continue
        related_motifs = [
            motif_id
            for motif_id in blueprint.get("motif_hints") or []
            if float(motif_scores.get(str(motif_id)) or 0.0) > 0.0
        ]
        source_primitives = [
            primitive_id
            for primitive_id in (
                str(left_entry.get("primitive_id") or ""),
                str(right_entry.get("primitive_id") or ""),
            )
            if primitive_id
        ]
        source_features = list(
            dict.fromkeys(
                [
                    *list(left_entry.get("source_features") or []),
                    *list(right_entry.get("source_features") or []),
                    *list(blueprint.get("feature_keys") or []),
                ]
            )
        )
        related_planets = list(
            dict.fromkeys(
                [
                    *list(left_entry.get("related_planets") or []),
                    *list(right_entry.get("related_planets") or []),
                ]
            )
        )
        confidence = _clamp01(
            0.30
            + (proto_score * 0.24)
            + (min(left_score, right_score) * 0.22)
            + (feature_bonus * 0.16)
            + (_clamp01((float(left_entry.get("confidence") or 0.0) + float(right_entry.get("confidence") or 0.0)) / 2.0) * 0.08)
        )
        signatures.append(
            {
                "id": contradiction_id,
                "family": str(blueprint.get("family") or "identity_tension"),
                "left": str(left_entry.get("primitive_id") or ""),
                "right": str(right_entry.get("primitive_id") or ""),
                "left_score": round(left_score, 4),
                "right_score": round(right_score, 4),
                "score": round(score, 4),
                "confidence": round(confidence, 4),
                "editorial_label": str(blueprint.get("editorial_label") or contradiction_id.replace("_", " ")),
                "priority": _priority_for_score(score),
                "slot_biases": list(blueprint.get("slot_biases") or []),
                "source_primitives": source_primitives,
                "source_features": source_features,
                "related_planets": related_planets,
                "related_motifs": related_motifs,
                "evidence": list(dict.fromkeys([*list(proto.get("evidence") or []), *related_motifs])),
                "debug": {
                    "proto_score": round(proto_score, 4),
                    "feature_bonus": round(feature_bonus, 4),
                    "left_confidence": round(float(left_entry.get("confidence") or 0.0), 4),
                    "right_confidence": round(float(right_entry.get("confidence") or 0.0), 4),
                },
            }
        )

    signatures.sort(key=lambda item: (-float(item.get("score") or 0.0), str(item.get("id") or "")))
    by_id = {str(item.get("id") or ""): dict(item) for item in signatures}
    return {
        "engine_version": "contradiction_engine_v1",
        "enabled": enabled,
        "mode": "active" if enabled else ("shadow" if debug_only else "disabled"),
        "signatures": signatures,
        "top_signatures": signatures[:4],
        "by_id": by_id,
        "debug": {
            "raw_feature_contradictions": list(feature_contradictions.values()),
            "compensation_patterns": dict(compensation_scores),
            "primitive_links": {
                contradiction_id: {
                    "left_ids": list(blueprint.get("left_ids") or []),
                    "right_ids": list(blueprint.get("right_ids") or []),
                }
                for contradiction_id, blueprint in _CONTRADICTION_BLUEPRINTS.items()
            },
        },
    }
