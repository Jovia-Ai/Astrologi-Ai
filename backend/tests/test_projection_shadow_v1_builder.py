import re

from app.meaning.projection_shadow_v1_builder import (
    build_profile_narrative_projection_v1,
    build_profile_v8_projection_v1,
    clear_last_projection_selection_debug,
    get_last_projection_selection_debug,
)
from app.natal.natal_promise_cluster_plan import build_natal_promise_cluster_plan_v1


def _packet(
    *,
    packet_id: str,
    domain: str,
    promise_type: str,
    strength: float,
    headline: str,
    direct: str,
    scene: str,
    gift: str,
    shadow: str = "",
    tension: str = "",
    growth: str = "",
    anchors: list[str] | None = None,
    evidence_ids: list[str] | None = None,
) -> dict:
    return {
        "id": packet_id,
        "domain": domain,
        "promise_type": promise_type,
        "strength": strength,
        "technical_anchors": anchors or [headline.split(".")[0]],
        "source_evidence_ids": evidence_ids or [packet_id],
        "direct_meaning": direct,
        "lived_scene": scene,
        "gift": gift,
        "shadow_or_friction": shadow,
        "inner_tension": tension,
        "growth_direction": growth,
        "voice_seeds": [headline],
        "avoid_phrases": [],
        "source_category_ids": [packet_id],
        "source_thread_ids": [],
        "source_section_ids": [packet_id],
        "projection_hints": {"priority": strength, "surfaces": ["profile_top", "profile_deep"]},
    }


def _cluster_plan_from_packets(packets: list[dict]) -> dict:
    return build_natal_promise_cluster_plan_v1(packets)


def _sample_graph() -> dict:
    return {
        "version": "meaning_graph_v1_1",
        "nodes": [
            {
                "node_id": "node_hero",
                "node_type": "narrative",
                "title": "Kimlik Çizgin",
                "summary": "Dışarıya net bir etki veriyorsun ama içeride ritmi önce tartıyorsun.",
                "layers": [{"layer": "effect", "weight": 0.6}, {"layer": "shadow", "weight": 0.4}],
                "primary_layer": "effect",
                "domain": "identity",
                "source_family": "core_story_ui",
                "source_path": "public.core_story_ui.text",
                "evidence_ids": ["evd_text", "evd_chips"],
                "projection_hints": {"surfaces": ["profile_top", "profile_deep"], "priority": 0.93, "short_text": None},
                "temporal_scope": None,
                "dedupe_fingerprint": "fp_1",
            },
            {
                "node_id": "node_extra",
                "node_type": "guidance",
                "title": "Gelişim İpucu",
                "summary": "Zorlandığında ritmi sadeleştirmen odak ve güveni güçlendirir.",
                "layers": [{"layer": "potential", "weight": 0.55}, {"layer": "shadow", "weight": 0.45}],
                "primary_layer": "potential",
                "domain": "mind",
                "source_family": "supporting_threads",
                "source_path": "public.supporting_threads[0].paragraph",
                "evidence_ids": ["evd_text_2"],
                "projection_hints": {"surfaces": ["profile_deep", "explainability"], "priority": 0.74, "short_text": None},
                "temporal_scope": None,
                "dedupe_fingerprint": "fp_2",
            },
        ],
        "evidence": [
            {
                "evidence_id": "evd_text",
                "node_id": "node_hero",
                "kind": "text",
                "source_family": "core_story_ui",
                "source_path": "public.core_story_ui.text",
                "weight": 0.9,
                "text_payload": "Kimlik hattın görünür ve etkili.",
                "structured_payload": None,
            },
            {
                "evidence_id": "evd_chips",
                "node_id": "node_hero",
                "kind": "signal",
                "source_family": "supporting_threads",
                "source_path": "public.supporting_threads[0].chips",
                "weight": 0.5,
                "text_payload": None,
                "structured_payload": {"chips": ["kimlik", "etki"]},
            },
            {
                "evidence_id": "evd_text_2",
                "node_id": "node_extra",
                "kind": "text",
                "source_family": "supporting_threads",
                "source_path": "public.supporting_threads[0].paragraph",
                "weight": 0.7,
                "text_payload": "Sade ritim karar kalitesini artırır.",
                "structured_payload": None,
            },
        ],
    }


def _diverse_graph() -> dict:
    nodes = [
        {
            "node_id": "collision_prefix_domain_identity_0001",
            "node_type": "narrative",
            "title": "Kimlik Odağı",
            "summary": "Dışarıda net bir duruşun var.",
            "layers": [{"layer": "recognition", "weight": 0.7}, {"layer": "effect", "weight": 0.3}],
            "primary_layer": "recognition",
            "domain": "identity",
            "source_family": "core_story_ui",
            "source_path": "public.core_story_ui.text",
            "evidence_ids": ["evd_i"],
            "projection_hints": {"surfaces": ["profile_top"], "priority": 0.98},
        },
        {
            "node_id": "collision_prefix_domain_mind_0002",
            "node_type": "signal",
            "title": "Zihin Akışı",
            "summary": "Karar anında önce ritmi sadeleştiriyorsun.",
            "layers": [{"layer": "mechanism", "weight": 0.8}],
            "primary_layer": "mechanism",
            "domain": "mind",
            "source_family": "supporting_threads",
            "source_path": "public.supporting_threads[0].paragraph",
            "evidence_ids": ["evd_m"],
            "projection_hints": {"surfaces": ["profile_top"], "priority": 0.94},
        },
        {
            "node_id": "collision_prefix_domain_career_0003",
            "node_type": "guidance",
            "title": "Kariyer Ritmi",
            "summary": "Görünürlük sende kalite eşiğiyle açılıyor.",
            "layers": [{"layer": "effect", "weight": 0.6}, {"layer": "shadow", "weight": 0.4}],
            "primary_layer": "effect",
            "domain": "career",
            "source_family": "core_story_ui",
            "source_path": "public.core_story_ui.text",
            "evidence_ids": ["evd_c"],
            "projection_hints": {"surfaces": ["profile_top"], "priority": 0.91},
        },
        {
            "node_id": "collision_prefix_domain_relationship_0004",
            "node_type": "narrative",
            "title": "Yakınlık Hattı",
            "summary": "Güven eşiği geçilince bağın hızla derinleşiyor.",
            "layers": [{"layer": "potential", "weight": 0.7}, {"layer": "shadow", "weight": 0.3}],
            "primary_layer": "potential",
            "domain": "relationships",
            "source_family": "supporting_threads",
            "source_path": "public.supporting_threads[1].paragraph",
            "evidence_ids": ["evd_r"],
            "projection_hints": {"surfaces": ["profile_deep"], "priority": 0.89},
        },
    ]
    evidence = [
        {
            "evidence_id": "evd_i",
            "node_id": "collision_prefix_domain_identity_0001",
            "kind": "text",
            "source_family": "core_story_ui",
            "source_path": "public.core_story_ui.text",
            "weight": 0.8,
            "text_payload": "İlk izlenimde omurgan güçlü okunuyor.",
            "structured_payload": None,
        },
        {
            "evidence_id": "evd_m",
            "node_id": "collision_prefix_domain_mind_0002",
            "kind": "text",
            "source_family": "supporting_threads",
            "source_path": "public.supporting_threads[0].paragraph",
            "weight": 0.7,
            "text_payload": "Cümleyi netleştirince zihinsel hızın artıyor.",
            "structured_payload": None,
        },
        {
            "evidence_id": "evd_c",
            "node_id": "collision_prefix_domain_career_0003",
            "kind": "text",
            "source_family": "core_story_ui",
            "source_path": "public.core_story_ui.text",
            "weight": 0.7,
            "text_payload": "Hazır hissetmeden görünür olmuyorsun.",
            "structured_payload": None,
        },
        {
            "evidence_id": "evd_r",
            "node_id": "collision_prefix_domain_relationship_0004",
            "kind": "text",
            "source_family": "supporting_threads",
            "source_path": "public.supporting_threads[1].paragraph",
            "weight": 0.7,
            "text_payload": "Yakınlıkta güven, hızdan daha belirleyici.",
            "structured_payload": None,
        },
    ]
    return {
        "version": "meaning_graph_v1_1",
        "nodes": nodes,
        "evidence": evidence,
    }


def _fingerprint_collision_graph() -> dict:
    nodes = [
        {
            "node_id": "fp_dup_a",
            "node_type": "narrative",
            "title": "Kimlik Odağı",
            "summary": "Dışarıdan net görünürsün ama içeride daha yoğun bir değerlendirme çalışır.",
            "layers": [{"layer": "effect", "weight": 0.7}, {"layer": "shadow", "weight": 0.3}],
            "primary_layer": "effect",
            "domain": "identity",
            "source_family": "core_story_ui",
            "source_path": "public.core_story_ui.text",
            "evidence_ids": ["evd_dup_a"],
            "projection_hints": {"surfaces": ["profile_top", "profile_deep"], "priority": 0.97},
            "dedupe_fingerprint": "fp_collision",
        },
        {
            "node_id": "fp_dup_b",
            "node_type": "signal",
            "title": "İkinci Varyant",
            "summary": "Dışarıdan net görünürsün ama içeride daha yoğun bir değerlendirme çalışır.",
            "layers": [{"layer": "effect", "weight": 0.65}, {"layer": "shadow", "weight": 0.35}],
            "primary_layer": "effect",
            "domain": "mind",
            "source_family": "supporting_threads",
            "source_path": "public.supporting_threads[0].paragraph",
            "evidence_ids": ["evd_dup_b"],
            "projection_hints": {"surfaces": ["profile_top", "profile_deep"], "priority": 0.96},
            "dedupe_fingerprint": "fp_collision",
        },
        {
            "node_id": "fp_unique_1",
            "node_type": "narrative",
            "title": "Kariyer Çizgisi",
            "summary": "Kariyerde hız ve kalite dengesini kurduğunda görünürlüğün belirginleşir.",
            "layers": [{"layer": "potential", "weight": 0.6}, {"layer": "mechanism", "weight": 0.4}],
            "primary_layer": "potential",
            "domain": "career",
            "source_family": "core_story_ui",
            "source_path": "public.core_story_ui.text",
            "evidence_ids": ["evd_unique_1"],
            "projection_hints": {"surfaces": ["profile_deep"], "priority": 0.9},
            "dedupe_fingerprint": "fp_unique_1",
        },
        {
            "node_id": "fp_unique_2",
            "node_type": "guidance",
            "title": "İlişki Ritmi",
            "summary": "İlişkilerde güven eşiği geçildiğinde duygusal yakınlık daha hızlı açılır.",
            "layers": [{"layer": "mechanism", "weight": 0.75}, {"layer": "effect", "weight": 0.25}],
            "primary_layer": "mechanism",
            "domain": "relationships",
            "source_family": "supporting_threads",
            "source_path": "public.supporting_threads[1].paragraph",
            "evidence_ids": ["evd_unique_2"],
            "projection_hints": {"surfaces": ["profile_deep"], "priority": 0.88},
            "dedupe_fingerprint": "fp_unique_2",
        },
        {
            "node_id": "fp_unique_3",
            "node_type": "signal",
            "title": "Duygusal Denge",
            "summary": "Duygusal alanda ritmi sakinleştirdiğinde karar netliği yükseliyor.",
            "layers": [{"layer": "shadow", "weight": 0.58}, {"layer": "potential", "weight": 0.42}],
            "primary_layer": "shadow",
            "domain": "emotional",
            "source_family": "supporting_threads",
            "source_path": "public.supporting_threads[2].paragraph",
            "evidence_ids": ["evd_unique_3"],
            "projection_hints": {"surfaces": ["profile_deep"], "priority": 0.86},
            "dedupe_fingerprint": "fp_unique_3",
        },
    ]
    evidence = [
        {
            "evidence_id": "evd_dup_a",
            "node_id": "fp_dup_a",
            "kind": "text",
            "source_family": "core_story_ui",
            "source_path": "public.core_story_ui.text",
            "weight": 0.8,
            "text_payload": "Kimlik hattın dışarıda netlik üretiyor.",
            "structured_payload": None,
        },
        {
            "evidence_id": "evd_dup_b",
            "node_id": "fp_dup_b",
            "kind": "text",
            "source_family": "supporting_threads",
            "source_path": "public.supporting_threads[0].paragraph",
            "weight": 0.75,
            "text_payload": "Aynı temanın ikinci varyantı.",
            "structured_payload": None,
        },
        {
            "evidence_id": "evd_unique_1",
            "node_id": "fp_unique_1",
            "kind": "text",
            "source_family": "core_story_ui",
            "source_path": "public.core_story_ui.text",
            "weight": 0.7,
            "text_payload": "Kariyerde kalite ritmi etkini artırır.",
            "structured_payload": None,
        },
        {
            "evidence_id": "evd_unique_2",
            "node_id": "fp_unique_2",
            "kind": "text",
            "source_family": "supporting_threads",
            "source_path": "public.supporting_threads[1].paragraph",
            "weight": 0.7,
            "text_payload": "İlişkide güven sonrası hız açılır.",
            "structured_payload": None,
        },
        {
            "evidence_id": "evd_unique_3",
            "node_id": "fp_unique_3",
            "kind": "text",
            "source_family": "supporting_threads",
            "source_path": "public.supporting_threads[2].paragraph",
            "weight": 0.7,
            "text_payload": "Duygusal ritimde sadeleşme netlik sağlar.",
            "structured_payload": None,
        },
    ]
    return {"version": "meaning_graph_v1_1", "nodes": nodes, "evidence": evidence}


def _soft_duplicate_underfilled_graph() -> dict:
    nodes = [
        {
            "node_id": "soft_dup_a",
            "node_type": "narrative",
            "title": "Ritim A",
            "summary": "Günlük hayatta net bir ritim kuruyor ve kararlarını tartarak ilerliyorsun.",
            "layers": [{"layer": "effect", "weight": 0.62}, {"layer": "shadow", "weight": 0.38}],
            "primary_layer": "effect",
            "domain": "identity",
            "source_family": "core_story_ui",
            "source_path": "public.core_story_ui.text",
            "evidence_ids": ["evd_soft_a"],
            "projection_hints": {"surfaces": ["profile_top", "profile_deep"], "priority": 0.95},
            "dedupe_fingerprint": "soft_fp_a",
        },
        {
            "node_id": "soft_dup_b",
            "node_type": "narrative",
            "title": "Ritim B",
            "summary": "Günlük hayatta net bir ritim kuruyor ve kararlarını tartarak hareket ediyorsun.",
            "layers": [{"layer": "effect", "weight": 0.6}, {"layer": "shadow", "weight": 0.4}],
            "primary_layer": "effect",
            "domain": "mind",
            "source_family": "supporting_threads",
            "source_path": "public.supporting_threads[0].paragraph",
            "evidence_ids": ["evd_soft_b"],
            "projection_hints": {"surfaces": ["profile_top", "profile_deep"], "priority": 0.94},
            "dedupe_fingerprint": "soft_fp_b",
        },
        {
            "node_id": "soft_unique_1",
            "node_type": "guidance",
            "title": "Kariyer Hat",
            "summary": "Kariyerde net bir odak kurduğunda görünür etki daha hızlı açılır.",
            "layers": [{"layer": "potential", "weight": 0.7}, {"layer": "mechanism", "weight": 0.3}],
            "primary_layer": "potential",
            "domain": "career",
            "source_family": "core_story_ui",
            "source_path": "public.core_story_ui.text",
            "evidence_ids": ["evd_soft_c"],
            "projection_hints": {"surfaces": ["profile_top", "profile_deep"], "priority": 0.9},
            "dedupe_fingerprint": "soft_fp_c",
        },
        {
            "node_id": "soft_unique_2",
            "node_type": "signal",
            "title": "İlişki Hat",
            "summary": "İlişkilerde güven kurulduğunda iletişim tonu daha esnek ve açık olur.",
            "layers": [{"layer": "mechanism", "weight": 0.72}, {"layer": "effect", "weight": 0.28}],
            "primary_layer": "mechanism",
            "domain": "relationships",
            "source_family": "supporting_threads",
            "source_path": "public.supporting_threads[1].paragraph",
            "evidence_ids": ["evd_soft_d"],
            "projection_hints": {"surfaces": ["profile_top", "profile_deep"], "priority": 0.89},
            "dedupe_fingerprint": "soft_fp_d",
        },
    ]
    evidence = [
        {
            "evidence_id": "evd_soft_a",
            "node_id": "soft_dup_a",
            "kind": "text",
            "source_family": "core_story_ui",
            "source_path": "public.core_story_ui.text",
            "weight": 0.7,
            "text_payload": "Ritim A desteği",
            "structured_payload": None,
        },
        {
            "evidence_id": "evd_soft_b",
            "node_id": "soft_dup_b",
            "kind": "text",
            "source_family": "supporting_threads",
            "source_path": "public.supporting_threads[0].paragraph",
            "weight": 0.7,
            "text_payload": "Ritim B desteği",
            "structured_payload": None,
        },
        {
            "evidence_id": "evd_soft_c",
            "node_id": "soft_unique_1",
            "kind": "text",
            "source_family": "core_story_ui",
            "source_path": "public.core_story_ui.text",
            "weight": 0.7,
            "text_payload": "Kariyer hat desteği",
            "structured_payload": None,
        },
        {
            "evidence_id": "evd_soft_d",
            "node_id": "soft_unique_2",
            "kind": "text",
            "source_family": "supporting_threads",
            "source_path": "public.supporting_threads[1].paragraph",
            "weight": 0.7,
            "text_payload": "İlişki hat desteği",
            "structured_payload": None,
        },
    ]
    return {"version": "meaning_graph_v1_1", "nodes": nodes, "evidence": evidence}


def _set_aware_selection_graph() -> dict:
    nodes = [
        {
            "node_id": "set_a",
            "node_type": "narrative",
            "title": "Kimlik Gölgesi A",
            "summary": "Dışarıdan güçlü bir izlenim veriyorsun ama içeride kontrolü bırakmak istemiyorsun.",
            "layers": [{"layer": "shadow", "weight": 0.78}, {"layer": "effect", "weight": 0.22}],
            "primary_layer": "shadow",
            "domain": "identity",
            "source_family": "core_story_ui",
            "source_path": "public.core_story_ui.text",
            "evidence_ids": ["evd_set_a"],
            "projection_hints": {"surfaces": ["profile_top", "home"], "priority": 0.98},
            "dedupe_fingerprint": "set_fp_dup",
        },
        {
            "node_id": "set_b",
            "node_type": "signal",
            "title": "Kimlik Gölgesi B",
            "summary": "Dışarıdan güçlü bir izlenim veriyorsun ama içeride kontrolü bırakmamak için geriliyorsun.",
            "layers": [{"layer": "shadow", "weight": 0.76}, {"layer": "effect", "weight": 0.24}],
            "primary_layer": "shadow",
            "domain": "identity",
            "source_family": "supporting_threads",
            "source_path": "public.supporting_threads[0].paragraph",
            "evidence_ids": ["evd_set_b"],
            "projection_hints": {"surfaces": ["profile_top", "home"], "priority": 0.97},
            "dedupe_fingerprint": "set_fp_dup",
        },
        {
            "node_id": "set_c",
            "node_type": "signal",
            "title": "Kimlik Gölgesi C",
            "summary": "Dışarıdan güçlü bir izlenim veriyorsun ama içeride kontrolü kaybetmemek için sürekli tetikte kalıyorsun.",
            "layers": [{"layer": "shadow", "weight": 0.74}, {"layer": "effect", "weight": 0.26}],
            "primary_layer": "shadow",
            "domain": "identity",
            "source_family": "supporting_threads",
            "source_path": "public.supporting_threads[1].paragraph",
            "evidence_ids": ["evd_set_c"],
            "projection_hints": {"surfaces": ["profile_top", "home"], "priority": 0.96},
            "dedupe_fingerprint": "set_fp_c",
        },
        {
            "node_id": "set_d",
            "node_type": "guidance",
            "title": "Zihin İşleyişi",
            "summary": "Zihinsel ritminde sadeleşme kurduğunda kararların daha net ve hızlı akıyor.",
            "layers": [{"layer": "mechanism", "weight": 0.71}, {"layer": "potential", "weight": 0.29}],
            "primary_layer": "mechanism",
            "domain": "mind",
            "source_family": "core_story_ui",
            "source_path": "public.core_story_ui.text",
            "evidence_ids": ["evd_set_d"],
            "projection_hints": {"surfaces": ["profile_top", "home"], "priority": 0.9},
            "dedupe_fingerprint": "set_fp_d",
        },
        {
            "node_id": "set_e",
            "node_type": "narrative",
            "title": "İlişki Etkisi",
            "summary": "İlişkilerde güven netleştiğinde ifade tonun daha açık ve yumuşak hale geliyor.",
            "layers": [{"layer": "effect", "weight": 0.67}, {"layer": "potential", "weight": 0.33}],
            "primary_layer": "effect",
            "domain": "relationships",
            "source_family": "supporting_threads",
            "source_path": "public.supporting_threads[2].paragraph",
            "evidence_ids": ["evd_set_e"],
            "projection_hints": {"surfaces": ["profile_top", "home"], "priority": 0.89},
            "dedupe_fingerprint": "set_fp_e",
        },
        {
            "node_id": "set_f",
            "node_type": "guidance",
            "title": "Kariyer Potansiyeli",
            "summary": "Kariyerde odak hattını koruduğunda görünür sonuçlar daha düzenli şekilde büyüyor.",
            "layers": [{"layer": "potential", "weight": 0.69}, {"layer": "effect", "weight": 0.31}],
            "primary_layer": "potential",
            "domain": "career",
            "source_family": "core_story_ui",
            "source_path": "public.core_story_ui.text",
            "evidence_ids": ["evd_set_f"],
            "projection_hints": {"surfaces": ["profile_top", "home"], "priority": 0.88},
            "dedupe_fingerprint": "set_fp_f",
        },
    ]
    evidence = [
        {
            "evidence_id": "evd_set_a",
            "node_id": "set_a",
            "kind": "text",
            "source_family": "core_story_ui",
            "source_path": "public.core_story_ui.text",
            "weight": 0.8,
            "text_payload": "Kimlik hattında yüksek kontrol baskısı.",
            "structured_payload": None,
        },
        {
            "evidence_id": "evd_set_b",
            "node_id": "set_b",
            "kind": "text",
            "source_family": "supporting_threads",
            "source_path": "public.supporting_threads[0].paragraph",
            "weight": 0.75,
            "text_payload": "Kontrol baskısının ikinci varyantı.",
            "structured_payload": None,
        },
        {
            "evidence_id": "evd_set_c",
            "node_id": "set_c",
            "kind": "text",
            "source_family": "supporting_threads",
            "source_path": "public.supporting_threads[1].paragraph",
            "weight": 0.72,
            "text_payload": "Kontrol baskısının üçüncü varyantı.",
            "structured_payload": None,
        },
        {
            "evidence_id": "evd_set_d",
            "node_id": "set_d",
            "kind": "text",
            "source_family": "core_story_ui",
            "source_path": "public.core_story_ui.text",
            "weight": 0.7,
            "text_payload": "Sade zihinsel ritim kararları hızlandırır.",
            "structured_payload": None,
        },
        {
            "evidence_id": "evd_set_e",
            "node_id": "set_e",
            "kind": "text",
            "source_family": "supporting_threads",
            "source_path": "public.supporting_threads[2].paragraph",
            "weight": 0.69,
            "text_payload": "İlişkilerde güven etkisi belirgin.",
            "structured_payload": None,
        },
        {
            "evidence_id": "evd_set_f",
            "node_id": "set_f",
            "kind": "text",
            "source_family": "core_story_ui",
            "source_path": "public.core_story_ui.text",
            "weight": 0.67,
            "text_payload": "Kariyerde odak potansiyeli büyütür.",
            "structured_payload": None,
        },
    ]
    return {"version": "meaning_graph_v1_1", "nodes": nodes, "evidence": evidence}


def _v8_unique_slots_graph() -> dict:
    base = _set_aware_selection_graph()
    nodes = [dict(node) for node in base["nodes"]]
    evidence = [dict(item) for item in base["evidence"]]

    extra_nodes = [
        {
            "node_id": "set_g",
            "node_type": "narrative",
            "title": "Yaşam Yönü Tanınma",
            "summary": "Yaşam yönünde görünürleşme çizgin, önceliklerini net kurduğunda daha kararlı akıyor.",
            "layers": [{"layer": "recognition", "weight": 0.72}, {"layer": "effect", "weight": 0.28}],
            "primary_layer": "recognition",
            "domain": "life_direction",
            "source_family": "core_story_ui",
            "source_path": "public.core_story_ui.text",
            "evidence_ids": ["evd_set_g"],
            "projection_hints": {"surfaces": ["profile_top", "home"], "priority": 0.87},
            "dedupe_fingerprint": "set_fp_g",
        },
        {
            "node_id": "set_h",
            "node_type": "guidance",
            "title": "İlişkide Mekanizma",
            "summary": "İlişkilerde ritmi yavaş kurduğunda bağın daha sürdürülebilir bir zemine oturuyor.",
            "layers": [{"layer": "mechanism", "weight": 0.7}, {"layer": "potential", "weight": 0.3}],
            "primary_layer": "mechanism",
            "domain": "relationships",
            "source_family": "supporting_threads",
            "source_path": "public.supporting_threads[3].paragraph",
            "evidence_ids": ["evd_set_h"],
            "projection_hints": {"surfaces": ["profile_deep", "profile_top"], "priority": 0.86},
            "dedupe_fingerprint": "set_fp_h",
        },
        {
            "node_id": "set_i",
            "node_type": "signal",
            "title": "Genel Etki Hattı",
            "summary": "Günlük düzende kurduğun tempo, dış etkiye daha sakin ama daha net bir ton veriyor.",
            "layers": [{"layer": "effect", "weight": 0.74}, {"layer": "mechanism", "weight": 0.26}],
            "primary_layer": "effect",
            "domain": "general",
            "source_family": "user_compact",
            "source_path": "public.user_compact.signature",
            "evidence_ids": ["evd_set_i"],
            "projection_hints": {"surfaces": ["profile_deep", "home"], "priority": 0.85},
            "dedupe_fingerprint": "set_fp_i",
        },
    ]
    extra_evidence = [
        {
            "evidence_id": "evd_set_g",
            "node_id": "set_g",
            "kind": "text",
            "source_family": "core_story_ui",
            "source_path": "public.core_story_ui.text",
            "weight": 0.66,
            "text_payload": "Yaşam yönünde tanınma çizgisi netleşiyor.",
            "structured_payload": None,
        },
        {
            "evidence_id": "evd_set_h",
            "node_id": "set_h",
            "kind": "text",
            "source_family": "supporting_threads",
            "source_path": "public.supporting_threads[3].paragraph",
            "weight": 0.64,
            "text_payload": "İlişkide yavaş kurulan ritim bağ kalitesini artırır.",
            "structured_payload": None,
        },
        {
            "evidence_id": "evd_set_i",
            "node_id": "set_i",
            "kind": "text",
            "source_family": "user_compact",
            "source_path": "public.user_compact.signature",
            "weight": 0.62,
            "text_payload": "Günlük tempo etkide sakin netlik üretir.",
            "structured_payload": None,
        },
    ]
    nodes.extend(extra_nodes)
    evidence.extend(extra_evidence)
    return {"version": "meaning_graph_v1_1", "nodes": nodes, "evidence": evidence}


def _test_normalize_similarity_text(value: str) -> str:
    clean = str(value or "").lower().strip()
    clean = clean.replace("ı", "i").replace("İ", "i")
    clean = clean.replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    clean = re.sub(r"[^a-z0-9\s]", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def _test_summary_tokens(value: str) -> set[str]:
    return {token for token in _test_normalize_similarity_text(value).split(" ") if token}


def _test_jaccard_similarity(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def _count_near_duplicates(nodes: list[dict], threshold: float = 0.55) -> int:
    count = 0
    for idx in range(len(nodes)):
        tokens_a = _test_summary_tokens(str(nodes[idx].get("summary") or ""))
        for jdx in range(idx + 1, len(nodes)):
            tokens_b = _test_summary_tokens(str(nodes[jdx].get("summary") or ""))
            if _test_jaccard_similarity(tokens_a, tokens_b) >= threshold:
                count += 1
    return count


def _count_duplicate_fingerprints(nodes: list[dict]) -> int:
    fingerprints = [str(node.get("dedupe_fingerprint") or "").strip() for node in nodes if str(node.get("dedupe_fingerprint") or "").strip()]
    return len(fingerprints) - len(set(fingerprints))


def _domain_diversity(nodes: list[dict]) -> int:
    domains = {str(node.get("domain") or "").strip() for node in nodes if str(node.get("domain") or "").strip()}
    return len(domains)


def _baseline_v8_like_pick(graph: dict, limit: int = 3) -> list[dict]:
    layer_bonus = {
        "shadow": 1.0,
        "effect": 0.95,
        "mechanism": 0.7,
        "potential": 0.68,
        "cause": 0.5,
        "recognition": 0.45,
    }
    nodes = [dict(item) for item in graph.get("nodes", []) if isinstance(item, dict)]
    candidates: list[dict] = []
    for node in nodes:
        hints = node.get("projection_hints") if isinstance(node.get("projection_hints"), dict) else {}
        surfaces = hints.get("surfaces") if isinstance(hints.get("surfaces"), list) else []
        if not set(str(item).strip() for item in surfaces).intersection({"profile_top", "home"}):
            continue
        importance = float(hints.get("priority") or 0.0)
        layers = node.get("layers") if isinstance(node.get("layers"), list) else []
        top_weight = 0.0
        for layer in layers:
            if isinstance(layer, dict):
                top_weight = max(top_weight, float(layer.get("weight") or 0.0))
        primary_layer = str(node.get("primary_layer") or "").strip().lower()
        score = (0.52 * importance) + (0.28 * top_weight) + (0.12 * 1.0) + (0.08 * layer_bonus.get(primary_layer, 0.3))
        candidates.append({"score": score, **node})
    candidates.sort(key=lambda item: (-float(item.get("score") or 0.0), str(item.get("node_id") or "")))
    return candidates[:limit]


def test_profile_narrative_projection_v1_contains_traceability() -> None:
    projection = build_profile_narrative_projection_v1(meaning_graph_v1_1=_sample_graph())

    assert projection["version"] == "profile_narrative_projection_v1"
    assert projection["source_graph"] == "meaning_graph_v1_1"
    core_blocks = projection["profile_public"]["core_blocks"]
    assert core_blocks
    first = core_blocks[0]
    assert first["trace"]["node_id"]
    assert first["trace"]["evidence_ids"]
    assert first["trace"]["evidence_ids"][0].startswith("evd_")

    detail_cards = projection["profile_public"]["detail_cards"]
    assert detail_cards
    assert detail_cards[0]["trace"]["node_id"]
    assert isinstance(detail_cards[0]["trace"]["evidence_ids"], list)


def test_profile_v8_projection_v1_contains_traceability() -> None:
    projection = build_profile_v8_projection_v1(meaning_graph_v1_1=_sample_graph())

    assert projection["version"] == "profile_v8_projection_v1"
    assert projection["source_graph"] == "meaning_graph_v1_1"
    assert projection["hero"]["trace"]["node_id"] == "node_hero"
    assert projection["hero"]["trace"]["evidence_ids"]
    assert projection["identity_axis"]["trace"]["node_id"]

    insight_strip = projection["insight_strip"]
    assert insight_strip
    assert insight_strip[0]["trace"]["node_id"]
    assert isinstance(insight_strip[0]["trace"]["evidence_ids"], list)


def test_profile_narrative_projection_v1_generates_unique_block_ids_for_colliding_prefixes() -> None:
    projection = build_profile_narrative_projection_v1(meaning_graph_v1_1=_diverse_graph())

    blocks = projection["profile_public"]["blocks"]
    block_ids = [str(item.get("id") or "").strip() for item in blocks]
    assert block_ids
    assert all(block_ids)
    assert len(block_ids) == len(set(block_ids))


def test_profile_narrative_projection_v1_enforces_domain_diversity_for_core_blocks() -> None:
    graph = _diverse_graph()
    projection = build_profile_narrative_projection_v1(meaning_graph_v1_1=graph)

    domain_by_node = {
        str(node.get("node_id") or "").strip(): str(node.get("domain") or "").strip()
        for node in graph["nodes"]
    }
    core_blocks = projection["profile_public"]["core_blocks"]
    selected_domains = {
        domain_by_node.get(str(block["trace"]["node_id"] or "").strip(), "")
        for block in core_blocks
    }
    selected_domains.discard("")
    assert len(selected_domains) >= 3


def test_profile_narrative_projection_v1_builds_multisentence_body_and_editorial_detail_blocks() -> None:
    projection = build_profile_narrative_projection_v1(meaning_graph_v1_1=_sample_graph())

    first_block = projection["profile_public"]["core_blocks"][0]
    body = str(first_block.get("body") or "").strip()
    sentences = [part for part in re.split(r"(?<=[.!?])\s+", body) if part.strip()]
    assert len(sentences) >= 2

    detail_cards = projection["profile_public"]["detail_cards"]
    assert detail_cards
    assert len(detail_cards[0]["detail_blocks"]) >= 2


def test_profile_narrative_projection_v1_body_uses_pattern_hooks_and_sentence_bounds() -> None:
    projection = build_profile_narrative_projection_v1(meaning_graph_v1_1=_diverse_graph())
    blocks = projection["profile_public"]["blocks"]
    assert blocks

    pattern_hooks = (
        "Dışarıdan",
        "Zorlandığında",
        "İçeride genelde",
        "İlişkilerde",
        "Bunu doğru kullandığında",
    )
    for block in blocks:
        body = str(block.get("body") or "").strip()
        assert any(hook in body for hook in pattern_hooks)
        sentences = [part for part in re.split(r"(?<=[.!?])\s+", body) if part.strip()]
        assert 2 <= len(sentences) <= 4


def test_profile_narrative_projection_v1_body_avoids_fixed_template_phrase() -> None:
    projection = build_profile_narrative_projection_v1(meaning_graph_v1_1=_diverse_graph())
    bodies = [
        str(block.get("body") or "").strip()
        for block in projection["profile_public"]["blocks"]
    ]
    assert bodies
    assert all("Bu tema en çok" not in body for body in bodies)


def test_profile_narrative_projection_v1_body_openings_are_not_single_template() -> None:
    projection = build_profile_narrative_projection_v1(meaning_graph_v1_1=_diverse_graph())
    bodies = [
        str(block.get("body") or "").strip()
        for block in projection["profile_public"]["blocks"]
        if str(block.get("body") or "").strip()
    ]
    openings = []
    for body in bodies:
        tokens = re.findall(r"[A-Za-zÇĞİÖŞÜçğıöşü0-9]+", body.lower())
        if tokens:
            openings.append(" ".join(tokens[:3]))
    assert openings
    assert len(set(openings)) >= 2


def test_profile_narrative_projection_v1_template_and_short_body_ratio_targets() -> None:
    projection = build_profile_narrative_projection_v1(meaning_graph_v1_1=_diverse_graph())
    bodies = [
        str(block.get("body") or "").strip()
        for block in projection["profile_public"]["blocks"]
        if str(block.get("body") or "").strip()
    ]
    assert bodies
    template_ratio = sum(1 for body in bodies if "Bu tema en çok" in body) / len(bodies)
    short_ratio = sum(1 for body in bodies if len(body) < 160) / len(bodies)
    assert template_ratio < 0.30
    assert short_ratio < 0.25


def test_profile_v8_projection_v1_uses_patterned_multisentence_bodies() -> None:
    projection = build_profile_v8_projection_v1(meaning_graph_v1_1=_diverse_graph())
    pattern_hooks = (
        "Dışarıdan",
        "Zorlandığında",
        "İçeride genelde",
        "İlişkilerde",
        "Bunu doğru kullandığında",
    )

    identity_body = str(projection["identity_axis"].get("body") or "").strip()
    differentiator_bodies = [str(item.get("body") or "").strip() for item in projection["differentiators"]]
    all_bodies = [identity_body, *differentiator_bodies]
    assert all_bodies

    for body in all_bodies:
        assert body
        assert "Bu tema en çok" not in body
        assert any(hook in body for hook in pattern_hooks)
        sentences = [part for part in re.split(r"(?<=[.!?])\s+", body) if part.strip()]
        assert 2 <= len(sentences) <= 4


def test_projection_microcopy_naturalization_guards() -> None:
    projection = build_profile_narrative_projection_v1(meaning_graph_v1_1=_diverse_graph())
    bodies = [
        str(block.get("body") or "").strip()
        for block in projection["profile_public"]["blocks"]
        if str(block.get("body") or "").strip()
    ]
    headlines = [
        str(block.get("headline") or "").strip()
        for block in projection["profile_public"]["blocks"]
    ]
    corpus = [*headlines, *bodies]
    assert all("Identity." not in item for item in corpus)
    assert all("Mind." not in item for item in corpus)
    assert all("alan alanında" not in item.lower() for item in corpus)

    generic_phrases = (
        "Bu hikayenin merkezinde şu var",
        "Zorlayan tarafı şu",
        "En belirgin etkisini",
        "Sende öne çıkan dinamik şu",
        "Temel tonun burada netleşiyor",
    )
    total_hits = 0
    for phrase in generic_phrases:
        total_hits += sum(1 for body in bodies if phrase in body)
    assert total_hits <= 1


def test_projection_builders_are_stable_for_same_graph() -> None:
    first_narrative = build_profile_narrative_projection_v1(meaning_graph_v1_1=_diverse_graph())
    second_narrative = build_profile_narrative_projection_v1(meaning_graph_v1_1=_diverse_graph())
    assert first_narrative == second_narrative

    first_v8 = build_profile_v8_projection_v1(meaning_graph_v1_1=_diverse_graph())
    second_v8 = build_profile_v8_projection_v1(meaning_graph_v1_1=_diverse_graph())
    assert first_v8 == second_v8


def test_profile_narrative_projection_v1_hard_dedupes_fingerprints() -> None:
    graph = _fingerprint_collision_graph()
    projection = build_profile_narrative_projection_v1(meaning_graph_v1_1=graph)
    blocks = projection["profile_public"]["blocks"]
    assert blocks

    fingerprint_by_node = {
        str(node.get("node_id") or "").strip(): str(node.get("dedupe_fingerprint") or "").strip()
        for node in graph["nodes"]
    }
    selected_fingerprints = [
        fingerprint_by_node.get(str(block["trace"]["node_id"] or "").strip(), "")
        for block in blocks
    ]
    selected_fingerprints = [item for item in selected_fingerprints if item]
    assert selected_fingerprints
    assert len(selected_fingerprints) == len(set(selected_fingerprints))


def test_profile_narrative_projection_v1_keeps_selection_size_with_one_soft_duplicate_relaxation() -> None:
    projection = build_profile_narrative_projection_v1(meaning_graph_v1_1=_soft_duplicate_underfilled_graph())
    core_blocks = projection["profile_public"]["core_blocks"]
    assert len(core_blocks) == 4

    node_ids = [str(block["trace"]["node_id"] or "").strip() for block in core_blocks]
    assert len(node_ids) == len(set(node_ids))


def test_profile_narrative_projection_v1_policy_selection_is_deterministic_with_duplicates() -> None:
    graph = _soft_duplicate_underfilled_graph()
    first = build_profile_narrative_projection_v1(meaning_graph_v1_1=graph)
    second = build_profile_narrative_projection_v1(meaning_graph_v1_1=graph)
    assert first == second


def test_profile_v8_projection_v1_set_aware_selection_reduces_near_duplicates_vs_naive() -> None:
    graph = _set_aware_selection_graph()
    projection = build_profile_v8_projection_v1(meaning_graph_v1_1=graph)

    nodes_by_id = {
        str(node.get("node_id") or "").strip(): node
        for node in graph["nodes"]
    }
    selected_ids = [
        str(item.get("trace", {}).get("node_id") or "").strip()
        for item in projection["insight_strip"]
        if str(item.get("trace", {}).get("node_id") or "").strip()
    ]
    selected_nodes = [dict(nodes_by_id[node_id]) for node_id in selected_ids if node_id in nodes_by_id]
    assert len(selected_nodes) == 3

    baseline_nodes = _baseline_v8_like_pick(graph, limit=3)
    assert len(baseline_nodes) == 3

    baseline_near_duplicates = _count_near_duplicates(baseline_nodes)
    selected_near_duplicates = _count_near_duplicates(selected_nodes)
    assert selected_near_duplicates < baseline_near_duplicates

    baseline_fingerprint_duplicates = _count_duplicate_fingerprints(baseline_nodes)
    selected_fingerprint_duplicates = _count_duplicate_fingerprints(selected_nodes)
    assert selected_fingerprint_duplicates <= baseline_fingerprint_duplicates

    baseline_domain_diversity = _domain_diversity(baseline_nodes)
    selected_domain_diversity = _domain_diversity(selected_nodes)
    assert selected_domain_diversity >= baseline_domain_diversity


def test_profile_v8_projection_v1_applies_domain_and_layer_soft_caps_without_underfill() -> None:
    projection = build_profile_v8_projection_v1(meaning_graph_v1_1=_set_aware_selection_graph())
    assert len(projection["insight_strip"]) == 3
    assert len(projection["differentiators"]) == 3

    graph = _set_aware_selection_graph()
    nodes_by_id = {
        str(node.get("node_id") or "").strip(): node
        for node in graph["nodes"]
    }
    selected_ids = [
        str(item.get("trace", {}).get("node_id") or "").strip()
        for item in projection["insight_strip"]
        if str(item.get("trace", {}).get("node_id") or "").strip()
    ]
    selected_nodes = [dict(nodes_by_id[node_id]) for node_id in selected_ids if node_id in nodes_by_id]

    domain_counts: dict[str, int] = {}
    layer_counts: dict[str, int] = {}
    for node in selected_nodes:
        domain = str(node.get("domain") or "").strip()
        primary_layer = str(node.get("primary_layer") or "").strip().lower()
        if domain:
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        if primary_layer:
            layer_counts[primary_layer] = layer_counts.get(primary_layer, 0) + 1

    assert domain_counts
    assert max(domain_counts.values()) <= 2
    assert max(layer_counts.values()) <= 2


def test_profile_v8_projection_v1_balances_shadow_with_floor_and_cap() -> None:
    graph = _set_aware_selection_graph()
    projection = build_profile_v8_projection_v1(meaning_graph_v1_1=graph)

    nodes_by_id = {
        str(node.get("node_id") or "").strip(): node
        for node in graph["nodes"]
    }
    insight_ids = [
        str(item.get("trace", {}).get("node_id") or "").strip()
        for item in projection["insight_strip"]
        if str(item.get("trace", {}).get("node_id") or "").strip()
    ]
    differentiator_ids = [
        str(item.get("trace", {}).get("node_id") or "").strip()
        for item in projection["differentiators"]
        if str(item.get("trace", {}).get("node_id") or "").strip()
    ]
    selected_ids = [*insight_ids, *differentiator_ids]
    selected_nodes = [dict(nodes_by_id[node_id]) for node_id in selected_ids if node_id in nodes_by_id]
    assert len(selected_nodes) == 6

    insight_shadow_count = sum(
        1 for node_id in insight_ids if str(nodes_by_id.get(node_id, {}).get("primary_layer") or "").strip().lower() == "shadow"
    )
    differentiator_shadow_count = sum(
        1 for node_id in differentiator_ids if str(nodes_by_id.get(node_id, {}).get("primary_layer") or "").strip().lower() == "shadow"
    )
    total_shadow_count = insight_shadow_count + differentiator_shadow_count
    assert total_shadow_count <= 2
    assert total_shadow_count >= 1

    shadow_ratio = total_shadow_count / max(1, len(selected_nodes))
    assert 0.2 <= shadow_ratio <= 0.35


def test_profile_v8_projection_v1_uses_unique_node_ids_across_slots_when_pool_is_sufficient() -> None:
    projection = build_profile_v8_projection_v1(meaning_graph_v1_1=_v8_unique_slots_graph())
    slot_node_ids = [
        str(projection.get("hero", {}).get("trace", {}).get("node_id") or "").strip(),
        str(projection.get("identity_axis", {}).get("trace", {}).get("node_id") or "").strip(),
        *[
            str(item.get("trace", {}).get("node_id") or "").strip()
            for item in projection.get("insight_strip", [])
        ],
        *[
            str(item.get("trace", {}).get("node_id") or "").strip()
            for item in projection.get("differentiators", [])
        ],
    ]
    assert len(slot_node_ids) == 8
    assert all(slot_node_ids)
    assert len(set(slot_node_ids)) == len(slot_node_ids)


def test_profile_v8_projection_v1_keeps_duplicates_and_near_duplicates_low_with_guardrails() -> None:
    graph = _set_aware_selection_graph()
    projection = build_profile_v8_projection_v1(meaning_graph_v1_1=graph)

    nodes_by_id = {
        str(node.get("node_id") or "").strip(): node
        for node in graph["nodes"]
    }
    selected_ids = [
        str(item.get("trace", {}).get("node_id") or "").strip()
        for item in [*projection["insight_strip"], *projection["differentiators"]]
        if str(item.get("trace", {}).get("node_id") or "").strip()
    ]
    selected_nodes = [dict(nodes_by_id[node_id]) for node_id in selected_ids if node_id in nodes_by_id]
    assert len(selected_nodes) == 6

    duplicate_fingerprint_count = _count_duplicate_fingerprints(selected_nodes)
    near_duplicate_count = _count_near_duplicates(selected_nodes)
    assert duplicate_fingerprint_count <= 1
    assert near_duplicate_count <= 2


def test_projection_selection_debug_metrics_exist_when_enabled() -> None:
    clear_last_projection_selection_debug()
    debug: dict = {}
    build_profile_narrative_projection_v1(
        meaning_graph_v1_1=_set_aware_selection_graph(),
        selection_debug=debug,
    )

    assert debug.get("projection") == "profile_narrative_projection_v1"
    branches = debug.get("branches")
    assert isinstance(branches, dict)
    assert "narrative_core" in branches
    core = branches["narrative_core"]

    assert isinstance(core.get("selected_node_ids"), list)
    assert core["selected_node_ids"]
    decomposition = core.get("candidate_score_decomposition")
    assert isinstance(decomposition, list)
    assert decomposition
    required_fields = {
        "base_score",
        "similarity_penalty",
        "domain_penalty",
        "layer_penalty",
        "repetition_penalty",
        "final_score",
    }
    assert required_fields.issubset(set(decomposition[0].keys()))

    counters = core.get("reason_counters")
    assert isinstance(counters, dict)
    assert int(counters.get("accepted", 0)) >= 1
    assert int(counters.get("scored_candidate", 0)) >= int(counters.get("accepted", 0))

    for metric in (
        "duplicate_fingerprint_hits",
        "near_duplicate_hits",
        "domain_cap_hits",
        "layer_cap_hits",
        "underfill_relaxation_used",
    ):
        assert metric in core

    snapshot = get_last_projection_selection_debug()
    assert snapshot.get("projection") == "profile_narrative_projection_v1"
    assert "narrative_core" in (snapshot.get("branches") or {})


def test_projection_selection_debug_does_not_change_public_output_schema() -> None:
    plain_narrative = build_profile_narrative_projection_v1(meaning_graph_v1_1=_diverse_graph())
    debug_narrative: dict = {}
    debugged_narrative = build_profile_narrative_projection_v1(
        meaning_graph_v1_1=_diverse_graph(),
        selection_debug=debug_narrative,
    )
    assert plain_narrative == debugged_narrative
    assert "selection_debug" not in plain_narrative

    plain_v8 = build_profile_v8_projection_v1(meaning_graph_v1_1=_set_aware_selection_graph())
    debug_v8: dict = {}
    debugged_v8 = build_profile_v8_projection_v1(
        meaning_graph_v1_1=_set_aware_selection_graph(),
        selection_debug=debug_v8,
    )
    assert plain_v8 == debugged_v8
    assert set(plain_v8.keys()) == {
        "version",
        "source_graph_version",
        "source_graph",
        "hero",
        "identity_axis",
        "insight_strip",
        "differentiators",
        "traceability",
    }


def test_projection_selection_debug_is_deterministic() -> None:
    clear_last_projection_selection_debug()
    first_debug: dict = {}
    first_output = build_profile_v8_projection_v1(
        meaning_graph_v1_1=_set_aware_selection_graph(),
        selection_debug=first_debug,
    )
    first_snapshot = get_last_projection_selection_debug()

    second_debug: dict = {}
    second_output = build_profile_v8_projection_v1(
        meaning_graph_v1_1=_set_aware_selection_graph(),
        selection_debug=second_debug,
    )
    second_snapshot = get_last_projection_selection_debug()

    assert first_output == second_output
    assert first_debug == second_debug
    assert first_snapshot == second_snapshot


def test_projection_cluster_plan_path_activates_and_v8_hero_prefers_identity_or_mind() -> None:
    packets = [
        _packet(
            packet_id="identity_self_construction",
            domain="identity",
            promise_type="behavior_reflex",
            strength=0.93,
            headline="Dışarıda çizgini korumak sende kimlik kurucu bir refleks.",
            direct="Dışarıda çizgini korumak sende kimlik kurucu bir refleks.",
            scene="Zor anlarda önce kendini toplar ve çizgini korursun.",
            gift="Kriz anında omurganı korumak.",
            anchors=["Yükselen Oğlak", "1th house ruler route"],
            evidence_ids=["house:1->ruler:Saturn->house:3"],
        ),
        _packet(
            packet_id="mind_structured_originality",
            domain="mind",
            promise_type="mind_style",
            strength=0.95,
            headline="Özgün fikri çalışır hale getiren bir zihnin var.",
            direct="Özgün fikri çalışır hale getiren bir zihnin var.",
            scene="Yeni fikri sistem kurup çalıştırırsın.",
            gift="Yenilikle yapıyı aynı anda tutmak.",
            anchors=["Saturn sextile Uranus", "Satürn 3. ev"],
            evidence_ids=["Saturn:Uranus:sextile"],
        ),
        _packet(
            packet_id="relationship_attachment_architecture",
            domain="relationship",
            promise_type="need",
            strength=0.89,
            headline="Yakınlık sende güven ve derinlik eşiğiyle açılıyor.",
            direct="Yakınlık sende güven ve derinlik eşiğiyle açılıyor.",
            scene="Birine açılmadan önce güvenin oturmasını beklersin.",
            gift="Derin bağ kurmak.",
            anchors=["7th house ruler route", "Ay 8. ev"],
            evidence_ids=["house:7->ruler:Moon->house:8"],
        ),
        _packet(
            packet_id="career_visibility_signature",
            domain="career",
            promise_type="career_signature",
            strength=0.86,
            headline="Görünürlük sende önce içeride olgunlaşıyor.",
            direct="Görünürlük sende önce içeride olgunlaşıyor.",
            scene="Bir işi göstermeden önce rafine etmeyi tercih edersin.",
            gift="Hazırlıkta kalite toplamak.",
            anchors=["Venüs 12. ev", "MC Terazi"],
            evidence_ids=["house:10->ruler:Venus->house:12"],
        ),
    ]
    cluster_plan = _cluster_plan_from_packets(packets)
    packet_payload = {"version": "natal_promise_packets_v1", "packets": packets}

    narrative = build_profile_narrative_projection_v1(
        meaning_graph_v1_1=_sample_graph(),
        natal_promise_packets_v1=packet_payload,
        natal_promise_cluster_plan_v1=cluster_plan,
        include_packet_debug=True,
    )
    assert narrative["source_graph"] == "natal_promise_cluster_plan_v1"
    assert narrative["traceability"]["cluster_public_main_count"] >= 3
    assert any(block["node_id"].startswith("promise::") for block in narrative["profile_public"]["core_blocks"])

    v8 = build_profile_v8_projection_v1(
        meaning_graph_v1_1=_sample_graph(),
        natal_promise_packets_v1=packet_payload,
        natal_promise_cluster_plan_v1=cluster_plan,
        include_packet_debug=True,
    )
    hero_id = str(v8["hero"]["trace"]["node_id"] or "")
    assert v8["source_graph"] == "natal_promise_cluster_plan_v1"
    assert hero_id in {
        "promise::identity_self_construction",
        "promise::mind_structured_originality",
    }
    visible_identity_slots = {
        str(v8["hero"]["trace"]["node_id"] or "").strip(),
        str(v8["identity_axis"]["trace"]["node_id"] or "").strip(),
        *(str(item["trace"]["node_id"] or "").strip() for item in v8["insight_strip"]),
        *(str(item["trace"]["node_id"] or "").strip() for item in v8["differentiators"]),
    }
    assert "promise::identity_self_construction" in visible_identity_slots
    all_block_ids = {
        str(block["node_id"] or "").strip()
        for block in narrative["profile_public"]["blocks"]
    }
    assert "promise::career_visibility_signature" in all_block_ids


def test_projection_cluster_plan_hybrid_fallback_uses_cluster_then_packet_then_legacy() -> None:
    packets = [
        _packet(
            packet_id="mind_packet",
            domain="mind",
            promise_type="mind_style",
            strength=0.92,
            headline="Zihnin hızlı ama kontrollü çalışıyor.",
            direct="Zihnin hızlı ama kontrollü çalışıyor.",
            scene="Bir fikir geldiğinde hızlıca sistem kurarsın.",
            gift="Düşünceyi yapıya çevirmek.",
            anchors=["Saturn sextile Uranus"],
            evidence_ids=["Saturn:Uranus:sextile"],
        ),
        _packet(
            packet_id="relationship_packet",
            domain="relationship",
            promise_type="love_style",
            strength=0.88,
            headline="Yakınlık sende güven oluşunca yumuşuyor.",
            direct="Yakınlık sende güven oluşunca yumuşuyor.",
            scene="Bir bağ içeri oturduğunda daha sıcak açılırsın.",
            gift="Sevgiyle iyi gelmek.",
            anchors=["Moon trine Venus"],
            evidence_ids=["Moon:Venus:trine"],
        ),
    ]
    cluster_plan = _cluster_plan_from_packets(packets)
    packet_payload = {"version": "natal_promise_packets_v1", "packets": packets}

    projection = build_profile_narrative_projection_v1(
        meaning_graph_v1_1=_sample_graph(),
        natal_promise_packets_v1=packet_payload,
        natal_promise_cluster_plan_v1=cluster_plan,
        include_packet_debug=True,
    )
    block_ids = [str(block["node_id"] or "") for block in projection["profile_public"]["blocks"]]

    assert projection["source_graph"] == "natal_promise_cluster_plan_v1"
    assert projection["traceability"]["cluster_public_main_count"] == 2
    assert any(node_id.startswith("promise::") for node_id in block_ids)
    assert any(node_id.startswith("node_") for node_id in block_ids)


def test_projection_cluster_plan_renderer_keeps_remaining_public_main_visible() -> None:
    packets = [
        _packet(
            packet_id="identity_main",
            domain="identity",
            promise_type="behavior_reflex",
            strength=0.94,
            headline="Duruşun sende kimliğin önemli bir parçası.",
            direct="Duruşun sende kimliğin önemli bir parçası.",
            scene="Zor anda bile çizgini korumaya çalışırsın.",
            gift="Omurganı korumak.",
            anchors=["Yükselen Oğlak"],
        ),
        _packet(
            packet_id="mind_main",
            domain="mind",
            promise_type="mind_style",
            strength=0.93,
            headline="Fikri hızla yapıya çevirebiliyorsun.",
            direct="Fikri hızla yapıya çevirebiliyorsun.",
            scene="Yeni fikri sistemli biçimde kurarsın.",
            gift="Yapıyla hız arasında köprü kurmak.",
            anchors=["Saturn sextile Uranus"],
        ),
        _packet(
            packet_id="relationship_main",
            domain="relationship",
            promise_type="need",
            strength=0.91,
            headline="Yakınlık sende güvenle açılıyor.",
            direct="Yakınlık sende güvenle açılıyor.",
            scene="Güven oluşmadan tam açılmazsın.",
            gift="Derin bağ kurmak.",
            anchors=["Moon trine Venus"],
        ),
        _packet(
            packet_id="career_main",
            domain="career",
            promise_type="career_signature",
            strength=0.9,
            headline="İşini önce içeride olgunlaştırırsın.",
            direct="İşini önce içeride olgunlaştırırsın.",
            scene="Bir şeyi göstermeden önce rafine edersin.",
            gift="Hazırlıkta kalite toplamak.",
            anchors=["MC Terazi"],
        ),
        _packet(
            packet_id="career_healing_voice",
            domain="career",
            promise_type="wound_to_gift",
            strength=0.89,
            headline="Kırılganlığını sese çevirebilirsin.",
            direct="Kırılganlığını sese çevirebilirsin.",
            scene="Görünür olmadan önce fazladan hazırlanırsın.",
            gift="Kırılganlığı sezgiye çevirmek.",
            anchors=["Chiron conjunct MC"],
        ),
        _packet(
            packet_id="identity_resilience",
            domain="identity",
            promise_type="gift",
            strength=0.88,
            headline="Baskıda dağılmak yerine derinleşirsin.",
            direct="Baskıda dağılmak yerine derinleşirsin.",
            scene="Zorlanınca içerde daha sert bir omurga kurarsın.",
            gift="Dayanıklılık.",
            anchors=["Saturn trine Pluto", "Sun square Saturn"],
        ),
    ]
    cluster_plan = _cluster_plan_from_packets(packets)
    packet_payload = {"version": "natal_promise_packets_v1", "packets": packets}

    narrative = build_profile_narrative_projection_v1(
        meaning_graph_v1_1=_sample_graph(),
        natal_promise_packets_v1=packet_payload,
        natal_promise_cluster_plan_v1=cluster_plan,
        include_packet_debug=True,
    )

    block_ids = [str(block["node_id"] or "").strip() for block in narrative["profile_public"]["blocks"]]
    assert "promise::career_healing_voice" in block_ids
    assert "promise::identity_resilience" in block_ids


# ---------------------------------------------------------------------------
# Adana audit regressions (P0 bug fixes)
# ---------------------------------------------------------------------------


def test_headline_slot_rejects_body_shape_paragraph() -> None:
    """Bug 2: a long-form multi-sentence string in node.headline must be
    demoted to body and a short alternative pulled into the headline slot."""
    from app.meaning.projection_shadow_v1_builder import (
        _clip_to_headline,
        _is_long_form_headline,
        _profile_block_from_node,
    )

    long_text = (
        "Sen dışarıdan uyumlu ve dengeli görünebilirsin. "
        "Yükselenin Terazi olduğu için bir ortama girdiğinde önce havayı, "
        "tonu ve insanlar arasındaki dengeyi yokluyorsun. "
        "Ama iş zihnine ve kendini ifade etme biçimine geldiğinde "
        "içeride çok daha ölçülü, seçici ve eleştirel bir şey çalışıyor."
    )
    # Direct helper assertion: the helper recognizes body-shape input.
    assert _is_long_form_headline(long_text) is True
    # And the clipper returns at most a single short sentence.
    clipped = _clip_to_headline(long_text)
    if clipped is not None:
        assert len(clipped) <= 120
        # No interior sentence terminator other than the trailing one.
        interior = clipped[:-1] if clipped[-1] in ".!?…" else clipped
        for term in ".!?…":
            assert term not in interior
    # And: when fed into a projection node, the block headline is short.
    node = {
        "node_id": "promise::mind_mind_system",
        "headline": long_text,
        "title": long_text,
        "summary": "Ne yapacağını bildiğin an tempo kendiliğinden yükselir.",
        "domain": "mind",
        "primary_layer": "mechanism",
        "layers": [{"layer": "mechanism", "weight": 1.0}],
        "evidence": [],
        "evidence_ids": [],
    }
    block = _profile_block_from_node(
        node=node,
        emphasis="core",
        used_block_ids=set(),
        used_openings=[],
        used_bodies=[],
    )
    headline = str(block.get("headline") or "")
    assert headline
    assert len(headline) <= 140, f"headline exceeded budget: {len(headline)}"
    # The body should now carry (some of) the demoted long-form copy.
    body = str(block.get("body") or "")
    assert body


def test_no_aux_mirror_duplicate_when_support_and_detail_empty() -> None:
    """Bug 1: when the cluster plan has 3 main clusters and no support or
    detail clusters, extra_blocks must NOT carry the `_aux` mirrors of the
    same main packets (which would produce identical-headline duplicate
    cards). Empty extra_blocks is preferable to duplicate cards."""
    packets = [
        _packet(
            packet_id="career_only",
            domain="career",
            promise_type="career_signature",
            strength=0.95,
            headline="Kariyer hattın görünür ve net.",
            direct="Kariyer hattın görünür ve net.",
            scene="İşte rahatça konumlanırsın.",
            gift="Görünürlüğü taşımak.",
            anchors=["MC Yengeç"],
        ),
        _packet(
            packet_id="career_only_aux",
            domain="career",
            promise_type="career_signature",
            strength=0.6,
            headline="Kariyer hattın görünür ve net.",
            direct="Kariyer hattın görünür ve net.",
            scene="Aux teaser.",
            gift="Aux.",
            anchors=["MC Yengeç"],
        ),
        _packet(
            packet_id="relationship_only",
            domain="relationship",
            promise_type="need",
            strength=0.94,
            headline="Yakınlık sende güvenle açılıyor.",
            direct="Yakınlık sende güvenle açılıyor.",
            scene="Güven oluşmadan açılmazsın.",
            gift="Derin bağ.",
            anchors=["Mars Aslan 11h"],
        ),
        _packet(
            packet_id="relationship_only_aux",
            domain="relationship",
            promise_type="need",
            strength=0.6,
            headline="Yakınlık sende güvenle açılıyor.",
            direct="Yakınlık sende güvenle açılıyor.",
            scene="Aux scene.",
            gift="Aux.",
            anchors=["Mars Aslan 11h"],
        ),
        _packet(
            packet_id="mind_only",
            domain="mind",
            promise_type="mind_style",
            strength=0.93,
            headline="Fikri hızla yapıya çevirebiliyorsun.",
            direct="Fikri hızla yapıya çevirebiliyorsun.",
            scene="Yapıyla hız aynı anda çalışır.",
            gift="Hız ve yapı.",
            anchors=["Venüs Başak 11h"],
        ),
        _packet(
            packet_id="mind_only_aux",
            domain="mind",
            promise_type="mind_style",
            strength=0.6,
            headline="Fikri hızla yapıya çevirebiliyorsun.",
            direct="Fikri hızla yapıya çevirebiliyorsun.",
            scene="Aux scene.",
            gift="Aux.",
            anchors=["Venüs Başak 11h"],
        ),
    ]
    cluster_plan = _cluster_plan_from_packets(packets)
    packet_payload = {"version": "natal_promise_packets_v1", "packets": packets}

    narrative = build_profile_narrative_projection_v1(
        meaning_graph_v1_1=_sample_graph(),
        natal_promise_packets_v1=packet_payload,
        natal_promise_cluster_plan_v1=cluster_plan,
        include_packet_debug=True,
    )
    core_blocks = narrative["profile_public"]["core_blocks"]
    extra_blocks = narrative["profile_public"]["extra_blocks"]
    core_packet_ids = {
        str(block.get("node_id") or "").replace("promise::", "")
        for block in core_blocks
    }
    # No extra_block should be the `_aux` mirror of a core packet.
    for block in extra_blocks:
        pid = str(block.get("node_id") or "").replace("promise::", "")
        assert not (pid.endswith("_aux") and pid[: -len("_aux")] in core_packet_ids), (
            f"extra_block {pid!r} is the _aux mirror of a core packet"
        )
    # And no two blocks should share a headline.
    headlines = [str(b.get("headline") or "") for b in [*core_blocks, *extra_blocks]]
    assert len(headlines) == len(set(headlines)), f"duplicate headlines: {headlines}"


def test_smart_clip_never_breaks_mid_word() -> None:
    """Bug 3: the body/teaser truncation helper must cut at sentence or word
    boundaries, never inside a word."""
    from app.meaning.projection_shadow_v1_builder import _smart_clip

    # Mid-word case: the original hard slice ended with "deği…" mid-word.
    text = (
        "İnsanlar sende yalnızca sonucu değil, kalite çıtasını da görür. "
        "Sen görünür olmaya sadece dikkat çekmek gibi bakmıyorsun."
    )
    clipped = _smart_clip(text, 60)
    assert len(clipped) <= 60
    # Must not end mid-word. If an ellipsis appears, the char before it must
    # be a whitespace-terminated boundary (whitespace was stripped) — i.e.
    # the original char before the cut must have been a space.
    if clipped.endswith("…"):
        before_ellipsis = clipped[:-1].rstrip()
        # The trimmed prefix must end at a word boundary in the source text.
        assert text.startswith(before_ellipsis)
        next_char_idx = len(before_ellipsis)
        if next_char_idx < len(text):
            assert text[next_char_idx] == " ", (
                f"smart_clip cut inside a word: {clipped!r} (next char: {text[next_char_idx]!r})"
            )
    # If under budget, return unchanged.
    short = "Kısa cümle."
    assert _smart_clip(short, 50) == short
    # Prefer sentence boundary if one fits inside the budget.
    multi = "Birinci cümle. İkinci cümle daha uzun ve buraya sığmayacak."
    cut = _smart_clip(multi, 30)
    assert cut.endswith(".")
    assert "Birinci cümle." in cut


def test_post_colon_capitalization_uses_turkish_i() -> None:
    """Bug 4: the post-period capitalization helper must also fire after
    `:` and `;`, and use Turkish dotted İ (U+0130), not the decomposed
    `i + combining-dot-above` (U+0307) sequence."""
    from app.meaning.projection_shadow_v1_builder import _localize_public_copy_tr

    raw = "Üretiminde sana özgün bir imza veren yer de burada: insanlar önce kalite çıtasını görür."
    fixed = _localize_public_copy_tr(raw)
    assert "burada: İnsanlar" in fixed, f"post-colon İ not applied: {fixed!r}"
    # The capital after the colon must be the precomposed İ (U+0130), not
    # the decomposed i + combining-dot-above (U+0307) sequence.
    assert "burada: İnsanlar" in fixed
    # The original decomposed bug pattern (lowercase i + U+0307) must not
    # appear after a sentence boundary in the produced string.
    assert "i̇" not in fixed
    # Also: an already-decomposed input must be repaired to the precomposed form.
    raw_decomposed = "burada: i̇nsanlar konuşur."
    fixed_decomposed = _localize_public_copy_tr(raw_decomposed)
    assert "burada: İnsanlar" in fixed_decomposed
    assert "i̇" not in fixed_decomposed
    # Semicolon path.
    raw_semi = "Bir yan duygusu; insanlar burada açık konuşur."
    fixed_semi = _localize_public_copy_tr(raw_semi)
    assert "; İnsanlar" in fixed_semi
    # The numbered-abbreviation guard must still hold ("1. ev" never capitalized).
    raw_house = "Bu çizgi 1. ev tarafında belirgin."
    fixed_house = _localize_public_copy_tr(raw_house)
    assert "1. ev" in fixed_house
    assert "1. Ev" not in fixed_house


# ---------------------------------------------------------------------------
# v8 identity_axis cluster-family preference (Adana §4/§5 regression).
# See docs/system/adana_cluster_plan_audit_after_v0_3_final.md §4 + §5 for
# the original bug evidence: with v0.3 active, Adana now carries an
# ``identity_identity_like_libra_asc_venus_chart_ruler_chart_exact`` cluster
# (detail tier), but the v8 selector was still picking a mind-family
# packet for ``identity_axis``. The fix below adds an identity-family
# preference to the v8 selector while keeping legacy fallback intact.
# ---------------------------------------------------------------------------


def _v8_for_artifact(artifact_path: str) -> dict:
    import json
    from pathlib import Path

    from app.natal.natal_promise_packets import build_natal_promise_packets_v1
    from app.natal.natal_promise_cluster_plan import build_natal_promise_cluster_plan_v1

    artifact = json.loads(Path(artifact_path).read_text(encoding="utf-8"))

    def _walk(payload, *, key):
        if isinstance(payload, dict):
            if key in payload:
                yield payload[key]
            for value in payload.values():
                yield from _walk(value, key=key)
        elif isinstance(payload, list):
            for item in payload:
                yield from _walk(item, key=key)

    sections = next(iter(_walk(artifact, key="sections_v2")), [])
    threads = next(iter(_walk(artifact, key="supporting_threads")), [])
    planets = artifact.get("planets") or next(iter(_walk(artifact, key="planets")), [])
    aspects = artifact.get("aspects") or next(iter(_walk(artifact, key="aspects")), [])
    natal_graph_compact = (
        artifact.get("natal_graph_compact")
        or next(iter(_walk(artifact, key="natal_graph_compact")), {})
    )
    metadata = artifact.get("metadata") or {}
    meta_info = artifact.get("meta_info") or {}

    inventory = build_natal_promise_packets_v1(
        sections_v2=sections,
        supporting_threads=threads,
        planets=planets,
        aspects=aspects,
        natal_graph_compact=natal_graph_compact,
        metadata=metadata,
        meta_info=meta_info,
        locale="tr",
        mode="candidate_inventory",
    )
    selected = build_natal_promise_packets_v1(
        sections_v2=sections,
        supporting_threads=threads,
        planets=planets,
        aspects=aspects,
        natal_graph_compact=natal_graph_compact,
        metadata=metadata,
        meta_info=meta_info,
        locale="tr",
        mode="selected",
    )
    plan = build_natal_promise_cluster_plan_v1(inventory.get("packets") or [])

    v8 = build_profile_v8_projection_v1(
        meaning_graph_v1_1={"version": "meaning_graph_v1_1", "nodes": [], "evidence": []},
        natal_promise_packets_v1=selected,
        natal_promise_cluster_plan_v1=plan,
        include_packet_debug=True,
    )

    pid_to_cluster: dict[str, str] = {}
    for cluster in plan.get("clusters") or []:
        cid = str(cluster.get("id") or "").strip()
        if cluster.get("main_packet_id"):
            pid_to_cluster.setdefault(str(cluster["main_packet_id"]), cid)
        for member in cluster.get("packet_members") or []:
            packet_id = str(member.get("packet_id") or "").strip()
            if packet_id:
                pid_to_cluster.setdefault(packet_id, cid)

    return {"v8": v8, "pid_to_cluster": pid_to_cluster, "plan": plan}


def _slot_packet_id(slot: dict) -> str:
    raw = str((slot.get("trace") or {}).get("node_id") or "")
    return raw.replace("promise::", "")


def test_adana_v8_identity_axis_prefers_identity_family_cluster() -> None:
    """Adana §4/§5 regression: when an identity-family cluster exists in the
    cluster plan (including detail tier), v8 ``identity_axis`` must pick
    from it rather than falling back to mind-family.

    Adana's plan carries ``identity_identity_like_libra_asc_venus_chart_ruler_chart_exact``
    in detail. The v8 selector previously picked
    ``mercury_virgo_12h_private_analytical_mind_chart_exact`` (mind family)
    for the ``Kimlik Ekseni`` slot. After the fix it must select the
    identity-family cluster's packet, and must NOT share a cluster with
    the v8 hero slot.
    """

    payload = _v8_for_artifact(
        "backend/tests/_artifacts/natal_interpret_full_1998-09-12_07-30_adana_user_compact_debug.json"
    )
    v8 = payload["v8"]
    pid_to_cluster = payload["pid_to_cluster"]

    hero_packet_id = _slot_packet_id(v8["hero"])
    identity_packet_id = _slot_packet_id(v8["identity_axis"])

    hero_cluster = pid_to_cluster.get(hero_packet_id)
    identity_cluster = pid_to_cluster.get(identity_packet_id)

    # The bug guard: the old mind fallback must not resurface.
    assert identity_packet_id != "mercury_virgo_12h_private_analytical_mind_chart_exact", (
        "v8 identity_axis must not fall back to the Mercury Virgo 12H mind packet "
        "when an identity-family cluster exists in the plan."
    )

    # Identity cluster must be from the identity-family.
    assert identity_cluster is not None, (
        f"identity_axis packet {identity_packet_id!r} has no cluster mapping in the plan"
    )
    assert identity_cluster.startswith("identity_"), (
        f"v8 identity_axis cluster must be identity-family; got {identity_cluster!r}"
    )

    # Adana-specific target: the pure-identity Libra ASC + Venus chart-ruler cluster.
    assert identity_cluster == (
        "identity_identity_like_libra_asc_venus_chart_ruler_chart_exact"
    ), (
        f"Adana v8 identity_axis should resolve to the chart-ruler identity cluster; "
        f"got {identity_cluster!r}"
    )

    # Hero and identity_axis must come from distinct clusters.
    assert hero_cluster and hero_cluster != identity_cluster, (
        f"hero and identity_axis must be different clusters; "
        f"hero={hero_cluster!r}, identity_axis={identity_cluster!r}"
    )


def test_istanbul_v8_identity_axis_unchanged_or_strictly_better() -> None:
    """Istanbul guard: the new identity-axis preference must not regress
    Istanbul. Pre-fix the v8 identity_axis was
    ``saturn_3h_aries_speech_decision_language_chart_exact`` (mind family).
    After the fix the slot may stay the same OR shift to a strictly better
    identity-family cluster (mind → identity-family is strictly better per
    the rule). It must NOT fall outside the identity-family if any
    identity-family cluster sits in Istanbul's plan, and it must not
    collide with the hero cluster.
    """

    payload = _v8_for_artifact(
        "backend/tests/_artifacts/natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json"
    )
    v8 = payload["v8"]
    pid_to_cluster = payload["pid_to_cluster"]
    plan = payload["plan"]

    hero_packet_id = _slot_packet_id(v8["hero"])
    identity_packet_id = _slot_packet_id(v8["identity_axis"])

    hero_cluster = pid_to_cluster.get(hero_packet_id) or ""
    identity_cluster = pid_to_cluster.get(identity_packet_id) or ""

    plan_has_identity_cluster = any(
        str(cluster.get("id") or "").startswith("identity_")
        for cluster in plan.get("clusters") or []
    )

    if plan_has_identity_cluster:
        # The prior surface was mind-family; the fix must promote it.
        assert identity_cluster.startswith("identity_"), (
            f"Istanbul v8 identity_axis must surface an identity-family cluster "
            f"now that the new rule is active; got {identity_cluster!r}"
        )
    else:
        # Defensive: if Istanbul ever loses every identity-family cluster,
        # the legacy layer-preference fallback must still produce a slot.
        assert identity_packet_id, "identity_axis must always produce a node"

    # No cluster overlap with hero.
    assert identity_cluster != hero_cluster or not hero_cluster, (
        f"hero / identity_axis cluster collision: {hero_cluster!r}"
    )


# ---------------------------------------------------------------------------
# Adana copy-polish pass regressions.
# See docs/system/adana_cluster_plan_audit_after_v0_3_final.md §7 for the
# four polish items handled below:
#   1. mc_cancer career body opener + chip dedup.
#   2. venus_square_pluto body opener (literal aspect + motif → lived voice).
#   3. mars_leo_11h community variant chip label (was "İçgörü" → "Topluluk").
#   4. ``_smart_clip`` must not leave a dangling ``\d+\.`` fragment when it
#      cuts mid-sentence inside a numbered-house abbreviation.
# ---------------------------------------------------------------------------


def _narrative_for_artifact(artifact_path: str) -> dict:
    import json
    from pathlib import Path

    from app.natal.natal_promise_packets import build_natal_promise_packets_v1
    from app.natal.natal_promise_cluster_plan import build_natal_promise_cluster_plan_v1

    artifact = json.loads(Path(artifact_path).read_text(encoding="utf-8"))

    def _walk(payload, *, key):
        if isinstance(payload, dict):
            if key in payload:
                yield payload[key]
            for value in payload.values():
                yield from _walk(value, key=key)
        elif isinstance(payload, list):
            for item in payload:
                yield from _walk(item, key=key)

    sections = next(iter(_walk(artifact, key="sections_v2")), [])
    threads = next(iter(_walk(artifact, key="supporting_threads")), [])
    planets = artifact.get("planets") or next(iter(_walk(artifact, key="planets")), [])
    aspects = artifact.get("aspects") or next(iter(_walk(artifact, key="aspects")), [])
    natal_graph_compact = (
        artifact.get("natal_graph_compact")
        or next(iter(_walk(artifact, key="natal_graph_compact")), {})
    )
    metadata = artifact.get("metadata") or {}
    meta_info = artifact.get("meta_info") or {}

    inventory = build_natal_promise_packets_v1(
        sections_v2=sections, supporting_threads=threads,
        planets=planets, aspects=aspects, natal_graph_compact=natal_graph_compact,
        metadata=metadata, meta_info=meta_info, locale="tr", mode="candidate_inventory",
    )
    selected = build_natal_promise_packets_v1(
        sections_v2=sections, supporting_threads=threads,
        planets=planets, aspects=aspects, natal_graph_compact=natal_graph_compact,
        metadata=metadata, meta_info=meta_info, locale="tr", mode="selected",
    )
    plan = build_natal_promise_cluster_plan_v1(inventory.get("packets") or [])
    return build_profile_narrative_projection_v1(
        meaning_graph_v1_1={"version": "meaning_graph_v1_1", "nodes": [], "evidence": []},
        natal_promise_packets_v1=selected,
        natal_promise_cluster_plan_v1=plan,
        include_packet_debug=True,
    )


def _adana_blocks() -> tuple[list, list]:
    narrative = _narrative_for_artifact(
        "backend/tests/_artifacts/natal_interpret_full_1998-09-12_07-30_adana_user_compact_debug.json"
    )
    public = narrative.get("profile_public") or {}
    return list(public.get("core_blocks") or []), list(public.get("extra_blocks") or [])


def _find_block(blocks: list, suffix: str):
    for block in blocks:
        if str(block.get("node_id") or "").endswith(suffix):
            return block
    return None


def test_adana_mc_cancer_body_opener_and_chip_dedup() -> None:
    """Polish #1: the mc_cancer career packet must use the bespoke body
    opener that names MC Yengeç + Ay 9. ev İkizler once each (no
    chip-fragment substitution, no "Yengeç…Yengeç'te" double-anchor), and
    the three chip slots must be non-overlapping."""

    core, _ = _adana_blocks()
    block = _find_block(core, "mc_cancer_moon_gemini_9h_teaching_voice_chart_exact")
    assert block is not None, "mc_cancer chart_exact career block missing from Adana core"

    body = str(block.get("body") or "")
    # New opener (user-supplied verbatim).
    assert body.startswith("Kariyer hattının Yengeç'te, yöneticisi Ay'ın da 9. evde İkizler'de olması"), (
        f"mc_cancer body opener regressed: {body[:120]!r}"
    )
    # Old defect markers must NOT reappear.
    assert "Yengeç · Ay 9. ev İkizler olması kadar" not in body
    assert "Kariyer hattının Yengeç'te olması de bu hattın karakterini" not in body

    chips = list(block.get("chips") or [])
    assert chips[:3] == ["Kariyer", "MC Yengeç", "Ay 9. ev İkizler"], (
        f"mc_cancer chips not deduped to three non-overlapping labels: {chips!r}"
    )


def test_adana_venus_square_pluto_body_opener_is_bespoke() -> None:
    """Polish #2: the venus_square_pluto packet must use the bespoke
    body opener that describes the square in lived voice, not the
    auto-built ``"Venüs kare Plüton ve Yoğun çekim aynı çizgiyi
    güçlendiriyor"`` template."""

    core, _ = _adana_blocks()
    block = _find_block(core, "venus_square_pluto_intense_love_chart_exact")
    assert block is not None, "venus_square_pluto chart_exact relationship block missing"

    body = str(block.get("body") or "")
    assert body.startswith("Venüs'ün Plüton'la kare çalışması, ilişkilerde çekimi"), (
        f"venus_pluto bespoke body opener regressed: {body[:120]!r}"
    )
    # The literal aspect-chip joiner must not reappear in the body.
    assert "Venüs kare Plüton ve Yoğun çekim aynı çizgiyi" not in body


def test_adana_mars_leo_11h_community_chip_label() -> None:
    """Polish #3: the mars_leo_11h community variant's first chip must
    surface a topluluk-context label ("Topluluk"), not the
    ``İçgörü`` fallback used when ``community`` was missing from the
    domain → label mapping."""

    _, extras = _adana_blocks()
    block = _find_block(extras, "mars_leo_11h_warm_visible_drive_community_chart_exact")
    assert block is not None, "mars_leo_11h community variant missing from Adana extras"
    chips = list(block.get("chips") or [])
    assert chips and chips[0] == "Topluluk", (
        f"community variant chip[0] must be 'Topluluk', got: {chips!r}"
    )
    assert chips[0] != "İçgörü"


def test_smart_clip_protects_numbered_house_abbreviation() -> None:
    """Polish #4: ``_smart_clip`` must not treat the period in a
    ``<digit>. ev`` / ``<digit>. evde`` abbreviation as a sentence
    terminator. Previously this left a dangling ``"7."`` at the tail of a
    clipped teaser whenever the budget cut mid-sentence inside a
    numbered-house phrase."""
    from app.meaning.projection_shadow_v1_builder import _smart_clip

    text = (
        "Sen ilişkide sadece biriyle olmak istemiyorsun. "
        "Senin aradığın şey, yanında fazla dolanmadan açık olabildiğin bir bağ. "
        "7. evin Koç olduğu için ilişkide netlik, cesaret ve doğrudanlık senin için çok şey belirliyor."
    )
    clipped = _smart_clip(text, 180)
    # Must NOT end with a bare numbered-house fragment ("...bir bağ. 7." or similar).
    assert not re.search(r"\b\d+\.\s*…?\s*$", clipped), (
        f"_smart_clip left a dangling numbered-house fragment: {clipped!r}"
    )
    # The clipped result must still end at a real sentence boundary.
    assert clipped.endswith("."), f"_smart_clip should end at a sentence boundary, got {clipped!r}"
    # Sanity: the period inside ``7. ev`` survives elsewhere in the codebase
    # — the variants ``12. evde``, ``1. evin`` must also be protected.
    for label in ("12. evde", "1. evin", "9. evdeki"):
        snippet = f"İlk cümle. {label} Aslan olduğu için bunu hızlı sezersin."
        out = _smart_clip(snippet, len("İlk cümle. ") + 4)  # forces a cut mid-token
        assert not re.search(r"\b\d+\.\s*…?\s*$", out), (
            f"_smart_clip left a dangling fragment for {label!r}: {out!r}"
        )


def test_adana_extras_no_dangling_numbered_house_fragments() -> None:
    """End-to-end regression for polish #4: no Adana teaser/body/micro
    may end with a bare ``\\d+\\.`` token."""
    core, extras = _adana_blocks()
    pattern = re.compile(r"\b\d+\.\s*…?\s*$")
    for block in [*core, *extras]:
        for field in ("teaser", "body", "micro"):
            value = str(block.get(field) or "").rstrip()
            if not value:
                continue
            assert not pattern.search(value), (
                f"dangling numbered-house fragment in {block.get('node_id')} {field}: "
                f"...{value[-80:]!r}"
            )


# ---------------------------------------------------------------------------
# Adana §8 copy-style naturalization pass regressions.
# See docs/system/adana_cluster_plan_audit_after_v0_3_final.md §8 for the
# bespoke per-packet overrides plus the chip-format / English-label
# backstop helper.
# ---------------------------------------------------------------------------


def test_adana_bodies_have_no_chip_format_separator() -> None:
    """§8 polish: the chip-format ``·`` separator must never appear inside
    a body / teaser / micro string. It belongs in chip arrays only."""

    core, extras = _adana_blocks()
    for block in [*core, *extras]:
        for field in ("body", "teaser", "micro"):
            value = str(block.get(field) or "")
            assert "·" not in value, (
                f"chip-format `·` leaked into {block.get('node_id')} {field}: {value[:160]!r}"
            )


def test_adana_bodies_have_no_public_maturity_english_label() -> None:
    """§8 polish: the English internal label ``Public maturity`` from the
    saturn_taurus_8h packet must never survive into a rendered body."""

    core, extras = _adana_blocks()
    for block in [*core, *extras]:
        for field in ("body", "teaser", "micro", "headline"):
            value = str(block.get(field) or "")
            assert "Public maturity" not in value, (
                f"English label `Public maturity` leaked into {block.get('node_id')} {field}: {value[:160]!r}"
            )
            assert "public maturity" not in value, (
                f"English label `public maturity` leaked into {block.get('node_id')} {field}: {value[:160]!r}"
            )


def test_adana_mars_leo_11h_community_vs_relationship_bodies_diverge() -> None:
    """§8 polish (E): the community-variant and the relationship-variant
    bodies must not share any substring longer than 40 chars. They share a
    match_id and previously ran through the same template, producing a
    near-duplicate mid-body sentence about ``topluluklar veya ortak
    idealler içinde görünür olma...``. The bespoke overrides separate
    them."""

    _, extras = _adana_blocks()
    comm = _find_block(extras, "mars_leo_11h_warm_visible_drive_community_chart_exact")
    rel = _find_block(extras, "mars_leo_11h_warm_visible_drive_chart_exact")
    assert comm is not None, "mars_leo_11h community variant missing from Adana extras"
    assert rel is not None, "mars_leo_11h relationship variant missing from Adana extras"

    a = str(comm.get("body") or "")
    b = str(rel.get("body") or "")

    # Longest common substring via DP. Bound is 40 chars (any phrase longer
    # than that signals the two variants are still sharing template prose).
    la, lb = len(a), len(b)
    dp = [[0] * (lb + 1) for _ in range(la + 1)]
    longest = 0
    for i in range(la):
        for j in range(lb):
            if a[i] == b[j]:
                dp[i + 1][j + 1] = dp[i][j] + 1
                if dp[i + 1][j + 1] > longest:
                    longest = dp[i + 1][j + 1]
    assert longest < 40, (
        f"mars_leo_11h community vs relationship bodies still share a "
        f"{longest}-char substring; they must diverge after §8."
    )
