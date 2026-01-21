import hashlib


ANGLE_THEME = {"ASC": "identity", "DSC": "relationships", "MC": "career", "IC": "home"}
TAG_THEME = {
    "self": "identity",
    "identity": "identity",
    "relationships": "relationships",
    "career": "career",
    "home": "home",
    "inner": "inner",
    "mind": "mind",
}
HOUSE_THEME = {
    1: "identity",
    3: "mind",
    4: "home",
    7: "relationships",
    10: "career",
    12: "inner",
}


def _hash_int(value: str) -> int:
    return int(hashlib.sha1(value.encode("utf-8")).hexdigest(), 16)


def pick_primary_theme(event: dict) -> str:
    context = event.get("context", {}) or {}
    if context.get("is_angle") and context.get("natal_point") in ANGLE_THEME:
        return ANGLE_THEME[context["natal_point"]]

    tags = event.get("tags") or []
    tag_candidates = []
    for tag in tags:
        if tag in TAG_THEME:
            tag_candidates.append(TAG_THEME[tag])
    if tag_candidates:
        event_id = str(event.get("event_id") or "")
        tag_candidates = sorted(set(tag_candidates), key=lambda t: _hash_int(f"{event_id}:{t}"))
        return tag_candidates[0]

    transit_house = context.get("transit_in_natal_house")
    natal_house = context.get("natal_house")
    if isinstance(transit_house, int) and transit_house in HOUSE_THEME:
        return HOUSE_THEME[transit_house]
    if isinstance(natal_house, int) and natal_house in HOUSE_THEME:
        return HOUSE_THEME[natal_house]

    themes = event.get("themes") or []
    if themes:
        candidates = []
        for theme in themes:
            mapped = TAG_THEME.get(theme, theme)
            candidates.append(mapped)
        if candidates:
            event_id = str(event.get("event_id") or "")
            candidates = sorted(set(candidates), key=lambda t: _hash_int(f"{event_id}:{t}"))
            return candidates[0]

    return "general"
