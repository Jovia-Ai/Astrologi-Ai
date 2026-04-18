# Flutter integration: stack clause rate-limit

Hand-off note for the UI rate-limit PR. Engine side is done — payload
already carries what the client needs.

## What the engine emits

Every transit event in `personal_transit_rail` / `structural_chapter_rail`
has two independent text fields:

- **`why_now_tr`** — stable narrative content (aspect why-now + PR9 solar
  resonance, if any). **Never contains the stack clause.** Render this
  unconditionally.
- **`stack_clause_tr`** — the stack synergy cue. Populated (non-empty) on
  exactly ONE event per natal-local day: the top-significance event in a
  gate-passing stack. Empty string `""` on every other event.

## Concat rule (one line)

```dart
final display = why_now_tr + (showStackClause ? ' ' + stack_clause_tr : '');
```

Where `showStackClause` is `stack_clause_tr.isNotEmpty && cooldownOk`.

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

## Example payloads (real engine output, 2026-03-04 probe on simple fixture)

### Event that gets the clause (top-sig member of a gated stack)

```json
{
  "event_id": "...",
  "event_family": "aspect_event",
  "event_subtype": "square",
  "title_tr": "Neptun Yukselen hattini calistiriyor",
  "why_now_tr": "Etki su anda zirveye; bu da Yukselen temasini daha fark edilir hale getiriyor.",
  "stack_clause_tr": "Bu hat bugun tek basina degil; birkac konu ayni anda calisiyor.",
  "significance_score": 1.043,
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
```

### Event that stays silent (part of the same stack, but not the top member)

```json
{
  "event_id": "...",
  "event_family": "aspect_event",
  "event_subtype": "square",
  "title_tr": "Neptun Alcalan hattini calistiriyor",
  "why_now_tr": "Etki su anda zirveye; bu da Alcalan temasini daha fark edilir hale getiriyor.",
  "stack_clause_tr": "",
  "significance_score": 1.043,
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
```

Both events share the same `stack_meta` (they belong to the same stack),
but only one has a non-empty `stack_clause_tr`. The client should not
derive clause eligibility from `stack_meta` directly — use
`stack_clause_tr` as the source of truth.

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

- `why_now_tr` will never contain the stack clause.
- `stack_clause_tr` will only ever contain one fixed string:
  `"Bu hat bugun tek basina degil; birkac konu ayni anda calisiyor."`
  or an empty string. No variant forms, no templating.
- At most ONE event per `stack_meta.day` has a non-empty
  `stack_clause_tr`.
- Gate for population is `size >= 3 AND capped == True`
  (see `docs/engine_toggles.md` for the full spec).

If any of these change, the commit must update this file in the same PR.
