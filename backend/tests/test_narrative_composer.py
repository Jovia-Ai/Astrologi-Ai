import re

from app.transit.narrative.composer import (
    compose_daily_line2_from_top_event,
    compose_event_summary_from_item,
)
from app.transit.narrative.generator import generate_daily_narrative


def _sentence_count(text: str) -> int:
    return len([p.strip() for p in re.split(r"[.!?]", text) if p.strip()])


def test_event_summary_max_two_sentences_and_blacklist_absent() -> None:
    item = {
        "event_id": "evt_1",
        "transit_body": "Venus",
        "natal_point": "Moon",
        "aspect": "trine",
        "phase": "applying",
        "bucket": "medium",
        "houses": {"transit_in_natal_house": 7},
        "domains": ["relationships"],
    }
    text = compose_event_summary_from_item(item, seed=11, voice_style="you")
    assert 1 <= _sentence_count(text) <= 2
    for banned in ["orb", "aspect", "applying", "separating", "percentile", "marker", "tier"]:
        assert banned not in text.lower()
    assert any(token in text.lower() for token in ("hissedebilirsin", "fark edebilirsin", "bazen", "olabilir"))


def test_event_summary_seed_is_deterministic() -> None:
    item = {
        "event_id": "evt_2",
        "transit_body": "Mars",
        "natal_point": "Saturn",
        "aspect": "square",
        "phase": "exact",
        "bucket": "short",
        "houses": {"transit_in_natal_house": 10},
        "domains": ["career"],
    }
    first = compose_event_summary_from_item(item, seed=99)
    second = compose_event_summary_from_item(item, seed=99)
    third = compose_event_summary_from_item(item, seed=100)
    assert first == second
    assert first != third


def test_daily_line_uses_top_event_composer() -> None:
    line2 = compose_daily_line2_from_top_event(
        top_event={"label": "Kariyer vurgusu", "bodies": ["Saturn", "MC"]},
        labels=["support_tone"],
        seed=12,
    )
    assert line2
    assert "aspect" not in line2.lower()


def test_daily_narrative_with_top_event_stays_three_sentences() -> None:
    text = generate_daily_narrative(
        rating=2,
        is_critical=False,
        labels=["career_axis", "support_tone"],
        seed=777,
        top_event={"label": "Kariyer vurgusu", "bodies": ["Saturn", "MC"]},
    )
    assert _sentence_count(text) == 3
