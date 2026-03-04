from typing import Any, Dict

from app.astro.synastry.engine_v1 import SynastryEngineV1

DEFAULT_BODIES = [
    "sun",
    "moon",
    "mercury",
    "venus",
    "mars",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
    "node",
    "vertex",
    "asc",
    "mc",
]

engine = SynastryEngineV1()


def analyze_synastry(payload: Dict[str, Any]) -> Dict[str, Any]:
    partner_a = payload["partner_a"]
    partner_b = payload["partner_b"]

    A_pos = partner_a["chart"]["positions"]
    B_pos = partner_b["chart"]["positions"]

    include_debug = payload.get("options", {}).get("include_debug", False)

    res = engine.score(
        A_pos=A_pos,
        B_pos=B_pos,
        overlay_bonus=None,
        resonance=None,
        include_debug=include_debug,
        bodies=payload.get("options", {}).get("bodies", DEFAULT_BODIES),
    )

    public = {
        "scores": {
            "bond": round(res.categories["bond"].total * 100),
            "depth": round(res.categories["depth"].total * 100),
            "spark": round(res.categories["spark"].total * 100),
            "freedom": round(res.categories["freedom"].total * 100),
            "risk_index": round(res.risk_index * 100),
            "confidence": round(res.confidence * 100),
        },
        "drivers": {
            c: res.categories[c].top_drivers for c in ("bond", "depth", "spark", "freedom")
        },
    }

    out: Dict[str, Any] = {"engine_version": res.meta["engine"], "public": public}

    if include_debug:
        out["debug"] = res.debug

    return out
