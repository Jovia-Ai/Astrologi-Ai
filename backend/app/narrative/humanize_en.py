from __future__ import annotations

import re
from typing import Any, Mapping


def cleanup_en_punctuation(text: str) -> str:
    out = str(text or "").strip()
    if not out:
        return ""
    out = re.sub(r"\s+([,.;:!?])", r"\1", out)
    out = re.sub(r"([,.;:!?])([^\s])", r"\1 \2", out)
    out = re.sub(r"\s+", " ", out).strip()
    out = re.sub(r"([.!?])[.!?]+", r"\1", out)
    return out


def split_en_sentences(text: str) -> list[str]:
    raw = str(text or "").strip()
    if not raw:
        return []
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", raw) if part.strip()]


def cleanup_duplicate_sentences_en(text: str) -> str:
    parts = split_en_sentences(text)
    deduped: list[str] = []
    seen: set[str] = set()
    for part in parts:
        key = re.sub(r"[^a-z0-9]+", " ", part.lower())
        key = re.sub(r"\s+", " ", key).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(part)
    return " ".join(deduped).strip() if deduped else str(text or "").strip()


def humanize_en_text(text: str, *, max_sentences: int | None = None) -> str:
    out = str(text or "").strip()
    if not out:
        return ""
    out = out.replace("\n", " ")
    out = re.sub(r"\s+", " ", out)
    out = cleanup_en_punctuation(out)
    out = cleanup_duplicate_sentences_en(out)
    if max_sentences and max_sentences > 0:
        parts = split_en_sentences(out)
        if len(parts) > max_sentences:
            out = " ".join(parts[:max_sentences]).strip()
    if out and out[-1] not in ".!?":
        out += "."
    return out


_PROFILE_FIELD_MAX_SENTENCES = {
    "headline": 1,
    "teaser": 2,
    "body": 4,
    "micro": 1,
    "astro_hint": 1,
}


def _naturalize_profile_en_text(text: str, *, field: str) -> str:
    value = " ".join(str(text or "").split()).strip()
    if not value:
        return ""
    if field == "headline":
        return cleanup_en_punctuation(value).strip(" .")
    return humanize_en_text(
        value,
        max_sentences=_PROFILE_FIELD_MAX_SENTENCES.get(field),
    )


def clean_public_block_en(block: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(block)
    for field in ("headline", "teaser", "body", "micro", "astro_hint"):
        raw = out.get(field)
        if isinstance(raw, str):
            out[field] = _naturalize_profile_en_text(raw, field=field)

    chips = out.get("chips")
    if isinstance(chips, list):
        normalized: list[str] = []
        seen: set[str] = set()
        for chip in chips:
            value = cleanup_en_punctuation(str(chip or "")).strip(" .")
            if not value:
                continue
            key = value.lower()
            if key in seen:
                continue
            seen.add(key)
            normalized.append(value)
            if len(normalized) >= 3:
                break
        out["chips"] = normalized
    return out
