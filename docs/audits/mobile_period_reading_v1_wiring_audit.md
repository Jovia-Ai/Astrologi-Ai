# Mobile `period_reading_v1` Wiring Audit

Generated on 2026-05-06.

## Executive Summary

- Mobile does **not** currently parse `period_core.period_reading_v1`.
- No mobile UI currently consumes `period_reading_v1.full_text`.
- No mobile UI currently consumes `period_reading_v1.blocks[]`.
- Current user-visible period copy still comes from legacy fields already exposed in `PeriodCoreDto`:
  - `title`
  - `core_story`
  - `upper_meaning`
  - `big_picture`
  - `mechanism`
- The smallest safe Phase 2 integration is:
  - add `periodReadingV1` to `PeriodCoreDto`
  - prefer `periodReadingV1.fullText` on Home + Calendar summary surfaces first
  - keep legacy fields as fallback
- Recommended rendering order:
  - Phase 2A: use `full_text` first
  - Phase 2B: use `blocks[]` on Period Detail / editorial reading surfaces

## 1. Current DTO Status

## 1.1 `mobile/lib/app/timing/narrative_dtos.dart`

Current `PeriodCoreDto` parses only:

- `title`
- `core_story`
- `upper_meaning`
- `big_picture`
- `mechanism`
- `tags`

Source:
- [narrative_dtos.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/timing/narrative_dtos.dart:599)

Observed:
- there is no DTO for `period_reading_v1`
- there is no `fullText` field
- there is no `blocks` field

Answer to question 1:
- **No**, `narrative_dtos.dart` does not currently parse `period_reading_v1`.

## 2. Current UI Consumption Map

## 2.1 Home UI

### `mobile/lib/app/tabs/home_page.dart`

Current period-core usage:

- fallback period card subtitle prefers:
  - `periodCore.coreStory`
  - then `periodCore.bigPicture`
- timing card body prefers:
  - `periodCore.coreStory`
  - then `periodCore.bigPicture`

Sources:
- [home_page.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/tabs/home_page.dart:85)
- [home_page.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/tabs/home_page.dart:1374)

### `mobile/lib/app/tabs/home_page_v2.dart`

Current period-core usage:

- hero headline precedence:
  - `periodCore.upperMeaning`
  - then first sentence of `periodCore.coreStory`
- detail body:
  - `periodCore.coreStory`
  - then `periodCore.upperMeaning`
- pull-quote section:
  - `periodCore.upperMeaning`
  - then `periodCore.coreStory`

Sources:
- [home_page_v2.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/tabs/home_page_v2.dart:242)
- [home_page_v2.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/tabs/home_page_v2.dart:3262)

Answer:
- Home UI does **not** consume `period_reading_v1`.
- It currently shows legacy `upperMeaning`, `coreStory`, and sometimes `bigPicture`.

## 2.2 Calendar UI

### `mobile/lib/app/tabs/calendar_hub_page.dart`

Current period-core usage:

- editorial direction body reads:
  - `periodCore.coreStory`
  - `periodCore.bigPicture`
- daily/editorial day summary may inject:
  - `periodCore.coreStory`
- long-term effect / hero summary prefers:
  - `periodCore.coreStory`
  - then `periodCore.bigPicture`
- `_PeriodCoreHero` renders:
  - `core.title`
  - `core.coreStory`

Sources:
- [calendar_hub_page.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/tabs/calendar_hub_page.dart:1248)
- [calendar_hub_page.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/tabs/calendar_hub_page.dart:1386)
- [calendar_hub_page.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/tabs/calendar_hub_page.dart:2656)
- [calendar_hub_page.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/tabs/calendar_hub_page.dart:6332)

Answer:
- Calendar UI does **not** consume `period_reading_v1`.
- It currently shows legacy `coreStory` and `bigPicture`, with `title` as heading.

## 2.3 Period Detail UI

### `mobile/lib/app/tabs/period_detail_page.dart`

`PeriodDetailPage` itself renders a `PeriodDetailNarrativeDto`, but the content is built upstream from `PeriodCardDto.buildDetailNarrative(...)`.

### `PeriodCardDto.buildDetailNarrative(...)`

Observed behavior:

- If the detail view is event-card based, content primarily comes from:
  - event card fields
  - optional `period_story` umbrella content from the event card
- If there is no event card, the fallback detail narrative uses:
  - `periodCore.title`
  - `periodCore.coreStory`
  - `timeHint`

Sources:
- [period_detail_page.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/tabs/period_detail_page.dart:1)
- [narrative_dtos.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/timing/narrative_dtos.dart:1946)

Answer:
- Period Detail does **not** consume `period_reading_v1.full_text`.
- Period Detail does **not** consume `period_reading_v1.blocks[]`.
- In practice it is still driven by event-card fields first, with `periodCore` only as fallback/context.

## 2.4 Consumption Table

| Surface | `period_reading_v1.full_text` | `period_reading_v1.blocks[]` | Current legacy fields used |
|---|---|---|---|
| Home Page | no | no | `core_story`, `big_picture`, `upper_meaning`, `title` |
| Home Page V2 | no | no | `upper_meaning`, `core_story` |
| Calendar Hub | no | no | `core_story`, `big_picture`, `title` |
| Period Detail | no | no | event-card prose first; `periodCore.coreStory` fallback |

## 3. Answers To The Audit Questions

## 3.1 Does mobile parse `period_reading_v1`?

- **No**

## 3.2 Does any Home / Calendar / Period Detail UI consume `period_reading_v1.full_text`?

- **No**

## 3.3 Does any UI consume `period_reading_v1.blocks[]`?

- **No**

## 3.4 If not, which legacy fields are currently shown to the user?

Current user-visible legacy fields are mainly:

- `core_story`
- `big_picture`
- `upper_meaning`
- `title`
- `mechanism` only in some narrative/detail derivation paths, not as the main period summary surface

## 4. Missing DTO Fields

The DTO gap is in `PeriodCoreDto`.

Currently missing:

- `periodReadingV1`
  - `version`
  - `fullText`
  - `blocks`
- block item DTO
  - `role`
  - `text`

Recommended additive DTO shape:

- `PeriodReadingBlockDto`
  - `role`
  - `text`
- `PeriodReadingV1Dto`
  - `version`
  - `blocks`
  - `fullText`
- `PeriodCoreDto`
  - existing fields remain
  - add nullable `periodReadingV1`

## 5. Recommended Phase 2 Implementation Plan

## Smallest safe integration

### Phase 2A

Use `periodReadingV1.fullText` first.

Why:

- smallest additive mobile change
- least UI churn
- backend already guarantees canonical paragraph separation
- easiest fallback model:
  - prefer `periodReadingV1.fullText`
  - else fallback to `coreStory`
  - else fallback to `bigPicture`

Recommended first surfaces:

1. `home_page.dart`
2. `home_page_v2.dart`
3. `calendar_hub_page.dart`

### Phase 2B

Use `periodReadingV1.blocks[]` on editorial/detail surfaces.

Why:

- blocks are more valuable when the UI wants paragraph rhythm
- period detail is the best candidate for structured editorial rendering

Recommended later surfaces:

1. `period_detail_page.dart`
2. any dedicated long-form period reading widget

## Recommendation on full_text vs blocks

Answer to question 6:

- **Use `full_text` first** for the smallest safe Phase 2.
- Use `blocks[]` later where UI wants true editorial paragraph rendering.

Reason:

- current surfaces mostly expect one summary body string
- `full_text` is already canonical and stable
- introducing blocks immediately would require more design decisions and widget changes

## 6. Screens That Need Updating

Minimum Phase 2 screens:

1. [narrative_dtos.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/timing/narrative_dtos.dart)
   - add DTO parsing
2. [home_page.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/tabs/home_page.dart)
   - prefer `periodReadingV1.fullText` over `coreStory` / `bigPicture`
3. [home_page_v2.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/tabs/home_page_v2.dart)
   - update hero/detail body sourcing
4. [calendar_hub_page.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/tabs/calendar_hub_page.dart)
   - update long-term/context/editorial period copy sourcing

Likely Phase 2B screen:

5. [period_detail_page.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/tabs/period_detail_page.dart)
   - use `blocks[]` for long-form reading only if the design wants paragraph-level rendering

Secondary/non-blocking screens to review after core Phase 2:

- chart-lab raw payload viewer uses raw `core_story`
- relationship preview/profile fallbacks also use legacy period core text

These are not the main user-facing period reading path and can follow later.

## 7. Test Plan

## Tests likely requiring updates

Primary mobile tests:

1. [home_page_logic_test.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/test/home_page_logic_test.dart)
   - currently asserts `coreStory` preference
   - should be updated to prefer `periodReadingV1.fullText` when present

2. [calendar_hub_page_test.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/test/calendar_hub_page_test.dart)
   - fixture payloads currently provide only legacy `period_core`
   - should add additive `period_reading_v1`
   - should verify calendar surfaces render it

3. [transit_source_mapping_test.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/test/transit_source_mapping_test.dart)
   - currently validates `PeriodCoreDto` mapping and detail fallback behavior
   - should add DTO parse coverage for `period_reading_v1`

Possible additional widget coverage:

4. `home_page_v2` tests if/when there is direct UI assertion on headline/detail copy source
5. period detail rendering tests if blocks-based rendering is introduced

## Recommended test additions

### DTO parsing

- `PeriodCoreDto.fromMap(...)` parses `period_reading_v1`
- preserves existing legacy fields

### Home / Calendar fallback ordering

- if `periodReadingV1.fullText` exists, use it first
- if absent, fallback to `coreStory`
- then fallback to `bigPicture`

### Blocks rendering, only in Phase 2B

- if `blocks[]` is rendered, preserve order
- preserve paragraph separation
- do not break legacy fallback when blocks are missing

## 8. Conclusion

Current mobile state is simple:

- backend already emits `period_core.period_reading_v1`
- mobile currently ignores it completely
- current UI still shows legacy period-core text fields

The smallest safe Phase 2 is therefore:

- add `periodReadingV1` to `PeriodCoreDto`
- adopt `full_text` first on Home and Calendar
- keep legacy fields as fallback
- only later decide whether Period Detail should render `blocks[]` as editorial paragraphs

That path is additive, low-risk, and aligned with the current backend contract.
