from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def cluster_daily_experience_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    config: Mapping[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    _ = config
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for raw in rows:
        row = dict(raw)
        feature_vector = row.get("feature_vector") if isinstance(row.get("feature_vector"), Mapping) else {}
        redundancy = feature_vector.get("redundancy") if isinstance(feature_vector.get("redundancy"), Mapping) else {}
        key = str(redundancy.get("cluster_key") or row.get("redundancy_key") or row.get("event_id") or "").strip()
        if not key:
            key = str(row.get("event_id") or "")
        grouped.setdefault(key, []).append(row)

    out: List[Dict[str, Any]] = []
    for cluster_key, cluster_rows in grouped.items():
        ranked = sorted(
            cluster_rows,
            key=lambda row: (
                -_safe_float(row.get("score"), 0.0),
                -_safe_float((row.get("score_breakdown") or {}).get("today_score"), 0.0),
                str(row.get("event_id") or ""),
            ),
        )
        representative = dict(ranked[0])
        support_rows = [dict(row) for row in ranked[1:]]
        support_bonus = min(0.12, 0.05 * len(support_rows))
        support_today = 0.0
        if support_rows:
            support_today = sum(
                _safe_float((row.get("score_breakdown") or {}).get("today_score"), 0.0) for row in support_rows
            ) / len(support_rows)
        cluster_score = _safe_float(representative.get("score"), 0.0) + support_bonus + (0.08 * support_today)
        representative["cluster_key"] = cluster_key
        representative["cluster_score"] = round(cluster_score, 4)
        representative["cluster_size"] = len(cluster_rows)
        representative["cluster_support_event_ids"] = [
            str(row.get("event_id") or "")
            for row in support_rows
            if str(row.get("event_id") or "")
        ]
        out.append(
            {
                "cluster_key": cluster_key,
                "cluster_score": round(cluster_score, 4),
                "cluster_size": len(cluster_rows),
                "representative_row": representative,
                "support_rows": support_rows,
                "support_event_ids": representative["cluster_support_event_ids"],
            }
        )

    out.sort(
        key=lambda cluster: (
            -_safe_float(cluster.get("cluster_score"), 0.0),
            -int(cluster.get("cluster_size") or 0),
            str((cluster.get("representative_row") or {}).get("event_id") or ""),
        )
    )
    return out
