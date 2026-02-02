from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict


class PublicMetaSummary(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    pressure_index: Optional[float] = None
    support_index: Optional[float] = None
    uncertainty: Optional[float] = None


class PublicNarrativeAnchor(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    domain: Optional[str] = None


class PublicFlags(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    dynamic_insights_enabled: bool = False
    premium_mode: bool = False


class PublicNatalView(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    locale: str = "tr"
    core_story: Optional[str] = None
    user_compact: Optional[Dict[str, str]] = None
    upper_meaning: Optional[Dict[str, Any]] = None
    theme_scores: Optional[Dict[str, Any]] = None
    meta_summary: PublicMetaSummary
    meaning_weighting: Dict[str, Any]
    data_quality_summary: Optional[Dict[str, Any]] = None
    narrative_anchor: PublicNarrativeAnchor
    flags: PublicFlags
