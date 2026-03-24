from __future__ import annotations

from typing import Any, Dict, List, Mapping

from app.natal.narrative.phrase_lib_tr_natal import pick_variant
from app.natal.natal_graph import TRADITIONAL_RULERS
from app.natal.supporting_threads_builder import PLANET_LABEL_TR, SIGN_LABEL_TR

CORE_HEADLINES = [
    "Kimliğin netleştikçe yönün açılıyor",
    "Netlik kurduğunda gücün daha görünür oluyor",
    "Ritmini koruduğunda yön duygun güçleniyor",
]


def _clamp_chars(text: str, limit: int) -> str:
    value = " ".join(str(text or "").split()).strip()
    if len(value) <= limit:
        return value
    cut = value[:limit]
    dot = cut.rfind(".")
    if dot > int(limit * 0.7):
        return cut[: dot + 1].strip()
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return f"{cut.strip()}…"


def _stable_seed(chart_data: Mapping[str, Any]) -> str:
    birth_dt = str(chart_data.get("birth_datetime") or chart_data.get("birthDateTime") or "").strip()
    loc = chart_data.get("location") if isinstance(chart_data.get("location"), Mapping) else {}
    city = str(loc.get("city") or "").strip()
    angles = chart_data.get("angles") if isinstance(chart_data.get("angles"), Mapping) else {}
    asc_sign = str(angles.get("ascendant_sign") or "").strip()
    mc_sign = str(angles.get("midheaven_sign") or "").strip()
    return f"{birth_dt}|{city}|{asc_sign}|{mc_sign}"


def _planet_map(planets: List[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for item in planets:
        if not isinstance(item, Mapping):
            continue
        name = str(item.get("planet") or "").strip()
        if name:
            out[name] = dict(item)
    return out


def _get_ruler(sign: str) -> str:
    return TRADITIONAL_RULERS.get(str(sign or "").strip().lower(), "")


def _to_house(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _sign_label(sign: str) -> str:
    return SIGN_LABEL_TR.get(str(sign or "").strip(), str(sign or "").strip())


def _planet_label(planet: str) -> str:
    return PLANET_LABEL_TR.get(str(planet or "").strip(), str(planet or "").strip())


def _build_core_text(asc_sign: str, asc_ruler: str, asc_ruler_house: int) -> str:
    sign_label = _sign_label(asc_sign)
    ruler_label = _planet_label(asc_ruler)
    if asc_ruler_house in {3, 6}:
        return (
            f"Netlik sende kontrol değil güven meselesi; Yükselen {sign_label} belirsizliği uzatmayı sevmez "
            f"ve yöneticin {ruler_label}'ün {asc_ruler_house}. ev vurgusu bunu en çok söz, karar ve ton "
            "üzerinden görünür kılar, bu yüzden bazen bir cümleyi kurmadan önce içinden ölçüp biçmen ya da "
            "konuşma bittikten sonra ne demek istediğini zihninde yeniden toplaman aslında fazla düşünmekten "
            "çok netlik aradığını gösterir."
        )
    if asc_ruler_house == 12:
        return (
            f"Netlik sende kontrol değil güven meselesi; Yükselen {sign_label} dışarıda ölçülü bir duruş verirken "
            f"yöneticin {ruler_label}'ün {asc_ruler_house}. ev vurgusu kararlarını önce içeride olgunlaştırmana neden "
            "olur, bu yüzden hızlı cevap vermek yerine geri çekilip toparlanman kaçınma değil, iç kalite "
            "standardını koruma biçimidir."
        )
    if asc_ruler_house == 11:
        return (
            f"Netlik sende yalnız kalınca değil, bağlam netleşince geliyor; Yükselen {sign_label} belirsizliği "
            f"uzatmayı sevmez ve yöneticin {ruler_label}'ün {asc_ruler_house}. ev vurgusu bunu en çok ekip, "
            "çevre ve ortak hedefler içinde görünür kılar, bu yüzden rolün ve yönün net olduğunda hem zihnin "
            "hem motivasyonun aynı anda toparlanır."
        )
    return (
        f"Netlik sende kontrol değil güven meselesi; Yükselen {sign_label} belirsizliği uzatmayı sevmez ve "
        f"yöneticin {ruler_label}'ün {asc_ruler_house}. ev vurgusu bunu en çok günlük kararların ve duruşun "
        "üzerinden görünür kılar, bu yüzden bir şeyi içinden tartıp sağlam bir cümleye dönüştürdüğünde hem "
        "ritmin hem yön duygun birlikte güçlenir."
    )


def build_core_story_ui(
    *,
    chart_data: Mapping[str, Any],
    planets: List[Mapping[str, Any]],
    natal_graph: Mapping[str, Any],
) -> Dict[str, Any]:
    del natal_graph
    seed = _stable_seed(chart_data)
    angles = chart_data.get("angles") if isinstance(chart_data.get("angles"), Mapping) else {}
    asc_sign = str(angles.get("ascendant_sign") or "").strip()
    asc_ruler = _get_ruler(asc_sign)
    pmap = _planet_map(planets)
    asc_ruler_house = _to_house((pmap.get(asc_ruler) or {}).get("house"), 1)

    headline = CORE_HEADLINES[pick_variant(f"{seed}:core_story_ui", len(CORE_HEADLINES))]
    text = _clamp_chars(_build_core_text(asc_sign, asc_ruler, asc_ruler_house), 520)
    return {
        "headline": headline,
        "text": text,
        "drivers": [
            {"type": "angle", "key": "ASC", "value": asc_sign},
            {"type": "ruler", "key": "asc_ruler", "value": asc_ruler},
            {"type": "house", "key": "asc_ruler_house", "value": asc_ruler_house},
        ],
    }
