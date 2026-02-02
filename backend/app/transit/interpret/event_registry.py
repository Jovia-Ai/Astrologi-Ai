from __future__ import annotations

from typing import Dict, Iterable

from .event_models import EventMeta
from .label_builder import build_label


def build_event_registry(raw_event_metas: Iterable[EventMeta]) -> Dict[str, EventMeta]:
    reg: Dict[str, EventMeta] = {}
    for meta in raw_event_metas:
        reg[meta.id] = build_label(meta)
    return reg
