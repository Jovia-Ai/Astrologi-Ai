"""Test ortamı için ortak setup.

Üretim ortamında `app.main.create_app()` Swiss Ephemeris path'ini
`swe.set_ephe_path(settings.swisseph_path)` ile set eder. Test'ler
`create_app()` çağırmadan doğrudan route fonksiyonlarını çalıştırdığı için
bu init kaçıyor — Chiron, Juno, Vesta gibi extended bodies sistem
default path'inde bulunamıyor (`/usr/share/swisseph/...`) ve hesaplama
başarısız oluyor.

Bu conftest tüm test session'ı boyunca production-equivalent path'i set eder.
Aksi halde snapshot test'leri production'dan farklı (eksik) çıktı üretir.
"""
from __future__ import annotations

import swisseph as swe

from app.core.config import settings


def pytest_configure(config) -> None:  # noqa: ARG001
    swe.set_ephe_path(settings.swisseph_path)
