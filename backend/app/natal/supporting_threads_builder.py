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
        if len(sentences) >= 3:
            break
    if micro and all(_semantic_overlap(micro, prior) < 0.74 for prior in sentences):
        sentences.append(micro)
    return _cleanup_text(" ".join(sentences[:4]))


def _family_line(options: Mapping[str, str], family: str, fallback: str) -> str:
    return str(options.get(family) or fallback).strip()


def _sign_label(sign: str) -> str:
    return SIGN_LABEL_TR.get(str(sign or "").strip(), str(sign or "").strip())


def _planet_label(planet: str) -> str:
    return PLANET_LABEL_TR.get(str(planet or "").strip(), str(planet or "").strip())


def _house_phrase(house: int) -> str:
    return f"{house}. ev"


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
    asc_house: int,
    loop_signature: str,
    family: str,
) -> Dict[str, Any]:
    micro = editorialize_micro(_pick_variant(_MIND_MICROS, seed + ":mind_micro"), family)
    body = (
        "Zihin sende yalnızca düşünce üretmiyor; duruşunla ve hareketinle aynı sistemde çalışıyor. "
        "Bu yüzden bir şeyi anlatmadan önce içinden tartman ya da konuşma bittikten sonra cümleyi yeniden toplaman, "
        "kararsızlıktan çok iç netlik arayışı. "
        f"Yükselen {_sign_label(asc_sign)} ve yöneticin {_planet_label(asc_ruler)}'ün {_house_phrase(asc_house)} "
        "vurgusu belirsizliği özellikle söz, ton ve karar anlarında büyüttüğü için, iyi gününde kısa cümleyle çok net "
        "çıkarken zor gününde kendine gereğinden fazla yük binebilir. "
        "Asıl fark, sınır netleştiğinde hem zihninin hem bedeninin aynı anda gevşemesinde."
    )
    if asc_house == 12:
        body = (
            "Zihin sende yalnızca düşünce üretmiyor; cevap vermeden önce içerde toparlayan bir merkez gibi çalışıyor. "
            f"Yükselen {_sign_label(asc_sign)} ve yöneticin {_planet_label(asc_ruler)}'ün {_house_phrase(asc_house)} "
            "vurgusu, belirsizliği dışarıdan çok içeride büyüttüğü için, iyi gününde sakin bir hazırlıkla çok temiz "
            "çıkarken zor gününde gereğinden fazla bekleyip kendini tutabiliyorsun. "
            "Burada asıl mesele daha çok düşünmek değil; içeride toparladığın şeyi doğru anda dışarı bırakabilmek."
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
        "chips": [f"Yükselen {_sign_label(asc_sign)}", f"{_planet_label(asc_ruler)} {_house_phrase(asc_house)}"],
        "legacy_id": "identity_mechanics",
    }


def _relationship_section(
    *,
    seed: str,
    dsc_sign: str,
    r7: str,
    r7_house: int,
    moon_house: int,
    family: str,
) -> Dict[str, Any]:
    micro = editorialize_micro(_pick_variant(_REL_MICROS, seed + ":rel_micro"), family)
    sign_label = _sign_label(dsc_sign)
    ruler_label = _planet_label(r7)
    moon_ref = "Ay"
    body = (
        "İlişkide aradığın şey yalnızca yakınlık değil; yakınlığın güvene oturması ve sözle davranışın aynı "
        "çizgide yürümesi. Belirsiz kalan bağlar bu yüzden çabuk yorar; netlik geldiğinde ise akış hemen değişir. "
        f"7. evin {sign_label} olduğu için ilişki dilin şefkat ve korunma üzerinden açılıyor, yöneticisi "
        f"{moon_ref if r7 == 'Moon' else ruler_label} {_house_phrase(r7_house)} vurgusu yüzünden de bağlar "
        "yüzeyde kalmıyor; güven, paylaşım ve gerçek temas üzerinden ağırlaşıyor. "
        "Zorlandığında ya tamamen içine kapanmak ya da ya hep ya hiç çizgisine kaymak kolay olabilir; buna rağmen "
        "dürüst bir işaret geldiğinde hem senin iç güvenin hem karşı tarafın zemini aynı anda toparlanıyor."
    )
    if r7_house == 11:
        body = (
            "İlişkide aradığın şey yalnızca yakınlık değil, aynı tarafta olma hissi. Bu yüzden bağın hangi çevrede "
            "ve hangi ritimde büyüdüğü, duygunun kendisi kadar belirleyici. "
            f"7. evin {sign_label} olduğu için ilişki dilin şefkatli ve koruyucu, yöneticisi {ruler_label}'ın "
            f"{_house_phrase(r7_house)} vurgusu ise güveni en çok arkadaşlık, ekip ve ortak hedef içinde görünür "
            "kılıyor; bağ çoğu zaman önce sosyal zeminde rahatlayıp sonra derinleşiyor. "
            "Zorlandığında ilişkiyi belirsiz bir alanda tutmak yorucu geliyor; rol netleştiğinde hem kalbin hem zihnin rahatlıyor."
        )
    elif r7_house == 3:
        body = (
            "İlişkide aradığın şey yalnızca yakınlık değil, yakınlığın konuşulabilir olması. Belirsiz kalan tonlar, "
            "yarım cümleler ve açık bırakılmış meseleler bu yüzden gereğinden fazla yük yaratabiliyor. "
            f"7. evin {sign_label} olduğu için ilişki dilin şefkatli, yöneticisi {ruler_label}'ın "
            f"{_house_phrase(r7_house)} vurgusu ise güveni en çok söz, ton ve mesaj trafiği üzerinden görünür "
            "kılıyor; bir bağın ritmi çoğu zaman nasıl konuştuğunuzla kuruluyor. "
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
        "micro": micro,
        "chips": [f"7. ev {_sign_label(dsc_sign)}", f"{_planet_label(r7)} {_house_phrase(r7_house)}"],
        "legacy_id": "relationships_depth",
    }


def _career_section(
    *,
    seed: str,
    mc_sign: str,
    mc_ruler: str,
    mc_house: int,
    family: str,
) -> Dict[str, Any]:
    micro = editorialize_micro(_pick_variant(_CAREER_MICROS, seed + ":career_micro"), family)
    body = (
        "Kariyerde gücün yalnızca iyi yapmak değil, doğru bağlamı kurup işi rafine etmek. Görünür olma anı geldiğinde "
        "hazır mıyım eşiğinin yükselmesi bu yüzden zayıflık değil, kalite standardı. "
        f"MC'nin {_sign_label(mc_sign)} olması insan ilişkileri, denge ve sunum becerisi tarafında doğal bir avantaj "
        f"veriyor, yöneticisi {_planet_label(mc_ruler)}'ün {_house_phrase(mc_house)} vurgusu ise üretiminin bir "
        "kısmının içeride olgunlaşmasını istiyor; taslağı önce derlediğinde dışarıya daha sağlam çıkıyorsun. "
        "Büyüme burada büyük çıkışlardan çok görünürlüğü kendi hızında taşıyabildiğinde belirginleşiyor; o zaman etki de daha temiz hissediliyor."
    )
    if mc_house == 11:
        body = (
            "Kariyerde gücün yalnızca iyi yapmak değil, doğru insanları ve doğru bağlamı birbirine bağlamak. "
            "Bu yüzden görünürlük burada tek başına parlamaktan çok doğru ağ içinde büyüyor. "
            f"MC'nin {_sign_label(mc_sign)} olması denge ve ilişki yönetimi tarafında doğal bir avantaj verirken, "
            f"yöneticisi {_planet_label(mc_ruler)}'ün {_house_phrase(mc_house)} vurgusu işi ekip, çevre ve ortak "
            "hedef üzerinden hızlandırıyor; doğru çevre kurulduğunda performansın da rahat akıyor. "
            "Burada ustalık herkese yetişmek değil, doğru bağlantıyı doğru dozda görünür kılmak."
        )
    elif mc_house == 10:
        body = (
            "Kariyerde gücün yalnızca iyi yapmak değil, doğru zamanda görünür olup ürettiğini dışarı taşıyabilmek. "
            "Bu yüzden hazırlık kadar sahne anı da burada belirleyici. "
            f"MC'nin {_sign_label(mc_sign)} olması denge ve sunum becerisi getirirken, yöneticisi "
            f"{_planet_label(mc_ruler)}'ün {_house_phrase(mc_house)} vurgusu işi doğrudan görünürlükle büyütüyor; "
            "senin için üretmek ve bunu dolaşıma sokmak aynı zincirin parçası. "
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
        "chips": [f"MC {_sign_label(mc_sign)}", f"{_planet_label(mc_ruler)} {_house_phrase(mc_house)}"],
        "legacy_id": "career_visibility",
    }


def build_sections_v2(
    *,
    chart_data: Mapping[str, Any],
    planets: List[Mapping[str, Any]],
    natal_graph: Mapping[str, Any],
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
    asc_house = _to_house(_planet_pos(asc_ruler, planets_map).get("house"), 1)

    house7 = _house_ruler(natal_graph, 7)
    dsc_sign = str(house7.get("cusp_sign") or "").strip()
    r7 = str(house7.get("primary_ruler") or "").strip() or TRADITIONAL_RULERS.get(dsc_sign.lower(), "")
    r7_house = _to_house(_planet_pos(r7, planets_map).get("house"), 7)
    moon_house = _to_house(_planet_pos("Moon", planets_map).get("house"), 8)

    house10 = _house_ruler(natal_graph, 10)
    mc_ruler = str(house10.get("primary_ruler") or "").strip() or TRADITIONAL_RULERS.get(mc_sign.lower(), "")
    mc_house = _to_house(_planet_pos(mc_ruler, planets_map).get("house"), 10)

    loops = natal_graph.get("dominant_loops") if isinstance(natal_graph.get("dominant_loops"), list) else []
    loop_signature = str(((loops or [{}])[0] or {}).get("signature") or "").strip()
    used_families: list[str] = []
    mind_family = select_rhythm_family(base_seed, "sections_v2", "mind_system", used_families)
    used_families.append(mind_family)
    rel_family = select_rhythm_family(base_seed, "sections_v2", "relationships", used_families)
    used_families.append(rel_family)
    career_family = select_rhythm_family(base_seed, "sections_v2", "career_visibility", used_families)

    return [
        _mind_section(
            seed=base_seed,
            asc_sign=asc_sign,
            asc_ruler=asc_ruler,
            asc_house=asc_house,
            loop_signature=loop_signature,
            family=mind_family,
        ),
        _relationship_section(
            seed=base_seed,
            dsc_sign=dsc_sign,
            r7=r7,
            r7_house=r7_house,
            moon_house=moon_house,
            family=rel_family,
        ),
        _career_section(
            seed=base_seed,
            mc_sign=mc_sign,
            mc_ruler=mc_ruler,
            mc_house=mc_house,
            family=career_family,
        ),
    ]


def build_supporting_threads(
    *,
    chart_data: Mapping[str, Any],
    planets: List[Mapping[str, Any]],
    natal_graph: Mapping[str, Any],
    max_threads: int = 4,
) -> List[Dict[str, Any]]:
    sections = build_sections_v2(
        chart_data=chart_data,
        planets=planets,
        natal_graph=natal_graph,
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
                "micro": micro,
                "chips": list(section.get("chips") or []),
                "section_id": section.get("id"),
                "evidence": [],
            }
        )
    return threads
