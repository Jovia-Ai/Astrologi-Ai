from __future__ import annotations

from dataclasses import dataclass, asdict
from math import exp
from typing import Dict, List, Optional, Tuple

from .config_v1 import (
    ASPECT_DEGREES,
    ASPECT_COEFFS,
    BODY_WEIGHTS,
    BODY_FAMILY,
    ORB_MAX_DEFAULT,
    ORB_MAX_BY_PAIR_FAMILY,
    CATEGORY_MAP_FACTOR,
    RISK_RULES,
    K_BY_CATEGORY,
    K_BY_RISK,
    OUTER_OUTER_DAMP,
)

CATEGORIES = ("bond", "depth", "spark", "freedom")


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if x < lo else hi if x > hi else x


def norm360(x: float) -> float:
    x = x % 360.0
    return x + 360.0 if x < 0 else x


def ang_dist(a: float, b: float) -> float:
    d = abs(a - b) % 360.0
    return d if d <= 180.0 else 360.0 - d


def sat_score(sum_contrib: float, k: float) -> float:
    return 1.0 - exp(-k * max(0.0, sum_contrib))


def pair_family_key(a: str, b: str) -> str:
    fa = BODY_FAMILY.get(a, "other")
    fb = BODY_FAMILY.get(b, "other")
    x, y = sorted([fa, fb])
    return f"{x}_{y}"


def orb_max(a: str, b: str) -> float:
    fam_key = pair_family_key(a, b)
    return ORB_MAX_BY_PAIR_FAMILY.get(fam_key, ORB_MAX_DEFAULT)


def is_outer(body: str) -> bool:
    return BODY_FAMILY.get(body) == "outer"


def sorted_pair_key(a: str, b: str) -> Tuple[str, str]:
    return tuple(sorted([a, b]))  # type: ignore


def map_key(a: str, b: str, aspect: str) -> str:
    x, y = sorted_pair_key(a, b)
    return f"{x}_{y}_{aspect}"


@dataclass
class AspectHit:
    a_body: str
    b_body: str
    aspect: str
    orb_deg: float
    tightness: float
    intensity: float
    friction: float
    flow: float
    weight: float
    contrib: Dict[str, float]
    risk: Dict[str, float]


@dataclass
class CategoryScore:
    direct: float
    resonance: float
    overlay: float
    total: float
    risk: Dict[str, float]
    top_drivers: List[dict]
    signal: dict


@dataclass
class SynastryResult:
    categories: Dict[str, CategoryScore]
    risk_index: float
    confidence: float
    meta: dict
    debug: Optional[dict] = None


class SynastryEngineV1:
    def __init__(self):
        pass

    def scan_aspects(
        self,
        A_pos: Dict[str, float],
        B_pos: Dict[str, float],
        bodies: Optional[List[str]] = None,
    ) -> List[AspectHit]:
        bodies = bodies or list(A_pos.keys())
        hits: List[AspectHit] = []

        for a_body, a_lon in A_pos.items():
            if a_body not in bodies:
                continue
            a_lon = norm360(a_lon)

            for b_body, b_lon in B_pos.items():
                if b_body not in bodies:
                    continue
                b_lon = norm360(b_lon)

                d = ang_dist(a_lon, b_lon)
                orb_lim = orb_max(a_body, b_body)

                # closest aspect within orb
                best: Optional[Tuple[str, float]] = None
                for asp_name, asp_deg in ASPECT_DEGREES.items():
                    delta = abs(d - asp_deg)
                    if delta <= orb_lim:
                        if best is None or delta < best[1]:
                            best = (asp_name, delta)

                if not best:
                    continue

                asp_name, delta = best
                tight = clamp(1.0 - (delta / orb_lim))

                coeff = ASPECT_COEFFS[asp_name]
                w = 0.5 * (BODY_WEIGHTS.get(a_body, 0.5) + BODY_WEIGHTS.get(b_body, 0.5))

                # outer-outer damp (spam engeli)
                damp = OUTER_OUTER_DAMP if (is_outer(a_body) and is_outer(b_body)) else 1.0

                mk = map_key(a_body, b_body, asp_name)
                factors = CATEGORY_MAP_FACTOR.get(mk, {})

                contrib: Dict[str, float] = {c: 0.0 for c in CATEGORIES}
                for cat, factor in factors.items():
                    # kareyi "yogunluk" gibi normalize: intensity yuksek, friction ayrica risk kanalina gider
                    contrib[cat] += tight * coeff["intensity"] * w * factor * damp

                risk: Dict[str, float] = {
                    "depth_control": 0.0,
                    "spark_irrit": 0.0,
                    "freedom_instab": 0.0,
                }
                # risk rules
                if RISK_RULES["depth_control"].get(mk):
                    risk["depth_control"] += tight * coeff["friction"] * w * damp
                if RISK_RULES["spark_irrit"].get(mk):
                    risk["spark_irrit"] += tight * coeff["friction"] * w * damp
                if RISK_RULES["freedom_instab"].get(mk):
                    risk["freedom_instab"] += tight * coeff["friction"] * w * damp

                hits.append(
                    AspectHit(
                        a_body=a_body,
                        b_body=b_body,
                        aspect=asp_name,
                        orb_deg=delta,
                        tightness=tight,
                        intensity=coeff["intensity"],
                        friction=coeff["friction"],
                        flow=coeff["flow"],
                        weight=w * damp,
                        contrib=contrib,
                        risk=risk,
                    )
                )
        return hits

    def score(
        self,
        A_pos: Dict[str, float],
        B_pos: Dict[str, float],
        overlay_bonus: Optional[Dict[str, float]] = None,
        resonance: Optional[Dict[str, float]] = None,
        include_debug: bool = False,
        bodies: Optional[List[str]] = None,
    ) -> SynastryResult:
        overlay_bonus = overlay_bonus or {c: 0.0 for c in CATEGORIES}
        resonance = resonance or {c: 0.0 for c in CATEGORIES}

        hits = self.scan_aspects(A_pos, B_pos, bodies=bodies)

        sum_contrib = {c: 0.0 for c in CATEGORIES}
        sum_risk = {"depth_control": 0.0, "spark_irrit": 0.0, "freedom_instab": 0.0}

        for h in hits:
            for c in CATEGORIES:
                sum_contrib[c] += h.contrib.get(c, 0.0)
            for rk in sum_risk.keys():
                sum_risk[rk] += h.risk.get(rk, 0.0)

        direct = {c: sat_score(sum_contrib[c], K_BY_CATEGORY[c]) for c in CATEGORIES}
        risk_sc = {rk: sat_score(sum_risk[rk], K_BY_RISK[rk]) for rk in sum_risk.keys()}

        # total combine: direct + resonance + overlay (MVP)
        # Not: resonance/overlay su an 0 olabilir; sonra ekleyecegiz.
        categories: Dict[str, CategoryScore] = {}
        for c in CATEGORIES:
            total = clamp(
                0.78 * direct[c]
                + 0.12 * resonance.get(c, 0.0)
                + 0.10 * overlay_bonus.get(c, 0.0)
            )
            categories[c] = CategoryScore(
                direct=direct[c],
                resonance=resonance.get(c, 0.0),
                overlay=overlay_bonus.get(c, 0.0),
                total=total,
                risk=risk_sc,
                top_drivers=self._top_drivers(hits, c),
                signal=self._signal_quality(hits, c),
            )

        # risk_index: basit birlesim (sonra lens/adjust ile ayristiririz)
        risk_index = clamp(
            0.45 * risk_sc["depth_control"]
            + 0.35 * risk_sc["freedom_instab"]
            + 0.20 * risk_sc["spark_irrit"]
        )

        confidence = self._confidence(hits)

        meta = {
            "engine": "synastry_v1",
            "aspect_count": len(hits),
        }

        debug = None
        if include_debug:
            debug = {
                "sum_contrib": sum_contrib,
                "sum_risk_raw": sum_risk,
                "hits": [asdict(h) for h in hits[:120]],
            }

        return SynastryResult(
            categories=categories,
            risk_index=risk_index,
            confidence=confidence,
            meta=meta,
            debug=debug,
        )

    def _top_drivers(self, hits: List[AspectHit], cat: str, n: int = 5) -> List[dict]:
        scored = []
        for h in hits:
            v = h.contrib.get(cat, 0.0)
            if v <= 0:
                continue
            scored.append((v, h))
        scored.sort(key=lambda x: x[0], reverse=True)
        out = []
        for v, h in scored[:n]:
            out.append(
                {
                    "a": h.a_body,
                    "b": h.b_body,
                    "aspect": h.aspect,
                    "orb": round(h.orb_deg, 2),
                    "tightness": round(h.tightness, 3),
                    "contrib": round(v, 4),
                }
            )
        return out

    def _signal_quality(self, hits: List[AspectHit], cat: str) -> dict:
        vals = [h.contrib.get(cat, 0.0) for h in hits if h.contrib.get(cat, 0.0) > 0]
        tight = [h.tightness for h in hits if h.contrib.get(cat, 0.0) > 0]
        return {
            "drivers": len(vals),
            "avg_tightness": round(sum(tight) / len(tight), 3) if tight else 0.0,
            "dominance": round(max(vals) / (sum(vals) + 1e-9), 3) if vals else 0.0,
        }

    def _confidence(self, hits: List[AspectHit]) -> float:
        # MVP: coverage + tightness
        if not hits:
            return 0.0
        tight_avg = sum(h.tightness for h in hits) / len(hits)
        coverage = clamp(len(hits) / 18.0)
        return clamp(0.55 * tight_avg + 0.45 * coverage)
