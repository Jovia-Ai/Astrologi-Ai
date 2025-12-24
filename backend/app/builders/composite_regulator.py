from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Sequence

DEFAULT_WEIGHTS: Dict[str, float] = {
    "mechanism": 0.2,
    "effect": 0.25,
    "shadow": 0.25,
    "potential": 0.3,
}


def build_composite_regulation(
    composites: Sequence[Mapping[str, Any]],
    patterns: Mapping[str, Mapping[str, Any]],
    axis_activation: Mapping[str, Any],
) -> Dict[str, Dict[str, Any]]:
    regulator: Dict[str, Dict[str, Any]] = {}
    axis_tension = str(axis_activation.get("axis_tension") or "").lower()
    energy_pressure = _map_energy_pressure(axis_tension)

    for composite in composites:
        comp_id = composite.get("composite_id")
        if not comp_id:
            continue
        meta = patterns.get(comp_id, {})
        priority = _derive_priority(composite, meta)
        tension_type = _derive_tension_type(axis_tension, composite, meta)
        regulation_axis = _derive_regulation_axis(tension_type)
        weights = _build_slot_weights(priority)
        upper_meaning_gate = energy_pressure == "high" and priority >= 0.7
        regulator[comp_id] = {
            "composite_id": comp_id,
            "tension_type": tension_type,
            "regulation_axis": regulation_axis,
            "energy_pressure": energy_pressure,
            "weights": weights,
            "upper_meaning_gate": upper_meaning_gate,
        }
    return regulator


def _derive_priority(composite: Mapping[str, Any], meta: Mapping[str, Any]) -> float:
    score = meta.get("priority_score") or composite.get("priority_score") or 0.0
    try:
        return float(score)
    except (TypeError, ValueError):
        return 0.0


def _derive_tension_type(axis_tension: str, composite: Mapping[str, Any], meta: Mapping[str, Any]) -> str:
    if axis_tension == "high" or meta.get("tension_high") or composite.get("tension_high"):
        return "visibility_vs_control"
    if meta.get("stellium") or composite.get("stellium"):
        return "trait_reinforcement"
    return "balanced_flow"


def _derive_regulation_axis(tension_type: str) -> str:
    axes = {
        "visibility_vs_control": "expression ↔ containment",
        "trait_reinforcement": "amplification ↔ stabilization",
        "balanced_flow": "integration ↔ clarity",
    }
    return axes.get(tension_type, "integration ↔ clarity")


def _map_energy_pressure(axis_tension: str) -> str:
    if axis_tension == "high":
        return "high"
    if axis_tension == "medium":
        return "medium"
    return "low"


def _build_slot_weights(priority: float) -> Dict[str, float]:
    base = DEFAULT_WEIGHTS.copy()
    modifier = max(-0.05, min(0.05, (priority - 0.5) / 5))
    adjusted: Dict[str, float] = {}
    for slot, weight in base.items():
        adjusted[slot] = max(0.0, weight + modifier)
    total = sum(adjusted.values()) or 1.0
    return {slot: round(value / total, 4) for slot, value in adjusted.items()}
