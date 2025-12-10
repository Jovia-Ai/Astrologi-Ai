"""Story persistence helpers."""
from __future__ import annotations

from typing import Any, Dict

from app.services.supabase import supabase


def save_story(user_id: str, story_type: str, content: Dict[str, Any]):
    response = (
        supabase.table("stories")
        .insert(
            {
                "user_id": user_id,
                "story_type": story_type,
                "content": content,
            }
        )
        .execute()
    )
    return response.data


def get_stories(user_id: str):
    response = (
        supabase.table("stories")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    return response.data
