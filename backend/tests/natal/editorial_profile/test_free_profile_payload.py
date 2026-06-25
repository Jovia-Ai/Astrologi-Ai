"""R4A narrow Free editorial profile payload tests (task section L, backend 1–17)."""
from __future__ import annotations

import ast
import json
import os

import app.natal.editorial_profile as ep
from app.natal.editorial_profile.free_profile_plan_builder import build_free_placement_plan
from app.natal.editorial_profile.free_profile_payload_builder import (
    build_free_editorial_profile,
    build_free_editorial_profile_public,
)
from app.natal.editorial_profile import legacy_source_readers as readers

_PKG_DIR = os.path.dirname(ep.__file__)

_FA = [
    {"planet": "Sun", "sign": "Leo", "house": 4},
    {"planet": "Moon", "sign": "Gemini", "house": 1},
    {"planet": "Mercury", "sign": "Virgo", "house": 5},
    {"planet": "Venus", "sign": "Virgo", "house": 5},
    {"planet": "Mars", "sign": "Sagittarius", "house": 7},
]
_FB = [
    {"planet": "Sun", "sign": "Capricorn", "house": 1},
    {"planet": "Moon", "sign": "Leo", "house": 8},
    {"planet": "Mercury", "sign": "Capricorn", "house": 1},
    {"planet": "Venus", "sign": "Sagittarius", "house": 12},
    {"planet": "Mars", "sign": "Virgo", "house": 9},
]
_FA_KEYS = [
    "sun_leo", "sun_house_4", "moon_gemini", "moon_house_1", "mercury_virgo",
    "mercury_house_5", "venus_virgo", "venus_house_5", "mars_sagittarius", "mars_house_7",
]


def test_1_exact_ten_key_plan():
    plan = build_free_placement_plan(_FA)
    assert [c.primary_key for c in plan.cards] == _FA_KEYS
    assert len(plan.cards) == 10


def test_2_deterministic_order():
    plan = build_free_placement_plan(_FA)
    assert [c.ordinal for c in plan.cards] == list(range(10))
    planets_seq = [c.planet for c in plan.cards]
    assert planets_seq == ["sun", "sun", "moon", "moon", "mercury", "mercury",
                           "venus", "venus", "mars", "mars"]
    # sign first, house second within each planet
    for i in range(0, 10, 2):
        assert plan.cards[i].placement_type == "planet_sign"
        assert plan.cards[i + 1].placement_type == "planet_house"


def test_3_real_chart_facts_not_text_scanning():
    # Builder reads structured sign/house, ignores any free-text field.
    facts = [{"planet": "Sun", "sign": "Leo", "house": 4, "note": "mars in scorpio text"}]
    plan = build_free_placement_plan(facts)
    keys = [c.primary_key for c in plan.cards]
    assert keys == ["sun_leo", "sun_house_4"]  # no scorpio/mars from text


def test_4_exact_key_resolution():
    p = build_free_editorial_profile(_FA)
    for c in p.cards:
        planet, _, rest = c.primary_key.partition("_")
        assert c.asset_id == f"editorial.{planet}.{rest}.tr.v1"


def test_5_missing_key_omission():
    p = build_free_editorial_profile(_FB)
    assert [o.primary_key for o in p.diagnostics.missing_keys] == ["mars_house_9"]
    assert p.diagnostics.missing_keys[0].reason == "ASSET_NOT_FOUND"
    assert "mars_house_9" not in [c.primary_key for c in p.cards]


def test_6_no_fallback():
    for F in (_FA, _FB):
        p = build_free_editorial_profile(F)
        assert p.diagnostics.fallback_used is False
    # missing mars house not replaced by mars sign or another mars house
    p = build_free_editorial_profile(_FB)
    action_keys = [c.primary_key for c in p.cards if c.domain == "action"]
    assert action_keys == ["mars_virgo"]  # only the sign; no substitute house


def test_7_ownership_alignment():
    p = build_free_editorial_profile(_FA)
    for c in p.cards:
        assert c.ownership.meaning_owner == f"natal_placement:{c.primary_key}"
        assert c.ownership.expression_owner == c.asset_id
        assert c.ownership.presentation_owner == "free_editorial_profile_v1"
        assert c.ownership.status == "aligned"


def test_8_chip_ownership():
    for F in (_FA, _FB):
        p = build_free_editorial_profile(F)
        for c in p.cards:
            assert all(ch.source == c.primary_key for ch in c.chips)
            assert 1 <= len(c.chips) <= 2


def test_9_content_block_field_mapping():
    p = build_free_editorial_profile(_FA)
    house = next(c for c in p.cards if c.primary_key == "sun_house_4")
    mapping = {b.role: b.source_field for b in house.content_blocks}
    assert mapping["recognition"] == "trait"
    assert mapping["mechanism"] == "drive"
    assert mapping["tension"] == "shadow"
    assert mapping["capacity"] == "gift"


def test_10_no_background_hint_in_public_payload():
    p = build_free_editorial_profile(_FA)
    for c in p.cards:
        assert all(b.source_field != "background_hint" for b in c.content_blocks)
        assert all(b.role != "origin" for b in c.content_blocks)
    doc = p.to_public_dict()
    assert "background_hint" not in json.dumps(doc, ensure_ascii=False)


def _minimal_response(planets):
    return {"planets": planets}


def test_11_default_attaches_editorial_profile():
    from app.natal.public_builder import build_public_natal_view
    os.environ.pop("FREE_EDITORIAL_PROFILE_DISABLED", None)
    out = build_public_natal_view(_minimal_response(_FA))
    assert "editorial_profile" in out
    assert out["editorial_profile"]["version"] == "free_editorial_profile_v1"
    assert len(out["editorial_profile"]["cards"]) == 10


def test_12_emergency_disabled_payload_byte_parity():
    from app.natal.public_builder import build_public_natal_view
    os.environ["FREE_EDITORIAL_PROFILE_DISABLED"] = "1"
    a = build_public_natal_view(_minimal_response(_FA))
    b = build_public_natal_view(_minimal_response(_FA))
    try:
        assert json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True, default=str)
        assert "editorial_profile" not in a
    finally:
        os.environ.pop("FREE_EDITORIAL_PROFILE_DISABLED", None)


def test_13_payload_additive_compatibility():
    from app.natal.public_builder import build_public_natal_view
    os.environ["FREE_EDITORIAL_PROFILE_DISABLED"] = "1"
    baseline = build_public_natal_view(_minimal_response(_FA))
    os.environ.pop("FREE_EDITORIAL_PROFILE_DISABLED", None)
    try:
        attached = build_public_natal_view(_minimal_response(_FA))
    finally:
        os.environ.pop("FREE_EDITORIAL_PROFILE_DISABLED", None)
    assert "editorial_profile" in attached
    # every baseline key unchanged
    for k, v in baseline.items():
        assert json.dumps(attached[k], sort_keys=True, default=str) == json.dumps(v, sort_keys=True, default=str)
    assert attached["editorial_profile"]["version"] == "free_editorial_profile_v1"
    assert len(attached["editorial_profile"]["cards"]) == 10


def test_14_fixture_a():
    p = build_free_editorial_profile(_FA)
    assert len(p.cards) == 10
    assert [c.domain for c in p.cards] == [
        "identity", "identity", "emotion", "emotion", "mind", "mind",
        "relationship", "relationship", "action", "action",
    ]
    assert [c.primary_key for c in p.cards] == _FA_KEYS


def test_15_fixture_b():
    p = build_free_editorial_profile(_FB)
    assert len(p.cards) == 9
    assert [c.primary_key for c in p.cards] == [
        "sun_capricorn",
        "sun_house_1",
        "moon_leo",
        "moon_house_8",
        "mercury_capricorn",
        "mercury_house_1",
        "venus_sagittarius",
        "venus_house_12",
        "mars_virgo",
    ]
    assert [o.primary_key for o in p.diagnostics.missing_keys] == ["mars_house_9"]


def test_16_stable_serialization():
    a = build_free_editorial_profile(_FA).to_public_dict()
    b = build_free_editorial_profile(_FA).to_public_dict()
    assert json.dumps(a, ensure_ascii=False, sort_keys=True) == json.dumps(b, ensure_ascii=False, sort_keys=True)


def test_17_no_shou_or_premium_import():
    forbidden = ("master_selector", "contradiction", "promise_vector", "internal_typed_guidance_renderer",
                 "shou_renderer", "premium", "natal_promise", "tam_okuma")
    for fname in ("free_profile_plan_contracts.py", "free_profile_plan_builder.py",
                  "free_profile_payload_contracts.py", "free_profile_payload_builder.py"):
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
                    assert bad not in m.lower(), f"{fname} imports {m!r}"


def test_18_interpret_ui_cache_key_splits_emergency_disabled_variant(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "http://localhost:54321")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "test-anon-key")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
    from app.api.routes.natal_interpretation import (
        NatalInterpretationRequest,
        _free_editorial_profile_cache_variant,
        _interpret_ui_cache_key,
    )

    request = NatalInterpretationRequest(
        birth_date="1990-01-01",
        birth_time="12:00",
        birth_place="Istanbul",
        locale="tr",
    )
    monkeypatch.delenv("FREE_EDITORIAL_PROFILE_DISABLED", raising=False)
    enabled_variant = _free_editorial_profile_cache_variant()
    enabled_key = _interpret_ui_cache_key(
        request,
        debug=False,
        include_debug=False,
        include_full_profile=False,
        profile_engine=None,
    )
    monkeypatch.setenv("FREE_EDITORIAL_PROFILE_DISABLED", "1")
    disabled_variant = _free_editorial_profile_cache_variant()
    disabled_key = _interpret_ui_cache_key(
        request,
        debug=False,
        include_debug=False,
        include_full_profile=False,
        profile_engine=None,
    )
    assert enabled_variant == "free_editorial_profile_v1:enabled"
    assert disabled_variant == "free_editorial_profile_v1:disabled"
    assert enabled_key != disabled_key
