from app.transit.calendar.best_times import _get_tz_from_payload


def test_get_tz_from_payload_prefers_valid_tz() -> None:
    payload = {"tz": "Europe/Istanbul"}
    assert _get_tz_from_payload(payload) == "Europe/Istanbul"


def test_get_tz_from_payload_falls_back_to_utc_for_invalid() -> None:
    payload = {"tz": "Not/AZone"}
    assert _get_tz_from_payload(payload) == "UTC"


def test_get_tz_from_payload_supports_nested_sources() -> None:
    payload = {"profile": {"tz": "America/New_York"}}
    assert _get_tz_from_payload(payload) == "America/New_York"
