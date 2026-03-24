from __future__ import annotations

from datetime import date, datetime, timezone

from app.sky_events.generator import generate_global_sky_events
from app.sky_events.service import (
    get_sky_archive,
    get_sky_event_detail,
    get_sky_now_feed,
    personalize_sky_event,
)
from app.sky_events.models import SkyEventPersonalizationRequest


def test_generate_global_sky_events_smoke() -> None:
    now = datetime(2026, 3, 14, 12, 0, tzinfo=timezone.utc)
    events = generate_global_sky_events(
        datetime(2026, 3, 1, tzinfo=timezone.utc),
        datetime(2026, 3, 31, 23, 59, tzinfo=timezone.utc),
        now=now,
    )

    assert events
    assert len({event.id for event in events}) == len(events)
    assert any(event.event_type in {"lunation_new_moon", "lunation_full_moon", "eclipse"} for event in events)
    assert any(event.event_type == "ingress" for event in events)


def test_sky_now_feed_returns_global_rail() -> None:
    now = datetime(2026, 3, 14, 12, 0, tzinfo=timezone.utc)
    feed = get_sky_now_feed(now=now, tz="Europe/Istanbul", limit=4, debug=True)

    assert feed.rail_type == "global_sky_events"
    assert feed.items
    assert feed.hero is not None
    assert feed.hero.personalization_cta["endpoint"].startswith("/sky/events/")
    assert "period_core" not in feed.model_dump()


def test_sky_detail_archive_and_personalization_smoke() -> None:
    now = datetime(2026, 3, 14, 12, 0, tzinfo=timezone.utc)
    feed = get_sky_now_feed(now=now, tz="Europe/Istanbul", limit=3)
    target = feed.items[0]

    detail = get_sky_event_detail(id_or_slug=target.id, now=now, tz="Europe/Istanbul")
    assert detail.event.id == target.id
    assert detail.personalization_cta["label_tr"]

    archive = get_sky_archive(
        date_from=date(2026, 3, 1),
        date_to=date(2026, 3, 31),
        tz="Europe/Istanbul",
        limit=20,
    )
    assert archive.items
    assert all("2026-03" in item.exact_at for item in archive.items)

    personalized = personalize_sky_event(
        id_or_slug=target.id,
        request=SkyEventPersonalizationRequest(
            birth_date="1996-12-28",
            birth_time="07:10",
            birth_place="Istanbul",
        ),
        now=now,
    )
    assert personalized.event_id == target.id
    assert personalized.summary_tr
    assert personalized.relevance_level in {"light", "medium", "high"}
