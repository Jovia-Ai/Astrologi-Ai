from __future__ import annotations

import hashlib
from typing import Any, Dict, Iterable, List, Mapping, Sequence

_DOMAIN_THEME_STEMS = {
    "identity": "self_expression",
    "money": "value_stability",
    "mind": "communication_clarity",
    "home": "inner_foundation",
    "body": "rhythm_regulation",
    "relationships": "relationship_balance",
    "career": "direction_visibility",
    "inner": "control_release",
    "general": "daily_recalibration",
}

_DOMAIN_LABELS_TR = {
    "identity": "kendini ortaya koyma biçimin",
    "money": "değer ve güvenlik tarafın",
    "mind": "zihin ve ifade biçimin",
    "home": "iç güven ve aitlik tarafın",
    "body": "ritim ve beden tarafın",
    "relationships": "yakınlık ve ilişki refleksin",
    "career": "yön ve görünürlük tarafın",
    "inner": "kontrol ve iç dünya tarafın",
    "general": "günü taşıma biçimin",
}

_DOMAIN_DESCRIPTION_TR = {
    "identity": "Bugünün ağırlığı kendini ortaya koyma biçimine düşüyor.",
    "money": "Bugünün ağırlığı değer, güvenlik ve denge hissine düşüyor.",
    "mind": "Bugünün ağırlığı ifade, netlik ve zihinsel akış tarafına düşüyor.",
    "home": "Bugünün ağırlığı iç güven ve aidiyet tarafına düşüyor.",
    "body": "Bugünün ağırlığı ritim, tempo ve beden tarafına düşüyor.",
    "relationships": "Bugünün ağırlığı yakınlık, mesafe ve karşı tarafla kurduğun dengeye düşüyor.",
    "career": "Bugünün ağırlığı yön, görünürlük ve sorumluluk tarafına düşüyor.",
    "inner": "Bugünün ağırlığı kontrol, güven ve içerde tuttuğun şeye düşüyor.",
    "general": "Bugünün ağırlığı genel akışın içinde bir ayar istiyor.",
}

_DOMAIN_BY_HOUSE = {
    1: "identity",
    2: "money",
    3: "mind",
    4: "home",
    5: "identity",
    6: "body",
    7: "relationships",
    8: "inner",
    9: "mind",
    10: "career",
    11: "career",
    12: "inner",
}

_MODE_SUFFIX = {
    "friction": "tension",
    "polarity": "tension",
    "concentration": "focus",
    "flow": "opening",
    "opening": "opening",
    "mixed": "activation",
}

_MODE_DESCRIPTION_TR = {
    "friction": "Bu tema bugün biraz sürtünmeyle açılıyor.",
    "polarity": "Bu tema bugün iki ayrı ihtiyacı aynı anda konuşturuyor.",
    "concentration": "Bu tema bugün tek bir noktada yoğunlaşıyor.",
    "flow": "Bu tema bugün daha akışkan bir kapıdan geliyor.",
    "opening": "Bu tema bugün küçük ama net bir açıklık yaratıyor.",
    "mixed": "Bu tema bugün birden fazla yerden aynı anda kıpırdıyor.",
}

_POINT_FOCUS_TR = {
    "sun": "kimliğin ve görünür duruşun",
    "moon": "duygusal ritmin",
    "mercury": "düşünme ve konuşma biçimin",
    "venus": "yakınlık ve beğeni ölçün",
    "mars": "tepki hızın",
    "jupiter": "büyütme eğilimin",
    "saturn": "sorumluluk eşiğin",
    "uranus": "ani kopuş refleksin",
    "neptune": "sınırlarının kolay dağıldığı yer",
    "pluto": "kontrol ve yoğunluk çizgin",
    "asc": "ilk tepkin ve dışarıya verdiğin izlenim",
    "dsc": "karşı tarafla tuttuğun çizgi",
    "mc": "yönün ve görünür rolün",
    "ic": "iç güvenin",
}

_SIGN_LABELS_TR = {
    "aries": "Koç",
    "taurus": "Boğa",
    "gemini": "İkizler",
    "cancer": "Yengeç",
    "leo": "Aslan",
    "virgo": "Başak",
    "libra": "Terazi",
    "scorpio": "Akrep",
    "sagittarius": "Yay",
    "capricorn": "Oğlak",
    "aquarius": "Kova",
    "pisces": "Balık",
}

_ASPECT_LABELS_TR = {
    "square": "kare",
    "opposition": "karşıt",
    "conjunction": "kavuşum",
    "trine": "üçgen",
    "sextile": "sekstil",
    "quincunx": "quincunx",
}

_DOMAIN_SCENES = {
    "mind": {
        "focus": {
            "friction": "bir konuşmada net kalmak",
            "polarity": "iki şeyi aynı anda anlatmak",
            "concentration": "tek bir kararı netleştirmek",
            "flow": "iletişimi toparlamak",
            "opening": "mesajını sadeleştirmek",
            "mixed": "zihinsel tempoyu ayarlamak",
        },
        "what": "Bugün bir konuşma, mesaj ya da karar anında tempo çabuk yükselebilir.",
        "landing": "Bu en çok {touchpoint} tarafında; yakın çevre, mesaj trafiği ve karar anlarında hissedilir.",
        "guidance": "Yanıtı uzatma; ne demek istediğini önce tek cümlede netleştir.",
    },
    "relationships": {
        "focus": {
            "friction": "karşılıklı beklentiyi net konuşmak",
            "polarity": "iki tarafın ihtiyacını aynı anda taşımak",
            "concentration": "ilişkide tek bir meseleyi ele almak",
            "flow": "arada kalan şeyi konuşmaya açmak",
            "opening": "sınırı daha temiz kurmak",
            "mixed": "ilişkide dengeyi korumak",
        },
        "what": "Bugün bir ilişkide söylenmeyen şeyler daha çabuk belirginleşebilir.",
        "landing": "Bu en çok {touchpoint} tarafında; beklenti, sınır ve konuşulmamış başlıklarda görünür olur.",
        "guidance": "Karşı tarafı test etme; neye evet neye hayır dediğini açık söyle.",
    },
    "identity": {
        "focus": {
            "friction": "ilk tepkinin tonunu ayarlamak",
            "polarity": "geri durmakla öne çıkmak arasında kalmak",
            "concentration": "duruşunu tek çizgide toplamak",
            "flow": "kendini daha doğal göstermek",
            "opening": "görünür olurken rahat kalmak",
            "mixed": "kendini ortaya koyma biçimini ayarlamak",
        },
        "what": "Bugün bir anda verdiğin ilk tepki daha çok dikkat çekebilir.",
        "landing": "Bu en çok {touchpoint} tarafında; duruşun, görünüşün ve kendini ortaya koyma biçiminde belirir.",
        "guidance": "İlk tepkiyi son söz yapma; iki saniye durup sonra cevap ver.",
    },
    "career": {
        "focus": {
            "friction": "işte önceliği net tutmak",
            "polarity": "sorumlulukla görünürlük arasında denge kurmak",
            "concentration": "tek bir işe odaklanmak",
            "flow": "yönünü daha temiz göstermek",
            "opening": "işte doğru kapıyı fark etmek",
            "mixed": "yükün sırasını ayarlamak",
        },
        "what": "Bugün iş tarafında senden netlik ve öncelik bekleyen bir an çıkabilir.",
        "landing": "Bu en çok {touchpoint} tarafında; sorumluluk, görünürlük ve yön duygusunda hissedilir.",
        "guidance": "Hepsini aynı anda taşıma; bugün tek öncelik seç ve onu kapat.",
    },
    "home": {
        "focus": {
            "friction": "ev içinde tansiyonu düşürmek",
            "polarity": "içerideki ihtiyaçlarla dışarıdaki tempoyu dengelemek",
            "concentration": "güven ihtiyacına odaklanmak",
            "flow": "ev içinde rahatlamak",
            "opening": "alanını düzenlemek",
            "mixed": "iç güvenini toparlamak",
        },
        "what": "Bugün ev hali ve iç güven tarafında daha hassas bir eşik olabilir.",
        "landing": "Bu en çok {touchpoint} tarafında; aitlik, güven ve ev içi düzen konularında görünür olur.",
        "guidance": "Önce alanını sadeleştir; sonra kiminle ne konuşacağını seç.",
    },
    "body": {
        "focus": {
            "friction": "günün temposunu düşürmek",
            "polarity": "dinlenmekle yetişmek arasında kalmak",
            "concentration": "ritmini tek çizgide tutmak",
            "flow": "rutini daha rahat kurmak",
            "opening": "bedeninin verdiği sinyali duymak",
            "mixed": "temponu ayarlamak",
        },
        "what": "Bugün tempo ve beden ritmi küçük bir şeyle bile bozulabilir.",
        "landing": "Bu en çok {touchpoint} tarafında; rutin, hız ve beden sinyallerinde hissedilir.",
        "guidance": "Hızı değil ritmi koru; bugün araya kısa bir durak koy.",
    },
    "money": {
        "focus": {
            "friction": "para kararında acele etmemek",
            "polarity": "güvenle harcama arasında denge kurmak",
            "concentration": "tek bir maddi kararı netleştirmek",
            "flow": "değer ölçünü sadeleştirmek",
            "opening": "maddi tarafta küçük rahatlama bulmak",
            "mixed": "güven duygunu ayarlamak",
        },
        "what": "Bugün para, değer ya da güvenlik hissi üzerinden küçük bir baskı doğabilir.",
        "landing": "Bu en çok {touchpoint} tarafında; harcama, değer ve sahip olduklarınla kurduğun ilişkide hissedilir.",
        "guidance": "Bugün ani karar verme; önce gerçekten neye ihtiyaç duyduğunu ayır.",
    },
    "inner": {
        "focus": {
            "friction": "kontrolü biraz gevşetmek",
            "polarity": "yakınlıkla geri çekilme arasında kalmak",
            "concentration": "derindeki bir meseleyi görmek",
            "flow": "içerde tuttuğunu fark etmek",
            "opening": "gerilimi daha erken fark etmek",
            "mixed": "iç baskıyı ayarlamak",
        },
        "what": "Bugün içerde tuttuğun bir şey daha çabuk büyüyebilir.",
        "landing": "Bu en çok {touchpoint} tarafında; yakınlık, güven ve kontrol başlıklarında görünür olur.",
        "guidance": "Kontrolü sıkma; önce seni geren şeyi kendi içinde adıyla koy.",
    },
    "general": {
        "focus": {
            "friction": "günün tonunu sakin tutmak",
            "polarity": "iki ihtiyacı aynı anda taşımak",
            "concentration": "tek meseleye odaklanmak",
            "flow": "akışı bozmadan ilerlemek",
            "opening": "küçük fırsatı fark etmek",
            "mixed": "günü dengede tutmak",
        },
        "what": "Bugün küçük bir an bile günün tonunu hızla değiştirebilir.",
        "landing": "Bu en çok {touchpoint} tarafında görünür olur.",
        "guidance": "Hızlanmadan önce neye cevap verdiğini ayır.",
    },
}


def _clean_text(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _ensure_sentence(value: Any) -> str:
    text = _clean_text(value)
    if not text:
        return ""
    if text.endswith((".", "!", "?")):
        return text
    return f"{text}."


def _normalize_token(value: Any) -> str:
    return _clean_text(value).lower().replace(" ", "_")


def _safe_float(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _pick(seed: str, slot: str, options: Sequence[str]) -> str:
    if not options:
        return ""
    digest = hashlib.sha1(f"{seed}:{slot}".encode("utf-8")).hexdigest()
    index = int(digest[:8], 16) % len(options)
    return options[index]


def _seed_from_inputs(
    daily_event_cards: Sequence[Mapping[str, Any]],
    period_core: Mapping[str, Any] | None,
    natal_snapshot: Mapping[str, Any] | None,
) -> str:
    event_ids = "|".join(_clean_text(card.get("event_id")) for card in daily_event_cards if _clean_text(card.get("event_id")))
    period_title = _clean_text((period_core or {}).get("title"))
    asc_sign = _clean_text((natal_snapshot or {}).get("asc_sign"))
    fallback = "|".join(part for part in (period_title, asc_sign) if part)
    return event_ids or fallback or "daily_synthesis"


def _aggregate_domain_scores(daily_event_cards: Sequence[Mapping[str, Any]]) -> Dict[str, float]:
    totals: Dict[str, float] = {}
    for card in daily_event_cards:
        projection = card.get("lens_projection") if isinstance(card.get("lens_projection"), Mapping) else {}
        projected_scores = projection.get("projected_scores") if isinstance(projection.get("projected_scores"), Mapping) else {}
        domain_scores = card.get("domain_scores") if isinstance(card.get("domain_scores"), Mapping) else {}
        semantic_core = card.get("semantic_core") if isinstance(card.get("semantic_core"), Mapping) else {}

        used_scores = projected_scores or domain_scores
        if isinstance(used_scores, Mapping) and used_scores:
            for domain, value in used_scores.items():
                numeric = _safe_float(value)
                if numeric is None or numeric <= 0.0:
                    continue
                totals[str(domain)] = totals.get(str(domain), 0.0) + numeric
            continue

        for fallback_domain in (
            semantic_core.get("target_house_domain"),
            semantic_core.get("source_house_domain"),
            semantic_core.get("target_affinity"),
        ):
            domain = _normalize_token(fallback_domain)
            if domain:
                totals[domain] = totals.get(domain, 0.0) + 0.3
                break
    return totals


def _dominant_domain(daily_event_cards: Sequence[Mapping[str, Any]]) -> str:
    totals = _aggregate_domain_scores(daily_event_cards)
    if not totals:
        return "general"
    return sorted(totals.items(), key=lambda item: (-item[1], item[0]))[0][0]


def _dominant_mode(daily_event_cards: Sequence[Mapping[str, Any]]) -> str:
    weights: Dict[str, float] = {}
    for index, card in enumerate(daily_event_cards):
        mode = _normalize_token(card.get("aspect_mode")) or "mixed"
        weights[mode] = weights.get(mode, 0.0) + max(0.2, 1.0 - (index * 0.15))
    if not weights:
        return "mixed"
    return sorted(weights.items(), key=lambda item: (-item[1], item[0]))[0][0]


def _theme_slug(domain: str, mode: str) -> str:
    stem = _DOMAIN_THEME_STEMS.get(domain, _DOMAIN_THEME_STEMS["general"])
    suffix = _MODE_SUFFIX.get(mode, _MODE_SUFFIX["mixed"])
    return f"{stem}_{suffix}"


def _theme_description(domain: str, mode: str) -> str:
    domain_line = _DOMAIN_DESCRIPTION_TR.get(domain, _DOMAIN_DESCRIPTION_TR["general"])
    mode_line = _MODE_DESCRIPTION_TR.get(mode, _MODE_DESCRIPTION_TR["mixed"])
    return f"{domain_line} {mode_line}"


def _focus_label(domain: str, daily_event_cards: Sequence[Mapping[str, Any]]) -> str:
    first_card = daily_event_cards[0] if daily_event_cards else {}
    touchpoint = _clean_text(first_card.get("house_touchpoint_tr"))
    if touchpoint:
        return touchpoint
    return _DOMAIN_LABELS_TR.get(domain, _DOMAIN_LABELS_TR["general"])


def _point_focus_label(natal_point: Any) -> str:
    token = _normalize_token(natal_point)
    return _POINT_FOCUS_TR.get(token, "")


def _domain_from_signal(
    *,
    domain: str,
    semantic_core: Mapping[str, Any],
    transit_house: int | None,
    target_house: int | None,
) -> str:
    for candidate in (
        semantic_core.get("target_house_domain"),
        semantic_core.get("source_house_domain"),
        domain,
        _DOMAIN_BY_HOUSE.get(target_house),
        _DOMAIN_BY_HOUSE.get(transit_house),
    ):
        token = _normalize_token(candidate)
        if token:
            return token
    return "general"


def _aspect_mode_from_raw(aspect: str, fallback_mode: str) -> str:
    normalized = _normalize_token(aspect)
    if normalized in {"square", "quincunx"}:
        return "friction"
    if normalized == "opposition":
        return "polarity"
    if normalized == "conjunction":
        return "concentration"
    if normalized == "trine":
        return "flow"
    if normalized == "sextile":
        return "opening"
    return _normalize_token(fallback_mode) or "mixed"


def _timing_flags(card: Mapping[str, Any]) -> Mapping[str, Any]:
    direct = card.get("time") if isinstance(card.get("time"), Mapping) else {}
    if direct:
        return direct
    feature_vector = card.get("feature_vector") if isinstance(card.get("feature_vector"), Mapping) else {}
    return feature_vector.get("time") if isinstance(feature_vector.get("time"), Mapping) else {}


def _extract_primary_signal(card: Mapping[str, Any], *, domain: str, mode: str) -> Dict[str, Any]:
    semantic_core = card.get("semantic_core") if isinstance(card.get("semantic_core"), Mapping) else {}
    derived_context = card.get("derived_context") if isinstance(card.get("derived_context"), Mapping) else {}
    natal_target = derived_context.get("natal_target") if isinstance(derived_context.get("natal_target"), Mapping) else {}
    houses = card.get("houses") if isinstance(card.get("houses"), Mapping) else {}
    timing = card.get("timing") if isinstance(card.get("timing"), Mapping) else {}
    time = _timing_flags(card)
    transit_house = _safe_int(houses.get("transit_in_natal_house"))
    target_house = _safe_int(houses.get("natal_point_house")) or _safe_int(natal_target.get("house"))
    resolved_domain = _domain_from_signal(
        domain=domain,
        semantic_core=semantic_core,
        transit_house=transit_house,
        target_house=target_house,
    )
    aspect = _normalize_token(card.get("aspect"))
    resolved_mode = _aspect_mode_from_raw(aspect, mode)
    orb_deg = _safe_float(card.get("orb_deg"))
    natal_promise = card.get("natal_promise") if isinstance(card.get("natal_promise"), Mapping) else {}
    score = _safe_float(natal_promise.get("score"))

    return {
        "event_id": _clean_text(card.get("event_id")),
        "transit_body": _clean_text(card.get("transit_body")),
        "natal_point": _clean_text(card.get("natal_point")),
        "aspect": aspect,
        "aspect_label_tr": _ASPECT_LABELS_TR.get(aspect, aspect),
        "aspect_mode": resolved_mode,
        "orb_deg": orb_deg,
        "phase": _normalize_token(card.get("phase")),
        "transit_house": transit_house,
        "target_house": target_house,
        "source_domain": _normalize_token(semantic_core.get("source_house_domain")) or _DOMAIN_BY_HOUSE.get(transit_house, ""),
        "target_domain": _normalize_token(semantic_core.get("target_house_domain")) or _DOMAIN_BY_HOUSE.get(target_house, ""),
        "domain": resolved_domain,
        "house_touchpoint_tr": _clean_text(card.get("house_touchpoint_tr")),
        "felt_line_tr": _clean_text(card.get("felt_line_tr")),
        "guidance_micro_tr": _clean_text(card.get("guidance_micro_tr")),
        "peak_date_utc": _clean_text(timing.get("peak_date_utc")),
        "is_peaking_today": bool(time.get("is_peaking_today")),
        "is_rising_today": bool(time.get("is_rising_today")),
        "is_releasing_today": bool(time.get("is_releasing_today")),
        "natal_promise_score": score,
        "natal_target_house": _safe_int(natal_target.get("house")),
        "rulership_houses": [
            house
            for house in (_safe_int(value) for value in (natal_target.get("rulership_houses") or []))
            if house is not None
        ],
    }


def _scene_pack(domain: str) -> Mapping[str, Any]:
    return _DOMAIN_SCENES.get(domain, _DOMAIN_SCENES["general"])


def _headline_focus(signal: Mapping[str, Any]) -> str:
    pack = _scene_pack(str(signal.get("domain") or "general"))
    focus_map = pack.get("focus") if isinstance(pack.get("focus"), Mapping) else {}
    focus = _clean_text(focus_map.get(str(signal.get("aspect_mode") or "mixed")))
    if focus:
        return focus
    return _clean_text(focus_map.get("mixed")) or _DOMAIN_LABELS_TR["general"]


def _headline_variants_for_signal(signal: Mapping[str, Any]) -> tuple[str, ...]:
    focus = _headline_focus(signal)
    mode = str(signal.get("aspect_mode") or "mixed")
    if mode == "friction":
        return (
            f"Bugün {focus} kolay olmayabilir",
            f"Bugün {focus} daha çabuk gerilebilir",
        )
    if mode == "polarity":
        return (
            f"Bugün {focus} seni arada bırakabilir",
            f"Bugün {focus} iki tarafa çekilebilir",
        )
    if mode == "concentration":
        return (
            f"Bugün {focus} bütün gün öne çıkabilir",
            f"Bugün {focus} tek başına büyüyebilir",
        )
    if mode == "flow":
        return (
            f"Bugün {focus} daha rahat ilerleyebilir",
            f"Bugün {focus} doğal bir akış yakalayabilir",
        )
    if mode == "opening":
        return (
            f"Bugün {focus} biraz daha rahat olabilir",
            f"Bugün {focus} için küçük bir fırsat doğabilir",
        )
    return (
        f"Bugün {focus} biraz daha özen isteyebilir",
        f"Bugün {focus} günün tonunu belirleyebilir",
    )


def _build_headline(
    primary_signal: Mapping[str, Any],
    seed: str,
    *,
    narrative_mode: str = "mixed",
    support_signal: Mapping[str, Any] | None = None,
) -> str:
    signal = primary_signal

    if narrative_mode == "support_dominant" and isinstance(support_signal, Mapping):
        signal = support_signal
        variants = _headline_variants_for_signal(signal)
    elif narrative_mode == "mixed" and isinstance(support_signal, Mapping):
        primary_focus = _headline_focus(primary_signal)
        support_focus = _headline_focus(support_signal)
        if support_focus == primary_focus:
            variants = (
                f"Bugün {primary_focus} zorlasa da küçük bir açılma var",
                f"Bugün {primary_focus} gerilse de işleyen bir kapı var",
            )
        else:
            variants = (
                f"Bugün {primary_focus} zorlasa da {support_focus} tarafı açılabilir",
                f"Bugün {primary_focus} gerilse de {support_focus} tarafında kapı aralanabilir",
            )
    else:
        variants = _headline_variants_for_signal(signal)

    is_peak = bool(signal.get("is_peaking_today"))
    tight_orb = (_safe_float(signal.get("orb_deg")) or 9.9) <= 1.2
    if is_peak or tight_orb:
        variants = tuple(
            text.replace("Bugün", "Bugün özellikle", 1)
            if len(text.split()) <= 11
            else text
            for text in variants
        )
    return _ensure_sentence(_pick(seed, "headline", variants))


def _build_what_now(signal: Mapping[str, Any]) -> str:
    felt_line = _ensure_sentence(signal.get("felt_line_tr"))
    if felt_line:
        return felt_line
    pack = _scene_pack(str(signal.get("domain") or "general"))
    return _ensure_sentence(pack.get("what"))


def _build_landing_sentence(signal: Mapping[str, Any]) -> str:
    pack = _scene_pack(str(signal.get("domain") or "general"))
    touchpoint = _clean_text(signal.get("house_touchpoint_tr")) or _DOMAIN_LABELS_TR.get(str(signal.get("domain") or "general"), _DOMAIN_LABELS_TR["general"])
    landing_template = _clean_text(pack.get("landing")) or "Bu en çok {touchpoint} tarafında hissedilir."
    landing = _ensure_sentence(landing_template.format(touchpoint=touchpoint))

    point_focus = _point_focus_label(signal.get("natal_point"))
    score = _safe_float(signal.get("natal_promise_score")) or 0.0
    extras: List[str] = []
    if point_focus and score >= 0.65:
        extras.append(f"Çünkü bu doğrudan {point_focus} çizgine değiyor")

    rulerships = signal.get("rulership_houses") if isinstance(signal.get("rulership_houses"), list) else []
    if rulerships:
        labels = ", ".join(f"{house}. ev" for house in rulerships[:2] if house)
        if labels:
            extras.append(f"O yüzden {labels} başlığı da bu etkiye kolayca eşlik edebilir")

    return _join_body_parts((landing, *extras))


def _tightness_text(signal: Mapping[str, Any]) -> str:
    if bool(signal.get("is_peaking_today")):
        return "Bugün etkisi daha güçlü."
    if bool(signal.get("is_rising_today")):
        return "Gün ilerledikçe bu daha belirginleşebilir."
    if bool(signal.get("is_releasing_today")):
        return "Bugün hâlâ hissedilir ama gün sonunda biraz gevşeyebilir."

    orb_deg = _safe_float(signal.get("orb_deg"))
    phase = str(signal.get("phase") or "")
    if orb_deg is not None and orb_deg <= 1.0:
        return "Bugün etkisi daha keskin hissedilebilir."
    if phase in {"exact", "exactish"}:
        return "Bugün tonu daha yüksek olabilir."
    if phase == "applying":
        return "Şimdilik yükselen bir baskı gibi gelebilir."
    if phase == "separating":
        return "İlk sertliği geçmiş olsa da izi bugün hâlâ sürer."
    return ""


def _mode_tone_sentence(signal: Mapping[str, Any]) -> str:
    mode = str(signal.get("aspect_mode") or "mixed")
    aspect_label = _clean_text(signal.get("aspect_label_tr"))
    timing_tail = _tightness_text(signal)
    aspect_prefix = f"Buradaki {aspect_label}" if aspect_label else "Bu etki"

    if mode == "friction":
        base = f"{aspect_prefix} tonunu daha baskılı ve takılarak hissettirebilir."
    elif mode == "polarity":
        base = f"{aspect_prefix} bir yandan seni, bir yandan karşı tarafı aynı anda konuşturabilir."
    elif mode == "concentration":
        base = f"{aspect_prefix} tek bir meseleyi büyütüp geri kalan şeyi arka plana itebilir."
    elif mode == "flow":
        base = f"{aspect_prefix} burada daha rahat bir akış verebilir."
    elif mode == "opening":
        base = f"{aspect_prefix} küçük ama işe yarar bir açıklık sağlayabilir."
    else:
        base = "Bugün bu başlık birden fazla yerden aynı anda kendini hatırlatabilir."

    if timing_tail:
        return _ensure_sentence(f"{base[:-1]} {timing_tail}")
    return _ensure_sentence(base)


def _period_title(period_core: Mapping[str, Any] | None) -> str:
    core = period_core or {}
    return _clean_text(core.get("title") or core.get("core_story") or core.get("upper_meaning"))


def _build_period_bridge(period_core: Mapping[str, Any] | None) -> str:
    title = _period_title(period_core)
    if not title:
        return ""
    return _ensure_sentence(f'Bu da "{title}" döneminin günlük hayata inen yüzü')


def _base_guidance(signal: Mapping[str, Any], domain: str) -> str:
    direct = _clean_text(signal.get("guidance_micro_tr"))
    if direct:
        return direct.rstrip(".!?")
    pack = _scene_pack(domain)
    guidance = _clean_text(pack.get("guidance"))
    if guidance:
        return guidance.rstrip(".!?")
    return "Hızlanmadan önce neye cevap verdiğini ayır"


def _build_guidance(
    signal: Mapping[str, Any],
    *,
    domain: str,
    narrative_mode: str = "mixed",
    support_signal: Mapping[str, Any] | None = None,
) -> str:
    if narrative_mode == "support_dominant" and isinstance(support_signal, Mapping):
        support_domain = str(support_signal.get("domain") or domain or "general")
        support_guidance = _base_guidance(support_signal, support_domain)
        if support_guidance:
            return _ensure_sentence(support_guidance)

    primary_guidance = _base_guidance(signal, domain)
    if primary_guidance:
        return _ensure_sentence(primary_guidance)

    if isinstance(support_signal, Mapping):
        support_domain = str(support_signal.get("domain") or domain or "general")
        support_guidance = _base_guidance(support_signal, support_domain)
        if support_guidance:
            return _ensure_sentence(support_guidance)

    return _ensure_sentence("Hızlanmadan önce neye cevap verdiğini ayır")


def _period_sources(period_core: Mapping[str, Any] | None) -> List[str]:
    if not isinstance(period_core, Mapping):
        return []
    if any(_clean_text(period_core.get(key)) for key in ("title", "core_story", "upper_meaning", "mechanism")):
        return ["period_core"]
    return []


def _natal_source_tokens(daily_event_cards: Sequence[Mapping[str, Any]], natal_snapshot: Mapping[str, Any] | None) -> List[str]:
    tokens: List[str] = []
    for card in daily_event_cards:
        semantic_core = card.get("semantic_core") if isinstance(card.get("semantic_core"), Mapping) else {}
        derived_context = card.get("derived_context") if isinstance(card.get("derived_context"), Mapping) else {}
        natal_target = derived_context.get("natal_target") if isinstance(derived_context.get("natal_target"), Mapping) else {}
        target_house = semantic_core.get("target_house") or natal_target.get("house")
        if target_house is not None:
            token = f"house_{target_house}"
            if token not in tokens:
                tokens.append(token)
        natal_point = _normalize_token(card.get("natal_point"))
        if natal_point:
            token = f"natal_point_{natal_point}"
            if token not in tokens:
                tokens.append(token)
    asc_sign = _normalize_token((natal_snapshot or {}).get("asc_sign"))
    if asc_sign:
        tokens.append(f"asc_sign_{asc_sign}")
    return tokens


def _daily_sources(daily_event_cards: Sequence[Mapping[str, Any]]) -> List[str]:
    return [
        event_id
        for event_id in (_clean_text(card.get("event_id")) for card in daily_event_cards)
        if event_id
    ]


def _astro_trace(signal: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "event_id": signal.get("event_id"),
        "transit_body": signal.get("transit_body") or None,
        "natal_point": signal.get("natal_point") or None,
        "aspect": signal.get("aspect") or None,
        "aspect_mode": signal.get("aspect_mode") or None,
        "orb_deg": signal.get("orb_deg"),
        "phase": signal.get("phase") or None,
        "transit_house": signal.get("transit_house"),
        "target_house": signal.get("target_house"),
        "source_domain": signal.get("source_domain") or None,
        "target_domain": signal.get("target_domain") or None,
        "house_touchpoint_tr": signal.get("house_touchpoint_tr") or None,
        "peak_date_utc": signal.get("peak_date_utc") or None,
        "is_peaking_today": bool(signal.get("is_peaking_today")),
        "is_rising_today": bool(signal.get("is_rising_today")),
        "is_releasing_today": bool(signal.get("is_releasing_today")),
        "natal_promise_score": signal.get("natal_promise_score"),
        "rulership_houses": list(signal.get("rulership_houses") or []),
    }


def _event_id(card: Mapping[str, Any] | None) -> str:
    if not isinstance(card, Mapping):
        return ""
    return _clean_text(card.get("event_id"))


def _period_featured_events(period_core: Mapping[str, Any] | None) -> List[Dict[str, Any]]:
    if not isinstance(period_core, Mapping):
        return []
    featured = period_core.get("featured_events")
    if not isinstance(featured, Sequence):
        return []
    return [dict(item) for item in featured if isinstance(item, Mapping)]


def _period_story_debug(period_core: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if not isinstance(period_core, Mapping):
        return {}
    debug = period_core.get("_period_story_debug")
    return debug if isinstance(debug, Mapping) else {}


def _signal_candidates(
    daily_event_cards: Sequence[Mapping[str, Any]],
    period_event_cards: Sequence[Mapping[str, Any]] | None,
    period_core: Mapping[str, Any] | None,
) -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    seen_ids: set[str] = set()
    for source in (
        daily_event_cards,
        period_event_cards or (),
        _period_featured_events(period_core),
    ):
        for item in source:
            if not isinstance(item, Mapping):
                continue
            event_id = _event_id(item)
            key = event_id or f"anon:{len(candidates)}"
            if key in seen_ids:
                continue
            seen_ids.add(key)
            candidates.append(dict(item))
    return candidates


def _signal_from_card(card: Mapping[str, Any], *, fallback_domain: str, fallback_mode: str) -> Dict[str, Any]:
    signal = _extract_primary_signal(
        card,
        domain=_dominant_domain([card]) or fallback_domain,
        mode=_dominant_mode([card]) or fallback_mode,
    )
    chapter_role = card.get("chapter_role") if isinstance(card.get("chapter_role"), Mapping) else {}
    signal["chapter_role"] = _clean_text(chapter_role.get("role")).lower()
    signal["chapter_role_score"] = _safe_float(chapter_role.get("score"))
    signal["story_score"] = _safe_float(card.get("story_score"))
    return signal


def _signal_strength(signal: Mapping[str, Any]) -> float:
    score = 0.0
    orb_deg = _safe_float(signal.get("orb_deg"))
    if orb_deg is not None:
        if orb_deg <= 0.5:
            score += 0.16
        elif orb_deg <= 1.2:
            score += 0.12
        elif orb_deg <= 2.5:
            score += 0.08
        elif orb_deg <= 4.0:
            score += 0.04

    if bool(signal.get("is_peaking_today")):
        score += 0.16
    elif bool(signal.get("is_rising_today")) or bool(signal.get("is_releasing_today")):
        score += 0.08

    score += max(0.0, min(1.0, _safe_float(signal.get("natal_promise_score")) or 0.0)) * 0.12
    score += max(0.0, min(1.0, _safe_float(signal.get("chapter_role_score")) or 0.0)) * 0.08
    score += max(0.0, min(1.0, _safe_float(signal.get("story_score")) or 0.0)) * 0.05
    return score


def _pressure_score(signal: Mapping[str, Any]) -> float:
    mode = _normalize_token(signal.get("aspect_mode"))
    base = {
        "friction": 0.60,
        "polarity": 0.52,
        "concentration": 0.38,
        "mixed": 0.30,
        "opening": 0.18,
        "flow": 0.16,
    }.get(mode, 0.28)
    return base + _signal_strength(signal)


def _support_score(
    signal: Mapping[str, Any],
    *,
    primary_signal: Mapping[str, Any],
    preferred_roles: set[str] | None = None,
) -> float:
    mode = _normalize_token(signal.get("aspect_mode"))
    score = {
        "opening": 0.28,
        "flow": 0.24,
        "concentration": 0.12,
        "mixed": 0.08,
        "polarity": 0.04,
        "friction": 0.0,
    }.get(mode, 0.05)
    score += _signal_strength(signal)

    if _normalize_token(signal.get("natal_point")) and _normalize_token(signal.get("natal_point")) == _normalize_token(primary_signal.get("natal_point")):
        score += 0.22
    if _safe_int(signal.get("target_house")) is not None and _safe_int(signal.get("target_house")) == _safe_int(primary_signal.get("target_house")):
        score += 0.14
    if _normalize_token(signal.get("domain")) and _normalize_token(signal.get("domain")) == _normalize_token(primary_signal.get("domain")):
        score += 0.10
    if _normalize_token(signal.get("target_domain")) and _normalize_token(signal.get("target_domain")) == _normalize_token(primary_signal.get("target_domain")):
        score += 0.08
    if preferred_roles and _normalize_token(signal.get("chapter_role")) in preferred_roles:
        score += 0.10
    if mode in {"friction", "polarity"}:
        score -= 0.08
    return score


def _cluster_support_ids(primary_card: Mapping[str, Any] | None) -> List[str]:
    if not isinstance(primary_card, Mapping):
        return []
    return [
        _clean_text(event_id)
        for event_id in (primary_card.get("cluster_support_event_ids") or [])
        if _clean_text(event_id)
    ]


def _find_signal_by_event_id(
    candidates: Sequence[Mapping[str, Any]],
    event_id: str,
    *,
    fallback_domain: str,
    fallback_mode: str,
) -> Dict[str, Any] | None:
    normalized_id = _clean_text(event_id)
    if not normalized_id:
        return None
    for item in candidates:
        if _event_id(item) == normalized_id:
            return _signal_from_card(item, fallback_domain=fallback_domain, fallback_mode=fallback_mode)
    return None


def _resolve_period_spine_signal(
    *,
    candidates: Sequence[Mapping[str, Any]],
    period_core: Mapping[str, Any] | None,
    primary_signal: Mapping[str, Any],
    default_card: Mapping[str, Any],
    default_domain: str,
    default_mode: str,
) -> Dict[str, Any]:
    debug = _period_story_debug(period_core)
    spine = _find_signal_by_event_id(
        candidates,
        _clean_text(debug.get("spine_event_id")),
        fallback_domain=default_domain,
        fallback_mode=default_mode,
    )
    if spine is not None:
        spine["chapter_role"] = _clean_text(debug.get("spine_role"))
        spine["_spine_source"] = "period_story_debug"
        return spine
    fallback = _signal_from_card(default_card, fallback_domain=default_domain, fallback_mode=default_mode)
    if _clean_text(primary_signal.get("event_id")):
        fallback["event_id"] = _clean_text(primary_signal.get("event_id"))
    fallback["chapter_role"] = _clean_text(debug.get("spine_role"))
    fallback["_spine_source"] = "primary_fallback"
    return fallback


def _support_priority(signal: Mapping[str, Any]) -> tuple[int, float, float]:
    mode = _normalize_token(signal.get("aspect_mode"))
    phase = _normalize_token(signal.get("phase"))
    orb_deg = _safe_float(signal.get("orb_deg")) or 9.9
    mode_rank = {
        "opening": 0,
        "flow": 1,
        "concentration": 2,
        "mixed": 3,
        "polarity": 4,
        "friction": 5,
    }.get(mode, 6)
    phase_rank = 0.0 if phase in {"exact", "exactish", "applying"} else 1.0
    return (mode_rank, phase_rank, orb_deg)


def _resolve_support_signal(
    *,
    candidates: Sequence[Mapping[str, Any]],
    period_core: Mapping[str, Any] | None,
    primary_signal: Mapping[str, Any],
    primary_card: Mapping[str, Any] | None,
    default_domain: str,
    default_mode: str,
) -> Dict[str, Any] | None:
    debug = _period_story_debug(period_core)
    trigger_id = _clean_text(primary_signal.get("event_id"))
    support_roles = {
        _clean_text(role).lower()
        for role in (debug.get("support_roles") or [])
        if _clean_text(role)
    }
    support_signals: List[tuple[float, Dict[str, Any]]] = []
    support_ids: List[str] = []
    support_id_sources: Dict[str, str] = {}
    cluster_support_ids = _cluster_support_ids(primary_card)
    for event_id in cluster_support_ids:
        if event_id not in support_ids:
            support_ids.append(event_id)
        support_id_sources[event_id] = "cluster_support_ids"
    for event_id in [
        _clean_text(event_id)
        for event_id in (debug.get("support_event_ids") or [])
        if _clean_text(event_id)
    ]:
        if event_id not in support_ids:
            support_ids.append(event_id)
        support_id_sources.setdefault(event_id, "period_story_debug")
    for event_id in support_ids:
        if event_id == trigger_id:
            continue
        signal = _find_signal_by_event_id(
            candidates,
            event_id,
            fallback_domain=default_domain,
            fallback_mode=default_mode,
        )
        if signal is not None:
            score = _support_score(signal, primary_signal=primary_signal, preferred_roles=support_roles)
            signal["_support_score"] = round(score, 4)
            signal["_support_source"] = support_id_sources.get(event_id, "support_ids")
            support_signals.append((score, signal))
    if support_signals:
        best_score, best_signal = sorted(
            support_signals,
            key=lambda item: (-item[0], _support_priority(item[1])),
        )[0]
        if best_score >= 0.55:
            return best_signal

    scored_candidates: List[tuple[float, Dict[str, Any]]] = []
    for item in candidates:
        if _event_id(item) == trigger_id:
            continue
        signal = _signal_from_card(item, fallback_domain=default_domain, fallback_mode=default_mode)
        score = _support_score(signal, primary_signal=primary_signal, preferred_roles=support_roles)
        signal["_support_score"] = round(score, 4)
        signal["_support_source"] = "candidate_score"
        scored_candidates.append((score, signal))
    if not scored_candidates:
        return None
    best_score, best_signal = sorted(
        scored_candidates,
        key=lambda item: (-item[0], _support_priority(item[1])),
    )[0]
    if best_score >= 0.82:
        return best_signal
    return None


def _resolve_narrative_mode(primary_signal: Mapping[str, Any], support_signal: Mapping[str, Any] | None) -> str:
    primary_pressure = _pressure_score(primary_signal)
    support_presence = 0.0
    if isinstance(support_signal, Mapping):
        support_presence = _support_score(
            support_signal,
            primary_signal=primary_signal,
            preferred_roles=None,
        )

    primary_mode = _normalize_token(primary_signal.get("aspect_mode"))
    if primary_mode in {"opening", "flow"} and support_presence <= primary_pressure:
        return "support_dominant"
    if primary_pressure >= 0.95 and support_presence < 0.75:
        return "pressure_dominant"
    if support_presence >= 0.8 and primary_pressure >= 0.75:
        return "mixed"
    if support_presence > primary_pressure + 0.18:
        return "support_dominant"
    if primary_pressure > support_presence + 0.18:
        return "pressure_dominant"
    return "mixed"


def _same_signal_token(left: Any, right: Any) -> bool:
    return bool(_normalize_token(left)) and _normalize_token(left) == _normalize_token(right)


def _planner_spine_debug(spine_signal: Mapping[str, Any], primary_signal: Mapping[str, Any]) -> Dict[str, Any]:
    reasons: List[str] = []
    if _clean_text(spine_signal.get("chapter_role")):
        reasons.append(f"chapter_role:{_clean_text(spine_signal.get('chapter_role'))}")
    if _same_signal_token(spine_signal.get("natal_point"), primary_signal.get("natal_point")):
        reasons.append("same_natal_point_as_trigger")
    if _same_signal_token(spine_signal.get("domain"), primary_signal.get("domain")):
        reasons.append("same_domain_as_trigger")
    if _safe_float(spine_signal.get("story_score")) is not None:
        reasons.append(f"story_score:{round(_safe_float(spine_signal.get('story_score')) or 0.0, 4)}")
    return {
        "event_id": _clean_text(spine_signal.get("event_id")) or None,
        "source": _clean_text(spine_signal.get("_spine_source")) or "unknown",
        "chapter_role": _clean_text(spine_signal.get("chapter_role")) or None,
        "reasons": reasons,
    }


def _planner_support_debug(
    support_signal: Mapping[str, Any] | None,
    *,
    primary_signal: Mapping[str, Any],
) -> Dict[str, Any]:
    if not isinstance(support_signal, Mapping):
        return {
            "event_id": None,
            "source": "none",
            "score": 0.0,
            "reasons": ["no_support_signal_cleared_threshold"],
        }

    reasons: List[str] = []
    if _same_signal_token(support_signal.get("natal_point"), primary_signal.get("natal_point")):
        reasons.append("same_natal_point")
    if _safe_int(support_signal.get("target_house")) is not None and _safe_int(support_signal.get("target_house")) == _safe_int(primary_signal.get("target_house")):
        reasons.append("same_target_house")
    if _same_signal_token(support_signal.get("domain"), primary_signal.get("domain")):
        reasons.append("same_domain")
    if _same_signal_token(support_signal.get("target_domain"), primary_signal.get("target_domain")):
        reasons.append("same_target_domain")
    if _clean_text(support_signal.get("chapter_role")):
        reasons.append(f"chapter_role:{_clean_text(support_signal.get('chapter_role'))}")
    if _normalize_token(support_signal.get("aspect_mode")) in {"opening", "flow"}:
        reasons.append(f"supportive_mode:{_normalize_token(support_signal.get('aspect_mode'))}")
    if _safe_float(support_signal.get("orb_deg")) is not None:
        reasons.append(f"orb:{round(_safe_float(support_signal.get('orb_deg')) or 0.0, 2)}")

    return {
        "event_id": _clean_text(support_signal.get("event_id")) or None,
        "source": _clean_text(support_signal.get("_support_source")) or "unknown",
        "score": round(_safe_float(support_signal.get("_support_score")) or 0.0, 4),
        "reasons": reasons,
    }


def _planner_mode_debug(
    *,
    primary_signal: Mapping[str, Any],
    support_signal: Mapping[str, Any] | None,
    narrative_mode: str,
) -> Dict[str, Any]:
    primary_pressure = round(_pressure_score(primary_signal), 4)
    support_presence = 0.0
    if isinstance(support_signal, Mapping):
        support_presence = round(
            _support_score(
                support_signal,
                primary_signal=primary_signal,
                preferred_roles=None,
            ),
            4,
        )

    if narrative_mode == "mixed":
        reason = "pressure_and_support_are_both_meaningful"
    elif narrative_mode == "support_dominant":
        reason = "support_signal_outweighs_daily_pressure"
    else:
        reason = "daily_pressure_outweighs_support_signal"

    return {
        "mode": narrative_mode,
        "primary_pressure_score": primary_pressure,
        "support_score": support_presence,
        "reason": reason,
    }


def _spine_source_tokens(spine_signal: Mapping[str, Any]) -> List[str]:
    tokens: List[str] = []
    event_id = _clean_text(spine_signal.get("event_id"))
    if event_id:
        tokens.append(event_id)
    for key in ("transit_body", "natal_point", "aspect"):
        token = _normalize_token(spine_signal.get(key))
        if token:
            tokens.append(f"{key}_{token}")
    return tokens


def _support_source_tokens(support_signal: Mapping[str, Any] | None) -> List[str]:
    if not isinstance(support_signal, Mapping):
        return []
    tokens: List[str] = []
    event_id = _clean_text(support_signal.get("event_id"))
    if event_id:
        tokens.append(event_id)
    for key in ("transit_body", "natal_point", "aspect"):
        token = _normalize_token(support_signal.get(key))
        if token:
            tokens.append(f"{key}_{token}")
    return tokens


def _build_support_sentence(signal: Mapping[str, Any]) -> str:
    if not signal:
        return ""
    support_felt = _clean_text(signal.get("felt_line_tr"))
    if support_felt:
        lowered = support_felt.lower()
        if lowered.startswith("bugün "):
            return _ensure_sentence(f"Ama aynı gün {support_felt[6:]}")
        return _ensure_sentence(f"Ama aynı gün {support_felt[:1].lower()}{support_felt[1:]}")
    domain = str(signal.get("domain") or "general")
    touchpoint = _clean_text(signal.get("house_touchpoint_tr")) or _DOMAIN_LABELS_TR.get(domain, _DOMAIN_LABELS_TR["general"])
    mode = _normalize_token(signal.get("aspect_mode"))
    if mode == "opening":
        return _ensure_sentence(f"Ama aynı gün {touchpoint} tarafında gerçekten işe yarayan küçük bir açıklık var")
    if mode == "flow":
        return _ensure_sentence(f"Aynı anda {touchpoint} tarafında daha doğal bir akış yakalanabilir")
    if mode == "concentration":
        return _ensure_sentence(f"Ayrıca {touchpoint} tarafında toparlayıcı bir odak oluşabilir")
    return ""


def _build_spine_bridge(period_core: Mapping[str, Any] | None, spine_signal: Mapping[str, Any]) -> str:
    title = _period_title(period_core)
    if not title:
        return ""
    touchpoint = _clean_text(spine_signal.get("house_touchpoint_tr"))
    if touchpoint:
        return _ensure_sentence(f'Bu yeni bir başlık değil; içinde olduğun "{title}" dönemi bugün en çok {touchpoint} tarafına vuruyor')
    return _ensure_sentence(f'Bu yeni bir başlık değil; içinde olduğun "{title}" dönemi bugün yine belirgin')


def _join_body_parts(parts: Iterable[str]) -> str:
    clean_parts = [_ensure_sentence(part) for part in parts if _clean_text(part)]
    return " ".join(part for part in clean_parts if part)


def build_daily_synthesis(
    *,
    daily_event_cards: Sequence[Mapping[str, Any]],
    period_core: Mapping[str, Any] | None,
    natal_snapshot: Mapping[str, Any] | None,
    period_event_cards: Sequence[Mapping[str, Any]] | None = None,
) -> Dict[str, Any]:
    cards = [dict(card) for card in daily_event_cards if isinstance(card, Mapping)]
    if not cards:
        return {}

    seed = _seed_from_inputs(cards, period_core, natal_snapshot)
    domain = _dominant_domain(cards)
    mode = _dominant_mode(cards)
    theme = _theme_slug(domain, mode)
    primary_signal = _signal_from_card(cards[0], fallback_domain=domain, fallback_mode=mode)
    domain = str(primary_signal.get("domain") or domain or "general")
    mode = str(primary_signal.get("aspect_mode") or mode or "mixed")
    candidates = _signal_candidates(cards, period_event_cards, period_core)
    period_spine = _resolve_period_spine_signal(
        candidates=candidates,
        period_core=period_core,
        primary_signal=primary_signal,
        default_card=cards[0],
        default_domain=domain,
        default_mode=mode,
    )
    support_signal = _resolve_support_signal(
        candidates=candidates,
        period_core=period_core,
        primary_signal=primary_signal,
        primary_card=cards[0],
        default_domain=domain,
        default_mode=mode,
    )
    narrative_mode = _resolve_narrative_mode(primary_signal, support_signal)

    headline = _build_headline(
        primary_signal,
        seed,
        narrative_mode=narrative_mode,
        support_signal=support_signal,
    )
    what_now = _build_what_now(primary_signal)
    landing = _build_landing_sentence(primary_signal)
    tone = _mode_tone_sentence(primary_signal)
    spine_bridge = _build_spine_bridge(period_core, period_spine)
    support_line = _build_support_sentence(support_signal or {})
    guidance = _build_guidance(
        primary_signal,
        domain=domain,
        narrative_mode=narrative_mode,
        support_signal=support_signal,
    )
    if narrative_mode == "support_dominant":
        body_parts = (what_now, support_line, landing, spine_bridge)
    elif narrative_mode == "mixed":
        body_parts = (what_now, landing, support_line, tone, spine_bridge)
    else:
        body_parts = (what_now, landing, tone, support_line, spine_bridge)

    return {
        "theme": _theme_slug(domain, mode),
        "theme_description": _theme_description(domain, mode),
        "headline": headline,
        "body": _join_body_parts(body_parts),
        "guidance": guidance,
        "narrative_mode": narrative_mode,
        "primary_signal": _astro_trace(primary_signal),
        "period_spine": _astro_trace(period_spine),
        "support_signal": _astro_trace(support_signal) if support_signal else None,
        "planner_debug": {
            "spine_resolution": _planner_spine_debug(period_spine, primary_signal),
            "support_resolution": _planner_support_debug(
                support_signal,
                primary_signal=primary_signal,
            ),
            "mode_resolution": _planner_mode_debug(
                primary_signal=primary_signal,
                support_signal=support_signal,
                narrative_mode=narrative_mode,
            ),
        },
        "sources": {
            "daily": _daily_sources(cards),
            "period": _period_sources(period_core),
            "natal": _natal_source_tokens(cards, natal_snapshot),
            "period_spine": _spine_source_tokens(period_spine),
            "support": _support_source_tokens(support_signal),
            "trace": _astro_trace(primary_signal),
        },
    }
