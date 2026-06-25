"""Immutable result contracts for the read-only legacy editorial adapter (R3B).

The adapter resolves a registry-eligible placement key to its real legacy
editorial content. The legacy library never selects meaning: meaning ownership
stays with the resolved placement/semantic key; this layer only reads and
normalizes already-reviewed expression.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

# Typed failure reasons (task section D).
ASSET_NOT_FOUND = "ASSET_NOT_FOUND"
SOURCE_SYMBOL_NOT_FOUND = "SOURCE_SYMBOL_NOT_FOUND"
TIER_NOT_ALLOWED = "TIER_NOT_ALLOWED"
SURFACE_NOT_ALLOWED = "SURFACE_NOT_ALLOWED"
CLASSIFICATION_NOT_LAUNCH_ELIGIBLE = "CLASSIFICATION_NOT_LAUNCH_ELIGIBLE"
CONTENT_INCOMPLETE = "CONTENT_INCOMPLETE"
UNKNOWN_OWNER = "UNKNOWN_OWNER"
SOURCE_HASH_MISMATCH = "SOURCE_HASH_MISMATCH"

FAILURE_REASONS: frozenset[str] = frozenset({
    ASSET_NOT_FOUND,
    SOURCE_SYMBOL_NOT_FOUND,
    TIER_NOT_ALLOWED,
    SURFACE_NOT_ALLOWED,
    CLASSIFICATION_NOT_LAUNCH_ELIGIBLE,
    CONTENT_INCOMPLETE,
    UNKNOWN_OWNER,
    SOURCE_HASH_MISMATCH,
})


@dataclass(frozen=True)
class ResolvedSource:
    path: str
    symbol_or_family: str
    content_hash: str


@dataclass(frozen=True)
class ResolvedContent:
    title: str
    summary: str
    body: str
    trait: str | None = None
    shadow: str | None = None
    gift: str | None = None
    background_hint: str | None = None


@dataclass(frozen=True)
class ResolvedAuthority:
    meaning_owner: str  # always "external_resolved_key"
    expression_owner: str  # "editorial_asset"
    selection_performed: bool  # always False


@dataclass(frozen=True)
class ResolvedPresentation:
    mode: str
    allowed_roles: Tuple[str, ...]


@dataclass(frozen=True)
class ResolvedEditorialAsset:
    asset_id: str
    registry_asset_id: str
    primary_key: str
    content_kind: str
    classification: str
    tier: str
    surface: str
    source: ResolvedSource
    content: ResolvedContent
    presentation: ResolvedPresentation
    authority: ResolvedAuthority


@dataclass(frozen=True)
class ResolutionFailure:
    reason: str
    primary_key: str | None = None
    asset_id: str | None = None
    registry_asset_id: str | None = None
    detail: str = ""

    def __post_init__(self) -> None:
        if self.reason not in FAILURE_REASONS:
            raise ValueError(f"unknown failure reason {self.reason!r}")


@dataclass(frozen=True)
class FreeReadyAssetStatus:
    registry_asset_id: str
    source_symbol: str
    governed_key_count: int
    representative_key: str | None
    resolved: bool
    note: str = ""


@dataclass(frozen=True)
class LegacyAdapterSummary:
    supported_source_families: Tuple[str, ...]
    governed_key_count: int
    free_ready_asset_count: int
    free_ready_resolved_count: int
    free_ready_statuses: Tuple[FreeReadyAssetStatus, ...]
    blocked_classifications_present: Tuple[str, ...]
