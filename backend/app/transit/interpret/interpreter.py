"""Interpret transit display items into textual guidance."""
from __future__ import annotations

from typing import Any, Dict

from .resolver import resolve_content
from .templating import pick_variant, time_status_from_orb_phase


def interpret_item(
    item: Dict[str, Any],
    content: Dict[str, Any],
    *,
    lang: str = "tr",
    version: str = "tr.v1",
) -> Dict[str, Any]:
    transit_body = str(item.get("transit_body") or "")
    aspect = str(item.get("aspect") or "")
    natal_point = str(item.get("natal_point") or "")
    polarity = str(item.get("polarity") or "")

    keys = [
        f"{transit_body}.{aspect}.{natal_point}",
        f"{transit_body}.{aspect}.ANY",
        f"{aspect}.{polarity}.ANY",
        "generic.ANY",
    ]

    block, used_key = resolve_content(keys, content)
    variants = block.get("variants") or []
    variant_index = pick_variant(str(item.get("event_id") or ""), lang, version, len(variants))
    chosen = variants[variant_index - 1] if variants else {}

    orb = float(item.get("orb_deg") or 0.0)
    phase = str(item.get("phase") or "applying")
    time_status = time_status_from_orb_phase(orb, phase)

    timing_confidence = 0.0
    timing = item.get("timing") or {}
    if isinstance(timing, dict):
        timing_confidence = float(timing.get("confidence") or 0.0)

    confidence = min(1.0, 0.6 + 0.4 * timing_confidence)

    evidence = {
        "transit": transit_body,
        "aspect": aspect,
        "natal": natal_point,
        "orb": orb,
        "strength": item.get("strength"),
    }

    return {
        "headline": chosen.get("headline", ""),
        "summary": chosen.get("summary", ""),
        "do": list(chosen.get("do", [])),
        "watch": list(chosen.get("watch", [])),
        "time_status": time_status,
        "themes": list(block.get("themes", [])),
        "confidence": round(confidence, 2),
        "evidence": [evidence],
        "content_ref": {
            "lang": lang,
            "version": version,
            "key": used_key,
            "variant": variant_index,
        },
    }
