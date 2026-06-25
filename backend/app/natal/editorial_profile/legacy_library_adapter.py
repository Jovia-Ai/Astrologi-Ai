"""Read-only legacy editorial library adapter (R3B).

Resolves a registry-eligible placement key to its real legacy editorial content
under a strict exact-key rule. The legacy library never selects meaning; the
resolved placement/semantic key is the meaning owner, the editorial asset is the
expression owner, and ``selection_performed`` is always ``False``.

Dormant: no runtime/public/mobile consumer imports this module. No SHOU semantic
selection is imported. No legacy constant is mutated. No cross-family fallback.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Dict, Tuple

from .content_asset_contracts import EditorialContentAssetV1
from .content_asset_registry import get_asset, load_registry
from .legacy_asset_contracts import (
    ASSET_NOT_FOUND,
    CLASSIFICATION_NOT_LAUNCH_ELIGIBLE,
    CONTENT_INCOMPLETE,
    FreeReadyAssetStatus,
    LegacyAdapterSummary,
    ResolvedAuthority,
    ResolvedEditorialAsset,
    ResolvedPresentation,
    ResolvedSource,
    ResolutionFailure,
    SOURCE_HASH_MISMATCH,
    SOURCE_SYMBOL_NOT_FOUND,
    SURFACE_NOT_ALLOWED,
    TIER_NOT_ALLOWED,
    UNKNOWN_OWNER,
)
from .legacy_source_readers import (
    SOURCE_FAMILIES,
    content_is_complete,
    family_content_hash,
    iter_entry_keys,
    normalize_entry,
    read_raw_entry,
    reader_family_id_for_registry_symbol,
)

_BLOCKED_OWNER_CLASSES = frozenset({"MISSING_OWNER", "UNKNOWN"})


def _synth_asset_id(primary_key: str) -> str:
    planet, _, rest = primary_key.partition("_")
    return f"editorial.{planet}.{rest}.tr.v1"


def _parse_placement_asset_id(asset_id: str) -> str | None:
    if not (asset_id.startswith("editorial.") and asset_id.endswith(".tr.v1")):
        return None
    middle = asset_id[len("editorial."):-len(".tr.v1")]
    planet, sep, rest = middle.partition(".")
    if not sep or not rest:
        return None
    return f"{planet}_{rest}"


@lru_cache(maxsize=1)
def _key_governance() -> Dict[str, str]:
    """placement key -> governing FREE_MODULAR_READY registry asset_id.

    Single-valued: each reader family is owned by the registry asset whose
    source symbol exactly matches the reader family id (logical aliases such as
    _V1/_V2 are not canonical per-key owners). Priority/support/sign/tone key
    sets are disjoint, so no key maps to two assets.
    """
    governance: Dict[str, str] = {}
    for asset in load_registry():
        if asset.classification != "FREE_MODULAR_READY":
            continue
        family_id = asset.source.symbol_or_family
        if family_id not in SOURCE_FAMILIES:
            continue  # alias-only assets (_V1/_V2) are not canonical per-key owners
        for key in iter_entry_keys(family_id):
            # disjoint sets guarantee no overwrite; guard anyway (deterministic).
            governance.setdefault(key, asset.asset_id)
    return governance


def _check_eligibility(
    asset: EditorialContentAssetV1, tier: str, surface: str
) -> str | None:
    if asset.classification != "FREE_MODULAR_READY" or not asset.launch_eligible:
        if asset.classification in _BLOCKED_OWNER_CLASSES:
            return UNKNOWN_OWNER
        return CLASSIFICATION_NOT_LAUNCH_ELIGIBLE
    if tier not in asset.allowed_tiers:
        return TIER_NOT_ALLOWED
    if surface in asset.prohibited_surfaces or surface not in asset.allowed_surfaces:
        return SURFACE_NOT_ALLOWED
    return None


def _resolve(
    asset: EditorialContentAssetV1, primary_key: str, tier: str, surface: str
) -> ResolvedEditorialAsset | ResolutionFailure:
    reason = _check_eligibility(asset, tier, surface)
    if reason is not None:
        return ResolutionFailure(
            reason=reason, primary_key=primary_key, registry_asset_id=asset.asset_id,
            asset_id=_synth_asset_id(primary_key),
        )
    family_id = reader_family_id_for_registry_symbol(asset.source.symbol_or_family)
    if family_id is None or family_id not in SOURCE_FAMILIES:
        return ResolutionFailure(
            reason=SOURCE_SYMBOL_NOT_FOUND, primary_key=primary_key,
            registry_asset_id=asset.asset_id, detail=asset.source.symbol_or_family,
        )
    raw = read_raw_entry(family_id, primary_key)
    if raw is None:
        return ResolutionFailure(
            reason=ASSET_NOT_FOUND, primary_key=primary_key,
            registry_asset_id=asset.asset_id, detail=f"key not in {family_id}",
        )
    content = normalize_entry(raw)
    if not content_is_complete(content):
        return ResolutionFailure(
            reason=CONTENT_INCOMPLETE, primary_key=primary_key,
            registry_asset_id=asset.asset_id,
        )
    content_hash = family_content_hash(family_id)
    declared = asset.source.content_hash
    if declared is not None and declared != content_hash:
        return ResolutionFailure(
            reason=SOURCE_HASH_MISMATCH, primary_key=primary_key,
            registry_asset_id=asset.asset_id,
        )
    return ResolvedEditorialAsset(
        asset_id=_synth_asset_id(primary_key),
        registry_asset_id=asset.asset_id,
        primary_key=primary_key,
        content_kind=asset.content_kind,
        classification=asset.classification,
        tier=tier,
        surface=surface,
        source=ResolvedSource(
            path=asset.source.path,
            symbol_or_family=family_id,
            content_hash=content_hash,
        ),
        content=content,
        presentation=ResolvedPresentation(
            mode=asset.presentation.mode,
            allowed_roles=asset.presentation.allowed_roles,
        ),
        authority=ResolvedAuthority(
            meaning_owner="external_resolved_key",
            expression_owner="editorial_asset",
            selection_performed=False,
        ),
    )


# ── public read-only API ─────────────────────────────────────────────────────
def resolve_key_detailed(
    primary_key: str, *, tier: str, surface: str
) -> ResolvedEditorialAsset | ResolutionFailure:
    """Resolve one placement key; returns a typed failure on any miss."""
    asset_id = _key_governance().get(primary_key)
    if asset_id is None:
        return ResolutionFailure(reason=ASSET_NOT_FOUND, primary_key=primary_key)
    asset = get_asset(asset_id)
    if asset is None:
        return ResolutionFailure(reason=ASSET_NOT_FOUND, primary_key=primary_key)
    return _resolve(asset, primary_key, tier, surface)


def resolve_assets_for_key(
    primary_key: str, *, tier: str, surface: str
) -> Tuple[ResolvedEditorialAsset, ...]:
    result = resolve_key_detailed(primary_key, tier=tier, surface=surface)
    if isinstance(result, ResolvedEditorialAsset):
        return (result,)
    return ()


def resolve_asset(
    asset_id: str, *, tier: str, surface: str
) -> ResolvedEditorialAsset | ResolutionFailure:
    """Resolve a placement asset_id, or a registry family asset_id (representative)."""
    registry_asset = get_asset(asset_id)
    if registry_asset is not None:
        # family-level request: resolve a representative governed key.
        if registry_asset.classification != "FREE_MODULAR_READY":
            reason = (
                UNKNOWN_OWNER
                if registry_asset.classification in _BLOCKED_OWNER_CLASSES
                else CLASSIFICATION_NOT_LAUNCH_ELIGIBLE
            )
            return ResolutionFailure(
                reason=reason, registry_asset_id=asset_id, asset_id=asset_id,
            )
        family_id = reader_family_id_for_registry_symbol(
            registry_asset.source.symbol_or_family
        )
        if family_id is None or family_id not in SOURCE_FAMILIES:
            return ResolutionFailure(
                reason=SOURCE_SYMBOL_NOT_FOUND, registry_asset_id=asset_id,
                detail=registry_asset.source.symbol_or_family,
            )
        keys = iter_entry_keys(family_id)
        if not keys:
            return ResolutionFailure(reason=CONTENT_INCOMPLETE, registry_asset_id=asset_id)
        return _resolve(registry_asset, keys[0], tier, surface)

    primary_key = _parse_placement_asset_id(asset_id)
    if primary_key is None:
        return ResolutionFailure(reason=ASSET_NOT_FOUND, asset_id=asset_id)
    return resolve_key_detailed(primary_key, tier=tier, surface=surface)


def source_content_hash(asset_id: str) -> str:
    """Deterministic content hash for a placement or registry family asset_id."""
    registry_asset = get_asset(asset_id)
    if registry_asset is not None:
        family_id = reader_family_id_for_registry_symbol(
            registry_asset.source.symbol_or_family
        )
        if family_id is None or family_id not in SOURCE_FAMILIES:
            raise KeyError(f"no reader family for {asset_id}")
        return family_content_hash(family_id)
    primary_key = _parse_placement_asset_id(asset_id)
    if primary_key is None:
        raise KeyError(f"unknown asset_id {asset_id}")
    governing = _key_governance().get(primary_key)
    if governing is None:
        raise KeyError(f"ungoverned key {primary_key}")
    asset = get_asset(governing)
    assert asset is not None
    family_id = reader_family_id_for_registry_symbol(asset.source.symbol_or_family)
    return family_content_hash(family_id)


def adapter_summary() -> LegacyAdapterSummary:
    registry = load_registry()
    free_ready = [a for a in registry if a.classification == "FREE_MODULAR_READY"]
    statuses = []
    resolved_count = 0
    for asset in sorted(free_ready, key=lambda a: a.asset_id):
        family_id = reader_family_id_for_registry_symbol(asset.source.symbol_or_family)
        if family_id is None or family_id not in SOURCE_FAMILIES:
            statuses.append(FreeReadyAssetStatus(
                registry_asset_id=asset.asset_id,
                source_symbol=asset.source.symbol_or_family,
                governed_key_count=0, representative_key=None, resolved=False,
                note="source-incomplete: no reader family",
            ))
            continue
        keys = iter_entry_keys(family_id)
        rep = keys[0] if keys else None
        res = _resolve(asset, rep, "free", "identity") if rep else None
        ok = isinstance(res, ResolvedEditorialAsset)
        if ok:
            resolved_count += 1
        statuses.append(FreeReadyAssetStatus(
            registry_asset_id=asset.asset_id,
            source_symbol=family_id,
            governed_key_count=len(keys),
            representative_key=rep,
            resolved=ok,
            note="" if ok else f"source-incomplete: {getattr(res, 'reason', 'no key')}",
        ))
    blocked = tuple(sorted({
        a.classification for a in registry if a.classification != "FREE_MODULAR_READY"
    }))
    return LegacyAdapterSummary(
        supported_source_families=tuple(sorted(SOURCE_FAMILIES.keys())),
        governed_key_count=len(_key_governance()),
        free_ready_asset_count=len(free_ready),
        free_ready_resolved_count=resolved_count,
        free_ready_statuses=tuple(statuses),
        blocked_classifications_present=blocked,
    )
