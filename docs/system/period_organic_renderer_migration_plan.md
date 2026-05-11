# Organic Period Renderer Migration Plan

Generated on 2026-05-05.

## TL;DR

1. **Current 4-field public surface lives inside `public.period_core`, not the typed `public.period` summary surface.** The real runtime owner path is `deep_archetype_engine.build_period_core(...) -> astrolog_narrative_engine.build_period_story(...) -> public_builder.build_public_response(...)`. Full consumer table is in sections 2 and 3.
2. **Mobile is `mixed`, but not 4-segment-native.** Current mobile runtime does **not** render `period_opening / mechanism / growth_edge / what_it_builds` as four dedicated period UI blocks. `PeriodCoreDto` only parses `title / core_story / upper_meaning / big_picture / mechanism`; `period_opening`, `growth_edge`, and `relational_or_life_expression` are ignored. Separate section rendering exists for **period event cards**, not for `period_core`.
3. **`period_reading_v1` is additive-safe if added under `period_core`.** `PublicTransitResponse.period_core` is an untyped `dict`, backend route shapers pass unknown keys through, and current mobile DTO parsing ignores unknown keys. This is backward-compatible if legacy fields remain populated.
4. **Test impact is real but mostly assertion-based, not snapshot-heavy.** Highest-impact backend file is `backend/tests/test_astrolog_narrative_engine.py`; highest mobile mapping risk is `mobile/test/transit_source_mapping_test.dart`. If old fields stay populated, Phase 1 should not require broad snapshot regeneration. Expected direct update surface: ~4 backend test files, ~0 required mobile test changes for backend-only Phase 1, plus 1 new backend contract/quality test file.
5. **Smallest safe phased path is 3 phases.**
   1. Add additive `period_core.period_reading_v1` and refactor renderer to organic composer output while preserving legacy 4 fields.
   2. Coordinate mobile to consume `period_reading_v1`.
   3. Remove legacy fields only after all consumers migrate.
6. **Recommended first implementation PR scope:** backend-only Phase 1, with `period_reading_v1` nested inside `period_core`, internal `composer_plan` debug, organic `full_text`, legacy 4-field compatibility shadow, and guardrail migration for organic blocks/full text.

## 1. Current Public Payload Structure

### 1.1 Equivalent schema files

There is no `backend/app/transit/narrative/transit_narrative_public_payload.py` in the current checkout.

The effective equivalent is split across:

- `backend/app/transit/present/public_models.py`
- `backend/app/transit/present/public_builder.py`
- `backend/app/transit/narrative/deep_archetype_engine.py`
- `backend/app/transit/narrative/astrolog_narrative_engine.py`
- mobile DTO mirrors in `mobile/lib/app/timing/narrative_dtos.dart`

### 1.2 Public shape overview

There are **two period surfaces**:

1. **Typed summary surface**
   - `public.period`
   - `PublicPeriod` in `public_models.py`
   - fields:
     - `core_story`
     - `summary.main_theme`
     - `summary.one_liner`
     - `period_space`
   - this is relatively stable and sparse

2. **Raw/additive runtime surface**
   - `public.period_core`
   - currently `dict`, not strongly typed
   - this is where all renderer/composer strings actually live

### 1.3 Current `period_core` field inventory

| Field | Type | Required in runtime | Added in | Current producer |
|---|---|---|---|---|
| `title` | `str` | yes | pre-audit legacy period core | `deep_archetype_engine.build_period_core(...)` |
| `core_story` | `str` | yes | pre-audit legacy period core | `build_period_core(...)`, then rebuilt from renderer output |
| `upper_meaning` | `str` | yes | pre-audit legacy period core | `build_period_story(...).upper_meaning` |
| `period_opening` | `str` | yes | pre-PR-SF1 period v2 surface; exact introducing PR not encoded in checkout | `build_period_story(...).period_opening` |
| `big_picture` | `str` | yes | pre-PR-SF1 period v2 surface | `build_period_story(...).big_picture` |
| `mechanism` | `str` | yes | pre-PR-SF1 period v2 surface | `build_period_story(...).mechanism` |
| `growth_edge` | `str` | yes | pre-PR-SF1 period v2 surface | `build_period_story(...).growth_edge` |
| `relational_or_life_expression` | `str` | yes | pre-PR-SF1 period v2 surface | `build_period_story(...).relational_or_life_expression` |
| `what_it_builds` | `str` | yes | pre-PR-SF1 period v2 surface | `build_period_story(...).what_it_builds` |
| `tags` | `list[dict]` | yes | legacy | `build_period_core(...)` |
| `featured_events` | `list[dict]` | yes | legacy | `build_period_core(...)` |
| `canonical_period_spine` | `dict` | yes | pre-PR-SF1 canonical spine wiring | `public_builder -> build_canonical_period_spine(...)` |
| `_period_story_debug` | `dict` | optional but usually present | pre-PR-SF1, enriched in PR-SF1 and PR-4.1 | `build_period_story(...).debug` |
| `semantic_focus` | `dict` | optional/additive | **PR-SF1** | `resolve_period_semantic_focus(...).to_debug_dict(...)` |
| `period_teaser` | `dict` | optional/additive | **S1-1** comment-marked in code | `public_builder._build_period_teaser(...)` |
| `period_locked` | `bool` | optional/additive | **S1-1** | `public_builder.build_public_response(...)` |
| `period_version` | `str` | optional/additive | **S1-1** | `public_builder._build_period_version(...)` |
| `story_tracks` | `dict` | optional | legacy period track surface | `build_period_core(...)` |
| `_event_story_map` | `dict` | optional/internal | legacy | `build_period_core(...)` |
| `_debug_root_causes` | `list` | optional/internal | legacy | `build_period_core(...)` |

### 1.4 Notes on “which PR added it”

The current checkout does **not** preserve exact PR provenance for the legacy 4-field period surface.

What can be identified from the code and recent changes:

- `semantic_focus` on `period_core` is **PR-SF1**
- `semantic_focus` renderer consumption + `composer_mode` debug markers are **PR-4.1**
- `period_teaser / period_locked / period_version` are marked as **S1-1** in code comments
- `period_opening / big_picture / mechanism / growth_edge / relational_or_life_expression / what_it_builds` are **pre-PR-SF1 existing period v2/public period_core surface**

## 2. Consumer Mapping — Backend

### 2.1 Runtime/backend consumers

| File | Line(s) | Consumer role | Critical / non-critical |
|---|---|---|---|
| `backend/app/transit/narrative/astrolog_narrative_engine.py` | `472-603` | Produces all period prose fields; current composer surface | `critical` |
| `backend/app/transit/narrative/deep_archetype_engine.py` | `786-985` | Period-core assembler; stores renderer output into `period_core` | `critical` |
| `backend/app/transit/present/public_builder.py` | `168-177`, `256-277` | Normalizes `period_opening / big_picture / mechanism / growth_edge / relational_or_life_expression / what_it_builds` in `_PERIOD_STORY_TEXT_KEYS` | `critical` |
| `backend/app/transit/present/public_builder.py` | `1182-1193` | `_global_period_story(...)` mirrors current 4-field structure into another public helper dict | `critical` |
| `backend/app/transit/present/public_builder.py` | `1215-1227` | `_build_period_teaser(...)` derives teaser from `period_opening` and `big_picture` | `critical` |
| `backend/app/transit/present/public_builder.py` | `1538-1650` | `build_public_response(...)` places raw `period_core` into public payload | `critical` |
| `backend/app/transit/present/public_builder.py` | `733-885` | `_build_home_period_core(...)` home-lite path also emits legacy 4-field shape | `critical` |
| `backend/app/transit/narrative/public_voice_en.py` | `453-485` | EN rewrite path rewrites the same legacy fields; would need parity update if new field is added | `critical` |
| `backend/app/api/routes/transits.py` | `662-667` | Prefix injection mutates `period_opening` and `core_story` | `critical` |
| `backend/app/transit/narrative/daily_synthesis.py` | `664-668` | `_period_sources(...)` uses `mechanism` as proof that period_core has content | `medium` |
| `backend/app/transit/narrative/daily_synthesis.py` | `620-623`, `1160-1167` | Daily bridge reads `title/core_story/upper_meaning`; indirect coupling | `medium` |
| `backend/scripts/dev/extract_reasoning_outputs.py` | `195-200` | Review artifact extractor serializes the five renderer fields directly | `non-critical` |
| `backend/scripts/generate_validation_samples.py` | `329-332`, `382-385` | Validation sample generator concatenates current field set into review bodies | `non-critical` |

### 2.2 Backend tests / assertions tied to current shape

| File | Line(s) | Consumer role | Critical / non-critical |
|---|---|---|---|
| `backend/tests/test_astrolog_narrative_engine.py` | many refs; especially `115-120`, `800-1099` | Direct renderer contract tests; asserts string presence/absence on all legacy fields | `critical` |
| `backend/tests/test_public_layered_output.py` | `128-137`, `372-376`, `470` | Public payload shape/integration; expects fields to exist and be non-empty | `critical` |
| `backend/tests/test_transit_narrative_public_payload.py` | `255`, `318`, `406` | Transit route payload and canonical prefix expectations | `medium` |
| `backend/tests/test_period_teaser_shape.py` | `33-69` | Teaser helper depends on `period_opening` and `big_picture` | `medium` |
| `backend/tests/_artifacts/reasoning_output_review/*.json` and review MDs | multiple | Review artifacts and comparison docs hard-code current field names | `non-critical` |

### 2.3 Daily / downstream note

Daily does **not** consume the whole 4-field surface as a dedicated renderer contract, but it does have indirect dependence through:

- `period_core.title`
- `period_core.core_story`
- `period_core.upper_meaning`
- `period_core.mechanism`

So a Phase 1 organic migration must keep those legacy fields populated, even if they become compatibility shadows.

## 3. Consumer Mapping — Mobile / Frontend

### 3.1 Repo presence

Mobile code **is present in this repo** under `mobile/`, so this audit could check real consumer code directly.

### 3.2 Mobile runtime findings

The current mobile app is **not** rendering `period_core` as four separate period prose blocks.

Actual behavior is mixed:

- `PeriodCoreDto` only parses:
  - `title`
  - `core_story`
  - `upper_meaning`
  - `big_picture`
  - `mechanism`
  - `tags`
- `period_opening`, `growth_edge`, and `relational_or_life_expression` are ignored by the mobile DTO layer
- `what_it_builds` is consumed heavily on **event cards**, not `period_core`
- mobile fallback cards and period calendar summaries collapse `period_core` into `title + subtitle + timeHint`, not dedicated 4-block rendering

### 3.3 Mobile consumer table

| Field | Mobile consumption | UI shape | File reference |
|---|---|---|---|
| `period_opening` | ignored in current `PeriodCoreDto` | ignored | `mobile/lib/app/timing/narrative_dtos.dart:599-626` |
| `mechanism` | parsed on `PeriodCoreDto`; also consumed heavily on event-card detail rendering | `separate` for event-card detail sections, `collapsed` for period core | `mobile/lib/app/timing/narrative_dtos.dart:599-626`, `2066-2176` |
| `growth_edge` | ignored on `PeriodCoreDto` | ignored | `mobile/lib/app/timing/narrative_dtos.dart:599-626` |
| `what_it_builds` | not parsed on `PeriodCoreDto`; used on `EventCardDto` and event-card detail sections | `separate` on event-card detail | `mobile/lib/app/timing/narrative_dtos.dart:1036-1063`, `2107-2176` |
| `relational_or_life_expression` | ignored in mobile DTOs | ignored | no runtime parse hit in `mobile/lib/app/timing/narrative_dtos.dart` |
| `big_picture` | parsed on `PeriodCoreDto`; used in fallback summary/subtitle and some calendar/home logic | `collapsed` / summary | `mobile/lib/app/timing/narrative_dtos.dart:599-626`, `mobile/lib/app/tabs/home_page.dart:91-99`, `mobile/lib/app/tabs/calendar_hub_page.dart:1257-1263` |
| `core_story` | parsed and used as primary summary/subtitle | `collapsed` / summary | `mobile/lib/app/timing/narrative_dtos.dart:599-626`, `mobile/lib/app/tabs/home_page.dart:91-99`, `mobile/lib/app/timing/narrative_dtos.dart:2420-2426` |
| `upper_meaning` | parsed and used as time-hint / small supporting line | `collapsed` / meta | same files above |

### 3.4 Important mobile conclusion

For **period_core** specifically, mobile is currently:

- **not separate 4-segment UI**
- **not full-text organic UI**
- mostly a **summary/metadata consumer**

The current “separate UI sections” behavior belongs to **period event cards**, not `period_core`.

That means **Phase 1 backend-only migration is feasible** if:

- legacy `period_core` fields stay populated
- `period_reading_v1` is additive
- mobile is not asked to consume it yet

## 4. Test Surface Impact

### 4.1 What is snapshot-like vs assertion-like

This repo has some “snapshot” language, but the period surface impact here is **mostly assertion-based**, not a classic golden snapshot suite.

For this migration, the main direct blast radius is:

| Test file | Dependency | Update effort | Notes |
|---|---|---|---|
| `backend/tests/test_astrolog_narrative_engine.py` | direct assertions on `period_opening / mechanism / growth_edge / relational_or_life_expression / what_it_builds` | `high` | Most sensitive backend file. |
| `backend/tests/test_public_layered_output.py` | public payload presence and some exact value assertions | `medium` | Will need additive-safe assertions for `period_reading_v1`. |
| `backend/tests/test_transit_narrative_public_payload.py` | route payload expectations and prefix behavior | `low-medium` | Old fields must remain. |
| `backend/tests/test_period_teaser_shape.py` | teaser depends on `period_opening` and `big_picture` | `medium` | Legacy fields must remain or teaser logic must intentionally stay legacy. |
| `mobile/test/transit_source_mapping_test.dart` | DTO/source mapping and period card detail shaping | `medium` | If Phase 1 is backend-only additive, these should not require immediate changes. |
| `mobile/test/calendar_hub_page_test.dart` | period_core mock maps include `mechanism` and event-card `what_it_builds` | `low-medium` | Mostly unaffected if old fields stay. |
| `mobile/test/home_page_logic_test.dart` | home fallback `period_core` mock map | `low` | Expects `core_story / upper_meaning / mechanism`; additive-safe. |

### 4.2 Estimated counts

- Backend files with direct period-4-field assertions likely needing review/update: **4**
  - `test_astrolog_narrative_engine.py`
  - `test_public_layered_output.py`
  - `test_transit_narrative_public_payload.py`
  - `test_period_teaser_shape.py`
- Mobile files likely needing **no required Phase 1 update** if additive-only: **0**
- Mobile files to revisit in **Phase 2** if UI starts consuming `period_reading_v1`: **3-5**
- New Phase 1 backend test files recommended: **1**
  - e.g. `backend/tests/test_period_reading_v1_contract.py`

### 4.3 Key finding

If Phase 1 keeps legacy 4 fields alive, this is **not** a “broad snapshot explosion” migration.

It is a **targeted assertion update** migration.

## 5. Schema Migration Safety Analysis

### 5.1 Proposed shape

Recommended placement:

```python
public["period_core"]["period_reading_v1"] = {
    "version": "period_reading_v1",
    "blocks": [
        {"role": "hook", "text": str},
        {"role": "unfolding", "text": str},
        {"role": "growth", "text": str},
        {"role": "closer", "text": str},
    ],
    "full_text": str,
}
```

### 5.2 Additive-safe or breaking?

**Additive-safe**, if:

- it is nested inside `period_core`
- old fields remain populated
- EN rewrite/normalization layers are updated not to drop the new field

Why this is safe:

- backend `PublicTransitResponse.period_core` is `Optional[dict]`, not a strict model
- backend shapers already tolerate additive keys
- mobile DTO parsing ignores unknown keys
- current mobile UI does not depend on a strict `period_core` schema beyond the fields it explicitly reads

### 5.3 Can old 4 fields stay as legacy/debug?

Yes, and they probably **must** in Phase 1.

Recommended Phase 1 stance:

- keep old fields live as **compatibility shadows**
- do **not** mark them debug-only yet in runtime behavior
- document them as legacy compatibility surface

### 5.4 Is removing old 4 fields safe now?

No.

Removing them in Phase 1 would break:

- backend renderer tests
- teaser helper logic
- some route-level prefix/path expectations
- mobile DTO / fallback assumptions around `mechanism`, `core_story`, `upper_meaning`, `big_picture`

### 5.5 Additional actual-code constraint

Two implementation details must be updated in Phase 1 or the new field will silently disappear:

1. `backend/app/transit/present/public_builder.py`
   - `_normalize_period_core_copy(...)`
   - `_PERIOD_STORY_TEXT_KEYS`
   - currently only knows the legacy strings

2. `backend/app/transit/narrative/public_voice_en.py`
   - `rewrite_period_core_en(...)`
   - currently rewrites only legacy fields

## 6. Composer Internal Plan Structure

### 6.1 Is current composer easily separable?

**Yes, moderately.**

Current renderer is not a single opaque paragraph builder anymore.

Useful existing structure already exists in:

- `backend/app/transit/narrative/astrolog_narrative_engine.py::build_period_story(...)`
- `_compose_semantic_focus_guidance(...)`
- `_compose_guided_fields(...)`

Current output is already assembled slot-by-slot:

- `period_opening`
- `big_picture`
- `mechanism`
- `growth_edge`
- `relational_or_life_expression`
- `what_it_builds`

### 6.2 Refactor effort estimate

**Moderate**, not high.

Why:

- current logic already computes slot-level strings separately
- PR-4.1 guided cases already return a dict of slot strings
- introducing internal `composer_plan` is mostly a re-expression of existing intermediate values, not a brand-new engine

### 6.3 Recommended internal-only shape

```python
ComposerPlanInternal = {
    "hook": str,
    "scene_anchor": str,
    "core_contrast": str,
    "mechanism": str,
    "growth_edge": str,
    "what_it_builds": str,
    "closer": str,
}
```

Recommended location:

- renderer internal helper output
- optional debug surface:
  - `period_narrative_prose.debug.composer_plan`

## 7. Block Role Mapping — Composer Plan -> Public Prose

### 7.1 Proposed mapping

| Composer plan slot | Public block role |
|---|---|
| `hook + scene_anchor` | `hook` |
| `core_contrast + mechanism` | `unfolding` |
| `growth_edge + what_it_builds` | `growth` |
| `closer` | `closer` |

### 7.2 Does this fit v4 reference?

**Mostly yes, with one caveat.**

The v4 reference examples are often **3 paragraphs**, not always 4 visibly separate paragraphs.

So the best interpretation is:

- **4 internal roles are good**
- **public `blocks[]` should allow 3-4 emitted blocks**

Recommendation:

- keep the 4-role taxonomy internally
- allow `closer` to merge into `growth` when the reading is naturally compact
- keep `full_text` canonical for mobile/simple rendering

This matches the sample targets better than forcing a visible 4-paragraph output every time.

## 8. Lint Guardrail Migration

### 8.1 Current guardrail base

Current render guardrail infrastructure already exists in:

- `backend/app/narrative/voice_guardrails_tr.py`
- `backend/app/transit/narrative/astrolog_narrative_engine.py::_render_guardrail_issues(...)`

Current live checks already cover:

- forbidden scaffold phrases
- hard-banned public words (`mekanizma`, `aktivasyon`, `proses`)
- technical leakage (`3. ev`, aspect names, planet names, etc.)

### 8.2 Organic prose guardrail mapping

| Rule | Organic target |
|---|---|
| opening↔mechanism duplication | compare `blocks[0].text` vs `blocks[1].text` for n-gram/scene duplication |
| parallel philosophy overuse | scan `full_text` and block transitions |
| anthropomorphic abstract subject | scan `full_text` with current forbidden-public-copy infrastructure |
| triple modifier stack | per-block sentence scan |
| segment-announcing connectors | reject at block openings: `Bu en çok... görünür`, `Risk...`, `Bu dönem sende... kasını geliştiriyor` |
| heavy emotional gravitas | per-block/full-text scan for moral-loaded 8th-house drift: `borç`, `suçluluk`, `yargı`, `hata` when not contextually justified |

### 8.3 Recommendation

Do **not** invent a separate organic renderer lint engine.

Add:

- new registry entries to `voice_guardrails_tr.py`
- one organic-output scan pass at:
  - `blocks[].text`
  - `full_text`

## 9. Phased Migration Plan

### Phase 1 — backend additive migration

Safe in isolation: **yes**

Recommended scope:

1. Add `period_core.period_reading_v1`
2. Refactor renderer to produce internal composer plan + organic blocks/full text
3. Keep legacy 4 fields populated
4. Apply guardrails to `blocks[]` and `full_text`
5. Add backend tests and sample review gate

Why backend-only Phase 1 is safe:

- mobile ignores unknown period_core keys
- `period_core` is already an additive raw dict surface
- current mobile UI is not yet block-role-driven for `period_core`

### Phase 2 — mobile-coordinated adoption

Safe only with coordination: **yes**

Needed coordination points:

- `mobile/lib/app/timing/narrative_dtos.dart`
- period calendar / period detail / home summary surfaces
- whether mobile wants:
  - `full_text` only
  - `blocks[]`
  - or both

### Phase 3 — legacy cleanup

Safe only after explicit verification:

- all runtime consumers migrated
- mobile no longer depends on legacy strings
- teaser/version logic either preserved from new structure or consciously redesigned

## 10. Smallest Safe First PR Scope

### Recommended Phase 1 concrete scope

- add `period_core.period_reading_v1`
- refactor renderer to produce:
  - internal `composer_plan`
  - public organic `blocks[]`
  - public `full_text`
- preserve legacy fields:
  - `period_opening`
  - `mechanism`
  - `growth_edge`
  - `what_it_builds`
  - `relational_or_life_expression`
- update normalization + EN rewrite paths so new field survives
- add guardrail coverage for organic output
- add backend-only tests
- produce before-commit sample review artifact

### Explicitly out of scope for first PR

- removing old fields
- mobile code changes
- PR-D feature flag work
- daily renderer rewrite
- natal changes
- LifeChapter detector changes

### Estimated implementation effort

- Backend runtime files changed: **4-6**
  - `astrolog_narrative_engine.py`
  - `public_builder.py`
  - `public_voice_en.py`
  - possibly `public_models.py` only if a typed nested model is introduced
  - possibly one helper/contract file
- Backend runtime LOC delta: **~300-500**
- Existing backend test files updated: **3-4**
- New backend test files: **1**
- Mobile files required in Phase 1: **0**
- Documentation updates in implementation phase: **2-3**

## 11. Risks and Trade-offs

### 11.1 Old 4 fields stale risk

**Risk:** duplicated content paths drift.

**Mitigation:**

- derive legacy fields from the same internal composer plan, not by reparsing `full_text`
- add a regression test that legacy fields map deterministically from plan/blocks

### 11.2 Composer refactor regression risk

**Risk:** renderer refactor changes prose shape and breaks current assertions.

**Mitigation:**

- keep additive rollout
- use substring/anchor assertions, not brittle full snapshots
- require sample review gate before merge

### 11.3 Mobile coordination risk

**Risk:** backend ships new field, mobile adoption lags, legacy fields live too long.

**Mitigation:**

- design Phase 1 so mobile can safely ignore the new field
- explicitly tag legacy fields as compatibility surface in docs

### 11.4 Lint coverage risk

**Risk:** new organic prose introduces new failure shapes not caught by legacy slot lint.

**Mitigation:**

- scan both block-level and full-text
- add the new connector and gravitas bans before cleanup PRs

### 11.5 Block role taxonomy lock-in

**Risk:** hard-coding 4 visible blocks may fight compact 3-paragraph readings.

**Mitigation:**

- lock the internal 4-role taxonomy
- allow public visible block count to be 3-4
- treat `full_text` as canonical reading surface

## 12. Recommended First Implementation PR

**Recommendation:** a backend-only additive Phase 1 that introduces `period_core.period_reading_v1`, keeps legacy period-core fields alive, refactors `astrolog_narrative_engine.py` to emit organic blocks/full text from an internal composer plan, and upgrades guardrails to scan organic prose.

## Appendix A — Key Files Inspected

- `backend/app/transit/present/public_models.py`
- `backend/app/transit/present/public_builder.py`
- `backend/app/transit/narrative/deep_archetype_engine.py`
- `backend/app/transit/narrative/astrolog_narrative_engine.py`
- `backend/app/transit/narrative/public_voice_en.py`
- `backend/app/transit/narrative/daily_synthesis.py`
- `backend/app/api/routes/transits.py`
- `backend/app/narrative/voice_guardrails_tr.py`
- `backend/scripts/dev/extract_reasoning_outputs.py`
- `backend/scripts/generate_validation_samples.py`
- `backend/tests/test_astrolog_narrative_engine.py`
- `backend/tests/test_public_layered_output.py`
- `backend/tests/test_transit_narrative_public_payload.py`
- `backend/tests/test_period_teaser_shape.py`
- `mobile/lib/app/timing/narrative_dtos.dart`
- `mobile/lib/app/tabs/home_page.dart`
- `mobile/lib/app/tabs/calendar_hub_page.dart`
- `mobile/test/home_page_logic_test.dart`
- `mobile/test/transit_source_mapping_test.dart`
- `mobile/test/calendar_hub_page_test.dart`
- `docs/voice/handcrafted_period_validation_v4_final.md`
- `docs/visual-system/normalized_interpretation_schema.ts`
