from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class PatchConfig:
    drop_day_labels: bool = True
    top_ids_transit_only: bool = True
    where_fallback: str = "genel"
    max_top_labels: int = 2
    include_debug_context: bool = False


ASPECT_SYMBOL = {
    "square": "□",
    "opposition": "☍",
    "trine": "△",
    "sextile": "✶",
    "conjunction": "☌",
}

ASPECT_TONE_TR = {
    "square": "gerilim",
    "opposition": "gerilim",
    "conjunction": "yoğunlaşma",
    "trine": "akış",
    "sextile": "destek",
}

HOUSE_THEME_UI_TR = {
    1: "benlik",
    2: "para",
    3: "iletişim",
    4: "ev",
    5: "yaratıcılık",
    6: "rutin",
    7: "ilişki",
    8: "dönüşüm",
    9: "ufuk",
    10: "kariyer",
    11: "çevre",
    12: "iç dünya",
}

AXIS_THEME_TR = {
    "IC": "ev",
    "MC": "iş",
    "ASC": "benlik",
    "DSC": "ilişki",
}

OBJECT_THEME_TR = {
    "Sun": "irade",
    "Moon": "duygu",
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
    "Vertex": "kesişim",
    "Fortune": "akış/şans",
    "ASC": "benlik",
    "DSC": "ilişki",
    "MC": "iş",
    "IC": "ev",
}


def _safe_int(x: Any) -> Optional[int]:
    try:
        return int(x) if x is not None else None
    except Exception:
    return None


def _nonempty(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def is_phase_event_id(event_id: str) -> bool:
    return event_id.startswith("phase.")


def get_object_theme(key: Optional[str]) -> str:
    if not key:
        return "tema"
    return OBJECT_THEME_TR.get(key, key)


def get_where_for_side(obj: Dict[str, Any]) -> Optional[str]:
    if not obj:
        return None
    key = obj.get("key")
    typ = obj.get("type")
    house = _safe_int(obj.get("house"))

    if house and 1 <= house <= 12:
        return HOUSE_THEME_UI_TR.get(house)

    if typ == "axis" and key in AXIS_THEME_TR:
        return AXIS_THEME_TR[key]

    return None


def build_where(a: Dict[str, Any], b: Dict[str, Any], fallback: str) -> str:
    a_where = get_where_for_side(a)
    b_where = get_where_for_side(b)

    if a_where and b_where:
        return f"{a_where} ↔ {b_where}"
    if a_where and not b_where:
        return a_where
    if b_where and not a_where:
        return b_where
    return fallback


def build_short(a_theme: str, b_theme: str, aspect: str) -> str:
    tone = ASPECT_TONE_TR.get(aspect, "etki")
    if aspect in ("square", "opposition"):
        return f"{a_theme} ↔ {b_theme} {tone}"
    return f"{a_theme} + {b_theme} {tone}"


def build_short_plus(a_key: str, aspect: str, b_key: str, short: str) -> str:
    sym = ASPECT_SYMBOL.get(aspect, aspect)
    return f"{a_key} {sym} {b_key}: {short}"


def build_mechanism(a_theme: str, a_where: str, b_theme: str, b_where: str, aspect: str) -> str:
    tone = ASPECT_TONE_TR.get(aspect, "etki")
    a_part = f"{a_theme} ({a_where})" if a_where and a_where != "genel" else a_theme
    b_part = f"{b_theme} ({b_where})" if b_where and b_where != "genel" else b_theme

    if aspect in ("square", "opposition"):
        return f"{a_part} ile {b_part} arasında sürtünme/gerilim."
    if aspect == "conjunction":
        return f"{a_part} ile {b_part} aynı noktada yoğunlaşıyor."
    if aspect == "trine":
        return f"{a_part} ile {b_part} arasında akış var; daha az dirençle ilerler."
    if aspect == "sextile":
        return f"{a_part} ile {b_part} arasında destekleyici bir bağlantı var; küçük adımlarla büyür."
    return f"{a_part} ile {b_part} arasında bir etkileşim var."


def build_advice(aspect: str, a_theme: str, b_theme: str) -> str:
    if aspect in ("square", "opposition"):
        return "10 dakika bekle, ihtiyacını 3 kelimeyle adlandır, sonra iki tarafı da gözeten tek net cümle kur."
    if aspect == "conjunction":
        return "Tek bir hedef seç, dikkatini oraya topla, fazlalıkları törpüle; bugün 'az ama öz' çalış."
    if aspect in ("trine", "sextile"):
        return f"Küçük bir adım at: {a_theme} alanında 1 pratik hamle seç ve {b_theme} ile bağlayarak tamamla."
    return "Bugün niyetini tek cümleye indir ve küçük bir uygulama adımı seç."


def ensure_event_label(meta: Dict[str, Any], config: PatchConfig) -> Dict[str, Any]:
    a = meta.get("a") or {}
    b = meta.get("b") or {}
    aspect = meta.get("aspect") or "conjunction"

    a_key = a.get("key") or "A"
    b_key = b.get("key") or "B"

    a_theme = get_object_theme(a_key)
    b_theme = get_object_theme(b_key)

    where = build_where(a, b, config.where_fallback)
    short = build_short(a_theme, b_theme, aspect)
    short_plus = build_short_plus(a_key, aspect, b_key, short)

    a_where = get_where_for_side(a) or (where if where != config.where_fallback else "")
    b_where = get_where_for_side(b) or (where if where != config.where_fallback else "")

    mechanism = build_mechanism(a_theme, a_where, b_theme, b_where, aspect)
    advice = build_advice(aspect, a_theme, b_theme)

    label = meta.get("label") or {}
    label_short = _nonempty(label.get("short")) or short
    label_where = _nonempty(label.get("where")) or where or config.where_fallback
    label_short_plus = _nonempty(label.get("short_plus")) or short_plus

    full = label.get("full")
    if isinstance(full, dict):
        full_mech = full.get("mechanism") or mechanism
        full_adv = full.get("advice") or advice
        full_norm = {"mechanism": full_mech, "advice": full_adv}
    elif isinstance(full, str) and full.strip():
        full_norm = {"mechanism": full.strip(), "advice": advice}
    else:
        full_norm = {"mechanism": mechanism, "advice": advice}

    out = {
        "short": label_short.strip(),
        "short_plus": label_short_plus.strip(),
        "where": label_where.strip(),
        "full": full_norm,
    }

    if config.include_debug_context:
        out["_debug"] = {
            "a_key": a_key,
            "b_key": b_key,
            "a_house": a.get("house", None),
            "b_house": b.get("house", None),
            "aspect": aspect,
        }

    meta["label"] = out
    return out


def build_label_pack_for_day(
    day_event_ids_foreground: List[str],
    day_event_ids_background: List[str],
    registry: Dict[str, Dict[str, Any]],
    markers_by_date: Dict[str, List[Dict[str, Any]]],
    date_str: str,
    config: PatchConfig,
) -> Dict[str, Any]:
    phase_labels: List[str] = []
    for m in markers_by_date.get(date_str, []):
        if m.get("kind") == "phase":
            lbl = m.get("label")
            if lbl:
                phase_labels.append(lbl)

    top_ids = []
    for eid in day_event_ids_foreground:
        if config.top_ids_transit_only and is_phase_event_id(eid):
            continue
        top_ids.append(eid)

    top_items: List[Dict[str, Any]] = []
    for eid in top_ids:
        meta = registry.get(eid)
        if not meta:
            top_items.append({"event_id": eid, "short": eid, "where": config.where_fallback})
            continue

        label = ensure_event_label(meta, config)
        where = _nonempty(label.get("where")) or config.where_fallback
        short = _nonempty(label.get("short")) or eid
        top_items.append(
            {
                "event_id": eid,
                "short": short,
                "where": where,
                "short_plus": _nonempty(label.get("short_plus")),
            }
        )

    if config.max_top_labels and len(top_items) > config.max_top_labels:
        top_items = top_items[: config.max_top_labels]

    return {"phase": phase_labels, "top": top_items}


def patch_day_output(
    day_obj: Dict[str, Any],
    items_map: Dict[str, Dict[str, List[str]]],
    registry: Dict[str, Dict[str, Any]],
    markers: List[Dict[str, Any]],
    config: PatchConfig,
) -> Dict[str, Any]:
    date_str = day_obj["date"]

    markers_by_date: Dict[str, List[Dict[str, Any]]] = {}
    for m in markers:
        d = m.get("date")
        if not d:
            continue
        markers_by_date.setdefault(d, []).append(m)

    fg = (items_map.get(date_str) or {}).get("foreground", []) or []
    bg = (items_map.get(date_str) or {}).get("background", []) or []

    phase_event_ids = []
    for m in markers_by_date.get(date_str, []):
        if m.get("kind") == "phase":
            eid = m.get("event_id")
            if eid:
                phase_event_ids.append(eid)

    top_event_ids = []
    for eid in fg:
        if config.top_ids_transit_only and is_phase_event_id(eid):
            continue
        top_event_ids.append(eid)

    label_pack = build_label_pack_for_day(fg, bg, registry, markers_by_date, date_str, config)

    out = dict(day_obj)

    if config.drop_day_labels and "labels" in out:
        out.pop("labels", None)

    out["label_pack"] = label_pack
    out["top_event_ids"] = top_event_ids
    out["phase_event_ids"] = phase_event_ids

    return out


def enrich_themes(
    themes: List[Dict[str, Any]],
    registry: Dict[str, Dict[str, Any]],
    config: PatchConfig,
) -> List[Dict[str, Any]]:
    out = []
    for theme in themes:
        tt = dict(theme)
        event_id = tt.get("event_id")
        meta = registry.get(event_id) if event_id else None

        if meta:
            label = ensure_event_label(meta, config)
            old = (tt.get("label") or "").strip().lower()
            if not old or old.endswith(" etkisi"):
                tt["label"] = label["short"]
            tt["label_pack"] = {
                "short": label["short"],
                "where": label["where"],
                "full": label.get("full"),
            }
        out.append(tt)
    return out


def patch_payload(
    payload: Dict[str, Any],
    registry: Dict[str, Dict[str, Any]],
    config: Optional[PatchConfig] = None,
) -> Dict[str, Any]:
    config = config or PatchConfig()

    items_map = payload.get("items_map") or {}
    markers = payload.get("markers") or []
    days = payload.get("days") or []
    themes = payload.get("themes") or []

    new_days = []
    for day in days:
        new_days.append(patch_day_output(day, items_map, registry, markers, config))

    new_themes = enrich_themes(themes, registry, config)

    out = dict(payload)
    out["days"] = new_days
    out["themes"] = new_themes
    return finalize_payload(out, config)


def finalize_payload(payload: Dict[str, Any], config: PatchConfig) -> Dict[str, Any]:
    for day in payload.get("days", []):
        if config.drop_day_labels and "labels" in day:
            day.pop("labels", None)
        label_pack = day.get("label_pack") or {}
        top_items = label_pack.get("top") or []
        for item in top_items:
            if isinstance(item, dict) and not item.get("where"):
                item["where"] = config.where_fallback
        top_ids = day.get("top_event_ids") or []
        if isinstance(top_ids, list):
            day["top_event_ids"] = [
                eid for eid in top_ids if isinstance(eid, str) and not eid.startswith("phase.")
            ]
    return payload
    return out


if __name__ == "__main__":
    pass
