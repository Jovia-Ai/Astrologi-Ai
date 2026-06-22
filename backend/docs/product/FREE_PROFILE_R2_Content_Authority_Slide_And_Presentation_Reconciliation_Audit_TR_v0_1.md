# FREE-PROFILE-R2 - Content Authority, Slide Contract and Premium Presentation Reconciliation Audit

## Audit Setup

- Branch: `codex/free-profile-r2-audit-wt`
- Starting commit: `c12473a70f027ecda0d5454de4ea21a76ce84a50`
- Worktree path: `/Users/sahradenizozdogan/.codex/worktrees/free-profile-r2-audit`
- Initial status: clean
- R1 audit on starting commit: not tracked on `HEAD` (`backend/docs/shou/FREE_PROFILE_R1_Modular_Profile_Card_System_Audit_TR_v0_1.md` is present in the dirty main tree, but `git ls-tree HEAD` does not include it)

## Verdict

`PROCEED_TO_NARROW_FREE_PROFILE_LAUNCH`

Reason: the free placement bank is usable today, but the full profile surface still mixes legacy poster logic, V8 teaser cards, detail-sheet storytelling, and Tam Okuma/internal preview content. The safe launch is a narrow free profile with SHOU meaning ownership kept separate from legacy editorial realization.

## A. Authority Reconciliation

| System | Meaning owner | Selection owner | Expression/content owner | Projection owner | Presentation owner | Fallback owner |
|---|---|---|---|---|---|---|
| Profile modular cards | Legacy profile narrative + sections builders, with SHOU preview only as a parallel diagnostic lane | `mobile/lib/app/tabs/profile_page.dart` and `mobile/lib/app/profile/profile_v8_adapter.dart` choose cards by family/keyword and dedupe | `backend/app/natal/profile_detail_editorial.py` and `backend/app/natal/narrative/phrase_lib_tr_profile.py` shape the copy | `backend/app/natal/public_builder.py` and `backend/app/natal/profile_v8_payload_builder.py` project `profile_narrative`, `sections_v2`, and `profile_v8` | `mobile/lib/app/profile/profile_v8_sections.dart`, `mobile/lib/app/profile/profile_detail_sheet.dart`, `mobile/lib/app/tabs/profile_page.dart` | Legacy poster fallback in `profile_page.dart` |
| Personality imprint cards | `backend/app/natal/personality_imprint/contracts.py` and its imported sign/tone libraries | `build_personality_imprint` plus `ProfileV8Adapter._pickLeadIdentityCard` / `_extractAuraLead` | `build_editorial_detail_blocks_for_imprint_entry` | `public_builder._personality_imprint_detail_cards` and `build_public_natal_view` | `ProfileV8SectionsView` unique metric slab, legacy poster chips, detail sheet | Support entries and background hints |
| Supporting threads | `backend/app/natal/supporting_threads_builder.py` | `profile_page.dart` + `ProfileV8Adapter._pickThread` | `build_editorial_detail_blocks_for_thread` | `public_builder._supporting_thread_detail_blocks_by_family` and `build_profile_narrative_v3` | `profile_page.dart` side theme rail, `ProfileV8SectionsView`, detail sheet slides | `profile_page.dart` synthesized full-map fallback |
| Narrative cards | `backend/app/natal/narrative/profile_narrative_engine.py` and `public_builder._build_profile_narrative_v3` | `profile_page.dart` chooses headline/hero/teaser cards; `ProfileV8Adapter` merges `narrativeCards` with `profilePublic` | `profile_detail_editorial.py` + `public_builder._detail_card_from_profile_block` | `public_builder._humanize_profile_narrative` / `build_profile_and_full_map_v8_payload` | Legacy poster tiles, feature rail, layered card detail page | `profile_page.dart` hero card fallback |
| Profile V8 | `backend/app/natal/profile_v8_payload_builder.py` after it receives already-resolved `profile_narrative` and `sections_v2` | `ProfileV8Adapter.fromPayload` precedence chain (`public`, `meta_info`, `profile_narrative.profile_public`) | `profile_detail_editorial.py` and `profile_v8_payload_builder.py` section builders | `public_builder.build_public_natal_view` + `build_profile_and_full_map_v8_payload` | `ProfileV8SectionsView`, `profile_detail_sheet.dart` | `profile_page.dart` legacy content view |
| SHOU semantic owners | `backend/app/natal/canonical_natal_meaning_authority.py` plus `sentence_pattern_selector_v2.py` | `shou_renderer_cards.py` and `shou_renderer_sentences.py` | `shou_renderer_sentences.py` + `general_render_cue_planner.py` | `shou_public_payload_preview.py` / internal preview projection | Internal-only preview payloads | `generic_fallback` nodes stay internal-only |
| SHOU internal preview | `shou_public_payload_preview.py` and `internal_typed_insight_preview_contract.py` | `shou_renderer_cards.py` | `shou_renderer_sentences.py` | `shou_public_payload_preview.py` | Internal preview consumers only | Not attached to public payloads |
| Tam Okuma | `mobile/lib/app/profile/profile_v9_adapter.dart` and its detail-card matching | `TamOkumaView` axis state + `profile_v9_adapter` matching | `profile_v9_adapter.dart` detail-card normalization | `profile_v9_adapter.dart` and `TamOkumaView` | `TamOkumaView`, layered kart detail page | Mock axis cards in `tam_okuma_view.dart` |
| Mobile fallback content | Legacy hard-coded copy in `profile_page.dart`, `profile_detail_sheet.dart`, `profile_relationship_preview.dart`, `tam_okuma_view.dart` | Same widgets pick from their own fallback strings when payloads are thin | Local copy helpers like `_profilePosterLeadText`, `_firstSentence`, `_mockIntroForAxis` | None; this is presentation fallback, not meaning projection | Legacy poster, relationship preview, detail sheet, Tam Okuma | Mock content and placeholder notes |

### Explicit answers

1. New SHOU owners do **not** fully replace legacy Profile card authority today. The SHOU authority stack is isolated and internal-only, but the live profile surface still selects legacy cards, threads, and poster copy in parallel.
2. Runtime-active legacy libraries still in play: `contracts.py`, `sign_support_library.py`, `tone_support_library.py`, `profile_detail_editorial.py`, `profile_v8_payload_builder.py`, `phrase_lib_tr_profile.py`, `supporting_threads_builder.py`, `public_builder.py`, `profile_v8_adapter.dart`, `profile_v8_sections.dart`, `profile_detail_sheet.dart`, `profile_page.dart`, `profile_relationship_preview.dart`, `profile_v9_adapter.dart`, `tam_okuma_view.dart`.
3. Reusable placement copy lives in the placement/sign banks: `contracts.py` V1/V2/priority/support banks, `sign_support_library.py`, `tone_support_library.py`, plus the direct title/caption helpers in `phrase_lib_tr_profile.py` and `supporting_threads_builder.py`.
4. Synthesized or cross-placement copy lives in `public_builder.py`, `profile_detail_editorial.py`, `supporting_threads_builder.py`, `shou_renderer_sentences.py`, `shou_renderer_cards.py`, and the legacy mobile merger code in `profile_page.dart` / `profile_v8_adapter.dart`.
5. Safe Free Profile assets are the direct placement/sign copies that stay one key to one explanation: house/sign/aspect banks, asc-ruler tones, short editorial titles, and non-synthesized chip labels. Anything that blends a support key, a secondary thread, or a preview paragraph needs an explicit registry wrapper before it can be meaning-owned by Free Profile.
6. Direct library-to-SHOU connection violates ownership boundaries when a legacy library becomes the semantic source instead of a realized surface. The biggest violations are `supporting_threads_builder.py` feeding detail copy straight into SHOU presentation, `profile_page.dart` choosing legacy cards before SHOU projection, and using the mobile mock/fallback copy as if it were the actual meaning owner.

## B. Content Library Inventory

### What I counted

- Content source files reviewed: 16
- Classified asset families: 25
- Free-ready asset families: 11
- Premium-only asset families: 3
- Unknown/unowned asset families: 1
- Slide-mode distribution: `single_card` 14, `multi_slide` 7, `long_read` 4

### Classification summary

- `FREE_MODULAR_READY`: direct one-key placement/sign assets that can safely render as modular cards.
- `FREE_MODULAR_NEEDS_EDIT`: direct placement assets that are reusable but still need explicit registry constraints or slide splitting.
- `PREMIUM_SYNTHESIS_ONLY`: assets that already mix multiple keys, support lines, or story sequencing.
- `SUPPORTING_COPY_ONLY`: reusable presentation copy, titles, hints, chip labels, and fallbacks that should not own meaning.
- `DUPLICATE_OR_SUPERSEDED`: normalization or replacement copy that should not be treated as a source of truth.
- `UNSAFE_OR_UNSUPPORTED`: placeholders, mock data, or internal-only preview copy that should not launch as content truth.
- `MISSING_OWNER`: copy that is visible in the product but lacks a clean semantic owner.

## C. Proposed Editorial Content Asset Registry

A safe registry needs to keep meaning ownership outside the editorial layer.

```json
{
  "asset_id": "editorial.sun.house_4.tr.v1",
  "source_path": "backend/app/natal/personality_imprint/contracts.py",
  "locale": "tr-TR",
  "content_kind": "planet_house",
  "primary_key": "sun_house_4",
  "domain": "identity",
  "meaning_authority": "none",
  "expression_authority": "editorial_library",
  "allowed_tiers": ["free"],
  "allowed_surfaces": ["identity", "first_felt"],
  "prohibited_surfaces": ["origin"],
  "presentation_mode": "multi_slide",
  "status": "reviewed",
  "supersedes": [],
  "quality": {}
}
```

### Free Profile flow

`chart placement key -> eligible editorial asset -> modular card`

The editorial asset is a realization layer only. It may adapt tone, line breaks, and surface order, but it must not replace the placement key as the semantic owner.

### Premium SHOU flow

`SHOU semantic owner -> PremiumNarrativeBrief -> premium realization`

Legacy editorial assets may contribute reviewed phrasing or narrow support lines, but the semantic brief stays with SHOU.

## D. Long-Text and Slide-Intent Audit

The current system mixes several intent shapes:

- one short card
- one long card
- two-slide story
- three-to-five-slide sequence
- long scroll article
- parent card plus detail slides
- synthesis narrative

The concrete split decision is currently made in `mobile/lib/app/profile/profile_detail_sheet.dart`:

- `leadSentence` is the first sentence only
- remaining sentences are moved into later body slides
- `details` become their own mechanism slide
- `extraLayers` become separate layer slides
- shadow text is peeled off by marker and becomes its own slide
- growth and context become additional slides when present

That is why a relationship flow can produce an underfilled `01/02` cover and an overfilled `02/02` second page: the hero owns only the first sentence, while the remaining semantic blocks pile into the next page.

The same overfill pattern is strengthened by the profile page merge path:

- `profile_page.dart` chooses a lead or featured narrative card
- `ProfileV8Adapter.fromPayload` merges `narrativeCards`, `profile_narrative.profile_public.detail_cards`, and `profilePublic.blocks`
- `ProfileV8SectionsView` sends section bullets and extra layers into the detail sheet
- `profile_detail_sheet.dart` then renders all of those blocks as sequential slide units

### Required example

For the relationship screen, the observed result comes from this combination:

- slide `01/02` is a hero/cover with only the headline and one lead sentence
- slide `02/02` receives the remaining body sentences plus the mechanism/details blocks
- 7H Scorpio, Mars 7H, Mars Sagittarius, shadow, and growth copy are all eligible to accumulate into the second page when the section model has more than one semantic source
- the reading model is ambiguous because the same flow mixes scrollable content with a page counter and slider progress

## E. Canonical Slide Contract

A stable contract should keep one dominant idea per slide and avoid arbitrary character-based splitting.

```json
{
  "presentation": {
    "mode": "single_card | multi_slide | long_read",
    "slides": [
      {
        "slide_id": "...",
        "role": "recognition | lived_pattern | mechanism | tension | capacity | context",
        "title": "...",
        "body": "...",
        "primary_source": "...",
        "support_sources": [],
        "word_count": 0
      }
    ]
  }
}
```

### Proposed contracts

- Free modular placement card: `single_card`, 1 to 3 slides maximum, one placement per slide
- Free aspect card: `multi_slide`, 1 to 3 slides, no mixed ownership with unrelated support lines
- Premium SHOU synthesis sequence: `multi_slide` or `long_read`, 3 to 6 slides, with `primary_source` fixed to SHOU
- Origin/background detail: separate slide family, never merged into the lead card unless explicitly requested
- Proof/evidence disclosure: separate supporting slide family, never the hero slide

### Rules

- no arbitrary split by character count
- no split based only on paragraph count
- no repeated body across slides
- first slide must contain meaningful content
- later slides must add new information
- one primary owner per slide
- mobile must not mix carousel paging and uncontrolled long scroll unless the contract explicitly says so

## F. Mobile Presentation and Design Audit

### Keep / repair / replace matrix

| Component family | Classification | Reason |
|---|---|---|
| `ProfilePage` legacy poster stack | `RESTRUCTURE_CONTENT` | It still mixes hero, feature tiles, side themes, and fallback story copy in one surface |
| `ProfileV8SectionsView` teaser cards | `KEEP_WITH_BINDING_REPAIR` | The teaser-first pattern is usable, but card-to-detail bindings need explicit ownership metadata |
| `ProfileDetailSheet` page-view story modal | `KEEP_WITH_BINDING_REPAIR` | The slide model is strong, but the split rules need a structured slide contract |
| `ProfileRelationshipPreview` | `KEEP_WITH_BINDING_REPAIR` | It is readable, but it still mixes narrative blocks, evidence, and fallback prompts on one panel |
| `TamOkumaView` | `REMOVE_FROM_LAUNCH` | Keep internally for now; the mock axis cards are not launch truth |
| `LayeredKartDetailPage` | `KEEP_AS_IS` | The 3-layer detail page is coherent enough to keep as a detail destination |
| `JoviaReadingPanel` and fallback cards | `KEEP_AS_IS` | Good enough as an error/empty-state primitive |
| `ProfilePosterLeadSection` / feature rail / placements strip / thread section | `RESTRUCTURE_CONTENT` | The legacy poster layout is useful but too crowded and too overlapping in role |
| `ProfileV8InsightStrip` | `KEEP_AS_IS` | Small, legible, and already bounded |
| `ProfileV8UniqueMetricSlab`, `ProfileV8PastTeaserCard`, `ProfileV8FirstImpressionCard`, `ProfileV8DefenseCard`, `ProfileV8FirstFeltCard`, `ProfileV8SectionCard` | `KEEP_WITH_BINDING_REPAIR` | The card primitives are fine, but their source binding needs a clearer registry and slide contract |
| `ProfileDetailFlowPage` PageView stacks | `RESTRUCTURE_CONTENT` | It is a stronger flow engine than the legacy poster, but it still mixes multiple semantic planes |

### Screen findings

1. `01/02` cover is underfilled.
2. `02/02` is overfilled.
3. Multiple semantic units are displayed as visually identical text boxes.
4. The reading model is unclear: carousel, long scroll, or story.
5. The screen does not yet feel like one coherent premium component system.

## G. Launch Surface Decision

### Option 1 - Existing Profile recovery
- Too broad for current content ownership and slide-contract state

### Option 2 - Narrow Free Profile
- Best fit for the current repository state
- Keep placement-led identity, emotion, mind, relationship, and action surfaces
- Hide origin, defense, and synthesis-heavy sections
- Keep Tam Okuma internal

### Option 3 - Full current surface cleanup
- Highest effort
- Would require aligning content ownership and presentation at the same time

### Recommendation

Choose Option 2.

This lets the team launch a narrower surface without letting legacy libraries become meaning owners.

## H. Required Fixture Review

### Fixture A

`Sun Leo 4H | Moon Gemini 1H | Mercury Virgo Rx 5H | Venus Virgo 5H | Mars Sagittarius 7H | ASC Taurus`

Available legacy assets:

- `sun_house_4` from `contracts.py`
- `moon_gemini` from `sign_support_library.py`
- `mercury_virgo` from `sign_support_library.py`
- `venus_virgo` from `sign_support_library.py`
- `mars_sagittarius` from `sign_support_library.py`
- `sun_taurus` / asc-ruler tone material from `tone_support_library.py`

SHOU-owned meanings:

- identity visibility and center from the Sun placement
- quick mental movement from Moon Gemini and Mercury Virgo
- relationship style and clean desire from Venus Virgo + Mars Sagittarius
- ascendant tone should stay on the SHOU side, not be copied as a free-form narrative owner

Free modular eligible assets:

- direct placement cards for Sun, Moon, Mercury, Venus, Mars
- short trait / shadow / gift lines only

Premium-only assets:

- cross-card synthesis across mind, relationship, and origin
- any sequence that combines house 4, house 5, and house 7 into one reading arc

Current rendered surfaces:

- legacy poster story block
- V8 teaser cards
- detail sheet / long-read modal when tapped

Incorrect merges:

- origin plus relationship into one hero card
- shadow and growth into the same visible card without a separate slide contract

Expected presentation modes:

- identity: `single_card`
- mind: `multi_slide`
- relationship: `multi_slide`
- origin: separate detail family

Missing content:

- a clean registry for the free card assets
- an explicit rule that keeps asc-ruler tone from becoming a meaning owner

### Fixture B

`Sun Capricorn 1H | Moon Leo 8H | Mercury Capricorn Rx 1H | Venus Sagittarius 12H | Mars Virgo 9H | ASC Capricorn`

Available legacy assets:

- `sun_house_1` / `sun_capricorn`-style material
- `moon_leo` and `moon_house_8`
- `mercury_capricorn` and `mercury_house_1`
- `venus_sagittarius` and `venus_house_12`
- `mars_virgo` and `mars_house_9`-style material
- `asc_ruler_saturn` tone material

SHOU-owned meanings:

- strong self-definition and control through the Capricorn Sun / Mercury / ASC cluster
- emotional intensity and trust-evaluation from Moon Leo in the 8th
- private love and meaning-seeking from Venus Sagittarius in the 12th
- practical movement and craft from Mars Virgo in the 9th

Free modular eligible assets:

- direct placement cards for the Sun / Moon / Mercury / Venus / Mars keys
- short, one-placement editorial cards for each axis

Premium-only assets:

- the combined story of duty, private desire, hidden meaning, and relational intensity

Current rendered surfaces:

- legacy poster cards
- V8 teaser surface
- relationship/detail pages for deeper reads

Incorrect merges:

- Capricorn identity + 12th-house love + 8th-house emotional intensity in one flat card
- growth, shadow, and mission all on the first slide

Expected presentation modes:

- identity: `single_card`
- private feeling / love: `multi_slide`
- mind and work: `multi_slide`
- deep synthesis: `long_read`

Missing content:

- a premium synthesis contract that keeps SHOU meaning above the editorial realization layer

## I. Final Implementation Plan

### 1) Content Asset Registry

- Expected files to change: `backend/app/natal/personality_imprint/*`, `backend/app/natal/narrative/phrase_lib_tr_profile.py`, `backend/app/natal/supporting_threads_builder.py`, `backend/app/natal/profile_v8_payload_builder.py`
- Prohibited files: mobile widgets, `shou_renderer_*`, API response shape outside registry attachment
- Acceptance tests: registry rows resolve from one placement key to one permitted asset family
- Rollback boundary: remove registry lookup, keep existing copy generation paths
- Dependency order: first

### 2) Legacy Library Adapter

- Expected files to change: `backend/app/natal/public_builder.py`, `mobile/lib/app/profile/profile_v8_adapter.dart`
- Prohibited files: meaning authority internals, SHOU renderers
- Acceptance tests: legacy copy is attached as expression only, not as owner
- Rollback boundary: adapter fallback to current precedence chain
- Dependency order: after registry

### 3) Card Ownership and Binding Repair

- Expected files to change: `mobile/lib/app/tabs/profile_page.dart`, `mobile/lib/app/profile/profile_v8_sections.dart`
- Prohibited files: core meaning selection, public payload schema
- Acceptance tests: every visible card can report a single primary owner and a deterministic fallback owner
- Rollback boundary: restore current dedupe logic
- Dependency order: after registry + adapter

### 4) Structured Slide Payload

- Expected files to change: `mobile/lib/app/profile/profile_detail_sheet.dart`, `mobile/lib/app/profile/profile_v8_sections.dart`
- Prohibited files: backend meaning builders
- Acceptance tests: each slide has one dominant idea, one primary owner, and no accidental body duplication
- Rollback boundary: keep current hero/body split if the new contract fails
- Dependency order: after card binding repair

### 5) Mobile Renderer and Design Recovery

- Expected files to change: `mobile/lib/app/tabs/profile_page.dart`, `mobile/lib/app/profile/profile_detail_sheet.dart`, `mobile/lib/app/profile/profile_v8_sections.dart`, `mobile/lib/app/profile/profile_v9_adapter.dart`
- Prohibited files: SHOU canonical ownership files
- Acceptance tests: profile reads cleanly as one system, not three stitched ones
- Rollback boundary: retain current poster/teaser layouts but hide launch-unsafe sections
- Dependency order: after slide contract

### 6) Content Migration and Editorial Review

- Expected files to change: content docs and registry data only
- Prohibited files: runtime logic and launcher widgets
- Acceptance tests: every migrated asset has a declared owner, tier, and surface list
- Rollback boundary: keep old copy files untouched until the new registry is validated
- Dependency order: after registry and binding repair

### 7) Launch QA and rollout

- Expected files to change: test fixtures and audit docs only
- Prohibited files: semantic owners and public payload shape
- Acceptance tests: fixture A and B render with the right launch scope and without mixed ownership
- Rollback boundary: disable narrow free launch and fall back to current profile page
- Dependency order: last

## J. Final Verdict

`PROCEED_TO_NARROW_FREE_PROFILE_LAUNCH`

Remaining risk is not missing content; it is that the current runtime still lets legacy editorial realization act like meaning ownership in a few places. The narrow free launch avoids that boundary breach while preserving the good placement copy.
