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

    assert packets["registry_authority"] == "v0.1_plus_manual_delta_v0_2_plus_v0_3_plus_v0_4"
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

    assert candidate_inventory["registry_authority"] == "v0.1_plus_manual_delta_v0_2_plus_v0_3_plus_v0_4"
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
