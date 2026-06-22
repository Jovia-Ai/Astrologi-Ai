"""R3A contract / audit-compatibility tests (task section G + H).

Proves the registry loads deterministically, preserves the audited baseline,
grants no semantic authority, imports nothing from runtime/public/mobile, and
serializes identically across two clean processes.
"""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys

import app.natal.editorial_profile as ep
from app.natal.editorial_profile import (
    load_registry,
    registry_summary,
    validate_registry,
)

_PKG_DIR = os.path.dirname(ep.__file__)
_BACKEND_ROOT = os.path.abspath(os.path.join(_PKG_DIR, "..", "..", ".."))
_REPO_ROOT = os.path.abspath(os.path.join(_BACKEND_ROOT, ".."))

# Audited baseline from FREE_PROFILE_R2 inventory.
_EXPECTED_CLASSIFICATION = {
    "FREE_MODULAR_READY": 11,
    "PREMIUM_SYNTHESIS_ONLY": 3,
    "SUPPORTING_COPY_ONLY": 7,
    "DUPLICATE_OR_SUPERSEDED": 1,
    "FREE_MODULAR_NEEDS_EDIT": 1,
    "MISSING_OWNER": 1,
    "UNSAFE_OR_UNSUPPORTED": 1,
}
_EXPECTED_MODES = {"single_card": 14, "multi_slide": 7, "long_read": 4}


def test_registry_loads_deterministically():
    a = load_registry()
    b = load_registry()
    assert [x.asset_id for x in a] == [x.asset_id for x in b]
    assert list(a) == sorted(a, key=lambda x: x.asset_id)
    assert len(a) == 25


def test_all_25_audited_families_exist():
    assets = load_registry()
    assert len(assets) == 25
    assert len({x.asset_id for x in assets}) == 25
    families = {x.source.symbol_or_family for x in assets}
    assert len(families) == 25  # one registry entry per audited family


def test_audited_classification_counts_match():
    assets = load_registry()
    counts: dict[str, int] = {}
    for x in assets:
        counts[x.classification] = counts.get(x.classification, 0) + 1
    assert counts == _EXPECTED_CLASSIFICATION


def test_audited_slide_mode_counts_match():
    assets = load_registry()
    modes: dict[str, int] = {}
    for x in assets:
        modes[x.presentation.mode] = modes.get(x.presentation.mode, 0) + 1
    assert modes == _EXPECTED_MODES


def test_summary_matches_audited_baseline():
    s = registry_summary()
    assert s.classified_asset_count == 25
    assert s.free_ready_asset_count == 11
    assert s.premium_only_asset_count == 3
    assert s.unknown_unowned_asset_count == 1
    assert s.launch_eligible_count == 11
    assert dict(s.slide_mode_distribution) == _EXPECTED_MODES


def test_all_source_paths_exist():
    for x in load_registry():
        assert os.path.exists(os.path.join(_REPO_ROOT, x.source.path)), x.source.path


def test_registry_validates_clean():
    res = validate_registry()
    assert res.ok, res.errors
    assert res.checked == 25


def test_free_ready_only_permitted_surfaces():
    free_ready = [x for x in load_registry() if x.classification == "FREE_MODULAR_READY"]
    assert len(free_ready) == 11
    for x in free_ready:
        assert x.allowed_tiers == ("free",)
        assert set(x.allowed_surfaces) <= {"identity", "first_felt"}
        assert "origin" in x.prohibited_surfaces
        assert not (set(x.allowed_surfaces) & set(x.prohibited_surfaces))
        assert x.launch_eligible is True


def test_premium_only_never_free_eligible():
    premium = [x for x in load_registry() if x.classification == "PREMIUM_SYNTHESIS_ONLY"]
    assert len(premium) == 3
    for x in premium:
        assert "free" not in x.allowed_tiers
        assert x.launch_eligible is False


def test_unknown_unowned_asset_stays_blocked():
    missing = [x for x in load_registry() if x.classification == "MISSING_OWNER"]
    assert len(missing) == 1
    asset = missing[0]
    assert asset.launch_eligible is False
    assert asset.is_primary_owner is False
    assert "free" not in asset.allowed_tiers
    assert asset.status == "unresolved"
    # the one unresolved family is the mobile poster copy
    assert asset.source.path == "mobile/lib/app/tabs/profile_page.dart"


def test_no_asset_receives_semantic_authority():
    for x in load_registry():
        assert x.authority.meaning_authority == "none", x.asset_id


def test_package_imports_nothing_from_runtime_public_or_mobile():
    forbidden = (
        "mobile",
        "public_builder",
        "profile_v8_payload_builder",
        "internal_typed_guidance_renderer",
        "shou_renderer",
        "supporting_threads_builder",
        "narrative",
    )
    for fname in (
        "__init__.py",
        "content_asset_contracts.py",
        "content_asset_registry.py",
        "content_asset_validator.py",
    ):
        path = os.path.join(_PKG_DIR, fname)
        tree = ast.parse(open(path, encoding="utf-8").read(), filename=path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                mods = [n.name for n in node.names]
            elif isinstance(node, ast.ImportFrom):
                mods = [node.module or ""]
            else:
                continue
            for mod in mods:
                for bad in forbidden:
                    assert bad not in mod, f"{fname} imports forbidden {mod!r}"
    # also assert no mobile module ended up loaded by importing the package
    assert not any(m.startswith("mobile") for m in sys.modules)


def test_serialization_stable_across_two_clean_processes():
    snippet = (
        "import json;"
        "from app.natal.editorial_profile import load_registry;"
        "print(json.dumps([(a.asset_id,a.classification,a.presentation.mode,"
        "a.authority.meaning_authority,a.launch_eligible) for a in load_registry()],"
        "ensure_ascii=False,sort_keys=True))"
    )
    env = dict(os.environ, PYTHONPATH=_BACKEND_ROOT)
    out1 = subprocess.run([sys.executable, "-c", snippet], capture_output=True, text=True, env=env)
    out2 = subprocess.run([sys.executable, "-c", snippet], capture_output=True, text=True, env=env)
    assert out1.returncode == 0, out1.stderr
    assert out2.returncode == 0, out2.stderr
    assert out1.stdout == out2.stdout
    assert len(json.loads(out1.stdout)) == 25


def test_registry_only_sanctioned_r4_runtime_importer():
    """The editorial_profile package may be imported by exactly one runtime file:
    the FREE-PROFILE-R4 default-off flag-gated attachment in public_builder.py.

    R3A established dormancy; R4 is the authorized scope that binds the package to
    the public payload behind ``FREE_EDITORIAL_PROFILE_ENABLED`` (default off).
    Any other runtime importer (and any mobile importer) is still forbidden.
    Uses AST import analysis (not a bare substring) so unrelated identifiers such
    as public_builder._editorial_profile_title do not count.
    """
    sanctioned = {"backend/app/natal/public_builder.py"}
    app_dir = os.path.join(_BACKEND_ROOT, "app")
    hits = []
    for root, _dirs, files in os.walk(app_dir):
        for f in files:
            if not f.endswith(".py"):
                continue
            p = os.path.join(root, f)
            if os.path.dirname(p) == _PKG_DIR:
                continue  # the package itself
            text = open(p, encoding="utf-8").read()
            try:
                tree = ast.parse(text, filename=p)
            except SyntaxError:
                # Pre-existing unparseable file in the base tree; fall back to a
                # conservative import-line check.
                if any(
                    "editorial_profile" in line and ("import" in line)
                    for line in text.splitlines()
                ):
                    hits.append(os.path.relpath(p, _REPO_ROOT))
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    mod = node.module or ""
                    if "editorial_profile" in mod.split("."):
                        hits.append(os.path.relpath(p, _REPO_ROOT))
                elif isinstance(node, ast.Import):
                    for n in node.names:
                        if "editorial_profile" in n.name.split("."):
                            hits.append(os.path.relpath(p, _REPO_ROOT))
    unsanctioned = sorted(set(hits) - sanctioned)
    assert unsanctioned == [], f"editorial_profile imported by unsanctioned files: {unsanctioned}"
    # the R4 binding must be present and flag-gated
    pb = open(os.path.join(_BACKEND_ROOT, "app", "natal", "public_builder.py"), encoding="utf-8").read()
    assert "FREE_EDITORIAL_PROFILE_ENABLED" in pb
