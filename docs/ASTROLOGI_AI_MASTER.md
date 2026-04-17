# Astrologi AI / SHOU — Ana Proje Dökümanı

> Bu döküman projenin **tek noktadan referans** dosyasıdır. Vizyon, mimari, modüller, akışlar, sözleşmeler ve geliştirme kuralları burada toplanır. Diğer spec dosyaları (roadmap, performance, regression) bu dökümanın ekleridir.
>
> Son güncelleme: 2026-04-17
> Mevcut branch: `claude/objective-taussig-2fefeb`
> Mağaza adı: **SHOU** · Domain: `shouastrology.com`

---

## 1. Vizyon ve Ürün Konumlandırması

### 1.1 Tek cümlelik vizyon
SHOU (kod adı: Astrologi AI / Jovia), ham gök verisini **deterministik astroloji motoru + kural tabanlı "Jovia dili" + AI yorum katmanı** ile birleştirerek kişiye özel, edebi ve duygusal olarak rezonans yaratan bir astroloji deneyimi sunar.

### 1.2 Ürün vaadi
- **Doğum haritası (natal)**: Sadece "Güneş Aslan'da" demez; lived_experience, mekanizma, refleks, gift, growth_edge çerçevesinde anlatır.
- **Sinastri (bond)**: İki haritayı karşılaştırarak ilişki dinamiklerini çözümler.
- **Transit takvimi**: Bugün / bu ay / bu dönem için "ne oluyor, neden, nasıl yaşanır" perspektifi.
- **AI sohbeti**: Profil + güncel transit bağlamlı kişisel asistan.
- **Story Studio**: Astrolojik anlara dayalı paylaşılabilir görsel hikâyeler.
- **Forum**: Topluluk paylaşımı.

### 1.3 Hedef kullanıcı
- Astrolojiyi günlük rehberlik için değil, **kendini tanıma + ilişki / zamanlama bilinci** için kullanan modern kullanıcı.
- "Generic burç yorumlarından" sıkılmış, derinlik isteyen kişi.
- Türkçe ve İngilizce konuşan, mobil-öncelikli kitle.

### 1.4 Marka tonu
- Editorial, sıcak ama kült-değil. Klişe astroloji görselleri (büyücü, kart, semboller) **kullanılmaz**.
- Renk paleti: beyaz/kırık beyaz arka plan + lime green (`#CAFF4D` civarı) accent. Splash zemini: `#090A0E`.
- Amber / sıcak ton **yasak** — markaya aykırı.
- Tipografi: editorial, büyük başlık, bold kontrast. Detay: `docs/visual-system/`.

---

## 2. Repo Yapısı (Yüksek Seviye)

```
Astrologi-Ai/
├── backend/          # FastAPI servisi (Python)
├── mobile/           # Flutter mobil uygulama (iOS öncelikli)
├── config/           # YAML konfigleri (tone, ontology, scoring, transit, classifiers, routing)
├── docs/             # Bu döküman dahil tüm mimari belgeler
├── compiler/         # Kural derleyici araçları
├── engine/           # Eski/paylaşılan motor parçaları
├── scripts/          # Pilot ve bakım scriptleri
├── tests/            # Engine + approval testleri (üst seviye)
├── overview.md       # Eski yüksek seviye özet (referans)
├── render.yaml       # Render.com deploy config (backend)
└── CLAUDE.md         # Claude Code için proje kuralları
```

---

## 3. Backend Mimarisi (FastAPI)

### 3.1 Çalıştırma
- Entry point: [backend/app/main.py](backend/app/main.py) — `create_app()` factory.
- Render start: `PYTHONPATH=backend python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Build: `pip install -r backend/requirements.txt`
- Local test: `cd backend && PYTHONPATH=backend python -m pytest -q ../tests/engine`

### 3.2 Bağımlılıklar (özet)
- **Astroloji**: `pyswisseph==2.10.3.2` + `backend/ephe/` veri dizini
- **Web**: `fastapi`, `uvicorn`, `gunicorn`
- **Config**: `pydantic>=2`, `pydantic-settings`
- **DB / Auth**: `supabase` (Supabase Python SDK)
- **Cache**: `redis>=5,<6` (opsiyonel; default = in-memory)
- **AI / LLM**: HTTP bazlı çağrılar (Groq, OpenAI). Yerel inference için `torch`, `transformers`, `accelerate`, `tokenizers`.
- **Yardımcı**: `requests`, `pytz`, `python-dotenv`, `email-validator`

### 3.3 Konfigürasyon (`backend/app/core/config.py`)
Tüm ortam değişkenleri Pydantic Settings ile yönetilir. Önemli env'ler:

| Env | Default | Anlamı |
|---|---|---|
| `DEBUG` | `False` | FastAPI debug |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | CORS |
| `SWISSEPH_PATH` | `./ephe` | Ephemeris dosyaları |
| `OPENCAGE_API_KEY` | — | Şehir → koordinat |
| `GROQ_API_KEY` / `GROQ_MODEL` | `llama-3.1-8b-instant` | Birincil LLM |
| `OPENAI_API_KEY` / `OPENAI_CHAT_MODEL` | `gpt-5.4-mini` | Yedek LLM |
| `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` | — | Supabase |
| `HOUSE_SYSTEM` | `P` (Placidus) | Ev sistemi |
| `ENABLE_HOME_FAST_CACHE`, `ENABLE_HOME_DEEP_CACHE`, `ENABLE_STALE_WHILE_REVALIDATE`, `ENABLE_BACKGROUND_REFRESH` | `True` | Cache anahtarları |
| `PERFORMANCE_CACHE_BACKEND` | `memory` | `memory` / `redis` / `layered` |
| `PERFORMANCE_CACHE_REDIS_URL` | — | Redis URL |
| `HOME_FAST_TTL_SECONDS` / `HOME_DEEP_TTL_SECONDS` | `1800` / `7200` | Home cache TTL |
| `TRANSIT_NARRATIVE_TTL_SECONDS` | `900` | Transit cache TTL |
| `REVENUECAT_WEBHOOK_AUTHORIZATION` | — | Webhook secret |

> ⚠️ `backend/app/core/config.py` ve `backend/app/main.py` izin almadan değiştirilmez (CLAUDE.md kuralı).

### 3.4 Modül haritası

```
backend/app/
├── main.py                  # FastAPI factory + router include
├── core/                    # config.py, logging.py
├── env/                     # BASE_DIR, .env loader
├── api/routes/              # Yeni API yüzeyleri
│   ├── home.py              # /home/fast vb.
│   ├── natal_interpretation.py  # /interpret, /interpret/ui
│   ├── sky.py               # /sky/now, sky events
│   └── transits.py          # /transits, /transit/calendar*, best-times
├── routers/                 # Klasik router'lar
│   ├── health.py            # /api/health, /api/readiness
│   ├── user.py              # auth, profile bilgisi
│   ├── charts.py            # natal/synastry chart endpoint
│   ├── chat.py              # AI sohbet
│   ├── profile.py           # /profile/fast vb.
│   ├── revenuecat.py        # webhook
│   ├── story.py             # story studio
│   ├── synastry.py          # bond / sinastri
│   └── interpretation.py    # legacy interpret
├── astro/                   # Swiss Ephemeris katmanı
│   ├── chart_engine/        # natal hesaplama
│   ├── synastry/            # ikili hesaplama
│   └── transits/            # transit hesaplama
├── astro_core/              # Düşük seviye astrofiziksel araçlar
├── transit/                 # Transit yorum motoru (V3)
│   ├── calendar/            # best_times.py vb.
│   ├── calendar_builder.py  # ay/gün payload üretimi
│   ├── narrative/           # transit anlatıları
│   ├── interpret/           # tek olay yorumları
│   ├── lens/                # bakış açısı filtreleri
│   ├── present/             # render katmanı
│   └── serialize/           # mobil sözleşmeleri
├── natal/                   # Natal yorum motoru
│   ├── natal_graph.py / natal_graph_v2.py
│   ├── narrative/           # primitive_engine_v2, master_selector, feature_graph
│   ├── personality_imprint/ # kişilik özeti
│   ├── profile_insights/
│   ├── archetype_profile.py + archetype_question_bank.py  # Arketip Test V1
│   ├── profile_v8_payload_builder.py  # mobile profile v8 payload
│   └── public_builder.py / public_models.py
├── synastry/                # Sinastri motoru
│   ├── resonance_engine.py
│   ├── activation_engine.py
│   ├── narrative/
│   └── public_builder.py
├── builders/                # Jovia narrative builders
│   ├── narrative_builder.py / narrative_renderer_v26.py
│   ├── composite_builder.py + composite_*.py
│   ├── phase2_selector.py / phase2_selector_engine.py
│   ├── semantic_normalizer.py
│   └── ssl_layer.py
├── ai/                      # LLM entegrasyonu
│   ├── narrative/           # JoviaSemanticNarrativeBuilder vb.
│   ├── archetypes/
│   └── prompts/
├── ontology/                # YAML ontoloji okuyucular
├── style/                   # Tone yardımcıları
├── resolvers/               # Veri çözücüler
├── helpers/, utils/         # Genel yardımcılar
├── data/                    # Statik veri (rules, libraries)
├── models/                  # Pydantic modelleri
├── services/                # Dış servis adaptörleri
│   ├── supabase.py
│   ├── profiles.py / users.py
│   ├── chart_service.py
│   ├── ai_chat.py
│   ├── revenuecat.py
│   ├── stories.py
│   ├── synastry.py / synastry_analysis.py
│   ├── firebase.py
│   └── performance/         # Cache, timing, orchestrator
│       ├── cache_store.py     # memory/redis/layered backend
│       ├── cache_keys.py
│       ├── home_orchestrator.py
│       ├── payload_versions.py
│       ├── refresh_scheduler.py
│       └── timing.py
├── forum/                   # Forum router + servisleri
├── sky_events/              # Astronomik olay akışı
├── social/                  # Sosyal etkileşim parçaları
├── story/                   # Story studio
├── pilot/                   # Deneysel pilot çalışmalar
└── ephe/ (data dizini)      # Swiss Ephemeris veri dosyaları
```

### 3.5 Önemli endpoint sözleşmeleri

#### Health & readiness
- `GET /api/health` → her zaman JSON, cache + Supabase summary döner. Fallback durumunda `status=degraded`.
- `GET /api/readiness` → cache veya Supabase hazır değilse `503`, ikisi de hazırsa `200`.
- Summary alanları: `selected_backend`, `active_backend`, `strict_mode`, `redis_configured`, `redis_ready`, `fallback_active`, `fail_fast_expected`, `shared_cache_expected`, `readiness_ok`, `status`, `reason`.

#### Natal yorumlama
- `POST /interpret` (legacy) ve `POST /interpret/ui` (mobile UI sözleşmesi) → natal narrative payload.
- `GET /profile/fast` → hızlı snapshot (sun/moon/rising vb).
- Narrative V2 alan sözleşmesi (kaynak gerçeği): `hook`, `lived_experience`, `mechanism`, `reflex`, `gift`, `growth_edge`, `what_it_builds`, `technical_anchor`.

#### Transit
- `POST /transits` → period / core transit narrative. **Takvim datasource olarak kullanılmaz.**
  - Body: `birth_date`, `birth_time`, `birth_place`, `transit_date`, `tz` (+ opsiyonel `transit_place`).
- `GET /transit/calendar` → ay/aralık için takvim (`days[]` döner).
  - Query: `birth_date`, `birth_time`, `birth_place`, `start`, `end`, `tz` (+ `transit_place`, `lens`, `view`, `include`).
- `GET /transit/calendar/day` → tek gün detayı (`date=`) **veya** range modu (`start` + `end`).
- `GET /transit/calendar/best-times` → niyet bazlı en iyi gün/aralıklar.
  - Query: `intent` (örn. `beauty_care`), `sub_intent` (`nourish` / `reduce` / `procedure`), `body_area`, `top`, `window`, `debug`, vb.
  - Risk kategorileri: `phase_shift`, `event_peak`, `injury_risk`, `procedure_block`.
- Transit event V2 alanları: `headline`, `opening`, `essence`, `mechanism`, `asks`, `watchout`, `what_it_builds`, `technical_note`.
- Period V2 alanları: `period_opening`, `big_picture`, `mechanism`, `growth_edge`, `relational_or_life_expression`, `what_it_builds`, `technical_note`.

#### Home
- `GET /home/fast` → hızlı home preview (cache TTL 30dk fast / 2sa deep).
- `GET /sky/now` → şu anki gök olayları akışı.

#### Diğer
- `POST /chat/...` → AI sohbet.
- `POST /story/...` → story studio.
- `POST /synastry/...` → sinastri.
- `POST /revenuecat/webhook` → abonelik durum güncellemesi (Authorization header doğrulamalı).
- `GET /forum/...` → topluluk içerikleri.

> 📌 Yeni endpoint eklemeden önce **CLAUDE.md kuralı gereği onay alınır.**

### 3.6 Yorumlama hattı (Jovia language system)
1. **Astroloji Engine** (Swiss Ephemeris): doğum bilgisi → UTC → Julian Day → gezegen/ev/açı pozisyonları (Placidus default).
2. **Rule Engine**: yapılandırılmış kural JSON'larını yükler (planet/sign/house/aspect/meta), eşleşmeleri etiketli çıktı üretir (cause/mechanism/effect/shadow/potential).
3. **Builder katmanı**:
   - `JoviaWeightedNarrativeBuilder` → her slot için en iyi cümleyi gezegen ağırlığı ile seçer.
   - `JoviaNarrativeFlowEngine` → cause→mechanism→shadow→potential bağlaçları ile akıcı paragraf üretir.
   - `JoviaSemanticNarrativeBuilder` (PRO) → fragmanları premium edebi proza yeniden yazar.
4. **AI Layer**: Premium akış için Groq → OpenAI → yerel LLaMA fallback zinciri. Prompt engineering, cache, harmful filter, rate limit ve loglama burada yaşar.
5. **Render**: API yanıtı; metadata + planets + aspects + interpretations + combined insights + `narrative_interpretation`.

### 3.7 Selection V3 ve Arketip Sistemi
- Hedef: `core_story`, `profile_narrative`, `personality_imprint`, `sections_v2`, `supporting_threads` aynı **kişilik omurgasından** beslensin.
- Yeni hat: `astro signals → natal feature graph → primitives → identity spine → layer arbitration → editorial rendering`.
- İlgili dosyalar:
  - [backend/app/natal/narrative/natal_feature_graph.py](backend/app/natal/narrative/natal_feature_graph.py)
  - [backend/app/natal/narrative/primitive_engine_v2.py](backend/app/natal/narrative/primitive_engine_v2.py)
  - [backend/app/natal/narrative/master_selector.py](backend/app/natal/narrative/master_selector.py)
- **Arketip Test V1 (8 arketip)**: Builder, Visionary, Analyst, Connector, … (detay: [docs/archetype_test_system_v1.md](docs/archetype_test_system_v1.md)). Çıktı: `top_archetypes`, `shadow_archetype`, `primary_contradiction`, `confidence`.

### 3.8 Caching stratejisi
- **Backend katmanları**:
  - Fast cache → Home preview (TTL 30 dk)
  - Deep cache → detaylı profil (TTL 2 sa)
  - Stale-while-revalidate + background refresh
  - Backend `memory` (default) veya `redis` / `layered`
- **Mobile katman**: in-memory response cache (TTL bazlı). Home `transit/narrative` istekleri için **client cache kullanılmaz** (boş payload UI'ı dakikalarca boş bırakırdı).
- **Backend yazma kuralı**: `payload_profile=home` veya `calendar_day` boş public payload **cache'e yazılmaz**.

---

## 4. Mobile Mimarisi (Flutter)

### 4.1 Çalıştırma & sürüm
- Dart SDK: `^3.11.0`, Material 3.
- Çalıştırma: standart `flutter run` (iOS öncelikli; Android dosyaları mevcut ama launcher_icons sadece iOS için açık).
- iOS app icon ve splash generator komutları: `pubspec.yaml` içinde dokümante.

### 4.2 Bağımlılıklar (pubspec.yaml)
- **State**: `flutter_riverpod: ^3.3.1` (NotifierProvider pattern)
- **Router**: `go_router: ^17.2.1`
- **Auth/DB**: `supabase_flutter: ^2.5.6`
- **HTTP**: `dio: ^5.7.0`
- **i18n**: `intl: ^0.20.2` + `flutter_localizations`
- **Görsel**: `flutter_svg: ^2.0.10+1`
- **Abonelik**: `purchases_flutter: ^9.16.1` (RevenueCat)
- **Diğer**: `image_picker`, `url_launcher`, `cupertino_icons`
- Dev: `flutter_test`, `flutter_native_splash`, `flutter_launcher_icons`, `flutter_lints`

> ⚠️ `pubspec.yaml`'a izin almadan paket eklenmez. Yeni Flutter paketi gerekirse **önce sorulur**.

### 4.3 Modül haritası

```
mobile/lib/
├── main.dart                # Uygulama girişi (dokunulmaz)
├── app/
│   ├── app_router.dart      # GoRouter (dokunulmaz)
│   ├── api/
│   │   ├── api_client.dart  # Dio + SLA timeouts + cache + dedupe
│   │   ├── api_environment.dart
│   │   └── backend_health_repository.dart
│   ├── auth/                # AuthGate, login, register
│   ├── onboarding/          # birth data toplama
│   ├── splash/              # native splash + splash_screen
│   ├── tabs/                # bottom nav sayfaları (bkz. 4.5)
│   ├── profile/             # profil providers / repository / v8 adapter
│   ├── people/              # bağlantılı kişiler / sinastri profilleri
│   ├── ai/                  # AI sohbet altyapısı
│   ├── chart_lab/           # Debug ChartLab (endpoint catalog + templates)
│   ├── data/                # local data modelleri
│   ├── forum/               # forum istemcisi
│   ├── legal/               # gizlilik / şartlar
│   ├── performance/         # load_tuning.dart (TTL/timeout SoT)
│   ├── preferences/         # app preferences
│   ├── supabase/            # supabase istemci yardımcıları
│   ├── telemetry/           # PerfTelemetry
│   ├── theme/               # tema yardımcıları
│   ├── timing/              # timing util
│   └── widgets/             # paylaşılan widget'lar (jovia_app_menu_drawer vb.)
├── design/
│   ├── theme/               # ⛔ DOKUNMA — design tokens
│   ├── tokens/              # design tokens
│   ├── typography/          # editorial font setup
│   ├── widgets/             # JoviaEditorial, JoviaBottomNav vb.
│   ├── astro/               # gezegen/eleman görselleri
│   └── assets/              # asset wrapper
├── l10n/                    # .arb dosyaları (tr, en) + l10n.dart
├── ui/                      # paylaşılan UI parçaları
└── screens/                 # legacy ekranlar
```

### 4.4 Auth + onboarding akışı
1. `main.dart` → Supabase init + `MaterialApp.router(buildRouter())`.
2. `/` → `AuthGate`. Session yoksa `/login` veya `/register`.
3. Session var ama doğum bilgisi yoksa → `OnboardingProfilePage` (`/onboarding_profile`).
4. Tamamlandığında → `/tabs` → `TabsShell`.

`buildRouter()` şu route'ları sunar: `/`, `/login`, `/register`, `/onboarding_profile`, `/tabs`. Diğer ekranlar `Navigator.of(context).push(MaterialPageRoute(...))` ile açılır (örn. ProfilePage, CalendarHubPage, ChartLab).

### 4.5 Tab yapısı (`TabsShell`)
| Index | Tab | Sayfa |
|---|---|---|
| 0 | Home | `home_page.dart` — günlük transit + profil özeti |
| 1 | Bond | `bond_page.dart` → `bond_result_page.dart` (sinastri) |
| 2 | Story Studio (öne çıkan +) | `story_studio_page.dart` |
| 3 | AI Chat | `ai_page.dart` (debug: long-press → ChartLab) |
| 4 | Profile | `profile_page.dart` |

Ek olarak `tabs/` altında:
- `calendar_hub_page.dart` — transit takvimi
- `period_detail_page.dart`, `period_detail_navigation.dart`, `period_marker_detail_page.dart`
- `sky_event_feed_page.dart`, `sky_event_detail_page.dart`
- `forum_page.dart`, `forum_post_detail_page.dart`
- `profile_archetype_page.dart`, `profile_detail_flow_page.dart`, `profile_relationship_preview.dart`, `experimental_profile_page.dart`, `profile_page_v2_experiment.dart`
- `transit_detail_page.dart`, `timing_page.dart`, `chart_lab_page.dart`

End drawer (`JoviaAppMenuDrawer`): Profil, People, Calendar, Archetype hızlı erişim.

### 4.6 API client kuralları (`api/api_client.dart`)
- Dio tabanlı, **SLA bazlı timeout**:
  - `fast` → 3 sn
  - `interactive` → 8 sn
  - `background` → 18 sn
  - Default Dio connect: 10 sn / receive: 20 sn
- Authorization header otomatik (`Supabase.instance.client.auth.currentSession.accessToken`).
- **Inflight dedupe** + opsiyonel response cache (TTL'li).
- Tüm requestler `PerfTelemetry` ile loglanır (`api_request_start/end/deduped`).

### 4.7 Performance / load tuning
**Single source of truth**: [mobile/lib/app/performance/load_tuning.dart](mobile/lib/app/performance/load_tuning.dart). Timeout/TTL değerleri ekran dosyalarına dağılmaz; önce buraya taşınır.

Home critical path (paralel):
- `home/fast` preview (asla narrative isteğini bloklamaz, sadece fallback/prefill kaynağı)
- `/transit/narrative` home payload
- `/interpret/ui` natal summary
- `/sky/now` sky feed

Günlük transit kaynak önceliği:
1. `daily_event_cards`
2. selected-day `calendar.days`
3. fallback `calendar_day/full`

Profile critical path:
- `/profile/fast` → sign chip'leri hemen güncellenir
- `/interpret/ui` (+ gerekirse legacy `/interpret`) → ağır anlatı paralel akışta

### 4.8 Tasarım sistemi kuralları
- `design/theme/` ve `main.dart`, `app_router.dart` → **dokunulmaz**.
- Riverpod provider tanımları → değiştirilmez (state yapısı kırılmasın).
- Asset'ler `ios/Flutter/assets/` altında SVG: `colors`, `illustrations`, `dividers`, `logo`, `planets`, `elements`. Logo: `assets/logos/circle_dark_mode.png`. Splash: `assets/logos/splash_shou_symbol_dark_2048.png`.
- Animasyon: `Curves.easeOutCubic` / `easeInOutCubic`. Sayfa geçişi 300–400ms, micro-interaction 150–250ms, stagger `index * 60ms`. Spring efektler **harici paket olmadan** `TweenSequence` ile.
- i18n: `tr` ve `en` `.arb` dosyalarından. UI metinleri kod içinde sabit yazılmaz; `context.l10n.<key>` kullanılır.

### 4.9 Görsel sistem sözleşmeleri
[docs/visual-system/](docs/visual-system/) altında:
- `normalized_interpretation_schema.ts` — payload + tag + token şeması
- `visual_adapter.ts` — backend payload → görsel sistem dönüşümü
- `illustration_selector.ts` — illüstrasyon seçimi + fallback
- `layout_rhythm_adapter.ts` — semantik layout-rhythm kararı
- `field_mapping_spec.md` — alan eşleme kuralları
- `example_outputs.json` — örnek payloadlar

---

## 5. Veri ve Persistence

- **Supabase (Postgres + Auth)** birincil veri katmanı: kullanıcılar, profiller, kayıtlı haritalar, story, forum, AI cache, request log.
- JWT auth: Supabase access token, mobile API client tarafından her isteğe Bearer header ile eklenir.
- Eski döküman MongoDB'ye atıf yapsa da güncel sistem **Supabase ile çalışır**.
- Şema değişiklikleri **önce sorulur** (CLAUDE.md kuralı).

---

## 6. AI Katmanı

### 6.1 Model zinciri
1. **Groq** (`llama-3.1-8b-instant`) — birincil
2. **OpenAI** (`gpt-5.4-mini` default; env'den değiştirilir) — fallback
3. **Yerel LLaMA** (`torch` + `transformers`) — son çare

### 6.2 Garantiler
- Cause → mechanism → effect → shadow → potential **sıralaması** prompt seviyesinde zorunlu.
- Üretim cache'lenir (tekrar maliyetini azaltır).
- Harmful filter + rate limit + structured logging.
- Free akış: deterministik builder pipeline. Premium akış: `JoviaSemanticNarrativeBuilder`.

### 6.3 RevenueCat
- iOS aboneliği RevenueCat üzerinden. Webhook → `backend/app/routers/revenuecat.py`.
- Mobile: `purchases_flutter` paketi. Paywall ve "Restore Purchases" + "Delete Account" menüde görünür (App Store gereksinimi).

---

## 7. Konfigürasyon Dosyaları (`config/`)

| Klasör | İçerik |
|---|---|
| `config/tone/tone.yaml` | Anlatı tonu kontrolleri |
| `config/ontology/mapping.yaml`, `themes.yaml` | Kural ontolojisi |
| `config/scoring/weights.yaml`, `archetype_fusion_v1.yaml`, `archetype_fusion_v2.yaml` | Selection / arketip skorları |
| `config/transit/daily_selection.yaml`, `selection_v3_config.yaml` | Transit selection V3 ayarları |
| `config/classifiers/`, `config/routing/` | Sınıflandırıcılar ve yönlendirme |

---

## 8. Test ve Kalite

- Backend testler: `backend/tests/` (53+ dosya). Komut:
  ```bash
  cd backend
  python -m pip install -r requirements-dev.txt
  PYTHONPATH=backend python -m pytest -q ../tests/engine
  PYTHONPATH=backend python -m pytest -q ../tests/approval/test_narrative_snapshots.py
  ```
- Mobile testler: `mobile/test/` (`flutter test`).
- **Selection V3 regression watchlist**: [docs/regression_watchlist.md](docs/regression_watchlist.md). Özellikle:
  - Daily top pick drift, low-signal collapse
  - Period spine bozulması, coverage override
  - Cluster collapse / aşırı agresif clustering
  - Fallback'in yanlış zamanlanması
  - Personalization tie-break dengesi
  - Specificity / shadow-only / flow-only collapse
  - Blocked point (Fortune, Vertex, Lilith) sızıntısı

---

## 9. Performans ve Telemetri

### 9.1 Backend
- `/interpret/ui` ve `/interpret` route'larında stage breakdown logu.
- `/profile/fast` timing logu (PII yok).
- Cache health → `/api/health` ve `/api/readiness` üzerinden raporlanır.

### 9.2 Mobile
PerfTelemetry event'leri:
- Startup: `app_launch_start`, `splash_visible`, `auth_gate_start`, `auth_gate_resolved`, `tabs_shell_visible`, `first_home_visible`
- API: `api_request_start`, `api_request_end`, `api_request_deduped` (alanlar: endpoint, method, request_sla, status_code, start_ms, end_ms, duration_ms, payload_bytes, payload_kb, cache_status, cache_store, inflight_dedupe)
- Profile: provider state geçişleri, fallback kararları
- Detay: [docs/performance_instrumentation_report.md](docs/performance_instrumentation_report.md)

---

## 10. Deployment

- **Platform**: Render.com (web servis).
- **Config**: [render.yaml](render.yaml) — `astrologi-backend` web servisi.
- **Build**: `pip install -r backend/requirements.txt`
- **Start**: `PYTHONPATH=backend python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **CI/CD**: GitHub Actions yok; **manuel deploy**.
- Mobile: iOS App Store (TestFlight → release). Android dosyaları repoda var ama aktif release değil.

### 10.1 App Store metadata (iOS)
- App adı: **SHOU** · Subtitle (TR): "Sana özel astroloji deneyimi"
- Support: `info@shouastrology.com`
- Privacy: `https://shouastrology.com/privacy` · Terms: `https://shouastrology.com/terms`
- iOS izinleri: `NSPhotoLibraryUsageDescription` var; Camera & PhotoLibraryAdd henüz eklenmedi.
- Restore Purchases + Delete Account menüde görünmek zorunda. Detay: [docs/shou_app_store_release_checklist.md](docs/shou_app_store_release_checklist.md).

---

## 11. Geliştirme Akışı ve Kurallar

### 11.1 Çalışma prensibi (CLAUDE.md özeti)
1. Dosyayı önce **OKU**.
2. Mevcut yapıyı koru; gereksiz refactor yok.
3. Sadece istenen bileşeni değiştir.
4. Değişen dosyaları listele.
5. Yeni paket gerekirse **önce sor**.

### 11.2 Onay gerektiren değişiklikler
- Yeni Flutter paketi
- Yeni Python bağımlılığı
- Bir widget veya servisi tamamen yeniden yazmak
- Navigation flow değişikliği
- Supabase şema değişikliği
- Caching stratejisi değişikliği
- Yeni API endpoint'i

### 11.3 Kesinlikle dokunulmaz
- Mobile: `lib/design/theme/`, `lib/main.dart`, `lib/app/app_router.dart`, tüm Riverpod provider tanımları, `pubspec.yaml` (izinsiz)
- Backend: `backend/app/core/config.py`, `backend/app/main.py`, `backend/ephe/`, `.env`

---

## 12. Roadmap (Özet)

| Faz | Kapsam | Durum |
|---|---|---|
| **MVP** | Natal calc + deterministik builder + rule engine + FastAPI + auth/log | ✅ Tamamlandı |
| **v1** | Synastry, transitler, weighted narrative, flow connector, premium AI ROI, gelişmiş API doc | ✅ Büyük ölçüde tamamlandı |
| **v2 (mevcut)** | Selection V3 (identity spine), Narrative V2 alan modeli, Arketip Test V1, Profile V8, Calendar Best Times, Story Studio, Forum, RevenueCat | 🔄 Aktif geliştirme |
| **Growth** | AI conversation derinleşme, celebrity similarity, life timeline, Aura/Story cards, CRON/Celery background tasks, gelişmiş monitoring, çoklu dil genişlemesi | ⏳ Planlı |

Önemli güncel iş başlıkları:
- **Profile V8 redesign + natal hattı konsolidasyonu** — yeni audit ve 4-fazlı yol haritası: [docs/profile_v8_audit_and_roadmap.md](docs/profile_v8_audit_and_roadmap.md)
- Selection V3 fine-tuning (regression watchlist üzerinden)
- Profile V8 selectors + splash animation iyileştirmesi (son commit)
- Shared cache hardening (tamamlandı; [docs/shared_cache_readiness_completion.md](docs/shared_cache_readiness_completion.md))
- Home transit fallback katmanı + natal summary streamline
- App menu drawer + preferences

---

## 13. Hızlı Referans (Cheat Sheet)

| Konu | Yer |
|---|---|
| Backend entry | [backend/app/main.py](backend/app/main.py) |
| Backend config | [backend/app/core/config.py](backend/app/core/config.py) |
| Backend health | `backend/app/routers/health.py` |
| Transit routes | [backend/app/api/routes/transits.py](backend/app/api/routes/transits.py) |
| Natal routes | [backend/app/api/routes/natal_interpretation.py](backend/app/api/routes/natal_interpretation.py) |
| Cache store | [backend/app/services/performance/cache_store.py](backend/app/services/performance/cache_store.py) |
| Selection V3 spec | [docs/natal_selection_v3.md](docs/natal_selection_v3.md) |
| Arketip V1 spec | [docs/archetype_test_system_v1.md](docs/archetype_test_system_v1.md) |
| Narrative V2 spec | [docs/narrative_v2_product_spec.md](docs/narrative_v2_product_spec.md) |
| **Profile V8 audit + roadmap** | [docs/profile_v8_audit_and_roadmap.md](docs/profile_v8_audit_and_roadmap.md) |
| **Profile V8 uygulama planı** | [docs/profile_v8_implementation_plan.md](docs/profile_v8_implementation_plan.md) |
| **Profile V8 baseline metrikleri (Sprint 0)** | [docs/profile_v8_baseline_metrics.md](docs/profile_v8_baseline_metrics.md) |
| Mobile loading | [docs/mobile_loading_tuning.md](docs/mobile_loading_tuning.md) |
| Regression watchlist | [docs/regression_watchlist.md](docs/regression_watchlist.md) |
| Performance report | [docs/performance_instrumentation_report.md](docs/performance_instrumentation_report.md) |
| App Store checklist | [docs/shou_app_store_release_checklist.md](docs/shou_app_store_release_checklist.md) |
| Visual system | [docs/visual-system/README.md](docs/visual-system/README.md) |
| GoRouter | [mobile/lib/app/app_router.dart](mobile/lib/app/app_router.dart) |
| API client | [mobile/lib/app/api/api_client.dart](mobile/lib/app/api/api_client.dart) |
| Tabs shell | [mobile/lib/app/tabs/tabs_shell.dart](mobile/lib/app/tabs/tabs_shell.dart) |
| Load tuning | [mobile/lib/app/performance/load_tuning.dart](mobile/lib/app/performance/load_tuning.dart) |
| Tone config | [config/tone/tone.yaml](config/tone/tone.yaml) |
| Transit selection config | [config/transit/selection_v3_config.yaml](config/transit/selection_v3_config.yaml) |
| Render config | [render.yaml](render.yaml) |
| Proje kuralları | [CLAUDE.md](CLAUDE.md) |

---

## 14. Bu Dökümanı Güncelleme

Bu döküman **canlı**dır. Aşağıdaki durumlarda güncelle:
- Yeni endpoint, yeni tab, yeni tab-altı flow eklendiğinde → bölüm 3.5 / 4.5
- Caching stratejisi değiştiğinde → bölüm 3.8
- Yeni bağımlılık eklendiğinde → bölüm 3.2 / 4.2
- Roadmap durumu değiştiğinde → bölüm 12
- Yeni mimari spec doc çıktığında → bölüm 13 cheat sheet'e ekle
- Marka / store bilgileri değiştiğinde → bölüm 1.4 / 10.1

> "Son güncelleme" tarihini yukarıda güncellemeyi unutma.
