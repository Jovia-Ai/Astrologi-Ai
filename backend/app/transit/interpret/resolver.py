"""Resolve interpretation content blocks."""
from __future__ import annotations

from typing import Any, Dict, Iterable, Tuple

from app.transit.interpret.canonical import canonical_key


def resolve_content(keys: Iterable[str], content: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    events = content.get("events") or {}
    fallbacks = content.get("fallbacks") or {}

    for key in keys:
        if key in events:
            return events[key], key
        if key in fallbacks:
            return fallbacks[key], key

    if "generic.ANY" in fallbacks:
        return fallbacks["generic.ANY"], "generic.ANY"

    return {"themes": [], "variants": []}, "generic.ANY"


def resolve_block(
    store: Dict[str, Any],
    transit_body: str,
    aspect: str,
    natal_point: str,
    polarity: str,
    theme: str,
    debug: Dict[str, Any] | None = None,
) -> Tuple[Dict[str, Any], str]:
    templates = store.get("templates") or {}
    specific = canonical_key(transit_body, aspect, natal_point)
    keys = [
        specific,
        canonical_key(transit_body, aspect, "ANY"),
        f"{aspect.lower()}.{polarity}.ANY",
        f"{polarity}.{theme}.ANY",
        "generic.ANY",
    ]

    used_key = None
    block: Dict[str, Any] = {}
    for key in keys:
        candidate = key.lower()
        if candidate in templates:
            used_key = candidate
            block = templates[candidate]
            break

    specific_key = specific.lower()
    if specific_key in templates and used_key != specific_key:
        used_key = specific_key
        block = templates[specific_key]

    if debug is not None:
        debug["resolver_trace"] = keys
        debug["resolver_selected_key"] = used_key
        debug["resolver_specific_exists"] = specific_key in templates

    return block, used_key or specific_key
