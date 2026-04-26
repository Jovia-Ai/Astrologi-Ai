"""Voice Tuning Sprint 1 — phrase-level lint guards.

Source: docs/system/projection_voice_tuning_gap_audit.md (phrase-level items only).

Bu test, audit tarafından temizlenmiş ifadelerin profile narrative + v8 projection
katmanına geri sızmadığını doğrular. Yalnızca **kaynak kod metni** üzerinde lint
yapılır — runtime çıktısı değil. Sebep:

* Pattern/template değişikliği yapmıyoruz; metnin koddaki sabit string olarak
  yer almasını engellemek yeterli.
* Snapshot baseline'ı (test_natal_v8_baseline_snapshot) runtime düzeyinde
  diff'i zaten yakalar.

Eğer Sprint 1'de temizlenen bir ifade tekrar koda geri girerse bu test düşer.
Yeni audit kategorilerine ait ifadeler buraya **eklenmemelidir** (pattern-level
ve semantic-enrichment maddeleri ayrı sprintlerde ele alınacak).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

# Bu lint kapsamına giren projection katmanı dosyaları. Selection ve UI
# orchestration kapsam DIŞI — yalnızca natal projection rendering yüzeyleri.
_PROJECTION_FILES = (
    Path("backend/app/natal/narrative/phrase_lib_tr_profile.py"),
    Path("backend/app/natal/narrative/profile_narrative_engine_signature.py"),
    Path("backend/app/natal/profile_v8_payload_builder.py"),
    Path("backend/app/narrative/humanize_tr.py"),
    Path("backend/app/narrative/editorial_render_policy.py"),
)

_REPO_ROOT = Path(__file__).resolve().parents[2]


# Sprint 1 phrase-level forbidden list. Her giriş:
#   (label, regex, expected_count, audit_category)
# expected_count = 0 → metin tamamen yok edilmeli.
# expected_count > 0 → kontrollü cleanup-rule olarak korunan satır var
#                      (örn. legacy text'i yeni forma çeviren regex hattı).
_FORBIDDEN: tuple[tuple[str, str, int, str], ...] = (
    # 2.1 calque
    ("yerine_oturdugunda_calque", r"\bYerine oturduğunda\b", 1, "phrase-level"),
    # 2.2 engineering colon
    ("ic_tarafta_isleyis", r"İç tarafta işleyiş şöyle", 0, "phrase-level"),
    # 2.4 biological metaphor
    ("damar_metaphor_profile", r"birden fazla damar aynı anda çalışıyor", 0, "phrase-level"),
    # 2.5 corporate jargon
    ("ic_standart_jargon", r"\biç standart\b", 0, "phrase-level"),
    ("ic_standardin_jargon", r"\biç standardın\b", 0, "phrase-level"),
    # 3.1 reward verb
    ("kazandirir_profile_gift", r"bir duruş kazandırır", 0, "phrase-level"),
    ("kazandirir_profile_ifade", r"berrak bir ifade kazandırır", 0, "phrase-level"),
    ("kazandirir_olgunlasinca_netlik", r"olgunlaştığında sana netlik ve istikrar kazandırır", 0, "phrase-level"),
    ("kazandirir_olgunlasinca_dayaniklilik", r"sana dayanıklılık ve güven veren bir netlik kazandırır", 0, "phrase-level"),
    ("kazandirir_priority_duris", r"taklit edilemeyen bir duruş kazandırır", 0, "phrase-level"),
    ("kazandirir_priority_etki", r"ufku geniş bir etki kazandırır", 0, "phrase-level"),
    # 3.4 empty verb
    ("etkiliyor_savunma", r"savunma gücünü etkiliyor", 0, "phrase-level"),
    # 3.6 generic affirmation
    ("anlamli_akis_buluyor", r"anlamlı bir akış buluyor", 0, "phrase-level"),
    # 5.1 coaching prescription
    ("buyume_tarafini_hizlandirir", r"büyüme tarafını hızlandırır", 0, "phrase-level"),
    # 5.2 life-as-coach
    ("hayat_seni_buyutuyor", r"Hayat seni .*?büyütüyor", 0, "phrase-level"),
    # 5.3 startup jargon
    ("olceklenebilen_zihin", r"ölçeklenebilen bir zihin", 0, "phrase-level"),
    # 5.4 competitive coaching
    ("onsezi_avantaji_veriyor", r"önsezi avantajı veriyor", 0, "phrase-level"),
    # 5.5 TED-talk pep
    ("donum_noktasi_olabilirsin", r"dönüm noktası olabilirsin", 0, "phrase-level"),
)


def _read_projection_corpus() -> str:
    parts: list[str] = []
    for relative in _PROJECTION_FILES:
        full = _REPO_ROOT / relative
        assert full.exists(), f"projection lint hedefi bulunamadı: {relative}"
        parts.append(full.read_text(encoding="utf-8"))
    return "\n\n".join(parts)


@pytest.mark.parametrize(
    ("label", "pattern", "expected_count", "category"),
    _FORBIDDEN,
    ids=[item[0] for item in _FORBIDDEN],
)
def test_projection_forbidden_phrase_count(
    label: str, pattern: str, expected_count: int, category: str
) -> None:
    """Sprint 1 phrase-level audit maddelerinin geri dönmediğini doğrular."""
    corpus = _read_projection_corpus()
    matches = list(re.finditer(pattern, corpus, flags=re.IGNORECASE))
    actual = len(matches)
    assert actual == expected_count, (
        f"phrase lint drift: {label} (kategori: {category})\n"
        f"  pattern={pattern!r}\n"
        f"  beklenen sayı={expected_count}, bulundu={actual}\n"
        f"  audit kaynağı: docs/system/projection_voice_tuning_gap_audit.md"
    )


def test_projection_lint_corpus_is_non_empty() -> None:
    """Lint hedef dosyaları yer değiştirirse / boşalırsa hatası."""
    corpus = _read_projection_corpus()
    assert len(corpus) > 5000, "projection lint corpus beklenmeyen şekilde küçük"


def test_yerine_oturdugunda_only_in_legacy_cleanup() -> None:
    """`Yerine oturduğunda` artık sadece legacy temizleme regex'inde olmalı.

    Sprint 1 ile bu calque tüm template/copy yüzeylerinden çıkarıldı; yalnızca
    `humanize_tr.py` içindeki cleanup regex satırı bu phrase'i tanıyıp yeni
    forma çeviriyor. Başka herhangi bir yerde geri görünürse drift demektir.
    """
    legacy_cleanup_path = _REPO_ROOT / "backend/app/narrative/humanize_tr.py"
    legacy_text = legacy_cleanup_path.read_text(encoding="utf-8")
    legacy_count = len(re.findall(r"Yerine oturduğunda", legacy_text))
    # humanize_tr.py'da: 2 cleanup regex satırı (ham phrase + duplicate-connector)
    assert legacy_count == 2, (
        f"humanize_tr.py içinde 'Yerine oturduğunda' beklenen sayı 2, bulundu {legacy_count}"
    )

    other_files = (
        _REPO_ROOT / "backend/app/natal/narrative/phrase_lib_tr_profile.py",
        _REPO_ROOT / "backend/app/natal/narrative/profile_narrative_engine_signature.py",
        _REPO_ROOT / "backend/app/natal/profile_v8_payload_builder.py",
        _REPO_ROOT / "backend/app/narrative/editorial_render_policy.py",
    )
    for path in other_files:
        text = path.read_text(encoding="utf-8")
        assert "Yerine oturduğunda" not in text, (
            f"calque sızdı: {path.relative_to(_REPO_ROOT)}"
        )
