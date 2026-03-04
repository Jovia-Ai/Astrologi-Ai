from __future__ import annotations

import hashlib
import re
from typing import Any, Dict, List, Mapping, Sequence

from app.transit.narrative.point_policy import is_public_point, normalize_point_token

BLOCKED_TOKENS: set[str] = set()

# --- P0: LANGUAGE ONLY ---
# Teknik kelimeler public metne sızmasın.
_TECH_TOKENS_RE = re.compile(
    r"\b("
    r"orb|orb_deg|exactish|exact|applying|separating|square|trine|sextile|opposition|conjunction|"
    r"asc|dsc|mc|ic|t:\d+->n:\d+|n:\d+|t:\d+"
    r")\b",
    flags=re.IGNORECASE,
)

HOUSE_LABEL_TR = {
    1: "kimlik/benlik",
    2: "değer/gelir",
    # 3.ev sadece “mesaj” değil: yakın çevre + öğrenme + iletişim tarzı + kısa yol trafiği
    3: "iletişim tarzı/öğrenme ritmi/yakın çevre",
    4: "ev/kök",
    5: "yaratıcılık/ifade",
    6: "rutin/sağlık",
    7: "ilişki/ortaklık",
    8: "derin bağ/dönüşüm",
    9: "anlam/ufuk/genişleme",
    10: "kariyer/görünürlük",
    11: "topluluk/hedef",
    12: "bilinçaltı/çözülme",
}

HOUSE_MOTIFS_TR: Dict[int, str] = {
    1: "benlik/duruş/imaj; başlangıç enerjisi ve yön hissi",
    3: "iletişim tarzın; yakın çevre, kardeşler, kısa eğitimler ve günlük trafik",
    4: "ev/kök; iç düzen, güven duygusu ve temel ritim",
    7: "ilişki/ortaklık; sınır, anlaşma ve karşılıklılık",
    9: "ufuk/uzmanlaşma; eğitim, yayın, yabancılar, inançlar ve yol haritası",
    10: "iş/itibar; hedef, görünürlük ve sorumluluk",
    11: "topluluk/hedef; network, ekip, proje ekosistemi ve gelecek planı",
}

PLANET_ARCHETYPES_TR: Dict[str, Dict[str, Sequence[str]]] = {
    "uranus": {
        "verbs": ("sarsar", "uyandırır", "yeni yol açar"),
        "shadow": ("sabırsız kopuş", "ani karar", "kanal dağılması"),
        "gift": ("yaratıcı sıçrama", "elektrik netlik", "yenilik cesareti"),
    },
    "neptune": {
        "verbs": ("bulanıklaştırır", "yumuşatır", "sezdirir"),
        "shadow": ("sınır erimesi", "projeksiyon", "yanlış okuma"),
        "gift": ("sezgiyi ayıklama", "nazik sınır", "ilhamlı netlik"),
    },
    "mars": {
        "verbs": ("başlatır", "iter", "hamleyi açar"),
        "shadow": ("acele", "sertleşme", "tepkisellik"),
        "gift": ("doğru hamle", "cesur netlik", "odak"),
    },
    "saturn": {
        "verbs": ("test eder", "sıkılaştırır", "olgunlaştırır"),
        "shadow": ("katılık", "aşırı yük", "yavaş kilitlenme"),
        "gift": ("ustalık", "kalıcı sistem", "iç otorite"),
    },
}

ASPECT_VOICES_TR: Dict[str, Dict[str, Sequence[str]]] = {
    "trine": {
        "conflict": (
            "Akış açık; doğal ilerleyen bir hat var.",
            "Yetenek devrede; kapı açılıyor ve sen girersen büyür.",
        ),
        "shadow": (
            "Fazla kanal açmak hızı dağıtır.",
            "Konfor alanı ölçümü gevşetebilir.",
        ),
        "upper": (
            "Ritim kurarsan bu açı kalıcı ivme üretir.",
            "Doğal akışı plana bağlamak hızlı sıçrama getirir.",
        ),
    },
    "sextile": {
        "conflict": (
            "Fırsat var; küçük hamleyle açılır.",
            "Mikro adım atarsan destek büyür.",
        ),
        "shadow": (
            "Pasif kalmak bu açının hızını söndürür.",
            "Erteleme küçük fırsatları kaçırabilir.",
        ),
        "upper": (
            "Küçük adım + düzenli tekrar büyük kazanca döner.",
            "Mikro hamleleri zincirlediğinde sonuç büyür.",
        ),
    },
    "square": {
        "conflict": (
            "Sürtünme davranışı test eder; tonu yanlış ayarlama riski artar.",
            "Baskı anında hızlanmak yerine çerçeve kurmak gerekir.",
        ),
        "shadow": (
            "Savunma refleksi veriyi kişisel saldırı gibi okutabilir.",
            "Acele yanıt kısa rahatlık verir, uzun maliyet çıkarır.",
        ),
        "upper": (
            "Gerilimi metoda çevirdiğinde net güç açılır.",
            "Sınır netliği bu açıda oyunu lehine çevirir.",
        ),
    },
    "opposition": {
        "conflict": (
            "Ayna etkisi kutupları büyütür; denge hızla bozulabilir.",
            "Karşı taraf ritmi değiştirirken iç merkez test edilir.",
        ),
        "shadow": (
            "Projeksiyon arttığında ihtiyaç görünmez kalır.",
            "Onay arayışı yön kaymasına yol açabilir.",
        ),
        "upper": (
            "Net soru ve net sınır kutupları ortak dile taşır.",
            "Karşıtlık doğru yönetilirse ilişki zekâsı büyür.",
        ),
    },
    "conjunction": {
        "conflict": (
            "Enerji tek hatta toplanınca yük hissi artar.",
            "Aynı anda çok hedef açmak odağı kırar.",
        ),
        "shadow": (
            "Yoğunlaşma kontrol takıntısına kayabilir.",
            "Hızlı sonuç isteği yöntemi daraltabilir.",
        ),
        "upper": (
            "Tek hedefte kalırsan bu açı ustalık üretir.",
            "Baskıyı sıraya koyduğunda netlik hızdan öne geçer.",
        ),
    },
}

ASPECT_SECTION_TR: Dict[str, Dict[str, str]] = {
    "square": {"label": "Sürtünme", "tone": "pressure"},
    "opposition": {"label": "Ayna", "tone": "mirror"},
    "trine": {"label": "Akış", "tone": "flow"},
    "sextile": {"label": "Fırsat", "tone": "opportunity"},
    "conjunction": {"label": "Yoğunlaşma", "tone": "focus"},
}

ASPECT_TONE_TR: Dict[str, str] = {
    "trine": "flow",
    "sextile": "chance",
    "square": "friction",
    "opposition": "mirror",
    "conjunction": "focus",
}

SECTION_LABELS_BY_TONE_TR: Dict[str, Dict[str, str]] = {
    "flow": {"conflict": "Akış", "shadow": "Abartırsan", "upper": "Potansiyel"},
    "chance": {"conflict": "Fırsat", "shadow": "Kaçırma riski", "upper": "Kazanca çevir"},
    "friction": {"conflict": "Sürtünme", "shadow": "Refleks", "upper": "Ustalık"},
    "mirror": {"conflict": "Ayna", "shadow": "Projeksiyon", "upper": "Denge"},
    "focus": {"conflict": "Yoğunluk", "shadow": "Taşma", "upper": "Tek hedef"},
}

HOUSE_SCENES_TR: Dict[int, Dict[str, Sequence[str]]] = {
    3: {
        "scene": ("mesaj", "konuşma", "yazı-not", "yakın çevre", "kanal yönetimi"),
        "examples": ("yanlış anlaşılma", "kısa metin", "toplantı notu"),
    },
    5: {
        "scene": ("üretim", "yaratıcılık", "sahne", "oyun", "prototip"),
        "examples": ("taslak", "mini demo", "üretim ritmi"),
    },
    7: {
        "scene": ("anlaşma dili", "ilişki ritmi", "ayna", "pazarlık", "sınır"),
        "examples": ("beklenti netliği", "karşılıklı söz"),
    },
    9: {
        "scene": ("eğitim", "sertifika", "yayın", "yabancı dil", "uzak temas"),
        "examples": ("öğrenme sprinti", "mentorluk", "uzmanlaşma"),
    },
    11: {
        "scene": ("topluluk", "network", "ortak hedef", "yayılım", "ürün ağı"),
        "examples": ("paylaşım planı", "takım koordinasyonu"),
    },
}

SIGN_STYLES_TR: Dict[str, Dict[str, str]] = {
    "virgo": {"style": "metod ve iyileştirme", "pitfall": "mükemmellik ertelemesi", "superpower": "ölçülü ustalık"},
    "capricorn": {"style": "yapı ve sorumluluk", "pitfall": "aşırı kontrol", "superpower": "sürdürülebilir sonuç"},
    "aries": {"style": "ilk hamle", "pitfall": "acele patlama", "superpower": "cesur başlatma"},
    "aquarius": {"style": "yenilik", "pitfall": "ani kopuş", "superpower": "yaratıcı sıçrama"},
    "pisces": {"style": "sezgi", "pitfall": "sınır erimesi", "superpower": "ince duyarlık"},
}

DISPOSITOR_HINTS_TR: Dict[str, Dict[str, Sequence[str]]] = {
    "Mercury": {
        "mechanism": ("mekanizma Merkür: not al, sırala, gönder", "Merkür hattı: kısa yaz, net sor"),
    },
    "Saturn": {
        "mechanism": ("mekanizma Satürn: sınır koy, takvimle", "Satürn hattı: yavaşla, sabitle, tamamla"),
    },
    "Mars": {
        "mechanism": ("mekanizma Mars: tek hamle, tek hedef", "Mars hattı: başlat, ölç, düzelt"),
    },
}

ROLE_VOICES_TR: Dict[str, Dict[str, str]] = {
    "north_node": {
        "conflict": "Yön hattı açılırken eski ivmeyle yeni rota arasında sürtünme olabilir.",
        "upper": "Büyüme rotası küçük ama sürekli ileri adımla netleşir.",
    },
    "south_node": {
        "conflict": "Otomatik pilot ve eski kalıp tekrar devreye girebilir.",
        "upper": "Alışkanlığı fark edip güncel seçim yaptığında enerji serbest kalır.",
    },
    "lilith": {
        "conflict": "Ham sınır ve dürtü dili sertleşirse temas kopabilir.",
        "upper": "Bastırılmış isteği net bir sınır cümlesiyle ifade etmek güç kazandırır.",
    },
}


_ALLOWED_PUBLIC_POINTS = {
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
}


def _safe_text(s: Any) -> str:
    return str(s or "").strip()


def strip_tech_tokens(text: str) -> str:
    out = _safe_text(text)
    out = _TECH_TOKENS_RE.sub("", out)
    out = re.sub(r"\s{2,}", " ", out).strip()
    out = re.sub(r"\s+([.,;:!?])", r"\1", out)
    return out


def house_motif_line(house: int | None) -> str:
    if not house:
        return ""
    return HOUSE_MOTIFS_TR.get(int(house), "")


def compose_phrase_pack(
    *,
    transit_body: str,
    aspect: str,
    natal_point: str,
    context_pack: Mapping[str, Any],
    event: Mapping[str, Any],
    max_len: Mapping[str, int],
) -> Dict[str, Any]:
    transit_l = str(transit_body or "").strip().lower()
    aspect_l = str(aspect or "").strip().lower()
    natal_point_safe = _safe_point(natal_point)
    pack = context_pack if isinstance(context_pack, Mapping) else {}
    target = pack.get("target") if isinstance(pack.get("target"), Mapping) else {}
    target_planet = _safe_point(target.get("planet") or natal_point_safe)
    target_house = _safe_int(target.get("house"))
    target_sign = str(target.get("sign") or "").strip().lower()
    target_sign_tr = str(target.get("sign_tr") or target.get("sign") or "").strip()
    dispositor = pack.get("dispositor") if isinstance(pack.get("dispositor"), Mapping) else {}
    rulership = pack.get("rulership_houses") if isinstance(pack.get("rulership_houses"), list) else []

    transit_house = _safe_int((event.get("houses") or {}).get("transit_in_natal_house"))
    seed = _seed(event, "phrase_pack")

    base = ASPECT_VOICES_TR.get(aspect_l, ASPECT_VOICES_TR["square"])
    style = SIGN_STYLES_TR.get(target_sign, {})

    scene_line = _build_scene_line(transit_house, target_house)
    title = _build_title(transit_l, aspect_l, target_planet, target_house, transit_house, seed)

    conflict_add = " ".join(base["conflict"][:2])
    shadow_add = " ".join(base["shadow"][:2])
    upper_add = " ".join(base["upper"][:2])

    guidance_add: List[str] = []
    watch_add: List[str] = []

    is_uranus_mars = transit_l == "uranus" and aspect_l in {"trine", "sextile"} and str(target_planet).lower() == "mars"
    if is_uranus_mars:
        conflict_add = (
            "Bir anda yöntem değiştirip hız kazanırsın; yaratıcı sıçrama burada kolay. "
            "Başak tarafında metod kurdukça akış büyür."
        )
        shadow_add = "Aşırı overclock odak kaydırır; aynı anda üç plan açmak kısa devre yaratır."
        upper_add = (
            "Yeni yöntem + yapılandırılmış sprint sıçraması burada çalışır; öğrenme ve yayın hattı hızlanır. "
            "Ölç, not al, sprint ritmi kur; sonra yayına al."
        )
        guidance_add = [
            "Seç tek bir hedef; 14 gün sprint aç.",
            "Yayınla mini bir prototip ve sonucu test et.",
        ]
        watch_add = ["Durdur aşırı optimizasyonu; başlamayı geciktirme."]

    if transit_l == "neptune" and aspect_l == "square" and natal_point_safe == "ASC":
        conflict_add = (
            "Neptün, ASC ile kare açı kuruyor; kimlik hattında sis artar. "
            "Dış imaj ile iç niyet kolay ayrışır, sınırı baştan yazmak gerekir."
        )
        shadow_add = "Belirsiz sözler yanlış anlaşılmayı büyütebilir."
        upper_add = "Nazik ama net sınır koyduğunda sezgi netliğe döner."
        guidance_add = ["Sözünü kısa tut; niyeti bir cümlede sabitle."]
        watch_add = ["Belirsiz vaat verme."]

    if transit_l == "neptune" and aspect_l == "square" and natal_point_safe == "DSC":
        conflict_add = (
            "Neptün, DSC ile kare açı kuruyor; ilişki aynasında projeksiyon artar. "
            "Karşı tarafı idealize etme riski bu hatta yükselir."
        )
        shadow_add = "Sınır erimesi beklenti karmaşası yaratabilir."
        upper_add = "İlişki dilini netleştirince sis yerine temas kalır."
        guidance_add = ["Beklentiyi iki maddede yaz ve karşılıklı teyit al."]
        watch_add = ["İma ile anlaşılmayı bekleme."]

    if transit_l == "neptune" and aspect_l == "conjunction" and natal_point_safe == "Saturn":
        conflict_add = "Eski yapı çözülürken kontrol refleksi sertleşebilir."
        shadow_add = "Katı planı bırakmadan yeni akış kurulmaz."
        upper_add = "Çerçeveyi sadeleştirip sınırı güncellediğinde sağlam bir yeniden kurulum gelir."
        guidance_add = ["Tek kural seç ve bu hafta onu uygula."]
        watch_add = ["Hepsini aynı anda düzeltmeye çalışma."]

    if style:
        conflict_add = f"{conflict_add} {target_sign_tr} stilinde tema: {style['style']}; risk: {style['pitfall']}."
        upper_add = f"{upper_add} Güç tarafı: {style['superpower']}."

    role_key = normalize_point_token(target_planet or natal_point_safe)
    role_voice = ROLE_VOICES_TR.get(role_key) or ROLE_VOICES_TR.get(normalize_point_token(natal_point_safe))
    if role_voice:
        conflict_add = _append_unique_sentence(conflict_add, role_voice.get("conflict") or "")
        upper_add = _append_unique_sentence(upper_add, role_voice.get("upper") or "")

    disp_planet = _safe_point(dispositor.get("planet") or "")
    if disp_planet and disp_planet in DISPOSITOR_HINTS_TR:
        mech = _pick(DISPOSITOR_HINTS_TR[disp_planet]["mechanism"], seed)
        upper_add = f"{upper_add} {mech}."

    rulership_line = _rulership_line(rulership)
    if rulership_line:
        upper_add = f"{rulership_line} {upper_add}"

    if transit_house == 5 and is_uranus_mars:
        conflict_add = f"{conflict_add} 5. Evde üretim ve sahne tarafında elektrikli bir itki var."
    if target_house == 9 and is_uranus_mars:
        upper_add = f"{upper_add} 9. Evde öğrenme, yayın ve uzmanlaşma burada sonuç verir."

    if not guidance_add:
        guidance_add = [
            "Tek bir hamle seç ve gün içinde tamamla.",
            "Kısa not al; akşam tek ölçümle sonucu kontrol et.",
        ]
    if not watch_add:
        watch_add = ["Aynı anda iki odak açıp ritmi dağıtma."]

    section = ASPECT_SECTION_TR.get(aspect_l, {"label": "Dinamik", "tone": "calibration"})

    out = {
        "title": _limit_sentences(_sanitize(title), 1),
        "conflict_label": section["label"],
        "conflict_tone": section["tone"],
        "tone": ASPECT_TONE_TR.get(aspect_l, "focus"),
        "section_labels": SECTION_LABELS_BY_TONE_TR.get(
            ASPECT_TONE_TR.get(aspect_l, "focus"),
            SECTION_LABELS_BY_TONE_TR["focus"],
        ),
        "why_now": _build_why_now(event),
        "conflict_add": _limit_sentences(_sanitize(conflict_add), int(max_len.get("conflict", 2))),
        "shadow_add": _limit_sentences(_sanitize(shadow_add), int(max_len.get("shadow", 2))),
        "upper_add": _limit_sentences(_sanitize(upper_add), int(max_len.get("upper", 2))),
        "guidance_add": _sanitize_bullets(guidance_add, exact_max=2),
        "watch_out_add": _sanitize_bullets(watch_add, exact_max=1),
        "scene_line": _limit_sentences(_sanitize(scene_line), 1),
    }
    return out


def _build_scene_line(transit_house: int | None, target_house: int | None) -> str:
    if transit_house and target_house and transit_house != target_house:
        return (
            f"Sahne {transit_house}. Ev ({HOUSE_LABEL_TR.get(transit_house, 'genel')}); "
            f"vurduğu yer {target_house}. Ev ({HOUSE_LABEL_TR.get(target_house, 'genel')})."
        )
    if target_house:
        return f"Sahne {target_house}. Ev ({HOUSE_LABEL_TR.get(target_house, 'genel')}); vurduğu yer aynı ev hattı."
    if transit_house:
        return f"Sahne {transit_house}. Ev ({HOUSE_LABEL_TR.get(transit_house, 'genel')}); vurduğu yer henüz dağınık."
    return ""


def _build_title(
    transit_body: str,
    aspect: str,
    target_planet: str,
    target_house: int | None,
    transit_house: int | None,
    seed: int,
) -> str:
    if transit_body == "uranus" and aspect in {"trine", "sextile"} and str(target_planet).lower() == "mars":
        pool = ["Kıvılcım Planı", "Yöntem Sıçraması", "Elektrik Prototip"]
        return pool[(seed + (target_house or 0) + (transit_house or 0)) % len(pool)]
    if transit_body == "neptune" and aspect == "square" and target_planet in {"ASC", "DSC"}:
        return "Sınır Kalibrasyonu" if target_planet == "ASC" else "Ayna Sisi"
    pool = {
        "square": ["Netlik Pazarlığı", "Sınır Testi"],
        "trine": ["Akış Hattı", "Hızlı İvme"],
        "sextile": ["Fırsat Penceresi", "Küçük Hamle"],
        "opposition": ["Ayna Dengesi", "Kutupları Birleştir"],
        "conjunction": ["Tek Kanal", "Yoğun Odak"],
    }.get(aspect, ["Tema Güncellemesi"])
    return pool[seed % len(pool)]


def _rulership_line(rulership_houses: Sequence[Mapping[str, Any]]) -> str:
    houses: List[int] = []
    for entry in rulership_houses:
        house = _safe_int(entry.get("house")) if isinstance(entry, Mapping) else None
        if house and house not in houses:
            houses.append(house)
    if not houses:
        return ""
    if len(houses) == 1:
        h = houses[0]
        return f"Arka bağlantı: {h}. Ev ({HOUSE_LABEL_TR.get(h, 'genel')}) hattına düşer."
    a, b = houses[0], houses[1]
    return (
        f"Arka bağlantı: {a}. Ev ({HOUSE_LABEL_TR.get(a, 'genel')}) ve "
        f"{b}. Ev ({HOUSE_LABEL_TR.get(b, 'genel')}) arasında çalışır."
    )


def _safe_point(value: Any) -> str:
    token = str(value or "").strip()
    if not token:
        return ""
    low = normalize_point_token(token)
    if is_public_point(low):
        if low in {"asc", "dsc", "mc", "ic"}:
            return low.upper()
        label_map = {
            "north_node": "North Node",
            "south_node": "South Node",
            "lilith": "Lilith",
            "chiron": "Chiron",
            "vertex": "Vertex",
            "fortune": "Fortune",
        }
        if low in label_map:
            return label_map[low]
        return low.replace("_", " ").title()
    return token


def _sanitize(text: str) -> str:
    out = strip_tech_tokens(str(text or ""))
    out = re.sub(r"\s+", " ", out).strip()
    out = re.sub(r"\s+([,.;:!?])", r"\1", out)
    return out


def _sanitize_bullets(values: Sequence[str], *, exact_max: int) -> List[str]:
    out: List[str] = []
    for value in values:
        text = _sanitize(value)
        if not text:
            continue
        words = text.split()
        if len(words) > 14:
            text = " ".join(words[:14])
        if text[-1] not in ".!?":
            text += "."
        out.append(text)
        if len(out) >= exact_max:
            break
    return out


def _build_why_now(event: Mapping[str, Any]) -> str:
    orb = _safe_float(event.get("orb_deg"), default=9.9)
    if orb <= 0.6:
        orb_phrase = "Orb çok yakın"
    elif orb <= 1.6:
        orb_phrase = "Orb yakın"
    else:
        orb_phrase = "Orb geniş"

    bucket = str(event.get("bucket") or "").strip().lower()
    duration_phrase = {
        "long": "aylar süren etki",
        "medium": "haftalar süren etki",
        "short": "günlük kısa etki",
    }.get(bucket, "orta süreli etki")

    natal_point = str(event.get("natal_point") or "").strip().upper()
    angle_phrase = "angle tetikleniyor" if natal_point in {"ASC", "DSC", "MC", "IC"} else "açı hattı aktif"

    phase = str(event.get("phase") or "").strip().lower()
    phase_phrase = {
        "exact": "exact",
        "exactish": "exact",
        "applying": "yaklaşıyor",
        "separating": "çözülüyor",
    }.get(phase, "")
    parts = [orb_phrase, duration_phrase, angle_phrase]
    if phase_phrase:
        parts.append(phase_phrase)
    text = " + ".join(parts) + "."
    text = _sanitize(text)
    words = text.split()
    if len(words) > 14:
        text = " ".join(words[:14]).rstrip(".,;:!?") + "."
    return text


def _limit_sentences(text: str, max_sentences: int) -> str:
    raw = str(text or "").strip()
    if not raw:
        return ""
    parts = [p.strip() for p in re.split(r"(?<!\d[.!?])(?<=[.!?])\s+", raw) if p.strip()]
    if not parts:
        return raw
    limited = " ".join(parts[: max(1, max_sentences)]).strip()
    if limited and limited[-1] not in ".!?":
        limited += "."
    return limited


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


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


def _pick(values: Sequence[str], seed: int) -> str:
    if not values:
        return ""
    return str(values[seed % len(values)])


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


def period_big_picture(domain: str, seed: int, enable_fun: bool = True) -> str:
    pool = [
        f"Bu dönem gökyüzü {domain} alanında ince bir ayar açıyor. Bazen aynı cümleyi kurup bambaşka duyulduğunu fark edebilirsin. Ama süreç seni daha gerçek ve daha güvenilir bir ifadeye taşıyor.",
        f"Bu dönem {domain} tarafında bir güncelleme var. Önce sistem ağırlaşıyor gibi görünür, sonra yeni ritim yerine oturur. Kafa karışıklığı gibi görünen şey aslında yeniden yön bulma süreci.",
        f"Bu dönem {domain} tarafında az ama net çizgisi büyüyor. His var, sezgi var. Asıl kazanım ise çerçeve kurabilmek.",
    ]
    return _pick(pool, seed)


def period_mechanism_chain(
    *,
    transit_body: str,
    aspect: str,
    natal_point: str,
    angle_chain: Mapping[str, Any] | None,
    target_chain: Mapping[str, Any] | None,
    start_theme: str,
    end_theme: str,
    seed: int,
    enable_fun: bool = True,
) -> str:
    if isinstance(angle_chain, Mapping):
        angle_name = str(angle_chain.get("angle") or natal_point or "").upper()
        angle_tr = {
            "ASC": "Yükselen",
            "DSC": "Alçalan",
            "MC": "Tepe Noktası",
            "IC": "Dip Noktası",
        }.get(angle_name, natal_point)
        sign = str(angle_chain.get("sign") or "").strip()
        ruler = str(angle_chain.get("ruler") or "").strip()
        ruler_house = _safe_int(angle_chain.get("ruler_house"))
        ruler_house_txt = f"{ruler_house}. evde" if ruler_house else "ilgili evde"

        pool = [
            f"{angle_tr} çizgin {sign} temasında çalıştığı için dış dünyaya net bir yerden yaklaşırsın. Bu çizginin yöneticisi {ruler} haritanda {ruler_house_txt} çalışır. Şimdi {transit_body} bu hatta {aspect} açıyla dokununca değişim önce {start_theme} tarafında hissedilir; sonuçta {end_theme} alanında görünür olur.",
            f"Bu dönem {angle_tr} hattı hassas. {sign} çizgisinin yöneticisi {ruler} {ruler_house_txt} olduğu için gökyüzündeki etki önce {start_theme} düzeninde başlar. {transit_body} etkisi sonunda {end_theme} tarafında kalıcı bir ayara dönüşür.",
        ]
        return _pick(pool, seed)

    if isinstance(target_chain, Mapping):
        planet = str(target_chain.get("planet") or natal_point or "").strip()
        sign = str(target_chain.get("sign") or "").strip()
        house = _safe_int(target_chain.get("house"))
        house_txt = f"{house}. evde" if house else "kendi alanında"
        dispositor = str(target_chain.get("dispositor") or "").strip()

        pool = [
            f"{planet} haritanda {house_txt} çalıştığı için bu dönem hikâye {end_theme} alanına bağlanıyor. {sign} vurgusu yöntemi ve detayları büyütür, {dispositor} tarafı bunu zihinsel bir çerçeveye oturtma ihtiyacını artırır. {transit_body} etkisi {start_theme} tarafında başlar ve {end_theme} tarafında kalıcı bir ayara döner.",
        ]
        return _pick(pool, seed)

    return _pick(
        [
            f"{transit_body} ile {aspect} teması bu dönem {start_theme} tarafında başlıyor ve zamanla {end_theme} alanına yayılıyor. Bu yüzden küçük görünen bir detay daha büyük bir yön değişimine bağlanabilir."
        ],
        seed,
    )


def period_upper_meaning(
    *,
    promise_theme: str,
    skill_gain: str,
    seed: int,
    enable_fun: bool = True,
) -> str:
    pool = [
        f"Bu transitin amacı bir şeyi bozmak değil, {skill_gain} kasını büyütmek. Sende bunun karşılığı {promise_theme} temasıyla birleşiyor. Netlik arttıkça hem kendini hem ilişkilerini daha az yorarak taşırsın. İyi kullanırsan bu dönem bittiğinde sende kalan şey daha az kelimeyle daha çok güven olur.",
        f"Bu dönem {promise_theme} tarafında olgunlaşma getiriyor. Zorlayan yer sisin içinden çerçeveyi bulmak, hediyesi ise {skill_gain}. Süreç tamamlandığında daha gerçek bir yön hissiyle ilerlersin.",
    ]
    return _pick(pool, seed)
