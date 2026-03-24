from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Mapping

from app.narrative.humanize_tr import humanize_tr_text
from app.natal.narrative.signature_engine import BLOCK_ORDER, normalize_facts

PLANET_LABELS_TR = {
    "Sun": "Güneş",
    "Moon": "Ay",
    "Mercury": "Merkür",
    "Venus": "Venüs",
    "Mars": "Mars",
    "Jupiter": "Jüpiter",
    "Saturn": "Satürn",
    "Uranus": "Uranüs",
    "Neptune": "Neptün",
    "Pluto": "Plüton",
    "Fortune": "Fortuna",
}


LEGACY_BLOCKS: Dict[str, List[Dict[str, Any]]] = {
    "identity_aura": [
        {
            "headline": "Dışarıdan ilk his",
            "teaser": "İnsanlar sende önce duruşu, sonra derinliği fark ediyor.",
            "body": "Haritanın genel omurgası, seni ilk anda daha kontrollü ve merkezli gösteriyor. Karar anlarında kendi çizgini koruman ve bulunduğun yerde yön duygusu oluşturman bu blokta belirginleşiyor.",
            "chips": ["Duruş", "Merkez", "İlk İzlenim"],
        }
    ],
    "mind_voice": [
        {
            "headline": "Zihin tonu",
            "teaser": "Düşünme ve ifade biçimin birbirini doğrudan besliyor.",
            "body": "Zihninde netlik oluştuğunda tempo da rahatlıyor. Bu yüzden senin için doğru cümle çoğu zaman doğru yönle aynı yerde birleşiyor; belirsizlik ise önce zihni, sonra ritmi yavaşlatabiliyor.",
            "chips": ["Zihin", "Ton", "Netlik"],
        }
    ],
    "drive_rhythm": [
        {
            "headline": "Gücün en çok nerede belirginleşiyor",
            "teaser": "Sende yetenek, anlamı bir yapıya dönüştürebildiğin yerde parlıyor.",
            "body": "Dağınık olanı toparlama ve sezgisel olanı anlaşılır hale getirme tarafın güçlü. Bir şeyi sadece hissetmekle kalmıyor, ona biçim verip başkalarının da tutabileceği bir düzene oturtmak istiyorsun; bu da seni hem derin düşünen hem de kurabilen biri yapıyor.",
            "chips": ["Anlam", "Yapı", "Kurucu Zihin"],
        }
    ],
    "love_depth": [
        {
            "headline": "Yakınlık biçimin",
            "teaser": "İlişkide güven ve tutarlılık sende belirleyici çalışıyor.",
            "body": "Bağların rahat akması için duygunun sadece hissedilmesi değil, taşınabilir bir zemine oturması da gerekiyor. Temas net ve tutarlı olduğunda sende yakınlık daha sıcak ve daha doğal büyüyor.",
            "chips": ["Güven", "Yakınlık", "Tutarlılık"],
        }
    ],
    "career_visibility": [
        {
            "headline": "Görünür olmadan önce",
            "teaser": "İşin güçlü; ama sen görünürlüğü önce içerde kurup sonra taşırsın.",
            "body": "Kariyerde seni öne çıkaran şey yalnızca iyi üretmek değil, onu içeride iyice olgunlaştırıp kendi adıyla dışarı taşıyabilmen. Baskı arttığında bekleme uzayabilir; yine de en güçlü halin, kalite ile etkinin aynı yerde birleştiği anlarda ortaya çıkıyor.",
            "chips": ["Kalite", "Etki", "Görünürlük"],
        }
    ],
    "home_roots": [
        {
            "headline": "Köklerin",
            "teaser": "İç güven alanın, dış performansını düşündüğünden daha fazla besliyor.",
            "body": "Kendi alanında ritim kurduğunda hem zihnin hem enerjin daha hızlı toparlanıyor. Bu blok, güven duygusunun sende yalnızca duygusal değil, işlevsel bir merkez kurduğunu anlatıyor.",
            "chips": ["Ev", "Güven", "Merkez"],
        }
    ],
    "luck_creation": [
        {
            "headline": "Şansın en kolay nerede açılıyor",
            "teaser": "Sende fırsat çoğu zaman tesadüf gibi değil; emek verdiğin yerde açılıyor.",
            "body": "Bir şeyi gerçekten sahiplenip ona kendi tadını kattığında hayatın da orada karşılık verme eğilimi artıyor. Şansın özellikle yaratım, ifade ve görünür olma cesaretiyle bağlantılı; beklediğinde durgunlaşsa da içinden gelen şeyi ortaya koyduğunda akış hızlanıyor.",
            "chips": ["Yaratım", "Akış", "Canlılık"],
        }
    ],
}


def _pick(seed: str, block_id: str, variants: List[Dict[str, Any]]) -> tuple[int, Dict[str, Any]]:
    idx = int(hashlib.sha256(f"{seed}|legacy|{block_id}".encode("utf-8")).hexdigest(), 16) % len(variants)
    return idx, dict(variants[idx])


def _cleanup(value: str, max_sentences: int) -> str:
    return humanize_tr_text(" ".join(str(value or "").split()), max_sentences=max_sentences)


def _legacy_astro_sources(block_id: str, facts: Mapping[str, Any]) -> list[str]:
    planets = facts.get("planets") if isinstance(facts.get("planets"), Mapping) else {}
    house_rulers = facts.get("house_rulers") if isinstance(facts.get("house_rulers"), Mapping) else {}
    angle_signs = facts.get("angle_signs") if isinstance(facts.get("angle_signs"), Mapping) else {}

    def placement(planet: str) -> str:
        payload = planets.get(planet) if isinstance(planets.get(planet), Mapping) else {}
        house = payload.get("house")
        label = PLANET_LABELS_TR.get(planet, planet)
        if house:
            return f"{label} {house}. ev"
        sign = str(payload.get("sign") or "").strip()
        return f"{label} {sign}".strip()

    def ruler(house: int) -> str:
        payload = house_rulers.get(str(house)) if isinstance(house_rulers.get(str(house)), Mapping) else {}
        pos = payload.get("primary_ruler_pos") if isinstance(payload.get("primary_ruler_pos"), Mapping) else {}
        ruler_name = str(payload.get("primary_ruler") or "").strip()
        ruler_house = pos.get("house")
        if ruler_name and ruler_house:
            return f"{house}. ev yöneticisi {ruler_name} {ruler_house}. ev"
        return ""

    angle_map = {
        "identity_aura": f"Yükselen {angle_signs.get('ASC') or ''}".strip(),
        "mind_voice": placement("Mercury"),
        "drive_rhythm": placement("Mars"),
        "love_depth": placement("Moon"),
        "career_visibility": f"MC {angle_signs.get('MC') or ''}".strip(),
        "home_roots": f"IC {angle_signs.get('IC') or ''}".strip(),
        "luck_creation": placement("Fortune"),
    }
    ruler_house_map = {
        "identity_aura": 1,
        "mind_voice": 3,
        "drive_rhythm": 9,
        "love_depth": 7,
        "career_visibility": 10,
        "home_roots": 4,
    }
    ruler_label = ""
    ruler_house = ruler_house_map.get(block_id)
    if isinstance(ruler_house, int):
        ruler_label = ruler(ruler_house)
    source_labels = [angle_map.get(block_id, ""), ruler_label]
    return [item for item in source_labels if item][:3]


def build_profile_narrative_legacy(
    chart: Mapping[str, Any],
    natal_graph: Mapping[str, Any],
    *,
    include_debug: bool = False,
    seed_key: str | None = None,
    locale: str = "tr",
) -> Dict[str, Any]:
    if (locale or "tr").lower() != "tr":
        locale = "tr"
    facts = normalize_facts(chart, natal_graph)
    seed_material = seed_key or str(facts.get("seed") or "")

    public_blocks: List[Dict[str, Any]] = []
    debug_blocks: List[Dict[str, Any]] = []

    for block_id in BLOCK_ORDER:
        template_index, template = _pick(seed_material, block_id, LEGACY_BLOCKS[block_id])
        public_blocks.append(
            {
                "id": block_id,
                "headline": _cleanup(str(template.get("headline") or ""), 2),
                "teaser": _cleanup(str(template.get("teaser") or ""), 2),
                "body": _cleanup(str(template.get("body") or ""), 5),
                "astro_sources": _legacy_astro_sources(block_id, facts),
                "chips": list(template.get("chips") or [])[:3],
            }
        )
        if include_debug:
            debug_blocks.append(
                {
                    "id": block_id,
                    "engine": "legacy",
                    "template_id": f"legacy:{block_id}:{template_index}",
                    "template_variant_id": f"legacy:{block_id}:{template_index}",
                    "seed_material": seed_material,
                    "primary_signature_id": f"legacy_{block_id}",
                    "color_signature_id": None,
                    "score_primary": None,
                    "score_color": None,
                    "fallback_reason": "legacy_kill_switch",
                    "evidence": [],
                }
            )

    payload: Dict[str, Any] = {
        "profile_public": {
            "engine_version": "profile_narrative_v1",
            "blocks": public_blocks,
        }
    }
    if include_debug:
        payload["profile_internal"] = {"blocks_debug": debug_blocks}
    return payload
