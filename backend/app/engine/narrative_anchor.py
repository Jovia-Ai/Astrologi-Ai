from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

DOMAIN_ORDER = ["identity", "psychology", "relationships", "mind", "career", "karma"]


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _ensure_sentence(s: str) -> str:
    s = " ".join(str(s).strip().split())
    if not s:
        return ""
    if s[-1] not in ".!?":
        s += "."
    return s[0].upper() + s[1:]


def _extract_fragment_id(frag: Mapping[str, Any] | None) -> str:
    if not isinstance(frag, Mapping):
        return ""
    for k in ("fragment_id", "fragment_ref", "id"):
        v = frag.get(k)
        if v:
            return str(v)
    return ""


def _get_domain_entry(fragments_by_domain: Mapping[str, Any], domain: str) -> Mapping[str, Any] | None:
    entry = fragments_by_domain.get(domain)
    return entry if isinstance(entry, Mapping) else None


def _get_slots(entry: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if not isinstance(entry, Mapping):
        return {}
    slots = entry.get("slots")
    return slots if isinstance(slots, Mapping) else {}


def _get_slot(slots: Mapping[str, Any], name: str) -> Mapping[str, Any] | None:
    v = slots.get(name)
    return v if isinstance(v, Mapping) else None


def _slot_text(frag: Mapping[str, Any] | None) -> Optional[str]:
    if not isinstance(frag, Mapping):
        return None
    t = frag.get("text")
    if not t:
        return None
    s = " ".join(str(t).strip().split())
    return s or None


def _compose_anchor_sentence(cause: str | None, mechanism: str | None) -> str:
    cause = (cause or "").strip()
    mechanism = (mechanism or "").strip()

    if cause and mechanism:
        return _ensure_sentence(f"Genellikle, {cause} olduğunda, {mechanism} eğilimi belirir")
    if cause:
        return _ensure_sentence(f"Genellikle, {cause} olduğunda içsel bir hareketlenme artar")
    if mechanism:
        return _ensure_sentence(f"Genellikle, {mechanism} yöneliminde olursun")
    return ""


def build_narrative_anchor(
    *,
    fragments_by_domain: Mapping[str, Any],
    dominant_domain: str,
    meaning_weighting: Mapping[str, Any],
) -> Dict[str, Any]:
    """
    Returns minimal stable contract:

    {
      "domain": str,
      "theme": str|None,
      "anchor_slot": "cause"|"mechanism",
      "cause": str|None,
      "mechanism": str|None,
      "anchor_sentence": str,
      "source_fragment_ids": {"cause": str, "mechanism": str},
      "experienced_weight": float  # 0..1
    }
    """
    primary_theme = meaning_weighting.get("primary_theme")
    dom = (dominant_domain or "").strip().lower()

    def pick_domain() -> str:
        entry = _get_domain_entry(fragments_by_domain, dom) if dom else None
        slots = _get_slots(entry)
        if slots and (_get_slot(slots, "cause") or _get_slot(slots, "mechanism")):
            return dom

        for d in DOMAIN_ORDER:
            entry2 = _get_domain_entry(fragments_by_domain, d)
            slots2 = _get_slots(entry2)
            if slots2 and (_get_slot(slots2, "cause") or _get_slot(slots2, "mechanism")):
                return d

        return dom or "identity"

    domain = pick_domain()
    entry = _get_domain_entry(fragments_by_domain, domain)
    slots = _get_slots(entry)

    cause_frag = _get_slot(slots, "cause")
    mech_frag = _get_slot(slots, "mechanism")

    cause = _slot_text(cause_frag)
    mechanism = _slot_text(mech_frag)

    anchor_slot = "cause" if cause else ("mechanism" if mechanism else "cause")
    anchor_sentence = _compose_anchor_sentence(cause, mechanism)

    ew = 0.5
    if isinstance(cause_frag, Mapping) and cause_frag.get("experienced_weight") is not None:
        try:
            ew = float(cause_frag["experienced_weight"])
        except (TypeError, ValueError):
            ew = 0.5
    elif isinstance(mech_frag, Mapping) and mech_frag.get("experienced_weight") is not None:
        try:
            ew = float(mech_frag["experienced_weight"])
        except (TypeError, ValueError):
            ew = 0.5
    ew = _clamp01(ew)

    return {
        "domain": domain,
        "theme": str(primary_theme) if primary_theme else None,
        "anchor_slot": anchor_slot,
        "cause": cause,
        "mechanism": mechanism,
        "anchor_sentence": anchor_sentence,
        "source_fragment_ids": {
            "cause": _extract_fragment_id(cause_frag),
            "mechanism": _extract_fragment_id(mech_frag),
        },
        "experienced_weight": ew,
    }
