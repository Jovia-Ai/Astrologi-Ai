from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Mapping

HOUSE_TO_DOMAIN = {
    1: "identity",
    2: "money",
    3: "mind",
    4: "home",
    5: "identity",
    6: "body",
    7: "relationships",
    8: "inner",
    9: "mind",
    10: "career",
    11: "career",
    12: "inner",
}


def _safe_int(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _body_rows(natal: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    bodies = natal.get("bodies")
    if isinstance(bodies, list):
        return [row for row in bodies if isinstance(row, Mapping)]
    if isinstance(bodies, Mapping):
        out: List[Mapping[str, Any]] = []
        for body, payload in bodies.items():
            if isinstance(payload, Mapping):
                row = dict(payload)
                row.setdefault("body", body)
                out.append(row)
        return out
    return []


def _label_to_domain(label: str) -> str:
    token = str(label or "").strip().lower().replace(" ", "_")
    if any(part in token for part in ("career", "visibility", "iş", "kariyer")):
        return "career"
    if any(part in token for part in ("relationship", "relations", "iliş", "partner")):
        return "relationships"
    if any(part in token for part in ("mind", "communication", "zihin", "konuş", "ileti")):
        return "mind"
    if any(part in token for part in ("home", "security", "ev", "güven")):
        return "home"
    if any(part in token for part in ("money", "value", "para", "değer")):
        return "money"
    if any(part in token for part in ("body", "rhythm", "sağlık", "rutin")):
        return "body"
    if any(part in token for part in ("inner", "depth", "iç", "derin")):
        return "inner"
    if any(part in token for part in ("identity", "self", "kimlik", "benlik")):
        return "identity"
    return ""


def extract_personalization_context(
    natal: Mapping[str, Any] | None,
    *,
    selected_day_context: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    natal_map = natal if isinstance(natal, Mapping) else {}
    day_context = selected_day_context if isinstance(selected_day_context, Mapping) else {}
    house_counter: Counter[int] = Counter()
    domain_counter: Counter[str] = Counter()

    for row in _body_rows(natal_map):
        house = _safe_int(row.get("house"))
        if house is None:
            continue
        house_counter[house] += 1
        domain = HOUSE_TO_DOMAIN.get(house)
        if domain:
            domain_counter[domain] += 1

    natal_hot_houses = [house for house, _count in house_counter.most_common(3)]
    dominant_domains = [domain for domain, _count in domain_counter.most_common(3)]

    labels = [str(label).strip() for label in (day_context.get("labels") or []) if str(label).strip()]
    behavioral_domains: List[str] = []
    for label in labels:
        domain = _label_to_domain(label)
        if domain and domain not in behavioral_domains:
            behavioral_domains.append(domain)

    raw_lens = str(day_context.get("lens") or "").strip()
    lens = _label_to_domain(raw_lens) or raw_lens.lower()
    if not lens and behavioral_domains:
        lens = behavioral_domains[0]

    return {
        "natal_hot_houses": natal_hot_houses,
        "dominant_domains": dominant_domains,
        "lens": lens,
        "behavioral_domains": behavioral_domains,
    }
