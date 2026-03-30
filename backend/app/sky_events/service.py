from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
import json
import logging
import os
from threading import Lock
from time import perf_counter
from typing import Any, Dict, Iterable, List, Optional
from zoneinfo import ZoneInfo

from app.astro.chart_engine.builder import build_natal_chart
from app.astro.chart_engine.positions import determine_house
from app.sky_events.copy_tr import BODY_TR
from app.sky_events.ephemeris import angle_distance, body_state, ensure_utc
from app.sky_events.generator import generate_global_sky_events
from app.sky_events.models import (
    GlobalSkyEvent,
    SkyArchiveResponse,
    SkyEventDetailResponse,
    SkyEventPersonalizationRequest,
    SkyEventPersonalizationResponse,
    SkyFeedItem,
    SkyFeedResponse,
    SkyPersonalTouchpoint,
)
from app.sky_events.ranking import rank_events

logger = logging.getLogger(__name__)

_CACHE_LOCK = Lock()
_CACHE: Dict[tuple[str, str, str], tuple[float, List[GlobalSkyEvent]]] = {}
_CACHE_TTL_SECONDS = 900.0

HOUSE_LABEL_TR = {
    1: "benlik ve görünür duruş",
    2: "para, özdeğer ve maddi güven",
    3: "iletişim, yakın çevre ve gündelik akış",
    4: "ev, kökler ve iç güven",
    5: "aşk, yaratıcılık ve keyif",
    6: "rutinler, sağlık ve iş düzeni",
    7: "ilişkiler ve ortaklıklar",
    8: "paylaşım, krizler ve dönüşüm",
    9: "ufuk, eğitim ve inançlar",
    10: "kariyer, hedefler ve görünürlük",
    11: "arkadaşlıklar, topluluklar ve gelecek planları",
    12: "içe çekilme, kapanışlar ve bilinçaltı",
}

ASPECT_TARGETS = {
    "conjunction": 0,
    "sextile": 60,
    "square": 90,
    "trine": 120,
    "opposition": 180,
}

ASPECT_LABEL_TR = {
    "conjunction": "kavuşum",
    "sextile": "sekstil",
    "square": "kare",
    "trine": "üçgen",
    "opposition": "karşıt",
}


def _utc_iso(value: datetime) -> str:
    return ensure_utc(value).replace(microsecond=0).isoformat()


def _zone(tz: str) -> ZoneInfo:
    try:
        return ZoneInfo(tz)
    except Exception:
        return ZoneInfo("UTC")


def _parse_iso(value: str) -> datetime:
    return ensure_utc(datetime.fromisoformat(value))


def _cache_key(start: datetime, end: datetime, anchor: datetime) -> tuple[str, str, str]:
    bucket = int(anchor.timestamp() // _CACHE_TTL_SECONDS)
    return (start.date().isoformat(), end.date().isoformat(), str(bucket))


def _load_events(start: datetime, end: datetime, anchor: datetime) -> List[GlobalSkyEvent]:
    key = _cache_key(start, end, anchor)
    now_ts = ensure_utc(datetime.now(timezone.utc)).timestamp()
    with _CACHE_LOCK:
        cached = _CACHE.get(key)
        if cached and now_ts - cached[0] <= _CACHE_TTL_SECONDS:
            return cached[1]
    events = generate_global_sky_events(start, end, now=anchor)
    with _CACHE_LOCK:
        _CACHE[key] = (now_ts, events)
    return events


def _cache_status(start: datetime, end: datetime, anchor: datetime) -> str:
    key = _cache_key(start, end, anchor)
    now_ts = ensure_utc(datetime.now(timezone.utc)).timestamp()
    with _CACHE_LOCK:
        cached = _CACHE.get(key)
        if cached and now_ts - cached[0] <= _CACHE_TTL_SECONDS:
            return "hit"
    return "miss"


def _relative_timing(now: datetime, exact_at: datetime, tz: str) -> str:
    local_now = ensure_utc(now).astimezone(_zone(tz))
    local_exact = ensure_utc(exact_at).astimezone(_zone(tz))
    delta = local_exact - local_now
    hours = round(delta.total_seconds() / 3600.0)
    if abs(hours) <= 2:
        return "Şu anda"
    if hours > 0:
        if hours < 24:
            return f"{hours} saat içinde"
        days = round(hours / 24.0)
        return f"{days} gün içinde"
    if hours > -24:
        return f"{abs(hours)} saat önce"
    days = round(abs(hours) / 24.0)
    return f"{days} gün önce"


def _badge_tr(event: GlobalSkyEvent) -> str:
    mapping = {
        "retrograde_start": "Retro başlıyor",
        "retrograde_end": "Retro bitiyor",
        "ingress": "Burç geçişi",
        "lunation_new_moon": "Yeniay",
        "lunation_full_moon": "Dolunay",
        "eclipse": "Tutulma",
        "exact_aspect_major": "Exact açı",
    }
    return mapping.get(event.event_type, "Gökyüzü olayı")


def _cta_payload(event: GlobalSkyEvent) -> Dict[str, Any]:
    return {
        "label_tr": event.personalization_cta_label_tr,
        "enabled": True,
        "endpoint": f"/sky/events/{event.id}/personalize",
    }


def _to_feed_item(event: GlobalSkyEvent, *, now: datetime, tz: str) -> SkyFeedItem:
    return SkyFeedItem(
        id=event.id,
        slug=event.slug,
        event_type=event.event_type,
        title_tr=event.title_tr,
        short_title_tr=event.short_title_tr,
        summary_tr=event.summary_tr,
        badge_tr=_badge_tr(event),
        relative_timing_tr=_relative_timing(now, _parse_iso(event.exact_at), tz),
        phase=event.phase,
        status=event.status,
        starts_at=event.starts_at,
        exact_at=event.exact_at,
        ends_at=event.ends_at,
        visibility_window_start=event.visibility_window_start,
        visibility_window_end=event.visibility_window_end,
        importance_score=event.importance_score,
        cultural_interest_score=event.cultural_interest_score,
        feed_score=event.feed_score,
        tags=event.tags,
        bodies=event.bodies,
        aspect=event.aspect,
        sign=event.sign,
        personalization_cta=_cta_payload(event),
    )


def _summary_from_items(items: List[SkyFeedItem]) -> str:
    if not items:
        return "Bugün gökyüzünde öne çıkan güçlü bir kolektif eşik görünmüyor."
    hero = items[0]
    if hero.badge_tr == "Tutulma":
        return f"Şu anda gökyüzü {hero.short_title_tr.lower()} etrafında daha sert bir eşik hissi taşıyor."
    if hero.badge_tr in {"Retro başlıyor", "Retro bitiyor"}:
        return f"Şu anda gökyüzünün ana başlığı {hero.short_title_tr.lower()}; ritim hızdan çok ayar istiyor."
    return f"Şu anda gökyüzünde {hero.short_title_tr.lower()} başlığı kolektif ritmi belirliyor."


def _select_active_events(
    events: Iterable[GlobalSkyEvent],
    *,
    now: datetime,
    limit: int,
    event_types: Optional[set[str]] = None,
) -> List[GlobalSkyEvent]:
    filtered = []
    for event in events:
        if event_types and event.event_type not in event_types:
            continue
        visibility_start = _parse_iso(event.visibility_window_start)
        visibility_end = _parse_iso(event.visibility_window_end)
        if visibility_start <= now <= visibility_end:
            filtered.append(event)
            continue
        exact_at = _parse_iso(event.exact_at)
        if now < visibility_start and exact_at <= now + timedelta(days=4):
            filtered.append(event)
    return rank_events(filtered, now, limit=limit)


def _search_pool(anchor: datetime) -> List[GlobalSkyEvent]:
    start = anchor - timedelta(days=40)
    end = anchor + timedelta(days=50)
    return _load_events(start, end, anchor)


def get_sky_now_feed(
    *,
    now: datetime,
    tz: str,
    limit: int = 4,
    event_types: Optional[List[str]] = None,
    debug: bool = False,
) -> SkyFeedResponse:
    started = perf_counter()
    anchor = ensure_utc(now)
    search_start = anchor - timedelta(days=40)
    search_end = anchor + timedelta(days=50)
    cache_status = _cache_status(search_start, search_end, anchor)
    pool = _load_events(search_start, search_end, anchor)
    selected = _select_active_events(pool, now=anchor, limit=max(limit, 1), event_types=set(event_types or []))
    items = [_to_feed_item(event, now=anchor, tz=tz) for event in selected]
    response = SkyFeedResponse(
        generated_at=_utc_iso(datetime.now(timezone.utc)),
        now=_utc_iso(anchor),
        tz=tz,
        summary_tr=_summary_from_items(items),
        hero=items[0] if items else None,
        items=items,
        filters={"types": sorted({event.event_type for event in selected})},
        debug={
            "event_pool_size": len(pool),
            "selected_count": len(selected),
        }
        if debug
        else None,
    )
    if debug:
        return response
    if os.getenv("ENABLE_TIMING_LOGS", "true").strip().lower() in {"1", "true", "yes", "on"}:
        logger.info(
            "sky_now_timing %s",
            json.dumps(
                {
                    "endpoint": "/sky/now",
                    "cache_status": cache_status,
                    "duration_ms": round((perf_counter() - started) * 1000.0, 3),
                    "pool_size": len(pool),
                    "selected_count": len(selected),
                    "payload_bytes": len(response.model_dump_json().encode("utf-8")),
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
        )
    return response


def get_sky_feed(
    *,
    now: datetime,
    tz: str,
    limit: int = 12,
    event_types: Optional[List[str]] = None,
    window: str = "now",
    debug: bool = False,
) -> SkyFeedResponse:
    days = 7 if window == "week" else 3
    start = ensure_utc(now) - timedelta(days=days)
    end = ensure_utc(now) + timedelta(days=14 if window == "week" else 7)
    pool = _load_events(start, end, ensure_utc(now))
    selected = _select_active_events(pool, now=ensure_utc(now), limit=limit, event_types=set(event_types or []))
    items = [_to_feed_item(event, now=ensure_utc(now), tz=tz) for event in selected]
    return SkyFeedResponse(
        generated_at=_utc_iso(datetime.now(timezone.utc)),
        now=_utc_iso(now),
        tz=tz,
        summary_tr=_summary_from_items(items),
        hero=items[0] if items else None,
        items=items,
        filters={"window": window, "types": sorted({event.event_type for event in selected})},
        debug={"pool_size": len(pool)} if debug else None,
    )


def get_sky_archive(
    *,
    date_from: date,
    date_to: date,
    tz: str,
    limit: int = 50,
    event_types: Optional[List[str]] = None,
    debug: bool = False,
) -> SkyArchiveResponse:
    start = datetime.combine(date_from, time.min, tzinfo=timezone.utc) - timedelta(days=10)
    end = datetime.combine(date_to, time.max, tzinfo=timezone.utc) + timedelta(days=10)
    pool = _load_events(start, end, datetime.now(timezone.utc))
    type_filter = set(event_types or [])
    items: List[SkyFeedItem] = []
    for event in sorted(pool, key=lambda item: item.exact_at, reverse=True):
        exact_date = _parse_iso(event.exact_at).date()
        if exact_date < date_from or exact_date > date_to:
            continue
        if type_filter and event.event_type not in type_filter:
            continue
        items.append(_to_feed_item(event, now=datetime.now(timezone.utc), tz=tz))
        if len(items) >= limit:
            break
    return SkyArchiveResponse(
        generated_at=_utc_iso(datetime.now(timezone.utc)),
        tz=tz,
        range={"start": date_from.isoformat(), "end": date_to.isoformat()},
        items=items,
        total=len(items),
        debug={"pool_size": len(pool)} if debug else None,
    )


def _find_event(id_or_slug: str, anchor: datetime) -> GlobalSkyEvent | None:
    pool = _search_pool(anchor)
    for event in pool:
        if event.id == id_or_slug or event.slug == id_or_slug:
            return event
    return None


def get_sky_event_detail(
    *,
    id_or_slug: str,
    now: datetime,
    tz: str,
    debug: bool = False,
) -> SkyEventDetailResponse:
    event = _find_event(id_or_slug, ensure_utc(now))
    if event is None:
        raise KeyError(id_or_slug)
    pool = _search_pool(ensure_utc(now))
    related = [
        candidate
        for candidate in pool
        if candidate.id != event.id and abs((_parse_iso(candidate.exact_at) - _parse_iso(event.exact_at)).total_seconds()) <= 864000
    ]
    related_ranked = rank_events(related, ensure_utc(now), limit=3)
    return SkyEventDetailResponse(
        generated_at=_utc_iso(datetime.now(timezone.utc)),
        tz=tz,
        event=event,
        related_events=[_to_feed_item(item, now=ensure_utc(now), tz=tz) for item in related_ranked],
        personalization_cta=_cta_payload(event),
        debug={"related_pool": len(related)} if debug else None,
    )


def _natal_points(chart: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    points: Dict[str, Dict[str, Any]] = {}
    for name, data in (chart.get("planets") or {}).items():
        longitude = data.get("longitude")
        if isinstance(longitude, (int, float)):
            points[name] = {"longitude": float(longitude), "point_type": "planet"}
    angles = chart.get("angles") or {}
    asc = angles.get("ascendant")
    mc = angles.get("midheaven")
    if isinstance(asc, (int, float)):
        points["Ascendant"] = {"longitude": float(asc) % 360, "point_type": "angle"}
        points["Descendant"] = {"longitude": (float(asc) + 180.0) % 360, "point_type": "angle"}
    if isinstance(mc, (int, float)):
        points["Midheaven"] = {"longitude": float(mc) % 360, "point_type": "angle"}
        points["Imum Coeli"] = {"longitude": (float(mc) + 180.0) % 360, "point_type": "angle"}
    return points


def _cusp_list(chart: Dict[str, Any]) -> List[float]:
    houses = chart.get("houses") or {}
    return [float(houses[str(index)]) for index in range(1, 13) if str(index) in houses]


def _event_longitudes(event: GlobalSkyEvent) -> Dict[str, float]:
    exact = _parse_iso(event.exact_at)
    positions: Dict[str, float] = {}
    for body in event.bodies:
        positions[body] = body_state(body, exact).longitude
    return positions


def _closest_aspect(transit_lon: float, natal_lon: float, orb_limit: float = 2.5) -> tuple[str, float] | None:
    best_name: str | None = None
    best_orb = 999.0
    for name, target in ASPECT_TARGETS.items():
        orb = abs(angle_distance(transit_lon, natal_lon) - target)
        if orb <= orb_limit and orb < best_orb:
            best_name = name
            best_orb = orb
    if best_name is None:
        return None
    return best_name, round(best_orb, 2)


def personalize_sky_event(
    *,
    id_or_slug: str,
    request: SkyEventPersonalizationRequest,
    now: datetime,
) -> SkyEventPersonalizationResponse:
    event = _find_event(id_or_slug, ensure_utc(now))
    if event is None:
        raise KeyError(id_or_slug)

    natal_chart = build_natal_chart(
        {
            "birth_date": request.birth_date,
            "birth_time": request.birth_time,
            "birth_place": request.birth_place,
        }
    )
    cusps = _cusp_list(natal_chart)
    natal_points = _natal_points(natal_chart)
    event_positions = _event_longitudes(event)
    touchpoints: List[SkyPersonalTouchpoint] = []
    house_hits: Dict[int, int] = defaultdict(int)

    for body, longitude in event_positions.items():
        if len(cusps) == 12:
            house = determine_house(longitude, cusps)
            house_hits[house] += 1
        else:
            house = None
        for point_name, point_data in natal_points.items():
            match = _closest_aspect(longitude, float(point_data["longitude"]))
            if match is None:
                continue
            aspect_name, orb_deg = match
            note = f"{BODY_TR.get(body, body)} {ASPECT_LABEL_TR[aspect_name]} {point_name}"
            touchpoints.append(
                SkyPersonalTouchpoint(
                    point=point_name,
                    point_type=str(point_data["point_type"]),
                    aspect=aspect_name,
                    orb_deg=orb_deg,
                    house=house,
                    note_tr=note,
                )
            )

    touchpoints.sort(key=lambda item: (item.orb_deg or 99.0, item.point))
    top_touchpoints = touchpoints[:6]
    activated_areas = [HOUSE_LABEL_TR[house] for house, _count in sorted(house_hits.items(), key=lambda item: (-item[1], item[0]))[:3]]
    score = 35.0 + len(top_touchpoints) * 7.0
    if any(tp.point_type == "angle" for tp in top_touchpoints):
        score += 12.0
    if top_touchpoints and (top_touchpoints[0].orb_deg or 99.0) <= 1.0:
        score += 10.0
    score = min(96.0, round(score, 1))
    level = "high" if score >= 75 else "medium" if score >= 55 else "light"

    if activated_areas:
        first_area = activated_areas[0]
        summary = f"Bu gökyüzü olayı haritanda en çok {first_area} alanını hareketlendiriyor."
    else:
        summary = "Bu gökyüzü olayı haritanda bazı temaları kolektif akıştan daha belirgin tetikleyebilir."
    if top_touchpoints:
        summary += f" En yakın temas {top_touchpoints[0].note_tr.lower()} hattında görünüyor."

    return SkyEventPersonalizationResponse(
        generated_at=_utc_iso(datetime.now(timezone.utc)),
        event_id=event.id,
        event_slug=event.slug,
        impact_score=score,
        relevance_level=level,
        summary_tr=summary,
        activated_areas_tr=activated_areas,
        matched_natal_points=top_touchpoints,
        strongest_window_start=event.starts_at,
        strongest_window_end=event.ends_at,
        related_personal_transit_ids=[],
        debug={
            "house_hits": dict(house_hits),
            "event_positions": {body: round(lon, 3) for body, lon in event_positions.items()},
        },
    )
