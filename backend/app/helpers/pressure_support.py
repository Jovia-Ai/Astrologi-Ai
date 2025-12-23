"""Helper that derives pressure/support indices from structural metadata."""
from __future__ import annotations

from math import tanh
from typing import Any, Dict, Iterable, Mapping, Sequence


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def calculate_pressure_support(
    composites: Sequence[Mapping[str, Any]],
    patterns: Mapping[str, Mapping[str, Any]],
    axis_activation: Mapping[str, Any],
) -> Dict[str, Any]:
    """Derive pressure/support metrics used by the expression resolver."""

    axis_tension = str(axis_activation.get("axis_tension") or "low").lower()
    active_axes = [str(axis).lower() for axis in axis_activation.get("active_axes") or []]
    axis_balance = len(active_axes) >= 2
    tension_map = {"low": 0.25, "medium": 0.55, "high": 0.85}
    hardness = min(1.0, tension_map.get(axis_tension, 0.25) + len(active_axes) * 0.05)
    unique_domains = {str(comp.get("domain") or "").lower() for comp in composites if comp.get("domain")}
    repetition_load = min(1.0, max(0.0, (len(unique_domains) - 1) / 3))
    life_stage_pressure = 0.3 if axis_tension == "high" else 0.1 if axis_tension == "medium" else 0.0
    centrality = 0.25 if axis_balance else 0.1

    raw_pressure = hardness * (1 + repetition_load + life_stage_pressure) + centrality

    struct_support = 0.0
    for comp in composites:
        domain = str(comp.get("domain") or "").lower()
        if domain in {"identity", "psychology", "relationships"}:
            struct_support += 0.1

    structural_support = min(1.0, struct_support)
    domain_support = min(1.0, len(unique_domains) / 4)
    temporal_support = 0.2 if axis_tension == "low" else 0.1
    soft_support = min(1.0, 0.35 if axis_balance else 0.15 + len(active_axes) * 0.05)

    raw_support = soft_support + structural_support + domain_support + temporal_support

    pressure_index = _clamp(tanh(raw_pressure))
    support_index = _clamp(tanh(raw_support))

    domain_scores: Dict[str, float] = {}
    for comp in composites:
        domain = str(comp.get("domain") or "identity").lower()
        comp_id = comp.get("composite_id") or ""
        priority = float(patterns.get(comp_id, {}).get("priority_score") or 0.0)
        domain_scores[domain] = max(domain_scores.get(domain, 0.0), priority)
    dominant_domain = max(domain_scores, key=domain_scores.get) if domain_scores else "identity"

    dominant_axis = active_axes[0] if active_axes else "1-7"

    sorted_patterns = sorted(
        patterns.items(),
        key=lambda item: float(item[1].get("priority_score") or 0.0),
        reverse=True,
    )
    themes = [entry[0] for entry in sorted_patterns[:3]]
    if not themes:
        themes = [dominant_domain]

    return {
        "pressure_index": pressure_index,
        "support_index": support_index,
        "axis_balance": axis_balance,
        "dominant_domain": dominant_domain,
        "dominant_axis": dominant_axis,
        "themes": themes,
    }
