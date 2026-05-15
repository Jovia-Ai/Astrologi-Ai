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
        if isinstance(value, list):
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
