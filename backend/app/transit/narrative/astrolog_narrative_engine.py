from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple
import hashlib

from app.transit.narrative import phrase_lib_tr
from app.transit.narrative import text_quality_tr

TRACK_IDS = {
    "identity_spine",
    "method_shift_9_virgo",
    "network_transform_11",
    "mirror_axis_1_7",
    "default",
}
ANGLE_POINTS = {"ASC", "DSC", "MC", "IC"}

RULERS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

HOUSE_THEME_TR: Dict[int, str] = {
    1: "kimlik ve duruş",
    2: "değer ve kaynaklar",
    3: "zihin ve iletişim",
    4: "temel düzen ve güven",
    5: "yaratıcılık ve ifade",
    6: "günlük ritim ve emek",
    7: "ilişkiler ve sözleşme",
    8: "derin bağlar ve güven",
    9: "ufuk, öğrenme ve yön",
    10: "kariyer yönü ve görünürlük",
    11: "topluluk, network ve hedefler",
    12: "iç dünya ve bırakış",
}

ANGLE_TO_CUSP_HOUSE = {"ASC": 1, "DSC": 7, "MC": 10, "IC": 4}


@dataclass(frozen=True)
class PeriodStoryContext:
    period_core: Dict[str, Any]
    chart_snapshot: Dict[str, Any]
    natal_promise: Dict[str, Any]
    locale: str = "tr"
    enable_fun: bool = True


@dataclass(frozen=True)
class PeriodNarrative:
    big_picture: str
    mechanism: str
    upper_meaning: str
    debug: Dict[str, Any]


def infer_story_track_id(
    card: Mapping[str, Any],
    period_root_causes: Optional[Sequence[Mapping[str, Any]]] = None,
) -> str:
    event_id = str(card.get("event_id") or "").strip()
    if period_root_causes and event_id:
        best_key = ""
        best_score = -1.0
        for rc in period_root_causes:
            key = str(rc.get("key") or "").strip()
            if key not in TRACK_IDS:
                continue
            score = _safe_float(rc.get("score"), 0.0)
            evidence = rc.get("evidence") if isinstance(rc.get("evidence"), Sequence) else []
            evidence_tokens = {str(x).strip() for x in evidence}
            if event_id in evidence_tokens and score > best_score:
                best_key = key
                best_score = score
        if best_key:
            return best_key

    transit_body = str(card.get("transit_body") or "").strip().lower()
    aspect = str(card.get("aspect") or "").strip().lower()
    target = str(card.get("natal_point") or "").strip().upper()

    if target == "DSC":
        return "mirror_axis_1_7"
    if transit_body == "neptune" and target in ANGLE_POINTS and aspect in {"square", "opposition"}:
        return "identity_spine" if target == "ASC" else "mirror_axis_1_7"
    if transit_body == "uranus":
        return "method_shift_9_virgo"
    if transit_body == "pluto" or target == "PLUTO":
        return "network_transform_11"
    return "default"


def build_story_track_copy(track_id: str, card: Mapping[str, Any]) -> Dict[str, Any]:
    packs = getattr(phrase_lib_tr, "PERIOD_TRACK_COPY_TR", {})
    pack = packs.get(track_id) or packs.get("default") or {}
    seed = str(card.get("event_id") or track_id)

    vars_map = {
        "planet_hook": _build_planet_hook_tr(
            transit_body=str(card.get("transit_body") or ""),
            aspect=str(card.get("aspect") or ""),
            target=str(card.get("natal_point") or ""),
        ),
        "spine_label": str(card.get("signature_tr") or card.get("signature") or "").strip(),
        "start_house_tr": HOUSE_THEME_TR.get(_safe_int((card.get("scene") or {}).get("start_house")) or 3, ""),
        "outcome_house_tr": HOUSE_THEME_TR.get(_safe_int((card.get("scene") or {}).get("outcome_house")) or 1, ""),
    }

    lead = _render_track_variant(pack.get("lead"), seed, "lead", vars_map)
    big = _render_track_variant(pack.get("big_picture"), seed, "big", vars_map)
    mech = _render_track_variant(pack.get("mechanism"), seed, "mech", vars_map)
    cont = _render_track_variant(pack.get("contribution"), seed, "cont", vars_map)

    return {
        "track_id": track_id,
        "version": str(pack.get("version") or "period_story_v1"),
        "lead": _final_polish_tr(lead),
        "big_picture": _final_polish_tr(big),
        "mechanism": _final_polish_tr(mech),
        "contribution": _final_polish_tr(cont),
        "upper_meaning": _final_polish_tr(cont),
    }


def build_period_story(ctx: PeriodStoryContext) -> PeriodNarrative:
    spine, supports = _select_spine_and_supports(ctx.period_core)

    big_picture = _build_big_picture(ctx, spine, supports)
    mechanism = _build_chain_paragraph(ctx, spine, supports)
    upper = _build_upper_meaning(ctx, spine, supports)

    return PeriodNarrative(
        big_picture=_final_polish_tr(big_picture),
        mechanism=_final_polish_tr(mechanism),
        upper_meaning=_final_polish_tr(upper),
        debug={
            "spine_event_id": str(spine.get("event_id") or ""),
            "support_event_ids": [str(e.get("event_id") or "") for e in supports],
        },
    )


def _select_spine_and_supports(period_core: Mapping[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    events_raw = (
        period_core.get("featured_events")
        or period_core.get("events")
        or period_core.get("items")
        or []
    )
    events = [dict(e) for e in events_raw if isinstance(e, Mapping)]
    if not events:
        return ({}, [])

    def rank_key(e: Mapping[str, Any]) -> Tuple[float, float, int, int]:
        strength = _safe_float(e.get("strength"), 0.0)
        orb = _safe_float(e.get("orb_deg"), 999.0)
        bucket = str(e.get("bucket") or "").lower()
        phase = str(e.get("phase") or "").lower()
        bucket_score = 2 if bucket == "long" else (1 if bucket == "medium" else 0)
        phase_score = 2 if phase in {"exact", "exactish"} else (1 if phase == "applying" else 0)
        return (strength, -orb, bucket_score, phase_score)

    sorted_events = sorted(events, key=rank_key, reverse=True)
    return (sorted_events[0], sorted_events[1:3])


def _build_big_picture(
    ctx: PeriodStoryContext,
    spine: Mapping[str, Any],
    supports: Sequence[Mapping[str, Any]],
) -> str:
    domain = _infer_domain_tr(spine)
    seed = _seed_for(str(spine.get("event_id") or "spine"))
    return phrase_lib_tr.period_big_picture(
        domain=domain,
        seed=seed,
        enable_fun=ctx.enable_fun,
    )


def _build_chain_paragraph(
    ctx: PeriodStoryContext,
    spine: Mapping[str, Any],
    supports: Sequence[Mapping[str, Any]],
) -> str:
    transit_body = str(spine.get("transit_body") or "")
    aspect = str(spine.get("aspect") or "")
    natal_point = str(spine.get("natal_point") or "")

    start_house, end_house = _infer_start_end_houses(spine)
    start_theme = HOUSE_THEME_TR.get(start_house, "günlük hayat")
    end_theme = HOUSE_THEME_TR.get(end_house, "hayat yönü")

    angle_chain = _angle_chain_from_event(spine)
    target_chain = _target_chain_from_event(spine)
    if natal_point in ANGLE_TO_CUSP_HOUSE:
        angle_chain = angle_chain or _angle_ruler_chain(ctx.chart_snapshot, natal_point)
    elif natal_point:
        target_chain = target_chain or _planet_target_chain(ctx.chart_snapshot, natal_point)

    seed = _seed_for(str(spine.get("event_id") or "chain"))

    return phrase_lib_tr.period_mechanism_chain(
        transit_body=transit_body,
        aspect=aspect,
        natal_point=natal_point,
        angle_chain=angle_chain,
        target_chain=target_chain,
        start_theme=start_theme,
        end_theme=end_theme,
        seed=seed,
        enable_fun=ctx.enable_fun,
    )


def _build_upper_meaning(
    ctx: PeriodStoryContext,
    spine: Mapping[str, Any],
    supports: Sequence[Mapping[str, Any]],
) -> str:
    promise_theme = _select_promise_theme(ctx.natal_promise, spine)
    skill_gain = _infer_skill_gain_tr(spine, promise_theme)
    seed = _seed_for(str(spine.get("event_id") or "upper"))
    return phrase_lib_tr.period_upper_meaning(
        promise_theme=promise_theme,
        skill_gain=skill_gain,
        seed=seed,
        enable_fun=ctx.enable_fun,
    )


def _angle_ruler_chain(snapshot: Mapping[str, Any], angle: str) -> Optional[Dict[str, Any]]:
    house_cusps = snapshot.get("house_cusps") or snapshot.get("houseCusps")
    bodies_map = _snapshot_bodies_map(snapshot)
    if angle not in ANGLE_TO_CUSP_HOUSE:
        return None

    cusp_house = ANGLE_TO_CUSP_HOUSE[angle]
    cusp = _cusp_for_house(house_cusps, cusp_house)
    sign = str((cusp or {}).get("sign") or "").strip()
    if not sign:
        return None

    ruler = RULERS.get(sign)
    ruler_body = bodies_map.get(str(ruler or "").lower()) or {}

    return {
        "angle": angle,
        "sign": sign,
        "ruler": ruler,
        "ruler_house": _safe_int(ruler_body.get("house")),
        "ruler_sign": str(ruler_body.get("sign") or "").strip(),
    }


def _angle_chain_from_event(event: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    derived = event.get("derived_context") if isinstance(event.get("derived_context"), Mapping) else {}
    angle = derived.get("angle") if isinstance(derived.get("angle"), Mapping) else {}
    angle_name = str(angle.get("name") or event.get("natal_point") or "").strip().upper()
    if angle_name not in ANGLE_TO_CUSP_HOUSE:
        return None
    sign = str(angle.get("sign") or "").strip()
    ruler = str(angle.get("ruler") or "").strip()
    if not (sign and ruler):
        return None
    return {
        "angle": angle_name,
        "sign": sign,
        "ruler": ruler,
        "ruler_house": _safe_int(angle.get("ruler_house")),
        "ruler_sign": str(angle.get("ruler_sign") or "").strip(),
    }


def _planet_target_chain(snapshot: Mapping[str, Any], planet: str) -> Optional[Dict[str, Any]]:
    bodies_map = _snapshot_bodies_map(snapshot)
    pb = bodies_map.get(planet.lower())
    if not isinstance(pb, Mapping):
        return None

    sign = str(pb.get("sign") or "").strip()
    return {
        "planet": planet,
        "sign": sign,
        "house": _safe_int(pb.get("house")),
        "dispositor": RULERS.get(sign),
    }


def _target_chain_from_event(event: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    derived = event.get("derived_context") if isinstance(event.get("derived_context"), Mapping) else {}
    target = derived.get("natal_target") if isinstance(derived.get("natal_target"), Mapping) else {}
    planet = str(target.get("name") or event.get("natal_point") or "").strip()
    if not planet or planet.upper() in ANGLE_TO_CUSP_HOUSE:
        return None
    sign = str(target.get("sign") or "").strip()
    if not sign:
        return None
    return {
        "planet": planet,
        "sign": sign,
        "house": _safe_int(target.get("house")),
        "dispositor": str(target.get("dispositor") or RULERS.get(sign) or "").strip() or None,
    }


def _infer_start_end_houses(event: Mapping[str, Any]) -> Tuple[int, int]:
    houses = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}
    start_house = _safe_int(houses.get("transit_in_natal_house")) or 3
    end_house = _safe_int(houses.get("natal_point_house")) or 1
    return (start_house, end_house)


def _infer_domain_tr(event: Mapping[str, Any]) -> str:
    tags = event.get("tags") if isinstance(event.get("tags"), list) else []
    tag_set = {str(tag).lower() for tag in tags}
    if "relationships" in tag_set:
        return "ilişki dili"
    if "mind" in tag_set or "communication" in tag_set:
        return "zihin ve iletişim"
    if "career" in tag_set:
        return "yön ve görünürlük"
    if "home" in tag_set:
        return "temel düzen"
    if "self" in tag_set:
        return "kimlik ve duruş"
    _, end_house = _infer_start_end_houses(event)
    return HOUSE_THEME_TR.get(end_house, "hayat yönü")


def _select_promise_theme(natal_promise: Mapping[str, Any], spine: Mapping[str, Any]) -> str:
    themes = natal_promise.get("themes") or natal_promise.get("promiseThemes") or []
    if isinstance(themes, list) and themes:
        return str(themes[0])
    drivers = natal_promise.get("drivers")
    if isinstance(drivers, list) and drivers:
        first = drivers[0]
        if isinstance(first, Mapping):
            label = str(first.get("label") or first.get("theme") or "").strip()
            if label:
                return label
        label = str(first).strip()
        if label:
            return label
    return _infer_domain_tr(spine)


def _infer_skill_gain_tr(spine: Mapping[str, Any], promise_theme: str) -> str:
    transit_body = str(spine.get("transit_body") or "")
    aspect = str(spine.get("aspect") or "")
    if transit_body == "Neptune" and aspect in {"square", "conjunction", "opposition"}:
        return "az kelimeyle net çerçeve kurma"
    if transit_body == "Uranus" and aspect in {"trine", "sextile"}:
        return "yeni yöntemi ritme bağlama"
    if transit_body == "Saturn":
        return "sorumluluğu sade bir sisteme çevirme"
    return "daha gerçek bir yön hissi"


def _seed_for(value: str) -> int:
    raw = value if value else "seed"
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def _snapshot_bodies_map(snapshot: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    bodies = snapshot.get("bodies")
    out: Dict[str, Dict[str, Any]] = {}

    if isinstance(bodies, Mapping):
        for key, value in bodies.items():
            if isinstance(value, Mapping):
                out[str(key).lower()] = dict(value)
        return out

    if isinstance(bodies, list):
        for item in bodies:
            if not isinstance(item, Mapping):
                continue
            name = str(item.get("name") or item.get("planet") or item.get("body") or "").strip()
            if not name:
                continue
            out[name.lower()] = dict(item)
    return out


def _cusp_for_house(house_cusps: Any, house: int) -> Optional[Dict[str, Any]]:
    if isinstance(house_cusps, Mapping):
        raw = house_cusps.get(str(house), house_cusps.get(house))
        if isinstance(raw, Mapping):
            return dict(raw)
    if isinstance(house_cusps, list):
        if 0 <= house < len(house_cusps) and isinstance(house_cusps[house], Mapping):
            return dict(house_cusps[house])
        idx = house - 1
        if 0 <= idx < len(house_cusps) and isinstance(house_cusps[idx], Mapping):
            return dict(house_cusps[idx])
    return None


def _safe_int(value: Any) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _render_track_variant(raw_pool: Any, seed: str, slot: str, vars_map: Mapping[str, str]) -> str:
    if not isinstance(raw_pool, Sequence) or isinstance(raw_pool, (str, bytes)):
        return ""
    pool = [str(x).strip() for x in raw_pool if str(x).strip()]
    if not pool:
        return ""
    idx = _seed_for(f"{seed}|{slot}") % len(pool)
    out = pool[idx]
    for key, value in vars_map.items():
        out = out.replace("{{" + key + "}}", str(value or ""))
    return out.strip()


def _build_planet_hook_tr(transit_body: str, aspect: str, target: str) -> str:
    planets = getattr(phrase_lib_tr, "PLANET_NATURE_TR", {})
    aspects = getattr(phrase_lib_tr, "ASPECT_FLAVOR_TR", {})
    targets = getattr(phrase_lib_tr, "TARGET_TONE_TR", {})

    p = planets.get(str(transit_body).strip(), {})
    a = aspects.get(str(aspect).strip().lower(), {})
    t_words = targets.get(str(target).strip().upper(), [str(target).strip() or "teması"])

    noun = (p.get("nouns") or ["tema"])[0]
    averb = (a.get("verbs") or ["çalışır"])[0]
    target_word = t_words[0]
    body = str(transit_body).strip() or "Bu etki"

    if str(aspect).strip().lower() in {"square", "opposition"}:
        return f"{body} {target_word} hattına {noun} getirir; bu açı {target_word} tarafını {averb}."
    if str(aspect).strip().lower() in {"trine", "sextile"}:
        return f"{body} {target_word} tarafında {noun} açar; bu açı süreci {averb}."
    return f"{body} {target_word} tarafında {noun} ile çalışır."


def _final_polish_tr(text: str) -> str:
    out = str(text or "").replace("(", "").replace(")", "")
    for token in ("period", "exactish", "applying", "separating", "orb", "orb_deg"):
        out = out.replace(token, "")

    out = phrase_lib_tr.strip_tech_tokens(out)

    try:
        out = text_quality_tr.tr_normalize(out)
    except Exception:
        pass

    out = " ".join(out.split()).strip()
    return out
