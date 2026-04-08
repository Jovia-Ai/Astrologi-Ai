from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta
import hashlib
import math
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from app.astro.chart_engine.builder import LocationData, resolve_location
from app.astro.chart_engine.positions import get_zodiac_sign
from app.engine.transit_engine import (
    ASPECT_ANGLES,
    _build_chart_snapshot,
    _calc_bodies,
    _calc_houses,
    _house_from_cusps,
    _min_angle_diff,
    _normalize_options,
    fetch_location,
    julian_day,
)
from app.transit.astro.rulership import ruler_of


PLANET_CLASS = {
    "Moon": "personal",
    "Mercury": "personal",
    "Venus": "personal",
    "Mars": "personal",
    "Jupiter": "social",
    "Saturn": "social",
    "Uranus": "outer",
    "Neptune": "outer",
    "Pluto": "outer",
    "Sun": "luminary",
    "North Node": "node",
    "South Node": "node",
    "Chiron": "healer",
    "ASC": "angle",
    "DSC": "angle",
    "MC": "angle",
    "IC": "angle",
    "Fortune": "point",
    "Vertex": "point",
    "Lilith": "point",
}

PLANET_CLASS_WEIGHT = {
    "point": 0.30,
    "angle": 0.75,
    "personal": 0.52,
    "social": 0.74,
    "outer": 0.92,
    "luminary": 0.82,
    "node": 0.78,
    "healer": 0.72,
}

EVENT_FAMILY_WEIGHT = {
    "aspect_event": 0.46,
    "cycle_event": 0.92,
    "house_ingress_event": 0.80,
    "station_event": 0.62,
    "lunation_trigger": 0.38,
    "eclipse_trigger": 0.72,
    "global_sky_event": 0.48,
    "solar_year_theme": 0.86,
}

EVENT_KIND_LABEL_TR = {
    "trigger": "Tetik",
    "emphasis": "Kisa vurgu",
    "season": "Donem temasi",
    "chapter": "Ana chapter",
    "transformation": "Derin donusum",
}

RECOGNITION_ORDER = {"low": 0, "medium": 1, "high": 2}
IMPORTANCE_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}

HOUSE_LABEL_TR = {
    1: "benlik",
    2: "maddi duzen",
    3: "iletisim ve zihin",
    4: "ev ve aidiyet",
    5: "yaraticilik ve keyif",
    6: "rutin ve saglik",
    7: "iliskiler",
    8: "paylasim ve donusum",
    9: "ufuk ve inanc",
    10: "kariyer ve yon",
    11: "topluluk ve hedefler",
    12: "ic dunya ve geri cekilme",
}

PLANET_TR = {
    "Sun": "Gunes",
    "Moon": "Ay",
    "Mercury": "Merkur",
    "Venus": "Venus",
    "Mars": "Mars",
    "Jupiter": "Jupiter",
    "Saturn": "Saturn",
    "Uranus": "Uranus",
    "Neptune": "Neptun",
    "Pluto": "Pluton",
    "North Node": "Kuzey Ay Dugumu",
    "South Node": "Guney Ay Dugumu",
    "Chiron": "Kiron",
    "ASC": "Yukselen",
    "DSC": "Alcalan",
    "MC": "Tepe Noktasi",
    "IC": "Dip Noktasi",
}

SIGN_TR = {
    "Aries": "Koc",
    "Taurus": "Boga",
    "Gemini": "Ikizler",
    "Cancer": "Yengec",
    "Leo": "Aslan",
    "Virgo": "Basak",
    "Libra": "Terazi",
    "Scorpio": "Akrep",
    "Sagittarius": "Yay",
    "Capricorn": "Oglak",
    "Aquarius": "Kova",
    "Pisces": "Balik",
}

ASPECT_TR = {
    "conjunction": "kavusum",
    "opposition": "karsitlik",
    "square": "kare",
    "trine": "ucgen",
    "sextile": "sekstil",
}

BEHAVIOR_MAP = {
    "Mars": "hareket, cesaret ve gerilim",
    "Venus": "ilgi, deger ve iliski tonu",
    "Mercury": "dusunce, mesaj ve plan",
    "Jupiter": "genisleme, firsat ve anlam",
    "Saturn": "sorumluluk, sinir ve olgunlasma",
    "Uranus": "ani degisim ve ozgurluk ihtiyaci",
    "Neptune": "cozulme, hassasiyet ve belirsizlik",
    "Pluto": "guc, yogunluk ve derin donusum",
    "Sun": "kimlik ve gorunurluk",
    "Moon": "duygu ve ihtiyac",
    "North Node": "yon duygusu ve gelisim hatti",
    "South Node": "gecmis kaliplari ve birakma hatt",
    "Chiron": "hassas nokta ve iyilesme ihtiyaci",
}

GLOBAL_BODIES = {
    "Mercury",
    "Venus",
    "Mars",
    "Sun",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
    "North Node",
    "South Node",
}

HOUSE_INGRESS_BODIES = {"Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "North Node", "South Node"}

SLOW_GLOBAL_ASPECT_BODIES = ["Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

TARGET_LOW_PRIORITY = {"Fortune", "Vertex", "Lilith"}
ANGLE_POINTS = {"ASC", "DSC", "MC", "IC"}
LUMINARY_POINTS = {"Sun", "Moon"}
CHAPTER_POINTS = ANGLE_POINTS | LUMINARY_POINTS | {"North Node", "South Node"}


@dataclass
class AstroEventV2:
    event_id: str
    event_family: str
    event_subtype: str
    audience: str
    event_kind: str
    importance_tier: str
    planet_class: str
    time_scale: str
    significance_score: float
    lasting_change_score: float
    chapter_opening: bool
    repeat_pass_count: int
    is_structural: bool
    recognition_intensity: str
    precision_signal: float
    planet_class_weight: float
    target_importance: float
    event_family_weight: float
    duration_weight: float
    repeat_pass_weight: float
    structural_significance: float
    angle_luminary_weight: float
    solar_resonance: float
    collective_interest_score: float
    start_at: Optional[str] = None
    exact_at: List[str] = field(default_factory=list)
    end_at: Optional[str] = None
    current_phase: str = "active"
    source_bodies: List[str] = field(default_factory=list)
    target_points: List[str] = field(default_factory=list)
    target_houses: List[int] = field(default_factory=list)
    title_tr: str = ""
    subtitle_tr: str = ""
    summary_tr: str = ""
    why_now_tr: str = ""
    guidance_tr: List[str] = field(default_factory=list)
    watch_for_tr: List[str] = field(default_factory=list)
    time_hint_tr: str = ""
    importance_label_tr: str = ""
    copy_mode: str = ""
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["significance_score"] = round(float(self.significance_score), 3)
        payload["lasting_change_score"] = round(float(self.lasting_change_score), 3)
        payload["precision_signal"] = round(float(self.precision_signal), 3)
        payload["planet_class_weight"] = round(float(self.planet_class_weight), 3)
        payload["target_importance"] = round(float(self.target_importance), 3)
        payload["event_family_weight"] = round(float(self.event_family_weight), 3)
        payload["duration_weight"] = round(float(self.duration_weight), 3)
        payload["repeat_pass_weight"] = round(float(self.repeat_pass_weight), 3)
        payload["structural_significance"] = round(float(self.structural_significance), 3)
        payload["angle_luminary_weight"] = round(float(self.angle_luminary_weight), 3)
        payload["solar_resonance"] = round(float(self.solar_resonance), 3)
        payload["collective_interest_score"] = round(float(self.collective_interest_score), 3)
        return payload


def build_personal_multi_event_payload(
    *,
    report: Mapping[str, Any],
    transit_date: str,
    transit_place: str,
    transit_latitude: float | None = None,
    transit_longitude: float | None = None,
    transit_timezone: str | None = None,
    window_report: Mapping[str, Any] | None = None,
    solar_year: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    natal = report.get("natal") if isinstance(report.get("natal"), Mapping) else {}
    display = report.get("display") if isinstance(report.get("display"), Mapping) else {}
    items = [dict(item) for item in (display.get("items") or []) if isinstance(item, Mapping)]
    solar_frame = dict(solar_year or {})
    if not solar_frame:
        solar_frame = build_solar_year_theme(
            birth_date=str((report.get("request_echo") or {}).get("birth_date") or ""),
            birth_time=str((report.get("request_echo") or {}).get("birth_time") or ""),
            birth_place=str((report.get("request_echo") or {}).get("birth_place") or ""),
            transit_date=transit_date,
            transit_place=transit_place,
            transit_latitude=transit_latitude,
            transit_longitude=transit_longitude,
            transit_timezone=transit_timezone,
            natal_snapshot=natal,
        )

    personal_events = [
        adapt_aspect_item_to_v2(item, natal_snapshot=natal, solar_year=solar_frame)
        for item in items
    ]
    personal_events = sorted(
        personal_events,
        key=lambda entry: (
            -float(entry.significance_score),
            -IMPORTANCE_ORDER.get(entry.importance_tier, 0),
            entry.event_id,
        ),
    )

    window_events = [dict(item) for item in ((window_report or {}).get("events") or []) if isinstance(item, Mapping)]
    cycle_events = detect_cycle_events(window_events, natal_snapshot=natal, solar_year=solar_frame)
    ingress_events = detect_house_ingress_events(
        natal_snapshot=natal,
        transit_place=transit_place,
        transit_location=resolve_location(
            transit_place,
            latitude=transit_latitude,
            longitude=transit_longitude,
            timezone=transit_timezone,
        ),
        start_date=_window_start(transit_date, days=120),
        end_date=_window_end(transit_date, days=120),
        transit_date=transit_date,
        solar_year=solar_frame,
    )
    structural_events = sorted(
        cycle_events + ingress_events,
        key=lambda entry: (
            -float(entry.significance_score),
            -IMPORTANCE_ORDER.get(entry.importance_tier, 0),
            entry.event_id,
        ),
    )

    by_id = {event.event_id: event.to_dict() for event in personal_events + structural_events}
    return {
        "schema_version": "astro_event.v2",
        "personal_transit_rail": [event.to_dict() for event in personal_events[:24]],
        "structural_chapter_rail": [event.to_dict() for event in structural_events[:12]],
        "solar_year_frame": solar_frame,
        "events_by_id": by_id,
    }


def detect_global_sky_events(
    *,
    start: str,
    end: str,
    transit_place: str,
    tz: str,
    top_n: int = 24,
) -> Dict[str, Any]:
    start_dt = _parse_date(start)
    end_dt = _parse_date(end)
    phase_events = _global_phase_events(start_dt, end_dt, transit_place)
    lunations = _detect_lunations(start_dt, end_dt, transit_place)
    exact_aspects = _detect_global_exact_aspects(start_dt, end_dt, transit_place)
    events = phase_events + lunations + exact_aspects
    events.sort(
        key=lambda entry: (
            -float(entry.collective_interest_score),
            -float(entry.significance_score),
            entry.event_id,
        )
    )
    return {
        "schema_version": "astro_event.v2",
        "range": {"start": start, "end": end, "tz": tz, "transit_place": transit_place},
        "events": [event.to_dict() for event in events[:top_n]],
    }


def personalize_global_event(
    *,
    global_event: Mapping[str, Any],
    birth_date: str,
    birth_time: str,
    birth_place: str,
    transit_place: str,
    transit_date: str,
) -> Dict[str, Any]:
    natal_snapshot = _build_chart_snapshot(
        date_value=birth_date,
        time_value=birth_time,
        place_value=birth_place,
        location=resolve_location(birth_place),
        options=_normalize_options(None),
    )
    solar_year = build_solar_year_theme(
        birth_date=birth_date,
        birth_time=birth_time,
        birth_place=birth_place,
        transit_date=transit_date,
        transit_place=transit_place,
        natal_snapshot=natal_snapshot,
    )
    source_bodies = [str(value) for value in (global_event.get("source_bodies") or []) if str(value).strip()]
    exact_at = [str(value) for value in (global_event.get("exact_at") or []) if str(value).strip()]
    event_time = exact_at[0] if exact_at else (global_event.get("start_at") or transit_date)
    source_positions = _positions_for_bodies(
        bodies=source_bodies or ["Sun"],
        when_iso=str(event_time),
        place=transit_place,
    )
    activated_houses = _activated_houses_for_positions(natal_snapshot=natal_snapshot, positions=source_positions)
    natal_contacts = _closest_natal_contacts(natal_snapshot=natal_snapshot, positions=source_positions)

    target_points = [entry["point"] for entry in natal_contacts[:2]]
    target_houses = [house for house in activated_houses if isinstance(house, int)]
    precision_signal = max([float(entry.get("precision_signal") or 0.0) for entry in natal_contacts] or [0.45])
    target_importance = max([float(entry.get("target_importance") or 0.0) for entry in natal_contacts] or [0.44])
    base_family = str(global_event.get("event_family") or "global_sky_event")
    subtype = str(global_event.get("event_subtype") or "bridge_projection")
    start_at = str(global_event.get("start_at") or "")
    end_at = str(global_event.get("end_at") or "")
    exact = [str(value) for value in (global_event.get("exact_at") or []) if str(value).strip()]
    title = _bridge_title(source_bodies, target_points, activated_houses)
    subtitle = _bridge_subtitle(target_points, activated_houses)
    summary = _bridge_summary(source_bodies, target_points, activated_houses)
    why_now = _bridge_why_now(natal_contacts, activated_houses, solar_year)
    guidance = _bridge_guidance(target_points, activated_houses)
    watch_for = _bridge_watch_for(target_points)

    bridge_event = _build_event(
        event_id=_hash_id(f"bridge|{global_event.get('event_id')}|{birth_date}|{birth_time}|{birth_place}"),
        event_family=base_family,
        event_subtype=f"bridge.{subtype}",
        audience="bridge",
        source_bodies=source_bodies,
        target_points=target_points,
        target_houses=target_houses,
        start_at=start_at or transit_date,
        exact_at=exact,
        end_at=end_at or start_at or transit_date,
        current_phase="active",
        precision_signal=precision_signal,
        duration_days=max(1, _days_between(start_at or transit_date, end_at or start_at or transit_date)),
        repeat_pass_count=1,
        is_structural=bool(target_points and any(point in CHAPTER_POINTS for point in target_points)),
        structural_significance=0.65 if target_points and any(point in CHAPTER_POINTS for point in target_points) else 0.35,
        chapter_opening=any(point in CHAPTER_POINTS for point in target_points),
        target_importance_override=target_importance,
        solar_year=solar_year,
        collective_interest_score=float(global_event.get("collective_interest_score") or 0.25),
        title_tr=title,
        subtitle_tr=subtitle,
        summary_tr=summary,
        why_now_tr=why_now,
        guidance_tr=guidance,
        watch_for_tr=watch_for,
        time_hint_tr=_time_hint_from_dates(start_at or transit_date, end_at or start_at or transit_date),
        provenance={
            "detector": "global_bridge.v1",
            "source_event_id": global_event.get("event_id"),
            "natal_contacts": natal_contacts[:4],
            "activated_houses": activated_houses,
        },
    )

    return {
        "schema_version": "astro_event.v2",
        "global_event": dict(global_event),
        "bridge": bridge_event.to_dict(),
        "solar_year_frame": solar_year,
    }


def build_solar_year_theme(
    *,
    birth_date: str,
    birth_time: str,
    birth_place: str,
    transit_date: str,
    transit_place: str,
    birth_latitude: float | None = None,
    birth_longitude: float | None = None,
    birth_timezone: str | None = None,
    transit_latitude: float | None = None,
    transit_longitude: float | None = None,
    transit_timezone: str | None = None,
    natal_snapshot: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    if not birth_date or not birth_time or not birth_place or not transit_date:
        return {}
    birth_location = resolve_location(
        birth_place,
        latitude=birth_latitude,
        longitude=birth_longitude,
        timezone=birth_timezone,
    )
    transit_location = resolve_location(
        transit_place or birth_place,
        latitude=transit_latitude,
        longitude=transit_longitude,
        timezone=transit_timezone,
    )
    natal = dict(natal_snapshot or _build_chart_snapshot(
        date_value=birth_date,
        time_value=birth_time,
        place_value=birth_place,
        location=birth_location,
        options=_normalize_options(None),
    ))
    natal_sun = _body_position(natal, "Sun")
    natal_sun_lon = float(natal_sun.get("lon") or 0.0)
    target_date = _parse_date(transit_date)
    candidate_years = [target_date.year, target_date.year - 1]
    return_time: Optional[datetime] = None
    for year in candidate_years:
        candidate = _solar_return_datetime(
            natal_sun_lon=natal_sun_lon,
            birth_date=birth_date,
            year=year,
            place=transit_place or birth_place,
            location=transit_location,
        )
        if candidate is None:
            continue
        if candidate.date() <= target_date:
            return_time = candidate
            break
        if return_time is None:
            return_time = candidate
    if return_time is None:
        return {}

    solar_snapshot = _build_chart_snapshot(
        date_value=return_time.date().isoformat(),
        time_value=return_time.strftime("%H:%M"),
        place_value=transit_place or birth_place,
        location=transit_location,
        options=_normalize_options(None),
    )
    next_return = _solar_return_datetime(
        natal_sun_lon=natal_sun_lon,
        birth_date=birth_date,
        year=return_time.year + 1,
        place=transit_place or birth_place,
        location=transit_location,
    )

    asc_sign = _angle_sign(solar_snapshot, "ASC")
    mc_sign = _angle_sign(solar_snapshot, "MC")
    solar_sun = _body_position(solar_snapshot, "Sun")
    solar_sun_house = _safe_int(solar_sun.get("house"))
    year_ruler = ruler_of(asc_sign)
    dominant_houses = _dominant_solar_houses(solar_snapshot)
    overlays = _solar_natal_overlays(natal_snapshot=natal, solar_snapshot=solar_snapshot, year_ruler=year_ruler)
    themes = _solar_themes_tr(solar_sun_house, dominant_houses, year_ruler)
    significance = 0.74
    if solar_sun_house in {1, 4, 7, 10}:
        significance += 0.08
    significance += min(0.12, len([house for house in dominant_houses if house in {1, 4, 7, 10}]) * 0.04)
    event_kind = "chapter" if significance >= 0.82 else "season"
    importance_tier = "critical" if significance >= 0.88 else "high"
    recognition = "high" if event_kind == "chapter" else "medium"
    title = f"Bu yilin ana sahnesi: {_solar_title_tr(solar_sun_house, dominant_houses)}"
    summary = _solar_summary_tr(solar_sun_house, dominant_houses, year_ruler, overlays)
    why_now = _solar_why_now_tr(solar_sun_house, dominant_houses, year_ruler)

    frame = {
        "event_id": _hash_id(f"solar|{birth_date}|{birth_time}|{birth_place}|{return_time.isoformat()}"),
        "event_family": "solar_year_theme",
        "event_subtype": "solar_return_frame",
        "audience": "solar",
        "event_kind": event_kind,
        "importance_tier": importance_tier,
        "planet_class": PLANET_CLASS.get(year_ruler, "social"),
        "time_scale": "annual",
        "significance_score": round(significance, 3),
        "lasting_change_score": round(0.78 if event_kind == "chapter" else 0.64, 3),
        "chapter_opening": True,
        "repeat_pass_count": 1,
        "is_structural": True,
        "recognition_intensity": recognition,
        "start_at": return_time.date().isoformat(),
        "exact_at": [return_time.isoformat()],
        "end_at": next_return.date().isoformat() if next_return else "",
        "current_phase": "active",
        "source_bodies": [body for body in ["Sun", year_ruler] if body],
        "target_points": [point for point in [year_ruler, "Sun"] if point],
        "target_houses": dominant_houses,
        "title_tr": title,
        "subtitle_tr": f"Yilin ritmi {PLANET_TR.get(year_ruler, year_ruler)} ve {', '.join(_house_name(h) for h in dominant_houses[:2])} uzerinden akiyor.",
        "summary_tr": summary,
        "why_now_tr": why_now,
        "guidance_tr": [
            "Yilin ana temasini gunluk telaşa kurban etme.",
            "En cok calisan iki evi takvim ve onceliklerinde gorunur kil.",
            "Hizli transitleri bu ana sahneye gore yorumla.",
        ],
        "watch_for_tr": [
            "Gunun tetigini yilin ana hikayesi sanmak.",
            "Yil yoneticisinin istedigi disiplini ertelemek.",
        ],
        "time_hint_tr": f"Etki {return_time.date().isoformat()} ile {(next_return.date().isoformat() if next_return else '')} arasinda yilin ana zemini olarak calisir.".strip(),
        "importance_label_tr": EVENT_KIND_LABEL_TR.get(event_kind, "Donem temasi"),
        "copy_mode": "solar_year",
        "collective_interest_score": 0.0,
        "solar_return_at": return_time.isoformat(),
        "year_start": return_time.date().isoformat(),
        "year_end": next_return.date().isoformat() if next_return else "",
        "solar_asc": {"sign": asc_sign, "label_tr": SIGN_TR.get(asc_sign, asc_sign)},
        "solar_mc": {"sign": mc_sign, "label_tr": SIGN_TR.get(mc_sign, mc_sign)},
        "solar_sun_house": solar_sun_house,
        "year_ruler": year_ruler,
        "dominant_houses": dominant_houses,
        "dominant_house_labels_tr": [_house_name(h) for h in dominant_houses],
        "solar_natal_overlays": overlays,
        "themes_tr": themes,
        "provenance": {"detector": "solar_year_frame.v1", "solar_return_at": return_time.isoformat()},
    }
    return frame


def adapt_aspect_item_to_v2(
    item: Mapping[str, Any],
    *,
    natal_snapshot: Mapping[str, Any] | None = None,
    solar_year: Mapping[str, Any] | None = None,
) -> AstroEventV2:
    timing = item.get("timing") if isinstance(item.get("timing"), Mapping) else {}
    start_at = str(timing.get("entry_date_utc") or "")
    peak = str(timing.get("peak_date_utc") or "")
    end_at = str(timing.get("exit_date_utc") or "")
    exact_at = [peak] if peak else []
    orb_deg = _safe_float(item.get("orb_deg"), 9.0)
    precision_signal = max(0.1, min(1.0, 1.0 - (orb_deg / 6.0)))
    bucket = str(item.get("bucket") or "medium").lower()
    duration_days = _duration_days_from_bucket(bucket, start_at, end_at)
    transit_body = str(item.get("transit_body") or "")
    natal_point = str(item.get("natal_point") or "")
    polarity = str(item.get("polarity") or "neutral")
    structural = transit_body in {"Saturn", "Uranus", "Neptune", "Pluto", "North Node", "South Node"} and (
        natal_point in CHAPTER_POINTS or polarity in {"hard", "neutral"}
    )
    chapter_opening = structural and str(item.get("phase") or "").lower() in {"applying", "exact", "exactish"}
    subtitle = _aspect_subtitle_tr(transit_body, natal_point, item.get("aspect"), item.get("houses"))
    summary = _aspect_summary_tr(transit_body, natal_point, item.get("aspect"), bucket, item.get("houses"))
    why_now = _aspect_why_now_tr(transit_body, natal_point, item.get("phase"), item.get("houses"), solar_year)
    guidance = _aspect_guidance_tr(transit_body, natal_point, bucket)
    watch_for = _aspect_watch_for_tr(transit_body, natal_point)
    time_hint = _aspect_time_hint_tr(start_at, peak, end_at, bucket)

    return _build_event(
        event_id=str(item.get("event_id") or _hash_id(f"aspect|{transit_body}|{item.get('aspect')}|{natal_point}")),
        event_family="aspect_event",
        event_subtype=str(item.get("aspect") or "aspect"),
        audience="personal",
        source_bodies=[transit_body] if transit_body else [],
        target_points=[natal_point] if natal_point else [],
        target_houses=_houses_from_item(item),
        start_at=start_at or peak or "",
        exact_at=exact_at,
        end_at=end_at or peak or start_at or "",
        current_phase=str(item.get("phase") or "active"),
        precision_signal=precision_signal,
        duration_days=duration_days,
        repeat_pass_count=max(1, len([value for value in (timing.get("peaks") or []) if value])),
        is_structural=structural,
        structural_significance=0.72 if structural else 0.34,
        chapter_opening=chapter_opening,
        natal_snapshot=natal_snapshot,
        solar_year=solar_year,
        collective_interest_score=0.0,
        title_tr=_aspect_title_tr(transit_body, natal_point),
        subtitle_tr=subtitle,
        summary_tr=summary,
        why_now_tr=why_now,
        guidance_tr=guidance,
        watch_for_tr=watch_for,
        time_hint_tr=time_hint,
        provenance={
            "detector": "aspect_adapter.v2",
            "legacy_scope": item.get("scope"),
            "orb_deg": orb_deg,
            "legacy_bucket": bucket,
            "legacy_tier": (item.get("ranking") or {}).get("tier"),
        },
    )


def detect_cycle_events(
    window_events: Sequence[Mapping[str, Any]],
    *,
    natal_snapshot: Mapping[str, Any] | None = None,
    solar_year: Mapping[str, Any] | None = None,
) -> List[AstroEventV2]:
    out: List[AstroEventV2] = []
    for raw in window_events:
        transit = str(raw.get("transit") or "")
        natal = str(raw.get("natal") or "")
        aspect = str(raw.get("aspect") or "")
        subtype = _cycle_subtype(transit, natal, aspect)
        if not subtype:
            continue
        timebox = raw.get("timebox") if isinstance(raw.get("timebox"), Mapping) else {}
        peaks = timebox.get("peaks") or []
        exact_at = [str(entry.get("t") or "") for entry in peaks if str(entry.get("t") or "").strip()]
        min_orb = _safe_float((raw.get("orb") or {}).get("min"), 2.5)
        title = _cycle_title_tr(subtype, transit, natal)
        summary = _cycle_summary_tr(subtype, transit, natal)
        why_now = _cycle_why_now_tr(subtype, raw)
        guidance = _cycle_guidance_tr(subtype, transit, natal)
        watch_for = _cycle_watch_for_tr(subtype, transit)
        out.append(
            _build_event(
                event_id=_hash_id(f"cycle|{transit}|{aspect}|{natal}|{timebox.get('enter')}|{timebox.get('exit')}"),
                event_family="cycle_event",
                event_subtype=subtype,
                audience="personal",
                source_bodies=[transit] if transit else [],
                target_points=[natal] if natal else [],
                target_houses=_target_houses_for_points(natal_snapshot, [natal]),
                start_at=str(timebox.get("enter") or ""),
                exact_at=exact_at,
                end_at=str(timebox.get("exit") or ""),
                current_phase=_phase_from_now(raw),
                precision_signal=max(0.25, min(1.0, 1.0 - (min_orb / 6.0))),
                duration_days=int(raw.get("duration_days") or 120),
                repeat_pass_count=max(1, len(exact_at)),
                is_structural=True,
                structural_significance=_cycle_structural_significance(subtype, transit, natal),
                chapter_opening=True,
                natal_snapshot=natal_snapshot,
                solar_year=solar_year,
                collective_interest_score=0.0,
                title_tr=title,
                subtitle_tr=_cycle_subtitle_tr(subtype, transit, natal),
                summary_tr=summary,
                why_now_tr=why_now,
                guidance_tr=guidance,
                watch_for_tr=watch_for,
                time_hint_tr=_time_hint_from_dates(str(timebox.get("enter") or ""), str(timebox.get("exit") or "")),
                provenance={
                    "detector": "cycle_event.v1",
                    "window_event_id": raw.get("id"),
                    "min_orb": min_orb,
                    "peaks": peaks,
                },
            )
        )
    return out


def detect_house_ingress_events(
    *,
    natal_snapshot: Mapping[str, Any],
    transit_place: str,
    start_date: str,
    end_date: str,
    transit_date: str,
    transit_location: LocationData | None = None,
    solar_year: Mapping[str, Any] | None = None,
) -> List[AstroEventV2]:
    start_dt = _parse_date(start_date)
    end_dt = _parse_date(end_date)
    cusps = [cusp.get("lon") for cusp in (natal_snapshot.get("house_cusps") or []) if cusp.get("lon") is not None]
    if len(cusps) < 12:
        return []
    resolved_location = transit_location or resolve_location(transit_place)
    prev_house: Dict[str, int] = {}
    pass_map: Dict[Tuple[str, int], List[Dict[str, Any]]] = {}
    current = start_dt
    while current <= end_dt:
        positions = _positions_for_bodies(
            bodies=sorted(HOUSE_INGRESS_BODIES),
            when_iso=current.isoformat(),
            place=transit_place,
            hour="12:00",
            location=resolved_location,
        )
        for position in positions:
            body = str(position.get("body") or "")
            lon = position.get("lon")
            if lon is None:
                continue
            house = _house_from_cusps(float(lon), cusps)
            previous = prev_house.get(body)
            if previous is not None and previous != house:
                pass_map.setdefault((body, house), []).append(
                    {
                        "body": body,
                        "from_house": previous,
                        "to_house": house,
                        "entry": current.isoformat(),
                    }
                )
            prev_house[body] = house
        current += timedelta(days=1)

    out: List[AstroEventV2] = []
    for (body, to_house), entries in pass_map.items():
        total = len(entries)
        for index, entry in enumerate(entries, start=1):
            start_at = str(entry.get("entry") or "")
            exit_at = _next_house_change(pass_map, body, to_house, start_at, end_dt.isoformat())
            phase = "final_settlement" if total == index else ("initial_entry" if index == 1 else "re_entry")
            subtitle = f"{PLANET_TR.get(body, body)} {to_house}. eve geciyor."
            summary = _house_ingress_summary_tr(body, to_house, phase)
            why_now = _house_ingress_why_now_tr(body, to_house, phase, solar_year)
            guidance = _house_ingress_guidance_tr(body, to_house)
            watch_for = _house_ingress_watch_for_tr(body)
            out.append(
                _build_event(
                    event_id=_hash_id(f"house_ingress|{body}|{to_house}|{start_at}|{index}"),
                    event_family="house_ingress_event",
                    event_subtype=f"{body.lower()}.house_{to_house}",
                    audience="personal",
                    source_bodies=[body],
                    target_points=[],
                    target_houses=[to_house],
                    start_at=start_at,
                    exact_at=[start_at],
                    end_at=exit_at,
                    current_phase=phase,
                    precision_signal=0.76 if phase == "final_settlement" else 0.66,
                    duration_days=max(30, _duration_for_ingress(body)),
                    repeat_pass_count=total,
                    is_structural=True,
                    structural_significance=_house_ingress_structural_significance(body, to_house),
                    chapter_opening=index == 1,
                    natal_snapshot=natal_snapshot,
                    solar_year=solar_year,
                    collective_interest_score=0.0,
                    title_tr=_house_ingress_title_tr(body, to_house),
                    subtitle_tr=subtitle,
                    summary_tr=summary,
                    why_now_tr=why_now,
                    guidance_tr=guidance,
                    watch_for_tr=watch_for,
                    time_hint_tr=_time_hint_from_dates(start_at, exit_at),
                    provenance={
                        "detector": "house_ingress.v1",
                        "from_house": entry.get("from_house"),
                        "to_house": to_house,
                        "pass_index": index,
                        "repeat_pass_count": total,
                    },
                )
            )
    out.sort(key=lambda event: (-float(event.significance_score), event.event_id))
    return out


def enrich_legacy_aspect_item(
    item: Dict[str, Any],
    *,
    natal_snapshot: Mapping[str, Any] | None = None,
    solar_year: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    event = adapt_aspect_item_to_v2(item, natal_snapshot=natal_snapshot, solar_year=solar_year)
    enriched = dict(item)
    enriched.update(
        {
            "event_family": event.event_family,
            "event_subtype": event.event_subtype,
            "audience": event.audience,
            "event_kind": event.event_kind,
            "importance_tier": event.importance_tier,
            "planet_class": event.planet_class,
            "time_scale": event.time_scale,
            "significance_score": round(event.significance_score, 3),
            "lasting_change_score": round(event.lasting_change_score, 3),
            "chapter_opening": event.chapter_opening,
            "repeat_pass_count": event.repeat_pass_count,
            "is_structural": event.is_structural,
            "recognition_intensity": event.recognition_intensity,
            "importance_label_tr": event.importance_label_tr,
            "copy_mode": event.copy_mode,
            "rank_components": {
                "precision_signal": round(event.precision_signal, 3),
                "planet_class_weight": round(event.planet_class_weight, 3),
                "target_importance": round(event.target_importance, 3),
                "event_family_weight": round(event.event_family_weight, 3),
                "duration_weight": round(event.duration_weight, 3),
                "repeat_pass_weight": round(event.repeat_pass_weight, 3),
                "structural_significance": round(event.structural_significance, 3),
                "lasting_change_score": round(event.lasting_change_score, 3),
                "angle_luminary_weight": round(event.angle_luminary_weight, 3),
                "solar_resonance": round(event.solar_resonance, 3),
            },
            "_astro_event_v2": event.to_dict(),
        }
    )
    return enriched


def _build_event(
    *,
    event_id: str,
    event_family: str,
    event_subtype: str,
    audience: str,
    source_bodies: List[str],
    target_points: List[str],
    target_houses: List[int],
    start_at: str,
    exact_at: List[str],
    end_at: str,
    current_phase: str,
    precision_signal: float,
    duration_days: int,
    repeat_pass_count: int,
    is_structural: bool,
    structural_significance: float,
    chapter_opening: bool,
    natal_snapshot: Mapping[str, Any] | None = None,
    solar_year: Mapping[str, Any] | None = None,
    collective_interest_score: float = 0.0,
    target_importance_override: float | None = None,
    title_tr: str = "",
    subtitle_tr: str = "",
    summary_tr: str = "",
    why_now_tr: str = "",
    guidance_tr: List[str] | None = None,
    watch_for_tr: List[str] | None = None,
    time_hint_tr: str = "",
    provenance: Dict[str, Any] | None = None,
) -> AstroEventV2:
    primary_source = source_bodies[0] if source_bodies else ""
    primary_target = target_points[0] if target_points else ""
    planet_class = PLANET_CLASS.get(primary_source, "social" if primary_source in {"Jupiter", "Saturn"} else "personal")
    planet_weight = PLANET_CLASS_WEIGHT.get(planet_class, 0.55)
    target_importance = (
        target_importance_override
        if target_importance_override is not None
        else _target_importance(primary_target, target_houses, natal_snapshot)
    )
    family_weight = EVENT_FAMILY_WEIGHT.get(event_family, 0.42)
    duration_weight = _duration_weight(duration_days, event_family)
    repeat_weight = min(1.0, 0.60 + min(max(repeat_pass_count, 1), 4) * 0.10)
    lasting_change = _lasting_change_score(
        source=primary_source,
        target=primary_target,
        target_houses=target_houses,
        event_family=event_family,
        structural_significance=structural_significance,
        repeat_pass_count=repeat_pass_count,
    )
    angle_weight = _angle_luminary_weight(primary_target, target_houses, natal_snapshot, primary_source)
    solar_resonance = _solar_resonance(source_bodies, target_points, target_houses, solar_year)
    significance = (
        0.14 * precision_signal
        + 0.12 * planet_weight
        + 0.14 * target_importance
        + 0.18 * family_weight
        + 0.10 * duration_weight
        + 0.08 * repeat_weight
        + 0.14 * structural_significance
        + 0.10 * lasting_change
    )
    significance *= 1 + 0.08 * angle_weight + 0.12 * solar_resonance
    significance += 0.06 * collective_interest_score
    significance = max(0.0, min(1.0, significance))
    event_kind = _classify_event_kind(
        event_family=event_family,
        planet_class=planet_class,
        primary_source=primary_source,
        primary_target=primary_target,
        target_houses=target_houses,
        duration_days=duration_days,
        structural_significance=structural_significance,
        lasting_change_score=lasting_change,
        precision_signal=precision_signal,
        collective_interest_score=collective_interest_score,
    )
    importance_tier = _importance_tier(significance, event_kind, is_structural)
    recognition = _recognition_intensity(event_kind, importance_tier, audience, angle_weight, lasting_change)
    if not title_tr:
        title_tr = _generic_title_tr(event_family, primary_source, primary_target, target_houses)
    if not summary_tr:
        summary_tr = _generic_summary_tr(event_family, primary_source, primary_target, target_houses, event_kind)
    if not why_now_tr:
        why_now_tr = _generic_why_now_tr(event_family, primary_source, primary_target, target_houses, solar_year)
    if not time_hint_tr:
        time_hint_tr = _time_hint_from_dates(start_at, end_at)
    return AstroEventV2(
        event_id=event_id,
        event_family=event_family,
        event_subtype=event_subtype,
        audience=audience,
        event_kind=event_kind,
        importance_tier=importance_tier,
        planet_class=planet_class,
        time_scale=_time_scale(duration_days, event_family),
        significance_score=significance,
        lasting_change_score=lasting_change,
        chapter_opening=chapter_opening,
        repeat_pass_count=max(1, repeat_pass_count),
        is_structural=is_structural,
        recognition_intensity=recognition,
        precision_signal=precision_signal,
        planet_class_weight=planet_weight,
        target_importance=target_importance,
        event_family_weight=family_weight,
        duration_weight=duration_weight,
        repeat_pass_weight=repeat_weight,
        structural_significance=structural_significance,
        angle_luminary_weight=angle_weight,
        solar_resonance=solar_resonance,
        collective_interest_score=collective_interest_score,
        start_at=start_at or None,
        exact_at=[value for value in exact_at if value],
        end_at=end_at or None,
        current_phase=current_phase or "active",
        source_bodies=source_bodies,
        target_points=target_points,
        target_houses=target_houses,
        title_tr=title_tr,
        subtitle_tr=subtitle_tr,
        summary_tr=summary_tr,
        why_now_tr=why_now_tr,
        guidance_tr=list(guidance_tr or []),
        watch_for_tr=list(watch_for_tr or []),
        time_hint_tr=time_hint_tr,
        importance_label_tr=EVENT_KIND_LABEL_TR.get(event_kind, "Donem temasi"),
        copy_mode=_copy_mode(audience, event_kind),
        provenance=dict(provenance or {}),
    )


def _target_importance(
    point: str,
    target_houses: Sequence[int],
    natal_snapshot: Mapping[str, Any] | None,
) -> float:
    if point in TARGET_LOW_PRIORITY:
        return 0.24
    chart_ruler = _chart_ruler(natal_snapshot)
    if point in ANGLE_POINTS:
        return 0.95
    if point in LUMINARY_POINTS:
        return 0.92
    if chart_ruler and point == chart_ruler:
        return 0.88
    if point in {"North Node", "South Node"}:
        return 0.82
    if point == "Chiron":
        return 0.72
    if point in {"Mercury", "Venus", "Mars"}:
        return 0.67
    if point in {"Jupiter", "Saturn"}:
        return 0.70
    if point in {"Uranus", "Neptune", "Pluto"}:
        return 0.62
    if any(house in {1, 4, 7, 10} for house in target_houses):
        return 0.84
    return 0.56


def _duration_weight(duration_days: int, event_family: str) -> float:
    if event_family == "solar_year_theme":
        return 1.0
    if duration_days >= 300:
        return 0.98
    if duration_days >= 120:
        return 0.92
    if duration_days >= 45:
        return 0.74
    if duration_days >= 10:
        return 0.52
    return 0.36


def _lasting_change_score(
    *,
    source: str,
    target: str,
    target_houses: Sequence[int],
    event_family: str,
    structural_significance: float,
    repeat_pass_count: int,
) -> float:
    source_class = PLANET_CLASS.get(source, "")
    base = 0.24
    if source_class == "social":
        base += 0.20
    elif source_class == "outer":
        base += 0.34
    elif source_class in {"node", "healer", "luminary"}:
        base += 0.16
    if event_family in {"cycle_event", "house_ingress_event", "solar_year_theme"}:
        base += 0.22
    if target in CHAPTER_POINTS:
        base += 0.14
    if any(house in {1, 4, 7, 10} for house in target_houses):
        base += 0.12
    if repeat_pass_count > 1:
        base += 0.06
    base += max(0.0, structural_significance - 0.40) * 0.25
    return max(0.0, min(1.0, base))


def _angle_luminary_weight(
    target: str,
    target_houses: Sequence[int],
    natal_snapshot: Mapping[str, Any] | None,
    source: str,
) -> float:
    score = 0.0
    if target in ANGLE_POINTS:
        score += 1.0
    elif target in LUMINARY_POINTS:
        score += 0.92
    elif target == _chart_ruler(natal_snapshot):
        score += 0.82
    if any(house in {1, 4, 7, 10} for house in target_houses):
        score = max(score, 0.74)
    if source in {"Pluto", "Saturn", "North Node", "South Node"} and target in CHAPTER_POINTS:
        score = max(score, 0.92)
    return max(0.0, min(1.0, score))


def _solar_resonance(
    source_bodies: Sequence[str],
    target_points: Sequence[str],
    target_houses: Sequence[int],
    solar_year: Mapping[str, Any] | None,
) -> float:
    if not isinstance(solar_year, Mapping) or not solar_year:
        return 0.0
    score = 0.0
    dominant_houses = [int(value) for value in (solar_year.get("dominant_houses") or []) if isinstance(value, int)]
    solar_sun_house = _safe_int(solar_year.get("solar_sun_house"))
    year_ruler = str(solar_year.get("year_ruler") or "")
    if solar_sun_house and solar_sun_house in target_houses:
        score += 0.60
    if dominant_houses and any(house in dominant_houses for house in target_houses):
        score += 0.50
    if year_ruler and (year_ruler in source_bodies or year_ruler in target_points):
        score += 0.44
    if any(point in CHAPTER_POINTS for point in target_points):
        score += 0.12
    return max(0.0, min(1.0, score))


def _classify_event_kind(
    *,
    event_family: str,
    planet_class: str,
    primary_source: str,
    primary_target: str,
    target_houses: Sequence[int],
    duration_days: int,
    structural_significance: float,
    lasting_change_score: float,
    precision_signal: float,
    collective_interest_score: float,
) -> str:
    if event_family == "solar_year_theme":
        return "chapter" if lasting_change_score >= 0.74 else "season"
    if event_family == "cycle_event":
        if primary_source in {"Pluto", "Neptune"} and primary_target in CHAPTER_POINTS:
            return "transformation"
        return "chapter"
    if event_family == "house_ingress_event":
        if primary_source in {"Pluto", "Neptune", "Uranus"} and any(house in {1, 4, 7, 10} for house in target_houses):
            return "transformation"
        return "chapter"
    if event_family == "eclipse_trigger":
        if primary_target in CHAPTER_POINTS and lasting_change_score >= 0.70:
            return "chapter"
        return "emphasis"
    if event_family == "lunation_trigger":
        return "emphasis" if primary_target in CHAPTER_POINTS else "trigger"
    if event_family == "station_event":
        return "season" if primary_source in {"Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"} else "emphasis"
    if event_family == "global_sky_event":
        if collective_interest_score >= 0.78:
            return "season"
        return "emphasis"

    depth = 0.0
    if planet_class == "outer":
        depth += 0.36
    elif planet_class == "social":
        depth += 0.24
    elif planet_class in {"luminary", "node", "healer"}:
        depth += 0.18
    else:
        depth += 0.10
    if primary_target in CHAPTER_POINTS:
        depth += 0.18
    if any(house in {1, 4, 7, 10} for house in target_houses):
        depth += 0.12
    depth += max(0.0, structural_significance - 0.30)
    depth += lasting_change_score * 0.28
    depth += min(0.12, duration_days / 365.0 * 0.12)
    depth += precision_signal * 0.06
    if depth >= 0.88:
        return "transformation"
    if depth >= 0.66:
        return "chapter"
    if depth >= 0.50:
        return "season"
    if depth >= 0.32:
        return "emphasis"
    return "trigger"


def _importance_tier(score: float, event_kind: str, is_structural: bool) -> str:
    if score >= 0.82:
        return "critical"
    if score >= 0.64:
        return "high"
    if score >= 0.42:
        return "medium"
    tier = "low"
    if is_structural and event_kind in {"chapter", "transformation"}:
        tier = "medium"
    return tier


def _recognition_intensity(
    event_kind: str,
    importance_tier: str,
    audience: str,
    angle_weight: float,
    lasting_change: float,
) -> str:
    if audience == "solar":
        return "high" if importance_tier in {"high", "critical"} else "medium"
    if audience == "global":
        if importance_tier in {"high", "critical"}:
            return "medium"
        return "low"
    if event_kind == "transformation":
        return "high"
    if event_kind == "chapter":
        return "high" if angle_weight >= 0.80 or lasting_change >= 0.78 else "medium"
    if event_kind == "season":
        return "medium"
    if importance_tier in {"high", "critical"}:
        return "medium"
    return "low"


def _copy_mode(audience: str, event_kind: str) -> str:
    if audience == "global":
        return "global_sky"
    if audience == "solar":
        return "solar_year"
    if event_kind in {"trigger", "emphasis", "season", "chapter", "transformation"}:
        return event_kind
    return "emphasis"


def _time_scale(duration_days: int, event_family: str) -> str:
    if event_family == "solar_year_theme":
        return "annual"
    if duration_days >= 180:
        return "months"
    if duration_days >= 21:
        return "weeks"
    if duration_days >= 2:
        return "days"
    return "hours"


def _chart_ruler(natal_snapshot: Mapping[str, Any] | None) -> str:
    if not isinstance(natal_snapshot, Mapping):
        return ""
    sign = _angle_sign(natal_snapshot, "ASC")
    if not sign:
        house_cusps = natal_snapshot.get("house_cusps") if isinstance(natal_snapshot.get("house_cusps"), list) else []
        if house_cusps:
            sign = str(house_cusps[0].get("sign") or "")
    return ruler_of(sign)


def _angle_sign(snapshot: Mapping[str, Any], key: str) -> str:
    angles = snapshot.get("angles") if isinstance(snapshot.get("angles"), Mapping) else {}
    angle = angles.get(key) if isinstance(angles.get(key), Mapping) else {}
    sign = str(angle.get("sign") or "").strip()
    if sign:
        return sign
    lon = angle.get("lon")
    try:
        return get_zodiac_sign(float(lon)) if lon is not None else ""
    except (TypeError, ValueError):
        return ""


def _body_position(snapshot: Mapping[str, Any], body_name: str) -> Mapping[str, Any]:
    for body in (snapshot.get("bodies") or []):
        if isinstance(body, Mapping) and str(body.get("body") or "") == body_name:
            return body
    return {}


def _duration_days_from_bucket(bucket: str, start_at: str, end_at: str) -> int:
    delta = _days_between(start_at, end_at)
    if delta > 0:
        return delta
    if bucket == "long":
        return 120
    if bucket == "medium":
        return 21
    return 3


def _days_between(start_at: str, end_at: str) -> int:
    if not start_at or not end_at:
        return 0
    try:
        start = datetime.fromisoformat(start_at.replace("Z", "+00:00"))
        end = datetime.fromisoformat(end_at.replace("Z", "+00:00"))
        return max(0, int(round((end - start).total_seconds() / 86400)))
    except ValueError:
        try:
            start_d = date.fromisoformat(start_at[:10])
            end_d = date.fromisoformat(end_at[:10])
            return max(0, (end_d - start_d).days)
        except ValueError:
            return 0


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _parse_date(value: str) -> date:
    return date.fromisoformat(str(value)[:10])


def _window_start(value: str, *, days: int) -> str:
    return (_parse_date(value) - timedelta(days=days)).isoformat()


def _window_end(value: str, *, days: int) -> str:
    return (_parse_date(value) + timedelta(days=days)).isoformat()


def _hash_id(seed: str) -> str:
    return hashlib.sha1(seed.encode("utf-8")).hexdigest()


def _house_name(value: int) -> str:
    return HOUSE_LABEL_TR.get(int(value), f"{value}. ev")


def _houses_from_item(item: Mapping[str, Any]) -> List[int]:
    houses = item.get("houses") if isinstance(item.get("houses"), Mapping) else {}
    out = []
    for key in ("natal_point_house", "transit_in_natal_house"):
        house = _safe_int(houses.get(key))
        if house and house not in out:
            out.append(house)
    return out


def _target_houses_for_points(natal_snapshot: Mapping[str, Any] | None, points: Sequence[str]) -> List[int]:
    if not isinstance(natal_snapshot, Mapping):
        return []
    mapping: Dict[str, int] = {}
    for body in natal_snapshot.get("bodies") or []:
        if isinstance(body, Mapping):
            house = _safe_int(body.get("house"))
            name = str(body.get("body") or "")
            if house and name:
                mapping[name] = house
    mapping.update({"ASC": 1, "IC": 4, "DSC": 7, "MC": 10})
    out: List[int] = []
    for point in points:
        house = mapping.get(point)
        if house and house not in out:
            out.append(house)
    return out


def _aspect_title_tr(transit_body: str, natal_point: str) -> str:
    return f"{PLANET_TR.get(transit_body, transit_body)} {PLANET_TR.get(natal_point, natal_point)} hattini calistiriyor"


def _aspect_subtitle_tr(transit_body: str, natal_point: str, aspect: Any, houses: Any) -> str:
    house_text = ""
    if isinstance(houses, Mapping):
        target_house = _safe_int(houses.get("natal_point_house"))
        if target_house:
            house_text = f" Ozellikle {_house_name(target_house)} tarafinda hissedilir."
    return f"{PLANET_TR.get(transit_body, transit_body)} - {PLANET_TR.get(natal_point, natal_point)} {ASPECT_TR.get(str(aspect or ''), str(aspect or 'etkisi'))}.{house_text}"


def _aspect_summary_tr(transit_body: str, natal_point: str, aspect: Any, bucket: str, houses: Any) -> str:
    behavior = BEHAVIOR_MAP.get(transit_body, "bir temayi")
    target_house = ""
    if isinstance(houses, Mapping):
        house = _safe_int(houses.get("natal_point_house"))
        if house:
            target_house = f" Bu etki en cok {_house_name(house)} alaninda okunur."
    scale = "birkac gun" if bucket == "short" else ("birkac hafta" if bucket == "medium" else "uzun bir donem")
    return f"{scale} boyunca {behavior} temasi {PLANET_TR.get(natal_point, natal_point)} uzerinden daha gorunur olabilir.{target_house}"


def _aspect_why_now_tr(transit_body: str, natal_point: str, phase: Any, houses: Any, solar_year: Mapping[str, Any] | None) -> str:
    phase_text = {"exact": "zirveye", "exactish": "zirveye", "applying": "yaklasirken", "separating": "cozulerken"}.get(str(phase or "").lower(), "calisirken")
    resonance = ""
    if isinstance(solar_year, Mapping) and solar_year:
        dominant = [int(v) for v in (solar_year.get("dominant_houses") or []) if isinstance(v, int)]
        if isinstance(houses, Mapping):
            target_house = _safe_int(houses.get("natal_point_house"))
            if target_house and target_house in dominant:
                resonance = f" Bu alan ayni zamanda bu yilin ana sahnelerinden biri."
    return f"Etki su anda {phase_text}; bu da {PLANET_TR.get(natal_point, natal_point)} temasini daha fark edilir hale getiriyor.{resonance}"


def _aspect_guidance_tr(transit_body: str, natal_point: str, bucket: str) -> List[str]:
    if transit_body == "Mars":
        return ["Tepkiyi hiz degil netlikle yonet.", "Gerilimi dogrudan ama olculu ifade et."]
    if transit_body == "Saturn":
        return ["Kucuk ama saglam adim sec.", "Sorumlulugu sade bir planla tasarla."]
    if transit_body == "Pluto":
        return ["Kontrol yerine farkindaligi sec.", "Eski tepkiyi surdurmeden once sebebine bak."]
    if bucket == "short":
        return ["Kisa sureli etkide buyuk karar icin acele etme."]
    return ["Bu etkiyi davranis duzeyinde izle; hangi konu surekli geri donuyor ona bak."]


def _aspect_watch_for_tr(transit_body: str, natal_point: str) -> List[str]:
    if transit_body == "Neptune":
        return ["Belirsizligi netlik sanmak.", "Sinirlar bulanirken acele soz vermek."]
    if transit_body == "Uranus":
        return ["Bir anda kopmak.", "Ozellikle iliskilerde sabri kaybetmek."]
    if transit_body == "Saturn":
        return ["Kendine fazla sert davranmak.", "Yuk hissettikce geri cekilmek."]
    return [f"{PLANET_TR.get(natal_point, natal_point)} temasinda asiri tepki vermek."]


def _aspect_time_hint_tr(start_at: str, peak: str, end_at: str, bucket: str) -> str:
    if peak:
        return f"Etki {peak[:10]} civarinda daha belirgin. Pencere {start_at[:10] if start_at else ''} - {end_at[:10] if end_at else ''}."
    if bucket == "short":
        return "Bu etki kisa bir tetik gibi calisir; hizli gelir, hizli dagilir."
    if bucket == "long":
        return "Bu etki kademeli calisir; bir anda degil zamana yayilarak gorunur olur."
    return _time_hint_from_dates(start_at, end_at)


def _cycle_subtype(transit: str, natal: str, aspect: str) -> str:
    if transit == "Saturn" and natal == "Saturn" and aspect == "conjunction":
        return "saturn_return"
    if transit == "Saturn" and natal == "Saturn" and aspect == "square":
        return "saturn_square_saturn"
    if transit == "Saturn" and natal == "Saturn" and aspect == "opposition":
        return "saturn_opposition_saturn"
    if transit == "Jupiter" and natal == "Jupiter" and aspect == "conjunction":
        return "jupiter_return"
    if transit == "North Node" and natal == "North Node" and aspect == "conjunction":
        return "nodal_return"
    if transit == "North Node" and natal == "North Node" and aspect == "opposition":
        return "nodal_opposition"
    if transit == "Chiron" and natal == "Chiron" and aspect == "conjunction":
        return "chiron_return"
    if transit in {"Saturn", "Uranus", "Neptune", "Pluto"} and natal in CHAPTER_POINTS and aspect in {"conjunction", "square", "opposition"}:
        return f"{transit.lower()}_{aspect}_{natal.lower()}_milestone"
    return ""


def _cycle_structural_significance(subtype: str, transit: str, natal: str) -> float:
    if subtype in {"saturn_return", "saturn_square_saturn", "saturn_opposition_saturn"}:
        return 0.96
    if subtype in {"nodal_return", "nodal_opposition"}:
        return 0.88
    if subtype in {"jupiter_return", "chiron_return"}:
        return 0.82
    if transit == "Pluto" and natal in CHAPTER_POINTS:
        return 0.96
    if transit in {"Neptune", "Uranus"} and natal in CHAPTER_POINTS:
        return 0.88
    return 0.78


def _cycle_title_tr(subtype: str, transit: str, natal: str) -> str:
    mapping = {
        "saturn_return": "Saturn donusu",
        "saturn_square_saturn": "Saturn kare Saturn",
        "saturn_opposition_saturn": "Saturn karsiti Saturn",
        "jupiter_return": "Jupiter donusu",
        "nodal_return": "Ay dugumu donusu",
        "nodal_opposition": "Ay dugumu karsitligi",
        "chiron_return": "Kiron donusu",
    }
    return mapping.get(subtype, f"{PLANET_TR.get(transit, transit)} {PLANET_TR.get(natal, natal)} esigi")


def _cycle_subtitle_tr(subtype: str, transit: str, natal: str) -> str:
    if subtype.startswith("saturn"):
        return "Bu sadece bir gunluk transit degil; daha buyuk bir olgunlasma esigi."
    if subtype.startswith("jupiter"):
        return "Hayatin yonunu genisletmek isteyen bir donem aciliyor."
    if subtype.startswith("nodal"):
        return "Yon, baglanti ve tekrar eden kader basliklari belirginlesiyor."
    if subtype.startswith("chiron"):
        return "Eski hassasiyet yeni bir olgunlukla gorunur oluyor."
    return f"{PLANET_TR.get(transit, transit)} {PLANET_TR.get(natal, natal)} hattinda yapisal bir esik calisiyor."


def _cycle_summary_tr(subtype: str, transit: str, natal: str) -> str:
    if subtype == "saturn_return":
        return "Hayatini ayakta tutmayan yapilari elemek ve kalici olanlari guclendirmek isteyen bir donemdesin."
    if subtype == "jupiter_return":
        return "Buyume, imkan ve ufuk genislemesi bu donemde daha cesur kararlar istiyor."
    if subtype in {"nodal_return", "nodal_opposition"}:
        return "Tekrar eden iliski ve yon kaliplari kendini daha net gosteriyor; yol duzeltmesi zamani."
    if subtype == "chiron_return":
        return "Eski yaraya ayni gozle bakamiyorsun; bu kez mesele iyilesme ve anlam kurma tarafina kayiyor."
    return f"{PLANET_TR.get(transit, transit)} uzun bir donemde {PLANET_TR.get(natal, natal)} hattinda kalici etki biraktigi icin bunu chapter gibi okumak gerekir."


def _cycle_why_now_tr(subtype: str, raw: Mapping[str, Any]) -> str:
    peaks = raw.get("timebox") if isinstance(raw.get("timebox"), Mapping) else {}
    peak_dates = [str(entry.get("t") or "")[:10] for entry in (peaks.get("peaks") or []) if str(entry.get("t") or "").strip()]
    if peak_dates:
        return f"Bu chapter {', '.join(peak_dates[:3])} gibi gecis noktalariyla tekrar tekrar belirginlesebilir."
    return "Bu etki tek bir zirveyle bitmez; geri donup ayni temayi baska bir derinlikle tekrar acabilir."


def _cycle_guidance_tr(subtype: str, transit: str, natal: str) -> List[str]:
    if subtype.startswith("saturn"):
        return ["Yuku azalt, omurgayi guclendir.", "Kisa vadeli rahatlik yerine uzun vadeli saglamligi sec."]
    if subtype.startswith("jupiter"):
        return ["Buyumeyi dagitma; tek bir hat sec.", "Firsati planla birlestir."]
    if subtype.startswith("nodal"):
        return ["Tekrar eden deseni fark et.", "Ayni iliski refleksine otomatik donme."]
    return [f"{PLANET_TR.get(natal, natal)} alaninda eski kalibi degil yeni duzeni besle."]


def _cycle_watch_for_tr(subtype: str, transit: str) -> List[str]:
    if subtype.startswith("saturn"):
        return ["Yoruldukca her seyi kisitlamak.", "Sorumlulugu ceza gibi okumak."]
    if subtype.startswith("jupiter"):
        return ["Asiri buyutmek.", "Ayni anda fazla kapidan girmek."]
    if subtype.startswith("nodal"):
        return ["Eski kalibi kader diye tekrar etmek."]
    return [f"{PLANET_TR.get(transit, transit)} temasini sadece kriz diye okumak."]


def _phase_from_now(raw: Mapping[str, Any]) -> str:
    peaks = (raw.get("timebox") or {}).get("peaks") or []
    if peaks:
        return "active"
    return "active"


def _house_ingress_structural_significance(body: str, house: int) -> float:
    score = 0.80
    if body in {"Pluto", "Neptune"}:
        score += 0.10
    if house in {1, 4, 7, 10}:
        score += 0.08
    if body in {"North Node", "South Node"}:
        score += 0.04
    return min(1.0, score)


def _duration_for_ingress(body: str) -> int:
    if body == "Jupiter":
        return 365
    if body == "Saturn":
        return 900
    if body in {"Uranus", "Neptune", "Pluto"}:
        return 1600
    return 240


def _house_ingress_title_tr(body: str, house: int) -> str:
    return f"{PLANET_TR.get(body, body)} {_house_name(house)} chapterini aciyor"


def _house_ingress_summary_tr(body: str, house: int, phase: str) -> str:
    phase_text = {
        "initial_entry": "ilk kez aciliyor",
        "re_entry": "yeniden bu alana donuyor",
        "final_settlement": "bu alana daha kalici sekilde yerlesiyor",
    }.get(phase, "bu alana geciyor")
    return f"{PLANET_TR.get(body, body)} {_house_name(house)} temasini kisa bir vurgu gibi degil, daha yapisal bir donem olarak calistirir; su anda bu hat {phase_text}."


def _house_ingress_why_now_tr(body: str, house: int, phase: str, solar_year: Mapping[str, Any] | None) -> str:
    resonance = ""
    if isinstance(solar_year, Mapping) and solar_year:
        dominant = [int(v) for v in (solar_year.get("dominant_houses") or []) if isinstance(v, int)]
        if house in dominant:
            resonance = " Bu alan ayni zamanda yilin ana sahnesiyle de hizlaniyor."
    return f"{PLANET_TR.get(body, body)} su anda {_house_name(house)} eksenini one cikariyor.{resonance}"


def _house_ingress_guidance_tr(body: str, house: int) -> List[str]:
    return [
        f"{_house_name(house)} tarafinda yeni duzen kurmak icin takvim ac.",
        "Bu gecisi bir gunluk motivasyon gibi degil, yapi degisikligi gibi ele al.",
    ]


def _house_ingress_watch_for_tr(body: str) -> List[str]:
    if body == "Saturn":
        return ["Yuku artiyor diye kapanmak.", "Sadece kisit tarafini gormek."]
    if body == "Jupiter":
        return ["Buyumeyi plansiz dagitmak."]
    if body == "Pluto":
        return ["Her seyi kontrol ederek degismeye calismak."]
    return [f"{PLANET_TR.get(body, body)} gecisini sadece ani bir his gibi okumak."]


def _generic_title_tr(event_family: str, source: str, target: str, houses: Sequence[int]) -> str:
    if event_family == "global_sky_event":
        return f"Gokyuzunde {PLANET_TR.get(source, source)} vurgusu"
    if event_family == "station_event":
        return f"{PLANET_TR.get(source, source)} yon degistiriyor"
    if event_family == "lunation_trigger":
        return "Ay fazi yeni bir vurgu aciyor"
    if event_family == "eclipse_trigger":
        return "Tutulma hatti hizlaniyor"
    if houses:
        return f"{PLANET_TR.get(source, source)} {_house_name(houses[0])} alanini calistiriyor"
    return f"{PLANET_TR.get(source, source)} etkisi"


def _generic_summary_tr(event_family: str, source: str, target: str, houses: Sequence[int], event_kind: str) -> str:
    if event_family == "global_sky_event":
        return f"Gokyuzu su anda {BEHAVIOR_MAP.get(source, 'belirli bir temayi')} daha kolektif bicimde gorunur kiliyor."
    if event_family == "station_event":
        return f"{PLANET_TR.get(source, source)} hiz kesip yon degistirdigi icin tempo ve karar ritmi de ayar isteyebilir."
    if event_family == "lunation_trigger":
        return "Bu lunasyon kisa sureli ama dikkat cekici bir vurgu olarak calisir."
    if event_family == "eclipse_trigger":
        return "Bu tutulma tetigi her haritada buyuk bir chapter degildir; ancak dogru noktaya dusunce esiği belirginlestirir."
    scale = EVENT_KIND_LABEL_TR.get(event_kind, "Donem temasi")
    return f"{scale} olarak okunan bu etki {PLANET_TR.get(source, source)} temasini daha belirgin hale getirir."


def _generic_why_now_tr(event_family: str, source: str, target: str, houses: Sequence[int], solar_year: Mapping[str, Any] | None) -> str:
    resonance = ""
    if isinstance(solar_year, Mapping) and solar_year:
        dominant = [int(v) for v in (solar_year.get("dominant_houses") or []) if isinstance(v, int)]
        if any(house in dominant for house in houses):
            resonance = " Ayrica bu konu yilin ana sahnesiyle de rezonansa giriyor."
    if houses:
        return f"Su anda {_house_name(houses[0])} alaninda acilan vurgu daha kolay fark ediliyor.{resonance}"
    return f"Su anda {PLANET_TR.get(source, source)} temasi daha belirgin.{resonance}"


def _time_hint_from_dates(start_at: str, end_at: str) -> str:
    if start_at and end_at:
        return f"Pencere {start_at[:10]} - {end_at[:10]} arasinda."
    if start_at:
        return f"Etkinin acildigi tarih {start_at[:10]}."
    return ""


def _positions_for_bodies(
    *,
    bodies: Sequence[str],
    when_iso: str,
    place: str,
    hour: str | None = None,
    location: LocationData | None = None,
) -> List[Dict[str, Any]]:
    when_date = str(when_iso)[:10]
    when_time = hour or ("12:00" if len(str(when_iso)) <= 10 else str(when_iso)[11:16] or "12:00")
    resolved_location = location or resolve_location(place)
    _local_dt, utc_dt = _parse_local_datetime(
        when_date,
        when_time,
        resolved_location.timezone,
    )
    jd = julian_day(utc_dt)
    cusps, angles_raw = _calc_houses(
        jd,
        resolved_location.latitude,
        resolved_location.longitude,
        house_system="placidus",
    )
    cusp_sequence = [0.0, *cusps]
    return _calc_bodies(jd, bodies, cusp_sequence, angles_raw)


def _parse_local_datetime(date_value: str, time_value: str, timezone_name: str) -> Tuple[datetime, datetime]:
    from app.utils.timezones import parse_birth_datetime_components

    return parse_birth_datetime_components(date_value, time_value, timezone_name)


def _activated_houses_for_positions(
    *,
    natal_snapshot: Mapping[str, Any],
    positions: Sequence[Mapping[str, Any]],
) -> List[int]:
    cusps = [cusp.get("lon") for cusp in (natal_snapshot.get("house_cusps") or []) if cusp.get("lon") is not None]
    if len(cusps) < 12:
        return []
    houses: List[int] = []
    for position in positions:
        lon = position.get("lon")
        if lon is None:
            continue
        house = _house_from_cusps(float(lon), cusps)
        if house not in houses:
            houses.append(house)
    return houses


def _closest_natal_contacts(
    *,
    natal_snapshot: Mapping[str, Any],
    positions: Sequence[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    natal_points: List[Tuple[str, float]] = []
    for body in natal_snapshot.get("bodies") or []:
        if isinstance(body, Mapping) and body.get("lon") is not None:
            natal_points.append((str(body.get("body") or ""), float(body.get("lon"))))
    for angle_name, house in (("ASC", 1), ("IC", 4), ("DSC", 7), ("MC", 10)):
        angle = ((natal_snapshot.get("angles") or {}).get(angle_name) if isinstance(natal_snapshot.get("angles"), Mapping) else {})
        if isinstance(angle, Mapping) and angle.get("lon") is not None:
            natal_points.append((angle_name, float(angle.get("lon"))))

    hits: List[Dict[str, Any]] = []
    for position in positions:
        body = str(position.get("body") or "")
        lon = position.get("lon")
        if lon is None:
            continue
        for point, natal_lon in natal_points:
            for aspect_name, angle in ASPECT_ANGLES.items():
                diff = abs(_min_angle_diff(float(lon) - natal_lon) - angle)
                orb_limit = 2.5 if point in CHAPTER_POINTS else 2.0
                if diff > orb_limit:
                    continue
                hits.append(
                    {
                        "body": body,
                        "point": point,
                        "aspect": aspect_name,
                        "orb_deg": round(diff, 3),
                        "precision_signal": round(max(0.2, 1.0 - diff / max(orb_limit, 0.1)), 3),
                        "target_importance": round(_target_importance(point, _target_houses_for_points(natal_snapshot, [point]), natal_snapshot), 3),
                    }
                )
    hits.sort(key=lambda item: (float(item.get("orb_deg") or 9.9), -float(item.get("target_importance") or 0.0), str(item.get("point") or "")))
    return hits


def _bridge_title(source_bodies: Sequence[str], target_points: Sequence[str], houses: Sequence[int]) -> str:
    if target_points:
        return f"Gokyuzundeki olay sende {PLANET_TR.get(target_points[0], target_points[0])} hattina dusuyor"
    if houses:
        return f"Gokyuzundeki olay sende {_house_name(houses[0])} alanini calistiriyor"
    if source_bodies:
        return f"Gokyuzundeki {PLANET_TR.get(source_bodies[0], source_bodies[0])} vurgusu sende de hissedilebilir"
    return "Bu olay haritanda da bir tema aciyor"


def _bridge_subtitle(target_points: Sequence[str], houses: Sequence[int]) -> str:
    if target_points:
        return "Kolektif olay dogrudan kisisel bir hedefe temas ediyor."
    if houses:
        return f"Haritanda daha cok {_house_name(houses[0])} tarafinda calisiyor."
    return "Bu etki sende daha zayif ama yine de fark edilir olabilir."


def _bridge_summary(source_bodies: Sequence[str], target_points: Sequence[str], houses: Sequence[int]) -> str:
    if target_points:
        return f"Kolektif gokyuzu olayi sende {PLANET_TR.get(target_points[0], target_points[0])} temasini daha belirginlestiriyor."
    if houses:
        return f"Bu olay sende {_house_name(houses[0])} alaninda kisa bir vurgu ya da yon duzeltmesi gibi hissedilebilir."
    if source_bodies:
        return f"{PLANET_TR.get(source_bodies[0], source_bodies[0])} vurgusu sende de dikkat cekebilir; ancak bu etki daha cok arka planda calisir."
    return "Bu olay haritanda hafif bir yanki uretiyor."


def _bridge_why_now(natal_contacts: Sequence[Mapping[str, Any]], houses: Sequence[int], solar_year: Mapping[str, Any] | None) -> str:
    if natal_contacts:
        first = natal_contacts[0]
        text = f"Sebep, olay aninda {PLANET_TR.get(str(first.get('body') or ''), str(first.get('body') or ''))} ile {PLANET_TR.get(str(first.get('point') or ''), str(first.get('point') or ''))} arasinda belirgin bir bag kurulmasi."
    elif houses:
        text = f"Sebep, olay aninda tema daha cok {_house_name(houses[0])} tarafina dusuyor."
    else:
        text = "Sebep, olay aninda haritanda hafif de olsa bir temas olusmasi."
    if isinstance(solar_year, Mapping) and solar_year:
        dominant = [int(v) for v in (solar_year.get("dominant_houses") or []) if isinstance(v, int)]
        if any(house in dominant for house in houses):
            text += " Bu konu ayni zamanda bu yilin ana zeminlerinden biri."
    return text


def _bridge_guidance(target_points: Sequence[str], houses: Sequence[int]) -> List[str]:
    if target_points:
        return [f"{PLANET_TR.get(target_points[0], target_points[0])} temasinda verdigin tepkiyi izle.", "Kolektif gundemi kisisel kader gibi okuma; temayi gozlemle."]
    if houses:
        return [f"{_house_name(houses[0])} tarafinda tempoyu bir tik dusur.", "Gundemin seni nereye cektigini not al."]
    return ["Olayi kendi hikayene zorla yapistirma; sadece yankisini izle."]


def _bridge_watch_for(target_points: Sequence[str]) -> List[str]:
    if target_points and target_points[0] in CHAPTER_POINTS:
        return ["Kolektif olayi tek basina kader karari gibi okumak."]
    return ["Gokyuzu gundemini gereksiz buyutmek."]


def _global_phase_events(start_dt: date, end_dt: date, transit_place: str) -> List[AstroEventV2]:
    from app.transit.calendar_builder import _scan_phase_markers

    markers = _scan_phase_markers(start=start_dt, end=end_dt, transit_place=transit_place, options=None)
    events: List[AstroEventV2] = []
    for marker in markers:
        body = _body_from_phase_id(marker.event_id)
        phase_kind = str(marker.phase_kind or "")
        family = "station_event" if phase_kind in {"retro", "station"} else "global_sky_event"
        subtype = _phase_subtype_from_marker(marker.event_id, marker.label or "", phase_kind)
        title = _global_title_from_marker(body, subtype, marker.label)
        summary = _global_summary_from_marker(body, subtype)
        why_now = _global_why_now_from_marker(body, subtype)
        guidance = _global_guidance_from_marker(subtype)
        watch_for = _global_watch_for_from_marker(subtype, body)
        collective = _collective_interest_for_phase(subtype, body)
        events.append(
            _build_event(
                event_id=marker.event_id,
                event_family=family,
                event_subtype=subtype,
                audience="global",
                source_bodies=[body] if body else [],
                target_points=[],
                target_houses=[],
                start_at=marker.date,
                exact_at=[marker.date],
                end_at=marker.date,
                current_phase=phase_kind or "active",
                precision_signal=0.72 if subtype.startswith("station") else 0.60,
                duration_days=1 if subtype.startswith("station") else 7,
                repeat_pass_count=1,
                is_structural=body in {"Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"},
                structural_significance=0.64 if body in {"Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"} else 0.46,
                chapter_opening=phase_kind == "ingress" and body in {"Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"},
                collective_interest_score=collective,
                title_tr=title,
                subtitle_tr=marker.label or "",
                summary_tr=summary,
                why_now_tr=why_now,
                guidance_tr=guidance,
                watch_for_tr=watch_for,
                time_hint_tr=f"Olay tarihi {marker.date}.",
                provenance={"detector": "global_phase.v1", "phase_kind": phase_kind},
            )
        )
    return events


def _detect_lunations(start_dt: date, end_dt: date, transit_place: str) -> List[AstroEventV2]:
    location = fetch_location(transit_place)
    candidates: List[Tuple[datetime, str, float, str]] = []
    current = datetime.combine(start_dt - timedelta(days=2), datetime.min.time())
    end_scan = datetime.combine(end_dt + timedelta(days=2), datetime.min.time())
    samples: List[Tuple[datetime, float, float, float, float]] = []
    while current <= end_scan:
        jd = julian_day(current)
        cusps, angles_raw = _calc_houses(jd, location.latitude, location.longitude, house_system="placidus")
        cusp_sequence = [0.0, *cusps]
        bodies = _calc_bodies(jd, ["Sun", "Moon", "North Node"], cusp_sequence, angles_raw)
        sun = next((entry for entry in bodies if entry.get("body") == "Sun"), {})
        moon = next((entry for entry in bodies if entry.get("body") == "Moon"), {})
        node = next((entry for entry in bodies if entry.get("body") == "North Node"), {})
        if sun.get("lon") is None or moon.get("lon") is None:
            current += timedelta(hours=6)
            continue
        phase = _min_angle_diff(float(moon.get("lon")) - float(sun.get("lon")))
        node_delta = _min_angle_diff(float(moon.get("lon")) - float(node.get("lon") or 0.0))
        samples.append((current, phase, node_delta, float(sun.get("lon")), float(moon.get("lon"))))
        current += timedelta(hours=6)

    def _append_if_min(kind: str, index: int, threshold: float) -> None:
        center = samples[index]
        prev_phase = samples[index - 1][1]
        next_phase = samples[index + 1][1]
        phase = center[1]
        if phase <= threshold and phase <= prev_phase and phase <= next_phase:
            when = center[0]
            node_delta = center[2]
            subtype = "solar_eclipse" if kind == "new_moon" and node_delta <= 18 else ("lunar_eclipse" if kind == "full_moon" and abs(phase - 180.0) <= 14 and node_delta <= 18 else kind)
            sun_sign = get_zodiac_sign(center[3])
            candidates.append((when, kind, node_delta, sun_sign))

    for index in range(1, len(samples) - 1):
        phase = samples[index][1]
        if phase <= 12:
            _append_if_min("new_moon", index, 12)
        if abs(phase - 180.0) <= 12:
            before = abs(samples[index - 1][1] - 180.0)
            after = abs(samples[index + 1][1] - 180.0)
            center = abs(phase - 180.0)
            if center <= before and center <= after:
                when = samples[index][0]
                node_delta = samples[index][2]
                sun_sign = get_zodiac_sign(samples[index][3])
                subtype = "lunar_eclipse" if node_delta <= 18 else "full_moon"
                candidates.append((when, subtype, node_delta, sun_sign))

    deduped: List[Tuple[datetime, str, float, str]] = []
    for item in sorted(candidates, key=lambda value: value[0]):
        if deduped and abs((item[0] - deduped[-1][0]).total_seconds()) < 4 * 86400 and item[1] == deduped[-1][1]:
            continue
        deduped.append(item)

    out: List[AstroEventV2] = []
    for when, subtype, node_delta, sign in deduped:
        if when.date() < start_dt or when.date() > end_dt:
            continue
        is_eclipse = subtype in {"solar_eclipse", "lunar_eclipse"}
        family = "eclipse_trigger" if is_eclipse else "lunation_trigger"
        title = _lunation_title_tr(subtype, sign)
        summary = _lunation_summary_tr(subtype, sign)
        why_now = _lunation_why_now_tr(subtype, node_delta)
        out.append(
            _build_event(
                event_id=_hash_id(f"lunation|{subtype}|{when.isoformat()}|{sign}"),
                event_family=family,
                event_subtype=subtype,
                audience="global",
                source_bodies=["Sun", "Moon"],
                target_points=[],
                target_houses=[],
                start_at=when.date().isoformat(),
                exact_at=[when.isoformat()],
                end_at=(when.date() + timedelta(days=(14 if is_eclipse else 7))).isoformat(),
                current_phase="exact",
                precision_signal=0.82 if is_eclipse else 0.74,
                duration_days=14 if is_eclipse else 7,
                repeat_pass_count=1,
                is_structural=is_eclipse,
                structural_significance=0.78 if is_eclipse else 0.44,
                chapter_opening=is_eclipse,
                collective_interest_score=0.90 if is_eclipse else 0.70,
                title_tr=title,
                subtitle_tr=f"{SIGN_TR.get(sign, sign)} ekseninde {'tutulma' if is_eclipse else 'lunasyon'}",
                summary_tr=summary,
                why_now_tr=why_now,
                guidance_tr=["Duygusal hizlanmada karar yerine gozlem sec.", "Yeni niyet ile somut ritmi birbirine bagla."],
                watch_for_tr=["Her lunasyonu buyuk kader karari gibi okumak." if not is_eclipse else "Tutulmayi panik nedeni yapmak."],
                time_hint_tr=f"Etki {when.date().isoformat()} civarinda belirgin.",
                provenance={"detector": "lunation.v1", "node_delta": round(node_delta, 3), "sign": sign},
            )
        )
    return out


def _detect_global_exact_aspects(start_dt: date, end_dt: date, transit_place: str) -> List[AstroEventV2]:
    events: List[AstroEventV2] = []
    location = fetch_location(transit_place)
    seen: set[str] = set()
    current = start_dt
    while current <= end_dt:
        jd = julian_day(datetime.combine(current, datetime.min.time()) + timedelta(hours=12))
        cusps, angles_raw = _calc_houses(jd, location.latitude, location.longitude, house_system="placidus")
        cusp_sequence = [0.0, *cusps]
        bodies = _calc_bodies(jd, SLOW_GLOBAL_ASPECT_BODIES, cusp_sequence, angles_raw)
        positions = {str(body.get("body") or ""): float(body.get("lon")) for body in bodies if body.get("lon") is not None}
        for idx, left in enumerate(SLOW_GLOBAL_ASPECT_BODIES):
            for right in SLOW_GLOBAL_ASPECT_BODIES[idx + 1 :]:
                if left not in positions or right not in positions:
                    continue
                for aspect_name, angle in {"conjunction": 0, "opposition": 180, "square": 90}.items():
                    orb = abs(_min_angle_diff(positions[left] - positions[right]) - angle)
                    if orb > 0.20:
                        continue
                    if left not in {"Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"} and right not in {"Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"}:
                        continue
                    key = f"{current.isoformat()}|{left}|{aspect_name}|{right}"
                    if key in seen:
                        continue
                    seen.add(key)
                    title = f"{PLANET_TR.get(left, left)} {ASPECT_TR.get(aspect_name, aspect_name)} {PLANET_TR.get(right, right)}"
                    events.append(
                        _build_event(
                            event_id=_hash_id(f"sky_aspect|{key}"),
                            event_family="global_sky_event",
                            event_subtype=f"exact_{aspect_name}",
                            audience="global",
                            source_bodies=[left, right],
                            target_points=[],
                            target_houses=[],
                            start_at=current.isoformat(),
                            exact_at=[current.isoformat()],
                            end_at=current.isoformat(),
                            current_phase="exact",
                            precision_signal=max(0.55, 1.0 - orb / 0.20),
                            duration_days=1,
                            repeat_pass_count=1,
                            is_structural=left in {"Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"} or right in {"Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"},
                            structural_significance=0.56,
                            chapter_opening=False,
                            collective_interest_score=0.66 if "Saturn" in {left, right} or "Jupiter" in {left, right} else 0.54,
                            title_tr=title,
                            subtitle_tr="Gokyuzunde kulturel olarak daha fark edilir bir tam temas",
                            summary_tr=f"Kolektif atmosferde {PLANET_TR.get(left, left)} ile {PLANET_TR.get(right, right)} arasindaki tema daha net duyulabilir.",
                            why_now_tr="Aspekt bugun tamlasmaya cok yakin oldugu icin toplu ritimde daha gorunur olabilir.",
                            guidance_tr=["Kolektif havayi dinle ama kendi kararini veriyle kur."],
                            watch_for_tr=["Kolektif ruh halini kendi ic sesin sanmak."],
                            time_hint_tr=f"Tarih {current.isoformat()} civari.",
                            provenance={"detector": "global_exact_aspect.v1", "orb_deg": round(orb, 3)},
                        )
                    )
        current += timedelta(days=1)
    return events


def _body_from_phase_id(event_id: str) -> str:
    parts = str(event_id or "").split(".")
    if len(parts) >= 3:
        return parts[2]
    return ""


def _phase_subtype_from_marker(event_id: str, label: str, phase_kind: str) -> str:
    text = str(label or "").lower()
    if phase_kind == "ingress":
        return "sign_ingress"
    if phase_kind == "station":
        return "station_retrograde" if "retro" in text else "station_direct"
    if phase_kind == "retro":
        return "retrograde_start" if "basliyor" in text else "retrograde_end"
    return phase_kind or "phase_shift"


def _global_title_from_marker(body: str, subtype: str, label: str) -> str:
    if subtype == "sign_ingress":
        return str(label or f"{PLANET_TR.get(body, body)} sign degistiriyor")
    if subtype.startswith("station"):
        return f"{PLANET_TR.get(body, body)} duragan"
    if subtype.startswith("retrograde"):
        return str(label or f"{PLANET_TR.get(body, body)} retro dongusu")
    return str(label or "Gokyuzunde yon degisimi")


def _global_summary_from_marker(body: str, subtype: str) -> str:
    if subtype == "sign_ingress":
        return f"{PLANET_TR.get(body, body)} yeni bir burca gectigi icin kolektif ton da yon degistiriyor."
    if subtype in {"station_direct", "station_retrograde"}:
        return f"{PLANET_TR.get(body, body)} hiz kesip yon degistirdigi icin ayni konuda netlik ve belirsizlik birlikte artabilir."
    if subtype == "retrograde_start":
        return f"{PLANET_TR.get(body, body)} retroya girdigi icin bu gezegenin temsil ettigi tema tekrar, duzeltme ve gozden gecirme ister."
    if subtype == "retrograde_end":
        return f"{PLANET_TR.get(body, body)} retrosu biterken konu yavas yavas yeniden akisa doner."
    return "Gokyuzu ritmi kolektif olarak ayar istiyor."


def _global_why_now_from_marker(body: str, subtype: str) -> str:
    if subtype == "sign_ingress":
        return "Burc degisimi ton degisimini tek bir gunun haberi olmaktan cikarip yeni bir atmosfer gibi hissettirir."
    if subtype.startswith("station"):
        return "Station gunlerinde hiz azalir ama farkindalik artar; o yuzden etki daha belirgin hissedilir."
    if subtype.startswith("retrograde"):
        return "Retro donusleri ayni basliga geri bakma ihtiyaci yarattigi icin kolektif ilgi daha hizli toplanir."
    return "Kolektif hava su anda bu basligi daha guclu duyuruyor."


def _global_guidance_from_marker(subtype: str) -> List[str]:
    if subtype.startswith("station"):
        return ["Ritmi zorlamadan ayar yap.", "Kesin karari hemen verme."]
    if subtype.startswith("retrograde"):
        return ["Tekrar ve duzeltmeyi verimsizlik sanma.", "Eksik baglamı tamamla."]
    return ["Kolektif akisi izle ama kisisel karari yavas kur."]


def _global_watch_for_from_marker(subtype: str, body: str) -> List[str]:
    if body == "Mercury" and subtype.startswith("retrograde"):
        return ["Iletisimde acele, varsayim ve eksik detay."]
    if subtype == "sign_ingress":
        return ["Yeni tonu hemen kalici sonuc sanmak."]
    return ["Kolektif gerginligi bireysel gercekle karistirmak."]


def _collective_interest_for_phase(subtype: str, body: str) -> float:
    if subtype.startswith("station"):
        return 0.88 if body in {"Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"} else 0.78
    if subtype.startswith("retrograde"):
        return 0.84 if body in {"Mercury", "Venus", "Mars"} else 0.72
    if subtype == "sign_ingress":
        return 0.74 if body in {"Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"} else 0.56
    return 0.52


def _lunation_title_tr(subtype: str, sign: str) -> str:
    if subtype == "new_moon":
        return f"{SIGN_TR.get(sign, sign)} yeniayi"
    if subtype == "full_moon":
        return f"{SIGN_TR.get(sign, sign)} dolunayi"
    if subtype == "solar_eclipse":
        return f"{SIGN_TR.get(sign, sign)} gunes tutulmasi"
    return f"{SIGN_TR.get(sign, sign)} ay tutulmasi"


def _lunation_summary_tr(subtype: str, sign: str) -> str:
    if subtype == "new_moon":
        return f"Yeniay {SIGN_TR.get(sign, sign)} tonunda yeni niyetleri daha kolay gorunur kilar; yine de etki once tohum gibidir."
    if subtype == "full_moon":
        return f"Dolunay {SIGN_TR.get(sign, sign)} tonunda duygusal ve iliskisel gorunurlugu artirabilir."
    if subtype == "solar_eclipse":
        return "Bu gunes tutulmasi kolektif olarak daha buyuk bir baslik acabilir; ama her haritada ayni kuvvette calismaz."
    return "Bu ay tutulmasi duygusal gozden gecirme ve kapanis hissini daha kuvvetli getirebilir."


def _lunation_why_now_tr(subtype: str, node_delta: float) -> str:
    if subtype in {"solar_eclipse", "lunar_eclipse"}:
        return f"Lunasyon dugum eksenine yeterince yaklastigi icin tutulma niteligine geciyor. Dugum mesafesi yaklasik {round(node_delta, 1)} derece."
    return "Ay-Sun hizalanmasi bu tarihte yeni bir vurgu olusturuyor."


def _phase_kind_from_house_event(pass_index: int, repeat_pass_count: int) -> str:
    if repeat_pass_count <= 1:
        return "final_settlement"
    if pass_index == 1:
        return "initial_entry"
    if pass_index == repeat_pass_count:
        return "final_settlement"
    return "re_entry"


def _next_house_change(
    pass_map: Mapping[Tuple[str, int], List[Mapping[str, Any]]],
    body: str,
    house: int,
    start_at: str,
    fallback: str,
) -> str:
    later_entries: List[str] = []
    for (entry_body, entry_house), rows in pass_map.items():
        if entry_body != body:
            continue
        for row in rows:
            entry_time = str(row.get("entry") or "")
            if entry_time > start_at:
                later_entries.append(entry_time)
    if later_entries:
        return sorted(later_entries)[0]
    return fallback


def _solar_return_datetime(
    *,
    natal_sun_lon: float,
    birth_date: str,
    year: int,
    place: str,
    location: LocationData | None = None,
) -> datetime | None:
    birth_dt = _parse_date(birth_date)
    seed_date = date(year, birth_dt.month, min(birth_dt.day, 28 if birth_dt.month == 2 else birth_dt.day))
    start = datetime.combine(seed_date - timedelta(days=2), datetime.min.time())
    end = datetime.combine(seed_date + timedelta(days=2), datetime.min.time())
    best_time: Optional[datetime] = None
    best_diff = 999.0
    current = start
    resolved_location = location or resolve_location(place)
    while current <= end:
        _local_dt, utc_dt = _parse_local_datetime(
            current.date().isoformat(),
            current.strftime("%H:%M"),
            resolved_location.timezone,
        )
        jd = julian_day(utc_dt)
        cusps, angles_raw = _calc_houses(
            jd,
            resolved_location.latitude,
            resolved_location.longitude,
            house_system="placidus",
        )
        cusp_sequence = [0.0, *cusps]
        sun = next((entry for entry in _calc_bodies(jd, ["Sun"], cusp_sequence, angles_raw) if entry.get("body") == "Sun"), {})
        if sun.get("lon") is not None:
            diff = _min_angle_diff(float(sun.get("lon")) - natal_sun_lon)
            if diff < best_diff:
                best_diff = diff
                best_time = current
        current += timedelta(hours=3)
    if best_time is None:
        return None
    refined = best_time - timedelta(hours=3)
    best_refined = best_time
    best_refined_diff = best_diff
    while refined <= best_time + timedelta(hours=3):
        _local_dt, utc_dt = _parse_local_datetime(
            refined.date().isoformat(),
            refined.strftime("%H:%M"),
            resolved_location.timezone,
        )
        jd = julian_day(utc_dt)
        cusps, angles_raw = _calc_houses(
            jd,
            resolved_location.latitude,
            resolved_location.longitude,
            house_system="placidus",
        )
        cusp_sequence = [0.0, *cusps]
        sun = next((entry for entry in _calc_bodies(jd, ["Sun"], cusp_sequence, angles_raw) if entry.get("body") == "Sun"), {})
        if sun.get("lon") is not None:
            diff = _min_angle_diff(float(sun.get("lon")) - natal_sun_lon)
            if diff < best_refined_diff:
                best_refined_diff = diff
                best_refined = refined
        refined += timedelta(minutes=30)
    return best_refined


def _dominant_solar_houses(solar_snapshot: Mapping[str, Any]) -> List[int]:
    weights: Dict[int, float] = {}
    for body in solar_snapshot.get("bodies") or []:
        if not isinstance(body, Mapping):
            continue
        house = _safe_int(body.get("house"))
        if not house:
            continue
        name = str(body.get("body") or "")
        weight = 1.0
        if name == "Sun":
            weight = 2.5
        elif name == "Moon":
            weight = 2.0
        elif name in {"Jupiter", "Saturn"}:
            weight = 1.5
        weights[house] = weights.get(house, 0.0) + weight
    ranked = sorted(weights.items(), key=lambda item: (-item[1], item[0]))
    return [house for house, _weight in ranked[:3]]


def _solar_natal_overlays(
    *,
    natal_snapshot: Mapping[str, Any],
    solar_snapshot: Mapping[str, Any],
    year_ruler: str,
) -> List[Dict[str, Any]]:
    cusps = [cusp.get("lon") for cusp in (natal_snapshot.get("house_cusps") or []) if cusp.get("lon") is not None]
    if len(cusps) < 12:
        return []
    overlays: List[Dict[str, Any]] = []
    for body_name in ["Sun", year_ruler]:
        if not body_name:
            continue
        body = _body_position(solar_snapshot, body_name)
        lon = body.get("lon")
        if lon is None:
            continue
        natal_house = _house_from_cusps(float(lon), cusps)
        overlays.append({"body": body_name, "natal_house": natal_house, "label_tr": _house_name(natal_house)})
    return overlays


def _solar_themes_tr(solar_sun_house: int | None, dominant_houses: Sequence[int], year_ruler: str) -> List[str]:
    themes = []
    if solar_sun_house:
        themes.append(f"Yilin ana sahnesi {_house_name(solar_sun_house)}.")
    if dominant_houses:
        themes.append(f"En cok calisan evler: {', '.join(_house_name(house) for house in dominant_houses[:2])}.")
    if year_ruler:
        themes.append(f"Yil yoneticisi {PLANET_TR.get(year_ruler, year_ruler)}.")
    return themes[:3]


def _solar_title_tr(solar_sun_house: int | None, dominant_houses: Sequence[int]) -> str:
    if solar_sun_house in {1, 4, 7, 10}:
        return _house_name(solar_sun_house or 1)
    if dominant_houses:
        return _house_name(dominant_houses[0])
    return "ana tema"


def _solar_summary_tr(
    solar_sun_house: int | None,
    dominant_houses: Sequence[int],
    year_ruler: str,
    overlays: Sequence[Mapping[str, Any]],
) -> str:
    base = f"Bu solar yil daha cok {_house_name(solar_sun_house or dominant_houses[0] if dominant_houses else 1)} temasinda aciliyor."
    if year_ruler:
        base += f" Temanin ritmi {PLANET_TR.get(year_ruler, year_ruler)} uzerinden kuruluyor."
    if overlays:
        body = overlays[0]
        base += f" Solar {PLANET_TR.get(str(body.get('body') or ''), str(body.get('body') or ''))} natal haritada {body.get('label_tr')} tarafina dusuyor."
    return base


def _solar_why_now_tr(solar_sun_house: int | None, dominant_houses: Sequence[int], year_ruler: str) -> str:
    house_bits = [_house_name(house) for house in dominant_houses[:2]]
    return f"Sebep, solar donus haritasinda yil {', '.join(house_bits) if house_bits else _house_name(solar_sun_house or 1)} ekseninden aciliyor; yon veren gezegen ise {PLANET_TR.get(year_ruler, year_ruler)}."
