import json
import logging

from app.api.routes import transits


def _transit_request(**kwargs):
    base = {
        "birth_date": "1996-12-28",
        "birth_time": "07:10",
        "birth_place": "Istanbul, TR",
        "transit_date": "2026-03-10",
        "transit_place": "Istanbul, TR",
    }
    base.update(kwargs)
    return transits.TransitRequest(**base)


def _calendar_payload():
    return {
        "calendar_internal": {"days": []},
        "calendar_public": {
            "range": {
                "start": "2026-03-01",
                "end": "2026-03-31",
                "tz": "Europe/Istanbul",
            },
            "days": [],
        },
    }


def test_transits_response_includes_meta_snapshot_id(monkeypatch) -> None:
    monkeypatch.setattr(
        transits,
        "_build_transits_engine_response",
        lambda _request: {"transit_date": _request.transit_date},
    )
    monkeypatch.setattr(
        transits,
        "build_public_response",
        lambda _response: {"period_core": {}, "event_cards": [], "timeline": {}},
    )

    response = transits.build_transits(_transit_request())

    assert response["meta"]["snapshot_id"].startswith("trsnap_")
    assert response["meta"]["source_meta"]["endpoint"] == "/transits"
    assert response["meta"]["source_meta"]["route_version"] == "v1"
    assert response["meta"]["source_meta"]["observability_stage"] == "phase0_pr1"


def test_transits_meta_merge_preserves_existing_keys(monkeypatch) -> None:
    monkeypatch.setattr(
        transits,
        "_build_transits_engine_response",
        lambda _request: {"transit_date": _request.transit_date},
    )
    monkeypatch.setattr(
        transits,
        "build_public_response",
        lambda _response: {
            "meta": {
                "snapshot_id": "existing_snapshot",
                "source_meta": {"endpoint": "existing_endpoint", "existing": "keep"},
            },
            "period_core": {},
            "event_cards": [],
            "timeline": {},
        },
    )

    response = transits.build_transits(_transit_request())

    assert response["meta"]["snapshot_id"] == "existing_snapshot"
    assert response["meta"]["source_meta"]["endpoint"] == "existing_endpoint"
    assert response["meta"]["source_meta"]["existing"] == "keep"
    assert response["meta"]["source_meta"]["route_version"] == "v1"
    assert response["meta"]["source_meta"]["observability_stage"] == "phase0_pr1"


def test_transit_calendar_response_includes_meta_snapshot_id(monkeypatch) -> None:
    monkeypatch.setattr(transits, "build_transit_calendar_public", lambda **_: _calendar_payload())

    response = transits.build_transit_calendar(
        birth_date="1996-12-28",
        birth_time="07:10",
        birth_place="Istanbul, TR",
        start="2026-03-01",
        end="2026-03-31",
        tz="Europe/Istanbul",
    )

    assert response["meta"]["snapshot_id"].startswith("trsnap_")
    assert response["meta"]["source_meta"]["endpoint"] == "/transit/calendar"


def test_best_times_response_includes_meta_snapshot_id(monkeypatch) -> None:
    monkeypatch.setattr(transits, "build_transit_calendar_public", lambda **_: _calendar_payload())
    monkeypatch.setattr(
        transits,
        "best_times_from_calendar_payload",
        lambda **_: {"candidates": [], "windows": []},
    )

    response = transits.transit_calendar_best_times(
        birth_date="1996-12-28",
        birth_time="07:10",
        birth_place="Istanbul, TR",
        start="2026-03-01",
        end="2026-03-31",
        tz="Europe/Istanbul",
        intent="beauty_care_nourish",
    )

    assert response["meta"]["snapshot_id"].startswith("trsnap_")
    assert response["meta"]["source_meta"]["endpoint"] == "/transit/calendar/best-times"


def test_transits_trace_log_includes_header_context(monkeypatch, caplog) -> None:
    monkeypatch.setenv("ENABLE_TIMING_LOGS", "true")
    monkeypatch.setattr(
        transits,
        "_build_transits_engine_response",
        lambda _request: {"transit_date": _request.transit_date},
    )
    monkeypatch.setattr(
        transits,
        "build_public_response",
        lambda _response: {"period_core": {}, "event_cards": [], "timeline": {}},
    )
    caplog.set_level(logging.INFO, logger=transits.logger.name)

    response = transits.build_transits(
        _transit_request(),
        client_trace_id="cli_trace_123",
        client_surface="timing_test_surface",
    )

    record = next(
        entry
        for entry in caplog.records
        if entry.name == transits.logger.name
        and entry.message.startswith("transit_trace ")
    )
    payload = json.loads(record.message[len("transit_trace ") :])

    assert payload["endpoint"] == "/transits"
    assert payload["snapshot_id"] == response["meta"]["snapshot_id"]
    assert payload["client_trace_id"] == "cli_trace_123"
    assert payload["client_surface"] == "timing_test_surface"
    assert payload["observability_stage"] == "phase0_pr1"
