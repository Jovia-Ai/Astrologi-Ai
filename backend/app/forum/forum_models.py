"""Pydantic models for the Forum feature."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

VALID_CATEGORIES = {"transit", "iliski", "kariyer", "golge", "genel"}


class ForumPostCreate(BaseModel):
    title: str = Field(..., max_length=120)
    body: str = Field(..., max_length=600)
    category: str = Field(..., description="One of: transit, iliski, kariyer, golge, genel")
    active_transit: Optional[str] = None


class ForumReplyCreate(BaseModel):
    body: str = Field(..., max_length=300)


class ForumPostResponse(BaseModel):
    id: str
    user_id: str
    user_display_name: str
    user_sun_sign: str
    user_rising_sign: str
    category: str
    title: str
    body: str
    active_transit: Optional[str] = None
    like_count: int = 0
    reply_count: int = 0
    created_at: datetime
    is_liked_by_me: bool = False


class ForumReplyResponse(BaseModel):
    id: str
    post_id: str
    user_id: str
    user_display_name: str
    user_sun_sign: str
    body: str
    like_count: int = 0
    created_at: datetime


class ForumPostDetailResponse(BaseModel):
    post: ForumPostResponse
    replies: List[ForumReplyResponse]


class ForumPostListResponse(BaseModel):
    posts: List[ForumPostResponse]
    total: int
    has_more: bool


class ActiveTransitResponse(BaseModel):
    label: str
    description: Optional[str] = None
