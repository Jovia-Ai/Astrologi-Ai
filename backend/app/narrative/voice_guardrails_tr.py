from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

HARD_BANNED_WORDS = (
    "mekanizma",
    "aktivasyon",
    "proses",
)

ASTRO_TECHNICAL_PATTERNS = (
    ("house_number", re.compile(r"\b(?:[1-9]|1[0-2])\.\s*ev\b", re.IGNORECASE)),
    ("transit_word", re.compile(r"\btransit\b", re.IGNORECASE)),
    ("orb_word", re.compile(r"\borb\b", re.IGNORECASE)),
    ("aspect_word", re.compile(r"\baçı\b|\baspekt\b", re.IGNORECASE)),
    ("aspect_name", re.compile(r"\b(?:kare|üçgen|karşıt|sekstil|sextil|konjunksiyon|opozisyon|kavuşum)\b", re.IGNORECASE)),
    ("planet_name", re.compile(r"\b(?:Satürn|Jüpiter|Mars|Venüs|Merkür|Güneş|Ay|Neptün|Uranüs|Plüton)\b", re.IGNORECASE)),
    ("sign_name", re.compile(r"\b(?:Koç|Boğa|İkizler|Yengeç|Aslan|Başak|Terazi|Akrep|Yay|Oğlak|Kova|Balık)\b", re.IGNORECASE)),
    ("astro_role", re.compile(r"\b(?:dispositor|ruler)\b", re.IGNORECASE)),
)

SCAFFOLD_PATTERNS = (
    ("backing_cliche", re.compile(r"haritanda .+? birbirine bağlı çalıştığı için", re.IGNORECASE)),
    ("uzerinden_calisiyor", re.compile(r"\büzerinden çalışıyor\b", re.IGNORECASE)),
    ("yerden_calisiyor", re.compile(r"\byerden çalışıyor\b", re.IGNORECASE)),
    ("buradaki_esik", re.compile(r"\bburadaki eşik\b", re.IGNORECASE)),
    ("bu_surec_scaffold", re.compile(r"\bbu süreç\b", re.IGNORECASE)),
    ("bu_yapi_scaffold", re.compile(r"\bbu yapı\b", re.IGNORECASE)),
    ("bu_dinamik_scaffold", re.compile(r"\bbu dinamik\b", re.IGNORECASE)),
    ("bu_kalip_scaffold", re.compile(r"\bbu kalıp\b", re.IGNORECASE)),
)

DIRECTIVE_PATTERNS = (
    ("directive_yap", re.compile(r"\byap\b", re.IGNORECASE)),
    ("directive_uygula", re.compile(r"\buygula\b", re.IGNORECASE)),
    ("directive_olmali", re.compile(r"\bolmalı\b", re.IGNORECASE)),
    ("directive_lazim", re.compile(r"\blazım\b", re.IGNORECASE)),
    ("directive_gerekli", re.compile(r"\bgerekli\b", re.IGNORECASE)),
)

ORGANIC_PARALLEL_PHILOSOPHY_PATTERNS = (
    ("parallel_same_thing", re.compile(r"\baynı şey değil\b", re.IGNORECASE)),
    ("parallel_same_place", re.compile(r"\baynı yerde durmuyor\b", re.IGNORECASE)),
    ("parallel_miss_the_difference", re.compile(r"\barasındaki farkı kaçırma\b", re.IGNORECASE)),
)

ORGANIC_SEGMENT_CONNECTOR_PATTERNS = (
    ("segment_bu_en_cok", re.compile(r"\bbu en çok\b", re.IGNORECASE)),
    ("segment_bunun_altinda", re.compile(r"\bbunun altında şu fark çalışıyor\b", re.IGNORECASE)),
    ("segment_risk_label", re.compile(r"\brisk:\b", re.IGNORECASE)),
    ("segment_kasini_gelistiriyor", re.compile(r"\bbu dönem sende\b[^.!?]{0,40}\bkasını geliştiriyor\b", re.IGNORECASE)),
)

ORGANIC_ANTHROPOMORPHIC_PATTERNS = (
    (
        "anthropomorphic_abstract_subject",
        re.compile(
            r"\b(?:ağırlık|refleks|söz|yön duygusu|güven|yakınlık|süreç|yapı|dinamik|eşik)\b"
            r"[^.!?]{0,50}\b(?:istiyor|arıyor|söylüyor|soruyor|çağırıyor|talep ediyor|bekliyor|adını istiyor)\b",
            re.IGNORECASE,
        ),
    ),
)

ORGANIC_TRIPLE_MODIFIER_PATTERNS = (
    (
        "triple_daha_stack",
        re.compile(r"\bdaha\s+\w+\b(?:[^.!?]{0,24}\bdaha\s+\w+\b){2,}", re.IGNORECASE),
    ),
)

ORGANIC_HEAVY_GRAVITAS_PATTERNS = (
    ("heavy_borc", re.compile(r"\bborç\b", re.IGNORECASE)),
    ("heavy_sucluluk", re.compile(r"\bsuçluluk\b", re.IGNORECASE)),
    ("heavy_yargi", re.compile(r"\byargı\b", re.IGNORECASE)),
    ("heavy_hata", re.compile(r"\bhata\b", re.IGNORECASE)),
)

PATTERN_NAME_FORBIDDEN_PATTERNS = (
    ("technical_planet_pair", re.compile(r"\b(?:Ay|Merkür|Venüs|Mars|Jüpiter|Satürn|Uranüs|Neptün|Plüton)\b", re.IGNORECASE)),
    ("technical_house", re.compile(r"\b(?:[1-9]|1[0-2])\.\s*ev\b", re.IGNORECASE)),
    ("astro_jargon", re.compile(r"\b(?:projeksiyon|satürnyen|neptünyen|uranüsyen|plütonik|dispositor|ruler)\b", re.IGNORECASE)),
    ("clinical_jargon", re.compile(r"\b(?:kaçınmacı bağlanma stili|bağlanma stili)\b", re.IGNORECASE)),
    ("judgmental_word", re.compile(r"\b(?:mükemmeliyetçilik)\b", re.IGNORECASE)),
)

PUBLIC_COPY_EXEMPTIONS = (
    re.compile(r"\bkapının eşiğinde\b", re.IGNORECASE),
    re.compile(r"\baile dinamiği\b", re.IGNORECASE),
    re.compile(r"\biç yapı\b", re.IGNORECASE),
    re.compile(r"\bdönüşüm süreci\b", re.IGNORECASE),
)

ALLOWLIST_HEDGE_LAYERS = {"cause", "effect", "shadow"}
FORBIDDEN_HEDGE_LAYERS = {"mechanism", "potential"}
HEDGE_PATTERN = re.compile(r"\b\w*(?:ebilir|abilir)\w*\b|\bolabilir\b", re.IGNORECASE)
BU_DONEM_OPENING = re.compile(r"^\s*Bu dönem\b", re.IGNORECASE)
RUN_ON_SENTENCE_PATTERN = re.compile(r"(?<=[a-zçğıöşü]) (?=(Bugün|Ama|O yüzden|Bu yeni bir başlık değil)\b)")

CONTENT_SCAN_PATHS = (
    "backend/app/transit/content/tr/style_do.v1.json",
    "backend/app/transit/content/tr/upper_meaning.v1.json",
    "backend/app/transit/content/tr/period_space.v1.json",
    "backend/app/transit/content/tr/period_space/house_story_templates.json",
    "backend/app/transit/content/tr/period_space/house_labels.json",
    "backend/app/transit/content/tr/period_space/axis_pack.json",
    "backend/app/transit/narrative/phrase_lib_tr.py",
    "backend/app/natal/narrative/phrase_lib_tr_profile.py",
    "backend/app/natal/narrative/phrase_lib_tr_natal.py",
)

LIFE_CHAPTER_COOKBOOK_PATTERNS = (
    ("generic_saturn_return", re.compile(r"\b(?:saturn|satürn)\s+return\s*=\s*sorumluluk dönemi\b", re.IGNORECASE)),
    ("generic_nodal_return", re.compile(r"\b(?:nodal|ay düğümü)\s+return\s*=\s*kader dönemi\b", re.IGNORECASE)),
    ("generic_chapter_formula", re.compile(r"\b(?:saturn|satürn|jupiter|jüpiter|nodal|ay düğümü)[^.!?]{0,32}=\s*[^.!?]{0,24}dönemi\b", re.IGNORECASE)),
)

LIFE_CHAPTER_PREDICTION_PATTERNS = (
    ("prediction_guaranteed_outcome", re.compile(r"\b(?:kesin|mutlaka)\b", re.IGNORECASE)),
    ("prediction_future_claim", re.compile(r"\b\w+(?:acaksın|eceksin)\b", re.IGNORECASE)),
    ("prediction_love_money_career", re.compile(r"\b(?:terfi alacaksın|para kazanacaksın|aşkı bulacaksın|evleneceksin)\b", re.IGNORECASE)),
)

LIFE_CHAPTER_SUBTLE_PREDICTION_BANS = (
    ("soft_prediction_new_beginning", re.compile(r"\b(?:yeni bir başlangıç olabilir)\b", re.IGNORECASE)),
    ("soft_prediction_opening_doors", re.compile(r"\b(?:yeni kapılar açılıyor)\b", re.IGNORECASE)),
    ("soft_prediction_change_will_come", re.compile(r"\b(?:değişim getirecek)\b", re.IGNORECASE)),
    ("probability_claim_struggle", re.compile(r"\b(?:zorlanabilirsin|zorluk yaşayabilirsin)\b", re.IGNORECASE)),
    ("probability_claim_maybe_notice", re.compile(r"\b(?:belki [^.!?]{0,32}fark edersin)\b", re.IGNORECASE)),
    ("outcome_assertion_life_changes", re.compile(r"\b(?:hayatın değişiyor)\b", re.IGNORECASE)),
    ("outcome_assertion_relationship_change", re.compile(r"\b(?:ilişkilerinde dönüşüm yaşanıyor)\b", re.IGNORECASE)),
    ("outcome_assertion_career_progress", re.compile(r"\b(?:kariyerinde ilerleme olacak)\b", re.IGNORECASE)),
    ("cosmic_agency_universe", re.compile(r"\b(?:evren sana [^.!?]{0,40}söylüyor)\b", re.IGNORECASE)),
    ("cosmic_agency_stars", re.compile(r"\b(?:yıldızlar [^.!?]{0,40}işaret ediyor)\b", re.IGNORECASE)),
    ("cosmic_agency_saturn_subject", re.compile(r"\b(?:saturn|satürn)\s+sana\s+öğretiyor\b", re.IGNORECASE)),
)


def _is_exempt(text: str) -> bool:
    return any(pattern.search(text) for pattern in PUBLIC_COPY_EXEMPTIONS)


def _issue(code: str, message: str, *, match: str | None = None) -> dict:
    out = {"code": code, "message": message}
    if match:
        out["match"] = match
    return out


def find_forbidden_public_copy_issues(
    text: str,
    *,
    allowlist: set[str] | None = None,
    check_directives: bool = True,
) -> list[dict]:
    allow = allowlist or set()
    issues: list[dict] = []
    if not text.strip():
        return issues

    for word in HARD_BANNED_WORDS:
        if word in allow:
            continue
        if re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE):
            issues.append(_issue("hard_banned_word", f"Hard-banned word detected: {word}", match=word))

    for code, pattern in SCAFFOLD_PATTERNS:
        match = pattern.search(text)
        if match and not _is_exempt(text):
            issues.append(_issue(code, "Forbidden scaffold pattern detected.", match=match.group(0)))

    if check_directives:
        for code, pattern in DIRECTIVE_PATTERNS:
            match = pattern.search(text)
            if match:
                issues.append(_issue(code, "Directive/coaching verb detected.", match=match.group(0)))

    if RUN_ON_SENTENCE_PATTERN.search(text):
        issues.append(_issue("run_on_sentence_transition", "Possible missing sentence boundary before discourse transition."))

    return issues


def find_technical_leakage(text: str, *, surface: str) -> list[dict]:
    if surface in {"proof", "debug", "explainability"}:
        return []

    issues: list[dict] = []
    for code, pattern in ASTRO_TECHNICAL_PATTERNS:
        match = pattern.search(text)
        if match:
            issues.append(_issue(code, "Technical astro term leaked into public body.", match=match.group(0)))
    return issues


def validate_pattern_name(name: str) -> list[dict]:
    text = str(name or "").strip()
    if not text:
        return [_issue("empty_pattern_name", "Pattern name cannot be empty.")]

    issues: list[dict] = []
    for code, pattern in PATTERN_NAME_FORBIDDEN_PATTERNS:
        match = pattern.search(text)
        if match:
            issues.append(_issue(code, "Pattern name contains forbidden technical, jargon, or judgmental wording.", match=match.group(0)))
    return issues


def validate_olabilir_usage(text: str, *, layer: str) -> list[dict]:
    normalized_layer = str(layer or "").strip().lower()
    if normalized_layer in ALLOWLIST_HEDGE_LAYERS:
        return []

    issues: list[dict] = []
    for match in HEDGE_PATTERN.finditer(text):
        token = match.group(0)
        if normalized_layer in FORBIDDEN_HEDGE_LAYERS:
            issues.append(_issue("hedge_forbidden_in_layer", f"`{token}` is not allowed in {normalized_layer} layer.", match=token))
    return issues


def validate_rotation_pair(previous_text: str, current_text: str) -> list[dict]:
    if BU_DONEM_OPENING.search(previous_text or "") and BU_DONEM_OPENING.search(current_text or ""):
        return [_issue("repeated_bu_donem_opening", "Repeated `Bu dönem...` opening across adjacent blocks.")]
    return []


def find_organic_period_copy_issues(
    text: str,
    *,
    allow_heavy_gravitas: bool = False,
) -> list[dict]:
    token = str(text or "").strip()
    if not token:
        return []

    issues: list[dict] = []
    for pattern_group in (
        ORGANIC_PARALLEL_PHILOSOPHY_PATTERNS,
        ORGANIC_SEGMENT_CONNECTOR_PATTERNS,
        ORGANIC_ANTHROPOMORPHIC_PATTERNS,
        ORGANIC_TRIPLE_MODIFIER_PATTERNS,
    ):
        for code, pattern in pattern_group:
            match = pattern.search(token)
            if match:
                issues.append(_issue(code, "Organic period prose guardrail failed.", match=match.group(0)))

    if not allow_heavy_gravitas:
        for code, pattern in ORGANIC_HEAVY_GRAVITAS_PATTERNS:
            match = pattern.search(token)
            if match:
                issues.append(_issue(code, "Heavy emotional gravitas drift detected.", match=match.group(0)))

    return issues


def validate_life_chapter_selected_meaning(text: str) -> list[dict]:
    token = str(text or "").strip()
    if not token:
        return [_issue("empty_selected_meaning", "Life chapter selected_meaning cannot be empty.")]

    issues: list[dict] = []
    for code, pattern in LIFE_CHAPTER_COOKBOOK_PATTERNS:
        match = pattern.search(token)
        if match:
            issues.append(_issue(code, "Cookbook chapter definition detected.", match=match.group(0)))

    for code, pattern in LIFE_CHAPTER_PREDICTION_PATTERNS:
        match = pattern.search(token)
        if match:
            issues.append(_issue(code, "Predictive or guaranteed-outcome chapter meaning detected.", match=match.group(0)))

    for code, pattern in LIFE_CHAPTER_SUBTLE_PREDICTION_BANS:
        match = pattern.search(token)
        if match:
            issues.append(_issue(code, "Subtle predictive, outcome-assertive, or cosmic-agency phrasing detected.", match=match.group(0)))

    if len(token.split()) < 4:
        issues.append(_issue("selected_meaning_too_short", "selected_meaning must be more specific than a short label."))

    return issues


def load_json_baseline(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def iter_content_scan_paths(root: str | Path = ".") -> Iterable[Path]:
    base = Path(root)
    for relative in CONTENT_SCAN_PATHS:
        yield base / relative
