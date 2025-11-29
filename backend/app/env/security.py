"""Security helpers for sanitising sensitive strings."""
from __future__ import annotations


def mask_secret(secret: str | None, *, visible: int = 4) -> str:
    """Return a masked version of a secret for logging."""
    if not secret:
        return ""
    secret = secret.strip()
    if len(secret) <= visible:
        return "*" * len(secret)
    return secret[:visible] + "*" * (len(secret) - visible)
