from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


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


class UserCompact(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    profile: Optional[str] = None
    domains: List[Dict[str, Any]] = Field(default_factory=list)
    micro_insights: List[Dict[str, Any]] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)
    tone_profile: Optional[Dict[str, Any]] = None


class PublicNatalView(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    locale: str = "tr"
    core_story: Optional[str] = None
    core_story_ui: Optional[Dict[str, Any]] = None
    user_compact: Optional[UserCompact] = None
    upper_meaning: Optional[Dict[str, Any]] = None
    theme_scores: Optional[Dict[str, Any]] = None
    meta_summary: PublicMetaSummary
    meaning_weighting: Dict[str, Any]
    data_quality_summary: Optional[Dict[str, Any]] = None
    narrative_anchor: PublicNarrativeAnchor
    natal_graph_compact: Optional[Dict[str, Any]] = None
    profile_narrative: Optional[Dict[str, Any]] = None
    sections_v2: List[Dict[str, Any]] = Field(default_factory=list)
    supporting_threads: List[Dict[str, Any]] = Field(default_factory=list)
    flags: PublicFlags
