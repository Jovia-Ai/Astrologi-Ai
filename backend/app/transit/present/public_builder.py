from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import unicodedata

from app.transit.narrative.archetype_engine import build_insight_pack
from app.transit.narrative.composer import compose_event_summary_from_item, compose_upper_meaning_line
from app.transit.narrative.deep_archetype_engine import (
    build_active_event_cards,
    build_daily_line,
    build_period_core,
    pick_top_event,
)

from .public_models import Block, PublicEvent, PublicPeriod, PublicPeriodSpace, PublicPeriodSummary, PublicTransitResponse

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

HOUSE_LABEL_TR = {
    1: "benlik/durus",
    2: "ozdeger/maddi duzen",
    3: "zihin/iletisim",
    4: "ev/ic guven",
    5: "yaraticilik/keyif",
    6: "rutin/saglik",
    7: "iliskiler/ortaklik",
    8: "paylasim/donusum",
    9: "inanc/ufuk",
    10: "kariyer/gorunurluk",
    11: "topluluk/hedefler",
    12: "bilincalti/cozulme",
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
        out.append(text)
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
        out.append(text)
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


def _build_signature_block(item: Dict[str, Any], *, phase: str | None, duration: str | None) -> Block:
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


def build_public_event(item: Dict[str, Any], *, headline_override: str | None = None) -> PublicEvent:
    interp = item.get("interpretation") or {}
    event_id = str(item.get("event_id") or "")
    tier = (item.get("ranking") or {}).get("tier") or "support"
    severity_tag = _severity_tag(item)

    headline = headline_override or _pick_headline(interp)
    summary = _ensure_two_sentences(compose_event_summary_from_item(item, voice_style="you"))
    if not summary.strip():
        summary = _pick_summary(interp, tier)
    time_hint = str(interp.get("time_hint") or "").strip()
    phase = str(item.get("phase") or "").strip() or None
    duration = str(item.get("bucket") or "").strip() or None
    houses = item.get("houses") if isinstance(item.get("houses"), dict) else {}
    overlay_house = houses.get("transit_in_natal_house")
    try:
        overlay_house_int = int(overlay_house) if overlay_house is not None else None
    except (TypeError, ValueError):
        overlay_house_int = None
    upper_meaning = compose_upper_meaning_line(
        transit_body=str(item.get("transit_body") or ""),
        natal_target=str(item.get("natal_point") or ""),
        house_overlay=overlay_house_int,
        seed=abs(hash((event_id, headline, tier))) % (2**31),
        voice_style="you",
    )

    blocks: List[Block] = []
    if headline:
        blocks.append(Block(type="headline", text=headline))
    blocks.append(_build_signature_block(item, phase=phase, duration=duration))
    if summary:
        blocks.append(Block(type="summary", text=summary))
    if upper_meaning:
        blocks.append(Block(type="upper_meaning", text=upper_meaning))
    insight_pack = build_insight_pack(item, voice_style="you")
    insight_items = [
        {"key": "conflict", "text": str(insight_pack.get("conflict") or "")},
        {"key": "shadow", "text": str(insight_pack.get("shadow") or "")},
        {"key": "upper", "text": str(insight_pack.get("upper") or "")},
    ]
    blocks.append(Block(type="insight_pack", items=insight_items))
    if time_hint:
        blocks.append(Block(type="time_hint", text=time_hint, phase=phase, duration=duration))

    guidance_items = _normalize_guidance(list(interp.get("do") or []))
    if guidance_items:
        blocks.append(Block(type="guidance", items=guidance_items))

    watch_items = _normalize_watch(list(interp.get("watch") or []))
    if watch_items:
        blocks.append(Block(type="watch_out", items=watch_items))

    cta = {"label": "Detaya in", "action": "open_event_detail"}
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


def build_public_period(response: Dict[str, Any]) -> PublicPeriod:
    presentable = response.get("presentable") or {}
    summary = presentable.get("summary") or {}
    period_space_raw = presentable.get("period_space") or {}
    period_space = None
    if isinstance(period_space_raw, dict):
        period_space = PublicPeriodSpace(
            label=period_space_raw.get("label"),
            one_liner=period_space_raw.get("one_liner"),
        )

    core_story = presentable.get("core_story") or summary.get("one_liner")
    top_item = ((response.get("display") or {}).get("items") or [None])[0]
    upper_meaning = ""
    if isinstance(top_item, dict):
        houses = top_item.get("houses") if isinstance(top_item.get("houses"), dict) else {}
        overlay_house = houses.get("transit_in_natal_house")
        try:
            overlay_house_int = int(overlay_house) if overlay_house is not None else None
        except (TypeError, ValueError):
            overlay_house_int = None
        upper_meaning = compose_upper_meaning_line(
            transit_body=str(top_item.get("transit_body") or ""),
            natal_target=str(top_item.get("natal_point") or ""),
            house_overlay=overlay_house_int,
            seed=abs(hash((str(core_story or ""), str(top_item.get("event_id") or "")))) % (2**31),
        )
    if upper_meaning:
        core_story = f"{(core_story or '').strip()} {upper_meaning}".strip()
    main_theme = summary.get("main_theme") or "identity"
    return PublicPeriod(
        core_story=core_story,
        summary=PublicPeriodSummary(
            main_theme=main_theme,
            one_liner=(summary.get("one_liner") or core_story),
        ),
        period_space=period_space,
    )


def build_public_response(response: Dict[str, Any]) -> Dict[str, Any]:
    display = response.get("display") or {}
    items = display.get("items") or []
    filtered_items = [item for item in items if isinstance(item, dict) and _is_public_allowed(item)]
    event_cards = build_active_event_cards(response, max_cards=5)
    period_core = build_period_core(response, event_cards=event_cards)
    global_period_story = {
        "title": str(period_core.get("title") or ""),
        "lead": str(period_core.get("big_picture") or ""),
        "big_picture": str(period_core.get("big_picture") or ""),
        "mechanism": str(period_core.get("mechanism") or ""),
        "contribution": str(period_core.get("upper_meaning") or ""),
        "upper_meaning": str(period_core.get("upper_meaning") or ""),
    }
    story_tracks = period_core.get("story_tracks") if isinstance(period_core.get("story_tracks"), dict) else {}
    event_story_map = (
        period_core.get("_event_story_map")
        if isinstance(period_core.get("_event_story_map"), dict)
        else {}
    )
    if event_cards:
        enriched_cards: List[Dict[str, Any]] = []
        for card in event_cards:
            card_out = dict(card)
            if str(card_out.get("horizon") or "").strip().lower() == "period":
                event_id = str(card_out.get("event_id") or "").strip()
                track_id = str(card_out.get("story_track_id") or event_story_map.get(event_id) or "").strip()
                if track_id:
                    card_out["story_track_id"] = track_id
                track_story = story_tracks.get(track_id) if track_id else None
                if isinstance(track_story, dict) and any(str(v).strip() for v in track_story.values()):
                    card_out["period_story"] = dict(track_story)
                elif any(str(v).strip() for v in global_period_story.values()):
                    card_out["period_story"] = dict(global_period_story)
            enriched_cards.append(card_out)
        event_cards = enriched_cards
    timeline = build_daily_line(
        str(response.get("transit_date") or ""),
        pick_top_event(response),
        context={"period_core": period_core},
    )
    debug_events = []
    recent_headlines: List[str] = []
    for item in filtered_items[:8]:
        interp = item.get("interpretation") or {}
        headline = _pick_headline(interp, recent=recent_headlines)
        recent_headlines.append(headline)
        debug_events.append(build_public_event(item, headline_override=headline).model_dump())
    public = PublicTransitResponse(
        locale=str(response.get("locale") or "tr"),
        period=build_public_period(response),
        period_core=period_core,
        event_cards=event_cards,
        timeline=timeline,
    )
    out = public.model_dump(exclude_none=True)
    if debug_events:
        out["_events_debug"] = debug_events
    return out
