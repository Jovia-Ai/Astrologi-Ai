from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Mapping

from app.narrative.humanize_tr import humanize_tr_text
from app.natal.narrative.signature_engine import BLOCK_ORDER, normalize_facts


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
            "headline": "Hareket ritmi",
            "teaser": "Sende hız, doğru zamanlama ve yönle birlikte büyüyor.",
            "body": "Bir şeye başladığında yalnızca ilerlemek değil, onu sürdürülebilir kılmak da önemli oluyor. Küçük bir plan, net bir başlangıç ve düzenli ilerleme sende performansı belirgin biçimde artırıyor.",
            "chips": ["Tempo", "İlk Adım", "Süreklilik"],
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
            "headline": "Görünürlük çizgin",
            "teaser": "İş tarafında etki, düzenli görünürlük ve net çıktı ile büyüyor.",
            "body": "Kariyerde seni öne çıkaran şey yalnızca iyi üretmek değil, onu doğru bağlamda görünür kılmak. Küçük ama tutarlı vitrin adımları, sende özgüven ve etkiyi aynı anda büyütüyor.",
            "chips": ["Vitrin", "İşçilik", "Çıktı"],
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
            "headline": "Fırsat ritmin",
            "teaser": "Şans sende çoğu zaman hareketle ve görünür adımla açılıyor.",
            "body": "Beklemekten çok başlatmak sende daha verimli çalışıyor. Küçük bir teklif, kısa bir görünürlük hamlesi ya da somut bir üretim adımı, akışın açılmasını beklediğinden daha hızlı sağlayabiliyor.",
            "chips": ["Fırsat", "Akış", "Başlat"],
        }
    ],
}


def _pick(seed: str, block_id: str, variants: List[Dict[str, Any]]) -> tuple[int, Dict[str, Any]]:
    idx = int(hashlib.sha256(f"{seed}|legacy|{block_id}".encode("utf-8")).hexdigest(), 16) % len(variants)
    return idx, dict(variants[idx])


def _cleanup(value: str, max_sentences: int) -> str:
    return humanize_tr_text(" ".join(str(value or "").split()), max_sentences=max_sentences)


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
