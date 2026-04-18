from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence


_ROOT = Path(__file__).resolve().parents[3]
_TAXONOMY_PATH = _ROOT / "config" / "classifiers" / "archetype_taxonomy_v2.yaml"
_FUSION_PATH = _ROOT / "config" / "scoring" / "archetype_fusion_v2.yaml"

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
_PRIMITIVE_PHRASES = {
    "self_definition": "kimligini net cizme",
    "inner_structure": "ic duzen kurma",
    "methodical_drive": "adim adim ilerleme",
    "public_refinement": "gorusunu cilalayip gorunur kilma",
    "visible_presence": "dunyanin onunde yer alma",
    "originality_drive": "kalibi bozup yenisini deneme",
    "big_picture_vision": "buyuk resmi gorme",
    "meaningful_expansion": "anlam uzerinden buyume",
    "mental_structuring": "zihni duzenleme",
    "systems_thinking": "parcalari sisteme baglama",
    "tone_sensitivity": "ince tonu ve iklimi okuma",
    "graceful_affection": "sicak bag kurma",
    "relational_security": "iliskide guven omurgasi",
    "network_luck": "insanlar arasinda akis kurma",
    "recharge_through_home": "guvende alanda toparlanma",
    "family_self_reliance": "yakin alani kendi gucuyle tutma",
    "emotional_threshold": "guven esigi yuksek olma",
    "intimacy_depth": "derin yakinlik arama",
    "transformative_bonding": "bag uzerinden donusme",
    "backstage_creation": "perde arkasinda olgunlastirma",
    "creation_luck": "yaratici akisla dogru ani yakalama",
    "push_pull_drive": "gerilimden hareket uretme",
}
_SLOT_LABELS = {
    "primary_identity_spine": "ana kimlik hattin",
    "secondary_balancing_line": "dengeleyici hattin",
    "relational_line": "iliskisel rolun",
    "work_visibility_line": "gorunurluk hattin",
    "shadow_protection_line": "koruma hattin",
}
_FAMILY_LABELS = {
    "structure_preference": "yapi tercihi",
    "responsibility_style": "sorumluluk alma bicimi",
    "execution_style": "uygulama ritmi",
    "future_pull": "gelecege cekilme hali",
    "novelty_vs_structure": "yenilik ve yapi dengesi",
    "meaning_orientation": "anlam ekseni",
    "mental_precision": "zihinsel hassasiyet",
    "decision_style": "karar bicimi",
    "error_avoidance": "hata onleme",
    "social_flow": "sosyal akis",
    "repair_style": "onarim tarzi",
    "bonding_style": "bag kurma bicimi",
    "stress_regulation": "stres duzenleme",
    "safety_needs": "guven ihtiyaci",
    "closeness_boundary": "yakinlik esigi",
    "transformational_bonding": "donusturucu bag",
    "trust_depth": "guven derinligi",
    "visibility_preference": "gorunurluk istegi",
    "expression_style": "ifade dili",
    "audience_energy": "izleyici enerjisi",
    "action_bias": "harekete gecme eglimi",
    "conflict_activation": "gerilimde hiz alma",
    "change_tolerance": "degisime tolerans",
}


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
        "engine_version": "archetype_profile_v2",
        "taxonomy_version": f"archetype_taxonomy_v2:{_safe_text(taxonomy.get('version')) or 'unknown'}",
        "fusion_version": f"archetype_fusion_v2:{_safe_text(fusion.get('version')) or 'unknown'}",
    }


def _archetype_text_payload(archetype: Mapping[str, Any]) -> Dict[str, str]:
    payload: Dict[str, str] = {}
    for key in _TEXT_FIELDS:
        value = _safe_text(archetype.get(key))
        if value:
            payload[key] = value
    return payload


def _primitive_lookup(
    primitive_scores: Mapping[str, Any] | None,
) -> Dict[str, Dict[str, Any]]:
    payload = primitive_scores if isinstance(primitive_scores, Mapping) else {}
    items = (
        payload.get("primitive_scores")
        if isinstance(payload.get("primitive_scores"), Sequence)
        else []
    )
    return {
        _safe_text(item.get("primitive_id")): dict(item)
        for item in items
        if isinstance(item, Mapping) and _safe_text(item.get("primitive_id"))
    }


def _identity_spine(
    master_selector: Mapping[str, Any] | None,
) -> Dict[str, Dict[str, Any]]:
    payload = master_selector if isinstance(master_selector, Mapping) else {}
    spine = (
        payload.get("identity_spine")
        if isinstance(payload.get("identity_spine"), Mapping)
        else {}
    )
    return {
        _safe_text(slot): dict(value)
        for slot, value in spine.items()
        if isinstance(value, Mapping) and _safe_text(slot)
    }


def _top_contradiction(
    contradiction_signatures: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    payload = (
        contradiction_signatures
        if isinstance(contradiction_signatures, Mapping)
        else {}
    )
    items = (
        payload.get("top_signatures")
        if isinstance(payload.get("top_signatures"), Sequence)
        else []
    )
    for item in items:
        if isinstance(item, Mapping):
            return dict(item)
    items = (
        payload.get("signatures")
        if isinstance(payload.get("signatures"), Sequence)
        else []
    )
    for item in items:
        if isinstance(item, Mapping):
            return dict(item)
    return {}


def _public_private(
    natal_feature_graph: Mapping[str, Any] | None,
) -> tuple[float, float, float]:
    payload = natal_feature_graph if isinstance(natal_feature_graph, Mapping) else {}
    split = (
        payload.get("public_private_split")
        if isinstance(payload.get("public_private_split"), Mapping)
        else {}
    )
    public_score = _clamp01(split.get("public_score"))
    private_score = _clamp01(split.get("private_score"))
    balance = 1.0 - abs(public_score - private_score)
    return public_score, private_score, _clamp01(balance)


def _slot_alignment_bonus(
    archetype: Mapping[str, Any],
    spine: Mapping[str, Mapping[str, Any]],
) -> tuple[float, dict[str, float]]:
    primitive_ids = set((archetype.get("primitive_weights") or {}).keys())
    slot_biases = {
        _safe_text(slot)
        for slot in archetype.get("slot_biases") or []
        if _safe_text(slot)
    }
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
    score = _clamp01(contradiction.get("score"))
    if score < 0.62:
        return 0.0, contradiction_id
    bonus = ((score - 0.62) / 0.38) * 0.04
    return round(_clamp01(bonus), 4), contradiction_id


def _public_private_bonus(
    archetype: Mapping[str, Any],
    *,
    public_score: float,
    private_score: float,
    balance_score: float,
) -> float:
    slot_biases = {
        _safe_text(slot)
        for slot in archetype.get("slot_biases") or []
        if _safe_text(slot)
    }
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
        primitive_weights = (
            archetype.get("primitive_weights")
            if isinstance(archetype.get("primitive_weights"), Mapping)
            else {}
        )
        base = 0.0
        contributing_primitives: list[dict[str, Any]] = []
        for primitive_id, weight in primitive_weights.items():
            primitive_key = _safe_text(primitive_id)
            if not primitive_key:
                continue
            primitive = primitives.get(primitive_key, {})
            score = _clamp01(primitive.get("score"))
            contribution = score * _safe_float(weight)
            base += contribution
            if contribution > 0:
                contributing_primitives.append(
                    {
                        "primitive_id": primitive_key,
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

    scored.sort(
        key=lambda item: (-_safe_float(item.get("score")), _safe_text(item.get("id")))
    )
    return {
        "engine_version": "archetype_chart_prior_v2",
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
    weights = (
        (_fusion().get("weights") or {})
        if isinstance(_fusion().get("weights"), Mapping)
        else {}
    )
    if name == "chart_only":
        return {"chart_prior": 1.0, "test_score": 0.0, "context_score": 0.0}
    payload = weights.get(name) if isinstance(weights.get(name), Mapping) else {}
    return {
        "chart_prior": _safe_float(payload.get("chart_prior")),
        "test_score": _safe_float(payload.get("test_score")),
        "context_score": _safe_float(payload.get("context_score")),
    }


# Birth time mode: `birth_time_confidence` inputunun kanonik üç-değerli özetine
# map'lendiği TEK yer. Audit snapshot + explain katmanında bu alana bağlanılır.
# Faz 1 PR 4'te implicit olan state (`chart_only weight_profile`, softening
# trigger'ları) explicit metadata'ya dönüşür.
_BIRTH_TIME_MODE_BY_CONFIDENCE: Mapping[str, str] = {
    "exact": "exact",
    "verified": "exact",
    "rounded": "rounded",
    "estimated": "rounded",
    "unknown": "unknown",
    "missing": "unknown",
    "approx": "unknown",
    "low": "unknown",
}


def birth_time_mode(birth_time_confidence: str) -> str:
    """`birth_time_confidence` → kanonik `{exact, rounded, unknown}` mode.

    Tek kaynak. Bilinmeyen/eşleşmeyen string → `"exact"` (muhafazakar default,
    mevcut `_chart_confidence` 0.7 baseline'ı ile tutarlı).
    """
    normalized = _safe_text(birth_time_confidence).lower()
    return _BIRTH_TIME_MODE_BY_CONFIDENCE.get(normalized, "exact")


def _chart_confidence(birth_time_confidence: str) -> float:
    config = (
        ((_fusion().get("confidence") or {}).get("chart"))
        if isinstance(((_fusion().get("confidence") or {}).get("chart")), Mapping)
        else {}
    )
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


def _normalized_weighted_average(
    weights: Mapping[str, Any] | None,
    values: Mapping[str, Any] | None,
) -> float:
    weight_map = weights if isinstance(weights, Mapping) else {}
    value_map = values if isinstance(values, Mapping) else {}
    total_weight = 0.0
    total = 0.0
    for key, weight in weight_map.items():
        item_key = _safe_text(key)
        item_weight = max(_safe_float(weight), 0.0)
        if not item_key or item_weight <= 0:
            continue
        total += _clamp01(value_map.get(item_key)) * item_weight
        total_weight += item_weight
    if total_weight <= 0:
        return 0.0
    return round(_clamp01(total / total_weight), 4)


def _slot_fit_score(
    slot_biases: Sequence[Any] | None,
    spine: Mapping[str, Mapping[str, Any]],
) -> float:
    slots = [_safe_text(item) for item in slot_biases or [] if _safe_text(item)]
    if not slots:
        return 0.0
    values = [
        _clamp01((spine.get(slot) or {}).get("confidence"))
        for slot in slots
        if isinstance(spine.get(slot), Mapping)
    ]
    if not values:
        return 0.0
    return round(sum(values) / len(values), 4)


def _contradiction_fit_score(
    contradiction: Mapping[str, Any],
    supported: Sequence[Any] | None,
) -> float:
    contradiction_id = _safe_text(contradiction.get("id"))
    if not contradiction_id:
        return 0.0
    if contradiction_id not in {
        _safe_text(item) for item in supported or [] if _safe_text(item)
    }:
        return 0.0
    return round(_clamp01(_safe_float(contradiction.get("score"))), 4)


def _public_private_fit_score(
    preference: str,
    *,
    public_score: float,
    private_score: float,
    balance_score: float,
) -> float:
    normalized = _safe_text(preference).lower()
    if normalized == "public":
        return round(public_score, 4)
    if normalized == "private":
        return round(private_score, 4)
    return round(balance_score, 4)


def _top_core_family_gap(final_items: Sequence[Mapping[str, Any]]) -> float:
    if len(final_items) < 2:
        return 1.0
    return round(
        _safe_float(final_items[0].get("score")) - _safe_float(final_items[1].get("score")),
        4,
    )


def _subprofile_selection_weights() -> Dict[str, float]:
    payload = (
        (_fusion().get("subprofile_weights") or {})
        if isinstance(_fusion().get("subprofile_weights"), Mapping)
        else {}
    )
    return {
        "core_signal": _safe_float(payload.get("core_signal")) or 0.22,
        "primitive_signal": _safe_float(payload.get("primitive_signal")) or 0.33,
        "question_signal": _safe_float(payload.get("question_signal")) or 0.20,
        "slot_signal": _safe_float(payload.get("slot_signal")) or 0.10,
        "contradiction_signal": _safe_float(payload.get("contradiction_signal")) or 0.07,
        "public_private_signal": _safe_float(payload.get("public_private_signal")) or 0.08,
    }


def _select_subprofile(
    *,
    archetype: Mapping[str, Any],
    core_score: float,
    primitives: Mapping[str, Mapping[str, Any]],
    family_scores: Mapping[str, float],
    spine: Mapping[str, Mapping[str, Any]],
    contradiction: Mapping[str, Any],
    public_score: float,
    private_score: float,
    balance_score: float,
) -> Dict[str, Any]:
    weight_profile = _subprofile_selection_weights()
    primitive_values = {
        key: _clamp01(value.get("score"))
        for key, value in primitives.items()
        if isinstance(value, Mapping)
    }
    candidates: list[dict[str, Any]] = []
    for entry in archetype.get("subprofiles") or []:
        if not isinstance(entry, Mapping):
            continue
        primitive_signal = _normalized_weighted_average(
            entry.get("primitive_weights"),
            primitive_values,
        )
        question_signal = _normalized_weighted_average(
            entry.get("question_family_weights"),
            family_scores,
        )
        slot_signal = _slot_fit_score(entry.get("slot_biases"), spine)
        contradiction_signal = _contradiction_fit_score(
            contradiction,
            entry.get("supports_contradictions"),
        )
        public_private_signal = _public_private_fit_score(
            _safe_text(entry.get("public_private_preference")) or "balanced",
            public_score=public_score,
            private_score=private_score,
            balance_score=balance_score,
        )
        score = _clamp01(
            (core_score * weight_profile["core_signal"])
            + (primitive_signal * weight_profile["primitive_signal"])
            + (question_signal * weight_profile["question_signal"])
            + (slot_signal * weight_profile["slot_signal"])
            + (contradiction_signal * weight_profile["contradiction_signal"])
            + (public_private_signal * weight_profile["public_private_signal"])
        )
        candidates.append(
            {
                "id": _safe_text(entry.get("id")),
                "label_tr": _safe_text(entry.get("label_tr")),
                "flavor_tr": _safe_text(entry.get("flavor_tr")),
                "gift_focus_tr": _safe_text(entry.get("gift_focus_tr")),
                "growth_edge_tr": _safe_text(entry.get("growth_edge_tr")),
                "differentiator_tr": _safe_text(entry.get("differentiator_tr")),
                "question_families": [
                    _safe_text(key)
                    for key in (entry.get("question_family_weights") or {}).keys()
                    if _safe_text(key)
                ],
                "score": round(score, 4),
                "signals": {
                    "primitive": primitive_signal,
                    "question": question_signal,
                    "slot": slot_signal,
                    "contradiction": contradiction_signal,
                    "public_private": public_private_signal,
                },
            }
        )
    candidates.sort(
        key=lambda item: (-_safe_float(item.get("score")), _safe_text(item.get("id")))
    )
    selected = candidates[0] if candidates else {}
    return {
        "selected": selected,
        "candidates": candidates,
    }


def _mixin_dimension_lookup() -> Dict[str, Dict[str, Any]]:
    payload = (
        _taxonomy().get("mixin_dimensions")
        if isinstance(_taxonomy().get("mixin_dimensions"), Sequence)
        else []
    )
    return {
        _safe_text(item.get("id")): dict(item)
        for item in payload
        if isinstance(item, Mapping) and _safe_text(item.get("id"))
    }


def _mixin_value_label(dimension_id: str, value_id: str) -> str:
    dimension = _mixin_dimension_lookup().get(dimension_id, {})
    values = dimension.get("values") if isinstance(dimension.get("values"), Mapping) else {}
    return _safe_text(values.get(value_id)) or value_id.replace("_", " ")


def _build_mixins(
    *,
    primitives: Mapping[str, Mapping[str, Any]],
    family_scores: Mapping[str, float],
    contradiction: Mapping[str, Any],
    public_score: float,
    private_score: float,
    balance_score: float,
) -> list[dict[str, Any]]:
    primitive_values = {
        key: _clamp01(value.get("score"))
        for key, value in primitives.items()
        if isinstance(value, Mapping)
    }
    dimensions = _mixin_dimension_lookup()

    def score(*keys: str) -> float:
        if not keys:
            return 0.0
        return round(
            sum(_clamp01(primitive_values.get(key)) for key in keys) / len(keys),
            4,
        )

    mixin_states: list[tuple[str, str, float]] = []

    public_signal = max(public_score, score("visible_presence", "public_refinement", "network_luck"))
    backstage_signal = max(private_score, score("backstage_creation", "intimacy_depth", "recharge_through_home"))
    if public_signal - backstage_signal > 0.12:
        mixin_states.append(("visibility_mode", "broadcast", public_signal))
    elif backstage_signal - public_signal > 0.08:
        mixin_states.append(("visibility_mode", "backstage", backstage_signal))
    else:
        mixin_states.append(("visibility_mode", "curated", max(balance_score, (public_signal + backstage_signal) / 2)))

    open_signal = max(
        _clamp01(1.0 - primitive_values.get("emotional_threshold", 0.0)),
        _clamp01((family_scores.get("bonding_style", 0.0) + family_scores.get("social_flow", 0.0)) / 2),
    )
    guarded_signal = max(
        score("emotional_threshold", "relational_security", "intimacy_depth"),
        _clamp01((family_scores.get("trust_depth", 0.0) + family_scores.get("closeness_boundary", 0.0)) / 2),
    )
    if open_signal - guarded_signal > 0.14:
        mixin_states.append(("relational_threshold", "open", open_signal))
    elif guarded_signal - open_signal > 0.10:
        mixin_states.append(("relational_threshold", "guarded", guarded_signal))
    else:
        mixin_states.append(("relational_threshold", "selective", max(open_signal, guarded_signal)))

    deliberate_signal = max(
        score("mental_structuring", "methodical_drive", "inner_structure"),
        _clamp01((family_scores.get("decision_style", 0.0) + family_scores.get("error_avoidance", 0.0)) / 2),
    )
    rapid_signal = max(
        score("push_pull_drive", "self_definition", "visible_presence"),
        _clamp01((family_scores.get("action_bias", 0.0) + family_scores.get("conflict_activation", 0.0)) / 2),
    )
    if deliberate_signal - rapid_signal > 0.12:
        mixin_states.append(("decision_tempo", "deliberate", deliberate_signal))
    elif rapid_signal - deliberate_signal > 0.10:
        mixin_states.append(("decision_tempo", "rapid", rapid_signal))
    else:
        mixin_states.append(("decision_tempo", "balanced", max(deliberate_signal, rapid_signal)))

    structure_signal = max(
        score("inner_structure", "methodical_drive", "mental_structuring"),
        _clamp01(family_scores.get("structure_preference")),
    )
    freedom_signal = max(
        score("originality_drive", "big_picture_vision", "meaningful_expansion"),
        _clamp01((family_scores.get("novelty_vs_structure", 0.0) + family_scores.get("future_pull", 0.0)) / 2),
    )
    if structure_signal - freedom_signal > 0.12:
        mixin_states.append(("structure_freedom_style", "structure_led", structure_signal))
    elif freedom_signal - structure_signal > 0.12:
        mixin_states.append(("structure_freedom_style", "freedom_led", freedom_signal))
    else:
        mixin_states.append(("structure_freedom_style", "hybrid", max(structure_signal, freedom_signal)))

    stabilize_signal = max(
        score("recharge_through_home", "family_self_reliance", "relational_security"),
        _clamp01((family_scores.get("stress_regulation", 0.0) + family_scores.get("safety_needs", 0.0)) / 2),
    )
    observe_signal = max(
        score("mental_structuring", "tone_sensitivity", "systems_thinking"),
        _clamp01((family_scores.get("mental_precision", 0.0) + family_scores.get("decision_style", 0.0)) / 2),
    )
    combustive_signal = max(
        score("push_pull_drive", "visible_presence", "self_definition"),
        _clamp01((family_scores.get("conflict_activation", 0.0) + family_scores.get("action_bias", 0.0)) / 2),
    )
    if stabilize_signal >= observe_signal and stabilize_signal >= combustive_signal:
        mixin_states.append(("stress_protection_mode", "stabilizing", stabilize_signal))
    elif observe_signal >= combustive_signal:
        mixin_states.append(("stress_protection_mode", "observing", observe_signal))
    else:
        mixin_states.append(("stress_protection_mode", "combustive", combustive_signal))

    contradiction_id = _safe_text(contradiction.get("id"))
    if contradiction_id == "composure_vs_internal_pressure" or private_score - public_score > 0.16:
        mixin_states.append(("outer_inner_rhythm", "steady_inside", max(private_score, _safe_float(contradiction.get("score")))))
    elif public_score - private_score > 0.16:
        mixin_states.append(("outer_inner_rhythm", "expressive_outside", public_score))
    else:
        mixin_states.append(("outer_inner_rhythm", "matched", balance_score))

    mixins: list[dict[str, Any]] = []
    for dimension_id, value_id, value_score in mixin_states:
        dimension = dimensions.get(dimension_id, {})
        mixins.append(
            {
                "id": dimension_id,
                "label_tr": _safe_text(dimension.get("label_tr")) or dimension_id.replace("_", " "),
                "value_id": value_id,
                "value_label_tr": _mixin_value_label(dimension_id, value_id),
                "score": round(_clamp01(value_score), 4),
            }
        )
    return mixins


def _top_weighted_primitive(
    primitive_weights: Mapping[str, Any] | None,
    primitives: Mapping[str, Mapping[str, Any]],
) -> str:
    best_id = ""
    best_score = -1.0
    weight_map = primitive_weights if isinstance(primitive_weights, Mapping) else {}
    for primitive_id, weight in weight_map.items():
        primitive_key = _safe_text(primitive_id)
        if not primitive_key:
            continue
        score = _clamp01((primitives.get(primitive_key) or {}).get("score")) * max(_safe_float(weight), 0.0)
        if score > best_score:
            best_score = score
            best_id = primitive_key
    return best_id


def _top_weighted_primitive_ids(
    primitive_weights: Mapping[str, Any] | None,
    primitives: Mapping[str, Mapping[str, Any]],
    *,
    limit: int = 3,
) -> list[str]:
    weight_map = primitive_weights if isinstance(primitive_weights, Mapping) else {}
    scored: list[tuple[str, float]] = []
    for primitive_id, weight in weight_map.items():
        primitive_key = _safe_text(primitive_id)
        if not primitive_key:
            continue
        score = _clamp01((primitives.get(primitive_key) or {}).get("score")) * max(
            _safe_float(weight),
            0.0,
        )
        if score <= 0:
            continue
        scored.append((primitive_key, score))
    scored.sort(key=lambda item: (-item[1], item[0]))
    return [primitive_id for primitive_id, _score in scored[: max(limit, 1)]]


def _primitive_phrase(primitive_id: str) -> str:
    return _PRIMITIVE_PHRASES.get(primitive_id, primitive_id.replace("_", " "))


def _join_tr(parts: Sequence[str]) -> str:
    cleaned = [_safe_text(item) for item in parts if _safe_text(item)]
    if not cleaned:
        return ""
    if len(cleaned) == 1:
        return cleaned[0]
    if len(cleaned) == 2:
        return f"{cleaned[0]} ve {cleaned[1]}"
    return f"{', '.join(cleaned[:-1])} ve {cleaned[-1]}"


def _join_sentences(parts: Sequence[str]) -> str:
    return " ".join(_safe_text(item) for item in parts if _safe_text(item)).strip()


def _ensure_sentence(text: str) -> str:
    cleaned = _safe_text(text)
    if not cleaned:
        return ""
    if cleaned[-1] in ".!?":
        return cleaned
    return f"{cleaned}."


def _contradiction_personal_line(contradiction: Mapping[str, Any]) -> str:
    contradiction_id = _safe_text(contradiction.get("id"))
    lines = {
        "structure_vs_originality": "Sende bir yan duzen kurmak isterken diger yan daha ozgur ve yeni bir yol acmak istiyor.",
        "visibility_vs_private_preparation": "Gorunmek istiyorsun ama bir seyi paylasmadan once icerde toparlama ihtiyacin da guclu.",
        "closeness_vs_threshold": "Yakinlik istiyorsun ama guveni kolay vermiyorsun.",
        "composure_vs_internal_pressure": "Disaridan toplu gorunurken iceride cok daha fazla yuk tasiyabiliyorsun.",
        "speed_vs_control": "Bir yanin hizlanmak isterken diger yanin once kontrol etmek istiyor.",
    }
    return _safe_text(lines.get(contradiction_id))


def _subprofile_personal_line(
    selected_subprofile: Mapping[str, Any],
    *,
    soften_subprofile: bool = False,
) -> str:
    label = _safe_text(selected_subprofile.get("label_tr"))
    flavor = _ensure_sentence(_safe_text(selected_subprofile.get("flavor_tr")))
    if not label and not flavor:
        return ""
    if soften_subprofile:
        if flavor:
            return f"Senin haritanda bu tema simdilik daha cok soyle calisiyor: {flavor}"
        return f"Senin haritanda bu tema simdilik daha yumusak bir {label.lower()} tonuna yakin duruyor."
    if label and flavor:
        return f"Senin versiyonunda bu arketip daha cok {label.lower()} tarafiyla aciliyor. {flavor}"
    if flavor:
        return f"Senin versiyonunda bu arketip soyle calisiyor: {flavor}"
    return f"Senin versiyonunda bu arketip daha cok {label.lower()} tarafina kayiyor."


def _primitive_personal_line(top_primitive_ids: Sequence[str]) -> str:
    primitive_reason = _join_tr([_primitive_phrase(item) for item in top_primitive_ids[:3]])
    if not primitive_reason:
        return ""
    return f"Bu profili en cok {primitive_reason} tarafin besliyor."


def _visibility_personal_line(value: str) -> str:
    value_id = _safe_text(value)
    lines = {
        "broadcast": "Kendini gorunur alanda rahat gosterebiliyorsun.",
        "curated": "Kendini gostermeden once nasil gorunecegini secmeyi seviyorsun.",
        "backstage": "Kendini hemen ortaya koymaktan cok once icerde hazirlanmayi tercih ediyorsun.",
    }
    return _safe_text(lines.get(value_id))


def _relationship_personal_line(value: str) -> str:
    value_id = _safe_text(value)
    lines = {
        "open": "Iliskide duygunu hizli gosteren tarafta olabilirsin.",
        "selective": "Iliskide acilirsin ama once karsindakini tartarsin.",
        "guarded": "Iliskide guveni yavas kurar, once emin olmak istersin.",
    }
    return _safe_text(lines.get(value_id))


def _decision_personal_line(tempo_value: str, structure_value: str) -> str:
    tempo_id = _safe_text(tempo_value)
    structure_id = _safe_text(structure_value)
    tempo_map = {
        "deliberate": "Karar alirken kolay kolay acele etmezsin.",
        "balanced": "Karar alirken ne fazla aceleci ne de fazla yavas kalirsin.",
        "rapid": "Karar aninda hiz kazanman kolaydir.",
    }
    structure_map = {
        "structure_led": "Icin rahat etsin diye bir duzen kurmak istersin.",
        "hybrid": "Hem duzen hem esneklik senin icin ayni anda onemlidir.",
        "freedom_led": "Seni en cok hareket ettiren sey alan ve ozgurluk hissidir.",
    }
    return _join_sentences(
        [
            _safe_text(tempo_map.get(tempo_id)),
            _safe_text(structure_map.get(structure_id)),
        ]
    )


def _stress_personal_line(value: str) -> str:
    value_id = _safe_text(value)
    lines = {
        "stabilizing": "Zorlandiginda once sakinlestirmeye ve toparlamaya gecersin.",
        "observing": "Zorlandiginda bir adim geri cekilip olan biteni anlamaya calisirsin.",
        "combustive": "Zorlandiginda enerjin bir anda yukselebilir ve tepkin hizlanabilir.",
    }
    return _safe_text(lines.get(value_id))


def _rhythm_personal_line(value: str) -> str:
    value_id = _safe_text(value)
    lines = {
        "steady_inside": "Disaridan daha sakin gorunup iceride cok daha yogun yasayabilirsin.",
        "matched": "Iceride neysen disariya da benzer bir ritimle yansirsin.",
        "expressive_outside": "Icinde dogan sey disari hizli yansima egilimindedir.",
    }
    return _safe_text(lines.get(value_id))


def _primary_slot_for_item(archetype_id: str, slots: Mapping[str, Any]) -> str:
    for slot_name, assigned_id in slots.items():
        if _safe_text(assigned_id) == archetype_id:
            return slot_name
    return ""


def _contradiction_line(
    contradiction: Mapping[str, Any],
    *,
    supported: Sequence[Any] | None,
) -> str:
    contradiction_id = _safe_text(contradiction.get("id"))
    if not contradiction_id:
        return ""
    supported_ids = {_safe_text(item) for item in supported or [] if _safe_text(item)}
    if contradiction_id not in supported_ids:
        return ""
    label = _safe_text((_taxonomy().get("contradiction_labels") or {}).get(contradiction_id))
    if not label:
        return ""
    return f"Burada {label.lower()}"


def _slot_line(slot_name: str) -> str:
    label = _SLOT_LABELS.get(slot_name, slot_name.replace("_", " "))
    if not label:
        return ""
    return f"Bu ton en cok {label} icinde belirginlesiyor."


def _mixins_by_id(mixins: Sequence[Mapping[str, Any]]) -> Dict[str, Mapping[str, Any]]:
    return {
        _safe_text(item.get("id")): item
        for item in mixins
        if isinstance(item, Mapping) and _safe_text(item.get("id"))
    }


def _build_differentiators(
    *,
    selected_subprofile: Mapping[str, Any],
    top_primitive_id: str,
    mixins: Sequence[Mapping[str, Any]],
    slot_name: str,
    soften_subprofile: bool = False,
) -> list[str]:
    mixin_lookup = _mixins_by_id(mixins)
    lead_line = _safe_text(selected_subprofile.get("differentiator_tr"))
    if soften_subprofile:
        lead_line = _safe_text(selected_subprofile.get("gift_focus_tr")) or _safe_text(
            selected_subprofile.get("flavor_tr")
        )
        if lead_line:
            lead_line = f"Bu profil sende simdilik su tarafa yakin duruyor: {lead_line}"
    differentiators = [
        lead_line,
        f"Bu profili ayiran sey, {_primitive_phrase(top_primitive_id)} tarafinin kolay kolay sonmemesi."
        if top_primitive_id
        else "",
        f"Gorunurlukte daha cok {_safe_text((mixin_lookup.get('visibility_mode') or {}).get('value_label_tr')).lower()} bir tarz calisiyor."
        if mixin_lookup.get("visibility_mode")
        else "",
        _slot_line(slot_name),
    ]
    return [item for item in differentiators if _safe_text(item)]


def _assemble_copy_blocks(
    *,
    archetype: Mapping[str, Any],
    selected_subprofile: Mapping[str, Any],
    mixins: Sequence[Mapping[str, Any]],
    contradiction: Mapping[str, Any],
    top_primitive_ids: Sequence[str],
    slot_name: str,
    public_score: float,
    private_score: float,
    soften_subprofile: bool = False,
    include_mixin_language: bool = True,
) -> Dict[str, str]:
    core_label = _safe_text(archetype.get("label_tr")) or "Arketip"
    subprofile_label = _safe_text(selected_subprofile.get("label_tr"))
    flavor = _safe_text(selected_subprofile.get("flavor_tr"))
    gift_focus = _safe_text(selected_subprofile.get("gift_focus_tr"))
    growth_edge = _safe_text(selected_subprofile.get("growth_edge_tr"))
    contradiction_line = _contradiction_line(
        contradiction,
        supported=selected_subprofile.get("supports_contradictions") or archetype.get("supports_contradictions"),
    )
    contradiction_personal = _contradiction_personal_line(contradiction)
    slot_line = _slot_line(slot_name)
    primitive_line = _primitive_personal_line(top_primitive_ids)
    mixin_lookup = _mixins_by_id(mixins)
    visibility_id = _safe_text((mixin_lookup.get("visibility_mode") or {}).get("value_id"))
    relational_id = _safe_text((mixin_lookup.get("relational_threshold") or {}).get("value_id"))
    tempo_id = _safe_text((mixin_lookup.get("decision_tempo") or {}).get("value_id"))
    structure_id = _safe_text((mixin_lookup.get("structure_freedom_style") or {}).get("value_id"))
    stress_id = _safe_text((mixin_lookup.get("stress_protection_mode") or {}).get("value_id"))
    rhythm_id = _safe_text((mixin_lookup.get("outer_inner_rhythm") or {}).get("value_id"))
    public_private_line = (
        "Insanlar once daha gorunur ve disariya donuk tarafini fark ediyor."
        if public_score - private_score > 0.12
        else "Bir seyi hemen gostermeden once icerde toparlamayi tercih ediyorsun."
        if private_score - public_score > 0.12
        else "Iceride neysen disariya da benzer bir ritimle yansiyorsun."
    )
    primitive_reason = _join_tr([_primitive_phrase(item) for item in top_primitive_ids[:3]])
    contradiction_label = _safe_text(
        ((_taxonomy().get("contradiction_labels") or {}).get(_safe_text(contradiction.get("id"))))
    ).rstrip(".!?")
    plain_summary = _join_sentences(
        [
            f"Bu haritada {core_label.lower()} arketipi one cikiyor."
            if core_label
            else "",
            f"Bunun arkasinda en cok {primitive_reason} var." if primitive_reason else "",
            contradiction_personal,
            f"Merkezde su gerilim calisiyor: {contradiction_label.lower()}."
            if contradiction_label
            and not contradiction_personal
            else "",
            f"Bu daha cok {_SLOT_LABELS.get(slot_name, slot_name.replace('_', ' ')).lower()} tarafinda toplaniyor."
            if slot_name
            else "",
        ]
    )
    reasoning_summary = _join_sentences(
        [
            f"Harita bu arketipi ozellikle {primitive_reason} uzerinden buyutuyor."
            if primitive_reason
            else "",
            contradiction_personal or contradiction_line.replace("Burada ", "")
            if contradiction_personal or contradiction_line
            else "",
            public_private_line,
        ]
    )
    portrait_parts = [
        _safe_text(archetype.get("portrait_tr")),
        _subprofile_personal_line(
            selected_subprofile,
            soften_subprofile=soften_subprofile,
        ),
        contradiction_personal or contradiction_line,
        primitive_line,
        public_private_line,
    ]
    gift_parts = [
        _safe_text(archetype.get("gift_tr")),
        f"Senin versiyonunda bunun en belirgin yani su: {_ensure_sentence(gift_focus)}"
        if gift_focus
        else "",
        _decision_personal_line(tempo_id, structure_id)
        if include_mixin_language and (tempo_id or structure_id)
        else "",
    ]
    fear_parts = [
        _safe_text(archetype.get("fear_tr")),
        _stress_personal_line(stress_id)
        if include_mixin_language and stress_id
        else "",
    ]
    shadow_parts = [
        _safe_text(archetype.get("shadow_tr")),
        _rhythm_personal_line(rhythm_id)
        if include_mixin_language and rhythm_id
        else "",
    ]
    relationship_parts = [
        _safe_text(archetype.get("relationship_tr")),
        _relationship_personal_line(relational_id)
        if include_mixin_language and relational_id
        else "",
    ]
    work_parts = [
        _safe_text(archetype.get("work_style_tr")),
        _visibility_personal_line(visibility_id)
        if include_mixin_language and visibility_id
        else "",
        slot_line,
    ]
    growth_parts = [
        _safe_text(archetype.get("growth_tr")),
        f"Senin versiyonunda burada gelisim dersi su: {_ensure_sentence(growth_edge)}"
        if growth_edge
        else "",
        _decision_personal_line(tempo_id, structure_id)
        if include_mixin_language and (tempo_id or structure_id)
        else "",
    ]

    def join(parts: Sequence[str]) -> str:
        return " ".join(_safe_text(item) for item in parts if _safe_text(item)).strip()

    return {
        "motto_tr": join(
            [
                _safe_text(archetype.get("motto_tr")),
                f"Bu sende {subprofile_label.lower()} tonu ile okunuyor."
                if subprofile_label and not soften_subprofile
                else f"Bu sende simdilik {subprofile_label.lower()} tonuna yaklasiyor."
                if subprofile_label
                else "",
            ]
        ),
        "plain_summary_tr": plain_summary,
        "reasoning_tr": reasoning_summary,
        "portrait_tr": join(portrait_parts),
        "gift_tr": join(gift_parts),
        "fear_tr": join(fear_parts),
        "shadow_tr": join(shadow_parts),
        "relationship_tr": join(relationship_parts),
        "work_style_tr": join(work_parts),
        "growth_tr": join(growth_parts),
        "flavor_tr": flavor,
    }


def _copy_variant(
    *,
    archetype_id: str,
    subprofile_id: str,
    mixins: Sequence[Mapping[str, Any]],
) -> str:
    mixin_lookup = _mixins_by_id(mixins)
    visibility = _safe_text((mixin_lookup.get("visibility_mode") or {}).get("value_id")) or "neutral"
    tempo = _safe_text((mixin_lookup.get("decision_tempo") or {}).get("value_id")) or "balanced"
    stress = _safe_text((mixin_lookup.get("stress_protection_mode") or {}).get("value_id")) or "steady"
    return ":".join([archetype_id or "unknown", subprofile_id or "default", visibility, tempo, stress])


def _tie_break_key(
    *,
    item: Mapping[str, Any],
    subprofile_selections: Mapping[str, Mapping[str, Any]],
    top_contradiction_id: str,
) -> tuple[float, float, int, float, str]:
    """Primary archetype sort key.

    Faz 1 PR 3 tie-break chain (strict-tie deterministik re-rank):

      1. -score          (fused score desc)
      2. -chart_prior    (astro evidence desc)
      3. -contradiction_support_match  (1 if supports top contradiction else 0)
      4. -subprofile_gap (daha net subprofile ayrımı öne)
      5. id_alpha        (son deterministic fallback)

    Signal roles:
      - All five are ranking signals (affect primary order).
      - #1 dominates; #2-4 only break strict ties at rounded precision.
      - #5 guarantees determinism across runs.
    """
    score = _safe_float(item.get("score"))
    source_split = item.get("source_split") if isinstance(item.get("source_split"), Mapping) else {}
    chart_prior = _safe_float(source_split.get("chart_prior"))

    archetype = item.get("core_archetype") if isinstance(item.get("core_archetype"), Mapping) else {}
    supports = {
        _safe_text(x)
        for x in (archetype.get("supports_contradictions") or [])
        if _safe_text(x)
    }
    supports_top = 1 if top_contradiction_id and top_contradiction_id in supports else 0

    archetype_id = _safe_text(item.get("id"))
    selection = subprofile_selections.get(archetype_id) if isinstance(subprofile_selections.get(archetype_id), Mapping) else {}
    candidates = selection.get("candidates") if isinstance(selection.get("candidates"), Sequence) else []
    if len(candidates) >= 2:
        gap = _safe_float(candidates[0].get("score")) - _safe_float(candidates[1].get("score"))
    else:
        gap = 1.0

    return (-score, -chart_prior, -supports_top, -gap, archetype_id)


def _build_contradiction_support_lookup(
    taxonomy: Mapping[str, Any],
) -> Dict[str, set[str]]:
    """Taxonomy'den {archetype_id → supports_contradictions set} map kurar."""
    lookup: Dict[str, set[str]] = {}
    for archetype in taxonomy.get("archetypes") or []:
        if not isinstance(archetype, Mapping):
            continue
        archetype_id = _safe_text(archetype.get("id"))
        if not archetype_id:
            continue
        lookup[archetype_id] = {
            _safe_text(x)
            for x in (archetype.get("supports_contradictions") or [])
            if _safe_text(x)
        }
    return lookup


def _select_shadow_archetype(
    *,
    final_items: Sequence[Mapping[str, Any]],
    primary_top_ids: set[str],
    top_contradiction_id: str,
    supports_lookup: Mapping[str, set[str]],
    fallback_ids: Sequence[str] = ("guardian", "depthkeeper", "analyst"),
) -> Dict[str, Any]:
    """Shadow archetype seçimi — contradiction-driven, primary ranking'den ayrı.

    Signal roles (Faz 1 PR 3 role taxonomy):
      - Shadow selection is contradiction-driven and shadow-only.
      - Uses: top_contradiction_id + taxonomy supports_contradictions mapping.
      - Does NOT affect: primary ranking, confidence, subprofile.
      - Fallback: hardcoded safety set (backward-compat).

    Algorithm:
      1. If top_contradiction_id is set:
         a. Filter archetypes whose supports_contradictions includes it.
         b. Prefer those NOT in primary_top_ids ("other side" semantic).
         c. Return highest-score supporter (final_items already score-desc
            sorted via tie-break chain).
      2. If step 1 yields nothing → hardcoded fallback set.
      3. If fallback also yields nothing → empty dict.

    TODO(faz1-pr4): Fallback usage frequency should be audited in prod
    telemetry. If rarely triggered, fallback can be removed entirely.
    """
    if top_contradiction_id:
        supporting: list[Mapping[str, Any]] = []
        for item in final_items:
            archetype_id = _safe_text(item.get("id"))
            if not archetype_id:
                continue
            if top_contradiction_id in supports_lookup.get(archetype_id, set()):
                supporting.append(item)

        not_in_primary = [
            item for item in supporting
            if _safe_text(item.get("id")) not in primary_top_ids
        ]
        pool = not_in_primary if not_in_primary else supporting
        if pool:
            return dict(pool[0])

    fallback_set = {_safe_text(x) for x in fallback_ids if _safe_text(x)}
    for item in final_items:
        if _safe_text(item.get("id")) in fallback_set:
            return dict(item)

    return {}


def _attach_why_this_not_that(
    *,
    final_items: list[dict[str, Any]],
    subprofile_candidates: Mapping[str, Mapping[str, Any]],
    minimum_gap_for_single_headline: float = 0.08,
) -> None:
    for index, item in enumerate(final_items):
        core_label = _safe_text(item.get("label"))
        subprofile_label = _safe_text(item.get("subprofile_label_tr"))
        soften_subprofile = bool(item.get("subprofile_is_softened"))
        if index == 0 and len(final_items) > 1:
            runner_up = final_items[1]
            gap = _safe_float(item.get("score")) - _safe_float(runner_up.get("score"))
            runner_up_label = _safe_text(runner_up.get("label"))
            if gap < minimum_gap_for_single_headline and runner_up_label:
                item["why_this_not_that"] = (
                    f"Seni {runner_up_label.lower()} cizgisine yaklastiran sinyaller de var; "
                    f"ama {('simdilik ' if soften_subprofile else '')}{subprofile_label.lower()} tonu ve {_safe_text((item.get('differentiators') or [''])[0]).lower()} "
                    f"bu profili one tasiyor."
                ).strip()
                continue
        candidates = (
            subprofile_candidates.get(_safe_text(item.get("id")), {}).get("candidates") or []
            if isinstance(subprofile_candidates.get(_safe_text(item.get("id"))), Mapping)
            else []
        )
        if len(candidates) > 1:
            runner_up_sub = _safe_text(candidates[1].get("label_tr"))
            item["why_this_not_that"] = (
                f"Ayni cekirdekte {runner_up_sub.lower()} tonu da mumkundu; "
                f"ama {('simdilik ' if soften_subprofile else '')}{subprofile_label.lower()} tarafi sende daha net ayrisiyor."
            ).strip()
        else:
            item["why_this_not_that"] = (
                f"{core_label} burada tek bir baslik degil, "
                f"{('simdilik ' if soften_subprofile else '')}{subprofile_label.lower()} tonu ile belirginlesiyor."
            ).strip()


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


def _adaptive_rules() -> Dict[str, float]:
    payload = (
        (_fusion().get("adaptive_rules") or {})
        if isinstance(_fusion().get("adaptive_rules"), Mapping)
        else {}
    )
    return {
        "core_gap_trigger": _safe_float(payload.get("core_gap_trigger")) or 0.10,
        "subprofile_gap_trigger": _safe_float(payload.get("subprofile_gap_trigger")) or 0.08,
        "max_families": _safe_float(payload.get("max_families")) or 3.0,
        "max_questions": _safe_float(payload.get("max_questions")) or 4.0,
    }


def _adaptive_recommendation(
    *,
    final_items: Sequence[Mapping[str, Any]],
    subprofile_candidates: Mapping[str, Mapping[str, Any]],
) -> Dict[str, Any]:
    if not final_items:
        return {"trigger_reason": "", "families": []}
    rules = _adaptive_rules()
    max_families = int(rules["max_families"])
    core_gap = _top_core_family_gap(final_items)
    if core_gap < rules["core_gap_trigger"] and len(final_items) > 1:
        primary = final_items[0]
        secondary = final_items[1]
        families: list[str] = []
        for item in [primary, secondary]:
            families.extend(
                [
                    _safe_text(name)
                    for name in item.get("question_families") or []
                    if _safe_text(name)
                ]
            )
        deduped = list(dict.fromkeys(families))[:max_families]
        return {"trigger_reason": "core_ambiguity", "families": deduped}

    primary_id = _safe_text(final_items[0].get("id"))
    candidate_payload = (
        subprofile_candidates.get(primary_id)
        if isinstance(subprofile_candidates.get(primary_id), Mapping)
        else {}
    )
    candidates = (
        candidate_payload.get("candidates")
        if isinstance(candidate_payload.get("candidates"), Sequence)
        else []
    )
    if len(candidates) > 1:
        gap = _safe_float(candidates[0].get("score")) - _safe_float(candidates[1].get("score"))
        if gap < rules["subprofile_gap_trigger"]:
            families = [
                _safe_text(name)
                for item in candidates[:2]
                for name in item.get("question_families") or []
                if _safe_text(name)
            ]
            deduped = list(dict.fromkeys(families))[:max_families]
            return {"trigger_reason": "subprofile_ambiguity", "families": deduped}
    return {"trigger_reason": "", "families": []}


def build_archetype_profile(
    *,
    primitive_scores: Mapping[str, Any],
    master_selector: Mapping[str, Any] | None = None,
    contradiction_signatures: Mapping[str, Any] | None = None,
    natal_feature_graph: Mapping[str, Any] | None = None,
    test_scores: Mapping[str, Any] | None = None,
    context_scores: Mapping[str, Any] | None = None,
    question_family_scores: Mapping[str, Any] | None = None,
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
    chart_by_id = (
        chart_prior.get("by_id") if isinstance(chart_prior.get("by_id"), Mapping) else {}
    )
    test_by_id = _normalized_mapping(test_scores)
    context_by_id = _normalized_mapping(context_scores)
    family_scores = _normalized_mapping(question_family_scores)
    primitives = _primitive_lookup(primitive_scores)
    spine = _identity_spine(master_selector)
    contradiction = _top_contradiction(contradiction_signatures)
    public_score, private_score, balance_score = _public_private(natal_feature_graph)

    profile_name = _select_weight_profile(
        has_test_scores=bool(test_by_id),
        birth_time_confidence=birth_time_confidence,
        answer_consistency=answer_consistency,
    )
    weights = _weight_profile(profile_name)

    raw_items: list[dict[str, Any]] = []
    final_score_map: Dict[str, float] = {}
    subprofile_selections: Dict[str, Dict[str, Any]] = {}
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
        subprofile_selection = _select_subprofile(
            archetype=archetype,
            core_score=final_score,
            primitives=primitives,
            family_scores=family_scores,
            spine=spine,
            contradiction=contradiction,
            public_score=public_score,
            private_score=private_score,
            balance_score=balance_score,
        )
        subprofile_selections[archetype_id] = subprofile_selection
        raw_items.append(
            {
                "id": archetype_id,
                "label": _safe_text(archetype.get("label_tr")),
                "score": final_score,
                "source_split": {
                    "chart_prior": round(chart_score, 4),
                    "test_score": round(test_score, 4),
                    "context_score": round(context_score, 4),
                },
                "question_families": [
                    _safe_text(item)
                    for item in archetype.get("question_families") or []
                    if _safe_text(item)
                ],
                "core_archetype": dict(archetype),
            }
        )

    top_contradiction_id = _safe_text(contradiction.get("id"))
    raw_items.sort(
        key=lambda item: _tie_break_key(
            item=item,
            subprofile_selections=subprofile_selections,
            top_contradiction_id=top_contradiction_id,
        )
    )
    slots = _select_slots(final_score_map)
    context_mixins = _build_mixins(
        primitives=primitives,
        family_scores=family_scores,
        contradiction=contradiction,
        public_score=public_score,
        private_score=private_score,
        balance_score=balance_score,
    )

    final_items: list[dict[str, Any]] = []
    soften_chart_only = profile_name == "chart_only" and not bool(test_by_id)
    for index, item in enumerate(raw_items):
        archetype_id = _safe_text(item.get("id"))
        archetype = item.get("core_archetype") if isinstance(item.get("core_archetype"), Mapping) else {}
        selected_subprofile = (
            (subprofile_selections.get(archetype_id) or {}).get("selected")
            if isinstance(subprofile_selections.get(archetype_id), Mapping)
            else {}
        )
        candidate_list = (
            (subprofile_selections.get(archetype_id) or {}).get("candidates")
            if isinstance(subprofile_selections.get(archetype_id), Mapping)
            else []
        )
        subprofile_gap = (
            _safe_float(candidate_list[0].get("score")) - _safe_float(candidate_list[1].get("score"))
            if isinstance(candidate_list, Sequence) and len(candidate_list) > 1
            else 1.0
        )
        soften_subprofile = soften_chart_only
        top_primitive_id = _top_weighted_primitive(
            (archetype.get("primitive_weights") or {}),
            primitives,
        )
        top_primitive_ids = _top_weighted_primitive_ids(
            (archetype.get("primitive_weights") or {}),
            primitives,
            limit=3,
        )
        slot_name = _primary_slot_for_item(archetype_id, slots)
        item_mixins = [dict(mixin) for mixin in context_mixins] if index == 0 else []
        differentiators = _build_differentiators(
            selected_subprofile=selected_subprofile if isinstance(selected_subprofile, Mapping) else {},
            top_primitive_id=top_primitive_id,
            mixins=item_mixins,
            slot_name=slot_name,
            soften_subprofile=soften_subprofile,
        )
        copy_blocks = _assemble_copy_blocks(
            archetype=archetype if isinstance(archetype, Mapping) else {},
            selected_subprofile=selected_subprofile if isinstance(selected_subprofile, Mapping) else {},
            mixins=item_mixins,
            contradiction=contradiction,
            top_primitive_ids=top_primitive_ids,
            slot_name=slot_name,
            public_score=public_score,
            private_score=private_score,
            soften_subprofile=soften_subprofile,
            include_mixin_language=index == 0,
        )
        final_items.append(
            {
                "id": archetype_id,
                "label": _safe_text(item.get("label")),
                **copy_blocks,
                "copy_blocks": copy_blocks,
                "score": _safe_float(item.get("score")),
                "source_split": dict(item.get("source_split") or {}),
                "question_families": list(item.get("question_families") or []),
                "subprofile_id": _safe_text((selected_subprofile or {}).get("id")),
                "subprofile_label_tr": _safe_text((selected_subprofile or {}).get("label_tr")),
                "subprofile_display_label_tr": ""
                if soften_subprofile
                else _safe_text((selected_subprofile or {}).get("label_tr")),
                "subprofile_is_softened": soften_subprofile,
                "subprofile_gap": round(_clamp01(subprofile_gap), 4),
                "mixins": item_mixins,
                "differentiators": differentiators,
                "copy_variant": _copy_variant(
                    archetype_id=archetype_id,
                    subprofile_id=_safe_text((selected_subprofile or {}).get("id")),
                    mixins=item_mixins,
                ),
            }
        )

    result_rules = (
        fusion.get("result_rules") if isinstance(fusion.get("result_rules"), Mapping) else {}
    )
    minimum_primary_score = _safe_float(result_rules.get("minimum_primary_score")) or 0.52
    minimum_gap_for_single_headline = (
        _safe_float(result_rules.get("minimum_gap_for_single_headline")) or 0.08
    )

    # `minimum_primary_score` gate değil flag olarak wire'landı — silent failure
    # yaratmıyor, consumer UI'a "düşük güven" sinyali veriyor.
    for item in final_items:
        item["score_meets_primary_threshold"] = (
            _safe_float(item.get("score")) >= minimum_primary_score
        )

    _attach_why_this_not_that(
        final_items=final_items,
        subprofile_candidates=subprofile_selections,
        minimum_gap_for_single_headline=minimum_gap_for_single_headline,
    )

    top_count = max(int(result_rules.get("top_archetypes") or 3), 1)
    top_archetypes = final_items[:top_count]

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

    shadow_archetype = _select_shadow_archetype(
        final_items=final_items,
        primary_top_ids={_safe_text(item.get("id")) for item in top_archetypes},
        top_contradiction_id=_safe_text(primary_contradiction.get("id")),
        supports_lookup=_build_contradiction_support_lookup(taxonomy),
    )

    chart_confidence = _chart_confidence(birth_time_confidence)
    test_confidence = _test_confidence(answer_consistency, bool(test_by_id))
    if test_by_id:
        global_confidence = round(_clamp01((chart_confidence * 0.45) + (test_confidence * 0.55)), 4)
    else:
        global_confidence = chart_confidence

    adaptive = _adaptive_recommendation(
        final_items=final_items,
        subprofile_candidates=subprofile_selections,
    )

    return {
        **get_archetype_runtime_versions(),
        "scoring_profile_version": "v1",
        "birth_time_mode": birth_time_mode(birth_time_confidence),
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
        "slots": slots,
        "context_mixins": context_mixins,
        "adaptive": adaptive,
        "debug": {
            "fusion_weights_used": weights,
            "answer_consistency": None if answer_consistency is None else round(_clamp01(answer_consistency), 4),
            "birth_time_confidence": _safe_text(birth_time_confidence) or "exact",
            "subprofile_candidates": {
                key: (value.get("candidates") or [])
                for key, value in subprofile_selections.items()
            },
            "mixins": context_mixins,
            "family_scores": family_scores,
        },
    }
