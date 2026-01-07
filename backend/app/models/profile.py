"""Profile schema definitions."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ProfileCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1)


class ProfileUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None

    model_config = ConfigDict(extra="forbid")
