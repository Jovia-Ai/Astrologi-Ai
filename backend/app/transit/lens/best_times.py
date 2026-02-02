from __future__ import annotations

from typing import Any, Dict, List


def best_times_from_calendar_payload(
    calendar_payload: Dict[str, Any],
    intent: str,
    top: int = 10,
) -> Dict[str, Any]:
    markers = calendar_payload.get("markers", [])
    days = calendar_payload.get("days", [])

    marker_index = {m.get("id"): m for m in markers if m.get("id")}

    candidates: List[Dict[str, Any]] = []
    for day in days:
        date = day.get("date")
        marker_ids = day.get("marker_ids") or []
        best_score = -1.0
        best_marker = None

        for mid in marker_ids:
            mk = marker_index.get(mid)
            if not mk:
                continue
            score = float((mk.get("score_by_intent") or {}).get(intent, 0.0))
            if score > best_score:
                best_score = score
                best_marker = mk

        if best_marker and best_score > 0:
            evidence = best_marker.get("evidence") or {}
            candidates.append(
                {
                    "date": date,
                    "score": round(best_score, 3),
                    "marker_id": best_marker.get("id"),
                    "label": best_marker.get("label"),
                    "why": (evidence.get("rules") or [])[:3],
                    "event_ids": (evidence.get("event_ids") or [])[:3],
                }
            )

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return {"intent": intent, "candidates": candidates[:top]}
