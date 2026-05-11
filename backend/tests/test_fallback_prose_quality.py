"""Regression tests for the non-LifeChapter fallback prose patch.

Two angles:

1. Turkish diacritics: any prose flowing through ``tr_normalize`` must not
   carry the bare-ASCII variants of Turkish words used by ``where.py`` and
   the ``upper_meaning`` content packs (durus, tarafina, tasabilir,
   netlestirme, cabasini, yumusatip).

2. Non-LifeChapter ``guided_fallback`` opening must center on the natal-side
   primary domain (e.g. h4 inner safety / h1 identity) and must drop the
   generic scaffold sentences listed in
   ``_FALLBACK_SCAFFOLD_PHRASES``.
"""
from __future__ import annotations

from typing import Sequence

from app.transit.narrative.astrolog_narrative_engine import (
    _FALLBACK_SCAFFOLD_PHRASES,
    _build_period_reading_v1,
    _semantic_enriched_fallback_plan,
    _strip_fallback_scaffold_sentences,
)
from app.transit.narrative.period_semantic_focus import PeriodSemanticFocusResult
from app.transit.narrative.text_quality_tr import tr_normalize


_FORBIDDEN_ASCII_TR = (
    "durus",
    "tarafina",
    "tasabilir",
    "netlestirme",
    "cabasini",
    "yumusatip",
)


def _assert_no_forbidden_ascii(text: str) -> None:
    lowered = text.lower()
    for token in _FORBIDDEN_ASCII_TR:
        assert token not in lowered, f"forbidden ASCII Turkish leaked: {token!r} in {text!r}"


# ---------------------------------------------------------------------------
# 1. tr_normalize must catch the canonical broken Turkish forms
# ---------------------------------------------------------------------------
def test_tr_normalize_fixes_where_house_label_phrases() -> None:
    raw = (
        "Bunu en cok kimlik ve durus alaninda hissedebilirsin; "
        "etkisi zihin ve iletisim tarafina da tasabilir."
    )
    out = tr_normalize(raw)
    _assert_no_forbidden_ascii(out)
    assert "duruş" in out
    assert "tarafına" in out
    assert "taşabilir" in out


def test_tr_normalize_fixes_upper_meaning_neptune_square_line() -> None:
    raw = (
        "Bu etki, her seyi netlestirme cabasini yumusatip belirsizligi "
        "daha sakin tasimana alan acabilir."
    )
    out = tr_normalize(raw)
    _assert_no_forbidden_ascii(out)
    assert "netleştirme" in out
    assert "çabasını" in out
    assert "yumuşatıp" in out


# ---------------------------------------------------------------------------
# 2. Scaffold-strip helper drops the listed forbidden seeds
# ---------------------------------------------------------------------------
def test_strip_fallback_scaffold_sentences_removes_known_phrases() -> None:
    text = (
        "Burada daha yavaş ama daha kalıcı bir çizgi oluşuyor. "
        "Bu dönem hayatının bir alanı daha görünür hale geliyor. "
        "Asıl konu netlik. "
        "İlk bakışta görünen şey tek mesele değil. "
        "Sende zaten çalışan birkaç ayrı taraf var."
    )
    cleaned = _strip_fallback_scaffold_sentences(text)
    for phrase in _FALLBACK_SCAFFOLD_PHRASES:
        assert phrase.lower() not in cleaned.lower()
    assert "Asıl konu netlik" in cleaned


# ---------------------------------------------------------------------------
# 3. End-to-end: non-LifeChapter fallback for a 2026-04-22-style scene
# ---------------------------------------------------------------------------
def _featured_event_neptune_square_sun_h1() -> dict:
    return {
        "event_id": "neptune_square_sun_h1",
        "transit_body": "Neptune",
        "natal_point": "Sun",
        "aspect": "square",
        "houses": {"transit_in_natal_house": 3, "natal_point_house": 1},
        "interpretation": {
            "headline": "Kimlikte basınç",
            "summary": "Duruşun ve yönün test edilebilir.",
            "where": (
                "Bunu en cok kimlik ve durus alaninda hissedebilirsin; "
                "etkisi zihin ve iletisim tarafina da tasabilir."
            ),
        },
    }


def _semantic_focus_h3_scene_with_h4_secondary() -> PeriodSemanticFocusResult:
    return PeriodSemanticFocusResult(
        selected_meaning="reorientation",
        meaning_family="reorientation",
        primary_domain="yakın çevrendeki ses",
        secondary_domains=["yakın çevrendeki ses", "house_3", "house_2", "house_4", "house_5"],
        confidence=0.7,
        source="period_voice_policy",
        scene_translation_request={
            "version": "manifestation_context_v1",
            "primary_house": 3,
            "house_axis": "3-1",
            "target_planet": "Sun",
            "target_planet_house": 1,
            "angle": "ASC",
            "life_scene": "yakın çevrendeki ses",
            "life_scene_variants": [
                "gündelik konuşmalar",
                "küçük cümlelerin ağırlığı",
                "yakın çevrendeki ses",
            ],
            "context_seed": "Bu tema daha çok yakın çevrendeki ses içinden görünür oluyor.",
            "variant_index": 2,
            "source": "event_house",
        },
    )


def _build_fallback_plan() -> dict:
    return _semantic_enriched_fallback_plan(
        semantic_focus_result=_semantic_focus_h3_scene_with_h4_secondary(),
        promise_prefix="",
        opening_seed=(
            "Bu dönem hayatının bir alanı daha görünür hale geliyor "
            "ve senden daha bilinçli seçimler istiyor."
        ),
        big_picture_seed=(
            "İlk bakışta görünen şey tek mesele değil; altında daha kişisel bir yön ayarı var."
        ),
        mechanism_seed=(
            "Sende zaten çalışan birkaç ayrı taraf var. "
            "Bu dönem onlar birbirini daha çok duyuyor."
        ),
        growth_edge_seed="Risk, ilk hissi sonuç sanıp süreci aceleye getirmek.",
        life_expression_seed="Daha esnek ama dağılmayan bir yön duygusu kuruyorsun.",
        what_it_builds_seed="Daha bütünlüklü bir yön kuruyorsun.",
        featured_events=[_featured_event_neptune_square_sun_h1()],
        human_scene="yakın çevrendeki ses",
        core_contrast="",
        chart_anchor="",
        raw_meaning_text="",
    )


def _full_text_from_plan(plan: dict) -> str:
    reading = _build_period_reading_v1(plan)
    return reading["full_text"]


def test_non_lifechapter_fallback_opens_with_primary_domain_anchor() -> None:
    plan = _build_fallback_plan()
    full_text = _full_text_from_plan(plan)

    # Opening must include at least one primary-domain anchor token.
    primary_anchor_tokens = (
        "sana ait",
        "iç güven",
        "ev,",
        "yalnız kaldığında",
        "kimliğini",
        "sınır",
    )
    opening_block = full_text.split("\n\n", 1)[0]
    assert any(tok in opening_block.lower() or tok in opening_block for tok in primary_anchor_tokens), (
        f"opening lacks primary-domain anchor: {opening_block!r}"
    )


def test_non_lifechapter_fallback_drops_scaffold_phrases() -> None:
    plan = _build_fallback_plan()
    full_text = _full_text_from_plan(plan)

    forbidden_substrings = (
        "Bu dönem hayatının bir alanı",
        "İlk bakışta görünen şey tek mesele değil",
        "Sende zaten çalışan birkaç ayrı taraf var",
        "Burada daha yavaş ama daha kalıcı bir çizgi",
    )
    for phrase in forbidden_substrings:
        assert phrase not in full_text, f"scaffold leaked: {phrase!r} in fallback prose"


def test_non_lifechapter_fallback_full_text_is_dense_enough() -> None:
    plan = _build_fallback_plan()
    full_text = _full_text_from_plan(plan)
    assert len(full_text) >= 450, f"fallback prose too thin: {len(full_text)} chars"


def test_non_lifechapter_fallback_full_text_has_no_broken_turkish() -> None:
    plan = _build_fallback_plan()
    full_text = _full_text_from_plan(plan)
    _assert_no_forbidden_ascii(full_text)


def test_non_lifechapter_fallback_keeps_3_to_4_blocks() -> None:
    plan = _build_fallback_plan()
    reading = _build_period_reading_v1(plan)
    assert 3 <= len(reading["blocks"]) <= 4
    assert "\n\n".join(b["text"] for b in reading["blocks"]) == reading["full_text"]


def test_non_lifechapter_fallback_marks_guided_fallback_mode() -> None:
    plan = _build_fallback_plan()
    assert plan.get("semantic_mode") == "guided_fallback"


def test_non_lifechapter_fallback_demotes_h3_scene_into_support() -> None:
    plan = _build_fallback_plan()
    full_text = _full_text_from_plan(plan)
    # The h3 scene phrase ("yakın çevrendeki ses") may still appear, but it
    # must NOT be the opening sentence — primary-domain anchor leads.
    opening_block = full_text.split("\n\n", 1)[0].lower()
    assert "yakın çevrendeki ses" not in opening_block.split(".", 1)[0], (
        f"h3 scene wrongly leads opening sentence: {opening_block!r}"
    )


# ---------------------------------------------------------------------------
# Wave-2 regression: extra scaffold strips, chart-specific closer,
# evidence-first mechanism.
# ---------------------------------------------------------------------------
def test_wave2_strips_onlar_and_generic_closer_seeds() -> None:
    plan = _build_fallback_plan()
    full_text = _full_text_from_plan(plan)

    forbidden = (
        "Bu dönem onlar birbirini daha çok duyuyor",
        "Daha esnek ama dağılmayan bir yön duygusu kuruyorsun",
    )
    for phrase in forbidden:
        assert phrase not in full_text, f"wave-2 scaffold leaked: {phrase!r}"


def test_wave2_h4_inner_anchor_emits_chart_specific_closer() -> None:
    plan = _build_fallback_plan()
    full_text = _full_text_from_plan(plan)
    assert (
        "içeride hissettiğin şeyle dışarıda gösterdiğin duruşu aynı hatta"
        in full_text
    ), f"chart-specific closer missing for h4+visible-axis combo: {full_text!r}"


def test_wave2_mechanism_leads_with_event_evidence_not_seed_scaffold() -> None:
    """Second block (mechanism) must NOT open with the seed-derived
    'Sende zaten çalışan birkaç ayrı taraf var' / 'Bu dönem onlar…' scaffold.

    For h4+visible-axis charts the mechanism leads with the concrete
    felt-sense sentence; otherwise it leads with the featured-event
    interpretation.summary. Either way, no seed scaffold first.
    """
    plan = _build_fallback_plan()
    full_text = _full_text_from_plan(plan)
    blocks = full_text.split("\n\n")
    assert len(blocks) >= 2
    second_block = blocks[1].strip()
    assert not second_block.lower().startswith("sende zaten çalışan"), (
        f"mechanism still leads with seed scaffold: {second_block!r}"
    )
    acceptable_leads = (
        "evde ya da yalnız kaldığında",  # chart-specific h4+visible support
        "duruşun ve yönün",  # event evidence fallback
    )
    assert any(second_block.lower().startswith(lead) for lead in acceptable_leads), (
        f"mechanism does not lead with chart-specific or event-evidence sentence: "
        f"{second_block!r}"
    )


# ---------------------------------------------------------------------------
# Final wave: explicit user-spec assertions for the 2026-04-22 fallback shape.
# ---------------------------------------------------------------------------
def test_final_2026_04_22_fallback_drops_orphan_pronoun_and_generic_yon_duygusu() -> None:
    plan = _build_fallback_plan()
    full_text = _full_text_from_plan(plan)
    assert "onlar birbirini" not in full_text, (
        "orphan 'onlar' scaffold leaked into fallback prose"
    )
    assert "yön duygusu" not in full_text, (
        "generic 'yön duygusu' closer leaked into fallback prose"
    )


def test_final_2026_04_22_fallback_carries_concrete_h4_h1_phrase() -> None:
    plan = _build_fallback_plan()
    full_text = _full_text_from_plan(plan).lower()
    concrete_phrases = (
        "içeride hissettiğin",
        "dışarıda gösterdiğin duruş",
        "evde",
        "yalnız kaldığında",
        "tepkini yavaşlattığında",
    )
    assert any(phrase in full_text for phrase in concrete_phrases), (
        f"no concrete h4/h1 phrase found in fallback prose: {full_text!r}"
    )


def test_final_2026_04_22_fallback_density_and_block_count_floor() -> None:
    plan = _build_fallback_plan()
    reading = _build_period_reading_v1(plan)
    assert len(reading["full_text"]) >= 400, (
        f"fallback prose too thin: {len(reading['full_text'])} chars"
    )
    assert 3 <= len(reading["blocks"]) <= 4
