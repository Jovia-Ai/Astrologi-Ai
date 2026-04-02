import os
import json
from contextlib import contextmanager
from pathlib import Path

from app.api.routes.natal_interpretation import (
    _prepare_payload_from_chart,
    build_natal_interpretation_response_from_chart,
)
from app.natal.narrative.core_story_tr_natal import build_core_story_ui
from app.natal.narrative.contradiction_engine import build_contradiction_signatures
from app.natal.narrative.layer_arbitrator import arbitrate_natal_layers
from app.natal.narrative.master_selector import build_master_natal_selector
from app.natal.narrative.natal_feature_graph import build_natal_feature_graph
from app.natal.narrative.natal_selection_config import get_natal_selection_v3_config
from app.natal.narrative.profile_narrative_engine import build_profile_narrative
from app.natal.narrative.primitive_engine_v2 import build_primitives_v2
from app.natal.narrative.voice_profile_resolver import resolve_voice_profile_v2
from app.natal.personality_imprint import build_personality_imprint
from app.natal.supporting_threads_builder import build_sections_v2, build_supporting_threads
from app.natal.natal_graph import build_natal_graph
from app.services.chart_service import serialize_aspects, serialize_planets


def _artifact_chart(name: str = "natal_full_1996-12-28_07-10_istanbul.json") -> dict:
    path = Path(__file__).resolve().parents[1] / "_artifacts" / name
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_chart_names() -> list[str]:
    root = Path(__file__).resolve().parents[1] / "_artifacts"
    return sorted(path.name for path in root.glob("natal_full_*.json"))


def _selection_seed_key(chart: dict) -> str:
    birth = str(chart.get("birth_datetime") or chart.get("birthDateTime") or chart.get("birth_datetime_iso") or "").strip()
    location = chart.get("location") if isinstance(chart.get("location"), dict) else {}
    city = str(location.get("city") or (chart.get("birth") or {}).get("place") or "").strip()
    angles = chart.get("angles") if isinstance(chart.get("angles"), dict) else {}
    asc = str(angles.get("ascendant_sign") or angles.get("asc_sign") or "").strip()
    mc = str(angles.get("midheaven_sign") or angles.get("mc_sign") or "").strip()
    return f"{birth}|{city}|{asc}|{mc}"


@contextmanager
def _temporary_env(**updates: str | None):
    previous = {key: os.environ.get(key) for key in updates}
    try:
        for key, value in updates.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _serialized(chart: dict) -> tuple[list[dict], list[dict], dict]:
    planets = serialize_planets(chart.get("planets", {}))
    angles = chart.get("angles") if isinstance(chart.get("angles"), dict) else {}
    asc_sign = angles.get("ascendant_sign")
    if asc_sign and not any(str(entry.get("planet") or "").strip().lower() == "ascendant" for entry in planets):
        planets.append(
            {
                "planet": "Ascendant",
                "sign": asc_sign,
                "house": 1,
                "degree": angles.get("ascendant"),
                "is_point": True,
            }
        )
    aspects = serialize_aspects(chart.get("aspects", []))
    graph = build_natal_graph(chart_data=chart, planets=planets, aspects=aspects)
    return planets, aspects, graph


def test_natal_selection_v3_config_scaffold_loads() -> None:
    config = get_natal_selection_v3_config()

    assert config["engine_version"] == "natal_selection_v3_config_v1"
    assert config["phase_flags"]["master_selector_enabled"] is True
    assert config["phase_flags"]["contradiction_engine_enabled"] is True
    assert config["phase_flags"]["surface_migration_enabled"] is True
    assert config["phase_flags"]["voice_profile_enabled"] is True
    assert config["phase_flags"]["layer_arbitration_debug_only"] is True
    assert config["phase_flags"]["surface_migration_debug_only"] is False
    assert config["phase_flags"]["voice_profile_debug_only"] is False
    assert config["rollouts"]["voice_profile_rollout_pct"] == 100
    assert config["weights"]["planet_salience"]["chart_ruler_centrality"] > 0.0


def test_natal_feature_graph_builds_stronger_foundation_payload() -> None:
    chart = _artifact_chart()
    planets, aspects, graph = _serialized(chart)

    feature_graph = build_natal_feature_graph(
        chart_data=chart,
        planets=planets,
        aspects=aspects,
        natal_graph=graph,
    )

    assert feature_graph["engine_version"] == "natal_feature_graph_v2"
    assert feature_graph["planet_salience"]
    assert "chart_ruler_centrality" in feature_graph
    assert "public_private_split" in feature_graph
    assert "contradiction_polarity" in feature_graph
    assert "compensation_patterns" in feature_graph
    assert feature_graph["public_private_split"]["dominant"] in {"public", "private", "balanced"}
    assert any(item["score"] > 0.0 for item in feature_graph["planet_salience"].values())


def test_primitive_engine_v2_rescores_legacy_primitives_with_feature_support() -> None:
    chart = _artifact_chart()
    planets, aspects, graph = _serialized(chart)
    chart_payload = {**chart, "planets": planets, "aspects": aspects}
    feature_graph = build_natal_feature_graph(
        chart_data=chart_payload,
        planets=planets,
        aspects=aspects,
        natal_graph=graph,
    )

    primitive_scores = build_primitives_v2(
        chart_payload,
        natal_graph=graph,
        natal_feature_graph=feature_graph,
    )

    assert primitive_scores["engine_version"] == "primitive_engine_v2"
    assert primitive_scores["primitive_scores"]
    assert primitive_scores["top_primitives"]
    assert primitive_scores["ranking_diff"]["v2_top_ids"]
    top_entry = primitive_scores["top_primitives"][0]
    assert "feature_support" in top_entry
    assert "legacy_score" in top_entry
    assert "confidence" in top_entry


def test_contradiction_engine_builds_structured_signatures() -> None:
    chart = _artifact_chart()
    planets, aspects, graph = _serialized(chart)
    chart_payload = {**chart, "planets": planets, "aspects": aspects}
    feature_graph = build_natal_feature_graph(
        chart_data=chart_payload,
        planets=planets,
        aspects=aspects,
        natal_graph=graph,
    )
    primitive_scores = build_primitives_v2(
        chart_payload,
        natal_graph=graph,
        natal_feature_graph=feature_graph,
    )

    contradictions = build_contradiction_signatures(
        natal_feature_graph=feature_graph,
        primitive_scores=primitive_scores,
    )

    assert contradictions["engine_version"] == "contradiction_engine_v1"
    assert contradictions["signatures"]
    assert contradictions["top_signatures"]
    top_entry = contradictions["top_signatures"][0]
    assert top_entry["left"]
    assert top_entry["right"]
    assert top_entry["slot_biases"]
    assert top_entry["editorial_label"]


def test_master_selector_selects_identity_spine_lines() -> None:
    chart = _artifact_chart()
    planets, aspects, graph = _serialized(chart)
    chart_payload = {**chart, "planets": planets, "aspects": aspects}
    feature_graph = build_natal_feature_graph(
        chart_data=chart_payload,
        planets=planets,
        aspects=aspects,
        natal_graph=graph,
    )
    primitive_scores = build_primitives_v2(
        chart_payload,
        natal_graph=graph,
        natal_feature_graph=feature_graph,
    )
    contradictions = build_contradiction_signatures(
        natal_feature_graph=feature_graph,
        primitive_scores=primitive_scores,
    )

    selector = build_master_natal_selector(
        primitive_scores=primitive_scores,
        natal_feature_graph=feature_graph,
        contradiction_signatures=contradictions,
    )

    assert selector["engine_version"] == "master_selector_v1"
    assert selector["identity_spine"]["primary_identity_spine"]
    assert selector["identity_spine"]["secondary_balancing_line"]
    assert selector["identity_spine"]["relational_line"]
    assert selector["candidate_pool"]["primary_identity_spine"]
    assert selector["selection_debug"]["selected_order"]
    primary = selector["primary_identity_spine"]
    assert primary["source_primitives"]
    assert "score_breakdown" in primary


def test_layer_arbitrator_scores_surfaces_against_selected_spine() -> None:
    chart = _artifact_chart()
    planets, aspects, graph = _serialized(chart)
    chart_payload = {**chart, "planets": planets, "aspects": aspects}
    feature_graph = build_natal_feature_graph(
        chart_data=chart_payload,
        planets=planets,
        aspects=aspects,
        natal_graph=graph,
    )
    primitive_scores = build_primitives_v2(
        chart_payload,
        natal_graph=graph,
        natal_feature_graph=feature_graph,
    )
    contradictions = build_contradiction_signatures(
        natal_feature_graph=feature_graph,
        primitive_scores=primitive_scores,
    )
    selector = build_master_natal_selector(
        primitive_scores=primitive_scores,
        natal_feature_graph=feature_graph,
        contradiction_signatures=contradictions,
    )
    arbitration = arbitrate_natal_layers(
        master_selector=selector,
        surfaces={
            "core_story_ui": build_core_story_ui(
                chart_data=chart,
                planets=planets,
                natal_graph=graph,
            ),
            "profile_narrative": build_profile_narrative(
                chart,
                graph,
                include_debug=True,
            ),
            "personality_imprint": build_personality_imprint(
                planets=planets,
                aspects=aspects,
                natal_graph=graph,
                include_debug=True,
            ),
            "sections_v2": build_sections_v2(
                chart_data=chart,
                planets=planets,
                natal_graph=graph,
            ),
            "supporting_threads": build_supporting_threads(
                chart_data=chart,
                planets=planets,
                natal_graph=graph,
            ),
        },
        primitive_scores=primitive_scores,
        contradiction_signatures=contradictions,
    )

    assert arbitration["engine_version"] == "layer_arbitrator_v1"
    assert arbitration["scores"]["profile_narrative"]["block_count"] > 0
    assert arbitration["scores"]["core_story_ui"]["block_count"] == 1
    assert arbitration["scores"]["overall"]["surface_count"] >= 5
    assert arbitration["debug"]["surface_blocks"]["supporting_threads"]
    assert isinstance(arbitration["rejected_or_demoted_blocks"], list)


def test_voice_profile_resolver_builds_shadow_axes_and_expression_preview() -> None:
    chart = _artifact_chart()
    planets, aspects, graph = _serialized(chart)
    chart_payload = {**chart, "planets": planets, "aspects": aspects}
    feature_graph = build_natal_feature_graph(
        chart_data=chart_payload,
        planets=planets,
        aspects=aspects,
        natal_graph=graph,
    )
    primitive_scores = build_primitives_v2(
        chart_payload,
        natal_graph=graph,
        natal_feature_graph=feature_graph,
    )
    contradictions = build_contradiction_signatures(
        natal_feature_graph=feature_graph,
        primitive_scores=primitive_scores,
    )
    selector = build_master_natal_selector(
        primitive_scores=primitive_scores,
        natal_feature_graph=feature_graph,
        contradiction_signatures=contradictions,
    )

    voice_profile = resolve_voice_profile_v2(
        master_selector=selector,
        contradiction_signatures=contradictions,
        natal_feature_graph=feature_graph,
        primitive_scores=primitive_scores,
        include_debug=True,
    )

    assert voice_profile["engine_version"] == "voice_profile_v2"
    assert voice_profile["mode"] == "active"
    assert voice_profile["axes"]["direct_vs_reflective"]["label"]
    assert voice_profile["axes"]["warm_vs_restrained"]["label"]
    assert voice_profile["derived_expression"]["tone"] in {"soft", "neutral", "firm"}
    assert voice_profile["derived_expression"]["sentence_length"] in {"short", "medium", "long"}


def test_voice_profile_rollout_is_chart_stable_across_golden_artifacts() -> None:
    observed_modes = {}
    with _temporary_env(
        VOICE_PROFILE_ENABLED="true",
        VOICE_PROFILE_ROLLOUT_PCT="50",
        VOICE_PROFILE_DEBUG_ONLY="true",
    ):
        for artifact_name in _artifact_chart_names():
            chart = _artifact_chart(artifact_name)
            planets, aspects, graph = _serialized(chart)
            chart_payload = {**chart, "planets": planets, "aspects": aspects}
            feature_graph = build_natal_feature_graph(
                chart_data=chart_payload,
                planets=planets,
                aspects=aspects,
                natal_graph=graph,
            )
            primitive_scores = build_primitives_v2(
                chart_payload,
                natal_graph=graph,
                natal_feature_graph=feature_graph,
            )
            contradictions = build_contradiction_signatures(
                natal_feature_graph=feature_graph,
                primitive_scores=primitive_scores,
            )
            selector = build_master_natal_selector(
                primitive_scores=primitive_scores,
                natal_feature_graph=feature_graph,
                contradiction_signatures=contradictions,
            )
            seed_key = _selection_seed_key(chart)

            first = resolve_voice_profile_v2(
                master_selector=selector,
                contradiction_signatures=contradictions,
                natal_feature_graph=feature_graph,
                primitive_scores=primitive_scores,
                seed_key=seed_key,
                include_debug=True,
            )
            second = resolve_voice_profile_v2(
                master_selector=selector,
                contradiction_signatures=contradictions,
                natal_feature_graph=feature_graph,
                primitive_scores=primitive_scores,
                seed_key=seed_key,
                include_debug=True,
            )

            first_rollout = first["debug"]["rollout"]
            second_rollout = second["debug"]["rollout"]
            expected_mode = "active" if int(first_rollout["seed_bucket"]) < 50 else "shadow"

            assert first_rollout["rollout_pct"] == 50
            assert first_rollout["seed_bucket"] == second_rollout["seed_bucket"]
            assert first["mode"] == expected_mode
            assert second["mode"] == expected_mode
            observed_modes[artifact_name] = expected_mode

    assert observed_modes


def test_prepare_payload_from_chart_exposes_active_selection_debug_hooks() -> None:
    chart = _artifact_chart()

    payload = _prepare_payload_from_chart(
        chart,
        premium_mode=False,
        debug_mode=True,
    )

    debug = payload["debug"]
    assert debug["natal_graph_v2"]["engine_version"] == "natal_graph_v2"
    assert debug["natal_feature_graph_v2"]["engine_version"] == "natal_feature_graph_v2"
    assert debug["primitive_scores"]["engine_version"] == "primitive_engine_v2"
    assert debug["contradiction_engine_v1"]["engine_version"] == "contradiction_engine_v1"
    assert debug["master_selector_v1"]["engine_version"] == "master_selector_v1"
    assert debug["layer_arbitrator_v1"]["engine_version"] == "layer_arbitrator_v1"
    assert debug["selected_identity_spine"]["primary_identity_spine"]
    assert debug["contradiction_signatures"]
    assert debug["old_vs_new_selection_diff"]["primitive_ranking"]["v2_top_ids"]
    assert debug["old_vs_new_selection_diff"]["selector_slots"]["primary_identity_spine"]
    assert debug["cross_layer_consistency_scores"]["profile_narrative"]["block_count"] > 0
    assert "surface_conflicts" in debug["old_vs_new_selection_diff"]
    assert isinstance(debug["rejected_or_demoted_blocks"], list)
    assert debug["surface_migration_v1"]["mode"] == "active"
    assert debug["surface_migration_v1"]["active"] is True
    assert debug["surface_migration_v1"]["profile_narrative"]["mode"] == "active"
    assert debug["surface_migration_v1"]["personality_imprint"]["mode"] == "active"
    assert debug["voice_profile_v2"]["engine_version"] == "voice_profile_v2"
    assert debug["voice_profile_v2"]["mode"] == "active"
    assert debug["expression_profile"]["voice_profile_v2"]["engine_version"] == "voice_profile_v2"
    assert debug["old_vs_new_selection_diff"]["voice_profile"]["mode"] == "active"


def test_prepare_payload_from_chart_applies_spine_and_voice_in_public_mode() -> None:
    chart = _artifact_chart()

    payload = _prepare_payload_from_chart(
        chart,
        premium_mode=False,
        debug_mode=False,
    )

    assert payload["expression_profile"]["tone_source"] == "voice_profile_v2"
    assert payload["profile_narrative"]["profile_public"]["blocks"]
    assert payload["personality_imprint"]["entries"]
    assert payload["sections_v2"]
    assert payload["supporting_threads"]


def test_prepare_payload_from_chart_uses_voice_profile_when_rollout_is_active() -> None:
    chart = _artifact_chart()

    with _temporary_env(
        VOICE_PROFILE_ENABLED="true",
        VOICE_PROFILE_ROLLOUT_PCT="100",
        VOICE_PROFILE_DEBUG_ONLY="true",
    ):
        payload = _prepare_payload_from_chart(
            chart,
            premium_mode=False,
            debug_mode=True,
        )

    debug = payload["debug"]
    assert debug["voice_profile_v2"]["engine_version"] == "voice_profile_v2"
    assert debug["voice_profile_v2"]["mode"] == "active"
    assert debug["expression_profile"]["tone_source"] == "voice_profile_v2"
    assert debug["old_vs_new_selection_diff"]["voice_profile"]["mode"] == "active"
    assert debug["voice_profile_v2"]["debug"]["rollout"]["rollout_pct"] == 100


def test_final_response_includes_core_story_in_arbitration_debug() -> None:
    chart = _artifact_chart()

    response = build_natal_interpretation_response_from_chart(
        chart,
        debug_mode=True,
        premium_mode=False,
    )

    assert response["core_story_ui"]["headline"]
    debug = response["debug"]
    assert debug["layer_arbitrator_v1"]["engine_version"] == "layer_arbitrator_v1"
    assert debug["cross_layer_consistency_scores"]["core_story_ui"]["block_count"] == 1
    assert debug["surface_migration_v1"]["mode"] == "active"
    assert debug["voice_profile_v2"]["engine_version"] == "voice_profile_v2"
    assert "overall" in debug["cross_layer_consistency_scores"]
