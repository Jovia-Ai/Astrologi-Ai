from typing import Any, Dict, List

from app.transit.serialize.calendar_public_text import humanize_label, generate_user_note
from app.transit.serialize.status_maps import map_status

DEFAULT_TOP_EVENTS = 3

RATING_TEXT = {
    3: "cok ideal",
    2: "uygun",
    1: "notr",
    0: "kacinilmali",
}

CRITICAL_UI = {
    "phase_shift": "donusum etkisi",
    "event_peak": "enerji zirvesi",
    "caution_window": "dikkat penceresi",
}

ASPECT_LABELS_TR = {
    "tr.mars.conjunction.mercury": "Mars-Merkur kavusumu",
    "tr.venus.conjunction.jupiter": "Venus-Jupiter kavusumu",
    "tr.sun.trine.mars": "Gunes-Mars ucgeni",
    "tr.mars.square.chiron": "Mars-Chiron karesi",
}

RATING_MAP = {
    0: "Önermiyoruz",
    1: "Nötr / yapılabilir",
    2: "İyi",
    3: "Çok ideal",
}

POSITIVE_HINTS = (
    "destek",
    "akış",
    "büyüme",
    "genişleme",
    "uygun",
    "fırsat",
)

LABEL_TRANSLATIONS = {
    "North Node duragan: yon degisimi": "Yön değişimi ve kader teması",
    "North Node retro bitiyor": "Kadersel konular netleşiyor",
    "South Node retro bitiyor": "Geçmiş temalar kapanıyor",
    "Chiron retro bitiyor": "Yara teması çözülüyor",
    "Chiron duragan: yon degisimi": "Hassas noktalar yön değiştiriyor",
}


def _rating_from_day(day: Dict[str, Any]) -> int:
    heat = int(day.get("heat") or 0)
    if heat >= 85:
        return 3
    if heat >= 60:
        return 2
    if heat >= 25:
        return 1
    return 0


def _adjust_rating_for_beauty(rating: int, *, sub_intent: str | None, day: Dict[str, Any]) -> int:
    if not sub_intent:
        return rating

    moon_phase = (day.get("moon_phase") or "").lower()
    labels_text = " ".join(day.get("labels", [])).lower()
    is_critical = bool(day.get("is_critical", False))

    if sub_intent == "procedure":
        if moon_phase == "full":
            return min(rating, 1)
        if is_critical:
            return min(rating, 1)
        if ("mars" in labels_text) or ("yaralanma" in labels_text) or ("gerilim" in labels_text):
            return 0
        return rating

    if sub_intent == "reduce":
        if moon_phase == "waxing":
            return min(rating, 1)
        if is_critical:
            return min(rating, 1)
        return rating

    if sub_intent == "nourish":
        if ("yaralanma" in labels_text) and ("gerilim" in labels_text):
            return min(rating, 1)
        return rating

    return rating


def _humanize_event_label(label: str) -> str:
    if not label:
        return ""
    return ASPECT_LABELS_TR.get(label, label)


def _translate_label(label: str) -> str:
    if not label:
        return ""
    return LABEL_TRANSLATIONS.get(label, label)


def _map_rating_to_status(rating: int) -> str:
    return RATING_MAP.get(int(rating or 0), "Nötr / yapılabilir")


def _pick_ui_labels(day: Dict[str, Any], *, lens_suffix: str | None = None) -> List[str]:
    labels: List[str] = []
    label_pack = day.get("label_pack") or {}
    phase = label_pack.get("phase") or []
    top = label_pack.get("top") or []

    if phase:
        labels.append(str(phase[0]))

    for item in top:
        if isinstance(item, dict) and item.get("short"):
            labels.append(str(item.get("short")))
        elif isinstance(item, str):
            labels.append(item)

    seen = set()
    cleaned: List[str] = []
    for l in labels:
        if not l:
            continue
        if l in seen:
            continue
        seen.add(l)
        cleaned.append(l)

    r = int(day.get("rating", 0) or 0)
    cap = 2 if r <= 1 else 3
    cleaned = cleaned[:cap]
    if not cleaned:
        fallback = [str(x) for x in (day.get("labels") or []) if x]
        cleaned = fallback[:2]
    return [humanize_label(l, lens_suffix=lens_suffix) for l in cleaned]


def _generate_user_note(day: Dict[str, Any]) -> str:
    rating = int(day.get("rating", 0) or 0)
    is_critical = bool(day.get("is_critical", False))
    reasons = set(day.get("critical_reason", []) or [])

    if is_critical:
        if rating >= 2:
            if "event_peak" in reasons:
                return "Zirve gün; doğru hedefe odaklanırsan çok verimli."
            if "phase_shift" in reasons:
                return "Dönüm noktası; planı sadeleştir, acele karar verme."
            return "Güçlü gün; tek bir ana hedef seçip oraya yüklen."
        return "Hassas gün; ağır işlemleri ertele, küçük adımlarla ilerle."
    if rating == 3:
        return "Akış güçlü; planladığını uygulamak için ideal."
    if rating == 2:
        return "İyi; küçük risklerle ilerleyebilirsin."
    if rating == 1:
        return "Nötr; rutin işler için uygun."
    return "Bugünü dinlenme ve hazırlık günü yap."


def _enforce_rating_label_consistency(rating: int, labels: List[str]) -> int:
    if rating != 0:
        return rating
    joined = " ".join(labels).lower()
    if any(w in joined for w in POSITIVE_HINTS):
        return 1
    return 0


def build_public_day(
    day: Dict[str, Any],
    *,
    intent: str = "transit",
    lens_suffix: str | None = None,
) -> Dict[str, Any]:
    rating = int(day.get("rating") or 0)
    labels = _pick_ui_labels(day, lens_suffix=lens_suffix)
    rating = _enforce_rating_label_consistency(rating, labels)
    note = generate_user_note(
        date=day.get("date", ""),
        rating=rating,
        is_critical=bool(day.get("is_critical")),
        labels=labels,
        intent=intent,
    )
    return {
        "date": day.get("date"),
        "display_date": day.get("display_date"),
        "rating": rating,
        "status": map_status(rating, intent=intent),
        "labels": labels,
        "note": note,
        "is_critical": bool(day.get("is_critical", False)),
    }


def _compact_event_from_marker(marker: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": marker.get("id"),
        "label": _humanize_event_label(marker.get("label")),
        "tier": marker.get("tier"),
        "severity": marker.get("severity"),
        "domains": marker.get("domains", []),
        "kind": marker.get("kind"),
        "phase_kind": marker.get("phase_kind"),
        "bodies": marker.get("bodies", []),
    }


def to_ui_compact_calendar(full: Dict[str, Any], top_n: int = DEFAULT_TOP_EVENTS) -> Dict[str, Any]:
    """
    full calendar payload -> UI'ya uygun hafif payload
    - markers[] dev listesini kaldırır
    - her gun icin top events'i gommer (marker_ids -> marker objesine bakarak)
    """
    marker_index = {m["id"]: m for m in full.get("markers", []) if m.get("id")}

    out_days: List[Dict[str, Any]] = []
    for d in full.get("days", []):
        ui_day = {
            "date": d.get("date"),
            "display_date": d.get("display_date"),
            "heat": d.get("heat", 0),
            "rating": _rating_from_day(d),
            "labels": d.get("labels", []),
            "is_critical": d.get("is_critical", False),
            "critical_reason": d.get("critical_reason", []),
            "event_count": d.get("event_count", 0),
            "moon_phase": d.get("moon_phase"),
        }

        top_event_ids = d.get("top_event_ids", []) or []
        events = []
        for eid in top_event_ids[:top_n]:
            m = marker_index.get(eid)
            if m:
                events.append(_compact_event_from_marker(m))
            else:
                events.append({"id": eid, "label": eid})

        if events:
            ui_day["top_events"] = events

        if d.get("label_pack"):
            ui_day["label_pack"] = d.get("label_pack")

        out_days.append(ui_day)

    return {
        "range": full.get("range", {}),
        "year_summary": full.get("year_summary", {}),
        "days": out_days,
    }


def to_ui_day_detail(full: Dict[str, Any], date: str, top_n: int = 7) -> Dict[str, Any]:
    """
    Tek gun detay endpoint'i icin:
    - full icinden ilgili gunu bulur
    - o gune ait marker detaylarini gommer
    """
    marker_index = {m["id"]: m for m in full.get("markers", []) if m.get("id")}
    day = next((x for x in full.get("days", []) if x.get("date") == date), None)
    if not day:
        return {"date": date, "error": "day_not_found"}

    top_event_ids = day.get("top_event_ids", []) or []
    events = []
    for eid in top_event_ids[:top_n]:
        m = marker_index.get(eid)
        events.append(_compact_event_from_marker(m) if m else {"id": eid, "label": eid})

    return {
        "range": full.get("range", {}),
        "date": day.get("date"),
        "display_date": day.get("display_date"),
        "heat": day.get("heat", 0),
        "rating": _rating_from_day(day),
        "labels": day.get("labels", []),
        "is_critical": day.get("is_critical", False),
        "critical_reason": day.get("critical_reason", []),
        "moon_phase": day.get("moon_phase"),
        "label_pack": day.get("label_pack"),
        "events": events,
    }


def _to_ui_year_summary(year_summary: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "core_story": year_summary.get("core_story", ""),
        "dominant_domains": year_summary.get("dominant_domains", []),
        "indices": year_summary.get("indices", {}),
    }


def _to_ui_day(day: Dict[str, Any], *, sub_intent: str | None = None) -> Dict[str, Any]:
    rating = _rating_from_day(day)
    rating = _adjust_rating_for_beauty(rating, sub_intent=sub_intent, day=day)

    critical_reason = day.get("critical_reason", []) or []
    critical_text = [CRITICAL_UI.get(r, r) for r in critical_reason][:2]

    top_events = []
    for ev in (day.get("top_events") or [])[:3]:
        top_events.append(
            {
                "id": ev.get("id"),
                "label": ev.get("label"),
                "kind": ev.get("kind"),
                "phase_kind": ev.get("phase_kind"),
                "bodies": (ev.get("bodies") or [])[:2],
            }
        )

    labels = (day.get("labels") or [])[:3]

    return {
        "date": day.get("date"),
        "display_date": day.get("display_date"),
        "rating": rating,
        "rating_text": RATING_TEXT.get(rating, "notr"),
        "heat": int(day.get("heat", 0)),
        "moon_phase": day.get("moon_phase"),
        "is_critical": bool(day.get("is_critical", False)),
        "critical_text": critical_text,
        "labels": labels,
        "top_events": top_events,
    }


def to_ui_calendar(
    full_payload: Dict[str, Any],
    *,
    lens: str = "general",
    intent: str | None = None,
    sub_intent: str | None = None,
    compact: bool = False,
) -> Dict[str, Any]:
    ui = {
        "range": full_payload.get("range", {}),
        "year_summary": _to_ui_year_summary(full_payload.get("year_summary", {})),
        "lens": lens,
        "intent": intent,
        "sub_intent": sub_intent,
        "days": [],
    }

    for day in full_payload.get("days", []):
        ui_day = _to_ui_day(day, sub_intent=sub_intent)
        if compact:
            if "labels" in ui_day:
                ui_day["labels"] = ui_day["labels"][:2]
            if "top_events" in ui_day:
                ui_day["top_events"] = ui_day["top_events"][:2]
            ui_day.pop("heat", None)
        ui["days"].append(ui_day)

    return ui


def build_calendar_outputs(
    range_cfg: Dict[str, Any],
    engine_result: Dict[str, Any],
    *,
    lens: str = "general",
    intent: str | None = None,
    sub_intent: str | None = None,
) -> Dict[str, Any]:
    full_payload = engine_result
    ui_payload = to_ui_calendar(full_payload, lens=lens, intent=intent, sub_intent=sub_intent)
    return {"full": full_payload, "ui": ui_payload}


def build_calendar_public(
    full_payload: Dict[str, Any],
    *,
    intent: str = "transit",
    lens_suffix: str | None = None,
) -> Dict[str, Any]:
    days_internal = full_payload.get("days") or []
    public_days = [
        build_public_day(d, intent=intent, lens_suffix=lens_suffix)
        for d in days_internal
        if isinstance(d, dict)
    ]
    return {
        "range": full_payload.get("range", {}) or {},
        "year_summary": full_payload.get("year_summary", {}) or {},
        "days": public_days,
    }
