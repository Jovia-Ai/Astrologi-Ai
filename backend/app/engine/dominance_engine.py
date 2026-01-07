from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence

from app.helpers.meta_detectors import normalize_node_alias, normalize_planet_key


class DominanceEngine:
    """Compute dominant planets based on deterministic rules."""

    def __init__(self, rules_root: str | None = None) -> None:
        root = (
            Path(rules_root)
            if rules_root
            else Path(__file__).resolve().parents[1] / "data" / "astro_rules" / "meta"
        )
        self.rules = self._load_rules(root)

    def _load_rules(self, root: Path) -> Dict[str, Any]:
        path = root / "dominance_rules.json"
        if not path.exists():
            return {}
        try:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (json.JSONDecodeError, OSError):
            return {}
        return payload if isinstance(payload, Mapping) else {}

    def compute(
        self,
        *,
        planets: Mapping[str, Any] | Sequence[Mapping[str, Any]],
        houses: Mapping[str, Any] | None,
        aspects: Sequence[Mapping[str, Any]] | None,
        meta_info: Mapping[str, Any] | None,
    ) -> Dict[str, Any]:
        if not self.rules:
            return {"dominant_planets": []}

        weights = self.rules.get("weights") or {}
        thresholds = self.rules.get("thresholds") or {}
        dignities = self.rules.get("dignities") or {}

        angular_bonus = float(weights.get("angular_house_bonus") or 0.0)
        dignity_bonus = float(weights.get("dignity_bonus") or 0.0)
        rulership_bonus = float(weights.get("rulership_bonus") or 0.0)
        stellium_bonus = float(weights.get("stellium_house_bonus") or 0.0)
        tight_orb_bonus = float(weights.get("aspect_tight_orb_bonus") or 0.0)

        dominant_min = float(thresholds.get("dominant_min_score") or 0.0)
        max_planets = int(thresholds.get("max_planets") or 0)

        normalized_planets = self._normalize_planets(planets)
        aspect_entries = aspects or []
        meta = meta_info or {}
        chart_ruler = self._normalize_planet(meta.get("chart_ruler"))
        house_clusters = meta.get("house_clusters") or {}

        results: list[Dict[str, Any]] = []
        for planet, payload in normalized_planets.items():
            score = 0.0
            reasons: list[str] = []
            house = payload.get("house")
            sign = payload.get("sign")

            if house in {1, 4, 7, 10}:
                score += angular_bonus
                reasons.append("angular_house")

            dignity_list = dignities.get(planet, [])
            if isinstance(sign, str) and sign in dignity_list:
                score += dignity_bonus
                reasons.append("dignity")

            if chart_ruler and planet == chart_ruler:
                score += rulership_bonus
                reasons.append("rulership")

            if house is not None:
                try:
                    house_value = int(house)
                except (TypeError, ValueError):
                    house_value = None
                if house_value is not None and house_clusters.get(house_value, 0) >= 3:
                    score += stellium_bonus
                    reasons.append("stellium_house")

            tight_count = self._count_tight_aspects(planet, aspect_entries)
            if tight_count:
                score += tight_count * tight_orb_bonus
                reasons.append("aspect_tight_orb")

            if score >= dominant_min:
                results.append(
                    {
                        "planet": planet,
                        "score": round(score, 3),
                        "reasons": reasons,
                    }
                )

        results.sort(key=lambda item: (-item["score"], item["planet"]))
        if max_planets > 0:
            results = results[:max_planets]

        return {"dominant_planets": results}

    @staticmethod
    def _normalize_planets(
        planets: Mapping[str, Any] | Sequence[Mapping[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        normalized: Dict[str, Dict[str, Any]] = {}
        if isinstance(planets, Mapping):
            items = planets.items()
            for name, payload in items:
                planet = DominanceEngine._normalize_planet(name)
                if not planet or not isinstance(payload, Mapping):
                    continue
                normalized[planet] = {
                    "sign": DominanceEngine._normalize_sign(payload.get("sign")),
                    "house": payload.get("house"),
                }
            return normalized

        if isinstance(planets, Sequence):
            for entry in planets:
                if not isinstance(entry, Mapping):
                    continue
                if entry.get("is_point"):
                    continue
                planet = DominanceEngine._normalize_planet(entry.get("planet"))
                if not planet:
                    continue
                if planet in {"ascendant", "descendant", "midheaven", "mc", "imum_coeli", "ic"}:
                    continue
                normalized[planet] = {
                    "sign": DominanceEngine._normalize_sign(entry.get("sign")),
                    "house": entry.get("house"),
                }
        return normalized

    @staticmethod
    def _normalize_planet(value: object | None) -> str:
        return normalize_node_alias(normalize_planet_key(value))

    @staticmethod
    def _normalize_sign(value: object | None) -> str | None:
        if not isinstance(value, str):
            return None
        return value.strip().lower()

    @staticmethod
    def _count_tight_aspects(
        planet: str,
        aspects: Iterable[Mapping[str, Any]],
        *,
        max_orb: float = 2.0,
    ) -> int:
        count = 0
        for aspect in aspects:
            planet1 = DominanceEngine._normalize_planet(aspect.get("planet1") or aspect.get("planet"))
            planet2 = DominanceEngine._normalize_planet(aspect.get("planet2") or aspect.get("target"))
            if planet not in {planet1, planet2}:
                continue
            orb = aspect.get("orb")
            if not isinstance(orb, (int, float)):
                continue
            if float(orb) <= max_orb:
                count += 1
        return count
