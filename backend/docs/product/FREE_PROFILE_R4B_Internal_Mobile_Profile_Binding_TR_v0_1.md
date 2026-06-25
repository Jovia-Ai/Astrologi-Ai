# FREE-PROFILE-R4B — Internal Mobile Profile Binding TR v0.1

> Dedicated narrow Free editorial Profile path, default-off. Parses only the
> additive `editorial_profile` payload; never consults legacy cross-source
> fallback; structured non-paged detail; no aura badge, no `_splitBodyIntoSlides`.

## 1. Starting commit

- Branch: `codex/free-profile-r4-narrow-binding`
- Backend R4A commit: `b0d275709e3a31479d38b1185ae42ac684104db4`
- Built on R3D → … → foundation history.

## 2. Files changed

Additive (new):
- `mobile/lib/app/profile/free_editorial_profile_adapter.dart`
- `mobile/lib/app/profile/free_editorial_profile_view.dart`
- `mobile/test/free_editorial_profile_test.dart`
- `backend/docs/product/FREE_PROFILE_R4B_Internal_Mobile_Profile_Binding_TR_v0_1.md`

No existing mobile file modified; `ProfileV8Adapter` fallback behavior untouched;
`app_router.dart`, providers, theme, `main.dart` untouched.

## 3. Feature flag

- `kFreeEditorialProfileEnabled` = `bool.fromEnvironment('FREE_EDITORIAL_PROFILE_ENABLED', defaultValue: false)`.
- Default **off**; the narrow surface is only mounted when enabled (dart-define).
  Backend pairs with env flag `FREE_EDITORIAL_PROFILE_ENABLED` (R4A).

## 4. Adapter (`free_editorial_profile_adapter.dart`)

- Parses ONLY `editorial_profile`; returns `FreeEditorialProfileModel.empty`
  (typed invalid state) on null/malformed input.
- Preserves backend ordinal order; one owner per card; content-block roles kept.
- Never searches `profile_v8`, `sections_v2`, supporting threads or mock cards
  (asserted at source level, comments excluded).
- Never merges chips across cards (each chip keeps its `source`).
- Never synthesizes a title (cards with empty title/primary_key are dropped).
- `cardsForDomain(domain)` returns at most two cards (sign then house), no
  cross-domain reuse, no fallback card.
- `orderedBlocks()` returns recognition→mechanism→tension→capacity, non-empty only.

## 5. Internal narrow surface (`free_editorial_profile_view.dart`)

- Renders the five fixed domains (identity/emotion/mind/relationship/action) in
  order; per domain ≤2 cards; card shows title, summary, exact placement chips,
  and one CTA ("Detayı aç").
- Does NOT show: origin, defense, supporting proof, aura semantic badge,
  `Koruyucu dalga`, aspect labels, dominant-signature chips, Tam Okuma CTA.
- Does NOT route through the legacy poster selection system; self-contained
  Material primitives only.
- Detail page: structured, non-paged; role blocks in order, non-empty only; role
  names hidden; no `_splitBodyIntoSlides`, no `PageView`, no page counters.

## 6. R3D badge classification (recorded)

```
Koruyucu dalga
= mobile-computed aura semantic family label (JoviaAuraSemanticFamily.protective)
= not a placement owner
= not a stale selected-card state
```

In the narrow path it does not render. It is NOT removed from the legacy path in
this scope.

## 7. Ownership invariant counts (mobile)

For both fixtures, in the parsed model: title mismatch 0 · chip mismatch 0 (all
chip `source == primaryKey`) · cross-card merge 0 · fallback 0 · duplicate surface
0 · aura/aspect/dominant leakage 0. Every card `ownershipStatus == "aligned"`.

## 8. Tests & results

`flutter test test/free_editorial_profile_test.dart` → **All tests passed (13)**:
mobile L1–L10 (order, no legacy fallback, chip ownership, max-two-per-domain,
missing-house omission, no aura badge, no `_splitBodyIntoSlides`, block order,
invalid→empty, default-off) plus three widget tests (domain render + max two +
no Koruyucu dalga; empty state; detail block order with no page counter).

`flutter analyze` on all three changed Dart files → **No issues found!**

## 9. Fixture matrices (parsed model)

- Fixture A: 10 cards, order preserved, domains
  identity·identity / emotion·emotion / mind·mind / relationship·relationship /
  action·action; chips bound to own key.
- Fixture B: action domain shows only `mars_virgo`; `mars_house_9` recorded in
  `missingKeys` (`ASSET_NOT_FOUND`), not substituted.

## 10. Visual captures — DEFERRED_REQUIRES_FULL_APP_RUNTIME

Screenshots require the full app (Supabase auth + live backend + chart facts) on
an emulator, which is not driven in this scope. Each required capture is specified
for manual validation:

| # | route | flag state | fixture | expected | acceptance | filename |
|---|---|---|---|---|---|---|
| 1 | narrow Profile overview | FREE_EDITORIAL_PROFILE_ENABLED=true | A | 5 domain sections, ≤2 cards each | no unrelated chips, no repeated owner across domains | r4b_A_overview.png |
| 2 | identity domain | on | A | Güneş Aslan + Güneş 4. Ev | chips Güneş/Aslan, Güneş/4. Ev | r4b_A_identity.png |
| 3 | emotion domain | on | A | Ay İkizler (+ Ay 1. Ev) | no Koruyucu dalga badge | r4b_A_emotion.png |
| 4 | mind domain | on | A | Merkür Başak + Merkür 5. Ev | no Venüs/Yükselen chips | r4b_A_mind.png |
| 5 | relationship domain | on | A | Venüs Başak + Venüs 5. Ev | single_card, CTA present | r4b_A_relationship.png |
| 6 | action domain | on | A | Mars Yay + Mars 7. Ev | chips bound to mars keys | r4b_A_action.png |
| 7 | sign detail | on | A | sun_leo blocks in order | recognition→mechanism→tension, no page counter | r4b_A_sign_detail.png |
| 8 | house detail | on | A | sun_house_4 incl. capacity | 4 blocks, no `01/02` cover | r4b_A_house_detail.png |
| 9 | action domain (missing) | on | B | only Mars Başak | no mars_house_9 card, no substitute | r4b_B_action_missing.png |

Visual acceptance to verify manually: no unrelated chips; no repeated owner across
domains; no `Koruyucu dalga`; no empty `01/02` cover; no overloaded `02/02`; no
carousel/scroll ambiguity; consistent spacing/typography; no legacy poster blocks.

## 11. Known remaining design debt

- Final multi-slide visual system is R5 (current detail is non-paged structured).
- Narrow surface is not yet wired into a route/tab (intentionally; default-off,
  mounted by the host behind the flag) — wiring + emulator capture is the manual
  validation step.
- Aspect/dominant cards and absent houses (`mars_house_9`) remain out of Free V1.

## 12. Exact R5 structured-slide scope

Define the slide contract over the resolved `content_blocks`: one role per slide
(recognition/mechanism/tension/capacity), word-budget per slide, deterministic
order, no per-sentence splitting, no new prose, no SHOU; plus the final visual
polish and the manual emulator capture review.

## 13. Commit & dirty files

Commit: `FREE-PROFILE-R4B: bind narrow editorial profile internally` (hash in final
response). After commit: clean.

## Verdict

`PROCEED_TO_MANUAL_VISUAL_VALIDATION`

(Code, analyzer and tests pass; the 14 emulator screenshots remain deferred and
specified for manual capture. `PROCEED_TO_STRUCTURED_SLIDE_AND_VISUAL_POLISH` must
not be claimed until those manual captures are completed and reviewed.)
