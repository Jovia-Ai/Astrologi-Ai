import copy

from app.meaning.composed_detail_renderer import (
    project_composed_detail_cards_to_public_lane,
    project_relationship_hidden_private_love_to_public_lane,
    render_composed_detail_card_v0_9a_2,
    render_relationship_hidden_private_love_card_v0_10_phase2,
)


def _candidate(*, variant: str) -> dict:
    base = {
        "id": "composed_career_route_v0_9a",
        "family": "career_route",
        "subtype": "public_voice",
        "source_type": "composed_semantic",
        "chart_facts_match": True,
        "domain_reason": ["MC route", "MC ruler involved", "10H planet"],
        "technical_anchors": ["MC Gemini", "Mercury 10H"],
        "public_job": "debug_only",
        "public_eligibility": {
            "debug_eligible": True,
            "detail_eligible": True,
            "public_support_eligible": False,
            "public_main_eligible": False,
        },
        "evidence_trace": {
            "primitive_facts": {
                "placements": [],
                "angles": [{"angle": "MC", "sign": "Gemini"}],
            },
        },
    }
    placements_by_variant = {
        "fix04": [
            {"planet": "Mercury", "sign": "Cancer", "house": 10},
            {"planet": "Mars", "sign": "Cancer", "house": 10},
        ],
        "tokyo": [
            {"planet": "Mercury", "sign": "Cancer", "house": 10},
            {"planet": "Sun", "sign": "Gemini", "house": 10},
        ],
        "toronto": [
            {"planet": "Mercury", "sign": "Gemini", "house": 10},
            {"planet": "Sun", "sign": "Cancer", "house": 10},
            {"planet": "Moon", "sign": "Gemini", "house": 10},
            {"planet": "Venus", "sign": "Cancer", "house": 10},
        ],
    }
    base["evidence_trace"]["primitive_facts"]["placements"] = placements_by_variant[variant]
    return base


_PUBLIC_TEXT_FIELDS = ("headline", "teaser", "body")
_REQUIRED_TURKISH_DIACRITICS_BY_VARIANT = {
    "fix04": ("İnsanlar", "Dışarıdaki", "nasıl", "söylediğini", "Söz", "Görünür", "güç", "doğru"),
    "tokyo": ("Dışarıdaki", "cümleyle", "söylediğin", "İfade", "doğru", "yön"),
    "toronto": ("Görünür", "söz", "Dış", "cümleyi", "çerçevelediğinde", "ağırlığın", "doğru"),
}
_BANNED_ASCII_TURKISH = (
    "Insanlar",
    "Disaridaki",
    "nasil",
    "soyledigini",
    "Soz",
    "Gorunur",
    "guc",
    "dogru",
    "cumle",
    "cercevelediginde",
    "agirligin",
    "Ifade",
)


def test_render_composed_detail_card_v0_9a_2_flag_off_returns_none(monkeypatch) -> None:
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", raising=False)
    assert render_composed_detail_card_v0_9a_2(_candidate(variant="fix04")) is None


def test_render_composed_detail_card_v0_9a_2_renders_supported_variants(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    for variant in ("fix04", "tokyo", "toronto"):
        card = render_composed_detail_card_v0_9a_2(_candidate(variant=variant))
        assert card is not None
        assert card["source_type"] == "composed_semantic"
        assert card["source_candidate_id"] == "composed_career_route_v0_9a"
        assert card["public_job"] == "detail_only"
        body = str(card["body"]).lower()
        for banned in ("mc, yöneticisi", "mc route", "10h", "source_type", "debug", "candidate", "fallback"):
            assert banned not in body


def test_render_composed_detail_card_v0_9a_2_rejects_non_target_signature(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    candidate = copy.deepcopy(_candidate(variant="fix04"))
    candidate["evidence_trace"]["primitive_facts"]["placements"] = [
        {"planet": "Mercury", "sign": "Cancer", "house": 10},
    ]
    assert render_composed_detail_card_v0_9a_2(candidate) is None


def test_render_composed_detail_card_v0_9a_2_public_fields_contain_turkish_diacritics(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    for variant in ("fix04", "tokyo", "toronto"):
        card = render_composed_detail_card_v0_9a_2(_candidate(variant=variant))
        assert card is not None
        combined_public_text = " ".join(str(card[field]) for field in _PUBLIC_TEXT_FIELDS)
        combined_public_text += " " + " ".join(str(chip) for chip in card["chips"])
        for required in _REQUIRED_TURKISH_DIACRITICS_BY_VARIANT[variant]:
            assert required in combined_public_text, (
                f"variant={variant} missing required Turkish form {required!r} in public copy"
            )


def test_render_composed_detail_card_v0_9a_2_public_fields_have_no_ascii_turkish_variants(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    import re

    for variant in ("fix04", "tokyo", "toronto"):
        card = render_composed_detail_card_v0_9a_2(_candidate(variant=variant))
        assert card is not None
        public_texts = [str(card[field]) for field in _PUBLIC_TEXT_FIELDS]
        public_texts.extend(str(chip) for chip in card["chips"])
        for text in public_texts:
            for banned in _BANNED_ASCII_TURKISH:
                pattern = re.compile(rf"\b{re.escape(banned)}\b")
                assert not pattern.search(text), (
                    f"variant={variant} ASCII Turkish residue {banned!r} found in public field: {text!r}"
                )


def test_render_composed_detail_card_v0_9a_2_preserves_traceability_fields(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    for variant in ("fix04", "tokyo", "toronto"):
        candidate = _candidate(variant=variant)
        card = render_composed_detail_card_v0_9a_2(candidate)
        assert card is not None
        assert card["source_type"] == "composed_semantic"
        assert card["source_candidate_id"] == candidate["id"]
        trace = card["source_anchor_trace"]
        assert trace["family"] == "career_route"
        assert trace["subtype"] == "public_voice"
        assert trace["domain_reason"] == candidate["domain_reason"]
        assert trace["technical_anchors"] == candidate["technical_anchors"]


# ---------------------------------------------------------------------------
# v0.9a.3 Phase B — public detail lane promotion
# ---------------------------------------------------------------------------


_PUBLIC_VISIBLE_FIELDS = {
    "id",
    "node_id",
    "headline",
    "teaser",
    "body",
    "chips",
    "family",
    "emphasis",
    "origin",
}

_TRACE_ONLY_FIELDS = {
    "source_type",
    "source_candidate_id",
    "public_job",
    "source_anchor_trace",
    "detail_items",
    "evidence_summary",
}


def _relationship_hidden_private_love_source(*, source_kind: str) -> dict:
    base = {
        "id": (
            "composed_relationship_route_v0_9b"
            if source_kind == "composed_semantic"
            else "venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact"
        ),
        "family": "relationship_route" if source_kind == "composed_semantic" else "",
        "subtype": "hidden_private_love" if source_kind == "composed_semantic" else "",
        "source_type": "composed_semantic" if source_kind == "composed_semantic" else "chart_exact",
        "chart_facts_match": True,
        "domain_reason": ["12H hidden-love signature"],
        "technical_anchors": ["Venüs 12. ev", "Yay", "relationship_hidden_private_love_pattern"],
        "public_eligibility": {
            "debug_eligible": True,
            "detail_eligible": True,
            "public_support_eligible": False,
            "public_main_eligible": False,
        },
        "evidence_trace": {
            "primitive_facts": {
                "placements": [
                    {"planet": "Venus", "sign": "Sagittarius", "house": 12},
                    {"planet": "Moon", "sign": "Leo", "house": 8},
                    {"planet": "Sun", "sign": "Capricorn", "house": 1},
                    {"planet": "Mercury", "sign": "Capricorn", "house": 1},
                ],
                "angles": [
                    {"angle": "ASC", "sign": "Capricorn"},
                    {"angle": "MC", "sign": "Libra"},
                ],
            },
        },
        "meta": {},
    }
    return base


def _rendered_cards_for_all_variants(monkeypatch) -> list[dict]:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    cards: list[dict] = []
    for variant in ("fix04", "tokyo", "toronto"):
        card = render_composed_detail_card_v0_9a_2(_candidate(variant=variant))
        assert card is not None
        cards.append(card)
    return cards


def test_project_public_lane_flag_off_returns_empty(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", raising=False)
    cards = _rendered_cards_for_all_variants(monkeypatch)
    assert project_composed_detail_cards_to_public_lane(cards) == []


def test_project_public_lane_render_off_returns_empty(monkeypatch) -> None:
    cards = _rendered_cards_for_all_variants(monkeypatch)
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", raising=False)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")
    assert project_composed_detail_cards_to_public_lane(cards) == []


def test_project_public_lane_both_on_promotes_target_cards(monkeypatch) -> None:
    cards = _rendered_cards_for_all_variants(monkeypatch)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")
    promoted = project_composed_detail_cards_to_public_lane(cards)
    assert len(promoted) == 3


def test_project_public_lane_strips_trace_fields(monkeypatch) -> None:
    cards = _rendered_cards_for_all_variants(monkeypatch)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")
    promoted = project_composed_detail_cards_to_public_lane(cards)
    assert promoted
    for visible in promoted:
        keys = set(visible.keys())
        assert keys <= _PUBLIC_VISIBLE_FIELDS, f"unexpected fields in public lane card: {keys - _PUBLIC_VISIBLE_FIELDS}"
        assert not (keys & _TRACE_ONLY_FIELDS), (
            f"trace-only fields leaked into public lane card: {keys & _TRACE_ONLY_FIELDS}"
        )


def test_project_public_lane_rejects_non_allowlisted_variants(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")
    forged = {
        "id": "composed_detail::composed_career_route_v0_9a::not_in_allowlist",
        "node_id": "promise::composed_career_route_v0_9a",
        "headline": "İnsanlar sende sadece ne yaptığını değil, nasıl söylediğini de fark ediyor.",
        "teaser": "Dışarıdaki etkin çoğu zaman sözünün tonu ve kurduğun pozisyonla güçleniyor.",
        "body": (
            "Bir işi yalnız tamamlaman değil, onu nasıl anlattığın da sende görünür rolün parçası oluyor. "
            "İnsanlar çoğu zaman önce fikrinin tonunu, sonra o tonun yarattığı etkiyi fark edebilir. "
            "Buradaki güç, sesini daha yüksek kullanmakta değil; doğru yerde netleştiğinde dışarıdaki rolün zaten belirginleşmesinde yatıyor."
        ),
        "chips": ["Kariyer", "Söz", "Görünür rol"],
        "family": "career_public_voice",
        "emphasis": "detail",
        "origin": "composed_detail_renderer_v0_9a_2",
    }
    assert project_composed_detail_cards_to_public_lane([forged]) == []


def test_project_public_lane_empty_input_returns_empty(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")
    assert project_composed_detail_cards_to_public_lane([]) == []
    assert project_composed_detail_cards_to_public_lane(None) == []


def test_project_public_lane_copy_quality_preserved(monkeypatch) -> None:
    cards = _rendered_cards_for_all_variants(monkeypatch)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")
    promoted = project_composed_detail_cards_to_public_lane(cards)
    import re

    banned_ascii = ("Insanlar", "Disaridaki", "nasil", "dogru", "Gorunur", "Soz", "Ifade")
    for visible in promoted:
        for text in (visible["headline"], visible["teaser"], visible["body"]):
            for banned in banned_ascii:
                assert not re.search(rf"\b{re.escape(banned)}\b", text), text
        # Each card must carry at least one diacritic somewhere in the visible
        # public copy — sanity check that promotion did not down-fold text.
        combined = " ".join((visible["headline"], visible["teaser"], visible["body"]))
        assert any(c in combined for c in "İıŞşĞğÇçÖöÜü"), combined


def test_render_relationship_hidden_private_love_card_v0_10_phase2_flag_off_returns_none(monkeypatch) -> None:
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", raising=False)
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", raising=False)
    monkeypatch.delenv(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_PUBLIC_DETAIL_LANE",
        raising=False,
    )
    source = _relationship_hidden_private_love_source(source_kind="composed_semantic")
    assert render_relationship_hidden_private_love_card_v0_10_phase2(
        source, source_kind="composed_semantic"
    ) is None


def test_render_relationship_hidden_private_love_card_v0_10_phase2_accepts_composed_and_exact_sources(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT", "true")
    monkeypatch.setenv(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_PUBLIC_DETAIL_LANE",
        "true",
    )
    composed = _relationship_hidden_private_love_source(source_kind="composed_semantic")
    exact = _relationship_hidden_private_love_source(source_kind="exact_owner")

    rendered_composed = render_relationship_hidden_private_love_card_v0_10_phase2(
        composed, source_kind="composed_semantic"
    )
    rendered_exact = render_relationship_hidden_private_love_card_v0_10_phase2(
        exact, source_kind="exact_owner"
    )

    assert rendered_composed is not None
    assert rendered_exact is not None
    assert (
        rendered_composed["slides"][0]["id"]
        == "slide::composed_relationship_route_v0_9b::private_scene"
    )
    assert (
        rendered_exact["slides"][0]["id"]
        == "slide::venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact::private_scene"
    )
    assert rendered_composed["slides"][0]["title"] == "Hemen göstermiyorsun"
    assert (
        rendered_composed["slides"][0]["body"]
        == "Birine karşı bir şey hissettiğinde, bunu hemen dışarıya açmak istemeyebilirsin. Önce kendi içinde anlamak, emin olmak ve biraz da korumak istersin. Bu yüzden dışarıdan sakin ya da mesafeli görünebilirsin. Ama bu, az hissettiğin anlamına gelmez; sadece duygularını herkes gibi açık yaşamıyorsun."
    )
    assert len(rendered_composed["slides"]) == 5
    assert all(set(slide.keys()) == {"id", "title", "body"} for slide in rendered_composed["slides"])
    assert rendered_composed["why_this_exists"]["title"] == "Nereden geliyor?"
    assert rendered_exact["source_candidate_id"] == "venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact"


def test_render_relationship_hidden_private_love_card_v0_10_phase2_rejects_non_target_signature(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT", "true")
    monkeypatch.setenv(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_PUBLIC_DETAIL_LANE",
        "true",
    )
    source = _relationship_hidden_private_love_source(source_kind="composed_semantic")
    source["evidence_trace"]["primitive_facts"]["placements"][1] = {
        "planet": "Moon",
        "sign": "Libra",
        "house": 10,
    }
    assert render_relationship_hidden_private_love_card_v0_10_phase2(
        source, source_kind="composed_semantic"
    ) is None


def test_project_relationship_hidden_private_love_to_public_lane_promotes_one_public_card(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")
    monkeypatch.setenv(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_PUBLIC_DETAIL_LANE",
        "true",
    )
    exact = _relationship_hidden_private_love_source(source_kind="exact_owner")
    promoted = project_relationship_hidden_private_love_to_public_lane(
        [exact],
        cluster_payload={
            "surface_plan": {"detail_cluster_ids": ["relationship_hidden_private_love_pattern"]},
            "clusters": [
                {
                    "id": "relationship_hidden_private_love_pattern",
                    "main_packet_id": "venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact",
                }
            ],
        },
    )
    assert len(promoted) == 1
    card = promoted[0]
    assert set(card.keys()) == {
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
    }
    assert len(card["slides"]) == 5
    assert all(set(slide.keys()) == {"id", "title", "body"} for slide in card["slides"])
    assert (
        card["slides"][0]["id"]
        == "slide::venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact::private_scene"
    )


def test_project_relationship_hidden_private_love_to_public_lane_cluster_fallback_uses_composed_candidate(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT", "true")
    monkeypatch.setenv(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_PUBLIC_DETAIL_LANE",
        "true",
    )
    composed = _relationship_hidden_private_love_source(source_kind="composed_semantic")
    promoted = project_relationship_hidden_private_love_to_public_lane(
        [composed],
        cluster_payload={
            "surface_plan": {"detail_cluster_ids": ["relationship_hidden_private_love_pattern"]},
            "clusters": [
                {
                    "id": "relationship_hidden_private_love_pattern",
                    "main_packet_id": "venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact",
                }
            ],
        },
    )
    assert len(promoted) == 1
    card = promoted[0]
    assert card["id"] == "composed_detail::composed_relationship_route_v0_9b::istanbul_1996_12_28_hidden_private_love"
    assert (
        card["slides"][0]["id"]
        == "slide::composed_relationship_route_v0_9b::private_scene"
    )


def test_project_relationship_hidden_private_love_to_public_lane_exact_owner_precedence_wins_over_cluster_fallback(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT", "true")
    monkeypatch.setenv(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_PUBLIC_DETAIL_LANE",
        "true",
    )
    exact = _relationship_hidden_private_love_source(source_kind="exact_owner")
    composed = _relationship_hidden_private_love_source(source_kind="composed_semantic")
    promoted = project_relationship_hidden_private_love_to_public_lane(
        [composed, exact],
        cluster_payload={
            "surface_plan": {"detail_cluster_ids": ["relationship_hidden_private_love_pattern"]},
            "clusters": [
                {
                    "id": "relationship_hidden_private_love_pattern",
                    "main_packet_id": "venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact",
                }
            ],
        },
    )
    assert len(promoted) == 1
    card = promoted[0]
    assert (
        card["id"]
        == "composed_detail::venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact::istanbul_1996_12_28_hidden_private_love"
    )


# ---------------------------------------------------------------------------
# v0.9b.1 — moon_signature.home_inner_security narrow detail rollout
# ---------------------------------------------------------------------------

from app.meaning.composed_detail_renderer import (  # noqa: E402
    render_moon_home_inner_security_card_v0_9b_1,
    moon_home_inner_security_public_detail_lane_enabled,
    project_moon_home_inner_security_to_public_lane,
)


_V0_9B_1_VARIANT_PRIMITIVE_FACTS = {
    "trabzon": {
        "placements": [
            {"planet": "Moon", "sign": "leo", "house": 4},
            {"planet": "Sun", "sign": "Virgo", "house": 5},
            {"planet": "Venus", "sign": "Leo", "house": 4},
        ],
        "angles": [{"angle": "IC", "sign": "Leo"}],
    },
    "fix08": {
        "placements": [
            {"planet": "Moon", "sign": "libra", "house": 4},
            {"planet": "Venus", "sign": "Capricorn", "house": 7},
        ],
        "angles": [{"angle": "IC", "sign": "Libra"}],
    },
    "cairo": {
        "placements": [
            {"planet": "Moon", "sign": "capricorn", "house": 4},
            {"planet": "Saturn", "sign": "Capricorn", "house": 4},
            {"planet": "Sun", "sign": "Capricorn", "house": 4},
        ],
        "angles": [{"angle": "IC", "sign": "Capricorn"}],
    },
}


def _v0_9b_1_candidate(*, variant_key: str, confidence: float = 0.85, **overrides) -> dict:
    facts = _V0_9B_1_VARIANT_PRIMITIVE_FACTS[variant_key]
    base = {
        "id": "composed_moon_signature_v0_9b",
        "family": "moon_signature",
        "subtype": "home_inner_security",
        "source_type": "composed_semantic",
        "chart_facts_match": True,
        "confidence": confidence,
        "domain_reason": [
            "Moon need signature",
            "Moon house scene",
            "Moon ruler route",
            "IC/4H reinforcement",
        ],
        "technical_anchors": ["Moon · 4. ev"],
        "public_eligibility": {
            "debug_eligible": True,
            "detail_eligible": True,
            "public_support_eligible": False,
            "public_main_eligible": False,
        },
        "meta": {
            "subtype_default_fallback": False,
            "moon_evidence_owned_by": "moon_signature",
        },
        "evidence_trace": {
            "primitive_facts": dict(facts),
            "discovery_routes": ["moon_signature"],
            "subtype_inputs": ["home_inner_security"],
            "cross_family_overlap": [],
        },
    }
    base.update(overrides)
    return base


def _set_all_v0_9b_1_flags_on(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")
    monkeypatch.setenv(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_HOME_INNER_SECURITY_PUBLIC_DETAIL_LANE",
        "true",
    )


def test_v0_9b_1_render_moon_home_inner_security_lane_flag_off_returns_none(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")
    monkeypatch.delenv(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_HOME_INNER_SECURITY_PUBLIC_DETAIL_LANE",
        raising=False,
    )
    assert render_moon_home_inner_security_card_v0_9b_1(_v0_9b_1_candidate(variant_key="trabzon")) is None


def test_v0_9b_1_render_render_detail_flag_off_returns_none(monkeypatch) -> None:
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", raising=False)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")
    monkeypatch.setenv(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_HOME_INNER_SECURITY_PUBLIC_DETAIL_LANE",
        "true",
    )
    assert render_moon_home_inner_security_card_v0_9b_1(_v0_9b_1_candidate(variant_key="trabzon")) is None


def test_v0_9b_1_render_public_detail_lane_flag_off_returns_none(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", raising=False)
    monkeypatch.setenv(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_HOME_INNER_SECURITY_PUBLIC_DETAIL_LANE",
        "true",
    )
    assert render_moon_home_inner_security_card_v0_9b_1(_v0_9b_1_candidate(variant_key="trabzon")) is None


def test_v0_9b_1_renders_each_target_variant(monkeypatch) -> None:
    _set_all_v0_9b_1_flags_on(monkeypatch)
    confidences = {"trabzon": 0.88, "fix08": 0.85, "cairo": 0.81}
    expected_variant_ids = {
        "trabzon": "trabzon_2001_09_14_moon_home_inner_security",
        "fix08": "fix08_cancer_capricorn_nodes_moon_home_inner_security",
        "cairo": "cairo_1991_01_15_moon_home_inner_security",
    }
    for key in ("trabzon", "fix08", "cairo"):
        candidate = _v0_9b_1_candidate(variant_key=key, confidence=confidences[key])
        card = render_moon_home_inner_security_card_v0_9b_1(candidate)
        assert card is not None, key
        assert card["id"].endswith(expected_variant_ids[key]), card["id"]
        assert card["family"] == "moon_home_inner_security"
        assert card["origin"] == "composed_detail_renderer_v0_9b_1"


def test_v0_9b_1_rejects_below_confidence_threshold(monkeypatch) -> None:
    _set_all_v0_9b_1_flags_on(monkeypatch)
    assert render_moon_home_inner_security_card_v0_9b_1(
        _v0_9b_1_candidate(variant_key="trabzon", confidence=0.79)
    ) is None
    assert render_moon_home_inner_security_card_v0_9b_1(
        _v0_9b_1_candidate(variant_key="trabzon", confidence=0.80)
    ) is not None


def test_v0_9b_1_rejects_default_fallback_subtype(monkeypatch) -> None:
    _set_all_v0_9b_1_flags_on(monkeypatch)
    cand = _v0_9b_1_candidate(variant_key="trabzon")
    cand["meta"] = dict(cand["meta"])
    cand["meta"]["subtype_default_fallback"] = True
    assert render_moon_home_inner_security_card_v0_9b_1(cand) is None


def test_v0_9b_1_rejects_chart_facts_mismatch(monkeypatch) -> None:
    _set_all_v0_9b_1_flags_on(monkeypatch)
    cand = _v0_9b_1_candidate(variant_key="trabzon")
    cand["chart_facts_match"] = False
    assert render_moon_home_inner_security_card_v0_9b_1(cand) is None


def test_v0_9b_1_rejects_non_target_signature(monkeypatch) -> None:
    _set_all_v0_9b_1_flags_on(monkeypatch)
    cand = _v0_9b_1_candidate(variant_key="trabzon")
    cand["evidence_trace"] = {
        "primitive_facts": {
            "placements": [{"planet": "Moon", "sign": "scorpio", "house": 8}],
            "angles": [{"angle": "IC", "sign": "Cancer"}],
        }
    }
    assert render_moon_home_inner_security_card_v0_9b_1(cand) is None


def test_v0_9b_1_rejects_public_main_eligible(monkeypatch) -> None:
    _set_all_v0_9b_1_flags_on(monkeypatch)
    cand = _v0_9b_1_candidate(variant_key="trabzon")
    cand["public_eligibility"] = dict(cand["public_eligibility"])
    cand["public_eligibility"]["public_main_eligible"] = True
    assert render_moon_home_inner_security_card_v0_9b_1(cand) is None


def test_v0_9b_1_rejects_public_support_eligible(monkeypatch) -> None:
    _set_all_v0_9b_1_flags_on(monkeypatch)
    cand = _v0_9b_1_candidate(variant_key="trabzon")
    cand["public_eligibility"] = dict(cand["public_eligibility"])
    cand["public_eligibility"]["public_support_eligible"] = True
    assert render_moon_home_inner_security_card_v0_9b_1(cand) is None


def test_v0_9b_1_rejects_detail_eligible_false(monkeypatch) -> None:
    _set_all_v0_9b_1_flags_on(monkeypatch)
    cand = _v0_9b_1_candidate(variant_key="trabzon")
    cand["public_eligibility"] = dict(cand["public_eligibility"])
    cand["public_eligibility"]["detail_eligible"] = False
    assert render_moon_home_inner_security_card_v0_9b_1(cand) is None


def test_v0_9b_1_card_has_only_public_visible_fields_after_promotion(monkeypatch) -> None:
    _set_all_v0_9b_1_flags_on(monkeypatch)
    promoted = project_moon_home_inner_security_to_public_lane(
        [_v0_9b_1_candidate(variant_key="trabzon")]
    )
    assert len(promoted) == 1
    keys = set(promoted[0].keys())
    expected = {
        "id", "node_id", "headline", "teaser", "body", "chips",
        "family", "emphasis", "origin",
    }
    assert keys <= expected
    forbidden = {
        "source_type", "source_candidate_id", "public_job",
        "source_anchor_trace", "detail_items", "evidence_summary",
        "avoid_readings",
    }
    assert not (keys & forbidden)


def test_v0_9b_1_card_copy_passes_semantic_direction(monkeypatch) -> None:
    _set_all_v0_9b_1_flags_on(monkeypatch)
    for key in ("trabzon", "fix08", "cairo"):
        card = render_moon_home_inner_security_card_v0_9b_1(
            _v0_9b_1_candidate(variant_key=key)
        )
        assert card is not None, key
        combined = " ".join(str(card[f]) for f in ("headline", "teaser", "body"))
        # Banned generic-family phrases must not appear.
        for banned in (
            "Aile önemlidir", "aile önemlidir",
            "Ev hayatın güçlüdür", "ev hayatın güçlüdür",
            "Annenle ilişkin", "Babanla ilişkin",
            "Ailen senin için her şey", "kalbinde yer eden aile",
        ):
            assert banned not in combined, (key, banned)
        # At least one safety / inner-base vocabulary token present.
        required = (
            "iç güven", "duygusal güvenl", "duygusal zemin", "iç zemin",
            "kök", "ait ol", "düzenle", "sakinleş", "toparla",
        )
        assert any(token in combined.lower() for token in required), (key, combined)
        # Turkish diacritics present.
        assert any(c in combined for c in "İıŞşĞğÇçÖöÜü"), key


def test_v0_9b_1_card_copy_has_no_p0_truthfulness_defects(monkeypatch) -> None:
    _set_all_v0_9b_1_flags_on(monkeypatch)
    import re as _re
    for key in ("trabzon", "fix08", "cairo"):
        card = render_moon_home_inner_security_card_v0_9b_1(
            _v0_9b_1_candidate(variant_key=key)
        )
        assert card is not None, key
        for field in ("headline", "teaser", "body"):
            text = str(card[field])
            assert not _re.search(r"olması de\b", text), (key, field, text)
            assert "Bazen de." not in text, (key, field, text)
            assert "bazen de." not in text, (key, field, text)
