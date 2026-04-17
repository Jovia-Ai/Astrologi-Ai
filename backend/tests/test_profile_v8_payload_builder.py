from __future__ import annotations

from app.natal.profile_v8_payload_builder import (
    NarrativeFragment,
    build_profile_and_full_map_v8_payload,
    build_fragment_pool,
    score_fragment_for_section,
    select_profile_v8_sections,
)


def _base_response() -> dict:
    return {
        "metadata": {
            "display_name": "Test User",
            "birth_date": "1996-12-28",
            "birth_place": "Istanbul",
        },
        "core_story_ui": {
            "headline": "Ana eksen",
            "text": "Kısa omurga.",
        },
        "social": {"followers_count": 12, "friends_count": 7, "is_forum_active": True},
        "natal_graph_compact": {"house_rulers": {"1": {"primary_ruler": "Saturn"}}},
        "meta_info": {"stelliums": {"1": 4}},
        "meaning_weighting": {"primary_theme": "identity", "secondary_theme": "net ritim"},
    }


def test_score_fragment_for_section_prefers_exact_orb_anchor() -> None:
    exact = NarrativeFragment(
        id="a",
        domain="effect",
        trigger="moon_trine_venus",
        text="Ay ve Venüs çok yakın açıyla çalışıyor.",
        section_hint="intimacy",
        score=0.6,
        meta={"orb": 0.2},
    )
    loose = NarrativeFragment(
        id="b",
        domain="effect",
        trigger="moon_trine_venus",
        text="Ay ve Venüs açı hattı çalışıyor.",
        section_hint="intimacy",
        score=0.6,
        meta={"orb": 4.8},
    )

    exact_score = score_fragment_for_section(exact, "intimacy", {})
    loose_score = score_fragment_for_section(loose, "intimacy", {})
    assert exact_score > loose_score


def test_select_profile_v8_sections_avoids_repeating_same_signature_everywhere() -> None:
    fragments = [
        NarrativeFragment(
            id="past",
            domain="past_experience",
            trigger="saturn_in_house_3",
            text="Geçmişte ifade alanında ağırlık hissetmiş olabilirsin.",
            section_hint="past_teaser",
            score=0.9,
            source_houses=[3],
        ),
        NarrativeFragment(
            id="first",
            domain="identity",
            trigger="sun_in_house_1",
            text="Dışarıdan görünür, içeride odaklı bir ton var.",
            section_hint="first_impression",
            score=0.85,
            source_houses=[1],
        ),
        NarrativeFragment(
            id="talent",
            domain="talent",
            trigger="mercury_conj_venus",
            text="Estetik ifade ve zihinsel akış birlikte çalışıyor.",
            section_hint="talents",
            score=0.84,
            source_planets=["Mercury", "Venus"],
        ),
        NarrativeFragment(
            id="talk",
            domain="conversation",
            trigger="mercury_in_house_3",
            text="Sohbette fikir inşa etmeyi seviyorsun.",
            section_hint="conversation_hooks",
            score=0.83,
            source_houses=[3],
        ),
        NarrativeFragment(
            id="affects",
            domain="effect",
            trigger="moon_trine_venus",
            text="Yakınlıkta sıcak ama seçici bir ritim çalışıyor.",
            section_hint="affects_you",
            score=0.82,
            source_planets=["Moon", "Venus"],
        ),
        NarrativeFragment(
            id="defense",
            domain="shadow",
            trigger="moon_saturn_square",
            text="Zorlandığında önce kendini geri çekip içeride tartarsın.",
            section_hint="defense",
            score=0.81,
            source_planets=["Moon", "Saturn"],
        ),
        NarrativeFragment(
            id="felt",
            domain="identity",
            trigger="sun_in_house_1_alt",
            text="İlk anda merkezde duran bir enerji hissediliyor.",
            section_hint="first_felt",
            score=0.8,
            source_houses=[1],
        ),
        NarrativeFragment(
            id="intimacy",
            domain="effect",
            trigger="moon_trine_venus_alt",
            text="Güven oluştuğunda hızla yumuşayan bir bağ açılıyor.",
            section_hint="intimacy",
            score=0.79,
            source_planets=["Moon", "Venus"],
        ),
        NarrativeFragment(
            id="mind",
            domain="mechanism",
            trigger="saturn_in_house_3_alt",
            text="Zihnin önce yapı kurar, sonra hızlanır.",
            section_hint="mind",
            score=0.78,
            source_houses=[3],
        ),
        NarrativeFragment(
            id="mission",
            domain="mission",
            trigger="north_node_libra",
            text="Misyonun iş birliği ve denge üzerinden açılıyor.",
            section_hint="mission",
            score=0.77,
        ),
    ]

    selected = select_profile_v8_sections(fragments=fragments, chart_context={})
    primary = [section[0].trigger for section in selected.values() if section]
    assert len(primary) >= 6
    assert len(set(primary)) >= 6


def test_build_fragment_pool_sanitizes_internal_bundle_keys() -> None:
    fragments = build_fragment_pool(
        facts={},
        profile_narrative={},
        sections_v2=[],
        supporting_threads=[],
        narrative_v2={
            "aspect_bundle_selector": {
                "selected_bundles": [
                    {
                        "bundle_type": "relational_pattern_bundle",
                        "score": 0.72,
                        "recognition_tags": ["yakınlık ritmi"],
                        "gift_tags": ["sadakat"],
                        "reflex_tags": ["geri çekilme"],
                        "astro_sources": ["Ay-Satürn"],
                        "source_planets": ["Moon", "Saturn"],
                    }
                ]
            }
        },
        personality_imprint={},
    )
    assert fragments
    assert all("_bundle" not in item.trigger for item in fragments)


def test_profile_v8_selection_differs_between_charts() -> None:
    response_a = _base_response()
    response_a["planets"] = [
        {"planet": "Moon", "house": 8, "sign": "Scorpio"},
        {"planet": "Venus", "house": 12, "sign": "Sagittarius"},
        {"planet": "Saturn", "house": 3, "sign": "Aries"},
        {"planet": "North Node", "house": 9, "sign": "Libra"},
        {"planet": "Sun", "house": 1, "sign": "Capricorn"},
    ]
    response_a["aspects"] = [
        {"planet1": "Moon", "planet2": "Venus", "aspect": "trine", "orb": 0.4},
        {"planet1": "Mercury", "planet2": "Saturn", "aspect": "trine", "orb": 1.1},
    ]

    response_b = _base_response()
    response_b["planets"] = [
        {"planet": "Moon", "house": 2, "sign": "Taurus"},
        {"planet": "Venus", "house": 6, "sign": "Virgo"},
        {"planet": "Saturn", "house": 10, "sign": "Capricorn"},
        {"planet": "North Node", "house": 11, "sign": "Aquarius"},
        {"planet": "Sun", "house": 11, "sign": "Aquarius"},
    ]
    response_b["aspects"] = [
        {"planet1": "Sun", "planet2": "Saturn", "aspect": "conjunction", "orb": 0.2},
        {"planet1": "Mars", "planet2": "Mercury", "aspect": "square", "orb": 0.9},
    ]

    profile_a, _ = build_profile_and_full_map_v8_payload(
        response=response_a,
        profile_narrative={},
        sections_v2=[],
        supporting_threads=[],
        narrative_v2={},
        personality_imprint={},
    )
    profile_b, _ = build_profile_and_full_map_v8_payload(
        response=response_b,
        profile_narrative={},
        sections_v2=[],
        supporting_threads=[],
        narrative_v2={},
        personality_imprint={},
    )

    assert profile_a["differentiators"] != profile_b["differentiators"]
    assert profile_a["hero"]["moon_sign"] != profile_b["hero"]["moon_sign"]
