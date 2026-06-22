"""Immutable contracts for the internal shadow modular card projection (R3C).

A shadow card is a dormant, ownership-safe projection of an already-resolved
placement key into structural role blocks. It performs no meaning selection, no
ranking, no slide splitting, and generates no new prose. Meaning ownership stays
with the externally resolved key; expression ownership stays with the editorial
asset; presentation ownership is the shadow card contract.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

PROJECTION_VERSION = "free_profile_shadow_card_v1"

# Typed failure reasons (task section E).
ASSET_NOT_FOUND = "ASSET_NOT_FOUND"
ASSET_NOT_LAUNCH_ELIGIBLE = "ASSET_NOT_LAUNCH_ELIGIBLE"
UNKNOWN_OWNER = "UNKNOWN_OWNER"
SURFACE_NOT_ALLOWED = "SURFACE_NOT_ALLOWED"
CONTENT_INCOMPLETE = "CONTENT_INCOMPLETE"
OWNERSHIP_MISMATCH = "OWNERSHIP_MISMATCH"
ALIAS_NOT_CANONICAL_OWNER = "ALIAS_NOT_CANONICAL_OWNER"
SOURCE_HASH_MISMATCH = "SOURCE_HASH_MISMATCH"

FAILURE_REASONS: frozenset[str] = frozenset({
    ASSET_NOT_FOUND,
    ASSET_NOT_LAUNCH_ELIGIBLE,
    UNKNOWN_OWNER,
    SURFACE_NOT_ALLOWED,
    CONTENT_INCOMPLETE,
    OWNERSHIP_MISMATCH,
    ALIAS_NOT_CANONICAL_OWNER,
    SOURCE_HASH_MISMATCH,
})

LAUNCH_VISIBILITIES: frozenset[str] = frozenset({"eligible", "optional", "internal_only"})

# Structural field -> role block map (verbatim text; never concatenated/rewritten).
# (block_id, role, source_field, launch_visibility)
BLOCK_PLAN: Tuple[Tuple[str, str, str, str], ...] = (
    ("recognition", "recognition", "trait", "eligible"),
    ("mechanism", "mechanism", "drive", "eligible"),
    ("tension", "tension", "shadow", "optional"),
    ("capacity", "capacity", "gift", "optional"),
    ("origin", "origin", "background_hint", "internal_only"),
)


@dataclass(frozen=True)
class ShadowBlock:
    block_id: str
    role: str
    text: str
    source_field: str
    launch_visibility: str


@dataclass(frozen=True)
class ShadowOwnership:
    meaning_owner: str
    expression_owner: str
    presentation_owner: str
    selection_performed: bool
    ownership_status: str  # "aligned"


@dataclass(frozen=True)
class ShadowSource:
    path: str
    symbol_or_family: str
    content_hash: str


@dataclass(frozen=True)
class ShadowCardContent:
    title: str
    summary: str
    blocks: Tuple[ShadowBlock, ...]


@dataclass(frozen=True)
class ShadowPresentationIntent:
    mode: str
    allowed_roles: Tuple[str, ...]
    min_slides: int
    max_slides: int
    slides_generated: bool = False


@dataclass(frozen=True)
class ShadowCardDiagnostics:
    fallback_used: bool
    alias_owner_used: bool
    missing_fields: Tuple[str, ...]
    warnings: Tuple[str, ...]


@dataclass(frozen=True)
class ShadowEditorialCard:
    card_id: str
    projection_version: str
    primary_key: str
    asset_id: str
    domain: str
    tier: str
    surface: str
    ownership: ShadowOwnership
    source: ShadowSource
    content: ShadowCardContent
    presentation_intent: ShadowPresentationIntent
    diagnostics: ShadowCardDiagnostics


@dataclass(frozen=True)
class ShadowProjectionFailure:
    reason: str
    primary_key: str
    detail: str = ""

    def __post_init__(self) -> None:
        if self.reason not in FAILURE_REASONS:
            raise ValueError(f"unknown projection failure reason {self.reason!r}")


@dataclass(frozen=True)
class ShadowEditorialPacket:
    tier: str
    surface: str
    requested_keys: Tuple[str, ...]
    cards: Tuple[ShadowEditorialCard, ...]
    failures: Tuple[ShadowProjectionFailure, ...]
    duplicate_keys: Tuple[str, ...]


@dataclass(frozen=True)
class ShadowProjectionSummary:
    requested: int
    projected: int
    failed: int
    aligned: int
    alias_owner_count: int
    fallback_count: int
    with_trait: int
    with_drive: int
    with_shadow: int
    with_gift: int
    with_background_hint: int
    missing_optional_fields: Tuple[Tuple[str, int], ...]
    mode_distribution: Tuple[Tuple[str, int], ...]
    missing_coverage_keys: Tuple[str, ...]
