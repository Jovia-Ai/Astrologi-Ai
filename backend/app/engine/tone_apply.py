from __future__ import annotations

import re
from typing import Mapping

from app.engine.tone_profile import ToneProfile, load_tone_config

HEDGE_LOW = ("bazen", "olabilir", "tetiklenince")
HEDGE_MID = ("genelde", "siklikla", "cogu zaman")

INTENSITY_TOKENS = ("tema", "egilim", "gerilim", "baski", "yuk", "yogunluk")

CERTAINTY_REWRITES_LOW = {
    "baskin bir psikolojik akistir": "baskin bir psikolojik akis olabilir",
    "yonune dogru akar": "yonune dogru akabilir",
    "kapasitesi belirir": "kapasitesi beliriyor olabilir",
}

SOFTENER = "Sunu fark etmek iyi gelebilir:"


def apply_tone(text: str, tone: ToneProfile, *, section: str) -> str:
    if not isinstance(text, str) or not text.strip():
        return ""

    config = load_tone_config()
    thresholds: Mapping[str, float] = config.get("tone_thresholds", {})
    certainty_hi = max(float(thresholds.get("certainty_hi", 0.75)), 0.85)
    certainty_mid = float(thresholds.get("certainty_mid", 0.45))
    directness_hi = max(float(thresholds.get("directness_hi", 0.65)), 0.7)
    warmth_hi = float(thresholds.get("warmth_hi", 0.65))
    tempo_hi = float(thresholds.get("tempo_hi", 0.65))
    distance_hi = float(thresholds.get("distance_hi", 0.6))

    cleaned = " ".join(text.strip().split())
    if section == "shadow" and not _looks_like_shadow_template(cleaned):
        cleaned = _apply_shadow_template(cleaned, tone, config)

    cleaned = _apply_intensity(cleaned, tone)
    cleaned = _apply_ethics_guard(cleaned)
    cleaned = _apply_certainty(cleaned, tone, certainty_hi, certainty_mid)
    if section == "recognition" and tone.directness >= directness_hi and tone.distance <= distance_hi:
        cleaned = _strip_leading_preface(cleaned)
        cleaned = _reduce_hedges_half(cleaned)
    cleaned = _apply_directness(cleaned, tone, directness_hi, distance_hi)
    cleaned = _apply_warmth(cleaned, tone, section, warmth_hi)
    cleaned = _apply_tempo(cleaned, tone, tempo_hi)
    cleaned = _normalize_punctuation(cleaned)

    return _ensure_sentence(cleaned)


def _apply_shadow_template(text: str, tone: ToneProfile, config: Mapping[str, object]) -> str:
    template = (
        config.get("shadow_safety", {}) or {}
    ).get(
        "template",
        "Golge tarafinda bu, {shadow_text} baskisini hissettirebilir; "
        "bu bir suc degil, sadece bir yuklenme alanidir.",
    )
    return template.format(shadow_text=text)


def _looks_like_shadow_template(text: str) -> bool:
    lowered = text.strip().lower()
    return lowered.startswith("golge tarafinda")


def _apply_intensity(text: str, tone: ToneProfile) -> str:
    if tone.intensity < 0.45:
        word = "tema"
        word_obj = "temayi"
    elif tone.intensity < 0.7:
        word = "gerilim"
        word_obj = "gerilimi"
    else:
        word = "yuk"
        word_obj = "yuku"
    if "[INTENSITY_OBJ]" in text:
        return text.replace("[INTENSITY_OBJ]", word_obj)
    if "[INTENSITY]" in text:
        return text.replace("[INTENSITY]", word)
    pattern = re.compile(rf"\\b({'|'.join(INTENSITY_TOKENS)})\\b", re.IGNORECASE)
    if pattern.search(text):
        return pattern.sub(word, text, count=1)
    return text


def _apply_certainty(text: str, tone: ToneProfile, high: float, mid: float) -> str:
    lowered = text.lower()
    if tone.certainty >= high:
        text = _normalize_hedges_high(text)
        text = _rewrite_certainty_low(text)
        return text
    if tone.certainty >= mid:
        return text
    softened = _rewrite_certainty_low(text)
    return softened


def _apply_directness(text: str, tone: ToneProfile, directness_hi: float, distance_hi: float) -> str:
    use_second_person = tone.directness >= directness_hi and tone.distance <= distance_hi
    if use_second_person:
        text = _replace_leading(text, "Bu harita", "Senin haritan")
        text = _replace_leading(text, "Bu yapı", "Senin yapin")
        text = _replace_leading(text, "Bu", "Sen")
        return text
    text = _replace_leading(text, "Senin haritan", "Bu harita")
    text = _replace_leading(text, "Senin yapin", "Bu yapi")
    text = _replace_leading(text, "Sen", "Bu yapi")
    return text


def _apply_warmth(text: str, tone: ToneProfile, section: str, warmth_hi: float) -> str:
    return text


def _apply_tempo(text: str, tone: ToneProfile, tempo_hi: float) -> str:
    if tone.tempo < tempo_hi:
        return text
    if ";" in text:
        return text.replace(";", ".")
    if len(text) > 140 and " ve " in text:
        return text.replace(" ve ", ". ", 1)
    if len(text) > 160 and ", " in text:
        parts = text.split(", ", 1)
        return ". ".join(parts)
    return text


def _strip_tokens(text: str, tokens: tuple[str, ...]) -> str:
    cleaned = text
    for token in tokens:
        pattern = re.compile(rf"\b{re.escape(token)}\b", re.IGNORECASE)
        cleaned = pattern.sub("", cleaned)
    return " ".join(cleaned.split())


def _strip_hedges_high(text: str) -> str:
    pattern = re.compile(r"\b(olabilir|gibi|muhtemelen|bazen|genelde)\b", re.IGNORECASE)
    cleaned = pattern.sub("", text)
    return " ".join(cleaned.split())


def _normalize_hedges_high(text: str) -> str:
    pattern = re.compile(r"\b(olabilir|gibi|muhtemelen|bazen|genelde)\b", re.IGNORECASE)
    normalized = pattern.sub("cogu zaman", text)
    normalized = re.sub(r"\b(cogu zaman)(\s+cogu zaman)+\b", "cogu zaman", normalized, flags=re.IGNORECASE)
    return " ".join(normalized.split())


def _strip_leading_preface(text: str) -> str:
    cleaned = text.strip()
    for prefix in ("Genelde,", "Bazen,", "Genellikle,"):
        if cleaned.lower().startswith(prefix.lower()):
            cleaned = cleaned[len(prefix):].lstrip()
            break
    return cleaned


def _rewrite_certainty_low(text: str) -> str:
    lowered = text.lower()
    for needle, replacement in CERTAINTY_REWRITES_LOW.items():
        if needle in lowered:
            pattern = re.compile(re.escape(needle), re.IGNORECASE)
            return pattern.sub(replacement, text)
    return text


def _replace_leading(text: str, needle: str, replacement: str) -> str:
    pattern = re.compile(rf"^{re.escape(needle)}\b", re.IGNORECASE)
    replaced = pattern.sub(replacement, text, count=1)
    if replaced == text and "," in text:
        head, rest = text.split(",", 1)
        replaced_head = pattern.sub(replacement, head, count=1)
        if replaced_head != head:
            return f"{replaced_head},{rest}"
    return replaced


def _ensure_sentence(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return ""
    if stripped[-1] not in ".!?":
        stripped += "."
    return stripped[0].upper() + stripped[1:]


def _reduce_hedges_half(text: str) -> str:
    tokens = text.split()
    hedge_set = {word.lower() for word in HEDGE_LOW + HEDGE_MID}
    reduced: list[str] = []
    hedge_count = 0
    for token in tokens:
        key = token.strip(",.").lower()
        if key in hedge_set:
            hedge_count += 1
            if hedge_count % 2 == 0:
                reduced.append(token)
            continue
        reduced.append(token)
    return " ".join(reduced)


def _apply_ethics_guard(text: str) -> str:
    cleaned = re.sub(r"\bkader\b", "yapi", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bkesin\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(
        r"\b(sen|siz)\s+boylesin\b",
        "senin sistemin boyle calisir",
        cleaned,
        flags=re.IGNORECASE,
    )
    return " ".join(cleaned.split())


def _normalize_punctuation(text: str) -> str:
    cleaned = text.replace(", ,", ",")
    cleaned = re.sub(r"^Genelde,\s*Cunku", "Genelde, cunku", cleaned, flags=re.IGNORECASE)
    return cleaned
