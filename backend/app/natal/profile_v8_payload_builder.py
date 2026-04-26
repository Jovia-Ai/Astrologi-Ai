from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
import re
from typing import Any, Literal, Mapping, Optional, Sequence

from app.natal.natal_graph import TRADITIONAL_RULERS

FragmentDomain = Literal[
    "past_experience",
    "mechanism",
    "effect",
    "shadow",
    "talent",
    "mission",
    "identity",
    "conversation",
]

FragmentDepth = Literal["profile", "full_map", "both"]

SectionHint = Literal[
    "insight_strip",
    "past_teaser",
    "first_impression",
    "talents",
    "conversation_hooks",
    "affects_you",
    "defense",
    "first_felt",
    "intimacy",
    "mind",
    "mission",
    "archetype_portal",
]


@dataclass
class NarrativeFragment:
    id: str
    domain: FragmentDomain
    trigger: str
    text: str

    score: float = 0.0
    depth: FragmentDepth = "both"
    section_hint: Optional[SectionHint] = None

    headline: Optional[str] = None
    highlight: Optional[str] = None
    chips: list[str] = field(default_factory=list)

    source_facts: list[str] = field(default_factory=list)
    source_planets: list[str] = field(default_factory=list)
    source_houses: list[int] = field(default_factory=list)

    internal_key: Optional[str] = None
    is_internal_only: bool = False

    meta: dict = field(default_factory=dict)


INTERNAL_KEY_BLOCKLIST = (
    "_bundle",
    "_pattern",
    "_internal",
    "_debug",
)


def is_user_visible_fragment(fragment: NarrativeFragment) -> bool:
    if fragment.is_internal_only:
        return False
    key = (fragment.internal_key or "").lower()
    return not any(token in key for token in INTERNAL_KEY_BLOCKLIST)


@dataclass
class HeroPayload:
    display_name: str
    location_age: str
    sun_sign: str
    rising_sign: str
    moon_sign: str
    followers_text: str
    forum_status_text: str


@dataclass
class InsightCellPayload:
    eyebrow: str
    title: str
    subtitle: str
    icon_type: str
    accent: str


@dataclass
class UniqueFactPayload:
    eyebrow: str
    headline: str
    body: str
    stat: str
    stat_label: str
    accent: str


@dataclass
class EditorialSectionPayload:
    eyebrow: str
    headline: str
    body: str
    chips: list[str] = field(default_factory=list)
    callout: Optional[str] = None
    footer: Optional[str] = None
    footer_cta: Optional[str] = None
    highlight: Optional[str] = None
    growth: Optional[str] = None


@dataclass
class EditorialListSectionPayload:
    eyebrow: str
    headline: str
    body: str
    rows: list[str] = field(default_factory=list)
    footer: Optional[str] = None


@dataclass
class TalentItemPayload:
    eyebrow: str
    text: str
    accent: str


@dataclass
class ArchetypePortalPayload:
    headline: str
    body: str
    items: list[dict] = field(default_factory=list)
    cta_label: str = "Arketip akışını aç →"


@dataclass
class ProfileV8Payload:
    hero: HeroPayload
    identity_axis: EditorialSectionPayload
    insight_strip: list[InsightCellPayload] = field(default_factory=list)
    differentiators: list[UniqueFactPayload] = field(default_factory=list)

    past_teaser: Optional[EditorialSectionPayload] = None
    past_teasers: list[EditorialSectionPayload] = field(default_factory=list)
    first_impression: Optional[EditorialSectionPayload] = None
    talents: list[TalentItemPayload] = field(default_factory=list)
    conversation_hooks: Optional[EditorialSectionPayload] = None
    affects_you: Optional[EditorialListSectionPayload] = None
    defense: Optional[EditorialSectionPayload] = None
    first_felt: Optional[EditorialSectionPayload] = None
    intimacy: Optional[EditorialSectionPayload] = None
    mind: Optional[EditorialSectionPayload] = None
    mission_preview: Optional[EditorialSectionPayload] = None
    archetype_portal: Optional[ArchetypePortalPayload] = None


@dataclass
class MissionStepPayload:
    label: str
    text: str
    accent: str


@dataclass
class MissionPayload:
    eyebrow: str
    headline: str
    body: str
    steps: list[MissionStepPayload] = field(default_factory=list)


@dataclass
class FullMapTabPayload:
    pull_quote: Optional[EditorialSectionPayload] = None
    past_fragments: list[EditorialSectionPayload] = field(default_factory=list)
    mechanism: Optional[EditorialSectionPayload] = None
    opening_point: Optional[EditorialSectionPayload] = None
    mission: Optional[MissionPayload] = None
    shadow_fragments: list[EditorialSectionPayload] = field(default_factory=list)
    potentials: list[EditorialSectionPayload] = field(default_factory=list)


@dataclass
class FullMapV8Payload:
    kimlik: FullMapTabPayload
    iliski: FullMapTabPayload
    kariyer: FullMapTabPayload
    golge: FullMapTabPayload


PAST_LAYER_TRIGGERS = {
    "saturn_in_house_3": {
        "domain": "past_experience",
        "section_hint": "past_teaser",
        "headline": "Küçükken konuşmanın bir bedeli olduğunu öğrenmiş olabilirsin.",
        "highlight": "konuşmanın bir bedeli",
        "chips": ["Satürn", "3. ev", "ifade"],
        "text": "Sözünü kurarken önce tartıp sonra açılman, erken dönemde cümlenin ağırlığını hissetmiş olmandan gelebilir.",
    },
    "venus_in_house_12": {
        "domain": "past_experience",
        "section_hint": "defense",
        "headline": "Sevdiğini tam göstermenin zor geldiği bir dönem olmuş olabilir.",
        "highlight": "tam göstermenin zor geldiği",
        "chips": ["Venüs", "12. ev", "gizli ihtiyaç"],
        "text": "Yakınlıkta duygunu önce içeride tutup sonra açma refleksi, görünmeyen bir korunma hattı kurmana yol açmış olabilir.",
    },
    "moon_in_house_8": {
        "domain": "past_experience",
        "section_hint": "intimacy",
        "headline": "Açıldığın bir an sana derinlik ve riskin birlikte geldiğini öğretmiş olabilir.",
        "highlight": "derinlik ve risk",
        "chips": ["Ay", "8. ev", "yakınlık"],
        "text": "Güven eşiğin yükselince kalbin bir anda derinleşiyor; bu hız, yakınlığın sende ne kadar gerçek çalıştığını gösteriyor.",
    },
    "south_node_aries": {
        "domain": "past_experience",
        "section_hint": "mission",
        "headline": "Bir dönem her şeyi tek başına çözmek zorunda hissetmiş olabilirsin.",
        "highlight": "tek başına çözmek",
        "chips": ["GAD", "Koç", "yalnız yük"],
        "text": "İçinde her şeyi tek elde tutan bir çizgi varsa, iş birliğine alan açıldığında bu hat daha esnek çalışıyor.",
    },
}

TALENT_RULES = {
    "mercury_jupiter_signature": {
        "domain": "talent",
        "section_hint": "talents",
        "headline": "Büyük fikir, kalıcı yapı.",
        "chips": ["Merkür", "Jüpiter", "vizyon"],
        "text": "Sende fikir üretimi ile sistemi kurma aynı hatta çalışıyor; doğru zeminde hızla genişleyen bir zihin hattı görünüyor.",
    },
    "moon_venus_harmony": {
        "domain": "talent",
        "section_hint": "talents",
        "headline": "Estetik zeka doğuştan.",
        "chips": ["Ay", "Venüs", "uyum"],
        "text": "Ton, uyum ve duygusal incelik bir araya geldiğinde etkini yükselten doğal bir estetik sezgi devreye giriyor.",
    },
    "neptune_first_house": {
        "domain": "talent",
        "section_hint": "talents",
        "headline": "Sezgi çok yüksek.",
        "chips": ["Neptün", "1. ev", "sezgi"],
        "text": "İnsanların görmediği tonu erken alman, hem ilişkide hem üretimde önseziyi merkeze çıkarıyor.",
    },
}

MISSION_RULES = {
    "north_node_libra": {
        "domain": "mission",
        "section_hint": "mission",
        "headline": "Yalnız çözümden iş birliği ve anlama doğru gidiyorsun.",
        "chips": ["KAD Terazi", "denge", "birlikte üretim"],
        "text": "Sende ilerleme, tek başına yüklenmekten çok ortak ritim ve karşılıklılık kurduğun yerde kolaylaşıyor.",
    },
    "saturn_third_house_teacher": {
        "domain": "mission",
        "section_hint": "mission",
        "headline": "Öğrendiklerini paylaştığın yerde, başkalarının düşüncesi net bir kayma yaşıyor.",
        "chips": ["Satürn", "3. ev", "öğretme"],
        "text": "Kelimelerini yapılandırıp paylaştığında, çevrendeki insanlar için netleştirici ve öğretici bir kanal açılıyor.",
    },
}

ARCHETYPE_LABELS = {
    "relational_pattern_bundle": "İlişki akışı",
    "angle_identity_bundle": "Kimlik ekseni",
    "soft_capacity_bundle": "Yumuşak kapasite",
}

ARCHETYPE_PUBLIC_KEYS = {
    "relational_pattern_bundle": "relationship_flow",
    "angle_identity_bundle": "angle_identity",
    "soft_capacity_bundle": "soft_capacity",
}

PROFILE_SECTION_ORDER: tuple[str, ...] = (
    "past_teaser",
    "first_impression",
    "talents",
    "conversation_hooks",
    "affects_you",
    "defense",
    "first_felt",
    "intimacy",
    "mind",
    "mission",
)

SECTION_DOMAIN_WEIGHTS: dict[str, dict[str, float]] = {
    "past_teaser": {"past_experience": 1.0, "shadow": 0.82, "effect": 0.58},
    "first_impression": {"identity": 1.0, "effect": 0.76, "mechanism": 0.62},
    "talents": {"talent": 1.0, "mechanism": 0.72, "mission": 0.56},
    "conversation_hooks": {"conversation": 1.0, "mechanism": 0.7, "effect": 0.46},
    "affects_you": {"effect": 1.0, "shadow": 0.5, "conversation": 0.42},
    "defense": {"shadow": 1.0, "past_experience": 0.76, "effect": 0.52},
    "first_felt": {"identity": 1.0, "effect": 0.74, "talent": 0.48},
    "intimacy": {"effect": 1.0, "past_experience": 0.7, "shadow": 0.52},
    "mind": {"mechanism": 1.0, "conversation": 0.68, "identity": 0.45},
    "mission": {"mission": 1.0, "identity": 0.62, "past_experience": 0.5},
}

SECTION_HINT_BONUS: dict[str, str] = {
    "past_teaser": "past_teaser",
    "first_impression": "first_impression",
    "talents": "talents",
    "conversation_hooks": "conversation_hooks",
    "affects_you": "affects_you",
    "defense": "defense",
    "first_felt": "first_felt",
    "intimacy": "intimacy",
    "mind": "mind",
    "mission": "mission",
}

SECTION_KEYWORDS: dict[str, tuple[str, ...]] = {
    "past_teaser": ("saturn", "chiron", "south node", "pluto", "12", "8"),
    "conversation_hooks": ("mercury", "mind", "konuş", "iletişim", "zihin"),
    "affects_you": ("yakın", "iliş", "etki", "bağ", "duygu"),
    "defense": ("savun", "koru", "tetik", "çekil"),
    "mind": ("zihin", "mind", "mercury", "ritim", "karar"),
    "mission": ("kuzey", "node", "mc", "amaç", "mission", "öğret"),
}

FULL_MAP_TAB_SPECS: dict[str, dict[str, tuple[str, ...]]] = {
    "kimlik": {
        "pull": ("identity", "mechanism"),
        "past": ("past_experience", "shadow"),
        "mechanism": ("mechanism",),
        "opening": ("effect", "identity"),
        "mission": ("mission",),
        "shadow": ("shadow",),
        "potential": ("talent",),
    },
    "iliski": {
        "pull": ("effect", "conversation"),
        "past": ("past_experience", "effect"),
        "mechanism": ("conversation", "mechanism"),
        "opening": ("effect",),
        "mission": ("mission", "effect"),
        "shadow": ("shadow", "past_experience"),
        "potential": ("talent", "effect"),
    },
    "kariyer": {
        "pull": ("mission", "identity"),
        "past": ("past_experience", "shadow"),
        "mechanism": ("mechanism", "mission"),
        "opening": ("mission", "effect"),
        "mission": ("mission",),
        "shadow": ("shadow",),
        "potential": ("talent", "mission"),
    },
    "golge": {
        "pull": ("shadow", "past_experience"),
        "past": ("past_experience",),
        "mechanism": ("mechanism", "shadow"),
        "opening": ("effect", "shadow"),
        "mission": ("mission",),
        "shadow": ("shadow",),
        "potential": ("talent", "identity"),
    },
}


_PROFILE_BLOCK_TO_DOMAIN: dict[str, tuple[FragmentDomain, SectionHint]] = {
    "identity_aura": ("identity", "first_impression"),
    "mind_voice": ("mechanism", "mind"),
    "drive_rhythm": ("talent", "talents"),
    "love_depth": ("effect", "intimacy"),
    "career_visibility": ("mission", "mission"),
    "home_roots": ("shadow", "defense"),
    "luck_creation": ("talent", "talents"),
}

_SECTION_TO_DOMAIN: dict[str, tuple[FragmentDomain, SectionHint]] = {
    "mind_system": ("mechanism", "mind"),
    "relationships": ("effect", "affects_you"),
    "career_visibility": ("mission", "mission"),
}

_BUNDLE_TO_DOMAIN: dict[str, tuple[FragmentDomain, SectionHint]] = {
    "relational_pattern_bundle": ("effect", "intimacy"),
    "angle_identity_bundle": ("identity", "first_impression"),
    "soft_capacity_bundle": ("talent", "talents"),
    "mental_style_bundle": ("mechanism", "mind"),
    "emotional_regulation_bundle": ("shadow", "defense"),
    "pressure_growth_bundle": ("mission", "mission"),
    "contradiction_bundle": ("shadow", "defense"),
    "personal_core_bundle": ("identity", "first_impression"),
}

_BUNDLE_HEADLINES: dict[str, str] = {
    "relational_pattern_bundle": "İlişki hattında tekrar eden bir desen var.",
    "angle_identity_bundle": "Dışarı verdiğin kimlik tonu güçlü.",
    "soft_capacity_bundle": "Yumuşak kapasitelerin hızlı açılıyor.",
    "mental_style_bundle": "Zihinsel ritminde ayırt edici bir hat var.",
    "emotional_regulation_bundle": "Duyguyu yönetme biçimin, savunma hattının da rengini veriyor.",
    "pressure_growth_bundle": "Baskı altında büyüme refleksin belirgin.",
    "contradiction_bundle": "İçeride iki yönü aynı anda taşıyorsun.",
    "personal_core_bundle": "Merkezinde net bir kişisel omurga var.",
}


def build_profile_and_full_map_v8_payload(
    *,
    response: Mapping[str, Any],
    profile_narrative: Mapping[str, Any] | None,
    sections_v2: Sequence[Mapping[str, Any]] | None,
    supporting_threads: Sequence[Mapping[str, Any]] | None,
    narrative_v2: Mapping[str, Any] | None,
    personality_imprint: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    facts = _build_facts(
        response=response,
        profile_narrative=profile_narrative or {},
        narrative_v2=narrative_v2 or {},
        personality_imprint=personality_imprint or {},
    )
    social = _build_social(response=response)
    fragments = build_fragment_pool(
        facts=facts,
        profile_narrative=profile_narrative or {},
        sections_v2=sections_v2 or [],
        supporting_threads=supporting_threads or [],
        narrative_v2=narrative_v2 or {},
        personality_imprint=personality_imprint or {},
    )

    profile = select_for_profile_v8(fragments=fragments, facts=facts, social=social)
    full_map = select_for_full_map_v8(fragments=fragments, facts=facts)
    return asdict(profile), asdict(full_map)


def build_fragment_pool(
    *,
    facts: Mapping[str, Any],
    profile_narrative: Mapping[str, Any],
    sections_v2: Sequence[Mapping[str, Any]],
    supporting_threads: Sequence[Mapping[str, Any]],
    narrative_v2: Mapping[str, Any],
    personality_imprint: Mapping[str, Any],
) -> list[NarrativeFragment]:
    fragments = _collect_fragments(
        facts=dict(facts),
        profile_narrative=profile_narrative,
        sections_v2=sections_v2,
        supporting_threads=supporting_threads,
        narrative_v2=narrative_v2,
        personality_imprint=personality_imprint,
    )
    sanitized: list[NarrativeFragment] = []
    for fragment in fragments:
        cleaned = _sanitize_fragment(fragment)
        if cleaned is not None:
            sanitized.append(cleaned)
    return sanitized


def select_for_profile_v8(
    *,
    fragments: list[NarrativeFragment],
    facts: dict,
    social: dict,
) -> ProfileV8Payload:
    visible = [
        f for f in fragments if is_user_visible_fragment(f) and f.depth in {"profile", "both"}
    ]
    section_pick = select_profile_v8_sections(fragments=visible, chart_context=facts)
    by_domain = _group_by_domain(visible)
    by_hint = _group_by_hint(visible)

    return ProfileV8Payload(
        hero=build_hero_payload(facts=facts, social=social),
        identity_axis=build_identity_axis(facts=facts, fragments=visible),
        insight_strip=build_insight_strip(facts=facts, fragments=visible),
        differentiators=build_differentiators(facts=facts),
        past_teaser=pick_past_teaser(
            hinted=section_pick.get("past_teaser", []) or by_hint["past_teaser"],
            fallback=by_domain["past_experience"],
        ),
        past_teasers=build_past_teasers(
            hinted=section_pick.get("past_teaser", []) or by_hint["past_teaser"],
            fallback=by_domain["past_experience"],
        ),
        first_impression=build_first_impression(
            hinted=section_pick.get("first_impression", []) or by_hint["first_impression"],
            facts=facts,
            fragments=visible,
        ),
        talents=pick_talents(
            hinted=section_pick.get("talents", []) or by_hint["talents"],
            fallback=by_domain["talent"],
            facts=facts,
        ),
        conversation_hooks=build_conversation_hooks(
            hinted=section_pick.get("conversation_hooks", []) or by_hint["conversation_hooks"],
            fallback=by_domain["conversation"],
            facts=facts,
        ),
        affects_you=build_affects_you(
            hinted=section_pick.get("affects_you", []) or by_hint["affects_you"],
            fallback=by_domain["effect"],
            facts=facts,
        ),
        defense=pick_defense(
            hinted=section_pick.get("defense", []) or by_hint["defense"],
            fallback=by_domain["shadow"],
            growth_source=by_domain["mission"] + by_domain["talent"] + by_domain["identity"],
        ),
        first_felt=build_first_felt(
            hinted=section_pick.get("first_felt", []) or by_hint["first_felt"],
            facts=facts,
            fragments=visible,
        ),
        intimacy=pick_intimacy(
            hinted=section_pick.get("intimacy", []) or by_hint["intimacy"],
            fallback=by_domain["effect"],
            facts=facts,
        ),
        mind=pick_mind(
            hinted=section_pick.get("mind", []) or by_hint["mind"],
            fallback=by_domain["mechanism"],
            facts=facts,
        ),
        mission_preview=build_mission_preview(
            hinted=section_pick.get("mission", []) or by_hint["mission"],
            fallback=by_domain["mission"],
            facts=facts,
        ),
        archetype_portal=build_archetype_portal(
            facts=facts,
            fragments=visible,
        ),
    )


def select_for_full_map_v8(
    *,
    fragments: list[NarrativeFragment],
    facts: dict,
) -> FullMapV8Payload:
    visible = [
        f for f in fragments if is_user_visible_fragment(f) and f.depth in {"full_map", "both"}
    ]
    tab_pick = select_full_map_v8_sections(fragments=visible, chart_context=facts)
    by_domain = _group_by_domain(visible)
    by_hint = _group_by_hint(visible)

    return FullMapV8Payload(
        kimlik=_build_full_map_tab(
            pull_source=tab_pick["kimlik"]["pull"] or (by_domain["identity"] + by_domain["mechanism"]),
            past_source=tab_pick["kimlik"]["past"] or by_domain["past_experience"],
            mechanism_source=tab_pick["kimlik"]["mechanism"] or by_domain["mechanism"],
            opening_source=tab_pick["kimlik"]["opening"] or (by_hint["first_impression"] + by_domain["effect"]),
            mission_source=tab_pick["kimlik"]["mission"] or by_domain["mission"],
            shadow_source=tab_pick["kimlik"]["shadow"] or by_domain["shadow"],
            potential_source=tab_pick["kimlik"]["potential"] or by_domain["talent"],
            pull_eyebrow="KİMLİK",
        ),
        iliski=_build_full_map_tab(
            pull_source=tab_pick["iliski"]["pull"] or (by_domain["effect"] + by_domain["conversation"]),
            past_source=tab_pick["iliski"]["past"] or (by_hint["intimacy"] + by_domain["past_experience"]),
            mechanism_source=tab_pick["iliski"]["mechanism"] or (by_domain["conversation"] + by_domain["mechanism"]),
            opening_source=tab_pick["iliski"]["opening"] or (by_hint["affects_you"] + by_domain["effect"]),
            mission_source=tab_pick["iliski"]["mission"] or (by_hint["mission"] + by_domain["mission"]),
            shadow_source=tab_pick["iliski"]["shadow"] or by_domain["shadow"],
            potential_source=tab_pick["iliski"]["potential"] or by_domain["talent"],
            pull_eyebrow="İLİŞKİ",
        ),
        kariyer=_build_full_map_tab(
            pull_source=tab_pick["kariyer"]["pull"] or (by_domain["mission"] + by_domain["identity"]),
            past_source=tab_pick["kariyer"]["past"] or by_domain["past_experience"],
            mechanism_source=tab_pick["kariyer"]["mechanism"] or by_domain["mechanism"],
            opening_source=tab_pick["kariyer"]["opening"] or (by_domain["mission"] + by_domain["effect"]),
            mission_source=tab_pick["kariyer"]["mission"] or by_domain["mission"],
            shadow_source=tab_pick["kariyer"]["shadow"] or by_domain["shadow"],
            potential_source=tab_pick["kariyer"]["potential"] or by_domain["talent"],
            pull_eyebrow="KARİYER",
        ),
        golge=_build_full_map_tab(
            pull_source=tab_pick["golge"]["pull"] or (by_domain["shadow"] + by_domain["past_experience"]),
            past_source=tab_pick["golge"]["past"] or by_domain["past_experience"],
            mechanism_source=tab_pick["golge"]["mechanism"] or by_domain["mechanism"],
            opening_source=tab_pick["golge"]["opening"] or by_domain["effect"],
            mission_source=tab_pick["golge"]["mission"] or by_domain["mission"],
            shadow_source=tab_pick["golge"]["shadow"] or by_domain["shadow"],
            potential_source=tab_pick["golge"]["potential"] or by_domain["talent"],
            pull_eyebrow="GÖLGE",
        ),
    )


def select_profile_v8_sections(
    *,
    fragments: Sequence[NarrativeFragment],
    chart_context: Mapping[str, Any],
) -> dict[str, list[NarrativeFragment]]:
    used_signatures: dict[str, int] = {}
    selected: dict[str, list[NarrativeFragment]] = {}
    section_limits = {"talents": 3, "affects_you": 3}

    for section_id in PROFILE_SECTION_ORDER:
        ranked = _rank_section_candidates(
            fragments=fragments,
            section_id=section_id,
            chart_context=chart_context,
            used_signatures=used_signatures,
            profile_mode=True,
        )
        limit = section_limits.get(section_id, 1)
        chosen: list[NarrativeFragment] = []
        for fragment in ranked:
            signature = _fragment_signature(fragment)
            repeats = used_signatures.get(signature, 0)
            if repeats >= 1 and section_id not in {"talents", "affects_you"}:
                continue
            chosen.append(fragment)
            used_signatures[signature] = repeats + 1
            if len(chosen) >= limit:
                break
        selected[section_id] = chosen
    return dedupe_selected_signatures(selected)


def select_full_map_v8_sections(
    *,
    fragments: Sequence[NarrativeFragment],
    chart_context: Mapping[str, Any],
) -> dict[str, dict[str, list[NarrativeFragment]]]:
    used_signatures: dict[str, int] = {}
    out: dict[str, dict[str, list[NarrativeFragment]]] = {}
    slot_limits = {
        "pull": 1,
        "past": 3,
        "mechanism": 1,
        "opening": 1,
        "mission": 2,
        "shadow": 3,
        "potential": 3,
    }

    for tab_id, slots in FULL_MAP_TAB_SPECS.items():
        tab_payload: dict[str, list[NarrativeFragment]] = {}
        for slot_id, domains in slots.items():
            section_id = "mission" if slot_id == "mission" else slot_id
            ranked = _rank_section_candidates(
                fragments=[f for f in fragments if f.domain in domains],
                section_id=section_id,
                chart_context=chart_context,
                used_signatures=used_signatures,
                profile_mode=False,
            )
            limit = slot_limits.get(slot_id, 1)
            picked: list[NarrativeFragment] = []
            for fragment in ranked:
                signature = _fragment_signature(fragment)
                repeats = used_signatures.get(signature, 0)
                if repeats >= 2 and slot_id != "past":
                    continue
                picked.append(fragment)
                used_signatures[signature] = repeats + 1
                if len(picked) >= limit:
                    break
            tab_payload[slot_id] = picked
        out[tab_id] = tab_payload
    return out


def score_fragment_for_section(
    fragment: NarrativeFragment,
    section_id: str,
    chart_context: Mapping[str, Any],
    *,
    used_signatures: Mapping[str, int] | None = None,
) -> float:
    base_score = max(0.0, min(float(fragment.score or 0.0), 1.2))
    orb_score = _orb_score(fragment=fragment, chart_context=chart_context)
    placement_score = _placement_score(fragment=fragment, section_id=section_id)
    visibility_score = _visibility_score(fragment=fragment, section_id=section_id)
    section_match_score = _section_match_score(fragment=fragment, section_id=section_id)
    novelty_score = _novelty_score(fragment=fragment, used_signatures=used_signatures or {})
    editorial_fit_score = _editorial_fit_score(fragment=fragment)

    return (
        (0.34 * base_score)
        + (0.16 * orb_score)
        + (0.14 * placement_score)
        + (0.1 * visibility_score)
        + (0.16 * section_match_score)
        + (0.06 * novelty_score)
        + (0.04 * editorial_fit_score)
    )


def dedupe_selected_signatures(
    selected_sections: Mapping[str, list[NarrativeFragment]],
) -> dict[str, list[NarrativeFragment]]:
    deduped: dict[str, list[NarrativeFragment]] = {}
    seen: set[str] = set()
    for section_id, fragments in selected_sections.items():
        output: list[NarrativeFragment] = []
        for fragment in fragments:
            signature = _fragment_signature(fragment)
            if signature in seen:
                continue
            seen.add(signature)
            output.append(fragment)
        if not output and fragments:
            output.append(fragments[0])
        deduped[section_id] = output
    return deduped


def _rank_section_candidates(
    *,
    fragments: Sequence[NarrativeFragment],
    section_id: str,
    chart_context: Mapping[str, Any],
    used_signatures: Mapping[str, int],
    profile_mode: bool,
) -> list[NarrativeFragment]:
    if not fragments:
        return []
    ranked: list[tuple[float, NarrativeFragment]] = []
    for fragment in fragments:
        if profile_mode and fragment.depth not in {"profile", "both"}:
            continue
        if not profile_mode and fragment.depth not in {"full_map", "both", "profile"}:
            continue
        if not is_user_visible_fragment(fragment):
            continue
        score = score_fragment_for_section(
            fragment,
            section_id,
            chart_context,
            used_signatures=used_signatures,
        )
        ranked.append((score, fragment))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [fragment for _, fragment in ranked]


def _section_match_score(fragment: NarrativeFragment, section_id: str) -> float:
    section_hint = SECTION_HINT_BONUS.get(section_id)
    domain_weights = SECTION_DOMAIN_WEIGHTS.get(section_id, {})
    hint_bonus = 0.0
    if section_hint and fragment.section_hint == section_hint:
        hint_bonus = 0.9
    domain_score = domain_weights.get(fragment.domain, 0.1)
    keyword_bonus = 0.0
    haystack = f"{fragment.trigger} {fragment.text} {fragment.headline or ''}".lower()
    for keyword in SECTION_KEYWORDS.get(section_id, ()):
        if keyword in haystack:
            keyword_bonus = 0.2
            break
    return min(1.0, domain_score + hint_bonus + keyword_bonus)


def _placement_score(fragment: NarrativeFragment, section_id: str) -> float:
    houses = set(fragment.source_houses or [])
    section_house_bias = {
        "past_teaser": {4, 8, 12},
        "intimacy": {7, 8, 12},
        "mind": {1, 3, 9},
        "mission": {9, 10, 11},
        "first_impression": {1, 10},
        "first_felt": {1, 5, 10},
    }
    preferred = section_house_bias.get(section_id, set())
    if not houses or not preferred:
        return 0.45 if houses else 0.35
    overlap = len(houses & preferred)
    return min(1.0, 0.35 + (0.28 * overlap))


def _visibility_score(fragment: NarrativeFragment, section_id: str) -> float:
    if section_id in {"past_teaser", "defense", "intimacy"} and fragment.depth == "full_map":
        return 0.38
    if fragment.depth == "profile":
        return 0.95
    if fragment.depth == "both":
        return 0.88
    return 0.62


def _novelty_score(fragment: NarrativeFragment, used_signatures: Mapping[str, int]) -> float:
    repeats = used_signatures.get(_fragment_signature(fragment), 0)
    if repeats <= 0:
        return 1.0
    if repeats == 1:
        return 0.55
    return 0.2


def _editorial_fit_score(fragment: NarrativeFragment) -> float:
    headline = sanitize_public_label(fragment.headline or "")
    body = _safe_text(fragment.text)
    score = 0.35
    if headline:
        score += 0.25
    if 40 <= len(body) <= 260:
        score += 0.25
    if "_" not in body and "__" not in body:
        score += 0.15
    return min(score, 1.0)


def _orb_score(fragment: NarrativeFragment, chart_context: Mapping[str, Any]) -> float:
    orb_value = _extract_orb_value(fragment)
    if orb_value is None:
        if fragment.trigger.startswith("moon_venus"):
            orb_value = _orb_from_label(str(chart_context.get("moon_venus_trine_orb") or ""))
        elif fragment.trigger.startswith("fortune_jupiter"):
            orb_value = _orb_from_label(str(chart_context.get("fortune_jupiter_trine_orb") or ""))
    if orb_value is None:
        return 0.34
    normalized = max(0.0, min(1.0, 1.0 - (orb_value / 8.0)))
    return max(normalized, 0.25)


def _extract_orb_value(fragment: NarrativeFragment) -> float | None:
    meta_orb = fragment.meta.get("orb") if isinstance(fragment.meta, Mapping) else None
    if meta_orb is not None:
        parsed = _safe_float(meta_orb, None)
        if parsed is not None:
            return parsed
    for source in [fragment.text, fragment.highlight or "", fragment.headline or ""]:
        parsed = _orb_from_label(source)
        if parsed is not None:
            return parsed
    return None


def _orb_from_label(value: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)\s*°", str(value or ""))
    if not match:
        return None
    return _safe_float(match.group(1), None)


def _fragment_signature(fragment: NarrativeFragment) -> str:
    planets = ",".join(sorted(str(item).lower() for item in fragment.source_planets))
    houses = ",".join(str(item) for item in sorted(fragment.source_houses))
    if planets or houses:
        return f"{fragment.trigger}|{planets}|{houses}"
    return f"{fragment.trigger}|{fragment.section_hint or ''}|{fragment.domain}"


def build_hero_payload(*, facts: dict, social: dict) -> HeroPayload:
    return HeroPayload(
        display_name=facts.get("display_name", ""),
        location_age=_join_nonempty(
            [
                facts.get("location_label"),
                f'{facts["age"]} yaş' if facts.get("age") else None,
            ],
            " · ",
        ),
        sun_sign=facts.get("sun_sign", ""),
        rising_sign=facts.get("rising_sign", ""),
        moon_sign=facts.get("moon_sign", ""),
        followers_text=_build_followers_text(social),
        forum_status_text="Forum aktif" if social.get("is_forum_active") else "Forum pasif",
    )


def build_identity_axis(*, facts: dict, fragments: list[NarrativeFragment]) -> EditorialSectionPayload:
    headline = facts.get("identity_axis_headline") or "Güç sende zaten var."
    body = facts.get("identity_axis_body") or ""
    if not body:
        identity_fragments = [f for f in fragments if f.domain == "identity" and f.text]
        if identity_fragments:
            body = _shorten(identity_fragments[0].text, 180)
    return EditorialSectionPayload(
        eyebrow="KİMLİK EKSENİ",
        headline=headline,
        body=body,
    )


def build_insight_strip(*, facts: dict, fragments: list[NarrativeFragment]) -> list[InsightCellPayload]:
    aura_title = sanitize_public_label(str(facts.get("aura_label") or "")) or "Dış aura"
    aura_subtitle = sanitize_public_label(str(facts.get("aura_source") or "")) or "İlk temasta yükselen ton"
    ruler_title = sanitize_public_label(str(facts.get("ruler_planet") or "")) or "Yönetici hat"
    ruler_subtitle = sanitize_public_label(str(facts.get("ruler_source") or "")) or "Kimlik yöneticisi"
    rhythm_title = sanitize_public_label(str(facts.get("rhythm_label") or "")) or "İç ritim"
    rhythm_subtitle = sanitize_public_label(str(facts.get("rhythm_description") or "")) or "Enerji akışı"

    return [
        InsightCellPayload(
            eyebrow="Aura",
            title=aura_title,
            subtitle=aura_subtitle,
            icon_type="dot",
            accent="lime",
        ),
        InsightCellPayload(
            eyebrow="Yönetici",
            title=ruler_title,
            subtitle=ruler_subtitle,
            icon_type="ring",
            accent="stone",
        ),
        InsightCellPayload(
            eyebrow="İç ritim",
            title=rhythm_title,
            subtitle=rhythm_subtitle,
            icon_type="wave",
            accent="lavender",
        ),
    ]


def build_differentiators(*, facts: dict) -> list[UniqueFactPayload]:
    items: list[UniqueFactPayload] = []
    accent_cycle = ["lime", "lavender", "stone"]

    if facts.get("stellium_house") and facts.get("stellium_count"):
        items.append(
            UniqueFactPayload(
                eyebrow=f'{facts["stellium_house"]}. ev',
                headline=f'{facts["stellium_count"]} gezegen, tek ev.',
                body="Varlığın taşıdığı yoğunluk nadir.",
                stat=f'{facts["stellium_count"]}×',
                stat_label=f'{facts["stellium_house"]}. ev',
                accent="lime",
            )
        )

    seen_pairs: set[str] = set()
    closest_aspects = facts.get("closest_aspects") if isinstance(facts.get("closest_aspects"), Sequence) else []
    for raw in closest_aspects:
        if not isinstance(raw, Mapping):
            continue
        left = sanitize_public_label(str(raw.get("planet1") or "")).strip()
        right = sanitize_public_label(str(raw.get("planet2") or "")).strip()
        aspect_type = str(raw.get("aspect") or "").strip().lower()
        orb = _safe_float(raw.get("orb"), None)
        if not left or not right or orb is None:
            continue
        pair = " · ".join(sorted([left.lower(), right.lower()]))
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        symbol = _aspect_symbol(aspect_type)
        eyebrow = f"{left} {symbol} {right}".strip()
        headline = _aspect_headline(left=left, right=right, aspect_type=aspect_type)
        stat = f"{orb:.2f}°"
        items.append(
            UniqueFactPayload(
                eyebrow=eyebrow,
                headline=headline,
                body=f"{stat} — exact açı hattı belirgin.",
                stat=stat,
                stat_label="orb",
                accent=accent_cycle[len(items) % len(accent_cycle)],
            )
        )
        if len(items) >= 3:
            break

    if len(items) < 3 and facts.get("moon_venus_trine_orb"):
        stat = str(facts["moon_venus_trine_orb"])
        items.append(
            UniqueFactPayload(
                eyebrow="Ay △ Venüs",
                headline="Estetik zeka doğuştan.",
                body=f"{stat} — yumuşak açı hattı güçlü.",
                stat=stat,
                stat_label="orb",
                accent=accent_cycle[len(items) % len(accent_cycle)],
            )
        )

    if len(items) < 3 and facts.get("fortune_jupiter_trine_orb"):
        stat = str(facts["fortune_jupiter_trine_orb"])
        items.append(
            UniqueFactPayload(
                eyebrow="Kader △ Jüpiter",
                headline="Şans akışı kendiliğinden hızlanıyor.",
                body=f"{stat} — yaratım ve genişleme aynı yönde.",
                stat=stat,
                stat_label="orb",
                accent=accent_cycle[len(items) % len(accent_cycle)],
            )
        )

    return items[:3]


def pick_past_teaser(
    *,
    hinted: list[NarrativeFragment],
    fallback: list[NarrativeFragment],
) -> EditorialSectionPayload | None:
    layers = build_past_teasers(hinted=hinted, fallback=fallback)
    if not layers:
        return None
    primary = layers[0]
    extra = max(len(layers) - 1, 0)
    return EditorialSectionPayload(
        eyebrow=primary.eyebrow,
        headline=primary.headline,
        body=primary.body,
        chips=primary.chips,
        footer=f"{extra} geçmiş katman daha" if extra > 0 else None,
        footer_cta="Tam haritada gör →" if extra > 0 else None,
        highlight=primary.highlight,
    )


def build_past_teasers(
    *,
    hinted: list[NarrativeFragment],
    fallback: list[NarrativeFragment],
) -> list[EditorialSectionPayload]:
    source = hinted or fallback
    if not source:
        return []
    seen: set[str] = set()
    out: list[EditorialSectionPayload] = []
    for fragment in source:
        key = (fragment.trigger or fragment.id or "").strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(
            EditorialSectionPayload(
                eyebrow="BU NEREDEN GELİYOR OLABİLİR",
                headline=fragment.headline or "Geçmişten gelen bir iz var.",
                body=fragment.text,
                chips=fragment.chips[:3],
                highlight=fragment.highlight,
            )
        )
        if len(out) >= 4:
            break
    return out


def build_first_impression(
    *,
    hinted: list[NarrativeFragment],
    facts: dict,
    fragments: list[NarrativeFragment],
) -> EditorialSectionPayload | None:
    source = hinted or [f for f in fragments if f.domain in {"identity", "mechanism"}]
    if not source:
        return None
    top = source[0]
    return EditorialSectionPayload(
        eyebrow="İLK İZLENİM",
        headline=top.headline or "Dışarıdan önce güçlü bir duruş okunuyor.",
        body=_shorten(top.text, 180),
        chips=top.chips[:3],
        highlight=top.highlight,
    )


def pick_talents(
    *,
    hinted: list[NarrativeFragment],
    fallback: list[NarrativeFragment],
    facts: dict,
) -> list[TalentItemPayload]:
    source = hinted or fallback
    picked = _pick_diverse(source, limit=3)
    accents = ["lime", "lavender", "stone"]

    return [
        TalentItemPayload(
            eyebrow=f.headline or _pretty_trigger(f.trigger),
            text=_shorten(f.text, 80),
            accent=accents[i] if i < len(accents) else "stone",
        )
        for i, f in enumerate(picked)
    ]


def build_conversation_hooks(
    *,
    hinted: list[NarrativeFragment],
    fallback: list[NarrativeFragment],
    facts: dict,
) -> EditorialSectionPayload | None:
    source = hinted or fallback
    if source:
        top = source[0]
        return EditorialSectionPayload(
            eyebrow="BU KİŞİYLE NE KONUŞULUR",
            headline=top.headline or "Fikir alışverişi. Derin konular. Uzun vadeli planlar.",
            body=_shorten(top.text, 180),
            callout='“Projeler, fikirler, ne inşa ediyorsun?”',
            chips=top.chips[:3],
            highlight=top.highlight,
        )

    if facts.get("mercury_prominent"):
        return EditorialSectionPayload(
            eyebrow="BU KİŞİYLE NE KONUŞULUR",
            headline="Fikir alışverişi. Derin konular. Uzun vadeli planlar.",
            body="Yüzeysel sohbet yormaz ama büyütmez.",
            callout='“Projeler, fikirler, ne inşa ediyorsun?”',
        )
    return None


def build_affects_you(
    *,
    hinted: list[NarrativeFragment],
    fallback: list[NarrativeFragment],
    facts: dict,
) -> EditorialListSectionPayload | None:
    source = hinted or fallback
    if not source:
        return None

    rows = [_shorten(f.text, 110) for f in source[:3] if f.text]
    if not rows:
        return None
    return EditorialListSectionPayload(
        eyebrow="SENİ NASIL ETKİLER",
        headline=source[0].headline or "Başta mesafeli, yakında çok farklı.",
        body="Kalbin, güven olmadan yarım açılmaz.",
        rows=rows,
        footer=None,
    )


def pick_defense(
    *,
    hinted: list[NarrativeFragment],
    fallback: list[NarrativeFragment],
    growth_source: list[NarrativeFragment] | None = None,
) -> EditorialSectionPayload | None:
    source = hinted or fallback
    if not source:
        return None

    top = source[0]
    growth_text: str | None = None
    if growth_source:
        top_chips = {chip.strip().lower() for chip in top.chips if chip.strip()}
        best = None
        for fragment in growth_source:
            text = (fragment.text or "").strip()
            if not text:
                continue
            frag_chips = {chip.strip().lower() for chip in fragment.chips if chip.strip()}
            if top_chips and frag_chips and top_chips & frag_chips:
                best = fragment
                break
            best = best or fragment
        if best is not None:
            growth_text = _shorten(best.text, 160)
    return EditorialSectionPayload(
        eyebrow="SAVUNMA MEKANİZMAN",
        headline=top.headline or "Sevilmek için kendini değil, parlayan halini gösteriyorsun.",
        body=_shorten(top.text, 220),
        chips=top.chips[:3],
        highlight=top.highlight,
        growth=growth_text,
    )


def build_first_felt(
    *,
    hinted: list[NarrativeFragment],
    facts: dict,
    fragments: list[NarrativeFragment],
) -> EditorialSectionPayload | None:
    source = hinted or [f for f in fragments if f.domain in {"identity", "effect"} and f.text]
    if not source:
        return None
    top = source[0]
    return EditorialSectionPayload(
        eyebrow="İLK HİSSEDİLEN ŞEY",
        headline=top.headline or "İlk anda güçlü ama ölçülü bir ton hissediliyor.",
        body=_shorten(top.text, 180),
        chips=top.chips[:3],
        highlight=top.highlight,
    )


def pick_intimacy(
    *,
    hinted: list[NarrativeFragment],
    fallback: list[NarrativeFragment],
    facts: dict,
) -> EditorialSectionPayload | None:
    source = hinted or fallback
    if not source and not facts.get("relationship_axis"):
        return None

    top = source[0] if source else None
    return EditorialSectionPayload(
        eyebrow="YAKINLIK",
        headline=(top.headline if top and top.headline else "Yakınlık sende nasıl açılıyor"),
        body=(
            top.text
            if top
            else "İlişkide önce yanında gerçekten yumuşayabildiğin bir bağ arıyorsun."
        ),
        chips=(top.chips[:4] if top else ["Güven", "Sadakat", "Derin Temas"]),
        highlight=(top.highlight if top else None),
    )


def pick_mind(
    *,
    hinted: list[NarrativeFragment],
    fallback: list[NarrativeFragment],
    facts: dict,
) -> EditorialSectionPayload | None:
    source = hinted or fallback
    if not source:
        return None

    top = source[0]
    return EditorialSectionPayload(
        eyebrow="ZİHİNSEL İŞLEYİŞ",
        headline=top.headline or "Zihnin nasıl çalışıyor",
        body=_shorten(top.text, 180),
        chips=top.chips[:4] or ["İç Ritim", "İnce Ayar", "Süreklilik"],
        highlight=top.highlight,
    )


def build_mission_preview(
    *,
    hinted: list[NarrativeFragment],
    fallback: list[NarrativeFragment],
    facts: dict,
) -> EditorialSectionPayload | None:
    source = hinted or fallback
    if source:
        top = source[0]
        return EditorialSectionPayload(
            eyebrow="MİSYON",
            headline=top.headline or "Öğrendiklerini paylaştığın yerde başkalarının düşüncesi net kayıyor.",
            body=_shorten(top.text, 180),
            chips=top.chips[:3],
            highlight=top.highlight,
        )

    if facts.get("north_node_sign") == "Libra":
        return EditorialSectionPayload(
            eyebrow="MİSYON",
            headline="Yalnız çözümden iş birliği ve anlama doğru gidiyorsun.",
            body="Hayat seni tek başına yük taşımaktan, birlikte anlam kurmaya çağırıyor.",
            chips=["İş birliği", "Denge", "Anlam"],
        )
    return None


def build_archetype_portal(
    *,
    facts: dict,
    fragments: list[NarrativeFragment],
) -> ArchetypePortalPayload | None:
    raw_items = facts.get("archetype_bundles") or []
    items = []
    seen: set[str] = set()

    for raw in raw_items:
        key = raw.get("key") if isinstance(raw, dict) else str(raw)
        key = str(key or "").strip()
        if not key:
            continue
        display = ARCHETYPE_LABELS.get(key)
        public_key = ARCHETYPE_PUBLIC_KEYS.get(key)
        if not display or not public_key:
            continue
        if public_key in seen:
            continue
        seen.add(public_key)
        items.append({"key": public_key, "display_label": display})

    if not items:
        return None

    return ArchetypePortalPayload(
        headline="Seni yöneten eksenleri birlikte gör.",
        body="Haritandaki aktif kimlik, koruma ve gerilim çizgilerini tek bir akışta gör.",
        items=items[:3],
        cta_label="Arketip akışını aç →",
    )


def _build_full_map_tab(
    *,
    pull_source: list[NarrativeFragment],
    past_source: list[NarrativeFragment],
    mechanism_source: list[NarrativeFragment],
    opening_source: list[NarrativeFragment],
    mission_source: list[NarrativeFragment],
    shadow_source: list[NarrativeFragment],
    potential_source: list[NarrativeFragment],
    pull_eyebrow: str,
) -> FullMapTabPayload:
    pull = _fragment_to_editorial(pull_source[0], eyebrow=pull_eyebrow) if pull_source else None
    past = [_fragment_to_editorial(item, eyebrow="GEÇMİŞ KATMAN") for item in _pick_diverse(past_source, 3)]
    mechanism = _fragment_to_editorial(mechanism_source[0], eyebrow="MEKANİZMA") if mechanism_source else None
    opening = _fragment_to_editorial(opening_source[0], eyebrow="AÇILMA NOKTASI") if opening_source else None
    mission = _build_mission_payload(mission_source)
    shadows = [_fragment_to_editorial(item, eyebrow="GÖLGE DESENİ") for item in _pick_diverse(shadow_source, 3)]
    potentials = [_fragment_to_editorial(item, eyebrow="POTANSİYEL") for item in _pick_diverse(potential_source, 3)]
    return FullMapTabPayload(
        pull_quote=pull,
        past_fragments=past,
        mechanism=mechanism,
        opening_point=opening,
        mission=mission,
        shadow_fragments=shadows,
        potentials=potentials,
    )


def _build_mission_payload(source: list[NarrativeFragment]) -> MissionPayload | None:
    if not source:
        return None
    top = source[0]
    steps = []
    accents = ["lime", "lavender", "stone"]
    for index, fragment in enumerate(_pick_diverse(source, 3), start=1):
        steps.append(
            MissionStepPayload(
                label=f"Adım {index}",
                text=_shorten(fragment.text, 180),
                accent=accents[index - 1] if index - 1 < len(accents) else "stone",
            )
        )
    return MissionPayload(
        eyebrow="MİSYON AKIŞI",
        headline=top.headline or "Yönün, tekrar eden desenleri dönüştürmek.",
        body=_shorten(top.text, 220),
        steps=steps,
    )


def _fragment_to_editorial(fragment: NarrativeFragment, *, eyebrow: str) -> EditorialSectionPayload:
    return EditorialSectionPayload(
        eyebrow=eyebrow,
        headline=fragment.headline or _pretty_trigger(fragment.trigger),
        body=_shorten(fragment.text, 260),
        chips=fragment.chips[:4],
        highlight=fragment.highlight,
    )


def _collect_fragments(
    *,
    facts: dict,
    profile_narrative: Mapping[str, Any],
    sections_v2: Sequence[Mapping[str, Any]],
    supporting_threads: Sequence[Mapping[str, Any]],
    narrative_v2: Mapping[str, Any],
    personality_imprint: Mapping[str, Any],
) -> list[NarrativeFragment]:
    out: list[NarrativeFragment] = []
    out.extend(_fragments_from_profile_blocks(profile_narrative))
    out.extend(_fragments_from_sections(sections_v2))
    out.extend(_fragments_from_threads(supporting_threads))
    out.extend(_fragments_from_bundles(narrative_v2))
    out.extend(_fragments_from_imprint(personality_imprint))
    out.extend(_fragments_from_chart_anchors(facts))
    out.extend(_rule_fragments_from_facts(facts))
    return out


def _fragments_from_profile_blocks(profile_narrative: Mapping[str, Any]) -> list[NarrativeFragment]:
    profile_public = (
        profile_narrative.get("profile_public")
        if isinstance(profile_narrative.get("profile_public"), Mapping)
        else {}
    )
    blocks = profile_public.get("blocks") if isinstance(profile_public.get("blocks"), Sequence) else []
    out: list[NarrativeFragment] = []
    for index, raw in enumerate(blocks):
        if not isinstance(raw, Mapping):
            continue
        block_id = str(raw.get("id") or "").strip()
        text = str(raw.get("body") or raw.get("teaser") or "").strip()
        if not block_id or not text:
            continue
        domain_hint = _PROFILE_BLOCK_TO_DOMAIN.get(block_id)
        if not domain_hint:
            continue
        domain, section_hint = domain_hint
        source_houses = _extract_house_numbers(raw.get("astro_sources"))
        out.append(
            NarrativeFragment(
                id=f"profile:{block_id}:{index}",
                domain=domain,
                trigger=block_id,
                text=text,
                score=max(0.2, 0.95 - (index * 0.06)),
                depth="profile",
                section_hint=section_hint,
                headline=str(raw.get("headline") or "").strip() or None,
                highlight=_pick_highlight(str(raw.get("teaser") or "").strip(), raw.get("chips")),
                chips=_safe_text_list(raw.get("chips"), max_items=4),
                source_facts=_safe_text_list(raw.get("astro_sources"), max_items=3),
                source_houses=source_houses,
            )
        )
    return out


def _fragments_from_sections(sections_v2: Sequence[Mapping[str, Any]]) -> list[NarrativeFragment]:
    out: list[NarrativeFragment] = []
    for index, raw in enumerate(sections_v2):
        if not isinstance(raw, Mapping):
            continue
        section_id = str(raw.get("id") or "").strip()
        text = str(raw.get("body") or raw.get("subtitle") or "").strip()
        if not section_id or not text:
            continue
        domain_hint = _SECTION_TO_DOMAIN.get(section_id)
        if not domain_hint:
            continue
        domain, section_hint = domain_hint
        out.append(
            NarrativeFragment(
                id=f"section:{section_id}:{index}",
                domain=domain,
                trigger=section_id,
                text=text,
                score=max(0.2, 0.8 - (index * 0.05)),
                depth="both",
                section_hint=section_hint,
                headline=str(raw.get("title") or "").strip() or None,
                highlight=_pick_highlight(text, raw.get("chips")),
                chips=_safe_text_list(raw.get("chips"), max_items=4),
                source_houses=_extract_house_numbers(raw.get("chips")),
            )
        )
    return out


def _fragments_from_threads(supporting_threads: Sequence[Mapping[str, Any]]) -> list[NarrativeFragment]:
    out: list[NarrativeFragment] = []
    for index, raw in enumerate(supporting_threads):
        if not isinstance(raw, Mapping):
            continue
        section_id = str(raw.get("section_id") or raw.get("id") or "").strip()
        title = str(raw.get("title") or "").strip()
        text = str(raw.get("paragraph") or raw.get("body") or raw.get("one_liner") or "").strip()
        if not section_id or not text:
            continue
        domain, hint = _resolve_thread_domain_hint(section_id=section_id, title=title, text=text)
        out.append(
            NarrativeFragment(
                id=f"thread:{section_id}:{index}",
                domain=domain,
                trigger=section_id,
                text=text,
                score=max(0.2, 0.72 - (index * 0.04)),
                depth="both",
                section_hint=hint,
                headline=title or None,
                highlight=_pick_highlight(str(raw.get("one_liner") or "").strip(), raw.get("chips")),
                chips=_safe_text_list(raw.get("chips"), max_items=4),
                source_houses=_extract_house_numbers(raw.get("chips")),
            )
        )
    return out


def _fragments_from_bundles(narrative_v2: Mapping[str, Any]) -> list[NarrativeFragment]:
    selector = narrative_v2.get("aspect_bundle_selector")
    if not isinstance(selector, Mapping):
        return []
    selected = selector.get("selected_bundles")
    if not isinstance(selected, Sequence):
        return []
    out: list[NarrativeFragment] = []
    for index, raw in enumerate(selected):
        if not isinstance(raw, Mapping):
            continue
        bundle_type = str(raw.get("bundle_type") or "").strip()
        if not bundle_type:
            continue
        domain_hint = _BUNDLE_TO_DOMAIN.get(bundle_type, ("identity", "first_impression"))
        domain, hint = domain_hint
        recognition = _safe_text_list(raw.get("recognition_tags"), max_items=3)
        gifts = _safe_text_list(raw.get("gift_tags"), max_items=2)
        reflex = _safe_text_list(raw.get("reflex_tags"), max_items=2)
        body = _join_nonempty(
            [
                _join_nonempty(recognition, ", "),
                _join_nonempty(gifts, ", "),
                _join_nonempty(reflex, ", "),
            ],
            ". ",
        )
        if not body:
            continue
        out.append(
            NarrativeFragment(
                id=f"bundle:{bundle_type}:{index}",
                domain=domain,
                trigger=bundle_type,
                text=_ensure_sentence(body),
                score=_safe_float(raw.get("score"), 0.55),
                depth="full_map",
                section_hint=hint,
                headline=_BUNDLE_HEADLINES.get(bundle_type),
                highlight=_pick_highlight(body, recognition),
                chips=_safe_text_list(raw.get("domains"), max_items=3) or recognition[:3],
                source_planets=_safe_text_list(raw.get("source_planets"), max_items=3),
                source_facts=_safe_text_list(raw.get("astro_sources"), max_items=3),
            )
        )
    return out


def _fragments_from_imprint(personality_imprint: Mapping[str, Any]) -> list[NarrativeFragment]:
    entries = personality_imprint.get("entries") if isinstance(personality_imprint.get("entries"), Sequence) else []
    extra_entries = (
        personality_imprint.get("extra_entries")
        if isinstance(personality_imprint.get("extra_entries"), Sequence)
        else []
    )
    out: list[NarrativeFragment] = []
    for index, raw in enumerate(list(entries)[:2]):
        if not isinstance(raw, Mapping):
            continue
        aura = str(raw.get("aura") or raw.get("trait") or "").strip()
        if not aura:
            continue
        out.append(
            NarrativeFragment(
                id=f"imprint:entry:{index}",
                domain="identity",
                trigger=str(raw.get("key") or "imprint_entry"),
                text=aura,
                score=0.66,
                depth="profile",
                section_hint="first_felt",
                headline=str(raw.get("label_tr") or "").strip() or None,
                highlight=_pick_highlight(aura, raw.get("tags")),
                chips=_safe_text_list(raw.get("tags"), max_items=3),
            )
        )
    for index, raw in enumerate(list(extra_entries)[:2]):
        if not isinstance(raw, Mapping):
            continue
        background = str(raw.get("background_hint") or raw.get("shadow") or "").strip()
        if not background:
            continue
        out.append(
            NarrativeFragment(
                id=f"imprint:extra:{index}",
                domain="past_experience",
                trigger=str(raw.get("key") or "imprint_extra"),
                text=background,
                score=0.64,
                depth="both",
                section_hint="past_teaser",
                headline=str(raw.get("label_tr") or "").strip() or None,
                highlight=_pick_highlight(background, raw.get("tags")),
                chips=_safe_text_list(raw.get("tags"), max_items=3),
            )
        )
    return out


def _fragments_from_chart_anchors(facts: Mapping[str, Any]) -> list[NarrativeFragment]:
    out: list[NarrativeFragment] = []

    aspects = facts.get("closest_aspects") if isinstance(facts.get("closest_aspects"), Sequence) else []
    for index, raw in enumerate(aspects[:5]):
        if not isinstance(raw, Mapping):
            continue
        left = sanitize_public_label(str(raw.get("planet1") or "")).strip()
        right = sanitize_public_label(str(raw.get("planet2") or "")).strip()
        aspect_type = str(raw.get("aspect") or "").strip().lower()
        orb = _safe_float(raw.get("orb"), None)
        if not left or not right or orb is None:
            continue
        text = f"{left} ile {right} arasındaki {sanitize_public_label(aspect_type)} hattı {orb:.2f}° ile çok yakın çalışıyor."
        domain, hint = _resolve_aspect_domain_hint(left=left, right=right, aspect_type=aspect_type)
        out.append(
            NarrativeFragment(
                id=f"aspect_anchor:{index}",
                domain=domain,
                trigger=f"{left}_{aspect_type}_{right}".lower().replace(" ", "_"),
                text=text,
                score=max(0.58, min(0.95, 1.0 - (orb / 10.0))),
                depth="both",
                section_hint=hint,
                headline=_aspect_headline(left=left, right=right, aspect_type=aspect_type),
                chips=[left, sanitize_public_label(aspect_type), right],
                source_planets=[left, right],
                meta={"orb": orb},
            )
        )

    if facts.get("stellium_house") and facts.get("stellium_count"):
        house = _safe_int(facts.get("stellium_house"), None)
        count = _safe_int(facts.get("stellium_count"), None)
        if house and count:
            out.append(
                NarrativeFragment(
                    id="house_anchor:stellium",
                    domain="identity",
                    trigger=f"stellium_house_{house}",
                    text=f"{house}. evde {count} gezegen birikimi, profile güçlü bir omurga veriyor.",
                    score=0.84,
                    depth="both",
                    section_hint="first_felt",
                    headline="Merkezde toplanan güçlü enerji",
                    chips=[f"{house}. ev", f"{count} gezegen", "yoğunluk"],
                    source_houses=[house],
                )
            )
    return out


def _rule_fragments_from_facts(facts: Mapping[str, Any]) -> list[NarrativeFragment]:
    triggers = _active_rule_triggers(facts)
    out: list[NarrativeFragment] = []
    for trigger in triggers:
        payload = (
            PAST_LAYER_TRIGGERS.get(trigger)
            or TALENT_RULES.get(trigger)
            or MISSION_RULES.get(trigger)
        )
        if not payload:
            continue
        domain = str(payload.get("domain") or "identity")
        hint = str(payload.get("section_hint") or "") or None
        out.append(
            NarrativeFragment(
                id=f"rule:{trigger}",
                domain=domain,  # type: ignore[arg-type]
                trigger=trigger,
                text=str(payload.get("text") or "").strip(),
                score=0.88,
                depth="both",
                section_hint=hint,  # type: ignore[arg-type]
                headline=str(payload.get("headline") or "").strip() or None,
                highlight=str(payload.get("highlight") or "").strip() or None,
                chips=_safe_text_list(payload.get("chips"), max_items=4),
                source_planets=_safe_text_list(payload.get("chips"), max_items=2),
            )
        )
    return out


def _build_facts(
    *,
    response: Mapping[str, Any],
    profile_narrative: Mapping[str, Any],
    narrative_v2: Mapping[str, Any],
    personality_imprint: Mapping[str, Any],
) -> dict[str, Any]:
    metadata = response.get("metadata") if isinstance(response.get("metadata"), Mapping) else {}
    angles = response.get("angles") if isinstance(response.get("angles"), Mapping) else {}
    planets = response.get("planets") if isinstance(response.get("planets"), Sequence) else []
    aspects = response.get("aspects") if isinstance(response.get("aspects"), Sequence) else []
    natal_graph = (
        response.get("natal_graph_compact")
        if isinstance(response.get("natal_graph_compact"), Mapping)
        else {}
    )
    meaning_weighting = (
        response.get("meaning_weighting")
        if isinstance(response.get("meaning_weighting"), Mapping)
        else {}
    )
    meta_summary = response.get("meta") if isinstance(response.get("meta"), Mapping) else {}
    meta_info = response.get("meta_info") if isinstance(response.get("meta_info"), Mapping) else {}
    core_story_ui = response.get("core_story_ui") if isinstance(response.get("core_story_ui"), Mapping) else {}

    sun_sign = _planet_sign(planets, "Sun")
    moon_sign = _planet_sign(planets, "Moon")
    rising_sign = _planet_sign(planets, "Ascendant") or str(angles.get("ascendant_sign") or "").strip()
    saturn_house = _planet_house(planets, "Saturn")
    venus_house = _planet_house(planets, "Venus")
    moon_house = _planet_house(planets, "Moon")
    neptune_house = _planet_house(planets, "Neptune")
    north_node_sign = _planet_sign_by_alias(planets, aliases={"North Node", "True Node", "Mean Node", "Node"})
    south_node_sign = _planet_sign_by_alias(planets, aliases={"South Node"})
    if not south_node_sign and north_node_sign:
        opposite = {
            "Aries": "Libra",
            "Taurus": "Scorpio",
            "Gemini": "Sagittarius",
            "Cancer": "Capricorn",
            "Leo": "Aquarius",
            "Virgo": "Pisces",
            "Libra": "Aries",
            "Scorpio": "Taurus",
            "Sagittarius": "Gemini",
            "Capricorn": "Cancer",
            "Aquarius": "Leo",
            "Pisces": "Virgo",
        }
        south_node_sign = opposite.get(north_node_sign, "")

    house_rulers = natal_graph.get("house_rulers") if isinstance(natal_graph.get("house_rulers"), Mapping) else {}
    first_house = house_rulers.get("1") if isinstance(house_rulers.get("1"), Mapping) else {}
    ruler = str(first_house.get("primary_ruler") or "").strip()
    if not ruler and rising_sign:
        ruler = TRADITIONAL_RULERS.get(str(rising_sign).lower(), "")

    location_label = _location_label(metadata)
    birth_date = str(metadata.get("birth_date") or "").strip()
    age = _age_from_birth_date(birth_date)
    aura_entry = _first_mapping(personality_imprint.get("entries"))
    aura_label = str(aura_entry.get("label_tr") or aura_entry.get("label") or "").strip()
    aura_source = str(aura_entry.get("label_tr") or aura_entry.get("label") or aura_entry.get("key") or "").strip()

    stellium_house, stellium_count = _best_stellium(meta_info.get("stelliums"))
    moon_venus_trine_orb = _format_orb(_find_orb(aspects, "Moon", "Venus", {"trine", "sextile"}))
    fortune_jupiter_trine_orb = _format_orb(
        _find_orb(aspects, "Fortune", "Jupiter", {"trine", "sextile", "conjunction"})
    )
    closest_aspects = _closest_major_aspects(aspects)

    facts: dict[str, Any] = {
        "display_name": str(metadata.get("display_name") or metadata.get("full_name") or "").strip(),
        "location_label": location_label,
        "age": age,
        "sun_sign": sun_sign,
        "rising_sign": rising_sign,
        "moon_sign": moon_sign,
        "saturn_house": saturn_house,
        "venus_house": venus_house,
        "moon_house": moon_house,
        "neptune_house": neptune_house,
        "north_node_sign": north_node_sign,
        "south_node_sign": south_node_sign,
        "identity_axis_headline": str(core_story_ui.get("headline") or "").strip(),
        "identity_axis_body": str(core_story_ui.get("text") or response.get("core_story") or "").strip(),
        "aura_label": aura_label or str(personality_imprint.get("headline") or "").strip() or "—",
        "aura_source": sanitize_public_label(aura_source),
        "ruler_planet": ruler or "—",
        "ruler_source": "1. ev yöneticisi" if ruler else "",
        "rhythm_label": str(meaning_weighting.get("primary_theme") or "").strip() or "—",
        "rhythm_description": str(meaning_weighting.get("secondary_theme") or "").strip(),
        "stellium_house": stellium_house,
        "stellium_count": stellium_count,
        "moon_venus_trine_orb": moon_venus_trine_orb,
        "fortune_jupiter_trine_orb": fortune_jupiter_trine_orb,
        "closest_aspects": closest_aspects,
        "relationship_axis": bool(_safe_text(response.get("sections_v2")) and _contains_text("iliş", response.get("sections_v2"))),
        "mercury_prominent": _mercury_prominent(planets, aspects),
        "archetype_bundles": _extract_archetype_bundles(narrative_v2),
    }
    return facts


def _build_social(*, response: Mapping[str, Any]) -> dict[str, Any]:
    social = response.get("social") if isinstance(response.get("social"), Mapping) else {}
    forum = response.get("forum") if isinstance(response.get("forum"), Mapping) else {}
    return {
        "followers_count": _safe_int(social.get("followers_count"), 0),
        "friends_count": _safe_int(social.get("friends_count"), 0),
        "is_forum_active": bool(
            social.get("is_forum_active")
            or forum.get("is_active")
            or forum.get("active")
        ),
    }


def _active_rule_triggers(facts: Mapping[str, Any]) -> list[str]:
    out: list[str] = []
    saturn_house = _planet_house_from_facts(facts, "saturn_house")
    venus_house = _planet_house_from_facts(facts, "venus_house")
    moon_house = _planet_house_from_facts(facts, "moon_house")
    neptune_house = _planet_house_from_facts(facts, "neptune_house")

    if saturn_house == 3:
        out.append("saturn_in_house_3")
        out.append("saturn_third_house_teacher")
    if venus_house == 12:
        out.append("venus_in_house_12")
    if moon_house == 8:
        out.append("moon_in_house_8")
    if str(facts.get("south_node_sign") or "").strip() == "Aries":
        out.append("south_node_aries")
    if str(facts.get("north_node_sign") or "").strip() == "Libra":
        out.append("north_node_libra")
    if facts.get("moon_venus_trine_orb"):
        out.append("moon_venus_harmony")
    if facts.get("mercury_prominent"):
        out.append("mercury_jupiter_signature")
    if neptune_house == 1:
        out.append("neptune_first_house")
    return out


def _planet_house_from_facts(facts: Mapping[str, Any], key: str) -> int | None:
    value = facts.get(key)
    try:
        ivalue = int(value)
    except (TypeError, ValueError):
        return None
    return ivalue


def _group_by_domain(
    fragments: Sequence[NarrativeFragment],
) -> dict[str, list[NarrativeFragment]]:
    out: dict[str, list[NarrativeFragment]] = {
        "past_experience": [],
        "mechanism": [],
        "effect": [],
        "shadow": [],
        "talent": [],
        "mission": [],
        "identity": [],
        "conversation": [],
    }
    for fragment in fragments:
        out.setdefault(fragment.domain, []).append(fragment)
    for key in out:
        out[key].sort(key=lambda item: item.score, reverse=True)
    return out


def _group_by_hint(
    fragments: Sequence[NarrativeFragment],
) -> dict[str, list[NarrativeFragment]]:
    keys = [
        "insight_strip",
        "past_teaser",
        "first_impression",
        "talents",
        "conversation_hooks",
        "affects_you",
        "defense",
        "first_felt",
        "intimacy",
        "mind",
        "mission",
        "archetype_portal",
    ]
    out: dict[str, list[NarrativeFragment]] = {key: [] for key in keys}
    for fragment in fragments:
        if fragment.section_hint:
            out.setdefault(fragment.section_hint, []).append(fragment)
    for key in out:
        out[key].sort(key=lambda item: item.score, reverse=True)
    return out


def _resolve_thread_domain_hint(
    *,
    section_id: str,
    title: str,
    text: str,
) -> tuple[FragmentDomain, SectionHint]:
    haystack = f"{section_id} {title} {text}".lower()
    if "mind" in haystack or "zihin" in haystack:
        return "mechanism", "mind"
    if "iliş" in haystack or "yakin" in haystack or "relation" in haystack:
        return "effect", "intimacy"
    if "kariyer" in haystack or "görün" in haystack or "career" in haystack:
        return "mission", "mission"
    if "savun" in haystack or "koru" in haystack:
        return "shadow", "defense"
    if "konuş" in haystack or "sohbet" in haystack:
        return "conversation", "conversation_hooks"
    return "identity", "first_impression"


def _extract_archetype_bundles(narrative_v2: Mapping[str, Any]) -> list[dict[str, str]]:
    selector = (
        narrative_v2.get("aspect_bundle_selector")
        if isinstance(narrative_v2.get("aspect_bundle_selector"), Mapping)
        else {}
    )
    selected = selector.get("selected_bundles") if isinstance(selector.get("selected_bundles"), Sequence) else []
    out = []
    for item in selected:
        if not isinstance(item, Mapping):
            continue
        key = str(item.get("bundle_type") or item.get("bundle_id") or "").strip()
        if not key:
            continue
        out.append({"key": key})
    return out


def _best_stellium(value: Any) -> tuple[int | None, int | None]:
    if not isinstance(value, Mapping):
        return None, None
    resolved: list[tuple[int, int]] = []
    for raw_house, raw_count in value.items():
        try:
            house = int(raw_house)
            count = int(raw_count)
        except (TypeError, ValueError):
            continue
        if count >= 3:
            resolved.append((house, count))
    if not resolved:
        return None, None
    resolved.sort(key=lambda item: (-item[1], item[0]))
    house, count = resolved[0]
    return house, count


def _find_orb(
    aspects: Sequence[Any],
    p1: str,
    p2: str,
    allowed_types: set[str],
) -> float | None:
    target = {p1.lower(), p2.lower()}
    best: float | None = None
    aliases = {
        "fortune": {"fortune", "part of fortune", "pars fortuna", "partoffortune"},
        "jupiter": {"jupiter"},
        "moon": {"moon"},
        "venus": {"venus"},
    }

    def normalize(value: Any) -> str:
        return str(value or "").strip().lower().replace("_", " ")

    def match(name: str, target_name: str) -> bool:
        key = normalize(name)
        group = aliases.get(target_name.lower(), {target_name.lower()})
        return key in group

    for raw in aspects:
        if not isinstance(raw, Mapping):
            continue
        aspect_type = str(raw.get("aspect") or raw.get("type") or "").strip().lower()
        if aspect_type not in allowed_types:
            continue
        left = str(raw.get("planet1") or raw.get("a") or "").strip()
        right = str(raw.get("planet2") or raw.get("b") or "").strip()
        pair = set()
        if match(left, p1):
            pair.add(p1.lower())
        if match(left, p2):
            pair.add(p2.lower())
        if match(right, p1):
            pair.add(p1.lower())
        if match(right, p2):
            pair.add(p2.lower())
        if pair != target:
            continue
        orb = _safe_float(raw.get("orb"), None)
        if orb is None:
            continue
        if best is None or orb < best:
            best = orb
    return best


def _format_orb(value: float | None) -> str | None:
    if value is None:
        return None
    return f"{value:.2f}°"


def _closest_major_aspects(aspects: Sequence[Any], *, limit: int = 6) -> list[dict[str, Any]]:
    allowed = {"conjunction", "trine", "square", "opposition", "sextile"}
    rows: list[dict[str, Any]] = []
    for raw in aspects:
        if not isinstance(raw, Mapping):
            continue
        aspect_type = str(raw.get("aspect") or raw.get("type") or "").strip().lower()
        if aspect_type not in allowed:
            continue
        left = sanitize_public_label(str(raw.get("planet1") or raw.get("a") or "").strip())
        right = sanitize_public_label(str(raw.get("planet2") or raw.get("b") or "").strip())
        orb = _safe_float(raw.get("orb"), None)
        if not left or not right or orb is None:
            continue
        rows.append(
            {
                "planet1": left,
                "planet2": right,
                "aspect": aspect_type,
                "orb": orb,
            }
        )
    rows.sort(key=lambda item: float(item.get("orb") or 99.0))
    return rows[:limit]


def _mercury_prominent(planets: Sequence[Any], aspects: Sequence[Any]) -> bool:
    mercury_house = None
    for item in planets:
        if not isinstance(item, Mapping):
            continue
        if str(item.get("planet") or "").strip().lower() == "mercury":
            mercury_house = _safe_int(item.get("house"), None)
            break
    if mercury_house in {1, 3, 6, 9, 10}:
        return True
    count = 0
    for item in aspects:
        if not isinstance(item, Mapping):
            continue
        left = str(item.get("planet1") or "").strip().lower()
        right = str(item.get("planet2") or "").strip().lower()
        if "mercury" in {left, right}:
            count += 1
    return count >= 2


def _extract_house_numbers(value: Any) -> list[int]:
    tokens = _safe_text_list(value, max_items=6)
    out: list[int] = []
    for token in tokens:
        for part in token.replace("·", " ").split():
            numeric = "".join(ch for ch in part if ch.isdigit())
            if not numeric:
                continue
            try:
                house = int(numeric)
            except ValueError:
                continue
            if 1 <= house <= 12 and house not in out:
                out.append(house)
    return out[:3]


def _planet_sign(planets: Sequence[Any], planet: str) -> str:
    normalized = planet.strip().lower()
    for item in planets:
        if not isinstance(item, Mapping):
            continue
        if str(item.get("planet") or item.get("name") or "").strip().lower() != normalized:
            continue
        return str(item.get("sign") or item.get("zodiac_sign") or "").strip()
    return ""


def _planet_house(planets: Sequence[Any], planet: str) -> int | None:
    normalized = planet.strip().lower()
    for item in planets:
        if not isinstance(item, Mapping):
            continue
        if str(item.get("planet") or item.get("name") or "").strip().lower() != normalized:
            continue
        return _safe_int(item.get("house"), None)
    return None


def _planet_sign_by_alias(planets: Sequence[Any], aliases: set[str]) -> str:
    alias_set = {item.strip().lower() for item in aliases}
    for raw in planets:
        if not isinstance(raw, Mapping):
            continue
        name = str(raw.get("planet") or raw.get("name") or "").strip().lower()
        if name in alias_set:
            return str(raw.get("sign") or raw.get("zodiac_sign") or "").strip()
    return ""


def _location_label(metadata: Mapping[str, Any]) -> str:
    location = metadata.get("location") if isinstance(metadata.get("location"), Mapping) else {}
    city = str(location.get("city") or metadata.get("birth_place") or "").strip()
    country = str(location.get("country") or "").strip()
    return _join_nonempty([city, country], ", ")


def _age_from_birth_date(value: str) -> int | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    parts = raw.split("-")
    if len(parts) != 3:
        return None
    try:
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        birth = date(year, month, day)
    except ValueError:
        return None
    today = date.today()
    years = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    return max(years, 0)


def _first_mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Sequence):
        for item in value:
            if isinstance(item, Mapping):
                return item
    return {}


def _safe_text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def sanitize_public_label(value: Any) -> str:
    text = _safe_text(value)
    if not text:
        return ""
    lowered = text.lower()
    if any(token in lowered for token in INTERNAL_KEY_BLOCKLIST):
        return ARCHETYPE_LABELS.get(lowered, "")
    if lowered in ARCHETYPE_LABELS:
        return ARCHETYPE_LABELS[lowered]
    if re.fullmatch(r"[a-z0-9_]+", lowered) and "_" in lowered:
        words = [chunk for chunk in lowered.split("_") if chunk]
        if len(words) > 6:
            return ""
        text = " ".join(words)
    return text.replace("__", " ").replace("_", " ").strip()


def _safe_text_list(value: Any, *, max_items: int = 5) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    out: list[str] = []
    for item in value:
        text = sanitize_public_label(item)
        if not text:
            continue
        if text.lower() in {entry.lower() for entry in out}:
            continue
        out.append(text)
        if len(out) >= max_items:
            break
    return out


def _pick_highlight(text: str, chips_value: Any) -> str | None:
    chips = _safe_text_list(chips_value, max_items=1)
    if chips:
        return chips[0]
    cleaned = sanitize_public_label(text)
    if not cleaned:
        return None
    return cleaned.split(".")[0][:56].strip() or None


def _contains_text(token: str, value: Any) -> bool:
    needle = str(token or "").strip().lower()
    if not needle:
        return False
    if isinstance(value, Mapping):
        return any(_contains_text(needle, nested) for nested in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(_contains_text(needle, nested) for nested in value)
    return needle in str(value or "").lower()


def _ensure_sentence(value: str) -> str:
    text = _safe_text(value)
    if not text:
        return ""
    return text if text[-1] in ".!?" else f"{text}."


def _shorten(text: str, limit: int) -> str:
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _join_nonempty(parts: Sequence[str | None], sep: str = " · ") -> str:
    values = [str(p).strip() for p in parts if p and str(p).strip()]
    return sep.join(values)


def _build_followers_text(social: Mapping[str, Any]) -> str:
    followers = _safe_int(social.get("followers_count"), 0)
    friends = _safe_int(social.get("friends_count"), 0)
    return f"{followers} takip · {friends} arkadaş"


def _pretty_trigger(trigger: str) -> str:
    mapping = {
        "saturn_in_house_3": "Satürn · 3. ev",
        "venus_in_house_12": "Venüs · 12. ev",
        "moon_in_house_8": "Ay · 8. ev",
        "south_node_aries": "Güney Ay Düğümü · Koç",
    }
    return mapping.get(trigger, sanitize_public_label(trigger).title())


def _aspect_symbol(aspect_type: str) -> str:
    symbols = {
        "conjunction": "☌",
        "trine": "△",
        "square": "□",
        "opposition": "☍",
        "sextile": "✶",
    }
    return symbols.get(aspect_type.strip().lower(), "•")


def _aspect_headline(*, left: str, right: str, aspect_type: str) -> str:
    relation = {
        "trine": "Doğal uyum hattı",
        "sextile": "Akışkan iş birliği hattı",
        "conjunction": "Aynı merkezde toplanan vurgu",
        "square": "Gerilimden güç üreten hat",
        "opposition": "Karşı kutupları dengede taşıyan çizgi",
    }.get(aspect_type, "Etkin bir astro bağ")
    return f"{relation}: {left} ve {right}"


def _resolve_aspect_domain_hint(
    *,
    left: str,
    right: str,
    aspect_type: str,
) -> tuple[FragmentDomain, SectionHint]:
    pair = {left.lower(), right.lower()}
    if {"moon", "venus"} & pair:
        return "effect", "intimacy"
    if {"mercury", "saturn"} & pair or {"mercury", "jupiter"} & pair:
        return "mechanism", "mind"
    if {"north node", "mc"} & pair or {"jupiter", "mc"} & pair:
        return "mission", "mission"
    if aspect_type in {"square", "opposition"}:
        return "shadow", "defense"
    return "identity", "first_felt"


def _sanitize_fragment(fragment: NarrativeFragment) -> NarrativeFragment | None:
    headline = sanitize_public_label(fragment.headline or "")
    highlight = sanitize_public_label(fragment.highlight or "")
    text = _safe_text(fragment.text)
    chips = [_safe_text(chip) for chip in fragment.chips]
    cleaned_chips = []
    for chip in chips:
        cleaned = sanitize_public_label(chip)
        if cleaned:
            cleaned_chips.append(cleaned)
    cleaned = NarrativeFragment(
        id=fragment.id,
        domain=fragment.domain,
        trigger=sanitize_public_label(fragment.trigger).replace(" ", "_").lower() or fragment.trigger,
        text=text,
        score=fragment.score,
        depth=fragment.depth,
        section_hint=fragment.section_hint,
        headline=headline or None,
        highlight=highlight or None,
        chips=cleaned_chips[:4],
        source_facts=[sanitize_public_label(item) for item in fragment.source_facts if sanitize_public_label(item)],
        source_planets=[sanitize_public_label(item) for item in fragment.source_planets if sanitize_public_label(item)],
        source_houses=[int(value) for value in fragment.source_houses if _safe_int(value, None)],
        internal_key=fragment.internal_key,
        is_internal_only=fragment.is_internal_only,
        meta=dict(fragment.meta),
    )
    if not cleaned.text:
        return None
    if cleaned.headline and cleaned.headline.lower() == cleaned.text.lower():
        cleaned.headline = None
    return cleaned


def _pick_diverse(source: Sequence[NarrativeFragment], limit: int = 3) -> list[NarrativeFragment]:
    out: list[NarrativeFragment] = []
    seen: set[tuple[str, tuple[str, ...], tuple[int, ...]]] = set()
    for fragment in source:
        key = (
            fragment.trigger,
            tuple(sorted(str(value) for value in fragment.source_planets)),
            tuple(sorted(int(value) for value in fragment.source_houses)),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(fragment)
        if len(out) >= limit:
            break
    return out


def _safe_float(value: Any, default: float | None = 0.0) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int | None = 0) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
