from __future__ import annotations

from typing import Any, Dict, Mapping
from uuid import uuid4

TRACE_EVENT_NAME = "transit_trace"
TRACE_ROUTE_VERSION = "v1"
TRACE_OBSERVABILITY_STAGE = "phase0_pr1"


def generate_snapshot_id() -> str:
    return f"trsnap_{uuid4().hex}"


def inject_snapshot_meta(
    payload: Any,
    *,
    endpoint: str,
    snapshot_id: str,
) -> Any:
    if not isinstance(payload, Mapping):
        return payload

    out = dict(payload)
    meta_raw = out.get("meta")
    meta: Dict[str, Any] = dict(meta_raw) if isinstance(meta_raw, Mapping) else {}
    source_meta_raw = meta.get("source_meta")
    source_meta: Dict[str, Any] = (
        dict(source_meta_raw) if isinstance(source_meta_raw, Mapping) else {}
    )

    meta.setdefault("snapshot_id", snapshot_id)
    source_meta.setdefault("endpoint", endpoint)
    source_meta.setdefault("route_version", TRACE_ROUTE_VERSION)
    source_meta.setdefault("observability_stage", TRACE_OBSERVABILITY_STAGE)
    meta["source_meta"] = source_meta
    out["meta"] = meta
    return out


def build_route_trace_log_payload(
    *,
    endpoint: str,
    snapshot_id: str,
    client_trace_id: str | None,
    client_surface: str | None,
    duration_ms: float,
    payload_bytes: int,
    extra_fields: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "event": TRACE_EVENT_NAME,
        "endpoint": endpoint,
        "snapshot_id": snapshot_id,
        "client_trace_id": client_trace_id,
        "client_surface": client_surface,
        "status": "ok",
        "duration_ms": round(duration_ms, 3),
        "payload_bytes": payload_bytes,
        "observability_stage": TRACE_OBSERVABILITY_STAGE,
    }
    if extra_fields:
        payload.update(dict(extra_fields))
    return payload
