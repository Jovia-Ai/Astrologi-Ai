# Transit `blocks[]` surface — source audit

**Date:** 2026-05-07
**Status:** investigation only, no code changed.
**Trigger:** observed `/transit/narrative` response carrying:
- top-level `calendar.days[]`
- top-level `blocks[]` with types `core_theme`, `daily_energy`, `event_list_preview`
- ASCII-only Turkish copy: `"Donem Temasi"`, `"Bu donemde emotions, growth alanlari one cikiyor"`, `"Gun Enerjisi"`, `"Dikkat Alani"`, `"Destek Alani"`, `"Gun Onizleme"` — none of which pass through `tr_normalize`.

This shape is **not** the new `public.period_core.period_reading_v1` surface. The audit
below traces where it is produced, who consumes it, and whether it should
be deprecated.

---

## 1. Producer — where the payload comes from

### 1.1 `assemble_blocks()` (top-level `response["blocks"]`)

| | |
|---|---|
| File | `backend/app/transit/narrative/assembler.py` |
| Function | `assemble_blocks()` (line 115) |
| Models | `backend/app/transit/narrative/models.py::UIBlock` / `CopyBundle` |
| Block types defined | `daily_energy`, `core_theme`, `event_list_preview`, `challenge`, `support`, `alert`, `best_time_primary`, `best_time_list`, `clarity` (`models.py` lines 6–18) |
| Hardcoded ASCII Turkish | `assembler.py` lines 158–166 (`"Donem Temasi"`), 184 (`"Dikkat Alani"`, `"Bazi gunlerde baski artabilir…"`), 200 (`"Destek Alani"`, `"Destekleyici akislari kullanmak icin…"`), 240 (`"Gun Enerjisi • {date}"`), 264 (`"Gun Onizleme"`, `"Gun detayini ac"`) |
| Long-form ASCII Turkish | `_synthesize_core_story()` lines 95–113 → emits `"Bu donemde {domains} alanlari one cikiyor. Baski seviyesi {x}, destek seviyesi {y}. Takvim sinyallerinde {labels} temalari daha sik gorulebilir."` |

### 1.2 `screen_builders` (top-level `response["screens"]`)

| | |
|---|---|
| File | `backend/app/transit/narrative/screen_builders.py` |
| Functions | `build_space_hub()`, `build_personal_transit()`, `build_calendar_day()`, `build_feed_snippet()` |
| Inputs | the `UIBlock[]` produced by `assemble_blocks()` — i.e. same source content |
| Hardcoded English titles | `"Space Hub"`, `"Personal Transit"`, `"Calendar Day"`, `"Feed Snippet"` (the screen builders never localize titles) |

### 1.3 Where they attach to the wire

`backend/app/api/routes/transits.py::build_transit_narrative()`:
- `assemble_blocks(...)` is called at line **3741** when
  `payload_profile not in {"calendar_day", "calendar_period"}` (line 3740 guard).
- Output is attached as `response["blocks"]` at **line 3831**.
- `screen_builders` results are attached as `response["screens"]` at **line 3833**.

The same route also emits the new `response["public"].period_core` (which
contains `period_reading_v1`). The two surfaces are produced
**independently** — see §3.

---

## 2. Consumer — who reads this surface

### 2.1 Mobile

| Consumer | What it reads | Read or just parsed? |
|---|---|---|
| `mobile/lib/app/timing/narrative_dtos.dart::NarrativeBlock.fromMap` | parses every block in `blocks[]` into `NarrativeBlock` | parses |
| `mobile/lib/app/timing/narrative_dtos.dart` (`NarrativeScreen`, `spaceHub`, `personalTransit`, `feedSnippet`) | parses `screens.*` | parsed but **never accessed** outside the DTO file (`grep -n "\.spaceHub\|\.personalTransit\|\.feedSnippet"` yields zero hits in mobile screens) |
| `mobile/lib/app/tabs/calendar_hub_page.dart` lines 1541, 1556, 5125, 5144 | `narrative.blocks.where((b) => b.type == 'best_time_primary')`, `b.type == 'best_time_list'` | **read** |
| Any mobile screen | `b.type == 'core_theme'` / `'daily_energy'` / `'event_list_preview'` / `'challenge'` / `'support'` / `'alert'` | **never read** (`grep -rn "\.type == 'core_theme'\|'daily_energy'\|'event_list_preview'\|'challenge'\|'support'\|'alert'"` returns 0 mobile hits) |
| `narrative.calendarDays` (top-level `calendar.days[]`) | `calendar_hub_page.dart`, `home_page.dart`, `home_page_v2.dart`, `home_v2_providers.dart` | **read** (this is the actively-used part of the same response) |

### 2.2 Web / other clients

No other clients in this repo. Mobile is the sole confirmed consumer.

---

## 3. Relation to `public.period_core.period_reading_v1`

### Wire layout

```
response = {
  "range": {...},
  "calendar": { "days": [...] },          ← actively consumed (calendarDays)
  "blocks": [                             ← legacy assembler surface
    {"type": "core_theme",       "copy": {...} },   ← NOT consumed
    {"type": "daily_energy",     "copy": {...} },   ← NOT consumed
    {"type": "event_list_preview","copy": {...} },  ← NOT consumed
    {"type": "best_time_primary","copy": {...} },   ← consumed
    {"type": "best_time_list",   "copy": {...} },   ← consumed
  ],
  "screens": {                            ← legacy screen builder surface
    "space_hub": {...},                   ← parsed, never accessed
    "personal_transit": {...},            ← parsed, never accessed
    "calendar_day": {...},                ← parsed, never accessed
    "feed_snippet": {...},                ← parsed, never accessed
  },
  "public": {
    "period_core": {                      ← actively consumed
      "title": ...,
      "core_story": ...,                  ← mobile reads as PeriodCoreDto.coreStory
      "upper_meaning": ...,
      "big_picture": ...,
      "mechanism": ...,
      "tags": [...],
      "period_reading_v1": {              ← canonical prose surface
        "version": "period_reading_v1",
        "blocks": [...],
        "full_text": "..."
      }
    }
  }
}
```

### Pipeline today

`period_reading_v1.full_text` is the canonical SHOU prose. It is written
into `period_core.core_story` inside `astrolog_narrative_engine.py`:

```python
# line ~573
polished_core_story = _final_polish_tr(
    str(period_reading_v1.get("full_text") or legacy_fields.get("core_story") or "")
)
```

Mobile's `PeriodCoreDto.fromMap` (`narrative_dtos.dart:617`) reads
`map['core_story']` into `coreStory`. So the period prose mobile actually
displays already comes from `period_reading_v1` — the `period_core.core_story`
field is just the surfaced wrapper.

The legacy assembler `core_theme` block carries an **independently
synthesized** `core_story` (built by `_synthesize_core_story()` in
`assembler.py:95`). It does **not** read from `period_reading_v1`. It
shares only the field name. The prose inside `core_theme` is therefore
older, lower-quality, ASCII-only Turkish — and unread by mobile.

### Bypass / replacement

- The top-level `blocks[]` shape **bypasses** `period_reading_v1` for the
  prose inside `core_theme` / `daily_energy`. They produce their own ASCII
  prose via `_synthesize_core_story()` and `generate_daily_narrative()`.
- It does **not replace** `period_reading_v1` — both surfaces ship in the
  same response, but only `period_reading_v1` (via `period_core.core_story`)
  is what the user actually sees.

---

## 4. Why this surface skips Turkish text-quality cleanup

| Step | Status |
|---|---|
| `tr_normalize` called inside `assembler.py` | **No.** No call to `tr_normalize` / `_final_polish_tr` anywhere in the file. |
| `tr_normalize` called inside `screen_builders.py` | **No.** Pure passthrough of the upstream `UIBlock.copy` text. |
| Route-level normalize sweep over `response` | **No.** `transits.py` imports `tr_normalize_tree` at line 62 but only uses it at line 1493 to normalize **content packs at load time** — not the outgoing payload. |
| Hardcoded copy uses Turkish diacritics | **No.** `f"Bu donemde {domain_text} alanlari one cikiyor. Baski seviyesi {pressure_text}, destek seviyesi {support_text}. Takvim sinyallerinde {labels_text} temalari daha sik gorulebilir."` is shipped raw. |

Net: the assembler surface was written before the project formalized
Turkish text quality (`text_quality_tr.py`, `_TR_WORD_FIXES`, the recent
`where.py` diacritic fix, etc.) and was never retrofitted because mobile
stopped consuming the relevant block types.

---

## 5. Old / legacy / current?

**Legacy.**

Evidence:

- Earliest commit touching `assemble_blocks` is `faf53f9 Add transit
  narrative pipeline and mobile app scaffold` — predates the canonical
  period story engine in `astrolog_narrative_engine.py` (`a19668f Add
  period astrolog narrative engine and integrate period story fields`).
- The newer SHOU voice work (commit `5abb09b Migrate period renderer
  toward SHOU v4 target voice`) lands inside
  `astrolog_narrative_engine.py` and `period_reading_v1`, not inside
  `assembler.py` or `screen_builders.py`.
- Mobile DTOs (`NarrativeScreen`, `spaceHub`, `personalTransit`,
  `feedSnippet`) parse the structure but no production screen reads it.
- Only two block types from this surface are still consumed
  (`best_time_primary`, `best_time_list`) and they have a separate prose
  pipeline (best-times) that is not the SHOU period prose.

The surface is still emitted unconditionally — so it is dead bytes on
the wire, not a removed feature.

---

## 6. Recommendation

**Deprecate the assembler-emitted block types except `best_time_*`, and
deprecate the `screens` envelope. Do not rewrite the ASCII prose inside.**

Rationale:

- Rewriting the prose inside `core_theme` / `daily_energy` / `event_list_preview`
  would be wasted effort: mobile never reads it, and `period_reading_v1`
  is already the canonical surface.
- Running `tr_normalize_tree` on the response right before send-out would
  paper over the diacritic issue but keep the dead-bytes problem (and
  would normalize text inside debug fields too — risky surface).
- Keeping the surface alive but stale is worse than removing it: any
  future SHOU voice review will keep tripping on these strings (this
  audit is the second time they've been flagged).

Suggested path (out of scope for this audit; flagged for a follow-up PR):

1. **Phase 1 — narrow `assemble_blocks` to `best_time_*` only.** Skip emission of
   `core_theme` / `daily_energy` / `event_list_preview` / `challenge` /
   `support` / `alert` blocks. Mobile already ignores them, so this is
   non-breaking.
2. **Phase 2 — drop `response["screens"]` envelope entirely.** Mobile parses
   it into DTOs but never accesses any field. Pure removal.
3. **Phase 3 — remove the now-unused helpers**: `assemble_blocks` becomes a
   thin best-times block emitter (or moves into the best-times module);
   `screen_builders.build_space_hub` / `build_personal_transit` /
   `build_calendar_day` / `build_feed_snippet` can be deleted along with
   their DTO mirror in `narrative_dtos.dart`.
4. **Phase 4 — delete `_synthesize_core_story()`** and the hardcoded
   ASCII strings (`"Donem Temasi"`, `"Gun Enerjisi"`, `"Dikkat Alani"`,
   `"Destek Alani"`, `"Gun Onizleme"`, etc.) — they no longer appear in
   any outgoing payload.

Each phase can ship independently behind a single payload-shape flag
(or just guarded by `payload_profile`). Phases 1+2 alone are enough to
stop the SHOU-quality flag from recurring; phases 3+4 are the cleanup.

A separate, lighter-weight option if any historical web build still
depends on the legacy shape:

- **Phase 0 — wrap the response in `tr_normalize_tree` before send-out**
  (one line change in `build_transit_narrative`), so the existing block
  copy at least normalizes diacritically. This does **not** fix the dead
  bytes / wasted bandwidth issue and does not improve prose quality, but
  it does stop the broken Turkish from showing up in audits. Treat this
  as a stopgap, not a destination.

---

## 7. Files touched (none)

This is an audit. No source code modified.

## 8. Files referenced

- `backend/app/transit/narrative/assembler.py`
- `backend/app/transit/narrative/screen_builders.py`
- `backend/app/transit/narrative/models.py`
- `backend/app/transit/narrative/rules.py`
- `backend/app/transit/narrative/astrolog_narrative_engine.py` (line ~573 — `polished_core_story` wiring)
- `backend/app/api/routes/transits.py` (lines 3741, 3831, 3833 — block / screens attachment; lines 62, 1493 — `tr_normalize_tree` import + load-time use)
- `mobile/lib/app/timing/narrative_dtos.dart` (`NarrativeBlock`, `NarrativeScreen`, `PeriodCoreDto`)
- `mobile/lib/app/tabs/calendar_hub_page.dart` (lines 1541, 1556, 5125, 5144 — only consumer of `blocks[]` types)
- `mobile/lib/app/tabs/home_page.dart`, `home_page_v2.dart`, `home_v2_providers.dart` — consumers of `narrative.calendarDays` and `narrative.periodCore`
