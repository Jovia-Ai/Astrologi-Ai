import re

from app.transit.narrative.generator import (
    generate_daily_narrative,
    make_birth_fingerprint,
    make_seed,
    pick_label_fragments,
)


def _sentence_count(text: str) -> int:
    parts = [p.strip() for p in re.split(r"[.!?]", text) if p.strip()]
    return len(parts)


def test_daily_narrative_has_exactly_three_sentences() -> None:
    seed = make_seed(
        birth_fingerprint=make_birth_fingerprint(
            birth_date="1996-12-28",
            birth_time="07:10",
            birth_place="Istanbul",
            tz="Europe/Istanbul",
        ),
        date="2026-03-05",
        intent="beauty_care_nourish",
        lens="general",
        rating=2,
        is_critical=False,
        labels=["support_tone", "relationships_axis"],
    )
    text = generate_daily_narrative(
        rating=2,
        is_critical=False,
        labels=["support_tone", "relationships_axis"],
        seed=seed,
    )
    assert _sentence_count(text) == 3


def test_daily_narrative_blacklist_absent() -> None:
    text = generate_daily_narrative(
        rating=3,
        is_critical=True,
        labels=["phase_shift", "peak_energy"],
        seed=42,
    )
    for banned in ["orb", "aspect", "transit", "marker", "percentile", "event_count"]:
        assert banned not in text.lower()


def test_seed_deterministic_and_variant() -> None:
    kwargs = dict(
        rating=1,
        is_critical=False,
        labels=["support_tone", "home_axis"],
    )
    t1 = generate_daily_narrative(seed=12345, **kwargs)
    t2 = generate_daily_narrative(seed=12345, **kwargs)
    t3 = generate_daily_narrative(seed=12346, **kwargs)
    assert t1 == t2
    assert t1 != t3


def test_label_priority_selection_prefers_primary_then_risk() -> None:
    selected, _fragments = pick_label_fragments(
        labels=["career_axis", "phase_shift", "injury_risk"],
        seed=9,
    )
    assert selected
    assert selected[0] in {"phase_shift", "ingress", "peak_energy", "retro_station", "eclipse_window"}
