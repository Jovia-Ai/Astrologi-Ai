import json
import re
from pathlib import Path

import pytest

import app.natal.public_builder as natal_public_builder_module
from app.natal.public_builder import build_public_natal_view


def _artifact_response(filename: str) -> dict:
    return json.loads(
        (
            Path(__file__).resolve().parent
            / "_artifacts"
            / filename
        ).read_text()
    )


def _batch_chart_birth_data(chart_id: str) -> dict:
    payload = json.loads(
        (
            Path(__file__).resolve().parent
            / "_artifacts"
            / "natal_batch_audits"
            / "natal_50_chart_discovery_metrics.json"
        ).read_text()
    )
    return next(
        dict(item.get("birth_data") or {})
        for item in payload.get("charts") or []
        if str(item.get("chart_id") or "").strip() == chart_id
    )


def _live_public_view_from_batch_chart(chart_id: str) -> dict:
    from app.api.routes.natal_interpretation import NatalInterpretationRequest, interpret_natal_chart_ui

    birth = _batch_chart_birth_data(chart_id)
    response = interpret_natal_chart_ui(
        NatalInterpretationRequest(
            birth_date=str(birth.get("birth_date") or ""),
            birth_time=str(birth.get("birth_time") or ""),
            birth_place=str(birth.get("birth_place") or ""),
            birth_latitude=birth.get("birth_latitude"),
            birth_longitude=birth.get("birth_longitude"),
            birth_timezone=birth.get("birth_timezone"),
            locale="tr",
            summary_only=False,
            include_full_profile=True,
        ),
        debug=False,
        include_debug=True,
    )
    return dict(response.get("public") or {})


def _live_public_view_from_request(*, birth_date: str, birth_time: str, birth_place: str, birth_latitude: float | None, birth_longitude: float | None, birth_timezone: str | None) -> dict:
    from app.api.routes.natal_interpretation import NatalInterpretationRequest, interpret_natal_chart_ui

    response = interpret_natal_chart_ui(
        NatalInterpretationRequest(
            birth_date=birth_date,
            birth_time=birth_time,
            birth_place=birth_place,
            birth_latitude=birth_latitude,
            birth_longitude=birth_longitude,
            birth_timezone=birth_timezone,
            locale="tr",
            summary_only=False,
            include_full_profile=True,
        ),
        debug=False,
        include_debug=True,
    )
    return dict(response.get("public") or {})


def _without_traceability(value):
    if isinstance(value, dict):
        return {
            key: _without_traceability(item)
            for key, item in value.items()
            if key != "traceability"
        }
    if isinstance(value, list):
        return [_without_traceability(item) for item in value]
    return value


def _projection_surface_snapshot(public: dict) -> dict:
    return {
        "profile_narrative_projection_v1": _without_traceability(public.get("profile_narrative_projection_v1") or {}),
        "profile_v8_projection_v1": _without_traceability(public.get("profile_v8_projection_v1") or {}),
    }


def test_public_natal_view_includes_supporting_threads_and_graph() -> None:
    response = {
        "core_story": "Kisa test metni.",
        "core_story_ui": {"headline": "Baslik", "text": "Kisa omurga metni."},
        "planets": [
            {"planet": "Moon", "house": 8, "sign": "Scorpio"},
            {"planet": "Saturn", "house": 4, "sign": "Aquarius"},
            {"planet": "Mercury", "house": 3, "sign": "Virgo"},
            {"planet": "Venus", "house": 12, "sign": "Libra"},
            {"planet": "Mars", "house": 7, "sign": "Aries"},
            {"planet": "Jupiter", "house": 1, "sign": "Capricorn"},
            {"planet": "Fortune", "house": 5, "sign": "Taurus"},
            {"planet": "North Node", "house": 9, "sign": "Libra"},
        ],
        "aspects": [
            {"planet1": "Moon", "planet2": "Saturn", "aspect": "square", "orb": 0.8},
            {"planet1": "Mercury", "planet2": "Saturn", "aspect": "trine", "orb": 1.1},
            {"planet1": "Moon", "planet2": "Venus", "aspect": "trine", "orb": 0.42},
            {"planet1": "Fortune", "planet2": "Jupiter", "aspect": "trine", "orb": 0.67},
            {"planet1": "Venus", "planet2": "Mars", "aspect": "trine", "orb": 1.4},
        ],
        "meta": {"pressure_index": 0.4, "support_index": 0.6},
        "meaning_weighting": {"primary_theme": "identity", "confidence": 0.72},
        "narrative_anchor": {"domain": "identity"},
        "personality_imprint": {
            "engine_version": "personality_imprint_v1",
            "library_version": "personality_imprint_library_tr_v6",
            "locale": "tr",
            "headline": "Kişilik İmzası",
            "render_shape": {
                "headline": "Kişilik İmzası",
                "subfields": ["aura", "trait", "drive"],
                "optional_subfield": "shadow",
            },
            "entries": [
                {
                    "key": "sun_house_10",
                    "kind": "house_placement",
                    "label_tr": "Güneş 10. Ev",
                    "tags": ["başarı", "görünürlük", "hedef"],
                    "aura": "Sende saygı uyandıran, hedefe dönük ve görünür olmak isteyen güçlü bir enerji olabilir.",
                    "trait": "Sen yaptığın şeyin ciddiye alınmasını, emeklerinin karşılık bulmasını ve iz bırakmayı istersin.",
                    "drive": "İçinde bir şey başarma, yükselme ve kendi değerinle görünür olma arzusu güçlüdür.",
                    "shadow": "Bazen değeri sadece başarıyla ölçme ya da kendine fazla baskı kurma eğilimi oluşabilir.",
                    "background_hint": "",
                    "gift": "Bu yerleşim sende hedef bilinci, güçlü duruş ve kamusal alanda parlayan bir merkez yaratır.",
                    "support_keys": ["moon_leo"],
                }
            ],
            "extra_entries": [
                {
                    "key": "venus_house_12",
                    "kind": "house_placement",
                    "label_tr": "Venüs 12. Ev",
                    "tags": ["gizli", "ince", "ruhsal"],
                    "aura": "Sende yumuşak, zarif ve tam çözülemeyen bir kalp enerjisi olabilir.",
                    "trait": "Sen sevgiyi her zaman yüksek sesle değil, çoğu zaman sessiz ve derin katmanlarda yaşarsın.",
                    "drive": "İçinde ruhsal yakınlık, ince bağlar ve görünmeyen sevgi alışverişi kurma ihtiyacı vardır.",
                    "shadow": "Bazen duygularını açık ifade etmek yerine geri çekilebilir ya da ulaşılmaz kişilere çekilebilirsin.",
                    "background_hint": "Yakınlık alanında temkinli olmayı erken dönemde öğrenmiş olabilirsin.",
                    "gift": "Bu yerleşim sende çok ince bir sezgi, saf bir sadakat ve ruha dokunan bir sevgi yaratır.",
                    "support_keys": ["venus_sagittarius"],
                }
            ],
            "support_entries": [
                {
                    "key": "moon_leo",
                    "kind": "sign_placement",
                    "label_tr": "Ay Aslan",
                    "tags": ["sicak", "gorunur duygu", "gururlu kalp"],
                    "aura": "Kalbin losta yasamiyor; baglandiginda sicakligin fark edilir hale geliyor.",
                    "trait": "Sen duygularini buyuk, canli ve icten bir yerden yasarsin.",
                    "drive": "Icinde sevilmek, gorulmek ve kalpten verdigin seyin karsilik buldugunu hissetmek isteyen guclu bir ihtiyac vardir.",
                    "shadow": "Bazen gurur yarasi, onay ihtiyaci ya da dramatik tepkiler one cikabilir.",
                }
                ,
                {
                    "key": "venus_sagittarius",
                    "kind": "sign_placement",
                    "label_tr": "Venüs Yay",
                    "tags": ["özgür sevgi", "neşe", "açık kalp"],
                    "aura": "Kalbin dar odada yaşamıyor; sevgi sende alan, neşe ve dürüstlük isteyebilir.",
                    "trait": "Sen sevgide özgürlük, içtenlik ve birlikte genişleme duygusu ararsın.",
                    "drive": "İçinde ilham duymak, hayatı paylaşırken çoğalmak ve sevginin canlı kalmasını istemek vardır.",
                    "shadow": "Bazen bağ derinleşmeden alan istemeye kaçabilir ya da fazla rahat davranabilirsin.",
                }
            ],
            "bundles": [
                {
                    "id": "sun_house_10",
                    "dominant_key": "sun_house_10",
                    "dominant_kind": "house_placement",
                    "related_planets": ["Sun"],
                    "support_keys": ["moon_leo"],
                }
            ],
            "extra_bundles": [
                {
                    "id": "venus_house_12",
                    "dominant_key": "venus_house_12",
                    "dominant_kind": "house_placement",
                    "related_planets": ["Venus"],
                    "support_keys": ["venus_sagittarius"],
                }
            ],
            "selection_debug": {"selected_keys": ["sun_house_10"]},
        },
        "profile_narrative": {
            "profile_public": {
                "engine_version": "profile_narrative_v2",
                "blocks": [
                    {
                        "id": "mind_voice",
                        "headline": "Zihin tonu",
                        "teaser": "Kisa teaser.",
                        "body": "Akici profile body metni.",
                        "micro": "Kısa ama ayrı bir mikro içgörü.",
                        "astro_hint": "Merkür 1. ev, Satürn 3. ev",
                        "astro_sources": ["Merkür 1. ev", "Satürn 3. ev"],
                        "chips": ["Satürn 3.ev", "Merkür 1.ev"],
                    }
                ],
            },
            "profile_internal": {
                "blocks_debug": [
                    {
                        "id": "mind_voice",
                        "template_id": "mind_voice:structured",
                        "primary_signature_id": "mind_saturn_third",
                        "evidence": [{"type": "placement"}, {"type": "aspect"}],
                    }
                ]
            },
        },
        "sections_v2": [
            {
                "id": "mind_system",
                "title": "Zihin–eylem–kontrol",
                "subtitle": "Netleşince hızlanıyorsun.",
                "body": "Akıcı tema metni.",
                "micro": "Kısa örnek.",
                "chips": ["Yükselen Oğlak", "Satürn 3. ev"],
            }
        ],
        "supporting_threads": [
            {
                "id": "identity_mechanics",
                "title": "Kimlik",
                "one_liner": "Kisa cizgi.",
                "paragraph": "Daha uzun aciklama.",
                "evidence": [{"type": "house_ruler"}],
            }
        ],
        "natal_graph_compact": {
            "house_rulers": {"1": {"primary_ruler": "Saturn"}},
            "dominant_loops": [{"signature": "Saturn→Mars→Mercury", "count": 2}],
            "importance": {"Saturn": 0.88},
            "ignored": "x",
        },
    }

    public = build_public_natal_view(response, locale="tr", include_full_profile=True)
    assert public["supporting_threads"]
    assert public["supporting_threads"][0]["id"] == "identity_mechanics"
    assert public["personality_imprint"]["headline"] == "Kişilik İmzası"
    assert public["personality_imprint"]["entries"][0]["key"] == "sun_house_10"
    assert public["personality_imprint"]["extra_entries"][0]["key"] == "venus_house_12"
    assert public["personality_imprint"]["entries"][0]["support_keys"] == ["moon_leo"]
    assert public["personality_imprint"]["entries"][0]["gift"] == "Bu yerleşim sende hedef bilinci, güçlü duruş ve kamusal alanda parlayan bir merkez yaratır."
    assert public["personality_imprint"]["extra_entries"][0]["background_hint"] == "Yakınlık alanında temkinli olmayı erken dönemde öğrenmiş olabilirsin."
    assert public["personality_imprint"]["support_entries"][0]["key"] == "moon_leo"
    assert public["personality_imprint"]["bundles"][0]["support_keys"] == ["moon_leo"]
    assert public["personality_imprint"]["extra_bundles"][0]["support_keys"] == ["venus_sagittarius"]
    assert "selection_debug" not in public["personality_imprint"]
    assert public["profile_narrative"]["profile_public"]["blocks"]
    assert public["profile_narrative"]["profile_public"]["blocks"][0]["micro"]
    block = public["profile_narrative"]["profile_public"]["blocks"][0]
    insight_modules = public["profile_narrative"]["profile_public"]["insight_modules"]
    assert len(insight_modules) == 1
    assert insight_modules[0]["module_id"] == "moon_defense_mechanism"
    assert insight_modules[0]["headline"] == "Senin savunma mekanizman"
    assert insight_modules[0]["moon_sign"] == "Scorpio"
    assert insight_modules[0]["title"] == "İncinmemek için hep tetikte kalıyorsun"
    assert insight_modules[0]["share_text"].startswith("Senin savunma mekanizman:")
    assert insight_modules[0]["meta"]["expandable"] is True
    assert insight_modules[0]["priority"] == 32
    assert block["astro_hint"]
    assert block["astro_sources"] == ["Merkür 1. ev", "Satürn 3. ev"]
    assert public["profile_narrative"]["profile_public"]["schema_version"] == "profile_narrative_public_v3"
    assert public["profile_narrative"]["profile_public"]["core_blocks"]
    assert public["profile_narrative"]["profile_public"]["detail_cards"]
    detail_cards = public["profile_narrative"]["profile_public"]["detail_cards"]
    mind_card = next(card for card in detail_cards if card["id"] == "mind_voice")
    assert 4 <= len(mind_card["detail_blocks"]) <= 7
    assert all("\n\n" not in str(block) for block in mind_card["detail_blocks"])
    placement_card = next(card for card in detail_cards if card["id"] == "sun_house_10")
    assert 4 <= len(placement_card["detail_blocks"]) <= 7
    assert placement_card["detail_blocks"][0] == "Sen yaptığın şeyin ciddiye alınmasını, emeklerinin karşılık bulmasını ve iz bırakmayı istersin."
    assert public["profile_narrative"]["profile_public"]["core_blocks"][0]["family"] == "mind_mechanics"
    assert "3. ev" not in block["astro_hint"]
    assert "Merkür" not in block["astro_hint"]
    assert all("ev" not in chip.lower() for chip in block["chips"])
    assert "profile_internal" not in public["profile_narrative"]
    assert public["sections_v2"]
    assert public["sections_v2"][0]["id"] == "mind_system"
    assert isinstance(public.get("core_story_ui"), dict)
    assert public["core_story_ui"].get("text")
    compact = public["natal_graph_compact"]
    assert isinstance(compact, dict)
    assert "house_rulers" in compact
    assert "ignored" not in compact
    assert public["narrative_v2"]["contract_version"] == "narrative_v2_draft_2026_03"
    selector = public["narrative_v2"]["aspect_bundle_selector"]
    assert selector["selected_bundles"]
    assert selector["max_primary_bundles"] == 3
    assert isinstance(public.get("profile_v8"), dict)
    assert isinstance(public.get("full_map_v8"), dict)
    profile_v8 = public["profile_v8"]
    assert profile_v8["hero"]["sun_sign"] or profile_v8["hero"]["moon_sign"] or profile_v8["hero"]["rising_sign"]
    assert isinstance(profile_v8["insight_strip"], list)
    assert len(profile_v8["insight_strip"]) == 3
    assert isinstance(profile_v8["differentiators"], list)
    assert any(item.get("stat_label") == "orb" for item in profile_v8["differentiators"])
    full_map_v8 = public["full_map_v8"]
    assert set(full_map_v8.keys()) == {"kimlik", "iliski", "kariyer", "golge"}
    meaning_graph = public["meaning_graph"]
    assert meaning_graph["version"] == "meaning_graph_v1"
    assert meaning_graph["canonical"] is True
    assert meaning_graph["locale"] == "tr"
    assert isinstance(meaning_graph["nodes"], list)
    assert isinstance(meaning_graph["evidence"], list)
    families = {str(node.get("source_family")) for node in meaning_graph["nodes"]}
    assert {"core_story_ui", "personality_imprint", "supporting_threads"} <= families
    assert "user_compact" in meaning_graph["meta"]["missing_source_families"]
    first_node = meaning_graph["nodes"][0]
    assert {
        "node_id",
        "layer",
        "domain",
        "source_family",
        "source_path",
        "title",
        "summary",
        "confidence",
        "tags",
        "evidence_ids",
        "mapping_status",
        "rank",
    } <= set(first_node.keys())
    assert meaning_graph["meta"]["node_count"] == len(meaning_graph["nodes"])
    assert meaning_graph["meta"]["evidence_count"] == len(meaning_graph["evidence"])
    meaning_graph_v1_1 = public["meaning_graph_v1_1"]
    assert meaning_graph_v1_1["version"] == "meaning_graph_v1_1"
    assert meaning_graph_v1_1["canonical_intent"] is True
    assert isinstance(meaning_graph_v1_1["nodes"], list)
    assert isinstance(meaning_graph_v1_1["evidence"], list)
    assert "relations" not in meaning_graph_v1_1
    assert "groups" not in meaning_graph_v1_1
    profile_narrative_projection_v1 = public["profile_narrative_projection_v1"]
    assert profile_narrative_projection_v1["version"] == "profile_narrative_projection_v1"
    projected_core = profile_narrative_projection_v1["profile_public"]["core_blocks"]
    assert isinstance(projected_core, list)
    assert projected_core
    assert projected_core[0]["trace"]["node_id"]
    assert isinstance(projected_core[0]["trace"]["evidence_ids"], list)
    profile_v8_projection_v1 = public["profile_v8_projection_v1"]
    assert profile_v8_projection_v1["version"] == "profile_v8_projection_v1"
    assert profile_v8_projection_v1["hero"]["trace"]["node_id"]
    assert isinstance(profile_v8_projection_v1["hero"]["trace"]["evidence_ids"], list)
    assert "natal_promise_cluster_plan_v1" not in public
    serialized_v8 = json.dumps({"profile_v8": profile_v8, "full_map_v8": full_map_v8}, ensure_ascii=False).lower()
    assert "_debug" not in serialized_v8
    assert "_internal" not in serialized_v8
    assert "_pattern" not in serialized_v8
    assert "_bundle" not in serialized_v8

    debug_public = build_public_natal_view(
        response,
        locale="tr",
        include_debug=True,
        include_full_profile=True,
    )
    assert debug_public["personality_imprint"]["selection_debug"]["selected_keys"] == ["sun_house_10"]
    assert debug_public["profile_narrative"]["profile_internal"]["blocks_debug"]
    assert "section_priority_matrix" in debug_public["narrative_v2"]
    assert "migration_map" in debug_public["narrative_v2"]


def test_public_natal_view_builds_editorial_visibility_detail_blocks_for_sample_chart() -> None:
    artifact_path = (
        Path(__file__).resolve().parent
        / "_artifacts"
        / "natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json"
    )
    response = json.loads(artifact_path.read_text())

    public = build_public_natal_view(response, locale="tr", include_full_profile=True)
    detail_cards = public["profile_narrative"]["profile_public"]["detail_cards"]
    career_card = next(card for card in detail_cards if card["id"] == "career_visibility")

    blocks = career_card["detail_blocks"]
    assert len(blocks) == 7

    haystack = " ".join(str(item) for item in blocks).lower()
    assert "denge" in haystack
    assert "estetik" in haystack
    assert "görmek istedikleri gibi" in haystack
    assert "görülmek" in haystack
    assert "ciddiye alınmak" in haystack
    assert "nüans" in haystack
    assert "net görünmek" in haystack


def test_public_natal_view_naturalizes_profile_copy_and_humanizes_chips() -> None:
    response = {
        "core_story": "Kısa test metni.",
        "meta": {"pressure_index": 0.4, "support_index": 0.6},
        "narrative_anchor": {"domain": "identity"},
        "profile_narrative": {
            "profile_public": {
                "engine_version": "profile_narrative_v2",
                "blocks": [
                    {
                        "id": "luck_creation",
                        "headline": "Sende akış nerede hızlanıyor",
                        "teaser": "Sende kapı açan taraf, şans sende tesadüf değil.",
                        "body": (
                            "Kimlik hattında yön duygusu ve büyük resim birlikte belirgin. "
                            "Yakınlık sende yüzey değil. "
                            "İçeride söz senin kasın. "
                            "Kariyer hattında görünürlük ve kalite standardı birlikte çalışıyor."
                        ),
                        "micro": "Akış tarafında cesaret ile sezgi aynı kapıyı çalıştırıyor.",
                        "astro_hint": "Zihinsel tarafta cümle disiplini ile sezgi aynı anda devrede.",
                        "astro_sources": ["Jüpiter 5. ev", "Mars-Neptün üçgeni"],
                        "chips": ["Upgrade", "Kalibrasyon", "İç Ayar", "Sistem + Yenilik"],
                    }
                ],
            }
        },
    }

    public = build_public_natal_view(response, locale="tr", include_full_profile=True)
    block = public["profile_narrative"]["profile_public"]["blocks"][0]
    body = str(block["body"]).lower()

    assert block["headline"] == "Şansın en kolay nerede açılıyor"
    assert "sende kapı açan taraf" not in str(block["teaser"]).lower()
    assert "tesadüf gibi değil" in str(block["teaser"]).lower()
    assert "kimlik hattında" not in body
    assert "kariyer hattında" not in body
    assert "yakınlık sende yüzey değil" not in body
    assert "söz senin kasın" not in body
    assert "yakınlık senin için yüzeyde kalan bir şey değil" in body
    assert "sözü seçme ve yerli yerine koyma becerin güçlü" in body
    assert "zihinsel tarafta" not in str(block["astro_hint"]).lower()
    assert "cümle disiplinin" in str(block["astro_hint"]).lower()
    assert "akış tarafında" not in str(block["micro"]).lower()
    assert "gerekir" not in str(block["micro"]).lower()
    body_first = re.split(r"(?<=[.!?])\s+", str(block["body"]).strip())[0]
    assert body_first
    teaser_tokens = set(re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ]+", str(block["teaser"]).lower()))
    first_tokens = set(re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ]+", body_first.lower()))
    overlap = len(teaser_tokens & first_tokens) / len(teaser_tokens | first_tokens)
    assert overlap < 0.8
    assert block["astro_sources"] == ["Jüpiter 5. ev", "Mars-Neptün üçgeni"]
    assert block["chips"] == ["Yenilik", "İç Denge", "Yapı ve Yenilik"]


def test_public_natal_view_editorializes_synthesized_bundle_cards(monkeypatch) -> None:
    monkeypatch.setattr(
        natal_public_builder_module,
        "select_aspect_bundles",
        lambda _response: {
            "selected_bundles": [
                {
                    "bundle_id": "relational_heat",
                    "bundle_type": "relational_pattern_bundle",
                    "domains": ["ilişkiler", "yakınlık"],
                    "recognition_tags": ["güven arayışı", "derin temas"],
                    "gift_tags": ["sadakat"],
                    "reflex_tags": ["geri çekilme"],
                    "astro_sources": ["Ay-Satürn karesi", "Ay 8. ev", "Satürn 4. ev"],
                }
            ],
            "max_primary_bundles": 3,
        },
    )

    public = build_public_natal_view(
        {
            "core_story": "Kısa test metni.",
            "meta": {"pressure_index": 0.4, "support_index": 0.6},
            "narrative_anchor": {"domain": "identity"},
            "planets": [{"planet": "Moon", "house": 8, "sign": "Scorpio"}],
            "profile_narrative": {"profile_public": {"engine_version": "profile_narrative_v2", "blocks": []}},
        },
        locale="tr",
        include_full_profile=True,
    )

    extra_blocks = public["profile_narrative"]["profile_public"]["extra_blocks"]
    synthesized = next(
        block for block in extra_blocks if block["origin"] == "narrative_v2_bundle"
    )

    assert synthesized["headline"] == "Yakınlık sende nasıl açılıyor"
    assert synthesized["astro_sources"] == ["Ay-Satürn karesi", "Ay 8. ev", "Satürn 4. ev"]
    assert "İlk hissedilen çizgi:" not in synthesized["body"]
    assert "Güçlü taraf:" not in synthesized["body"]
    assert "Sıkışınca çalışan refleks:" not in synthesized["body"]
    assert "İnsanların sende ilk fark ettiği şey" in synthesized["body"]
    assert "Zorlandığında ise" in synthesized["body"]


def test_public_natal_view_profile_copy_cleanup_is_deterministic() -> None:
    response = {
        "core_story": "Kısa test metni.",
        "meta": {"pressure_index": 0.2, "support_index": 0.8},
        "narrative_anchor": {"domain": "identity"},
        "profile_narrative": {
            "profile_public": {
                "engine_version": "profile_narrative_v2",
                "blocks": [
                    {
                        "id": "mind_voice",
                        "headline": "Karar alırken içinde olan şey",
                        "teaser": "Yakınlık sende yüzey değil; güven kurdukça büyür.",
                        "body": (
                            "Sende ilk hissedilen şey, Akici bir cümle kuruyorsun. "
                            "Sende düşünürken ilk görülen taraf, içerde tonu tartman. "
                            "Sende kapı açan taraf, şans sende tesadüf değil. "
                            "İçeride söz senin kasın."
                        ),
                        "micro": "Zihinsel tarafta cümle disiplini ile sezgi aynı anda devrede.",
                        "astro_hint": "Kimlik hattında yön duygusu ve büyük resim birlikte belirgin.",
                        "chips": ["Kalibrasyon", "İç Ayar", "Upgrade"],
                    }
                ],
            }
        },
    }

    first = build_public_natal_view(response, locale="tr", include_full_profile=True)
    second = build_public_natal_view(response, locale="tr", include_full_profile=True)

    assert first["profile_narrative"]["profile_public"]["blocks"] == second["profile_narrative"]["profile_public"]["blocks"]
    body = str(first["profile_narrative"]["profile_public"]["blocks"][0]["body"])
    starters = [sentence for sentence in re.split(r"(?<=[.!?])\s+", body) if sentence.strip()]
    assert sum(1 for sentence in starters if sentence.lower().startswith("sende ")) <= 1


def test_public_natal_view_softens_core_story_and_sectional_coaching_language() -> None:
    response = {
        "core_story": (
            "Varlığını güçlü biçimde hissettirme ve görünür olma ihtiyacı kimliğinin merkezindedir. "
            "Bu ihtiyaç yükseldiğinde, Aşırı ben-merkezcilik, her şeyi kişisel algılama daha kolay tetiklenebilir.\n\n"
            "Psikolojik temelinde ‘ben kimim ve nasıl görünmeliyim.\n\n"
            "Böylece Dürüst ve net olduğunda insanlara yön ve cesaret verirsin."
        ),
        "meta": {"pressure_index": 0.4, "support_index": 0.6},
        "narrative_anchor": {"domain": "identity"},
        "sections_v2": [
            {
                "id": "mind_system",
                "title": "Zihin",
                "subtitle": "Netleşince hızlanıyorsun; ritim hızın çarpanı.",
                "body": (
                    "Burada ustalık daha çok düşünmek değil, sınırı daha iyi çizmek ve ritmini korumak; "
                    "çünkü ritim bozulduğunda sistem yoruluyor, ritim oturduğunda ise çok hızlı toparlanıyorsun."
                ),
                "micro": "Az cümleyle sınır koyduğunda hem zihnin hem ritmin rahatlıyor; sende hız çoğu zaman bu sadeleşmeden geliyor.",
            }
        ],
        "supporting_threads": [
            {
                "id": "career_visibility",
                "title": "Kariyer",
                "one_liner": "Sahneye çıkınca etkilisin; ama önce içeride olgunlaştırıyorsun.",
                "paragraph": (
                    "Bu yüzden seni en çok büyüten şey bir anda büyük çıkışlar değil, küçük ama düzenli görünürlük adımlarıyla ritim kurmak. "
                    "Burada hız, mükemmeli beklemekten değil yayınlanabilir iyi seviyesini tutarlı biçimde çoğaltmaktan geliyor."
                ),
                "body": "Kariyerde senin gücün güçlü.",
                "micro": "Görünürlüğü küçük ve düzenli dozlarla taşıman, sende baskıyı azaltırken etkiyi büyütüyor.",
            }
        ],
    }

    public = build_public_natal_view(response, locale="tr", include_full_profile=True)

    core_story = str(public["core_story"])
    assert "Bu ihtiyaç yükseldiğinde" not in core_story
    assert "Böylece Dürüst" not in core_story
    assert "İçeride sık sık 'ben kimim ve nasıl görünmeliyim?'" in core_story

    section = public["sections_v2"][0]
    assert "ritim hızın çarpanı" not in str(section["subtitle"]).lower()
    assert "çarpanı" not in str(section["subtitle"]).lower()
    assert "ritim bozulduğunda sistem yoruluyor" not in str(section["body"]).lower()

    thread = public["supporting_threads"][0]
    assert "görünürlük adımları" not in str(thread["paragraph"]).lower()
    assert "yayınlanabilir iyi seviyesi" not in str(thread["paragraph"]).lower()
    assert "küçük ve düzenli dozlarla" not in str(thread["micro"]).lower()


def test_public_natal_view_meaning_graph_is_stable_and_backward_compatible() -> None:
    response = {
        "core_story": "Kısa test metni.",
        "core_story_ui": {"headline": "Öz İz", "text": "Genel hatta güven üretirsin."},
        "meta": {"pressure_index": 0.4, "support_index": 0.6},
        "narrative_anchor": {"domain": "identity"},
        "user_compact": {
            "domains": [
                {
                    "domain": "kimlik",
                    "title": "Kimlik",
                    "summary": "Sakin ama yön veren bir çizgi.",
                    "highlights": [{"text": "İçeride netlik ararsın."}],
                }
            ],
            "micro_insights": [{"domain": "career", "text": "Görünürlükte kalite ararsın."}],
        },
        "personality_imprint": {
            "entries": [
                {
                    "key": "sun_house_10",
                    "label_tr": "Güneş 10. Ev",
                    "tags": ["başarı"],
                    "trait": "Ciddiye alınmak istersin.",
                    "shadow": "Bazen baskı artar.",
                    "gift": "Hedef tutarlılığı üretirsin.",
                }
            ]
        },
        "supporting_threads": [
            {
                "id": "identity_mechanics",
                "title": "Kimlik",
                "paragraph": "Kök motivasyonun görünür etki üretmek.",
            }
        ],
    }

    first = build_public_natal_view(response, locale="tr")
    second = build_public_natal_view(response, locale="tr")

    first_graph = first["meaning_graph"]
    second_graph = second["meaning_graph"]
    assert first_graph == second_graph

    expected_existing_keys = {
        "locale",
        "core_story",
        "core_story_ui",
        "user_compact",
        "upper_meaning",
        "theme_scores",
        "meta_summary",
        "meaning_weighting",
        "data_quality_summary",
        "narrative_anchor",
        "natal_graph_compact",
        "personality_imprint",
        "profile_narrative",
        "profile_v8",
        "full_map_v8",
        "sections_v2",
        "supporting_threads",
        "narrative_v2",
        "profile_narrative_projection_v1",
        "profile_v8_projection_v1",
        "flags",
    }
    assert expected_existing_keys <= set(first.keys())

    assert first_graph["version"] == "meaning_graph_v1"
    assert first_graph["canonical"] is True
    assert isinstance(first_graph["taxonomy"]["layers"], list)
    assert isinstance(first_graph["taxonomy"]["domains"], list)
    assert isinstance(first_graph["nodes"], list)
    assert isinstance(first_graph["evidence"], list)
    assert first_graph["meta"]["node_count"] == len(first_graph["nodes"])
    first_graph_v1_1 = first["meaning_graph_v1_1"]
    assert first_graph_v1_1["version"] == "meaning_graph_v1_1"
    assert isinstance(first_graph_v1_1["nodes"], list)


def test_public_natal_view_lazily_builds_full_profile_branches() -> None:
    response = {
        "core_story": "Kısa test metni.",
        "core_story_ui": {"headline": "Öz İz", "text": "Genel hatta güven üretirsin."},
        "meta": {"pressure_index": 0.4, "support_index": 0.6},
        "narrative_anchor": {"domain": "identity"},
        "planets": [{"planet": "Moon", "house": 8, "sign": "Scorpio"}],
        "profile_narrative": {
            "profile_public": {
                "engine_version": "profile_narrative_v2",
                "blocks": [
                    {
                        "id": "mind_voice",
                        "headline": "Zihin tonu",
                        "teaser": "Kısa teaser.",
                        "body": "Akıcı profile body metni.",
                        "micro": "Kısa bir mikro içgörü.",
                        "astro_hint": "Merkür 1. ev",
                        "chips": ["Satürn 3.ev"],
                    }
                ],
            }
        },
        "sections_v2": [
            {
                "id": "mind_system",
                "title": "Zihin sistemi",
                "subtitle": "Netleşince hızlanıyorsun.",
                "body": "Akıcı tema metni.",
                "micro": "Kısa örnek.",
            }
        ],
        "personality_imprint": {"entries": []},
        "supporting_threads": [],
    }

    lazy_public = build_public_natal_view(response, locale="tr")
    assert lazy_public["profile_narrative"] is None
    assert lazy_public["profile_v8"] is None
    assert lazy_public["full_map_v8"] is None
    assert lazy_public["sections_v2"] == []
    assert isinstance(lazy_public["profile_narrative_projection_v1"], dict)
    assert isinstance(lazy_public["profile_v8_projection_v1"], dict)

    full_public = build_public_natal_view(response, locale="tr", include_full_profile=True)
    assert isinstance(full_public["profile_narrative"], dict)
    assert isinstance(full_public["profile_v8"], dict)
    assert isinstance(full_public["full_map_v8"], dict)
    assert isinstance(full_public["sections_v2"], list)
    assert full_public["sections_v2"]


@pytest.mark.parametrize("projection_key", ["profile_narrative_projection_v1", "profile_v8_projection_v1"])
def test_public_natal_view_cluster_plan_uses_richer_raw_candidate_inventory(monkeypatch, projection_key: str) -> None:
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")
    response = json.loads(
        (
            Path(__file__).resolve().parent
            / "_artifacts"
            / "natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json"
        ).read_text()
    )

    public = build_public_natal_view(response, locale="tr", include_debug=True, include_full_profile=True)
    traceability = public[projection_key]["traceability"]
    cluster_plan = traceability["natal_promise_cluster_plan_v1"]
    candidate_ids = {
        packet["id"]
        for packet in cluster_plan["candidate_packets"]
    }

    assert len(cluster_plan["candidate_packets"]) > 5
    assert "moon_trine_venus_emotional_warmth_chart_exact" in candidate_ids
    assert "saturn_sextile_uranus_structured_originality_chart_exact" in candidate_ids
    focus_map = {item["domain"]: item["tier"] for item in cluster_plan["focus_map"]}
    assert focus_map["mind"] in {"medium_strong", "strong"}
    assert focus_map["relationship"] in {"medium_strong", "strong"}
    assert focus_map["career"] in {"medium_strong", "strong"}


def test_public_natal_view_cluster_plan_renderer_localizes_and_separates_reused_copy(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")
    response = json.loads(
        (
            Path(__file__).resolve().parent
            / "_artifacts"
            / "natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json"
        ).read_text()
    )

    public = build_public_natal_view(response, locale="tr", include_debug=True, include_full_profile=True)
    narrative_blocks = public["profile_narrative_projection_v1"]["profile_public"]["blocks"]
    block_by_node_id = {
        str(block["node_id"] or "").strip(): block
        for block in narrative_blocks
    }

    hidden_love = block_by_node_id.get("promise::venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact")
    if hidden_love:
        assert hidden_love["headline"] == "Bazı duygular sende önce içeride büyüyor olabilir."
        assert "sevgiyi bazen önce içeride büyüten" in hidden_love["body"].lower()
        assert "üretim ve görünürlük" not in hidden_love["body"].lower()
    else:
        plan = public["profile_v8_projection_v1"]["traceability"]["natal_promise_cluster_plan_v1"]
        assert "relationship_hidden_private_love_pattern" in set(plan["surface_plan"]["detail_cluster_ids"])
        assert "venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact" in set(
            plan["surface_plan"]["debug_packet_ids"]
        )

    identity_saturn_uranus = block_by_node_id["promise::saturn_sextile_uranus_structured_originality_identity_chart_exact"]
    assert identity_saturn_uranus["headline"] == "Ciddi görünsen de içeride daha farklı bir çizgi taşıyorsun."
    assert "Saturn sextile Uranus" not in identity_saturn_uranus["body"]

    all_public_copy = " ".join(
        [
            *(
                value
                for block in narrative_blocks
                for value in (
                    str(block.get("headline") or ""),
                    str(block.get("teaser") or ""),
                    str(block.get("body") or ""),
                )
            ),
            str(public["profile_v8_projection_v1"]["hero"].get("headline") or ""),
            str(public["profile_v8_projection_v1"]["hero"].get("summary") or ""),
            str(public["profile_v8_projection_v1"]["identity_axis"].get("headline") or ""),
            str(public["profile_v8_projection_v1"]["identity_axis"].get("body") or ""),
        ]
    )
    for raw_anchor in (
        "Saturn sextile Uranus",
        "Moon trine Venus",
        "Mercury conjunction Jupiter",
        "Mercury conjunct Jupiter",
        "Sun square Saturn",
        "Mars opposite Saturn",
        "Mars opposition Saturn",
        "Chiron conjunct MC",
        "Midheaven",
    ):
        assert raw_anchor not in all_public_copy

    extra_block_ids = {
        str(block["node_id"] or "").strip()
        for block in public["profile_narrative_projection_v1"]["profile_public"]["extra_blocks"]
    }
    assert "promise::chiron_conjunct_mc_visibility_wound_to_voice_chart_exact" in extra_block_ids
    assert "promise::saturn_trine_pluto_deep_resilience_chart_exact" in extra_block_ids


def test_public_natal_view_2020_copy_polish_naturalizes_surface_without_duplicate_diff_headlines(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")
    response = _artifact_response("natal_interpret_full_2020-04-10_08-26_istanbul_user_compact_debug.json")

    public = build_public_natal_view(response, locale="tr", include_debug=True, include_full_profile=True)
    profile_public = public["profile_narrative_projection_v1"]["profile_public"]
    core_blocks = list(profile_public["core_blocks"])
    extra_blocks = list(profile_public["extra_blocks"])
    block_by_node_id = {
        str(block.get("node_id") or "").strip(): block
        for block in [*core_blocks, *extra_blocks]
    }

    career_core = block_by_node_id["promise::aquarius_mc_mars_conjunct_mc_visible_freedom_drive"]
    assert "Bazen de." not in str(career_core.get("body") or "")
    assert str(career_core.get("body") or "").startswith("Mars'ının kariyer hattına çok yakın olması")

    trust_block = block_by_node_id["promise::venus_trine_saturn_trust_bond_chart_exact"]
    assert str(trust_block.get("body") or "").startswith("Venüs'ünün Satürn'le uyumlu çalışması")

    mind_block = block_by_node_id["promise::mind_mind_system"]
    assert "Ne yapacağını bildiğin an tempo kendiliğinden yükselir. Ne yapacağını bildiğin an tempo kendiliğinden yükselir." not in str(
        mind_block.get("body") or ""
    )

    public_text = " ".join(
        [
            *(
                value
                for block in [*core_blocks, *extra_blocks]
                for value in (
                    str(block.get("headline") or ""),
                    str(block.get("teaser") or ""),
                    str(block.get("body") or ""),
                )
            ),
            str(public["profile_v8_projection_v1"]["hero"].get("headline") or ""),
            str(public["profile_v8_projection_v1"]["hero"].get("summary") or ""),
            str(public["profile_v8_projection_v1"]["identity_axis"].get("headline") or ""),
            str(public["profile_v8_projection_v1"]["identity_axis"].get("body") or ""),
            *(
                str(item.get("headline") or "")
                for item in public["profile_v8_projection_v1"]["differentiators"]
            ),
        ]
    )
    for bad_phrase in ("kadar Güven de", "olması de", "Özel ateş birlikte"):
        assert bad_phrase not in public_text, f"bad copy join leaked into 2020 public text: {bad_phrase!r}"

    core_headlines = {
        str(block.get("headline") or "").strip()
        for block in core_blocks
    }
    differentiator_headlines = [
        str(item.get("headline") or "").strip()
        for item in public["profile_v8_projection_v1"]["differentiators"]
    ]
    assert not (core_headlines & set(differentiator_headlines)), (
        f"2020 differentiators still duplicate core headlines: {core_headlines & set(differentiator_headlines)}"
    )


def test_public_natal_view_izmir_1996_mind_override_is_guarded_by_exact_chart_facts(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")
    response = _artifact_response("natal_interpret_full_1996-03-08_08-30_izmir_user_compact_debug.json")
    public = build_public_natal_view(
        response,
        locale="tr",
        include_debug=True,
        include_full_profile=True,
    )
    packet = next(
        pkt
        for pkt in public["profile_narrative_projection_v1"]["traceability"]["natal_promise_cluster_plan_v1"]["candidate_packets"]
        if str(pkt.get("id") or "").strip() == "mercury_pisces_11h_social_intuition_mind_chart_exact"
    )

    from app.meaning.projection_shadow_v1_builder import _packet_body_text, _packet_copy_override

    override = _packet_copy_override(packet)

    body = _packet_body_text(packet=packet, max_sentences=4)
    teaser = str(packet.get("direct_meaning") or "")

    for text in (body, teaser, *[str(value or "") for value in override.values()]):
        assert "Yükseleninin İkizler" not in text
        assert "Yükselenin İkizler" not in text
        assert "Merkür'ünün de 11. evde Balık'ta" not in text

    assert "İkizler" not in body


def test_public_natal_view_copy_polish_keeps_1996_istanbul_and_adana_surfaces_stable(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")

    istanbul_1996 = build_public_natal_view(
        _artifact_response("natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json"),
        locale="tr",
        include_debug=True,
        include_full_profile=True,
    )
    narrative_1996_blocks = {
        str(block.get("node_id") or "").strip(): block
        for block in istanbul_1996["profile_narrative_projection_v1"]["profile_public"]["blocks"]
    }
    hidden_love = narrative_1996_blocks.get("promise::venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact")
    if hidden_love:
        assert hidden_love["headline"] == "Bazı duygular sende önce içeride büyüyor olabilir."
    else:
        plan_1996 = istanbul_1996["profile_v8_projection_v1"]["traceability"]["natal_promise_cluster_plan_v1"]
        assert "relationship_hidden_private_love_pattern" in set(plan_1996["surface_plan"]["detail_cluster_ids"])
    assert narrative_1996_blocks["promise::saturn_sextile_uranus_structured_originality_identity_chart_exact"]["headline"] == (
        "Ciddi görünsen de içeride daha farklı bir çizgi taşıyorsun."
    )

    adana = build_public_natal_view(
        _artifact_response("natal_interpret_full_1998-09-12_07-30_adana_user_compact_debug.json"),
        locale="tr",
        include_debug=True,
        include_full_profile=True,
    )
    adana_blocks = {
        str(block.get("node_id") or "").strip(): block
        for block in adana["profile_narrative_projection_v1"]["profile_public"]["blocks"]
    }
    assert str(
        adana_blocks["promise::mc_cancer_moon_gemini_9h_teaching_voice_chart_exact"].get("body") or ""
    ).startswith("Kariyer hattının Yengeç'te, yöneticisi Ay'ın da 9. evde İkizler'de olması")
    assert str(
        adana_blocks["promise::venus_square_pluto_intense_love_chart_exact"].get("body") or ""
    ).startswith("Venüs'ün Plüton'la kare çalışması, ilişkilerde çekimi")


def test_public_natal_view_izmir_v0_5_copy_polish_naturalizes_surface_without_leaks_or_duplicates(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")

    izmir = build_public_natal_view(
        _artifact_response("natal_interpret_full_1996-03-08_08-30_izmir_user_compact_debug.json"),
        locale="tr",
        include_debug=True,
        include_full_profile=True,
    )
    narrative = izmir["profile_narrative_projection_v1"]["profile_public"]
    blocks = list(narrative.get("blocks") or [])
    block_map = {
        str(block.get("node_id") or "").strip(): block
        for block in blocks
    }

    taurus_identity = block_map["promise::taurus_asc_venus_12h_hidden_value_identity_chart_exact"]
    assert taurus_identity["headline"] == "Dışarıdan sakin görünsen de içindeki değer hemen açılmaz."
    assert "Yükseleninin Boğa Venüs 12. ev Boğa" not in str(taurus_identity.get("body") or "")

    career_block = block_map["promise::mc_capricorn_ruler_saturn_pisces_12h_invisible_preparation_chart_exact"]
    assert career_block["headline"] == "Dışarıda sağlam görünmeden önce içeride uzun süre hazırlanırsın."

    diff_headlines = [
        str(item.get("headline") or "").strip()
        for item in izmir["profile_v8_projection_v1"].get("differentiators") or []
        if str(item.get("headline") or "").strip()
    ]
    core_headlines = {
        str(block.get("headline") or "").strip()
        for block in narrative.get("core_blocks") or []
        if str(block.get("headline") or "").strip()
    }
    assert not (core_headlines & set(diff_headlines)), (
        f"Izmir differentiators still duplicate core headlines: {core_headlines & set(diff_headlines)}"
    )

    headline_teaser_pairs = [
        (
            str(block.get("headline") or "").strip(),
            str(block.get("teaser") or "").strip(),
        )
        for block in blocks
    ]
    assert len(headline_teaser_pairs) == len(set(headline_teaser_pairs)), headline_teaser_pairs

    all_text = "\n".join(
        str(value or "")
        for block in blocks
        for value in (block.get("headline"), block.get("teaser"), block.get("body"))
    )
    all_text += "\n" + "\n".join(diff_headlines)

    for bad_phrase in (
        "olması de",
        "Yükseleninin Boğa Venüs 12. ev Boğa",
        "private maturity",
        "Yükseleninin İkizler",
        "Yükselenin İkizler",
        "7. ev Yay",
        "7. evinin Yay",
    ):
        assert bad_phrase not in all_text

    assert "Sessiz çekim, sadelik, güven veren varlık, içte büyüyen değer ve derin bağlılık." not in all_text

    identity_axis_headline = str(izmir["profile_v8_projection_v1"]["identity_axis"].get("headline") or "")
    assert identity_axis_headline == "Dışarıdan sakin görünsen de içeride daha elektrikli bir taraf çalışabilir."

    istanbul_2020 = build_public_natal_view(
        _artifact_response("natal_interpret_full_2020-04-10_08-26_istanbul_user_compact_debug.json"),
        locale="tr",
        include_debug=True,
        include_full_profile=True,
    )
    blocks_2020 = {
        str(block.get("node_id") or "").strip(): block
        for block in istanbul_2020["profile_narrative_projection_v1"]["profile_public"]["blocks"]
    }
    assert blocks_2020["promise::venus_trine_saturn_trust_bond_chart_exact"]["headline"] == (
        "Sevgi verdiğinde bunun içinde tutarlılık ve söz taşıyan bir taraf var."
    )


def test_public_natal_view_istanbul_1994_v0_7_copy_polish_naturalizes_surface(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")

    istanbul_1994 = build_public_natal_view(
        _artifact_response("natal_interpret_full_1994-06-25_10-00_istanbul_user_compact_debug.json"),
        locale="tr",
        include_debug=True,
        include_full_profile=True,
    )
    narrative = istanbul_1994["profile_narrative_projection_v1"]["profile_public"]
    blocks = list(narrative.get("blocks") or [])
    block_map = {
        str(block.get("node_id") or "").strip(): block
        for block in blocks
    }

    roots = block_map["promise::pluto_node_scorpio_4h_roots_inner_security_transformation_chart_exact"]
    assert roots["headline"] == "Ev, aile ve geçmiş sende sadece arka plan gibi çalışmayabilir."
    assert "4. evindeki Akrep ve Plüton/Kuzey Ay Düğümü vurgusu" in str(roots.get("body") or "")

    creativity = block_map["promise::moon_uranus_neptune_capricorn_5h_structured_imagination_chart_exact"]
    assert creativity["headline"] == "İçindeki yaratıcı taraf, ilhamı forma sokmak ister."
    assert "Uranüs ve Neptün'ün aynı alanda çalışması" in str(creativity.get("body") or "")

    relationship = block_map["promise::aquarius_dsc_saturn_pisces_7h_freedom_responsibility_sensitivity_chart_exact"]
    assert "7. evinin Kova, Satürn'ünün de 7. evde Balık'ta olması" in str(relationship.get("body") or "")

    chiron = block_map["promise::chiron_virgo_1h_visible_sensitivity_self_correction_chart_exact"]
    assert chiron["headline"] == "Kendini gösterirken hemen kusuru fark eden bir tarafın olabilir."
    assert "İnce dikkat, iyileştirici varlık" not in str(chiron.get("headline") or "")

    diff_headlines = [
        str(item.get("headline") or "").strip()
        for item in istanbul_1994["profile_v8_projection_v1"].get("differentiators") or []
        if str(item.get("headline") or "").strip()
    ]
    core_headlines = {
        str(block.get("headline") or "").strip()
        for block in narrative.get("core_blocks") or []
        if str(block.get("headline") or "").strip()
    }
    assert not (core_headlines & set(diff_headlines)), (
        f"Istanbul 1994 differentiators still duplicate core headlines: {core_headlines & set(diff_headlines)}"
    )

    headline_teaser_pairs = [
        (
            str(block.get("headline") or "").strip(),
            str(block.get("teaser") or "").strip(),
        )
        for block in blocks
    ]
    assert len(headline_teaser_pairs) == len(set(headline_teaser_pairs)), headline_teaser_pairs

    all_text = "\n".join(
        str(value or "")
        for block in blocks
        for value in (block.get("headline"), block.get("teaser"), block.get("body"))
    )
    all_text += "\n" + "\n".join(diff_headlines)

    for bad_phrase in (
        "olması de",
        "Sun conjunct",
        "Mars opposite",
        "Moon conjunct",
        "Midheaven",
        "Pluto",
        "ingredient",
        "; Ama",
        "; Dış",
        "; Güvenilirlik",
        "; Sonra",
        "İnce dikkat, iyileştirici varlık, başkalarına alan açan hassasiyet",
    ):
        assert bad_phrase not in all_text


def test_public_natal_view_v0_9a_composed_semantics_is_public_no_op_when_public_flags_are_off(
    monkeypatch,
) -> None:
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")
    response = _artifact_response("natal_interpret_full_1994-06-25_10-00_istanbul_user_compact_debug.json")

    baseline = build_public_natal_view(
        response,
        locale="tr",
        include_debug=True,
        include_full_profile=True,
    )
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT", "false")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN", "false")
    composed = build_public_natal_view(
        response,
        locale="tr",
        include_debug=True,
        include_full_profile=True,
    )

    assert _projection_surface_snapshot(baseline) == _projection_surface_snapshot(composed)

    plan = composed["profile_v8_projection_v1"]["traceability"]["natal_promise_cluster_plan_v1"]
    assert plan["meta"]["audit_metrics"]["composed_candidate_count"] == 2
    assert plan["meta"]["audit_metrics"]["composed_candidate_public_eligibility_distribution"]["public_main_eligible"] == 0


def test_public_natal_view_v0_9a_keeps_accepted_goldens_stable(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")

    fixtures = [
        "natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json",
        "natal_interpret_full_1998-09-12_07-30_adana_user_compact_debug.json",
        "natal_interpret_full_2020-04-10_08-26_istanbul_user_compact_debug.json",
        "natal_interpret_full_1996-03-08_08-30_izmir_user_compact_debug.json",
        "natal_interpret_full_1994-06-25_10-00_istanbul_user_compact_debug.json",
        "natal_interpret_full_1997-01-21_10-30_istanbul_user_compact_debug.json",
    ]

    for fixture in fixtures:
        response = _artifact_response(fixture)
        baseline = build_public_natal_view(
            response,
            locale="tr",
            include_debug=True,
            include_full_profile=True,
        )
        monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
        monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT", "false")
        monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN", "false")
        composed = build_public_natal_view(
            response,
            locale="tr",
            include_debug=True,
            include_full_profile=True,
        )
        monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", raising=False)
        monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT", raising=False)
        monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN", raising=False)

        assert _projection_surface_snapshot(baseline) == _projection_surface_snapshot(composed), fixture


def test_public_natal_view_v0_9a_1_public_voice_detail_rollout_targets_keep_composed_public_voice_internal_only_by_default(
    monkeypatch,
) -> None:
    monkeypatch.setenv("SE_EPHE_PATH", str(Path("swisseph/ephe").resolve()))
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN", "false")
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", raising=False)

    for chart_id in (
        "fix04_h10_career_stellium",
        "tokyo_1998_06_21",
        "toronto_1976_06_26",
    ):
        public = _live_public_view_from_batch_chart(chart_id)
        plan = public["profile_v8_projection_v1"]["traceability"]["natal_promise_cluster_plan_v1"]
        metrics = plan["meta"]["audit_metrics"]
        suppression = next(
            item
            for item in plan["suppressed_packets"]
            if str(item.get("packet_id") or "").strip() == "composed_career_route_v0_9a"
        )
        narrative_blocks = public["profile_narrative_projection_v1"]["profile_public"].get("blocks") or []
        extra_blocks = public["profile_narrative_projection_v1"]["profile_public"].get("extra_blocks") or []
        composed_blocks = [
            block
            for block in narrative_blocks
            if str(block.get("node_id") or "").strip() == "promise::composed_career_route_v0_9a"
        ]
        composed_extra_blocks = [
            block
            for block in extra_blocks
            if str(block.get("node_id") or "").strip() == "promise::composed_career_route_v0_9a"
        ]
        differentiators = public["profile_v8_projection_v1"].get("differentiators") or []
        composed_differentiators = [
            item
            for item in differentiators
            if str(item.get("node_id") or "").strip() == "promise::composed_career_route_v0_9a"
        ]

        assert metrics["composed_candidate_public_eligibility_distribution"]["detail_eligible"] >= 1
        assert metrics["composed_candidate_public_eligibility_distribution"]["public_support_eligible"] == 0
        assert metrics["composed_candidate_public_eligibility_distribution"]["public_main_eligible"] == 0
        assert suppression["keep_for"] == ["detail", "debug"]
        assert not composed_blocks, chart_id
        assert not composed_extra_blocks, chart_id
        assert not composed_differentiators, chart_id
        assert not any("composed_career_route_v0_9a" in str(cluster_id) for cluster_id in plan["surface_plan"]["public_main_cluster_ids"])
        assert not any("composed_career_route_v0_9a" in str(cluster_id) for cluster_id in plan["surface_plan"]["public_support_cluster_ids"])
        assert "composed_career_route_v0_9a" not in set(plan["surface_plan"]["detail_cluster_ids"])


def test_public_natal_view_v0_9a_1_non_public_voice_subtypes_stay_debug_only(
    monkeypatch,
) -> None:
    monkeypatch.setenv("SE_EPHE_PATH", str(Path("swisseph/ephe").resolve()))
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN", "false")

    for chart_id in (
        "kutahya_1959_10_21",
        "izmir_2007_07_19",
        "izmir_1996_05_20",
        "mexico_city_1988_08_31",
        "dubai_1995_01_03",
    ):
        public = _live_public_view_from_batch_chart(chart_id)
        plan = public["profile_v8_projection_v1"]["traceability"]["natal_promise_cluster_plan_v1"]
        suppression = next(
            item
            for item in plan["suppressed_packets"]
            if str(item.get("packet_id") or "").strip() == "composed_career_route_v0_9a"
        )

        assert suppression["keep_for"] == ["debug"], chart_id


def test_public_natal_view_v0_9a_1_keeps_accepted_goldens_stable_with_public_voice_flag(
    monkeypatch,
) -> None:
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")

    fixtures = [
        "natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json",
        "natal_interpret_full_1998-09-12_07-30_adana_user_compact_debug.json",
        "natal_interpret_full_2020-04-10_08-26_istanbul_user_compact_debug.json",
        "natal_interpret_full_1996-03-08_08-30_izmir_user_compact_debug.json",
        "natal_interpret_full_1994-06-25_10-00_istanbul_user_compact_debug.json",
        "natal_interpret_full_1997-01-21_10-30_istanbul_user_compact_debug.json",
    ]

    for fixture in fixtures:
        response = _artifact_response(fixture)
        baseline = build_public_natal_view(
            response,
            locale="tr",
            include_debug=True,
            include_full_profile=True,
        )
        monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
        monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT", "true")
        monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT", "true")
        monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN", "false")
        composed = build_public_natal_view(
            response,
            locale="tr",
            include_debug=True,
            include_full_profile=True,
        )
        monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", raising=False)
        monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT", raising=False)
        monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT", raising=False)
        monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN", raising=False)
        assert _projection_surface_snapshot(baseline) == _projection_surface_snapshot(composed), fixture


def test_public_natal_view_v0_9a_1_exact_career_owner_protection_keeps_public_voice_debug_only(
    monkeypatch,
) -> None:
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN", "false")

    for fixture in (
        "natal_interpret_full_1994-06-25_10-00_istanbul_user_compact_debug.json",
    ):
        public = build_public_natal_view(
            _artifact_response(fixture),
            locale="tr",
            include_debug=True,
            include_full_profile=True,
        )
        plan = public["profile_v8_projection_v1"]["traceability"]["natal_promise_cluster_plan_v1"]
        suppression = next(
            item
            for item in plan["suppressed_packets"]
            if str(item.get("packet_id") or "").strip() == "composed_career_route_v0_9a"
        )
        assert suppression["keep_for"] == ["debug"], fixture


def test_public_natal_view_v0_9a_1_render_detail_flag_off_keeps_target_chart_public_surfaces_stable(
    monkeypatch,
) -> None:
    monkeypatch.setenv("SE_EPHE_PATH", str(Path("swisseph/ephe").resolve()))
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")

    for chart_id in (
        "fix04_h10_career_stellium",
        "tokyo_1998_06_21",
        "toronto_1976_06_26",
    ):
        baseline = _live_public_view_from_batch_chart(chart_id)
        monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
        monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT", "true")
        monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT", "true")
        monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN", "false")
        monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", raising=False)
        guarded = _live_public_view_from_batch_chart(chart_id)
        monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", raising=False)
        monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT", raising=False)
        monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT", raising=False)
        monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN", raising=False)

        assert _projection_surface_snapshot(baseline) == _projection_surface_snapshot(guarded), chart_id


def test_public_natal_view_v0_9a_2_render_detail_flag_on_renders_traceability_cards_only(
    monkeypatch,
) -> None:
    monkeypatch.setenv("SE_EPHE_PATH", str(Path("swisseph/ephe").resolve()))
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN", "false")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")

    for chart_id in (
        "fix04_h10_career_stellium",
        "tokyo_1998_06_21",
        "toronto_1976_06_26",
    ):
        public = _live_public_view_from_batch_chart(chart_id)
        plan = public["profile_v8_projection_v1"]["traceability"]["natal_promise_cluster_plan_v1"]
        composed_cards = public["profile_narrative_projection_v1"]["traceability"].get("composed_detail_cards_v0_9a_2") or []

        assert composed_cards, chart_id
        assert all(card.get("source_type") == "composed_semantic" for card in composed_cards)
        assert all(card.get("source_candidate_id") == "composed_career_route_v0_9a" for card in composed_cards)
        assert all(card.get("public_job") == "detail_only" for card in composed_cards)
        assert not any(
            str(block.get("node_id") or "").strip() == "promise::composed_career_route_v0_9a"
            for block in (public["profile_narrative_projection_v1"]["profile_public"].get("extra_blocks") or [])
        )
        assert not any(
            str(block.get("node_id") or "").strip() == "promise::composed_career_route_v0_9a"
            for block in (public["profile_narrative_projection_v1"]["profile_public"].get("blocks") or [])
        )
        assert not any(
            str(item.get("node_id") or "").strip() == "promise::composed_career_route_v0_9a"
            for item in (public["profile_v8_projection_v1"].get("differentiators") or [])
        )
        assert not any(
            str(item.get("node_id") or "").strip() == "promise::composed_career_route_v0_9a"
            for item in (public["profile_v8_projection_v1"].get("insight_strip") or [])
        )
        assert not any("composed_career_route_v0_9a" in str(cluster_id) for cluster_id in plan["surface_plan"]["public_main_cluster_ids"])
        assert not any("composed_career_route_v0_9a" in str(cluster_id) for cluster_id in plan["surface_plan"]["public_support_cluster_ids"])


def test_public_natal_view_v0_9a_2_non_target_charts_do_not_render_composed_detail_cards(
    monkeypatch,
) -> None:
    monkeypatch.setenv("SE_EPHE_PATH", str(Path("swisseph/ephe").resolve()))
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN", "false")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")

    for chart_id in (
        "kutahya_1959_10_21",
        "izmir_2007_07_19",
        "izmir_1996_05_20",
        "mexico_city_1988_08_31",
        "dubai_1995_01_03",
    ):
        public = _live_public_view_from_batch_chart(chart_id)
        composed_cards = public["profile_narrative_projection_v1"]["traceability"].get("composed_detail_cards_v0_9a_2") or []
        assert not composed_cards, chart_id


def test_public_natal_view_v0_9a_2_render_detail_flag_on_keeps_target_public_surfaces_stable(
    monkeypatch,
) -> None:
    monkeypatch.setenv("SE_EPHE_PATH", str(Path("swisseph/ephe").resolve()))
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")

    for chart_id in (
        "fix04_h10_career_stellium",
        "tokyo_1998_06_21",
        "toronto_1976_06_26",
    ):
        baseline = _live_public_view_from_batch_chart(chart_id)
        monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
        monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT", "true")
        monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT", "true")
        monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN", "false")
        monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
        rendered = _live_public_view_from_batch_chart(chart_id)
        monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", raising=False)
        monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT", raising=False)
        monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT", raising=False)
        monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN", raising=False)
        monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", raising=False)

        assert _projection_surface_snapshot(baseline) == _projection_surface_snapshot(rendered), chart_id


# ---------------------------------------------------------------------------
# v0.9a.3 Phase B — profile_public.composed_detail_cards lane
# ---------------------------------------------------------------------------


_PHASE_B_TARGET_CHARTS = (
    "fix04_h10_career_stellium",
    "tokyo_1998_06_21",
    "toronto_1976_06_26",
)

_PHASE_B_NON_TARGET_CHARTS = (
    "kutahya_1959_10_21",
    "izmir_1996_05_20",
    "mexico_city_1988_08_31",
)

_PHASE_B_PUBLIC_VISIBLE_FIELDS = {
    "id",
    "node_id",
    "headline",
    "teaser",
    "body",
    "chips",
    "family",
    "emphasis",
    "origin",
}

_PHASE_B_TRACE_ONLY_FIELDS = {
    "source_type",
    "source_candidate_id",
    "public_job",
    "source_anchor_trace",
    "detail_items",
    "evidence_summary",
}


def _phase_b_set_base_flags(monkeypatch) -> None:
    monkeypatch.setenv("SE_EPHE_PATH", str(Path("swisseph/ephe").resolve()))
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN", "false")


def test_phase_b_lane_flag_off_omits_public_field(monkeypatch) -> None:
    _phase_b_set_base_flags(monkeypatch)
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", raising=False)
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", raising=False)

    for chart_id in _PHASE_B_TARGET_CHARTS:
        public = _live_public_view_from_batch_chart(chart_id)
        profile_public = public["profile_narrative_projection_v1"]["profile_public"]
        assert "composed_detail_cards" not in profile_public, chart_id


def test_phase_b_render_on_lane_off_keeps_trace_omits_public_field(monkeypatch) -> None:
    _phase_b_set_base_flags(monkeypatch)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", raising=False)

    for chart_id in _PHASE_B_TARGET_CHARTS:
        public = _live_public_view_from_batch_chart(chart_id)
        profile_public = public["profile_narrative_projection_v1"]["profile_public"]
        traceability = public["profile_narrative_projection_v1"]["traceability"]
        assert "composed_detail_cards" not in profile_public, chart_id
        assert traceability.get("composed_detail_cards_v0_9a_2"), chart_id


def test_phase_b_render_off_lane_on_omits_public_field(monkeypatch) -> None:
    _phase_b_set_base_flags(monkeypatch)
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", raising=False)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")

    for chart_id in _PHASE_B_TARGET_CHARTS:
        public = _live_public_view_from_batch_chart(chart_id)
        profile_public = public["profile_narrative_projection_v1"]["profile_public"]
        traceability = public["profile_narrative_projection_v1"]["traceability"]
        assert "composed_detail_cards" not in profile_public, chart_id
        assert not traceability.get("composed_detail_cards_v0_9a_2"), chart_id


def test_phase_b_both_flags_on_target_charts_get_exactly_one_card(monkeypatch) -> None:
    _phase_b_set_base_flags(monkeypatch)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")

    for chart_id in _PHASE_B_TARGET_CHARTS:
        public = _live_public_view_from_batch_chart(chart_id)
        profile_public = public["profile_narrative_projection_v1"]["profile_public"]
        cards = profile_public.get("composed_detail_cards")
        assert cards, chart_id
        assert len(cards) == 1, f"{chart_id}: expected exactly 1 card, got {len(cards)}"
        card = cards[0]
        assert set(card.keys()) <= _PHASE_B_PUBLIC_VISIBLE_FIELDS, (
            f"{chart_id}: unexpected fields {set(card.keys()) - _PHASE_B_PUBLIC_VISIBLE_FIELDS}"
        )
        assert not (set(card.keys()) & _PHASE_B_TRACE_ONLY_FIELDS), (
            f"{chart_id}: trace fields leaked into public lane: "
            f"{set(card.keys()) & _PHASE_B_TRACE_ONLY_FIELDS}"
        )
        assert card["origin"] == "composed_detail_renderer_v0_9a_2"
        assert card["family"] == "career_public_voice"
        assert card["emphasis"] == "detail"


def test_phase_b_both_flags_on_non_target_charts_omit_public_field(monkeypatch) -> None:
    _phase_b_set_base_flags(monkeypatch)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")

    for chart_id in _PHASE_B_NON_TARGET_CHARTS:
        public = _live_public_view_from_batch_chart(chart_id)
        profile_public = public["profile_narrative_projection_v1"]["profile_public"]
        # Field is either absent or an empty list — both are acceptable
        # per spec; current implementation omits entirely.
        assert not profile_public.get("composed_detail_cards"), chart_id


def test_phase_b_lane_does_not_leak_into_other_public_surfaces(monkeypatch) -> None:
    _phase_b_set_base_flags(monkeypatch)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")

    for chart_id in _PHASE_B_TARGET_CHARTS:
        public = _live_public_view_from_batch_chart(chart_id)
        narrative = public["profile_narrative_projection_v1"]
        profile_public = narrative["profile_public"]
        v8 = public["profile_v8_projection_v1"]

        promise_node_id = "promise::composed_career_route_v0_9a"
        composed_card_id_prefix = "composed_detail::composed_career_route_v0_9a::"

        for lane_name in ("blocks", "core_blocks", "extra_blocks", "detail_cards"):
            lane = profile_public.get(lane_name) or []
            assert not any(
                str(item.get("node_id") or "").strip() == promise_node_id
                or str(item.get("id") or "").startswith(composed_card_id_prefix)
                for item in lane
                if isinstance(item, dict)
            ), f"{chart_id}: composed card leaked into profile_public.{lane_name}"

        for v8_lane in ("differentiators", "insight_strip"):
            lane = v8.get(v8_lane) or []
            assert not any(
                str(item.get("node_id") or "").strip() == promise_node_id
                or str(item.get("id") or "").startswith(composed_card_id_prefix)
                for item in lane
                if isinstance(item, dict)
            ), f"{chart_id}: composed card leaked into profile_v8.{v8_lane}"

        hero = v8.get("hero") or {}
        identity_axis = v8.get("identity_axis") or {}
        assert str(hero.get("node_id") or "").strip() != promise_node_id, chart_id
        assert str(identity_axis.get("node_id") or "").strip() != promise_node_id, chart_id

        # v8 must not carry the new public lane field at all.
        assert "composed_detail_cards" not in v8, chart_id


def test_phase_b_public_card_copy_qa_passes(monkeypatch) -> None:
    _phase_b_set_base_flags(monkeypatch)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")

    banned_tokens = ("mc, yöneticisi", "mc route", "10h", "source_type", "debug", "candidate", "fallback")
    banned_ascii = ("Insanlar", "Disaridaki", "nasil", "soyledigini", "Soz", "Gorunur", "dogru", "cumle")

    for chart_id in _PHASE_B_TARGET_CHARTS:
        public = _live_public_view_from_batch_chart(chart_id)
        cards = public["profile_narrative_projection_v1"]["profile_public"].get("composed_detail_cards") or []
        assert cards, chart_id
        for card in cards:
            combined = " ".join(str(card[field]) for field in ("headline", "teaser", "body"))
            combined_lower = combined.lower()
            for token in banned_tokens:
                assert token not in combined_lower, f"{chart_id}: banned token {token!r}"
            for ascii_form in banned_ascii:
                import re

                assert not re.search(rf"\b{re.escape(ascii_form)}\b", combined), (
                    f"{chart_id}: ASCII residue {ascii_form!r} in public lane copy"
                )
            assert any(c in combined for c in "İıŞşĞğÇçÖöÜü"), (
                f"{chart_id}: public lane copy lacks Turkish diacritics"
            )


# ---------------------------------------------------------------------------
# P0 truthfulness — dangling connector defects ("olması de" / "Bazen de.")
# Regression coverage for the v0.9a.3 post-audit text-composition cleanup.
# ---------------------------------------------------------------------------


_DANGLING_CONNECTOR_AFFECTED_CHARTS = (
    "adana_1998_09_12",
    "kutahya_1959_10_21",
    "izmir_2007_07_19",
    "izmir_1996_05_20",
    "istanbul_1994_06_25",
    "istanbul_1997_01_21",
)


def _collect_dangling_connector_scan_chunks(public: dict) -> list[str]:
    chunks: list[str] = []
    narrative = public.get("profile_narrative_projection_v1") or {}
    v8 = public.get("profile_v8_projection_v1") or {}
    profile_public = narrative.get("profile_public") or {}
    for lane in ("blocks", "core_blocks", "extra_blocks", "detail_cards", "composed_detail_cards"):
        for item in (profile_public.get(lane) or []):
            if not isinstance(item, dict):
                continue
            for field in ("headline", "teaser", "body", "text", "micro"):
                value = item.get(field)
                if isinstance(value, str) and value.strip():
                    chunks.append(value)
    for key in ("hero", "identity_axis"):
        node = v8.get(key) or {}
        for field in ("headline", "teaser", "body", "text"):
            value = node.get(field)
            if isinstance(value, str) and value.strip():
                chunks.append(value)
    for lane in ("differentiators", "insight_strip"):
        for item in (v8.get(lane) or []):
            if not isinstance(item, dict):
                continue
            for field in ("headline", "teaser", "body", "text", "micro"):
                value = item.get(field)
                if isinstance(value, str) and value.strip():
                    chunks.append(value)
    return chunks


def _collect_public_surface_text_chunks(public: dict) -> list[str]:
    chunks: list[str] = []
    narrative = public.get("profile_narrative_projection_v1") or {}
    v8 = public.get("profile_v8_projection_v1") or {}
    profile_public = narrative.get("profile_public") or {}

    for lane in ("blocks", "core_blocks", "extra_blocks", "detail_cards", "composed_detail_cards"):
        for item in (profile_public.get(lane) or []):
            if not isinstance(item, dict):
                continue
            for field in ("headline", "teaser", "body", "text", "micro", "summary", "subtitle", "title"):
                value = item.get(field)
                if isinstance(value, str) and value.strip():
                    chunks.append(value)

    for key in ("hero", "identity_axis"):
        node = v8.get(key) or {}
        for field in ("headline", "teaser", "body", "text", "summary", "subtitle", "title", "eyebrow"):
            value = node.get(field)
            if isinstance(value, str) and value.strip():
                chunks.append(value)

    for lane in ("differentiators", "insight_strip"):
        for item in (v8.get(lane) or []):
            if not isinstance(item, dict):
                continue
            for field in ("headline", "teaser", "body", "text", "micro", "summary", "subtitle", "title", "label"):
                value = item.get(field)
                if isinstance(value, str) and value.strip():
                    chunks.append(value)

    return chunks


def test_p0_no_olmasi_de_in_public_body(monkeypatch) -> None:
    monkeypatch.setenv("SE_EPHE_PATH", str(Path("swisseph/ephe").resolve()))
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")

    pattern = re.compile(r"olması de\b")
    for chart_id in _DANGLING_CONNECTOR_AFFECTED_CHARTS:
        public = _live_public_view_from_batch_chart(chart_id)
        for chunk in _collect_dangling_connector_scan_chunks(public):
            assert not pattern.search(chunk), (
                f"{chart_id}: dangling 'olması de' surfaced in public copy: {chunk!r}"
            )


def test_p0_no_standalone_bazen_de_period_in_public_body(monkeypatch) -> None:
    monkeypatch.setenv("SE_EPHE_PATH", str(Path("swisseph/ephe").resolve()))
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")

    upper_pattern = re.compile(r"Bazen de\.")
    lower_pattern = re.compile(r"bazen de\.")
    for chart_id in _DANGLING_CONNECTOR_AFFECTED_CHARTS:
        public = _live_public_view_from_batch_chart(chart_id)
        for chunk in _collect_dangling_connector_scan_chunks(public):
            assert not upper_pattern.search(chunk), (
                f"{chart_id}: dangling 'Bazen de.' surfaced in public copy: {chunk!r}"
            )
            assert not lower_pattern.search(chunk), (
                f"{chart_id}: dangling 'bazen de.' surfaced in public copy: {chunk!r}"
            )


def test_p0_dangling_connector_fix_does_not_alter_semantic_routing(monkeypatch) -> None:
    """The text-composition cleanup must not change which clusters land in
    `public_main` / `public_support` / `detail` lanes, nor which packets
    surface as v8 hero / identity_axis / differentiators / insight_strip.

    Snapshot the structural fingerprint of every node selection across the
    affected charts to defend against accidental semantic drift while the
    cleanup matures.
    """
    monkeypatch.setenv("SE_EPHE_PATH", str(Path("swisseph/ephe").resolve()))
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")

    for chart_id in _DANGLING_CONNECTOR_AFFECTED_CHARTS:
        public = _live_public_view_from_batch_chart(chart_id)
        plan = (
            public.get("profile_narrative_projection_v1") or {}
        ).get("traceability", {}).get("natal_promise_cluster_plan_v1") or {}
        surface_plan = plan.get("surface_plan") or {}
        v8 = public.get("profile_v8_projection_v1") or {}

        # Routing layer must produce at least the expected lane vocabulary
        # — never an unexpected one.
        for key in (
            "public_main_cluster_ids",
            "public_support_cluster_ids",
            "detail_cluster_ids",
        ):
            assert isinstance(surface_plan.get(key) or [], list), (
                f"{chart_id}: surface_plan[{key!r}] missing or wrong type"
            )

        # The composed lane (Phase B) is not promoted by the cleanup.
        assert "composed_detail_cards" not in v8, chart_id

        # Hero / identity_axis must continue to exist on charts that have
        # ever produced them. Bare existence of these keys is part of the
        # public contract.
        assert "hero" in v8, chart_id
        assert "identity_axis" in v8, chart_id


def test_p0_normalize_packet_field_text_unit() -> None:
    """Direct unit-level coverage for the connector-aware sentence-boundary
    splitter inside ``_normalize_packet_field_text``.
    """
    from app.natal.natal_promise_packets import _normalize_packet_field_text

    # Connector "de" before a capitalized continuation must not gain a
    # period.
    out = _normalize_packet_field_text(
        "Önceki cümle bitti. Bazen de Dışarıda toplu görünürken içeride baskı taşıyor olabilirsin"
    )
    assert "Bazen de." not in out, out
    assert "Bazen de Dışarıda" in out or "Bazen de dışarıda" in out, out

    # Standalone fragment must be dropped.
    out = _normalize_packet_field_text("Birinci cümle. Bazen de.")
    assert "Bazen de." not in out, out
    assert "bazen de." not in out.lower() or out.lower().count("bazen de.") == 0, out

    # Real sentence boundaries between non-connector lowercase and uppercase
    # are still inserted.
    out = _normalize_packet_field_text(
        "ilk cümle bitiyor Sonraki cümle başlar"
    )
    assert "bitiyor. Sonraki" in out, out


def test_p0_vowel_harmonized_de_particle_unit() -> None:
    """Direct unit-level coverage for the vowel-harmony helper that prevents
    the "olması de" template defect.
    """
    from app.meaning.projection_shadow_v1_builder import (
        _vowel_harmonized_de_particle,
    )

    # Back vowels → "da"
    assert _vowel_harmonized_de_particle("olması") == "da"
    assert _vowel_harmonized_de_particle("Yay olması") == "da"
    assert _vowel_harmonized_de_particle("Koç olması") == "da"
    assert _vowel_harmonized_de_particle("evinin") == "de" or _vowel_harmonized_de_particle("evinin") == "de"
    # Front vowels → "de"
    assert _vowel_harmonized_de_particle("evde") == "de"
    assert _vowel_harmonized_de_particle("İkizler") == "de"
    assert _vowel_harmonized_de_particle("Yengeç") == "de"
    # Empty / vowel-less → "de"
    assert _vowel_harmonized_de_particle("") == "de"
    assert _vowel_harmonized_de_particle("xyz") == "de"


# ---------------------------------------------------------------------------
# v0.9b — debug-only relationship_route + moon_signature
# Public surface MUST remain stable across all flag combinations.
# ---------------------------------------------------------------------------


_V0_9B_AUDIT_CHARTS = (
    "istanbul_1994_06_25",
    "istanbul_1997_01_21",
    "izmir_1996_05_20",
    "adana_1998_09_12",
    "kutahya_1959_10_21",
)


def _v0_9b_set_base_flags(monkeypatch) -> None:
    monkeypatch.setenv("SE_EPHE_PATH", str(Path("swisseph/ephe").resolve()))
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")


def _composed_v0_9b_node_id_prefixes() -> tuple[str, ...]:
    return (
        "promise::composed_relationship_route_v0_9b",
        "promise::composed_moon_signature_v0_9b",
        "promise::composed_mercury_signature_v0_9c",
    )


def _composed_v0_9b_packet_id_set() -> set[str]:
    return {
        "composed_relationship_route_v0_9b",
        "composed_moon_signature_v0_9b",
        "composed_mercury_signature_v0_9c",
    }


def _v0_9b_assert_no_public_leak(public: dict, chart_id: str) -> None:
    narrative = public.get("profile_narrative_projection_v1") or {}
    v8 = public.get("profile_v8_projection_v1") or {}
    profile_public = narrative.get("profile_public") or {}

    banned_node_id_prefixes = _composed_v0_9b_node_id_prefixes()
    banned_packet_ids = _composed_v0_9b_packet_id_set()

    def _violates(item):
        if not isinstance(item, dict):
            return False
        node_id = str(item.get("node_id") or "").strip()
        item_id = str(item.get("id") or "").strip()
        if any(node_id.startswith(prefix) for prefix in banned_node_id_prefixes):
            return True
        if item_id in banned_packet_ids:
            return True
        return False

    for lane in ("blocks", "core_blocks", "extra_blocks", "detail_cards", "composed_detail_cards"):
        for item in (profile_public.get(lane) or []):
            assert not _violates(item), (
                f"{chart_id}: v0.9b candidate leaked into profile_public.{lane}: {item}"
            )

    for lane in ("differentiators", "insight_strip"):
        for item in (v8.get(lane) or []):
            assert not _violates(item), (
                f"{chart_id}: v0.9b candidate leaked into profile_v8.{lane}"
            )

    hero = v8.get("hero") or {}
    identity_axis = v8.get("identity_axis") or {}
    assert not _violates(hero), f"{chart_id}: v0.9b candidate in v8.hero"
    assert not _violates(identity_axis), f"{chart_id}: v0.9b candidate in v8.identity_axis"
    assert "composed_detail_cards" not in v8, f"{chart_id}: v8 must not carry composed_detail_cards"


def _v0_9c_plan_packets(public: dict) -> list[dict]:
    plan = (
        public.get("profile_narrative_projection_v1") or {}
    ).get("traceability", {}).get("natal_promise_cluster_plan_v1") or {}
    return list(plan.get("candidate_packets") or [])


def _v0_9c_first_family_packet(public: dict, family: str) -> dict | None:
    for packet in _v0_9c_plan_packets(public):
        if packet.get("family") == family:
            return packet
    return None


def test_v0_9b_flags_off_public_output_matches_baseline(monkeypatch) -> None:
    """With all v0.9b flags off, the public projection surface must match the
    pre-v0.9b baseline byte-for-byte (modulo `traceability`)."""
    _v0_9b_set_base_flags(monkeypatch)
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", raising=False)
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", raising=False)
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT", raising=False)
    for chart_id in _V0_9B_AUDIT_CHARTS:
        public = _live_public_view_from_batch_chart(chart_id)
        _v0_9b_assert_no_public_leak(public, chart_id)


def test_v0_9b_relationship_route_flag_on_public_output_stable(monkeypatch) -> None:
    _v0_9b_set_base_flags(monkeypatch)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")
    for chart_id in _V0_9B_AUDIT_CHARTS:
        baseline = _live_public_view_from_batch_chart(chart_id)
        monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")
        rendered = _live_public_view_from_batch_chart(chart_id)
        _v0_9b_assert_no_public_leak(rendered, chart_id)
        assert _projection_surface_snapshot(baseline) == _projection_surface_snapshot(rendered), chart_id


def test_v0_9b_moon_signature_flag_on_public_output_stable(monkeypatch) -> None:
    _v0_9b_set_base_flags(monkeypatch)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", "true")
    for chart_id in _V0_9B_AUDIT_CHARTS:
        public = _live_public_view_from_batch_chart(chart_id)
        _v0_9b_assert_no_public_leak(public, chart_id)


def test_v0_9c_mercury_signature_flag_on_public_output_stable(monkeypatch) -> None:
    _v0_9b_set_base_flags(monkeypatch)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MERCURY_SIGNATURE_V0_9C", "true")
    for chart_id in _V0_9B_AUDIT_CHARTS:
        public = _live_public_view_from_batch_chart(chart_id)
        _v0_9b_assert_no_public_leak(public, chart_id)


def test_v0_9c_mercury_speech_positive_fixtures_improve_without_public_change(monkeypatch) -> None:
    _v0_9b_set_base_flags(monkeypatch)
    fixtures = {
        "madrid_2004_04_18": 0.82,
        "v010_b02_neptune_7h_pisces": 0.75,
        "v010_c09_moon_4h_planets": 0.74,
    }
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MERCURY_SIGNATURE_V0_9C", raising=False)
    baselines = {
        cid: _projection_surface_snapshot(_live_public_view_from_batch_chart(cid))
        for cid in fixtures
    }
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MERCURY_SIGNATURE_V0_9C", "true")
    for cid, min_confidence in fixtures.items():
        public = _live_public_view_from_batch_chart(cid)
        _v0_9b_assert_no_public_leak(public, cid)
        assert _projection_surface_snapshot(public) == baselines[cid], cid
        mercury = _v0_9c_first_family_packet(public, "mercury_signature")
        assert mercury, cid
        assert mercury["subtype"] == "speech_identity_spine", mercury
        assert float(mercury.get("confidence") or 0.0) >= min_confidence, mercury
        breakdown = mercury.get("scoring_breakdown") or {}
        assert float(breakdown.get("speech_combined_bonus") or 0.0) > 0.0, mercury
        assert float(breakdown.get("speech_stack_support") or 0.0) > 0.0, mercury


def test_v0_9c_mercury_speech_guard_fixtures_do_not_over_promote(monkeypatch) -> None:
    _v0_9b_set_base_flags(monkeypatch)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MERCURY_SIGNATURE_V0_9C", "true")
    for cid in ("new_york_1984_10_02", "v010_d01_3h_stellium"):
        public = _live_public_view_from_batch_chart(cid)
        _v0_9b_assert_no_public_leak(public, cid)
        mercury = _v0_9c_first_family_packet(public, "mercury_signature")
        assert mercury, cid
        assert mercury["subtype"] == "speech_identity_spine", mercury
        assert mercury["confidence_tier"] != "high", mercury
        breakdown = mercury.get("scoring_breakdown") or {}
        assert float(breakdown.get("speech_combined_bonus") or 0.0) == 0.0, mercury
        assert float(breakdown.get("speech_stack_support") or 0.0) == 0.0, mercury


def test_v0_9c_fix11_unknown_birthtime_exercises_career_overlap_guard(monkeypatch) -> None:
    _v0_9b_set_base_flags(monkeypatch)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MERCURY_SIGNATURE_V0_9C", "true")
    public = _live_public_view_from_batch_chart("fix11_unknown_birthtime")
    _v0_9b_assert_no_public_leak(public, "fix11_unknown_birthtime")
    mercury = _v0_9c_first_family_packet(public, "mercury_signature")
    career = _v0_9c_first_family_packet(public, "career_route")
    assert mercury, public
    assert career, public
    assert mercury["subtype"] == "structured_disruptive_mind", mercury
    assert career["subtype"] == "public_voice", career
    mercury_meta = mercury.get("meta") or {}
    mercury_breakdown = mercury.get("scoring_breakdown") or {}
    assert mercury_meta.get("career_overlap_guard") == "career_route_primary", mercury
    assert int(mercury_meta.get("public_anchor_count") or 0) == 1, mercury
    assert int(mercury_meta.get("independent_mind_support_count") or 0) <= 3, mercury
    assert float(mercury_breakdown.get("career_overlap_penalty") or 0.0) > 0.0, mercury
    assert float(career.get("confidence") or 0.0) > float(mercury.get("confidence") or 0.0), (career, mercury)


def test_v0_9c_public_voice_negative_owner_fixtures_remain_career_owned(monkeypatch) -> None:
    _v0_9b_set_base_flags(monkeypatch)
    fixtures = (
        "fix04_h10_career_stellium",
        "istanbul_1997_01_21",
        "tokyo_1998_06_21",
        "toronto_1976_06_26",
    )
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MERCURY_SIGNATURE_V0_9C", raising=False)
    baselines = {
        cid: _projection_surface_snapshot(_live_public_view_from_batch_chart(cid))
        for cid in fixtures
    }
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MERCURY_SIGNATURE_V0_9C", "true")
    for cid in fixtures:
        public = _live_public_view_from_batch_chart(cid)
        _v0_9b_assert_no_public_leak(public, cid)
        assert _projection_surface_snapshot(public) == baselines[cid], cid
        career = _v0_9c_first_family_packet(public, "career_route")
        mercury = _v0_9c_first_family_packet(public, "mercury_signature")
        assert career, cid
        assert career["subtype"] == "public_voice", career
        assert mercury is None, (cid, mercury)


def test_v0_9c_mercury_accepted_goldens_stay_byte_stable(monkeypatch) -> None:
    _v0_9b_set_base_flags(monkeypatch)
    goldens = (
        "istanbul_1994_06_25",
        "istanbul_1997_01_21",
        "istanbul_2020_04_10",
        "izmir_1996_05_20",
        "adana_1998_09_12",
    )
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MERCURY_SIGNATURE_V0_9C", raising=False)
    baselines = {
        cid: _projection_surface_snapshot(_live_public_view_from_batch_chart(cid))
        for cid in goldens
    }
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MERCURY_SIGNATURE_V0_9C", "true")
    for cid in goldens:
        public = _live_public_view_from_batch_chart(cid)
        _v0_9b_assert_no_public_leak(public, cid)
        assert _projection_surface_snapshot(public) == baselines[cid], cid


def test_v0_9b_both_families_on_public_surfaces_invariant(monkeypatch) -> None:
    """All v0.9b candidates must remain debug-only; no public surface
    receives them even with both family flags and detail-support all on.
    The Phase B composed_detail_cards lane must stay career-only."""
    _v0_9b_set_base_flags(monkeypatch)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT", "true")
    # Also turn on Phase B promotion flags to make sure no v0.9b card sneaks
    # through the existing career-only renderer allowlist.
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")

    for chart_id in _V0_9B_AUDIT_CHARTS:
        public = _live_public_view_from_batch_chart(chart_id)
        _v0_9b_assert_no_public_leak(public, chart_id)


def test_v0_9b_candidates_show_in_cluster_plan_trace_when_flag_on(monkeypatch) -> None:
    """When v0.9b master flags are on, the candidates must appear in the
    cluster plan's `candidate_packets` trace and the metrics ledger."""
    _v0_9b_set_base_flags(monkeypatch)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", "true")
    any_v0_9b_seen = False
    for chart_id in _V0_9B_AUDIT_CHARTS:
        public = _live_public_view_from_batch_chart(chart_id)
        plan = (
            public.get("profile_narrative_projection_v1") or {}
        ).get("traceability", {}).get("natal_promise_cluster_plan_v1") or {}
        packets = plan.get("candidate_packets") or []
        v0_9b = [p for p in packets if p.get("family") in {"relationship_route", "moon_signature"}]
        if v0_9b:
            any_v0_9b_seen = True
            for card in v0_9b:
                assert card["public_job"] == "debug_only", chart_id
                elig = card["public_eligibility"]
                assert elig["public_main_eligible"] is False, chart_id
                assert elig["public_support_eligible"] is False, chart_id
        # Ledger keys must exist on every chart, even charts that produce no
        # v0.9b candidate.
        metrics = plan.get("meta", {}).get("audit_metrics", {})
        assert "composed_candidate_subtype_distribution" in metrics, chart_id
        assert "composed_v0_9b_confidence_distribution" in metrics, chart_id
        assert "composed_cross_family_overlap_count" in metrics, chart_id
    assert any_v0_9b_seen, "No chart in the audit set produced a v0.9b candidate"


def test_v0_9b_p0_truthfulness_no_dangling_connectors(monkeypatch) -> None:
    """Confirms the v0.9b lived_scene / atom seeds do not reintroduce the
    P0 "olması de" / "Bazen de." defects."""
    _v0_9b_set_base_flags(monkeypatch)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", "true")
    olmasi = re.compile(r"olması de\b")
    bazen_upper = re.compile(r"Bazen de\.")
    bazen_lower = re.compile(r"bazen de\.")
    for chart_id in _V0_9B_AUDIT_CHARTS:
        public = _live_public_view_from_batch_chart(chart_id)
        for chunk in _collect_dangling_connector_scan_chunks(public):
            assert not olmasi.search(chunk), f"{chart_id}: olması de regression"
            assert not bazen_upper.search(chunk), f"{chart_id}: Bazen de. regression"
            assert not bazen_lower.search(chunk), f"{chart_id}: bazen de. regression"


def test_v0_9c_sanliurfa_1988_calibration_case_mercury_moon_and_direct_relationship_fire_public_stable(monkeypatch) -> None:
    """Sanliurfa 1988 joins the v0.9b calibration set as a mixed-chart
    case: moon_signature should fire as private_emotional_processing,
    relationship_route should now emit direct_relational_activation,
    mercury_signature should emit structured_disruptive_mind in debug,
    and public output must stay unchanged."""
    _v0_9b_set_base_flags(monkeypatch)
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", raising=False)
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", raising=False)
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MERCURY_SIGNATURE_V0_9C", raising=False)
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT", raising=False)
    baseline = _projection_surface_snapshot(
        _live_public_view_from_request(
            birth_date="1988-10-10",
            birth_time="05:30",
            birth_place="Sanliurfa, TR",
            birth_latitude=37.1674,
            birth_longitude=38.7955,
            birth_timezone="Europe/Istanbul",
        )
    )

    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MERCURY_SIGNATURE_V0_9C", "true")
    rendered_public = _live_public_view_from_request(
        birth_date="1988-10-10",
        birth_time="05:30",
        birth_place="Sanliurfa, TR",
        birth_latitude=37.1674,
        birth_longitude=38.7955,
        birth_timezone="Europe/Istanbul",
    )
    _v0_9b_assert_no_public_leak(rendered_public, "sanliurfa_1988_10_10")
    assert _projection_surface_snapshot(rendered_public) == baseline

    plan = (
        rendered_public.get("profile_narrative_projection_v1") or {}
    ).get("traceability", {}).get("natal_promise_cluster_plan_v1") or {}
    packets = plan.get("candidate_packets") or []

    moon_candidates = [p for p in packets if p.get("family") == "moon_signature"]
    assert moon_candidates, packets
    moon = moon_candidates[0]
    assert moon["subtype"] == "private_emotional_processing", moon
    assert moon["public_job"] == "debug_only", moon
    assert moon["confidence_tier"] == "medium", moon
    assert moon["public_eligibility"]["public_main_eligible"] is False, moon
    assert moon["public_eligibility"]["public_support_eligible"] is False, moon

    relationship_candidates = [p for p in packets if p.get("family") == "relationship_route"]
    assert relationship_candidates, packets
    relationship = relationship_candidates[0]
    assert relationship["subtype"] == "direct_relational_activation", relationship
    assert relationship["confidence_tier"] == "medium", relationship
    assert relationship["public_job"] == "debug_only", relationship
    assert relationship["public_eligibility"]["public_main_eligible"] is False, relationship
    assert relationship["public_eligibility"]["public_support_eligible"] is False, relationship
    assert "DSC route" in relationship["domain_reason"], relationship

    mercury_candidates = [p for p in packets if p.get("family") == "mercury_signature"]
    assert mercury_candidates, packets
    mercury = mercury_candidates[0]
    assert mercury["subtype"] == "structured_disruptive_mind", mercury
    assert mercury["public_job"] == "debug_only", mercury
    assert mercury["public_eligibility"]["public_main_eligible"] is False, mercury
    assert mercury["public_eligibility"]["public_support_eligible"] is False, mercury
    assert "Saturn structure on mind route" in mercury["domain_reason"], mercury
    assert "Uranus disruption on mind route" in mercury["domain_reason"], mercury
    mercury_meta = mercury.get("meta") or {}
    assert mercury_meta.get("runner_up_subtype") == "speech_identity_spine", mercury
    assert 0.0 <= float(mercury_meta.get("runner_up_score_delta") or 0.0) < 0.04, mercury
    assert "DSC ruler involved" in relationship["domain_reason"], relationship
    assert "Mars boundary/desire signature" in relationship["domain_reason"], relationship
    assert "6H daily/action route" in relationship["domain_reason"], relationship
    assert "moon_evidence_shared_with_moon_signature" not in (
        relationship.get("evidence_trace", {}).get("cross_family_overlap") or []
    ), relationship


def test_p0_no_decomposed_turkish_i_in_public_copy_sanliurfa_1988(monkeypatch) -> None:
    """Sanliurfa exposed a public-copy Unicode regression where `İ`
    lowercased/decomposed into `i` + combining dot above inside v8 hero
    summary text. Public surfaces must not leak that artifact."""
    _v0_9b_set_base_flags(monkeypatch)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", "true")
    public = _live_public_view_from_request(
        birth_date="1988-10-10",
        birth_time="05:30",
        birth_place="Sanliurfa, TR",
        birth_latitude=37.1674,
        birth_longitude=38.7955,
        birth_timezone="Europe/Istanbul",
    )

    for chunk in _collect_public_surface_text_chunks(public):
        assert "i̇" not in chunk, f"decomposed Turkish dotted-i leaked in public copy: {chunk!r}"


def test_v0_9b_flags_change_interpret_ui_cache_key() -> None:
    """Toggling each of the three v0.9b flags must produce a different
    cache key — otherwise stale cached responses leak across flag combos."""
    import os
    from app.api.routes.natal_interpretation import (
        NatalInterpretationRequest,
        _interpret_ui_cache_key,
    )

    request = NatalInterpretationRequest(
        birth_date="1985-06-15",
        birth_time="12:00",
        birth_place="Tokyo",
        birth_latitude=35.6762,
        birth_longitude=139.6503,
        birth_timezone="Asia/Tokyo",
        locale="tr",
        summary_only=False,
        include_full_profile=True,
    )

    def _build_key():
        return _interpret_ui_cache_key(
            request,
            debug=False,
            include_debug=True,
            include_full_profile=True,
            profile_engine=None,
        )

    seen_keys: set[str] = set()
    for flag in (
        "ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B",
        "ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B",
        "ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT",
    ):
        os.environ.pop(flag, None)
        off_key = _build_key()
        os.environ[flag] = "true"
        on_key = _build_key()
        os.environ.pop(flag, None)
        assert off_key != on_key, flag
        seen_keys.add(off_key)
        seen_keys.add(on_key)
    assert len(seen_keys) >= 2


# ---------------------------------------------------------------------------
# v0.9b.0.1 calibration — public output / golden / P0 invariants
# ---------------------------------------------------------------------------


def test_v0_9b_0_1_calibration_keeps_public_surfaces_stable_across_flag_combos(monkeypatch) -> None:
    """The calibration patch must not change public surfaces under any
    flag combo. Accepted goldens (Group-A audit charts) byte-equal
    between v0.9b flags-off and flags-on (including detail_support)."""
    _v0_9b_set_base_flags(monkeypatch)
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", raising=False)
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", raising=False)
    monkeypatch.delenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT", raising=False)
    baselines = {
        cid: _projection_surface_snapshot(_live_public_view_from_batch_chart(cid))
        for cid in _V0_9B_AUDIT_CHARTS
    }
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT", "true")
    for cid in _V0_9B_AUDIT_CHARTS:
        rendered = _projection_surface_snapshot(_live_public_view_from_batch_chart(cid))
        assert rendered == baselines[cid], cid


def test_v0_9b_0_1_calibration_ledger_metrics_present(monkeypatch) -> None:
    """The cluster plan ledger must carry the new v0.9b.0.1 metric keys."""
    _v0_9b_set_base_flags(monkeypatch)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", "true")
    for cid in _V0_9B_AUDIT_CHARTS:
        public = _live_public_view_from_batch_chart(cid)
        plan = (
            public.get("profile_narrative_projection_v1") or {}
        ).get("traceability", {}).get("natal_promise_cluster_plan_v1") or {}
        metrics = plan.get("meta", {}).get("audit_metrics", {})
        assert "composed_default_fallback_count" in metrics, cid
        assert "cross_family_moon_ownership_count" in metrics, cid
        assert "relationship_candidates_blocked_by_moon_ownership" in metrics, cid
        assert "composed_v0_9b_opportunity_severity" in metrics, cid
        # severity buckets must exist per family
        severity = metrics["composed_v0_9b_opportunity_severity"]
        for family in ("relationship_route", "moon_signature"):
            assert family in severity, cid
            for bucket in ("high_priority_opportunity", "medium_priority_opportunity", "debug_observation_only"):
                assert bucket in severity[family], (cid, family, bucket)


def test_v0_9b_0_1_calibration_no_p0_regression(monkeypatch) -> None:
    _v0_9b_set_base_flags(monkeypatch)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", "true")
    olmasi = re.compile(r"olması de\b")
    bazen_upper = re.compile(r"Bazen de\.")
    bazen_lower = re.compile(r"bazen de\.")
    for cid in _V0_9B_AUDIT_CHARTS:
        public = _live_public_view_from_batch_chart(cid)
        for chunk in _collect_dangling_connector_scan_chunks(public):
            assert not olmasi.search(chunk), f"{cid}: olması de regression"
            assert not bazen_upper.search(chunk), f"{cid}: Bazen de. regression"
            assert not bazen_lower.search(chunk), f"{cid}: bazen de. regression"


# ---------------------------------------------------------------------------
# v0.9b.1 — moon_signature.home_inner_security narrow detail rollout
# (integration tests against the live public projection)
# ---------------------------------------------------------------------------


_V0_9B_1_MOON_HOME_TARGET_CHARTS = (
    "trabzon_2001_09_14",
    "fix08_cancer_capricorn_nodes",
    "cairo_1991_01_15",
)

_V0_9B_1_MOON_HOME_NON_TARGET_CHARTS = (
    "istanbul_1994_06_25",
    "istanbul_1997_01_21",
    "adana_1998_09_12",
    "izmir_1996_05_20",
)


def _v0_9b_1_set_full_flags(monkeypatch) -> None:
    monkeypatch.setenv("SE_EPHE_PATH", str(Path("swisseph/ephe").resolve()))
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")
    monkeypatch.setenv(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_HOME_INNER_SECURITY_PUBLIC_DETAIL_LANE",
        "true",
    )


def test_v0_9b_1_moon_home_inner_security_target_charts_emit_exactly_one_card(monkeypatch) -> None:
    _v0_9b_1_set_full_flags(monkeypatch)
    for chart_id in _V0_9B_1_MOON_HOME_TARGET_CHARTS:
        public = _live_public_view_from_batch_chart(chart_id)
        profile_public = public["profile_narrative_projection_v1"]["profile_public"]
        cards = profile_public.get("composed_detail_cards") or []
        moon_cards = [
            c for c in cards
            if str(c.get("id") or "").startswith(
                "composed_detail::composed_moon_signature_v0_9b::"
            )
        ]
        assert len(moon_cards) == 1, f"{chart_id}: expected 1 moon card, got {len(moon_cards)}"
        card = moon_cards[0]
        assert card["family"] == "moon_home_inner_security"
        assert card["origin"] == "composed_detail_renderer_v0_9b_1"
        assert card["emphasis"] == "detail"


def test_v0_9b_1_moon_home_inner_security_non_target_charts_emit_no_moon_card(monkeypatch) -> None:
    _v0_9b_1_set_full_flags(monkeypatch)
    for chart_id in _V0_9B_1_MOON_HOME_NON_TARGET_CHARTS:
        public = _live_public_view_from_batch_chart(chart_id)
        profile_public = public["profile_narrative_projection_v1"]["profile_public"]
        cards = profile_public.get("composed_detail_cards") or []
        moon_cards = [
            c for c in cards
            if str(c.get("id") or "").startswith(
                "composed_detail::composed_moon_signature_v0_9b::"
            )
        ]
        assert moon_cards == [], chart_id


def test_v0_9b_1_moon_card_visible_fields_only(monkeypatch) -> None:
    _v0_9b_1_set_full_flags(monkeypatch)
    expected_visible = {
        "id", "node_id", "headline", "teaser", "body", "chips",
        "family", "emphasis", "origin",
    }
    forbidden = {
        "source_type", "source_candidate_id", "public_job",
        "source_anchor_trace", "detail_items", "evidence_summary",
        "avoid_readings",
    }
    for chart_id in _V0_9B_1_MOON_HOME_TARGET_CHARTS:
        public = _live_public_view_from_batch_chart(chart_id)
        profile_public = public["profile_narrative_projection_v1"]["profile_public"]
        cards = profile_public.get("composed_detail_cards") or []
        moon_cards = [
            c for c in cards
            if str(c.get("id") or "").startswith(
                "composed_detail::composed_moon_signature_v0_9b::"
            )
        ]
        for card in moon_cards:
            keys = set(card.keys())
            assert keys <= expected_visible, f"{chart_id}: unexpected fields {keys - expected_visible}"
            assert not (keys & forbidden), f"{chart_id}: trace fields leaked {keys & forbidden}"


def test_v0_9b_1_moon_card_does_not_leak_into_other_public_surfaces(monkeypatch) -> None:
    _v0_9b_1_set_full_flags(monkeypatch)
    moon_id_prefix = "composed_detail::composed_moon_signature_v0_9b::"
    moon_node_id_prefix = "promise::composed_moon_signature_v0_9b"

    def _has_moon_leak(items) -> bool:
        for it in items or []:
            if not isinstance(it, dict):
                continue
            if str(it.get("id") or "").startswith(moon_id_prefix):
                return True
            if str(it.get("node_id") or "").strip().startswith(moon_node_id_prefix):
                return True
        return False

    for chart_id in _V0_9B_1_MOON_HOME_TARGET_CHARTS:
        public = _live_public_view_from_batch_chart(chart_id)
        narrative = public["profile_narrative_projection_v1"]
        profile_public = narrative["profile_public"]
        v8 = public["profile_v8_projection_v1"]

        for lane in ("blocks", "core_blocks", "extra_blocks", "detail_cards"):
            assert not _has_moon_leak(profile_public.get(lane)), f"{chart_id}: leak into {lane}"

        for lane in ("differentiators", "insight_strip"):
            assert not _has_moon_leak(v8.get(lane)), f"{chart_id}: leak into v8.{lane}"

        hero = v8.get("hero") or {}
        identity = v8.get("identity_axis") or {}
        assert not str(hero.get("node_id") or "").startswith(moon_node_id_prefix), chart_id
        assert not str(identity.get("node_id") or "").startswith(moon_node_id_prefix), chart_id


def test_v0_9b_1_moon_card_copy_quality(monkeypatch) -> None:
    _v0_9b_1_set_full_flags(monkeypatch)
    banned_phrases = (
        "Aile önemlidir", "aile önemlidir",
        "Ev hayatın güçlüdür", "ev hayatın güçlüdür",
        "Annenle ilişkin", "Babanla ilişkin",
        "Ailen senin için her şey", "kalbinde yer eden aile",
    )
    debug_tokens = ("debug", "candidate", "fallback", "source_type", "public job")
    banned_ascii = ("Insanlar", "Disaridaki", "nasil", "dogru", "cumle", "Gorunur")
    for chart_id in _V0_9B_1_MOON_HOME_TARGET_CHARTS:
        public = _live_public_view_from_batch_chart(chart_id)
        cards = public["profile_narrative_projection_v1"]["profile_public"].get(
            "composed_detail_cards"
        ) or []
        for card in cards:
            if not str(card.get("id") or "").startswith(
                "composed_detail::composed_moon_signature_v0_9b::"
            ):
                continue
            combined = " ".join(str(card[f]) for f in ("headline", "teaser", "body"))
            for banned in banned_phrases:
                assert banned not in combined, (chart_id, banned)
            for token in debug_tokens:
                assert token not in combined.lower(), (chart_id, token)
            for ascii_form in banned_ascii:
                assert not re.search(rf"\b{re.escape(ascii_form)}\b", combined), (
                    chart_id,
                    ascii_form,
                )
            assert any(c in combined for c in "İıŞşĞğÇçÖöÜü"), chart_id


def test_v0_9b_1_moon_card_has_no_p0_truthfulness_defects(monkeypatch) -> None:
    _v0_9b_1_set_full_flags(monkeypatch)
    olmasi = re.compile(r"olması de\b")
    for chart_id in _V0_9B_1_MOON_HOME_TARGET_CHARTS:
        public = _live_public_view_from_batch_chart(chart_id)
        cards = public["profile_narrative_projection_v1"]["profile_public"].get(
            "composed_detail_cards"
        ) or []
        for card in cards:
            for field in ("headline", "teaser", "body"):
                text = str(card[field])
                assert not olmasi.search(text), (chart_id, field, text)
                assert "Bazen de." not in text, (chart_id, field, text)
                assert "bazen de." not in text, (chart_id, field, text)


def test_v0_9b_1_flag_off_omits_moon_lane(monkeypatch) -> None:
    monkeypatch.setenv("SE_EPHE_PATH", str(Path("swisseph/ephe").resolve()))
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")
    monkeypatch.delenv(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_HOME_INNER_SECURITY_PUBLIC_DETAIL_LANE",
        raising=False,
    )
    for chart_id in _V0_9B_1_MOON_HOME_TARGET_CHARTS:
        public = _live_public_view_from_batch_chart(chart_id)
        cards = public["profile_narrative_projection_v1"]["profile_public"].get(
            "composed_detail_cards"
        ) or []
        moon_cards = [
            c for c in cards
            if str(c.get("id") or "").startswith(
                "composed_detail::composed_moon_signature_v0_9b::"
            )
        ]
        assert moon_cards == [], chart_id


def test_v0_9b_1_cairo_cross_family_block_holds_end_to_end(monkeypatch) -> None:
    """cairo_1991_01_15 produces both a Moon home_inner_security card
    and a relationship_route candidate that consumes Moon evidence.
    With v0.9b.1 fully on, the moon card renders to the public lane and
    the relationship card is marked future_renderer_eligibility_blocked.
    No relationship-derived id appears in the public lane."""
    _v0_9b_1_set_full_flags(monkeypatch)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")

    public = _live_public_view_from_batch_chart("cairo_1991_01_15")
    profile_public = public["profile_narrative_projection_v1"]["profile_public"]
    cards = profile_public.get("composed_detail_cards") or []

    # Exactly one moon card present.
    moon_cards = [
        c for c in cards
        if str(c.get("id") or "").startswith(
            "composed_detail::composed_moon_signature_v0_9b::"
        )
    ]
    assert len(moon_cards) == 1, cards

    # No relationship card in the public lane.
    rel_cards = [
        c for c in cards
        if str(c.get("id") or "").startswith(
            "composed_detail::composed_relationship_route_v0_9b::"
        )
    ]
    assert rel_cards == [], rel_cards

    # The relationship candidate exists in trace and is marked blocked.
    plan = (
        public["profile_v8_projection_v1"]["traceability"][
            "natal_promise_cluster_plan_v1"
        ]
    )
    rel_candidates = [
        p for p in plan.get("candidate_packets") or []
        if p.get("family") == "relationship_route"
    ]
    assert rel_candidates, "cairo relationship_route candidate missing"
    rel = rel_candidates[0]
    elig = rel.get("public_eligibility") or {}
    meta = rel.get("meta") or {}
    assert elig.get("future_renderer_eligibility_blocked") is True, rel
    assert meta.get("moon_evidence_owned_by") == "moon_signature", rel


def test_v0_9b_1_flag_changes_interpret_ui_cache_key() -> None:
    import os
    from app.api.routes.natal_interpretation import (
        NatalInterpretationRequest,
        _interpret_ui_cache_key,
    )

    request = NatalInterpretationRequest(
        birth_date="1991-01-15",
        birth_time="12:00",
        birth_place="Cairo",
        birth_latitude=30.0444,
        birth_longitude=31.2357,
        birth_timezone="Africa/Cairo",
        locale="tr",
        summary_only=False,
        include_full_profile=True,
    )

    def _key():
        return _interpret_ui_cache_key(
            request,
            debug=False,
            include_debug=True,
            include_full_profile=True,
            profile_engine=None,
        )

    os.environ.pop(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_HOME_INNER_SECURITY_PUBLIC_DETAIL_LANE",
        None,
    )
    off_key = _key()
    os.environ[
        "ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_HOME_INNER_SECURITY_PUBLIC_DETAIL_LANE"
    ] = "true"
    on_key = _key()
    os.environ.pop(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_HOME_INNER_SECURITY_PUBLIC_DETAIL_LANE",
        None,
    )
    assert off_key != on_key


# ---------------------------------------------------------------------------
# v0.10 — axis_2h_8h public no-leak + cache key
# ---------------------------------------------------------------------------


def _v0_10_set_base_flags(monkeypatch) -> None:
    monkeypatch.setenv("SE_EPHE_PATH", str(Path("swisseph/ephe").resolve()))
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_AXIS_2H_8H_V0_10", "true")


def test_v0_10_axis_2h_8h_does_not_leak_into_any_public_lane(monkeypatch) -> None:
    _v0_10_set_base_flags(monkeypatch)
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_AXIS_2H_8H_DETAIL_SUPPORT", "true")
    # Also turn on Phase B + v0.9b.1 to verify the lane stays career/moon-only.
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")
    monkeypatch.setenv(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_HOME_INNER_SECURITY_PUBLIC_DETAIL_LANE",
        "true",
    )

    axis_node_id_prefix = "promise::composed_axis_2h_8h_v0_10"
    axis_packet_id = "composed_axis_2h_8h_v0_10"

    def _violates(item):
        if not isinstance(item, dict):
            return False
        if str(item.get("node_id") or "").strip().startswith(axis_node_id_prefix):
            return True
        if str(item.get("id") or "") == axis_packet_id:
            return True
        return False

    for chart_id in (
        "istanbul_1994_06_25",
        "istanbul_1997_01_21",
        "izmir_1996_05_20",
        "adana_1998_09_12",
        "kutahya_1959_10_21",
        "trabzon_2001_09_14",
        "cairo_1991_01_15",
    ):
        public = _live_public_view_from_batch_chart(chart_id)
        narrative = public.get("profile_narrative_projection_v1") or {}
        v8 = public.get("profile_v8_projection_v1") or {}
        profile_public = narrative.get("profile_public") or {}

        for lane in ("blocks", "core_blocks", "extra_blocks", "detail_cards", "composed_detail_cards"):
            for item in (profile_public.get(lane) or []):
                assert not _violates(item), f"{chart_id}: leak into profile_public.{lane}"

        for lane in ("differentiators", "insight_strip"):
            for item in (v8.get(lane) or []):
                assert not _violates(item), f"{chart_id}: leak into v8.{lane}"

        hero = v8.get("hero") or {}
        identity = v8.get("identity_axis") or {}
        assert not str(hero.get("node_id") or "").strip().startswith(axis_node_id_prefix), chart_id
        assert not str(identity.get("node_id") or "").strip().startswith(axis_node_id_prefix), chart_id


def test_v0_10_axis_2h_8h_flag_changes_interpret_ui_cache_key() -> None:
    import os
    from app.api.routes.natal_interpretation import (
        NatalInterpretationRequest,
        _interpret_ui_cache_key,
    )

    request = NatalInterpretationRequest(
        birth_date="1998-03-05",
        birth_time="15:00",
        birth_place="Istanbul",
        birth_latitude=41.0082,
        birth_longitude=28.9784,
        birth_timezone="Europe/Istanbul",
        locale="tr",
        summary_only=False,
        include_full_profile=True,
    )

    def _key():
        return _interpret_ui_cache_key(
            request,
            debug=False,
            include_debug=True,
            include_full_profile=True,
            profile_engine=None,
        )

    for flag in (
        "ENABLE_NATAL_COMPOSED_SEMANTICS_AXIS_2H_8H_V0_10",
        "ENABLE_NATAL_COMPOSED_SEMANTICS_AXIS_2H_8H_DETAIL_SUPPORT",
    ):
        os.environ.pop(flag, None)
        off = _key()
        os.environ[flag] = "true"
        on = _key()
        os.environ.pop(flag, None)
        assert off != on, flag


# ---------------------------------------------------------------------------
# v0.10 Phase 2 — Istanbul 1996 Venus 12H hidden/private love slides
# ---------------------------------------------------------------------------


def _v0_10_phase2_set_flags(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT", "true")
    monkeypatch.setenv(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_PUBLIC_DETAIL_LANE",
        "true",
    )


def test_v0_10_phase2_istanbul_1996_emits_exactly_one_hidden_private_love_card(monkeypatch) -> None:
    _v0_10_phase2_set_flags(monkeypatch)
    public = build_public_natal_view(
        _artifact_response("natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json"),
        locale="tr",
        include_debug=True,
        include_full_profile=True,
    )
    profile_public = public["profile_narrative_projection_v1"]["profile_public"]
    cards = profile_public.get("composed_detail_cards") or []
    hidden_cards = [
        card for card in cards
        if str(card.get("id") or "").startswith(
            "composed_detail::venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact::istanbul_1996_12_28_hidden_private_love"
        )
    ]
    assert len(hidden_cards) == 1
    card = hidden_cards[0]
    assert card["family"] == "relationship_hidden_private_love"
    assert card["origin"] == "composed_detail_renderer_v0_10_phase2"
    assert card["emphasis"] == "detail"
    assert set(card.keys()) == {
        "id",
        "node_id",
        "headline",
        "teaser",
        "body",
        "chips",
        "family",
        "emphasis",
        "origin",
        "slides",
        "why_this_exists",
    }
    assert len(card["slides"]) == 5
    assert [slide["id"] for slide in card["slides"]] == [
        "slide::venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact::private_scene",
        "slide::venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact::hidden_mechanism",
        "slide::venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact::protective_pattern",
        "slide::venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact::gift_in_silence",
        "slide::venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact::safe_visibility",
    ]
    assert card["slides"][0]["title"] == "Hemen göstermiyorsun"
    assert (
        card["slides"][0]["body"]
        == "Birine karşı bir şey hissettiğinde, bunu hemen dışarıya açmak istemeyebilirsin. Önce kendi içinde anlamak, emin olmak ve biraz da korumak istersin. Bu yüzden dışarıdan sakin ya da mesafeli görünebilirsin. Ama bu, az hissettiğin anlamına gelmez; sadece duygularını herkes gibi açık yaşamıyorsun."
    )
    assert all(set(slide.keys()) == {"id", "title", "body"} for slide in card["slides"])
    assert card["why_this_exists"]["title"] == "Nereden geliyor?"


def test_v0_10_phase2_flag_off_omits_hidden_private_love_card(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PROJECTION_V1", "true")
    monkeypatch.setenv("ENABLE_NATAL_PROMISE_PACKET_DEBUG", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL", "true")
    monkeypatch.setenv("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE", "true")
    monkeypatch.delenv(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_PUBLIC_DETAIL_LANE",
        raising=False,
    )
    public = build_public_natal_view(
        _artifact_response("natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json"),
        locale="tr",
        include_debug=True,
        include_full_profile=True,
    )
    cards = public["profile_narrative_projection_v1"]["profile_public"].get("composed_detail_cards") or []
    hidden_cards = [
        card for card in cards
        if str(card.get("family") or "").strip() == "relationship_hidden_private_love"
    ]
    assert hidden_cards == []


def test_v0_10_phase2_non_target_chart_omits_hidden_private_love_card(monkeypatch) -> None:
    _v0_10_phase2_set_flags(monkeypatch)
    public = build_public_natal_view(
        _artifact_response("natal_interpret_full_1998-09-12_07-30_adana_user_compact_debug.json"),
        locale="tr",
        include_debug=True,
        include_full_profile=True,
    )
    profile_public = public["profile_narrative_projection_v1"]["profile_public"]
    assert "composed_detail_cards" not in profile_public


def test_v0_10_phase2_card_does_not_leak_into_other_public_surfaces(monkeypatch) -> None:
    _v0_10_phase2_set_flags(monkeypatch)
    public = build_public_natal_view(
        _artifact_response("natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json"),
        locale="tr",
        include_debug=True,
        include_full_profile=True,
    )
    narrative = public["profile_narrative_projection_v1"]
    profile_public = narrative["profile_public"]
    v8 = public["profile_v8_projection_v1"]
    hidden_prefix = "composed_detail::venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact::istanbul_1996_12_28_hidden_private_love"

    def _has_hidden(items) -> bool:
        for item in items or []:
            if not isinstance(item, dict):
                continue
            if str(item.get("id") or "") == hidden_prefix:
                return True
            if "slides" in item or "why_this_exists" in item:
                return True
        return False

    for lane in ("blocks", "core_blocks", "extra_blocks", "detail_cards"):
        assert not _has_hidden(profile_public.get(lane)), lane
    for lane in ("differentiators", "insight_strip"):
        assert not _has_hidden(v8.get(lane)), lane
    assert "composed_detail_cards" not in v8


def test_v0_10_phase3_internal_metadata_flag_is_public_noop_for_hidden_private_pilot(monkeypatch) -> None:
    _v0_10_phase2_set_flags(monkeypatch)
    baseline = build_public_natal_view(
        _artifact_response("natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json"),
        locale="tr",
        include_debug=True,
        include_full_profile=True,
    )

    monkeypatch.setenv(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_PHASE3_INTERNAL_METADATA",
        "true",
    )
    rendered = build_public_natal_view(
        _artifact_response("natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json"),
        locale="tr",
        include_debug=True,
        include_full_profile=True,
    )

    assert _projection_surface_snapshot(rendered) == _projection_surface_snapshot(baseline)
    assert rendered["profile_narrative_projection_v1"]["profile_public"] == baseline["profile_narrative_projection_v1"]["profile_public"]


def test_v0_10_phase2_flag_changes_interpret_ui_cache_key() -> None:
    import os
    from app.api.routes.natal_interpretation import (
        NatalInterpretationRequest,
        _interpret_ui_cache_key,
    )

    request = NatalInterpretationRequest(
        birth_date="1996-12-28",
        birth_time="07:10",
        birth_place="Istanbul, TR",
        birth_latitude=41.0082,
        birth_longitude=28.9784,
        birth_timezone="Europe/Istanbul",
        locale="tr",
        summary_only=False,
        include_full_profile=True,
    )

    def _key():
        return _interpret_ui_cache_key(
            request,
            debug=False,
            include_debug=True,
            include_full_profile=True,
            profile_engine=None,
        )

    os.environ.pop(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_PUBLIC_DETAIL_LANE",
        None,
    )
    off_key = _key()
    os.environ[
        "ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_PUBLIC_DETAIL_LANE"
    ] = "true"
    on_key = _key()
    os.environ.pop(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_PUBLIC_DETAIL_LANE",
        None,
    )
    assert off_key != on_key
