"""Test ortamı için ortak setup.

Üretim ortamında `app.main.create_app()` Swiss Ephemeris path'ini
`swe.set_ephe_path(settings.swisseph_path)` ile set eder. Test'ler
`create_app()` çağırmadan doğrudan route fonksiyonlarını çalıştırdığı için
bu init kaçıyor — Chiron, Juno, Vesta gibi extended bodies sistem
default path'inde bulunamıyor (`/usr/share/swisseph/...`) ve hesaplama
başarısız oluyor.

Bu conftest tüm test session'ı boyunca production-equivalent path'i set eder.
Aksi halde snapshot test'leri production'dan farklı (eksik) çıktı üretir.

Ek olarak `PYTHONHASHSEED` set edilmemişse process'i deterministik bir hash
seed (0) ile yeniden başlatır. Sebep: natal interpretation pipeline'ında
bir veya birden çok yerde `set` / hash-order'a duyarlı iterasyon, aynı
fixture için iki pytest process arasında farklı `core_story` çıktısına yol
açıyor (`fix01_leo_leo_classic` paragraph 3 fallback path'i en görünür
örnek). Bu non-determinism baseline snapshot suite'inde test-ordering flake
gibi göründü; gerçekte process-bazlı hash randomization. Detaylar için
bkz. `docs/system/projection_voice_tuning_gap_audit.md` ve fix01 araştırma
raporu. Bu hook üretim koduna dokunmaz, yalnızca test launch'unu sabitler.
"""
from __future__ import annotations

import os
import subprocess
import sys

# Sentinel kontrol: re-exec sonsuz döngüye girmemesi için marker bırakırız.
# `PYTHONHASHSEED` kontrolü yeterli ama explicit guard güvenlik sağlar.
# `random` veya boş değer hâlâ deterministik değil — gerçek pin için bir
# integer string bekleriz.
_HASHSEED_GUARD = "_ASTROLOGI_TESTS_PYTHONHASHSEED_PINNED"
_existing_seed = os.environ.get("PYTHONHASHSEED")
_seed_is_pinned = bool(_existing_seed) and _existing_seed.lower() != "random"
if not _seed_is_pinned and os.environ.get(_HASHSEED_GUARD) is None:
    # Aynı argv ile yeniden başlat. Subprocess yaklaşımı, execvp ile bazı
    # shell wrapper'larında stdout pipe kaybolması probleminden kaçınır.
    new_env = os.environ.copy()
    new_env["PYTHONHASHSEED"] = "0"
    new_env[_HASHSEED_GUARD] = "1"
    result = subprocess.run(sys.argv, env=new_env)
    sys.exit(result.returncode)

import swisseph as swe  # noqa: E402

from app.core.config import settings  # noqa: E402


def pytest_configure(config) -> None:  # noqa: ARG001
    swe.set_ephe_path(settings.swisseph_path)
