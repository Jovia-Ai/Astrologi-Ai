"\"\"\"Builds a narrative guidance object from structural composite metadata.\"\"\""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Sequence


def build_guidance(
    composites: Sequence[Mapping[str, Any]],
    patterns: Mapping[str, Mapping[str, Any]],
    meta_info: Mapping[str, Any],
    dispositor_flow: Mapping[str, Any],
    axis_activation: Mapping[str, Any],
    activation_sensitivity: Mapping[str, str],
) -> Dict[str, Any]:
    active_domains = sorted({str(comp.get("domain")).lower() for comp in composites if comp.get("domain")})
    domain_priority: Dict[str, float] = {}
    for comp in composites:
        domain = str(comp.get("domain")).lower()
        comp_id = comp.get("composite_id")
        priority = 0.0
        if comp_id:
            priority = float(patterns.get(comp_id, {}).get("priority_score") or 0.0)
        current = domain_priority.get(domain, 0.0)
        if priority > current:
            domain_priority[domain] = priority

    stellium_domains = []
    for comp in composites:
        comp_id = comp.get("composite_id")
        if not comp_id:
            continue
        if patterns.get(comp_id, {}).get("stellium"):
            stellium_domains.append(str(comp.get("domain")).lower())
    element = None
    dominant_elements = meta_info.get("dominant_elements") or {}
    if dominant_elements:
        element = next(iter(dominant_elements), None)

    tone_modifiers = {
        "conflict_level": _map_conflict(axis_activation.get("axis_tension")),
        "flow_state": _map_flow(dispositor_flow.get("dispositor_structure")),
        "intensity": _map_intensity(activation_sensitivity.values()),
        "temporal_mode": _map_temporal(axis_activation.get("axis_tension")),
        "effort_tone": "engaged" if dispositor_flow.get("dispositor_structure") == "loop" else "steady",
        "awareness_tone": "sensitive" if element else "attentive",
    }

    derived_signals = _collect_derived_signals(composites)

    guidance = {
        "active_domains": active_domains,
        "domain_priority": domain_priority,
        "dominance": {
            "stellium_domains": sorted(set(stellium_domains)),
            "element": element,
            "modality": _map_modality(meta_info.get("dominant_modalities")),
        },
        "derived_signals": derived_signals,
        "tone_modifiers": tone_modifiers,
        "axis_tension": axis_activation.get("axis_tension"),
        "sensitivity": activation_sensitivity,
    }
    return guidance


def _map_conflict(tension: object | None) -> str:
    if tension == "high":
        return "high"
    if tension == "medium":
        return "medium"
    return "low"


def _map_flow(structure: object | None) -> str:
    if structure == "loop":
        return "cyclical"
    if structure == "fragmented":
        return "fragmented"
    return "natural"


def _map_intensity(levels: Iterable[str]) -> str:
    normalized = {str(level).lower() for level in levels if level}
    if "high" in normalized:
        return "high"
    if "medium" in normalized:
        return "medium"
    return "background"


def _map_temporal(tension: object | None) -> str:
    if tension == "high":
        return "dynamic"
    if tension == "low":
        return "steady"
    return "integrated"


def _map_modality(modality: Mapping[str, Any] | None) -> str | None:
    if not modality:
        return None
    return next(iter(modality), None)


def _collect_derived_signals(composites: Sequence[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
    signals: Dict[str, Dict[str, Any]] = {}
    for comp in composites:
        domain = str(comp.get("domain") or "").lower()
        derived = comp.get("derived_signals") or {}
        if derived:
            existing = signals.setdefault(domain, {})
            for key, value in derived.items():
                if key not in existing:
                    existing[key] = value
    return signals
