"""Proof raw template + render path — voice spec v2.1 §11.4–11.9.

S1 Commit 1 invariants:
  - Thread-level raw proof: "Yönetici · Ev · İşaret" Title Case format
  - Title Case preserved (no .lower() — Turkish locale safety)
  - Eksik context → empty string (zero-diff fallback)
  - h-variants inherit base thread template
  - proof_line always empty in this commit (infrastructure only)
  - render_thread_tr returns 5 keys (title, one_liner, paragraph, proof_raw, proof_line)
"""

from __future__ import annotations

import pytest

from app.natal.narrative.phrase_lib_tr_natal import (
    _PROOF_RAW_REQUIRED_CTX,
    _PROOF_RAW_TEMPLATES,
    render_proof_raw,
    render_thread_tr,
)


# ---------------------------------------------------------------------------
# render_proof_raw — happy paths (4 core threads)
# ---------------------------------------------------------------------------

def test_identity_mechanics_full_context_renders():
    ctx = {"asc_ruler": "Satürn", "asc_ruler_house": 3, "asc_ruler_sign": "Oğlak"}
    assert render_proof_raw("identity_mechanics", ctx) == "Satürn · 3. ev · Oğlak"


def test_relationships_depth_full_context_renders():
    ctx = {"r7": "Venüs", "r7_house": 11, "r7_sign": "Balık"}
    assert render_proof_raw("relationships_depth", ctx) == "Venüs · 11. ev · Balık"


def test_career_visibility_full_context_renders():
    ctx = {"mc_ruler": "Merkür", "mc_ruler_house": 6, "mc_ruler_sign": "Başak"}
    assert render_proof_raw("career_visibility", ctx) == "Merkür · 6. ev · Başak"


def test_direction_learning_full_context_renders():
    ctx = {"mars_house": 9, "mars_sign": "Yay"}
    assert render_proof_raw("direction_learning", ctx) == "Mars · 9. ev · Yay"


# ---------------------------------------------------------------------------
# h-variant fallback (identity_mechanics:h11 → identity_mechanics template)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "variant",
    [
        "identity_mechanics:h11",
        "identity_mechanics:h3",
        "identity_mechanics:h12",
        "identity_mechanics:hX",
    ],
)
def test_h_variants_inherit_base_thread_template(variant):
    ctx = {"asc_ruler": "Satürn", "asc_ruler_house": 3, "asc_ruler_sign": "Oğlak"}
    assert render_proof_raw(variant, ctx) == "Satürn · 3. ev · Oğlak"


def test_relationships_h_variant_fallback():
    ctx = {"r7": "Venüs", "r7_house": 8, "r7_sign": "Akrep"}
    assert render_proof_raw("relationships_depth:h8", ctx) == "Venüs · 8. ev · Akrep"


# ---------------------------------------------------------------------------
# Title Case + Turkish locale safety
# ---------------------------------------------------------------------------

def test_turkish_characters_preserved():
    # İ / ı / ğ / ş / ö / ü — Turkish-specific glyphs survive render
    ctx = {"asc_ruler": "Jüpiter", "asc_ruler_house": 9, "asc_ruler_sign": "İkizler"}
    assert render_proof_raw("identity_mechanics", ctx) == "Jüpiter · 9. ev · İkizler"


def test_title_case_not_lowercased():
    # Voice spec §11.5 — no .lower() transform (Türkçe İ → i̇ bug avoidance)
    ctx = {"asc_ruler": "Satürn", "asc_ruler_house": 3, "asc_ruler_sign": "Oğlak"}
    rendered = render_proof_raw("identity_mechanics", ctx)
    assert rendered == rendered  # sanity
    assert "Satürn" in rendered, "capital Ü preserved"
    assert "Oğlak" in rendered, "capital O with ğ preserved"
    assert "satürn" not in rendered, "no lowercase transform"


# ---------------------------------------------------------------------------
# Missing context → empty string fallback
# ---------------------------------------------------------------------------

def test_missing_ruler_returns_empty():
    ctx = {"asc_ruler_house": 3, "asc_ruler_sign": "Oğlak"}
    assert render_proof_raw("identity_mechanics", ctx) == ""


def test_missing_house_returns_empty():
    ctx = {"asc_ruler": "Satürn", "asc_ruler_sign": "Oğlak"}
    assert render_proof_raw("identity_mechanics", ctx) == ""


def test_missing_sign_returns_empty():
    ctx = {"asc_ruler": "Satürn", "asc_ruler_house": 3}
    assert render_proof_raw("identity_mechanics", ctx) == ""


def test_empty_string_value_treated_as_missing():
    ctx = {"asc_ruler": "Satürn", "asc_ruler_house": 3, "asc_ruler_sign": "   "}
    assert render_proof_raw("identity_mechanics", ctx) == ""


def test_none_value_treated_as_missing():
    ctx = {"asc_ruler": "Satürn", "asc_ruler_house": 3, "asc_ruler_sign": None}
    assert render_proof_raw("identity_mechanics", ctx) == ""


def test_empty_ctx_returns_empty():
    assert render_proof_raw("identity_mechanics", {}) == ""


def test_unknown_thread_returns_empty():
    ctx = {"asc_ruler": "Satürn", "asc_ruler_house": 3, "asc_ruler_sign": "Oğlak"}
    assert render_proof_raw("nonexistent_thread", ctx) == ""


# ---------------------------------------------------------------------------
# Consistency invariants — template + required ctx alignment
# ---------------------------------------------------------------------------

def test_every_template_has_required_ctx():
    # Voice spec §11.7 — every core thread template MUST declare required ctx keys.
    for thread_id in _PROOF_RAW_TEMPLATES:
        assert thread_id in _PROOF_RAW_REQUIRED_CTX, (
            f"{thread_id} missing required ctx declaration"
        )


def test_every_required_ctx_has_template():
    for thread_id in _PROOF_RAW_REQUIRED_CTX:
        assert thread_id in _PROOF_RAW_TEMPLATES, (
            f"{thread_id} missing template mapping"
        )


def test_all_four_core_threads_covered():
    # Voice spec §11.7 — 4 core threads required
    expected = {
        "identity_mechanics",
        "relationships_depth",
        "career_visibility",
        "direction_learning",
    }
    assert set(_PROOF_RAW_TEMPLATES.keys()) == expected


# ---------------------------------------------------------------------------
# render_thread_tr — full return dict contract
# ---------------------------------------------------------------------------

def test_render_thread_returns_five_keys_on_hit():
    ctx = {
        "asc_sign": "Oğlak",
        "asc_ruler": "Satürn",
        "asc_ruler_house": 3,
        "asc_ruler_sign": "Oğlak",
        "loop_line": "",
        "micro": "",
    }
    result = render_thread_tr("identity_mechanics", ctx, seed="user-abc")
    assert set(result.keys()) == {"title", "one_liner", "paragraph", "proof_raw", "proof_line"}


def test_render_thread_returns_five_keys_on_miss():
    result = render_thread_tr("nonexistent_thread", {}, seed="x")
    assert set(result.keys()) == {"title", "one_liner", "paragraph", "proof_raw", "proof_line"}
    assert all(v == "" for v in result.values())


def test_proof_line_is_always_empty_in_this_commit():
    # S1 Commit 1 scope — proof_line infrastructure only, no content yet.
    ctx = {
        "asc_sign": "Oğlak",
        "asc_ruler": "Satürn",
        "asc_ruler_house": 3,
        "asc_ruler_sign": "Oğlak",
        "loop_line": "",
        "micro": "",
    }
    result = render_thread_tr("identity_mechanics", ctx, seed="seed")
    assert result["proof_line"] == ""


def test_proof_raw_renders_in_full_dict_call():
    ctx = {
        "asc_sign": "Oğlak",
        "asc_ruler": "Satürn",
        "asc_ruler_house": 3,
        "asc_ruler_sign": "Oğlak",
        "loop_line": "",
        "micro": "",
    }
    result = render_thread_tr("identity_mechanics", ctx, seed="seed")
    assert result["proof_raw"] == "Satürn · 3. ev · Oğlak"


def test_proof_raw_empty_when_chart_context_missing():
    # Legacy caller — no chart placements in ctx
    ctx = {"loop_line": "", "micro": ""}
    result = render_thread_tr("identity_mechanics", ctx, seed="seed")
    assert result["proof_raw"] == ""


def test_existing_fields_not_affected_by_proof_logic():
    # Zero-diff regression — title/one_liner/paragraph must render regardless of proof ctx.
    ctx_without_proof_data = {
        "asc_sign": "Oğlak",
        "asc_ruler": "Satürn",
        "asc_ruler_house": 3,
        "loop_line": "",
        "micro": "",
    }
    result = render_thread_tr("identity_mechanics", ctx_without_proof_data, seed="seed")
    assert result["title"], "title still renders"
    assert result["paragraph"], "paragraph still renders"
    assert result["proof_raw"] == "", "proof_raw empty when asc_ruler_sign missing"
