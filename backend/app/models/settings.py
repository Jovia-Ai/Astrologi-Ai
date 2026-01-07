"""Astro settings schema definitions."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AstroSettingsCreate(BaseModel):
    user_id: str = Field(..., min_length=1)
    house_system: str = "placidus"
    zodiac_type: str = "tropical"


class AstroSettingsUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    house_system: Optional[str] = None
    zodiac_type: Optional[str] = None
