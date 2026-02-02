from __future__ import annotations

import os
from typing import Any, Dict

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


def build_public_natal_view(response: Dict[str, Any], *, locale: str = "tr") -> Dict[str, Any]:
    meta = response.get("meta") or {}
    narrative_anchor = response.get("narrative_anchor") or {}
    meaning_weighting = response.get("meaning_weighting") or {}

    dynamic_insights_enabled = bool(response.get("dynamic_insights")) or bool(
        os.getenv("ENABLE_DYNAMIC_INSIGHTS", "false").strip().lower() in {"1", "true", "yes", "on"}
    )

    public = PublicNatalView(
        locale=locale or "tr",
        core_story=response.get("core_story"),
        user_compact=response.get("user_compact"),
        upper_meaning=response.get("upper_meaning_selected"),
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
        flags=PublicFlags(
            dynamic_insights_enabled=dynamic_insights_enabled,
            premium_mode=bool(response.get("premium_mode")),
        ),
    )
    return public.model_dump()
