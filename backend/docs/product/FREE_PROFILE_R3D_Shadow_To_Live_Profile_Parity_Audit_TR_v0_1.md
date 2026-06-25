# FREE-PROFILE-R3D — Shadow-to-Live Profile Card Parity & Binding Audit TR v0.1

> Forensic, documentation-only. No production source modified, no projection
> attached to public payloads, no binding/slide implementation. Compares the
> ownership-safe R3C shadow cards against the live Profile pipeline's source chain.

## 0. Worktree

- Branch: `codex/free-profile-r3d-parity-audit`
- HEAD: `91be84ee51a384bccf3eb66a7e61e4e1e9cb86f1`
- Path: `/Users/sahradenizozdogan/.codex/worktrees/free-profile-r3d`
- Initial `git status --short`: clean.

## 0.1 Trace method & honest limitation

The **shadow side** is executed (R3C projection). The **live side** is traced
through the actual runtime **source chain** in code (selector → personality_imprint
library → profile_v8 builder → public payload → ProfileV8Adapter → SectionsView →
DetailSheet), as §C mandates ("do not infer ownership only from visible text").
Per-fixture **live body hashes were not captured from a running pipeline** — the
public snapshot suite is red on the base (`10 failed / 74 passed`, pre-existing)
and the mobile app is not executed here. Ownership parity is therefore asserted at
the **source-family / owner** level; rows are marked
`trace_confidence = source_chain_traced_runtime_value_not_captured`.

## A. Measurement guard

| metric | value |
|---|---|
| registry asset-family count | 25 |
| canonical per-key owner count | **9** (priority houses, support houses, V3×4 sign, V4×3 tone) |
| unique source-content hash count | 9 |
| unique projected card (governed key) count | 174 |

Aliases (must not inflate canonical coverage):

| registry asset | canonical owner | rep key | content hash | in visible output |
|---|---|---|---|---|
| `editorial.personality_imprint_library_tr_v1.tr.v1` (_V1) | PRIORITY_HOUSES_V1 | jupiter_house_1 | `f3969289…` | yes (house + aspect cards) |
| `editorial.personality_imprint_library_tr_v2.tr.v1` (_V2) | PRIORITY_HOUSES_V1 | jupiter_house_1 | `f3969289…` | yes (house cards) |

Both aliases collapse to the same canonical owner and hash — they add **zero**
unique canonical coverage.

## B. Fixtures

Fixture A required shadow keys: `sun_house_4, moon_gemini, mercury_virgo,
venus_virgo, mars_sagittarius` → all project (R3C).
Fixture B required shadow keys include `mars_house_9 → ASSET_NOT_FOUND` (no
substitute, no pin). The other 9 project.

## C. Live pipeline source chain (traced)

```
chart facts
  → select_personality_imprint_entries (selector.py: _rerank_candidates, slot/primitive/
      counterweight/combination/family/confidence bonuses, master_selector)  ← CHART-DRIVEN SELECTION
  → build_personality_imprint (entries / extra_entries / bundles / support_entries)
  → profile_v8_payload_builder (pick_*/build_* with fallback=by_domain[<other domain>])
  → public payload
  → ProfileV8Adapter (_dedupeCards / _dedupeByIdentity / chipCandidates / proofRaw / auraEntry)
  → ProfilePage selection
  → ProfileV8SectionsView + ProfileDetailSheet (_splitBodyIntoSlides, per-sentence)
```

The decisive structural fact: **the live pipeline selects, reranks and merges**;
the shadow projection never selects. Live ownership is selection+fallback-driven.

## D. Shadow-to-live parity matrix

Full matrix: `data/FREE_PROFILE_R3D_Shadow_Live_Parity_Matrix_TR_v0_1.json`
(15 shadow rows + 5 live-only cards).

Parity-status counts:

| status | count |
|---|---|
| TEXT_MATCH_OWNER_UNKNOWN (house placements; same family, runtime value not captured) | 5 |
| SHADOW_ASSET_NOT_RENDERED (sign placements — hidden good assets) | 9 |
| MISSING_EDITORIAL_COVERAGE (`mars_house_9`) | 1 |
| LIVE_CARD_HAS_NO_FREE_OWNER (`sun_trine_jupiter` aspect) | 1 |
| BODY_OWNER_MISMATCH (Case 2) | 1 |
| CHIP_OWNER_MISMATCH (Case 3) | 1 |
| DUPLICATE_SURFACE_ASSIGNMENT (Case 4) | 1 |
| STATE_OR_SELECTION_LEAK (Case 5 aura badge) | 1 |

Secondary diagnostics on house placements: `CHIP_OWNER_MISMATCH`,
`STATE_OR_SELECTION_LEAK` (cross-card chips + selection-driven body).

## E. Live-surface scope classification

See `data/...Narrow_Launch_Surface_Decision...json`. Summary: placement/lead/
first_impression/first_felt/intimacy/mind/detail-modal → `KEEP_AFTER_BINDING_REPAIR`;
insight_strip/talents/conversation/effect/defense → `HIDE_FROM_NARROW_FREE`;
narrative_cards/relationship_preview → `PREMIUM_ONLY`; aura badge → `INTERNAL_ONLY`;
supporting_threads → `REMOVE_FALLBACK`.

## F. Observed cases — root cause

**Case 1 — Güneş Üçgen Jüpiter.** Title/body source = `contracts.py` entry
`key="sun_trine_jupiter", kind="aspect"` — its **own** aura/trait/drive/shadow. The
body is **not** from `sun_house_4`; it is a distinct aspect entry. Aspects are
covered only by the non-canonical alias #1 (`house_placements_and_aspects`, _V1) →
**`LIVE_CARD_HAS_NO_FREE_OWNER`** in the narrow-Free model.

**Case 2 — Güneş 4. Ev with relationship/conflict language.** Exact mechanism:
`profile_v8_payload_builder` `pick_*`/`build_*` calls use
`hinted=section_pick[...] or by_hint[...]` with `fallback=by_domain["conversation"]`
/ `["effect"]` / `["shadow"]`. When the identity domain has no hinted fragment, the
card body **falls back to the conversation/effect (relationship) domain** →
`BODY_OWNER_MISMATCH` + `LEGACY_FALLBACK_USED`.

**Case 3 — Merkür 5. Ev with unrelated chips (Yükselen Boğa / Venüs 5. ev).** Chips
are assembled in `ProfileV8Adapter` from `chipCandidates` merging multiple sources
(`conversationThread?['chips']`, `conversationCard?['chips']`, `identityDrivers`)
plus backend hardcoded chip templates (`profile_v8_payload_builder` literals like
`"chips": ["Satürn","3. ev","ifade"]`). Chips are **not bound** to the card's own
placement family → `CHIP_OWNER_MISMATCH` / `CROSS_FAMILY_MERGE`.

**Case 4 — Repeated Güneş 4. Ev.** The same placement reaches: (a) lead identity /
unique block, (b) a placement card, (c) the aura/selected-placement badge. Mobile
`_dedupeCards` / `_dedupeByIdentity` only dedupe within a list, not across surfaces.
Classification: a mix of **correct repeated reference** (lead vs detail) and
**duplicate owner assignment** (card + badge) and possible **stale selected-card
state** → `DUPLICATE_SURFACE_ASSIGNMENT`.

**Case 5 — Koruyucu dalga badge.** Source = `mobile/lib/design/widgets/jovia_aura.dart:699`
`JoviaAuraSemanticFamily.protective => 'Koruyucu dalga'`, fed by `auraEntry['aura']`
in the adapter. It is an **aura semantic / shared component label**, computed
mobile-side — **not** an editorial asset owner and not a placement → treat as
`STATE_OR_SELECTION_LEAK` for ownership purposes (component label, `INTERNAL_ONLY`).

## G. Hidden-good-asset analysis (11 Free-ready)

| total | value |
|---|---|
| Free-ready assets rendered correctly (confirmed EXACT) | 0 (no runtime hash captured) |
| Free-ready rendered with mismatch | 2 house families (priority/support) — selection + chip + fallback mismatch |
| Free-ready **never rendered** (hidden good) | 7 sign/tone families (V3×4 + V4×3) not surfaced as standalone cards |
| live Free cards without a Free-ready asset | ≥1 (`sun_trine_jupiter` aspect; dominant signatures) |
| duplicate content hashes rendered across surfaces | ≥1 (repeated Güneş 4. Ev across lead/card/badge) |

The 9 sign-placement shadow assets (`moon_gemini`, `mercury_virgo`, …) are
**launch-useful but hidden**: rich reviewed content that the chart-driven dominant
selector does not surface as its own card.

## H. Slide-intent observation (no implementation)

`ProfileDetailSheet._splitBodyIntoSlides(body)` splits **one body string into
per-sentence slides** ("her cümle kendi slide'ında"); `_SlideKind` = hero, body,
mechanism, layer, shadow, growth, context. Consequences (structural):

- rendered slides = sentence count of the body (variable), **not** the modular
  role-block count.
- slide 1 (hero, up to a marker) can be **underfilled**; later reframe slides can be
  **overfilled** depending on sentence length.
- a single body = single owner per slide-set, but the per-sentence split mixes
  role semantics that the modular block plan keeps separate.
- relationship flow `01/02` → `02/02`: a 2-slide split of the relationship-preview
  body; both slides draw from one source field, so primary-owner count per slide = 1,
  but the body is a long-read (PREMIUM_ONLY in the narrow-Free decision). Exact word
  counts require a runtime capture (not done here) — flagged for the structured-slide
  scope.

## I. Narrow Free launch recommendation

Domains `identity, emotion, mind, relationship, action` — see decision JSON. Key
rules: single_card only (multi_slide not yet safe — detail sheet splits per-sentence,
not per-role-block); remove all `by_domain[*]` cross-domain fallback from Free
surfaces; aspects/dominants → hide or PREMIUM; aura badge INTERNAL_ONLY; one
canonical owner per surface (suppress cross-surface placement repeats); on missing
coverage (`mars_house_9`) omit the card, never substitute.

## J. Artifacts

- `backend/docs/product/FREE_PROFILE_R3D_Shadow_To_Live_Profile_Parity_Audit_TR_v0_1.md` (this report)
- `backend/docs/product/data/FREE_PROFILE_R3D_Shadow_Live_Parity_Matrix_TR_v0_1.json`
- `backend/docs/product/data/FREE_PROFILE_R3D_Narrow_Launch_Surface_Decision_TR_v0_1.json`

## K. Next scope — FREE-PROFILE-R4 (Card Ownership & Binding Repair)

Binding is repairable independently of slide generation (house/sign placements have
valid Free owners). Proposed bounded changes:

1. **Backend source provenance/binding** — `profile_v8_payload_builder.py`
   `pick_talents/build_conversation_hooks/build_affects_you/pick_defense/pick_intimacy/pick_mind`.
   Current: `fallback=by_domain[<other domain>]` injects cross-domain text.
   Corrected: drop cross-domain fallback for Free surfaces; emit explicit
   `owner_primary_key` per fragment. Visible impact: identity cards stop showing
   relationship/effect text. Rollback: keep fallback behind a flag. Tests: assert no
   Free card body originates from a non-matching `by_domain`. Fixture: Case 2.
2. **Mobile adapter binding** — `profile_v8_adapter.dart` `chipCandidates` assembly
   (lines ~447/487/514/559). Current: merges chips across cards/threads. Corrected:
   bind chips only to the card's own `owner_primary_key`. Impact: Merkür card stops
   showing Venüs/Yükselen chips. Rollback: per-surface flag. Tests: chip-owner ==
   card-owner. Fixture: Case 3.
3. **ProfilePage selection** — placement/lead selection. Current: same placement may
   feed lead + card + badge. Corrected: one canonical surface per owner per render.
   Impact: no repeated Güneş 4. Ev. Tests: cross-surface owner uniqueness. Fixture: Case 4.
4. **Chip/proof binding** — `proofRaw`/`proof_raw` provenance: bind proof to the
   card owner; drop unrelated proof. Tests: proof-owner == card-owner.
5. **Deduplication** — `_dedupeCards`/`_dedupeByIdentity`: extend to cross-surface
   owner dedupe. Tests: no duplicate content hash across surfaces.
6. **Stale state / fallback cleanup** — aura/selected-placement badge
   (`jovia_aura.dart` + `auraEntry`): make INTERNAL_ONLY for narrow Free; ensure no
   selected-card state leaks into card ownership. Fixture: Case 5.

Structured-slide implementation is **out of R4** — the audit shows binding can be
repaired independently of slide logic.

## L/M. Validation & commit

Both JSON artifacts pass `python -m json.tool`; `git diff --check` clean. Only the
three audit artifacts are committed. No production source modified.

## N. Verdict

`PROCEED_TO_CARD_BINDING_REPAIR`

(House/sign placements have valid Free owners; the divergences — cross-domain
fallback, cross-card chips, cross-surface duplication, aspect cards without a Free
owner, and the mobile aura badge — are each traced to an exact function and are
repairable in R4 without slide work. Runtime body-hash capture is deferred into R4
implementation, where the live pipeline is exercised per fixture.)
