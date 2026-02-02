from __future__ import annotations


def moon_phase_score(phase: str) -> float:
    if phase == "waning":
        return 0.6
    if phase == "new":
        return 0.3
    if phase == "waxing":
        return -0.2
    if phase == "full":
        return -0.4
    return 0.0
