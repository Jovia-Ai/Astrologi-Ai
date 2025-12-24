from __future__ import annotations

import re
from typing import Mapping

CONNECTOR_PREFIXES = (
    "bu yapı",
    "bu durum",
    "bu nedenle",
    "bu süreçte",
    "ancak",
    "yine de",
    "bu bakımdan",
)

TEMPORAL_MARKERS = (
    "ne zaman",
    "her zaman",
    "sürekli",
    "şimdi",
    "her an",
    "yakın zamanda",
    "artık",
)

PROGRESSIVE_SUFFIXES = ("ıyor", "iyor", "uyor", "üyor")
INTENT_SUFFIXES = ("acak", "ecek")
TRACE_SUFFIXES = ("miş", "mış", "muş", "müş")
HELPER_SUFFIXES = ("dır", "dir", "dur", "dür", "tır", "tir", "tur", "tür", "olur", "eder", "yapar")

VERB_SUFFIX_PATTERN = re.compile(
    r"\b\w{3,}(?:mak|mek|iyor|ıyor|uyor|üyor|acak|ecek|ebil|ebilir|miş|mış|muş|müş|yor)\b",
    re.IGNORECASE,
)

_SLOT_STRATEGIES: Mapping[str, Mapping[str, bool]] = {
    "cause": {
        "strip_connectors": True,
        "strip_temporal_markers": True,
        "aggressive_nominalization": True,
    },
    "mechanism": {
        "strip_connectors": True,
        "strip_temporal_markers": True,
        "aggressive_nominalization": True,
    },
    "effect": {
        "strip_connectors": True,
        "strip_temporal_markers": False,
        "aggressive_nominalization": False,
    },
    "shadow": {
        "strip_connectors": True,
        "strip_temporal_markers": False,
        "aggressive_nominalization": False,
    },
    "potential": {
        "strip_connectors": True,
        "strip_temporal_markers": True,
        "aggressive_nominalization": True,
    },
}
_DEFAULT_STRATEGY = {
    "strip_connectors": True,
    "strip_temporal_markers": True,
    "aggressive_nominalization": True,
}


def normalize_slot_text(text: str | None, slot_name: str | None = None) -> str | None:
    """Normalize a slot text with slot-aware tuning and safe fallbacks."""

    if not text:
        return None
    base = str(text).strip()
    if not base:
        return None
    base = re.sub(r"[.!?]+$", "", base).strip()

    strategy = _slot_strategy(slot_name)
    stripped = _drop_connectors(base) if strategy["strip_connectors"] else base
    cleaned = _strip_subjects(stripped)
    timed = _strip_temporal_markers(cleaned) if strategy["strip_temporal_markers"] else cleaned
    should_nominalize = strategy["aggressive_nominalization"] and _should_aggressively_nominalize(timed)
    normalized_candidate = (
        nominalize_text(timed, aggressive=True) if should_nominalize else timed
    )

    final = normalized_candidate.strip(" ,")
    if final:
        return final

    for candidate in (
        normalized_candidate,
        timed,
        cleaned,
        stripped,
        base,
    ):
        fallback = candidate.strip(" ,") if candidate else ""
        if fallback:
            return fallback
    return None


def contains_verb_phrase(text: str | None) -> bool:
    if not text:
        return False
    return bool(VERB_SUFFIX_PATTERN.search(text))


def nominalize_text(text: str, *, aggressive: bool = True) -> str:
    """Turn verb-heavy fragments into nominal forms via simple heuristics."""

    if not text:
        return ""
    words = text.split()
    nominalized_words: list[str] = []
    for word in words:
        nominalized = _nominalize_word(word, aggressive)
        if nominalized:
            nominalized_words.append(nominalized)
    return " ".join(nominalized_words)


def _slot_strategy(slot_name: str | None) -> Mapping[str, bool]:
    if not slot_name:
        return _DEFAULT_STRATEGY
    return _SLOT_STRATEGIES.get(slot_name, _DEFAULT_STRATEGY)


def _drop_connectors(text: str) -> str:
    lower = text.lower()
    for prefix in CONNECTOR_PREFIXES:
        if lower.startswith(prefix):
            return text[len(prefix) :].strip()
    return text


def _strip_subjects(text: str) -> str:
    cleaned = re.sub(r"\bseni\b", "", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bsenin\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bbiri\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bolarak\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bgibi\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bşeklinde\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\btarzında\b", "", cleaned, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", cleaned).strip()


def _strip_temporal_markers(text: str) -> str:
    cleaned = text
    for marker in TEMPORAL_MARKERS:
        pattern = rf"\b{re.escape(marker)}\b"
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", cleaned).strip()


def _nominalize_word(word: str, aggressive: bool) -> str:
    cleaned = word.strip(" ,.-")
    if not cleaned:
        return ""
    lowered = cleaned.lower()

    for suffix in HELPER_SUFFIXES:
        if lowered.endswith(suffix) and len(cleaned) > len(suffix):
            candidate = cleaned[: -len(suffix)].strip(" ,.-")
            if candidate:
                return candidate

    for suffix in PROGRESSIVE_SUFFIXES:
        idx = lowered.find(suffix)
        if idx > 0:
            root = cleaned[:idx].strip(" ,.-")
            if root:
                return f"{root}ma"

    if aggressive:
        for suffix in INTENT_SUFFIXES:
            idx = lowered.find(suffix)
            if idx > 0:
                root = cleaned[:idx].strip(" ,.-")
                if root:
                    return f"{root}ma"
        for suffix in TRACE_SUFFIXES:
            idx = lowered.find(suffix)
            if idx > 0:
                root = cleaned[:idx].strip(" ,.-")
                if root:
                    return f"{root}ma"

    return cleaned


def _should_aggressively_nominalize(text: str) -> bool:
    words = [word for word in text.split() if word]
    if not words:
        return False
    lower = text.lower()
    connectors_start = any(lower.startswith(prefix) for prefix in CONNECTOR_PREFIXES)
    short_text = len(words) <= 8 or (connectors_start and len(words) <= 12)
    if not short_text:
        return False
    verb_count = sum(1 for word in words if VERB_SUFFIX_PATTERN.search(word))
    return verb_count < max(1, len(words) // 2)
