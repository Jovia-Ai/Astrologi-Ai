from app.natal.archetype_question_bank import (
    build_public_question_bank,
    current_question_bank_version,
    score_archetype_answers,
    select_adaptive_questions,
)


def test_public_question_bank_exposes_core_and_adaptive_questions() -> None:
    payload = build_public_question_bank(locale="tr")

    assert payload["version"] == current_question_bank_version()
    assert payload["summary"]["core_questions"] == 24
    assert payload["summary"]["adaptive_questions"] == 12
    assert payload["questions"][0]["id"] == "aq01"
    assert payload["questions"][-1]["id"] == "aq24"
    assert payload["adaptive_questions"][0]["id"] == "aq25"
    assert payload["all_questions"][-1]["id"] == "aq36"


def test_select_adaptive_questions_prefers_requested_families() -> None:
    payload = select_adaptive_questions(
        families=["trust_depth"],
        limit=1,
    )

    assert payload
    assert len(payload) == 1
    assert payload[0]["family"] == "trust_depth"


def test_score_archetype_answers_tracks_family_and_adaptive_metadata() -> None:
    payload = score_archetype_answers(
        [
            {"item_id": "aq01", "value": 5},
            {"item_id": "aq02", "value": 1},
            {"item_id": "aq03", "value": 5},
            {"item_id": "aq07", "value": 4},
            {"item_id": "aq08", "value": 2},
            {"item_id": "aq14", "value": 4},
            {"item_id": "aq25", "value": 4},
            {"item_id": "aq26", "value": 5},
        ]
    )

    assert payload["scores"]["builder"] > payload["scores"].get("visionary", 0.0)
    assert payload["scores"]["builder"] > payload["scores"].get("performer", 0.0)
    assert payload["answered_count"] == 8
    assert payload["adaptive_answered_count"] == 2
    assert payload["family_scores"]["structure_preference"] > 0
    assert payload["family_scores"]["visibility_preference"] > 0
    assert payload["answer_consistency"] is not None
