"""Environment loading helpers for the backend."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BASE_DIR.parent
_ENV_IS_LOADED = False


def load_environment(dotenv_path: Optional[Path] = None) -> None:
    """Load .env variables exactly once."""

    global _ENV_IS_LOADED  # noqa: PLW0603 - module level flag
    if _ENV_IS_LOADED:
        return

    if dotenv_path is None:
        dotenv_path = BASE_DIR / ".env"

    load_dotenv(dotenv_path)
    _ENV_IS_LOADED = True
