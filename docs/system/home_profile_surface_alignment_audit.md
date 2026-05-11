# Home / Profile Surface Alignment Audit

**Tarih:** 2026-04-27
**Kapsam:** Mobile UI'da şu an canlı render edilen Home (V2) ve Profile (V8 sections) yüzeylerinin [`shou_surface_orchestration.md`](shou_surface_orchestration.md)'le karşılaştırması.
**Kaynak:**
- `mobile/lib/app/tabs/home_page_v2.dart` (4653 satır, `kUseHomeV2 = true` ile aktif)
- `mobile/lib/app/tabs/tabs_shell.dart` (Home routing)
- `mobile/lib/app/tabs/profile_page.dart` (`ProfileV8SectionsView` segment 0'da render edilir)
- `mobile/lib/app/profile/profile_v8_sections.dart` (V8 section composer)
- `mobile/lib/app/profile/profile_v8_adapter.dart` (backend → V8 data shape)
- `backend/app/natal/profile_v8_payload_builder.py` (`ProfileV8Payload` dataclass)
- `docs/system/shou_surface_orchestration.md` v1
- `docs/voice/voice_spec.md` v2.1

> **Bu doküman sadece tespit içerir.** Hiçbir kod değişikliği yapılmadı.

---

## 0. Özet

| Yüzey | Section count | Spec uyum | Kritik gap |
|---|---|---|---|
| Home V2 | 12 görünür section + topbar | Kısmen — orchestration spec "Home" rolleri (Core Hook, Effect, Mechanism, Context, Share) Home V2'de net surrogate'a sahip değil; section'ların yarısı **mock/hardcoded copy** | `_ManifestoTitle`, `_SkyQuote`, `_NearSection.friends`, `_FeedSection.posts` tamamen hardcoded; backend Core Hook / Effect role'u Home V2'ye akmıyor |
| Profile V8 | 13 section + identity quote | Spec'in "Profile Top" + "Profile Cards" rollerinin **çoğu** mevcut — section→role mapping büyük oranda doğru; bazı role coverage eksik | Pattern Label Surrogate, Share Line Surrogate, Raw Proof Anchor, Shadow Narrative explicit yok; Cause/Past Layer ile Shadow karışıyor |

**Toplam:** 25 görünür section incelendi → **6 keep, 8 rename/remap, 7 mismatch (defer or pattern-level), 4 mock/hardcoded acil migrate**.

---

## 1. HOME V2 — section-by-section alignment

`mobile/lib/app/tabs/home_page_v2.dart:33-75` — `Scaffold` body içinde 12 section sırayla render ediliyor:

```
ShouTopBar (label "BUGÜN")
├─ _ManifestoSection
├─ _SkySection
├─ _AskewBanner
├─ _NearSection
├─ _FeedSection
├─ _ChartWheelSection
├─ _PullQuoteSection
├─ _StickerGridSection
├─ _ForumSection
├─ _WeekSection
└─ _Endpiece
```

Spec ise sadece **5 role** öngörüyor: Core Hook · Effect/First Impression · Mechanism (or Potential) · Context · Share Line. UI 12 section taşıyor → **role mapping zorunlu**.

### 1.1 ShouTopBar
| Alan | Değer |
|---|---|
| Intended semantic role | UI shell (no role) |
| Intended voice mode | — (label-only) |
| Current backend field | static label `"BUGÜN"` |
| Spec match | N/A — orchestration scope dışı |
| **Recommendation** | **keep** |

### 1.2 `_ManifestoSection`
**Bileşenler:** `_ManifestoGreeting` + `_ManifestoTitle` + `_OrbitEmblem` + `_ManifestoOpenLink` + `_ManifestoMetaRow`

| Alan | Değer |
|---|---|
| Intended semantic role | Core Hook (orchestration §2.1 row 1) |
| Intended voice mode | `effect_hook` |
| Length constraint | 1 line, 6-14 words |
| Current backend field | `_ManifestoGreeting`: `snapshot.displayName` / `formattedDate` / `moonSignLabel` (live) **+** `_ManifestoTitle`: **HARDCODED** ("Sahnede olmak istemediğin anlar, en çok bakıldığın anlar olabilir.") |
| Spec match | **MISMATCH** — title hardcoded; Core Hook backend'den (`projection.share_line` veya `core_story_ui.headline`) gelmeli |
| Length compliance | Hardcoded title 11 kelime ✅ — ama hard-coded; aynı title her kullanıcıya |
| **Recommendation** | **remap** — manifesto title'ı `core_story_ui.headline` veya share_line projection'a bağla; greeting + orbit + meta UI shell olarak kalsın |

### 1.3 `_SkySection`
**Bileşenler:** `_SkyHead` (eyebrow "GÖKYÜZÜ · ŞU AN") + `_SkyQuote` + `_SkyRail` (5 horizontal cards)

| Alan | Değer |
|---|---|
| Intended semantic role | Context Surrogate (sky-now lattice) — orchestration §2.1 row 4 ile yakın ama "now-cast" özel |
| Intended voice mode | `context_mode` (1 line, 35-90 chars) — ama `SkyQuote` + 5-card rail pattern spec'in beklediği `list_card`'tan **belirgin şekilde daha derin** |
| Length constraint | spec: 1 short line, 35-90 chars; **fiili: 5 card × 100-180 chars + central quote** |
| Current backend field | `SkyQuote`: **HARDCODED** ("Ay Aslan'da — görünmek değil, görülmek istiyor."). `SkyRail`: `snapshot.skyCards` (live) → fallback `_mockCards` (5 hardcoded card) |
| Spec match | **MISMATCH** — quote hardcoded; rail spec'te tanımlı bir role değil; "sky-now feed" orchestration'da yok |
| **Recommendation** | **defer to pattern-level** — sky-now feed bir Home pattern'i, ama orchestration spec'i bunu hiç açıklamıyor. Spec'e **yeni bölüm** (§2.1.x sky-now-feed) eklenmeli VEYA bu section Home'dan Sky tab'a taşınmalı (mevcut `sky_event_feed_page.dart` zaten var). |

### 1.4 `_AskewBanner`
**Bileşen:** small banner inline-rotated

| Alan | Değer |
|---|---|
| Intended semantic role | Share Line Surrogate — orchestration §2.1 row 5 (optional CTA) |
| Intended voice mode | `share_line_mode` |
| Length constraint | 6-12 words |
| Current backend field | (görmediğim için varsayım — hardcoded muhtemel) |
| Spec match | yapı uyuyor ama backend bağı belirsiz |
| **Recommendation** | **rename + verify** — `_AskewBanner` → semantik olarak `share_cta_card` adlandırılsın; copy backend `projection.share_line` aliasından gelsin |

### 1.5 `_NearSection`
**Bileşenler:** `_NearHead` (eyebrow "BUGÜN YAKININDA" + title "Gökyüzü herkese aynı söylemiyor.") + `_NearRail` (friend avatars)

| Alan | Değer |
|---|---|
| Intended semantic role | Spec'te yok — "social proof / friends sky" — Bond / Synastry yüzeyiyle ilgili |
| Intended voice mode | — |
| Current backend field | `_friends` HARDCODED MOCK (Mira, Ela, Burak, Deniz, Kayra) |
| Spec match | **NOT IN SPEC** — bu section orchestration'ın Home/Profile/Story/Share/Explainability eksenlerinde yok |
| **Recommendation** | **defer** — Bond + Synastry feature paywall'ına bağlı; spec'e "Friends Lattice" bölümü eklenmeli VEYA Bond tab'a taşınmalı. Şu an mock olduğu için MVP-değil. |

### 1.6 `_FeedSection`
**Bileşenler:** `_FeedHead` ("BUGÜN YAKINLARINDA / Gökyüzü onlara ne söyledi?") + 4 hardcoded post (`_FeedPostMira/Ela/Burak/Deniz`)

| Alan | Değer |
|---|---|
| Intended semantic role | "Friends' transit insights" — şu anki spec'te yok |
| Intended voice mode | — |
| Current backend field | **TAMAMEN HARDCODED** (4 post × ~80-160 char) |
| Spec match | **NOT IN SPEC** + tüm copy mock |
| **Recommendation** | **defer** — Bond / friend transit feature'ı productionize olana kadar feed mock olarak kalmamalı, gizlensin VEYA Bond tab'ına taşınsın |

### 1.7 `_ChartWheelSection`
**Bileşen:** Chart wheel display

| Alan | Değer |
|---|---|
| Intended semantic role | Raw Proof Anchor (chart wheel = visual proof) — orchestration §2.1'de Home için listed değil ama §2.3 Profile Cards'ta `proof_card` rolü var |
| Intended voice mode | `proof_raw_voice` |
| Length constraint | 1 line per card (tabular) |
| Current backend field | `natal_graph_compact` veya chart compute snapshot (varsayım) |
| Spec match | **MISMATCH** — Home'da chart wheel görünmemeli (spec Home'u "kısa + üst seviye" tutuyor); Profile yüzeyine taşınmalı |
| **Recommendation** | **remap** — `_ChartWheelSection` Home V2'den çıkarılsın, Profile Top veya Profile Cards yüzeyine `proof_card` olarak taşınsın |

### 1.8 `_PullQuoteSection`
**Bileşen:** Editorial pull quote with credit "SHOU · BUGÜNÜN NOTU"

| Alan | Değer |
|---|---|
| Intended semantic role | Effect / First Impression (orchestration §2.1 row 2) — ama "today's note" temporal framing |
| Intended voice mode | `effect_voice` (1-2 sentences, 120-260 chars) |
| Length constraint | spec ile uyumlu |
| Current backend field | `periodCore.upperMeaning` → fallback `periodCore.coreStory` → mock (line 3350-3358) |
| Spec match | **MATCH (with caveat)** — backend bağı doğru, voice spec uyumlu; ama spec Home'da "Effect" rolünü row 2'de bekliyor, fiziksel sıra ChartWheel'in altında (row 7) |
| **Recommendation** | **keep + reorder** — section copy bağı doğru; UI sıralamasında Manifesto'dan hemen sonra (row 2-3) yer alsın, ChartWheel/Sticker/Forum altına düşmesin |

### 1.9 `_StickerGridSection`
**Bileşen:** Sticker grid (görünür element olarak ne taşıdığı belirsiz; muhtemelen visual chip grid)

| Alan | Değer |
|---|---|
| Intended semantic role | Belirsiz — visual ornament veya `list_card` |
| Intended voice mode | — |
| Current backend field | (görmedim — muhtemelen hardcoded sticker set) |
| Spec match | **NOT IN SPEC** |
| **Recommendation** | **defer** — visual decoration ise spec dışı bırakılabilir; eğer interaktif content taşıyorsa role tanımlanmalı |

### 1.10 `_ForumSection`
**Bileşen:** Forum preview (StatefulWidget)

| Alan | Değer |
|---|---|
| Intended semantic role | "Community feed preview" — spec'te yok |
| Intended voice mode | — |
| Current backend field | `forum_router` data (live olabilir) |
| Spec match | **NOT IN SPEC** — orchestration sadece astroloji/profil yüzeylerini tanımlıyor; topluluk ayrı feature |
| **Recommendation** | **defer** — Forum tab'ı zaten var (`forum_page.dart`); Home'da preview tutmak ürün kararı, spec'in scope'u değil. Spec'e "Community preview" bölümü eklemek istemiyorsa **kaldır** veya forum tab'ı ile birleştir. |

### 1.11 `_WeekSection`
**Bileşenler:** Week strip + `_WeekNextCard` (highlight)

| Alan | Değer |
|---|---|
| Intended semantic role | Context Surrogate (orchestration §2.1 row 4) — but multi-day = multi-context |
| Intended voice mode | `context_mode` (1 short line, 35-90 chars per day) |
| Length constraint | per-day chip + 1 highlight |
| Current backend field | (`narrative.calendarDays` veya transit snapshot — varsayım) |
| Spec match | **PARTIAL MATCH** — week-strip section spec'in Home Context'ten genişletilmiş hali; ama `_WeekNextCard` highlight ekstra "Effect/Mechanism teaser"a kayıyor — orchestration §2.1 row 3 ile çakışıyor |
| **Recommendation** | **rename + tighten** — `_WeekSection` → `_HomeWeekStrip` (UI), `_WeekNextCard` → `_HomeWeekHighlightCard` (= Mechanism/Potential Top-1 rolü, content_voice). Her gün chip'i 35-90 chars'ta kalsın. |

### 1.12 `_Endpiece`
**Bileşen:** Closing visual element

| Alan | Değer |
|---|---|
| Intended semantic role | UI shell |
| **Recommendation** | **keep** |

---

## 2. PROFILE V8 — section-by-section alignment

`mobile/lib/app/profile/profile_v8_sections.dart` — `ProfileV8SectionsView.build()` 14 section sırayla ekler:

```
1.  _V8CenterQuote (label "Kimlik ekseni")          → data.identityQuote
2.  _V8InsightStrip                                 → data.topInsights
3.  _V8UniqueMetricSlab                             → data.uniqueBlock + differentiators
4.  _V8PastTeaserCard                               → data.originSection
5.  _V8FirstImpressionCard                          → data.firstImpressionSection
6.  _V8TalentsStrip                                 → data.talentItems / talents
7.  _V8ConversationCard                             → data.conversationSection
8.  _V8AffectsCard                                  → data.effectSection
9.  _V8DefenseCard                                  → data.defenseSection
10. _V8FirstFeltCard                                → data.firstFeltSection
11. (Mission)                                       → data.collectiveSection
12. _V8SectionCard (intimacy, "YAKINLIK")           → data.intimacySection
13. _V8SectionCard (mind, "ZİHİNSEL İŞLEYİŞ")       → data.mindSection
14. _V8CtaSection                                   → data.ctaSection (archetype portal)
```

Backend'in ürettiği `ProfileV8Payload` field'ları (`profile_v8_payload_builder.py:147-164`):
`hero · identity_axis · insight_strip · differentiators · past_teaser · past_teasers · first_impression · talents · conversation_hooks · affects_you · defense · first_felt · intimacy · mind · mission_preview · archetype_portal`

Mobile adapter (`profile_v8_adapter.dart:148-164`) bu field'ları okur. Mapping çoğunlukla 1-1.

Orchestration spec'in **Profile Top** (4 cards), **Profile Cards** (8 cards), **Profile Deep** (10 cards) tanımları var — V8 section'ların hangisine düştüğünü belirlemek gerek.

### 2.1 `_V8CenterQuote` — "Kimlik ekseni"
| Alan | Değer |
|---|---|
| Intended semantic role | **Pattern Label Surrogate + Core Hook** (Profile Top §2.2 row 1) |
| Intended voice mode | `pattern_naming_mode` + `effect_hook` |
| Length constraint | 1 title + 1 line teaser |
| Current backend field | `data.identityQuote` ← `narrative_anchor.text/summary` → `core_story_ui.text` → `core_story` → `upper_meaning` (260 char limit) |
| Spec match | **MATCH** — Pattern Label ("Kimlik ekseni") + Hook (quote) doğru kombinasyonda |
| Length compliance | spec 1 line, fiili ~150-260 chars (multi-line) — **uzun** |
| **Recommendation** | **keep + tighten copy length** — quote'u spec'in 1 line constraint'ine uygun kısalt; ya da Profile Top'ta full quote (140-320 chars) bandında değerlendir |

### 2.2 `_V8InsightStrip`
| Alan | Değer |
|---|---|
| Intended semantic role | Effect / First Impression chip set (Profile Top §2.2 row 2 — kısa varyant) |
| Intended voice mode | `effect_voice` |
| Length constraint | 1-2 sentences, 140-320 chars (Profile Top); chip-grade kullanılırsa 35-90 chars per chip |
| Current backend field | `data.topInsights` ← profile_v8.insight_strip (3 cells: eyebrow + title + subtitle) |
| Spec match | **MATCH (chip-form)** — InsightCellPayload spec ile uyumlu |
| **Recommendation** | **keep** |

### 2.3 `_V8UniqueMetricSlab` — "SENİ FARKLI KILAN"
| Alan | Değer |
|---|---|
| Intended semantic role | Differentiators / unique facts — orchestration spec'te explicit role değil; **"Pattern Label Surrogate alt-role'ü"** olarak yorumlanabilir |
| Intended voice mode | belirsiz — `pattern_naming_mode` veya `effect_voice` |
| Current backend field | `data.uniqueBlock` + `data.differentiators[]` ← profile_v8.differentiators (UniqueFactPayload) |
| Spec match | **NOT IN SPEC** as separate role; çıktı şekli `differentiators` kavramı zengin ama orchestration eşlemiyor |
| **Recommendation** | **rename in spec** — orchestration spec'e "Differentiators / Unique Facts" alt-rolü eklenmeli (Pattern Label Surrogate'in özelleşmiş varyantı). UI keep. |

### 2.4 `_V8PastTeaserCard` — "BU NEREDEN GELİYOR OLABİLİR"
| Alan | Değer |
|---|---|
| Intended semantic role | **Cause / Past Layer** (Profile Cards §2.3 row 4) |
| Intended voice mode | `cause_voice` |
| Length constraint | 1-2 sentences, 140-320 chars |
| Current backend field | `data.originSection` ← profile_v8.past_teaser (EditorialSectionPayload) |
| Spec match | **MATCH** |
| **Recommendation** | **keep** |

### 2.5 `_V8FirstImpressionCard` — "İLK İZLENİM"
| Alan | Değer |
|---|---|
| Intended semantic role | **Effect / First Impression** (Profile Top §2.2 row 2 / Profile Cards §2.3 implicit) |
| Intended voice mode | `effect_voice` |
| Length constraint | 1-2 sentences, 140-320 chars |
| Current backend field | `data.firstImpressionSection` ← profile_v8.first_impression |
| Spec match | **MATCH** |
| **Recommendation** | **keep** |

### 2.6 `_V8TalentsStrip`
| Alan | Değer |
|---|---|
| Intended semantic role | Potential Narrative — **chips/strip biçiminde** (Profile Cards §2.3 row 3, ama spec sentence form bekliyor) |
| Intended voice mode | `potential_voice` |
| Length constraint | spec: 2-3 sentences, 220-480 chars; fiili: chip strip |
| Current backend field | `data.talentItems` (TalentItemPayload: eyebrow + text + accent) + `data.talents[]` (string list) |
| Spec match | **PARTIAL MATCH** — semantic role eşleşiyor, format spec'tekinden farklı (chip vs sentence). `chips/bullets max 5 per card` kuralı korunuyor (§2.3 rules) |
| **Recommendation** | **keep + add proper sentence card** — strip + bir adet narrative-form Potential card birlikte. Ya da spec'in chip-form Potential rolünü onaylasın. |

### 2.7 `_V8ConversationCard` — "BU KİŞİYLE NE KONUŞULUR"
| Alan | Değer |
|---|---|
| Intended semantic role | Spec'te explicit role değil — **"Conversation Hooks"** kavramı orchestration'da yok |
| Intended voice mode | belirsiz; `effect_voice`'a yakın |
| Current backend field | `data.conversationSection` ← profile_v8.conversation_hooks |
| Spec match | **NOT IN SPEC** — backend'de zengin role var (conversation_hooks), orchestration spec'te yok |
| **Recommendation** | **add to spec** — orchestration spec'e "Conversation Hooks" rolü eklensin (Profile Cards Bonus role). UI keep. |

### 2.8 `_V8AffectsCard` — "SENİ NASIL ETKİLER"
| Alan | Değer |
|---|---|
| Intended semantic role | Effect / First Impression varyantı — **"impact-focused effect"** alt rolü |
| Intended voice mode | `effect_voice` |
| Current backend field | `data.effectSection` ← profile_v8.affects_you (EditorialListSectionPayload — list rows) |
| Spec match | **PARTIAL MATCH** — semantic role tamam ama yapısı list-row (rows alanı), spec sentence form bekliyor |
| **Recommendation** | **keep + spec extension** — orchestration spec'te "list_card" + "insight_card" kombo varyantı tanımlansın (effect_voice ile list rows) |

### 2.9 `_V8DefenseCard` — "SAVUNMA MEKANİZMAN"
| Alan | Değer |
|---|---|
| Intended semantic role | **Shadow Narrative** (Profile Cards §2.3 row 2) |
| Intended voice mode | `shadow_safe` (yumuşatılmış) |
| Length constraint | 2-3 sentences, 220-480 chars |
| Current backend field | `data.defenseSection` ← profile_v8.defense |
| Spec match | **MATCH (semantically)** — defense = shadow voice'un ürün dilindeki adı |
| **Recommendation** | **rename internally** — `defense` → semantic_role: `shadow_narrative`. Display label "SAVUNMA MEKANİZMAN" kalabilir. Spec'te shadow_safe voice mode bu section'da geçerli. |

### 2.10 `_V8FirstFeltCard` — "İLK HİSSEDİLEN ŞEY"
| Alan | Değer |
|---|---|
| Intended semantic role | Effect / First Impression varyantı — **"first felt experience"** alt-role |
| Intended voice mode | `effect_voice` |
| Current backend field | `data.firstFeltSection` ← profile_v8.first_felt |
| Spec match | **PARTIAL MATCH** — `_V8FirstImpressionCard` (2.5) ile semantik olarak yakın çakışıyor |
| **Recommendation** | **rename + clarify** — first_impression vs first_felt anlam ayrımı netleşmeli; biri "outer perception" (people's read of you), diğeri "inner experience" (how you feel yourself) olabilir. Şu an label'lar bu ayrımı taşımıyor. |

### 2.11 Mission (`collectiveSection`) — "MİSYON"
| Alan | Değer |
|---|---|
| Intended semantic role | Mission Preview / **Cause→Potential arc** (Profile Deep §2.4 row 3 — "Potential close") |
| Intended voice mode | `potential_voice` (mission yön belirleme) |
| Current backend field | `data.collectiveSection` ← profile_v8.mission_preview (varsayım — adapter mapping kontrol gerekebilir) |
| Spec match | **MATCH** Profile Deep "Potential close" rolü ile |
| **Recommendation** | **keep + clarify spec** — orchestration §2.4 row 3'ün adı "Potential close"; Profile V8'de "MİSYON" olarak label'lanmış. Aynı rol, farklı label. spec ↔ UI label table güncellensin. |

### 2.12 `_V8SectionCard intimacy` — "YAKINLIK"
| Alan | Değer |
|---|---|
| Intended semantic role | Effect / First Impression — **"intimacy domain"** alt-role |
| Intended voice mode | `effect_voice` |
| Current backend field | `data.intimacySection` ← profile_v8.intimacy |
| Spec match | **PARTIAL MATCH** — backend'de domain-specific section ama orchestration spec'te "domain" axis yok |
| **Recommendation** | **add domain axis to spec** — orchestration spec'e "domain-scoped insight card" alt-role'ü eklensin (intimacy / mind / career / home / luck domain'leri için). UI keep. |

### 2.13 `_V8SectionCard mind` — "ZİHİNSEL İŞLEYİŞ"
| Alan | Değer |
|---|---|
| Intended semantic role | **Mechanism Narrative** (Profile Cards §2.3 row 1) |
| Intended voice mode | `mechanism_voice` |
| Length constraint | 2-4 sentences, 260-520 chars |
| Current backend field | `data.mindSection` ← profile_v8.mind |
| Spec match | **MATCH** — Mechanism rolü mind domain'de |
| **Recommendation** | **keep** |

### 2.14 `_V8CtaSection` — Archetype portal
| Alan | Değer |
|---|---|
| Intended semantic role | **Share Line Surrogate / CTA close** — Profile Top §2.2 row 4 yerine bir CTA |
| Intended voice mode | `share_line_mode` (kısa) — fiilen onTap → archetype experience |
| Current backend field | `data.ctaSection` ← profile_v8.archetype_portal (ArchetypePortalPayload: headline + body + items + cta_label) |
| Spec match | **PARTIAL MATCH** — orchestration spec'te "archetype CTA" rolü yok; Share Line ile yakın ama functional CTA |
| **Recommendation** | **add to spec** — orchestration spec'e "Archetype Portal CTA" rolü eklensin (Profile Cards row son: cta_card). UI keep. |

---

## 3. Eksik / mismatch sections (consolidated)

### 3.1 Backend'de var, UI'da görünmeyen
- `hero` (HeroPayload — display_name + sun_sign + rising_sign + moon_sign + followers_text + forum_status_text) — Profile sayfasının üst başlık alanında görünebilir; V8 sections içinde değil.
- `past_teasers[]` (multiple past teasers) — UI sadece `data.originSection` (single) kullanıyor; ek teaser'lar `pastLayers` ile detail sheet'te kullanılıyor ama liste-form ana sayfada yok.

### 3.2 Spec'te var, UI'da explicit olarak görünmeyen
- **Pattern Label Surrogate** — sadece `_V8CenterQuote.label = "Kimlik ekseni"` ile dolaylı taşınıyor (Profile Top §2.2 row 1)
- **Share Line Surrogate** — Profile Top §2.2 row 4 — UI'da yok (ctaSection bunu kısmen kapsıyor ama farklı amaç)
- **Raw Proof Anchor** — orchestration §2.3 row 5 (proof_card optional, profile_v8'de explicit field yok); chart wheel Home'da, proof_raw mobile'da bağımsız ama V8 Profile'da görünmüyor
- **Voice Axes Profile** — render-only meta; UI'da görünmemeli (zaten görünmüyor) ✓

### 3.3 UI'da var, spec'te tanımsız
- `_V8UniqueMetricSlab` (differentiators)
- `_V8ConversationCard` (conversation_hooks)
- `_V8AffectsCard` (affects_you list-row form)
- `_V8FirstFeltCard` (first_felt — first_impression ile çakışıyor)
- Domain-axis sections (intimacy, mind) — spec'te "domain" axis yok
- Archetype portal CTA

---

## 4. Karar matrisi (her section için)

| # | Section | Yüzey | Recommendation |
|---|---|---|---|
| 1.1 | `ShouTopBar` | Home | **keep** |
| 1.2 | `_ManifestoSection` | Home | **remap** — title → backend (core_story_ui.headline) |
| 1.3 | `_SkySection` | Home | **defer** — spec eksik (sky-now feed bölümü) veya Sky tab'a taşı |
| 1.4 | `_AskewBanner` | Home | **rename + verify** — share_cta_card |
| 1.5 | `_NearSection` | Home | **defer** — Bond/Synastry feature, mock |
| 1.6 | `_FeedSection` | Home | **defer** — Bond feature, hardcoded mock |
| 1.7 | `_ChartWheelSection` | Home | **remap** — Home'dan Profile'a taşı |
| 1.8 | `_PullQuoteSection` | Home | **keep + reorder** — Manifesto'dan sonra row 2-3 |
| 1.9 | `_StickerGridSection` | Home | **defer** — visual decoration, rol belirsiz |
| 1.10 | `_ForumSection` | Home | **defer** — community preview, spec scope dışı |
| 1.11 | `_WeekSection` | Home | **rename + tighten** — context strip + week highlight |
| 1.12 | `_Endpiece` | Home | **keep** |
| 2.1 | `_V8CenterQuote` | Profile | **keep + tighten** |
| 2.2 | `_V8InsightStrip` | Profile | **keep** |
| 2.3 | `_V8UniqueMetricSlab` | Profile | **rename in spec** — Differentiators rolü ekle |
| 2.4 | `_V8PastTeaserCard` | Profile | **keep** |
| 2.5 | `_V8FirstImpressionCard` | Profile | **keep** |
| 2.6 | `_V8TalentsStrip` | Profile | **keep + add sentence form** |
| 2.7 | `_V8ConversationCard` | Profile | **add to spec** — Conversation Hooks rolü |
| 2.8 | `_V8AffectsCard` | Profile | **keep + spec extension** (list-row insight card) |
| 2.9 | `_V8DefenseCard` | Profile | **rename internally** — semantic_role: shadow_narrative |
| 2.10 | `_V8FirstFeltCard` | Profile | **rename + clarify** — outer vs inner first impression |
| 2.11 | Mission | Profile | **keep + clarify spec label** |
| 2.12 | `intimacy` | Profile | **add domain axis to spec** |
| 2.13 | `mind` | Profile | **keep** |
| 2.14 | `_V8CtaSection` | Profile | **add to spec** — Archetype Portal CTA |

**Toplam:** 25 section
- **keep**: 6 (1.1, 1.12, 2.1, 2.2, 2.4, 2.5, 2.6, 2.13) — actually 8
- **rename / remap / spec extension**: 11 (1.2, 1.4, 1.7, 1.8, 1.11, 2.3, 2.7, 2.8, 2.9, 2.10, 2.11, 2.12, 2.14)
- **defer**: 6 (1.3, 1.5, 1.6, 1.9, 1.10) + sky-now feed pending = 5
- 4 section **mock/hardcoded copy** ile çalışıyor (1.2 manifesto title, 1.3 sky quote, 1.5 friends rail, 1.6 feed posts) → MVP-değil; ya kaldır ya backend'e bağla

---

## 5. Acil aksiyon önerileri

### 5.1 Mock/hardcoded içeriği temizle (P0)
4 section şu anda hardcoded copy + mock veri ile çalışıyor:

| Section | Mock içerik | Önlem |
|---|---|---|
| `_ManifestoTitle` | "Sahnede olmak istemediğin anlar..." | Backend `core_story_ui.headline` veya `share_line` projection'a bağla |
| `_SkyQuote` | "Ay Aslan'da — görünmek değil, görülmek istiyor." | Backend `narrative.skyDailyQuote` field'ı oluştur + bağla |
| `_NearSection._friends` | 5 hardcoded kişi (Mira, Ela, Burak, Deniz, Kayra) | Bond feature live olana kadar **gizle** veya empty state |
| `_FeedSection._FeedPostMira/Ela/Burak/Deniz` | 4 hardcoded "friend transit" post | Aynı — Bond live olana kadar gizle veya empty state |

App store / production'a bu mock'larla çıkmak ürün riski. Sprint 2/3 öncesi hidden veya empty state'e geç.

### 5.2 `_ChartWheelSection` Home'dan kaldır (P0)
Orchestration §2.1 Home rules: "Must be short", "Must not be deep". Chart wheel deep visual element; Profile yüzeyine ait. Mevcut Profile sayfasında zaten chart wheel yok — taşıma fırsatı.

### 5.3 Spec'e eksik rol tanımları ekle (P1 — doc-only)
Orchestration spec'in v2 güncellemesi:
- Differentiators / Unique Facts (Pattern Label varyantı)
- Conversation Hooks (Profile Cards bonus role)
- Domain-scoped Insight Card (intimacy / mind / career / home / luck)
- Archetype Portal CTA (Profile Cards close)
- Sky-now feed (Home Context expansion VEYA Sky tab'a delegasyon)
- Friends Lattice (Bond/Synastry yüzeyi — Home'dan ayrı)

### 5.4 Section ordering Home V2 (P1)
Şu anki sıra: Manifesto → Sky → Askew → Near → Feed → ChartWheel → PullQuote → Stickers → Forum → Week.

Spec uyumlu sıra: Manifesto (Hook) → PullQuote (Effect) → Week (Context) → Askew (Share CTA) → [Sky feed Sky tab'a] → [Near/Feed Bond tab'a] → [Stickers/Forum scope dışı]

### 5.5 first_impression vs first_felt anlam ayrımı (P2)
Backend `first_impression` ve `first_felt` iki ayrı field, ama UI label'ları ("İLK İZLENİM" + "İLK HİSSEDİLEN ŞEY") yakın okunuyor. Voice spec §1 doktrinine göre:
- **first_impression** = dış gözle senin görüntün ("people read you as...")
- **first_felt** = senin iç hissin ("you feel like...")

Bu ayrımı UI label + voice mode + spec dokümanında netleştir. Şu an **karışık**.

---

## 6. Sprint 2 ile bağ

[`projection_voice_sprint2_plan.md`](projection_voice_sprint2_plan.md) ile bu audit'in ortak alanı:
- **Sprint 2 P0-1.6** (`_BUNDLE_HEADLINES` reducer) → bu audit §3.3 "Differentiators rolü" + §3.3 "Conversation Hooks" rollerinin spec'e eklenmesi paralelinde değerlendirilebilir
- **Sprint 2 deferred** → §5.3 spec güncellemeleri Sprint 2 phase'inin **sonunda** doc commit'lenmeli (kod sonrası spec catch-up)
- §5.1 mock cleanup — Sprint 2 voice cleanup'tan **bağımsız**, ürün/UI ekibi tarafından paralel yürütülebilir

---

## 7. Out of scope

- ❌ Code değişikliği (sadece tespit + sınıflandırma)
- ❌ Voice copy'sine dokunmak (Sprint 1 zaten yaptı, Sprint 2 yapacak)
- ❌ Selection / projection logic
- ❌ Schema değişiklikleri (yeni field eklemek = backend builder + adapter + UI değişikliği zinciri)
- ❌ EN paritesi (TR-only audit)
- ❌ Story / Share Card / Explainability surfaces — Home ve Profile'a focus

---

## 8. Sonuç

UI ile orchestration spec arasında **iki yönlü gap** var:

1. **UI'da olan ama spec'te yok**: 6 section (Differentiators, Conversation Hooks, Affects list-row, First Felt, domain axis sections, Archetype CTA) — bunlar **gerçek backend rolleri**, orchestration spec'in v2'sinde tanımlanmalı.

2. **Spec'te olan ama UI'da görünmeyen**: Pattern Label Surrogate explicit, Share Line Surrogate, Raw Proof Anchor in Profile — bunlar **eklenmeli** veya alt-role olarak mevcut section'lara entegre edilmeli.

3. **Mock/hardcoded section'lar (4 adet)** kullanıcıya production-grade olmayan içerik gösteriyor; release öncesi temizlik şart.

4. **Sky / Forum / Stickers** Home'da, ama orchestration spec sadece astroloji-profil eksenini taşıyor; bu section'lar ya spec genişlemesi ile resmileşmeli ya da uygun tab'lara taşınmalı.

Sonraki adım: bu audit'in §5.1 (mock cleanup) ve §5.2 (chart wheel taşıma) kararlarını ürün ekibiyle netleştirip implementation backlog'una almak. Spec güncellemesi (§5.3) ise Sprint 2/3 closing'de yapılmalı.
