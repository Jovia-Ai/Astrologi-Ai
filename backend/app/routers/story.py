"""Story endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from app.models.story import StorySchema
from app.services.stories import get_stories, save_story

router = APIRouter(prefix="/api", tags=["stories"])


@router.post("/story")
def create_story(payload: StorySchema):
    saved = save_story(payload.user_id, payload.story_type, payload.content)
    return {"saved": saved}


@router.get("/story/{user_id}")
def list_stories(user_id: str):
    return get_stories(user_id)
