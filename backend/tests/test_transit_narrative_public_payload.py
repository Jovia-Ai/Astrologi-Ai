import pytest

from app.api.routes import transits
from app.astro_os.natal.contracts import CanonicalNatalStateV1
from app.core.config import settings
from app.services.performance.cache_store import InMemoryCacheStore
import re


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
    monkeypatch.setattr(transits, "_build_transits_engine_response", lambda _request, **_kwargs: {})
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
    assert response["public"]["daily_synthesis"]["headline"]
    assert response["public"]["daily_synthesis"]["body"]
    assert response["public"]["daily_synthesis"]["guidance"]
    assert response["public"]["daily_synthesis"]["sources"]["daily"] == ["evt_1"]
    assert response["public"]["daily_synthesis"]["sources"]["trace"]["event_id"] == "evt_1"
    assert response["public"]["daily_synthesis"]["primary_signal"]["event_id"] == "evt_1"
    assert response["public"]["daily_synthesis"]["planner_debug"]["mode_resolution"]["mode"]
    assert response["public"]["period_event_cards"] == []
    assert response["calendar"]["days"][0]["signal_label_tr"] == "Yüksek tempo."
    assert response["calendar"]["days"][0]["tone_label_tr"] == "yuksek_tempo"
    assert response["calendar"]["days"][0]["micro_summary_tr"] == card["felt_line_tr"]


def test_transit_narrative_uses_period_fallback_when_daily_missing(monkeypatch) -> None:
    monkeypatch.setattr(transits, "_build_transits_engine_response", lambda _request, **_kwargs: {})
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
    monkeypatch.setattr(transits, "_build_transits_engine_response", lambda _request, **_kwargs: {})
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


def test_live_route_like_period_reading_v1_keeps_non_lifechapter_density() -> None:
    generic_stub = (
        "Bu dönem dikkatini tek bir hatta topluyor.\n\n"
        "Küçük görünen anlar alttaki daha büyük meseleyi görünür kılıyor.\n\n"
        "Bunu daha sahipli bir çizgiye yerleştiriyorsun."
    )
    outputs: dict[str, str] = {}

    for target_date in ("2026-03-04", "2026-04-22"):
        payload = transits.build_transit_narrative(
            _request(
                start=target_date,
                end=target_date,
                selected_date=target_date,
                include_best_times=False,
                locale="tr",
            )
        )
        period_core = payload["public"]["period_core"]
        reading = period_core["period_reading_v1"]["full_text"]
        outputs[target_date] = reading
        lowered = reading.lower()

        assert reading != generic_stub
        assert len(reading) >= 350
        assert 3 <= len(period_core["period_reading_v1"]["blocks"]) <= 4
        assert period_core["_period_story_debug"]["composer_mode"] == "semantic_focus_guided"
        expected_semantic_mode = "guided" if target_date == "2026-03-04" else "guided_fallback"
        assert period_core["_period_story_debug"]["composer_plan"]["semantic_mode"] == expected_semantic_mode
        assert "bu tema daha çok" not in lowered
        assert "asıl ayrım" not in lowered
        assert "söz istiyor" not in lowered
        assert not re.search(r"\bsende\b.+\bkuruyor\b", reading, flags=re.IGNORECASE)
        assert any(token in lowered for token in ("konuş", "cümle", "güven", "duruş", "görün", "kendin", "ilişki", "sınır"))
        sentences = [item.strip() for item in re.split(r"(?<=[.!?])\s+", reading) if item.strip()]
        assert len(sentences) == len({item.lower() for item in sentences})
        assert all(sentence[:1].upper() == sentence[:1] for sentence in sentences if sentence[:1].isalpha())

    assert outputs["2026-03-04"] != outputs["2026-04-22"]


def test_real_chart_saturn_return_priority_applies_only_on_2026_03_04(monkeypatch) -> None:
    monkeypatch.setattr(settings, "life_chapter_priority_enabled", True)

    march_payload = transits._build_narrative_public_payload(
        _request(
            start="2026-03-04",
            end="2026-03-04",
            selected_date="2026-03-04",
            include_best_times=False,
            locale="tr",
        ),
        transits.date_type.fromisoformat("2026-03-04"),
    )
    april_payload = transits._build_narrative_public_payload(
        _request(
            start="2026-04-22",
            end="2026-04-22",
            selected_date="2026-04-22",
            include_best_times=False,
            locale="tr",
        ),
        transits.date_type.fromisoformat("2026-04-22"),
    )

    march_core = march_payload["period_core"]
    april_core = april_payload["period_core"]

    assert march_core["semantic_focus"]["source"] == "life_chapter"
    assert march_core["chapter_priority"]["applied"] is True
    assert march_core["chapter_priority"]["chapter_type"] == "saturn_return"
    assert march_core["chapter_priority"]["event_cards_role"] == "evidence_support"
    assert isinstance(march_core["period_reading_v1"]["full_text"], str) and march_core["period_reading_v1"]["full_text"].strip()

    assert april_core["chapter_priority"]["applied"] is False
    assert april_core["chapter_priority"]["chapter_type"] != "saturn_return"
    assert isinstance(april_core["period_reading_v1"]["full_text"], str) and len(april_core["period_reading_v1"]["full_text"]) >= 350


def test_public_payload_injects_canonical_natal_activation_context(monkeypatch) -> None:
    monkeypatch.setattr(transits, "_build_transits_engine_response", lambda _request, **_kwargs: {"display": {"items": []}, "natal": {"bodies": []}})
    monkeypatch.setattr(
        transits,
        "build_public_response",
        lambda _response: {
            "period_core": {
                "title": "Core",
                "period_opening": "Ana tema burada toplanıyor.",
                "core_story": "Dönem hikâyesi.",
                "canonical_period_spine": {
                    "version": "canonical_period_spine_v1",
                    "source": "canonical_natal_activation_v1",
                    "hook_id": "hook:relationship",
                    "target_node_id": "promise_build_safe_intimacy",
                    "primary_domain": "relationship",
                    "spine_lines": ["relational_line"],
                },
            },
            "event_cards": [],
            "period_peak_timeline": [],
            "timeline": {},
        },
    )
    monkeypatch.setattr(transits, "build_period_coverage", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(
        transits,
        "_select_daily_and_period_event_cards",
        lambda **_: {
            "daily_event_cards": [
                {
                    "event_id": "evt_daily",
                    "transit_body": "Saturn",
                    "aspect": "opposition",
                    "natal_point": "Venus",
                    "tags": {"domain": "relationships"},
                    "scene": {"start_house": 7, "outcome_house": 8},
                }
            ],
            "period_event_cards": [{"event_id": "evt_period", "tags": {"domain": "career"}, "scene": {"start_house": 10, "outcome_house": 10}}],
            "daily_selection": {
                "trigger_selection": {
                    "version": "daily_trigger_selection_v1",
                    "authority": "today_story_candidate_shadow",
                    "primary_trigger_event_id": "evt_daily",
                    "support_event_ids": [],
                    "background_event_ids": [],
                    "suppressed_event_ids": [],
                    "candidates": [],
                    "debug": {
                        "legacy_primary_event_id": "evt_daily",
                        "candidate_primary_trigger_event_id": "evt_daily",
                        "mismatch": False,
                    },
                }
            },
        },
    )
    monkeypatch.setattr(
        transits,
        "build_daily_synthesis",
        lambda **_kwargs: {"headline": "x", "body": "", "guidance": "", "sources": {"daily": [], "period": [], "natal": []}},
    )
    monkeypatch.setattr(transits, "compute_natal_chart", lambda *args, **kwargs: {"birth_date": "1996-12-28", "birth_time": "07:10", "birth_place": "Istanbul"})
    monkeypatch.setattr(
        transits,
        "build_canonical_natal_state_from_chart_data",
        lambda chart_data, metadata=None, include_debug=False: CanonicalNatalStateV1(
            chart_id="chart_for_transit",
            meaning_graph={
                "version": "natal_meaning_graph_v1",
                "activation_hooks": [
                    {
                        "hook_id": "hook:relationship",
                        "target_node_id": "promise_build_safe_intimacy",
                        "domains": ["relationship"],
                        "spine_lines": ["relational_line"],
                    },
                    {
                        "hook_id": "hook:career",
                        "target_node_id": "promise_mature_visibility",
                        "domains": ["career_visibility"],
                        "spine_lines": ["work_visibility_line"],
                    },
                ],
            },
        ),
    )

    payload = transits._build_narrative_public_payload(
        _request(selected_date="2026-03-10"),
        transits.date_type.fromisoformat("2026-03-01"),
    )

    assert payload["period_core"]["natal_activation_context"]["matched_event_ids"] == ["evt_period"]
    assert payload["period_core"]["canonical_promise_prefix"] == "Bu dönem doğum haritandaki yön ve görünürlük hattını özellikle çalıştırıyor."
    assert payload["period_core"]["period_opening"].startswith(payload["period_core"]["canonical_promise_prefix"])
    assert payload["daily_selection"]["natal_activation_context"]["matched_event_ids"] == ["evt_daily"]
    assert payload["daily_synthesis"]["natal_activation_context"]["top_target_node_ids"] == [
        "promise_build_safe_intimacy",
        "promise_mature_visibility",
    ]
    assert payload["daily_synthesis"]["sources"]["natal"] == ["chart_for_transit"]
    assert payload["daily_synthesis"]["today_story_candidate"]["story_type"] == "period_triggered_today"
    assert payload["daily_synthesis"]["today_story_candidate"]["primary_spine_line"] == "relational_line"
    assert payload["daily_synthesis"]["today_story_candidate"]["event_nature"] == "boundary"
    assert payload["daily_synthesis"]["today_story_candidate"]["reason_line_allowed"] is True
    assert payload["daily_synthesis"]["today_story_candidate"]["debug"]["activation_hook_match"] is True
    assert payload["daily_synthesis"]["daily_trigger_selection"]["primary_trigger_event_id"] == "evt_daily"
    assert payload["daily_synthesis"]["daily_trigger_selection"]["authority"] == "today_story_candidate_shadow"


def test_public_payload_skips_natal_activation_when_canonical_build_fails(monkeypatch) -> None:
    monkeypatch.setattr(transits, "_build_transits_engine_response", lambda _request, **_kwargs: {"display": {"items": []}, "natal": {"bodies": []}})
    monkeypatch.setattr(
        transits,
        "build_public_response",
        lambda _response: {
            "period_core": {"title": "Core"},
            "event_cards": [],
            "period_peak_timeline": [],
            "timeline": {},
        },
    )
    monkeypatch.setattr(transits, "build_period_coverage", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(
        transits,
        "_select_daily_and_period_event_cards",
        lambda **_: {
            "daily_event_cards": [{"event_id": "evt_daily"}],
            "period_event_cards": [],
            "daily_selection": {},
        },
    )
    monkeypatch.setattr(
        transits,
        "build_daily_synthesis",
        lambda **_kwargs: {"headline": "x", "body": "", "guidance": "", "sources": {"daily": [], "period": [], "natal": []}},
    )
    monkeypatch.setattr(transits, "compute_natal_chart", lambda *args, **kwargs: {"birth_date": "1996-12-28"})
    monkeypatch.setattr(
        transits,
        "build_canonical_natal_state_from_chart_data",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    payload = transits._build_narrative_public_payload(
        _request(selected_date="2026-03-10"),
        transits.date_type.fromisoformat("2026-03-01"),
    )

    assert "natal_activation_context" not in payload["period_core"]
    assert "natal_activation_context" not in payload["daily_selection"]
    assert payload["daily_synthesis"]["sources"]["natal"] == []


def test_public_payload_passes_canonical_natal_state_to_public_builder(monkeypatch) -> None:
    captured = {}

    monkeypatch.setattr(
        transits,
        "_build_transits_engine_response",
        lambda _request, **_kwargs: {"display": {"items": []}, "natal": {"bodies": []}},
    )

    def _fake_build_public_response(response):
        captured["canonical_state"] = response.get("_canonical_natal_state")
        return {
            "period_core": {"title": "Core"},
            "event_cards": [],
            "period_peak_timeline": [],
            "timeline": {},
        }

    monkeypatch.setattr(transits, "build_public_response", _fake_build_public_response)
    monkeypatch.setattr(transits, "build_period_coverage", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(
        transits,
        "_select_daily_and_period_event_cards",
        lambda **_: {
            "daily_event_cards": [],
            "period_event_cards": [],
            "daily_selection": {},
        },
    )
    monkeypatch.setattr(
        transits,
        "build_daily_synthesis",
        lambda **_kwargs: {"headline": "x", "body": "", "guidance": "", "sources": {"daily": [], "period": [], "natal": []}},
    )
    monkeypatch.setattr(transits, "compute_natal_chart", lambda *args, **kwargs: {"birth_date": "1996-12-28"})
    monkeypatch.setattr(
        transits,
        "build_canonical_natal_state_from_chart_data",
        lambda chart_data, metadata=None, include_debug=False: CanonicalNatalStateV1(
            chart_id="chart_builder_pass",
            meaning_graph={"version": "natal_meaning_graph_v1", "activation_hooks": []},
        ),
    )

    transits._build_narrative_public_payload(
        _request(selected_date="2026-03-10"),
        transits.date_type.fromisoformat("2026-03-01"),
    )

    assert isinstance(captured["canonical_state"], CanonicalNatalStateV1)
    assert captured["canonical_state"].chart_id == "chart_builder_pass"


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
        lambda _request, **_kwargs: {"display": {"items": raw_items}, "natal": {"bodies": []}},
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


def test_public_payload_home_uses_fast_builder_and_records_timing(monkeypatch) -> None:
    raw_items = [
        {"event_id": "evt_1", "transit_body": "Moon", "aspect": "square", "natal_point": "Venus"},
        {"event_id": "evt_2", "transit_body": "Saturn", "aspect": "trine", "natal_point": "Mercury"},
    ]
    captured = {"home_called": 0}

    monkeypatch.setattr(
        transits,
        "_build_transits_engine_response",
        lambda _request, **kwargs: {
            **captured.setdefault("engine_kwargs", kwargs),
        } and {"display": {"items": raw_items}, "natal": {"angles": {"asc": {"sign": "Capricorn"}}}},
    )

    def _home_builder(_response, selected_events=None, include_debug_artifacts=True):
        captured["home_called"] += 1
        captured["selected_event_ids"] = [str(item.get("event_id") or "") for item in selected_events or []]
        return {
            "period_core": {"title": "Core"},
            "event_cards": [{"event_id": "evt_1", "headline": "One"}],
        }

    monkeypatch.setattr(transits, "build_home_response", _home_builder)
    monkeypatch.setattr(
        transits,
        "build_public_response",
        lambda *_args, **_kwargs: pytest.fail("home payload should not call build_public_response"),
    )
    monkeypatch.setattr(
        transits,
        "select_event_ids",
        lambda _items, max_cards, natal=None: ([raw_items[0]], {"selection_mode": "test"}),
    )
    monkeypatch.setattr(transits, "build_period_coverage", lambda _items, selected_ids, now_date, tz: {})
    monkeypatch.setattr(
        transits,
        "_select_daily_and_period_event_cards",
        lambda **_kwargs: {
            "daily_event_cards": [{"event_id": "evt_1"}],
            "period_event_cards": [],
            "daily_selection": {},
        },
    )
    monkeypatch.setattr(
        transits,
        "build_daily_synthesis",
        lambda **_kwargs: {
            "headline": "Bugün konuşma daha dikkat çekiyor.",
            "body": "",
            "guidance": "",
            "theme": "communication",
            "theme_description": "",
            "sources": {"daily": ["evt_1"], "period": [], "natal": []},
        },
    )

    timing_probe = {"stages": {}, "metrics": {}}
    payload = transits._build_narrative_public_payload(
        _request(start="2026-03-10", end="2026-03-10", selected_date="2026-03-10", payload_profile="home"),
        transits.date_type.fromisoformat("2026-03-10"),
        selected_day_context={},
        timing_probe=timing_probe,
    )

    assert captured["home_called"] == 1
    assert captured["selected_event_ids"] == ["evt_1"]
    assert captured["engine_kwargs"] == {
        "include_window_report": False,
        "include_period_space": False,
        "include_multi_event_payload": False,
    }
    assert payload["period_core"]["title"] == "Core"
    assert payload["daily_synthesis"]["headline"] == "Bugün konuşma daha dikkat çekiyor."
    assert "build_home_response" in timing_probe["stages"]
    assert "daily_synthesis_build" in timing_probe["stages"]


def test_public_payload_home_limits_daily_selection_to_home_candidates(monkeypatch) -> None:
    raw_items = [
        {"event_id": "evt_1", "transit_body": "Neptune", "aspect": "square", "natal_point": "Venus", "phase": "separating"},
        {"event_id": "evt_2", "transit_body": "Moon", "aspect": "trine", "natal_point": "Mercury", "phase": "exact", "bucket": "short"},
        {"event_id": "evt_3", "transit_body": "Saturn", "aspect": "opposition", "natal_point": "Sun", "phase": "applying"},
        {"event_id": "evt_4", "transit_body": "Mercury", "aspect": "sextile", "natal_point": "Moon", "phase": "exactish", "bucket": "short"},
    ]
    captured = {}

    monkeypatch.setattr(
        transits,
        "_build_transits_engine_response",
        lambda _request, **_kwargs: {"display": {"items": raw_items}, "natal": {"bodies": []}},
    )
    monkeypatch.setattr(
        transits,
        "build_home_response",
        lambda _response, selected_events=None, include_debug_artifacts=True: {
            "period_core": {"title": "Core"},
            "event_cards": [
                {"event_id": "evt_1", "headline": "One"},
                {"event_id": "evt_3", "headline": "Three"},
            ],
        },
    )
    monkeypatch.setattr(
        transits,
        "select_event_ids",
        lambda _items, max_cards, natal=None: ([raw_items[0], raw_items[2]], {"selection_mode": "test"}),
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
        _request(
            start="2026-03-10",
            end="2026-03-10",
            selected_date="2026-03-10",
            payload_profile="home",
        ),
        transits.date_type.fromisoformat("2026-03-10"),
        selected_day_context={
            "top_event_ids": ["tr.moon.square.uranus"],
            "top_raw_event_ids": ["evt_4", "evt_2"],
        },
    )

    assert captured["raw_events"] == ["evt_4", "evt_2", "evt_1", "evt_3"]


def test_selected_day_context_reads_internal_top_event_ids_and_signals() -> None:
    context = transits._selected_day_context_from_calendar(
        {
            "days": [
                {
                    "date": "2026-03-10",
                    "labels": ["mind"],
                    "top_event_ids": ["evt_internal_a", "evt_internal_b"],
                    "top_raw_event_ids": ["raw_evt_a", "raw_evt_b"],
                    "raw_event_ids": ["raw_evt_a", "raw_evt_b", "raw_evt_c"],
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
    assert context["top_raw_event_ids"] == ["raw_evt_a", "raw_evt_b"]
    assert context["raw_event_ids"] == ["raw_evt_a", "raw_evt_b", "raw_evt_c"]
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
                        "top_event_ids": ["tr.moon.square.uranus"],
                        "top_raw_event_ids": ["evt_internal"],
                        "raw_event_ids": ["evt_internal", "evt_other"],
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

    assert captured["selected_day_context"]["top_event_ids"] == ["tr.moon.square.uranus"]
    assert captured["selected_day_context"]["top_raw_event_ids"] == ["evt_internal"]
    assert captured["selected_day_context"]["raw_event_ids"] == ["evt_internal", "evt_other"]
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
                        "top_raw_event_ids": ["evt_public_only"],
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
    assert captured["selected_day_context"]["top_raw_event_ids"] == ["evt_public_only"]
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


def test_home_wrapper_returns_populated_payload() -> None:
    response = transits.build_transit_narrative(
        _request(
            selected_date="2026-04-22",
            response_mode="public_only",
            payload_profile="home",
            start="2026-04-22",
            end="2026-04-22",
            debug=True,
        )
    )

    period_core = response["public"]["period_core"]
    degraded = response["debug"]["degraded_path"]

    assert period_core != {}
    assert degraded["active"] is False
    assert degraded["reason"] != "public_payload_exception"
    assert degraded["error_type"] == ""


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
