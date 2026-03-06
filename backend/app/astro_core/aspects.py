from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.models.chart_models import AspectHit, AspectName, ChartBody


ASPECTS: List[Tuple[AspectName, float, float]] = [
    ("conjunction", 0.0, 8.0),
    ("opposition", 180.0, 8.0),
    ("trine", 120.0, 7.0),
    ("square", 90.0, 7.0),
    ("sextile", 60.0, 5.0),
    ("quincunx", 150.0, 3.0),
]


def _angle_diff(a: float, b: float) -> float:
    d = abs((a - b) % 360.0)
    return 360.0 - d if d > 180.0 else d


def _orb_text(orb_deg: float) -> str:
    d = int(orb_deg)
    m = int(round((orb_deg - d) * 60.0))
    if m == 60:
        d += 1
        m = 0
    return f"{d}°{m:02d}′"


def _tightness(orb_deg: float, max_orb: float) -> float:
    if max_orb <= 0:
        return 0.0
    t = 1.0 - (orb_deg / max_orb)
    return max(0.0, min(1.0, t))


def compute_aspects(bodies: List[ChartBody], options: Dict[str, Any] | None = None) -> List[AspectHit]:
    # simple intra-chart aspects; cross-aspects later can reuse same function with concatenated lists + filtering
    out: List[AspectHit] = []
    n = len(bodies)
    for i in range(n):
        for j in range(i + 1, n):
            a = bodies[i]
            b = bodies[j]
            diff = _angle_diff(a.longitude, b.longitude)
            for name, exact, max_orb in ASPECTS:
                orb = abs(diff - exact)
                if orb <= max_orb:
                    out.append(
                        AspectHit(
                            a_body=a.body,
                            b_body=b.body,
                            aspect=name,
                            orb_deg=orb,
                            orb_text=_orb_text(orb),
                            tightness=_tightness(orb, max_orb),
                        )
                    )
                    break
    # sort tightest first
    out.sort(key=lambda x: x.orb_deg)
    return out

