from __future__ import annotations

import hashlib
import re
from typing import Any, Dict, List, Mapping, Sequence

from app.narrative.editorial_render_policy import (
    editorialize_micro,
    editorialize_teaser,
    opening_key,
    quality_issues,
)
from app.narrative.humanize_en import humanize_en_text


RENDER_MODES = ("A", "B", "C", "D")

MODE_LABELS_EN = {
    "A": "direct",
    "B": "observational",
    "C": "editorial",
    "D": "intimate",
}


TITLE_FAMILIES_EN: Dict[str, List[str]] = {
    "identity_aura": [
        "The Way You Come Across",
        "Your Outer Signature",
        "What People Meet First",
        "The Spine Of Your Presence",
    ],
    "mind_voice": [
        "How Your Mind Moves",
        "Your Inner Pace",
        "The Way You Process",
        "What Sits Behind Your Words",
    ],
    "drive_rhythm": [
        "Where Your Momentum Lives",
        "Your Working Rhythm",
        "How You Build Momentum",
        "What Gives You Traction",
    ],
    "love_depth": [
        "How You Open In Love",
        "Your Bonding Style",
        "What Intimacy Feels Like",
        "Where Your Heart Softens",
    ],
    "career_visibility": [
        "How You Become Visible",
        "What People Notice In Your Work",
        "Your Public Rhythm",
        "How Your Work Lands",
    ],
    "home_roots": [
        "Where You Reset",
        "What Home Does For You",
        "Your Inner Base",
        "How You Come Back To Yourself",
    ],
    "luck_creation": [
        "How Opportunity Opens",
        "Where Life Starts Moving",
        "Your Creative Luck",
        "The Door That Opens For You",
    ],
}


BODY_TEMPLATES_EN: Dict[str, Dict[str, str]] = {
    block_id: {
        "A": (
            "{copy.core} "
            "{copy.mechanism} "
            "Under pressure, {copy.shadow_lower}. "
            "At its best, {copy.gift_lower}."
        ),
        "B": (
            "People often notice this first: {copy.core_lower}. "
            "In real life it tends to work like this: {copy.mechanism_lower}. "
            "When the system is strained, {copy.shadow_lower}. "
            "When you are in rhythm, {copy.gift_lower}."
        ),
        "C": (
            "You can look one way on the outside, but underneath it works like this: {copy.core_lower}. "
            "The deeper mechanism sits here: {copy.mechanism_lower}. "
            "Its shadow side is that {copy.shadow_lower}. "
            "Its mature expression is that {copy.gift_lower}."
        ),
        "D": (
            "{copy.core} "
            "On the inside, it usually works like this: {copy.mechanism_lower}. "
            "The vulnerable edge is that {copy.shadow_lower}. "
            "The stronger expression is that {copy.gift_lower}."
        ),
    }
    for block_id in TITLE_FAMILIES_EN
}


SOFT_ASTRO_HINTS_EN: Dict[str, List[str]] = {
    "identity_aura": [
        "There is both structure and individuality in the way you come across.",
        "Your chart carries backbone, but it also resists becoming generic.",
        "People meet both steadiness and self-direction in you.",
    ],
    "mind_voice": [
        "Your mind is working with both clarity and self-monitoring.",
        "There is precision in the way you think, but also a strong inner filter.",
        "Your words tend to come from an internal process, not impulse alone.",
    ],
    "drive_rhythm": [
        "You do well when meaning and method start working together.",
        "Momentum grows when you can turn instinct into structure.",
        "Your best drive tends to come with both direction and form.",
    ],
    "love_depth": [
        "For you, closeness works best when warmth and emotional safety move together.",
        "You do not open on chemistry alone; trust needs to be there too.",
        "In love, depth matters as much as feeling.",
    ],
    "career_visibility": [
        "Your public life is tied to both quality and timing.",
        "You want the work to feel solid before it becomes visible.",
        "Visibility matters, but craftsmanship matters just as much.",
    ],
    "home_roots": [
        "Your private space is closely tied to how you regulate yourself.",
        "Home is not just shelter for you; it is recalibration.",
        "Your inner base works best when it feels orderly and emotionally safe.",
    ],
    "luck_creation": [
        "Things tend to open when expression, courage, and timing align.",
        "Opportunity grows when you stop hovering and make something visible.",
        "Your chart opens up when instinct turns into expression.",
    ],
}


DEFAULT_PUBLIC_CHIPS_EN: Dict[str, List[str]] = {
    "identity_aura": ["Presence", "Self-Definition", "Direction"],
    "mind_voice": ["Inner Pace", "Clarity", "Tone"],
    "drive_rhythm": ["Momentum", "Method", "Traction"],
    "love_depth": ["Trust", "Closeness", "Depth"],
    "career_visibility": ["Craft", "Visibility", "Impact"],
    "home_roots": ["Reset", "Grounding", "Inner Base"],
    "luck_creation": ["Opening", "Expression", "Flow"],
}


CHIP_REPLACEMENTS_EN = {
    "Aidiyet": "Belonging",
    "Akış": "Flow",
    "Analiz": "Analysis",
    "Anlatı": "Narrative",
    "Ayna": "Mirror",
    "Ayna Etkisi": "Mirror Effect",
    "Ağırlık": "Weight",
    "Bağımsızlık": "Independence",
    "Büyük Resim": "Big Picture",
    "Derin Bağ": "Deep Bond",
    "Derinlik": "Depth",
    "Duruş": "Presence",
    "Eşitlik": "Equality",
    "Gelir": "Income",
    "Görünürlük": "Visibility",
    "Güven": "Trust",
    "Güç": "Strength",
    "Güçlü Benlik": "Strong Self",
    "Hedef": "Direction",
    "Kendi Çizgin": "Own Line",
    "Keyif": "Joy",
    "Kök": "Roots",
    "Net Cümle": "Clear Language",
    "Net Duruş": "Clear Presence",
    "Net Mesaj": "Clear Message",
    "Strong Self": "Presence",
    "Tone": "Tone",
    "Boundary": "Boundaries",
    "Pattern": "Pattern Sense",
    "Network": "Connections",
    "Upgrade": "Growth",
    "Rafine": "Refinement",
    "Ritim": "Rhythm",
    "Sadakat": "Loyalty",
    "Sahne": "Stage Presence",
    "Sezgi": "Intuition",
    "Somut Sonuç": "Concrete Results",
    "Sorumluluk": "Responsibility",
    "Ton": "Tone",
    "Ufuk": "Horizon",
    "Ustalık": "Mastery",
    "Vizyon": "Vision",
    "Yakınlık": "Closeness",
    "Yaratım": "Creation",
    "Yenilik": "Innovation",
    "Yön": "Direction",
    "Yöntem": "Method",
    "Yüksek Standart": "High Standards",
    "Zemin": "Grounding",
    "Zihin Gücü": "Mental Strength",
    "Çerçeve": "Structure",
    "Öz Güven": "Confidence",
    "Özgün Yol": "Originality",
    "İç Denge": "Inner Balance",
    "İç Güven": "Inner Security",
    "Şarj": "Recharge",
}

KNOWN_PUBLIC_CHIPS_EN = {
    value
    for value in CHIP_REPLACEMENTS_EN.values()
} | {
    chip
    for chips in DEFAULT_PUBLIC_CHIPS_EN.values()
    for chip in chips
}


TECH_ASTRO_PATTERN = re.compile(
    r"(\b(?:sun|moon|mercury|venus|mars|jupiter|saturn|uranus|neptune|pluto)\b|"
    r"\b(?:asc|mc|ic|dsc|midheaven|ascendant|descendant)\b|"
    r"\b\d{1,2}(?:st|nd|rd|th)\s+house\b|"
    r"\b(?:square|opposition|conjunction|trine|sextile|stellium|ruler)\b)",
    re.IGNORECASE,
)

TECH_CHIP_PATTERN = re.compile(
    r"(\b\d{1,2}(?:st|nd|rd|th)\s+house\b|"
    r"\b(?:saturn|mercury|mars|venus|jupiter|uranus|neptune|pluto|asc|mc|ic|dsc)\b|"
    r"[+/])",
    re.IGNORECASE,
)


def _stable_int(seed: str) -> int:
    return int(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:8], 16)


def _cleanup(text: str, *, max_sentences: int = 4) -> str:
    return humanize_en_text(text, max_sentences=max_sentences)


def _cleanup_fragment(text: str) -> str:
    value = str(text or "").strip()
    if not value:
        return ""
    value = re.sub(r"[.!?]+$", "", value).strip()
    value = value.replace(";", ",").replace(":", ",")
    value = re.sub(r"\s+", " ", value).strip(" ,")
    return value


class _SafeDict(dict[str, Any]):
    def __missing__(self, key: str) -> str:
        return ""


def _normalize_copy_fragment(text: str) -> str:
    value = _cleanup_fragment(text)
    if not value:
        return ""
    return value[:1].lower() + value[1:]


def _render_text(template: str, slots: Mapping[str, Any], *, max_sentences: int) -> str:
    local = dict(slots)
    copy_payload = {k: str(v or "") for k, v in dict(local.get("copy") or {}).items()}
    defaults = {
        "core": "There is a clear inner line running through the way you move.",
        "mechanism": "More than one internal signal is active at the same time.",
        "shadow": "pressure can make you tighten around the wrong thing",
        "gift": "the mature version of this feels clearer, calmer, and more effective",
    }
    for field, default in defaults.items():
        if not str(copy_payload.get(field) or "").strip():
            copy_payload[field] = default
    for field in ("headline", "teaser", "core", "mechanism", "shadow", "gift", "spark", "watch"):
        copy_payload.setdefault(field, "")
        copy_payload[f"{field}_lower"] = _normalize_copy_fragment(copy_payload.get(field, ""))

    rendered = str(template or "")
    for field, value in copy_payload.items():
        rendered = rendered.replace(f"{{copy.{field}}}", value)
    rendered = rendered.format_map(_SafeDict({key: value for key, value in local.items() if key != "copy"}))
    return _cleanup(rendered, max_sentences=max_sentences)


def _candidate_modes(seed: str, block_id: str, signature_id: str, preferred_family: str = "") -> List[str]:
    start_index = _stable_int(f"{seed}|{block_id}|{signature_id}|mode") % len(RENDER_MODES)
    ordered = list(RENDER_MODES[start_index:]) + list(RENDER_MODES[:start_index])
    preferred_mode = next((mode for mode, label in MODE_LABELS_EN.items() if label == preferred_family), "")
    if preferred_mode and preferred_mode in ordered:
        ordered.remove(preferred_mode)
        ordered.insert(0, preferred_mode)
    return ordered


def _select_title(block_id: str, seed: str, mode: str, signature_id: str) -> tuple[int, str]:
    titles = TITLE_FAMILIES_EN.get(block_id) or [""]
    index = _stable_int(f"{seed}|{block_id}|{signature_id}|{mode}|headline") % len(titles)
    return index, str(titles[index])


def _is_technical_hint(text: str) -> bool:
    value = str(text or "").strip()
    return bool(value and TECH_ASTRO_PATTERN.search(value))


def soft_public_astro_hint(
    block_id: str,
    raw_hint: str | None,
    *,
    seed: str = "",
    signature_id: str = "",
) -> str:
    value = str(raw_hint or "").strip()
    if value and not _is_technical_hint(value) and len(value) <= 110:
        return _cleanup(value, max_sentences=1)
    hints = SOFT_ASTRO_HINTS_EN.get(block_id) or [""]
    index = _stable_int(f"{seed}|{block_id}|{signature_id}|{value}|astro_hint") % len(hints)
    return _cleanup(str(hints[index]), max_sentences=1)


def humanize_public_chips(block_id: str, chips: Sequence[Any] | None) -> List[str]:
    out: List[str] = []
    seen: set[str] = set()
    for chip in chips or []:
        value = CHIP_REPLACEMENTS_EN.get(str(chip or "").strip(), str(chip or "").strip())
        if (
            not value
            or TECH_CHIP_PATTERN.search(value)
            or re.search(r"[çğıöşüÇĞİÖŞÜ]", value)
            or value not in KNOWN_PUBLIC_CHIPS_EN
        ):
            continue
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
        if len(out) >= 3:
            return out
    for fallback in DEFAULT_PUBLIC_CHIPS_EN.get(block_id, []):
        key = fallback.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(fallback)
        if len(out) >= 3:
            break
    return out


def render_block_template(
    *,
    block_id: str,
    seed: str,
    slots: Mapping[str, Any],
    signature_id: str = "",
    preferred_family: str = "",
    used_openings: Sequence[str] | None = None,
    used_bodies: Sequence[str] | None = None,
) -> Dict[str, Any]:
    copy_payload = (slots.get("copy") or {}) if isinstance(slots.get("copy"), Mapping) else {}
    teaser_seed = str(copy_payload.get("teaser") or copy_payload.get("core") or "").strip()
    best_payload: Dict[str, Any] | None = None

    for mode in _candidate_modes(seed, block_id, signature_id, preferred_family):
        title_index, headline = _select_title(block_id, seed, mode, signature_id)
        family = MODE_LABELS_EN.get(mode, "direct")
        body_template = ((BODY_TEMPLATES_EN.get(block_id) or {}).get(mode)) or "{copy.core}. {copy.mechanism}. {copy.shadow}. {copy.gift}."
        teaser = editorialize_teaser(teaser_seed, family)
        teaser = _cleanup(teaser, max_sentences=2) if teaser else ""
        micro = _cleanup(editorialize_micro(str(slots.get("micro") or ""), family), max_sentences=1)
        body = _render_text(body_template, slots, max_sentences=4)
        issues = quality_issues(
            teaser=teaser,
            body=body,
            micro=micro,
            used_openings=used_openings,
            used_bodies=used_bodies,
        )
        candidate = {
            "headline": _cleanup(headline, max_sentences=1).strip(" ."),
            "teaser": teaser,
            "body": body,
            "micro": micro,
            "mode": mode,
            "mode_label": family,
            "template_index": RENDER_MODES.index(mode),
            "title_index": title_index,
            "quality_issues": issues,
            "opening_key": opening_key(body),
        }
        if best_payload is None or len(issues) < len(best_payload.get("quality_issues") or []):
            best_payload = candidate
        if not issues:
            best_payload = candidate
            break

    return best_payload or {
        "headline": "",
        "teaser": "",
        "body": "",
        "micro": "",
        "mode": "A",
        "mode_label": "direct",
        "template_index": 0,
        "title_index": 0,
        "quality_issues": [],
        "opening_key": "",
    }
