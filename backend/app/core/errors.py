"""Shared exception types for the backend."""
from __future__ import annotations


class ApiError(Exception):
    """Raised when an external API request fails."""


class AIError(Exception):
    """Raised when AI interpretation fails."""
