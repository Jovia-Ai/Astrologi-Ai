"""Deterministic templating helpers."""
from __future__ import annotations

import hashlib


def pick_variant(event_id: str, lang: str, version: str, n: int) -> int:
    if n <= 0:
        return 1
    payload = f"{event_id}|{lang}|{version}".encode("utf-8")
    digest = hashlib.sha1(payload).hexdigest()
    return (int(digest[:8], 16) % n) + 1


def time_status_from_orb_phase(orb: float, phase: str | None) -> str:
    if orb <= 0.30:
        return "en yoğun"
    if phase == "applying":
        return "yaklaşıyor"
    return "çözülüyor"
