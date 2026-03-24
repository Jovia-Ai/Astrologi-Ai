from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Tuple

from app.sky_events.models import GlobalSkyEvent


BODY_WEIGHT = {
    "Sun": 58.0,
    "Mercury": 70.0,
    "Venus": 68.0,
    "Mars": 72.0,
    "Jupiter": 80.0,
    "Saturn": 86.0,
    "Uranus": 90.0,
    "Neptune": 88.0,
    "Pluto": 92.0,
    "Moon": 60.0,
}

EVENT_BASE = {
    "retrograde_start": 82.0,
    "retrograde_end": 79.0,
    "ingress": 62.0,
    "lunation_new_moon": 78.0,
    "lunation_full_moon": 79.0,
    "eclipse": 94.0,
    "exact_aspect_major": 74.0,
}

READABILITY = {
    "retrograde_start": 96.0,
    "retrograde_end": 95.0,
    "ingress": 89.0,
    "lunation_new_moon": 93.0,
    "lunation_full_moon": 93.0,
    "eclipse": 92.0,
    "exact_aspect_major": 78.0,
}


def _to_utc(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _body_score(bodies: Iterable[str]) -> float:
    vals = [BODY_WEIGHT.get(body, 60.0) for body in bodies]
    if not vals:
        return 60.0
    return max(vals)


def importance_score(event_type: str, bodies: List[str]) -> float:
    base = EVENT_BASE.get(event_type, 65.0)
    body_bonus = (_body_score(bodies) - 60.0) * 0.45
    return round(min(99.0, base + body_bonus), 1)


def cultural_interest_score(event_type: str, bodies: List[str]) -> float:
    primary = bodies[0] if bodies else ""
    score = {
        "retrograde_start": 88.0,
        "retrograde_end": 82.0,
        "ingress": 70.0,
        "lunation_new_moon": 78.0,
        "lunation_full_moon": 80.0,
        "eclipse": 95.0,
        "exact_aspect_major": 74.0,
    }.get(event_type, 68.0)
    if primary == "Mercury" and event_type.startswith("retrograde"):
        score += 8.0
    if primary in {"Saturn", "Uranus", "Neptune", "Pluto"} and event_type in {"ingress", "exact_aspect_major"}:
        score += 4.0
    if primary == "Jupiter" and event_type == "retrograde_end":
        score += 3.0
    return round(min(99.0, score), 1)


def readability_score(event_type: str) -> float:
    return READABILITY.get(event_type, 76.0)


def temporal_relevance(
    now: datetime,
    visibility_start: str | datetime,
    exact_at: str | datetime,
    visibility_end: str | datetime,
) -> float:
    current = _to_utc(now)
    start_dt = _to_utc(visibility_start)
    exact_dt = _to_utc(exact_at)
    end_dt = _to_utc(visibility_end)
    if current < start_dt:
        lead = (exact_dt - current).total_seconds()
        if lead <= 0:
            return 0.0
        days = lead / 86400.0
        return max(10.0, 70.0 - min(days, 10.0) * 6.0)
    if current > end_dt:
        lag = (current - end_dt).total_seconds() / 86400.0
        return max(0.0, 35.0 - min(lag, 7.0) * 5.0)

    window_half = max((end_dt - start_dt).total_seconds() / 2.0, 3600.0)
    distance = abs((current - exact_dt).total_seconds())
    centered = max(0.0, 1.0 - min(distance / window_half, 1.0))
    return round(45.0 + centered * 55.0, 1)


def score_event(event: GlobalSkyEvent, now: datetime) -> Tuple[float, Dict[str, float]]:
    temporal = temporal_relevance(now, event.visibility_window_start, event.exact_at, event.visibility_window_end)
    body_score = _body_score(event.bodies)
    score = (
        temporal * 0.30
        + event.importance_score * 0.25
        + event.cultural_interest_score * 0.20
        + body_score * 0.10
        + event.readability_score * 0.10
        + event.editorial_boost * 0.05
    )
    breakdown = {
        "temporal_relevance": round(temporal, 1),
        "importance": round(event.importance_score, 1),
        "cultural_interest": round(event.cultural_interest_score, 1),
        "body_weight": round(body_score, 1),
        "readability": round(event.readability_score, 1),
        "editorial_boost": round(event.editorial_boost, 1),
    }
    return round(score, 2), breakdown


def rank_events(events: Iterable[GlobalSkyEvent], now: datetime, limit: int) -> List[GlobalSkyEvent]:
    scored: List[GlobalSkyEvent] = []
    for event in events:
        feed_score, breakdown = score_event(event, now)
        updated = event.model_copy(
            update={
                "feed_score": feed_score,
                "debug": {**event.debug, "score_breakdown": breakdown},
            }
        )
        scored.append(updated)

    scored.sort(key=lambda item: (item.feed_score, item.importance_score, item.cultural_interest_score), reverse=True)

    selected: List[GlobalSkyEvent] = []
    family_counter: Counter[str] = Counter()
    aspect_count = 0
    for event in scored:
        if family_counter[event.event_family] >= 2:
            continue
        if event.event_type == "exact_aspect_major" and aspect_count >= 2:
            continue
        selected.append(event)
        family_counter[event.event_family] += 1
        if event.event_type == "exact_aspect_major":
            aspect_count += 1
        if len(selected) >= limit:
            break
    return selected
