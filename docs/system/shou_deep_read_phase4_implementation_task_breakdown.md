# SHOU deep_read Phase-4 Implementation Task Breakdown

> Planning artifact only. No code. No renderer change. No public
> output change in this document.

## 1. Purpose

This document breaks the approved Phase-4 renderer design into an
implementation-shaped task list for the **hidden/private pilot only**.
It does not authorize code by itself. It defines:

- likely file touch map
- proposed flag strategy
- data flow from Phase-3 metadata into a pilot renderer
- proposed output contract
- QA set and test plan
- non-goals
- rollback strategy

Source of truth:

- [shou_deep_read_phase4_renderer_design_plan.md](/Users/sahradenizozdogan/Astrologi-Ai/docs/system/shou_deep_read_phase4_renderer_design_plan.md)
- [shou_voice_phase3_hidden_private_closure.md](/Users/sahradenizozdogan/Astrologi-Ai/docs/system/shou_voice_phase3_hidden_private_closure.md)

## 2. Pilot Scope

Phase-4 implementation remains strictly bounded to:

- hidden/private `deep_read` only
- `pattern_to_gift` pilot profile only
- Turkish-primary (`TR`) output only

Still out of scope:

- any other `deep_read` family
- global taxonomy work
- mobile
- endpoints
- ARC/A2 merge
- generalized `pattern_to_gift`

## 3. New Flag Proposal

Phase-4 should use a **separate** renderer flag from Phase-3.

Proposed name:

- `ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_DEEP_READ_RENDERER`

Principles:

- default `off`
- independent from Phase-3 metadata flag
- Phase-3 flag may be `on` while Phase-4 renderer flag remains `off`
- Phase-4 user-visible behavior must never activate through Phase-3 flag alone

Flag split:

- Phase-3 flag: internal metadata availability
  - `ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_PHASE3_INTERNAL_METADATA`
- Phase-4 flag: user-visible deep_read rendering
  - `ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_DEEP_READ_RENDERER`

## 4. Exact Files Likely To Be Touched

### 4.1 Primary implementation files

- [backend/app/meaning/composed_detail_renderer.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/meaning/composed_detail_renderer.py)
  - primary pilot renderer entrypoint
  - likely place for alternate hidden/private card rendering path
  - likely place for share line / trace surfaces assembly

- [backend/app/meaning/projection_shadow_v1_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/meaning/projection_shadow_v1_builder.py)
  - only if routing must choose Phase-2 vs Phase-4 pilot render path
  - should remain a narrow flag-checked switch, not a broader projection rewrite

### 4.2 Existing metadata source files

- [backend/app/natal/natal_promise_packets.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/natal_promise_packets.py)
  - ideally **no semantic expansion**
  - touch only if a minimal metadata normalization bug appears
  - Phase-4 should primarily consume the already-committed Phase-3 metadata

### 4.3 Test files

- [backend/tests/test_composed_detail_renderer.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/tests/test_composed_detail_renderer.py)
  - renderer unit tests
  - pilot flag-off / flag-on behavior
  - exact-owner vs composed-fallback behavior

- [backend/tests/test_natal_public_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/tests/test_natal_public_builder.py)
  - route-equivalent output contract
  - no-op with Phase-4 flag off
  - no leakage to other surfaces
  - non-target chart guards

### 4.4 Files that should stay untouched unless explicitly re-approved

- `backend/app/natal/public_models.py`
- `backend/app/natal/public_builder.py`
- endpoint/router files
- mobile files
- config/taxonomy files

Default rule:

- avoid `public_models.py` unless a later explicit public contract
  decision requires it
- avoid endpoint work entirely

## 5. Data Flow

Phase-4 should consume the already-bounded Phase-3 metadata path, not
invent a parallel ownership layer.

### 5.1 Upstream source

`relationship_route.hidden_private_love` candidate / exact-owner
source already carries:

- `deep_read_phase3`
- semantic carriers:
  - `lived_scene`
  - `direct_meaning`
  - `shadow_or_friction`
  - `gift`
  - `growth_direction`

### 5.2 Internal handoff

Proposed flow:

1. candidate/exact source enters hidden/private renderer seam
2. Phase-4 flag checked
3. renderer reads `deep_read_phase3`
4. renderer maps role bindings into slide plan
5. renderer produces pilot card surfaces
6. promotion to `profile_public.composed_detail_cards` remains bounded to the same family only

### 5.3 Metadata mapping

Verified against the committed Phase-3 schema in
`backend/app/natal/natal_promise_packets.py` (lines 277–286) and
`backend/app/meaning/composed_detail_renderer.py` (lines 559–577).
Phase-4 must consume these shapes verbatim — not invent parallel
names:

- `slide_profile` → `"pattern_to_gift"` → pilot render logic
- `role_bindings.origin_hint` → `{surface_role: "hidden_mechanism",
  eligible: bool, allow_reasons: [str], deny_reasons: [str]}`
  → opt-in secondary surface only if `eligible == true` AND
  `deny_reasons` is empty
- `role_bindings.gift` → `{surface_role: "gift_in_silence",
  source_field: "gift"}` → grounded gift copy mode, sourced from
  the packet's `gift` field
- `role_bindings.shadow` → `{surface_role: "protective_pattern",
  source_field: "shadow_or_friction"}`
- `role_bindings.integration` → `{surface_role: "safe_visibility",
  source_field: "growth_direction"}`
- `map_trace` → separate trace surface
- `deselected_trace` → separate “not rendered” surface

### 5.4 Data-flow constraint

Phase-4 may sequence and humanize meaning, but may not:

- alter semantic ownership
- upgrade ineligible origin into main text
- pull deselected items into the thesis
- expose technical anchors as main prose

## 6. Proposed Output Contract

This section is a **proposal for later implementation approval**. It
does not change public output now.

### 6.1 Parent card

Proposed parent card surface:

- one thesis
- one lived hidden/private frame
- no mechanical astrology
- no repeated summary on every child slide

Suggested fields:

- `id`
- `node_id`
- `headline`
- `teaser`
- `body`
- `family`
- `emphasis`
- `origin`

### 6.2 Slides

Proposed slide contract:

- `slides[]`
- 5–7 items
- each item keeps:
  - `id`
  - `title`
  - `body`

Default slide order:

1. private scene
2. hidden mechanism
3. protective pattern
4. gift in silence
5. safe visibility

Extended order allowed only if semantically distinct:

- add `how_seen`
- add `integration`

### 6.3 Share line

Proposed additional surface:

- `share_line`

Constraints:

- one short line
- no technical tokens
- no motivational uplift
- no invasive origin

### 6.4 `map_trace`

Proposed additional surface:

- `map_trace`

Purpose:

- explain role mapping
- light provenance only
- must remain secondary, not thesis-owning

### 6.5 `deselected_trace`

Proposed additional surface:

- `deselected_trace`

Purpose:

- show intentionally omitted angles
- prevent “why wasn’t X rendered?” confusion
- stay non-dominant and non-teaching in tone

### 6.6 Contract caution

Any public field addition above requires a later explicit approval at
implementation time. The default safer path is:

- keep existing parent/slides contract stable first
- treat `share_line`, `map_trace`, and `deselected_trace` as proposed additions
- if needed, ship the pilot in phases rather than widening the public shape all at once

## 7. 3-Chart QA Set Proposal

Each chart serves a **distinct gate** — the three are not
interchangeable, and the blind/falsification discipline depends on
keeping the purposes separate:

1. **`2007` — felt-experience quality bar** *(blind/falsification gate)*
   - has gold + LOCK PASS (`shou_voice_deep_read_lock_BLIND.md`)
   - this is the **only chart** that satisfies the felt-experience
     "feels seen vs feels presumed" judgement; the Phase-4 render on
     2007 must hold the canonical bar set by the LOCK reference

2. **`1996-12-28 Istanbul` — code-seam compatibility** *(NOT a felt
   validation; no gold)*
   - this is the existing Phase-2/Phase-3 implementation pilot
     fixture (see `shou_voice_phase3_hidden_private_closure.md` and
     `tests/test_natal_public_builder.py`
     `v0_10_phase2_istanbul_1996_emits_exactly_one_hidden_private_love_card`)
   - role here is **compatibility only**: route-equivalent payload,
     flag-off no-op, exact-owner precedence preserved
   - it is **not** in the falsification corpus and must **not** be
     used as a felt-experience proxy for 2007

3. **`1975 Helsinki` — overreach contrast** *(falsification gate)*
   - no-dominant chart from the validated corpus; deliberately
     selected to fail hidden/private if the renderer over-pulls
   - pass condition: hidden/private tone does **not** activate on 1975

Reserve contrast if needed:

- `2010 Sydney` — distributed secondary-visibility contrast (same role
  as 1975, used only if 1975 is inconclusive)

Reserve contrast if needed:

- `2010 Sydney`
  - distributed secondary-visibility contrast

Review questions:

- does hidden/private feel seen rather than presumed?
- does origin stay non-invasive?
- does the contrast chart avoid false hidden/private pull?

## 8. Tests To Add Before Implementation

### 8.1 Flag-off no-op tests

- Phase-4 flag off preserves current hidden/private Phase-2 output exactly
- Phase-4 flag off preserves current `profile_public.composed_detail_cards` field set
- Phase-4 flag off leaves non-target charts unchanged

### 8.2 Flag-on pilot renderer tests

- exact-owner hidden/private source renders through the new pilot path
- composed fallback hidden/private source renders through the same contract
- renderer uses `deep_read_phase3.slide_profile == pattern_to_gift`
- renderer refuses if pilot metadata is missing or malformed

### 8.3 Origin safety tests

These tests must **assert on the existing committed Phase-3
telemetry** (`role_bindings.origin_hint.allow_reasons` /
`deny_reasons`), not invent a new safety layer:

- `origin_hint` omitted when `eligible == false` (already enforced by
  the Phase-3 assessment; Phase-4 must respect, never override)
- for every rendered passage: `deny_reasons` is empty (renderer must
  refuse to fire `origin_hint` if any deny reason is present)
- `allow_reasons` non-empty when fired (positive eligibility evidence
  is recorded, not assumed)
- origin stays out of the default main slide sequence unless
  explicitly surfaced as opt-in
- origin text contains no banned diagnostic/blame/event-certainty
  language (packet §6 bad-example scan)

### 8.4 Gift drift tests

- gift slide contains no coaching/motivational formula
- gift does not become a generic encouragement ending

### 8.5 Trace-surface tests

- `map_trace` does not contaminate main text
- `deselected_trace` does not contaminate main text
- technical anchors stay out of parent/slides unless explicitly on the trace side

### 8.6 Regression tests

- no other family adopts the Phase-4 renderer path
- current hidden/private exact-owner precedence still holds unless explicitly redesigned
- no other public surface receives Phase-4-only fields by accident

### 8.7 Manual QA before enablement

- 3-chart side-by-side hidden/private read
- blind felt-experience check
- banned phrase scan
- origin safety scan
- gift motivational drift scan

## 9. Explicit Non-Goals

Phase-4 hidden/private implementation must **not** do any of the following:

- generalize to other `deep_read` families
- modify natal packet semantics
- widen global taxonomy
- add mobile consumption work
- add endpoint work
- merge ARC/A2 logic
- solve `identity_polarity`, `held_plurality`, or `emotional_base`
- turn `map_trace` into a teaching/explainer mode

## 10. Rollback Strategy

Rollback must be operationally trivial.

### 10.1 Primary rollback

- keep Phase-4 renderer behind its own flag
- default remains `off`
- disabling the Phase-4 flag returns behavior to the committed Phase-3 no-op baseline

### 10.2 Structural rollback

- preserve Phase-3 metadata as independent infrastructure
- if Phase-4 render quality fails, remove or disable only the pilot renderer branch
- do not unwind candidate metadata unless it proves harmful by itself

### 10.3 Test-backed rollback confidence

Rollback is considered safe only if:

- Phase-4 flag off path still passes the Phase-3 no-op tests
- Phase-2 hidden/private exact-owner behavior remains intact
- no endpoint/mobile contract depends on the Phase-4 branch

## 11. Approval Questions Before Implementation

Before any code starts, the following should be explicitly approved:

1. exact Phase-4 flag name
2. whether `share_line` is part of the first pilot or deferred
3. whether `map_trace` / `deselected_trace` are public pilot surfaces or later optional surfaces
4. primary 3-chart QA set (with the §7 purpose split intact: 2007 =
   felt bar, 1996 = code-seam compatibility, 1975 = overreach contrast)
5. whether Phase-4 first pass keeps the current parent/slides public
   contract stable before adding auxiliary surfaces
6. **Phase-3 schema reconciliation confirmed** — §5.3 metadata
   mapping was cross-checked against the committed schema
   (`natal_promise_packets.py:277–286`,
   `composed_detail_renderer.py:559–577`). carrier names
   (`lived_scene`, `direct_meaning`, `shadow_or_friction`, `gift`,
   `growth_direction`), `slide_profile: "pattern_to_gift"`, and the
   full `role_bindings` shape (`origin_hint` w/ telemetry, `gift`,
   `shadow`, `integration` w/ `surface_role`/`source_field`) all
   match. Phase-4 must consume these verbatim; no parallel naming.

## 12. Recommended Execution Order

If approved later, the implementation order should be:

1. freeze Phase-4 public contract for the pilot
2. add flag-off regression tests first
3. add flag-on renderer tests second
4. implement only the hidden/private renderer branch
5. run automated regression tests
6. run 3-chart side-by-side manual QA
7. only then decide on pilot enablement

## 13. Decision

This breakdown is ready for approval review.

It does not authorize implementation by itself. The next step, if
approved, would be a separate “implement Phase-4 hidden/private pilot”
request under the bounded files, flag strategy, QA set, and rollback
rules defined here.

## 14. Review-readiness changelog

Three review-grounding edits applied before re-review (no scope
change, no code, no taxonomy change):

- **§5.3** — metadata mapping now lists the **verbatim committed
  shape** of `role_bindings` (`origin_hint` with
  `allow_reasons`/`deny_reasons` telemetry, `gift`
  `gift_in_silence`/`gift`, `shadow`
  `protective_pattern`/`shadow_or_friction`, `integration`
  `safe_visibility`/`growth_direction`), cross-referenced to the
  exact source lines. Phase-4 must consume verbatim; no parallel
  naming.
- **§7** — 3-chart QA set purposes made explicit and non-fungible:
  2007 = felt-experience bar (only chart with gold + LOCK), 1996 =
  code-seam compatibility (no gold, *not* a felt validation),
  1975 = overreach contrast (falsification gate). Blind/falsification
  discipline preserved.
- **§8.3** — origin safety tests now **assert on the existing
  committed Phase-3 telemetry** (`allow_reasons`/`deny_reasons`)
  rather than inventing a parallel safety layer; refusal-to-fire is
  required whenever `deny_reasons` is non-empty.
- **§11** — added explicit "Phase-3 schema reconciliation confirmed"
  approval item so a future implementer does not redo or skip the
  cross-check.
