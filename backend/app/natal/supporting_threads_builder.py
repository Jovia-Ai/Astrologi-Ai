from __future__ import annotations

import hashlib
import re
from typing import Any, Dict, List, Mapping

from app.narrative.editorial_render_policy import editorialize_micro, select_rhythm_family
from app.natal.natal_graph import TRADITIONAL_RULERS

SIGN_VIBE_TR = {
    "Aries": "direkt ve atak",
    "Taurus": "sakin ve sağlam",
    "Gemini": "meraklı ve hareketli",
    "Cancer": "koruyucu ve duyarlı",
    "Leo": "sıcak ve görünür",
    "Virgo": "ölçülü ve düzenli",
    "Libra": "uyumlu ve dengeli",
    "Scorpio": "derin ve kontrollü",
    "Sagittarius": "açık ve vizyoner",
    "Capricorn": "ciddi ve hedef odaklı",
    "Aquarius": "bağımsız ve özgün",
    "Pisces": "sezgisel ve yumuşak",
}

SIGN_TONE_TR = {
    "Aries": "hızlı, dürtüsel ve mücadeleci",
    "Taurus": "sabit, dayanıklı ve inatçı",
    "Gemini": "hareketli, meraklı ve dağınık",
    "Cancer": "duygusal, korumacı ve çekingen",
    "Leo": "görünür, sıcak ve gururlu",
    "Virgo": "ölçülü, seçici ve eleştirel",
    "Libra": "uyum arayan, tartan ve kararsız",
    "Scorpio": "yoğun, kontrollü ve kuşkulu",
    "Sagittarius": "açık, cesur ve risk alan",
    "Capricorn": "kontrollü, ciddi ve dayanıklı",
    "Aquarius": "bağımsız, mesafeli ve sıra dışı",
    "Pisces": "sezgisel, geçirgen ve dalgalı",
}

SIGN_LABEL_TR = {
    "Aries": "Koç",
    "Taurus": "Boğa",
    "Gemini": "İkizler",
    "Cancer": "Yengeç",
    "Leo": "Aslan",
    "Virgo": "Başak",
    "Libra": "Terazi",
    "Scorpio": "Akrep",
    "Sagittarius": "Yay",
    "Capricorn": "Oğlak",
    "Aquarius": "Kova",
    "Pisces": "Balık",
}

SIGN_LOCATIVE_TR = {
    "Aries": "Koç'ta",
    "Taurus": "Boğa'da",
    "Gemini": "İkizler'de",
    "Cancer": "Yengeç'te",
    "Leo": "Aslan'da",
    "Virgo": "Başak'ta",
    "Libra": "Terazi'de",
    "Scorpio": "Akrep'te",
    "Sagittarius": "Yay'da",
    "Capricorn": "Oğlak'ta",
    "Aquarius": "Kova'da",
    "Pisces": "Balık'ta",
}

PLANET_LABEL_TR = {
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
}

HOUSE_ARENA_TR = {
    1: "benlik ve duruş",
    2: "özdeğer ve kaynaklar",
    3: "söz, ton ve karar dili",
    4: "ev ve iç güven",
    5: "yaratıcılık ve ifade",
    6: "günlük ritim ve düzen",
    7: "yakın ilişkiler",
    8: "güven, mahremiyet ve derinlik",
    9: "anlam, inanç ve ufuk",
    10: "kariyer ve görünürlük",
    11: "network, ekip ve sosyal bağlam",
    12: "perde arkası ve iç dünya",
}

_MIND_MICROS = [
    "Bir cümleyi göndermeden önce içinden bir kez daha tartarsın.",
    "Bir konuşmanın ardından tonu daha da sadeleştirmek istersin.",
    "Yanlış anlaşılma ihtimali doğduğunda kelimeleri içeride hemen yeniden dizersin.",
]

_REL_MICROS = [
    "Yakınlık ciddileştiğinde önce içini yoklar, sonra açılırsın.",
    "Güven geldiğinde sıcaklığın bir anda daha görünür olur.",
    "Belirsizlik uzadığında kalbin çabuk yorulur.",
]

_CAREER_MICROS = [
    "Bir şeyi tam sahiplenmeden ortaya koymak istemezsin.",
    "Görünür olmadan önce içerden bir kez daha ölçüp tartarsın.",
    "İçinde olgunlaşan şeyi doğru anda dışarı çıkarırsın.",
]

_RELATIONSHIP_SIGN_OPENING_TR = {
    "Aries": {
        "need": "yanında fazla dolanmadan açık olabildiğin bir bağ",
        "line": "7. evin Koç olduğu için ilişkide netlik, cesaret ve doğrudanlık senin için çok şey belirliyor.",
        "gate": "Duygu varsa bunun hareketi de olsun istiyorsun; sürekli beklemek ya da ölçmek seni çabuk yorabiliyor.",
    },
    "Taurus": {
        "need": "yanında gerçekten gevşeyebildiğin, yavaşlayabildiğin bir bağ",
        "line": "7. evin Boğa olduğu için ilişkide istikrar, güven ve bedensel rahatlık senin için çok belirleyici.",
        "gate": "Zemin oynamıyorsa açılıyorsun; zemin kayıyorsa hemen mesafe koyabiliyorsun.",
    },
    "Gemini": {
        "need": "yanında hem rahat konuşabildiğin hem de zihninin canlı kaldığı bir bağ",
        "line": "7. evin İkizler olduğu için ilişkide söz, merak ve zihinsel akış senin için duygunun kendisi kadar önemli.",
        "gate": "Cümle tıkanıyorsa ya da iletişim ağırlaşıyorsa bağın ritmi sende hemen düşebiliyor.",
    },
    "Cancer": {
        "need": "yanında gerçekten yumuşayabildiğin bir bağ",
        "line": "7. evin Yengeç olduğu için sen aşkı biraz ev gibi yaşıyorsun.",
        "gate": "Güven yoksa, duygusal sıcaklık yoksa ve ait hissetmiyorsan kolay kolay tam açılmıyorsun.",
    },
    "Leo": {
        "need": "yanında hem sevildiğini hem de içtenlikle seçildiğini hissedebildiğin bir bağ",
        "line": "7. evin Aslan olduğu için ilişkide sıcaklık, görünür sevgi ve açık ilgi senin için çok şey anlatıyor.",
        "gate": "Kalpten gelen bir ışık yoksa bağ sende kolay kolay tam canlanmıyor.",
    },
    "Virgo": {
        "need": "yanında hem huzur bulduğun hem de hayatın daha düzenli aktığı bir bağ",
        "line": "7. evin Başak olduğu için ilişkide özen, tutarlılık ve küçük şeylere dikkat edilmesi senin için önemli.",
        "gate": "Dağınıklık, belirsizlik ya da sürekli açıkta kalan detaylar sende bağı yorabiliyor.",
    },
    "Libra": {
        "need": "yanında hem yakınlık hem de karşılıklılık hissedebildiğin bir bağ",
        "line": "7. evin Terazi olduğu için ilişkide denge, zarafet ve karşılıklı istek senin için çok belirleyici.",
        "gate": "Tek taraflılık ya da kaba bir ton varsa içten içe hızla geri çekilebiliyorsun.",
    },
    "Scorpio": {
        "need": "yanında hem güvende hem de gerçekten derinde hissedebildiğin bir bağ",
        "line": "7. evin Akrep olduğu için ilişkide yoğunluk, dürüstlük ve duygusal çıplaklık senin için önemli.",
        "gate": "Yüzeyde kalan bağlar sende kolay kolay yer etmiyor.",
    },
    "Sagittarius": {
        "need": "yanında hem yakınlık hem de içinin genişlediğini hissedebildiğin bir bağ",
        "line": "7. evin Yay olduğu için ilişkide açıklık, dürüstlük ve ortak ufuk duygusu seni çok etkiliyor.",
        "gate": "Daraltan, boğan ya da sürekli hesap yapan ilişkiler sende çabuk yorulma yaratabiliyor.",
    },
    "Capricorn": {
        "need": "yanında hem güven hem de omurga hissedebildiğin bir bağ",
        "line": "7. evin Oğlak olduğu için ilişkide ciddiyet, güvenilirlik ve uzun vadeli duruş senin için önemli.",
        "gate": "Duygu varsa bunun ağırlığı da olsun istiyorsun; hafiflik bazen sende güvensizlik yaratabiliyor.",
    },
    "Aquarius": {
        "need": "yanında hem yakınlık hem de kendin kalabildiğin bir bağ",
        "line": "7. evin Kova olduğu için ilişkide özgürlük, zihinsel alan ve farklılık payı seni çok etkiliyor.",
        "gate": "Üzerine fazla gelinen ya da kalıba sokan bağlar sende hızla mesafe yaratabiliyor.",
    },
    "Pisces": {
        "need": "yanında hem duygusal akış hem de ruhsal bir yakınlık hissedebildiğin bir bağ",
        "line": "7. evin Balık olduğu için ilişkide sezgi, merhamet ve görünmeyen bağlar senin için önemli.",
        "gate": "Ruhsuz, kuru ya da fazla sert hissettiren ilişkiler sende kolay kolay derinleşmiyor.",
    },
}

_RELATIONSHIP_RULER_SIGN_NEED_TR = {
    "Aries": "Kalbinde yer açtığında sevginin biraz daha cesur, direkt ve beklemeye tahammülsüz akmasını istiyorsun.",
    "Taurus": "Kalbinde yer açtığında sevginin daha somut, sakin ve güven veren bir şekilde görünmesini istiyorsun.",
    "Gemini": "Kalbinde yer açtığında sevginin konuşulabilir, canlı ve hareketli kalmasını istiyorsun.",
    "Cancer": "Kalbinde yer açtığında sevginin koruyucu, yumuşak ve duygusal olarak güven veren bir hale gelmesini istiyorsun.",
    "Leo": "Sen sadece sevilmek istemiyorsun; özel hissetmek, seçildiğini görmek ve sevginin görünür olmasını da istiyorsun.",
    "Virgo": "Kalbinde yer açtığında sevginin özenli, dikkatli ve küçük jestlerle hissedilir olmasını istiyorsun.",
    "Libra": "Kalbinde yer açtığında sevginin dengeli, zarif ve karşılıklı akmasını istiyorsun.",
    "Scorpio": "Kalbinde yer açtığında sevginin yüzeyde kalmasını değil, gerçek ve dönüştürücü olmasını istiyorsun.",
    "Sagittarius": "Kalbinde yer açtığında sevginin açık, dürüst ve ferah hissettiren bir tonda akmasını istiyorsun.",
    "Capricorn": "Kalbinde yer açtığında sevginin ciddi, güvenilir ve omurgalı bir şekilde görünmesini istiyorsun.",
    "Aquarius": "Kalbinde yer açtığında sevginin alan bırakan, özgür ama yine de gerçek kalan bir tonda akmasını istiyorsun.",
    "Pisces": "Kalbinde yer açtığında sevginin sezgisel, içten ve yumuşatan bir şekilde hissedilmesini istiyorsun.",
}

_SECTION_SLOT = {
    "mind_system": "secondary_balancing_line",
    "relationships": "relational_line",
    "career_visibility": "work_visibility_line",
}

_PRIMITIVE_CHIP_TR = {
    "self_definition": "Kimlik",
    "visible_presence": "Görünürlük",
    "inner_structure": "İç Yapı",
    "originality_drive": "Özgünlük",
    "big_picture_vision": "Vizyon",
    "tone_sensitivity": "Ton Hassasiyeti",
    "systems_thinking": "Sistem Zihni",
    "inner_critic": "İç Standart",
    "push_pull_drive": "İtme-Çekme",
    "methodical_drive": "Yöntem",
    "mental_structuring": "Zihinsel Düzen",
    "intimacy_depth": "Derin Yakınlık",
    "relational_security": "İlişki Güveni",
    "graceful_affection": "Yumuşak Bağ",
    "transformative_bonding": "Dönüştürücü Bağ",
    "emotional_threshold": "Güven Eşiği",
    "public_refinement": "Rafine Etki",
    "visibility_sensitivity": "Görünürlük Eşiği",
    "backstage_creation": "Perde Arkası",
    "recharge_through_home": "İç Toparlanma",
    "family_self_reliance": "Kendi Zemini",
    "creation_luck": "Yaratım Akışı",
    "network_luck": "Çevre Akışı",
    "meaningful_expansion": "Anlamlı Büyüme",
}


def _house_ruler(graph: Mapping[str, Any], house: int) -> Mapping[str, Any]:
    house_rulers = graph.get("house_rulers")
    if not isinstance(house_rulers, Mapping):
        return {}
    raw = house_rulers.get(str(house))
    return raw if isinstance(raw, Mapping) else {}


def _planet_positions(planets: List[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for item in planets:
        if not isinstance(item, Mapping):
            continue
        name = str(item.get("planet") or "").strip()
        if not name:
            continue
        out[name] = dict(item)
    return out


def _planet_pos(planet: str, planets_map: Mapping[str, Mapping[str, Any]]) -> Mapping[str, Any]:
    raw = planets_map.get(planet)
    return raw if isinstance(raw, Mapping) else {}


def _seed_base(chart_data: Mapping[str, Any], asc_sign: str, mc_sign: str) -> str:
    birth_dt = (
        str(chart_data.get("birth_datetime") or "").strip()
        or str(chart_data.get("birthDateTime") or "").strip()
        or str(chart_data.get("metadata", {}).get("birth_datetime") or "").strip()
    )
    raw = f"{birth_dt}|{asc_sign}|{mc_sign}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _to_house(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _pick_variant(options: List[str], seed: str) -> str:
    if not options:
        return ""
    index = int(hashlib.sha256(seed.encode("utf-8")).hexdigest(), 16) % len(options)
    return options[index]


def _cleanup_text(text: str) -> str:
    value = str(text or "").replace("/", " ").replace("(", "").replace(")", "")
    value = re.sub(r"\s+", " ", value).strip()
    parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", value) if part.strip()]
    seen: set[str] = set()
    deduped: List[str] = []
    for part in parts:
        key = re.sub(r"[^a-z0-9çğıöşü]+", "", part.lower())
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(part)
    return " ".join(deduped).strip()


def _join_body_micro(body: str, micro: str) -> str:
    return _cleanup_text(f"{body} {micro}")


def _split_sentences(text: str) -> List[str]:
    raw = str(text or "").strip()
    if not raw:
        return []
    protected = re.sub(r"(\b\d{1,2})\.\s*(ev\w*)\b", r"\1__EV_DOT__ \2", raw, flags=re.IGNORECASE)
    parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", protected) if part.strip()]
    return [part.replace("__EV_DOT__", ".").strip() for part in parts]


def _semantic_tokens(text: str) -> set[str]:
    stopwords = {
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
        "sen",
        "sende",
        "senin",
        "şey",
        "olan",
    }
    return {
        token
        for token in re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ]+", str(text or "").lower())
        if len(token) >= 3 and token not in stopwords
    }


def _semantic_overlap(a: str, b: str) -> float:
    left = _semantic_tokens(a)
    right = _semantic_tokens(b)
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _build_thread_paragraph(one_liner: str, body: str, micro: str) -> str:
    sentences: List[str] = []
    lead = str(one_liner or "").strip()
    body_sentences = _split_sentences(body)
    if lead and (not body_sentences or _semantic_overlap(lead, body_sentences[0]) < 0.7):
        sentences.append(lead)
    for sentence in body_sentences:
        if any(_semantic_overlap(sentence, prior) >= 0.78 for prior in sentences):
            continue
        sentences.append(sentence)
        if len(sentences) >= 4:
            break
    if len(sentences) < 4 and micro and all(_semantic_overlap(micro, prior) < 0.74 for prior in sentences):
        sentences.append(micro)
    return _cleanup_text(" ".join(sentences[:4]))


def _family_line(options: Mapping[str, str], family: str, fallback: str) -> str:
    return str(options.get(family) or fallback).strip()


def _spine_line(master_selector: Mapping[str, Any] | None, slot: str) -> Mapping[str, Any]:
    identity_spine = (
        master_selector.get("identity_spine")
        if isinstance(master_selector, Mapping) and isinstance(master_selector.get("identity_spine"), Mapping)
        else {}
    )
    payload = identity_spine.get(slot)
    return payload if isinstance(payload, Mapping) else {}


def _spine_chip_labels(line: Mapping[str, Any]) -> list[str]:
    labels: list[str] = []
    for primitive_id in line.get("source_primitives") or []:
        label = _PRIMITIVE_CHIP_TR.get(str(primitive_id))
        if label and label not in labels:
            labels.append(label)
        if len(labels) >= 2:
            break
    return labels


def _spine_sentence(slot: str, line: Mapping[str, Any]) -> str:
    labels = _spine_chip_labels(line)
    phrase = " ve ".join(labels[:2]) if labels else str(line.get("label") or "").strip()
    if not phrase:
        return ""
    if slot == "secondary_balancing_line":
        return f"Burada asıl çalışan çizgi, {phrase.lower()} tarafını düzen kurdukça daha net hissetmen."
    if slot == "relational_line":
        return f"Bu alanda merkezde duran şey, {phrase.lower()} çizgisinin güven geldikçe açılması."
    if slot == "work_visibility_line":
        return f"Görünür tarafta fark yaratan şey, {phrase.lower()} hattının hazırlıkla birlikte güçlenmesi."
    if slot == "shadow_protection_line":
        return f"Zorlandığında seni toparlayan çizgi, {phrase.lower()} tarafının içerde zemin kurması."
    return f"Bu başlıkta merkezde duran tema, {phrase.lower()} çizginin daha belirgin çalışması."


def _apply_spine_to_sections(
    sections: List[Dict[str, Any]],
    *,
    master_selector: Mapping[str, Any] | None,
) -> List[Dict[str, Any]]:
    aligned: List[Dict[str, Any]] = []
    for section in sections:
        if not isinstance(section, Mapping):
            continue
        item = dict(section)
        slot = _SECTION_SLOT.get(str(item.get("id") or ""))
        line = _spine_line(master_selector, slot or "")
        if not slot or not line:
            aligned.append(item)
            continue
        spine_sentence = _spine_sentence(slot, line)
        body = str(item.get("body") or "").strip()
        if spine_sentence and _semantic_overlap(body, spine_sentence) < 0.48:
            item["body"] = _cleanup_text(f"{body} {spine_sentence}")
        chips = list(item.get("chips") or [])
        for label in _spine_chip_labels(line):
            if label not in chips:
                chips.append(label)
            if len(chips) >= 4:
                break
        item["chips"] = chips[:4]
        aligned.append(item)
    return aligned


def _sign_label(sign: str) -> str:
    return SIGN_LABEL_TR.get(str(sign or "").strip(), str(sign or "").strip())


def _planet_label(planet: str) -> str:
    return PLANET_LABEL_TR.get(str(planet or "").strip(), str(planet or "").strip())


def _house_phrase(house: int) -> str:
    return f"{house}. ev"


def _house_locative(house: int) -> str:
    return f"{house}. evde"


def _sign_locative(sign: str) -> str:
    return SIGN_LOCATIVE_TR.get(str(sign or "").strip(), "")


def _sign_vibe(sign: str) -> str:
    return SIGN_VIBE_TR.get(str(sign or "").strip(), "kendine özgü")


def _sign_tone(sign: str) -> str:
    return SIGN_TONE_TR.get(str(sign or "").strip(), "kendine özgü")


def _relationship_opening_block(dsc_sign: str) -> str:
    sign_label = _sign_label(dsc_sign)
    payload = _RELATIONSHIP_SIGN_OPENING_TR.get(dsc_sign) or {}
    need = str(payload.get("need") or "yanında gerçekten rahatlayabildiğin bir bağ").strip()
    line = str(payload.get("line") or f"7. evin {sign_label} olduğu için yakınlığı kendine özgü bir tonda yaşıyorsun.").strip()
    gate = str(payload.get("gate") or "Güven oluşmadan tam açılman kolay olmuyor.").strip()
    return _cleanup_text(
        f"Sen ilişkide sadece biriyle olmak istemiyorsun. "
        f"Senin aradığın şey, {need}. "
        f"{line} "
        f"{gate}"
    )


def _relationship_house_block(*, ruler_label: str, r7_house: int) -> str:
    if r7_house == 8:
        return _cleanup_text(
            f"Birine bağlandığında bunu hafif yaşamıyorsun. "
            "Karşındaki insan bir noktadan sonra yalnızca hoşlandığın biri olmaktan çıkıp iç dünyanda yer eden birine dönüşebiliyor. "
            f"{ruler_label} {_house_locative(r7_house)} olduğu için sen bağ kurarken yüzeyde kalmıyorsun. "
            "Ya gerçekten giriyorsun, ya da zaten hiç girmemiş oluyorsun."
        )
    if r7_house == 3:
        return _cleanup_text(
            "Birine bağlandığında bunu sadece kalbinle değil, zihninle de yaşıyorsun. "
            f"{ruler_label} {_house_locative(r7_house)} olduğu için bağın ritmi çoğu zaman sözle, tonla ve mesaj trafiğiyle kuruluyor. "
            "Yarım cümleler, açıkta kalan meseleler ve belirsiz konuşmalar sende gereğinden fazla yük yaratabiliyor. "
            "Senin için yakınlık biraz da konuşulabilir olmak demek."
        )
    if r7_house == 11:
        return _cleanup_text(
            "Birine bağlandığında mesele sadece aranızdaki duygu olmuyor; aynı tarafta olup olmadığınız da önem kazanıyor. "
            f"{ruler_label} {_house_locative(r7_house)} olduğu için güven sende çoğu zaman arkadaşlık, ekip ve ortak hedef üzerinden kuruluyor. "
            "Bir bağ sosyal zeminde rahatladığında kalbin de daha kolay açılıyor. "
            "Bu yüzden bir ilişkinin yalnızca özel değil, aynı zamanda yönü olan bir tarafı da olsun istiyorsun."
        )
    return _cleanup_text(
        f"Birine bağlandığında bunu hafif yaşamıyorsun. "
        f"{ruler_label} {_house_locative(r7_house)} olduğu için ilişki sende en çok {_house_phrase(r7_house)} temaları üzerinden derinleşiyor. "
        "Bu yüzden bir bağ ya gerçekten içeri giriyor ya da sende yüzeyde kalıyor. "
        "Senin için yakınlık, biraz da o ilişkinin hayatında nereye dokunduğuyla ilgili."
    )


def _relationship_ruler_sign_block(*, r7: str, r7_sign: str) -> str:
    ruler_label = _planet_label(r7)
    sign_label = _sign_label(r7_sign)
    locative = _sign_locative(r7_sign)
    need = _RELATIONSHIP_RULER_SIGN_NEED_TR.get(r7_sign) or (
        "Sen sadece sevilmek istemiyorsun; sevginin sende nasıl hissettirdiği de en az bunun kadar önemli."
    )
    return _cleanup_text(
        f"{ruler_label} {locative if locative else sign_label} olduğu için ilişkide kalbinin aradığı ton daha görünür hale geliyor. "
        f"{need} "
        "Sessiz, belirsiz ya da ne hissettirdiği anlaşılmayan sevgiler sende kolay kolay tam karşılık bulmuyor."
    )


def _relationship_strength_block(*, dsc_sign: str, r7_house: int) -> str:
    if dsc_sign == "Cancer":
        return _cleanup_text(
            "Sen sevdiğinde cömert, koruyan ve duygusal olarak alan açan birine dönüşebiliyorsun. "
            "Karşındaki insanın ihtiyacını, tonunu ve geri çekildiği yeri çabuk fark edebiliyorsun. "
            "Tam da bu yüzden ilişkide karşı tarafın mesafesi seni normalden daha fazla yaralayabiliyor. "
            "Çünkü sen bağa yalnızca ilginle değil, kalbinden yatırım yaparak giriyorsun."
        )
    return _cleanup_text(
        "Sen sevdiğinde ilişkinin içine yalnızca ilgi değil, ciddi bir dikkat de koyuyorsun. "
        "Karşındaki insanın tonunu, mesafesini ve gerçekten orada olup olmadığını kolay fark edebiliyorsun. "
        "Bu sana ilişkide güçlü bir sezgi veriyor. "
        "Ama aynı hassasiyet, karşı tarafın yarım kalışını da sende daha büyük hissettirebiliyor."
    )


def _relationship_shadow_block(*, r7_house: int) -> str:
    if r7_house == 8:
        return _cleanup_text(
            "Buradaki hassas nokta şu: sen bazen bağ kurunca sadece sevmiyorsun, o bağın yükünü de taşımaya başlıyorsun. "
            "Karşındakini anlamaya, çözmeye ve aradaki bağı korumaya çok emek verebiliyorsun. "
            "Bu yüzden kaybetme korkusu, açıkta kalma korkusu ya da 'ben bu kadar açıldım ya karşılığı yoksa?' hissi kolay tetiklenebiliyor. "
            "Ve bunu her zaman dışarı göstermeyebilirsin; dışarıda güçlü dururken içeride çok daha derin etkileniyor olabiliyorsun."
        )
    return _cleanup_text(
        "Buradaki hassas nokta şu: sen bazen bağ kurunca sadece sevmiyor, o bağın düzenini de içinde taşımaya başlıyorsun. "
        "Karşı tarafın tonunu, mesafesini ya da kararsızlığını fazlasıyla üstlenebiliyorsun. "
        "Bu yüzden bir noktadan sonra yalnızca üzülmüyor, aynı zamanda aradaki yükü de tek başına taşımış gibi hissedebiliyorsun. "
        "Dışarıdan kontrollü görünsen bile içeride çok daha derin etkileniyor olabiliyorsun."
    )


def _relationship_growth_block() -> str:
    return _cleanup_text(
        "Senin ilişkide öğrenmeye geldiğin şey şu olabilir: derin bağ kurmak için kendini tüketmen gerekmiyor. "
        "Yoğun sevmen, çok önemsemen ve ciddi bağlanman güzel; ama gerçek bağın illa kriz, kaygı ya da duygusal savaşla kanıtlanması gerekmiyor. "
        "Seni gerçekten besleyen bağ, seni yoran değil; seni sakinleştiren, güven veren ve kalbini yumuşatan bağ."
    )


def _relationship_caption_block(*, dsc_sign: str, r7_house: int) -> str:
    sign_label = _sign_label(dsc_sign)
    return _cleanup_text(
        f"Sen ilişkide sadece aşk aramıyorsun. "
        f"7. evin {sign_label} ve yöneticinin {_house_locative(r7_house)} olması yüzünden, birinin yanında gerçekten içeri alınmayı arıyorsun. "
        "Sevilmekten fazlasını; seçilmek, önemsenmek ve gerçekten tutulmak istiyorsun. "
        "Bu seni hassas yapabiliyor olabilir ama aynı zamanda çok derin, çok sadık ve çok gerçek bir sevme biçimi veriyor."
    )


def _relationship_detail_blocks(
    *,
    dsc_sign: str,
    r7: str,
    r7_sign: str,
    r7_house: int,
) -> List[str]:
    ruler_label = _planet_label(r7)
    return [
        _relationship_opening_block(dsc_sign),
        _relationship_house_block(ruler_label=ruler_label, r7_house=r7_house),
        _relationship_ruler_sign_block(r7=r7, r7_sign=r7_sign),
        _relationship_strength_block(dsc_sign=dsc_sign, r7_house=r7_house),
        _relationship_shadow_block(r7_house=r7_house),
        _relationship_growth_block(),
        _relationship_caption_block(dsc_sign=dsc_sign, r7_house=r7_house),
    ]


def _core_mind_body(
    *,
    asc_sign: str,
    asc_ruler: str,
    asc_house: int,
    loop_signature: str,
) -> str:
    sign_label = _sign_label(asc_sign)
    ruler_label = _planet_label(asc_ruler)
    arena = HOUSE_ARENA_TR.get(asc_house, "günlük akış")
    loop_line = ""
    if loop_signature:
        loop_line = (
            " Karar, ifade ve hareketin birbirini tetiklemesi yüzünden bazen zihnin bir cümleyi "
            "söylemeden önce birkaç kez tartabiliyor."
        )
    if asc_house in {3, 6}:
        return _cleanup_text(
            f"Netlik sende kontrol değil güven meselesi; Yükselen {sign_label} belirsizliği uzatmayı sevmez "
            f"ve yöneticin {ruler_label}'ün {_house_phrase(asc_house)} vurgusu bunu en çok söz, ton ve karar "
            f"anlarında görünür kılar, bu yüzden bazen bir cümleyi kurmadan önce içinden ölçüp biçmen ya da "
            f"konuşma bittikten sonra ne demek istediğini zihninde yeniden toplaman fazla düşünmekten çok "
            f"netlik aradığını gösterir.{loop_line}"
        )
    if asc_house == 12:
        return _cleanup_text(
            f"Netlik sende kontrol değil güven meselesi; Yükselen {sign_label} dışarıda ölçülü dururken "
            f"yöneticin {ruler_label}'ün {_house_phrase(asc_house)} vurgusu kararlarını önce içeride olgunlaştırmana "
            f"neden olur, bu yüzden hızlı cevap vermek yerine içinden toparlayıp sonra konuşmak senin için "
            f"kaçınma değil kalite filtresidir."
        )
    if asc_house == 11:
        return _cleanup_text(
            f"Netlik sende yalnız kalınca değil, bağlam netleşince geliyor; Yükselen {sign_label} belirsizliği "
            f"uzatmayı sevmez ve yöneticin {ruler_label}'ün {_house_phrase(asc_house)} vurgusu rolünü en çok "
            f"ekip, çevre ve ortak hedef içinde görünür kılıyor, bu yüzden kiminle ve ne için ilerlediğini "
            f"bildiğinde zihnin de çok daha hızlı toparlanıyor."
        )
    return _cleanup_text(
        f"Netlik sende kontrol değil güven meselesi; Yükselen {sign_label} belirsizliği uzatmayı sevmez ve "
        f"yöneticin {ruler_label}'ün {_house_phrase(asc_house)} vurgusu bunu en çok {arena} alanında görünür "
        f"kılar, bu yüzden kararlarını içinden tartıp sağlam bir cümleye dönüştürdüğünde hem ritmin hem "
        f"duruşun aynı anda güçlenir."
    )


def _mind_section(
    *,
    seed: str,
    asc_sign: str,
    asc_ruler: str,
    asc_ruler_sign: str,
    asc_house: int,
    loop_signature: str,
    family: str,
) -> Dict[str, Any]:
    micro = editorialize_micro(_pick_variant(_MIND_MICROS, seed + ":mind_micro"), family)
    sign_label = _sign_label(asc_sign)
    ruler_label = _planet_label(asc_ruler)
    ruler_sign_label = _sign_label(asc_ruler_sign)
    ruler_sign_locative = _sign_locative(asc_ruler_sign)
    arena = HOUSE_ARENA_TR.get(asc_house, "günlük akış")
    tone_line = (
        f"{ruler_label}'ün {ruler_sign_locative} olması da burayı daha {_sign_tone(asc_ruler_sign)} bir tona çekiyor."
        if ruler_sign_locative
        else ""
    )
    body = (
        f"Yükselen {sign_label} sana dışarıda daha {_sign_vibe(asc_sign)} bir duruş veriyor; insanlar çoğu zaman "
        "sende önce kontrollü tarafı görüyor. "
        "Ama zihnin çoğu zaman o kadar sakin çalışmıyor; içeride karar, tepki ve ifade aynı anda hızlanan bir hat gibi ilerliyor. "
        f"Yükselen {sign_label} olup yöneticin {ruler_label} {_house_locative(asc_house)}"
        f"{' ve ' + ruler_sign_locative if ruler_sign_locative else ''} olduğu için, bu hat en çok "
        f"{arena} tarafında belirginleşiyor{'; ' + tone_line if tone_line else '.'} "
        "Bu yüzden bazen tek bir cümleyi söylemeden önce uzun uzun tartıyor, bazen de tam tersine bir anda çok net ve "
        "keskin çıkabiliyorsun; iyi gününde bu sana isabetli bir ifade gücü verirken zor gününde zihnin tek bir "
        "cümle üzerinde gereğinden fazla yük taşıyabiliyor."
    )
    if asc_house == 12:
        body = (
            f"Yükselen {sign_label} sana dışarıda daha {_sign_vibe(asc_sign)} bir duruş veriyor; ama içeride olan şey "
            "çoğu zaman bundan daha hareketli. "
            "Senin zihnin önce içeride toparlıyor, sonra dışarı açılıyor; bu yüzden hemen cevap vermemek sende kaçınma "
            "değil, cümleyi ve duyguyu yerli yerine koyma ihtiyacı. "
            f"Yükselen {sign_label} olup yöneticin {ruler_label} {_house_locative(asc_house)}"
            f"{' ve ' + ruler_sign_locative if ruler_sign_locative else ''} olduğu için, belirsizlik en çok "
            f"içeride büyüyor{'; ' + tone_line if tone_line else '.'} Asıl rahatlama, ne hissettiğini kelimeye "
            "dökebildiğin anda geliyor."
        )
    elif asc_house == 11:
        body = (
            f"Yükselen {sign_label} dışarıda daha {_sign_vibe(asc_sign)} bir izlenim bırakıyor; ama zihnin özellikle "
            "bağlam netleşince hızlanıyor. "
            "Bir grubun içinde yerin, yönün ve neden orada olduğun belli olduğunda cümlen de kararın da daha rahat akıyor. "
            f"Yükselen {sign_label} olup yöneticin {ruler_label} {_house_locative(asc_house)}"
            f"{' ve ' + ruler_sign_locative if ruler_sign_locative else ''} olduğu için, belirsizlik en çok ekip, "
            f"çevre ve ortak hedef tarafında yük yaratıyor{'; ' + tone_line if tone_line else '.'} Kiminle ve ne için ilerlediğini bildiğinde hem zihnin "
            "hem ritmin rahatlıyor."
        )
    return {
        "id": "mind_system",
        "title": "Zihin–eylem–kontrol",
        "subtitle": _family_line(
            {
                "direct": "Ne yapacağını bildiğin an tempo kendiliğinden yükselir.",
                "observational": "İnsanlar sende önce kontrollü zihni, sonra hızlanan tempoyu görür.",
                "cinematic": "Cümle yerine oturduğu anda iç ritmin de hızlanır.",
                "intimate": "İçeride netleştiğin an dışarıdaki tempo da rahatlar.",
            },
            family,
            "Ne yapacağını bildiğin an tempo kendiliğinden yükselir.",
        ),
        "body": _cleanup_text(body),
        "micro": micro,
        "chips": [
            f"Yükselen {sign_label}",
            f"{ruler_label} {_house_phrase(asc_house)}",
            *( [ruler_sign_label] if ruler_sign_label else [] ),
        ],
        "legacy_id": "identity_mechanics",
    }


def _relationship_section(
    *,
    seed: str,
    dsc_sign: str,
    r7: str,
    r7_sign: str,
    r7_house: int,
    moon_house: int,
    family: str,
) -> Dict[str, Any]:
    micro = editorialize_micro(_pick_variant(_REL_MICROS, seed + ":rel_micro"), family)
    sign_label = _sign_label(dsc_sign)
    ruler_label = _planet_label(r7)
    ruler_sign_label = _sign_label(r7_sign)
    ruler_sign_locative = _sign_locative(r7_sign)
    tone_line = (
        f"{ruler_label}'ın {ruler_sign_locative} olması da bu hattı daha {_sign_tone(r7_sign)} bir tona çekiyor."
        if ruler_sign_locative
        else ""
    )
    detail_blocks = _relationship_detail_blocks(
        dsc_sign=dsc_sign,
        r7=r7,
        r7_sign=r7_sign,
        r7_house=r7_house,
    )
    moon_ref = "Ay"
    body = (
        "Sen ilişkide yüzeysel bir sıcaklıktan çok, içine oturan bir güven arıyorsun. "
        "Bu yüzden bir bağın gidişi sende yalnızca söylenen şeyden değil, söylenmeyenlerden de etkileniyor. "
        f"7. evin {sign_label} olduğu ve yöneticisi {moon_ref if r7 == 'Moon' else ruler_label} "
        f"{_house_locative(r7_house)}{' ve ' + ruler_sign_locative if ruler_sign_locative else ''} olduğu için, "
        f"yakınlık sende kolayca daha derin ve daha belirleyici bir yere oturabiliyor{'; ' + tone_line if tone_line else '.'} "
        "İyi gününde bu sana çok güçlü bir bağ sezgisi veriyor; zor gününde ise ya içine çekiliyor ya da duyguyu bir anda "
        "hep ya hiç çizgisine taşıyabiliyorsun."
    )
    if r7_house == 11:
        body = (
            "Sen ilişkide yalnızca sıcaklık değil, aynı tarafta olma hissi arıyorsun. "
            "Bu yüzden bağın hangi çevrede ve hangi ritimde büyüdüğü, duygunun kendisi kadar belirleyici oluyor. "
            f"7. evin {sign_label} olduğu ve yöneticisi {ruler_label} {_house_locative(r7_house)}"
            f"{' ve ' + ruler_sign_locative if ruler_sign_locative else ''} olduğu için, güven en çok arkadaşlık, "
            f"ekip ve ortak hedef tarafında kuruluyor; bağ çoğu zaman önce sosyal zeminde rahatlayıp sonra derinleşiyor{'; ' + tone_line if tone_line else '.'} "
            "Rol netleştiğinde hem kalbin hem zihnin rahatlıyor."
        )
    elif r7_house == 3:
        body = (
            "Sen ilişkide yalnızca yakınlık değil, o yakınlığın konuşulabilir olmasını da istiyorsun. "
            "Bu yüzden yarım cümleler, belirsiz tonlar ve açıkta kalan meseleler sende gereğinden fazla yük yaratabiliyor. "
            f"7. evin {sign_label} olduğu ve yöneticisi {ruler_label} {_house_locative(r7_house)}"
            f"{' ve ' + ruler_sign_locative if ruler_sign_locative else ''} olduğu için, güven en çok söz, ton ve "
            f"mesaj trafiği üzerinden kuruluyor; bir bağın ritmi çoğu zaman nasıl konuştuğunuzla şekilleniyor{'; ' + tone_line if tone_line else '.'} "
            "Burada belirleyici olan büyük açıklamalar değil, doğru anda gelen temiz bir netlik cümlesi."
        )
    return {
        "id": "relationships",
        "title": "Duygusal derinlik" if r7_house == 8 else "İlişkiler ve yakınlık",
        "subtitle": _family_line(
            {
                "direct": "Güven geldiğinde bağ hızla derinleşir.",
                "observational": "İnsanlar sende sıcaklıktan önce güven eşiğini hisseder.",
                "cinematic": "Yakınlık burada hafif ilerlemez; bir anda derine çekilir.",
                "intimate": "Kalbin, güven olmadan yarım açılmaz.",
            },
            family,
            "Güven geldiğinde bağ hızla derinleşir.",
        ),
        "body": _cleanup_text(body),
        "detail_blocks": detail_blocks,
        "micro": micro,
        "chips": [
            f"7. ev {sign_label}",
            f"{ruler_label} {_house_phrase(r7_house)}",
            *( [ruler_sign_label] if ruler_sign_label else [] ),
        ],
        "legacy_id": "relationships_depth",
    }


def _career_section(
    *,
    seed: str,
    mc_sign: str,
    mc_ruler: str,
    mc_ruler_sign: str,
    mc_house: int,
    family: str,
) -> Dict[str, Any]:
    micro = editorialize_micro(_pick_variant(_CAREER_MICROS, seed + ":career_micro"), family)
    mc_sign_label = _sign_label(mc_sign)
    mc_ruler_label = _planet_label(mc_ruler)
    mc_ruler_sign_label = _sign_label(mc_ruler_sign)
    mc_ruler_sign_locative = _sign_locative(mc_ruler_sign)
    tone_line = (
        f"{mc_ruler_label}'ün {mc_ruler_sign_locative} olması da görünürlük hattını daha {_sign_tone(mc_ruler_sign)} çalıştırıyor."
        if mc_ruler_sign_locative
        else ""
    )
    body = (
        "Sen işte yalnızca iyi yapmak istemiyorsun; yaptığın şeyin yerine oturmasını ve içe sinmesini de istiyorsun. "
        "Bu yüzden hazırlık süreci sende işin kendisi kadar önemli çalışıyor; acele görünür olmak çoğu zaman sana göre değil. "
        f"MC'nin {mc_sign_label} olması sana denge, ilişki yönetimi ve sunum tarafında avantaj veriyor; yöneticin "
        f"{mc_ruler_label} {_house_locative(mc_house)}{' ve ' + mc_ruler_sign_locative if mc_ruler_sign_locative else ''} "
        f"olduğu için üretiminin bir kısmı önce içeride olgunlaşmak istiyor{'; ' + tone_line if tone_line else '.'} "
        "İyi gününde bu sana rafine, güven veren ve etkisi kolay dağılmayan bir görünürlük veriyor."
    )
    if mc_house == 11:
        body = (
            "Sen işte yalnızca iyi yapmak istemiyorsun; doğru insanları ve doğru bağlamı birbirine bağlamak da senin gücün. "
            "Bu yüzden görünürlük burada tek başına parlamaktan çok doğru ağ içinde büyüyor. "
            f"MC'nin {mc_sign_label} olması sana denge ve ilişki yönetimi getirirken, yöneticin {mc_ruler_label} "
            f"{_house_locative(mc_house)}{' ve ' + mc_ruler_sign_locative if mc_ruler_sign_locative else ''} olduğu için "
            f"işin ekip, çevre ve ortak hedef üzerinden hızlanıyor{'; ' + tone_line if tone_line else '.'} "
            "Doğru çevre kurulduğunda performansın da görünürlüğün de daha rahat akıyor."
        )
    elif mc_house == 10:
        body = (
            "Sen işte yalnızca iyi yapmak istemiyorsun; doğru zamanda görünür olup ürettiğini dışarı taşıyabilmek de senin hikâyenin parçası. "
            "Bu yüzden hazırlık kadar sahne anı da belirleyici oluyor. "
            f"MC'nin {mc_sign_label} olması sana denge ve sunum becerisi verirken, yöneticin {mc_ruler_label} "
            f"{_house_locative(mc_house)}{' ve ' + mc_ruler_sign_locative if mc_ruler_sign_locative else ''} olduğu için "
            f"üretmek ve bunu dolaşıma sokmak aynı zincirin iki halkası gibi çalışıyor{'; ' + tone_line if tone_line else '.'} "
            "Burada asıl fark, her şeyi kusursuzlaştırmayı beklemeden görünür kılabildiğinde ortaya çıkıyor."
        )
    return {
        "id": "career_visibility",
        "title": "Görünür olma ritmin",
        "subtitle": _family_line(
            {
                "direct": "Hazır hissettiğin an görünürlüğün de ağırlık kazanır.",
                "observational": "İnsanlar önce kalite çıtasını, sonra etkini görür.",
                "cinematic": "Perde açılmadan önce içeride uzun bir son prova olur.",
                "intimate": "İçinde yerine oturmayan şeyi dışarı taşımak istemezsin.",
            },
            family,
            "Hazır hissettiğin an görünürlüğün de ağırlık kazanır.",
        ),
        "body": _cleanup_text(body),
        "micro": micro,
        "chips": [
            f"MC {mc_sign_label}",
            f"{mc_ruler_label} {_house_phrase(mc_house)}",
            *( [mc_ruler_sign_label] if mc_ruler_sign_label else [] ),
        ],
        "legacy_id": "career_visibility",
    }


def build_sections_v2(
    *,
    chart_data: Mapping[str, Any],
    planets: List[Mapping[str, Any]],
    natal_graph: Mapping[str, Any],
    master_selector: Mapping[str, Any] | None = None,
    migration_mode: str = "legacy",
) -> List[Dict[str, Any]]:
    planets_map = _planet_positions(planets)
    angles = chart_data.get("angles")
    asc_sign = ""
    mc_sign = ""
    if isinstance(angles, Mapping):
        asc_sign = str(angles.get("ascendant_sign") or "").strip()
        mc_sign = str(angles.get("midheaven_sign") or "").strip()
    base_seed = _seed_base(chart_data, asc_sign, mc_sign)

    house1 = _house_ruler(natal_graph, 1)
    asc_ruler = str(house1.get("primary_ruler") or "").strip() or TRADITIONAL_RULERS.get(asc_sign.lower(), "")
    asc_ruler_pos = _planet_pos(asc_ruler, planets_map)
    asc_house = _to_house(asc_ruler_pos.get("house"), 1)
    asc_ruler_sign = str(asc_ruler_pos.get("sign") or "").strip()

    house7 = _house_ruler(natal_graph, 7)
    dsc_sign = str(house7.get("cusp_sign") or "").strip()
    r7 = str(house7.get("primary_ruler") or "").strip() or TRADITIONAL_RULERS.get(dsc_sign.lower(), "")
    r7_pos = _planet_pos(r7, planets_map)
    r7_house = _to_house(r7_pos.get("house"), 7)
    r7_sign = str(r7_pos.get("sign") or "").strip()
    moon_house = _to_house(_planet_pos("Moon", planets_map).get("house"), 8)

    house10 = _house_ruler(natal_graph, 10)
    mc_ruler = str(house10.get("primary_ruler") or "").strip() or TRADITIONAL_RULERS.get(mc_sign.lower(), "")
    mc_ruler_pos = _planet_pos(mc_ruler, planets_map)
    mc_house = _to_house(mc_ruler_pos.get("house"), 10)
    mc_ruler_sign = str(mc_ruler_pos.get("sign") or "").strip()

    loops = natal_graph.get("dominant_loops") if isinstance(natal_graph.get("dominant_loops"), list) else []
    loop_signature = str(((loops or [{}])[0] or {}).get("signature") or "").strip()
    used_families: list[str] = []
    mind_family = select_rhythm_family(base_seed, "sections_v2", "mind_system", used_families)
    used_families.append(mind_family)
    rel_family = select_rhythm_family(base_seed, "sections_v2", "relationships", used_families)
    used_families.append(rel_family)
    career_family = select_rhythm_family(base_seed, "sections_v2", "career_visibility", used_families)

    sections = [
        _mind_section(
            seed=base_seed,
            asc_sign=asc_sign,
            asc_ruler=asc_ruler,
            asc_ruler_sign=asc_ruler_sign,
            asc_house=asc_house,
            loop_signature=loop_signature,
            family=mind_family,
        ),
        _relationship_section(
            seed=base_seed,
            dsc_sign=dsc_sign,
            r7=r7,
            r7_sign=r7_sign,
            r7_house=r7_house,
            moon_house=moon_house,
            family=rel_family,
        ),
        _career_section(
            seed=base_seed,
            mc_sign=mc_sign,
            mc_ruler=mc_ruler,
            mc_ruler_sign=mc_ruler_sign,
            mc_house=mc_house,
            family=career_family,
        ),
    ]
    if migration_mode == "active":
        return _apply_spine_to_sections(
            sections,
            master_selector=master_selector,
        )
    return sections


def build_supporting_threads(
    *,
    chart_data: Mapping[str, Any],
    planets: List[Mapping[str, Any]],
    natal_graph: Mapping[str, Any],
    max_threads: int = 4,
    master_selector: Mapping[str, Any] | None = None,
    migration_mode: str = "legacy",
) -> List[Dict[str, Any]]:
    sections = build_sections_v2(
        chart_data=chart_data,
        planets=planets,
        natal_graph=natal_graph,
        master_selector=master_selector,
        migration_mode=migration_mode,
    )
    threads: List[Dict[str, Any]] = []
    for section in sections[: min(max_threads, 3)]:
        body = str(section.get("body") or "").strip()
        micro = str(section.get("micro") or "").strip()
        threads.append(
            {
                "id": section.get("legacy_id") or section.get("id"),
                "title": section.get("title", ""),
                "one_liner": section.get("subtitle", ""),
                "paragraph": _build_thread_paragraph(str(section.get("subtitle") or ""), body, micro),
                "body": body,
                "detail_blocks": list(section.get("detail_blocks") or []),
                "micro": micro,
                "chips": list(section.get("chips") or []),
                "section_id": section.get("id"),
                "evidence": [],
            }
        )
    return threads
