# Flutter integration: stack clause rate-limit

Hand-off note for the UI rate-limit PR. Engine side is done — payload
already carries what the client needs.

## Payload path (mobile-visible)

`stack_clause_tr` reaches the mobile card via
**`response.public.event_cards[].stack_clause_tr`** and, equivalently,
**`response.public.period_peak_timeline[].event_card.stack_clause_tr`**.

The engine computes the clause on the `event_engine_v2` rail
(`personal_transit_rail` / `structural_chapter_rail`), and
`public_builder._merge_event_v2` whitelist-grafts it onto every
`display.items`/`event_cards` entry whose `event_id` matches a v2
event. Mobile's `EventCardDto` reads from the public path; rail events
themselves are not consumed directly.

## What the mobile card carries

Two independent text fields on each event card:

- **`why_now`** — the mobile card's narrative (card.why_now, consumed as
  `EventCardDto.whyNow`). Unchanged by this work; continues to be built
  by `deep_archetype_engine.build_event_card`. **Never contains the
  stack clause.** Render this unconditionally.
- **`stack_clause_tr`** — the stack synergy cue, propagated from the
  engine's AstroEventV2. Populated (non-empty) on exactly ONE event per
  natal-local day: the top-significance event in a gate-passing stack.
  Empty string `""` on every other event. The full astro_event payload
  is also accessible as `card.astro_event` if the client ever wants
  the underlying `stack_meta`.

Note: mobile's existing `why_now` field is snake_case `why_now` (no
`_tr` suffix) because it originates from `build_event_card`, which
predates the engine's `_tr` naming convention. The new field is
`stack_clause_tr` to match the engine contract. The two fields coexist
on the card dict and on the Flutter DTO.

## Concat rule (one line)

```dart
final display = card.whyNow + (showStackClause ? ' ' + card.stackClauseTr : '');
```

Where `showStackClause` is `stackClauseTr.isNotEmpty && cooldownOk`.

## Cooldown rule (rolling 7 days)

```dart
final lastShownMs = prefs.getInt('stack_clause_last_shown_at_ms') ?? 0;
final nowMs = DateTime.now().millisecondsSinceEpoch;
final sevenDaysMs = 7 * 24 * 60 * 60 * 1000;
final cooldownOk = (nowMs - lastShownMs) >= sevenDaysMs;
```

When the clause is actually rendered on screen, update the timestamp:

```dart
await prefs.setInt('stack_clause_last_shown_at_ms', nowMs);
```

## Behavior contract

| State | Action |
|---|---|
| `stack_clause_tr == ""` | Render `why_now_tr` alone. Do NOT update timestamp. |
| `stack_clause_tr != ""` AND `cooldownOk` | Render concat. Update timestamp to now. |
| `stack_clause_tr != ""` AND NOT `cooldownOk` | Render `why_now_tr` alone. Do NOT update timestamp. |
| First-ever user (no prefs entry) | Treat as cooldownOk → clause fires on first eligible event. |
| Returning after long absence (>7d) | Same as cooldownOk → clause fires on first eligible event seen. |

## Example mobile-visible card payload (after v2 merge)

```json
{
  "event_id": "evt_xyz",
  "why_now": "Etki su anda zirveye; bu da Yukselen temasini daha fark edilir hale getiriyor.",
  "stack_clause_tr": "Bu hat bugun tek basina degil; birkac konu ayni anda calisiyor.",
  "event_family": "aspect_event",
  "event_subtype": "square",
  "significance_score": 0.872,
  "astro_event": {
    "stack_clause_tr": "Bu hat bugun tek basina degil; birkac konu ayni anda calisiyor.",
    "significance_score": 0.872,
    "provenance": {
      "stack_meta": {
        "day": "2026-03-05",
        "size": 3,
        "boost": 1.2,
        "flags": ["polarity_mix", "planet_diversity", "outer_present"],
        "capped": true
      }
    }
  }
}
```

A non-top stack member on the same day looks identical in shape but has
`stack_clause_tr: ""`. Both cards share the same `stack_meta`
(accessible under `astro_event.provenance.stack_meta`), but only one
has a non-empty `stack_clause_tr`. The client should NOT derive clause
eligibility from `stack_meta.size` or `capped` — use `stack_clause_tr`
as the single source of truth.

## Suggested Flutter unit tests

Keep them minimal; these catch the obvious regressions:

1. **Empty clause → no concat, no timestamp update.**
   Event with `stack_clause_tr: ""` renders `why_now_tr` exactly; prefs
   untouched.

2. **Non-empty clause + fresh cooldown → concat + timestamp update.**
   Prefs has `last_shown_at_ms = 0`. Render includes clause. After
   render, prefs holds a near-now timestamp.

3. **Non-empty clause + active cooldown → render silent, timestamp
   unchanged.**
   Prefs has `last_shown_at_ms = now - 3 days`. Render is `why_now_tr`
   only. Prefs unchanged.

4. **Cooldown boundary → fires at exactly 7 days.**
   `last_shown_at_ms = now - 7 days exactly`. Render includes clause.

## Known limitations (v1 accepted debt)

- **Multi-device drift.** Cooldown state lives in each device's
  `SharedPreferences`. A user on phone + tablet may see the clause twice
  within 7 days (once per device). This is intentional for v1 — avoids a
  server roundtrip and a Supabase schema change. If field feedback shows
  the drift is noticeable, v2 will move state to a `user_state` column.

- **Timestamp reset on app reinstall.** Prefs are wiped on uninstall; a
  reinstalling user sees the clause on their next eligible event even if
  they just saw it. Acceptable for v1.

## Telemetry (consider for v2, not blocking)

A simple analytics event on every actual clause render — `stack_clause_shown`
with `{event_id, stack_size, flags}` payload — would let us validate the
live fire rate against the engine's 22.7% expectation and the UI's post-
rate-limit ~1/week target. Not required to ship v1, but the earlier we
wire it the sooner we can tune.

## Rollback path

If the clause causes UX issues in prod:

1. **Full kill switch** (server-side): set `apply_stack_boost=false` on
   the relevant engine code path. `stack_clause_tr` will be empty for all
   events; the client does nothing by default. No client deploy needed.

2. **Client-only disable**: feature-flag `showStackClause` to always
   `false`. Engine still emits; nothing rendered.

## Engine contract guarantees (won't change without a follow-up PR)

- `why_now` (mobile card field) never contains the stack clause.
- `stack_clause_tr` will only ever contain one fixed string:
  `"Bu hat bugun tek basina degil; birkac konu ayni anda calisiyor."`
  or an empty string. No variant forms, no templating.
- At most ONE event per natal-local day (the top-sig stack member) has
  a non-empty `stack_clause_tr`.
- Gate for population is `size >= 3 AND capped == True`
  (see `docs/engine_toggles.md` for the full spec).
- `stack_clause_tr` is propagated via the `PUBLIC_EVENT_V2_FIELDS`
  whitelist in `backend/app/transit/present/public_builder.py`. Any
  mobile-reachable card that matches an engine v2 event id receives it.

If any of these change, the commit must update this file in the same PR.
