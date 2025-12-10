"""Story schemas."""
from __future__ import annotations

from typing import Dict, Any

from pydantic import BaseModel


class StorySchema(BaseModel):
    user_id: str
    story_type: str
    content: Dict[str, Any]
