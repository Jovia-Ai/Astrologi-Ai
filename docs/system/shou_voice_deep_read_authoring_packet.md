# SHOU `deep_read` — Authoring Packet (tone_aware §13.2)

> Planning artifact. The committed §13.2 mechanism that turns the
> frozen deep_read design into reviewable, codeable config. No code/
> taxonomy/merge/production change yet. This is the LOCK artifact
> (spec §9.10): after this, §13.2 review → code; no further hand vN.

## 1. Rationale

Three converging blind reads isolated one variable: ARC selection is
sound; the gap was the render's lived-ness + rhythm. The frozen
contract closes it. Product reason: the user must feel both "ben
böyleyim" *and* "ben bunu neden böyle yapıyor olabilirim" *and* "bunun
bana ne kazandırdığı" — without determinism, without invasiveness.

## 2. Frozen contract (the four rules)

1. **one spine per swipe**
2. **thesis once** (signature lands a single time; intermediate slides
   open new faces)
3. **lived-scene** (concrete experience, not abstract category nouns;
   scenes carry recurrence)
4. **rhythm-modulation** (explanatory depth preserved; cadence set by
   each slide's emotional nature — calm/heavy/disciplined/sharp/warm/
   quiet/settling — slide-to-slide and within a paragraph)

## 3. Roles (all reconciled to committed semantic roles)

| slide_role | binds to (committed) | voice_mode | certainty |
|---|---|---|---|
| `current_behavior` / `how_seen` / `what_inside` | Core Hook / Effect / Mechanism | per Rule 4 | high |
| `origin_hint` | **cause_voice** / Cause-Past-Layer (§2 emerging) | softened_interpretive | low_to_medium |
| `shadow` | Shadow Narrative / shadow_safe | shadow_safe | medium |
| `gift` | **potential_voice** / Potential Narrative (§2 confirmed) | grounded_gift | high |
| `integration` | Potential / threshold | threshold_statement | medium_high |

`slide_profile = pattern_to_gift`:
`current_behavior → how_seen → what_inside → origin_hint → shadow →
gift → integration` (5–7 by theme; origin_hint only if §6 eligible).

## 4. origin_hint eligibility (sparse — committed)

12H/hidden · Moon-Saturn · Moon-Pluto · Saturn 1/4/7/10 · Chiron ·
Pluto density · Venus 12 · Saturn 3 · Cancer-Asc+Saturn-1 ·
relationship trust/threshold. Default surface = opt-in expandable
"Nereden geliyor olabilir?" (consent-by-expansion). NOT inline by
default. NOT on neutral/gift-only signatures.

## 5. Good examples (the user's copy — integrated, not re-authored)

**origin_hint — Card A (12H):**
> Bazı şeyleri hemen dışarı açmadan önce içeride güvene kavuşturman
> gerekebilir. Bir düşünceyi, bir sevgiyi ya da bir yön değişimini
> erken gösterirsen başkasının sözüyle bozulacakmış gibi gelir. Bu
> sende zamanla kurulmuş bir korunma biçimi olabilir; içinden geçeni
> hemen anlatmanın anlaşılmadığı dönemler olmuş olabilir. Herkes için
> böyle olmak zorunda değil — ama sende bazı şeyler önce sessiz bir
> alanda güç toplamak ister.

**gift — Card A:**
> Bu yapının hediyesi, görünmeyenden anlam çıkarabilmen. Her deneyimi
> hemen dışarı taşımadığın için bazı şeyleri daha derinden
> işleyebiliyorsun. İçeride uzun süre taşıdığın bir şey, bir gün
> dışarıda başkasının da işine yarayan bir forma kavuşabilir. Sende
> sessizlik boşluk değil — bazen en güçlü hazırlığın orada olur.

**origin_hint — Card B (Cancer Asc + Saturn 1):**
> İnsanlara hemen açılmaman sadece mesafe değil; içinde önce ortamı
> tartan, güvenli mi diye bakan bir taraf var. Bu sende zamanla
> güçlenmiş bir korunma biçimi olabilir — erken dönemde kontrollü
> görünmenin daha güvenli geldiği zamanlar olmuş olabilir. Bu bir
> kusur değil; bir zamanlar işe yaramış bir koruma.

**gift — Card B:**
> Bu temkinli yapı sana bir farkındalık verir: insanları, ortamları
> ve niyetleri hızlı okuyabilirsin. Bu seni sadece hassas değil,
> seçici de yapar. Doğru çalıştığında bu sende güçlü bir iç ölçüye
> dönüşür.

## 6. Bad examples (must fail review)

- "Çocukluğunda ailen sana güvenmedi, o yüzden böylesin." (determinist,
  blame, no opt-out — forbidden origin_hint)
- "Bu seni özel yapar, her şeyi başarırsın." (motivational, forbidden
  gift)
- origin_hint on a neutral/gift signature (eligibility breach)
- origin_hint inline + on every slide (sparsity + consent breach)
- "silik" / faded-lesser words denying a *shade* not a *deficit*

## 7. Worked example — frozen Card A (consolidated, canonical)

`pattern_to_gift`, Jupiter 8th, thesis once, "silik"→"eksiklik değil",
origin_hint as opt-in expandable. Title: `Gücün önce görünmeyende kök
salıyor`.

1. **Çoğu şey önce içeride olur** `[sakin]` — (v4 slide 1, unchanged)
2. **Görünmeyen yer boş değil** `[kontrast]` — (v4 slide 2)
3. **▸ Nereden geliyor olabilir?** `[origin_hint · opt-in]` — §5 Card A
   origin_hint copy
4. **Derinlikte anlam ararsın** `[ağır]` — (v4 slide 3, Jupiter Yay 8)
5. **Dışarıda forma sokarsın** `[disiplinli, kısa]` — (v4 slide 4)
6. **Gölge: tek başına taşımak** `[sessiz]` — (v4 slide 8)
7. **Hediye** `[sıcak, gözleme dayalı]` — §5 Card A gift copy
8. **Asıl imza** `[yatışan — tez tek kez]` — (v4 slide 9)

Parent: > Çoğu şey sende önce içeride başlıyor… Bu **bir eksiklik
değil** — sadece senin büyüme yerin başkalarınınkinden farklı.

deselected_trace + map_trace + deep_evidence: unchanged from v4.

## 8. Affected / QA

- Affected roles: origin_hint, gift, shadow, integration (new
  voice_modes); profiles: pattern_to_gift (proposed).
- Affected families: any deep_read card; origin_hint only the §4 set.
- QA (tone_aware §15 + §13.3 side-by-side): banned-phrase scan;
  origin_hint determinism scan (every passage ≥1 opt-out clause; zero
  event/blame/clinical tokens); gift motivational-drift scan; one-spine
  + thesis-once + rhythm-variation tests; same-family read across
  charts; **feels-seen vs feels-presumed** human check on origin_hint.

## 9. Status — LOCK PASS (blind-confirmed)

Final blind confirmation of §7 consolidated Card A: **PASS**. The
deep_read voice contract (Rules 1–4 + origin_hint + gift +
pattern_to_gift) is **frozen and validated on the canonical worked
example**. Design phase of the voice layer is closed.

**Validated:** the deep_read voice/render contract, on Card A (2007),
via the blind loop (1985 scannable → 2007/1975 deep_read → v1..v4 →
LOCK).

**NOT yet done (honest — does not ship on this PASS):**
- tone_aware §13.2 *human code review* of the new constraint families
  (this packet is the input to that review, not a substitute).
- tone_aware §13.3 *side-by-side multi-chart family read* QA gate
  (only the canonical example is blind-confirmed; Card B consolidated
  + more charts still owed before public rollout).
- The earlier PROPOSED items still pending §13.2: `identity_polarity`
  / `held_plurality` / `pattern_to_gift` profiles; themes.yaml
  "emotional_base" question; "slide_profile must be ARC-owner-driven"
  finding (2007); no-dominant profile (1975).
- The scannable-card surface (original §10.3 path) — separate from
  this deep_read lock.
- **The ARC scorer / A2 merge question is untouched and still
  unauthorized** (Pass-1 closed negative; A2 best candidate; its own
  §10.3 still owed). The voice LOCK does not merge or validate A2.
- Zero code. tone_aware §16 Phase 3 (slides[] contract) is real
  backend/renderer work → CLAUDE.md approval-gated, needs its own
  bounded plan.

Next: §13.2 review + a tightly-scoped Phase-3 plan for ONE pilot card
family (no broad build, no production change until reviewed +
approved).
