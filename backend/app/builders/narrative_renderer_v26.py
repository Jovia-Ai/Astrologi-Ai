from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from app.builders.phrase_mapper import Claim
from app.engine.tone_apply import apply_tone
from app.engine.tone_profile import ToneProfile

# V26 dead branch removed 2026-05-20 per matrix §7.2b + S2.2 trace
# audit. `NarrativeDomainOutput`, `build_domain_narrative_v26`, and
# the `StylePackV26TR` import were unused at runtime (only callers
# were inside `narrative_binding.build_narrative`, which was itself
# unused). The live `core_story` renderer path was migrated to
# `app.natal.narrative.core_story.renderer`; residue below is kept
# intentionally for deferred orphan-helper cleanup only.


CORE_STORY_SLOT_ORDER = ["cause", "mechanism", "effect", "shadow", "potential"]
def _select_focus_claims(claims: Sequence[Claim], *, limit: int = 2) -> list[Claim]:
    if not claims:
        return []
    ranked = sorted(claims, key=lambda claim: claim.salience, reverse=True)
    return ranked[:limit]


def _section(section_type: str, paragraphs: Sequence[str]) -> list[dict]:
    cleaned = [para for para in paragraphs if para]
    if not cleaned:
        return []
    text = "\n\n".join(cleaned).strip()
    return [{"type": section_type, "text": text}]


def _join_sections(sections: Sequence[Mapping[str, Any]]) -> str:
    blocks: list[str] = []
    for section in sections:
        text = str(section.get("text") or "").strip()
        if text:
            blocks.append(text)
    return "\n\n".join(blocks)


def _resolve_tone_profile(profile: Mapping[str, Any] | ToneProfile | None) -> ToneProfile:
    if isinstance(profile, ToneProfile):
        return profile
    if isinstance(profile, Mapping):
        required = {"directness", "warmth", "intensity", "certainty", "tempo", "distance"}
        if required.issubset(profile.keys()):
            return ToneProfile(
                directness=float(profile.get("directness") or 0.5),
                warmth=float(profile.get("warmth") or 0.55),
                intensity=float(profile.get("intensity") or 0.5),
                certainty=float(profile.get("certainty") or 0.55),
                tempo=float(profile.get("tempo") or 0.5),
                distance=float(profile.get("distance") or 0.5),
            )
    return ToneProfile(0.5, 0.55, 0.5, 0.55, 0.5, 0.5)


def _apply_tone_safe(text: str, tone: ToneProfile, section: str) -> str:
    if not text:
        return text
    return apply_tone(text, tone, section=section)


def _build_fragment_index(
    phase2_snapshot: Mapping[str, Any]
) -> dict[str, Mapping[str, Mapping[str, Any]]]:
    index: dict[str, Mapping[str, Mapping[str, Any]]] = {}
    for domain, entry in phase2_snapshot.items():
        slots = entry.get("slots") if isinstance(entry, Mapping) else None
        if not isinstance(slots, Mapping):
            continue
        index[domain] = slots
    return index


def _build_fragment_id_map(
    fragments: Mapping[str, Mapping[str, Mapping[str, Any]]]
) -> dict[str, Mapping[str, Any]]:
    fragment_map: dict[str, Mapping[str, Any]] = {}
    for domain_slots in fragments.values():
        for fragment in domain_slots.values():
            if not isinstance(fragment, Mapping):
                continue
            fragment_id = fragment.get("fragment_id")
            if fragment_id:
                fragment_map[str(fragment_id)] = fragment
            for supporting_key in ("supporting_facts", "supporting_facts_full"):
                supporting = fragment.get(supporting_key) or []
                if not isinstance(supporting, list):
                    continue
                for fact in supporting:
                    if not isinstance(fact, Mapping):
                        continue
                    fact_id = fact.get("fragment_id")
                    if fact_id and fact_id not in fragment_map:
                        fragment_map[str(fact_id)] = fact
    return fragment_map


def _build_fragment_id_text_map(phase2_snapshot: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    accepted = ((phase2_snapshot.get("slots") or {}).get("accepted") or [])
    fragment_map: dict[str, Mapping[str, Any]] = {}
    if not isinstance(accepted, list):
        return fragment_map
    for fragment in accepted:
        if not isinstance(fragment, Mapping):
            continue
        fragment_id = fragment.get("fragment_id")
        if not fragment_id:
            continue
        text = fragment.get("original_text") or fragment.get("normalized_text") or ""
        text = " ".join(str(text).split()).strip()
        if not text:
            continue
        fragment_map[str(fragment_id)] = {
            "fragment_id": str(fragment_id),
            "text": text,
        }
    return fragment_map


def _build_id_to_text(phase2_snapshot: Mapping[str, Any]) -> dict[str, str]:
    accepted = ((phase2_snapshot.get("slots") or {}).get("accepted") or [])
    id_to_text: dict[str, str] = {}
    if not isinstance(accepted, list):
        return id_to_text
    for fragment in accepted:
        if not isinstance(fragment, Mapping):
            continue
        fragment_id = fragment.get("fragment_id")
        if not fragment_id:
            continue
        text = fragment.get("original_text") or fragment.get("normalized_text") or ""
        text = " ".join(str(text).split()).strip()
        if text:
            id_to_text[str(fragment_id)] = text
    return id_to_text


def _plan_section_map(core_story_plan: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    sections = core_story_plan.get("sections") if isinstance(core_story_plan, Mapping) else None
    if not isinstance(sections, list):
        return {}
    return {section.get("section_id"): section for section in sections if isinstance(section, Mapping)}


def _pick_sentences(
    plan_sections: Mapping[str, Mapping[str, Any]],
    section_id: str,
    id_to_text: Mapping[str, str],
    used_ids: set[str],
    used_fingerprints: set[str],
    *,
    min_n: int,
    max_n: int,
    slot_order: Sequence[str] | None = None,
) -> list[str]:
    section = plan_sections.get(section_id) or {}
    slots = section.get("slots") if isinstance(section, Mapping) else None
    if not isinstance(slots, Mapping):
        return []
    out: list[str] = []
    for slot in (slot_order or CORE_STORY_SLOT_ORDER):
        entry = slots.get(slot) or {}
        if not isinstance(entry, Mapping):
            continue
        fragment_id = entry.get("fragment_id")
        if not fragment_id:
            continue
        fragment_id = str(fragment_id)
        if fragment_id in used_ids:
            continue
        text = id_to_text.get(fragment_id, "").strip()
        if text:
            fingerprint = _fingerprint_text(text)
            if fingerprint and fingerprint in used_fingerprints:
                continue
            out.append(text)
            used_ids.add(fragment_id)
            if fingerprint:
                used_fingerprints.add(fingerprint)
        if len(out) >= max_n:
            break
    return out[:max_n] if out else []


def _resolve_slot_text(
    plan_sections: Mapping[str, Mapping[str, Any]],
    section_id: str,
    slot: str,
    id_to_text: Mapping[str, str],
) -> str:
    section = plan_sections.get(section_id) or {}
    slots = section.get("slots") if isinstance(section, Mapping) else None
    if not isinstance(slots, Mapping):
        return ""
    entry = slots.get(slot) or {}
    if not isinstance(entry, Mapping):
        return ""
    fragment_id = entry.get("fragment_id")
    if not fragment_id:
        return ""
    return id_to_text.get(str(fragment_id), "").strip()


def _extend_from_section(
    paragraph: list[str],
    plan_sections: Mapping[str, Mapping[str, Any]],
    section_id: str,
    id_to_text: Mapping[str, str],
    used_ids: set[str],
    used_fingerprints: set[str],
    *,
    slot_order: Sequence[str],
    max_count: int,
) -> None:
    if len(paragraph) >= max_count:
        return
    section = plan_sections.get(section_id) or {}
    slots = section.get("slots") if isinstance(section, Mapping) else None
    if not isinstance(slots, Mapping):
        return
    for slot in slot_order:
        if len(paragraph) >= max_count:
            break
        entry = slots.get(slot) or {}
        if not isinstance(entry, Mapping):
            continue
        fragment_id = entry.get("fragment_id")
        if not fragment_id:
            continue
        fragment_id = str(fragment_id)
        if fragment_id in used_ids:
            continue
        text = id_to_text.get(fragment_id, "").strip()
        if not text:
            continue
        fingerprint = _fingerprint_text(text)
        if fingerprint and fingerprint in used_fingerprints:
            continue
        paragraph.append(text)
        used_ids.add(fragment_id)
        if fingerprint:
            used_fingerprints.add(fingerprint)


def _ensure_min_sentences(
    paragraph: list[str],
    fallback_pool: Sequence[str],
    *,
    target_min: int,
) -> None:
    if len(paragraph) >= target_min:
        return
    for candidate in fallback_pool:
        if len(paragraph) >= target_min:
            break
        if not candidate or candidate in paragraph:
            continue
        fingerprint = _fingerprint_text(candidate)
        if fingerprint and fingerprint in (_fingerprint_text(text) for text in paragraph):
            continue
        paragraph.append(candidate)


def _join_sentences(sentences: Sequence[str]) -> str:
    cleaned: list[str] = []
    for sentence in sentences:
        text = _normalize_sentence_start(str(sentence).strip())
        if not text:
            continue
        if text[-1] not in ".!?":
            text += "."
        cleaned.append(text)
    return " ".join(cleaned).strip()


def _fingerprint_text(text: str) -> str:
    lowered = "".join(ch for ch in text.lower() if ch.isalnum() or ch.isspace())
    return " ".join(lowered.split())


def _insert_micro_transition(paragraph: list[str], sentence: str, *, position: int) -> None:
    if not paragraph:
        return
    normalized = _fingerprint_text(sentence)
    if any(_fingerprint_text(item) == normalized for item in paragraph):
        return
    if position <= 0:
        paragraph.insert(0, sentence)
        return
    if position >= len(paragraph):
        paragraph.append(sentence)
        return
    paragraph.insert(position, sentence)


def _build_spine_index(dynamic_insights: Mapping[str, Any] | None) -> dict[str, Mapping[str, Any]]:
    index: dict[str, Mapping[str, Any]] = {}
    if not dynamic_insights:
        return index
    selected = dynamic_insights.get("selected")
    if not isinstance(selected, list):
        return index
    for entry in selected:
        if not isinstance(entry, Mapping):
            continue
        insight_id = entry.get("insight_id")
        if insight_id:
            index[str(insight_id)] = entry
    return index


def _build_insight_index(
    dynamic_insights: Mapping[str, Any] | None,
) -> dict[tuple[str, str], Mapping[str, Any]]:
    index: dict[tuple[str, str], Mapping[str, Any]] = {}
    if not dynamic_insights:
        return index
    selected = dynamic_insights.get("selected")
    if not isinstance(selected, list):
        return index
    for entry in selected:
        if not isinstance(entry, Mapping):
            continue
        insight_id = entry.get("insight_id")
        instance_id = entry.get("instance_id")
        if insight_id and instance_id:
            index[(str(insight_id), str(instance_id))] = entry
    return index


def _build_meaning_index(
    composite_meanings: Mapping[str, Any] | None,
) -> dict[tuple[str, str], Mapping[str, Any]]:
    index: dict[tuple[str, str], Mapping[str, Any]] = {}
    if not composite_meanings:
        return index
    selected = composite_meanings.get("selected")
    if not isinstance(selected, list):
        return index
    for entry in selected:
        if not isinstance(entry, Mapping):
            continue
        meaning_id = entry.get("meaning_id")
        instance_id = entry.get("instance_id")
        if meaning_id and instance_id:
            index[(str(meaning_id), str(instance_id))] = entry
    return index


def _headline_ref(core_story_plan: Mapping[str, Any]) -> Mapping[str, Any] | None:
    sections = core_story_plan.get("sections") if isinstance(core_story_plan, Mapping) else None
    if isinstance(sections, list):
        for section in sections:
            if not isinstance(section, Mapping):
                continue
            if section.get("section_id") != "inner_core":
                continue
            headline = section.get("headline")
            if not isinstance(headline, Mapping):
                continue
            meaning_id = headline.get("cm_id") or headline.get("meaning_id")
            instance_id = headline.get("instance_id")
            if meaning_id and instance_id:
                return {"meaning_id": str(meaning_id), "instance_id": str(instance_id)}
    composite = core_story_plan.get("composite_meanings") if isinstance(core_story_plan, Mapping) else None
    if not isinstance(composite, Mapping):
        return None
    selected = composite.get("selected")
    if not isinstance(selected, list) or not selected:
        return None
    entry = selected[0]
    if not isinstance(entry, Mapping):
        return None
    meaning_id = entry.get("meaning_id") or entry.get("cm_id")
    instance_id = entry.get("instance_id")
    if not meaning_id or not instance_id:
        return None
    return {"meaning_id": str(meaning_id), "instance_id": str(instance_id)}


def _find_composite_ref(
    core_story_plan: Mapping[str, Any],
    meaning_id: str,
    *,
    fallback_id: str | None = None,
) -> Mapping[str, Any] | None:
    composite = core_story_plan.get("composite_meanings") if isinstance(core_story_plan, Mapping) else None
    if not isinstance(composite, Mapping):
        return None
    selected = composite.get("selected")
    if not isinstance(selected, list):
        return None
    for entry in selected:
        if not isinstance(entry, Mapping):
            continue
        if entry.get("meaning_id") == meaning_id and entry.get("instance_id"):
            return {"meaning_id": str(entry.get("meaning_id")), "instance_id": str(entry.get("instance_id"))}
    if fallback_id:
        for entry in selected:
            if not isinstance(entry, Mapping):
                continue
            if entry.get("meaning_id") == fallback_id and entry.get("instance_id"):
                return {"meaning_id": str(entry.get("meaning_id")), "instance_id": str(entry.get("instance_id"))}
    return None


def _pick_spine_ref(core_story_plan: Mapping[str, Any], *, paragraph: int) -> Mapping[str, Any] | None:
    sections = core_story_plan.get("sections") if isinstance(core_story_plan, Mapping) else None
    if isinstance(sections, list):
        for section in sections:
            if not isinstance(section, Mapping):
                continue
            if paragraph == 1 and section.get("section_id") != "inner_core":
                continue
            if paragraph == 2 and section.get("section_id") != "emotions":
                continue
            if paragraph == 3 and section.get("section_id") != "relationships":
                continue
            spine = section.get("spine")
            if isinstance(spine, Mapping):
                insight_id = spine.get("insight_id")
                instance_id = spine.get("instance_id")
                if insight_id and instance_id:
                    return {"insight_id": str(insight_id), "instance_id": str(instance_id)}
    spines = core_story_plan.get("spines") if isinstance(core_story_plan, Mapping) else None
    if not isinstance(spines, list):
        return None
    for entry in spines:
        if not isinstance(entry, Mapping):
            continue
        if entry.get("paragraph") != paragraph:
            continue
        insight_id = entry.get("spine_id")
        instance_id = entry.get("instance_id")
        if insight_id and instance_id:
            return {"insight_id": str(insight_id), "instance_id": str(instance_id)}
    return None


def _build_fragment_index(phase2_snapshot: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    idx: dict[str, Mapping[str, Any]] = {}
    slots = (phase2_snapshot or {}).get("slots") or {}
    accepted = slots.get("accepted") or []
    if not isinstance(accepted, list):
        return idx
    for frag in accepted:
        if not isinstance(frag, Mapping):
            continue
        fid = frag.get("fragment_id")
        if isinstance(fid, str) and fid:
            idx[fid] = frag
    return idx


def _resolve_fragment_text(fragment_id: str, frag_index: Mapping[str, Mapping[str, Any]]) -> str:
    frag = frag_index.get(fragment_id) or {}
    text = frag.get("original_text") or frag.get("normalized_text") or ""
    return str(text).strip()


def _split_sentences(text: str) -> list[str]:
    cleaned = " ".join(str(text or "").replace("!", ".").replace("?", ".").split())
    if not cleaned:
        return []
    parts = [part.strip() for part in cleaned.split(".") if part.strip()]
    return parts


def _capitalize_turkish_initial(text: str) -> str:
    value = str(text or "").strip()
    if not value:
        return ""
    first = value[:1]
    mapped = {"i": "İ", "ı": "I"}.get(first, first.upper())
    return mapped + value[1:]


def _normalize_sentence(sentence: str) -> str:
    cleaned = " ".join(str(sentence or "").split())
    if not cleaned:
        return ""
    if cleaned[0].islower():
        cleaned = _capitalize_turkish_initial(cleaned)
    if cleaned[-1] not in ".!?":
        cleaned += "."
    return cleaned


def _sentence_key(sentence: str) -> str:
    cleaned = str(sentence or "").lower()
    cleaned = re.sub(r"[^\w\s]", "", cleaned)
    return " ".join(cleaned.split())


def _dedupe_sentences(sentences: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for sentence in sentences:
        key = _sentence_key(sentence)
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(sentence)
    return deduped


def _cap_connector_usage(sentences: list[str], *, max_per_paragraph: int = 1) -> tuple[list[str], int]:
    connector_count = 0
    capped: list[str] = []
    tokens = (
        "Temelde",
        "Aslında",
        "Çoğu zaman",
        "Bunu çoğunlukla",
        "Bu da",
        "Sonuç olarak",
        "Yani",
        "İçeride",
        "Dışarıdan",
    )
    used_prefixes: set[str] = set()
    for sentence in sentences:
        trimmed = sentence.strip()
        lower = trimmed.lower()
        token = next((t for t in tokens if lower.startswith(t.lower())), None)
        if token:
            token_key = token.lower()
            if token_key in used_prefixes or connector_count >= max_per_paragraph:
                trimmed = trimmed[len(token) :].lstrip(" ,:;-")
                trimmed = _normalize_sentence(trimmed)
            else:
                connector_count += 1
                used_prefixes.add(token_key)
        capped.append(trimmed)
    return capped, connector_count


def _soften_shadow(s: str, *, anchor: str | None = None) -> str:
    _ = anchor
    cleaned = s.strip()
    prefix = "Bu ihtiyaç yükseldiğinde "
    lowered = cleaned.lower()
    if lowered.startswith(("aşırı", "fazla", "ego", "ben-merkez")) or "," in cleaned:
        core = cleaned[0].lower() + cleaned[1:] if cleaned and cleaned[0].isupper() else cleaned
        return f"{prefix}{core} eğilimi ortaya çıkabilir."
    return f"{prefix}{cleaned} ortaya çıkabilir."


def _is_enum_like(text: str) -> bool:
    if text.count(",") >= 2:
        return True
    if re.search(r"\bve\b", text) and text.count(",") >= 1:
        return True
    return False


def _wrap_shadow(shadow_text: str) -> list[str]:
    t = shadow_text.strip().rstrip(".")
    if not t:
        return []
    if _is_enum_like(t):
        return [
            f"Bu ihtiyaç yükseldiğinde, {t} daha kolay tetiklenebilir.",
            "Bu bir kusur değil; sistemin yük bindirdiği alan.",
        ]
    lowered = t.lower()
    return [
        f"Baskı arttığında {lowered} ortaya çıkabilir.",
        "Bu bir kusur değil; sistemin yük bindirdiği alan.",
    ]


def _fix_duplicate_tokens(s: str) -> str:
    return re.sub(r"\b(\w+)\s+\1\b", r"\1", s, flags=re.IGNORECASE)


def _clean_sentence(s: str) -> str:
    cleaned = s.strip()
    cleaned = _fix_duplicate_tokens(cleaned)
    cleaned = re.sub(r"\s+,", ",", cleaned)
    cleaned = re.sub(r",\s+\.", ".", cleaned)
    return cleaned


_CORE_STORY_STOPWORDS = {
    "ve",
    "ile",
    "bu",
    "bir",
    "da",
    "de",
    "için",
    "gibi",
    "ama",
    "daha",
    "çok",
    "olan",
    "oluyor",
    "olduğunda",
    "geldiğinde",
}


def _core_story_tokens(text: str) -> set[str]:
    tokens = re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ]+", str(text or "").lower())
    return {
        token
        for token in tokens
        if len(token) >= 3 and token not in _CORE_STORY_STOPWORDS
    }


def _core_story_overlap(a: str, b: str) -> float:
    left = _core_story_tokens(a)
    right = _core_story_tokens(b)
    if not left or not right:
        return 0.0
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def _polish_core_story_sentence(sentence: str) -> str:
    cleaned = str(sentence or "").replace("‘", "'").replace("’", "'").strip()
    if not cleaned:
        return ""
    cleaned = re.sub(r"^Bu ihtiyaç yükseldiğinde,\s*", "Yük arttığında ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^Böylece\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(
        r"^Psikolojik temelinde\s+'?([^.!?']{6,})\.?$",
        r"İçeride sık sık '\1?' sorusu çalışıyor.",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s+\?'", "?'", cleaned)
    cleaned = re.sub(r",\s*([A-ZÇĞİÖŞÜ])", lambda m: ", " + m.group(1).lower(), cleaned, count=1)
    cleaned = re.sub(r"([?!])\s+'", r"\1'", cleaned)
    cleaned = re.sub(r"'\s+sorusu", "' sorusu", cleaned)
    cleaned = cleaned.replace("? '", "?'").replace("! '", "!'")
    cleaned = _clean_sentence(cleaned)
    return _normalize_sentence(cleaned)


def _polish_core_story_paragraph(text: str) -> str:
    sentences = [_polish_core_story_sentence(piece) for piece in _split_sentences(text)]
    filtered: list[str] = []
    for sentence in sentences:
        if not sentence:
            continue
        if any(_core_story_overlap(sentence, prior) >= 0.82 for prior in filtered):
            continue
        filtered.append(sentence)
    filtered, _ = _cap_connector_usage(filtered, max_per_paragraph=1)
    return " ".join(filtered).strip()


def _bridge_inner_outer(sentences: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(sentences):
        a = sentences[i].strip()
        b = sentences[i + 1].strip() if i + 1 < len(sentences) else ""
        if a.startswith("Bazen içeride") and b.startswith("Kendini tanıdıkça"):
            merged = a.rstrip(".") + "; bu yüzden " + b[0].lower() + b[1:]
            merged += " Bu, dışarıya yansıttığın kimliği de destekler."
            out.append(merged)
            i += 2
            continue
        out.append(a)
        i += 1
    return out

def _collapse_repeated_leads(text: str) -> str:
    return re.sub(r"\b(Temelde[, ]+){2,}", "Temelde, ", text, flags=re.I)


def _resolve_sentence_role(role: str, sentence: str) -> str:
    if role in {"cause", "mechanism", "effect", "shadow", "potential"}:
        return role
    lowered = sentence.lower()
    if any(token in lowered for token in ("baskı", "gerilim", "gölge", "zorlanma")):
        return "shadow"
    if any(token in lowered for token in ("doğru kullanıldığında", "geliştirdiğinde", "açıldığında")):
        return "potential"
    if any(token in lowered for token in ("bu yüzden", "böylece", "işleyiş")):
        return "mechanism"
    return "effect"


def _needs_connector(prev_role: str, next_role: str) -> bool:
    return (prev_role, next_role) in {
        ("cause", "effect"),
        ("mechanism", "effect"),
        ("shadow", "potential"),
        ("effect", "potential"),
        ("cause", "potential"),
        ("lived_experience", "potential"),
    }


def _pick_connector(prev_role: str, next_role: str, used_connectors: set[str]) -> str:
    mapping = {
        ("cause", "effect"): "Bu yüzden",
        ("mechanism", "effect"): "Böylece",
        ("shadow", "potential"): "Ama",
        ("effect", "potential"): "Bu yüzden",
        ("cause", "potential"): "Sonuç olarak",
        ("lived_experience", "potential"): "Bu yüzden",
    }
    connector = mapping.get((prev_role, next_role), "")
    if not connector or connector in used_connectors:
        return ""
    return connector


def _join_with_connector(prev: str, nxt: str, connector: str) -> str:
    _ = prev
    if not connector:
        return nxt
    return f"{connector} {nxt}".strip()


def _has_leading_connector(sentence: str) -> bool:
    lowered = sentence.strip().lower()
    for token in CONNECTOR_TOKENS:
        if lowered.startswith(token.lower()):
            return True
    for token in ("Bu yüzden", "Böylece", "Bu da", "Sonuç olarak", "Bazen", "Ama"):
        if lowered.startswith(token.lower()):
            return True
    return False


def _dedupe_within_paragraph(sentences_with_role: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    deduped: list[dict[str, str]] = []
    for entry in sentences_with_role:
        sentence = entry.get("sentence", "")
        if len(sentence.split()) < 8:
            deduped.append(entry)
            continue
        key = _sentence_key(sentence)
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(entry)
    return deduped


def _add_connectors_with_cap(
    sentences_with_role: list[dict[str, str]],
    *,
    max_connectors: int,
) -> tuple[list[str], int]:
    if not sentences_with_role:
        return [], 0
    used_connectors: set[str] = set()
    out: list[str] = []
    connector_count = 0
    for idx, entry in enumerate(sentences_with_role):
        sentence = entry.get("sentence", "")
        role = entry.get("role", "")
        if idx > 0:
            prev_role = sentences_with_role[idx - 1].get("role", "")
            if (
                connector_count < max_connectors
                and _needs_connector(prev_role, role)
                and not _has_leading_connector(sentence)
            ):
                connector = _pick_connector(prev_role, role, used_connectors)
                if connector:
                    sentence = _join_with_connector(out[-1] if out else "", sentence, connector)
                    used_connectors.add(connector)
                    connector_count += 1
        out.append(sentence)
    return out, connector_count


def _merge_sentence(prev: str, nxt: str, *, connector: str | None = None) -> str:
    left = prev.strip()
    if left.endswith("."):
        left = left[:-1]
    right = nxt.strip()
    if connector:
        return f"{left}; {connector} {right}".strip()
    return f"{left}; {right}".strip()


def _merge_adjacent_sentences(
    sentences_with_kind: list[dict[str, str]],
) -> list[dict[str, str]]:
    if not sentences_with_kind:
        return []
    merged: list[dict[str, str]] = []
    for entry in sentences_with_kind:
        if not merged:
            merged.append(entry)
            continue
        merged.append(entry)
    return merged


def _normalize_clause(text: str) -> str:
    return " ".join(str(text or "").split()).strip().rstrip(".")


def _ensure_terminal_punctuation(sentence: str) -> str:
    cleaned = sentence.strip()
    if not cleaned:
        return cleaned
    if cleaned[-1] not in ".!?":
        return f"{cleaned}."
    return cleaned


def _section_entries(core_story_plan: Mapping[str, Any], section_id: str) -> list[Mapping[str, Any]]:
    sections = core_story_plan.get("sections") if isinstance(core_story_plan, Mapping) else None
    if not isinstance(sections, list):
        return []
    for section in sections:
        if not isinstance(section, Mapping):
            continue
        if section.get("section_id") == section_id:
            entries = section.get("sentences")
            if isinstance(entries, list):
                return [entry for entry in entries if isinstance(entry, Mapping)]
    return []


def _slot_texts(
    entries: Sequence[Mapping[str, Any]],
    slot: str,
    frag_index: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    for entry in entries:
        if entry.get("slot") != slot:
            continue
        fragment_id = entry.get("fragment_id")
        if not isinstance(fragment_id, str) or not fragment_id:
            continue
        text = _resolve_fragment_text(fragment_id, frag_index)
        if not text:
            continue
        results.append({"fragment_id": fragment_id, "text": text, "slot": slot})
    return results


def _first_text(entries: Sequence[Mapping[str, str]]) -> Mapping[str, str] | None:
    if not entries:
        return None
    return {
        "fragment_id": entries[0].get("fragment_id", ""),
        "text": entries[0].get("text", ""),
        "slot": entries[0].get("slot", ""),
    }


def _synthesize_paragraph(
    *,
    anchor: Mapping[str, str] | None,
    mechanisms: list[Mapping[str, str]],
    effects: list[Mapping[str, str]],
    potentials: list[Mapping[str, str]],
    shadows: list[Mapping[str, str]],
    extras: list[str] | None = None,
    softener: str | None = None,
    budget_sentences: int = 6,
    max_connectors: int = 1,
) -> dict[str, Any]:
    items: list[dict[str, str]] = []
    used_fragment_ids: list[str] = []
    used_slots: list[str] = []
    shadow_linked = False

    if softener:
        items.append({"kind": "softener", "text": softener})

    if anchor and anchor.get("text"):
        items.append(
            {
                "kind": "anchor",
                "text": anchor.get("text", ""),
                "fragment_id": anchor.get("fragment_id", ""),
                "slot": anchor.get("slot", ""),
            }
        )

    for entry in mechanisms[:2]:
        items.append(
            {
                "kind": "mechanism",
                "text": entry.get("text", ""),
                "fragment_id": entry.get("fragment_id", ""),
                "slot": entry.get("slot", ""),
            }
        )

    for entry in effects[:1]:
        items.append(
            {
                "kind": "effect",
                "text": entry.get("text", ""),
                "fragment_id": entry.get("fragment_id", ""),
                "slot": entry.get("slot", ""),
            }
        )

    for entry in shadows[:1]:
        items.append(
            {
                "kind": "shadow",
                "text": entry.get("text", ""),
                "fragment_id": entry.get("fragment_id", ""),
                "slot": entry.get("slot", ""),
            }
        )

    for entry in potentials[:1]:
        items.append(
            {
                "kind": "potential",
                "text": entry.get("text", ""),
                "fragment_id": entry.get("fragment_id", ""),
                "slot": entry.get("slot", ""),
            }
        )

    if extras:
        for extra in extras:
            if extra:
                items.append({"kind": "extra", "text": extra})

    sentences_with_kind: list[dict[str, str]] = []
    anchor_need = _extract_need((anchor or {}).get("text", "")) or _extract_need(
        (mechanisms[0].get("text", "") if mechanisms else "")
    )
    for item in items:
        raw_text = item.get("text", "")
        if item.get("kind") == "shadow" and raw_text:
            candidates = _wrap_shadow(raw_text)
            shadow_linked = True
        elif item.get("kind") == "shadow":
            candidates = [raw_text] if raw_text else []
        else:
            candidates = _split_sentences(raw_text)[:1]
        for raw_sentence in candidates:
            if item.get("kind") == "shadow":
                normalized = _normalize_clause(raw_sentence)
            else:
                normalized = _normalize_sentence(raw_sentence)
            if normalized:
                role = item.get("slot") or item.get("kind") or ""
                if role == "anchor":
                    role = "cause"
                elif role == "extra":
                    role = "lived_experience"
                role = _resolve_sentence_role(role, normalized)
                sentences_with_kind.append(
                    {
                        "kind": item.get("kind", ""),
                        "sentence": normalized,
                        "fragment_id": item.get("fragment_id", ""),
                        "slot": item.get("slot", ""),
                        "role": role,
                    }
                )

    sentences_with_kind = _dedupe_within_paragraph(sentences_with_kind)
    sentences_with_kind = _merge_adjacent_sentences(sentences_with_kind)

    if budget_sentences < 1:
        budget_sentences = 1
    if len(sentences_with_kind) > budget_sentences:
        drop_order = ["potential", "shadow", "effect", "mechanism", "anchor", "softener"]
        for kind in drop_order:
            if len(sentences_with_kind) <= budget_sentences:
                break
            for idx in range(len(sentences_with_kind) - 1, -1, -1):
                if sentences_with_kind[idx].get("kind") == kind:
                    sentences_with_kind.pop(idx)
                    break
        sentences_with_kind = sentences_with_kind[:budget_sentences]

    sentences, connector_count = _add_connectors_with_cap(sentences_with_kind, max_connectors=max_connectors)
    sentences, _ = _cap_connector_usage(sentences, max_per_paragraph=max_connectors)
    sentences = [_clean_sentence(sentence) for sentence in sentences if sentence]
    sentences = _bridge_inner_outer(sentences)
    sentences = _dedupe_sentences(sentences)
    sentences = [_ensure_terminal_punctuation(sentence) for sentence in sentences if sentence]

    for entry in sentences_with_kind:
        fragment_id = entry.get("fragment_id")
        if fragment_id:
            used_fragment_ids.append(fragment_id)
        slot = entry.get("slot")
        if slot:
            used_slots.append(str(slot))

    text = " ".join(sentences).strip()
    text = _collapse_repeated_leads(text)
    return {
        "text": text,
        "used_fragment_ids": used_fragment_ids,
        "used_slots": sorted(set(used_slots)),
        "sentence_count": len(sentences),
        "connector_count": connector_count,
        "sentences": sentences,
        "shadow_linked": shadow_linked,
        "micro_lived_added": any(item.get("kind") == "extra" for item in items),
    }


def _ensure_min_sentences_payload(
    payload: dict[str, Any],
    phase2_snapshot: Mapping[str, Any],
    *,
    min_count: int = 3,
) -> dict[str, Any]:
    sentences = list(payload.get("sentences") or [])
    if len(sentences) >= min_count:
        payload["sentence_count"] = len(sentences)
        payload["text"] = " ".join(sentences).strip()
        return payload

    accepted = ((phase2_snapshot.get("slots") or {}).get("accepted") or [])
    used_keys = {_sentence_key(s) for s in sentences}
    used_ids = list(payload.get("used_fragment_ids") or [])

    for frag in accepted:
        if len(sentences) >= min_count:
            break
        if not isinstance(frag, Mapping):
            continue
        raw = frag.get("original_text") or frag.get("normalized_text") or ""
        fragment_id = frag.get("fragment_id")
        if not raw:
            continue
        for piece in _split_sentences(raw):
            normalized = _normalize_sentence(piece)
            key = _sentence_key(normalized)
            if not key or key in used_keys:
                continue
            sentences.append(normalized)
            used_keys.add(key)
            if fragment_id:
                used_ids.append(fragment_id)
            break

    sentences, connector_count = _cap_connector_usage(sentences, max_per_paragraph=1)
    payload["sentences"] = sentences
    payload["used_fragment_ids"] = used_ids
    payload["sentence_count"] = len(sentences)
    payload["connector_count"] = connector_count
    payload["text"] = " ".join(sentences).strip()
    return payload


def _extract_need(text: str) -> str:
    cleaned = re.sub(r"[^\w\s]", "", str(text or ""))
    words = [word for word in cleaned.split() if word]
    if not words:
        return ""
    return " ".join(words[:8])


def _link_shadow(need: str, shadow_text: str) -> str:
    base = " ".join(str(shadow_text or "").split()).strip()
    if not base:
        return ""
    lower = base.lower()
    prefix = f"{need} ihtiyacı yükseldiğinde, " if need else ""
    if "bu bir kusur değil" in lower or "bu bir suç değil" in lower:
        return _normalize_sentence(f"{prefix}{base}")
    linked = f"{prefix}{base}"
    if linked[-1] not in ".!?":
        linked += "."
    linked += " Bu bir kusur değil; sistemin yük bindirdiği alan."
    return _normalize_sentence(linked)


def _render_upper_meaning(upper_meaning_selected: Mapping[str, Any] | None) -> str:
    if not upper_meaning_selected:
        return ""
    if isinstance(upper_meaning_selected, Mapping):
        if not upper_meaning_selected.get("enabled", True):
            return ""
        text = upper_meaning_selected.get("text")
        if isinstance(text, str) and text.strip():
            return _normalize_sentence(text)
        mode = str(upper_meaning_selected.get("mode") or "strong").lower()
        if mode == "soft":
            return _normalize_sentence(
                "Bu yapı zamanla seni sadece güçlü bir kimlik kurmaya değil, aynı zamanda başkalarına yön gösteren, anlam ve vizyon taşıyan bir duruş geliştirmeye iter."
            )
        return _normalize_sentence(
            "Bu yapı zamanla seni sadece güçlü bir kimlik kurmaya değil, aynı zamanda başkalarına yön gösteren, anlam ve vizyon taşıyan bir duruş geliştirmeye iter."
        )
    if isinstance(upper_meaning_selected, str) and upper_meaning_selected.strip():
        return _normalize_sentence(upper_meaning_selected)
    return ""


def _render_section_sentences(
    core_story_plan: Mapping[str, Any],
    frag_index: Mapping[str, Mapping[str, Any]],
    *,
    section_id: str,
    used_fingerprints: set[str],
    global_fingerprints: set[str],
    slots: Sequence[str],
    max_sentences: int,
    used_connector: bool,
) -> tuple[list[str], bool]:
    sections = core_story_plan.get("sections") if isinstance(core_story_plan, Mapping) else None
    if not isinstance(sections, list):
        return [], used_connector
    section = next((s for s in sections if isinstance(s, Mapping) and s.get("section_id") == section_id), None)
    if not isinstance(section, Mapping):
        return [], used_connector
    sentence_entries = section.get("sentences")
    if not isinstance(sentence_entries, list):
        return [], used_connector
    rendered: list[str] = []
    for entry in sentence_entries:
        if len(rendered) >= max_sentences:
            break
        if not isinstance(entry, Mapping):
            continue
        if entry.get("slot") not in slots:
            continue
        fragment_id = entry.get("fragment_id")
        if not isinstance(fragment_id, str) or not fragment_id:
            continue
        text = _resolve_fragment_text(fragment_id, frag_index)
        if not text:
            continue
        role = str(entry.get("role") or "explain")
        sentence = _render_role_sentence(text, role)
        fingerprint = _fingerprint_text(sentence)
        if fingerprint in used_fingerprints or fingerprint in global_fingerprints:
            continue
        sentence, used_connector = _apply_connector(sentence, role, used_connector)
        rendered.append(sentence)
        used_fingerprints.add(fingerprint)
        global_fingerprints.add(fingerprint)
    return rendered, used_connector


def _append_unique_sentence(
    sentences: list[str],
    seen: set[str],
    global_seen: set[str],
    sentence: str,
    *,
    role: str,
    used_connector: bool,
) -> bool:
    cleaned = sentence.strip()
    if not cleaned:
        return used_connector
    fingerprint = _fingerprint_text(cleaned)
    if fingerprint in seen or fingerprint in global_seen:
        return used_connector
    prefixed, used_connector = _apply_connector(cleaned, role, used_connector)
    sentences.append(prefixed)
    seen.add(fingerprint)
    global_seen.add(fingerprint)
    return used_connector


def _render_role_sentence(text: str, role: str) -> str:
    templates = {
        "claim": "{text}.",
        "mechanism": "Bunu genelde şöyle yaparsın: {text}",
        "outer": "{text}.",
        "shadow": "{text}.",
        "growth": "{text}.",
        "spine": "{text}.",
        "explain": "{text}.",
    }
    cleaned = text.strip().rstrip(".")
    template = templates.get(role, "{text}.")
    return template.format(text=cleaned)


SLOT_CONNECTORS = {
    "claim": ["Temelde,", "Kökünde,"],
    "mechanism": ["Bunu genelde", "Bu yüzden"],
    "outer": ["Dışarıdan", "İnsanlar seni çoğunlukla"],
    "growth": ["Zamanla", "Doğru kullanınca"],
    "shadow": ["Zorlandığında", "Bazen"],
}


CONNECTOR_TOKENS = [
    "Temelde,",
    "Temelde",
    "Kökünde,",
    "Kökünde",
    "Bunu genelde",
    "Bu yüzden",
    "Dışarıdan",
    "İnsanlar seni çoğunlukla",
    "Zamanla",
    "Zorlandığında",
    "Bazen",
]


def _apply_connector(text: str, role: str, used_connector: bool) -> tuple[str, bool]:
    if not text:
        return text, used_connector
    lowered = text.lower()
    for token in CONNECTOR_TOKENS:
        if lowered.startswith(token.lower()):
            return text, True
    if used_connector:
        return text, True
    options = SLOT_CONNECTORS.get(role)
    if not options:
        return text, used_connector
    connector = options[0]
    if connector.endswith(","):
        return f"{connector} {text}", True
    return f"{connector} {text}", True


def _limit_sentences(sentences: list[str], *, limit: int) -> list[str]:
    if len(sentences) <= limit:
        return sentences
    return sentences[:limit]


def _ensure_spine_fallback(
    sentences: list[str],
    phase2_snapshot: Mapping[str, Any],
    used_fingerprints: set[str],
    global_fingerprints: set[str],
) -> list[str]:
    if sentences:
        return sentences
    accepted = ((phase2_snapshot.get("slots") or {}).get("accepted") or [])
    if not isinstance(accepted, list):
        return sentences
    for frag in accepted:
        if not isinstance(frag, Mapping):
            continue
        text = frag.get("original_text") or frag.get("normalized_text") or ""
        text = str(text).strip()
        if not text:
            continue
        sentence = _render_role_sentence(text, "claim")
        fingerprint = _fingerprint_text(sentence)
        if fingerprint in used_fingerprints or fingerprint in global_fingerprints:
            continue
        used_fingerprints.add(fingerprint)
        global_fingerprints.add(fingerprint)
        return [sentence]
    return sentences


def _ensure_min_sentences_count(
    sentences: list[str],
    phase2_snapshot: Mapping[str, Any],
    used_fingerprints: set[str],
    global_fingerprints: set[str],
    *,
    min_count: int,
) -> list[str]:
    if len(sentences) >= min_count:
        return sentences
    accepted = ((phase2_snapshot.get("slots") or {}).get("accepted") or [])
    if not isinstance(accepted, list):
        return sentences
    ordered = sorted(
        [frag for frag in accepted if isinstance(frag, Mapping)],
        key=lambda frag: (-float(frag.get("salience_score") or 0.0), str(frag.get("fragment_id") or "")),
    )
    for frag in ordered:
        if len(sentences) >= min_count:
            break
        text = frag.get("original_text") or frag.get("normalized_text") or ""
        text = str(text).strip()
        if not text:
            continue
        sentence = _render_role_sentence(text, "claim")
        fingerprint = _fingerprint_text(sentence)
        if fingerprint in used_fingerprints or fingerprint in global_fingerprints:
            continue
        sentences.append(sentence)
        used_fingerprints.add(fingerprint)
        global_fingerprints.add(fingerprint)
    return sentences


def _build_composite_lookup(composite_meanings: Mapping[str, Any] | None) -> dict[tuple[str, str], Mapping[str, Any]]:
    lookup: dict[tuple[str, str], Mapping[str, Any]] = {}
    if not composite_meanings:
        return lookup
    meanings = composite_meanings.get("meanings")
    if not isinstance(meanings, list):
        meanings = composite_meanings.get("selected")
    if not isinstance(meanings, list):
        return lookup
    for entry in meanings:
        if not isinstance(entry, Mapping):
            continue
        meaning_id = entry.get("meaning_id")
        instance_id = entry.get("instance_id")
        if meaning_id and instance_id:
            lookup[(str(meaning_id), str(instance_id))] = entry
    return lookup


def _plan_composite_selected(core_story_plan: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    composite = core_story_plan.get("composite_meanings") if isinstance(core_story_plan, Mapping) else None
    if not isinstance(composite, Mapping):
        return []
    selected = composite.get("selected")
    if not isinstance(selected, list):
        return []
    return [item for item in selected if isinstance(item, Mapping)]


def _insert_composite_headline(
    paragraph: list[str],
    composite_lookup: Mapping[tuple[str, str], Mapping[str, Any]],
    composite_selected: Sequence[Mapping[str, Any]],
    *,
    target_id: str,
    used_fingerprints: set[str],
    position: int,
) -> None:
    for entry in composite_selected:
        if entry.get("meaning_id") != target_id:
            continue
        meaning = composite_lookup.get((str(entry.get("meaning_id")), str(entry.get("instance_id"))))
        if not meaning:
            continue
        headline = ((meaning.get("claim") or {}).get("headline") or "").strip()
        if not headline:
            continue
        fingerprint = _fingerprint_text(headline)
        if fingerprint and fingerprint in used_fingerprints:
            return
        paragraph.insert(max(0, min(position, len(paragraph))), headline)
        if fingerprint:
            used_fingerprints.add(fingerprint)
        return


def _insert_composite_explain(
    paragraph: list[str],
    composite_lookup: Mapping[tuple[str, str], Mapping[str, Any]],
    composite_selected: Sequence[Mapping[str, Any]],
    *,
    target_id: str,
    fallback_id: str | None = None,
    used_fingerprints: set[str],
    position: int,
) -> None:
    target = target_id
    entry = next((item for item in composite_selected if item.get("meaning_id") == target), None)
    if not entry and fallback_id:
        target = fallback_id
        entry = next((item for item in composite_selected if item.get("meaning_id") == target), None)
    if not entry:
        return
    meaning = composite_lookup.get((str(entry.get("meaning_id")), str(entry.get("instance_id"))))
    if not meaning:
        return
    explain = (meaning.get("claim") or {}).get("explain") or []
    if not explain:
        return
    sentence = str(explain[0]).strip()
    if not sentence:
        return
    fingerprint = _fingerprint_text(sentence)
    if fingerprint and fingerprint in used_fingerprints:
        return
    paragraph.insert(max(0, min(position, len(paragraph))), sentence)
    if fingerprint:
        used_fingerprints.add(fingerprint)


def _insert_spines(
    paragraph: list[str],
    core_story_plan: Mapping[str, Any],
    spine_by_id: Mapping[str, Mapping[str, Any]],
    used_insight_ids: set[str],
    used_fingerprints: set[str],
    *,
    target_paragraph: int,
    max_count: int,
) -> list[str]:
    spines = core_story_plan.get("spines") if isinstance(core_story_plan, Mapping) else None
    if not isinstance(spines, list):
        return []
    used: list[str] = []
    for spine in spines:
        if len(paragraph) >= max_count:
            break
        if not isinstance(spine, Mapping):
            continue
        if spine.get("paragraph") != target_paragraph:
            continue
        spine_id = spine.get("spine_id")
        if not spine_id or spine_id in used_insight_ids:
            continue
        spine_entry = spine_by_id.get(str(spine_id))
        if not spine_entry:
            continue
        story = spine_entry.get("story_spine") or {}
        sentences = []
        if target_paragraph == 1:
            if story.get("p1"):
                sentences.append(story.get("p1"))
        elif target_paragraph == 3:
            if story.get("p3"):
                sentences.append(story.get("p3"))
        for sentence in sentences:
            if len(paragraph) >= max_count:
                break
            text = str(sentence).strip()
            if not text:
                continue
            fingerprint = _fingerprint_text(text)
            if fingerprint and fingerprint in used_fingerprints:
                continue
            paragraph.append(text)
            if fingerprint:
                used_fingerprints.add(fingerprint)
            if spine_id not in used:
                used.append(str(spine_id))
        used_insight_ids.add(str(spine_id))
    return used


def _select_spine_links(dynamic_insights: Mapping[str, Any] | None) -> list[Mapping[str, Any]]:
    if not dynamic_insights:
        return []
    links = dynamic_insights.get("links")
    if not isinstance(links, list):
        return []
    return [link for link in links if isinstance(link, Mapping)]


def _insert_link_connector(
    paragraph: list[str],
    links: Sequence[Mapping[str, Any]],
    allowed_types: set[str],
) -> None:
    if not paragraph:
        return
    for link in links:
        link_type = str(link.get("link_type") or "")
        if link_type not in allowed_types:
            continue
        connector = str(link.get("connector_text") or "").strip()
        if not connector:
            continue
        if any(_fingerprint_text(item) == _fingerprint_text(connector) for item in paragraph):
            return
        paragraph.insert(1 if len(paragraph) > 1 else 0, connector)
        return


def _insert_shadow_from_spines(
    paragraph: list[str],
    core_story_plan: Mapping[str, Any],
    spine_by_id: Mapping[str, Mapping[str, Any]],
    *,
    max_count: int,
) -> None:
    if len(paragraph) >= max_count:
        return
    spines = core_story_plan.get("spines") if isinstance(core_story_plan, Mapping) else None
    if not isinstance(spines, list):
        return
    for spine in spines:
        if len(paragraph) >= max_count:
            break
        if not isinstance(spine, Mapping):
            continue
        if spine.get("paragraph") != 3:
            continue
        spine_entry = spine_by_id.get(str(spine.get("spine_id") or ""))
        if not spine_entry:
            continue
        story = spine_entry.get("story_spine") or {}
        shadow = story.get("shadow")
        if not shadow:
            continue
        sentence = f"Golge tarafinda bu, {shadow}."
        fingerprint = _fingerprint_text(sentence)
        if fingerprint and fingerprint in (_fingerprint_text(item) for item in paragraph):
            continue
        paragraph.append(sentence)
        break


def _build_fallback_pool(
    id_to_text: Mapping[str, str],
    used_ids: set[str],
    used_fingerprints: set[str],
) -> list[str]:
    pool: list[str] = []
    for fragment_id in sorted(id_to_text.keys()):
        if fragment_id in used_ids:
            continue
        text = id_to_text.get(fragment_id, "")
        if not text:
            continue
        fingerprint = _fingerprint_text(text)
        if fingerprint and fingerprint in used_fingerprints:
            continue
        pool.append(text)
    return pool


def _normalize_sentence_start(text: str) -> str:
    if not text:
        return text
    replacements = {
        "Iceride ": "İçeride ",
        "Iliskilerde ": "İlişkilerde ",
        "Disaridan ": "Dışarıdan ",
        "bu disaridan": "Bu dışarıdan",
    }
    for prefix, replacement in replacements.items():
        if text.startswith(prefix):
            return replacement + text[len(prefix):]
    return text


def _select_paragraph_fragments_from_plan(
    plan_sections: Mapping[str, Mapping[str, Any]],
    fragment_map: Mapping[str, Mapping[str, Any]],
    *,
    paragraph_index: int,
    min_count: int,
    max_count: int,
) -> list[Mapping[str, Any]]:
    selected: list[Mapping[str, Any]] = []
    if paragraph_index == 0:
        identity = plan_sections.get("inner_core") or {}
        selected = _select_from_plan(identity, fragment_map, ["cause", "mechanism", "potential"])
    elif paragraph_index == 1:
        identity = plan_sections.get("inner_core") or {}
        emotions = plan_sections.get("emotions") or {}
        mind = plan_sections.get("mind") or {}
        selected.extend(_select_from_plan(identity, fragment_map, ["mechanism"]))
        selected.extend(_select_from_plan(emotions, fragment_map, ["cause", "mechanism"], pick_one=True))
        selected.extend(_select_from_plan(mind, fragment_map, ["mechanism"]))
    else:
        identity = plan_sections.get("inner_core") or {}
        relations = plan_sections.get("relationships") or {}
        mind = plan_sections.get("mind") or {}
        selected.extend(_select_from_plan(identity, fragment_map, ["effect"]))
        selected.extend(_select_from_plan(relations, fragment_map, ["effect"], pick_one=True))
        if not selected or len(selected) < 2:
            selected.extend(_select_from_plan(mind, fragment_map, ["effect"], pick_one=True))

    selected = [frag for frag in selected if frag]
    if len(selected) > max_count:
        selected = selected[:max_count]
    if len(selected) < min_count:
        selected = _pad_with_fragment_map(selected, fragment_map, min_count, max_count)
    return selected


def _select_from_plan(
    section: Mapping[str, Any],
    fragment_map: Mapping[str, Mapping[str, Any]],
    slots: Sequence[str],
    *,
    pick_one: bool = False,
) -> list[Mapping[str, Any]]:
    selected: list[Mapping[str, Any]] = []
    section_slots = section.get("slots") if isinstance(section, Mapping) else None
    if not isinstance(section_slots, Mapping):
        return selected
    for slot in slots:
        slot_entry = section_slots.get(slot)
        if not isinstance(slot_entry, Mapping):
            continue
        fragment_id = slot_entry.get("fragment_id")
        fragment = fragment_map.get(str(fragment_id))
        if fragment:
            selected.append(fragment)
            if pick_one:
                break
    return selected


def _pad_with_fragment_map(
    selected: list[Mapping[str, Any]],
    fragment_map: Mapping[str, Mapping[str, Any]],
    min_count: int,
    max_count: int,
) -> list[Mapping[str, Any]]:
    if len(selected) >= min_count:
        return selected
    for fragment in fragment_map.values():
        if fragment in selected:
            continue
        selected.append(fragment)
        if len(selected) >= min_count:
            break
    return selected[:max_count]


def _select_supporting_fact(selected: Sequence[Mapping[str, Any]]) -> Mapping[str, Any] | None:
    for fragment in selected:
        slot = fragment.get("type") or fragment.get("slot")
        supporting = fragment.get("supporting_facts") or []
        if not isinstance(supporting, list):
            continue
        for fact in supporting:
            if not isinstance(fact, Mapping):
                continue
            if fact.get("slot") != slot:
                continue
            return fact
    return None


def _compose_paragraph(
    fragments: Sequence[Mapping[str, Any]],
    supporting: Mapping[str, Any] | None,
    *,
    seed: str,
) -> str:
    connectors = [
        "Bazen",
        "Cogu zaman",
        "Disaridan bakinca",
        "Iceride ise",
        "Yine de",
    ]
    parts: list[str] = []
    for idx, fragment in enumerate(fragments):
        text = _clean_fragment_text(fragment.get("text"))
        if not text:
            continue
        if idx == 0:
            parts.append(text)
        else:
            connector = _stable_pick(seed + str(idx), connectors)
            parts.append(f"{connector} {text}")
    if supporting:
        text = _clean_fragment_text(supporting.get("text"))
        if text:
            parts.append(f"Ayrica {text}")
    paragraph = " ".join(parts).strip()
    return paragraph


def _clean_fragment_text(value: Any) -> str:
    if value is None:
        return ""
    cleaned = " ".join(str(value).strip().split())
    return cleaned.replace("\n", " ")


def _stable_pick(signature: str, variants: Sequence[str]) -> str:
    if not variants:
        return ""
    total = sum(ord(ch) for ch in (signature or "default"))
    return variants[total % len(variants)]
