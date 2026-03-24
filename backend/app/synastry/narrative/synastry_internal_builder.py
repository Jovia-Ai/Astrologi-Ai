from __future__ import annotations

from typing import Any, Mapping, Sequence


def _round_score(value: Any) -> float:
    try:
        return round(float(value), 4)
    except (TypeError, ValueError):
        return 0.0


def _materialize_debug_entries(items: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in items:
        out.append(
            {
                "id": str(item.get("id") or ""),
                "source_debug": [str(value).strip() for value in (item.get("source_debug") or []) if str(value).strip()],
                "primary_signature_id": str(item.get("primary_signature_id") or ""),
                "support_signature_ids": [
                    str(value).strip() for value in (item.get("support_signature_ids") or []) if str(value).strip()
                ],
                "confidence": _round_score(item.get("confidence")),
            }
        )
    return [item for item in out if item["id"]]


def build_synastry_imprint_internal(selection: Mapping[str, Any]) -> dict[str, Any] | None:
    if not isinstance(selection, Mapping):
        return None
    pair_signature_debug = _materialize_debug_entries(selection.get("pair_signature") or [])
    a_to_b_debug = _materialize_debug_entries(selection.get("a_to_b") or [])
    b_to_a_debug = _materialize_debug_entries(selection.get("b_to_a") or [])
    together_field_debug = _materialize_debug_entries(selection.get("together_field") or [])
    if not pair_signature_debug and not a_to_b_debug and not b_to_a_debug and not together_field_debug:
        return None
    return {
        "version": "synastry_imprint_v1_debug",
        "pair_signature_debug": pair_signature_debug,
        "a_to_b_debug": a_to_b_debug,
        "b_to_a_debug": b_to_a_debug,
        "together_field_debug": together_field_debug,
    }
