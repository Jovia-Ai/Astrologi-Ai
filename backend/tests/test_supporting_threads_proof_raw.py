"""Supporting threads builder — proof_raw consumer integration (S2 Commit 1).

Invariants:
  - 3 live core section builders (_mind_section, _relationship_section,
    _career_section) emit proof_raw in return dict.
  - build_supporting_threads passes proof_raw through to final thread list.
  - Empty/missing context → empty string (no render).
  - Existing fields (title, one_liner, paragraph, chips) untouched.
"""

from __future__ import annotations

from app.natal.supporting_threads_builder import (
    _career_section,
    _mind_section,
    _relationship_section,
    build_supporting_threads,
)


# ---------------------------------------------------------------------------
# Section-level proof_raw emit
# ---------------------------------------------------------------------------

def test_mind_section_emits_proof_raw():
    section = _mind_section(
        seed="seed-abc",
        asc_sign="Capricorn",
        asc_ruler="Saturn",
        asc_ruler_sign="Capricorn",
        asc_house=3,
        loop_signature="",
        profile=None,
        family="direct",
    )
    # _sign_label("Capricorn") → "Oğlak", _planet_label("Saturn") → "Satürn"
    assert section["proof_raw"] == "Satürn · 3. ev · Oğlak"
    assert section["legacy_id"] == "identity_mechanics"


def test_relationship_section_emits_proof_raw():
    section = _relationship_section(
        seed="seed-abc",
        dsc_sign="Taurus",
        r7="Venus",
        r7_sign="Pisces",
        r7_house=11,
        moon_house=4,
        profile=None,
        family="direct",
    )
    assert section["proof_raw"] == "Venüs · 11. ev · Balık"
    assert section["legacy_id"] == "relationships_depth"


def test_career_section_emits_proof_raw():
    section = _career_section(
        seed="seed-abc",
        mc_sign="Libra",
        mc_ruler="Mercury",
        mc_ruler_sign="Virgo",
        mc_house=6,
        profile=None,
        family="direct",
    )
    assert section["proof_raw"] == "Merkür · 6. ev · Başak"
    assert section["legacy_id"] == "career_visibility"


# ---------------------------------------------------------------------------
# build_supporting_threads passthrough
# ---------------------------------------------------------------------------

def test_build_supporting_threads_passes_proof_raw_through():
    # Build directly from synthetic section list — bypass chart engine plumbing.
    sections = [
        {
            "id": "mind_system",
            "legacy_id": "identity_mechanics",
            "title": "Zihin",
            "subtitle": "...",
            "body": "...",
            "micro": "...",
            "detail_blocks": [],
            "chips": ["Yükselen Oğlak", "Satürn 3. evde"],
            "proof_raw": "Satürn · 3. ev · Oğlak",
        },
    ]
    threads = build_supporting_threads(
        chart_data={},
        planets=[],
        natal_graph={},
        sections=sections,
    )
    assert len(threads) == 1
    assert threads[0]["proof_raw"] == "Satürn · 3. ev · Oğlak"
    assert threads[0]["id"] == "identity_mechanics"


def test_build_supporting_threads_empty_proof_raw_when_missing():
    sections = [
        {
            "id": "mind_system",
            "legacy_id": "identity_mechanics",
            "title": "...",
            "subtitle": "...",
            "body": "...",
            "micro": "...",
            "detail_blocks": [],
            "chips": [],
            # proof_raw intentionally absent — simulates legacy section payload
        },
    ]
    threads = build_supporting_threads(
        chart_data={},
        planets=[],
        natal_graph={},
        sections=sections,
    )
    assert threads[0]["proof_raw"] == ""


def test_build_supporting_threads_non_string_proof_raw_coerced():
    # Guardrail: non-string input coerced to empty-safe string (no None leak).
    sections = [
        {
            "id": "relationships",
            "legacy_id": "relationships_depth",
            "title": "...",
            "subtitle": "...",
            "body": "...",
            "micro": "...",
            "detail_blocks": [],
            "chips": [],
            "proof_raw": None,
        },
    ]
    threads = build_supporting_threads(
        chart_data={},
        planets=[],
        natal_graph={},
        sections=sections,
    )
    assert threads[0]["proof_raw"] == ""


# ---------------------------------------------------------------------------
# Zero-diff — existing chip payload untouched
# ---------------------------------------------------------------------------

def test_mind_section_chips_unchanged_by_proof_raw_addition():
    section = _mind_section(
        seed="seed-abc",
        asc_sign="Capricorn",
        asc_ruler="Saturn",
        asc_ruler_sign="Capricorn",
        asc_house=3,
        loop_signature="",
        profile=None,
        family="direct",
    )
    # Chips remain as structured rozet list (voice spec §11.4 — parallel form)
    assert isinstance(section["chips"], list)
    assert any("Yükselen" in chip for chip in section["chips"])
    assert any("Satürn" in chip for chip in section["chips"])


def test_section_retains_title_paragraph_body_keys():
    section = _mind_section(
        seed="seed-abc",
        asc_sign="Capricorn",
        asc_ruler="Saturn",
        asc_ruler_sign="Capricorn",
        asc_house=3,
        loop_signature="",
        profile=None,
        family="direct",
    )
    # Legacy field contract intact — proof_raw is additive only.
    assert "title" in section
    assert "body" in section
    assert "chips" in section
    assert "detail_blocks" in section
    assert "legacy_id" in section
