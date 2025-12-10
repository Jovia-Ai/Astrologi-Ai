from typing import Any, Dict, List, Mapping, Optional, Sequence
import re

SLOTS = ("cause", "mechanism", "effect", "shadow", "potential")


class JoviaSemanticNarrativeBuilder:
    """
    Jovia Narrative Builder v3 (pro)
    --------------------------------
    - Eski template/composer pipeline'ını tamamen devre dışı bırakmak için tek giriş noktası.
    - input: interpretation: Dict[str, List[str]]  (identity/psychology/relationships/mind/career/karma -> cümle listesi)
    - output: Dict[str, str] (her kategori için tek insan gibi paragraf)
    """

    SLOT_ORDER = ["cause", "mechanism", "effect", "shadow", "potential"]

    def __init__(self, engine_result: Any) -> None:
        interp = getattr(engine_result, "interpretation", None)
        if isinstance(interp, Mapping):
            self.interpretation: Dict[str, List[str]] = {
                category: [s for s in (values or []) if isinstance(s, str) and s.strip()]
                for category, values in interp.items()
            }
        else:
            self.interpretation = {}

        self.slot_keywords: Dict[str, Dict[str, float]] = {
            "cause": {
                "temelinde": 3.0,
                "merkezinde": 3.0,
                "kökünde": 3.0,
                "çekirdeğinde": 2.5,
                "ihtiyacı": 1.5,
                "tema": 1.0,
                "üzerine kuruludur": 1.0,
                "bulunur": 0.5,
                "vardır": 0.5,
            },
            "mechanism": {
                "içsel": 2.0,
                "iç dünyanda": 2.5,
                "içsel dünyanda": 2.5,
                "şeklinde": 1.0,
                "çalışır": 1.2,
                "yönlendirir": 1.5,
                "işlersin": 1.0,
                "işler": 1.0,
                "eğilimindesin": 1.5,
                "yatkınsın": 1.5,
            },
            "effect": {
                "dışarıdan": 3.0,
                "dışarıya": 3.0,
                "olarak görünürsün": 2.0,
                "olarak algılanırsın": 2.0,
                "insanlar seni": 2.5,
                "algılar": 1.0,
                "yansır": 1.5,
                "ortaya": 0.5,
            },
            "shadow": {
                "aşırı": 2.0,
                "fazla": 1.5,
                "zorlayabilir": 2.0,
                "kriz": 2.0,
                "yorgunluk": 1.5,
                "tükenmişlik": 2.0,
                "yalnızlık": 1.5,
                "bağımlılık": 1.8,
                "takıntı": 1.8,
                "kontrol": 0.8,
                "kaygı": 1.5,
                "çatışma": 1.5,
                "sorun": 1.2,
                "karmayı": 1.8,
                "gölge": 2.0,
            },
            "potential": {
                "olduğunda": 2.0,
                "geliştir": 1.5,
                "gelişir": 1.5,
                "dönüşür": 2.0,
                "ustalık": 2.0,
                "bilgelik": 2.0,
                "güçlen": 1.5,
                "güçlü": 1.0,
                "özgür": 1.5,
                "şifa": 2.0,
                "potansiyel": 1.5,
                "büyütür": 1.5,
                "açılır": 1.5,
            },
        }

        self.prefixes: List[str] = [
            "Kimliğinin temelinde",
            "Kimliğinin merkezinde",
            "Kimliğinin kökünde",
            "Kimliğinin çekirdeğinde",
            "Kimliğin temelinde",
            "Kimliğin merkezinde",
            "Kimliğin çekirdeğinde",
            "Psikolojik temelinde",
            "Psikolojik yapında",
            "Psikolojik altyapında",
            "Psikolojik olarak",
            "İçsel enerjin",
            "İçsel dünyanda",
            "İç dünyanda",
            "İçsel olarak",
            "Zihnin",
            "Zihinsel olarak",
            "İlişkilerde",
            "Yakın ilişkilerde",
            "Bağlarda",
            "İş hayatında",
            "Kariyerde",
            "Bu yaşamda",
            "Bu yaşamın teması",
            "Ruhsal tema,",
            "Ruhsal yolunda",
            "Bu süreç",
            "Bu enerji",
            "Bu nedenle",
            "Bilinçle yönetildiğinde",
            "Bilinçle yönettiğinde",
            "Kalbinle hizalandığında",
            "Gerçekçilik bilgelikle birleştiğinde",
            "Kimliğini içten kurduğunda",
        ]

    def build(self) -> Dict[str, str]:
        return {
            "identity": self._build_category("identity"),
            "psychology": self._build_category("psychology"),
            "relationships": self._build_category("relationships"),
            "mind": self._build_category("mind"),
            "career": self._build_category("career"),
            "karma": self._build_category("karma"),
        }

    def _build_category(self, key: str) -> str:
        sentences = self.interpretation.get(key, []) or []
        if not sentences:
            return ""

        slots = self._select_slot_fragments(sentences)
        cause = slots.get("cause")
        mechanism = slots.get("mechanism")
        effect = slots.get("effect")
        shadow = slots.get("shadow")
        potential = slots.get("potential")

        parts: List[str] = []
        if cause:
            parts.append(self._ensure_sentence(self._normalize(cause)))

        if mechanism:
            inner = self._normalize(mechanism)
            if not self._starts_with(inner, ["bu enerji", "iç dünyanda", "içsel dünyanda"]):
                inner = "Bu enerji iç dünyanda " + self._decapitalize(inner)
            parts.append(self._ensure_sentence(inner))

        if effect and key == "identity":
            outer = self._normalize(effect)
            if not self._starts_with(
                outer,
                ["dışarıdan", "dışarıya", "insanlar seni", "çevren seni"],
            ):
                outer = "Dışarıya ise " + self._decapitalize(outer)
            parts.append(self._ensure_sentence(outer))

        if shadow:
            shadow_clean = self._normalize(shadow)
            if not self._starts_with(shadow_clean, ["denge", "fakat", "aşırı", "kriz"]):
                shadow_clean = "Denge bozulduğunda " + self._decapitalize(shadow_clean)
            parts.append(self._ensure_sentence(shadow_clean))

        if potential:
            potential_clean = self._normalize(potential)
            if not self._starts_with(
                potential_clean,
                ["bilinçle yönettiğinde", "bilgece kullandığında", "bu farkındalıkla"],
            ):
                potential_clean = (
                    "Bilinçle yönettiğinde " + self._decapitalize(potential_clean)
                )
            parts.append(self._ensure_sentence(potential_clean))

        return " ".join(parts).strip()

    def _select_slot_fragments(self, fragments: List[str]) -> Dict[str, Optional[str]]:
        cleaned = [self._normalize(self._clean_prefix(f)) for f in fragments if f]
        buckets: Dict[str, List[str]] = {slot: [] for slot in self.SLOT_ORDER}

        for frag in cleaned:
            best_slot = None
            best_score = 0.0
            for slot in self.SLOT_ORDER:
                score = self._score_fragment(frag, slot)
                if score > best_score:
                    best_score = score
                    best_slot = slot
            if best_slot:
                buckets[best_slot].append(frag)

        return {
            slot: self._pick_best(buckets.get(slot, []), slot) for slot in self.SLOT_ORDER
        }

    def _score_fragment(self, fragment: str, slot: str) -> float:
        score = 0.01
        fragment_lower = fragment.lower()
        for keyword, weight in self.slot_keywords.get(slot, {}).items():
            if keyword in fragment_lower:
                score += weight
        return score

    def _pick_best(self, fragments: List[str], slot: str) -> Optional[str]:
        if not fragments:
            return None
        ranked = sorted(
            fragments,
            key=lambda text: (
                -self._score_fragment(text, slot),
                len(text),
            ),
        )
        return ranked[0]

    def _clean_prefix(self, text: str) -> str:
        trimmed = text.strip()
        lower = trimmed.lower()
        for pref in self.prefixes:
            if lower.startswith(pref.lower()):
                trimmed = trimmed[len(pref) :].lstrip(" ,:-")
                lower = trimmed.lower()
        return trimmed

    def _normalize(self, text: str) -> str:
        return " ".join(text.strip().split())

    def _ensure_sentence(self, text: str) -> str:
        if not text:
            return ""
        if text[-1] not in ".!?":
            text += "."
        return text[0].upper() + text[1:]

    def _decapitalize(self, text: str) -> str:
        if not text:
            return ""
        return text[0].lower() + text[1:]

    def _starts_with(self, text: str, prefixes: List[str]) -> bool:
        lower = text.strip().lower()
        return any(lower.startswith(prefix.lower()) for prefix in prefixes)


# Backwards compatibility: eski isim hâlâ çalışsın
JoviaLightNarrativeBuilder = JoviaSemanticNarrativeBuilder
