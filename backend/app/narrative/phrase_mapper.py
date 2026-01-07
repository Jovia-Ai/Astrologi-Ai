"""Deterministic slot text -> intent/voice/polarity tags."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class MappedItem:
    domain: str
    slot: str
    text: str
    salience: float
    intent: str
    voice: str
    polarity: str


INTENT_KEYWORDS: dict[str, list[str]] = {
    "visibility": ["görün", "kabul", "fark edil", "sahne", "onay", "beğen"],
    "control": ["kontrol", "düzen", "disiplin", "plan", "sınır", "ciddi", "sorumluluk"],
    "security": ["güven", "istikrar", "garanti", "risk", "dayan", "sağlam"],
    "depth": ["derin", "yoğun", "yakın", "bağ", "iç dünya", "hassas"],
    "autonomy": ["bağımsız", "özgür", "kendi", "alan", "mesafe"],
    "worth": ["değer", "yeter", "kanıt", "hak", "başarı", "saygı"],
}

VOICE_KEYWORDS: dict[str, list[str]] = {
    "outer_perception": ["dışarıdan", "insanlar", "algılan", "görünürsün"],
    "inner_state": ["içinde", "içten", "hissedersin", "zorlan", "kaygı", "yara"],
    "behavior": ["yaparsın", "gidersin", "kaçarsın", "kurarsın", "seçersin"],
    "question": ["mı?", "mi?", "soru", "acaba", "neden"],
}

POLARITY_KEYWORDS: dict[str, list[str]] = {
    "tension": ["gerilim", "zor", "çatış", "yara", "korku", "baskı", "kaçın"],
    "support": ["güç", "destek", "kolay", "akış", "rahat", "denge"],
}


def map_slot_item(item: Mapping[str, Any]) -> MappedItem:
    domain = str(item.get("domain") or "").strip().lower()
    slot = str(item.get("slot") or "").strip().lower()
    text = str(item.get("text") or "").strip()
    salience = _safe_float(item.get("salience")) or _safe_float(item.get("salience_score"))
    intent = detect_intent(text)
    voice = detect_voice(text)
    polarity = detect_polarity(text)
    return MappedItem(
        domain=domain,
        slot=slot,
        text=text,
        salience=salience,
        intent=intent,
        voice=voice,
        polarity=polarity,
    )


def detect_intent(text: str) -> str:
    lowered = text.lower()
    best_intent = "generic"
    best_score = 0
    for intent, keywords in INTENT_KEYWORDS.items():
        score = _keyword_score(lowered, keywords)
        if score > best_score:
            best_score = score
            best_intent = intent
    return best_intent


def detect_voice(text: str) -> str:
    lowered = text.lower()
    if _keyword_score(lowered, VOICE_KEYWORDS["outer_perception"]) > 0:
        return "outer_perception"
    if _keyword_score(lowered, VOICE_KEYWORDS["question"]) > 0:
        return "question"
    if _keyword_score(lowered, VOICE_KEYWORDS["inner_state"]) > 0:
        return "inner_state"
    if _keyword_score(lowered, VOICE_KEYWORDS["behavior"]) > 0:
        return "behavior"
    return "inner_state"


def detect_polarity(text: str) -> str:
    lowered = text.lower()
    if _keyword_score(lowered, POLARITY_KEYWORDS["tension"]) > 0:
        return "tension"
    if _keyword_score(lowered, POLARITY_KEYWORDS["support"]) > 0:
        return "support"
    return "neutral"


def _keyword_score(text: str, keywords: Sequence[str]) -> int:
    return sum(1 for keyword in keywords if keyword in text)


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
