from __future__ import annotations

import re

from typing import Any, Dict, List, Mapping

from app.builders.semantic_normalizer import contains_verb_phrase
from app.helpers.domain_normalizer import canon_domain
from app.engine.tone_apply import apply_tone
from app.engine.tone_profile import ToneProfile, compute_tone, load_tone_config


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
    "visibility_vs_control": "Görünürlük ile kontrol arasındaki denge",
    "trait_reinforcement": "Belli bir niteliği güçlendirme yönelimi",
    "balanced_flow": "Dengeyi koruma ihtiyacı",
}

DOMAIN_TEMPLATES: Dict[str, Dict[str, str]] = {
    "identity": {
        "opening": "{core_tension}",
        "effect": "Bu durum seni dış dünyada {effect_expression} biri olarak algılanır hale getirir.",
        "shadow": "Denge bozulduğunda ise {shadow_risk} eğilimi ortaya çıkabilir.",
        "potential": "Ancak bu düzen, doğru regülasyonla {potential_gain} kapasitesine dönüşebilir.",
    },
    "psychology": {
        "opening": "{core_tension}",
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

CAUSE_SENTENCE_LIMIT = 2


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
        self.narrative_anchor: Mapping[str, Any] = getattr(engine_result, "narrative_anchor", {}) or {}
        self.meaning_weighting: Mapping[str, Any] = getattr(engine_result, "meaning_weighting", {}) or {}
        self.guidance: Mapping[str, Any] = getattr(engine_result, "guidance", {}) or {}
        guidance_domains: List[str] = []
        for domain in self.guidance.get("active_domains", []):
            canonical = canon_domain(domain)
            if canonical:
                guidance_domains.append(canonical)
        fragment_domains: List[str] = []
        for domain in self.fragments.keys():
            canonical = canon_domain(domain)
            if canonical:
                fragment_domains.append(canonical)
        if guidance_domains:
            self.active_domains = set(guidance_domains)
            self.narrative_debug_active_domains_source = "guidance"
        else:
            self.active_domains = set(fragment_domains)
            self.narrative_debug_active_domains_source = "phase2"
        self.regulations: Mapping[str, Dict[str, Any]] = getattr(engine_result, "regulations", {}) or {}
        self.expression_profile: Mapping[str, Any] = getattr(engine_result, "expression_profile", {}) or {}
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
        self.tone_profiles: Dict[str, Dict[str, float]] = {}
        self._domain_salience = self._build_domain_salience_map()
        self.tone_enabled = bool(getattr(engine_result, "tone_enabled", True))
        self.compressed_domains: Mapping[str, Any] = getattr(engine_result, "compressed_domains", {}) or {}

    def build(self) -> Dict[str, str]:
        golden_path_enabled = False
        if golden_path_enabled:
            paragraph = self.build_identity_narrative_golden_path(self.fragments)
            if paragraph:
                return {"identity": paragraph}
            return {}

        result: Dict[str, str] = {}
        for category in CATEGORY_LABELS:
            text = self._build_category_text(category)
            if text:
                result[category] = text
        if "identity" not in result and self._identity_slots_present():
            fallback = self._soft_fail_sentence("identity")
            if fallback:
                result["identity"] = fallback
        other_domains = self._build_other_domains_summary()
        if other_domains:
            result["other_domains"] = other_domains
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
        bound = self._build_bound_paragraph(domain, slots, regulation)
        if bound:
            return bound
        template = DOMAIN_TEMPLATES.get(domain)
        if not template:
            return None
        core_tension = self._core_tension_phrase(regulation)
        header = template["opening"].format(core_tension=core_tension).strip()
        return header or None

    def _anchor_for_domain(self, domain: str) -> Mapping[str, Any] | None:
        na = self.narrative_anchor
        if isinstance(na, Mapping) and str(na.get("domain") or "").lower() == str(domain).lower():
            return na
        return None

    def _anchor_sentence_for_domain(
        self,
        domain: str,
        slots: Mapping[str, Dict[str, Any]],
    ) -> str | None:
        anchor_payload = self._anchor_for_domain(domain)
        if anchor_payload:
            sentence = str(anchor_payload.get("anchor_sentence") or "").strip()
            if sentence:
                return self._ensure_sentence(sentence)
        cause_text = self._slot_fragment_text(slots.get("cause"), "cause")
        mechanism_text = self._slot_fragment_text(slots.get("mechanism"), "mechanism")
        anchor = self._compose_anchor_sentence(cause_text, mechanism_text)
        return self._ensure_sentence(anchor) if anchor else None

    def _build_bound_paragraph(
        self,
        domain: str,
        slots: Mapping[str, Dict[str, Any]],
        regulation: Mapping[str, Any] | None,
    ) -> str | None:
        recognition = self._recognition_sentence(domain, regulation)
        experienced = self._experienced_reality_sentence(slots)
        potential = self._potential_sentence(slots)
        shadow = self._shadow_sentence(slots)
        upper = self._upper_meaning_sentence(domain)

        tone = self._tone_profile_for_domain(domain, slots, regulation) if self.tone_enabled else None
        if tone:
            recognition = self._apply_tone_section(recognition, tone, "recognition")
            experienced = self._apply_tone_section(experienced, tone, "experienced")
            potential = self._apply_tone_section(potential, tone, "potential")
            shadow = self._apply_tone_section(shadow, tone, "shadow")
            upper = self._apply_tone_section(upper, tone, "upper")

        recognition = self._limit_sentences(recognition, max_count=1)
        experienced = self._limit_sentences(experienced, max_count=4)
        potential = self._limit_sentences(potential, max_count=2)
        shadow = self._limit_sentences(shadow, max_count=1)
        upper = self._limit_sentences(upper, max_count=1)

        sentences = [
            sentence
            for sentence in (recognition, experienced, potential, shadow, upper)
            if sentence
        ]
        if not sentences:
            return None
        return " ".join(sentences)

    def _recognition_sentence(self, domain: str, regulation: Mapping[str, Any] | None) -> str | None:
        primary = str(self.meaning_weighting.get("primary_theme") or "").strip()
        secondary = str(self.meaning_weighting.get("secondary_theme") or "").strip()
        label = CATEGORY_LABELS.get(domain, domain.capitalize())
        if primary and secondary and primary != secondary:
            theme_summary = f"{primary} ve {secondary}"
            sentence = f"Bu harita, {label} alaninda {theme_summary} [INTENSITY_OBJ] anlatir."
        elif primary:
            sentence = f"Bu harita, {label} alaninda {primary} [INTENSITY_OBJ] anlatir."
        else:
            core_tension = self._core_tension_phrase(regulation)
            sentence = f"Bu harita, {label} alaninda {core_tension} hikayesini anlatir."
        return self._ensure_sentence(sentence)

    def _experienced_reality_sentence(self, slots: Mapping[str, Dict[str, Any]]) -> str | None:
        mechanism_text = self._slot_fragment_text(slots.get("mechanism"), "mechanism")
        if not mechanism_text:
            return None
        cause_text = self._slot_fragment_text(slots.get("cause"), "cause")
        extra_causes = self._supporting_texts(slots.get("cause"), limit=CAUSE_SENTENCE_LIMIT - 1)
        cause_bits = [text for text in [cause_text, *extra_causes] if text]
        if cause_bits:
            joined = " ve ".join(cause_bits[:CAUSE_SENTENCE_LIMIT])
            sentence = (
                f"Deneyim duzeyinde, {mechanism_text}; bunun arka planinda {joined} etkisi bulunur."
            )
        else:
            sentence = f"Deneyim duzeyinde, {mechanism_text} baskin bir psikolojik akistir."
        return self._ensure_sentence(sentence)

    def _potential_sentence(self, slots: Mapping[str, Dict[str, Any]]) -> str | None:
        effect_text = self._slot_fragment_text(slots.get("effect"), "effect")
        potential_text = self._slot_fragment_text(slots.get("potential"), "potential")
        if effect_text and potential_text:
            sentence = f"Bu, {effect_text} hissini dogururken {potential_text} yonune de acilir."
        elif effect_text:
            sentence = f"Bu, {effect_text} yonune dogru akar."
        elif potential_text:
            sentence = f"Bu akista {potential_text} kapasitesi belirir."
        else:
            return None
        return self._ensure_sentence(sentence)

    def _shadow_sentence(self, slots: Mapping[str, Dict[str, Any]]) -> str | None:
        shadow_text = self._slot_fragment_text(slots.get("shadow"), "shadow")
        if not shadow_text:
            return None
        template = (load_tone_config().get("shadow_safety") or {}).get("template")
        if isinstance(template, str) and "{shadow_text}" in template:
            sentence = template.format(shadow_text=shadow_text)
        else:
            sentence = f"Golge tarafta ise {shadow_text} kisa ama net bir risk olabilir."
        return self._ensure_sentence(sentence)

    def _upper_meaning_sentence(self, domain: str) -> str | None:
        if not self._upper_meaning_allowed():
            return None
        upper_text = self._upper_meaning_for_domain(domain)
        if not upper_text:
            return None
        cleaned = self._sanitize_upper_text(upper_text)
        if not cleaned:
            return None
        return self._ensure_sentence(f"Ust anlamda ise {cleaned}")

    def _upper_meaning_allowed(self) -> bool:
        allowed = self.meaning_weighting.get("upper_meaning_allowed")
        if isinstance(allowed, bool):
            return allowed
        strain = ((self.meta_info.get("strain_resilience") or {}).get("strain") or {}).get("score")
        resilience = ((self.meta_info.get("strain_resilience") or {}).get("resilience") or {}).get("score")
        try:
            return float(strain) >= 0.6 and float(resilience) >= 0.6
        except (TypeError, ValueError):
            return False

    def _upper_meaning_for_domain(self, domain: str) -> str | None:
        canonical_domain = canon_domain(domain) or domain
        domain_composites = []
        for comp in self.composites:
            comp_domain = canon_domain(comp.get("domain")) or comp.get("domain")
            if comp_domain == canonical_domain:
                domain_composites.append(comp.get("composite_id"))
        for comp_id in domain_composites:
            entry = self.upper_map.get(comp_id)
            if not entry:
                continue
            meanings = entry.get("upper_meaning") or []
            if meanings:
                return str(meanings[0]).strip()
        return None

    def _sanitize_upper_text(self, text: str) -> str | None:
        sanitized = self._sanitize(text)
        normalized = self._normalize(sanitized)
        if not normalized:
            return None
        filtered = self._apply_forbidden_policy(normalized, None)
        if filtered is None:
            return None
        if contains_verb_phrase(filtered):
            return None
        if self._contains_forbidden_language(filtered):
            return None
        return filtered

    def _supporting_texts(
        self,
        fragment: Mapping[str, Any] | None,
        *,
        limit: int,
    ) -> List[str]:
        if not fragment or limit <= 0:
            return []
        supporting = fragment.get("supporting_facts") or []
        texts: List[str] = []
        for entry in supporting:
            if len(texts) >= limit:
                break
            if not isinstance(entry, Mapping):
                continue
            text = entry.get("text")
            cleaned = self._sanitize_upper_text(str(text or ""))
            if cleaned:
                texts.append(cleaned)
        return texts

    def _build_domain_salience_map(self) -> Dict[str, Dict[str, float]]:
        scores: Dict[str, float] = {}
        for domain, entry in self.fragments.items():
            slots = entry.get("slots") if isinstance(entry, Mapping) else {}
            if not isinstance(slots, Mapping):
                continue
            salience_scores = [
                float(fragment.get("salience_score") or 0.0)
                for fragment in slots.values()
                if isinstance(fragment, Mapping)
            ]
            if salience_scores:
                salience_scores.sort(reverse=True)
                scores[domain] = sum(salience_scores[:2])
            else:
                scores[domain] = 0.0
        max_score = max(scores.values(), default=0.0) or 1.0
        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        result: Dict[str, Dict[str, float]] = {}
        for idx, (domain, score) in enumerate(ranked, start=1):
            result[domain] = {
                "score": round(min(score / max_score, 1.0), 4),
                "rank": float(idx),
            }
        return result

    def _domain_uncertainty(self, slots: Mapping[str, Dict[str, Any]]) -> float:
        if not slots:
            return 1.0
        filled = sum(1 for name in SLOT_NAMES if slots.get(name))
        total = len(SLOT_NAMES) or 1
        coverage = filled / total
        return max(0.0, min(1.0, 1.0 - coverage))

    def _tone_profile_for_domain(
        self,
        domain: str,
        slots: Mapping[str, Dict[str, Any]],
        regulation: Mapping[str, Any] | None,
    ) -> ToneProfile | None:
        domain_key = canon_domain(domain) or domain
        salience = self._domain_salience.get(domain_key) or {"score": 0.5, "rank": 1.0}
        uncertainty = self._domain_uncertainty(slots)
        strain_block = (self.meta_info.get("strain_resilience") or {}).get("strain") or {}
        resilience_block = (self.meta_info.get("strain_resilience") or {}).get("resilience") or {}
        upper_used = bool(self._upper_meaning_for_domain(domain) and self._upper_meaning_allowed())
        data_quality = {
            "uncertainty": uncertainty,
            "strain": strain_block.get("score", 0.0),
            "resilience": resilience_block.get("score", 0.0),
            "upper_meaning_used": upper_used,
        }
        tone = compute_tone(regulation, self.meaning_weighting, salience, data_quality)
        self.tone_profiles[domain_key] = tone.to_dict()
        return tone

    def _apply_tone_section(self, text: str | None, tone: ToneProfile, section: str) -> str | None:
        if not text:
            return None
        toned = apply_tone(text, tone, section=section)
        return toned or None

    def _limit_sentences(self, text: str | None, *, max_count: int) -> str | None:
        if not text:
            return None
        parts = [part.strip() for part in re.split(r"(?<=[.!?])\\s+", text) if part.strip()]
        if len(parts) <= max_count:
            return text
        trimmed = " ".join(parts[:max_count])
        return trimmed

    def _build_other_domains_summary(self) -> str | None:
        items = self.compressed_domains.get("items") if isinstance(self.compressed_domains, Mapping) else None
        if not items:
            return None
        summaries: List[str] = []
        for item in items:
            if not isinstance(item, Mapping):
                continue
            domain = canon_domain(item.get("domain")) or str(item.get("domain") or "").strip().lower()
            text = item.get("text")
            if not domain or not text:
                continue
            label = CATEGORY_LABELS.get(domain, domain.capitalize())
            sentence = self._ensure_sentence(f"Diger alanlarda {label} icin {text}")
            summaries.append(sentence)
        if not summaries:
            return None
        return " ".join(summaries)

    def _compose_anchor_sentence(self, cause: str | None, mechanism: str | None) -> str | None:
        cause_text = cause.strip() if cause else ""
        mechanism_text = mechanism.strip() if mechanism else ""
        if cause_text and mechanism_text:
            return f"Genellikle, {cause_text} olduğunda, {mechanism_text} eğilimi ortaya çıkar."
        if cause_text:
            return f"Genellikle, {cause_text} olduğunda içsel bir hareketlenme yaşanır."
        if mechanism_text:
            return f"Genellikle, {mechanism_text} yöneliminde olursun."
        return None

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

    def build_identity_narrative_golden_path(self, fragments: Mapping[str, Any]) -> str | None:
        """
        GOLDEN PATH v1 — JOVIA CANON
        'Sen / senin yapin' dili
        Tanimlayici, yargisiz, akiskan
        """

        identity = fragments.get("identity")
        if not identity:
            return None

        cause = identity.get("cause", {}).get("text")
        effect = identity.get("effect", {}).get("text")
        shadow = identity.get("shadow", {}).get("text")

        if not cause or not effect:
            return None

        paragraph = (
            "Senin yapin, kimligini cogu zaman kontrollu ve olculu bir durus uzerinden "
            "insa etmeye calisirken, ayni anda "
            f"{cause} ile birlikte calisiyor. "
            "Bu iki yonun eszamanliligi, icinde "
            f"{effect} gibi bir deneyim yaratabiliyor. "
        )

        if shadow:
            paragraph += (
                f"Bazen de {shadow}, "
                "hangi taraftan hareket ettigini netlestirmeyi zorlastirabiliyor."
            )

        return paragraph
