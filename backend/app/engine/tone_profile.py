from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from functools import lru_cache
import os
from pathlib import Path
from typing import Any, Mapping

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "tone" / "tone.yaml"

DEFAULT_CONFIG = {
    "tone_defaults": {"warmth_bias": 0.6, "uncertainty_default": 0.35},
    "tone_thresholds": {
        "certainty_hi": 0.75,
        "certainty_mid": 0.45,
        "directness_hi": 0.65,
        "warmth_hi": 0.65,
        "tempo_hi": 0.65,
        "distance_hi": 0.6,
    },
    "shadow_safety": {
        "always_soften": True,
        "template": (
            "Golge tarafinda bu, {shadow_text} baskisini hissettirebilir; "
            "bu bir suc degil, sadece bir yuklenme alanidir."
        ),
    },
}


@dataclass(frozen=True)
class ToneProfile:
    directness: float
    warmth: float
    intensity: float
    certainty: float
    tempo: float
    distance: float

    def to_dict(self) -> dict[str, float]:
        return {key: round(float(value), 4) for key, value in asdict(self).items()}


@lru_cache(maxsize=1)
def load_tone_config() -> Mapping[str, Any]:
    if not CONFIG_PATH.exists():
        return _apply_env_overrides(DEFAULT_CONFIG)
    try:
        payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _apply_env_overrides(DEFAULT_CONFIG)
    if not isinstance(payload, Mapping):
        return _apply_env_overrides(DEFAULT_CONFIG)
    merged = _merge_config(DEFAULT_CONFIG, payload)
    return _apply_env_overrides(merged)


def compute_tone(
    regulation: Mapping[str, Any] | None,
    meaning_weighting: Mapping[str, Any] | None,
    domain_salience: Mapping[str, Any] | float | None,
    data_quality: Mapping[str, Any] | None,
) -> ToneProfile:
    regulation = regulation or {}
    meaning_weighting = meaning_weighting or {}
    data_quality = data_quality or {}
    config = load_tone_config()
    defaults = config.get("tone_defaults", {})

    energy_pressure = _energy_pressure_value(regulation.get("energy_pressure"))
    strain = _safe_float(data_quality.get("strain"))
    resilience = _safe_float(data_quality.get("resilience"))
    uncertainty = _safe_float(
        data_quality.get("uncertainty", defaults.get("uncertainty_default", 0.35))
    )
    domain_salience_value = _domain_salience_value(domain_salience)

    warmth_bias = _safe_float(defaults.get("warmth_bias", 0.6))

    intensity = _clamp(0.15 + 0.55 * energy_pressure + 0.20 * strain + 0.10 * domain_salience_value)
    certainty = _clamp(0.80 - 0.55 * uncertainty - 0.25 * strain + 0.15 * resilience)
    directness = _clamp(0.35 + 0.30 * resilience + 0.20 * domain_salience_value - 0.25 * warmth_bias)
    warmth = _clamp(0.55 + 0.25 * (1 - directness) + 0.20 * (1 - strain))
    tempo = _clamp(0.40 + 0.35 * intensity + 0.25 * certainty)
    distance = _clamp(0.50 + 0.30 * (1 - warmth) + 0.20 * uncertainty)

    if data_quality.get("upper_meaning_used"):
        intensity = _clamp(intensity * 0.90)
        tempo = _clamp(tempo * 0.85)
        certainty = _clamp(certainty * 0.95)
        warmth = _clamp(warmth * 1.05)

    return ToneProfile(
        directness=directness,
        warmth=warmth,
        intensity=intensity,
        certainty=certainty,
        tempo=tempo,
        distance=distance,
    )


def _energy_pressure_value(value: Any) -> float:
    if isinstance(value, (int, float)):
        return _clamp(float(value))
    mapped = {"low": 0.35, "medium": 0.6, "high": 0.85}
    if isinstance(value, str):
        return mapped.get(value.lower().strip(), 0.5)
    return 0.5


def _domain_salience_value(value: Mapping[str, Any] | float | None) -> float:
    if isinstance(value, (int, float)):
        return _clamp(float(value))
    if isinstance(value, Mapping):
        for key in ("score", "salience_score", "domain_salience_score"):
            if key in value:
                return _clamp(_safe_float(value.get(key)))
    return 0.5


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _merge_config(defaults: Mapping[str, Any], override: Mapping[str, Any]) -> Mapping[str, Any]:
    merged = dict(defaults)
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = _merge_config(merged.get(key, {}), value)
        else:
            merged[key] = value
    return merged


def _apply_env_overrides(config: Mapping[str, Any]) -> Mapping[str, Any]:
    env_payload = os.getenv("JOVIA_TONE_CONFIG", "").strip()
    if not env_payload:
        return config
    try:
        override = json.loads(env_payload)
    except json.JSONDecodeError:
        return config
    if not isinstance(override, Mapping):
        return config
    return _merge_config(config, override)
