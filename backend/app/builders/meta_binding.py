"""Meta summary builder for structural pressure/support insights."""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, Mapping, Sequence


_AXIS_TENSION_MAP = {"low": 0.25, "medium": 0.55, "high": 0.85}
_SENSITIVITY_MAP = {"low": 0.3, "medium": 0.6, "high": 0.85}
_AXES = ("1-7", "4-10", "2-8", "3-9")


def build_meta_summary(
    *,
    composites: Sequence[Mapping[str, Any]] | None = None,
    patterns: Mapping[str, Mapping[str, Any]] | None = None,
    axis_activation: Mapping[str, Any] | None = None,
    pressure_support: Mapping[str, Any] | None = None,
    dispositor_flow: Mapping[str, Any] | None = None,
    meta_info: Mapping[str, Any] | None = None,
    placements: Sequence[str] | None = None,
    core_aspects: Sequence[str] | None = None,
) -> Dict[str, Any]:
    composites = list(composites or [])
    patterns = patterns or {}
    axis_activation = axis_activation or {}
    pressure_support = pressure_support or {}
    dispositor_flow = dispositor_flow or {}
    meta_info = meta_info or {}

    dominant_domains = _build_dominant_domains(composites, patterns)
    axis_rank = _build_axis_rank(axis_activation, pressure_support)
    dominant_axis = axis_rank[0] if axis_rank else _default_axis_entry(pressure_support)
    pressure_index = _safe_float(pressure_support.get("pressure_index"))
    support_index = _safe_float(pressure_support.get("support_index"))
    regulation_required = pressure_index >= 0.65 and support_index <= 0.45
    planet_load_count = _build_planet_load_counts(placements, core_aspects, meta_info)
    load_level = _planet_load_level(planet_load_count)
    psychological_intensity = _clamp(0.6 * pressure_index + 0.4 * load_level)
    house_cluster_weights = _build_house_cluster_weights(meta_info)
    ruler_flow = _build_ruler_flow(dispositor_flow)

    meta_summary_text = _build_meta_summary_text(
        dominant_domains=dominant_domains,
        dominant_axis=dominant_axis,
        pressure_index=pressure_index,
        support_index=support_index,
        regulation_required=regulation_required,
    )

    return {
        "dominant_domains": dominant_domains,
        "dominant_axis": dominant_axis,
        "axis_rank": axis_rank,
        "pressure_index": pressure_index,
        "support_index": support_index,
        "psychological_intensity": psychological_intensity,
        "regulation_required": regulation_required,
        "ruler_flow": ruler_flow,
        "house_cluster_weights": house_cluster_weights,
        "planet_load_count": planet_load_count,
        "meta_summary_text": meta_summary_text,
        "debug": {
            "axis_tension": axis_activation.get("axis_tension"),
            "active_axes": axis_activation.get("active_axes"),
            "pressure_support_source": {
                "pressure_index": pressure_support.get("pressure_index"),
                "support_index": pressure_support.get("support_index"),
            },
            "planet_load_level": load_level,
        },
    }


def _build_dominant_domains(
    composites: Sequence[Mapping[str, Any]],
    patterns: Mapping[str, Mapping[str, Any]],
) -> list[Dict[str, float]]:
    scores: Dict[str, float] = {}
    for comp in composites:
        domain = str(comp.get("domain") or "identity").lower()
        comp_id = str(comp.get("composite_id") or "")
        priority = _safe_float(patterns.get(comp_id, {}).get("priority_score"))
        scores[domain] = scores.get(domain, 0.0) + priority
    if not scores:
        scores = {"identity": 0.0}
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return [{"domain": domain, "score": round(score, 3)} for domain, score in ranked[:3]]


def _build_axis_rank(
    axis_activation: Mapping[str, Any],
    pressure_support: Mapping[str, Any],
) -> list[Dict[str, float]]:
    axis_tension_label = str(axis_activation.get("axis_tension") or "low").lower()
    tension_value = _AXIS_TENSION_MAP.get(axis_tension_label, 0.25)
    support_index = _safe_float(pressure_support.get("support_index"))
    active_axes = [str(axis) for axis in axis_activation.get("active_axes") or []]
    axes = active_axes or list(_AXES)
    entries = [
        {
            "axis": axis,
            "tension": round(tension_value, 3),
            "support": round(support_index, 3),
        }
        for axis in axes
    ]
    return sorted(entries, key=lambda item: item["tension"], reverse=True)


def _default_axis_entry(pressure_support: Mapping[str, Any]) -> Dict[str, float]:
    support_index = _safe_float(pressure_support.get("support_index"))
    return {"axis": "1-7", "tension": 0.25, "support": round(support_index, 3)}


def _build_ruler_flow(dispositor_flow: Mapping[str, Any]) -> Dict[str, Any]:
    flow_type = dispositor_flow.get("dispositor_structure")
    if not flow_type:
        return {"final_ruler": None, "flow_type": None, "harshness": None}
    harshness = {"loop": 0.8, "fragmented": 0.6, "chain": 0.4}.get(str(flow_type), 0.4)
    return {
        "final_ruler": dispositor_flow.get("final_dispositor"),
        "flow_type": flow_type,
        "harshness": harshness,
    }


def _build_house_cluster_weights(meta_info: Mapping[str, Any]) -> Dict[str, float]:
    house_counts = meta_info.get("house_counts") or {}
    angular = _sum_houses(house_counts, {1, 4, 7, 10})
    succedent = _sum_houses(house_counts, {2, 5, 8, 11})
    cadent = _sum_houses(house_counts, {3, 6, 9, 12})
    total = angular + succedent + cadent
    if total <= 0:
        return {"angular": 0.0, "succedent": 0.0, "cadent": 0.0}
    return {
        "angular": round(angular / total, 3),
        "succedent": round(succedent / total, 3),
        "cadent": round(cadent / total, 3),
    }


def _sum_houses(house_counts: Mapping[int, int], houses: Iterable[int]) -> int:
    total = 0
    for house in houses:
        total += int(house_counts.get(house, 0) or 0)
    return total


def _build_planet_load_counts(
    placements: Sequence[str] | None,
    core_aspects: Sequence[str] | None,
    meta_info: Mapping[str, Any],
) -> Dict[str, int]:
    counts: Counter[str] = Counter()
    if placements:
        for placement in placements:
            planet = str(placement).split("_in_", 1)[0]
            if planet:
                counts[planet] += 1
    if core_aspects:
        for aspect in core_aspects:
            parts = str(aspect).split("_")
            if len(parts) >= 3:
                counts[parts[0]] += 1
                counts[parts[2]] += 1
    if not counts:
        for planet in (meta_info.get("planet_signs") or {}).keys():
            counts[str(planet)] += 1
    formatted = {str(key).title(): int(value) for key, value in counts.items()}
    return dict(sorted(formatted.items(), key=lambda item: item[1], reverse=True))


def _planet_load_level(planet_counts: Mapping[str, int]) -> float:
    max_count = max(planet_counts.values(), default=0)
    if max_count >= 5:
        return 0.85
    if max_count >= 3:
        return 0.55
    return 0.25


def _build_meta_summary_text(
    *,
    dominant_domains: Sequence[Mapping[str, Any]],
    dominant_axis: Mapping[str, Any],
    pressure_index: float,
    support_index: float,
    regulation_required: bool,
) -> str:
    domain_names = [entry.get("domain") for entry in dominant_domains if entry.get("domain")]
    axis = dominant_axis.get("axis") or "1-7"
    tension_value = _safe_float(dominant_axis.get("tension"))
    tension_label = "yuksek" if tension_value >= 0.7 else "orta" if tension_value >= 0.4 else "dusuk"
    pressure_label = "yuksek" if pressure_index >= 0.65 else "orta" if pressure_index >= 0.45 else "dusuk"
    support_label = "sinirli" if support_index <= 0.4 else "orta" if support_index <= 0.6 else "guclu"

    if len(domain_names) >= 2:
        domain_sentence = f"Bu sistemde {domain_names[0]} ve {domain_names[1]} alanlari yogun calisiyor."
    elif domain_names:
        domain_sentence = f"Bu sistemde {domain_names[0]} alani yogun calisiyor."
    else:
        domain_sentence = "Bu sistemde baskin alanlar aktif."

    axis_sentence = f"{axis} ekseni {tension_label} gerilim tasiyor."
    pressure_sentence = f"Baski {pressure_label}, destek {support_label}."
    if regulation_required:
        regulation_sentence = "Hayat bu yapinin ciddiye alinmasini zorunlu kiliyor."
    else:
        regulation_sentence = "Yapi duzenlenebilir bir dengede ilerliyor."

    return " ".join([domain_sentence, axis_sentence, pressure_sentence, regulation_sentence])


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))
