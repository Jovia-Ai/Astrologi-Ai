"""Internal shadow modular card projection (R3C).

Dormant. Converts an explicit, externally ordered list of placement keys into
ownership-safe shadow card packets via the read-only legacy adapter. Performs no
meaning selection, no ranking, no suppression, no cohort/chart inspection, no
slide splitting, and no prose generation. Not attached to any public payload.
"""
from __future__ import annotations

from collections import Counter
from typing import Tuple

from .content_asset_contracts import EditorialContentAssetV1
from .content_asset_registry import get_asset, load_registry
from .legacy_asset_contracts import ResolvedEditorialAsset, ResolutionFailure
from .legacy_library_adapter import _key_governance, resolve_key_detailed
from .legacy_source_readers import REGISTRY_FAMILY_ALIASES, SOURCE_FAMILIES
from .shadow_card_contracts import (
    ALIAS_NOT_CANONICAL_OWNER,
    ASSET_NOT_FOUND,
    ASSET_NOT_LAUNCH_ELIGIBLE,
    BLOCK_PLAN,
    CONTENT_INCOMPLETE,
    OWNERSHIP_MISMATCH,
    PROJECTION_VERSION,
    SOURCE_HASH_MISMATCH,
    SURFACE_NOT_ALLOWED,
    UNKNOWN_OWNER,
    ShadowBlock,
    ShadowCardContent,
    ShadowCardDiagnostics,
    ShadowEditorialCard,
    ShadowEditorialPacket,
    ShadowOwnership,
    ShadowPresentationIntent,
    ShadowProjectionFailure,
    ShadowProjectionSummary,
    ShadowSource,
)

# adapter failure reason -> projection failure reason
_ADAPTER_FAILURE_MAP = {
    "ASSET_NOT_FOUND": ASSET_NOT_FOUND,
    "SOURCE_SYMBOL_NOT_FOUND": ASSET_NOT_FOUND,
    "TIER_NOT_ALLOWED": ASSET_NOT_LAUNCH_ELIGIBLE,
    "CLASSIFICATION_NOT_LAUNCH_ELIGIBLE": ASSET_NOT_LAUNCH_ELIGIBLE,
    "SURFACE_NOT_ALLOWED": SURFACE_NOT_ALLOWED,
    "CONTENT_INCOMPLETE": CONTENT_INCOMPLETE,
    "UNKNOWN_OWNER": UNKNOWN_OWNER,
    "SOURCE_HASH_MISMATCH": SOURCE_HASH_MISMATCH,
}

# Resolved-content attribute that backs each structural source_field.
_FIELD_ATTR = {
    "trait": "trait",
    "drive": "body",        # body is the verbatim `drive` field
    "shadow": "shadow",
    "gift": "gift",
    "background_hint": "background_hint",
}

_OPTIONAL_FIELDS = ("shadow", "gift", "background_hint")


def _is_alias_symbol(symbol: str) -> bool:
    return symbol in REGISTRY_FAMILY_ALIASES and symbol not in SOURCE_FAMILIES


def _canonical_owner_check(registry_asset_id: str) -> str | None:
    """Return ALIAS_NOT_CANONICAL_OWNER if the registry owner is an alias-only family."""
    asset = get_asset(registry_asset_id)
    if asset is None:
        return ASSET_NOT_FOUND
    if _is_alias_symbol(asset.source.symbol_or_family):
        return ALIAS_NOT_CANONICAL_OWNER
    return None


def _family_blocked_reason(asset: EditorialContentAssetV1) -> str:
    if asset.classification in {"MISSING_OWNER", "UNKNOWN"}:
        return UNKNOWN_OWNER
    return ASSET_NOT_LAUNCH_ELIGIBLE


def _build_card(
    resolved: ResolvedEditorialAsset, tier: str, surface: str
) -> ShadowEditorialCard | ShadowProjectionFailure:
    primary_key = resolved.primary_key

    # Ownership / alias guard: the governing registry asset must be the exact-match
    # canonical owner, never a _V1/_V2 audit alias.
    owner_problem = _canonical_owner_check(resolved.registry_asset_id)
    if owner_problem is not None:
        return ShadowProjectionFailure(reason=owner_problem, primary_key=primary_key,
                                       detail=resolved.registry_asset_id)
    registry_asset = get_asset(resolved.registry_asset_id)
    assert registry_asset is not None

    # required title + primary body material
    if not resolved.content.title or not resolved.content.summary or not resolved.content.body:
        return ShadowProjectionFailure(reason=CONTENT_INCOMPLETE, primary_key=primary_key)

    # Ownership alignment: the resolved owner must be the exact governance owner
    # for this key (title, summary and all blocks come from this one asset).
    governance_owner = _key_governance().get(primary_key)
    if governance_owner != resolved.registry_asset_id:
        return ShadowProjectionFailure(reason=OWNERSHIP_MISMATCH, primary_key=primary_key,
                                       detail=f"{governance_owner} != {resolved.registry_asset_id}")

    blocks: list[ShadowBlock] = []
    missing_fields: list[str] = []
    for block_id, role, source_field, visibility in BLOCK_PLAN:
        value = getattr(resolved.content, _FIELD_ATTR[source_field])
        if value is None or not str(value).strip():
            if source_field in _OPTIONAL_FIELDS:
                missing_fields.append(source_field)
            continue
        blocks.append(ShadowBlock(
            block_id=block_id, role=role, text=value,
            source_field=source_field, launch_visibility=visibility,
        ))

    card = ShadowEditorialCard(
        card_id=f"free.shadow.{primary_key}",
        projection_version=PROJECTION_VERSION,
        primary_key=primary_key,
        asset_id=resolved.asset_id,
        domain=registry_asset.domain,
        tier=tier,
        surface=surface,
        ownership=ShadowOwnership(
            meaning_owner="external_resolved_key",
            expression_owner=resolved.asset_id,
            presentation_owner="shadow_card_contract",
            selection_performed=False,
            ownership_status="aligned",
        ),
        source=ShadowSource(
            path=resolved.source.path,
            symbol_or_family=resolved.source.symbol_or_family,
            content_hash=resolved.source.content_hash,
        ),
        content=ShadowCardContent(
            title=resolved.content.title,
            summary=resolved.content.summary,
            blocks=tuple(blocks),
        ),
        presentation_intent=ShadowPresentationIntent(
            mode=resolved.presentation.mode,
            allowed_roles=resolved.presentation.allowed_roles,
            min_slides=1 if resolved.presentation.mode == "single_card" else 1,
            max_slides=1 if resolved.presentation.mode == "single_card" else 3,
            slides_generated=False,
        ),
        diagnostics=ShadowCardDiagnostics(
            fallback_used=False,
            alias_owner_used=False,
            missing_fields=tuple(missing_fields),
            warnings=(),
        ),
    )
    return card


def project_shadow_card(
    primary_key: str, *, tier: str, surface: str
) -> ShadowEditorialCard | ShadowProjectionFailure:
    resolved = resolve_key_detailed(primary_key, tier=tier, surface=surface)
    if isinstance(resolved, ResolvedEditorialAsset):
        return _build_card(resolved, tier, surface)

    # Not a governed placement key. If the key names a registry *family* primary_key
    # of a blocked asset, surface the blocked reason; otherwise map the adapter reason.
    family_matches = [a for a in load_registry() if a.primary_key == primary_key]
    blocked = [a for a in family_matches if a.classification != "FREE_MODULAR_READY"]
    if blocked:
        return ShadowProjectionFailure(
            reason=_family_blocked_reason(blocked[0]), primary_key=primary_key,
            detail=blocked[0].asset_id,
        )
    reason = _ADAPTER_FAILURE_MAP.get(resolved.reason, ASSET_NOT_FOUND)
    return ShadowProjectionFailure(reason=reason, primary_key=primary_key, detail=resolved.detail)


def project_shadow_cards(
    primary_keys: Tuple[str, ...], *, tier: str, surface: str
) -> ShadowEditorialPacket:
    seen: set[str] = set()
    duplicates: list[str] = []
    cards: list[ShadowEditorialCard] = []
    failures: list[ShadowProjectionFailure] = []
    for key in primary_keys:
        if key in seen:
            duplicates.append(key)
            continue
        seen.add(key)
        result = project_shadow_card(key, tier=tier, surface=surface)
        if isinstance(result, ShadowEditorialCard):
            cards.append(result)
        else:
            failures.append(result)
    return ShadowEditorialPacket(
        tier=tier,
        surface=surface,
        requested_keys=tuple(primary_keys),
        cards=tuple(cards),
        failures=tuple(failures),
        duplicate_keys=tuple(duplicates),
    )


def shadow_projection_summary(packet: ShadowEditorialPacket) -> ShadowProjectionSummary:
    cards = packet.cards
    def has(field: str) -> int:
        return sum(1 for c in cards for b in c.content.blocks if b.source_field == field)
    missing = Counter()
    for c in cards:
        for f in c.diagnostics.missing_fields:
            missing[f] += 1
    modes = Counter(c.presentation_intent.mode for c in cards)
    return ShadowProjectionSummary(
        requested=len(packet.requested_keys),
        projected=len(cards),
        failed=len(packet.failures),
        aligned=sum(1 for c in cards if c.ownership.ownership_status == "aligned"),
        alias_owner_count=sum(1 for c in cards if c.diagnostics.alias_owner_used),
        fallback_count=sum(1 for c in cards if c.diagnostics.fallback_used),
        with_trait=has("trait"),
        with_drive=has("drive"),
        with_shadow=has("shadow"),
        with_gift=has("gift"),
        with_background_hint=has("background_hint"),
        missing_optional_fields=tuple(sorted(missing.items())),
        mode_distribution=tuple(sorted(modes.items())),
        missing_coverage_keys=tuple(f.primary_key for f in packet.failures
                                    if f.reason == ASSET_NOT_FOUND),
    )


def free_ready_corpus_reps() -> Tuple[Tuple[str, str], ...]:
    """Deterministic (registry_asset_id, representative placement key) for each of
    the 11 FREE_MODULAR_READY registry assets.

    Alias assets (_V1/_V2) resolve through the reader alias map to the concrete
    library; their representative key is canonically governed by the exact-match
    house asset, so projection never yields an alias owner.
    """
    from .legacy_source_readers import (
        iter_entry_keys,
        reader_family_id_for_registry_symbol,
    )

    free_ready = sorted(
        (a for a in load_registry() if a.classification == "FREE_MODULAR_READY"),
        key=lambda a: a.asset_id,
    )
    reps: list[Tuple[str, str]] = []
    used_per_family: dict[str, int] = {}
    for asset in free_ready:
        family_id = reader_family_id_for_registry_symbol(asset.source.symbol_or_family)
        keys = sorted(iter_entry_keys(family_id))
        idx = used_per_family.get(family_id, 0)
        used_per_family[family_id] = idx + 1
        reps.append((asset.asset_id, keys[idx % len(keys)]))
    return tuple(reps)
