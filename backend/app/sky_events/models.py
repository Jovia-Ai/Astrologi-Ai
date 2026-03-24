from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class GlobalSkyEvent(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    id: str
    slug: str
    event_type: str
    event_family: str
    title_tr: str
    short_title_tr: str
    status: str
    phase: str
    primary_body: Optional[str] = None
    secondary_body: Optional[str] = None
    bodies: List[str] = Field(default_factory=list)
    aspect: Optional[str] = None
    aspect_angle: Optional[int] = None
    sign: Optional[str] = None
    degree: Optional[float] = None
    degree_abs: Optional[float] = None
    starts_at: str
    exact_at: str
    ends_at: str
    visibility_window_start: str
    visibility_window_end: str
    importance_score: float = 0.0
    cultural_interest_score: float = 0.0
    readability_score: float = 0.0
    editorial_boost: float = 0.0
    feed_score: float = 0.0
    dedupe_priority: float = 0.0
    tags: List[str] = Field(default_factory=list)
    summary_tr: str
    general_meaning_tr: str
    what_it_can_feel_like_tr: str
    what_to_watch_tr: str
    how_to_work_with_it_tr: str
    who_feels_it_stronger_tr: Optional[str] = None
    personalization_cta_label_tr: str = "Benim haritamda nasıl etkiliyor?"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    debug: Dict[str, Any] = Field(default_factory=dict)


class SkyFeedItem(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    id: str
    slug: str
    event_type: str
    title_tr: str
    short_title_tr: str
    summary_tr: str
    badge_tr: str
    relative_timing_tr: str
    phase: str
    status: str
    starts_at: str
    exact_at: str
    ends_at: str
    visibility_window_start: str
    visibility_window_end: str
    importance_score: float = 0.0
    cultural_interest_score: float = 0.0
    feed_score: float = 0.0
    tags: List[str] = Field(default_factory=list)
    bodies: List[str] = Field(default_factory=list)
    aspect: Optional[str] = None
    sign: Optional[str] = None
    personalization_cta: Dict[str, Any] = Field(default_factory=dict)


class SkyFeedResponse(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    rail_type: str = "global_sky_events"
    generated_at: str
    now: str
    tz: str
    locale: str = "tr"
    summary_tr: str
    hero: Optional[SkyFeedItem] = None
    items: List[SkyFeedItem] = Field(default_factory=list)
    filters: Dict[str, Any] = Field(default_factory=dict)
    debug: Optional[Dict[str, Any]] = None


class SkyEventDetailResponse(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    rail_type: str = "global_sky_events"
    generated_at: str
    tz: str
    locale: str = "tr"
    event: GlobalSkyEvent
    related_events: List[SkyFeedItem] = Field(default_factory=list)
    personalization_cta: Dict[str, Any] = Field(default_factory=dict)
    debug: Optional[Dict[str, Any]] = None


class SkyArchiveResponse(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    rail_type: str = "global_sky_events"
    generated_at: str
    tz: str
    locale: str = "tr"
    range: Dict[str, str]
    items: List[SkyFeedItem] = Field(default_factory=list)
    total: int = 0
    debug: Optional[Dict[str, Any]] = None


class SkyEventPersonalizationRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    birth_date: str
    birth_time: str
    birth_place: str


class SkyPersonalTouchpoint(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    point: str
    point_type: str
    aspect: Optional[str] = None
    orb_deg: Optional[float] = None
    house: Optional[int] = None
    note_tr: str


class SkyEventPersonalizationResponse(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    rail_type: str = "global_sky_events"
    generated_at: str
    event_id: str
    event_slug: str
    impact_score: float
    relevance_level: str
    summary_tr: str
    activated_areas_tr: List[str] = Field(default_factory=list)
    matched_natal_points: List[SkyPersonalTouchpoint] = Field(default_factory=list)
    strongest_window_start: str
    strongest_window_end: str
    related_personal_transit_ids: List[str] = Field(default_factory=list)
    debug: Optional[Dict[str, Any]] = None
