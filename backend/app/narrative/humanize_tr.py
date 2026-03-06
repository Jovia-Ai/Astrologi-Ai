from __future__ import annotations

import re
from typing import Any, Mapping

_TECH_REPLACEMENTS = (
    (r"\borb\b", "etki payı"),
    (r"\bapplying\b", "yaklaşan"),
    (r"\bseparating\b", "geri çekilen"),
    (r"\bconjunction\b", "kavuşum"),
    (r"\bopposition\b", "karşıtlık"),
    (r"\bsquare\b", "zorlayan açı"),
    (r"\btrine\b", "uyumlu etki"),
    (r"\bsextile\b", "destekleyici etki"),
    (r"\bphase\b", "evre"),
    (r"\btransit\b", "geçiş etkisi"),
    (r"\bnatal\b", "doğum haritası"),
    (r"\bmarker\b", "işaret"),
    (r"\bscore\b", "etkinin gücü"),
    (r"\bexactish\b", "en yoğun noktaya yakın"),
)

_TONE_SOFTENERS = (
    (r"\bkesinlikle\b", "çoğu durumda"),
    (r"\bkesin\b", "daha net"),
    (r"\bmutlaka\b", "mümkünse"),
    (r"\bkritik\b", "önemli"),
)


def humanize_tr_text(text: str, *, max_sentences: int | None = None) -> str:
    out = str(text or "").strip()
    if not out:
        return ""

    paragraph_token = " __PARA_BREAK__ "
    out = out.replace("\n\n", paragraph_token)
    out = out.replace("\n", " ")
    out = re.sub(r"\s+", " ", out)
    for pattern, replacement in _TECH_REPLACEMENTS:
        out = re.sub(pattern, replacement, out, flags=re.IGNORECASE)
    for pattern, replacement in _TONE_SOFTENERS:
        out = re.sub(pattern, replacement, out, flags=re.IGNORECASE)
    out = re.sub(r"\b(Genel iklim|Dönemin havası):\s*\1:\s*", r"\1: ", out, flags=re.IGNORECASE)

    # Reduce dry parenthetical metadata in user-facing copy.
    out = re.sub(r"\((?:\s*[a-z_]+:\s*[^()]+)\)", "", out, flags=re.IGNORECASE)
    out = re.sub(r"\s+([,.;:!?])", r"\1", out)
    out = re.sub(r"\s+", " ", out).strip()

    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", out) if p.strip()]
    deduped: list[str] = []
    seen: set[str] = set()
    for part in parts:
        key = re.sub(r"[^a-z0-9çğıöşü]+", " ", part.lower())
        key = re.sub(r"\s+", " ", key).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(part)
    if deduped:
        out = " ".join(deduped).strip()

    if max_sentences and max_sentences > 0:
        limited = [p.strip() for p in re.split(r"(?<=[.!?])\s+", out) if p.strip()]
        if len(limited) > max_sentences:
            out = " ".join(limited[:max_sentences]).strip()

    if out and out[-1] not in ".!?":
        out += "."
    out = out.replace(paragraph_token, "\n\n").strip()
    return out


def humanize_compact_item(item: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(item)
    for field in ("title", "summary", "text", "condition", "how_to_use", "message"):
        value = out.get(field)
        if isinstance(value, str) and value.strip():
            out[field] = humanize_tr_text(value)
    return out
