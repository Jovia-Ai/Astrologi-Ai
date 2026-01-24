import hashlib
import re
from typing import Any, Dict, List, Tuple

from app.transit.interpret.canonical import canon_aspect, canonical_key
from app.transit.interpret.mechanism import build_mechanism_sentence
from app.transit.interpret.themes import pick_primary_theme
from app.transit.interpret.where import HOUSE_LABELS_TR, build_where_sentence


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
    def __init__(
        self,
        templates: Dict,
        claims: Dict,
        mapping: Dict,
        upper_meaning: Dict | None = None,
        style_do: Dict | None = None,
        approach_pack: Dict | None = None,
    ):
        self.templates = templates
        self.claims = claims
        self.mapping = mapping
        self.upper_meaning = upper_meaning or {}
        self.style_do = style_do or {}
        self.approach_pack = approach_pack or {}

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


PUNCT_RE = re.compile(r"[.?!;:\s]+$")
POINT_ALIASES = {
    "asc": "asc",
    "ascendant": "asc",
    "dsc": "dsc",
    "desc": "dsc",
    "descendant": "dsc",
    "mc": "mc",
    "midheaven": "mc",
    "ic": "ic",
    "imumcoeli": "ic",
    "imum_coeli": "ic",
}


def interpret_items(
    items: List[Dict[str, Any]],
    content: ContentStore,
    promise: Dict[str, Any] | None = None,
    mode: str = "context-lite",
    *,
    debug: bool = False,
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
        short_headline = _pick_variant(
            f"{event_id}:sh",
            template.get("short_headline_variants", []),
        )
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
            "short_headline": short_headline or "",
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

        claim_micro = None
        if mode_label == "B":
            mode_reason = "strength>=0.75" if strength >= 0.75 else "orb<=1.0"
            interpretation["debug"] = {
                "mode_reason": [mode_reason],
                "rule_version": "mode_gate.v1",
            }
            context = _inject_context(item, promise, content)
            if context:
                claim_micro = (context.get("matched_claims") or [{}])[0].get("micro_phrase")
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

        upper_text, upper_ref = _resolve_upper_meaning(
            event_id=event_id,
            transit_body=transit,
            aspect=aspect,
            natal_point=natal_point,
            polarity=polarity,
            content=content,
            include_debug=debug,
        )
        if upper_text:
            interpretation["upper_meaning"] = upper_text
        if upper_ref:
            interpretation["upper_meaning_ref"] = upper_ref

        style_text, style_ref = _resolve_style_do(
            event_id=event_id,
            transit_body=transit,
            aspect=aspect,
            natal_point=natal_point,
            polarity=polarity,
            content=content,
            include_debug=debug,
        )
        if style_text:
            core_do = do_list[:2]
            do_items = list(core_do)
            do_items.append(style_text)
            interpretation["do"] = do_items[:4]
        if style_ref:
            interpretation["style_do_ref"] = style_ref

        approach_text, approach_ref = _resolve_approach_text(
            event_id=event_id,
            transit_body=transit,
            polarity=polarity,
            transit_style=(item.get("astro_style") or {}).get("transit"),
            target_style=(item.get("astro_style") or {}).get("target"),
            content=content,
            include_debug=debug,
        )
        if approach_text:
            do_items = list(interpretation.get("do") or do_list[:2])
            if len(do_items) < 2:
                do_items = do_list[:2]
            do_items.append(f"Yaklasim: {approach_text}")
            interpretation["do"] = do_items[:4]
        if approach_ref:
            interpretation["approach_ref"] = approach_ref

        interpretation["one_liner"] = _build_event_one_liner(
            item,
            interpretation,
            house_labels=HOUSE_LABELS_TR,
            claim_phrase=claim_micro,
            upper_meaning=upper_text,
            approach_text=approach_text,
        )
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


def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


def _norm_point(value: Any) -> str:
    key = _norm(value)
    return POINT_ALIASES.get(key, key)


def _norm_polarity(polarity: Any, aspect: Any) -> str:
    pol = _norm(polarity)
    if pol in {"hard", "soft", "neutral"}:
        return pol
    asp = _norm(aspect)
    if asp:
        if asp in {"square", "opposition"}:
            return "hard"
        if asp in {"trine", "sextile"}:
            return "soft"
        if asp == "conjunction":
            return "neutral"
    return "neutral"


def _stable_variant_index(event_id: str, n: int) -> int:
    if n <= 1:
        return 0
    seed = (event_id or "evt").encode("utf-8")
    digest = hashlib.sha256(seed).digest()
    return int.from_bytes(digest[:4], "big") % n


def _clean_trailing_punct(text: str) -> str:
    return PUNCT_RE.sub("", (text or "").strip())


def _dedupe_repeats(text: str) -> str:
    words = text.split()
    cleaned = []
    for word in words:
        if cleaned and cleaned[-1] == word:
            continue
        cleaned.append(word)
    text = " ".join(cleaned)
    for phrase in (
        "yardimci olabilir",
        "alan acabilir",
        "kolaylastirabilir",
        "destek olabilir",
        "gosterebilir",
        "olabilir",
    ):
        escaped = re.escape(phrase)
        pattern = re.compile(rf"({escaped})(?:\s+\1)+")
        text = pattern.sub(phrase, text)
    return text


def _headline_text(interpretation: Dict[str, Any]) -> str:
    headline = _clean_trailing_punct(str(interpretation.get("headline") or ""))
    if headline:
        return headline
    summary_first = _first_sentence(interpretation.get("summary") or "")
    cleaned = _clean_trailing_punct(summary_first)
    return cleaned or "Bu etki"


def _short_headline_text(interpretation: Dict[str, Any]) -> str:
    short_headline = _clean_trailing_punct(str(interpretation.get("short_headline") or ""))
    if short_headline:
        return short_headline
    return _headline_text(interpretation)


def _group_where_label(label: str) -> str:
    lowered = label.lower()
    if any(key in lowered for key in ("kimlik", "durus", "gorunurluk", "imaj")):
        return "kimlik ve durus"
    if any(key in lowered for key in ("zihin", "iletisim", "ogren", "merak")):
        return "zihin ve iletisim"
    if any(key in lowered for key in ("iliski", "ortaklik", "yakinlik")):
        return "iliskiler"
    if any(key in lowered for key in ("saglik", "ritim", "is akisi", "gunluk")):
        return "gunluk duzen"
    if any(key in lowered for key in ("para", "ozdeger", "deger")):
        return "para ve ozdeger"
    if any(key in lowered for key in ("yon", "anlam", "uzak")):
        return "yon ve anlam"
    if any(key in lowered for key in ("ev", "ic guven", "kok")):
        return "ev ve ic guven"
    if any(key in lowered for key in ("cevre", "gelecek")):
        return "cevre ve gelecek"
    return label


def _where_short_label(
    item: Dict[str, Any],
    interpretation: Dict[str, Any],
    *,
    house_labels: Dict[int, str],
) -> str:
    houses = item.get("houses") or {}
    context = interpretation.get("context") or {}
    natal_h = context.get("natal_target_house") or houses.get("natal_point_house")
    overlay_h = houses.get("transit_in_natal_house")

    natal_label = _house_label(natal_h, house_labels)
    overlay_label = _house_label(overlay_h, house_labels)
    if natal_label:
        return _group_where_label(_clean_trailing_punct(natal_label))
    if overlay_label:
        return _group_where_label(_clean_trailing_punct(overlay_label))

    where_text = str(interpretation.get("where") or "")
    lowered = where_text.lower()
    for anchor, direct_label in (
        ("alaninda", None),
        ("tarafinda", None),
        ("konusunda", None),
        ("iliskilerde", "iliskiler"),
        ("iste", "is"),
        ("evde", "ev"),
        ("gunluk", "gunluk duzen"),
    ):
        if anchor not in lowered:
            continue
        if direct_label:
            return _group_where_label(direct_label)
        before = lowered.split(anchor, 1)[0].strip()
        if not before:
            continue
        words = [w for w in before.split() if w]
        if not words:
            continue
        label_words = words[-4:]
        return _group_where_label(" ".join(label_words))

    return "hayatinin akisi"


def _first_sentence(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    split = text.split(".")
    return _normalize_sentence(split[0]) if split else _normalize_sentence(text)


def _first_sentence_with_period(value: Any) -> str:
    sentence = _first_sentence(value)
    if not sentence:
        return ""
    if sentence.endswith("."):
        return sentence
    return f"{sentence}."


def _timing_band(item: Dict[str, Any], time_hint: str | None = None) -> str:
    phase = str(item.get("phase") or "").lower()
    bucket = str(item.get("bucket") or "").lower()

    base = ""
    if phase == "applying":
        base = "onumuzdeki haftalarda belirginlesebilir"
    elif phase in {"exact", "exactish"}:
        base = "su an en yogun doneminde olabilir"
    elif phase == "separating":
        base = "kademeli olarak yumusuyor olabilir"
    else:
        base = str(time_hint or "").strip()

    if bucket == "long":
        if base:
            return f"{base}; etkisi aylar boyunca hissedilebilir"
        return "etkisi aylar boyunca hissedilebilir"

    return base


def _house_label(house_num: int | None, house_labels: Dict[int, str]) -> str | None:
    if not house_num:
        return None
    return house_labels.get(house_num)


def _mechanic_phrase(item: Dict[str, Any]) -> str:
    body = item.get("transit_body")
    polarity = str(item.get("polarity") or "").lower()

    if body == "Saturn" and polarity == "hard":
        return "sinirlari, gecikmeleri ve eforu daha gorunur kilmasi"
    if body == "Neptune" and polarity == "hard":
        return "netligi azaltip varsayimlari artirmasi"
    if body == "Pluto":
        return "kontrol ve donusum temasini derinlestirmesi"
    if body == "Uranus":
        return "ani degisim ve ozgurlesme ihtiyaci yaratmasi"
    if body == "Jupiter":
        return "genisleme ve firsat arayisini buyutmesi"
    if body == "Venus":
        return "iliski ve deger temasini belirginlestirmesi"
    if body == "Mercury":
        return "iletisim ve zihin temposunu belirginlestirmesi"
    if body == "Mars":
        return "aksiyon ve gerilim temasini belirginlestirmesi"

    if polarity == "hard":
        return "baski ve surtunme yaratmasi"
    if polarity == "soft":
        return "akisi desteklemesi"
    return "temayi gorunur kilmasi"


def _his_phrase(summary_first: str | None) -> str:
    cleaned = _normalize_sentence(summary_first or "").lower()
    if not cleaned:
        return "bazi seyleri daha hassas hissettirebilir"
    if len(cleaned.split()) > 12:
        return "bazi seyleri daha hassas hissettirebilir"
    return cleaned


def _build_event_one_liner(
    item: Dict[str, Any],
    interpretation: Dict[str, Any],
    *,
    house_labels: Dict[int, str],
    claim_phrase: str | None,
    upper_meaning: str | None,
    approach_text: str | None,
) -> str:
    headline = _headline_text(interpretation)
    short_headline = _short_headline_text(interpretation)
    where_short = _where_short_label(item, interpretation, house_labels=house_labels)
    variant = _stable_variant_index(str(item.get("event_id") or ""), 3)

    if variant == 1:
        first_sentence = f"{headline}; etki en cok {where_short} tarafinda toplanabilir."
    elif variant == 2:
        first_sentence = f"{headline}; ozellikle {where_short} tarafinda belirginlesebilir."
    else:
        first_sentence = f"{headline}; bunu en cok {where_short} tarafinda hissedebilirsin."

    second_sentence = ""
    if upper_meaning:
        normalized = _clean_trailing_punct(upper_meaning)
        lowered = normalized.lower()
        keywords = [
            "alan acabilir",
            "yardimci olabilir",
            "kolaylastirabilir",
            "destekleyebilir",
            "gosterebilir",
            "mumkun",
            "olabilir",
        ]
        if any(keyword in lowered for keyword in keywords):
            second_sentence = f"{normalized[:1].upper()}{normalized[1:]}."
        else:
            second_sentence = f"Uzun vadede {normalized}."
    elif approach_text:
        normalized = _clean_trailing_punct(approach_text)
        second_sentence = f"{normalized[:1].upper()}{normalized[1:]}."
    elif claim_phrase:
        short_enough = len(claim_phrase.split()) <= 6 and len(claim_phrase) <= 40
        if short_enough:
            second_sentence = f"Ozellikle {claim_phrase} refleksini yumusatabilir."

    first_sentence = _clean_trailing_punct(first_sentence) + "."
    first_sentence = _dedupe_repeats(first_sentence)

    if second_sentence:
        second_sentence = _clean_trailing_punct(second_sentence) + "."
        second_sentence = _dedupe_repeats(second_sentence)

    result = " ".join(part for part in [first_sentence, second_sentence] if part).strip()

    if len(result) > 220:
        if second_sentence and "refleksini yumusatabilir" in second_sentence:
            result = first_sentence.strip()
        if len(result) > 220:
            short_label = " ".join(where_short.split()[:2]) or where_short
            if variant == 1:
                first_sentence = f"{headline}; etki en cok {short_label} tarafinda toplanabilir."
            elif variant == 2:
                first_sentence = f"{headline}; ozellikle {short_label} tarafinda belirginlesebilir."
            else:
                first_sentence = f"{headline}; bunu en cok {short_label} tarafinda hissedebilirsin."
            first_sentence = _clean_trailing_punct(first_sentence) + "."
            first_sentence = _dedupe_repeats(first_sentence)
            result = " ".join(part for part in [first_sentence, second_sentence] if part).strip()
        if len(result) > 220:
            short_headline = _clean_trailing_punct(short_headline)
            if variant == 1:
                first_sentence = f"{short_headline}; etki en cok {where_short} tarafinda toplanabilir."
            elif variant == 2:
                first_sentence = f"{short_headline}; ozellikle {where_short} tarafinda belirginlesebilir."
            else:
                first_sentence = f"{short_headline}; bunu en cok {where_short} tarafinda hissedebilirsin."
            first_sentence = _clean_trailing_punct(first_sentence) + "."
            first_sentence = _dedupe_repeats(first_sentence)
            result = " ".join(part for part in [first_sentence, second_sentence] if part).strip()
        if len(result) > 220:
            result = first_sentence.strip()

    result = _dedupe_repeats(result)
    result = _clean_trailing_punct(result) + "."
    return result


def _upper_meaning_keys(
    transit_body: str,
    aspect: str,
    natal_point: str,
    polarity: str,
) -> List[str]:
    body = _norm(transit_body)
    aspect_key = _norm(aspect)
    point = _norm_point(natal_point)
    polarity_key = _norm_polarity(polarity, aspect_key)
    return [
        f"{body}.{aspect_key}.{point}",
        f"{body}.{aspect_key}.any",
        f"{aspect_key}.{polarity_key}.any",
        f"{polarity_key}.any",
        "generic.any",
    ]


def _resolve_upper_meaning(
    *,
    event_id: str,
    transit_body: str,
    aspect: str,
    natal_point: str,
    polarity: str,
    content: ContentStore,
    include_debug: bool = False,
) -> Tuple[str, Dict[str, Any] | None]:
    pack = content.upper_meaning or {}
    if not pack:
        return "", None
    keys = _upper_meaning_keys(transit_body, aspect, natal_point, polarity)
    for key in keys:
        variants = pack.get(key)
        if not isinstance(variants, list) or not variants:
            continue
        variant_index = _stable_variant_index(str(event_id), len(variants))
        text = str(variants[variant_index]).strip()
        if not text:
            continue
        ref = {
            "key": key,
            "variant": variant_index,
            "lang": "tr",
            "version": "v1",
        }
        if include_debug:
            ref["resolver_path"] = keys
            ref["selected_key"] = key
        return text, ref
    return "", None


def _resolve_style_do(
    *,
    event_id: str,
    transit_body: str,
    aspect: str,
    natal_point: str,
    polarity: str,
    content: ContentStore,
    include_debug: bool = False,
) -> Tuple[str, Dict[str, Any] | None]:
    pack = content.style_do or {}
    if not pack:
        return "", None
    keys = _upper_meaning_keys(transit_body, aspect, natal_point, polarity)
    for key in keys:
        variants = pack.get(key)
        if not isinstance(variants, list) or not variants:
            continue
        variant_index = _stable_variant_index(str(event_id), len(variants))
        text = str(variants[variant_index]).strip()
        if not text:
            continue
        if not include_debug:
            return text, None
        return text, {
            "key": key,
            "variant": variant_index,
            "lang": "tr",
            "version": "v1",
            "resolver_path": keys,
            "selected_key": key,
        }
    return "", None


def _resolve_approach_text(
    *,
    event_id: str,
    transit_body: str,
    polarity: str,
    transit_style: Dict[str, Any] | None,
    target_style: Dict[str, Any] | None,
    content: ContentStore,
    include_debug: bool = False,
) -> Tuple[str, Dict[str, Any] | None]:
    pack = content.approach_pack or {}
    if not pack:
        return "", None
    transit_element = _norm((transit_style or {}).get("element") or "any") or "any"
    transit_modality = _norm((transit_style or {}).get("modality") or "any") or "any"
    target_element = _norm((target_style or {}).get("element") or "any") or "any"
    target_modality = _norm((target_style or {}).get("modality") or "any") or "any"
    body = _norm(transit_body)
    pol = _norm_polarity(polarity, None)

    keys = [
        f"approach.{body}.{pol}.{transit_element}.{transit_modality}.{target_element}.{target_modality}",
        f"approach.{body}.{pol}.{transit_element}.{transit_modality}.any.any",
        f"approach.{body}.{pol}.{transit_element}.any.any.any",
        f"approach.{body}.{pol}.any.any.any.any",
        f"approach.{body}.any.any.any.any.any",
        f"approach.{pol}.any",
        "approach.generic.any",
    ]
    for key in keys:
        variants = pack.get(key)
        if not isinstance(variants, list) or not variants:
            continue
        variant_index = _stable_variant_index(str(event_id), len(variants))
        text = str(variants[variant_index]).strip()
        if not text:
            continue
        if not include_debug:
            return text, None
        return text, {
            "key": key,
            "variant": variant_index,
            "lang": "tr",
            "version": "v1",
            "resolver_path": keys,
            "selected_key": key,
        }
    return "", None


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
        text_variants = claims[cid].get("text_variants", [])
        claim_text = _pick_variant(f"{event['event_id']}:{cid}:v1", text_variants)
        phrase_variants = claims[cid].get("phrase_variants", [])
        micro_phrase = _pick_variant(f"{event['event_id']}:{cid}:p1", phrase_variants)
        if not micro_phrase:
            micro_phrase = _normalize_sentence(claim_text).lower() if claim_text else ""
        matched_claims.append(
            {
                "id": cid,
                "score": round(score, 2),
                "text": claim_text,
                "micro_phrase": micro_phrase,
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
