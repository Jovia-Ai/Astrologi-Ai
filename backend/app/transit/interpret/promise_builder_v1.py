"""V1 rule-based natal promise builder."""
from __future__ import annotations


def build_promise_model(natal_snapshot: dict, claims_library: dict) -> dict:
    """
    V1: rule-based promise builder
    natal_snapshot: ASC, Sun, Moon, dominant houses, etc.
    """
    claims = {}
    themes = {
        "identity": {"score": 0.0, "claim_ids": []},
        "relationships": {"score": 0.0, "claim_ids": []},
        "career": {"score": 0.0, "claim_ids": []},
        "home": {"score": 0.0, "claim_ids": []},
        "inner": {"score": 0.0, "claim_ids": []},
        "mind": {"score": 0.0, "claim_ids": []},
    }

    asc_sign = natal_snapshot.get("asc_sign")
    sun_house = natal_snapshot.get("sun_house")
    moon_house = natal_snapshot.get("moon_house")
    saturn_house = natal_snapshot.get("saturn_house")
    neptune_house = natal_snapshot.get("neptune_house")
    pluto_house = natal_snapshot.get("pluto_house")

    if asc_sign in ["Capricorn", "Virgo", "Scorpio"]:
        claims["claim.identity.core"] = claims_library.get("claim.identity.core")
        themes["identity"]["score"] += 0.6

    if sun_house in [1, 10]:
        claims["claim.identity.control_need"] = claims_library.get("claim.identity.control_need")
        themes["identity"]["score"] += 0.4

    if moon_house in [4, 8, 12]:
        claims["claim.inner.escape"] = claims_library.get("claim.inner.escape")
        themes["inner"]["score"] += 0.4

    if saturn_house in [1, 4, 7, 10]:
        claims["claim.career.authority"] = claims_library.get("claim.career.authority")
        themes["career"]["score"] += 0.5

    if neptune_house in [4, 7, 12]:
        claims["claim.relationships.idealization"] = claims_library.get(
            "claim.relationships.idealization"
        )
        themes["relationships"]["score"] += 0.35

    if pluto_house in [1, 8, 12]:
        claims["claim.identity.core"] = claims_library.get("claim.identity.core")
        themes["identity"]["score"] += 0.25

    claims = {k: v for k, v in claims.items() if v}

    for claim_id, claim in claims.items():
        domain = claim.get("domain")
        if domain in themes:
            themes[domain]["claim_ids"].append(claim_id)
            themes[domain]["score"] += float(claim.get("weight") or 0.0) * 0.1

    max_score = max((value["score"] for value in themes.values()), default=1.0)
    for value in themes.values():
        value["score"] = round(value["score"] / max_score, 3) if max_score else 0.0

    return {
        "promise_version": "promise.v1",
        "themes": themes,
        "claims": claims,
    }
