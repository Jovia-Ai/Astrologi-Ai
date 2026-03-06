from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.astro.chart_engine.builder import build_natal_chart
from app.astro_core.formatting import format_lon
from app.models.chart_models import ChartAngle, ChartBody, ChartMeta, HouseCusp, NormalizedChart

_PLANET_NAME_MAP = {
    "sun": "sun",
    "moon": "moon",
    "mercury": "mercury",
    "venus": "venus",
    "mars": "mars",
    "jupiter": "jupiter",
    "saturn": "saturn",
    "uranus": "uranus",
    "neptune": "neptune",
    "pluto": "pluto",
    "north node": "node",
    "true node": "node",
    "node": "node",
    "lilith": "lilith",
    "chiron": "chiron",
    "vertex": "vertex",
    "fortune": "fortune",
    "part of fortune": "fortune",
}

_ALLOWED_BODIES = set(_PLANET_NAME_MAP.values())


def compute_raw_natal(input_data: Dict[str, Any], tz: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Adapter hook: connect this to YOUR existing natal computation.

    Expected return shape (minimal):
      {
        "planets": [{"body": "sun", "longitude": 276.75, "house": 1}, ...],
        "angles":  [{"body": "asc", "longitude": 271.18}, {"body":"mc","longitude":205.28}],
        "houses":  [{"house":1,"longitude":271.18}, ... {"house":12,"longitude":251.19}],
      }
    """
    chart = build_natal_chart(input_data)

    planets_out: List[Dict[str, Any]] = []
    for raw_name, payload in (chart.get("planets") or {}).items():
        if not isinstance(payload, dict):
            continue
        lon = payload.get("longitude")
        if lon is None:
            continue
        key = str(raw_name).strip().lower()
        body = _PLANET_NAME_MAP.get(key)
        if not body or body not in _ALLOWED_BODIES:
            continue
        planets_out.append(
            {
                "body": body,
                "longitude": float(lon),
                "house": payload.get("house"),
            }
        )

    angles_out: List[Dict[str, Any]] = []
    angles = chart.get("angles") or {}
    asc = angles.get("ascendant")
    mc = angles.get("midheaven")
    if asc is not None:
        angles_out.append({"body": "asc", "longitude": float(asc)})
    if mc is not None:
        angles_out.append({"body": "mc", "longitude": float(mc)})

    houses_out: List[Dict[str, Any]] = []
    houses = chart.get("houses") or {}
    for i in range(1, 13):
        val = houses.get(str(i))
        if val is None:
            continue
        houses_out.append({"house": i, "longitude": float(val)})

    return {"planets": planets_out, "angles": angles_out, "houses": houses_out}


def normalize_raw_natal(raw: Dict[str, Any], tz: str, name: str) -> NormalizedChart:
    bodies: List[ChartBody] = []
    for p in raw.get("planets", []):
        lon = float(p["longitude"])
        sign, deg_in_sign, formatted = format_lon(lon)
        bodies.append(
            ChartBody(
                body=p["body"],
                longitude=lon,
                sign=sign,
                deg_in_sign=deg_in_sign,
                formatted=formatted,
                house=p.get("house"),
            )
        )

    angles: List[ChartAngle] = []
    for a in raw.get("angles", []):
        lon = float(a["longitude"])
        _, _, formatted = format_lon(lon)
        angles.append(ChartAngle(body=a["body"], longitude=lon, formatted=formatted))

    houses: List[HouseCusp] = []
    for h in raw.get("houses", []):
        lon = float(h["longitude"])
        _, _, formatted = format_lon(lon)
        houses.append(HouseCusp(house=int(h["house"]), longitude=lon, formatted=formatted))
    houses.sort(key=lambda x: x.house)

    meta = ChartMeta(kind="natal", tz=tz, notes={"name": name})
    return NormalizedChart(meta=meta, bodies=bodies, angles=angles, houses=houses, aspects=[], overlays=None)
