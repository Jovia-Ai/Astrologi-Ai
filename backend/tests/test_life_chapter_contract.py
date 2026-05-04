from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.narrative.voice_guardrails_tr import validate_life_chapter_selected_meaning
from app.transit.narrative.life_chapter_contract import (
    ActivatedNatalFactor,
    ChapterConfidence,
    ChapterPhase,
    ChapterPriority,
    ChapterType,
    LifeChapter,
    LifeChapterEvidence,
    LifeChapterTimeWindow,
    SuppressedReading,
)


def _base_payload(*, chapter_type: ChapterType = ChapterType.SATURN_RETURN, selected_meaning: str = "Koç 3. evdeki eski refleksif konuşma biçiminin daha seçilmiş bir forma girmesi") -> dict:
    return {
        "chapter_id": "chapter:saturn-return-aries-3",
        "chapter_type": chapter_type,
        "domain": "communication_learning",
        "spine_line": "growth_integration_line",
        "time_window": LifeChapterTimeWindow(start="2026-03-01", peak="2026-05-01", end="2026-10-01"),
        "phase": ChapterPhase.FIRST_PASS,
        "activated_natal_factors": [
            ActivatedNatalFactor(type="planet", id="saturn"),
            ActivatedNatalFactor(type="node", id="south_node"),
            ActivatedNatalFactor(type="house", id="house:3"),
        ],
        "core_question": "Sözün hangi yerde daha seçilmiş ve daha sorumlu bir forma girmek istiyor?",
        "selected_meaning": selected_meaning,
        "selected_meaning_family": "speech_authority_maturation",
        "semantic_focus": {
            "primary": "speech_authority",
            "secondary": ["self_definition", "mental_reflex_maturation"],
            "not_this": ["generic communication stress"],
        },
        "domain_ownership": {
            "primary_domain": "communication_learning",
            "secondary_domains": ["identity_presence"],
            "rationale": "3. evdeki Satürn dönüşü söz ve zihinsel refleks alanını sahipleniyor.",
        },
        "renderer_handoff": {
            "human_scene": "kısa mesajlar, yarım kalmış konuşmalar, hızlı cevap verme anları",
            "core_contrast": "hızlı cevap vermek ile gerçekten nerede durduğunu söylemek",
            "chapter_weight": "not ordinary transit; long-cycle maturation",
            "chart_specific_anchor": "eski refleksif konuşma kalıbının daha seçilmiş bir omurgaya yerleşmesi",
            "voice_register": "maturation / medium",
            "avoid_readings": ["generic communication stress"],
        },
        "evidence": [
            LifeChapterEvidence(
                factor="transit_saturn_conj_natal_saturn",
                role="chapter_trigger",
                explanation="Transit Satürn natal Satürn hattını doğrudan tetikliyor.",
            )
        ],
        "suppressed_readings": [
            SuppressedReading(
                reading="generic communication stress",
                reason="Node overlap ve natal pattern desteği bunu daha spesifik bir olgunlaşma teması yapıyor.",
            )
        ],
        "suppressed_surface_readings": [
            SuppressedReading(
                reading="generic communication stress",
                reason="Bu chapter iletişim sorunu diye daraltılmıyor; söz otoritesinin olgunlaşması olarak okunuyor.",
            )
        ],
        "voice_hints": {
            "valence_mode": "maturation",
            "intensity_mode": "medium",
            "rhetorical_frame": "construction",
            "tone": "friend-warm",
        },
        "priority": ChapterPriority.LIFE_CHAPTER,
        "confidence": ChapterConfidence.HIGH,
        "debug": {"source_signal_types": ["saturn_return", "node_overlap"]},
    }


def test_minimal_life_chapter_instantiates() -> None:
    chapter = LifeChapter(**_base_payload())
    assert chapter.version == "life_chapter_v1"
    assert chapter.chapter_type == ChapterType.SATURN_RETURN
    assert chapter.priority == ChapterPriority.LIFE_CHAPTER


@pytest.mark.parametrize("chapter_type", list(ChapterType))
def test_all_eleven_chapter_types_are_accepted(chapter_type: ChapterType) -> None:
    chapter = LifeChapter(**_base_payload(chapter_type=chapter_type))
    assert chapter.chapter_type == chapter_type


def test_missing_evidence_fails() -> None:
    payload = _base_payload()
    payload["evidence"] = []
    with pytest.raises(ValidationError):
        LifeChapter(**payload)


def test_missing_suppressed_readings_fails() -> None:
    payload = _base_payload()
    payload["suppressed_readings"] = []
    with pytest.raises(ValidationError):
        LifeChapter(**payload)


def test_missing_suppressed_surface_readings_fails() -> None:
    payload = _base_payload()
    payload["suppressed_surface_readings"] = []
    with pytest.raises(ValidationError):
        LifeChapter(**payload)


def test_empty_selected_meaning_fails() -> None:
    payload = _base_payload(selected_meaning="")
    with pytest.raises(ValidationError):
        LifeChapter(**payload)


def test_cookbook_selected_meaning_fails() -> None:
    payload = _base_payload(selected_meaning="Saturn return = sorumluluk dönemi")
    with pytest.raises(ValidationError):
        LifeChapter(**payload)


def test_predictive_selected_meaning_fails() -> None:
    payload = _base_payload(selected_meaning="Bu chapter sayesinde terfi alacaksın ve para kazanacaksın")
    with pytest.raises(ValidationError):
        LifeChapter(**payload)


def test_natal_specific_selected_meaning_passes() -> None:
    chapter = LifeChapter(**_base_payload(selected_meaning="Koç 3. evdeki eski refleksif konuşma biçiminin daha seçilmiş bir forma girmesi"))
    assert "Koç 3. evdeki" in chapter.selected_meaning


def test_life_chapter_selected_meaning_guardrail_flags_cookbook_and_prediction() -> None:
    cookbook = validate_life_chapter_selected_meaning("Nodal return = kader dönemi")
    prediction = validate_life_chapter_selected_meaning("Bu dönem kesin terfi alacaksın")
    assert cookbook
    assert prediction


def test_life_chapter_selected_meaning_guardrail_accepts_specific_non_predictive_meaning() -> None:
    issues = validate_life_chapter_selected_meaning(
        "Koç 3. evde hızla çıkan sözlerin daha ölçülü ve daha seçilmiş bir omurga kazanması"
    )
    assert issues == []
