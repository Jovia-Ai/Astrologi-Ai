"""Story studio generation placeholders."""
from __future__ import annotations

from typing import Dict, Mapping


def generate_story_prompt(chart_summary: Mapping[str, str]) -> Dict[str, str]:
    """Return a placeholder story prompt."""
    return {
        "title": "Kozmik Günlüğün",
        "body": f"Bu alan yakında {chart_summary.get('name', 'kullanıcı')} için hikayeler yazacak.",
    }
