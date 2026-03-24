from app.natal.natal_graph_v2 import build_natal_graph_v2


def _sample_chart() -> dict:
    return {
        "house_positions": {
            "1": {"sign": "Capricorn"},
            "2": {"sign": "Aquarius"},
            "3": {"sign": "Pisces"},
            "4": {"sign": "Aries"},
            "5": {"sign": "Taurus"},
            "6": {"sign": "Gemini"},
            "7": {"sign": "Cancer"},
            "8": {"sign": "Leo"},
            "9": {"sign": "Virgo"},
            "10": {"sign": "Libra"},
            "11": {"sign": "Scorpio"},
            "12": {"sign": "Sagittarius"},
        },
        "angles": {
            "ascendant_sign": "Capricorn",
            "midheaven_sign": "Libra",
        },
        "planets": [
            {"planet": "Sun", "sign": "Capricorn", "house": 1},
            {"planet": "Moon", "sign": "Leo", "house": 8},
            {"planet": "Mercury", "sign": "Capricorn", "house": 1},
            {"planet": "Venus", "sign": "Sagittarius", "house": 12},
            {"planet": "Mars", "sign": "Virgo", "house": 9},
            {"planet": "Jupiter", "sign": "Capricorn", "house": 1},
            {"planet": "Saturn", "sign": "Aries", "house": 3},
            {"planet": "Uranus", "sign": "Aquarius", "house": 1},
            {"planet": "Neptune", "sign": "Capricorn", "house": 1},
            {"planet": "Pluto", "sign": "Sagittarius", "house": 11},
            {"planet": "Node", "sign": "Libra", "house": 9},
            {"planet": "Lilith", "sign": "Leo", "house": 8},
            {"planet": "Chiron", "sign": "Libra", "house": 10},
            {"planet": "Fortune", "sign": "Taurus", "house": 5},
        ],
        "aspects": [
            {"planet1": "Sun", "planet2": "Saturn", "aspect": "Square", "orb": 5.59},
            {"planet1": "Moon", "planet2": "Venus", "aspect": "Trine", "orb": 0.24},
            {"planet1": "Mars", "planet2": "Saturn", "aspect": "Opposition", "orb": 3.23},
            {"planet1": "Mars", "planet2": "Neptune", "aspect": "Trine", "orb": 1.24},
            {"planet1": "Jupiter", "planet2": "Neptune", "aspect": "Conjunction", "orb": 2.39},
            {"planet1": "Jupiter", "planet2": "Midheaven", "aspect": "Square", "orb": 0.99},
            {"planet1": "Neptune", "planet2": "Midheaven", "aspect": "Square", "orb": 1.4},
        ],
    }


def _subtle_private_chart() -> dict:
    return {
        "house_positions": {
            "1": {"sign": "Libra"},
            "2": {"sign": "Scorpio"},
            "3": {"sign": "Sagittarius"},
            "4": {"sign": "Capricorn"},
            "5": {"sign": "Aquarius"},
            "6": {"sign": "Pisces"},
            "7": {"sign": "Aries"},
            "8": {"sign": "Taurus"},
            "9": {"sign": "Gemini"},
            "10": {"sign": "Cancer"},
            "11": {"sign": "Leo"},
            "12": {"sign": "Virgo"},
        },
        "angles": {
            "ascendant_sign": "Libra",
            "midheaven_sign": "Cancer",
        },
        "planets": [
            {"planet": "Sun", "sign": "Virgo", "house": 12},
            {"planet": "Moon", "sign": "Gemini", "house": 9},
            {"planet": "Mercury", "sign": "Virgo", "house": 12},
            {"planet": "Venus", "sign": "Virgo", "house": 11},
            {"planet": "Mars", "sign": "Leo", "house": 11},
            {"planet": "Jupiter", "sign": "Pisces", "house": 6},
            {"planet": "Saturn", "sign": "Taurus", "house": 8},
            {"planet": "Uranus", "sign": "Aquarius", "house": 5},
            {"planet": "Neptune", "sign": "Capricorn", "house": 4},
            {"planet": "Pluto", "sign": "Sagittarius", "house": 3},
            {"planet": "Node", "sign": "Virgo", "house": 11},
            {"planet": "Lilith", "sign": "Scorpio", "house": 2},
            {"planet": "Chiron", "sign": "Scorpio", "house": 2},
            {"planet": "Fortune", "sign": "Gemini", "house": 9},
        ],
        "aspects": [
            {"planet1": "Sun", "planet2": "Mercury", "aspect": "Conjunction", "orb": 0.2},
            {"planet1": "Mercury", "planet2": "Moon", "aspect": "Square", "orb": 0.4},
            {"planet1": "Mercury", "planet2": "Saturn", "aspect": "Trine", "orb": 4.2},
            {"planet1": "Venus", "planet2": "Mars", "aspect": "Conjunction", "orb": 7.61},
            {"planet1": "Saturn", "planet2": "Neptune", "aspect": "Trine", "orb": 3.38},
        ],
    }


def test_build_natal_graph_v2_basic_build() -> None:
    graph = build_natal_graph_v2(_sample_chart())

    assert graph["engine_version"] == "natal_graph_v2"
    assert graph["chart_rulers"]
    assert graph["dispositor_chains"]
    assert graph["signature_motifs"]


def test_build_natal_graph_v2_rulers_present() -> None:
    graph = build_natal_graph_v2(_sample_chart())

    assert graph["chart_rulers"]["asc_ruler_primary"] == "Saturn"
    assert graph["chart_rulers"]["mc_ruler_primary"] == "Venus"
    assert graph["chart_rulers"]["house_rulers"]["7"]["primary"] == "Moon"


def test_build_natal_graph_v2_dispositor_chains_are_stable() -> None:
    graph = build_natal_graph_v2(_sample_chart())

    for body in ("Sun", "Venus", "Mars"):
        chain = graph["dispositor_chains"][body]
        assert isinstance(chain["primary_chain"], list)
        assert len(chain["primary_chain"]) <= 6
        assert chain["terminated"] is True
        assert chain["termination_reason"] in {
            "loop_detected",
            "domicile",
            "missing_data",
            "max_hops",
        }


def test_build_natal_graph_v2_vectors_are_clamped() -> None:
    graph = build_natal_graph_v2(_sample_chart())

    for bucket in (
        "domain_vectors",
        "familiarity_vectors",
        "sensitivity_vectors",
        "promise_vectors",
    ):
        for score in graph[bucket].values():
            assert 0.0 <= float(score) <= 1.0


def test_build_natal_graph_v2_evidence_exists_for_major_vectors() -> None:
    graph = build_natal_graph_v2(_sample_chart())

    evidence = graph["debug"]["vector_evidence"]
    assert evidence["identity"]
    assert evidence["intimacy_depth"]


def test_build_natal_graph_v2_is_deterministic() -> None:
    first = build_natal_graph_v2(_sample_chart())
    second = build_natal_graph_v2(_sample_chart())

    assert first == second


def test_build_natal_graph_v2_handles_missing_optional_bodies() -> None:
    chart = _sample_chart()
    chart["planets"] = [
        item
        for item in chart["planets"]
        if str(item.get("planet") or "") not in {"Chiron", "Fortune", "Vertex"}
    ]
    graph = build_natal_graph_v2(chart)

    assert graph["engine_version"] == "natal_graph_v2"
    assert graph["domain_vectors"]["identity"] >= 0.0
    assert graph["promise_vectors"]["mature_visibility"] >= 0.0


def test_build_natal_graph_v2_models_subtle_private_chart_without_fallback_collapse() -> None:
    graph = build_natal_graph_v2(_subtle_private_chart())

    motif_ids = {item["id"] for item in graph["signature_motifs"] if float(item.get("score") or 0.0) >= 0.18}

    assert len(motif_ids) >= 6
    assert {"private_intellect", "selective_bonding", "service_love", "relational_perfectionism", "mentalized_emotion"} <= motif_ids
    assert graph["debug"]["non_fallback_ratio"] >= 0.7
    assert graph["debug"]["motif_dispositor_support"]
