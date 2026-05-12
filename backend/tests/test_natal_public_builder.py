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

    hidden_love = block_by_node_id["promise::venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact"]
    assert hidden_love["headline"] == "Bazı duygular sende önce içeride büyüyor olabilir."
    assert "sevgiyi bazen önce içeride büyüten" in hidden_love["body"].lower()
    assert "üretim ve görünürlük" not in hidden_love["body"].lower()

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
    assert narrative_1996_blocks["promise::venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact"]["headline"] == (
        "Bazı duygular sende önce içeride büyüyor olabilir."
    )
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
