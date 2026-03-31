from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

from app.transit.narrative.daily_humanizer_tr import (
    aspect_mode_from_event,
    generate_daily_from_event,
    house_touchpoint_from_event,
    humanize_event_card_tr,
)
from app.transit.narrative.deep_archetype_engine import build_event_card
from app.transit.narrative.point_policy import is_public_event, normalize_point_token

CONFIG_PATH = Path(__file__).resolve().parents[4] / "config" / "transit" / "daily_selection.yaml"

DEFAULT_CONFIG: Dict[str, Any] = {
    "component_weights": {
        "orb_weight_max": 0.28,
        "exactness_max": 0.18,
        "natal_resonance_max": 0.14,
        "angle_activation_max": 0.12,
        "peak_day_boost_max": 0.10,
    },
    "planet_speed_weights": {
        "moon": 0.18,
        "sun": 0.14,
        "mercury": 0.14,
        "mars": 0.14,
        "venus": 0.10,
        "jupiter": 0.06,
        "saturn": 0.04,
        "uranus": 0.04,
        "neptune": 0.04,
        "pluto": 0.04,
    },
    "aspect_weights": {
        "square": 0.16,
        "opposition": 0.16,
        "conjunction": 0.14,
        "quincunx": 0.10,
        "trine": 0.11,
        "sextile": 0.09,
        "default": 0.07,
    },
    "phase_weights": {
        "exact": 0.18,
        "exactish": 0.16,
        "applying": 0.10,
        "separating": 0.04,
        "default": 0.0,
    },
    "date_proximity_weights": {
        "exact_day": 0.10,
        "one_day": 0.06,
        "two_days": 0.03,
    },
    "thresholds": {
        "high_score_candidate_min": 0.58,
        "meaningful_event_min": 0.42,
        "eligible_strength_min": 0.18,
        "eligible_today_min": 0.12,
        "eligible_narrative_min": 0.12,
        "humanizer_confidence_min": 0.35,
    },
    "limits": {
        "max_daily_cards": 2,
        "max_period_cards": 3,
        "orb_max_deg": 6.0,
    },
    "lunation_boosts": {
        "lunation_trigger": 0.16,
        "eclipse_trigger": 0.24,
        "new_moon": 0.22,
        "full_moon": 0.22,
    },
    "angle_activation": {
        "angle_points": ["ASC", "DSC", "MC", "IC"],
        "angular_houses": [1, 4, 7, 10],
    },
    "candidate_rules": {
        "short_window_buckets": ["short"],
        "exact_phases": ["exact", "exactish", "applying"],
        "near_exact_max_days": 2,
        "selected_day_top_event_boost": 0.10,
        "explicit_lunation_priority": True,
        "explicit_lunation_window_days": 2,
    },
    "score_mix": {
        "strength": 0.45,
        "today": 0.35,
        "narrative": 0.20,
    },
    "strength_weights": {
        "event_family_weight_max": 0.14,
        "luminary_priority": {
            "moon": 0.04,
            "sun": 0.03,
        },
        "event_family_weights": {
            "lunation_trigger": 1.0,
            "eclipse_trigger": 1.0,
            "station_event": 0.85,
            "house_ingress_event": 0.72,
            "retro_shift": 0.78,
            "direction_change": 0.78,
            "peak_family": 0.62,
        },
    },
    "today_weights": {
        "selected_date_proximity_max": 0.14,
        "calendar_salience_max": 0.12,
        "surfaceability_max": 0.09,
        "peak_shift_max": 0.10,
    },
    "narrative_weights": {
        "house_clarity_max": 0.25,
        "planet_feel_clarity_max": 0.18,
        "aspect_readability_max": 0.16,
        "humanizer_confidence_max": 0.23,
        "guidance_value_max": 0.18,
        "house_anchor_penalty": 0.12,
    },
    "narrative_clarity": {
        "house_weights": {
            "1": 0.84,
            "2": 0.82,
            "3": 1.0,
            "4": 0.96,
            "5": 0.84,
            "6": 0.90,
            "7": 1.0,
            "8": 0.86,
            "9": 0.74,
            "10": 1.0,
            "11": 0.72,
            "12": 0.62,
        },
        "planet_translation": {
            "moon": 1.0,
            "mercury": 1.0,
            "venus": 0.95,
            "mars": 0.95,
            "sun": 0.88,
            "saturn": 0.78,
            "jupiter": 0.72,
            "uranus": 0.72,
            "neptune": 0.68,
            "pluto": 0.72,
            "default": 0.60,
        },
        "aspect_readability": {
            "friction": 0.96,
            "polarity": 1.0,
            "concentration": 0.90,
            "flow": 0.82,
            "opening": 0.78,
            "mixed": 0.60,
        },
    },
    "penalties": {
        "same_house_penalty": 0.08,
        "same_aspect_mode_penalty": 0.06,
        "same_tone_penalty": 0.04,
        "redundancy_penalty": 0.07,
    },
    "balance": {
        "prefer_non_shadow_bonus": 0.05,
        "all_shadow_penalty": 0.03,
    },
}

PUBLIC_BLOCKED_POINTS = {"fortune", "lilith", "south_node", "north_node", "vertex"}
PUBLIC_EVENT_V2_FIELDS = (
    "event_family",
    "event_subtype",
    "audience",
    "event_kind",
    "importance_tier",
    "planet_class",
    "time_scale",
    "significance_score",
    "lasting_change_score",
    "chapter_opening",
    "repeat_pass_count",
    "is_structural",
    "recognition_intensity",
    "importance_label_tr",
    "copy_mode",
)

LABEL_TO_DOMAIN = {
    "identity": {"identity", "self"},
    "mind": {"mind", "communication", "zihin"},
    "home": {"home", "security"},
    "career": {"career", "visibility"},
    "relationships": {"relationship", "relationships"},
    "money": {"money", "value"},
    "body": {"body", "rhythm", "routine"},
    "inner": {"inner", "depth"},
}

HOUSE_TO_DOMAIN = {
    1: "identity",
    2: "money",
    3: "mind",
    4: "home",
    5: "identity",
    6: "body",
    7: "relationships",
    8: "inner",
    9: "mind",
    10: "career",
    11: "career",
    12: "inner",
}

GENERIC_GUIDANCE = {
    "acele etme.",
    "ilk cümleye mecbur değilsin.",
    "hemen tepki verme.",
    "her şeyi bugün çözmeye çalışma.",
}

TECHNICAL_TOKENS = (
    "transit",
    "orb",
    "exact",
    "applying",
    "separating",
    "square",
    "opposition",
    "conjunction",
    "trine",
    "sextile",
)


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


def _date_head(value: Any) -> str:
    text = str(value or "").strip()
    return text[:10] if len(text) >= 10 else ""


def _merge_config(defaults: Mapping[str, Any], override: Mapping[str, Any]) -> Dict[str, Any]:
    merged = dict(defaults)
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = _merge_config(merged.get(key, {}), value)
        else:
            merged[key] = value
    return merged


@lru_cache(maxsize=1)
def load_daily_selection_config() -> Mapping[str, Any]:
    config = dict(DEFAULT_CONFIG)
    if CONFIG_PATH.exists():
        try:
            payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {}
        if isinstance(payload, Mapping):
            config = _merge_config(config, payload)
    env_payload = os.getenv("JOVIA_DAILY_SELECTION_CONFIG", "").strip()
    if env_payload:
        try:
            override = json.loads(env_payload)
        except json.JSONDecodeError:
            override = {}
        if isinstance(override, Mapping):
            config = _merge_config(config, override)
    return config


def _days_to_selected(selected_date: str, raw: Any) -> int | None:
    import datetime as _dt

    head = _date_head(raw)
    if not head:
        return None
    try:
        return abs((_dt.date.fromisoformat(head) - _dt.date.fromisoformat(selected_date)).days)
    except ValueError:
        return None


def _is_public_allowed(item: Mapping[str, Any]) -> bool:
    if not is_public_event(item):
        return False
    transit = normalize_point_token(item.get("transit_body"))
    target = normalize_point_token(item.get("natal_point"))
    return transit not in PUBLIC_BLOCKED_POINTS and target not in PUBLIC_BLOCKED_POINTS


def _house_candidates(item: Mapping[str, Any], card: Mapping[str, Any] | None) -> List[int]:
    out: List[int] = []
    if isinstance(card, Mapping):
        derived = card.get("derived_context") if isinstance(card.get("derived_context"), Mapping) else {}
        target = derived.get("natal_target") if isinstance(derived.get("natal_target"), Mapping) else {}
        scene = card.get("scene") if isinstance(card.get("scene"), Mapping) else {}
        for raw in (target.get("house"), scene.get("outcome_house"), scene.get("start_house")):
            house = _safe_int(raw)
            if house is not None:
                out.append(house)
    houses = item.get("houses") if isinstance(item.get("houses"), Mapping) else {}
    for raw in (houses.get("natal_point_house"), houses.get("transit_in_natal_house")):
        house = _safe_int(raw)
        if house is not None:
            out.append(house)
    return out


def _event_family(item: Mapping[str, Any], card: Mapping[str, Any] | None) -> str:
    for source in (item, card or {}):
        family = str(source.get("event_family") or "").strip().lower()
        if family:
            return family
    return ""


def _event_subtype_token(item: Mapping[str, Any], card: Mapping[str, Any] | None) -> str:
    for source in (item, card or {}):
        subtype = str(source.get("event_subtype") or "").strip().lower()
        if subtype:
            return subtype
        for key in ("title", "title_tr", "summary_tr", "headline", "event_id"):
            text = str(source.get(key) or "").strip().lower()
            if "new_moon" in text or "yeniay" in text or "yeni ay" in text:
                return "new_moon"
            if "full_moon" in text or "dolunay" in text:
                return "full_moon"
            if "retro" in text or "station" in text:
                return "retro_shift"
            if "ingress" in text:
                return "ingress"
    return ""


def _source_horizon(item: Mapping[str, Any], card: Mapping[str, Any] | None) -> str:
    source_horizon = str((item.get("horizon") or (card or {}).get("horizon") or "")).strip().lower()
    if source_horizon:
        return source_horizon
    bucket = str((item.get("bucket") or (card or {}).get("bucket") or "")).strip().lower()
    return "daily" if bucket == "short" else "period"


def _event_body(item: Mapping[str, Any], card: Mapping[str, Any] | None) -> str:
    return str((item.get("transit_body") or (card or {}).get("transit_body") or "")).strip().lower()


def _event_aspect(item: Mapping[str, Any], card: Mapping[str, Any] | None) -> str:
    return str((item.get("aspect") or (card or {}).get("aspect") or "")).strip().lower()


def _event_phase(item: Mapping[str, Any], card: Mapping[str, Any] | None) -> str:
    return str((item.get("phase") or (card or {}).get("phase") or "")).strip().lower()


def _ranking_exact_in_days(item: Mapping[str, Any], card: Mapping[str, Any] | None) -> int | None:
    ranking = item.get("ranking") if isinstance(item.get("ranking"), Mapping) else {}
    exact_in_days = _safe_int(ranking.get("exact_in_days"))
    if exact_in_days is None and isinstance(card, Mapping):
        tags = card.get("tags") if isinstance(card.get("tags"), Mapping) else {}
        exact_in_days = _safe_int(tags.get("exact_in_days"))
    return exact_in_days


def _timing_map(item: Mapping[str, Any], card: Mapping[str, Any] | None) -> Mapping[str, Any]:
    for source in (card or {}, item):
        timing = source.get("timing") if isinstance(source.get("timing"), Mapping) else {}
        if timing:
            return timing
    return {}


def _event_importance_tier(item: Mapping[str, Any], card: Mapping[str, Any] | None) -> str:
    return str((item.get("importance_tier") or (card or {}).get("importance_tier") or "")).strip().lower()


def _event_signal_family(item: Mapping[str, Any], card: Mapping[str, Any] | None) -> str:
    family = _event_family(item, card)
    subtype = _event_subtype_token(item, card)
    if family in {"lunation_trigger", "eclipse_trigger"}:
        return family
    if family == "station_event" or subtype in {"retro_shift", "direction_change"}:
        return "station_event"
    if family == "house_ingress_event" or subtype == "ingress":
        return "house_ingress_event"
    if _event_importance_tier(item, card) in {"high", "critical"}:
        return "peak_family"
    return family or subtype


def _orb_weight(item: Mapping[str, Any], config: Mapping[str, Any]) -> float:
    weights = config.get("component_weights") if isinstance(config.get("component_weights"), Mapping) else {}
    limits = config.get("limits") if isinstance(config.get("limits"), Mapping) else {}
    orb = _safe_float(item.get("orb_deg"), default=99.0)
    max_orb = max(0.1, _safe_float(limits.get("orb_max_deg"), default=6.0))
    max_weight = _safe_float(weights.get("orb_weight_max"), default=0.28)
    ratio = max(0.0, min(1.0, 1.0 - (min(orb, max_orb) / max_orb)))
    return round(max_weight * (ratio**1.35), 4)


def _planet_speed_weight(item: Mapping[str, Any], card: Mapping[str, Any] | None, config: Mapping[str, Any]) -> float:
    weights = config.get("planet_speed_weights") if isinstance(config.get("planet_speed_weights"), Mapping) else {}
    return round(_safe_float(weights.get(_event_body(item, card)), default=0.0), 4)


def _luminary_priority_weight(item: Mapping[str, Any], card: Mapping[str, Any] | None, config: Mapping[str, Any]) -> float:
    strength_weights = config.get("strength_weights") if isinstance(config.get("strength_weights"), Mapping) else {}
    luminary = strength_weights.get("luminary_priority") if isinstance(strength_weights.get("luminary_priority"), Mapping) else {}
    return round(_safe_float(luminary.get(_event_body(item, card)), default=0.0), 4)


def _aspect_weight(item: Mapping[str, Any], card: Mapping[str, Any] | None, config: Mapping[str, Any]) -> float:
    weights = config.get("aspect_weights") if isinstance(config.get("aspect_weights"), Mapping) else {}
    aspect = _event_aspect(item, card)
    return round(_safe_float(weights.get(aspect), default=_safe_float(weights.get("default"), 0.07)), 4)


def _exactness_weight(item: Mapping[str, Any], card: Mapping[str, Any] | None, config: Mapping[str, Any]) -> float:
    weights = config.get("phase_weights") if isinstance(config.get("phase_weights"), Mapping) else {}
    phase = _event_phase(item, card)
    phase_weight = _safe_float(weights.get(phase), default=_safe_float(weights.get("default"), 0.0))
    exact_in_days = _ranking_exact_in_days(item, card)
    if exact_in_days == 0:
        phase_weight = max(phase_weight, _safe_float(weights.get("exact"), 0.18))
    elif exact_in_days == 1:
        phase_weight = max(phase_weight, 0.12)
    elif exact_in_days == 2:
        phase_weight = max(phase_weight, 0.08)
    return round(phase_weight, 4)


def _angle_activation_weight(item: Mapping[str, Any], card: Mapping[str, Any] | None, config: Mapping[str, Any]) -> float:
    angle_cfg = config.get("angle_activation") if isinstance(config.get("angle_activation"), Mapping) else {}
    max_weight = _safe_float((config.get("component_weights") or {}).get("angle_activation_max"), default=0.12)
    angle_points = {str(token).upper() for token in (angle_cfg.get("angle_points") or [])}
    angular_houses = {int(token) for token in (angle_cfg.get("angular_houses") or []) if _safe_int(token) is not None}
    natal_point = str((item.get("natal_point") or (card or {}).get("natal_point") or "")).strip().upper()
    if natal_point in angle_points:
        return round(max_weight, 4)
    houses = _house_candidates(item, card)
    if any(house in angular_houses for house in houses):
        return round(max_weight, 4)
    return 0.0


def _natal_resonance_weight(item: Mapping[str, Any], card: Mapping[str, Any] | None, config: Mapping[str, Any]) -> float:
    max_weight = _safe_float((config.get("component_weights") or {}).get("natal_resonance_max"), default=0.14)
    resonance = 0.0
    if isinstance(card, Mapping):
        promise = card.get("natal_promise") if isinstance(card.get("natal_promise"), Mapping) else {}
        resonance = _safe_float(promise.get("score"), default=0.0)
    if resonance <= 0.0:
        promise = item.get("natal_promise") if isinstance(item.get("natal_promise"), Mapping) else {}
        resonance = _safe_float(promise.get("score"), default=0.0)
    return round(max(0.0, resonance) * max_weight, 4)


def _event_family_weight(item: Mapping[str, Any], card: Mapping[str, Any] | None, config: Mapping[str, Any]) -> float:
    strength_weights = config.get("strength_weights") if isinstance(config.get("strength_weights"), Mapping) else {}
    family_cfg = strength_weights.get("event_family_weights") if isinstance(strength_weights.get("event_family_weights"), Mapping) else {}
    max_weight = _safe_float(strength_weights.get("event_family_weight_max"), default=0.14)
    family_key = _event_signal_family(item, card)
    family_ratio = _safe_float(family_cfg.get(family_key), default=0.0)
    return round(max_weight * family_ratio, 4)


def _selected_date_proximity_weight(item: Mapping[str, Any], card: Mapping[str, Any] | None, *, selected_date: str, config: Mapping[str, Any]) -> float:
    weights = config.get("date_proximity_weights") if isinstance(config.get("date_proximity_weights"), Mapping) else {}
    today_weights = config.get("today_weights") if isinstance(config.get("today_weights"), Mapping) else {}
    max_weight = _safe_float(today_weights.get("selected_date_proximity_max"), default=0.14)
    timing = _timing_map(item, card)
    best = 0.0
    for key in ("peak_date_utc", "entry_date_utc", "exit_date_utc"):
        delta = _days_to_selected(selected_date, timing.get(key))
        if delta is None:
            continue
        if delta == 0:
            best = max(best, _safe_float(weights.get("exact_day"), 0.10))
        elif delta == 1:
            best = max(best, _safe_float(weights.get("one_day"), 0.06))
        elif delta == 2:
            best = max(best, _safe_float(weights.get("two_days"), 0.03))
    exact_in_days = _ranking_exact_in_days(item, card)
    if exact_in_days == 0:
        best = max(best, _safe_float(weights.get("exact_day"), 0.10))
    elif exact_in_days == 1:
        best = max(best, _safe_float(weights.get("one_day"), 0.06))
    elif exact_in_days == 2:
        best = max(best, _safe_float(weights.get("two_days"), 0.03))
    return round(min(max_weight, best), 4)


def _label_alignment_score(labels: Sequence[str], house: int | None) -> float:
    if house is None or not labels:
        return 0.0
    domain = HOUSE_TO_DOMAIN.get(house, "")
    accepted = LABEL_TO_DOMAIN.get(domain, set())
    matched = 0
    for label in labels:
        token = str(label).strip().lower().replace(" ", "_")
        if any(part in token for part in accepted):
            matched += 1
    return min(1.0, matched / max(1, len(labels)))


def _calendar_salience_weight(
    item: Mapping[str, Any],
    context: Mapping[str, Any],
    *,
    house: int | None,
    config: Mapping[str, Any],
) -> float:
    today_weights = config.get("today_weights") if isinstance(config.get("today_weights"), Mapping) else {}
    max_weight = _safe_float(today_weights.get("calendar_salience_max"), default=0.12)
    selected_day_context = context.get("selected_day_context") if isinstance(context.get("selected_day_context"), Mapping) else {}
    event_id = str(item.get("event_id") or "").strip()
    top_event_ids = {str(token).strip() for token in (selected_day_context.get("top_event_ids") or []) if str(token).strip()}
    labels = [str(label).strip() for label in (selected_day_context.get("labels") or []) if str(label).strip()]
    critical_reasons = [str(reason).strip().lower() for reason in (selected_day_context.get("critical_reasons") or []) if str(reason).strip()]

    score = 0.0
    if event_id and event_id in top_event_ids:
        score += 0.10
    score += 0.06 * _label_alignment_score(labels, house)
    if critical_reasons:
        aspect = _event_aspect(item, context.get("card") if isinstance(context.get("card"), Mapping) else None)
        if aspect in {"square", "opposition", "conjunction"}:
            score += 0.02
    signals_count = _safe_int(selected_day_context.get("signals_count")) or 0
    if signals_count >= 3:
        score += 0.01
    return round(min(max_weight, score), 4)


def _surfaceability_weight(context: Mapping[str, Any], config: Mapping[str, Any]) -> float:
    today_weights = config.get("today_weights") if isinstance(config.get("today_weights"), Mapping) else {}
    max_weight = _safe_float(today_weights.get("surfaceability_max"), default=0.09)
    preview = context.get("preview") if isinstance(context.get("preview"), Mapping) else {}
    metrics = context.get("narrative_metrics") if isinstance(context.get("narrative_metrics"), Mapping) else {}
    source_horizon = str(context.get("source_horizon") or "").strip().lower()
    score = 0.0
    if source_horizon == "daily":
        score += 0.04
    if str(preview.get("felt_line_tr") or "").strip():
        score += 0.03
    score += 0.02 * _safe_float(metrics.get("humanizer_confidence"), default=0.0)
    return round(min(max_weight, score), 4)


def _peak_shift_weight(item: Mapping[str, Any], card: Mapping[str, Any] | None, *, selected_date: str, config: Mapping[str, Any]) -> float:
    today_weights = config.get("today_weights") if isinstance(config.get("today_weights"), Mapping) else {}
    max_weight = _safe_float(today_weights.get("peak_shift_max"), default=0.10)
    family_key = _event_signal_family(item, card)
    phase = _event_phase(item, card)
    timing = _timing_map(item, card)
    exact_in_days = _ranking_exact_in_days(item, card)
    score = 0.0
    if family_key in {"lunation_trigger", "eclipse_trigger", "station_event", "house_ingress_event"}:
        delta = _days_to_selected(selected_date, timing.get("peak_date_utc"))
        lunation_window = _safe_int((config.get("candidate_rules") or {}).get("explicit_lunation_window_days")) or 2
        if delta is not None and delta <= lunation_window:
            score = max(score, 0.08)
    if phase in {"exact", "exactish"} or exact_in_days == 0:
        score = max(score, 0.10)
    elif phase == "applying" or exact_in_days == 1:
        score = max(score, 0.06)
    if _days_to_selected(selected_date, timing.get("entry_date_utc")) == 0:
        score = max(score, 0.07)
    return round(min(max_weight, score), 4)


def _sentence_quality(text: str) -> float:
    words = [word for word in str(text or "").split() if word]
    if not words:
        return 0.0
    if len(words) <= 3:
        return 0.45
    if len(words) <= 16:
        return 1.0
    if len(words) <= 22:
        return 0.78
    return 0.55


def _guidance_value(preview: Mapping[str, Any]) -> float:
    guidance = str(preview.get("guidance_micro_tr") or "").strip().lower()
    if not guidance:
        return 0.0
    if guidance in GENERIC_GUIDANCE:
        return 0.52
    if any(token in guidance for token in ("cümle", "mesafe", "tempo", "alan", "hız", "heves", "beklenti", "duruş")):
        return 1.0
    return 0.76


def _house_anchor_visible(preview: Mapping[str, Any]) -> bool:
    house_touchpoint = str(preview.get("house_touchpoint_tr") or "").strip().lower()
    if not house_touchpoint:
        return False
    merged = " ".join(
        [
            str(preview.get("felt_line_tr") or "").lower(),
            str(preview.get("why_it_feels_this_way_tr") or "").lower(),
            str(preview.get("guidance_micro_tr") or "").lower(),
        ]
    )
    probe_tokens = [token for token in house_touchpoint.replace("ve", " ").split() if len(token) >= 4]
    return any(token in merged for token in probe_tokens)


def _narrative_metrics(preview: Mapping[str, Any], *, house: int | None, body: str, mode: str, config: Mapping[str, Any]) -> Dict[str, float]:
    clarity = config.get("narrative_clarity") if isinstance(config.get("narrative_clarity"), Mapping) else {}
    house_weights = clarity.get("house_weights") if isinstance(clarity.get("house_weights"), Mapping) else {}
    planet_weights = clarity.get("planet_translation") if isinstance(clarity.get("planet_translation"), Mapping) else {}
    aspect_weights = clarity.get("aspect_readability") if isinstance(clarity.get("aspect_readability"), Mapping) else {}

    felt = str(preview.get("felt_line_tr") or "").strip()
    why = str(preview.get("why_it_feels_this_way_tr") or "").strip()
    guidance = str(preview.get("guidance_micro_tr") or "").strip()
    merged = " ".join([felt.lower(), why.lower(), guidance.lower()])

    house_visible = _house_anchor_visible(preview)
    non_technical = 1.0 if not any(token in merged for token in TECHNICAL_TOKENS) else 0.0
    felt_quality = _sentence_quality(felt)
    why_quality = _sentence_quality(why)
    guidance_quality = _sentence_quality(guidance)
    guidance_value = _guidance_value(preview)

    humanizer_confidence = round(
        (
            felt_quality
            + why_quality
            + guidance_quality
            + guidance_value
            + (1.0 if house_visible else 0.35)
            + non_technical
        )
        / 6.0,
        4,
    )
    return {
        "house_clarity_ratio": _safe_float(house_weights.get(str(house or ""), 0.5), default=0.5),
        "planet_feel_ratio": _safe_float(planet_weights.get(body, planet_weights.get("default", 0.6)), default=0.6),
        "aspect_readability_ratio": _safe_float(aspect_weights.get(mode, aspect_weights.get("mixed", 0.6)), default=0.6),
        "guidance_value_ratio": guidance_value,
        "humanizer_confidence": humanizer_confidence,
        "house_anchor_visible": 1.0 if house_visible else 0.0,
        "redundancy_key": f"{preview.get('house_touchpoint_tr')}|{preview.get('aspect_mode')}|{preview.get('tone_face')}|{body}",
    }


def build_scoring_context(
    event: Mapping[str, Any],
    *,
    selected_date: str,
    context: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    context = dict(context or {})
    config = context.get("config") if isinstance(context.get("config"), Mapping) else load_daily_selection_config()
    card = context.get("card") if isinstance(context.get("card"), Mapping) else dict(event)
    source_horizon = _source_horizon(event, card)
    preview = context.get("preview") if isinstance(context.get("preview"), Mapping) else humanize_event_card_tr(card)
    house = house_touchpoint_from_event(preview)
    mode = aspect_mode_from_event(preview)
    body = _event_body(event, card)
    metrics = context.get("narrative_metrics") if isinstance(context.get("narrative_metrics"), Mapping) else _narrative_metrics(
        preview,
        house=house,
        body=body,
        mode=mode,
        config=config,
    )
    out = dict(context)
    out.update(
        {
            "config": config,
            "card": dict(card),
            "preview": dict(preview),
            "selected_date": selected_date,
            "source_horizon": source_horizon,
            "house": house,
            "aspect_mode": mode,
            "body": body,
            "narrative_metrics": dict(metrics),
            "selected_day_context": dict(context.get("selected_day_context") or {}),
        }
    )
    return out


def compute_strength_score(event: Mapping[str, Any], selected_date: str, context: Mapping[str, Any]) -> float:
    ctx = build_scoring_context(event, selected_date=selected_date, context=context)
    config = ctx["config"]
    parts = {
        "orb_weight": _orb_weight(event, config),
        "planet_speed_weight": _planet_speed_weight(event, ctx["card"], config),
        "luminary_priority_weight": _luminary_priority_weight(event, ctx["card"], config),
        "aspect_weight": _aspect_weight(event, ctx["card"], config),
        "exactness_weight": _exactness_weight(event, ctx["card"], config),
        "angle_activation_weight": _angle_activation_weight(event, ctx["card"], config),
        "natal_resonance_weight": _natal_resonance_weight(event, ctx["card"], config),
        "event_family_weight": _event_family_weight(event, ctx["card"], config),
    }
    return round(sum(parts.values()), 4)


def compute_today_score(event: Mapping[str, Any], selected_date: str, context: Mapping[str, Any]) -> float:
    ctx = build_scoring_context(event, selected_date=selected_date, context=context)
    config = ctx["config"]
    parts = {
        "selected_date_proximity_weight": _selected_date_proximity_weight(event, ctx["card"], selected_date=selected_date, config=config),
        "calendar_salience_weight": _calendar_salience_weight(event, ctx, house=ctx["house"], config=config),
        "surfaceability_weight": _surfaceability_weight(ctx, config),
        "peak_shift_weight": _peak_shift_weight(event, ctx["card"], selected_date=selected_date, config=config),
    }
    return round(sum(parts.values()), 4)


def compute_narrative_score(event: Mapping[str, Any], selected_date: str, context: Mapping[str, Any]) -> float:
    ctx = build_scoring_context(event, selected_date=selected_date, context=context)
    config = ctx["config"]
    weights = config.get("narrative_weights") if isinstance(config.get("narrative_weights"), Mapping) else {}
    metrics = ctx["narrative_metrics"]

    score = (
        _safe_float(weights.get("house_clarity_max"), 0.25) * _safe_float(metrics.get("house_clarity_ratio"), 0.5)
        + _safe_float(weights.get("planet_feel_clarity_max"), 0.18) * _safe_float(metrics.get("planet_feel_ratio"), 0.6)
        + _safe_float(weights.get("aspect_readability_max"), 0.16) * _safe_float(metrics.get("aspect_readability_ratio"), 0.6)
        + _safe_float(weights.get("humanizer_confidence_max"), 0.23) * _safe_float(metrics.get("humanizer_confidence"), 0.5)
        + _safe_float(weights.get("guidance_value_max"), 0.18) * _safe_float(metrics.get("guidance_value_ratio"), 0.5)
    )
    if _safe_float(metrics.get("house_anchor_visible"), 0.0) < 0.5:
        score -= _safe_float(weights.get("house_anchor_penalty"), 0.12)
    return round(max(0.0, score), 4)


def compute_final_daily_score(*, strength_score: float, today_score: float, narrative_score: float, config: Mapping[str, Any]) -> float:
    mix = config.get("score_mix") if isinstance(config.get("score_mix"), Mapping) else {}
    return round(
        (_safe_float(mix.get("strength"), 0.45) * strength_score)
        + (_safe_float(mix.get("today"), 0.35) * today_score)
        + (_safe_float(mix.get("narrative"), 0.20) * narrative_score),
        4,
    )


def _is_short_window(item: Mapping[str, Any], card: Mapping[str, Any] | None, config: Mapping[str, Any]) -> bool:
    candidate = config.get("candidate_rules") if isinstance(config.get("candidate_rules"), Mapping) else {}
    short_buckets = {str(token).lower() for token in (candidate.get("short_window_buckets") or ["short"])}
    exact_phases = {str(token).lower() for token in (candidate.get("exact_phases") or [])}
    near_exact_max_days = _safe_int(candidate.get("near_exact_max_days")) or 2
    bucket = str((item.get("bucket") or (card or {}).get("bucket") or "")).strip().lower()
    phase = _event_phase(item, card)
    if bucket in short_buckets or phase in exact_phases:
        return True
    exact_in_days = _ranking_exact_in_days(item, card)
    return exact_in_days is not None and exact_in_days <= near_exact_max_days


def _is_explicit_lunation(item: Mapping[str, Any], card: Mapping[str, Any] | None) -> bool:
    return _event_family(item, card) in {"lunation_trigger", "eclipse_trigger"}


def _materialize_card(
    item: Mapping[str, Any],
    *,
    existing_by_id: Mapping[str, Mapping[str, Any]],
    natal: Mapping[str, Any] | None,
    event_v2_by_id: Mapping[str, Mapping[str, Any]],
) -> Dict[str, Any]:
    event_id = str(item.get("event_id") or "").strip()
    if event_id and event_id in existing_by_id:
        return dict(existing_by_id[event_id])

    card = build_event_card(item, context={"natal": natal or {}})
    merged = dict(card)
    event_meta = event_v2_by_id.get(event_id) if event_id else None
    for source in (item, event_meta or {}):
        for key in PUBLIC_EVENT_V2_FIELDS:
            if key in source:
                merged[key] = source.get(key)
    if isinstance(event_meta, Mapping):
        merged["astro_event"] = dict(event_meta)
    return humanize_event_card_tr(merged)


def _build_row(
    item: Mapping[str, Any],
    *,
    selected_date: str,
    selected_day_context: Mapping[str, Any],
    existing_by_id: Mapping[str, Mapping[str, Any]],
    natal: Mapping[str, Any] | None,
    event_v2_by_id: Mapping[str, Mapping[str, Any]],
    config: Mapping[str, Any],
) -> Dict[str, Any]:
    card = _materialize_card(
        item,
        existing_by_id=existing_by_id,
        natal=natal,
        event_v2_by_id=event_v2_by_id,
    )
    context = build_scoring_context(
        item,
        selected_date=selected_date,
        context={
            "config": config,
            "card": card,
            "preview": humanize_event_card_tr(card),
            "selected_day_context": selected_day_context,
        },
    )
    strength_score = compute_strength_score(item, selected_date, context)
    today_score = compute_today_score(item, selected_date, context)
    narrative_score = compute_narrative_score(item, selected_date, context)
    final_score = compute_final_daily_score(
        strength_score=strength_score,
        today_score=today_score,
        narrative_score=narrative_score,
        config=config,
    )

    thresholds = config.get("thresholds") if isinstance(config.get("thresholds"), Mapping) else {}
    confidence_min = _safe_float(thresholds.get("humanizer_confidence_min"), 0.35)
    eligible_strength_min = _safe_float(thresholds.get("eligible_strength_min"), 0.18)
    eligible_today_min = _safe_float(thresholds.get("eligible_today_min"), 0.12)
    eligible_narrative_min = _safe_float(thresholds.get("eligible_narrative_min"), 0.12)

    event_id = str(item.get("event_id") or "").strip()
    top_event_ids = {str(token).strip() for token in (selected_day_context.get("top_event_ids") or []) if str(token).strip()}
    explicit_lunation = _is_explicit_lunation(item, context["card"])
    short_window = _is_short_window(item, context["card"], config)
    orb = _safe_float(item.get("orb_deg"), 99.0)
    max_orb = _safe_float((config.get("limits") or {}).get("orb_max_deg"), 6.0)
    humanizer_confidence = _safe_float(context["narrative_metrics"].get("humanizer_confidence"), 0.0)
    eligible = (
        orb <= max_orb
        and humanizer_confidence >= confidence_min
        and (
            short_window
            or explicit_lunation
            or event_id in top_event_ids
            or strength_score >= eligible_strength_min
            or today_score >= eligible_today_min
            or narrative_score >= eligible_narrative_min
        )
    )

    high_score_candidate_min = _safe_float(thresholds.get("high_score_candidate_min"), 0.58)
    meaningful_event_min = _safe_float(thresholds.get("meaningful_event_min"), 0.42)
    qualifies = eligible and (
        short_window
        or explicit_lunation
        or event_id in top_event_ids
        or final_score >= high_score_candidate_min
        or today_score >= 0.22
    )
    meaningful = eligible and (
        qualifies
        or final_score >= meaningful_event_min
        or (narrative_score >= 0.20 and today_score >= 0.16)
    )

    return {
        "event_id": event_id,
        "item": dict(item),
        "card": dict(context["card"]),
        "preview": dict(context["preview"]),
        "context": dict(context),
        "house": context["house"],
        "aspect_mode": context["aspect_mode"],
        "tone_face": str(context["preview"].get("tone_face") or ""),
        "source_horizon": context["source_horizon"],
        "strength_score": strength_score,
        "today_score": today_score,
        "narrative_score": narrative_score,
        "score": final_score,
        "score_breakdown": {
            "strength_score": strength_score,
            "today_score": today_score,
            "narrative_score": narrative_score,
            "humanizer_confidence": humanizer_confidence,
        },
        "short_window": short_window,
        "explicit_lunation": explicit_lunation,
        "selected_day_top_event": event_id in top_event_ids,
        "qualifies": qualifies,
        "meaningful": meaningful,
        "eligible": eligible,
        "redundancy_key": str(context["narrative_metrics"].get("redundancy_key") or ""),
    }


def _rerank_daily_rows(rows: List[Dict[str, Any]], *, max_daily_cards: int, config: Mapping[str, Any]) -> List[Dict[str, Any]]:
    penalties = config.get("penalties") if isinstance(config.get("penalties"), Mapping) else {}
    balance = config.get("balance") if isinstance(config.get("balance"), Mapping) else {}
    pool = [dict(row) for row in rows]
    selected: List[Dict[str, Any]] = []

    while pool and len(selected) < max_daily_cards:
        best_idx = 0
        best_score = float("-inf")
        for idx, row in enumerate(pool):
            rerank_score = _safe_float(row.get("score"), 0.0)
            applied_penalties: List[Dict[str, float]] = []

            if any(sel.get("house") == row.get("house") and row.get("house") is not None for sel in selected):
                penalty = _safe_float(penalties.get("same_house_penalty"), 0.08)
                rerank_score -= penalty
                applied_penalties.append({"same_house_penalty": penalty})
            if any(sel.get("aspect_mode") == row.get("aspect_mode") for sel in selected):
                penalty = _safe_float(penalties.get("same_aspect_mode_penalty"), 0.06)
                rerank_score -= penalty
                applied_penalties.append({"same_aspect_mode_penalty": penalty})
            if any(sel.get("tone_face") == row.get("tone_face") for sel in selected):
                penalty = _safe_float(penalties.get("same_tone_penalty"), 0.04)
                rerank_score -= penalty
                applied_penalties.append({"same_tone_penalty": penalty})
            if any(sel.get("redundancy_key") == row.get("redundancy_key") for sel in selected):
                penalty = _safe_float(penalties.get("redundancy_penalty"), 0.07)
                rerank_score -= penalty
                applied_penalties.append({"redundancy_penalty": penalty})

            if selected and all(str(sel.get("tone_face") or "") == "shadow" for sel in selected):
                if str(row.get("tone_face") or "") in {"flow", "growth"}:
                    rerank_score += _safe_float(balance.get("prefer_non_shadow_bonus"), 0.05)
                elif str(row.get("tone_face") or "") == "shadow":
                    rerank_score -= _safe_float(balance.get("all_shadow_penalty"), 0.03)

            if rerank_score > best_score:
                best_score = rerank_score
                best_idx = idx
                row["rerank_score"] = round(rerank_score, 4)
                row["rerank_penalties"] = applied_penalties

        selected.append(pool.pop(best_idx))
    return selected


def select_daily_and_period_event_cards(
    *,
    raw_events: Sequence[Mapping[str, Any]],
    event_cards: Sequence[Mapping[str, Any]],
    selected_date: str,
    selected_day_context: Mapping[str, Any] | None = None,
    natal: Mapping[str, Any] | None = None,
    event_v2_by_id: Mapping[str, Mapping[str, Any]] | None = None,
) -> Dict[str, Any]:
    config = load_daily_selection_config()
    thresholds = config.get("thresholds") if isinstance(config.get("thresholds"), Mapping) else {}
    limits = config.get("limits") if isinstance(config.get("limits"), Mapping) else {}
    max_daily_cards = max(1, _safe_int(limits.get("max_daily_cards")) or 2)
    max_period_cards = max(1, _safe_int(limits.get("max_period_cards")) or 3)
    meaningful_event_min = _safe_float(thresholds.get("meaningful_event_min"), 0.42)

    selected_day_context = dict(selected_day_context or {})
    event_card_index = {
        str(card.get("event_id") or "").strip(): dict(card)
        for card in event_cards
        if isinstance(card, Mapping) and str(card.get("event_id") or "").strip()
    }
    v2_index = {
        str(event_id).strip(): dict(meta)
        for event_id, meta in (event_v2_by_id or {}).items()
        if str(event_id).strip() and isinstance(meta, Mapping)
    }

    candidate_items_by_id: Dict[str, Dict[str, Any]] = {}
    for item in raw_events:
        if not isinstance(item, Mapping) or not _is_public_allowed(item):
            continue
        event_id = str(item.get("event_id") or "").strip()
        if event_id:
            candidate_items_by_id[event_id] = dict(item)
    for event_id, card in event_card_index.items():
        if event_id and event_id not in candidate_items_by_id:
            candidate_items_by_id[event_id] = dict(card)

    scored_rows = [
        _build_row(
            item,
            selected_date=selected_date,
            selected_day_context=selected_day_context,
            existing_by_id=event_card_index,
            natal=natal,
            event_v2_by_id=v2_index,
            config=config,
        )
        for item in candidate_items_by_id.values()
    ]
    scored_rows.sort(
        key=lambda row: (
            -int(row["explicit_lunation"]),
            -int(row["selected_day_top_event"]),
            -int(row["short_window"]),
            -float(row["score"]),
            str(row["event_id"]),
        )
    )

    qualified_rows = [row for row in scored_rows if row["qualifies"] and row["meaningful"]]
    daily_rows = _rerank_daily_rows(qualified_rows, max_daily_cards=max_daily_cards, config=config)

    used_period_fallback = False
    if not daily_rows:
        fallback_pool = [row for row in scored_rows if row["meaningful"] and row["score"] >= meaningful_event_min]
        if fallback_pool:
            fallback_pool = sorted(
                fallback_pool,
                key=lambda row: (-float(row["narrative_score"]), -float(row["today_score"]), -float(row["score"]), str(row["event_id"])),
            )
            daily_rows = [fallback_pool[0]]
            used_period_fallback = True

    daily_cards: List[Dict[str, Any]] = []
    for row in daily_rows:
        card = dict(row["card"])
        card["daily_score"] = row["score"]
        daily_cards.append(
            generate_daily_from_event(
                card,
                score=row["score"],
                is_period_derived=bool(used_period_fallback or row["source_horizon"] != "daily"),
                force_daily_horizon=True,
            )
        )

    period_cards: List[Dict[str, Any]] = []
    period_ids: set[str] = set()
    for card in event_cards:
        if not isinstance(card, Mapping):
            continue
        event_id = str(card.get("event_id") or "").strip()
        horizon = str(card.get("horizon") or "").strip().lower()
        if not event_id or horizon != "period" or event_id in period_ids:
            continue
        period_ids.add(event_id)
        period_cards.append(dict(card))
        if len(period_cards) >= max_period_cards:
            break

    for row in daily_rows:
        if row["source_horizon"] == "daily":
            continue
        if row["event_id"] in period_ids or len(period_cards) >= max_period_cards:
            continue
        period_ids.add(row["event_id"])
        period_cards.append(dict(row["card"]))

    return {
        "daily_event_cards": daily_cards,
        "period_event_cards": period_cards,
        "daily_selection": {
            "used_period_fallback": used_period_fallback,
            "period_only_note": (
                "Bugün kısa vadeli bir tetikten çok, arkada çalışan tema öne çıkıyor."
                if used_period_fallback and period_cards
                else ""
            ),
            "daily_count": len(daily_cards),
            "period_count": len(period_cards),
            "selected_day_top_event_ids": sorted(
                {
                    str(token).strip()
                    for token in (selected_day_context.get("top_event_ids") or [])
                    if str(token).strip()
                }
            ),
            "candidate_event_ids": [str(row["event_id"]) for row in daily_rows],
            "score_breakdown": {
                str(row["event_id"]): {
                    "strength_score": row["strength_score"],
                    "today_score": row["today_score"],
                    "narrative_score": row["narrative_score"],
                    "final_daily_score": row["score"],
                    "rerank_score": row.get("rerank_score"),
                    "rerank_penalties": row.get("rerank_penalties", []),
                    "source_horizon": row["source_horizon"],
                    "tone_face": row["tone_face"],
                    "aspect_mode": row["aspect_mode"],
                }
                for row in scored_rows[:10]
            },
        },
    }
