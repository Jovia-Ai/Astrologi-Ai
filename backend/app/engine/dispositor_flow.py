from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Mapping, Sequence

from app.helpers.placement_utils import extract_planet_signs


class DispositorFlowEngine:
    """Mechanical detector for dispositor chains and governance rhythm."""

    SIGN_RULERS: Mapping[str, List[str]] = {
        "aries": ["mars"],
        "taurus": ["venus"],
        "gemini": ["mercury"],
        "cancer": ["moon"],
        "leo": ["sun"],
        "virgo": ["mercury"],
        "libra": ["venus"],
        "scorpio": ["pluto", "mars"],
        "sagittarius": ["jupiter"],
        "capricorn": ["saturn"],
        "aquarius": ["uranus", "saturn"],
        "pisces": ["neptune", "jupiter"],
    }

    def build(self, placements: Sequence[str]) -> Dict[str, Any]:
        planet_signs = extract_planet_signs(placements)
        if not planet_signs:
            return {
                "final_dispositor": None,
                "dispositor_structure": None,
                "governance_weight": None,
                "mutual_receptions": [],
                "chains": [],
            }

        chains = []
        for planet in planet_signs:
            chain, final, looped = self._trace_chain(planet, planet_signs)
            chains.append({"chain": chain, "final": final, "loop": looped})

        finals = [entry["final"] for entry in chains if entry["final"]]
        final_dispositor = (
            Counter(finals).most_common(1)[0][0] if finals else None
        )

        has_loop = any(entry["loop"] for entry in chains)
        unique_finals = {entry["final"] for entry in chains if entry["final"]}
        structure = self._determine_structure(has_loop, unique_finals, chains)
        governance = (
            "centralized"
            if structure == "chain" and len(unique_finals) <= 1
            else "distributed"
        )
        mutual = self._detect_mutual_receptions(planet_signs)

        return {
            "final_dispositor": final_dispositor,
            "dispositor_structure": structure,
            "governance_weight": governance,
            "mutual_receptions": mutual,
            "chains": [entry["chain"] for entry in chains],
        }

    @staticmethod
    def _determine_structure(
        has_loop: bool,
        unique_finals: set,
        chains: List[Dict[str, Any]],
    ) -> str:
        if has_loop:
            return "loop"
        if len(unique_finals) > 1 or len(chains) > 1:
            return "fragmented"
        return "chain"

    @classmethod
    def _trace_chain(
        cls,
        start: str,
        planet_signs: Mapping[str, str],
    ) -> tuple[List[str], str | None, bool]:
        visited = [start]
        current = start
        while True:
            next_planet = cls._next_planet(current, planet_signs)
            if not next_planet:
                return visited, current, False
            if next_planet == current:
                return visited, current, False
            if next_planet in visited:
                return visited + [next_planet], next_planet, True
            visited.append(next_planet)
            current = next_planet

    @classmethod
    def _next_planet(
        cls,
        planet: str,
        planet_signs: Mapping[str, str],
    ) -> str | None:
        sign = planet_signs.get(planet)
        if not sign:
            return None
        rulers = cls.SIGN_RULERS.get(sign, [])
        for ruler in rulers:
            if ruler == planet:
                return planet
            if ruler in planet_signs:
                return ruler
        return None

    @classmethod
    def _detect_mutual_receptions(
        cls,
        planet_signs: Mapping[str, str],
    ) -> List[tuple[str, str]]:
        pairs: set[tuple[str, str]] = set()
        for planet, sign in planet_signs.items():
            ruler = cls._primary_ruler(sign)
            if not ruler or ruler not in planet_signs:
                continue
            counterpart_sign = planet_signs.get(ruler)
            if not counterpart_sign:
                continue
            if cls._primary_ruler(counterpart_sign) == planet:
                pair = tuple(sorted([planet, ruler]))
                pairs.add(pair)
        return sorted(pairs)

    @classmethod
    def _primary_ruler(cls, sign: str) -> str | None:
        rulers = cls.SIGN_RULERS.get(sign, [])
        return rulers[0] if rulers else None
