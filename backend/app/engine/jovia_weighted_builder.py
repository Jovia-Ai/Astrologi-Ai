from typing import Any, Dict, List, Optional, Sequence, Mapping


class JoviaWeightedNarrativeBuilder:
    """
    Weighted narrative builder for Jovia.

    - Her kategori (identity, psychology, relationships, mind, career, karma)
      için gezegen öncelikleri ile cümle seçimi yapar.
    - RuleEngine'in ürettiği interpretation dict'inden:
        cause, mechanism, effect, shadow, potential
      cümle setini seçer.
    - Amaç: daha tutarlı, daha astrolojik, daha isabetli metin üretmek.
    """

    CATEGORY_WEIGHTS = {
        "identity": {
            "Sun": 1.00,
            "Ascendant": 0.95,
            "Mars": 0.80,
            "Jupiter": 0.75,
            "Saturn": 0.55,
            "Moon": 0.50,
            "Mercury": 0.45,
            "Pluto": 0.40,
            "Neptune": 0.30,
            "Uranus": 0.30,
            "Venus": 0.25,
            "Lilith": 0.20,
            "North Node": 0.20,
        },

        "psychology": {
            "Moon": 1.00,
            "Mercury": 0.80,
            "Pluto": 0.70,
            "Saturn": 0.60,
            "Neptune": 0.55,
            "Mars": 0.50,
            "Venus": 0.40,
            "Lilith": 0.35,
            "Jupiter": 0.30,
            "Sun": 0.25,
            "Uranus": 0.25,
            "North Node": 0.20,
        },

        "relationships": {
            "Venus": 1.00,
            "Mars": 0.90,
            "Moon": 0.75,
            "Sun": 0.55,
            "Jupiter": 0.50,
            "Saturn": 0.45,
            "Pluto": 0.40,
            "North Node": 0.35,
            "Mercury": 0.30,
            "Uranus": 0.25,
            "Neptune": 0.25,
            "Lilith": 0.20,
        },

        "mind": {
            "Mercury": 1.00,
            "Uranus": 0.80,
            "Jupiter": 0.70,
            "Sun": 0.50,
            "Saturn": 0.45,
            "Neptune": 0.40,
            "Moon": 0.35,
            "Mars": 0.35,
            "Pluto": 0.35,
            "North Node": 0.25,
        },

        "career": {
            "Saturn": 1.00,
            "Jupiter": 0.90,
            "Sun": 0.75,
            "Mars": 0.65,
            "Pluto": 0.50,
            "Moon": 0.35,
            "Mercury": 0.35,
            "North Node": 0.30,
            "Uranus": 0.30,
            "Neptune": 0.25,
            "Venus": 0.20,
        },

        "karma": {
            "North Node": 1.00,
            "Saturn": 0.90,
            "Pluto": 0.80,
            "Neptune": 0.60,
            "Uranus": 0.55,
            "Jupiter": 0.50,
            "Mars": 0.40,
            "Sun": 0.35,
            "Moon": 0.35,
            "Lilith": 0.30,
            "Mercury": 0.25,
        },
    }

    TYPE_ORDER = {
        "cause": 1.0,
        "mechanism": 1.0,
        "effect": 0.9,
        "shadow": 0.8,
        "potential": 0.9,
    }

    def score_sentence(self, sent: Dict, category: str) -> float:
        planet = sent.get("planet", "")
        base_weight = self.CATEGORY_WEIGHTS.get(category, {}).get(planet, 0.1)

        type_weight = self.TYPE_ORDER.get(sent.get("type", ""), 0.5)

        return base_weight * type_weight

    def pick_best(self, sentences: List[Dict], category: str, type_name: str) -> Optional[str]:
        subset = [s for s in sentences if s.get("type") == type_name]
        if not subset:
            return None

        scored = [(s, self.score_sentence(s, category)) for s in subset]
        scored.sort(key=lambda x: x[1], reverse=True)

        return scored[0][0]["text"]

    def build_category_text(self, sentences: List[Dict], category: str) -> Dict[str, str]:
        normalized = [self._ensure_sentence_dict(s) for s in sentences]
        result: Dict[str, str] = {}

        for t in ["cause", "mechanism", "shadow", "potential"]:
            chosen = self.pick_best(normalized, category, t)
            if chosen:
                result[t] = chosen
            else:
                result[t] = ""

        return result

    def build(self, interpretation: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        output = {}
        for category, sents in interpretation.items():
            output[category] = self.build_category_text(self._flatten_sentences(sents), category)
        return output

    def _flatten_sentences(self, data: Any) -> List[Dict]:
        aggregated: List[Dict] = []
        if isinstance(data, Mapping):
            for value in data.values():
                aggregated.extend(self._flatten_sentences(value))
        elif isinstance(data, Sequence) and not isinstance(data, (str, bytes)):
            for item in data:
                aggregated.extend(self._flatten_sentences(item))
        elif isinstance(data, dict):
            aggregated.append(data)
        elif isinstance(data, str):
            aggregated.append({"planet": "", "type": "", "text": data})
        return aggregated

    def _ensure_sentence_dict(self, entry) -> Dict:
        if isinstance(entry, dict):
            return {
                "planet": entry.get("planet", ""),
                "type": entry.get("type", ""),
                "text": entry.get("text") or entry.get("sentence") or "",
            }
        if isinstance(entry, str):
            return {"planet": "", "type": self._infer_type(entry), "text": entry}
        return {"planet": "", "type": "cause", "text": ""}

    def _infer_type(self, text: str) -> str:
        lower = text.lower()
        mapping = {
            "cause": ["temel", "kök", "neden", "ihtiyaç", "kaynak", "başlangıç"],
            "mechanism": ["içsel", "çalışır", "işler", "yönlendirir", "mekanizma", "süreç", "şeklinde"],
            "effect": ["dışarı", "dışarıya", "yansır", "görünür", "algılanır", "davranış"],
            "shadow": ["aşırı", "kriz", "gölge", "zorlan", "tüken", "yıpran", "karamsar"],
            "potential": ["bilinç", "potansiyel", "olgun", "gelişir", "dönüşür", "ustalık", "güçlen"],
        }
        for type_name, keywords in mapping.items():
            if any(kw in lower for kw in keywords):
                return type_name
        return "cause"
