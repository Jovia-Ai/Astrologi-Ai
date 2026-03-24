from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProfileInsightAstroSource(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    primary: Literal["moon_sign"] = "moon_sign"
    value: str


class ProfileInsightContent(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str
    body: str
    share_text: str
    tone: Literal["hard_truth_softened"] = "hard_truth_softened"


class ProfileInsightMeta(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    visibility: Literal["profile"] = "profile"
    priority: int = 32
    expandable: bool = True
    version: str = "v1"


class ProfileInsightCard(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    module_id: str
    type: Literal["profile_insight_card"] = "profile_insight_card"
    headline: str
    subheadline: str
    moon_sign: str
    title: str
    body: str
    tone: Literal["hard_truth_softened"] = "hard_truth_softened"
    share_text: str
    priority: int = Field(default=32, ge=0)
    astro_source: ProfileInsightAstroSource
    content: ProfileInsightContent
    meta: ProfileInsightMeta
