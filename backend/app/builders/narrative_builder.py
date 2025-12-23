from __future__ import annotations

import re

from typing import Any, Dict, List, Mapping

from app.builders.semantic_normalizer import contains_verb_phrase


SLOT_NAMES: tuple[str, ...] = ("cause", "mechanism", "effect", "shadow", "potential")

CATEGORY_LABELS: Dict[str, str] = {
    "identity": "Kimlik",
    "psychology": "Psikoloji",
    "relationships": "İlişkiler",
    "mind": "Zihin",
    "career": "Kariyer",
    "karma": "Karma",
}

TENSION_DESCRIPTIONS: Dict[str, str] = {
    "visibility_vs_control": "görünürlük ile kontrol arasında titreyen",
    "trait_reinforcement": "özelliklerin güçlenmesine odaklanan",
    "balanced_flow": "dengeyi gözeten",
}

DOMAIN_TEMPLATES: Dict[str, Dict[str, str]] = {
    "identity": {
        "opening": "Kimliğin, {core_tension} etrafında şekillenen bir yapı gösterir.",
        "effect": "Bu durum seni dış dünyada {effect_expression} biri olarak algılanır hale getirir.",
        "shadow": "Denge bozulduğunda ise {shadow_risk} eğilimi ortaya çıkabilir.",
        "potential": "Ancak bu düzen, doğru regülasyonla {potential_gain} kapasitesine dönüşebilir.",
    },
    "psychology": {
        "opening": "Psikolojik alanın, {core_tension} çevresinde bir iç denge haritası çıkarıyor.",
        "effect": "Bu durum, çevrendekilerin seni {effect_expression} biri olarak gözlemlemesine yol açıyor.",
        "shadow": "Kontrol kaybı anı {shadow_risk} eğilimini gün yüzüne çıkarabiliyor.",
        "potential": "Yine de bu bütünleşme, sınırlarını bilinçle belirlediğinde {potential_gain} bir güç sunuyor.",
    },
}

FORBIDDEN_TOKENS = (
    "aktif eksen",
    "açı profili",
    "aktivasyon",
    "hassasiyet",
    "tempo",
    "friction",
    "flow",
)

PROHIBITED_ASTRO_TERMS = re.compile(
    r"\\b(aries|taurus|gemini|cancer|leo|virgo|libra|scorpio|sagittarius|capricorn|aquarius|pisces|house|square|trine|opposition|sextile|conjunction)\\b",
    re.IGNORECASE,
)


class JoviaSemanticNarrativeBuilder:
    """Composite-driven builder that respects the canonical narrative arc."""

    def __init__(self, engine_result: Any) -> None:
        self.meta_info: Mapping[str, Any] = getattr(engine_result, "meta_info", {}) or {}
        self.composites: List[Mapping[str, Any]] = getattr(engine_result, "composites", []) or []
        self.patterns: Dict[str, Any] = getattr(engine_result, "patterns", {}) or {}
        self.upper_meanings: List[Dict[str, Any]] = getattr(engine_result, "upper_meanings", []) or []
        self.dispositor_flow: Mapping[str, Any] = getattr(engine_result, "dispositor_flow", {}) or {}
        self.axis_activation: Mapping[str, Any] = getattr(engine_result, "axis_activation", {}) or {}
        self.fragments: Mapping[str, Dict[str, Any]] = getattr(engine_result, "fragments", {}) or {}
        self.guidance: Mapping[str, Any] = getattr(engine_result, "guidance", {}) or {}
        self.active_domains: set[str] = set(
            str(domain).lower() for domain in self.guidance.get("active_domains", [])
        )
        self.regulations: Mapping[str, Dict[str, Any]] = getattr(engine_result, "regulations", {}) or {}
        self.expression_profile: Mapping[str, Any] = getattr(engine_result, "expression_profile", {}) or {}
        self._allowed_templates: set[str] = {
            str(template).lower() for template in self.expression_profile.get("allowed_templates", []) or []
        }
        self._fallback_mode = str(self.expression_profile.get("fallback_mode") or "regulator_neutral").lower()
        self._softening_level = float(self.expression_profile.get("softening_level") or 0.5)

        self.used_composite_ids: List[str] = []
        self.upper_triggered: List[str] = []
        self.upper_map = {
            entry["composite_id"]: entry for entry in self.upper_meanings if entry.get("composite_id")
        }
        self._fallback_used = False

    def build(self) -> Dict[str, str]:
        result: Dict[str, str] = {}
        for category in CATEGORY_LABELS:
            text = self._build_category_text(category)
            if text:
                result[category] = text
        if "identity" not in result and self._identity_slots_present():
            fallback = self._soft_fail_sentence("identity")
            if fallback:
                result["identity"] = fallback
        return result

    @property
    def fallback_used(self) -> bool:
        return self._fallback_used

    def _build_category_text(self, category: str) -> str:
        if self.guidance and category not in self.active_domains:
            return ""
        if self._fallback_mode == "silent":
            return ""
        if self._allowed_templates and category not in self._allowed_templates:
            return ""
        domain_data = self.fragments.get(category, {})
        if not isinstance(domain_data, Mapping):
            return self._apply_expression_profile(self._soft_fail_sentence(category))
        slots = domain_data.get("slots")
        if not isinstance(slots, Mapping):
            slots = {}
        anchor = domain_data.get("anchor")
        if not slots:
            return self._apply_expression_profile(self._soft_fail_sentence(category))
        regulation = self.regulations.get(category)
        paragraph = self._build_locked_paragraph(category, slots, regulation)
        self._mark_composites(category)
        if paragraph:
            return self._apply_expression_profile(paragraph)
        return self._apply_expression_profile(self._soft_fail_sentence(category))

    def _build_locked_paragraph(
        self,
        domain: str,
        slots: Mapping[str, Dict[str, Any]],
        regulation: Mapping[str, Any] | None,
    ) -> str | None:
        template = DOMAIN_TEMPLATES.get(domain)
        if not template:
            return None
        sentences: List[str] = []
        core_tension = self._core_tension_phrase(regulation)
        sentences.append(template["opening"].format(core_tension=core_tension))
        effect_text = self._slot_fragment_text(slots.get("effect"))
        if effect_text:
            sentences.append(template["effect"].format(effect_expression=effect_text))
        axis_tension = (self.axis_activation or {}).get("axis_tension")
        include_shadow = axis_tension in {"high", "medium"}
        shadow_text = self._slot_fragment_text(slots.get("shadow"))
        if include_shadow and shadow_text:
            sentences.append(template["shadow"].format(shadow_risk=shadow_text))
        potential_text = self._slot_fragment_text(slots.get("potential"))
        if potential_text:
            sentences.append(template["potential"].format(potential_gain=potential_text))
        return " ".join(sentences)

    def _slot_fragment_text(self, fragment: Mapping[str, Any] | None) -> str | None:
        if not fragment or not isinstance(fragment, Mapping):
            return None
        text = fragment.get("text")
        normalized = self._normalize(self._sanitize(text))
        if not normalized:
            return None
        if contains_verb_phrase(normalized) or self._contains_forbidden_language(normalized):
            return None
        return normalized

    def _core_tension_phrase(self, regulation: Mapping[str, Any] | None) -> str:
        tension_type = str((regulation or {}).get("tension_type") or "balanced_flow")
        return TENSION_DESCRIPTIONS.get(tension_type, "dengeyi gözeten gerilim")

    def _mark_composites(self, category: str) -> None:
        for composite in self.composites:
            if composite.get("domain") == category:
                comp_id = composite.get("composite_id")
                if comp_id and comp_id not in self.used_composite_ids:
                    self.used_composite_ids.append(comp_id)

    def _soft_fail_sentence(self, domain: str) -> str | None:
        self._mark_fallback()
        regulation = self.regulations.get(domain)
        core_tension = self._core_tension_phrase(regulation)
        template = DOMAIN_TEMPLATES.get(domain)
        if template:
            return self._ensure_sentence(template["opening"].format(core_tension=core_tension))
        label = CATEGORY_LABELS.get(domain, domain.capitalize())
        sentence = f"{label} alanında {core_tension} dinamikleri öne çıkıyor."
        return self._ensure_sentence(sentence)

    def _mark_fallback(self) -> None:
        self._fallback_used = True

    def _identity_slots_present(self) -> bool:
        identity_entry = self.fragments.get("identity")
        if not isinstance(identity_entry, Mapping):
            return False
        slots = identity_entry.get("slots")
        if not isinstance(slots, Mapping):
            return False
        return any(isinstance(value, Mapping) for value in slots.values() if value)

    def _composite_priority(self, composite: Mapping[str, Any]) -> float:
        comp_id = composite.get("composite_id")
        meta = self.patterns.get(comp_id or "", {})
        try:
            return float(meta.get("priority_score") or 0.0)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _ensure_sentence(text: str) -> str:
        stripped = text.strip()
        if not stripped:
            return ""
        if stripped[-1] not in ".!?":
            stripped += "."
        return stripped[0].upper() + stripped[1:]

    @staticmethod
    def _normalize(text: Any) -> str:
        if not text:
            return ""
        return " ".join(str(text).strip().split())

    def _contains_forbidden_language(self, text: str) -> bool:
        lowered = text.lower()
        if any(token in lowered for token in FORBIDDEN_TOKENS):
            return True
        profile_terms = self.expression_profile.get("forbidden_phrases") or []
        return any(str(term).lower() in lowered for term in profile_terms)

    def _apply_expression_profile(self, text: str) -> str:
        normalized = self._normalize(text)
        if not normalized:
            return ""
        length_map = {"short": 90, "medium": 150, "long": 220}
        limit = length_map.get(self.expression_profile.get("sentence_length"), 160)
        trimmed = self._trim_text(normalized, limit)
        tone = str(self.expression_profile.get("tone") or "").lower()
        if tone == "firm":
            trimmed = trimmed.replace(" olabilir", " olur")
        if self.expression_profile.get("fallback_mode") == "regulator_neutral" and self._softening_level < 0.4:
            trimmed = trimmed.split(".")[0].strip() + "."
        return trimmed

    def _trim_text(self, text: str, limit: int) -> str:
        if len(text) <= limit:
            return text
        snippet = text[: limit].rstrip()
        if " " in snippet:
            snippet = snippet[: snippet.rfind(" ")]
        return f"{snippet}..."

    @staticmethod
    def _sanitize(text: str | None) -> str:
        if not isinstance(text, str):
            return ""
        if PROHIBITED_ASTRO_TERMS.search(text):
            return ""
        return text
