"""Deterministic narrative planner for v2.6 templates."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from app.narrative.phrase_mapper import MappedItem


@dataclass(frozen=True)
class NarrativePlan:
    title: str
    tempo: str
    trait1: str
    trait2: str
    outer1: str
    outer2: str
    tension_pair: str
    tension_line: str
    inner_q1: str
    inner_q2: str
    mechanism_anchor: str
    growth_dir: str
    resource_anchor: str
    positive_outcome: str
    shadow_risk: str | None


def build_plan(domain: str, mapped_items: Sequence[MappedItem], *, title: str) -> NarrativePlan:
    items = list(mapped_items)
    tempo = _tempo_from_intents(items)
    traits = _top_intent_phrases(items, limit=2, fallback=("sakin", "kararli"))
    outer = _outer_intent_phrases(items, limit=2, fallback=("sakin", "kararli"))
    tension_pair = " / ".join(_tension_pair_intents(items))
    tension_line = _tension_line(items)
    inner_q1, inner_q2 = _inner_questions(items)
    mechanism_anchor = _mechanism_anchor(items)
    growth_dir = _intent_growth(items) or "daha stabil bir yone"
    resource_anchor = _resource_anchor(items) or "ic dayanagini"
    positive_outcome = _positive_outcome(items) or "denge"
    shadow_risk = _shadow_risk(items)

    return NarrativePlan(
        title=title,
        tempo=tempo,
        trait1=traits[0],
        trait2=traits[1],
        outer1=outer[0],
        outer2=outer[1],
        tension_pair=tension_pair,
        tension_line=tension_line,
        inner_q1=inner_q1,
        inner_q2=inner_q2,
        mechanism_anchor=mechanism_anchor,
        growth_dir=growth_dir,
        resource_anchor=resource_anchor,
        positive_outcome=positive_outcome,
        shadow_risk=shadow_risk,
    )


def _top_intent_phrases(
    items: Iterable[MappedItem],
    *,
    limit: int,
    fallback: tuple[str, str],
) -> list[str]:
    scored: dict[str, float] = {}
    for item in items:
        if item.intent == "generic":
            continue
        scored[item.intent] = max(scored.get(item.intent, 0.0), item.salience)
    ranked = sorted(scored.items(), key=lambda entry: entry[1], reverse=True)
    intents = [intent for intent, _score in ranked[:limit]]
    while len(intents) < limit:
        intents.append(fallback[len(intents)])
    return [_intent_to_trait(intent) for intent in intents]


def _outer_intent_phrases(
    items: Iterable[MappedItem],
    *,
    limit: int,
    fallback: tuple[str, str],
) -> list[str]:
    scored: dict[str, float] = {}
    for item in items:
        if item.voice != "outer_perception":
            continue
        intent = item.intent
        if not intent or intent == "generic":
            continue
        scored[intent] = max(scored.get(intent, 0.0), item.salience)
    ranked = sorted(scored.items(), key=lambda entry: entry[1], reverse=True)
    intents = [intent for intent, _score in ranked[:limit]]
    while len(intents) < limit:
        intents.append(fallback[len(intents)])
    return [_intent_to_trait(intent) for intent in intents]


def _inner_questions(items: Iterable[MappedItem]) -> tuple[str, str]:
    intents = {item.intent for item in items}
    questions: list[str] = []
    if "visibility" in intents:
        questions.append("beni gercekten goren var mi?")
    if "depth" in intents:
        questions.append("bu kadar hissetmem anlasilir mi?")
    if "worth" in intents:
        questions.append("yeterli miyim?")
    if not questions:
        questions = ["burada beni zorlayan ne", "nereye dogru akiyorum"]
    if len(questions) == 1:
        questions.append("icimde neyi yavaslatmaliyim")
    return questions[0], questions[1]


def _intent_to_trait(intent: str) -> str:
    mapping = {
        "visibility": "gorunur",
        "control": "kontrollu",
        "security": "guven arayan",
        "depth": "derin",
        "autonomy": "ozgur",
        "worth": "deger odakli",
    }
    return mapping.get(intent, "sakin")


def _tempo_from_intents(items: Iterable[MappedItem]) -> str:
    intents = {item.intent for item in items}
    if "visibility" in intents:
        return "gorunur"
    if "security" in intents:
        return "sakin"
    return "dengeli"


def _intent_growth(items: Iterable[MappedItem]) -> str:
    intents = {item.intent for item in items}
    if "visibility" in intents:
        return "gorunurluge"
    if "security" in intents:
        return "guvene"
    if "control" in intents:
        return "kontrollu bir akisa"
    return "daha olgun bir yone"


def _resource_anchor(items: Iterable[MappedItem]) -> str:
    intents = {item.intent for item in items}
    if "security" in intents:
        return "ic guvenine"
    if "control" in intents:
        return "ic duzenine"
    return "ic dengesine"


def _positive_outcome(items: Iterable[MappedItem]) -> str:
    intents = {item.intent for item in items}
    if "depth" in intents:
        return "yakinlik"
    if "worth" in intents:
        return "deger"
    return "denge"


def _tension_pair_intents(items: Iterable[MappedItem]) -> list[str]:
    scored: dict[str, float] = {}
    for item in items:
        if item.polarity != "tension":
            continue
        if item.intent == "generic":
            continue
        scored[item.intent] = max(scored.get(item.intent, 0.0), item.salience)
    if len(scored) < 2:
        return _top_intent_phrases(items, limit=2, fallback=("control", "visibility"))
    ranked = sorted(scored.items(), key=lambda entry: entry[1], reverse=True)
    intents = [intent for intent, _score in ranked[:2]]
    return [_intent_to_trait(intent) for intent in intents]


def _tension_line(items: Iterable[MappedItem]) -> str:
    for item in items:
        if item.polarity == "tension" and item.text:
            return item.text
    for item in items:
        if item.slot == "mechanism" and item.text:
            return item.text
    return "icte iki motivasyon yan yana durur"


def _mechanism_anchor(items: Iterable[MappedItem]) -> str:
    mechanisms = [item for item in items if item.slot == "mechanism"]
    if not mechanisms:
        return "istikrar kurma ve kontrolu elde tutma"
    top = max(mechanisms, key=lambda item: item.salience)
    return _intent_paraphrase(top.intent)


def _intent_paraphrase(intent: str) -> str:
    mapping = {
        "control": "istikrar kurma ve kontrolu elde tutma",
        "visibility": "gorunur olma ve degerinin fark edilmesi ihtiyaci",
        "security": "guven arayisi ve saglam zemin kurma",
        "depth": "derin bag ve yogun his",
    }
    return mapping.get(intent, "istikrar kurma ve kontrolu elde tutma")


def _shadow_risk(items: Iterable[MappedItem]) -> str | None:
    for item in items:
        if item.slot != "shadow":
            continue
        return _shadow_risk_sentence(item.intent)
    return None


def _shadow_risk_sentence(intent: str) -> str:
    mapping = {
        "worth": "kendi icinde celiski yaratabilir",
        "visibility": "iliskilerde gereksiz gerilime donebilir",
        "control": "kendi icinde celiski yaratabilir",
        "security": "iliskilerde gereksiz gerilime donebilir",
    }
    return mapping.get(intent, "kendi icinde celiski yaratabilir")
