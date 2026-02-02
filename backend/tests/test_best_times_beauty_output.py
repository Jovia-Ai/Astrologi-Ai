from app.transit.calendar.best_times import best_times_from_calendar_payload


def test_beauty_candidate_base_final_rating_and_why_support():
    payload = {
        "range": {"tz": "Europe/Istanbul"},
        "days": [
            {
                "date": "2026-01-08",
                "moon_phase": "waning",
                "moon_sign": "Scorpio",
                "moon_element": "water",
                "flags": {},
                "rating": 2,
                "critical_reason": ["phase_shift"],
                "is_critical": True,
                "top_event_ids": [],
            }
        ],
    }

    out = best_times_from_calendar_payload(payload, intent="beauty_care", sub_intent="nourish", top=5)
    candidates = {c["date"]: c for c in out.get("candidates", [])}
    cand = candidates["2026-01-08"]

    assert cand["base_rating"] == 2
    assert cand["final_rating"] == 1
    assert cand["cautions"]
    assert "yön değişimi" in cand["cautions"][0].lower()
    assert cand["action_type"] == "care"
    assert cand["rating_reason_user"]
    assert cand["recommendation_user"]
    assert "gate:" not in " ".join(cand.get("why_support", []))
    assert "phase_shift" in (cand.get("explainers") or {})
    assert "waning_moon" in (cand.get("explainers") or {})


def test_beauty_action_type_change_when_venus_support():
    payload = {
        "range": {"tz": "Europe/Istanbul"},
        "days": [
            {
                "date": "2026-01-10",
                "moon_phase": "waxing",
                "moon_sign": "Taurus",
                "moon_element": "earth",
                "flags": {},
                "rating": 2,
                "top_event_ids": ["tr.venus.sextile.jupiter"],
            }
        ],
    }

    out = best_times_from_calendar_payload(payload, intent="beauty_care", sub_intent="nourish", top=5)
    cand = out["candidates"][0]

    assert cand["action_type"] == "change"
    assert "Değişim yapılabilir" in cand["recommendation_user"]


def test_daily_hint_has_all_days():
    payload = {
        "range": {"tz": "Europe/Istanbul"},
        "days": [
            {
                "date": "2026-01-11",
                "moon_phase": "waxing",
                "moon_sign": "Gemini",
                "moon_element": "air",
                "flags": {},
                "rating": 2,
                "top_event_ids": [],
            },
            {
                "date": "2026-01-12",
                "moon_phase": "waning",
                "moon_sign": "Cancer",
                "moon_element": "water",
                "flags": {},
                "rating": 2,
                "top_event_ids": [],
            },
        ],
    }

    out = best_times_from_calendar_payload(payload, intent="beauty_care", sub_intent="nourish", top=5)
    assert len(out["daily_hint"]["days"]) == 2
    assert all("gate:" not in s for s in cand.get("why_support", []))
