"""Social like tracking placeholders."""
from __future__ import annotations

from typing import Dict


def toggle_like(post_id: str, user_id: str) -> Dict[str, bool]:
    """Pretend to toggle a like entry."""
    return {"post_id": post_id, "user_id": user_id, "liked": True}
