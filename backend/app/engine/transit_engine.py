"""Transit engine v1: data-only transit snapshot and metrics."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import math
from typing import Any, Dict, Iterable, Mapping, Sequence
import time

import swisseph as swe

from app.astro.chart_engine.builder import (
    LocationData,
    fetch_location,
    julian_day,
    resolve_location,
)
from app.astro.chart_engine.positions import PLANET_CODES, get_zodiac_sign
from app.helpers.meta_detectors import ELEMENT_MAP, MODALITY_MAP
from app.helpers.transit_normalize import (
    build_angle_position,
    build_body_position,
    build_house_cusps,
    clamp01,
)
from app.utils.timezones import parse_birth_datetime_components


ASPECT_ANGLES = {
    "conjunction": 0,
    "opposition": 180,
    "square": 90,
    "trine": 120,
    "sextile": 60,
    "quincunx": 150,
    "semisextile": 30,
}

# Expected circular sign separation for each aspect type when formed "in sign".
# Used to detect dissociate (out-of-sign) aspects — where the bodies are at
# the geometric angle but in signs that don't match the aspect's natural
# element/modality relationship. Out-of-sign aspects are real but muted.
ASPECT_EXPECTED_SIGN_SEP = {
    "conjunction": 0,
    "semisextile": 1,
    "sextile": 2,
    "square": 3,
    "trine": 4,
    "quincunx": 5,
    "opposition": 6,
}

# Multiplier applied to orb_max when an aspect is out-of-sign. A tight
# dissociate aspect still qualifies, but a borderline one is filtered out.
OUT_OF_SIGN_ORB_FACTOR = 0.6

# Gaussian decay sigma, expressed as a fraction of orb_max. sigma = orb_max/2
# gives a softer decay near exact and a sharper tail; combined with the
# edge-subtraction below it yields strength=1 at orb=0 and strength=0 at
# orb=orb_max, with a bell-shaped curve in between.
_GAUSSIAN_SIGMA_RATIO = 0.5


def _decay_strength(orb: float, orb_max: float, mode: str) -> float:
    """Map (orb, orb_max) → strength in [0, 1] under the requested decay curve.

    linear:   strength = 1 - orb / orb_max                       (pre-PR6)
    gaussian: strength = (g(orb) - g(orb_max)) / (1 - g(orb_max))
              where g(x) = exp(-0.5 * (x / sigma)²), sigma = orb_max/2

    The Gaussian variant is edge-subtracted so strength=0 at orb=orb_max,
    keeping downstream threshold semantics (eligible_strength_min etc.)
    interpretable. Gaussian rewards tight orbs more than linear (e.g. at
    orb=orb_max/4: Gaussian ≈ 0.86 vs linear 0.75) and penalises borderline
    orbs slightly more (at orb=0.75·orb_max: Gaussian ≈ 0.22 vs linear 0.25).
    """
    if orb_max <= 0:
        return 0.0
    ratio = orb / orb_max
    if ratio >= 1.0:
        return 0.0
    if mode == "linear":
        return clamp01(1.0 - ratio)
    # gaussian (default)
    sigma = _GAUSSIAN_SIGMA_RATIO
    g_orb = math.exp(-0.5 * (ratio / sigma) ** 2)
    g_edge = math.exp(-0.5 * (1.0 / sigma) ** 2)
    return clamp01((g_orb - g_edge) / (1.0 - g_edge))

_TIMING_CACHE: dict[str, Dict[str, Any] | None] = {}
_TIMING_CACHE_MAX = 4096


@dataclass(frozen=True)
class TransitOptions:
    house_system: str
    zodiac: str
    include_bodies: list[str]
    include_angles: bool
    include_house_cusps: bool
    aspect_types: list[str]
    orbs: dict[str, float]
    max_aspects_per_transit_body: int
    debug: bool
    apply_out_of_sign_filter: bool = True
    orb_decay_mode: str = "gaussian"


def build_transit_report(
    *,
    birth_date: str,
    birth_time: str,
    birth_place: str,
    transit_date: str,
    transit_time: str,
    transit_place: str,
    options: Mapping[str, Any] | None,
    assumptions: Sequence[str],
    birth_latitude: float | None = None,
    birth_longitude: float | None = None,
    birth_timezone: str | None = None,
    transit_latitude: float | None = None,
    transit_longitude: float | None = None,
    transit_timezone: str | None = None,
) -> Dict[str, Any]:
    cfg = _normalize_options(options)
    natal_location = resolve_location(
        birth_place,
        latitude=birth_latitude,
        longitude=birth_longitude,
        timezone=birth_timezone,
    )
    transit_location = resolve_location(
        transit_place,
        latitude=transit_latitude,
        longitude=transit_longitude,
        timezone=transit_timezone,
    )

    natal = _build_chart_snapshot(
        date_value=birth_date,
        time_value=birth_time,
        place_value=birth_place,
        location=natal_location,
        options=cfg,
    )
    transit = _build_chart_snapshot(
        date_value=transit_date,
        time_value=transit_time,
        place_value=transit_place,
        location=transit_location,
        options=cfg,
    )

    aspects = _build_aspects(
        transit_bodies=transit["bodies"],
        natal_bodies=natal["bodies"],
        natal_angles=natal["angles"],
        transit_jd=float(transit["_jd_ut"]),
        options=cfg,
    )
    overlays = _build_house_overlays(transit["bodies"], natal["house_cusps"])
    metrics = _build_metrics(aspects["full_transit_to_natal"] + aspects["full_transit_to_angles"])
    presentable = _build_presentable(
        aspects["transit_to_natal"] + aspects["transit_to_angles"],
        metrics,
        cfg,
    )
    display = _build_display(
        transit_to_natal=aspects["transit_to_natal"],
        transit_to_angles=aspects["transit_to_angles"],
        natal_snapshot=natal,
        house_overlays=overlays,
        transit_datetime_utc=transit["datetime_utc"],
        transit_location=transit_location,
        options=cfg,
    )
    astro_full = _build_astro_full(
        aspects["full_transit_to_natal"] + aspects["full_transit_to_angles"],
        cfg,
    )
    natal.pop("_jd_ut", None)
    transit.pop("_jd_ut", None)

    debug_payload: Dict[str, Any] = {}
    if cfg.debug:
        timing_entries = [item.get("timing") for item in display.get("items") or []]
        timing_entries = [entry for entry in timing_entries if entry]
        exit_null_count = sum(1 for entry in timing_entries if entry.get("exit_date_utc") is None)
        window_days_used = max(
            [int(entry.get("window_days") or 0) for entry in timing_entries] or [0]
        )
        debug_payload = {
            "assumptions": list(assumptions),
            "options_used": cfg.__dict__,
            "presentable_counts": {
                "table_count": len(presentable.get("aspects_table") or []),
                "highlights_count": len(presentable.get("highlights") or []),
            },
            "timing_debug": {
                "exit_null_count": exit_null_count,
                "sampled_event_count": len(timing_entries),
                "window_days_used": window_days_used,
            },
        }

    return {
        "schema_version": "transit.v1",
        "engine_version": "transit-engine.v1",
        "request_echo": {
            "birth_date": birth_date,
            "birth_time": birth_time,
            "birth_place": birth_place,
            "transit_date": transit_date,
            "transit_time": transit_time,
            "transit_place": transit_place,
            "options": cfg.__dict__,
            "assumptions": list(assumptions),
        },
        "natal": natal,
        "transit": transit,
        "aspects": {
            "transit_to_natal": aspects["transit_to_natal"],
            "transit_to_angles": aspects["transit_to_angles"],
            "house_overlays": overlays,
        },
        "display": display,
        "astro_full": {"aspects": astro_full},
        "metrics": metrics,
        "presentable": presentable,
        "debug": debug_payload,
    }


def build_transit_event_timing(
    *,
    birth_date: str,
    birth_time: str,
    birth_place: str,
    transit_date: str,
    transit_time: str,
    transit_place: str,
    options: Mapping[str, Any] | None,
    selector: Mapping[str, Any],
    birth_latitude: float | None = None,
    birth_longitude: float | None = None,
    birth_timezone: str | None = None,
    transit_latitude: float | None = None,
    transit_longitude: float | None = None,
    transit_timezone: str | None = None,
) -> Dict[str, Any]:
    cfg = _normalize_options(options)
    natal_location = resolve_location(
        birth_place,
        latitude=birth_latitude,
        longitude=birth_longitude,
        timezone=birth_timezone,
    )
    transit_location = resolve_location(
        transit_place,
        latitude=transit_latitude,
        longitude=transit_longitude,
        timezone=transit_timezone,
    )
    natal = _build_chart_snapshot(
        date_value=birth_date,
        time_value=birth_time,
        place_value=birth_place,
        location=natal_location,
        options=cfg,
    )
    transit = _build_chart_snapshot(
        date_value=transit_date,
        time_value=transit_time,
        place_value=transit_place,
        location=transit_location,
        options=cfg,
    )
    aspects = _build_aspects(
        transit_bodies=transit["bodies"],
        natal_bodies=natal["bodies"],
        natal_angles=natal["angles"],
        transit_jd=float(transit["_jd_ut"]),
        options=cfg,
    )

    scope = str(selector.get("scope") or "transit_to_natal")
    if scope == "transit_to_angles":
        entries = aspects["transit_to_angles"]
    else:
        scope = "transit_to_natal"
        entries = aspects["transit_to_natal"]

    target_transit = _normalize_selector(selector.get("transit_body"))
    target_aspect = _normalize_selector(selector.get("aspect"))
    target_point = _normalize_selector(selector.get("natal_point"))

    matched: Mapping[str, Any] | None = None
    for entry in entries:
        transit_body = _normalize_selector((entry.get("transit") or {}).get("body"))
        aspect_type = _normalize_selector(entry.get("type"))
        natal_point = _normalize_selector(
            _normalize_angle_name(str((entry.get("natal") or {}).get("body") or ""))
        )
        if (
            transit_body == target_transit
            and aspect_type == target_aspect
            and natal_point == target_point
        ):
            matched = entry
            break

    if matched is None:
        return {"timing": None}

    transit_local_dt, transit_utc_dt = parse_birth_datetime_components(
        transit_date,
        transit_time,
        transit_location.timezone,
    )

    timing = _sample_display_timing(
        aspect_entry=matched,
        transit_dt=transit_utc_dt,
        location=transit_location,
        options=cfg,
        bucket=_duration_category(str((matched.get("transit") or {}).get("body") or "")),
        transit_date_utc_day=transit_utc_dt.date().isoformat(),
        natal_birth_signature=_natal_birth_signature(natal),
        house_system=cfg.house_system,
    )
    return {"timing": timing}


def build_transit_window_report(
    *,
    birth_date: str,
    birth_time: str,
    birth_place: str,
    transit_date: str,
    transit_time: str,
    transit_place: str,
    options: Mapping[str, Any] | None,
    window_days: int,
    step_hours: int,
    refine_near_exact: bool,
    max_events: int,
    orb_hysteresis_deg: float,
    assumptions: Sequence[str],
    birth_latitude: float | None = None,
    birth_longitude: float | None = None,
    birth_timezone: str | None = None,
    transit_latitude: float | None = None,
    transit_longitude: float | None = None,
    transit_timezone: str | None = None,
) -> Dict[str, Any]:
    cfg = _normalize_options(options)
    window_days = max(1, min(int(window_days), 365))
    step_hours = max(1, int(step_hours))
    max_events = max(1, int(max_events))
    orb_hysteresis_deg = max(0.0, float(orb_hysteresis_deg))

    natal_location = resolve_location(
        birth_place,
        latitude=birth_latitude,
        longitude=birth_longitude,
        timezone=birth_timezone,
    )
    natal = _build_chart_snapshot(
        date_value=birth_date,
        time_value=birth_time,
        place_value=birth_place,
        location=natal_location,
        options=cfg,
    )

    transit_location = resolve_location(
        transit_place,
        latitude=transit_latitude,
        longitude=transit_longitude,
        timezone=transit_timezone,
    )
    transit_local_dt, transit_utc_dt = parse_birth_datetime_components(
        transit_date,
        transit_time,
        transit_location.timezone,
    )

    try:
        swe.set_topo(transit_location.longitude, transit_location.latitude, 0.0)
    except Exception:
        pass

    transit_jd = julian_day(transit_utc_dt)
    cusps, angles_raw = _calc_houses(
        transit_jd,
        transit_location.latitude,
        transit_location.longitude,
        house_system=cfg.house_system,
    )
    cusp_sequence = [0.0, *cusps]
    transit_bodies = _calc_bodies(transit_jd, cfg.include_bodies, cusp_sequence, angles_raw)

    start_utc = transit_utc_dt - timedelta(days=window_days)
    end_utc = transit_utc_dt + timedelta(days=window_days)

    start_perf = time.perf_counter()
    candidates = _build_window_candidates(
        transit_bodies=transit_bodies,
        natal_snapshot=natal,
        aspect_types=cfg.aspect_types,
        orbs=cfg.orbs,
    )
    candidates = _sort_candidates(candidates)[: max_events * 2]

    events: list[Dict[str, Any]] = []
    for candidate in candidates:
        event = _scan_candidate_window(
            candidate=candidate,
            transit_location=transit_location,
            start_utc=start_utc,
            end_utc=end_utc,
            step_hours=step_hours,
            refine_near_exact=refine_near_exact,
            orb_hysteresis_deg=orb_hysteresis_deg,
        )
        if event:
            events.append(event)

    events = sorted(events, key=lambda entry: entry["timebox"]["enter"])
    if len(events) > max_events:
        events = events[:max_events]

    presentable = _build_window_presentable(events)
    elapsed_ms = int(round((time.perf_counter() - start_perf) * 1000))

    return {
        "schema_version": "transit.window.v1",
        "engine_version": "transit-engine.v1.5",
        "presentable": presentable,
        "events": events,
        "meta": {
            "scan": {
                "window_days": window_days,
                "step_hours": step_hours,
                "refine_near_exact": refine_near_exact,
                "max_events": max_events,
                "orb_hysteresis_deg": orb_hysteresis_deg,
                "candidate_count": len(candidates),
                "event_count": len(events),
                "assumptions": list(assumptions),
            },
            "performance": {"elapsed_ms": elapsed_ms},
        },
    }


def _normalize_options(options: Mapping[str, Any] | None) -> TransitOptions:
    raw = dict(options or {})
    include_bodies = raw.get("include_bodies") or [
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
        "Pluto",
        "North Node",
        "South Node",
        "Chiron",
        "Lilith",
        "Vertex",
        "Fortune",
    ]
    return TransitOptions(
        house_system=str(raw.get("house_system") or "placidus").strip().lower(),
        zodiac=str(raw.get("zodiac") or "tropical").strip().lower(),
        include_bodies=[str(body) for body in include_bodies],
        include_angles=bool(raw.get("include_angles", True)),
        include_house_cusps=bool(raw.get("include_house_cusps", True)),
        aspect_types=[str(item) for item in (raw.get("aspect_types") or list(ASPECT_ANGLES.keys()))],
        orbs={
            "conjunction": float((raw.get("orbs") or {}).get("conjunction", 4.0)),
            "opposition": float((raw.get("orbs") or {}).get("opposition", 4.0)),
            "square": float((raw.get("orbs") or {}).get("square", 3.5)),
            "trine": float((raw.get("orbs") or {}).get("trine", 3.0)),
            "sextile": float((raw.get("orbs") or {}).get("sextile", 2.5)),
            "quincunx": float((raw.get("orbs") or {}).get("quincunx", 2.0)),
            "semisextile": float((raw.get("orbs") or {}).get("semisextile", 1.5)),
        },
        max_aspects_per_transit_body=int(raw.get("max_aspects_per_transit_body") or 12),
        debug=bool(raw.get("debug", False)),
        apply_out_of_sign_filter=bool(raw.get("apply_out_of_sign_filter", True)),
        orb_decay_mode=str(raw.get("orb_decay_mode") or "gaussian").strip().lower(),
    )


DOMAIN_RULES = {
    "ASC": ["identity"],
    "MC": ["career", "life_direction"],
    "DSC": ["relationships"],
    "IC": ["inner_world", "home"],
    "Sun": ["identity", "purpose"],
    "Moon": ["emotions"],
    "Mercury": ["mind", "communication"],
    "Venus": ["relationships", "values"],
    "Mars": ["drive", "energy"],
    "Jupiter": ["growth", "beliefs"],
    "Saturn": ["structure", "responsibility"],
    "Uranus": ["change", "freedom"],
    "Neptune": ["meaning", "confusion"],
    "Pluto": ["power", "transformation"],
}


def _build_chart_snapshot(
    *,
    date_value: str,
    time_value: str,
    place_value: str,
    location: LocationData | None,
    options: TransitOptions,
) -> Dict[str, Any]:
    resolved_location = location or resolve_location(place_value)
    local_dt, utc_dt = parse_birth_datetime_components(
        date_value,
        time_value,
        resolved_location.timezone,
    )
    jd_ut = julian_day(utc_dt)

    try:
        swe.set_topo(resolved_location.longitude, resolved_location.latitude, 0.0)
    except Exception:
        pass

    cusps, angles_raw = _calc_houses(
        jd_ut,
        resolved_location.latitude,
        resolved_location.longitude,
        house_system=options.house_system,
    )
    cusp_sequence = [0.0, *cusps]
    bodies = _calc_bodies(jd_ut, options.include_bodies, cusp_sequence, angles_raw)
    angles = _normalize_angles(angles_raw) if options.include_angles else {}
    house_cusps = build_house_cusps(cusps) if options.include_house_cusps else []

    return {
        "_jd_ut": jd_ut,
        "datetime_utc": utc_dt.isoformat(),
        "location": {
            "lat": resolved_location.latitude,
            "lon": resolved_location.longitude,
            "tz": resolved_location.timezone,
        },
        "house_system": options.house_system,
        "zodiac": options.zodiac,
        "bodies": bodies,
        "angles": angles,
        "house_cusps": house_cusps,
    }


def _calc_houses(
    jd_ut: float,
    latitude: float,
    longitude: float,
    *,
    house_system: str,
) -> tuple[list[float], Dict[str, float]]:
    flag = (house_system[:1] or "P").upper().encode("ascii")
    cusps_raw, ascmc = swe.houses(jd_ut, latitude, longitude, flag)
    cusps = [float(cusps_raw[i]) % 360 for i in range(12)]
    angles = {
        "ascendant": float(ascmc[0] % 360),
        "midheaven": float(ascmc[1] % 360),
    }
    angles["descendant"] = (angles["ascendant"] + 180) % 360
    angles["imum_coeli"] = (angles["midheaven"] + 180) % 360
    return cusps, angles


def _calc_bodies(
    jd_ut: float,
    include_bodies: Iterable[str],
    cusp_sequence: Sequence[float],
    angles_raw: Mapping[str, float],
) -> list[Dict[str, Any]]:
    positions: list[Dict[str, Any]] = []
    for body in include_bodies:
        if body == "South Node":
            node_result = swe.calc_ut(jd_ut, PLANET_CODES["North Node"])
            node_values = node_result[0] if isinstance(node_result[0], (list, tuple)) else node_result
            node_lon = node_values[0] if len(node_values) > 0 else None
            node_speed = node_values[3] if len(node_values) > 3 else None
            lon = (float(node_lon) + 180) % 360 if node_lon is not None else None
            positions.append(build_body_position(body, lon, node_speed, cusp_sequence[1:13]))
            continue
        if body == "Fortune":
            asc = angles_raw.get("ascendant")
            sun = _body_lon("Sun", positions)
            moon = _body_lon("Moon", positions)
            if asc is not None and sun is not None and moon is not None:
                fortune_lon = (asc + moon - sun) % 360
                positions.append(build_body_position(body, fortune_lon, None, cusp_sequence[1:13]))
            continue
        planet_id = PLANET_CODES.get(body)
        if planet_id is None:
            continue
        result = swe.calc_ut(jd_ut, planet_id)
        values = result[0] if isinstance(result[0], (list, tuple)) else result
        lon = values[0] if len(values) > 0 else None
        speed = values[3] if len(values) > 3 else None
        positions.append(build_body_position(body, lon, speed, cusp_sequence[1:13]))
    return positions


def _normalize_angles(angles_raw: Mapping[str, float]) -> Dict[str, Dict[str, Any]]:
    return {
        "ASC": build_angle_position("ASC", angles_raw.get("ascendant")),
        "MC": build_angle_position("MC", angles_raw.get("midheaven")),
        "DSC": build_angle_position("DSC", angles_raw.get("descendant")),
        "IC": build_angle_position("IC", angles_raw.get("imum_coeli")),
    }


def _build_aspects(
    *,
    transit_bodies: Sequence[Mapping[str, Any]],
    natal_bodies: Sequence[Mapping[str, Any]],
    natal_angles: Mapping[str, Mapping[str, Any]],
    transit_jd: float,
    options: TransitOptions,
) -> Dict[str, list[Dict[str, Any]]]:
    full_transit_to_natal: list[Dict[str, Any]] = []
    full_transit_to_angles: list[Dict[str, Any]] = []
    allowed_types = [t for t in options.aspect_types if t in ASPECT_ANGLES]

    for transit in transit_bodies:
        transit_lon = transit.get("lon")
        if transit_lon is None:
            continue
        for natal in natal_bodies:
            natal_lon = natal.get("lon")
            if natal_lon is None:
                continue
            full_transit_to_natal.extend(
                _aspects_for_pair(
                    transit,
                    natal,
                    transit_lon,
                    natal_lon,
                    allowed_types,
                    options.orbs,
                    transit_jd=transit_jd,
                    apply_oos_filter=options.apply_out_of_sign_filter,
                    decay_mode=options.orb_decay_mode,
                )
            )
        if options.include_angles:
            for angle in natal_angles.values():
                angle_lon = angle.get("lon")
                if angle_lon is None:
                    continue
                full_transit_to_angles.extend(
                    _aspects_for_pair(
                        transit,
                        {"body": _normalize_angle_name(angle.get("point"))},
                        transit_lon,
                        angle_lon,
                        allowed_types,
                        options.orbs,
                        transit_jd=transit_jd,
                    )
                )

    transit_to_natal = _cap_per_transit(full_transit_to_natal, options.max_aspects_per_transit_body)
    transit_to_angles = _cap_per_transit(full_transit_to_angles, options.max_aspects_per_transit_body)

    return {
        "full_transit_to_natal": _sort_aspects(full_transit_to_natal),
        "full_transit_to_angles": _sort_aspects(full_transit_to_angles),
        "transit_to_natal": _sort_aspects(transit_to_natal),
        "transit_to_angles": _sort_aspects(transit_to_angles),
    }


def _aspects_for_pair(
    transit: Mapping[str, Any],
    natal: Mapping[str, Any],
    transit_lon: float,
    natal_lon: float,
    allowed_types: Sequence[str],
    orbs: Mapping[str, float],
    *,
    transit_jd: float,
    apply_oos_filter: bool = True,
    decay_mode: str = "gaussian",
) -> list[Dict[str, Any]]:
    aspects: list[Dict[str, Any]] = []
    for aspect_type in allowed_types:
        exact = ASPECT_ANGLES[aspect_type]
        orb = abs(_min_angle_diff(transit_lon - natal_lon) - exact)
        orb_max = float(orbs.get(aspect_type, 6.0))
        expected_sep = ASPECT_EXPECTED_SIGN_SEP.get(aspect_type)
        out_of_sign = False
        if expected_sep is not None:
            actual_sep = _sign_separation(transit_lon, natal_lon)
            out_of_sign = actual_sep != expected_sep
        effective_orb_max = orb_max * OUT_OF_SIGN_ORB_FACTOR if (out_of_sign and apply_oos_filter) else orb_max
        if orb > effective_orb_max:
            continue
        strength = _decay_strength(orb, effective_orb_max, decay_mode)
        polarity = "neutral"
        if aspect_type in {"square", "opposition"}:
            polarity = "hard"
        elif aspect_type in {"trine", "sextile"}:
            polarity = "soft"
        phase = _aspect_phase(transit.get("body"), transit_lon, natal_lon, exact, transit_jd)
        orb_parts = _orb_parts(orb)
        duration_full, duration_note = _duration_full(
            transit.get("body"),
            entry_speed=transit.get("speed"),
            orb=orb,
            orb_max=effective_orb_max,
            phase=phase,
        )
        aspects.append(
            {
                "type": aspect_type,
                "orb": round(orb, 2),
                "strength": round(strength, 3),
                "polarity": polarity,
                "out_of_sign": out_of_sign,
                "transit": {
                    "body": transit.get("body"),
                    "lon": transit_lon,
                    "speed": transit.get("speed"),
                },
                "natal": {"body": natal.get("body"), "lon": natal_lon},
                "exact_angle": exact,
                "phase": phase,
                "orb_parts": orb_parts,
                "duration_full": duration_full,
                "duration_note": duration_note,
            }
        )
    return aspects


def _sign_separation(lon_a: float, lon_b: float) -> int:
    """Circular separation between two zodiac signs, 0..6."""
    sign_a = int((lon_a % 360.0) / 30.0)
    sign_b = int((lon_b % 360.0) / 30.0)
    diff = abs(sign_a - sign_b)
    return min(diff, 12 - diff)


def _cap_per_transit(aspects: list[Dict[str, Any]], cap: int) -> list[Dict[str, Any]]:
    if cap <= 0:
        return aspects
    by_body: Dict[str, list[Dict[str, Any]]] = {}
    for entry in aspects:
        body = str((entry.get("transit") or {}).get("body") or "")
        by_body.setdefault(body, []).append(entry)
    capped: list[Dict[str, Any]] = []
    for body in sorted(by_body.keys()):
        entries = _sort_aspects(by_body[body])[:cap]
        capped.extend(entries)
    return capped


def _sort_aspects(aspects: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
    return sorted(
        aspects,
        key=lambda entry: (
            -float(entry.get("strength") or 0.0),
            float(entry.get("orb") or 0.0),
            str((entry.get("transit") or {}).get("body") or ""),
            str((entry.get("natal") or {}).get("body") or (entry.get("natal") or {}).get("angle") or ""),
            str(entry.get("type") or ""),
        ),
    )


def _sort_astro_full(aspects: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
    return sorted(
        aspects,
        key=lambda entry: (
            -float(entry.get("strength") or 0.0),
            float((entry.get("orb") or {}).get("value_deg") or 0.0),
            str((entry.get("transit") or {}).get("body") or ""),
            str((entry.get("natal") or {}).get("point") or ""),
            str((entry.get("aspect") or {}).get("type") or ""),
        ),
    )


def _build_house_overlays(
    transit_bodies: Sequence[Mapping[str, Any]],
    natal_cusps: Sequence[Mapping[str, Any]],
) -> list[Dict[str, Any]]:
    cusps = [cusp.get("lon") for cusp in natal_cusps if cusp.get("lon") is not None]
    if len(cusps) < 12:
        return []
    overlays: list[Dict[str, Any]] = []
    for body in transit_bodies:
        lon = body.get("lon")
        if lon is None:
            continue
        house = _house_from_cusps(lon, cusps)
        overlays.append(
            {
                "transit_body": body.get("body"),
                "natal_house": house,
                "confidence": 0.95,
            }
        )
    return overlays


def _house_from_cusps(lon: float, cusps: Sequence[float]) -> int:
    lon_val = lon % 360
    for idx in range(12):
        start = cusps[idx] % 360
        end = cusps[(idx + 1) % 12] % 360
        if start <= end:
            if start <= lon_val < end:
                return idx + 1
        else:
            if lon_val >= start or lon_val < end:
                return idx + 1
    return 12


def _build_metrics(aspects: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    hard_types = {"square", "opposition"}
    soft_types = {"trine", "sextile"}
    by_transit: Dict[str, list[Mapping[str, Any]]] = {}
    by_natal: Dict[str, list[Mapping[str, Any]]] = {}
    total_hard = 0.0
    total_soft = 0.0
    total_neutral = 0.0

    for entry in aspects:
        strength = float(entry.get("strength") or 0.0)
        aspect_type = str(entry.get("type") or "")
        transit_body = str((entry.get("transit") or {}).get("body") or "")
        natal_body = str((entry.get("natal") or {}).get("body") or (entry.get("natal") or {}).get("angle") or "")
        by_transit.setdefault(transit_body, []).append(entry)
        by_natal.setdefault(natal_body, []).append(entry)
        if aspect_type in hard_types:
            total_hard += strength
        elif aspect_type in soft_types:
            total_soft += strength
        else:
            total_neutral += strength

    hot_bodies = _rank_hits(by_transit)
    hot_natal = _rank_hits(by_natal, key_name="point")
    top_aspects = _sort_aspects(list(aspects))[:10]

    total_sum = total_hard + total_soft
    denom = total_sum + 1e-9
    pressure_index = clamp01(total_hard / denom) if total_sum else 0.0
    support_index = clamp01(total_soft / denom) if total_sum else 0.0
    intensity_index = clamp01(total_sum / 12.0)
    return {
        "hot_bodies": hot_bodies,
        "hot_natal_points": hot_natal,
        "pressure_index": round(pressure_index, 3),
        "support_index": round(support_index, 3),
        "intensity_index": round(intensity_index, 3),
        "top_aspects": top_aspects,
        "debug_totals": {
            "total_hard": round(total_hard, 3),
            "total_soft": round(total_soft, 3),
            "total_neutral": round(total_neutral, 3),
            "denom": round(denom, 6),
        },
    }


def _rank_hits(
    mapping: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    key_name: str = "body",
) -> list[Dict[str, Any]]:
    ranked: list[Dict[str, Any]] = []
    for key, entries in mapping.items():
        score = sum(float(entry.get("strength") or 0.0) for entry in entries)
        top_hits = _sort_aspects(list(entries))[:3]
        ranked.append(
            {
                key_name: key,
                "score": round(score, 3),
                "top_hits": [
                    {
                        "type": hit.get("type"),
                        "natal": (hit.get("natal") or {}).get("body"),
                        "strength": hit.get("strength"),
                    }
                    for hit in top_hits
                ],
            }
        )
    ranked.sort(key=lambda entry: (-float(entry.get("score") or 0.0), str(entry.get(key_name) or "")))
    return ranked


def _build_presentable(
    aspects: Sequence[Mapping[str, Any]],
    metrics: Mapping[str, Any],
    options: TransitOptions,
) -> Dict[str, Any]:
    aspects_sorted = _sort_aspects(list(aspects))
    table: list[Dict[str, Any]] = []
    per_body_count: Dict[str, int] = {}
    for entry in aspects_sorted:
        transit_body = str((entry.get("transit") or {}).get("body") or "")
        natal_point = str((entry.get("natal") or {}).get("body") or "")
        if not transit_body or not natal_point:
            continue
        if len(table) >= 25:
            break
        count = per_body_count.get(transit_body, 0)
        if count >= options.max_aspects_per_transit_body:
            continue
        duration = _estimate_duration(entry, options)
        table.append(
            {
                "transit_body": transit_body,
                "aspect": entry.get("type"),
                "natal_point": natal_point,
                "orb": entry.get("orb"),
                "strength": entry.get("strength"),
                "polarity": entry.get("polarity"),
                "duration": duration,
                "tags": _derive_tags(entry),
            }
        )
        per_body_count[transit_body] = count + 1

    highlights: list[Dict[str, Any]] = []
    hot_bodies = list(metrics.get("hot_bodies") or [])[:3]
    for hot in hot_bodies:
        body = hot.get("body") or hot.get("point")
        if not body:
            continue
        hits = _sort_aspects(
            [entry for entry in aspects_sorted if (entry.get("transit") or {}).get("body") == body]
        )[:2]
        items = []
        for hit in hits:
            duration = _estimate_duration(hit, options)
            items.append(
                {
                    "label": f"{body} {hit.get('type')} {(hit.get('natal') or {}).get('body')}",
                    "orb": hit.get("orb"),
                    "strength": hit.get("strength"),
                    "category": duration.get("category"),
                    "duration_estimate_days": duration.get("estimate_days"),
                    "why_important": _why_important(hit),
                }
            )
        if items:
            highlights.append(
                {
                    "title": _highlight_title(body, items),
                    "items": items,
                }
            )

    return {"highlights": highlights, "aspects_table": table}


def _build_astro_full(
    aspects: Sequence[Mapping[str, Any]],
    options: TransitOptions,
) -> list[Dict[str, Any]]:
    out: list[Dict[str, Any]] = []
    angle_points = {"ASC", "MC", "DSC", "IC"}
    for entry in aspects:
        transit = entry.get("transit") or {}
        natal = entry.get("natal") or {}
        aspect_type = entry.get("type")
        orb_value = float(entry.get("orb") or 0.0)
        orb_parts = entry.get("orb_parts") or _orb_parts(orb_value)
        duration_full = entry.get("duration_full")
        duration = dict(duration_full) if isinstance(duration_full, dict) else None
        if duration:
            duration.update(
                {
                    "to_exact_days": duration_full.get("estimate_days_to_exact"),
                    "remaining_days": duration_full.get("estimate_days_to_exit"),
                    "total_window_days": duration_full.get("estimate_days_total_window"),
                }
            )
        natal_point = natal.get("body")
        scope = "transit_to_angles" if natal_point in angle_points else "transit_to_natal"
        out.append(
            {
                "scope": scope,
                "transit": {
                    "body": transit.get("body"),
                    "sign": _sign_from_lon(transit.get("lon")),
                    "lon": transit.get("lon"),
                    "speed": transit.get("speed"),
                },
                "natal": {
                    "point": natal.get("body"),
                    "sign": _sign_from_lon(natal.get("lon")),
                    "lon": natal.get("lon"),
                },
                "aspect": {
                    "type": aspect_type,
                    "exact_angle": entry.get("exact_angle"),
                },
                "orb": {
                    "value_deg": orb_value,
                    "deg": orb_parts["deg"],
                    "min": orb_parts["min"],
                },
                "phase": entry.get("phase"),
                "strength": entry.get("strength"),
                "polarity": entry.get("polarity"),
                "duration": duration,
            }
        )
    return _sort_astro_full(out)


def _build_display(
    *,
    transit_to_natal: Sequence[Mapping[str, Any]],
    transit_to_angles: Sequence[Mapping[str, Any]],
    natal_snapshot: Mapping[str, Any],
    house_overlays: Sequence[Mapping[str, Any]],
    transit_datetime_utc: str,
    transit_location: LocationData,
    options: TransitOptions,
) -> Dict[str, Any]:
    items: list[Dict[str, Any]] = []
    natal_house_map = _natal_house_map(natal_snapshot)
    transit_house_map = _transit_house_map(house_overlays)
    transit_dt = datetime.fromisoformat(transit_datetime_utc)
    transit_date_utc_day = transit_dt.date().isoformat()
    natal_birth_signature = _natal_birth_signature(natal_snapshot)
    try:
        swe.set_topo(transit_location.longitude, transit_location.latitude, 0.0)
    except Exception:
        pass

    combined = [
        ("transit_to_natal", transit_to_natal),
        ("transit_to_angles", transit_to_angles),
    ]
    for scope, entries in combined:
        for idx, entry in enumerate(entries):
            transit_body = str((entry.get("transit") or {}).get("body") or "")
            natal_point = _normalize_angle_name(str((entry.get("natal") or {}).get("body") or ""))
            aspect_type = str(entry.get("type") or "")
            transit_sign = _sign_from_lon((entry.get("transit") or {}).get("lon"))
            target_sign = _sign_from_lon((entry.get("natal") or {}).get("lon"))
            orb_limit = float(options.orbs.get(aspect_type, 6.0))
            orb_value = float(entry.get("orb") or 0.0)
            phase = _display_phase(orb_value, orb_limit, entry.get("phase"))
            event_id = _display_event_id(transit_body, aspect_type, natal_point, scope, transit_dt)
            base_tags = _display_tags(natal_point, natal_house_map)
            aspect_tags = _aspect_tag_map(aspect_type)
            planet_tags = _planet_tag_map(transit_body)
            tags = _merge_tags(base_tags, aspect_tags, planet_tags)
            items.append(
                {
                    "event_id": event_id,
                    "scope": scope,
                    "label": f"{transit_body} {aspect_type} {natal_point} (orb {orb_value:.2f}°)",
                    "transit_body": transit_body,
                    "aspect": aspect_type,
                    "natal_point": natal_point,
                    "polarity": entry.get("polarity"),
                    "strength": entry.get("strength"),
                    "orb_deg": orb_value,
                    "phase": phase,
                    "bucket": _duration_category(transit_body),
                    "tags": tags,
                    "astro_style": {
                        "transit": _style_from_sign(transit_sign) or {},
                        "target": _style_from_sign(target_sign) or {},
                    },
                    "houses": {
                        "transit_in_natal_house": transit_house_map.get(transit_body),
                        "natal_point_house": natal_house_map.get(natal_point),
                    },
                    "timing": None,
                    "raw_ref": {"scope": scope, "index": idx},
                }
            )

    items = _sort_display_items(items)
    featured_indices = _select_featured_indices(items)
    featured = [items[idx] for idx in featured_indices]

    max_items_to_sample = 20
    sample_indices = set(featured_indices)
    for idx in range(len(items)):
        if len(sample_indices) >= max_items_to_sample:
            break
        sample_indices.add(idx)

    for idx in sorted(sample_indices):
        entry = items[idx]
        raw_ref = entry.get("raw_ref") or {}
        source_scope = raw_ref.get("scope")
        source_index = int(raw_ref.get("index") or 0)
        source = transit_to_natal if source_scope == "transit_to_natal" else transit_to_angles
        if source_index >= len(source):
            continue
        aspect_entry = source[source_index]
        timing = _sample_display_timing(
            aspect_entry=aspect_entry,
            transit_dt=transit_dt,
            location=transit_location,
            options=options,
            bucket=str(entry.get("bucket") or ""),
            transit_date_utc_day=transit_date_utc_day,
            natal_birth_signature=natal_birth_signature,
            house_system=options.house_system,
        )
        entry["timing"] = timing

    timeline = _build_display_timeline(featured)
    return {"items": items, "featured": featured, "timeline": timeline}


def _build_window_candidates(
    *,
    transit_bodies: Sequence[Mapping[str, Any]],
    natal_snapshot: Mapping[str, Any],
    aspect_types: Sequence[str],
    orbs: Mapping[str, float],
) -> list[Dict[str, Any]]:
    natal_points: list[Dict[str, Any]] = []
    for body in natal_snapshot.get("bodies") or []:
        lon = body.get("lon")
        if lon is None:
            continue
        natal_points.append({"point": body.get("body"), "lon": lon})
    for angle in (natal_snapshot.get("angles") or {}).values():
        lon = angle.get("lon")
        if lon is None:
            continue
        natal_points.append({"point": angle.get("point"), "lon": lon})

    allowed_types = [t for t in aspect_types if t in ASPECT_ANGLES]
    candidates: list[Dict[str, Any]] = []
    for transit in transit_bodies:
        transit_lon = transit.get("lon")
        if transit_lon is None:
            continue
        body = str(transit.get("body") or "")
        buffer_deg = _candidate_buffer(body)
        for natal in natal_points:
            natal_lon = natal.get("lon")
            if natal_lon is None:
                continue
            for aspect_type in allowed_types:
                orb_max = float(orbs.get(aspect_type, 6.0))
                exact = ASPECT_ANGLES[aspect_type]
                delta = abs(_min_angle_diff(transit_lon - natal_lon) - exact)
                if delta > orb_max + buffer_deg:
                    continue
                strength = clamp01(1 - delta / (orb_max + buffer_deg))
                candidates.append(
                    {
                        "transit_body": body,
                        "natal_point": str(natal.get("point") or ""),
                        "aspect_type": aspect_type,
                        "orb_max": orb_max,
                        "buffer_deg": buffer_deg,
                        "natal_lon": natal_lon,
                        "strength": strength,
                    }
                )
    return candidates


def _sort_candidates(candidates: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
    return sorted(
        candidates,
        key=lambda entry: (
            -float(entry.get("strength") or 0.0),
            float(entry.get("orb_max") or 0.0),
            str(entry.get("transit_body") or ""),
            str(entry.get("natal_point") or ""),
            str(entry.get("aspect_type") or ""),
        ),
    )


def _candidate_buffer(body: str) -> float:
    if body == "Moon":
        return 3.0
    if body in {"Mercury", "Venus", "Mars"}:
        return 2.0
    return 1.0


def _scan_candidate_window(
    *,
    candidate: Mapping[str, Any],
    transit_location: Any,
    start_utc: datetime,
    end_utc: datetime,
    step_hours: int,
    refine_near_exact: bool,
    orb_hysteresis_deg: float,
) -> Dict[str, Any] | None:
    transit_body = str(candidate.get("transit_body") or "")
    natal_point = str(candidate.get("natal_point") or "")
    aspect_type = str(candidate.get("aspect_type") or "")
    orb_max = float(candidate.get("orb_max") or 0.0)
    natal_lon = float(candidate.get("natal_lon") or 0.0)
    exact = ASPECT_ANGLES.get(aspect_type)
    if exact is None:
        return None

    enter_dt: datetime | None = None
    exit_dt: datetime | None = None
    in_window = False
    peaks: list[tuple[datetime, float]] = []
    min_orb = 999.0
    min_dt: datetime | None = None

    prev_orb: float | None = None
    prev_trend: str | None = None
    prev_time: datetime | None = None

    current = start_utc
    while current <= end_utc:
        jd = julian_day(current)
        transit_lon = _transit_lon_at(
            body=transit_body,
            jd_ut=jd,
            location=transit_location,
        )
        if transit_lon is None:
            current += timedelta(hours=step_hours)
            continue
        orb = abs(_min_angle_diff(transit_lon - natal_lon) - exact)
        if not in_window and orb <= orb_max:
            in_window = True
            enter_dt = current
        if in_window and orb > (orb_max + orb_hysteresis_deg):
            in_window = False
            exit_dt = current
        if in_window and orb < min_orb:
            min_orb = orb
            min_dt = current

        trend = prev_trend
        if prev_orb is not None:
            if orb < prev_orb:
                trend = "down"
            elif orb > prev_orb:
                trend = "up"
            if prev_trend == "down" and trend == "up" and prev_time is not None:
                if prev_orb <= orb_max:
                    peaks.append((prev_time, prev_orb))
        prev_orb = orb
        prev_trend = trend
        prev_time = current
        current += timedelta(hours=step_hours)

    if not peaks and min_dt is not None and min_orb <= orb_max:
        peaks.append((min_dt, min_orb))

    if refine_near_exact and peaks:
        refined: list[tuple[datetime, float]] = []
        for peak_time, _ in peaks:
            refined.append(
                _refine_peak(
                    body=transit_body,
                    natal_lon=natal_lon,
                    exact=exact,
                    peak_time=peak_time,
                    location=transit_location,
                )
            )
        peaks = refined

    if enter_dt is None or exit_dt is None or not peaks:
        return None

    peaks_sorted = sorted(peaks, key=lambda item: item[0])
    min_orb = min(item[1] for item in peaks_sorted)
    category = _duration_category(transit_body)
    duration_days = int(round((exit_dt - enter_dt).total_seconds() / 86400))
    confidence = clamp01(1 - (min_orb / (orb_max + 1e-6)))
    domains = _event_domains(transit_body, natal_point)
    event_id = _event_id(transit_body, aspect_type, natal_point)

    return {
        "id": event_id,
        "transit": transit_body,
        "natal": natal_point,
        "aspect": aspect_type,
        "timebox": {
            "enter": enter_dt.date().isoformat(),
            "peaks": [{"t": peak.date().isoformat(), "orb": round(orb, 4)} for peak, orb in peaks_sorted],
            "exit": exit_dt.date().isoformat(),
        },
        "orb": {"min": round(min_orb, 4), "max_allowed": orb_max},
        "duration_days": duration_days,
        "category": category,
        "domains": domains,
        "confidence": round(confidence, 3),
        "polarity": _aspect_polarity(aspect_type),
    }


def _refine_peak(
    *,
    body: str,
    natal_lon: float,
    exact: float,
    peak_time: datetime,
    location: Any,
) -> tuple[datetime, float]:
    refine_step = 6
    window = timedelta(hours=24)
    start = peak_time - window
    end = peak_time + window
    best_orb = 999.0
    best_time = peak_time
    current = start
    while current <= end:
        jd = julian_day(current)
        transit_lon = _transit_lon_at(body=body, jd_ut=jd, location=location)
        if transit_lon is not None:
            orb = abs(_min_angle_diff(transit_lon - natal_lon) - exact)
            if orb < best_orb:
                best_orb = orb
                best_time = current
        current += timedelta(hours=refine_step)
    return best_time, best_orb


def _transit_lon_at(*, body: str, jd_ut: float, location: Any) -> float | None:
    if body == "South Node":
        result = swe.calc_ut(jd_ut, PLANET_CODES["North Node"])
        values = result[0] if isinstance(result[0], (list, tuple)) else result
        lon = values[0] if len(values) > 0 else None
        return (float(lon) + 180) % 360 if lon is not None else None
    if body == "Fortune":
        cusps_raw, ascmc = swe.houses(jd_ut, location.latitude, location.longitude, b"P")
        asc = float(ascmc[0] % 360)
        sun = _lon_for_body("Sun", jd_ut)
        moon = _lon_for_body("Moon", jd_ut)
        if sun is None or moon is None:
            return None
        return (asc + moon - sun) % 360
    planet_id = PLANET_CODES.get(body)
    if planet_id is None:
        return None
    result = swe.calc_ut(jd_ut, planet_id)
    values = result[0] if isinstance(result[0], (list, tuple)) else result
    lon = values[0] if len(values) > 0 else None
    return float(lon) if lon is not None else None


def _lon_for_body(body: str, jd_ut: float) -> float | None:
    planet_id = PLANET_CODES.get(body)
    if planet_id is None:
        return None
    result = swe.calc_ut(jd_ut, planet_id)
    values = result[0] if isinstance(result[0], (list, tuple)) else result
    lon = values[0] if len(values) > 0 else None
    return float(lon) if lon is not None else None


def _event_domains(transit_body: str, natal_point: str) -> list[str]:
    domains = []
    domains.extend(DOMAIN_RULES.get(transit_body, []))
    domains.extend(DOMAIN_RULES.get(natal_point, []))
    out: list[str] = []
    for value in domains:
        if value not in out:
            out.append(value)
    return out


def _event_id(transit_body: str, aspect_type: str, natal_point: str) -> str:
    return f"tr.{_slug(transit_body)}.{_slug(aspect_type)}.{_slug(natal_point)}"


def _slug(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("/", "_")


def _aspect_polarity(aspect_type: str) -> str:
    if aspect_type in {"square", "opposition"}:
        return "hard"
    if aspect_type in {"trine", "sextile"}:
        return "soft"
    return "neutral"


def _build_window_presentable(events: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    timeline: list[Dict[str, Any]] = []
    cards: list[Dict[str, Any]] = []
    trackers: list[Dict[str, Any]] = []

    for event in events:
        peak = (event.get("timebox") or {}).get("peaks") or []
        peak_time = peak[0]["t"] if peak else None
        label = _event_headline(event)
        timeline.append(
            {
                "id": event.get("id"),
                "label": label,
                "start": (event.get("timebox") or {}).get("enter"),
                "peak": peak_time,
                "end": (event.get("timebox") or {}).get("exit"),
                "category": event.get("category"),
                "intensity_curve": "ramp_peak_fade",
                "confidence": event.get("confidence"),
            }
        )

        copy = _event_copy(event)
        cards.append(
            {
                "id": event.get("id"),
                "headline": label,
                "domains": event.get("domains") or [],
                "copy": copy,
                "timebox": {
                    "start": (event.get("timebox") or {}).get("enter"),
                    "peak": peak_time,
                    "end": (event.get("timebox") or {}).get("exit"),
                },
                "intensity": event.get("confidence"),
                "top_evidence": [
                    {
                        "transit": event.get("transit"),
                        "aspect": event.get("aspect"),
                        "natal": event.get("natal"),
                        "orb_at_peak": ((event.get("timebox") or {}).get("peaks") or [{}])[0].get("orb"),
                    }
                ],
            }
        )

    return {"timeline": timeline, "cards": cards, "trackers": trackers}


def _event_headline(event: Mapping[str, Any]) -> str:
    body = str(event.get("transit") or "")
    if body == "Pluto":
        return "Yön değişimi"
    if body == "Saturn":
        return "Disiplin ve yük testi"
    if body == "Neptune":
        return "Belirsizlik ve çözülme"
    return f"{body} etkisi"


def _event_copy(event: Mapping[str, Any]) -> Dict[str, Any]:
    body = str(event.get("transit") or "")
    polarity = str(event.get("polarity") or "")
    if body == "Saturn" and polarity == "hard":
        return {
            "felt_sense": "Yavaşlama ve ağırlık hissi artabilir.",
            "suggestion": "Küçük ama sağlam adımlara odaklan.",
            "watch_for": ["aşırı kendini eleştirme"],
        }
    if body == "Neptune" and polarity == "hard":
        return {
            "felt_sense": "Belirsizlik ve dağılma hissi oluşabilir.",
            "suggestion": "Net olmayan konularda kesin karar alma.",
            "watch_for": ["kaçış", "idealizasyon"],
        }
    if body == "Pluto":
        return {
            "felt_sense": "Kontrol ihtiyacı ile teslimiyet arasında gidip gelme.",
            "suggestion": "Direnç yerine dönüşümü izle.",
            "watch_for": ["güç savaşları"],
        }
    return {
        "felt_sense": "Bazı temalar daha görünür hale gelebilir.",
        "suggestion": "Ritmi zorlamadan ilerle.",
        "watch_for": ["aşırı baskı", "aceleci kararlar"],
    }


def _estimate_duration(entry: Mapping[str, Any], options: TransitOptions) -> Dict[str, Any]:
    transit_body = str((entry.get("transit") or {}).get("body") or "")
    orb_max = float(options.orbs.get(str(entry.get("type") or ""), 6.0))
    speed = (entry.get("transit") or {}).get("speed")
    raw = (2 * orb_max) / (abs(speed) + 1e-6) if speed is not None else 0.0
    category = _duration_category(transit_body)
    if category == "short":
        estimate = min(round(raw), 5)
    elif category == "medium":
        estimate = min(round(raw), 45)
    else:
        estimate = min(round(raw), 365)
    return {"category": category, "estimate_days": int(max(1, estimate))}


def _duration_full(
    body: str | None,
    *,
    entry_speed: float | None,
    orb: float,
    orb_max: float,
    phase: str | None,
) -> tuple[Dict[str, Any] | None, str | None]:
    if entry_speed is None:
        return None, "static_or_unknown_speed"
    if abs(entry_speed) < 0.005:
        return None, "too_slow_for_estimate"
    speed = abs(entry_speed) + 1e-6
    total_window = int(round((2 * orb_max) / speed))
    to_exact = int(round(orb / speed))
    if phase == "applying":
        to_exit = int(round((orb + orb_max) / speed))
    else:
        to_exit = int(round(max(0.0, orb_max - orb) / speed))
    category = _duration_category(str(body or ""))
    if category == "short":
        total_window = min(total_window, 5)
    elif category == "medium":
        total_window = min(total_window, 45)
    else:
        total_window = min(total_window, 365)
    return (
        {
            "category": category,
            "estimate_days_to_exact": max(0, to_exact),
            "estimate_days_to_exit": max(0, to_exit),
            "estimate_days_total_window": max(1, total_window),
        },
        None,
    )


def _duration_category(body: str) -> str:
    if body in {"Moon", "ASC", "MC", "DSC", "IC", "Vertex", "Fortune", "Lilith"}:
        return "short"
    if body in {"Sun", "Mercury", "Venus", "Mars", "Jupiter"}:
        return "medium"
    if body in {"Saturn", "Uranus", "Neptune", "Pluto", "North Node", "South Node", "Chiron"}:
        return "long"
    return "long"


def _derive_tags(entry: Mapping[str, Any]) -> list[str]:
    tags = []
    natal_body = str((entry.get("natal") or {}).get("body") or "")
    if natal_body in {"Sun", "ASC", "MC"}:
        tags.append("identity")
    if entry.get("polarity") == "hard":
        tags.append("pressure")
    elif entry.get("polarity") == "soft":
        tags.append("support")
    return tags


def _highlight_title(body: str, items: Sequence[Mapping[str, Any]]) -> str:
    if not items:
        return "Transit highlights"
    if body == "Saturn":
        return "Disiplin ve yük testi"
    if body == "Jupiter":
        return "Genişleme ve fırsatlar"
    if body == "Mars":
        return "Eylem ve hızlanma"
    return f"{body} hareketi"


def _why_important(entry: Mapping[str, Any]) -> str:
    natal_body = str((entry.get("natal") or {}).get("body") or "")
    if natal_body == "Sun":
        return "Kimlik/enerji üzerinde baskı, sorumluluk artışı"
    if natal_body == "Moon":
        return "Duygusal dalgalanma ve güven ihtiyacı"
    if natal_body == "Mercury":
        return "Zihinsel yoğunluk ve karar baskısı"
    if natal_body == "Venus":
        return "İlişkilerde hassasiyet ve denge ihtiyacı"
    if natal_body == "Mars":
        return "Eylem ve irade sınavı"
    return "Tema odaklanması ve farkındalık artışı"


def _normalize_angle_name(value: str | None) -> str:
    if not value:
        return ""
    key = str(value).strip().lower()
    mapping = {
        "asc": "ASC",
        "ascendant": "ASC",
        "mc": "MC",
        "medium_coeli": "MC",
        "midheaven": "MC",
        "dsc": "DSC",
        "descendant": "DSC",
        "ic": "IC",
        "imum_coeli": "IC",
    }
    return mapping.get(key, str(value))


def _normalize_selector(value: Any) -> str:
    return str(value or "").strip().lower().replace(" ", "_")


def _natal_house_map(natal_snapshot: Mapping[str, Any]) -> Dict[str, int]:
    mapping: Dict[str, int] = {}
    for body in natal_snapshot.get("bodies") or []:
        name = body.get("body")
        house = body.get("house")
        if name and isinstance(house, int):
            mapping[str(name)] = house
    return mapping


def _transit_house_map(house_overlays: Sequence[Mapping[str, Any]]) -> Dict[str, int]:
    mapping: Dict[str, int] = {}
    for entry in house_overlays:
        body = entry.get("transit_body")
        house = entry.get("natal_house")
        if body and isinstance(house, int):
            mapping[str(body)] = house
    return mapping


def _display_tags(natal_point: str, house_map: Mapping[str, int]) -> list[str]:
    if natal_point == "ASC":
        return ["self"]
    if natal_point == "MC":
        return ["career"]
    if natal_point == "DSC":
        return ["relationships"]
    if natal_point == "IC":
        return ["home"]
    house = house_map.get(natal_point)
    if house is None:
        return []
    if house in {1, 2, 3}:
        return ["self"]
    if house == 4:
        return ["home"]
    if house in {5, 7, 8}:
        return ["relationships"]
    if house in {9, 10, 11}:
        return ["career"]
    if house == 12:
        return ["inner"]
    return []


def _aspect_tag_map(aspect_type: str) -> list[str]:
    mapping = {
        "conjunction": ["amplify"],
        "square": ["pressure", "friction"],
        "opposition": ["pressure", "tension"],
        "trine": ["support", "flow"],
        "sextile": ["support", "opportunity"],
    }
    return mapping.get(aspect_type, [])


def _planet_tag_map(body: str) -> list[str]:
    mapping = {
        "Neptune": ["fog", "idealization", "boundaries", "dissolve"],
        "Uranus": ["shock", "freedom", "change"],
        "Pluto": ["intensity", "power", "transform"],
        "Saturn": ["limits", "responsibility", "discipline"],
        "Jupiter": ["growth", "expansion"],
        "Mars": ["drive", "conflict"],
        "Venus": ["love", "values"],
        "Mercury": ["mind", "communication"],
        "Moon": ["mood", "needs"],
    }
    return mapping.get(body, [])


def _merge_tags(*tag_lists: Sequence[str]) -> list[str]:
    out: list[str] = []
    for tags in tag_lists:
        for tag in tags:
            if tag not in out:
                out.append(tag)
    return out


def _display_phase(orb: float, orb_limit: float, base_phase: str | None) -> str:
    exactish_limit = min(0.2, orb_limit * 0.05)
    if orb <= exactish_limit:
        return "exactish"
    if base_phase in {"applying", "separating"}:
        return str(base_phase)
    return "applying"


def _display_event_id(
    transit_body: str,
    aspect_type: str,
    natal_point: str,
    scope: str,
    transit_dt: datetime,
) -> str:
    event_key = f"{transit_body}|{aspect_type}|{natal_point}|{scope}"
    return hashlib.sha1(event_key.encode("utf-8")).hexdigest()


def _sort_display_items(items: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
    return sorted(
        items,
        key=lambda entry: (
            -float(entry.get("strength") or 0.0),
            float(entry.get("orb_deg") or 0.0),
            str(entry.get("label") or ""),
        ),
    )


def _select_featured_indices(items: Sequence[Mapping[str, Any]]) -> list[int]:
    bucket_rank = {"long": 0, "medium": 1, "short": 2}
    ranked = sorted(
        enumerate(items),
        key=lambda pair: (
            bucket_rank.get(str(pair[1].get("bucket") or ""), 3),
            -float(pair[1].get("strength") or 0.0),
            float(pair[1].get("orb_deg") or 0.0),
        ),
    )
    limit = 5 if len(items) >= 5 else len(items)
    return [idx for idx, _ in ranked[: max(3, limit)]]


def _build_display_timeline(items: Sequence[Mapping[str, Any]]) -> list[Dict[str, Any]]:
    timeline: list[Dict[str, Any]] = []
    for entry in items:
        timing = entry.get("timing")
        if not timing:
            continue
        timeline.append(
            {
                "id": entry.get("event_id"),
                "label": entry.get("label"),
                "start": timing.get("entry_date_utc"),
                "peak": timing.get("peak_date_utc"),
                "end": timing.get("exit_date_utc"),
                "category": entry.get("bucket"),
                "intensity_curve": "ramp_peak_fade",
                "confidence": timing.get("confidence"),
            }
        )
    return timeline


def _sample_display_timing(
    *,
    aspect_entry: Mapping[str, Any],
    transit_dt: datetime,
    location: Any,
    options: TransitOptions,
    bucket: str,
    transit_date_utc_day: str,
    natal_birth_signature: str,
    house_system: str,
) -> Dict[str, Any] | None:
    transit_body = str((aspect_entry.get("transit") or {}).get("body") or "")
    natal_lon = (aspect_entry.get("natal") or {}).get("lon")
    if natal_lon is None:
        return None
    aspect_type = str(aspect_entry.get("type") or "")
    orb_limit = float(options.orbs.get(aspect_type, 6.0))

    window_days, step_hours = _timing_window(bucket)
    window_days = min(365, window_days)
    timing_cache_key = _build_timing_cache_key(
        transit_date_utc_day=transit_date_utc_day,
        house_system=house_system,
        natal_birth_signature=natal_birth_signature,
        transit_body=transit_body,
        aspect_type=aspect_type,
        natal_lon=float(natal_lon),
        bucket=bucket,
        step_hours=step_hours,
        window_days=window_days,
    )
    if timing_cache_key in _TIMING_CACHE:
        cached = _TIMING_CACHE[timing_cache_key]
        if cached is None:
            return None
        return dict(cached)

    start = transit_dt - timedelta(days=window_days)
    end = transit_dt + timedelta(days=window_days)

    entry_time: datetime | None = None
    exit_time: datetime | None = None
    peak_time: datetime | None = None
    min_orb = 999.0

    current = start
    seen_entry = False
    while current <= end:
        jd = julian_day(current)
        transit_lon = _transit_lon_at(body=transit_body, jd_ut=jd, location=location)
        if transit_lon is None:
            current += timedelta(hours=step_hours)
            continue
        orb = abs(_min_angle_diff(transit_lon - natal_lon) - ASPECT_ANGLES.get(aspect_type, 0))
        if orb <= orb_limit and not seen_entry:
            entry_time = current
            seen_entry = True
        if orb < min_orb:
            min_orb = orb
            peak_time = current
        if seen_entry and peak_time is not None and orb > orb_limit:
            exit_time = current
            break
        current += timedelta(hours=step_hours)

    if entry_time is None and peak_time is None:
        _timing_cache_set(timing_cache_key, None)
        return None

    confidence = 0.3
    timing_note = None
    if entry_time and peak_time and exit_time:
        confidence = 0.9
    elif entry_time and peak_time:
        confidence = 0.6
        if exit_time is None:
            timing_note = "exit_not_found_in_window"
    elif entry_time is None and peak_time:
        confidence = 0.6
    if entry_time and exit_time is None and timing_note is None:
        timing_note = "exit_not_found_in_window"

    peaks: list[str] = []
    if peak_time is not None:
        peaks.append(peak_time.isoformat())
    if not peaks:
        timing_note = _append_timing_note(timing_note, "missing_peaks")

    if exit_time is not None and exit_time < transit_dt:
        result = {
            "entry_date_utc": None,
            "peak_date_utc": None,
            "exit_date_utc": None,
            "confidence": round(confidence, 2),
            "orb_limit_deg": orb_limit,
            "step_hours": step_hours,
            "window_days": window_days,
            "peaks": peaks,
            "timing_note": "timing_out_of_range_for_transit_date",
            "debug": {
                "transit_date_used_for_orb": transit_dt.isoformat(),
                "transit_date_used_for_timing": transit_dt.isoformat(),
                "timing_cache_key": timing_cache_key,
                "timing_computed_at_utc": datetime.now(timezone.utc).isoformat(),
            },
        }
        _timing_cache_set(timing_cache_key, result)
        return result

    phase = _display_phase(float(aspect_entry.get("orb") or 9.9), orb_limit, aspect_entry.get("phase"))
    if peak_time is not None and phase in {"exact", "exactish"}:
        delta_sec = abs((peak_time - transit_dt).total_seconds())
        if delta_sec > (7 * 24 * 3600):
            timing_note = _append_timing_note(timing_note, "peak_far_from_transit_date")

    result = {
        "entry_date_utc": entry_time.isoformat() if entry_time else None,
        "peak_date_utc": peak_time.isoformat() if peak_time else None,
        "exit_date_utc": exit_time.isoformat() if exit_time else None,
        "confidence": round(confidence, 2),
        "orb_limit_deg": orb_limit,
        "step_hours": step_hours,
        "window_days": window_days,
        "peaks": peaks,
        "timing_note": timing_note,
        "debug": {
            "transit_date_used_for_orb": transit_dt.isoformat(),
            "transit_date_used_for_timing": transit_dt.isoformat(),
            "timing_cache_key": timing_cache_key,
            "timing_computed_at_utc": datetime.now(timezone.utc).isoformat(),
        },
    }
    _timing_cache_set(timing_cache_key, result)
    return result


def _timing_window(bucket: str) -> tuple[int, int]:
    if bucket == "long":
        return 365, 72
    if bucket == "medium":
        return 60, 24
    return 14, 6


def _build_timing_cache_key(
    *,
    transit_date_utc_day: str,
    house_system: str,
    natal_birth_signature: str,
    transit_body: str,
    aspect_type: str,
    natal_lon: float,
    bucket: str,
    step_hours: int,
    window_days: int,
) -> str:
    raw = "|".join(
        [
            transit_date_utc_day,
            str(house_system or "").lower(),
            natal_birth_signature,
            str(transit_body or "").lower(),
            str(aspect_type or "").lower(),
            f"{float(natal_lon):.6f}",
            str(bucket or "").lower(),
            str(step_hours),
            str(window_days),
        ]
    )
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def _timing_cache_set(key: str, value: Dict[str, Any] | None) -> None:
    if len(_TIMING_CACHE) >= _TIMING_CACHE_MAX:
        _TIMING_CACHE.pop(next(iter(_TIMING_CACHE)), None)
    _TIMING_CACHE[key] = dict(value) if isinstance(value, dict) else None


def _natal_birth_signature(natal_snapshot: Mapping[str, Any]) -> str:
    payload = {
        "datetime_utc": natal_snapshot.get("datetime_utc"),
        "timezone": natal_snapshot.get("timezone"),
        "angles": natal_snapshot.get("angles"),
        "house_cusps": natal_snapshot.get("house_cusps"),
    }
    raw = str(payload)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def _append_timing_note(base: str | None, token: str) -> str:
    seed = str(base or "").strip()
    if not seed:
        return token
    parts = [p.strip() for p in seed.split(";") if p.strip()]
    if token in parts:
        return seed
    parts.append(token)
    return ";".join(parts)


def _aspect_phase(
    body: str | None,
    transit_lon: float,
    natal_lon: float,
    exact: float,
    transit_jd: float,
) -> str:
    if not body:
        return "unknown"
    next_lon = _next_transit_lon(body, transit_jd)
    if next_lon is None:
        return "unknown"
    orb_now = abs(_min_angle_diff(transit_lon - natal_lon) - exact)
    orb_next = abs(_min_angle_diff(next_lon - natal_lon) - exact)
    return "applying" if orb_next < orb_now else "separating"


def _next_transit_lon(body: str, jd_ut: float) -> float | None:
    if body == "South Node":
        result = swe.calc_ut(jd_ut + 1.0, PLANET_CODES["North Node"])
        values = result[0] if isinstance(result[0], (list, tuple)) else result
        lon = values[0] if len(values) > 0 else None
        if lon is None:
            return None
        return (float(lon) + 180) % 360
    planet_id = PLANET_CODES.get(body)
    if planet_id is None:
        return None
    result = swe.calc_ut(jd_ut + 1.0, planet_id)
    values = result[0] if isinstance(result[0], (list, tuple)) else result
    lon = values[0] if len(values) > 0 else None
    return float(lon) if lon is not None else None


def _orb_parts(orb: float) -> Dict[str, int]:
    deg = int(orb)
    minute = int(round((orb - deg) * 60))
    if minute == 60:
        minute = 0
        deg += 1
    return {"deg": deg, "min": minute}


def _sign_from_lon(lon: float | None) -> str | None:
    if lon is None:
        return None
    return get_zodiac_sign(float(lon))


def _style_from_sign(sign: str | None) -> Dict[str, str] | None:
    if not sign:
        return None
    element = ELEMENT_MAP.get(sign)
    modality = MODALITY_MAP.get(sign)
    if not element or not modality:
        return None
    return {
        "element": element.lower(),
        "modality": modality.lower(),
    }


def _body_lon(body: str, bodies: Sequence[Mapping[str, Any]]) -> float | None:
    for entry in bodies:
        if entry.get("body") == body:
            return entry.get("lon")
    return None


def _min_angle_diff(value: float) -> float:
    return abs((value + 180) % 360 - 180)
