from app.transit.calendar.best_times import best_times_from_calendar_payload


def test_windows_end_in_candidates_for_beauty():
    payload = {
        "range": {"tz": "Europe/Istanbul"},
        "days": [
            {
                "date": "2026-01-01",
                "moon_phase": "waxing",
                "moon_sign": "Aries",
                "moon_element": "fire",
                "flags": {},
                "rating": 1,
                "top_event_ids": [],
            },
            {
                "date": "2026-01-02",
                "moon_phase": "waxing",
                "moon_sign": "Taurus",
                "moon_element": "earth",
                "flags": {},
                "rating": 1,
                "top_event_ids": [],
            },
            {
                "date": "2026-01-03",
                "moon_phase": "waxing",
                "moon_sign": "Gemini",
                "moon_element": "air",
                "flags": {},
                "rating": 1,
                "top_event_ids": [],
            },
        ],
    }

    out = best_times_from_calendar_payload(payload, intent="beauty_care", sub_intent="nourish", top=5)
    candidate_dates = {c["date"] for c in out.get("candidates", [])}
    for w in out.get("windows", []):
        assert w["start"] in candidate_dates
        assert w["end"] in candidate_dates
