# S2 Commit 2 — Mobile Scope Document

**Hedef:** Backend'den gelen `proof_raw` field'ını mobile payload zincirinde doğrulayıp, profile detail flow'da paragraph altına `ProfileProofChip` olarak render etmek.

**Checkpoint referans:** main tip `667724f` (voice spec v2.1 + proof_raw backend)
**Çalışma ortamı:** Bu iş **ayrı worktree**'de yapılır — `claude/proof-raw-mobile`, main'den açılır.

---

## 1. Veri Zinciri — Şu An Main'de Proof_raw Nereye Kadar Geliyor

Backend `667724f` commit'iyle şu field ekleyen pipeline:

```
supporting_threads_builder.build_supporting_threads()
  → thread item: {id, title, one_liner, paragraph, body, detail_blocks,
                  micro, chips, proof_raw, section_id, evidence}
```

Bu thread list **API endpoint'i** [natal_interpretation.py:2055](backend/app/api/routes/natal_interpretation.py) üzerinden payload'a çıkıyor.

### Mobile'da şu an zinciri takip

| Adım | Dosya / fonksiyon | Şu an proof_raw? |
|---|---|---|
| **Fetch** | `profile_repository.dart` → API client, payload `Map<String, dynamic>` | ✅ Transparent (raw map) |
| **Normalize** | [profile_v8_adapter.dart:1679](mobile/lib/app/profile/profile_v8_adapter.dart) `_normalizeThread()` | ❌ **Filtered out** — sadece id/title/subtitle/body/chips/detail_blocks alıyor |
| **Pick + Make** | `_pickThread()` + `_makeSection()` (conversationSection, effectSection, originSection, vs.) | ❌ Thread'den section'a mapping proof_raw'ı taşımıyor |
| **Section class** | [profile_v8_adapter.dart:84](mobile/lib/app/profile/profile_v8_adapter.dart) `ProfileV8TextSection` | ❌ Sadece eyebrow/headline/body/bullets/chips/callout/footer/cta/growth field'ları |
| **Playback map** | [profile_detail_flow_page.dart:1514](mobile/lib/app/tabs/profile_detail_flow_page.dart) `_ProfileDetailPlaybackPageData` | ❌ Body'ye mapping var, proof_raw yok |
| **Render** | [profile_detail_flow_page.dart:3161](mobile/lib/app/tabs/profile_detail_flow_page.dart) `_DetailTextSection` | ❌ Chips render ediyor (3233-3240), proof_raw widget yok |

**Özet:** proof_raw backend'den çıkıyor ama `_normalizeThread` tarafından **ilk adımda filtreleniyor.** Zincirin geri kalanı onu hiç görmüyor.

---

## 2. Boşluklar — Hangi Dosyalar Dokunulmalı

Sıralı değişim listesi (her adım öncekine bağlı):

| # | Dosya | Değişim | LoC tahmin |
|---|---|---|---|
| 1 | `profile_v8_adapter.dart:1679` `_normalizeThread()` | Return map'e `'proof_raw': safeText(raw['proof_raw']) ?? ''` eklensin | +1 |
| 2 | `profile_v8_adapter.dart:84` `ProfileV8TextSection` class | Opsiyonel `final String proofRaw` field'ı eklensin (default `''`) | +3 |
| 3 | `profile_v8_adapter.dart` `_makeSection()` helper | Opsiyonel `proofRawCandidates: <dynamic>[thread?['proof_raw']]` param'ı eklensin → ilk non-empty seçsin | +8 |
| 4 | `profile_v8_adapter.dart:415+` section builder'lar (uniqueBlock, originSection, conversationSection, vb.) | İlgili olanlara `proofRawCandidates: [...]` param geçilsin — **sadece 3 core thread (identity / relationships / career) map'lenenler** | +3×5 |
| 5 | `profile_detail_flow_page.dart:1514` `_ProfileDetailPlaybackPageData` | `proofRaw` field ekle | +3 |
| 6 | Page data mapping (v8_adapter → playback data) | TextSection.proofRaw → PageData.proofRaw passthrough | +2 |
| 7 | `profile_detail_flow_page.dart:3161` `_DetailTextSection.build()` | bodyBlocks sonrası, chips'ten **önce** `ProfileProofChip` render | +3 |
| 8 | **Widget dosyası** — `mobile/lib/app/profile/proof_chip.dart` | S1'de admiring-archimedes worktree'sinde yazılan dosya — **kopyalanacak** (birebir) | +70 (new) |
| 9 | **Widget test** — `mobile/test/profile_proof_chip_test.dart` | S1'de yazılan 12 test — **kopyalanacak** | +203 (new) |
| 10 | Integration test (yeni) | `_normalizeThread` + `ProfileV8TextSection` proof_raw passthrough + `_DetailTextSection` render site widget test | +100 |

**Yaklaşık toplam:** 1 dosya new (proof_chip), 1 dosya new test, ~30 satır değişim 3 mevcut dosyada.

---

## 3. Render Site Kararı — Nereye Oturur

Mevcut `_DetailTextSection.build()` sırası ([profile_detail_flow_page.dart:3180-3240](mobile/lib/app/tabs/profile_detail_flow_page.dart)):

```
1. eyebrow      ← MONO, UPPERCASE etiket
2. title        ← Büyük başlık
3. intro        ← (opsiyonel)
4. highlightLines ← JoviaSentenceBubbleStack (opsiyonel)
5. bodyBlocks   ← Ana paragraph(lar)
6. chips        ← Wrap ile rozetler
```

Proof_raw için 3 olası konum:

| Konum | Artı | Eksi |
|---|---|---|
| **A.** bodyBlocks sonrası, chips öncesi | Paragraf ile doğal bağ — voice spec §13.4 "sessiz imza paragraph altı" | Chips hemen altında → yoğun gibi görünebilir |
| B. bodyBlocks öncesi (intro altı) | Üstte kanıt → okumaya başlamadan güven | "Sessiz" değil, güçlü → imza değil etiket |
| C. En sonda (chips'ten sonra) | En az dikkat çeker | "Mühür" hissi kaybolur, notasyon gibi kalır |

**Karar: A.** Voice spec §13.4'te yazılı — "paragraf altında sessiz imza". Chips görsel ritim olarak zaten sonra; proof_raw tek satır olduğu için araya girdiğinde kesintisiz bir iniş sağlar: **paragraph → proof_raw (imza) → chips (rozet grubu)**.

### Pozisyon detayı (A için)

```dart
// mevcut bodyBlocks for-loop sonu
if (page.bodyBlocks.isNotEmpty) { ... }

// YENİ — bodyBlocks ile chips arası
ProfileProofChip(proofRaw: page.proofRaw),

// mevcut chips wrap
if (page.chips.isNotEmpty) { ... }
```

ProfileProofChip'in kendi `topSpacing: 14` default'u paragraph'tan nefesini ayarlıyor. Chips zaten altında `SizedBox(height: 16)` ile ayrılıyor, ritim korunur.

---

## 4. Chips × Proof_raw — Görsel Hiyerarşi

Bilgi tekrarı **bilinçli** (A/B ölçüm kararı, önceki onay). Ama görsel hiyerarşide iki katman farklı ağırlıkta durmalı:

| Katman | Görsel karakter | Okuma önceliği |
|---|---|---|
| **bodyBlocks** (paragraph) | 14.3px, bodyReading, rahat satır yüksekliği | Birincil — ana metin |
| **proof_raw** (ProfileProofChip) | 11px, alpha 0.60, sol lime border, tek satır | **Dip not** — okunur ama dikkat çekmez |
| **chips** (Wrap rozetler) | 13-14px, rozet bg + border, çoklu parça | İkincil — göz gezerken tarama |

**Çakışma yönetimi:**
- Aynı bilgi iki format → `"Satürn 3. evde"` (chip) ve `"Satürn · 3. ev · Oğlak"` (proof). Üçüncü parça (`Oğlak`) chip set'inde ayrı olarak mevcut.
- Riskli durum: her iki katman da **güçlü görsel** olursa okuyucu "bu niye iki kez?" der.
- Çözüm: proof_raw'ın **bastırılmış** olması (%60 alpha, 11px, border'sız metin) chips'in altında sessiz kalır. Chips daha belirgin, proof_raw "dipnot".

**Ölçüm hipotezi:** Kullanıcı önce chips'i tarar, sonra paragraph'a iner, **en altta proof_raw'ı görür ve "aaa bu yüzden" der.** "Aa bu bana özel" hissi için bu sıra önemli.

Eğer ölçüm tersini gösterirse (kullanıcı chips'i ignore ediyor, proof_raw'u çok seviyor), sonraki iterasyon kararı: chips'i secondary yapmak veya kaldırmak.

---

## 5. Minimum Commit Sırası (Yeni Worktree'de)

**Commit 2a — Adapter + model passthrough**
- `_normalizeThread` + `ProfileV8TextSection` + `_makeSection` + ilgili section builder'lar
- Unit test: normalizeThread proof_raw passthrough + TextSection model round-trip
- Zero UI impact

**Commit 2b — Playback data + widget**
- `_ProfileDetailPlaybackPageData.proofRaw`
- Mapping site TextSection → PageData
- `proof_chip.dart` + widget test dosyaları kopyalansın (birebir, S1'den)
- `_DetailTextSection.build` → bodyBlocks sonrası ProfileProofChip render

**Commit 2c — Integration test**
- End-to-end: synthetic payload → adapter → page data → widget render
- Locale guard + empty fallback + accessibility invariant

Her commit kendi başına yeşil. Rollback granüler.

---

## 6. Risk Matrisi

| Risk | Olasılık | Etki | Azaltma |
|---|---|---|---|
| `_normalizeThread` field eklemesi başka consumer'ı kırar | Düşük | Düşük | Additive — default `''`, consumer null-check yapıyor zaten |
| `ProfileV8TextSection` constructor parametre breaking | Orta | Orta | Opsiyonel param (`proofRaw = ''`) — breaking olmaz |
| `_DetailTextSection` render'da görsel overflow | Düşük | Düşük | Widget zaten maxLines 1 + ellipsis; `if (proofRaw.isNotEmpty)` guard |
| Locale guard bazı profile'da yanlış tetiklenir | Düşük | Düşük | Widget test EN / TR / unsupported locale matrisi |
| Chips + proof_raw birlikte aşırı görsel yük | Orta | Düşük (UI review ile ölçülür) | Kasıtlı A/B — screenshot review + kullanıcı geri bildirimi |
| Faz 2 backend'i proof_raw sadece 3 thread için üretiyor, diğer section'lar boş → ritim kırılır | Orta | Düşük | `proofRaw.isEmpty` → `SizedBox.shrink()` — boş thread hiç render etmez |
| Integration test setup karmaşık (chart pipeline mock) | Orta | Düşük | Synthetic section map ile adapter'ı besle — chart engine bypass |

---

## 7. Doğrulama Check-List (Commit 2'nin sonu)

Aşağıdakilerin hepsi yeşil olursa Commit 2 hazır:

- [ ] `_normalizeThread` proof_raw passthrough — unit test yeşil
- [ ] `ProfileV8TextSection` proof_raw round-trip — unit test yeşil
- [ ] `ProfileProofChip` widget test — 12/12 yeşil (S1'den import)
- [ ] `_DetailTextSection` render site integration test — paragraph + proof_raw + chips doğru sırada
- [ ] Locale TR → render; EN → shrink
- [ ] Empty proof_raw → shrink (chips etkilenmez)
- [ ] flutter analyze → 0 issue
- [ ] Mevcut `profile_archetype_page_test.dart` + diğer widget test suite regression yeşil
- [ ] Manual screenshot — TR locale, sample natal profile, 3 thread → paragraph altında sessiz proof satırı görünür

---

## 8. Ne Yapılmaz (Bu Scope'un Dışı)

- **Chips değişikliği yok** — aynı yerde aynı format. A/B için bilinçli.
- **proof_line (soft cümle) içerik yok** — field payload'da boş, widget render etmez.
- **`direction_learning` thread** — backend'de hâlâ section builder yok; mobile tarafı da map'leyemez.
- **Explainability panel** — zaten kendi proof mimarisini kullanıyor, dokunulmaz.
- **Archetype card** — proof_raw burada **görünmemeli** (voice spec §13.4 matrisi).
- **Share card / Story Studio / Home hero** — proof_raw layer mapping bu yüzeylerde ❌.

---

## 9. Açılış Komutu (Bu Worktree Kapatıldığında)

```bash
cd /Users/sahradenizozdogan/Astrologi-Ai
git worktree add .claude/worktrees/proof-raw-mobile -b claude/proof-raw-mobile main
cd .claude/worktrees/proof-raw-mobile

# S1'deki widget dosyalarını kopyala — birebir
cp ../admiring-archimedes-2bb9a8/mobile/lib/app/profile/proof_chip.dart \
   mobile/lib/app/profile/proof_chip.dart
cp ../admiring-archimedes-2bb9a8/mobile/test/profile_proof_chip_test.dart \
   mobile/test/profile_proof_chip_test.dart

# Scope doc'a göre sırayla: Commit 2a → 2b → 2c
```

Bu doküman yeni worktree'de **implementation guide** olarak kullanılır.
