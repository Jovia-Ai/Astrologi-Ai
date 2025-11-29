"""Narrative formatting helpers for interpretations and cards."""
from __future__ import annotations

import re
from typing import Any, Dict, Iterable, Mapping, Sequence

from app.ai.archetypes.analyzer import clean_text, limit_sentences, map_confidence_label, translate_keyword

DEFAULT_REASON_FALLBACKS = [
    "İç sesini duymak, dış dünyada kurduğun yapıya sıcaklık katıyor.",
    "Duygularını sorumluluklarınla dengelemek olgunlaşma alanın.",
    "Anlam arayışını paylaşmak çevrende güven köprüleri kuruyor.",
]

DEFAULT_ACTION_FALLBACKS = [
    "Her gün 5 dakikalık nefesle bedeni ve zihni hizala.",
    "Haftada bir sezgisel yazı çalışmasıyla hislerini isimlendir.",
    "Akşamları günü üç maddede yeniden çerçevele.",
]

ELEMENT_STORIES = {
    "Ateş": "Ateş vurgusu içindeki cesur kıvılcımı diri tutuyor; hızlanmadan önce kalbinin ritmini dinlemek sana iyi geliyor.",
    "Toprak": "Toprak baskınlığı güveni yavaş ve somut adımlarla kurduğunu, sabrın seni ayakta tuttuğunu fısıldıyor.",
    "Hava": "Hava elementinin yoğunluğu zihnini sürekli harekette tutuyor; ilişkileri anlamak için sözcüklerden nefes alıyorsun.",
    "Su": "Su enerjisi duygularını derinleştiriyor; sezgilerini saklamak yerine paylaşmak seni rahatlatıyor.",
}

ELEMENT_ACTIONS = {
    "Ateş": "Enerjini yakmadan önce nefesinle merkezlen; öfke yerine cesaretle konuş.",
    "Toprak": "Gününe kısa beden egzersizleri ekle; esnekliği bedende kurduğunda zihin de yumuşuyor.",
    "Hava": "Düşüncelerini tek cümlelik niyetlere indir; zihinsel rüzgarın yönünü sen belirlersin.",
    "Su": "Her gün duygularını yazıya dök; adını koyduğun duygu hafifler.",
}

MODALITY_STORIES = {
    "Öncü": "Öncü enerji seni yeni sayfalar açmaya iter; acele etmeden liderlik etmek gücünü berraklaştırıyor.",
    "Sabit": "Sabit modalite kararlılığını güçlendiriyor; yumuşak bir esneme alanı açtığında iç huzurun artıyor.",
    "Değişken": "Değişken enerji sana esneklik veriyor; kararlarını küçük ritüellerle sabitleyince dağılmıyorsun.",
}

PLANET_STORIES = {
    "Sun": "Güneş ışığın kim olduğunun farkındalığını canlı tutuyor.",
    "Moon": "Ay duygularını dalgalandırırken içsel güven alanını hatırlatıyor.",
    "Mercury": "Merkür vurgusu zihnini hızlı çalıştırıyor; ifadeni yavaşlatınca daha çok anlaşılıyorsun.",
    "Venus": "Venüs enerjisi ilişkilerde sıcaklık ve estetik ihtiyacını büyütüyor.",
    "Mars": "Mars harekete geçirme gücünü ateşliyor; öfkeyi cesarete dönüştürebilirsin.",
    "Jupiter": "Jüpiter vurgusu büyüme ve anlam arayışını güçlendiriyor.",
    "Saturn": "Satürn tonu sorumluluk ve sınır koyma becerini olgunlaştırıyor.",
    "Uranus": "Uranüs etkisi içindeki özgürlük kıvılcımını ateşliyor; sıradışı yollar seni çağırıyor.",
    "Neptune": "Neptün vurgusu sezgisel hayal gücünü büyütüyor; sınırlar bulanıklaştığında kendine dön.",
    "Pluto": "Plüton etkisi dönüşümü derinlerden başlatıyor; yüzleştiğinde güçleniyorsun.",
}

POLAR_AXIS_STORIES = {
    "Koç–Terazi": "Koç–Terazi ekseni benliğin ile ilişkilerin arasında denge kurma çağrısı yapıyor.",
    "Boğa–Akrep": "Boğa–Akrep hattı güven ve teslimiyet derslerini derinleştiriyor.",
    "İkizler–Yay": "İkizler–Yay aksı merakla anlam arayışı arasında köprü kuruyor.",
    "Yengeç–Oğlak": "Yengeç–Oğlak hattı şefkati sorumlulukla birleştirmeni istiyor.",
    "Aslan–Kova": "Aslan–Kova ekseni bireysel yaratıcılığını kolektif faydayla harmanlıyor.",
    "Başak–Balık": "Başak–Balık hattı kusursuzluk arayışıyla teslimiyet arasında denge kurmana yardım ediyor.",
}

ENERGY_PATTERN_STORIES = {
    "Splay": "Splay düzeni enerjini farklı alanlara yaydığını gösteriyor; merkezini sık sık hatırlamak iyi geliyor.",
    "Bundle": "Bundle deseni içsel odağının yoğun olduğunu söylüyor; molalarla nefes almayı unutma.",
    "Bowl": "Bowl dağılımı enerjinin belirli bir yaşam alanında toplandığını hatırlatıyor; eksik kalan alanları besle.",
    "Locomotive": "Locomotive deseni hedeflerine doğru kararlı ilerleyişini simgeliyor.",
    "Splash": "Splash deseni seni çok yönlü kılıyor; önceliklerini belirlemek esenliğini arttırır.",
}

ENERGY_PATTERN_ACTIONS = {
    "Splay": "Günlük programına iki kez nefes molası ekleyip bedenini dinle.",
    "Bundle": "Kısa yürüyüşlerle enerjini dağıt; tek bir alana sıkışmaktan çık.",
    "Bowl": "Eksik kalan alanlara küçük adımlar atarak iç dengenin genişlemesine izin ver.",
    "Locomotive": "Hedeflerine giderken kalbini dinle; hızını kalbin belirlesin.",
    "Splash": "Her sabah üç öncelik belirleyip günün akışına niyet koy.",
}

LABEL_PREFIX_PATTERN = re.compile(r"^(?:[\s•·\-–—]*)\b(headline|summary|advice|challenge|struggle|gift|strength|lesson|shadow|insight|focus|theme|themes|story)\b[:\-–—]?\s*", re.IGNORECASE)
SUMMARY_LABEL_PATTERN = re.compile(r"^(?P<label>[A-Za-zÇĞİÖŞÜçğıöşü\s]{2,24})[:\-–—]\s*(?P<body>.+)$")
SUMMARY_LABEL_MAP = {
    "challenge": "Meydan okuman",
    "struggle": "Zorlandığın alan",
    "gift": "Doğuştan ışığın",
    "strength": "Dayandığın güç",
    "lesson": "Öğrenme alanın",
    "shadow": "Gölgede kalan yönün",
}


def strip_label_prefix(text: Any) -> str:
    if not isinstance(text, str):
        return ""
    cleaned = LABEL_PREFIX_PATTERN.sub("", text or "").strip()
    cleaned = re.sub(r"^[•·\-\u2022]+\s*", "", cleaned)
    return cleaned.strip()


def flatten_summary_text(text: Any, *, joiner: str = " ") -> str:
    if not isinstance(text, str):
        return ""
    segments: list[str] = []
    for raw_line in re.split(r"[\n•\u2022]+", text):
        line = raw_line.strip()
        if not line:
            continue
        match = SUMMARY_LABEL_PATTERN.match(line)
        if match:
            label = match.group("label").strip().lower()
            body = match.group("body").strip()
            if not body:
                continue
            if label in {"headline", "summary", "advice"}:
                segments.append(body)
                continue
            prefix = SUMMARY_LABEL_MAP.get(label, "")
            if prefix:
                segments.append(f"{prefix}: {body}")
            else:
                segments.append(body)
        else:
            segments.append(line)

    if not segments:
        return clean_text(strip_label_prefix(text))

    combined = joiner.join(segments).strip()
    combined = re.sub(r"\s{2,}", " ", combined)
    return clean_text(combined)


def first_sentences(text: str, limit: int = 2) -> str:
    if not text:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    if len(sentences) <= limit:
        return text.strip()
    return " ".join(sentences[:limit]).strip()


def _dominant_from_balance(balance: Mapping[str, Any] | None) -> tuple[str, float] | None:
    if not isinstance(balance, Mapping):
        return None
    scores: Dict[str, float] = {}
    for key, value in balance.items():
        try:
            scores[key] = float(value)
        except (TypeError, ValueError):
            continue
    if not scores:
        return None
    dominant = max(scores, key=scores.get)
    return dominant, scores[dominant]


def _summarise_element_balance(balance: Mapping[str, Any] | None) -> str:
    dominant = _dominant_from_balance(balance)
    if not dominant:
        return ""
    element, ratio = dominant
    if ratio < 0.35:
        return "Element dengesi birbirine yakın; farklı ruh hallerini esnekçe taşıyorsun."
    return ELEMENT_STORIES.get(element, "")


def _summarise_modality_balance(balance: Mapping[str, Any] | None) -> str:
    dominant = _dominant_from_balance(balance)
    if not dominant:
        return ""
    modality, ratio = dominant
    if ratio < 0.35:
        return "Modaliteler dengeli; değişen koşullara uyumlanırken merkezini koruyorsun."
    return MODALITY_STORIES.get(modality, "")


def _summarise_dominant_planet(name: str | None) -> str:
    if not isinstance(name, str) or not name.strip():
        return ""
    planet = name.strip()
    return PLANET_STORIES.get(planet, f"Baskın enerji {planet} tonundan akıyor; bu ses seni yönlendiriyor.")


def _summarise_polar_axis(axis_label: str | None) -> str:
    if not axis_label:
        return ""
    return POLAR_AXIS_STORIES.get(axis_label, "")


def _summarise_energy_pattern(pattern: str | None) -> str:
    if not pattern:
        return ""
    return ENERGY_PATTERN_STORIES.get(pattern, "")


def _action_from_energy(pattern: str | None) -> str:
    if not pattern:
        return ""
    return ENERGY_PATTERN_ACTIONS.get(pattern, "")


def _action_from_element(balance: Mapping[str, Any] | None) -> str:
    dominant = _dominant_from_balance(balance)
    if not dominant:
        return ""
    element = dominant[0]
    return ELEMENT_ACTIONS.get(element, "")


def _format_title(title: str | None) -> str:
    cleaned = clean_text(title)
    return cleaned or "Kozmik Yorum"


def _prepare_reasons(
    reasons: Iterable[str] | None,
    fallback_tags: Iterable[str] | None = None,
) -> list[str]:
    prepared: list[str] = []
    seen: set[str] = set()

    def _append(sentence: str) -> None:
        text = clean_text(strip_label_prefix(sentence))
        if not text:
            return
        if not text.endswith("."):
            text += "."
        if text not in seen:
            seen.add(text)
            prepared.append(text)

    for item in reasons or []:
        _append(item)
        if len(prepared) >= 4:
            break

    for tag in fallback_tags or []:
        if len(prepared) >= 4:
            break
        tag_text = clean_text(tag)
        translated = translate_keyword(tag_text)
        if not translated:
            continue
        template = f"Tema: {translated} enerjisini bilinçli yönettiğinde dengede kalırsın."
        _append(template)

    idx = 0
    while len(prepared) < 2 and idx < len(DEFAULT_REASON_FALLBACKS):
        _append(DEFAULT_REASON_FALLBACKS[idx])
        idx += 1

    if len(prepared) < 2:
        while len(prepared) < 2:
            _append("İçsel ritmini duyduğunda adımların hafifler.")

    return prepared[:4]


def _prepare_actions(actions: Iterable[str] | None) -> list[str]:
    prepared: list[str] = []
    seen: set[str] = set()

    def _append(sentence: str) -> None:
        text = clean_text(strip_label_prefix(sentence))
        if not text:
            return
        text = text[0].upper() + text[1:] if text else text
        if not text.endswith("."):
            text += "."
        if text not in seen:
            seen.add(text)
            prepared.append(text)

    for item in actions or []:
        _append(item)
        if len(prepared) >= 2:
            break

    idx = 0
    while len(prepared) < 1 and idx < len(DEFAULT_ACTION_FALLBACKS):
        _append(DEFAULT_ACTION_FALLBACKS[idx])
        idx += 1

    idx = 0
    while len(prepared) < 2 and idx < len(DEFAULT_ACTION_FALLBACKS):
        _append(DEFAULT_ACTION_FALLBACKS[idx])
        idx += 1

    return prepared[:2]


def _prepare_tags(tags: Iterable[str] | None) -> list[str]:
    cleaned_tags: list[str] = []
    seen: set[str] = set()
    for tag in tags or []:
        text = translate_keyword(clean_text(tag))
        if not text:
            continue
        if text not in seen:
            seen.add(text)
            cleaned_tags.append(text)
        if len(cleaned_tags) >= 6:
            break
    return cleaned_tags


def build_card_payload(
    *,
    title: str,
    main: str,
    reasons: Iterable[str] | None = None,
    actions: Iterable[str] | None = None,
    tags: Iterable[str] | None = None,
    confidence: Any = None,
) -> Dict[str, Any]:
    narrative_text = limit_sentences(main, min_sentences=3, max_sentences=6) if main else ""
    fragments = [
        fragment.strip()
        for fragment in re.split(r"(?<=[.!?])\s+", narrative_text)
        if fragment.strip()
    ]
    filler_idx = 0
    while len(fragments) < 3 and filler_idx < len(DEFAULT_REASON_FALLBACKS):
        filler_sentence = clean_text(DEFAULT_REASON_FALLBACKS[filler_idx])
        if filler_sentence:
            fragments.append(filler_sentence)
        filler_idx += 1
    if fragments:
        narrative_text = " ".join(fragments[:6]).rstrip(".!?")
        if narrative_text:
            narrative_text += "."

    prepared_tags = _prepare_tags(tags)

    card = {
        "title": _format_title(title),
        "narrative": {
            "main": narrative_text,
        },
        "reasons": {
            "psychology": _prepare_reasons(reasons, prepared_tags),
        },
        "actions": _prepare_actions(actions),
        "tags": prepared_tags,
    }
    confidence_label = map_confidence_label(confidence)
    if confidence_label:
        card["confidence_label"] = confidence_label
    return card


def build_life_card(
    ai_payload: Mapping[str, Any] | None,
    life_narrative: Mapping[str, Any] | None,
    archetype: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    ai_payload = ai_payload or {}
    life_narrative = life_narrative or {}
    archetype = archetype or {}

    title = ai_payload.get("headline") or "Hayat Anlatısı"
    correlations = (
        life_narrative.get("correlations")
        or archetype.get("correlations")
        or {}
    )

    primary_texts = [
        life_narrative.get("text"),
        ai_payload.get("summary"),
        archetype.get("life_expression"),
    ]
    sentences: list[str] = []
    for block in primary_texts:
        cleaned_block = clean_text(strip_label_prefix(block))
        if not cleaned_block:
            continue
        for piece in re.split(r"(?<=[.!?])\s+", cleaned_block):
            piece_clean = clean_text(piece)
            if piece_clean and piece_clean not in sentences:
                sentences.append(piece_clean)
    if len(sentences) < 3:
        sentences.extend(DEFAULT_REASON_FALLBACKS)
    main_text = " ".join(sentences[:6])

    enrichment_sentences: list[str] = []
    if correlations:
        elem_sentence = _summarise_element_balance(correlations.get("element_balance"))
        mod_sentence = _summarise_modality_balance(correlations.get("modality_balance"))
        planet_sentence = _summarise_dominant_planet(correlations.get("dominant_planet"))
        polar_sentence = _summarise_polar_axis(correlations.get("polar_axis"))
        energy_sentence = _summarise_energy_pattern(correlations.get("dominant_cluster"))
        for sentence in (elem_sentence, mod_sentence, planet_sentence, polar_sentence, energy_sentence):
            if sentence:
                enrichment_sentences.append(sentence)
        if enrichment_sentences:
            main_text = f"{main_text.strip()} {' '.join(enrichment_sentences)}".strip()

    reasons: list[str] = []
    axis = life_narrative.get("axis")
    focus = life_narrative.get("focus")
    if axis:
        reasons.append(f"Eksen: {axis} hattı kişisel derslerini belirliyor.")
    if focus:
        reasons.append(f"Odak: {focus}.")
    derived = life_narrative.get("derived_from")
    if isinstance(derived, Sequence):
        for item in derived[:3]:
            if isinstance(item, Mapping):
                pair = item.get("pair")
                aspect = item.get("aspect")
                orb = item.get("orb")
                if pair and aspect:
                    text = f"{pair} • {aspect}"
                    if isinstance(orb, (int, float)):
                        text += f" • orb {orb}°"
                    reasons.append(text)
    themes = life_narrative.get("themes")
    if correlations:
        correlation_reasons = [
            _summarise_element_balance(correlations.get("element_balance")),
            _summarise_modality_balance(correlations.get("modality_balance")),
            _summarise_dominant_planet(correlations.get("dominant_planet")),
            _summarise_polar_axis(correlations.get("polar_axis")),
            _summarise_energy_pattern(correlations.get("dominant_cluster")),
        ]
        reasons.extend(sentence for sentence in correlation_reasons if sentence)
    if not reasons and isinstance(themes, Sequence):
        reasons.extend(f"Tema: {theme}" for theme in themes[:3] if isinstance(theme, str))

    actions: list[str] = []
    advice = ai_payload.get("advice")
    if isinstance(advice, str) and advice.strip():
        actions.append(advice)
    life_focus = archetype.get("life_focus")
    if isinstance(life_focus, str) and life_focus.strip():
        actions.append(f"Odaklan: {life_focus.strip()}")
    if correlations:
        elem_action = _action_from_element(correlations.get("element_balance"))
        energy_action = _action_from_energy(correlations.get("dominant_cluster"))
        for act in (elem_action, energy_action):
            if act:
                actions.append(act)

    tags = []
    if isinstance(themes, Sequence):
        tags.extend(theme for theme in themes if isinstance(theme, str))
    if not tags and isinstance(archetype.get("core_themes"), Sequence):
        tags.extend(theme for theme in archetype["core_themes"] if isinstance(theme, str))

    return build_card_payload(
        title=title,
        main=main_text,
        reasons=reasons,
        actions=actions,
        tags=tags,
        confidence=life_narrative.get("confidence"),
    )


def build_category_card(
    category: Mapping[str, Any] | None,
    *,
    default_title: str,
    fallback_themes: Iterable[str] | None = None,
    extra_reasons: Iterable[str] | None = None,
    extra_actions: Iterable[str] | None = None,
    confidence: Any = None,
) -> Dict[str, Any] | None:
    if not isinstance(category, Mapping):
        return None
    title = category.get("headline") or default_title
    summary = category.get("summary") or ""
    themes = category.get("themes") or fallback_themes or []

    reasons = list(extra_reasons or [])
    tag_sources = []
    if isinstance(themes, Sequence):
        tag_sources.extend(theme for theme in themes if isinstance(theme, str))

    actions = list(extra_actions or [])
    advice = category.get("advice")
    if isinstance(advice, str) and advice.strip():
        actions.append(advice)

    return build_card_payload(
        title=title,
        main=summary,
        reasons=reasons,
        actions=actions,
        tags=tag_sources or themes,
        confidence=confidence,
    )


def build_shadow_card(
    category: Mapping[str, Any] | None,
    behavior_patterns: Iterable[Mapping[str, Any]] | None,
) -> Dict[str, Any] | None:
    extra_reasons = []
    extra_tags = []
    if behavior_patterns:
        for pattern in list(behavior_patterns)[:3]:
            if isinstance(pattern, Mapping):
                label = pattern.get("pattern")
                expression = pattern.get("expression")
                if label and expression:
                    extra_reasons.append(f"{label}: {expression}")
                    extra_tags.append(label)
    card = build_category_card(
        category,
        default_title="Gölge Çalışması",
        fallback_themes=[pattern for pattern in extra_tags],
        extra_reasons=extra_reasons,
    )
    if card is None and extra_reasons:
        card = build_card_payload(
            title="Gölgeler",
            main="Gölgede kalan kalıpları sevgiyle tanımak dönüşümü başlatır.",
            reasons=extra_reasons,
            actions=[],
            tags=extra_tags,
        )
    elif card is not None:
        tags = card.get("tags") or []
        card["tags"] = list({*tags, *extra_tags})[:6]
    return card


def normalize_ai_payload(value: Any) -> Dict[str, str]:
    fallback = {
        "headline": "Interpretation unavailable",
        "summary": "We could not generate a full interpretation at this time.",
        "advice": "Stay grounded and patient; your insight is unfolding.",
    }
    if isinstance(value, Mapping):
        if all(key in value for key in ("headline", "summary", "advice")):
            result = {
                "headline": clean_text(strip_label_prefix(value.get("headline") or fallback["headline"]))
                or fallback["headline"],
                "summary": flatten_summary_text(value.get("summary") or fallback["summary"]) or fallback["summary"],
                "advice": clean_text(strip_label_prefix(value.get("advice") or fallback["advice"])) or fallback["advice"],
            }
            return result
        inner = value.get("ai_interpretation")
        if isinstance(inner, Mapping):
            return normalize_ai_payload(inner)
    return {
        "headline": fallback["headline"],
        "summary": fallback["summary"],
        "advice": fallback["advice"],
    }


def fallback_life_story(meta: Mapping[str, Any]) -> Dict[str, Any]:
    """Produce a deterministic, style-compliant payload if Groq fails."""

    summary = (
        "İç sesin zaman zaman dalgalansa da kalbinde taşıdığın sıcaklık seni koruyor. "
        "Kendini anlatmak istediğinde kelimelerin çoğalsa da asıl ihtiyacın anlaşılmak oluyor. "
        "Nefesini yavaşlattığında zihnin berraklaşıyor ve duyguların sadeleşiyor."
    )

    focus_value = meta.get("focus")
    reasons = [
        "Anlaşılmak senin için güven hissi yaratıyor; paylaştıkça omuzların gevşiyor.",
        "Yoğun duygularını saklamak yerine onları isimlendirdiğinde iç baskı azalıyor.",
    ]
    if isinstance(focus_value, str) and focus_value.strip():
        reasons.append("İlginin yöneldiği alan seni daha dürüst ve sıcak ifadeye çağırıyor.")
    reasons = reasons[:4]

    actions = [
        "Dinle ve gün içinde tek bir duygunu kısa bir cümleyle yaz.",
        "Yaz ve akşam kendine sakinleştirici bir not bırak.",
    ]

    defaults = ["denge", "ifade", "farkındalık", "istikrar"]
    raw_themes = []
    if isinstance(meta, Mapping):
        for item in meta.get("themes") or []:
            if isinstance(item, str):
                candidate = clean_text(item).lower()
                candidate = re.sub(r"[^a-zçğıöşüİĞÜŞÖÇ\s]", "", candidate).strip()
                if candidate and candidate not in raw_themes:
                    raw_themes.append(candidate)
    for word in defaults:
        if len(raw_themes) >= 4:
            break
        if word not in raw_themes:
            raw_themes.append(word)

    return {
        "headline": "İç Sesinin İzinde",
        "summary": summary,
        "reasons": reasons,
        "actions": actions,
        "themes": raw_themes[:4],
    }


def build_interpretation_categories(
    archetype: Mapping[str, Any],
    ai_output: Mapping[str, str],
) -> Dict[str, Dict[str, Any]]:
    def clean_list(items: Iterable[Any]) -> list[str]:
        cleaned = []
        for item in items or []:
            if isinstance(item, str):
                text = item.strip()
                if text:
                    cleaned.append(text)
        return cleaned

    def make_card(headline: str, summary: str, advice: str, themes: Iterable[str]) -> Dict[str, Any]:
        return {
            "headline": headline.strip() or ai_output.get("headline"),
            "summary": summary.strip() or ai_output.get("summary"),
            "advice": advice.strip() or ai_output.get("advice"),
            "themes": clean_list(themes),
        }

    themes = clean_list(archetype.get("core_themes"))
    tone = str(archetype.get("story_tone") or "").strip()
    life_focus = str(archetype.get("life_focus") or "").strip()
    life_expression = strip_label_prefix(archetype.get("life_expression") or "")
    dominant_axis = str(archetype.get("dominant_axis") or "").strip()
    behavior_patterns = archetype.get("behavior_patterns") or []

    summary_text = ai_output.get("summary", "")
    primary_summary = first_sentences(summary_text, 2)

    love_card = make_card(
        ai_output.get("headline") or "Kalbin Kimyası",
        primary_summary or life_expression or summary_text,
        ai_output.get("advice") or "Kalbini sezgilerinle hizala.",
        themes[:3],
    )

    career_summary_parts = []
    if life_focus:
        career_summary_parts.append(life_focus.capitalize())
    if tone:
        career_summary_parts.append(f"{tone} bir yaklaşımla ilerliyorsun.")
    if not career_summary_parts:
        career_summary_parts.append("Enerjini anlamlı bir amaca yönlendiriyorsun.")
    career_card = make_card(
        "İş & Misyon",
        " ".join(career_summary_parts),
        "Somut hedeflerini ruhunun ritmiyle hizala.",
        themes[3:6] or themes[:3],
    )

    spiritual_card = make_card(
        "Ruhsal Akış",
        first_sentences(life_expression or summary_text, 3),
        "Ruhunun fısıltılarını her günkü ritüellerine davet et.",
        clean_list([tone, dominant_axis]) or themes[1:4],
    )

    pattern_lines = []
    pattern_names = []
    for item in behavior_patterns[:2]:
        if isinstance(item, Mapping):
            pattern = str(item.get("pattern") or "").strip()
            expression = str(item.get("expression") or "").strip()
            if pattern:
                pattern_names.append(pattern)
            if pattern and expression:
                pattern_lines.append(f"{pattern}: {expression}")
    shadow_summary = " • ".join(pattern_lines) or "Gölgelerini kabullenmek, potansiyelini özgürleştiriyor."
    shadow_card = make_card(
        "Shadow Work",
        shadow_summary,
        "Karanlık noktalarına da sevgiyle dokun.",
        pattern_names or themes[-3:] or themes[:3],
    )

    return {
        "love": love_card,
        "career": career_card,
        "spiritual": spiritual_card,
        "shadow": shadow_card,
    }
