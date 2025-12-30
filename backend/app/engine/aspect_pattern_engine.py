"""Detect classic aspect patterns like t-square and grand trine."""
from __future__ import annotations

from itertools import combinations
from typing import Any, Dict, Iterable, Mapping, Sequence

from app.helpers.meta_detectors import normalize_node_alias, normalize_planet_key


class AspectPatternEngine:
    """Deterministic detector for classic aspect patterns."""

    MAJOR_ASPECTS = {"conjunction", "opposition", "square", "trine", "sextile"}

    def __init__(self, orb_threshold: float = 3.0) -> None:
        self.orb_threshold = float(orb_threshold)

    def compute(
        self,
        *,
        aspects: Sequence[Mapping[str, Any]],
        planets: Mapping[str, Any],
        meta_info: Mapping[str, Any] | None = None,
    ) -> Dict[str, Any]:
        aspect_index = self._build_aspect_index(aspects, planets)
        self._add_quincunx_aspects(aspect_index, planets)

        patterns: list[dict[str, Any]] = []
        patterns.extend(self._detect_t_square(aspect_index))
        patterns.extend(self._detect_grand_trine(aspect_index))
        patterns.extend(self._detect_yod(aspect_index))
        patterns.extend(self._detect_kite(aspect_index))
        return {"aspect_patterns": patterns}

    @staticmethod
    def _normalize_planet(value: object | None) -> str:
        return normalize_node_alias(normalize_planet_key(value))

    def _normalize_aspect(self, value: object | None) -> str:
        if not value:
            return ""
        normalized = str(value).strip().lower()
        if normalized in {"conj", "conjunction"}:
            return "conjunction"
        if normalized in {"opp", "opposition"}:
            return "opposition"
        if normalized in {"square", "sqr"}:
            return "square"
        if normalized in {"trine", "tri"}:
            return "trine"
        if normalized in {"sextile", "sex"}:
            return "sextile"
        if normalized in {"quincunx", "inconjunct", "inconjunction"}:
            return "quincunx"
        return normalized

    def _build_aspect_index(
        self,
        aspects: Sequence[Mapping[str, Any]],
        planets: Mapping[str, Any],
    ) -> Dict[tuple[tuple[str, str], str], float]:
        aspect_index: Dict[tuple[tuple[str, str], str], float] = {}
        planet_set = set(self._extract_planet_degrees(planets))
        for aspect in aspects:
            planet1 = self._normalize_planet(aspect.get("planet1"))
            planet2 = self._normalize_planet(aspect.get("planet2"))
            aspect_type = self._normalize_aspect(aspect.get("type") or aspect.get("aspect"))
            if not planet1 or not planet2 or not aspect_type:
                continue
            if planet1 not in planet_set or planet2 not in planet_set:
                continue
            if aspect_type not in self.MAJOR_ASPECTS:
                continue
            orb = aspect.get("orb")
            if not isinstance(orb, (int, float)):
                continue
            if orb > self.orb_threshold:
                continue
            pair = tuple(sorted((planet1, planet2)))
            key = (pair, aspect_type)
            existing = aspect_index.get(key)
            if existing is None or orb < existing:
                aspect_index[key] = float(orb)
        return aspect_index

    def _add_quincunx_aspects(
        self,
        aspect_index: Dict[tuple[tuple[str, str], str], float],
        planets: Mapping[str, Any],
    ) -> None:
        planet_degrees = self._extract_planet_degrees(planets)
        planet_items = list(planet_degrees.items())
        for idx, (planet_a, degree_a) in enumerate(planet_items):
            for planet_b, degree_b in planet_items[idx + 1 :]:
                diff = abs(float(degree_a) - float(degree_b)) % 360
                diff = diff if diff <= 180 else 360 - diff
                deviation = abs(diff - 150.0)
                if deviation > self.orb_threshold:
                    continue
                pair = tuple(sorted((planet_a, planet_b)))
                key = (pair, "quincunx")
                existing = aspect_index.get(key)
                if existing is None or deviation < existing:
                    aspect_index[key] = float(deviation)

    def _extract_planet_degrees(self, planets: Mapping[str, Any]) -> Dict[str, float]:
        planet_degrees: Dict[str, float] = {}
        for planet, payload in planets.items():
            normalized = self._normalize_planet(planet)
            if not normalized:
                continue
            degree: float | None = None
            if isinstance(payload, Mapping):
                raw_degree = payload.get("degree")
                if raw_degree is None:
                    raw_degree = payload.get("longitude")
                if isinstance(raw_degree, (int, float)):
                    degree = float(raw_degree)
            elif isinstance(payload, (int, float)):
                degree = float(payload)
            if degree is not None:
                planet_degrees[normalized] = degree % 360
        return planet_degrees

    def _get_orb(
        self,
        aspect_index: Mapping[tuple[tuple[str, str], str], float],
        planet_a: str,
        planet_b: str,
        aspect_type: str,
    ) -> float | None:
        pair = tuple(sorted((planet_a, planet_b)))
        return aspect_index.get((pair, aspect_type))

    def _score(self, orbs: Iterable[float]) -> float:
        values = [orb for orb in orbs if isinstance(orb, (int, float))]
        if not values:
            return 0.0
        avg_orb = sum(values) / len(values)
        score = 1.0 - (avg_orb / self.orb_threshold)
        return round(max(0.0, min(1.0, score)), 2)

    def _detect_t_square(
        self,
        aspect_index: Mapping[tuple[tuple[str, str], str], float],
    ) -> list[dict[str, Any]]:
        planets = sorted({planet for pair, _ in aspect_index for planet in pair})
        seen: set[tuple[str, str, str]] = set()
        patterns: list[dict[str, Any]] = []
        for a, b, c in combinations(planets, 3):
            combos = ((a, b, c), (a, c, b), (b, c, a))
            for planet_x, planet_y, planet_z in combos:
                opp = self._get_orb(aspect_index, planet_x, planet_y, "opposition")
                square_x = self._get_orb(aspect_index, planet_x, planet_z, "square")
                square_y = self._get_orb(aspect_index, planet_y, planet_z, "square")
                if opp is None or square_x is None or square_y is None:
                    continue
                trio = tuple(sorted((planet_x, planet_y, planet_z)))
                if trio in seen:
                    continue
                seen.add(trio)
                patterns.append(
                    {
                        "pattern": "t_square",
                        "planets": list(trio),
                        "score": self._score([opp, square_x, square_y]),
                    }
                )
        return patterns

    def _detect_grand_trine(
        self,
        aspect_index: Mapping[tuple[tuple[str, str], str], float],
    ) -> list[dict[str, Any]]:
        planets = sorted({planet for pair, _ in aspect_index for planet in pair})
        patterns: list[dict[str, Any]] = []
        for a, b, c in combinations(planets, 3):
            orb_ab = self._get_orb(aspect_index, a, b, "trine")
            orb_ac = self._get_orb(aspect_index, a, c, "trine")
            orb_bc = self._get_orb(aspect_index, b, c, "trine")
            if orb_ab is None or orb_ac is None or orb_bc is None:
                continue
            patterns.append(
                {
                    "pattern": "grand_trine",
                    "planets": [a, b, c],
                    "score": self._score([orb_ab, orb_ac, orb_bc]),
                }
            )
        return patterns

    def _detect_yod(
        self,
        aspect_index: Mapping[tuple[tuple[str, str], str], float],
    ) -> list[dict[str, Any]]:
        planets = sorted({planet for pair, _ in aspect_index for planet in pair})
        patterns: list[dict[str, Any]] = []
        seen: set[tuple[str, str, str]] = set()
        for a, b, c in combinations(planets, 3):
            for apex in (a, b, c):
                base = [planet for planet in (a, b, c) if planet != apex]
                sextile = self._get_orb(aspect_index, base[0], base[1], "sextile")
                quincunx_a = self._get_orb(aspect_index, base[0], apex, "quincunx")
                quincunx_b = self._get_orb(aspect_index, base[1], apex, "quincunx")
                if sextile is None or quincunx_a is None or quincunx_b is None:
                    continue
                trio = tuple(sorted((a, b, c)))
                if trio in seen:
                    continue
                seen.add(trio)
                patterns.append(
                    {
                        "pattern": "yod",
                        "planets": list(trio),
                        "score": self._score([sextile, quincunx_a, quincunx_b]),
                    }
                )
        return patterns

    def _detect_kite(
        self,
        aspect_index: Mapping[tuple[tuple[str, str], str], float],
    ) -> list[dict[str, Any]]:
        trines = self._detect_grand_trine(aspect_index)
        if not trines:
            return []
        planets = sorted({planet for pair, _ in aspect_index for planet in pair})
        seen: set[tuple[str, str, str, str]] = set()
        patterns: list[dict[str, Any]] = []
        for trine in trines:
            triad = trine["planets"]
            for candidate in planets:
                if candidate in triad:
                    continue
                for anchor in triad:
                    opposition = self._get_orb(aspect_index, candidate, anchor, "opposition")
                    if opposition is None:
                        continue
                    quartet = tuple(sorted((*triad, candidate)))
                    if quartet in seen:
                        continue
                    seen.add(quartet)
                    trine_orbs = []
                    for pair in combinations(triad, 2):
                        orb = self._get_orb(aspect_index, pair[0], pair[1], "trine")
                        if orb is not None:
                            trine_orbs.append(orb)
                    score = self._score(trine_orbs + [opposition])
                    patterns.append(
                        {
                            "pattern": "kite",
                            "planets": list(quartet),
                            "score": score,
                        }
                    )
        return patterns
