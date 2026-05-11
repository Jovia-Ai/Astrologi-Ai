from __future__ import annotations

import hashlib
import re
from collections import Counter
from typing import Any, Dict, List, Mapping

from app.core.config import settings
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
from app.transit.narrative.period_semantic_focus import resolve_period_semantic_focus
from app.transit.narrative.period_voice_policy import build_period_voice_policy
from app.transit.narrative.phrase_lib_tr import render_signature_tr
from app.transit.narrative.point_policy import is_public_event
from app.transit.narrative.selection import select_event_ids
from app.transit.narrative.text_quality_tr import (
    apply_copy_quality_layer,
    build_period_copy,
    rewrite_event_card_tr,
    rewrite_period_card_tr,
    tr_normalize,
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

_PR_D_V1_ALLOWED_CHAPTER_TYPES = {"saturn_return", "nodal_return", "nodal_activation"}
_PR_D_V1_EXCLUDED_CHAPTER_TYPES = {
    "structural_natal_chapter",
    "profection_year",
    "progressed_lunation",
    "solar_return_theme",
    "outer_planet_angle_hit",
}


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
    _ = time_hint
    return render_signature_tr(event)


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


def _enum_token(value: Any) -> str:
    raw = getattr(value, "value", value)
    return str(raw or "").strip().lower()


def _chapter_confidence_rank(value: Any) -> int:
    return {"low": 1, "medium": 2, "high": 3}.get(_enum_token(value), 0)


def _semantic_focus_confidence(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def is_life_chapter_priority_eligible(
    active_life_chapter: Mapping[str, Any] | None,
    semantic_focus_result: Any,
    flag_enabled: bool,
) -> bool:
    if not flag_enabled:
        return False
    if not isinstance(active_life_chapter, Mapping) or not active_life_chapter:
        return False
    chapter_type = _enum_token(active_life_chapter.get("chapter_type"))
    if chapter_type in _PR_D_V1_EXCLUDED_CHAPTER_TYPES or chapter_type not in _PR_D_V1_ALLOWED_CHAPTER_TYPES:
        return False
    if _chapter_confidence_rank(active_life_chapter.get("confidence")) < 2:
        return False
    if str(getattr(semantic_focus_result, "source", "") or "").strip() != "life_chapter":
        return False
    return _semantic_focus_confidence(getattr(semantic_focus_result, "confidence", 0.0)) >= 0.55


def _build_chapter_priority_debug(
    *,
    active_life_chapter: Mapping[str, Any] | None,
    semantic_focus_result: Any,
    flag_enabled: bool,
) -> Dict[str, Any]:
    chapter = active_life_chapter if isinstance(active_life_chapter, Mapping) else {}
    chapter_type = _enum_token(chapter.get("chapter_type"))
    semantic_source = str(getattr(semantic_focus_result, "source", "") or "").strip() or "unknown"
    semantic_confidence = _semantic_focus_confidence(getattr(semantic_focus_result, "confidence", 0.0))

    payload: Dict[str, Any] = {
        "enabled": bool(flag_enabled),
        "applied": False,
        "owner": "life_chapter",
        "chapter_type": chapter_type,
        "chapter_id": str(chapter.get("chapter_id") or "").strip(),
        "semantic_focus_source": semantic_source,
        "scope": "pr_d_v1_tier_1",
        "event_cards_role": "selected_owner",
    }
    if not flag_enabled:
        payload["reason"] = "flag_disabled"
        return payload
    if not chapter:
        payload["reason"] = "no_active_life_chapter"
        return payload
    if chapter_type in _PR_D_V1_EXCLUDED_CHAPTER_TYPES:
        payload["reason"] = "excluded_chapter_type"
        return payload
    if chapter_type not in _PR_D_V1_ALLOWED_CHAPTER_TYPES:
        payload["reason"] = "unsupported_chapter_type"
        return payload
    if _chapter_confidence_rank(chapter.get("confidence")) < 2:
        payload["reason"] = "insufficient_chapter_confidence"
        return payload
    if semantic_source != "life_chapter":
        payload["reason"] = "semantic_focus_not_life_chapter"
        return payload
    if semantic_confidence < 0.55:
        payload["reason"] = "semantic_focus_confidence_too_low"
        return payload

    payload["applied"] = is_life_chapter_priority_eligible(
        chapter,
        semantic_focus_result,
        flag_enabled,
    )
    payload["event_cards_role"] = "evidence_support"
    payload["reason"] = "eligible_tier1_life_chapter"
    return payload


def _safe_float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _mapping_or_none(value: Any) -> Dict[str, Any] | None:
    return dict(value) if isinstance(value, Mapping) else None


def _mapping_list(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, Mapping)]


def _list_str(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    out: List[str] = []
    for item in value:
        text = str(item or "").strip()
        if text:
            out.append(text)
    return out


def _event_ids_from_spine(canonical_period_spine: Mapping[str, Any] | None) -> List[str]:
    spine = canonical_period_spine if isinstance(canonical_period_spine, Mapping) else {}
    return _list_str(spine.get("matched_event_ids"))


def _summarize_natal_target(target: Any) -> Dict[str, Any]:
    if not isinstance(target, Mapping):
        return {}
    summary: Dict[str, Any] = {}
    for key in ("name", "house", "sign", "dispositor", "rulership_houses", "node_id"):
        if key in target:
            value = target.get(key)
            if isinstance(value, list):
                summary[key] = [item for item in value if item is not None]
            else:
                summary[key] = value
    return summary


def _summarize_derived_context(derived_context: Any) -> Dict[str, Any]:
    if not isinstance(derived_context, Mapping):
        return {}
    return {
        "derived_domains": _clean_domain_list(derived_context.get("derived_domains")),
        "motifs": _list_str(derived_context.get("motifs")),
        "connected_points": _mapping_list(derived_context.get("connected_points")),
        "links": _mapping_list(derived_context.get("links")),
        "natal_target": _summarize_natal_target(derived_context.get("natal_target")),
    }


def _house_scene_ref(item: Mapping[str, Any], derived_context: Mapping[str, Any] | None) -> str | None:
    natal_target = (
        derived_context.get("natal_target")
        if isinstance(derived_context.get("natal_target"), Mapping)
        else {}
    ) if isinstance(derived_context, Mapping) else {}
    target_house = natal_target.get("house")
    if target_house is not None:
        return f"house_{target_house}"
    houses = item.get("houses") if isinstance(item.get("houses"), Mapping) else {}
    transit_house = houses.get("transit_in_natal_house")
    if transit_house is not None:
        return f"house_{transit_house}"
    return None


def _event_domain_ref(item: Mapping[str, Any], derived_context: Mapping[str, Any] | None) -> str | None:
    if isinstance(derived_context, Mapping):
        derived_domains = _clean_domain_list(derived_context.get("derived_domains"))
        if derived_domains:
            return derived_domains[0]
    domains = item.get("domains") if isinstance(item.get("domains"), list) else []
    for domain in domains:
        text = str(domain or "").strip()
        if text:
            return text
    return None


def _build_period_evidence_items(
    featured_events: List[Dict[str, Any]],
    *,
    semantic_focus_source: str | None,
) -> List[Dict[str, Any]]:
    evidence_items: List[Dict[str, Any]] = []
    for index, item in enumerate(featured_events):
        if not isinstance(item, Mapping):
            continue
        event_id = str(item.get("event_id") or "").strip()
        if not event_id:
            continue
        derived_context = item.get("derived_context") if isinstance(item.get("derived_context"), Mapping) else {}
        chapter_role = item.get("chapter_role") if isinstance(item.get("chapter_role"), Mapping) else {}
        evidence_items.append(
            {
                "event_id": event_id,
                "evidence_role": str(chapter_role.get("role") or item.get("semantic_role") or "support").strip() or "support",
                "rank": int(item.get("selection_index") if item.get("selection_index") is not None else index),
                "transit_body": _safe_text(item.get("transit_body")),
                "natal_point": _safe_text(item.get("natal_point")),
                "aspect": _safe_text(item.get("aspect")),
                "public_event_type": _safe_text(item.get("event_kind") or item.get("event_subtype") or item.get("event_family")),
                "domain": _event_domain_ref(item, derived_context),
                "house_scene": _house_scene_ref(item, derived_context),
                "derived_context_summary": _summarize_derived_context(derived_context),
                "natal_target_summary": _summarize_natal_target(derived_context.get("natal_target")),
                "timing_phase": _safe_text(item.get("phase")),
                "timing_bucket": _safe_text(item.get("bucket")),
                "chapter_role": dict(chapter_role) if chapter_role else None,
                "story_score": _safe_float_or_none(item.get("story_score")),
                "semantic_owner": _safe_text(item.get("semantic_owner")) or _safe_text(semantic_focus_source),
                "debug_refs": {
                    "selection_index": item.get("selection_index"),
                    "selection_mode": item.get("selection_mode"),
                    "raw_ref": _mapping_or_none(item.get("raw_ref")),
                },
            }
        )
    return evidence_items


def _build_period_card_context(
    *,
    semantic_focus_result: Any,
    chapter_priority: Mapping[str, Any] | None,
    canonical_period_spine: Mapping[str, Any] | None,
    featured_events: List[Dict[str, Any]],
    period_reading_v1: Mapping[str, Any] | None,
    composer_plan: Mapping[str, Any] | None,
    manifestation_context: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    semantic_source = _safe_text(getattr(semantic_focus_result, "source", None))
    selected_meaning = _safe_text(getattr(semantic_focus_result, "selected_meaning", None))
    meaning_family = _safe_text(getattr(semantic_focus_result, "meaning_family", None))
    confidence = _safe_float_or_none(getattr(semantic_focus_result, "confidence", None))
    primary_domain = _safe_text(getattr(semantic_focus_result, "primary_domain", None))
    secondary_domains = _list_str(getattr(semantic_focus_result, "secondary_domains", []))
    suppressed_meanings = _list_str(getattr(semantic_focus_result, "suppressed_meanings", []))
    chapter_priority_map = dict(chapter_priority or {})
    reading = period_reading_v1 if isinstance(period_reading_v1, Mapping) else {}
    blocks = reading.get("blocks") if isinstance(reading.get("blocks"), list) else []
    composer = composer_plan if isinstance(composer_plan, Mapping) else {}
    matched_event_ids = _event_ids_from_spine(canonical_period_spine)
    return {
        "version": "period_card_context_v1",
        "owner_ref": {
            "semantic_focus_source": semantic_source,
            "selected_meaning": selected_meaning,
            "meaning_family": meaning_family,
            "confidence": confidence,
        },
        "primary_meaning": {
            "label": selected_meaning,
            "primary_domain": primary_domain,
            "secondary_domains": secondary_domains,
            "suppressed_meanings": suppressed_meanings,
        },
        "source_owner": {
            "chapter_priority_applied": bool(chapter_priority_map.get("applied")),
            "chapter_type": _safe_text(chapter_priority_map.get("chapter_type")),
            "event_cards_role": _safe_text(chapter_priority_map.get("event_cards_role")),
        },
        "chapter_priority": chapter_priority_map,
        "main_domains": [domain for domain in [primary_domain, *secondary_domains] if domain],
        "suppressed_meanings": suppressed_meanings,
        "period_reading_ref": {
            "version": _safe_text(reading.get("version")),
            "full_text": _safe_text(reading.get("full_text")),
            "block_roles": [
                str(block.get("role") or "").strip()
                for block in blocks
                if isinstance(block, Mapping) and str(block.get("role") or "").strip()
            ],
        },
        "composer_frame": {
            "semantic_mode": _safe_text(composer.get("semantic_mode")),
            "hook": _safe_text(composer.get("hook")),
            "scene_anchor": _safe_text(composer.get("scene_anchor")),
            "core_contrast": _safe_text(composer.get("core_contrast")),
            "mechanism": _safe_text(composer.get("mechanism")),
            "growth_edge": _safe_text(composer.get("growth_edge")),
            "what_it_builds": _safe_text(composer.get("what_it_builds")),
            "closer": _safe_text(composer.get("closer")),
        },
        "manifestation_context": dict(manifestation_context) if isinstance(manifestation_context, Mapping) else None,
        "natal_activation_ref": {
            "matched_event_ids": matched_event_ids,
            "top_hook_ids": [],
        } if matched_event_ids else None,
        "evidence_items": _build_period_evidence_items(
            featured_events,
            semantic_focus_source=semantic_source,
        ),
        "debug": {
            "authority_inputs": [
                "semantic_focus",
                "chapter_priority",
                "canonical_period_spine",
                "featured_events",
                "manifestation_context",
            ],
            "framing_only_inputs": [
                "period_reading_v1",
                "composer_plan",
            ],
            "blocked_authority_inputs": [
                "blocks[]",
                "daily_synthesis.body",
                "best_times.score_by_intent",
                "heat",
                "rating",
                "story_tracks",
                "_event_story_map",
                "profile_v8",
                "full_map_v8",
                "personality_imprint",
                "meaning_graph_v1_1",
            ],
            "period_reading_reparsed_for_evidence": False,
            "composer_plan_reparsed_for_evidence": False,
        },
    }


def _find_ids_in_canonical_nodes(nodes: Any, node_id: str | None) -> List[str]:
    if not node_id:
        return []
    out: List[str] = []
    for node in nodes if isinstance(nodes, list) else []:
        if not isinstance(node, Mapping):
            continue
        candidate = str(node.get("id") or "").strip()
        if candidate == node_id and candidate not in out:
            out.append(candidate)
    return out


def _spine_line_refs(chart_spine: Any, spine_lines: List[str], target_node_id: str | None) -> List[Dict[str, Any]]:
    if not isinstance(chart_spine, Mapping):
        return []
    refs: List[Dict[str, Any]] = []
    for line_key in spine_lines:
        line = chart_spine.get(line_key)
        if not isinstance(line, Mapping):
            continue
        refs.append(
            {
                "line_key": line_key,
                "node_id": _safe_text(line.get("node_id")),
                "label": _safe_text(line.get("label") or line.get("summary")),
                "matches_target_node": bool(target_node_id and str(line.get("node_id") or "").strip() == target_node_id),
            }
        )
    return refs


def _filter_activation_hooks(meaning_graph: Any, *, target_node_id: str | None, spine_lines: List[str]) -> List[Dict[str, Any]]:
    graph = meaning_graph if isinstance(meaning_graph, Mapping) else {}
    hooks = graph.get("activation_hooks") if isinstance(graph.get("activation_hooks"), list) else []
    refs: List[Dict[str, Any]] = []
    for hook in hooks:
        if not isinstance(hook, Mapping):
            continue
        hook_target = str(hook.get("target_node_id") or "").strip()
        hook_spine_lines = _list_str(hook.get("spine_lines"))
        if target_node_id and hook_target == target_node_id:
            pass
        elif spine_lines and any(line in hook_spine_lines for line in spine_lines):
            pass
        else:
            continue
        refs.append(
            {
                "hook_id": _safe_text(hook.get("hook_id")),
                "type": _safe_text(hook.get("type")),
                "target_node_id": hook_target or None,
                "spine_lines": hook_spine_lines,
                "domains": _list_str(hook.get("domains")),
            }
        )
    return refs


def _filter_structural_refs(routes: Any, *, target_node_id: str | None, spine_lines: List[str]) -> List[Dict[str, Any]]:
    refs: List[Dict[str, Any]] = []
    for route in routes if isinstance(routes, list) else []:
        if not isinstance(route, Mapping):
            continue
        linked_ids = _list_str(route.get("linked_node_ids"))
        source_candidates = _list_str(route.get("source_candidates"))
        candidate_id = str(route.get("id") or "").strip()
        if target_node_id and (candidate_id == target_node_id or target_node_id in linked_ids):
            pass
        elif spine_lines and any(line in source_candidates for line in spine_lines):
            pass
        else:
            continue
        refs.append(
            {
                "id": candidate_id or None,
                "label": _safe_text(route.get("label")),
                "domain": _safe_text(route.get("domain")),
                "linked_node_ids": linked_ids,
                "source_candidates": source_candidates,
            }
        )
    return refs


def _build_event_natal_links(featured_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    links: List[Dict[str, Any]] = []
    for item in featured_events:
        if not isinstance(item, Mapping):
            continue
        event_id = str(item.get("event_id") or "").strip()
        if not event_id:
            continue
        derived_context = item.get("derived_context") if isinstance(item.get("derived_context"), Mapping) else {}
        natal_promise = item.get("natal_promise") if isinstance(item.get("natal_promise"), Mapping) else {}
        link = {
            "event_id": event_id,
            "natal_target": _summarize_natal_target(derived_context.get("natal_target")),
            "derived_domains": _clean_domain_list(derived_context.get("derived_domains")),
            "motifs": _list_str(derived_context.get("motifs")),
        }
        if natal_promise:
            link["natal_promise"] = {
                "summary": _safe_text(natal_promise.get("summary")),
                "drivers": _mapping_list(natal_promise.get("drivers")),
            }
        links.append(link)
    return links


def _build_natal_context_for_period_cards(
    *,
    canonical_natal_state: Mapping[str, Any] | None,
    semantic_focus_result: Any,
    canonical_period_spine: Mapping[str, Any] | None,
    featured_events: List[Dict[str, Any]],
    active_life_chapter: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    state = canonical_natal_state if isinstance(canonical_natal_state, Mapping) else {}
    target_node_id = _safe_text((canonical_period_spine or {}).get("target_node_id"))
    spine_lines = _list_str((canonical_period_spine or {}).get("spine_lines"))
    core_promises = state.get("core_promises") if isinstance(state.get("core_promises"), list) else []
    contradictions = state.get("contradictions") if isinstance(state.get("contradictions"), list) else []
    chart_spine = state.get("chart_spine") if isinstance(state.get("chart_spine"), Mapping) else {}
    meaning_graph = state.get("meaning_graph") if isinstance(state.get("meaning_graph"), Mapping) else {}
    structural_state = state.get("structural_state") if isinstance(state.get("structural_state"), Mapping) else {}
    active_chapter = active_life_chapter if isinstance(active_life_chapter, Mapping) else {}
    return {
        "version": "natal_context_for_period_cards_v1",
        "chart_id": _safe_text(state.get("chart_id")),
        "semantic_owner_ref": {
            "source": _safe_text(getattr(semantic_focus_result, "source", None)),
            "selected_meaning": _safe_text(getattr(semantic_focus_result, "selected_meaning", None)),
        },
        "activated_core_promise_ids": _find_ids_in_canonical_nodes(core_promises, target_node_id),
        "activated_contradiction_ids": _find_ids_in_canonical_nodes(contradictions, target_node_id),
        "chart_spine_refs": _spine_line_refs(chart_spine, spine_lines, target_node_id),
        "activation_hook_refs": _filter_activation_hooks(
            meaning_graph,
            target_node_id=target_node_id,
            spine_lines=spine_lines,
        ),
        "dispositor_route_refs": _filter_structural_refs(
            structural_state.get("dispositor_routes"),
            target_node_id=target_node_id,
            spine_lines=spine_lines,
        ),
        "house_ruler_route_refs": _filter_structural_refs(
            structural_state.get("house_ruler_routes"),
            target_node_id=target_node_id,
            spine_lines=spine_lines,
        ),
        "event_natal_links": _build_event_natal_links(featured_events),
        "life_chapter_bridge": {
            "renderer_handoff": dict(active_chapter.get("renderer_handoff") or {})
            if isinstance(active_chapter.get("renderer_handoff"), Mapping)
            else None,
            "natal_architecture_anchor": dict(active_chapter.get("natal_architecture_anchor") or {})
            if isinstance(active_chapter.get("natal_architecture_anchor"), Mapping)
            else None,
        },
        "suppressed_identity_claims": _list_str(active_chapter.get("suppressed_readings")),
        "debug": {
            "authority_inputs": [
                "canonical_natal_state",
                "core_promises",
                "contradictions",
                "chart_spine",
                "meaning_graph.activation_hooks",
                "structural_state.dispositor_routes",
                "structural_state.house_ruler_routes",
                "featured_events.derived_context",
                "featured_events.natal_promise",
                "active_life_chapter.renderer_handoff",
            ],
            "blocked_authority_inputs": [
                "profile_v8",
                "full_map_v8",
                "personality_imprint",
                "meaning_graph_v1_1",
                "projection_outputs",
            ],
        },
    }


def _clean_domain_token(value: Any) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    match = re.search(r"'domain'\s*:\s*'([^']+)'", text)
    if match:
        return match.group(1).strip() or None
    return text


def _clean_domain_list(values: Any) -> List[str]:
    out: List[str] = []
    for item in values if isinstance(values, list) else []:
        token = _clean_domain_token(item)
        if token and token not in out:
            out.append(token)
    return out


def _safe_voice_hints(semantic_focus_result: Any) -> Dict[str, Any]:
    payload = getattr(semantic_focus_result, "voice_register_hints", None)
    return dict(payload) if isinstance(payload, Mapping) else {}


def _first_nonempty(*values: Any) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def _theme_palette_for_cluster(
    *,
    cluster_kind: str,
    semantic_source: str,
    chapter_type: str | None,
    source_event_ids: List[str],
    featured_events_by_id: Mapping[str, Mapping[str, Any]],
) -> str:
    chapter_token = str(chapter_type or "").strip().lower()
    if cluster_kind in {"speech_authority", "shared_boundary", "direction_line"}:
        if chapter_token == "saturn_return":
            return "saturn_maturation"
        if chapter_token.startswith("nodal"):
            return "node_direction"
    for event_id in source_event_ids:
        event = featured_events_by_id.get(event_id) if isinstance(featured_events_by_id, Mapping) else None
        if not isinstance(event, Mapping):
            continue
        transit_body = str(event.get("transit_body") or "").strip().lower()
        if transit_body == "chiron":
            return "chiron_old_sensitivity"
        if transit_body == "neptune":
            return "neptune_blur_or_sensitivity"
        if transit_body == "pluto":
            return "pluto_depth"
        if transit_body == "mars":
            return "mars_action"
        if transit_body == "venus":
            return "venus_value_closeness"
        if transit_body == "mercury":
            return "mercury_message_mind"
        if transit_body == "jupiter":
            return "jupiter_growth"
        if transit_body == "uranus":
            return "uranus_change"
        if transit_body == "moon":
            return "moon_emotional_rhythm"
        if transit_body == "sun":
            return "sun_visibility"
        if transit_body == "saturn":
            return "saturn_maturation"
        if transit_body == "north node":
            return "node_direction"
    if semantic_source == "life_chapter":
        return "saturn_maturation" if chapter_token == "saturn_return" else "node_direction"
    if cluster_kind in {"inner_safety_identity", "relationship_boundary"}:
        return "neptune_blur_or_sensitivity"
    if cluster_kind == "supportive_opening":
        return "mercury_message_mind"
    return "sun_visibility"


def _domain_palette_for_cluster(
    *,
    cluster_kind: str,
    main_domains: List[str],
    manifestation_context: Mapping[str, Any] | None,
) -> str:
    if cluster_kind == "speech_authority" or cluster_kind == "communication_reflex":
        return "mind_communication_learning"
    if cluster_kind == "shared_boundary":
        return "relationship_intimacy_agreements"
    if cluster_kind == "direction_line":
        return "relationship_intimacy_agreements"
    if cluster_kind == "inner_safety_identity":
        return "home_family_inner_security"
    if cluster_kind == "relationship_boundary":
        return "relationship_intimacy_agreements"
    if cluster_kind == "supportive_opening":
        return "mind_communication_learning"
    context = manifestation_context if isinstance(manifestation_context, Mapping) else {}
    life_scene = str(context.get("life_scene") or "").strip().lower()
    domains = [str(item or "").strip().lower() for item in main_domains]
    if "house_4" in domains or "trust_transformation" in domains or "iç güven" in life_scene or "sana ait" in life_scene:
        return "home_family_inner_security"
    if "communication_learning" in domains or "mental_patterning" in domains or "küçük cümlelerin ağırlığı" in domains or "house_3" in domains:
        return "mind_communication_learning"
    if "relationships" in domains or "relationship" in domains or "self_definition" in domains:
        return "relationship_intimacy_agreements"
    if "identity_presence" in domains or "identity" in domains:
        return "work_career_visibility"
    if "social" in domains:
        return "social_friends_community"
    return "inner_work_solitude_spirituality"


def _narrative_move_for_cluster(cluster_kind: str, theme_palette: str) -> str:
    if cluster_kind == "speech_authority":
        return "communication_reflex"
    if cluster_kind == "shared_boundary":
        return "boundary"
    if cluster_kind == "direction_line":
        return "choice"
    if cluster_kind == "inner_safety_identity":
        return "home_inner_safety"
    if cluster_kind == "relationship_boundary":
        return "relationship_mirror"
    if cluster_kind == "supportive_opening":
        return "support"
    if theme_palette == "neptune_blur_or_sensitivity":
        return "clarification"
    return "integration"


def _cluster_fingerprint(title: str, preview: str, body: str) -> str:
    raw = "|".join([title.strip().lower(), preview.strip().lower(), body.strip().lower()])
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def _normalize_public_card_text(text: str) -> str:
    normalized = tr_normalize(str(text or "").strip())
    normalized = re.sub(r"\b[Ss]emantik\b", "", normalized)
    normalized = re.sub(r"\b[Mm]ekanizma\b", "", normalized)
    normalized = re.sub(r"\b[Pp]roses\b", "", normalized)
    normalized = re.sub(r"\b[Aa]ktivasyon\b", "", normalized)
    normalized = re.sub(r"\b[Gg]eçirgen\b", "hassas", normalized)
    normalized = re.sub(r"\büst anlam\b", "ana çizgi", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bbütünlüklü yön\b", "daha net bir çizgi", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\byön duygusu\b", "yön", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def _preview_body_distinct(preview: str, body: str) -> tuple[str, str]:
    preview_clean = _normalize_public_card_text(preview)
    body_clean = _normalize_public_card_text(body)
    if preview_clean and body_clean.startswith(preview_clean):
        body_clean = body_clean[len(preview_clean) :].lstrip(" .")
    if body_clean == preview_clean:
        body_clean = f"{body_clean} Burada mesele sadece bunu görmek değil; onun sende nasıl yer değiştirdiğini fark etmek."
    return preview_clean, body_clean


def _timing_hint_for_cluster(source_event_ids: List[str], featured_events_by_id: Mapping[str, Mapping[str, Any]]) -> str | None:
    phases: List[str] = []
    for event_id in source_event_ids:
        event = featured_events_by_id.get(event_id) if isinstance(featured_events_by_id, Mapping) else None
        phase = str((event or {}).get("phase") or "").strip().lower() if isinstance(event, Mapping) else ""
        if phase and phase not in phases:
            phases.append(phase)
    if "exact" in phases or "exactish" in phases:
        return "Şu sıralar daha görünür."
    if "applying" in phases:
        return "Yavaş yavaş güç kazanıyor."
    if "separating" in phases:
        return "İlk yoğunluğu geçti ama izi duruyor."
    return None


def _context_used_summary(
    *,
    period_card_context: Mapping[str, Any],
    natal_context: Mapping[str, Any],
    source_event_ids: List[str],
    theme_palette: str,
    domain_palette: str,
    manifestation_scene: str | None,
) -> Dict[str, Any]:
    evidence_by_id = {
        str(item.get("event_id") or "").strip(): dict(item)
        for item in (period_card_context.get("evidence_items") or [])
        if isinstance(item, Mapping) and str(item.get("event_id") or "").strip()
    }
    event_natal_links = {
        str(item.get("event_id") or "").strip(): dict(item)
        for item in (natal_context.get("event_natal_links") or [])
        if isinstance(item, Mapping) and str(item.get("event_id") or "").strip()
    }
    first_spine = next(
        (
            item
            for item in (natal_context.get("chart_spine_refs") or [])
            if isinstance(item, Mapping)
        ),
        None,
    )
    first_route = next(
        (
            item
            for item in [
                *(natal_context.get("dispositor_route_refs") or []),
                *(natal_context.get("house_ruler_route_refs") or []),
            ]
            if isinstance(item, Mapping)
        ),
        None,
    )
    first_promise = next(
        (
            item
            for item in [
                *(natal_context.get("activated_core_promise_ids") or []),
                *(natal_context.get("activated_contradiction_ids") or []),
            ]
            if item
        ),
        None,
    )
    return {
        "semantic_focus": {
            "source": ((period_card_context.get("owner_ref") or {}).get("semantic_focus_source")),
            "selected_meaning": ((period_card_context.get("owner_ref") or {}).get("selected_meaning")),
            "primary_domain": ((period_card_context.get("primary_meaning") or {}).get("primary_domain")),
        },
        "period_owner": {
            "chapter_priority_applied": ((period_card_context.get("source_owner") or {}).get("chapter_priority_applied")),
            "chapter_type": ((period_card_context.get("source_owner") or {}).get("chapter_type")),
            "event_cards_role": ((period_card_context.get("source_owner") or {}).get("event_cards_role")),
        },
        "period_evidence": [
            {
                "event_id": event_id,
                "role": ((evidence_by_id.get(event_id) or {}).get("evidence_role")),
                "domain": ((evidence_by_id.get(event_id) or {}).get("domain")),
                "house_scene": ((evidence_by_id.get(event_id) or {}).get("house_scene")),
            }
            for event_id in source_event_ids
            if event_id in evidence_by_id
        ],
        "natal_context": {
            "event_natal_links": [event_natal_links[event_id] for event_id in source_event_ids if event_id in event_natal_links],
            "activated_core_promise_ids": list(natal_context.get("activated_core_promise_ids") or []),
            "activated_contradiction_ids": list(natal_context.get("activated_contradiction_ids") or []),
        },
        "manifestation_context": manifestation_scene,
        "dispositor_or_ruler_route": dict(first_route) if isinstance(first_route, Mapping) else None,
        "chart_spine": dict(first_spine) if isinstance(first_spine, Mapping) else None,
        "promise_or_contradiction": first_promise,
        "theme_palette": theme_palette,
        "domain_palette": domain_palette,
    }


def _feature_lookup(period_card_context: Mapping[str, Any]) -> Dict[str, Mapping[str, Any]]:
    return {
        str(item.get("event_id") or "").strip(): dict(item)
        for item in (period_card_context.get("evidence_items") or [])
        if isinstance(item, Mapping) and str(item.get("event_id") or "").strip()
    }


def _cluster_source_event_ids(
    featured_events_by_id: Mapping[str, Mapping[str, Any]],
    *,
    predicate,
    fallback_ids: List[str],
    limit: int = 3,
) -> List[str]:
    selected: List[str] = []
    for event_id, event in featured_events_by_id.items():
        if not isinstance(event, Mapping):
            continue
        if predicate(event):
            selected.append(event_id)
            if len(selected) >= limit:
                break
    if not selected:
        return fallback_ids[:limit]
    return selected


def _contains_home_signal(period_card_context: Mapping[str, Any], manifestation_context: Mapping[str, Any] | None) -> bool:
    main_domains = [str(item or "").strip().lower() for item in (period_card_context.get("main_domains") or [])]
    if "house_4" in main_domains:
        return True
    scene = str((manifestation_context or {}).get("life_scene") or "").lower()
    variants = [str(item or "").lower() for item in ((manifestation_context or {}).get("life_scene_variants") or [])]
    return any(token in scene for token in ("sana ait", "ev", "iç güven")) or any(
        any(token in variant for token in ("sana ait", "ev", "iç güven"))
        for variant in variants
    )


def _contains_mind_signal(period_card_context: Mapping[str, Any]) -> bool:
    main_domains = [str(item or "").strip().lower() for item in (period_card_context.get("main_domains") or [])]
    return any(
        token in main_domains
        for token in ("communication_learning", "mental_patterning", "küçük cümlelerin ağırlığı", "house_3")
    )


def _contains_relationship_signal(period_card_context: Mapping[str, Any]) -> bool:
    main_domains = [str(item or "").strip().lower() for item in (period_card_context.get("main_domains") or [])]
    return any(token in main_domains for token in ("relationships", "relationship", "house_7", "self_definition"))


def _theme_cluster_contexts(
    *,
    period_card_context: Mapping[str, Any],
    natal_context: Mapping[str, Any],
    semantic_focus_result: Any,
    active_life_chapter: Mapping[str, Any] | None,
) -> List[Dict[str, Any]]:
    owner_ref = period_card_context.get("owner_ref") if isinstance(period_card_context.get("owner_ref"), Mapping) else {}
    source_owner = period_card_context.get("source_owner") if isinstance(period_card_context.get("source_owner"), Mapping) else {}
    semantic_source = str(owner_ref.get("semantic_focus_source") or "").strip()
    selected_meaning = str(owner_ref.get("selected_meaning") or "").strip()
    manifestation_context = (
        period_card_context.get("manifestation_context")
        if isinstance(period_card_context.get("manifestation_context"), Mapping)
        else {}
    )
    featured_events_by_id = _feature_lookup(period_card_context)
    fallback_ids = list(featured_events_by_id.keys())
    handoff = (
        ((natal_context.get("life_chapter_bridge") or {}).get("renderer_handoff"))
        if isinstance(natal_context.get("life_chapter_bridge"), Mapping)
        else {}
    )
    if not isinstance(handoff, Mapping):
        handoff = {}
    manifestation_scene = _first_nonempty(
        handoff.get("human_scene"),
        manifestation_context.get("human_scene"),
        manifestation_context.get("life_scene"),
    )
    chapter_type = _first_nonempty(source_owner.get("chapter_type"), (active_life_chapter or {}).get("chapter_type"))
    voice_hints = _safe_voice_hints(semantic_focus_result)

    clusters: List[Dict[str, Any]] = []
    if semantic_source == "life_chapter" and selected_meaning == "speech_authority":
        clusters.extend(
            [
                {
                    "kind": "speech_authority",
                    "source_event_ids": fallback_ids[:3],
                    "manifestation_scene": manifestation_scene or "kısa mesajlar ve hızlı cevap verme anları",
                },
                {
                    "kind": "communication_reflex",
                    "source_event_ids": _cluster_source_event_ids(
                        featured_events_by_id,
                        predicate=lambda event: str(event.get("house_scene") or "") == "house_3"
                        or "mind" in _clean_domain_list([(event.get("domain"))]),
                        fallback_ids=fallback_ids,
                    ),
                    "manifestation_scene": manifestation_scene or "yarım kalmış konuşmalar",
                },
                {
                    "kind": "relationship_boundary",
                    "source_event_ids": _cluster_source_event_ids(
                        featured_events_by_id,
                        predicate=lambda event: str(event.get("house_scene") or "") == "house_7"
                        or "relationships" in _clean_domain_list([event.get("domain")]),
                        fallback_ids=fallback_ids[1:] or fallback_ids,
                    ),
                    "manifestation_scene": "yan yana dururken nerede durduğunu söylemek",
                },
            ]
        )
    elif semantic_source == "life_chapter" and selected_meaning == "shared_emotional_territory":
        clusters.extend(
            [
                {
                    "kind": "shared_boundary",
                    "source_event_ids": fallback_ids[:2],
                    "manifestation_scene": manifestation_scene or "mahrem konuşmalar ve paylaşılan yükler",
                },
                {
                    "kind": "relationship_boundary",
                    "source_event_ids": fallback_ids[:2],
                    "manifestation_scene": "ne kadarını taşıyacağını ayırdığın anlar",
                },
                {
                    "kind": "supportive_opening",
                    "source_event_ids": fallback_ids[:1],
                    "manifestation_scene": "güvenin daha açık ama dağılmadan kurulduğu anlar",
                },
            ]
        )
    elif semantic_source == "life_chapter" and selected_meaning == "directional_self_definition":
        clusters.extend(
            [
                {
                    "kind": "direction_line",
                    "source_event_ids": fallback_ids[:2],
                    "manifestation_scene": manifestation_scene or "yan yana dururken yönünü seçtiğin anlar",
                },
                {
                    "kind": "relationship_boundary",
                    "source_event_ids": fallback_ids[:1],
                    "manifestation_scene": "uyumu korurken kendini kısmadığın anlar",
                },
                {
                    "kind": "supportive_opening",
                    "source_event_ids": fallback_ids[:1],
                    "manifestation_scene": "kendi çizginle masada kaldığın anlar",
                },
            ]
        )
    else:
        if _contains_home_signal(period_card_context, manifestation_context):
            clusters.append(
                {
                    "kind": "inner_safety_identity",
                    "source_event_ids": _cluster_source_event_ids(
                        featured_events_by_id,
                        predicate=lambda event: str(event.get("house_scene") or "") in {"house_1", "house_4"},
                        fallback_ids=fallback_ids,
                    ),
                    "manifestation_scene": _first_nonempty(
                        manifestation_context.get("life_scene"),
                        "ev, iç güvenlik ya da yalnız kaldığında kurduğun düzen",
                    ),
                }
            )
        if any(str((featured_events_by_id[event_id] or {}).get("transit_body") or "").lower() == "neptune" for event_id in fallback_ids):
            clusters.append(
                {
                    "kind": "clarity_blur",
                    "source_event_ids": _cluster_source_event_ids(
                        featured_events_by_id,
                        predicate=lambda event: str(event.get("transit_body") or "").strip().lower() == "neptune",
                        fallback_ids=fallback_ids,
                    ),
                    "manifestation_scene": manifestation_scene or "neye net cevap vereceğini seçtiğin anlar",
                }
            )
        if _contains_mind_signal(period_card_context):
            clusters.append(
                {
                    "kind": "communication_reflex",
                    "source_event_ids": _cluster_source_event_ids(
                        featured_events_by_id,
                        predicate=lambda event: str(event.get("house_scene") or "") == "house_3"
                        or "mind" in _clean_domain_list([event.get("domain")]),
                        fallback_ids=fallback_ids,
                    ),
                    "manifestation_scene": _first_nonempty(
                        manifestation_context.get("life_scene"),
                        "küçük cümlelerin ağırlığı",
                    ),
                }
            )
        if _contains_relationship_signal(period_card_context):
            clusters.append(
                {
                    "kind": "relationship_boundary",
                    "source_event_ids": _cluster_source_event_ids(
                        featured_events_by_id,
                        predicate=lambda event: str(event.get("house_scene") or "") == "house_7"
                        or "relationships" in _clean_domain_list([event.get("domain")]),
                        fallback_ids=fallback_ids[1:] or fallback_ids,
                    ),
                    "manifestation_scene": "yakınlıkta kendi cümleni seçtiğin anlar",
                }
            )
        supportive_ids = _cluster_source_event_ids(
            featured_events_by_id,
            predicate=lambda event: str(event.get("aspect") or "").strip().lower() in {"trine", "sextile"}
            and str(event.get("transit_body") or "").strip().lower() in {"north node", "jupiter", "venus", "mercury", "sun", "uranus"},
            fallback_ids=[],
        )
        if supportive_ids:
            clusters.append(
                {
                    "kind": "supportive_opening",
                    "source_event_ids": supportive_ids,
                    "manifestation_scene": _first_nonempty(
                        manifestation_context.get("life_scene"),
                        str(((period_card_context.get("primary_meaning") or {}).get("primary_domain")) or "").strip(),
                        "bir şeyin daha az zorlayarak yerine oturduğu anlar",
                    ),
                }
            )

    out: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for cluster in clusters:
        kind = str(cluster.get("kind") or "").strip()
        source_event_ids = [event_id for event_id in cluster.get("source_event_ids") or [] if event_id]
        if not kind or not source_event_ids:
            continue
        cluster_key = f"{kind}|{'-'.join(source_event_ids)}"
        if cluster_key in seen:
            continue
        seen.add(cluster_key)
        theme_palette = _theme_palette_for_cluster(
            cluster_kind=kind,
            semantic_source=semantic_source,
            chapter_type=chapter_type,
            source_event_ids=source_event_ids,
            featured_events_by_id=featured_events_by_id,
        )
        domain_palette = _domain_palette_for_cluster(
            cluster_kind=kind,
            main_domains=[str(item or "") for item in (period_card_context.get("main_domains") or [])],
            manifestation_context=manifestation_context,
        )
        out.append(
            {
                "kind": kind,
                "source_event_ids": source_event_ids,
                "manifestation_scene": str(cluster.get("manifestation_scene") or "").strip(),
                "theme_palette": theme_palette,
                "domain_palette": domain_palette,
                "narrative_move": _narrative_move_for_cluster(kind, theme_palette),
                "tone": _first_nonempty(str(voice_hints.get("valence_mode") or ""), "maturation" if semantic_source == "life_chapter" else "recognition"),
                "intensity_mode": _first_nonempty(str(voice_hints.get("intensity_mode") or ""), "medium"),
                "core_contrast": _first_nonempty(handoff.get("core_contrast"), manifestation_context.get("shared_vs_private_contrast")),
                "chart_anchor": _first_nonempty(
                    handoff.get("chart_specific_anchor"),
                    (((natal_context.get("life_chapter_bridge") or {}).get("natal_architecture_anchor")) or {}).get("human") if isinstance((natal_context.get("life_chapter_bridge") or {}).get("natal_architecture_anchor"), Mapping) else "",
                ),
            }
        )
    return out[:6]


def _render_cluster_copy(
    *,
    cluster: Mapping[str, Any],
    period_card_context: Mapping[str, Any],
) -> Dict[str, str]:
    kind = str(cluster.get("kind") or "").strip()
    scene = str(cluster.get("manifestation_scene") or "").strip()
    core_contrast = str(cluster.get("core_contrast") or "").strip()
    chart_anchor = str(cluster.get("chart_anchor") or "").strip()
    primary_domain = str(((period_card_context.get("primary_meaning") or {}).get("primary_domain")) or "").strip()
    theme_palette = str(cluster.get("theme_palette") or "").strip()
    domain_palette = str(cluster.get("domain_palette") or "").strip()
    source_event_ids = [str(event_id or "").strip() for event_id in (cluster.get("source_event_ids") or []) if str(event_id or "").strip()]
    selected_meaning = str(((period_card_context.get("owner_ref") or {}).get("selected_meaning")) or "").strip()
    chapter_type = str(((period_card_context.get("source_owner") or {}).get("chapter_type")) or "").strip()

    if kind == "speech_authority":
        return {
            "title": "Sözün yerini buluyor",
            "preview": "Kelimelerin artık daha seçilmiş bir yere oturuyor. Hızlıca verilen cevaplar eskisi kadar rahat taşınmıyor.",
            "body": (
                "Bir mesajı göndermeden önce kelimeleri tarttığın o küçük duraksama var ya; tam orada bir şey değişiyor. "
                "Eskiden hızlı cevap vermek seni koruyor gibi görünmüş olabilir. "
                "Şimdi cümle hızlı çıktığında değil, gerçekten sana ait olduğunda ağırlık kazanıyor. "
                "Sadece konuşmuyor, sözünle oraya bir imza bırakıyorsun."
            ),
        }
    if kind == "communication_reflex":
        return {
            "title": "İlk cümle yetmiyor",
            "preview": "Boşluğu hemen dolduran cevap, içerideki gerçek yerini tam taşımıyor. Biraz durduğunda ne söylemek istediğin daha net çıkıyor.",
            "body": (
                "Yarım kalmış konuşmalar ya da kısa mesajlar bu ara sandığından fazla iz bırakıyor. "
                "İlk tepkinle son sözünün aynı olmadığını daha çabuk fark ediyorsun. "
                "Özellikle küçük cümlelerin ağırlığı artarken, aceleyle kurduğun ton bütün hikâyenin yerine geçebiliyor. "
                "Bir nefeslik duraksama burada zayıflık değil; cümleni gerçekten seçtiğin yer."
            ),
        }
    if kind == "relationship_boundary":
        return {
            "title": "Yakınlıkta çizgin beliriyor",
            "preview": "Yan yana dururken kendi cümleni fazla kısmadan da kalabildiğin anlar çoğalıyor. İlişki burada sadece uyumla yürümüyor.",
            "body": (
                "Karşı tarafı kollarken kendi yerini sessizce geri çektiğin anlar daha görünür. "
                "Burada mesele sertleşmek değil; ne hissettiğini fazla dolandırmadan söyleyebilmek. "
                "Sıcak kalırken çizgini de koruduğunda, yakınlık savunmaya değil açıklığa yaslanıyor. "
                "Bu da ilişkide seni silmeden kalmanın başka bir yolunu açıyor."
            ),
        }
    if kind == "shared_boundary":
        return {
            "title": "Neyin sana ait olduğu",
            "preview": "Paylaşılan yük ile tek başına taşıdığın şey aynı yerde durmuyor. Bunu ayırdıkça yakınlık daha sağlam bir zemine oturuyor.",
            "body": (
                "Mahrem konuşmaların ya da birlikte taşınan yüklerin içinde, sessizce üstlendiğin şey daha görünür. "
                "Güveni sadece susarak değil, neyi taşıyacağını ve neyi geri vereceğini söyleyerek de kurabiliyorsun. "
                "Burada fazlalığı atmak değil, paylaşılanı daha doğru ölçüyle taşımak var. "
                "Sınırın netleştikçe yakınlık da daha dayanıklı bir forma yerleşiyor."
            ),
        }
    if kind == "direction_line":
        return {
            "title": "Yönünü daha açık söylüyorsun",
            "preview": "İlişkiyi korumak için kendi yönünü kısmak eskisi kadar kolay gelmiyor. Sözün biraz daha doğrudanlaşıyor.",
            "body": (
                "Yan yana dururken kendini ne kadar çabuk ayarladığını daha net görüyorsun. "
                "Burada kopmak ya da sertleşmek değil, kendi çizgini saklamadan söylemek öne çıkıyor. "
                "Onayın içinde erimeden de masada kalabildiğinde, yönün sadece içeride değil dışarıda da belirginleşiyor. "
                "Bu da seni ilişkiyi korurken kendini silmeyen bir çizgiye taşıyor."
            ),
        }
    if kind == "inner_safety_identity":
        return {
            "title": "İçeride olan dışarıya taşıyor",
            "preview": "Sana ait hissettiren alan, dışarıda nasıl durduğunu daha doğrudan etkiliyor. Evde ya da yalnız kaldığında tuttuğun ritim gizli kalmıyor.",
            "body": (
                "İç güvenlik ya da yalnız kaldığında kurduğun düzen şu ara arka plan gibi durmuyor. "
                "İçeride taşıdığın duygu, dışarıdaki yüzüne ve sınırına daha çabuk yansıyor. "
                "Bu yüzden meseleyi sadece dışarıdaki duruşta çözmeye çalışmak yetmiyor. "
                "Ne kadarını gerçekten kendin için tuttuğunu ayırdığında, kimliğin de daha sakin bir yerden yerleşiyor."
            ),
        }
    if kind == "clarity_blur":
        return {
            "title": "Netlik aceleye gelmiyor",
            "preview": "Her boşluğu hemen cevapla kapatma isteği artıyor. Ama bu kez hızlı netlik değil, doğru ayıklama daha çok şey söylüyor.",
            "body": (
                "Bazı anlarda neye net cevap vereceğini seçmek zorlaşıyor. "
                "Zihin boşluğu hızla doldurmak istese de, ilk cümle bazen sadece tedirginliği taşıyor. "
                "Burada bulanıklığı düşman gibi görmek yerine, hangi parçanın gerçekten sana ait olduğunu ayırmak önemli. "
                "Netliğin geç gelmesi, yanlış bir cevaba erkenden tutunmaktan daha dürüst olabiliyor."
            ),
        }
    if kind == "supportive_opening":
        if chapter_type == "saturn_return" and selected_meaning == "shared_emotional_territory":
            return {
                "title": "Güven daha açık kuruluyor",
                "preview": "Mahrem olanı korurken her şeyi sessizce taşımak gerekmiyor. Paylaşılan yük adını buldukça yakınlık daha sakin akıyor.",
                "body": (
                    "Bazı şeyleri tek başına sırtlanmak seni güvende tutmuş olabilir. "
                    "Şimdi paylaşılan yükü, mahrem olanı dağıtmadan da konuşabildiğin bir yer açılıyor. "
                    "Kısa bir açıklık, neyin sana ait neyin ortak olduğunu daha rahat ayırıyor. "
                    "Yakınlık burada büyük bir itirafla değil, güveni daha açık kurabildiğin küçük anlarla güçleniyor."
                ),
            }
        if selected_meaning == "directional_self_definition":
            return {
                "title": "Kendini kısmadan kalıyorsun",
                "preview": "Onay aramadan da sıcak kalabildiğin anlar çoğalıyor. Aynı masada dururken yönün daha az geri çekiliyor.",
                "body": (
                    "Bazen ilişkiyi korumak için cümleni hemen yumuşatmak kolay geliyor. "
                    "Şimdi aynı masada kalırken kendi çizgini de bırakmıyorsun. "
                    "Küçük bir netlik, onay beklemeden de sıcaklığın bozulmadığını gösteriyor. "
                    "Yönünü saklamadığında ilişki sertleşmiyor; sadece seni daha doğru yerden görüyor."
                ),
            }
        if domain_palette == "home_family_inner_security":
            return {
                "title": "Küçük bir netlik yetiyor",
                "preview": "İç güvenlik ile dışarıdaki duruş aynı anda gevşiyor. Bazen tek bir cümle ya da kısa bir mesaj, gereğinden fazla yükü indiriyor.",
                "body": (
                    "Her şeyi bir anda çözmek gerekmiyor. "
                    "Bazen evde taşıdığın duyguyu adını koyacak kadar netleştirmek, dışarıdaki duruşunu da rahatlatıyor. "
                    "Kısa bir mesaj ya da sade bir cümle, içeride büyüyen şeyi fazla zorlamadan yerine oturtabiliyor. "
                    "Bu küçük netlik, hem sözünü hem sınırını daha az kasılarak taşımanı sağlıyor."
                ),
            }
        if "yakın çevrendeki ses" in scene or "yakın çevrendeki ses" in primary_domain.lower():
            return {
                "title": "Bir cümle daha sade çıkıyor",
                "preview": "Söylemek istediğin şey bazen fazla uzamadan yerini buluyor. Mesajı taşımak için artık o kadar çok cümle gerekmiyor.",
                "body": (
                    "Bazı konuşmalarda doğru kelime beklediğinden daha çabuk beliriyor. "
                    "Boşluğu uzun açıklamalarla kapatmak yerine, tek bir cümle daha sade çıkıyor. "
                    "Bu sadeleşme seni eksiltmiyor; ne demek istediğini daha net duyuruyor. "
                    "Yakın çevrende ya da mesajlarda, az zorlanan söz bazen en güçlü duruşu taşıyor."
                ),
            }
        if "küçük cümlelerin ağırlığı" in scene or "küçük cümlelerin ağırlığı" in primary_domain.lower():
            return {
                "title": "Sözün daha az zorlanıyor",
                "preview": "Küçük cümlelerin yükü biraz hafifliyor. Aynı şeyi söylemek için artık o kadar sert bir ton gerekmiyor.",
                "body": (
                    "Bazen kısa bir mesaj ya da tek bir cevap, düşündüğünden daha temiz bir yere oturuyor. "
                    "Kelimeleri fazla sıkıştırmadığında, ne demek istediğin daha rahat anlaşılıyor. "
                    "Bu yumuşama seni belirsiz bırakmıyor; tam tersine sözünü daha net taşıyor. "
                    "Yakın çevrende, az zorlanan cümle bu kez daha uzun bir yankı bırakıyor."
                ),
            }
        if domain_palette == "mind_communication_learning" or "mind" in primary_domain.lower() or source_event_ids:
            return {
                "title": "Küçük bir netlik yetiyor",
                "preview": "Söylemek istediğin şey bazen fazla büyümeden yerini buluyor. Az cümleyle gelen netlik daha çok şey taşıyor.",
                "body": (
                    "Her şeyi uzun uzun anlatmak gerekmiyor. "
                    "Bazen küçük bir netlik, içinde tuttuğun şeyi daha düzgün taşıyor. "
                    "Cümle kısaldığında ne demek istediğin kaybolmuyor; tam tersine daha seçilmiş bir duruş kazanıyor. "
                    "Bu da sözünü zorlama olmadan yerleştiren sakin bir destek veriyor."
                ),
            }
        return {
            "title": "Sıcaklık daha rahat akıyor",
            "preview": "Kendini fazla zorlamadan da açık kalabildiğin anlar çoğalıyor. Küçük bir yumuşama, bütün tonu değiştiriyor.",
            "body": (
                "Her şey büyük bir konuşma istemiyor. "
                "Bazen sade bir bakış ya da kısa bir cümle yeterince şey taşıyor. "
                "Kendini fazla zorlamadığında, açık olan tarafın daha doğal görünüyor. "
                "Bu da desteğin gösterişli değil, gerçek bir yerden gelmesini sağlıyor."
            ),
        }
    return {
        "title": "Bir çizgi belirginleşiyor",
        "preview": f"{scene or primary_domain or 'Bu hat'} artık daha görünür. Burada küçük görünen şey, alttaki ana hareketi açıyor.",
        "body": (
            f"{scene or 'Bu alan'} artık sadece arka planda kalmıyor. "
            f"{core_contrast or 'İçeride olanla dışarıda taşıdığın şey aynı yerde toplanmak istiyor.'} "
            f"{chart_anchor or 'Daha seçilmiş bir çizgi kurdukça bu tema sende daha sağlam yerleşiyor.'}"
        ),
    }


def _blocked_source_check() -> Dict[str, bool]:
    return {
        "used_old_blocks": False,
        "used_daily_body": False,
        "used_best_times_score": False,
        "used_story_tracks_as_owner": False,
        "used_event_story_map_as_owner": False,
        "used_profile_v8_as_authority": False,
        "used_personality_imprint_as_authority": False,
        "used_meaning_graph_v1_1_as_authority": False,
    }


def _public_copy_has_technical_leakage(*parts: str) -> bool:
    joined = " ".join(str(part or "") for part in parts)
    patterns = (
        r"\b(satürn|saturn|neptün|neptune|plüton|pluto|uranüs|uranus|kiron|chiron|güneş|sun|merkür|mercury|venüs|venus|mars|jüpiter|jupiter)\b",
        r"\b(kare|square|sextile|sextil|üçgen|trine|conjunction|kavuşum|opposition|karşıt)\b",
        r"\b\d+\.\s*ev\b",
        r"\borb\b",
    )
    return any(re.search(pattern, joined, flags=re.IGNORECASE) for pattern in patterns)


def _build_period_signal_lines_v1(
    *,
    period_card_context: Mapping[str, Any],
    natal_context: Mapping[str, Any],
    semantic_focus_result: Any,
    active_life_chapter: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    owner_ref = period_card_context.get("owner_ref") if isinstance(period_card_context.get("owner_ref"), Mapping) else {}
    source_owner = period_card_context.get("source_owner") if isinstance(period_card_context.get("source_owner"), Mapping) else {}
    clusters = _theme_cluster_contexts(
        period_card_context=period_card_context,
        natal_context=natal_context,
        semantic_focus_result=semantic_focus_result,
        active_life_chapter=active_life_chapter,
    )
    cards: List[Dict[str, Any]] = []
    dropped_candidates: List[Dict[str, Any]] = []
    dedupe_fingerprints: List[str] = []
    seen_fingerprints: set[str] = set()
    featured_events_by_id = _feature_lookup(period_card_context)
    suppressed = [str(item or "").strip().lower() for item in (period_card_context.get("suppressed_meanings") or [])]

    for cluster in clusters:
        copy = _render_cluster_copy(cluster=cluster, period_card_context=period_card_context)
        title = _normalize_public_card_text(copy.get("title", ""))
        preview = _normalize_public_card_text(copy.get("preview", ""))
        body = _normalize_public_card_text(copy.get("body", ""))
        preview, body = _preview_body_distinct(preview, body)
        fingerprint = _cluster_fingerprint(title, preview, body)
        reasons: List[str] = []
        if fingerprint in seen_fingerprints:
            reasons.append("duplicate_fingerprint")
        if _public_copy_has_technical_leakage(title, preview, body):
            reasons.append("technical_leakage")
        lowered = f"{title} {preview} {body}".lower()
        if any(token and token in lowered for token in suppressed):
            reasons.append("suppressed_meaning_conflict")
        if preview and body and preview == body:
            reasons.append("body_repeats_preview")
        if reasons:
            dropped_candidates.append({"kind": cluster.get("kind"), "reasons": reasons})
            continue
        seen_fingerprints.add(fingerprint)
        dedupe_fingerprints.append(fingerprint)
        source_event_ids = [event_id for event_id in cluster.get("source_event_ids") or [] if event_id]
        theme_palette = str(cluster.get("theme_palette") or "").strip()
        domain_palette = str(cluster.get("domain_palette") or "").strip()
        narrative_move = str(cluster.get("narrative_move") or "").strip()
        manifestation_scene = str(cluster.get("manifestation_scene") or "").strip() or None
        card_id_seed = "|".join([str(cluster.get("kind") or ""), *source_event_ids, fingerprint])
        card_id = f"psl_{hashlib.sha1(card_id_seed.encode('utf-8')).hexdigest()[:10]}"
        cards.append(
            {
                "id": card_id,
                "rank": len(cards) + 1,
                "title": title,
                "preview": preview,
                "body": body,
                "tone": str(cluster.get("tone") or "").strip() or "recognition",
                "theme_palette": theme_palette,
                "domain_palette": domain_palette,
                "narrative_move": narrative_move,
                "timing_hint": _timing_hint_for_cluster(source_event_ids, featured_events_by_id),
                "evidence_refs": [
                    {
                        "event_id": event_id,
                        "role": ((featured_events_by_id.get(event_id) or {}).get("evidence_role")),
                        "domain": ((featured_events_by_id.get(event_id) or {}).get("domain")),
                        "house_scene": ((featured_events_by_id.get(event_id) or {}).get("house_scene")),
                    }
                    for event_id in source_event_ids
                    if event_id in featured_events_by_id
                ],
                "source_event_ids": source_event_ids,
                "linked_to_period_reading": True,
                "context_used": _context_used_summary(
                    period_card_context=period_card_context,
                    natal_context=natal_context,
                    source_event_ids=source_event_ids,
                    theme_palette=theme_palette,
                    domain_palette=domain_palette,
                    manifestation_scene=manifestation_scene,
                ),
                "debug": {
                    "cluster_kind": str(cluster.get("kind") or ""),
                    "semantic_owner": owner_ref.get("semantic_focus_source"),
                    "chapter_type": source_owner.get("chapter_type"),
                    "fingerprint": fingerprint,
                    "intensity_mode": str(cluster.get("intensity_mode") or ""),
                },
            }
        )

    return {
        "version": "period_signal_lines_v1",
        "source_owner": _first_nonempty(owner_ref.get("semantic_focus_source"), source_owner.get("chapter_type")),
        "primary_meaning": _first_nonempty(owner_ref.get("selected_meaning"), ((period_card_context.get("primary_meaning") or {}).get("label"))),
        "cards": cards[:8],
        "debug": {
            "selection_reason": [
                "semantic_focus_owner_first",
                "theme_cluster_contexts",
                "natal_context_projection",
                "no_second_meaning_engine",
            ],
            "dropped_candidates": dropped_candidates,
            "dedupe_fingerprints": dedupe_fingerprints,
            "blocked_source_check": _blocked_source_check(),
        },
    }


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
    timing = event.get("timing") if isinstance(event.get("timing"), Mapping) else {}

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
        "transit_body": str(event.get("transit_body") or ""),
        "natal_point": str(event.get("natal_point") or ""),
        "aspect": str(event.get("aspect") or ""),
        "phase": str(event.get("phase") or ""),
        "bucket": str(event.get("bucket") or ""),
        "orb_deg": event.get("orb_deg"),
        "houses": dict(houses),
        "timing": dict(timing),
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
    out = rewrite_event_card_tr(out, event=event, horizon=horizon)

    # Deterministic title/signature/teaser are set after quality layer to avoid drift.
    out["horizon"] = horizon
    out["title"] = str(out.get("headline") or out.get("title") or "").strip() or _deterministic_title(event, fallback="Aktif Transit")
    out["headline"] = str(out.get("headline") or out.get("title") or "").strip()
    resolved_time_hint = str(out.get("time_hint_tr") or out.get("time_hint") or time_hint or "").strip()
    out["signature"] = _signature(event, time_hint=resolved_time_hint)
    out["signature_tr"] = _signature_tr(event, time_hint=resolved_time_hint)
    out["signature"] = out["signature_tr"]
    out["time_hint_tr"] = resolved_time_hint
    out["narrative_provenance"] = {
        "headline_source": "event.headline",
        "opening_source": "event.opening",
        "essence_source": "event.essence",
        "mechanism_source": "event.mechanism",
        "asks_source": "event.asks",
        "watchout_source": "event.watchout",
        "what_it_builds_source": "event.what_it_builds",
        "technical_note_source": "event.technical_note",
        "story_track_id": str(out.get("story_track_id") or ""),
        "period_track_used": False,
        "fallback_keys_used": [],
    }
    if horizon == "period":
        out = rewrite_period_card_tr(out, event=event)
    return out


def build_period_core(
    report: Mapping[str, Any],
    event_cards: List[Mapping[str, Any]] | None = None,
    locale: str = "tr",
    canonical_period_spine: Mapping[str, Any] | None = None,
    active_life_chapter: Mapping[str, Any] | None = None,
    canonical_natal_state: Mapping[str, Any] | None = None,
    include_adaptive_card_contexts: bool = False,
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
            for key in ("chapter_role", "story_score", "selection_index", "selection_mode"):
                if key in card_ctx:
                    merged[key] = card_ctx.get(key)
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
        event_source = item_by_id.get(event_id) if event_id else None
        story_source = dict(event_source) if isinstance(event_source, Mapping) else {}
        story_source.update(card)
        track_id = infer_story_track_id(story_source, root_causes)
        card["story_track_id"] = track_id
        event_story_map[event_id] = track_id
        if track_id not in story_tracks:
            story_tracks[track_id] = build_story_track_copy(track_id, story_source)
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
        "canonical_period_spine": dict(canonical_period_spine or {}),
    }
    policy_seed = build_period_voice_policy(
        canonical_period_spine=dict(canonical_period_spine or {}),
        matched_events=selected_enriched,
        chapter_role=(
            str(
                (
                    (selected_enriched[0].get("chapter_role") or {})
                    if isinstance(selected_enriched[0].get("chapter_role"), Mapping)
                    else {}
                ).get("role")
                or ""
            ).strip().lower()
            if selected_enriched
            else None
        ),
        canonical_backing_node_ids=[],
        semantic_focus_result=None,
    )
    manifestation_context = (
        dict(policy_seed.get("manifestation_context") or {})
        if isinstance(policy_seed.get("manifestation_context"), Mapping)
        else None
    )
    semantic_focus_result = resolve_period_semantic_focus(
        canonical_period_spine=dict(canonical_period_spine or {}),
        active_life_chapter=active_life_chapter,
        period_voice_policy=policy_seed,
        manifestation_context=manifestation_context,
        selected_events=selected_enriched,
        period_core_seed=result,
        canonical_natal_state=canonical_natal_state,
        debug=True,
    )
    result["semantic_focus"] = semantic_focus_result.to_debug_dict(include_evidence=False)
    chapter_priority = _build_chapter_priority_debug(
        active_life_chapter=active_life_chapter,
        semantic_focus_result=semantic_focus_result,
        flag_enabled=bool(settings.life_chapter_priority_enabled),
    )
    result["chapter_priority"] = chapter_priority
    if chapter_priority.get("applied"):
        for item in selected_enriched:
            if not isinstance(item, dict):
                continue
            item["semantic_role"] = "evidence_support"
            item["semantic_owner"] = "life_chapter"

    try:
        narr = build_period_story(
            PeriodStoryContext(
                period_core=result,
                chart_snapshot=report.get("natal") if isinstance(report.get("natal"), Mapping) else {},
                natal_promise={"themes": promise_themes},
                canonical_period_spine=dict(canonical_period_spine or {}),
                active_life_chapter=active_life_chapter,
                semantic_focus_result=semantic_focus_result,
                locale=locale,
                enable_fun=True,
            )
        )
        if narr.big_picture:
            result["big_picture"] = narr.big_picture
        if isinstance(narr.period_reading_v1, Mapping) and narr.period_reading_v1:
            result["period_reading_v1"] = dict(narr.period_reading_v1)
        if narr.period_opening:
            result["period_opening"] = narr.period_opening
        if narr.mechanism:
            result["mechanism"] = narr.mechanism
        if narr.growth_edge:
            result["growth_edge"] = narr.growth_edge
        if narr.relational_or_life_expression:
            result["relational_or_life_expression"] = narr.relational_or_life_expression
        if narr.what_it_builds:
            result["what_it_builds"] = narr.what_it_builds
        if narr.upper_meaning:
            result["upper_meaning"] = narr.upper_meaning
        result["core_story"] = (
            str((narr.period_reading_v1 or {}).get("full_text") or "").strip()
            or "\n\n".join(
                part
                for part in (
                    narr.period_opening,
                    narr.big_picture,
                    narr.relational_or_life_expression,
                )
                if str(part).strip()
            )
            or result["core_story"]
        )
        result["narrative_version"] = "period_story_v2"
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

    story_debug = result.get("_period_story_debug") if isinstance(result.get("_period_story_debug"), Mapping) else {}
    composer_plan = story_debug.get("composer_plan") if isinstance(story_debug.get("composer_plan"), Mapping) else {}
    period_card_context = _build_period_card_context(
        semantic_focus_result=semantic_focus_result,
        chapter_priority=chapter_priority,
        canonical_period_spine=dict(canonical_period_spine or {}),
        featured_events=selected_enriched,
        period_reading_v1=result.get("period_reading_v1") if isinstance(result.get("period_reading_v1"), Mapping) else {},
        composer_plan=composer_plan,
        manifestation_context=manifestation_context,
    )
    natal_context_for_period_cards = _build_natal_context_for_period_cards(
        canonical_natal_state=dict(canonical_natal_state or {}) if isinstance(canonical_natal_state, Mapping) else None,
        semantic_focus_result=semantic_focus_result,
        canonical_period_spine=dict(canonical_period_spine or {}),
        featured_events=selected_enriched,
        active_life_chapter=active_life_chapter,
    )
    result["period_signal_lines_v1"] = _build_period_signal_lines_v1(
        period_card_context=period_card_context,
        natal_context=natal_context_for_period_cards,
        semantic_focus_result=semantic_focus_result,
        active_life_chapter=active_life_chapter,
    )

    if include_adaptive_card_contexts:
        adaptive_cards_context = {
            "period_card_context": period_card_context,
            "natal_context_for_period_cards": natal_context_for_period_cards,
        }
        adaptive_cards_context["debug"] = {
            "visibility": "artifact_test_only",
            "public_exposed": False,
            "single_emission_point": "build_period_core",
            "natal_activation_context_present_at_build_time": False,
        }
        result["_adaptive_cards_context"] = adaptive_cards_context
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
    selected, selection_meta = select_event_ids(typed_items, max_cards=max_cards, natal=report.get("natal") if isinstance(report, Mapping) else None)
    context = {"natal": report.get("natal")} if isinstance(report, Mapping) else {}
    cards: List[Dict[str, Any]] = []
    story_scores = selection_meta.get("story_scores") if isinstance(selection_meta.get("story_scores"), Mapping) else {}
    chapter_roles = selection_meta.get("chapter_roles") if isinstance(selection_meta.get("chapter_roles"), Mapping) else {}
    selection_mode = str(selection_meta.get("selection_mode") or "").strip()
    for index, event in enumerate(selected[:max_cards]):
        event_id = str(event.get("event_id") or "").strip()
        card = build_event_card(event, context=context)
        if event_id:
            card["story_score"] = story_scores.get(event_id)
            card["chapter_role"] = dict(chapter_roles.get(event_id) or {})
        card["selection_index"] = index
        card["selection_mode"] = selection_mode
        cards.append(card)
    cards = _inject_cofeatured_links(cards, selected)
    cards = _apply_global_guidance_diversity(cards, selected)
    return _ensure_unique_titles(cards, selected)


def _title_key(value: str) -> str:
    return re.sub(r"[\W_]+", "", str(value or "").lower()).strip()


def _ensure_unique_titles(
    cards: List[Dict[str, Any]],
    selected_events: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    used: set[str] = set()
    event_by_id = {
        str(event.get("event_id") or ""): event
        for event in selected_events
        if isinstance(event, Mapping) and str(event.get("event_id") or "").strip()
    }
    out: List[Dict[str, Any]] = []

    for index, raw_card in enumerate(cards):
        card = dict(raw_card)
        title = str(card.get("title") or "").strip()
        key = _title_key(title)
        if key and key not in used:
            used.add(key)
            out.append(card)
            continue

        event = event_by_id.get(str(card.get("event_id") or "").strip()) or {}
        replacement = ""
        for candidate in _title_pool_for_event(event):
            candidate_key = _title_key(candidate)
            if candidate_key and candidate_key not in used:
                replacement = str(candidate).strip()
                break

        if not replacement:
            target = _point_label_tr(str(event.get("natal_point") or "")).strip()
            if title and target:
                replacement = f"{title.rstrip('.')} / {target}"
            elif title:
                replacement = f"{title.rstrip('.')} {index + 1}"
            else:
                replacement = f"Aktif Transit {index + 1}"

        if replacement and replacement[-1] not in ".!?":
            replacement = f"{replacement}."
        card["title"] = replacement
        used.add(_title_key(replacement))
        out.append(card)

    return out


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
        if not existing_watch:
            existing_watch = _watch_bullets_from_text(str(card_out.get("watchout") or ""), limit=2)

        house_pool = HOUSE_GUIDANCE_POOL_TR.get(house, [])
        _append_from_rotated_pool(guidance, house_pool, seen_guidance, seed=seed, cap=1)
        _append_from_rotated_pool(guidance, TONE_GUIDANCE_POOL_TR.get(tone, []), seen_guidance, seed=seed + 11, cap=2)
        _append_from_rotated_pool(guidance, MECHANISM_GUIDANCE_TR.get(disp, []), seen_guidance, seed=seed + 23, cap=3)
        _append_from_rotated_pool(guidance, existing_guidance, seen_guidance, seed=seed + 37, cap=3)
        _append_from_rotated_pool(guidance, FALLBACK_GUIDANCE_TR, seen_guidance, seed=seed + 41, cap=3)
        if len(guidance) < 2:
            _append_from_rotated_pool(guidance, FALLBACK_GUIDANCE_TR, seen_guidance, seed=seed + 47, cap=2, ignore_seen=True)
        card_out["guidance"] = guidance[:3]

        if existing_watch:
            _append_from_rotated_pool(watch_out, existing_watch, seen_watch, seed=seed + 13, cap=2)
        else:
            _append_from_rotated_pool(watch_out, TONE_WATCH_POOL_TR.get(tone, []), seen_watch, seed=seed + 3, cap=2)
            if not watch_out:
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


def _watch_bullets_from_text(text: str, *, limit: int = 2) -> List[str]:
    raw = str(text or "").replace("!", ".").replace("?", ".")
    parts = [part.strip() for part in raw.split(".") if part.strip()]
    out: List[str] = []
    for part in parts:
        sentence = part if part.endswith(".") else f"{part}."
        if sentence not in out:
            out.append(sentence)
        if len(out) >= limit:
            break
    return out


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
