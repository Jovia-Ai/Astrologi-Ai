from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def evaluate_daily_selection(
    *,
    scored_rows: Sequence[Mapping[str, Any]],
    daily_rows: Sequence[Mapping[str, Any]],
    used_period_fallback: bool,
) -> Dict[str, Any]:
    house_keys = {row.get("house") for row in daily_rows if row.get("house") is not None}
    aspect_modes = {str(row.get("aspect_mode") or "") for row in daily_rows if str(row.get("aspect_mode") or "")}
    tone_faces = [str(row.get("tone_face") or "") for row in daily_rows if str(row.get("tone_face") or "")]
    return {
        "candidate_count": len(scored_rows),
        "selected_count": len(daily_rows),
        "used_period_fallback": bool(used_period_fallback),
        "avg_narrative_score": round(
            sum(_safe_float(row.get("narrative_score"), 0.0) for row in daily_rows) / max(1, len(daily_rows)),
            4,
        ),
        "avg_delta_salience_score": round(
            sum(_safe_float(row.get("delta_salience_score"), 0.0) for row in daily_rows) / max(1, len(daily_rows)),
            4,
        ),
        "avg_personalization_score": round(
            sum(_safe_float(row.get("personalization_score"), 0.0) for row in daily_rows) / max(1, len(daily_rows)),
            4,
        ),
        "house_diversity": len(house_keys),
        "aspect_mode_diversity": len(aspect_modes),
        "shadow_only_surface": bool(tone_faces) and all(face == "shadow" for face in tone_faces),
    }


def evaluate_period_selection(
    *,
    selected: Sequence[Mapping[str, Any]],
    story_scores: Mapping[str, Any],
    chapter_roles: Mapping[str, Mapping[str, Any]],
) -> Dict[str, Any]:
    selected_ids = [str(item.get("event_id") or "") for item in selected if str(item.get("event_id") or "")]
    domains = {str(item.get("domain") or item.get("house_domain") or "") for item in selected if str(item.get("domain") or item.get("house_domain") or "")}
    roles = {
        str((chapter_roles.get(event_id) or {}).get("role") or "")
        for event_id in selected_ids
        if str((chapter_roles.get(event_id) or {}).get("role") or "")
    }
    avg_story_score = sum(_safe_float(story_scores.get(event_id), 0.0) for event_id in selected_ids) / max(1, len(selected_ids))
    avg_personalization_bonus = sum(_safe_float(item.get("personalization_bonus"), 0.0) for item in selected) / max(1, len(selected))
    return {
        "selected_count": len(selected_ids),
        "distinct_domains": len({domain for domain in domains if domain}),
        "distinct_roles": len(roles),
        "avg_story_score": round(avg_story_score, 4),
        "avg_personalization_bonus": round(avg_personalization_bonus, 4),
        "spine_event_id": selected_ids[0] if selected_ids else "",
        "spine_role": str((chapter_roles.get(selected_ids[0]) or {}).get("role") or "") if selected_ids else "",
    }
