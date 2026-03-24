from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence

from .bundles import build_signature_bundles
from .contracts import (
    PERSONALITY_IMPRINT_ENGINE_VERSION,
    PERSONALITY_IMPRINT_LIBRARY_VERSION,
    PERSONALITY_IMPRINT_RENDER_SHAPE,
)
from .selector import select_personality_imprint_entries


def build_personality_imprint(
    *,
    planets: Sequence[Mapping[str, Any]],
    aspects: Sequence[Mapping[str, Any]],
    natal_graph: Mapping[str, Any],
    locale: str = "tr",
    include_debug: bool = False,
) -> Dict[str, Any]:
    selection = select_personality_imprint_entries(
        planets=planets,
        aspects=aspects,
        natal_graph=natal_graph,
    )
    bundle_payload = build_signature_bundles(
        dominant_candidates=selection["ranked"],
        planets=planets,
        natal_graph=natal_graph,
    )
    bundle_support_map = bundle_payload["debug"]["bundle_support_map"]

    def _materialize_entries(items: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
        entries = []
        for item in items:
            if not isinstance(item.get("entry"), Mapping):
                continue
            entry = dict(item["entry"])
            entry["support_keys"] = list(bundle_support_map.get(str(entry.get("key") or ""), []))
            entries.append(entry)
        return entries

    entries = _materialize_entries(selection["selected"])
    extra_entries = _materialize_entries(selection["extras"])
    selected_keys = {str(entry.get("key") or "") for entry in entries}
    extra_keys = {str(entry.get("key") or "") for entry in extra_entries}
    bundles = [
        dict(bundle)
        for bundle in bundle_payload["bundles"]
        if str(bundle.get("dominant_key") or "") in selected_keys
    ]
    extra_bundles = [
        dict(bundle)
        for bundle in bundle_payload["bundles"]
        if str(bundle.get("dominant_key") or "") in extra_keys
    ]

    payload: Dict[str, Any] = {
        "engine_version": PERSONALITY_IMPRINT_ENGINE_VERSION,
        "library_version": PERSONALITY_IMPRINT_LIBRARY_VERSION,
        "locale": "tr" if not str(locale or "").strip().lower().startswith("tr") else str(locale),
        "headline": str(PERSONALITY_IMPRINT_RENDER_SHAPE["headline"]),
        "render_shape": dict(PERSONALITY_IMPRINT_RENDER_SHAPE),
        "entries": entries,
        "extra_entries": extra_entries,
        "support_entries": bundle_payload["support_entries"],
        "bundles": bundles,
        "extra_bundles": extra_bundles,
    }
    if include_debug:
        payload["selection_debug"] = {
            **selection["debug"],
            **bundle_payload["debug"],
        }
    return payload
