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

FORBIDDEN_REPLACEMENTS: Dict[str, str] = {
    "aktif eksen": "odak hattı",
    "açı profili": "açı düzeni",
    "aktivasyon": "hareketlenme",
    "hassasiyet": "duyarlılık",
    "tempo": "ritim",
    "friction": "sürtünme",
    "flow": "akış",
    "pressure": "baskı",
    "pull": "çekim",
    "internal": "içsel",
    "external": "dışsal",
    "dynamic": "dinamik",
    "sun": "güneş",
    "moon": "ay",
    "house": "ev",
    "aspect": "açı",
    "trauma": "sarsıntı",
    "subconscious": "bilinçaltı",
    "attachment": "bağlanma",
}


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
        self.quality_gates_applied: Mapping[str, Any] = getattr(engine_result, "quality_gates", {}) or {}
        self.narrative_plan: Dict[str, Any] = {}
        self.narrative_debug_selected_domains: List[str] = []
        self.narrative_debug_selected_slots: Dict[str, List[str]] = {}
        self.narrative_debug_source_fragment_ids: Dict[str, Dict[str, str]] = {}
        self.narrative_debug_relaxed_domains: List[str] = []
        self.quality_actions_applied: List[Dict[str, Any]] = []
        self._current_plan_entry: Dict[str, Any] | None = None
        self._current_plan_selected_slots: List[str] = []

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
        plan_entry = self._start_plan_entry(category)
        final_text = ""
        try:
            raw_domain_data = self.fragments.get(category)
            has_fragment_data = isinstance(raw_domain_data, Mapping)
            if self.guidance and category not in self.active_domains and has_fragment_data:
                self._register_relaxed_domain(category)

            raw_paragraph = ""
            if self._fallback_mode == "silent":
                raw_paragraph = ""
            elif self._allowed_templates and category not in self._allowed_templates:
                raw_paragraph = ""
            else:
                if not has_fragment_data:
                    raw_paragraph = self._soft_fail_sentence(category) or ""
                else:
                    domain_data = raw_domain_data
                    slots = domain_data.get("slots")
                    if not isinstance(slots, Mapping):
                        slots = {}
                    if not slots:
                        raw_paragraph = self._soft_fail_sentence(category) or ""
                    else:
                        regulation = self.regulations.get(category)
                        paragraph = self._build_locked_paragraph(category, slots, regulation)
                        if paragraph:
                            self._mark_composites(category)
                            raw_paragraph = paragraph
                        else:
                            raw_paragraph = self._soft_fail_sentence(category) or ""

            plan_entry["compiler_input"] = raw_paragraph or ""
            final_text = self._apply_expression_profile(raw_paragraph or "")
            plan_entry["final_text"] = final_text
            return final_text
        finally:
            self._finalize_plan_entry(category)

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
        effect_text = self._slot_fragment_text(slots.get("effect"), "effect")
        if effect_text:
            sentences.append(template["effect"].format(effect_expression=effect_text))
        axis_tension = (self.axis_activation or {}).get("axis_tension")
        include_shadow = axis_tension in {"high", "medium"}
        shadow_text = self._slot_fragment_text(slots.get("shadow"), "shadow")
        if include_shadow and shadow_text:
            sentences.append(template["shadow"].format(shadow_risk=shadow_text))
        potential_text = self._slot_fragment_text(slots.get("potential"), "potential")
        if potential_text:
            sentences.append(template["potential"].format(potential_gain=potential_text))
        return " ".join(sentences)

    def _slot_fragment_text(self, fragment: Mapping[str, Any] | None, slot_name: str | None = None) -> str | None:
        if not fragment or not isinstance(fragment, Mapping):
            return None
        text_value = fragment.get("text")
        sanitized_source = self._sanitize(text_value)
        normalized = self._normalize(sanitized_source)
        if not normalized:
            self._register_slot_plan(slot_name, fragment, False, text_value, "empty_after_sanitize")
            return None
        filtered = self._apply_forbidden_policy(normalized, slot_name)
        if filtered is None:
            self._register_slot_plan(slot_name, fragment, False, normalized, "filtered_by_policy")
            return None
        if contains_verb_phrase(filtered):
            self._register_slot_plan(slot_name, fragment, False, filtered, "contains_verb_phrase")
            return None
        if self._contains_forbidden_language(filtered):
            self._register_slot_plan(slot_name, fragment, False, filtered, "forbidden_language")
            return None
        self._register_slot_plan(slot_name, fragment, True, filtered)
        return filtered

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

    def _register_relaxed_domain(self, domain: str) -> None:
        if domain not in self.narrative_debug_relaxed_domains:
            self.narrative_debug_relaxed_domains.append(domain)

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

    def _start_plan_entry(self, domain: str) -> Dict[str, Any]:
        entry: Dict[str, Any] = {
            "domain": domain,
            "compiler_input": "",
            "final_text": "",
            "slots": {},
            "selected_slots": [],
            "source_fragment_ids": {},
        }
        self.narrative_plan[domain] = entry
        self._current_plan_entry = entry
        self._current_plan_selected_slots = []
        return entry

    def _finalize_plan_entry(self, domain: str) -> None:
        entry = self.narrative_plan.get(domain)
        if not entry:
            return
        selected_slots = sorted(set(self._current_plan_selected_slots))
        entry["selected_slots"] = selected_slots
        entry["slots"] = dict(entry.get("slots", {}))
        entry["source_fragment_ids"] = dict(entry.get("source_fragment_ids", {}))
        if selected_slots:
            if domain not in self.narrative_debug_selected_domains:
                self.narrative_debug_selected_domains.append(domain)
            self.narrative_debug_selected_slots[domain] = selected_slots
            self.narrative_debug_source_fragment_ids[domain] = dict(entry["source_fragment_ids"])
        self._current_plan_entry = None
        self._current_plan_selected_slots = []

    def _register_slot_plan(
        self,
        slot_name: str | None,
        fragment: Mapping[str, Any] | None,
        accepted: bool,
        text: Any | None = None,
        reason: str | None = None,
    ) -> None:
        if not slot_name:
            return
        entry = self._current_plan_entry
        if not entry:
            return

        slot_info: Dict[str, Any] = {
            "accepted": accepted,
            "text": str(text or ""),
            "fragment_id": self._extract_fragment_id(fragment),
        }
        if reason:
            slot_info["reason"] = reason
        if isinstance(fragment, Mapping):
            original_text = fragment.get("text")
            if original_text is not None:
                slot_info["original_text"] = str(original_text)

        entry.setdefault("slots", {})[slot_name] = slot_info
        if accepted:
            selected = self._current_plan_selected_slots
            if slot_name not in selected:
                selected.append(slot_name)
            entry.setdefault("source_fragment_ids", {})[slot_name] = slot_info["fragment_id"]

    @staticmethod
    def _extract_fragment_id(fragment: Mapping[str, Any] | None) -> str:
        if not isinstance(fragment, Mapping):
            return ""
        for key in ("fragment_ref", "fragment_id", "id"):
            candidate = fragment.get(key)
            if candidate:
                return str(candidate)
        return ""

    def _contains_forbidden_language(self, text: str) -> bool:
        lowered = text.lower()
        if any(token in lowered for token in FORBIDDEN_TOKENS):
            return True
        profile_terms = self.expression_profile.get("forbidden_phrases") or []
        return any(str(term).lower() in lowered for term in profile_terms)

    def _apply_forbidden_policy(self, text: str, slot_name: str | None) -> str | None:
        lowered = text.lower()
        forbidden = {
            token.strip().lower()
            for token in FORBIDDEN_TOKENS
            if token and token.strip()
        }
        profile_terms = {
            str(term).strip().lower()
            for term in self.expression_profile.get("forbidden_phrases") or []
            if str(term).strip()
        }
        terms = sorted(forbidden | profile_terms, key=len, reverse=True)
        if not terms:
            return text
        sanitized = text
        actions: List[str] = []
        for term in terms:
            if not term or term not in sanitized.lower():
                continue
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            if not pattern.search(sanitized):
                continue
            replacement = FORBIDDEN_REPLACEMENTS.get(term)
            if replacement:
                sanitized = pattern.sub(replacement, sanitized)
                actions.append(f"replace:{term}")
            else:
                sanitized = pattern.sub("", sanitized)
                actions.append(f"soften:{term}")
        sanitized = self._normalize(sanitized)
        if not sanitized:
            actions.append("drop_clause")
            self._record_quality_actions(slot_name, text, actions)
            return None
        if actions:
            self._record_quality_actions(slot_name, text, actions)
        return sanitized

    def _record_quality_actions(self, slot_name: str | None, original_text: str, actions: List[str]) -> None:
        if not actions:
            return
        self.quality_actions_applied.append(
            {
                "slot": slot_name or "unknown",
                "actions": actions,
                "text": original_text,
            }
        )

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
