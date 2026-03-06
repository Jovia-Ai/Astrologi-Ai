from __future__ import annotations

import hashlib
from typing import List, Set

from .micro_example_lib_tr import MICRO_EXAMPLES, MicroExample


def _stable_int(seed: str) -> int:
    return int(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:8], 16)


def choose_micro_example(
    seed: str,
    arena_house: int,
    mode: str,
    tone_planets: List[str],
    valence: str,
) -> str:
    """
    Deterministic selection:
      1) filter by arena_house & valence & mode
      2) boost matches on tones
      3) pick deterministically by seed
    """
    tones: Set[str] = set(tone_planets or [])
    mode = (mode or "neutral").lower().strip()
    valence = (valence or "growth").lower().strip()

    candidates: List[MicroExample] = []
    for ex in MICRO_EXAMPLES:
        if ex.valence != valence:
            continue
        if arena_house not in ex.houses:
            continue
        if mode not in {m.lower() for m in ex.modes}:
            continue
        candidates.append(ex)

    if not candidates:
        for ex in MICRO_EXAMPLES:
            if ex.valence == valence and arena_house in ex.houses:
                candidates.append(ex)

    if not candidates:
        return ""

    def score(ex: MicroExample) -> int:
        base = 1 if "*" in ex.tones else 0
        return base + len(tones.intersection(ex.tones))

    candidates.sort(key=score, reverse=True)

    top = candidates[: min(6, len(candidates))]
    idx = _stable_int(seed + f"|{arena_house}|{mode}|{valence}|" + ",".join(sorted(tones))) % len(top)
    return top[idx].template_tr
