from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.helpers.normalize import normalize_planet_key, normalize_sign_key


@dataclass(frozen=True)
class Claim:
    domain: str
    slot: str
    signature: str
    meaning_key: str
    theme_tags: list[str]
    payload: dict[str, Any]
    salience: float
    source: dict[str, Any]


@dataclass(frozen=True)
class PhraseMapConfig:
    rulegroup_to_meaning: dict[str, str]
    placement_to_meaning: dict[tuple[str, str, int], str]
    meaning_to_tags: dict[str, list[str]]


def default_phrase_map_config() -> PhraseMapConfig:
    rulegroup_to_meaning = {
        "visibility_core": "visibility_need",
        "control_core": "control_need",
        "security_core": "security_need",
        "deep_feeling_core": "deep_feeling",
        "mind_core": "mind_system",
        "bond_core": "bond_need",
    }
    placement_to_meaning = {
        ("sun", "capricorn", 1): "control_need",
        ("moon", "leo", 8): "deep_feeling",
        ("mercury", "capricorn", 1): "mind_system",
        ("venus", "sagittarius", 5): "bond_need",
    }
    meaning_to_tags = {
        "visibility_need": ["visibility"],
        "control_need": ["control"],
        "security_need": ["security"],
        "deep_feeling": ["depth"],
        "mind_system": ["mind"],
        "bond_need": ["bond"],
    }
    return PhraseMapConfig(
        rulegroup_to_meaning=rulegroup_to_meaning,
        placement_to_meaning=placement_to_meaning,
        meaning_to_tags=meaning_to_tags,
    )


def infer_rule_group(rule_ids: list[str] | None) -> str | None:
    if not rule_ids:
        return None
    rule_id = str(rule_ids[0] or "").strip().lower()
    if not rule_id:
        return None
    if "_in_" in rule_id:
        prefix = rule_id.split("_in_", 1)[0]
        return f"{prefix}_core"
    return rule_id


def infer_meaning_key(
    domain: str,
    slot: str,
    planet: str | None,
    sign: str | None,
    house: int | None,
    rule_group: str | None,
    cfg: PhraseMapConfig,
) -> str:
    if rule_group and rule_group in cfg.rulegroup_to_meaning:
        return cfg.rulegroup_to_meaning[rule_group]
    if planet and sign and house is not None:
        lookup = (planet, sign, house)
        if lookup in cfg.placement_to_meaning:
            return cfg.placement_to_meaning[lookup]
    domain_key = domain.lower().strip()
    slot_key = slot.lower().strip()
    if domain_key == "identity" and slot_key == "mechanism":
        return "identity_core_mechanism"
    if domain_key == "psychology" and slot_key == "shadow":
        return "psychology_shadow"
    if domain_key == "relationships" and slot_key == "potential":
        return "relationships_potential"
    return f"{domain_key}_{slot_key}"


def build_claim(
    fragment: dict[str, Any],
    *,
    domain: str,
    slot: str,
    salience: float,
    cfg: PhraseMapConfig,
) -> Claim:
    trigger = fragment.get("trigger") or {}
    planet = normalize_planet_key(trigger.get("planet") or trigger.get("planet1") or fragment.get("planet"))
    sign = normalize_sign_key(trigger.get("sign") or fragment.get("sign"))
    house = trigger.get("house") if trigger.get("house") is not None else fragment.get("house")
    try:
        house_value = int(house) if house is not None else None
    except (TypeError, ValueError):
        house_value = None

    rule_ids = fragment.get("source_rule_ids") or fragment.get("rule_ids") or []
    rule_group = infer_rule_group(rule_ids)
    meaning_key = infer_meaning_key(domain, slot, planet, sign, house_value, rule_group, cfg)

    payload = _payload_for_meaning(meaning_key)
    theme_tags = cfg.meaning_to_tags.get(meaning_key, [])

    signature = _fragment_signature(domain, slot, fragment)
    source = {
        "rule_group": rule_group,
        "rule_ids": rule_ids,
        "planet": planet,
        "sign": sign,
        "house": house_value,
        "source_text": fragment.get("text"),
    }
    return Claim(
        domain=domain,
        slot=slot,
        signature=signature,
        meaning_key=meaning_key,
        theme_tags=theme_tags,
        payload=payload,
        salience=float(salience),
        source=source,
    )


def _payload_for_meaning(meaning_key: str) -> dict[str, Any]:
    if meaning_key == "visibility_need":
        return {
            "need": "gorulmek / fark edilmek",
            "inner": "gorunmek isteyen",
            "outer": "dikkat ceken",
        }
    if meaning_key == "control_need":
        return {
            "need": "kontrol / duzen",
            "strategy": "planli ve temkinli ilerleme",
        }
    if meaning_key == "security_need":
        return {
            "need": "guvende hissetmek",
            "strategy": "zemini garantiye almak",
        }
    return {
        "need": "temel ihtiyac",
        "strategy": "temkinli kalma",
        "experience": "icsel baski",
    }


def _fragment_signature(domain: str, slot: str, fragment: dict[str, Any]) -> str:
    trigger = fragment.get("trigger") or {}
    planet = normalize_planet_key(trigger.get("planet") or trigger.get("planet1") or fragment.get("planet"))
    sign = normalize_sign_key(trigger.get("sign") or fragment.get("sign"))
    house = trigger.get("house") if trigger.get("house") is not None else fragment.get("house")
    house_value = "" if house is None else str(house)
    rule_group = infer_rule_group(fragment.get("source_rule_ids") or fragment.get("rule_ids") or []) or ""
    return "|".join([domain, slot, planet, sign, house_value, rule_group])
