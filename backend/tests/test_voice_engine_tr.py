from app.transit.narrative.deep_archetype_engine import build_active_event_cards, build_event_card
from app.transit.narrative.text_quality_tr import _dedupe_section_overlap


def _natal_snapshot() -> dict:
    return {
        "bodies": [
            {"body": "Sun", "lon": 276.75, "sign": "Capricorn", "house": 1},
            {"body": "Moon", "lon": 133.94, "sign": "Leo", "house": 8},
            {"body": "Mercury", "lon": 287.36, "sign": "Capricorn", "house": 1, "rx": True},
            {"body": "Venus", "lon": 253.71, "sign": "Sagittarius", "house": 12},
            {"body": "Mars", "lon": 177.93, "sign": "Virgo", "house": 9},
            {"body": "Jupiter", "lon": 294.29, "sign": "Capricorn", "house": 1},
            {"body": "Saturn", "lon": 1.15, "sign": "Aries", "house": 3},
            {"body": "Uranus", "lon": 303.06, "sign": "Aquarius", "house": 1},
            {"body": "Neptune", "lon": 296.69, "sign": "Capricorn", "house": 1},
            {"body": "Pluto", "lon": 244.25, "sign": "Sagittarius", "house": 11},
        ],
        "angles": {
            "ASC": {"point": "ASC", "sign": "Capricorn"},
            "MC": {"point": "MC", "sign": "Libra"},
            "DSC": {"point": "DSC", "sign": "Cancer"},
            "IC": {"point": "IC", "sign": "Aries"},
        },
        "house_cusps": [
            {"house": 1, "sign": "Capricorn"},
            {"house": 2, "sign": "Aquarius"},
            {"house": 3, "sign": "Pisces"},
            {"house": 4, "sign": "Aries"},
            {"house": 5, "sign": "Taurus"},
            {"house": 6, "sign": "Gemini"},
            {"house": 7, "sign": "Cancer"},
            {"house": 8, "sign": "Leo"},
            {"house": 9, "sign": "Virgo"},
            {"house": 10, "sign": "Libra"},
            {"house": 11, "sign": "Scorpio"},
            {"house": 12, "sign": "Sagittarius"},
        ],
    }


def _event_neptune_square_dsc() -> dict:
    return {
        "event_id": "evt_neptune_dsc",
        "transit_body": "Neptune",
        "natal_point": "DSC",
        "aspect": "square",
        "phase": "applying",
        "bucket": "long",
        "orb_deg": 0.9,
        "houses": {"transit_in_natal_house": 3},
        "domains": ["relationships"],
        "ranking": {"tier": "main", "weight": 1.2},
        "interpretation": {"headline": "Uzun soluklu ayar"},
    }


def _event_uranus_trine_mars() -> dict:
    return {
        "event_id": "evt_uranus_mars",
        "transit_body": "Uranus",
        "natal_point": "Mars",
        "aspect": "trine",
        "phase": "applying",
        "bucket": "long",
        "orb_deg": 0.8,
        "houses": {"transit_in_natal_house": 9},
        "domains": ["mind"],
        "ranking": {"tier": "main", "weight": 1.3},
        "interpretation": {
            "headline": "Uzun soluklu ayar",
            "watch": ["south node gerilimi"],
        },
    }


def test_title_not_generic() -> None:
    card = build_event_card(_event_neptune_square_dsc(), context={"natal": _natal_snapshot()})
    assert card["title"] != "Uzun soluklu ayar"


def test_rulership_houses_in_copy() -> None:
    card = build_event_card(_event_uranus_trine_mars(), context={"natal": _natal_snapshot()})
    merged = f"{card.get('conflict','')} {card.get('upper','')}".lower()
    assert any(token in merged for token in ("4.", "11.", "ev/kok", "topluluk/hedef"))


def test_no_blocked_tokens_in_public_copy() -> None:
    card = build_event_card(_event_uranus_trine_mars(), context={"natal": _natal_snapshot()})
    merged = " ".join([card.get("conflict", ""), card.get("shadow", ""), card.get("upper", "")]).lower()
    for banned in ("south node", "north node", "lilith", "vertex", "fortune", "chiron"):
        assert banned not in merged


def test_angle_event_lead_is_not_ruler_lead() -> None:
    event = {
        "event_id": "evt_neptune_asc",
        "transit_body": "Neptune",
        "natal_point": "ASC",
        "aspect": "square",
        "phase": "applying",
        "bucket": "long",
        "orb_deg": 0.9,
        "houses": {"transit_in_natal_house": 3},
        "domains": ["identity"],
        "ranking": {"tier": "main", "weight": 1.2},
        "interpretation": {"headline": "Uzun soluklu ayar"},
    }
    card = build_event_card(event, context={"natal": _natal_snapshot()})
    merged = " ".join(
        [
            str(card.get("title") or ""),
            str(card.get("teaser") or ""),
            str(card.get("conflict") or ""),
            str(card.get("why_now") or ""),
            str(card.get("shadow") or ""),
            str(card.get("upper") or ""),
        ]
    )
    assert "Yükselen" in merged
    assert "yöneticisi Satürn" in merged
    assert "3. ev" in merged
    assert "iletişim ritminde başlar; sonra duruşuna/kimliğine yansır." in str(card.get("mechanism") or "")
    assert str(card.get("headline") or "").strip() != str(card.get("big_picture") or "").strip()
    for banned in ("orb", "phase", "bucket", "Sahne", "vurduğu yer", "exact", "applying", "separating", "period"):
        assert banned.lower() not in merged.lower()


def test_bullets_have_quality_rules() -> None:
    card = build_event_card(_event_uranus_trine_mars(), context={"natal": _natal_snapshot()})
    guidance = card.get("guidance") if isinstance(card.get("guidance"), list) else []
    watch_out = card.get("watch_out") if isinstance(card.get("watch_out"), list) else []
    assert len(guidance) >= 2
    assert len(watch_out) >= 2
    all_items = [str(x) for x in guidance + watch_out]
    assert all(item.strip() for item in all_items)
    assert all("Netleştir:" not in item for item in all_items)
    for item in all_items:
        assert len(item.split()) <= 14


def test_upper_repetition_not_globally_copied() -> None:
    base = _event_uranus_trine_mars()
    items = []
    variants = [
        ("evt1", "Uranus", "trine", "Mars", 9),
        ("evt2", "Neptune", "square", "ASC", 3),
        ("evt3", "Saturn", "opposition", "DSC", 7),
        ("evt4", "Jupiter", "sextile", "Mercury", 3),
        ("evt5", "Mars", "conjunction", "MC", 10),
    ]
    for event_id, body, aspect, natal_point, house in variants:
        item = dict(base)
        item["event_id"] = event_id
        item["transit_body"] = body
        item["aspect"] = aspect
        item["natal_point"] = natal_point
        item["houses"] = {"transit_in_natal_house": house}
        items.append(item)
    report = {"display": {"items": items}, "natal": _natal_snapshot()}
    cards = build_active_event_cards(report, max_cards=5)
    merged = " ".join(str(card.get("upper") or "") for card in cards)
    assert merged.count("Çerçeveyi net kurduğunda") <= 1


def test_guidance_watch_frequency_cap_across_cards() -> None:
    base = _event_uranus_trine_mars()
    events = []
    variants = [
        ("evt_a", "Uranus", "trine", "Mars", 9),
        ("evt_b", "Neptune", "square", "ASC", 3),
        ("evt_c", "Saturn", "opposition", "DSC", 7),
        ("evt_d", "Pluto", "conjunction", "MC", 10),
        ("evt_e", "Jupiter", "sextile", "Mercury", 11),
    ]
    for event_id, body, aspect, natal_point, house in variants:
        item = dict(base)
        item["event_id"] = event_id
        item["transit_body"] = body
        item["aspect"] = aspect
        item["natal_point"] = natal_point
        item["strength"] = 0.9
        item["houses"] = {"transit_in_natal_house": house, "natal_point_house": house}
        events.append(item)
    report = {"display": {"items": events}, "natal": _natal_snapshot()}
    cards = build_active_event_cards(report, max_cards=5)
    assert len(cards) == 5
    all_guidance = [str(line) for card in cards for line in (card.get("guidance") or [])]
    all_watch = [str(line) for card in cards for line in (card.get("watch_out") or [])]
    assert len(all_guidance) == len(set(x.lower() for x in all_guidance))
    assert len(all_watch) == len(set(x.lower() for x in all_watch))


def test_house_specific_guidance_keywords_for_house_3_and_9() -> None:
    event_9 = _event_uranus_trine_mars()
    event_9["strength"] = 0.9
    event_9["houses"] = {"transit_in_natal_house": 5, "natal_point_house": 9}
    event_3 = _event_neptune_square_dsc()
    event_3["event_id"] = "evt_neptune_asc_3"
    event_3["natal_point"] = "ASC"
    event_3["strength"] = 0.9
    event_3["houses"] = {"transit_in_natal_house": 3, "natal_point_house": 3}

    report = {"display": {"items": [event_9, event_3]}, "natal": _natal_snapshot()}
    cards = build_active_event_cards(report, max_cards=2)
    assert len(cards) == 2
    by_id = {card["event_id"]: card for card in cards}

    merged_9 = " ".join(str(x) for x in by_id[event_9["event_id"]].get("guidance", [])).lower()
    assert any(token in merged_9 for token in ("sprint", "öğren", "yayın", "roadmap"))

    merged_3 = " ".join(str(x) for x in by_id[event_3["event_id"]].get("guidance", [])).lower()
    assert any(token in merged_3 for token in ("özet", "soru", "taslak", "yazılı"))


def test_neptune_square_asc_links_to_neptune_saturn_cofeatured() -> None:
    neptune_asc = {
        "event_id": "evt_neptune_asc",
        "transit_body": "Neptune",
        "natal_point": "ASC",
        "aspect": "square",
        "phase": "applying",
        "bucket": "long",
        "orb_deg": 0.17,
        "houses": {"transit_in_natal_house": 3, "natal_point_house": 1},
        "domains": ["identity"],
        "ranking": {"tier": "main", "weight": 1.3},
    }
    neptune_saturn = {
        "event_id": "evt_neptune_saturn",
        "transit_body": "Neptune",
        "natal_point": "Saturn",
        "aspect": "conjunction",
        "phase": "applying",
        "bucket": "long",
        "orb_deg": 0.14,
        "houses": {"transit_in_natal_house": 3, "natal_point_house": 3},
        "domains": ["mind"],
        "ranking": {"tier": "main", "weight": 1.28},
    }
    report = {"display": {"items": [neptune_asc, neptune_saturn]}, "natal": _natal_snapshot()}
    cards = build_active_event_cards(report, max_cards=2)
    by_id = {str(card.get("event_id")): card for card in cards}
    links = (by_id["evt_neptune_asc"].get("derived_context") or {}).get("links") or []
    assert any(
        isinstance(link, dict)
        and link.get("type") == "cofeatured_hit"
        and link.get("target_event_id") == "evt_neptune_saturn"
        and link.get("because") == "same transit hits ASC and ASC ruler"
        for link in links
    )


def test_dedupe_headline_vs_big_picture_similarity_below_threshold() -> None:
    card = {
        "headline": "Bu dönem dilini kalibre etmen gerekiyor ve netleşme alanı açılıyor.",
        "big_picture": "Bu dönem dilini kalibre etmen gerekiyor ve netleşme alanı açılıyor.",
        "mechanism": "Sahne 3. Ev; vurduğu yer 1. Ev. Etki iletişim ritminde başlar; sonra duruşuna yansır.",
        "upper": "Nazik ama net sınır koy.",
    }
    out = _dedupe_section_overlap(card)
    headline = str(out.get("headline") or "")
    big_picture = str(out.get("big_picture") or "")
    mechanism = str(out.get("mechanism") or "")
    assert "sahne" not in mechanism.lower()
    assert "vurduğu yer" not in mechanism.lower()
    if big_picture:
        import difflib

        ratio = difflib.SequenceMatcher(None, headline.lower(), big_picture.lower()).ratio()
        assert ratio < 0.8
