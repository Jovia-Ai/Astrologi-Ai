# Natal Chart Dependency Audit

**Date:** 2026-04-29  
**Scope:** Backend + mobile dependency audit for natal chart calculation inputs, geometry reuse, and chart wheel data sourcing.  
**Constraint:** No code changes.

## 0. Executive Summary

The natal chart stack is split into two layers:

1. **Core geometry layer**
   - `backend/app/astro/chart_engine/builder.py`
   - builds resolved location, houses, planets, angles, and aspects
2. **Consumer routes/features**
   - `/api/calculate-natal-chart`
   - `/interpret/ui` and related public/profile payloads
   - synastry
   - sky event personalization
   - transit engines that reuse the same location resolver but not the exact natal builder route

Key findings:

- `POST /api/calculate-natal-chart` exists and is registered in `backend/app/routers/charts.py:98` and `backend/app/main.py:45`.
- Mobile currently calls this endpoint from **two places**:
  - `mobile/lib/app/chart/chart_wheel_repository.dart:20`
  - `mobile/lib/app/tabs/home_v2_natal.dart:242`
- The **Profile chart wheel** first tries to parse existing payload data locally, then falls back to `/api/calculate-natal-chart` only if direct geometry is unavailable.
- `/interpret/ui`, `profile_v8`, `core_story_ui`, and `meaning_graph_v1_1` are all **downstream of the same natal geometry**, but they reach it through typed `birth_place` inputs and `compute_natal_chart(...)`, not through the raw `/api/calculate-natal-chart` JSON contract.
- **Transit** does not use `build_natal_chart(...)` directly for its main reports, but it **does** reuse the same location resolution path via `resolve_location(...)`.
- Changing `city` vs `birth_place` precedence in `extract_birth_inputs(...)` would mostly affect **raw JSON callers** of `build_natal_chart(...)` and `/api/calculate-natal-chart`, not the typed `/interpret/ui` path.
- `/api/calculate-natal-chart` is **over-broad for chart wheel use**:
  - it computes full chart geometry,
  - formats positions/houses/aspects,
  - builds a textual summary,
  - and may call Groq AI plus OpenCage geocoding.
- A minimal chart-wheel endpoint should **wrap the existing natal builder**, not duplicate chart math.

## 1. Endpoint Definition And Callers

### 1.1 Where `/api/calculate-natal-chart` is defined

- Route definition: `backend/app/routers/charts.py:98`
- Alternate alias: `backend/app/routers/charts.py:99` via `@router.post("/natal-chart")`
- Router prefix: `backend/app/routers/charts.py:26` sets `APIRouter(prefix="/api", tags=["charts"])`
- Router registration: `backend/app/main.py:45`

### 1.2 What the route actually does

`backend/app/routers/charts.py` does not only return geometry. `_calculate_chart(...)`:

- calls `build_natal_chart(payload)`
- calls `chart_to_summary(chart)`
- calls `generate_ai_interpretation(summary)`
- adds formatted positions, houses, and aspects

This means `/api/calculate-natal-chart` is not a pure geometry endpoint.

### 1.3 Where the route is called from mobile

Current mobile callers:

1. `mobile/lib/app/chart/chart_wheel_repository.dart:20`
   - used by Profile natal chart wheel
2. `mobile/lib/app/tabs/home_v2_natal.dart:242`
   - used by Home V2 natal snapshot / Home chart wheel flow

No other mobile call site to `/api/calculate-natal-chart` was found in the current repo.

## 2. Mobile Feature Dependency Map

### 2.1 Profile natal chart wheel

Files:

- `mobile/lib/app/profile/profile_natal_chart_section.dart`
- `mobile/lib/app/chart/chart_wheel_repository.dart`
- `mobile/lib/app/chart/chart_wheel_data.dart`

Behavior:

- `ProfileNatalChartSection` first tries `ChartWheelData.tryFromInterpretPayload(widget.payload)`.
- If that fails and birth data exists, it calls `ChartWheelRepository.fetch(...)`.
- `ChartWheelRepository.fetch(...)` posts to `/api/calculate-natal-chart`.

Implication:

- Profile chart wheel is **partially decoupled** from the endpoint already.
- But current local parser expects raw chart-style fields:
  - `angles.ascendant`
  - `angles.midheaven`
  - `house_positions`
  - `planets`
- It does **not** read `public.natal_graph_compact` directly.

Classification: `should be wrapped by new endpoint`

Reason:

- The wheel needs only geometry.
- The current endpoint returns much more than geometry and may trigger third-party calls.

### 2.2 Home V2 natal/chart wheel flow

Files:

- `mobile/lib/app/tabs/home_v2_natal.dart`
- `mobile/lib/app/tabs/home_page_v2.dart:71`
- `mobile/lib/app/tabs/home_page_v2.dart:149`
- `mobile/lib/app/tabs/home_page_v2.dart:2060`

Behavior:

- `NatalRepository` posts to `/api/calculate-natal-chart`.
- The resulting large payload is reduced into `HomeV2NatalSnapshot`.
- Home uses this for chart wheel / rising-sign-driven UI.

Important contract note:

- This repository still sends both `birth_place` and `city`.
- That means it is still exposed to the current `extract_birth_inputs(...)` precedence.

Classification: `needs contract cleanup`

Reason:

- It uses the same over-broad endpoint as chart wheel.
- It still sends ambiguous location fields.

## 3. Shared Backend Geometry Stack

## 3.1 Core natal builder

Primary source:

- `backend/app/astro/chart_engine/builder.py`

Key functions:

- `extract_birth_inputs(...)` at `backend/app/astro/chart_engine/builder.py:182`
- `build_natal_chart(...)` at `backend/app/astro/chart_engine/builder.py:233`
- `calculate_chart_from_birth_details(...)` at `backend/app/astro/chart_engine/builder.py:316`

`build_natal_chart(...)` returns:

- resolved `location`
- `birth_datetime`
- `timezone`
- `planets`
- `houses`
- `house_positions`
- `angles`
- `aspects`

Classification: `should not be changed`

Reason:

- This is the canonical geometry engine used by multiple product surfaces.
- Chart wheel work should wrap or trim its outputs, not fork or replace its calculation logic.

## 3.2 Shared service wrapper used by typed natal flows

File:

- `backend/app/services/chart_service.py`

Key functions:

- `compute_natal_chart(...)`
- `serialize_planets(...)`
- `serialize_aspects(...)`

Important detail:

- `compute_natal_chart(...)` accepts `birth_place` semantically,
- then forwards it to `calculate_chart_from_birth_details(...)`,
- which currently builds a payload with `city=...`.

Classification: `safe to leave`

Reason:

- Typed natal flows are already semantically clean at the API boundary.
- Their internal conversion to `city` is awkward naming, but not the same bug as raw payload precedence.

## 3.3 Direct backend consumers of `build_natal_chart(...)`

### A. Charts router

File:

- `backend/app/routers/charts.py`

Uses:

- `/api/calculate-natal-chart`
- `/api/natal-chart`
- `/api/calculate-synastry`

Classification: `production privacy risk`

Reason:

- raw birth data accepted on a route that does not enforce auth
- can trigger Groq and OpenCage
- returns much more than a wheel needs

### B. Synastry analysis

File:

- `backend/app/services/synastry_analysis.py:174`

Uses:

- `build_natal_chart(partner)`
- reads planet longitudes, asc/mc, and house cusps

Classification: `should not be changed`

Reason:

- Synastry depends on the same core geometry and angle/cusp math.
- Any geometry refactor here would have relational side effects.

### C. Sky event personalization

File:

- `backend/app/sky_events/service.py`

Uses:

- `build_natal_chart({...})`
- derives natal points and house hits for event personalization

Classification: `should not be changed`

Reason:

- This is another legitimate geometry consumer.
- It should keep reusing the builder, not a chart-wheel-specific contract.

### D. Chart adapter layer

File:

- `backend/app/charts/_adapters/natal_adapter.py`

Uses:

- `build_natal_chart(input_data)`
- normalizes planets, angles, and houses for a generic chart model

Classification: `safe to leave`

Reason:

- This is already a wrapper around the shared builder.
- It is a useful pattern for a future wheel-specific wrapper endpoint.

## 4. `/interpret/ui`, `profile_v8`, `meaning_graph_v1_1`, transit, synastry, chart wheel

### 4.1 `/interpret/ui`

File:

- `backend/app/api/routes/natal_interpretation.py`

Key path:

- `compute_natal_chart(...)` at `backend/app/api/routes/natal_interpretation.py:1519`
- `_prepare_payload_from_chart(...)` builds the rest of the stack

This route depends on natal geometry for:

- `NatalContext.from_chart(chart_data)`
- `build_natal_graph(...)`
- rule engine
- composites
- narrative layers
- public payload assembly

Classification: `should not be changed`

Reason:

- This is a major production pipeline.
- Changes to geometry contract or core builder behavior would affect many downstream narrative systems.

### 4.2 `profile_v8`

Files:

- `backend/app/natal/public_builder.py:102`
- `backend/app/natal/profile_v8_payload_builder.py`

Dependency shape:

- `profile_v8` is not built directly from `/api/calculate-natal-chart`
- it is built downstream of the same `chart_data`

Classification: `should not be changed`

Reason:

- It depends on the same natal geometry indirectly.
- Contract cleanup should happen at endpoint/wrapper level, not by disturbing the profile builder path.

### 4.3 `meaning_graph_v1_1`

Files:

- `backend/app/natal/public_builder.py:117`
- `backend/app/meaning/meaning_graph_v1_1_builder.py`

Dependency shape:

- `meaning_graph_v1_1` is built from `core_story_ui`, personality/profile outputs, and public payload surfaces
- those surfaces are themselves downstream of the natal geometry

Classification: `safe to leave`

Reason:

- It is not a raw chart geometry consumer.
- It is indirectly dependent on chart data quality, but not on `city` vs `birth_place` parser precedence in the raw endpoint path.

### 4.4 Transit

Files:

- `backend/app/api/routes/transits.py`
- `backend/app/engine/transit_engine.py`
- `backend/app/transit/calendar_builder.py`

Dependency shape:

- Transit routes use typed fields:
  - `birth_place`
  - `birth_latitude`
  - `birth_longitude`
  - `birth_timezone`
- Transit engines call `resolve_location(...)` directly.
- Transit does **not** appear to rely on `/api/calculate-natal-chart`.
- Transit does **not** appear to call `build_natal_chart(...)` for its main report path.

Classification: `safe to leave`

Reason:

- Transit shares the location-resolution layer, not the raw natal chart endpoint contract.
- A raw `city` vs `birth_place` precedence fix in `extract_birth_inputs(...)` should not materially change transit behavior.

### 4.5 Synastry

Files:

- `backend/app/routers/charts.py`
- `backend/app/services/synastry_analysis.py`

Dependency shape:

- Synastry does use the same core natal geometry.
- It is a valid non-wheel consumer of the builder.

Classification: `should not be changed`

### 4.6 Chart wheel

Files:

- `mobile/lib/app/chart/chart_wheel_repository.dart`
- `mobile/lib/app/profile/profile_natal_chart_section.dart`
- `mobile/lib/app/tabs/home_v2_natal.dart`

Dependency shape:

- Profile wheel: local parse first, then endpoint fallback
- Home wheel: endpoint-driven

Classification: `should be wrapped by new endpoint`

Reason:

- The current endpoint is broader than required and has privacy/cost side effects.

## 5. `city` vs `birth_place` Precedence Blast Radius

## 5.1 Current precedence

`extract_birth_inputs(...)` currently prefers:

1. `city`
2. `birth_place`
3. `birthPlace`
4. `place`
5. other aliases

Source:

- `backend/app/astro/chart_engine/builder.py:182`

## 5.2 What would be affected by changing precedence

### Affected

- `/api/calculate-natal-chart`
- `/api/natal-chart`
- Home V2 natal repository, because it still sends both `birth_place` and `city`
- any direct backend or test payloads that call `build_natal_chart(...)` with both keys populated
- synastry callers if they pass ambiguous raw payloads

### Mostly unaffected

- `/interpret/ui` and typed natal routes
- `profile_v8`
- `meaning_graph_v1_1`
- transit typed routes

Reason:

- typed natal flows use `compute_natal_chart(birth_place=...)`
- they do not rely on raw endpoint alias precedence at the API boundary

Classification:

- raw JSON parser precedence: `needs contract cleanup`
- typed natal flows: `safe to leave`

## 6. Should A Minimal Chart-Wheel Endpoint Be Added?

Short answer: **yes, but only as a wrapper around the existing builder.**

Recommended shape:

- new endpoint accepts:
  - `birth_date`
  - `birth_time`
  - `birth_place`
  - optional `birth_latitude`
  - optional `birth_longitude`
  - optional `birth_timezone`
- internally calls existing `build_natal_chart(...)` or `compute_natal_chart(...)`
- returns only:
  - `angles.ascendant`
  - `angles.midheaven`
  - `house_positions`
  - `planets` with longitude/house/sign/retrograde

Why this is safe:

- no astro math duplication
- no separate source of truth for houses/angles/planets
- clear wheel-specific contract
- easy to exclude AI interpretation and formatted extras

Classification: `should be wrapped by new endpoint`

What should not happen:

- copying house/planet calculation logic into a second code path
- creating a wheel-only geometry builder that can drift from the main natal builder

## 7. Does `/api/calculate-natal-chart` Trigger AI Or Third-Party Calls?

Yes.

### AI

Files:

- `backend/app/routers/charts.py`
- `backend/app/ai/narrative/groq_client.py`

Current behavior:

- `_calculate_chart(...)` always calls `chart_to_summary(...)`
- then calls `generate_ai_interpretation(...)`
- `generate_ai_interpretation(...)` posts to Groq when `GROQ_API_KEY` is configured

### Third-party geocoding

File:

- `backend/app/astro/chart_engine/builder.py`

Current behavior:

- if explicit `latitude` + `longitude` + `timezone` are not supplied,
- `resolve_location(...)` may fall through to `fetch_location(...)`
- `fetch_location(...)` calls OpenCage via `requests.get(...)`

Implication for normal mobile usage:

- Profile chart wheel can avoid this if explicit lat/lon/timezone are present and direct payload parsing succeeds.
- Home and fallback chart-wheel fetches may still trigger both geocoding and AI.

Classification: `production privacy risk`

## 8. Canonical Field Assessment

## 8.1 What is canonical today in typed natal routes

For `/interpret/ui`-style typed requests, the canonical fields are:

- `birth_place`
- `birth_latitude`
- `birth_longitude`
- `birth_timezone`

Source:

- `backend/app/api/routes/natal_interpretation.py:199-209`

This is the cleanest contract in the codebase.

## 8.2 What is canonical today in the raw natal builder

For raw payload parsing in `extract_birth_inputs(...)`, the effective canonical primary label is:

- `city`

with `birth_place` only as a fallback alias.

This is the main contract mismatch.

## 8.3 What is canonical in mobile stored profile data

The profile store currently persists:

- `birth_date`
- `birth_time`
- `place`
- `city`
- `country`
- `timezone`
- `latitude`
- `longitude`

Source:

- `mobile/lib/app/profile/profile_repository.dart:103`
- `mobile/lib/app/profile/profile_repository.dart:272-279`

Interpretation:

- `place` appears to be the most specific human-readable location label in mobile profile storage
- `city` is a secondary structured field
- `latitude` / `longitude` / `timezone` are the safest canonical machine fields when available

## 8.4 Recommended canonical order going forward

For future cleanup, the safest semantic order is:

1. `birth_place` or `place` as the human-readable canonical label
2. `birth_latitude` + `birth_longitude` + `birth_timezone` as the machine-precise canonical resolver inputs
3. `city` only as a compatibility alias, not primary precedence

Classification: `needs contract cleanup`

## 9. Classification Matrix

| Dependency | Current usage | Classification | Notes |
|---|---|---|---|
| `backend/app/astro/chart_engine/builder.py` | Canonical natal geometry builder | `should not be changed` | Reuse, do not fork |
| `backend/app/services/chart_service.py` | Typed natal wrapper | `safe to leave` | Naming is awkward internally, behavior is stable |
| `/api/calculate-natal-chart` | Raw chart route for mobile/Home/wheel | `production privacy risk` | AI + OpenCage + no enforced auth |
| `mobile/lib/app/chart/chart_wheel_repository.dart` | Profile wheel fallback fetch | `should be wrapped by new endpoint` | Needs geometry-only route |
| `mobile/lib/app/tabs/home_v2_natal.dart` | Home V2 endpoint consumer | `needs contract cleanup` | Still sends both `birth_place` and `city` |
| `/interpret/ui` path | Main natal interpretation pipeline | `should not be changed` | Major downstream dependency chain |
| `profile_v8` | Downstream of typed natal geometry | `should not be changed` | Do not refactor around chart wheel |
| `meaning_graph_v1_1` | Downstream meaning layer | `safe to leave` | Indirect dependency only |
| Transit routes | Shared location resolver, not raw natal route | `safe to leave` | Separate engine, typed fields |
| Synastry | Shared natal geometry consumer | `should not be changed` | Depends on same house/angle math |
| Sky event personalization | Shared natal geometry consumer | `should not be changed` | Valid builder reuse |
| Raw `city` precedence in `extract_birth_inputs(...)` | Alias parser contract | `needs contract cleanup` | Main ambiguity source |
| Future minimal chart-wheel endpoint | Wrapper around existing builder | `should be wrapped by new endpoint` | Best path for data-source cleanup |

## 10. Bottom Line

- **Do not change natal chart math.**
- **Do not fork geometry logic for chart wheel.**
- **Do clean up the raw payload contract.**
- **Do not keep using `/api/calculate-natal-chart` as the long-term wheel endpoint.**

The safest next move is:

1. keep `build_natal_chart(...)` as the single geometry source of truth
2. keep typed natal flows (`/interpret/ui`, `profile_v8`, `meaning_graph_v1_1`) untouched
3. add a minimal wheel-specific wrapper endpoint around the existing builder
4. stop sending ambiguous `city` + `birth_place` together from remaining mobile consumers
5. treat the current `/api/calculate-natal-chart` route as privacy-sensitive and broader than the wheel use case requires
