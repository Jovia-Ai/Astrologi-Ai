from __future__ import annotations

import re
from typing import Any, Dict, List, Mapping, Optional, Tuple
import unicodedata

from app.narrative.humanize_en import humanize_en_text
from app.transit.narrative.archetype_engine import build_insight_pack
from app.transit.narrative.composer import compose_event_summary_from_item, compose_upper_meaning_line
from app.transit.narrative.public_voice_en import (
    build_insight_pack_en,
    build_signature_text_en,
    compose_event_summary_en,
    compose_upper_meaning_line_en,
    rewrite_event_card_en,
    rewrite_period_core_en,
    rewrite_period_summary_en,
)
from app.transit.narrative.deep_archetype_engine import (
    build_active_event_cards,
    build_daily_line,
    build_event_card,
    build_period_core,
    pick_top_event,
)
from app.transit.narrative.text_quality_tr import tr_normalize

from .public_models import Block, PublicEvent, PublicPeriod, PublicPeriodSpace, PublicPeriodSummary, PublicTransitResponse

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

_TURKISH_UPPER_MAP = {
    "i": "İ",
    "ı": "I",
    "ğ": "Ğ",
    "ü": "Ü",
    "ş": "Ş",
    "ö": "Ö",
    "ç": "Ç",
}

HOUSE_LABEL_TR = {
    1: "benlik/duruş",
    2: "özdeğer/maddi düzen",
    3: "zihin/iletişim",
    4: "ev/iç güven",
    5: "yaratıcılık/keyif",
    6: "rutin/sağlık",
    7: "ilişkiler/ortaklık",
    8: "paylaşım/dönüşüm",
    9: "inanç/ufuk",
    10: "kariyer/görünürlük",
    11: "topluluk/hedefler",
    12: "bilinçaltı/çözülme",
}

ASPECT_SYMBOL = {
    "conjunction": "☌",
    "square": "□",
    "trine": "△",
    "sextile": "✶",
    "opposition": "☍",
    "quincunx": "⚻",
}

PHASE_MAP = {
    "applying": "applying",
    "separating": "separating",
    "exact": "exact",
    "exactish": "exact",
}

DURATION_MAP = {
    "short": "days",
    "medium": "weeks",
    "long": "months",
    "hours": "hours",
    "days": "days",
    "weeks": "weeks",
    "months": "months",
}

PUBLIC_BLOCKED_POINTS = {"fortune", "lilith", "south node", "north node", "vertex"}
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
DEFAULT_PERIOD_PEAK_TIMELINE_ITEMS = 4

_EVENT_CARD_DISPLAY_TEXT_KEYS = frozenset(
    {
        "headline",
        "opening",
        "essence",
        "asks",
        "watchout",
        "what_it_builds",
        "technical_note",
        "title",
        "signature_tr",
        "teaser",
        "big_picture",
        "mechanism",
        "why_now",
        "conflict",
        "shadow",
        "upper",
        "upper_meaning",
        "extra_line",
        "time_hint",
        "time_hint_tr",
        "felt_line_tr",
        "why_it_feels_this_way_tr",
        "guidance_micro_tr",
        "signal_label_tr",
        "tone_label_tr",
        "house_touchpoint_tr",
        "house_touchpoint_hint_tr",
        "period_opening",
        "core_story",
        "summary",
        "one_liner",
        "lead",
        "growth_edge",
        "relational_or_life_expression",
        "contribution",
    }
)
_EVENT_CARD_DISPLAY_LIST_KEYS = frozenset({"guidance", "watch_out", "hook_tags"})
_PERIOD_STORY_TEXT_KEYS = frozenset(
    {
        "title",
        "lead",
        "period_opening",
        "big_picture",
        "mechanism",
        "growth_edge",
        "relational_or_life_expression",
        "what_it_builds",
        "contribution",
        "upper_meaning",
    }
)


def _normalize_display_text(value: Any, *, locale: str = "tr") -> Any:
    if not isinstance(value, str):
        return value
    text = " ".join(value.split()).strip()
    if not text:
        return ""
    if str(locale or "tr").lower().startswith("en"):
        if len(text.split()) <= 5 and not any(ch in text for ch in ".!?"):
            return text
        return humanize_en_text(text)
    try:
        normalized = tr_normalize(text)
        return re.sub(
            r"(^|[.!?]\s+)([a-zçğıöşü])",
            lambda match: f"{match.group(1)}{_TURKISH_UPPER_MAP.get(match.group(2), match.group(2).upper())}",
            normalized,
        )
    except Exception:
        return text


def _normalize_display_list(values: Any, *, locale: str = "tr") -> Any:
    if not isinstance(values, list):
        return values
    out: List[Any] = []
    for item in values:
        if isinstance(item, str):
            normalized = _normalize_display_text(item, locale=locale)
            if normalized:
                out.append(normalized)
        else:
            out.append(item)
    return out


def _normalize_period_story_copy(story: Mapping[str, Any], *, locale: str = "tr") -> Dict[str, Any]:
    out = dict(story)
    for key in _PERIOD_STORY_TEXT_KEYS:
        if key in out:
            out[key] = _normalize_display_text(out.get(key), locale=locale)
    return out


def _normalize_event_card_copy(card: Mapping[str, Any], *, locale: str = "tr") -> Dict[str, Any]:
    out = dict(card)
    for key in _EVENT_CARD_DISPLAY_TEXT_KEYS:
        if key in out:
            out[key] = _normalize_display_text(out.get(key), locale=locale)
    for key in _EVENT_CARD_DISPLAY_LIST_KEYS:
        if key in out:
            out[key] = _normalize_display_list(out.get(key), locale=locale)
    section_labels = out.get("section_labels")
    if isinstance(section_labels, Mapping):
        out["section_labels"] = {
            str(key): _normalize_display_text(value, locale=locale)
            for key, value in section_labels.items()
        }
    timing = out.get("timing")
    if isinstance(timing, Mapping):
        timing_out = dict(timing)
        if "timing_note" in timing_out:
            timing_out["timing_note"] = _normalize_display_text(
                timing_out.get("timing_note"),
                locale=locale,
            )
        out["timing"] = timing_out
    period_story = out.get("period_story")
    if isinstance(period_story, Mapping):
        out["period_story"] = _normalize_period_story_copy(period_story, locale=locale)
    return out


def _normalize_period_core_copy(period_core: Mapping[str, Any], *, locale: str = "tr") -> Dict[str, Any]:
    out = dict(period_core)
    for key in _PERIOD_STORY_TEXT_KEYS | {"core_story"}:
        if key in out:
            out[key] = _normalize_display_text(out.get(key), locale=locale)
    tags = out.get("tags")
    if isinstance(tags, list):
        normalized_tags: List[Any] = []
        for item in tags:
            if not isinstance(item, Mapping):
                normalized_tags.append(item)
                continue
            tag_out = dict(item)
            if "value" in tag_out:
                tag_out["value"] = _normalize_display_text(tag_out.get("value"), locale=locale)
            if "label" in tag_out:
                tag_out["label"] = _normalize_display_text(tag_out.get("label"), locale=locale)
            normalized_tags.append(tag_out)
        out["tags"] = normalized_tags
    story_tracks = out.get("story_tracks")
    if isinstance(story_tracks, Mapping):
        out["story_tracks"] = {
            str(track_id): _normalize_period_story_copy(track_story, locale=locale)
            if isinstance(track_story, Mapping)
            else track_story
            for track_id, track_story in story_tracks.items()
        }
    return out


def _normalize_timeline_copy(timeline: Mapping[str, Any], *, locale: str = "tr") -> Dict[str, Any]:
    out = dict(timeline)
    if "summary" in out:
        out["summary"] = _normalize_display_text(out.get("summary"), locale=locale)
    if "title" in out:
        out["title"] = _normalize_display_text(out.get("title"), locale=locale)
    if "lines" in out:
        out["lines"] = _normalize_display_list(out.get("lines"), locale=locale)
    return out


def _split_sentences(text: str) -> List[str]:
    if not text:
        return []
    parts = [p.strip() for p in text.replace("!", ".").replace("?", ".").split(".") if p.strip()]
    return parts


def _ensure_two_sentences(text: str) -> str:
    parts = _split_sentences(text)
    if not parts:
        return ""
    if len(parts) == 1:
        return f"{parts[0]}. Etki zamanla daha net hissedilebilir."
    return f"{parts[0]}. {parts[1]}."


def _normalize_text(value: str) -> str:
    lowered = (value or "").strip().lower()
    normalized = unicodedata.normalize("NFKD", lowered)
    stripped = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return " ".join(stripped.split())


def _titlecase_words(text: str) -> str:
    words = [w for w in str(text or "").split() if w]
    return " ".join(w[:1].upper() + w[1:] for w in words)


def _headline_fallback(text: str) -> str:
    words = [w for w in str(text or "").split() if w]
    short = " ".join(words[:5]) if words else ""
    return _titlecase_words(short)


def _is_generic_sentence(text: str) -> bool:
    generic = {
        "bu etki dikkatini belirli bir temaya yoneltebilir",
        "bu etki belirgin bir vurgu yaratabilir",
        "bu donemde birkac tema ayni anda hareketli gorunuyor",
    }
    norm = _normalize_text(text).replace(".", "")
    return norm in generic


def _severity_tag(item: Dict[str, Any]) -> str:
    ranking = item.get("ranking") or {}
    weight = float(ranking.get("weight") or 0.0)
    if weight <= 0.0:
        weight = float(ranking.get("strength") or item.get("strength") or 0.0)
    if weight >= 1.3:
        return "high"
    if weight >= 1.05:
        return "medium"
    return "low"


def _normalize_guidance(items: List[str]) -> List[str]:
    out: List[str] = []
    approach_added = False
    seen = set()
    for raw in items:
        if not raw:
            continue
        text = str(raw).strip()
        lower = text.lower()
        if lower.startswith(("yaklasim:", "uygulama:", "ritim:")):
            if approach_added:
                continue
            tail = text.split(":", 1)[1].strip() if ":" in text else text
            text = f"Yaklasim: {tail}"
            approach_added = True
        norm = _normalize_text(text)
        if norm in seen:
            continue
        seen.add(norm)
        out.append(_normalize_display_text(text))
        if len(out) >= 3:
            break
    return out


def _normalize_watch(items: List[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for raw in items:
        if not raw:
            continue
        text = str(raw).strip()
        norm = _normalize_text(text)
        if norm in seen:
            continue
        seen.add(norm)
        out.append(_normalize_display_text(text))
        if len(out) >= 2:
            break
    return out


def _pick_headline(interp: Dict[str, Any], recent: List[str] | None = None) -> str:
    headline = str(interp.get("headline_short") or interp.get("headline") or "").strip()
    if headline:
        candidates = [
            str(interp.get("headline_short") or "").strip(),
            str(interp.get("headline") or "").strip(),
        ]
        seen_recent = {h for h in (recent or []) if h}
        for cand in candidates:
            if cand and cand not in seen_recent:
                return cand
        return headline
    fallback_source = str(interp.get("one_liner") or interp.get("summary") or "").strip()
    return _headline_fallback(fallback_source)


def _pick_summary(interp: Dict[str, Any], tier: str) -> str:
    _ = tier
    summary_source = str(interp.get("one_liner") or "").strip()
    if not summary_source:
        summary_source = str(interp.get("summary") or "").strip()
    if _is_generic_sentence(summary_source):
        alt = str(interp.get("summary") or "").strip()
        if alt and not _is_generic_sentence(alt):
            summary_source = alt
    return _ensure_two_sentences(summary_source)


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _sign_tr_from_any(value: Any) -> str:
    text = _safe_text(value)
    if not text:
        return ""
    return SIGN_TR.get(text, text)


def _extract_sign(item: Dict[str, Any]) -> str:
    signs = item.get("signs") if isinstance(item.get("signs"), dict) else {}
    source_pos = item.get("source_pos") if isinstance(item.get("source_pos"), dict) else {}
    transit_pos = item.get("transit_pos") if isinstance(item.get("transit_pos"), dict) else {}
    target_pos = item.get("target_pos") if isinstance(item.get("target_pos"), dict) else {}
    return (
        _sign_tr_from_any(item.get("sign_tr"))
        or _sign_tr_from_any(item.get("signTR"))
        or _sign_tr_from_any(item.get("sign"))
        or _sign_tr_from_any(signs.get("transit_body_sign"))
        or _sign_tr_from_any(source_pos.get("sign"))
        or _sign_tr_from_any(transit_pos.get("sign"))
        or _sign_tr_from_any(target_pos.get("sign"))
        or "—"
    )


def _extract_degree_from_pos(pos: Dict[str, Any]) -> float | None:
    for key in ("deg", "degree", "lon", "longitude"):
        raw = pos.get(key)
        if raw is None:
            continue
        try:
            value = float(raw)
            if key in {"lon", "longitude"}:
                value = value % 30.0
            return value
        except (TypeError, ValueError):
            continue
    return None


def _extract_source_degree(item: Dict[str, Any]) -> float | None:
    for key in ("source_deg", "transit_deg"):
        raw = item.get(key)
        if raw is not None:
            try:
                return float(raw)
            except (TypeError, ValueError):
                pass
    source_pos = item.get("source_pos") if isinstance(item.get("source_pos"), dict) else {}
    transit_pos = item.get("transit_pos") if isinstance(item.get("transit_pos"), dict) else {}
    return _extract_degree_from_pos(source_pos) or _extract_degree_from_pos(transit_pos)


def _extract_target_degree(item: Dict[str, Any]) -> float | None:
    for key in ("target_deg", "natal_deg"):
        raw = item.get(key)
        if raw is not None:
            try:
                return float(raw)
            except (TypeError, ValueError):
                pass
    target_pos = item.get("target_pos") if isinstance(item.get("target_pos"), dict) else {}
    natal_pos = item.get("natal_pos") if isinstance(item.get("natal_pos"), dict) else {}
    return _extract_degree_from_pos(target_pos) or _extract_degree_from_pos(natal_pos)


def _normalize_phase(value: str | None) -> str | None:
    norm = _safe_text(value).lower()
    return PHASE_MAP.get(norm)


def _normalize_duration(value: str | None) -> str | None:
    norm = _safe_text(value).lower()
    return DURATION_MAP.get(norm)


def _target_frame(item: Dict[str, Any], target_name: str) -> str:
    frame = _safe_text(item.get("target_frame")).lower()
    if frame in {"natal", "transit"}:
        return frame
    if target_name in {"ASC", "MC", "DSC", "IC"}:
        return ""
    return "natal"


def _source_frame(item: Dict[str, Any]) -> str:
    frame = _safe_text(item.get("source_frame")).lower()
    if frame in {"transit", "natal"}:
        return frame
    return "transit"


def _build_signature_block(
    item: Dict[str, Any],
    *,
    phase: str | None,
    duration: str | None,
    locale: str = "tr",
) -> Block:
    if str(locale or "tr").lower().startswith("en"):
        return Block(
            type="signature",
            text=build_signature_text_en(item),
            items={},
            phase=_normalize_phase(phase),
            duration=_normalize_duration(duration),
        )

    source_body = _safe_text(item.get("source_name")) or _safe_text(item.get("transit_body")) or "Unknown"
    source_frame = _source_frame(item)
    source_frame_label = "Transit" if source_frame == "transit" else "Natal"
    source_sign = _extract_sign(item)
    source_deg = _extract_source_degree(item)
    source_deg_text = f"{source_deg:.1f}°" if source_deg is not None else "—"

    houses = item.get("houses") if isinstance(item.get("houses"), dict) else {}
    house_raw = houses.get("transit_in_natal_house")
    try:
        house_num = int(house_raw) if house_raw is not None else None
    except (TypeError, ValueError):
        house_num = None
    if house_num is None:
        house_part = "?. Ev (bilinmiyor)"
    else:
        house_label = HOUSE_LABEL_TR.get(house_num, "genel alan")
        house_part = f"{house_num}. Ev ({house_label})"

    parts: List[str] = [f"{source_frame_label} {source_body} {source_sign} {source_deg_text} — {house_part}"]

    aspect = str(item.get("aspect") or "").lower().strip()
    target = _safe_text(item.get("target_name")) or _safe_text(item.get("natal_point"))
    target_sign = _sign_tr_from_any(item.get("target_sign")) or "—"
    target_deg = _extract_target_degree(item)
    target_deg_text = f"{target_deg:.1f}°" if target_deg is not None else "—"
    target_frame = _target_frame(item, target)
    if target_frame == "natal":
        target_label = f"Natal {target}"
    elif target_frame == "transit":
        target_label = f"Transit {target}"
    else:
        target_label = target

    if aspect and target:
        symbol = ASPECT_SYMBOL.get(aspect, aspect)
        parts.append(f"{symbol} {target_label} {target_sign} {target_deg_text}")
    elif target:
        parts.append(target_label)

    orb_value: float | None = None
    for key in ("orb_deg", "orb", "abs_orb"):
        try:
            raw = item.get(key)
            if raw is not None:
                orb_value = float(raw)
                break
        except (TypeError, ValueError):
            continue
    if orb_value is not None:
        parts.append(f"orb {orb_value:.1f}°")

    normalized_phase = _normalize_phase(phase)
    normalized_duration = _normalize_duration(duration)
    if normalized_phase:
        parts.append(normalized_phase)
    if normalized_duration:
        parts.append(normalized_duration)

    structured = {
        "source": {
            "frame": source_frame,
            "body": source_body,
            "sign_tr": source_sign,
            "deg": source_deg,
        },
        "house": {
            "num": house_num,
            "label_tr": HOUSE_LABEL_TR.get(house_num, "genel alan") if house_num is not None else "—",
        },
        "aspect": {
            "code": aspect or None,
            "symbol": ASPECT_SYMBOL.get(aspect) if aspect else None,
        },
        "target": {
            "frame": target_frame or None,
            "body_or_angle": target or None,
            "sign_tr": target_sign,
            "deg": target_deg,
        },
        "orb": round(orb_value, 1) if orb_value is not None else None,
        "phase": normalized_phase,
        "duration": normalized_duration,
    }

    return Block(
        type="signature",
        text=" • ".join(parts),
        items=structured,
        phase=normalized_phase,
        duration=normalized_duration,
    )


def build_public_event(
    item: Dict[str, Any],
    *,
    headline_override: str | None = None,
    locale: str = "tr",
) -> PublicEvent:
    interp = item.get("interpretation") or {}
    event_id = str(item.get("event_id") or "")
    tier = (item.get("ranking") or {}).get("tier") or "support"
    severity_tag = _severity_tag(item)
    use_en = str(locale or "tr").lower().startswith("en")

    if use_en:
        headline = humanize_en_text(
            str(headline_override or interp.get("headline") or compose_event_summary_en(item)).strip(),
            max_sentences=1,
        ).strip(".")
        summary = _normalize_display_text(
            compose_event_summary_en(item, voice_style="you"),
            locale=locale,
        )
    else:
        headline = _normalize_display_text(headline_override or _pick_headline(interp), locale=locale)
        summary = _normalize_display_text(
            _ensure_two_sentences(compose_event_summary_from_item(item, voice_style="you")),
            locale=locale,
        )
    if not summary.strip():
        summary = _normalize_display_text(_pick_summary(interp, tier), locale=locale)
    time_hint = _normalize_display_text(
        str((interp.get("time_hint") or "").strip() if not use_en else ""),
        locale=locale,
    )
    phase = str(item.get("phase") or "").strip() or None
    duration = str(item.get("bucket") or "").strip() or None
    houses = item.get("houses") if isinstance(item.get("houses"), dict) else {}
    overlay_house = houses.get("transit_in_natal_house")
    try:
        overlay_house_int = int(overlay_house) if overlay_house is not None else None
    except (TypeError, ValueError):
        overlay_house_int = None
    upper_meaning = _normalize_display_text(
        compose_upper_meaning_line_en(
            transit_body=str(item.get("transit_body") or ""),
            natal_target=str(item.get("natal_point") or ""),
            house_overlay=overlay_house_int,
            seed=abs(hash((event_id, headline, tier))) % (2**31),
            voice_style="you",
        )
        if use_en
        else compose_upper_meaning_line(
            transit_body=str(item.get("transit_body") or ""),
            natal_target=str(item.get("natal_point") or ""),
            house_overlay=overlay_house_int,
            seed=abs(hash((event_id, headline, tier))) % (2**31),
            voice_style="you",
        ),
        locale=locale,
    )

    blocks: List[Block] = []
    if headline:
        blocks.append(Block(type="headline", text=headline))
    blocks.append(_build_signature_block(item, phase=phase, duration=duration, locale=locale))
    if summary:
        blocks.append(Block(type="summary", text=summary))
    if upper_meaning:
        blocks.append(Block(type="upper_meaning", text=upper_meaning))
    insight_pack = (
        build_insight_pack_en(item, voice_style="you")
        if use_en
        else build_insight_pack(item, voice_style="you")
    )
    insight_items = [
        {"key": "conflict", "text": _normalize_display_text(str(insight_pack.get("conflict") or ""), locale=locale)},
        {"key": "shadow", "text": _normalize_display_text(str(insight_pack.get("shadow") or ""), locale=locale)},
        {"key": "upper", "text": _normalize_display_text(str(insight_pack.get("upper") or ""), locale=locale)},
    ]
    blocks.append(Block(type="insight_pack", items=insight_items))
    if time_hint:
        blocks.append(Block(type="time_hint", text=time_hint, phase=phase, duration=duration))

    guidance_items = (
        [humanize_en_text(line, max_sentences=1) for line in rewrite_event_card_en({}, item).get("guidance", [])]
        if use_en
        else _normalize_guidance(list(interp.get("do") or []))
    )
    if guidance_items:
        blocks.append(Block(type="guidance", items=guidance_items))

    watch_items = (
        [humanize_en_text(line, max_sentences=1) for line in rewrite_event_card_en({}, item).get("watch_out", [])]
        if use_en
        else _normalize_watch(list(interp.get("watch") or []))
    )
    if watch_items:
        blocks.append(Block(type="watch_out", items=watch_items))

    cta = {"label": "Open detail" if use_en else "Detaya in", "action": "open_event_detail"}
    return PublicEvent(
        event_id=event_id,
        tier=tier,
        severity_tag=severity_tag,
        blocks=blocks,
        cta=cta,
    )


def _is_public_allowed(item: Dict[str, Any]) -> bool:
    transit_body = str(item.get("transit_body") or "").strip().lower()
    natal_point = str(item.get("natal_point") or "").strip().lower()
    return transit_body not in PUBLIC_BLOCKED_POINTS and natal_point not in PUBLIC_BLOCKED_POINTS


def _event_v2_index(response: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    payload = response.get("event_engine_v2") if isinstance(response.get("event_engine_v2"), Mapping) else {}
    events_by_id = payload.get("events_by_id") if isinstance(payload.get("events_by_id"), Mapping) else {}
    out: Dict[str, Dict[str, Any]] = {}
    for event_id, raw in events_by_id.items():
        if not str(event_id).strip() or not isinstance(raw, Mapping):
            continue
        out[str(event_id)] = dict(raw)
    return out


def _merge_event_v2(card: Mapping[str, Any], event_meta: Mapping[str, Any] | None) -> Dict[str, Any]:
    card_out = dict(card)
    if not isinstance(event_meta, Mapping):
        return card_out
    astro_event = dict(event_meta)
    for key in PUBLIC_EVENT_V2_FIELDS:
        if key in astro_event:
            card_out[key] = astro_event.get(key)
    card_out["astro_event"] = astro_event
    return card_out


def _merge_period_peak_timeline_v2(
    items: List[Dict[str, Any]],
    event_v2_by_id: Mapping[str, Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    if not items or not event_v2_by_id:
        return items
    out: List[Dict[str, Any]] = []
    for entry in items:
        event_id = str(entry.get("event_id") or "").strip()
        event_meta = event_v2_by_id.get(event_id)
        if not event_meta:
            out.append(entry)
            continue
        merged = dict(entry)
        merged["astro_event"] = dict(event_meta)
        if isinstance(merged.get("event_card"), Mapping):
            merged["event_card"] = _merge_event_v2(merged["event_card"], event_meta)
        out.append(merged)
    return out


def _global_period_story(period_core: Mapping[str, Any]) -> Dict[str, str]:
    return {
        "title": str(period_core.get("title") or ""),
        "lead": str(period_core.get("period_opening") or period_core.get("big_picture") or ""),
        "period_opening": str(period_core.get("period_opening") or ""),
        "big_picture": str(period_core.get("big_picture") or ""),
        "mechanism": str(period_core.get("mechanism") or ""),
        "growth_edge": str(period_core.get("growth_edge") or ""),
        "relational_or_life_expression": str(period_core.get("relational_or_life_expression") or ""),
        "what_it_builds": str(period_core.get("what_it_builds") or period_core.get("upper_meaning") or ""),
        "contribution": str(period_core.get("what_it_builds") or period_core.get("upper_meaning") or ""),
        "upper_meaning": str(period_core.get("upper_meaning") or ""),
    }


def _enrich_period_story(
    card: Mapping[str, Any],
    *,
    period_core: Mapping[str, Any],
    global_period_story: Mapping[str, Any],
    story_tracks: Mapping[str, Any],
    event_story_map: Mapping[str, Any],
) -> Dict[str, Any]:
    card_out = dict(card)
    if str(card_out.get("horizon") or "").strip().lower() != "period":
        return card_out
    event_id = str(card_out.get("event_id") or "").strip()
    track_id = str(card_out.get("story_track_id") or event_story_map.get(event_id) or "").strip()
    if track_id:
        card_out["story_track_id"] = track_id
    track_story = story_tracks.get(track_id) if track_id else None
    if isinstance(track_story, dict) and any(str(v).strip() for v in track_story.values()):
        card_out["period_story"] = dict(track_story)
    elif any(str(v).strip() for v in global_period_story.values()):
        card_out["period_story"] = dict(global_period_story)
    provenance = card_out.get("narrative_provenance")
    if isinstance(provenance, Mapping):
        updated = dict(provenance)
        updated["story_track_id"] = track_id
        updated["period_track_used"] = "period_story" in card_out
        card_out["narrative_provenance"] = updated
    return card_out


def _event_peak_date_utc(item: Mapping[str, Any]) -> str:
    timing = item.get("timing") if isinstance(item.get("timing"), Mapping) else {}
    return str(timing.get("peak_date_utc") or "").strip()


def _event_weight(item: Mapping[str, Any]) -> float:
    ranking = item.get("ranking") if isinstance(item.get("ranking"), Mapping) else {}
    try:
        return float(ranking.get("weight") or ranking.get("strength") or item.get("strength") or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _build_period_peak_timeline(
    response: Mapping[str, Any],
    *,
    filtered_items: List[Dict[str, Any]],
    period_core: Mapping[str, Any],
    locale: str = "tr",
    max_items: Optional[int] = None,
) -> List[Dict[str, Any]]:
    global_period_story = _global_period_story(period_core)
    story_tracks = period_core.get("story_tracks") if isinstance(period_core.get("story_tracks"), dict) else {}
    event_story_map = (
        period_core.get("_event_story_map")
        if isinstance(period_core.get("_event_story_map"), dict)
        else {}
    )
    natal = response.get("natal") if isinstance(response.get("natal"), Mapping) else {}
    candidates = [
        item
        for item in filtered_items
        if str(item.get("bucket") or "").strip().lower() in {"medium", "long"}
        and _event_peak_date_utc(item)
    ]
    candidates.sort(
        key=lambda item: (
            _event_peak_date_utc(item),
            -_event_weight(item),
            str(item.get("event_id") or ""),
        )
    )

    used_ids: set[str] = set()
    used_titles: set[str] = set()
    out: List[Dict[str, Any]] = []
    for item in candidates:
        event_id = str(item.get("event_id") or "").strip()
        if not event_id or event_id in used_ids:
            continue
        card = build_event_card(item, context={"natal": natal})
        if str(locale or "tr").lower().startswith("en"):
            card = rewrite_event_card_en(card, item=item)
        card = _normalize_event_card_copy(
            _enrich_period_story(
                card,
                period_core=period_core,
                global_period_story=global_period_story,
                story_tracks=story_tracks,
                event_story_map=event_story_map,
            ),
            locale=locale,
        )
        if str(card.get("horizon") or "").strip().lower() != "period":
            continue

        timing = card.get("timing") if isinstance(card.get("timing"), Mapping) else {}
        title = str(card.get("title") or "").strip()
        if title in used_titles:
            signature = str(card.get("signature_tr") or card.get("signature") or "").strip()
            if signature:
                title = signature
        used_ids.add(event_id)
        if title:
            used_titles.add(title)

        out.append(
            {
                "event_id": event_id,
                "title": _normalize_display_text(title, locale=locale),
                "signature_tr": _normalize_display_text(
                    str(card.get("signature_tr") or card.get("signature") or "").strip()
                    ,
                    locale=locale,
                ),
                "peak_date_utc": str(timing.get("peak_date_utc") or "").strip(),
                "entry_date_utc": str(timing.get("entry_date_utc") or "").strip(),
                "exit_date_utc": str(timing.get("exit_date_utc") or "").strip(),
                "bucket": str(card.get("bucket") or item.get("bucket") or "").strip(),
                "phase": str(card.get("phase") or item.get("phase") or "").strip(),
                "time_hint_tr": _normalize_display_text(
                    str(card.get("time_hint_tr") or card.get("time_hint") or "").strip()
                    ,
                    locale=locale,
                ),
                "event_card": card,
            }
        )
        if max_items is not None and len(out) >= max_items:
            break
    return out


def build_public_period(response: Dict[str, Any], *, locale: str = "tr") -> PublicPeriod:
    presentable = response.get("presentable") or {}
    summary = presentable.get("summary") or {}
    use_en = str(locale or "tr").lower().startswith("en")
    period_space_raw = presentable.get("period_space") or {}
    period_space = None
    if isinstance(period_space_raw, dict):
        period_space = PublicPeriodSpace(
            label=_normalize_display_text(period_space_raw.get("label"), locale=locale),
            one_liner=_normalize_display_text(period_space_raw.get("one_liner"), locale=locale),
        )

    core_story = _normalize_display_text(
        presentable.get("core_story") or summary.get("one_liner"),
        locale=locale,
    )
    top_item = ((response.get("display") or {}).get("items") or [None])[0]
    upper_meaning = ""
    if isinstance(top_item, dict):
        houses = top_item.get("houses") if isinstance(top_item.get("houses"), dict) else {}
        overlay_house = houses.get("transit_in_natal_house")
        try:
            overlay_house_int = int(overlay_house) if overlay_house is not None else None
        except (TypeError, ValueError):
            overlay_house_int = None
        upper_meaning = (
            compose_upper_meaning_line_en(
                transit_body=str(top_item.get("transit_body") or ""),
                natal_target=str(top_item.get("natal_point") or ""),
                house_overlay=overlay_house_int,
                seed=abs(hash((str(core_story or ""), str(top_item.get("event_id") or "")))) % (2**31),
            )
            if use_en
            else compose_upper_meaning_line(
                transit_body=str(top_item.get("transit_body") or ""),
                natal_target=str(top_item.get("natal_point") or ""),
                house_overlay=overlay_house_int,
                seed=abs(hash((str(core_story or ""), str(top_item.get("event_id") or "")))) % (2**31),
            )
        )
    if upper_meaning:
        core_story = _normalize_display_text(f"{(core_story or '').strip()} {upper_meaning}".strip(), locale=locale)
    main_theme = summary.get("main_theme") or "identity"
    if use_en:
        rewritten = rewrite_period_summary_en(
            {
                "core_story": core_story,
                "summary": {
                    "main_theme": main_theme,
                    "one_liner": summary.get("one_liner") or core_story,
                },
            },
            item=top_item if isinstance(top_item, dict) else None,
        )
        core_story = str(rewritten.get("core_story") or core_story)
        summary = rewritten.get("summary") if isinstance(rewritten.get("summary"), Mapping) else summary
    return PublicPeriod(
        core_story=core_story,
        summary=PublicPeriodSummary(
            main_theme=_normalize_display_text(summary.get("main_theme") or main_theme, locale=locale),
            one_liner=_normalize_display_text(summary.get("one_liner") or core_story, locale=locale),
        ),
        period_space=period_space,
    )


def build_public_response(
    response: Dict[str, Any],
    *,
    include_debug_artifacts: bool = True,
) -> Dict[str, Any]:
    locale = str(response.get("locale") or "tr")
    use_en = locale.lower().startswith("en")
    display = response.get("display") or {}
    items = display.get("items") or []
    filtered_items = [item for item in items if isinstance(item, dict) and _is_public_allowed(item)]
    item_by_id = {
        str(item.get("event_id") or "").strip(): item
        for item in filtered_items
        if isinstance(item, Mapping) and str(item.get("event_id") or "").strip()
    }
    multi_event_payload = (
        dict(response.get("event_engine_v2"))
        if isinstance(response.get("event_engine_v2"), Mapping)
        else {}
    )
    event_v2_by_id = _event_v2_index(response)
    event_cards = [
        _normalize_event_card_copy(card, locale=locale)
        for card in build_active_event_cards(response, max_cards=5)
    ]
    period_core = _normalize_period_core_copy(
        build_period_core(
            response,
            event_cards=event_cards,
            locale=locale,
        ),
        locale=locale,
    )
    top_item = filtered_items[0] if filtered_items else None
    if use_en:
        period_core = _normalize_period_core_copy(
            rewrite_period_core_en(period_core, item=top_item if isinstance(top_item, Mapping) else None),
            locale=locale,
        )
    global_period_story = _global_period_story(period_core)
    story_tracks = period_core.get("story_tracks") if isinstance(period_core.get("story_tracks"), dict) else {}
    event_story_map = (
        period_core.get("_event_story_map")
        if isinstance(period_core.get("_event_story_map"), dict)
        else {}
    )
    if event_cards:
        enriched_cards: List[Dict[str, Any]] = []
        for card in event_cards:
            event_id = str(card.get("event_id") or "").strip()
            card_item = item_by_id.get(event_id)
            if use_en:
                card = rewrite_event_card_en(card, item=card_item)
            enriched_cards.append(
                _normalize_event_card_copy(
                    _enrich_period_story(
                        card,
                        period_core=period_core,
                        global_period_story=global_period_story,
                        story_tracks=story_tracks,
                        event_story_map=event_story_map,
                    ),
                    locale=locale,
                )
            )
        event_cards = enriched_cards
    if event_v2_by_id and event_cards:
        event_cards = [
            _normalize_event_card_copy(
                _merge_event_v2(card, event_v2_by_id.get(str(card.get("event_id") or "").strip()))
                ,
                locale=locale,
            )
            for card in event_cards
        ]
    period_peak_timeline = _build_period_peak_timeline(
        response,
        filtered_items=filtered_items,
        period_core=period_core,
        locale=locale,
        max_items=DEFAULT_PERIOD_PEAK_TIMELINE_ITEMS,
    )
    period_peak_timeline = _merge_period_peak_timeline_v2(period_peak_timeline, event_v2_by_id)
    timeline = _normalize_timeline_copy(
        build_daily_line(
        str(response.get("transit_date") or ""),
        pick_top_event(response),
        context={"period_core": period_core},
        ),
        locale=locale,
    )
    if use_en and isinstance(top_item, Mapping):
        timeline = {
            **dict(timeline),
            "title": "Today",
            "summary": compose_event_summary_en(top_item),
            "lines": [
                build_insight_pack_en(top_item).get("conflict_short") or "",
                compose_upper_meaning_line_en(
                    transit_body=str(top_item.get("transit_body") or ""),
                    natal_target=str(top_item.get("natal_point") or ""),
                    house_overlay=_safe_int(
                        ((top_item.get("houses") or {}) if isinstance(top_item.get("houses"), Mapping) else {}).get("transit_in_natal_house")
                    ),
                ),
            ],
        }
        timeline = _normalize_timeline_copy(timeline, locale=locale)
    debug_events: List[Dict[str, Any]] = []
    if include_debug_artifacts:
        recent_headlines: List[str] = []
        for item in filtered_items[:8]:
            interp = item.get("interpretation") or {}
            headline = _pick_headline(interp, recent=recent_headlines)
            recent_headlines.append(headline)
            debug_events.append(
                build_public_event(
                    item,
                    headline_override=headline,
                    locale=locale,
                ).model_dump()
            )
    public = PublicTransitResponse(
        locale=locale,
        period=build_public_period(response, locale=locale),
        period_core=period_core,
        event_cards=event_cards,
        period_peak_timeline=period_peak_timeline,
        timeline=timeline,
        multi_event=multi_event_payload or None,
        personal_transit_rail=multi_event_payload.get("personal_transit_rail") if multi_event_payload else None,
        structural_chapter_rail=multi_event_payload.get("structural_chapter_rail") if multi_event_payload else None,
        solar_year_frame=(
            response.get("solar_year_frame")
            if isinstance(response.get("solar_year_frame"), Mapping)
            else (multi_event_payload.get("solar_year_frame") if multi_event_payload else None)
        ),
    )
    out = public.model_dump(exclude_none=True)
    if debug_events:
        out["_events_debug"] = debug_events
    return out
