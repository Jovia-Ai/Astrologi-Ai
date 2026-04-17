from __future__ import annotations

from app.engine import rule_engine as rule_engine_module


def test_normalize_cache_preserves_fragment_output_and_order(monkeypatch) -> None:
    calls = {"count": 0}

    def fake_normalize_slot_text(text: str, slot: str) -> str:
        calls["count"] += 1
        return f"{slot}|{text.lower()}"

    monkeypatch.setattr(rule_engine_module, "normalize_slot_text", fake_normalize_slot_text)

    engine = rule_engine_module.RuleEngine.__new__(rule_engine_module.RuleEngine)
    trigger = {"type": "planet", "planet": "Sun", "sign": "capricorn", "house": 1}
    value = ["  SAME TEXT  ", "SAME TEXT", {"nested": [" SAME TEXT "]}]

    baseline = engine._normalize_fragments(
        value,
        "cause",
        trigger,
        "identity",
        "rule_1",
        normalize_slot_cache=None,
    )
    baseline_calls = calls["count"]
    assert baseline_calls == 3

    calls["count"] = 0
    cached = engine._normalize_fragments(
        value,
        "cause",
        trigger,
        "identity",
        "rule_1",
        normalize_slot_cache={},
    )
    assert calls["count"] == 1

    assert cached == baseline
    assert [entry["text"] for entry in cached] == ["SAME TEXT", "SAME TEXT", "SAME TEXT"]

