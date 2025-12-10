"""Astro settings schema definitions."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class AstroSettingsCreate(BaseModel):
    user_id: str = Field(..., min_length=1)
    house_system: str = "placidus"
    zodiac_type: str = "tropical"


class AstroSettingsUpdate(BaseModel):
    house_system: Optional[str] = None
    zodiac_type: Optional[str] = None

    class Config:
        extra = "forbid"
