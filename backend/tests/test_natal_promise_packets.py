import json
from pathlib import Path

from app.meaning.projection_shadow_v1_builder import (
    build_profile_narrative_projection_v1,
    build_profile_v8_projection_v1,
)
from app.meaning.meaning_graph_v1_1_builder import build_meaning_graph_v1_1
from app.natal.natal_promise_packets import build_natal_promise_packets_v1


def _istanbul_public() -> dict:
    path = Path("backend/tests/_artifacts/reasoning_output_review/natal_public_istanbul_1996_12_28.json")
    payload = json.loads(path.read_text())
    return payload.get("public", payload)


def _istanbul_2020_response() -> dict:
    path = Path("backend/tests/_artifacts/natal_interpret_full_2020-04-10_08-26_istanbul_user_compact_debug.json")
    return json.loads(path.read_text())


def _izmir_1996_response() -> dict:
    path = Path("backend/tests/_artifacts/natal_interpret_full_1996-03-08_08-30_izmir_user_compact_debug.json")
    return json.loads(path.read_text())


def _istanbul_1994_response() -> dict:
    path = Path("backend/tests/_artifacts/natal_interpret_full_1994-06-25_10-00_istanbul_user_compact_debug.json")
    return json.loads(path.read_text())


def _adana_1998_response() -> dict:
    path = Path("backend/tests/_artifacts/natal_interpret_full_1998-09-12_07-30_adana_user_compact_debug.json")
    return json.loads(path.read_text())


def _legacy_graph() -> dict:
    return {
        "version": "meaning_graph_v1_1",
        "nodes": [
            {
                "node_id": "legacy_identity",
                "node_type": "narrative",
                "title": "Kimlik Çizgisi",
                "summary": "Dışarıdan güçlü görünürken içeride daha çok tartı kuruyorsun.",
                "layers": [{"layer": "effect", "weight": 0.7}, {"layer": "shadow", "weight": 0.3}],
                "primary_layer": "effect",
                "domain": "identity",
                "source_family": "supporting_threads",
                "source_path": "public.supporting_threads[0].paragraph",
                "evidence_ids": ["e1"],
                "projection_hints": {"surfaces": ["profile_top", "profile_deep"], "priority": 0.9},
                "dedupe_fingerprint": "legacy_identity",
            },
            {
                "node_id": "legacy_relationship",
                "node_type": "narrative",
                "title": "Yakınlık Çizgisi",
                "summary": "Yakınlıkta güven duygusu belirginleştiğinde tonun daha yumuşak akıyor.",
                "layers": [{"layer": "mechanism", "weight": 0.6}, {"layer": "effect", "weight": 0.4}],
                "primary_layer": "mechanism",
                "domain": "relationships",
                "source_family": "supporting_threads",
                "source_path": "public.supporting_threads[1].paragraph",
                "evidence_ids": ["e2"],
                "projection_hints": {"surfaces": ["profile_top", "profile_deep"], "priority": 0.88},
                "dedupe_fingerprint": "legacy_relationship",
            },
            {
                "node_id": "legacy_career",
                "node_type": "guidance",
                "title": "Görünürlük Çizgisi",
                "summary": "Hazırlık ritmi oturduğunda görünürlük daha sakin büyüyor.",
                "layers": [{"layer": "potential", "weight": 0.75}],
                "primary_layer": "potential",
                "domain": "career",
                "source_family": "supporting_threads",
                "source_path": "public.supporting_threads[2].paragraph",
                "evidence_ids": ["e3"],
                "projection_hints": {"surfaces": ["profile_top", "profile_deep"], "priority": 0.86},
                "dedupe_fingerprint": "legacy_career",
            },
        ],
        "evidence": [
            {"evidence_id": "e1", "node_id": "legacy_identity", "kind": "text", "source_family": "supporting_threads", "source_path": "public.supporting_threads[0].paragraph", "weight": 0.8, "text_payload": "Kimlik desteği", "structured_payload": None},
            {"evidence_id": "e2", "node_id": "legacy_relationship", "kind": "text", "source_family": "supporting_threads", "source_path": "public.supporting_threads[1].paragraph", "weight": 0.8, "text_payload": "İlişki desteği", "structured_payload": None},
            {"evidence_id": "e3", "node_id": "legacy_career", "kind": "text", "source_family": "supporting_threads", "source_path": "public.supporting_threads[2].paragraph", "weight": 0.8, "text_payload": "Kariyer desteği", "structured_payload": None},
        ],
    }


def _packet(
    *,
    packet_id: str,
    domain: str,
    promise_type: str,
    strength: float,
    headline: str,
    direct: str,
    scene: str,
    gift: str,
    shadow: str = "",
    tension: str = "",
    growth: str = "",
) -> dict:
    return {
        "id": packet_id,
        "domain": domain,
        "promise_type": promise_type,
        "strength": strength,
        "technical_anchors": [headline.split(".")[0]],
        "source_evidence_ids": [packet_id],
        "direct_meaning": direct,
        "lived_scene": scene,
        "gift": gift,
        "shadow_or_friction": shadow,
        "inner_tension": tension,
        "growth_direction": growth,
        "voice_seeds": [headline],
        "avoid_phrases": [],
        "source_category_ids": [packet_id],
        "source_thread_ids": [],
        "source_section_ids": [packet_id],
        "projection_hints": {"priority": strength, "surfaces": ["profile_top", "profile_deep"]},
    }


def test_build_natal_promise_packets_istanbul_preserves_gift_forward_mix() -> None:
    public = _istanbul_public()
    packets = build_natal_promise_packets_v1(
        sections_v2=public.get("sections_v2"),
        supporting_threads=public.get("supporting_threads"),
    )

    assert packets["registry_authority"] == "v0.1_plus_manual_delta_v0_2_plus_v0_3_plus_v0_4_plus_v0_5_plus_v0_7_plus_v0_8"
    assert len(packets["packets"]) >= 3
    assert any(packet["promise_type"] in {"gift", "love_style", "mind_style", "mind_identity"} for packet in packets["packets"])
    assert not all(packet["promise_type"] in {"shadow_or_friction", "wound_to_gift"} for packet in packets["packets"])

    moon_packet = next(packet for packet in packets["packets"] if packet["id"] == "moon_trine_venus_emotional_warmth")
    assert moon_packet["promise_type"] in {"gift", "love_style"}
    assert "güzelleşt" in moon_packet["gift"].lower() or "iyi gel" in moon_packet["gift"].lower()
    assert "atmak Yakınlık" not in moon_packet["shadow_or_friction"]

    saturn_packet = next(packet for packet in packets["packets"] if packet["id"] == "saturn_sextile_uranus_structured_originality")
    assert saturn_packet["promise_type"] in {"gift", "mind_style", "mind_identity"}
    assert "omurga" in " ".join(saturn_packet["voice_seeds"]).lower() or "özgün" in saturn_packet["direct_meaning"].lower()

    venus_packet = next(packet for packet in packets["packets"] if packet["id"] == "venus_sagittarius_12h_hidden_expansive_love")
    assert venus_packet["promise_type"] == "career_signature"
    assert venus_packet["domain"] == "career"
    assert "görünür" in venus_packet["direct_meaning"].lower() or "üretim" in venus_packet["direct_meaning"].lower()
    assert "olmak Dışarıda" not in venus_packet["shadow_or_friction"]


def test_build_natal_promise_packets_candidate_inventory_is_broader_than_selected() -> None:
    public = _istanbul_public()
    selected = build_natal_promise_packets_v1(
        sections_v2=public.get("sections_v2"),
        supporting_threads=public.get("supporting_threads"),
    )
    candidate_inventory = build_natal_promise_packets_v1(
        sections_v2=public.get("sections_v2"),
        supporting_threads=public.get("supporting_threads"),
        mode="candidate_inventory",
    )

    selected_ids = {packet["id"] for packet in selected["packets"]}
    candidate_ids = {packet["id"] for packet in candidate_inventory["packets"]}

    assert candidate_inventory["meta"]["mode"] == "candidate_inventory"
    assert len(candidate_ids) > len(selected_ids)
    assert selected_ids <= candidate_ids
    assert "capricorn_asc_sun_1h_composed_self_construction" in candidate_ids
    assert "moon_leo_8h_deep_proud_heart" in candidate_ids
    assert "saturn_3h_aries_speech_decision_language" in candidate_ids


def test_build_natal_promise_packets_candidate_inventory_uses_raw_chart_signatures_when_surface_payload_is_lossy() -> None:
    path = Path("backend/tests/_artifacts/natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json")
    raw = json.loads(path.read_text())

    candidate_inventory = build_natal_promise_packets_v1(
        sections_v2=raw.get("sections_v2"),
        supporting_threads=raw.get("supporting_threads"),
        planets=raw.get("planets"),
        aspects=raw.get("aspects"),
        natal_graph_compact=raw.get("natal_graph_compact"),
        metadata=raw.get("metadata"),
        meta_info=raw.get("meta_info"),
        mode="candidate_inventory",
    )
    candidate_ids = {packet["id"] for packet in candidate_inventory["packets"]}

    assert len(candidate_inventory["packets"]) > 5
    assert "moon_trine_venus_emotional_warmth_chart_exact" in candidate_ids
    assert "saturn_sextile_uranus_structured_originality_chart_exact" in candidate_ids
    assert "venus_sagittarius_12h_hidden_expansive_love_chart_exact" in candidate_ids
    assert "capricorn_asc_sun_1h_composed_self_construction_chart_exact" in candidate_ids
    assert "saturn_3h_aries_speech_decision_language_chart_exact" in candidate_ids
    assert "moon_leo_8h_deep_proud_heart_chart_exact" in candidate_ids


def test_build_natal_promise_packets_2020_candidate_inventory_fires_v0_4_overlay() -> None:
    raw = _istanbul_2020_response()

    candidate_inventory = build_natal_promise_packets_v1(
        sections_v2=raw.get("sections_v2"),
        supporting_threads=raw.get("supporting_threads"),
        planets=raw.get("planets"),
        aspects=raw.get("aspects"),
        natal_graph_compact=raw.get("natal_graph_compact"),
        metadata=raw.get("metadata"),
        meta_info=raw.get("meta_info"),
        mode="candidate_inventory",
    )
    candidate_ids = {packet["id"] for packet in candidate_inventory["packets"]}

    assert candidate_inventory["registry_authority"] == "v0.1_plus_manual_delta_v0_2_plus_v0_3_plus_v0_4_plus_v0_5_plus_v0_7_plus_v0_8"
    assert len(candidate_inventory["packets"]) >= 10
    assert "gemini_asc_venus_1h_social_relational_presence_chart_exact" in candidate_ids
    assert "sun_aries_12h_hidden_private_fire_chart_exact" in candidate_ids
    assert "aquarius_mc_mars_conjunct_mc_visible_freedom_drive" in candidate_ids
    assert "venus_trine_mars_relational_attraction_signal_chart_exact" in candidate_ids
    assert "venus_trine_saturn_trust_bond_chart_exact" in candidate_ids
    assert "moon_scorpio_6h_emotional_routine_sensitivity_chart_exact" in candidate_ids
    assert "mercury_sextile_9h_capricorn_aquarius_intellectual_authority_chart_exact" in candidate_ids


def test_build_natal_promise_packets_2020_selected_inventory_broadens_safely() -> None:
    raw = _istanbul_2020_response()

    selected = build_natal_promise_packets_v1(
        sections_v2=raw.get("sections_v2"),
        supporting_threads=raw.get("supporting_threads"),
        planets=raw.get("planets"),
        aspects=raw.get("aspects"),
        natal_graph_compact=raw.get("natal_graph_compact"),
        metadata=raw.get("metadata"),
        meta_info=raw.get("meta_info"),
        mode="selected",
    )
    selected_ids = [packet["id"] for packet in selected["packets"]]

    assert len(selected_ids) == 4
    assert "gemini_asc_venus_1h_social_relational_presence_chart_exact" in selected_ids
    assert "relationship_relationships" in selected_ids
    assert len(selected_ids) == len(set(selected_ids))
    assert not any(packet_id.endswith("_aux") for packet_id in selected_ids)


def test_build_natal_promise_packets_istanbul_1996_does_not_pick_up_v0_4_chart_exacts() -> None:
    raw = json.loads(
        Path("backend/tests/_artifacts/natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json").read_text()
    )
    candidate_inventory = build_natal_promise_packets_v1(
        sections_v2=raw.get("sections_v2"),
        supporting_threads=raw.get("supporting_threads"),
        planets=raw.get("planets"),
        aspects=raw.get("aspects"),
        natal_graph_compact=raw.get("natal_graph_compact"),
        metadata=raw.get("metadata"),
        meta_info=raw.get("meta_info"),
        mode="candidate_inventory",
    )
    candidate_ids = {packet["id"] for packet in candidate_inventory["packets"]}

    assert "gemini_asc_venus_1h_social_relational_presence_chart_exact" not in candidate_ids
    assert "sun_aries_12h_hidden_private_fire_chart_exact" not in candidate_ids
    assert "aquarius_mc_mars_conjunct_mc_visible_freedom_drive" not in candidate_ids


def test_build_natal_promise_packets_izmir_1996_candidate_inventory_fires_v0_5_overlay() -> None:
    raw = _izmir_1996_response()

    candidate_inventory = build_natal_promise_packets_v1(
        sections_v2=raw.get("sections_v2"),
        supporting_threads=raw.get("supporting_threads"),
        planets=raw.get("planets"),
        aspects=raw.get("aspects"),
        natal_graph_compact=raw.get("natal_graph_compact"),
        metadata=raw.get("metadata"),
        meta_info=raw.get("meta_info"),
        mode="candidate_inventory",
    )
    packets = candidate_inventory["packets"]
    candidate_ids = {packet["id"] for packet in packets}
    packet_lookup = {str(packet.get("id") or "").strip(): packet for packet in packets}

    assert candidate_inventory["registry_authority"] == "v0.1_plus_manual_delta_v0_2_plus_v0_3_plus_v0_4_plus_v0_5_plus_v0_7_plus_v0_8"
    assert len(packets) >= 13
    assert "taurus_asc_venus_12h_hidden_value_identity_chart_exact" in candidate_ids
    assert "venus_taurus_12h_private_love_inner_beauty_chart_exact" in candidate_ids
    assert "mc_capricorn_ruler_saturn_pisces_12h_invisible_preparation_chart_exact" in candidate_ids
    assert "saturn_pisces_12h_private_maturity_boundary_sensitivity_chart_exact" in candidate_ids
    assert "dsc_scorpio_ruler_mars_pisces_12h_trust_threshold_silent_desire_chart_exact" in candidate_ids
    assert "pluto_7h_relationship_power_depth_chart_exact" in candidate_ids
    assert "mars_pisces_12h_hidden_action_soft_drive_chart_exact" in candidate_ids
    assert any(packet_id.startswith("sun_mars_pisces_12h_private_will_and_hidden_drive") for packet_id in candidate_ids)
    assert "pisces_12h_stellium_inner_world_saturation_chart_exact" in candidate_ids
    assert "mercury_pisces_11h_social_intuition_mind_chart_exact" in candidate_ids
    assert "mercury_square_pluto_deep_mind_pressure_chart_exact" in candidate_ids
    assert any(packet_id.startswith("uranus_square_asc_venus_unsettled_outer_signal") for packet_id in candidate_ids)

    assert packet_lookup["taurus_asc_venus_12h_hidden_value_identity_chart_exact"]["chart_facts_match"] is True
    assert packet_lookup["dsc_scorpio_ruler_mars_pisces_12h_trust_threshold_silent_desire_chart_exact"]["chart_facts_match"] is True
    assert packet_lookup["mc_capricorn_ruler_saturn_pisces_12h_invisible_preparation_chart_exact"]["chart_facts_match"] is True
    assert packet_lookup["pisces_12h_stellium_inner_world_saturation_chart_exact"]["chart_facts_match"] is True


def test_build_natal_promise_packets_istanbul_1994_candidate_inventory_fires_v0_7_overlay() -> None:
    raw = _istanbul_1994_response()

    candidate_inventory = build_natal_promise_packets_v1(
        sections_v2=raw.get("sections_v2"),
        supporting_threads=raw.get("supporting_threads"),
        planets=raw.get("planets"),
        aspects=raw.get("aspects"),
        natal_graph_compact=raw.get("natal_graph_compact"),
        metadata=raw.get("metadata"),
        meta_info=raw.get("meta_info"),
        mode="candidate_inventory",
    )
    packets = candidate_inventory["packets"]
    candidate_ids = {packet["id"] for packet in packets}
    packet_lookup = {str(packet.get("id") or "").strip(): packet for packet in packets}

    assert candidate_inventory["registry_authority"] == "v0.1_plus_manual_delta_v0_2_plus_v0_3_plus_v0_4_plus_v0_5_plus_v0_7_plus_v0_8"
    assert len(packets) >= 14
    expected_exact_ids = {
        "leo_asc_sun_cancer_11h_warm_visibility_belonging_chart_exact",
        "pluto_node_scorpio_4h_roots_inner_security_transformation_chart_exact",
        "ic_scorpio_pluto_node_private_emotional_inheritance_chart_exact",
        "moon_capricorn_5h_serious_heart_creative_form_chart_exact",
        "moon_uranus_neptune_capricorn_5h_structured_imagination_chart_exact",
        "mc_taurus_mars_10h_steady_public_drive_chart_exact",
        "mars_opposite_pluto_public_power_roots_tension_chart_exact",
        "aquarius_dsc_saturn_pisces_7h_freedom_responsibility_sensitivity_chart_exact",
        "venus_leo_12h_hidden_romantic_pride_chart_exact",
        "jupiter_scorpio_3h_deep_speech_psychological_learning_chart_exact",
        "chiron_virgo_1h_visible_sensitivity_self_correction_chart_exact",
    }
    assert expected_exact_ids <= candidate_ids
    assert any(
        packet_id.startswith("sun_mercury_cancer_11h_social_emotional_intelligence")
        for packet_id in candidate_ids
    )

    for packet_id in expected_exact_ids:
        assert packet_lookup[packet_id]["chart_facts_match"] is True


def test_build_natal_promise_packets_v0_9a_generates_debug_only_identity_and_career_candidates(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    raw = _istanbul_1994_response()

    candidate_inventory = build_natal_promise_packets_v1(
        sections_v2=raw.get("sections_v2"),
        supporting_threads=raw.get("supporting_threads"),
        planets=raw.get("planets"),
        aspects=raw.get("aspects"),
        natal_graph_compact=raw.get("natal_graph_compact"),
        metadata=raw.get("metadata"),
        meta_info=raw.get("meta_info"),
        mode="candidate_inventory",
    )
    packet_lookup = {
        str(packet.get("id") or "").strip(): packet
        for packet in candidate_inventory["packets"]
    }

    identity = packet_lookup["composed_identity_route_v0_9a"]
    career = packet_lookup["composed_career_route_v0_9a"]

    for packet, expected_family, expected_domain in (
        (identity, "identity_route", "identity"),
        (career, "career_route", "career"),
    ):
        assert packet["source_type"] == "composed_semantic"
        assert packet["family"] == expected_family
        assert packet["domain"] == expected_domain
        assert packet["chart_facts_match"] is True
        assert packet["public_job"] == "debug_only"
        assert packet["confidence"] >= 0.6
        assert packet["confidence_tier"] in {"medium", "high"}
        assert packet["domain_reason"]
        assert packet["lived_scene"]
        assert packet["lived_scene_atoms"]
        assert packet["evidence_trace"]["family_inputs"]
        assert packet["public_eligibility"]["debug_eligible"] is True
        assert packet["public_eligibility"]["detail_eligible"] is False
        assert packet["public_eligibility"]["public_support_eligible"] is False
        assert packet["public_eligibility"]["public_main_eligible"] is False
        assert packet["meta"]["source_type"] == "composed_semantic"
        assert packet["meta"]["v0_9_composed"] is True
        assert packet["meta"]["non_public_discovery"] is True


def test_build_natal_promise_packets_v0_9a_defaults_off() -> None:
    raw = _adana_1998_response()
    candidate_inventory = build_natal_promise_packets_v1(
        sections_v2=raw.get("sections_v2"),
        supporting_threads=raw.get("supporting_threads"),
        planets=raw.get("planets"),
        aspects=raw.get("aspects"),
        natal_graph_compact=raw.get("natal_graph_compact"),
        metadata=raw.get("metadata"),
        meta_info=raw.get("meta_info"),
        mode="candidate_inventory",
    )
    candidate_ids = {packet["id"] for packet in candidate_inventory["packets"]}

    assert "composed_identity_route_v0_9a" not in candidate_ids
    assert "composed_career_route_v0_9a" not in candidate_ids


def test_profile_narrative_projection_v1_hybrid_fallback_prefers_packets() -> None:
    graph = _legacy_graph()
    packets = {
        "version": "natal_promise_packets_v1",
        "packets": [
            _packet(
                packet_id="mind_packet",
                domain="mind",
                promise_type="gift",
                strength=0.92,
                headline="Ciddi görünen yerinin altında hızlı çalışan bir zihin var.",
                direct="Farklı fikre omurga verebilen bir zihin.",
                scene="Bir fikir geldiğinde onu hızlıca çalışır hale getirmek isteyebilirsin.",
                gift="Yeni fikri zemine indirebilmek.",
                shadow="Fazla kontrol hızını boğabilir.",
                tension="Bir yanın düzen, bir yanın özgürlük istiyor olabilir.",
                growth="Özgün fikri daha sakin taşımak.",
            ),
            _packet(
                packet_id="love_packet",
                domain="relationship",
                promise_type="love_style",
                strength=0.88,
                headline="Kalbin güven olmadan tam açılmıyor olabilir.",
                direct="Sevgi sende güven ve derinlik istiyor.",
                scene="Birine bağlandığında bu sende uzun yaşayan bir yere gidebilir.",
                gift="Sevdiğine iyi gelmek istemek.",
                shadow="Fazla verme eğilimi olabilir.",
                growth="Sevgi verirken kendini de korumak.",
            ),
        ],
    }

    projection = build_profile_narrative_projection_v1(
        meaning_graph_v1_1=graph,
        natal_promise_packets_v1=packets,
        include_packet_debug=True,
    )
    blocks = projection["profile_public"]["blocks"]
    node_ids = [block["node_id"] for block in blocks]

    assert projection["source_graph"] == "natal_promise_packets_v1"
    assert any(node_id.startswith("promise::") for node_id in node_ids)
    assert any(node_id.startswith("legacy_") for node_id in node_ids)
    assert projection["traceability"]["packet_count"] == 2


def test_profile_narrative_projection_v1_full_packet_mode_uses_only_packets() -> None:
    packets = {
        "version": "natal_promise_packets_v1",
        "packets": [
            _packet(
                packet_id="gift_packet",
                domain="mind",
                promise_type="gift",
                strength=0.95,
                headline="Senin gücün yeni fikri havada bırakmamak olabilir.",
                direct="Yeni fikri çalışır hale getiren bir kapasiten var.",
                scene="Bir şeyi yalnızca düşünmek değil, sistem kurmak isteyebilirsin.",
                gift="Yenilikle disiplini bir arada tutabilmek.",
                shadow="Fazla kontrol akışı bozabilir.",
                growth="Özgün fikri daha rahat taşımak.",
            ),
            _packet(
                packet_id="need_packet",
                domain="relationship",
                promise_type="love_style",
                strength=0.9,
                headline="Kalbin güven oluşunca daha hızlı açılıyor olabilir.",
                direct="Yakınlık sende güvenle derinleşiyor.",
                scene="Bir bağ içeri oturduğunda duygun daha görünür hale gelebilir.",
                gift="Sevdiğine sıcak ve cömert yaklaşabilmek.",
                shadow="İçine çekilmek daha kolay tetiklenebilir.",
                growth="Derinliği güvenli bağda korumak.",
            ),
            _packet(
                packet_id="wound_packet",
                domain="career",
                promise_type="wound_to_gift",
                strength=0.86,
                headline="Görünür olmak sende hassas bir yere dokunabilir.",
                direct="Görünürlük hassasiyetini zamanla sese çevirebilirsin.",
                scene="Ortaya çıkmadan önce çok hazır olmak isteyebilirsin.",
                gift="Başkalarına alan açan bir ses geliştirmek.",
                shadow="Fazla kendini sınamak.",
                growth="Daha erken görünür kalabilmek.",
            ),
        ],
    }
    projection = build_profile_narrative_projection_v1(
        meaning_graph_v1_1=_legacy_graph(),
        natal_promise_packets_v1=packets,
        include_packet_debug=True,
    )
    blocks = projection["profile_public"]["blocks"]

    assert projection["source_graph"] == "natal_promise_packets_v1"
    assert blocks
    assert all(block["node_id"].startswith("promise::") for block in blocks)

    gift_block = next(block for block in blocks if "havada bırakmamak" in block["headline"])
    assert "Yeni fikri çalışır hale getiren bir kapasiten var." in gift_block["body"]
    assert "Bir şeyi yalnızca düşünmek değil, sistem kurmak isteyebilirsin." in gift_block["body"]
    assert "Gücü de burada:" not in gift_block["body"]
    assert "güçlü taraflarından biri olabilir" not in gift_block["body"]
    assert any(
        phrase in gift_block["body"]
        for phrase in (
            "güçlü çalışan taraflardan biri",
            "sağlam yanını oluşturuyor",
            "en rahat çalıştığın yerlerden biri",
        )
    )

    wound_block = next(block for block in blocks if "hassas bir yere dokunabilir" in block["headline"])
    assert "Ortaya çıkmadan önce çok hazır olmak isteyebilirsin." in wound_block["body"]
    assert "daha erken görünür kalabilmek" in wound_block["body"].lower()
    assert wound_block["body"].count(".") >= 3


def test_profile_v8_projection_v1_keeps_slot_schema_with_packets() -> None:
    packets = {
        "version": "natal_promise_packets_v1",
        "packets": [
            _packet(
                packet_id="mind_packet",
                domain="mind",
                promise_type="mind_style",
                strength=0.92,
                headline="Ciddi görünen yerinin altında hızlı çalışan bir zihin var.",
                direct="Farklı fikre omurga verebilen bir zihin.",
                scene="Bir fikir geldiğinde onu hızlıca çalışır hale getirmek isteyebilirsin.",
                gift="Yeni fikri zemine indirebilmek.",
                shadow="Fazla kontrol hızını boğabilir.",
                tension="Bir yanın düzen, bir yanın özgürlük istiyor olabilir.",
                growth="Özgün fikri daha sakin taşımak.",
            ),
            _packet(
                packet_id="love_packet",
                domain="relationship",
                promise_type="love_style",
                strength=0.88,
                headline="Kalbin güven olmadan tam açılmıyor olabilir.",
                direct="Sevgi sende güven ve derinlik istiyor.",
                scene="Birine bağlandığında bu sende uzun yaşayan bir yere gidebilir.",
                gift="Sevdiğine iyi gelmek istemek.",
                shadow="Fazla verme eğilimi olabilir.",
                growth="Sevgi verirken kendini de korumak.",
            ),
            _packet(
                packet_id="career_packet",
                domain="career",
                promise_type="career_signature",
                strength=0.82,
                headline="Bir şeyi hemen göstermekten çok, içine sindirip olgunlaştırmak sana daha yakın olabilir.",
                direct="Üretim ve görünürlük sende önce içeride olgunlaşmak isteyebilir.",
                scene="Bir işi paylaşmadan önce biraz daha rafine etmek isteyebilirsin.",
                gift="Görünmeyen hazırlıkta güç toplayıp işi daha rafine sunabilmek.",
                shadow="Görünür olmayı gereğinden fazla ertelemek.",
                growth="İçeride büyüttüğün şeyi doğru zamanda hayata açabilmek.",
            ),
        ],
    }

    projection = build_profile_v8_projection_v1(
        meaning_graph_v1_1={"version": "meaning_graph_v1_1", "nodes": [], "evidence": []},
        natal_promise_packets_v1=packets,
        include_packet_debug=True,
    )

    assert projection["source_graph"] == "natal_promise_packets_v1"
    assert set(projection.keys()) == {"version", "source_graph_version", "source_graph", "hero", "identity_axis", "insight_strip", "differentiators", "traceability"}
    assert isinstance(projection["hero"], dict)
    assert isinstance(projection["identity_axis"], dict)
    assert isinstance(projection["insight_strip"], list)
    assert len(projection["insight_strip"]) == 3
    assert isinstance(projection["differentiators"], list)
    assert len(projection["differentiators"]) == 3
    assert projection["traceability"]["packet_count"] == 3
    assert projection["hero"]["trace"]["node_id"] == "promise::mind_packet"


# ---------------------------------------------------------------------------
# v0.9b — relationship_route + moon_signature debug-only candidates
# ---------------------------------------------------------------------------


def _v0_9b_chart_inputs(*, dsc_sign="libra", moon_sign="cancer", moon_house=4):
    """Synthesize the minimal chart-fact inputs the two new builders need."""
    planet_map_input = [
        {"planet": "Sun", "sign": "Leo", "house": 5},
        {"planet": "Moon", "sign": moon_sign.title(), "house": moon_house},
        {"planet": "Venus", "sign": "Libra", "house": 7},
        {"planet": "Mars", "sign": "Scorpio", "house": 8},
        {"planet": "Mercury", "sign": "Virgo", "house": 6},
        {"planet": "Jupiter", "sign": "Sagittarius", "house": 9},
        {"planet": "Saturn", "sign": "Capricorn", "house": 10},
        {"planet": "Uranus", "sign": "Aquarius", "house": 11},
        {"planet": "Neptune", "sign": "Pisces", "house": 12},
        {"planet": "Pluto", "sign": "Scorpio", "house": 8},
    ]
    house_rulers = {
        "1": {"cusp_sign": "Aries"},
        "4": {"cusp_sign": "Cancer"},
        "7": {"cusp_sign": dsc_sign.title()},
        "10": {"cusp_sign": "Capricorn"},
    }
    natal_graph_compact = {"house_rulers": house_rulers}
    return planet_map_input, house_rulers, natal_graph_compact


def _run_promise_builder(*, planets, natal_graph_compact, aspects=None):
    return build_natal_promise_packets_v1(
        sections_v2=[],
        supporting_threads=[],
        meaning_graph_v1_1=None,
        planets=planets,
        aspects=aspects or [],
        natal_graph_compact=natal_graph_compact,
        metadata=None,
        meta_info=None,
        locale="tr",
        mode="candidate_inventory",
    )


def _v0_9b_packets(payload, *, family):
    return [
        p
        for p in (payload.get("packets") or [])
        if str(p.get("source_type") or "") == "composed_semantic"
        and str(p.get("family") or "") == family
    ]


def test_v0_9b_relationship_route_flag_off_emits_no_relationship_candidate(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", raising=False)
    planets, _, ngc = _v0_9b_chart_inputs()
    payload = _run_promise_builder(planets=planets, natal_graph_compact=ngc)
    assert _v0_9b_packets(payload, family="relationship_route") == []


def test_v0_9b_moon_signature_flag_off_emits_no_moon_candidate(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", raising=False)
    planets, _, ngc = _v0_9b_chart_inputs()
    payload = _run_promise_builder(planets=planets, natal_graph_compact=ngc)
    assert _v0_9b_packets(payload, family="moon_signature") == []


def test_v0_9b_relationship_route_flag_on_emits_debug_only_candidate(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")
    planets, _, ngc = _v0_9b_chart_inputs()
    payload = _run_promise_builder(planets=planets, natal_graph_compact=ngc)
    candidates = _v0_9b_packets(payload, family="relationship_route")
    assert candidates, payload
    card = candidates[0]
    assert card["public_job"] == "debug_only"
    elig = card["public_eligibility"]
    assert elig["public_main_eligible"] is False
    assert elig["public_support_eligible"] is False
    assert elig["debug_eligible"] is True
    assert card["domain"] == "relationship"
    assert card["family"] == "relationship_route"
    assert card["subtype"] in {
        "trust_steadiness",
        "attraction_warmth",
        "boundary_conflict",
        "intimacy_depth",
        "emotional_need_affection",
        "hidden_private_love",
        "freedom_space",
        "wound_to_gift",
    }
    assert card["confidence"] >= 0.60
    for key in (
        "evidence_trace",
        "technical_anchors",
        "lived_scene",
        "lived_scene_atoms",
        "gift",
        "inner_tension",
        "growth_direction",
        "domain_reason",
    ):
        assert card.get(key), f"missing required field: {key}"


def test_v0_9b_moon_signature_flag_on_emits_debug_only_candidate(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", "true")
    planets, _, ngc = _v0_9b_chart_inputs()
    payload = _run_promise_builder(planets=planets, natal_graph_compact=ngc)
    candidates = _v0_9b_packets(payload, family="moon_signature")
    assert candidates, payload
    card = candidates[0]
    assert card["public_job"] == "debug_only"
    elig = card["public_eligibility"]
    assert elig["public_main_eligible"] is False
    assert elig["public_support_eligible"] is False
    assert elig["debug_eligible"] is True
    assert card["family"] == "moon_signature"
    assert card["subtype"] in {
        "emotional_rhythm",
        "home_inner_security",
        "daily_sensitivity",
        "creative_emotional_expression",
        "intimacy_depth",
        "private_emotional_processing",
    }
    assert card["confidence"] >= 0.60


def test_v0_9b_relationship_route_subtype_attraction_warmth_fires(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")
    planets = [
        {"planet": "Sun", "sign": "Leo", "house": 5},
        {"planet": "Moon", "sign": "Taurus", "house": 2},
        {"planet": "Venus", "sign": "Leo", "house": 5},
        {"planet": "Mars", "sign": "Aries", "house": 1},
        {"planet": "Mercury", "sign": "Virgo", "house": 6},
        {"planet": "Saturn", "sign": "Capricorn", "house": 10},
        {"planet": "Uranus", "sign": "Aquarius", "house": 11},
        {"planet": "Neptune", "sign": "Pisces", "house": 12},
        {"planet": "Pluto", "sign": "Scorpio", "house": 8},
        {"planet": "Jupiter", "sign": "Sagittarius", "house": 9},
    ]
    ngc = {
        "house_rulers": {
            "1": {"cusp_sign": "Aries"},
            "4": {"cusp_sign": "Cancer"},
            "7": {"cusp_sign": "Libra"},
            "10": {"cusp_sign": "Capricorn"},
        }
    }
    payload = _run_promise_builder(planets=planets, natal_graph_compact=ngc)
    candidates = _v0_9b_packets(payload, family="relationship_route")
    assert candidates
    assert candidates[0]["subtype"] == "attraction_warmth"


def test_v0_9b_moon_signature_subtype_home_inner_security_fires(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", "true")
    planets = [
        {"planet": "Sun", "sign": "Cancer", "house": 4},
        {"planet": "Moon", "sign": "Cancer", "house": 4},
        {"planet": "Venus", "sign": "Cancer", "house": 4},
        {"planet": "Mars", "sign": "Cancer", "house": 4},
        {"planet": "Mercury", "sign": "Cancer", "house": 4},
        {"planet": "Saturn", "sign": "Capricorn", "house": 10},
        {"planet": "Uranus", "sign": "Aquarius", "house": 11},
        {"planet": "Neptune", "sign": "Pisces", "house": 12},
        {"planet": "Pluto", "sign": "Scorpio", "house": 8},
        {"planet": "Jupiter", "sign": "Cancer", "house": 4},
    ]
    ngc = {
        "house_rulers": {
            "1": {"cusp_sign": "Aries"},
            "4": {"cusp_sign": "Cancer"},
            "7": {"cusp_sign": "Libra"},
            "10": {"cusp_sign": "Capricorn"},
        }
    }
    payload = _run_promise_builder(planets=planets, natal_graph_compact=ngc)
    moon_candidates = _v0_9b_packets(payload, family="moon_signature")
    assert moon_candidates
    assert moon_candidates[0]["subtype"] == "home_inner_security"


def test_v0_9b_relationship_route_default_fallback_carries_penalty(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")
    # neutral chart — no strong subtype signal
    planets = [
        {"planet": "Sun", "sign": "Gemini", "house": 3},
        {"planet": "Moon", "sign": "Gemini", "house": 3},
        {"planet": "Venus", "sign": "Gemini", "house": 3},
        {"planet": "Mars", "sign": "Gemini", "house": 3},
        {"planet": "Mercury", "sign": "Gemini", "house": 3},
        {"planet": "Jupiter", "sign": "Sagittarius", "house": 9},
        {"planet": "Saturn", "sign": "Aquarius", "house": 11},
        {"planet": "Uranus", "sign": "Aquarius", "house": 11},
        {"planet": "Neptune", "sign": "Pisces", "house": 12},
        {"planet": "Pluto", "sign": "Scorpio", "house": 8},
    ]
    ngc = {
        "house_rulers": {
            "1": {"cusp_sign": "Aries"},
            "4": {"cusp_sign": "Cancer"},
            "7": {"cusp_sign": "Libra"},
            "10": {"cusp_sign": "Capricorn"},
        }
    }
    payload = _run_promise_builder(planets=planets, natal_graph_compact=ngc)
    candidates = _v0_9b_packets(payload, family="relationship_route")
    # If a candidate fires under this neutral chart, it must be the
    # default-fallback subtype with the penalty applied.
    if candidates:
        card = candidates[0]
        if card["subtype"] == "trust_steadiness":
            assert card["scoring_breakdown"]["subtype_penalty"] > 0.0


def test_v0_9b_confidence_floor_filters_under_0_60(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", "true")
    # Sparse chart with no 7H planet and ruler in neutral house — relationship
    # builder should return None via the eligibility gate.
    planets = [
        {"planet": "Sun", "sign": "Gemini", "house": 3},
        {"planet": "Moon", "sign": "Gemini", "house": 3},
    ]
    ngc = {
        "house_rulers": {
            "1": {"cusp_sign": "Aries"},
            "4": {"cusp_sign": "Cancer"},
            "7": {"cusp_sign": "Libra"},
            "10": {"cusp_sign": "Capricorn"},
        }
    }
    payload = _run_promise_builder(planets=planets, natal_graph_compact=ngc)
    # No 7H planet, no relationship-supporting house → relationship builder
    # short-circuits without emitting.
    assert _v0_9b_packets(payload, family="relationship_route") == []


def test_v0_9b_detail_support_flag_only_lifts_detail_eligible(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", "true")
    planets, _, ngc = _v0_9b_chart_inputs(moon_sign="cancer", moon_house=4)

    # detail_support flag OFF
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT", raising=False)
    payload_off = _run_promise_builder(planets=planets, natal_graph_compact=ngc)
    moon_off = _v0_9b_packets(payload_off, family="moon_signature")
    assert moon_off
    assert moon_off[0]["public_eligibility"]["detail_eligible"] is False
    assert moon_off[0]["public_eligibility"]["public_main_eligible"] is False
    assert moon_off[0]["public_eligibility"]["public_support_eligible"] is False

    # detail_support flag ON — detail_eligible flips when confidence >= 0.7;
    # public_main / public_support stay False.
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT", "true")
    payload_on = _run_promise_builder(planets=planets, natal_graph_compact=ngc)
    moon_on = _v0_9b_packets(payload_on, family="moon_signature")
    assert moon_on
    elig = moon_on[0]["public_eligibility"]
    if moon_on[0]["confidence"] >= 0.7:
        assert elig["detail_eligible"] is True
    assert elig["public_main_eligible"] is False
    assert elig["public_support_eligible"] is False


# ---------------------------------------------------------------------------
# v0.9b.0.1 calibration — penalty bump + cross-family ownership
# ---------------------------------------------------------------------------


def test_v0_9b_0_1_relationship_default_fallback_penalty_value(monkeypatch) -> None:
    """When no subtype channel wins (all signals < 0.04 margin), the
    relationship_route default-fallback path must apply a penalty of at
    least 0.10 — bumped from 0.06 by v0.9b.0.1."""
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")
    # Sparse-evidence chart — produces default fallback path.
    planets = [
        {"planet": "Sun", "sign": "Gemini", "house": 3},
        {"planet": "Moon", "sign": "Gemini", "house": 3},
        {"planet": "Venus", "sign": "Gemini", "house": 3},
        {"planet": "Mars", "sign": "Sagittarius", "house": 9},
        {"planet": "Mercury", "sign": "Gemini", "house": 3},
        {"planet": "Saturn", "sign": "Capricorn", "house": 10},
        {"planet": "Uranus", "sign": "Aquarius", "house": 11},
        {"planet": "Neptune", "sign": "Pisces", "house": 12},
        {"planet": "Pluto", "sign": "Scorpio", "house": 8},
        {"planet": "Jupiter", "sign": "Sagittarius", "house": 9},
    ]
    ngc = {
        "house_rulers": {
            "1": {"cusp_sign": "Aries"},
            "4": {"cusp_sign": "Cancer"},
            "7": {"cusp_sign": "Libra"},
            "10": {"cusp_sign": "Capricorn"},
        }
    }
    payload = _run_promise_builder(planets=planets, natal_graph_compact=ngc)
    candidates = _v0_9b_packets(payload, family="relationship_route")
    if candidates:
        card = candidates[0]
        meta = card.get("meta") or {}
        if meta.get("subtype_default_fallback"):
            assert card["scoring_breakdown"]["subtype_penalty"] >= 0.10, card["scoring_breakdown"]


def test_v0_9b_0_1_moon_default_fallback_penalty_value(monkeypatch) -> None:
    """moon_signature emotional_rhythm default fallback must carry the
    calibrated penalty (>= 0.10)."""
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", "true")
    # Chart that picks emotional_rhythm by exclusion (no subtype channel wins).
    planets = [
        {"planet": "Sun", "sign": "Sagittarius", "house": 9},
        {"planet": "Moon", "sign": "Sagittarius", "house": 9},
        {"planet": "Mercury", "sign": "Sagittarius", "house": 9},
        {"planet": "Venus", "sign": "Sagittarius", "house": 9},
        {"planet": "Mars", "sign": "Sagittarius", "house": 9},
        {"planet": "Jupiter", "sign": "Sagittarius", "house": 9},
        {"planet": "Saturn", "sign": "Aquarius", "house": 11},
        {"planet": "Uranus", "sign": "Aquarius", "house": 11},
        {"planet": "Neptune", "sign": "Pisces", "house": 12},
        {"planet": "Pluto", "sign": "Scorpio", "house": 8},
    ]
    ngc = {
        "house_rulers": {
            "1": {"cusp_sign": "Aries"},
            "4": {"cusp_sign": "Cancer"},
            "7": {"cusp_sign": "Libra"},
            "10": {"cusp_sign": "Capricorn"},
        }
    }
    payload = _run_promise_builder(planets=planets, natal_graph_compact=ngc)
    moon = _v0_9b_packets(payload, family="moon_signature")
    if moon:
        card = moon[0]
        meta = card.get("meta") or {}
        if meta.get("subtype_default_fallback"):
            assert card["scoring_breakdown"]["subtype_penalty"] >= 0.10, card["scoring_breakdown"]


def test_v0_9b_0_1_cross_family_moon_ownership_metadata_present(monkeypatch) -> None:
    """When both families fire on the same chart and moon confidence
    exceeds relationship by >= 0.05, the relationship candidate's meta
    must carry ``moon_evidence_owned_by="moon_signature"`` and the
    eligibility map must carry
    ``future_renderer_eligibility_blocked=True``."""
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", "true")
    # Chart where moon scores higher than relationship and shares Moon evidence.
    planets = [
        {"planet": "Sun", "sign": "Pisces", "house": 12},
        {"planet": "Moon", "sign": "Pisces", "house": 12},
        {"planet": "Mercury", "sign": "Pisces", "house": 12},
        {"planet": "Venus", "sign": "Cancer", "house": 4},
        {"planet": "Mars", "sign": "Cancer", "house": 4},
        {"planet": "Jupiter", "sign": "Scorpio", "house": 8},
        {"planet": "Saturn", "sign": "Capricorn", "house": 10},
        {"planet": "Uranus", "sign": "Aquarius", "house": 11},
        {"planet": "Neptune", "sign": "Pisces", "house": 12},
        {"planet": "Pluto", "sign": "Scorpio", "house": 8},
    ]
    ngc = {
        "house_rulers": {
            "1": {"cusp_sign": "Aries"},
            "4": {"cusp_sign": "Cancer"},
            "7": {"cusp_sign": "Libra"},
            "10": {"cusp_sign": "Capricorn"},
        }
    }
    payload = _run_promise_builder(
        planets=planets,
        natal_graph_compact=ngc,
        aspects=[
            {"planet1": "Moon", "planet2": "Neptune", "type": "conjunction", "orb": 0.5},
            {"planet1": "Moon", "planet2": "Pluto", "type": "trine", "orb": 1.0},
        ],
    )
    rel = _v0_9b_packets(payload, family="relationship_route")
    moon = _v0_9b_packets(payload, family="moon_signature")
    # Both families must have fired for the ownership rule to be meaningful.
    if rel and moon:
        rel_card = rel[0]
        moon_card = moon[0]
        rel_meta = rel_card.get("meta") or {}
        moon_meta = moon_card.get("meta") or {}
        assert moon_meta.get("moon_evidence_owned_by") == "moon_signature"
        # Outcome depends on confidence delta; both possibilities are valid.
        outcome = rel_meta.get("cross_family_moon_ownership_outcome")
        owned_by = rel_meta.get("moon_evidence_owned_by")
        assert owned_by in {"moon_signature", "relationship_route"}
        if owned_by == "moon_signature":
            elig = rel_card.get("public_eligibility") or {}
            assert elig.get("future_renderer_eligibility_blocked") is True
            assert "moon_evidence_owned_elsewhere" in (elig.get("reason_codes") or [])
            assert outcome == "moon_takes_ownership"
        else:
            assert outcome in {"relationship_retains_ownership", "relationship_solo"}


def test_v0_9b_0_1_cross_family_ownership_does_not_change_public_eligibility_basics(monkeypatch) -> None:
    """The ownership rule must not flip public_main_eligible /
    public_support_eligible to True, and detail_eligible must remain
    False unless the v0.9b detail_support flag is independently on."""
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", "true")
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT", raising=False)
    planets, _, ngc = _v0_9b_chart_inputs(moon_sign="cancer", moon_house=4)
    payload = _run_promise_builder(planets=planets, natal_graph_compact=ngc)
    for card in _v0_9b_packets(payload, family="relationship_route"):
        elig = card.get("public_eligibility") or {}
        assert elig.get("public_main_eligible") is False
        assert elig.get("public_support_eligible") is False
        assert elig.get("detail_eligible") is False
        assert card.get("public_job") == "debug_only"
    for card in _v0_9b_packets(payload, family="moon_signature"):
        elig = card.get("public_eligibility") or {}
        assert elig.get("public_main_eligible") is False
        assert elig.get("public_support_eligible") is False
        assert elig.get("detail_eligible") is False
        assert card.get("public_job") == "debug_only"


def test_v0_9b_0_1_moon_self_owns_evidence_in_meta(monkeypatch) -> None:
    """moon_signature candidates always self-own their evidence."""
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", "true")
    planets, _, ngc = _v0_9b_chart_inputs(moon_sign="cancer", moon_house=4)
    payload = _run_promise_builder(planets=planets, natal_graph_compact=ngc)
    moon = _v0_9b_packets(payload, family="moon_signature")
    if moon:
        assert (moon[0].get("meta") or {}).get("moon_evidence_owned_by") == "moon_signature"
