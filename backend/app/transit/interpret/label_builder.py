from __future__ import annotations

from dataclasses import replace
from typing import Dict, Optional

from .dicts import ASPECT_SYMBOL, AXIS_THEME, HOUSE_THEME_UI
from .event_models import EventLabel, EventMeta, EventObj, LabelFull
from .normalize import canonical_obj_key, norm_aspect

PLANET_MEANING: Dict[str, str] = {
    "Moon": "duygu",
    "Sun": "irade",
    "Mercury": "zihin",
    "Venus": "değer/çekim",
    "Mars": "hareket",
    "Jupiter": "genişleme",
    "Saturn": "sorumluluk",
    "Uranus": "değişim",
    "Neptune": "algı",
    "Pluto": "dönüşüm",
    "Chiron": "yaralanma",
    "North Node": "yön",
    "South Node": "geçmiş",
    "Fortune": "akıntı/fırsat",
    "Vertex": "kesişim",
}

ASPECT_TONE: Dict[str, str] = {
    "square": "gerilim",
    "opposition": "gerilim",
    "conjunction": "yoğunlaşma",
    "trine": "akış",
    "sextile": "destek",
}


def _theme_for_obj(obj: EventObj) -> str:
    key = canonical_obj_key(obj.key)
    if obj.type != "axis":
        return PLANET_MEANING.get(key, key.lower())
    return AXIS_THEME.get(key, key)


def build_where(a: EventObj, b: EventObj) -> Optional[str]:
    def where_for(obj: EventObj) -> Optional[str]:
        key = canonical_obj_key(obj.key)
        if obj.type == "axis":
            return AXIS_THEME.get(key)
        if obj.house is not None:
            return HOUSE_THEME_UI.get(obj.house)
        return None

    wa = where_for(a)
    wb = where_for(b)

    if wa and wb:
        return f"{wa} ↔ {wb}"
    if wa and not wb:
        return wa
    if wb and not wa:
        return wb
    return None


def _advice_template(tone: Optional[str], where: str) -> str:
    if tone == "gerilim":
        if "iletişim" in where:
            return "Mesaj atmadan önce 10 dakika bekle; ne hissettiğini 3 kelimeyle adlandır, sonra tek net cümle kur."
        return "10 dakika bekle, ne hissettiğini 3 kelimeyle adlandır, sonra tek net cümle kur."
    if tone == "yoğunlaşma":
        return "Bugün tek bir öncelik seç; fazla yüklenmeyi törpüleyip onu bitir."
    if tone == "akış":
        return "Fırsatı küçült ve somutlaştır; 30 dakikalık tek bir adım at."
    if tone == "destek":
        return "Kolay akan şeyi büyüt; küçük bir teklif/hamleyle kapıyı arala."
    return "Küçük bir adım at ve sonucu gözlemle."


def build_label(meta: EventMeta) -> EventMeta:
    aspect = norm_aspect(meta.aspect)
    a_key = canonical_obj_key(meta.a.key)
    b_key = canonical_obj_key(meta.b.key)

    a_theme = _theme_for_obj(replace(meta.a, key=a_key))
    b_theme = _theme_for_obj(replace(meta.b, key=b_key))

    where = build_where(replace(meta.a, key=a_key), replace(meta.b, key=b_key)) or "genel"
    tone = ASPECT_TONE.get(aspect)

    short = f"{a_theme} ↔ {b_theme}" + (f" {tone}" if tone else "")
    short = short.strip()

    sym = ASPECT_SYMBOL.get(aspect, aspect)
    short_plus = f"{a_key} {sym} {b_key}: {short}"

    parts = where.split(" ↔ ")
    left = parts[0] if parts and parts[0] else "genel"
    right = parts[1] if len(parts) > 1 and parts[1] else left
    tone_text = tone or "etkileşim"

    mechanism = f"{a_theme} ({left}) ile {b_theme} ({right}) arasında {tone_text}."
    advice = _advice_template(tone, where)

    label = EventLabel(
        short=short,
        where=where,
        short_plus=short_plus,
        full=LabelFull(mechanism=mechanism, advice=advice),
    )

    context = {
        "a_key": a_key,
        "b_key": b_key,
        "a_theme": a_theme,
        "b_theme": b_theme,
        "aspect_norm": aspect,
        "aspect_tone": tone,
    }

    meta2 = replace(
        meta,
        aspect=aspect,
        a=replace(meta.a, key=a_key),
        b=replace(meta.b, key=b_key),
        label=label,
        context=context,
    )
    return meta2
