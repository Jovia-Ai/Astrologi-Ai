from backend.app.astro_core.math import midpoint_longitude


def test_midpoint_wrap():
    assert abs(midpoint_longitude(350.0, 10.0) - 0.0) < 1e-6


def test_midpoint_regular():
    assert abs(midpoint_longitude(100.0, 140.0) - 120.0) < 1e-6
