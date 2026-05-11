from __future__ import annotations

from typing import Any, Mapping, Sequence

from app.transit.narrative.period_voice_policy import build_period_voice_policy


_EXCEPTIONAL_EVENT_FAMILIES = {
    "eclipse_trigger",
    "lunation_trigger",
    "station_trigger",
    "outer_planet_exact_hit",
}


def build_today_story_candidate(
    *,
    canonical_period_spine: Mapping[str, Any] | None,
    daily_event_cards: Sequence[Mapping[str, Any]] | None,
    period_event_cards: Sequence[Mapping[str, Any]] | None = None,
    daily_selection: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    period_spine = canonical_period_spine if isinstance(canonical_period_spine, Mapping) else {}
    daily_cards = [dict(card) for card in (daily_event_cards or []) if isinstance(card, Mapping)]
    period_cards = [dict(card) for card in (period_event_cards or []) if isinstance(card, Mapping)]
    selection = daily_selection if isinstance(daily_selection, Mapping) else {}
    daily_activation = selection.get("natal_activation_context") if isinstance(selection.get("natal_activation_context"), Mapping) else {}
    trigger_selection = selection.get("trigger_selection") if isinstance(selection.get("trigger_selection"), Mapping) else {}

    exceptional = _first_exceptional_event(daily_cards)
    if exceptional:
        return _candidate(
            story_type="exceptional_event",
            trigger_event=exceptional,
            period_spine=period_spine,
            support_event_ids=_support_event_ids(daily_cards, primary_event_id=str(exceptional.get("event_id") or "")),
            activation_hook_match=False,
            selected_trigger_reason="exceptional_event",
            suppressed_daily_events=[],
        )

    if period_spine:
        trigger_event = _trigger_event_from_selection(
            trigger_selection=trigger_selection,
            daily_cards=daily_cards,
        )
        if trigger_event is not None:
            return _candidate(
                story_type="period_triggered_today",
                trigger_event=trigger_event,
                period_spine=period_spine,
                support_event_ids=_support_event_ids_from_selection(
                    trigger_selection,
                    daily_cards=daily_cards,
                    primary_event_id=str(trigger_event.get("event_id") or ""),
                ),
                activation_hook_match=True,
                selected_trigger_reason="daily_trigger_selection_primary",
                suppressed_daily_events=_suppressed_event_ids_from_selection(trigger_selection, daily_cards=daily_cards),
            )
        if trigger_selection and not str(trigger_selection.get("primary_trigger_event_id") or "").strip():
            return _candidate(
                story_type="period_continuation",
                trigger_event=period_cards[0] if period_cards else {},
                period_spine=period_spine,
                support_event_ids=_support_event_ids_from_selection(
                    trigger_selection,
                    daily_cards=daily_cards,
                    primary_event_id="",
                ),
                activation_hook_match=False,
                selected_trigger_reason="daily_trigger_selection_period_continuation",
                suppressed_daily_events=_suppressed_event_ids_from_selection(trigger_selection, daily_cards=daily_cards),
            )
        trigger_event = _period_trigger_event(
            period_spine=period_spine,
            daily_cards=daily_cards,
            daily_activation=daily_activation,
        )
        if trigger_event is not None:
            return _candidate(
                story_type="period_triggered_today",
                trigger_event=trigger_event,
                period_spine=period_spine,
                support_event_ids=_support_event_ids(daily_cards, primary_event_id=str(trigger_event.get("event_id") or "")),
                activation_hook_match=True,
                selected_trigger_reason="daily_event_matches_period_spine_hook",
                suppressed_daily_events=_suppressed_daily_events(daily_cards, primary_event_id=str(trigger_event.get("event_id") or "")),
            )
        return _candidate(
            story_type="period_continuation",
            trigger_event=period_cards[0] if period_cards else {},
            period_spine=period_spine,
            support_event_ids=_event_ids(daily_cards),
            activation_hook_match=False,
            selected_trigger_reason="canonical_period_spine_without_daily_trigger",
            suppressed_daily_events=_event_ids(daily_cards),
        )

    if daily_cards:
        trigger_event = _trigger_event_from_selection(
            trigger_selection=trigger_selection,
            daily_cards=daily_cards,
        )
        if trigger_event is not None:
            return _candidate(
                story_type="daily_flavor",
                trigger_event=trigger_event,
                period_spine={},
                support_event_ids=_support_event_ids_from_selection(
                    trigger_selection,
                    daily_cards=daily_cards,
                    primary_event_id=str(trigger_event.get("event_id") or ""),
                ),
                activation_hook_match=False,
                selected_trigger_reason="daily_trigger_selection_without_period_spine",
                suppressed_daily_events=_suppressed_event_ids_from_selection(trigger_selection, daily_cards=daily_cards),
            )
        return _candidate(
            story_type="daily_flavor",
            trigger_event=daily_cards[0],
            period_spine={},
            support_event_ids=_support_event_ids(daily_cards, primary_event_id=str(daily_cards[0].get("event_id") or "")),
            activation_hook_match=False,
            selected_trigger_reason="no_period_spine_daily_event_available",
            suppressed_daily_events=_suppressed_daily_events(daily_cards, primary_event_id=str(daily_cards[0].get("event_id") or "")),
        )

    return _candidate(
        story_type="quiet_day",
        trigger_event={},
        period_spine={},
        support_event_ids=[],
        activation_hook_match=False,
        selected_trigger_reason="no_period_spine_no_daily_event",
        suppressed_daily_events=[],
    )


def _candidate(
    *,
    story_type: str,
    trigger_event: Mapping[str, Any],
    period_spine: Mapping[str, Any],
    support_event_ids: Sequence[str],
    activation_hook_match: bool,
    selected_trigger_reason: str,
    suppressed_daily_events: Sequence[str],
) -> dict[str, Any]:
    backing_node_ids = _backing_node_ids(period_spine)
    voice_policy = build_period_voice_policy(
        canonical_period_spine=period_spine,
        matched_events=[trigger_event] if trigger_event else [],
        chapter_role=_chapter_role(trigger_event),
        canonical_backing_node_ids=backing_node_ids,
    )
    debug = dict(voice_policy.get("debug") or {}) if isinstance(voice_policy.get("debug"), Mapping) else {}

    return {
        "story_type": story_type,
        "primary_period_spine_id": str(period_spine.get("hook_id") or period_spine.get("target_node_id") or "").strip() or None,
        "primary_spine_line": _primary_spine_line(period_spine),
        "primary_trigger_event_id": str(trigger_event.get("event_id") or "").strip() or None,
        "support_event_ids": list(support_event_ids),
        "event_nature": debug.get("event_nature"),
        "natal_backing_node_ids": backing_node_ids,
        "chapter_role": debug.get("chapter_role") or _chapter_role(trigger_event) or None,
        "voice_policy_id": str(voice_policy.get("version") or "").strip() or None,
        "mechanism_lens": str(voice_policy.get("mechanism_lens") or "").strip() or None,
        "growth_edge": str(voice_policy.get("growth_edge") or "").strip() or None,
        "reason_line_allowed": bool(voice_policy.get("reason_line_allowed")),
        "reason_line_seed": str(voice_policy.get("reason_line_seed") or "").strip() or None,
        "debug": {
            "selected_trigger_reason": selected_trigger_reason,
            "suppressed_daily_events": list(suppressed_daily_events),
            "period_spine_source": str(period_spine.get("source") or "").strip(),
            "activation_hook_match": bool(activation_hook_match),
            "period_spine_hook_id": str(period_spine.get("hook_id") or "").strip(),
            "period_spine_target_node_id": str(period_spine.get("target_node_id") or "").strip(),
            "voice_policy_debug": debug,
        },
    }


def _period_trigger_event(
    *,
    period_spine: Mapping[str, Any],
    daily_cards: Sequence[Mapping[str, Any]],
    daily_activation: Mapping[str, Any],
) -> dict[str, Any] | None:
    daily_matched_ids = {
        str(event_id).strip()
        for event_id in (daily_activation.get("matched_event_ids") or [])
        if str(event_id).strip()
    }
    daily_hook_ids = {
        str(hook_id).strip()
        for hook_id in (daily_activation.get("top_hook_ids") or [])
        if str(hook_id).strip()
    }
    period_hook_id = str(period_spine.get("hook_id") or "").strip()

    if period_hook_id and daily_hook_ids and period_hook_id not in daily_hook_ids:
        return None

    for card in daily_cards:
        event_id = str(card.get("event_id") or "").strip()
        if event_id and event_id in daily_matched_ids:
            return dict(card)
    return None


def _first_exceptional_event(daily_cards: Sequence[Mapping[str, Any]]) -> dict[str, Any] | None:
    for card in daily_cards:
        family = str(card.get("event_family") or card.get("event_subtype") or card.get("event_kind") or "").strip().lower()
        if family in _EXCEPTIONAL_EVENT_FAMILIES or bool(card.get("is_exceptional")):
            return dict(card)
    return None


def _trigger_event_from_selection(
    *,
    trigger_selection: Mapping[str, Any],
    daily_cards: Sequence[Mapping[str, Any]],
) -> dict[str, Any] | None:
    primary_event_id = str(trigger_selection.get("primary_trigger_event_id") or "").strip()
    if not primary_event_id:
        return None
    for card in daily_cards:
        if str(card.get("event_id") or "").strip() == primary_event_id:
            return dict(card)
    for candidate in trigger_selection.get("candidates") or []:
        if not isinstance(candidate, Mapping) or str(candidate.get("event_id") or "").strip() != primary_event_id:
            continue
        debug = candidate.get("debug") if isinstance(candidate.get("debug"), Mapping) else {}
        snapshot = debug.get("event_snapshot") if isinstance(debug.get("event_snapshot"), Mapping) else {}
        if snapshot:
            return dict(snapshot)
        return {"event_id": primary_event_id}
    return None


def _support_event_ids_from_selection(
    trigger_selection: Mapping[str, Any],
    *,
    daily_cards: Sequence[Mapping[str, Any]],
    primary_event_id: str,
) -> list[str]:
    support_ids = [
        str(event_id).strip()
        for event_id in (trigger_selection.get("support_event_ids") or [])
        if str(event_id).strip() and str(event_id).strip() != primary_event_id
    ]
    if support_ids:
        return support_ids[:3]
    return _support_event_ids(daily_cards, primary_event_id=primary_event_id)


def _suppressed_event_ids_from_selection(
    trigger_selection: Mapping[str, Any],
    *,
    daily_cards: Sequence[Mapping[str, Any]],
) -> list[str]:
    suppressed_ids = [
        str(event_id).strip()
        for event_id in (trigger_selection.get("suppressed_event_ids") or [])
        if str(event_id).strip()
    ]
    if suppressed_ids:
        return suppressed_ids
    primary_event_id = str(trigger_selection.get("primary_trigger_event_id") or "").strip()
    return _suppressed_daily_events(daily_cards, primary_event_id=primary_event_id)


def _primary_spine_line(period_spine: Mapping[str, Any]) -> str | None:
    spine_lines = [
        str(item).strip()
        for item in (period_spine.get("spine_lines") or [])
        if str(item).strip()
    ]
    return spine_lines[0] if spine_lines else None


def _backing_node_ids(period_spine: Mapping[str, Any]) -> list[str]:
    out: list[str] = []
    for key in ("target_node_id", "target_node_ids", "backing_node_ids"):
        raw = period_spine.get(key)
        values = raw if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)) else [raw]
        for value in values:
            token = str(value or "").strip()
            if token and token not in out:
                out.append(token)
    return out


def _chapter_role(event: Mapping[str, Any]) -> str:
    chapter_role = event.get("chapter_role") if isinstance(event.get("chapter_role"), Mapping) else {}
    return str(chapter_role.get("role") or "").strip().lower()


def _event_ids(cards: Sequence[Mapping[str, Any]]) -> list[str]:
    out: list[str] = []
    for card in cards:
        event_id = str(card.get("event_id") or "").strip()
        if event_id and event_id not in out:
            out.append(event_id)
    return out


def _support_event_ids(cards: Sequence[Mapping[str, Any]], *, primary_event_id: str) -> list[str]:
    return [event_id for event_id in _event_ids(cards) if event_id != primary_event_id][:3]


def _suppressed_daily_events(cards: Sequence[Mapping[str, Any]], *, primary_event_id: str) -> list[str]:
    return [event_id for event_id in _event_ids(cards) if event_id != primary_event_id]
