# Home Wrapper Empty / Degraded Payload Trace

## Scope

- payload profile: `home`
- chart/date: Istanbul `1996-12-28 07:10`, selected date `2026-04-22`
- artifact under review:
  - `backend/tests/_artifacts/transit_output_review_after_period_reading_v1/raw_transit_narrative_home_istanbul_2026-04-22.json`

## Observed Failure

The captured home payload is degraded:

- `public.period_core = {}`
- `event_cards = []`
- `daily_event_cards = []`
- `period_event_cards = []`
- `debug.degraded_path.active = true`
- `debug.degraded_path.reason = public_payload_exception`
- `debug.degraded_path.error_type = TypeError`

Current artifact size comparison:

- home public payload JSON size: `420`
- full public payload JSON size for same chart/date: `193614`

This is not a partial degradation. It is an exception-triggered empty fallback.

## Exact Exception

Reproducing `_build_narrative_public_payload(...)` with `payload_profile='home'` yields:

```text
TypeError: unsupported operand type(s) for -: 'datetime.date' and 'str'
```

Exact stack boundary:

- [transits.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/transits.py)
  - `_build_narrative_public_payload(...)`
  - `_home_daily_candidate_ids(...)`
  - `_home_daily_trigger_score(...)`

Exact failing operation:

```python
delta = abs((peak_date - selected_date).days)
```

At this point:

- `peak_date` is `datetime.date`
- `selected_date` is `str`

## Date Type Flow

### Expected helper contract

Confirmed signatures:

- `_home_daily_trigger_score(item, *, selected_date: date_type) -> float`
- `_home_daily_candidate_ids(..., selected_date: date_type) -> List[str]`

Both helpers expect `datetime.date`.

### Actual call path

Inside `_build_narrative_public_payload(...)`:

- `transit_date = request.selected_date or start_date.isoformat()`
- this produces a `str`
- home path then calls:

```python
home_candidate_ids = _home_daily_candidate_ids(
    raw_events=daily_selection_events,
    selected_day_context=selected_day_context,
    event_cards=event_cards,
    selected_date=transit_date,
)
```

So the home helper boundary receives a string where it expects `date_type`.

## Why the Live Route Degrades

The public route wraps `_build_narrative_public_payload(...)` in a defensive try/except.

When the `TypeError` is raised:

- the route logs `public_payload_exception`
- falls back to `_empty_public_narrative_payload()`
- on `payload_profile=home`, also emits a minimal calendar shell

That is why the home payload is empty instead of partially populated.

## Root Cause

Root cause is isolated and narrow:

- inconsistent `selected_date` type at the home helper boundary
- string is passed into helpers that are explicitly written for `datetime.date`

This is not a renderer problem.
This is not a selection rewrite problem.
This is not a chart math problem.

## Minimal Fix Proposal

Normalize `selected_date / transit_date` once at the helper boundary and keep the type consistent through:

- `_home_daily_candidate_ids(...)`
- `_home_daily_trigger_score(...)`

Smallest safe fix:

1. parse `transit_date` into `date_type` before calling `_home_daily_candidate_ids(...)`
2. keep the rest of the home scoring helpers on `date_type`
3. do not broaden the change into daily renderer logic

## Suggested Regression Test

- `test_home_wrapper_returns_populated_payload`
  - chart/date: Istanbul `1996-12-28 07:10`, `2026-04-22`
  - assert `period_core != {}`
  - assert no `public_payload_exception` in debug
  - assert home wrapper output payload size `>=` plain builder output size
