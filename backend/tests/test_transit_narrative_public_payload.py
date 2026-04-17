import pytest

from app.api.routes import transits
from app.services.performance.cache_store import InMemoryCacheStore


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


@pytest.fixture(autouse=True)
def _fresh_transit_route_cache(monkeypatch):
    monkeypatch.setattr(transits, "default_cache_store", InMemoryCacheStore())


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
    assert response["meta"]["snapshot_id"].startswith("trsnap_")
    assert response["meta"]["source_meta"]["endpoint"] == "/transit/narrative"
    assert isinstance(response["public"]["event_cards"], list)
    assert response["public"]["event_cards"][0]["natal_promise"]["score"] == 0.7
    assert response["public"]["period_peak_timeline"][0]["peak_date_utc"] == "2026-03-05T09:00:00+00:00"


def test_transit_narrative_humanizes_event_cards_and_calendar_days(monkeypatch) -> None:
    monkeypatch.setattr(transits, "_build_transits_engine_response", lambda _request: {})
    base_card = {
        "event_id": "evt_1",
        "transit_body": "Moon",
        "aspect": "square",
        "horizon": "daily",
        "derived_context": {"natal_target": {"house": 3}},
        "natal_promise": {"score": 0.7},
    }
    monkeypatch.setattr(
        transits,
        "build_public_response",
        lambda _response: {
            "period_core": {"title": "Core"},
            "event_cards": [base_card],
            "period_peak_timeline": [],
            "timeline": {"summary": "line"},
        },
    )
    monkeypatch.setattr(
        transits,
        "select_event_ids",
        lambda _items, max_cards, natal=None: ([], {"selection_mode": "test"}),
    )
    monkeypatch.setattr(
        transits,
        "build_period_coverage",
        lambda _items, selected_ids, now_date, tz: {"counts": {"total": 0}},
    )
    monkeypatch.setattr(
        transits,
        "build_transit_calendar_public",
        lambda **_: {"calendar_internal": {"days": [{"date": "2026-03-10", "rating": 4, "heat": 3, "event_count": 2}]}} ,
    )
    monkeypatch.setattr(
        transits,
        "to_ui_calendar",
        lambda *_args, **_kwargs: {
            "range": {"start": "2026-03-01", "end": "2026-03-31", "tz": "Europe/Istanbul"},
            "days": [
                {
                    "date": "2026-03-10",
                    "labels": ["mind"],
                    "top_events": [{"id": "evt_1"}, {"id": "evt_2"}],
                    "event_count": 2,
                    "heat": 3,
                    "rating": 4,
                    "is_critical": False,
                }
            ],
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
        "_select_daily_and_period_event_cards",
        lambda **_: {
            "daily_event_cards": [transits._humanize_event_card(base_card)],
            "period_event_cards": [],
            "daily_selection": {
                "used_period_fallback": False,
                "period_only_note": "",
                "daily_count": 1,
                "period_count": 0,
            },
        },
    )
    response = transits.build_transit_narrative(_request(selected_date="2026-03-10"))

    card = response["public"]["event_cards"][0]
    assert card["felt_line_tr"]
    assert card["why_it_feels_this_way_tr"]
    assert card["guidance_micro_tr"]
    assert card["house_touchpoint_tr"] == "zihnin ve konuşma halin"
    assert response["public"]["daily_event_cards"][0]["event_id"] == "evt_1"
    assert response["public"]["period_event_cards"] == []
    assert response["calendar"]["days"][0]["signal_label_tr"] == "Yüksek tempo."
    assert response["calendar"]["days"][0]["tone_label_tr"] == "yuksek_tempo"
    assert response["calendar"]["days"][0]["micro_summary_tr"] == card["felt_line_tr"]


def test_transit_narrative_uses_period_fallback_when_daily_missing(monkeypatch) -> None:
    monkeypatch.setattr(transits, "_build_transits_engine_response", lambda _request: {})
    period_card = {
        "event_id": "evt_period",
        "transit_body": "Saturn",
        "aspect": "opposition",
        "horizon": "period",
        "bucket": "long",
        "derived_context": {"natal_target": {"house": 7}},
    }
    monkeypatch.setattr(
        transits,
        "build_public_response",
        lambda _response: {
            "period_core": {"title": "Core"},
            "event_cards": [period_card],
            "period_peak_timeline": [],
            "timeline": {"summary": "line"},
        },
    )
    monkeypatch.setattr(
        transits,
        "select_event_ids",
        lambda _items, max_cards, natal=None: ([], {"selection_mode": "test"}),
    )
    monkeypatch.setattr(
        transits,
        "build_period_coverage",
        lambda _items, selected_ids, now_date, tz: {"counts": {"total": 0}},
    )
    monkeypatch.setattr(
        transits,
        "_select_daily_and_period_event_cards",
        lambda **_: {
            "daily_event_cards": [
                {
                    **transits._humanize_event_card(period_card),
                    "horizon": "daily",
                    "is_period_derived": True,
                    "today_facing_fallback": True,
                    "source_horizon": "period",
                }
            ],
            "period_event_cards": [transits._humanize_event_card(period_card)],
            "daily_selection": {
                "used_period_fallback": True,
                "period_only_note": "fallback",
                "daily_count": 1,
                "period_count": 1,
            },
        },
    )

    payload = transits._build_narrative_public_payload(
        _request(selected_date="2026-03-10"),
        transits.date_type.fromisoformat("2026-03-01"),
    )

    assert payload["daily_selection"]["used_period_fallback"] is True
    assert payload["daily_event_cards"][0]["horizon"] == "daily"
    assert payload["period_event_cards"][0]["event_id"] == "evt_period"


def test_public_payload_attaches_global_period_story_to_daily_cards(monkeypatch) -> None:
    monkeypatch.setattr(transits, "_build_transits_engine_response", lambda _request: {})
    monkeypatch.setattr(
        transits,
        "build_public_response",
        lambda _response: {
            "period_core": {
                "title": "Zihinsel Otoriteni İnşa Ediyorsun",
                "core_story": "Dönemin omurgası burada.",
                "mechanism": "Önce zihinde başlıyor, sonra duruşa yansıyor.",
            },
            "event_cards": [],
            "period_peak_timeline": [],
            "timeline": {"summary": "line"},
        },
    )
    monkeypatch.setattr(
        transits,
        "select_event_ids",
        lambda _items, max_cards, natal=None: ([], {"selection_mode": "test"}),
    )
    monkeypatch.setattr(
        transits,
        "build_period_coverage",
        lambda _items, selected_ids, now_date, tz: {"counts": {"total": 0}},
    )
    monkeypatch.setattr(
        transits,
        "_select_daily_and_period_event_cards",
        lambda **_: {
            "daily_event_cards": [
                {
                    "event_id": "evt_1",
                    "transit_body": "Mercury",
                    "natal_point": "Sun",
                    "aspect": "square",
                    "horizon": "daily",
                    "signature_tr": "Merkür □ Güneş • Tam üstünde",
                    "derived_context": {"natal_target": {"house": 3}},
                    "scene": {"start_house": 3, "outcome_house": 3},
                }
            ],
            "period_event_cards": [],
            "daily_selection": {
                "used_period_fallback": False,
                "period_only_note": "",
                "daily_count": 1,
                "period_count": 0,
            },
        },
    )

    payload = transits._build_narrative_public_payload(
        _request(selected_date="2026-03-10"),
        transits.date_type.fromisoformat("2026-03-01"),
    )

    assert (
        '"Zihinsel Otoriteni İnşa Ediyorsun" döneminin sana hangi kapıdan açıldığını gösteriyor'
        in payload["daily_event_cards"][0]["why_it_feels_this_way_tr"]
    )
    assert "Bu hikâye tek katmanlı değil: Dönemin omurgası burada" in payload["daily_event_cards"][0]["why_it_feels_this_way_tr"]


def test_public_payload_limits_daily_selection_to_public_cards_without_day_context(monkeypatch) -> None:
    raw_items = [
        {"event_id": "evt_1", "transit_body": "Moon", "aspect": "square", "natal_point": "Venus"},
        {"event_id": "evt_2", "transit_body": "Saturn", "aspect": "trine", "natal_point": "Mercury"},
        {"event_id": "evt_3", "transit_body": "Mars", "aspect": "opposition", "natal_point": "Sun"},
    ]
    captured = {}

    monkeypatch.setattr(
        transits,
        "_build_transits_engine_response",
        lambda _request: {"display": {"items": raw_items}, "natal": {"bodies": []}},
    )
    monkeypatch.setattr(
        transits,
        "build_public_response",
        lambda _response: {
            "period_core": {"title": "Core"},
            "event_cards": [
                {"event_id": "evt_1", "headline": "One"},
                {"event_id": "evt_3", "headline": "Three"},
            ],
            "period_peak_timeline": [],
            "timeline": {},
        },
    )
    monkeypatch.setattr(
        transits,
        "select_event_ids",
        lambda _items, max_cards, natal=None: ([], {"selection_mode": "test"}),
    )
    monkeypatch.setattr(transits, "build_period_coverage", lambda _items, selected_ids, now_date, tz: {})

    def _capture_daily_selection(**kwargs):
        captured["raw_events"] = [str(item.get("event_id") or "") for item in kwargs.get("raw_events") or []]
        return {
            "daily_event_cards": [],
            "period_event_cards": [],
            "daily_selection": {},
        }

    monkeypatch.setattr(transits, "_select_daily_and_period_event_cards", _capture_daily_selection)

    transits._build_narrative_public_payload(
        _request(start="2026-03-10", end="2026-03-10", selected_date="2026-03-10"),
        transits.date_type.fromisoformat("2026-03-10"),
        selected_day_context={},
    )

    assert captured["raw_events"] == ["evt_1", "evt_3"]


def test_selected_day_context_reads_internal_top_event_ids_and_signals() -> None:
    context = transits._selected_day_context_from_calendar(
        {
            "days": [
                {
                    "date": "2026-03-10",
                    "labels": ["mind"],
                    "top_event_ids": ["evt_internal_a", "evt_internal_b"],
                    "event_count": 5,
                    "signals_count": 7,
                    "is_critical": True,
                    "critical_reason": ["event_peak"],
                }
            ]
        },
        "2026-03-10",
    )

    assert context["top_event_ids"] == ["evt_internal_a", "evt_internal_b"]
    assert context["event_count"] == 5
    assert context["signals_count"] == 7
    assert context["critical_reasons"] == ["event_peak"]
    assert context["is_critical"] is True


def test_transit_narrative_uses_internal_day_context_for_public_payload(monkeypatch) -> None:
    captured = {}

    monkeypatch.setattr(
        transits,
        "build_transit_calendar_public",
        lambda **_: {
            "calendar_internal": {
                "days": [
                    {
                        "date": "2026-03-10",
                        "labels": ["mind"],
                        "top_event_ids": ["evt_internal"],
                        "event_count": 4,
                        "signals_count": 6,
                        "is_critical": False,
                    }
                ]
            }
        },
    )
    monkeypatch.setattr(
        transits,
        "to_ui_calendar",
        lambda *_args, **_kwargs: {
            "range": {"start": "2026-03-10", "end": "2026-03-10", "tz": "Europe/Istanbul"},
            "days": [{"date": "2026-03-10", "labels": ["mind"], "top_events": [], "is_critical": False}],
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

    def _capture_public_payload(_request, _start_date, *, selected_day_context=None):
        captured["selected_day_context"] = dict(selected_day_context or {})
        return {
            "period_core": {},
            "event_cards": [],
            "daily_event_cards": [],
            "period_event_cards": [],
            "daily_selection": {},
            "period_peak_timeline": [],
            "timeline": {},
        }

    monkeypatch.setattr(transits, "_build_narrative_public_payload", _capture_public_payload)

    transits.build_transit_narrative(_request(selected_date="2026-03-10"))

    assert captured["selected_day_context"]["top_event_ids"] == ["evt_internal"]
    assert captured["selected_day_context"]["event_count"] == 4
    assert captured["selected_day_context"]["signals_count"] == 6


def test_public_only_builds_selected_day_context_for_selected_date(monkeypatch) -> None:
    captured = {}

    monkeypatch.setattr(
        transits,
        "build_transit_calendar_public",
        lambda **_: {
            "calendar_internal": {
                "days": [
                    {
                        "date": "2026-03-10",
                        "labels": ["mind"],
                        "top_event_ids": ["evt_public_only"],
                        "event_count": 3,
                        "signals_count": 5,
                        "is_critical": False,
                    }
                ]
            }
        },
    )

    def _capture_public_payload(_request, _start_date, *, selected_day_context=None):
        captured["selected_day_context"] = dict(selected_day_context or {})
        return {
            "period_core": {},
            "event_cards": [],
            "daily_event_cards": [],
            "period_event_cards": [],
            "daily_selection": {},
            "period_peak_timeline": [],
            "timeline": {},
        }

    monkeypatch.setattr(transits, "_build_narrative_public_payload", _capture_public_payload)

    transits.build_transit_narrative(
        _request(
            start="2026-03-10",
            end="2026-03-10",
            selected_date="2026-03-10",
            response_mode="public_only",
        )
    )

    assert captured["selected_day_context"]["top_event_ids"] == ["evt_public_only"]
    assert captured["selected_day_context"]["event_count"] == 3
    assert captured["selected_day_context"]["signals_count"] == 5


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
    assert response["meta"]["snapshot_id"].startswith("trsnap_")
    assert response["meta"]["source_meta"]["endpoint"] == "/transit/narrative"
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
    assert response["meta"]["snapshot_id"].startswith("trsnap_")
    assert response["meta"]["source_meta"]["endpoint"] == "/transit/narrative"
    assert "_period_coverage" not in response["public"]
    assert "_period_selection" not in response["public"]
    assert "_period_root_causes" not in response["public"]
    assert response["debug"]["period_coverage"]["counts"]["total"] == 1
    assert response["debug"]["period_selection"]["selection_mode"] == "coverage_first_v1"
    assert response["debug"]["period_root_causes"][0]["key"] == "identity_spine"
    assert response["debug"]["events_debug"][0]["event_id"] == "ev_debug_1"
    assert response["debug"]["selected_day_public"]["date"] == "2026-03-01"


def test_transit_narrative_uses_route_cache(monkeypatch) -> None:
    monkeypatch.setattr(transits, "default_cache_store", InMemoryCacheStore())
    monkeypatch.setattr(transits.settings, "transit_narrative_ttl_seconds", 300)
    monkeypatch.setattr(transits.settings, "transit_narrative_stale_ttl_seconds", 300)

    calls = {"calendar": 0}

    def _calendar_payload(**_kwargs):
        calls["calendar"] += 1
        return {"calendar_internal": {"days": [{"date": "2026-03-10", "rating": 2, "heat": 1, "event_count": 1}]}}

    monkeypatch.setattr(transits, "build_transit_calendar_public", _calendar_payload)
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
            "daily_event_cards": [],
            "period_event_cards": [],
            "daily_selection": {},
            "period_peak_timeline": [{"event_id": "evt_1"}],
            "timeline": {"summary": "line"},
        },
    )

    first = transits.build_transit_narrative(_request(debug=True, selected_date="2026-03-10"))
    second = transits.build_transit_narrative(_request(debug=True, selected_date="2026-03-10"))

    assert calls["calendar"] == 1
    assert first["debug"]["cache_status"] == "miss"
    assert second["debug"]["cache_status"] == "hit"
    assert first["meta"]["snapshot_id"] != second["meta"]["snapshot_id"]


def test_transit_narrative_public_only_uses_selected_day_context_without_calendar_response(monkeypatch) -> None:
    calls = {"calendar": 0}

    monkeypatch.setattr(
        transits,
        "build_transit_calendar_public",
        lambda **_: (
            calls.__setitem__("calendar", calls["calendar"] + 1) or {
                "calendar_internal": {
                    "days": [
                        {
                            "date": "2026-03-10",
                            "labels": ["mind"],
                            "top_event_ids": ["evt_context"],
                            "event_count": 2,
                            "signals_count": 3,
                            "is_critical": False,
                        }
                    ]
                }
            }
        ),
    )
    monkeypatch.setattr(
        transits,
        "_build_narrative_public_payload",
        lambda _request, _start_date, selected_day_context=None: {
            "period_core": {"title": "Relationship core"},
            "daily_event_cards": [{"event_id": "evt_daily"}],
            "period_event_cards": [{"event_id": "evt_period"}],
            "daily_selection": {"daily_count": 1, "period_count": 1},
            "event_cards": [{"event_id": "evt_daily"}],
            "period_peak_timeline": [],
            "timeline": {"summary": "line"},
        },
    )

    response = transits.build_transit_narrative(
        _request(
            selected_date="2026-03-10",
            response_mode="public_only",
            start="2026-03-10",
            end="2026-03-10",
        )
    )

    assert response["public"]["period_core"]["title"] == "Relationship core"
    assert response["public"]["daily_event_cards"][0]["event_id"] == "evt_daily"
    assert "calendar" not in response
    assert response["range"]["start"] == "2026-03-10"
    assert calls["calendar"] == 1


def test_transit_narrative_public_only_home_includes_selected_day_calendar(monkeypatch) -> None:
    monkeypatch.setattr(
        transits,
        "build_transit_calendar_public",
        lambda **_: {
            "calendar_internal": {
                "days": [
                    {
                        "date": "2026-03-10",
                        "labels": ["mind"],
                        "top_event_ids": ["evt_context"],
                        "event_count": 2,
                        "signals_count": 3,
                        "is_critical": False,
                    }
                ]
            }
        },
    )
    monkeypatch.setattr(
        transits,
        "_build_narrative_public_payload",
        lambda _request, _start_date, selected_day_context=None: {
            "period_core": {"title": "Home core"},
            "daily_event_cards": [
                {
                    "event_id": "evt_daily",
                    "felt_line_tr": "Bugün bir konu netleşiyor.",
                    "why_it_feels_this_way_tr": "Zihin ve yakın çevre alanı aktif.",
                }
            ],
            "period_event_cards": [],
            "daily_selection": {"daily_count": 1, "period_count": 0},
            "event_cards": [{"event_id": "evt_daily"}],
            "period_peak_timeline": [],
            "timeline": {"summary": "line"},
        },
    )

    response = transits.build_transit_narrative(
        _request(
            selected_date="2026-03-10",
            response_mode="public_only",
            payload_profile="home",
            start="2026-03-10",
            end="2026-03-10",
        )
    )

    assert response["public"]["period_core"]["title"] == "Home core"
    assert response["calendar"]["days"][0]["date"] == "2026-03-10"
    assert response["calendar"]["days"][0]["signals_count"] == 3
    assert response["calendar"]["days"][0]["micro_summary_tr"] == "Bugün bir konu netleşiyor."


def test_transit_narrative_public_only_home_empty_payload_does_not_cache(monkeypatch) -> None:
    calls = {"calendar": 0}

    monkeypatch.setattr(
        transits,
        "build_transit_calendar_public",
        lambda **_: (
            calls.__setitem__("calendar", calls["calendar"] + 1) or {
                "calendar_internal": {"days": []}
            }
        ),
    )
    monkeypatch.setattr(
        transits,
        "_build_narrative_public_payload",
        lambda _request, _start_date, selected_day_context=None: {
            "period_core": {},
            "daily_event_cards": [],
            "period_event_cards": [],
            "daily_selection": {},
            "event_cards": [],
            "period_peak_timeline": [],
            "timeline": {},
        },
    )

    first = transits.build_transit_narrative(
        _request(
            selected_date="2026-03-10",
            response_mode="public_only",
            payload_profile="home",
            start="2026-03-10",
            end="2026-03-10",
            debug=True,
        )
    )
    second = transits.build_transit_narrative(
        _request(
            selected_date="2026-03-10",
            response_mode="public_only",
            payload_profile="home",
            start="2026-03-10",
            end="2026-03-10",
            debug=True,
        )
    )

    assert first["debug"]["cache_status"] == "miss"
    assert second["debug"]["cache_status"] == "miss"
    assert calls["calendar"] == 2


def test_transit_narrative_public_only_home_timeline_only_payload_does_not_cache(monkeypatch) -> None:
    calls = {"calendar": 0}

    monkeypatch.setattr(
        transits,
        "build_transit_calendar_public",
        lambda **_: (
            calls.__setitem__("calendar", calls["calendar"] + 1) or {
                "calendar_internal": {"days": []}
            }
        ),
    )
    monkeypatch.setattr(
        transits,
        "_build_narrative_public_payload",
        lambda _request, _start_date, selected_day_context=None: {
            "period_core": {"title": "Home core"},
            "daily_event_cards": [],
            "period_event_cards": [],
            "daily_selection": {},
            "event_cards": [],
            "period_peak_timeline": [],
            "timeline": {"summary": "timeline-only"},
        },
    )

    first = transits.build_transit_narrative(
        _request(
            selected_date="2026-03-10",
            response_mode="public_only",
            payload_profile="home",
            start="2026-03-10",
            end="2026-03-10",
            debug=True,
        )
    )
    second = transits.build_transit_narrative(
        _request(
            selected_date="2026-03-10",
            response_mode="public_only",
            payload_profile="home",
            start="2026-03-10",
            end="2026-03-10",
            debug=True,
        )
    )

    assert first["debug"]["cache_status"] == "miss"
    assert second["debug"]["cache_status"] == "miss"
    assert calls["calendar"] == 2


def test_transit_narrative_public_only_home_exception_marks_degraded_debug(monkeypatch) -> None:
    monkeypatch.setattr(
        transits,
        "build_transit_calendar_public",
        lambda **_: {
            "calendar_internal": {
                "days": [
                    {
                        "date": "2026-03-10",
                        "labels": ["mind"],
                        "top_event_ids": ["evt_context"],
                        "event_count": 2,
                        "signals_count": 3,
                        "is_critical": False,
                    }
                ]
            }
        },
    )

    def _raise(*_args, **_kwargs):
        raise RuntimeError("home public_only failure")

    monkeypatch.setattr(transits, "_build_narrative_public_payload", _raise)

    response = transits.build_transit_narrative(
        _request(
            selected_date="2026-03-10",
            response_mode="public_only",
            payload_profile="home",
            start="2026-03-10",
            end="2026-03-10",
            debug=True,
        )
    )

    assert response["public"]["daily_event_cards"] == []
    assert response["calendar"]["days"][0]["date"] == "2026-03-10"
    assert response["debug"]["degraded_path"]["active"] is True
    assert response["debug"]["degraded_path"]["reason"] == "public_payload_exception"
    assert response["debug"]["degraded_path"]["error_type"] == "RuntimeError"


def test_transit_narrative_public_only_home_invalid_selected_date_falls_back_to_anchor(monkeypatch) -> None:
    monkeypatch.setattr(
        transits,
        "build_transit_calendar_public",
        lambda **_: {
            "calendar_internal": {
                "days": [
                    {
                        "date": "2026-03-10",
                        "labels": ["mind"],
                        "top_event_ids": ["evt_context"],
                        "event_count": 2,
                        "signals_count": 3,
                        "is_critical": False,
                    }
                ]
            }
        },
    )
    monkeypatch.setattr(
        transits,
        "_build_narrative_public_payload",
        lambda _request, _start_date, selected_day_context=None: {
            "period_core": {"title": "Home core"},
            "daily_event_cards": [
                {
                    "event_id": "evt_daily",
                    "felt_line_tr": "Bugün bir konu netleşiyor.",
                    "why_it_feels_this_way_tr": "Zihin ve yakın çevre alanı aktif.",
                }
            ],
            "period_event_cards": [],
            "daily_selection": {"daily_count": 1, "period_count": 0},
            "event_cards": [{"event_id": "evt_daily"}],
            "period_peak_timeline": [],
            "timeline": {"summary": "line"},
        },
    )

    response = transits.build_transit_narrative(
        _request(
            selected_date="not-a-date",
            response_mode="public_only",
            payload_profile="home",
            start="2026-03-10",
            end="2026-03-10",
            debug=True,
        )
    )

    assert response["calendar"]["days"][0]["date"] == "2026-03-10"
    assert response["debug"]["selected_day_public"]["date"] == "2026-03-10"


def test_transit_narrative_calendar_period_profile_skips_block_assembly(monkeypatch) -> None:
    monkeypatch.setattr(
        transits,
        "build_transit_calendar_public",
        lambda **_: {"calendar_internal": {"days": [{"date": "2026-03-10", "rating": 2, "heat": 1, "event_count": 1}]}}
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
    monkeypatch.setattr(
        transits,
        "assemble_blocks",
        lambda **_: pytest.fail("calendar_period should skip block assembly"),
    )
    monkeypatch.setattr(
        transits,
        "_build_narrative_public_payload",
        lambda _request, _start_date, selected_day_context=None: {
            "period_core": {"title": "Core"},
            "event_cards": [],
            "daily_event_cards": [],
            "period_event_cards": [{"event_id": "evt_1"}],
            "daily_selection": {},
            "period_peak_timeline": [{"event_id": "evt_1"}],
            "timeline": {"summary": "line"},
        },
    )

    response = transits.build_transit_narrative(
        _request(
            selected_date="2026-03-10",
            payload_profile="calendar_period",
            include_best_times=False,
        )
    )

    assert "blocks" not in response
    assert "screens" not in response
    assert response["public"]["period_event_cards"] == [{"event_id": "evt_1"}]


def test_shape_public_payload_limits_calendar_period_to_visible_window_for_free() -> None:
    shaped = transits._shape_public_payload(
        {
            "event_cards": [
                {
                    "event_id": "evt_in",
                    "horizon": "period",
                    "timing": {
                        "entry_date_utc": "2026-03-10T09:00:00+00:00",
                        "exit_date_utc": "2026-03-13T09:00:00+00:00",
                    },
                },
                {
                    "event_id": "evt_out",
                    "horizon": "period",
                    "timing": {
                        "entry_date_utc": "2026-03-24T09:00:00+00:00",
                        "exit_date_utc": "2026-03-28T09:00:00+00:00",
                    },
                },
            ],
            "period_event_cards": [
                {
                    "event_id": "evt_in",
                    "timing": {
                        "entry_date_utc": "2026-03-10T09:00:00+00:00",
                        "exit_date_utc": "2026-03-13T09:00:00+00:00",
                    },
                },
                {
                    "event_id": "evt_out",
                    "timing": {
                        "entry_date_utc": "2026-03-24T09:00:00+00:00",
                        "exit_date_utc": "2026-03-28T09:00:00+00:00",
                    },
                },
            ],
            "period_peak_timeline": [
                {"event_id": "evt_in", "peak_date_utc": "2026-03-12T09:00:00+00:00"},
                {"event_id": "evt_out", "peak_date_utc": "2026-03-26T09:00:00+00:00"},
            ],
        },
        payload_profile="calendar_period",
        subscription_tier="free",
        visible_days_limit=7,
        anchor_date=transits.date_type.fromisoformat("2026-03-10"),
    )

    assert [card["event_id"] for card in shaped["period_event_cards"]] == ["evt_in"]
    assert [item["event_id"] for item in shaped["period_peak_timeline"]] == ["evt_in"]
    assert [card["event_id"] for card in shaped["event_cards"]] == ["evt_in"]


def test_transit_calendar_limits_public_days_for_free_window(monkeypatch) -> None:
    monkeypatch.setattr(
        transits,
        "build_transit_calendar_public",
        lambda **_: {
            "calendar_internal": {"days": []},
            "calendar_public": {
                "range": {"start": "2026-03-01", "end": "2026-03-31", "tz": "Europe/Istanbul"},
                "year_summary": {},
                "days": [
                    {"date": f"2026-03-{day:02d}", "rating": 1, "status": "ok", "labels": [], "note": ""}
                    for day in range(10, 20)
                ],
            },
        },
    )

    response = transits.build_transit_calendar(
        birth_date="1996-12-28",
        birth_time="07:10",
        birth_place="Istanbul, TR",
        start="2026-03-01",
        end="2026-03-31",
        tz="Europe/Istanbul",
        view="public",
        anchor_date=transits.date_type.fromisoformat("2026-03-10"),
        visible_days_limit=7,
        subscription_tier="free",
    )

    assert [day["date"] for day in response["days"]] == [
        "2026-03-10",
        "2026-03-11",
        "2026-03-12",
        "2026-03-13",
        "2026-03-14",
        "2026-03-15",
        "2026-03-16",
    ]
