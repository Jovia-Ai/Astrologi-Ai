from __future__ import annotations

from typing import Any

from .event_models import EventMeta
from .label_builder import ASPECT_TONE, _theme_for_obj
from .normalize import norm_aspect


def label_for_theme(meta: EventMeta | Any) -> str:
    if not hasattr(meta, "a") or not hasattr(meta, "b"):
        return getattr(meta, "label", None) or getattr(meta, "event_id", None) or str(meta)

    a_mean = _theme_for_obj(meta.a)
    b_mean = _theme_for_obj(meta.b)
    aspect = norm_aspect(meta.aspect)
    tone = ASPECT_TONE.get(aspect)

    base = f"{a_mean} ↔ {b_mean}"
    return (base + (f" {tone}" if tone else "")).strip()
