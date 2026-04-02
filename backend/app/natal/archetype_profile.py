from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence


_ROOT = Path(__file__).resolve().parents[3]
_TAXONOMY_PATH = _ROOT / "config" / "classifiers" / "archetype_taxonomy_v1.yaml"
_FUSION_PATH = _ROOT / "config" / "scoring" / "archetype_fusion_v1.yaml"

_PRIVATE_SLOT = {"shadow_protection_line", "relational_line"}
_PUBLIC_SLOT = {"work_visibility_line", "primary_identity_spine"}
_TEXT_FIELDS = (
    "motto_tr",
    "portrait_tr",
    "gift_tr",
    "fear_tr",
    "shadow_tr",
    "relationship_tr",
    "work_style_tr",
    "growth_tr",
)


def _clamp01(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, number))


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _read_jsonish(path: Path) -> Dict[str, Any]:
    raw = path.read_text(encoding="utf-8").strip()
    if raw.startswith('"') and raw.endswith('"'):
        raw = raw[1:-1].replace('\\"', '"')
    return json.loads(raw)


@lru_cache(maxsize=1)
def _taxonomy() -> Dict[str, Any]:
    return _read_jsonish(_TAXONOMY_PATH)


@lru_cache(maxsize=1)
def _fusion() -> Dict[str, Any]:
    return _read_jsonish(_FUSION_PATH)


def get_archetype_runtime_versions() -> Dict[str, str]:
    taxonomy = _taxonomy()
    fusion = _fusion()
    return {
        "engine_version": "archetype_profile_v1",
        "taxonomy_version": f"archetype_taxonomy_v1:{_safe_text(taxonomy.get('version')) or 'unknown'}",
        "fusion_version": f"archetype_fusion_v1:{_safe_text(fusion.get('version')) or 'unknown'}",
    }


def _archetype_text_payload(archetype: Mapping[str, Any]) -> Dict[str, str]:
    payload: Dict[str, str] = {}
    for key in _TEXT_FIELDS:
        value = _safe_text(archetype.get(key))
        if value:
            payload[key] = value
    return payload


def _primitive_lookup(primitive_scores: Mapping[str, Any] | None) -> Dict[str, Dict[str, Any]]:
    payload = primitive_scores if isinstance(primitive_scores, Mapping) else {}
    items = payload.get("primitive_scores") if isinstance(payload.get("primitive_scores"), Sequence) else []
    return {
        _safe_text(item.get("primitive_id")): dict(item)
        for item in items
        if isinstance(item, Mapping) and _safe_text(item.get("primitive_id"))
    }


def _identity_spine(master_selector: Mapping[str, Any] | None) -> Dict[str, Dict[str, Any]]:
    payload = master_selector if isinstance(master_selector, Mapping) else {}
    spine = payload.get("identity_spine") if isinstance(payload.get("identity_spine"), Mapping) else {}
    return {
        _safe_text(slot): dict(value)
        for slot, value in spine.items()
        if isinstance(value, Mapping) and _safe_text(slot)
    }


def _top_contradiction(contradiction_signatures: Mapping[str, Any] | None) -> Dict[str, Any]:
    payload = contradiction_signatures if isinstance(contradiction_signatures, Mapping) else {}
    items = payload.get("top_signatures") if isinstance(payload.get("top_signatures"), Sequence) else []
    for item in items:
        if isinstance(item, Mapping):
            return dict(item)
    items = payload.get("signatures") if isinstance(payload.get("signatures"), Sequence) else []
    for item in items:
        if isinstance(item, Mapping):
            return dict(item)
    return {}


def _public_private(natal_feature_graph: Mapping[str, Any] | None) -> tuple[float, float, float]:
    payload = natal_feature_graph if isinstance(natal_feature_graph, Mapping) else {}
    split = payload.get("public_private_split") if isinstance(payload.get("public_private_split"), Mapping) else {}
    public_score = _clamp01(split.get("public_score"))
    private_score = _clamp01(split.get("private_score"))
    balance = 1.0 - abs(public_score - private_score)
    return public_score, private_score, _clamp01(balance)


def _slot_alignment_bonus(
    archetype: Mapping[str, Any],
    spine: Mapping[str, Mapping[str, Any]],
) -> tuple[float, dict[str, float]]:
    primitive_ids = set((archetype.get("primitive_weights") or {}).keys())
    slot_biases = {_safe_text(slot) for slot in archetype.get("slot_biases") or [] if _safe_text(slot)}
    details: dict[str, float] = {}
    total = 0.0
    for slot, payload in spine.items():
        if slot not in slot_biases:
            continue
        source_primitives = {
            _safe_text(item)
            for item in payload.get("source_primitives") or []
            if _safe_text(item)
        }
        if not source_primitives:
            overlap_ratio = 0.0
        else:
            overlap_ratio = len(source_primitives & primitive_ids) / len(source_primitives)
        confidence = _clamp01(payload.get("confidence"))
        bonus = confidence * (0.05 + (overlap_ratio * 0.13))
        details[slot] = round(bonus, 4)
        total += bonus
    return round(_clamp01(total), 4), details


def _contradiction_bonus(
    archetype: Mapping[str, Any],
    contradiction: Mapping[str, Any],
) -> tuple[float, str]:
    contradiction_id = _safe_text(contradiction.get("id"))
    supported = {
        _safe_text(item)
        for item in archetype.get("supports_contradictions") or []
        if _safe_text(item)
    }
    if contradiction_id not in supported:
        return 0.0, ""
    return round(_clamp01(_safe_float(contradiction.get("score")) * 0.10), 4), contradiction_id


def _public_private_bonus(
    archetype: Mapping[str, Any],
    *,
    public_score: float,
    private_score: float,
    balance_score: float,
) -> float:
    slot_biases = {_safe_text(slot) for slot in archetype.get("slot_biases") or [] if _safe_text(slot)}
    if slot_biases & _PUBLIC_SLOT and not slot_biases & _PRIVATE_SLOT:
        return round(public_score * 0.08, 4)
    if slot_biases & _PRIVATE_SLOT and not slot_biases & _PUBLIC_SLOT:
        return round(private_score * 0.08, 4)
    return round(balance_score * 0.05, 4)


def build_chart_prior(
    *,
    primitive_scores: Mapping[str, Any],
    master_selector: Mapping[str, Any] | None = None,
    contradiction_signatures: Mapping[str, Any] | None = None,
    natal_feature_graph: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    taxonomy = _taxonomy()
    primitives = _primitive_lookup(primitive_scores)
    spine = _identity_spine(master_selector)
    contradiction = _top_contradiction(contradiction_signatures)
    public_score, private_score, balance_score = _public_private(natal_feature_graph)

    scored: list[dict[str, Any]] = []
    for archetype in taxonomy.get("archetypes") or []:
        if not isinstance(archetype, Mapping):
            continue
        primitive_weights = archetype.get("primitive_weights") if isinstance(archetype.get("primitive_weights"), Mapping) else {}
        base = 0.0
        contributing_primitives: list[dict[str, Any]] = []
        for primitive_id, weight in primitive_weights.items():
            if not _safe_text(primitive_id):
                continue
            primitive = primitives.get(_safe_text(primitive_id), {})
            score = _clamp01(primitive.get("score"))
            contribution = score * _safe_float(weight)
            base += contribution
            if contribution > 0:
                contributing_primitives.append(
                    {
                        "primitive_id": _safe_text(primitive_id),
                        "primitive_score": round(score, 4),
                        "weight": round(_safe_float(weight), 4),
                        "contribution": round(contribution, 4),
                    }
                )
        slot_bonus, slot_details = _slot_alignment_bonus(archetype, spine)
        contradiction_boost, contradiction_id = _contradiction_bonus(archetype, contradiction)
        split_bonus = _public_private_bonus(
            archetype,
            public_score=public_score,
            private_score=private_score,
            balance_score=balance_score,
        )
        total = _clamp01(base + slot_bonus + contradiction_boost + split_bonus)
        scored.append(
            {
                "id": _safe_text(archetype.get("id")),
                "label": _safe_text(archetype.get("label_tr")),
                **_archetype_text_payload(archetype),
                "score": round(total, 4),
                "components": {
                    "base": round(_clamp01(base), 4),
                    "slot_bonus": slot_bonus,
                    "contradiction_bonus": contradiction_boost,
                    "public_private_bonus": split_bonus,
                },
                "slot_alignment": slot_details,
                "matched_contradiction": contradiction_id,
                "primitive_contributors": contributing_primitives,
            }
        )

    scored.sort(key=lambda item: (-_safe_float(item.get("score")), _safe_text(item.get("id"))))
    return {
        "engine_version": "archetype_chart_prior_v1",
        "taxonomy_version": _safe_text(taxonomy.get("version")),
        "items": scored,
        "by_id": {_safe_text(item.get("id")): item for item in scored},
    }


def _select_weight_profile(
    *,
    has_test_scores: bool,
    birth_time_confidence: str,
    answer_consistency: float | None,
) -> str:
    if not has_test_scores:
        return "chart_only"
    normalized_birth = _safe_text(birth_time_confidence).lower()
    consistency = _safe_float(answer_consistency) if answer_consistency is not None else 1.0
    birth_low = normalized_birth in {"unknown", "missing", "approx", "low"}
    test_low = consistency < 0.45
    if birth_low and test_low:
        return "both_low_confidence"
    if birth_low:
        return "birth_time_low_confidence"
    if test_low:
        return "answer_consistency_low"
    return "default"


def _weight_profile(name: str) -> Dict[str, float]:
    weights = (_fusion().get("weights") or {}) if isinstance(_fusion().get("weights"), Mapping) else {}
    if name == "chart_only":
        return {"chart_prior": 1.0, "test_score": 0.0, "context_score": 0.0}
    payload = weights.get(name) if isinstance(weights.get(name), Mapping) else {}
    return {
        "chart_prior": _safe_float(payload.get("chart_prior")),
        "test_score": _safe_float(payload.get("test_score")),
        "context_score": _safe_float(payload.get("context_score")),
    }


def _chart_confidence(birth_time_confidence: str) -> float:
    config = ((_fusion().get("confidence") or {}).get("chart")) if isinstance((_fusion().get("confidence") or {}).get("chart"), Mapping) else {}
    normalized = _safe_text(birth_time_confidence).lower()
    score = 0.7
    if normalized in {"exact", "verified"}:
        score += _safe_float(config.get("exact_birth_time_bonus"))
    elif normalized in {"rounded", "estimated"}:
        score += _safe_float(config.get("rounded_birth_time_bonus"))
    elif normalized in {"unknown", "missing", "approx", "low"}:
        score -= _safe_float(config.get("missing_birth_time_penalty"))
    return round(_clamp01(score), 4)


def _test_confidence(answer_consistency: float | None, has_test_scores: bool) -> float:
    if not has_test_scores:
        return 0.0
    if answer_consistency is None:
        return 0.7
    return round(_clamp01(answer_consistency), 4)


def _normalized_mapping(values: Mapping[str, Any] | None) -> Dict[str, float]:
    payload = values if isinstance(values, Mapping) else {}
    return {
        _safe_text(key): _clamp01(value)
        for key, value in payload.items()
        if _safe_text(key)
    }


def _select_slots(final_scores: Mapping[str, float]) -> Dict[str, str]:
    taxonomy = _taxonomy()
    by_slot: Dict[str, tuple[str, float]] = {}
    for archetype in taxonomy.get("archetypes") or []:
        if not isinstance(archetype, Mapping):
            continue
        archetype_id = _safe_text(archetype.get("id"))
        score = _safe_float(final_scores.get(archetype_id))
        for slot in archetype.get("slot_biases") or []:
            slot_id = _safe_text(slot)
            if not slot_id:
                continue
            current = by_slot.get(slot_id)
            if current is None or score > current[1]:
                by_slot[slot_id] = (archetype_id, score)
    return {slot: value[0] for slot, value in by_slot.items()}


def build_archetype_profile(
    *,
    primitive_scores: Mapping[str, Any],
    master_selector: Mapping[str, Any] | None = None,
    contradiction_signatures: Mapping[str, Any] | None = None,
    natal_feature_graph: Mapping[str, Any] | None = None,
    test_scores: Mapping[str, Any] | None = None,
    context_scores: Mapping[str, Any] | None = None,
    birth_time_confidence: str = "exact",
    answer_consistency: float | None = None,
) -> Dict[str, Any]:
    taxonomy = _taxonomy()
    fusion = _fusion()
    chart_prior = build_chart_prior(
        primitive_scores=primitive_scores,
        master_selector=master_selector,
        contradiction_signatures=contradiction_signatures,
        natal_feature_graph=natal_feature_graph,
    )
    chart_by_id = chart_prior.get("by_id") if isinstance(chart_prior.get("by_id"), Mapping) else {}
    test_by_id = _normalized_mapping(test_scores)
    context_by_id = _normalized_mapping(context_scores)

    profile_name = _select_weight_profile(
        has_test_scores=bool(test_by_id),
        birth_time_confidence=birth_time_confidence,
        answer_consistency=answer_consistency,
    )
    weights = _weight_profile(profile_name)

    final_items: list[dict[str, Any]] = []
    final_score_map: Dict[str, float] = {}
    for archetype in taxonomy.get("archetypes") or []:
        if not isinstance(archetype, Mapping):
            continue
        archetype_id = _safe_text(archetype.get("id"))
        chart_score = _safe_float((chart_by_id.get(archetype_id) or {}).get("score"))
        test_score = _safe_float(test_by_id.get(archetype_id))
        context_score = _safe_float(context_by_id.get(archetype_id))
        if profile_name == "chart_only":
            final_score = chart_score
        else:
            final_score = (
                (chart_score * weights["chart_prior"])
                + (test_score * weights["test_score"])
                + (context_score * weights["context_score"])
            )
        final_score = round(_clamp01(final_score), 4)
        final_score_map[archetype_id] = final_score
        final_items.append(
            {
                "id": archetype_id,
                "label": _safe_text(archetype.get("label_tr")),
                **_archetype_text_payload(archetype),
                "score": final_score,
                "source_split": {
                    "chart_prior": round(chart_score, 4),
                    "test_score": round(test_score, 4),
                    "context_score": round(context_score, 4),
                },
            }
        )

    final_items.sort(key=lambda item: (-_safe_float(item.get("score")), _safe_text(item.get("id"))))
    result_rules = (fusion.get("result_rules") or {}) if isinstance(fusion.get("result_rules"), Mapping) else {}
    top_count = max(int(result_rules.get("top_archetypes") or 3), 1)
    top_archetypes = final_items[:top_count]

    shadow_candidates = [
        item
        for item in final_items
        if _safe_text(item.get("id")) in {"guardian", "depthkeeper", "analyst"}
    ]
    shadow_archetype = shadow_candidates[0] if shadow_candidates else {}

    contradiction = _top_contradiction(contradiction_signatures)
    contradiction_score = _safe_float(contradiction.get("score"))
    contradiction_threshold = _safe_float(result_rules.get("minimum_contradiction_score") or 0.58)
    contradiction_labels = (
        taxonomy.get("contradiction_labels")
        if isinstance(taxonomy.get("contradiction_labels"), Mapping)
        else {}
    )
    if contradiction_score >= contradiction_threshold:
        primary_contradiction = {
            "id": _safe_text(contradiction.get("id")),
            "label": _safe_text(contradiction_labels.get(_safe_text(contradiction.get("id")))),
            "score": round(contradiction_score, 4),
        }
    else:
        primary_contradiction = {}

    chart_confidence = _chart_confidence(birth_time_confidence)
    test_confidence = _test_confidence(answer_consistency, bool(test_by_id))
    if test_by_id:
        global_confidence = round(_clamp01((chart_confidence * 0.45) + (test_confidence * 0.55)), 4)
    else:
        global_confidence = chart_confidence

    return {
        **get_archetype_runtime_versions(),
        "chart_prior": {
            "items": chart_prior.get("items") or [],
            "weight_profile": profile_name,
        },
        "test_scores": [
            {
                "id": item["id"],
                "label": item["label"],
                "score": item["source_split"]["test_score"],
            }
            for item in final_items
            if item["source_split"]["test_score"] > 0
        ],
        "top_archetypes": top_archetypes,
        "shadow_archetype": shadow_archetype,
        "primary_contradiction": primary_contradiction,
        "confidence": {
            "global": global_confidence,
            "chart": chart_confidence,
            "test": test_confidence,
        },
        "slots": _select_slots(final_score_map),
        "debug": {
            "fusion_weights_used": weights,
            "answer_consistency": None if answer_consistency is None else round(_clamp01(answer_consistency), 4),
            "birth_time_confidence": _safe_text(birth_time_confidence) or "exact",
        },
    }
