from app.transit.present.public_builder import (
    PERIOD_VERSION_SCHEMA,
    _build_period_teaser,
    _build_period_version,
    _compute_transit_set_hash,
    _first_sentence,
    _natal_fingerprint,
)


# S1-1: Teaser + lock + version shape'i için unit test'ler.
# Integration (build_public_response) ayrı test dosyasında; buradaki test'ler
# helper'ları izole doğruluyor.


# ---------- _first_sentence ----------

def test_first_sentence_returns_up_to_period() -> None:
    assert _first_sentence("Bu dönem güç değişiyor. Devamı gelecek.") == (
        "Bu dönem güç değişiyor."
    )


def test_first_sentence_handles_exclaim_and_question() -> None:
    assert _first_sentence("Şu sıralar farkındasın! Sonrası uzun.") == "Şu sıralar farkındasın!"
    assert _first_sentence("Hazır mısın? Devam.") == "Hazır mısın?"


def test_first_sentence_no_terminator_returns_whole() -> None:
    assert _first_sentence("Tek parça metin") == "Tek parça metin"


def test_first_sentence_empty_returns_empty() -> None:
    assert _first_sentence("") == ""
    assert _first_sentence(None) == ""  # type: ignore[arg-type]


# ---------- _build_period_teaser ----------

def test_teaser_uses_first_sentence_of_opening_and_big_picture() -> None:
    pc = {
        "period_opening": "Bu dönem ilişkilerde güç değişiyor. Devamı gelecek.",
        "big_picture": "En kritik pencere 3 hafta içinde. Sonra durulur.",
    }
    teaser = _build_period_teaser(pc)
    assert teaser == {
        "hook": "Bu dönem ilişkilerde güç değişiyor.",
        "highlight": "En kritik pencere 3 hafta içinde.",
    }


def test_teaser_returns_none_when_both_sources_empty() -> None:
    assert _build_period_teaser({}) is None
    assert _build_period_teaser({"period_opening": "", "big_picture": ""}) is None


def test_teaser_returns_hook_only_when_big_picture_empty() -> None:
    pc = {"period_opening": "Hook cümlesi var.", "big_picture": ""}
    teaser = _build_period_teaser(pc)
    assert teaser is not None
    assert teaser["hook"] == "Hook cümlesi var."
    assert teaser["highlight"] == ""


def test_teaser_char_limit_guard_under_120() -> None:
    # Mevcut period_opening / big_picture ilk cümleleri editorial; ≤120 char beklenir.
    pc = {
        "period_opening": (
            "Bu dönem önce kendini nasıl anlattığın değişiyor, sonra bunun etkisi "
            "dışarıda nasıl göründüğüne yansıyor."
        ),
        "big_picture": (
            "Kimlik hattında gereksiz fazlalıklar ayıklanıyor."
        ),
    }
    teaser = _build_period_teaser(pc)
    assert teaser is not None
    assert len(teaser["hook"]) <= 120, f"hook çok uzun: {len(teaser['hook'])}"
    assert len(teaser["highlight"]) <= 120, f"highlight çok uzun: {len(teaser['highlight'])}"


# ---------- _compute_transit_set_hash ----------

def test_transit_set_hash_deterministic_for_same_events() -> None:
    pc = {"featured_events": [{"event_id": "e1"}, {"event_id": "e2"}]}
    assert _compute_transit_set_hash(pc) == _compute_transit_set_hash(pc)


def test_transit_set_hash_order_independent() -> None:
    pc_a = {"featured_events": [{"event_id": "alpha"}, {"event_id": "beta"}]}
    pc_b = {"featured_events": [{"event_id": "beta"}, {"event_id": "alpha"}]}
    assert _compute_transit_set_hash(pc_a) == _compute_transit_set_hash(pc_b)


def test_transit_set_hash_differs_when_events_change() -> None:
    pc_a = {"featured_events": [{"event_id": "e1"}, {"event_id": "e2"}]}
    pc_b = {"featured_events": [{"event_id": "e1"}, {"event_id": "e3"}]}
    assert _compute_transit_set_hash(pc_a) != _compute_transit_set_hash(pc_b)


def test_transit_set_hash_none_for_empty() -> None:
    assert _compute_transit_set_hash({}) == "none"
    assert _compute_transit_set_hash({"featured_events": []}) == "none"


def test_transit_set_hash_falls_back_to_events_key() -> None:
    pc = {"events": [{"event_id": "only_one"}]}
    assert _compute_transit_set_hash(pc) != "none"


# ---------- _natal_fingerprint ----------

def test_natal_fingerprint_deterministic() -> None:
    natal = {"bodies": [{"name": "Sun", "lon": 91.5}], "angles": {"asc": 15.0}, "house_cusps": [0.0, 30.0]}
    assert _natal_fingerprint(natal) == _natal_fingerprint(natal)


def test_natal_fingerprint_differs_for_different_natals() -> None:
    a = {"bodies": [{"name": "Sun", "lon": 91.5}]}
    b = {"bodies": [{"name": "Sun", "lon": 92.5}]}
    assert _natal_fingerprint(a) != _natal_fingerprint(b)


def test_natal_fingerprint_empty_for_missing_or_invalid() -> None:
    assert _natal_fingerprint(None) == ""
    assert _natal_fingerprint({}) == ""
    assert _natal_fingerprint({"bodies": [], "angles": {}, "house_cusps": []}) == ""


# ---------- _build_period_version ----------

def test_period_version_eight_hex_chars() -> None:
    pc = {"track_id": "identity_spine", "featured_events": [{"event_id": "e1"}]}
    version = _build_period_version(None, pc)
    assert len(version) == 8
    assert all(c in "0123456789abcdef" for c in version)


def test_period_version_deterministic_for_same_input() -> None:
    pc = {"track_id": "creativity_5", "featured_events": [{"event_id": "e1"}, {"event_id": "e2"}]}
    assert _build_period_version(None, pc) == _build_period_version(None, pc)


def test_period_version_changes_when_track_id_changes() -> None:
    events = [{"event_id": "e1"}]
    v1 = _build_period_version(None, {"track_id": "identity_spine", "featured_events": events})
    v2 = _build_period_version(None, {"track_id": "creativity_5", "featured_events": events})
    assert v1 != v2


def test_period_version_changes_when_transit_set_changes() -> None:
    pc_a = {"track_id": "default", "featured_events": [{"event_id": "e1"}]}
    pc_b = {"track_id": "default", "featured_events": [{"event_id": "e2"}]}
    assert _build_period_version(None, pc_a) != _build_period_version(None, pc_b)


def test_period_version_incorporates_natal_when_provided() -> None:
    pc = {"track_id": "default", "featured_events": [{"event_id": "e1"}]}
    natal_a = {"bodies": [{"name": "Sun", "lon": 91.5}]}
    natal_b = {"bodies": [{"name": "Sun", "lon": 92.5}]}
    v_no_natal = _build_period_version(None, pc)
    v_natal_a = _build_period_version(natal_a, pc)
    v_natal_b = _build_period_version(natal_b, pc)
    assert v_no_natal != v_natal_a  # natal ekleyince değişmeli
    assert v_natal_a != v_natal_b   # farklı natal, farklı hash


def test_period_version_schema_const_is_v1() -> None:
    # Schema bump edildiğinde bu test güncellenmeli; aksi halde unbeknownst
    # mobile cache invalidation regression riski.
    assert PERIOD_VERSION_SCHEMA == "v1"


def test_period_version_changes_when_schema_bumped(monkeypatch) -> None:
    # Bu test: schema değişirse aynı input için hash değişir (migration stratejisi).
    pc = {"track_id": "default", "featured_events": [{"event_id": "e1"}]}
    v_before = _build_period_version(None, pc)
    import app.transit.present.public_builder as pb
    monkeypatch.setattr(pb, "PERIOD_VERSION_SCHEMA", "v_test_bump")
    v_after = pb._build_period_version(None, pc)
    assert v_before != v_after
