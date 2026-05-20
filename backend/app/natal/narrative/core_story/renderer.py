from __future__ import annotations

import re
from typing import Any, Dict, Mapping, Sequence

from app.engine.tone_apply import apply_tone
from app.engine.tone_profile import ToneProfile


def render_core_story(
    phase2_snapshot: Mapping[str, Any],
    core_story_plan: Mapping[str, Any],
    tone_profile: Mapping[str, Any] | ToneProfile | None,
    *,
    dynamic_insights: Mapping[str, Any] | None = None,
    composite_meanings: Mapping[str, Any] | None = None,
    upper_meaning_selected: Mapping[str, Any] | None = None,
    debug: bool = False,
    debug_payload: dict[str, Any] | None = None,
) -> str:
    tone = _resolve_tone_profile(tone_profile)
    frag_index = _build_fragment_index(phase2_snapshot)
    meaning_index = _build_meaning_index(composite_meanings)

    paragraph_debug: Dict[str, Any] = {
        "sentence_counts": {},
        "connector_counts": {},
        "used_fragment_ids": {},
        "used_slots": {},
        "shadow_linked": {},
        "micro_lived_added": {},
    }

    headline_text = ""
    master_ref = _headline_ref(core_story_plan)
    if master_ref:
        master = meaning_index.get((master_ref["meaning_id"], master_ref["instance_id"]))
        if master:
            narrative = master.get("narrative") or {}
            headline_text = str(narrative.get("headline") or master.get("headline") or "").strip()

    inner_entries = _section_entries(core_story_plan, "inner_core")
    emotions_entries = _section_entries(core_story_plan, "emotions")
    mind_entries = _section_entries(core_story_plan, "mind")
    relationships_entries = _section_entries(core_story_plan, "relationships")

    global_connector_budget = 2
    p1_payload = _synthesize_paragraph(
        anchor=_first_text(_slot_texts(inner_entries, "cause", frag_index)),
        mechanisms=_slot_texts(inner_entries, "mechanism", frag_index),
        effects=_slot_texts(inner_entries, "effect", frag_index),
        potentials=_slot_texts(inner_entries, "potential", frag_index),
        shadows=_slot_texts(inner_entries, "shadow", frag_index),
        softener=headline_text or None,
        budget_sentences=6,
        max_connectors=1,
    )
    p1_payload = _ensure_min_sentences_payload(p1_payload, phase2_snapshot, min_count=3)
    global_connector_budget = max(0, global_connector_budget - int(p1_payload.get("connector_count") or 0))

    psychology_texts = (
        _slot_texts(emotions_entries, "cause", frag_index)
        + _slot_texts(emotions_entries, "mechanism", frag_index)
        + _slot_texts(emotions_entries, "effect", frag_index)
        + _slot_texts(emotions_entries, "potential", frag_index)
        + _slot_texts(emotions_entries, "shadow", frag_index)
    )
    micro_lived = (
        "Bazen içeride çok şey varken dışarıya daha azı çıkıyor gibi hissediyor olabilirsin."
        if len(psychology_texts) >= 2
        else ""
    )
    p2_payload = _synthesize_paragraph(
        anchor=_first_text(_slot_texts(emotions_entries, "cause", frag_index)),
        mechanisms=_slot_texts(emotions_entries, "mechanism", frag_index)
        + _slot_texts(mind_entries, "mechanism", frag_index),
        effects=_slot_texts(emotions_entries, "effect", frag_index) or _slot_texts(mind_entries, "effect", frag_index),
        potentials=_slot_texts(emotions_entries, "potential", frag_index),
        shadows=_slot_texts(emotions_entries, "shadow", frag_index),
        extras=[micro_lived] if micro_lived else None,
        softener=None,
        budget_sentences=6,
        max_connectors=1 if global_connector_budget > 0 else 0,
    )
    p2_payload = _ensure_min_sentences_payload(p2_payload, phase2_snapshot, min_count=3)
    global_connector_budget = max(0, global_connector_budget - int(p2_payload.get("connector_count") or 0))

    p3_payload = _synthesize_paragraph(
        anchor=_first_text(_slot_texts(relationships_entries, "cause", frag_index)),
        mechanisms=_slot_texts(relationships_entries, "mechanism", frag_index),
        effects=_slot_texts(relationships_entries, "effect", frag_index)
        + _slot_texts(inner_entries, "effect", frag_index),
        potentials=_slot_texts(relationships_entries, "potential", frag_index),
        shadows=_slot_texts(relationships_entries, "shadow", frag_index),
        softener=None,
        budget_sentences=6,
        max_connectors=1 if global_connector_budget > 0 else 0,
    )
    p3_payload = _ensure_min_sentences_payload(p3_payload, phase2_snapshot, min_count=3)

    paragraphs = []
    for label, payload in (("p1", p1_payload), ("p2", p2_payload), ("p3", p3_payload)):
        sentences = list(payload.get("sentences") or [])
        if sentences and len(sentences) < 2:
            accepted = ((phase2_snapshot.get("slots") or {}).get("accepted") or [])
            used_keys = {_sentence_key(sentence) for sentence in sentences}
            if isinstance(accepted, list):
                for frag in accepted:
                    if len(sentences) >= 2:
                        break
                    if not isinstance(frag, Mapping):
                        continue
                    raw = frag.get("original_text") or frag.get("normalized_text") or ""
                    if not raw:
                        continue
                    for piece in _split_sentences(raw):
                        normalized = _normalize_sentence(piece)
                        key = _sentence_key(normalized)
                        if not key or key in used_keys:
                            continue
                        sentences.append(normalized)
                        used_keys.add(key)
                        break
            payload["sentences"] = sentences
            payload["sentence_count"] = len(sentences)
            payload["text"] = " ".join(sentences).strip()
        if debug_payload is not None:
            paragraph_debug["sentence_counts"][label] = payload.get("sentence_count", 0)
            paragraph_debug["connector_counts"][label] = payload.get("connector_count", 0)
            paragraph_debug["used_fragment_ids"][label] = payload.get("used_fragment_ids", [])
            paragraph_debug["used_slots"][label] = payload.get("used_slots", [])
            paragraph_debug["shadow_linked"][label] = payload.get("shadow_linked", False)
            paragraph_debug["micro_lived_added"][label] = payload.get("micro_lived_added", False)
        text = payload.get("text") or ""
        if text:
            text = _collapse_repeated_leads(text)
            text = _polish_core_story_paragraph(text)
            payload["text"] = text
        if text:
            paragraphs.append(text)

    upper_paragraph = _render_upper_meaning(upper_meaning_selected)
    if upper_paragraph and paragraphs:
        paragraphs[-1] = _collapse_repeated_leads(_normalize_sentence(f"{paragraphs[-1]} {upper_paragraph}"))
    elif upper_paragraph:
        paragraphs.append(upper_paragraph)

    if not paragraphs:
        fallback: list[str] = []
        accepted = ((phase2_snapshot.get("slots") or {}).get("accepted") or [])
        for frag in accepted[:3]:
            if not isinstance(frag, Mapping):
                continue
            t = frag.get("original_text") or frag.get("normalized_text") or ""
            t = str(t).strip()
            if t:
                fallback.append(_normalize_sentence(t))
        paragraphs = [p for p in fallback if p]

    paragraphs = [_polish_core_story_paragraph(_apply_tone_safe(p, tone, "core_story")) for p in paragraphs if p]
    text = "\n\n".join([para.strip() for para in paragraphs if para and para.strip()])

    if debug_payload is not None:
        paragraph_debug["upper_meaning"] = {"included": bool(upper_paragraph)}
        debug_payload["core_story_synthesis"] = {
            "p1": {
                "used_slots": paragraph_debug["used_slots"].get("p1", []),
                "shadow_linked": paragraph_debug["shadow_linked"].get("p1", False),
            },
            "p2": {
                "micro_lived_added": paragraph_debug["micro_lived_added"].get("p2", False),
            },
            "upper_meaning": {"included": bool(upper_paragraph)},
        }
    elif debug:
        print("DEBUG core_story:", paragraph_debug)
    return text


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
    _ = anchor_need
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
