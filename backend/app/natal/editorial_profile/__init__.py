"""Editorial content asset registry (R3A foundation).

Bounded, dormant package. Classifies reviewed editorial content assets without
granting them meaning authority and without changing runtime behavior. Not
attached to any runtime/public/mobile consumer in R3A.
"""
from .content_asset_contracts import (
    AssetAuthority,
    AssetPresentation,
    AssetSource,
    EditorialContentAssetV1,
    RegistrySummary,
    RegistryValidationResult,
)
from .content_asset_registry import (
    find_assets,
    get_asset,
    load_registry,
    registry_path,
    registry_summary,
    validate_registry,
)

__all__ = [
    "AssetAuthority",
    "AssetPresentation",
    "AssetSource",
    "EditorialContentAssetV1",
    "RegistrySummary",
    "RegistryValidationResult",
    "find_assets",
    "get_asset",
    "load_registry",
    "registry_path",
    "registry_summary",
    "validate_registry",
]
