# Astrologi AI — Claude Code Kuralları

## Proje yapısı

### Genel
```
Astrologi-Ai/
├── backend/          # Python / FastAPI
├── mobile/           # Flutter / Dart
├── config/           # YAML konfigürasyonları (tone, ontology, transit, scoring)
├── docs/             # Mimari belgeler, ürün spec'leri
├── scripts/          # Otomasyon ve setup scriptleri
└── render.yaml       # Render.com deployment config
```

### Mobile (Flutter)
- **State management**: Riverpod 2.5.1 — `NotifierProvider` pattern
- **Router**: go_router 14.8.1 — `/mobile/lib/app/app_router.dart`
- **Auth**: Supabase Auth (JWT) → `AuthGate` → `BirthDataGate` → `/tabs`
- **HTTP client**: Dio 5.7.0 — SLA bazlı timeout (fast 3s / interactive 8s / background 18s), request coalescing
- **i18n**: Flutter intl — Türkçe (`tr`) ve İngilizce (`en`) — `.arb` dosyalarından
- **SDK**: Dart 3.11.0+, Material 3
- **Önemli bağımlılıklar**: `supabase_flutter`, `purchases_flutter` (RevenueCat), `flutter_svg`

### Mobile sayfa yapısı (`/mobile/lib/app/tabs/`)
| Dosya | Amaç |
|---|---|
| `home_page.dart` | Ana dashboard — transit/event özeti |
| `profile_page.dart` | Kullanıcı profili + arketip detayları |
| `profile_detail_flow_page.dart` | Derin profil analizi akışı |
| `calendar_hub_page.dart` | Transit takvimi UI |
| `bond_page.dart` / `bond_result_page.dart` | Sinastri / ilişki analizi |
| `ai_page.dart` | AI sohbet arayüzü |
| `story_studio_page.dart` | Hikaye üretimi |
| `forum_page.dart` | Topluluk forumu |
| `sky_event_feed_page.dart` | Astronomik olaylar akışı |

### Backend (FastAPI)
- **Entry point**: `backend/app/main.py`
- **Config**: `backend/app/core/config.py` — Pydantic v2 Settings
- **Deployment**: Render.com (`render.yaml`)
- **Astroloji motoru**: PySwissEph 2.10.3.2 + ephe/ veri dizini
- **LLM**: Groq (LLaMA 3.1-8b-instant) → OpenAI fallback → yerel LLaMA

### Backend router yapısı
```
app/routers/          → charts, health, user, chat, profile, revenuecat, story, synastry
app/api/routes/       → natal_interpretation, transits, home, sky
app/services/         → supabase, profiles, chart_service, ai_chat, stories, performance/
app/astro/            → Swiss Ephemeris tabanlı hesaplamalar
app/transit/          → Gezegensel transit hesaplamaları
app/synastry/         → İlişki uyumu analizi
app/ai/ + app/engine/ → LLM entegrasyonu, narrative builder'lar
```

### Caching katmanları
1. **Mobile**: In-memory response cache (TTL tabanlı)
2. **Backend fast cache**: TTL 30 dakika (home page)
3. **Backend deep cache**: TTL 2 saat (detaylı profil)
4. **Strateji**: Stale-while-revalidate + background refresh
5. **Backend**: Memory (default) veya Redis backend

---

## Tasarım dili

- **Renk paleti**: Beyaz/kırık beyaz arka plan, lime green (`#CAFF4D` civarı) accent
- **Tipografi**: Editorial, büyük başlıklar, bold kontrast
- **Amber/sıcak ton KULLANMA** — bu markaya aykırı
- **Klasik astroloji görselleri KULLANMA**
- **Design token'lar**: `/docs/visual-system/` belgelerine bak
- **Asset'ler**: `ios/Flutter/assets/` — SVG formatında (illustrations, planets, logo, elements)

---

## Animasyon standartları

- **Tercih edilen eğriler**: `Curves.easeOutCubic`, `Curves.easeInOutCubic`
- **Sayfa geçişleri**: 300–400ms
- **Micro-interaction**: 150–250ms
- **Spring efektleri**: Özel `TweenSequence` ile — harici paket EKLEME
- **Stagger delay**: `index * 60ms`

---

## Değişiklik yaparken

1. Dosyayı önce **OKU**
2. Mevcut yapıyı koru — refactor yapma
3. Sadece istenen bileşeni değiştir
4. Değiştirilen dosyaları listele
5. Yeni Flutter paketi gerekiyorsa önce **sor** (`pubspec.yaml`'a dokunma)

---

## Kesinlikle dokunma

### Mobile
- `lib/design/theme/` klasörü
- `lib/main.dart`
- `lib/app/app_router.dart` (go_router config)
- Tüm Riverpod provider tanımları (state management)
- `pubspec.yaml` (izin almadan yeni paket ekleme)

### Backend
- `backend/app/core/config.py` — izin almadan değiştirme
- `backend/app/main.py` — izin almadan değiştirme
- `backend/ephe/` — Swiss Ephemeris veri dosyaları
- `.env` dosyası — secret'lara dokunma

---

## Onay gerektiren durumlar

- Yeni Flutter paketi eklemek
- Yeni Python bağımlılığı eklemek
- Mevcut bir widget'ı veya servisi tamamen yeniden yazmak
- Navigation flow'u değiştirmek
- Supabase şema değişikliği
- Caching stratejisini değiştirmek
- Yeni bir API endpoint'i eklemek

---

## Önemli dosya konumları

| Amaç | Konum |
|---|---|
| GoRouter config | `mobile/lib/app/app_router.dart` |
| API client | `mobile/lib/app/api/api_client.dart` |
| Auth gate | `mobile/lib/app/auth/auth_gate.dart` |
| App preferences | `mobile/lib/app/preferences/` |
| Localization | `mobile/lib/l10n/` |
| FastAPI entry | `backend/app/main.py` |
| Backend config | `backend/app/core/config.py` |
| Transit routes | `backend/app/api/routes/transits.py` |
| Natal routes | `backend/app/api/routes/natal_interpretation.py` |
| Cache store | `backend/app/services/performance/cache_store.py` |
| Tone/ontology config | `config/tone/tone.yaml`, `config/ontology/` |
| Mimari belgeler | `docs/current_architecture.md` |

---

## Test yapısı

- **Backend testler**: `backend/tests/` — 53 test dosyası
- **Mobile testler**: `mobile/test/`
- Backend test komutu: `pytest` (backend/ dizininden)
- Test isimlendirme: `test_<konu>_<senaryo>.py`

---

## Deployment

- **Platform**: Render.com
- **Config**: `render.yaml` (proje root'unda)
- **Build**: `pip install -r backend/requirements.txt`
- **Start**: `PYTHONPATH=backend python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **CI/CD**: Manuel deploy (GitHub Actions yok)

