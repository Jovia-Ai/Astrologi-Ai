"""Supabase service placeholder."""
from __future__ import annotations

from typing import Any, Dict


class SupabaseClient:
    """Very small adapter placeholder."""

    def __init__(self, project_url: str | None = None, api_key: str | None = None) -> None:
        self.project_url = project_url
        self.api_key = api_key

    def health(self) -> Dict[str, Any]:
        return {"connected": bool(self.project_url and self.api_key)}
