from app.api.routes import transits


def _request(**kwargs):
    base = {
        "birth_date": "1996-12-28",
        "birth_time": "07:10",
        "birth_place": "Istanbul, TR",
        "start": "2026-03-01",
        "end": "2026-03-31",
        "tz": "Europe/Istanbul",
        "include_best_times": False,
    }
    base.update(kwargs)
    return transits.TransitNarrativeRequest(**base)


def test_transit_narrative_includes_public_event_cards(monkeypatch) -> None:
    monkeypatch.setattr(
        transits,
        "build_transit_calendar_public",
        lambda **_: {"calendar_internal": {"days": [{"date": "2026-03-10", "rating": 2, "heat": 1, "event_count": 1}]}} ,
    )
    monkeypatch.setattr(
        transits,
        "to_ui_calendar",
        lambda *_args, **_kwargs: {
            "range": {"start": "2026-03-01", "end": "2026-03-31", "tz": "Europe/Istanbul"},
            "days": [{"date": "2026-03-10", "labels": ["mind"], "top_events": [{"id": "evt_1"}], "is_critical": False}],
            "year_summary": {},
        },
    )
    monkeypatch.setattr(transits, "assemble_blocks", lambda **_: [])
    monkeypatch.setattr(transits, "build_space_hub", lambda _blocks: {"title": "", "blocks": [], "count": 0})
    monkeypatch.setattr(
        transits,
        "build_personal_transit",
        lambda _blocks: {"title": "", "blocks": [], "count": 0},
    )
    monkeypatch.setattr(
        transits,
        "build_calendar_day",
        lambda _blocks, _date: {"title": "", "blocks": [], "count": 0},
    )
    monkeypatch.setattr(transits, "build_feed_snippet", lambda _blocks: {"title": "", "blocks": [], "count": 0})
    monkeypatch.setattr(
        transits,
        "_build_narrative_public_payload",
        lambda _request, _start_date: {
            "period_core": {"title": "Core"},
            "event_cards": [{"event_id": "evt_1", "natal_promise": {"score": 0.7}}],
            "period_peak_timeline": [
                {
                    "event_id": "evt_1",
                    "peak_date_utc": "2026-03-05T09:00:00+00:00",
                    "event_card": {"event_id": "evt_1"},
                }
            ],
            "timeline": {"summary": "line"},
        },
    )

    response = transits.build_transit_narrative(_request(selected_date="2026-03-10"))
    assert "public" in response
    assert isinstance(response["public"]["event_cards"], list)
    assert response["public"]["event_cards"][0]["natal_promise"]["score"] == 0.7
    assert response["public"]["period_peak_timeline"][0]["peak_date_utc"] == "2026-03-05T09:00:00+00:00"


def test_transit_narrative_public_payload_fallback_on_error(monkeypatch) -> None:
    monkeypatch.setattr(
        transits,
        "build_transit_calendar_public",
        lambda **_: {"calendar_internal": {"days": [{"date": "2026-03-10", "rating": 2, "heat": 1, "event_count": 1}]}} ,
    )
    monkeypatch.setattr(
        transits,
        "to_ui_calendar",
        lambda *_args, **_kwargs: {
            "range": {"start": "2026-03-01", "end": "2026-03-31", "tz": "Europe/Istanbul"},
            "days": [{"date": "2026-03-10", "labels": [], "top_events": [], "is_critical": False}],
            "year_summary": {},
        },
    )
    monkeypatch.setattr(transits, "assemble_blocks", lambda **_: [])
    monkeypatch.setattr(transits, "build_space_hub", lambda _blocks: {"title": "", "blocks": [], "count": 0})
    monkeypatch.setattr(
        transits,
        "build_personal_transit",
        lambda _blocks: {"title": "", "blocks": [], "count": 0},
    )
    monkeypatch.setattr(
        transits,
        "build_calendar_day",
        lambda _blocks, _date: {"title": "", "blocks": [], "count": 0},
    )
    monkeypatch.setattr(transits, "build_feed_snippet", lambda _blocks: {"title": "", "blocks": [], "count": 0})

    def _raise(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(transits, "_build_narrative_public_payload", _raise)

    response = transits.build_transit_narrative(_request())
    assert "public" in response
    assert response["public"]["event_cards"] == []
    assert response["public"]["period_peak_timeline"] == []
    assert response["public"]["period_core"] == {}
    assert response["public"]["timeline"] == {}


def test_transit_narrative_debug_includes_period_selection(monkeypatch) -> None:
    monkeypatch.setattr(
        transits,
        "build_transit_calendar_public",
        lambda **_: {"calendar_internal": {"days": [{"date": "2026-03-10", "rating": 2, "heat": 1, "event_count": 1}]}} ,
    )
    monkeypatch.setattr(
        transits,
        "to_ui_calendar",
        lambda *_args, **_kwargs: {
            "range": {"start": "2026-03-01", "end": "2026-03-31", "tz": "Europe/Istanbul"},
            "days": [{"date": "2026-03-10", "labels": [], "top_events": [], "is_critical": False}],
            "year_summary": {},
        },
    )
    monkeypatch.setattr(transits, "assemble_blocks", lambda **_: [])
    monkeypatch.setattr(transits, "build_space_hub", lambda _blocks: {"title": "", "blocks": [], "count": 0})
    monkeypatch.setattr(transits, "build_personal_transit", lambda _blocks: {"title": "", "blocks": [], "count": 0})
    monkeypatch.setattr(transits, "build_calendar_day", lambda _blocks, _date: {"title": "", "blocks": [], "count": 0})
    monkeypatch.setattr(transits, "build_feed_snippet", lambda _blocks: {"title": "", "blocks": [], "count": 0})
    monkeypatch.setattr(
        transits,
        "_build_narrative_public_payload",
        lambda _request, _start_date: {
            "period_core": {"title": "Core"},
            "event_cards": [{"event_id": "evt_1"}],
            "period_peak_timeline": [{"event_id": "evt_1"}],
            "timeline": {"summary": "line"},
            "_period_coverage": {"counts": {"total": 1}},
            "_period_selection": {"selection_mode": "coverage_first_v1", "selected_ids": ["evt_1"]},
            "_period_root_causes": [{"key": "identity_spine", "score": 0.82, "evidence": ["Neptune square ASC"]}],
            "_events_debug": [{"event_id": "ev_debug_1"}],
        },
    )

    response = transits.build_transit_narrative(_request(debug=True))
    assert "_period_coverage" not in response["public"]
    assert "_period_selection" not in response["public"]
    assert "_period_root_causes" not in response["public"]
    assert response["debug"]["period_coverage"]["counts"]["total"] == 1
    assert response["debug"]["period_selection"]["selection_mode"] == "coverage_first_v1"
    assert response["debug"]["period_root_causes"][0]["key"] == "identity_spine"
    assert response["debug"]["events_debug"][0]["event_id"] == "ev_debug_1"
