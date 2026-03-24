from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Mapping, Sequence

from app.transit.narrative.chain_explainer_tr import build_chain_explainer_tr

BLOCKED_TOKENS = ("south node", "north node", "lilith", "vertex", "fortune", "chiron")

HOUSE_LABEL_TR = {
    1: "kimlik/benlik",
    2: "deger/gelir",
    3: "zihin/iletisim",
    4: "ev/kok",
    5: "yaraticilik/ifade",
    6: "rutin/saglik",
    7: "iliski/ortaklik",
    8: "derin_bag/donusum",
    9: "anlam/ufuk/genisleme",
    10: "kariyer/gorunurluk",
    11: "topluluk/hedef",
    12: "bilincalti/cozulme",
}

HOUSE_SCENE_TR = {
    3: ["mesaj ve konuşma trafiği", "yazı/not akışı", "yakın çevre koordinasyonu", "ekran-kanal yönetimi"],
    4: ["ev düzeni", "kök güvenlik", "özel alan ritmi", "temel planlar"],
    7: ["ilişki pazarlığı", "sınır ve anlaşma dili", "biz dengesini kurma", "yansıma etkisi"],
    9: ["öğrenme ve uzmanlaşma", "yayınlama-üretim", "yabancı dil/uzak temaslar", "vizyon güncellemesi"],
    11: ["topluluk ağı", "ortak hedef üretimi", "network koordinasyonu", "gelecek planı"],
}

SIGN_STYLE_TR = {
    "virgo": "metod ve iyileştirme",
    "capricorn": "yapı ve otorite",
    "aries": "hız ve ilk hamle",
    "aquarius": "yenilik ve elektrik",
    "pisces": "sezgi ve akış",
    "libra": "denge ve müzakere",
}

ASPECT_LABEL_TR = {
    "conjunction": "kavuşum",
    "square": "kare",
    "opposition": "karşıt",
    "trine": "üçgen",
    "sextile": "altmışlık",
}

ASPECT_ESSENCE_TR = {
    "square": {
        "conflict_core": [
            "Bu açı davranışı zorlayarak kalibrasyon ister.",
            "Yanıt hızlandıkça niyet ve ton ayrışabilir.",
        ],
        "shadow_core": [
            "Savunma refleksi açık veriyi kişisel baskı gibi okutabilir.",
            "Acele karar kısa vadede rahatlatır, uzun vadede maliyet çıkarır.",
        ],
        "upper_core": [
            "Sürtünmeyi metoda çevirdiğinde net güç açılır.",
            "Elektrik burada yön bulursa üretim kalitesi sıçrar.",
        ],
    },
    "trine": {
        "conflict_core": [
            "Akış güçlü; fakat rehavet odağı dağıtabilir.",
            "Kolay giden hat, kritik detayı görünmez kılabilir.",
        ],
        "shadow_core": [
            "Konfor artınca bitmemiş iş ertelenebilir.",
            "Hızlı kazanım hissi ölçümü gevşetebilir.",
        ],
        "upper_core": [
            "Doğal akışı ritimle birleştirirsen kalıcı ivme gelir.",
            "Bu açı yaratıcı sıçramayı somut plana taşımak için ideal.",
        ],
    },
    "conjunction": {
        "conflict_core": [
            "Enerji tek noktada toplanınca yük hissi artabilir.",
            "Aynı anda çok hedef açmak odağı kırar.",
        ],
        "shadow_core": [
            "Yoğunlaşma kontrol takıntısına dönebilir.",
            "Hızlı sonuç isteği çerçeveyi daraltabilir.",
        ],
        "upper_core": [
            "Tek hedefte kaldığında bu açı ciddi ustalık üretir.",
            "Baskıyı sıraya koyduğunda netlik hızdan öne geçer.",
        ],
    },
    "opposition": {
        "conflict_core": [
            "Ayna etkisi iki uç arasında salınım yaratabilir.",
            "Karşı taraf ritmi değiştirirken iç denge test edilir.",
        ],
        "shadow_core": [
            "Projeksiyon artarsa gerçek ihtiyaç görünmez kalır.",
            "Onay arama dürtüsü yön kaymasına yol açabilir.",
        ],
        "upper_core": [
            "Karşıtlığı pazarlığa çevirdiğinde ilişki zekası büyür.",
            "Net soru sormak kutupları ortak dile taşır.",
        ],
    },
    "sextile": {
        "conflict_core": [
            "Fırsat kapısı açık ama pasif kalırsan hız düşer.",
            "Küçük adım atılmadığında ivme sönük kalabilir.",
        ],
        "shadow_core": [
            "Erteleme alışkanlığı fırsatı sıradanlaştırır.",
            "Düşük sürtünme odaksızlığa davet çıkarabilir.",
        ],
        "upper_core": [
            "Mikro hamleleri zincirlediğinde sonuç beklenenden büyük olur.",
            "Bu açı düzenli tekrar ile hızlı kazanım üretir.",
        ],
    },
}

TITLE_BANK = {
    ("square", 3, True): ["Sözün Sınırı", "Netlik Pazarlığı"],
    ("trine", 9, False): ["Kıvılcım Planı", "Yöntem Değişimi"],
    ("trine", 9, True): ["Ayna Kıvılcımı", "Vizyon Kalibrasyonu"],
    ("square", 7, True): ["Ayna Gerilimi", "Sınır Sözleşmesi"],
}

TITLE_FALLBACK = ["Ritim Ayarı", "Yön Güncellemesi", "Temayı Netleştir"]


def build_card_copy(
    card: Mapping[str, Any],
    natal_context_pack: Mapping[str, Any],
    connected_points: Sequence[Mapping[str, Any]],
    event: Mapping[str, Any],
) -> Dict[str, Any]:
    out = dict(card)
    if _is_neptune_square_asc(event):
        return _build_neptune_square_asc_copy(out, event)

    pack = natal_context_pack if isinstance(natal_context_pack, Mapping) else {}
    target = pack.get("target") if isinstance(pack.get("target"), Mapping) else {}
    aspects = pack.get("natal_aspects_focus") if isinstance(pack.get("natal_aspects_focus"), list) else []
    rulership = pack.get("rulership_houses") if isinstance(pack.get("rulership_houses"), list) else []
    house = _safe_int(target.get("house"))
    sign = str(target.get("sign") or "").strip().lower()
    sign_tr = str(target.get("sign_tr") or target.get("sign") or "").strip()
    target_planet = str(target.get("planet") or event.get("natal_point") or "Nokta").strip()
    aspect = str(event.get("aspect") or "").lower().strip()
    axis_hit = str(event.get("natal_point") or "").upper() in {"ASC", "DSC", "MC", "IC"}

    title = title_generator_tr(event, pack, connected_points)
    if title:
        out["title"] = title

    scene = _pick_scene(house, event_seed=_seed(event, "scene"))
    style = SIGN_STYLE_TR.get(sign, "net ritim")
    aspect_essence = ASPECT_ESSENCE_TR.get(aspect, ASPECT_ESSENCE_TR["square"])
    flavor = _flavor_line(aspects)
    lead = _lead_sentence(event, target_planet, house, scene)

    conflict_lines = [lead]
    conflict_lines.extend(aspect_essence["conflict_core"][:2])
    conflict_lines.append(f"Bu tema {sign_tr} tonunda daha çok {style} ihtiyacı doğuruyor.")
    conflict_lines = _dedupe_lines(conflict_lines)

    shadow_lines = list(aspect_essence["shadow_core"][:2])
    if flavor:
        shadow_lines.append(flavor["shadow"])
    shadow_lines = _dedupe_lines(shadow_lines)

    upper_lines = list(aspect_essence["upper_core"][:2])
    upper_lines.append(f"{house or '?'}. Ev hattında bu temayı ustalığa taşıyabilirsin.")
    if flavor:
        upper_lines.append(flavor["upper"])
    if axis_hit:
        upper_lines.append("İlişki aynasından gelen veri kimlik ayarını güçlendirir.")
    upper_lines = _dedupe_lines(upper_lines)

    guidance = _normalize_bullets(_guidance_lines(house, sign_tr, style), minimum=2, fallback=_guidance_fallback(house))
    watch = [
        "Sabitle önce niyeti, sonra hız ver.",
        "Açma aynı anda iki kanal.",
        "Tamamla tek kanaldaki işi, sonra yenisini aç.",
    ]
    watch = _normalize_bullets(watch, minimum=2, fallback=["Önce dur ve nefes al.", "Tek hamle seç ve uygula."])

    out["conflict"] = " ".join(conflict_lines[:4])
    out["shadow"] = " ".join(shadow_lines[:2])
    out["upper"] = " ".join(upper_lines[:4])
    out["guidance"] = guidance[:3]
    out["watch_out"] = watch[:2]
    return _sanitize_blocked(out)


def title_generator_tr(
    event: Mapping[str, Any],
    natal_context_pack: Mapping[str, Any],
    connected_points: Sequence[Mapping[str, Any]],
) -> str:
    _ = connected_points
    target = natal_context_pack.get("target") if isinstance(natal_context_pack.get("target"), Mapping) else {}
    house = _safe_int(target.get("house")) or _safe_int((event.get("houses") or {}).get("transit_in_natal_house"))
    aspect = str(event.get("aspect") or "").lower().strip()
    axis_hit = str(event.get("natal_point") or "").upper() in {"ASC", "DSC", "MC", "IC"}
    options = TITLE_BANK.get((aspect, house or -1, axis_hit)) or TITLE_BANK.get((aspect, house or -1, False)) or TITLE_FALLBACK
    idx = _seed(event, "title") % len(options)
    return options[idx]


def _guidance_lines(house: int | None, sign_tr: str, style: str) -> List[str]:
    return [
        "Yaz tek cümle niyet.",
        "Çıkar önce taslak, sonra gönder.",
        f"Bağla ritmi mini-rutine; {sign_tr} çizgisinde {style} tarafını koru.",
    ]


def _guidance_fallback(house: int | None) -> List[str]:
    return [
        f"Yaz {house or '?'}. Ev odağında tek cümle niyet.",
        "Çıkar taslak, sonra gönder.",
        "Açma aynı anda iki kanal.",
    ]


def _lead_sentence(event: Mapping[str, Any], target_planet: str, house: int | None, scene: str) -> str:
    transit = _planet_tr(str(event.get("transit_body") or "Transit"))
    natal_point = str(event.get("natal_point") or target_planet or "natal nokta").upper()
    return f"{transit} bu sıralar {scene} tarafını hareketlendiriyor; etkisi zamanla {natal_point} hattında daha görünür hale geliyor."


def _is_neptune_square_asc(event: Mapping[str, Any]) -> bool:
    return (
        str(event.get("transit_body") or "").strip().lower() == "neptune"
        and str(event.get("aspect") or "").strip().lower() == "square"
        and str(event.get("natal_point") or "").strip().upper() == "ASC"
    )


def _build_neptune_square_asc_copy(card: Dict[str, Any], event: Mapping[str, Any]) -> Dict[str, Any]:
    out = dict(card)
    derived = out.get("derived_context") if isinstance(out.get("derived_context"), Mapping) else {}
    chain = build_chain_explainer_tr(event, derived if isinstance(derived, Mapping) else {})
    headline_lines = [
        "Kendini anlatırken niyetin net olsa da karşı tarafa bulanık geçiyormuş gibi hissettirebilir.",
        "Mesajı yazıp silmek ya da konuşmadan sonra ben bunu mu dedim diye geri dönmek bu dönemde çok tanıdık.",
    ]
    if chain:
        headline_lines.append(chain)
    headline_text = " ".join(headline_lines[:4])
    big_picture_text = "Bu transit kimliği çözmez; dili kalibre eder ve sezgisel netlik kasını güçlendirir."
    mechanism_text = "Etki iletişim ritminde başlar; sonra duruşuna/kimliğine yansır."
    out["conflict"] = headline_text
    out["headline"] = headline_text
    out["why_now"] = big_picture_text
    out["big_picture"] = big_picture_text
    out["mechanism"] = mechanism_text
    out["shadow"] = (
        "Yanlış anlaşılma korkusu iki uca savurabilir: ya fazla açıklarsın ya da tamamen susarsın."
    )
    out["upper"] = (
        "Nazik ama net sınır kurduğunda sezgi netliğe döner."
    )
    out["guidance"] = [
        "Kısa yazılı netlik kur: niyetin, talebin, sınırın.",
        "Niyet cümlesi yaz: Benim niyetim net anlaşılmak, savunmak değil.",
        "Önce taslakta beklet, sonra gönder.",
    ]
    out["watch_out"] = ["Belirsiz cümleleri çoğaltma.", "Savunmaya geçip tonu sertleştirme."]
    return _sanitize_blocked(out)


def _pick_scene(house: int | None, event_seed: int) -> str:
    options = HOUSE_SCENE_TR.get(house or -1) or ["ana sahne"]
    return options[event_seed % len(options)]


def _flavor_line(aspects: Sequence[Mapping[str, Any]]) -> Dict[str, str] | None:
    if not aspects:
        return None
    top = aspects[0]
    tone = str(top.get("tone") or "").lower()
    with_p = str(top.get("with") or "").strip()
    if tone == "electric":
        return {
            "shadow": f"{with_p} hattındaki elektrik sabırsız kopuş refleksi yaratabilir.",
            "upper": f"{with_p} bağlantısı doğru kurulduğunda yaratıcı sıçrama açar.",
        }
    if tone == "friction":
        return {
            "shadow": f"{with_p} teması iç freni artırıp hamleyi geciktirebilir.",
            "upper": f"{with_p} sürtünmesini metoda çevirirsen net güç çıkar.",
        }
    if tone == "flow":
        return {
            "shadow": f"{with_p} akışı rehavete kayarsa fırsat dağılabilir.",
            "upper": f"{with_p} akışını düzenle birleştirince ivme kalıcı olur.",
        }
    return {
        "shadow": f"{with_p} hattı görünmeyen dağınıklığı tetikleyebilir.",
        "upper": f"{with_p} hattını netlediğinde odak hızlı toplanır.",
    }


def _rulership_line(rulership_houses: Sequence[Mapping[str, Any]]) -> str:
    houses = []
    for entry in rulership_houses:
        house = _safe_int(entry.get("house"))
        if house and house not in houses:
            houses.append(house)
    if not houses:
        return ""
    if len(houses) == 1:
        h = houses[0]
        return f"İkincil yankı {h}. Ev ({HOUSE_LABEL_TR.get(h, 'genel')}) alanına uzanabilir."
    first, second = houses[0], houses[1]
    return (
        f"İkincil yankı {first}. Ev ({HOUSE_LABEL_TR.get(first, 'genel')}) ve "
        f"{second}. Ev ({HOUSE_LABEL_TR.get(second, 'genel')}) alanlarına uzanabilir."
    )


def _sanitize_blocked(card: Dict[str, Any]) -> Dict[str, Any]:
    for field in ("conflict", "shadow", "upper", "extra_line", "title"):
        value = str(card.get(field) or "")
        lowered = value.lower()
        for token in BLOCKED_TOKENS:
            if token in lowered:
                value = value.replace(token, "")
                value = value.replace(token.title(), "")
        card[field] = " ".join(value.split())
    for field in ("guidance", "watch_out"):
        values = card.get(field) if isinstance(card.get(field), list) else []
        cleaned = []
        for item in values:
            text = str(item or "")
            for token in BLOCKED_TOKENS:
                text = text.replace(token, "").replace(token.title(), "")
            text = " ".join(text.split())
            if text:
                cleaned.append(text)
        card[field] = cleaned
    return card


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _dedupe_lines(lines: Sequence[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for line in lines:
        text = " ".join(str(line or "").split()).strip()
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        if text[-1] not in ".!?":
            text += "."
        out.append(text)
    return out


def _normalize_bullets(items: Sequence[str], *, minimum: int, fallback: Sequence[str]) -> List[str]:
    out: List[str] = []
    for item in items:
        text = _bullet_line(item)
        if text:
            out.append(text)
    for item in fallback:
        if len(out) >= minimum:
            break
        text = _bullet_line(item)
        if text and text not in out:
            out.append(text)
    if len(out) < minimum:
        hard = ["Yaz tek cümle niyet.", "Çıkar taslak, sonra gönder."]
        for item in hard:
            if len(out) >= minimum:
                break
            if item not in out:
                out.append(item)
    return out


def _bullet_line(text: str, max_words: int = 14) -> str:
    raw = " ".join(str(text or "").split()).strip()
    if not raw:
        return ""
    raw = raw.strip(" .")
    if not raw:
        return ""
    words = raw.split()
    if len(words) > max_words:
        words = words[:max_words]
    candidate = " ".join(words).strip()
    if not candidate:
        return ""
    lead = words[0].lower()
    if lead not in {
        "yaz",
        "çıkar",
        "cikar",
        "bağla",
        "bagla",
        "sabitle",
        "açma",
        "acma",
        "tamamla",
        "koru",
        "ölç",
        "olc",
        "planla",
        "seç",
        "sec",
    }:
        return ""
    if len(words) < 3:
        return ""
    if candidate[-1] not in ".!?":
        candidate += "."
    return candidate


def _seed(event: Mapping[str, Any], key: str) -> int:
    raw = "|".join(
        [
            str(event.get("event_id") or ""),
            str(event.get("transit_body") or ""),
            str(event.get("aspect") or ""),
            str(event.get("natal_point") or ""),
            key,
        ]
    )
    return int(hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8], 16)


def _planet_tr(name: str) -> str:
    mapping = {
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
    token = str(name or "").strip().lower()
    return mapping.get(token, str(name or ""))
