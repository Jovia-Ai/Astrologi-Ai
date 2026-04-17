from app.transit.present import public_builder
from app.transit.present.public_builder import build_public_response
from app.transit.narrative.deep_archetype_engine import build_combined_meaning


def _natal_snapshot() -> dict:
    return {
        "bodies": [
            {"body": "Sun", "lon": 276.75, "sign": "Capricorn", "house": 1},
            {"body": "Moon", "lon": 133.94, "sign": "Leo", "house": 8},
            {"body": "Mercury", "lon": 287.36, "sign": "Capricorn", "house": 1},
            {"body": "Venus", "lon": 253.71, "sign": "Sagittarius", "house": 12},
            {"body": "Mars", "lon": 177.93, "sign": "Virgo", "house": 9},
            {"body": "Jupiter", "lon": 294.29, "sign": "Capricorn", "house": 1},
            {"body": "Saturn", "lon": 1.15, "sign": "Aries", "house": 3},
            {"body": "Uranus", "lon": 303.06, "sign": "Aquarius", "house": 1},
            {"body": "Neptune", "lon": 296.69, "sign": "Capricorn", "house": 1},
            {"body": "Pluto", "lon": 244.25, "sign": "Sagittarius", "house": 11},
        ],
        "angles": {
            "ASC": {"point": "ASC", "sign": "Capricorn"},
            "MC": {"point": "MC", "sign": "Libra"},
            "DSC": {"point": "DSC", "sign": "Cancer"},
            "IC": {"point": "IC", "sign": "Aries"},
        },
        "house_cusps": [
            {"house": 1, "sign": "Capricorn"},
            {"house": 2, "sign": "Aquarius"},
            {"house": 3, "sign": "Pisces"},
            {"house": 4, "sign": "Aries"},
            {"house": 5, "sign": "Taurus"},
            {"house": 6, "sign": "Gemini"},
            {"house": 7, "sign": "Cancer"},
            {"house": 8, "sign": "Leo"},
            {"house": 9, "sign": "Virgo"},
            {"house": 10, "sign": "Libra"},
            {"house": 11, "sign": "Scorpio"},
            {"house": 12, "sign": "Sagittarius"},
        ],
    }


def _event(
    *,
    event_id: str,
    body: str,
    natal: str,
    aspect: str,
    house: int,
    phase: str = "applying",
    bucket: str = "long",
    weight: float = 1.2,
    tier: str = "main",
) -> dict:
    return {
        "event_id": event_id,
        "transit_body": body,
        "natal_point": natal,
        "aspect": aspect,
        "phase": phase,
        "bucket": bucket,
        "houses": {"transit_in_natal_house": house},
        "signs": {"transit_body_sign": "Aries"},
        "domains": ["mind", "career"],
        "source_pos": {"sign": "Aries", "deg": 12.3},
        "target_pos": {"sign": "Virgo", "deg": 12.4},
        "orb_deg": 0.1,
        "strength": min(1.0, max(0.05, weight / 1.5)),
        "ranking": {"tier": tier, "weight": weight},
        "interpretation": {
            "headline": f"{body} etkisi",
            "summary": "Test ozeti",
            "time_hint": "yaklasiyor",
            "do": ["Not al", "Ritmi koru", "Sade kal"],
            "watch": ["Asiri tepki", "Acele karar"],
        },
    }


def test_public_response_includes_layered_fields() -> None:
    response = {
        "locale": "tr",
        "transit_date": "2026-03-10",
        "metrics": {"pressure_index": 0.62, "support_index": 0.54},
        "presentable": {"summary": {"main_theme": "mind", "one_liner": "Donem temasi"}},
        "natal": _natal_snapshot(),
        "display": {
            "items": [
                _event(
                    event_id="evt_saturn",
                    body="Saturn",
                    natal="Mercury",
                    aspect="square",
                    house=3,
                    weight=1.4,
                ),
                _event(
                    event_id="evt_pluto",
                    body="Pluto",
                    natal="MC",
                    aspect="trine",
                    house=10,
                    weight=1.3,
                ),
                _event(
                    event_id="evt_moon",
                    body="Moon",
                    natal="Venus",
                    aspect="conjunction",
                    house=5,
                    weight=1.1,
                ),
            ]
        },
    }

    out = build_public_response(response)
    public = out

    assert "period_core" in public
    assert "event_cards" in public
    assert "timeline" in public
    assert "events" not in public

    period = public["period_core"]
    assert isinstance(period["title"], str) and period["title"]
    assert isinstance(period["core_story"], str) and period["core_story"]
    assert isinstance(period["upper_meaning"], str) and period["upper_meaning"]
    assert isinstance(period["tags"], list) and period["tags"]
    for key in (
        "period_opening",
        "big_picture",
        "mechanism",
        "growth_edge",
        "relational_or_life_expression",
        "what_it_builds",
    ):
        assert isinstance(period.get(key), str) and str(period.get(key)).strip()

    cards = public["event_cards"]
    assert isinstance(cards, list) and cards
    first = cards[0]
    for key in (
        "event_id",
        "title",
        "headline",
        "opening",
        "essence",
        "asks",
        "watchout",
        "what_it_builds",
        "technical_note",
        "signature",
        "tone",
        "section_labels",
        "why_now",
        "conflict",
        "shadow",
        "upper",
        "time_hint",
        "guidance",
        "watch_out",
        "connected_points",
        "natal_context_pack",
        "natal_promise",
        "narrative_provenance",
    ):
        assert key in first
    assert "Moon" not in {card["signature"] for card in cards}
    natal_promise = first["natal_promise"]
    assert 0.0 <= float(natal_promise["score"]) <= 1.0
    assert natal_promise["verdict"] in {"low", "medium", "high"}
    assert isinstance(natal_promise["drivers"], list) and len(natal_promise["drivers"]) >= 3
    assert isinstance(natal_promise["connected_points"], list) and len(natal_promise["connected_points"]) >= 3
    assert isinstance(natal_promise["gate"], dict)
    assert isinstance(first["connected_points"], list)
    assert isinstance(first["natal_context_pack"], dict)
    if first["natal_context_pack"]:
        target = first["natal_context_pack"].get("target") or {}
        assert "planet" in target
        assert "house" in target
    provenance = first["narrative_provenance"]
    assert provenance["headline_source"] == "event.headline"
    assert provenance["opening_source"] == "event.opening"
    assert isinstance(provenance["period_track_used"], bool)

    point_kinds = {
        p.get("kind")
        for card in cards
        for p in ((card.get("natal_promise") or {}).get("connected_points") or [])
        if isinstance(p, dict)
    }
    assert "house" in point_kinds
    assert "sign" in point_kinds
    assert "dispositor_chain" in point_kinds

    timeline = public["timeline"]
    assert "summary" in timeline and isinstance(timeline["summary"], str)
    assert "lines" in timeline and len(timeline["lines"]) >= 1


def test_public_response_supports_english_public_copy() -> None:
    response = {
        "locale": "en",
        "transit_date": "2026-03-10",
        "metrics": {"pressure_index": 0.62, "support_index": 0.54},
        "presentable": {"summary": {"main_theme": "mind", "one_liner": "Period theme"}},
        "natal": _natal_snapshot(),
        "display": {
            "items": [
                _event(
                    event_id="evt_saturn",
                    body="Saturn",
                    natal="Mercury",
                    aspect="square",
                    house=3,
                    weight=1.4,
                ),
            ]
        },
    }

    out = build_public_response(response)
    period = out["period"]
    first = out["event_cards"][0]
    timeline = out["timeline"]

    merged = " ".join(
        [
            str(period.get("core_story") or ""),
            str((period.get("summary") or {}).get("one_liner") or ""),
            str(first.get("headline") or ""),
            str(first.get("summary") or ""),
            str(first.get("conflict") or ""),
            str(first.get("upper_meaning") or ""),
            str(timeline.get("summary") or ""),
        ]
    ).lower()

    assert "you " in merged or "your " in merged
    assert "etkisi" not in merged
    assert "dönem" not in merged
    assert "gün" not in merged
    assert "saturn" in merged


def test_saturn_aries_third_house_combined_meaning_keywords() -> None:
    event = _event(
        event_id="evt_saturn_aries_3",
        body="Saturn",
        natal="Mercury",
        aspect="square",
        house=3,
    )
    meaning = build_combined_meaning(event)
    merged = " ".join(
        [meaning["conflict"], meaning["shadow"], meaning["upper"]]
    ).lower()
    assert "saturn" in merged
    assert "3. ev" in merged
    assert any(token in merged for token in ("zihin", "iletisim"))
    assert any(token in merged for token in ("hizli", "dogrudan"))


def test_event_card_natal_promise_is_deterministic() -> None:
    response = {
        "locale": "tr",
        "transit_date": "2026-03-10",
        "metrics": {"pressure_index": 0.62, "support_index": 0.54},
        "presentable": {"summary": {"main_theme": "mind", "one_liner": "Donem temasi"}},
        "natal": _natal_snapshot(),
        "display": {
            "items": [
                _event(
                    event_id="evt_saturn",
                    body="Saturn",
                    natal="Mercury",
                    aspect="square",
                    house=3,
                    weight=1.4,
                )
            ]
        },
    }
    out_a = build_public_response(response)
    out_b = build_public_response(response)
    assert out_a["event_cards"][0]["natal_promise"] == out_b["event_cards"][0]["natal_promise"]


def test_event_card_natal_promise_fallback_when_natal_missing() -> None:
    response = {
        "locale": "tr",
        "transit_date": "2026-03-10",
        "metrics": {"pressure_index": 0.62, "support_index": 0.54},
        "presentable": {"summary": {"main_theme": "mind", "one_liner": "Donem temasi"}},
        "display": {
            "items": [
                _event(
                    event_id="evt_saturn",
                    body="Saturn",
                    natal="Mercury",
                    aspect="square",
                    house=3,
                    weight=1.4,
                )
            ]
        },
    }
    out = build_public_response(response)
    promise = out["event_cards"][0]["natal_promise"]
    assert promise["score"] == 0.0
    assert promise["verdict"] == "low"
    assert len(promise["drivers"]) >= 3
    assert promise["drivers"][0]["text"] == "not available"


def test_public_response_caps_period_peak_timeline(monkeypatch) -> None:
    response = {
        "locale": "tr",
        "transit_date": "2026-03-10",
        "metrics": {"pressure_index": 0.62, "support_index": 0.54},
        "presentable": {"summary": {"main_theme": "mind", "one_liner": "Donem temasi"}},
        "natal": _natal_snapshot(),
        "display": {
            "items": [
                {
                    **_event(
                        event_id=f"evt_{index}",
                        body="Saturn",
                        natal="Mercury",
                        aspect="square",
                        house=3,
                        weight=1.4 - (index * 0.05),
                    ),
                    "timing": {
                        "peak_date_utc": f"2026-03-{10 + index:02d}T09:00:00+00:00",
                        "entry_date_utc": f"2026-03-{9 + index:02d}T09:00:00+00:00",
                        "exit_date_utc": f"2026-03-{11 + index:02d}T09:00:00+00:00",
                    },
                }
                for index in range(8)
            ]
        },
    }
    build_event_card_calls = {"count": 0}

    def _stub_build_event_card(event, context=None):
        build_event_card_calls["count"] += 1
        event_id = str(event.get("event_id") or "")
        return {
            "event_id": event_id,
            "title": f"Card {event_id}",
            "headline": f"Headline {event_id}",
            "signature": f"Signature {event_id}",
            "signature_tr": f"Imza {event_id}",
            "bucket": str(event.get("bucket") or "long"),
            "phase": str(event.get("phase") or "applying"),
            "horizon": "period",
            "time_hint_tr": "Zaman akiyor.",
            "timing": dict(event.get("timing") or {}),
        }

    monkeypatch.setattr(public_builder, "build_active_event_cards", lambda _response, max_cards=5: [])
    monkeypatch.setattr(public_builder, "build_period_core", lambda _response, event_cards=None: {})
    monkeypatch.setattr(public_builder, "build_event_card", _stub_build_event_card)

    out = build_public_response(response)

    assert len(out["period_peak_timeline"]) == public_builder.DEFAULT_PERIOD_PEAK_TIMELINE_ITEMS
    assert build_event_card_calls["count"] == public_builder.DEFAULT_PERIOD_PEAK_TIMELINE_ITEMS
