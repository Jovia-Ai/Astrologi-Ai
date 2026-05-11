from __future__ import annotations

import hashlib
import re
from typing import Any, Dict, Mapping, Sequence

from app.narrative.humanize_en import humanize_en_text, split_en_sentences


PLANET_EN = {
    "Sun": "Sun",
    "Moon": "Moon",
    "Mercury": "Mercury",
    "Venus": "Venus",
    "Mars": "Mars",
    "Jupiter": "Jupiter",
    "Saturn": "Saturn",
    "Uranus": "Uranus",
    "Neptune": "Neptune",
    "Pluto": "Pluto",
}

POINT_EN = {
    "ASC": "Ascendant",
    "MC": "Midheaven",
    "DSC": "Descendant",
    "IC": "IC",
}

SIGN_EN = {
    "Aries": "Aries",
    "Taurus": "Taurus",
    "Gemini": "Gemini",
    "Cancer": "Cancer",
    "Leo": "Leo",
    "Virgo": "Virgo",
    "Libra": "Libra",
    "Scorpio": "Scorpio",
    "Sagittarius": "Sagittarius",
    "Capricorn": "Capricorn",
    "Aquarius": "Aquarius",
    "Pisces": "Pisces",
}

HOUSE_LABEL_EN = {
    1: "identity and presentation",
    2: "money, value, and steadiness",
    3: "language, thinking, and everyday exchange",
    4: "home, roots, and inner stability",
    5: "creativity, joy, and self-expression",
    6: "routine, work, and upkeep",
    7: "partnership and relational balance",
    8: "trust, vulnerability, and emotional depth",
    9: "meaning, learning, and direction",
    10: "career, reputation, and visibility",
    11: "community, collaboration, and future plans",
    12: "the inner world, retreat, and release",
}

HOUSE_SCENE_EN = {
    1: "how you carry yourself",
    2: "your sense of value and material steadiness",
    3: "your words, tone, and day-to-day exchanges",
    4: "your home base and emotional footing",
    5: "your spark, expression, and appetite for joy",
    6: "your daily rhythm and the way you hold things together",
    7: "the way you negotiate closeness and expectation",
    8: "trust, sharing, and emotional exposure",
    9: "your sense of meaning and mental horizon",
    10: "your career direction and public role",
    11: "your communities, collaborations, and future vision",
    12: "what happens in private and beneath the surface",
}

HOUSE_TITLE_EN = {
    1: "Self-Presentation",
    2: "Value And Stability",
    3: "Language And Thinking",
    4: "Home And Grounding",
    5: "Expression And Joy",
    6: "Daily Systems",
    7: "Relational Balance",
    8: "Trust And Depth",
    9: "Meaning And Direction",
    10: "Career And Visibility",
    11: "Community And Plans",
    12: "The Inner Field",
}

PLANET_DRIVE_EN = {
    "Sun": "clarifies what matters",
    "Moon": "heightens sensitivity",
    "Mercury": "speeds up the mind",
    "Venus": "softens the relational field",
    "Mars": "pushes for movement",
    "Jupiter": "widens the frame",
    "Saturn": "tightens the structure",
    "Uranus": "shakes the routine loose",
    "Neptune": "blurs and sensitises the edges",
    "Pluto": "intensifies what is already real",
}

PLANET_GIFTS_EN = {
    "Sun": "cleaner self-definition",
    "Moon": "better emotional timing",
    "Mercury": "clearer thinking and cleaner language",
    "Venus": "more grace in the way you relate",
    "Mars": "decisive movement",
    "Jupiter": "wider perspective",
    "Saturn": "stronger structure",
    "Uranus": "useful change instead of random disruption",
    "Neptune": "better intuition with softer edges",
    "Pluto": "real depth and cleaner focus",
}

ASPECT_TONE_EN = {
    "square": {
        "conflict": "creates friction that wants a response",
        "shadow": "can pull you into defensiveness or overcorrection",
        "gift": "can sharpen your boundaries if you work with it consciously",
    },
    "opposition": {
        "conflict": "puts the tension in plain sight",
        "shadow": "can split you between two extremes",
        "gift": "can teach better balance and better relational intelligence",
    },
    "conjunction": {
        "conflict": "concentrates the pressure in one place",
        "shadow": "can make the whole theme feel louder than it is",
        "gift": "can bring real focus once the energy is given a direction",
    },
    "trine": {
        "conflict": "opens the path more easily than usual",
        "shadow": "can be wasted if you stay passive",
        "gift": "gives you usable momentum",
    },
    "sextile": {
        "conflict": "opens through small, timely moves",
        "shadow": "can stay theoretical if you do nothing with it",
        "gift": "rewards initiative very quickly",
    },
}

DOMAIN_LABEL_EN = {
    "mind": "Mind",
    "career": "Career",
    "relationships": "Relationships",
    "home": "Home",
    "identity": "Identity",
    "money": "Money",
}


def _seed_from_parts(*parts: str) -> int:
    raw = "|".join(str(part or "") for part in parts)
    return int(hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8], 16)


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _sign_name(item: Mapping[str, Any]) -> str:
    signs = item.get("signs") if isinstance(item.get("signs"), Mapping) else {}
    raw = str(signs.get("transit_body_sign") or "").strip()
    return SIGN_EN.get(raw, raw)


def _house_num(item: Mapping[str, Any]) -> int | None:
    houses = item.get("houses") if isinstance(item.get("houses"), Mapping) else {}
    return _safe_int(houses.get("transit_in_natal_house"))


def _target_house_num(item: Mapping[str, Any]) -> int | None:
    houses = item.get("houses") if isinstance(item.get("houses"), Mapping) else {}
    return _safe_int(houses.get("natal_point_house"))


def _planet_label(raw: str) -> str:
    return PLANET_EN.get(str(raw or "").strip(), str(raw or "").strip())


def _point_label(raw: str) -> str:
    value = str(raw or "").strip().upper()
    if value in POINT_EN:
        return POINT_EN[value]
    return _planet_label(str(raw or "").strip())


def _aspect_symbol(aspect: str) -> str:
    return {
        "conjunction": "conjunct",
        "opposition": "opposite",
        "square": "square",
        "trine": "trine",
        "sextile": "sextile",
    }.get(str(aspect or "").strip().lower(), "touching")


def _house_scene(house: int | None) -> str:
    if house is None:
        return "this area of life"
    return HOUSE_SCENE_EN.get(house, "this area of life")


def _house_label(house: int | None) -> str:
    if house is None:
        return "a live area of life"
    return HOUSE_LABEL_EN.get(house, "a live area of life")


def _time_hint_en(item: Mapping[str, Any]) -> str:
    phase = str(item.get("phase") or "").strip().lower()
    bucket = str(item.get("bucket") or "").strip().lower()
    if phase in {"exact", "exactish"}:
        return "peak phase"
    if phase == "applying":
        return "building now"
    if phase == "separating":
        return "already easing"
    if bucket == "long":
        return "long arc"
    if bucket == "medium":
        return "multi-week arc"
    return "short window"


def _ensure_two_sentences(text: str) -> str:
    parts = split_en_sentences(text)
    if not parts:
        return ""
    if len(parts) == 1:
        return f"{parts[0]} A little conscious pacing goes a long way here."
    return f"{parts[0]} {parts[1]}"


def build_signature_text_en(item: Mapping[str, Any]) -> str:
    transit_body = _planet_label(str(item.get("transit_body") or "Transit"))
    natal_point = _point_label(str(item.get("natal_point") or "point"))
    aspect = _aspect_symbol(str(item.get("aspect") or ""))
    sign = _sign_name(item)
    house = _house_num(item)
    scene = _house_label(house)
    sign_part = f" in {sign}" if sign else ""
    house_part = f" through {scene}" if scene else ""
    return humanize_en_text(f"{transit_body} {aspect} {natal_point}{sign_part}{house_part}", max_sentences=1).strip(".")


def _title_for_event_en(item: Mapping[str, Any]) -> str:
    house = _house_num(item)
    aspect = str(item.get("aspect") or "").strip().lower()
    house_title = HOUSE_TITLE_EN.get(house, "A Live Theme")
    if aspect in {"square", "opposition"}:
        return f"{house_title} Under Pressure"
    if aspect in {"trine", "sextile"}:
        return f"Flow Through {house_title}"
    return f"{_planet_label(str(item.get('transit_body') or 'Transit'))} Through {house_title}"


def build_insight_pack_en(
    item: Mapping[str, Any],
    *,
    voice_style: str = "you",
) -> Dict[str, str]:
    _ = voice_style
    transit_body = str(item.get("transit_body") or "Saturn")
    aspect = str(item.get("aspect") or "").lower()
    sign = _sign_name(item)
    house = _house_num(item)
    scene = _house_scene(house)
    tone = ASPECT_TONE_EN.get(aspect, ASPECT_TONE_EN["conjunction"])
    drive = PLANET_DRIVE_EN.get(transit_body, "changes the atmosphere")
    gift = PLANET_GIFTS_EN.get(transit_body, "clearer movement")
    sign_part = f" in {sign}" if sign else ""

    conflict = humanize_en_text(
        f"{transit_body}{sign_part} is working through {scene}, and it {tone['conflict']}. This is the part of life that is asking for a cleaner response from you."
    )
    shadow = humanize_en_text(
        f"The shadow side is that it {tone['shadow']}. If you move too fast, the signal gets louder but not clearer."
    )
    upper = humanize_en_text(
        f"The higher use of this transit is {gift}. At its best, it {tone['gift']}."
    )
    conflict_short = humanize_en_text(
        f"This transit is most noticeable around {scene}.",
        max_sentences=1,
    )
    return {
        "conflict": conflict,
        "shadow": shadow,
        "upper": upper,
        "conflict_short": conflict_short,
    }


def compose_event_summary_en(
    item: Mapping[str, Any],
    *,
    voice_style: str = "you",
) -> str:
    _ = voice_style
    transit_body = str(item.get("transit_body") or "Transit")
    natal_point = _point_label(str(item.get("natal_point") or "point"))
    house = _house_num(item)
    scene = _house_scene(house)
    aspect = str(item.get("aspect") or "").lower()
    tone = ASPECT_TONE_EN.get(aspect, ASPECT_TONE_EN["conjunction"])
    drive = PLANET_DRIVE_EN.get(transit_body, "changes the atmosphere")
    line = (
        f"{_planet_label(transit_body)} is active around {scene} and {drive}. "
        f"In relation to your {natal_point}, it {tone['conflict']}."
    )
    return _ensure_two_sentences(humanize_en_text(line))


def compose_upper_meaning_line_en(
    *,
    transit_body: str,
    natal_target: str,
    house_overlay: int | None,
    seed: int | None = None,
    voice_style: str = "you",
) -> str:
    _ = seed, voice_style
    gift = PLANET_GIFTS_EN.get(transit_body or "Saturn", "clearer movement")
    scene = _house_scene(house_overlay)
    target = _point_label(natal_target)
    return humanize_en_text(
        f"What this can build over time is {gift} around {scene}, especially in the way you handle {target}.",
        max_sentences=1,
    )


def _guidance_items_en(item: Mapping[str, Any]) -> list[str]:
    aspect = str(item.get("aspect") or "").lower()
    house = _house_num(item)
    scene = _house_scene(house)
    items = [
        f"Keep the response simple around {scene}.",
        "Choose one clear move instead of five partial ones.",
    ]
    if aspect in {"square", "opposition"}:
        items.append("Answer the pressure without hardening your tone.")
    else:
        items.append("Use the opening while it is available.")
    return [humanize_en_text(item, max_sentences=1) for item in items]


def _watch_items_en(item: Mapping[str, Any]) -> list[str]:
    aspect = str(item.get("aspect") or "").lower()
    if aspect in {"square", "opposition"}:
        items = [
            "Watch defensiveness.",
            "Do not mistake urgency for clarity.",
        ]
    else:
        items = [
            "Do not stay passive just because the path feels easier.",
            "Avoid opening too many channels at once.",
        ]
    return [humanize_en_text(item, max_sentences=1) for item in items]


def rewrite_period_story_en(story: Mapping[str, Any], *, item: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    event = item or {}
    base = build_insight_pack_en(event) if event else {}
    out = dict(story)
    out["title"] = "What This Period Is Building"
    out["lead"] = humanize_en_text(base.get("conflict_short") or "")
    out["period_opening"] = humanize_en_text(
        f"This period is concentrating pressure around {_house_scene(_house_num(event))}."
    )
    out["big_picture"] = humanize_en_text(compose_event_summary_en(event))
    out["mechanism"] = humanize_en_text(base.get("conflict") or "")
    out["growth_edge"] = humanize_en_text(base.get("shadow") or "")
    out["relational_or_life_expression"] = humanize_en_text(
        f"In daily life this shows up most clearly around {_house_scene(_house_num(event))}."
    )
    builds = compose_upper_meaning_line_en(
        transit_body=str(event.get("transit_body") or ""),
        natal_target=str(event.get("natal_point") or ""),
        house_overlay=_house_num(event),
    )
    out["what_it_builds"] = humanize_en_text(builds)
    out["contribution"] = out["what_it_builds"]
    out["upper_meaning"] = humanize_en_text(out["what_it_builds"])
    return out


def rewrite_event_card_en(card: Mapping[str, Any], item: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    event = item or {}
    out = dict(card)
    insight = build_insight_pack_en(event) if event else {
        "conflict": "",
        "shadow": "",
        "upper": "",
        "conflict_short": "",
    }
    summary = compose_event_summary_en(event) if event else str(out.get("summary") or "")
    upper = compose_upper_meaning_line_en(
        transit_body=str(event.get("transit_body") or out.get("transit_body") or ""),
        natal_target=str(event.get("natal_point") or out.get("natal_point") or ""),
        house_overlay=_house_num(event) or _target_house_num(event),
    )
    signature = build_signature_text_en(event) if event else str(out.get("signature") or "")
    out["title"] = _title_for_event_en(event)
    out["headline"] = out["title"]
    out["signature"] = signature
    out["signature_tr"] = signature
    out["time_hint"] = _time_hint_en(event) if event else str(out.get("time_hint") or "")
    out["time_hint_tr"] = out["time_hint"]
    out["teaser"] = humanize_en_text(insight.get("conflict_short") or summary, max_sentences=2)
    out["opening"] = humanize_en_text(summary)
    out["summary"] = humanize_en_text(summary)
    out["one_liner"] = humanize_en_text(insight.get("conflict_short") or summary, max_sentences=1)
    out["lead"] = out["one_liner"]
    out["essence"] = humanize_en_text(insight.get("conflict") or summary)
    out["why_now"] = humanize_en_text(
        f"This is concentrating around {_house_scene(_house_num(event))}.",
        max_sentences=2,
    )
    out["asks"] = humanize_en_text(upper, max_sentences=2)
    out["watchout"] = humanize_en_text(insight.get("shadow"), max_sentences=2)
    out["what_it_builds"] = humanize_en_text(upper, max_sentences=2)
    out["technical_note"] = humanize_en_text(signature, max_sentences=1)
    out["conflict"] = humanize_en_text(insight.get("conflict"))
    out["shadow"] = humanize_en_text(insight.get("shadow"))
    out["upper"] = humanize_en_text(insight.get("upper"))
    out["upper_meaning"] = humanize_en_text(str(out.get("upper_meaning") or upper))
    out["extra_line"] = humanize_en_text(insight.get("conflict_short"), max_sentences=1)
    out["guidance"] = _guidance_items_en(event) if event else list(out.get("guidance") or [])
    out["watch_out"] = _watch_items_en(event) if event else list(out.get("watch_out") or [])
    out["period_story"] = rewrite_period_story_en(
        out["period_story"] if isinstance(out.get("period_story"), Mapping) else {},
        item=event,
    )
    section_labels = out.get("section_labels")
    if isinstance(section_labels, Mapping):
        out["section_labels"] = {
            "opening": "What is happening",
            "essence": "Why it feels like this",
            "asks": "What it asks of you",
            "watchout": "Watch out for",
            "what_it_builds": "What it is building",
        }
    return out


def rewrite_period_core_en(period_core: Mapping[str, Any], *, item: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    event = item or {}
    out = dict(period_core)
    summary = compose_event_summary_en(event) if event else str(out.get("core_story") or "")
    upper = compose_upper_meaning_line_en(
        transit_body=str(event.get("transit_body") or ""),
        natal_target=str(event.get("natal_point") or ""),
        house_overlay=_house_num(event),
    )
    scene = _house_scene(_house_num(event))
    out["title"] = humanize_en_text(str(out.get("title") or f"Focus Around {scene.title()}"), max_sentences=1).strip(".")
    out["core_story"] = humanize_en_text(str(out.get("core_story") or f"{summary} {upper}".strip()))
    out["period_opening"] = humanize_en_text(
        str(out.get("period_opening") or f"This period is asking for a cleaner response around {scene}.")
    )
    out["big_picture"] = humanize_en_text(str(out.get("big_picture") or summary))
    out["mechanism"] = humanize_en_text(
        str(out.get("mechanism") or build_insight_pack_en(event).get("conflict") or "")
    )
    out["growth_edge"] = humanize_en_text(
        str(out.get("growth_edge") or build_insight_pack_en(event).get("shadow") or "")
    )
    out["relational_or_life_expression"] = humanize_en_text(
        str(out.get("relational_or_life_expression") or f"In daily life, you are most likely to notice it around {scene}.")
    )
    out["what_it_builds"] = humanize_en_text(str(out.get("what_it_builds") or upper))
    out["contribution"] = humanize_en_text(str(out.get("contribution") or out["what_it_builds"]))
    out["upper_meaning"] = humanize_en_text(str(out.get("upper_meaning") or upper))
    tags = out.get("tags")
    if isinstance(tags, list):
        rewritten = []
        for tag in tags:
            if not isinstance(tag, Mapping):
                rewritten.append(tag)
                continue
            tag_out = dict(tag)
            if "label" in tag_out:
                tag_out["label"] = humanize_en_text(str(tag_out.get("label") or ""), max_sentences=1).strip(".")
            if "value" in tag_out:
                tag_out["value"] = humanize_en_text(str(tag_out.get("value") or ""), max_sentences=1).strip(".")
            rewritten.append(tag_out)
        out["tags"] = rewritten
    story_tracks = out.get("story_tracks")
    if isinstance(story_tracks, Mapping):
        out["story_tracks"] = {
            str(track_id): rewrite_period_story_en(track_story, item=event)
            if isinstance(track_story, Mapping)
            else track_story
            for track_id, track_story in story_tracks.items()
        }
    period_reading_v1 = out.get("period_reading_v1")
    if isinstance(period_reading_v1, Mapping):
        reading_out = dict(period_reading_v1)
        blocks = reading_out.get("blocks")
        if isinstance(blocks, list):
            rewritten_blocks = []
            for block in blocks:
                if not isinstance(block, Mapping):
                    rewritten_blocks.append(block)
                    continue
                block_out = dict(block)
                block_out["text"] = humanize_en_text(str(block_out.get("text") or ""))
                rewritten_blocks.append(block_out)
            reading_out["blocks"] = rewritten_blocks
            reading_out["full_text"] = "\n\n".join(
                str(block.get("text") or "").strip()
                for block in rewritten_blocks
                if isinstance(block, Mapping) and str(block.get("text") or "").strip()
            )
        elif "full_text" in reading_out:
            reading_out["full_text"] = humanize_en_text(str(reading_out.get("full_text") or ""))
        out["period_reading_v1"] = reading_out
    return out


def rewrite_period_summary_en(period: Mapping[str, Any], *, item: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    event = item or {}
    out = dict(period)
    core_story = str(out.get("core_story") or "").strip() or compose_event_summary_en(event)
    summary = out.get("summary") if isinstance(out.get("summary"), Mapping) else {}
    out["core_story"] = humanize_en_text(core_story)
    out["summary"] = {
        "main_theme": DOMAIN_LABEL_EN.get(str(summary.get("main_theme") or "").lower(), str(summary.get("main_theme") or "Focus")),
        "one_liner": humanize_en_text(str(summary.get("one_liner") or core_story), max_sentences=2),
    }
    return out
