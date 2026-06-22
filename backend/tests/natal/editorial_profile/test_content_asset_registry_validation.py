"""R3A validator invariant tests (task section E).

Each test takes a valid asset and mutates it to violate exactly one invariant,
then asserts the validator flags that invariant. The clean registry must pass.
"""
from __future__ import annotations

import dataclasses
import os

from app.natal.editorial_profile import load_registry, validate_registry
from app.natal.editorial_profile.content_asset_contracts import EditorialContentAssetV1
from app.natal.editorial_profile.content_asset_validator import validate_assets

_PKG_DIR = os.path.dirname(__import__("app.natal.editorial_profile", fromlist=["x"]).__file__)
_REPO_ROOT = os.path.abspath(os.path.join(_PKG_DIR, "..", "..", "..", ".."))


def _replace(asset: EditorialContentAssetV1, **kw) -> EditorialContentAssetV1:
    return dataclasses.replace(asset, **kw)


def _src(asset, **kw):
    return dataclasses.replace(asset, source=dataclasses.replace(asset.source, **kw))


def _auth(asset, **kw):
    return dataclasses.replace(asset, authority=dataclasses.replace(asset.authority, **kw))


def _pres(asset, **kw):
    return dataclasses.replace(asset, presentation=dataclasses.replace(asset.presentation, **kw))


def _free_ready() -> EditorialContentAssetV1:
    return next(a for a in load_registry() if a.classification == "FREE_MODULAR_READY")


def _premium() -> EditorialContentAssetV1:
    return next(a for a in load_registry() if a.classification == "PREMIUM_SYNTHESIS_ONLY")


def _missing() -> EditorialContentAssetV1:
    return next(a for a in load_registry() if a.classification == "MISSING_OWNER")


def _multi_free() -> EditorialContentAssetV1:
    return next(
        a for a in load_registry()
        if a.presentation.mode == "multi_slide" and "free" in a.allowed_tiers
    )


def _long_read() -> EditorialContentAssetV1:
    return next(a for a in load_registry() if a.presentation.mode == "long_read")


def _supporting() -> EditorialContentAssetV1:
    return next(a for a in load_registry() if a.classification == "SUPPORTING_COPY_ONLY")


def _errors(*assets) -> tuple[str, ...]:
    return validate_assets(assets, repo_root=_REPO_ROOT).errors


def _has(code: str, errors) -> bool:
    return any(e.startswith(code) or f" {code} " in e or e.split(" ")[0] == code for e in errors)


def test_clean_registry_validates():
    res = validate_registry()
    assert res.ok, res.errors


def test_inv1_duplicate_asset_id():
    a = _free_ready()
    dup = _replace(a, source=dataclasses.replace(a.source, symbol_or_family="OTHER"))
    assert any("INV1" in e for e in _errors(a, dup))


def test_inv2_duplicate_primary_ownership_same_version():
    a = _free_ready()
    twin = _replace(a, asset_id=a.asset_id + ".twin")  # same primary_key/tier/surface/version
    assert any("INV2" in e for e in _errors(a, twin))


def test_inv2_allows_distinct_versions():
    a = _free_ready()
    twin = _replace(a, asset_id=a.asset_id + ".twin", version="v99")
    assert not any("INV2" in e for e in _errors(a, twin))


def test_inv3_free_ready_without_primary_key():
    a = _replace(_free_ready(), primary_key="", is_primary_owner=False)
    assert any("INV3" in e for e in _errors(a))


def test_inv4_free_asset_with_meaning_authority():
    a = _auth(_free_ready(), meaning_authority="chart_placement")
    assert any("INV4" in e for e in _errors(a))


def test_inv5_premium_synthesis_free_eligible():
    a = _replace(_premium(), allowed_tiers=("free",))
    assert any("INV5" in e for e in _errors(a))


def test_inv6_missing_owner_launch_eligible():
    a = _replace(_missing(), launch_eligible=True)
    assert any("INV6" in e for e in _errors(a))


def test_inv7_single_card_multi_slide():
    a = _pres(_free_ready(), max_slides=2)
    assert any("INV7" in e for e in _errors(a))


def test_inv8_free_multi_slide_too_many():
    a = _pres(_multi_free(), max_slides=4)
    assert any("INV8" in e for e in _errors(a))


def test_inv9_long_read_launch_eligible():
    a = _replace(_long_read(), launch_eligible=True)
    assert any("INV9" in e for e in _errors(a))


def test_inv10_overlapping_surfaces():
    a = _replace(_free_ready(), allowed_surfaces=("identity",), prohibited_surfaces=("identity",))
    assert any("INV10" in e for e in _errors(a))


def test_inv11_source_path_missing():
    a = _src(_free_ready(), path="backend/app/natal/does_not_exist_xyz.py")
    assert any("INV11" in e for e in _errors(a))


def test_inv12_internal_preview_as_free_truth():
    a = _free_ready()
    a = _replace(a, content_kind="internal_preview")
    assert any("INV12" in e for e in _errors(a))


def test_inv13_mobile_fallback_as_canonical_meaning():
    a = _replace(_missing(), is_primary_owner=True)  # mobile/ path + primary owner
    assert any("INV13" in e for e in _errors(a))


def test_inv14_supporting_copy_as_primary_owner():
    a = _replace(_supporting(), is_primary_owner=True)
    assert any("INV14" in e for e in _errors(a))
