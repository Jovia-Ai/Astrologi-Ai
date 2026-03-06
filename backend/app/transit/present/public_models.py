from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict


class Block(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    type: str
    text: Optional[str] = None
    items: Optional[Any] = None
    phase: Optional[str] = None
    duration: Optional[str] = None


class PublicEvent(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    event_id: str
    tier: str
    severity_tag: str
    blocks: List[Block]
    cta: dict


class PublicPeriodSummary(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    main_theme: Optional[str] = None
    one_liner: Optional[str] = None


class PublicPeriodSpace(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    label: Optional[str] = None
    one_liner: Optional[str] = None


class PublicPeriod(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    core_story: Optional[str] = None
    summary: PublicPeriodSummary
    period_space: Optional[PublicPeriodSpace] = None


class PublicTransitResponse(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    locale: str = "tr"
    period: PublicPeriod
    events: Optional[List[PublicEvent]] = None
    period_core: Optional[dict] = None
    event_cards: Optional[List[dict]] = None
    timeline: Optional[dict] = None
