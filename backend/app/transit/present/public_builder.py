from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import unicodedata

from .public_models import Block, PublicEvent, PublicPeriod, PublicPeriodSpace, PublicPeriodSummary, PublicTransitResponse


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
    summary_source = str(interp.get("one_liner") or "").strip()
    if not summary_source:
        summary_source = str(interp.get("summary") or "").strip()
    if _is_generic_sentence(summary_source) and tier in {"main", "support"}:
        alt = str(interp.get("summary") or "").strip()
        if alt and not _is_generic_sentence(alt):
            summary_source = alt
    return _ensure_two_sentences(summary_source)


def build_public_event(item: Dict[str, Any], *, headline_override: str | None = None) -> PublicEvent:
    interp = item.get("interpretation") or {}
    event_id = str(item.get("event_id") or "")
    tier = (item.get("ranking") or {}).get("tier") or "support"
    severity_tag = _severity_tag(item)

    headline = headline_override or _pick_headline(interp)
    summary = _pick_summary(interp, tier)
    where_short = str(interp.get("where_short") or "").strip()
    where_text = f"Bunu en cok {where_short} alaninda hissedebilirsin." if where_short else ""
    time_hint = str(interp.get("time_hint") or "").strip()
    phase = str(item.get("phase") or "").strip() or None
    duration = str(item.get("bucket") or "").strip() or None

    blocks: List[Block] = []
    if headline:
        blocks.append(Block(type="headline", text=headline))
    if summary:
        blocks.append(Block(type="summary", text=summary))
    if where_text:
        blocks.append(Block(type="where", text=where_text))
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
    main_theme = summary.get("main_theme") or "identity"
    return PublicPeriod(
        core_story=core_story,
        summary=PublicPeriodSummary(
            main_theme=main_theme,
            one_liner=summary.get("one_liner"),
        ),
        period_space=period_space,
    )


def build_public_response(response: Dict[str, Any]) -> Dict[str, Any]:
    display = response.get("display") or {}
    items = display.get("items") or []
    recent_headlines: List[str] = []
    deduped: Dict[Tuple[str, str, str], PublicEvent] = {}
    tier_rank = {"main": 3, "support": 2, "flavor": 1}
    severity_rank = {"high": 3, "medium": 2, "low": 1}
    for item in items:
        interp = item.get("interpretation") or {}
        headline = _pick_headline(interp, recent=recent_headlines)
        recent_headlines.append(headline)
        if len(recent_headlines) > 5:
            recent_headlines = recent_headlines[-5:]
        event = build_public_event(item, headline_override=headline)
        where_text = ""
        duration = ""
        for block in event.blocks:
            if block.type == "where":
                where_text = block.text or ""
            if block.type == "time_hint":
                duration = block.duration or ""
        key = (_normalize_text(headline), _normalize_text(where_text), _normalize_text(duration))
        existing = deduped.get(key)
        if not existing:
            deduped[key] = event
            continue
        existing_tier = tier_rank.get(existing.tier, 0)
        new_tier = tier_rank.get(event.tier, 0)
        if new_tier > existing_tier:
            deduped[key] = event
            continue
        if new_tier == existing_tier:
            if severity_rank.get(event.severity_tag, 0) > severity_rank.get(
                existing.severity_tag, 0
            ):
                deduped[key] = event
    events = list(deduped.values())
    public = PublicTransitResponse(
        locale=str(response.get("locale") or "tr"),
        period=build_public_period(response),
        events=events,
    )
    return public.model_dump()
