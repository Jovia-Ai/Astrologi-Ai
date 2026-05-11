from __future__ import annotations

from typing import Any, Mapping

from pydantic import BaseModel, ConfigDict, Field


class LegacyNatalReasoningBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chart_id: str
    raw_chart: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    dispositor_data: dict[str, Any] | None = None
    natal_graph: dict[str, Any] | None = None
    natal_graph_v2: dict[str, Any] | None = None
    feature_graph: dict[str, Any] | None = None
    promise_vectors: dict[str, Any] | None = None
    contradiction_signatures: dict[str, Any] | None = None
    master_selector: dict[str, Any] | None = None
    source_trace: dict[str, str] = Field(default_factory=dict)

    @property
    def legacy_sources_used(self) -> list[str]:
        ordered_sources = [
            "dispositor_data",
            "natal_graph",
            "natal_graph_v2",
            "feature_graph",
            "promise_vectors",
            "contradiction_signatures",
            "master_selector",
        ]
        return [name for name in ordered_sources if getattr(self, name) is not None]


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _chart_id_from_payload(payload: Mapping[str, Any]) -> str:
    metadata = payload.get("metadata")
    if isinstance(metadata, Mapping):
        candidate = metadata.get("chart_id") or metadata.get("birth_datetime")
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    chart_data = payload.get("chart_data")
    if isinstance(chart_data, Mapping):
        birth_date = str(chart_data.get("birth_date") or "").strip()
        birth_time = str(chart_data.get("birth_time") or "").strip()
        birth_place = str(chart_data.get("birth_place") or "").strip()
        if birth_date and birth_time and birth_place:
            normalized_place = birth_place.lower().replace(" ", "_")
            return f"{birth_date}_{birth_time}_{normalized_place}"
    return "unknown_chart"


def build_legacy_natal_bundle_from_base_payload(
    base_payload: Mapping[str, Any],
) -> LegacyNatalReasoningBundle:
    payload = dict(base_payload or {})
    return LegacyNatalReasoningBundle(
        chart_id=_chart_id_from_payload(payload),
        raw_chart=_as_dict(payload.get("chart_data")),
        metadata=_as_dict(payload.get("metadata")),
        dispositor_data=_as_dict(payload.get("dispositor_flow")) or None,
        natal_graph=_as_dict(payload.get("natal_graph")) or None,
        natal_graph_v2=_as_dict(payload.get("_natal_graph_v2")) or None,
        feature_graph=_as_dict(payload.get("_natal_feature_graph_v2")) or None,
        promise_vectors=(
            _as_dict((_as_dict(payload.get("_natal_graph_v2"))).get("promise_vectors")) or None
        ),
        contradiction_signatures=_as_dict(payload.get("_contradiction_signatures_v1")) or None,
        master_selector=_as_dict(payload.get("_master_selector_v1")) or None,
        source_trace={
            "dispositor_data": "base_payload.dispositor_flow",
            "natal_graph": "base_payload.natal_graph",
            "natal_graph_v2": "base_payload._natal_graph_v2",
            "feature_graph": "base_payload._natal_feature_graph_v2",
            "promise_vectors": "base_payload._natal_graph_v2.promise_vectors",
            "contradiction_signatures": "base_payload._contradiction_signatures_v1",
            "master_selector": "base_payload._master_selector_v1",
        },
    )


def build_legacy_natal_bundle_from_chart(
    chart_data: Mapping[str, Any],
    *,
    metadata: Mapping[str, Any] | None = None,
    dispositor_data: Mapping[str, Any] | None = None,
    natal_graph: Mapping[str, Any] | None = None,
    natal_graph_v2: Mapping[str, Any] | None = None,
    feature_graph: Mapping[str, Any] | None = None,
    promise_vectors: Mapping[str, Any] | None = None,
    contradiction_signatures: Mapping[str, Any] | None = None,
    master_selector: Mapping[str, Any] | None = None,
) -> LegacyNatalReasoningBundle:
    raw_chart = dict(chart_data or {})
    return LegacyNatalReasoningBundle(
        chart_id=_chart_id_from_payload({"chart_data": raw_chart, "metadata": metadata or {}}),
        raw_chart=raw_chart,
        metadata=_as_dict(metadata),
        dispositor_data=_as_dict(dispositor_data) or None,
        natal_graph=_as_dict(natal_graph) or None,
        natal_graph_v2=_as_dict(natal_graph_v2) or None,
        feature_graph=_as_dict(feature_graph) or None,
        promise_vectors=_as_dict(promise_vectors) or None,
        contradiction_signatures=_as_dict(contradiction_signatures) or None,
        master_selector=_as_dict(master_selector) or None,
        source_trace={
            "dispositor_data": "explicit_argument.dispositor_data",
            "natal_graph": "explicit_argument.natal_graph",
            "natal_graph_v2": "explicit_argument.natal_graph_v2",
            "feature_graph": "explicit_argument.feature_graph",
            "promise_vectors": "explicit_argument.promise_vectors",
            "contradiction_signatures": "explicit_argument.contradiction_signatures",
            "master_selector": "explicit_argument.master_selector",
        },
    )

