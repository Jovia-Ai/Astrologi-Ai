"""Pydantic models for user payloads."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserProfile(BaseModel):
    firstName: str = Field(..., min_length=1)
    lastName: str = Field(..., min_length=1)
    email: EmailStr
    date: str
    time: Optional[str]
    city: str
    chart: Optional[dict]
    updated_at: datetime = Field(default_factory=datetime.utcnow)
