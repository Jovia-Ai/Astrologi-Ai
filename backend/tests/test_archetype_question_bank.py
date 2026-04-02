from app.natal.archetype_question_bank import (
    build_public_question_bank,
    current_question_bank_version,
    score_archetype_answers,
)


def test_public_question_bank_exposes_core_and_adaptive_questions() -> None:
    payload = build_public_question_bank(locale="tr")

    assert payload["version"] == current_question_bank_version()
    assert payload["summary"]["core_questions"] == 24
    assert payload["summary"]["adaptive_questions"] == 6
    assert payload["questions"][0]["id"] == "aq01"
    assert payload["questions"][-1]["id"] == "aq30"


def test_score_archetype_answers_prefers_builder_for_structured_answers() -> None:
    payload = score_archetype_answers(
        [
            {"item_id": "aq01", "value": 5},
            {"item_id": "aq02", "value": 1},
            {"item_id": "aq03", "value": 5},
            {"item_id": "aq07", "value": 4},
            {"item_id": "aq08", "value": 2},
            {"item_id": "aq14", "value": 4},
        ]
    )

    assert payload["scores"]["builder"] > payload["scores"].get("visionary", 0.0)
    assert payload["scores"]["builder"] > payload["scores"].get("performer", 0.0)
    assert payload["answered_count"] == 6
    assert payload["answer_consistency"] is not None
