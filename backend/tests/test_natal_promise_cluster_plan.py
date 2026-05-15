import json
from pathlib import Path

from app.natal.natal_promise_cluster_plan import build_natal_promise_cluster_plan_v1
from app.natal.public_builder import build_public_natal_view


def _istanbul_response() -> dict:
    path = Path("backend/tests/_artifacts/natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json")
    return json.loads(path.read_text())


def _istanbul_2020_response() -> dict:
    path = Path("backend/tests/_artifacts/natal_interpret_full_2020-04-10_08-26_istanbul_user_compact_debug.json")
    return json.loads(path.read_text())


def _izmir_1996_response() -> dict:
    path = Path("backend/tests/_artifacts/natal_interpret_full_1996-03-08_08-30_izmir_user_compact_debug.json")
    return json.loads(path.read_text())


def _istanbul_1994_response() -> dict:
    path = Path("backend/tests/_artifacts/natal_interpret_full_1994-06-25_10-00_istanbul_user_compact_debug.json")
    return json.loads(path.read_text())


def _packet(
    *,
    packet_id: str,
    domain: str,
    promise_type: str,
    strength: float,
    direct: str,
    scene: str,
    gift: str,
    anchors: list[str],
    evidence_ids: list[str],
    shadow: str = "",
    tension: str = "",
    growth: str = "",
    source_type: str = "legacy_graph",
    matched_archetypes: list[str] | None = None,
) -> dict:
    return {
        "id": packet_id,
        "domain": domain,
        "promise_type": promise_type,
        "source_type": source_type,
        "strength": strength,
        "technical_anchors": anchors,
        "source_evidence_ids": evidence_ids,
        "direct_meaning": direct,
        "lived_scene": scene,
        "gift": gift,
        "shadow_or_friction": shadow,
        "inner_tension": tension,
        "growth_direction": growth,
        "voice_seeds": [direct],
        "avoid_phrases": [],
        "source_category_ids": [packet_id],
        "source_thread_ids": [],
        "source_section_ids": [packet_id],
        "projection_hints": {"priority": strength, "surfaces": ["profile_top", "profile_deep"]},
        "scoring_breakdown": {"contradiction": 0.62, "archetype": 0.88},
        "matched_archetypes": list(matched_archetypes or []),
        "meta": {"source_type": source_type},
    }


def _composed_packet(
    *,
    packet_id: str,
    family: str,
    domain: str,
    confidence: float,
    confidence_tier: str,
    lived_scene: str,
    domain_reason: list[str] | None = None,
    public_job: str = "debug_only",
) -> dict:
    return {
        "id": packet_id,
        "theme_key": packet_id,
        "family": family,
        "subtype": "test_subtype",
        "source_type": "composed_semantic",
        "domain": domain,
        "promise_type": "identity_style" if domain == "identity" else "career_signature",
        "strength": confidence,
        "confidence": confidence,
        "confidence_tier": confidence_tier,
        "chart_facts_match": True,
        "technical_anchors": ["Test anchor"],
        "source_evidence_ids": [f"test:{family}:1"],
        "evidence_trace": {
            "primitive_facts": {"placements": [{"planet": "Sun", "sign": "Aries", "house": 1}]},
            "discovery_routes": [family],
            "family_inputs": ["test_input"],
            "subtype_inputs": ["test_subtype"],
        },
        "direct_meaning": "Test composed semantic candidate.",
        "lived_scene": lived_scene,
        "lived_scene_atoms": ["bir şeyi göstermeden önce durman"],
        "gift": "Test gift.",
        "inner_tension": "Test tension.",
        "growth_direction": "Test growth.",
        "domain_reason": list(domain_reason or ["Test route"]),
        "public_job": public_job,
        "shadow_or_friction": "Test tension.",
        "voice_seeds": ["Test composed semantic candidate."],
        "avoid_phrases": [],
        "source_category_ids": [packet_id],
        "source_thread_ids": [],
        "source_section_ids": [packet_id],
        "projection_hints": {"priority": confidence, "surfaces": ["debug_only"]},
        "scoring_breakdown": {"test_confidence": confidence},
        "matched_archetypes": [],
        "public_eligibility": {
            "debug_eligible": True,
            "detail_eligible": False,
            "public_support_eligible": False,
            "public_main_eligible": False,
            "reason_codes": ["test_debug_only"],
        },
        "meta": {
            "source_type": "composed_semantic",
            "v0_9_composed": True,
            "v0_9_family": family,
            "debug_only": True,
            "non_public_discovery": True,
            "public_eligibility": {
                "debug_eligible": True,
                "detail_eligible": False,
                "public_support_eligible": False,
                "public_main_eligible": False,
            },
            "domain_reason": list(domain_reason or ["Test route"]),
            "lived_scene_atoms": ["bir şeyi göstermeden önce durman"],
        },
    }


def test_natal_promise_cluster_plan_istanbul_golden(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")
    response = _istanbul_response()
    public = build_public_natal_view(response, locale="tr", include_debug=True, include_full_profile=True)
    plan = public["profile_v8_projection_v1"]["traceability"]["natal_promise_cluster_plan_v1"]

    focus_tiers = {item["domain"]: item["tier"] for item in plan["focus_map"]}
    assert focus_tiers["identity"] == "strong"
    assert focus_tiers["mind"] in {"medium_strong", "strong"}
    assert focus_tiers["relationship"] in {"medium_strong", "strong"}
    assert focus_tiers["career"] == "strong"

    candidate_ids = {packet["id"] for packet in plan["candidate_packets"]}
    assert "moon_trine_venus_emotional_warmth_chart_exact" in candidate_ids
    assert "saturn_sextile_uranus_structured_originality_chart_exact" in candidate_ids
    assert "venus_sagittarius_12h_hidden_expansive_love_chart_exact" in candidate_ids

    venus_memberships = []
    for cluster in plan["clusters"]:
        for member in cluster["packet_members"]:
            if member["packet_id"] == "venus_sagittarius_12h_hidden_expansive_love_chart_exact":
                venus_memberships.append((cluster["domain_family"], member["cluster_role"]))
    assert ("career", "primary_anchor") in venus_memberships or ("career", "secondary_anchor") in venus_memberships
    assert any(
        domain_family == "relationship" and role in {"secondary_anchor", "modifier"}
        for domain_family, role in venus_memberships
    )

    public_main_ids = plan["surface_plan"]["public_main_cluster_ids"]
    public_support_ids = plan["surface_plan"]["public_support_cluster_ids"]
    detail_ids = plan["surface_plan"]["detail_cluster_ids"]
    assert 5 <= len(public_main_ids) <= 6
    assert "relationship_attachment_architecture" in public_main_ids or "relationship_affection_gift" in public_main_ids
    assert "relationship_hidden_private_love_pattern" not in public_main_ids
    assert "mind_structured_originality" in public_main_ids
    assert "identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact" not in public_main_ids
    assert "identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact" in detail_ids
    assert detail_ids

    for suppression in plan["suppressed_packets"]:
        keep_for = set(suppression["keep_for"])
        assert {"detail", "debug", "transit_activation"} <= keep_for

    assert len(public_main_ids) <= 7

    if focus_tiers["identity"] == "strong":
        identity_clusters = [
            cluster["id"]
            for cluster in plan["clusters"]
            if cluster["domain_family"] == "identity"
        ]
        surfaced = set(public_main_ids) | set(public_support_ids) | set(detail_ids)
        assert any(cluster_id in surfaced for cluster_id in identity_clusters)

    projection = public["profile_v8_projection_v1"]
    hero_trace = str(projection["hero"]["trace"]["node_id"])
    assert hero_trace.startswith("promise::")
    assert "relationship" not in hero_trace
    assert any(token in hero_trace for token in ("mind", "saturn", "identity", "capricorn"))
    for anchor_state in plan["anchor_usage"]:
        if not anchor_state["chart_defining_override"]:
            assert anchor_state["public_main_explicit_uses"] <= anchor_state["explicit_use_budget"]


def test_natal_promise_cluster_plan_source_type_distribution_tracks_registry_legacy_and_generic() -> None:
    plan = build_natal_promise_cluster_plan_v1(
        [
            _packet(
                packet_id="identity_self_construction",
                domain="identity",
                promise_type="behavior_reflex",
                strength=0.92,
                direct="Kimlik hattın net çalışıyor.",
                scene="Dışarıda çizgini koruyorsun.",
                gift="Omurganı koruyabilmek.",
                anchors=["Yükselen Aslan", "1th house ruler route"],
                evidence_ids=["house:1->ruler:Sun->house:11"],
                source_type="exact_registry",
                matched_archetypes=["identity_self_construction"],
            ),
            _packet(
                packet_id="career_career_visibility",
                domain="career",
                promise_type="career_signature",
                strength=0.88,
                direct="Kariyer görünürlüğü sende çalışıyor.",
                scene="İşin görünür olmasını önemsiyorsun.",
                gift="Dışarıda ciddiye alınmak.",
                anchors=["MC Oğlak"],
                evidence_ids=["house:10:cusp_sign:Capricorn"],
                source_type="generic_fallback",
            ),
            _packet(
                packet_id="legacy_thread_packet",
                domain="mind",
                promise_type="mind_style",
                strength=0.8,
                direct="Zihnin anlatım üzerinden açılıyor.",
                scene="Bir fikri anlatırken netleşiyorsun.",
                gift="Düşünceyi dile çevirebilmek.",
                anchors=["Merkür 3. ev"],
                evidence_ids=["section:mind_system"],
                source_type="legacy_graph",
            ),
        ],
        locale="tr",
    )
    metrics = plan["meta"]["audit_metrics"]
    candidate_dist = metrics["candidate_source_type_distribution"]
    public_main_dist = metrics["public_main_source_type_distribution"]
    cluster_lookup = {cluster["main_packet_id"]: cluster for cluster in plan["clusters"]}

    assert candidate_dist["exact_registry"] == 1
    assert candidate_dist["generic_fallback"] == 1
    assert candidate_dist["legacy_graph"] == 1
    assert candidate_dist["composed_semantic"] == 0
    assert candidate_dist["discovery_scaffold"] == 0

    assert cluster_lookup["career_career_visibility"]["source_type"] == "generic_fallback"
    assert cluster_lookup["identity_self_construction"]["source_type"] == "exact_registry"
    assert public_main_dist["composed_semantic"] == 0


def test_natal_promise_cluster_plan_v0_9a_composed_candidates_stay_debug_only_and_expose_metrics(
    monkeypatch,
) -> None:
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")

    response = _istanbul_1994_response()
    public = build_public_natal_view(response, locale="tr", include_debug=True, include_full_profile=True)
    plan = public["profile_v8_projection_v1"]["traceability"]["natal_promise_cluster_plan_v1"]
    packet_lookup = {
        str(packet.get("id") or "").strip(): packet
        for packet in plan["candidate_packets"]
    }
    suppressed_lookup = {
        str(item.get("packet_id") or "").strip(): item
        for item in plan["suppressed_packets"]
    }
    metrics = plan["meta"]["audit_metrics"]

    identity = packet_lookup["composed_identity_route_v0_9a"]
    career = packet_lookup["composed_career_route_v0_9a"]
    for packet in (identity, career):
        assert packet["source_type"] == "composed_semantic"
        assert packet["chart_facts_match"] is True
        assert packet["public_eligibility"]["debug_eligible"] is True
        assert packet["public_eligibility"]["detail_eligible"] is False
        assert packet["public_eligibility"]["public_support_eligible"] is False
        assert packet["public_eligibility"]["public_main_eligible"] is False
        keep_for = set(suppressed_lookup[packet["id"]]["keep_for"])
        assert keep_for == {"debug"}

    assert metrics["composed_candidate_count"] == 2
    assert metrics["candidate_source_type_distribution"]["composed_semantic"] == 2
    assert metrics["composed_candidate_family_distribution"] == {
        "identity_route": 1,
        "career_route": 1,
    }
    assert metrics["composed_candidate_confidence_distribution"]["high"] + metrics["composed_candidate_confidence_distribution"]["medium"] >= 2
    assert metrics["composed_candidate_public_eligibility_distribution"]["debug_only"] == 2
    assert metrics["composed_candidate_public_eligibility_distribution"]["public_main_eligible"] == 0
    assert all(
        item["packet_id"] in {"composed_identity_route_v0_9a", "composed_career_route_v0_9a"}
        for item in metrics["composed_vs_generic_fallback_opportunities"]
    ) or metrics["composed_vs_generic_fallback_opportunities"] == []
    assert "composed_identity_route_v0_9a" in set(plan["surface_plan"]["debug_packet_ids"])
    assert "composed_career_route_v0_9a" in set(plan["surface_plan"]["debug_packet_ids"])
    surfaced = (
        set(plan["surface_plan"]["public_main_cluster_ids"])
        | set(plan["surface_plan"]["public_support_cluster_ids"])
        | set(plan["surface_plan"]["detail_cluster_ids"])
    )
    assert not any("composed_identity_route_v0_9a" in cluster_id for cluster_id in surfaced)
    assert not any("composed_career_route_v0_9a" in cluster_id for cluster_id in surfaced)


def test_natal_promise_cluster_plan_v0_9a_career_raw_generic_owner_is_high_priority_opportunity() -> None:
    plan = build_natal_promise_cluster_plan_v1(
        [
            _packet(
                packet_id="career_career_visibility",
                domain="career",
                promise_type="career_signature",
                strength=0.86,
                direct="Kariyer görünürlüğü sende çalışıyor.",
                scene="İşte görünür olmak istiyorsun.",
                gift="Dışarıda görünmek.",
                anchors=["MC Oğlak"],
                evidence_ids=["house:10:cusp_sign:Capricorn"],
                source_type="generic_fallback",
            ),
            _composed_packet(
                packet_id="composed_career_route_v0_9a",
                family="career_route",
                domain="career",
                confidence=0.78,
                confidence_tier="medium",
                lived_scene="Bir işi göstermeden önce uzun süre hazırlayıp sonra dışarıda net bir rol alman.",
                domain_reason=["MC route", "MC ruler involved", "10H planet"],
            ),
        ],
        locale="tr",
    )
    metrics = plan["meta"]["audit_metrics"]
    opportunities = metrics["composed_vs_generic_fallback_opportunities"]

    assert metrics["composed_opportunity_severity_distribution"]["high_priority_opportunity"] == 1
    assert metrics["composed_opportunity_severity_distribution"]["medium_priority_opportunity"] == 0
    assert metrics["composed_opportunity_severity_distribution"]["debug_observation_only"] == 0
    assert len(opportunities) == 1
    assert opportunities[0]["packet_id"] == "composed_career_route_v0_9a"
    assert opportunities[0]["severity"] == "high_priority_opportunity"
    assert opportunities[0]["current_owner_quality"] == ["raw_generic_fallback"]
    assert "career_visibility" in " ".join(opportunities[0]["target_generic_cluster_ids"]).lower() or opportunities[0]["target_main_packet_ids"] == ["career_career_visibility"]


def test_natal_promise_cluster_plan_v0_9a_identity_chart_specific_owner_stays_debug_observation() -> None:
    plan = build_natal_promise_cluster_plan_v1(
        [
            _packet(
                packet_id="identity_identity_like_sun_aries_12h_hidden_private_fire_chart_exact",
                domain="identity",
                promise_type="behavior_reflex",
                strength=0.9,
                direct="Kimlik hattın içerde olgunlaşan bir ateş taşıyor.",
                scene="Kendini göstermeden önce içerde uzun süre yönünü toplayıp sonra net bir duruş alıyorsun.",
                gift="İçerde olgunlaşan netlik.",
                anchors=["Sun Aries 12H"],
                evidence_ids=["planet:Sun:sign:Aries:house:12"],
                source_type="generic_fallback",
            ),
            _composed_packet(
                packet_id="composed_identity_route_v0_9a",
                family="identity_route",
                domain="identity",
                confidence=0.82,
                confidence_tier="high",
                lived_scene="Kendini göstermeden önce içerde toparlanıp sonra duruşunu netleştirmen.",
                domain_reason=["ASC route", "chart ruler route", "Sun identity anchor"],
            ),
        ],
        locale="tr",
    )
    metrics = plan["meta"]["audit_metrics"]

    assert metrics["composed_vs_generic_fallback_opportunities"] == []
    assert metrics["composed_opportunity_severity_distribution"]["high_priority_opportunity"] == 0
    assert metrics["composed_opportunity_severity_distribution"]["medium_priority_opportunity"] == 0
    assert metrics["composed_opportunity_severity_distribution"]["debug_observation_only"] == 1
    assert len(metrics["composed_debug_observations"]) == 1
    observation = metrics["composed_debug_observations"][0]
    assert observation["packet_id"] == "composed_identity_route_v0_9a"
    assert observation["severity"] == "debug_observation_only"
    assert observation["current_owner_quality"] == ["cluster_specific_fallback"]
    assert observation["target_main_packet_ids"] == ["identity_identity_like_sun_aries_12h_hidden_private_fire_chart_exact"]


def test_natal_promise_cluster_plan_synthetic_multi_domain_case() -> None:
    packets = [
        _packet(
            packet_id="identity_self_construction",
            domain="identity",
            promise_type="behavior_reflex",
            strength=0.93,
            direct="Dışarıda toparlı görünmek sende kimlik kurucu bir refleks.",
            scene="Zor anlarda önce kendini toplar ve çizgini korursun.",
            gift="Kriz anında bile omurganı korumak.",
            anchors=["Yükselen Oğlak", "1th house ruler route"],
            evidence_ids=["house:1->ruler:Saturn->house:3"],
        ),
        _packet(
            packet_id="mind_structured_originality",
            domain="mind",
            promise_type="mind_style",
            strength=0.95,
            direct="Özgün fikri çalışır hale getiren bir zihnin var.",
            scene="Yeni bir fikri hızlıca sistem kurup çalıştırırsın.",
            gift="Yenilikle yapıyı aynı anda tutmak.",
            anchors=["Saturn sextile Uranus", "Satürn 3. ev"],
            evidence_ids=["Saturn:Uranus:sextile", "house:3->ruler:Jupiter->house:1"],
        ),
        _packet(
            packet_id="relationship_attachment_architecture",
            domain="relationship",
            promise_type="need",
            strength=0.9,
            direct="Yakınlık sende güven ve derinlik eşiğiyle açılıyor.",
            scene="Birine açılmadan önce önce güvenin gerçekten oturmasını beklersin.",
            gift="Kolay bağ değil, derin bağ kurmak.",
            anchors=["7th house ruler route", "Ay 8. ev"],
            evidence_ids=["house:7->ruler:Moon->house:8"],
        ),
        _packet(
            packet_id="relationship_affection_gift",
            domain="relationship",
            promise_type="love_style",
            strength=0.88,
            direct="Sevdiğin kişiyi yumuşatıp güzelleştirmek istiyorsun.",
            scene="Gergin ortamı sıcaklıkla yumuşatmak senin sevgi dilin olabilir.",
            gift="Şefkatle iyi gelmek.",
            anchors=["Moon trine Venus"],
            evidence_ids=["Moon:Venus:trine"],
        ),
        _packet(
            packet_id="relationship_hidden_private_love",
            domain="relationship",
            promise_type="love_style",
            strength=0.82,
            direct="Sevgi sende önce içeride ve sessizce olgunlaşıyor.",
            scene="Duygunu dışarı açmadan önce kendi içinde uzun süre taşıyabilirsin.",
            gift="İnce ve derin sevgi bağı kurmak.",
            anchors=["Venüs 12. ev", "Yay"],
            evidence_ids=["house:10->ruler:Venus->house:12"],
        ),
        _packet(
            packet_id="career_duplicate_main",
            domain="career",
            promise_type="career_signature",
            strength=0.87,
            direct="Görünürlük sende önce içeride olgunlaşıyor.",
            scene="Bir işi göstermeden önce uzun süre rafine etmek istersin.",
            gift="Hazırlıkta kalite toplamak.",
            anchors=["Venüs 12. ev", "MC Terazi"],
            evidence_ids=["house:10->ruler:Venus->house:12", "Jupiter:Fortune:trine"],
        ),
        _packet(
            packet_id="career_duplicate_weaker",
            domain="career",
            promise_type="career_signature",
            strength=0.72,
            direct="Bir işi göstermeden önce içerde uzun süre bekletiyorsun.",
            scene="Bir işi göstermeden önce uzun süre rafine etmek istersin.",
            gift="Hazırlıkta sakinlik bulmak.",
            anchors=["Venüs 12. ev", "MC Terazi"],
            evidence_ids=["house:10->ruler:Venus->house:12"],
        ),
        _packet(
            packet_id="career_distinct_builder",
            domain="career",
            promise_type="wound_to_gift",
            strength=0.84,
            direct="Görünür olma hassasiyetini zamanla sese çevirebilirsin.",
            scene="Sahneye çıkmadan önce kusuru kapatmak için fazladan hazırlanırsın.",
            gift="Hassasiyeti başkalarına alan açan sese çevirmek.",
            anchors=["Chiron conjunct MC", "Saturn sextile Uranus"],
            evidence_ids=["Chiron:MC:conjunction", "Saturn:Uranus:sextile"],
        ),
    ]

    plan = build_natal_promise_cluster_plan_v1(packets)
    suppressed_lookup = {item["packet_id"]: item for item in plan["suppressed_packets"]}

    assert "career_duplicate_weaker" in suppressed_lookup
    assert {"detail", "debug", "transit_activation"} <= set(suppressed_lookup["career_duplicate_weaker"]["keep_for"])
    assert "mind_structured_originality" in plan["surface_plan"]["public_main_cluster_ids"]
    assert "relationship_attachment_architecture" in plan["surface_plan"]["public_main_cluster_ids"]
    assert "relationship_hidden_private_love_pattern" in plan["surface_plan"]["detail_cluster_ids"]
    assert "career_distinct_builder" not in suppressed_lookup

    anchor_state = next(
        item for item in plan["anchor_usage"] if item["anchor_id"] == "saturn sextile uranus"
    )
    assert len(anchor_state["cluster_ids"]) >= 2
    assert anchor_state["public_main_explicit_uses"] <= anchor_state["explicit_use_budget"]

    assert len(plan["surface_plan"]["public_main_cluster_ids"]) <= 7
    assert len(plan["surface_plan"]["detail_cluster_ids"]) >= 1
    assert {
        packet["id"]
        for packet in packets
    } <= set(plan["surface_plan"]["debug_packet_ids"])


def test_natal_promise_cluster_plan_v0_9a_does_not_override_exact_registry_public_clusters(
    monkeypatch,
) -> None:
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")

    response = _istanbul_response()
    baseline_public = build_public_natal_view(response, locale="tr", include_debug=True, include_full_profile=True)
    baseline_plan = baseline_public["profile_v8_projection_v1"]["traceability"]["natal_promise_cluster_plan_v1"]

    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    composed_public = build_public_natal_view(response, locale="tr", include_debug=True, include_full_profile=True)
    composed_plan = composed_public["profile_v8_projection_v1"]["traceability"]["natal_promise_cluster_plan_v1"]

    assert baseline_plan["surface_plan"]["public_main_cluster_ids"] == composed_plan["surface_plan"]["public_main_cluster_ids"]
    assert baseline_plan["surface_plan"]["public_support_cluster_ids"] == composed_plan["surface_plan"]["public_support_cluster_ids"]
    assert baseline_plan["surface_plan"]["detail_cluster_ids"] == composed_plan["surface_plan"]["detail_cluster_ids"]
    assert composed_plan["meta"]["audit_metrics"]["candidate_source_type_distribution"]["composed_semantic"] >= 1


def test_natal_promise_cluster_plan_2020_istanbul_v0_4_overlay_surfaces_new_domains(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")
    response = _istanbul_2020_response()
    public = build_public_natal_view(response, locale="tr", include_debug=True, include_full_profile=True)
    plan = public["profile_v8_projection_v1"]["traceability"]["natal_promise_cluster_plan_v1"]

    candidate_ids = {packet["id"] for packet in plan["candidate_packets"]}
    assert len(plan["candidate_packets"]) >= 10
    assert "gemini_asc_venus_1h_social_relational_presence_chart_exact" in candidate_ids
    assert "sun_aries_12h_hidden_private_fire_chart_exact" in candidate_ids
    assert "aquarius_mc_mars_conjunct_mc_visible_freedom_drive" in candidate_ids
    assert "venus_trine_mars_relational_attraction_signal_chart_exact" in candidate_ids
    assert "venus_trine_saturn_trust_bond_chart_exact" in candidate_ids
    assert "moon_scorpio_6h_emotional_routine_sensitivity_chart_exact" in candidate_ids
    assert "mercury_sextile_9h_capricorn_aquarius_intellectual_authority_chart_exact" in candidate_ids

    focus_tiers = {item["domain"]: item["tier"] for item in plan["focus_map"]}
    assert focus_tiers["career"] == "strong"
    assert focus_tiers["mind"] in {"medium_strong", "strong"}
    assert focus_tiers["identity"] in {"medium_strong", "strong"}
    assert focus_tiers["relationship"] in {"supporting", "medium_strong", "strong"}

    public_main_ids = set(plan["surface_plan"]["public_main_cluster_ids"])
    detail_ids = set(plan["surface_plan"]["detail_cluster_ids"])
    assert any("identity" in cluster_id for cluster_id in public_main_ids)
    assert any("career" in cluster_id for cluster_id in public_main_ids)
    assert any("mind" in cluster_id for cluster_id in public_main_ids)
    assert any("relationship" in cluster_id for cluster_id in public_main_ids)
    relationship_main_ids = [cluster_id for cluster_id in public_main_ids if "relationship" in cluster_id]
    assert relationship_main_ids
    assert any(
        "trust_bond" in cluster_id or "attraction_signal" in cluster_id
        for cluster_id in relationship_main_ids
    ), f"2020 relationship public_main should be specific, not generic: {relationship_main_ids}"
    assert not any("relationship_relationships" in cluster_id for cluster_id in relationship_main_ids)
    assert any("mercury_sextile_9h_capricorn_aquarius_intellectual_authority" in cluster_id for cluster_id in detail_ids)
    assert any(
        "attraction_signal" in cluster_id
        or "trust_bond" in cluster_id
        for cluster_id in detail_ids
    )
    assert any("sun_aries_12h_hidden_private_fire" in cluster_id for cluster_id in detail_ids)
    assert any("emotional_routine_sensitivity" in cluster_id for cluster_id in detail_ids)
    assert any("relationship_relationships" in cluster_id for cluster_id in detail_ids)

    projection = public["profile_v8_projection_v1"]
    hero_node = str(projection["hero"]["trace"]["node_id"])
    identity_axis_node = str(projection["identity_axis"]["trace"]["node_id"])
    assert "gemini_asc_venus_1h_social_relational_presence" in hero_node
    assert "sun_aries_12h_hidden_private_fire" in identity_axis_node
    assert hero_node != identity_axis_node


def test_natal_promise_cluster_plan_istanbul_1997_truthfulness_guards_block_false_saturn_uranus_packets(
    monkeypatch,
) -> None:
    monkeypatch.setenv("SE_EPHE_PATH", str(Path("swisseph/ephe").resolve()))
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")

    from app.api.routes.natal_interpretation import NatalInterpretationRequest, interpret_natal_chart_ui

    response = interpret_natal_chart_ui(
        NatalInterpretationRequest(
            birth_date="1997-01-21",
            birth_time="10:30",
            birth_place="Istanbul, TR",
            locale="tr",
            summary_only=False,
            include_full_profile=True,
        ),
        debug=False,
        include_debug=True,
        profile_engine=None,
    )
    public = response["public"]
    projection = public["profile_narrative_projection_v1"]
    v8 = public["profile_v8_projection_v1"]
    plan = v8["traceability"]["natal_promise_cluster_plan_v1"]

    candidate_lookup = {
        str(packet.get("id") or "").strip(): packet
        for packet in plan["candidate_packets"]
    }
    bad_packet_ids = {
        "saturn_sextile_uranus_structured_originality_chart_exact",
        "saturn_sextile_uranus_structured_originality_identity_chart_exact",
    }
    for packet_id in bad_packet_ids:
        assert candidate_lookup[packet_id]["chart_facts_match"] is False

    suppressed_lookup = {
        str(item.get("packet_id") or "").strip(): item
        for item in plan["suppressed_packets"]
    }
    for packet_id in bad_packet_ids:
        keep_for = set(suppressed_lookup[packet_id]["keep_for"])
        assert {"debug", "transit_activation"} <= keep_for
        assert "detail" not in keep_for
        assert "public_support" not in keep_for

    assert bad_packet_ids <= set(plan["surface_plan"]["debug_packet_ids"])

    surfaced_node_ids = {
        str(block.get("node_id") or "").strip()
        for block in projection["profile_public"]["blocks"]
    }
    surfaced_node_ids |= {
        str((v8.get("hero") or {}).get("node_id") or "").strip(),
        str((v8.get("identity_axis") or {}).get("node_id") or "").strip(),
        *(
            str(item.get("node_id") or "").strip()
            for item in (v8.get("insight_strip") or [])
        ),
        *(
            str(item.get("node_id") or "").strip()
            for item in (v8.get("differentiators") or [])
        ),
    }
    assert "promise::saturn_sextile_uranus_structured_originality_chart_exact" not in surfaced_node_ids
    assert "promise::saturn_sextile_uranus_structured_originality_identity_chart_exact" not in surfaced_node_ids

    public_text = "\n".join(
        str(value or "")
        for block in (projection["profile_public"]["blocks"] or [])
        for value in (
            block.get("headline"),
            block.get("teaser"),
            block.get("body"),
            block.get("micro"),
        )
    )
    public_text += "\n" + "\n".join(
        str(value or "")
        for section in [
            v8.get("hero") or {},
            v8.get("identity_axis") or {},
            *(v8.get("insight_strip") or []),
            *(v8.get("differentiators") or []),
        ]
        for value in (
            section.get("headline"),
            section.get("summary"),
            section.get("title"),
            section.get("subtitle"),
            section.get("body"),
        )
    )
    for bad_phrase in (
        "Yükselen Oğlak",
        "Satürn 3. ev",
        "Uranüs 1. ev",
        "pressure vs resilience",
    ):
        assert bad_phrase not in public_text


def test_natal_promise_cluster_plan_istanbul_1997_v0_8_overlay_surfaces_axis_and_roots(
    monkeypatch,
) -> None:
    monkeypatch.setenv("SE_EPHE_PATH", str(Path("swisseph/ephe").resolve()))
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")

    from app.api.routes.natal_interpretation import NatalInterpretationRequest, interpret_natal_chart_ui

    response = interpret_natal_chart_ui(
        NatalInterpretationRequest(
            birth_date="1997-01-21",
            birth_time="10:30",
            birth_place="Istanbul, TR",
            locale="tr",
            summary_only=False,
            include_full_profile=True,
        ),
        debug=False,
        include_debug=True,
        profile_engine=None,
    )
    public = response["public"]
    projection = public["profile_narrative_projection_v1"]
    v8 = public["profile_v8_projection_v1"]
    plan = v8["traceability"]["natal_promise_cluster_plan_v1"]

    candidate_ids = {packet["id"] for packet in plan["candidate_packets"]}
    assert len(plan["candidate_packets"]) >= 20
    assert "aries_asc_mars_libra_6h_action_through_balance_chart_exact" in candidate_ids
    assert "mars_opposite_saturn_action_restraint_inner_brake_chart_exact" in candidate_ids
    assert "saturn_aries_12h_private_pressure_hidden_self_control_chart_exact" in candidate_ids
    assert "moon_cancer_ic_home_security_roots_chart_exact" in candidate_ids
    assert "mercury_capricorn_mc_public_voice_strategic_mind_chart_exact" in candidate_ids
    assert any(packet_id.startswith("moon_mercury_ic_mc_private_security_public_voice_axis") for packet_id in candidate_ids)
    assert "sun_aquarius_11h_collective_identity_future_networks_chart_exact" in candidate_ids
    assert "aquarius_11h_future_collective_signal_chart_exact" in candidate_ids
    assert "capricorn_10h_mercury_venus_neptune_public_style_responsibility_chart_exact" in candidate_ids
    assert "libra_dsc_chiron_scorpio_7h_harmony_wound_depth_chart_exact" in candidate_ids
    assert "venus_capricorn_10h_public_love_style_responsibility_chart_exact" in candidate_ids

    focus_tiers = {item["domain"]: item["tier"] for item in plan["focus_map"]}
    assert focus_tiers["home_family"] == "strong"
    assert focus_tiers["career"] == "strong"
    assert focus_tiers["axis_tension"] == "strong"
    assert focus_tiers["community"] in {"medium_strong", "strong"}
    assert focus_tiers["relationship"] in {"medium_strong", "strong"}
    assert focus_tiers["action"] in {"medium_strong", "strong"}
    assert focus_tiers["inner_world"] in {"supporting", "medium_strong", "strong"}

    public_main_ids = set(plan["surface_plan"]["public_main_cluster_ids"])
    public_support_ids = set(plan["surface_plan"]["public_support_cluster_ids"])
    detail_ids = set(plan["surface_plan"]["detail_cluster_ids"])
    assert {
        "home_family_home_security_roots",
        "career_public_voice_strategic_mind",
        "axis_tension_private_security_public_voice_axis",
        "action_action_through_balance",
        "community_collective_identity",
        "relationship_harmony_wound_depth",
    } <= public_main_ids
    assert public_support_ids
    assert detail_ids
    assert "inner_world_private_pressure" in public_support_ids | detail_ids

    surfaced_node_ids = {
        str(block.get("node_id") or "").strip()
        for block in projection["profile_public"]["blocks"]
    }
    surfaced_node_ids |= {
        str((v8.get("hero") or {}).get("node_id") or "").strip(),
        str((v8.get("identity_axis") or {}).get("node_id") or "").strip(),
        *(
            str(item.get("node_id") or "").strip()
            for item in (v8.get("insight_strip") or [])
        ),
        *(
            str(item.get("node_id") or "").strip()
            for item in (v8.get("differentiators") or [])
        ),
    }
    assert "promise::saturn_sextile_uranus_structured_originality_chart_exact" not in surfaced_node_ids
    assert "promise::saturn_sextile_uranus_structured_originality_identity_chart_exact" not in surfaced_node_ids

    public_text = "\n".join(
        str(value or "")
        for block in (projection["profile_public"]["blocks"] or [])
        for value in (
            block.get("headline"),
            block.get("teaser"),
            block.get("body"),
            block.get("micro"),
        )
    )
    public_text += "\n" + "\n".join(
        str(value or "")
        for section in [
            v8.get("hero") or {},
            v8.get("identity_axis") or {},
            *(v8.get("insight_strip") or []),
            *(v8.get("differentiators") or []),
        ]
        for value in (
            section.get("headline"),
            section.get("summary"),
            section.get("title"),
            section.get("subtitle"),
            section.get("body"),
        )
    )
    for bad_phrase in (
        "Yükselen Oğlak",
        "Satürn 3. ev",
        "Uranüs 1. ev",
        "pressure vs resilience",
    ):
        assert bad_phrase not in public_text


def test_natal_promise_cluster_plan_istanbul_1997_copy_polish_keeps_axis_surfaces_clean(
    monkeypatch,
) -> None:
    monkeypatch.setenv("SE_EPHE_PATH", str(Path("swisseph/ephe").resolve()))
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")

    from app.api.routes.natal_interpretation import NatalInterpretationRequest, interpret_natal_chart_ui

    response = interpret_natal_chart_ui(
        NatalInterpretationRequest(
            birth_date="1997-01-21",
            birth_time="10:30",
            birth_place="Istanbul, TR",
            locale="tr",
            summary_only=False,
            include_full_profile=True,
        ),
        debug=False,
        include_debug=True,
        profile_engine=None,
    )
    public = response["public"]
    profile_public = public["profile_narrative_projection_v1"]["profile_public"]
    v8 = public["profile_v8_projection_v1"]

    core_blocks = list(profile_public.get("core_blocks") or [])
    extra_blocks = list(profile_public.get("extra_blocks") or [])
    blocks_by_node_id = {
        str(block.get("node_id") or "").strip(): block
        for block in [*core_blocks, *extra_blocks]
    }

    axis_core = blocks_by_node_id["promise::moon_mercury_ic_mc_private_security_public_voice_axis"]
    assert axis_core["chips"] == ["İçgörü", "Ay–Merkür aksı", "IC/MC hattı"]
    axis_chip_blob = " ".join(str(chip or "").lower() for chip in axis_core["chips"])
    for forbidden in ("venüs", "7. ev", "dsc", "terazi"):
        assert forbidden not in axis_chip_blob, axis_core["chips"]

    identity_axis_body = str(v8["identity_axis"].get("body") or "")
    assert "Bazen de." not in identity_axis_body
    assert "bazen de." not in identity_axis_body

    differentiators = list(v8.get("differentiators") or [])
    diff_by_node_id = {
        str(item.get("node_id") or "").strip(): item
        for item in differentiators
    }

    axis_aux = diff_by_node_id["promise::moon_mercury_ic_mc_private_security_public_voice_axis_aux"]
    assert axis_aux["headline"] == "İçeride güvende hissettiğin yer, dışarıda kurduğun sözü etkileyebilir."
    assert str(axis_aux.get("body") or "").startswith(
        "Ay'ının IC'ye, Merkür'ünün de MC'ye yakın çalışması, özel alanla dış rol arasında güçlü bir eksen kuruyor."
    )

    core_headlines = {
        str(block.get("headline") or "").strip().lower()
        for block in core_blocks
        if str(block.get("headline") or "").strip()
    }
    differentiator_headlines = {
        str(item.get("headline") or "").strip().lower()
        for item in differentiators
        if str(item.get("headline") or "").strip()
    }
    assert not (core_headlines & differentiator_headlines), (
        f"Istanbul 1997 differentiators still duplicate core headlines: "
        f"{core_headlines & differentiator_headlines}"
    )

    public_text = "\n".join(
        str(value or "")
        for block in [*core_blocks, *extra_blocks]
        for value in (
            block.get("headline"),
            block.get("teaser"),
            block.get("body"),
            block.get("micro"),
        )
    )
    public_text += "\n" + "\n".join(
        str(value or "")
        for section in [
            v8.get("hero") or {},
            v8.get("identity_axis") or {},
            *(v8.get("insight_strip") or []),
            *differentiators,
        ]
        for value in (
            section.get("headline"),
            section.get("summary"),
            section.get("title"),
            section.get("subtitle"),
            section.get("body"),
        )
    )
    for bad_phrase in (
        "Moon opposite Mercury",
        "olması de",
        "Bazen de.",
        "bazen de.",
        "Yükselen Oğlak",
        "Satürn 3. ev",
        "Uranüs 1. ev",
        "pressure vs resilience",
        "; Ama",
        "; Hem",
    ):
        assert bad_phrase not in public_text


def test_natal_promise_cluster_plan_izmir_1996_v0_5_overlay_surfaces_hidden_value_and_inner_world(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")
    response = _izmir_1996_response()
    public = build_public_natal_view(response, locale="tr", include_debug=True, include_full_profile=True)
    plan = public["profile_v8_projection_v1"]["traceability"]["natal_promise_cluster_plan_v1"]

    candidate_ids = {packet["id"] for packet in plan["candidate_packets"]}
    assert "taurus_asc_venus_12h_hidden_value_identity_chart_exact" in candidate_ids
    assert "mc_capricorn_ruler_saturn_pisces_12h_invisible_preparation_chart_exact" in candidate_ids
    assert "dsc_scorpio_ruler_mars_pisces_12h_trust_threshold_silent_desire_chart_exact" in candidate_ids
    assert "pisces_12h_stellium_inner_world_saturation_chart_exact" in candidate_ids
    assert "mercury_square_pluto_deep_mind_pressure_chart_exact" in candidate_ids

    focus_tiers = {item["domain"]: item["tier"] for item in plan["focus_map"]}
    assert focus_tiers["identity"] in {"medium_strong", "strong"}
    assert focus_tiers["career"] in {"medium_strong", "strong"}
    assert focus_tiers["relationship"] in {"medium_strong", "strong"}
    assert focus_tiers["mind"] in {"supporting", "medium_strong", "strong"}
    assert focus_tiers["inner_world"] in {"supporting", "medium_strong", "strong"}

    public_main_ids = set(plan["surface_plan"]["public_main_cluster_ids"])
    public_support_ids = set(plan["surface_plan"]["public_support_cluster_ids"])
    detail_ids = set(plan["surface_plan"]["detail_cluster_ids"])
    surfaced = public_main_ids | public_support_ids | detail_ids

    assert any("hidden_value_identity" in cluster_id for cluster_id in public_main_ids)
    assert any("invisible_preparation" in cluster_id for cluster_id in public_main_ids)
    relationship_main_ids = [cluster_id for cluster_id in public_main_ids if cluster_id.startswith("relationship_")]
    assert relationship_main_ids
    assert any(
        "trust_threshold_silent_desire" in cluster_id or "relationship_power_depth" in cluster_id
        for cluster_id in relationship_main_ids
    ), f"expected specific Izmir relationship public_main, got {relationship_main_ids}"
    assert not any("relationship_relationships" in cluster_id for cluster_id in relationship_main_ids)
    assert any(cluster_id.startswith("inner_world_") for cluster_id in surfaced)
    assert any("deep_mind_pressure" in cluster_id for cluster_id in surfaced)

    projection = public["profile_v8_projection_v1"]
    hero_node = str(projection["hero"]["trace"]["node_id"])
    identity_axis_node = str(projection["identity_axis"]["trace"]["node_id"])
    assert "taurus_asc_venus_12h_hidden_value_identity" in hero_node
    assert hero_node != identity_axis_node


def test_natal_promise_cluster_plan_istanbul_1994_v0_7_overlay_surfaces_roots_creativity_and_identity(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")
    response = _istanbul_1994_response()
    public = build_public_natal_view(response, locale="tr", include_debug=True, include_full_profile=True)
    plan = public["profile_v8_projection_v1"]["traceability"]["natal_promise_cluster_plan_v1"]

    candidate_ids = {packet["id"] for packet in plan["candidate_packets"]}
    expected_ids = {
        "leo_asc_sun_cancer_11h_warm_visibility_belonging_chart_exact",
        "pluto_node_scorpio_4h_roots_inner_security_transformation_chart_exact",
        "moon_uranus_neptune_capricorn_5h_structured_imagination_chart_exact",
        "mc_taurus_mars_10h_steady_public_drive_chart_exact",
        "mars_opposite_pluto_public_power_roots_tension_chart_exact",
        "aquarius_dsc_saturn_pisces_7h_freedom_responsibility_sensitivity_chart_exact",
        "venus_leo_12h_hidden_romantic_pride_chart_exact",
        "jupiter_scorpio_3h_deep_speech_psychological_learning_chart_exact",
        "chiron_virgo_1h_visible_sensitivity_self_correction_chart_exact",
    }
    assert expected_ids <= candidate_ids
    assert any(
        packet_id.startswith("sun_mercury_cancer_11h_social_emotional_intelligence")
        for packet_id in candidate_ids
    )

    focus_tiers = {item["domain"]: item["tier"] for item in plan["focus_map"]}
    for domain in ("home_family", "career", "creativity", "identity", "relationship", "mind"):
        assert domain in focus_tiers, f"focus_map missing domain={domain}"
        assert focus_tiers[domain] in {"supporting", "medium_strong", "strong"}

    public_main_ids = set(plan["surface_plan"]["public_main_cluster_ids"])
    public_support_ids = set(plan["surface_plan"]["public_support_cluster_ids"])
    detail_ids = set(plan["surface_plan"]["detail_cluster_ids"])
    surfaced = public_main_ids | public_support_ids | detail_ids

    assert any("roots_inner_security_transformation" in cluster_id for cluster_id in surfaced)
    assert any("steady_public_drive" in cluster_id for cluster_id in public_main_ids)
    assert any("structured_imagination" in cluster_id for cluster_id in public_main_ids)
    assert any("warm_visibility_belonging" in cluster_id for cluster_id in public_main_ids)
    assert any("freedom_responsibility_sensitivity" in cluster_id for cluster_id in public_main_ids)
    assert any("social_emotional_intelligence" in cluster_id for cluster_id in surfaced)
    assert public_support_ids or detail_ids
    assert not public_main_ids <= {
        "mind_mind_like_mind_mind_system",
        "relationship_love_like_relationship_relationships",
        "career_wound_like_career_career_visibility",
    }

    projection = public["profile_v8_projection_v1"]
    hero_node = str(projection["hero"]["trace"]["node_id"])
    identity_axis_node = str(projection["identity_axis"]["trace"]["node_id"])
    assert "leo_asc_sun_cancer_11h_warm_visibility_belonging" in hero_node
    assert hero_node != identity_axis_node


def _adana_artifact_data():
    """Load Adana artifact and extract the build_natal_promise_packets_v1 inputs."""
    path = Path("backend/tests/_artifacts/natal_interpret_full_1998-09-12_07-30_adana_user_compact_debug.json")
    artifact = json.loads(path.read_text())

    def walk(payload, *, key):
        if isinstance(payload, dict):
            if key in payload:
                yield payload[key]
            for value in payload.values():
                yield from walk(value, key=key)
        elif isinstance(payload, list):
            for item in payload:
                yield from walk(item, key=key)

    sections = next(iter(walk(artifact, key="sections_v2")), [])
    threads = next(iter(walk(artifact, key="supporting_threads")), [])
    return {
        "sections": sections,
        "threads": threads,
        "planets": artifact.get("planets") or [],
        "aspects": artifact.get("aspects") or [],
        "metadata": artifact.get("metadata") or {},
        "natal_graph_compact": next(iter(walk(artifact, key="natal_graph_compact")), {}),
        "meta_info": artifact.get("meta_info") or {},
    }


def test_natal_promise_cluster_plan_adana_golden_v0_3_overlay() -> None:
    """v0.3 addendum (Adana golden expected map).

    Adana chart: ASC Libra, Sun/Mercury Virgo 12H, Venus Virgo 11H, Mars Leo 11H,
    Moon Gemini 9H, Saturn Taurus 8H, MC Cancer, Venus-Pluto square,
    Mars-Uranus opposition, Moon-Venus square.
    """
    from app.natal.natal_promise_packets import build_natal_promise_packets_v1

    data = _adana_artifact_data()
    inventory = build_natal_promise_packets_v1(
        sections_v2=data["sections"],
        supporting_threads=data["threads"],
        planets=data["planets"],
        aspects=data["aspects"],
        natal_graph_compact=data["natal_graph_compact"],
        metadata=data["metadata"],
        meta_info=data["meta_info"],
        locale="tr",
        mode="candidate_inventory",
    )
    plan = build_natal_promise_cluster_plan_v1(inventory["packets"])

    candidate_ids = {packet["id"] for packet in inventory["packets"]}

    # v0.3 §17: focus_map must include mind, identity, relationship, career
    # at strong / medium_strong tiers (no domain may collapse to "supporting").
    focus_tiers = {item["domain"]: item["tier"] for item in plan["focus_map"]}
    for domain in ("mind", "identity", "relationship", "career"):
        assert domain in focus_tiers, f"focus_map missing domain={domain}"
        assert focus_tiers[domain] in {"strong", "medium_strong"}, (
            f"Adana {domain} tier dropped to {focus_tiers[domain]}; v0.3 expects strong/medium_strong"
        )

    # v0.3 §17.2: identity cluster must be driven by Libra ASC + Venus chart-ruler
    # / Sun Virgo 12H. Previously Adana had NO identity cluster; this is the
    # explicit fix in the addendum.
    identity_packets_with_chart_facts = {
        packet["id"]
        for packet in inventory["packets"]
        if packet.get("domain") == "identity"
        and packet.get("chart_facts_match") is True
    }
    assert "libra_asc_venus_chart_ruler_chart_exact" in identity_packets_with_chart_facts, (
        f"v0.3 §17.2: Adana identity must surface libra_asc_venus_chart_ruler. "
        f"Got identity packets with chart_facts_match=True: {identity_packets_with_chart_facts}"
    )
    assert "sun_virgo_12h_quiet_inner_self_chart_exact" in candidate_ids, (
        "v0.3 §16.3: Sun Virgo 12H must fire on Adana"
    )

    # v0.3 §17.3: relationship anchors must include Mars-Uranus / Venus-Pluto /
    # Mars Leo 11H. Moon Leo 8H (the wrong relationship cluster on Adana) must
    # NOT have a chart_facts_match=True version in the inventory.
    relationship_anchor_ids = {
        "mars_opposite_uranus_freedom_in_action_chart_exact",
        "venus_square_pluto_intense_love_chart_exact",
        "mars_leo_11h_warm_visible_drive_chart_exact",
        "moon_square_venus_need_affection_friction_chart_exact",
    }
    fired_relationship_anchors = relationship_anchor_ids & candidate_ids
    assert len(fired_relationship_anchors) >= 3, (
        f"v0.3 §17.3 expects at least 3 of Mars-Uranus / Venus-Pluto / Mars Leo 11H / "
        f"Moon-Venus to fire on Adana; got: {fired_relationship_anchors}"
    )

    moon_leo_8h_fired = any(
        packet.get("id", "").startswith("moon_leo_8h_deep_proud_heart")
        and packet.get("chart_facts_match") is not False
        for packet in inventory["packets"]
    )
    assert not moon_leo_8h_fired, (
        "v0.3 §17 non-goals: Moon Leo 8H must not fire on Adana (Moon is in Gemini 9H)"
    )

    # v0.3 §16.5 mind cluster: Moon Gemini 9H + Mercury Virgo 12H must both be
    # available, since Adana's mind story is built on these two anchors.
    assert "moon_gemini_9h_curious_mind_chart_exact" in candidate_ids
    assert "mercury_virgo_12h_private_analytical_mind_chart_exact" in candidate_ids

    # v0.3 §16.15 career: MC Cancer → Moon Gemini 9H teaching voice must fire.
    assert "mc_cancer_moon_gemini_9h_teaching_voice_chart_exact" in candidate_ids

    # Packet ids that encode chart placements must have chart_facts_match=True
    # on Adana when the placement matches (no misleading placement-encoded
    # labels for chart-correct packets).
    for packet in inventory["packets"]:
        if packet.get("id", "").endswith("_chart_exact") and "chart_facts_match" in packet:
            assert packet["chart_facts_match"] is True, (
                f"chart_facts_match should be True for chart-fact-matching packet "
                f"{packet.get('id')}, got {packet.get('chart_facts_match')}"
            )


def test_natal_promise_packets_chart_correctness_filter_drops_misencoded_archetypes() -> None:
    """Placement-encoded registry entries must not bleed voice_seeds into other
    packets via the text-based registry match when the chart does not match
    the encoded placement."""
    from app.natal.natal_promise_packets import build_natal_promise_packets_v1

    data = _adana_artifact_data()
    selected = build_natal_promise_packets_v1(
        sections_v2=data["sections"],
        supporting_threads=data["threads"],
        planets=data["planets"],
        aspects=data["aspects"],
        natal_graph_compact=data["natal_graph_compact"],
        metadata=data["metadata"],
        meta_info=data["meta_info"],
        locale="tr",
        mode="selected",
    )
    # Joined voice_seed surface area
    voice_text = " ".join(
        " ".join(packet.get("voice_seeds") or [])
        for packet in selected["packets"]
    ).lower()
    # The Moon Leo 8H signature voice_seed should never appear on Adana.
    assert "sevgi sende hafif yaşamıyor" not in voice_text, (
        "Moon Leo 8H voice_seed bled into Adana packets despite chart filter"
    )


def test_natal_promise_cluster_plan_adana_relationship_main_is_chart_anchored() -> None:
    """v0.3 regression: Adana's relationship cluster main_packet_id MUST be a
    real relationship-domain archetype (per spec §16.7, §16.11–§16.13).
    Crucially, ``moon_square_mercury_emotion_mind_friction`` is a mind/cognitive
    friction archetype (spec §16.6) and must NEVER appear as the main packet
    (or even cluster into) any ``relationship_*`` cluster.
    """
    from app.natal.natal_promise_packets import build_natal_promise_packets_v1

    data = _adana_artifact_data()
    inventory = build_natal_promise_packets_v1(
        sections_v2=data["sections"],
        supporting_threads=data["threads"],
        planets=data["planets"],
        aspects=data["aspects"],
        natal_graph_compact=data["natal_graph_compact"],
        metadata=data["metadata"],
        meta_info=data["meta_info"],
        locale="tr",
        mode="candidate_inventory",
    )
    plan = build_natal_promise_cluster_plan_v1(inventory["packets"])

    relationship_clusters = [
        cluster for cluster in plan["clusters"]
        if cluster["domain_family"] == "relationship"
    ]
    assert relationship_clusters, "Adana must produce at least one relationship cluster"

    # No relationship cluster may carry the mind-domain ``moon_square_mercury``
    # archetype (in any role: main, support, or member).
    for cluster in relationship_clusters:
        member_ids = {member["packet_id"] for member in cluster["packet_members"]}
        offending = {pid for pid in member_ids if "moon_square_mercury_emotion_mind_friction" in pid}
        assert not offending, (
            f"v0.3 §16.6: ``moon_square_mercury_emotion_mind_friction`` is a "
            f"mind/cognitive archetype and must not appear in relationship "
            f"cluster {cluster['id']}; found {offending}"
        )

    # The relationship cluster that wins a public_main slot must be driven by
    # a spec-listed relationship anchor.
    expected_relationship_mains = {
        "mars_leo_11h_warm_visible_drive_chart_exact",
        "mars_opposite_uranus_freedom_in_action_chart_exact",
        "venus_square_pluto_intense_love_chart_exact",
        "moon_square_venus_need_affection_friction_chart_exact",
        "moon_square_venus_need_affection_friction",
        "mars_leo_11h_warm_visible_drive",
        "mars_opposite_uranus_freedom_in_action",
        "venus_square_pluto_intense_love",
    }
    public_main_ids = set(plan["surface_plan"]["public_main_cluster_ids"])
    cluster_lookup = {cluster["id"]: cluster for cluster in plan["clusters"]}
    relationship_public_main = [
        cluster_lookup[cid] for cid in public_main_ids
        if cluster_lookup.get(cid, {}).get("domain_family") == "relationship"
    ]
    assert relationship_public_main, (
        "Adana must surface at least one relationship cluster in public_main"
    )
    for cluster in relationship_public_main:
        assert cluster["main_packet_id"] in expected_relationship_mains, (
            f"Adana relationship public_main {cluster['id']} resolved to "
            f"main_packet_id={cluster['main_packet_id']}, which is not in the "
            f"spec-listed relationship anchors {expected_relationship_mains}"
        )


def test_adana_aux_anchor_does_not_bleed_across_domain_families() -> None:
    """Adana audit §5 regression: ``moon_square_mercury_emotion_mind_friction_aux``
    is a mind/cognitive friction packet, but when its aux variant was built
    from the relationship section seed it inherited the section's chips (Mars
    11. ev, 7. ev Koç) and detail_blocks (the "Sen ilişkide..." sentence)
    verbatim. The result was an extras card / insight strip whose body opened
    with relationship anchors despite the headline being a Moon-Mercury
    cognitive-friction statement.

    The fix runs a domain-family compatibility filter at packet-build time:
    when the aux's resolved registry family conflicts with the seed section's
    family, cross-domain chips / lived_scene / direct_meaning are stripped
    and replaced with registry-supplied mind-domain content. When the filter
    leaves the aux with no in-domain anchors AND no in-domain body, the aux
    is removed from public surfaces (debug / transit_activation remain).

    Either branch (rendered with mind-domain anchors OR suppressed from
    extras) is acceptable. What MUST NOT happen is a Zihin (mind) extras card
    or insight-strip item carrying relationship-section anchors / body lines.
    """
    from app.natal.natal_promise_packets import build_natal_promise_packets_v1
    from app.meaning.projection_shadow_v1_builder import (
        build_profile_narrative_projection_v1,
        build_profile_v8_projection_v1,
    )

    data = _adana_artifact_data()
    inventory = build_natal_promise_packets_v1(
        sections_v2=data["sections"],
        supporting_threads=data["threads"],
        planets=data["planets"],
        aspects=data["aspects"],
        natal_graph_compact=data["natal_graph_compact"],
        metadata=data["metadata"],
        meta_info=data["meta_info"],
        locale="tr",
        mode="candidate_inventory",
    )
    selected = build_natal_promise_packets_v1(
        sections_v2=data["sections"],
        supporting_threads=data["threads"],
        planets=data["planets"],
        aspects=data["aspects"],
        natal_graph_compact=data["natal_graph_compact"],
        metadata=data["metadata"],
        meta_info=data["meta_info"],
        locale="tr",
        mode="selected",
    )
    plan = build_natal_promise_cluster_plan_v1(inventory["packets"])

    narrative = build_profile_narrative_projection_v1(
        meaning_graph_v1_1={"version": "meaning_graph_v1_1", "nodes": [], "evidence": []},
        natal_promise_packets_v1=selected,
        natal_promise_cluster_plan_v1=plan,
    )
    v8 = build_profile_v8_projection_v1(
        meaning_graph_v1_1={"version": "meaning_graph_v1_1", "nodes": [], "evidence": []},
        natal_promise_packets_v1=selected,
        natal_promise_cluster_plan_v1=plan,
    )

    aux_node_id = "promise::moon_square_mercury_emotion_mind_friction_aux"
    public = narrative.get("profile_public") or {}
    extras = public.get("extra_blocks") or []
    aux_blocks = [b for b in extras if str(b.get("node_id") or "").strip() == aux_node_id]
    insight_strip = v8.get("insight_strip") or []
    aux_strip_items = [item for item in insight_strip if str(item.get("node_id") or "").strip() == aux_node_id]

    # --- A. The aux MUST NOT carry relationship-section chips. ---
    forbidden_chip_tokens = {"mars · 11. ev · aslan", "7. ev koç"}
    for block in aux_blocks:
        chips = [str(chip).strip().lower() for chip in (block.get("chips") or [])]
        leaked = [chip for chip in chips if chip in forbidden_chip_tokens]
        assert not leaked, (
            f"Adana audit §5: extras block for {aux_node_id} leaks relationship "
            f"chips into a mind card. Forbidden chips found: {leaked}. "
            f"Full chip list: {block.get('chips')}"
        )

    # --- B. The aux MUST NOT carry relationship-only body lines. ---
    forbidden_body_phrase = "sen ilişkide sadece biriyle olmak istemiyorsun"
    for block in aux_blocks:
        body = " ".join(str(block.get(field) or "") for field in ("headline", "teaser", "body", "micro")).lower()
        assert forbidden_body_phrase not in body, (
            f"Adana audit §5: extras block for {aux_node_id} reproduces the "
            f"relationship-section sentence \"Sen ilişkide sadece biriyle olmak "
            f"istemiyorsun.\" inside a mind card."
        )

    # --- C. insight_strip subtitle must not carry relationship anchors. ---
    forbidden_subtitle_fragments = (
        "mars'ının 11. evde aslan",
        "7. evinin koç",
        "sen ilişkide sadece biriyle olmak istemiyorsun",
    )
    for item in aux_strip_items:
        subtitle = str(item.get("subtitle") or "").lower()
        for fragment in forbidden_subtitle_fragments:
            assert fragment not in subtitle, (
                f"Adana audit §5: insight_strip item for {aux_node_id} has "
                f"subtitle carrying relationship anchor fragment {fragment!r}. "
                f"Subtitle: {item.get('subtitle')}"
            )

    # --- D. Acceptance: either the aux renders with mind-domain anchors, or
    # it is suppressed entirely from public surfaces. ---
    mind_anchor_tokens = (
        "ay–merkür",
        "moon square mercury",
        "ay-merkür",
        "ay merkür",
        "ay · 9. ev · ikizler",
        "merkür · 12. ev · başak",
        "merkür–venüs",
        "mercury conjunction venus",
    )
    if aux_blocks:
        for block in aux_blocks:
            chip_blob = " ".join(str(c) for c in (block.get("chips") or [])).lower()
            body_blob = str(block.get("body") or "").lower()
            assert any(token in chip_blob or token in body_blob for token in mind_anchor_tokens), (
                f"Adana audit §5: extras block for {aux_node_id} kept its slot "
                f"but contains no mind-domain anchor. chips={block.get('chips')!r}, "
                f"body={block.get('body')[:200]!r}"
            )
    if aux_strip_items:
        for item in aux_strip_items:
            subtitle_blob = str(item.get("subtitle") or "").lower()
            assert any(token in subtitle_blob for token in mind_anchor_tokens), (
                f"Adana audit §5: insight_strip item for {aux_node_id} kept its "
                f"slot but subtitle carries no mind-domain anchor. "
                f"Subtitle: {item.get('subtitle')!r}"
            )

    # --- E. The aux packet must still be reachable for debug / transit
    # activation (per the suppression policy in the audit doc). ---
    debug_ids = set(plan["surface_plan"].get("debug_packet_ids") or [])
    assert "moon_square_mercury_emotion_mind_friction_aux" in debug_ids, (
        "Suppression policy: aux variants filtered out of public surfaces must "
        "remain in debug_packet_ids so debugging / transit_activation can still "
        "discover them."
    )


def test_natal_promise_cluster_plan_v0_6_discovery_marks_mixed_batch_with_debug_only_candidates(
    monkeypatch,
) -> None:
    monkeypatch.setenv("SE_EPHE_PATH", str(Path("swisseph/ephe").resolve()))
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")

    from app.api.routes.natal_interpretation import NatalInterpretationRequest, interpret_natal_chart_ui

    charts = [
        {
            "label": "kutahya_1959",
            "birth_date": "1959-10-21",
            "birth_time": "11:00",
            "birth_place": "Kutahya, TR",
            "birth_latitude": 39.4167,
            "birth_longitude": 29.9833,
            "expected_discovery_ids": {
                "discovery_identity_asc_chart_ruler_sun_composed",
                "discovery_career_mc_ruler_tenth_house_composed",
                "discovery_axis_2h_8h_gap",
            },
            "expected_warnings": {"generic_fallback_public_main", "mixed_chart_undercovered", "support_detail_empty"},
        },
        {
            "label": "izmir_1996_mixed",
            "birth_date": "1996-05-20",
            "birth_time": "00:45",
            "birth_place": "Izmir, TR",
            "birth_latitude": 38.4237,
            "birth_longitude": 27.1428,
            "expected_discovery_ids": {
                "discovery_identity_asc_chart_ruler_sun_composed",
                "discovery_house_5h_concentration_gap",
                "discovery_house_12h_concentration_gap",
                "discovery_axis_2h_8h_gap",
                "discovery_aspect_moon_conjunction_venus_gap",
            },
            "expected_warnings": {"generic_fallback_public_main", "mixed_chart_undercovered", "support_detail_empty"},
        },
        {
            "label": "izmir_2007_mixed",
            "birth_date": "2007-07-19",
            "birth_time": "13:30",
            "birth_place": "Izmir, TR",
            "birth_latitude": 38.4237,
            "birth_longitude": 27.1428,
            "expected_discovery_ids": {
                "discovery_axis_3h_9h_gap",
                "discovery_house_4h_ic_concentration_gap",
                "discovery_aspect_moon_square_pluto_gap",
            },
            "expected_warnings": {"generic_fallback_public_main", "mixed_chart_undercovered"},
        },
        {
            "label": "istanbul_2012_mixed",
            "birth_date": "2012-08-02",
            "birth_time": "13:45",
            "birth_place": "Istanbul, TR",
            "birth_latitude": 41.0082,
            "birth_longitude": 28.9784,
            "expected_discovery_ids": {
                "discovery_axis_3h_9h_gap",
                "discovery_axis_2h_8h_gap",
                "discovery_house_4h_ic_concentration_gap",
                "discovery_mind_mercury_axis_composed",
            },
            "expected_warnings": {"generic_fallback_public_main", "mixed_chart_undercovered", "support_detail_empty"},
        },
    ]

    for chart in charts:
        response = interpret_natal_chart_ui(
            NatalInterpretationRequest(
                birth_date=chart["birth_date"],
                birth_time=chart["birth_time"],
                birth_place=chart["birth_place"],
                birth_latitude=chart["birth_latitude"],
                birth_longitude=chart["birth_longitude"],
                birth_timezone="Europe/Istanbul",
                locale="tr",
                summary_only=False,
                include_full_profile=True,
            ),
            debug=False,
            include_debug=True,
            profile_engine=None,
        )
        plan = response["public"]["profile_v8_projection_v1"]["traceability"]["natal_promise_cluster_plan_v1"]
        packets = plan["candidate_packets"]
        discovery_packets = [
            packet
            for packet in packets
            if isinstance(packet.get("meta"), dict) and packet["meta"].get("v0_6_discovery")
        ]
        discovery_ids = {packet["id"] for packet in discovery_packets}
        warnings = set(plan["meta"]["coverage_warnings"])
        metrics = plan["meta"]["audit_metrics"]
        suppression_lookup = {
            str(item.get("packet_id") or "").strip(): item
            for item in plan["suppressed_packets"]
        }

        assert chart["expected_discovery_ids"] <= discovery_ids, (
            f"{chart['label']} missing discovery ids: {chart['expected_discovery_ids'] - discovery_ids}"
        )
        assert chart["expected_warnings"] <= warnings
        assert metrics["debug_only_discovery_count"] >= len(chart["expected_discovery_ids"])
        assert metrics["missing_domain_flags"] == []
        assert metrics["candidate_count"] >= len(discovery_packets)
        assert metrics["candidate_source_type_distribution"]["composed_semantic"] >= 0
        assert metrics["candidate_source_type_distribution"]["discovery_scaffold"] >= len(chart["expected_discovery_ids"])
        assert "public_main_source_type_distribution" in metrics
        composed_packets = [
            packet
            for packet in packets
            if str(packet.get("source_type") or "").strip() == "composed_semantic"
        ]
        for packet in composed_packets:
            public_eligibility = packet.get("public_eligibility") or {}
            assert public_eligibility.get("public_main_eligible") is False
        for packet in discovery_packets:
            meta = packet["meta"]
            assert packet["source_type"] == "discovery_scaffold"
            assert meta["source_type"] == "discovery_scaffold"
            assert meta["non_public_discovery"] is True
            assert meta["debug_only"] is True
        for packet_id in chart["expected_discovery_ids"]:
            keep_for = set(suppression_lookup[packet_id]["keep_for"])
            assert keep_for == {"debug", "transit_activation"}


def test_v0_9b_composed_candidates_stay_debug_only_in_cluster_plan(monkeypatch) -> None:
    """When v0.9b family flags are on, the resulting composed candidates
    appear in the cluster plan's candidate_packets but their suppression
    must use ``keep_for=["debug"]`` (or include ``"detail"`` only when the
    shared detail-support flag is also on).
    The candidates must not enter ``surface_plan.public_main_cluster_ids``
    or ``surface_plan.public_support_cluster_ids``.
    """
    import os
    from pathlib import Path
    from app.api.routes.natal_interpretation import (
        NatalInterpretationRequest,
        interpret_natal_chart_ui,
    )
    import json

    payload = json.loads(
        (
            Path("backend/tests/_artifacts/natal_batch_audits/natal_50_chart_discovery_metrics.json")
        ).read_text()
    )
    chart_index = {
        str(item.get("chart_id") or "").strip(): dict(item.get("birth_data") or {})
        for item in payload.get("charts") or []
    }
    monkeypatch.setenv("SE_EPHE_PATH", str(Path("swisseph/ephe").resolve()))
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", "true")

    found_v0_9b_candidate = False
    for chart_id in (
        "istanbul_1994_06_25",
        "istanbul_1997_01_21",
        "izmir_1996_05_20",
        "adana_1998_09_12",
        "kutahya_1959_10_21",
    ):
        birth = chart_index[chart_id]
        response = interpret_natal_chart_ui(
            NatalInterpretationRequest(
                birth_date=str(birth.get("birth_date") or ""),
                birth_time=str(birth.get("birth_time") or ""),
                birth_place=str(birth.get("birth_place") or ""),
                birth_latitude=birth.get("birth_latitude"),
                birth_longitude=birth.get("birth_longitude"),
                birth_timezone=birth.get("birth_timezone"),
                locale="tr",
                summary_only=False,
                include_full_profile=True,
            ),
            debug=False,
            include_debug=True,
        )
        public = dict(response.get("public") or {})
        plan = (public.get("profile_v8_projection_v1") or {}).get("traceability", {}).get("natal_promise_cluster_plan_v1") or {}
        packets = plan.get("candidate_packets") or []
        v0_9b = [p for p in packets if str(p.get("family") or "") in {"relationship_route", "moon_signature"}]
        if not v0_9b:
            continue
        found_v0_9b_candidate = True
        suppressed = {
            str(item.get("packet_id") or "").strip(): item
            for item in plan.get("suppressed_packets") or []
        }
        for packet in v0_9b:
            pid = str(packet.get("id") or "").strip()
            sup = suppressed.get(pid) or {}
            keep_for = set(sup.get("keep_for") or [])
            assert keep_for <= {"debug", "detail"}, f"{chart_id}: unexpected keep_for {keep_for}"
            assert "public_main" not in keep_for, chart_id
            assert "public_support" not in keep_for, chart_id
        surface = plan.get("surface_plan") or {}
        for cluster_id in surface.get("public_main_cluster_ids") or []:
            assert "composed_relationship_route_v0_9b" not in str(cluster_id), chart_id
            assert "composed_moon_signature_v0_9b" not in str(cluster_id), chart_id
        for cluster_id in surface.get("public_support_cluster_ids") or []:
            assert "composed_relationship_route_v0_9b" not in str(cluster_id), chart_id
            assert "composed_moon_signature_v0_9b" not in str(cluster_id), chart_id
    assert found_v0_9b_candidate, "Expected at least one v0.9b candidate across audit charts"
