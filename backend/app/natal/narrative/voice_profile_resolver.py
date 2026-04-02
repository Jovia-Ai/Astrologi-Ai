from __future__ import annotations

import hashlib
import os
from typing import Any, Dict, Mapping, Sequence

from .natal_selection_config import get_natal_selection_v3_config


def _clamp01(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, number))


def _safe_avg(values: Sequence[float]) -> float:
    cleaned = [float(value) for value in values if value is not None]
    if not cleaned:
        return 0.0
    return sum(cleaned) / len(cleaned)


def _hash_int(value: str) -> int:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def _env_flag(name: str) -> bool | None:
    raw = os.getenv(name)
    if raw is None or not str(raw).strip():
        return None
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


def _rollout_pct(config: Mapping[str, Any]) -> int:
    rollouts = config.get("rollouts") if isinstance(config.get("rollouts"), Mapping) else {}
    raw = os.getenv("VOICE_PROFILE_ROLLOUT_PCT")
    if raw is None or not str(raw).strip():
        raw = rollouts.get("voice_profile_rollout_pct", 0)
    try:
        pct = int(raw)
    except (TypeError, ValueError):
        pct = 0
    return max(0, min(100, pct))


def _primitive_lookup(primitive_scores: Mapping[str, Any] | None) -> Dict[str, Dict[str, Any]]:
    payload = primitive_scores if isinstance(primitive_scores, Mapping) else {}
    items = payload.get("primitive_scores") if isinstance(payload.get("primitive_scores"), Sequence) else []
    return {
        str(item.get("primitive_id") or ""): dict(item)
        for item in items
        if isinstance(item, Mapping) and str(item.get("primitive_id") or "").strip()
    }


def _primitive_score(lookup: Mapping[str, Mapping[str, Any]], primitive_id: str) -> float:
    entry = lookup.get(str(primitive_id))
    if not isinstance(entry, Mapping):
        return 0.0
    return float(entry.get("score") or 0.0)


def _top_contradiction(contradiction_signatures: Mapping[str, Any] | None) -> Dict[str, Any]:
    payload = contradiction_signatures if isinstance(contradiction_signatures, Mapping) else {}
    items = payload.get("top_signatures") if isinstance(payload.get("top_signatures"), Sequence) else []
    if items and isinstance(items[0], Mapping):
        return dict(items[0])
    items = payload.get("signatures") if isinstance(payload.get("signatures"), Sequence) else []
    if items and isinstance(items[0], Mapping):
        return dict(items[0])
    return {}


def _voice_mode(*, include_debug: bool, seed_key: str | None = None) -> tuple[bool, str, Dict[str, Any]]:
    config = get_natal_selection_v3_config()
    phase_flags = config.get("phase_flags") if isinstance(config.get("phase_flags"), Mapping) else {}
    enabled_override = _env_flag("VOICE_PROFILE_ENABLED")
    debug_override = _env_flag("VOICE_PROFILE_DEBUG_ONLY")
    enabled_requested = enabled_override if enabled_override is not None else bool(phase_flags.get("voice_profile_enabled"))
    debug_only = debug_override if debug_override is not None else bool(phase_flags.get("voice_profile_debug_only", True))
    rollout_pct = _rollout_pct(config)
    seed_material = str(seed_key or "").strip()
    seed_bucket = (_hash_int(seed_material) % 100) if seed_material else None

    decision = {
        "enabled_requested": enabled_requested,
        "debug_only": debug_only,
        "rollout_pct": rollout_pct,
        "seed_bucket": seed_bucket,
        "has_seed_key": bool(seed_material),
    }

    if enabled_requested:
        if rollout_pct >= 100:
            return True, "active", {**decision, "mode_reason": "rollout_full_active"}
        if rollout_pct <= 0:
            if include_debug and debug_only:
                return False, "shadow", {**decision, "mode_reason": "rollout_zero_shadow"}
            return False, "disabled", {**decision, "mode_reason": "rollout_zero_disabled"}
        if seed_bucket is None:
            if include_debug and debug_only:
                return False, "shadow", {**decision, "mode_reason": "missing_seed_for_partial_rollout"}
            return False, "disabled", {**decision, "mode_reason": "missing_seed_disabled"}
        if seed_bucket < rollout_pct:
            return True, "active", {**decision, "mode_reason": "rollout_bucket_active"}
        if include_debug and debug_only:
            return False, "shadow", {**decision, "mode_reason": "rollout_bucket_shadow"}
        return False, "disabled", {**decision, "mode_reason": "rollout_bucket_skipped"}
    if include_debug and debug_only:
        return False, "shadow", {**decision, "mode_reason": "debug_shadow"}
    return False, "disabled", {**decision, "mode_reason": "disabled"}


def _axis_payload(score: float, *, positive: str, negative: str) -> Dict[str, Any]:
    clamped = round(_clamp01(score), 4)
    if clamped >= 0.58:
        label = positive
    elif clamped <= 0.42:
        label = negative
    else:
        label = "balanced"
    return {
        "score": clamped,
        "label": label,
        "positive": positive,
        "negative": negative,
    }


def _spine_payload(master_selector: Mapping[str, Any] | None) -> Dict[str, Dict[str, Any]]:
    payload = master_selector if isinstance(master_selector, Mapping) else {}
    spine = payload.get("identity_spine") if isinstance(payload.get("identity_spine"), Mapping) else {}
    return {
        str(slot): dict(value)
        for slot, value in spine.items()
        if isinstance(value, Mapping)
    }


def resolve_voice_profile_v2(
    *,
    master_selector: Mapping[str, Any] | None = None,
    contradiction_signatures: Mapping[str, Any] | None = None,
    natal_feature_graph: Mapping[str, Any] | None = None,
    primitive_scores: Mapping[str, Any] | None = None,
    seed_key: str | None = None,
    include_debug: bool = False,
) -> Dict[str, Any]:
    config = get_natal_selection_v3_config()
    weights = (
        (config.get("weights") or {}).get("voice_profile_v2")
        if isinstance(config.get("weights"), Mapping)
        else {}
    )
    enabled, mode, mode_decision = _voice_mode(include_debug=include_debug, seed_key=seed_key)
    spine = _spine_payload(master_selector)
    primitives = _primitive_lookup(primitive_scores)
    feature_graph = natal_feature_graph if isinstance(natal_feature_graph, Mapping) else {}
    top_contradiction = _top_contradiction(contradiction_signatures)

    public_private = feature_graph.get("public_private_split") if isinstance(feature_graph.get("public_private_split"), Mapping) else {}
    public_score = float(public_private.get("public_score") or 0.0)
    private_score = float(public_private.get("private_score") or 0.0)

    spine_confidence = _safe_avg([
        float((spine.get(slot) or {}).get("confidence") or 0.0)
        for slot in (
            "primary_identity_spine",
            "secondary_balancing_line",
            "relational_line",
            "work_visibility_line",
            "shadow_protection_line",
        )
        if isinstance(spine.get(slot), Mapping)
    ])
    structurality = _safe_avg([
        _primitive_score(primitives, "inner_structure"),
        _primitive_score(primitives, "systems_thinking"),
        _primitive_score(primitives, "methodical_drive"),
        _primitive_score(primitives, "mental_structuring"),
        _primitive_score(primitives, "public_refinement") * 0.7,
    ])
    emotional_threshold = _safe_avg([
        _primitive_score(primitives, "emotional_threshold"),
        _primitive_score(primitives, "tone_sensitivity"),
        _primitive_score(primitives, "inner_critic") * 0.8,
    ])
    visibility = _safe_avg([
        _primitive_score(primitives, "visible_presence"),
        _primitive_score(primitives, "public_refinement"),
        _primitive_score(primitives, "creation_luck"),
        _primitive_score(primitives, "network_luck"),
        public_score,
    ])
    privacy = _safe_avg([
        _primitive_score(primitives, "backstage_creation"),
        _primitive_score(primitives, "recharge_through_home"),
        _primitive_score(primitives, "family_self_reliance"),
        private_score,
    ])
    originality = _safe_avg([
        _primitive_score(primitives, "originality_drive"),
        _primitive_score(primitives, "big_picture_vision"),
    ])
    warmth_capacity = _safe_avg([
        _primitive_score(primitives, "relational_security"),
        _primitive_score(primitives, "graceful_affection"),
        _primitive_score(primitives, "intimacy_depth") * 0.7,
    ])
    seriousness = _safe_avg([
        _primitive_score(primitives, "inner_structure"),
        _primitive_score(primitives, "inner_critic"),
        _primitive_score(primitives, "methodical_drive"),
    ])
    playful_drive = _safe_avg([
        _primitive_score(primitives, "creation_luck"),
        _primitive_score(primitives, "network_luck"),
        _primitive_score(primitives, "originality_drive"),
        _primitive_score(primitives, "visible_presence") * 0.6,
    ])
    holding_capacity = _safe_avg([
        _primitive_score(primitives, "relational_security"),
        _primitive_score(primitives, "recharge_through_home"),
        emotional_threshold,
        private_score,
    ])
    contradiction_score = float(top_contradiction.get("score") or 0.0)
    contradiction_id = str(top_contradiction.get("id") or "")

    directness = _clamp01(
        0.50
        + visibility * 0.22
        + _primitive_score(primitives, "self_definition") * 0.14
        - privacy * 0.16
        - emotional_threshold * 0.12
        - structurality * 0.02
        + (0.05 if contradiction_id == "speed_vs_control" else 0.0)
        - (0.08 if contradiction_id == "visibility_vs_private_preparation" else 0.0)
        - (0.05 if contradiction_id == "closeness_vs_threshold" else 0.0)
    )
    warmth = _clamp01(
        0.50
        + warmth_capacity * 0.22
        + spine_confidence * 0.08
        - emotional_threshold * 0.14
        - private_score * 0.04
        - (0.06 if contradiction_id == "closeness_vs_threshold" else 0.0)
        - (0.04 if contradiction_id == "composure_vs_internal_pressure" else 0.0)
    )
    poetic = _clamp01(
        0.50
        + originality * 0.10
        + _primitive_score(primitives, "big_picture_vision") * 0.14
        + _primitive_score(primitives, "backstage_creation") * 0.12
        + _primitive_score(primitives, "transformative_bonding") * 0.10
        - structurality * 0.14
        - _primitive_score(primitives, "public_refinement") * 0.06
    )
    playfulness = _clamp01(
        0.50
        + playful_drive * 0.18
        + originality * 0.08
        - seriousness * 0.18
        - emotional_threshold * 0.06
        + (0.03 if contradiction_id == "speed_vs_control" else 0.0)
    )
    holding = _clamp01(
        0.50
        + holding_capacity * 0.18
        + warmth * 0.10
        - visibility * 0.10
        - _primitive_score(primitives, "push_pull_drive") * 0.08
        + (0.05 if contradiction_id in {"closeness_vs_threshold", "composure_vs_internal_pressure"} else 0.0)
    )

    intensity = _clamp01(
        0.38
        + contradiction_score * 0.22
        + visibility * float(weights.get("visibility_weight") or 0.10)
        + emotional_threshold * float(weights.get("emotional_threshold_weight") or 0.14)
        + originality * 0.08
    )
    certainty = _clamp01(
        0.42
        + spine_confidence * float(weights.get("spine_confidence_weight") or 0.22)
        + structurality * float(weights.get("structurality_weight") or 0.20)
        - contradiction_score * 0.08
    )
    tempo = _clamp01(
        0.44
        + directness * 0.16
        + playfulness * 0.10
        - holding * 0.10
        - structurality * 0.04
        + (0.04 if contradiction_id == "speed_vs_control" else 0.0)
    )
    distance = _clamp01(
        0.42
        + holding * 0.16
        + private_score * float(weights.get("public_private_weight") or 0.18) * 0.6
        + emotional_threshold * 0.10
        - warmth * 0.10
    )

    tone = "neutral"
    if directness >= 0.60 and warmth <= 0.48 and intensity >= 0.56:
        tone = "firm"
    elif warmth >= 0.56 or holding >= 0.58:
        tone = "soft"

    sentence_length = "medium"
    if directness >= 0.62 and poetic <= 0.46:
        sentence_length = "short"
    elif poetic >= 0.58 or (1.0 - directness) >= 0.56:
        sentence_length = "long"

    softening_level = _clamp01(
        0.24
        + warmth * 0.32
        + holding * 0.18
        + (1.0 - directness) * 0.10
        - intensity * 0.08
    )

    derived_expression = {
        "tone": tone,
        "sentence_length": sentence_length,
        "softening_level": round(softening_level, 4),
        "tone_profile": {
            "directness": round(directness, 4),
            "warmth": round(warmth, 4),
            "intensity": round(intensity, 4),
            "certainty": round(certainty, 4),
            "tempo": round(tempo, 4),
            "distance": round(distance, 4),
        },
    }

    return {
        "engine_version": "voice_profile_v2",
        "enabled": enabled,
        "mode": mode,
        "directness": _axis_payload(directness, positive="direct", negative="reflective"),
        "warmth": _axis_payload(warmth, positive="warm", negative="restrained"),
        "texture": _axis_payload(poetic, positive="poetic", negative="crisp"),
        "playfulness": _axis_payload(playfulness, positive="playful", negative="serious"),
        "holding_style": _axis_payload(holding, positive="holding", negative="confrontive"),
        "axes": {
            "direct_vs_reflective": _axis_payload(directness, positive="direct", negative="reflective"),
            "warm_vs_restrained": _axis_payload(warmth, positive="warm", negative="restrained"),
            "poetic_vs_crisp": _axis_payload(poetic, positive="poetic", negative="crisp"),
            "playful_vs_serious": _axis_payload(playfulness, positive="playful", negative="serious"),
            "confrontive_vs_holding": _axis_payload(holding, positive="holding", negative="confrontive"),
        },
        "drivers": {
            "spine_confidence": round(spine_confidence, 4),
            "structurality": round(structurality, 4),
            "emotional_threshold": round(emotional_threshold, 4),
            "visibility": round(visibility, 4),
            "privacy": round(privacy, 4),
            "warmth_capacity": round(warmth_capacity, 4),
            "playful_drive": round(playful_drive, 4),
            "seriousness": round(seriousness, 4),
            "public_score": round(public_score, 4),
            "private_score": round(private_score, 4),
        },
        "contradiction_context": {
            "primary_contradiction_id": contradiction_id,
            "primary_contradiction_label": str(top_contradiction.get("editorial_label") or ""),
            "primary_contradiction_score": round(contradiction_score, 4),
        },
        "derived_expression": derived_expression,
        "debug": {
            "selected_lines": {
                slot: {
                    "line_id": str(item.get("line_id") or ""),
                    "label": str(item.get("label") or ""),
                    "confidence": round(float(item.get("confidence") or 0.0), 4),
                }
                for slot, item in spine.items()
            },
            "mode_reason": str(mode_decision.get("mode_reason") or ""),
            "rollout": {
                "enabled_requested": bool(mode_decision.get("enabled_requested")),
                "debug_only": bool(mode_decision.get("debug_only")),
                "rollout_pct": int(mode_decision.get("rollout_pct") or 0),
                "seed_bucket": mode_decision.get("seed_bucket"),
                "has_seed_key": bool(mode_decision.get("has_seed_key")),
            },
        },
    }
