import pytest

from app.api.routes import natal_interpretation


def test_interpret_ui_summary_only_uses_fast_payload_only(monkeypatch) -> None:
    monkeypatch.setattr(
        natal_interpretation,
        "_build_profile_fast_payload",
        lambda request: (
            {
                "profile_fast": {
                    "sun_sign": "Capricorn",
                    "moon_sign": "Leo",
                    "rising_sign": "Capricorn",
                    "chart_ruler": "Saturn",
                    "chart_ruler_house": 3,
                    "placements": [],
                }
            },
            {"chart_compute_ms": 12.0, "serialization_ms": 2.0},
        ),
    )
    monkeypatch.setattr(
        natal_interpretation,
        "_prepare_payload",
        lambda *args, **kwargs: pytest.fail("summary_only should skip full natal preparation"),
    )

    response = natal_interpretation.interpret_natal_chart_ui(
        natal_interpretation.NatalInterpretationRequest(
            birth_date="1996-12-28",
            birth_time="07:10",
            birth_place="Istanbul, TR",
            locale="tr",
            summary_only=True,
        )
    )

    public = response["public"]
    assert public["summary_mode"] == "summary_only"
    assert public["core_story_ui"]["headline"]
    assert public["core_story_ui"]["text"]
    assert public["angles"]["ascendant_sign"] == "Capricorn"
    assert {item["planet"] for item in public["planets"]} == {
        "Sun",
        "Moon",
        "Ascendant",
    }
