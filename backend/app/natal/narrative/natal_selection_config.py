from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml


_DEFAULT_CONFIG: Dict[str, Any] = {
    "engine_version": "natal_selection_v3_config_v1",
    "phase_flags": {
        "feature_foundation_debug": True,
        "master_selector_enabled": False,
        "master_selector_debug_only": True,
        "contradiction_engine_enabled": False,
        "contradiction_engine_debug_only": True,
        "layer_arbitration_enabled": False,
        "layer_arbitration_debug_only": True,
        "surface_migration_enabled": False,
        "surface_migration_debug_only": True,
        "voice_profile_enabled": False,
        "voice_profile_debug_only": True,
    },
    "rollouts": {
        "profile_narrative_selector_rollout_pct": 0,
        "personality_imprint_selector_rollout_pct": 0,
        "supporting_threads_selector_rollout_pct": 0,
        "voice_profile_rollout_pct": 0,
    },
    "thresholds": {
        "motif_min_score": 0.18,
        "strong_orb_max": 1.5,
        "medium_orb_max": 3.5,
        "aspect_max_orb": 6.0,
        "public_houses": [1, 7, 10, 11],
        "private_houses": [4, 8, 12],
        "bridge_houses": [3, 5, 6, 9],
    },
    "weights": {
        "planet_salience": {
            "base": 0.22,
            "angularity": 0.16,
            "chart_ruler_centrality": 0.14,
            "luminary_condition": 0.12,
            "aspect_density": 0.10,
            "exact_aspect_salience": 0.12,
            "dispositor_chain_pressure": 0.08,
            "motif_density": 0.08,
            "contradiction_polarity": 0.06,
            "public_private_split": 0.06,
            "house_ruler_recursion": 0.06,
        },
        "primitive_v2": {
            "legacy_score_weight": 0.44,
            "feature_support_weight": 0.36,
            "salience_weight": 0.20,
        },
        "selector_v1": {
            "primitive_core_weight": 0.34,
            "primitive_support_weight": 0.16,
            "feature_support_weight": 0.16,
            "motif_support_weight": 0.12,
            "contradiction_bonus_weight": 0.10,
            "salience_bonus_weight": 0.06,
            "role_fit_weight": 0.06,
            "redundancy_penalty_weight": 0.08,
            "incoherence_penalty_weight": 0.08,
        },
        "layer_arbitrator_v1": {
            "primitive_alignment_weight": 0.36,
            "text_alignment_weight": 0.24,
            "slot_alignment_weight": 0.16,
            "contradiction_alignment_weight": 0.14,
            "surface_role_weight": 0.10,
            "conflict_margin": 0.12,
            "keep_threshold": 0.58,
            "rewrite_threshold": 0.40,
            "demote_threshold": 0.28,
        },
        "surface_migration_v1": {
            "profile_direct_match_bonus": 0.18,
            "profile_counterweight_bonus": 0.08,
            "profile_confidence_bonus": 0.06,
            "imprint_slot_bonus": 0.16,
            "imprint_primitive_bonus": 0.18,
            "imprint_counterweight_bonus": 0.08,
            "imprint_combination_bonus": 0.10,
        },
        "voice_profile_v2": {
            "spine_confidence_weight": 0.22,
            "structurality_weight": 0.20,
            "public_private_weight": 0.18,
            "contradiction_weight": 0.16,
            "emotional_threshold_weight": 0.14,
            "visibility_weight": 0.10,
        },
    },
}

_CONFIG_CACHE: Dict[str, Any] | None = None
_CONFIG_CACHE_MTIME_NS: int | None = None


def _merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = dict(base)
    for key, value in override.items():
        current = merged.get(key)
        if isinstance(current, dict) and isinstance(value, dict):
            merged[key] = _merge_dicts(current, value)
        else:
            merged[key] = value
    return merged


def _config_path() -> Path:
    return Path(__file__).resolve().parents[2] / "config" / "natal" / "natal_selection_v3.yaml"


def get_natal_selection_v3_config() -> Dict[str, Any]:
    global _CONFIG_CACHE
    global _CONFIG_CACHE_MTIME_NS
    path = _config_path()
    try:
        stat = path.stat()
        mtime_ns = int(stat.st_mtime_ns)
    except Exception:
        mtime_ns = None

    if _CONFIG_CACHE is not None and _CONFIG_CACHE_MTIME_NS == mtime_ns:
        return dict(_CONFIG_CACHE)

    try:
        parsed = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        parsed = {}
    config = _merge_dicts(_DEFAULT_CONFIG, parsed if isinstance(parsed, dict) else {})
    config["config_path"] = str(path)
    _CONFIG_CACHE = dict(config)
    _CONFIG_CACHE_MTIME_NS = mtime_ns
    return dict(config)
