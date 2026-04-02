from __future__ import annotations

from itertools import combinations
from typing import Any, Dict, Mapping, Sequence

from .natal_selection_config import get_natal_selection_v3_config


_SLOT_ORDER = [
    "primary_identity_spine",
    "secondary_balancing_line",
    "relational_line",
    "work_visibility_line",
    "shadow_protection_line",
]

_SLOT_FAMILY = {
    "primary_identity_spine": "identity",
    "secondary_balancing_line": "identity",
    "relational_line": "relational",
    "work_visibility_line": "visibility",
    "shadow_protection_line": "shadow",
}

_SLOT_PRIORITIES = {
    "primary_identity_spine": [
        "self_definition",
        "inner_structure",
        "originality_drive",
        "big_picture_vision",
        "visible_presence",
        "mental_structuring",
        "meaningful_expansion",
        "systems_thinking",
    ],
    "secondary_balancing_line": [
        "originality_drive",
        "systems_thinking",
        "methodical_drive",
        "recharge_through_home",
        "backstage_creation",
        "visible_presence",
        "big_picture_vision",
        "mental_structuring",
        "inner_structure",
    ],
    "relational_line": [
        "intimacy_depth",
        "relational_security",
        "graceful_affection",
        "transformative_bonding",
        "emotional_threshold",
    ],
    "work_visibility_line": [
        "public_refinement",
        "visibility_sensitivity",
        "visible_presence",
        "creation_luck",
        "network_luck",
        "backstage_creation",
        "meaningful_expansion",
    ],
    "shadow_protection_line": [
        "inner_critic",
        "push_pull_drive",
        "emotional_threshold",
        "tone_sensitivity",
        "recharge_through_home",
        "family_self_reliance",
        "backstage_creation",
        "methodical_drive",
    ],
}

_PRIMITIVE_LABELS = {
    "self_definition": "defined selfhood",
    "visible_presence": "visible presence",
    "inner_structure": "inner structure",
    "originality_drive": "originality drive",
    "big_picture_vision": "big-picture vision",
    "tone_sensitivity": "tone sensitivity",
    "systems_thinking": "systems thinking",
    "inner_critic": "inner critic",
    "push_pull_drive": "push-pull drive",
    "methodical_drive": "methodical drive",
    "mental_structuring": "mental structuring",
    "intimacy_depth": "intimacy depth",
    "relational_security": "relational security",
    "graceful_affection": "graceful affection",
    "transformative_bonding": "transformative bonding",
    "emotional_threshold": "emotional threshold",
    "public_refinement": "public refinement",
    "visibility_sensitivity": "visibility sensitivity",
    "backstage_creation": "backstage creation",
    "recharge_through_home": "recharge through home",
    "family_self_reliance": "family self-reliance",
    "creation_luck": "creative flow",
    "network_luck": "network luck",
    "meaningful_expansion": "meaningful expansion",
}

_PRIMITIVE_MOTIF_HINTS = {
    "self_definition": ["identity_structure"],
    "visible_presence": ["identity_structure", "visibility_sensitivity"],
    "inner_structure": ["identity_structure", "language_boundary", "system_builder"],
    "originality_drive": ["visionary_originality"],
    "big_picture_vision": ["visionary_originality", "creative_flow"],
    "tone_sensitivity": ["language_boundary", "private_intellect"],
    "systems_thinking": ["system_builder", "language_boundary", "private_intellect"],
    "inner_critic": ["language_boundary", "depth_guardedness"],
    "push_pull_drive": ["push_pull_drive"],
    "methodical_drive": ["system_builder", "push_pull_drive"],
    "mental_structuring": ["private_intellect", "mentalized_emotion", "language_boundary"],
    "intimacy_depth": ["depth_intimacy", "transformational_intensity", "thresholded_intimacy"],
    "relational_security": ["soft_bonding", "quiet_loyalty", "selective_bonding", "service_love"],
    "graceful_affection": ["soft_bonding"],
    "transformative_bonding": ["transformational_intensity", "depth_intimacy"],
    "emotional_threshold": ["thresholded_intimacy", "depth_guardedness", "selective_bonding"],
    "public_refinement": ["visibility_sensitivity", "identity_structure", "creative_flow"],
    "visibility_sensitivity": ["visibility_sensitivity", "hidden_creation"],
    "backstage_creation": ["hidden_creation", "hidden_devotion", "private_intellect"],
    "recharge_through_home": ["independent_roots", "hidden_devotion"],
    "family_self_reliance": ["independent_roots"],
    "creation_luck": ["creative_flow"],
    "network_luck": ["social_fire_private_core", "creative_flow", "quiet_loyalty"],
    "meaningful_expansion": ["visionary_originality", "creative_flow"],
}

_PAIR_LABELS = {
    frozenset({"self_definition", "inner_structure"}): ("identity_structure_core", "defined structure"),
    frozenset({"inner_structure", "originality_drive"}): ("structured_originality", "structured originality"),
    frozenset({"self_definition", "visible_presence"}): ("defined_visibility", "defined visibility"),
    frozenset({"big_picture_vision", "meaningful_expansion"}): ("expansive_vision", "expansive vision"),
    frozenset({"mental_structuring", "systems_thinking"}): ("mental_architecture", "mental architecture"),
    frozenset({"intimacy_depth", "emotional_threshold"}): ("guarded_depth", "guarded depth"),
    frozenset({"public_refinement", "visibility_sensitivity"}): ("sensitive_visibility", "sensitive visibility"),
    frozenset({"push_pull_drive", "methodical_drive"}): ("controlled_momentum", "controlled momentum"),
}


def _clamp01(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, number))


def _primitive_entries(primitive_scores: Mapping[str, Any] | None) -> Dict[str, Dict[str, Any]]:
    payload = primitive_scores if isinstance(primitive_scores, Mapping) else {}
    items = payload.get("primitive_scores") if isinstance(payload.get("primitive_scores"), Sequence) else []
    return {
        str(item.get("primitive_id") or ""): dict(item)
        for item in items
        if isinstance(item, Mapping) and str(item.get("primitive_id") or "").strip()
    }


def _contradiction_entries(contradiction_signatures: Mapping[str, Any] | None) -> Dict[str, Dict[str, Any]]:
    payload = contradiction_signatures if isinstance(contradiction_signatures, Mapping) else {}
    items = payload.get("signatures") if isinstance(payload.get("signatures"), Sequence) else []
    return {
        str(item.get("id") or ""): dict(item)
        for item in items
        if isinstance(item, Mapping) and str(item.get("id") or "").strip()
    }


def _priority_weight(slot: str, primitive_id: str) -> float:
    priorities = _SLOT_PRIORITIES.get(slot, [])
    if primitive_id not in priorities:
        return 0.0
    index = priorities.index(primitive_id)
    return max(0.02, 0.12 - (index * 0.012))


def _motif_scores(natal_feature_graph: Mapping[str, Any] | None) -> Dict[str, float]:
    payload = natal_feature_graph if isinstance(natal_feature_graph, Mapping) else {}
    repeated = payload.get("repeated_motif_count") if isinstance(payload.get("repeated_motif_count"), Mapping) else {}
    dominant = repeated.get("dominant_motifs") if isinstance(repeated.get("dominant_motifs"), Sequence) else []
    return {
        str(item.get("id") or ""): float(item.get("score") or 0.0)
        for item in dominant
        if isinstance(item, Mapping) and str(item.get("id") or "").strip()
    }


def _dominant_planets(source_primitives: Sequence[str], primitive_lookup: Mapping[str, Mapping[str, Any]], natal_feature_graph: Mapping[str, Any]) -> list[str]:
    planet_salience = natal_feature_graph.get("planet_salience") if isinstance(natal_feature_graph.get("planet_salience"), Mapping) else {}
    seen: Dict[str, float] = {}
    for primitive_id in source_primitives:
        entry = primitive_lookup.get(str(primitive_id)) if isinstance(primitive_lookup.get(str(primitive_id)), Mapping) else {}
        for planet in entry.get("related_planets") or []:
            seen[str(planet)] = max(float(planet_salience.get(str(planet), {}).get("score") or 0.0), float(seen.get(str(planet)) or 0.0))
    return [
        planet
        for planet, _score in sorted(seen.items(), key=lambda item: (-float(item[1]), item[0]))
    ][:4]


def _candidate_label(
    source_primitives: Sequence[str],
    contradiction_ids: Sequence[str],
    contradiction_lookup: Mapping[str, Mapping[str, Any]],
) -> tuple[str, str]:
    if contradiction_ids:
        contradiction = contradiction_lookup.get(str(contradiction_ids[0])) if isinstance(contradiction_lookup.get(str(contradiction_ids[0])), Mapping) else {}
        label = str(contradiction.get("editorial_label") or str(contradiction_ids[0]).replace("_", " "))
        line_id = str(contradiction.get("id") or contradiction_ids[0])
        if source_primitives:
            line_id = f"{line_id}__{'_'.join(sorted(source_primitives))}"
        return line_id, label
    if len(source_primitives) == 2:
        pair_key = frozenset(str(item) for item in source_primitives)
        if pair_key in _PAIR_LABELS:
            return _PAIR_LABELS[pair_key]
    labels = [_PRIMITIVE_LABELS.get(str(primitive_id), str(primitive_id).replace("_", " ")) for primitive_id in source_primitives]
    if not labels:
        return "empty_line", "unresolved line"
    if len(labels) == 1:
        primitive_id = str(source_primitives[0])
        return primitive_id, labels[0]
    return "__".join(sorted(str(item) for item in source_primitives)), " + ".join(labels[:2])


def _supporting_motifs(source_primitives: Sequence[str], motif_scores: Mapping[str, float]) -> list[str]:
    motif_ids = []
    for primitive_id in source_primitives:
        motif_ids.extend(_PRIMITIVE_MOTIF_HINTS.get(str(primitive_id), []))
    return [
        motif_id
        for motif_id in dict.fromkeys(motif_ids)
        if float(motif_scores.get(str(motif_id)) or 0.0) > 0.0
    ]


def _slot_role_fit(
    slot: str,
    *,
    source_primitives: Sequence[str],
    contradiction_ids: Sequence[str],
    primitive_lookup: Mapping[str, Mapping[str, Any]],
    natal_feature_graph: Mapping[str, Any],
    contradiction_lookup: Mapping[str, Mapping[str, Any]],
) -> float:
    bonus = 0.0
    weights = [_priority_weight(slot, str(primitive_id)) for primitive_id in source_primitives]
    if weights:
        bonus += sum(weights) / len(weights)
    public_private = natal_feature_graph.get("public_private_split") if isinstance(natal_feature_graph.get("public_private_split"), Mapping) else {}
    public_score = float(public_private.get("public_score") or 0.0)
    private_score = float(public_private.get("private_score") or 0.0)
    if slot == "primary_identity_spine":
        if any(str(primitive_id) in {"self_definition", "inner_structure", "originality_drive"} for primitive_id in source_primitives):
            bonus += 0.07
    elif slot == "secondary_balancing_line":
        if contradiction_ids:
            bonus += 0.06
        if any(str(primitive_id) in {"originality_drive", "systems_thinking", "backstage_creation"} for primitive_id in source_primitives):
            bonus += 0.04
    elif slot == "relational_line":
        bonus += private_score * 0.08
    elif slot == "work_visibility_line":
        bonus += public_score * 0.08
    elif slot == "shadow_protection_line":
        bonus += private_score * 0.06
        if any(str(primitive_id) in {"inner_critic", "emotional_threshold", "tone_sensitivity"} for primitive_id in source_primitives):
            bonus += 0.05
    for contradiction_id in contradiction_ids:
        contradiction = contradiction_lookup.get(str(contradiction_id)) if isinstance(contradiction_lookup.get(str(contradiction_id)), Mapping) else {}
        if slot in (contradiction.get("slot_biases") or []):
            bonus += 0.05
    return round(_clamp01(bonus), 4)


def _build_candidate(
    *,
    slot: str,
    source_primitives: Sequence[str],
    contradiction_ids: Sequence[str],
    primitive_lookup: Mapping[str, Mapping[str, Any]],
    contradiction_lookup: Mapping[str, Mapping[str, Any]],
    natal_feature_graph: Mapping[str, Any],
    selector_weights: Mapping[str, Any],
) -> Dict[str, Any] | None:
    entries = [
        dict(primitive_lookup.get(str(primitive_id)) or {})
        for primitive_id in source_primitives
        if isinstance(primitive_lookup.get(str(primitive_id)), Mapping)
    ]
    if not entries:
        return None
    primitive_scores = [float(entry.get("score") or 0.0) for entry in entries]
    primitive_core = max(primitive_scores, default=0.0)
    remaining = primitive_scores[1:]
    primitive_support = (sum(remaining) / len(remaining)) if remaining else 0.0
    feature_support = sum(float(entry.get("feature_support") or 0.0) for entry in entries) / len(entries)
    salience_bonus = sum(float(entry.get("salience") or 0.0) for entry in entries) / len(entries)
    contradiction_scores = [
        float((contradiction_lookup.get(str(contradiction_id)) or {}).get("score") or 0.0)
        for contradiction_id in contradiction_ids
    ]
    contradiction_bonus = (sum(contradiction_scores) / len(contradiction_scores)) if contradiction_scores else 0.0
    motif_scores = _motif_scores(natal_feature_graph)
    supporting_motifs = _supporting_motifs(source_primitives, motif_scores)
    for contradiction_id in contradiction_ids:
        contradiction = contradiction_lookup.get(str(contradiction_id)) if isinstance(contradiction_lookup.get(str(contradiction_id)), Mapping) else {}
        for motif_id in contradiction.get("related_motifs") or []:
            if float(motif_scores.get(str(motif_id)) or 0.0) > 0.0 and motif_id not in supporting_motifs:
                supporting_motifs.append(str(motif_id))
    motif_support = (
        sum(float(motif_scores.get(str(motif_id)) or 0.0) for motif_id in supporting_motifs) / len(supporting_motifs)
        if supporting_motifs
        else 0.0
    )
    role_fit_bonus = _slot_role_fit(
        slot,
        source_primitives=source_primitives,
        contradiction_ids=contradiction_ids,
        primitive_lookup=primitive_lookup,
        natal_feature_graph=natal_feature_graph,
        contradiction_lookup=contradiction_lookup,
    )
    base_score = _clamp01(
        (primitive_core * float(selector_weights.get("primitive_core_weight") or 0.34))
        + (primitive_support * float(selector_weights.get("primitive_support_weight") or 0.16))
        + (feature_support * float(selector_weights.get("feature_support_weight") or 0.16))
        + (motif_support * float(selector_weights.get("motif_support_weight") or 0.12))
        + (contradiction_bonus * float(selector_weights.get("contradiction_bonus_weight") or 0.10))
        + (salience_bonus * float(selector_weights.get("salience_bonus_weight") or 0.06))
        + (role_fit_bonus * float(selector_weights.get("role_fit_weight") or 0.06))
    )
    confidence = _clamp01(
        (sum(float(entry.get("confidence") or 0.0) for entry in entries) / len(entries)) * 0.45
        + feature_support * 0.20
        + motif_support * 0.15
        + contradiction_bonus * 0.10
        + role_fit_bonus * 0.10
    )
    line_id, label = _candidate_label(source_primitives, contradiction_ids, contradiction_lookup)
    supporting_features = list(
        dict.fromkeys(
            [
                feature
                for entry in entries
                for feature in (entry.get("source_features") or [])
            ]
            + [
                feature
                for contradiction_id in contradiction_ids
                for feature in ((contradiction_lookup.get(str(contradiction_id)) or {}).get("source_features") or [])
            ]
        )
    )
    counterweights = list(
        dict.fromkeys(
            [
                value
                for entry in entries
                for value in (entry.get("counterweights") or [])
            ]
            + list(contradiction_ids)
        )
    )
    dominant_primitive = max(entries, key=lambda item: float(item.get("score") or 0.0))
    return {
        "line_id": line_id,
        "slot": slot,
        "family": _SLOT_FAMILY.get(slot, "identity"),
        "label": label,
        "score": round(base_score, 4),
        "confidence": round(confidence, 4),
        "source_primitives": list(dict.fromkeys([str(item) for item in source_primitives if str(item).strip()])),
        "supporting_features": supporting_features,
        "supporting_motifs": supporting_motifs,
        "counterweights": counterweights,
        "contradiction_ids": list(dict.fromkeys([str(item) for item in contradiction_ids if str(item).strip()])),
        "dominant_primitive": str(dominant_primitive.get("primitive_id") or ""),
        "dominant_planets": _dominant_planets(source_primitives, primitive_lookup, natal_feature_graph),
        "evidence": [
            {"type": "primitive", "id": str(entry.get("primitive_id") or ""), "score": round(float(entry.get("score") or 0.0), 4)}
            for entry in entries
        ]
        + [{"type": "contradiction", "id": contradiction_id} for contradiction_id in contradiction_ids],
        "score_breakdown": {
            "primitive_core": round(primitive_core, 4),
            "primitive_support": round(primitive_support, 4),
            "feature_support": round(feature_support, 4),
            "motif_support": round(motif_support, 4),
            "contradiction_bonus": round(contradiction_bonus, 4),
            "salience_bonus": round(salience_bonus, 4),
            "role_fit_bonus": round(role_fit_bonus, 4),
            "redundancy_penalty": 0.0,
            "incoherence_penalty": 0.0,
        },
        "candidate_type": "contradiction" if contradiction_ids else ("pair" if len(source_primitives) > 1 else "single"),
    }


def _candidate_overlap(candidate: Mapping[str, Any], selected: Mapping[str, Any]) -> float:
    left = {str(item) for item in candidate.get("source_primitives") or [] if str(item).strip()}
    right = {str(item) for item in selected.get("source_primitives") or [] if str(item).strip()}
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _selection_penalties(
    *,
    slot: str,
    candidate: Mapping[str, Any],
    selected: Mapping[str, Mapping[str, Any]],
) -> tuple[float, float]:
    redundancy = 0.0
    incoherence = 0.0
    primary = selected.get("primary_identity_spine") if isinstance(selected.get("primary_identity_spine"), Mapping) else {}
    for payload in selected.values():
        if not isinstance(payload, Mapping):
            continue
        overlap = _candidate_overlap(candidate, payload)
        redundancy = max(redundancy, overlap)
        if overlap >= 0.67 and not list(candidate.get("contradiction_ids") or []):
            redundancy = max(redundancy, 1.0)
    if primary and slot != "primary_identity_spine":
        if str(candidate.get("dominant_primitive") or "") == str(primary.get("dominant_primitive") or "") and not list(candidate.get("contradiction_ids") or []):
            incoherence = max(incoherence, 0.7)
        if slot == "secondary_balancing_line" and _candidate_overlap(candidate, primary) >= 0.67 and not list(candidate.get("contradiction_ids") or []):
            incoherence = max(incoherence, 1.0)
        if slot == "shadow_protection_line" and str(candidate.get("family") or "") != "shadow" and not list(candidate.get("contradiction_ids") or []):
            incoherence = max(incoherence, 0.6)
    return round(_clamp01(redundancy), 4), round(_clamp01(incoherence), 4)


def build_master_natal_selector(
    *,
    primitive_scores: Mapping[str, Any] | None = None,
    natal_feature_graph: Mapping[str, Any] | None = None,
    contradiction_signatures: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    config = get_natal_selection_v3_config()
    phase_flags = config.get("phase_flags") if isinstance(config.get("phase_flags"), Mapping) else {}
    enabled = bool(phase_flags.get("master_selector_enabled"))
    debug_only = bool(phase_flags.get("master_selector_debug_only", True))
    selector_weights = (config.get("weights") or {}).get("selector_v1") if isinstance(config.get("weights"), Mapping) else {}
    primitive_lookup = _primitive_entries(primitive_scores)
    contradiction_lookup = _contradiction_entries(contradiction_signatures)
    feature_graph = natal_feature_graph if isinstance(natal_feature_graph, Mapping) else {}

    candidate_pool: Dict[str, list[dict[str, Any]]] = {}
    for slot in _SLOT_ORDER:
        relevant_ids = [primitive_id for primitive_id in _SLOT_PRIORITIES.get(slot, []) if primitive_id in primitive_lookup]
        relevant_entries = sorted(
            [dict(primitive_lookup[primitive_id]) for primitive_id in relevant_ids],
            key=lambda item: (-float(item.get("score") or 0.0), str(item.get("primitive_id") or "")),
        )
        if not relevant_entries:
            relevant_entries = sorted(
                [
                    dict(entry)
                    for entry in primitive_lookup.values()
                    if str(entry.get("category") or "") in {_SLOT_FAMILY.get(slot, "identity"), "compensation"}
                ]
                or [dict(entry) for entry in primitive_lookup.values()],
                key=lambda item: (-float(item.get("score") or 0.0), str(item.get("primitive_id") or "")),
            )
        candidates: list[dict[str, Any]] = []
        top_entries = relevant_entries[:5]
        for entry in top_entries:
            candidate = _build_candidate(
                slot=slot,
                source_primitives=[str(entry.get("primitive_id") or "")],
                contradiction_ids=[],
                primitive_lookup=primitive_lookup,
                contradiction_lookup=contradiction_lookup,
                natal_feature_graph=feature_graph,
                selector_weights=selector_weights,
            )
            if candidate:
                candidates.append(candidate)
        for left, right in combinations(top_entries[:4], 2):
            if float(right.get("score") or 0.0) < 0.48:
                continue
            candidate = _build_candidate(
                slot=slot,
                source_primitives=[str(left.get("primitive_id") or ""), str(right.get("primitive_id") or "")],
                contradiction_ids=[],
                primitive_lookup=primitive_lookup,
                contradiction_lookup=contradiction_lookup,
                natal_feature_graph=feature_graph,
                selector_weights=selector_weights,
            )
            if candidate:
                candidates.append(candidate)
        for contradiction in contradiction_lookup.values():
            if slot not in (contradiction.get("slot_biases") or []):
                continue
            source_primitives = [
                primitive_id
                for primitive_id in contradiction.get("source_primitives") or []
                if primitive_id in primitive_lookup
            ]
            if not source_primitives:
                continue
            candidate = _build_candidate(
                slot=slot,
                source_primitives=source_primitives[:2],
                contradiction_ids=[str(contradiction.get("id") or "")],
                primitive_lookup=primitive_lookup,
                contradiction_lookup=contradiction_lookup,
                natal_feature_graph=feature_graph,
                selector_weights=selector_weights,
            )
            if candidate:
                candidates.append(candidate)
        deduped: Dict[str, dict[str, Any]] = {}
        for candidate in candidates:
            key = f"{candidate['line_id']}::{candidate['slot']}"
            existing = deduped.get(key)
            if not existing or float(candidate.get("score") or 0.0) > float(existing.get("score") or 0.0):
                deduped[key] = candidate
        candidate_pool[slot] = sorted(
            deduped.values(),
            key=lambda item: (-float(item.get("score") or 0.0), -float(item.get("confidence") or 0.0), str(item.get("line_id") or "")),
        )[:8]

    selected: Dict[str, Dict[str, Any] | None] = {}
    selected_order: list[dict[str, Any]] = []
    rejections: list[dict[str, Any]] = []
    for slot in _SLOT_ORDER:
        best: Dict[str, Any] | None = None
        best_score = -1.0
        for candidate in candidate_pool.get(slot, []):
            redundancy_penalty, incoherence_penalty = _selection_penalties(
                slot=slot,
                candidate=candidate,
                selected={key: value for key, value in selected.items() if isinstance(value, Mapping)},
            )
            final_score = _clamp01(
                float(candidate.get("score") or 0.0)
                - redundancy_penalty * float(selector_weights.get("redundancy_penalty_weight") or 0.08)
                - incoherence_penalty * float(selector_weights.get("incoherence_penalty_weight") or 0.08)
            )
            if final_score > best_score:
                best_score = final_score
                best = {
                    **dict(candidate),
                    "score": round(final_score, 4),
                    "selection_score": round(final_score, 4),
                    "fallback_used": float(candidate.get("confidence") or 0.0) < 0.52,
                    "score_breakdown": {
                        **dict(candidate.get("score_breakdown") or {}),
                        "redundancy_penalty": round(redundancy_penalty, 4),
                        "incoherence_penalty": round(incoherence_penalty, 4),
                    },
                }
            else:
                rejections.append(
                    {
                        "slot": slot,
                        "line_id": str(candidate.get("line_id") or ""),
                        "reason": "lower_selection_score",
                    }
                )
        selected[slot] = best
        if best is not None:
            selected_order.append(
                {
                    "slot": slot,
                    "line_id": str(best.get("line_id") or ""),
                    "score": round(float(best.get("score") or 0.0), 4),
                }
            )

    identity_spine = {
        slot: dict(payload)
        for slot, payload in selected.items()
        if isinstance(payload, Mapping)
    }
    return {
        "engine_version": "master_selector_v1",
        "enabled": enabled,
        "mode": "active" if enabled else ("shadow" if debug_only else "disabled"),
        "identity_spine": identity_spine,
        "primary_identity_spine": selected.get("primary_identity_spine"),
        "secondary_balancing_line": selected.get("secondary_balancing_line"),
        "relational_line": selected.get("relational_line"),
        "work_visibility_line": selected.get("work_visibility_line"),
        "shadow_protection_line": selected.get("shadow_protection_line"),
        "candidate_pool": candidate_pool,
        "selection_debug": {
            "selected_order": selected_order,
            "candidate_counts": {slot: len(items) for slot, items in candidate_pool.items()},
            "rejections": rejections[:20],
        },
    }
