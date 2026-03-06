from __future__ import annotations

import hashlib
import random
import re
from typing import Any, Mapping

from app.transit.narrative.archetype_engine import build_insight_pack

BLACKLIST = {
    "orb",
    "aspect",
    "applying",
    "separating",
    "percentile",
    "marker",
    "tier",
}

PLANET_VERBS = {
    "Sun": ["gorus acisini netlestiriyor", "odagini belirginlestiriyor", "kendini ifade etmeni istiyor"],
    "Moon": ["duygusal ritmini hizlandiriyor", "hassasiyetini arttiriyor", "ic tepkilerini gorunur kiliyor"],
    "Mercury": ["zihnini canlandiriyor", "iletisimi hizlandiriyor", "dusunceleri toparlamani istiyor"],
    "Venus": ["iliski dilini yumusatiyor", "uyum arayisini one cikartiyor", "yaklasimini inceltiyor"],
    "Mars": ["hareket istegini arttiriyor", "tepkilerini hizlandiriyor", "adimlarini netlestirmeye zorluyor"],
    "Jupiter": ["ufkunu genisletiyor", "firsatlara bakisini buyutuyor", "guven duygunu canlandiriyor"],
    "Saturn": ["sorumluluklarini sertlestiriyor", "sinirlarini belirginlestiriyor", "duzen kurmaya zorluyor"],
    "Uranus": ["beklenmedik degisimleri tetikliyor", "rutini kiriyor", "esneklik ihtiyacini arttiriyor"],
    "Neptune": ["sezgiyi yukseltiyor", "belirsizlige karsi hassaslastiriyor", "ince detaylari fark ettiriyor"],
    "Pluto": ["derin donusumu calistiriyor", "kontrol ihtiyacini test ediyor", "koklu degisimi zorluyor"],
}

ASPECT_CONNECTORS = {
    "conjunction": ["bu etkiyi dogrudan hissettirebilir", "temayi guclu sekilde one cikarabilir"],
    "opposition": ["denge kurma ihtiyacini arttirabilir", "iki uc arasinda gidis gelis yaratabilir"],
    "square": ["gerilimli bir itilim yaratabilir", "sabri zorlayip karar baskisi dogurabilir"],
    "trine": ["akisi kolaylastirabilir", "dogal bir uyum hissi verebilir"],
    "sextile": ["kucuk adimlarla ilerlemeyi destekleyebilir", "firsatlara acik bir zemin sunabilir"],
}

TARGET_PHRASES = {
    "Sun": "kimlik ve yon algin",
    "Moon": "duygusal denge ihtiyacin",
    "Mercury": "dusunce ve iletisim tarzin",
    "Venus": "iliski ve bag kurma tarzin",
    "Mars": "eylem ve tepki tarzin",
    "Jupiter": "buyume ve guven alanin",
    "Saturn": "sorumluluk sinirlarin",
    "Uranus": "ozgurluk arayisin",
    "Neptune": "sezgi ve belirsizlikle iliskin",
    "Pluto": "guc ve donusum tema",
    "ASC": "dis dunyaya yansiyan durusun",
    "MC": "yon ve hedef algin",
    "DSC": "ikili iliskilerde denge arayisin",
    "IC": "ic guven ve aidiyet alanin",
}

HOUSE_PHRASES = {
    1: "benlik ve durus alaninda",
    2: "para ve ozdeger alaninda",
    3: "zihin ve iletisim alaninda",
    4: "ev ve aidiyet alaninda",
    5: "yaraticilik ve keyif alaninda",
    6: "duzen ve saglik alaninda",
    7: "iliski ve ortaklik alaninda",
    8: "guven ve paylasim alaninda",
    9: "anlam ve yon arayisinda",
    10: "kariyer ve gorunurluk alaninda",
    11: "cevre ve gelecek planlarinda",
    12: "ic dunya ve dinlenme alaninda",
}

DOMAIN_PHRASES = {
    "relationships": "iliski tarafini daha gorunur kilar",
    "career": "is ve sorumluluk tarafini one tasir",
    "money": "maddi konulara dikkat cekebilir",
    "mind": "zihinsel yogunlugu arttirabilir",
    "home": "ev ve duzen ihtiyacini arttirabilir",
    "identity": "kendini konumlandirma bicimini etkileyebilir",
}

DURATION_PHRASES = {
    "long": "etki gun icine degil daha genis bir zamana yayilabilir",
    "medium": "etki birkac gunde belirginlesebilir",
    "short": "etki hizli baslayip hizli durulabilir",
}

PHASE_PHRASES = {
    "applying": "surec yeni hiz kazaniyor",
    "exact": "etki zirveye yaklasiyor",
    "exactish": "etki zirvede hissedilebilir",
    "separating": "etki yavas yavas cozuluyor",
}
YOU_STYLE_HINTS = ("hissedebilirsin", "fark edebilirsin", "bazen", "olabilir")


def _normalize_sentence(text: str) -> str:
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    if not text:
        return ""
    text = re.sub(r"[.!?]+", ".", text)
    if not text.endswith("."):
        text = f"{text}."
    return text


def _first_sentence(text: str) -> str:
    normalized = _normalize_sentence(text)
    if not normalized:
        return ""
    chunks = [part.strip() for part in re.split(r"[.!?]+", normalized) if part.strip()]
    if not chunks:
        return ""
    return _normalize_sentence(chunks[0])


def _clean_blacklist(text: str) -> str:
    low = text.lower()
    if any(word in low for word in BLACKLIST):
        return "Bugun kendine uygun hizda ilerlemek daha iyi hissettirebilir."
    return text


def _ensure_you_style_sentence(text: str) -> str:
    low = text.lower()
    if any(token in low for token in YOU_STYLE_HINTS):
        return text
    base = text.rstrip(".")
    return _normalize_sentence(f"{base} ve bunu daha net hissedebilirsin")


def _seed_from_parts(*parts: str) -> int:
    raw = "|".join(str(part or "") for part in parts)
    return int(hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8], 16)


def _pick(rng: random.Random, items: list[str], fallback: str) -> str:
    if not items:
        return fallback
    return rng.choice(items)


def compose_event_summary_from_item(
    item: Mapping[str, Any],
    *,
    seed: int | None = None,
    voice_style: str = "you",
) -> str:
    event_id = str(item.get("event_id") or "")
    transit_body = str(item.get("transit_body") or "")
    natal_target = str(item.get("natal_point") or "")
    aspect = str(item.get("aspect") or "").lower()
    phase = str(item.get("phase") or "").lower()
    duration = str(item.get("bucket") or "").lower()
    houses = item.get("houses") if isinstance(item.get("houses"), Mapping) else {}
    house_overlay = houses.get("transit_in_natal_house")

    domains_raw = item.get("domains")
    domains: list[str] = []
    if isinstance(domains_raw, list):
        domains = [str(d).strip().lower() for d in domains_raw if str(d).strip()]

    if seed is None:
        seed = _seed_from_parts(event_id, transit_body, natal_target, aspect, phase, duration)
    rng = random.Random(seed)

    verb = _pick(rng, PLANET_VERBS.get(transit_body, []), "gunluk ritmi etkileyebilir")
    connector = _pick(rng, ASPECT_CONNECTORS.get(aspect, []), "dengeyi yeniden ayarlamayi isteyebilir")
    target_phrase = TARGET_PHRASES.get(natal_target, "onemli bir alanin")

    sentence_main = _normalize_sentence(f"{transit_body or 'Bu etki'} {verb}; {target_phrase} uzerinde {connector}")

    house_text = ""
    if isinstance(house_overlay, int):
        house_text = HOUSE_PHRASES.get(house_overlay, "gunluk duzende")

    domain_text = ""
    if domains:
        domain_text = DOMAIN_PHRASES.get(domains[0], "bir alani daha gorunur hale getirebilir")

    phase_text = PHASE_PHRASES.get(phase, "")
    duration_text = DURATION_PHRASES.get(duration, "")

    parts = [part for part in [house_text, domain_text, phase_text or duration_text] if part]
    if not parts:
        parts = ["gun icinde daha bilincli ilerlemek faydali olabilir"]
    insight_pack = build_insight_pack(item, seed=seed, voice_style=voice_style)
    if aspect in {"trine", "sextile"}:
        sentence_context = _first_sentence(str(insight_pack.get("upper") or ""))
    else:
        sentence_context = _first_sentence(str(insight_pack.get("conflict") or ""))
    if not sentence_context:
        sentence_context = _normalize_sentence("Bu donemde " + ", ".join(parts[:2]))

    sentence_main = _clean_blacklist(sentence_main)
    sentence_context = _clean_blacklist(sentence_context)
    if voice_style == "you":
        sentence_context = _ensure_you_style_sentence(sentence_context)
    return f"{sentence_main} {sentence_context}".strip()


def compose_daily_line2_from_top_event(
    *,
    top_event: Mapping[str, Any] | None,
    labels: list[str],
    seed: int,
    voice_style: str = "you",
) -> str:
    rng = random.Random(seed)
    if isinstance(top_event, Mapping):
        synthetic_item = {
            "event_id": str(top_event.get("id") or top_event.get("event_id") or "daily_top"),
            "transit_body": "",
            "natal_point": "",
            "aspect": "",
            "phase": "",
            "bucket": "",
            "houses": {
                "transit_in_natal_house": top_event.get("house_overlay"),
            },
            "signs": {},
            "domains": labels,
        }
        label = str(top_event.get("label") or "").strip()
        bodies = top_event.get("bodies") if isinstance(top_event.get("bodies"), list) else []
        transit = str(bodies[0]) if bodies else ""
        target = str(bodies[1]) if len(bodies) > 1 else ""
        if transit:
            synthetic_item["transit_body"] = transit
        if target:
            synthetic_item["natal_point"] = target
        insight = build_insight_pack(synthetic_item, seed=seed, voice_style=voice_style)
        conflict_short = _normalize_sentence(str(insight.get("conflict_short") or ""))
        if conflict_short:
            return _clean_blacklist(conflict_short)
        if label:
            sentence = _normalize_sentence(f"{label} etkisi gunun ritmini belirginlestirebilir")
            return _clean_blacklist(sentence)
        if transit:
            phrase = TARGET_PHRASES.get(target, "onemli bir alanin")
            sentence = _normalize_sentence(f"{transit} etkisi {phrase} uzerinde daha belirgin hissedilebilir")
            return _clean_blacklist(sentence)

    if labels:
        mapped = DOMAIN_PHRASES.get(labels[0].lower(), "bazi konulari daha gorunur hale getirebilir")
        return _clean_blacklist(_normalize_sentence(f"Bugun {mapped}"))

    fallback = [
        "Bugunun ana temasi gun icinde daha netlesebilir",
        "Gunluk akista bir konu daha fazla dikkat cekebilir",
        "Kucuk kararlarin etkisi bugun daha hizli gorulebilir",
    ]
    return _clean_blacklist(_normalize_sentence(rng.choice(fallback)))


def compose_upper_meaning_line(
    *,
    transit_body: str,
    natal_target: str,
    house_overlay: int | None,
    seed: int,
    voice_style: str = "you",
) -> str:
    synthetic_item = {
        "event_id": f"upper_{transit_body}_{natal_target}_{house_overlay}",
        "transit_body": transit_body,
        "natal_point": natal_target,
        "aspect": "",
        "phase": "",
        "bucket": "",
        "houses": {"transit_in_natal_house": house_overlay},
        "signs": {},
        "domains": [],
    }
    insight = build_insight_pack(synthetic_item, seed=seed, voice_style=voice_style)
    upper = _normalize_sentence(str(insight.get("upper") or ""))
    if upper:
        return _clean_blacklist(upper)

    rng = random.Random(seed)
    target = TARGET_PHRASES.get(natal_target, "yasam duzenin")
    house = HOUSE_PHRASES.get(house_overlay or -1, "gunluk duzende")
    templates = [
        f"{transit_body or 'Bu etki'} bu donemde {house} {target} ile ilgili bakisini olgunlastirabilir.",
        f"{house.capitalize()} {transit_body or 'bu etki'} sayesinde {target} konusunda yeni bir netlik getirebilir.",
        f"{target.capitalize()} bu donemde {house} daha sakin ve bilincli adimlarla guclenebilir.",
    ]
    line = _normalize_sentence(rng.choice(templates))
    return _clean_blacklist(line)
