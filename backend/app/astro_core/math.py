from __future__ import annotations


def norm360(lon: float) -> float:
    x = lon % 360.0
    return x if x >= 0 else x + 360.0


def shortest_arc_delta(a: float, b: float) -> float:
    # delta from a -> b in (-180, +180]
    a = norm360(a)
    b = norm360(b)
    d = (b - a) % 360.0
    if d > 180.0:
        d -= 360.0
    return d


def midpoint_longitude(a: float, b: float) -> float:
    a = norm360(a)
    b = norm360(b)
    d = shortest_arc_delta(a, b)
    return norm360(a + d / 2.0)
