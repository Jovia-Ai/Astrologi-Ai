# Real-Chart Tier-1 LifeChapter Detection Trace

## Scope

- real chart: Istanbul `1996-12-28 07:10`
- dates:
  - `2026-03-04`
  - `2026-04-22`
- goal:
  - determine whether the chart/date should qualify for Saturn return or another Tier-1 LifeChapter under the intended current policy
  - determine why live runtime does or does not emit `active_life_chapter`

## 1. Natal Saturn

From live engine response:

- sign: `Aries`
- degree: `1.1579`
- house: `3`
- source path: live `_build_transits_engine_response(...).natal.bodies[]`

Natal Saturn signature:

```json
{
  "body": "Saturn",
  "lon": 1.1579,
  "sign": "Aries",
  "sign_deg": 1.1579,
  "house": 3
}
```

## 2. Transit Saturn on Sample Dates

### 2026-03-04

- sign: `Aries`
- degree: `2.1288`
- house: `11` in transit snapshot
- orb to natal Saturn: `0.9709`

Transit Saturn signature:

```json
{
  "body": "Saturn",
  "lon": 2.1288,
  "sign": "Aries",
  "sign_deg": 2.1288,
  "house": 11
}
```

Interpretation:

- conjunction is still close
- the live event engine also emits a Saturn return chapter window for this date

### 2026-04-22

- sign: `Aries`
- degree: `8.1514`
- house: `9` in transit snapshot
- orb to natal Saturn: `6.9935`

Transit Saturn signature:

```json
{
  "body": "Saturn",
  "lon": 8.1514,
  "sign": "Aries",
  "sign_deg": 8.1514,
  "house": 9
}
```

Interpretation:

- orb is materially wider
- live Saturn return chapter window has already ended by this date

## 3. Intended Saturn Return Policy Signals Present in Runtime

From `window_report` and `event_engine_v2.structural_chapter_rail`:

### 2026-03-04

Saturn return cycle event exists:

- `event_family = cycle_event`
- `event_subtype = saturn_return`
- `start_at = 2025-11-04`
- `exact_at = 2026-02-24`
- `end_at = 2026-04-16`
- `current_phase = active`
- `chapter_opening = true`
- `precision_signal = 0.998`

Also present:

- `saturn_conjunction_south node_milestone`
- `saturn_opposition_north node_milestone`

So March 4 sits inside:

- active Saturn return window
- active node-overlap milestone window

### 2026-04-22

No `saturn_return` cycle event exists in `structural_chapter_rail`.

The only Saturn chapter-like rail present is:

- `saturn_square_sun_milestone`

That means April 22 is outside the Saturn return chapter window currently emitted by the event engine.

## 4. Event Engine vs Display Items

### What the live detector currently receives

`_attach_internal_period_reasoning_state(...)` builds `transit_events` from:

- `core_response["display"]["items"]`

These are mostly `aspect_event` items such as:

- `Saturn square DSC`
- `Saturn square ASC`
- `Saturn conjunction Saturn`
- `Saturn conjunction South Node`

But they are not emitted as `cycle_event / saturn_return` candidates in `display.items`.

### What the event engine also has, but detector misses

`core_response["event_engine_v2"]["structural_chapter_rail"]` is a **list** containing:

- `saturn_return`
- `saturn_square_dsc_milestone`
- `saturn_square_asc_milestone`
- `saturn_conjunction_south node_milestone`
- `saturn_opposition_north node_milestone`

This is where the real chapter-level Saturn return signal lives on `2026-03-04`.

## 5. Why `detect_active_life_chapter(...)` Emits Nothing

Direct live detector result on both dates:

- `candidate_count = 0`
- `active_life_chapter = None`

Why:

### a. Candidate extractor logic

`life_chapter_detector.py` creates Tier-1 candidates from:

- `cycle_event` family
- or subtype in:
  - `saturn_return`
  - `nodal_return`
  - `nodal_opposition`

Plain `aspect_event` conjunctions do not become Saturn return candidates.

### b. Runtime wiring bug

`_attach_internal_period_reasoning_state(...)` passes:

- `transit_events = display.items`
- `structural_chapter_rail = event_engine_v2.get("structural_chapter_rail")`

But the detector currently accepts `structural_chapter_rail` only when it is a `Mapping`.

In real runtime it is a `list`.

So the actual `saturn_return` cycle event list is silently ignored.

### c. Solar year side-rail also underfed

`_attach_internal_period_reasoning_state(...)` reads:

- `response_out.get("solar_year_frame")`

But live core response keeps this under:

- `response_out["event_engine_v2"]["solar_year_frame"]`

So the solar year side-rail is also not being passed from the live response shape.

## 6. Decision

This trace produces a split conclusion by date:

### 2026-03-04

Decision: **E) runtime wiring bug**

Why:

- the chart/date does qualify under current emitted Saturn return policy
- the event engine already produces `cycle_event / saturn_return`
- the detector does not see it because the live route feeds the wrong shape

Secondary characterization:

- this is also a detector input-shape mismatch
- but the primary failure in live runtime is the wiring boundary

### 2026-04-22

Decision: **A) no bug — chart/date outside Saturn return policy**

Why:

- Saturn orb is `6.9935`
- the live Saturn return chapter window ended on `2026-04-16`
- no `saturn_return` cycle event is emitted for this date

So April 22 should **not** be force-promoted into a Saturn return.

## 7. Minimal Fix Boundary

Do not loosen detector policy globally.

If a fix is approved, the minimal safe fix is:

1. fix the runtime input wiring so the detector can see chapter-level cycle events that already exist on the live core response
2. support the actual `structural_chapter_rail` live shape
3. pass the actual solar year frame from the live response shape
4. keep April 22 as a no-false-positive control

## 8. Suggested Regression Tests After Fix

If March 4 is used:

- `test_saturn_return_detected_for_real_istanbul_chart_2026_03_04`
- assert `active_life_chapter.chapter_type == saturn_return`
- assert `semantic_focus.source == life_chapter`

Keep a no-false-positive control:

- real Istanbul chart on `2026-04-22`
- assert no Saturn return chapter is emitted

This preserves policy while fixing the live runtime wiring bug only where it is proven.
