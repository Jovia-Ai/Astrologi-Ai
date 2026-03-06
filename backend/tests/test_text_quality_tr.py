import hashlib

from app.transit.narrative.text_quality_tr import (
    apply_copy_quality_layer,
    build_root_causes,
    build_period_copy,
    normalize_card_text_tr,
    polish_collocations,
    select_path_motifs,
    tr_normalize,
)


def _sample_card() -> dict:
    return {
        "event_id": "evt_1",
        "title": "capricorn stili iletisim",
        "signature": "Transit Neptune (3. Ev) □ Natal Mercury • exact • weeks",
        "conflict": "south node ile ilgili gerilim, 3 evde iletisim baskisi",
        "shadow": "north node etiketi ve neptune disiplini birlikte akiyor",
        "upper": "3 evde duzen kur",
        "extra_line": "hizli tepki yerine netlik",
        "time_hint": "yaklasiyor",
        "guidance": [
            "mesaji hemen atma",
            "yaziyi kisalt",
            "yakın çevre ile teyit al",
        ],
        "watch_out": ["south node etiketi ile sertlesme", "acele karar"],
        "hook_tags": [],
        "natal_promise": {
            "connected_points": [
                {"kind": "house", "value": 3, "score": 0.8},
                {"kind": "sign", "value": "capricorn", "score": 0.6},
                {"kind": "dispositor_chain", "value": "neptune->jupiter", "score": 0.7},
                {"kind": "planet", "value": "south node", "score": 0.4},
            ]
        },
    }


def test_tr_normalize_basic_diacritics() -> None:
    assert tr_normalize("iletisim hiz dogrudan kacinma golge duzen") == "iletişim hız doğrudan kaçınma gölge düzen"


def test_house_format() -> None:
    assert "3. Ev" in tr_normalize("3 ev vurgusu")


def test_collocation_fix() -> None:
    out = polish_collocations("neptune disiplini ve capricorn stili")
    lowered = out.lower()
    assert "neptune disiplini" not in lowered
    assert "capricorn stili" not in lowered
    assert "belirsizliği yönetme becerin" in lowered
    assert "kontrole çekilme hali" in lowered


def test_no_nodes_in_public_copy_default() -> None:
    card = _sample_card()
    connected = card["natal_promise"]["connected_points"]
    out = apply_copy_quality_layer(card, connected, context={"transit_house": 3})
    merged = " ".join(
        [
            str(out.get("conflict") or ""),
            str(out.get("shadow") or ""),
            str(out.get("upper") or ""),
            " ".join(str(x) for x in out.get("guidance", [])),
            " ".join(str(x) for x in out.get("watch_out", [])),
        ]
    ).lower()
    assert "south node" not in merged
    assert "north node" not in merged


def test_determinism_same_input_same_output() -> None:
    card = _sample_card()
    out_a = apply_copy_quality_layer(card, card["natal_promise"]["connected_points"], context={"transit_house": 9})
    out_b = apply_copy_quality_layer(card, card["natal_promise"]["connected_points"], context={"transit_house": 9})
    hash_a = hashlib.sha1(str(normalize_card_text_tr(out_a)).encode("utf-8")).hexdigest()
    hash_b = hashlib.sha1(str(normalize_card_text_tr(out_b)).encode("utf-8")).hexdigest()
    assert hash_a == hash_b


def test_guidance_and_watch_out_lengths_and_non_empty() -> None:
    card = _sample_card()
    out = apply_copy_quality_layer(card, card["natal_promise"]["connected_points"], context={"transit_house": 3})
    guidance = out.get("guidance") if isinstance(out.get("guidance"), list) else []
    watch = out.get("watch_out") if isinstance(out.get("watch_out"), list) else []
    assert len(guidance) == 3
    assert len(watch) == 2
    assert all(str(item).strip() for item in guidance)
    assert all(str(item).strip() for item in watch)


def test_path_scoring_selects_house_sign_dispositor_motifs() -> None:
    bits = {
        "house_values": [3],
        "signs": ["Oğlak"],
        "dispositor_chain": "Neptün -> Jüpiter",
    }
    motifs = select_path_motifs(bits, context={"transit_house": 3})
    selected = motifs["selected"]
    types = [item["type"] for item in selected]
    assert "house_scene" in types
    assert "sign_style" in types
    assert "dispositor_hint" in types


def test_phrase_injection_uses_hybrid_context_for_uranus_mars() -> None:
    card = _sample_card()
    card["natal_context_pack"] = {
        "target": {"planet": "Mars", "house": 9, "sign": "virgo", "sign_tr": "Başak"},
        "dispositor": {"planet": "Mercury", "house": 1, "sign": "capricorn"},
        "rulership_houses": [{"house": 4, "sign": "aries"}, {"house": 11, "sign": "scorpio"}],
    }
    out = apply_copy_quality_layer(
        card,
        card["natal_promise"]["connected_points"],
        context={
            "transit_planet": "Uranus",
            "transit_house": 5,
            "aspect": "trine",
            "target": "Mars",
        },
    )
    merged = " ".join(
        [
            str(out.get("conflict") or ""),
            str(out.get("upper") or ""),
            " ".join(str(x) for x in out.get("guidance", [])),
        ]
    )
    assert "Başak" in merged
    assert "9. Ev" in merged
    assert any(token in merged.lower() for token in ("eğitim", "yayın", "uzman", "yabancı dil", "mentorluk"))
    assert any(token in merged.lower() for token in ("üretim", "yaratıc", "sahne", "prototip"))
    assert any(token in merged.lower() for token in ("sprint", "prototip", "not", "ölç"))
    assert out.get("conflict_label") == "Akış"
    assert out.get("conflict_tone") == "flow"


def test_period_copy_is_multi_paragraph_and_has_hooks() -> None:
    selected_events = [
        {"transit_body": "Neptune", "aspect": "square", "natal_point": "ASC", "houses": {"transit_in_natal_house": 3}},
        {"transit_body": "Uranus", "aspect": "trine", "natal_point": "Mars", "houses": {"transit_in_natal_house": 5, "natal_point_house": 9}},
    ]
    out = build_period_copy(
        selected_events=selected_events,
        natal_snapshot={
            "bodies": [{"body": "Mars", "house": 9, "sign": "Virgo"}, {"body": "Sun", "house": 1, "sign": "Capricorn"}],
            "angles": {"ASC": {"point": "ASC", "sign": "Capricorn"}},
        },
        dominant_house=9,
        dominant_planet="Saturn",
        pressure=0.62,
        support=0.54,
        domains=["zihin", "kariyer"],
    )
    assert "\n\n" in out["core_story"]
    assert "çünkü" in out["core_story"].lower()
    assert "bu dönem 'nasıl'ı değiştiriyor" in out["core_story"].lower()
    assert isinstance(out.get("root_causes"), list) and out["root_causes"]


def test_build_root_causes_is_deterministic() -> None:
    selected_events = [
        {"event_id": "e1", "transit_body": "Neptune", "aspect": "square", "natal_point": "ASC", "houses": {"transit_in_natal_house": 3}},
        {"event_id": "e2", "transit_body": "Uranus", "aspect": "trine", "natal_point": "Mars", "houses": {"transit_in_natal_house": 5, "natal_point_house": 9}},
        {"event_id": "e3", "transit_body": "Saturn", "aspect": "opposition", "natal_point": "DSC", "houses": {"transit_in_natal_house": 7}},
    ]
    natal = {
        "bodies": [{"body": "Mars", "house": 9, "sign": "Virgo"}, {"body": "Sun", "house": 1, "sign": "Capricorn"}],
        "angles": {"ASC": {"point": "ASC", "sign": "Capricorn"}},
    }
    out_a = build_root_causes(selected_events, natal)
    out_b = build_root_causes(selected_events, natal)
    assert out_a == out_b


def test_root_causes_identity_spine_sanity_with_neptune_square_asc() -> None:
    selected_events = [
        {"event_id": "e1", "transit_body": "Neptune", "aspect": "square", "natal_point": "ASC", "houses": {"transit_in_natal_house": 3}},
    ]
    natal = {
        "bodies": [{"body": "Sun", "house": 1, "sign": "Capricorn"}],
        "angles": {"ASC": {"point": "ASC", "sign": "Capricorn"}},
    }
    causes = build_root_causes(selected_events, natal)
    by_key = {item["key"]: item for item in causes}
    assert "identity_spine" in by_key
    assert float(by_key["identity_spine"]["score"]) >= 0.7


def test_root_causes_method_shift_9_virgo_sanity() -> None:
    selected_events = [
        {"event_id": "e1", "transit_body": "Uranus", "aspect": "trine", "natal_point": "Mars", "houses": {"transit_in_natal_house": 5, "natal_point_house": 9}},
    ]
    natal = {
        "bodies": [{"body": "Mars", "house": 9, "sign": "Virgo"}],
        "angles": {"ASC": {"point": "ASC", "sign": "Capricorn"}},
    }
    causes = build_root_causes(selected_events, natal)
    keys = {item["key"] for item in causes}
    assert "method_shift_9_virgo" in keys
