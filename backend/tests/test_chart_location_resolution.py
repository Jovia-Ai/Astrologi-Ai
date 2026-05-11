from __future__ import annotations

from app.astro.chart_engine import builder
from app.routers import charts as charts_router


def test_build_natal_chart_uses_explicit_location_without_geocode(monkeypatch) -> None:
    def fail_fetch_location(city: str):
        raise AssertionError(f"fetch_location should not be called for {city}")

    monkeypatch.setattr(builder, "fetch_location", fail_fetch_location)

    chart = builder.build_natal_chart(
        {
            "birth_date": "1996-12-28",
            "birth_time": "07:10",
            "birth_place": "Null Island",
            "latitude": 0.0,
            "longitude": 0.0,
            "timezone": "UTC",
        }
    )

    assert chart["location"]["latitude"] == 0.0
    assert chart["location"]["longitude"] == 0.0
    assert chart["location"]["timezone"] == "UTC"


def test_calculate_natal_chart_route_skips_geocoding_when_coordinates_and_timezone_present(
    monkeypatch,
) -> None:
    called = False

    def fail_fetch_location(city: str):
        nonlocal called
        called = True
        raise AssertionError(f"fetch_location should not be called for {city}")

    monkeypatch.setattr(builder, "fetch_location", fail_fetch_location)
    monkeypatch.setattr(charts_router, "chart_to_summary", lambda chart: "summary")
    monkeypatch.setattr(
        charts_router,
        "generate_ai_interpretation",
        lambda summary: "interpretation",
    )

    chart = charts_router.calculate_natal_chart(
        {
            "birth_date": "1996-12-28",
            "birth_time": "07:10",
            "birth_place": "Null Island",
            "latitude": 0.0,
            "longitude": 0.0,
            "timezone": "UTC",
        }
    )

    assert chart["location"]["city"] == "Null Island"
    assert chart["location"]["latitude"] == 0.0
    assert chart["location"]["longitude"] == 0.0
    assert chart["location"]["timezone"] == "UTC"
    assert chart["interpretation"] == "interpretation"
    assert called is False


def test_resolve_location_calls_geocoder_when_explicit_timezone_missing(monkeypatch) -> None:
    calls: list[str] = []

    def fake_fetch_location(city: str) -> builder.LocationData:
        calls.append(city)
        return builder.LocationData(10.0, 20.0, "Etc/GMT", "Fetched Place")

    monkeypatch.setattr(builder, "fetch_location", fake_fetch_location)

    location = builder.resolve_location(
        "Unknown Place",
        latitude=0.0,
        longitude=0.0,
        timezone=None,
    )

    assert location == builder.LocationData(10.0, 20.0, "Etc/GMT", "Fetched Place")
    assert calls == ["Unknown Place"]


def test_resolve_location_maps_istanbul_turkey_to_local_fallback(monkeypatch) -> None:
    def fail_fetch_location(city: str):
        raise AssertionError(f"fetch_location should not be called for {city}")

    monkeypatch.setattr(builder, "fetch_location", fail_fetch_location)

    location = builder.resolve_location("Istanbul, Turkey")

    assert location.latitude == 41.0082
    assert location.longitude == 28.9784
    assert location.timezone == "Europe/Istanbul"
    assert location.label == "Istanbul, TR"
