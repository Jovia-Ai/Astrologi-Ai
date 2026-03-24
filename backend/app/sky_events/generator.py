from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import itertools
import math
import re
from typing import Callable, Dict, Iterable, List, Sequence

from app.sky_events.copy_tr import BODY_TR, SIGN_TR, build_event_copy
from app.sky_events.ephemeris import aspect_error, body_state, ensure_utc
from app.sky_events.models import GlobalSkyEvent
from app.sky_events.ranking import cultural_interest_score, importance_score, readability_score


RETROGRADE_BODIES: Sequence[str] = ("Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto")
INGRESS_BODIES: Sequence[str] = ("Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto")
ASPECT_BODIES: Sequence[str] = ("Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto")
SLOW_BODIES = {"Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"}
MAJOR_ASPECTS = {
    "conjunction": 0,
    "sextile": 60,
    "square": 90,
    "trine": 120,
    "opposition": 180,
}

LUNATION_ORB = 1.8
ASPECT_ORB = 1.0
ECLIPSE_NODE_ORB = 18.0


def _iso(dt: datetime) -> str:
    return ensure_utc(dt).replace(microsecond=0).isoformat()


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower())
    return cleaned.strip("-")


def _event_identity(*parts: str) -> tuple[str, str]:
    canonical = ":".join(parts)
    digest = hashlib.sha1(canonical.encode("utf-8")).hexdigest()[:12]
    return f"sky_{digest}", canonical


def _body_list(primary_body: str | None, secondary_body: str | None) -> List[str]:
    return [body for body in (primary_body, secondary_body) if body]


def _window_for_event(event_type: str, bodies: List[str]) -> tuple[timedelta, timedelta]:
    outer = any(body in SLOW_BODIES for body in bodies)
    if event_type in {"retrograde_start", "retrograde_end"}:
        return (timedelta(days=3 if outer else 2), timedelta(days=10 if outer else 5))
    if event_type == "ingress":
        return (timedelta(hours=12), timedelta(days=3 if outer else 2))
    if event_type in {"lunation_new_moon", "lunation_full_moon"}:
        return (timedelta(hours=24), timedelta(days=3))
    if event_type == "eclipse":
        return (timedelta(days=7), timedelta(days=10))
    return (timedelta(days=2 if outer else 1), timedelta(days=4 if outer else 2))


def _status_phase(now: datetime, exact_at: datetime, visibility_start: datetime, visibility_end: datetime) -> tuple[str, str]:
    current = ensure_utc(now)
    exact = ensure_utc(exact_at)
    if current < visibility_start:
        return "upcoming", "building"
    if current > visibility_end:
        return "archived", "past"
    delta_hours = (current - exact).total_seconds() / 3600.0
    if abs(delta_hours) <= 3.0:
        return "active", "exact"
    if delta_hours < 0:
        return "active", "approaching"
    if delta_hours <= 48.0:
        return "active", "unfolding"
    return "recent", "settling"


def _human_tags(event_type: str, primary_body: str | None, secondary_body: str | None, sign: str | None) -> List[str]:
    tags = ["Kolektif"]
    if event_type.startswith("retrograde"):
        tags.append("Retro")
    elif event_type == "ingress":
        tags.append("Burç geçişi")
    elif event_type.startswith("lunation"):
        tags.append("Lunasyon")
    elif event_type == "eclipse":
        tags.append("Tutulma")
    elif event_type == "exact_aspect_major":
        tags.append("Açı")
    for body in (primary_body, secondary_body):
        if body:
            tags.append(BODY_TR.get(body, body))
    if sign:
        tags.append(SIGN_TR.get(sign, sign))
    deduped: List[str] = []
    for tag in tags:
        if tag not in deduped:
            deduped.append(tag)
    return deduped[:4]


def _refine_transition(start: datetime, end: datetime, predicate: Callable[[datetime], bool]) -> datetime:
    low = ensure_utc(start)
    high = ensure_utc(end)
    start_value = predicate(low)
    for _ in range(18):
        mid = low + (high - low) / 2
        if predicate(mid) == start_value:
            low = mid
        else:
            high = mid
    return high.replace(second=0, microsecond=0)


def _refine_minimum(start: datetime, end: datetime, scorer: Callable[[datetime], float]) -> tuple[datetime, float]:
    low = ensure_utc(start)
    high = ensure_utc(end)
    best_time = low
    best_score = math.inf
    for _ in range(4):
        span = high - low
        for index in range(25):
            point = low + span * (index / 24)
            score = scorer(point)
            if score < best_score:
                best_score = score
                best_time = point
        delta = max(span / 8, timedelta(minutes=20))
        low = max(ensure_utc(start), best_time - delta)
        high = min(ensure_utc(end), best_time + delta)
    return best_time.replace(second=0, microsecond=0), round(best_score, 4)


def _time_grid(start: datetime, end: datetime, step_hours: int) -> List[datetime]:
    current = ensure_utc(start)
    stop = ensure_utc(end)
    times: List[datetime] = []
    while current <= stop:
        times.append(current)
        current += timedelta(hours=step_hours)
    if not times or times[-1] < stop:
        times.append(stop)
    return times


def _make_event(
    *,
    now: datetime,
    event_type: str,
    event_family: str,
    exact_at: datetime,
    primary_body: str | None,
    secondary_body: str | None = None,
    sign: str | None = None,
    degree_abs: float | None = None,
    degree_in_sign: float | None = None,
    aspect: str | None = None,
    aspect_angle: int | None = None,
    eclipse_kind: str | None = None,
    debug: Dict[str, object] | None = None,
    metadata: Dict[str, object] | None = None,
) -> GlobalSkyEvent:
    bodies = _body_list(primary_body, secondary_body)
    window_before, window_after = _window_for_event(event_type, bodies)
    starts_at = exact_at - window_before
    ends_at = exact_at + window_after
    visibility_start = starts_at
    visibility_end = ends_at
    status, phase = _status_phase(now, exact_at, visibility_start, visibility_end)
    copy_pack = build_event_copy(
        event_type=event_type,
        primary_body=primary_body,
        secondary_body=secondary_body,
        sign=sign,
        aspect=aspect,
        eclipse_kind=eclipse_kind,
    )
    slug_bits = [event_type]
    if primary_body:
        slug_bits.append(primary_body)
    if secondary_body:
        slug_bits.append(secondary_body)
    if aspect:
        slug_bits.append(aspect)
    if sign:
        slug_bits.append(sign)
    slug_bits.append(exact_at.date().isoformat())
    slug = _slugify("-".join(slug_bits))
    event_id, canonical_key = _event_identity(*slug_bits)
    importance = importance_score(event_type, bodies)
    culture = cultural_interest_score(event_type, bodies)
    readability = readability_score(event_type)
    return GlobalSkyEvent(
        id=event_id,
        slug=slug,
        event_type=event_type,
        event_family=event_family,
        title_tr=str(copy_pack["title_tr"]),
        short_title_tr=str(copy_pack["short_title_tr"]),
        status=status,
        phase=phase,
        primary_body=primary_body,
        secondary_body=secondary_body,
        bodies=bodies,
        aspect=aspect,
        aspect_angle=aspect_angle,
        sign=sign,
        degree=round(degree_in_sign, 2) if degree_in_sign is not None else None,
        degree_abs=round(degree_abs, 2) if degree_abs is not None else None,
        starts_at=_iso(starts_at),
        exact_at=_iso(exact_at),
        ends_at=_iso(ends_at),
        visibility_window_start=_iso(visibility_start),
        visibility_window_end=_iso(visibility_end),
        importance_score=importance,
        cultural_interest_score=culture,
        readability_score=readability,
        editorial_boost=0.0,
        feed_score=0.0,
        dedupe_priority=importance,
        tags=_human_tags(event_type, primary_body, secondary_body, sign),
        summary_tr=str(copy_pack["summary_tr"]),
        general_meaning_tr=str(copy_pack["general_meaning_tr"]),
        what_it_can_feel_like_tr=str(copy_pack["what_it_can_feel_like_tr"]),
        what_to_watch_tr=str(copy_pack["what_to_watch_tr"]),
        how_to_work_with_it_tr=str(copy_pack["how_to_work_with_it_tr"]),
        who_feels_it_stronger_tr=str(copy_pack["who_feels_it_stronger_tr"] or "") or None,
        metadata={"canonical_key": canonical_key, **(metadata or {})},
        debug={"rule_version": "sky_v1", **(debug or {})},
    )


def _generate_retrogrades(start: datetime, end: datetime, now: datetime) -> List[GlobalSkyEvent]:
    times = _time_grid(start, end, 6)
    events: List[GlobalSkyEvent] = []
    for body in RETROGRADE_BODIES:
        previous_time = times[0]
        previous_state = body_state(body, previous_time)
        for current_time in times[1:]:
            current_state = body_state(body, current_time)
            if previous_state.retrograde != current_state.retrograde:
                exact_at = _refine_transition(
                    previous_time,
                    current_time,
                    lambda candidate: body_state(body, candidate).retrograde,
                )
                exact_state = body_state(body, exact_at)
                event_type = "retrograde_start" if exact_state.retrograde else "retrograde_end"
                events.append(
                    _make_event(
                        now=now,
                        event_type=event_type,
                        event_family="retrograde",
                        exact_at=exact_at,
                        primary_body=body,
                        sign=exact_state.sign,
                        degree_abs=exact_state.longitude,
                        degree_in_sign=exact_state.degree_in_sign,
                        debug={
                            "source_positions": {
                                body: {
                                    "longitude": round(exact_state.longitude, 3),
                                    "speed": round(exact_state.speed, 5),
                                }
                            },
                            "detection_evidence": {"transition": "retrograde_state_change"},
                        },
                    )
                )
            previous_time = current_time
            previous_state = current_state
    return events


def _generate_ingresses(start: datetime, end: datetime, now: datetime) -> List[GlobalSkyEvent]:
    times = _time_grid(start, end, 6)
    events: List[GlobalSkyEvent] = []
    for body in INGRESS_BODIES:
        previous_time = times[0]
        previous_state = body_state(body, previous_time)
        for current_time in times[1:]:
            current_state = body_state(body, current_time)
            if previous_state.sign_index != current_state.sign_index:
                exact_at = _refine_transition(
                    previous_time,
                    current_time,
                    lambda candidate: body_state(body, candidate).sign_index == previous_state.sign_index,
                )
                exact_state = body_state(body, exact_at)
                events.append(
                    _make_event(
                        now=now,
                        event_type="ingress",
                        event_family="ingress",
                        exact_at=exact_at,
                        primary_body=body,
                        sign=exact_state.sign,
                        degree_abs=exact_state.longitude,
                        degree_in_sign=exact_state.degree_in_sign,
                        debug={
                            "source_positions": {
                                body: {
                                    "longitude": round(exact_state.longitude, 3),
                                    "speed": round(exact_state.speed, 5),
                                }
                            },
                            "detection_evidence": {"transition": "sign_change"},
                        },
                    )
                )
            previous_time = current_time
            previous_state = current_state
    return events


def _generate_lunations(start: datetime, end: datetime, now: datetime) -> List[GlobalSkyEvent]:
    times = _time_grid(start, end, 3)
    errors_new = [aspect_error(body_state("Sun", point).longitude, body_state("Moon", point).longitude, 0) for point in times]
    errors_full = [aspect_error(body_state("Sun", point).longitude, body_state("Moon", point).longitude, 180) for point in times]
    events: List[GlobalSkyEvent] = []

    def build_local_minima(target_errors: List[float], event_type: str, target_angle: int) -> None:
        for index in range(1, len(times) - 1):
            center = target_errors[index]
            if center > LUNATION_ORB:
                continue
            if center > target_errors[index - 1] or center > target_errors[index + 1]:
                continue
            exact_at, refined_error = _refine_minimum(
                times[index - 1],
                times[index + 1],
                lambda candidate: aspect_error(
                    body_state("Sun", candidate).longitude,
                    body_state("Moon", candidate).longitude,
                    target_angle,
                ),
            )
            if refined_error > LUNATION_ORB:
                continue
            sun = body_state("Sun", exact_at)
            moon = body_state("Moon", exact_at)
            node = body_state("North Node", exact_at)
            node_distance = aspect_error(sun.longitude, node.longitude, 0)
            is_eclipse = node_distance <= ECLIPSE_NODE_ORB
            sign = sun.sign if event_type == "lunation_new_moon" else moon.sign
            actual_type = "eclipse" if is_eclipse else event_type
            eclipse_kind = None
            if is_eclipse:
                eclipse_kind = "Güneş Tutulması" if target_angle == 0 else "Ay Tutulması"
            events.append(
                _make_event(
                    now=now,
                    event_type=actual_type,
                    event_family="eclipse" if is_eclipse else "lunation",
                    exact_at=exact_at,
                    primary_body="Sun",
                    secondary_body="Moon",
                    sign=sign,
                    degree_abs=sun.longitude,
                    degree_in_sign=sun.degree_in_sign,
                    aspect="conjunction" if target_angle == 0 else "opposition",
                    aspect_angle=target_angle,
                    eclipse_kind=eclipse_kind,
                    debug={
                        "source_positions": {
                            "Sun": {"longitude": round(sun.longitude, 3)},
                            "Moon": {"longitude": round(moon.longitude, 3)},
                            "North Node": {"longitude": round(node.longitude, 3)},
                        },
                        "detection_evidence": {
                            "lunation_error": refined_error,
                            "node_distance": round(node_distance, 3),
                            "is_eclipse": is_eclipse,
                        },
                    },
                    metadata={"eclipse_kind": eclipse_kind} if eclipse_kind else {},
                )
            )

    build_local_minima(errors_new, "lunation_new_moon", 0)
    build_local_minima(errors_full, "lunation_full_moon", 180)
    return events


def _generate_aspects(start: datetime, end: datetime, now: datetime) -> List[GlobalSkyEvent]:
    times = _time_grid(start, end, 3)
    events: List[GlobalSkyEvent] = []
    for body_a, body_b in itertools.combinations(ASPECT_BODIES, 2):
        if body_a not in SLOW_BODIES and body_b not in SLOW_BODIES:
            continue
        for aspect_name, target_angle in MAJOR_ASPECTS.items():
            errors = [
                aspect_error(body_state(body_a, point).longitude, body_state(body_b, point).longitude, target_angle)
                for point in times
            ]
            for index in range(1, len(times) - 1):
                center = errors[index]
                if center > ASPECT_ORB:
                    continue
                if center > errors[index - 1] or center > errors[index + 1]:
                    continue
                exact_at, refined_error = _refine_minimum(
                    times[index - 1],
                    times[index + 1],
                    lambda candidate: aspect_error(
                        body_state(body_a, candidate).longitude,
                        body_state(body_b, candidate).longitude,
                        target_angle,
                    ),
                )
                if refined_error > ASPECT_ORB:
                    continue
                state_a = body_state(body_a, exact_at)
                state_b = body_state(body_b, exact_at)
                events.append(
                    _make_event(
                        now=now,
                        event_type="exact_aspect_major",
                        event_family="aspect",
                        exact_at=exact_at,
                        primary_body=body_a,
                        secondary_body=body_b,
                        sign=state_a.sign,
                        degree_abs=state_a.longitude,
                        degree_in_sign=state_a.degree_in_sign,
                        aspect=aspect_name,
                        aspect_angle=target_angle,
                        debug={
                            "source_positions": {
                                body_a: {"longitude": round(state_a.longitude, 3)},
                                body_b: {"longitude": round(state_b.longitude, 3)},
                            },
                            "detection_evidence": {"aspect_error": refined_error},
                        },
                    )
                )
    return events


def _dedupe_events(events: Iterable[GlobalSkyEvent]) -> List[GlobalSkyEvent]:
    by_key: Dict[str, GlobalSkyEvent] = {}
    eclipses: List[GlobalSkyEvent] = []
    for event in events:
        key = str(event.metadata.get("canonical_key") or event.slug)
        current = by_key.get(key)
        if current is None or event.importance_score > current.importance_score:
            by_key[key] = event
    deduped = list(by_key.values())
    for event in deduped:
        if event.event_type == "eclipse":
            eclipses.append(event)

    filtered: List[GlobalSkyEvent] = []
    for event in sorted(deduped, key=lambda item: item.exact_at):
        if event.event_type.startswith("lunation"):
            same_window_eclipse = next(
                (
                    eclipse
                    for eclipse in eclipses
                    if eclipse.sign == event.sign
                    and abs((datetime.fromisoformat(eclipse.exact_at) - datetime.fromisoformat(event.exact_at)).total_seconds()) <= 86400
                ),
                None,
            )
            if same_window_eclipse is not None:
                continue
        if filtered and event.event_type == "exact_aspect_major":
            previous = filtered[-1]
            if (
                previous.event_type == "exact_aspect_major"
                and previous.primary_body == event.primary_body
                and previous.secondary_body == event.secondary_body
                and previous.aspect == event.aspect
                and abs((datetime.fromisoformat(previous.exact_at) - datetime.fromisoformat(event.exact_at)).total_seconds()) <= 43200
            ):
                continue
        filtered.append(event)
    return filtered


def generate_global_sky_events(start: datetime, end: datetime, *, now: datetime | None = None) -> List[GlobalSkyEvent]:
    current = ensure_utc(now or datetime.now(timezone.utc))
    scan_start = ensure_utc(start)
    scan_end = ensure_utc(end)
    events: List[GlobalSkyEvent] = []
    events.extend(_generate_retrogrades(scan_start, scan_end, current))
    events.extend(_generate_ingresses(scan_start, scan_end, current))
    events.extend(_generate_lunations(scan_start, scan_end, current))
    events.extend(_generate_aspects(scan_start, scan_end, current))
    return _dedupe_events(events)
