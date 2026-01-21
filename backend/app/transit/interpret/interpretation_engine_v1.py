import hashlib
from typing import Any, Dict, List, Tuple

from app.transit.interpret.canonical import canon_aspect, canonical_key
from app.transit.interpret.mechanism import build_mechanism_sentence
from app.transit.interpret.themes import pick_primary_theme
from app.transit.interpret.where import build_where_sentence


def _hash_int(value: str) -> int:
    return int(hashlib.sha1(value.encode("utf-8")).hexdigest(), 16)


def _pick_variant(seed: str, options: List[Any]) -> Any:
    if not options:
        return ""
    idx = _hash_int(seed) % len(options)
    return options[idx]


def _normalize_key(value: str) -> str:
    return str(value or "").strip().lower().replace(" ", "_")


class ContentStore:
    def __init__(self, templates: Dict, claims: Dict, mapping: Dict):
        self.templates = templates
        self.claims = claims
        self.mapping = mapping

    def resolve_template(
        self,
        transit: str,
        aspect: str,
        natal_point: str,
        polarity: str,
        theme: str,
    ):
        specific = canonical_key(transit, aspect, natal_point)
        specific_key = specific.lower()
        transit_any = canonical_key(transit, aspect, "ANY").lower()
        aspect_key = canon_aspect(aspect)
        polarity_key = _normalize_key(polarity)
        theme_key = _normalize_key(theme)
        keys = [
            specific_key,
            transit_any,
            f"{polarity_key}.{theme_key}.any",
            f"{aspect_key}.{polarity_key}.any",
            f"{polarity_key}.any",
            "generic.any",
        ]
        used_key = None
        block = {}
        for key in keys:
            if key in self.templates:
                used_key = key
                block = self.templates[key]
                break
        if used_key is None:
            used_key = "generic.any"
            block = self.templates.get("generic.any", {})
        if specific_key in self.templates and used_key != specific_key:
            used_key = specific_key
            block = self.templates[specific_key]
        return used_key, block, keys, specific_key in self.templates

    def has(self, key: str) -> bool:
        return key.lower() in self.templates

    def get(self, key: str) -> Dict[str, Any]:
        return self.templates.get(key.lower(), {})


def interpret_items(
    items: List[Dict[str, Any]],
    content: ContentStore,
    promise: Dict[str, Any] | None = None,
    mode: str = "context-lite",
) -> Tuple[List[Dict], Dict]:
    interpreted = []

    for item in items:
        event_id = item["event_id"]
        transit = item["transit_body"]
        aspect = item["aspect"]
        natal_point = item["natal_point"]
        polarity = item["polarity"]
        strength = float(item.get("strength") or 0.0)
        orb_deg = float(item.get("orb_deg") or 99.0)

        houses = item.get("houses") or {}
        angle_map = {"ASC": 1, "DSC": 7, "MC": 10, "IC": 4}
        natal_target_house = houses.get("natal_point_house")
        if natal_point in angle_map:
            natal_target_house = angle_map[natal_point]
        transit_house = houses.get("transit_in_natal_house")
        axis = None
        if isinstance(natal_target_house, int) and isinstance(transit_house, int):
            if natal_target_house != transit_house:
                axis = f"{min(natal_target_house, transit_house)}-{max(natal_target_house, transit_house)}"

        item_with_context = dict(item)
        item_with_context["context"] = {
            "natal_point": natal_point,
            "is_angle": _normalize_key(natal_point) in {"asc", "mc", "dsc", "ic"},
            "transit_in_natal_house": transit_house,
            "natal_house": houses.get("natal_point_house"),
            "natal_target_house": natal_target_house,
            "transit_house": transit_house,
            "axis": axis,
        }
        primary_theme = pick_primary_theme(item_with_context)
        template_key, template, fallback_chain, specific_exists = content.resolve_template(
            transit, aspect, natal_point, polarity, primary_theme
        )

        headline = _pick_variant(f"{event_id}:h", template.get("headline_variants", []))
        summary = _pick_variant(f"{event_id}:s", template.get("summary_variants", []))
        do_list = _pick_variant(f"{event_id}:d", template.get("do_variants", [])) or []
        watch_list = _pick_variant(f"{event_id}:w", template.get("watch_variants", [])) or []
        if isinstance(do_list, str):
            do_list = [do_list]
        if isinstance(watch_list, str):
            watch_list = [watch_list]
        do_list = _ensure_min_list(do_list, polarity, primary_theme, kind="do")
        watch_list = _ensure_min_list(watch_list, polarity, primary_theme, kind="watch")
        themes = template.get("themes", [])

        is_high_intensity = strength >= 0.75 or orb_deg <= 1.0
        mode_label = "B" if is_high_intensity else "A"

        context = item_with_context["context"]

        headline = _duration_safe_headline(
            headline=headline,
            event=item,
            template_key=template_key,
        )
        main_summary = _duration_safe_summary(
            summary=_first_sentence(summary) or "Bu etki belirgin bir vurgu yaratabilir",
            event=item,
            template_key=template_key,
        )
        item_with_context["primary_theme"] = primary_theme
        mechanism = _normalize_sentence(build_mechanism_sentence(item_with_context)) or (
            "Bu etki farkindalikla yonetildiginde dengeye gelir"
        )
        summary_text = f"{main_summary}. {mechanism}."

        interpretation = {
            "mode": mode_label,
            "headline": headline,
            "summary": summary_text,
            "do": do_list,
            "watch": watch_list,
            "themes": themes,
            "time_status": _time_status_tr(item.get("phase")),
            "confidence": round(min(1.0, 0.6 + strength * 0.4), 2),
            "where": build_where_sentence(context),
            "time_hint": _build_time_hint(item),
            "context": {
                "natal_target_house": natal_target_house,
                "transit_house": transit_house,
                "axis": axis,
            },
            "content_ref": {
                "pack": "tr.transit.v1",
                "key": template_key,
                "fallbacks": fallback_chain,
            },
            "resolver_debug": {
                "keys_tried": fallback_chain,
                "selected_key": template_key,
                "specific_key": canonical_key(transit, aspect, natal_point).lower(),
                "specific_exists": specific_exists,
                "fallback_level": _fallback_level(fallback_chain, template_key),
                "primary_theme": primary_theme,
            },
        }

        interpretation["summary"] = _ensure_two_sentences(interpretation["summary"], mechanism)
        if not interpretation.get("where"):
            interpretation["where"] = "Bunu gunluk akis icinde daha belirgin hissedebilirsin."
        if not interpretation.get("time_hint"):
            interpretation["time_hint"] = _build_time_hint(item)

        if mode_label == "B":
            mode_reason = "strength>=0.75" if strength >= 0.75 else "orb<=1.0"
            interpretation["debug"] = {
                "mode_reason": [mode_reason],
                "rule_version": "mode_gate.v1",
            }
            context = _inject_context(item, promise, content)
            if context:
                interpretation["natal_promise"] = {
                    "claim_id": (context.get("matched_claims") or [{}])[0].get("id"),
                    "claim_score": (context.get("matched_claims") or [{}])[0].get("score"),
                    "used": bool(context.get("context_sentence")),
                    "fit": "direct" if context.get("context_sentence") else "indirect",
                    "why_this_claim": context.get("promise_debug", {}).get("why") or [],
                }
                interpretation["context_sentence"] = context["context_sentence"]
                interpretation["promise_refs"] = context["matched_claims"]
                interpretation["promise_debug"] = context["promise_debug"]
                if context.get("resolver_debug"):
                    interpretation["resolver_debug"] = context["resolver_debug"]
                if context.get("context_claims"):
                    interpretation["debug"]["context_claims"] = context["context_claims"]

        item["interpretation"] = interpretation
        interpreted.append(item)

    summary = _build_summary(interpreted)
    return interpreted, summary


def _time_status_tr(phase: str | None) -> str:
    mapping = {
        "applying": "yaklaşıyor",
        "exactish": "zirvede",
        "separating": "çözülüyor",
    }
    return mapping.get(str(phase or ""), "yaklaşıyor")


def _build_time_hint(event: Dict[str, Any]) -> str:
    phase_map = {"applying": "yaklaşıyor", "exactish": "en yoğun", "separating": "çözülüyor"}
    dur_map = {
        "short": "günlük/kısa etki",
        "medium": "haftalar süren vurgu",
        "long": "aylar süren ana tema",
    }
    phase = phase_map.get(str(event.get("phase") or ""), "yaklaşıyor")
    duration = dur_map.get(str(event.get("bucket") or ""), "dönemsel vurgu")
    return f"{phase} — {duration}"


def _normalize_sentence(value: Any) -> str:
    text = str(value or "").strip()
    while text and text[-1] in ".!?:;…":
        text = text[:-1].rstrip()
    return text


def _first_sentence(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    split = text.split(".")
    return _normalize_sentence(split[0]) if split else _normalize_sentence(text)


def _ensure_two_sentences(summary: str, mechanism: str) -> str:
    base = _normalize_sentence(summary)
    if not base:
        base = "Bu etki belirgin bir vurgu yaratabilir"
    pieces = [p for p in base.split(".") if p.strip()]
    if len(pieces) >= 2:
        first = _normalize_sentence(pieces[0])
        second = _normalize_sentence(pieces[1])
        return f"{first}. {second}."
    return f"{_normalize_sentence(pieces[0])}. {_normalize_sentence(mechanism)}."


def _ensure_min_list(
    items: List[str],
    polarity: str,
    theme: str,
    *,
    kind: str,
) -> List[str]:
    cleaned = [str(item).strip() for item in items if str(item).strip()]
    defaults = {
        "do": {
            "hard": ["Hizini dusur.", "Net sinir koy."],
            "soft": ["Firsati somutlastir.", "Kucuk adim at."],
            "neutral": ["Gozlemde kal.", "Not al."],
        },
        "watch": {
            "hard": ["Tepkisel davranis.", "Acele karar."],
            "soft": ["Erteleme.", "Rahatliga kapilma."],
            "neutral": ["Asiri anlam yukleme.", "Varsayim."],
        },
    }
    key = "hard" if polarity == "hard" else "soft" if polarity == "soft" else "neutral"
    fallback_items = defaults.get(kind, {}).get(key, [])
    while len(cleaned) < 2 and fallback_items:
        next_item = fallback_items[len(cleaned)]
        cleaned.append(next_item)
    return cleaned


def _fallback_level(keys_tried: list[str], selected_key: str) -> int | None:
    try:
        return keys_tried.index(selected_key)
    except ValueError:
        return None


def _duration_safe_headline(*, headline: str, event: Dict[str, Any], template_key: str) -> str:
    bucket = str(event.get("bucket") or "")
    if bucket != "long":
        return headline
    if template_key not in {"generic.any", "hard.any", "soft.any", "neutral.any"}:
        return headline
    variants = ["Dönemsel tema", "Ana vurgu", "Uzun soluklu ayar"]
    seed = f"{event.get('event_id')}:{template_key}:h"
    return _pick_variant(seed, variants)


def _duration_safe_summary(*, summary: str, event: Dict[str, Any], template_key: str) -> str:
    bucket = str(event.get("bucket") or "")
    if bucket != "long":
        return summary
    if template_key not in {"generic.any", "hard.any", "soft.any", "neutral.any"}:
        return summary
    lowered = summary.lower()
    if "kısa" in lowered or "geçici" in lowered:
        return "Bu etki dönemsel bir ana vurgu getirir ve zamana yayılarak çalışır"
    return summary


# ----------------- CONTEXT INJECTION ----------------- #

def _inject_context(event: Dict, promise: Dict | None, content: ContentStore) -> Dict | None:
    if not promise:
        return None
    claims = promise.get("claims", {})
    if not claims:
        return None

    event_tags = set(event.get("tags", []))
    event_point = event.get("natal_point")
    point_affinity = (content.mapping.get("point_affinity") or {}).get(event_point)
    event_domain = _domain_from_tags(event_tags)

    scored: List[Tuple[str, float]] = []
    for cid, claim in claims.items():
        claim_tags = set(claim.get("tags", []))
        tag_overlap = len(event_tags & claim_tags) / max(len(event_tags | claim_tags), 1)
        domain_match = 1.0 if claim.get("domain") == event_domain else 0.0
        point_match = 1.0 if claim.get("domain") == point_affinity else 0.0
        score = 0.55 * tag_overlap + 0.30 * point_match + 0.15 * domain_match
        scored.append((cid, score))

    scored.sort(key=lambda x: (-x[1], _hash_int(event["event_id"] + x[0])))
    min_claim_score = 0.15
    best_score = scored[0][1] if scored else 0.0
    if not scored or best_score < min_claim_score:
        return {
            "matched_claims": [],
            "context_sentence": None,
            "resolver_debug": {
                "top_candidates": [
                    {"id": cid, "score": round(score, 3)} for cid, score in scored[:5]
                ],
                "picked": [],
                "tie_break": "hash",
                "threshold": min_claim_score,
                "best_score": round(best_score, 3),
                "threshold_applied": True,
            },
            "context_claims": [],
            "promise_debug": {
                "selected_claim_id": None,
                "dropped_claim_ids": [],
                "tie_breaker": "hash(event_id, claim_id)",
                "why": ["below_threshold"],
            },
        }
    limit = (
        2
        if float(event.get("strength") or 0.0) >= 0.75
        or float(event.get("orb_deg") or 99.0) <= 1.0
        else 1
    )
    selected = scored[:limit]

    matched_claims = []
    resolver_debug = {
        "top_candidates": [
            {"id": cid, "score": round(score, 3)} for cid, score in scored[: max(5, limit)]
        ],
        "picked": [],
        "tie_break": "hash",
    }
    if not selected:
        return None

    claim_texts: list[str] = []
    for idx, (cid, score) in enumerate(selected):
        variants = claims[cid].get("text_variants", [])
        claim_text = _pick_variant(f"{event['event_id']}:{cid}:v1", variants)
        matched_claims.append(
            {
                "id": cid,
                "score": round(score, 2),
                "text": claim_text,
                "used_for_render": idx == 0,
            }
        )
        resolver_debug["picked"].append(cid)
        if claim_text:
            claim_texts.append(claim_text)

    if not claim_texts:
        return None

    claim_text = _normalize_sentence(claim_texts[0])
    context_sentence = (
        f"Bu etki sende özellikle {claim_text} temasını daha görünür kılabilir."
    )
    why_this_claim = []
    if event_domain:
        why_this_claim.append(f"theme_match:{event_domain}")
    if claim_texts:
        why_this_claim.append("tags:overlap")
    promise_debug = {
        "selected_claim_id": matched_claims[0]["id"],
        "dropped_claim_ids": [entry["id"] for entry in matched_claims[1:]],
        "tie_breaker": "hash(event_id, claim_id)",
        "why": why_this_claim,
    }

    return {
        "matched_claims": matched_claims,
        "context_sentence": context_sentence,
        "resolver_debug": resolver_debug,
        "context_claims": matched_claims,
        "promise_debug": promise_debug,
    }


def _domain_from_tags(tags: set) -> str | None:
    mapping = {
        "self": "identity",
        "relationships": "relationships",
        "career": "career",
        "home": "home",
        "inner": "inner",
        "mind": "mind",
    }
    for tag in tags:
        if tag in mapping:
            return mapping[tag]
    return None


# ----------------- SUMMARY ----------------- #

def _build_summary(items: List[Dict]) -> Dict:
    theme_scores: Dict[str, float] = {}
    featured_ids = []

    for item in items:
        if item.get("event_id") and len(featured_ids) < 3:
            featured_ids.append(item["event_id"])
        for t in item.get("interpretation", {}).get("themes", []):
            theme_scores[t] = theme_scores.get(t, 0.0) + float(item.get("strength") or 0.0)

    top_themes = sorted(theme_scores.items(), key=lambda x: -x[1])
    top_theme_list = [
        {"theme": k, "score": round(v, 2), "drivers": featured_ids} for k, v in top_themes[:2]
    ]

    return {
        "one_liner": "Bu dönem kimlik/sınır teması baskın; netlik yavaş geliyor.",
        "top_themes": top_theme_list,
        "featured_ids": featured_ids,
    }
