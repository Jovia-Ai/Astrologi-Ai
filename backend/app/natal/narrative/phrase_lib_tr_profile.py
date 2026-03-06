from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Mapping, Sequence

from app.narrative.humanize_tr import humanize_tr_text


BLOCK_TEMPLATES_TR: Dict[str, List[Dict[str, str]]] = {
    "identity_aura": [
        {
            "headline": "{copy.headline}",
            "teaser": "{copy.teaser}",
            "body": (
                "{copy.spark} {copy.gift} "
                "{bridge}"
                "Bunu en iyi çalıştırdığında, kendini anlatmak zorunda kalmadan varlığınla yön verirsin; zorlandığında ise aynı gücü kendine yük bindiren bir şeye çevirmeden önce ritmini hatırlamak iyi gelir. "
                "{micro}"
            ),
        },
        {
            "headline": "{copy.headline}",
            "teaser": "{copy.teaser}",
            "body": (
                "{copy.spark} "
                "Netliğin sertlik değil, güven kurma biçimi olduğunda hem hafiflersin hem de etki büyür; burada küçük bir çerçeve kurmak bile tüm günün enerjisini değiştirir. "
                "{copy.watch} "
                "{micro}"
            ),
        },
    ],
    "mind_voice": [
        {
            "headline": "{copy.headline}",
            "teaser": "{copy.teaser}",
            "body": (
                "{copy.spark} "
                "Senin zihin gücün, ayrıntıyı büyütmekten çok niyeti temiz taşımakta parlar; cümle kısaldıkça, sınır netleştikçe, hem sen hem karşı taraf rahatlar. "
                "{copy.gift} "
                "{micro}"
            ),
        },
        {
            "headline": "{copy.headline}",
            "teaser": "{copy.teaser}",
            "body": (
                "{copy.spark} {copy.watch} "
                "En iyi hamlen genelde daha fazla açıklamak değil, tek bir niyet cümlesiyle çerçeveyi kurmak; sonra gerekiyorsa detay açılır. "
                "{micro}"
            ),
        },
    ],
    "drive_rhythm": [
        {
            "headline": "{copy.headline}",
            "teaser": "{copy.teaser}",
            "body": (
                "{copy.spark} "
                "Bu yüzden sende en verimli ritim, küçük bir planla ilk adımı atıp sonra rafine etmek; başladıkça akış açılır, akış açıldıkça motivasyon büyür. "
                "{copy.gift} "
                "{micro}"
            ),
        },
        {
            "headline": "{copy.headline}",
            "teaser": "{copy.teaser}",
            "body": (
                "{copy.spark} {copy.watch} "
                "Bunu çözen şey çoğu zaman ‘mükemmel başlangıç’ değil, ‘ilk çıktı’; ilk çıktı geldiğinde zihin rahatlar ve tempo oturur. "
                "{micro}"
            ),
        },
    ],
    "love_depth": [
        {
            "headline": "{copy.headline}",
            "teaser": "{copy.teaser}",
            "body": (
                "{copy.spark} "
                "İlişkide en çok işe yarayan şey büyük konuşmalar değil, küçük ama tutarlı netlik; çünkü tutarlılık geldiğinde kalbin daha hızlı açılıyor. "
                "{copy.gift} "
                "{micro}"
            ),
        },
        {
            "headline": "{copy.headline}",
            "teaser": "{copy.teaser}",
            "body": (
                "{copy.spark} {copy.watch} "
                "Küçük bir sinyal, temiz bir cümle ve adım adım ilerlemek sende hem güveni hem yakınlığı aynı anda büyütür. "
                "{micro}"
            ),
        },
    ],
    "career_visibility": [
        {
            "headline": "{copy.headline}",
            "teaser": "{copy.teaser}",
            "body": (
                "{copy.spark} "
                "Senin en iyi stratejin büyük bir çıkış yapmak değil, küçük ama düzenli vitrinle iz bırakmak; içeride olgunlaştırıp net bir paketle paylaştığında etki iki katına çıkar. "
                "{copy.gift} "
                "{micro}"
            ),
        },
        {
            "headline": "{copy.headline}",
            "teaser": "{copy.teaser}",
            "body": (
                "{copy.spark} {copy.watch} "
                "Bugün için en iyi hamle, tek bir şeyi görünür kılmak ve ritmi bozmadan devam etmek; süreklilik sende özgüvenin çarpanı. "
                "{micro}"
            ),
        },
    ],
    "home_roots": [
        {
            "headline": "{copy.headline}",
            "teaser": "{copy.teaser}",
            "body": (
                "{copy.spark} "
                "Ev içinde kurduğun küçük ritimler, zihin ve kalbi aynı anda toparlar; bu yüzden dış hedeflere açılman da daha kolay olur. "
                "{copy.gift} "
                "{micro}"
            ),
        },
        {
            "headline": "{copy.headline}",
            "teaser": "{copy.teaser}",
            "body": (
                "{copy.spark} {copy.watch} "
                "Bazen tek bir küçük düzenleme bile bütün günün enerjisini değiştirir; çünkü sende güven biraz ritimle birlikte kurulur. "
                "{micro}"
            ),
        },
    ],
    "luck_creation": [
        {
            "headline": "{copy.headline}",
            "teaser": "{copy.teaser}",
            "body": (
                "{copy.spark} "
                "Şansı büyüten şey beklemek değil, başlatmak; tek bir paylaşım, tek bir teklif ya da küçük bir görünürlük adımı akışı hareketlendirir. "
                "{copy.gift} "
                "{micro}"
            ),
        },
        {
            "headline": "{copy.headline}",
            "teaser": "{copy.teaser}",
            "body": (
                "{copy.spark} {copy.watch} "
                "Senin şansın ‘zemin kurunca’ açılır; bugün tek bir adım, yarın daha büyük bir kapı olabilir. "
                "{micro}"
            ),
        },
    ],
}


def _cleanup(text: str) -> str:
    value = " ".join(str(text or "").split()).strip()
    return humanize_tr_text(value, max_sentences=6)


def _pick_template(templates: Sequence[Dict[str, str]], seed: str) -> tuple[int, Dict[str, str]]:
    if not templates:
        return 0, {"headline": "", "teaser": "", "body": ""}
    index = int(hashlib.sha256(seed.encode("utf-8")).hexdigest(), 16) % len(templates)
    return index, dict(templates[index])


class _SafeDict(dict[str, Any]):
    def __missing__(self, key: str) -> str:
        return ""


def _format_line(template: str, slots: Mapping[str, Any]) -> str:
    local = dict(slots)
    copy_payload = {k: str(v or "") for k, v in dict(local.get("copy") or {}).items()}
    rendered = str(template or "")
    for field in ("headline", "teaser", "spark", "gift", "watch"):
        rendered = rendered.replace(f"{{copy.{field}}}", copy_payload.get(field, ""))
    rendered = rendered.format_map(_SafeDict({key: value for key, value in local.items() if key != "copy"}))
    return _cleanup(rendered)


def render_block_template(
    *,
    block_id: str,
    seed: str,
    slots: Mapping[str, Any],
) -> Dict[str, Any]:
    templates = BLOCK_TEMPLATES_TR.get(block_id) or []
    template_index, template = _pick_template(templates, f"{seed}|{block_id}")
    return {
        "headline": _format_line(template.get("headline", ""), slots),
        "teaser": _format_line(template.get("teaser", ""), slots),
        "body": _format_line(template.get("body", ""), slots),
        "template_index": template_index,
    }
