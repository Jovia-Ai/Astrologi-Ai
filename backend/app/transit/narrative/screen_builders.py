from __future__ import annotations

from typing import Any, Dict, List

from app.transit.narrative.models import UIBlock
from app.transit.narrative.rules import (
    CALENDAR_DAY_ORDER,
    FEED_ORDER,
    PERSONAL_ORDER,
    SPACE_HUB_PRIORITY,
    enforce_word_limit,
    ordered,
)


def _to_payload(blocks: List[UIBlock]) -> List[Dict[str, Any]]:
    return [b.to_dict() for b in blocks]


def build_space_hub(blocks: List[UIBlock]) -> Dict[str, Any]:
    prioritized = ordered(blocks, SPACE_HUB_PRIORITY)
    selected = prioritized[:3]
    if not selected:
        fallback = next(
            (b for b in blocks if b.type in {"core_theme", "daily_energy", "clarity"}),
            None,
        )
        selected = [fallback] if fallback else []
    trimmed = enforce_word_limit(selected, max_words=100)
    return {
        "title": "Space Hub",
        "blocks": _to_payload(trimmed),
        "count": len(trimmed),
    }


def build_personal_transit(blocks: List[UIBlock]) -> Dict[str, Any]:
    prioritized = ordered(blocks, PERSONAL_ORDER)
    chosen: List[UIBlock] = []
    picked_types = set()
    for block in prioritized:
        if block.type in PERSONAL_ORDER and block.type not in picked_types:
            chosen.append(block)
            picked_types.add(block.type)
    # keep bounded length and deterministic order
    chosen = ordered(chosen, PERSONAL_ORDER)[:6]
    has_core = any(block.type == "core_theme" for block in chosen)
    if not has_core:
        fallback = next(
            (b for b in blocks if b.type in {"daily_energy", "clarity"}),
            None,
        )
        if fallback is not None:
            chosen = [fallback, *chosen][:6]
    return {
        "title": "Personal Transit",
        "blocks": _to_payload(chosen),
        "count": len(chosen),
    }


def build_calendar_day(blocks: List[UIBlock], date: str | None) -> Dict[str, Any]:
    prioritized = ordered(blocks, CALENDAR_DAY_ORDER)
    chosen: List[UIBlock] = []
    for block in prioritized:
        meta_date = str(block.meta.get("date") or "") if isinstance(block.meta, dict) else ""
        if block.type in {"daily_energy", "event_list_preview", "alert"}:
            if date and meta_date and meta_date != date:
                continue
        chosen.append(block)
        if len(chosen) >= 4:
            break

    selected_events_count = 0
    selected_signals_count = 0
    has_signals = False
    for block in chosen:
        if block.type == "daily_energy":
            selected_events_count = int(block.meta.get("events_count") or 0)
            selected_signals_count = int(block.meta.get("signals_count") or 0)
            has_signals = bool(block.meta.get("has_signals"))
            break

    return {
        "title": "Calendar Day",
        "date": date,
        "events_count": selected_events_count,
        "signals_count": selected_signals_count,
        "has_signals": has_signals,
        "blocks": _to_payload(chosen),
    }


def build_feed_snippet(blocks: List[UIBlock]) -> Dict[str, Any]:
    prioritized = ordered(blocks, FEED_ORDER)
    snippet = prioritized[:1]
    snippet = enforce_word_limit(snippet, max_words=40)
    text = snippet[0].copy.short if snippet else ""
    return {
        "title": "Feed Snippet",
        "text": text,
        "blocks": _to_payload(snippet),
    }
