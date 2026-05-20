from __future__ import annotations

import os
import re
from typing import Any, Iterable, Mapping, Sequence

_ENABLED_VALUES = {"1", "true", "yes", "on"}
_BANNED_PUBLIC_TOKENS = (
    "mc, yöneticisi",
    "mc route",
    "10h",
    "source_type",
    "debug",
    "candidate",
    "fallback",
    "public job",
)

# Narrow composed-detail Turkish normalization guard.
# Lists ASCII variants of Turkish words that must not appear in user-facing
# public fields (headline/teaser/body/chips). Used to defend against regressions
# where copy is authored without proper Turkish diacritics. Technical trace
# fields (anchors, ids, source_type, etc.) are intentionally excluded.
#
# Matched case-sensitively against original text. This is deliberate:
# - re.IGNORECASE under Python's simple case folding equates "i"/"I"/"ı"/"İ",
#   so an IGNORECASE pattern for "insanlar" would incorrectly hit the
#   diacritic-correct "İnsanlar" and a pattern for "yalniz" would hit "yalnız".
# - For words like "insanlar"/"ifade" whose lowercase form is identical in
#   ASCII and proper Turkish (no internal diacritic), we only ban the
#   capitalized ASCII form ("Insanlar", "Ifade") — that is the only form
#   that is unambiguously wrong (the proper capital is "İ", with dot).
# - For all other words (whose lowercase Turkish form contains a diacritic
#   like ı/ş/ğ/ç/ö/ü), the lowercase ASCII variant is unambiguously wrong
#   and can be matched directly.
_TURKISH_ASCII_RESIDUE_WORDS = (
    # Capitalized ASCII forms that should be Turkish "İ..." at sentence start
    # or as chip labels. Lowercase forms of these are intentionally excluded
    # because they are indistinguishable from correct Turkish.
    "Insanlar",
    "Ifade",
    # Lowercase ASCII forms whose correct Turkish lowercase contains a
    # diacritic (so the bare ASCII form is unambiguously wrong).
    "disaridaki",
    "Disaridaki",
    "nasil",
    "soyledigini",
    "soyledigin",
    "soz",
    "Soz",
    "sozun",
    "sozunun",
    "sozunu",
    "Sozunun",
    "gorunur",
    "Gorunur",
    "gorunurluk",
    "gorunurlukle",
    "guc",
    "Guc",
    "gucu",
    "gucleniyor",
    "guclendirebilir",
    "guclendiriyor",
    "dogru",
    "Dogru",
    "cumle",
    "Cumle",
    "cumleyi",
    "cumleyle",
    "cercevelediginde",
    "agirligin",
    "yaptigini",
    "degil",
    "cogu",
    "Cogu",
    "kurdugun",
    "Kurdugun",
    "kurdugunda",
    "isi",
    "isin",
    "isini",
    "yalniz",
    "yalnizca",
    "anlattigin",
    "anlatim",
    "Anlatim",
    "rolun",
    "rolunu",
    "parcasi",
    "once",
    "yarattigi",
    "yuksek",
    "yuzden",
    "netlestiginde",
    "netlesiyor",
    "belirginlesmesinde",
    "belirginlestirebiliyor",
    "yatiyor",
    "yon",
    "calismani",
    "calismayi",
    "calisan",
    "calisiyor",
    "tasidigini",
    "tasiyor",
    "hizli",
    "hizlica",
    "asil",
    "icin",
    "geldiginde",
    "oldugunda",
    "cok",
    "dunyadaki",
    "biciminle",
    "bicimi",
    "biraktigin",
    "buyuyebilir",
    "buyutuyor",
    "bazi",
    "Bazi",
    "konusuldugu",
    "onemli",
    "seyi",
    "hattin",
    "hatti",
    "bulusuyor",
    "Dis",
)

_TURKISH_ASCII_RESIDUE_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(word) for word in _TURKISH_ASCII_RESIDUE_WORDS) + r")\b",
)


def _env_enabled(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in _ENABLED_VALUES


def render_composed_detail_card_v0_9a_2(candidate: Mapping[str, Any]) -> dict[str, Any] | None:
    if not _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL"):
        return None
    if not isinstance(candidate, Mapping):
        return None
    if str(candidate.get("source_type") or "").strip() != "composed_semantic":
        return None
    if str(candidate.get("family") or "").strip() != "career_route":
        return None
    if str(candidate.get("subtype") or "").strip() != "public_voice":
        return None
    if candidate.get("chart_facts_match") is not True:
        return None

    eligibility = candidate.get("public_eligibility") if isinstance(candidate.get("public_eligibility"), Mapping) else {}
    if not bool(eligibility.get("detail_eligible")):
        return None
    if bool(eligibility.get("public_support_eligible")) or bool(eligibility.get("public_main_eligible")):
        return None

    variant = _match_supported_public_voice_variant(candidate)
    if variant is None:
        return None

    card = _render_variant_card(variant=variant, candidate=candidate)
    if card is None:
        return None
    if not _meets_public_quality(card):
        return None
    return card


def _render_variant_card(*, variant: str, candidate: Mapping[str, Any]) -> dict[str, Any] | None:
    candidate_id = str(candidate.get("id") or "").strip()
    source_trace = {
        "family": str(candidate.get("family") or "").strip(),
        "subtype": str(candidate.get("subtype") or "").strip(),
        "domain_reason": list(candidate.get("domain_reason") or []),
        "technical_anchors": list(candidate.get("technical_anchors") or []),
    }

    if variant == "fix04_h10_career_stellium":
        return {
            "id": f"composed_detail::{candidate_id}::{variant}",
            "node_id": f"promise::{candidate_id}",
            "headline": "İnsanlar sende sadece ne yaptığını değil, nasıl söylediğini de fark ediyor.",
            "teaser": "Dışarıdaki etkin çoğu zaman sözünün tonu ve kurduğun pozisyonla güçleniyor.",
            "body": (
                "Bir işi yalnız tamamlaman değil, onu nasıl anlattığın da sende görünür rolün parçası oluyor. "
                "İnsanlar çoğu zaman önce fikrinin tonunu, sonra o tonun yarattığı etkiyi fark edebilir. "
                "Buradaki güç, sesini daha yüksek kullanmakta değil; doğru yerde netleştiğinde dışarıdaki rolün zaten belirginleşmesinde yatıyor."
            ),
            "chips": ["Kariyer", "Söz", "Görünür rol"],
            "detail_items": [],
            "family": "career_public_voice",
            "emphasis": "detail",
            "origin": "composed_detail_renderer_v0_9a_2",
            "evidence_summary": [
                "Sözünün tonu dışarıdaki rolünü güçlendiriyor.",
                "Anlatım biçimi görünür etkiyle birlikte çalışıyor.",
            ],
            "source_type": "composed_semantic",
            "source_candidate_id": candidate_id,
            "public_job": "detail_only",
            "source_anchor_trace": source_trace,
        }

    if variant == "tokyo_1998_06_21":
        return {
            "id": f"composed_detail::{candidate_id}::{variant}",
            "node_id": f"promise::{candidate_id}",
            "headline": "Dışarıdaki yerin çoğu zaman kurduğun cümleyle netleşiyor.",
            "teaser": "Ne söylediğin kadar, onu hangi sakinlik ve yön duygusuyla söylediğin de fark yaratıyor.",
            "body": (
                "İnsanlar sende yalnızca çalışmanı değil, o çalışmayı nasıl taşıdığını da duyabilir. "
                "Bir konuda netleştiğinde sözün dışarıdaki rolünü hızlıca güçlendirebilir. "
                "Burada asıl fark, görünür olmak için zorlaman değil; doğru cümle geldiğinde yerinin zaten daha belirgin hale gelmesi."
            ),
            "chips": ["Kariyer", "İfade", "Konum"],
            "detail_items": [],
            "family": "career_public_voice",
            "emphasis": "detail",
            "origin": "composed_detail_renderer_v0_9a_2",
            "evidence_summary": [
                "Kurduğun cümle dışarıdaki yerini belirginleştirebiliyor.",
                "Söz ve yön duygusu aynı kariyer hattında buluşuyor.",
            ],
            "source_type": "composed_semantic",
            "source_candidate_id": candidate_id,
            "public_job": "detail_only",
            "source_anchor_trace": source_trace,
        }

    if variant == "toronto_1976_06_26":
        return {
            "id": f"composed_detail::{candidate_id}::{variant}",
            "node_id": f"promise::{candidate_id}",
            "headline": "Görünür olduğunda bunu en çok sözün taşıyor.",
            "teaser": "Dış dünyadaki etkin, anlatım biçiminle ve insanlarda bıraktığın zihinsel iz ile büyüyebilir.",
            "body": (
                "Bazı insanlar işini yapar; sende ise işin nasıl konuşulduğu da rolün önemli bir parçası olabilir. "
                "Bir cümleyi doğru kurduğunda ya da bir şeyi doğru çerçevelediğinde dışarıdaki ağırlığın daha hızlı hissedilebilir. "
                "Bu yüzden kariyer hattın yalnız görünürlük değil, görünürlükle birlikte çalışan bir ifade gücü de taşıyor."
            ),
            "chips": ["Kariyer", "Söz", "Etki"],
            "detail_items": [],
            "family": "career_public_voice",
            "emphasis": "detail",
            "origin": "composed_detail_renderer_v0_9a_2",
            "evidence_summary": [
                "Anlatım biçimi görünür etkiyi büyütüyor.",
                "İfade gücü ve kariyer hattı birlikte çalışıyor.",
            ],
            "source_type": "composed_semantic",
            "source_candidate_id": candidate_id,
            "public_job": "detail_only",
            "source_anchor_trace": source_trace,
        }
    return None


def _match_supported_public_voice_variant(candidate: Mapping[str, Any]) -> str | None:
    trace = candidate.get("evidence_trace") if isinstance(candidate.get("evidence_trace"), Mapping) else {}
    primitive = trace.get("primitive_facts") if isinstance(trace.get("primitive_facts"), Mapping) else {}
    placements = primitive.get("placements") if isinstance(primitive.get("placements"), Sequence) else []
    angles = primitive.get("angles") if isinstance(primitive.get("angles"), Sequence) else []

    normalized_placements = {
        (
            str(item.get("planet") or "").strip(),
            str(item.get("sign") or "").strip(),
            int(item.get("house") or 0),
        )
        for item in placements
        if isinstance(item, Mapping) and str(item.get("planet") or "").strip()
    }
    normalized_angles = {
        (
            str(item.get("angle") or "").strip(),
            str(item.get("sign") or "").strip(),
        )
        for item in angles
        if isinstance(item, Mapping) and str(item.get("angle") or "").strip()
    }

    if ("MC", "Gemini") not in normalized_angles:
        return None

    if {
        ("Mercury", "Gemini", 10),
        ("Sun", "Cancer", 10),
        ("Moon", "Gemini", 10),
        ("Venus", "Cancer", 10),
    } <= normalized_placements:
        return "toronto_1976_06_26"

    if {
        ("Mercury", "Cancer", 10),
        ("Sun", "Gemini", 10),
    } <= normalized_placements:
        return "tokyo_1998_06_21"

    if {
        ("Mercury", "Cancer", 10),
        ("Mars", "Cancer", 10),
    } <= normalized_placements:
        return "fix04_h10_career_stellium"

    return None


def _has_turkish_ascii_residue(text: str) -> bool:
    if not text:
        return False
    return bool(_TURKISH_ASCII_RESIDUE_PATTERN.search(text))


def _iter_chip_strings(chips: Any) -> Iterable[str]:
    if not isinstance(chips, Sequence) or isinstance(chips, (str, bytes)):
        return ()
    return (str(chip) for chip in chips if isinstance(chip, str))


def _meets_public_quality(card: Mapping[str, Any]) -> bool:
    for field in ("headline", "teaser", "body"):
        text = str(card.get(field) or "").strip()
        if not text:
            return False
        lowered = text.lower()
        if any(token in lowered for token in _BANNED_PUBLIC_TOKENS):
            return False
        if _has_turkish_ascii_residue(text):
            return False
    for chip in _iter_chip_strings(card.get("chips")):
        if _has_turkish_ascii_residue(chip):
            return False
    body = str(card.get("body") or "").strip()
    if not body or len(body.split()) < 18:
        return False
    return True


# v0.9a.3 Phase B — dedicated public detail lane.
#
# Promotes already-rendered composed_detail_cards_v0_9a_2 trace entries into
# a separate, user-facing public payload field
# (`profile_public.composed_detail_cards`). Promotion is gated by:
#   1) ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL must be true
#      (so a trace card actually exists upstream),
#   2) ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE must be true,
#   3) the card's variant must be in the Phase B allowlist,
#   4) the card must still pass public quality (Turkish diacritics,
#      no debug/banned tokens).
#
# The lane is a strict subset projection — technical/trace fields
# (source_type, source_candidate_id, public_job, source_anchor_trace,
# detail_items, evidence_summary) are stripped so they never reach the
# visible payload.

_PUBLIC_DETAIL_LANE_VARIANT_ALLOWLIST: tuple[str, ...] = (
    "fix04_h10_career_stellium",
    "tokyo_1998_06_21",
    "toronto_1976_06_26",
)

_PUBLIC_DETAIL_LANE_VISIBLE_FIELDS: tuple[str, ...] = (
    "id",
    "node_id",
    "headline",
    "teaser",
    "body",
    "chips",
    "family",
    "emphasis",
    "origin",
    "slides",
    "why_this_exists",
)


def public_detail_lane_enabled() -> bool:
    return _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE")


def _variant_from_card_id(card_id: str) -> str:
    # id form: composed_detail::<candidate_id>::<variant>
    parts = card_id.split("::")
    if len(parts) != 3:
        return ""
    return parts[-1].strip()


def _strip_to_public_visible(card: Mapping[str, Any]) -> dict[str, Any]:
    visible: dict[str, Any] = {}
    for key in _PUBLIC_DETAIL_LANE_VISIBLE_FIELDS:
        if key not in card:
            continue
        value = card[key]
        if key == "slides" and isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            slides: list[dict[str, Any]] = []
            for item in value:
                if not isinstance(item, Mapping):
                    continue
                slide = {
                    "id": str(item.get("id") or "").strip(),
                    "title": str(item.get("title") or "").strip(),
                    "body": str(item.get("body") or "").strip(),
                }
                slides.append(slide)
            visible[key] = slides
        elif key == "why_this_exists" and isinstance(value, Mapping):
            visible[key] = {
                "title": str(value.get("title") or "").strip(),
                "body": str(value.get("body") or "").strip(),
            }
        elif isinstance(value, list):
            visible[key] = list(value)
        else:
            visible[key] = value
    return visible


def project_composed_detail_cards_to_public_lane(
    rendered_cards: Sequence[Mapping[str, Any]] | None,
) -> list[dict[str, Any]]:
    """Promote rendered trace cards into the public detail lane.

    Returns an empty list when any gate is unmet. Callers decide whether
    to omit the public field entirely based on emptiness; this function
    never emits the field itself.
    """
    if not public_detail_lane_enabled():
        return []
    if not _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL"):
        return []
    if not rendered_cards:
        return []
    promoted: list[dict[str, Any]] = []
    for card in rendered_cards:
        if not isinstance(card, Mapping):
            continue
        variant = _variant_from_card_id(str(card.get("id") or ""))
        if variant not in _PUBLIC_DETAIL_LANE_VARIANT_ALLOWLIST:
            continue
        if not _meets_public_quality(card):
            continue
        promoted.append(_strip_to_public_visible(card))
    return promoted


# ---------------------------------------------------------------------------
# v0.10 Phase 2 — Istanbul 1996 Venus 12H hidden/private love slide card.
# ---------------------------------------------------------------------------

_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_VARIANT_ALLOWLIST: tuple[str, ...] = (
    "istanbul_1996_12_28_hidden_private_love",
)

_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_ALLOWED_PACKET_IDS: tuple[str, ...] = (
    "venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact",
)

_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_ALLOWED_CLUSTER_IDS: tuple[str, ...] = (
    "relationship_hidden_private_love_pattern",
)


def relationship_hidden_private_love_public_detail_lane_enabled() -> bool:
    return _env_enabled(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_PUBLIC_DETAIL_LANE"
    )


_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_PHASE3_ORIGIN_HINT_DENYLIST: tuple[str, ...] = (
    "neutral_or_gift_only_signature",
    "generic_fallback_packet",
    "debug_only_family",
    "exactness_only_without_owner_route",
    "non_owner_broad_category_summary",
    "generic_relationship_friction_without_trust_owner",
    "weak_global_or_generational_only_anchor",
)


def relationship_hidden_private_love_phase3_internal_metadata_enabled() -> bool:
    return _env_enabled(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_PHASE3_INTERNAL_METADATA"
    )


def relationship_hidden_private_love_deep_read_renderer_enabled() -> bool:
    """Phase-4 hidden/private pilot deep_read renderer flag (default off).

    Scaffolding only at this point. The flag is intentionally not wired
    to any rendering behavior yet — it is introduced first so the
    "flag-off no-op" invariant (Phase-4 implementation request §4.1)
    can be locked by test before any renderer branch is added.

    Per request §3 / §4: independent from the Phase-3
    INTERNAL_METADATA flag; Phase-4 user-visible behavior must never
    activate through the Phase-3 flag alone.
    """
    return _env_enabled(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_DEEP_READ_RENDERER"
    )


def _relationship_hidden_private_love_origin_hint_assessment(
    source: Mapping[str, Any],
) -> dict[str, Any]:
    domain_reason = (
        source.get("domain_reason")
        if isinstance(source.get("domain_reason"), Sequence) and not isinstance(source.get("domain_reason"), (str, bytes))
        else []
    )
    technical_anchors = (
        source.get("technical_anchors")
        if isinstance(source.get("technical_anchors"), Sequence) and not isinstance(source.get("technical_anchors"), (str, bytes))
        else []
    )
    meta = source.get("meta") if isinstance(source.get("meta"), Mapping) else {}
    reasons_lower = {str(item or "").strip().lower() for item in domain_reason if str(item or "").strip()}
    anchors_lower = [str(item or "").strip().lower() for item in technical_anchors if str(item or "").strip()]
    has_personal_or_angle_anchor = any(
        marker in anchor
        for anchor in anchors_lower
        for marker in ("venüs", "venus", "moon", "sun", "asc", "dsc", "yükselen")
    )
    has_owner_route = "12h hidden-love signature" in reasons_lower and has_personal_or_angle_anchor

    deny_reasons: list[str] = []
    if str(source.get("subtype") or "").strip() not in {"", "hidden_private_love"}:
        deny_reasons.append("non_owner_broad_category_summary")
    if str(source.get("source_type") or "").strip() == "generic_fallback" or bool(meta.get("subtype_default_fallback")):
        deny_reasons.append("generic_fallback_packet")
    if str(source.get("source_type") or "").strip() == "discovery_scaffold":
        deny_reasons.append("debug_only_family")
    if not has_owner_route:
        deny_reasons.append("exactness_only_without_owner_route")
    if not has_personal_or_angle_anchor:
        deny_reasons.append("weak_global_or_generational_only_anchor")

    allow_reasons: list[str] = []
    if str(source.get("subtype") or "").strip() in {"", "hidden_private_love"}:
        allow_reasons.append("hidden_private_signature")
    if has_owner_route:
        allow_reasons.append("owner_hidden_private_route")
    if has_personal_or_angle_anchor:
        allow_reasons.append("personalized_anchor_present")
    return {
        "eligible": bool(allow_reasons) and not deny_reasons,
        "allow_reasons": allow_reasons,
        "deny_reasons": deny_reasons,
        "deny_catalog": list(_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_PHASE3_ORIGIN_HINT_DENYLIST),
    }


def _build_relationship_hidden_private_love_phase3_internal_metadata(
    source: Mapping[str, Any],
    *,
    source_kind: str,
) -> dict[str, Any]:
    source_meta = source.get("meta") if isinstance(source.get("meta"), Mapping) else {}
    inherited = (
        dict(source_meta.get("deep_read_phase3") or {})
        if isinstance(source_meta.get("deep_read_phase3"), Mapping)
        else {}
    )
    origin_hint = _relationship_hidden_private_love_origin_hint_assessment(source)
    payload = {
        "pilot_family": "hidden_private_deep_read",
        "slide_profile": "pattern_to_gift",
        "status": "pilot_scoped_approval_pending_section_13_2",
        "phase_boundary": "internal_metadata_only",
        "source_kind": source_kind,
        "source_candidate_id": str(source.get("id") or "").strip(),
        "role_bindings": {
            "origin_hint": {
                "surface_role": "hidden_mechanism",
                "eligible": origin_hint["eligible"],
                "allow_reasons": list(origin_hint["allow_reasons"]),
                "deny_reasons": list(origin_hint["deny_reasons"]),
            },
            "gift": {"surface_role": "gift_in_silence", "source_field": "gift"},
            "shadow": {"surface_role": "protective_pattern", "source_field": "shadow_or_friction"},
            "integration": {"surface_role": "safe_visibility", "source_field": "growth_direction"},
        },
        "map_trace": [
            "private_scene<=lived_scene",
            "hidden_mechanism<=origin_hint",
            "protective_pattern<=shadow_or_friction",
            "gift_in_silence<=gift",
            "safe_visibility<=growth_direction",
        ],
        "deselected_trace": [
            "identity_polarity=pending",
            "held_plurality=pending",
            "emotional_base=pending",
            "phase4_renderer=not_enabled",
        ],
        "scope_guards": [
            "pilot_only_hidden_private",
            "no_public_output_change",
            "no_global_taxonomy_promotion",
        ],
    }
    if inherited:
        payload.update({k: v for k, v in inherited.items() if k not in {"source_kind", "source_candidate_id"}})
        payload["source_kind"] = source_kind
        payload["source_candidate_id"] = str(source.get("id") or "").strip()
        payload["role_bindings"] = payload.get("role_bindings") or {}
        payload["role_bindings"]["origin_hint"] = {
            **dict((payload["role_bindings"].get("origin_hint") or {})),
            "eligible": origin_hint["eligible"],
            "allow_reasons": list(origin_hint["allow_reasons"]),
            "deny_reasons": list(origin_hint["deny_reasons"]),
        }
    return payload


def _is_istanbul_1996_hidden_private_love_signature(
    source: Mapping[str, Any],
) -> bool:
    trace = source.get("evidence_trace") if isinstance(source.get("evidence_trace"), Mapping) else {}
    primitive = trace.get("primitive_facts") if isinstance(trace.get("primitive_facts"), Mapping) else {}
    placements = primitive.get("placements") if isinstance(primitive.get("placements"), Sequence) else []
    angles = primitive.get("angles") if isinstance(primitive.get("angles"), Sequence) else []

    normalized_placements = {
        (
            str(item.get("planet") or "").strip().lower(),
            str(item.get("sign") or "").strip().lower(),
            int(item.get("house") or 0),
        )
        for item in placements
        if isinstance(item, Mapping) and str(item.get("planet") or "").strip()
    }
    normalized_angles = {
        (
            str(item.get("angle") or "").strip().lower(),
            str(item.get("sign") or "").strip().lower(),
        )
        for item in angles
        if isinstance(item, Mapping) and str(item.get("angle") or "").strip()
    }

    return (
        ("asc", "capricorn") in normalized_angles
        and ("mc", "libra") in normalized_angles
        and ("venus", "sagittarius", 12) in normalized_placements
        and ("moon", "leo", 8) in normalized_placements
        and ("sun", "capricorn", 1) in normalized_placements
        and ("mercury", "capricorn", 1) in normalized_placements
    )


def _match_supported_relationship_hidden_private_love_variant(
    source: Mapping[str, Any],
) -> str | None:
    source_id = str(source.get("id") or "").strip()
    if (
        source_id in _RELATIONSHIP_HIDDEN_PRIVATE_LOVE_ALLOWED_PACKET_IDS
        and source.get("chart_facts_match") is True
    ):
        return "istanbul_1996_12_28_hidden_private_love"
    if not _is_istanbul_1996_hidden_private_love_signature(source):
        return None
    return "istanbul_1996_12_28_hidden_private_love"


def _meets_relationship_hidden_private_love_public_quality(
    card: Mapping[str, Any],
) -> bool:
    if not _meets_public_quality(card):
        return False
    slides = card.get("slides")
    if not isinstance(slides, Sequence) or isinstance(slides, (str, bytes)):
        return False
    if len(slides) != 5:
        return False
    seen_ids: set[str] = set()
    seen_titles: set[str] = set()
    seen_bodies: set[str] = set()
    for item in slides:
        if not isinstance(item, Mapping):
            return False
        slide_id = str(item.get("id") or "").strip()
        title = str(item.get("title") or "").strip()
        body = str(item.get("body") or "").strip()
        if not slide_id or not title or not body:
            return False
        if "\n" in body:
            return False
        if "astro_hint" in item:
            return False
        lowered = f"{title} {body}".lower()
        if any(token in lowered for token in _BANNED_PUBLIC_TOKENS):
            return False
        if _has_turkish_ascii_residue(title) or _has_turkish_ascii_residue(body):
            return False
        if slide_id in seen_ids or title in seen_titles or body in seen_bodies:
            return False
        seen_ids.add(slide_id)
        seen_titles.add(title)
        seen_bodies.add(body)
    why_this_exists = card.get("why_this_exists")
    if why_this_exists is not None:
        if not isinstance(why_this_exists, Mapping):
            return False
        if str(why_this_exists.get("title") or "").strip() != "Nereden geliyor?":
            return False
        if not str(why_this_exists.get("body") or "").strip():
            return False
    return True


def render_relationship_hidden_private_love_card_v0_10_phase2(
    source: Mapping[str, Any],
    *,
    source_kind: str,
) -> dict[str, Any] | None:
    if not _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL"):
        return None
    if not _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE"):
        return None
    if not relationship_hidden_private_love_public_detail_lane_enabled():
        return None
    if not isinstance(source, Mapping):
        return None

    variant = _match_supported_relationship_hidden_private_love_variant(source)
    if variant is None:
        return None

    source_id = str(source.get("id") or "").strip()
    public_eligibility = (
        source.get("public_eligibility")
        if isinstance(source.get("public_eligibility"), Mapping)
        else {}
    )
    meta = source.get("meta") if isinstance(source.get("meta"), Mapping) else {}

    if source_kind == "composed_semantic":
        if not _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B"):
            return None
        if not _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT"):
            return None
        if str(source.get("source_type") or "").strip() != "composed_semantic":
            return None
        if str(source.get("family") or "").strip() != "relationship_route":
            return None
        if str(source.get("subtype") or "").strip() != "hidden_private_love":
            return None
        if source.get("chart_facts_match") is not True:
            return None
        if not bool(public_eligibility.get("detail_eligible")):
            return None
        if bool(public_eligibility.get("public_support_eligible")) or bool(
            public_eligibility.get("public_main_eligible")
        ):
            return None
        if bool(meta.get("subtype_default_fallback")):
            return None
    elif source_kind == "exact_owner":
        if source_id not in _RELATIONSHIP_HIDDEN_PRIVATE_LOVE_ALLOWED_PACKET_IDS:
            return None
        if source.get("chart_facts_match") is not True:
            return None
    else:
        return None

    source_trace = {
        "source_kind": source_kind,
        "family": str(source.get("family") or "").strip(),
        "subtype": str(source.get("subtype") or "").strip(),
        "domain_reason": list(source.get("domain_reason") or []),
        "technical_anchors": list(source.get("technical_anchors") or []),
    }
    source_refs = [source_id] if source_id else []

    card = {
        "id": f"composed_detail::{source_id or 'relationship_hidden_private_love_pattern'}::{variant}",
        "node_id": f"promise::{source_id or 'relationship_hidden_private_love_pattern'}",
        "headline": "Bazı duygular sende önce içeride büyüyor olabilir.",
        "teaser": "Sevgi bazen önce iç dünyanda anlam kazanıyor olabilir.",
        "body": (
            "Bu kart, sevginin önce içeride anlam kazanıp güvenli olduğunda gerçek temasla buluştuğu bir yakınlık biçimini açar. "
            "Dışarıdan sakin görünen yerde, çoğu zaman korunmak isteyen daha derin bir duygu çalışır."
        ),
        "chips": ["İlişki", "Venüs 12. ev", "İçeride büyüyen sevgi"],
        "family": "relationship_hidden_private_love",
        "emphasis": "detail",
        "origin": "composed_detail_renderer_v0_10_phase2",
        "slides": [
            {
                "id": f"slide::{source_id or 'relationship_hidden_private_love_pattern'}::private_scene",
                "title": "Hemen göstermiyorsun",
                "body": (
                    "Birine karşı bir şey hissettiğinde, bunu hemen dışarıya açmak istemeyebilirsin. "
                    "Önce kendi içinde anlamak, emin olmak ve biraz da korumak istersin. "
                    "Bu yüzden dışarıdan sakin ya da mesafeli görünebilirsin. "
                    "Ama bu, az hissettiğin anlamına gelmez; sadece duygularını herkes gibi açık yaşamıyorsun."
                ),
            },
            {
                "id": f"slide::{source_id or 'relationship_hidden_private_love_pattern'}::hidden_mechanism",
                "title": "Sevgi sende anlamla karışabilir",
                "body": (
                    "Venüs’ünün 12. evde olması, sevgiyi bazen açıkça gösterilen bir duygu olmaktan çok, içeride taşınan bir "
                    "anlam haline getirir. Yay tonu ise bu sevgiye mesafe, umut, büyük resim ve “bu bana ne açtı?” sorusunu ekler. "
                    "Bu yüzden bazen sadece kişiye değil, o kişinin sende uyandırdığı ihtimale de bağlanabilirsin."
                ),
            },
            {
                "id": f"slide::{source_id or 'relationship_hidden_private_love_pattern'}::protective_pattern",
                "title": "Saklamak bazen korumak gibidir",
                "body": (
                    "Bir duyguyu hemen göstermek, onu küçültecek ya da savunmasız bırakacakmış gibi gelebilir. "
                    "Bu yüzden kalbin bazen sevdiği şeyi önce kendi içinde korumak ister. "
                    "Ama uzun süre sadece içeride kalan sevgi, gerçek davranışla sınanmadığında büyüyebilir, idealize olabilir ya da olduğundan daha ulaşılmaz hale gelebilir."
                ),
            },
            {
                "id": f"slide::{source_id or 'relationship_hidden_private_love_pattern'}::gift_in_silence",
                "title": "İçten bağlılık sende güçlü çalışır",
                "body": (
                    "Bu yerleşim sende sessiz ama derin bir bağlılık verebilir. "
                    "Sevdiğin şeyi hemen tüketmek, hemen açıklamak ya da herkesin göreceği şekilde büyütmek istemeyebilirsin. "
                    "Güven duyduğunda sevgin cömert, anlamlı ve uzun süre yaşayan bir yere dönüşebilir; kolay söylenmeyen ama varlığı hissedilen bir sıcaklık taşıyabilirsin."
                ),
            },
            {
                "id": f"slide::{source_id or 'relationship_hidden_private_love_pattern'}::safe_visibility",
                "title": "Kalbini sadece içeride taşımak zorunda değilsin",
                "body": (
                    "Bu hat sana, içinde büyüyen sevgiyi güvenli olduğunda gerçek temasla buluşturmayı öğretir. "
                    "Her şeyi hemen açmak zorunda değilsin; ama gerçekten güvendiğin yerde, duygunu sadece içinde taşımak yerine küçük bir davranışla, sade bir cümleyle ya da daha açık bir varlıkla gösterebilirsin."
                ),
            },
        ],
        "why_this_exists": {
            "title": "Nereden geliyor?",
            "body": (
                "Venüs’ün 12. evde olması, sevgi ve değer alanını daha içsel, saklı ve görünmeden olgunlaşan bir yerden çalıştırır. "
                "Yay vurgusu ise bu alana anlam, uzaklık, umut ve büyüme isteği katar. "
                "Bu yüzden sevgi sende bazen sadece bir kişiye değil, o kişinin iç dünyanda açtığı anlama da bağlanabilir."
            ),
        },
        "source_type": str(source.get("source_type") or source_kind).strip(),
        "source_candidate_id": source_id,
        "public_job": "detail_only",
        "source_anchor_trace": source_trace,
        "source_refs": source_refs,
    }
    if relationship_hidden_private_love_phase3_internal_metadata_enabled():
        card["deep_read_phase3"] = _build_relationship_hidden_private_love_phase3_internal_metadata(
            source,
            source_kind=source_kind,
        )
    if (
        relationship_hidden_private_love_deep_read_renderer_enabled()
        and "deep_read_phase3" in card
    ):
        # Phase-4 B2 — actual content composition. Replaces the
        # Phase-2 static slides with the deep_read voice per the
        # frozen authoring packet (Rules 1–4) for the hidden/private
        # pilot. Slide IDs / surface roles / shape are preserved
        # (5 slides, each {id, title, body}) so the public contract
        # stays stable (implementation request §4 invariant 2:
        # no public schema widening in first pass).
        #
        # Inline origin / past-claim language is INTENTIONALLY NOT
        # added in this first pass: authoring packet §4 mandates
        # origin_hint default = opt-in expandable (not inline), and
        # the implementation request §2 defers auxiliary surfaces.
        # The origin_hint role_binding telemetry remains intact in
        # `deep_read_phase3` for a later opt-in surface decision.
        #
        # Gated on `deep_read_phase3 in card` so the Phase-3
        # eligibility chain (allowlist + origin-hint assessment) is
        # required. Marker is stripped on promotion by the
        # _strip_to_public_visible allowlist.
        card["slides"] = _build_relationship_hidden_private_love_phase4_deep_read_slides(
            source_id=source_id,
        )
        card["deep_read_phase4_render_path"] = {
            "version": "v0_10_phase4_minimal",
            "source_kind": str(source_kind),
            "stub": False,
            "slide_count": len(card["slides"]),
            "inline_origin_hint": False,
        }
    if not _meets_relationship_hidden_private_love_public_quality(card):
        return None
    return card


def _build_relationship_hidden_private_love_phase4_deep_read_slides(
    *, source_id: str,
) -> list[dict[str, str]]:
    """Phase-4 hidden/private pilot deep_read slides.

    TR-primary template set. Same 5-surface-role structure as Phase-2
    (private_scene → hidden_mechanism → protective_pattern →
    gift_in_silence → safe_visibility) so the public slide contract is
    preserved. Per Rule 4 each slide carries its own cadence; per
    Rule 3 each opens on a lived behavior, not an abstract category;
    per Rule 2 the thesis lands once (final slide) and is not
    pre-stated; per Rule 1 each slide carries one spine.

    No inline origin_hint / past-claim language in this first pass
    (see render_relationship_hidden_private_love_card_v0_10_phase2
    routing block for rationale).
    """
    sid = source_id or "relationship_hidden_private_love_pattern"
    return [
        {
            # private_scene · [ritim: sakin, içe dönük, yere basan]
            "id": f"slide::{sid}::private_scene",
            "title": "Hemen göstermiyorsun",
            "body": (
                "Sen birine karşı bir şey hissettiğinde onu hemen "
                "gösterebilen yapıda değilsin. Önce içinde onun anlamını "
                "düşünür, senin için ne ifade ettiğini anlamaya "
                "çalışırsın. Bir şeyleri diğerlerine göre daha hassas "
                "ve derinden işlediğin için, düşünmeden söylediğinde "
                "karşı tarafın anlamayacağından ya da o hissin senin "
                "içindeki anlamının bozulacağından çekiniyor "
                "olabilirsin."
            ),
        },
        {
            # hidden_mechanism · [ritim: kontrast — dış bakıştan içe + placement entegre]
            "id": f"slide::{sid}::hidden_mechanism",
            "title": "Sessizliğin boşluk değil",
            "body": (
                "Bu yüzden dışarıdan biri seni bazen olduğundan sakin "
                "ya da biraz uzak bulabilir. Oysa içinde sakinlik "
                "değil, sürekli bir hareket var: sezgin, hayal gücün, "
                "bağlanma biçimin orada güçlü çalıştığı için bazen "
                "susarsın. Sezgilerinin \"şimdi\" dediği zamanı "
                "beklersin. 12. evinin Yay'da olması bu beklemeye "
                "bir yön daha katıyor — bir his sende anlam kazanmadan, "
                "daha büyük bir bütüne nasıl bağlandığını hissetmeden "
                "dışarı vermeyebilirsin."
            ),
        },
        {
            # protective_pattern · [ritim: sessiz, dürüst, dramsız — konuşan ton]
            "id": f"slide::{sid}::protective_pattern",
            "title": "Saklamak her zaman kaçmak değil",
            "body": (
                "Aslında senin yaptığın korkmak ya da kaçmak değil; "
                "bir şeyi koruma biçimindir. Onu başkasının sözüyle "
                "bozdurmadan, kendi içinde sahip çıkmak istersin. "
                "Doğru şekilde dışarı çıkmasını, karşı tarafın da "
                "onu öyle hissetmesini önemsersin. Yine de bir "
                "bedeli olabilir: her duyguyu tek başına taşımak yorar."
            ),
        },
        {
            # gift_in_silence · [ritim: sıcak, açılan, cömert + light placement]
            "id": f"slide::{sid}::gift_in_silence",
            "title": "İçten bağlılık sende güçlü çalışır",
            "body": (
                "Sevgi sende hemen tüketilmek istemez. Venüs'ün "
                "Yay'da işlemesi sevgine anlam arayan bir karakter "
                "veriyor: sevdiğin şeye dair sessiz ama derin bir "
                "bağlılık taşırsın. Güven oluştuğunda bu sıcaklık "
                "cömert, anlamlı ve uzun süre yaşayan bir bağa "
                "dönüşebilir — kolay söylenmeyen ama varlığı "
                "hissedilen bir şey."
            ),
        },
        {
            # safe_visibility · [ritim: yatışan, eşik — imza bir kez]
            "id": f"slide::{sid}::safe_visibility",
            "title": "İçeride taşımak ile gösterebilmek arasında",
            "body": (
                "Her şeyi hemen açmak zorunda değilsin. Ama içeride "
                "büyüttüğün şeyi güvendiğin bir yerde gerçek temasla "
                "buluşturabildiğinde, bu sende hem koruyan hem "
                "ilişkini daha gerçek kılan bir denge kurar. Sevgi "
                "sadece içeride taşınmaya devam etmek zorunda değil."
            ),
        },
    ]


def project_relationship_hidden_private_love_to_public_lane(
    candidates: Sequence[Mapping[str, Any]] | None,
    *,
    cluster_payload: Mapping[str, Any] | None,
) -> list[dict[str, Any]]:
    if not relationship_hidden_private_love_public_detail_lane_enabled():
        return []
    if not _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL"):
        return []
    if not _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE"):
        return []

    candidate_items = [
        dict(item)
        for item in (candidates or [])
        if isinstance(item, Mapping)
    ]
    cluster_payload = dict(cluster_payload or {})

    for candidate in candidate_items:
        if str(candidate.get("id") or "").strip() not in _RELATIONSHIP_HIDDEN_PRIVATE_LOVE_ALLOWED_PACKET_IDS:
            continue
        card = render_relationship_hidden_private_love_card_v0_10_phase2(
            candidate,
            source_kind="exact_owner",
        )
        if card is None:
            continue
        variant = _variant_from_card_id(str(card.get("id") or ""))
        if variant not in _RELATIONSHIP_HIDDEN_PRIVATE_LOVE_VARIANT_ALLOWLIST:
            continue
        return [_strip_to_public_visible(card)]

    clusters = cluster_payload.get("clusters") if isinstance(cluster_payload.get("clusters"), Sequence) else []
    detail_cluster_ids = {
        str(item).strip()
        for item in ((cluster_payload.get("surface_plan") or {}).get("detail_cluster_ids") or [])
        if str(item).strip()
    }
    matching_cluster = next(
        (
            dict(cluster)
            for cluster in clusters
            if isinstance(cluster, Mapping)
            and str(cluster.get("id") or "").strip() in _RELATIONSHIP_HIDDEN_PRIVATE_LOVE_ALLOWED_CLUSTER_IDS
            and str(cluster.get("id") or "").strip() in detail_cluster_ids
        ),
        None,
    )
    if not matching_cluster:
        return []

    for candidate in candidate_items:
        if str(candidate.get("source_type") or "").strip() != "composed_semantic":
            continue
        if str(candidate.get("family") or "").strip() != "relationship_route":
            continue
        if str(candidate.get("subtype") or "").strip() != "hidden_private_love":
            continue
        card = render_relationship_hidden_private_love_card_v0_10_phase2(
            candidate,
            source_kind="composed_semantic",
        )
        if card is None:
            continue
        variant = _variant_from_card_id(str(card.get("id") or ""))
        if variant not in _RELATIONSHIP_HIDDEN_PRIVATE_LOVE_VARIANT_ALLOWLIST:
            continue
        return [_strip_to_public_visible(card)]
    return []


# ---------------------------------------------------------------------------
# v0.9b.1 — moon_signature.home_inner_security narrow detail rollout.
#
# Three target charts, three bespoke TR copy variants, one new flag.
# The Phase B career allowlist is unchanged — this is a parallel,
# independently-gated extension of the same public lane
# (``profile_public.composed_detail_cards``).
# ---------------------------------------------------------------------------

_MOON_HOME_INNER_SECURITY_VARIANT_ALLOWLIST: tuple[str, ...] = (
    "trabzon_2001_09_14_moon_home_inner_security",
    "fix08_cancer_capricorn_nodes_moon_home_inner_security",
    "cairo_1991_01_15_moon_home_inner_security",
)

_MOON_HOME_INNER_SECURITY_CONFIDENCE_FLOOR: float = 0.80

# Banned phrases for moon_signature.home_inner_security public copy.
# These route the card into generic-family / sentimental / fatalistic
# territory and must be refused before the card lands on a public
# surface. Inherited from the v0.9b.1 plan §6.3.
_MOON_HOME_INNER_SECURITY_BANNED_PHRASES: tuple[str, ...] = (
    "Aile önemlidir",
    "aile önemlidir",
    "Ev hayatın güçlüdür",
    "ev hayatın güçlüdür",
    "Annenle ilişkin",
    "Babanla ilişkin",
    "Ailen senin için her şey",
    "kalbinde yer eden aile",
)


def moon_home_inner_security_public_detail_lane_enabled() -> bool:
    return _env_enabled(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_HOME_INNER_SECURITY_PUBLIC_DETAIL_LANE"
    )


def _match_supported_moon_home_inner_security_variant(
    candidate: Mapping[str, Any],
) -> str | None:
    """Return the v0.9b.1 variant id when the candidate's primitive
    facts match one of the three allowlist signatures, else None.

    The match keys are case-insensitive (primitive_facts placements
    arrive with mixed casing from upstream).
    """
    trace = candidate.get("evidence_trace") if isinstance(candidate.get("evidence_trace"), Mapping) else {}
    primitive = trace.get("primitive_facts") if isinstance(trace.get("primitive_facts"), Mapping) else {}
    placements = primitive.get("placements") if isinstance(primitive.get("placements"), Sequence) else []
    angles = primitive.get("angles") if isinstance(primitive.get("angles"), Sequence) else []

    normalized_placements = {
        (
            str(item.get("planet") or "").strip().lower(),
            str(item.get("sign") or "").strip().lower(),
            int(item.get("house") or 0),
        )
        for item in placements
        if isinstance(item, Mapping) and str(item.get("planet") or "").strip()
    }
    normalized_angles = {
        (
            str(item.get("angle") or "").strip().lower(),
            str(item.get("sign") or "").strip().lower(),
        )
        for item in angles
        if isinstance(item, Mapping) and str(item.get("angle") or "").strip()
    }

    # cairo_1991_01_15: Moon Capricorn 4H + Saturn Capricorn 4H + IC Capricorn
    if (
        ("ic", "capricorn") in normalized_angles
        and ("moon", "capricorn", 4) in normalized_placements
        and ("saturn", "capricorn", 4) in normalized_placements
    ):
        return "cairo_1991_01_15_moon_home_inner_security"

    # fix08_cancer_capricorn_nodes: Moon Libra 4H + IC Libra + Venus Capricorn 7H
    if (
        ("ic", "libra") in normalized_angles
        and ("moon", "libra", 4) in normalized_placements
        and ("venus", "capricorn", 7) in normalized_placements
    ):
        return "fix08_cancer_capricorn_nodes_moon_home_inner_security"

    # trabzon_2001_09_14: Moon Leo 4H + IC Leo + Sun Virgo 5H
    if (
        ("ic", "leo") in normalized_angles
        and ("moon", "leo", 4) in normalized_placements
        and ("sun", "virgo", 5) in normalized_placements
    ):
        return "trabzon_2001_09_14_moon_home_inner_security"

    return None


def _render_moon_home_inner_security_variant_card(
    *,
    variant: str,
    candidate: Mapping[str, Any],
) -> dict[str, Any] | None:
    candidate_id = str(candidate.get("id") or "").strip()
    source_trace = {
        "family": str(candidate.get("family") or "").strip(),
        "subtype": str(candidate.get("subtype") or "").strip(),
        "domain_reason": list(candidate.get("domain_reason") or []),
        "technical_anchors": list(candidate.get("technical_anchors") or []),
    }
    common_avoid = [
        "Aile önemlidir genelizasyonundan kaçın.",
        "Ev hayatın güçlüdür gibi nostaljik kalıplardan kaçın.",
        "Anne/baba ile birebir ilişki iddiası yapma — Ay rotası iç zemini anlatır.",
    ]

    if variant == "trabzon_2001_09_14_moon_home_inner_security":
        return {
            "id": f"composed_detail::{candidate_id}::{variant}",
            "node_id": f"promise::{candidate_id}",
            "headline": "İç zemininde toparlandığında dış ritmin de sakinleşiyor.",
            "teaser": "Duygusal güvenliğin yerinde olduğunda taşıyıcı oluyor; o zemin sarsıldığında dışarıdaki düzen de hızlıca zorlaşıyor.",
            "body": (
                "Kendine ait özel bir alana ya da güvenli bir köke döndüğünde toparlanıyor, ritmin yeniden yerine oturuyor. "
                "Bu zemin sarsıldığında yalnız iç dünya değil, dış rolün de daha çabuk yorulabiliyor. "
                "Bu hattın armağanı duygusal hafıza, bakım ve içeriden taşınan koruma; sürtüşmesi ise çevreye fazla bağlanma ya da bilinen alana hızla geri çekilme. Büyüme yönü, iç güvenliği yalnız dış zemine bırakmadan içeride taşıyabilmek."
            ),
            "chips": ["İç güven", "Duygusal zemin", "Kök"],
            "detail_items": [],
            "family": "moon_home_inner_security",
            "emphasis": "detail",
            "origin": "composed_detail_renderer_v0_9b_1",
            "evidence_summary": [
                "Ay'ın 4. evdeki yerleşimi iç düzen ihtiyacını öne çıkarıyor.",
                "IC ekseni duygusal toparlanma sahnesini netleştiriyor.",
            ],
            "source_type": "composed_semantic",
            "source_candidate_id": candidate_id,
            "public_job": "detail_only",
            "source_anchor_trace": source_trace,
            "avoid_readings": common_avoid,
        }

    if variant == "fix08_cancer_capricorn_nodes_moon_home_inner_security":
        return {
            "id": f"composed_detail::{candidate_id}::{variant}",
            "node_id": f"promise::{candidate_id}",
            "headline": "Duygusal güvenliğin, içeride kurduğun dengeyle birlikte çalışıyor.",
            "teaser": "İç zeminin sağlamken dışarıdaki rolünü de daha ölçülü taşıyabiliyorsun; o denge bozulduğunda dış ritm çabuk yıpranıyor.",
            "body": (
                "Duygusal güvenliği içeride kurduğun bir denge üzerinden taşıyorsun; bu denge yerindeyken kendini ait hissettiğin alana yaslanabiliyorsun. "
                "İç zeminin sarsıldığında dış dünyadaki ölçü ve sorumluluk hızlıca daha yorucu hale gelebiliyor. "
                "Bu hattın armağanı sakin bir bakım kapasitesi, duygusal hafıza ve koruma; sürtüşmesi ise ihtiyaçlarını fazla içeride tutma ya da düzeni dağıtmamak için fazla geri çekilme. Büyüme yönü, dış sorumluluğu omuzlarken iç güveni de aynı özenle besleyebilmek."
            ),
            "chips": ["İç güven", "Duygusal denge", "Ait olma"],
            "detail_items": [],
            "family": "moon_home_inner_security",
            "emphasis": "detail",
            "origin": "composed_detail_renderer_v0_9b_1",
            "evidence_summary": [
                "Ay'ın 4. evi iç düzen sahnesini taşıyor.",
                "İçeride kurulan denge dış rolün ölçüsünü destekliyor.",
            ],
            "source_type": "composed_semantic",
            "source_candidate_id": candidate_id,
            "public_job": "detail_only",
            "source_anchor_trace": source_trace,
            "avoid_readings": common_avoid,
        }

    if variant == "cairo_1991_01_15_moon_home_inner_security":
        return {
            "id": f"composed_detail::{candidate_id}::{variant}",
            "node_id": f"promise::{candidate_id}",
            "headline": "Duygusal güvenliğin sağlam bir yapı üzerinden taşınıyor.",
            "teaser": "İç zemininde kurulu bir omurga olduğunda kendini düzenleyebiliyorsun; o yapı zayıfladığında dış ritm de hızlıca sertleşebiliyor.",
            "body": (
                "Duygusal güvenliği bir gevşeklik üzerinden değil, içeride kurduğun sağlam bir yapı ve çerçeve üzerinden topluyorsun. "
                "Bu iç omurga yerindeyken kendini düzenleyebiliyorsun; sarsıldığında dış dünyadaki ritm çabuk gerginleşiyor ve kontrol ihtiyacı öne çıkıyor. "
                "Bu hattın armağanı dayanıklılık, duygusal hafıza ve koruma kapasitesi; sürtüşmesi ise iç güveni yalnız dış zeminden bekleme ya da çevreye fazla tutunma. Büyüme yönü, içeride taşınan bir güveni dışarıdan gelen onaya bağlamadan kurabilmek."
            ),
            "chips": ["İç güven", "Sağlam zemin", "Düzenleme"],
            "detail_items": [],
            "family": "moon_home_inner_security",
            "emphasis": "detail",
            "origin": "composed_detail_renderer_v0_9b_1",
            "evidence_summary": [
                "Ay'ın 4. evdeki Satürn-Ay birlikteliği yapısal iç zemini taşıyor.",
                "IC eksenindeki sağlam çerçeve duygusal düzenleme sahnesini netleştiriyor.",
            ],
            "source_type": "composed_semantic",
            "source_candidate_id": candidate_id,
            "public_job": "detail_only",
            "source_anchor_trace": source_trace,
            "avoid_readings": common_avoid,
        }
    return None


def _meets_moon_home_inner_security_public_quality(card: Mapping[str, Any]) -> bool:
    """Stricter quality gate for v0.9b.1: extends ``_meets_public_quality``
    with banned-phrase checks specific to the Moon family + a required
    semantic-direction vocabulary token.
    """
    if not _meets_public_quality(card):
        return False
    fields = ("headline", "teaser", "body")
    combined = " ".join(str(card.get(field) or "") for field in fields)
    for banned in _MOON_HOME_INNER_SECURITY_BANNED_PHRASES:
        if banned in combined:
            return False
    # Must mention at least one of the safety / inner-base / regulation
    # vocabulary tokens (case-insensitive).
    required_tokens = (
        "iç güven",
        "duygusal güvenli",
        "duygusal güvenl",
        "duygusal zemin",
        "iç zemin",
        "kök",
        "ait ol",
        "düzenle",
        "sakinleş",
        "toparla",
    )
    if not any(token in combined.lower() for token in required_tokens):
        return False
    return True


def render_moon_home_inner_security_card_v0_9b_1(
    candidate: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Render a moon_signature.home_inner_security public detail card.

    Returns None unless every gate from the v0.9b.1 plan §1 holds.
    """
    if not _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL"):
        return None
    if not _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE"):
        return None
    if not moon_home_inner_security_public_detail_lane_enabled():
        return None
    if not isinstance(candidate, Mapping):
        return None
    if str(candidate.get("source_type") or "").strip() != "composed_semantic":
        return None
    if str(candidate.get("family") or "").strip() != "moon_signature":
        return None
    if str(candidate.get("subtype") or "").strip() != "home_inner_security":
        return None
    if candidate.get("chart_facts_match") is not True:
        return None

    confidence = float(candidate.get("confidence") or 0.0)
    if confidence < _MOON_HOME_INNER_SECURITY_CONFIDENCE_FLOOR:
        return None

    eligibility = (
        candidate.get("public_eligibility")
        if isinstance(candidate.get("public_eligibility"), Mapping)
        else {}
    )
    if not bool(eligibility.get("detail_eligible")):
        return None
    if bool(eligibility.get("public_support_eligible")) or bool(
        eligibility.get("public_main_eligible")
    ):
        return None

    meta = candidate.get("meta") if isinstance(candidate.get("meta"), Mapping) else {}
    if bool(meta.get("subtype_default_fallback")):
        return None
    # Moon-evidence ownership: defensive. Moon family always self-owns.
    if str(meta.get("moon_evidence_owned_by") or "moon_signature") not in {
        "",
        "moon_signature",
    }:
        return None

    variant = _match_supported_moon_home_inner_security_variant(candidate)
    if variant is None:
        return None

    card = _render_moon_home_inner_security_variant_card(
        variant=variant, candidate=candidate
    )
    if card is None:
        return None
    if not _meets_moon_home_inner_security_public_quality(card):
        return None
    return card


def project_moon_home_inner_security_to_public_lane(
    candidates: Sequence[Mapping[str, Any]] | None,
) -> list[dict[str, Any]]:
    """Render+promote moon_signature.home_inner_security candidates into
    the shared ``profile_public.composed_detail_cards`` lane.

    Mirrors ``project_composed_detail_cards_to_public_lane`` for the
    career family but operates directly on the upstream candidate
    packets rather than on already-rendered trace cards — the Moon
    family does not currently route through the v0.9a.2 trace renderer.
    """
    if not candidates:
        return []
    if not moon_home_inner_security_public_detail_lane_enabled():
        return []
    if not _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL"):
        return []
    if not _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE"):
        return []
    promoted: list[dict[str, Any]] = []
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            continue
        if str(candidate.get("source_type") or "").strip() != "composed_semantic":
            continue
        if str(candidate.get("family") or "").strip() != "moon_signature":
            continue
        if str(candidate.get("subtype") or "").strip() != "home_inner_security":
            continue
        card = render_moon_home_inner_security_card_v0_9b_1(candidate)
        if card is None:
            continue
        variant = _variant_from_card_id(str(card.get("id") or ""))
        if variant not in _MOON_HOME_INNER_SECURITY_VARIANT_ALLOWLIST:
            continue
        promoted.append(_strip_to_public_visible(card))
    return promoted
