from __future__ import annotations

from datetime import datetime, timedelta, date
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List
from zoneinfo import ZoneInfo

import yaml

BASE_DIR = Path(__file__).resolve().parents[1]

INTENT_RULES = yaml.safe_load(
    open(BASE_DIR / "lens/beauty/intent_rules.yaml", "r", encoding="utf-8")
) or {}

BODY_MAP = yaml.safe_load(
    open(BASE_DIR / "lens/beauty/body_area_map.yaml", "r", encoding="utf-8")
) or {}


def _get_tz_from_payload(payload: dict) -> str:
    """
    Best-effort tz extraction. Never raises.
    Accepts common keys: tz, timezone, birth.tz, profile.tz.
    """
    if not isinstance(payload, dict):
        return "UTC"
    tz = (
        payload.get("tz")
        or payload.get("timezone")
        or (payload.get("birth") or {}).get("tz")
        or (payload.get("profile") or {}).get("tz")
    )
    if not tz:
        return "UTC"
    try:
        ZoneInfo(tz)
        return tz
    except Exception:
        return "UTC"


def normalize(v, min_v=0.0, max_v=1.0):
    return max(min((v - min_v) / (max_v - min_v), 1.0), 0.0)


def score_to_rating(score: float) -> int:
    if score >= 0.8:
        return 5
    if score >= 0.65:
        return 4
    if score >= 0.5:
        return 3
    if score >= 0.35:
        return 2
    return 1


def _is_risk_event_id(event_id: str) -> bool:
    eid = (event_id or "").lower()
    return ("eclipse" in eid) or ("station" in eid) or (".rx." in eid) or ("retro" in eid)


def _reorder_event_ids_for_beauty(event_ids: list[str]) -> list[str]:
    ranked: list[tuple[int, int, str]] = []
    for i, eid in enumerate(event_ids):
        if eid.startswith("tr."):
            bucket = 0
        elif eid.startswith("phase."):
            bucket = 2
        elif _is_risk_event_id(eid):
            bucket = 1
        else:
            bucket = 1
        ranked.append((bucket, i, eid))
    ranked.sort(key=lambda x: (x[0], x[1]))
    return [eid for _b, _i, eid in ranked]


def _extract_event_ids_with_source(
    day: dict,
    intent: str,
    *,
    max_events_per_day: int = 6,
) -> tuple[list[str], list[str], str]:
    ids = day.get("top_event_ids")
    if ids:
        raw = [str(x) for x in ids if x]
        source = "top_event_ids"
    else:
        ids = day.get("marker_ids")
        if ids:
            raw = [str(x) for x in ids if x]
            source = "marker_ids"
        else:
            top_events = day.get("top_events") or []
            raw = [str(e.get("id")) for e in top_events if e.get("id")]
            source = "top_events"

    if intent == "beauty_care":
        ordered = _reorder_event_ids_for_beauty(raw)
        return raw, ordered[:max_events_per_day], source
    return raw, raw, source


class BeautySubIntent(str, Enum):
    nourish = "nourish"
    reduce = "reduce"
    procedure = "procedure"


def resolve_sub_intent(sub_intent: str | None) -> BeautySubIntent:
    if sub_intent in (BeautySubIntent.nourish, BeautySubIntent.reduce, BeautySubIntent.procedure):
        return BeautySubIntent(sub_intent)
    return BeautySubIntent.nourish


SIGN_ELEMENT_MAP = {
    "Aries": "fire",
    "Leo": "fire",
    "Sagittarius": "fire",
    "Taurus": "earth",
    "Virgo": "earth",
    "Capricorn": "earth",
    "Gemini": "air",
    "Libra": "air",
    "Aquarius": "air",
    "Cancer": "water",
    "Scorpio": "water",
    "Pisces": "water",
}

RISK_LABEL_WORDS = (
    "injury",
    "bleeding",
    "risk",
    "yaralanma",
    "kanama",
    "risk",
    "toksik",
)

GATE_NORMALIZATION = {
    "gate:critical:phase_shift": "phase_shift",
    "gate:critical:event_peak": "event_peak",
    "gate:injury_risk": "injury_risk",
    "gate:procedure_block": "procedure_block",
    "phase_shift": "phase_shift",
    "event_peak": "event_peak",
    "injury_risk": "injury_risk",
    "procedure_block": "procedure_block",
}

GATE_TO_CAUTION_TR = {
    "phase_shift": "Kritik gün: yön değişimi — bugün hızdan çok ayar ve sadeleşme iyi gelir.",
    "event_peak": "Kritik gün: enerji yoğun — yüklenmek yerine nazik ilerlemek daha iyi olur.",
    "injury_risk": "Hassasiyet riski — tahriş edici adımlardan kaçın.",
    "procedure_block": "Profesyonel işlem için uygun görünmüyor.",
}

GATE_SHORT_TR = {
    "phase_shift": "yön değişimi etkisi var",
    "event_peak": "enerji yoğun",
    "injury_risk": "hassasiyet riski var",
    "procedure_block": "işlem için uygun değil",
}

EXPLAINERS_TR = {
    "phase_shift": (
        "‘Yön değişimi’ günleri ileri koşmaktan çok ayar alma modudur. "
        "Yeni şey eklemektense rutini sadeleştirmek ve dengelemek daha iyi sonuç verir."
    ),
    "waning_moon": (
        "Ay küçülürken enerji ‘toparlama ve azaltma’ tarafına döner. "
        "Sadeleşmek ve onarmak daha iyi çalışır."
    ),
    "waxing_moon": (
        "Ay büyürken enerji ‘ekleme ve güçlendirme’ tarafına döner. "
        "Yeni adımlar daha destekli olur."
    ),
}


def normalize_gates(raw_gates: list[str] | None) -> list[str]:
    out: list[str] = []
    for g in (raw_gates or []):
        norm = GATE_NORMALIZATION.get(g)
        if norm and norm not in out:
            out.append(norm)
    return out


def normalize_critical_reason(raw: list[str] | None) -> list[str]:
    return normalize_gates([f"gate:critical:{r}" for r in (raw or []) if r])


def _has_venus_change_signal(
    *,
    rules_fired: list[str] | None,
    support_sources: dict[str, list[str]] | None,
    event_ids: list[str],
) -> bool:
    rules_fired = rules_fired or []
    for r in rules_fired:
        if "venus_jupiter_soft" in r or "venus_neptune" in r:
            return True
    if support_sources:
        has_venus = False
        has_jupiter_or_neptune = False
        for eids in support_sources.values():
            for eid in eids:
                if not isinstance(eid, str):
                    continue
                low = eid.lower()
                if "venus" in low:
                    has_venus = True
                if "jupiter" in low or "neptune" in low:
                    has_jupiter_or_neptune = True
        if has_venus and has_jupiter_or_neptune:
            return True
    for eid in event_ids or []:
        low = str(eid).lower()
        if "venus" in low and ("jupiter" in low or "neptune" in low):
            return True
    return False


def _action_type_from_signals(
    *,
    sub: BeautySubIntent,
    gates: list[str],
    rules_fired: list[str] | None,
    support_sources: dict[str, list[str]] | None,
    event_ids: list[str],
) -> str:
    if sub == BeautySubIntent.procedure:
        return "procedure"
    if gates:
        return "care"
    if _has_venus_change_signal(
        rules_fired=rules_fired,
        support_sources=support_sources,
        event_ids=event_ids,
    ):
        return "change"
    return "care"


def build_recommendation_user(
    sub: BeautySubIntent,
    action_type: str,
    final_rating: int,
) -> str:
    if action_type == "procedure":
        if final_rating >= 3:
            return "Profesyonel işlem için güçlü bir gün; planlı ve kontrollü ilerle."
        if final_rating == 2:
            return "İşlem yapılabilir; yine de basit/standart protokol tercih et."
        if final_rating == 1:
            return "İşlem için temkinli: ağır uygulamalar yerine danışma/planlama daha iyi."
        return "Bugün profesyonel işlem önermiyoruz; ertelemek daha güvenli."

    if action_type == "change":
        if final_rating >= 3:
            return (
                "Değişim için ideal bir gün; kesim/renk/stil gibi görünür adımlar destekli. "
                "Net bir planla ilerle."
            )
        if final_rating == 2:
            return "Değişim yapılabilir; net bir planla ilerlersen sonuç alma ihtimali iyi."

    if sub == BeautySubIntent.nourish and final_rating >= 2:
        return (
            "Bugün rutinini güçlendirmek için iyi; görünür değişim yapacaksan "
            "ölçülü ilerle (kesim/ton düzeltme gibi)."
        )
    if final_rating >= 2:
        return "Bugün toparlama ve bakım iyi çalışır; küçük dokunuşlar yap, aşırıya kaçma."
    if final_rating == 1:
        return "Hafif dokunuş günü: sadeleş, minimum müdahale ile ilerle."
    return "Bugün ertele: dinlenme, hazırlık ve toparlama daha iyi sonuç verir."


def gates_to_cautions(gates: list[str]) -> list[str]:
    return [GATE_TO_CAUTION_TR[g] for g in gates if g in GATE_TO_CAUTION_TR]


def build_why_support(
    day: dict,
    *,
    event_summaries: dict | None = None,
    support_sources: dict | None = None,
) -> list[str]:
    """
    User-facing supportive signals only.
    MUST NOT contain gate strings.
    """
    out: list[str] = []
    moon_phase = day.get("moon_phase")
    moon_sign = day.get("moon_sign")
    moon_element = day.get("moon_element")

    if moon_phase:
        out.append(f"Ay fazı: {moon_phase}")
    if moon_sign:
        if moon_element:
            out.append(f"Ay burcu: {moon_sign} ({moon_element})")
        else:
            out.append(f"Ay burcu: {moon_sign}")

    support_labels: list[str] = []
    if support_sources:
        for _rule, eids in support_sources.items():
            if not isinstance(eids, list):
                continue
            for eid in eids:
                if isinstance(eid, str) and eid.startswith("tr.venus.") and "Venüs destekli etkiler" not in support_labels:
                    support_labels.append("Venüs destekli etkiler (uyum/çekim artışı)")
                if len(support_labels) >= 2:
                    break
            if len(support_labels) >= 2:
                break

    if event_summaries and len(support_labels) < 2:
        for _eid, meta in event_summaries.items():
            if not isinstance(meta, dict):
                continue
            if meta.get("tier") == "support":
                label = meta.get("label")
                if label and label not in support_labels:
                    support_labels.append(label)
            if len(support_labels) >= 2:
                break

    out.extend(support_labels[:2])
    return out[:2]


def build_rating_reason_user(base_rating: int, final_rating: int, gates: list[str]) -> str | None:
    if not gates and base_rating == final_rating:
        return None
    primary = gates[0] if gates else None
    caution_short = GATE_SHORT_TR.get(primary, "temkinli olmak iyi olur") if primary else "temkinli olmak iyi olur"

    if base_rating != final_rating:
        return (
            "Bugün potansiyel var; ama "
            f"{caution_short}. Bu yüzden daha kontrollü ve sade ilerlemek en iyisi."
        )
    return f"Genel olarak uygun; yine de {caution_short} nedeniyle temkinli ilerlemek iyi olur."


def build_beauty_recommendation_variants(
    sub: BeautySubIntent, gates: list[str], final_rating: int
) -> dict:
    """
    Returns {general, skin, hair}
    Behavior-first, non-lecturing.
    """
    has_phase_shift = "phase_shift" in gates
    has_event_peak = "event_peak" in gates
    has_injury_risk = "injury_risk" in gates
    has_procedure_block = "procedure_block" in gates

    if sub == BeautySubIntent.procedure:
        if has_procedure_block or has_injury_risk or final_rating <= 1:
            return {
                "general": (
                    "Bugün profesyonel işlem için uygun görünmüyor. "
                    "Bakım yerine dinlenme ve toparlanma daha iyi sonuç verir."
                ),
                "skin": (
                    "Ciltte hassasiyet artabilir; profesyonel uygulama yerine "
                    "bariyer/nem odaklı sade rutin daha iyi."
                ),
                "hair": (
                    "Kimyasal/ısı yükünü azalt; profesyonel işlem yerine sade bakım "
                    "ve dinlendirme daha iyi."
                ),
            }
        return {
            "general": "Profesyonel işlem için genel olarak uygun; yine de aşırıya kaçmadan planlı ilerle.",
            "skin": (
                "Cilt için profesyonel uygulama düşünüyorsan, öncesi/sonrası "
                "bariyer desteğini sade tut."
            ),
            "hair": (
                "Saç için işlem planlıyorsan, eşlik eden besleyici bakım ve düşük ısı "
                "daha iyi olur."
            ),
        }

    if has_phase_shift:
        return {
            "general": (
                "Bugün bakım yapılabilir ama yüklenmek için ideal değil. "
                "Rutini sade tut; destekleyici adımlarla ilerle."
            ),
            "skin": (
                "Cilt hassas çalışabilir; onarım/nem odaklı sade rutin daha iyi. "
                "Yeni aktif ekleme, abartma."
            ),
            "hair": (
                "Saç için sade destek iyi gelir; nazik bakım + minimum ısı tercih et. "
                "Radikal değişiklik yerine toparlanma seç."
            ),
        }
    if has_event_peak:
        return {
            "general": (
                "Enerji yoğun; kısa ve nazik bir bakım daha iyi sonuç verir. "
                "Aşırı katmanlama yapma."
            ),
            "skin": (
                "Tahriş riski artabilir; hafif nem + bariyer, minimum aktif. "
                "Uzun/sert uygulamalardan kaçın."
            ),
            "hair": "Isı ve kimyasal yüklemeyi azalt; kısa bakım ve dinlendirme daha iyi.",
        }
    if has_injury_risk:
        return {
            "general": "Hassasiyet riski var; bakımda nazik ilerle. Tahriş edici adımlardan kaçın.",
            "skin": "Aktifleri azalt; nem + bariyer odaklı sade rutin daha güvenli.",
            "hair": "Saçı yormadan ilerle; sert uygulama ve yüksek ısıyı azalt.",
        }

    if sub == BeautySubIntent.reduce:
        return {
            "general": (
                "Toparlama ve hafifletme için uygun. Rutini sade tut; şişliği azaltan, "
                "dinlendirici adımlar iyi çalışır."
            ),
            "skin": (
                "Şişlik/morluk azaltma odaklı sade rutin iyi gider. "
                "Aşırı aktif yerine serinletme + nem tercih et."
            ),
            "hair": "Saçı yormadan toparlama iyi gider; nazik yıkama, hafif maske ve düşük ısı.",
        }

    return {
        "general": "Bakım rutini için iyi bir gün. Düzenli ilerle; nem/besleme ağırlıklı sade bir akış en verimlisi.",
        "skin": (
            "Cilt için nem + bariyer odağında ilerlemek iyi çalışır. "
            "Aktifleri minimumda tutup düzenli kal."
        ),
        "hair": (
            "Saç için besleyici bakım (maske/yağ) ve nazik şekillendirme uygun. "
            "Aşırı ısı/işlem yerine destekleyici rutin iyi gelir."
        ),
    }


def build_beauty_candidate_output(
    day: dict,
    *,
    sub: BeautySubIntent,
    score: float,
    base_rating: int,
    final_rating: int,
    raw_gates: list[str] | None,
    event_ids: list[str],
    event_summaries: dict | None,
    support_sources: dict[str, list[str]] | None = None,
    rules_fired: list[str] | None = None,
    debug: bool = False,
    score_breakdown: dict | None = None,
) -> dict:
    gates = normalize_gates(raw_gates)
    cautions = gates_to_cautions(gates)[:1]

    why_support = build_why_support(
        day,
        event_summaries=event_summaries,
        support_sources=support_sources,
    )
    rating_reason_user = build_rating_reason_user(base_rating, final_rating, gates)

    variants = build_beauty_recommendation_variants(sub, gates, final_rating)
    action_type = _action_type_from_signals(
        sub=sub,
        gates=gates,
        rules_fired=rules_fired,
        support_sources=support_sources,
        event_ids=event_ids,
    )
    recommendation_user = build_recommendation_user(sub, action_type, final_rating)

    explainers: dict[str, str] = {}
    mp = day.get("moon_phase")
    if "phase_shift" in gates:
        explainers["phase_shift"] = EXPLAINERS_TR["phase_shift"]
    if mp == "waning":
        explainers["waning_moon"] = EXPLAINERS_TR["waning_moon"]
    if mp == "waxing":
        explainers["waxing_moon"] = EXPLAINERS_TR["waxing_moon"]

    missing: list[str] = []
    confidence = "high"
    if day.get("moon_sign") is None:
        missing.append("moon_sign")
        confidence = "low"

    out = {
        "date": day.get("date"),
        "score": float(score),
        "base_rating": int(base_rating),
        "final_rating": int(final_rating),
        "rating": int(final_rating),
        "why": day.get("why", []),
        "why_support": why_support,
        "cautions": cautions,
        "rating_reason_user": rating_reason_user,
        "recommendation_user": recommendation_user,
        "recommendation": recommendation_user,
        "action_type": action_type,
        "event_ids": event_ids,
        "confidence": confidence,
        "missing": missing,
    }
    if explainers:
        out["explainers"] = explainers

    if debug:
        out["_debug"] = out.get("_debug", {})
        out["_debug"]["gates_applied"] = gates
        out["_debug"]["base_rating"] = int(base_rating)
        out["_debug"]["final_rating"] = int(final_rating)
        if base_rating != final_rating:
            out["_debug"]["rating_reason_system"] = (
                f"base_rating={base_rating} -> final_rating={final_rating} via gates={gates}"
            )
        if score_breakdown is not None:
            out["score_breakdown"] = score_breakdown
        if rules_fired is not None:
            out["rules_fired"] = rules_fired
        if event_summaries is not None:
            out["event_summaries"] = event_summaries
        out["_debug"]["recommendation_variants"] = variants

    if gates or base_rating != final_rating:
        if not out["cautions"]:
            out["cautions"] = ["Bugün temkinli ilerlemek iyi olur."]
        if not out.get("rating_reason_user"):
            out["rating_reason_user"] = "Bugün temkinli ve sade ilerlemek daha iyi sonuç verir."

    out["why_support"] = [w for w in out["why_support"] if "gate:" not in w]
    return out


def _moon_element_from_sign(sign: str | None) -> str | None:
    if not sign:
        return None
    return SIGN_ELEMENT_MAP.get(sign)


def _phase_modifier(sub: BeautySubIntent, phase: str | None) -> float:
    if sub == BeautySubIntent.nourish:
        if phase == "waxing":
            return 0.15
        if phase == "waning":
            return 0.05
        if phase == "full":
            return -0.05
        return 0.0
    if sub == BeautySubIntent.reduce:
        if phase == "waning":
            return 0.15
        if phase == "waxing":
            return 0.05
        if phase == "full":
            return -0.05
        return 0.0
    # procedure
    if phase == "waxing":
        return 0.05
    if phase in ("full", "new"):
        return -0.10
    return 0.0


def _element_modifier(sub: BeautySubIntent, element: str | None) -> float:
    if not element:
        return 0.0
    if sub == BeautySubIntent.nourish:
        if element in ("water", "earth"):
            return 0.10
        if element == "air":
            return 0.05
        return 0.0
    if sub == BeautySubIntent.reduce:
        if element == "earth":
            return 0.10
        if element == "water":
            return 0.05
        return 0.0
    # procedure
    if element == "earth":
        return 0.05
    if element == "fire":
        return -0.05
    return 0.0


def _event_signal_score(
    sub: BeautySubIntent,
    event_ids: list[str],
    marker_index: dict[str, dict[str, Any]] | None = None,
) -> tuple[float, float, list[str], dict[str, list[str]]]:
    support = 0.0
    penalty = 0.0
    rules: list[str] = []
    support_sources: dict[str, list[str]] = {}
    support_base: dict[str, float] = {}
    for eid in event_ids or []:
        low = eid.lower()
        marker = marker_index.get(eid) if marker_index else None
        severity = (marker.get("severity") if isinstance(marker, dict) else None) or ""
        tier = (marker.get("tier") if isinstance(marker, dict) else None) or ""
        domains = (marker.get("domains") if isinstance(marker, dict) else None) or []
        dom_text = " ".join(str(d) for d in domains).lower()

        is_hard_aspect = (".square." in low) or (".opposition." in low)
        is_soft_aspect = (".trine." in low) or (".sextile." in low) or (".conjunction." in low)

        if ("venus" in low or "jupiter" in low) and is_soft_aspect:
            rules.append("event_support:venus_jupiter_soft")
            support_sources.setdefault("event_support:venus_jupiter_soft", []).append(eid)
            support_base.setdefault("event_support:venus_jupiter_soft", 0.10)
        if "saturn" in low and sub == BeautySubIntent.reduce and is_soft_aspect:
            rules.append("event_support:saturn_reduce")
            support_sources.setdefault("event_support:saturn_reduce", []).append(eid)
            support_base.setdefault("event_support:saturn_reduce", 0.10)
        if "neptune" in low:
            if sub == BeautySubIntent.procedure:
                penalty += 0.10
                rules.append("event_penalty:neptune_procedure")
            elif sub == BeautySubIntent.nourish:
                rules.append("event_support:neptune_nourish")
                support_sources.setdefault("event_support:neptune_nourish", []).append(eid)
                support_base.setdefault("event_support:neptune_nourish", 0.05)

        if ("mars" in low or "chiron" in low) and is_hard_aspect:
            penalty += 0.30
            rules.append("event_penalty:mars_chiron_hard")

        if "injury" in dom_text or "risk" in dom_text or "bleeding" in dom_text:
            penalty += 0.20
            rules.append("event_penalty:risk_domain")
        if severity == "high" and tier == "main" and is_hard_aspect:
            penalty += 0.10
            rules.append("event_penalty:high_severity_hard")
    # Apply diminishing returns per support rule
    for rule_key, base_bonus in support_base.items():
        n = len(support_sources.get(rule_key) or [])
        if n <= 0:
            continue
        mult = 1.0 + 0.35 * max(0, n - 1)
        mult = min(mult, 1.7)
        support += base_bonus * mult

    return support, penalty, rules, support_sources


def _has_risk_signal(day: dict, event_ids: list[str], marker_index: dict[str, dict[str, Any]] | None) -> bool:
    text = " ".join(str(x) for x in (day.get("labels") or [])).lower()
    if any(w in text for w in RISK_LABEL_WORDS):
        return True
    for eid in event_ids or []:
        low = eid.lower()
        if ("mars" in low or "chiron" in low) and (".square." in low or ".opposition." in low):
            return True
        marker = marker_index.get(eid) if marker_index else None
        if isinstance(marker, dict):
            domains = marker.get("domains") or []
            dom_text = " ".join(str(d) for d in domains).lower()
            if "injury" in dom_text or "risk" in dom_text or "bleeding" in dom_text:
                return True
    return False


def _normalize_aspect(marker: dict[str, Any]) -> str | None:
    raw = (
        marker.get("aspect")
        or marker.get("aspect_name")
        or marker.get("aspect_type")
        or marker.get("aspectType")
    )
    if not raw:
        return None
    return _canonical_aspect(str(raw))


def _canonical_aspect(value: str | None) -> str | None:
    if not value:
        return None
    v = value.strip().lower()
    if v in ("conj", "conjunction"):
        return "conjunction"
    if v in ("opp", "opposition"):
        return "opposition"
    if v in ("sq", "square"):
        return "square"
    if v in ("tri", "trine"):
        return "trine"
    if v in ("sex", "sextile"):
        return "sextile"
    return v


def _aspect_from_event_id(event_id: str) -> str | None:
    if not event_id or not event_id.startswith("tr."):
        return None
    parts = event_id.split(".")
    if len(parts) >= 3:
        return _canonical_aspect(parts[2])
    return None


def _normalize_orb(marker: dict[str, Any]) -> float | None:
    for key in ("orb", "orb_deg", "orbDegrees"):
        val = marker.get(key)
        if isinstance(val, (int, float)):
            return float(val)
    val = marker.get("orbMinutes")
    if isinstance(val, (int, float)):
        return float(val) / 60.0
    return None


def resolve_event_summary(
    event_id: str,
    marker_index: dict[str, dict[str, Any]],
    events: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    marker = marker_index.get(event_id)
    if marker is None and events:
        ev = next(
            (
                e
                for e in events
                if isinstance(e, dict)
                and (e.get("id") == event_id or e.get("event_id") == event_id)
            ),
            None,
        )
        if ev:
            marker_id = ev.get("marker_id") or ev.get("id")
            if marker_id:
                marker = marker_index.get(marker_id) or marker_index.get(ev.get("event_id") or "")

    if event_id.startswith("phase."):
        kind = "phase"
    elif event_id.startswith("tr."):
        kind = "transit"
    else:
        kind = None

    if not isinstance(marker, dict):
        aspect = _aspect_from_event_id(event_id)
        return {
            "kind": kind,
            "label": None,
            "bodies": [],
            "aspect": aspect,
            "orb": None,
            "severity": None,
            "tier": None,
            "domains": [],
            "critical_reason": None,
        }

    aspect = _normalize_aspect(marker) or _aspect_from_event_id(event_id)
    orb = _normalize_orb(marker)

    return {
        "kind": kind or marker.get("kind"),
        "label": marker.get("label"),
        "bodies": marker.get("bodies") or [],
        "aspect": aspect,
        "orb": orb,
        "severity": marker.get("severity"),
        "tier": marker.get("tier"),
        "domains": marker.get("domains") or [],
        "critical_reason": marker.get("critical_reason"),
    }


def score_to_rating_beauty(score: float) -> int:
    if score < 0.20:
        return 0
    if score < 0.45:
        return 1
    if score < 0.70:
        return 2
    return 3


def bound_beauty_rating(sub: BeautySubIntent, beauty_rating: int, base_rating: int) -> int:
    base_rating = int(base_rating)
    if sub == BeautySubIntent.procedure:
        return min(beauty_rating, base_rating)
    return min(beauty_rating, max(base_rating, 1))


def apply_missing_enrichment(day_payload: dict, rating: int) -> tuple[int, str, list[str]]:
    missing: list[str] = []
    confidence = "high"

    if day_payload.get("moon_sign") is None:
        missing.append("moon_sign")
        confidence = "low"
        rating = max(0, rating - 1)

    return rating, confidence, missing


def cap_rating_for_missing(sub: BeautySubIntent, rating: int, missing: list[str]) -> int:
    if "moon_sign" not in missing:
        return rating
    if sub == BeautySubIntent.procedure:
        return min(rating, 1)
    return min(rating, 2)


BEAUTY_RISK_EVENTS = {
    "tr.mars.square.chiron",
    "tr.moon.square.mars",
    "tr.moon.square.saturn",
    "tr.sun.square.mars",
    "tr.sun.square.chiron",
}


def has_beauty_risk(event_ids: list[str]) -> bool:
    s = set(event_ids or [])
    return any(e in s for e in BEAUTY_RISK_EVENTS)


def apply_risk_policy(sub: BeautySubIntent, rating: int, event_ids: list[str]) -> int:
    if not has_beauty_risk(event_ids):
        return rating
    if sub == BeautySubIntent.procedure:
        return min(rating, 1)
    return max(0, rating - 1)


def beauty_recommendation(
    sub: BeautySubIntent, rating: int, labels: list[str] | None = None
) -> str:
    labels = labels or []

    if rating == 0:
        if sub == BeautySubIntent.procedure:
            return "Bugün profesyonel işlem için uygun görünmüyor; tempoyu düşür, dinlenme ve toparlama iyi gelir."
        return "Bugün yoğun uygulamalar yerine hafif bakım ve toparlama daha uygun. Rutini sade tut."

    if rating == 1:
        if sub == BeautySubIntent.reduce:
            return "Hafif toparlama iyi gelir: uyku, su, kısa yürüyüş, soğuk-kompres gibi nazik adımlar."
        return "Hafif bakım için uygun; rutini sade tut, cildi yormadan ilerle."

    if rating == 2:
        if sub == BeautySubIntent.reduce:
            return "Toparlama için iyi bir gün; şişlik/ödem odağında nazik bir rutin seç."
        return "Bakım için iyi; nem ve bariyer odağında düzenli ilerleyebilirsin."

    if sub == BeautySubIntent.reduce:
        return "Toparlama için güçlü bir gün; nazik ama etkili bir rutinle destekle."
    return "Bakım için güçlü bir gün; planladığın hafif bakımı rahatça yapabilirsin."


def best_times_from_calendar_payload(
    payload: dict,
    intent: str,
    sub_intent: str | None = None,
    body_area: str | None = None,
    top: int = 5,
    window: int = 3,
    debug: bool = False,
):
    sub_intent = sub_intent or payload.get("sub_intent")
    resolved_sub = resolve_sub_intent(sub_intent) if intent == "beauty_care" else None
    if intent == "beauty_care":
        rule_key = f"beauty_care_{resolved_sub.value}"
    else:
        rule_key = intent
    rules = INTENT_RULES.get(rule_key)
    if rules is None and intent == "beauty_care":
        # default fallback when sub_intent not provided
        rules = INTENT_RULES.get("beauty_care_nourish")
    if rules is None:
        return {"intent": intent, "sub_intent": sub_intent, "tz": _get_tz_from_payload(payload), "windows": [], "candidates": []}
    tz = payload.get("range", {}).get("tz", "UTC")

    marker_index: Dict[str, Dict[str, Any]] = {}
    day_index: Dict[str, Dict[str, Any]] = {}
    if intent == "beauty_care":
        markers = payload.get("markers") or []
        marker_index = {
            (m.get("event_id") or m.get("id")): m
            for m in markers
            if isinstance(m, dict) and (m.get("event_id") or m.get("id"))
        }
    if debug:
        markers = payload.get("markers") or []
        marker_index = {
            (m.get("event_id") or m.get("id")): m
            for m in markers
            if isinstance(m, dict) and (m.get("event_id") or m.get("id"))
        }
        for d in (payload.get("days") or []):
            if isinstance(d, dict) and d.get("date"):
                day_index[str(d["date"])] = d

        def _why_for_day(date_str: str) -> List[str]:
            d = day_index.get(date_str) or {}
            out: List[str] = []
            mp = d.get("moon_phase")
            if mp:
                out.append(f"Ay fazı: {mp}")
            ms = d.get("moon_sign")
            if ms:
                out.append(f"Ay burcu: {ms}")
            else:
                out.append("Ay burcu bilinmiyor (enrichment eksik)")
            return out[:3]

        events_payload = payload.get("events") or payload.get("raw_events") or []

        def _resolve_event(event_id: str) -> Dict[str, Any]:
            summary = resolve_event_summary(event_id, marker_index, events_payload)
            return {
                "id": event_id,
                "event_id": event_id,
                "label": summary.get("label"),
                "kind": summary.get("kind"),
                "tier": summary.get("tier"),
                "severity": summary.get("severity"),
                "domains": summary.get("domains"),
                "bodies": summary.get("bodies"),
                "aspect": summary.get("aspect"),
                "orb": summary.get("orb"),
                "critical_reason": summary.get("critical_reason"),
            }

    results = []
    daily_hint_days: list[dict] = []

    for day in payload.get("days", []):
        why: list[str] = []
        score = 0.0
        critical_reasons: list[str] = []

        flags = day.get("flags", {})

        blocked = False
        if rules["hard_blocks"].get("venus_retro") and flags.get("venus_retro"):
            blocked = True
        if rules["hard_blocks"].get("mars_retro") and flags.get("mars_retro"):
            blocked = True
        if rules["hard_blocks"].get("eclipse_window") and flags.get("eclipse"):
            blocked = True

        event_ids_before, event_ids, event_source = _extract_event_ids_with_source(day, intent)

        phase = day.get("moon_phase")
        why.append(f"Ay fazı: {phase}")

        moon_sign = day.get("moon_sign")
        element = day.get("moon_element") or _moon_element_from_sign(moon_sign)
        if moon_sign and element:
            why.append(f"Ay {moon_sign} ({element})")
        else:
            why.append("Ay burcu bilinmiyor (enrichment eksik)")

        area_penalty = 0.0
        if intent == "beauty_care" and resolved_sub == BeautySubIntent.procedure and body_area:
            area = BODY_MAP.get(body_area)
            if area:
                if moon_sign in area["ruled_by"] or moon_sign in area["opposite"]:
                    area_penalty = 0.20
                    why.append("⚠︎ Ay işlem bölgesini yönetiyor")

        if flags.get("moon_voc"):
            why.append("Ay boşlukta")
        if flags.get("moon_square_mars"):
            why.append("Ay–Mars sert açı")
        if flags.get("moon_square_saturn"):
            why.append("Ay–Satürn sert açı")

        sub = resolved_sub or BeautySubIntent.nourish if intent == "beauty_care" else None
        base_day_rating = int(day.get("rating") or 0)
        risk_signal = False
        base_norm = max(0.0, min(1.0, base_day_rating / 3.0))
        if sub == BeautySubIntent.nourish:
            base_component = base_norm * 0.45
        elif sub == BeautySubIntent.reduce:
            base_component = base_norm * 0.40
        elif sub == BeautySubIntent.procedure:
            base_component = base_norm * 0.55
        else:
            base_component = 0.0

        phase_modifier = _phase_modifier(sub, phase) if sub else 0.0
        moon_element_modifier = _element_modifier(sub, element) if sub else 0.0

        event_support = 0.0
        event_penalty = 0.0
        rules_from_events: list[str] = []
        support_sources: dict[str, list[str]] = {}
        if intent == "beauty_care":
            event_support, event_penalty, rules_from_events, support_sources = _event_signal_score(
                sub, event_ids, marker_index
            )

        missing_penalty = 0.0
        if intent == "beauty_care":
            if not moon_sign:
                missing_penalty = 0.20 if sub == BeautySubIntent.procedure else 0.10

        score = (
            base_component
            + phase_modifier
            + moon_element_modifier
            + event_support
            - event_penalty
            - missing_penalty
            - area_penalty
        )
        score = max(0.0, min(1.0, score))

        critical_reasons = list(day.get("critical_reason") or [])
        if not critical_reasons:
            if flags.get("moon_voc"):
                critical_reasons.append("void_of_course")
            if flags.get("moon_square_mars"):
                critical_reasons.append("hard_mars")
            if flags.get("moon_square_saturn"):
                critical_reasons.append("hard_saturn")

        if intent == "beauty_care":
            risk_signal = _has_risk_signal(day, event_ids, marker_index)
            if risk_signal and "risk_signal" not in critical_reasons:
                critical_reasons.append("risk_signal")

        is_critical = bool(day.get("is_critical")) or bool(critical_reasons)
        if is_critical and not critical_reasons:
            critical_reasons.append("critical")

        raw_gates = [f"gate:critical:{r}" for r in (critical_reasons or []) if r]
        if risk_signal:
            raw_gates.append("gate:injury_risk")
            if sub == BeautySubIntent.procedure:
                raw_gates.append("gate:procedure_block")
        if blocked:
            raw_gates.append("gate:procedure_block" if sub == BeautySubIntent.procedure else "gate:injury_risk")

        if intent == "beauty_care":
            base_rating = score_to_rating_beauty(score)
            final_rating = int(base_rating)

            if sub == BeautySubIntent.procedure and base_day_rating == 0:
                final_rating = 0
            elif sub in (BeautySubIntent.nourish, BeautySubIntent.reduce) and base_day_rating == 0:
                final_rating = min(final_rating, 1)

            if not moon_sign:
                final_rating = min(final_rating, 1)
            if day.get("moon_sign_changes_today"):
                if sub == BeautySubIntent.procedure:
                    final_rating = min(final_rating, 1)
                else:
                    final_rating = min(final_rating, 2)

            if is_critical or risk_signal:
                final_rating = min(final_rating, 1)
                if sub == BeautySubIntent.procedure:
                    score = min(score, 0.35)
                else:
                    score = min(score, 0.49)

            if sub == BeautySubIntent.procedure and risk_signal:
                final_rating = 0
                score = min(score, 0.35)
            if blocked:
                final_rating = 0
                score = 0.0

            day["why"] = why
            candidate = build_beauty_candidate_output(
                day,
                sub=sub,
                score=score,
                base_rating=base_rating,
                final_rating=final_rating,
                raw_gates=raw_gates,
                event_ids=event_ids,
                event_summaries=None,
                support_sources=support_sources,
                rules_fired=None,
                debug=False,
            )
        else:
            candidate = {
                "date": day["date"],
                "score": round(score, 3),
                "rating": score_to_rating(score),
                "why": why,
                "event_ids": event_ids,
            }
        if debug:
            max_events_per_day = 6
            event_ids_after = event_ids
            base_rating = int(candidate.get("base_rating") or 0)
            final_rating = int(candidate.get("final_rating") or candidate.get("rating") or 0)
            final_score = float(candidate.get("score") or score)
            score_breakdown = {
                "base_day_rating": int(day.get("rating") or 0),
                "base_rating": base_rating,
                "base_component": round(base_component, 3),
                "phase_modifier": round(phase_modifier, 3),
                "moon_element_modifier": round(moon_element_modifier, 3),
                "event_support": round(event_support, 3),
                "event_penalty": round(event_penalty, 3),
                "missing_penalty": round(missing_penalty, 3),
                "hard_blocks_applied": [f"gate:critical:{r}" for r in (critical_reasons or [])],
                "final_score": round(final_score, 3),
                "final_rating": final_rating,
            }

            rules_fired: List[str] = []
            if phase:
                rules_fired.append(f"phase:{phase}")
            if not moon_sign:
                rules_fired.append("missing:moon_sign")
            if flags.get("moon_voc"):
                rules_fired.append("penalty:moon_voc")
            if flags.get("moon_square_mars"):
                rules_fired.append("penalty:moon_square_mars")
            if flags.get("moon_square_saturn"):
                rules_fired.append("penalty:moon_square_saturn")
            rules_fired.extend(rules_from_events)
            if bool(day.get("is_critical")) or bool(critical_reasons):
                rules_fired.append("gate:critical")
            if base_rating == 0:
                rules_fired.append("gate:base_rating_0")
            if risk_signal:
                rules_fired.append("gate:risk_signal")

            rules_fired_counts: Dict[str, int] = {}
            for r in rules_fired:
                rules_fired_counts[r] = rules_fired_counts.get(r, 0) + 1
            # de-dup for display
            rules_fired_unique = list(dict.fromkeys(rules_fired))

            event_summaries: Dict[str, Dict[str, Any]] = {}
            for eid in event_ids_after:
                summary = resolve_event_summary(eid, marker_index, events_payload)
                event_summaries[eid] = summary
            if intent == "beauty_care":
                candidate = build_beauty_candidate_output(
                    day,
                    sub=sub,
                    score=final_score,
                    base_rating=base_rating,
                    final_rating=final_rating,
                    raw_gates=raw_gates,
                    event_ids=event_ids_after,
                    event_summaries=event_summaries,
                    support_sources=support_sources,
                    rules_fired=rules_fired_unique[:10],
                    debug=True,
                    score_breakdown=score_breakdown,
                )
                candidate["_debug"]["picked_event_source"] = event_source
                candidate["_debug"]["event_ids_before_filter"] = event_ids_before
                candidate["_debug"]["event_ids_after_filter"] = event_ids_after
                candidate["_debug"]["max_events_per_day"] = max_events_per_day
                candidate["rules_fired_counts"] = rules_fired_counts
                candidate["support_sources"] = support_sources
                candidate["critical_reason"] = critical_reasons
            else:
                candidate["_debug"] = {
                    "picked_event_source": event_source,
                    "event_ids_before_filter": event_ids_before,
                    "event_ids_after_filter": event_ids_after,
                    "max_events_per_day": max_events_per_day,
                }
                candidate["score_breakdown"] = score_breakdown
                candidate["rules_fired"] = rules_fired_unique[:10]
                candidate["rules_fired_counts"] = rules_fired_counts
                candidate["support_sources"] = support_sources
                candidate["event_summaries"] = event_summaries
                candidate["critical_reason"] = critical_reasons

        results.append(candidate)
        if intent == "beauty_care":
            action_type = candidate.get("action_type") or "care"
            gates_normalized = normalize_gates(raw_gates)
            if action_type == "procedure" and final_rating <= 0:
                one_liner = "Bugün işlem için uygun değil."
            elif action_type == "change":
                one_liner = "Bugün değişim için ideal." if final_rating >= 3 else "Bugün değişim yapılabilir."
            else:
                if "phase_shift" in gates_normalized:
                    one_liner = "Bugün ayar günü; hafif dokunuş daha iyi."
                elif "event_peak" in gates_normalized:
                    one_liner = "Enerji yoğun; sade ilerle."
                elif final_rating <= 0:
                    one_liner = "Bugün ertelemek daha iyi."
                elif final_rating == 1:
                    one_liner = "Bugün hafif dokunuş daha iyi."
                else:
                    one_liner = "Bugün toparlama/bakım iyi çalışır."
            daily_hint_days.append(
                {
                    "date": day.get("date"),
                    "final_rating": int(final_rating),
                    "action_type": action_type,
                    "one_liner": one_liner,
                }
            )

    results.sort(key=lambda x: x["score"], reverse=True)

    top_candidates = results[:top]
    def _parse_date(s: str):
        y, m, d = map(int, s.split("-"))
        return date(y, m, d)

    def _build_windows_from_clusters(
        candidates: list[dict],
        min_rating: int = 2,
        max_windows: int = 2,
        gap_tolerance_days: int = 0,
    ):
        good = [c for c in candidates if int(c.get("rating", 0)) >= min_rating]
        good.sort(key=lambda x: x["date"])

        clusters = []
        cur = []
        for c in good:
            if not cur:
                cur = [c]
                continue
            prev = _parse_date(cur[-1]["date"])
            now = _parse_date(c["date"])
            if now <= prev + timedelta(days=1 + gap_tolerance_days):
                cur.append(c)
            else:
                clusters.append(cur)
                cur = [c]
        if cur:
            clusters.append(cur)

        def agg(cluster):
            scores = [float(x.get("score", 0)) for x in cluster]
            ratings = [int(x.get("rating", 0)) for x in cluster]
            days = [x["date"] for x in cluster]
            return {
                "start": cluster[0]["date"],
                "end": cluster[-1]["date"],
                "days": days,
                "avg_score": round(sum(scores) / max(1, len(scores)), 3),
                "avg_rating": round(sum(ratings) / max(1, len(ratings)), 2),
                "count": len(cluster),
            }

        windows = [agg(cl) for cl in clusters]
        windows.sort(key=lambda w: (w["avg_rating"], w["avg_score"], w["count"]), reverse=True)
        return windows[:max_windows]

    if intent == "beauty_care":
        min_rating = 2 if resolved_sub == BeautySubIntent.procedure else 1
        gap_tolerance = 1 if resolved_sub in (BeautySubIntent.nourish, BeautySubIntent.reduce) else 0
    else:
        min_rating = 2
        gap_tolerance = 0
    windows = _build_windows_from_clusters(
        top_candidates,
        min_rating=min_rating,
        max_windows=2,
        gap_tolerance_days=gap_tolerance,
    )

    result: Dict[str, Any] = {
        "intent": intent,
        "sub_intent": resolved_sub.value if resolved_sub else sub_intent,
        "tz": tz,
        "windows": windows,
        "candidates": top_candidates,
    }
    if intent == "beauty_care":
        result["daily_hint"] = {"days": daily_hint_days}

    if debug:
        enriched: List[Dict[str, Any]] = []
        for c in (result.get("candidates") or []):
            if not isinstance(c, dict):
                continue
            cc = dict(c)
            if cc.get("date"):
                cc["why"] = _why_for_day(str(cc["date"]))
            eids = cc.get("event_ids") or []
            resolved = [_resolve_event(eid) for eid in eids if isinstance(eid, str)]
            cc["events"] = resolved
            enriched.append(cc)
        result["candidates"] = enriched

        kind_set: set[str] = set()
        markers_for_kinds = list(marker_index.values()) if marker_index else (payload.get("markers") or [])
        for m in markers_for_kinds:
            if not isinstance(m, dict):
                continue
            kind = m.get("kind")
            if not kind:
                eid = m.get("event_id") or m.get("id") or ""
                if eid.startswith("tr."):
                    kind = "transit"
                elif eid.startswith("phase."):
                    kind = "phase"
            if kind:
                kind_set.add(str(kind))

        ephemeris_provider = None
        ephemeris_version = None
        try:
            import swisseph as swe  # type: ignore

            ephemeris_provider = "swisseph"
            ephemeris_version = getattr(swe, "__version__", None) or getattr(swe, "swe_version", None)
            if callable(ephemeris_version):
                ephemeris_version = ephemeris_version()
        except Exception:
            ephemeris_provider = None
            ephemeris_version = None

        result["_debug_calendar"] = {
            "internal_has_days": bool(payload.get("days")),
            "days_count": len(payload.get("days") or []),
            "sample_day_keys": sorted(list((payload.get("days") or [{}])[0].keys()))[:60] if (payload.get("days") or []) else [],
            "sample_moon_phase": (payload.get("days") or [{}])[0].get("moon_phase") if (payload.get("days") or []) else None,
            "sample_moon_sign": (payload.get("days") or [{}])[0].get("moon_sign") if (payload.get("days") or []) else None,
            "has_markers": bool(payload.get("markers")),
            "has_items_map_raw": bool(payload.get("items_map_raw")),
            "markers_kinds_top": sorted(kind_set)[:10],
            "calculation_timestamp_utc": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
            "day_sample_time_local": "12:00",
            "ephemeris_provider": ephemeris_provider,
            "ephemeris_version": ephemeris_version,
        }

    return result


def build_beauty_intent_output(intent_payload: dict, base_calendar_by_date: dict) -> dict:
    sub = resolve_sub_intent(intent_payload.get("sub_intent"))
    tz = intent_payload.get("tz", "Europe/Istanbul")

    out_days = []
    for cand in intent_payload.get("candidates", []):
        d = cand.get("date")
        base_rating = int((base_calendar_by_date.get(d, {}) or {}).get("rating", 1))

        score = float(cand.get("score", 0.0))
        rating = score_to_rating_beauty(score)

        rating, confidence, missing = apply_missing_enrichment(cand, rating)
        rating = cap_rating_for_missing(sub, rating, missing)
        rating = apply_risk_policy(sub, rating, cand.get("event_ids", []))
        rating = bound_beauty_rating(sub, rating, base_rating)

        rec = beauty_recommendation(sub, rating, cand.get("why", []))

        out_days.append(
            {
                "date": d,
                "score": round(score, 3),
                "rating": rating,
                "confidence": confidence,
                "missing": missing,
                "why": cand.get("why", []),
                "event_ids": cand.get("event_ids", []),
                "recommendation": rec,
                "base_rating": base_rating,
            }
        )

    windows = _build_windows_from_clusters(out_days, min_rating=1, max_windows=2)

    return {
        "intent": "beauty_care",
        "sub_intent": sub.value,
        "tz": tz,
        "best_windows": windows,
        "days": out_days,
    }


def debug_beauty_trace(payload: dict, sub_intent: str | None = None) -> list[dict]:
    """
    Debug helper (no schema change): returns step-by-step rating transitions for beauty.
    """
    sub = resolve_sub_intent(sub_intent or payload.get("sub_intent"))
    out: list[dict] = []

    for day in payload.get("days", []) or []:
        event_ids = _extract_event_ids(day)
        score = float(day.get("score") or 0.0)
        raw_rating = score_to_rating_beauty(score)
        base_rating = int(day.get("rating") or 0)

        rating = bound_beauty_rating(sub, raw_rating, base_rating)
        rating_after_missing, confidence, missing = apply_missing_enrichment(day, rating)
        rating_after_cap = cap_rating_for_missing(sub, rating_after_missing, missing)
        if "moon_sign" in missing and sub in (BeautySubIntent.nourish, BeautySubIntent.reduce) and rating_after_cap == 0:
            rating_after_cap = 1
        rating_after_risk = apply_risk_policy(sub, rating_after_cap, event_ids)

        out.append(
            {
                "date": day.get("date"),
                "score": score,
                "raw_rating": raw_rating,
                "after_missing": rating_after_missing,
                "after_cap": rating_after_cap,
                "after_risk": rating_after_risk,
                "final_rating": rating_after_risk,
                "confidence": confidence,
                "missing": missing,
                "base_day_rating": base_rating,
            }
        )
    return out


def build_windows(candidates: list[dict], window_size: int = 3, top: int = 3):
    c_sorted = sorted(candidates, key=lambda x: x["date"])
    windows = []

    for i in range(0, len(c_sorted) - window_size + 1):
        chunk = c_sorted[i:i + window_size]
        avg_score = sum(x["score"] for x in chunk) / window_size
        avg_rating = round(sum(x["rating"] for x in chunk) / window_size)
        windows.append(
            {
                "start": chunk[0]["date"],
                "end": chunk[-1]["date"],
                "avg_score": round(avg_score, 4),
                "avg_rating": int(avg_rating),
            }
        )

    windows.sort(key=lambda w: w["avg_score"], reverse=True)
    return windows[:top]
