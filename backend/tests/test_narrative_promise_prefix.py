from app.transit.narrative.astrolog_narrative_engine import _build_promise_prefix


# S0-4: _build_promise_prefix helper'ının branching davranışını doğrular.
# Pozitif path: verdict strong/exact + bilinen domain → prefix string.
# Negatif path: zayıf verdict / boş points / general domain / None input → None.


def _spine(event_id: str = "evt_test") -> dict:
    return {"event_id": event_id}


def _promise(verdict: str, house: int) -> dict:
    return {
        "verdict": verdict,
        "connected_points": [{"house": house, "planet": "Mars", "sign": "aries"}],
    }


# ---------- Regression: mevcut davranış (prefix YOK) ----------

def test_weak_verdict_returns_none() -> None:
    assert _build_promise_prefix(_promise("weak", 10), _spine()) is None


def test_medium_verdict_returns_none() -> None:
    assert _build_promise_prefix(_promise("medium", 10), _spine()) is None


def test_none_promise_returns_none() -> None:
    assert _build_promise_prefix(None, _spine()) is None


def test_empty_connected_points_returns_none() -> None:
    promise = {"verdict": "strong", "connected_points": []}
    assert _build_promise_prefix(promise, _spine()) is None


def test_missing_house_returns_none() -> None:
    promise = {"verdict": "strong", "connected_points": [{"planet": "Mars"}]}
    assert _build_promise_prefix(promise, _spine()) is None


def test_general_domain_house_returns_none() -> None:
    # House 2 = HOUSE_DOMAIN_HINTS içinde "general" — prefix eklenmemeli.
    assert _build_promise_prefix(_promise("strong", 2), _spine()) is None


def test_house_5_returns_none_general_domain() -> None:
    # House 5 = general; prefix yok.
    assert _build_promise_prefix(_promise("strong", 5), _spine()) is None


# ---------- Pozitif: strong/exact verdict + bilinen domain ----------

def test_strong_verdict_career_house_10_returns_career_prefix() -> None:
    prefix = _build_promise_prefix(_promise("strong", 10), _spine())
    assert prefix is not None
    assert "kariyer" in prefix.lower()


def test_exact_verdict_relationships_house_7_returns_relationship_prefix() -> None:
    prefix = _build_promise_prefix(_promise("exact", 7), _spine())
    assert prefix is not None
    assert "ilişki" in prefix.lower() or "bağ" in prefix.lower()


def test_strong_verdict_identity_house_1_returns_identity_prefix() -> None:
    prefix = _build_promise_prefix(_promise("strong", 1), _spine())
    assert prefix is not None
    assert "kimlik" in prefix.lower()


def test_strong_verdict_home_house_4_returns_home_prefix() -> None:
    prefix = _build_promise_prefix(_promise("strong", 4), _spine())
    assert prefix is not None
    merged = prefix.lower()
    assert "kök" in merged or "ev" in merged or "zemin" in merged


def test_strong_verdict_mind_house_3_returns_mind_prefix() -> None:
    prefix = _build_promise_prefix(_promise("strong", 3), _spine())
    assert prefix is not None
    merged = prefix.lower()
    assert "zihin" in merged or "düşünce" in merged or "iletişim" in merged


def test_strong_verdict_inner_house_8_returns_inner_prefix() -> None:
    prefix = _build_promise_prefix(_promise("strong", 8), _spine())
    assert prefix is not None
    merged = prefix.lower()
    assert "iç" in merged or "derinlik" in merged


# ---------- Deterministic: aynı event_id aynı varyant ----------

def test_prefix_is_deterministic_per_event_id() -> None:
    promise = _promise("strong", 10)
    a = _build_promise_prefix(promise, _spine("evt_deterministic_1"))
    b = _build_promise_prefix(promise, _spine("evt_deterministic_1"))
    assert a == b and a is not None


def test_prefix_varies_between_event_ids() -> None:
    # Varyant rotation: farklı event_id'ler farklı varyant seçmeli (en az bir çift farklı olsun).
    promise = _promise("strong", 10)
    prefixes = {
        _build_promise_prefix(promise, _spine(f"evt_{i}"))
        for i in range(20)
    }
    # 2 varyant tanımlı; 20 event içinde ikisi de görülmüş olmalı.
    assert len(prefixes) == 2
