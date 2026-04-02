from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

CONFIG_PATH = Path(__file__).resolve().parents[4] / "config" / "transit" / "selection_v3_config.yaml"

DEFAULT_CONFIG: Dict[str, Any] = {
    "chapter_roles": {
        "opener_families": ["lunation_trigger", "eclipse_trigger", "house_ingress_event"],
        "builder_buckets": ["long", "medium"],
        "release_phases": ["separating"],
        "integrator_modes": ["flow", "opening"],
        "min_role_score": 0.36,
    }
}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _merge_config(defaults: Mapping[str, Any], override: Mapping[str, Any]) -> Dict[str, Any]:
    merged = dict(defaults)
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = _merge_config(merged.get(key, {}), value)
        else:
            merged[key] = value
    return merged


@lru_cache(maxsize=1)
def load_chapter_role_config() -> Mapping[str, Any]:
    config = dict(DEFAULT_CONFIG)
    if CONFIG_PATH.exists():
        try:
            payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {}
        if isinstance(payload, Mapping):
            config = _merge_config(config, payload)
    env_payload = os.getenv("JOVIA_SELECTION_V3_CONFIG", "").strip()
    if env_payload:
        try:
            override = json.loads(env_payload)
        except json.JSONDecodeError:
            override = {}
        if isinstance(override, Mapping):
            config = _merge_config(config, override)
    return config


def _role_scores(
    event: Mapping[str, Any],
    *,
    features: Mapping[str, Any],
    config: Mapping[str, Any],
) -> Dict[str, float]:
    chapter_cfg = config.get("chapter_roles") if isinstance(config.get("chapter_roles"), Mapping) else {}
    meta = features.get("meta") if isinstance(features.get("meta"), Mapping) else {}
    meaning = features.get("meaning") if isinstance(features.get("meaning"), Mapping) else {}
    time = features.get("time") if isinstance(features.get("time"), Mapping) else {}
    family = str(meta.get("family") or "").strip().lower()
    subtype = str(meta.get("subtype") or "").strip().lower()
    bucket = str(meta.get("bucket") or "").strip().lower()
    phase = str(meta.get("phase") or "").strip().lower()
    aspect_mode = str(meaning.get("aspect_mode") or "").strip().lower()
    opener_families = {str(item).strip().lower() for item in (chapter_cfg.get("opener_families") or [])}
    builder_buckets = {str(item).strip().lower() for item in (chapter_cfg.get("builder_buckets") or [])}
    release_phases = {str(item).strip().lower() for item in (chapter_cfg.get("release_phases") or [])}
    integrator_modes = {str(item).strip().lower() for item in (chapter_cfg.get("integrator_modes") or [])}

    opener = (
        0.42 * _safe_float(meaning.get("chapter_opening"), 0.0)
        + 0.26 * (1.0 if family in opener_families or subtype in {"new_moon", "full_moon", "ingress"} else 0.0)
        + 0.18 * (1.0 if bool(time.get("is_rising_today")) else 0.0)
        + 0.14 * (1.0 if _safe_float(time.get("entry_distance"), 99.0) == 0 else 0.0)
    )
    builder = (
        0.42 * _safe_float(meaning.get("structurality"), 0.0)
        + 0.32 * _safe_float(meaning.get("lasting_change"), 0.0)
        + 0.14 * (1.0 if bucket in builder_buckets else 0.0)
        + 0.12 * min(1.0, _safe_float(meaning.get("repeat_pass"), 0.0) / 2.0)
    )
    peak = (
        0.54 * (1.0 if bool(time.get("is_peaking_today")) else 0.0)
        + 0.24 * (1.0 if _safe_float(time.get("peak_distance"), 99.0) == 0 else 0.0)
        + 0.22 * _safe_float(meaning.get("root_cause_weight"), 0.0)
    )
    release = (
        0.46 * (1.0 if phase in release_phases else 0.0)
        + 0.28 * (1.0 if bool(time.get("is_releasing_today")) else 0.0)
        + 0.16 * (1.0 if _safe_float(time.get("exit_distance"), 99.0) == 0 else 0.0)
        + 0.10 * _safe_float(meaning.get("contrastability"), 0.0)
    )
    integrator = (
        0.34 * (1.0 if aspect_mode in integrator_modes else 0.0)
        + 0.26 * _safe_float(meaning.get("surfaceability"), 0.0)
        + 0.20 * _safe_float(meaning.get("guidance_value"), 0.0)
        + 0.20 * _safe_float(meaning.get("house_clarity"), 0.0)
    )
    return {
        "opener": round(min(1.0, opener), 4),
        "builder": round(min(1.0, builder), 4),
        "peak": round(min(1.0, peak), 4),
        "release": round(min(1.0, release), 4),
        "integrator": round(min(1.0, integrator), 4),
    }


def infer_chapter_role(
    event: Mapping[str, Any],
    *,
    features: Mapping[str, Any],
    config: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    resolved = config if isinstance(config, Mapping) else load_chapter_role_config()
    scores = _role_scores(event, features=features, config=resolved)
    chapter_cfg = resolved.get("chapter_roles") if isinstance(resolved.get("chapter_roles"), Mapping) else {}
    min_role_score = _safe_float(chapter_cfg.get("min_role_score"), 0.36)
    role, score = max(scores.items(), key=lambda item: item[1])
    if score < min_role_score:
        role = "integrator"
        score = scores.get("integrator", score)
    return {
        "role": role,
        "score": round(score, 4),
        "scores": scores,
    }


def infer_chapter_roles(
    events: Sequence[Mapping[str, Any]],
    *,
    feature_map: Mapping[str, Mapping[str, Any]],
    config: Mapping[str, Any] | None = None,
) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for event in events:
        event_id = str(event.get("event_id") or "").strip()
        if not event_id:
            continue
        features = feature_map.get(event_id)
        if not isinstance(features, Mapping):
            continue
        out[event_id] = infer_chapter_role(event, features=features, config=config)
    return out
