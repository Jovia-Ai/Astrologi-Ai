from __future__ import annotations

from typing import Any, Dict, List

from .event_models import EventMeta


def build_label_pack_top(top_event_ids: List[str], registry: Dict[str, EventMeta]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for eid in top_event_ids:
        meta = registry.get(eid)
        if not meta or not meta.label:
            continue
        out.append(
            {
                "short": meta.label.short,
                "where": meta.label.where,
                "short_plus": meta.label.short_plus,
                "full": {
                    "mechanism": meta.label.full.mechanism if meta.label.full else None,
                    "advice": meta.label.full.advice if meta.label.full else None,
                },
            }
        )
    return out


def split_phase_vs_transit(event_ids: List[str]) -> Dict[str, List[str]]:
    phase = [eid for eid in event_ids if eid.startswith("phase.")]
    tr = [eid for eid in event_ids if eid.startswith("tr.")]
    return {"phase": phase, "transit": tr}
