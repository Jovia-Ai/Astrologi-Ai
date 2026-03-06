from __future__ import annotations

import hashlib
from collections import Counter
from typing import Any, Dict, List, Mapping

from app.transit.narrative.archetype_engine import build_insight_pack
from app.transit.narrative.astrolog_narrative_engine import (
    PeriodStoryContext,
    build_story_track_copy,
    build_period_story,
    infer_story_track_id,
)
from app.transit.narrative.chain_explainer_tr import build_chain_explainer_tr
from app.transit.narrative.hybrid_context import build_hybrid_event_context
from app.transit.narrative.natal_promise import build_natal_promise, build_section_injections
from app.transit.narrative.point_policy import is_public_event
from app.transit.narrative.selection import select_event_ids
from app.transit.narrative.text_quality_tr import (
    apply_copy_quality_layer,
    build_period_copy,
    rewrite_period_card_tr,
)
from app.transit.narrative.voice_engine_tr import build_card_copy

OUTER_PLANETS = {"Pluto", "Neptune", "Uranus"}
ALWAYS_PLANETS = {"Saturn"} | OUTER_PLANETS
ANGLE_POINTS = {"ASC", "MC", "DSC", "IC"}

HOUSE_THEME = {
    3: "Zihinsel Otoriteni Insa Ediyorsun",
    7: "Iliski Dengesini Yeniden Kuruyorsun",
    10: "Yon ve Sorumluluk Cizgin Netlesiyor",
}

DOMAIN_TR = {
    "mind": "zihin",
    "relationships": "iliski",
    "career": "kariyer",
    "identity": "kimlik",
    "money": "maddi duzen",
    "home": "ev duzeni",
}

ASPECT_MOD = {
    "square": {
        "conflict": "Baski arttikca dil keskinlesebilir ve savunma hizlanabilir.",
        "shadow": "Savunma refleksi dusunce akisina gereksiz sertlik katabilir.",
        "upper": "Gerilimi yapisal netlige cevirmek daha olgun bir ifade getirir.",
    },
    "opposition": {
        "conflict": "Iki uc arasinda denge kurmak zorlayici olabilir.",
        "shadow": "Dis onayi beklemek kendi sesini bastirabilir.",
        "upper": "Karsi kutuplari uzlastirmak bakisini olgunlastirir.",
    },
    "trine": {
        "conflict": "Akis rahat gorunse de dagilmaya acik bir alan olabilir.",
        "shadow": "Rahatlik disiplini geciktirebilir.",
        "upper": "Dusunceyi yapilandirmak daha dogal bir ritim kazanabilir.",
    },
    "sextile": {
        "conflict": "Kucuk firsatlar gozden kacarsa momentum zayiflayabilir.",
        "shadow": "Erteleme hizli adim ihtiyacini perdeleyebilir.",
        "upper": "Kucuk ama duzenli adimlar net bir ustalik biriktirir.",
    },
}

PLANET_ARCHETYPE_TR = {
    "Saturn": {
        "conflict": "iç otoriteyi aşırı denetimle karıştırabilirsin",
        "shadow": "kendi sesine karşı sertleşme eğilimi oluşabilir",
        "upper": "disiplini netlik için kullanırsan kalıcı güç kurarsın",
    },
    "Pluto": {
        "conflict": "kontrol ihtiyaci guven temalarini zorlayabilir",
        "shadow": "guc cekismesi ya hep ya hic diline kayabilir",
        "upper": "derin donusumu bilincli yonettiginde dayanıklilik artar",
    },
    "Neptune": {
        "conflict": "belirsizlik sinirlari bulaniklastirabilir",
        "shadow": "kacinma refleksi net karari erteleyebilir",
        "upper": "sezgi ile net siniri dengelemek berraklik getirir",
    },
    "Uranus": {
        "conflict": "ani degisim ihtiyaci duzeni zorlayabilir",
        "shadow": "kopus refleksi istikrar ihtiyacini bastirabilir",
        "upper": "yeniligi ritimle birlestirdiginde ozgurluk kalici olur",
    },
    "Jupiter": {
        "conflict": "fazla buyutme onceligi dagitabilir",
        "shadow": "asiri guven detaylari atlamana yol acabilir",
        "upper": "genis bakisi odakla birlestirince firsat olgunlasir",
    },
    "Mars": {
        "conflict": "hizli tepki sabri zorlayabilir",
        "shadow": "rekabet refleksi iletisimi sertlestirebilir",
        "upper": "enerjiyi net hedefe koymak etkini guclendirir",
    },
    "Venus": {
        "conflict": "uyum arzusu net siniri erteleyebilir",
        "shadow": "onay arayisi kendi degerini disariya baglayabilir",
        "upper": "nazik ama acik durus iliski kalitesini yukseltir",
    },
}

HOUSE_ARCHETYPE_TR = {
    1: "benlik ve duruş",
    2: "özdeğer ve maddi düzen",
    3: "zihin ve iletişim",
    4: "ev ve iç güven",
    5: "yaratıcılık ve keyif",
    6: "rutin ve sağlık",
    7: "ilişki ve ortaklık",
    8: "paylaşım ve dönüşüm",
    9: "inanç ve ufuk",
    10: "kariyer ve görünürlük",
    11: "topluluk ve hedefler",
    12: "bilinçaltı ve çözülme",
}

SIGN_STYLE_TR = {
    "Aries": "hizli ve dogrudan",
    "Taurus": "sabit ve guvence odakli",
    "Gemini": "merakli ve degisken",
    "Cancer": "duygusal ve koruyucu",
    "Leo": "gorunur ve iddiali",
    "Virgo": "detayci ve duzenleyici",
    "Libra": "denge ve iliski odakli",
    "Scorpio": "derin ve yogun",
    "Sagittarius": "genis ve anlam arayan",
    "Capricorn": "yapi ve sonuc odakli",
    "Aquarius": "yenilikci ve farkli",
    "Pisces": "sezgisel ve akin",
}

ASPECT_DYNAMICS_TR = {
    "conjunction": "yoğunlaşma",
    "square": "sürtünme ve ayar",
    "opposition": "denge ve karşılaşma",
    "trine": "akış ve destek",
    "sextile": "fırsat ve açılan kapı",
    "quincunx": "uyum arayışı",
}

PLANET_TR = {
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

ANGLE_TR = {
    "ASC": "Yükselen",
    "DSC": "Alçalan",
    "MC": "Tepe Noktası",
    "IC": "Dip Noktası",
}

HOUSE_SCENE_TR = {
    1: "kimlik ve duruş; imaj, beden, başlangıç enerjisi",
    3: "zihin ve iletişim tarzı; yakın çevre, kardeşler, kısa eğitimler, günlük trafik",
    7: "ilişki aynası; anlaşmalar, partnerlik, açık çatışma/uyum",
    9: "ufuk ve uzmanlaşma; eğitim, yayın, yabancılar, inançlar, yol haritası",
    10: "kariyer ve görünürlük; itibar, hedefler",
}

PLANET_EFFECT_TR = {
    "neptune": "bulanıklık artabilir; sezgi yükselirken sınırları yeniden netlemek gerekebilir",
    "saturn": "disiplin ve yapı kurma ihtiyacı öne çıkar",
    "uranus": "yenilik ve beklenmedik açılımlar hız kazanır",
    "mars": "hamle isteği artar; işi başlatmak kolaylaşır",
    "chiron": "hassas nokta görünür olur; iyileştirme ihtiyacı belirginleşir",
    "jupiter": "ufuk genişler; abartı riskine karşı ölçü önemli olur",
    "venus": "ilişki ve değerler alanında denge arayışı belirginleşir",
}

PLANET_ASPECT_TARGET_TEASER_TR = {
    ("uranus", "trine", "mars"): "cesaret ve yeni yöntemle hamle yapmak kolaylaşıyor",
    ("neptune", "square", "asc"): "kimlik ve duruş tarafı bulanıklaşabilir; netlik ihtiyacı artıyor",
    ("neptune", "conjunction", "saturn"): "zihinsel kontrol gevşerken sezgi artıyor; yapı yeniden kurulmak istiyor",
    ("chiron", "square", "jupiter"): "inanç ve büyüme tarafında hassasiyet artıyor; ölçü korumak iyi geliyor",
}

TITLE_POOL_TR = [
    "Sis Dağılırken",
    "Netliğin Yeni Tanımı",
    "Sözün Altındaki Niyet",
    "Çerçeve Yenileniyor",
    "Yöntem Sıçraması",
    "Gerçeklik Testi: Dil",
    "İmajın Buharı",
    "Aynada Bulanıklık",
    "Yapı Kur, Hafifle",
    "Sınır Çizgisi",
    "Sözün Bedeli",
    "Karar Kasını Güçlendir",
    "Dayanıklılık Provası",
    "Düzenin Yeni Versiyonu",
    "Ciddiyetin Hediyesi",
    "Basınç Altında Netlik",
    "Kıvılcım Planı",
    "Yeni Yöntem Kapısı",
    "Ani Cesaret",
    "Rotayı Değiştiren Fikir",
    "Elektrik: Hamle",
    "Hızlı Pivot",
    "Kilidi Açan Detay",
    "Özgürleşme Hamlesi",
    "Tek Hedef Modu",
    "Başlat ve Bitir",
    "Keskin Netlik",
    "İnisiyatif Zamanı",
    "Eforun Yönü",
    "Hamleye Dönüş",
    "Ufuk Genişliyor",
    "Yol Haritası Yazılıyor",
    "Uzmanlaşma Dönemeci",
    "Yayın ve Öğrenme",
    "Büyük Resim Çağrısı",
    "Topluluk Sahnesi",
    "Gelecek Ağı",
    "Ekip ve Vizyon",
    "Sahne Arkası Güç",
    "Network'te Dönüşüm",
]

TITLE_POOL_AXIS_TR = ["Sözün Sınırı", "Aynada Bulanıklık", "Yön Hattı", "Duruş Ayarı"]
TITLE_POOL_9_URANUS_MARS_TR = ["Kıvılcım Planı", "Yeni Yöntem Kapısı", "Rotayı Değiştiren Fikir"]
TITLE_POOL_3_NEPTUNE_SATURN_TR = ["Zihin Sisinin İçinden", "Netliğin Yeni Tanımı", "Dil ve Çerçeve"]

BEHAVIORAL_CUES = [
    "mesaji hemen atma, bir nefeslik ara ver",
    "cumleyi yarida kesmeden once niyetini netle",
    "yanit vermeden once uc kelimelik bir odak notu al",
    "ilk tepkiyi degil en net cumleyi sec",
]

HOUSE_GUIDANCE_POOL_TR: Dict[int, List[str]] = {
    3: [
        "Kısa yazılı özet çıkar.",
        "Soruyu tek cümlede netleştir.",
        "Tonu test et: gönderme, taslağa al.",
    ],
    5: [
        "Mini prototip çıkar.",
        "Paylaş ve geri bildirim topla.",
        "Oyuna çevir: 30 dk üret.",
    ],
    7: [
        "Beklentiyi iki maddeye indir, teyit al.",
        "Sınır cümlesini seç: Şu an buna girmiyorum.",
        "Kontrat dili: tarih ve çerçeve netleştir.",
    ],
    9: [
        "14 gün sprint seç; bir çıktı tanımla.",
        "Öğrenmeyi yayına bağla: kısa paylaşım.",
        "Roadmapi üç adıma indir.",
    ],
    11: [
        "Paylaşım planı çıkar.",
        "Tek kişiye ulaş: network hamlesi.",
        "Hedefi toplulukla test et.",
    ],
}

TONE_WATCH_POOL_TR: Dict[str, List[str]] = {
    "flow": ["Aşırı rahatlama.", "Dağılma."],
    "chance": ["Erteleme.", "Pasif kalma."],
    "friction": ["Tepkisellik.", "Acele karar."],
    "mirror": ["Projeksiyon.", "Yanlış okuma."],
    "focus": ["Kontrol takıntısı.", "Taşma."],
}

TONE_GUIDANCE_POOL_TR: Dict[str, List[str]] = {
    "flow": ["Tek hedefte kal, ritmi koru."],
    "chance": ["Küçük hamleyi bugün başlat."],
    "friction": ["Tepki yerine kısa yazılı netlik seç."],
    "mirror": ["Önce beklentini açık yaz, sonra konuş."],
    "focus": ["Tek kanal seç ve tamamlamaya odaklan."],
}

MECHANISM_GUIDANCE_TR: Dict[str, List[str]] = {
    "mercury": ["Yazılı netlik kur: soru, bağlam, karar."],
    "saturn": ["Takvimi kilitle: tek görev, sabit saat."],
    "mars": ["Tek hamle seç ve bitir."],
}

FALLBACK_GUIDANCE_TR: List[str] = [
    "Yaz tek cümle niyet.",
    "Çıkar taslak, sonra gönder.",
    "Açma aynı anda iki kanal.",
]


def _seed(event: Mapping[str, Any], key: str) -> int:
    raw = "|".join(
        [
            str(event.get("event_id") or ""),
            str(event.get("transit_body") or ""),
            str(event.get("aspect") or ""),
            str(event.get("natal_point") or ""),
            str(event.get("phase") or ""),
            str(event.get("bucket") or ""),
            key,
        ]
    )
    return int(hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8], 16)


def _pick_variant(options: List[str], *, seed: int, key: str) -> str:
    if not options:
        return ""
    idx_seed = int(hashlib.sha1(f"{seed}|{key}".encode("utf-8")).hexdigest()[:8], 16)
    return options[idx_seed % len(options)]


def _house_num(event: Mapping[str, Any]) -> int | None:
    houses = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}
    raw = houses.get("transit_in_natal_house")
    try:
        return int(raw) if raw is not None else None
    except (TypeError, ValueError):
        return None


def _sign_name(event: Mapping[str, Any]) -> str:
    signs = event.get("signs") if isinstance(event.get("signs"), Mapping) else {}
    sign = str(signs.get("transit_body_sign") or "").strip()
    return sign or "Aries"


def _is_angular(event: Mapping[str, Any]) -> bool:
    natal = str(event.get("natal_point") or "").upper()
    if natal in ANGLE_POINTS:
        return True
    house = _house_num(event)
    return house in {1, 4, 7, 10}


def _is_peak(event: Mapping[str, Any]) -> bool:
    phase = str(event.get("phase") or "").lower()
    return phase in {"exact", "exactish", "applying"}


def _tier(event: Mapping[str, Any]) -> str:
    ranking = event.get("ranking") if isinstance(event.get("ranking"), Mapping) else {}
    return str(ranking.get("tier") or "support")


def _weight(event: Mapping[str, Any]) -> float:
    ranking = event.get("ranking") if isinstance(event.get("ranking"), Mapping) else {}
    for key in ("weight", "strength"):
        try:
            value = float(ranking.get(key))
            return value
        except (TypeError, ValueError):
            continue
    return 0.0


def _event_selected(event: Mapping[str, Any]) -> bool:
    body = str(event.get("transit_body") or "")
    if body == "Moon":
        return False
    if body in ALWAYS_PLANETS:
        return True
    if body == "Jupiter":
        return _tier(event) in {"main", "support"} or _weight(event) >= 1.0
    if body in {"Mars", "Venus"}:
        return _is_angular(event) and _is_peak(event)
    return _tier(event) == "main"


def _phase_label(raw: str) -> str:
    value = raw.lower().strip()
    if value == "exactish":
        return "exact"
    return value or "applying"


def _duration_label(raw: str) -> str:
    mapping = {"short": "days", "medium": "weeks", "long": "months"}
    key = raw.lower().strip()
    return mapping.get(key, key or "weeks")


def _house_semantic_tags(house: int | None) -> List[str]:
    if house == 9:
        return ["mind", "meaning", "learning", "roadmap"]
    if house == 3:
        return ["mind", "communication"]
    if house == 7:
        return ["relationships"]
    if house == 10:
        return ["career"]
    if house == 4:
        return ["home"]
    return []


def _horizon_from_event(event: Mapping[str, Any]) -> str:
    bucket = str(event.get("bucket") or "").strip().lower()
    if bucket in {"long", "medium"}:
        return "period"
    if bucket == "short":
        return "daily"
    timing = event.get("timing") if isinstance(event.get("timing"), Mapping) else {}
    try:
        window_days = int(timing.get("window_days"))
    except (TypeError, ValueError):
        window_days = 0
    return "period" if window_days >= 60 else "daily"


def _aspect_symbol(aspect: str) -> str:
    return {
        "conjunction": "☌",
        "square": "□",
        "trine": "△",
        "sextile": "✶",
        "opposition": "☍",
        "quincunx": "⚻",
    }.get(aspect.strip().lower(), "•")


def _target_house_num(event: Mapping[str, Any]) -> int | None:
    houses = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}
    raw = houses.get("natal_point_house")
    try:
        return int(raw) if raw is not None else None
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _time_hint_for_signature(event: Mapping[str, Any], existing: str | None = None) -> str:
    return _time_hint_from_orb_phase(event)


def _point_label_tr(raw: str) -> str:
    value = str(raw or "").strip()
    if not value:
        return "Nokta"
    up = value.upper()
    if up in ANGLE_TR:
        return ANGLE_TR[up]
    return PLANET_TR.get(value.lower(), value.title())


def _signature(event: Mapping[str, Any], *, time_hint: str | None = None) -> str:
    body = str(event.get("transit_body") or "Transit").strip().title()
    natal = str(event.get("natal_point") or "Nokta").strip().upper()
    aspect = str(event.get("aspect") or "").lower()
    symbol = _aspect_symbol(aspect)
    resolved_time = _time_hint_for_signature(event, existing=time_hint)
    return f"{body} {symbol} {natal} • {resolved_time}"


def _signature_tr(event: Mapping[str, Any], *, time_hint: str | None = None) -> str:
    body = _point_label_tr(str(event.get("transit_body") or "Transit"))
    natal = _point_label_tr(str(event.get("natal_point") or "Nokta"))
    aspect = str(event.get("aspect") or "").lower()
    symbol = _aspect_symbol(aspect)
    resolved_time = _time_hint_for_signature(event, existing=time_hint)
    return f"{body} {symbol} {natal} • {resolved_time}"


def _title_pool_for_event(event: Mapping[str, Any]) -> List[str]:
    natal_point = str(event.get("natal_point") or "").strip().upper()
    transit = str(event.get("transit_body") or "").strip().lower()
    aspect = str(event.get("aspect") or "").strip().lower()
    house = _house_num(event)
    if transit == "neptune" and aspect == "square" and natal_point == "ASC" and house == 3:
        return ["Sözün Sınırı"]
    if natal_point in ANGLE_POINTS:
        return TITLE_POOL_AXIS_TR
    target = str(event.get("natal_point") or "").strip().lower()
    if house == 9 and transit in {"uranus", "mars"}:
        return TITLE_POOL_9_URANUS_MARS_TR
    if house == 3 and transit in {"neptune", "saturn"}:
        return TITLE_POOL_3_NEPTUNE_SATURN_TR
    if aspect in {"square", "opposition"} and target in {"asc", "dsc", "mc", "ic"}:
        return TITLE_POOL_AXIS_TR
    return TITLE_POOL_TR


def _deterministic_title(event: Mapping[str, Any], fallback: str = "Aktif Transit") -> str:
    pool = _title_pool_for_event(event)
    if not pool:
        return fallback
    event_id = str(event.get("event_id") or "").strip()
    seed_key = event_id or "|".join(
        [
            str(event.get("transit_body") or ""),
            str(event.get("aspect") or ""),
            str(event.get("natal_point") or ""),
            str(_house_num(event) or ""),
        ]
    )
    idx = int(hashlib.sha1(seed_key.encode("utf-8")).hexdigest(), 16) % len(pool)
    return pool[idx]


def _aspect_dynamic_tr(aspect: str) -> str:
    return ASPECT_DYNAMICS_TR.get(aspect.strip().lower(), "denge ayarı")


def _house_scene_text(house_num: int | None) -> str:
    if house_num is None:
        return "günlük sahnede"
    return HOUSE_SCENE_TR.get(house_num, f"{house_num}. ev temasında")


def _planet_effect_short(event: Mapping[str, Any]) -> str:
    transit = str(event.get("transit_body") or "").strip().lower()
    aspect = str(event.get("aspect") or "").strip().lower()
    target = str(event.get("natal_point") or "").strip().lower()
    direct = PLANET_ASPECT_TARGET_TEASER_TR.get((transit, aspect, target))
    if direct:
        return direct
    return PLANET_EFFECT_TR.get(transit, "küçük ama belirgin bir yön değişimi hissedilebilir")


def _first_sentence(text: str) -> str:
    raw = str(text or "").strip()
    if not raw:
        return ""
    parts = raw.split(".")
    return parts[0].strip().lower()


def _teaser_for_event(event: Mapping[str, Any], *, horizon: str, why_now: str, conflict: str) -> str:
    house = _target_house_num(event) or _house_num(event)
    house_scene = _house_scene_text(house)
    aspect_dynamic = _aspect_dynamic_tr(str(event.get("aspect") or ""))
    planet_effect = _planet_effect_short(event)
    if horizon == "period":
        teaser = f"Bu dönem {house_scene} alanında {aspect_dynamic} çalışıyor: {planet_effect}."
    else:
        teaser = f"Bugün {house_scene} tarafında {planet_effect}; küçük bir hamle çok şey açabilir."
    teaser_key = _first_sentence(teaser)
    if teaser_key and teaser_key in {_first_sentence(why_now), _first_sentence(conflict)}:
        if horizon == "period":
            teaser = f"Bu dönem ana sahnede ritim değişiyor; {planet_effect}."
        else:
            teaser = f"Bugün tempoda yön güncellemesi var; {planet_effect}."
    return teaser


def _chain_explainer_tr(derived_context: Mapping[str, Any]) -> str:
    if not isinstance(derived_context, Mapping):
        return ""
    angle = derived_context.get("angle") if isinstance(derived_context.get("angle"), Mapping) else {}
    target = derived_context.get("natal_target") if isinstance(derived_context.get("natal_target"), Mapping) else {}
    target_house = _safe_int(target.get("house"))
    target_sign = str(target.get("sign") or "").strip()
    dispositor = str(target.get("dispositor") or "").strip()
    rulership = target.get("rulership_houses") if isinstance(target.get("rulership_houses"), list) else []

    lines: List[str] = []
    if angle:
        angle_name = str(angle.get("name") or "").strip().upper()
        angle_sign = str(angle.get("sign") or "").strip()
        angle_ruler = str(angle.get("ruler") or "").strip()
        angle_ruler_house = _safe_int(angle.get("ruler_house"))
        if angle_name and angle_sign and angle_ruler:
            ruler_part = f"{angle_ruler_house}. ev" if angle_ruler_house else "ilgili ev"
            lines.append(
                f"{_point_label_tr(angle_name)} {angle_sign} çizgisinde; yönetici {_point_label_tr(angle_ruler)} {ruler_part} üzerinden çalışıyor."
            )
    if target_house or target_sign or dispositor:
        pieces: List[str] = []
        if target_house:
            pieces.append(f"{target_house}. ev")
        if target_sign:
            pieces.append(target_sign)
        if dispositor:
            pieces.append(f"dispozitör {_point_label_tr(dispositor)}")
        if pieces:
            lines.append(f"Etkinin omurgası {' • '.join(pieces)} hattında toplanıyor.")
    if rulership:
        house_list = [str(int(h)) for h in rulership if _safe_int(h)]
        if house_list:
            lines.append(f"Bu tema {', '.join(house_list[:2])}. ev başlıklarına da iner.")
    return " ".join(lines[:2]).strip()


def _dedupe_text_list(items: List[str], *, limit: int) -> List[str]:
    out: List[str] = []
    seen = set()
    for raw in items:
        text = " ".join(str(raw or "").split()).strip()
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(text)
        if len(out) >= limit:
            break
    return out


def build_combined_meaning(event: Mapping[str, Any]) -> Dict[str, Any]:
    seed = _seed(event, "combined")
    planet = str(event.get("transit_body") or "Saturn")
    house = _house_num(event) or 3
    sign = _sign_name(event)
    aspect = str(event.get("aspect") or "").lower().strip()
    planet_pack = PLANET_ARCHETYPE_TR.get(planet, PLANET_ARCHETYPE_TR["Saturn"])
    house_text = HOUSE_ARCHETYPE_TR.get(house, "gunluk alan")
    sign_text = SIGN_STYLE_TR.get(sign, "denge arayan")
    aspect_text = ASPECT_DYNAMICS_TR.get(aspect, "denge sınaması")
    cue = _pick_variant(BEHAVIORAL_CUES, seed=seed, key="cue")

    conflict = (
        f"{planet} etkisi {house}. evde {house_text} tarafini {sign_text} bir ritimle calistirirken "
        f"{aspect_text} baskisi yaratabilir; bu anda {cue}."
    )
    shadow = (
        f"Bu kombinasyon bazen ic sesi sertlestirip kontrol ihtiyacini buyutebilir; "
        f"{planet_pack['shadow']}."
    )
    upper = (
        f"{planet_pack['upper']}; {house_text} alaninda adimlari sadeleyip tutarli kalmak "
        f"uzun vadede daha guvenilir bir etki uretebilir."
    )

    def _dedupe(a: str, b: str) -> str:
        if a.strip().lower() == b.strip().lower():
            return f"{b} Farkli bir aci icin once niyeti sonra hizi sec."
        return b

    shadow = _dedupe(conflict, shadow)
    upper = _dedupe(shadow, upper)
    hook_tags = [planet.lower(), f"house_{house}", sign.lower(), aspect or "mixed"]
    hook_tags.extend(_house_semantic_tags(house))
    hook_tags = _dedupe_text_list(hook_tags, limit=10)
    return {
        "conflict": conflict,
        "shadow": shadow,
        "upper": upper,
        "hook_tags": hook_tags,
    }


def build_event_card(event: Mapping[str, Any], context: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    context_map = context if isinstance(context, Mapping) else {}
    natal = context_map.get("natal") if isinstance(context_map.get("natal"), Mapping) else None
    combined = build_combined_meaning(event)
    natal_promise = build_natal_promise(event, natal)
    hybrid = build_hybrid_event_context(event, natal, natal_promise)
    connected_points = hybrid.get("connected_points") if isinstance(hybrid, Mapping) else []
    natal_context_pack = hybrid.get("natal_context_pack") if isinstance(hybrid, Mapping) else {}
    derived_context = hybrid.get("derived_context") if isinstance(hybrid, Mapping) else {}
    injections = build_section_injections(event, natal_promise)
    extra = build_insight_pack(event, seed=_seed(event, "insight"), voice_style="you")
    interp = event.get("interpretation") if isinstance(event.get("interpretation"), Mapping) else {}
    time_hint = _time_hint_from_orb_phase(event)
    horizon = _horizon_from_event(event)
    guidance_raw = interp.get("do") if isinstance(interp.get("do"), list) else []
    watch_raw = interp.get("watch") if isinstance(interp.get("watch"), list) else []
    domains = event.get("domains") if isinstance(event.get("domains"), list) else []
    domain = str(domains[0]) if domains else ""
    ranking = event.get("ranking") if isinstance(event.get("ranking"), Mapping) else {}
    exact_in_days = ranking.get("exact_in_days")
    houses = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}

    guidance = _dedupe_text_list(
        [injections["guidance"]] + [str(x).strip() for x in guidance_raw if str(x).strip()],
        limit=3,
    )

    watch_out = _dedupe_text_list(
        [injections["watch"]] + [str(x).strip() for x in watch_raw if str(x).strip()],
        limit=2,
    )

    card = {
        "event_id": str(event.get("event_id") or ""),
        "title": str((interp.get("headline_short") or interp.get("headline") or "Aktif Transit")).strip(),
        "signature": _signature(event, time_hint=time_hint),
        "conflict": f"{combined['conflict']} {injections['conflict']}".strip(),
        "shadow": f"{combined['shadow']} {injections['shadow']}".strip(),
        "upper": f"{combined['upper']} {injections['upper']}".strip(),
        "extra_line": extra.get("conflict_short"),
        "time_hint": time_hint,
        "time_hint_tr": _time_hint_for_signature(event, existing=time_hint),
        "horizon": horizon,
        "guidance": guidance,
        "watch_out": watch_out,
        "hook_tags": combined["hook_tags"],
        "connected_points": connected_points if isinstance(connected_points, list) else [],
        "natal_context_pack": natal_context_pack if isinstance(natal_context_pack, Mapping) else {},
        "derived_context": derived_context if isinstance(derived_context, Mapping) else {},
        "scene": {
            "start_house": _safe_int(houses.get("transit_in_natal_house")),
            "outcome_house": _safe_int(houses.get("natal_point_house")),
        },
        "natal_promise": natal_promise,
        "tags": {
            "duration": _duration_label(str(event.get("bucket") or "")),
            "phase": _phase_label(str(event.get("phase") or "")),
            "domain": DOMAIN_TR.get(domain, domain or "general"),
            "intensity": min(1.0, max(0.0, _weight(event) / 1.6)),
            "exact_in_days": exact_in_days,
        },
    }
    chain_line = build_chain_explainer_tr(event, derived_context if isinstance(derived_context, Mapping) else {})
    if chain_line:
        existing_why = str(card.get("why_now") or "").strip()
        card["why_now"] = f"{chain_line} {existing_why}".strip()
    card = build_card_copy(
        card,
        natal_context_pack if isinstance(natal_context_pack, Mapping) else {},
        connected_points if isinstance(connected_points, list) else [],
        event,
    )
    quality_context = {
        "transit_planet": event.get("transit_body"),
        "transit_house": houses.get("transit_in_natal_house"),
        "aspect": event.get("aspect"),
        "target": event.get("natal_point"),
        "orb_deg": event.get("orb_deg"),
        "phase": event.get("phase"),
        "duration": event.get("bucket"),
    }
    connected = card.get("connected_points") if isinstance(card.get("connected_points"), list) else []
    if not connected:
        connected = natal_promise.get("connected_points") if isinstance(natal_promise, Mapping) else []
    out = apply_copy_quality_layer(card, connected, context=quality_context)

    # Deterministic title/signature/teaser are set after quality layer to avoid drift.
    out["horizon"] = horizon
    out["title"] = _deterministic_title(event, fallback=str(out.get("title") or "Aktif Transit"))
    resolved_time_hint = str(out.get("time_hint_tr") or out.get("time_hint") or time_hint or "").strip()
    out["signature"] = _signature(event, time_hint=resolved_time_hint)
    out["signature_tr"] = _signature_tr(event, time_hint=resolved_time_hint)
    out["signature"] = out["signature_tr"]
    out["time_hint_tr"] = resolved_time_hint
    out["teaser"] = _teaser_for_event(
        event,
        horizon=horizon,
        why_now=str(out.get("why_now") or ""),
        conflict=str(out.get("conflict") or ""),
    )
    if chain_line and chain_line.lower() not in str(out.get("teaser") or "").lower():
        out["teaser"] = f"{chain_line} {str(out.get('teaser') or '').strip()}".strip()
    if horizon == "period":
        out = rewrite_period_card_tr(out, event=event)
    return out


def build_period_core(
    report: Mapping[str, Any],
    event_cards: List[Mapping[str, Any]] | None = None,
) -> Dict[str, Any]:
    items = report.get("display", {}).get("items", []) if isinstance(report.get("display"), Mapping) else []
    typed_items = [item for item in items if isinstance(item, Mapping)]
    item_by_id = {str(item.get("event_id") or ""): dict(item) for item in typed_items}

    cards = [dict(card) for card in (event_cards or []) if isinstance(card, Mapping)]
    selected_ids = [str(card.get("event_id") or "") for card in cards if str(card.get("event_id") or "").strip()]
    selected = [item_by_id[eid] for eid in selected_ids if eid in item_by_id]
    selected.sort(key=lambda item: selected_ids.index(str(item.get("event_id") or "")))
    card_by_id = {
        str(card.get("event_id") or ""): card
        for card in cards
        if isinstance(card, Mapping) and str(card.get("event_id") or "").strip()
    }
    selected_enriched: List[Dict[str, Any]] = []
    for item in selected:
        event_id = str(item.get("event_id") or "")
        merged = dict(item)
        card_ctx = card_by_id.get(event_id)
        if isinstance(card_ctx, Mapping):
            derived_context = card_ctx.get("derived_context")
            if isinstance(derived_context, Mapping):
                merged["derived_context"] = dict(derived_context)
        selected_enriched.append(merged)

    house_counter: Counter[int] = Counter()
    domain_counter: Counter[str] = Counter()
    for item in selected_enriched:
        house = _house_num(item)
        if house is not None:
            house_counter[house] += 1
        domains = item.get("domains") if isinstance(item.get("domains"), list) else []
        for domain in domains:
            domain_counter[str(domain)] += 1

    dominant_house = house_counter.most_common(1)[0][0] if house_counter else None
    title = HOUSE_THEME.get(dominant_house or -1, "Denge ve Yapi Temasi Derinlesiyor")
    metrics = report.get("metrics") if isinstance(report.get("metrics"), Mapping) else {}
    pressure = float(metrics.get("pressure_index") or 0.0)
    support = float(metrics.get("support_index") or 0.0)
    domains = [DOMAIN_TR.get(key, key) for key, _ in domain_counter.most_common(2)]
    if not domains:
        domains = ["zihin", "iliski"]

    planet = str(selected[0].get("transit_body") or "Saturn") if selected else "Saturn"
    period_copy = build_period_copy(
        selected_events=selected,
        natal_snapshot=report.get("natal") if isinstance(report, Mapping) else {},
        dominant_house=dominant_house,
        dominant_planet=planet,
        pressure=pressure,
        support=support,
        domains=domains,
    )
    story = period_copy["core_story"]
    upper = period_copy["upper_meaning"]
    root_causes_raw = period_copy.get("root_causes") if isinstance(period_copy.get("root_causes"), list) else []
    root_causes: List[Dict[str, Any]] = []
    selected_id_set = set(selected_ids)
    for cause in root_causes_raw:
        if not isinstance(cause, Mapping):
            continue
        ids = []
        for eid in cause.get("evidence_ids") or []:
            token = str(eid or "").strip()
            if token and token in selected_id_set and token not in ids:
                ids.append(token)
        root_causes.append(
            {
                "key": str(cause.get("key") or ""),
                "score": float(cause.get("score") or 0.0),
                "evidence": ids,
            }
        )

    story_tracks: Dict[str, Dict[str, Any]] = {}
    event_story_map: Dict[str, str] = {}
    cards_with_tracks: List[Dict[str, Any]] = []
    for raw_card in cards:
        card = dict(raw_card)
        event_id = str(card.get("event_id") or "").strip()
        track_id = infer_story_track_id(card, root_causes)
        card["story_track_id"] = track_id
        event_story_map[event_id] = track_id
        if track_id not in story_tracks:
            story_tracks[track_id] = build_story_track_copy(track_id, card)
        card["period_story"] = dict(story_tracks.get(track_id) or {})
        cards_with_tracks.append(card)
    cards = cards_with_tracks

    dominant_planet = str(selected_enriched[0].get("transit_body") or "Saturn") if selected_enriched else "Saturn"
    tags = [
        {"type": "dominant_house", "value": str(dominant_house or "3")},
        {"type": "dominant_planet", "value": dominant_planet},
    ]
    promise_themes: List[str] = []
    for card in cards:
        if not isinstance(card, Mapping):
            continue
        np = card.get("natal_promise") if isinstance(card.get("natal_promise"), Mapping) else {}
        drivers = np.get("drivers") if isinstance(np.get("drivers"), list) else []
        for driver in drivers:
            if isinstance(driver, Mapping):
                label = str(driver.get("label") or driver.get("theme") or "").strip()
            else:
                label = str(driver or "").strip()
            if label and label not in promise_themes:
                promise_themes.append(label)
                if len(promise_themes) >= 3:
                    break
        if len(promise_themes) >= 3:
            break

    result = {
        "title": title,
        "core_story": story,
        "upper_meaning": upper,
        "tags": tags,
        "featured_events": selected_enriched,
    }

    try:
        narr = build_period_story(
            PeriodStoryContext(
                period_core=result,
                chart_snapshot=report.get("natal") if isinstance(report.get("natal"), Mapping) else {},
                natal_promise={"themes": promise_themes},
                locale="tr",
                enable_fun=True,
            )
        )
        if narr.big_picture:
            result["big_picture"] = narr.big_picture
        if narr.mechanism:
            result["mechanism"] = narr.mechanism
        if narr.upper_meaning:
            result["upper_meaning"] = narr.upper_meaning
        result["narrative_version"] = "period_story_v1"
        result["_period_story_debug"] = narr.debug
    except Exception:
        # Narrative layer must stay non-blocking.
        pass

    if root_causes:
        result["_debug_root_causes"] = root_causes
    if story_tracks:
        result["story_tracks"] = story_tracks
    if event_story_map:
        result["_event_story_map"] = event_story_map
    return result


def build_daily_line(date: str, top_event: Mapping[str, Any] | None, context: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    context_map = context if isinstance(context, Mapping) else {}
    if top_event and isinstance(top_event, Mapping):
        card = build_event_card(top_event, context=context_map)
        lines = [
            card["conflict"].split(".")[0].strip() + ".",
            "Tepki vermeden once ritmi yavaslatmak bugun daha iyi calisir.",
            "Netlik aceleden daha guclu bir sonuc uretebilir.",
        ]
    else:
        lines = [
            "Bugun ritim daha sade akabilir.",
            "Kucuk adimlari korumak dengeyi tutar.",
            "Gunu sakin bir planla tamamlamak daha iyi hissettirebilir.",
        ]
    return {
        "date": date,
        "summary": " ".join(lines[:3]),
        "lines": lines[:3],
        "dot_intensity": 1 if top_event else 0,
    }


def build_active_event_cards(report: Mapping[str, Any], *, max_cards: int = 5) -> List[Dict[str, Any]]:
    items = report.get("display", {}).get("items", []) if isinstance(report.get("display"), Mapping) else []
    typed_items = [item for item in items if isinstance(item, Mapping) and _is_public_allowed(item)]
    selected, _meta = select_event_ids(typed_items, max_cards=max_cards, natal=report.get("natal") if isinstance(report, Mapping) else None)
    context = {"natal": report.get("natal")} if isinstance(report, Mapping) else {}
    cards: List[Dict[str, Any]] = []
    for event in selected[:max_cards]:
        card = build_event_card(event, context=context)
        cards.append(card)
    cards = _inject_cofeatured_links(cards, selected)
    return _apply_global_guidance_diversity(cards, selected)


def _inject_cofeatured_links(
    cards: List[Dict[str, Any]],
    selected_events: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    event_by_id = {
        str(e.get("event_id") or ""): e
        for e in selected_events
        if isinstance(e, Mapping) and str(e.get("event_id") or "").strip()
    }
    out: List[Dict[str, Any]] = []
    for card in cards:
        card_out = dict(card)
        eid = str(card_out.get("event_id") or "")
        event = event_by_id.get(eid) or {}
        current_house = _house_num(event)
        current_body = str(event.get("transit_body") or "").strip().lower()
        derived = card_out.get("derived_context") if isinstance(card_out.get("derived_context"), Mapping) else {}
        links = list(derived.get("links") or []) if isinstance(derived.get("links"), list) else []
        existing = {(str(x.get("type") or ""), str(x.get("event_id") or ""), str(x.get("target") or "")) for x in links if isinstance(x, Mapping)}

        angle = derived.get("angle") if isinstance(derived.get("angle"), Mapping) else {}
        angle_ruler = str(angle.get("ruler") or "").strip().lower()
        if angle_ruler:
            for peer_id, peer in event_by_id.items():
                if peer_id == eid:
                    continue
                peer_body = str(peer.get("transit_body") or "").strip().lower()
                peer_target = str(peer.get("natal_point") or "").strip().lower()
                if peer_body == current_body and peer_target == angle_ruler:
                    key = ("cofeatured_hit", peer_id, "")
                    if key not in existing:
                        links.append(
                            {
                                "type": "cofeatured_hit",
                                "event_id": peer_id,
                                "target_event_id": peer_id,
                                "because": "same transit hits ASC and ASC ruler",
                            }
                        )
                        existing.add(key)
                    break

        if current_body and isinstance(current_house, int):
            for peer_id, peer in event_by_id.items():
                if peer_id == eid:
                    continue
                peer_body = str(peer.get("transit_body") or "").strip().lower()
                peer_house = _house_num(peer)
                if peer_body == current_body and peer_house == current_house:
                    key = ("cofeatured_hit", peer_id, "")
                    if key not in existing:
                        links.append(
                            {
                                "type": "cofeatured_hit",
                                "event_id": peer_id,
                                "target_event_id": peer_id,
                                "because": f"{_point_label_tr(current_body)} aynı ev odağında ikinci vurgu",
                            }
                        )
                        existing.add(key)
                    break

        if links:
            derived_out = dict(derived)
            derived_out["links"] = links
            card_out["derived_context"] = derived_out
        out.append(card_out)
    return out


def pick_top_event(report: Mapping[str, Any]) -> Mapping[str, Any] | None:
    items = report.get("display", {}).get("items", []) if isinstance(report.get("display"), Mapping) else []
    typed = [item for item in items if isinstance(item, Mapping) and _is_public_allowed(item)]
    selected = [item for item in typed if _event_selected(item)]
    if not selected:
        return None
    return max(selected, key=_weight)


def _is_public_allowed(item: Mapping[str, Any]) -> bool:
    return is_public_event(item)


def _time_hint_from_orb_phase(event: Mapping[str, Any]) -> str:
    phase = str(event.get("phase") or "").strip().lower()
    bucket = str(event.get("bucket") or "").strip().lower()
    try:
        orb = float(event.get("orb_deg"))
    except (TypeError, ValueError):
        orb = 9.9
    if bucket == "short":
        return "Bugün/yarın: kısa dalga"
    if phase in {"exact", "exactish"} or orb <= 0.2:
        return "Şu an güçlü, dalga dalga birkaç ay"
    if phase == "applying":
        return "Yaklaşıyor; etkisi artıyor"
    if phase == "separating":
        return "Geri çekiliyor; izi kalır"
    return "Etkisi sürüyor; ritim dalgalı ilerleyebilir"


def _apply_global_guidance_diversity(
    cards: List[Dict[str, Any]],
    selected_events: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    event_map = {str(item.get("event_id") or ""): item for item in selected_events if isinstance(item, Mapping)}
    seen_guidance: set[str] = set()
    seen_watch: set[str] = set()
    out: List[Dict[str, Any]] = []

    for card in cards:
        card_out = dict(card)
        eid = str(card_out.get("event_id") or "")
        event = event_map.get(eid) or {}
        house = _card_target_house(card_out, event)
        tone = _normalize_tone(str(card_out.get("tone") or card_out.get("conflict_tone") or ""), str(event.get("aspect") or ""))
        disp = _card_dispositor(card_out)
        seed = int(hashlib.sha1(f"{eid}|diversify".encode("utf-8")).hexdigest()[:8], 16)

        guidance: List[str] = []
        watch_out: List[str] = []
        existing_guidance = [str(x) for x in (card_out.get("guidance") or []) if str(x).strip()]
        existing_watch = [str(x) for x in (card_out.get("watch_out") or []) if str(x).strip()]

        house_pool = HOUSE_GUIDANCE_POOL_TR.get(house, [])
        _append_from_rotated_pool(guidance, house_pool, seen_guidance, seed=seed, cap=1)
        _append_from_rotated_pool(guidance, TONE_GUIDANCE_POOL_TR.get(tone, []), seen_guidance, seed=seed + 11, cap=2)
        _append_from_rotated_pool(guidance, MECHANISM_GUIDANCE_TR.get(disp, []), seen_guidance, seed=seed + 23, cap=3)
        _append_from_rotated_pool(guidance, existing_guidance, seen_guidance, seed=seed + 37, cap=3)
        _append_from_rotated_pool(guidance, FALLBACK_GUIDANCE_TR, seen_guidance, seed=seed + 41, cap=3)
        if len(guidance) < 2:
            _append_from_rotated_pool(guidance, FALLBACK_GUIDANCE_TR, seen_guidance, seed=seed + 47, cap=2, ignore_seen=True)
        card_out["guidance"] = guidance[:3]

        _append_from_rotated_pool(watch_out, TONE_WATCH_POOL_TR.get(tone, []), seen_watch, seed=seed + 3, cap=2)
        _append_from_rotated_pool(watch_out, existing_watch, seen_watch, seed=seed + 13, cap=2)
        _append_from_rotated_pool(
            watch_out,
            ["Aşırı yüklenme.", "Odak kaybı.", "Acele karar."],
            seen_watch,
            seed=seed + 19,
            cap=2,
        )
        if len(watch_out) < 2:
            _append_from_rotated_pool(
                watch_out,
                ["Aşırı yüklenme.", "Odak kaybı.", "Acele karar."],
                seen_watch,
                seed=seed + 29,
                cap=2,
                ignore_seen=True,
            )
        card_out["watch_out"] = watch_out[:2]
        out.append(card_out)
    return out


def _append_from_rotated_pool(
    target: List[str],
    pool: List[str],
    seen: set[str],
    *,
    seed: int,
    cap: int,
    ignore_seen: bool = False,
) -> None:
    if len(target) >= cap or not pool:
        return
    normalized_pool = [" ".join(str(item or "").split()).strip() for item in pool if str(item or "").strip()]
    if not normalized_pool:
        return
    start = seed % len(normalized_pool)
    ordered = normalized_pool[start:] + normalized_pool[:start]
    for raw in ordered:
        if len(target) >= cap:
            break
        key = raw.lower()
        if not ignore_seen and key in seen:
            continue
        if key in {item.lower() for item in target}:
            continue
        seen.add(key)
        target.append(raw)


def _card_target_house(card: Mapping[str, Any], event: Mapping[str, Any]) -> int | None:
    pack = card.get("natal_context_pack") if isinstance(card.get("natal_context_pack"), Mapping) else {}
    target = pack.get("target") if isinstance(pack.get("target"), Mapping) else {}
    try:
        raw = target.get("house")
        if raw is not None:
            return int(raw)
    except (TypeError, ValueError):
        pass
    houses = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}
    for key in ("natal_point_house", "transit_in_natal_house"):
        try:
            raw = houses.get(key)
            if raw is not None:
                return int(raw)
        except (TypeError, ValueError):
            continue
    return None


def _card_dispositor(card: Mapping[str, Any]) -> str:
    pack = card.get("natal_context_pack") if isinstance(card.get("natal_context_pack"), Mapping) else {}
    disp = pack.get("dispositor") if isinstance(pack.get("dispositor"), Mapping) else {}
    return str(disp.get("planet") or "").strip().lower()


def _normalize_tone(raw: str, aspect: str) -> str:
    tone = str(raw or "").strip().lower()
    mapping = {"flow": "flow", "chance": "chance", "friction": "friction", "mirror": "mirror", "focus": "focus"}
    compatibility = {"pressure": "friction", "opportunity": "chance"}
    if tone in mapping:
        return tone
    if tone in compatibility:
        return compatibility[tone]
    aspect_key = str(aspect or "").strip().lower()
    aspect_map = {
        "trine": "flow",
        "sextile": "chance",
        "square": "friction",
        "opposition": "mirror",
        "conjunction": "focus",
    }
    return aspect_map.get(aspect_key, "focus")
