from app.narrative.voice_guardrails_tr import (
    find_forbidden_public_copy_issues,
    find_technical_leakage,
)
from app.transit.narrative.astrolog_narrative_engine import (
    PeriodStoryContext,
    build_period_story,
)


def _event(**kwargs):
    base = {
        "event_id": "evt_np_asc",
        "transit_body": "Neptune",
        "aspect": "square",
        "natal_point": "ASC",
        "strength": 0.95,
        "orb_deg": 0.2,
        "phase": "exactish",
        "bucket": "long",
        "tags": ["self", "pressure"],
        "houses": {"transit_in_natal_house": 3, "natal_point_house": None},
    }
    base.update(kwargs)
    return base


def test_period_story_deterministic_for_same_seed() -> None:
    ctx = PeriodStoryContext(
        period_core={"featured_events": [_event()]},
        chart_snapshot={
            "house_cusps": {"1": {"sign": "Capricorn"}},
            "bodies": {"Saturn": {"house": 3, "sign": "Aries"}},
        },
        natal_promise={"themes": ["kimlik ve ifade"]},
    )

    a = build_period_story(ctx)
    b = build_period_story(ctx)

    assert a.period_opening == b.period_opening
    assert a.big_picture == b.big_picture
    assert a.mechanism == b.mechanism
    assert a.upper_meaning == b.upper_meaning


def test_period_story_fallback_without_snapshot_data() -> None:
    ctx = PeriodStoryContext(
        period_core={"featured_events": [_event(event_id="evt_fallback", natal_point="Mars")]},
        chart_snapshot={},
        natal_promise={},
    )

    out = build_period_story(ctx)
    assert isinstance(out.period_opening, str) and out.period_opening
    assert isinstance(out.big_picture, str) and out.big_picture
    assert isinstance(out.mechanism, str) and out.mechanism
    assert isinstance(out.growth_edge, str) and out.growth_edge
    assert isinstance(out.relational_or_life_expression, str) and out.relational_or_life_expression
    assert isinstance(out.what_it_builds, str) and out.what_it_builds
    assert isinstance(out.upper_meaning, str) and out.upper_meaning


def test_period_story_strips_technical_token_leaks() -> None:
    ctx = PeriodStoryContext(
        period_core={
            "featured_events": [
                _event(
                    event_id="evt_tokens",
                    phase="applying",
                    natal_point="ASC",
                    tags=["self", "mind"],
                )
            ]
        },
        chart_snapshot={"house_cusps": {"1": {"sign": "Capricorn"}}},
        natal_promise={"themes": ["zihin ve iletişim"]},
    )

    out = build_period_story(ctx)
    merged = (
        f"{out.period_opening} {out.big_picture} {out.mechanism} "
        f"{out.growth_edge} {out.relational_or_life_expression} {out.what_it_builds}"
    ).lower()
    for token in ("period", "exactish", "applying", "separating", "orb_deg"):
        assert token not in merged


def test_period_story_exposes_growth_and_build_fields() -> None:
    ctx = PeriodStoryContext(
        period_core={
            "featured_events": [
                _event(
                    event_id="evt_combo",
                    transit_body="Uranus",
                    aspect="trine",
                    natal_point="Mars",
                    houses={"transit_in_natal_house": 5, "natal_point_house": 9},
                )
            ]
        },
        chart_snapshot={
            "bodies": [{"body": "Mars", "house": 9, "sign": "Virgo"}],
            "angles": {"ASC": {"point": "ASC", "sign": "Capricorn"}},
        },
        natal_promise={"themes": ["öğrenme ve yön"]},
    )

    out = build_period_story(ctx)
    assert "öğrenme" in out.mechanism.lower() or "uzmanlaşma" in out.mechanism.lower()
    assert any(token in out.growth_edge.lower() for token in ("risk", "heves", "dağı", "ölçü"))
    assert "kasını" in out.what_it_builds.lower()


def test_period_story_uses_chapter_role_in_opening_and_debug() -> None:
    ctx = PeriodStoryContext(
        period_core={
            "featured_events": [
                _event(
                    event_id="evt_builder",
                    transit_body="Saturn",
                    aspect="conjunction",
                    natal_point="MC",
                    chapter_role={"role": "builder"},
                    story_score=0.92,
                    selection_index=0,
                    houses={"transit_in_natal_house": 10, "natal_point_house": 10},
                ),
                _event(
                    event_id="evt_peak",
                    transit_body="Mars",
                    aspect="square",
                    natal_point="Moon",
                    chapter_role={"role": "peak"},
                    story_score=0.74,
                    selection_index=1,
                    houses={"transit_in_natal_house": 4, "natal_point_house": 4},
                ),
            ]
        },
        chart_snapshot={},
        natal_promise={},
    )

    out = build_period_story(ctx)
    assert "omurga" in out.period_opening.lower() or "kalıcı" in out.period_opening.lower()
    assert out.debug["spine_role"] == "builder"
    assert "peak" in out.debug["support_roles"]


def test_period_story_prefers_canonical_period_spine_prefix() -> None:
    ctx = PeriodStoryContext(
        period_core={"featured_events": [_event(event_id="evt_canonical", natal_point="Venus")]},
        chart_snapshot={},
        natal_promise={
            "verdict": "strong",
            "connected_points": [{"house": 7}],
            "themes": ["ilişkide güven"],
        },
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "promise_safe_intimacy",
            "theme": "yakınlık ve güven",
            "prefix": "Bu dönem doğum haritandaki yakınlık ve güven hattını özellikle çalıştırıyor.",
            "spine_lines": ["relational_line"],
            "matched_event_ids": ["evt_canonical"],
        },
    )

    out = build_period_story(ctx)

    assert out.period_opening.startswith(
        "Bu dönem doğum haritandaki yakınlık ve güven hattını özellikle çalıştırıyor."
    )
    assert out.debug["promise_prefix_source"] == "canonical_period_spine"
    assert out.debug["canonical_period_spine_source"] == "canonical_natal_activation_v1"
    assert out.debug["canonical_period_spine_target_node_id"] == "promise_safe_intimacy"


def test_period_story_falls_back_to_legacy_natal_promise_prefix_without_canonical() -> None:
    ctx = PeriodStoryContext(
        period_core={"featured_events": [_event(event_id="evt_legacy", natal_point="Venus")]},
        chart_snapshot={},
        natal_promise={
            "verdict": "strong",
            "connected_points": [{"house": 7}],
            "themes": ["ilişkide güven"],
        },
        canonical_period_spine={},
    )

    out = build_period_story(ctx)

    assert isinstance(out.period_opening, str) and out.period_opening
    assert out.debug["promise_prefix_source"] == "legacy_natal_promise"


def test_period_story_uses_spine_aware_period_voice_policy_with_backing() -> None:
    ctx = PeriodStoryContext(
        period_core={
            "featured_events": [
                _event(
                    event_id="evt_work_saturn",
                    transit_body="Saturn",
                    aspect="conjunction",
                    natal_point="MC",
                    chapter_role={"role": "builder"},
                    story_score=0.91,
                    selection_index=0,
                    houses={"transit_in_natal_house": 10, "natal_point_house": 10},
                )
            ]
        },
        chart_snapshot={},
        natal_promise={},
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "promise_mature_visibility",
            "theme": "yön ve görünürlük",
            "prefix": "Bu dönem doğum haritandaki yön ve görünürlük hattını özellikle çalıştırıyor.",
            "spine_lines": ["work_visibility_line"],
            "matched_event_ids": ["evt_work_saturn"],
        },
    )

    out = build_period_story(ctx)

    assert "sorumluluk" in out.mechanism.lower()
    assert "gerçekten sana ait olan yük" in out.big_picture
    assert "hangisini gerçekten seçtiğini netleştirmek" in out.growth_edge
    assert "uzun vadeli yönünü de netleştirir" in out.relational_or_life_expression
    assert out.debug["period_voice_policy_version"] == "period_voice_policy_v1"
    assert out.debug["period_voice_policy_reason_line_allowed"] is True
    assert out.debug["period_voice_policy_meaning_intent"] == "responsibility_selection"
    assert out.debug["period_voice_policy_rhetorical_frame"] == "sorting"
    assert out.debug["period_voice_policy_match_level"] == "exact"
    assert out.debug["period_voice_policy_manifestation_context"]["primary_house"] == 10
    assert "unbacked_natal_reason" in out.debug["period_voice_policy_avoid_tags"]
    assert out.debug["period_voice_policy"]["spine_line"] == "work_visibility_line"
    assert out.debug["period_voice_policy"]["event_nature"] == "responsibility"


def test_period_story_spine_aware_policy_does_not_render_reason_line_without_backing() -> None:
    ctx = PeriodStoryContext(
        period_core={
            "featured_events": [
                _event(
                    event_id="evt_work_mars",
                    transit_body="Mars",
                    aspect="trine",
                    natal_point="MC",
                    chapter_role={"role": "opener"},
                    story_score=0.91,
                    selection_index=0,
                    houses={"transit_in_natal_house": 10, "natal_point_house": 10},
                )
            ]
        },
        chart_snapshot={},
        natal_promise={},
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "theme": "yön ve görünürlük",
            "prefix": "Bu dönem doğum haritandaki yön ve görünürlük hattını özellikle çalıştırıyor.",
            "spine_lines": ["work_visibility_line"],
            "matched_event_ids": ["evt_work_mars"],
        },
    )

    out = build_period_story(ctx)

    assert "daha çok yer kaplaman" in out.mechanism
    assert "Bu konu boşuna" not in out.relational_or_life_expression
    assert out.debug["period_voice_policy_reason_line_allowed"] is False
    assert out.debug["period_voice_policy"]["event_nature"] == "courage"


def test_period_story_reads_relational_saturn_as_boundary_voice() -> None:
    ctx = PeriodStoryContext(
        period_core={
            "featured_events": [
                _event(
                    event_id="evt_rel_saturn",
                    transit_body="Saturn",
                    aspect="conjunction",
                    natal_point="Venus",
                    chapter_role={"role": "builder"},
                    story_score=0.9,
                    selection_index=0,
                    houses={"transit_in_natal_house": 7, "natal_point_house": 7},
                )
            ]
        },
        chart_snapshot={},
        natal_promise={},
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "promise_safe_intimacy",
            "theme": "yakınlık ve güven",
            "prefix": "Bu dönem doğum haritandaki yakınlık ve güven hattını özellikle çalıştırıyor.",
            "spine_lines": ["relational_line"],
            "matched_event_ids": ["evt_rel_saturn"],
        },
    )

    out = build_period_story(ctx)

    assert "sınır" in out.mechanism.lower()
    assert "aynı cümlede tutacak ayarı" in out.big_picture
    assert "Asıl ayar" in out.growth_edge
    assert "karşındaki kişiyle kurduğun denge" in out.growth_edge
    assert out.debug["period_voice_policy"]["event_nature"] == "boundary"
    assert out.debug["period_voice_policy"]["event_nature_source"] == "spine_line_context"
    assert out.debug["period_voice_policy_meaning_intent"] == "trust_calibration"
    assert out.debug["period_voice_policy_rhetorical_frame"] == "calibration"
    assert out.debug["period_voice_policy_manifestation_context"]["primary_house"] == 7


def test_period_story_preserves_legacy_text_when_canonical_spine_is_absent() -> None:
    base_kwargs = {
        "period_core": {"featured_events": [_event(event_id="evt_legacy_compare", natal_point="Mars")]},
        "chart_snapshot": {},
        "natal_promise": {
            "verdict": "strong",
            "connected_points": [{"house": 7}],
            "themes": ["ilişkide güven"],
        },
    }
    without_canonical = build_period_story(PeriodStoryContext(**base_kwargs, canonical_period_spine=None))
    with_empty_canonical = build_period_story(PeriodStoryContext(**base_kwargs, canonical_period_spine={}))

    assert without_canonical.period_opening == with_empty_canonical.period_opening
    assert without_canonical.big_picture == with_empty_canonical.big_picture
    assert without_canonical.mechanism == with_empty_canonical.mechanism
    assert without_canonical.growth_edge == with_empty_canonical.growth_edge
    assert without_canonical.relational_or_life_expression == with_empty_canonical.relational_or_life_expression
    assert without_canonical.what_it_builds == with_empty_canonical.what_it_builds
    assert with_empty_canonical.debug["period_voice_policy_version"] == ""
    assert with_empty_canonical.debug["period_voice_policy_avoid_tags"] == []


def test_period_story_threshold_frame_does_not_use_esik_word() -> None:
    ctx = PeriodStoryContext(
        period_core={
            "featured_events": [
                _event(
                    event_id="evt_id_mars",
                    transit_body="Mars",
                    aspect="conjunction",
                    natal_point="ASC",
                    chapter_role={"role": "opener"},
                    story_score=0.9,
                    selection_index=0,
                )
            ]
        },
        chart_snapshot={},
        natal_promise={},
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "promise_identity_direction",
            "theme": "kimlik ve yön",
            "spine_lines": ["primary_identity_line"],
            "matched_event_ids": ["evt_id_mars"],
        },
    )

    out = build_period_story(ctx)
    merged = f"{out.big_picture} {out.growth_edge}".lower()

    assert out.debug["period_voice_policy_rhetorical_frame"] == "threshold"
    assert "eşik" not in merged
    assert "karar şurada" in merged


def test_period_story_release_frame_uses_release_variation_without_plain_birakmak() -> None:
    ctx = PeriodStoryContext(
        period_core={
            "featured_events": [
                _event(
                    event_id="evt_shadow_neptune",
                    transit_body="Neptune",
                    aspect="square",
                    natal_point="ASC",
                    chapter_role={"role": "release"},
                    story_score=0.9,
                    selection_index=0,
                )
            ]
        },
        chart_snapshot={},
        natal_promise={},
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "contradiction_boundary_blur",
            "theme": "iç sınır",
            "spine_lines": ["shadow_protection_line"],
            "matched_event_ids": ["evt_shadow_neptune"],
        },
        recent_rhetorical_frames=["naked"],
    )

    out = build_period_story(ctx)
    merged = f"{out.big_picture} {out.growth_edge}".lower()

    assert out.debug["period_voice_policy_rhetorical_frame"] == "release"
    assert "yer açmak" in merged
    assert " bırakmak" not in merged


def test_period_story_manifestation_context_differs_for_same_policy_house_six_vs_ten() -> None:
    six_ctx = PeriodStoryContext(
        period_core={
            "featured_events": [
                _event(
                    event_id="evt_work_6",
                    transit_body="Saturn",
                    aspect="conjunction",
                    natal_point="Venus",
                    chapter_role={"role": "builder"},
                    story_score=0.9,
                    selection_index=0,
                    houses={"transit_in_natal_house": 6, "natal_point_house": 6},
                )
            ]
        },
        chart_snapshot={},
        natal_promise={},
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "promise_mature_visibility",
            "spine_lines": ["work_visibility_line"],
            "matched_event_ids": ["evt_work_6"],
        },
    )
    ten_ctx = PeriodStoryContext(
        period_core={
            "featured_events": [
                _event(
                    event_id="evt_work_10",
                    transit_body="Saturn",
                    aspect="conjunction",
                    natal_point="MC",
                    chapter_role={"role": "builder"},
                    story_score=0.9,
                    selection_index=0,
                    houses={"transit_in_natal_house": 10, "natal_point_house": 10},
                )
            ]
        },
        chart_snapshot={},
        natal_promise={},
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "promise_mature_visibility",
            "spine_lines": ["work_visibility_line"],
            "matched_event_ids": ["evt_work_10"],
        },
    )

    six = build_period_story(six_ctx)
    ten = build_period_story(ten_ctx)

    assert six.debug["period_voice_policy_manifestation_context"]["primary_house"] == 6
    assert ten.debug["period_voice_policy_manifestation_context"]["primary_house"] == 10
    assert "böyle taşımaya devam edebilir miyim" in six.mechanism.lower()
    assert "senden beklenen duruş" in ten.mechanism.lower() or "dış dünyadaki rolün" in ten.mechanism.lower() or "isminin geçtiği yer" in ten.mechanism.lower()


def test_period_story_manifestation_context_relational_third_house_uses_conversation_scene() -> None:
    ctx = PeriodStoryContext(
        period_core={
            "featured_events": [
                _event(
                    event_id="evt_rel_3",
                    transit_body="Saturn",
                    aspect="conjunction",
                    natal_point="Venus",
                    chapter_role={"role": "peak"},
                    story_score=0.9,
                    selection_index=0,
                    houses={"transit_in_natal_house": 3, "natal_point_house": 7},
                )
            ]
        },
        chart_snapshot={},
        natal_promise={},
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "promise_safe_intimacy",
            "spine_lines": ["relational_line"],
            "matched_event_ids": ["evt_rel_3"],
        },
    )

    out = build_period_story(ctx)
    merged = f"{out.mechanism} {out.big_picture}".lower()

    assert out.debug["period_voice_policy_manifestation_context"]["primary_house"] == 3
    assert any(token in merged for token in ("gündelik konuşmalar", "küçük cümlelerin ağırlığı", "yakın çevrendeki ses"))
    for token in ("3. ev", " açı ", "transit "):
        assert token not in merged


def test_period_story_manifestation_context_relational_seventh_house_uses_relationship_scene() -> None:
    ctx = PeriodStoryContext(
        period_core={
            "featured_events": [
                _event(
                    event_id="evt_rel_7_scene",
                    transit_body="Saturn",
                    aspect="conjunction",
                    natal_point="Venus",
                    chapter_role={"role": "peak"},
                    story_score=0.9,
                    selection_index=0,
                    houses={"transit_in_natal_house": 7, "natal_point_house": 7},
                )
            ]
        },
        chart_snapshot={},
        natal_promise={},
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "promise_safe_intimacy",
            "spine_lines": ["relational_line"],
            "matched_event_ids": ["evt_rel_7_scene"],
        },
    )

    out = build_period_story(ctx)
    merged = f"{out.mechanism} {out.big_picture}".lower()

    assert out.debug["period_voice_policy_manifestation_context"]["primary_house"] == 7
    assert any(token in merged for token in ("karşındaki kişiyle kurduğun denge", "anlaşma yapma biçimin", "yakın ilişkideki karşılıklı alan"))


def test_period_story_manifestation_context_shadow_twelfth_house_stays_nontechnical() -> None:
    ctx = PeriodStoryContext(
        period_core={
            "featured_events": [
                _event(
                    event_id="evt_shadow_12_scene",
                    transit_body="Neptune",
                    aspect="square",
                    natal_point="ASC",
                    chapter_role={"role": "release"},
                    story_score=0.9,
                    selection_index=0,
                    houses={"transit_in_natal_house": 12, "natal_point_house": 1},
                )
            ]
        },
        chart_snapshot={},
        natal_promise={},
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "contradiction_boundary_blur",
            "spine_lines": ["shadow_protection_line"],
            "matched_event_ids": ["evt_shadow_12_scene"],
        },
    )

    out = build_period_story(ctx)
    merged = f"{out.mechanism} {out.big_picture} {out.growth_edge} {out.relational_or_life_expression}".lower()

    assert out.debug["period_voice_policy_manifestation_context"]["primary_house"] == 12
    assert any(token in merged for token in ("geri çekildiğin iç dünya", "gözükmeyen hassasiyetlerin", "kapanış ve çözülme alanı"))
    assert "sende zaten" not in merged
    for token in ("12. ev", " açı ", "transit "):
        assert token not in merged


def test_period_story_dense_integration_reframes_friction_as_learning() -> None:
    ctx = PeriodStoryContext(
        period_core={
            "featured_events": [
                _event(
                    event_id="evt_dense_integration",
                    transit_body="Venus",
                    aspect="square",
                    natal_point="Jupiter",
                    chapter_role={"role": "builder"},
                    story_score=0.9,
                    selection_index=0,
                    houses={"transit_in_natal_house": 7, "natal_point_house": 7},
                )
            ]
        },
        chart_snapshot={},
        natal_promise={},
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "promise_build_safe_intimacy",
            "spine_lines": ["relational_line"],
            "matched_event_ids": ["evt_dense_integration"],
        },
    )

    out = build_period_story(ctx)
    merged = f"{out.mechanism} {out.growth_edge} {out.what_it_builds}".lower()

    assert out.debug["period_voice_policy_valence_mode"] == "integration"
    assert out.debug["period_voice_policy_intensity_mode"] == "dense"
    assert "rahat akmıyor" in merged
    assert any(token in merged for token in ("birbirini öğreniyor", "birlikte çalışmayı", "pürüzsüz akışı"))


def test_period_story_recognition_light_reads_as_visibility_opening_not_burden() -> None:
    ctx = PeriodStoryContext(
        period_core={
            "featured_events": [
                _event(
                    event_id="evt_recognition",
                    transit_body="Sun",
                    aspect="trine",
                    natal_point="MC",
                    chapter_role={"role": "peak"},
                    story_score=0.92,
                    selection_index=0,
                    houses={"transit_in_natal_house": 10, "natal_point_house": 10},
                )
            ]
        },
        chart_snapshot={},
        natal_promise={},
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "promise_mature_visibility",
            "spine_lines": ["work_visibility_line"],
            "matched_event_ids": ["evt_recognition"],
        },
    )

    out = build_period_story(ctx)
    merged = f"{out.mechanism} {out.big_picture} {out.what_it_builds}".lower()

    assert out.debug["period_voice_policy_valence_mode"] == "recognition"
    assert out.debug["period_voice_policy_intensity_mode"] == "light"
    assert any(token in merged for token in ("rahat görünüyorsun", "görünürlük", "emeğin"))
    assert "yük" not in merged


def test_period_story_release_light_uses_hafifleme_not_plain_birakmak() -> None:
    ctx = PeriodStoryContext(
        period_core={
            "featured_events": [
                _event(
                    event_id="evt_release_light",
                    transit_body="Neptune",
                    aspect="sextile",
                    natal_point="ASC",
                    chapter_role={"role": "release"},
                    story_score=0.91,
                    selection_index=0,
                    houses={"transit_in_natal_house": 12, "natal_point_house": 1},
                )
            ]
        },
        chart_snapshot={},
        natal_promise={},
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "contradiction_boundary_blur",
            "spine_lines": ["shadow_protection_line"],
            "matched_event_ids": ["evt_release_light"],
        },
    )

    out = build_period_story(ctx)
    merged = f"{out.mechanism} {out.big_picture} {out.growth_edge} {out.what_it_builds}".lower()

    assert out.debug["period_voice_policy_valence_mode"] == "release"
    assert out.debug["period_voice_policy_intensity_mode"] == "light"
    assert any(token in merged for token in ("hafif", "yer aç", "çözülme"))
    assert " bırakmak" not in merged


def test_period_story_momentum_dense_carries_pressure_and_motion() -> None:
    ctx = PeriodStoryContext(
        period_core={
            "featured_events": [
                _event(
                    event_id="evt_momentum_dense",
                    transit_body="Mars",
                    aspect="trine",
                    natal_point="Pluto",
                    chapter_role={"role": "peak"},
                    story_score=0.95,
                    selection_index=0,
                    houses={"transit_in_natal_house": 1, "natal_point_house": 1},
                )
            ]
        },
        chart_snapshot={},
        natal_promise={},
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "promise_identity_direction",
            "spine_lines": ["primary_identity_line"],
            "matched_event_ids": ["evt_momentum_dense"],
        },
    )

    out = build_period_story(ctx)
    merged = f"{out.mechanism} {out.big_picture} {out.growth_edge} {out.what_it_builds}".lower()

    assert out.debug["period_voice_policy_valence_mode"] == "momentum"
    assert out.debug["period_voice_policy_intensity_mode"] == "dense"
    assert any(token in merged for token in ("hareket", "kanal", "baskı", "yoğunluk"))


def test_period_story_v4_chart1_maturation_scene_reads_as_selected_voice() -> None:
    ctx = PeriodStoryContext(
        period_core={
            "featured_events": [
                _event(
                    event_id="evt_v4_chart1",
                    transit_body="Saturn",
                    aspect="sextile",
                    natal_point="ASC",
                    chapter_role={"role": "builder"},
                    story_score=0.92,
                    selection_index=0,
                    houses={"transit_in_natal_house": 3, "natal_point_house": 1},
                )
            ]
        },
        chart_snapshot={},
        natal_promise={},
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "promise_identity_direction",
            "spine_lines": ["primary_identity_line"],
            "matched_event_ids": ["evt_v4_chart1"],
        },
    )

    out = build_period_story(ctx)
    merged = f"{out.period_opening} {out.mechanism} {out.growth_edge} {out.what_it_builds}".lower()

    assert out.debug["period_voice_policy_valence_mode"] == "maturation"
    assert out.debug["period_voice_policy_intensity_mode"] == "medium"
    assert any(token in merged for token in ("yakın çevrendeki ses", "küçük cümlelerin ağırlığı", "gündelik konuşmalar"))
    assert any(token in merged for token in ("sözün", "küçük bir cümle", "nerede durduğunu"))
    assert out.debug["render_guardrails"]["period_opening"] == []


def test_period_story_v4_chart2_release_scene_reads_as_softening_not_burden() -> None:
    ctx = PeriodStoryContext(
        period_core={
            "featured_events": [
                _event(
                    event_id="evt_v4_chart2",
                    transit_body="Neptune",
                    aspect="sextile",
                    natal_point="ASC",
                    chapter_role={"role": "release"},
                    story_score=0.91,
                    selection_index=0,
                    houses={"transit_in_natal_house": 12, "natal_point_house": 1},
                )
            ]
        },
        chart_snapshot={},
        natal_promise={},
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "contradiction_boundary_blur",
            "spine_lines": ["shadow_protection_line"],
            "matched_event_ids": ["evt_v4_chart2"],
        },
    )

    out = build_period_story(ctx)
    merged = f"{out.period_opening} {out.big_picture} {out.mechanism} {out.growth_edge}".lower()

    assert out.debug["period_voice_policy_valence_mode"] == "release"
    assert out.debug["period_voice_policy_intensity_mode"] == "light"
    assert any(token in merged for token in ("içeri almak zorunda değilsin", "hafifliyor", "yer açmak"))
    assert "yük gibi" not in merged


def test_period_story_v4_chart3_recognition_scene_reads_as_identity_stage() -> None:
    ctx = PeriodStoryContext(
        period_core={
            "featured_events": [
                _event(
                    event_id="evt_v4_chart3",
                    transit_body="Sun",
                    aspect="trine",
                    natal_point="MC",
                    chapter_role={"role": "peak"},
                    story_score=0.92,
                    selection_index=0,
                    houses={"transit_in_natal_house": 10, "natal_point_house": 10},
                )
            ]
        },
        chart_snapshot={},
        natal_promise={},
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "promise_mature_visibility",
            "spine_lines": ["work_visibility_line"],
            "matched_event_ids": ["evt_v4_chart3"],
        },
    )

    out = build_period_story(ctx)
    merged = f"{out.period_opening} {out.big_picture} {out.mechanism} {out.relational_or_life_expression}".lower()

    assert out.debug["period_voice_policy_valence_mode"] == "recognition"
    assert out.debug["period_voice_policy_intensity_mode"] == "light"
    assert any(token in merged for token in ("isminin geçtiği yer", "senden beklenen duruş", "dış dünyadaki rolün"))
    assert any(token in merged for token in ("kanıtlamak", "emeğin", "görünürlük"))
    assert "yük" not in merged


def test_period_story_v4_chart4_dense_integration_reads_as_learning_not_alarm() -> None:
    ctx = PeriodStoryContext(
        period_core={
            "featured_events": [
                _event(
                    event_id="evt_v4_chart4",
                    transit_body="Venus",
                    aspect="square",
                    natal_point="Jupiter",
                    chapter_role={"role": "builder"},
                    story_score=0.9,
                    selection_index=0,
                    houses={"transit_in_natal_house": 4, "natal_point_house": 4},
                )
            ]
        },
        chart_snapshot={},
        natal_promise={},
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "promise_build_safe_intimacy",
            "spine_lines": ["relational_line"],
            "matched_event_ids": ["evt_v4_chart4"],
        },
    )

    out = build_period_story(ctx)
    merged = f"{out.period_opening} {out.big_picture} {out.mechanism} {out.growth_edge} {out.what_it_builds}".lower()

    assert out.debug["period_voice_policy_valence_mode"] == "integration"
    assert out.debug["period_voice_policy_intensity_mode"] == "dense"
    assert "sana ait hissettiren alan" in merged
    assert any(token in merged for token in ("sürtünme", "öğrenmesi", "kası"))
    assert "alarm" not in merged


def test_period_story_v4_chart5_momentum_reads_as_direction_not_generic_push() -> None:
    ctx = PeriodStoryContext(
        period_core={
            "featured_events": [
                _event(
                    event_id="evt_v4_chart5",
                    transit_body="Mars",
                    aspect="trine",
                    natal_point="Pluto",
                    chapter_role={"role": "peak"},
                    story_score=0.95,
                    selection_index=0,
                    houses={"transit_in_natal_house": 1, "natal_point_house": 1},
                )
            ]
        },
        chart_snapshot={},
        natal_promise={},
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "promise_identity_direction",
            "spine_lines": ["primary_identity_line"],
            "matched_event_ids": ["evt_v4_chart5"],
        },
    )

    out = build_period_story(ctx)
    merged = f"{out.period_opening} {out.big_picture} {out.mechanism} {out.what_it_builds}".lower()

    assert out.debug["period_voice_policy_valence_mode"] == "momentum"
    assert out.debug["period_voice_policy_intensity_mode"] == "dense"
    assert any(token in merged for token in ("yön", "hareket", "geri çekilmiyor"))
    assert "generic" not in merged


def test_period_story_render_guardrails_are_empty_for_public_fields() -> None:
    ctx = PeriodStoryContext(
        period_core={"featured_events": [_event(event_id="evt_guardrails_runtime")]},
        chart_snapshot={"house_cusps": {"1": {"sign": "Capricorn"}}},
        natal_promise={"themes": ["yön ve görünürlük"]},
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "promise_mature_visibility",
            "spine_lines": ["work_visibility_line"],
            "matched_event_ids": ["evt_guardrails_runtime"],
        },
    )

    out = build_period_story(ctx)
    for field_name in (
        "period_opening",
        "big_picture",
        "mechanism",
        "growth_edge",
        "relational_or_life_expression",
        "what_it_builds",
        "upper_meaning",
    ):
        text = getattr(out, field_name)
        assert out.debug["render_guardrails"][field_name] == []
        assert find_forbidden_public_copy_issues(text, check_directives=False) == []
        assert find_technical_leakage(text, surface="body") == []


def test_period_story_active_life_chapter_debug_passthrough_is_noop() -> None:
    ctx = PeriodStoryContext(
        period_core={"featured_events": [_event(event_id="evt_life_chapter_noop")]},
        chart_snapshot={},
        natal_promise={},
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "promise_mature_visibility",
            "spine_lines": ["work_visibility_line"],
            "matched_event_ids": ["evt_life_chapter_noop"],
        },
        active_life_chapter={
            "chapter_type": "saturn_return",
            "phase": "first_pass",
            "selected_meaning": "sözün daha seçilmiş bir ağırlık taşıması",
        },
    )

    out = build_period_story(ctx)

    assert out.debug["active_life_chapter_present"] is True
    assert out.debug["active_life_chapter_type"] == "saturn_return"
    assert out.debug["active_life_chapter_phase"] == "first_pass"
    assert out.debug["active_life_chapter_selected_meaning"] == "sözün daha seçilmiş bir ağırlık taşıması"
