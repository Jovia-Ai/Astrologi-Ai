"""Social feed placeholder services."""
from __future__ import annotations

from typing import List


def get_latest_posts(limit: int = 20) -> List[dict]:
    """Return canned feed data until the social module is implemented."""
    return [
        {"author": "Astrologi-AI", "text": "Topluluk güncellemeleri yakında burada olacak.", "likes": 108},
    ][:limit]
