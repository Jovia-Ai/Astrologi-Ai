from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from app.api.routes import natal_interpretation as natal
from app.core.logging import configure_logging


def _request() -> natal.NatalInterpretationRequest:
    return natal.NatalInterpretationRequest(
        birth_date="1996-12-28",
        birth_time="07:10",
        birth_place="Istanbul, TR",
        locale="tr",
    )


def _configure_timing_log_env(monkeypatch, log_path: Path) -> None:
    monkeypatch.setenv("ENABLE_TIMING_LOGS", "true")
    monkeypatch.setenv("ENABLE_NATAL_STAGE_TIMINGS", "true")
    monkeypatch.setenv("ENABLE_NATAL_TIMING_FILE_SINK", "true")
    monkeypatch.setenv("NATAL_TIMING_LOG_PATH", str(log_path))
    configure_logging("INFO")


def _read_json_lines(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            raw = line.strip()
            if not raw:
                continue
            rows.append(json.loads(raw))
    return rows


def test_timing_file_sink_writes_valid_json(tmp_path, monkeypatch) -> None:
    log_path = tmp_path / "natal_timings.jsonl"
    _configure_timing_log_env(monkeypatch, log_path)

    natal._emit_timing_event(
        {
            "type": "natal_timing",
            "route": "/interpret",
            "request_id": "rid-smoke",
            "debug": False,
            "status": "ok",
            "duration_ms": 1.23,
            "timestamp": natal._utc_iso_timestamp(),
        }
    )

    rows = _read_json_lines(log_path)
    assert rows
    assert rows[0]["type"] == "natal_timing"


def test_interpret_routes_emit_timing_events(tmp_path, monkeypatch) -> None:
    log_path = tmp_path / "natal_timings.jsonl"
    _configure_timing_log_env(monkeypatch, log_path)

    def fake_prepare_payload(
        request,
        *,
        premium_mode: bool,
        debug_mode: bool = False,
        tone_enabled: bool = True,
        profile_engine: str | None = None,
        route: str | None = None,
        request_id: str | None = None,
    ):
        del request, premium_mode, tone_enabled, profile_engine
        resolved_request_id = natal._resolve_request_id(request_id)
        natal._log_natal_stage_timing(
            phase="prepare_payload",
            stage_breakdown_ms={
                "normalize_chart_inputs": 1.2,
                "rule_engine": 2.4,
            },
            compute_groups=["normalize_chart_inputs", "rule_engine"],
            route=route or "natal_internal",
            request_id=resolved_request_id,
            debug=debug_mode,
            chart_data={"birth_date": "1996-12-28", "birth_time": "07:10", "birth_place": "Istanbul, TR"},
        )
        return {"_stub": True}

    def fake_finalize_response(
        base_payload,
        *,
        premium_mode: bool,
        debug_mode: bool = False,
        output_profile: str = "user_compact",
        route: str | None = None,
        request_id: str | None = None,
    ):
        del base_payload, premium_mode, output_profile
        resolved_request_id = natal._resolve_request_id(request_id)
        natal._log_natal_stage_timing(
            phase="finalize_response",
            stage_breakdown_ms={
                "core_story_layers": 3.7,
                "finalize_payload": 0.8,
            },
            compute_groups=["core_story_layers", "finalize_payload"],
            route=route or "natal_internal",
            request_id=resolved_request_id,
            debug=debug_mode,
            chart_data={"birth_date": "1996-12-28", "birth_time": "07:10", "birth_place": "Istanbul, TR"},
        )
        return {
            "sections_v2": [{"id": "s1"}],
            "supporting_threads": [{"id": "t1"}],
            "core_story_ui": {"title": "stub"},
            "profile_narrative": {},
            "personality_imprint": {},
            "narrative_v2": {},
        }

    monkeypatch.setattr(natal, "_prepare_payload", fake_prepare_payload)
    monkeypatch.setattr(natal, "_finalize_response", fake_finalize_response)
    monkeypatch.setattr(
        natal,
        "_interpret_ui_cache_key",
        lambda *_args, **_kwargs: f"timing-test-{uuid4().hex}",
    )
    monkeypatch.setattr(
        natal,
        "build_public_natal_view",
        lambda response, locale, include_debug: {
            "sections_v2": response.get("sections_v2", []),
            "supporting_threads": response.get("supporting_threads", []),
            "core_story_ui": response.get("core_story_ui", {}),
            "profile_narrative": {},
            "personality_imprint": {},
            "narrative_v2": {},
            "locale": locale,
            "include_debug": include_debug,
        },
    )

    request = _request()
    natal.interpret_natal_chart(request, x_request_id="rid-interpret")
    natal.interpret_natal_chart_ui(request, x_request_id="rid-interpret-ui")

    rows = _read_json_lines(log_path)
    assert rows, "expected timing logs to be written to sink"

    def _assert_request_events(request_id: str, route: str) -> None:
        request_rows = [row for row in rows if row.get("request_id") == request_id]
        assert any(row.get("type") == "natal_timing" and row.get("route") == route for row in request_rows)
        stage_rows = [row for row in request_rows if row.get("type") == "natal_stage_timing"]
        assert len(stage_rows) >= 2
        for row in stage_rows:
            assert row.get("type")
            assert row.get("route")
            assert row.get("request_id")

    _assert_request_events("rid-interpret", "/interpret")
    _assert_request_events("rid-interpret-ui", "/interpret/ui")
