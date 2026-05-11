# Home / Profile Surface Cleanup Plan

**Tarih:** 2026-04-27
**Kaynak:** [`home_profile_surface_alignment_audit.md`](home_profile_surface_alignment_audit.md)
**Referans:** [`shou_surface_orchestration.md`](shou_surface_orchestration.md), [`projection_voice_sprint2_plan.md`](projection_voice_sprint2_plan.md), [`docs/voice/voice_spec.md`](../voice/voice_spec.md) v2.1

> **Bu doküman implementation içermez.** Audit bulgularını P0/P1/P2 önceliğe koyar, her kalemi sahiplenebilir bir backlog item'ı olarak yazar. Hiç kod değiştirilmedi.

---

## 0. Özet

25 section incelemesinden çıkan iş kalemleri 3 önceliğe ayrıldı:

| Öncelik | Konu | Kalem sayısı | Toplam effort |
|---|---|---|---|
| **P0** Release blockers | Mock/hardcoded içerik + yanlış yüzeydeki section + obvious mismatch | 6 | ~3.5 sprint günü |
| **P1** Spec updates | Orchestration spec'e eksik 6 Profile rolü + Home expansion | 1 (doc-only) | ~0.5 sprint günü |
| **P2** Semantic refinement | first_impression vs first_felt + proof anchors + share line role | 3 | ~2 sprint günü |

**Toplam:** ~6 sprint günü (Sprint 2 voice work ile paralel yürütülebilir, çakışma yok)

**Production gating**: P0 kalemleri release öncesi mutlaka kapatılmalı. Mock copy kullanıcıya sızdığı an "hayalet kullanıcı" / "lorem ipsum" hissi yaratır — App Store review riski + güven kaybı.

---

## 1. 🔴 P0 — Release blockers

### P0-1 — `_ManifestoTitle` mock copy'yi kaldır
**Kaynak:** audit §1.2 + §5.1
**Konum:** `mobile/lib/app/tabs/home_page_v2.dart:319-387` (`_ManifestoTitle` widget)

**Mevcut durum:**
```dart
// Hardcoded:
"Sahnede olmak istemediğin anlar, en çok bakıldığın anlar olabilir."
```
Her kullanıcıya birebir aynı title gösteriliyor — Home V2'nin Core Hook role'ü editorial bir lorem ipsum'a sıkışmış.

**Hedef:** Backend `core_story_ui.headline` veya `share_line` projection'ından kullanıcıya özel hook çek.

**İmplementasyon yaklaşımı (kod yazmadan):**
1. `home_v2_providers.dart`'ta yeni accessor: `homeV2HookProvider` → snapshot'tan `core_story_ui.headline` veya `share_line` döner
2. `_ManifestoSection` `ConsumerWidget` zaten — `ref.watch(homeV2HookProvider)` ile çek
3. Boş gelirse fallback: `core_story_ui.text` ilk cümle (truncate)
4. Hâlâ boş ise — **section gizlensin**, mock title koyma

**Risk:** LOW. Backend zaten bu field'ları üretiyor (`profile_v8_payload_builder` + `core_story_ui`); adapter'a tek getter ekleme.

**Tahmini effort:** 0.5 sprint günü.

**Kabul kriteri:**
- Title backend'den geliyor
- Boş kullanıcıda section gracefully gizleniyor (mock fallback yok)
- Voice spec §1.4 "you often feel..." anti-pattern'i tetiklemiyor

---

### P0-2 — `_SkyQuote` mock copy'yi kaldır
**Kaynak:** audit §1.3 + §5.1
**Konum:** `home_page_v2.dart:811-857`

**Mevcut durum:**
```dart
// Hardcoded:
"Ay Aslan'da — görünmek değil, görülmek istiyor."
```

**Karar gereken:** Bu cümle "sky-now context" rolü — backend bu role için spesifik bir field üretmiyor. İki opsiyon:
- **A**: Backend'de `narrative.sky_now_quote` field'ı oluştur (yeni field — schema değişikliği)
- **B**: Section'ı kaldır + Sky tab'ına yönlendir (Sky tab'da `sky_event_feed_page.dart` zaten benzer içerik için)

**Önerim: B** — yeni schema field'ı eklemek bu sprint'in scope'unda değil. Sky tab'ı zaten var; Home'da eyebrow + sky rail kalır, central quote kaldırılır VEYA `pullQuote` (zaten live `periodCore.upperMeaning`'a bağlı) ile değiştirilir.

**Risk:** MEDIUM. UX kaybı: tek satırlık güçlü editorial moment kaybolur. PM kararı gerek.

**Tahmini effort:** 0.25 sprint günü (sadece kaldırma; opsiyon A seçilirse 1.5 gün — yeni field + builder + adapter)

**Kabul kriteri:**
- Hardcoded sky quote görünmüyor
- Section ya kaldırılmış ya da live data'ya bağlanmış
- Sky rail kendi başına anlamlı (eyebrow + rail yeterli context)

---

### P0-3 — `_NearSection` (friends rail) hide / empty state
**Kaynak:** audit §1.5 + §5.1
**Konum:** `home_page_v2.dart:1411-1693`

**Mevcut durum:**
```dart
static const _friends = <_FriendAviData>[
    _FriendAviData(name: 'Sen',   meta: 'PAYLAŞ',  initial: '+', tone: _FriendTone.me),
    _FriendAviData(name: 'Mira',  meta: 'OĞLAK',   initial: 'M', tone: _FriendTone.lime),
    _FriendAviData(name: 'Ela',   meta: 'BALIK',   initial: 'E', tone: _FriendTone.lavender),
    _FriendAviData(name: 'Burak', meta: 'İKİZLER', initial: 'B', tone: _FriendTone.blush),
    ...
];
```
5 hardcoded "kullanıcı arkadaşı" — ürün gerçekliğinde kullanıcının böyle bir listesi yok. Bond feature live olana kadar **kesinlikle** mock görünmemeli.

**Hedef:** Bond feature production'a geçene kadar section'ı **gizle** veya empty-state'e dönüştür ("Henüz kimseyi eklemedin → Bond'da partner ekle").

**Karar:**
- **Kısa vade:** section visibility'yi `kBondFeatureEnabled` flag'e bağla, default `false`
- **Empty state copy:** "Bond'da partnerinizin haritasını ekleyin → onun bugününü buradan görün."
- **Live data accessor:** `bondPartnersProvider` (yoksa create) — varsa rail'i live data ile doldur

**Risk:** LOW. Section gizlemek izole değişiklik; UI compose'unda kontrollü.

**Tahmini effort:** 0.5 sprint günü.

**Kabul kriteri:**
- Mock isimler/burçlar görünmüyor
- Empty state Bond feature pitch'i veriyor
- Bond live olduğunda rail gerçek partner data'sına bağlı

---

### P0-4 — `_FeedSection` (friends' transit posts) hide / empty state
**Kaynak:** audit §1.6 + §5.1
**Konum:** `home_page_v2.dart:1694-1820+`

**Mevcut durum:** 4 tamamen hardcoded "friend transit post" (`_FeedPostMira`, `_FeedPostEla`, `_FeedPostBurak`, `_FeedPostDeniz`). Her biri ~80-160 char editorial copy + sahte avatar.

**Hedef:** Aynı `kBondFeatureEnabled` flag'i ile gizle. Live'da Bond partner'larının daily transit teaser'larını çek.

**Karar:** P0-3 ile **tek paket** olarak ele al — Near + Feed birlikte feature'lansın veya birlikte gizlensin. Yarım state çok kötü ("avatar var ama post yok" gibi).

**Risk:** LOW (gizleme) / MEDIUM (live'a bağlama — Bond infra dependency).

**Tahmini effort:** 0.5 sprint günü (gizleme); 1.5 gün (live bağlama, Bond infra hazırsa).

**Kabul kriteri:**
- 4 hardcoded post görünmüyor
- Bond paywall awareness varsa empty state Pro CTA içeriyor

---

### P0-5 — `_ChartWheelSection` Home'dan kaldır → Profile'a taşı
**Kaynak:** audit §1.7 + §5.2
**Konum:** `home_page_v2.dart:2361+` (definition); render order line 61

**Mevcut durum:** Chart wheel Home V2'de inline render ediliyor.

**Spec ihlali:** `shou_surface_orchestration.md` §2.1 Home rules:
> Must be short: orders 1–3.
> Must not be deep: no long narrative body.

Chart wheel **deep visual proof element** — Profile Cards yüzeyinin `proof_card` rolünde olması gerek. Home'da olması spec'in §2.1 row 4 (Context Surrogate, 1 short line) ile çelişiyor.

**Hedef:**
- Home V2 render listesinden `_ChartWheelSection` kaldırılsın (line 61)
- Profile Cards yüzeyine `proof_card` formunda eklensin (`profile_v8_sections.dart`'ta yeni section)
- Profile detail sheet'lerin altında "see chart wheel" CTA olabilir

**Risk:** MEDIUM. Profile'da nereye yerleştirileceği UX kararı; chart wheel widget reuse'u sorun yok ama Profile'ın dark theme'i ile entegrasyon test gerek.

**Tahmini effort:** 0.75 sprint günü (Home kaldırma 0.1 + Profile entegrasyonu 0.5 + UX gözden geçirme 0.15).

**Kabul kriteri:**
- Home V2'de chart wheel görünmüyor
- Profile'da Profile Cards alt-yüzeyinde chart wheel render ediliyor
- Profile detail sheet'leri chart wheel'a tıklamayla açılıyor (mevcut tap pattern korunur)

---

### P0-6 — Section reordering (Home V2 spec uyumu)
**Kaynak:** audit §1.8 + §5.4
**Konum:** `home_page_v2.dart:53-67` (Column children)

**Mevcut sıra:**
```
Manifesto → Sky → Askew → Near → Feed → ChartWheel → PullQuote → Stickers → Forum → Week → Endpiece
```

**Spec hedefi (orchestration §2.1):**
```
1. Core Hook         (Manifesto)
2. Effect            (PullQuote — şu an row 7'de!)
3. Mechanism/Potential (Week highlight — şu an row 10'da!)
4. Context           (Week strip)
5. Share CTA         (Askew — şu an row 3'te ama doğru rolde)
```

**Hedef sıra (P0-1..P0-5 sonrası):**
```
1. Manifesto (Hook — backend'e bağlı)
2. PullQuote (Effect)
3. Week (Context strip + highlight)
4. Sky rail (sky-now feed — pattern-level work sonrası kalacak / taşınacak)
5. Askew (Share CTA)
6. Endpiece
```

**Çıkarılanlar:** Near, Feed (Bond live olana kadar gizli), ChartWheel (Profile'a taşındı), Stickers (rol belirsiz, defer), Forum (forum tab'a yönlendir).

**Risk:** LOW. Sadece Column children sırası ve gizleme; visual continuity testi gerek.

**Tahmini effort:** 0.5 sprint günü (P0-1..P0-5'in son adımı, hepsi tamamlanınca yapılır).

**Kabul kriteri:**
- Home V2 sıra: Manifesto → PullQuote → Week → Sky → Askew → Endpiece
- 6 section gizli/taşınmış (Near, Feed, ChartWheel, Stickers, Forum + ManifestoTitle/SkyQuote temiz)
- Visual rhythm bozulmamış (PM/UX onayı gerek)

---

### P0 toplam

| # | İş | Effort |
|---|---|---|
| P0-1 | ManifestoTitle backend bağlama | 0.5 |
| P0-2 | SkyQuote remove veya bağla | 0.25 (kaldır) / 1.5 (bağla) |
| P0-3 | NearSection gizle/empty state | 0.5 |
| P0-4 | FeedSection gizle/empty state | 0.5 |
| P0-5 | ChartWheel Home → Profile | 0.75 |
| P0-6 | Home reordering | 0.5 |

**Min:** 3.0 sprint günü (kaldırma yolu) **Max:** 4.25 sprint günü (P0-2 backend bağlama yolu seçilirse)

---

## 2. 🟡 P1 — Spec updates (doc-only)

Bu kalemler **hiç kod değiştirmez** — sadece `shou_surface_orchestration.md`'i v1'den v2'ye taşır. Backend zaten bu rolleri üretiyor; UI zaten render ediyor; spec catch-up yapmıyor.

### P1-1 — Orchestration spec v2 güncellemesi
**Kaynak:** audit §3.3 + §5.3
**Konum:** `docs/system/shou_surface_orchestration.md`

**Eklenmesi gereken roller** (audit §3.3 + §4 karar matrisinden):

#### 2.1.a Differentiators / Unique Facts
- **Pozisyon:** Pattern Label Surrogate alt-rolü
- **Surface:** Profile Top, Profile Cards
- **Card type:** `unique_fact_card` (yeni) veya `list_card` varyantı
- **Voice mode:** `pattern_naming_mode` + spesifik referans (orb, derece)
- **Length:** 35-90 chars per fact, 3-5 fact strip
- **Backend field:** `profile_v8.differentiators[]` (UniqueFactPayload)
- **Mobile widget:** `_V8UniqueMetricSlab`

#### 2.1.b Conversation Hooks
- **Pozisyon:** Profile Cards bonus role (mevcut Mechanism + Shadow + Potential + Cause + Proof setine 6.'sı)
- **Surface:** Profile Cards
- **Card type:** `conversation_card` (yeni)
- **Voice mode:** `effect_voice` (anchored to relational dynamic)
- **Length:** 1-2 sentences, 140-280 chars
- **Backend field:** `profile_v8.conversation_hooks` (EditorialSectionPayload)
- **Mobile widget:** `_V8ConversationCard`

#### 2.1.c Affects-You (list-row insight)
- **Pozisyon:** Effect alt-rolü, list-row form
- **Surface:** Profile Cards
- **Card type:** `insight_list_card` (mevcut `insight_card` + `list_card` kombo)
- **Voice mode:** `effect_voice` (per row)
- **Length:** 3-5 row, her row 25-60 chars
- **Backend field:** `profile_v8.affects_you` (EditorialListSectionPayload)
- **Mobile widget:** `_V8AffectsCard`

#### 2.1.d First Felt vs First Impression ayrımı
- **First Impression** — outer perception: "people read you as..."
- **First Felt** — inner experience: "you feel like..."
- İki ayrı semantic role olarak listele (audit §5.5)
- **Voice mode farkı:** First Impression = `effect_voice` (gözlem); First Felt = `cause_voice` (içe dönük)
- Voice spec §2 axes (warmth, directness, certainty) ayrımı doc'lansın

#### 2.1.e Domain-scoped Insight Card
- **Pozisyon:** Profile Cards yeni alt-eksen
- **Surface:** Profile Cards
- **Card type:** `domain_card`
- **Voice mode:** `effect_voice` veya `mechanism_voice` (domain'e bağlı)
- **Length:** 2-3 sentences, 220-480 chars
- **Domains:** intimacy / mind / career / home / luck (Türkçe: yakınlık / zihin / kariyer / ev / şans)
- **Backend field:** `profile_v8.intimacy`, `profile_v8.mind` (her domain için ayrı)
- **Mobile widget:** `_V8SectionCard` (paramı `domain` parametresi alır)

#### 2.1.f Archetype Portal CTA
- **Pozisyon:** Profile Cards close (post-content CTA)
- **Surface:** Profile Cards (last position)
- **Card type:** `cta_card` (yeni)
- **Voice mode:** `share_line_mode` + functional CTA framing
- **Length:** headline 6-12 words + body 1-2 sentences + 1 CTA label
- **Backend field:** `profile_v8.archetype_portal` (ArchetypePortalPayload)
- **Mobile widget:** `_V8CtaSection`
- **Behavior:** tap → archetype experience flow (mevcut deep-link)

#### 2.1.g Sky-now feed (Home § yeni)
- **Pozisyon:** Home Context expansion (mevcut row 4 — Context Surrogate genişletilir)
- **Surface:** Home (alternatif: Sky tab'a delegate)
- **Card type:** `sky_now_rail_card` (multi-card horizontal rail)
- **Voice mode:** `context_mode` + `effect_hook` per card
- **Length:** title 6-14 words + sub 1 sentence + meta chip
- **Backend field:** `narrative.sky_now_cards[]` (yeni veya mevcut field ne ise)
- **Mobile widget:** `_SkyRail` + `_SkyCard`
- **Karar:** Home'da kalır mı, Sky tab'a taşınır mı — PM kararı (P0-2 ile bağlı)

#### 2.1.h Friends Lattice (Bond — Home'dan ayrı)
- **Pozisyon:** Yeni surface `Bond` (audit §1.5/§1.6 — orchestration spec şu an Home/Profile/Story/Share/Explainability eksenli; Bond yeni eksen olarak eklenmeli)
- **Surface:** Bond tab
- **Card types:** `partner_avi_card`, `partner_transit_card`
- **Backend fields:** Bond partnership data + her partner için transit teaser
- **Mobile widget:** `_NearRail` + `_FeedPost*` (Bond tab'a taşınmış)

**Toplam yeni section spec'te:** 8 yeni rol/section tanımı

**Risk:** ZERO (doc-only).

**Tahmini effort:** 0.5 sprint günü (yazım + cross-reference + diagram update).

**Kabul kriteri:**
- `shou_surface_orchestration.md` v2 olarak güncellenmiş
- 8 yeni rol her surface tablosunda doğru pozisyonda
- Backend payload field ↔ semantic role ↔ mobile widget mapping eksiksiz
- Voice mode listesi (§3) yeni mode'larla genişletilmiş

---

## 3. 🟢 P2 — Semantic refinements

Bu kalemler ürün-derinliği iyileştirmesi; release blocker değil ama UX kalitesini yükseltir. Sprint 3'e bırakılabilir.

### P2-1 — first_impression vs first_felt anlam ayrımı
**Kaynak:** audit §2.10 + §5.5

**Mevcut sorun:** Profile V8'de iki ayrı section ("İLK İZLENİM" + "İLK HİSSEDİLEN ŞEY") yan yana duruyor. Backend iki ayrı field üretiyor (`first_impression`, `first_felt`) ama UI label'ları kullanıcı tarafında **anlamca yakın okunuyor** — fark net değil.

**Hedef:** İki section'ın semantic ayrımını hem voice hem label seviyesinde netleştir:

| Field | Semantic role | Voice mode | UI label |
|---|---|---|---|
| `first_impression` | Outer perception ("dış göze nasıl görünüyorsun") | `effect_voice` (gözlem, warmth 0.55, certainty 0.6) | "DIŞARIDAN OKUNAN" veya "İLK İZLENİM" (kalır) |
| `first_felt` | Inner experience ("içeride nasıl hissediyorsun") | `cause_voice` (içe dönük, warmth 0.7, certainty 0.45) | "İÇERİDE OLAN" veya "İLK HİSSEDİLEN" |

**İmplementasyon yaklaşımı (kod yazmadan):**
1. Backend `profile_v8_payload_builder.py`'da iki field'ın content generation logic'inin **explicit ayrım** yapması gerek (selection + projection level)
2. Mobile UI label'larını netleştir
3. Voice spec'e §2.7 yeni "perception axis" doctrine ekle (outer vs inner)

**Risk:** MEDIUM. Backend selection logic değişikliği — `_V8FirstFeltCard`'ın gerçekten farklı bir semantic'i kapsadığından emin olmak gerek; şu an aynı pool'dan çekiyor olabilir.

**Tahmini effort:** 1.0 sprint günü (Sprint 3 semantic enrichment paketinde).

**Kabul kriteri:**
- İki section'ın user testing'de (5+ kullanıcı) anlam ayrımı netleşmiş
- Backend selection iki field'a farklı fragment havuzlarından seçim yapıyor
- Voice mode kalibrasyonu spec'e işlenmiş

---

### P2-2 — Raw Proof Anchor (proof_card) Profile'a entegrasyon
**Kaynak:** audit §3.2 + orchestration §2.3 row 5

**Mevcut sorun:** Orchestration spec Profile Cards yüzeyinde **proof_card optional but available** diyor. V8 Profile'da bu rol explicit olarak yok — proof bilgisi (orb, derece, gezegen-aspekt) detail sheet'lerde gizli.

**Hedef:** Profile Cards'ın altında veya her insight_card'ın içinde **opt-in expandable proof row** ekle.

**Tasarım alternatifleri:**
- **A**: Her V8 section card'ının altına "Kanıt" toggle — basıldığında orb + aspect + house gösterir
- **B**: Profile Cards'ın sonuna global "Tüm kanıtlar" section — `proof_raw` payload'ından list-form
- **C**: Detail sheet'in zaten yaptığını UI'da explicit "see why" CTA olarak yüzeye çıkar

**Önerim: C** — kullanıcı tarafında en az invazif; mevcut detail sheet pattern'ı zaten proof'u taşıyor; sadece "see why" link'ini card'lara explicit ekle.

**Risk:** LOW. UI-only değişiklik, backend zaten `proof_raw` üretiyor.

**Tahmini effort:** 0.5 sprint günü.

**Kabul kriteri:**
- Profile Cards her section'da "Kanıt" / "Why" CTA görünür
- Tap → mevcut detail sheet açılır + proof row vurgulu
- Voice spec §4.3 "spesifik referans body'de evet" doctrine'i UI'da artık kullanıcıya explicit

---

### P2-3 — Share Line Surrogate (Share CTA) Profile'a entegrasyon
**Kaynak:** audit §3.2 + orchestration §2.2 row 4

**Mevcut sorun:** Orchestration spec Profile Top'ta Share Line (row 4) bekliyor — kısa shareable cümle ("6-12 words"). Profile V8'de bu rol explicit yok — `_V8CtaSection` (archetype portal) functional CTA, share değil.

**Hedef:** Profile Top veya Profile Cards'ın sonuna **share-ready snippet** ekle:
- Backend `core_story_ui.share_line` veya `projection.share_line` field'ı oluştur
- UI'da küçük share button + text snippet
- Tap → system share sheet (Instagram story, twitter, copy)

**Önerim:** Profile sayfasının altına (mevcut CTA'dan ayrı) bir mini share row.

**Risk:** MEDIUM. Backend share_line field'ı eklemek schema değişikliği ve voice spec §13 (yüzey kalıpları) Share Card kuralları ile entegre olmak zorunda.

**Tahmini effort:** 1.0 sprint günü (backend share_line field 0.5 + mobile share row + share intent integration 0.5).

**Kabul kriteri:**
- Backend `share_line` field'ı production-ready
- Profile sayfasında share row görünür
- Tap → share sheet açılır, snippet pre-filled
- Voice spec §13 Share Card kuralları (asla raw astro jargon, 6-12 word) korunur

---

### P2 toplam

| # | İş | Effort |
|---|---|---|
| P2-1 | first_impression vs first_felt netleştirme | 1.0 |
| P2-2 | Proof anchor Profile'a entegre | 0.5 |
| P2-3 | Share line Profile'a entegre | 1.0 |

**Toplam:** 2.5 sprint günü (Sprint 3 önerilir)

---

## 4. Sprint 2/3 ile bağ ve sıra önerisi

```
   ┌───────────────────────────────────┐
   │ ŞİMDİ (paralel)                   │
   │ ──────────────────                │
   │ • Sprint 2 voice tuning           │
   │   (template + bundle headlines)   │
   │ • P0 cleanup (3-4.25 gün)         │
   │ • P1 spec update (0.5 gün, doc)   │
   └────────────────┬──────────────────┘
                    │
   ┌────────────────┴──────────────────┐
   │ SPRINT 3                          │
   │ ──────────                        │
   │ • Sprint 3 semantic enrichment    │
   │   (PAST_LAYER / TALENT / MISSION) │
   │ • P2-1 first_impression/first_felt│
   │ • P2-2 proof anchor profile       │
   │ • P2-3 share line                 │
   └───────────────────────────────────┘
```

**Bağımlılıklar:**
- P0 ve Sprint 2 voice tuning **bağımsız** — paralel yürür. Voice tuning copy seviyesinde, P0 surface compose level'da.
- P1 doc-only — diğer kalemlerden sonra yazılabilir (Sprint 2 + P0 closing'de).
- P2 Sprint 3 ile birlikte — semantic enrichment paketi ile aynı tema (selection-adjacent).

---

## 5. Karar checkpoint'leri

P0 başlamadan önce ürün/PM kararı bekleyen 3 nokta:

### 5.1 SkyQuote — kaldır mı, backend'e bağla mı? (P0-2)
- **Kaldırma**: hızlı, güvenli, UX'te tek satırlık güçlü editorial moment kaybı
- **Backend'e bağlama**: schema değişikliği (yeni field), 1.5 gün ekstra effort, ama UX impact yüksek

PM önerisi: kısa vadede kaldır + Sprint 3'te backend field eklenip geri yükle.

### 5.2 Bond / Friends — gizle mi, paywall pitch mi? (P0-3 + P0-4)
- **Gizle**: zero UI footprint, kullanıcı feature'ın varlığından haberdar değil
- **Empty state Pro pitch**: "Partneri ekle, onun bugününü gör" — Pro upsell + feature awareness

PM önerisi: empty state pitch (Pro funnel'a katkı yapar).

### 5.3 ChartWheel Profile'da nereye? (P0-5)
- **Üst** (identityQuote'un altı): visual proof olarak en görünür
- **Profile Cards içinde** (insight strip'in altı): orchestration spec'e en yakın
- **Section detay sheet'lerinin içine entegre**: minimal Home benzeri "see chart" CTA

PM/UX önerisi: ortayı seç — InsightStrip'ten sonra Profile Cards'ın `proof_card` rolünde.

---

## 6. Validation strategy

P0 her madde için kabul kriterlerinde belirtildi. Genel test stratejisi:

### 6.1 Visual regression
Home V2 ve Profile V8 sayfalarının golden screenshot'ları:
- Pre-cleanup baseline (current main)
- Post-P0 baseline (mock-free)
- Diff inspection: visible card count, copy length, mock vs live data

### 6.2 Live data smoke
P0-1 (manifesto), P0-2 (sky), P0-3/4 (Bond) için:
- Cold start fix01-fix08 charts ile Profile + Home render test
- Live narrative data hot path'te boş gelirse section gizleniyor mu?
- Mock fallback'a düşmüyor mu?

### 6.3 Phrase lint genişletme
Sprint 1'in `test_projection_phrase_lint.py`'sine yeni satırlar:
- "Sahnede olmak istemediğin anlar" — manifesto title hardcoded check
- "Ay Aslan'da — görünmek değil" — sky quote hardcoded check
- "Mira", "Ela", "Burak", "Deniz" + tone enum string'leri — friends mock check

Bu lint mock copy'nin geri sızmasını koddan engeller.

### 6.4 PM/UX visual review
P0-5 (chart wheel taşıma) ve P0-6 (reorder) sonrası PM'den 1 saatlik visual review.

---

## 7. Out of scope

Bu plan dokunulmayacaklar:

- ❌ Code (sadece backlog item ve sıra)
- ❌ Voice copy / projection phrase (Sprint 2'nin işi)
- ❌ Selection logic
- ❌ Schema changes — P2-3 share_line ve P0-2 sky_quote backend field'ları açıklandı ama bu plan onları **önermiyor**, PM kararına bırakıyor
- ❌ EN paritesi (TR-only)
- ❌ Story / Share Card / Explainability surfaces (Home + Profile dışı yüzeyler)
- ❌ Story Studio / Bond tab UI (Home'dan referanslananlar haricinde)

---

## 8. Sonuç

P0 (release blockers) **6 kalem, ~3-4.25 sprint günü** — Sprint 2'nin voice work'ü ile **paralel** koşulabilir. Mock copy'lerin app store review veya ilk kullanıcı kohort'una sızmasını engelliyor.

P1 (doc-only) **0.5 sprint günü** — orchestration spec'i v2'ye taşır, backend ↔ UI gerçeğini yakalatır. Risk yok.

P2 (semantic refinement) **2.5 sprint günü** — Sprint 3 semantic enrichment paketi ile birlikte, ürün derinliği işi.

**Toplam:** ~6 sprint günü, çoğunluğu Sprint 2 ile paralel + Sprint 3'e taşan bir kuyruk.

**Kritik öneri**: P0-3 + P0-4 (Bond mock cleanup) Bond paywall stratejisinin (önceki konuşmada plan yapılan timing/ilişki paywall'ı) erken impression'ını şekillendirir. Empty state copy "Pro'da partnerini ekle" pitch'i ile yazılırsa Bond launch'tan önce **awareness** kuruyor.
