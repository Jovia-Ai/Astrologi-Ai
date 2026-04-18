from app.transit.narrative.archetype_engine import build_insight_pack
from app.transit.present.public_builder import build_public_event


def _sample_item(*, with_sign: bool = True) -> dict:
    item = {
        "event_id": "evt_saturn_aries_3",
        "transit_body": "Saturn",
        "natal_point": "Mercury",
        "aspect": "square",
        "phase": "applying",
        "bucket": "long",
        "houses": {"transit_in_natal_house": 3},
        "source_pos": {"sign": "Aries", "deg": 12.3},
        "target_pos": {"sign": "Virgo", "deg": 12.4},
        "orb_deg": 0.1,
        "domains": ["mind", "relationships"],
        "interpretation": {"headline": "Test", "summary": "Test"},
        "ranking": {"tier": "main", "weight": 1.2},
    }
    if with_sign:
        item["signs"] = {"transit_body_sign": "Aries"}
    return item


def test_insight_pack_deterministic() -> None:
    first = build_insight_pack(_sample_item(), seed=1234)
    second = build_insight_pack(_sample_item(), seed=1234)
    third = build_insight_pack(_sample_item(), seed=1235)
    assert first == second
    assert first != third


def test_insight_pack_has_required_keys_and_lengths() -> None:
    out = build_insight_pack(_sample_item(), seed=77, voice_style="you")
    assert set(out.keys()) == {"conflict", "shadow", "upper", "conflict_short"}
    for key in ("conflict", "shadow", "upper"):
        assert out[key]
        assert len(out[key]) <= 280


def test_insight_pack_blacklist_absent() -> None:
    out = build_insight_pack(_sample_item(), seed=99, voice_style="you")
    text = " ".join(out.values()).lower()
    for banned in ("orb", "aspect", "applying", "separating", "percentile", "marker", "tier"):
        assert banned not in text


def test_insight_pack_fallback_when_sign_missing() -> None:
    out = build_insight_pack(_sample_item(with_sign=False), seed=88, voice_style="you")
    assert out["conflict"]
    assert out["upper"]


def test_public_event_contains_insight_pack_block_with_three_items() -> None:
    event = build_public_event(_sample_item())
    insight_blocks = [block for block in event.blocks if block.type == "insight_pack"]
    assert len(insight_blocks) == 1
    items = insight_blocks[0].items or []
    assert len(items) == 3
    keys = [item.get("key") for item in items if isinstance(item, dict)]
    assert keys == ["conflict", "shadow", "upper"]


def test_public_event_signature_follows_headline() -> None:
    event = build_public_event(_sample_item())
    block_types = [block.type for block in event.blocks]
    assert "headline" in block_types
    assert "signature" in block_types
    assert block_types.index("signature") == block_types.index("headline") + 1
    signature = event.blocks[block_types.index("signature")]
    assert signature.text is not None
    assert "Saturn" in signature.text
    assert "Koç" in signature.text
    assert "3. Ev" in signature.text
    assert "□ Natal Mercury" in signature.text
    assert signature.text.startswith("Transit ")
    assert " • orb " in signature.text
    assert "Bilinmiyor" not in signature.text
    assert signature.phase == "applying"
    assert signature.duration == "months"


def test_voice_style_you_includes_soft_modality() -> None:
    out = build_insight_pack(_sample_item(), seed=11, voice_style="you")
    joined = " ".join(out.values()).lower()
    assert any(token in joined for token in ("hissedebilirsin", "fark edebilirsin", "bazen", "olabilir"))
