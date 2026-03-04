from app.transit.narrative.astrolog_narrative_engine import (
    PeriodStoryContext,
    build_period_story,
)


def _event(**kwargs):
    base = {
        "event_id": "evt_np_asc",
        "transit_body": "Neptune",
        "aspect": "square",
        "natal_point": "ASC",
        "strength": 0.95,
        "orb_deg": 0.2,
        "phase": "exactish",
        "bucket": "long",
        "tags": ["self", "pressure"],
        "houses": {"transit_in_natal_house": 3, "natal_point_house": None},
    }
    base.update(kwargs)
    return base


def test_period_story_deterministic_for_same_seed() -> None:
    ctx = PeriodStoryContext(
        period_core={"featured_events": [_event()]},
        chart_snapshot={
            "house_cusps": {"1": {"sign": "Capricorn"}},
            "bodies": {"Saturn": {"house": 3, "sign": "Aries"}},
        },
        natal_promise={"themes": ["kimlik ve ifade"]},
    )

    a = build_period_story(ctx)
    b = build_period_story(ctx)

    assert a.big_picture == b.big_picture
    assert a.mechanism == b.mechanism
    assert a.upper_meaning == b.upper_meaning


def test_period_story_fallback_without_snapshot_data() -> None:
    ctx = PeriodStoryContext(
        period_core={"featured_events": [_event(event_id="evt_fallback", natal_point="Mars")]},
        chart_snapshot={},
        natal_promise={},
    )

    out = build_period_story(ctx)
    assert isinstance(out.big_picture, str) and out.big_picture
    assert isinstance(out.mechanism, str) and out.mechanism
    assert isinstance(out.upper_meaning, str) and out.upper_meaning


def test_period_story_strips_technical_token_leaks() -> None:
    ctx = PeriodStoryContext(
        period_core={
            "featured_events": [
                _event(
                    event_id="evt_tokens",
                    phase="applying",
                    natal_point="ASC",
                    tags=["self", "mind"],
                )
            ]
        },
        chart_snapshot={"house_cusps": {"1": {"sign": "Capricorn"}}},
        natal_promise={"themes": ["zihin ve iletişim"]},
    )

    out = build_period_story(ctx)
    merged = f"{out.big_picture} {out.mechanism} {out.upper_meaning}".lower()
    for token in ("period", "exactish", "applying", "separating", "orb_deg"):
        assert token not in merged
