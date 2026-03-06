from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence, Tuple

from app.transit.astro.rulership import ruler_of, ruler_of_lower

ASPECT_TARGETS = {
    "conjunction": 0.0,
    "opposition": 180.0,
    "square": 90.0,
    "trine": 120.0,
    "sextile": 60.0,
}

ASPECT_ORBS = {
    "conjunction": 8.0,
    "opposition": 8.0,
    "square": 7.0,
    "trine": 7.0,
    "sextile": 5.0,
}

HOUSE_LABEL_TR = {
    1: "kimlik/benlik",
    2: "deger/gelir",
    3: "zihin/iletisim",
    4: "ev/kok",
    5: "yaraticilik/ifade",
    6: "rutin/saglik",
    7: "iliski/ortaklik",
    8: "derin_bag/donusum",
    9: "anlam/ufuk/genisleme",
    10: "kariyer/gorunurluk",
    11: "topluluk/hedef",
    12: "bilincalti/cozulme",
}

SIGN_LABEL_TR = {
    "aries": "Koç",
    "taurus": "Boğa",
    "gemini": "İkizler",
    "cancer": "Yengeç",
    "leo": "Aslan",
    "virgo": "Başak",
    "libra": "Terazi",
    "scorpio": "Akrep",
    "sagittarius": "Yay",
    "capricorn": "Oğlak",
    "aquarius": "Kova",
    "pisces": "Balık",
}

ANGLE_HOUSES = {"ASC": 1, "IC": 4, "DSC": 7, "MC": 10}
ANGLE_KEYS = set(ANGLE_HOUSES.keys())
PLANET_ALLOW = {
    "sun",
    "moon",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
    "asc",
    "dsc",
    "mc",
    "ic",
}

NODE_BLOCK = {"south node", "north node", "lilith", "vertex", "fortune", "chiron"}


def build_hybrid_event_context(
    event: Mapping[str, Any],
    natal: Mapping[str, Any] | None,
    natal_promise: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    natal_map = natal if isinstance(natal, Mapping) else {}
    bodies = natal_map.get("bodies") if isinstance(natal_map.get("bodies"), list) else []
    cusps = natal_map.get("house_cusps") if isinstance(natal_map.get("house_cusps"), list) else []
    angles = natal_map.get("angles") if isinstance(natal_map.get("angles"), Mapping) else {}
    body_map = _index_bodies(bodies)
    if not body_map or not cusps:
        return {"connected_points": [], "natal_context_pack": {}, "derived_context": {}}

    house_rulers = _build_house_rulers(cusps)
    target_planet = _resolve_target_planet(event, body_map, house_rulers)
    if not target_planet:
        return {"connected_points": [], "natal_context_pack": {}, "derived_context": {}}

    is_angle_target = target_planet.upper() in ANGLE_KEYS
    angle_ruler = ""
    if is_angle_target:
        angle_key = target_planet.upper()
        angle_entry = angles.get(angle_key) if isinstance(angles, Mapping) else {}
        target_house = ANGLE_HOUSES[angle_key]
        target_sign = str((angle_entry or {}).get("sign") or (house_rulers.get(target_house) or {}).get("sign") or "").strip()
        target_sign_l = target_sign.lower()
        angle_ruler = _resolve_angle_ruler(angle_key, house_rulers, body_map)
        dispositor = {}
        rulership_houses = []
        natal_aspects = []
    else:
        target_info = body_map.get(target_planet.lower(), {})
        target_house = _safe_int(target_info.get("house"))
        target_sign = str(target_info.get("sign") or "").strip()
        target_sign_l = target_sign.lower()
        dispositor = _resolve_dispositor(target_sign_l, body_map)
        rulership_houses = _rulership_houses(target_planet, house_rulers)
        natal_aspects = _natal_aspects_focus(target_planet, natal_map, bodies)

    pack = {
        "target": {
            "planet": target_planet,
            "sign": target_sign,
            "sign_tr": SIGN_LABEL_TR.get(target_sign_l, target_sign),
            "house": target_house,
        },
        "dispositor": dispositor,
        "rulership_houses": rulership_houses,
        "natal_aspects_focus": natal_aspects,
    }
    if angle_ruler:
        pack["angle_ruler"] = angle_ruler

    points = _connected_points_v2(
        event=event,
        target_planet=target_planet,
        target_house=target_house,
        target_sign=target_sign_l,
        dispositor=dispositor,
        rulership_houses=rulership_houses,
        natal_aspects=natal_aspects,
        natal_promise=natal_promise,
        angles=angles,
        angle_ruler=angle_ruler,
    )
    derived_context = _build_derived_context(
        event=event,
        target_planet=target_planet,
        target_house=target_house,
        target_sign=target_sign,
        dispositor=dispositor,
        rulership_houses=rulership_houses,
        points=points,
        angle_ruler=angle_ruler,
        house_rulers=house_rulers,
        body_map=body_map,
    )
    return {"connected_points": points, "natal_context_pack": pack, "derived_context": derived_context}


def _build_derived_context(
    *,
    event: Mapping[str, Any],
    target_planet: str,
    target_house: int | None,
    target_sign: str,
    dispositor: Mapping[str, Any],
    rulership_houses: Sequence[Mapping[str, Any]],
    points: Sequence[Mapping[str, Any]],
    angle_ruler: str,
    house_rulers: Mapping[int, Mapping[str, Any]],
    body_map: Mapping[str, Mapping[str, Any]],
) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    target_upper = target_planet.upper()
    if target_upper in ANGLE_KEYS:
        house = ANGLE_HOUSES.get(target_upper)
        sign = str((house_rulers.get(house or -1) or {}).get("sign") or "").strip().title()
        ruler = ruler_of(sign) or angle_ruler or str((house_rulers.get(house or -1) or {}).get("ruler") or "").title()
        ruler_entry = body_map.get(ruler.lower(), {}) if ruler else {}
        out["angle"] = {
            "name": target_upper,
            "sign": sign,
            "ruler": ruler,
            "ruler_house": _safe_int(ruler_entry.get("house")),
            "ruler_sign": str(ruler_entry.get("sign") or "").strip().title(),
        }
    out["natal_target"] = {
        "name": target_planet,
        "house": target_house,
        "sign": str(target_sign or "").strip().title(),
        "dispositor": str(dispositor.get("planet") or "").strip() or None,
        "rulership_houses": [int(x.get("house")) for x in rulership_houses if _safe_int(x.get("house"))],
    }
    out["connected_points"] = [_point_to_connected(p) for p in list(points)[:4] if isinstance(p, Mapping)]
    links: List[Dict[str, Any]] = []
    if target_upper in ANGLE_KEYS and angle_ruler:
        links.append(
            {
                "type": "angle_ruler_resonance",
                "target": angle_ruler,
                "because": f"{target_upper} ruler",
            }
        )
    out["links"] = links
    out["motifs"] = _derive_motifs(out.get("connected_points") if isinstance(out.get("connected_points"), list) else [])
    out["derived_domains"] = _derive_domains_from_house(target_house)
    return out


def _point_to_connected(point: Mapping[str, Any]) -> Dict[str, Any]:
    kind = str(point.get("kind") or "").strip().lower()
    value = point.get("value")
    label = str(point.get("label_tr") or "").strip()
    score = round(_safe_float(point.get("score"), 0.0), 3)
    if kind == "house":
        return {"type": "target_house", "label_tr": label or f"{value}. Ev", "score": score}
    if kind == "sign":
        return {"type": "target_sign", "label_tr": label or str(value), "score": score}
    if kind in {"rulership_house", "dispositor", "angle_ruler"}:
        return {"type": "rulership", "label_tr": label or str(value), "score": score}
    return {"type": kind or "point", "label_tr": label or str(value), "score": score}


def _derive_motifs(points: Sequence[Mapping[str, Any]]) -> List[str]:
    motifs: List[str] = []
    labels = " ".join(str(p.get("label_tr") or "").lower() for p in points)
    if "zihin" in labels or "iletisim" in labels:
        motifs.extend(["yazılı netlik", "ton ayarı"])
    if "ufuk" in labels or "anlam" in labels:
        motifs.extend(["tek sprint", "yeni yöntem"])
    if "iliski" in labels:
        motifs.append("sınır cümlesi")
    dedup: List[str] = []
    for motif in motifs:
        if motif not in dedup:
            dedup.append(motif)
    return dedup[:4]


def _derive_domains_from_house(house: int | None) -> List[Dict[str, Any]]:
    mapping = {
        1: ("identity", 0.55),
        3: ("mind", 0.52),
        4: ("home", 0.5),
        5: ("creativity", 0.47),
        7: ("relationships", 0.55),
        8: ("inner", 0.5),
        9: ("meaning", 0.55),
        10: ("career", 0.58),
        11: ("social", 0.48),
    }
    if house in mapping:
        name, score = mapping[house]
        return [{"domain": name, "score": score}]
    return [{"domain": "identity", "score": 0.35}]


def _connected_points_v2(
    *,
    event: Mapping[str, Any],
    target_planet: str,
    target_house: int | None,
    target_sign: str,
    dispositor: Mapping[str, Any],
    rulership_houses: Sequence[Mapping[str, Any]],
    natal_aspects: Sequence[Mapping[str, Any]],
    natal_promise: Mapping[str, Any] | None,
    angles: Mapping[str, Any],
    angle_ruler: str = "",
) -> List[Dict[str, Any]]:
    phase = str(event.get("phase") or "").lower()
    aspect = str(event.get("aspect") or "").lower()
    angle_boost = 0.9 if str(event.get("natal_point") or "").upper() in ANGLE_KEYS else 1.0
    phase_boost = 1.0 if phase in {"exact", "exactish", "applying"} else 0.85
    aspect_boost = 1.0 if aspect in ASPECT_TARGETS else 0.9
    orb_deg = _safe_float(event.get("orb_deg"), 99.0)
    orb_boost = 1.0 if orb_deg <= 1.0 else 0.92 if orb_deg <= 2.0 else 0.84 if orb_deg <= 4.0 else 0.76
    promise_bonus = 0.0
    if isinstance(natal_promise, Mapping):
        promise_bonus = 0.08 * max(0.0, min(1.0, _safe_float((natal_promise.get("score") or 0.0), 0.0)))
    base = min(1.0, 0.35 + (0.30 * phase_boost) + (0.18 * aspect_boost) + (0.09 * orb_boost) + promise_bonus)

    points: List[Dict[str, Any]] = []

    if isinstance(target_house, int):
        score = min(1.0, base * 0.9 * angle_boost)
        points.append(
            {
                "kind": "house",
                "value": target_house,
                "label_tr": HOUSE_LABEL_TR.get(target_house, "genel"),
                "score": round(score, 3),
            }
        )

    if target_sign and target_sign in SIGN_LABEL_TR:
        score = min(1.0, base * 0.75)
        points.append(
            {
                "kind": "sign",
                "value": target_sign,
                "label_tr": SIGN_LABEL_TR[target_sign],
                "score": round(score, 3),
            }
        )

    disp_planet = str(dispositor.get("planet") or "").strip()
    if disp_planet:
        token = disp_planet.lower()
        if token in PLANET_ALLOW and token not in NODE_BLOCK:
            score = min(1.0, base * 0.72 * aspect_boost)
            points.append(
                {
                    "kind": "dispositor",
                    "value": disp_planet,
                    "label_tr": _planet_tr(disp_planet),
                    "score": round(score, 3),
                }
            )

    for item in natal_aspects[:2]:
        aspect_name = str(item.get("aspect") or "").lower()
        with_planet = str(item.get("with") or "").strip()
        if with_planet.lower() in NODE_BLOCK:
            continue
        score = min(1.0, base * 0.68 * _orb_weight(_safe_float(item.get("orb_deg"), 6.0)))
        points.append(
            {
                "kind": "natal_aspect",
                "value": f"{target_planet} {aspect_name} {with_planet}",
                "label_tr": _aspect_tr(aspect_name),
                "score": round(score, 3),
            }
        )

    for entry in rulership_houses[:2]:
        house = _safe_int(entry.get("house"))
        sign = str(entry.get("sign") or "").lower()
        if not house:
            continue
        score = min(1.0, base * 0.62)
        points.append(
            {
                "kind": "rulership_house",
                "value": house,
                "label_tr": f"{house}. Ev / {SIGN_LABEL_TR.get(sign, sign)}",
                "score": round(score, 3),
            }
        )

    if target_planet.upper() in ANGLE_KEYS and angle_ruler:
        token = angle_ruler.lower()
        if token in PLANET_ALLOW and token not in NODE_BLOCK:
            score = min(1.0, base * 0.70 * angle_boost)
            points.append(
                {
                    "kind": "angle_ruler",
                    "value": angle_ruler,
                    "label_tr": f"{target_planet.upper()} yöneticisi: {_planet_tr(angle_ruler)}",
                    "score": round(score, 3),
                }
            )

    deduped: List[Dict[str, Any]] = []
    seen = set()
    for point in sorted(points, key=lambda x: float(x.get("score") or 0.0), reverse=True):
        key = (point.get("kind"), str(point.get("value")))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(point)
        if len(deduped) >= 6:
            break
    return deduped


def _index_bodies(bodies: Sequence[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for body in bodies:
        name = str(body.get("body") or "").strip()
        if not name:
            continue
        out[name.lower()] = {
            "body": name,
            "sign": str(body.get("sign") or "").strip(),
            "house": body.get("house"),
            "lon": body.get("lon"),
            "rx": bool(body.get("rx") or body.get("retrograde") or False),
        }
    return out


def _build_house_rulers(cusps: Sequence[Mapping[str, Any]]) -> Dict[int, Dict[str, Any]]:
    out: Dict[int, Dict[str, Any]] = {}
    for cusp in cusps:
        house = _safe_int(cusp.get("house"))
        if not house:
            continue
        sign = str(cusp.get("sign") or "").strip().lower()
        fallback_ruler = ruler_of_lower(sign)
        rulers = [fallback_ruler] if fallback_ruler else []
        out[house] = {"house": house, "sign": sign, "rulers": rulers, "ruler": rulers[0] if rulers else ""}
    return out


def _resolve_target_planet(
    event: Mapping[str, Any],
    body_map: Mapping[str, Mapping[str, Any]],
    house_rulers: Mapping[int, Mapping[str, Any]],
) -> str:
    for key in ("natal_point", "natal_body"):
        raw = str(event.get(key) or "").strip()
        up = raw.upper()
        if up in ANGLE_KEYS:
            return up
        low = raw.lower()
        if low in body_map:
            return str(body_map[low].get("body") or raw)
    return ""


def _resolve_angle_ruler(
    angle: str,
    house_rulers: Mapping[int, Mapping[str, Any]],
    body_map: Mapping[str, Mapping[str, Any]],
) -> str:
    house = ANGLE_HOUSES.get(angle.upper())
    if not house:
        return ""
    rulers = (house_rulers.get(house) or {}).get("rulers") or []
    for candidate in rulers:
        if candidate in body_map:
            return str(body_map[candidate].get("body") or candidate.title())
    if rulers:
        return str(rulers[0]).title()
    return ""


def _resolve_dispositor(target_sign: str, body_map: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
    fallback_ruler = ruler_of_lower(target_sign)
    rulers = [fallback_ruler] if fallback_ruler else []
    chosen = ""
    for ruler in rulers:
        if ruler in body_map:
            chosen = ruler
            break
    if not chosen and rulers:
        chosen = rulers[0]
    if not chosen:
        return {}
    body = body_map.get(chosen, {})
    return {
        "planet": str(body.get("body") or chosen.title()),
        "sign": str(body.get("sign") or ""),
        "house": _safe_int(body.get("house")),
        "rx": bool(body.get("rx") or False),
    }


def _rulership_houses(target_planet: str, house_rulers: Mapping[int, Mapping[str, Any]]) -> List[Dict[str, Any]]:
    token = target_planet.lower()
    out: List[Dict[str, Any]] = []
    for house, entry in house_rulers.items():
        rulers = entry.get("rulers") if isinstance(entry.get("rulers"), list) else []
        if token in {str(x).lower() for x in rulers}:
            out.append({"sign": str(entry.get("sign") or ""), "house": int(house)})
    out.sort(key=lambda item: int(item.get("house") or 99))
    return out


def _natal_aspects_focus(
    target_planet: str,
    natal: Mapping[str, Any],
    bodies: Sequence[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    explicit = natal.get("aspects")
    if isinstance(explicit, list):
        parsed = _parse_explicit_aspects(target_planet, explicit)
        if parsed:
            return parsed[:2]

    computed = _compute_natal_aspects(bodies)
    target = target_planet.lower()
    focus = [item for item in computed if item["a"].lower() == target or item["b"].lower() == target]
    focus.sort(key=lambda item: float(item.get("orb_deg") or 99.0))
    output: List[Dict[str, Any]] = []
    for item in focus[:2]:
        other = item["b"] if item["a"].lower() == target else item["a"]
        aspect = str(item["aspect"])
        output.append(
            {
                "aspect": aspect,
                "with": other,
                "orb_deg": round(float(item.get("orb_deg") or 0.0), 2),
                "tone": _tone(aspect, other),
            }
        )
    return output


def _parse_explicit_aspects(target_planet: str, aspects: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    target = target_planet.lower()
    parsed: List[Dict[str, Any]] = []
    for aspect in aspects:
        a = str(aspect.get("a") or aspect.get("p1") or "").strip()
        b = str(aspect.get("b") or aspect.get("p2") or "").strip()
        if not a or not b:
            continue
        if target not in {a.lower(), b.lower()}:
            continue
        asp = str(aspect.get("aspect") or aspect.get("name") or "").strip().lower()
        orb = _safe_float(aspect.get("orb") if "orb" in aspect else aspect.get("orb_deg"), 99.0)
        if asp not in ASPECT_TARGETS:
            continue
        other = b if a.lower() == target else a
        parsed.append(
            {
                "aspect": asp,
                "with": other,
                "orb_deg": round(orb, 2),
                "tone": _tone(asp, other),
            }
        )
    parsed.sort(key=lambda item: float(item.get("orb_deg") or 99.0))
    return parsed[:2]


def _compute_natal_aspects(bodies: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    points: List[Tuple[str, float]] = []
    for body in bodies:
        name = str(body.get("body") or "").strip()
        lon = body.get("lon")
        if not name or not isinstance(lon, (int, float)):
            continue
        points.append((name, float(lon)))
    out: List[Dict[str, Any]] = []
    for idx, (a, a_lon) in enumerate(points):
        for b, b_lon in points[idx + 1 :]:
            diff = _angle_diff(a_lon, b_lon)
            for aspect, target in ASPECT_TARGETS.items():
                orb = abs(diff - target)
                if orb <= ASPECT_ORBS[aspect]:
                    out.append({"a": a, "b": b, "aspect": aspect, "orb_deg": orb})
                    break
    return out


def _angle_diff(a: float, b: float) -> float:
    diff = abs((a - b) % 360.0)
    return 360.0 - diff if diff > 180.0 else diff


def _aspect_tr(name: str) -> str:
    mapping = {
        "conjunction": "kavusum",
        "square": "kare",
        "opposition": "karsit",
        "trine": "ucgen",
        "sextile": "altmislik",
    }
    return mapping.get(name, name)


def _tone(aspect: str, other: str) -> str:
    if other.lower() == "uranus":
        return "electric"
    if aspect in {"square", "opposition"}:
        return "friction"
    if aspect in {"trine", "sextile"}:
        return "flow"
    return "focus"


def _planet_tr(name: str) -> str:
    mapping = {
        "sun": "Güneş",
        "moon": "Ay",
        "mercury": "Merkür",
        "venus": "Venüs",
        "mars": "Mars",
        "jupiter": "Jüpiter",
        "saturn": "Satürn",
        "uranus": "Uranüs",
        "neptune": "Neptün",
        "pluto": "Plüton",
    }
    token = str(name or "").strip().lower()
    return mapping.get(token, str(name or ""))


def _orb_weight(orb: float) -> float:
    if orb <= 1.0:
        return 1.0
    if orb <= 2.0:
        return 0.9
    if orb <= 4.0:
        return 0.8
    return 0.65


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
