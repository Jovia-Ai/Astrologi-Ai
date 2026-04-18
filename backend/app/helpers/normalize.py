"""Shared normalization helpers for deterministic parsing."""
from __future__ import annotations


def normalize_token(value: str) -> str:
    if not isinstance(value, str):
        return ""
    normalized = value.strip().lower().replace("-", "_")
    return "_".join(normalized.split())


def normalize_planet_key(value: object | None) -> str:
    if not value:
        return ""
    return str(value).strip().lower().replace(" ", "_")


def normalize_node_alias(value: str) -> str:
    if not isinstance(value, str):
        return ""
    normalized = value.strip().lower()
    if normalized in {"north_node", "true_node", "mean_node", "node"}:
        return "node"
    if normalized in {"lilith", "black_moon_lilith"}:
        return "lilith"
    return normalized


def normalize_sign_key(value: str | None) -> str:
    if not value:
        return ""
    return str(value).strip().lower()


def normalize_aspect_type(value: str | None) -> str:
    if not value:
        return ""
    normalized = str(value).strip().lower()
    if normalized in {"conj", "conjunction"}:
        return "conjunction"
    if normalized in {"opp", "opposition"}:
        return "opposition"
    if normalized in {"square", "sqr"}:
        return "square"
    if normalized in {"trine", "tri"}:
        return "trine"
    if normalized in {"sextile", "sex"}:
        return "sextile"
    if normalized in {"quincunx", "inconjunct", "inconjunction"}:
        return "quincunx"
    if normalized in {"semisextile", "semi_sextile", "semi-sextile", "semisextil"}:
        return "semisextile"
    return normalized
