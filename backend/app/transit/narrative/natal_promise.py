from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple

ANGLE_POINTS = {"ASC", "MC", "DSC", "IC"}
ANGLE_HOUSES = {"ASC": 1, "IC": 4, "DSC": 7, "MC": 10}
OUTER_FOR_IMPACT = {"Saturn", "Uranus", "Neptune", "Pluto"}
ASPECT_TARGET_ANGLE = {
    "conjunction": 0.0,
    "opposition": 180.0,
    "square": 90.0,
    "trine": 120.0,
    "sextile": 60.0,
}
ASPECT_ORB_MAX = {
    "conjunction": 8.0,
    "opposition": 8.0,
    "square": 7.0,
    "trine": 7.0,
    "sextile": 5.0,
}

# Must follow the same prioritized order as DispositorFlowEngine.SIGN_RULERS.
SIGN_RULERS: Mapping[str, List[str]] = {
    "aries": ["mars"],
    "taurus": ["venus"],
    "gemini": ["mercury"],
    "cancer": ["moon"],
    "leo": ["sun"],
    "virgo": ["mercury"],
    "libra": ["venus"],
    "scorpio": ["pluto", "mars"],
    "sagittarius": ["jupiter"],
    "capricorn": ["saturn"],
    "aquarius": ["uranus", "saturn"],
    "pisces": ["neptune", "jupiter"],
}

SIGN_STYLE_BY_SIGN = {
    "aries": "cardinal",
    "cancer": "cardinal",
    "libra": "cardinal",
    "capricorn": "cardinal",
    "taurus": "fixed",
    "leo": "fixed",
    "scorpio": "fixed",
    "aquarius": "fixed",
    "gemini": "mutable",
    "virgo": "mutable",
    "sagittarius": "mutable",
    "pisces": "mutable",
}

PHRASE_LIBRARY: Mapping[Tuple[str, str, str, str], Dict[str, str]] = {
    ("*", "*", "hard", "cardinal"): {
        "condition": "Baslangic hamlesi dis baski ile carpistiginda konu disa tasar.",
        "how_to_use": "Hizi degil sirayi yonet; once sinir sonra adim sec.",
        "conflict": "{point} ile ilgili gerilim, {house} ev temasinda hizli reaksiyonu tetikleyebilir.",
        "shadow": "Golge tarafta {sign} stili savunmaya cekebilir; {planet} disiplini burada denge kurar.",
        "upper": "Ayni mekanik ustaliga donustugunde {house} evde kalici bir ilerleme acilir.",
        "guidance": "{house} evde mikro-plan kullan ve tek metrik takip et.",
        "watch": "{point} uzerinde kontrolu sertlestirmek yerine ritmi sabitle.",
    },
    ("*", "*", "hard", "fixed"): {
        "condition": "Tutundugun kalip zorlandiginda etki daha belirgin olur.",
        "how_to_use": "Direnci azaltip adim boyunu kucultmek etkiyi yararli hale getirir.",
        "conflict": "{point} hattinda sertlesme riski, {house} ev konularini kilitleyebilir.",
        "shadow": "Golge tarafta {sign} sabitligi gereksiz inada donebilir.",
        "upper": "Esneklik eklendiginde {planet} enerjisi yapisal ustaliga doner.",
        "guidance": "{house} evde tek bir engeli coz ve sonucu olc.",
        "watch": "{point} alaninda ya hep ya hic kararindan kacin.",
    },
    ("*", "*", "hard", "mutable"): {
        "condition": "Dagilan odak toparlanamadiginda etki icten disa tasar.",
        "how_to_use": "Bir gorev, bir kanal, bir zaman blogu ilkesi uygula.",
        "conflict": "{point} ekseninde zihinsel dagilma, {house} evde verimi dusurebilir.",
        "shadow": "{sign} stili fazla opsiyon urettiginde karar gecikir.",
        "upper": "{planet} odagi ile sade plan kuruldugunda {house} evde netlik artis gorulur.",
        "guidance": "{house} ev icin 48 saatlik net bir hedef yaz.",
        "watch": "{point} temasinda ayni anda cok sey baslatma.",
    },
    ("*", "*", "soft", "cardinal"): {
        "condition": "Net niyetle ilk adim atildiginda etki disa yansir.",
        "how_to_use": "Firsati hizli ama olculu bir planla somutlastir.",
        "conflict": "{point} tarafinda rahat akis olsa da yonsuz hiz dagitim yaratabilir.",
        "shadow": "{sign} temposu aceleyle ayrintiyi atlayabilir.",
        "upper": "{house} evde baslangic cesareti dogru strukuturle buyur.",
        "guidance": "{house} evde ilk adimi bugun at, ikinci adimi takvime koy.",
        "watch": "{point} hattinda sadece motivasyonla yetinme.",
    },
    ("*", "*", "soft", "fixed"): {
        "condition": "Duzene giren ritim etkiyi gorunur sonuca cevirir.",
        "how_to_use": "Istikrari koru ve kazanimi tekrar eden rutine bagla.",
        "conflict": "{point} uzerinde rahatlik atalete kayarsa firsat soguyabilir.",
        "shadow": "{sign} sabitligi gereksiz konfor alani yaratabilir.",
        "upper": "{house} evde sabit tempo uzun vadeli guc biriktirir.",
        "guidance": "{house} evde calisan modeli ayni saatte tekrar et.",
        "watch": "{point} temasinda degisimi tamamen erteleme.",
    },
    ("*", "*", "soft", "mutable"): {
        "condition": "Akis dogru kanala girerse etki hizli ogrenmeye doner.",
        "how_to_use": "Secenekleri azalt ve tek odaga enerji ver.",
        "conflict": "{point} tarafinda daginik firsatlar yon kaybina neden olabilir.",
        "shadow": "{sign} degiskenligi surekli rota degistirmeye itebilir.",
        "upper": "{house} evde ogrenme hizi disiplinle birlesince ustalik getirir.",
        "guidance": "{house} evde bir deneme plani sec ve 7 gun izle.",
        "watch": "{point} icin ayni soruna yeni arac yigmaktan kacin.",
    },
    ("*", "*", "conjunction", "cardinal"): {
        "condition": "Enerji ayni noktada biriktiginde konu hizla gorunurlesir.",
        "how_to_use": "Tek hedef secip gucu dagitmadan ilerle.",
        "conflict": "{point} odaginda yogunlasma, {house} evde fazla yukleme yaratabilir.",
        "shadow": "{sign} hizinda acele kontrolsuz harcama yapabilir.",
        "upper": "{planet} ile odak korundugunda {house} evde ciddi ivme acilir.",
        "guidance": "{house} ev hedefini tek satira indir ve takip et.",
        "watch": "{point} icin ayni anda birden fazla cephe acma.",
    },
    ("*", "*", "conjunction", "fixed"): {
        "condition": "Biriken enerji sabit bir yone baglaninca dis sonuc verir.",
        "how_to_use": "Surdurulebilir bir tempo kur ve kararlari sade tut.",
        "conflict": "{point} odaginda birikme, {house} evde sikisiklik hissi yaratabilir.",
        "shadow": "{sign} sabitligi guncelleme ihtiyacini geciktirebilir.",
        "upper": "{house} evde agir ama kalici bir buyume hattina girebilirsin.",
        "guidance": "{house} evde tek sistemi optimize et.",
        "watch": "{point} tarafinda yeni veri gelince plana direnc gosterme.",
    },
    ("*", "*", "conjunction", "mutable"): {
        "condition": "Biriken enerji dagilmazsa hizli ogrenme etkisi disa cikar.",
        "how_to_use": "Odagi daralt ve net cikti ureten bir dongu kur.",
        "conflict": "{point} odagi dagilinca {house} evde belirsizlik artabilir.",
        "shadow": "{sign} oynakligi karar yorulmasi yaratabilir.",
        "upper": "{planet} etkisiyle {house} evde esnek ama net bir uzmanlik gelisir.",
        "guidance": "{house} ev icin 3 adimli mini surec tasarla.",
        "watch": "{point} ekseninde sonuca varmadan once arac degistirme.",
    },
}

HOUSE_DOMAIN_HINTS = {
    1: "identity",
    3: "mind",
    4: "home",
    7: "relationships",
    8: "inner",
    9: "mind",
    10: "career",
}


def build_natal_promise(
    event: Mapping[str, Any],
    natal: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    natal_map = natal if isinstance(natal, Mapping) else {}
    if not natal_map:
        return _minimal_not_available()

    bodies = natal_map.get("bodies") if isinstance(natal_map.get("bodies"), list) else []
    angles = natal_map.get("angles") if isinstance(natal_map.get("angles"), Mapping) else {}
    cusps = natal_map.get("house_cusps") if isinstance(natal_map.get("house_cusps"), list) else []

    if not bodies or not cusps:
        return _minimal_not_available()

    body_index = _index_bodies(bodies)
    house_rulers = _build_house_rulers(cusps)
    natal_aspects = _compute_natal_aspects(bodies)
    graph = _build_graph(body_index, angles, house_rulers, natal_aspects)
    target = _resolve_target(event, body_index, angles, house_rulers)
    walk = _walk_graph(event, graph, target)
    connected_points = _build_connected_points(target, walk, body_index, house_rulers)
    domains = _derive_domains(target, connected_points)
    dispositor_chain = _build_dispositor_chain(target, body_index, house_rulers)

    score, verdict, score_parts = _score_event(event, target, body_index, walk)
    drivers = _build_drivers(
        event,
        target,
        body_index,
        natal_aspects,
        dispositor_chain,
        score_parts,
    )
    gate = _build_gate(event, target, domains, connected_points)

    return {
        "score": round(score, 3),
        "verdict": verdict,
        "drivers": drivers,
        "connected_points": connected_points[:6],
        "gate": gate,
    }


def build_section_injections(event: Mapping[str, Any], natal_promise: Mapping[str, Any]) -> Dict[str, str]:
    connected = natal_promise.get("connected_points") if isinstance(natal_promise, Mapping) else []
    if not isinstance(connected, list) or not connected:
        return {
            "conflict": "Natal baglanti verisi su an mevcut degil.",
            "shadow": "Derin neden katmani su an sinirli.",
            "upper": "Yine de sureci olculu adimlarla ustaliga cevirebilirsin.",
            "guidance": "Baglanti verisi olmadigi icin sade plan uygula.",
            "watch": "Veri eksiginde acele buyuk karar alma.",
        }

    house = _first_value(connected, "house", default="3")
    point = _first_value(connected, "planet", default=_text(event.get("natal_point"), "natal nokta"))
    sign = _first_value(connected, "sign", default="aries")
    planet = _text(event.get("transit_body"), "saturn").lower()
    aspect_family = _aspect_family(_text(event.get("aspect"), ""))
    sign_style = SIGN_STYLE_BY_SIGN.get(sign.lower(), "cardinal")
    phrases = _pick_phrase_pack(planet, str(house), aspect_family, sign_style)

    scope = {
        "planet": planet,
        "house": str(house),
        "point": str(point),
        "sign": sign,
    }
    return {
        "conflict": phrases["conflict"].format(**scope),
        "shadow": phrases["shadow"].format(**scope),
        "upper": phrases["upper"].format(**scope),
        "guidance": phrases["guidance"].format(**scope),
        "watch": phrases["watch"].format(**scope),
    }


def _minimal_not_available() -> Dict[str, Any]:
    drivers = [
        {"type": "house_ruler_link", "text": "not available", "score": 0.0},
        {"type": "resonance", "text": "not available", "score": 0.0},
        {"type": "timers", "text": "not available", "score": 0.0},
    ]
    connected = [
        {"kind": "status", "value": "not available", "score": 0.0},
        {"kind": "house", "value": "not available", "score": 0.0},
        {"kind": "sign", "value": "not available", "score": 0.0},
    ]
    return {
        "score": 0.0,
        "verdict": "low",
        "drivers": drivers,
        "connected_points": connected,
        "gate": {
            "condition": "Natal context not available.",
            "how_to_use": "Use low-risk pacing until natal context is available.",
        },
    }


def _text(value: Any, default: str = "") -> str:
    text = str(value or "").strip()
    return text or default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _index_bodies(bodies: Sequence[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for body in bodies:
        name = _text(body.get("body"))
        if not name:
            continue
        out[name.lower()] = {
            "name": name,
            "sign": _text(body.get("sign")),
            "house": body.get("house"),
            "lon": body.get("lon"),
        }
    return out


def _build_house_rulers(cusps: Sequence[Mapping[str, Any]]) -> Dict[int, Dict[str, Any]]:
    out: Dict[int, Dict[str, Any]] = {}
    for cusp in cusps:
        try:
            house = int(cusp.get("house"))
        except (TypeError, ValueError):
            continue
        sign = _text(cusp.get("sign"))
        rulers = list(SIGN_RULERS.get(sign.lower(), []))
        primary = rulers[0] if rulers else None
        out[house] = {
            "house": house,
            "sign": sign,
            "ruler": primary,
            "rulers": rulers,
        }
    return out


def _diff_angle(a: float, b: float) -> float:
    diff = abs((a - b) % 360.0)
    return 360.0 - diff if diff > 180.0 else diff


def _compute_natal_aspects(bodies: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    points: List[Tuple[str, float]] = []
    for body in bodies:
        name = _text(body.get("body"))
        lon = body.get("lon")
        if name and isinstance(lon, (int, float)):
            points.append((name, float(lon)))

    aspects: List[Dict[str, Any]] = []
    for idx, (a_name, a_lon) in enumerate(points):
        for b_name, b_lon in points[idx + 1 :]:
            diff = _diff_angle(a_lon, b_lon)
            for aspect, target in ASPECT_TARGET_ANGLE.items():
                orb = abs(diff - target)
                max_orb = ASPECT_ORB_MAX[aspect]
                if orb <= max_orb:
                    aspects.append(
                        {
                            "a": a_name,
                            "b": b_name,
                            "aspect": aspect,
                            "orb": orb,
                            "max_orb": max_orb,
                        }
                    )
                    break
    return aspects


def _node_id(kind: str, value: Any) -> str:
    return f"{kind}:{value}"


def _build_graph(
    body_index: Mapping[str, Mapping[str, Any]],
    angles: Mapping[str, Any],
    house_rulers: Mapping[int, Mapping[str, Any]],
    natal_aspects: Sequence[Mapping[str, Any]],
) -> Dict[str, Any]:
    adjacency: MutableMapping[str, List[Dict[str, Any]]] = defaultdict(list)
    nodes: Dict[str, Dict[str, Any]] = {}

    def add_node(kind: str, value: Any, score: float = 1.0) -> str:
        node = _node_id(kind, value)
        if node not in nodes:
            nodes[node] = {"kind": kind, "value": value, "score": max(0.0, min(1.0, float(score)))}
        return node

    def connect(a: str, b: str, weight: float, label: str) -> None:
        w = max(0.05, min(1.0, float(weight)))
        adjacency[a].append({"to": b, "weight": w, "label": label})
        adjacency[b].append({"to": a, "weight": w, "label": label})

    for house, entry in house_rulers.items():
        house_node = add_node("house", house, 0.9)
        sign = _text(entry.get("sign")).lower()
        if sign:
            sign_node = add_node("sign", sign, 0.65)
            connect(house_node, sign_node, 0.6, "house_sign")
        ruler = _text(entry.get("ruler"))
        if ruler:
            planet_node = add_node("planet", ruler, 0.85)
            connect(house_node, planet_node, 0.82, "house_ruler")

    for lower_name, info in body_index.items():
        planet_name = _text(info.get("name"), lower_name)
        planet_node = add_node("planet", planet_name.lower(), 0.9)
        house = info.get("house")
        if isinstance(house, int):
            house_node = add_node("house", house, 0.9)
            connect(planet_node, house_node, 0.64, "in_house")
        sign = _text(info.get("sign")).lower()
        if sign:
            sign_node = add_node("sign", sign, 0.65)
            connect(planet_node, sign_node, 0.58, "in_sign")
            rulers = SIGN_RULERS.get(sign, [])
            for idx, ruler in enumerate(rulers):
                if ruler not in body_index:
                    continue
                disp_node = add_node("planet", ruler, 0.88)
                base = 0.78 if idx == 0 else 0.62
                connect(planet_node, disp_node, base, "dispositor")

    for aspect in natal_aspects:
        a = _text(aspect.get("a")).lower()
        b = _text(aspect.get("b")).lower()
        if not a or not b:
            continue
        a_node = add_node("planet", a, 0.9)
        b_node = add_node("planet", b, 0.9)
        orb = _safe_float(aspect.get("orb"), 6.0)
        max_orb = _safe_float(aspect.get("max_orb"), 6.0)
        orb_weight = max(0.2, min(1.0, 1.0 - (orb / max_orb))) if max_orb > 0 else 0.2
        connect(a_node, b_node, 0.52 + (0.4 * orb_weight), f"aspect:{_text(aspect.get('aspect'))}")

    by_house: Dict[int, List[str]] = defaultdict(list)
    for info in body_index.values():
        house = info.get("house")
        if isinstance(house, int):
            by_house[house].append(_text(info.get("name")).lower())
    for house, planet_names in by_house.items():
        if len(planet_names) < 2:
            continue
        for idx, name_a in enumerate(planet_names):
            for name_b in planet_names[idx + 1 :]:
                a_node = add_node("planet", name_a, 0.88)
                b_node = add_node("planet", name_b, 0.88)
                base = 0.68 if len(planet_names) >= 3 else 0.6
                connect(a_node, b_node, base, f"co_presence:{house}")

    for angle_key, angle_value in angles.items():
        if not isinstance(angle_value, Mapping):
            continue
        point = _text(angle_value.get("point"), _text(angle_key)).upper()
        sign = _text(angle_value.get("sign")).lower()
        if point not in ANGLE_POINTS:
            continue
        angle_node = add_node("angle", point, 1.0)
        if sign:
            sign_node = add_node("sign", sign, 0.7)
            connect(angle_node, sign_node, 0.58, "angle_sign")
            rulers = SIGN_RULERS.get(sign, [])
            for idx, ruler in enumerate(rulers):
                if ruler not in body_index:
                    continue
                planet_node = add_node("planet", ruler, 0.92)
                connect(angle_node, planet_node, 0.75 if idx == 0 else 0.6, "angle_ruler")

    return {"nodes": nodes, "adjacency": dict(adjacency)}


def _resolve_target(
    event: Mapping[str, Any],
    body_index: Mapping[str, Mapping[str, Any]],
    angles: Mapping[str, Any],
    house_rulers: Mapping[int, Mapping[str, Any]],
) -> Dict[str, Any]:
    natal_point = _text(event.get("natal_point") or event.get("natal_body")).upper()
    transit_body = _text(event.get("transit_body"))
    target_house = None
    houses = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}
    raw_target_house = houses.get("natal_point_house")
    if isinstance(raw_target_house, int):
        target_house = raw_target_house
    elif natal_point in ANGLE_HOUSES:
        target_house = ANGLE_HOUSES[natal_point]
    else:
        transit_house = houses.get("transit_in_natal_house")
        if isinstance(transit_house, int):
            target_house = transit_house

    target_sign = ""
    target_planet = ""
    if natal_point.lower() in body_index:
        entry = body_index[natal_point.lower()]
        target_planet = _text(entry.get("name"))
        target_sign = _text(entry.get("sign"))
        if not target_house and isinstance(entry.get("house"), int):
            target_house = int(entry.get("house"))
    elif natal_point in ANGLE_POINTS:
        angle_value = angles.get(natal_point)
        if isinstance(angle_value, Mapping):
            target_sign = _text(angle_value.get("sign"))
        house_entry = house_rulers.get(ANGLE_HOUSES.get(natal_point, -1))
        if isinstance(house_entry, Mapping):
            target_planet = _text(house_entry.get("ruler"))
    elif target_house and target_house in house_rulers:
        target_sign = _text(house_rulers[target_house].get("sign"))

    angle_primary_rulers: set[str] = set()
    for angle in ANGLE_POINTS:
        angle_value = angles.get(angle)
        if not isinstance(angle_value, Mapping):
            continue
        angle_sign = _text(angle_value.get("sign")).lower()
        rulers = SIGN_RULERS.get(angle_sign, [])
        if rulers:
            angle_primary_rulers.add(rulers[0])

    return {
        "natal_point": natal_point,
        "target_house": target_house,
        "target_sign": target_sign,
        "target_planet": target_planet,
        "transit_body": transit_body,
        "is_angle": natal_point in ANGLE_POINTS,
        "angle_primary_rulers": sorted(angle_primary_rulers),
    }


def _walk_graph(
    event: Mapping[str, Any],
    graph: Mapping[str, Any],
    target: Mapping[str, Any],
    *,
    depth: int = 3,
) -> Dict[str, Any]:
    nodes = graph.get("nodes") if isinstance(graph.get("nodes"), Mapping) else {}
    adjacency = graph.get("adjacency") if isinstance(graph.get("adjacency"), Mapping) else {}
    strength = _safe_float(event.get("strength"), 0.0)
    ranking = event.get("ranking") if isinstance(event.get("ranking"), Mapping) else {}
    if strength <= 0.0:
        strength = _safe_float(ranking.get("strength"), 0.0)
    if strength <= 0.0:
        strength = min(1.0, _safe_float(ranking.get("weight"), 0.0) / 2.5)
    strength_boost = max(0.75, min(1.1, 0.8 + (0.3 * strength)))

    starts: List[str] = []
    natal_point = _text(target.get("natal_point"))
    if natal_point in ANGLE_POINTS:
        starts.append(_node_id("angle", natal_point))
    if _text(target.get("target_planet")):
        starts.append(_node_id("planet", _text(target.get("target_planet")).lower()))
    if natal_point and natal_point.lower() not in {p.lower() for p in ANGLE_POINTS}:
        starts.append(_node_id("planet", natal_point.lower()))
    if isinstance(target.get("target_house"), int):
        starts.append(_node_id("house", int(target.get("target_house"))))
    starts = [s for s in starts if s in nodes]

    if not starts:
        return {"scores": {}, "best_path_score": 0.0, "start_nodes": []}

    best_score: Dict[str, float] = {}
    queue: List[Tuple[str, int, float, Tuple[str, ...]]] = []
    for start in starts:
        queue.append((start, 0, strength_boost, (start,)))
        best_score[start] = max(best_score.get(start, 0.0), strength_boost)

    while queue:
        node_id, current_depth, score, path = queue.pop(0)
        if current_depth >= depth:
            continue
        for edge in adjacency.get(node_id, []):
            if not isinstance(edge, Mapping):
                continue
            nxt = _text(edge.get("to"))
            if not nxt or nxt in path:
                continue
            edge_weight = max(0.05, min(1.0, _safe_float(edge.get("weight"), 0.5)))
            new_score = score * edge_weight
            prev = best_score.get(nxt, 0.0)
            if new_score <= prev:
                continue
            best_score[nxt] = new_score
            queue.append((nxt, current_depth + 1, new_score, path + (nxt,)))

    best_path_score = max(best_score.values()) if best_score else 0.0
    return {"scores": best_score, "best_path_score": best_path_score, "start_nodes": starts}


def _build_connected_points(
    target: Mapping[str, Any],
    walk: Mapping[str, Any],
    body_index: Mapping[str, Mapping[str, Any]],
    house_rulers: Mapping[int, Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    scores = walk.get("scores") if isinstance(walk.get("scores"), Mapping) else {}
    start_nodes = set(walk.get("start_nodes") or [])
    points: List[Dict[str, Any]] = []

    target_house = target.get("target_house")
    if isinstance(target_house, int):
        house_score = _safe_float(scores.get(_node_id("house", target_house)), 0.6)
        points.append({"kind": "house", "value": target_house, "score": round(min(1.0, house_score), 3)})

    target_sign = _text(target.get("target_sign")).lower()
    if target_sign:
        sign_score = _safe_float(scores.get(_node_id("sign", target_sign)), 0.55)
        points.append({"kind": "sign", "value": target_sign, "score": round(min(1.0, sign_score), 3)})

    chain = _build_dispositor_chain(target, body_index, house_rulers)
    if chain:
        chain_score = min(1.0, 0.5 + (0.1 * min(len(chain), 4)))
        points.append({"kind": "dispositor_chain", "value": "->".join(chain), "score": round(chain_score, 3)})

    ranked_nodes = sorted(
        (
            (node_id, _safe_float(score))
            for node_id, score in scores.items()
            if node_id not in start_nodes
        ),
        key=lambda item: item[1],
        reverse=True,
    )
    for node_id, score in ranked_nodes[:8]:
        if ":" not in node_id:
            continue
        kind, raw_value = node_id.split(":", 1)
        value: Any = raw_value
        if kind == "house":
            try:
                value = int(raw_value)
            except ValueError:
                value = raw_value
        points.append({"kind": kind, "value": value, "score": round(min(1.0, score), 3)})

    deduped: List[Dict[str, Any]] = []
    seen = set()
    for point in points:
        key = (point.get("kind"), str(point.get("value")))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(point)
        if len(deduped) >= 6:
            break
    while len(deduped) < 3:
        deduped.append({"kind": "status", "value": "not available", "score": 0.0})
    return deduped


def _build_dispositor_chain(
    target: Mapping[str, Any],
    body_index: Mapping[str, Mapping[str, Any]],
    house_rulers: Mapping[int, Mapping[str, Any]],
) -> List[str]:
    seed = _text(target.get("target_planet")).lower()
    if not seed and isinstance(target.get("target_house"), int):
        entry = house_rulers.get(int(target.get("target_house")))
        seed = _text((entry or {}).get("ruler")).lower()
    if not seed or seed not in body_index:
        return []

    chain = [seed]
    current = seed
    for _ in range(5):
        sign = _text(body_index.get(current, {}).get("sign")).lower()
        if not sign:
            break
        rulers = SIGN_RULERS.get(sign, [])
        nxt = ""
        for candidate in rulers:
            if candidate in body_index:
                nxt = candidate
                break
        if not nxt:
            break
        if nxt == current:
            break
        if nxt in chain:
            chain.append(nxt)
            break
        chain.append(nxt)
        current = nxt
    return chain


def _derive_domains(target: Mapping[str, Any], connected_points: Sequence[Mapping[str, Any]]) -> List[str]:
    domains: List[str] = []
    if target.get("is_angle"):
        point = _text(target.get("natal_point"))
        if point in {"ASC"}:
            domains.append("identity")
        if point in {"DSC"}:
            domains.append("relationships")
        if point in {"MC"}:
            domains.append("career")
        if point in {"IC"}:
            domains.append("home")
    target_house = target.get("target_house")
    if isinstance(target_house, int):
        domains.append(HOUSE_DOMAIN_HINTS.get(target_house, "general"))
    for point in connected_points:
        if point.get("kind") != "house":
            continue
        value = point.get("value")
        if isinstance(value, int):
            domains.append(HOUSE_DOMAIN_HINTS.get(value, "general"))
    seen = set()
    ordered: List[str] = []
    for item in domains:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered or ["general"]


def _score_event(
    event: Mapping[str, Any],
    target: Mapping[str, Any],
    body_index: Mapping[str, Mapping[str, Any]],
    walk: Mapping[str, Any],
) -> Tuple[float, str, Dict[str, float]]:
    impact = 0.30
    natal_point = _text(target.get("natal_point"))
    transit_body = _text(event.get("transit_body"))
    phase = _text(event.get("phase")).lower()
    orb_deg = _safe_float(event.get("orb_deg"), 99.0)
    ranking = event.get("ranking") if isinstance(event.get("ranking"), Mapping) else {}
    tier = _text(ranking.get("tier"), "support").lower()

    if natal_point in ANGLE_POINTS:
        impact += 0.20
    if transit_body in OUTER_FOR_IMPACT:
        impact += 0.15
    if phase in {"applying", "exactish", "exact"}:
        impact += 0.10
    if orb_deg <= 1.0:
        impact += 0.10
    if tier == "main":
        impact += 0.10

    receptivity = 0.0
    target_house = target.get("target_house")
    if isinstance(target_house, int) and target_house in {1, 4, 7, 10}:
        receptivity += 0.10

    if isinstance(target_house, int):
        count = 0
        for body in body_index.values():
            if body.get("house") == target_house:
                count += 1
        if count >= 3:
            receptivity += 0.10

    target_planet = _text(target.get("target_planet")).lower()
    angle_primary_rulers = {
        str(item).lower() for item in (target.get("angle_primary_rulers") or []) if str(item).strip()
    }
    if target_planet and target_planet in angle_primary_rulers:
        receptivity += 0.05

    best_path_score = _safe_float(walk.get("best_path_score"), 0.0)
    best_path_score_normalized = max(0.0, min(1.0, best_path_score))
    graph_activation = min(0.25, best_path_score_normalized)

    score = max(0.0, min(1.0, impact + receptivity + graph_activation))
    if score < 0.45:
        verdict = "low"
    elif score <= 0.70:
        verdict = "medium"
    else:
        verdict = "high"

    return score, verdict, {
        "impact": round(impact, 3),
        "receptivity": round(receptivity, 3),
        "graph_activation": round(graph_activation, 3),
    }


def _build_drivers(
    event: Mapping[str, Any],
    target: Mapping[str, Any],
    body_index: Mapping[str, Mapping[str, Any]],
    natal_aspects: Sequence[Mapping[str, Any]],
    dispositor_chain: Sequence[str],
    score_parts: Mapping[str, float],
) -> List[Dict[str, Any]]:
    drivers: List[Dict[str, Any]] = []
    natal_point = _text(target.get("natal_point"))
    target_house = target.get("target_house")
    target_planet = _text(target.get("target_planet"))
    phase = _text(event.get("phase")).lower()
    orb_deg = _safe_float(event.get("orb_deg"), 99.0)

    if target.get("is_angle"):
        drivers.append(
            {
                "type": "angle_activation",
                "text": f"{natal_point} aktivasyonu bu olayi dis dunyada daha gorunur kilar.",
                "score": 1.0,
            }
        )

    if isinstance(target_house, int):
        drivers.append(
            {
                "type": "house_ruler_link",
                "text": f"{target_house}. ev yonetici bagi olay etkisini natal zemine bagliyor.",
                "score": 0.75,
            }
        )

    chain = list(dispositor_chain)
    if chain:
        drivers.append(
            {
                "type": "dispositor_chain",
                "text": f"Dispositor zinciri: {' -> '.join(chain)}.",
                "score": min(1.0, 0.5 + (0.1 * min(len(chain), 4))),
            }
        )

    if isinstance(target_house, int):
        same_house = [b for b in body_index.values() if b.get("house") == target_house]
        if len(same_house) >= 3:
            drivers.append(
                {
                    "type": "natal_emphasis",
                    "text": f"{target_house}. evde natal yigilim bu temayi buyutur.",
                    "score": 0.85,
                }
            )

    if target_planet:
        involved = [
            asp
            for asp in natal_aspects
            if _text(asp.get("a")).lower() == target_planet.lower()
            or _text(asp.get("b")).lower() == target_planet.lower()
        ]
        if involved:
            tightest = min(_safe_float(asp.get("orb"), 6.0) for asp in involved)
            resonance_score = max(0.2, min(1.0, 1.0 - (tightest / 8.0)))
            drivers.append(
                {
                    "type": "resonance",
                    "text": f"Natal aci rezonansi {target_planet} temasini tekrar aktive ediyor.",
                    "score": round(resonance_score, 3),
                }
            )

    orb_phase_score = 0.35
    if phase in {"applying", "exactish", "exact"}:
        orb_phase_score += 0.30
    if orb_deg <= 1.0:
        orb_phase_score += 0.35
    drivers.append(
        {
            "type": "orb_phase",
            "text": "Orb ve faz etkisi olay gucunu belirginlestiriyor.",
            "score": round(min(1.0, orb_phase_score), 3),
        }
    )

    timers_text = "not available"
    timers_score = 0.0
    ranking = event.get("ranking") if isinstance(event.get("ranking"), Mapping) else {}
    exact_in_days = ranking.get("exact_in_days")
    if isinstance(exact_in_days, (int, float)):
        timers_text = f"Exact zamanlayici: {exact_in_days} gun."
        timers_score = 0.5
    drivers.append({"type": "timers", "text": timers_text, "score": timers_score})

    if not drivers:
        drivers = [{"type": "timers", "text": "not available", "score": 0.0}]

    drivers_sorted = sorted(drivers, key=lambda item: float(item.get("score") or 0.0), reverse=True)
    selected = drivers_sorted[:5]
    if len(selected) < 3:
        selected.append({"type": "timers", "text": "not available", "score": 0.0})
        selected = selected[:3]

    # Ensure score part visibility in a deterministic, interpretable way.
    selected.append(
        {
            "type": "impact_breakdown",
            "text": (
                f"impact={score_parts.get('impact', 0.0):.2f}, "
                f"receptivity={score_parts.get('receptivity', 0.0):.2f}, "
                f"graph={score_parts.get('graph_activation', 0.0):.2f}"
            ),
            "score": round(min(1.0, _safe_float(score_parts.get("impact"), 0.0)), 3),
        }
    )
    return selected[:6]


def _build_gate(
    event: Mapping[str, Any],
    target: Mapping[str, Any],
    domains: Sequence[str],
    connected_points: Sequence[Mapping[str, Any]],
) -> Dict[str, str]:
    house = target.get("target_house")
    point = _text(target.get("natal_point"), "natal point")
    sign = _text(target.get("target_sign"), "aries").lower()
    planet = _text(event.get("transit_body"), "saturn").lower()
    aspect_family = _aspect_family(_text(event.get("aspect"), ""))
    sign_style = SIGN_STYLE_BY_SIGN.get(sign, "cardinal")
    phrases = _pick_phrase_pack(planet, str(house or "3"), aspect_family, sign_style)

    first_domain = domains[0] if domains else "general"
    cp_text = ""
    for point_entry in connected_points:
        kind = _text(point_entry.get("kind"))
        value = point_entry.get("value")
        if kind and value is not None:
            cp_text = f"Bagli nokta: {kind}={value}."
            break

    return {
        "condition": f"{phrases['condition']} {cp_text}".strip(),
        "how_to_use": f"{phrases['how_to_use']} Alan odagi: {first_domain}.",
    }


def _aspect_family(aspect: str) -> str:
    value = aspect.lower().strip()
    if value in {"square", "opposition", "quincunx"}:
        return "hard"
    if value in {"trine", "sextile"}:
        return "soft"
    if value == "conjunction":
        return "conjunction"
    return "mixed"


def _pick_phrase_pack(planet: str, house: str, aspect_family: str, sign_style: str) -> Dict[str, str]:
    keys = [
        (planet, house, aspect_family, sign_style),
        (planet, "*", aspect_family, sign_style),
        ("*", house, aspect_family, sign_style),
        ("*", "*", aspect_family, sign_style),
        ("*", "*", "hard", "cardinal"),
    ]
    for key in keys:
        if key in PHRASE_LIBRARY:
            return PHRASE_LIBRARY[key]
    return PHRASE_LIBRARY[("*", "*", "hard", "cardinal")]


def _first_value(points: Sequence[Mapping[str, Any]], kind: str, default: str) -> str:
    for item in points:
        if _text(item.get("kind")) != kind:
            continue
        return _text(item.get("value"), default)
    return default
