import json
from pathlib import Path

from app.astro_os.natal.contracts import CanonicalNatalStateV1
from app.astro_os.natal.legacy_adapter import (
    build_legacy_natal_bundle_from_base_payload,
    build_legacy_natal_bundle_from_chart,
)
from app.astro_os.natal.contradiction_hierarchy import build_contradiction_hierarchy
from app.astro_os.natal.meaning_graph import build_natal_meaning_graph
from app.astro_os.natal.promise_hierarchy import build_promise_hierarchy
from app.astro_os.natal.state_builder import build_canonical_natal_state_v1


def test_canonical_natal_state_v1_empty_shape_is_valid() -> None:
    state = CanonicalNatalStateV1(chart_id="chart_123")

    assert state.chart_id == "chart_123"
    assert state.chart_spine.primary_identity_line.key == "primary_identity_line"
    assert state.structural_state.planet_conditions == []
    assert state.core_promises == []


def test_legacy_bundle_from_chart_tracks_used_sources() -> None:
    bundle = build_legacy_natal_bundle_from_chart(
        {"birth_date": "1996-12-28", "birth_time": "07:10", "birth_place": "Istanbul"},
        natal_graph_v2={"promise_vectors": {"identity": 0.8}},
        contradiction_signatures={"top_signatures": []},
    )

    assert bundle.chart_id.startswith("1996-12-28_07:10")
    assert bundle.natal_graph_v2 is not None
    assert bundle.contradiction_signatures is not None
    assert bundle.legacy_sources_used == ["natal_graph_v2", "contradiction_signatures"]


def test_legacy_bundle_from_base_payload_extracts_known_fields() -> None:
    payload = {
        "metadata": {"chart_id": "chart_seed_1"},
        "chart_data": {"birth_date": "1996-12-28"},
        "dispositor_flow": {"chains": []},
        "_natal_graph_v2": {"promise_vectors": {"identity": 0.5}},
        "_natal_feature_graph_v2": {"dominant_planets": []},
        "_contradiction_signatures_v1": {"signatures": []},
        "_master_selector_v1": {"identity_spine": {}},
    }

    bundle = build_legacy_natal_bundle_from_base_payload(payload)

    assert bundle.chart_id == "chart_seed_1"
    assert bundle.dispositor_data == {"chains": []}
    assert bundle.promise_vectors == {"identity": 0.5}
    assert "master_selector" in bundle.legacy_sources_used


def test_state_builder_projects_source_trace_into_debug() -> None:
    bundle = build_legacy_natal_bundle_from_chart(
        {"birth_date": "1996-12-28", "birth_time": "07:10", "birth_place": "Istanbul"},
        natal_graph_v2={"promise_vectors": {"identity": 0.8}},
        feature_graph={"dominant_planets": []},
    )

    state = build_canonical_natal_state_v1(bundle, include_debug=True)

    assert state.debug is not None
    assert "natal_graph_v2" in state.debug.legacy_sources_used
    assert state.debug.source_trace["natal_graph_v2"] == [
        "explicit_argument.natal_graph_v2"
    ]


def test_promise_hierarchy_builds_ranked_promise_nodes() -> None:
    bundle = build_legacy_natal_bundle_from_chart(
        {"birth_date": "1996-12-28", "birth_time": "07:10", "birth_place": "Istanbul"},
        natal_graph_v2={
            "promise_vectors": {
                "build_safe_intimacy": 0.81,
                "mature_visibility": 0.58,
            },
            "debug": {
                "vector_evidence": {
                    "build_safe_intimacy": [
                        "7th ruler in 8th",
                        "Moon in 8th",
                        "depth_intimacy motif",
                    ],
                    "mature_visibility": [
                        "MC ruler carries visibility lesson",
                    ],
                }
            },
        },
    )

    result = build_promise_hierarchy(bundle)

    assert [node.id for node in result.active] == [
        "promise_build_safe_intimacy",
        "promise_mature_visibility",
    ]
    assert result.active[0].centrality == "core"
    assert result.active[1].centrality == "major"
    assert len(result.active[0].evidence) == 3


def test_state_builder_integrates_ranked_promises() -> None:
    bundle = build_legacy_natal_bundle_from_chart(
        {"birth_date": "1996-12-28", "birth_time": "07:10", "birth_place": "Istanbul"},
        natal_graph_v2={
            "promise_vectors": {"build_safe_intimacy": 0.81},
            "debug": {
                "vector_evidence": {
                    "build_safe_intimacy": [
                        "7th ruler in 8th",
                        "Moon in 8th",
                    ]
                }
            },
        },
    )

    state = build_canonical_natal_state_v1(bundle, include_debug=True)

    assert [node.id for node in state.core_promises] == ["promise_build_safe_intimacy"]
    assert state.core_promises[0].centrality == "core"
    assert state.debug is not None
    assert state.debug.evidence_count == 2


def test_contradiction_hierarchy_builds_ranked_contradictions() -> None:
    bundle = build_legacy_natal_bundle_from_chart(
        {"birth_date": "1996-12-28", "birth_time": "07:10", "birth_place": "Istanbul"},
        contradiction_signatures={
            "signatures": [
                {
                    "id": "closeness_vs_threshold",
                    "score": 0.74,
                    "editorial_label": "closeness with a high trust threshold",
                    "left": "intimacy_depth",
                    "right": "emotional_threshold",
                    "evidence": ["depth_intimacy", "thresholded_intimacy"],
                }
            ]
        },
    )

    result = build_contradiction_hierarchy(bundle)

    assert [node.id for node in result.active] == ["contradiction_closeness_vs_threshold"]
    assert result.active[0].centrality == "primary"
    assert len(result.active[0].evidence) == 2


def test_state_builder_publishes_spine_only_with_backing() -> None:
    bundle = build_legacy_natal_bundle_from_chart(
        {"birth_date": "1996-12-28", "birth_time": "07:10", "birth_place": "Istanbul"},
        natal_graph_v2={
            "promise_vectors": {
                "build_safe_intimacy": 0.81,
                "mature_visibility": 0.58,
            },
            "debug": {
                "vector_evidence": {
                    "build_safe_intimacy": ["7th ruler in 8th", "Moon in 8th"],
                    "mature_visibility": ["MC ruler carries visibility lesson"],
                }
            },
        },
        contradiction_signatures={
            "signatures": [
                {
                    "id": "closeness_vs_threshold",
                    "score": 0.74,
                    "editorial_label": "closeness with a high trust threshold",
                    "left": "intimacy_depth",
                    "right": "emotional_threshold",
                    "evidence": ["depth_intimacy", "thresholded_intimacy"],
                }
            ]
        },
        master_selector={
            "primary_identity_spine": {"line_id": "identity_candidate"},
            "relational_line": {
                "line_id": "relational_candidate",
                "contradiction_ids": ["closeness_vs_threshold"],
            },
            "work_visibility_line": {"line_id": "visibility_candidate"},
        },
    )

    state = build_canonical_natal_state_v1(bundle, include_debug=True)

    assert state.contradictions[0].id == "contradiction_closeness_vs_threshold"
    assert state.chart_spine.relational_line.node_id == "contradiction_closeness_vs_threshold"
    assert state.chart_spine.work_visibility_line.node_id == "promise_mature_visibility"
    assert state.chart_spine.primary_identity_line.node_id is None
    assert state.debug is not None
    assert any(
        item.get("candidate_id") == "identity_candidate"
        for item in state.debug.suppressed_candidates
    )
    assert state.meaning_graph["version"] == "natal_meaning_graph_v1"
    assert state.meaning_graph["meta"]["activation_hook_count"] >= 1


def test_natal_meaning_graph_contains_nodes_edges_and_activation_hooks() -> None:
    bundle = build_legacy_natal_bundle_from_chart(
        {"birth_date": "1996-12-28", "birth_time": "07:10", "birth_place": "Istanbul"},
        natal_graph_v2={
            "promise_vectors": {
                "build_safe_intimacy": 0.81,
                "mature_visibility": 0.58,
            },
            "debug": {
                "vector_evidence": {
                    "build_safe_intimacy": ["7th ruler in 8th", "Moon in 8th"],
                    "mature_visibility": ["MC ruler carries visibility lesson"],
                }
            },
        },
        contradiction_signatures={
            "signatures": [
                {
                    "id": "closeness_vs_threshold",
                    "score": 0.74,
                    "editorial_label": "closeness with a high trust threshold",
                    "left": "intimacy_depth",
                    "right": "emotional_threshold",
                    "evidence": ["depth_intimacy", "thresholded_intimacy"],
                }
            ]
        },
        master_selector={
            "relational_line": {
                "line_id": "relational_candidate",
                "contradiction_ids": ["closeness_vs_threshold"],
            },
            "work_visibility_line": {"line_id": "visibility_candidate"},
        },
    )

    state = build_canonical_natal_state_v1(bundle, include_debug=True)
    graph = build_natal_meaning_graph(state)

    node_ids = {node["node_id"] for node in graph["nodes"]}
    edge_types = {edge["type"] for edge in graph["edges"]}
    hook_target_ids = {hook["target_node_id"] for hook in graph["activation_hooks"]}

    assert "promise_build_safe_intimacy" in node_ids
    assert "contradiction_closeness_vs_threshold" in node_ids
    assert "spine:relational_line" in node_ids
    assert "spine:work_visibility_line" in node_ids
    assert "integrates_through" in edge_types
    assert "contradiction_closeness_vs_threshold" in hook_target_ids
    assert "promise_mature_visibility" in hook_target_ids


def test_golden_manifest_seeds_minimum_foundation_corpus() -> None:
    manifest_path = (
        Path(__file__).resolve().parent / "golden" / "natal_canonical_core" / "manifest.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["minimum_chart_count_for_ontology_acceptance"] == 15
    assert len(manifest["cases"]) >= 15
