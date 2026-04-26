from __future__ import annotations

import hashlib
import re
from collections import Counter
from typing import Iterable, Sequence


RHYTHM_FAMILIES = ("direct", "observational", "cinematic", "intimate")

_STOPWORDS = {
    "ve",
    "ile",
    "bu",
    "bir",
    "da",
    "de",
    "gibi",
    "için",
    "daha",
    "çok",
    "ama",
    "hem",
    "sen",
    "sende",
    "senin",
    "olan",
    "olanı",
    "şey",
    "artık",
    "bile",
    "ise",
    "kadar",
    "önce",
    "sonra",
    "anda",
}

_VERB_PATTERN = re.compile(
    r"\b\w{3,}(?:yor|ıyor|iyor|uyor|üyor|mış|miş|muş|müş|malı|meli|abilir|ebilir|acak|ecek|dır|dir|dur|dür|tır|tir|tur|tür|arsın|ersin|ırsın|irsin|ursun|ürsün)\b",
    re.IGNORECASE,
)

_COACHING_PATTERN = re.compile(
    r"\b(?:gerekir|yardımcı olur|iyi gelir|ihtiyacın var|adım|strateji|çözüm|pratik|yapman iyi olur|tek paylaşım)\b",
    re.IGNORECASE,
)

_COOKBOOK_PATTERN = re.compile(
    r"\b(?:bu açı|yerleşim|yerlesim|vurgusu|şunu verir|kavuşum|kare|sekstil|üçgen|stellium)\b",
    re.IGNORECASE,
)

_ABSTRACT_SUFFIXES = ("lık", "lik", "luk", "lük", "sallık", "sellik", "suzluk", "süzlük")


def stable_int(seed: str) -> int:
    return int(hashlib.sha256(str(seed).encode("utf-8")).hexdigest()[:8], 16)


def cleanup_text(text: str) -> str:
    value = " ".join(str(text or "").split()).strip()
    value = value.replace(" ,", ",").replace(" .", ".").replace(" ;", ";").replace(" :", ":")
    return value.strip()


def ensure_sentence(text: str) -> str:
    value = cleanup_text(text)
    if not value:
        return ""
    return value if value[-1] in ".!?" else f"{value}."


def normalize_fragment(text: str) -> str:
    value = cleanup_text(text)
    value = re.sub(r"[.!?]+$", "", value).strip(" ,;:")
    return value


def semantic_tokens(text: str, *, extra_stopwords: Iterable[str] | None = None) -> set[str]:
    stopwords = set(_STOPWORDS)
    if extra_stopwords:
        stopwords.update(str(item).lower() for item in extra_stopwords)
    return {
        token
        for token in re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ]+", str(text or "").lower())
        if len(token) >= 3 and token not in stopwords
    }


def semantic_overlap(a: str, b: str) -> float:
    left = semantic_tokens(a)
    right = semantic_tokens(b)
    if not left or not right:
        return 0.0
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def opening_key(text: str, *, words: int = 2) -> str:
    tokens = [token for token in re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ]+", str(text or "").lower()) if token]
    return " ".join(tokens[:words])


def has_coaching_tone(text: str) -> bool:
    return bool(_COACHING_PATTERN.search(str(text or "")))


def has_cookbook_tone(text: str) -> bool:
    return bool(_COOKBOOK_PATTERN.search(str(text or "")))


def looks_abstract(text: str) -> bool:
    value = cleanup_text(text)
    if not value:
        return True
    tokens = [token for token in re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ]+", value.lower()) if len(token) >= 3]
    if not tokens:
        return True
    if _VERB_PATTERN.search(value):
        return False
    abstract_hits = sum(1 for token in tokens if token.endswith(_ABSTRACT_SUFFIXES))
    return abstract_hits >= max(1, len(tokens) // 3)


def select_rhythm_family(
    seed: str,
    namespace: str,
    key: str,
    used_families: Sequence[str] | None = None,
) -> str:
    used = Counter(str(item) for item in (used_families or []) if item)
    start = stable_int(f"{seed}|{namespace}|{key}|family") % len(RHYTHM_FAMILIES)
    ordered = list(RHYTHM_FAMILIES[start:]) + list(RHYTHM_FAMILIES[:start])
    ranked = [(used.get(item, 0), index, item) for index, item in enumerate(ordered)]
    ranked.sort()
    return ranked[0][2]


def apply_phrase_policy(text: str, *, mode: str = "core") -> str:
    value = cleanup_text(text)
    if not value:
        return ""
    replacements = (
        (r"\bbu senden\b", "bu refleks sende belirgin"),
        (r"\bbu sende şöyle çalışır\b", "bu yapı çoğu kez böyle akar"),
        (r"\bbu açı şunu verir\b", "bu kombinasyonun etkisi şurada belirginleşir"),
        (r"\bgenellikle\b", "çoğu kez"),
        (r"\bkişi\b", "sen"),
    )
    for pattern, replacement in replacements:
        value = re.sub(pattern, replacement, value, flags=re.IGNORECASE)
    if mode == "core":
        value = re.sub(r"\bolabilirsin\b", "olursun", value, flags=re.IGNORECASE)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def editorialize_micro(text: str, family: str) -> str:
    value = apply_phrase_policy(text, mode="core")
    if not value:
        return ""
    lowered = value.lower()
    stripped = re.sub(r"[.!?]+$", "", lowered)
    for suffix in ("senden", "çok tipik"):
        if re.search(rf"\b{suffix}$", stripped):
            stem = re.sub(rf"\s*\b{suffix}\b[.!?]*$", "", value, flags=re.IGNORECASE).strip()
            return _nominal_observation(stem, family, role="micro")
    if lowered.startswith("sende "):
        stem = normalize_fragment(value[6:])
        return _nominal_observation(stem, family, role="micro")
    return ensure_sentence(value)


def editorialize_teaser(text: str, family: str) -> str:
    value = apply_phrase_policy(text, mode="core")
    if not value:
        return ""
    lowered = value.lower()
    if lowered.startswith("sende "):
        stem = normalize_fragment(value[6:])
        return _nominal_observation(stem, family, role="teaser")
    return ensure_sentence(value)


def render_fragment_line(
    text: str,
    *,
    family: str,
    role: str,
    evidence_text: str = "",
    mode: str = "core",
) -> str:
    primary = apply_phrase_policy(text, mode=mode)
    evidence = apply_phrase_policy(evidence_text, mode=mode)
    chosen = primary or evidence
    if not chosen:
        return ""
    tokens = [token for token in re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ]+", chosen.lower()) if len(token) >= 3]
    if evidence and (
        looks_abstract(chosen)
        or (not _VERB_PATTERN.search(chosen) and len(tokens) <= 6)
        or (role in {"experienced", "potential"} and chosen.lower().startswith("bu "))
    ):
        chosen = evidence
    if looks_abstract(chosen):
        return _nominal_observation(normalize_fragment(chosen), family, role=role)
    if chosen.lower().startswith("sende "):
        return _nominal_observation(normalize_fragment(chosen[6:]), family, role=role)
    return ensure_sentence(chosen)


def quality_issues(
    *,
    teaser: str,
    body: str,
    micro: str = "",
    used_openings: Sequence[str] | None = None,
    used_bodies: Sequence[str] | None = None,
) -> list[str]:
    issues: list[str] = []
    opening = opening_key(body)
    if opening and opening in set(used_openings or []):
        issues.append("repeated_opening")
    if str(body or "").lower().count("sende ") > 1:
        issues.append("too_many_sende")
    if teaser and semantic_overlap(teaser, body) >= 0.74:
        issues.append("teaser_overlap")
    if micro and semantic_overlap(micro, body) >= 0.74:
        issues.append("micro_overlap")
    if has_coaching_tone(body) or has_coaching_tone(micro):
        issues.append("coaching_tone")
    if has_cookbook_tone(body):
        issues.append("cookbook_tone")
    for prior in used_bodies or []:
        if semantic_overlap(body, prior) >= 0.78:
            issues.append("cross_block_overlap")
            break
    return issues


def _nominal_observation(fragment: str, family: str, *, role: str) -> str:
    stem = normalize_fragment(fragment)
    if not stem:
        return ""
    lower = stem[:1].lower() + stem[1:] if stem else stem
    templates = {
        "teaser": {
            "direct": "Öne çıkan çizgi şu: {fragment}.",
            "observational": "İnsanlar ilk anda en çok şunu okur: {fragment}.",
            "cinematic": "Ortama ilk düşen ton şu: {fragment}.",
            "intimate": "En görünür ama en kişisel tarafın burada: {fragment}.",
        },
        "micro": {
            "direct": "İlk refleksin, {fragment}.",
            "observational": "Dışarıdan önce şu refleksin fark edilir: {fragment}.",
            "cinematic": "Sahne çoğu kez aynı yerden açılır: {fragment}.",
            "intimate": "İçeride hemen şu olur: {fragment}.",
        },
        "recognition": {
            "direct": "İlk anda öne çıkan şey {fragment}.",
            "observational": "İnsanlar önce {fragment} tarafını hisseder.",
            "cinematic": "İlk karede görünen şey {fragment}.",
            "intimate": "En görünür yerinde {fragment}.",
        },
        "experienced": {
            "direct": "Günlük hayatta bunun karşılığı {fragment}.",
            "observational": "Gündelik akışta en çok {fragment} hissedilir.",
            "cinematic": "Günlük ritimde sahne hep {fragment} yerinden açılır.",
            "intimate": "İçeride bu, {fragment} olarak yaşanır.",
        },
        "potential": {
            "direct": "Yerini bulduğunda {fragment}.",
            "observational": "Olgunlaştığında dışarıya {fragment} diye yansır.",
            "cinematic": "Denge geldiğinde tablo {fragment} tarafına döner.",
            "intimate": "Güven bulduğunda {fragment} daha rahat görünür.",
        },
        "shadow": {
            "direct": "Zorlandığında gerilim {fragment} tarafında birikir.",
            "observational": "Baskı anlarında en çok {fragment} hissedilebilir.",
            "cinematic": "Perde gerildiğinde gölge {fragment} yerinden yükselir.",
            "intimate": "Kırılgan yerde bu, {fragment} olarak açığa çıkabilir.",
        },
    }
    family_templates = templates.get(role) or templates["micro"]
    template = family_templates.get(family) or family_templates["direct"]
    return ensure_sentence(template.format(fragment=lower))
