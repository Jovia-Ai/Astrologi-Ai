from __future__ import annotations

from typing import Any, Dict, Mapping

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


def generate_daily_from_event(
    event: Mapping[str, Any],
    *,
    score: float | None = None,
    is_period_derived: bool = False,
    force_daily_horizon: bool = False,
) -> Dict[str, Any]:
    out = dict(event)
    pack = _house_pack(out)
    trigger = _trigger_family_from_event(out)
    mode = aspect_mode_from_event(out)
    score_value = max(0.0, float(score or out.get("daily_score") or 0.0))
    face = _select_tone_face(mode, score_value, is_period_derived=is_period_derived)
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

    out["felt_line_tr"] = _sentence(lines[0])
    out["why_it_feels_this_way_tr"] = _sentence(lines[1])
    out["guidance_micro_tr"] = _sentence(lines[2])
    out["signal_label_tr"] = _sentence(FLOW_SIGNAL_BY_MODE.get(mode, FLOW_SIGNAL_BY_MODE["mixed"]))
    out["tone_label_tr"] = TONE_LABEL_BY_MODE.get(mode, "mixed")
    out["house_touchpoint_tr"] = str(pack.get("touchpoint") or "").strip()
    out["house_touchpoint_hint_tr"] = str(pack.get("hint") or "").strip()
    out["aspect_mode"] = mode
    out["tone_face"] = face
    out["is_period_derived"] = bool(is_period_derived)
    out["today_facing_fallback"] = bool(is_period_derived)
    return out


def humanize_event_card_tr(
    card: Mapping[str, Any],
    *,
    score: float | None = None,
    is_period_derived: bool | None = None,
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
    )


def summarize_daily_micro_copy(card: Mapping[str, Any]) -> str:
    felt = _sentence(str(card.get("felt_line_tr") or "").strip())
    why = _sentence(str(card.get("why_it_feels_this_way_tr") or "").strip())
    return felt or why or ""
