from __future__ import annotations

from datetime import date

from app.api.routes import transits
from app.transit import astro_event_v2 as event_v2
from app.transit.present.public_builder import build_public_response


def _natal_snapshot() -> dict:
    signs = [
        "Aries",
        "Taurus",
        "Gemini",
        "Cancer",
        "Leo",
        "Virgo",
        "Libra",
        "Scorpio",
        "Sagittarius",
        "Capricorn",
        "Aquarius",
        "Pisces",
    ]
    house_cusps = []
    for index, sign in enumerate(signs, start=1):
        house_cusps.append({"house": index, "lon": float((index - 1) * 30), "sign": sign})
    return {
        "bodies": [
            {"body": "Sun", "lon": 12.0, "sign": "Aries", "house": 1},
            {"body": "Venus", "lon": 183.0, "sign": "Libra", "house": 7},
            {"body": "Saturn", "lon": 95.0, "sign": "Cancer", "house": 4},
            {"body": "Pluto", "lon": 273.0, "sign": "Capricorn", "house": 10},
        ],
        "angles": {
            "ASC": {"point": "ASC", "lon": 0.0, "sign": "Aries"},
            "DSC": {"point": "DSC", "lon": 180.0, "sign": "Libra"},
            "MC": {"point": "MC", "lon": 270.0, "sign": "Capricorn"},
            "IC": {"point": "IC", "lon": 90.0, "sign": "Cancer"},
        },
        "house_cusps": house_cusps,
    }


def _legacy_item(
    *,
    event_id: str = "evt_pluto_asc",
    transit_body: str = "Pluto",
    natal_point: str = "ASC",
    bucket: str = "long",
) -> dict:
    return {
        "event_id": event_id,
        "transit_body": transit_body,
        "natal_point": natal_point,
        "aspect": "square",
        "phase": "applying",
        "bucket": bucket,
        "orb_deg": 0.2,
        "polarity": "hard",
        "strength": 0.94,
        "timing": {
            "entry_date_utc": "2026-03-01T00:00:00+00:00",
            "peak_date_utc": "2026-05-18T00:00:00+00:00",
            "exit_date_utc": "2026-11-01T00:00:00+00:00",
            "peaks": [
                {"t": "2026-05-18T00:00:00+00:00"},
                {"t": "2026-08-14T00:00:00+00:00"},
            ],
        },
        "houses": {"natal_point_house": 1, "transit_in_natal_house": 10},
        "signs": {"transit_body_sign": "Aquarius"},
        "source_pos": {"sign": "Aquarius", "deg": 3.0},
        "target_pos": {"sign": "Aries", "deg": 0.0},
        "ranking": {"tier": "main", "weight": 1.82},
        "interpretation": {
            "headline": "Kimlik hattinda yogun baski",
            "summary": "Kimlik ve yon duygusu daha derin bir donusumden geciyor.",
            "time_hint": "Zamana yayilan etki",
            "do": ["Merkezde neyin degistigini izle."],
            "watch": ["Kontrol tepkisi."],
        },
    }


def test_enrich_legacy_aspect_item_marks_deep_structural_events() -> None:
    enriched = event_v2.enrich_legacy_aspect_item(
        _legacy_item(),
        natal_snapshot=_natal_snapshot(),
        solar_year={
            "dominant_houses": [1, 10],
            "solar_sun_house": 1,
            "year_ruler": "Mars",
        },
    )

    assert enriched["event_family"] == "aspect_event"
    assert enriched["event_kind"] == "transformation"
    assert enriched["importance_tier"] in {"high", "critical"}
    assert enriched["recognition_intensity"] == "high"
    assert enriched["is_structural"] is True
    assert enriched["chapter_opening"] is True
    assert enriched["importance_label_tr"] == "Derin donusum"


def test_detect_cycle_events_promotes_saturn_return_to_chapter() -> None:
    events = event_v2.detect_cycle_events(
        [
            {
                "id": "win_saturn_return",
                "transit": "Saturn",
                "natal": "Saturn",
                "aspect": "conjunction",
                "duration_days": 420,
                "orb": {"min": 0.12},
                "timebox": {
                    "enter": "2026-01-14T00:00:00+00:00",
                    "exit": "2027-03-01T00:00:00+00:00",
                    "peaks": [
                        {"t": "2026-05-10T00:00:00+00:00"},
                        {"t": "2026-11-22T00:00:00+00:00"},
                    ],
                },
            }
        ],
        natal_snapshot=_natal_snapshot(),
        solar_year={"dominant_houses": [4], "solar_sun_house": 4, "year_ruler": "Saturn"},
    )

    assert len(events) == 1
    event = events[0]
    assert event.event_family == "cycle_event"
    assert event.event_subtype == "saturn_return"
    assert event.event_kind == "chapter"
    assert event.repeat_pass_count == 2
    assert event.is_structural is True
    assert event.importance_tier in {"high", "critical"}


def test_detect_house_ingress_events_tracks_initial_and_final_pass(monkeypatch) -> None:
    daily_longitudes = {
        "2026-03-01": 15.0,
        "2026-03-02": 45.0,
        "2026-03-03": 15.0,
        "2026-03-04": 45.0,
        "2026-03-05": 45.0,
    }

    def _fake_positions_for_bodies(*, bodies, when_iso, place, hour=None):
        day = str(when_iso)[:10]
        out = []
        if "Saturn" in bodies:
            out.append({"body": "Saturn", "lon": daily_longitudes[day]})
        return out

    monkeypatch.setattr(event_v2, "_positions_for_bodies", _fake_positions_for_bodies)

    events = event_v2.detect_house_ingress_events(
        natal_snapshot=_natal_snapshot(),
        transit_place="Istanbul, TR",
        start_date="2026-03-01",
        end_date="2026-03-05",
        transit_date="2026-03-03",
        solar_year={"dominant_houses": [2], "solar_sun_house": 2, "year_ruler": "Venus"},
    )

    saturn_second_house = [
        entry
        for entry in events
        if entry.source_bodies == ["Saturn"] and entry.target_houses == [2]
    ]

    assert len(saturn_second_house) == 2
    assert {entry.current_phase for entry in saturn_second_house} == {"initial_entry", "final_settlement"}
    assert all(entry.event_family == "house_ingress_event" for entry in saturn_second_house)
    assert all(entry.event_kind == "chapter" for entry in saturn_second_house)
    assert all(entry.repeat_pass_count == 2 for entry in saturn_second_house)


def test_build_transits_engine_response_attaches_multi_event_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        transits,
        "build_transit_report",
        lambda **_: {
            "locale": "tr",
            "transit_date": "2026-03-10",
            "natal": _natal_snapshot(),
            "display": {"items": []},
            "request_echo": {
                "birth_date": "1996-12-28",
                "birth_time": "07:10",
                "birth_place": "Istanbul, TR",
            },
        },
    )
    monkeypatch.setattr(transits, "build_transit_window_report", lambda **_: {"events": []})
    monkeypatch.setattr(
        transits,
        "build_solar_year_theme",
        lambda **_: {"event_id": "solar_2026", "event_family": "solar_year_theme", "dominant_houses": [1]},
    )
    monkeypatch.setattr(
        transits,
        "build_personal_multi_event_payload",
        lambda **_: {
            "schema_version": "astro_event.v2",
            "personal_transit_rail": [],
            "structural_chapter_rail": [{"event_id": "chapter_1"}],
            "solar_year_frame": {"event_id": "solar_2026"},
            "events_by_id": {},
        },
    )

    response = transits._build_transits_engine_response(
        transits.TransitRequest(
            birth_date="1996-12-28",
            birth_time="07:10",
            birth_place="Istanbul, TR",
            transit_date="2026-03-10",
            transit_place="Istanbul, TR",
        )
    )

    assert response["solar_year_frame"]["event_id"] == "solar_2026"
    assert response["event_engine_v2"]["schema_version"] == "astro_event.v2"
    assert response["event_engine_v2"]["structural_chapter_rail"][0]["event_id"] == "chapter_1"


def test_narrative_public_payload_keeps_multi_event_projection(monkeypatch) -> None:
    monkeypatch.setattr(
        transits,
        "_build_transits_engine_response",
        lambda _request: {
            "display": {"items": []},
            "natal": _natal_snapshot(),
        },
    )
    monkeypatch.setattr(
        transits,
        "build_public_response",
        lambda _response: {
            "period_core": {"title": "Core"},
            "event_cards": [],
            "period_peak_timeline": [],
            "timeline": {},
            "multi_event": {"schema_version": "astro_event.v2"},
            "personal_transit_rail": [{"event_id": "evt_1"}],
            "structural_chapter_rail": [{"event_id": "chapter_1"}],
            "solar_year_frame": {"event_id": "solar_2026"},
        },
    )
    monkeypatch.setattr(transits, "select_event_ids", lambda *_args, **_kwargs: ([], {"selected_ids": []}))
    monkeypatch.setattr(transits, "build_period_coverage", lambda *_args, **_kwargs: {"counts": {"total": 0}})

    payload = transits._build_narrative_public_payload(
        transits.TransitNarrativeRequest(
            birth_date="1996-12-28",
            birth_time="07:10",
            birth_place="Istanbul, TR",
            start="2026-03-01",
            end="2026-03-31",
            tz="Europe/Istanbul",
            transit_place="Istanbul, TR",
            include_best_times=False,
        ),
        date(2026, 3, 1),
    )

    assert payload["multi_event"]["schema_version"] == "astro_event.v2"
    assert payload["personal_transit_rail"][0]["event_id"] == "evt_1"
    assert payload["structural_chapter_rail"][0]["event_id"] == "chapter_1"
    assert payload["solar_year_frame"]["event_id"] == "solar_2026"


def test_public_response_exposes_multi_event_payload_and_card_metadata() -> None:
    response = {
        "locale": "tr",
        "transit_date": "2026-03-10",
        "metrics": {"pressure_index": 0.64, "support_index": 0.52},
        "presentable": {"summary": {"main_theme": "identity", "one_liner": "Donem temasi"}},
        "natal": _natal_snapshot(),
        "display": {"items": [_legacy_item()]},
        "event_engine_v2": {
            "schema_version": "astro_event.v2",
            "personal_transit_rail": [{"event_id": "evt_pluto_asc"}],
            "structural_chapter_rail": [{"event_id": "chapter_1"}],
            "solar_year_frame": {"event_id": "solar_2026"},
            "events_by_id": {
                "evt_pluto_asc": {
                    "event_id": "evt_pluto_asc",
                    "event_family": "aspect_event",
                    "event_subtype": "square",
                    "audience": "personal",
                    "event_kind": "transformation",
                    "importance_tier": "critical",
                    "planet_class": "outer",
                    "time_scale": "months",
                    "significance_score": 0.92,
                    "lasting_change_score": 0.88,
                    "chapter_opening": True,
                    "repeat_pass_count": 2,
                    "is_structural": True,
                    "recognition_intensity": "high",
                    "importance_label_tr": "Derin donusum",
                    "copy_mode": "transformation",
                    "title_tr": "Pluton ASC hattini calistiriyor",
                }
            },
        },
        "solar_year_frame": {"event_id": "solar_2026"},
    }

    public = build_public_response(response)

    assert public["multi_event"]["schema_version"] == "astro_event.v2"
    assert public["structural_chapter_rail"][0]["event_id"] == "chapter_1"
    assert public["solar_year_frame"]["event_id"] == "solar_2026"
    assert public["event_cards"]
    assert public["event_cards"][0]["event_kind"] == "transformation"
    assert public["event_cards"][0]["astro_event"]["event_id"] == "evt_pluto_asc"
