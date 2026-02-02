from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .event_models import EventMeta


@dataclass
class CooldownState:
    last_top_day: Dict[str, str] = field(default_factory=dict)
    streak: Dict[str, int] = field(default_factory=dict)


def _is_consecutive(prev_day: str, day: str) -> bool:
    from datetime import date

    y1, m1, d1 = map(int, prev_day.split("-"))
    y2, m2, d2 = map(int, day.split("-"))
    return (date(y2, m2, d2) - date(y1, m1, d1)).days == 1


def pick_top_with_cooldown(
    day: str,
    candidates: List[Tuple[str, float]],
    registry: Dict[str, EventMeta],
    state: CooldownState,
    top_k: int = 5,
    max_nonpeak_streak: int = 2,
) -> List[str]:
    candidates = sorted(candidates, key=lambda x: x[1], reverse=True)

    chosen: List[str] = []
    for event_id, _score in candidates:
        if event_id not in registry:
            continue
        meta = registry[event_id]
        if meta.timing.is_peak:
            chosen.append(event_id)
        else:
            prev_day = state.last_top_day.get(event_id)
            prev_streak = state.streak.get(event_id, 0)

            if prev_day and _is_consecutive(prev_day, day):
                if prev_streak >= max_nonpeak_streak:
                    continue
            chosen.append(event_id)

        if len(chosen) >= top_k:
            break

    for event_id in chosen:
        prev_day = state.last_top_day.get(event_id)
        if prev_day and _is_consecutive(prev_day, day):
            state.streak[event_id] = state.streak.get(event_id, 0) + 1
        else:
            state.streak[event_id] = 1
        state.last_top_day[event_id] = day

    if len(state.last_top_day) > 2000:
        items = list(state.last_top_day.items())[-500:]
        state.last_top_day = dict(items)
        keep = set(state.last_top_day.keys())
        state.streak = {k: v for k, v in state.streak.items() if k in keep}

    return chosen
