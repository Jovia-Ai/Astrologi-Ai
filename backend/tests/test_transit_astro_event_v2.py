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


# --- PR7: stack boost tests ---


def _stack_event(
    *,
    event_id: str,
    subtype: str,
    source_bodies,
    significance: float,
    family: str = "aspect_event",
    exact_at: str = "2026-03-04T10:00:00+03:00",
    target_points=None,
) -> event_v2.AstroEventV2:
    return event_v2.AstroEventV2(
        event_id=event_id,
        event_family=family,
        event_subtype=subtype,
        audience="personal",
        event_kind="transit",
        importance_tier="standard",
        planet_class="social",
        time_scale="daily",
        significance_score=significance,
        lasting_change_score=0.0,
        chapter_opening=False,
        repeat_pass_count=1,
        is_structural=False,
        recognition_intensity="medium",
        precision_signal=0.5,
        planet_class_weight=0.5,
        target_importance=0.5,
        event_family_weight=0.46,
        duration_weight=0.5,
        repeat_pass_weight=0.5,
        structural_significance=0.5,
        angle_luminary_weight=0.0,
        solar_resonance=0.0,
        collective_interest_score=0.0,
        exact_at=[exact_at],
        source_bodies=list(source_bodies),
        target_points=list(target_points or []),
    )


def test_stack_boost_low_size2_homogeneous_applies_size_bonus_only() -> None:
    """2 soft events, same body, no outer planet → only size-2 bonus (1.06)."""
    events = [
        _stack_event(event_id="e1", subtype="trine", source_bodies=["Venus"], significance=0.48),
        _stack_event(event_id="e2", subtype="sextile", source_bodies=["Venus"], significance=0.44),
    ]
    meta = event_v2._apply_stack_boost(events, "Europe/Istanbul")
    assert len(meta) == 2
    for m in meta.values():
        assert m["size"] == 2
        assert m["flags"] == []  # no polarity_mix (both soft), no diversity (1 body), no outer
        assert abs(m["boost"] - 1.06) < 1e-9
        assert m["capped"] is False
    # significance scaled in place
    assert abs(events[0].significance_score - 0.48 * 1.06) < 1e-6
    assert abs(events[1].significance_score - 0.44 * 1.06) < 1e-6


def test_stack_boost_mid_size3_mixed_polarity_triggers_modifiers() -> None:
    """3 events, hard+soft mix, 3 distinct bodies, no outer → 1.20 (caps)."""
    events = [
        _stack_event(event_id="e1", subtype="square", source_bodies=["Sun"], significance=0.52),
        _stack_event(event_id="e2", subtype="trine", source_bodies=["Venus"], significance=0.61),
        _stack_event(event_id="e3", subtype="sextile", source_bodies=["Mars"], significance=0.47),
    ]
    meta = event_v2._apply_stack_boost(events, "Europe/Istanbul")
    assert len(meta) == 3
    m = next(iter(meta.values()))
    assert m["size"] == 3
    assert "polarity_mix" in m["flags"]
    assert "planet_diversity" in m["flags"]
    assert "outer_present" not in m["flags"]
    # base 0.10 + polarity 0.05 + diversity 0.05 = 0.20 → 1.20, exactly at cap
    assert abs(m["boost"] - 1.20) < 1e-9


def test_stack_boost_high_size4_all_modifiers_hits_cap() -> None:
    """4 events, all modifiers active → raw_bonus 0.28 but capped at 1.20."""
    events = [
        _stack_event(event_id="e1", subtype="conjunction", source_bodies=["Pluto"], significance=0.78),
        _stack_event(event_id="e2", subtype="square", source_bodies=["Mars"], significance=0.58),
        _stack_event(event_id="e3", subtype="trine", source_bodies=["Saturn"], significance=0.64),
        _stack_event(event_id="e4", subtype="sextile", source_bodies=["Mercury"], significance=0.45),
    ]
    meta = event_v2._apply_stack_boost(events, "Europe/Istanbul")
    assert len(meta) == 4
    m = next(iter(meta.values()))
    assert m["size"] == 4
    assert set(m["flags"]) == {"polarity_mix", "planet_diversity", "outer_present"}
    # raw_bonus = 0.13 + 0.05*3 = 0.28 → 1.28 capped at 1.20
    assert abs(m["raw_bonus"] - 0.28) < 1e-9
    assert abs(m["boost"] - 1.20) < 1e-9
    assert m["capped"] is True
    # Pluto event: 0.78 * 1.20 = 0.936
    assert abs(events[0].significance_score - 0.936) < 1e-6


def test_stack_boost_below_threshold_events_excluded_from_stack() -> None:
    """Events with significance < 0.42 don't participate in stack eligibility."""
    events = [
        _stack_event(event_id="e1", subtype="square", source_bodies=["Sun"], significance=0.55),
        _stack_event(event_id="e2", subtype="trine", source_bodies=["Venus"], significance=0.30),  # weak
    ]
    meta = event_v2._apply_stack_boost(events, "Europe/Istanbul")
    # Only 1 eligible → no stack
    assert meta == {}
    assert events[0].significance_score == 0.55  # unchanged
    assert events[1].significance_score == 0.30  # unchanged


def test_stack_boost_different_days_do_not_stack() -> None:
    """Events on different natal-local days are separate — no cross-day stack."""
    events = [
        _stack_event(event_id="e1", subtype="square", source_bodies=["Sun"], significance=0.55,
                     exact_at="2026-03-04T10:00:00+03:00"),
        _stack_event(event_id="e2", subtype="trine", source_bodies=["Venus"], significance=0.60,
                     exact_at="2026-03-05T10:00:00+03:00"),
    ]
    meta = event_v2._apply_stack_boost(events, "Europe/Istanbul")
    assert meta == {}


def test_stack_boost_respects_natal_timezone_day_boundary() -> None:
    """Two events with UTC times that fall on the same natal-local day stack,
    even if they span a UTC date boundary."""
    # 2026-03-04 22:30 Europe/Istanbul = 2026-03-04 19:30 UTC
    # 2026-03-05 00:30 Europe/Istanbul = 2026-03-04 21:30 UTC
    # Both are 2026-03-04 in Istanbul local, 2026-03-04 in UTC. Use clearer case:
    # 2026-03-05 02:00 Europe/Istanbul = 2026-03-04 23:00 UTC
    # 2026-03-05 10:00 Europe/Istanbul = 2026-03-05 07:00 UTC
    # In UTC these are different days; in Istanbul local both are 2026-03-05.
    events = [
        _stack_event(event_id="e1", subtype="square", source_bodies=["Sun"], significance=0.55,
                     exact_at="2026-03-04T23:00:00+00:00"),
        _stack_event(event_id="e2", subtype="trine", source_bodies=["Venus"], significance=0.60,
                     exact_at="2026-03-05T07:00:00+00:00"),
    ]
    meta = event_v2._apply_stack_boost(events, "Europe/Istanbul")
    # Both events land on 2026-03-05 local → should stack
    assert len(meta) == 2
    for m in meta.values():
        assert m["day"] == "2026-03-05"


def test_stack_boost_disabled_is_no_op() -> None:
    events = [
        _stack_event(event_id="e1", subtype="square", source_bodies=["Sun"], significance=0.55),
        _stack_event(event_id="e2", subtype="trine", source_bodies=["Venus"], significance=0.60),
    ]
    meta = event_v2._apply_stack_boost(events, "Europe/Istanbul", enabled=False)
    assert meta == {}
    assert events[0].significance_score == 0.55
    assert events[1].significance_score == 0.60


# --- PR7.1: axis-shadow collapse ---


def test_stack_axis_collapse_asc_dsc_pair_alone_does_not_stack() -> None:
    """Neptune-square-ASC + Neptune-square-DSC = one astrological contact.
    Without a third distinct event, no stack forms."""
    events = [
        _stack_event(event_id="e1", subtype="square", source_bodies=["Neptune"],
                     significance=0.90, target_points=["ASC"]),
        _stack_event(event_id="e2", subtype="square", source_bodies=["Neptune"],
                     significance=0.90, target_points=["DSC"]),
    ]
    meta = event_v2._apply_stack_boost(events, "Europe/Istanbul")
    assert meta == {}
    # neither event gets boosted
    assert events[0].significance_score == 0.90
    assert events[1].significance_score == 0.90


def test_stack_axis_collapse_asc_dsc_plus_third_event_stacks_as_size2() -> None:
    """Axis pair + one distinct event = genuine 2-event stack after collapse.
    All three raw events get the size=2 boost consistently."""
    events = [
        _stack_event(event_id="e1", subtype="square", source_bodies=["Neptune"],
                     significance=0.90, target_points=["ASC"]),
        _stack_event(event_id="e2", subtype="square", source_bodies=["Neptune"],
                     significance=0.90, target_points=["DSC"]),
        _stack_event(event_id="e3", subtype="trine", source_bodies=["Venus"],
                     significance=0.55, target_points=["Moon"]),
    ]
    meta = event_v2._apply_stack_boost(events, "Europe/Istanbul")
    assert len(meta) == 3  # all three raw events get stack_meta
    m = next(iter(meta.values()))
    assert m["size"] == 2  # collapsed size, not raw 3
    assert m["raw_count"] == 3
    # Neptune is outer + axis contact — outer_present fires; no polarity mix
    # (all square/trine is one hard + one soft = mix actually)
    assert "outer_present" in m["flags"]
    # size 2 bonus (0.06) + outer (0.05) + polarity_mix (0.05) = 0.16 → 1.16
    assert abs(m["boost"] - 1.16) < 1e-9
    # All three events boosted by the same multiplier
    for e, initial in zip(events, [0.90, 0.90, 0.55]):
        assert abs(e.significance_score - initial * 1.16) < 1e-6


def test_stack_axis_collapse_mc_ic_pair_alone_does_not_stack() -> None:
    events = [
        _stack_event(event_id="e1", subtype="trine", source_bodies=["Mercury"],
                     significance=0.70, target_points=["IC"]),
        _stack_event(event_id="e2", subtype="sextile", source_bodies=["Mercury"],
                     significance=0.70, target_points=["MC"]),
    ]
    meta = event_v2._apply_stack_boost(events, "Europe/Istanbul")
    assert meta == {}


def test_stack_axis_collapse_node_axis_pair_alone_does_not_stack() -> None:
    events = [
        _stack_event(event_id="e1", subtype="conjunction", source_bodies=["Chiron"],
                     significance=0.72, target_points=["South Node"]),
        _stack_event(event_id="e2", subtype="opposition", source_bodies=["Chiron"],
                     significance=0.72, target_points=["North Node"]),
    ]
    meta = event_v2._apply_stack_boost(events, "Europe/Istanbul")
    assert meta == {}


def test_stack_axis_collapse_different_transit_bodies_do_not_collapse() -> None:
    """Mars-square-ASC and Neptune-square-DSC share targets on the ASC/DSC
    axis but have different transit bodies — two genuine events, not one."""
    events = [
        _stack_event(event_id="e1", subtype="square", source_bodies=["Mars"],
                     significance=0.70, target_points=["ASC"]),
        _stack_event(event_id="e2", subtype="square", source_bodies=["Neptune"],
                     significance=0.70, target_points=["DSC"]),
    ]
    meta = event_v2._apply_stack_boost(events, "Europe/Istanbul")
    assert len(meta) == 2
    m = next(iter(meta.values()))
    assert m["size"] == 2
    assert m["raw_count"] == 2  # no collapse happened


def test_stack_axis_collapse_preserves_non_axis_targets() -> None:
    """Targets that aren't axis partners shouldn't be collapsed even if they
    happen to be opposite in the natal (that's a candidate for PR7.1b, not
    covered here)."""
    events = [
        _stack_event(event_id="e1", subtype="conjunction", source_bodies=["Mars"],
                     significance=0.60, target_points=["Venus"]),
        _stack_event(event_id="e2", subtype="opposition", source_bodies=["Mars"],
                     significance=0.60, target_points=["Saturn"]),
    ]
    meta = event_v2._apply_stack_boost(events, "Europe/Istanbul")
    # Venus and Saturn are not in the hardcoded axis pair list, so no collapse.
    # Natural 2-event stack forms.
    assert len(meta) == 2
    m = next(iter(meta.values()))
    assert m["size"] == 2
    assert m["raw_count"] == 2


def test_stack_axis_collapse_source_side_node_pair_alone_does_not_stack() -> None:
    """PR7.1a: NN-conj-Neptune + SN-opp-Neptune = one nodal axis contact on
    Neptune. Alone (no third event), no stack forms."""
    events = [
        _stack_event(event_id="e1", subtype="conjunction", source_bodies=["North Node"],
                     significance=0.78, target_points=["Neptune"]),
        _stack_event(event_id="e2", subtype="opposition", source_bodies=["South Node"],
                     significance=0.78, target_points=["Neptune"]),
    ]
    meta = event_v2._apply_stack_boost(events, "Europe/Istanbul")
    assert meta == {}
    assert events[0].significance_score == 0.78
    assert events[1].significance_score == 0.78


def test_stack_axis_collapse_source_side_node_pair_with_third_event_stacks() -> None:
    """Source-side node shadow + one distinct event = genuine size=2 stack."""
    events = [
        _stack_event(event_id="e1", subtype="conjunction", source_bodies=["North Node"],
                     significance=0.78, target_points=["Neptune"]),
        _stack_event(event_id="e2", subtype="opposition", source_bodies=["South Node"],
                     significance=0.78, target_points=["Neptune"]),
        _stack_event(event_id="e3", subtype="trine", source_bodies=["Mars"],
                     significance=0.55, target_points=["Venus"]),
    ]
    meta = event_v2._apply_stack_boost(events, "Europe/Istanbul")
    assert len(meta) == 3
    m = next(iter(meta.values()))
    assert m["size"] == 2  # collapsed
    assert m["raw_count"] == 3  # pre-collapse
    # All three events get the same boost
    for e, initial in zip(events, [0.78, 0.78, 0.55]):
        assert abs(e.significance_score - initial * m["boost"]) < 1e-6


def test_stack_axis_collapse_source_side_node_ingress_pair_collapses() -> None:
    """PR7.1a: nodal ingress pair (NN house_3 ingress + SN house_9 ingress)
    represents one nodal shift. Collapsed even though target_points is empty
    for both, because (empty == empty) satisfies the target-set equality."""
    events = [
        _stack_event(event_id="e1", subtype="north node.house_3",
                     source_bodies=["North Node"], significance=0.81,
                     family="house_ingress_event", target_points=[]),
        _stack_event(event_id="e2", subtype="south node.house_9",
                     source_bodies=["South Node"], significance=0.81,
                     family="house_ingress_event", target_points=[]),
    ]
    meta = event_v2._apply_stack_boost(events, "Europe/Istanbul")
    # No third event → collapsed to size=1 → no stack
    assert meta == {}
    # But the collapse itself worked: add a third event to prove
    events.append(
        _stack_event(event_id="e3", subtype="trine", source_bodies=["Mars"],
                     significance=0.55, target_points=["Venus"])
    )
    meta = event_v2._apply_stack_boost(events, "Europe/Istanbul")
    m = next(iter(meta.values()))
    assert m["size"] == 2  # NN+SN ingress pair collapsed into 1 group
    assert m["raw_count"] == 3


def test_stack_narrative_gate_size3_capped_passes() -> None:
    """PR7c: size>=3 AND capped==True is the only passing combination."""
    assert event_v2._stack_narrative_passes_gate(
        {"size": 3, "boost": 1.20, "capped": True}
    ) is True


def test_stack_narrative_gate_size3_not_capped_fails() -> None:
    """PR7c: size>=3 without cap is NOT enough — genuine density requires
    both count and maxed modifiers."""
    assert event_v2._stack_narrative_passes_gate(
        {"size": 3, "boost": 1.15, "capped": False}
    ) is False


def test_stack_narrative_gate_size4_capped_passes() -> None:
    assert event_v2._stack_narrative_passes_gate(
        {"size": 4, "boost": 1.20, "capped": True}
    ) is True


def test_stack_narrative_gate_size2_capped_fails() -> None:
    """A capped size=2 stack (e.g. 2 events with all 3 modifiers) still
    doesn't pass: PR7c requires size>=3 for genuine multi-event density."""
    assert event_v2._stack_narrative_passes_gate(
        {"size": 2, "boost": 1.20, "capped": True}
    ) is False


def test_stack_narrative_gate_empty_meta_fails() -> None:
    assert event_v2._stack_narrative_passes_gate(None) is False
    assert event_v2._stack_narrative_passes_gate({}) is False


def test_stack_narrative_fires_only_on_top_member_per_day() -> None:
    """Three gate-passing events on the same day → only the top-sig one
    gets the clause populated in stack_clause_tr. Others stay "".

    To reach the cap (required by PR7c gate) we need all 3 modifiers: hard
    (square) + soft (trine) gives polarity_mix, 3 distinct bodies gives
    diversity, and Saturn in source gives outer_present."""
    events = [
        _stack_event(event_id="e1", subtype="square", source_bodies=["Saturn"],
                     significance=0.52, target_points=["Moon"]),
        _stack_event(event_id="e2", subtype="trine", source_bodies=["Venus"],
                     significance=0.61, target_points=["Jupiter"]),
        _stack_event(event_id="e3", subtype="sextile", source_bodies=["Mars"],
                     significance=0.47, target_points=["MC"]),
    ]
    event_v2._apply_stack_boost(events, "Europe/Istanbul")
    applied = event_v2._apply_stack_narrative(events)
    assert len(applied) == 1  # exactly one event got the clause
    # Top-sig event after boost is e2 (0.61 * 1.20 = 0.732)
    assert "e2" in applied
    # why_now_tr is NEVER touched — empty (or whatever the builder set)
    for e in events:
        assert e.why_now_tr == ""
    # stack_clause_tr populated only on the top event
    assert events[0].stack_clause_tr == ""
    assert events[1].stack_clause_tr == event_v2.STACK_NARRATIVE_CLAUSE_TR
    assert events[2].stack_clause_tr == ""


def test_stack_narrative_does_not_touch_why_now_tr() -> None:
    """Even when the gate fires, why_now_tr remains exactly as the builder
    set it. The stack clause lives only in stack_clause_tr."""
    events = [
        _stack_event(event_id="e1", subtype="square", source_bodies=["Saturn"],
                     significance=0.52, target_points=["Moon"]),
        _stack_event(event_id="e2", subtype="trine", source_bodies=["Venus"],
                     significance=0.61, target_points=["Jupiter"]),
        _stack_event(event_id="e3", subtype="sextile", source_bodies=["Mars"],
                     significance=0.47, target_points=["MC"]),
    ]
    # Builder has pre-populated why_now_tr with real content (aspect +
    # PR9 solar resonance). The narrative apply must NOT append to it.
    events[1].why_now_tr = "Etki su anda zirveye; bu da Jupiter temasini one cikariyor."
    event_v2._apply_stack_boost(events, "Europe/Istanbul")
    event_v2._apply_stack_narrative(events)
    assert events[1].why_now_tr == (
        "Etki su anda zirveye; bu da Jupiter temasini one cikariyor."
    )
    assert events[1].stack_clause_tr == event_v2.STACK_NARRATIVE_CLAUSE_TR


def test_stack_narrative_idempotent_on_repeat_call() -> None:
    events = [
        _stack_event(event_id="e1", subtype="square", source_bodies=["Saturn"],
                     significance=0.52, target_points=["Moon"]),
        _stack_event(event_id="e2", subtype="trine", source_bodies=["Venus"],
                     significance=0.61, target_points=["Jupiter"]),
        _stack_event(event_id="e3", subtype="sextile", source_bodies=["Mars"],
                     significance=0.47, target_points=["MC"]),
    ]
    event_v2._apply_stack_boost(events, "Europe/Istanbul")
    event_v2._apply_stack_narrative(events)
    once_clause = events[1].stack_clause_tr
    once_why = events[1].why_now_tr
    event_v2._apply_stack_narrative(events)  # second call
    assert events[1].stack_clause_tr == once_clause  # no change
    assert events[1].why_now_tr == once_why


def test_stack_narrative_silent_when_boost_disabled() -> None:
    """No stack_meta → gate silent → stack_clause_tr empty on all events."""
    events = [
        _stack_event(event_id="e1", subtype="square", source_bodies=["Saturn"],
                     significance=0.52, target_points=["Moon"]),
        _stack_event(event_id="e2", subtype="trine", source_bodies=["Venus"],
                     significance=0.61, target_points=["Jupiter"]),
        _stack_event(event_id="e3", subtype="sextile", source_bodies=["Mars"],
                     significance=0.47, target_points=["MC"]),
    ]
    event_v2._apply_stack_boost(events, "Europe/Istanbul", enabled=False)
    applied = event_v2._apply_stack_narrative(events)
    assert applied == {}
    for e in events:
        assert e.stack_clause_tr == ""


def test_stack_narrative_silent_on_marginal_size2_stack() -> None:
    """Size=2 no-modifier stack (boost=1.06) must NOT fire the narrative."""
    events = [
        _stack_event(event_id="e1", subtype="trine", source_bodies=["Venus"],
                     significance=0.48, target_points=["Moon"]),
        _stack_event(event_id="e2", subtype="sextile", source_bodies=["Venus"],
                     significance=0.44, target_points=["Mars"]),
    ]
    event_v2._apply_stack_boost(events, "Europe/Istanbul")
    applied = event_v2._apply_stack_narrative(events)
    assert applied == {}
    for e in events:
        assert e.stack_clause_tr == ""


def test_stack_axis_collapse_source_side_different_targets_do_not_collapse() -> None:
    """NN-conj-Sun + SN-conj-Moon: source is axis pair but targets differ,
    so these are two genuine events."""
    events = [
        _stack_event(event_id="e1", subtype="conjunction", source_bodies=["North Node"],
                     significance=0.60, target_points=["Sun"]),
        _stack_event(event_id="e2", subtype="conjunction", source_bodies=["South Node"],
                     significance=0.60, target_points=["Moon"]),
    ]
    meta = event_v2._apply_stack_boost(events, "Europe/Istanbul")
    # Natural size=2 stack, no collapse
    assert len(meta) == 2
    m = next(iter(meta.values()))
    assert m["size"] == 2
    assert m["raw_count"] == 2


def test_stack_axis_collapse_five_raw_events_with_axis_shadow_becomes_size4() -> None:
    """Realistic stack: axis shadow (Mars MC/IC) + 3 distinct aspects."""
    events = [
        _stack_event(event_id="e1", subtype="opposition", source_bodies=["Mars"],
                     significance=0.76, target_points=["MC"]),
        _stack_event(event_id="e2", subtype="conjunction", source_bodies=["Mars"],
                     significance=0.76, target_points=["IC"]),
        _stack_event(event_id="e3", subtype="quincunx", source_bodies=["Sun"],
                     significance=0.72, target_points=["Mercury"]),
        _stack_event(event_id="e4", subtype="quincunx", source_bodies=["Mars"],
                     significance=0.70, target_points=["North Node"]),
        _stack_event(event_id="e5", subtype="trine", source_bodies=["Venus"],
                     significance=0.60, target_points=["Jupiter"]),
    ]
    meta = event_v2._apply_stack_boost(events, "Europe/Istanbul")
    assert len(meta) == 5  # all raw events receive stack_meta
    m = next(iter(meta.values()))
    # MC/IC pair collapses → 4 groups: (Mars-MC+Mars-IC), Sun-Mercury, Mars-NN, Venus-Jupiter
    assert m["size"] == 4
    assert m["raw_count"] == 5
