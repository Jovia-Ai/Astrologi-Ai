from dataclasses import asdict
from typing import Any, Dict, List, Optional, Tuple
import math

from app.astro.chart_engine.builder import build_natal_chart
from app.astro.synastry.engine_v1 import SynastryEngineV1
from app.natal.natal_graph_v2 import build_natal_graph_v2
from app.synastry.activation_engine import synastry_hit_to_partner_activation
from app.synastry.narrative.synastry_imprint_engine import build_synastry_imprint
from app.synastry.narrative.synastry_narrative_engine import build_synastry_narrative
from app.synastry.public_builder import build_synastry_public
from app.synastry.resonance_engine import (
    bridge_bonus_for_public_scores,
    build_activation_bundles,
    build_asymmetry_notes,
    build_narrative_ready_summary,
    build_overlay_cluster_summary,
    build_relationship_calibration,
    build_relational_modes,
    compute_directional_asymmetry,
    compute_familiarity_resonance,
    compute_growth_tension,
    compute_magnetic_intensity,
    compute_mutuality,
    compute_promise_alignment_breakdown,
    compute_sustainable_bond,
    compute_trigger_load,
    expand_activation_records,
    rank_partner_domains,
)

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
    "juno",
    "node",
    "vertex",
    "asc",
    "mc",
]

engine = SynastryEngineV1()

PLANET_KEY_MAP = {
    "north node": "node",
    "vertex": "vertex",
    "juno": "juno",
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


def _build_partner_activation_records(
    for_partner: str,
    overlay_table: List[Dict[str, Any]],
    overlay_by_body: Dict[str, Any],
    aspect_hits: List[Dict[str, Any]],
    natal_graph_v2: Dict[str, Any],
) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    overlay_lookup = {str(item.get("body") or ""): item for item in overlay_table if isinstance(item, dict)}

    for row in overlay_table:
        record = synastry_hit_to_partner_activation(None, row, natal_graph_v2)
        if record:
            records.append(record)

    for hit in aspect_hits:
        if for_partner == "a":
            incoming_body = str(hit.get("b_body") or "")
            native_body = str(hit.get("a_body") or "")
        else:
            incoming_body = str(hit.get("a_body") or "")
            native_body = str(hit.get("b_body") or "")
        house = overlay_by_body.get(incoming_body)
        overlay_info = dict(overlay_lookup.get(incoming_body) or {})
        overlay_info["incoming_body"] = incoming_body
        overlay_info["native_body"] = native_body
        overlay_info["in_house"] = house if house is not None else overlay_info.get("in_house")
        hit_payload = dict(hit)
        hit_payload["incoming_body"] = incoming_body
        hit_payload["native_body"] = native_body
        record = synastry_hit_to_partner_activation(hit_payload, overlay_info, natal_graph_v2)
        if record:
            records.append(record)

    return records


def _normalize_base_relationship_scores(res: Any) -> Dict[str, float]:
    return {
        "bond": float(res.categories["bond"].total or 0.0),
        "depth": float(res.categories["depth"].total or 0.0),
        "spark": float(res.categories["spark"].total or 0.0),
        "freedom": float(res.categories["freedom"].total or 0.0),
        "risk_index": float(res.risk_index or 0.0),
        "confidence": float(res.confidence or 0.0),
    }


def _to_percent_map(scores: Dict[str, float]) -> Dict[str, int]:
    return {key: round(float(value or 0.0) * 100) for key, value in scores.items()}


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

    aspect_hits = [asdict(hit) for hit in engine.scan_aspects(A_pos=A_pos, B_pos=B_pos, bodies=bodies)]
    res = engine.score(
        A_pos=A_pos,
        B_pos=B_pos,
        overlay_bonus=None,
        resonance=None,
        include_debug=include_debug,
        bodies=bodies,
    )
    overlays = _build_overlays(chart_a, chart_b)
    natal_graph_a = build_natal_graph_v2(chart_a)
    natal_graph_b = build_natal_graph_v2(chart_b)

    partner_a_name = _extract_partner_name(payload, partner_a, "partner_a") or "Partner A"
    partner_b_name = _extract_partner_name(payload, partner_b, "partner_b") or "Partner B"

    partner_a_records = _build_partner_activation_records(
        for_partner="a",
        overlay_table=list((overlays.get("b_in_a") or {}).get("table") or []),
        overlay_by_body=dict((overlays.get("b_in_a") or {}).get("by_body") or {}),
        aspect_hits=aspect_hits,
        natal_graph_v2=natal_graph_a,
    )
    partner_b_records = _build_partner_activation_records(
        for_partner="b",
        overlay_table=list((overlays.get("a_in_b") or {}).get("table") or []),
        overlay_by_body=dict((overlays.get("a_in_b") or {}).get("by_body") or {}),
        aspect_hits=aspect_hits,
        natal_graph_v2=natal_graph_b,
    )

    partner_a_hits = expand_activation_records(partner_a_records, natal_graph_a, for_partner="a")
    partner_b_hits = expand_activation_records(partner_b_records, natal_graph_b, for_partner="b")
    promise_alignment_breakdown = {
        "partner_a": compute_promise_alignment_breakdown(partner_a_hits, natal_graph_a),
        "partner_b": compute_promise_alignment_breakdown(partner_b_hits, natal_graph_b),
    }
    base_scores = _normalize_base_relationship_scores(res)
    overlay_cluster_summary = build_overlay_cluster_summary(overlays)
    activation_bundles = build_activation_bundles(
        resonance_hits={
            "partner_a": partner_a_hits,
            "partner_b": partner_b_hits,
        },
        overlay_cluster_summary=overlay_cluster_summary,
        natal_graph_v2={
            "partner_a": natal_graph_a,
            "partner_b": natal_graph_b,
        },
    )
    domain_rankings = rank_partner_domains(activation_bundles)

    partner_a_resonance = {
        "familiarity_resonance": compute_familiarity_resonance(partner_a_hits, natal_graph_a),
        "promise_alignment": promise_alignment_breakdown["partner_a"]["score"],
        "growth_tension": compute_growth_tension(partner_a_hits, natal_graph_a),
        "trigger_load": compute_trigger_load(partner_a_hits, natal_graph_a),
    }
    partner_b_resonance = {
        "familiarity_resonance": compute_familiarity_resonance(partner_b_hits, natal_graph_b),
        "promise_alignment": promise_alignment_breakdown["partner_b"]["score"],
        "growth_tension": compute_growth_tension(partner_b_hits, natal_graph_b),
        "trigger_load": compute_trigger_load(partner_b_hits, natal_graph_b),
    }
    partner_a_context = [
        {
            "domain": row["domain"],
            "score": row["score"],
            "because": list(row.get("because") or [])[:5],
        }
        for row in list(domain_rankings.get("partner_a") or [])[:3]
    ]
    partner_b_context = [
        {
            "domain": row["domain"],
            "score": row["score"],
            "because": list(row.get("because") or [])[:5],
        }
        for row in list(domain_rankings.get("partner_b") or [])[:3]
    ]
    relationship_resonance = {
        "mutuality": compute_mutuality(partner_a_resonance, partner_b_resonance),
        "asymmetry": 0.0,
        "magnetic_intensity": compute_magnetic_intensity(
            base_scores,
            partner_a_resonance,
            partner_b_resonance,
        ),
    }
    resonance_scores = {
        "partner_a": partner_a_resonance,
        "partner_b": partner_b_resonance,
        "relationship": relationship_resonance,
    }
    resonance_scores["relationship"]["sustainable_bond"] = compute_sustainable_bond(
        base_scores,
        resonance_scores,
    )
    relational_modes = build_relational_modes(resonance_scores, promise_alignment_breakdown)
    resonance_scores["relationship"]["asymmetry"] = compute_directional_asymmetry(
        resonance_scores=resonance_scores,
        overlay_cluster_summary=overlay_cluster_summary,
        domain_rankings=domain_rankings,
    )
    public_score_bridge = bridge_bonus_for_public_scores(
        base_scores=base_scores,
        resonance_scores=resonance_scores,
        partner_hits={
            "a": partner_a_hits,
            "b": partner_b_hits,
        },
        overlays=overlays,
        aspect_hits=aspect_hits,
        bundles_by_partner=activation_bundles,
    )
    corrected_score_context = dict(public_score_bridge["scores"])
    corrected_score_context["mutuality"] = resonance_scores["relationship"]["mutuality"]
    corrected_score_context["sustainable_bond"] = resonance_scores["relationship"]["sustainable_bond"]
    relationship_calibration = build_relationship_calibration(
        corrected_scores=corrected_score_context,
        resonance_scores=resonance_scores,
        relational_modes=relational_modes,
        asymmetry=resonance_scores["relationship"]["asymmetry"],
    )
    narrative_ready = build_narrative_ready_summary(
        bundles_by_partner=activation_bundles,
        domain_rankings=domain_rankings,
        relational_modes=relational_modes,
        corrected_scores=corrected_score_context,
        asymmetry=resonance_scores["relationship"]["asymmetry"],
        overlay_cluster_summary=overlay_cluster_summary,
    )
    narrative_payload = build_synastry_narrative(
        partner_a_name=partner_a_name,
        partner_b_name=partner_b_name,
        activation_bundles=activation_bundles,
        domain_rankings=domain_rankings,
        relational_modes=relational_modes,
        resonance_scores=resonance_scores,
        corrected_scores=public_score_bridge["scores"],
        narrative_ready=narrative_ready,
    )
    imprint_payload = build_synastry_imprint(
        partner_a_name=partner_a_name,
        partner_b_name=partner_b_name,
        aspect_hits=aspect_hits,
        overlays=overlays,
        domain_rankings=domain_rankings,
        activation_bundles=activation_bundles,
        corrected_scores=public_score_bridge["scores"],
        relationship_calibration=relationship_calibration,
    )

    public = {
        "scores": _to_percent_map(public_score_bridge["scores"]),
        "raw_scores": _to_percent_map(public_score_bridge["public_score_bridge_debug"]["base_scores"]),
        "contextual_scores": _to_percent_map(public_score_bridge["scores"]),
        "drivers": {
            "bond": list(public_score_bridge.get("drivers", {}).get("bond") or []),
            "depth": list(public_score_bridge.get("drivers", {}).get("depth") or []),
            "risk_index": list(public_score_bridge.get("drivers", {}).get("risk_index") or []),
            "spark": res.categories["spark"].top_drivers,
            "freedom": res.categories["freedom"].top_drivers,
        },
        "formatted": {
            "partner_a": _build_formatted_partner(chart_a),
            "partner_b": _build_formatted_partner(chart_b),
        },
        "overlays": overlays,
        "resonance_scores": {
            "partner_a": _to_percent_map(partner_a_resonance),
            "partner_b": _to_percent_map(partner_b_resonance),
            "relationship": _to_percent_map(resonance_scores["relationship"]),
        },
        "domain_rankings": domain_rankings,
        "relational_modes": relational_modes,
        "derived_context": {
            "partner_a_activated": partner_a_context,
            "partner_b_activated": partner_b_context,
            "asymmetry_notes": build_asymmetry_notes(
                partner_a_context,
                partner_b_context,
                partner_a_name,
                partner_b_name,
                resonance_scores["relationship"]["asymmetry"],
            ),
            "meaning_summaries": {
                "partner_a": str((narrative_ready.get("partner_a_story") or {}).get("summary_line") or ""),
                "partner_b": str((narrative_ready.get("partner_b_story") or {}).get("summary_line") or ""),
                "relationship": str((narrative_ready.get("relationship_shape") or {}).get("summary_line") or ""),
            },
        },
        "narrative_ready": narrative_ready,
        "narrative": narrative_payload["public"],
    }
    if isinstance(imprint_payload.get("public"), dict):
        public["synastry_imprint"] = imprint_payload["public"]

    out: Dict[str, Any] = {"engine_version": res.meta["engine"], "public": public}

    if include_debug:
        debug_payload = dict(res.debug or {})
        debug_payload["natal_graph_v2"] = {
            "partner_a": natal_graph_a,
            "partner_b": natal_graph_b,
        }
        debug_payload["resonance_hits"] = (partner_a_hits + partner_b_hits)[:160]
        debug_payload["overlay_cluster_summary"] = overlay_cluster_summary
        debug_payload["activation_bundles"] = activation_bundles
        debug_payload["domain_rankings"] = domain_rankings
        debug_payload["relational_modes"] = relational_modes
        debug_payload["relationship_calibration"] = relationship_calibration
        debug_payload["narrative_ready"] = narrative_ready
        debug_payload["narrative_debug"] = narrative_payload["debug"]
        debug_payload["public_score_bridge_debug"] = public_score_bridge["public_score_bridge_debug"]
        debug_payload["promise_alignment_breakdown"] = promise_alignment_breakdown
        if isinstance(imprint_payload.get("internal"), dict):
            debug_payload["synastry_imprint_internal"] = imprint_payload["internal"]
        out["debug"] = debug_payload

    return build_synastry_public(out, partner_a_name, partner_b_name)
