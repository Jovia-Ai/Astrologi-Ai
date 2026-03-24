from __future__ import annotations

from types import SimpleNamespace

from app.api.routes import sky
from app.sky_events.models import SkyEventPersonalizationRequest


class _Dumpable:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def model_dump(self) -> dict:
        return dict(self._payload)


def test_sky_personalize_includes_astro_event_v2_bridge(monkeypatch) -> None:
    monkeypatch.setattr(
        sky,
        "personalize_sky_event",
        lambda **_: _Dumpable(
            {
                "event_id": "sky_1",
                "event_slug": "sky-1",
                "summary_tr": "Kolektif etki haritada belirgin.",
                "relevance_level": "medium",
            }
        ),
    )
    monkeypatch.setattr(
        sky,
        "get_sky_event_detail",
        lambda **_: SimpleNamespace(
            event=SimpleNamespace(
                id="sky_1",
                event_type="retrograde_start",
                bodies=["Mercury"],
                starts_at="2026-03-10T00:00:00+00:00",
                exact_at="2026-03-12T00:00:00+00:00",
                ends_at="2026-03-20T00:00:00+00:00",
                cultural_interest_score=88.0,
            )
        ),
    )
    monkeypatch.setattr(
        sky,
        "personalize_global_event",
        lambda **_: {
            "schema_version": "astro_event.v2",
            "bridge": {"event_id": "bridge_1", "event_kind": "emphasis"},
        },
    )

    payload = sky.sky_event_personalize(
        "sky_1",
        SkyEventPersonalizationRequest(
            birth_date="1996-12-28",
            birth_time="07:10",
            birth_place="Istanbul, TR",
        ),
        tz="Europe/Istanbul",
        at="2026-03-12T12:00:00+00:00",
    )

    assert payload["event_id"] == "sky_1"
    assert payload["astro_event_v2"]["schema_version"] == "astro_event.v2"
    assert payload["astro_event_v2"]["bridge"]["event_id"] == "bridge_1"
