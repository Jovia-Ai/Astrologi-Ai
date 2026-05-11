from __future__ import annotations

from app.meaning.meaning_graph_v1_1_builder import build_meaning_graph_v1_1


def _sample_payload() -> dict:
    return {
        "core_story_ui": {
            "headline": "Ritmini korudugunda yon duygun gucleniyor",
            "text": (
                "Disarida net gorunursun ama zorlandiginda sabirsizlik artabilir. "
                "Bu cizgi mekanizmani ve etkini birlikte tasir."
            ),
            "drivers": [
                {"type": "angle", "key": "ASC", "value": "Capricorn"},
                {"type": "house", "key": "asc_ruler_house", "value": 3},
            ],
        },
        "user_compact": {
            "domains": [
                {
                    "domain": "identity",
                    "title": "Identity",
                    "summary": (
                        "Kimlik cizgin uzun vadeli dusunur. "
                        "Insanlar sende guvenilir bir etki hisseder."
                    ),
                    "highlights": [{"text": "Sakin oldugunda kararlar netlesir."}],
                }
            ],
            "micro_insights": [
                {
                    "domain": "identity",
                    "text": "Guven cizgin hizli toparlar.",
                    "evidence": [{"ref": "saturn_house_3", "type": "planet"}],
                }
            ],
        },
        "personality_imprint": {
            "entries": [
                {
                    "label_tr": "Gunes 1. Ev",
                    "trait": "Kendini net gostermek istersin.",
                    "shadow": "Bazen fazla sert gorunebilirsin.",
                    "gift": "Gucunu yon cizgisine cevirebilirsin.",
                    "drive": "Kendi ritmini korumak istersin.",
                    "background_hint": "Erken donemde sorumluluk agirlasmis olabilir.",
                    "tags": ["gorunurluk", "kimlik"],
                    "support_keys": ["moon_leo"],
                }
            ]
        },
        "supporting_threads": [
            {
                "id": "identity_mechanics",
                "title": "Kimlik",
                "paragraph": "Disa yansima gucludur ama iceride ton hizli degisebilir.",
                "proof_raw": "Saturn · 3. ev · Aries",
                "chips": ["Netlik", "Ritim"],
            }
        ],
    }


def test_meaning_graph_v1_1_layers_and_node_types_are_valid() -> None:
    sample = _sample_payload()
    graph = build_meaning_graph_v1_1(
        core_story_ui=sample["core_story_ui"],
        user_compact=sample["user_compact"],
        personality_imprint=sample["personality_imprint"],
        supporting_threads=sample["supporting_threads"],
        locale="tr",
    )

    assert graph["version"] == "meaning_graph_v1_1"
    assert graph["canonical_intent"] is True
    assert "relations" not in graph
    assert "groups" not in graph

    assert graph["nodes"]
    allowed_types = {"narrative", "signal", "guidance", "quality", "reference"}
    node_types = {node["node_type"] for node in graph["nodes"]}
    assert node_types <= allowed_types
    assert "narrative" in node_types
    assert "signal" in node_types

    for node in graph["nodes"]:
        layers = node["layers"]
        assert 1 <= len(layers) <= 3
        total = sum(float(layer["weight"]) for layer in layers)
        assert abs(total - 1.0) <= 0.01
        weights = [float(layer["weight"]) for layer in layers]
        assert weights == sorted(weights, reverse=True)
        max_layer = max(layers, key=lambda item: float(item["weight"]))["layer"]
        assert node["primary_layer"] == max_layer


def test_meaning_graph_v1_1_long_prose_with_house_reference_is_not_reference() -> None:
    graph = build_meaning_graph_v1_1(
        core_story_ui=None,
        user_compact=None,
        personality_imprint=None,
        supporting_threads=[
            {
                "id": "prose_case",
                "title": "Uzun Prose",
                "paragraph": (
                    "Saturn 3. ev vurgusu zihinsel ritmini etkiler ama burada asıl mesele korku değil, "
                    "netlik ihtiyacını doğru tonda ifade etmeyi öğrenmendir."
                ),
            }
        ],
        locale="tr",
    )
    assert graph["nodes"]
    node = graph["nodes"][0]
    assert node["node_type"] != "reference"
    assert node["node_type"] == "narrative"


def test_meaning_graph_v1_1_potential_title_prioritizes_potential_primary_layer() -> None:
    graph = build_meaning_graph_v1_1(
        core_story_ui=None,
        user_compact=None,
        personality_imprint={
            "entries": [
                {
                    "label_tr": "Gunes 1. Ev",
                    "gift": "Bu yerlesim sende guclu bir kimlik kapasitesi ve buyume enerjisi yaratir.",
                }
            ]
        },
        supporting_threads=None,
        locale="tr",
    )
    potential_node = next(node for node in graph["nodes"] if "Potential" in node["title"])
    assert potential_node["primary_layer"] == "potential"


def test_meaning_graph_v1_1_shadow_title_prioritizes_shadow_primary_layer() -> None:
    graph = build_meaning_graph_v1_1(
        core_story_ui=None,
        user_compact=None,
        personality_imprint={
            "entries": [
                {
                    "label_tr": "Venus 12. Ev",
                    "shadow": "Denge bozuldugunda geri cekilme ve duyguyu saklama gorulebilir.",
                }
            ]
        },
        supporting_threads=None,
        locale="tr",
    )
    shadow_node = next(node for node in graph["nodes"] if "Shadow" in node["title"])
    assert shadow_node["primary_layer"] == "shadow"


def test_meaning_graph_v1_1_contrast_rule_prefers_two_layer_mix() -> None:
    graph = build_meaning_graph_v1_1(
        core_story_ui=None,
        user_compact=None,
        personality_imprint=None,
        supporting_threads=[
            {
                "id": "contrast_case",
                "title": "Thread",
                "paragraph": "Disa acik gorunursun ama zorlandiginda bir anda kapanabilirsin.",
            }
        ],
        locale="tr",
    )
    assert graph["nodes"]
    node = graph["nodes"][0]
    layers = node["layers"]
    assert len(layers) == 2
    layer_set = {layer["layer"] for layer in layers}
    assert layer_set in ({"effect", "shadow"}, {"mechanism", "effect"})
    assert [float(layer["weight"]) for layer in layers] == sorted(
        [float(layer["weight"]) for layer in layers], reverse=True
    )


def test_meaning_graph_v1_1_preserves_typed_evidence() -> None:
    sample = _sample_payload()
    graph = build_meaning_graph_v1_1(
        core_story_ui=sample["core_story_ui"],
        user_compact=sample["user_compact"],
        personality_imprint=sample["personality_imprint"],
        supporting_threads=sample["supporting_threads"],
        locale="tr",
    )
    evidence = graph["evidence"]
    assert evidence

    driver_structured = [
        item for item in evidence if item["kind"] == "signal_driver" and isinstance(item["structured_payload"], dict)
    ]
    assert any(item["source_path"].startswith("public.core_story_ui.drivers[") for item in driver_structured)
    assert any("type" in item["structured_payload"] for item in driver_structured)

    assert any(
        item["kind"] == "reference"
        and isinstance(item["structured_payload"], dict)
        and "support_keys" in item["structured_payload"]
        for item in evidence
    )
    assert any(
        item["kind"] == "reference"
        and isinstance(item["structured_payload"], dict)
        and "proof_raw" in item["structured_payload"]
        for item in evidence
    )
    assert any(
        item["kind"] == "signal"
        and isinstance(item["structured_payload"], dict)
        and "chips" in item["structured_payload"]
        for item in evidence
    )


def test_meaning_graph_v1_1_dedupe_fingerprint_is_stable_against_reorder() -> None:
    payload = _sample_payload()

    graph_a = build_meaning_graph_v1_1(
        core_story_ui=payload["core_story_ui"],
        user_compact=payload["user_compact"],
        personality_imprint=payload["personality_imprint"],
        supporting_threads=payload["supporting_threads"],
        locale="tr",
    )

    reordered = _sample_payload()
    reordered["user_compact"]["domains"] = list(reversed(reordered["user_compact"]["domains"]))
    reordered["supporting_threads"] = list(reversed(reordered["supporting_threads"]))
    graph_b = build_meaning_graph_v1_1(
        core_story_ui=reordered["core_story_ui"],
        user_compact=reordered["user_compact"],
        personality_imprint=reordered["personality_imprint"],
        supporting_threads=reordered["supporting_threads"],
        locale="tr",
    )

    fingerprints_a = sorted(node["dedupe_fingerprint"] for node in graph_a["nodes"])
    fingerprints_b = sorted(node["dedupe_fingerprint"] for node in graph_b["nodes"])
    assert fingerprints_a == fingerprints_b


def test_meaning_graph_v1_1_primary_layer_matches_max_weight_layer() -> None:
    sample = _sample_payload()
    graph = build_meaning_graph_v1_1(
        core_story_ui=sample["core_story_ui"],
        user_compact=sample["user_compact"],
        personality_imprint=sample["personality_imprint"],
        supporting_threads=sample["supporting_threads"],
        locale="tr",
    )
    for node in graph["nodes"]:
        max_layer = max(node["layers"], key=lambda item: float(item["weight"]))["layer"]
        assert node["primary_layer"] == max_layer
