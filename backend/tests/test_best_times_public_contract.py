from app.api.routes.transits import _normalize_best_times_public_payload


def test_best_times_public_payload_sorted_and_shaped() -> None:
    raw = {
        "candidates": [
            {"date": "2026-03-02", "score": 0.7, "reason": "B"},
            {"date": "2026-03-01", "score": 0.7, "reason": "A"},
            {"date": "2026-03-03", "score": 0.9, "reason": "C"},
        ],
        "windows": [
            {"start": "2026-03-04", "end": "2026-03-06", "avg_score": 0.8},
            {"start": "2026-03-01", "end": "2026-03-02", "avg_score": 0.8},
        ],
    }

    payload = _normalize_best_times_public_payload(
        raw=raw,
        start="2026-03-01",
        end="2026-03-31",
        tz="Europe/Istanbul",
        intent="beauty_care_nourish",
    )

    assert payload["range"]["start"] == "2026-03-01"
    assert payload["intent"] == "beauty_care_nourish"
    assert payload["intent_label"] == "Besle"
    assert payload["candidates"][0]["date"] == "2026-03-03"
    assert payload["candidates"][1]["date"] == "2026-03-01"
    assert payload["windows"][0]["start"] == "2026-03-01"
    assert "reason" in payload["candidates"][0]
    assert "caution_tags" in payload["candidates"][0]
