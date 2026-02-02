from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from .intent_rules import INTENT_RULES, IntentWeights


@dataclass(frozen=True)
class IntentDayScore:
    date: str
    score: float
    rating: int
    why: List[str]
    marker_count: int


def _rating_from_score(score: float) -> int:
    if score >= 0.45:
        return 5
    if score >= 0.30:
        return 4
    if score >= 0.18:
        return 3
    if score >= 0.08:
        return 2
    return 1


def _score_marker(marker: Dict[str, Any], rules: IntentWeights) -> tuple[float, List[str]]:
    score = 0.0
    why: List[str] = []

    flags = marker.get("flags") or {}
    bodies = marker.get("bodies") or []

    if "Venus" in bodies:
        score += rules.w_venus
        why.append("Venüs teması")
    if "Moon" in bodies:
        score += rules.w_moon
        why.append("Ay teması")
    if "Jupiter" in bodies:
        score += rules.w_jupiter
        why.append("Jüpiter teması")
    if "Neptune" in bodies:
        score += rules.w_neptune
        why.append("Neptün teması")
    if "Saturn" in bodies:
        score += rules.w_saturn
        why.append("Satürn teması")
    if "Mercury" in bodies:
        score += rules.w_mercury
        why.append("Merkür teması")

    if flags.get("venus_retro"):
        score -= rules.p_venus_retro
        why.append("Venüs retro")
    if flags.get("mars_retro"):
        score -= rules.p_mars_retro
        why.append("Mars retro")
    if flags.get("mercury_retro"):
        score -= rules.p_mercury_retro
        why.append("Merkür retro")
    if flags.get("eclipse"):
        score -= rules.p_eclipse
        why.append("Tutulma etkisi")
    if flags.get("moon_voc"):
        score -= rules.p_moon_voc
        why.append("Ay boşlukta (VOC)")

    if flags.get("moon_waxing"):
        score += rules.b_waxing
        why.append("Ay büyüyen faz")
    if flags.get("moon_waning"):
        score += rules.b_waning
        why.append("Ay küçülen faz")

    sev = marker.get("severity")
    if isinstance(sev, (int, float)):
        score += 0.04 * float(sev)

    why = list(dict.fromkeys(why))
    return score, why


def score_day_for_intent(
    intent: str,
    day: Dict[str, Any],
    marker_index: Dict[str, Dict[str, Any]],
    max_why: int = 5,
) -> IntentDayScore:
    rules = INTENT_RULES.get(intent)
    if rules is None:
        return IntentDayScore(
            date=str(day.get("date") or ""),
            score=0.0,
            rating=1,
            why=[],
            marker_count=0,
        )

    marker_ids = day.get("marker_ids") or day.get("markers") or []
    if not isinstance(marker_ids, list):
        marker_ids = []

    total = 0.0
    why_all: List[str] = []
    used = 0

    density = min(len(marker_ids), rules.density_cap)
    if density > 0:
        total += density * rules.density_bonus

    for mid in marker_ids:
        marker = marker_index.get(str(mid))
        if not marker:
            continue
        score, why = _score_marker(marker, rules)
        if score <= 0.0:
            continue
        total += score
        used += 1
        for w in why:
            if w not in why_all:
                why_all.append(w)

    rating = _rating_from_score(total)
    return IntentDayScore(
        date=str(day.get("date") or ""),
        score=round(total, 4),
        rating=rating,
        why=why_all[:max_why],
        marker_count=used,
    )


def score_month_payload_for_intent(
    intent: str,
    payload: Dict[str, Any],
    max_why: int = 5,
) -> List[IntentDayScore]:
    days = payload.get("days") or []
    markers = payload.get("markers") or []

    marker_index: Dict[str, Dict[str, Any]] = {}
    if isinstance(markers, list):
        for marker in markers:
            if isinstance(marker, dict) and marker.get("id"):
                marker_index[str(marker["id"])] = marker

    out: List[IntentDayScore] = []
    if isinstance(days, list):
        for day in days:
            if isinstance(day, dict):
                out.append(score_day_for_intent(intent, day, marker_index, max_why=max_why))
    return out


def build_best_windows(
    scored_days: List[IntentDayScore],
    window: int = 3,
    top_windows: int = 3,
) -> List[Dict[str, Any]]:
    if window <= 1:
        return []

    wins: List[tuple[float, int]] = []
    for i in range(0, max(0, len(scored_days) - window + 1)):
        chunk = scored_days[i:i + window]
        avg = sum(x.score for x in chunk) / float(window)
        wins.append((avg, i))

    wins.sort(key=lambda x: x[0], reverse=True)
    out: List[Dict[str, Any]] = []
    for avg, idx in wins[:top_windows]:
        chunk = scored_days[idx:idx + window]
        out.append(
            {
                "start": chunk[0].date,
                "end": chunk[-1].date,
                "avg_score": round(avg, 4),
                "avg_rating": int(round(sum(x.rating for x in chunk) / float(window))),
            }
        )
    return out
