from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

CONFIG_PATH = Path(__file__).resolve().parents[4] / "config" / "transit" / "selection_v3_config.yaml"

DEFAULT_CONFIG: Dict[str, Any] = {
    "limits": {
        "orb_max_deg": 6.0,
        "visibility_window_days": 3,
    },
    "narrative": {
        "generic_guidance": [
            "acele etme.",
            "ilk cümleye mecbur değilsin.",
            "hemen tepki verme.",
            "her şeyi bugün çözmeye çalışma.",
        ],
        "technical_tokens": [
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
        ],
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
    "structurality": {
        "importance_tier": {
            "critical": 1.0,
            "high": 0.84,
            "medium": 0.62,
            "low": 0.40,
        },
        "bucket": {
            "long": 0.86,
            "medium": 0.58,
            "short": 0.28,
        },
    },
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

ANGLE_POINTS = {"ASC", "DSC", "MC", "IC"}
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
def load_selection_v3_config() -> Mapping[str, Any]:
    config = dict(DEFAULT_CONFIG)
    if CONFIG_PATH.exists():
        try:
            payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {}
        if isinstance(payload, Mapping):
            config = _merge_config(config, payload)
    env_payload = os.getenv("JOVIA_SELECTION_V3_CONFIG", "").strip()
    if env_payload:
        try:
            override = json.loads(env_payload)
        except json.JSONDecodeError:
            override = {}
        if isinstance(override, Mapping):
            config = _merge_config(config, override)
    return config


def _days_from_selected(selected_date: str, raw: Any) -> int | None:
    import datetime as _dt

    head = _date_head(raw)
    if not head:
        return None
    try:
        return abs((_dt.date.fromisoformat(head) - _dt.date.fromisoformat(selected_date)).days)
    except ValueError:
        return None


def _signed_days_from_selected(selected_date: str, raw: Any) -> int | None:
    import datetime as _dt

    head = _date_head(raw)
    if not head:
        return None
    try:
        return (_dt.date.fromisoformat(head) - _dt.date.fromisoformat(selected_date)).days
    except ValueError:
        return None


def _aspect_mode(aspect: str) -> str:
    mapping = {
        "square": "friction",
        "opposition": "polarity",
        "conjunction": "concentration",
        "trine": "flow",
        "sextile": "opening",
    }
    return mapping.get(str(aspect or "").strip().lower(), "mixed")


def _event_family(item: Mapping[str, Any], card: Mapping[str, Any] | None, event_v2_meta: Mapping[str, Any] | None) -> str:
    for source in (event_v2_meta or {}, card or {}, item):
        family = str(source.get("event_family") or "").strip().lower()
        if family:
            return family
    return ""


def _event_subtype(item: Mapping[str, Any], card: Mapping[str, Any] | None, event_v2_meta: Mapping[str, Any] | None) -> str:
    for source in (event_v2_meta or {}, card or {}, item):
        subtype = str(source.get("event_subtype") or "").strip().lower()
        if subtype:
            return subtype
    return ""


def _timing_map(item: Mapping[str, Any], card: Mapping[str, Any] | None) -> Mapping[str, Any]:
    for source in (card or {}, item):
        timing = source.get("timing") if isinstance(source.get("timing"), Mapping) else {}
        if timing:
            return timing
    return {}


def _exact_in_days(item: Mapping[str, Any], card: Mapping[str, Any] | None) -> int | None:
    ranking = item.get("ranking") if isinstance(item.get("ranking"), Mapping) else {}
    exact = _safe_int(ranking.get("exact_in_days"))
    if exact is not None:
        return exact
    if isinstance(card, Mapping):
        tags = card.get("tags") if isinstance(card.get("tags"), Mapping) else {}
        return _safe_int(tags.get("exact_in_days"))
    return None


def _house_candidates(item: Mapping[str, Any], card: Mapping[str, Any] | None) -> list[int]:
    out: list[int] = []
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
    deduped: list[int] = []
    for house in out:
        if house not in deduped:
            deduped.append(house)
    return deduped


def _house_domain(house: int | None) -> str:
    return HOUSE_TO_DOMAIN.get(house or -1, "identity")


def _visibility_ratio(distance: int | None, window_days: int) -> float:
    if distance is None:
        return 0.0
    if distance > window_days:
        return 0.0
    return round(max(0.0, 1.0 - (distance / max(1, window_days))), 4)


def _guidance_value(guidance: str, config: Mapping[str, Any]) -> float:
    generic = {str(item).strip().lower() for item in ((config.get("narrative") or {}).get("generic_guidance") or [])}
    text = str(guidance or "").strip().lower()
    if not text:
        return 0.0
    if text in generic:
        return 0.52
    if any(token in text for token in ("cümle", "mesafe", "tempo", "alan", "hız", "heves", "beklenti", "duruş")):
        return 1.0
    return 0.76


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


def _is_house_anchor_visible(preview: Mapping[str, Any]) -> bool:
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


def _narrative_metrics(
    *,
    preview: Mapping[str, Any],
    body: str,
    house: int | None,
    aspect_mode: str,
    config: Mapping[str, Any],
) -> Dict[str, float]:
    narrative_cfg = config.get("narrative") if isinstance(config.get("narrative"), Mapping) else {}
    house_weights = narrative_cfg.get("house_weights") if isinstance(narrative_cfg.get("house_weights"), Mapping) else {}
    planet_weights = narrative_cfg.get("planet_translation") if isinstance(narrative_cfg.get("planet_translation"), Mapping) else {}
    aspect_weights = narrative_cfg.get("aspect_readability") if isinstance(narrative_cfg.get("aspect_readability"), Mapping) else {}
    technical_tokens = {str(token).strip().lower() for token in (narrative_cfg.get("technical_tokens") or [])}

    felt = str(preview.get("felt_line_tr") or "").strip()
    why = str(preview.get("why_it_feels_this_way_tr") or "").strip()
    guidance = str(preview.get("guidance_micro_tr") or "").strip()
    merged = " ".join([felt.lower(), why.lower(), guidance.lower()])
    house_visible = _is_house_anchor_visible(preview)
    non_technical = 1.0 if not any(token in merged for token in technical_tokens) else 0.0
    guidance_value = _guidance_value(guidance, config)
    humanizer_confidence = round(
        (
            _sentence_quality(felt)
            + _sentence_quality(why)
            + _sentence_quality(guidance)
            + guidance_value
            + (1.0 if house_visible else 0.35)
            + non_technical
        )
        / 6.0,
        4,
    )
    return {
        "house_clarity": round(_safe_float(house_weights.get(str(house or ""), 0.5), 0.5), 4),
        "planet_feel_clarity": round(_safe_float(planet_weights.get(body, planet_weights.get("default", 0.6)), 0.6), 4),
        "aspect_readability": round(_safe_float(aspect_weights.get(aspect_mode, aspect_weights.get("mixed", 0.6)), 0.6), 4),
        "guidance_value": round(guidance_value, 4),
        "humanizer_confidence": round(humanizer_confidence, 4),
        "house_anchor_visible": 1.0 if house_visible else 0.0,
    }


def _structurality(
    *,
    event: Mapping[str, Any],
    event_v2_meta: Mapping[str, Any] | None,
    config: Mapping[str, Any],
) -> Dict[str, float]:
    meta = event_v2_meta if isinstance(event_v2_meta, Mapping) else {}
    importance_cfg = ((config.get("structurality") or {}).get("importance_tier") or {})
    bucket_cfg = ((config.get("structurality") or {}).get("bucket") or {})
    importance_tier = str(meta.get("importance_tier") or event.get("importance_tier") or "").strip().lower()
    bucket = str(meta.get("time_scale") or event.get("bucket") or "").strip().lower()
    significance = _safe_float(meta.get("significance_score"), 0.0)
    lasting_change = _safe_float(meta.get("lasting_change_score"), 0.0)
    chapter_opening = _safe_float(meta.get("chapter_opening"), 0.0)
    recognition = _safe_float(meta.get("recognition_intensity"), 0.0)
    repeat_pass = max(0, _safe_int(meta.get("repeat_pass_count")) or 0)
    structural_flag = 1.0 if bool(meta.get("is_structural")) else 0.0

    structurality = (
        0.34 * structural_flag
        + 0.22 * significance
        + 0.18 * lasting_change
        + 0.14 * _safe_float(importance_cfg.get(importance_tier), 0.4)
        + 0.12 * _safe_float(bucket_cfg.get(bucket), 0.3)
    )
    root_cause_weight = min(1.0, (0.6 * significance) + (0.4 * recognition))
    return {
        "structurality": round(min(1.0, structurality), 4),
        "chapter_opening": round(min(1.0, max(chapter_opening, 0.0)), 4),
        "lasting_change": round(min(1.0, max(lasting_change, 0.0)), 4),
        "repeat_pass": float(repeat_pass),
        "root_cause_weight": round(min(1.0, root_cause_weight), 4),
    }


def _specificity(preview: Mapping[str, Any]) -> float:
    text = " ".join(
        [
            str(preview.get("felt_line_tr") or "").strip(),
            str(preview.get("why_it_feels_this_way_tr") or "").strip(),
            str(preview.get("guidance_micro_tr") or "").strip(),
        ]
    ).lower()
    if not text:
        return 0.0
    unique_tokens = {token for token in text.split() if len(token) >= 4}
    return round(min(1.0, max(0.28, len(unique_tokens) / 18.0)), 4)


def _memorability(preview: Mapping[str, Any]) -> float:
    felt = str(preview.get("felt_line_tr") or "").strip()
    if not felt:
        return 0.0
    words = [word for word in felt.split() if word]
    if 5 <= len(words) <= 13:
        return 0.88
    if 4 <= len(words) <= 16:
        return 0.72
    return 0.54


def _contrastability(aspect_mode: str, domain: str) -> float:
    base = {
        "friction": 0.9,
        "polarity": 0.96,
        "concentration": 0.82,
        "flow": 0.74,
        "opening": 0.68,
        "mixed": 0.55,
    }.get(aspect_mode, 0.55)
    if domain in {"relationships", "career", "mind"}:
        base += 0.04
    return round(min(1.0, base), 4)


def _label_alignment(labels: Sequence[str], house: int | None) -> float:
    if house is None or not labels:
        return 0.0
    accepted = LABEL_TO_DOMAIN.get(_house_domain(house), set())
    matched = 0
    for label in labels:
        token = str(label).strip().lower().replace(" ", "_")
        if any(part in token for part in accepted):
            matched += 1
    return round(min(1.0, matched / max(1, len(labels))), 4)


def build_event_feature_vector(
    event: Mapping[str, Any],
    *,
    selected_date: str,
    card: Mapping[str, Any] | None = None,
    selected_day_context: Mapping[str, Any] | None = None,
    event_v2_meta: Mapping[str, Any] | None = None,
    preview: Mapping[str, Any] | None = None,
    narrative_metrics: Mapping[str, Any] | None = None,
    personalization_context: Mapping[str, Any] | None = None,
    config: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    resolved = config if isinstance(config, Mapping) else load_selection_v3_config()
    card_map = dict(card or {})
    preview_map = dict(preview or {})
    day_context = dict(selected_day_context or {})
    personalization = dict(personalization_context or {})
    timing = _timing_map(event, card_map)
    body = str((event.get("transit_body") or card_map.get("transit_body") or "")).strip().lower()
    aspect = str((event.get("aspect") or card_map.get("aspect") or "")).strip().lower()
    phase = str((event.get("phase") or card_map.get("phase") or "")).strip().lower()
    bucket = str((event.get("bucket") or card_map.get("bucket") or "")).strip().lower()
    houses = _house_candidates(event, card_map)
    primary_house = houses[0] if houses else None
    aspect_mode = _aspect_mode(aspect)
    metrics = (
        dict(narrative_metrics)
        if isinstance(narrative_metrics, Mapping)
        else _narrative_metrics(
            preview=preview_map,
            body=body,
            house=primary_house,
            aspect_mode=aspect_mode,
            config=resolved,
        )
    )

    orb = _safe_float(event.get("orb_deg"), 99.0)
    max_orb = _safe_float(((resolved.get("limits") or {}).get("orb_max_deg")), 6.0)
    orb_ratio = max(0.0, min(1.0, 1.0 - (min(orb, max_orb) / max_orb)))
    phase_salience = {
        "exact": 1.0,
        "exactish": 0.9,
        "applying": 0.72,
        "separating": 0.38,
    }.get(phase, 0.24)
    planet_speed = {
        "moon": 1.0,
        "sun": 0.82,
        "mercury": 0.84,
        "mars": 0.84,
        "venus": 0.74,
        "jupiter": 0.42,
        "saturn": 0.30,
        "uranus": 0.26,
        "neptune": 0.22,
        "pluto": 0.24,
    }.get(body, 0.2)
    aspect_intensity = {
        "square": 0.96,
        "opposition": 0.94,
        "conjunction": 0.9,
        "trine": 0.72,
        "sextile": 0.62,
        "quincunx": 0.56,
    }.get(aspect, 0.48)
    angle_activation = 1.0 if str((event.get("natal_point") or card_map.get("natal_point") or "")).strip().upper() in ANGLE_POINTS or any(house in {1, 4, 7, 10} for house in houses) else 0.0
    family = _event_family(event, card_map, event_v2_meta)
    subtype = _event_subtype(event, card_map, event_v2_meta)
    event_family_salience = {
        "lunation_trigger": 1.0,
        "eclipse_trigger": 1.0,
        "station_event": 0.82,
        "house_ingress_event": 0.74,
        "retro_shift": 0.78,
        "direction_change": 0.78,
    }.get(family or subtype, 0.36)
    luminary_priority = 1.0 if body == "moon" else 0.86 if body == "sun" else 0.0
    natal_resonance = _safe_float(((card_map.get("natal_promise") or {}).get("score")), 0.0)
    if natal_resonance <= 0.0:
        natal_resonance = _safe_float(((event.get("natal_promise") or {}).get("score")), 0.0)

    peak_signed = _signed_days_from_selected(selected_date, timing.get("peak_date_utc"))
    entry_signed = _signed_days_from_selected(selected_date, timing.get("entry_date_utc"))
    exit_signed = _signed_days_from_selected(selected_date, timing.get("exit_date_utc"))
    peak_distance = abs(peak_signed) if peak_signed is not None else None
    entry_distance = abs(entry_signed) if entry_signed is not None else None
    exit_distance = abs(exit_signed) if exit_signed is not None else None
    selected_date_distance = min(
        [delta for delta in (peak_distance, entry_distance, exit_distance) if delta is not None],
        default=None,
    )

    visibility_window = max(1, _safe_int(((resolved.get("limits") or {}).get("visibility_window_days"))) or 3)
    anchor_signed = peak_signed if peak_signed is not None else entry_signed
    if anchor_signed is not None:
        today_visibility = _visibility_ratio(abs(anchor_signed), visibility_window)
        yesterday_visibility = _visibility_ratio(abs(anchor_signed + 1), visibility_window)
        tomorrow_visibility = _visibility_ratio(abs(anchor_signed - 1), visibility_window)
        delta_vs_yesterday = round(today_visibility - yesterday_visibility, 4)
        delta_vs_tomorrow = round(today_visibility - tomorrow_visibility, 4)
    else:
        today_visibility = 0.0
        delta_vs_yesterday = 0.0
        delta_vs_tomorrow = 0.0

    exact_in_days = _exact_in_days(event, card_map)
    is_peaking_today = bool((peak_distance == 0) or (exact_in_days == 0) or phase in {"exact", "exactish"})
    is_rising_today = bool(delta_vs_yesterday > 0.08 and today_visibility >= 0.2)
    is_releasing_today = bool(phase == "separating" and delta_vs_tomorrow > 0.08)

    structural_bits = _structurality(event=event, event_v2_meta=event_v2_meta, config=resolved)
    house_domain = _house_domain(primary_house)
    labels = [str(label).strip() for label in (day_context.get("labels") or []) if str(label).strip()]

    hot_houses = {_safe_int(value) for value in (personalization.get("natal_hot_houses") or [])}
    hot_houses.discard(None)
    dominant_domains = {str(value).strip().lower() for value in (personalization.get("dominant_domains") or []) if str(value).strip()}
    lens = str(personalization.get("lens") or "").strip().lower()
    behavioral_domains = {str(value).strip().lower() for value in (personalization.get("behavioral_domains") or []) if str(value).strip()}

    natal_hot_house_match = 1.0 if primary_house in hot_houses else 0.0
    dominant_theme_match = 1.0 if house_domain in dominant_domains else 0.0
    lens_match = 1.0 if lens and lens in {house_domain, aspect_mode, family, subtype} else 0.0
    behavioral_history_match = 1.0 if house_domain in behavioral_domains else 0.0

    feature_vector = {
        "event_id": str(event.get("event_id") or "").strip(),
        "strength": {
            "base_strength": round(_safe_float(event.get("strength"), 0.0), 4),
            "orb_proximity": round(orb_ratio, 4),
            "phase_salience": round(phase_salience, 4),
            "planet_speed": round(planet_speed, 4),
            "aspect_intensity": round(aspect_intensity, 4),
            "angle_activation": round(angle_activation, 4),
            "event_family_salience": round(event_family_salience, 4),
            "luminary_priority": round(luminary_priority, 4),
            "natal_resonance": round(min(1.0, natal_resonance), 4),
        },
        "time": {
            "selected_date_distance": selected_date_distance,
            "peak_distance": peak_distance,
            "entry_distance": entry_distance,
            "exit_distance": exit_distance,
            "delta_vs_yesterday": delta_vs_yesterday,
            "delta_vs_tomorrow": delta_vs_tomorrow,
            "is_rising_today": is_rising_today,
            "is_peaking_today": is_peaking_today,
            "is_releasing_today": is_releasing_today,
            "surface_alignment": _label_alignment(labels, primary_house),
        },
        "meaning": {
            "house_domain": house_domain,
            "house_clarity": metrics.get("house_clarity", 0.5),
            "planet_feel_clarity": metrics.get("planet_feel_clarity", 0.6),
            "aspect_mode": aspect_mode,
            "aspect_readability": metrics.get("aspect_readability", 0.6),
            "structurality": structural_bits["structurality"],
            "chapter_opening": structural_bits["chapter_opening"],
            "lasting_change": structural_bits["lasting_change"],
            "repeat_pass": int(structural_bits["repeat_pass"]),
            "root_cause_weight": structural_bits["root_cause_weight"],
            "surfaceability": round(
                min(
                    1.0,
                    (0.42 if bucket == "short" else 0.22)
                    + (0.22 if str(preview_map.get("felt_line_tr") or "").strip() else 0.0)
                    + (0.18 * _safe_float(metrics.get("humanizer_confidence"), 0.0))
                    + (0.18 * _label_alignment(labels, primary_house)),
                ),
                4,
            ),
            "guidance_value": metrics.get("guidance_value", 0.0),
            "specificity": _specificity(preview_map),
            "memorability": _memorability(preview_map),
            "contrastability": _contrastability(aspect_mode, house_domain),
        },
        "personalization": {
            "natal_hot_house_match": natal_hot_house_match,
            "dominant_theme_match": dominant_theme_match,
            "lens_match": lens_match,
            "behavioral_history_match": behavioral_history_match,
        },
        "redundancy": {
            "domain_key": house_domain,
            "tone_key": str(preview_map.get("tone_face") or "").strip().lower() or aspect_mode,
            "cluster_key": f"{house_domain}|{aspect_mode}|{body}",
        },
        "meta": {
            "family": family,
            "subtype": subtype,
            "body": body,
            "aspect": aspect,
            "phase": phase,
            "bucket": bucket,
            "primary_house": primary_house,
        },
    }
    return feature_vector
