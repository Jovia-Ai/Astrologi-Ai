import re
from collections import Counter

from app.natal.narrative.profile_narrative_engine import build_profile_narrative
from app.natal.narrative.signature_engine import normalize_facts
from app.natal.natal_graph import build_natal_graph


def _chart_a() -> dict:
    return {
        "birth_datetime": "1996-12-28T07:10:00+02:00",
        "location": {"city": "Istanbul, TR"},
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
    }


def _planets_a() -> list[dict]:
    return [
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
        {"planet": "Chiron", "sign": "Libra", "house": 10},
        {"planet": "Fortune", "sign": "Taurus", "house": 5},
        {"planet": "Ascendant", "sign": "Capricorn", "house": 1, "is_point": True},
        {"planet": "Midheaven", "sign": "Libra", "house": 10, "is_point": True},
    ]


def _aspects_a() -> list[dict]:
    return [
        {"planet1": "Sun", "planet2": "Saturn", "aspect": "Square", "orb": 5.59},
        {"planet1": "Moon", "planet2": "Venus", "aspect": "Trine", "orb": 0.24},
        {"planet1": "Mars", "planet2": "Saturn", "aspect": "Opposition", "orb": 3.23},
        {"planet1": "Mars", "planet2": "Jupiter", "aspect": "Trine", "orb": 3.63},
        {"planet1": "Mars", "planet2": "Neptune", "aspect": "Trine", "orb": 1.24},
        {"planet1": "Jupiter", "planet2": "Neptune", "aspect": "Conjunction", "orb": 2.39},
        {"planet1": "Jupiter", "planet2": "Midheaven", "aspect": "Square", "orb": 0.99},
        {"planet1": "Neptune", "planet2": "Midheaven", "aspect": "Square", "orb": 1.4},
    ]


def _chart_b() -> dict:
    return {
        "birth_datetime": "1993-06-10T19:45:00+03:00",
        "location": {"city": "Ankara, TR"},
        "house_positions": {
            "1": {"sign": "Leo"},
            "2": {"sign": "Virgo"},
            "3": {"sign": "Libra"},
            "4": {"sign": "Scorpio"},
            "5": {"sign": "Sagittarius"},
            "6": {"sign": "Capricorn"},
            "7": {"sign": "Aquarius"},
            "8": {"sign": "Pisces"},
            "9": {"sign": "Aries"},
            "10": {"sign": "Taurus"},
            "11": {"sign": "Gemini"},
            "12": {"sign": "Cancer"},
        },
        "angles": {
            "ascendant_sign": "Leo",
            "midheaven_sign": "Taurus",
        },
    }


def _planets_b() -> list[dict]:
    return [
        {"planet": "Sun", "sign": "Gemini", "house": 11},
        {"planet": "Moon", "sign": "Pisces", "house": 8},
        {"planet": "Mercury", "sign": "Gemini", "house": 11},
        {"planet": "Venus", "sign": "Cancer", "house": 12},
        {"planet": "Mars", "sign": "Leo", "house": 1},
        {"planet": "Jupiter", "sign": "Libra", "house": 3},
        {"planet": "Saturn", "sign": "Aquarius", "house": 7},
        {"planet": "Uranus", "sign": "Capricorn", "house": 6},
        {"planet": "Neptune", "sign": "Capricorn", "house": 6},
        {"planet": "Pluto", "sign": "Scorpio", "house": 4},
        {"planet": "Fortune", "sign": "Gemini", "house": 11},
        {"planet": "Ascendant", "sign": "Leo", "house": 1, "is_point": True},
        {"planet": "Midheaven", "sign": "Taurus", "house": 10, "is_point": True},
    ]


def _aspects_b() -> list[dict]:
    return [
        {"planet1": "Moon", "planet2": "Venus", "aspect": "Trine", "orb": 0.9},
        {"planet1": "Fortune", "planet2": "Jupiter", "aspect": "Trine", "orb": 1.2},
        {"planet1": "Mars", "planet2": "Ascendant", "aspect": "Conjunction", "orb": 2.0},
    ]


def _graph(chart: dict, planets: list[dict], aspects: list[dict]) -> dict:
    return build_natal_graph(chart_data=chart, planets=planets, aspects=aspects)


def _chart_c() -> dict:
    return {
        "birth_datetime": "1988-02-14T05:20:00+03:00",
        "location": {"city": "Izmir, TR"},
        "house_positions": {
            "1": {"sign": "Scorpio"},
            "2": {"sign": "Sagittarius"},
            "3": {"sign": "Capricorn"},
            "4": {"sign": "Aquarius"},
            "5": {"sign": "Pisces"},
            "6": {"sign": "Aries"},
            "7": {"sign": "Taurus"},
            "8": {"sign": "Gemini"},
            "9": {"sign": "Cancer"},
            "10": {"sign": "Leo"},
            "11": {"sign": "Virgo"},
            "12": {"sign": "Libra"},
        },
        "angles": {
            "ascendant_sign": "Scorpio",
            "midheaven_sign": "Leo",
        },
    }


def _planets_c() -> list[dict]:
    return [
        {"planet": "Sun", "sign": "Aquarius", "house": 4},
        {"planet": "Moon", "sign": "Aquarius", "house": 4},
        {"planet": "Mercury", "sign": "Capricorn", "house": 3, "retrograde": True},
        {"planet": "Venus", "sign": "Pisces", "house": 5},
        {"planet": "Mars", "sign": "Cancer", "house": 9},
        {"planet": "Jupiter", "sign": "Taurus", "house": 7},
        {"planet": "Saturn", "sign": "Capricorn", "house": 3},
        {"planet": "Uranus", "sign": "Sagittarius", "house": 2},
        {"planet": "Neptune", "sign": "Capricorn", "house": 3},
        {"planet": "Chiron", "sign": "Leo", "house": 10},
        {"planet": "Fortune", "sign": "Pisces", "house": 5},
        {"planet": "Ascendant", "sign": "Scorpio", "house": 1, "is_point": True},
        {"planet": "Midheaven", "sign": "Leo", "house": 10, "is_point": True},
    ]


def _aspects_c() -> list[dict]:
    return [
        {"planet1": "Mars", "planet2": "Neptune", "aspect": "Trine", "orb": 1.8},
        {"planet1": "Moon", "planet2": "Venus", "aspect": "Sextile", "orb": 1.5},
        {"planet1": "Saturn", "planet2": "Mercury", "aspect": "Conjunction", "orb": 1.1},
        {"planet1": "Fortune", "planet2": "Jupiter", "aspect": "Conjunction", "orb": 2.2},
    ]


def _semantic_tokens(text: str) -> set[str]:
    stopwords = {
        "ve",
        "ile",
        "bu",
        "bir",
        "da",
        "de",
        "için",
        "gibi",
        "ama",
        "çok",
        "daha",
        "sen",
        "sende",
        "senin",
    }
    return {
        token
        for token in re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ]+", str(text or "").lower())
        if len(token) >= 3 and token not in stopwords
    }


def _semantic_overlap(a: str, b: str) -> float:
    left = _semantic_tokens(a)
    right = _semantic_tokens(b)
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _assert_block_quality(block: dict) -> None:
    sentence_count = len(re.findall(r"[.!?]", block["body"]))
    assert 3 <= sentence_count <= 4
    body_sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", str(block["body"])) if sentence.strip()]
    assert sum(1 for sentence in body_sentences if sentence.lower().startswith("sende ")) <= 1
    merged_public = " ".join(
        [
            str(block.get("headline") or ""),
            str(block.get("teaser") or ""),
            str(block.get("body") or ""),
            str(block.get("astro_hint") or ""),
            " ".join(str(chip) for chip in block.get("chips") or []),
        ]
    )
    lowered_body = str(block.get("body") or "").lower()
    lowered_micro = str(block.get("micro") or "").lower()
    for banned in (
        "vitrin",
        "çıktı",
        "cikti",
        "rota",
        "upgrade",
        "kalibrasyon",
        "paket",
        "workflow",
        "sprint",
    ):
        assert not re.search(rf"\b{re.escape(banned)}\b", lowered_body)
        assert not re.search(rf"\b{re.escape(banned)}\b", lowered_micro)
    for debuggy in ("kimlik hattında", "kariyer hattında", "akış tarafında", "zihinsel tarafta"):
        assert debuggy not in lowered_body
        assert debuggy not in lowered_micro
    for awkward in ("yakınlık sende yüzey değil", "söz senin kasın", "sende kapı açan taraf"):
        assert awkward not in merged_public.lower()
    for templated in ("bu tarafının dışarıdaki hali", "yetenek tarafında ilk görülen şey", "dışarıya verdiğin iş sinyalinde ilk görülen taraf"):
        assert templated not in lowered_body


def test_profile_narrative_signature_supports_natural_english_output() -> None:
    chart = _chart_a()
    graph = _graph(chart, _planets_a(), _aspects_a())

    out = build_profile_narrative(
        chart,
        graph,
        locale="en",
        include_debug=False,
        engine_override="signature",
    )

    profile_public = out.get("profile_public") if isinstance(out.get("profile_public"), dict) else {}
    blocks = profile_public.get("blocks") if isinstance(profile_public.get("blocks"), list) else []
    assert len(blocks) >= 5
    merged = " ".join(
        " ".join(
            [
                str(block.get("headline") or ""),
                str(block.get("teaser") or ""),
                str(block.get("body") or ""),
                str(block.get("micro") or ""),
                str(block.get("astro_hint") or ""),
            ]
        )
        for block in blocks
        if isinstance(block, dict)
    ).lower()

    assert "you " in merged
    assert "the way you" in merged or "your " in merged
    assert "yükselen" not in merged
    assert "ilişkide" not in merged
    assert "görünürlük" not in merged
    assert "yakınlık" not in merged


def test_profile_narrative_is_deterministic_for_same_chart() -> None:
    chart = _chart_a()
    graph = _graph(chart, _planets_a(), _aspects_a())
    first = build_profile_narrative(chart, graph, include_debug=True, engine_override="signature")
    second = build_profile_narrative(chart, graph, include_debug=True, engine_override="signature")

    assert first["profile_public"] == second["profile_public"]
    assert first["profile_public"]["engine_version"] == "profile_narrative_v2"
    assert first["profile_public"]["blocks"]
    assert len(first["profile_public"]["blocks"]) == 7


def test_profile_narrative_public_blocks_have_required_fields_and_separate_micro() -> None:
    chart = _chart_a()
    graph = _graph(chart, _planets_a(), _aspects_a())
    payload = build_profile_narrative(chart, graph, include_debug=True, engine_override="signature")

    public_blocks = payload["profile_public"]["blocks"]
    assert len(public_blocks) == 7

    for block in public_blocks:
        assert {"id", "headline", "teaser", "body", "micro", "chips", "astro_sources"} <= set(block.keys())
        assert block["headline"]
        assert block["teaser"]
        assert block["body"]
        assert isinstance(block["micro"], str)
        assert isinstance(block["astro_sources"], list)
        assert block["body"] != block["micro"]
        if block["micro"]:
            assert block["micro"] not in block["body"]
            lowered_micro = block["micro"].lower()
            for banned in ("48 saat", "sprint", "tek adım", "tek paylaşım", "en iyi çözüm", "iyi gelir", "gerekir", "strateji", "rota", "vitrin", "çıktı", "paket", " senden", "çok tipik"):
                assert banned not in lowered_micro
            for debuggy in ("kimlik hattında", "kariyer hattında", "akış tarafında", "zihinsel tarafta"):
                assert debuggy not in lowered_micro
        lowered_body = str(block.get("body") or "").lower()
        assert not re.search(
            r"\b(?:merkür|merkur|güneş|gunes|ay|venüs|venus|mars|jüpiter|jupiter|satürn|saturn|uran[üu]s|nept[üu]n|pl[üu]ton)\b",
            lowered_body,
            re.IGNORECASE,
        )
        _assert_block_quality(block)
        if block["astro_sources"]:
            assert len(block["astro_sources"]) <= 3
    assert any(
        any(marker in str(block.get("body") or "") for marker in ("Yük arttığında", "Belirsizlikte", "Kırılgan yerde", "Denge bozulduğunda"))
        and any(marker in str(block.get("body") or "") for marker in ("Yerine oturduğunda", "Güven oluştuğunda", "Güçlü halinde", "Denge geldiğinde"))
        for block in public_blocks
    )


def test_profile_narrative_debug_has_evidence_and_v2_metadata() -> None:
    chart = _chart_a()
    graph = _graph(chart, _planets_a(), _aspects_a())
    payload = build_profile_narrative(chart, graph, include_debug=True, engine_override="signature")

    public_blocks = payload["profile_public"]["blocks"]
    debug_blocks = payload["profile_internal"]["blocks_debug"]
    assert len(public_blocks) == 7
    assert len(debug_blocks) == 7
    debug_by_id = {block["id"]: block for block in debug_blocks}

    for block in public_blocks:
        debug_block = debug_by_id[block["id"]]
        if not debug_block.get("fallback_reason"):
            assert len(debug_block["evidence"]) >= 2
        assert debug_block["engine"] == "signature"
        assert debug_block["template_id"]
        assert debug_block["template_variant_id"]
        assert debug_block["seed_material"]
        assert debug_block["seed_version"] == "profile_signature_seed_v2_s1"
        assert debug_block["selected_template_index"] in {0, 1, 2, 3}
        assert debug_block["render_mode"] in {"A", "B", "C", "D"}


def test_profile_narrative_quality_holds_across_multiple_chart_shapes() -> None:
    charts = [
        (_chart_b(), _planets_b(), _aspects_b()),
        (_chart_c(), _planets_c(), _aspects_c()),
    ]

    for chart, planets, aspects in charts:
        graph = _graph(chart, planets, aspects)
        payload = build_profile_narrative(chart, graph, include_debug=False, engine_override="signature")
        blocks = payload["profile_public"]["blocks"]
        assert len(blocks) == 7
        for block in blocks:
            _assert_block_quality(block)


def test_profile_narrative_seeds_and_bodies_change_across_different_charts() -> None:
    chart_a = _chart_a()
    graph_a = _graph(chart_a, _planets_a(), _aspects_a())
    chart_b = _chart_b()
    graph_b = _graph(chart_b, _planets_b(), _aspects_b())
    chart_c = _chart_c()
    graph_c = _graph(chart_c, _planets_c(), _aspects_c())

    facts_a = normalize_facts(chart_a, graph_a)
    facts_b = normalize_facts(chart_b, graph_b)
    facts_c = normalize_facts(chart_c, graph_c)
    payload_a = build_profile_narrative(chart_a, graph_a, include_debug=True, engine_override="signature")
    payload_b = build_profile_narrative(chart_b, graph_b, include_debug=True, engine_override="signature")
    payload_c = build_profile_narrative(chart_c, graph_c, include_debug=True, engine_override="signature")

    assert facts_a["seed"] != facts_b["seed"]
    assert facts_a["seed"] != facts_c["seed"]
    assert facts_b["seed"] != facts_c["seed"]
    bodies_a = {block["id"]: block["body"] for block in payload_a["profile_public"]["blocks"]}
    bodies_b = {block["id"]: block["body"] for block in payload_b["profile_public"]["blocks"]}
    bodies_c = {block["id"]: block["body"] for block in payload_c["profile_public"]["blocks"]}
    assert any(bodies_a.get(block_id) != bodies_b.get(block_id) for block_id in set(bodies_a) & set(bodies_b))
    assert any(bodies_a.get(block_id) != bodies_c.get(block_id) for block_id in set(bodies_a) & set(bodies_c))


def test_profile_narrative_fallback_path_keeps_stable_debug_evidence() -> None:
    chart = {
        "birth_datetime": "2001-01-01T10:00:00+03:00",
        "location": {"city": "Bursa, TR"},
        "angles": {"ascendant_sign": "Aries", "midheaven_sign": "Capricorn"},
        "house_positions": {"1": {"sign": "Aries"}, "10": {"sign": "Capricorn"}},
    }
    graph = {
        "chart_planets": {},
        "chart_aspects": [],
        "house_rulers": {
            "1": {"cusp_sign": "Aries", "primary_ruler": "Mars", "primary_ruler_pos": {"house": 1, "sign": "Aries"}},
            "3": {"cusp_sign": "Gemini", "primary_ruler": "Mercury", "primary_ruler_pos": {"house": 3, "sign": "Gemini"}},
            "4": {"cusp_sign": "Cancer", "primary_ruler": "Moon", "primary_ruler_pos": {"house": 4, "sign": "Cancer"}},
            "7": {"cusp_sign": "Libra", "primary_ruler": "Venus", "primary_ruler_pos": {"house": 7, "sign": "Libra"}},
            "9": {"cusp_sign": "Sagittarius", "primary_ruler": "Jupiter", "primary_ruler_pos": {"house": 9, "sign": "Sagittarius"}},
            "10": {"cusp_sign": "Capricorn", "primary_ruler": "Saturn", "primary_ruler_pos": {"house": 10, "sign": "Capricorn"}},
        },
    }

    first = build_profile_narrative(chart, graph, include_debug=True, engine_override="signature")
    second = build_profile_narrative(chart, graph, include_debug=True, engine_override="signature")

    assert first == second
    for block in first["profile_internal"]["blocks_debug"]:
        assert len(block["evidence"]) >= 2
        assert block["template_id"]
        assert block["primary_signature_id"]


def test_profile_narrative_chart_with_strong_sparks_uses_multiple_spark_signatures() -> None:
    chart = _chart_a()
    graph = _graph(chart, _planets_a(), _aspects_a())
    payload = build_profile_narrative(chart, graph, include_debug=True, engine_override="signature")

    spark_blocks = [
        block
        for block in payload["profile_internal"]["blocks_debug"]
        if str(block.get("spark_signature_id") or "").strip()
    ]
    assert len(spark_blocks) >= 3


def test_identity_block_prioritizes_identity_spine_over_saturn_third_only_signature() -> None:
    chart = _chart_a()
    graph = _graph(chart, _planets_a(), _aspects_a())
    payload = build_profile_narrative(chart, graph, include_debug=True, engine_override="signature")

    identity_debug = next(block for block in payload["profile_internal"]["blocks_debug"] if block["id"] == "identity_aura")
    assert str(identity_debug["primary_signature_id"]).startswith("identity_")
    assert identity_debug["primary_signature_id"] != "mind_saturn_3rd_boundary"


def test_identity_block_uses_identity_centered_language_when_identity_signatures_are_strong() -> None:
    chart = _chart_a()
    graph = _graph(chart, _planets_a(), _aspects_a())
    payload = build_profile_narrative(chart, graph, include_debug=True, engine_override="signature")

    identity_public = next(block for block in payload["profile_public"]["blocks"] if block["id"] == "identity_aura")
    body = str(identity_public["body"]).lower()
    assert any(token in body for token in ("özgün", "omurga", "büyük resmi", "kendi yolunu", "çizgin"))
    assert "mesaj" not in body


def test_profile_narrative_uses_multiple_render_modes_when_possible() -> None:
    chart = _chart_a()
    graph = _graph(chart, _planets_a(), _aspects_a())
    payload = build_profile_narrative(chart, graph, include_debug=True, engine_override="signature")

    modes = {
        str(block.get("render_mode") or "")
        for block in payload["profile_internal"]["blocks_debug"]
        if str(block.get("render_mode") or "")
    }
    assert len(modes) >= 2


def test_profile_narrative_reduces_repeated_discourse_starters() -> None:
    chart = _chart_a()
    graph = _graph(chart, _planets_a(), _aspects_a())
    payload = build_profile_narrative(chart, graph, include_debug=True, engine_override="signature")

    starters = []
    for block in payload["profile_public"]["blocks"]:
        words = str(block.get("body") or "").split()
        starters.append(" ".join(words[:3]).lower())
    counts = Counter(starters)
    assert counts
    assert max(counts.values()) <= 2


def test_profile_narrative_legacy_override_keeps_schema() -> None:
    chart = _chart_b()
    graph = _graph(chart, _planets_b(), _aspects_b())
    payload = build_profile_narrative(chart, graph, include_debug=True, engine_override="legacy")

    blocks = payload["profile_public"]["blocks"]
    debug_blocks = payload["profile_internal"]["blocks_debug"]
    assert len(blocks) == 7
    assert len(debug_blocks) == 7
    assert all({"id", "headline", "teaser", "body", "chips"} <= set(block.keys()) for block in blocks)
    assert all(block.get("engine") == "legacy" for block in debug_blocks)
