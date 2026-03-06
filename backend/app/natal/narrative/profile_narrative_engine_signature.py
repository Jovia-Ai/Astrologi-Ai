from __future__ import annotations

from typing import Any, Dict, Mapping

from app.natal.narrative.micro_example_engine_tr import choose_micro_example
from app.natal.narrative.phrase_lib_tr_profile import render_block_template
from app.natal.narrative.signature_catalog_tr import SIGNATURE_CATALOG_TR
from app.natal.narrative.signature_engine import BLOCK_ORDER, extract_candidates, normalize_facts, select_by_block


FALLBACK_ARENA_BY_BLOCK = {
    "identity_aura": 1,
    "mind_voice": 3,
    "drive_rhythm": 9,
    "love_depth": 8,
    "career_visibility": 10,
    "home_roots": 4,
    "luck_creation": 5,
}

FALLBACK_SIGNATURES_BY_BLOCK = {
    "identity_aura": {
        "signature_id": "fallback_identity_chart_ruler",
        "spark": False,
        "chips": ["Duruş", "Yön", "Çerçeve"],
        "copy_tr": {
            "headline": "Duruşun",
            "teaser": "Haritanın yönü, senin duruş ve karar tarzın üzerinden güçleniyor.",
            "spark": "Kendini ortaya koyma biçimin, hayatın ritmini de belirler.",
            "gift": "İyi çalıştığında netlik ve istikrar verir.",
            "watch": "Zorlandığında dağılma artabilir; küçük çerçeve iyi gelir.",
        },
    },
    "mind_voice": {
        "signature_id": "fallback_mind_voice",
        "spark": False,
        "chips": ["Zihin", "İfade", "Netlik"],
        "copy_tr": {
            "headline": "Zihnin yönü",
            "teaser": "Düşünme ve anlatma biçimin hayat akışında belirleyici bir yer tutuyor.",
            "spark": "Senin için doğru cümle, çoğu zaman doğru kararla aynı kapıyı açıyor.",
            "gift": "İyi çalıştığında açıklık ve sağlam iletişim kurarsın.",
            "watch": "Zorlandığında konuyu uzatmak yerine niyeti netlemek iyi gelir.",
        },
    },
    "drive_rhythm": {
        "signature_id": "fallback_drive_rhythm",
        "spark": False,
        "chips": ["Ritim", "Tempo", "İlk Adım"],
        "copy_tr": {
            "headline": "Hareket ritmin",
            "teaser": "Sende hız, doğru ritim oturunca daha verimli çalışıyor.",
            "spark": "Başlangıç şeklin günün geri kalan temposunu doğrudan etkiliyor.",
            "gift": "İyi çalıştığında sürdürülebilir ve temiz bir hareket hattı kurarsın.",
            "watch": "Zorlandığında tek adımı seçmek dağılmayı azaltır.",
        },
    },
    "love_depth": {
        "signature_id": "fallback_love_depth",
        "spark": False,
        "chips": ["Yakınlık", "Güven", "Netlik"],
        "copy_tr": {
            "headline": "Yakınlık biçimin",
            "teaser": "İlişkide güven duygusu, sende hızdan daha önemli çalışıyor.",
            "spark": "Bağ kurarken tutarlılık ve temiz sinyal kalbini daha hızlı açıyor.",
            "gift": "İyi çalıştığında sıcak, güven veren bir temas kurarsın.",
            "watch": "Zorlandığında küçük ama net cümleler ilişkiyi taşır.",
        },
    },
    "career_visibility": {
        "signature_id": "fallback_career_visibility",
        "spark": False,
        "chips": ["Vitrin", "Süreklilik", "İşçilik"],
        "copy_tr": {
            "headline": "Görünürlük çizgin",
            "teaser": "İşin büyümesi, çoğu zaman düzenli görünürlükle güçleniyor.",
            "spark": "Sende etki, bir anda parlamaktan çok istikrarlı iz bırakınca büyüyor.",
            "gift": "İyi çalıştığında kaliteyi görünür sonuca dönüştürürsün.",
            "watch": "Zorlandığında beklemek yerine küçük vitrin adımı daha iyi çalışır.",
        },
    },
    "home_roots": {
        "signature_id": "fallback_home_roots",
        "spark": False,
        "chips": ["Ev", "Güven", "Toparlanma"],
        "copy_tr": {
            "headline": "Köklerin",
            "teaser": "İç güven alanın, dış dünyadaki performansını doğrudan besliyor.",
            "spark": "Kendi alanında ritim kurduğunda zihin ve beden daha hızlı toparlanıyor.",
            "gift": "İyi çalıştığında ev, senin merkezlenme alanın olur.",
            "watch": "Zorlandığında küçük düzenlemeler güveni geri toplar.",
        },
    },
    "luck_creation": {
        "signature_id": "fallback_luck_creation",
        "spark": False,
        "chips": ["Fırsat", "Akış", "Başlat"],
        "copy_tr": {
            "headline": "Fırsat ritmin",
            "teaser": "Şans sende çoğu zaman hareketle ve görünür adımla açılıyor.",
            "spark": "Bir şeyi başlattığında akışın sana cevap verme ihtimali yükseliyor.",
            "gift": "İyi çalıştığında fırsatı üretime ve temasa çevirebilirsin.",
            "watch": "Zorlandığında beklemek yerine küçük bir deneme şansı açar.",
        },
    },
}


def _bridge(color_signature: Mapping[str, Any] | None) -> str:
    if not isinstance(color_signature, Mapping):
        return ""
    spark = str(((color_signature.get("copy_tr") or {}) if isinstance(color_signature.get("copy_tr"), Mapping) else {}).get("spark") or "").strip()
    if not spark:
        return ""
    return f"Buna eşlik eden ikinci ton da açık: {spark} "


def _infer_arena_house(block_id: str, selection: Mapping[str, Any]) -> int:
    for candidate in (selection.get("primary"), selection.get("color")):
        if not isinstance(candidate, Mapping):
            continue
        for token in candidate.get("astro_tokens") or []:
            if not isinstance(token, Mapping):
                continue
            house = token.get("house") or token.get("target_house")
            resolved = _safe_house(house)
            if resolved is not None:
                return resolved
        for evidence in candidate.get("evidence") or []:
            if not isinstance(evidence, Mapping):
                continue
            house = evidence.get("house") or evidence.get("ruler_house")
            resolved = _safe_house(house)
            if resolved is not None:
                return resolved
    return FALLBACK_ARENA_BY_BLOCK.get(block_id, 1)


def _safe_house(value: Any) -> int | None:
    try:
        ivalue = int(value)
    except (TypeError, ValueError):
        return None
    return ivalue if 1 <= ivalue <= 12 else None


def _micro_mode(selection: Mapping[str, Any]) -> str:
    primary = selection.get("primary") if isinstance(selection.get("primary"), Mapping) else {}
    for evidence in primary.get("evidence") or []:
        if not isinstance(evidence, Mapping):
            continue
        aspect = str(evidence.get("aspect") or "").lower()
        if aspect in {"square", "opposition"}:
            return "hard"
        if aspect in {"trine", "sextile"}:
            return "soft"
        if aspect == "conjunction":
            return "conj"
    return "neutral"


def _micro_valence(selection: Mapping[str, Any]) -> str:
    primary = selection.get("primary") if isinstance(selection.get("primary"), Mapping) else {}
    if primary.get("spark"):
        return "growth"
    for evidence in primary.get("evidence") or []:
        if isinstance(evidence, Mapping) and str(evidence.get("aspect") or "").lower() in {"square", "opposition"}:
            return "repair"
    return "growth"


def _tone_planets(selection: Mapping[str, Any]) -> list[str]:
    planets: list[str] = []
    for candidate in (selection.get("primary"), selection.get("color")):
        if not isinstance(candidate, Mapping):
            continue
        for token in candidate.get("astro_tokens") or []:
            if not isinstance(token, Mapping):
                continue
            for key in ("planet", "a", "b"):
                value = str(token.get(key) or "").strip()
                if value and value not in {"ASC", "MC", "DSC", "IC"} and value not in planets:
                    planets.append(value)
        for evidence in candidate.get("evidence") or []:
            if not isinstance(evidence, Mapping):
                continue
            for key in ("planet", "planet1", "planet2", "ruler"):
                value = str(evidence.get(key) or "").strip()
                if value and value not in {"Ascendant", "Midheaven", "Descendant", "Imum Coeli"} and value not in planets:
                    planets.append(value)
    return planets


def _fallback_evidence(block_id: str, facts: Mapping[str, Any]) -> list[Dict[str, Any]]:
    planets = facts.get("planets") if isinstance(facts.get("planets"), Mapping) else {}
    house_rulers = facts.get("house_rulers") if isinstance(facts.get("house_rulers"), Mapping) else {}
    angle_signs = facts.get("angle_signs") if isinstance(facts.get("angle_signs"), Mapping) else {}

    def placement(planet: str) -> Dict[str, Any]:
        payload = planets.get(planet) if isinstance(planets.get(planet), Mapping) else {}
        return {"type": "placement", "planet": planet, "sign": payload.get("sign"), "house": payload.get("house")}

    def ruler(house: int) -> Dict[str, Any]:
        payload = house_rulers.get(str(house)) if isinstance(house_rulers.get(str(house)), Mapping) else {}
        pos = payload.get("primary_ruler_pos") if isinstance(payload.get("primary_ruler_pos"), Mapping) else {}
        return {
            "type": "house_ruler",
            "house": house,
            "cusp_sign": payload.get("cusp_sign"),
            "ruler": payload.get("primary_ruler"),
            "ruler_house": pos.get("house"),
        }

    mapping = {
        "identity_aura": [{"type": "angle", "angle": "ASC", "sign": angle_signs.get("ASC")}, ruler(1)],
        "mind_voice": [placement("Mercury"), ruler(3)],
        "drive_rhythm": [placement("Mars"), ruler(9)],
        "love_depth": [placement("Moon"), ruler(7)],
        "career_visibility": [{"type": "angle", "angle": "MC", "sign": angle_signs.get("MC")}, ruler(10)],
        "home_roots": [{"type": "angle", "angle": "IC", "sign": angle_signs.get("IC")}, ruler(4)],
        "luck_creation": [placement("Fortune"), placement("Jupiter")],
    }
    return mapping.get(block_id, [])


def _render_block(block_id: str, selection: Mapping[str, Any], seed: str) -> Dict[str, Any]:
    primary = selection.get("primary") if isinstance(selection.get("primary"), Mapping) else {}
    arena_house = _infer_arena_house(block_id, selection)
    micro = choose_micro_example(
        seed=f"{seed}|{block_id}|{primary.get('signature_id')}",
        arena_house=arena_house,
        mode=_micro_mode(selection),
        tone_planets=_tone_planets(selection),
        valence=_micro_valence(selection),
    )
    slots = {
        "copy": dict(primary.get("copy_tr") or {}),
        "astro_hint": "",
        "micro": micro,
        "bridge": _bridge(selection.get("color")),
    }
    return render_block_template(block_id=block_id, seed=f"{seed}|{primary.get('signature_id')}", slots=slots)


def _fallback_selection(block_id: str, facts: Mapping[str, Any]) -> Dict[str, Any]:
    base = FALLBACK_SIGNATURES_BY_BLOCK[block_id]
    primary = {
        **base,
        "id": base["signature_id"],
        "score": 0.2,
        "evidence": _fallback_evidence(block_id, facts),
        "astro_tokens": [{"type": "fallback", "house": FALLBACK_ARENA_BY_BLOCK.get(block_id)}],
    }
    return {"primary": primary, "color": None}


def _public_block(block_id: str, rendered: Mapping[str, Any], selection: Mapping[str, Any]) -> Dict[str, Any]:
    primary = selection.get("primary") if isinstance(selection.get("primary"), Mapping) else {}
    color = selection.get("color") if isinstance(selection.get("color"), Mapping) else {}
    chips: list[str] = []
    for source in (primary.get("chips") or [], color.get("chips") or []):
        for chip in source:
            value = str(chip).strip()
            if value and value not in chips and len(chips) < 3:
                chips.append(value)
    return {
        "id": block_id,
        "headline": rendered.get("headline"),
        "teaser": rendered.get("teaser"),
        "body": rendered.get("body"),
        "chips": chips,
    }


def _debug_block(block_id: str, selection: Mapping[str, Any], rendered: Mapping[str, Any], facts: Mapping[str, Any]) -> Dict[str, Any]:
    primary = selection.get("primary") if isinstance(selection.get("primary"), Mapping) else {}
    color = selection.get("color") if isinstance(selection.get("color"), Mapping) else {}
    fallback_reason = None
    if str(primary.get("signature_id") or "").startswith("fallback_"):
        fallback_reason = "no_matching_signature"
    evidence = list(primary.get("evidence") or [])
    for item in color.get("evidence") or []:
        if item not in evidence:
            evidence.append(item)
    if len(evidence) < 2:
        for item in _fallback_evidence(block_id, facts):
            if item not in evidence:
                evidence.append(item)
    return {
        "id": block_id,
        "engine": "signature",
        "seed": facts.get("seed"),
        "seed_material": facts.get("seed"),
        "selected_template_index": rendered.get("template_index"),
        "template_id": f"{block_id}:{rendered.get('template_index')}",
        "template_variant_id": f"{block_id}:{rendered.get('template_index')}",
        "primary_signature_id": primary.get("signature_id"),
        "score_primary": primary.get("score"),
        "primary_score": primary.get("score"),
        "color_signature_id": color.get("signature_id"),
        "score_color": color.get("score"),
        "color_score": color.get("score"),
        "evidence": evidence,
        "fallback_reason": fallback_reason,
    }


def build_profile_narrative_signature(
    chart: Mapping[str, Any],
    natal_graph: Mapping[str, Any],
    locale: str = "tr",
    include_debug: bool = False,
    seed_key: str | None = None,
) -> Dict[str, Any]:
    if (locale or "tr").lower() != "tr":
        locale = "tr"
    facts = normalize_facts(chart, natal_graph)
    if seed_key:
        facts = dict(facts)
        facts["seed"] = seed_key
    candidates = extract_candidates(facts, SIGNATURE_CATALOG_TR)
    selected = select_by_block(candidates, facts)

    public_blocks = []
    debug_blocks = []
    for block_id in BLOCK_ORDER:
        selection = selected.get(block_id) or _fallback_selection(block_id, facts)
        rendered = _render_block(block_id, selection, str(facts.get("seed") or ""))
        public_blocks.append(_public_block(block_id, rendered, selection))
        if include_debug:
            debug_blocks.append(_debug_block(block_id, selection, rendered, facts))

    payload: Dict[str, Any] = {
        "profile_public": {
            "engine_version": "profile_narrative_v1",
            "blocks": public_blocks,
        }
    }
    if include_debug:
        payload["profile_internal"] = {"blocks_debug": debug_blocks}
    return payload
