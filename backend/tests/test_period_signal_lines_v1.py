from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

import pytest

from app.api.routes import transits
from app.core.config import settings
from app.services.performance.cache_store import InMemoryCacheStore
from app.transit.narrative.canonical_natal_activation import build_canonical_period_spine
from app.transit.narrative.deep_archetype_engine import build_active_event_cards, build_period_core
from app.transit.narrative.life_chapter_detector import detect_active_life_chapter
from app.transit.present.public_builder import build_public_response


_FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "life_chapter"
_TECH_RE = re.compile(
    r"\b(satürn|saturn|neptün|neptune|plüton|pluto|uranüs|uranus|kiron|chiron|merkür|mercury|venüs|venus|jüpiter|jupiter)\b|"
    r"\b(kare|square|sextile|sextil|üçgen|trine|conjunction|kavuşum|opposition|karşıt)\b|"
    r"\b\d+\.\s*ev\b",
    re.IGNORECASE,
)
_BANNED_COPY_TOKENS = (
    "geçirgen",
    "üst anlam",
    "bütünlüklü yön",
    "yön duygusu",
    "aktivasyon",
    "mekanizma",
    "proses",
)


@pytest.fixture(autouse=True)
def _fresh_transit_route_cache(monkeypatch):
    monkeypatch.setattr(transits, "default_cache_store", InMemoryCacheStore())


def _load_fixture(group: str, name: str) -> dict:
    return json.loads((_FIXTURE_ROOT / group / f"{name}.json").read_text(encoding="utf-8"))


def _fixture_report(fixture: dict, *, events: list[dict] | None = None) -> dict:
    return {
        "locale": "tr",
        "metrics": {"pressure_index": 0.61, "support_index": 0.43},
        "natal": fixture["canonical_natal_state"],
        "display": {"items": events or fixture["transit_events"]},
    }


def _fixture_event_cards(events: list[dict]) -> list[dict]:
    return [
        {
            "event_id": str(event.get("event_id") or ""),
            "story_score": 0.95 - idx * 0.05,
            "selection_index": idx,
            "selection_mode": "fixture",
            "chapter_role": {"role": "builder"},
        }
        for idx, event in enumerate(events)
        if str(event.get("event_id") or "").strip()
    ]


@lru_cache(maxsize=8)
def _route_case(transit_date: str) -> dict:
    request = transits.TransitRequest(
        birth_date="1996-12-28",
        birth_time="07:10",
        birth_place="Istanbul, TR",
        birth_latitude=41.0082,
        birth_longitude=28.9784,
        birth_timezone="Europe/Istanbul",
        transit_date=transit_date,
        transit_time="12:00",
        transit_place="Istanbul, TR",
        transit_latitude=41.0082,
        transit_longitude=28.9784,
        transit_timezone="Europe/Istanbul",
        locale="tr",
    )
    response = transits._build_transits_engine_response(request)
    response, canonical_natal_state = transits._attach_internal_period_reasoning_state(request, response)
    event_cards = build_active_event_cards(response, max_cards=5)
    canonical_period_spine = (
        build_canonical_period_spine(
            canonical_state=canonical_natal_state,
            period_event_cards=event_cards,
        )
        if canonical_natal_state is not None
        else {}
    )
    period_core = build_period_core(
        response,
        event_cards=event_cards,
        locale="tr",
        canonical_period_spine=canonical_period_spine,
        active_life_chapter=response.get("_active_life_chapter"),
        canonical_natal_state=canonical_natal_state,
        include_adaptive_card_contexts=True,
    )
    public_payload = build_public_response(response, include_debug_artifacts=False)
    return {
        "response": response,
        "canonical_natal_state": canonical_natal_state,
        "period_core": period_core,
        "public_payload": public_payload,
    }


def _fixture_case(group: str, name: str, *, spine: dict) -> dict:
    fixture = _load_fixture(group, name)
    chapter_payload = detect_active_life_chapter(
        canonical_natal_state=fixture["canonical_natal_state"],
        transit_events=fixture["transit_events"],
    )
    active_life_chapter = dict(chapter_payload["active_life_chapter"] or {})
    assert active_life_chapter
    period_core = build_period_core(
        _fixture_report(fixture),
        event_cards=_fixture_event_cards(fixture["transit_events"]),
        locale="tr",
        canonical_period_spine=spine,
        active_life_chapter=active_life_chapter,
        canonical_natal_state=fixture["canonical_natal_state"],
        include_adaptive_card_contexts=True,
    )
    return {"period_core": period_core, "active_life_chapter": active_life_chapter}


def _signal(period_core: dict) -> dict:
    payload = dict(period_core.get("period_signal_lines_v1") or {})
    assert payload["version"] == "period_signal_lines_v1"
    return payload


def _assert_card_contract(card: dict, *, selected_meaning: str) -> None:
    assert card["id"]
    assert isinstance(card["rank"], int) and card["rank"] >= 1
    assert card["title"] and 3 <= len(card["title"].split()) <= 7
    assert card["preview"]
    assert card["body"]
    assert card["preview"] != card["body"]
    assert not card["body"].startswith(card["preview"])
    assert card["source_event_ids"] or card["evidence_refs"]
    assert card["context_used"]["semantic_focus"]["selected_meaning"] == selected_meaning
    assert card["linked_to_period_reading"] is True
    public_copy = " ".join([card["title"], card["preview"], card["body"]])
    assert not _TECH_RE.search(public_copy)
    assert not any(token in public_copy.lower() for token in _BANNED_COPY_TOKENS)
    assert "alanında" not in public_copy.lower()[:40]
    assert "teması" not in public_copy.lower()
    assert "bu tema" not in public_copy.lower()
    assert "bu dinamik" not in public_copy.lower()
    assert "bu yapı" not in public_copy.lower()
    assert "olacak" not in public_copy.lower()
    assert "kader" not in public_copy.lower()


def test_period_signal_lines_v1_real_route_saturn_return_shape() -> None:
    period_core = _route_case("2026-03-04")["period_core"]
    signal = _signal(period_core)
    cards = signal["cards"]

    assert period_core["semantic_focus"]["selected_meaning"] == "speech_authority"
    assert 3 <= len(cards) <= 6
    assert len(cards) == len({card["id"] for card in cards})
    assert any("Söz" in card["title"] for card in cards)
    for card in cards:
        _assert_card_contract(card, selected_meaning="speech_authority")
        assert card["context_used"]["period_owner"]["chapter_type"] in {"saturn_return", ""}


def test_period_signal_lines_v1_real_route_non_lifechapter_shape() -> None:
    period_core = _route_case("2026-04-22")["period_core"]
    signal = _signal(period_core)
    cards = signal["cards"]

    assert period_core["chapter_priority"]["applied"] is False
    assert 3 <= len(cards) <= 6
    assert any(any(token in card["preview"].lower() for token in ("ev", "iç", "yalnız", "kimli")) for card in cards)
    for card in cards:
        _assert_card_contract(card, selected_meaning=period_core["semantic_focus"]["selected_meaning"])


def test_period_signal_lines_v1_fixture_chapter_cases_orbit_owner() -> None:
    cancer = _fixture_case(
        "saturn_return",
        "cancer_8th_water_emotional",
        spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "promise_focus",
            "spine_lines": ["growth_integration_line"],
            "matched_event_ids": ["evt-saturn-return-cancer-8"],
            "primary_domain": "trust_transformation",
        },
    )["period_core"]
    nodal = _fixture_case(
        "nodal",
        "nn_aries_sn_libra",
        spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "direction_axis",
            "spine_lines": ["direction_line"],
            "matched_event_ids": ["evt-nodal-return-aries"],
            "primary_domain": "identity",
        },
    )["period_core"]

    cancer_cards = _signal(cancer)["cards"]
    nodal_cards = _signal(nodal)["cards"]

    assert 2 <= len(cancer_cards) <= 4
    assert any(any(token in card["preview"].lower() for token in ("paylaşı", "güven", "yakınlık")) for card in cancer_cards)
    assert 2 <= len(nodal_cards) <= 4
    assert any(any(token in card["preview"].lower() for token in ("yön", "çizgi", "uyum")) for card in nodal_cards)
    assert all("denge" not in card["body"].lower() for card in nodal_cards)


def test_period_signal_lines_v1_support_cards_rotate_by_case_context() -> None:
    route_0422 = _signal(_route_case("2026-04-22")["period_core"])["cards"]
    route_0508 = _signal(_route_case("2026-05-08")["period_core"])["cards"]
    cancer = _signal(
        _fixture_case(
            "saturn_return",
            "cancer_8th_water_emotional",
            spine={
                "source": "canonical_natal_activation_v1",
                "target_node_id": "promise_focus",
                "spine_lines": ["growth_integration_line"],
                "matched_event_ids": ["evt-saturn-return-cancer-8"],
                "primary_domain": "trust_transformation",
            },
        )["period_core"]
    )["cards"]
    nodal = _signal(
        _fixture_case(
            "nodal",
            "nn_aries_sn_libra",
            spine={
                "source": "canonical_natal_activation_v1",
                "target_node_id": "direction_axis",
                "spine_lines": ["direction_line"],
                "matched_event_ids": ["evt-nodal-return-aries"],
                "primary_domain": "identity",
            },
        )["period_core"]
    )["cards"]

    def _support_card(cards: list[dict]) -> dict:
        return next(card for card in cards if card["narrative_move"] == "support")

    support_cards = {
        "2026-04-22": _support_card(route_0422),
        "2026-05-08": _support_card(route_0508),
        "cancer_8th": _support_card(cancer),
        "nodal": _support_card(nodal),
    }

    title_to_fingerprints: dict[str, set[str]] = {}
    body_to_fingerprints: dict[str, set[str]] = {}
    for card in support_cards.values():
        title_to_fingerprints.setdefault(card["title"], set()).add(card["debug"]["fingerprint"])
        body_to_fingerprints.setdefault(card["body"], set()).add(card["debug"]["fingerprint"])

    assert all(len(fingerprints) == 1 for fingerprints in title_to_fingerprints.values())
    assert len(title_to_fingerprints) == len(support_cards)
    assert all(len(fingerprints) == 1 for fingerprints in body_to_fingerprints.values())
    assert len(body_to_fingerprints) == len(support_cards)

    cancer_joined = " ".join(
        [support_cards["cancer_8th"]["title"], support_cards["cancer_8th"]["preview"], support_cards["cancer_8th"]["body"]]
    ).lower()
    nodal_joined = " ".join(
        [support_cards["nodal"]["title"], support_cards["nodal"]["preview"], support_cards["nodal"]["body"]]
    ).lower()
    route_0422_joined = " ".join(
        [support_cards["2026-04-22"]["title"], support_cards["2026-04-22"]["preview"], support_cards["2026-04-22"]["body"]]
    ).lower()

    assert any(token in cancer_joined for token in ("güven", "paylaşılan", "mahrem", "yük", "yakınlık"))
    assert any(token in nodal_joined for token in ("onay", "yön", "kendini kısmadan", "aynı masada", "çizgi"))
    assert any(token in route_0422_joined for token in ("cümle", "netlik", "iç güvenlik", "duruş", "mesaj"))


def test_period_signal_lines_v1_no_cards_without_evidence() -> None:
    period_core = build_period_core(
        {"locale": "tr", "metrics": {"pressure_index": 0.0, "support_index": 0.0}, "natal": {}, "display": {"items": []}},
        event_cards=[],
        locale="tr",
        canonical_period_spine={},
        active_life_chapter=None,
        canonical_natal_state=None,
        include_adaptive_card_contexts=True,
    )
    signal = _signal(period_core)

    assert signal["cards"] == []


def test_period_signal_lines_v1_public_payload_additive_and_guarded() -> None:
    case = _route_case("2026-04-22")
    public_period_core = dict(case["public_payload"].get("period_core") or {})
    signal = dict(public_period_core.get("period_signal_lines_v1") or {})

    assert signal["version"] == "period_signal_lines_v1"
    assert signal["cards"]
    assert "_adaptive_cards_context" not in public_period_core
    assert public_period_core["period_reading_v1"]["full_text"] == case["period_core"]["period_reading_v1"]["full_text"]
    assert all(value is False for value in signal["debug"]["blocked_source_check"].values())
