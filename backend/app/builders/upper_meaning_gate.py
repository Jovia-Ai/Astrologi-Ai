"""Upper meaning selection gate and formatter."""
from __future__ import annotations

import os
from typing import Any, Dict, Mapping, Sequence


def build_upper_meaning_output(
    upper_meanings: Sequence[Mapping[str, Any]] | None,
    *,
    pressure_index: float,
    support_index: float,
    capacity_score: float,
    integration_score: float,
    integration_components: Mapping[str, float] | None = None,
    dispositor_flow: Mapping[str, Any] | None = None,
    latent_potential: Mapping[str, bool] | None = None,
    potential_count: int = 0,
    axis_activation: Mapping[str, Any] | None = None,
    dynamic_insights: Mapping[str, Any] | None = None,
    premium_mode: bool = False,
) -> Dict[str, Any]:
    upper_meanings = list(upper_meanings or [])
    dispositor_flow = dispositor_flow or {}
    latent_potential = latent_potential or {}
    axis_activation = axis_activation or {}

    _ = (dispositor_flow, latent_potential, potential_count, axis_activation)
    integration_components = dict(integration_components or {})
    pressure_min = _env_float("UPPER_MEANING_PRESSURE_MIN", 0.45)
    support_min = _env_float("UPPER_MEANING_SUPPORT_MIN", 0.45)
    capacity_min = _env_float("UPPER_MEANING_CAPACITY_MIN", 0.55)
    integration_min = _env_float("UPPER_MEANING_INTEGRATION_MIN", 0.55)

    reasons: list[str] = []
    pressure_ok = pressure_index >= pressure_min
    capacity_ok = capacity_score >= capacity_min
    integration_ok = integration_score >= integration_min
    reasons.append("pressure_high" if pressure_ok else "pressure_low")
    reasons.append("capacity_ok" if capacity_ok else "capacity_low")
    reasons.append("integration_ok" if integration_ok else "integration_low")
    gate_ok = capacity_ok and (pressure_ok or integration_ok)
    alt_gate_enabled = _env_flag("UPPER_MEANING_ALT_GATE", False)
    tension_spine_hit = _has_tension_spine(dynamic_insights)
    alt_gate_ok = (
        alt_gate_enabled
        and (not gate_ok)
        and tension_spine_hit
        and support_index >= support_min
        and capacity_ok
    )
    mode: str | None = None
    enabled = False
    reason: list[str] = []
    if gate_ok:
        mode = "strong"
        enabled = bool(upper_meanings)
        if not upper_meanings:
            reasons.append("no_content")
    elif alt_gate_ok:
        mode = "soft"
        reason.append("alt_gate_tension_spine")
        reasons.append("alt_gate_tension_spine")
        enabled = bool(upper_meanings)
        if not upper_meanings:
            reasons.append("no_content")
    if not enabled:
        return {
            "enabled": False,
            "mode": None,
            "reasons": reasons,
            "reason": reason,
            "content": None,
            "text": None,
            "thresholds": {
                "pressure_min": pressure_min,
                "support_min": support_min,
                "capacity_min": capacity_min,
                "integration_min": integration_min,
            },
            "debug_scores": {
                "pressure": round(pressure_index, 3),
                "support": round(support_index, 3),
                "capacity": round(capacity_score, 3),
                "integration": round(integration_score, 3),
                "integration_components": integration_components,
            },
            "level": 0,
        }

    selected = upper_meanings[0]
    lines = list(selected.get("upper_meaning") or [])
    parsed = _parse_upper_meaning_lines(lines)
    evidence = []
    comp_id = selected.get("composite_id")
    if comp_id:
        evidence.append(f"composite:{comp_id}")

    growth_axis = parsed["growth_axis"] or parsed["core_thesis"]
    mastery_potential = parsed["mastery_potential"] or parsed["core_thesis"]
    fall_form = parsed["fall_form"]

    text = (
        "Bu yapı zamanla seni sadece güçlü bir kimlik kurmaya değil, aynı zamanda başkalarına yön gösteren, anlam ve vizyon taşıyan bir duruş geliştirmeye iter."
    )

    level = 1
    if capacity_score >= 0.65 and (pressure_index >= 0.55 or integration_score >= 0.70):
        level = 2
    if premium_mode and capacity_score >= 0.75 and pressure_index >= 0.65 and integration_score >= 0.80:
        level = 3

    return {
        "enabled": True,
        "mode": mode,
        "reasons": reasons,
        "reason": reason,
        "content": {
            "growth_axis": growth_axis,
            "mastery_potential": mastery_potential,
            "fall_form": fall_form,
            "evidence": evidence,
        },
        "text": text,
        "thresholds": {
            "pressure_min": pressure_min,
            "support_min": support_min,
            "capacity_min": capacity_min,
            "integration_min": integration_min,
        },
        "debug_scores": {
            "pressure": round(pressure_index, 3),
            "support": round(support_index, 3),
            "capacity": round(capacity_score, 3),
            "integration": round(integration_score, 3),
            "integration_components": integration_components,
        },
        "level": level,
        "debug": {
            "upper_meaning_enabled": enabled,
            "pressure_index": round(pressure_index, 3),
            "support_index": round(support_index, 3),
            "pressure_min": round(pressure_min, 3),
            "support_min": round(support_min, 3),
            "capacity_min": round(capacity_min, 3),
            "integration_min": round(integration_min, 3),
            "mode": mode,
            "alt_gate_enabled": alt_gate_enabled,
            "tension_spine_hit": tension_spine_hit,
            "level": level,
        },
    }


def _parse_upper_meaning_lines(lines: Sequence[str]) -> Dict[str, str]:
    core_thesis = _clean_line(lines[0]) if len(lines) >= 1 else ""
    mastery_potential = _clean_line(lines[1]) if len(lines) >= 2 else ""
    fall_form = ""
    growth_axis = ""
    if len(lines) >= 3:
        third = _clean_line(lines[2])
        fall_form, growth_axis = _split_fall_growth(third)
    return {
        "core_thesis": core_thesis,
        "mastery_potential": mastery_potential,
        "fall_form": fall_form,
        "growth_axis": growth_axis,
    }


def _split_fall_growth(line: str) -> tuple[str, str]:
    lowered = line.lower()
    fall_marker = "basarisiz calisma formu:"
    growth_marker = "evrilmis formu:"
    fall = ""
    growth = ""
    if fall_marker in lowered and growth_marker in lowered:
        pre, post = lowered.split(fall_marker, 1)
        fall_part, growth_part = post.split(growth_marker, 1)
        fall = line[len(pre) + len(fall_marker) : len(pre) + len(fall_marker) + len(fall_part)].strip()
        growth = line[-len(growth_part) :].strip()
        return fall, growth
    if growth_marker in lowered:
        parts = line.split("Evrilmis Formu:", 1)
        if len(parts) == 2:
            growth = parts[1].strip()
    return fall, growth


def _clean_line(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.strip().split())


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _env_float(key: str, default: float) -> float:
    raw = os.getenv(key)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_flag(key: str, default: bool = False) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _has_tension_spine(dynamic_insights: Mapping[str, Any] | None) -> bool:
    if not dynamic_insights:
        return False
    selected = dynamic_insights.get("selected")
    if not isinstance(selected, list):
        return False
    tensions: list[float] = []
    for entry in selected:
        if not isinstance(entry, Mapping):
            continue
        if str(entry.get("kind") or "") != "tension_to_mastery":
            continue
        polarity = entry.get("polarity") or {}
        tension = _safe_float(polarity.get("tension"))
        tensions.append(tension)
    if len(tensions) < 2:
        return False
    avg_tension = sum(tensions) / len(tensions)
    return avg_tension >= 0.55
