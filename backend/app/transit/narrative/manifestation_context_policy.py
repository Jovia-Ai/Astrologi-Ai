from __future__ import annotations

import hashlib
from typing import Any, Mapping, Sequence


HOUSE_LIFE_SCENES: dict[int, tuple[str, ...]] = {
    1: (
        "bedenin, duruşun ve kişisel yönün",
        "kendini başlatma biçimin",
        "hayata nasıl girdiğin yer",
    ),
    2: (
        "değer gördüğün yer",
        "emeğinin karşılığı",
        "neyi neyle dengelediğin",
    ),
    3: (
        "gündelik konuşmalar",
        "küçük cümlelerin ağırlığı",
        "yakın çevrendeki ses",
    ),
    4: (
        "iç güvenliğin",
        "evin, köklerin ve kendi içine döndüğün yer",
        "sana ait hissettiren alan",
    ),
    5: (
        "kendini yaratıcı biçimde gösterdiğin yer",
        "keyif, aşk ve oyun alanın",
        "içinden geldiği gibi ifade ettiğin taraf",
    ),
    6: (
        "günlük tempo",
        "ne kadarını sürdürebildiğin",
        "ritüellerin ve işleyişin",
    ),
    7: (
        "karşındaki kişiyle kurduğun denge",
        "anlaşma yapma biçimin",
        "yakın ilişkideki karşılıklı alan",
    ),
    8: (
        "derinlemesine bağ",
        "ortak olan ve paylaşırken zorlandığın yer",
        "kaybetmeyi göze aldıkların",
    ),
    9: (
        "hayata verdiğin anlam",
        "uzak hedeflerin ve inançların",
        "büyük resmi kurduğun yer",
    ),
    10: (
        "dış dünyadaki rolün",
        "isminin geçtiği yer",
        "senden beklenen duruş",
    ),
    11: (
        "geleceğe doğru kurduğun çevre",
        "ait olduğun topluluklar",
        "birlikte yürüdüğün insanlar",
    ),
    12: (
        "geri çekildiğin iç dünya",
        "gözükmeyen hassasiyetlerin",
        "kapanış ve çözülme alanı",
    ),
}

_ANGLE_TO_HOUSE = {
    "ASC": 1,
    "IC": 4,
    "DSC": 7,
    "MC": 10,
}

_FALLBACK_HOUSE_BY_SPINE = {
    "primary_identity_line": 1,
    "relational_line": 7,
    "emotional_regulation_line": 4,
    "work_visibility_line": 10,
    "growth_integration_line": 9,
    "shadow_protection_line": 12,
}


def build_manifestation_context(
    *,
    matched_events: Sequence[Mapping[str, Any]] | None,
    spine_line: str,
    event_nature: str,
    chapter_role: str,
) -> dict[str, Any]:
    events = [dict(item) for item in (matched_events or []) if isinstance(item, Mapping)]
    primary_house, source = _select_primary_house(events, spine_line=spine_line)
    target_planet = _select_target_planet(events)
    target_planet_house = _select_target_planet_house(events)
    ruled_houses = _select_ruled_houses(events)
    angle = _select_angle(events)
    house_axis = _house_axis(primary_house, target_planet_house)

    variants = list(HOUSE_LIFE_SCENES.get(primary_house or 0, ()))
    variant_index = _variant_index(
        primary_house=primary_house,
        spine_line=spine_line,
        event_nature=event_nature,
        events=events,
    )
    life_scene = variants[variant_index] if variants else ""
    context_seed = _context_seed(life_scene)

    return {
        "version": "manifestation_context_v1",
        "primary_house": primary_house,
        "house_axis": house_axis,
        "target_planet": target_planet,
        "target_planet_house": target_planet_house,
        "ruled_houses": ruled_houses,
        "angle": angle,
        "life_scene": life_scene,
        "life_scene_variants": variants,
        "context_seed": context_seed,
        "variant_index": variant_index if variants else None,
        "source": source,
        "release_strengthened": _release_strengthened(
            primary_house=primary_house,
            event_nature=event_nature,
            chapter_role=chapter_role,
            events=events,
        ),
        "debug": {
            "event_ids": [
                str(event.get("event_id") or "").strip()
                for event in events
                if str(event.get("event_id") or "").strip()
            ],
        },
    }


def _select_primary_house(
    events: Sequence[Mapping[str, Any]],
    *,
    spine_line: str,
) -> tuple[int | None, str]:
    for event in events:
        houses = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}
        house = _safe_house(houses.get("transit_in_natal_house"))
        if house:
            return house, "event_house"

    for event in events:
        scene = event.get("scene") if isinstance(event.get("scene"), Mapping) else {}
        for key in ("start_house", "outcome_house"):
            house = _safe_house(scene.get(key))
            if house:
                return house, "event_house"

    for event in events:
        houses = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}
        house = _safe_house(houses.get("natal_point_house"))
        if house:
            return house, "target_planet_house"

    for event in events:
        derived = event.get("derived_context") if isinstance(event.get("derived_context"), Mapping) else {}
        natal_target = derived.get("natal_target") if isinstance(derived.get("natal_target"), Mapping) else {}
        house = _safe_house(natal_target.get("house"))
        if house:
            return house, "target_planet_house"

    for event in events:
        ruled_houses = _select_ruled_houses([event])
        if ruled_houses:
            return ruled_houses[0], "ruled_house"

    for event in events:
        point = str(event.get("natal_point") or "").strip().upper()
        house = _ANGLE_TO_HOUSE.get(point)
        if house:
            return house, "angle"

    fallback_house = _FALLBACK_HOUSE_BY_SPINE.get(spine_line)
    if fallback_house:
        return fallback_house, "fallback"
    return None, "none"


def _select_target_planet(events: Sequence[Mapping[str, Any]]) -> str | None:
    for event in events:
        token = str(event.get("natal_point") or "").strip()
        if token:
            return token
    return None


def _select_target_planet_house(events: Sequence[Mapping[str, Any]]) -> int | None:
    for event in events:
        houses = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}
        house = _safe_house(houses.get("natal_point_house"))
        if house:
            return house
    for event in events:
        derived = event.get("derived_context") if isinstance(event.get("derived_context"), Mapping) else {}
        natal_target = derived.get("natal_target") if isinstance(derived.get("natal_target"), Mapping) else {}
        house = _safe_house(natal_target.get("house"))
        if house:
            return house
    return None


def _select_ruled_houses(events: Sequence[Mapping[str, Any]]) -> list[int]:
    out: list[int] = []
    for event in events:
        candidates = []
        if isinstance(event.get("ruled_houses"), Sequence) and not isinstance(event.get("ruled_houses"), (str, bytes)):
            candidates.extend(event.get("ruled_houses") or [])
        if event.get("ruled_house") is not None:
            candidates.append(event.get("ruled_house"))
        derived = event.get("derived_context") if isinstance(event.get("derived_context"), Mapping) else {}
        if isinstance(derived.get("ruled_houses"), Sequence) and not isinstance(derived.get("ruled_houses"), (str, bytes)):
            candidates.extend(derived.get("ruled_houses") or [])
        for candidate in candidates:
            house = _safe_house(candidate)
            if house and house not in out:
                out.append(house)
    return out


def _select_angle(events: Sequence[Mapping[str, Any]]) -> str | None:
    for event in events:
        token = str(event.get("natal_point") or "").strip().upper()
        if token in _ANGLE_TO_HOUSE:
            return token
    return None


def _house_axis(primary_house: int | None, target_planet_house: int | None) -> str | None:
    if primary_house and target_planet_house and primary_house != target_planet_house:
        return f"{primary_house}-{target_planet_house}"
    if primary_house:
        return str(primary_house)
    return None


def _variant_index(
    *,
    primary_house: int | None,
    spine_line: str,
    event_nature: str,
    events: Sequence[Mapping[str, Any]],
) -> int:
    variants = HOUSE_LIFE_SCENES.get(primary_house or 0, ())
    if not variants:
        return 0
    event_ids = [
        str(event.get("event_id") or "").strip()
        for event in events
        if str(event.get("event_id") or "").strip()
    ]
    raw = "|".join([str(primary_house or ""), spine_line, event_nature, *event_ids])
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % len(variants)


def _context_seed(life_scene: str) -> str:
    if not life_scene:
        return ""
    return f"Bu tema daha çok {life_scene} içinden görünür oluyor."


def _release_strengthened(
    *,
    primary_house: int | None,
    event_nature: str,
    chapter_role: str,
    events: Sequence[Mapping[str, Any]],
) -> bool:
    if str(chapter_role or "").strip().lower() == "release":
        return True
    bodies = {
        str(event.get("transit_body") or event.get("body") or "").strip().lower()
        for event in events
        if str(event.get("transit_body") or event.get("body") or "").strip()
    }
    if event_nature == "dissolution" and primary_house in {8, 12}:
        return True
    if bodies & {"pluto", "neptune", "south_node", "south node", "southnode"} and primary_house in {8, 12}:
        return True
    return False


def _safe_house(value: Any) -> int | None:
    try:
        house = int(value)
    except (TypeError, ValueError):
        return None
    return house if 1 <= house <= 12 else None
