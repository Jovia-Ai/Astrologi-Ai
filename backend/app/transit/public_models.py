from __future__ import annotations

from typing import Any, Dict, List, Optional, Literal
from pydantic import Field

from pydantic import BaseModel, ConfigDict


class CalendarDayLite(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    date: str = Field(..., description="YYYY-MM-DD")
    display_date: str = Field(..., description="Localized date label")
    heat: int = Field(..., ge=0, le=100)
    rating: int = Field(0, ge=0, le=3)
    score: Optional[float] = None
    labels: List[str] = Field(
        default_factory=list,
        description="Public-facing, max 3 summary labels",
    )
    is_critical: bool = False
    critical_reason: List[str] = Field(
        default_factory=list,
        description="['event_peak', 'phase_shift']",
    )
    event_count: int = 0
    top_event_ids: List[str] = Field(
        default_factory=list,
        description="Max 5 event ids shown in calendar",
    )
    label_pack: Optional[Dict[str, Any]] = None
    active_theme_ids: Optional[List[str]] = None
    marker_ids: Optional[List[str]] = None
    top_marker_id: Optional[str] = None
    moon_phase: Optional[str] = None
    moon_sign: Optional[str] = None


class CalendarMarker(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    id: str = Field(..., description="Marker id")
    date: str = Field(..., description="YYYY-MM-DD")
    kind: Literal["phase", "aspect_peak"]
    event_id: str
    label: str
    severity: Literal["low", "medium", "high"]
    tier: Literal["main", "support"]
    is_critical: bool = False
    phase_kind: Optional[Literal["ingress", "retro", "station"]] = None

    domains: List[str] = Field(default_factory=list)
    intents: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    score_by_lens: Dict[str, float] = Field(default_factory=dict)
    score_by_intent: Dict[str, float] = Field(default_factory=dict)
    evidence: Dict[str, Any] = Field(default_factory=dict)
    flags: Dict[str, bool] = Field(default_factory=dict)
    bodies: List[str] = Field(default_factory=list)


class TransitCalendarPublic(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    range: Dict[str, str]
    year_summary: Dict[str, Any]
    days: List[CalendarDayLite]
    markers: List[CalendarMarker]
    items_map: Dict[str, List[str]]
