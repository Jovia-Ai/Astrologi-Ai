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
) -> dict:
    return {
        "id": packet_id,
        "domain": domain,
        "promise_type": promise_type,
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
