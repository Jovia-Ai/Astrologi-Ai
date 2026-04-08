from __future__ import annotations

from app.astro.chart_engine import builder


def test_build_natal_chart_uses_explicit_location_without_geocode(monkeypatch) -> None:
    def fail_fetch_location(city: str):
        raise AssertionError(f"fetch_location should not be called for {city}")

    monkeypatch.setattr(builder, "fetch_location", fail_fetch_location)

    chart = builder.build_natal_chart(
        {
            "date": "1996-12-28",
            "time": "07:10",
            "city": "Unknown Place",
            "birth_latitude": 41.0082,
            "birth_longitude": 28.9784,
            "birth_timezone": "Europe/Istanbul",
        }
    )

    assert chart["location"]["latitude"] == 41.0082
    assert chart["location"]["longitude"] == 28.9784
    assert chart["location"]["timezone"] == "Europe/Istanbul"


def test_resolve_location_maps_istanbul_turkey_to_local_fallback(monkeypatch) -> None:
    def fail_fetch_location(city: str):
        raise AssertionError(f"fetch_location should not be called for {city}")

    monkeypatch.setattr(builder, "fetch_location", fail_fetch_location)

    location = builder.resolve_location("Istanbul, Turkey")

    assert location.latitude == 41.0082
    assert location.longitude == 28.9784
    assert location.timezone == "Europe/Istanbul"
    assert location.label == "Istanbul, TR"
