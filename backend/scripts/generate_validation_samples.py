from __future__ import annotations

import argparse
import copy
import difflib
import hashlib
import json
import re
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import swisseph as swe

from app.api.routes import transits
from app.astro.chart_engine import builder as chart_builder
from app.astro.chart_engine.builder import LocationData
from app.core.config import settings
from app.core.ephemeris_guard import assert_ephemeris_ready
from app.narrative.voice_guardrails_tr import (
    find_forbidden_public_copy_issues,
    find_technical_leakage,
)
from app.transit import astro_event_v2
from app.transit.narrative import period_voice_policy
from app.transit.narrative.astrolog_narrative_engine import (
    PeriodStoryContext,
    build_period_story,
    build_story_track_copy,
    infer_story_track_id,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_PATH = REPO_ROOT / "backend/tests/_fixtures/natal_v8_baseline.json"
NATAL_ARTIFACT_DIR = REPO_ROOT / "backend/tests/_artifacts/natal_v8_baseline"
DEFAULT_OUTPUT_MD = REPO_ROOT / "docs/voice/sample_validation_pack.md"
DEFAULT_OUTPUT_JSON = REPO_ROOT / "docs/voice/sample_validation_samples.json"


@dataclass(frozen=True)
class ValidationCase:
    fixture_id: str
    window_start: str
    window_end: str
    selected_date: str


PERIOD_DAILY_CASES: tuple[ValidationCase, ...] = (
    ValidationCase("fix02_capricorn_stellium", "2026-05-01", "2026-05-31", "2026-05-03"),
    ValidationCase("fix03_pisces_cancer_water", "2026-05-01", "2026-05-31", "2026-05-03"),
    ValidationCase("fix04_h10_career_stellium", "2026-05-01", "2026-05-31", "2026-05-03"),
    ValidationCase("fix05_t_square_tense", "2026-05-01", "2026-05-31", "2026-05-03"),
    ValidationCase("fix07_aries_libra_nodes", "2026-05-01", "2026-05-31", "2026-05-03"),
)

NATAL_SANITY_CASES: tuple[str, ...] = (
    "fix02_capricorn_stellium",
    "fix04_h10_career_stellium",
    "fix05_t_square_tense",
)

PERIOD_QUESTIONS = (
    'Hangisi daha "beni görüyor" hissi veriyor?',
    "Hangisi generic horoscope gibi?",
    "Hangisi fazla teknik?",
    "Hangisi fazla koçluk/motivasyon gibi?",
    "Hangisini tekrar okumak isterdin?",
    "Hangisinde cümleler birbirine benziyor?",
)

NATAL_SANITY_QUESTIONS = (
    "Akışta beklenmedik kırılma veya dağınıklık var mı?",
    "Beklenenden farklı bir astro term kalıbı var mı?",
    "SHOU vNext tonu ile açık çelişen bir bölüm var mı?",
    "Bu chart için bariz bir içerik regresyonu hissediliyor mu?",
)

DECISION_CRITERIA = {
    "A": "Period B/C clearly wins → runtime alignment ve daily migration devam eder.",
    "B": "Period no difference → canonical policy renderer görünürlüğü tekrar kontrol edilir.",
    "C": "Period better but Daily weak → PR-5 Daily Today-ness Signal ve PR-7 Daily Canonical Renderer önceliklenir.",
    "D": "Legacy wins → legacy insight rescue yapılır; cleanup durur.",
    "E": "Mixed → frame / scene / proof / daily trigger / natal backing bazında parçalanır.",
}

NUMERIC_RATING_FIELDS = (
    "seen_score",
    "generic_score",
    "too_technical_score",
    "coaching_motivation_score",
    "reread_score",
    "repetition_score",
)

CHOICE_FIELDS = (
    "best_overall",
    "worst_overall",
)

MIN_BODY_CHARS = 30
SIMILARITY_THRESHOLD = 0.85
CROSS_CHART_DUPLICATION_THRESHOLD = 0.95
EXCEPTION_LEAK_PATTERNS = (
    re.compile(r"swisseph", re.IGNORECASE),
    re.compile(r"opencage", re.IGNORECASE),
    re.compile(r"traceback", re.IGNORECASE),
    re.compile(r"keyerror", re.IGNORECASE),
    re.compile(r"httpexception", re.IGNORECASE),
)
MORPHOLOGY_PATTERNS = (
    re.compile(r"\b(?:Mars|Satürn|Jüpiter|Merkür|Venüs|Neptün|Uranüs|Plüton|Güneş|Ay)'ün\b"),
)
BU_DONEM_COUNT_PATTERN = re.compile(r"\bBu dönem\b", re.IGNORECASE)
_RUNTIME_READY = False
REVIEWER_POST_PROCESS_RULES = [
    "turkish_char_normalization",
    "repeated_opening_reduction",
    "system_scaffold_softening",
    "threshold_word_softening",
]
SYSTEM_SCAFFOLD_PATTERNS = (
    re.compile(r"Bu dönem doğum haritandaki [^.]+ özellikle çalıştırıyor\.", re.IGNORECASE),
    re.compile(r"Bu dönem hayatının bir alanı daha görünür hale geliyor[^.]*\.", re.IGNORECASE),
    re.compile(r"Bu dönem görünürlük kazanan eşik[^.]*\.", re.IGNORECASE),
)
THRESHOLD_WORD_PATTERN = re.compile(r"\beşik\b", re.IGNORECASE)
TURKISH_CHARACTER_PATTERNS = (
    re.compile(r"\bInsa\b"),
    re.compile(r"\bTemasi\b"),
    re.compile(r"\bDerinlesiyor\b"),
    re.compile(r"\bIlişk"),
    re.compile(r"\bIş\b"),
)
TURKISH_DISPLAY_REPLACEMENTS = {
    "Insa": "İnşa",
    "Temasi": "Teması",
    "Derinlesiyor": "Derinleşiyor",
    "Ilişk": "İlişk",
    "Iş": "İş",
}
REPEATED_OPENING_START_PATTERN = re.compile(r"(?:(?<=\.)|^)\s*Bu dönem\s+", re.IGNORECASE)
ISOLATED_NAKED_FRAME_PATTERN = re.compile(r"^Bu, [^.]{0,70} değil\.$", re.MULTILINE)


def _load_fixture_index() -> dict[str, dict[str, Any]]:
    payload = json.loads(FIXTURES_PATH.read_text())
    fixtures = payload.get("fixtures") or []
    return {
        str(item.get("id") or ""): dict(item)
        for item in fixtures
        if isinstance(item, Mapping) and str(item.get("id") or "").strip()
    }


def _ensure_validation_runtime_ready() -> None:
    global _RUNTIME_READY
    if _RUNTIME_READY:
        return
    assert_ephemeris_ready(settings.swisseph_path)
    swe.set_ephe_path(settings.swisseph_path)
    _RUNTIME_READY = True


def _fixture_location(fixture: Mapping[str, Any]) -> LocationData:
    return LocationData(
        latitude=float(fixture.get("birth_latitude")),
        longitude=float(fixture.get("birth_longitude")),
        timezone=str(fixture.get("birth_timezone") or ""),
        label=str(fixture.get("birth_place") or ""),
    )


@contextmanager
def _fixture_location_bypass(fixture: Mapping[str, Any]):
    target_place = str(fixture.get("birth_place") or "").strip().lower()
    location = _fixture_location(fixture)
    original_builder_fetch = chart_builder.fetch_location
    original_astro_event_fetch = astro_event_v2.fetch_location

    def _patched_fetch_location(city: str) -> LocationData:
        city_key = str(city or "").strip().lower()
        if city_key == target_place:
            return location
        return original_builder_fetch(city)

    chart_builder.fetch_location = _patched_fetch_location
    astro_event_v2.fetch_location = _patched_fetch_location
    try:
        yield
    finally:
        chart_builder.fetch_location = original_builder_fetch
        astro_event_v2.fetch_location = original_astro_event_fetch


def _request_from_fixture(case: ValidationCase, fixture: Mapping[str, Any]) -> transits.TransitNarrativeRequest:
    return transits.TransitNarrativeRequest(
        birth_date=str(fixture.get("birth_date") or ""),
        birth_time=str(fixture.get("birth_time") or ""),
        birth_place=str(fixture.get("birth_place") or ""),
        birth_latitude=fixture.get("birth_latitude"),
        birth_longitude=fixture.get("birth_longitude"),
        birth_timezone=str(fixture.get("birth_timezone") or ""),
        start=case.window_start,
        end=case.window_end,
        tz=str(fixture.get("birth_timezone") or ""),
        transit_place=str(fixture.get("birth_place") or ""),
        transit_latitude=fixture.get("birth_latitude"),
        transit_longitude=fixture.get("birth_longitude"),
        transit_timezone=str(fixture.get("birth_timezone") or ""),
        selected_date=case.selected_date,
        include_best_times=False,
        response_mode="public_only",
        payload_profile="full",
        locale="tr",
    )


def _build_live_public_payload(case: ValidationCase, fixture: Mapping[str, Any]) -> dict[str, Any]:
    _ensure_validation_runtime_ready()
    request = _request_from_fixture(case, fixture)
    with _fixture_location_bypass(fixture):
        response = transits.build_transit_narrative(request)
    public = response.get("public") if isinstance(response.get("public"), Mapping) else {}
    return dict(public)


def _find_spine_card(period_core: Mapping[str, Any]) -> dict[str, Any]:
    featured = period_core.get("featured_events") if isinstance(period_core.get("featured_events"), Sequence) else []
    if featured:
        first = featured[0]
        if isinstance(first, Mapping):
            return dict(first)
    return {}


def _derive_natal_promise_themes(event_cards: Sequence[Mapping[str, Any]]) -> list[str]:
    promise_themes: list[str] = []
    for card in event_cards:
        np = card.get("natal_promise") if isinstance(card.get("natal_promise"), Mapping) else {}
        drivers = np.get("drivers") if isinstance(np.get("drivers"), Sequence) else []
        for driver in drivers:
            if isinstance(driver, Mapping):
                label = str(driver.get("label") or driver.get("theme") or "").strip()
            else:
                label = str(driver or "").strip()
            if label and label not in promise_themes:
                promise_themes.append(label)
            if len(promise_themes) >= 3:
                return promise_themes
    return promise_themes


def _join_paragraphs(*parts: str) -> str:
    cleaned = [str(part).strip() for part in parts if str(part).strip()]
    return "\n\n".join(cleaned)


def _normalize_text(text: str) -> str:
    normalized = re.sub(r"\s+", " ", str(text or "").strip().lower())
    return normalized


def _similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(a=_normalize_text(a), b=_normalize_text(b)).ratio()


def _contains_exception_leak(text: str) -> list[str]:
    flags: list[str] = []
    for pattern in EXCEPTION_LEAK_PATTERNS:
        if pattern.search(text or ""):
            flags.append("exception_leak")
            break
    return flags


def _morphology_flags(text: str) -> list[str]:
    flags: list[str] = []
    for pattern in MORPHOLOGY_PATTERNS:
        if pattern.search(text or ""):
            flags.append("morphology_issue")
            break
    return flags


def _repeated_bu_donem_flags(text: str) -> list[str]:
    matches = BU_DONEM_COUNT_PATTERN.findall(text or "")
    return ["repeated_bu_donem_opening"] if len(matches) > 1 else []


def _quality_flags_for_text(text: str, *, surface: str, lint_exempt: bool) -> list[str]:
    flags: list[str] = []
    flags.extend(_contains_exception_leak(text))
    flags.extend(_morphology_flags(text))
    flags.extend(_repeated_bu_donem_flags(text))
    if not lint_exempt:
        flags.extend(issue["code"] for issue in find_forbidden_public_copy_issues(text))
        flags.extend(issue["code"] for issue in find_technical_leakage(text, surface=surface))
    return sorted(set(flags))


def _base_variant(
    *,
    source_variant: str,
    headline: str,
    body: str,
    guidance: str = "",
    debug: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "source_variant": source_variant,
        "headline": str(headline or "").strip(),
        "body": str(body or "").strip(),
        "guidance": str(guidance or "").strip(),
        "debug": dict(debug or {}),
    }


def _period_legacy_variant(period_core: Mapping[str, Any]) -> dict[str, Any]:
    spine = _find_spine_card(period_core)
    root_causes = period_core.get("_debug_root_causes") if isinstance(period_core.get("_debug_root_causes"), Sequence) else []
    track_id = infer_story_track_id(spine, root_causes)
    story = build_story_track_copy(track_id, spine)
    return _base_variant(
        source_variant="legacy_period_output",
        headline=str(period_core.get("title") or "").strip(),
        body=_join_paragraphs(
            str(story.get("period_opening") or ""),
            str(story.get("big_picture") or ""),
            str(story.get("mechanism") or ""),
            str(story.get("growth_edge") or ""),
        ),
        debug={"track_id": track_id, "source": "build_story_track_copy"},
    )


@contextmanager
def _manifestation_context_disabled():
    original = period_voice_policy.build_manifestation_context
    period_voice_policy.build_manifestation_context = lambda **_kwargs: {}
    try:
        yield
    finally:
        period_voice_policy.build_manifestation_context = original


def _period_context(
    period_core: Mapping[str, Any],
    event_cards: Sequence[Mapping[str, Any]],
) -> PeriodStoryContext:
    return PeriodStoryContext(
        period_core=dict(period_core),
        chart_snapshot={},
        natal_promise={"themes": _derive_natal_promise_themes(event_cards)},
        canonical_period_spine=dict(period_core.get("canonical_period_spine") or {})
        if isinstance(period_core.get("canonical_period_spine"), Mapping)
        else {},
        locale="tr",
        enable_fun=True,
    )


def _period_canonical_variant(
    period_core: Mapping[str, Any],
    event_cards: Sequence[Mapping[str, Any]],
    *,
    include_manifestation_context: bool,
) -> dict[str, Any]:
    ctx = _period_context(period_core, event_cards)
    if include_manifestation_context:
        narr = build_period_story(ctx)
        source_variant = "canonical_period_plus_manifestation_context"
    else:
        with _manifestation_context_disabled():
            narr = build_period_story(ctx)
        source_variant = "canonical_period_spine_plus_voice_policy"
    return _base_variant(
        source_variant=source_variant,
        headline=str(period_core.get("title") or "").strip(),
        body=_join_paragraphs(
            narr.period_opening,
            narr.big_picture,
            narr.mechanism,
            narr.growth_edge,
        ),
        debug=dict(narr.debug or {}),
    )


def _first_daily_card(public_payload: Mapping[str, Any]) -> dict[str, Any]:
    cards = public_payload.get("daily_event_cards") if isinstance(public_payload.get("daily_event_cards"), Sequence) else []
    for card in cards:
        if isinstance(card, Mapping):
            return dict(card)
    cards = public_payload.get("event_cards") if isinstance(public_payload.get("event_cards"), Sequence) else []
    for card in cards:
        if isinstance(card, Mapping):
            return dict(card)
    return {}


def _daily_legacy_variant(public_payload: Mapping[str, Any]) -> dict[str, Any]:
    card = _first_daily_card(public_payload)
    headline = str(card.get("signal_label_tr") or card.get("felt_line_tr") or "").strip()
    body = _join_paragraphs(
        str(card.get("felt_line_tr") or ""),
        str(card.get("why_it_feels_this_way_tr") or ""),
    )
    guidance = str(card.get("guidance_micro_tr") or "").strip()
    return _base_variant(
        source_variant="legacy_daily_output",
        headline=headline,
        body=body,
        guidance=guidance,
        debug={"source": "daily_event_card_legacy_humanizer"},
    )


def _daily_current_variant(public_payload: Mapping[str, Any]) -> dict[str, Any]:
    synthesis = public_payload.get("daily_synthesis") if isinstance(public_payload.get("daily_synthesis"), Mapping) else {}
    candidate = synthesis.get("today_story_candidate") if isinstance(synthesis.get("today_story_candidate"), Mapping) else {}
    debug = {
        "story_type": candidate.get("story_type"),
        "spine_line": candidate.get("primary_spine_line"),
        "event_nature": candidate.get("event_nature"),
        "meaning_intent": (((candidate.get("debug") or {}) if isinstance(candidate.get("debug"), Mapping) else {}).get("voice_policy_debug") or {}).get("meaning_intent"),
        "rhetorical_frame": (((candidate.get("debug") or {}) if isinstance(candidate.get("debug"), Mapping) else {}).get("voice_policy_debug") or {}).get("rhetorical_frame"),
        "manifestation_context": ((((candidate.get("debug") or {}) if isinstance(candidate.get("debug"), Mapping) else {}).get("voice_policy_debug") or {}).get("manifestation_context") or {}),
        "source": "daily_synthesis_current_runtime",
        "today_story_candidate_present": bool(candidate),
    }
    return _base_variant(
        source_variant="today_story_candidate_plus_current_daily_synthesis",
        headline=str(synthesis.get("headline") or "").strip(),
        body=str(synthesis.get("body") or "").strip(),
        guidance=str(synthesis.get("guidance") or "").strip(),
        debug=debug,
    )


def _find_event_by_id(cards: Sequence[Mapping[str, Any]], event_id: str | None) -> dict[str, Any]:
    target = str(event_id or "").strip()
    if not target:
        return {}
    for card in cards:
        if str(card.get("event_id") or "").strip() == target:
            return dict(card)
    return {}


def _mock_today_delta_signal(trigger_card: Mapping[str, Any], story_type: str) -> str:
    body = str(trigger_card.get("transit_body") or "").strip()
    aspect = str(trigger_card.get("aspect") or "").strip()
    orb = trigger_card.get("orb_deg")
    if story_type == "period_continuation":
        return "Bugün belirgin bir tek olaydan çok, birkaç küçük işaret bu hattın çalıştığını hatırlatıyor."
    if body and aspect:
        orb_piece = f" Yakınlık {orb:.2f}°." if isinstance(orb, (int, float)) else ""
        return f"Bugün {body} {aspect} hattı konuyu daha görünür yapıyor.{orb_piece}".strip()
    return "Bugün küçük bir sinyal temayı dünden daha sesli hale getiriyor."


def _mock_scene_aware_daily_variant(public_payload: Mapping[str, Any]) -> dict[str, Any]:
    synthesis = public_payload.get("daily_synthesis") if isinstance(public_payload.get("daily_synthesis"), Mapping) else {}
    candidate = synthesis.get("today_story_candidate") if isinstance(synthesis.get("today_story_candidate"), Mapping) else {}
    cards = [dict(card) for card in (public_payload.get("daily_event_cards") or []) if isinstance(card, Mapping)]
    primary = _find_event_by_id(cards, candidate.get("primary_trigger_event_id"))
    voice_debug = ((candidate.get("debug") or {}) if isinstance(candidate.get("debug"), Mapping) else {}).get("voice_policy_debug")
    voice_debug = dict(voice_debug or {}) if isinstance(voice_debug, Mapping) else {}
    manifestation_context = voice_debug.get("manifestation_context")
    manifestation_context = dict(manifestation_context or {}) if isinstance(manifestation_context, Mapping) else {}
    life_scene = str(manifestation_context.get("life_scene") or "").strip()
    story_type = str(candidate.get("story_type") or "").strip() or "daily_flavor"
    event_nature = str(candidate.get("event_nature") or "").strip()
    chapter_role = str(candidate.get("chapter_role") or "").strip()
    trigger_line = _mock_today_delta_signal(primary, story_type)

    if story_type == "quiet_day":
        headline = "Bugün tema arka planda."
        body = "Bugün büyük bir tetik olmadan, dönem arkada sessizce çalışıyor."
        guidance = "Zorla anlam yüklemek yerine hangisinin gerçekten öne çıktığını beklemek daha doğru."
    else:
        line_intro = "Bugün bu konu dünden daha sesli." if story_type == "period_triggered_today" else "Bugün tema tek bir olaydan çok, alttan gelen bir devam hissiyle çalışıyor."
        scene_part = (
            f" Özellikle {life_scene} tarafında görünür oluyor."
            if life_scene
            else ""
        )
        nature_part = (
            f" Ana hareket daha çok {event_nature} tarafında."
            if event_nature
            else ""
        )
        role_part = (
            f" Günün tonu {chapter_role} gibi ilerliyor."
            if chapter_role
            else ""
        )
        headline = str(synthesis.get("headline") or "Bugün öne çıkan tema").strip()
        body = _join_paragraphs(
            f"{line_intro}{scene_part} {trigger_line}".strip(),
            f"{nature_part}{role_part}".strip(),
        )
        guidance = str(candidate.get("growth_edge") or "").strip() or str(synthesis.get("guidance") or "").strip()

    return _base_variant(
        source_variant="mock_today_delta_signal_plus_scene_aware_daily",
        headline=headline,
        body=body,
        guidance=guidance,
        debug={
            "story_type": story_type,
            "spine_line": candidate.get("primary_spine_line"),
            "event_nature": event_nature,
            "meaning_intent": voice_debug.get("meaning_intent"),
            "rhetorical_frame": voice_debug.get("rhetorical_frame"),
            "manifestation_context": manifestation_context,
            "life_scene": life_scene,
            "source": "script_mock_scene_aware_daily",
            "today_story_candidate_present": bool(candidate),
        },
    )


def _blind_permutation(seed: str) -> list[str]:
    labels = ["A", "B", "C"]
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    ranked = sorted(((digest[i : i + 2], label) for i, label in zip(range(0, 6, 2), labels)), key=lambda item: item[0])
    return [label for _, label in ranked]


def _blind_wrap(case_id: str, surface: str, variants: Sequence[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    blind_labels = _blind_permutation(f"{case_id}:{surface}")
    blind_variants: list[dict[str, Any]] = []
    answer_key: dict[str, str] = {}
    for blind_label, variant in zip(blind_labels, variants):
        blind_variant = copy.deepcopy(variant)
        blind_variant["blind_label"] = blind_label
        blind_variants.append(blind_variant)
        answer_key[blind_label] = str(variant.get("source_variant") or "")
    blind_variants.sort(key=lambda item: str(item.get("blind_label") or ""))
    return blind_variants, answer_key


def _artifact_profile_excerpt(fixture_id: str) -> dict[str, Any]:
    artifact_path = NATAL_ARTIFACT_DIR / f"{fixture_id}.json"
    payload = json.loads(artifact_path.read_text())
    profile_v8 = ((payload.get("public") or {}) if isinstance(payload.get("public"), Mapping) else {}).get("profile_v8")
    profile_v8 = dict(profile_v8 or {}) if isinstance(profile_v8, Mapping) else {}
    sections: list[dict[str, str]] = []
    for key in ("identity_axis", "mind", "intimacy"):
        block = profile_v8.get(key)
        if not isinstance(block, Mapping):
            continue
        headline = str(block.get("headline") or "").strip()
        body = str(block.get("body") or "").strip()
        if headline or body:
            sections.append({"slot": key, "headline": headline, "body": body})
    return {
        "source": str(artifact_path.relative_to(REPO_ROOT)),
        "sections": sections[:3],
    }


def _safe_generate_period_daily_case(case: ValidationCase, fixture: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "fixture_id": case.fixture_id,
        "fixture_label": str(fixture.get("label") or case.fixture_id),
        "window_start": case.window_start,
        "window_end": case.window_end,
        "selected_date": case.selected_date,
    }
    try:
        public_payload = _build_live_public_payload(case, fixture)
    except Exception as exc:  # pragma: no cover - env dependent
        result["status"] = "unavailable"
        result["error"] = f"{type(exc).__name__}: {exc}"
        return result

    period_core = dict(public_payload.get("period_core") or {}) if isinstance(public_payload.get("period_core"), Mapping) else {}
    event_cards = [dict(card) for card in (public_payload.get("event_cards") or []) if isinstance(card, Mapping)]
    period_variants = [
        _period_legacy_variant(period_core),
        _period_canonical_variant(period_core, event_cards, include_manifestation_context=False),
        _period_canonical_variant(period_core, event_cards, include_manifestation_context=True),
    ]
    daily_variants = [
        _daily_legacy_variant(public_payload),
        _daily_current_variant(public_payload),
        _mock_scene_aware_daily_variant(public_payload),
    ]
    period_blind, period_key = _blind_wrap(case.fixture_id, "period", period_variants)
    daily_blind, daily_key = _blind_wrap(case.fixture_id, "daily", daily_variants)

    result.update(
        {
            "status": "ok",
            "period_variants": period_blind,
            "daily_variants": daily_blind,
            "runtime_quality": {
                "degraded_path": bool(
                    ((period_core.get("_period_story_debug") or {}) if isinstance(period_core.get("_period_story_debug"), Mapping) else {}).get("degraded_path_active")
                ),
                "degraded_path_reason": str(
                    ((period_core.get("_period_story_debug") or {}) if isinstance(period_core.get("_period_story_debug"), Mapping) else {}).get("degraded_path_reason") or ""
                ),
            },
            "answer_key": {
                "period": period_key,
                "daily": daily_key,
            },
        }
    )
    return result


def _build_natal_sanity_payload(fixture_id: str, fixture: Mapping[str, Any]) -> dict[str, Any]:
    excerpt = _artifact_profile_excerpt(fixture_id)
    combined_text = "\n\n".join(
        _join_paragraphs(str(section.get("headline") or ""), str(section.get("body") or ""))
        for section in excerpt["sections"]
    )
    quality_flags = _quality_flags_for_text(combined_text, surface="body", lint_exempt=True)
    return {
        "fixture_id": fixture_id,
        "fixture_label": str(fixture.get("label") or fixture_id),
        "status": "ok",
        "surface_mode": "legacy_compat",
        "excerpt_source": excerpt["source"],
        "sections": excerpt["sections"],
        "quality_flags": quality_flags,
    }


def _variant_story_metadata(variant: Mapping[str, Any]) -> dict[str, Any]:
    debug = variant.get("debug") if isinstance(variant.get("debug"), Mapping) else {}
    voice_policy_debug = debug.get("period_voice_policy")
    voice_policy_debug = dict(voice_policy_debug or {}) if isinstance(voice_policy_debug, Mapping) else {}
    manifestation_context = (
        debug.get("manifestation_context")
        or debug.get("period_voice_policy_manifestation_context")
        or voice_policy_debug.get("manifestation_context")
    )
    manifestation_context = dict(manifestation_context or {}) if isinstance(manifestation_context, Mapping) else {}
    return {
        "story_type": debug.get("story_type") or voice_policy_debug.get("story_type"),
        "spine_line": debug.get("spine_line") or voice_policy_debug.get("spine_line"),
        "event_nature": debug.get("event_nature") or voice_policy_debug.get("event_nature"),
        "meaning_intent": debug.get("period_voice_policy_meaning_intent") or debug.get("meaning_intent"),
        "rhetorical_frame": debug.get("period_voice_policy_rhetorical_frame") or debug.get("rhetorical_frame"),
        "manifestation_context": manifestation_context,
    }


def _evaluate_variant(
    variant: Mapping[str, Any],
    *,
    surface: str,
    lint_exempt: bool,
) -> dict[str, Any]:
    body = str(variant.get("body") or "").strip()
    headline = str(variant.get("headline") or "").strip()
    combined = _join_paragraphs(headline, body, str(variant.get("guidance") or "").strip())
    quality_flags = _quality_flags_for_text(combined, surface="body", lint_exempt=lint_exempt)
    available = True
    unavailable_reason = ""
    if not body or len(body) < MIN_BODY_CHARS:
        available = False
        unavailable_reason = "empty_body"
    elif "No content generated" in combined:
        available = False
        unavailable_reason = "empty_body"
    elif "exception_leak" in quality_flags:
        available = False
        unavailable_reason = "exception_leak"
    elif surface == "period" and not lint_exempt and any(
        flag in quality_flags
        for flag in (
            "hard_banned_word",
            "backing_cliche",
            "uzerinden_calisiyor",
            "yerden_calisiyor",
            "buradaki_esik",
            "house_number",
            "transit_word",
            "aspect_word",
            "aspect_name",
            "planet_name",
            "sign_name",
            "astro_role",
        )
    ):
        available = False
        unavailable_reason = "lint_violation"

    out = dict(variant)
    out["available"] = available
    out["unavailable_reason"] = unavailable_reason
    out["quality_flags"] = quality_flags
    out.update(_variant_story_metadata(variant))
    return out


def _period_structural_gate(variants: Sequence[dict[str, Any]]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    by_source = {str(variant.get("source_variant") or ""): variant for variant in variants}
    canonical_b = by_source.get("canonical_period_spine_plus_voice_policy")
    canonical_c = by_source.get("canonical_period_plus_manifestation_context")
    for variant in (canonical_b, canonical_c):
        if not isinstance(variant, Mapping):
            reasons.append("missing_canonical_input")
            continue
        debug = variant.get("debug") if isinstance(variant.get("debug"), Mapping) else {}
        if not str(debug.get("period_voice_policy_version") or "").strip():
            reasons.append("missing_canonical_input")
        if not str(debug.get("canonical_period_spine_source") or "").strip():
            reasons.append("missing_canonical_input")
    if isinstance(canonical_b, Mapping):
        if not str(canonical_b.get("meaning_intent") or "").strip():
            reasons.append("missing_canonical_input")
    if isinstance(canonical_c, Mapping):
        life_scene = str((((canonical_c.get("manifestation_context") or {}) if isinstance(canonical_c.get("manifestation_context"), Mapping) else {}).get("life_scene")) or "").strip()
        if not life_scene:
            reasons.append("missing_canonical_input")
        elif life_scene not in str(canonical_c.get("body") or ""):
            reasons.append("missing_manifestation_render")
    return (not reasons, sorted(set(reasons)))


def _daily_structural_gate(variants: Sequence[dict[str, Any]]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    by_source = {str(variant.get("source_variant") or ""): variant for variant in variants}
    current = by_source.get("today_story_candidate_plus_current_daily_synthesis")
    mock = by_source.get("mock_today_delta_signal_plus_scene_aware_daily")
    if isinstance(current, Mapping):
        if not bool((current.get("debug") or {}).get("today_story_candidate_present")):
            reasons.append("missing_canonical_input")
        if not str(current.get("story_type") or "").strip():
            reasons.append("missing_canonical_input")
    else:
        reasons.append("missing_canonical_input")
    if isinstance(mock, Mapping):
        life_scene = str((((mock.get("manifestation_context") or {}) if isinstance(mock.get("manifestation_context"), Mapping) else {}).get("life_scene")) or str((mock.get("debug") or {}).get("life_scene") or "")).strip()
        if not life_scene:
            reasons.append("missing_canonical_input")
        elif life_scene not in str(mock.get("body") or ""):
            reasons.append("missing_manifestation_render")
    else:
        reasons.append("missing_canonical_input")
    return (not reasons, sorted(set(reasons)))


def _pairwise_similarity_flags(variants: Sequence[Mapping[str, Any]]) -> list[str]:
    reasons: list[str] = []
    for i, left in enumerate(variants):
        for right in variants[i + 1 :]:
            if _similarity(str(left.get("body") or ""), str(right.get("body") or "")) > SIMILARITY_THRESHOLD:
                reasons.append("variants_not_distinct")
    return sorted(set(reasons))


def _mark_surface_unavailable(case: dict[str, Any], *, surface: str, reason: str) -> None:
    availability = case.setdefault("surface_availability", {})
    state = availability.setdefault(surface, {"available": True, "reasons": []})
    state["available"] = False
    reasons = state.setdefault("reasons", [])
    if reason not in reasons:
        reasons.append(reason)


def _evaluate_surface_case(case: dict[str, Any], *, surface: str, variants_key: str) -> None:
    lint_exempt = surface == "natal"
    variants = [
        _evaluate_variant(variant, surface=surface, lint_exempt=lint_exempt)
        for variant in case.get(variants_key, [])
        if isinstance(variant, Mapping)
    ]
    case[variants_key] = variants
    availability = case.setdefault("surface_availability", {})
    availability[surface] = {"available": True, "reasons": []}
    if len(variants) != 3:
        _mark_surface_unavailable(case, surface=surface, reason="missing_variant")
        return
    if any(not bool(variant.get("available")) for variant in variants):
        for variant in variants:
            if not bool(variant.get("available")):
                _mark_surface_unavailable(case, surface=surface, reason=str(variant.get("unavailable_reason") or "empty_body"))
    for reason in _pairwise_similarity_flags(variants):
        _mark_surface_unavailable(case, surface=surface, reason=reason)
    structural_ok, structural_reasons = (
        _period_structural_gate(variants) if surface == "period" else _daily_structural_gate(variants)
    )
    if not structural_ok:
        for reason in structural_reasons:
            _mark_surface_unavailable(case, surface=surface, reason=reason)


def _apply_cross_chart_duplication(cases: list[dict[str, Any]], *, surface: str, variants_key: str) -> None:
    signatures: dict[str, list[dict[str, Any]]] = {}
    for case in cases:
        availability = case.get("surface_availability") if isinstance(case.get("surface_availability"), Mapping) else {}
        if not bool(((availability.get(surface) or {}) if isinstance(availability.get(surface), Mapping) else {}).get("available")):
            continue
        variants = [variant for variant in case.get(variants_key, []) if isinstance(variant, Mapping)]
        signature = "||".join(_normalize_text(str(variant.get("body") or "")) for variant in variants)
        signatures.setdefault(signature, []).append(case)
    for group in signatures.values():
        if len(group) < 2:
            continue
        reference = group[0]
        ref_variants = [variant for variant in reference.get(variants_key, []) if isinstance(variant, Mapping)]
        for case in group[1:]:
            variants = [variant for variant in case.get(variants_key, []) if isinstance(variant, Mapping)]
            pair_scores = [
                _similarity(str(left.get("body") or ""), str(right.get("body") or ""))
                for left, right in zip(ref_variants, variants)
            ]
            if pair_scores and min(pair_scores) > CROSS_CHART_DUPLICATION_THRESHOLD:
                _mark_surface_unavailable(reference, surface=surface, reason="cross_chart_duplication")
                _mark_surface_unavailable(case, surface=surface, reason="cross_chart_duplication")


def _pack_readiness(cases: Sequence[Mapping[str, Any]], natal_cases: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    usable_period = sum(
        1
        for case in cases
        if bool((((case.get("surface_availability") or {}) if isinstance(case.get("surface_availability"), Mapping) else {}).get("period") or {}).get("available"))
    )
    usable_daily = sum(
        1
        for case in cases
        if bool((((case.get("surface_availability") or {}) if isinstance(case.get("surface_availability"), Mapping) else {}).get("daily") or {}).get("available"))
    )
    usable_natal = sum(1 for case in natal_cases if str(case.get("status") or "") == "ok")
    validation_ready = usable_period >= 4 and usable_daily >= 4 and usable_natal >= 3
    period_only_validation_ready = usable_period >= 4 and usable_natal >= 3
    return {
        "usable_period_charts": usable_period,
        "usable_daily_charts": usable_daily,
        "usable_natal_sanity_charts": usable_natal,
        "validation_ready": validation_ready,
        "period_only_validation_ready": period_only_validation_ready,
        "daily_validation_deferred": True,
        "blocking_reasons": [
            reason
            for reason, condition in (
                ("insufficient_period_samples", usable_period < 4),
                ("insufficient_daily_samples", usable_daily < 4),
                ("insufficient_natal_sanity_samples", usable_natal < 3),
            )
            if condition
        ],
        "period_only_blocking_reasons": [
            reason
            for reason, condition in (
                ("insufficient_period_samples", usable_period < 4),
                ("insufficient_natal_sanity_samples", usable_natal < 3),
            )
            if condition
        ],
    }


def build_validation_payload(*, fixture_ids: Sequence[str] | None = None) -> dict[str, Any]:
    fixtures = _load_fixture_index()
    selected_fixture_ids = {str(item).strip() for item in (fixture_ids or []) if str(item).strip()}
    period_daily_cases = [
        _safe_generate_period_daily_case(case, fixtures[case.fixture_id])
        for case in PERIOD_DAILY_CASES
        if case.fixture_id in fixtures and (not selected_fixture_ids or case.fixture_id in selected_fixture_ids)
    ]
    natal_cases = [
        _build_natal_sanity_payload(fixture_id, fixtures[fixture_id])
        for fixture_id in NATAL_SANITY_CASES
        if fixture_id in fixtures and (not selected_fixture_ids or fixture_id in selected_fixture_ids)
    ]
    for case in period_daily_cases:
        _evaluate_surface_case(case, surface="period", variants_key="period_variants")
        _evaluate_surface_case(case, surface="daily", variants_key="daily_variants")
    _apply_cross_chart_duplication(period_daily_cases, surface="period", variants_key="period_variants")
    _apply_cross_chart_duplication(period_daily_cases, surface="daily", variants_key="daily_variants")
    readiness = _pack_readiness(period_daily_cases, natal_cases)
    return {
        "generated_by": "backend/scripts/generate_validation_samples.py",
        "variant_contracts": {
            "period": {
                "A": "legacy_period_output",
                "B": "canonical_period_spine_plus_voice_policy",
                "C": "canonical_period_plus_manifestation_context",
            },
            "daily": {
                "A": "legacy_daily_output",
                "B": "today_story_candidate_plus_current_daily_synthesis",
                "C": "mock_today_delta_signal_plus_scene_aware_daily",
            },
            "natal": {"mode": "sanity_review_only"},
        },
        "blind_protocol": {
            "mapping_visibility": "reviewers_must_not_see_semantic_A_B_C_mapping",
            "answer_key_location": "docs/voice/sample_validation_samples.json",
            "randomization": "deterministic_per_chart_seed",
        },
        "minimum_requirements": {
            "minimum_reviewers": 5,
            "minimum_usable_period_charts": 4,
            "minimum_usable_daily_charts": 4,
            "minimum_usable_natal_sanity_charts": 3,
        },
        "decision_thresholds": {
            "period_win_primary": "B_or_C_seen_score >= A_seen_score + 0.7 and B_or_C_generic_score < A_generic_score",
            "period_win_secondary": "B_or_C_best_overall_share >= 0.60",
            "daily_failure_signal": "If Daily B/C does not beat A, mark as evidence for PR-5 Daily Today-ness Signal",
        },
        "numeric_rating_fields": list(NUMERIC_RATING_FIELDS),
        "choice_fields": list(CHOICE_FIELDS),
        "pack_readiness": readiness,
        "period_daily_cases": period_daily_cases,
        "natal_sanity_cases": natal_cases,
        "decision_criteria": DECISION_CRITERIA,
        "validation_questions": list(PERIOD_QUESTIONS),
    }


def _render_questions(items: Sequence[str]) -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(items, start=1))


def _variant_body(variant: Mapping[str, Any], *, include_guidance: bool) -> str:
    headline = str(variant.get("display_headline") or variant.get("headline") or "").strip()
    body = str(variant.get("display_body") or variant.get("body") or "").strip()
    guidance = str(variant.get("display_guidance") or variant.get("guidance") or "").strip()
    parts: list[str] = []
    if headline:
        parts.append(f"**Başlık:** {headline}")
    if body:
        parts.append(body)
    if include_guidance and guidance:
        parts.append(f"**Guidance:** {guidance}")
    return "\n\n".join(parts) if parts else "_No content generated._"


def _detect_display_polish_flags(*, headline: str, body: str) -> list[str]:
    flags: list[str] = []
    combined = _join_paragraphs(headline, body)
    if len(REPEATED_OPENING_START_PATTERN.findall(body)) > 1:
        flags.append("repeated_opening")
    if any(pattern.search(combined) for pattern in SYSTEM_SCAFFOLD_PATTERNS):
        flags.append("system_scaffold_phrase")
    if THRESHOLD_WORD_PATTERN.search(combined):
        flags.append("threshold_word_leak")
    if any(pattern.search(combined) for pattern in TURKISH_CHARACTER_PATTERNS):
        flags.append("turkish_character_issue")
    if len(ISOLATED_NAKED_FRAME_PATTERN.findall(body)) >= 2:
        flags.append("isolated_naked_frame")
    return sorted(set(flags))


def _normalize_turkish_display(text: str) -> str:
    out = str(text or "")
    for source, target in TURKISH_DISPLAY_REPLACEMENTS.items():
        out = out.replace(source, target)
    return out


def _soften_system_scaffolds(text: str) -> str:
    out = str(text or "")

    def _soften_source_phrase(match: re.Match[str]) -> str:
        phrase = str(match.group(1) or "").strip()
        phrase = re.sub(r"\bhattını$", "hattı", phrase, flags=re.IGNORECASE)
        phrase = re.sub(r"\bçizgisini$", "çizgisi", phrase, flags=re.IGNORECASE)
        return f"{phrase.capitalize()} bu dönemde özellikle belirginleşiyor."

    out = re.sub(
        r"Bu dönem doğum haritandaki ([^.]+?) özellikle çalıştırıyor\.",
        _soften_source_phrase,
        out,
        flags=re.IGNORECASE,
    )
    out = re.sub(
        r"Bu dönem hayatının bir alanı daha görünür hale geliyor ve senden daha bilinçli seçimler istiyor\.",
        "Hayatının bir alanı daha görünür hale geliyor; senden daha bilinçli seçimler istiyor.",
        out,
        flags=re.IGNORECASE,
    )
    out = re.sub(
        r"Bu dönem görünürlük kazanan eşik tam bu hatta toplanıyor\.",
        "Görünürlük kazanan çizgi bu kez tam bu hatta toplanıyor.",
        out,
        flags=re.IGNORECASE,
    )
    return out


def _reduce_repeated_openings(text: str) -> str:
    count = 0

    def _replace(match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        if count == 1:
            return match.group(0)
        replacements = ["Şu sıralar ", "Burada ", "Bu kez "]
        prefix = " " if match.start() > 0 else ""
        return prefix + replacements[min(count - 2, len(replacements) - 1)]

    return REPEATED_OPENING_START_PATTERN.sub(_replace, text)


def _soften_threshold_words(text: str) -> str:
    out = str(text or "")
    out = re.sub(r"\bgörünürlük kazanan eşik\b", "görünürlük kazanan çizgi", out, flags=re.IGNORECASE)
    return out


def _finalize_display_spacing(text: str) -> str:
    return re.sub(r"([.!?])([A-ZÇĞİÖŞÜ])", r"\1 \2", str(text or ""))


def _apply_display_polish_to_variant(variant: dict[str, Any]) -> dict[str, Any]:
    headline = str(variant.get("headline") or "").strip()
    body = str(variant.get("body") or "").strip()
    guidance = str(variant.get("guidance") or "").strip()
    display_headline = _normalize_turkish_display(headline)
    display_body = _normalize_turkish_display(body)
    display_body = _soften_system_scaffolds(display_body)
    display_body = _reduce_repeated_openings(display_body)
    display_body = _soften_threshold_words(display_body)
    display_body = _finalize_display_spacing(display_body)
    display_guidance = _normalize_turkish_display(guidance)
    flags = _detect_display_polish_flags(headline=headline, body=body)
    existing_flags = [str(flag) for flag in (variant.get("quality_flags") or []) if str(flag).strip()]
    variant["display_headline"] = display_headline
    variant["display_body"] = display_body
    variant["display_guidance"] = display_guidance
    variant["quality_flags"] = sorted(set(existing_flags + flags))
    return variant


def enrich_validation_payload_for_reviewer_pack(payload: Mapping[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(dict(payload))
    out["post_processed_for_display"] = True
    out["post_process_rules"] = list(REVIEWER_POST_PROCESS_RULES)
    for case in out.get("period_daily_cases") or []:
        if not isinstance(case, dict):
            continue
        for variant in case.get("period_variants") or []:
            if isinstance(variant, dict):
                _apply_display_polish_to_variant(variant)
    return out


def render_markdown_pack(payload: Mapping[str, Any]) -> str:
    readiness = payload.get("pack_readiness") if isinstance(payload.get("pack_readiness"), Mapping) else {}
    lines: list[str] = []
    lines.append("# SHOU Voice vNext — Sample Validation Pack")
    lines.append("")
    lines.append("Bu dosya `backend/scripts/generate_validation_samples.py` tarafından doldurulur.")
    lines.append("Blind test insan moderasyonuyla yürür; event card bu pack'in dışında tutulur.")
    lines.append("")
    lines.append("## Validation Readiness")
    lines.append("")
    lines.append(f"- `validation_ready`: `{bool(readiness.get('validation_ready'))}`")
    lines.append(f"- `period_only_validation_ready`: `{bool(readiness.get('period_only_validation_ready'))}`")
    lines.append(f"- `usable_period_charts`: `{readiness.get('usable_period_charts', 0)}`")
    lines.append(f"- `usable_daily_charts`: `{readiness.get('usable_daily_charts', 0)}`")
    lines.append(f"- `usable_natal_sanity_charts`: `{readiness.get('usable_natal_sanity_charts', 0)}`")
    if readiness.get("blocking_reasons"):
        lines.append(f"- `blocking_reasons`: `{', '.join(readiness.get('blocking_reasons') or [])}`")
    if readiness.get("period_only_blocking_reasons"):
        lines.append(f"- `period_only_blocking_reasons`: `{', '.join(readiness.get('period_only_blocking_reasons') or [])}`")
    lines.append(f"- `daily_validation_deferred`: `{bool(readiness.get('daily_validation_deferred'))}`")
    lines.append("")
    lines.append("Daily blind test bu turda reviewer pack'e dahil değildir; daily renderer guardrail injection ayrı cycle'da kapanacaktır.")
    lines.append("")
    if readiness.get("period_only_validation_ready"):
        lines.append("Bu pack reviewer'a period-only validation için gönderilebilir. Daily diagnosis JSON artefaktında tutulur.")
    elif readiness.get("blocking_reasons"):
        lines.append("Bu durumda pack reviewer'a gönderilmez. Aşağıdaki içerik facilitator diagnosis içindir.")
    lines.append("")
    lines.append("## Runbook")
    lines.append("")
    lines.append("```bash")
    lines.append("PYTHONPATH=backend backend/venv/bin/python backend/scripts/generate_validation_samples.py")
    lines.append("```")
    lines.append("")
    lines.append("Not: Script canlı transit generation yapabiliyorsa pack'i doldurur. Swiss ephemeris veya runtime bağımlılıkları yoksa ilgili chart satırı `unavailable` olarak işaretlenir.")
    lines.append("")
    lines.append("Validation sonuçlarını tamamlandıktan sonra `docs/voice/validation_results_2026_05_xx.md` dosyasına kaydedin.")
    lines.append("")
    lines.append("## Variant Contract")
    lines.append("")
    lines.append("Bu mapping facilitator içindir; reviewer'a gösterilmez.")
    lines.append("")
    lines.append("- Period: `A legacy`, `B canonical spine + voice policy`, `C canonical + manifestation context`")
    lines.append("- Daily: `A legacy`, `B TodayStoryCandidate + current daily_synthesis`, `C mock today_delta_signal + scene-aware daily`")
    lines.append("- Natal: `sanity review only`")
    lines.append("- Natal sanity surface `legacy_compat` olarak değerlendirilir; vNext lint gate'inden muaf, ama quality flag taşır.")
    lines.append("")
    lines.append("## Blind Protocol")
    lines.append("")
    lines.append("- Reviewer A/B/C semantic mapping'i görmez.")
    lines.append("- Chart başına A/B/C sırası deterministic seed ile karıştırılır.")
    lines.append("- Answer key yalnız `docs/voice/sample_validation_samples.json` içinde tutulur.")
    lines.append("")
    lines.append("## Rating Scale")
    lines.append("")
    lines.append("Per-variant `1–5` numeric rating fields:")
    lines.append("")
    for field in NUMERIC_RATING_FIELDS:
        lines.append(f"- `{field}`")
    lines.append("")
    lines.append("Chart-level choice fields:")
    lines.append("")
    lines.append("- `best_overall`: `A | B | C`")
    lines.append("- `worst_overall`: `A | B | C`")
    lines.append("")
    lines.append("Skor yönü:")
    lines.append("")
    lines.append("- `seen_score`, `reread_score`: yüksek daha iyi")
    lines.append("- `generic_score`, `too_technical_score`, `coaching_motivation_score`, `repetition_score`: düşük daha iyi")
    lines.append("")
    lines.append("Not: `best_overall` ve `worst_overall` numeric skor değil; chart-level seçim alanıdır.")
    lines.append("")
    lines.append("## Minimum Sample / Reviewer Count")
    lines.append("")
    lines.append("- Minimum reviewer: `5`")
    lines.append("- Minimum usable period charts: `4`")
    lines.append("- Minimum usable daily charts: `4` (`full validation` için; bu tur reviewer pack'ine dahil değil)")
    lines.append("- Minimum usable natal sanity charts: `3`")
    lines.append("")
    lines.append("## Decision Thresholds")
    lines.append("")
    lines.append("- Period `B/C wins` if average `seen_score` beats `A` by at least `0.7` and `generic_score` is lower.")
    lines.append("- Secondary win rule: `B/C` wins `best_overall` in at least `60%` of reviews.")
    lines.append("- If Daily `B/C` does not beat `A`, mark this as evidence for `PR-5 Daily Today-ness Signal`.")
    lines.append("- Bu reviewer pack şu an yalnız period + natal sanity için kullanılacaktır.")
    lines.append("")
    lines.append("Reviewer-facing `A/B/C` label chart başına randomize edilebilir. Source variant çözümü için `docs/voice/sample_validation_samples.json` kullanılır.")
    lines.append("")
    lines.append("## PR-2v.1 Period Blind Test")
    lines.append("")

    for case in payload.get("period_daily_cases") or []:
        if not isinstance(case, Mapping):
            continue
        availability = case.get("surface_availability") if isinstance(case.get("surface_availability"), Mapping) else {}
        period_state = (availability.get("period") or {}) if isinstance(availability.get("period"), Mapping) else {}
        if not bool(period_state.get("available")):
            continue
        lines.append(f"### {case.get('fixture_label')}")
        lines.append("")
        lines.append(f"- `fixture_id`: `{case.get('fixture_id')}`")
        lines.append(f"- `window`: `{case.get('window_start')} -> {case.get('window_end')}`")
        lines.append(f"- `selected_date`: `{case.get('selected_date')}`")
        status = str(case.get("status") or "").strip()
        if status != "ok":
            lines.append(f"- `status`: `{status or 'unavailable'}`")
            lines.append(f"- `error`: `{case.get('error') or 'unknown'}`")
            lines.append("")
            continue
        runtime_quality = case.get("runtime_quality") if isinstance(case.get("runtime_quality"), Mapping) else {}
        if bool(runtime_quality.get("degraded_path")):
            lines.append(f"- `runtime_warning`: `degraded_path`")
            if str(runtime_quality.get("degraded_path_reason") or "").strip():
                lines.append(f"- `runtime_warning_reason`: `{runtime_quality.get('degraded_path_reason')}`")
            lines.append("")
        for variant in case.get("period_variants") or []:
            if not isinstance(variant, Mapping):
                continue
            lines.append(f"#### Variant {variant.get('blind_label')}")
            lines.append("")
            lines.append(_variant_body(variant, include_guidance=False))
            lines.append("")
            lines.append("Score sheet:")
            lines.append("")
            lines.append("| seen_score | generic_score | too_technical_score | coaching_motivation_score | reread_score | repetition_score |")
            lines.append("|---|---|---|---|---|---|")
            lines.append("|   |   |   |   |   |   |")
            lines.append("")
        lines.append("**Sorular**")
        lines.append("")
        lines.append(_render_questions(PERIOD_QUESTIONS))
        lines.append("")
        lines.append("- `best_overall`: ")
        lines.append("- `worst_overall`: ")
        lines.append("")

    lines.append("## PR-2v.3 Natal Sanity Check")
    lines.append("")
    lines.append("Bu bölüm blind ranking değil; 3 chart üzerinde beklenmedik ton/akış bozulması var mı diye manuel sanity pass.")
    lines.append("Buradaki surface `legacy_compat`; soru seti astro-terim var/yok yerine beklenmedik regressions ve tone mismatch üstüne kurulu.")
    lines.append("")

    for case in payload.get("natal_sanity_cases") or []:
        if not isinstance(case, Mapping):
            continue
        lines.append(f"### {case.get('fixture_label')}")
        lines.append("")
        lines.append(f"- `fixture_id`: `{case.get('fixture_id')}`")
        lines.append(f"- `source`: `{case.get('excerpt_source')}`")
        if case.get("quality_flags"):
            lines.append(f"- `quality_flags`: `{', '.join(case.get('quality_flags') or [])}`")
        lines.append("")
        for section in case.get("sections") or []:
            if not isinstance(section, Mapping):
                continue
            lines.append(f"#### {section.get('headline') or section.get('slot')}")
            lines.append("")
            lines.append(str(section.get("body") or "").strip() or "_No excerpt._")
            lines.append("")
        lines.append("**Sanity soruları**")
        lines.append("")
        lines.append(
            _render_questions(
                (
                    "Akışta beklenmedik kırılma veya dağınıklık var mı?",
                    "Yeni vNext renderer'a geçmesi gerekirken hâlâ legacy şablonda duran bir cümle var mı?",
                    "SHOU vNext tonu ile açık çelişen bir bölüm var mı?",
                    "Bu chart için bariz bir içerik regresyonu hissediliyor mu?",
                )
            )
        )
        lines.append("")

    lines.append("## Decision Criteria")
    lines.append("")
    for key, value in DECISION_CRITERIA.items():
        lines.append(f"- `{key}`: {value}")
    lines.append("")
    lines.append("Decision authority: **Sahra**")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate PR-2v sample validation pack.")
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument(
        "--fixture-id",
        action="append",
        dest="fixture_ids",
        help="Limit generation to one or more fixture ids for smoke testing.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = build_validation_payload(fixture_ids=args.fixture_ids)
    payload = enrich_validation_payload_for_reviewer_pack(payload)
    args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    args.output_md.write_text(render_markdown_pack(payload))
    print(f"Wrote {args.output_json}")
    print(f"Wrote {args.output_md}")


if __name__ == "__main__":
    main()
