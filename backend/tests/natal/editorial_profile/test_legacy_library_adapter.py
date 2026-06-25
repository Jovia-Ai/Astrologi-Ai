"""R3B read-only legacy editorial adapter tests (task section H, 1–15)."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys

import app.natal.editorial_profile as ep
from app.natal.editorial_profile import load_registry, registry_summary
from app.natal.editorial_profile.legacy_asset_contracts import (
    ResolvedEditorialAsset,
    ResolutionFailure,
)
from app.natal.editorial_profile.legacy_library_adapter import (
    adapter_summary,
    resolve_asset,
    resolve_assets_for_key,
    resolve_key_detailed,
    source_content_hash,
)
from app.natal.editorial_profile import legacy_source_readers as readers

_PKG_DIR = os.path.dirname(ep.__file__)
_BACKEND_ROOT = os.path.abspath(os.path.join(_PKG_DIR, "..", "..", ".."))

_FIXTURE_A = ["sun_house_4", "moon_gemini", "mercury_virgo", "venus_virgo", "mars_sagittarius"]
_FIXTURE_B = [
    "sun_house_1", "sun_capricorn", "moon_leo", "moon_house_8", "mercury_capricorn",
    "mercury_house_1", "venus_sagittarius", "venus_house_12", "mars_virgo", "mars_house_9",
]


def _free_ready_family_ids():
    return [a.asset_id for a in load_registry() if a.classification == "FREE_MODULAR_READY"]


def test_1_exact_key_resolves_only_matching_asset():
    r = resolve_key_detailed("sun_house_4", tier="free", surface="identity")
    assert isinstance(r, ResolvedEditorialAsset)
    assert r.primary_key == "sun_house_4"
    assert r.asset_id == "editorial.sun.house_4.tr.v1"
    tup = resolve_assets_for_key("sun_house_4", tier="free", surface="identity")
    assert len(tup) == 1 and tup[0].primary_key == "sun_house_4"


def test_2_title_and_body_remain_from_one_asset():
    r = resolve_key_detailed("moon_gemini", tier="free", surface="identity")
    assert isinstance(r, ResolvedEditorialAsset)
    raw = readers.read_raw_entry("PERSONALITY_IMPRINT_LIBRARY_TR_V3.moon_signs", "moon_gemini")
    assert r.content.title == raw["label_tr"]
    assert r.content.summary == raw["aura"]
    assert r.content.body == raw["drive"]
    assert r.content.trait == raw["trait"]
    # no other key's text bled in
    other = readers.read_raw_entry("PERSONALITY_IMPRINT_LIBRARY_TR_V3.moon_signs", "moon_leo")
    assert r.content.body != other["drive"]


def test_3_legacy_constants_not_mutated():
    def snapshot():
        return {fid: readers.family_content_hash(fid) for fid in readers.SOURCE_FAMILIES}
    before = snapshot()
    for k in _FIXTURE_A + _FIXTURE_B:
        resolve_key_detailed(k, tier="free", surface="identity")
    for fid in _free_ready_family_ids():
        resolve_asset(fid, tier="free", surface="identity")
    assert snapshot() == before


def test_4_blocked_classifications_fail_predictably():
    by_cls = {}
    for a in load_registry():
        by_cls.setdefault(a.classification, a.asset_id)
    for cls in ("PREMIUM_SYNTHESIS_ONLY", "SUPPORTING_COPY_ONLY",
                "FREE_MODULAR_NEEDS_EDIT", "DUPLICATE_OR_SUPERSEDED", "UNSAFE_OR_UNSUPPORTED"):
        r = resolve_asset(by_cls[cls], tier="free", surface="identity")
        assert isinstance(r, ResolutionFailure)
        assert r.reason == "CLASSIFICATION_NOT_LAUNCH_ELIGIBLE", (cls, r.reason)


def test_5_unknown_unowned_fails():
    mo = next(a.asset_id for a in load_registry() if a.classification == "MISSING_OWNER")
    r = resolve_asset(mo, tier="free", surface="identity")
    assert isinstance(r, ResolutionFailure)
    assert r.reason == "UNKNOWN_OWNER"


def test_6_prohibited_surface_fails():
    r = resolve_key_detailed("sun_house_4", tier="free", surface="origin")
    assert isinstance(r, ResolutionFailure)
    assert r.reason == "SURFACE_NOT_ALLOWED"


def test_6b_disallowed_tier_fails():
    r = resolve_key_detailed("sun_house_4", tier="premium", surface="identity")
    assert isinstance(r, ResolutionFailure)
    assert r.reason == "TIER_NOT_ALLOWED"


def test_7_premium_never_resolves_for_free():
    for a in load_registry():
        if a.classification == "PREMIUM_SYNTHESIS_ONLY":
            r = resolve_asset(a.asset_id, tier="free", surface="identity")
            assert isinstance(r, ResolutionFailure)
            assert r.reason in {"CLASSIFICATION_NOT_LAUNCH_ELIGIBLE", "TIER_NOT_ALLOWED"}
    # no placement key is governed by a premium asset
    from app.natal.editorial_profile.legacy_library_adapter import _key_governance
    premium_ids = {a.asset_id for a in load_registry() if a.classification == "PREMIUM_SYNTHESIS_ONLY"}
    assert not (set(_key_governance().values()) & premium_ids)


def test_8_missing_content_never_cross_falls_back():
    r = resolve_key_detailed("mars_house_9", tier="free", surface="identity")
    assert isinstance(r, ResolutionFailure)
    assert r.reason == "ASSET_NOT_FOUND"
    assert resolve_assets_for_key("mars_house_9", tier="free", surface="identity") == ()


def test_9_source_hashes_deterministic():
    aid = "editorial.sun.house_4.tr.v1"
    h1 = source_content_hash(aid)
    h2 = source_content_hash(aid)
    assert h1 == h2 and len(h1) == 64
    # equals the governing family hash (sun_house_4 lives in the support-house bank)
    assert h1 == readers.family_content_hash("PERSONALITY_IMPRINT_LIBRARY_TR_SUPPORT_HOUSES_V1")


def test_10_repeated_resolution_deterministic():
    a = resolve_key_detailed("venus_virgo", tier="free", surface="identity")
    b = resolve_key_detailed("venus_virgo", tier="free", surface="identity")
    assert a == b


def test_11_two_clean_processes_serialize_identically():
    snippet = (
        "import json;"
        "from app.natal.editorial_profile.legacy_library_adapter import resolve_key_detailed;"
        "from app.natal.editorial_profile.legacy_asset_contracts import ResolvedEditorialAsset;"
        "keys=['sun_house_4','moon_gemini','mercury_virgo','venus_virgo','mars_sagittarius',"
        "'sun_house_1','sun_capricorn','moon_leo','moon_house_8','mercury_capricorn',"
        "'mercury_house_1','venus_sagittarius','venus_house_12','mars_virgo','mars_house_9'];"
        "out=[];\n"
        "import dataclasses;\n"
        "for k in keys:\n"
        " r=resolve_key_detailed(k,tier='free',surface='identity');\n"
        " out.append((k, r.content.body if isinstance(r,ResolvedEditorialAsset) else r.reason, r.source.content_hash if isinstance(r,ResolvedEditorialAsset) else None));\n"
        "print(json.dumps(out,ensure_ascii=False,sort_keys=True))"
    )
    env = dict(os.environ, PYTHONPATH=_BACKEND_ROOT)
    o1 = subprocess.run([sys.executable, "-c", snippet], capture_output=True, text=True, env=env)
    o2 = subprocess.run([sys.executable, "-c", snippet], capture_output=True, text=True, env=env)
    assert o1.returncode == 0, o1.stderr
    assert o2.returncode == 0, o2.stderr
    assert o1.stdout == o2.stdout
    assert len(json.loads(o1.stdout)) == 15


def _adapter_module_files():
    return [
        os.path.join(_PKG_DIR, f)
        for f in (
            "legacy_asset_contracts.py",
            "legacy_library_adapter.py",
            "legacy_source_readers.py",
        )
    ]


def test_12_no_public_or_mobile_imports_the_adapter():
    app_dir = os.path.join(_BACKEND_ROOT, "app")
    hits = []
    for root, _d, files in os.walk(app_dir):
        for f in files:
            if not f.endswith(".py") or os.path.join(root, f).startswith(_PKG_DIR):
                continue
            p = os.path.join(root, f)
            text = open(p, encoding="utf-8").read()
            try:
                tree = ast.parse(text, filename=p)
            except SyntaxError:
                if any("legacy_library_adapter" in ln and "import" in ln for ln in text.splitlines()):
                    hits.append(p)
                continue
            for node in ast.walk(tree):
                mods = []
                if isinstance(node, ast.ImportFrom):
                    mods = [node.module or ""]
                elif isinstance(node, ast.Import):
                    mods = [n.name for n in node.names]
                for m in mods:
                    if "legacy_library_adapter" in m or "legacy_source_readers" in m:
                        hits.append(p)
    assert hits == [], hits
    assert not any(m.startswith("mobile") for m in sys.modules)


def test_13_adapter_does_not_import_shou_semantic_selection():
    forbidden = (
        "master_selector", "contradiction", "promise_vector", "natal_feature_graph",
        "natal_graph", "internal_typed_guidance_renderer", "shou_renderer",
        "public_builder", "mobile",
    )
    for path in _adapter_module_files():
        tree = ast.parse(open(path, encoding="utf-8").read(), filename=path)
        for node in ast.walk(tree):
            mods = []
            if isinstance(node, ast.ImportFrom):
                mods = [node.module or ""]
            elif isinstance(node, ast.Import):
                mods = [n.name for n in node.names]
            for m in mods:
                for bad in forbidden:
                    assert bad not in m, f"{os.path.basename(path)} imports {m!r}"


def test_14_registry_totals_unchanged():
    s = registry_summary()
    assert s.classified_asset_count == 25
    assert s.free_ready_asset_count == 11
    assert s.premium_only_asset_count == 3
    assert s.unknown_unowned_asset_count == 1


def test_15_all_free_ready_resolved_or_source_incomplete():
    s = adapter_summary()
    assert s.free_ready_asset_count == 11
    accounted = sum(
        1 for st in s.free_ready_statuses
        if st.resolved or "source-incomplete" in st.note
    )
    assert accounted == 11
    # in this tree all 11 are resolvable
    assert s.free_ready_resolved_count == 11


def test_fixture_a_and_b_matrix_is_stable():
    resolved_a = [resolve_key_detailed(k, tier="free", surface="identity") for k in _FIXTURE_A]
    assert all(isinstance(r, ResolvedEditorialAsset) for r in resolved_a)
    resolved_b = [resolve_key_detailed(k, tier="free", surface="identity") for k in _FIXTURE_B]
    ok_b = [r for r in resolved_b if isinstance(r, ResolvedEditorialAsset)]
    fail_b = [r for r in resolved_b if isinstance(r, ResolutionFailure)]
    assert len(ok_b) == 9
    assert len(fail_b) == 1 and fail_b[0].primary_key == "mars_house_9"
