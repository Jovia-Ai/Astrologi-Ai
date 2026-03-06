from __future__ import annotations

import os
from typing import Any, Dict

from app.narrative.humanize_tr import humanize_compact_item, humanize_tr_text
from .public_models import (
    PublicFlags,
    PublicMetaSummary,
    PublicNarrativeAnchor,
    PublicNatalView,
)


def _allowlist_meaning_weighting(value: Any) -> Dict[str, Any]:
    allowed = {
        "primary_theme",
        "secondary_theme",
        "upper_meaning_allowed",
        "pressure_index",
        "support_index",
        "confidence",
        "load_state",
    }
    payload = value if isinstance(value, dict) else {}
    return {key: payload.get(key) for key in allowed if key in payload}


def build_public_natal_view(response: Dict[str, Any], *, locale: str = "tr", include_debug: bool = False) -> Dict[str, Any]:
    meta = response.get("meta") or {}
    narrative_anchor = response.get("narrative_anchor") or {}
    meaning_weighting = response.get("meaning_weighting") or {}

    dynamic_insights_enabled = bool(response.get("dynamic_insights")) or bool(
        os.getenv("ENABLE_DYNAMIC_INSIGHTS", "false").strip().lower() in {"1", "true", "yes", "on"}
    )

    compact = _humanize_user_compact(response.get("user_compact"))
    upper_meaning = _humanize_upper_meaning(response.get("upper_meaning_selected"))

    raw_core_story = response.get("core_story")
    core_story = (
        humanize_tr_text(str(raw_core_story), max_sentences=14)
        if isinstance(raw_core_story, str) and raw_core_story.strip()
        else raw_core_story
    )
    core_story_ui = _humanize_core_story_ui(response.get("core_story_ui"))

    public = PublicNatalView(
        locale=locale or "tr",
        core_story=core_story,
        core_story_ui=core_story_ui,
        user_compact=compact,
        upper_meaning=upper_meaning,
        theme_scores=response.get("theme_scores"),
        meta_summary=PublicMetaSummary(
            pressure_index=meta.get("pressure_index"),
            support_index=meta.get("support_index"),
            uncertainty=None,
        ),
        meaning_weighting=_allowlist_meaning_weighting(meaning_weighting),
        data_quality_summary=(response.get("data_quality") or {}).get("summary"),
        narrative_anchor=PublicNarrativeAnchor(
            domain=narrative_anchor.get("domain"),
        ),
        natal_graph_compact=_allowlist_natal_graph(response.get("natal_graph_compact")),
        profile_narrative=_humanize_profile_narrative(response.get("profile_narrative"), include_debug=include_debug),
        sections_v2=_humanize_sections_v2(response.get("sections_v2")),
        supporting_threads=_humanize_supporting_threads(response.get("supporting_threads")),
        flags=PublicFlags(
            dynamic_insights_enabled=dynamic_insights_enabled,
            premium_mode=bool(response.get("premium_mode")),
        ),
    )
    return public.model_dump()


def _humanize_user_compact(value: Any) -> Dict[str, Any] | None:
    compact = value if isinstance(value, dict) else None
    if not compact:
        return compact
    out = dict(compact)
    domains = out.get("domains") if isinstance(out.get("domains"), list) else []
    normalized_domains = []
    for domain in domains:
        if not isinstance(domain, dict):
            continue
        normalized = humanize_compact_item(domain)
        highlights = normalized.get("highlights") if isinstance(normalized.get("highlights"), list) else []
        normalized["highlights"] = [
            humanize_compact_item(item) if isinstance(item, dict) else item for item in highlights
        ]
        normalized_domains.append(normalized)
    out["domains"] = normalized_domains

    micro = out.get("micro_insights") if isinstance(out.get("micro_insights"), list) else []
    out["micro_insights"] = [
        humanize_compact_item(item) if isinstance(item, dict) else item for item in micro
    ]
    return out


def _humanize_upper_meaning(value: Any) -> Dict[str, Any] | None:
    payload = value if isinstance(value, dict) else None
    if not payload:
        return payload
    out = dict(payload)
    for key in ("title", "condition", "how_to_use", "message"):
        raw = out.get(key)
        if isinstance(raw, str) and raw.strip():
            out[key] = humanize_tr_text(raw, max_sentences=3)
    lines = out.get("lines")
    if isinstance(lines, list):
        out["lines"] = [humanize_tr_text(str(line), max_sentences=2) for line in lines if str(line).strip()]
    return out


def _allowlist_natal_graph(value: Any) -> Dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    allowed = {"house_rulers", "dominant_loops", "importance"}
    return {key: value.get(key) for key in allowed if key in value}


def _humanize_supporting_threads(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    out: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        entry = dict(item)
        for key, max_sentences in (("one_liner", 2), ("paragraph", 5), ("body", 5), ("micro", 2)):
            raw = entry.get(key)
            if isinstance(raw, str) and raw.strip():
                entry[key] = humanize_tr_text(raw, max_sentences=max_sentences)
        out.append(entry)
    return out


def _humanize_sections_v2(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    out: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        entry = dict(item)
        for key, max_sentences in (("subtitle", 2), ("body", 5), ("micro", 2)):
            raw = entry.get(key)
            if isinstance(raw, str) and raw.strip():
                entry[key] = humanize_tr_text(raw, max_sentences=max_sentences)
        out.append(entry)
    return out


def _humanize_profile_narrative(value: Any, *, include_debug: bool = False) -> Dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    public_payload = value.get("profile_public") if isinstance(value.get("profile_public"), dict) else {}
    blocks = public_payload.get("blocks") if isinstance(public_payload.get("blocks"), list) else []
    normalized_blocks: list[dict[str, Any]] = []
    for item in blocks:
        if not isinstance(item, dict):
            continue
        entry = dict(item)
        for key, max_sentences in (("headline", 2), ("teaser", 2), ("body", 5)):
            raw = entry.get(key)
            if isinstance(raw, str) and raw.strip():
                entry[key] = humanize_tr_text(raw, max_sentences=max_sentences)
        normalized_blocks.append(entry)
    out: Dict[str, Any] = {
        "profile_public": {
            "engine_version": public_payload.get("engine_version"),
            "blocks": normalized_blocks,
        }
    }
    if include_debug and isinstance(value.get("profile_internal"), dict):
        out["profile_internal"] = value.get("profile_internal")
    return out


def _humanize_core_story_ui(value: Any) -> Dict[str, Any] | None:
    payload = value if isinstance(value, dict) else None
    if not payload:
        return None
    out = dict(payload)
    headline = out.get("headline")
    if isinstance(headline, str) and headline.strip():
        out["headline"] = humanize_tr_text(headline, max_sentences=2)
    text = out.get("text")
    if isinstance(text, str) and text.strip():
        out["text"] = humanize_tr_text(text, max_sentences=5)
    return out
