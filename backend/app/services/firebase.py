"""Firebase service placeholder."""
from __future__ import annotations

from typing import Any, Dict


class FirebaseClient:
    """Tiny placeholder client to satisfy the new structure."""

    def __init__(self, project_id: str | None = None) -> None:
        self.project_id = project_id

    def health(self) -> Dict[str, Any]:
        return {"connected": bool(self.project_id)}
