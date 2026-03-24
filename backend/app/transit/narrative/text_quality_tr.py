from __future__ import annotations

import os
import re
from collections import Counter
from typing import Any, Dict, List, Mapping, Sequence

from app.narrative.humanize_tr import humanize_tr_text
from app.transit.narrative.chain_explainer_tr import build_chain_explainer_tr
from app.transit.narrative.phrase_lib_tr import (
    PLANET_TR,
    POINT_TR,
    SIGN_TR,
    compose_phrase_pack,
    house_motif_line,
    render_signature_tr,
    strip_tech_tokens,
)

_COPY_QUALITY_ENABLED = str(os.getenv("COPY_QUALITY_LAYER", "1")).strip().lower() not in {
    "0",
    "false",
    "off",
    "no",
}
_ENABLE_MICRO_LLM_POLISH = str(os.getenv("ENABLE_MICRO_LLM_POLISH", "0")).strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
_MICRO_LLM_PROVIDER = str(os.getenv("MICRO_LLM_PROVIDER", "none")).strip().lower() or "none"

_TR_WORD_FIXES = {
    "iletisim": "iletişim",
    "iliski": "ilişki",
    "hiz": "hız",
    "dogrudan": "doğrudan",
    "kacinma": "kaçınma",
    "golge": "gölge",
    "duzen": "düzen",
    "donusum": "dönüşüm",
    "ic": "iç",
    "dis": "dış",
    "firsat": "fırsat",
    "netlik": "netlik",
    "yonsuz": "yönsüz",
    "stili": "stili",
    "yaklasim": "yaklaşım",
    "uygulama": "uygulama",
    "donemde": "dönemde",
    "donem": "dönem",
    "surec": "süreç",
    "sureci": "süreci",
    "ozet": "özet",
    "ozel": "özel",
    "ozgur": "özgür",
    "ozgurluk": "özgürlük",
    "goz": "göz",
    "gonder": "gönder",
    "cikar": "çıkar",
    "karsi": "karşı",
    "cozuluyor": "çözülüyor",
    "cozulme": "çözülme",
    "bilincalti": "bilinçaltı",
    "olcum": "ölçüm",
    "olc": "ölç",
    "tasma": "taşma",
    "saglik": "sağlık",
    "gorunurluk": "görünürlük",
    "iliski": "ilişki",
    "iliski": "ilişki",
    "yontem": "yöntem",
    "degisim": "değişim",
    "netlesme": "netleşme",
    "dengeleme": "dengeleme",
}

_SIGN_TR = {
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

_PLANET_ALLOWLIST = {
    "sun",
    "moon",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
    "asc",
    "dsc",
    "mc",
    "ic",
    "north_node",
    "south_node",
    "lilith",
    "chiron",
    "vertex",
    "fortune",
}

_PLANET_TR = {
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
    "asc": "ASC",
    "dsc": "DSC",
    "mc": "MC",
    "ic": "IC",
    "north_node": "Kuzey Ay Düğümü",
    "south_node": "Güney Ay Düğümü",
    "lilith": "Lilith",
    "chiron": "Chiron",
    "vertex": "Vertex",
    "fortune": "Fortune",
}

_VERB_STARTS = (
    "netleştir",
    "sadeleştir",
    "yaz",
    "çıkar",
    "cikar",
    "bağla",
    "bagla",
    "sabitle",
    "açma",
    "acma",
    "tamamla",
    "planla",
    "koru",
    "seç",
    "ölç",
    "sor",
    "bekle",
    "gözden",
    "durdur",
    "teyit",
    "odaklan",
    "yenile",
    "yavaşlat",
)

_THEME_BANK: Dict[str, Any] = {
    "modes": {
        "daily": {
            "length": {
                "conflict_sentences": (2, 3),
                "shadow_sentences": (1, 2),
                "upper_sentences": (2, 3),
                "extra_line_sentences": (1, 1),
                "guidance_bullets": 3,
                "watch_out_bullets": 2,
            }
        },
        "period": {
            "length": {
                "core_story_paragraphs": (2, 4),
                "core_story_sentences_per_paragraph": (3, 5),
                "upper_meaning_paragraphs": (1, 2),
                "upper_meaning_sentences": (3, 5),
            }
        },
    },
    "event_generation": {
        "path_scoring": {
            "max_hops": 3,
            "node_weights": {
                "transit_planet": 0.9,
                "aspect": 0.7,
                "natal_target_planet": 1.0,
                "natal_target_house": 0.9,
                "natal_target_sign": 0.7,
                "dispositor": 0.6,
                "rulership_house": 0.5,
                "angle_hit": 0.85,
            },
            "edge_weights": {
                "aspect_edge": 1.0,
                "house_edge": 0.6,
                "sign_edge": 0.6,
                "dispositor_edge": 0.8,
                "rulership_edge": 0.7,
                "angle_edge": 0.9,
            },
        },
        "motif_selection": {
            "top_motifs": 3,
            "must_include": ("house_scene",),
            "prefer_include": ("sign_style", "dispositor_hint"),
        },
    },
    "houses": {
        3: {
            "label": "zihin/iletisim",
            "scene": "mesajlar-konuşmalar ve yazma-not alma ritmi",
            "motif": "dil kalibrasyonu",
        },
        6: {
            "label": "rutin/saglik/servis",
            "scene": "takvim ve iş akışı ritmi",
            "motif": "mikro alışkanlık",
        },
        7: {
            "label": "iliskiler/ortaklik",
            "scene": "anlaşma dili ve beklenti dengesi",
            "motif": "uyum ve sınır",
        },
        9: {
            "label": "anlam/ufuk/genisleme",
            "scene": "öğrenme, yayın ve yabancı dil sahnesi",
            "motif": "anlam motoru",
        },
    },
    "promise_hooks": {
        "identity_line": "Dış geri bildirim içeride kalıcı bir kimlik ayarı kuruyor.",
        "mind_line": "Zihinsel otoriteyi kurdukça kararların kalıcılığı artıyor.",
    },
}

HOUSE_SCENES_TR: Dict[int, str] = {
    1: "benlik/duruş/imaj",
    2: "para/değer/özgüven",
    3: "iletişim tarzı/yakın çevre/kardeşler/kısa eğitim/günlük trafik",
    4: "ev/kök/dinlenme",
    5: "yaratıcılık/aşk/keyif",
    6: "iş rutini/sağlık/verim",
    7: "ilişki/ortaklık",
    8: "yakınlık/güven/kriz",
    9: "ufuk/uzmanlaşma/eğitim/yayın/yabancılar/inançlar/yol haritası",
    10: "kariyer/itibar/yön",
    11: "topluluk/network/hedef/ekip",
    12: "iç dünya/arınma/geri çekilme",
}

PLANET_ESSENCE_TR: Dict[str, Dict[str, str]] = {
    "neptune": {"gift": "sezgi", "risk": "sis/idealizasyon"},
    "pluto": {"gift": "dönüşüm gücü", "risk": "kontrol/yoğunluk"},
    "uranus": {"gift": "yenilik", "risk": "dağılma/ani kopuş"},
    "saturn": {"gift": "yapı", "risk": "baskı/sertlik"},
    "mars": {"gift": "hamle", "risk": "acele/gerilim"},
    "jupiter": {"gift": "genişleme", "risk": "abartı"},
    "moon": {"gift": "duygu sinyali", "risk": "dalga"},
    "sun": {"gift": "odak", "risk": "ego inadı"},
    "mercury": {"gift": "zihin/ifade", "risk": "fazla düşünme"},
    "venus": {"gift": "uyum", "risk": "taviz"},
    "chiron": {"gift": "şifa", "risk": "hassas tetik"},
    "lilith": {"gift": "ham dürüstlük", "risk": "sert sınır"},
    "north_node": {"gift": "yön büyümesi", "risk": "eski alışkanlıkla çekişme"},
    "south_node": {"gift": "yük boşaltma", "risk": "otomatik pilot"},
}

ASPECT_DYNAMIC_TR: Dict[str, Dict[str, str]] = {
    "square": {"name": "sürtünme", "verb": "ayar ister", "risk": "yanlış ayar/yanlış anlaşılma"},
    "opposition": {"name": "çekişme", "verb": "denge ister", "risk": "iki uca savrulma"},
    "conjunction": {"name": "büyüteç", "verb": "büyütür", "risk": "fazla yüklenme"},
    "trine": {"name": "akış", "verb": "kolay açar", "risk": "rehavet/dağılma"},
    "sextile": {"name": "fırsat", "verb": "kapı açar", "risk": "pasif kalma"},
}

_ORPHAN_BACKLINK_RE = re.compile(r"(?i)^\s*arka bağlantı:\s*\d+\.?\s*$")
_ORDINAL_RE = re.compile(r"(\b\d{1,2})\.(\s*)(Ev|ev)\b")
_PUNCT_STRIP_RE = re.compile(r"[^\wçğıöşü]+", flags=re.IGNORECASE)


def protect_ordinals(text: str) -> str:
    return _ORDINAL_RE.sub(r"\1<EV_DOT>\2\3", str(text or ""))


def restore_ordinals(text: str) -> str:
    return str(text or "").replace("<EV_DOT>", ".")


def _split_sentences(text: str) -> List[str]:
    protected = protect_ordinals(text)
    parts = [part.strip() for part in re.split(r"(?<!\d[.!?])(?<=[.!?])\s+", protected) if part.strip()]
    if len(parts) == 1 and "." not in protected and "!" not in protected and "?" not in protected:
        parts = [part.strip() for part in re.split(r"\s*;\s*", protected) if part.strip()]
    return [restore_ordinals(part) for part in parts if restore_ordinals(part).strip()]


def normalize(text: str) -> str:
    value = restore_ordinals(strip_tech_tokens(tr_normalize(str(text or "")))).lower()
    value = _PUNCT_STRIP_RE.sub(" ", value)
    return re.sub(r"\s+", " ", value).strip()


def similarity(a: str, b: str) -> float:
    left = set(normalize(a).split())
    right = set(normalize(b).split())
    if not left or not right:
        return 0.0
    inter = len(left & right)
    union = len(left | right)
    return inter / union if union else 0.0


def tr_normalize(text: str) -> str:
    out = str(text or "")
    if not out.strip():
        return ""

    out = out.replace("\n", " ")
    out = re.sub(r"\s+", " ", out).strip()

    for raw, fixed in _TR_WORD_FIXES.items():
        out = re.sub(rf"\b{re.escape(raw)}\b", fixed, out, flags=re.IGNORECASE)

    out = re.sub(r"\b([1-9]|1[0-2])\s*ev\b", r"\1. Ev", out, flags=re.IGNORECASE)
    out = re.sub(r"\b([1-9]|1[0-2])\.\s*ev\b", r"\1. Ev", out, flags=re.IGNORECASE)

    for raw_sign, tr_sign in {**_SIGN_TR, **SIGN_TR}.items():
        out = re.sub(rf"\b{re.escape(raw_sign)}\b", tr_sign, out, flags=re.IGNORECASE)
    for raw_planet, tr_planet in PLANET_TR.items():
        out = re.sub(rf"\b{re.escape(raw_planet)}\b", tr_planet, out, flags=re.IGNORECASE)
    for raw_point, tr_point in POINT_TR.items():
        out = re.sub(rf"\b{re.escape(raw_point)}\b", tr_point, out, flags=re.IGNORECASE)

    out = re.sub(r"\s+([,.;:!?])", r"\1", out)
    out = re.sub(r"([,;:!?])(?!\s|$)", r"\1 ", out)
    out = re.sub(r"\.{2,}", ".", out)
    out = re.sub(r"\s+", " ", out).strip()
    return out


def _norm(s: str) -> str:
    return tr_normalize(strip_tech_tokens(str(s or "")))


def _collapse_period_prefix(text: str) -> str:
    t = _norm(text)
    if not t:
        return ""
    matches = list(re.finditer(r"(?i)bu dönem[^:]{20,220}:\s*", t))
    if len(matches) <= 1:
        return t
    return (t[: matches[0].end()] + t[matches[-1].end() :]).strip()


def _house_scene(house: int | None) -> str:
    if not house:
        return "genel"
    return HOUSE_SCENES_TR.get(int(house), "genel")


def _axis_house(point: str) -> int | None:
    return {"ASC": 1, "DSC": 7, "MC": 10, "IC": 4}.get(str(point or "").strip().upper())


def _planet_key(name: Any) -> str:
    return str(name or "").strip().lower().replace(" ", "_")


def _aspect_key(name: Any) -> str:
    return str(name or "").strip().lower()


def _is_period(horizon: str) -> bool:
    return str(horizon or "").strip().lower() == "period"


def _soften_today(text: str, horizon: str) -> str:
    t = _norm(text)
    if not t:
        return ""
    if _is_period(horizon):
        t = re.sub(r"(?i)\bbugün\b", "bu hafta", t)
    return t


def _coerce_house(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if str(value or "").isdigit():
        return int(str(value))
    return None


HOUSE_LIFE_TRANSLATIONS_TR: Dict[int, Dict[str, str]] = {
    1: {
        "short": "kendini ortaya koyuş biçimin",
        "full": "kendini dışarıda nasıl taşıdığın, beden dilin ve ilk izlenimin",
        "build": "kendini daha net ortaya koyma",
    },
    2: {
        "short": "para ve özdeğer dengen",
        "full": "para kararların, sahip oldukların ve güven duygun",
        "build": "değerini daha net sahiplenme",
    },
    3: {
        "short": "iletişim biçimin",
        "full": "mesajların, konuşmaların, yakın çevre trafiğin ve yazı dilin",
        "build": "kendini daha açık ifade etme",
    },
    4: {
        "short": "ev ve iç güven alanın",
        "full": "ev düzenin, dinlenme alanın ve iç güvenlik hissin",
        "build": "kendi içinde daha güvenli kalma",
    },
    5: {
        "short": "yaratıcılık ve görünür üretim alanın",
        "full": "yaratıcılığın, keyif alanın, flört enerjin ve görünür üretimin",
        "build": "ilhamı görünür kılma",
    },
    6: {
        "short": "günlük düzenin",
        "full": "iş akışın, alışkanlıkların, sağlığın ve günlük düzenin",
        "build": "kendine işleyen bir düzen kurma",
    },
    7: {
        "short": "ilişkilerde kurduğun denge",
        "full": "yakın bağların, ortaklıkların ve karşı tarafla kurduğun denge",
        "build": "ilişkide beklentiyi açık kurma",
    },
    8: {
        "short": "yakınlık ve güven alanın",
        "full": "yakınlık, güven, paylaşım ve derin bağ kurma biçimin",
        "build": "yakınlıkta kendini kaybetmeden kalma",
    },
    9: {
        "short": "öğrenme ve yön duygun",
        "full": "öğrenme, uzmanlaşma, yayınlama, uzaklar ve dünya görüşün",
        "build": "öğrendiklerini somut bir yöne çevirme",
    },
    10: {
        "short": "kariyer yönün",
        "full": "kariyer yönün, görünürlüğün ve dışarıda üstlendiğin sorumluluklar",
        "build": "sorumluluğu net bir yöne çevirme",
    },
    11: {
        "short": "çevren ve gelecek planların",
        "full": "arkadaş çevren, ekipler, networkün ve ortak hedeflerin",
        "build": "gücünü doğru çevrelerle birleştirme",
    },
    12: {
        "short": "iç dünya alanın",
        "full": "iç dünyan, geri çekilme ihtiyacın ve perde arkasında yürüyen süreçlerin",
        "build": "içeride net kalabilme",
    },
}

ANGLE_LIFE_TRANSLATIONS_TR: Dict[str, str] = {
    "ASC": "kendini dışarıda nasıl taşıdığın",
    "DSC": "yakın ilişkilerde kurduğun denge",
    "MC": "dışarıda tuttuğun yön ve görünürlük",
    "IC": "iç güvenlik ve kök duygun",
}

PLANET_EXPERIENCE_TR: Dict[str, Dict[str, str]] = {
    "neptune": {
        "pressure": "bulanıklık ve idealizasyon",
        "gift": "sezgi ve incelik",
        "watch": "muğlak konuşmak ya da kararı ertelemek",
    },
    "uranus": {
        "pressure": "ani kopuş ve sabırsız sıçrama",
        "gift": "yenilik ve cesur deneme",
        "watch": "aynı anda her şeyi değiştirmeye kalkmak",
    },
    "pluto": {
        "pressure": "kontrol etme ve her şeyi aşırı yükleme",
        "gift": "derinleşme ve eleme gücü",
        "watch": "gücü yalnızca sıkı tutmak sanmak",
    },
    "saturn": {
        "pressure": "aşırı sertleşme ve gecikme korkusu",
        "gift": "dayanıklılık ve yapı",
        "watch": "kusursuz olana kadar beklemek",
    },
    "mars": {
        "pressure": "acele tepki ve gereksiz sertlik",
        "gift": "hareket ve cesaret",
        "watch": "hız uğruna niyeti bulanıklaştırmak",
    },
    "jupiter": {
        "pressure": "abartı ve fazla açılma",
        "gift": "genişleme ve fırsat",
        "watch": "ölçüsüz iyimserlik",
    },
    "venus": {
        "pressure": "uyum uğruna taviz vermek",
        "gift": "uyum ve bağ kurma",
        "watch": "onay için kendi ölçünü bırakmak",
    },
    "mercury": {
        "pressure": "fazla düşünmek ve dağılmak",
        "gift": "ayrıştırma ve anlatma",
        "watch": "detayda takılıp özü kaçırmak",
    },
}

ASPECT_EXPERIENCE_TR: Dict[str, Dict[str, str]] = {
    "square": {
        "tone": "ayar istiyor",
        "watch": "ilk tepkiyle hareket etmek",
    },
    "opposition": {
        "tone": "denge ve karşı tarafı doğru okuma ihtiyacı yaratıyor",
        "watch": "karşı tarafı niyetinin tamamı sanmak",
    },
    "conjunction": {
        "tone": "bir alanı büyüteç altına alıyor",
        "watch": "her şeyi tek başına taşımaya kalkmak",
    },
    "trine": {
        "tone": "doğal bir kolaylık açıyor",
        "watch": "kolay geliyor diye odağı gevşetmek",
    },
    "sextile": {
        "tone": "küçük ama gerçek bir kapı aralıyor",
        "watch": "fırsatı fark edip yine de hareketsiz kalmak",
    },
}


def _life_scene(house: int | None, *, detail: str = "short") -> str:
    if not house:
        return "hayatının bu alanı"
    return HOUSE_LIFE_TRANSLATIONS_TR.get(int(house), {}).get(detail) or "hayatının bu alanı"


def _target_life_label(natal_point: str, target_house: int | None) -> str:
    point = str(natal_point or "").strip().upper()
    if point in ANGLE_LIFE_TRANSLATIONS_TR:
        return ANGLE_LIFE_TRANSLATIONS_TR[point]
    return _life_scene(target_house, detail="short")


def _transit_target_houses(card: Mapping[str, Any], event: Mapping[str, Any]) -> tuple[int | None, int | None]:
    houses = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}
    pack = card.get("natal_context_pack") if isinstance(card.get("natal_context_pack"), Mapping) else {}
    target = pack.get("target") if isinstance(pack.get("target"), Mapping) else {}
    transit_house = _coerce_house(houses.get("transit_in_natal_house"))
    target_house = _coerce_house(houses.get("natal_point_house")) or _coerce_house(target.get("house")) or _axis_house(event.get("natal_point"))
    return transit_house, target_house


def _secondary_context_sentence(card: Mapping[str, Any], event: Mapping[str, Any], target_house: int | None) -> str:
    pack = card.get("natal_context_pack") if isinstance(card.get("natal_context_pack"), Mapping) else {}
    target = pack.get("target") if isinstance(pack.get("target"), Mapping) else {}
    sign_tr = str(target.get("sign_tr") or target.get("sign") or "").strip()
    planet = str(target.get("planet") or event.get("natal_point") or "").strip()
    natal_point = str(event.get("natal_point") or "").strip().upper()

    if natal_point in ANGLE_LIFE_TRANSLATIONS_TR and sign_tr:
        return {
            "ASC": f"Bu hatta mesele sadece görünmek değil, {sign_tr} tonunda daha güvenilir ve anlaşılır görünmek.",
            "DSC": f"Bu hatta mesele sadece yakınlık değil, {sign_tr} tonunda daha açık ve dengeli bağ kurmak.",
            "MC": f"Bu hatta mesele sadece görünür olmak değil, {sign_tr} tonunda daha tutarlı bir yön göstermek.",
            "IC": f"Bu hatta mesele sadece huzur aramak değil, {sign_tr} tonunda daha sağlam bir iç alan kurmak.",
        }.get(natal_point, "")
    if planet and target_house:
        return f"Sende {POINT_TR.get(natal_point, planet)} zaten {_life_scene(target_house, detail='short')} tarafında çalıştığı için bu etki yüzeyde kalmıyor."
    return ""


def _supporting_spillover_note(card: Mapping[str, Any]) -> str:
    pack = card.get("natal_context_pack") if isinstance(card.get("natal_context_pack"), Mapping) else {}
    rulership = pack.get("rulership_houses") if isinstance(pack.get("rulership_houses"), list) else []
    houses: List[int] = []
    for entry in rulership:
        house = _safe_int(entry.get("house")) if isinstance(entry, Mapping) else None
        if house and house not in houses:
            houses.append(house)
    if not houses:
        return ""
    labels = [_life_scene(house, detail="short") for house in houses[:2]]
    if len(labels) == 1:
        return f"İkincil yankı {labels[0]} tarafına da uzanabilir."
    return f"İkincil yankı zamanla {labels[0]} ve {labels[1]} alanına da uzanabilir."


def _title_for_event(event: Mapping[str, Any], transit_house: int | None, target_house: int | None) -> str:
    transit = _planet_key(event.get("transit_body"))
    aspect = _aspect_key(event.get("aspect"))
    natal_point = str(event.get("natal_point") or "").strip().upper()
    if transit == "neptune" and aspect == "square" and natal_point == "ASC":
        return "Kendini Anlatışını Yeniden Ayarlıyorsun"
    if transit == "uranus" and aspect in {"trine", "sextile"} and natal_point.lower() == "mars":
        return "İlhamını Yönteme Çeviriyorsun"
    if transit == "pluto" and aspect == "sextile" and natal_point.lower() == "pluto":
        return "Çevren ve Yönün Daha Seçici Hale Geliyor"
    if target_house == 7:
        return "İlişkide Çerçeve Netleşiyor"
    if target_house == 9:
        return "Yönün ve Öğrenme Biçimin Değişiyor"
    if target_house == 11:
        return "Çevren ve Gelecek Planların Yenileniyor"
    if target_house == 1:
        return "Kendini Ortaya Koyuşun Değişiyor"
    if transit_house == 3:
        return "İfade Tarzın Güncelleniyor"
    return "Bu Dönem Sende Yeni Bir Ayar Açıyor"


def _generic_opening(event: Mapping[str, Any], card: Mapping[str, Any], transit_house: int | None, target_house: int | None) -> str:
    transit = _planet_key(event.get("transit_body"))
    aspect = _aspect_key(event.get("aspect"))
    natal_point = str(event.get("natal_point") or "").strip().upper()
    start_full = _life_scene(transit_house, detail="full")
    end_short = _target_life_label(natal_point, target_house)

    if transit == "neptune" and aspect == "square" and natal_point == "ASC":
        return _dedupe_sentences(
            "Şu sıralar sadece ne söylediğin değil, nasıl duyulduğun da hassaslaşıyor. "
            "Aynı niyet bazen daha muğlak, daha yumuşak ya da olduğundan sert algılanabilir."
        )
    if transit == "uranus" and aspect in {"trine", "sextile"} and natal_point.lower() == "mars":
        return _dedupe_sentences(
            "Yeni bir şey denemek, üretmek ya da cesur bir çıkış yapmak daha doğal geliyor. "
            "Asıl değişim hevesin kendisinde değil; bunu öğrenme planına, uzmanlaşmaya ya da somut bir hatta taşıyabildiğinde başlıyor."
        )
    if transit == "pluto" and aspect == "sextile" and natal_point.lower() == "pluto":
        return _dedupe_sentences(
            "Bazı insanlara, hedeflere ve uzun vadeli planlara eski gözle bakmıyorsun. "
            "İçeride güç tanımın değiştikçe hangi çevrede yer almak istediğin de seçiliyor."
        )

    return _dedupe_sentences(
        f"Bu etki önce {start_full} tarafında hareket yaratıyor. "
        f"Sonra bunun karşılığı {end_short} alanında daha görünür hale geliyor."
    )


def _generic_essence(event: Mapping[str, Any], transit_house: int | None, target_house: int | None) -> str:
    transit = _planet_key(event.get("transit_body"))
    aspect = _aspect_key(event.get("aspect"))
    natal_point = str(event.get("natal_point") or "").strip().upper()
    end_short = _target_life_label(natal_point, target_house)
    aspect_tone = ASPECT_EXPERIENCE_TR.get(aspect, {}).get("tone", "bir ayar açıyor")

    if transit == "neptune" and aspect == "square" and natal_point == "ASC":
        return _dedupe_sentences(
            "Bu dönem temel mesele kendini daha çok göstermek değil, daha anlaşılır göstermek. "
            "İçeride ne hissettiğinle dışarıda nasıl okunduğun arasındaki mesafe kapanmak istiyor."
        )
    if transit == "uranus" and aspect in {"trine", "sextile"} and natal_point.lower() == "mars":
        return _dedupe_sentences(
            "Bu dönem sana kısa süreli gaz değil, yeni bir yöntem teklif ediyor. "
            "Kıvılcımını plana çevirdiğinde değişim geçici bir heyecan olmaktan çıkıp gerçek bir yön haline geliyor."
        )
    if transit == "pluto" and aspect == "sextile" and natal_point.lower() == "pluto":
        return _dedupe_sentences(
            "Buradaki değişim gürültülü değil; daha seçici, daha derin ve daha stratejik. "
            "Seni büyütmeyen çevre, hedef ya da rol ile seni gerçekten güçlendiren olan arasındaki fark belirginleşiyor."
        )

    pressure = PLANET_EXPERIENCE_TR.get(transit, {}).get("pressure", "bir baskı")
    return _dedupe_sentences(
        f"Bu süreç {end_short} alanında eski alışkanlıkları gözden geçirmeni istiyor. "
        f"Yüzeyde {aspect_tone}; altta ise {pressure} tarafını daha bilinçli yönetmeyi öğretiyor."
    )


def _generic_mechanism(card: Mapping[str, Any], event: Mapping[str, Any], transit_house: int | None, target_house: int | None) -> str:
    natal_point = str(event.get("natal_point") or "").strip().upper()
    start_full = _life_scene(transit_house, detail="full")
    end_full = _target_life_label(natal_point, target_house)
    secondary = _secondary_context_sentence(card, event, target_house)
    base = (
        f"Önce {start_full} tarafında bir hareket başlıyor. "
        f"Sonra bunun etkisi {end_full} alanında belirginleşiyor."
    )
    if secondary:
        base = f"{base} {secondary}"
    return _dedupe_sentences(base)


def _generic_asks(event: Mapping[str, Any], transit_house: int | None, target_house: int | None) -> str:
    transit = _planet_key(event.get("transit_body"))
    aspect = _aspect_key(event.get("aspect"))
    natal_point = str(event.get("natal_point") or "").strip().upper()

    if transit == "neptune" and aspect == "square" and natal_point == "ASC":
        return _dedupe_sentences(
            "Senden ne hissettiğini değil, neyi netleştirmen gerektiğini fark etmeni istiyor. "
            "Cümleyi sadeleştirip sınırı baştan söylediğinde bu etki lehine çalışıyor."
        )
    if transit == "uranus" and aspect in {"trine", "sextile"} and natal_point.lower() == "mars":
        return _dedupe_sentences(
            "Hevesi tek seferlik bir çıkışta bırakmamanı istiyor. "
            "Denemeyi plana, planı da tekrar eden bir yönteme çevirdiğinde gerçek kazanım geliyor."
        )
    if transit == "pluto" and aspect == "sextile" and natal_point.lower() == "pluto":
        return _dedupe_sentences(
            "Kiminle, ne uğruna ve hangi bedelle ilerlemek istediğini daha seçici belirlemeni istiyor. "
            "Her kapıyı açık tutmak yerine doğru kapıyı bilinçli seçtiğinde güç birikiyor."
        )

    build_target = _life_scene(target_house, detail="build")
    return _dedupe_sentences(
        f"Buradaki davet, {_life_scene(transit_house, detail='short')} tarafında olanı {build_target} kasına çevirmek. "
        "Net olanı seçip onu tekrar edilebilir hale getirdiğinde bu dönem hızlanıyor."
    )


def _generic_watchout(event: Mapping[str, Any], transit_house: int | None, target_house: int | None) -> str:
    transit = _planet_key(event.get("transit_body"))
    aspect = _aspect_key(event.get("aspect"))
    natal_point = str(event.get("natal_point") or "").strip().upper()
    planet_watch = PLANET_EXPERIENCE_TR.get(transit, {}).get("watch", "otomatik pilota kaymak")
    aspect_watch = ASPECT_EXPERIENCE_TR.get(aspect, {}).get("watch", "ölçüyü kaçırmak")

    if transit == "neptune" and aspect == "square" and natal_point == "ASC":
        return _dedupe_sentences(
            "Asıl risk, yanlış anlaşılmayı yalnızca ton meselesi sanıp içeriği netleştirmemek. "
            "Muğlak konuşmak ya da niyetini açık söylememek seni gereksiz açıklama döngüsüne sokabilir."
        )
    if transit == "uranus" and aspect in {"trine", "sextile"} and natal_point.lower() == "mars":
        return _dedupe_sentences(
            "Risk, aynı anda fazla fikir açıp hiçbiriyle yeterince derine gitmemek. "
            "Hızın cazibesi ölçüyü dağıttığında gerçek kazanım yerine kısa süreli heyecan kalır."
        )
    if transit == "pluto" and aspect == "sextile" and natal_point.lower() == "pluto":
        return _dedupe_sentences(
            "Risk, seçiciliği içe kapanmaya ya da her şeyi kontrol etmeye çevirmek. "
            "Güç toplamak isterken insanları yalnızca işe yarayıp yaramadığına göre okumak bağı kurutabilir."
        )

    return _dedupe_sentences(
        f"Bu süreçte {aspect_watch} kolay. "
        f"Özellikle {planet_watch} refleksi devreye girdiğinde konu gereğinden fazla büyüyebilir."
    )


def _generic_what_it_builds(event: Mapping[str, Any], transit_house: int | None, target_house: int | None) -> str:
    transit = _planet_key(event.get("transit_body"))
    aspect = _aspect_key(event.get("aspect"))
    natal_point = str(event.get("natal_point") or "").strip().upper()
    if transit == "neptune" and aspect == "square" and natal_point == "ASC":
        return "kendini daha net ifade etme ve yanlış anlaşılma payını azaltma kasını"
    if transit == "uranus" and aspect in {"trine", "sextile"} and natal_point.lower() == "mars":
        return "ilhamı çalışır bir yönteme ve gerçek bir yöne çevirme kasını"
    if transit == "pluto" and aspect == "sextile" and natal_point.lower() == "pluto":
        return "gücünü doğru çevre ve doğru hedefle birleştirme kasını"
    return f"{_life_scene(target_house, detail='build')} kasını"


def _technical_note(card: Mapping[str, Any], event: Mapping[str, Any], transit_house: int | None, target_house: int | None) -> str:
    transit = _PLANET_TR.get(_planet_key(event.get("transit_body")), str(event.get("transit_body") or "Transit"))
    natal_point = str(event.get("natal_point") or "").strip().upper()
    target = POINT_TR.get(natal_point, natal_point.title() if natal_point else "Nokta")
    aspect_label = {"square": "kare", "opposition": "karşıt", "conjunction": "kavuşum", "trine": "üçgen", "sextile": "sekstil"}.get(_aspect_key(event.get("aspect")), "açı")
    parts = [
        f"Teknik not: {transit} {target} ile {aspect_label} açı yapıyor.",
    ]
    if transit_house:
        parts.append(f"Ana sahne {transit_house}. Ev: {_life_scene(transit_house, detail='short')}.")
    if target_house:
        parts.append(f"Hedef alan {target_house}. Ev: {_life_scene(target_house, detail='short')}.")
    spillover = _supporting_spillover_note(card)
    if spillover:
        parts.append(spillover)
    return _dedupe_sentences(" ".join(parts))


def _event_guidance_bullets(event: Mapping[str, Any], transit_house: int | None, target_house: int | None) -> List[str]:
    transit = _planet_key(event.get("transit_body"))
    aspect = _aspect_key(event.get("aspect"))
    natal_point = str(event.get("natal_point") or "").strip().upper()
    if transit == "neptune" and aspect == "square" and natal_point == "ASC":
        return [
            "Önemli cümleyi göndermeden önce bir kez sadeleştir.",
            "Niyetini ve sınırını aynı anda söyle.",
            "Yanlış anlaşılma ihtimali olan konuşmayı yazılı teyitle kapat.",
        ]
    if transit == "uranus" and aspect in {"trine", "sextile"} and natal_point.lower() == "mars":
        return [
            "Aynı anda üç fikir açma; birini seçip sonuna kadar götür.",
            "Ürettiğin şeyi küçük bir çıktı ya da paylaşım haline getir.",
            "Öğrenme planını haftalık bir düzene bağla.",
        ]
    if transit == "pluto" and aspect == "sextile" and natal_point.lower() == "pluto":
        return [
            "Gerçekten güçlendiren çevreyi ayıkla.",
            "Uzun vadeli hedefi tek cümlede yeniden tanımla.",
            "Sırf alıştığın için açık tuttuğun kapıları gözden geçir.",
        ]
    bullets = [
        f"{_life_scene(transit_house, detail='short').capitalize()} tarafında bir şeyi sadeleştir.",
        f"{_target_life_label(natal_point, target_house).capitalize()} alanında tek net adım seç.",
        "Ölçülü ilerle; tek seferde her şeyi çözmeye çalışma.",
    ]
    return bullets


def _event_watch_bullets(watchout: str) -> List[str]:
    sentences = _split_sentences(watchout)
    return [cap_sentences(sentence, max_sentences=1) for sentence in sentences[:2] if sentence.strip()]


def _build_event_narrative_fields(card: Mapping[str, Any], event: Mapping[str, Any], horizon: str) -> Dict[str, Any]:
    transit_house, target_house = _transit_target_houses(card, event)
    headline = _title_for_event(event, transit_house, target_house)
    opening = _generic_opening(event, card, transit_house, target_house)
    essence = _generic_essence(event, transit_house, target_house)
    mechanism = _generic_mechanism(card, event, transit_house, target_house)
    asks = _generic_asks(event, transit_house, target_house)
    watchout = _generic_watchout(event, transit_house, target_house)
    what_it_builds = _generic_what_it_builds(event, transit_house, target_house)
    technical_note = _technical_note(card, event, transit_house, target_house)
    why_now = why_now_tr(event)
    guidance = _normalize_bullet_list(
        _event_guidance_bullets(event, transit_house, target_house),
        fallback=["Önce niyeti netleştir.", "Tek bir adım seç ve tamamla."],
        minimum=3,
    )[:3]
    watch_bullets = _normalize_bullet_list(
        _event_watch_bullets(watchout),
        fallback=["Acele tepki verme."],
        minimum=1,
    )[:2]

    out: Dict[str, Any] = dict(card)
    out.update(
        {
            "headline": _clamp_text(headline, max_chars=120, max_sentences=1),
            "opening": _clamp_text(opening, max_chars=300, max_sentences=3),
            "essence": _clamp_text(essence, max_chars=280, max_sentences=2),
            "mechanism": _clamp_text(mechanism, max_chars=320, max_sentences=3),
            "asks": _clamp_text(asks, max_chars=280, max_sentences=2),
            "watchout": _clamp_text(watchout, max_chars=260, max_sentences=2),
            "what_it_builds": _clamp_text(f"Bu dönem sende {what_it_builds} geliştiriyor.", max_chars=180, max_sentences=1),
            "technical_note": _clamp_text(technical_note, max_chars=260, max_sentences=3),
            "why_now": _clamp_text(why_now, max_chars=220, max_sentences=3),
            "guidance": guidance,
            "watch_out": watch_bullets,
            "title": _clamp_text(headline, max_chars=120, max_sentences=1),
            "teaser": _clamp_text(opening, max_chars=300, max_sentences=3),
            "conflict": _clamp_text(essence, max_chars=280, max_sentences=2),
            "shadow": _clamp_text(watchout, max_chars=260, max_sentences=2),
            "upper": _clamp_text(asks, max_chars=280, max_sentences=2),
            "big_picture": _clamp_text(essence, max_chars=280, max_sentences=2),
            "upper_meaning": _clamp_text(f"Bu dönem sende {what_it_builds} geliştiriyor.", max_chars=180, max_sentences=1),
            "potential": "",
            "extra_line": "",
            "time_hint": _clamp_text(why_now, max_chars=220, max_sentences=2),
        }
    )
    return out


def rewrite_event_card_tr(card: Mapping[str, Any], event: Mapping[str, Any], horizon: str) -> Dict[str, Any]:
    out = _build_event_narrative_fields(card, event, horizon)
    for field in (
        "headline",
        "opening",
        "essence",
        "mechanism",
        "asks",
        "watchout",
        "what_it_builds",
        "technical_note",
        "teaser",
        "why_now",
        "conflict",
        "shadow",
        "upper",
        "big_picture",
        "upper_meaning",
        "time_hint",
    ):
        if field in out:
            out[field] = _dedupe_sentences(str(out.get(field) or ""))

    for list_key in ("guidance", "watch_out"):
        raw = out.get(list_key)
        if not isinstance(raw, list):
            continue
        out[list_key] = _clamp_bullets(raw, max_n=3 if list_key == "guidance" else 2)

    out = _dedupe_section_overlap(out)
    out["horizon"] = str(horizon or out.get("horizon") or "").strip().lower() or str(out.get("horizon") or "")
    return out

def why_now_tr(event: Mapping[str, Any]) -> str:
    orb = _safe_float(event.get("orb_deg"), 9.9)
    if orb <= 0.3:
        orb_line = "Etki şu an en yoğun noktasına yakın."
    elif orb <= 1.0:
        orb_line = "Etki güçlü biçimde hissediliyor."
    else:
        orb_line = "Etki şimdiden çalışıyor; ana tema görünür durumda."

    bucket = str(event.get("bucket") or "").strip().lower()
    duration_line = {
        "long": "Bu dalga birkaç ay boyunca katman katman çalışır.",
        "medium": "Bu tema birkaç hafta boyunca gündemde kalır.",
        "short": "Bu etki kısa ama belirgin bir pencere açar.",
    }.get(bucket, "Bu etki bir süre daha gündemde kalır.")

    natal_point = str(event.get("natal_point") or "").strip().upper()
    axis_line = {
        "ASC": "Kimlik hattı aktif.",
        "DSC": "İlişki hattı aktif.",
        "MC": "Yön ve kariyer hattı aktif.",
        "IC": "Ev ve iç güven hattı aktif.",
    }.get(natal_point, "")

    phase = str(event.get("phase") or "").strip().lower()
    phase_line = {
        "applying": "Etki büyüyor.",
        "exact": "Tam odakta.",
        "exactish": "Tam odakta.",
        "separating": "Ana vurgu geçti ama yankısı sürüyor.",
    }.get(phase, "")

    if axis_line and phase_line:
        phase_fragment = {
            "applying": "etki giderek belirginleşiyor",
            "exact": "tema tam odakta",
            "exactish": "tema tam odakta",
            "separating": "ana vurgu geçti ama yankısı sürüyor",
        }.get(phase)
        if phase_fragment:
            axis_line = f"{axis_line[:-1]}; {phase_fragment}."
            phase_line = ""

    lines = [orb_line, duration_line]
    if axis_line:
        lines.append(axis_line)
    if phase_line and normalize(phase_line) not in normalize(" ".join(lines)):
        lines.append(phase_line)
    return _dedupe_sentences(" ".join(lines[:3]))


def _period_muscle_line(event: Mapping[str, Any], scene_house: int | None) -> str:
    if scene_house == 3:
        return "Zamanla neyi söyleyip neyi bırakacağını daha iyi seçersin; ifade sadeleşir."
    if scene_house == 9:
        return "Dağılmadan tek yönteme bağlandığında yön duygun ve uzmanlaşma isteğin birlikte güçlenir."
    if scene_house == 11:
        return "Doğru insanı, doğru hedefi ve doğru mesafeyi seçmek burada kolaylaşır."
    return "Net olanı seçip tekrar edilebilir hale getirdiğinde kazanım kalıcı olur."


def _salient_fallback_excerpt(text: str, max_len: int = 140) -> str:
    parts = _split_sentences(str(text or ""))
    if not parts:
        return ""

    def _is_contextful(part: str) -> bool:
        cleaned = normalize(part)
        return bool(
            re.search(r"\b\d+\s+ev\b", cleaned)
            or any(
                token in cleaned
                for token in (
                    "yükselen",
                    "alçalan",
                    "tepe noktası",
                    "dip noktası",
                    "yöneticisi",
                    "kimlik benlik",
                    "topluluk hedef",
                    "ev kök",
                    "ilişki ortaklık",
                )
            )
        )

    for part in parts:
        if _is_contextful(part):
            return _first_sentence(part, max_len=max_len)
    return _first_sentence(str(text or ""), max_len=max_len)


def _period_conflict_line(event: Mapping[str, Any], fallback: str) -> str:
    aspect = _aspect_key(event.get("aspect"))
    dynamics = ASPECT_DYNAMIC_TR.get(aspect, {})
    transit = _planet_key(event.get("transit_body"))
    risk = PLANET_ESSENCE_TR.get(transit, {}).get("risk", "dağılma")
    if aspect in {"square", "opposition"}:
        base = f"Bu temada {dynamics.get('name', 'gerilim')} öne çıkıyor; {risk} artarsa ayarı kaçırmak kolaylaşır."
    elif aspect == "conjunction":
        base = "Gündem tek noktada büyüdüğü için yük hissi artabilir ve ölçü kolayca kayabilir."
    else:
        base = "Akış açık ama tam da bu yüzden ölçü kaçarsa konu kolayca dağılabilir."
    if fallback and similarity(base, fallback) < 0.5:
        base = f"{base} {_salient_fallback_excerpt(fallback, max_len=120)}"
    return _dedupe_sentences(base)


def _period_shadow_line(event: Mapping[str, Any], fallback: str) -> str:
    aspect = _aspect_key(event.get("aspect"))
    transit = _planet_key(event.get("transit_body"))
    risk = PLANET_ESSENCE_TR.get(transit, {}).get("risk", "dağılma")
    if aspect in {"square", "opposition"}:
        base = f"Otomatik refleks, baskı anında {risk} tarafına kaymak olabilir."
    elif aspect == "conjunction":
        base = "Otomatik refleks, her şeyi aynı anda taşıyıp yükü gereksiz büyütmek olabilir."
    else:
        base = "Otomatik refleks, akış var diye odağı gevşetmek olabilir."
    if fallback and similarity(base, fallback) < 0.45:
        base = f"{base} {_first_sentence(fallback, max_len=90)}"
    return _dedupe_sentences(base)


def _period_upper_line(event: Mapping[str, Any], fallback: str, scene_house: int | None) -> str:
    muscle = _period_muscle_line(event, scene_house)
    transit = _planet_key(event.get("transit_body"))
    gift = PLANET_ESSENCE_TR.get(transit, {}).get("gift", "netlik")
    base = f"Kazanç, {gift} tarafını daha bilinçli kullanabilmende. {muscle}"
    if fallback and similarity(base, fallback) < 0.45:
        base = f"{base} {_salient_fallback_excerpt(fallback, max_len=120)}"
    return _dedupe_sentences(base)


def _period_big_picture_line(event: Mapping[str, Any], fallback: str, scene_house: int | None) -> str:
    point = str(event.get("natal_point") or "").strip().upper()
    if point in {"ASC", "DSC", "MC", "IC"}:
        base = f"Bu süreç {POINT_TR.get(point, point).lower()} hattında daha sakin bir ayar kuruyor."
    elif scene_house:
        base = f"Bu süreç {scene_house}. Ev temasını daha olgun bir çizgiye taşıyor."
    else:
        base = "Bu süreç seni daha net ve daha ölçülü bir hatta topluyor."
    if fallback and similarity(base, fallback) < 0.35:
        return _dedupe_sentences(base)
    return _dedupe_sentences(base)


def _period_context_line(card: Mapping[str, Any], event: Mapping[str, Any]) -> str:
    derived = card.get("derived_context") if isinstance(card.get("derived_context"), Mapping) else {}
    chain_line = build_chain_explainer_tr(event, derived if isinstance(derived, Mapping) else {})
    if chain_line:
        return chain_line

    target = derived.get("natal_target") if isinstance(derived.get("natal_target"), Mapping) else {}
    rulership_houses = target.get("rulership_houses") if isinstance(target.get("rulership_houses"), list) else []
    houses: List[int] = []
    for raw_house in rulership_houses:
        house = _safe_int(raw_house)
        if house and house not in houses:
            houses.append(house)

    if not houses:
        return ""

    labels = [f"{house}. Ev ({_house_scene(house)})" for house in houses[:2]]
    if len(labels) == 1:
        return f"Bu tema {labels[0]} hattına da iner."
    return f"Bu tema {labels[0]} ve {labels[1]} hattına da iner."


def _period_mechanism_line(card: Mapping[str, Any], event: Mapping[str, Any], scene_house: int | None) -> str:
    derived = card.get("derived_context") if isinstance(card.get("derived_context"), Mapping) else {}
    chain_line = build_chain_explainer_tr(event, derived if isinstance(derived, Mapping) else {})

    houses = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}
    transit_house = _safe_int(houses.get("transit_in_natal_house"))
    target_house = _safe_int(houses.get("natal_point_house"))
    natal_point = str(event.get("natal_point") or "").strip().upper()

    lines: List[str] = []
    if chain_line:
        lines.append(chain_line)

    if natal_point == "ASC" and transit_house == 3:
        lines.append("Etki iletişim ritminde başlar; sonra duruşuna/kimliğine yansır.")
        return _clamp_text(" ".join(lines), max_chars=320, max_sentences=3)

    if transit_house and target_house:
        lines.append(
            f"Etki önce {transit_house}. Evde {_house_scene(transit_house)} tarafında belirir; "
            f"sonra {target_house}. Evde {_house_scene(target_house)} tarafına yansır."
        )
    elif transit_house and natal_point in POINT_TR:
        lines.append(
            f"Etki önce {transit_house}. Evde {_house_scene(transit_house)} tarafında belirir; "
            f"sonra {POINT_TR.get(natal_point, natal_point).lower()} hattına yansır."
        )
    elif scene_house:
        lines.append(f"Etki {scene_house}. Evde {_house_scene(scene_house)} tarafında ritmi değiştirir.")

    return _clamp_text(" ".join(line for line in lines if line), max_chars=320, max_sentences=2)


def _clamp_text(text: str, *, max_chars: int, max_sentences: int) -> str:
    cleaned = _dedupe_sentences(_collapse_period_prefix(text))
    if not cleaned:
        return ""
    parts = _split_sentences(cleaned)[: max(1, max_sentences)]
    candidate = " ".join(parts).strip()
    if len(candidate) <= max_chars:
        return candidate
    best = ""
    current: List[str] = []
    for part in parts:
        tentative = " ".join(current + [part]).strip()
        if len(tentative) > max_chars:
            break
        current.append(part)
        best = tentative
    return best or parts[0]


def dedupe_fields(card: Mapping[str, Any], horizon: str) -> Dict[str, Any]:
    out = dict(card)
    for field in (
        "headline",
        "opening",
        "essence",
        "asks",
        "watchout",
        "what_it_builds",
        "technical_note",
        "teaser",
        "why_now",
        "conflict",
        "shadow",
        "upper",
        "big_picture",
        "mechanism",
        "upper_meaning",
    ):
        if field in out:
            out[field] = _dedupe_sentences(str(out.get(field) or ""))

    pairs = [
        ("headline", "opening"),
        ("opening", "essence"),
        ("essence", "asks"),
        ("asks", "what_it_builds"),
        ("teaser", "upper"),
        ("teaser", "big_picture"),
        ("teaser", "mechanism"),
        ("why_now", "conflict"),
        ("upper", "big_picture"),
        ("upper", "mechanism"),
        ("big_picture", "mechanism"),
    ]
    for left, right in pairs:
        if similarity(str(out.get(left) or ""), str(out.get(right) or "")) >= 0.75:
            if horizon == "period":
                if right in {"mechanism", "big_picture"}:
                    out[right] = ""
                elif left == "teaser" and right == "upper":
                    out[right] = ""
            else:
                out["mechanism"] = ""

    if horizon == "period":
        if similarity(str(out.get("teaser") or ""), str(out.get("big_picture") or "")) >= 0.55:
            out["big_picture"] = ""
    return out


def sanitize_connected_points(connected_points: Sequence[Mapping[str, Any]] | None) -> Dict[str, Any]:
    items = connected_points if isinstance(connected_points, Sequence) else []
    houses: List[str] = []
    house_values: List[int] = []
    signs: List[str] = []
    planets: List[str] = []
    chain = ""
    seen = set()

    def _append_unique(bucket: List[str], value: str) -> None:
        key = (id(bucket), value)
        if key in seen:
            return
        seen.add(key)
        bucket.append(value)

    for entry in items:
        if not isinstance(entry, Mapping):
            continue
        kind = str(entry.get("kind") or "").strip().lower()
        raw_value = entry.get("value")

        if kind == "house":
            number = None
            if isinstance(raw_value, int):
                number = raw_value
            else:
                match = re.search(r"\d+", str(raw_value or ""))
                if match:
                    number = int(match.group(0))
            if isinstance(number, int) and 1 <= number <= 12:
                _append_unique(houses, f"{number}. Ev")
                house_values.append(number)
            continue

        if kind == "sign":
            sign = str(raw_value or "").strip().lower()
            if sign in _SIGN_TR:
                _append_unique(signs, _SIGN_TR[sign])
            continue

        if kind == "planet":
            planet = str(raw_value or "").strip().lower()
            if planet in _PLANET_ALLOWLIST:
                _append_unique(planets, _PLANET_TR.get(planet, planet.title()))
            continue

        if kind == "dispositor_chain" and not chain:
            raw_parts = re.split(r"\s*->\s*", str(raw_value or ""))
            safe_parts = []
            for part in raw_parts:
                token = part.strip().lower()
                if token in _PLANET_ALLOWLIST:
                    safe_parts.append(_PLANET_TR.get(token, token.title()))
                if len(safe_parts) >= 4:
                    break
            if safe_parts:
                chain = " -> ".join(safe_parts)

    return {
        "houses": houses,
        "house_values": house_values,
        "signs": signs,
        "planets": planets,
        "dispositor_chain": chain,
        "house_3": 3 in house_values,
        "house_9": 9 in house_values,
    }


def polish_collocations(text: str) -> str:
    out = str(text or "")
    if not out.strip():
        return ""

    replacements = {
        r"\bneptune disiplini\b": "belirsizliği yönetme becerin",
        r"\bneptun disiplini\b": "belirsizliği yönetme becerin",
        r"\bneptün disiplini\b": "belirsizliği yönetme becerin",
        r"\bcapricorn stili\b": "kontrole çekilme hali",
        r"\boğlak stili\b": "kontrole çekilme hali",
    }
    for pattern, value in replacements.items():
        out = re.sub(pattern, value, out, flags=re.IGNORECASE)

    # Keep all allowed points visible; only normalize spacing/punctuation.
    out = re.sub(r"\s{2,}", " ", out).strip()
    out = re.sub(r"\s+([,.;:!?])", r"\1", out)
    out = re.sub(r"\s+,", ",", out)
    out = re.sub(r",\s*,", ", ", out)
    return out


def cap_sentences(text: str, max_sentences: int = 3) -> str:
    raw = str(text or "").strip()
    if not raw:
        return ""
    if max_sentences < 1:
        return ""

    parts = _split_sentences(raw)
    if not parts:
        return ""

    out = " ".join(parts[:max_sentences]).strip()
    if out and out[-1] not in ".!?":
        out += "."
    return out


def _s(x: Any) -> str:
    return str(x or "").strip()


def _first_sentence(text: str, max_len: int = 160) -> str:
    t = restore_ordinals(strip_tech_tokens(str(text or "")).strip())
    if not t:
        return ""
    parts = _split_sentences(t)
    s = parts[0] if parts else t
    if len(s) > max_len:
        s = s[:max_len].rstrip() + "…"
    return s


def _dedupe_sentences(text: str) -> str:
    t = _norm(text)
    if not t:
        return ""
    parts = _split_sentences(t)
    seen: set[str] = set()
    out: List[str] = []
    for p in parts:
        key = normalize(p)
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(p)
    merged = " ".join(out).strip()
    if merged and merged[-1] not in ".!?":
        merged += "."
    return merged


def _clamp_bullets(items: Any, max_n: int = 3) -> List[str]:
    if not isinstance(items, list):
        return []
    out: List[str] = []
    seen: set[str] = set()
    for it in items:
        s = restore_ordinals(strip_tech_tokens(str(it or "")).strip())
        if not s:
            continue
        key = normalize(s)
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
        if len(out) >= max_n:
            break
    return out


def rewrite_period_card_tr(
    card: Mapping[str, Any],
    event: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    ev = dict(event or {})
    out = rewrite_event_card_tr(card, ev, horizon="period")
    transit_house, target_house = _transit_target_houses(out, ev)
    natal_point = str(ev.get("natal_point") or "").strip().upper()
    life_expression = _dedupe_sentences(
        f"Günlük hayatta bu tema en çok {_life_scene(transit_house, detail='short')} tarafında başlar; "
        f"asıl sonucu {_target_life_label(natal_point, target_house)} alanında görünür olur."
    )
    out.update(
        {
            "period_opening": out.get("opening") or out.get("teaser") or "",
            "growth_edge": out.get("watchout") or out.get("shadow") or "",
            "relational_or_life_expression": _clamp_text(life_expression, max_chars=260, max_sentences=2),
            "what_it_builds": out.get("what_it_builds") or "",
            "signature": render_signature_tr(ev) if ev else str(out.get("signature") or ""),
            "signature_tr": render_signature_tr(ev) if ev else str(out.get("signature_tr") or out.get("signature") or ""),
        }
    )
    out["teaser"] = out.get("period_opening") or out.get("teaser") or ""
    out["conflict"] = out.get("essence") or out.get("conflict") or ""
    out["shadow"] = out.get("growth_edge") or out.get("shadow") or ""
    out["upper"] = out.get("asks") or out.get("upper") or ""
    out["upper_meaning"] = out.get("what_it_builds") or out.get("upper_meaning") or ""
    out["big_picture"] = out.get("essence") or out.get("big_picture") or ""
    out["mechanism"] = out.get("mechanism") or ""
    out["watch_out"] = _clamp_bullets(out.get("watch_out"), max_n=2)
    out["guidance"] = _clamp_bullets(out.get("guidance"), max_n=3)
    return _dedupe_section_overlap(out)


def normalize_card_text_tr(card: Mapping[str, Any]) -> Dict[str, Any]:
    normalized: Dict[str, Any] = dict(card)

    for field in ("title", "conflict", "shadow", "upper", "extra_line", "time_hint"):
        value = str(normalized.get(field) or "")
        value = humanize_tr_text(value)
        value = tr_normalize(value)
        value = polish_collocations(value)
        cap = 2 if field in {"title", "time_hint"} else 3
        normalized[field] = cap_sentences(value, max_sentences=cap)

    guidance = normalized.get("guidance") if isinstance(normalized.get("guidance"), list) else []
    normalized["guidance"] = _normalize_bullet_list(
        guidance,
        fallback=["Yaz tek cümle niyet.", "Çıkar taslak, sonra gönder.", "Bağla ritmi mini-rutine."],
        minimum=3,
    )[:3]

    watch = normalized.get("watch_out") if isinstance(normalized.get("watch_out"), list) else []
    normalized["watch_out"] = _normalize_bullet_list(watch, fallback=["Açma aynı anda iki kanal.", "Sabitle önce niyeti, sonra hız ver."], minimum=2)[:2]
    return normalized


def apply_house_theme_hints(
    card: Mapping[str, Any],
    injection_bits: Mapping[str, Any],
    context: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    out: Dict[str, Any] = dict(card)
    ctx = context if isinstance(context, Mapping) else {}

    transit_house = _safe_int(ctx.get("transit_house"))
    is_house_3 = bool(injection_bits.get("house_3")) or transit_house == 3
    is_house_9 = bool(injection_bits.get("house_9")) or transit_house == 9

    if is_house_3:
        conflict = str(out.get("conflict") or "")
        if not _has_any(conflict, ("mesaj", "konuş", "yazı", "yanlış anlaşıl", "yakın çevre", "dijital")):
            conflict = f"{conflict} Mesaj ve konuşma trafiğinde yanlış anlaşılmayı azaltmak kritik."
            out["conflict"] = cap_sentences(tr_normalize(conflict), max_sentences=3)
        guidance = out.get("guidance") if isinstance(out.get("guidance"), list) else []
        if not _list_has_any(guidance, ("mesaj", "konuş", "yaz", "yakın çevre", "dijital")):
            guidance = list(guidance)
            clause = "Mesajını kısa ve net yaz; yakın çevre iletişiminde teyit al."
            if len(guidance) < 3:
                guidance.append(clause)
            elif guidance:
                guidance[-1] = clause
            out["guidance"] = [_normalize_bullet(x) for x in guidance][:3]

    if is_house_9:
        upper = str(out.get("upper") or "")
        if not _has_any(upper, ("öğren", "uzmanlaş", "yayın", "dünya görüş", "yabancı dil", "uzak")):
            upper = f"{upper} Öğrenme, uzmanlaşma ve dünya görüşünü güncelleme burada güçlenir."
            out["upper"] = cap_sentences(tr_normalize(upper), max_sentences=3)
        guidance = out.get("guidance") if isinstance(out.get("guidance"), list) else []
        if not _list_has_any(guidance, ("öğren", "uzman", "yayın", "yabancı dil", "uzak")):
            guidance = list(guidance)
            clause = "Öğrenme veya yabancı dil planını haftalık rutine bağla."
            if len(guidance) < 3:
                guidance.append(clause)
            elif guidance:
                guidance[-1] = clause
            out["guidance"] = [_normalize_bullet(x) for x in guidance][:3]

    return out


def apply_copy_quality_layer(
    card: Mapping[str, Any],
    connected_points: Sequence[Mapping[str, Any]] | None,
    context: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    if not _COPY_QUALITY_ENABLED:
        return dict(card)
    bits = sanitize_connected_points(connected_points)
    motifs = select_path_motifs(bits, context=context)
    out = normalize_card_text_tr(card)
    out = inject_selected_motifs(out, motifs, bits, context=context)
    out = apply_house_theme_hints(out, bits, context=context)
    out = _inject_phrase_pack(out, context=context)
    out = _dedupe_section_overlap(out)
    out = finalize_daily_lengths(out)
    if _ENABLE_MICRO_LLM_POLISH and _MICRO_LLM_PROVIDER != "none":
        out = polish_with_llm(out, {"connected_points": list(connected_points or []), "context": dict(context or {})})
    return out


def polish_with_llm(text_blocks: Mapping[str, Any], context: Mapping[str, Any]) -> Dict[str, Any]:
    _ = context
    # Placeholder hook only; provider integration intentionally disabled.
    return dict(text_blocks)


def _inject_phrase_pack(card: Mapping[str, Any], context: Mapping[str, Any] | None) -> Dict[str, Any]:
    out = dict(card)
    ctx = context if isinstance(context, Mapping) else {}
    pack = out.get("natal_context_pack") if isinstance(out.get("natal_context_pack"), Mapping) else {}

    event = {
        "event_id": str(out.get("event_id") or ""),
        "transit_body": str(ctx.get("transit_planet") or ""),
        "aspect": str(ctx.get("aspect") or ""),
        "natal_point": str(ctx.get("target") or ""),
        "orb_deg": _safe_float(ctx.get("orb_deg"), 9.9),
        "bucket": str(ctx.get("duration") or ""),
        "phase": str(ctx.get("phase") or ""),
        "houses": {"transit_in_natal_house": _safe_int(ctx.get("transit_house"))},
    }
    phrase = compose_phrase_pack(
        transit_body=str(event["transit_body"]),
        aspect=str(event["aspect"]),
        natal_point=str(event["natal_point"]),
        context_pack=pack,
        event=event,
        max_len={"conflict": 2, "shadow": 2, "upper": 2},
    )

    conflict_label = str(phrase.get("conflict_label") or "").strip()
    conflict_tone = str(phrase.get("conflict_tone") or "").strip()
    if conflict_label:
        out["conflict_label"] = conflict_label
    if conflict_tone:
        out["conflict_tone"] = conflict_tone
    tone = str(phrase.get("tone") or "").strip()
    if tone:
        out["tone"] = tone
    section_labels = phrase.get("section_labels") if isinstance(phrase.get("section_labels"), Mapping) else {}
    if section_labels:
        out["section_labels"] = dict(section_labels)
    why_now = str(phrase.get("why_now") or "").strip()
    if why_now:
        out["why_now"] = why_now

    title = str(phrase.get("title") or "").strip()
    if title:
        out["title"] = title

    scene_line = str(phrase.get("scene_line") or "").strip()
    conflict = str(out.get("conflict") or "").strip()
    conflict_add = str(phrase.get("conflict_add") or "").strip()
    if scene_line:
        conflict = _append_unique_sentence(scene_line, conflict)
    if conflict_add:
        conflict = _append_unique_sentence(conflict_add, conflict)
    out["conflict"] = conflict

    shadow = str(out.get("shadow") or "").strip()
    shadow_add = str(phrase.get("shadow_add") or "").strip()
    if shadow_add:
        shadow = _append_unique_sentence(shadow_add, shadow)
    out["shadow"] = shadow

    upper = str(out.get("upper") or "").strip()
    upper_add = str(phrase.get("upper_add") or "").strip()
    if upper_add:
        upper = _append_unique_sentence(upper_add, upper)
    out["upper"] = upper

    guidance = out.get("guidance") if isinstance(out.get("guidance"), list) else []
    guidance_add = phrase.get("guidance_add") if isinstance(phrase.get("guidance_add"), list) else []
    out["guidance"] = _merge_unique_list([str(x) for x in guidance_add], [str(x) for x in guidance], cap=3)

    watch = out.get("watch_out") if isinstance(out.get("watch_out"), list) else []
    watch_add = phrase.get("watch_out_add") if isinstance(phrase.get("watch_out_add"), list) else []
    out["watch_out"] = _merge_unique_list([str(x) for x in watch_add], [str(x) for x in watch], cap=2)
    return out


def select_path_motifs(injection_bits: Mapping[str, Any], context: Mapping[str, Any] | None) -> Dict[str, Any]:
    ctx = context if isinstance(context, Mapping) else {}
    node_weights = _THEME_BANK["event_generation"]["path_scoring"]["node_weights"]
    edge_weights = _THEME_BANK["event_generation"]["path_scoring"]["edge_weights"]
    top_k = int(_THEME_BANK["event_generation"]["motif_selection"]["top_motifs"])

    motifs: List[Dict[str, Any]] = []
    houses = injection_bits.get("house_values") if isinstance(injection_bits.get("house_values"), list) else []
    signs = injection_bits.get("signs") if isinstance(injection_bits.get("signs"), list) else []
    chain = str(injection_bits.get("dispositor_chain") or "").strip()

    if houses:
        h = int(houses[0])
        score = 1.0 * float(node_weights.get("natal_target_house", 0.9)) * float(edge_weights.get("house_edge", 0.6))
        motifs.append({"type": "house_scene", "value": h, "score": round(min(1.0, score), 3)})
    if signs:
        score = 1.0 * float(node_weights.get("natal_target_sign", 0.7)) * float(edge_weights.get("sign_edge", 0.6))
        motifs.append({"type": "sign_style", "value": signs[0], "score": round(min(1.0, score), 3)})
    if chain:
        score = 1.0 * float(node_weights.get("dispositor", 0.6)) * float(edge_weights.get("dispositor_edge", 0.8))
        motifs.append({"type": "dispositor_hint", "value": chain, "score": round(min(1.0, score), 3)})

    transit_house = _safe_int(ctx.get("transit_house"))
    if transit_house and all(m.get("type") != "house_scene" for m in motifs):
        score = 0.9 * float(node_weights.get("transit_planet", 0.9)) * float(edge_weights.get("house_edge", 0.6))
        motifs.append({"type": "house_scene", "value": transit_house, "score": round(min(1.0, score), 3)})

    motifs.sort(key=lambda item: _safe_float(item.get("score"), 0.0), reverse=True)
    selected = motifs[:top_k]

    must = _THEME_BANK["event_generation"]["motif_selection"]["must_include"]
    if "house_scene" in must and all(item.get("type") != "house_scene" for item in selected) and transit_house:
        selected.append({"type": "house_scene", "value": transit_house, "score": 0.3})

    selected = selected[:top_k]
    return {"selected": selected}


def inject_selected_motifs(
    card: Mapping[str, Any],
    motifs: Mapping[str, Any],
    injection_bits: Mapping[str, Any],
    context: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    out = dict(card)
    selected = motifs.get("selected") if isinstance(motifs.get("selected"), list) else []
    if not selected:
        return out

    motif_types = {str(item.get("type")): item for item in selected if isinstance(item, Mapping)}
    house_motif = motif_types.get("house_scene")
    sign_motif = motif_types.get("sign_style")
    disp_motif = motif_types.get("dispositor_hint")

    if house_motif:
        house = _safe_int(house_motif.get("value"))
        scene = (_THEME_BANK["houses"].get(house) or {}).get("scene")
        if scene:
            conflict = str(out.get("conflict") or "")
            if not _has_any(conflict, ("mesaj", "öğren", "yakın çevre", "yayın", "takvim", "anlaşma")):
                conflict = f"{conflict} Etki {house}. Evde {scene} üzerinden görünür olur."
                out["conflict"] = cap_sentences(tr_normalize(conflict), max_sentences=3)

    if sign_motif:
        sign = str(sign_motif.get("value") or "")
        upper = str(out.get("upper") or "")
        if sign and sign not in upper:
            upper = f"{upper} {sign} stili burada tempoyu belirliyor."
            out["upper"] = cap_sentences(tr_normalize(upper), max_sentences=3)

    if disp_motif:
        chain = str(disp_motif.get("value") or "")
        extra_line = str(out.get("extra_line") or "")
        if chain and chain not in extra_line:
            extra_line = f"{extra_line} Dispozitor akışı: {chain}."
            out["extra_line"] = cap_sentences(tr_normalize(extra_line), max_sentences=1)

    return out


def finalize_daily_lengths(card: Mapping[str, Any]) -> Dict[str, Any]:
    out = dict(card)
    daily = _THEME_BANK["modes"]["daily"]["length"]
    out["conflict"] = cap_sentences(str(out.get("conflict") or ""), max_sentences=int(daily["conflict_sentences"][1]))
    out["shadow"] = cap_sentences(str(out.get("shadow") or ""), max_sentences=int(daily["shadow_sentences"][1]))
    out["upper"] = cap_sentences(str(out.get("upper") or ""), max_sentences=int(daily["upper_sentences"][1]))
    out["extra_line"] = cap_sentences(str(out.get("extra_line") or ""), max_sentences=int(daily["extra_line_sentences"][1]))
    guidance = out.get("guidance") if isinstance(out.get("guidance"), list) else []
    watch = out.get("watch_out") if isinstance(out.get("watch_out"), list) else []
    out["guidance"] = _normalize_bullet_list(
        guidance,
        fallback=["Yaz tek cümle niyet.", "Çıkar taslak, sonra gönder.", "Bağla ritmi mini-rutine."],
        minimum=3,
    )[: int(daily["guidance_bullets"])]
    out["watch_out"] = _normalize_bullet_list(
        watch,
        fallback=["Açma aynı anda iki kanal.", "Sabitle önce niyeti, sonra hız ver."],
        minimum=2,
    )[: int(daily["watch_out_bullets"])]
    return out


def build_period_copy(
    *,
    selected_events: Sequence[Mapping[str, Any]],
    natal_snapshot: Mapping[str, Any] | None = None,
    dominant_house: int | None,
    dominant_planet: str,
    pressure: float,
    support: float,
    domains: Sequence[str],
) -> Dict[str, str]:
    houses = []
    for event in selected_events:
        houses_map = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}
        house = _safe_int(houses_map.get("transit_in_natal_house"))
        if house:
            houses.append(house)
    house_counter = Counter(houses)
    main_house = dominant_house or (house_counter.most_common(1)[0][0] if house_counter else 3)
    house_pack = _THEME_BANK["houses"].get(main_house) or _THEME_BANK["houses"][3]
    scene = house_pack["scene"]
    motif = house_pack["motif"]
    domain_text = ", ".join(str(x) for x in domains[:2]) if domains else "zihin"

    if pressure >= support + 0.08:
        mode = "pressure"
    elif support >= pressure + 0.08:
        mode = "expansion"
    else:
        mode = "calibration"

    root_causes = build_root_causes(selected_events, natal_snapshot or {})
    primary = root_causes[0] if root_causes else {"key": "identity_spine", "evidence": []}
    secondary = root_causes[1] if len(root_causes) > 1 else {"key": "mind_axis_3_9", "evidence": []}

    p1 = _period_paragraph_for_root(primary, mode=mode, paragraph_idx=1, domain_text=domain_text)
    p2 = _period_paragraph_for_root(secondary, mode=mode, paragraph_idx=2, domain_text=domain_text)
    p3 = _period_transform_paragraph(
        root_causes=root_causes,
        mode=mode,
        main_house=main_house,
        scene=scene,
        motif=motif,
    )

    paragraphs = [p1, p2, p3]
    normalized_paragraphs: List[str] = []
    seen = set()
    for paragraph in paragraphs:
        cleaned = cap_sentences(tr_normalize(polish_collocations(paragraph)), max_sentences=4)
        key = " ".join(cleaned.lower().split())
        if not cleaned or key in seen:
            continue
        seen.add(key)
        normalized_paragraphs.append(cleaned)
    core_story = "\n\n".join(normalized_paragraphs[:3])
    core_story = _period_general_climate(core_story)
    core_story = humanize_tr_text(core_story, max_sentences=12)

    upper_lines = [
        "Bu dönemde nedeni fark ettiğinde adımlarını daha kolay netleştirirsin.",
        "Sürecini sadeleştirdikçe sonuçları daha az yorularak alırsın.",
        "Dönem sonunda sana iyi gelen ritmi daha kalıcı hale getirebilirsin.",
    ]
    if any(cause.get("key") == "mind_axis_3_9" for cause in root_causes):
        upper_lines.insert(1, "3/9 hattı hareketliyken öğrenme planını küçük adımlara bölmek işleri hızlandırır.")
    if any(cause.get("key") == "identity_spine" for cause in root_causes):
        upper_lines.insert(1, "Kimlik tarafı netleştikçe dış yorumlar seni daha az dağıtır.")
    upper = cap_sentences(" ".join(upper_lines[:5]), max_sentences=4)
    upper = humanize_tr_text(upper, max_sentences=4)
    return {"core_story": core_story, "upper_meaning": upper, "root_causes": root_causes}


def _period_general_climate(text: str) -> str:
    out = str(text or "").strip()
    if not out:
        return out
    replacements = (
        (r"\bana hat\b", "dönemin havası"),
        (r"\bkalibrasyon\b", "denge ayarı"),
        (r"\bgüncelleme\b", "değişim"),
        (r"\bnetlik ayarı\b", "netleşme"),
        (r"\byöntem güncellemesi\b", "ritim değişimi"),
    )
    paragraphs = [p.strip() for p in out.split("\n\n") if p.strip()]
    normalized: List[str] = []
    for paragraph in paragraphs:
        line = paragraph
        for pattern, dst in replacements:
            line = re.sub(pattern, dst, line, flags=re.IGNORECASE)
        normalized.append(line)
    if normalized and not normalized[0].lower().startswith("dönemin havası"):
        normalized[0] = f"Dönemin havası: {normalized[0]}"
    return "\n\n".join(normalized)


def build_root_causes(
    selected_events: Sequence[Mapping[str, Any]],
    natal_snapshot: Mapping[str, Any] | None,
) -> List[Dict[str, Any]]:
    events = [item for item in selected_events if isinstance(item, Mapping)]
    natal = natal_snapshot if isinstance(natal_snapshot, Mapping) else {}
    if not events:
        return []

    bodies = natal.get("bodies") if isinstance(natal.get("bodies"), list) else []
    first_house_natal = 0
    for body in bodies:
        if not isinstance(body, Mapping):
            continue
        if _safe_int(body.get("house")) == 1:
            first_house_natal += 1
    first_density = min(1.0, first_house_natal / 3.0)
    asc_present = 1.0 if isinstance(natal.get("angles"), Mapping) and natal.get("angles", {}).get("ASC") else 0.0

    angle_hits = 0
    outer_angle_hits = 0
    mind_hits = 0
    mirror_house_hits = 0
    mercury_chain_hits = 0
    uranus_mars_candidates: List[Mapping[str, Any]] = []
    evidence_map: Dict[str, List[str]] = {
        "identity_spine": [],
        "mind_axis_3_9": [],
        "mirror_axis_1_7": [],
        "method_shift_9_virgo": [],
    }
    evidence_id_map: Dict[str, List[str]] = {
        "identity_spine": [],
        "mind_axis_3_9": [],
        "mirror_axis_1_7": [],
        "method_shift_9_virgo": [],
    }

    natal_mars_house, natal_mars_sign = _natal_mars_signature(natal)
    for event in events:
        houses = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}
        transit_house = _safe_int(houses.get("transit_in_natal_house"))
        target_house = _safe_int(houses.get("natal_point_house"))
        natal_point = str(event.get("natal_point") or "").upper()
        body = str(event.get("transit_body") or "").lower()
        aspect = str(event.get("aspect") or "").lower()

        is_angle = natal_point in {"ASC", "DSC", "MC", "IC"}
        event_id = str(event.get("event_id") or "").strip()
        if is_angle or transit_house in {1, 4, 7, 10}:
            angle_hits += 1
            evidence_map["identity_spine"].append(_event_evidence(event))
            if event_id:
                evidence_id_map["identity_spine"].append(event_id)
        if (is_angle or transit_house == 1) and body in {"neptune", "pluto", "saturn", "uranus"}:
            outer_angle_hits += 1
            evidence_map["identity_spine"].append(_event_evidence(event))
            if event_id:
                evidence_id_map["identity_spine"].append(event_id)

        if transit_house in {3, 9} or target_house in {3, 9}:
            mind_hits += 1
            evidence_map["mind_axis_3_9"].append(_event_evidence(event))
            if event_id:
                evidence_id_map["mind_axis_3_9"].append(event_id)

        if (natal_point in {"ASC", "DSC"}) or (transit_house in {1, 7} and target_house in {1, 7}):
            evidence_map["mirror_axis_1_7"].append(_event_evidence(event))
            if event_id:
                evidence_id_map["mirror_axis_1_7"].append(event_id)
        if transit_house in {1, 7} or target_house in {1, 7}:
            mirror_house_hits += 1

        if _has_mercury_dispositor(event):
            mercury_chain_hits += 1
            evidence_map["mind_axis_3_9"].append(_event_evidence(event))
            if event_id:
                evidence_id_map["mind_axis_3_9"].append(event_id)

        if body == "uranus" and aspect in {"trine", "sextile", "conjunction", "opposition", "square"}:
            target_planet = str(event.get("natal_point") or "").strip().lower()
            if target_planet == "mars":
                uranus_mars_candidates.append(event)

    total = max(1, len(events))
    identity_score = (
        0.20 * first_density
        + 0.30 * asc_present
        + 0.25 * min(1.0, angle_hits / total * 1.8)
        + 0.25 * min(1.0, outer_angle_hits / total * 2.4)
    )

    mind_score = (
        0.75 * min(1.0, mind_hits / total * 1.8)
        + 0.25 * min(1.0, mercury_chain_hits / max(1, total // 2 or 1))
    )

    mirror_score = (
        0.55 * min(1.0, len(evidence_map["mirror_axis_1_7"]) / total * 2.0)
        + 0.45 * min(1.0, mirror_house_hits / total * 1.8)
    )

    method_score = 0.0
    if uranus_mars_candidates:
        has_9th = False
        has_virgo = False
        for event in uranus_mars_candidates:
            houses = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}
            event_target_house = _safe_int(houses.get("natal_point_house"))
            if event_target_house == 9 or natal_mars_house == 9:
                has_9th = True
            event_sign = _event_target_sign(event)
            if event_sign == "virgo" or natal_mars_sign == "virgo":
                has_virgo = True
            evidence_map["method_shift_9_virgo"].append(_event_evidence(event, suffix="(9th Virgo)"))
            event_id = str(event.get("event_id") or "").strip()
            if event_id:
                evidence_id_map["method_shift_9_virgo"].append(event_id)
        method_score = 0.40
        if has_9th:
            method_score += 0.30
        if has_virgo:
            method_score += 0.30
        method_score = min(1.0, method_score)

    candidates: List[Dict[str, Any]] = [
        {
            "key": "identity_spine",
            "score": round(identity_score, 3),
            "evidence": _dedupe_strings(evidence_map["identity_spine"])[:3],
            "evidence_ids": _dedupe_strings(evidence_id_map["identity_spine"])[:3],
        },
        {
            "key": "mind_axis_3_9",
            "score": round(mind_score, 3),
            "evidence": _dedupe_strings(evidence_map["mind_axis_3_9"])[:3],
            "evidence_ids": _dedupe_strings(evidence_id_map["mind_axis_3_9"])[:3],
        },
        {
            "key": "mirror_axis_1_7",
            "score": round(mirror_score, 3),
            "evidence": _dedupe_strings(evidence_map["mirror_axis_1_7"])[:3],
            "evidence_ids": _dedupe_strings(evidence_id_map["mirror_axis_1_7"])[:3],
        },
    ]
    if method_score > 0:
        candidates.append(
            {
                "key": "method_shift_9_virgo",
                "score": round(method_score, 3),
                "evidence": _dedupe_strings(evidence_map["method_shift_9_virgo"])[:3],
                "evidence_ids": _dedupe_strings(evidence_id_map["method_shift_9_virgo"])[:3],
            }
        )

    filtered = [item for item in candidates if float(item.get("score") or 0.0) >= 0.35]
    filtered.sort(key=lambda item: (-float(item.get("score") or 0.0), str(item.get("key") or "")))
    return filtered


def _period_paragraph_for_root(
    cause: Mapping[str, Any],
    *,
    mode: str,
    paragraph_idx: int,
    domain_text: str,
) -> str:
    key = str(cause.get("key") or "")
    evidence = ", ".join(_dedupe_strings(cause.get("evidence") or [])[:2]) or "seçili transitler"
    if paragraph_idx == 1:
        if key == "identity_spine":
            return f"Bu dönem kimlik omurgasına dokunuyor çünkü açıların ağırlığı ASC/1.ev eksenine biniyor: {evidence}."
        if key == "mind_axis_3_9":
            return f"Bu dönem zihinsel omurgayı zorluyor çünkü 3/9 hattı tekrar eden şekilde aktif: {evidence}."
        if key == "mirror_axis_1_7":
            return f"Bu dönem ilişki aynasını büyütüyor çünkü 1/7 ekseni aynı anda uyarılıyor: {evidence}."
        if key == "method_shift_9_virgo":
            return f"Bu dönem yöntemi değiştiriyor çünkü 9.ev Başak hattı Uranüs etkisiyle açılıyor: {evidence}."
    if key == "mind_axis_3_9":
        return f"Zihin ve ifade hattı bu yüzden devrede; {domain_text} tarafında karar kalitesi kullanılan metoda bağlı: {evidence}."
    if key == "mirror_axis_1_7":
        return f"İlişki aynası bu yüzden güçlü; sınır ve karşılıklılık dili güncellendikçe gerilim düşer: {evidence}."
    if key == "identity_spine":
        return f"Kimlik hattı ikinci dalga olarak çalışıyor; dış geri bildirim iç omurgayı kalibre ediyor: {evidence}."
    if key == "method_shift_9_virgo":
        return f"Yöntem tarafı bu yüzden kritik; dağınık hız yerine düzenli deneme ritmi kazandırır: {evidence}."
    if mode == "pressure":
        return "İkinci hat baskıyı davranış modeline çevirme testinde; netlik tepkiden önce gelince dönem yumuşar."
    if mode == "expansion":
        return "İkinci hat fırsatı kalıcı kas haline getirme testinde; seçici odak akışı büyütür."
    return "İkinci hat kalibrasyon testi; hız ve çerçeve birlikte güncellendiğinde sonuç temizleşir."


def _period_transform_paragraph(
    *,
    root_causes: Sequence[Mapping[str, Any]],
    mode: str,
    main_house: int,
    scene: str,
    motif: str,
) -> str:
    keys = {str(item.get("key") or "") for item in root_causes}
    if "method_shift_9_virgo" in keys:
        return (
            f"Bu dönem {scene} tarafında küçük bir yöntem değişikliğini büyütüyor. "
            "Asıl kazanım, hevesi mikro denemelerden çıkıp kalıcı bir öğrenme ve üretim düzenine bağladığında geliyor."
        )
    if "identity_spine" in keys and "mirror_axis_1_7" in keys:
        return (
            f"Bu dönem {motif} temasını daha çok ilişki dili ve sınır cümleleri üzerinden çalıştırıyor. "
            "Asıl kazanım, karşı tarafı doğru okuyup kendi merkezini daha sakin ve tutarlı kurabilmek."
        )
    if mode == "pressure":
        return (
            f"Bu dönem {scene} tarafında tekrar ve net çerçeve istiyor. "
            "Baskıyı dağıtmak yerine tek kanallı bir yönteme çevirdiğinde daha güvenilir bir düzen kuruyorsun."
        )
    if mode == "expansion":
        return (
            f"Bu dönem {scene} tarafında açılan fırsatları daha seçici kullanmanı istiyor. "
            "Küçük ama tekrarlı hamleler büyümeyi daha görünür ve daha sürdürülebilir hale getirir."
        )
    return (
        f"Bu dönem {scene} tarafında daha bilinçli bir ayar kuruyor. "
        f"{motif.capitalize()} burada ana tema; sadeleştikçe içerideki yön hissi daha netleşiyor."
    )


def _append_unique_sentence(base: str, addon: str) -> str:
    left = str(base or "").strip()
    right = str(addon or "").strip()
    if not right:
        return left
    if not left:
        return right
    left_norm = " ".join(left.lower().split())
    right_norm = " ".join(right.lower().split())
    if right_norm in left_norm:
        return left
    return f"{left} {right}".strip()


def _merge_unique_list(base: Sequence[str], addon: Sequence[str], *, cap: int) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in list(base) + list(addon):
        raw = str(item or "").strip()
        if not raw:
            continue
        key = " ".join(raw.lower().split())
        if key in seen:
            continue
        seen.add(key)
        out.append(raw)
        if len(out) >= cap:
            break
    return out


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _has_any(text: str, keywords: Sequence[str]) -> bool:
    haystack = str(text or "").lower()
    return any(keyword in haystack for keyword in keywords)


def _list_has_any(items: Sequence[Any], keywords: Sequence[str]) -> bool:
    for item in items:
        if _has_any(str(item or ""), keywords):
            return True
    return False


def _normalize_bullet(text: Any, max_words: int = 14) -> str:
    value = cap_sentences(polish_collocations(tr_normalize(str(text or ""))), max_sentences=1)
    if not value:
        return ""
    value = re.sub(r"^\s*\d+\.?\s*ev\b[^:;,.!?-]*[:\-]?\s*", "", value, flags=re.IGNORECASE)
    value = re.sub(r"^\s*[^:]{1,24}:\s*", "", value).strip()
    words = value.split()
    if not words:
        return ""
    if len(words) > max_words:
        words = words[:max_words]
        value = " ".join(words).rstrip(".,;:!?") + "."
    first = words[0].lower().strip(".,;:!?") if words else ""
    compact = re.sub(r"[^a-zA-Z0-9çğıöşüÇĞİÖŞÜ ]", "", value).strip().lower()
    if not compact or re.fullmatch(r"[\d. ]+", compact):
        return ""
    if len(words) <= 2:
        return ""

    if first not in _VERB_STARTS:
        lowered = value.lower()
        if "yaz" in lowered:
            value = f"Yaz {value[0].lower() + value[1:] if len(value) > 1 else value.lower()}"
        elif "gonder" in lowered or "gönder" in lowered:
            value = "Çıkar taslak, sonra gönder."
        elif "acma" in lowered or "açma" in lowered:
            value = "Açma aynı anda iki kanal."
        else:
            return ""
    value = " ".join(value.split()).strip()
    if value and value[-1] not in ".!?":
        value += "."
    return value


def _normalize_bullet_list(items: Sequence[Any], *, fallback: Sequence[str], minimum: int) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in items:
        normalized = _normalize_bullet(item)
        key = normalized.lower()
        if not normalized or key in seen:
            continue
        seen.add(key)
        out.append(normalized)
    for item in fallback:
        if len(out) >= minimum:
            break
        normalized = _normalize_bullet(item)
        key = normalized.lower()
        if not normalized or key in seen:
            continue
        seen.add(key)
        out.append(normalized)
    return out


def _event_evidence(event: Mapping[str, Any], *, suffix: str = "") -> str:
    body = str(event.get("transit_body") or "").strip().title()
    aspect = str(event.get("aspect") or "").strip().lower()
    point = str(event.get("natal_point") or "").strip().upper()
    if point and point not in {"ASC", "DSC", "MC", "IC"}:
        point = point.title()
    if not body:
        return ""
    chunk = f"{body} {aspect} {point}".strip()
    if suffix:
        chunk = f"{chunk} {suffix}".strip()
    return chunk


def _natal_mars_signature(natal_snapshot: Mapping[str, Any]) -> tuple[int | None, str]:
    bodies = natal_snapshot.get("bodies") if isinstance(natal_snapshot.get("bodies"), list) else []
    for body in bodies:
        if not isinstance(body, Mapping):
            continue
        if str(body.get("body") or "").strip().lower() != "mars":
            continue
        house = _safe_int(body.get("house"))
        sign = str(body.get("sign") or "").strip().lower()
        return house, sign
    return None, ""


def _event_target_sign(event: Mapping[str, Any]) -> str:
    ctx = event.get("natal_context_pack") if isinstance(event.get("natal_context_pack"), Mapping) else {}
    target = ctx.get("target") if isinstance(ctx.get("target"), Mapping) else {}
    sign = str(target.get("sign") or "").strip().lower()
    if sign:
        return sign
    return ""


def _has_mercury_dispositor(event: Mapping[str, Any]) -> bool:
    context = event.get("natal_context_pack") if isinstance(event.get("natal_context_pack"), Mapping) else {}
    disp = context.get("dispositor") if isinstance(context.get("dispositor"), Mapping) else {}
    planet = str(disp.get("planet") or "").strip().lower()
    if planet == "mercury":
        return True
    connected = event.get("connected_points") if isinstance(event.get("connected_points"), list) else []
    for item in connected:
        if not isinstance(item, Mapping):
            continue
        value = str(item.get("value") or "").strip().lower()
        kind = str(item.get("kind") or "").strip().lower()
        if kind == "dispositor_chain" and "mercury" in value:
            return True
    return False


def _dedupe_strings(values: Sequence[Any]) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in values:
        text = str(item or "").strip()
        if not text:
            continue
        key = " ".join(text.lower().split())
        if key in seen:
            continue
        seen.add(key)
        out.append(text)
    return out


def _dedupe_section_overlap(card: Mapping[str, Any]) -> Dict[str, Any]:
    out = dict(card)
    seen: set[str] = set()

    def _strip_sentences(text: str) -> str:
        parts = _split_sentences(str(text or "").strip())
        cleaned: List[str] = []
        for part in parts:
            lowered = normalize(part)
            if re.match(r"^\s*Sahne\s", part, flags=re.IGNORECASE):
                continue
            if " sahne " in f" {lowered} ":
                continue
            if "vurduğu yer" in lowered or "vurdugu yer" in lowered:
                continue
            key = normalize(part)
            if not key or key in seen:
                continue
            seen.add(key)
            cleaned.append(part)
        merged = " ".join(cleaned).strip()
        if merged and merged[-1] not in ".!?":
            merged += "."
        return merged

    for field in (
        "opening",
        "essence",
        "asks",
        "watchout",
        "what_it_builds",
        "technical_note",
        "teaser",
        "why_now",
        "conflict",
        "shadow",
        "upper",
        "headline",
        "big_picture",
        "mechanism",
        "upper_meaning",
    ):
        if field in out:
            out[field] = _strip_sentences(out.get(field) or "")

    def _drop_if_similar(primary: str, secondary: str, threshold: float = 0.8) -> None:
        left = str(out.get(primary) or "").strip()
        right = str(out.get(secondary) or "").strip()
        if similarity(left, right) >= threshold:
            out[secondary] = ""

    _drop_if_similar("headline", "big_picture", 0.8)
    _drop_if_similar("headline", "upper", 0.8)
    _drop_if_similar("big_picture", "mechanism", 0.8)
    _drop_if_similar("teaser", "why_now", 0.8)
    _drop_if_similar("teaser", "upper", 0.8)
    _drop_if_similar("why_now", "conflict", 0.8)
    horizon = str(out.get("horizon") or "").strip().lower()
    return dedupe_fields(out, horizon="period" if horizon == "period" else "daily")
