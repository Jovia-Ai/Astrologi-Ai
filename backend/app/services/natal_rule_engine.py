import json
from pathlib import Path
from typing import List, Dict, Any


class NatalRuleEngine:
    """
    Reads natal_rules.json and evaluates identity, psychology, karma categories.
    Returns structured interpretation output.
    """

    def __init__(self):
        rules_path = Path(__file__).parent.parent / "data" / "natal_rules.json"
        with open(rules_path, "r", encoding="utf-8") as f:
            self.rules = json.load(f)

    def interpret(self, planets: List[Dict[str, Any]], aspects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        planets: [{planet: "Sun", sign: "Capricorn", house: 1, degree: 12.0}, ...]
        aspects: [{planet1: "Sun", planet2: "Mars", type: "square"}]
        """
        planet_map = {p["planet"]: p for p in planets}

        # Build quick lookup tables
        signs = {p["planet"]: p["sign"] for p in planets if p.get("sign") is not None}
        houses = {p["planet"]: p.get("house") for p in planets}

        aspect_set = set()
        for asp in aspects:
            p1 = asp.get("planet1")
            p2 = asp.get("planet2")
            aspect_type = asp.get("type") or asp.get("aspect")
            if not (p1 and p2 and aspect_type):
                continue
            key = f"{p1}.{aspect_type}.{p2}".lower()
            aspect_set.add(key)
            key_rev = f"{p2}.{aspect_type}.{p1}".lower()
            aspect_set.add(key_rev)

        def check_condition(condition: str) -> bool:
            """
            Supported:
            Sun.sign = Capricorn
            Venus.house = 5
            Moon.square.Saturn
            Mercury.retrograde = true
            """
            cond = condition.replace(" ", "")

            if ".sign=" in cond:
                planet, rest = cond.split(".sign=")
                value = rest
                return signs.get(planet) == value

            if ".house=" in cond:
                planet, rest = cond.split(".house=")
                try:
                    return str(houses.get(planet)) == rest
                except Exception:
                    return False

            if ".retrograde=" in cond:
                planet, rest = cond.split(".retrograde=")
                want = rest.lower() == "true"
                actual = planet_map.get(planet, {}).get("retrograde")
                return bool(actual) == want

            if any(aspect in cond for aspect in (".square.", ".trine.", ".opposition.", ".sextile.", ".conjunction.")):
                return cond.lower() in aspect_set

            return False

        output: Dict[str, List[str]] = {}

        for category, block in self.rules.items():
            collected: List[str] = []
            for rule in block.get("rules", []):
                conditions = rule.get("if", [])
                if conditions and all(check_condition(c) for c in conditions):
                    collected.append(rule.get("then", ""))
            output[category] = collected

        return output
