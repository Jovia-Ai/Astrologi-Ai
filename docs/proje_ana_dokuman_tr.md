# Astrologi-AI Proje Ana Dokümanı (Güncel Durum)

Son güncelleme: 2026-04-17  
Kapsam: Monorepo içindeki mevcut kod tabanına göre hazırlanmıştır.

## 1) Projenin Vizyonu ve Amacı

Astrologi-AI; astrolojik hesaplamaları, kural tabanlı yorumlama altyapısını ve AI destekli anlatımı birleştirerek kişiye özel dijital astroloji deneyimi sunmayı hedefleyen bir platformdur.

Ürün vizyonu:
- Doğum verisini teknik hesaplamadan kullanıcıya anlaşılır içgörüye dönüştürmek.
- Ücretsiz ve premium deneyimi net ayırmak.
- Mobilde hızlı, güvenilir ve ölçeklenebilir bir astrolog-asistan deneyimi sağlamak.

## 2) Ürün Kapsamı (Bugün Aktif Olanlar)

- Natal yorumlama ve profil odaklı içerik üretimi
- Transit hesaplama, takvimleme, gün bazlı detay ve best-times önerisi
- Synastry/ilişki analiz endpointleri
- Sky feed/olay arşivi/personalization akışı
- Forum API yüzeyi
- AI chat (kota kontrollü, paywall entegre)
- RevenueCat webhook ile kredi/pro entitlement güncelleme

## 3) Monorepo Yapısı

- `backend/`: FastAPI tabanlı API ve astroloji/yorumlama motorları
- `mobile/`: Flutter mobil uygulaması (iOS/Android)
- `docs/`: mimari ve ürün dokümantasyonu
- `tests/`: engine, ontology ve approval testleri
- `render.yaml`: backend deploy tanımı

Not: Bu repoda aktif, ayrı bir web frontend uygulaması görünmüyor; ana istemci Flutter mobil uygulama.

## 4) Teknoloji Yığını

## Backend
- Dil: Python
- API: FastAPI (`backend/app/main.py`)
- Sunucu: Uvicorn (Render start command)
- Validasyon/Konfigürasyon: Pydantic + pydantic-settings
- Astro hesaplama: Swiss Ephemeris (`pyswisseph`)
- HTTP çağrıları: `requests`
- Cache altyapısı: memory veya Redis (ayar bazlı)
- AI çağrıları: OpenAI Responses API (model env ile yönetiliyor)
- Opsiyonel AI paketleri: `torch`, `transformers`, `accelerate`

## Mobile (Frontend)
- Çatı: Flutter (Dart)
- State yönetimi: Riverpod
- Navigasyon: go_router
- Ağ istemcisi: Dio
- Auth/DB istemcisi: supabase_flutter
- Satın alma: purchases_flutter (RevenueCat)
- Yerelleştirme: Flutter localization + `app_en.arb`, `app_tr.arb`

## Dış Servisler
- Supabase: Auth + tablo bazlı veri işlemleri
- OpenAI: Chat üretimi
- RevenueCat: satın alma olayları ve entitlement/kredi senkronizasyonu

## 5) Backend Mimarisi (Yüksek Seviye)

Uygulama giriş noktası `backend/app/main.py`:
- CORS middleware
- Swiss Ephemeris path set
- Router kayıtları (health/user/charts/natal/home/transits/sky/chat/revenuecat/profile/story/synastry/forum)

Temel katmanlar:
- API Routes: `backend/app/api/routes/*`, `backend/app/routers/*`, `backend/app/forum/*`
- Domain Engine:
  - Natal: `backend/app/natal/*`
  - Transit: `backend/app/transit/*`
  - Astro çekirdek/hesaplama: `backend/app/astro*`, `backend/app/engine/*`
- Service katmanı:
  - Supabase erişimi (`backend/app/services/supabase.py`)
  - AI chat quota/log/cost (`backend/app/services/ai_chat.py`)
  - RevenueCat webhook işleme (`backend/app/services/revenuecat.py`)
  - Profil/ayar persistence (`backend/app/services/profiles.py`)

## 6) Önemli API Alanları

- Health: `/api/health`, `/api/readiness`
- Natal/Profile:
  - `/interpret`, `/interpret/ui`, premium/debug varyantları
  - `/profile/fast`, `/profile/archetype`, `/profile/archetype/questions`
- Transit:
  - `/transits`
  - `/transit/calendar`
  - `/transit/calendar/day`
  - `/transit/calendar/best-times`
  - `/transit/narrative`
  - `/transits/window`
  - `/transits/event_timing`
- Chat: `/v1/ai/chat`
- Billing: `/v1/billing/revenuecat/webhook`
- Sky: `/sky/now`, `/sky/feed`, `/sky/archive`, `/sky/events/...`
- Synastry/Charts/Forum/Profile/Story için ek endpoint setleri

## 7) Mobile Mimarisi (Yüksek Seviye)

Giriş:
- `mobile/lib/main.dart`
- Supabase bootstrap: `mobile/lib/app/supabase/supabase_bootstrap.dart`

Auth ve yönlendirme:
- Auth gate: `mobile/lib/app/auth/auth_gate.dart`
- Router: `mobile/lib/app/app_router.dart`
- Session varsa kullanıcının doğum verisine göre onboarding veya ana tab akışı seçiliyor.

API erişimi:
- Base URL: `API_BASE_URL` (`mobile/lib/app/api/api_environment.dart`)
- HTTP client: `ApiClient` (`mobile/lib/app/api/api_client.dart`)
  - Bearer token otomatik ekleniyor (Supabase session)
  - SLA bazlı timeout, request dedupe, hafif response cache, telemetry

Özel ürün modülleri:
- ChartLab: endpoint test/inceleme ekranları (`mobile/lib/app/chart_lab/*`)
- AI chat: `mobile/lib/app/ai/ai_chat_service.dart`
- Paywall/satın alma: `mobile/lib/app/ai/revenuecat_service.dart` + paywall UI

## 8) Entegrasyonlar ve Birbirine Bağlı Akışlar

## A) Auth akışı
1. Mobilde Supabase session oluşur.
2. Mobil, backend çağrılarında `Authorization: Bearer <token>` gönderir.
3. Backend `supabase.auth.get_user(token)` ile kullanıcıyı doğrular.

## B) AI Chat + Kota + Paywall akışı
1. Mobil `/v1/ai/chat` çağırır.
2. Backend kullanıcı profil/entitlement satırlarını garanti eder.
3. Kota uygunsa OpenAI Responses API çağrısı yapılır.
4. Başarı sonrası kota tüketilir ve kullanım maliyeti/event log kaydı yazılır.
5. Kota yoksa `paywall=true` yanıtı döner.

## C) RevenueCat entitlement akışı
1. RevenueCat webhook backend’e düşer (`/v1/billing/revenuecat/webhook`).
2. Duplicate event kontrolü yapılır.
3. Ürüne göre kredi veya pro durumu güncellenir.
4. Etkilenen ürünler:
   - Kredi: `jovia_q1`, `jovia_q5`, `jovia_q15`
   - Pro: `jovia_pro_monthly`

## D) Transit takvim akışı
1. Mobil ilgili ay için `/transit/calendar` çağırır.
2. Aynı aralık için `/transit/calendar/best-times` çağırır.
3. Gün seçimi için `/transit/calendar/day` çağırır.
4. Backend; transit engine + narrative + calendar serializer katmanlarını birleştirir.

## 9) Veri Katmanı ve Bilinen Tablolar

Kodda geçen ana tablolar:
- `profiles`
- `ai_entitlements`
- `ai_usage_events`
- `revenuecat_webhook_events`
- `astro_settings`
- `birth_data`
- `archetype_profiles`

Genel yaklaşım:
- Supabase istemcisi (anon) ve admin istemcisi (service role fallback) birlikte kullanılıyor.
- İş kurallarının bir kısmı RPC ile çalışıyor (`consume_ai_quota`).

## 10) Konfigürasyon ve Ortam Değişkenleri

Backend (`backend/app/core/config.py`) öne çıkan ayarlar:
- APP/infra: `APP_ENV`, `DEBUG`, `LOG_LEVEL`, `ALLOWED_ORIGINS`
- Ephemeris: `SWISSEPH_PATH`, `HOUSE_SYSTEM`
- Supabase: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- OpenAI: `OPENAI_API_KEY`, `OPENAI_API_URL`, `OPENAI_CHAT_MODEL`, token/cost/timeouts
- RevenueCat: `REVENUECAT_WEBHOOK_AUTHORIZATION`
- Cache/perf: `PERFORMANCE_CACHE_BACKEND`, Redis URL/prefix, TTL ayarları

Mobile (`--dart-define`) öne çıkanlar:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `API_BASE_URL`
- `REVENUECAT_APPLE_PUBLIC_SDK_KEY`
- `REVENUECAT_GOOGLE_PUBLIC_SDK_KEY`

## 11) Deploy, Operasyon ve Gözlemlenebilirlik

Render deploy tanımı (`render.yaml`):
- Build: `pip install -r backend/requirements.txt`
- Start: `PYTHONPATH=backend python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Observability:
- Backend log seviyesi env ile yönetiliyor.
- Transit ve API katmanında performans/trace yardımcıları mevcut.
- Mobilde performans telemetry noktaları var.

## 12) Test ve Kalite

Test klasörleri:
- `tests/engine/*`
- `tests/ontology/*`
- `tests/approval/*`

Dokümanlanmış test komutları `docs/README.md` içinde mevcut.

## 13) Bilinen Dokümantasyon Tutarsızlıkları

- `backend/README.md` halen Flask merkezli eski içerik taşıyor.
- `overview.md` içinde eski/yarı-tarihi mimari referansları bulunuyor.
- Güncel teknik gerçeklik için bu doküman ve `docs/current_architecture.md` esas alınmalı.

## 14) Kısa Yol Haritası Önerisi (Dokümantasyon Açısından)

- Backend ve mobile README dosyalarını gerçek stack ile güncellemek
- Endpoint sözleşmeleri için tek bir “API contract” dokümanı çıkarmak
- Supabase şema/RPC bağımlılıklarını ayrı bir “data contract” dokümanına taşımak
- Deploy/rollback/runbook dökümanı eklemek

