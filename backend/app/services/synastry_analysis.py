from typing import Any, Dict, List, Optional, Tuple
import math

from app.astro.chart_engine.builder import build_natal_chart
from app.astro.synastry.engine_v1 import SynastryEngineV1
from app.synastry.public_builder import build_synastry_public

DEFAULT_BODIES = [
    "sun",
    "moon",
    "mercury",
    "venus",
    "mars",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
    "node",
    "vertex",
    "asc",
    "mc",
]

engine = SynastryEngineV1()

PLANET_KEY_MAP = {
    "north node": "node",
    "vertex": "vertex",
}

SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]


def _norm360(x: float) -> float:
    x = float(x) % 360.0
    return x + 360.0 if x < 0 else x


def _sign_deg(lon: float) -> Tuple[str, float]:
    lon = _norm360(lon)
    sign_index = int(lon // 30.0)
    deg_in_sign = lon - (sign_index * 30.0)
    return SIGNS[sign_index], deg_in_sign


def _format_deg(deg: float) -> str:
    d = int(math.floor(deg))
    m = int(round((deg - d) * 60))
    if m == 60:
        d += 1
        m = 0
    return f"{d}°{m:02d}′"


def _format_lon(lon: float) -> str:
    sign, deg = _sign_deg(lon)
    return f"{sign} {_format_deg(deg)}"


def _extract_house_cusps(chart: Dict[str, Any]) -> Optional[List[float]]:
    houses = chart.get("houses") or {}
    cusps = houses.get("cusps") or houses.get("cusp_longitudes") or None
    if isinstance(cusps, list) and len(cusps) >= 12:
        return [float(x) for x in cusps[:12]]
    if isinstance(houses, dict):
        try:
            ordered = [float(houses[str(i)]) for i in range(1, 13)]
            return ordered
        except Exception:
            return None
    return None


def _house_from_cusps(lon: float, cusps: List[float]) -> int:
    lon = _norm360(lon)
    c = [_norm360(x) for x in cusps]
    for i in range(12):
        start = c[i]
        end = c[(i + 1) % 12]
        if i == 11:
            end = end + 360.0
        if end < start:
            end += 360.0

        test_lon = lon
        if test_lon < start:
            test_lon += 360.0

        if start <= test_lon < end:
            return i + 1
    return 12


def _planet_house_from_chart(chart: Dict[str, Any], lon: float) -> Optional[int]:
    cusps = _extract_house_cusps(chart)
    if not cusps:
        return None
    return _house_from_cusps(lon, cusps)


def _midpoint(a: float, b: float) -> float:
    a = _norm360(a)
    b = _norm360(b)
    diff = (b - a + 540.0) % 360.0 - 180.0
    return _norm360(a + diff / 2.0)


def _positions_from_chart(chart: Dict[str, Any]) -> Dict[str, float]:
    positions: Dict[str, float] = {}
    planets = chart.get("planets") or {}
    for name, data in planets.items():
        if not isinstance(data, dict):
            continue
        lon = data.get("longitude")
        if lon is None:
            continue
        key = PLANET_KEY_MAP.get(str(name).strip().lower(), str(name).strip().lower())
        positions[key] = float(lon)

    angles = chart.get("angles") or {}
    asc = angles.get("ascendant")
    mc = angles.get("midheaven")
    if asc is not None:
        positions["asc"] = float(asc)
    if mc is not None:
        positions["mc"] = float(mc)

    return positions


def _build_partner_chart(partner: Dict[str, Any]) -> Dict[str, Any]:
    chart_payload = partner.get("chart") if isinstance(partner.get("chart"), dict) else None
    if chart_payload and "positions" in chart_payload:
        raise ValueError("positions are not allowed; provide birth_date, birth_time, birth_place instead.")
    return build_natal_chart(partner)


def _build_formatted_partner(chart: Dict[str, Any]) -> Dict[str, Any]:
    planet_list = []
    planets = chart.get("planets") or {}
    for raw_name, data in planets.items():
        if not isinstance(data, dict):
            continue
        lon = data.get("longitude")
        if lon is None:
            continue
        name = PLANET_KEY_MAP.get(str(raw_name).strip().lower(), str(raw_name).strip().lower())
        lonf = float(lon)
        sign, deg = _sign_deg(lonf)
        house = data.get("house")
        if house is None:
            house = _planet_house_from_chart(chart, lonf)
        planet_list.append(
            {
                "body": name,
                "longitude": lonf,
                "sign": sign,
                "deg_in_sign": deg,
                "formatted": _format_lon(lonf),
                "house": int(house) if house is not None else None,
            }
        )

    angles = chart.get("angles") or {}
    asc = angles.get("ascendant")
    mc = angles.get("midheaven")
    angle_list = []
    if asc is not None:
        angle_list.append({"body": "asc", "longitude": float(asc), "formatted": _format_lon(float(asc))})
    if mc is not None:
        angle_list.append({"body": "mc", "longitude": float(mc), "formatted": _format_lon(float(mc))})

    cusps = _extract_house_cusps(chart)
    house_list = []
    if cusps:
        house_list = [
            {"house": i + 1, "longitude": float(c), "formatted": _format_lon(float(c))}
            for i, c in enumerate(cusps)
        ]

    return {"planets": planet_list, "angles": angle_list, "houses": house_list}


def _build_overlays(chart_a: Dict[str, Any], chart_b: Dict[str, Any]) -> Dict[str, Any]:
    cusps_a = _extract_house_cusps(chart_a)
    cusps_b = _extract_house_cusps(chart_b)

    def planet_lon_map(chart: Dict[str, Any]) -> Dict[str, float]:
        out = {}
        for raw_name, data in (chart.get("planets") or {}).items():
            if not isinstance(data, dict):
                continue
            lon = data.get("longitude")
            if lon is None:
                continue
            name = PLANET_KEY_MAP.get(str(raw_name).strip().lower(), str(raw_name).strip().lower())
            out[name] = float(lon)
        angles = chart.get("angles") or {}
        if angles.get("ascendant") is not None:
            out["asc"] = float(angles["ascendant"])
        if angles.get("midheaven") is not None:
            out["mc"] = float(angles["midheaven"])
        return out

    amap = planet_lon_map(chart_a)
    bmap = planet_lon_map(chart_b)

    def overlay(map_src: Dict[str, float], cusps_dst: Optional[List[float]]) -> Dict[str, Any]:
        if not cusps_dst:
            return {"by_body": {}, "table": []}
        by_body = {}
        table = []
        for body, lon in map_src.items():
            h = _house_from_cusps(lon, cusps_dst)
            by_body[body] = int(h)
            table.append(
                {
                    "body": body,
                    "longitude": lon,
                    "formatted": _format_lon(lon),
                    "in_house": int(h),
                }
            )
        return {"by_body": by_body, "table": table}

    overlays = {
        "a_in_b": overlay(amap, cusps_b),
        "b_in_a": overlay(bmap, cusps_a),
    }

    angles_a = chart_a.get("angles") or {}
    angles_b = chart_b.get("angles") or {}
    sun_a = (chart_a.get("planets") or {}).get("Sun") or (chart_a.get("planets") or {}).get("sun")
    moon_a = (chart_a.get("planets") or {}).get("Moon") or (chart_a.get("planets") or {}).get("moon")
    sun_b = (chart_b.get("planets") or {}).get("Sun") or (chart_b.get("planets") or {}).get("sun")
    moon_b = (chart_b.get("planets") or {}).get("Moon") or (chart_b.get("planets") or {}).get("moon")

    def _lon_from_obj(obj: Any) -> Optional[float]:
        if isinstance(obj, dict) and obj.get("longitude") is not None:
            return float(obj["longitude"])
        return None

    mp = {"partner_a": {}, "partner_b": {}}
    if angles_a.get("ascendant") is not None and angles_a.get("midheaven") is not None:
        m = _midpoint(float(angles_a["ascendant"]), float(angles_a["midheaven"]))
        mp["partner_a"]["asc_mc"] = {"longitude": m, "formatted": _format_lon(m)}
    if angles_b.get("ascendant") is not None and angles_b.get("midheaven") is not None:
        m = _midpoint(float(angles_b["ascendant"]), float(angles_b["midheaven"]))
        mp["partner_b"]["asc_mc"] = {"longitude": m, "formatted": _format_lon(m)}
    s_a = _lon_from_obj(sun_a)
    m_a = _lon_from_obj(moon_a)
    s_b = _lon_from_obj(sun_b)
    m_b = _lon_from_obj(moon_b)
    if s_a is not None and m_a is not None:
        x = _midpoint(s_a, m_a)
        mp["partner_a"]["sun_moon"] = {"longitude": x, "formatted": _format_lon(x)}
    if s_b is not None and m_b is not None:
        x = _midpoint(s_b, m_b)
        mp["partner_b"]["sun_moon"] = {"longitude": x, "formatted": _format_lon(x)}

    overlays["midpoints"] = mp
    return overlays


def _first_non_empty(values: List[Any]) -> Optional[str]:
    for v in values:
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _name_from_profile(profile: Any) -> Optional[str]:
    if not isinstance(profile, dict):
        return None
    first = profile.get("firstName") or profile.get("first_name")
    last = profile.get("lastName") or profile.get("last_name")
    display = profile.get("displayName") or profile.get("display_name")
    full = profile.get("fullName") or profile.get("full_name")
    direct = profile.get("name")
    preferred = _first_non_empty([display, full, direct])
    if preferred:
        return preferred
    if first and last:
        return f"{first} {last}".strip()
    return _first_non_empty([first, last])


def _extract_partner_name(payload: Dict[str, Any], partner: Dict[str, Any], key: str) -> Optional[str]:
    return _first_non_empty(
        [
            payload.get(f"{key}_name"),
            partner.get("name"),
            partner.get("display_name"),
            partner.get("displayName"),
            partner.get("full_name"),
            partner.get("fullName"),
            _name_from_profile(partner.get("profile")),
            _name_from_profile(payload.get(f"{key}_profile")),
            _name_from_profile(payload.get("profile")),
            _name_from_profile(payload.get("user_profile")),
        ]
    )


def analyze_synastry(payload: Dict[str, Any]) -> Dict[str, Any]:
    partner_a = payload.get("partner_a") or {}
    partner_b = payload.get("partner_b") or {}
    options = payload.get("options") or {}
    include_debug = bool(options.get("include_debug"))

    chart_a = _build_partner_chart(partner_a)
    chart_b = _build_partner_chart(partner_b)
    A_pos = _positions_from_chart(chart_a)
    B_pos = _positions_from_chart(chart_b)

    bodies = options.get("bodies", DEFAULT_BODIES)
    if bodies:
        bodies = [str(b).strip().lower() for b in bodies]

    res = engine.score(
        A_pos=A_pos,
        B_pos=B_pos,
        overlay_bonus=None,
        resonance=None,
        include_debug=include_debug,
        bodies=bodies,
    )

    public = {
        "scores": {
            "bond": round(res.categories["bond"].total * 100),
            "depth": round(res.categories["depth"].total * 100),
            "spark": round(res.categories["spark"].total * 100),
            "freedom": round(res.categories["freedom"].total * 100),
            "risk_index": round(res.risk_index * 100),
            "confidence": round(res.confidence * 100),
        },
        "drivers": {
            c: res.categories[c].top_drivers for c in ("bond", "depth", "spark", "freedom")
        },
        "formatted": {
            "partner_a": _build_formatted_partner(chart_a),
            "partner_b": _build_formatted_partner(chart_b),
        },
        "overlays": _build_overlays(chart_a, chart_b),
    }

    out: Dict[str, Any] = {"engine_version": res.meta["engine"], "public": public}

    if include_debug:
        out["debug"] = res.debug

    partner_a_name = _extract_partner_name(payload, partner_a, "partner_a")
    partner_b_name = _extract_partner_name(payload, partner_b, "partner_b")
    return build_synastry_public(out, partner_a_name, partner_b_name)
