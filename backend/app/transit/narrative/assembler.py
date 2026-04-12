from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Mapping

from app.transit.narrative.composer import compose_upper_meaning_line
from app.transit.narrative.generator import generate_daily_narrative, make_seed
from app.transit.narrative.models import CopyBundle, UIBlock


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_list(value: Any) -> List[Any]:
    return list(value) if isinstance(value, list) else []


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _expand_window_days(start: str, end: str) -> List[str]:
    d0 = _parse_date(start)
    d1 = _parse_date(end)
    if not d0 or not d1 or d0 > d1:
        return []
    out: List[str] = []
    cur = d0
    while cur <= d1:
        out.append(cur.isoformat())
        cur = date.fromordinal(cur.toordinal() + 1)
    return out


def _normalize_block_id(prefix: str, suffix: str) -> str:
    clean = suffix.replace(" ", "_").replace(":", "_")
    return f"{prefix}_{clean}"


def _extract_upper_meaning_from_day(day: Mapping[str, Any] | None) -> str:
    if not isinstance(day, Mapping):
        return ""
    top_events = _safe_list(day.get("top_events"))
    if not top_events:
        return ""
    top = top_events[0] if isinstance(top_events[0], Mapping) else {}
    bodies = _safe_list(top.get("bodies"))
    transit_body = str(bodies[0]) if bodies else ""
    natal_target = str(bodies[1]) if len(bodies) > 1 else ""
    if not transit_body and not natal_target:
        return ""
    house_overlay = None
    raw_house = top.get("house_overlay")
    try:
        house_overlay = int(raw_house) if raw_house is not None else None
    except (TypeError, ValueError):
        house_overlay = None
    seed = abs(hash((str(day.get("date") or ""), transit_body, natal_target))) % (2**31)
    return compose_upper_meaning_line(
        transit_body=transit_body,
        natal_target=natal_target,
        house_overlay=house_overlay,
        seed=seed,
    )


def _pick_selected_day(
    calendar_public: Mapping[str, Any],
    selected_date: str | None,
) -> Dict[str, Any] | None:
    days = _safe_list(calendar_public.get("days"))
    if not days:
        return None
    if selected_date:
        for day in days:
            if isinstance(day, Mapping) and str(day.get("date")) == selected_date:
                return dict(day)
    return dict(days[0]) if isinstance(days[0], Mapping) else None


def _infer_signals_count(day: Mapping[str, Any]) -> int:
    labels = _safe_list(day.get("labels"))
    top_events = _safe_list(day.get("top_events"))
    event_count = int(day.get("event_count") or len(top_events) or 0)
    return max(event_count, len(labels), len(top_events))


def _synthesize_core_story(
    *,
    domains: List[str],
    pressure: float,
    support: float,
    top_labels: List[str],
) -> str:
    domain_text = ", ".join(domains[:2]) if domains else "genel yasam"
    pressure_text = "yuksek" if pressure >= 0.6 else ("orta" if pressure >= 0.35 else "dusuk")
    support_text = "guclu" if support >= 0.6 else ("orta" if support >= 0.35 else "sinirli")
    labels_text = ", ".join(top_labels[:3]) if top_labels else "gunluk ritim"
    return (
        f"Bu donemde {domain_text} alanlari one cikiyor. "
        f"Baski seviyesi {pressure_text}, destek seviyesi {support_text}. "
        f"Takvim sinyallerinde {labels_text} temalari daha sik gorulebilir."
    )


def assemble_blocks(
    *,
    calendar_public: Mapping[str, Any],
    calendar_internal: Mapping[str, Any] | None = None,
    best_times: Mapping[str, Any] | None = None,
    year_summary: Mapping[str, Any] | None = None,
    selected_date: str | None = None,
    seed_context: Mapping[str, Any] | None = None,
    locale: str = "tr",
) -> List[UIBlock]:
    blocks: List[UIBlock] = []
    range_payload = dict(calendar_public.get("range") or {})
    selected_day = _pick_selected_day(calendar_public, selected_date)

    ys = dict(year_summary or calendar_public.get("year_summary") or {})
    core_story = str(ys.get("core_story") or "").strip()
    domains = [str(d) for d in _safe_list(ys.get("dominant_domains")) if str(d).strip()]
    indices = dict(ys.get("indices") or {})
    pressure = _safe_float(indices.get("pressure"), 0.0)
    support = _safe_float(indices.get("support"), 0.0)
    intensity = max(pressure, support)
    top_labels: List[str] = []
    for day in _safe_list(calendar_public.get("days")):
        if not isinstance(day, Mapping):
            continue
        for label in _safe_list(day.get("labels")):
            label_text = str(label).strip()
            if label_text:
                top_labels.append(label_text)
    if not core_story:
        core_story = _synthesize_core_story(
            domains=domains,
            pressure=pressure,
            support=support,
            top_labels=top_labels,
        )
    upper_meaning = _extract_upper_meaning_from_day(_pick_selected_day(calendar_public, selected_date))
    if upper_meaning:
        core_story = f"{core_story} {upper_meaning}".strip()

    if core_story:
        blocks.append(
            UIBlock(
                id=_normalize_block_id("core_theme", f"{range_payload.get('start', 'range')}_{range_payload.get('end', '')}"),
                type="core_theme",
                horizon="month",
                intensity=min(1.0, max(0.2, intensity if intensity > 0 else 0.55)),
                domains=domains,
                copy=CopyBundle(
                    title="Donem Temasi",
                    short=core_story,
                    medium=core_story,
                    long=core_story,
                ),
                why=[f"dominant_domains: {', '.join(domains)}"] if domains else [],
                cta={"label": "Detaya in", "action": "open_period_theme", "payload": range_payload},
            )
        )

    if pressure >= 0.6:
        blocks.append(
            UIBlock(
                id=_normalize_block_id("challenge", range_payload.get("start", "range")),
                type="challenge",
                horizon="week",
                intensity=min(1.0, pressure),
                domains=domains,
                copy=CopyBundle(
                    title="Dikkat Alani",
                    short="Bazi gunlerde baski artabilir; adimlari sade tutmak daha iyi calisir.",
                    medium="Baski indeksi yuksek oldugunda kararlari kademeli almak ve oncelik azaltmak daha verimli olur.",
                    long="Baski indeksi bu donemde yuksek. Buyuk hamleleri tek gunde bitirmeye calismak yerine parcali ilerleme daha istikrarli sonuc verir.",
                ),
                why=[f"pressure_index={pressure:.2f}"],
            )
        )

    if support >= 0.55:
        blocks.append(
            UIBlock(
                id=_normalize_block_id("support", range_payload.get("start", "range")),
                type="support",
                horizon="week",
                intensity=min(1.0, support),
                domains=domains,
                copy=CopyBundle(
                    title="Destek Alani",
                    short="Destekleyici akislari kullanmak icin duzenli ve net bir plan faydali.",
                    medium="Destek indeksi belirgin. Iliski, iletisim ve rutin tarafinda ritimli ilerleyis daha hizli geri donus verir.",
                    long="Bu aralikta destek sinyalleri gorunur. Net takvim, sade oncelik ve ritimli ilerleme ile olumlu etkileri daha kolay toplayabilirsin.",
                ),
                why=[f"support_index={support:.2f}"],
            )
        )

    if selected_day:
        event_count = int(selected_day.get("event_count") or 0)
        signals_count = _infer_signals_count(selected_day)
        has_signals = signals_count > 0
        rating = int(selected_day.get("rating") or 0)
        label_values = [str(label) for label in _safe_list(selected_day.get("labels")) if str(label).strip()]
        is_critical_day = bool(selected_day.get("is_critical"))
        context = dict(seed_context or {})
        narrative_seed = make_seed(
            birth_fingerprint=str(context.get("birth_fingerprint") or ""),
            date=str(selected_day.get("date") or ""),
            intent=str(context.get("intent") or "general"),
            lens=str(context.get("lens") or "general"),
            rating=rating,
            is_critical=is_critical_day,
            labels=label_values,
        )
        note = generate_daily_narrative(
            rating=rating,
            is_critical=is_critical_day,
            labels=label_values,
            seed=narrative_seed,
            top_event=(selected_day.get("top_events") or [None])[0],
            locale=locale,
        )

        blocks.append(
            UIBlock(
                id=_normalize_block_id("daily_energy", str(selected_day.get("date") or "day")),
                type="daily_energy",
                horizon="day",
                intensity=min(1.0, max(0.2, _safe_float(selected_day.get("rating"), 1.0) / 3.0)),
                domains=domains,
                copy=CopyBundle(
                    title=f"Gun Enerjisi • {selected_day.get('date')}",
                    short=note,
                    medium=note,
                    long=note,
                ),
                why=[str(label) for label in label_values[:2]],
                meta={
                    "date": selected_day.get("date"),
                    "events_count": event_count,
                    "signals_count": signals_count,
                    "has_signals": has_signals,
                    "labels": _safe_list(selected_day.get("labels"))[:3],
                    "seed": narrative_seed,
                },
            )
        )

        blocks.append(
            UIBlock(
                id=_normalize_block_id("event_list_preview", str(selected_day.get("date") or "day")),
                type="event_list_preview",
                horizon="day",
                intensity=min(1.0, max(0.1, signals_count / 6.0)),
                domains=domains,
                copy=CopyBundle(
                    title="Gun Onizleme",
                    short=note,
                    medium=note,
                    long=note,
                ),
                why=[str(l) for l in _safe_list(selected_day.get("labels"))[:2]],
                cta={"label": "Gun detayini ac", "action": "open_calendar_day", "payload": {"date": selected_day.get("date")}},
                meta={
                    "date": selected_day.get("date"),
                    "events_count": event_count,
                    "signals_count": signals_count,
                    "has_signals": has_signals,
                },
            )
        )

        if bool(selected_day.get("is_critical")):
            blocks.append(
                UIBlock(
                    id=_normalize_block_id("alert", str(selected_day.get("date") or "day")),
                    type="alert",
                    horizon="day",
                    intensity=0.9,
                    domains=domains,
                    copy=CopyBundle(
                        title="Dikkat Sinyali",
                        short="Bugun etkiler daha keskin olabilir; oncelikleri azaltmak faydali.",
                        medium="Kritik sinyal gorulen gunlerde karar ve efor yogunlugunu dusurmek daha iyi sonuc verir.",
                        long="Bu gun kritik sinyal var. Zorunlu olmayan kararlarin ertelenmesi ve daha kontrollu tempo daha guvenli bir akistir.",
                    ),
                    why=[str(r) for r in _safe_list(selected_day.get("critical_text"))],
                )
            )

    bt = dict(best_times or {})
    candidates = [c for c in _safe_list(bt.get("candidates")) if isinstance(c, Mapping)]
    windows = [w for w in _safe_list(bt.get("windows")) if isinstance(w, Mapping)]
    intent = str(bt.get("intent") or "").strip()
    intent_label = str(bt.get("intent_label") or "").strip() or intent or "Genel"

    if candidates:
        top = dict(candidates[0])
        top_date = str(top.get("date") or "")
        top_reason = str(top.get("reason") or "En guclu gun penceresi.").strip()
        blocks.append(
            UIBlock(
                id=_normalize_block_id("best_time_primary", top_date or "range"),
                type="best_time_primary",
                horizon="week",
                intensity=min(1.0, max(0.1, _safe_float(top.get("score"), 0.7))),
                domains=domains,
                copy=CopyBundle(
                    title="En Iyi Zaman",
                    short=f"{top_date} gunu {intent_label} icin one cikiyor.",
                    medium=top_reason,
                    long=f"{top_date} icin puan {top.get('score')}. {top_reason}",
                ),
                why=[top_reason] if top_reason else [],
                cta={"label": "Takvimde goster", "action": "focus_date", "payload": {"date": top_date, "intent": intent}},
                meta={
                    "date": top_date,
                    "intent": intent,
                    "intent_label": intent_label,
                    "score": top.get("score"),
                },
            )
        )

        list_short = ", ".join(str(c.get("date")) for c in candidates[:5])
        blocks.append(
            UIBlock(
                id=_normalize_block_id("best_time_list", range_payload.get("start", "range")),
                type="best_time_list",
                horizon="month",
                intensity=min(1.0, max(0.1, _safe_float(candidates[0].get("score"), 0.65))),
                domains=domains,
                copy=CopyBundle(
                    title="Alternatif Gunler",
                    short=f"Aday gunler: {list_short}",
                    medium="Aday gunler puan ve risk etiketine gore siralanmistir.",
                    long="Aday gun listesi niyet kurallarina gore olusur; ayni ayda birden fazla pencere olabilir.",
                ),
                why=[f"intent={intent_label}", f"candidate_count={len(candidates)}"],
                meta={
                    "intent": intent,
                    "intent_label": intent_label,
                    "candidates": [dict(c) for c in candidates[:10]],
                },
            )
        )

    if windows:
        first = dict(windows[0])
        days = _expand_window_days(str(first.get("start") or ""), str(first.get("end") or ""))
        reason = str(first.get("reason") or "").strip()
        blocks.append(
            UIBlock(
                id=_normalize_block_id("long_term", str(first.get("start") or "window")),
                type="long_term",
                horizon="month",
                intensity=min(1.0, max(0.1, _safe_float(first.get("score"), 0.6))),
                domains=domains,
                copy=CopyBundle(
                    title="Pencere Gorunumu",
                    short=f"{first.get('start')} - {first.get('end')} arasi destekli pencere.",
                    medium=reason or "Bu aralik planli adimlar icin daha stabil bir zemin sunar.",
                    long=reason or "Pencere puanlamasi aday gunlerin ortalamasina ve risk filtrelerine gore hesaplanir.",
                ),
                why=[f"window_days={len(days)}", f"intent={intent_label}"],
                meta={
                    "window": first,
                    "window_days": days,
                    "intent": intent,
                    "intent_label": intent_label,
                },
            )
        )

    blocks.append(
        UIBlock(
            id=_normalize_block_id("clarity", date.today().isoformat()),
            type="clarity",
            horizon="week",
            intensity=0.45,
            domains=domains,
            copy=CopyBundle(
                title="Netlik",
                short="Gunluk sinyal ve uzun pencereyi birlikte okuyarak karar almak daha saglikli.",
                medium="Kisa vadede gun sinyali, orta vadede pencere skorunu takip etmek belirsizligi azaltir.",
                long="Takvim sinyalleri anlik ritmi, best-times ise niyet odakli pencereyi gosterir. Ikisini birlikte kullanmak yanlis pozitifleri azaltir.",
            ),
            why=["calendar+best_times birleşik okuma"],
        )
    )

    return blocks
