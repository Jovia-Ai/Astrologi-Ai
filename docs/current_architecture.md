# Current Architecture

Updated: 2026-02-23

## System Overview
- Monorepo has two main apps:
- `backend/`: FastAPI API + astrology/transit computation engine.
- `mobile/`: Flutter app (Supabase auth/profile + ChartLab UI/debug tooling).

## Backend Structure
- Transit routes: `backend/app/api/routes/transits.py`
- Calendar builder: `backend/app/transit/calendar_builder.py`
- Best-times scoring: `backend/app/transit/calendar/best_times.py`
- Calendar serializers: `backend/app/transit/serialize/calendar_serializers.py`
- Time parsing helpers: `backend/app/utils/timezones.py`

## Transit API Contracts
### `POST /transits`
- Purpose: period/core transit narrative (not calendar datasource).
- Body keys: `birth_date`, `birth_time`, `birth_place`, `transit_date`, `tz`
- Optional: `transit_place`

### `GET /transit/calendar`
- Purpose: month/range calendar days for grid.
- Query keys: `birth_date`, `birth_time`, `birth_place`, `start`, `end`, `tz`
- Optional: `transit_place`, `lens`, `view`, `include`
- Preferred response source for UI: `days[]` in public payload.

### `GET /transit/calendar/day`
- Purpose: single-day detail OR range mode.
- Query:
- Single day: `date`
- Range: `start` + `end`
- Common keys: `birth_date`, `birth_time`, `birth_place`, `tz`
- Optional: `transit_place`, `view`
- Current behavior:
- `date` => day detail payload
- `start/end` => calendar UI payload (`days[]`)

### `GET /transit/calendar/best-times`
- Purpose: best candidate days/windows for same range.
- Query keys: `intent`, `birth_date`, `birth_time`, `birth_place`, `start`, `end`, `tz`
- Optional: `sub_intent`, `body_area`, `top`, `window`, `debug`, `transit_place`, `lens`
- Response usually includes `candidates[]` and `windows[]`.

## Time/Date Normalization Rules
- `birth_time` is normalized in mobile to `HH:MM` before request.
- Backend parser accepts `HH:MM` and `HH:MM:SS` formats.
- Calendar month requests must always use focused month boundaries:
- `start = first day of focused month`
- `end = last day of focused month`

## Best-Times Category Model
- Main intent currently used in scoring rules: `beauty_care`
- Sub-intents:
- `nourish`
- `reduce`
- `procedure`
- Risk/gate categories:
- `phase_shift`, `event_peak`, `injury_risk`, `procedure_block`

## Mobile ChartLab Architecture
- Main file: `mobile/lib/app/tabs/chart_lab_page.dart`
- Endpoint action catalog: `mobile/lib/app/chart_lab/endpoint_catalog.dart`
- Request templates: `mobile/lib/app/chart_lab/chart_templates.dart`
- API client (`Dio`, JSON response type): `mobile/lib/app/api/api_client.dart`

## Calendar UX Flow in Mobile
### Transit: Calendar
- Calls `/transit/calendar` with focused month `start/end`.
- Builds `_eventsByDay` index from `days[]` (fallback from `events[]` if needed).
- Also calls `/transit/calendar/best-times` for same range.
- Best-times failure does not break calendar rendering.

### Transit: Calendar Day
- Calls `/transit/calendar/day` with `date=YYYY-MM-DD`.
- Uses returned day events as selected-day detail.

### Transit: Calendar Best Times
- Calls `/transit/calendar/best-times` directly with focused month range.
- Renders best-time list separately from day event list.

## UI State Decisions
- Single source of truth for selected-day list:
- `selectedEvents = _eventsByDay[_dayKey(_selectedDay)] ?? []`
- Header count and rendered cards both use the same `selectedEvents`.
- Month navigation:
- updates `_focusedMonth`
- clamps `_selectedDay` into valid day of that month
- re-fetches calendar data

## Error Handling
- 422 errors show validation details (`detail`) in UI.
- 4xx/5xx show status + JSON body where available.
- Best-times errors are shown inline in Best Times section and do not crash calendar card.
- Backend `/best-times` and `/calendar/day` routes now wrap failures and return structured JSON error payloads.

## Known Constraints
- `/transits` remains narrative/core endpoint and should not be used as date-keyed calendar datasource.
- Best-times output can vary by intent/rules; mobile parser supports `best_times[]`, `windows[]`, and `candidates[]`.
- Existing architecture is ChartLab-first (debug-capable). Product-grade screens may later split from ChartLab.
