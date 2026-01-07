"""Conflict vector builder that turns phase-2 signals into pressure/support diagnostics."""

from __future__ import annotations

from collections import Counter
from math import tanh
from typing import Iterable, Mapping, Sequence

from app.builders.ssl_layer import SSLLayer


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


class ConflictVectorBuilderError(Exception):
    """Raised when conflict vector building fails."""


class ConflictVectorBuilder:
    """Builds pressure/support metadata for deterministic compilers."""

    _LIFE_STAGE_PRESSURE_TYPES = {"life_stage_bound", "episodic"}
    _CENTRAL_FOCUS_HIGH = {"chart_ruler", "asc", "mc"}

    def __init__(self, ssl_layer: SSLLayer | None = None):
        self.ssl_layer = ssl_layer or SSLLayer()

    def build(
        self,
        phase2_slots: Sequence[Mapping[str, object]],
        *,
        chart_stage: str = "mid",
    ) -> Mapping[str, object]:
        if not phase2_slots:
            raise ConflictVectorBuilderError("No phase-2 slots provided.")
        ssl_reports = self.ssl_layer.apply(phase2_slots, chart_stage=chart_stage)
        ssl_components = self._aggregate_ssl_components(ssl_reports)
        hardness = self._compute_hardness(phase2_slots)
        repetition = ssl_components.get("repetition_across_domains", 0.0)
        life_stage_pressure = 0.3 if self._has_life_stage_pressure(phase2_slots) else 0.0
        centrality = self._compute_centrality(phase2_slots)
        raw_pressure = hardness * (1 + repetition + life_stage_pressure) + centrality
        soft_support = self._compute_soft_support(phase2_slots)
        structural_support = self._compute_structural_support(phase2_slots)
        axis_balanced = any(slot.get("axis_balanced") for slot in phase2_slots)
        domain_support = self._compute_domain_support(phase2_slots, axis_balanced)
        temporal_support = 0.2 if self._has_constant_activation(phase2_slots) else 0.0
        raw_support = soft_support + structural_support + domain_support + temporal_support
        pressure_index = _clamp(tanh(raw_pressure))
        support_index = _clamp(tanh(raw_support))
        has_hard_tag = any("hard" in self._tags(slot) for slot in phase2_slots)
        pressure_index = self._apply_pressure_guards(
            pressure_index, hardness, repetition, soft_support, has_hard_tag
        )
        support_index = self._apply_support_guards(support_index, soft_support)
        felt_net = pressure_index - support_index
        breakdown = {
            "hardness": _clamp(hardness),
            "repetition": _clamp(repetition * 0.4),
            "life_stage": life_stage_pressure,
            "centrality": centrality,
            "soft_support": soft_support,
            "structural_support": structural_support,
            "domain_support": domain_support,
            "temporal_support": temporal_support,
        }
        focus_object = self._pick_focus(phase2_slots)
        conflict_bundle = {
            "focus_object": focus_object,
            "pressure_index": pressure_index,
            "support_index": support_index,
            "net_vector": _clamp(felt_net, -1.0, 1.0),
            "component_breakdown": breakdown,
            "ssl_components": ssl_components,
            "provenance_summary": self._build_provenance_summary(phase2_slots),
            "vector_context": self._build_vector_context(phase2_slots, pressure_index, support_index),
            "high_load_high_capacity": pressure_index > 0.6 and support_index > 0.6,
        }
        return {"conflict_bundle": conflict_bundle}

    def _compute_hardness(self, slots: Sequence[Mapping[str, object]]) -> float:
        total = 0.0
        repeats: Counter[str] = Counter()
        for slot in slots:
            if not self._is_hard(slot):
                continue
            weight = float(slot.get("experienced_weight", 0.0))
            orb_strength = self._orb_strength(slot)
            total += weight * orb_strength
            repeats[self._repeat_key(slot)] += 1
            if "tight_orb" in self._tags(slot):
                total += 0.05
        for repeat_count in repeats.values():
            if repeat_count > 1:
                total += 0.04 * (repeat_count - 1)
        return total

    def _compute_soft_support(self, slots: Sequence[Mapping[str, object]]) -> float:
        total = 0.0
        for slot in slots:
            if not self._is_soft(slot):
                continue
            weight = float(slot.get("experienced_weight", 0.0))
            total += weight * self._orb_strength(slot)
        return total

    def _compute_structural_support(self, slots: Sequence[Mapping[str, object]]) -> float:
        support = 0.0
        if any(slot.get("dispositor_loop_supportive") for slot in slots):
            support += 0.25
        if any(slot.get("axis_balanced") for slot in slots):
            support += 0.2
        return _clamp(support)

    def _compute_domain_support(self, slots: Sequence[Mapping[str, object]], axis_balanced: bool) -> float:
        domains = {slot.get("domain") for slot in slots if slot.get("domain")}
        base = min(len(domains) / 3, 1.0)
        return base * (0.3 if axis_balanced else 0.15)

    def _orb_strength(self, slot: Mapping[str, object]) -> float:
        explicit = slot.get("orb_strength")
        if explicit is not None:
            return _clamp(float(explicit))
        orb = slot.get("orb")
        if orb is not None:
            orbit = float(orb)
            return _clamp(1.0 - (orbit / 10.0))
        return 1.0 if "tight_orb" in self._tags(slot) else 0.6

    def _central_focus(self, slot: Mapping[str, object]) -> float:
        focus = str(slot.get("focus_object", "")).lower()
        if focus in self._CENTRAL_FOCUS_HIGH:
            return 0.3
        if slot.get("stellium_core"):
            return 0.2
        return 0.0

    def _compute_centrality(self, slots: Sequence[Mapping[str, object]]) -> float:
        return max(self._central_focus(slot) for slot in slots)

    def _tags(self, slot: Mapping[str, object]) -> list[str]:
        tags = slot.get("trigger_tags")
        if not isinstance(tags, Iterable):
            return []
        return [str(tag).lower() for tag in tags]

    def _repeat_key(self, slot: Mapping[str, object]) -> str:
        return f"{slot.get('theme', '')}:{slot.get('axis', '')}:{slot.get('focus_object', '')}"

    def _is_hard(self, slot: Mapping[str, object]) -> bool:
        tags = self._tags(slot)
        aspect = str(slot.get("aspect_type", "")).lower()
        return "hard" in tags or aspect == "hard" or slot.get("slot") in {"cause", "mechanism"}

    def _is_soft(self, slot: Mapping[str, object]) -> bool:
        tags = self._tags(slot)
        aspect = str(slot.get("aspect_type", "")).lower()
        return "soft" in tags or aspect == "soft" or slot.get("slot") in {"effect", "potential"}

    def _has_life_stage_pressure(self, slots: Sequence[Mapping[str, object]]) -> bool:
        return any(
            str(slot.get("activation_type", "")).lower() in self._LIFE_STAGE_PRESSURE_TYPES
            for slot in slots
        )

    def _has_constant_activation(self, slots: Sequence[Mapping[str, object]]) -> bool:
        return any(str(slot.get("activation_type", "")).lower() == "constant" for slot in slots)

    def _aggregate_ssl_components(self, reports: Sequence[Mapping[str, object]]) -> Mapping[str, float]:
        totals: Counter[str] = Counter()
        for report in reports:
            totals["repetition_across_domains"] += float(report.get("repetition_penalty", 0.0))
            totals["life_stage_alignment"] += float(report.get("life_stage_alignment", 0.0))
            totals["identity_axis_overlap"] += float(report.get("axis_overlap", 0.0))
        result = {}
        for key in ("repetition_across_domains", "life_stage_alignment", "identity_axis_overlap"):
            result[key] = _clamp(totals.get(key, 0.0))
        return result

    def _apply_pressure_guards(
        self,
        pressure_index: float,
        hardness: float,
        repetition: float,
        soft_support: float,
        has_hard_tag: bool,
    ) -> float:
        if pressure_index > 0.7 and hardness < 0.3:
            pressure_index = max(0.0, pressure_index - 0.1)
        if pressure_index < 0.3 and repetition * 0.4 > 0.25:
            pressure_index = max(0.35, pressure_index)
        if pressure_index > 0.9 and soft_support < 0.1:
            pressure_index = 0.9
        if has_hard_tag:
            pressure_index = min(pressure_index, 0.7)
        return _clamp(pressure_index)

    def _apply_support_guards(self, support_index: float, soft_support: float) -> float:
        if support_index > 0.6 and soft_support == 0.0:
            support_index = max(0.0, support_index - 0.1)
        return _clamp(support_index)

    def _build_vector_context(
        self,
        slots: Sequence[Mapping[str, object]],
        pressure_index: float,
        support_index: float,
    ) -> Mapping[str, object]:
        dominant_domain = self._dominant_key(slots, "domain")
        dominant_axis = self._dominant_key(slots, "axis")
        centrality = self._dominant_key(slots, "focus_object")
        focus_tier = self._focus_tier(centrality)
        return {
            "dominant_domain": dominant_domain,
            "dominant_axis": dominant_axis,
            "focus_centrality_tier": focus_tier,
            "pressure_support_state": self._pressure_support_state(pressure_index, support_index),
        }

    def _dominant_key(self, slots: Sequence[Mapping[str, object]], key: str) -> str:
        counts: Counter[str] = Counter()
        for slot in slots:
            value = slot.get(key)
            if value:
                counts[str(value)] += 1
        if not counts:
            return "unknown"
        return counts.most_common(1)[0][0]

    def _focus_tier(self, focus: str) -> str:
        focus = str(focus or "").lower()
        if focus in self._CENTRAL_FOCUS_HIGH:
            return "high"
        if focus:
            return "mid"
        return "low"

    def _pressure_support_state(self, pressure: float, support: float) -> str:
        if pressure >= 0.7 and support >= 0.7:
            return "resilient_pressure"
        if pressure >= 0.7:
            return "high_pressure"
        if support >= 0.7:
            return "high_support"
        return "balanced"

    def _pick_focus(self, slots: Sequence[Mapping[str, object]]) -> str:
        focus = self._dominant_key(slots, "focus_object")
        return focus if focus != "unknown" else "general"

    def _build_provenance_summary(self, slots: Sequence[Mapping[str, object]]) -> list[Mapping[str, object]]:
        summary: list[Mapping[str, object]] = []
        for slot in slots[:3]:
            prov = slot.get("provenance", [])
            summary.append(
                {
                    "signal_id": slot.get("signal_id"),
                    "provenance": prov[:2] if isinstance(prov, list) else [],
                }
            )
        return summary
