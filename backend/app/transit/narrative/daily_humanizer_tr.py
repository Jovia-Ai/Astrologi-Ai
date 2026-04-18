from __future__ import annotations

import re
from typing import Any, Dict, Mapping

from app.transit.narrative.semantic_projection import (
    build_semantic_projection,
    normalize_lens,
)

HOUSE_PACKS_TR: dict[int, dict[str, Any]] = {
    1: {
        "touchpoint": "kendini ortaya koyma biçimin",
        "felt_context": "Kendine karşı",
        "why_context": "tavrında",
        "guidance_context": "duruşunu",
        "hint": "En çok tavrına vurabilir.",
        "visibility_tokens": ("kendine", "tavr", "duruş", "öne çık"),
    },
    2: {
        "touchpoint": "para ve özdeğer tarafın",
        "felt_context": "Para ya da değer tarafında",
        "why_context": "özdeğer tarafında",
        "guidance_context": "harcamayı ya da değer ölçünü",
        "hint": "Para ya da değer tarafında daha çabuk belli olabilir.",
        "visibility_tokens": ("para", "değer", "özdeğer"),
    },
    3: {
        "touchpoint": "zihnin ve konuşma halin",
        "felt_context": "Konuşurken",
        "why_context": "zihninde",
        "guidance_context": "cümleni",
        "hint": "En çok konuşurken belli olabilir.",
        "visibility_tokens": ("konuş", "cümle", "zihin", "söz"),
    },
    4: {
        "touchpoint": "ev içi güven halin",
        "felt_context": "Ev halin içinde",
        "why_context": "güven alanında",
        "guidance_context": "alanını",
        "hint": "Ev haline çabuk yansıyabilir.",
        "visibility_tokens": ("ev", "alan", "güven", "içeri"),
    },
    5: {
        "touchpoint": "kalbin ve keyif alanın",
        "felt_context": "Kalbini açtığın yerde",
        "why_context": "keyif tarafında",
        "guidance_context": "hevesini",
        "hint": "Kalbine ve keyfine çabuk düşebilir.",
        "visibility_tokens": ("kalp", "keyif", "heves", "yarat"),
    },
    6: {
        "touchpoint": "günün ritmi ve düzenin",
        "felt_context": "Günün akışında",
        "why_context": "ritminde",
        "guidance_context": "tempoyu",
        "hint": "Günün ritmini kolay bozabilir.",
        "visibility_tokens": ("ritim", "tempo", "gün", "düzen"),
    },
    7: {
        "touchpoint": "karşı tarafla arandaki çizgi",
        "felt_context": "Karşı tarafla aranda",
        "why_context": "denge tarafında",
        "guidance_context": "mesafeyi",
        "hint": "En çok karşı tarafta fark edilebilir.",
        "visibility_tokens": ("karşı", "arada", "denge", "mesafe"),
    },
    8: {
        "touchpoint": "yakınlık ve kontrol tarafın",
        "felt_context": "Yakınlık tarafında",
        "why_context": "kontrol duygunda",
        "guidance_context": "gerilimi",
        "hint": "Yakınlıkta ya da kontrolde büyüyebilir.",
        "visibility_tokens": ("yakın", "kontrol", "derin", "paylaş"),
    },
    9: {
        "touchpoint": "bakışın ve ufkun",
        "felt_context": "Bakışında",
        "why_context": "ufkunda",
        "guidance_context": "fikrini",
        "hint": "Bakışını ve fikrini hızlı değiştirebilir.",
        "visibility_tokens": ("bakış", "ufuk", "fikir", "yön"),
    },
    10: {
        "touchpoint": "yönün ve görünürlüğün",
        "felt_context": "İş tarafında",
        "why_context": "görünür olduğun yerde",
        "guidance_context": "hızını",
        "hint": "Duruşuna ve görünürlüğüne taşabilir.",
        "visibility_tokens": ("iş", "görün", "yön", "dışarı"),
    },
    11: {
        "touchpoint": "arkadaşların ve planların",
        "felt_context": "Arkadaşlar ve planlar tarafında",
        "why_context": "gelecek tarafında",
        "guidance_context": "beklentiyi",
        "hint": "Arkadaşlarınla planda daha görünür olur.",
        "visibility_tokens": ("arkadaş", "plan", "gelecek", "çevre"),
    },
    12: {
        "touchpoint": "içine çekildiğin yerler",
        "felt_context": "İçe çekildiğin yerde",
        "why_context": "arkada kalan tarafta",
        "guidance_context": "yalnız kalma ihtiyacını",
        "hint": "İçine kapanınca daha çok büyüyebilir.",
        "visibility_tokens": ("iç", "arkada", "yalnız", "geri çek"),
    },
}

DEFAULT_HOUSE_PACK_TR = {
    "touchpoint": "günün içinde tuttuğun yer",
    "felt_context": "Bugün",
    "why_context": "arka planda",
    "guidance_context": "hızını",
    "hint": "Bugün en çok tuttuğun yerde belli olabilir.",
    "visibility_tokens": ("bugün",),
}

TRIGGER_FAMILY_TR = {
    "moon": "emotion",
    "sun": "self",
    "mercury": "mind",
    "venus": "closeness",
    "mars": "reaction",
    "jupiter": "expansion",
    "saturn": "brake",
    "uranus": "surprise",
    "neptune": "blur",
    "pluto": "intensity",
}

ASPECT_MODE_TR = {
    "square": "friction",
    "quincunx": "friction",
    "opposition": "polarity",
    "conjunction": "concentration",
    "trine": "flow",
    "sextile": "opening",
    "semisextile": "opening",
}

FLOW_SIGNAL_BY_MODE = {
    "friction": "Bugün biraz sürtünmeli.",
    "polarity": "Bugün iki taraf konuşuyor.",
    "concentration": "Tek bir şey fazla öne çıkıyor.",
    "flow": "Bugün akış açılıyor.",
    "opening": "Küçük bir alan açılıyor.",
    "mixed": "Bugün bir şey kıpırdıyor.",
}

TONE_LABEL_BY_MODE = {
    "friction": "friction",
    "polarity": "polarity",
    "concentration": "concentration",
    "flow": "flow",
    "opening": "opening",
    "mixed": "mixed",
}

PLANET_LABEL_TR = {
    "sun": "Güneş",
    "moon": "Ay",
    "mercury": "Merkür",
    "venus": "Venüs",
    "mars": "Mars",
    "jupiter": "Jüpiter",
    "saturn": "Satürn",
    "uranus": "Uranüs",
    "neptune": "Neptün",
    "pluto": "Plüton",
}

POINT_LABEL_TR = {
    "sun": "Güneş",
    "moon": "Ay",
    "mercury": "Merkür",
    "venus": "Venüs",
    "mars": "Mars",
    "jupiter": "Jüpiter",
    "saturn": "Satürn",
    "uranus": "Uranüs",
    "neptune": "Neptün",
    "pluto": "Plüton",
    "asc": "Yükselen",
    "dsc": "Alçalan",
    "mc": "Tepe Noktası",
    "ic": "Dip Noktası",
}

ASPECT_LABEL_TR = {
    "conjunction": "kavuşumu",
    "square": "karesi",
    "opposition": "karşıtı",
    "trine": "üçgeni",
    "sextile": "sekstili",
    "quincunx": "quincunxu",
    "semisextile": "yarı altıgeni",
}

TR_LOWER_MAP = {
    "I": "ı",
    "İ": "i",
    "Ğ": "ğ",
    "Ü": "ü",
    "Ş": "ş",
    "Ö": "ö",
    "Ç": "ç",
}

TR_UPPER_MAP = {
    "ı": "I",
    "i": "İ",
    "ğ": "Ğ",
    "ü": "Ü",
    "ş": "Ş",
    "ö": "Ö",
    "ç": "Ç",
}

SIGN_LABEL_TR = {
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

HOUSE_DOMAIN_TR = {
    1: "benlik ve duruş",
    2: "özdeğer ve maddi düzen",
    3: "zihin ve iletişim",
    4: "ev ve iç güven",
    5: "yaratıcılık ve ifade",
    6: "rutin ve beden ritmi",
    7: "ilişki ve ortaklık",
    8: "yakınlık ve güven",
    9: "ufuk ve yön arayışı",
    10: "kariyer ve görünürlük",
    11: "çevre ve gelecek planları",
    12: "arka plan ve iç dünya",
}


def _safe_int(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _sentence(text: str) -> str:
    cleaned = " ".join(str(text or "").strip().split())
    if not cleaned:
        return ""
    if cleaned.endswith((".", "!", "?")):
        return cleaned
    return f"{cleaned}."


def _lowercase_first(text: str) -> str:
    cleaned = " ".join(str(text or "").strip().split())
    if not cleaned:
        return ""
    head = cleaned[0]
    lowered = TR_LOWER_MAP.get(head, head.lower())
    return f"{lowered}{cleaned[1:]}"


def _capitalize_first(text: str) -> str:
    cleaned = " ".join(str(text or "").strip().split())
    if not cleaned:
        return ""
    head = cleaned[0]
    uppered = TR_UPPER_MAP.get(head, head.upper())
    return f"{uppered}{cleaned[1:]}"


def _strip_leading_because(text: str) -> str:
    cleaned = " ".join(str(text or "").strip().split())
    lowered = cleaned.lower()
    if lowered.startswith("çünkü "):
        return cleaned[6:].strip()
    return cleaned


def _first_sentence(text: str) -> str:
    cleaned = " ".join(str(text or "").strip().split())
    if not cleaned:
        return ""
    parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", cleaned) if part.strip()]
    if not parts:
        return ""
    return parts[0].rstrip(".!?")


def _append_unique_sentence(lines: list[str], text: str) -> None:
    sentence = _sentence(text)
    normalized = re.sub(r"\s+", " ", sentence).strip().lower()
    if not normalized:
        return
    if any(re.sub(r"\s+", " ", existing).strip().lower() == normalized for existing in lines):
        return
    lines.append(sentence)


def _compact_signature(event: Mapping[str, Any]) -> str:
    raw = str(event.get("signature_tr") or event.get("signature") or "").strip()
    if raw:
        compact = re.split(r"\s+[•—-]\s+", raw, maxsplit=1)[0].strip()
        compact = re.sub(r"\s*\([^)]*\)", "", compact).strip().rstrip(".")
        if compact:
            return compact

    body = PLANET_LABEL_TR.get(str(event.get("transit_body") or "").strip().lower(), "")
    target = POINT_LABEL_TR.get(str(event.get("natal_point") or "").strip().lower(), "")
    aspect = ASPECT_LABEL_TR.get(str(event.get("aspect") or "").strip().lower(), "")
    if body and target and aspect:
        return f"{body} ile {target} {aspect}"
    if body and aspect:
        return f"{body} {aspect}"
    return body or "bu gökyüzü hareketi"


def _signature_display(event: Mapping[str, Any]) -> str:
    compact = _compact_signature(event)
    if compact:
        return compact
    return _narrative_signature(event)


def _narrative_signature(event: Mapping[str, Any]) -> str:
    body = PLANET_LABEL_TR.get(str(event.get("transit_body") or "").strip().lower(), "")
    point_key = str(event.get("natal_point") or "").strip().lower()
    target = POINT_LABEL_TR.get(point_key, "")
    aspect = ASPECT_LABEL_TR.get(str(event.get("aspect") or "").strip().lower(), "")
    if body and target and aspect:
        return f"{body}-{target} {aspect}"
    compact = _compact_signature(event)
    return compact if compact else "bu gökyüzü hareketi"


def _house_domain(house: int | None) -> str:
    if house is None:
        return "hayatının aktif alanı"
    return HOUSE_DOMAIN_TR.get(house, f"{house}. ev alanı")


def _scene_activation_sentence(event: Mapping[str, Any], *, pack: Mapping[str, Any]) -> str:
    scene = event.get("scene") if isinstance(event.get("scene"), Mapping) else {}
    houses = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}
    transit_house = _safe_int(scene.get("start_house"))
    if transit_house is None:
        transit_house = _safe_int(houses.get("transit_in_natal_house"))
    target_house = _safe_int(scene.get("outcome_house"))
    if target_house is None:
        target_house = _safe_int(houses.get("natal_point_house"))
    touchpoint = str(pack.get("touchpoint") or "günün aktif alanı").strip()

    if transit_house is not None and target_house is not None and transit_house != target_house:
        return (
            f"Bu hareket önce {transit_house}. evinde, yani {_house_domain(transit_house)} alanında çalışıyor. "
            f"Ama hikâye orada kalmıyor; {target_house}. evdeki temayı tetiklediği için bu etki en çok "
            f"{touchpoint} üzerinde görünür oluyor"
        )
    if transit_house is not None:
        return (
            f"Bu hareket {transit_house}. evinde çalıştığı için bugün {_house_domain(transit_house)} tarafı "
            f"daha görünür. Orada görünen şey, özellikle {touchpoint} daha çabuk hareketleniyor"
        )
    if target_house is not None:
        return (
            f"Bu hareket {target_house}. evdeki temayı tetiklediği için bugün en görünür başlık {touchpoint}; "
            "hikâye en hızlı orada hassaslaşıyor"
        )

    technical_note = _first_sentence(str(event.get("technical_note") or "").replace("Teknik not:", "").strip())
    if technical_note:
        return technical_note
    return ""


def _natal_resonance_sentence(event: Mapping[str, Any]) -> str:
    derived = event.get("derived_context") if isinstance(event.get("derived_context"), Mapping) else {}
    angle = derived.get("angle") if isinstance(derived.get("angle"), Mapping) else {}
    if angle:
        angle_name = POINT_LABEL_TR.get(str(angle.get("name") or "").strip().lower(), str(angle.get("name") or "").strip())
        angle_sign = SIGN_LABEL_TR.get(str(angle.get("sign") or "").strip().lower(), str(angle.get("sign") or "").strip())
        ruler = PLANET_LABEL_TR.get(str(angle.get("ruler") or "").strip().lower(), str(angle.get("ruler") or "").strip())
        ruler_house = _safe_int(angle.get("ruler_house"))
        transit_house = _safe_int(((event.get("scene") or {}).get("start_house")))
        if angle_name and angle_sign and ruler and ruler_house is not None and transit_house is not None:
            return (
                f"{angle_name} hattın {angle_sign}; yöneticisi {ruler} sende {ruler_house}. evde. "
                f"O yüzden burada görünen şey yalnızca {transit_house}. evdeki gündelik tetik değil; "
                "doğrudan o hatta inen daha derin bir ayar"
            )
        if angle_name and angle_sign and ruler and ruler_house is not None:
            return (
                f"{angle_name} hattın {angle_sign}; yöneticisi {ruler} sende {ruler_house}. evde. "
                "Bu yüzden bu açı sende daha kişisel; dışarıda görünen şeyin altında daha derin bir eşik de çalışıyor"
            )

    pack = event.get("natal_context_pack") if isinstance(event.get("natal_context_pack"), Mapping) else {}
    target = pack.get("target") if isinstance(pack.get("target"), Mapping) else {}
    planet = POINT_LABEL_TR.get(str(target.get("planet") or "").strip().lower(), str(target.get("planet") or "").strip())
    sign = str(target.get("sign_tr") or "").strip() or SIGN_LABEL_TR.get(str(target.get("sign") or "").strip().lower(), str(target.get("sign") or "").strip())
    house = _safe_int(target.get("house"))
    if planet and sign and house is not None:
        return (
            f"Natal haritanda {planet} {sign} burcunda {house}. evde. "
            f"Bu yüzden bu açı sende sadece bugünün havasını anlatmıyor; altta zaten çalışan "
            f"{_house_domain(house)} temasını yeniden uyandırıyor"
        )

    natal_target = derived.get("natal_target") if isinstance(derived.get("natal_target"), Mapping) else {}
    sign_fallback = SIGN_LABEL_TR.get(str(natal_target.get("sign") or "").strip().lower(), str(natal_target.get("sign") or "").strip())
    house_fallback = _safe_int(natal_target.get("house"))
    point_name = POINT_LABEL_TR.get(str(natal_target.get("name") or "").strip().lower(), str(natal_target.get("name") or "").strip())
    if point_name and sign_fallback and house_fallback is not None:
        return (
            f"Natal haritanda {point_name} {sign_fallback} çizgisi {house_fallback}. ev temasıyla bağlı. "
            "Bu yüzden bu gökyüzü hareketi sende yeni değil; tanıdık geldiği yer tam da bu daha derin hat"
        )
    return ""


def _period_bridge_sentence(
    event: Mapping[str, Any],
    *,
    is_period_derived: bool,
    source_horizon: str,
) -> str:
    period_story = event.get("period_story") if isinstance(event.get("period_story"), Mapping) else {}
    period_title = str(period_story.get("title") or "").strip()
    bucket = str(event.get("bucket") or "").strip().lower()
    time_hint = str(event.get("time_hint_tr") or event.get("time_hint") or "").strip().lower()

    if period_title:
        if is_period_derived or source_horizon == "period":
            return f"Bugün yaşadığın şey tek başına değil; \"{period_title}\" döneminin bugüne inen yüzü."
        return f"Yani bugünkü tetik tek başına değil; arkada \"{period_title}\" döneminin sana hangi kapıdan açıldığını gösteriyor."
    if is_period_derived or source_horizon == "period":
        if bucket == "long" or "ay" in time_hint:
            return "Bugün yaşadığın şey tek başına değil; birkaç aydır çalışan dönemin bugüne inen yüzü."
        if bucket == "medium" or "hafta" in time_hint:
            return "Bugün yaşadığın şey tek başına değil; birkaç haftadır şekillenen dönemin bugüne inen yüzü."
        return "Bugün yaşadığın şey tek başına değil; arka planda süren dönemin bugüne inen yüzü."

    return "Yani bugünkü tetik tek başına değil; dönemin ana temasının sana bugün hangi kapıdan dokunduğunu gösteriyor."


def _period_story_editorial_sentence(event: Mapping[str, Any]) -> str:
    period_story = event.get("period_story") if isinstance(event.get("period_story"), Mapping) else {}
    if not period_story:
        return ""

    preferred_fields = (
        ("big_picture", "Bu hikâye tek katmanlı değil"),
        ("lead", "Bu hikâye tek katmanlı değil"),
        ("period_opening", "Bu dönemin açtığı eşik de burada"),
        ("what_it_builds", "Altta çalışan şey biraz da bu"),
        ("upper_meaning", "Altta çalışan şey biraz da bu"),
        ("mechanism", "Arka planda süreç şöyle işliyor"),
    )
    for field_name, intro in preferred_fields:
        excerpt = _first_sentence(str(period_story.get(field_name) or "").strip())
        if not excerpt:
            continue
        return f"{intro}: {excerpt}"
    return ""


def _build_enriched_why_line(
    event: Mapping[str, Any],
    *,
    pack: Mapping[str, Any],
    base_why_line: str,
    is_period_derived: bool,
) -> str:
    signature = _signature_display(event)
    narrative_signature = _narrative_signature(event)
    source_horizon = str(event.get("source_horizon") or event.get("horizon") or "").strip().lower()
    why_clause = _capitalize_first(_lowercase_first(_strip_leading_because(base_why_line)))
    sentences: list[str] = []

    if signature and narrative_signature and signature.lower() != narrative_signature.lower():
        _append_unique_sentence(
            sentences,
            f"Bugünün tonunu özellikle {signature} belirliyor; bu {narrative_signature} bugün daha görünür çalışıyor",
        )
    else:
        _append_unique_sentence(sentences, f"Bugünün tonunu özellikle {signature or narrative_signature} belirliyor")

    scene_line = _scene_activation_sentence(event, pack=pack)
    if scene_line:
        _append_unique_sentence(sentences, scene_line)
    elif why_clause:
        _append_unique_sentence(sentences, why_clause)

    natal_line = _natal_resonance_sentence(event)
    if natal_line:
        _append_unique_sentence(sentences, natal_line)
    elif why_clause:
        _append_unique_sentence(sentences, why_clause)

    period_line = _period_bridge_sentence(
        event,
        is_period_derived=is_period_derived,
        source_horizon=source_horizon,
    )
    if period_line:
        _append_unique_sentence(sentences, period_line)
    period_story_line = _period_story_editorial_sentence(event)
    if period_story_line:
        _append_unique_sentence(sentences, period_story_line)

    return " ".join(sentences).strip()


def house_touchpoint_from_event(event: Mapping[str, Any]) -> int | None:
    derived = event.get("derived_context") if isinstance(event.get("derived_context"), Mapping) else {}
    natal_target = derived.get("natal_target") if isinstance(derived.get("natal_target"), Mapping) else {}
    scene = event.get("scene") if isinstance(event.get("scene"), Mapping) else {}
    houses = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}
    for candidate in (
        natal_target.get("house"),
        scene.get("outcome_house"),
        scene.get("start_house"),
        houses.get("natal_point_house"),
        houses.get("transit_in_natal_house"),
    ):
        house = _safe_int(candidate)
        if house is not None and 1 <= house <= 12:
            return house
    return None


def aspect_mode_from_event(event: Mapping[str, Any]) -> str:
    aspect = str(event.get("aspect") or "").strip().lower()
    return ASPECT_MODE_TR.get(aspect, "mixed")


def _trigger_family_from_event(event: Mapping[str, Any]) -> str:
    body = str(event.get("transit_body") or "").strip().lower()
    return TRIGGER_FAMILY_TR.get(body, "mixed")


def _house_pack(event: Mapping[str, Any]) -> dict[str, Any]:
    house = house_touchpoint_from_event(event)
    if house is None:
        return dict(DEFAULT_HOUSE_PACK_TR)
    pack = HOUSE_PACKS_TR.get(house)
    return dict(pack or DEFAULT_HOUSE_PACK_TR)


def _select_tone_face(mode: str, score: float, *, is_period_derived: bool) -> str:
    if mode == "flow":
        return "flow"
    if mode == "opening":
        return "flow" if score >= 0.72 else "growth"
    if mode == "concentration":
        return "growth" if is_period_derived or score >= 0.62 else "shadow"
    if mode == "polarity":
        return "growth" if score >= 0.74 else "shadow"
    if mode == "friction":
        return "growth" if is_period_derived or score >= 0.8 else "shadow"
    return "growth"


def _felt_line(pack: Mapping[str, Any], trigger: str, mode: str) -> str:
    context = str(pack.get("felt_context") or "Bugün").strip()
    if mode == "polarity":
        mapping = {
            "mind": f"{context} söylemek isteyip aynı anda geri çekilebilirsin bugün.",
            "closeness": f"{context} yakın gelmekle mesafe koymak aynı anda çalışabilir.",
            "reaction": f"{context} hızlanıp bir anda geri durabilirsin bugün.",
            "self": f"{context} görünmek isteyip sonra geri çekilebilirsin bugün.",
        }
        return mapping.get(trigger, f"{context} bir yanın isterken diğer yanın geri durabilir.")
    if mode == "concentration":
        mapping = {
            "reaction": f"{context} tek bir dürtü fazla büyüyebilir bugün.",
            "mind": f"{context} tek bir düşünce fazla yer kaplayabilir bugün.",
            "intensity": f"{context} tek bir mesele fazla ağır basabilir bugün.",
            "self": f"{context} tek bir konu üstünde fazla durabilirsin bugün.",
        }
        return mapping.get(trigger, f"{context} tek bir şey fazla öne çıkabilir bugün.")
    if mode == "flow":
        mapping = {
            "self": f"{context} bir şey daha doğal akıyor bugün.",
            "mind": f"{context} ne diyeceğin daha rahat geliyor bugün.",
            "closeness": f"{context} yakınlık daha yumuşak akabilir bugün.",
            "reaction": f"{context} içinden gelenle yaptığın şey daha uyumlu olabilir.",
        }
        return mapping.get(trigger, f"{context} bir şey daha rahat akıyor bugün.")
    if mode == "opening":
        mapping = {
            "emotion": f"{context} ufak bir rahatlama alanı açılabilir bugün.",
            "mind": f"{context} küçük ama işe yarayan bir açıklık doğabilir bugün.",
            "closeness": f"{context} küçük bir yakınlaşma alanı açılabilir bugün.",
            "self": f"{context} geri durmadan görünmek biraz daha kolay olabilir bugün.",
        }
        return mapping.get(trigger, f"{context} küçük bir alan açılabilir bugün.")
    mapping = {
        "mind": f"{context} sürtünme çabuk büyüyebilir bugün.",
        "closeness": f"{context} denge çabuk bozulabilir bugün.",
        "reaction": f"{context} sabırsızlık hızla yükselebilir bugün.",
        "blur": f"{context} ne hissettiğini toparlamak zorlaşabilir bugün.",
        "brake": f"{context} ağırlık daha fazla hissedilebilir bugün.",
    }
    return mapping.get(trigger, f"{context} bir sürtünme çabuk büyüyebilir bugün.")


def _why_line(pack: Mapping[str, Any], trigger: str, mode: str, face: str) -> str:
    context = str(pack.get("why_context") or "arka planda").strip()
    if mode == "polarity":
        mapping = {
            "mind": f"Çünkü {context} bir yanın netleşmek isterken diğer yanın geri duruyor.",
            "closeness": f"Çünkü {context} yaklaşmak isteyen tarafınla sınır koyan tarafın aynı anda çalışıyor.",
            "self": f"Çünkü {context} açılmak isteyen tarafınla sakınan tarafın aynı hızda değil.",
        }
        return mapping.get(trigger, f"Çünkü {context} iki ayrı yön aynı anda bastırıyor.")
    if mode == "concentration":
        mapping = {
            "reaction": f"Çünkü {context} aynı yere fazla yük biniyor.",
            "mind": f"Çünkü {context} aynı düşünce dönüp dönüp geri geliyor.",
            "intensity": f"Çünkü {context} bir şey artık arka planda kalmıyor.",
            "self": f"Çünkü {context} tek bir duruş büyüyüp her şeyi boyuyor.",
        }
        return mapping.get(trigger, f"Çünkü {context} tek bir konu fazla büyüyor.")
    if mode == "flow":
        mapping = {
            "mind": f"Çünkü {context} ne düşündüğünle ne dediğin daha kolay buluşuyor.",
            "self": f"Çünkü {context} kendini göstermek daha doğal geliyor.",
            "closeness": f"Çünkü {context} yakınlık kurmak zorlamadan oluyor.",
            "reaction": f"Çünkü {context} refleksinle yönün daha aynı yerde duruyor.",
        }
        return mapping.get(trigger, f"Çünkü {context} içinle yaptığın şey daha uyumlu ilerliyor.")
    if mode == "opening":
        mapping = {
            "mind": f"Çünkü {context} küçük bir netlik kapısı aralanıyor.",
            "emotion": f"Çünkü {context} biraz daha rahat yer buluyor.",
            "self": f"Çünkü {context} gerilmeden görünmek mümkün oluyor.",
            "closeness": f"Çünkü {context} yumuşak bir yaklaşım işe yarıyor.",
        }
        return mapping.get(trigger, f"Çünkü {context} küçük ama gerçek bir açıklık var.")
    if face == "growth":
        return f"Çünkü {context} zorlayan şey sana neyin artık taşmadığını gösteriyor."
    mapping = {
        "mind": f"Çünkü {context} aklın hızlanıyor ama cümlen aynı rahatlıkta gelmiyor.",
        "closeness": f"Çünkü {context} beklentiyle gördüğün şey aynı gelmiyor.",
        "reaction": f"Çünkü {context} dürtü önce geliyor, ayar sonradan yetişiyor.",
        "blur": f"Çünkü {context} neyin net neyin dağınık olduğu hemen ayrışmıyor.",
        "brake": f"Çünkü {context} bir yanın yüklenirken diğer yanın dur diyor.",
    }
    return mapping.get(trigger, f"Çünkü {context} içinden geçenle yaptığın şey aynı hızda akmıyor.")


def _guidance_line(pack: Mapping[str, Any], trigger: str, mode: str, face: str) -> str:
    context = str(pack.get("guidance_context") or "hızını").strip()
    if mode == "flow":
        return f"{context[:1].upper() + context[1:]} biraz daha görünür kıl."
    if mode == "opening":
        return f"{context[:1].upper() + context[1:]} zorlamadan aç."
    if mode == "polarity":
        return "İlk tarafı final sanma."
    if mode == "concentration":
        return "Her şeyi bugün çözmeye çalışma."
    if trigger == "mind":
        return "İlk cümleye mecbur değilsin."
    if trigger == "reaction":
        return "Hemen tepki verme."
    if face == "growth":
        return f"{context[:1].upper() + context[1:]} biraz yavaşlat."
    return "Acele etme."


def _has_house_visibility(lines: list[str], pack: Mapping[str, Any]) -> bool:
    text = " ".join(lines).lower()
    return any(token in text for token in pack.get("visibility_tokens", ()))


def _enforce_house_visibility(lines: list[str], pack: Mapping[str, Any]) -> list[str]:
    if _has_house_visibility(lines, pack):
        return lines
    why = f"Bu en çok {pack.get('touchpoint')} tarafında belli oluyor."
    return [lines[0], why, lines[2]]


def _relationship_house_context(house: int | None) -> str:
    mapping = {
        1: "kendi duruşunda",
        3: "konuşma ve mesajlaşma tarafında",
        4: "güvende hissetme alanında",
        5: "çekim ve kalp açıklığında",
        7: "karşı tarafla aranda",
        8: "yakınlık ve güven tarafında",
        12: "daha içte ve özel bir yerde",
    }
    return mapping.get(house, "ilişki tarafında")


def _relationship_channel_line(core: Mapping[str, Any]) -> str:
    source_house = _safe_int(core.get("source_house"))
    target_house = _safe_int(core.get("target_house"))
    if source_house == 3:
        return "Bunu en çok konuşma, mesajlaşma ya da niyetini söyleme tarafında hissedebilirsin."
    if source_house == 7:
        return "Karşı tarafın sözü, beklentisi ya da varlığı bunu daha görünür kılıyor."
    if source_house == 12:
        return "Bu dışarıdan çok içeride çalışan bir hareket gibi ilerliyor."
    if source_house == 1:
        return "Mesele kadar onu nasıl taşıdığın da belirleyici oluyor."
    if target_house == 12:
        return "Yakınlık burada daha çok sessiz, özel ve içte yaşanıyor."
    if target_house == 8:
        return "Yakınlıkla güven ihtiyacı birbirine daha yakın duruyor."
    if target_house == 5:
        return "Kalbinin neye açıldığını daha net hissedebilirsin."
    if target_house == 7:
        return "Karşı taraf aynası duyguyu daha görünür hale getiriyor."
    return "Bunun nasıl ilerlediği kadar nasıl hissettirdiği de önemli hale geliyor."


def _relationship_guidance_line(mode: str) -> str:
    if mode == "flow":
        return "Yumuşayan şeyi hemen tanım koymaya zorlama."
    if mode == "opening":
        return "Açılan alanı aceleyle büyütmeye çalışma."
    if mode == "polarity":
        return "İlk tepkiyi nihai karar sanma."
    if mode == "concentration":
        return "Tek meseleyi bütün ilişkinin yerine koyma."
    return "Hem sınırı hem teması aynı cümlede tutmaya çalış."


def _relationship_daily_lines(core: Mapping[str, Any], mode: str) -> list[str]:
    target_house = _safe_int(core.get("target_house"))
    context = _relationship_house_context(target_house)
    if mode == "flow":
        felt = {
            12: "Yakınlık şu an daha çok içte büyüyor bugün.",
            7: "Karşı tarafla arandaki akış biraz daha doğal bugün.",
            8: "Yakınlık ve güven tarafı daha yumuşak akabilir bugün.",
            5: "Çekim ve kalp açıklığı daha rahat akıyor bugün.",
        }.get(target_house, f"{context[:1].upper() + context[1:]} yumuşayan bir alan var bugün.")
    elif mode == "opening":
        felt = {
            12: "İlişkide içte kalan bir alan hafifçe açılıyor bugün.",
            7: "Karşı tarafla aranda küçük ama gerçek bir açıklık doğuyor bugün.",
            8: "Yakınlıkta küçük ama işe yarayan bir açıklık var bugün.",
            5: "Çekim tarafında küçük bir açılma mümkün bugün.",
        }.get(target_house, "İlişkide küçük ama gerçek bir alan açılıyor bugün.")
    elif mode == "polarity":
        felt = {
            7: "İlişkide bir yanın yaklaşırken bir yanın mesafe isteyebilir bugün.",
            1: "İlişkide açılmak isterken aynı anda kendini korumak da isteyebilirsin bugün.",
        }.get(target_house, "Yakınlık isterken aynı anda geri çekilmek de isteyebilirsin bugün.")
    elif mode == "concentration":
        felt = "İlişkide tek bir mesele fazla yer kaplayabilir bugün."
    else:
        felt = "İlişkide temas ve sınır aynı anda sürtebilir bugün."
    why = _relationship_channel_line(core)
    guidance = _relationship_guidance_line(mode)
    return [felt, why, guidance]


def generate_daily_from_event(
    event: Mapping[str, Any],
    *,
    score: float | None = None,
    is_period_derived: bool = False,
    force_daily_horizon: bool = False,
    lens: str = "general",
) -> Dict[str, Any]:
    out = dict(event)
    pack = _house_pack(out)
    trigger = _trigger_family_from_event(out)
    mode = aspect_mode_from_event(out)
    projection = build_semantic_projection(out, lens=lens)
    semantic_core = projection.get("semantic_core") if isinstance(projection.get("semantic_core"), Mapping) else {}
    lens_projection = projection.get("lens_projection") if isinstance(projection.get("lens_projection"), Mapping) else {}
    score_value = max(0.0, float(score or out.get("daily_score") or 0.0))
    face = _select_tone_face(mode, score_value, is_period_derived=is_period_derived)
    relationship_score = float(
        ((lens_projection.get("projected_scores") or {}).get("relationships") or 0.0)
    )
    if normalize_lens(lens) == "relationships" and relationship_score >= 0.42:
        lines = _relationship_daily_lines(semantic_core, mode)
    else:
        lines = _enforce_house_visibility(
            [
                _felt_line(pack, trigger, mode),
                _why_line(pack, trigger, mode, face),
                _guidance_line(pack, trigger, mode, face),
            ],
            pack,
        )

    source_horizon = str(out.get("source_horizon") or out.get("horizon") or "").strip().lower()
    if force_daily_horizon:
        out["source_horizon"] = source_horizon or "period"
        out["horizon"] = "daily"

    selected_why_line = lines[1]
    if str(selected_why_line or "").strip().lower().startswith("bu en çok "):
        selected_why_line = _why_line(pack, trigger, mode, face)

    out["felt_line_tr"] = _sentence(lines[0])
    out["why_it_feels_this_way_tr"] = _build_enriched_why_line(
        out,
        pack=pack,
        base_why_line=selected_why_line,
        is_period_derived=bool(is_period_derived),
    )
    out["guidance_micro_tr"] = _sentence(lines[2])
    out["signal_label_tr"] = _sentence(FLOW_SIGNAL_BY_MODE.get(mode, FLOW_SIGNAL_BY_MODE["mixed"]))
    out["tone_label_tr"] = TONE_LABEL_BY_MODE.get(mode, "mixed")
    out["house_touchpoint_tr"] = str(pack.get("touchpoint") or "").strip()
    out["house_touchpoint_hint_tr"] = str(pack.get("hint") or "").strip()
    out["aspect_mode"] = mode
    out["tone_face"] = face
    out["is_period_derived"] = bool(is_period_derived)
    out["today_facing_fallback"] = bool(is_period_derived)
    out["semantic_core"] = semantic_core
    out["domain_scores"] = projection.get("domain_scores") or {}
    out["lens_projection"] = lens_projection
    return out


def humanize_event_card_tr(
    card: Mapping[str, Any],
    *,
    score: float | None = None,
    is_period_derived: bool | None = None,
    lens: str = "general",
) -> Dict[str, Any]:
    derived = bool(is_period_derived)
    if is_period_derived is None:
        source_horizon = str(card.get("source_horizon") or "").strip().lower()
        derived = source_horizon == "period"
    return generate_daily_from_event(
        card,
        score=score,
        is_period_derived=derived,
        force_daily_horizon=False,
        lens=lens,
    )


def summarize_daily_micro_copy(card: Mapping[str, Any]) -> str:
    felt = _sentence(str(card.get("felt_line_tr") or "").strip())
    why = _sentence(str(card.get("why_it_feels_this_way_tr") or "").strip())
    return felt or why or ""
