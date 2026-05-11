from __future__ import annotations

import json
from pathlib import Path

from app.narrative.voice_guardrails_tr import (
    CONTENT_SCAN_PATHS,
    find_forbidden_public_copy_issues,
    find_technical_leakage,
    iter_content_scan_paths,
    load_json_baseline,
    validate_olabilir_usage,
    validate_pattern_name,
    validate_rotation_pair,
)


def test_content_scan_paths_exist() -> None:
    for path in iter_content_scan_paths(Path(".")):
        assert path.exists(), f"guardrail content scan target missing: {path}"


def test_hard_banned_public_copy_words_are_detected() -> None:
    issues = find_forbidden_public_copy_issues("Bu mekanizma aktivasyon gibi çalışan bir proses.")
    codes = {issue["code"] for issue in issues}
    assert "hard_banned_word" in codes
    assert len([issue for issue in issues if issue["code"] == "hard_banned_word"]) == 3


def test_scaffold_patterns_are_detected_but_natural_exemptions_pass() -> None:
    banned = find_forbidden_public_copy_issues("Buradaki eşik aslında bu süreç içinde görünür oluyor.")
    banned_codes = {issue["code"] for issue in banned}
    assert "buradaki_esik" in banned_codes
    assert "bu_surec_scaffold" in banned_codes

    exempt = find_forbidden_public_copy_issues("Kapının eşiğinde dururken aile dinamiği de görünür olabilir.")
    exempt_codes = {issue["code"] for issue in exempt}
    assert "buradaki_esik" not in exempt_codes
    assert "bu_dinamik_scaffold" not in exempt_codes


def test_technical_leakage_is_detected_in_public_body() -> None:
    issues = find_technical_leakage(
        "Bugün 3. ev tarafında Satürn ve Koç etkisi transit gibi çalışıyor; orb dar.",
        surface="body",
    )
    codes = {issue["code"] for issue in issues}
    assert "house_number" in codes
    assert "planet_name" in codes
    assert "sign_name" in codes
    assert "transit_word" in codes
    assert "orb_word" in codes


def test_technical_references_are_allowed_in_proof_and_debug() -> None:
    proof_issues = find_technical_leakage("Satürn · 3. ev · Oğlak", surface="proof")
    debug_issues = find_technical_leakage("Transit orb 0.6 ve kare açı", surface="debug")
    assert proof_issues == []
    assert debug_issues == []


def test_bad_pattern_names_fail_and_good_pattern_names_pass() -> None:
    bad_names = [
        "Ay-Merkür gerilimi",
        "12. ev projeksiyonu",
        "mükemmeliyetçilik",
        "Satürnyen disiplin",
        "Kaçınmacı bağlanma stili",
    ]
    for name in bad_names:
        assert validate_pattern_name(name), f"expected bad pattern name to fail: {name}"

    good_names = [
        "entelektüel savunma",
        "perde arkası çalışma",
        "titiz estetik zeka",
    ]
    for name in good_names:
        assert validate_pattern_name(name) == [], f"expected good pattern name to pass: {name}"


def test_olabilir_rule_is_refined_by_layer() -> None:
    assert validate_olabilir_usage("Bu çizgi bazen daha görünür olabilir.", layer="cause") == []
    assert validate_olabilir_usage("Dışarıdan daha ciddi görünebilirsin.", layer="effect") == []
    assert validate_olabilir_usage("Bu bazen daha ağır hissedilebilir.", layer="shadow") == []

    mechanism_issues = validate_olabilir_usage("Bu hat böyle çalışıyor olabilir.", layer="mechanism")
    potential_issues = validate_olabilir_usage("Buradan daha görünür olabilirsin.", layer="potential")
    assert mechanism_issues
    assert potential_issues


def test_rotation_rule_catches_repeated_bu_donem_opening() -> None:
    issues = validate_rotation_pair(
        "Bu dönem ilişkilerde sınır konusu daha görünür oluyor.",
        "Bu dönem iş tarafında daha net bir seçim yapıyorsun.",
    )
    assert issues
    assert issues[0]["code"] == "repeated_bu_donem_opening"


def test_directive_verbs_are_detected() -> None:
    issues = find_forbidden_public_copy_issues("Şimdi bunu yap, hemen uygula; bu sana gerekli.")
    codes = {issue["code"] for issue in issues}
    assert "directive_yap" in codes
    assert "directive_uygula" in codes
    assert "directive_gerekli" in codes


def test_pr_0_5_daily_baseline_is_caught_by_guardrails() -> None:
    baseline = load_json_baseline("backend/tests/baselines/daily_legacy_baseline_2026_05_03.json")
    issues = [
        *find_technical_leakage(baseline["body"], surface="body"),
        *find_forbidden_public_copy_issues(baseline["body"], check_directives=False),
        *validate_olabilir_usage(baseline["body"], layer=baseline["layer"]),
    ]
    codes = {issue["code"] for issue in issues}
    assert "house_number" in codes
    assert "hedge_forbidden_in_layer" in codes
    assert "run_on_sentence_transition" in codes


def test_handcrafted_validation_answer_key_exposes_valence_and_intensity() -> None:
    payload = json.loads(
        Path("docs/voice/handcrafted_validation_answer_key.json").read_text(encoding="utf-8")
    )
    cases = payload["cases"]
    assert len(cases) == 5
    for case in cases:
        assert "runtime_source_metadata" in case
        assert case["target_valence_mode"]
        assert case["target_intensity_mode"]


def test_handcrafted_validation_pack_passes_vnext_guardrails() -> None:
    payload = json.loads(
        Path("docs/voice/handcrafted_validation_answer_key.json").read_text(encoding="utf-8")
    )
    for case in payload["cases"]:
        for variant in case["variants"].values():
            text = variant["body"]
            assert find_forbidden_public_copy_issues(text) == []
            assert find_technical_leakage(text, surface="body") == []
            assert validate_olabilir_usage(text, layer="mechanism") == []
            assert validate_olabilir_usage(text, layer="potential") == []


def test_vnext_spec_includes_period_aspect_texture_section() -> None:
    text = Path("docs/voice/SHOU_VOICE_VNEXT.md").read_text(encoding="utf-8")
    assert "## 22. Period Aspect Texture: Valence + Intensity" in text
    assert "planet pair + aspect type + natal backing + chapter role" in text
    assert "dense + integration" in text.lower()
    assert "light + opening" in text.lower()
    assert "light + recognition" in text.lower()
    assert "medium + maturation" in text.lower()
    assert "light + release" in text.lower()
    assert "dense + tension" in text.lower()
