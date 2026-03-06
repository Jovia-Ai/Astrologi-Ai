from __future__ import annotations

from typing import Iterable, List

from app.transit.narrative.models import UIBlock

SPACE_HUB_PRIORITY = ["alert", "daily_energy", "core_theme", "best_time_primary", "support"]
PERSONAL_ORDER = ["core_theme", "challenge", "support", "long_term", "clarity", "best_time_primary"]
CALENDAR_DAY_ORDER = ["alert", "daily_energy", "best_time_primary", "event_list_preview"]
FEED_ORDER = ["alert", "daily_energy", "core_theme", "support", "challenge"]


def word_count(text: str) -> int:
    return len([tok for tok in (text or "").strip().split() if tok])


def _first_sentence(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    for sep in (". ", "! ", "? "):
        if sep in text:
            return text.split(sep, 1)[0].strip() + text[text.find(sep)]
    return text


def enforce_word_limit(blocks: Iterable[UIBlock], *, max_words: int) -> List[UIBlock]:
    kept: List[UIBlock] = []
    total = 0
    for block in blocks:
        words = word_count(block.copy.short)
        if total + words <= max_words:
            kept.append(block)
            total += words
            continue
        shortened = _first_sentence(block.copy.short)
        shortened_words = word_count(shortened)
        if shortened and total + shortened_words <= max_words:
            block.copy.short = shortened
            kept.append(block)
            total += shortened_words
    return kept


def ordered(blocks: Iterable[UIBlock], priority: list[str]) -> List[UIBlock]:
    by_type = {t: [] for t in priority}
    rest = []
    for block in blocks:
        if block.type in by_type:
            by_type[block.type].append(block)
        else:
            rest.append(block)
    out: List[UIBlock] = []
    for key in priority:
        out.extend(by_type[key])
    out.extend(rest)
    return out
