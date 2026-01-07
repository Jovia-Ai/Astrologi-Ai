"""Composite layer builder for structural meaning summaries."""
from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence


_SENSITIVITY_MAP = {"low": 0.3, "medium": 0.6, "high": 0.85}


def build_composite_layer(
    composites: Sequence[Mapping[str, Any]] | None,
    *,
    patterns: Mapping[str, Mapping[str, Any]] | None = None,
    axis_activation: Mapping[str, Any] | None = None,
    activation_sensitivity: Mapping[str, str] | None = None,
    meta_summary: Mapping[str, Any] | None = None,
    dispositor_flow: Mapping[str, Any] | None = None,
    meta_info: Mapping[str, Any] | None = None,
) -> list[Dict[str, Any]]:
    composites = list(composites or [])
    patterns = patterns or {}
    axis_activation = axis_activation or {}
    activation_sensitivity = activation_sensitivity or {}
    meta_summary = meta_summary or {}
    dispositor_flow = dispositor_flow or {}
    meta_info = meta_info or {}

    dominant_axis = None
    active_axes = axis_activation.get("active_axes") or []
    if active_axes:
        dominant_axis = str(active_axes[0])

    output: list[Dict[str, Any]] = []
    seen: set[str] = set()
    for comp in composites:
        comp_id = str(comp.get("composite_id") or "")
        if not comp_id or comp_id in seen:
            continue
        seen.add(comp_id)

        meta = patterns.get(comp_id, {})
        strength = _safe_float(meta.get("priority_score"))
        aspect_weight = _safe_float(meta.get("aspect_weight"))
        emotional_weight = min(1.0, aspect_weight / 4) if aspect_weight else 0.3
        structural_importance = strength or 0.3
        narrative_relevance = strength or 0.35
        sensitivity_label = str(activation_sensitivity.get(comp_id) or "low").lower()
        psychological_intensity = _SENSITIVITY_MAP.get(sensitivity_label, 0.3)
        evidence = [str(item) for item in comp.get("sources", []) or [] if item]
        axis_hint = comp.get("axis") or dominant_axis
        axis_overlap = 0.2 if axis_hint and axis_hint in active_axes else 0.0
        focus_score = strength + axis_overlap + psychological_intensity
        evidence_signals = _build_evidence_signals(meta_summary, dispositor_flow, meta_info, axis_activation)

        output.append(
            {
                "composite_id": comp_id,
                "label": _derive_label(
                    comp,
                    meta_summary=meta_summary,
                    axis_activation=axis_activation,
                    dispositor_flow=dispositor_flow,
                    meta_info=meta_info,
                ),
                "domain": str(comp.get("domain") or "identity"),
                "axis": axis_hint,
                "strength": round(strength, 3),
                "strength_score": round(strength, 3),
                "emotional_weight": round(emotional_weight, 3),
                "structural_importance": round(structural_importance, 3),
                "narrative_relevance": round(narrative_relevance, 3),
                "psychological_intensity": round(psychological_intensity, 3),
                "focus_score": round(focus_score, 3),
                "axis_overlap": round(axis_overlap, 3),
                "evidence": evidence,
                "evidence_signals": evidence_signals,
                "domain_hint": str(comp.get("domain") or "identity"),
                "axis_hint": axis_hint,
            }
        )

    return output


def split_composites(
    composites: Sequence[Mapping[str, Any]],
) -> Dict[str, list[Dict[str, Any]]]:
    scored: list[tuple[float, Dict[str, Any]]] = []
    for comp in composites:
        score = _safe_float(comp.get("focus_score"))
        scored.append((score, dict(comp)))
    scored.sort(key=lambda item: item[0], reverse=True)
    focus_count = min(3, len(scored))
    focus = [entry for _score, entry in scored[:focus_count]]
    supporting = [entry for _score, entry in scored[focus_count:]]
    debug: Dict[str, str] = {}
    if not supporting:
        debug["supporting_reason"] = "no_supporting_candidates"
    return {"focus": focus, "supporting": supporting, "debug": debug}


def _derive_label(
    comp: Mapping[str, Any],
    *,
    meta_summary: Mapping[str, Any],
    axis_activation: Mapping[str, Any],
    dispositor_flow: Mapping[str, Any],
    meta_info: Mapping[str, Any],
) -> str:
    for key in ("label", "title"):
        value = comp.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    domain = str(comp.get("domain") or "identity").strip().lower()
    parts: list[str] = []
    domain_label = _domain_label(domain)
    if domain_label:
        parts.append(domain_label)

    tension = str(axis_activation.get("axis_tension") or "").lower()
    tension_label = _tension_label(tension)
    if tension_label:
        parts.append(tension_label)

    planet = _top_planet(meta_summary.get("planet_load_count") or {})
    if planet:
        parts.append(f"{planet} etkisi")

    flow = _flow_label(dispositor_flow.get("dispositor_structure"))
    if flow:
        parts.append(flow)

    cluster = _house_cluster_label(meta_info.get("house_clusters") or {})
    if cluster:
        parts.append(cluster)

    if parts:
        return " + ".join(parts)

    comp_id = str(comp.get("composite_id") or "").replace("_", " ").strip()
    if comp_id:
        return comp_id.title()
    return "Composite"


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _domain_label(domain: str) -> str:
    labels = {
        "identity": "Kontrollu kimlik",
        "psychology": "Derin duygu",
        "relationships": "Iliski kutbu",
        "mind": "Zihinsel odak",
        "career": "Yapi hedefi",
        "karma": "Karmik iz",
    }
    return labels.get(domain, domain.replace("_", " ").title())


def _tension_label(tension: str) -> str:
    if tension == "high":
        return "yuksek gerilim"
    if tension == "medium":
        return "orta gerilim"
    return ""


def _top_planet(planet_counts: Mapping[str, Any]) -> str:
    if not planet_counts:
        return ""
    items = [(str(key), _safe_float(value)) for key, value in planet_counts.items()]
    items.sort(key=lambda item: item[1], reverse=True)
    if not items:
        return ""
    return items[0][0]


def _flow_label(flow: Any) -> str:
    if flow == "loop":
        return "dongu akisi"
    if flow == "fragmented":
        return "daginik akisi"
    if flow == "chain":
        return "zincir akisi"
    return ""


def _house_cluster_label(house_clusters: Mapping[int, int]) -> str:
    if not house_clusters:
        return ""
    strongest = max(house_clusters.values(), default=0)
    if strongest >= 4:
        return "house yogunlugu"
    if strongest >= 3:
        return "house vurgu"
    return ""


def _build_evidence_signals(
    meta_summary: Mapping[str, Any],
    dispositor_flow: Mapping[str, Any],
    meta_info: Mapping[str, Any],
    axis_activation: Mapping[str, Any],
) -> list[str]:
    signals: list[str] = []
    if meta_summary.get("dominant_axis"):
        signals.append("axis_tension")
    if meta_summary.get("planet_load_count"):
        signals.append("planet_load")
    if dispositor_flow.get("dispositor_structure"):
        signals.append("ruler_flow")
    if meta_info.get("house_clusters"):
        signals.append("house_cluster")
    if axis_activation.get("active_axes"):
        signals.append("active_axes")
    return signals
