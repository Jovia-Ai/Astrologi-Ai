"""API route for transit engine v1."""
from __future__ import annotations

from pathlib import Path
import copy
import hashlib
import os
from datetime import date as date_type, time as time_type
from typing import Any, Dict, List, Mapping, Optional, Tuple, Literal
import json
import logging
from functools import lru_cache
from time import perf_counter

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from app.engine.transit_engine import (
    build_transit_event_timing,
    build_transit_report,
    build_transit_window_report,
)
from app.transit.interpret.interpretation_engine_v1 import (
    ContentStore,
    diversify_where_short,
    interpret_items,
)
from app.transit.present.public_builder import build_public_response
from app.transit.calendar_builder import build_transit_calendar_public
from app.transit.calendar.best_times import best_times_from_calendar_payload
from app.transit.serialize.calendar_serializers import to_ui_day_detail, to_ui_calendar
from app.transit.interpret.promise_builder_v1 import build_promise_model
from app.transit.astro_event_v2 import (
    build_personal_multi_event_payload,
    build_solar_year_theme,
    enrich_legacy_aspect_item,
)
from app.transit.narrative import (
    assemble_blocks,
    build_calendar_day,
    build_feed_snippet,
    build_personal_transit,
    build_space_hub,
)
from app.transit.narrative.coverage import build_period_coverage
from app.transit.narrative.selection import select_event_ids
from app.transit.narrative.generator import make_birth_fingerprint

router = APIRouter(tags=["transits"])
logger = logging.getLogger(__name__)


def _json_safe(value: Any) -> Any:
    if isinstance(value, set):
        return sorted(value)
    return str(value)


def _payload_size_bytes(payload: Any) -> int:
    return len(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            default=_json_safe,
        ).encode("utf-8")
    )


def _log_transit_timing(
    *,
    endpoint: str,
    request: "TransitNarrativeRequest",
    response: Mapping[str, Any],
    duration_ms: float,
) -> None:
    if not os.getenv("ENABLE_TIMING_LOGS", "true").strip().lower() in {"1", "true", "yes", "on"}:
        return
    start_date = _parse_iso_date(request.start, field_name="start")
    end_date = _parse_iso_date(request.end, field_name="end")
    range_days = (end_date - start_date).days + 1
    logger.info(
        "transit_timing %s",
        json.dumps(
            {
                "endpoint": endpoint,
                "cache_status": "not_cached",
                "duration_ms": round(duration_ms, 3),
                "range_start": start_date.isoformat(),
                "range_end": end_date.isoformat(),
                "range_days": range_days,
                "selected_date": request.selected_date,
                "transit_window": "monthly_range_with_selected_day"
                if request.selected_date and range_days > 1
                else "single_day"
                if range_days == 1
                else "range_only",
                "include_best_times": bool(request.include_best_times),
                "top": int(request.top),
                "window": int(request.window),
                "payload_bytes": _payload_size_bytes(response),
            },
            ensure_ascii=False,
            sort_keys=True,
        ),
    )

def _normalize_calendar_view(view: str) -> Literal["public", "internal", "both"]:
    """
    Backward-compatible view mapper.
    Old:
      - ui   => public
      - full => internal
    New:
      - public | internal | both
    """
    v = (view or "").strip().lower()
    if v == "ui":
        return "public"
    if v == "full":
        return "internal"
    if v in {"public", "internal", "both"}:
        return v
    return "public"


def _parse_iso_date(value: str, *, field_name: str) -> date_type:
    try:
        return date_type.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "validation_error",
                "message": f"{field_name} must be in YYYY-MM-DD format.",
            },
        ) from exc


def _parse_best_times_intent(
    intent_raw: str,
    sub_intent_raw: str | None,
) -> tuple[str, str | None, str]:
    intent_value = (intent_raw or "").strip().lower()
    sub_value = (sub_intent_raw or "").strip().lower() or None

    # Accept both:
    # - beauty_care + sub_intent=nourish
    # - beauty_care_nourish (single intent key)
    if intent_value.startswith("beauty_care_"):
        suffix = intent_value.removeprefix("beauty_care_")
        if suffix in {"nourish", "reduce", "procedure"}:
            return "beauty_care", suffix, f"beauty_care_{suffix}"
        return "beauty_care", None, "beauty_care_nourish"

    if intent_value == "beauty_care":
        if sub_value in {"nourish", "reduce", "procedure"}:
            return "beauty_care", sub_value, f"beauty_care_{sub_value}"
        return "beauty_care", None, "beauty_care_nourish"

    if not intent_value:
        return "beauty_care", "nourish", "beauty_care_nourish"

    return intent_value, sub_value, intent_value


def _normalize_best_times_public_payload(
    *,
    raw: Mapping[str, Any],
    start: str,
    end: str,
    tz: str,
    intent: str,
) -> Dict[str, Any]:
    def _intent_label(value: str) -> str:
        mapping = {
            "general": "Genel",
            "beauty_care_nourish": "Besle",
            "beauty_care_reduce": "Azalt",
            "beauty_care_procedure": "Islem",
        }
        return mapping.get(value, value.replace("_", " ").title())

    def _sort_key_date(value: Any) -> tuple[int, str]:
        text = str(value or "")
        return (0 if text else 1, text)

    def _normalize_caution_tags(item: Mapping[str, Any]) -> list[str]:
        tags = item.get("caution_tags")
        if isinstance(tags, list):
            return [str(tag) for tag in tags if str(tag).strip()]
        gates = item.get("gates")
        if isinstance(gates, list):
            return [str(tag) for tag in gates if str(tag).strip()]
        critical_reason = item.get("critical_reason")
        if isinstance(critical_reason, list):
            return [str(tag) for tag in critical_reason if str(tag).strip()]
        return []

    def _normalize_reason(item: Mapping[str, Any]) -> str:
        for key in ("reason", "summary", "recommendation_user", "rating_reason_user"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        why = item.get("why_support")
        if isinstance(why, list):
            compact = [str(v).strip() for v in why if str(v).strip()]
            if compact:
                return " ".join(compact[:2])
        return ""

    normalized_candidates: list[Dict[str, Any]] = []
    for candidate in raw.get("candidates") or []:
        if not isinstance(candidate, Mapping):
            continue
        date_value = str(candidate.get("date") or "").strip()
        if not date_value:
            continue
        score_value = candidate.get("score")
        try:
            score = max(0.0, min(1.0, float(score_value)))
        except (TypeError, ValueError):
            score = 0.0
        label = candidate.get("label")
        if not isinstance(label, str) or not label.strip():
            rating = candidate.get("final_rating") or candidate.get("rating")
            label = "Best day" if isinstance(rating, int) and rating >= 3 else None
        top_event_ids = candidate.get("top_event_ids")
        if not isinstance(top_event_ids, list):
            top_event_ids = candidate.get("event_ids")
        normalized_candidates.append(
            {
                "date": date_value,
                "score": round(score, 3),
                "label": label.strip() if isinstance(label, str) and label.strip() else None,
                "reason": _normalize_reason(candidate),
                "caution_tags": _normalize_caution_tags(candidate),
                "top_event_ids": [
                    str(event_id)
                    for event_id in (top_event_ids or [])
                    if str(event_id).strip()
                ][:5],
            }
        )

    normalized_candidates.sort(
        key=lambda item: (-float(item.get("score") or 0.0), _sort_key_date(item.get("date"))),
    )

    normalized_windows: list[Dict[str, Any]] = []
    for window in raw.get("windows") or []:
        if not isinstance(window, Mapping):
            continue
        start_value = str(window.get("start") or "").strip()
        end_value = str(window.get("end") or "").strip()
        if not start_value or not end_value:
            continue
        score_value = window.get("score")
        if score_value is None:
            score_value = window.get("avg_score")
        try:
            score = max(0.0, min(1.0, float(score_value)))
        except (TypeError, ValueError):
            score = 0.0
        label = window.get("label")
        if not isinstance(label, str) or not label.strip():
            label = window.get("action_type")
        normalized_windows.append(
            {
                "start": start_value,
                "end": end_value,
                "score": round(score, 3),
                "label": label.strip() if isinstance(label, str) and label.strip() else None,
                "reason": _normalize_reason(window),
                "caution_tags": _normalize_caution_tags(window),
            }
        )

    normalized_windows.sort(
        key=lambda item: (
            -float(item.get("score") or 0.0),
            _sort_key_date(item.get("start")),
        ),
    )

    return {
        "range": {"start": start, "end": end, "tz": tz},
        "intent": intent,
        "intent_label": _intent_label(intent),
        "candidates": normalized_candidates,
        "windows": normalized_windows,
    }

_CONTENT_STORE: ContentStore | None = None
_PERIOD_SPACE_PACK: Dict[str, Any] | None = None
DEFAULT_PERIOD_DAYS = 120
DEFAULT_PERIOD_STEP_HOURS = 24
DEFAULT_PERIOD_MAX_EVENTS = 20
DEFAULT_PERIOD_REFINE_NEAR_EXACT = True
DEFAULT_PERIOD_ORB_HYSTERESIS = 0.2


def _load_content_store() -> ContentStore:
    global _CONTENT_STORE
    if _CONTENT_STORE is None:
        base_path = Path(__file__).resolve().parents[2] / "transit" / "content" / "tr"
        with (base_path / "transit_templates.v1.json").open("r", encoding="utf-8") as handle:
            templates = json.load(handle)
        with (base_path / "promise_claims.v1.json").open("r", encoding="utf-8") as handle:
            claims = json.load(handle)
        with (base_path / "point_affinity.v1.json").open("r", encoding="utf-8") as handle:
            point_affinity = json.load(handle)
        with (base_path / "tag_map.v1.json").open("r", encoding="utf-8") as handle:
            tag_map = json.load(handle)
        upper_meaning = _load_upper_meaning_pack(base_path)
        style_do = _load_style_do_pack(base_path)
        approach_pack = _load_approach_pack(base_path)
        mapping = {"point_affinity": point_affinity, **tag_map}
        _CONTENT_STORE = ContentStore(templates, claims, mapping, upper_meaning, style_do, approach_pack)
    return _CONTENT_STORE


@lru_cache(maxsize=1)
def _load_upper_meaning_pack(base_path: Path) -> Dict[str, Any]:
    with (base_path / "upper_meaning.v1.json").open("r", encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=1)
def _load_style_do_pack(base_path: Path) -> Dict[str, Any]:
    with (base_path / "style_do.v1.json").open("r", encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=1)
def _load_approach_pack(base_path: Path) -> Dict[str, Any]:
    with (base_path / "approach_pack.v1.json").open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_period_space_pack() -> Dict[str, Any]:
    global _PERIOD_SPACE_PACK
    if _PERIOD_SPACE_PACK is None:
        base_path = (
            Path(__file__).resolve().parents[2] / "transit" / "content" / "tr" / "period_space"
        )
        pack = {}
        with (base_path / "house_labels.json").open("r", encoding="utf-8") as handle:
            pack["house_labels"] = json.load(handle)
        with (base_path / "house_story_templates.json").open("r", encoding="utf-8") as handle:
            pack["house_story"] = json.load(handle)
        with (base_path / "axis_pack.json").open("r", encoding="utf-8") as handle:
            pack["axis_pack"] = json.load(handle)
        with (base_path / "housepair_interactions.json").open("r", encoding="utf-8") as handle:
            pack["housepair_pack"] = json.load(handle)
        _PERIOD_SPACE_PACK = pack
    return _PERIOD_SPACE_PACK or {}


def _default_house_labels() -> Dict[int, str]:
    return {
        1: "kimlik ve durus",
        2: "para ve ozdeger",
        3: "zihin ve iletisim",
        4: "ev ve ic guven",
        5: "yaraticilik ve keyif",
        6: "ritim ve saglik",
        7: "iliski ve ortaklik",
        8: "yakinlik ve guven",
        9: "yon ve anlam",
        10: "kariyer ve gorunurluk",
        11: "cevre ve gelecek plani",
        12: "ic dunya ve cozunme",
    }


def _house_labels_from_pack(pack: Dict[str, Any]) -> Dict[int, str]:
    raw = pack.get("house_labels") or {}
    labels: Dict[int, str] = {}
    for key, label in raw.items():
        if not key.startswith("house_"):
            continue
        try:
            house_num = int(key.split("_", 1)[1])
        except ValueError:
            continue
        labels[house_num] = str(label)
    return labels or _default_house_labels()


def _natal_house_map_from_payload(natal: Mapping[str, Any]) -> Dict[str, int]:
    mapping: Dict[str, int] = {}
    for body in natal.get("bodies") or []:
        name = body.get("body")
        house = body.get("house")
        if name and isinstance(house, int):
            mapping[str(name)] = house
    return mapping


def _window_items_for_period_space(
    window_report: Mapping[str, Any],
    *,
    natal: Mapping[str, Any],
) -> List[Dict[str, Any]]:
    events = window_report.get("events") or []
    natal_house_map = _natal_house_map_from_payload(natal)
    items: List[Dict[str, Any]] = []
    for event in events:
        transit_body = event.get("transit")
        natal_point = event.get("natal")
        items.append(
            {
                "event_id": event.get("id"),
                "bucket": event.get("category"),
                "transit_body": transit_body,
                "natal_point": natal_point,
                "strength": event.get("confidence"),
                "houses": {
                    "natal_point_house": natal_house_map.get(natal_point),
                    "transit_in_natal_house": None,
                },
            }
        )
    return items


def _build_content_debug(items: List[Dict[str, Any]], content_store: ContentStore) -> Dict[str, Any]:
    templates = content_store.templates or {}
    missing_keys: set[str] = set()
    resolved_exact = 0
    resolved_mid = 0
    resolved_fallback = 0

    resolved_keys_top: list[Dict[str, Any]] = []
    for item in sorted(items, key=lambda it: -float(it.get("strength") or 0.0))[:10]:
        wanted = _format_key(item.get("transit_body"), item.get("aspect"), item.get("natal_point"))
        used = ((item.get("interpretation") or {}).get("content_ref") or {}).get("key")
        resolved_keys_top.append(
            {
                "event_id": item.get("event_id"),
                "wanted": wanted.lower(),
                "used": str(used or "").lower(),
            }
        )

    for item in items:
        transit_body = item.get("transit_body")
        aspect = item.get("aspect")
        natal_point = item.get("natal_point")
        wanted = _format_key(transit_body, aspect, natal_point)
        used = ((item.get("interpretation") or {}).get("content_ref") or {}).get("key")
        polarity = item.get("polarity")

        if wanted.lower() not in templates:
            missing_keys.add(wanted.lower())

        if str(used or "").lower() == wanted.lower():
            resolved_exact += 1
        elif str(used or "").lower() == _format_key(transit_body, aspect, "ANY").lower():
            resolved_mid += 1
        else:
            resolved_fallback += 1

    return {
        "resolved_keys_top": resolved_keys_top,
        "missing_keys": sorted(missing_keys),
        "coverage": {
            "items_total": len(items),
            "resolved_exact": resolved_exact,
            "resolved_mid": resolved_mid,
            "resolved_fallback": resolved_fallback,
        },
    }


def _build_presentable_summary(items: List[Dict[str, Any]], featured: List[Dict[str, Any]]) -> Dict[str, Any]:
    theme_scores: Dict[str, float] = {}
    for item in featured or []:
        themes = ((item.get("interpretation") or {}).get("themes") or []) or []
        strength = float(item.get("strength") or 0.0)
        for theme in themes:
            theme_scores[theme] = theme_scores.get(theme, 0.0) + strength

    sorted_scores = sorted(theme_scores.items(), key=lambda kv: kv[1], reverse=True)
    max_score = sorted_scores[0][1] if sorted_scores else 1.0
    theme_scores_list = [
        {"theme": theme, "score": round(score / max_score, 3)} for theme, score in sorted_scores
    ]
    main_theme = sorted_scores[0][0] if sorted_scores else None
    one_liner = _theme_one_liner(main_theme)
    top_drivers = [item.get("label") for item in featured[:3] if item.get("label")]

    return {
        "main_theme": main_theme,
        "one_liner": one_liner,
        "top_drivers": top_drivers,
        "theme_scores": theme_scores_list,
    }


def _build_period_space(
    items: List[Dict[str, Any]],
    *,
    include_axis_focus: bool,
) -> Dict[str, Any]:
    pack = _load_period_space_pack()
    house_labels = _house_labels_from_pack(pack)
    angle_house = {"ASC": 1, "DSC": 7, "MC": 10, "IC": 4}
    long_bodies = {
        "Saturn",
        "Uranus",
        "Neptune",
        "Pluto",
        "North Node",
        "South Node",
        "Chiron",
    }

    candidates = [
        item
        for item in items
        if item.get("bucket") == "long"
        and item.get("transit_body") in long_bodies
        and float(item.get("strength") or 0.0) >= 0.55
    ]
    candidates = sorted(
        candidates, key=lambda item: -float(item.get("strength") or 0.0)
    )[:15]

    house_scores: Dict[int, float] = {}
    house_why: Dict[int, List[Dict[str, Any]]] = {}

    for item in candidates:
        event_id = item.get("event_id")
        strength = float(item.get("strength") or 0.0)
        natal_point = item.get("natal_point")
        houses = item.get("houses") or {}
        natal_house = houses.get("natal_point_house")
        overlay_house = houses.get("transit_in_natal_house")

        if natal_point in angle_house:
            natal_house = angle_house[natal_point]

        if isinstance(natal_house, int):
            weight = strength * 0.6
            house_scores[natal_house] = house_scores.get(natal_house, 0.0) + weight
            house_why.setdefault(natal_house, []).append(
                {"event_id": event_id, "weight": round(weight, 3)}
            )
        if isinstance(overlay_house, int):
            weight = strength * 0.4
            house_scores[overlay_house] = house_scores.get(overlay_house, 0.0) + weight
            house_why.setdefault(overlay_house, []).append(
                {"event_id": event_id, "weight": round(weight, 3)}
            )

    if not house_scores:
        return {
            "house_weights": [],
            "house_focus": {"primary": [], "secondary": []},
            "house_story": "",
            "axis_focus": [],
            "interactions": [],
            "content_ref": {"pack": "tr.period_space.v1"},
        }

    max_score = max(house_scores.values()) or 1.0
    ordered = sorted(house_scores.items(), key=lambda kv: (-kv[1], kv[0]))
    house_weights = []
    for house, score in ordered:
        why_entries = house_why.get(house, [])
        why_total = sum(entry.get("weight", 0.0) for entry in why_entries)
        house_weights.append(
            {
                "house": house,
                "label": house_labels.get(house, "alan"),
                "score": round(score / max_score, 3),
                "why": why_entries,
                "why_total": round(why_total, 3),
            }
        )

    primary_house = ordered[0][0]
    secondary_houses = [house for house, _ in ordered[1:3]]
    def _focus_entry(house: int) -> Dict[str, Any]:
        label = house_labels.get(house, "alan")
        score = next((entry["score"] for entry in house_weights if entry["house"] == house), 0.0)
        return {"house": house, "label": label, "score": score}

    house_focus = {
        "primary": [_focus_entry(primary_house)],
        "secondary": [_focus_entry(house) for house in secondary_houses],
    }

    story_pack = pack.get("house_story") or {}
    opening_templates = story_pack.get("primary_opening") or []
    body_templates = story_pack.get("primary_body") or []
    secondary_templates = story_pack.get("secondary_bridge") or []
    closing_templates = story_pack.get("closing") or []
    not_about_templates = story_pack.get("not_about") or []

    def _pick_template(templates: List[str], seed: str) -> str:
        if not templates:
            return ""
        idx = int(hashlib.sha1(seed.encode("utf-8")).hexdigest(), 16) % len(templates)
        return templates[idx]

    primary_label = house_labels.get(primary_house, "alan")
    opening_sentence = _pick_template(opening_templates, f"{primary_house}:open") or (
        f"Bu donemin ana sahnesi {primary_label} tarafinda kuruluyor."
    )
    body_sentence = _pick_template(body_templates, f"{primary_house}:body") or (
        "Burada olan sey, eski aliskanliklarin artik ayni sekilde calismamasi ve yeni bir duzen ihtiyacinin buyumesi olabilir."
    )
    primary_sentence = " ".join(
        [
            opening_sentence.format(primary_label=primary_label, house=primary_house),
            body_sentence.format(primary_label=primary_label, house=primary_house),
        ]
    ).strip()

    secondary_sentences = []
    for house in secondary_houses:
        label = house_labels.get(house, "alan")
        template = _pick_template(secondary_templates, f"{primary_house}:{house}") or (
            f"Ikinci katman {label} alaninda calisiyor."
        )
        secondary_sentences.append(
            template.format(secondary_label=label, house=house, primary_label=primary_label)
        )

    closing_sentence = _pick_template(closing_templates, f"{primary_house}:closing") or (
        "Bu donem 'hemen sonuc' degil, daha cok 'yerini saglamlastirma' donemi gibi calisabilir."
    )
    not_about_sentence = _pick_template(not_about_templates, f"{primary_house}:not_about")

    paragraphs = [primary_sentence]
    if secondary_sentences:
        paragraphs.append(" ".join(secondary_sentences).strip())
    closing_block = closing_sentence
    if not_about_sentence:
        closing_block = f"{closing_block} {not_about_sentence.format(primary_label=primary_label)}"
    paragraphs.append(closing_block.strip())
    house_story = "\n\n".join([p for p in paragraphs if p]).strip()

    axis_pairs = [
        (1, 7, "1-7", "benlik - iliskiler"),
        (2, 8, "2-8", "deger - yakinlik"),
        (3, 9, "3-9", "zihin - yon"),
        (4, 10, "4-10", "ev - kariyer"),
        (5, 11, "5-11", "ifade - topluluk"),
        (6, 12, "6-12", "ritim - ic dunya"),
    ]
    axis_focus = []
    if include_axis_focus:
        axis_pack = pack.get("axis_pack") or {}

        def _resolve_axis(axis_id: str, mode: str) -> Tuple[str, Dict[str, Any]]:
            keys = [
                f"axis.{axis_id}.{mode}.any",
                f"axis.{axis_id}.any",
                f"axis.generic.{mode}.any",
                "axis.generic.any",
            ]
            for key in keys:
                if key in axis_pack:
                    return key, axis_pack[key]
            return "axis.generic.any", {}

        axis_stats: Dict[str, Dict[str, Any]] = {}
        for item in candidates:
            strength = float(item.get("strength") or 0.0)
            polarity = str(item.get("polarity") or "")
            houses = item.get("houses") or {}
            natal_point = item.get("natal_point")
            natal_house = houses.get("natal_point_house")
            overlay_house = houses.get("transit_in_natal_house")
            if natal_point in angle_house:
                natal_house = angle_house[natal_point]
            if natal_house is None and overlay_house is None:
                continue
            if natal_house is None:
                natal_house = overlay_house
            if overlay_house is None:
                overlay_house = natal_house
            if natal_house is None or overlay_house is None:
                continue
            pair = tuple(sorted([int(natal_house), int(overlay_house)]))
            axis_id = f"{pair[0]}-{pair[1]}"
            stats = axis_stats.setdefault(
                axis_id,
                {"total": 0.0, "pressure": 0.0, "support": 0.0, "drivers": []},
            )
            stats["total"] += strength
            if polarity == "hard":
                stats["pressure"] += strength
            elif polarity == "soft":
                stats["support"] += strength
            stats["drivers"].append(
                {
                    "event_id": item.get("event_id"),
                    "weight": round(strength, 3),
                    "houses": [natal_house, overlay_house],
                }
            )

        for left, right, axis_id, label in axis_pairs:
            stats = axis_stats.get(axis_id)
            if not stats:
                continue
            total = stats.get("total", 0.0)
            if total <= 0:
                continue
            pressure = stats.get("pressure", 0.0)
            support = stats.get("support", 0.0)
            ratio = pressure / (pressure + support + 1e-6)
            if ratio >= 0.6:
                mode = "pressure"
            elif ratio <= 0.4:
                mode = "support"
            else:
                mode = "mixed"

            block_key, block = _resolve_axis(axis_id, mode)
            left_label = house_labels.get(left, "alan")
            right_label = house_labels.get(right, "alan")
            axis_focus.append(
                {
                    "axis": axis_id,
                    "label": block.get("label") or label,
                    "weight": round(total / max_score, 3),
                    "experience": [
                        block.get("one_liner")
                        or f"{left_label} ile {right_label} arasinda denge kurma ihtiyaci artabilir."
                    ],
                    "one_liner": block.get("one_liner")
                    or f"{left_label} ile {right_label} arasinda denge kurma ihtiyaci artabilir.",
                    "how_it_plays": (
                        block.get("how_it_plays")
                        or [
                            "Iki alan arasinda gidip gelme hissi",
                            "Karar vermeden once daha cok dusunme ihtiyaci",
                        ]
                    )[:2],
                    "good_management": (
                        block.get("good_management")
                        or [
                            "Kucuk ve geri donuslu adimlar sec",
                            "Varsayim yerine soru sormak",
                        ]
                    )[:2],
                    "why": stats.get("drivers", []),
                    "content_ref": {"lang": "tr", "pack": "period_space.v1", "key": block_key},
                    "mode_debug": {
                        "pressure": round(pressure, 3),
                        "support": round(support, 3),
                        "ratio": round(ratio, 3),
                    },
                }
            )
        axis_focus = sorted(axis_focus, key=lambda entry: (-entry["weight"], entry["axis"]))[:2]

    interactions = _build_period_interactions(items, pack)
    housepair_focus = interactions[:2] if interactions else []
    return {
        "house_weights": house_weights,
        "house_focus": house_focus,
        "house_story": house_story,
        "axis_focus": axis_focus,
        "interactions": interactions,
        "housepair_focus": housepair_focus,
        "content_ref": {"lang": "tr", "pack": "period_space.v1"},
    }


def _build_ranking(items: List[Dict[str, Any]]) -> None:
    body_weight = {
        "Pluto": 1.70,
        "Neptune": 1.45,
        "Uranus": 1.40,
        "Saturn": 1.65,
        "Jupiter": 1.25,
        "Mars": 1.15,
        "Sun": 1.15,
        "Venus": 1.10,
        "Mercury": 1.05,
        "Moon": 1.10,
        "North Node": 1.35,
        "South Node": 1.35,
        "Chiron": 1.10,
        "Lilith": 0.85,
        "Vertex": 0.80,
        "Fortune": 0.75,
    }
    target_weight = {
        "ASC": 1.35,
        "MC": 1.35,
        "DSC": 1.35,
        "IC": 1.35,
        "Sun": 1.30,
        "Moon": 1.30,
        "Mercury": 1.15,
        "Venus": 1.15,
        "Mars": 1.15,
        "Jupiter": 1.10,
        "Saturn": 1.10,
        "Uranus": 1.00,
        "Neptune": 1.00,
        "Pluto": 1.00,
        "North Node": 0.95,
        "South Node": 0.95,
        "Chiron": 0.90,
        "Lilith": 0.80,
        "Vertex": 0.80,
        "Fortune": 0.80,
    }
    aspect_weight = {
        "conjunction": 1.25,
        "opposition": 1.20,
        "square": 1.20,
        "trine": 1.05,
        "sextile": 1.00,
    }
    house_weight = {1: 1.18, 4: 1.18, 7: 1.18, 10: 1.18}
    time_weight = {"long": 1.15, "medium": 1.05, "short": 0.95}
    phase_weight = {"applying": 1.08, "exact": 1.12, "exactish": 1.12, "separating": 0.98}

    for item in items:
        strength = float(item.get("strength") or 0.0)
        transit_body = str(item.get("transit_body") or "")
        natal_point = str(item.get("natal_point") or "")
        aspect = str(item.get("aspect") or "").lower()
        bucket = str(item.get("bucket") or "")
        phase = str(item.get("phase") or "")
        context = (item.get("interpretation") or {}).get("context") or {}
        natal_house = context.get("natal_target_house") or (item.get("houses") or {}).get(
            "natal_point_house"
        )
        house_mul = house_weight.get(int(natal_house), 1.00) if natal_house else 1.00

        weight = (
            strength
            * body_weight.get(transit_body, 1.0)
            * target_weight.get(natal_point, 1.0)
            * aspect_weight.get(aspect, 1.0)
            * house_mul
            * time_weight.get(bucket, 1.0)
            * phase_weight.get(phase, 1.0)
        )

        reasons = []
        if transit_body in {"Pluto", "Neptune", "Uranus", "Saturn"}:
            reasons.append("outer_planet")
        if transit_body in {"North Node", "South Node"}:
            reasons.append("nodes")
        if natal_point in {"ASC", "MC", "DSC", "IC"}:
            reasons.append("angular")
        if aspect in {"square", "opposition", "conjunction"}:
            reasons.append("hard_aspect")
        if bucket == "long":
            reasons.append("long_window")

        tier = "flavor"
        if weight >= 1.60:
            tier = "main"
        elif weight >= 1.20:
            tier = "support"

        if transit_body in {"Lilith", "Vertex", "Fortune"} or natal_point in {
            "Lilith",
            "Vertex",
            "Fortune",
        }:
            tier = "support" if weight >= 1.20 else "flavor"
            reasons.append("point_body")

        if transit_body in {"Pluto", "Saturn", "North Node", "South Node"} and aspect in {
            "square",
            "opposition",
            "conjunction",
        }:
            if tier == "flavor":
                tier = "support"
            reasons.append("outer_hard")

        item["ranking"] = {
            "strength": round(strength, 3),
            "weight": round(weight, 2),
            "tier": tier,
            "reasons": reasons,
        }


def _select_event_tiers(items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    max_main = 5
    max_support = 8
    max_flavor = 6
    max_per_transit_body = 3
    max_per_natal_target = 2

    deduped: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    for item in items:
        key = (
            str(item.get("transit_body") or ""),
            str(item.get("natal_point") or ""),
            str(item.get("aspect") or ""),
        )
        existing = deduped.get(key)
        if not existing or float(item.get("ranking", {}).get("weight") or 0.0) > float(
            existing.get("ranking", {}).get("weight") or 0.0
        ):
            deduped[key] = item

    def _filter_by_tier(tier: str) -> List[Dict[str, Any]]:
        filtered = [item for item in deduped.values() if item.get("ranking", {}).get("tier") == tier]
        filtered.sort(
            key=lambda it: (-float(it.get("ranking", {}).get("weight") or 0.0), str(it.get("event_id") or "")),
        )
        body_counts: Dict[str, int] = {}
        target_counts: Dict[str, int] = {}
        out = []
        for item in filtered:
            body = str(item.get("transit_body") or "")
            target = str(item.get("natal_point") or "")
            if body_counts.get(body, 0) >= max_per_transit_body:
                continue
            if target_counts.get(target, 0) >= max_per_natal_target:
                continue
            body_counts[body] = body_counts.get(body, 0) + 1
            target_counts[target] = target_counts.get(target, 0) + 1
            out.append(item)
        return out

    main_events = _filter_by_tier("main")[:max_main]
    support_events = _filter_by_tier("support")[:max_support]
    flavor_events = _filter_by_tier("flavor")[:max_flavor]
    return {
        "main_events": main_events,
        "support_events": support_events,
        "flavor_events": flavor_events,
    }


def _build_period_interactions(items: List[Dict[str, Any]], pack: Dict[str, Any]) -> List[Dict[str, Any]]:
    house_labels = _house_labels_from_pack(pack)
    angle_house = {"ASC": 1, "DSC": 7, "MC": 10, "IC": 4}
    duration_weight = {"long": 1.0, "medium": 0.7, "short": 0.3}
    polarity_weight = {"hard": 1.0, "soft": 0.7, "neutral": 0.6}
    preferred_planets = {"Saturn", "Uranus", "Neptune", "Pluto", "Jupiter"}

    scored_events = []
    for item in items:
        strength = float(item.get("strength") or 0.0)
        if strength < 0.70:
            continue
        bucket = str(item.get("bucket") or "")
        if bucket not in {"long", "medium"}:
            continue
        if str(item.get("transit_body") or "") not in preferred_planets:
            continue
        weight = strength * duration_weight.get(bucket, 0.7)
        weight *= polarity_weight.get(str(item.get("polarity") or ""), 0.6)
        scored_events.append((item, weight))

    scored_events = sorted(
        scored_events,
        key=lambda pair: (-pair[1], str(pair[0].get("event_id") or "")),
    )[:15]

    pair_stats: Dict[str, Dict[str, Any]] = {}
    for item, weight in scored_events:
        houses = item.get("houses") or {}
        natal_point = item.get("natal_point")
        natal_house = houses.get("natal_point_house")
        overlay_house = houses.get("transit_in_natal_house")
        if natal_point in angle_house:
            natal_house = angle_house[natal_point]
        if natal_house is None and overlay_house is None:
            continue
        if natal_house is None:
            natal_house = overlay_house
        if overlay_house is None:
            overlay_house = natal_house
        if natal_house is None or overlay_house is None:
            continue

        pair = tuple(sorted([int(natal_house), int(overlay_house)]))
        key = f"housepair.{pair[0]}-{pair[1]}"

        stats = pair_stats.setdefault(
            key,
            {
                "pair": pair,
                "total_weight": 0.0,
                "hard_weight": 0.0,
                "soft_weight": 0.0,
                "drivers": [],
            },
        )
        stats["total_weight"] += weight
        if item.get("polarity") == "hard":
            stats["hard_weight"] += weight
        elif item.get("polarity") == "soft":
            stats["soft_weight"] += weight
        stats["drivers"].append(
            {
                "event_id": item.get("event_id"),
                "weight": round(weight, 3),
                "houses": [natal_house, overlay_house],
            }
        )

    templates = pack.get("housepair_pack") or {}

    def _resolve_housepair(pair_id: str, mode: str) -> Tuple[str, Dict[str, Any]]:
        keys = [
            f"housepair.{pair_id}.{mode}.any",
            f"housepair.{pair_id}.any",
            f"housepair.generic.{mode}.any",
            "housepair.generic.any",
        ]
        for key in keys:
            if key in templates:
                return key, templates[key]
        return "housepair.generic.any", {}

    interactions = []
    for key, stats in sorted(
        pair_stats.items(), key=lambda kv: (-kv[1]["total_weight"], kv[0])
    )[:4]:
        total = stats["total_weight"]
        if total <= 0:
            continue
        hard_ratio = stats["hard_weight"] / total if total else 0.0
        soft_ratio = stats["soft_weight"] / total if total else 0.0
        if hard_ratio > 0.6:
            mode = "pressure"
        elif soft_ratio > 0.6:
            mode = "support"
        else:
            mode = "mixed"

        pressure = stats["hard_weight"]
        support = stats["soft_weight"]
        ratio = pressure / (pressure + support + 1e-6)
        pair = stats["pair"]
        pair_id = f"{pair[0]}-{pair[1]}"
        block_key, block = _resolve_housepair(pair_id, mode)
        left_label = house_labels.get(pair[0], "alan")
        right_label = house_labels.get(pair[1], "alan")
        label = block.get("label") or f"{left_label} - {right_label} hatti"

        one_liner = block.get("one_liner")
        how_it_plays = block.get("how_it_plays") or []
        good_management = block.get("good_management") or []

        if not one_liner or not how_it_plays or not good_management:
            fallback_key, fallback_block = _resolve_housepair("generic", mode)
            block_key = fallback_key
            if not one_liner:
                one_liner = fallback_block.get("one_liner")
            if not how_it_plays:
                how_it_plays = fallback_block.get("how_it_plays") or []
            if not good_management:
                good_management = fallback_block.get("good_management") or []

        interactions.append(
            {
                "id": key,
                "houses": list(pair),
                "label": label,
                "mode": mode,
                "one_liner": one_liner,
                "drivers": stats["drivers"][:3],
                "how_it_plays": how_it_plays[:2],
                "good_management": good_management[:2],
                "why": stats["drivers"][:3],
                "content_ref": {"lang": "tr", "pack": "period_space.v1", "key": block_key},
                "mode_debug": {
                    "pressure": round(pressure, 3),
                    "support": round(support, 3),
                    "ratio": round(ratio, 3),
                },
            }
        )

    return interactions


def _theme_one_liner(theme: str | None) -> str | None:
    mapping = {
        "self": "Bu dönem benlik teması daha görünür.",
        "relationships": "İlişkilerde denge kurma ihtiyacı artar.",
        "career": "Kariyer ve yön teması öne çıkar.",
        "home": "Ev ve aidiyet alanında yeniden ayar yapılır.",
        "inner": "İç dünyada farkındalık artar.",
        "mind": "Zihin/iletişim teması hızlanır.",
    }
    if theme is None:
        return None
    return mapping.get(theme, "Bu dönem belirgin bir tema vurgusu getirir.")


def _normalize_key(value: Any) -> str:
    return str(value or "").strip().lower().replace(" ", "_")


def _format_key(transit_body: Any, aspect: Any, natal_point: Any) -> str:
    return f"{_normalize_key(transit_body)}.{_normalize_key(aspect)}.{_normalize_key(natal_point)}"


def _build_natal_snapshot(natal: Dict[str, Any]) -> Dict[str, Any]:
    asc_sign = ((natal.get("angles") or {}).get("ASC") or {}).get("sign")
    sun_house = None
    moon_house = None
    saturn_house = None
    neptune_house = None
    pluto_house = None
    for body in natal.get("bodies") or []:
        name = body.get("body")
        house = body.get("house")
        if name == "Sun":
            sun_house = house
        elif name == "Moon":
            moon_house = house
        elif name == "Saturn":
            saturn_house = house
        elif name == "Neptune":
            neptune_house = house
        elif name == "Pluto":
            pluto_house = house
    return {
        "asc_sign": asc_sign,
        "sun_house": sun_house,
        "moon_house": moon_house,
        "saturn_house": saturn_house,
        "neptune_house": neptune_house,
        "pluto_house": pluto_house,
    }


class TransitOptions(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    house_system: str = "placidus"
    zodiac: str = "tropical"
    include_bodies: List[str] = Field(default_factory=list)
    include_angles: bool = True
    include_house_cusps: bool = True
    aspect_types: List[str] = Field(default_factory=list)
    orbs: Dict[str, float] = Field(default_factory=dict)
    max_aspects_per_transit_body: int = 12
    debug: bool = False
    interpretation_mode: Optional[str] = None
    include_axis_focus: bool = False


class TransitRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    birth_date: str
    birth_time: str
    birth_place: str
    transit_date: str
    transit_time: Optional[str] = None
    transit_place: str
    options: Optional[TransitOptions] = None
    context_mode: str = "context-lite"


class TransitWindowRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    birth_date: str
    birth_time: str
    birth_place: str
    transit_date: str
    transit_time: Optional[str] = None
    transit_place: str
    options: Optional[TransitOptions] = None
    window_days: int = 120
    step_hours: int = 24
    refine_near_exact: bool = True
    max_events: int = 20
    orb_hysteresis_deg: float = 0.2


class TransitEventSelector(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    transit_body: str
    aspect: str
    natal_point: str
    scope: str = "transit_to_natal"


class TransitEventTimingRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    birth_date: str
    birth_time: str
    birth_place: str
    transit_date: str
    transit_time: Optional[str] = None
    transit_place: str
    options: Optional[TransitOptions] = None
    selector: TransitEventSelector


class TransitNarrativeRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    birth_date: str
    birth_time: str
    birth_place: str
    start: str
    end: str
    tz: str
    transit_place: str | None = None
    lens: str = "general"
    intent: str | None = "beauty_care_nourish"
    sub_intent: str | None = None
    selected_date: str | None = None
    include_best_times: bool = True
    top: int = 10
    window: int = 3
    debug: bool = False


class SolarYearFrameRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    birth_date: str
    birth_time: str
    birth_place: str
    transit_date: str
    transit_place: str


def _build_narrative_public_payload(request: TransitNarrativeRequest, start_date: date_type) -> Dict[str, Any]:
    transit_date = request.selected_date or start_date.isoformat()
    core_request = TransitRequest(
        birth_date=request.birth_date,
        birth_time=request.birth_time,
        birth_place=request.birth_place,
        transit_date=transit_date,
        transit_time="12:00",
        transit_place=request.transit_place or request.birth_place,
        options=None,
        context_mode="context-lite",
    )
    core_response = _build_transits_engine_response(core_request)
    public_payload = build_public_response(core_response)
    period_core_raw = public_payload.get("period_core") if isinstance(public_payload.get("period_core"), Mapping) else {}
    period_core = dict(period_core_raw)
    period_root_causes = period_core.pop("_debug_root_causes", [])
    events_debug = public_payload.get("_events_debug") if isinstance(public_payload.get("_events_debug"), list) else []
    items_unscored = (core_response.get("display") or {}).get("items") or []
    selected_events, period_selection = select_event_ids(
        [item for item in items_unscored if isinstance(item, Mapping)],
        max_cards=5,
        natal=core_response.get("natal") if isinstance(core_response, Mapping) else None,
    )
    selected_ids = {
        str(item.get("event_id") or "")
        for item in selected_events
        if isinstance(item, Mapping)
    }
    coverage = build_period_coverage(
        items_unscored,
        selected_ids=selected_ids,
        now_date=transit_date,
        tz=request.tz,
    )
    include_public_coverage = str(os.getenv("PERIOD_COVERAGE_PUBLIC", "0")).strip().lower() in {"1", "true", "yes", "on"}
    return {
        "period_core": period_core,
        "event_cards": public_payload.get("event_cards") or [],
        "period_peak_timeline": public_payload.get("period_peak_timeline") or [],
        "timeline": public_payload.get("timeline") or {},
        "multi_event": public_payload.get("multi_event") or {},
        "personal_transit_rail": public_payload.get("personal_transit_rail") or [],
        "structural_chapter_rail": public_payload.get("structural_chapter_rail") or [],
        "solar_year_frame": public_payload.get("solar_year_frame") or {},
        "_period_coverage": coverage,
        "_period_selection": period_selection,
        "_period_root_causes": period_root_causes,
        "_events_debug": events_debug,
        **({"period_coverage": coverage} if include_public_coverage else {}),
    }


def _build_transits_engine_response(request: TransitRequest) -> Dict[str, Any]:
    assumptions: list[str] = []
    transit_time = request.transit_time
    if not transit_time:
        transit_time = "12:00"
        assumptions.append("default_transit_time")
    try:
        options_payload = request.options.model_dump() if request.options else {}
        response = build_transit_report(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            birth_place=request.birth_place,
            transit_date=request.transit_date,
            transit_time=transit_time,
            transit_place=request.transit_place,
            options=options_payload,
            assumptions=assumptions,
        )
        window_report = build_transit_window_report(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            birth_place=request.birth_place,
            transit_date=request.transit_date,
            transit_time=transit_time,
            transit_place=request.transit_place,
            options=options_payload,
            window_days=DEFAULT_PERIOD_DAYS,
            step_hours=DEFAULT_PERIOD_STEP_HOURS,
            refine_near_exact=DEFAULT_PERIOD_REFINE_NEAR_EXACT,
            max_events=DEFAULT_PERIOD_MAX_EVENTS,
            orb_hysteresis_deg=DEFAULT_PERIOD_ORB_HYSTERESIS,
            assumptions=assumptions,
        )
        solar_year_frame = build_solar_year_theme(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            birth_place=request.birth_place,
            transit_date=request.transit_date,
            transit_place=request.transit_place,
            natal_snapshot=response.get("natal") if isinstance(response, Mapping) else None,
        )
        display = response.get("display") or {}
        items = display.get("items") or []
        if items:
            content_store = _load_content_store()
            natal_snapshot = _build_natal_snapshot(response.get("natal") or {})
            promise = build_promise_model(natal_snapshot, content_store.claims)
            mode = request.context_mode
            if request.options and request.options.interpretation_mode:
                mode = request.options.interpretation_mode
            interpreted_items, summary = interpret_items(
                items,
                content=content_store,
                promise=promise,
                mode=mode,
                debug=bool(request.options.debug) if request.options else False,
            )
            featured_ids = {
                item.get("event_id") for item in (display.get("featured") or [])
            }
            for item in interpreted_items:
                interp = item.get("interpretation") or {}
                if interp.get("mode") != "B":
                    continue
                if item.get("event_id") not in featured_ids:
                    continue
                houses = item.get("houses") or {}
                natal_house = houses.get("natal_point_house")
                overlay_house = houses.get("transit_in_natal_house")
                natal_point = item.get("natal_point")
                angle_house = {"ASC": 1, "DSC": 7, "MC": 10, "IC": 4}
                if natal_point in angle_house:
                    natal_house = angle_house[natal_point]
                if natal_house is None or overlay_house is None:
                    continue
                labels = _house_labels_from_pack(_load_period_space_pack())
                left_label = labels.get(natal_house, "alan")
                right_label = labels.get(overlay_house, "alan")
                polarity = item.get("polarity")
                if polarity == "hard":
                    mode_label = "gerilim"
                elif polarity == "soft":
                    mode_label = "akis"
                else:
                    mode_label = "denge"
                interp["interaction_context"] = (
                    f"{left_label} ile {right_label} arasinda {mode_label} gibi calisabilir."
                )
                item["interpretation"] = interp
            diversify_where_short(interpreted_items)
            display["items"] = interpreted_items
            response["display"] = display
            _build_ranking(display["items"])
            display["items"] = [
                enrich_legacy_aspect_item(
                    dict(item),
                    natal_snapshot=response.get("natal") if isinstance(response, Mapping) else None,
                    solar_year=solar_year_frame,
                )
                for item in display["items"]
                if isinstance(item, Mapping)
            ]
            response["display"] = display
            summary["pressure_index"] = float(
                response.get("metrics", {}).get("pressure_index") or 0.0
            )
            summary["support_index"] = float(
                response.get("metrics", {}).get("support_index") or 0.0
            )
            presentable = response.get("presentable") or {}
            presentable["summary"] = summary
            presentable.update(_select_event_tiers(display["items"]))
            presentable["natal_promise_catalog"] = promise.get("claims", {}) if promise else {}
            active_claims = []
            for item in display["items"]:
                entry = (item.get("interpretation") or {}).get("natal_promise") or {}
                if entry.get("used") and entry.get("claim_id"):
                    active_claims.append(entry.get("claim_id"))
            if active_claims:
                summary["active_claims"] = sorted(set(active_claims))
            include_axis_focus = bool(request.options.include_axis_focus) if request.options else False
            period_items = _window_items_for_period_space(
                window_report, natal=response.get("natal") or {}
            )
            presentable["period_space"] = _build_period_space(
                period_items, include_axis_focus=include_axis_focus
            )
            response["presentable"] = presentable
            response["content_debug"] = _build_content_debug(interpreted_items, content_store)
            response["natal_promise"] = promise
        response["window_report"] = window_report
        response["solar_year_frame"] = solar_year_frame
        response["event_engine_v2"] = build_personal_multi_event_payload(
            report=response,
            transit_date=request.transit_date,
            transit_place=request.transit_place,
            window_report=window_report,
            solar_year=solar_year_frame,
        )
        return response
    except Exception as exc:  # pragma: no cover - passthrough for API response
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/transits")
def build_transits(request: TransitRequest) -> Dict[str, Any]:
    response = _build_transits_engine_response(request)
    return build_public_response(response)


@router.post("/transits/debug")
def build_transits_debug(request: TransitRequest) -> Dict[str, Any]:
    return _build_transits_engine_response(request)


@router.post("/solar/year-frame")
def build_solar_year_frame(request: SolarYearFrameRequest) -> Dict[str, Any]:
    frame = build_solar_year_theme(
        birth_date=request.birth_date,
        birth_time=request.birth_time,
        birth_place=request.birth_place,
        transit_date=request.transit_date,
        transit_place=request.transit_place,
    )
    return {
        "schema_version": "astro_event.v2",
        "solar_year_frame": frame,
    }


@router.get("/transit/calendar")
def build_transit_calendar(
    birth_date: str,
    birth_time: str,
    birth_place: str,
    start: str,
    end: str,
    tz: str,
    transit_place: str | None = None,
    lens: str = "general",
    view: str = Query("public", description="public | internal | both (ui/full are accepted aliases)"),
    include: str | None = Query(None, description="markers,items_map,items_map_raw,themes,intent_summary,calendar_internal"),
) -> Dict[str, Any]:
    payload = build_transit_calendar_public(
        birth_date=birth_date,
        birth_time=birth_time,
        birth_place=birth_place,
        transit_place=transit_place or birth_place,
        start=start,
        end=end,
        tz=tz,
        lens=lens,
        options=None,
    )
    v = _normalize_calendar_view(view)
    internal = payload.get("calendar_internal") or payload
    public = payload.get("calendar_public") or {}
    if v == "internal":
        return internal
    if v == "both":
        return {"calendar_internal": internal, "calendar_public": public}

    # public + optional include (never mutate public in-place)
    out = copy.deepcopy(public)
    if include:
        inc = {p.strip().lower() for p in include.split(",") if p.strip()}
        if "markers" in inc:
            out["markers"] = internal.get("markers", [])
        if "items_map" in inc:
            out["items_map"] = internal.get("items_map", {})
        if "items_map_raw" in inc:
            out["items_map_raw"] = internal.get("items_map_raw", {})
        if "themes" in inc:
            out["themes"] = internal.get("themes", [])
        if "intent_summary" in inc:
            out["intent_summary"] = internal.get("intent_summary", {})
        if "calendar_internal" in inc:
            out["calendar_internal"] = internal
    return out


@router.get("/transit/calendar/best-times")
def transit_calendar_best_times(
    intent: str = Query(
        "beauty_care_nourish",
        description="beauty_care_nourish | beauty_care_reduce | beauty_care_procedure | ...",
    ),
    sub_intent: str | None = Query(None, description="nourish | reduce | procedure (for beauty_care)"),
    body_area: str | None = Query(None),
    birth_date: str = Query(..., description="YYYY-MM-DD"),
    birth_time: str = Query(..., description="HH:MM"),
    birth_place: str = Query(..., description="City, Country (or your place id)"),
    start: str = Query(..., description="YYYY-MM-DD"),
    end: str = Query(..., description="YYYY-MM-DD"),
    tz: str = Query("Europe/Istanbul"),
    view: str = Query("public", description="public | internal | both (ui/full are accepted aliases)"),
    top: int = Query(10, ge=1, le=50),
    window: int = Query(3, ge=2, le=14),
    debug: int = Query(0, description="1 => evidence/rules döndür"),
    transit_place: str | None = None,
    lens: str = Query("general", description="general | relationship | marriage | business | career | money | health | home"),
) -> Dict[str, Any]:
    try:
        start_date = _parse_iso_date(start, field_name="start")
        end_date = _parse_iso_date(end, field_name="end")
        if start_date > end_date:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "validation_error",
                    "message": "start must be earlier than or equal to end.",
                },
            )

        normalized_intent, normalized_sub_intent, public_intent = _parse_best_times_intent(
            intent,
            sub_intent,
        )
        v = _normalize_calendar_view(view)

        payload = build_transit_calendar_public(
            birth_date=birth_date,
            birth_time=birth_time,
            birth_place=birth_place,
            transit_place=transit_place or birth_place,
            start=start_date.isoformat(),
            end=end_date.isoformat(),
            tz=tz,
            lens=lens,
            options=None,
        )

        internal_payload = payload.get("calendar_internal") or payload
        internal_result = best_times_from_calendar_payload(
            payload=payload.get("calendar_internal") or payload,
            intent=normalized_intent,
            sub_intent=normalized_sub_intent,
            body_area=body_area,
            top=top,
            window=window,
            debug=bool(debug),
        )
        public_result = _normalize_best_times_public_payload(
            raw=internal_result,
            start=start_date.isoformat(),
            end=end_date.isoformat(),
            tz=tz,
            intent=public_intent,
        )

        if v == "internal":
            return internal_result
        if v == "both":
            return {"public": public_result, "internal": internal_result}

        if debug:
            if "_debug_calendar" not in internal_result:
                days = internal_payload.get("days") or []
                sample = days[0] if days else {}
                internal_result["_debug_calendar"] = {
                    "internal_has_days": bool(days),
                    "days_count": len(days),
                    "sample_day_keys": sorted(list(sample.keys()))[:50] if isinstance(sample, dict) else [],
                    "sample_moon_phase": sample.get("moon_phase") if isinstance(sample, dict) else None,
                    "sample_moon_sign": sample.get("moon_sign") if isinstance(sample, dict) else None,
                    "has_markers": bool(internal_payload.get("markers")) if isinstance(internal_payload, dict) else False,
                    "has_items_map_raw": bool(internal_payload.get("items_map_raw")) if isinstance(internal_payload, dict) else False,
                }
            public_result["_debug"] = {
                "calendar": internal_result.get("_debug_calendar") or {},
            }

        return public_result
    except ValueError as exc:
        logger.warning("best-times validation error: %s", exc)
        raise HTTPException(
            status_code=422,
            detail={"error": "validation_error", "message": str(exc)},
        ) from exc
    except Exception as exc:  # pragma: no cover - defensive guard for UI
        logger.exception("best-times failed")
        raise HTTPException(
            status_code=500,
            detail={"error": "best_times_failed", "message": str(exc)},
        ) from exc


@router.get("/transit/calendar/day")
def build_transit_calendar_day(
    birth_date: date_type,
    birth_time: time_type,
    birth_place: str,
    tz: str,
    date: date_type | None = None,
    start: date_type | None = None,
    end: date_type | None = None,
    transit_place: str | None = None,
    view: str = Query("internal", description="public | internal | both (ui/full are accepted aliases)"),
) -> Dict[str, Any]:
    v = _normalize_calendar_view(view)
    birth_date_str = birth_date.isoformat()
    birth_time_str = birth_time.strftime("%H:%M")

    try:
        if date:
            date_str = date.isoformat()
            payload = build_transit_calendar_public(
                birth_date=birth_date_str,
                birth_time=birth_time_str,
                birth_place=birth_place,
                transit_place=transit_place or birth_place,
                start=date_str,
                end=date_str,
                tz=tz,
                lens="general",
                options=None,
            )
            internal = payload.get("calendar_internal") or payload
            public = payload.get("calendar_public") or {}
            if v == "public":
                return to_ui_day_detail(internal, date=date_str, top_n=7)
            if v == "both":
                return {
                    "calendar_internal": internal,
                    "calendar_public": public,
                    "day_ui": to_ui_day_detail(internal, date=date_str, top_n=7),
                }
            return internal

        if not start or not end:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "validation_error",
                    "message": "Provide either 'date' or both 'start' and 'end'.",
                },
            )
        start_str = start.isoformat()
        end_str = end.isoformat()

        payload = build_transit_calendar_public(
            birth_date=birth_date_str,
            birth_time=birth_time_str,
            birth_place=birth_place,
            transit_place=transit_place or birth_place,
            start=start_str,
            end=end_str,
            tz=tz,
            lens="general",
            options=None,
        )
        internal = payload.get("calendar_internal") or payload
        public = payload.get("calendar_public") or {}
        ui = to_ui_calendar(internal, lens="general")

        if v == "public":
            return ui
        if v == "both":
            return {
                "calendar_internal": internal,
                "calendar_public": public,
                "calendar_ui": ui,
            }
        return internal
    except HTTPException:
        raise
    except ValueError as exc:
        logger.warning("calendar/day validation error: %s", exc)
        raise HTTPException(
            status_code=422,
            detail={"error": "validation_error", "message": str(exc)},
        ) from exc
    except Exception as exc:  # pragma: no cover - defensive guard for UI
        logger.exception("calendar/day failed")
        raise HTTPException(
            status_code=500,
            detail={"error": "calendar_day_failed", "message": str(exc)},
        ) from exc


@router.post("/transit/narrative")
def build_transit_narrative(request: TransitNarrativeRequest) -> Dict[str, Any]:
    started = perf_counter()
    start_date = _parse_iso_date(request.start, field_name="start")
    end_date = _parse_iso_date(request.end, field_name="end")
    if start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "validation_error",
                "message": "start must be earlier than or equal to end.",
            },
        )

    payload = build_transit_calendar_public(
        birth_date=request.birth_date,
        birth_time=request.birth_time,
        birth_place=request.birth_place,
        transit_place=request.transit_place or request.birth_place,
        start=start_date.isoformat(),
        end=end_date.isoformat(),
        tz=request.tz,
        lens=request.lens,
        options=None,
    )
    internal = payload.get("calendar_internal") or payload
    calendar_public = to_ui_calendar(internal, lens=request.lens)

    best_times_public: Dict[str, Any] | None = None
    best_times_internal: Dict[str, Any] | None = None
    if request.include_best_times:
        normalized_intent, normalized_sub_intent, public_intent = _parse_best_times_intent(
            request.intent or "",
            request.sub_intent,
        )
        best_times_internal = best_times_from_calendar_payload(
            payload=internal,
            intent=normalized_intent,
            sub_intent=normalized_sub_intent,
            body_area=None,
            top=request.top,
            window=request.window,
            debug=request.debug,
        )
        best_times_public = _normalize_best_times_public_payload(
            raw=best_times_internal,
            start=start_date.isoformat(),
            end=end_date.isoformat(),
            tz=request.tz,
            intent=public_intent,
        )

    blocks = assemble_blocks(
        calendar_public=calendar_public,
        calendar_internal=internal,
        best_times=best_times_public,
        year_summary=calendar_public.get("year_summary") or {},
        selected_date=request.selected_date,
        seed_context={
            "birth_fingerprint": make_birth_fingerprint(
                birth_date=request.birth_date,
                birth_time=request.birth_time,
                birth_place=request.birth_place,
                tz=request.tz,
            ),
            "intent": request.intent or "general",
            "lens": request.lens,
        },
    )

    screens = {
        "space_hub": build_space_hub(blocks),
        "personal_transit": build_personal_transit(blocks),
        "calendar_day": build_calendar_day(blocks, request.selected_date),
        "feed_snippet": build_feed_snippet(blocks),
    }
    internal_days_by_date: Dict[str, Mapping[str, Any]] = {}
    for day in internal.get("days") or []:
        if isinstance(day, Mapping):
            key = str(day.get("date") or "")
            if key:
                internal_days_by_date[key] = day

    calendar_days: list[Dict[str, Any]] = []
    for day in calendar_public.get("days") or []:
        if not isinstance(day, Mapping):
            continue
        day_date = str(day.get("date") or "")
        internal_day = internal_days_by_date.get(day_date) or {}
        labels = [str(label) for label in (day.get("labels") or []) if str(label).strip()]
        top_events = day.get("top_events") or []
        if not isinstance(top_events, list):
            top_events = []
        event_count = int(day.get("event_count") or len(top_events) or 0)
        signals_count = max(event_count, len(labels), len(top_events))
        rating = day.get("rating")
        if not isinstance(rating, int):
            rating = int(internal_day.get("rating") or 0)
        heat = day.get("heat")
        if not isinstance(heat, int):
            heat = int(internal_day.get("heat") or 0)
        critical_reasons_raw = internal_day.get("critical_reason") or day.get("critical_reason") or []
        critical_reasons = [
            str(reason)
            for reason in critical_reasons_raw
            if str(reason).strip()
        ]
        calendar_days.append(
            {
                "date": day_date,
                "signals_count": signals_count,
                "is_critical": bool(day.get("is_critical")),
                "labels": labels[:3],
                "critical_reasons": critical_reasons,
            }
        )

    response: Dict[str, Any] = {
        "range": calendar_public.get("range", {}),
        "blocks": [block.to_dict() for block in blocks],
        "screens": screens,
        "calendar": {
            "days": calendar_days,
        },
    }
    period_coverage_debug: Dict[str, Any] = {}
    period_selection_debug: Dict[str, Any] = {}
    period_root_causes_debug: List[Dict[str, Any]] = []
    public_events_debug: List[Dict[str, Any]] = []
    try:
        response["public"] = _build_narrative_public_payload(request, start_date)
        if isinstance(response.get("public"), Mapping):
            period_coverage_debug = dict(response["public"].get("_period_coverage") or {})
            response["public"].pop("_period_coverage", None)
            period_selection_debug = dict(response["public"].get("_period_selection") or {})
            response["public"].pop("_period_selection", None)
            period_root_causes_debug = [
                dict(item)
                for item in (response["public"].get("_period_root_causes") or [])
                if isinstance(item, Mapping)
            ]
            response["public"].pop("_period_root_causes", None)
            public_events_debug = [
                dict(item)
                for item in (response["public"].get("_events_debug") or [])
                if isinstance(item, Mapping)
            ]
            response["public"].pop("_events_debug", None)
    except Exception:  # pragma: no cover - defensive; do not fail narrative screen due to public cards
        logger.exception("transit narrative public payload failed")
        response["public"] = {
            "period_core": {},
            "event_cards": [],
            "period_peak_timeline": [],
            "timeline": {},
            "multi_event": {
                "schema_version": "astro_event.v2",
                "personal_transit_rail": [],
                "structural_chapter_rail": [],
                "solar_year_frame": {},
                "events_by_id": {},
            },
            "personal_transit_rail": [],
            "structural_chapter_rail": [],
            "solar_year_frame": {},
        }
    if best_times_public is not None:
        response["best_times"] = best_times_public
    if request.debug:
        response["debug"] = {
            "calendar_public_keys": sorted(list(calendar_public.keys())),
            "calendar_days_count": len(calendar_public.get("days") or []),
            "best_times_enabled": bool(request.include_best_times),
            "best_times_candidates": len((best_times_public or {}).get("candidates") or []),
            "best_times_windows": len((best_times_public or {}).get("windows") or []),
            "calendar_numeric": {
                day["date"]: {
                    "signals_count": int(day.get("signals_count") or 0),
                    "rating": int((internal_days_by_date.get(day["date"]) or {}).get("rating") or 0),
                    "heat": int((internal_days_by_date.get(day["date"]) or {}).get("heat") or 0),
                    "event_count": int((internal_days_by_date.get(day["date"]) or {}).get("event_count") or 0),
                }
                for day in calendar_days
                if day.get("date")
            },
            "period_coverage": period_coverage_debug,
            "period_selection": period_selection_debug,
            "period_root_causes": period_root_causes_debug,
            "events_debug": public_events_debug,
        }
        if best_times_public is not None:
            response["best_times"] = best_times_public
        if best_times_internal is not None:
            response["best_times_internal"] = best_times_internal
    _log_transit_timing(
        endpoint="/transit/narrative",
        request=request,
        response=response,
        duration_ms=(perf_counter() - started) * 1000.0,
    )
    return response


@router.post("/transits/window")
def build_transits_window(request: TransitWindowRequest) -> Dict[str, Any]:
    assumptions: list[str] = []
    transit_time = request.transit_time
    if not transit_time:
        transit_time = "12:00"
        assumptions.append("default_transit_time")
    try:
        return build_transit_window_report(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            birth_place=request.birth_place,
            transit_date=request.transit_date,
            transit_time=transit_time,
            transit_place=request.transit_place,
            options=request.options.model_dump() if request.options else {},
            window_days=request.window_days,
            step_hours=request.step_hours,
            refine_near_exact=request.refine_near_exact,
            max_events=request.max_events,
            orb_hysteresis_deg=request.orb_hysteresis_deg,
            assumptions=assumptions,
        )
    except Exception as exc:  # pragma: no cover - passthrough for API response
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/transits/event_timing")
def build_transit_event_timing_response(request: TransitEventTimingRequest) -> Dict[str, Any]:
    assumptions: list[str] = []
    transit_time = request.transit_time
    if not transit_time:
        transit_time = "12:00"
        assumptions.append("default_transit_time")
    try:
        result = build_transit_event_timing(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            birth_place=request.birth_place,
            transit_date=request.transit_date,
            transit_time=transit_time,
            transit_place=request.transit_place,
            options=request.options.model_dump() if request.options else {},
            selector=request.selector.model_dump(),
        )
        result["assumptions"] = assumptions
        result["selector"] = request.selector.model_dump()
        return result
    except Exception as exc:  # pragma: no cover - passthrough for API response
        raise HTTPException(status_code=500, detail=str(exc)) from exc
