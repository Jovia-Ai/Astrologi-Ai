from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple
import math
import re

from app.engine.transit_engine import (
    build_transit_window_report,
    fetch_location,
    julian_day,
    parse_birth_datetime_components,
    _calc_bodies,
    _calc_houses,
    _event_headline,
    _normalize_options,
)
from app.transit.interpret.theme_labeler import label_for_theme
from app.transit.serialize.calendar_serializers import build_calendar_public, build_public_day
from app.transit.interpret.interpretation_engine_v1 import enrich_markers_with_lens
from app.transit.lens.intent_scoring import score_month_payload_for_intent
from app.transit.calendar.day_enrichment import enrich_calendar_payload
from app.transit.lens.marker_features import infer_bodies, infer_marker_features
from .public_models import CalendarDayLite, CalendarMarker, TransitCalendarPublic


TIER_W = {"main": 3.0, "support": 2.0, "flavor": 1.0}
SEV_W = {"high": 3.0, "medium": 2.0, "low": 1.0}
PHASE_W = {"peak": 2.5, "start": 1.5, "end": 1.2, None: 1.0}

_PHASE_CLEAN_RE = re.compile(r"\s*\((basliyor|zirve|bitiyor)\)\s*", re.IGNORECASE)

# -----------------------------
# Calendar UX constants
# -----------------------------
_THEME_MIN_DAYS = 14
_SPIKE_MAX_SPREAD_DAYS = 7
_PEAK_WINDOW_DAYS = 2
_SLOW_THEME_BODIES = {
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
    "North Node",
    "South Node",
    "Chiron",
}

MONTH_TR = {
    1: "Ocak",
    2: "Şubat",
    3: "Mart",
    4: "Nisan",
    5: "Mayıs",
    6: "Haziran",
    7: "Temmuz",
    8: "Ağustos",
    9: "Eylül",
    10: "Ekim",
    11: "Kasım",
    12: "Aralık",
}
DOW_TR = {
    0: "Pazartesi",
    1: "Salı",
    2: "Çarşamba",
    3: "Perşembe",
    4: "Cuma",
    5: "Cumartesi",
    6: "Pazar",
}

PLANET_CORE_TR = {
    "Sun": "irade",
    "Moon": "duygu",
    "Mercury": "zihin",
    "Venus": "değer/çekim",
    "Mars": "hareket",
    "Jupiter": "genişleme",
    "Saturn": "sorumluluk",
    "Uranus": "değişim",
    "Neptune": "algı",
    "Pluto": "dönüşüm",
    "North Node": "yön",
    "South Node": "alışkanlık",
    "Chiron": "yaralanma",
    "Fortune": "akış",
    "Vertex": "kesişim",
}

HOUSE_THEME_TR = {
    1: "benlik",
    2: "maddi güven",
    3: "iletişim",
    4: "ev",
    5: "yaratıcılık",
    6: "günlük düzen",
    7: "ilişki",
    8: "paylaşım",
    9: "inanç",
    10: "kariyer",
    11: "gelecek",
    12: "iç dünya",
}

AXIS_THEME_TR = {"IC": "ev", "MC": "iş", "ASC": "benlik", "DSC": "ilişki"}

ASPECT_TONE_TR = {
    "conjunction": "yoğunlaşma",
    "square": "gerilim",
    "opposition": "çekişme",
    "trine": "akış",
    "sextile": "destek",
}

SIGN_TR = {
    "Aries": "Koç",
    "Taurus": "Boğa",
    "Gemini": "İkizler",
    "Cancer": "Yengeç",
    "Leo": "Aslan",
    "Virgo": "Başak",
    "Libra": "Terazi",
    "Scorpio": "Akrep",
    "Sagittarius": "Yay",
    "Capricorn": "Oğlak",
    "Aquarius": "Kova",
    "Pisces": "Balık",
}

PLANET_TR = {
    "Mercury": "Merkür",
    "Venus": "Venüs",
    "Mars": "Mars",
    "Sun": "Güneş",
    "Moon": "Ay",
    "Neptune": "Neptün",
    "Jupiter": "Jüpiter",
    "Saturn": "Satürn",
    "Uranus": "Uranüs",
    "Pluto": "Plüton",
}


@dataclass
class _EventMeta:
    event_id: str
    label: str
    start: date
    peak: date
    end: date
    transit: str
    natal: str
    aspect: str
    tier: str
    severity: str
    confidence: float


@dataclass(frozen=True)
class Marker:
    date: str
    kind: str
    event_id: str
    label: str
    severity: str
    tier: str
    is_critical: bool
    phase_kind: Optional[str]


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _date_range(start: date, end: date) -> Iterable[date]:
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def _in_range(d: date, start_d: date, end_d: date) -> bool:
    return start_d <= d <= end_d


def _split_slash(label: str) -> List[str]:
    return [p.strip() for p in (label or "").split("/") if p.strip()]


def _strip_phase_suffix(lbl: str) -> str:
    return _PHASE_CLEAN_RE.sub("", lbl or "").strip()


def _top2(parts: List[str]) -> Tuple[List[str], List[str]]:
    return parts[:2], parts[2:]


def _marker_weight(tier: str, severity: str, phase: Optional[str]) -> float:
    return TIER_W.get(tier, 1.0) * SEV_W.get(severity, 1.0) * PHASE_W.get(phase, 1.0)


def _dedupe_keep_order(values: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for value in values:
        if not value:
            continue
        if value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


def _diminishing(n: int) -> float:
    return math.log1p(max(0, n))


def _percentile(values_sorted: List[float], v: float) -> float:
    import bisect

    if len(values_sorted) <= 1:
        return 1.0
    i = bisect.bisect_right(values_sorted, v)
    return (i - 1) / (len(values_sorted) - 1)


def format_display_date(dt: date) -> str:
    return f"{dt.day} {MONTH_TR.get(dt.month, dt.month)} {dt.year}, {DOW_TR.get(dt.weekday(), '')}".strip()


def _moon_phase_from_lons(sun_lon: float | None, moon_lon: float | None) -> Optional[str]:
    if sun_lon is None or moon_lon is None:
        return None
    elong = (moon_lon - sun_lon) % 360.0
    if elong < 45.0 or elong >= 315.0:
        return "new"
    if elong < 135.0:
        return "waxing"
    if elong < 225.0:
        return "full"
    return "waning"


def _infer_domains_from_label(label: str) -> List[str]:
    s = (label or "").lower()
    domains: List[str] = []

    if "venüs" in s or "venus" in s:
        domains += ["venus", "beauty", "relationship"]
    if "ay " in s or s.startswith("ay") or "moon" in s:
        domains += ["moon"]
    if "mc" in s or "kariyer" in s or "iş" in s:
        domains += ["career", "business"]
    if "merkür" in s or "mercury" in s:
        domains += ["mercury", "business"]
    if "para" in s or "money" in s or "jüpiter" in s or "jupiter" in s:
        domains += ["money"]
    if "ilişki" in s:
        domains += ["relationship"]
    if "satürn" in s or "saturn" in s:
        domains += ["saturn"]
    if "node" in s:
        domains += ["node"]
    if "fortune" in s or "part of fortune" in s:
        domains += ["fortune"]

    return sorted(set(domains))


def _clamp_date(value: date, lo: date, hi: date) -> date:
    return max(lo, min(hi, value))


def _is_long_theme(meta: "_EventMeta") -> bool:
    span = (meta.end - meta.start).days
    return span >= _THEME_MIN_DAYS


def _make_theme_id(event_id: str) -> str:
    return f"theme.{event_id}"


def _force_theme(meta: "_EventMeta") -> bool:
    t = (meta.transit or "").strip()
    return t in _SLOW_THEME_BODIES


def _passes_conf(meta: "_EventMeta") -> bool:
    if meta.confidence >= 0.15:
        return True
    return meta.tier == "main" and meta.severity in ("high", "medium") and meta.confidence >= 0.08


def _entity_core(entity_key: str, entity_type: str) -> str:
    if entity_type == "axis":
        return AXIS_THEME_TR.get(entity_key, entity_key.lower())
    return PLANET_CORE_TR.get(entity_key, entity_key.lower())


def _entity_where(entity_type: str, house: Optional[int], entity_key: str) -> Optional[str]:
    if entity_type == "axis":
        return AXIS_THEME_TR.get(entity_key)
    if house:
        return HOUSE_THEME_TR.get(house)
    return None


def _normalize_target(raw: str) -> Dict[str, str]:
    low = (raw or "").lower()
    axis_keys = {"ic": "IC", "mc": "MC", "asc": "ASC", "dsc": "DSC"}
    if low in axis_keys:
        return {"key": axis_keys[low], "type": "axis"}
    return {"key": (raw[:1].upper() + raw[1:]) if raw else "", "type": "planet"}


def _build_labels(a: Dict[str, Any], aspect: str, b: Dict[str, Any]) -> Dict[str, str | None]:
    a_core = _entity_core(a.get("key", ""), a.get("type", "planet"))
    b_core = _entity_core(b.get("key", ""), b.get("type", "planet"))
    tone = ASPECT_TONE_TR.get(aspect, aspect or "etkileşim")

    a_where = _entity_where(a.get("type", "planet"), a.get("house"), a.get("key", ""))
    b_where = _entity_where(b.get("type", "planet"), b.get("house"), b.get("key", ""))

    if tone in ("gerilim", "çekişme"):
        short = f"{a_core} ↔ {b_core} {tone}"
    else:
        short = f"{a_core} + {b_core} {tone}"

    where = None
    if a_where or b_where:
        where = f"{a_where or '—'} ↔ {b_where or '—'}"

    if tone == "gerilim":
        full = f"{a_core.capitalize()} ({a_where}) ile {b_core} ({b_where}) arasında sürtünme."
    elif tone == "destek":
        full = f"{a_core.capitalize()} ({a_where}) ile {b_core} ({b_where}) arasında destek."
    elif tone == "akış":
        full = f"{a_core.capitalize()} ({a_where}) ile {b_core} ({b_where}) arasında akış."
    else:
        full = f"{a_core.capitalize()} ({a_where}) ile {b_core} ({b_where}) etkileşimi."

    full = full.replace("(None)", "").replace("  ", " ").replace(" ()", "").strip()
    return {"short": short, "where": where, "full": full}


def format_ingress_label(body_key: str, sign_key: str) -> str:
    return f"{PLANET_TR.get(body_key, body_key)} {SIGN_TR.get(sign_key, sign_key)} girişi"


def _detect_phase_kind(event_id: str, label: str) -> Optional[str]:
    eid = event_id or ""
    if "phase.ingress." in eid:
        return "ingress"
    if "phase.retro." in eid:
        return "retro"
    if label and "station" in label.lower():
        return "station"
    return None


def _normalize_marker_kind(old_kind: str) -> Tuple[str, Optional[str]]:
    if old_kind in ("start", "peak", "end"):
        return "aspect_window", old_kind
    if old_kind in ("aspect_window", "phase"):
        return old_kind, None
    return "phase", None


def _is_marker_critical(
    kind: str,
    phase: Optional[str],
    tier: str,
    severity: str,
    phase_kind: Optional[str],
) -> bool:
    if kind == "aspect_peak":
        return True
    if kind == "phase" and phase_kind in ("retro", "station"):
        return True
    return False


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _severity_weight(sev: str) -> float:
    return {"low": 0.6, "medium": 1.0, "high": 1.5}.get(sev, 1.0)


def _phase_kind_weight(phase_kind: Optional[str]) -> float:
    if phase_kind == "station":
        return 1.35
    if phase_kind == "retro":
        return 1.25
    if phase_kind == "ingress":
        return 1.05
    return 1.0


def _marker_weight_for_marker(marker: Marker) -> float:
    return _severity_weight(marker.severity) * _phase_kind_weight(marker.phase_kind)


def _is_long_running_event(event_id: str) -> bool:
    slow = ("saturn", "jupiter", "pluto", "neptune", "uranus")
    return event_id.startswith("tr.") and any(f".{planet}." in event_id for planet in slow)


def _daily_event_score(
    event_id: str,
    event_payload: Optional[Dict[str, Any]],
    *,
    fallback: float = 0.35,
) -> float:
    if not event_payload:
        base = fallback
    else:
        base = float(event_payload.get("weight", fallback))
        orb = event_payload.get("orb", None)
        if isinstance(orb, (int, float)):
            base *= float(math.exp(-0.35 * abs(float(orb))))
        if event_payload.get("is_exact") is True:
            base *= 1.35
        if event_payload.get("is_peak") is True:
            base *= 1.25
    if _is_long_running_event(event_id):
        base *= 0.55
    return clamp(base, 0.0, 1.0)


def _select_foreground_background(
    event_ids: List[str],
    event_payloads_by_id: Dict[str, Dict[str, Any]],
    *,
    foreground_max: int = 7,
    background_max: int = 3,
) -> Tuple[List[str], List[str]]:
    scored: List[Tuple[str, float]] = []
    for eid in event_ids:
        scored.append((eid, _daily_event_score(eid, event_payloads_by_id.get(eid))))
    scored.sort(key=lambda t: t[1], reverse=True)

    foreground: List[str] = []
    background: List[str] = []
    for eid, score in scored:
        if len(foreground) < foreground_max and score >= 0.25:
            foreground.append(eid)
        else:
            if _is_long_running_event(eid) and len(background) < background_max:
                background.append(eid)

    if len(foreground) < max(3, min(5, foreground_max)):
        for eid, _score in scored:
            if eid in foreground or eid in background:
                continue
            foreground.append(eid)
            if len(foreground) >= max(3, min(5, foreground_max)):
                break

    return foreground[:foreground_max], background[:background_max]


def _compute_heat(
    *,
    foreground_ids: List[str],
    background_ids: List[str],
    markers_today: List[Marker],
    is_critical: bool,
) -> int:
    fg = clamp(len(foreground_ids) / 7.0, 0.0, 1.0) * 70.0
    bg = clamp(len(background_ids) / 3.0, 0.0, 1.0) * 8.0
    phase_score = 0.0
    for marker in markers_today:
        phase_score += 7.0 * _marker_weight_for_marker(marker)
    phase_score = clamp(phase_score, 0.0, 25.0)
    crit = 8.0 if is_critical else 0.0
    heat = fg + bg + phase_score + crit
    heat = clamp(heat, 0.0, 100.0)
    return int(round(heat))


def _markers_by_date(markers: List[Dict[str, Any]]) -> Dict[str, List[Marker]]:
    out: Dict[str, List[Marker]] = {}
    for raw in markers or []:
        phase_kind = raw.get("phase_kind")
        if raw.get("kind") == "phase" and raw.get("event_id", "").startswith("phase.station."):
            phase_kind = phase_kind or "station"
        m = Marker(
            date=raw["date"],
            kind=raw.get("kind", "phase"),
            event_id=raw.get("event_id", ""),
            label=raw.get("label", ""),
            severity=raw.get("severity", "medium"),
            tier=raw.get("tier", "support"),
            is_critical=bool(raw.get("is_critical", False)),
            phase_kind=phase_kind,
        )
        out.setdefault(m.date, []).append(m)
    return out


def _event_tier(event: Mapping[str, Any]) -> str:
    body = str(event.get("transit") or "")
    duration = int(event.get("duration_days") or 0)
    confidence = float(event.get("confidence") or 0.0)
    if body in {"Saturn", "Uranus", "Neptune", "Pluto"} or duration >= 90:
        return "main"
    if confidence >= 0.6:
        return "support"
    return "support"


def _event_severity(event: Mapping[str, Any]) -> str:
    min_orb = float((event.get("orb") or {}).get("min") or 99.0)
    confidence = float(event.get("confidence") or 0.0)
    if min_orb <= 1.0 or confidence >= 0.75:
        return "high"
    if min_orb <= 2.5 or confidence >= 0.5:
        return "medium"
    return "low"


def _event_meta(event: Mapping[str, Any]) -> _EventMeta | None:
    timebox = event.get("timebox") or {}
    peaks = timebox.get("peaks") or []
    if not timebox.get("enter") or not timebox.get("exit") or not peaks:
        return None
    start = _parse_date(timebox.get("enter"))
    peak = _parse_date(peaks[0].get("t"))
    end = _parse_date(timebox.get("exit"))
    label = _event_headline(event)
    tier = _event_tier(event)
    severity = _event_severity(event)
    return _EventMeta(
        event_id=str(event.get("id") or ""),
        label=label,
        start=start,
        peak=peak,
        end=end,
        transit=str(event.get("transit") or ""),
        natal=str(event.get("natal") or ""),
        aspect=str(event.get("aspect") or ""),
        tier=tier,
        severity=severity,
        confidence=float(event.get("confidence") or 0.0),
    )


def _event_score(event_meta: _EventMeta, day: date) -> float:
    base = TIER_W.get(event_meta.tier, 1.0) * SEV_W.get(event_meta.severity, 1.0)
    bonus = 0.0
    if day == event_meta.peak:
        bonus = 0.4
    elif abs((day - event_meta.peak).days) == 1:
        bonus = 0.2
    return base + bonus


def _build_markers(events: List[_EventMeta]) -> List[CalendarMarker]:
    markers: List[CalendarMarker] = []
    for event in events or []:
        if not event.event_id:
            continue
        peak_date = event.peak.isoformat()
        markers.append(
            CalendarMarker(
                id=f"tr.peak.{event.event_id}",
                date=peak_date,
                kind="aspect_peak",
                event_id=event.event_id,
                label=_aspect_peak_label(event),
                severity=event.severity,
                tier=event.tier,
                is_critical=True,
                phase_kind=None,
            )
        )
    return markers


def _cluster_markers(markers: List[CalendarMarker]) -> List[CalendarMarker]:
    clustered: Dict[Tuple[str, str], CalendarMarker] = {}
    for marker in markers:
        key = (marker.date, marker.event_id)
        if key not in clustered:
            clustered[key] = marker
            continue
        existing = clustered[key]
        if _marker_weight(marker.tier, marker.severity, None) > _marker_weight(
            existing.tier, existing.severity, None
        ):
            clustered[key] = marker
    return list(clustered.values())


def _scan_phase_markers(
    *,
    start: date,
    end: date,
    transit_place: str,
    options: Mapping[str, Any] | None,
) -> List[CalendarMarker]:
    cfg = _normalize_options(options)
    location = fetch_location(transit_place)
    markers: List[CalendarMarker] = []

    prev_state: Dict[str, Dict[str, Any]] = {}
    monthly_seen: Dict[Tuple[str, str, str], str] = {}
    current = start
    while current <= end:
        local_dt, utc_dt = parse_birth_datetime_components(
            current.isoformat(),
            "12:00",
            location.timezone,
        )
        jd = julian_day(utc_dt)
        cusps, angles_raw = _calc_houses(jd, location.latitude, location.longitude, house_system=cfg.house_system)
        cusp_sequence = [0.0, *cusps]
        bodies = _calc_bodies(jd, cfg.include_bodies, cusp_sequence, angles_raw)
        for body in bodies:
            name = str(body.get("body") or "")
            sign = body.get("sign")
            retrograde = bool(body.get("retrograde"))
            speed = body.get("speed")
            prev = prev_state.get(name)
            if prev is not None:
                if sign and prev.get("sign") and sign != prev.get("sign"):
                    month_key = current.strftime("%Y-%m")
                    seen_key = (name, "ingress", month_key)
                    if seen_key in monthly_seen:
                        pass
                    else:
                        monthly_seen[seen_key] = current.isoformat()
                    markers.append(
                        CalendarMarker(
                            id=f"phase.ingress.{name}.{current.isoformat()}",
                            date=current.isoformat(),
                            kind="phase",
                            event_id=f"phase.ingress.{name}.{current.isoformat()}",
                            label=format_ingress_label(name, str(sign)),
                            severity="medium",
                            tier="support",
                            is_critical=True,
                            phase_kind="ingress",
                        )
                    )
                if retrograde != bool(prev.get("retrograde")):
                    label = f"{name} retro basliyor" if retrograde else f"{name} retro bitiyor"
                    month_key = current.strftime("%Y-%m")
                    seen_key = (name, "retro", month_key)
                    if seen_key in monthly_seen:
                        pass
                    else:
                        monthly_seen[seen_key] = current.isoformat()
                        markers.append(
                            CalendarMarker(
                                id=f"phase.retro.{name}.{current.isoformat()}",
                                date=current.isoformat(),
                                kind="phase",
                                event_id=f"phase.retro.{name}.{current.isoformat()}",
                                label=label,
                                severity="high",
                                tier="main",
                                is_critical=True,
                                phase_kind="retro",
                            )
                        )
                if speed is not None and prev.get("speed") is not None:
                    if (speed < 0) != (prev.get("speed") < 0):
                        month_key = current.strftime("%Y-%m")
                        seen_key = (name, "station", month_key)
                        if seen_key in monthly_seen:
                            pass
                        else:
                            monthly_seen[seen_key] = current.isoformat()
                            markers.append(
                                CalendarMarker(
                                    id=f"phase.station.{name}.{current.isoformat()}",
                                    date=current.isoformat(),
                                    kind="phase",
                                    event_id=f"phase.station.{name}.{current.isoformat()}",
                                    label=f"{PLANET_TR.get(name, name)} durağan: yön değişimi",
                                    severity="high",
                                    tier="main",
                                    is_critical=True,
                                    phase_kind="station",
                                )
                            )
            prev_state[name] = {"sign": sign, "retrograde": retrograde, "speed": speed}
        current += timedelta(days=1)
    return markers


def _is_outer_planet_ingress(name: str) -> bool:
    return name in {"Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"}


def _aspect_peak_label(event: _EventMeta) -> str:
    transit = _normalize_target(event.transit or "")
    natal = _normalize_target(event.natal or "")
    labels = _build_labels(
        {"key": transit.get("key"), "type": transit.get("type"), "house": None},
        event.aspect or "",
        {"key": natal.get("key"), "type": natal.get("type"), "house": None},
    )
    short = labels.get("short") or ""
    where = labels.get("where")
    if where:
        return f"{short} ({where})"
    return short or (event.label or "")


def build_transit_calendar_public(
    *,
    birth_date: str,
    birth_time: str,
    birth_place: str,
    transit_place: str,
    start: str,
    end: str,
    tz: str,
    lens: str = "general",
    options: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    start_date = _parse_date(start)
    end_date = _parse_date(end)
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    days_span = (end_date - start_date).days
    window_days = max(1, min(365, int(days_span / 2) + 2))
    mid_date = (start_date + timedelta(days=days_span // 2)).isoformat()

    window_report = build_transit_window_report(
        birth_date=birth_date,
        birth_time=birth_time,
        birth_place=birth_place,
        transit_date=mid_date,
        transit_time="12:00",
        transit_place=transit_place,
        options=options or {},
        window_days=window_days,
        step_hours=12,
        refine_near_exact=True,
        max_events=200,
        orb_hysteresis_deg=0.2,
        assumptions=[],
    )

    raw_events = window_report.get("events") or []
    event_meta = [meta for event in raw_events if (meta := _event_meta(event))]

    cfg = _normalize_options(options)
    location = fetch_location(transit_place)

    markers = _build_markers(event_meta)
    markers.extend(_scan_phase_markers(start=start_date, end=end_date, transit_place=transit_place, options=options))

    normalized_markers: List[CalendarMarker] = []
    for marker in markers:
        marker_date = _parse_date(marker.date)
        if not _in_range(marker_date, start_date, end_date):
            continue
        new_kind, _phase = _normalize_marker_kind(marker.kind)
        if new_kind != "phase":
            continue
        detected = _detect_phase_kind(marker.event_id, marker.label)
        marker.kind = "phase"
        marker.phase_kind = detected or marker.phase_kind
        marker.label = _strip_phase_suffix(marker.label)
        marker.is_critical = _is_marker_critical(
            marker.kind, None, marker.tier, marker.severity, marker.phase_kind
        )
        if marker.phase_kind == "ingress":
            body = marker.event_id.split(".")[2] if marker.event_id and len(marker.event_id.split(".")) > 2 else ""
            if _is_outer_planet_ingress(body):
                marker.is_critical = True
        if not getattr(marker, "id", None):
            marker.id = marker.event_id or f"mk.{marker.date}.{marker.label}"
        normalized_markers.append(marker)

    markers = _cluster_markers(normalized_markers)
    markers = enrich_markers_with_lens(markers)

    for marker in markers:
        marker.flags = marker.flags or infer_marker_features(marker.__dict__)
        marker.bodies = marker.bodies or infer_bodies(marker.__dict__)
        if not marker.domains:
            marker.domains = _infer_domains_from_label(marker.label or "")

    items_map_raw_spikes: Dict[str, List[str]] = {d.isoformat(): [] for d in _date_range(start_date, end_date)}
    active_theme_map: Dict[str, List[str]] = {d.isoformat(): [] for d in _date_range(start_date, end_date)}
    themes: List[Dict[str, Any]] = []
    theme_index: Dict[str, Dict[str, Any]] = {}
    days: List[CalendarDayLite] = []
    raw_scores: Dict[str, float] = {}

    markers_by_date: Dict[str, List[CalendarMarker]] = {}
    for marker in markers:
        markers_by_date.setdefault(marker.date, []).append(marker)

    event_meta_map: Dict[str, _EventMeta] = {meta.event_id: meta for meta in event_meta if meta.event_id}

    for meta in event_meta:
        if not _passes_conf(meta):
            continue
        forced_theme = _force_theme(meta)
        long_theme = _is_long_theme(meta)
        is_theme = long_theme or forced_theme
        range_start = max(start_date, meta.start)
        range_end = min(end_date, meta.end)
        if range_start > range_end:
            continue

        if is_theme:
            theme_id = _make_theme_id(meta.event_id)
            if theme_id not in theme_index:
                peak = max(meta.start, min(meta.peak, meta.end))
                theme_payload = {
                    "theme_id": theme_id,
                    "event_id": meta.event_id,
                    "label": label_for_theme(meta),
                    "start": meta.start.isoformat(),
                    "peak": peak.isoformat(),
                    "end": meta.end.isoformat(),
                    "tier": meta.tier,
                    "severity": meta.severity,
                    "confidence": meta.confidence,
                }
                theme_index[theme_id] = theme_payload
                themes.append(theme_payload)

            for d in _date_range(range_start, range_end):
                active_theme_map[d.isoformat()].append(theme_id)

            if long_theme and (not forced_theme):
                win_start = _clamp_date(meta.peak - timedelta(days=_PEAK_WINDOW_DAYS), start_date, end_date)
                win_end = _clamp_date(meta.peak + timedelta(days=_PEAK_WINDOW_DAYS), start_date, end_date)
                for d in _date_range(win_start, win_end):
                    items_map_raw_spikes[d.isoformat()].append(meta.event_id)
        else:
            span = (meta.end - meta.start).days
            if span <= _SPIKE_MAX_SPREAD_DAYS:
                for d in _date_range(range_start, range_end):
                    items_map_raw_spikes[d.isoformat()].append(meta.event_id)
            else:
                win_start = _clamp_date(meta.peak - timedelta(days=_PEAK_WINDOW_DAYS), start_date, end_date)
                win_end = _clamp_date(meta.peak + timedelta(days=_PEAK_WINDOW_DAYS), start_date, end_date)
                for d in _date_range(win_start, win_end):
                    items_map_raw_spikes[d.isoformat()].append(meta.event_id)

    for marker in markers:
        if marker.kind != "phase":
            continue
        day_key = marker.date
        if not day_key or day_key not in items_map_raw_spikes:
            continue
        if marker.event_id:
            items_map_raw_spikes[day_key].append(marker.event_id)

    for key in list(items_map_raw_spikes.keys()):
        items_map_raw_spikes[key] = _dedupe_keep_order(items_map_raw_spikes[key])
    for key in list(active_theme_map.keys()):
        active_theme_map[key] = _dedupe_keep_order(active_theme_map[key])

    recent_top_map: Dict[str, int] = {}

    for day in _date_range(start_date, end_date):
        day_str = day.isoformat()
        local_dt, utc_dt = parse_birth_datetime_components(
            day_str,
            "12:00",
            location.timezone,
        )
        jd = julian_day(utc_dt)
        cusps, angles_raw = _calc_houses(jd, location.latitude, location.longitude, house_system=cfg.house_system)
        cusp_sequence = [0.0, *cusps]
        bodies = _calc_bodies(jd, ["Sun", "Moon"], cusp_sequence, angles_raw)
        sun_lon = next((b.get("lon") for b in bodies if b.get("body") == "Sun"), None)
        moon_lon = next((b.get("lon") for b in bodies if b.get("body") == "Moon"), None)
        moon_phase = _moon_phase_from_lons(sun_lon, moon_lon)
        moon_sign = next((b.get("sign") for b in bodies if b.get("body") == "Moon"), None)
        active: List[_EventMeta] = [e for e in event_meta if e.start <= day <= e.end]
        scored = sorted(((e, _event_score(e, day)) for e in active), key=lambda x: x[1], reverse=True)

        day_markers = markers_by_date.get(day_str, [])
        label_scores: Dict[str, float] = {}
        for marker in day_markers:
            weight = _marker_weight(marker.tier, marker.severity, None)
            label = _strip_phase_suffix(marker.label)
            if not label:
                continue
            label_scores[label] = label_scores.get(label, 0.0) + weight

        peak_events = [e for e in active if e.peak == day]
        for event in peak_events:
            label = _aspect_peak_label(event)
            if not label:
                continue
            label_scores[label] = label_scores.get(label, 0.0) + 2.0

        ranked = sorted(label_scores.items(), key=lambda x: x[1], reverse=True)

        phase_shift_labels = [_strip_phase_suffix(m.label) for m in day_markers if m.kind == "phase"]
        phase_shift_labels = _dedupe_keep_order(phase_shift_labels)
        peak_labels = [_aspect_peak_label(e) for e in peak_events if _aspect_peak_label(e)]
        peak_labels = _dedupe_keep_order(peak_labels)
        dominant_labels = [lbl for lbl, _ in ranked]

        labels: List[str] = []
        for bucket in (phase_shift_labels, peak_labels, dominant_labels):
            for lbl in bucket:
                if lbl in labels:
                    continue
                labels.append(lbl)
                if len(labels) >= 3:
                    break
            if len(labels) >= 3:
                break
        if not labels and scored:
            labels = [_aspect_peak_label(scored[0][0])]

        is_phase_shift = any(
            m.kind == "phase" and m.phase_kind in ("retro", "station") for m in day_markers
        )
        has_peak = bool(peak_events)
        critical_reason: List[str] = []
        if is_phase_shift:
            critical_reason.append("phase_shift")
        if has_peak:
            critical_reason.append("event_peak")

        day_event_ids = items_map_raw_spikes.get(day_str, [])
        day_theme_ids = active_theme_map.get(day_str, [])
        phase_event_ids = [m.event_id for m in day_markers if m.kind == "phase" and m.event_id]
        peak_event_ids = [e.event_id for e in peak_events if e.event_id]

        def event_key(event_id: str) -> float:
            if event_id in phase_event_ids:
                return 3.0
            if event_id in peak_event_ids:
                return 2.0
            return 1.0

        ranked_ids = sorted(day_event_ids, key=event_key, reverse=True)

        top_ids: List[str] = []
        phase_picked = 0
        peak_picked = 0
        for eid in ranked_ids:
            if len(top_ids) >= 5:
                break
            is_peak = False
            meta = event_meta_map.get(eid)
            if meta and meta.peak == day:
                is_peak = True
            streak = recent_top_map.get(eid, 0)
            if (not is_peak) and streak >= 3 and eid not in phase_event_ids:
                continue
            if eid in phase_event_ids and phase_picked < 2:
                top_ids.append(eid)
                phase_picked += 1
                continue
            if eid in peak_event_ids and peak_picked < 2:
                top_ids.append(eid)
                peak_picked += 1
                continue
            if eid not in top_ids:
                top_ids.append(eid)

        top_ids = top_ids[:5]

        marker_score = sum(_marker_weight(m.tier, m.severity, None) for m in day_markers)
        raw = marker_score * 0.6 + math.sqrt(len(day_event_ids)) * 0.4
        raw_scores[day_str] = raw

        label_pack = {
            "phase": phase_shift_labels[:2],
            "top": [
                {"short": lbl, "where": None} for lbl in peak_labels[:2]
            ],
        }

        # Canonical daily distribution:
        # marker_ids/top_event_ids/top_marker_id all derive from the same selected event set.
        selected_event_ids = [eid for eid in top_ids if isinstance(eid, str)]
        marker_ids = [eid for eid in selected_event_ids if eid.startswith(("phase.", "tr."))]
        top_event_ids = marker_ids[:]
        top_marker_id = marker_ids[0] if marker_ids else None

        days.append(
            CalendarDayLite(
                date=day_str,
                display_date=format_display_date(day),
                moon_phase=moon_phase,
                moon_sign=moon_sign,
                heat=0,
                labels=labels[:3],
                is_critical=False,
                critical_reason=critical_reason,
                event_count=len(day_event_ids),
                top_event_ids=top_event_ids,
                label_pack=label_pack,
                active_theme_ids=day_theme_ids,
                marker_ids=marker_ids,
                top_marker_id=top_marker_id,
            )
        )

    raw_sorted = sorted(raw_scores.values()) if raw_scores else [0.0]
    for entry in days:
        raw = raw_scores.get(entry.date, 0.0)
        percentile = _percentile(raw_sorted, raw)
        entry.heat = int(round(percentile * 100))
        if entry.heat == 0:
            if entry.is_critical:
                entry.heat = max(entry.heat, 60)
            elif entry.event_count >= 3:
                entry.heat = max(entry.heat, 25)
            elif entry.event_count > 0:
                entry.heat = max(entry.heat, 15)
        # score: normalized 0..1 for internal/debug
        entry.score = round(entry.heat / 100.0, 4)
        # rating: 0..3 (neutral default if heat missing)
        if entry.heat >= 85:
            entry.rating = 3
        elif entry.heat >= 60:
            entry.rating = 2
        elif entry.heat >= 25:
            entry.rating = 1
        else:
            entry.rating = 0
        phase_shift_day = "phase_shift" in entry.critical_reason
        ingress_outer = any(
            m.kind == "phase"
            and m.phase_kind == "ingress"
            and _is_outer_planet_ingress(
                (m.event_id.split(".")[2] if m.event_id and len(m.event_id.split(".")) > 2 else "")
            )
            for m in markers_by_date.get(entry.date, [])
        )
        if entry.heat >= 85 or phase_shift_day or ingress_outer:
            entry.is_critical = True
        else:
            entry.is_critical = False
        if not entry.is_critical:
            entry.critical_reason = []

        in_top = set(entry.top_event_ids)
        for eid in list(recent_top_map.keys()):
            if eid not in in_top:
                recent_top_map[eid] = 0
        for eid in in_top:
            recent_top_map[eid] = recent_top_map.get(eid, 0) + 1

    domain_counts: Dict[str, int] = {}
    hard = 0
    soft = 0
    for event in raw_events:
        for domain in event.get("domains") or []:
            domain_counts[str(domain)] = domain_counts.get(str(domain), 0) + 1
        polarity = str(event.get("polarity") or "")
        if polarity == "hard":
            hard += 1
        elif polarity == "soft":
            soft += 1
    dominant_domains = [k for k, _ in sorted(domain_counts.items(), key=lambda x: -x[1])[:2]]
    total = max(1, hard + soft)
    year_summary = {
        "core_story": "",
        "dominant_domains": dominant_domains,
        "indices": {
            "pressure": round(hard / total, 3),
            "support": round(soft / total, 3),
        },
    }

    calendar = TransitCalendarPublic(
        range={"start": start_date.isoformat(), "end": end_date.isoformat(), "tz": tz},
        year_summary=year_summary,
        days=days,
        markers=markers,
        items_map=items_map_raw_spikes,
    )
    raw_payload = calendar.model_dump()
    payload = build_calendar_payload(
        range_payload=raw_payload.get("range", {}),
        year_summary=raw_payload.get("year_summary", {}),
        days=raw_payload.get("days", []),
        markers=raw_payload.get("markers", []),
        items_map_raw=items_map_raw_spikes,
        themes=themes,
        context=None,
    )
    dbg = payload.get("calendar_internal") or payload
    print("DBG internal keys:", dbg.keys())
    print("DBG markers:", len(dbg.get("markers", [])))
    print("DBG themes:", len(dbg.get("themes", [])))
    print("DBG items_map_raw:", len(dbg.get("items_map_raw", {})))
    return enrich_calendar_payload(payload)


def _score_event(event_id: str, context: Dict[str, Any]) -> float:
    score_map = context.get("score_map") or {}
    return float(score_map.get(event_id, 0.0))


def _pick_top(
    day_event_ids: List[str],
    *,
    n: int,
    context: Dict[str, Any],
) -> List[str]:
    scored = [(eid, _score_event(eid, context)) for eid in day_event_ids]
    scored.sort(key=lambda t: (-t[1], t[0]))
    return [eid for eid, _score in scored[:n]]


def _split_foreground_background(
    day_event_ids: List[str],
    top_ids: List[str],
) -> Tuple[List[str], List[str]]:
    top_set = set(top_ids)
    foreground = [eid for eid in day_event_ids if eid in top_set]
    background = [eid for eid in day_event_ids if eid not in top_set]
    return foreground, background


def _pin_phase_into_top(
    *,
    top_ids: List[str],
    phase_event_ids: List[str],
    max_pins: int,
    top_n: int,
) -> List[str]:
    if not phase_event_ids:
        return top_ids[:top_n]
    pins = phase_event_ids[:max_pins]
    merged = _dedupe_keep_order(pins + top_ids)
    return merged[:top_n]


def build_calendar_payload(
    *,
    range_payload: Dict[str, Any],
    year_summary: Dict[str, Any],
    days: List[Dict[str, Any]],
    markers: List[Dict[str, Any]],
    items_map_raw: Dict[str, List[str]],
    themes: List[Dict[str, Any]],
    top_n: int = 5,
    pin_phase_into_top: bool = True,
    phase_pin_max: int = 2,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    context = context or {}

    phase_ids_by_day: Dict[str, List[str]] = {}
    for marker in markers or []:
        if marker.get("kind") != "phase":
            continue
        day_key = marker.get("date")
        if not day_key:
            continue
        phase_ids_by_day.setdefault(day_key, []).append(marker.get("event_id"))

    derived_items_map_layers: Dict[str, Dict[str, List[str]]] = {}

    for day in days:
        day_str = day.get("date")
        if not day_str:
            continue

        raw_day_ids = _dedupe_keep_order(list(items_map_raw.get(day_str, [])))
        phase_event_ids = _dedupe_keep_order(
            [x for x in (phase_ids_by_day.get(day_str) or []) if x]
        )

        if "phase_event_ids" not in day:
            day["phase_event_ids"] = phase_event_ids

        top_ids = day.get("top_event_ids")
        if not top_ids:
            top_ids = _pick_top(raw_day_ids, n=top_n, context=context)
            if pin_phase_into_top:
                top_ids = _pin_phase_into_top(
                    top_ids=top_ids,
                    phase_event_ids=phase_event_ids,
                    max_pins=phase_pin_max,
                    top_n=top_n,
                )
            day["top_event_ids"] = top_ids

        foreground, background = _split_foreground_background(raw_day_ids, top_ids)
        derived_items_map_layers[day_str] = {
            "foreground": foreground,
            "background": background,
        }

        if "event_count" not in day:
            day["event_count"] = len(raw_day_ids)

    payload: Dict[str, Any] = {
        "range": range_payload,
        "year_summary": year_summary,
        "days": days,
        "markers": markers,
        "items_map": derived_items_map_layers,
        "items_map_raw": items_map_raw,
        "themes": themes,
    }

    default_intents = ["beauty_care", "business", "money", "relationship"]
    intent_summary: Dict[str, Dict[str, Any]] = {}
    for intent in default_intents:
        try:
            scored = score_month_payload_for_intent(intent=intent, payload=payload, max_why=3)
        except Exception:
            continue
        by_date = {s.date: {"score": s.score, "rating": s.rating} for s in scored if s.date}
        intent_summary[intent] = {"by_date": by_date}

    payload["intent_summary"] = intent_summary

    public_payload = build_calendar_public(payload, intent="transit", lens_suffix=None)
    # Quick self-check: lengths should match
    if len(public_payload.get("days", [])) != len(payload.get("days", [])):
        public_payload["days"] = [
            build_public_day(d) for d in (payload.get("days") or []) if isinstance(d, dict)
        ]

    return {
        "range": payload.get("range", {}),
        "year_summary": payload.get("year_summary", {}),
        "calendar_internal": payload,
        "calendar_public": public_payload,
    }
