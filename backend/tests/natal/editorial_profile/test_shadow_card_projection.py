"""R3C internal shadow modular card projection tests (task section J, 1–20)."""
from __future__ import annotations

import ast
import dataclasses
import json
import os
import subprocess
import sys

import app.natal.editorial_profile as ep
from app.natal.editorial_profile import load_registry
from app.natal.editorial_profile import legacy_source_readers as readers
from app.natal.editorial_profile.legacy_library_adapter import resolve_key_detailed
from app.natal.editorial_profile.legacy_asset_contracts import ResolvedEditorialAsset
from app.natal.editorial_profile.shadow_card_contracts import (
    BLOCK_PLAN,
    ShadowEditorialCard,
    ShadowProjectionFailure,
)
from app.natal.editorial_profile.shadow_card_projection import (
    _build_card,
    _canonical_owner_check,
    free_ready_corpus_reps,
    project_shadow_card,
    project_shadow_cards,
    shadow_projection_summary,
)

_PKG_DIR = os.path.dirname(ep.__file__)
_BACKEND_ROOT = os.path.abspath(os.path.join(_PKG_DIR, "..", "..", ".."))

_FIXTURE_A = ("sun_house_4", "moon_gemini", "mercury_virgo", "venus_virgo", "mars_sagittarius")
_FIXTURE_B = (
    "sun_house_1", "sun_capricorn", "moon_leo", "moon_house_8", "mercury_capricorn",
    "mercury_house_1", "venus_sagittarius", "venus_house_12", "mars_virgo", "mars_house_9",
)
_ALIAS_ASSET_ID = "editorial.personality_imprint_library_tr_v1.tr.v1"  # _V1 alias


def _card(key, tier="free", surface="identity"):
    return project_shadow_card(key, tier=tier, surface=surface)


def test_1_one_exact_key_one_card():
    c = _card("sun_house_4")
    assert isinstance(c, ShadowEditorialCard)
    assert c.card_id == "free.shadow.sun_house_4"
    assert c.primary_key == "sun_house_4"
    assert c.asset_id == "editorial.sun.house_4.tr.v1"


def test_2_all_content_fields_from_one_asset():
    c = _card("moon_gemini")
    raw = readers.read_raw_entry("PERSONALITY_IMPRINT_LIBRARY_TR_V3.moon_signs", "moon_gemini")
    assert c.content.title == raw["label_tr"]
    assert c.content.summary == raw["aura"]
    by_field = {b.source_field: b.text for b in c.content.blocks}
    assert by_field["trait"] == raw["trait"]
    assert by_field["drive"] == raw["drive"]
    assert by_field["shadow"] == raw["shadow"]


def test_3_field_to_role_mapping_correct():
    c = _card("sun_house_4")
    expected = {bid: (role, field, vis) for bid, role, field, vis in BLOCK_PLAN}
    for b in c.content.blocks:
        role, field, vis = expected[b.block_id]
        assert b.role == role and b.source_field == field and b.launch_visibility == vis


def test_4_no_text_rewriting():
    c = _card("venus_virgo")
    raw = readers.read_raw_entry("PERSONALITY_IMPRINT_LIBRARY_TR_V3.venus_signs", "venus_virgo")
    for b in c.content.blocks:
        assert b.text == raw[{"drive": "drive", "trait": "trait", "shadow": "shadow",
                              "gift": "gift", "background_hint": "background_hint"}[b.source_field]]


def test_5_empty_optional_fields_omitted():
    # sign entries have no gift / background_hint -> those blocks absent
    c = _card("mars_sagittarius")
    fields = {b.source_field for b in c.content.blocks}
    assert "gift" not in fields and "background_hint" not in fields
    assert "gift" in c.diagnostics.missing_fields
    assert "background_hint" in c.diagnostics.missing_fields
    # no empty-text blocks ever
    assert all(b.text.strip() for b in c.content.blocks)


def test_6_input_order_preserved():
    p = project_shadow_cards(_FIXTURE_A, tier="free", surface="identity")
    assert [c.primary_key for c in p.cards] == list(_FIXTURE_A)


def test_7_duplicate_keys_deduplicated():
    p = project_shadow_cards(("sun_house_4", "sun_house_4", "moon_gemini", "moon_gemini"),
                             tier="free", surface="identity")
    assert [c.primary_key for c in p.cards] == ["sun_house_4", "moon_gemini"]


def test_8_duplicate_input_diagnostics_recorded():
    p = project_shadow_cards(("sun_house_4", "sun_house_4", "moon_gemini"),
                             tier="free", surface="identity")
    assert p.duplicate_keys == ("sun_house_4",)


def test_9_blocked_classifications_fail():
    for cls in ("SUPPORTING_COPY_ONLY", "FREE_MODULAR_NEEDS_EDIT",
                "DUPLICATE_OR_SUPERSEDED", "UNSAFE_OR_UNSUPPORTED"):
        key = next(a.primary_key for a in load_registry() if a.classification == cls)
        r = _card(key)
        assert isinstance(r, ShadowProjectionFailure)
        assert r.reason in {"ASSET_NOT_LAUNCH_ELIGIBLE", "ASSET_NOT_FOUND"}


def test_10_premium_never_projects_for_free():
    for a in load_registry():
        if a.classification == "PREMIUM_SYNTHESIS_ONLY":
            r = _card(a.primary_key)
            assert isinstance(r, ShadowProjectionFailure)
            assert r.reason == "ASSET_NOT_LAUNCH_ELIGIBLE"


def test_11_unknown_owner_fails():
    key = next(a.primary_key for a in load_registry() if a.classification == "MISSING_OWNER")
    r = _card(key)
    assert isinstance(r, ShadowProjectionFailure)
    assert r.reason == "UNKNOWN_OWNER"


def test_12_prohibited_surface_fails():
    r = _card("sun_house_4", surface="origin")
    assert isinstance(r, ShadowProjectionFailure)
    assert r.reason == "SURFACE_NOT_ALLOWED"


def test_13_aliases_cannot_become_canonical_owners():
    # direct guard
    assert _canonical_owner_check(_ALIAS_ASSET_ID) == "ALIAS_NOT_CANONICAL_OWNER"
    # crafted resolved pointing at the alias owner -> rejected
    base = resolve_key_detailed("sun_house_4", tier="free", surface="identity")
    assert isinstance(base, ResolvedEditorialAsset)
    crafted = dataclasses.replace(base, registry_asset_id=_ALIAS_ASSET_ID)
    res = _build_card(crafted, "free", "identity")
    assert isinstance(res, ShadowProjectionFailure)
    assert res.reason == "ALIAS_NOT_CANONICAL_OWNER"
    # no real projected card ever uses an alias source symbol
    p = project_shadow_cards(_FIXTURE_A + _FIXTURE_B, tier="free", surface="identity")
    for c in p.cards:
        assert c.source.symbol_or_family in readers.SOURCE_FAMILIES
        assert c.diagnostics.alias_owner_used is False


def test_13b_ownership_mismatch_guard():
    base = resolve_key_detailed("sun_house_4", tier="free", surface="identity")
    # point at a different *exact* owner than governance -> OWNERSHIP_MISMATCH
    other = next(a.asset_id for a in load_registry()
                 if a.classification == "FREE_MODULAR_READY"
                 and a.source.symbol_or_family == "PERSONALITY_IMPRINT_LIBRARY_TR_PRIORITY_HOUSES_V1")
    crafted = dataclasses.replace(base, registry_asset_id=other)
    res = _build_card(crafted, "free", "identity")
    assert isinstance(res, ShadowProjectionFailure)
    assert res.reason == "OWNERSHIP_MISMATCH"


def test_14_source_hashes_match_adapter():
    c = _card("sun_house_4")
    resolved = resolve_key_detailed("sun_house_4", tier="free", surface="identity")
    assert c.source.content_hash == resolved.source.content_hash
    assert len(c.source.content_hash) == 64


def test_15_repeated_projection_deterministic():
    assert _card("venus_virgo") == _card("venus_virgo")


def test_16_two_clean_processes_serialize_identically():
    snippet = (
        "import json,dataclasses;"
        "from app.natal.editorial_profile.shadow_card_projection import project_shadow_cards;"
        "keys=('sun_house_4','moon_gemini','mercury_virgo','venus_virgo','mars_sagittarius',"
        "'sun_house_1','sun_capricorn','moon_leo','moon_house_8','mercury_capricorn',"
        "'mercury_house_1','venus_sagittarius','venus_house_12','mars_virgo','mars_house_9');"
        "p=project_shadow_cards(keys,tier='free',surface='identity');"
        "out=[(c.card_id,c.asset_id,c.content.title,[ (b.block_id,b.text) for b in c.content.blocks]) for c in p.cards]"
        "+[('FAIL',f.primary_key,f.reason) for f in p.failures];"
        "print(json.dumps(out,ensure_ascii=False,sort_keys=True))"
    )
    env = dict(os.environ, PYTHONPATH=_BACKEND_ROOT)
    o1 = subprocess.run([sys.executable, "-c", snippet], capture_output=True, text=True, env=env)
    o2 = subprocess.run([sys.executable, "-c", snippet], capture_output=True, text=True, env=env)
    assert o1.returncode == 0, o1.stderr
    assert o1.stdout == o2.stdout


def test_17_fixture_a_result():
    p = project_shadow_cards(_FIXTURE_A, tier="free", surface="identity")
    assert len(p.cards) == 5 and len(p.failures) == 0
    assert all(c.ownership.ownership_status == "aligned" for c in p.cards)
    assert all(not c.diagnostics.fallback_used for c in p.cards)
    assert all(not c.diagnostics.alias_owner_used for c in p.cards)
    assert [c.primary_key for c in p.cards] == list(_FIXTURE_A)


def test_18_fixture_b_result():
    p = project_shadow_cards(_FIXTURE_B, tier="free", surface="identity")
    assert len(p.cards) == 9
    assert len(p.failures) == 1
    assert p.failures[0].primary_key == "mars_house_9"
    assert p.failures[0].reason == "ASSET_NOT_FOUND"
    s = shadow_projection_summary(p)
    assert s.missing_coverage_keys == ("mars_house_9",)


def test_19_all_11_free_ready_project_successfully():
    reps = free_ready_corpus_reps()
    assert len(reps) == 11
    aligned = 0
    alias_owners = 0
    fallback = 0
    for _aid, key in reps:
        c = project_shadow_card(key, tier="free", surface="identity")
        assert isinstance(c, ShadowEditorialCard), (_aid, key)
        if c.ownership.ownership_status == "aligned":
            aligned += 1
        alias_owners += int(c.diagnostics.alias_owner_used)
        fallback += int(c.diagnostics.fallback_used)
        assert c.source.symbol_or_family in readers.SOURCE_FAMILIES  # no alias owner
    assert aligned == 11 and alias_owners == 0 and fallback == 0


def test_20_no_runtime_public_mobile_importer():
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
                if any("shadow_card_projection" in ln and "import" in ln for ln in text.splitlines()):
                    hits.append(p)
                continue
            for node in ast.walk(tree):
                mods = []
                if isinstance(node, ast.ImportFrom):
                    mods = [node.module or ""]
                elif isinstance(node, ast.Import):
                    mods = [n.name for n in node.names]
                for m in mods:
                    if "shadow_card_projection" in m or "shadow_card_contracts" in m:
                        hits.append(p)
    assert hits == [], hits
    assert not any(m.startswith("mobile") for m in sys.modules)


def test_projection_does_not_import_shou_selection():
    forbidden = ("master_selector", "contradiction", "promise_vector", "natal_feature_graph",
                 "internal_typed_guidance_renderer", "shou_renderer", "public_builder", "mobile")
    for fname in ("shadow_card_contracts.py", "shadow_card_projection.py"):
        path = os.path.join(_PKG_DIR, fname)
        tree = ast.parse(open(path, encoding="utf-8").read(), filename=path)
        for node in ast.walk(tree):
            mods = []
            if isinstance(node, ast.ImportFrom):
                mods = [node.module or ""]
            elif isinstance(node, ast.Import):
                mods = [n.name for n in node.names]
            for m in mods:
                for bad in forbidden:
                    assert bad not in m, f"{fname} imports {m!r}"
