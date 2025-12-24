from __future__ import annotations

from typing import Sequence

CANONICAL_DOMAINS: Sequence[str] = (
    "identity",
    "psychology",
    "relationships",
    "mind",
    "career",
    "karma",
)

_DOMAIN_CANON_MAP: dict[str, str] = {
    "identity": "identity",
    "psychology": "psychology",
    "relationships": "relationships",
    "mind": "mind",
    "career": "career",
    "karma": "karma",
    "psyche": "psychology",
    "emotions": "psychology",
    "relationship": "relationships",
    "rel": "relationships",
    "relating": "relationships",
    "resources": "career",
    "inner_life": "psychology",
    "inner-life": "psychology",
    "public_life": "career",
    "public-life": "career",
    "mental": "mind",
    "intellect": "mind",
    "purpose": "karma",
    "evolution": "karma",
}

DOMAIN_CANON_MAP: dict[str, str] = {
    key.strip().lower(): value
    for key, value in {**_DOMAIN_CANON_MAP, **{domain: domain for domain in CANONICAL_DOMAINS}}.items()
    if key or value
}


def canon_domain(domain: str | None) -> str:
    """
    Normalize free-form domain labels to a canonical domain key.
    """
    raw = str(domain or "").strip().lower()
    if not raw:
        return ""
    return DOMAIN_CANON_MAP.get(raw, raw)


def canonical_domains() -> Sequence[str]:
    """Return the canonical ordering of domain keys."""
    return CANONICAL_DOMAINS
